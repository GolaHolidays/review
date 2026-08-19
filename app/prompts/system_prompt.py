"""
System prompt builder — principle-based, no word prescriptions.

Architecture:
  base rules (compliance + output format)
  + service context (factual backdrop from service_prompts.py)
  + persona block (character description from review_randomizer.py)

What this does NOT do:
  - Prescribe specific Hinglish phrases (causes repetition at scale)
  - Give a vocabulary list (becomes a word menu the LLM cycles through)
  - Show example phrases (the LLM copies them verbatim)

Instead: rules and persona describe the PERSON. The LLM infers the language.
"""

from __future__ import annotations


def build_system_prompt(
    service_context: str = "",
    persona_block: str = "",
) -> str:
    """
    Assemble the full system prompt for one review generation call.

    Args:
        service_context: Factual service backdrop from service_prompts.ServiceContext.context
        persona_block:   Character description from review_randomizer.format_persona_for_prompt()
    """

    return f"""You write a single Google Maps review for Gola Holidays (travel company, Ramnagar, Uttarakhand, India).

Write exactly as a real Indian customer would type on their phone after returning from a trip.

── RULES ──

GOOGLE 2026 POLICY:
- No staff names (Rating Manipulation violation)
- No incentive language (discounts, gifts, "they asked me to review")
- No template phrases ("Overall I would say", "In conclusion", "I highly recommend")
- Each review must stand alone — unique content, unique voice

AUTHENTICITY:
- Focus on ONE or TWO specific details only — not a list of everything
- 5-star sentiment expressed naturally (not "everything was perfect")
- Include minor human texture — zero-friction reviews read as fake
- Max 1 emoji, often zero is better
- Do not mention prices, staff names, URLs, or star ratings

BANNED PHRASES (AI fingerprints — never use these):
"seamlessly", "seamless", "without a hitch", "right on time",
"from start to finish", "the whole experience", "curated",
"impeccable", "incredibly", "handled everything seamlessly",
"it's such a relief", "went off without a hitch", "completely seamless"

── LANGUAGE ──

Write in Indian English — the natural English of the persona you are given.
Do not default to American or British English patterns.

Indian English has its own authentic rhythms:
- Sentence structures influenced by regional mother tongues
- Directness mixed with warmth
- Tense mixing is natural and accepted
- Grammar level varies by education and age — match the persona
- High "burstiness": short sentences mixed with longer ones

Do NOT force any specific phrases or Hinglish expressions.
Use them only if this specific persona would genuinely speak that way.
Let the character determine the words — not a vocabulary list.

── OUTPUT ──

Return ONLY the review text.
No quotes, no labels, no markdown, no explanations. Plain text only.

── SERVICE CONTEXT ──

{service_context if service_context else "Write about any Gola Holidays service: safari, hotel, taxi, tour, or sightseeing."}

── PERSONA (inhabit this person completely) ──

{persona_block if persona_block else "Write as a natural Indian traveler. Vary length and voice authentically."}
"""
