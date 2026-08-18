"""
Review generator -- orchestrates prompt building + LLM call.
Pure business logic, no HTTP concerns.

ReviewPool:
  Pre-generates reviews in the background and keeps a ready queue.
  When a request comes in, it pops one instantly from the queue
  (sub-millisecond) and immediately triggers a background refill.
  Cold start: warmup() is called at app startup to pre-fill the pool.
  Pool empty (edge case): falls back to a live agenerate() call.
"""

from __future__ import annotations

import asyncio
import logging

from app.core.llm import LLMClient, get_llm_client
from app.prompts.system_prompt import build_system_prompt


logger = logging.getLogger(__name__)

# -- Module-level singleton LLM client ----------------------------------------
# Built once at import time; reused across all warm serverless invocations.
# Preserves round-robin key rotation state between requests.
_default_client: LLMClient | None = None


def _get_default_client() -> LLMClient:
    """Return (and lazily initialise) the module-level LLM client."""
    global _default_client
    if _default_client is None:
        _default_client = get_llm_client()
    return _default_client


# -- Async review generation ---------------------------------------------------

async def agenerate_review(client: LLMClient | None = None) -> str:
    """
    Async: generate a single natural-sounding Google review.
    Uses the async LLM path -- never blocks the event loop.
    """
    resolved = client or _get_default_client()
    system_prompt = build_system_prompt()
    user_prompt   = "Write a new, unique Google review for this business."
    return await resolved.agenerate(system_prompt, user_prompt)


def generate_review(client: LLMClient | None = None) -> str:
    """
    Sync: generate a review (kept for backwards compatibility / testing).
    """
    resolved = client or _get_default_client()
    system_prompt = build_system_prompt()
    user_prompt   = "Write a new, unique Google review for this business."
    return resolved.generate(system_prompt, user_prompt)


# -- Review Pool ---------------------------------------------------------------

class ReviewPool:
    """
    Background pre-generation pool.

    Strategy:
      - Holds up to `size` pre-generated reviews in an asyncio.Queue.
      - warmup()     -- fills the pool at app startup (called from lifespan).
      - get()        -- pops a review instantly; triggers background refill.
      - _refill()    -- background task that generates until pool is full.
      - On pool empty (cold edge case): falls back to a live agenerate() call.
    """

    def __init__(self, size: int = 3) -> None:
        self._size  = size
        self._queue: asyncio.Queue[str] = asyncio.Queue(maxsize=size)
        self._refilling = False

    async def warmup(self) -> None:
        """Pre-fill the pool at startup. Errors are logged, not raised."""
        logger.info("ReviewPool: warming up with %d reviews...", self._size)
        await self._refill()
        logger.info("ReviewPool: ready with %d reviews.", self._queue.qsize())

    async def get(self) -> str:
        """
        Return a review immediately if available, otherwise generate live.
        Always schedules a background refill after returning.
        """
        try:
            review = self._queue.get_nowait()
            logger.debug("ReviewPool: served from pool (%d remaining).", self._queue.qsize())
        except asyncio.QueueEmpty:
            # Pool exhausted -- generate live (rare after warmup)
            logger.warning("ReviewPool: pool empty, generating live (cold path).")
            review = await agenerate_review()

        # Refill in background without blocking the response
        asyncio.create_task(self._refill())
        return review

    async def _refill(self) -> None:
        """Generate reviews until the pool is full. Runs in background."""
        if self._refilling:
            return
        self._refilling = True
        try:
            while not self._queue.full():
                try:
                    review = await agenerate_review()
                    await self._queue.put(review)
                    logger.debug("ReviewPool: added review (%d/%d).", self._queue.qsize(), self._size)
                except Exception as exc:
                    logger.error("ReviewPool: generation error during refill: %s", exc)
                    break
        finally:
            self._refilling = False


# Module-level pool instance -- shared across all requests
review_pool = ReviewPool(size=3)
