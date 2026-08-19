"""
Review Randomizer — 7-Dice Generative Persona Engine.

Design philosophy:
  Old system: fixed pool of 12 archetypes + word prescription lists
    → LLM cycles through the same phrases across reviews

  New system: 7 independent dice compose a unique person every call
    → Thousands of combinations, zero word prescriptions
    → LLM infers natural language FROM the character — not from a vocabulary menu

Dice:
  1. Age bucket         — energy level, vocabulary complexity, tech-savviness
  2. Region/Language    — sentence structure, Hinglish ratio, cultural tone
  3. Travel group       — what they notice, whose comfort matters, group energy
  4. Personality type   — emotional register and narrative style
  5. Typing style       — grammar level, sentence rhythm, punctuation habits
  6. Priority           — which aspect of the trip they focus on most
  7. Service used       — correlated with Die 1 (age) + Die 3 (group), NOT pure random

Possible combinations: 5 × 5 × 5 × 5 × 5 × 5 = 15,625 base combinations
(before length and temperature variation — effectively unlimited at 50 reviews)
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.prompts.service_prompts import ALL_SERVICES, ServiceContext


# ── Length profiles ────────────────────────────────────────────────────────────

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
        description="Ultra short, punchy — quick tap-and-go Google review",
    ),
    LengthProfile(
        label="short",
        sentence_range=(1, 2),
        word_hint="15 to 40 words",
        description="Brief but contains one specific detail, no filler",
    ),
    LengthProfile(
        label="medium",
        sentence_range=(3, 4),
        word_hint="50 to 90 words",
        description="Standard review — a couple of specific details, natural close",
    ),
    LengthProfile(
        label="long",
        sentence_range=(5, 7),
        word_hint="100 to 170 words",
        description="Detailed and textured — sets a scene, has a sense of the trip",
    ),
]

# Mirrors real review length distribution — short reviews are more common
_LENGTH_WEIGHTS: list[float] = [0.12, 0.30, 0.38, 0.20]


# ── Die 1: Age Bucket ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AgeBucket:
    label: str
    character_note: str  # behavioral texture, NOT word instructions


_AGE_BUCKETS: list[AgeBucket] = [
    AgeBucket(
        label="20s",
        character_note=(
            "Young, spontaneous, grew up on the internet. Comfort with short, "
            "punchy writing. Energy comes through naturally. Likely wrote this on a phone."
        ),
    ),
    AgeBucket(
        label="30s",
        character_note=(
            "Working professional or young parent. Values efficiency and clarity. "
            "Writing mixes casual warmth with practical observation."
        ),
    ),
    AgeBucket(
        label="40s",
        character_note=(
            "Mid-life, established, family-oriented or senior professional. "
            "Writes with some deliberateness. Neither too casual nor overly formal."
        ),
    ),
    AgeBucket(
        label="50s",
        character_note=(
            "Nearing or at senior stage. More thoughtful and measured. "
            "Appreciates reliability, courtesy, and things done properly. "
            "Writing style tends to be careful and complete."
        ),
    ),
    AgeBucket(
        label="60s+",
        character_note=(
            "Retired or senior. Takes time with words. Notices the small things — "
            "a courteous driver, a beautiful view, a peaceful moment. "
            "May write longer sentences. Appreciates nature and sincerity."
        ),
    ),
]

_AGE_WEIGHTS: list[float] = [0.20, 0.28, 0.22, 0.18, 0.12]


# ── Die 2: Region / Language Background ───────────────────────────────────────

@dataclass(frozen=True)
class Region:
    label: str
    language_note: str  # how this shapes writing texture — not word lists


_REGIONS: list[Region] = [
    Region(
        label="Metro city (Delhi / Mumbai / Bangalore / Hyderabad)",
        language_note=(
            "Comfortable in English. May use modern casual phrasing. "
            "Urban, direct. Hinglish is possible but not heavy — only where it feels natural."
        ),
    ),
    Region(
        label="Hindi-belt city or town (UP / MP / Rajasthan / Uttarakhand / Bihar)",
        language_note=(
            "Natural Hindi-English mix in daily speech. Sentence structure influenced by Hindi. "
            "Polite and respectful tone is cultural default. "
            "Writes as they would speak — warm, sometimes formal in small ways."
        ),
    ),
    Region(
        label="South India (Tamil Nadu / Karnataka / Kerala / Andhra Pradesh)",
        language_note=(
            "Writes in structured, grammatically careful English. "
            "Minimal Hinglish — only if this person would genuinely know the phrase. "
            "Formal and thoughtful. Complete sentences preferred."
        ),
    ),
    Region(
        label="East India (West Bengal / Odisha / Northeast)",
        language_note=(
            "Slightly descriptive and warm in style. Notices atmosphere and aesthetics. "
            "Gentle personal tone. May frame the review as a small story."
        ),
    ),
    Region(
        label="NRI / living abroad",
        language_note=(
            "Fluent English, slightly more formal. May naturally compare to experiences abroad. "
            "Impressed by local knowledge and authenticity. "
            "Review may reflect both outsider wonder and insider Indian roots."
        ),
    ),
]

_REGION_WEIGHTS: list[float] = [0.30, 0.30, 0.18, 0.12, 0.10]


# ── Die 3: Travel Group ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TravelGroup:
    label: str
    perspective_note: str  # what they observe and care about as a group type


_TRAVEL_GROUPS: list[TravelGroup] = [
    TravelGroup(
        label="Solo traveler",
        perspective_note=(
            "Writes from a personal, first-person singular perspective. "
            "Notices their own individual experience — freedom, value, ease of solo travel."
        ),
    ),
    TravelGroup(
        label="Couple (anniversary or leisure trip)",
        perspective_note=(
            "Writes as 'we'. Notices shared moments, ambiance, and the experience together. "
            "May refer to a partner. Emotional resonance matters."
        ),
    ),
    TravelGroup(
        label="Family with young children",
        perspective_note=(
            "Very aware of the children's experience — their reactions, safety, patience required. "
            "Comfort and ease are top priorities. May mention the kids noticed or enjoyed something."
        ),
    ),
    TravelGroup(
        label="Friends group trip",
        perspective_note=(
            "Group energy — writes as 'we all', references shared fun. "
            "Casual and upbeat. The collective good time is the measure of success."
        ),
    ),
    TravelGroup(
        label="Traveling with parents or senior family members",
        perspective_note=(
            "Very conscious of accessibility and ease for elders. "
            "Grateful and responsible tone. Driver patience, comfort, and no-hassle experience matter most."
        ),
    ),
]

_TRAVEL_GROUP_WEIGHTS: list[float] = [0.15, 0.22, 0.25, 0.20, 0.18]


# ── Die 4: Personality Type ────────────────────────────────────────────────────

@dataclass(frozen=True)
class Personality:
    label: str
    description: str


_PERSONALITIES: list[Personality] = [
    Personality(
        label="Enthusiastic",
        description=(
            "Genuinely excited. High energy and expressive. Positive emotion comes through "
            "naturally without feeling forced. Exclamations feel earned."
        ),
    ),
    Personality(
        label="Calm and practical",
        description=(
            "Matter-of-fact. States what happened, whether it worked, and gives a verdict. "
            "No drama, no hyperbole. Trust is built through understatement."
        ),
    ),
    Personality(
        label="Grateful and warm",
        description=(
            "Genuinely appreciative. Thanks the team or acknowledges the effort in a human way. "
            "Warmth without being gushing or performative."
        ),
    ),
    Personality(
        label="Pleasantly surprised (slight skeptic)",
        description=(
            "Came in without high expectations — pleasantly proved wrong. "
            "Review reflects being won over. Slightly understated but genuinely positive."
        ),
    ),
    Personality(
        label="Storyteller",
        description=(
            "Builds context before landing the verdict. Sets a small scene or describes a moment. "
            "Review reads like they're telling a friend about the trip."
        ),
    ),
]


# ── Die 5: Typing Style ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TypingStyle:
    label: str
    description: str


_TYPING_STYLES: list[TypingStyle] = [
    TypingStyle(
        label="Fast phone typer",
        description=(
            "Short bursts of thought. Doesn't overthink punctuation or grammar. "
            "May skip commas. Occasionally runs sentences together. Direct and unpolished."
        ),
    ),
    TypingStyle(
        label="Careful and structured writer",
        description=(
            "Full, complete sentences. Proper punctuation. Reads like they thought about "
            "what to say before typing. Consistent and clear."
        ),
    ),
    TypingStyle(
        label="Natural Hinglish code-switcher",
        description=(
            "Moves between Hindi and English mid-thought — not forced, just how they think. "
            "The Hindi words emerge where they feel more natural than the English equivalent."
        ),
    ),
    TypingStyle(
        label="Gen-Z internet style",
        description=(
            "Very brief. Minimal punctuation. May use casual internet abbreviations "
            "where they'd genuinely use them. Maximum meaning with minimum words."
        ),
    ),
    TypingStyle(
        label="Formal and measured",
        description=(
            "Polite, complete language. Would not use slang. "
            "Reads like a considered feedback response, not a casual tap."
        ),
    ),
]


# ── Die 6: What They Prioritize ───────────────────────────────────────────────

@dataclass(frozen=True)
class Priority:
    label: str
    focus_note: str  # what aspect of the trip their review naturally gravitates toward


_PRIORITIES: list[Priority] = [
    Priority(
        label="Value for money",
        focus_note=(
            "Their review gravitates toward whether the trip was worth the cost. "
            "Not necessarily cheap — just fair and worthwhile."
        ),
    ),
    Priority(
        label="Physical comfort and convenience",
        focus_note=(
            "Notices quality of vehicle, hotel room, road conditions, ease of travel. "
            "The physical experience of the journey matters to them."
        ),
    ),
    Priority(
        label="The experience and memories",
        focus_note=(
            "Focuses on what they saw, felt, and experienced — the wildlife, the views, "
            "a specific moment. The memory is the measure."
        ),
    ),
    Priority(
        label="Reliability and logistics",
        focus_note=(
            "Cares most about things running smoothly — punctuality, pre-arrangement, "
            "no last-minute surprises. Good logistics = good trip for this person."
        ),
    ),
    Priority(
        label="Nature, scenery, and environment",
        focus_note=(
            "Most moved by the forest, the mountains, the river, the birds, the morning mist. "
            "The place itself — not the service — is what they write about most."
        ),
    ),
]


# ── Die 7: Service — correlated with age + travel group ───────────────────────

def _compute_service_weights(age: AgeBucket, group: TravelGroup) -> list[float]:
    """
    Compute service selection weights based on who this person is.
    Order maps to ALL_SERVICES: [safari, hotel, taxi, tour, sightseeing]

    Not random — real people's demographics influence what they book.
    Still probabilistic — a 60yr old CAN book a safari, just less likely.
    """
    # Base weights: [safari, hotel, taxi, tour, sightseeing]
    # Priority order requested: tour, hotel, safari, sightseeing, taxi
    w = [0.20, 0.25, 0.08, 0.35, 0.12]

    # Age adjustments
    if age.label in ("50s", "60s+"):
        w[0] -= 0.08  # deep safari less likely for older travelers
        w[4] += 0.05  # sightseeing more comfortable
        w[3] += 0.03  # tour packages (including pilgrimage) preferred
    elif age.label == "20s":
        w[0] += 0.07  # safari is the exciting option for young travelers
        w[2] += 0.04  # budget cab/taxi very common for young

    # Travel group adjustments
    if group.label == "Family with young children":
        w[3] += 0.10  # pre-arranged tour package most practical
        w[1] += 0.03  # hotel stay important for families
        w[0] -= 0.08  # deep jungle safari less practical with small kids
    elif group.label == "Friends group trip":
        w[0] += 0.08  # safari is the group adventure choice
        w[3] += 0.03
    elif group.label == "Traveling with parents or senior family members":
        w[4] += 0.10  # sightseeing easiest for seniors
        w[3] += 0.04  # pre-arranged tour best for senior travel
        w[0] -= 0.10  # rough safari terrain not ideal for seniors
    elif group.label == "Couple (anniversary or leisure trip)":
        w[1] += 0.04  # hotel/resort stay matters for couples
        w[4] += 0.04  # scenic sightseeing
    elif group.label == "Solo traveler":
        w[2] += 0.08  # taxi/cab most useful for solo travelers
        w[0] += 0.04

    # Clamp minimum probability and normalize to 1.0
    w = [max(0.04, x) for x in w]
    total = sum(w)
    return [x / total for x in w]


# ── PersonaCard ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PersonaCard:
    """
    A fully composed persona for one review generation.
    Contains all 7 dice rolls in a single coherent package.
    """
    seed: int
    age: AgeBucket           # Die 1
    region: Region           # Die 2
    travel_group: TravelGroup  # Die 3
    personality: Personality   # Die 4
    typing_style: TypingStyle  # Die 5
    priority: Priority         # Die 6
    service: ServiceContext    # Die 7 — correlated, not independent
    length: LengthProfile
    temperature_offset: float
    resolved_context_str: str  # The specific scenario string for this roll


# ── Roll function ──────────────────────────────────────────────────────────────

def roll_persona() -> PersonaCard:
    """
    Roll all 7 dice to compose a unique, internally coherent persona.

    Dice 1–6 are independent. Die 7 (service) uses weights computed
    from Die 1 (age) + Die 3 (travel group) for realistic correlation.

    Each call gets a fresh seed — fully reproducible if needed.
    """
    seed = random.randint(10000, 99999)
    rng = random.Random(seed)

    age          = rng.choices(_AGE_BUCKETS,      weights=_AGE_WEIGHTS,          k=1)[0]
    region       = rng.choices(_REGIONS,           weights=_REGION_WEIGHTS,       k=1)[0]
    travel_group = rng.choices(_TRAVEL_GROUPS,     weights=_TRAVEL_GROUP_WEIGHTS, k=1)[0]
    personality  = rng.choice(_PERSONALITIES)
    typing_style = rng.choice(_TYPING_STYLES)
    priority     = rng.choice(_PRIORITIES)
    length       = rng.choices(_LENGTH_PROFILES,   weights=_LENGTH_WEIGHTS,       k=1)[0]

    # Die 7: service correlated with age + travel group
    service_weights = _compute_service_weights(age, travel_group)
    service = rng.choices(ALL_SERVICES, weights=service_weights, k=1)[0]
    
    # Resolve the final specific scenario in Python using the same rng seed
    resolved_context = service.get_context(rng)

    temperature_offset = rng.uniform(-0.10, 0.10)

    return PersonaCard(
        seed=seed,
        age=age,
        region=region,
        travel_group=travel_group,
        personality=personality,
        typing_style=typing_style,
        priority=priority,
        service=service,
        length=length,
        temperature_offset=temperature_offset,
        resolved_context_str=resolved_context,
    )


# ── Prompt formatter ───────────────────────────────────────────────────────────

def format_persona_for_prompt(card: PersonaCard) -> str:
    """
    Convert a PersonaCard into a purely descriptive character profile
    for injection into the LLM system prompt.

    Design rule: Describe WHO this person IS.
    Do NOT prescribe specific words, phrases, or Hinglish examples.
    The LLM infers natural language from the character — not from a vocabulary menu.
    This prevents any single phrase from repeating across reviews.
    """
    return f"""── THIS REVIEWER (seed #{card.seed}) ──

WHO THEY ARE:
A person in their {card.age.label}, from {card.region.label}.
Traveling as: {card.travel_group.label}

THEIR CHARACTER:
{card.personality.description}

WHAT MATTERED MOST TO THEM ON THIS TRIP:
{card.priority.focus_note}

HOW THEY WRITE:
{card.typing_style.description}
Cultural language texture: {card.region.language_note}
Age and energy context: {card.age.character_note}
Travel group lens: {card.travel_group.perspective_note}

REVIEW LENGTH: {card.length.label} — {card.length.word_hint}
  → {card.length.description}
  → Aim for {card.length.sentence_range[0]} to {card.length.sentence_range[1]} sentences

WRITE AS THIS PERSON — fully inhabit their voice.
Adopt their energy level, grammar habits, sentence rhythm, and cultural background completely.
If their natural style includes small imperfections, let them be.
If they would write three words and stop, stop there.
Do NOT sand down their voice into smooth, polished AI prose."""
