"""
Review generator — orchestrates dice roll + prompt assembly + LLM call.

Each call to roll_persona() returns a PersonaCard that already contains
the service selection (Die 7, correlated with age + travel group).
No separate service picker needed.
"""

from __future__ import annotations

import logging

from app.core.llm import LLMClient, get_llm_client
from app.core.review_randomizer import roll_persona, format_persona_for_prompt
from app.prompts.system_prompt import build_system_prompt


logger = logging.getLogger(__name__)

_default_client: LLMClient | None = None


def _get_default_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = get_llm_client()
    return _default_client


def _build_prompts() -> tuple[str, str, float]:
    """Roll all 7 dice → assemble (system_prompt, user_prompt, temp_offset)."""
    card = roll_persona()
    persona_block = format_persona_for_prompt(card)

    system_prompt = build_system_prompt(
        service_context=card.service.context,
        persona_block=persona_block,
    )

    user_prompt = (
        f"Write one Google Maps review for Gola Holidays "
        f"about their {card.service.service_name} service."
    )

    logger.debug(
        "Rolled seed=%d service=%s age=%s region=%s group=%s personality=%s",
        card.seed,
        card.service.service_id,
        card.age.label,
        card.region.label[:20],
        card.travel_group.label[:20],
        card.personality.label,
    )

    return system_prompt, user_prompt, card.temperature_offset


async def agenerate_review(client: LLMClient | None = None) -> str:
    """Async: generate one unique review with full 7-dice randomization."""
    resolved = client or _get_default_client()
    system_prompt, user_prompt, temp_offset = _build_prompts()
    return await resolved.agenerate(system_prompt, user_prompt, temp_offset)


def generate_review(client: LLMClient | None = None) -> str:
    """Sync: generate one unique review with full 7-dice randomization."""
    resolved = client or _get_default_client()
    system_prompt, user_prompt, temp_offset = _build_prompts()
    return resolved.generate(system_prompt, user_prompt, temp_offset)
