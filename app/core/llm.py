"""
LLM client abstraction -- decoupled from any specific provider.

Key pool strategy:
  - Round-robin across all configured API keys (even load distribution)
  - Automatic fallback on rate-limit / quota errors (tries next key)
  - Thread-safe rotation via threading.Lock
  - Raises only when all keys are exhausted
  - Async agenerate() path uses client.aio -- never blocks the event loop
"""

from __future__ import annotations

import logging
import threading
from typing import Protocol

from google import genai
from google.genai import types

from app.config import Settings, get_settings


logger = logging.getLogger(__name__)


# -- Retryable error signals (quota / rate limit) ------------------------------

_RETRYABLE_CODES    = {429, 503, 500}
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


# -- Thread-safe Key Pool ------------------------------------------------------

class KeyPool:
    """
    Round-robin, thread-safe pool of API keys.

    - .next() returns the next key in rotation atomically.
    - Each call advances the internal index so load is spread evenly.
    - Keys are pre-validated at construction time.
    """

    def __init__(self, keys: list[str]) -> None:
        if not keys:
            raise ValueError(
                "No API keys configured. "
                "Set at least GEMINI_API_KEY_1 in your .env file."
            )
        self._keys  = keys
        self._index = 0
        self._lock  = threading.Lock()
        logger.info("KeyPool initialised with %d key(s).", len(keys))

    def __len__(self) -> int:
        return len(self._keys)

    def next(self) -> tuple[int, str]:
        """Return (slot_number, api_key) for the next key in rotation."""
        with self._lock:
            slot        = self._index
            self._index = (self._index + 1) % len(self._keys)
        return slot, self._keys[slot]

    def get(self, slot: int) -> str:
        """Return the key at a specific slot (used for fallback iteration)."""
        return self._keys[slot % len(self._keys)]


# -- Protocol -- LLM provider interface ----------------------------------------

class LLMClient(Protocol):
    """Interface any LLM provider must satisfy."""

    def generate(self, system_prompt: str, user_prompt: str) -> str: ...
    async def agenerate(self, system_prompt: str, user_prompt: str) -> str: ...


# -- Gemini Implementation with round-robin + fallback -------------------------

class GeminiClient:
    """
    Google Gemini client with:
      - Round-robin key selection (even load across N keys)
      - Automatic fallback chain on quota / rate-limit errors
      - Sync  generate()  -- for direct/test usage
      - Async agenerate() -- preferred server path, non-blocking
    """

    def __init__(self, settings: Settings) -> None:
        self._pool       = KeyPool(settings.gemini_api_keys)
        self._model      = settings.llm_model
        self._gen_config = types.GenerateContentConfig(
            temperature=0.85,
            top_p=0.95,
            max_output_tokens=300,
        )

    # -- shared helpers --------------------------------------------------------

    def _build_config(self, system_prompt: str) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=self._gen_config.temperature,
            top_p=self._gen_config.top_p,
            max_output_tokens=self._gen_config.max_output_tokens,
        )

    def _build_attempts(self) -> list[tuple[int, str]]:
        """Return ordered attempt list starting from the next round-robin slot."""
        n = len(self._pool)
        start_slot, start_key = self._pool.next()
        return [
            (start_slot, start_key),
            *[
                ((start_slot + i) % n, self._pool.get(start_slot + i))
                for i in range(1, n)
            ],
        ]

    # -- sync path -------------------------------------------------------------

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Synchronous generation with round-robin + fallback."""
        attempts = self._build_attempts()
        config   = self._build_config(system_prompt)
        last_exc: Exception | None = None

        for attempt_num, (slot, api_key) in enumerate(attempts):
            try:
                if attempt_num > 0:
                    logger.warning(
                        "Key slot %d failed -- falling back to slot %d.",
                        attempts[attempt_num - 1][0], slot,
                    )
                else:
                    logger.debug("Using key slot %d (round-robin).", slot)

                client   = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self._model, contents=user_prompt, config=config,
                )
                return response.text.strip()

            except Exception as exc:
                last_exc = exc
                if _is_retryable(exc) and attempt_num < len(attempts) - 1:
                    logger.warning("Slot %d retryable error: %s", slot, exc)
                    continue
                raise

        raise RuntimeError(f"All {len(attempts)} API key(s) exhausted.") from last_exc

    # -- async path ------------------------------------------------------------

    async def agenerate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Async generation -- uses client.aio so it never blocks the event loop.
        Identical fallback logic to generate(). Preferred for all server paths.
        """
        attempts = self._build_attempts()
        config   = self._build_config(system_prompt)
        last_exc: Exception | None = None

        for attempt_num, (slot, api_key) in enumerate(attempts):
            try:
                if attempt_num > 0:
                    logger.warning(
                        "Async: key slot %d failed -- falling back to slot %d.",
                        attempts[attempt_num - 1][0], slot,
                    )
                else:
                    logger.debug("Async: using key slot %d (round-robin).", slot)

                client   = genai.Client(api_key=api_key)
                response = await client.aio.models.generate_content(
                    model=self._model, contents=user_prompt, config=config,
                )
                return response.text.strip()

            except Exception as exc:
                last_exc = exc
                if _is_retryable(exc) and attempt_num < len(attempts) - 1:
                    logger.warning("Async slot %d retryable error: %s", slot, exc)
                    continue
                raise

        raise RuntimeError(
            f"All {len(attempts)} async API key(s) exhausted."
        ) from last_exc


# -- Provider Registry ---------------------------------------------------------

_PROVIDERS: dict[str, type] = {
    "gemini": GeminiClient,
}


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    """
    Factory -- returns the configured LLM client.
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
