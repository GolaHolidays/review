"""
Review generator -- orchestrates randomizer + service prompt + LLM call.
Each call rolls a fresh persona + picks a random service = unique review.
"""

from __future__ import annotations

import logging

from app.core.llm import LLMClient, get_llm_client
from app.core.review_randomizer import roll_persona, format_persona_for_prompt
from app.prompts.service_prompts import pick_random_service
from app.prompts.system_prompt import build_system_prompt


logger = logging.getLogger(__name__)

_default_client: LLMClient | None = None


def _get_default_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = get_llm_client()
    return _default_client


def _build_prompts() -> tuple[str, str, float]:
    """Roll randomizer + pick service → return (system_prompt, user_prompt, temp_offset)."""
    card = roll_persona()
    service = pick_random_service()
    persona_block = format_persona_for_prompt(card)

    system_prompt = build_system_prompt(
        service_context=service.context,
        persona_block=persona_block,
    )

    # User prompt is now minimal — all instructions are in system prompt
    user_prompt = f"Write one Google Maps review for Gola Holidays about their {service.service_name} service."

    logger.debug(
        "Rolled seed=%d service=%s persona=%s length=%s",
        card.seed, service.service_id, card.persona["who"][:30], card.length.label,
    )

    return system_prompt, user_prompt, card.temperature_offset


async def agenerate_review(client: LLMClient | None = None) -> str:
    """Async: generate one unique review with full randomization."""
    resolved = client or _get_default_client()
    system_prompt, user_prompt, temp_offset = _build_prompts()
    return await resolved.agenerate(system_prompt, user_prompt, temp_offset)


def generate_review(client: LLMClient | None = None) -> str:
    """Sync: generate one unique review with full randomization."""
    resolved = client or _get_default_client()
    system_prompt, user_prompt, temp_offset = _build_prompts()
    return resolved.generate(system_prompt, user_prompt, temp_offset)
