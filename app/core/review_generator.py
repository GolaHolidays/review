"""
Review generator — orchestrates prompt building + LLM call.
Pure business logic, no HTTP concerns.
"""

from app.core.llm import LLMClient, get_llm_client
from app.prompts.system_prompt import build_system_prompt


def generate_review(client: LLMClient | None = None) -> str:
    """
    Generate a single natural-sounding Google review.

    Args:
        client: Optional pre-built LLM client (useful for testing / DI).
                Falls back to the default configured client.

    Returns:
        A plain-text review string ready for the user.
    """
    client = client or get_llm_client()
    system_prompt = build_system_prompt()
    user_prompt = "Write a new, unique Google review for this business."

    return client.generate(system_prompt, user_prompt)
