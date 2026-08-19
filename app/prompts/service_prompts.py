"""
Service-specific context blocks for Gola Holidays review generation.

Each ServiceContext provides factual background about ONE service.
To prevent the LLM from deterministically picking the first bullet point every time,
the specific scenario/route/hotel is chosen randomly in Python via `get_context(rng)`.
The LLM only ever sees ONE scenario to write about per generation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceContext:
    """Factual context about a single Gola Holidays service."""
    service_id: str       # e.g., "safari", "hotel", "taxi"
    service_name: str     # human-readable name
    base_context: str     # general background info
    scenarios: list[str]  # specific routes, zones, or packages

    def get_context(self, rng: random.Random) -> str:
        """Pick a specific scenario randomly in Python so the LLM doesn't just pick the first one."""
        scenario = rng.choice(self.scenarios)
        return (
            f"{self.base_context}\n\n"
            f"SPECIFIC SCENARIO TO WRITE ABOUT (Focus only on this):\n- {scenario}"
        )


# ── SERVICE 1: JIM CORBETT SAFARI ─────────────────────────────────────────────

_SAFARI = ServiceContext(
    service_id="safari",
    service_name="Jim Corbett Safari",
    base_context=(
        "SERVICE: Jim Corbett jungle safari booked through Gola Holidays.\n"
        "WHAT GOLA ARRANGED: permit booking, safari vehicle, and guide.\n"
        "Company: Gola Holidays, Ramnagar, Uttarakhand."
    ),
    scenarios=[
        "Bijrani Zone (Jeep Safari) — dense sal forest, high tiger activity, spotted a tiger, jeep picked us up from resort",
        "Jhirna Zone (Jeep Safari) — open grassland, saw elephants and leopard, morning slot",
        "Garjia Zone (Jeep Safari) — near Garjia Devi Temple, lots of birds and spotted deer, resort pickup",
        "Dhikala Zone (Day Visit via Canter Safari) — shared open Canter bus starting from Ramnagar town (no resort pickup), deep core zone, very limited permits, saw a tusker",
        "Durga Devi Zone (Jeep Safari) — remote, river views, less crowded, crocodile on Ramganga riverbank",
        "Sitabani Zone (Jeep Safari) — buffer zone, no permit needed, quieter, peacocks and hornbills",
        "Forest Rest House stay (Night Stay inside Dhikala) — sleeping inside the core park, exclusive jeep safari inside, jungle sounds at night"
    ],
)


# ── SERVICE 2: HOTEL / RESORT STAY ────────────────────────────────────────────

_HOTEL = ServiceContext(
    service_id="hotel",
    service_name="Hotel / Resort Booking",
    base_context=(
        "SERVICE: Hotel or resort stay booked through Gola Holidays.\n"
        "WHAT GOLA ARRANGED: matched property to budget, confirmed booking, no check-in surprises.\n"
        "Company: Gola Holidays, Ramnagar, Uttarakhand."
    ),
    scenarios=[
        "Corbett: Jungle-facing resort — wildlife sounds at night, forest atmosphere",
        "Corbett: River-facing resort on Kosi or Ramganga — water sounds, outdoor seating",
        "Corbett: Budget lodge in Ramnagar town — clean, simple, practical",
        "Nainital: Lake-view hotel, short walking distance to Mall Road",
        "Bhimtal: Quieter lakeside property, peaceful and away from city noise",
        "Rishikesh: Ganga view property, calm and spiritual atmosphere",
        "Haridwar: Hotel near the ghats, easy access for evening aarti",
        "Auli: Mountain resort with snow views and Nanda Devi peak backdrop",
        "Mussoorie: Hillside property with valley view, near Mall Road",
        "Munsiyari: Remote Himalayan stay, Panchachuli peaks visible on clear mornings"
    ],
)


# ── SERVICE 3: TAXI / CAB SERVICE ─────────────────────────────────────────────

_TAXI = ServiceContext(
    service_id="taxi",
    service_name="Taxi / Cab Service",
    base_context=(
        "SERVICE: Taxi or cab arranged through Gola Holidays.\n"
        "WHAT GOLA ARRANGED: cab booking, vehicle assignment, driver coordination.\n"
        "Company: Gola Holidays, Ramnagar, Uttarakhand."
    ),
    scenarios=[
        "Airport Transfer: Pantnagar Airport → Ramnagar / Corbett (Swift Dzire or Etios)",
        "Airport Transfer: Jolly Grant Airport (Dehradun) → Rishikesh / Haridwar (Innova)",
        "Railway Transfer: Kathgodam Station → Nainital / Bhimtal (Innova Crysta)",
        "Railway Transfer: Kathgodam Station → Ramnagar / Corbett (Swift Dzire)",
        "Railway Transfer: Ramnagar Station → Corbett resort (Tempo Traveller)",
        "Long Route: Delhi → Nainital overnight drive (Innova Crysta)",
        "Long Route: Delhi → Haridwar / Rishikesh (Swift Dzire)",
        "Long Route: Kathgodam → Munsiyari long scenic mountain drive (Innova Crysta)",
        "Long Route: Ramnagar → Corbett safari zones (Local Jeep)"
    ],
)


# ── SERVICE 4: TOUR PACKAGES ───────────────────────────────────────────────────

_TOUR = ServiceContext(
    service_id="tour",
    service_name="Tour Package (Multi-day)",
    base_context=(
        "SERVICE: Multi-day tour package from Gola Holidays.\n"
        "WHAT GOLA ARRANGED: itinerary, accommodation, transport, guide, permit where needed.\n"
        "Company: Gola Holidays, Ramnagar, Uttarakhand."
    ),
    scenarios=[
        "Wildlife: Jim Corbett 2N/3D — stay + safari + local sightseeing",
        "Hill Station: Nainital 3N/4D — Naini Lake, Tiffin Top, Mall Road, Bhimtal day trip",
        "Hill Station: Bhimtal + Naukuchiatal 2N/3D — quieter lakes circuit",
        "Hill Station: Mussoorie 2N/3D — Kempty Falls, Company Garden, Cable Car",
        "Hill Station: Munsiyari 4N/5D — 'Little Kashmir', Khaliya Top, Milam Glacier base",
        "Hill Station: Auli 3N/4D — skiing in winter, meadows in summer, Nanda Devi views",
        "Hill Station: Ranikhet 2N/3D — peaceful cantonment, apple orchards",
        "Hill Station: Kausani 2N/3D — sunrise over Himalayan peaks",
        "Pilgrimage: Kedarnath Yatra — helicopter or trek option",
        "Pilgrimage: Char Dham Yatra — Yamunotri, Gangotri, Kedarnath, Badrinath",
        "Pilgrimage: Haridwar + Rishikesh 2N/3D spiritual trip",
        "Adventure: Valley of Flowers + Hemkund Sahib trekking package"
    ],
)


# ── SERVICE 5: LOCAL SIGHTSEEING ──────────────────────────────────────────────

_SIGHTSEEING = ServiceContext(
    service_id="sightseeing",
    service_name="Local Sightseeing",
    base_context=(
        "SERVICE: Local sightseeing trip arranged by Gola Holidays.\n"
        "WHAT GOLA ARRANGED: cab and driver for the day, route planning, local area knowledge.\n"
        "Company: Gola Holidays, Ramnagar, Uttarakhand."
    ),
    scenarios=[
        "Corbett Area: Garjia Devi Temple — hillside temple on a rock in the Kosi river",
        "Corbett Area: Corbett Falls — waterfall in the forest, short trail",
        "Corbett Area: Corbett Museum (Choti Haldwani) — Jim Corbett's old home",
        "Corbett Area: Ramganga river viewpoint — popular sunset spot",
        "Nainital: Naini Lake boat ride and Mall Road stroll",
        "Nainital: Tiffin Top (Dorothy's Seat) — panoramic Himalayan view",
        "Nainital: Snow View Point (cable car) and Naina Devi Temple",
        "Nainital: Day trip covering Bhimtal Lake, Sattal, and Naukuchiatal"
    ],
)


# ── All services list ──────────────────────────────────────────────────────────
# Used by review_randomizer._compute_service_weights()
# Order matters: [safari, hotel, taxi, tour, sightseeing]

ALL_SERVICES: list[ServiceContext] = [_SAFARI, _HOTEL, _TAXI, _TOUR, _SIGHTSEEING]
