"""
Review generator -- orchestrates prompt building + LLM call.
Pure business logic, no HTTP concerns.

On Vercel serverless, each request may be a cold start -- there is no
persistent state between invocations. The pool/warmup pattern doesn't
work here. Instead: one async LLM call per request, as fast as possible.
"""

from __future__ import annotations

import logging

from app.core.llm import LLMClient, get_llm_client
from app.prompts.system_prompt import build_system_prompt


logger = logging.getLogger(__name__)

# -- Module-level singleton LLM client ----------------------------------------
_default_client: LLMClient | None = None


def _get_default_client() -> LLMClient:
    """Return (and lazily initialise) the module-level LLM client."""
    global _default_client
    if _default_client is None:
        _default_client = get_llm_client()
    return _default_client


# -- Async review generation (preferred server path) --------------------------

async def agenerate_review(client: LLMClient | None = None) -> str:
    """
    Async: generate a single natural-sounding Google review.
    Uses the async LLM path -- never blocks the event loop.
    Single call, no pool, no warmup -- ideal for serverless.
    """
    resolved = client or _get_default_client()
    system_prompt = build_system_prompt()
    user_prompt = "Write a new, unique Google review for this business."
    return await resolved.agenerate(system_prompt, user_prompt)


def generate_review(client: LLMClient | None = None) -> str:
    """Sync: generate a review (kept for backwards compat / testing)."""
    resolved = client or _get_default_client()
    system_prompt = build_system_prompt()
    user_prompt = "Write a new, unique Google review for this business."
    return resolved.generate(system_prompt, user_prompt)
