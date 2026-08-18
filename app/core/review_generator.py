"""
Review generator — orchestrates prompt building + LLM call.
Pure business logic, no HTTP concerns.

Singleton pattern:
  _default_client is initialised once at module import time and reused
  across all warm serverless invocations. This preserves round-robin
  key rotation state between requests and avoids re-initialisation
  overhead on every call.
"""

from app.core.llm import LLMClient, get_llm_client
from app.prompts.system_prompt import build_system_prompt


# Module-level singleton — built once, reused across warm invocations.
# On Vercel serverless, a container may handle many requests before being
# recycled; reusing the client ensures even key rotation across those requests.
_default_client: LLMClient | None = None


def _get_default_client() -> LLMClient:
    """Return (and lazily initialise) the module-level LLM client."""
    global _default_client
    if _default_client is None:
        _default_client = get_llm_client()
    return _default_client


def generate_review(client: LLMClient | None = None) -> str:
    """
    Generate a single natural-sounding Google review.

    Args:
        client: Optional pre-built LLM client (useful for testing / DI).
                Falls back to the module-level singleton client.

    Returns:
        A plain-text review string ready for the user.
    """
    resolved_client = client or _get_default_client()
    system_prompt = build_system_prompt()
    user_prompt = "Write a new, unique Google review for this business."

    return resolved_client.generate(system_prompt, user_prompt)
