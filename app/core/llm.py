"""
LLM client abstraction — decoupled from any specific provider.

Key pool strategy:
  - Round-robin across all configured API keys (even load distribution)
  - Automatic fallback on rate-limit / quota errors (tries next key)
  - Thread-safe rotation via threading.Lock
  - Raises only when all keys are exhausted
"""

from __future__ import annotations

import logging
import threading
from typing import Protocol

from google import genai
from google.genai import types

from app.config import Settings, get_settings


logger = logging.getLogger(__name__)


# ── Retryable error signals (quota / rate limit) ──────────────────────────────

_RETRYABLE_CODES = {429, 503, 500}  # quota exceeded, rate limit, transient
_RETRYABLE_STATUSES = {"RESOURCE_EXHAUSTED", "UNAVAILABLE", "INTERNAL"}


def _is_retryable(exc: Exception) -> bool:
    """Check if the exception is a quota / rate-limit error worth retrying."""
    msg = str(exc)
    return (
        any(str(code) in msg for code in _RETRYABLE_CODES)
        or any(status in msg for status in _RETRYABLE_STATUSES)
        or "quota" in msg.lower()
        or "rate" in msg.lower()
    )


# ── Thread-safe Key Pool ──────────────────────────────────────────────────────

class KeyPool:
    """
    Round-robin, thread-safe pool of API keys.

    - `.next()` returns the next key in rotation atomically.
    - Each call advances the internal index so load is spread evenly.
    - Keys are pre-validated at construction time.
    """

    def __init__(self, keys: list[str]) -> None:
        if not keys:
            raise ValueError(
                "No API keys configured. "
                "Set at least GEMINI_API_KEY_1 in your .env file."
            )
        self._keys = keys
        self._index = 0
        self._lock = threading.Lock()
        logger.info("KeyPool initialised with %d key(s).", len(keys))

    def __len__(self) -> int:
        return len(self._keys)

    def next(self) -> tuple[int, str]:
        """Return (slot_number, api_key) for the next key in rotation."""
        with self._lock:
            slot = self._index
            self._index = (self._index + 1) % len(self._keys)
        return slot, self._keys[slot]

    def get(self, slot: int) -> str:
        """Return the key at a specific slot (used for fallback iteration)."""
        return self._keys[slot % len(self._keys)]


# ── Protocol — LLM provider interface ────────────────────────────────────────

class LLMClient(Protocol):
    """Interface any LLM provider must satisfy."""

    def generate(self, system_prompt: str, user_prompt: str) -> str: ...


# ── Gemini Implementation with round-robin + fallback ────────────────────────

class GeminiClient:
    """
    Google Gemini client with:
      - Round-robin key selection (even load across 3 keys)
      - Automatic fallback chain on quota / rate-limit errors
      - Logs which key slot is used and any fallback events
    """

    def __init__(self, settings: Settings) -> None:
        self._pool = KeyPool(settings.gemini_api_keys)
        self._model = settings.llm_model
        self._gen_config = types.GenerateContentConfig(
            temperature=1.4,
            top_p=0.95,
            max_output_tokens=300,
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate content with round-robin key selection and fallback.

        Flow:
          1. Pick next key via round-robin.
          2. Try the request.
          3. On retryable error → rotate to next key and retry.
          4. Repeat until all keys tried or a non-retryable error occurs.
        """
        num_keys = len(self._pool)
        start_slot, start_key = self._pool.next()

        # Build the attempt sequence: start key + the remaining keys in order
        attempts = [
            (start_slot, start_key),
            *[
                ((start_slot + i) % num_keys, self._pool.get(start_slot + i))
                for i in range(1, num_keys)
            ],
        ]

        last_exc: Exception | None = None

        for attempt_num, (slot, api_key) in enumerate(attempts):
            try:
                if attempt_num > 0:
                    logger.warning(
                        "Key slot %d failed — falling back to slot %d.",
                        attempts[attempt_num - 1][0],
                        slot,
                    )
                else:
                    logger.debug("Using key slot %d (round-robin).", slot)

                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self._model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=self._gen_config.temperature,
                        top_p=self._gen_config.top_p,
                        max_output_tokens=self._gen_config.max_output_tokens,
                    ),
                )
                return response.text.strip()

            except Exception as exc:
                last_exc = exc
                if _is_retryable(exc) and attempt_num < num_keys - 1:
                    logger.warning("Slot %d retryable error: %s", slot, exc)
                    continue
                # Non-retryable or last key → re-raise immediately
                raise

        # Should never reach here, but keeps type-checker happy
        raise RuntimeError(
            f"All {num_keys} API key(s) exhausted."
        ) from last_exc


# ── Provider Registry ─────────────────────────────────────────────────────────

_PROVIDERS: dict[str, type] = {
    "gemini": GeminiClient,
}


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    """
    Factory — returns the configured LLM client.
    Add new providers to _PROVIDERS without touching callers.
    """
    settings = settings or get_settings()
    provider = settings.llm_provider.lower()

    if provider not in _PROVIDERS:
        raise ValueError(
            f"Unknown LLM provider '{provider}'. "
            f"Available: {', '.join(_PROVIDERS)}"
        )

    return _PROVIDERS[provider](settings)
