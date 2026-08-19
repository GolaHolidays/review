"""
Service-specific prompt snippets for Gola Holidays review generation.

Instead of one giant prompt covering ALL services, each service has its
own small, focused context block. The randomizer picks ONE per call.

This means the LLM only sees context for ONE service at a time — producing
more specific, accurate, and varied reviews.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceContext:
    """A focused service context block for a single review generation."""
    service_id: str       # e.g., "safari", "hotel", "taxi"
    service_name: str     # human-readable name
    context: str          # the actual prompt text injected into system prompt
    weight: float         # selection probability (safari is their main service)


# ── SERVICE 1: JIM CORBETT SAFARI ─────────────────────────────────────────────

_SAFARI = ServiceContext(
    service_id="safari",
    service_name="Jim Corbett Safari",
    weight=0.30,
    context="""SERVICE YOU USED: Jim Corbett jungle safari booked through Gola Holidays.

Pick ONE specific safari scenario and write about ONLY that:

JEEP SAFARI ZONES (pick one):
- Bijrani Zone — dense forest, popular for tiger sightings
- Jhirna Zone — open grassland, elephants and leopard, open all year
- Garjia Zone — near Garjia Devi Temple, birds and deer
- Dhikala Zone — deep core zone, dramatic experience, permits very limited
- Durga Devi Zone — remote, river views, less crowded
- Sitabani Zone — buffer zone, no permit, quieter jungle walk

OTHER SAFARI TYPES:
- Canter Safari into Dhikala — shared open vehicle, early morning, misty forest roads
- Forest Rest House stay — sleeping inside the park, jungle sounds at night

WILDLIFE YOU MIGHT HAVE SEEN (pick one or two, not all):
- Tiger sighting (rare, makes the whole trip)
- Elephant herd crossing the road
- Gharial/crocodile on the Ramganga riverbank
- Peacocks, hornbills, spotted deer

WHAT GOLA DID: permit booking (limited availability), jeep + guide arranged, morning/evening slot, pickup from station/resort

Company: Gola Holidays, Ramnagar, Uttarakhand. Local team since 2010.""",
)


# ── SERVICE 2: HOTEL / RESORT STAY ───────────────────────────────────────────

_HOTEL = ServiceContext(
    service_id="hotel",
    service_name="Hotel / Resort Booking",
    weight=0.15,
    context="""SERVICE YOU USED: Hotel or resort booked through Gola Holidays.

Pick ONE specific location and write about ONLY that stay:

RESORTS NEAR CORBETT (Ramnagar area):
- Jungle-facing resort — wildlife sounds at night
- River-facing resort on Kosi or Ramganga river — flowing water sounds, outdoor seating
- Budget lodge in Ramnagar town — clean, simple, good for one night

HOTELS IN OTHER UTTARAKHAND DESTINATIONS (pick one):
- Nainital — lake-view hotel, Mall Road walking distance
- Bhimtal — quieter than Nainital, lakeside, peaceful
- Rishikesh — Ganga-view, yoga/meditation vibe
- Haridwar — near ghats, Ganga aarti visible
- Auli — snow views, Nanda Devi peak backdrop
- Mussoorie — hillside, valley view, Mall Road nearby
- Munsiyari — remote Himalayan stay, Panchachuli peaks on clear mornings

WHAT GUESTS NOTICED: Gola matched them to right property for budget, no check-in surprises, hotel was as described

Company: Gola Holidays, Ramnagar, Uttarakhand. Local team since 2010.""",
)


# ── SERVICE 3: TAXI / CAB SERVICE ────────────────────────────────────────────

_TAXI = ServiceContext(
    service_id="taxi",
    service_name="Taxi / Cab Service",
    weight=0.20,
    context="""SERVICE YOU USED: Taxi or cab service from Gola Holidays.

Pick ONE specific route/scenario and write about ONLY that ride:

AIRPORT TRANSFERS:
- Pantnagar Airport → Ramnagar / Corbett
- Jolly Grant Airport (Dehradun) → Rishikesh / Haridwar / Mussoorie

RAILWAY STATION TRANSFERS:
- Kathgodam Station → Nainital / Bhimtal / Munsiyari / Ranikhet
- Kathgodam Station → Ramnagar / Corbett
- Ramnagar Station → resort / hotel
- Haridwar Station → Rishikesh / Dehradun

LONG ROUTES:
- Delhi → Nainital (overnight or early morning drive)
- Delhi → Haridwar / Rishikesh
- Kathgodam → Munsiyari (long mountain drive, scenic)
- Ramnagar → Corbett zones

VEHICLES (mention if relevant):
- Swift Dzire / Etios — couples, solo
- Innova Crysta — family of 4-5, comfortable on mountain roads
- Tempo Traveller — group of 8-12

WHAT GUESTS NOTICED: driver on time, clean vehicle, no haggling, knew the roads well, helpful with luggage

Company: Gola Holidays, Ramnagar, Uttarakhand. Local team since 2010.""",
)


# ── SERVICE 4: TOUR PACKAGES ─────────────────────────────────────────────────

_TOUR = ServiceContext(
    service_id="tour",
    service_name="Tour Package (Multi-day)",
    weight=0.20,
    context="""SERVICE YOU USED: Multi-day tour package from Gola Holidays.

Pick ONE specific package and write about ONLY that trip:

WILDLIFE PACKAGE:
- Jim Corbett 2N/3D — stay + safari + sightseeing included

HILL STATION PACKAGES (pick one):
- Nainital 3N/4D — Naini Lake, Tiffin Top, Mall Road, Bhimtal day trip
- Bhimtal + Naukuchiatal — quieter lakes circuit
- Mussoorie 2N/3D — Kempty Falls, Company Garden, Cable Car
- Munsiyari 4N/5D — "Little Kashmir", Khaliya Top, Milam Glacier base
- Auli 3N/4D — skiing (winter), Gorson Bugyal meadow (summer), Nanda Devi views
- Ranikhet 2N/3D — peaceful cantonment, apple orchards, Chaubatia gardens
- Kausani 2N/3D — sunrise over Himalayan peaks, Anasakti Ashram

PILGRIMAGE PACKAGES (pick one):
- Kedarnath Yatra — helicopter or trek option
- Char Dham Yatra — Yamunotri, Gangotri, Kedarnath, Badrinath (all 4)
- Do Dham — Kedarnath + Badrinath only
- Haridwar + Rishikesh spiritual trip

ADVENTURE / TREKKING:
- Valley of Flowers + Hemkund Sahib (July-September)
- Roopkund Trek
- Pindari Glacier Trek
- Khaliya Top, Munsiyari

WHAT GUESTS NOTICED: everything pre-arranged, good itinerary pacing, driver + guide knew the area, good value

Company: Gola Holidays, Ramnagar, Uttarakhand. Local team since 2010.""",
)


# ── SERVICE 5: SIGHTSEEING ───────────────────────────────────────────────────

_SIGHTSEEING = ServiceContext(
    service_id="sightseeing",
    service_name="Local Sightseeing",
    weight=0.15,
    context="""SERVICE YOU USED: Local sightseeing trip arranged by Gola Holidays.

Pick ONE specific area and write about ONLY those spots:

AROUND JIM CORBETT / RAMNAGAR:
- Garjia Devi Temple — hillside temple on a rock in the Kosi river, scenic
- Corbett Falls — waterfall in the forest, short trail
- Corbett Museum (Choti Haldwani) — Jim Corbett's old home, historical
- Ramganga river viewpoint — sunset spot

NAINITAL SIGHTSEEING:
- Naini Lake boat ride
- Tiffin Top (Dorothy's Seat) — panoramic Himalayan view
- Snow View Point (cable car)
- Naina Devi Temple
- Bhimtal Lake, Sattal, Naukuchiatal day trips

WHAT GUESTS NOTICED: driver doubled as a local guide, knew best times, no rushed schedule, showed hidden spots tourists usually miss

Company: Gola Holidays, Ramnagar, Uttarakhand. Local team since 2010.""",
)


# ── All services list ─────────────────────────────────────────────────────────

ALL_SERVICES: list[ServiceContext] = [_SAFARI, _HOTEL, _TAXI, _TOUR, _SIGHTSEEING]
_SERVICE_WEIGHTS: list[float] = [s.weight for s in ALL_SERVICES]


def pick_random_service() -> ServiceContext:
    """
    Pick one service using weighted random selection.
    
    Safari has the highest weight (0.30) since it's Gola's primary business.
    Each call independently rolls — no memory of previous selections.
    """
    return random.choices(ALL_SERVICES, weights=_SERVICE_WEIGHTS, k=1)[0]
