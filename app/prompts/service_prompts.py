"""
Service-specific context blocks for Gola Holidays review generation.

Each ServiceContext provides factual background about ONE service —
locations, scenarios, what Gola arranges — without prescribing
what words or phrases the reviewer should use.

The persona (review_randomizer.py) determines the voice and focus.
The service context provides the factual backdrop to write from.

Note: pick_random_service() has been removed.
      Service selection now lives in review_randomizer.roll_persona()
      as Die 7, correlated with age + travel group.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceContext:
    """Factual context about a single Gola Holidays service."""
    service_id: str       # e.g., "safari", "hotel", "taxi"
    service_name: str     # human-readable name
    context: str          # factual backdrop injected into system prompt


# ── SERVICE 1: JIM CORBETT SAFARI ─────────────────────────────────────────────

_SAFARI = ServiceContext(
    service_id="safari",
    service_name="Jim Corbett Safari",
    context="""SERVICE: Jim Corbett jungle safari booked through Gola Holidays.

Pick ONE specific safari scenario — write about only that:

JEEP SAFARI ZONES (pick one):
- Bijrani Zone — dense sal forest, high tiger activity
- Jhirna Zone — open grassland, elephants and leopard, open year-round
- Garjia Zone — near Garjia Devi Temple, birds and spotted deer
- Dhikala Zone — deep core zone, dramatic, very limited permits
- Durga Devi Zone — remote, river views, less crowded
- Sitabani Zone — buffer zone, no permit needed, quieter

OTHER SAFARI TYPES:
- Canter Safari into Dhikala — shared open vehicle, early morning, misty forest roads
- Forest Rest House stay — sleeping inside the park, jungle sounds at night

WILDLIFE (pick one or two, not all):
- Tiger sighting (rare and memorable)
- Elephant herd crossing
- Gharial or crocodile on Ramganga riverbank
- Peacocks, hornbills, spotted deer

WHAT GOLA ARRANGED: permit booking, jeep and guide, morning or evening slot, pickup from station or resort.

Company: Gola Holidays, Ramnagar, Uttarakhand.""",
)


# ── SERVICE 2: HOTEL / RESORT STAY ────────────────────────────────────────────

_HOTEL = ServiceContext(
    service_id="hotel",
    service_name="Hotel / Resort Booking",
    context="""SERVICE: Hotel or resort stay booked through Gola Holidays.

Pick ONE specific property type and location — write about only that:

NEAR CORBETT (Ramnagar area):
- Jungle-facing resort — wildlife sounds at night, forest atmosphere
- River-facing resort on Kosi or Ramganga — water sounds, outdoor seating
- Budget lodge in Ramnagar town — clean, simple, practical

OTHER UTTARAKHAND DESTINATIONS (pick one):
- Nainital — lake-view hotel, Mall Road proximity
- Bhimtal — quieter than Nainital, lakeside, peaceful
- Rishikesh — Ganga view, calm atmosphere
- Haridwar — near the ghats
- Auli — snow views, Nanda Devi peak backdrop
- Mussoorie — hillside valley view, Mall Road nearby
- Munsiyari — remote Himalayan stay, Panchachuli peaks on clear mornings

WHAT GOLA ARRANGED: matched property to budget, confirmed booking, no check-in surprises.

Company: Gola Holidays, Ramnagar, Uttarakhand.""",
)


# ── SERVICE 3: TAXI / CAB SERVICE ─────────────────────────────────────────────

_TAXI = ServiceContext(
    service_id="taxi",
    service_name="Taxi / Cab Service",
    context="""SERVICE: Taxi or cab arranged through Gola Holidays.

Pick ONE specific route — write about only that ride:

AIRPORT TRANSFERS:
- Pantnagar Airport → Ramnagar / Corbett
- Jolly Grant Airport (Dehradun) → Rishikesh / Haridwar / Mussoorie

RAILWAY STATION TRANSFERS:
- Kathgodam Station → Nainital / Bhimtal / Munsiyari / Ranikhet
- Kathgodam Station → Ramnagar / Corbett
- Ramnagar Station → resort or hotel
- Haridwar Station → Rishikesh / Dehradun

LONG MOUNTAIN ROUTES:
- Delhi → Nainital
- Delhi → Haridwar / Rishikesh
- Kathgodam → Munsiyari (long scenic mountain drive)
- Ramnagar → Corbett zones

VEHICLES (mention if relevant to the experience):
- Swift Dzire / Etios — for couples or solo travelers
- Innova Crysta — comfortable family vehicle, good on mountain roads
- Tempo Traveller — for groups of 8–12

WHAT GOLA ARRANGED: cab booking, vehicle assignment, driver coordination.

Company: Gola Holidays, Ramnagar, Uttarakhand.""",
)


# ── SERVICE 4: TOUR PACKAGES ───────────────────────────────────────────────────

_TOUR = ServiceContext(
    service_id="tour",
    service_name="Tour Package (Multi-day)",
    context="""SERVICE: Multi-day tour package from Gola Holidays.

Pick ONE specific package — write about only that trip:

WILDLIFE PACKAGE:
- Jim Corbett 2N/3D — stay + safari + local sightseeing

HILL STATION PACKAGES (pick one):
- Nainital 3N/4D — Naini Lake, Tiffin Top, Mall Road, Bhimtal day trip
- Bhimtal + Naukuchiatal — quieter lakes circuit
- Mussoorie 2N/3D — Kempty Falls, Company Garden, Cable Car
- Munsiyari 4N/5D — "Little Kashmir", Khaliya Top, Milam Glacier base
- Auli 3N/4D — skiing in winter, meadows in summer, Nanda Devi views
- Ranikhet 2N/3D — peaceful cantonment, apple orchards
- Kausani 2N/3D — sunrise over Himalayan peaks

PILGRIMAGE PACKAGES (pick one):
- Kedarnath Yatra — helicopter or trek option
- Char Dham Yatra — Yamunotri, Gangotri, Kedarnath, Badrinath
- Do Dham — Kedarnath + Badrinath
- Haridwar + Rishikesh spiritual trip

ADVENTURE / TREKKING:
- Valley of Flowers + Hemkund Sahib (July–September)
- Roopkund Trek
- Pindari Glacier Trek

WHAT GOLA ARRANGED: itinerary, accommodation, transport, guide, permit where needed.

Company: Gola Holidays, Ramnagar, Uttarakhand.""",
)


# ── SERVICE 5: LOCAL SIGHTSEEING ──────────────────────────────────────────────

_SIGHTSEEING = ServiceContext(
    service_id="sightseeing",
    service_name="Local Sightseeing",
    context="""SERVICE: Local sightseeing trip arranged by Gola Holidays.

Pick ONE specific area — write about only those spots:

AROUND JIM CORBETT / RAMNAGAR:
- Garjia Devi Temple — hillside temple on a rock in the Kosi river
- Corbett Falls — waterfall in the forest, short trail
- Corbett Museum (Choti Haldwani) — Jim Corbett's old home, historical
- Ramganga river viewpoint — popular sunset spot

NAINITAL SIGHTSEEING:
- Naini Lake boat ride
- Tiffin Top (Dorothy's Seat) — panoramic Himalayan view
- Snow View Point (cable car)
- Naina Devi Temple
- Bhimtal Lake, Sattal, Naukuchiatal day trips

WHAT GOLA ARRANGED: cab and driver for the day, route planning, local area knowledge.

Company: Gola Holidays, Ramnagar, Uttarakhand.""",
)


# ── All services list ──────────────────────────────────────────────────────────
# Used by review_randomizer._compute_service_weights()
# Order matters: [safari, hotel, taxi, tour, sightseeing]

ALL_SERVICES: list[ServiceContext] = [_SAFARI, _HOTEL, _TAXI, _TOUR, _SIGHTSEEING]
