"""
Review Randomizer — pseudo-random diversity engine.

Uses Python's random module to inject genuine variation into each
review generation call. This breaks the LLM out of its "safe path"
repetition loop by giving it a different persona, length, tone,
opening style, and vocabulary set EVERY time.

Each call to roll_persona() produces a unique "persona card" that
gets injected into the prompt — so the LLM has no choice but to
write differently each time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


# ── Length profiles ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LengthProfile:
    label: str
    sentence_range: tuple[int, int]
    word_hint: str
    description: str


_LENGTH_PROFILES: list[LengthProfile] = [
    LengthProfile(
        label="one-liner",
        sentence_range=(1, 1),
        word_hint="8 to 20 words max",
        description="Ultra short, punchy, like a quick Google review tap-and-go",
    ),
    LengthProfile(
        label="short",
        sentence_range=(1, 2),
        word_hint="15 to 40 words",
        description="Brief but has one specific detail, no fluff",
    ),
    LengthProfile(
        label="medium",
        sentence_range=(3, 4),
        word_hint="50 to 90 words",
        description="Standard review with a couple specific details",
    ),
    LengthProfile(
        label="long",
        sentence_range=(5, 7),
        word_hint="100 to 170 words",
        description="Detailed storytelling review, sets a scene, has texture",
    ),
]

# Weighted distribution — short reviews are MORE common (mirrors real data)
_LENGTH_WEIGHTS: list[float] = [0.12, 0.30, 0.38, 0.20]


# ── Persona archetypes ───────────────────────────────────────────────────────

_PERSONAS: list[dict[str, str]] = [
    {
        "who": "a 28-year-old guy from Delhi on a boys' trip",
        "voice": "casual, uses slang, short sentences, might say 'bro' or 'dude'",
        "quirk": "writes fast, doesn't care about grammar perfection",
    },
    {
        "who": "a 55-year-old uncle from Lucknow traveling with wife",
        "voice": "polite, slightly formal, uses 'very good' and 'excellent', might say 'ji'",
        "quirk": "mentions wife or 'we both', writes in a dignified way",
    },
    {
        "who": "a 32-year-old mom from Mumbai traveling with kids and in-laws",
        "voice": "warm, practical, mentions kids' reactions, concerned about comfort",
        "quirk": "mentions 'my kids loved it' or 'even my mother-in-law enjoyed'",
    },
    {
        "who": "a 24-year-old solo traveler / backpacker from Bangalore",
        "voice": "modern, uses internet slang, might write 'ngl' or 'lowkey', brief",
        "quirk": "writes like an Instagram caption, minimal words maximum impact",
    },
    {
        "who": "a 40-year-old IT professional from Pune on a family vacation",
        "voice": "structured but warm, mentions planning and logistics positively",
        "quirk": "appreciates efficiency, might compare to other services",
    },
    {
        "who": "a 60-year-old retired teacher from Jaipur on a pilgrimage/nature trip",
        "voice": "gentle, philosophical, notices small beautiful details",
        "quirk": "writes longer sentences, appreciates nature and peace",
    },
    {
        "who": "a 35-year-old couple from Hyderabad on their anniversary trip",
        "voice": "romantic undertone, appreciative, mentions 'my husband/wife'",
        "quirk": "focused on the experience and setting, not logistics",
    },
    {
        "who": "a 22-year-old college student from Chandigarh on a group trip",
        "voice": "enthusiastic, uses exclamation marks, casual Hindi mixed in",
        "quirk": "might write 'paisa vasool' or 'full masti', very brief",
    },
    {
        "who": "a 45-year-old businessman from Gujarat traveling with family",
        "voice": "value-conscious, practical, mentions 'worth it' or 'good value'",
        "quirk": "cares about punctuality and no-nonsense service",
    },
    {
        "who": "a 38-year-old government employee from UP on leave with family",
        "voice": "straightforward Hindi-influenced English, polite, grateful",
        "quirk": "might write 'bahut accha' or 'sab kuch badhiya', uses 'thank you' at end",
    },
    {
        "who": "a 30-year-old woman from Kolkata traveling with friends",
        "voice": "descriptive, uses vivid imagery, appreciates aesthetics",
        "quirk": "mentions views, photographs, and the 'vibe' of the place",
    },
    {
        "who": "a 50-year-old NRI visiting from the US with family",
        "voice": "compares to international standards, impressed by local knowledge",
        "quirk": "mentions 'even by US standards' or 'better than expected', slightly formal",
    },
]


# ── Tones ─────────────────────────────────────────────────────────────────────

_TONES: list[str] = [
    "enthusiastic, uses exclamation marks, high energy",
    "calm and understated, matter-of-fact, no exaggeration",
    "grateful and warm, says thank you naturally",
    "brief and no-nonsense, just facts and verdict",
    "storytelling — starts with a scene or moment",
    "advice-giving — writes tips for other travelers",
    "slightly surprised — didn't expect it to be this good",
    "casual, like telling a friend about the trip",
]


# ── Opening styles (to BREAK the 'We booked' pattern) ────────────────────────

_OPENINGS: list[str] = [
    "Start with a specific moment or scene from the trip (e.g., 'The morning mist in Dhikala was something else...')",
    "Start with a short exclamation (e.g., 'What a trip!', 'Brilliant experience!', 'Loved it!')",
    "Start with who you traveled with (e.g., 'Went with my family...', 'Me and my friends planned...')",
    "Start with the destination directly (e.g., 'Jim Corbett in December is magical.', 'Nainital was beautiful as always.')",
    "Start with how you found them (e.g., 'Someone recommended Gola Holidays...', 'Found them on Google...')",
    "Start mid-story (e.g., 'So we were stuck with permit issues when...', 'Honestly was skeptical at first but...')",
    "Start with the verdict first (e.g., 'Best decision we made for this trip.', 'Totally worth it.')",
    "Start with advice (e.g., 'If you are going to Corbett, use these guys.', 'Don't waste time booking permits yourself.')",
    "Start with a time reference (e.g., 'Visited last month...', 'We went in March and...', 'Just came back from...')",
    "Start by mentioning the specific service used (e.g., 'Used their cab service from Kathgodam...', 'Booked a safari through them...')",
    "Start with a contrast (e.g., 'Unlike our last Corbett trip which was a mess, this time...')",
    "Start with a direct statement about the company (e.g., 'These people know their job.', 'Very professional team.')",
]


# ── Indian English vocabulary swaps ───────────────────────────────────────────
# Words the LLM overuses → replacements that sound more Indian/natural

_VOCAB_INSTRUCTIONS: list[str] = [
    "Use 'smooth' or 'sorted' instead of 'seamless'",
    "Use 'on time' or 'before time only' instead of 'right on time'",
    "Use 'no tension' or 'tension free' instead of 'relief'",
    "Use 'proper' instead of 'well-organized'",
    "Use 'very cooperative' instead of 'incredibly helpful'",
    "Use 'paisa vasool' if it fits naturally",
    "Use 'bhaiya' or 'uncle' to refer to the driver if appropriate",
    "Use 'accha' or 'badhiya' if it fits the persona naturally",
    "Use 'only' as emphasis like Indians do (e.g., 'driver came before time only')",
    "End with 'Recommended!' or 'Must try!' or 'Thank you!' if it fits naturally",
    "Use 'Keep it up!' or 'Hats off!' at the end if the persona would say that",
    "Use simple words — 'good' is better than 'exceptional', 'nice' is better than 'impeccable'",
]


# ── Closing style variation ──────────────────────────────────────────────────

_CLOSINGS: list[str] = [
    "End with a recommendation (e.g., 'Would recommend to everyone.')",
    "End with a plan to return (e.g., 'Planning to come back next year.')",
    "End with gratitude (e.g., 'Thanks Gola team!')",
    "End with the specific highlight (e.g., 'That tiger sighting made the whole trip.')",
    "End abruptly — just stop after the last detail, no conclusion needed",
    "End with advice for others (e.g., 'Book Dhikala zone if you can, it's worth it.')",
    "End with a comparison (e.g., 'Much better than our last agent.')",
    "End with an emoji or two max (👍 or 🙏 or ❤️)",
]


# ── The main roll function ───────────────────────────────────────────────────

@dataclass(frozen=True)
class PersonaCard:
    """Everything the LLM needs to write a unique review."""
    seed: int
    persona: dict[str, str]
    tone: str
    length: LengthProfile
    opening_style: str
    closing_style: str
    vocab_hints: list[str]
    temperature_offset: float  # small random offset for LLM temperature


def roll_persona() -> PersonaCard:
    """
    Roll a completely random persona card using pseudo-random numbers.
    
    Every attribute is independently randomized, creating thousands
    of possible combinations — making pattern repetition nearly impossible.
    """
    seed = random.randint(10000, 99999)

    # Use the seed for reproducibility within this roll, but each roll
    # gets a fresh seed so results vary across calls
    rng = random.Random(seed)

    persona = rng.choice(_PERSONAS)
    tone = rng.choice(_TONES)
    length = rng.choices(_LENGTH_PROFILES, weights=_LENGTH_WEIGHTS, k=1)[0]
    opening_style = rng.choice(_OPENINGS)
    closing_style = rng.choice(_CLOSINGS)

    # Pick 2-3 random vocab hints (not all — that would over-constrain)
    num_vocab = rng.randint(2, 3)
    vocab_hints = rng.sample(_VOCAB_INSTRUCTIONS, k=num_vocab)

    # Small temperature offset: ±0.08 to add micro-variation
    temperature_offset = rng.uniform(-0.08, 0.08)

    return PersonaCard(
        seed=seed,
        persona=persona,
        tone=tone,
        length=length,
        opening_style=opening_style,
        closing_style=closing_style,
        vocab_hints=vocab_hints,
        temperature_offset=temperature_offset,
    )


def format_persona_for_prompt(card: PersonaCard) -> str:
    """
    Convert a PersonaCard into a natural-language instruction block
    that gets injected into the user prompt.
    """
    vocab_block = "\n".join(f"   - {v}" for v in card.vocab_hints)

    return f"""── THIS REVIEW'S IDENTITY (seed #{card.seed}) ──

WHO IS WRITING: {card.persona['who']}
THEIR VOICE: {card.persona['voice']}
THEIR QUIRK: {card.persona['quirk']}

TONE FOR THIS REVIEW: {card.tone}

LENGTH: {card.length.label} — {card.length.word_hint}
  → {card.length.description}
  → Aim for {card.length.sentence_range[0]} to {card.length.sentence_range[1]} sentences

HOW TO START: {card.opening_style}
HOW TO END: {card.closing_style}

VOCABULARY HINTS FOR THIS REVIEW:
{vocab_block}

CRITICAL: Write EXACTLY as this person would write — with their grammar level,
their word choices, their sentence length patterns. Do NOT write "perfect English"
if this person wouldn't. Indian English is the target, not American/British English."""
