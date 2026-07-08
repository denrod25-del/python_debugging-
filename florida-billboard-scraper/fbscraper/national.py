"""National seed dataset: billboard / OOH companies across the top-10 US cities.

Top-10 US cities by population (city proper): New York, Los Angeles, Chicago,
Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas, Jacksonville.

Compiled from public web sources on 2026-07-08 (company sites, market listings,
industry directories). Same caveat as the Florida seed: this is a real, usable
starting list, not the exhaustive permit-level roster — there is no single
national equivalent of Florida's FDOT licensee database, so local operators are
gathered market by market.

For the national workbook the Company fields are repurposed:
  * counties_served     -> which of the top-10 cities the company serves
  * serves_palm_beach   -> "Yes" = national / multi-market operator (highlighted)
  * city / state        -> the company's HQ / main office
Header labels are overridden accordingly in build_national().
"""
from __future__ import annotations

from typing import List

from .models import (
    Company,
    TYPE_NATIONAL,
    TYPE_REGIONAL,
    TYPE_INDEPENDENT,
    TYPE_MOBILE,
    TYPE_BROKER,
)

TOP_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "Jacksonville",
]

_REF = "Static ~$1k–$25k+/4wk; premium/spectacular boards much higher (market avg)"

# Header overrides so the repurposed columns read correctly in the workbook/CSV.
HEADER_OVERRIDES = {
    "counties_served": "Top-10 Cities Served",
    "serves_palm_beach": "National / multi-market",
    "city": "HQ City",
    "state": "HQ State",
    "primary_market": "Primary Market(s)",
}


NATIONAL_SEED: List[Company] = [
    # ------------------------------------------------------------------ #
    # THE BIG THREE — present in essentially every top-10 city
    # ------------------------------------------------------------------ #
    Company(
        company_name="Lamar Advertising",
        company_type=TYPE_NATIONAL,
        primary_market="Nationwide (largest US billboard network)",
        counties_served="Los Angeles; Houston; Phoenix; San Antonio; San Diego; Dallas; Jacksonville (+ most US metros)",
        serves_palm_beach="Yes",
        city="Baton Rouge",
        state="LA",
        website="https://lamar.com/",
        pricing_reference=_REF,
        notes="Largest US OOH operator; ~350k+ displays. Strong in LA, TX, AZ, San Diego (I-5/I-805/I-15/Hwy 78), Jacksonville.",
        source="lamar.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Clear Channel Outdoor",
        company_type=TYPE_NATIONAL,
        primary_market="Nationwide (top-3 US operator)",
        counties_served="New York; Los Angeles; Chicago; Houston; Phoenix; Philadelphia; San Antonio; San Diego; Dallas; Jacksonville",
        serves_palm_beach="Yes",
        city="San Antonio",
        state="TX",
        website="https://clearchanneloutdoor.com/",
        pricing_reference=_REF,
        notes="Big-three operator; ~$2.1B revenue. e.g. Phoenix ~500 displays reaching 88% of adults 18+ weekly.",
        source="clearchanneloutdoor.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="OUTFRONT Media",
        company_type=TYPE_NATIONAL,
        primary_market="Nationwide (top-3 US operator; major transit)",
        counties_served="New York; Los Angeles; Chicago; Houston; Phoenix; Philadelphia; San Antonio; San Diego; Dallas; Jacksonville",
        serves_palm_beach="Yes",
        city="New York",
        state="NY",
        website="https://www.outfront.com/",
        pricing_reference=_REF,
        notes="Big-three operator; runs NYC MTA transit advertising. Billboards + transit in all top-10 markets.",
        source="outfront.com; WebSearch 2026-07-08",
        confidence="High",
    ),

    # ------------------------------------------------------------------ #
    # NATIONAL / MULTI-MARKET INDEPENDENTS & PREMIUM NETWORKS
    # ------------------------------------------------------------------ #
    Company(
        company_name="New Tradition Media",
        company_type=TYPE_NATIONAL,
        primary_market="Premium spectaculars: NYC Times Sq, LA Hollywood, Chicago",
        counties_served="New York; Los Angeles; Chicago",
        serves_palm_beach="Yes",
        city="Chicago",
        state="IL",
        website="https://www.newtradition.com/",
        pricing_reference="Premium / spectacular placements — quote only, high-end",
        notes="Large-format 'spectacular' billboards in marquee locations (Times Square, Hollywood).",
        source="newtradition.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Capitol Outdoor",
        company_type=TYPE_NATIONAL,
        primary_market="Chicago; Los Angeles; Manhattan; Philadelphia; San Diego; Miami",
        counties_served="New York; Los Angeles; Chicago; Philadelphia; San Diego",
        serves_palm_beach="Yes",
        website="https://capitoloutdoor.com/",
        pricing_reference=_REF,
        notes="Digital billboards, kiosks, wallscapes across major markets.",
        source="capitoloutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Brooklyn Outdoor",
        company_type=TYPE_REGIONAL,
        primary_market="New York DMA; Los Angeles; Chicago",
        counties_served="New York; Los Angeles; Chicago",
        serves_palm_beach="Yes",
        city="New York",
        state="NY",
        website="https://brooklynoutdoor.com/",
        pricing_reference=_REF,
        notes="Woman-owned OOH firm; billboards, wallscapes, experiential.",
        source="brooklynoutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Digital Outdoor Advertising, LLC",
        company_type=TYPE_NATIONAL,
        primary_market="Coast-to-coast digital network (200+ markets)",
        counties_served="Philadelphia; Jacksonville (+ 200 US markets)",
        serves_palm_beach="Yes",
        website="https://digitaloutdooradvertising.com/",
        pricing_reference=_REF,
        notes="20,000+ digital & static billboards across 200+ markets incl. Philadelphia and Jacksonville.",
        source="digitaloutdooradvertising.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Becker Boards",
        company_type=TYPE_REGIONAL,
        primary_market="Phoenix (+ SF, Miami, Ft. Lauderdale, Orlando, Chicago)",
        counties_served="Phoenix; Chicago",
        serves_palm_beach="Yes",
        city="Phoenix",
        state="AZ",
        website="https://www.beckerboards.com/",
        pricing_reference=_REF,
        notes="Digital, static & wallscape billboards; city-wide greater-Phoenix coverage.",
        source="beckerboards.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="AltTerrain",
        company_type=TYPE_MOBILE,
        primary_market="Mobile & street-level: NYC, Chicago, LA",
        counties_served="New York; Chicago; Los Angeles",
        serves_palm_beach="Yes",
        website="https://altterrain.com/",
        pricing_reference="Mobile / street-level placements — quote only",
        notes="Mobile billboards + street-level media (bodegas, laundromats, barbershops).",
        source="altterrain.com; WebSearch 2026-07-08",
        confidence="Low",
    ),

    # ------------------------------------------------------------------ #
    # TEXAS (Houston / Dallas / San Antonio)
    # ------------------------------------------------------------------ #
    Company(
        company_name="SignAd Outdoor Advertising",
        company_type=TYPE_REGIONAL,
        primary_market="Texas (Houston-based) + parts of Louisiana",
        counties_served="Houston; San Antonio; Dallas",
        serves_palm_beach="No",
        city="Houston",
        state="TX",
        website="https://www.signad.com/",
        pricing_reference=_REF,
        notes="Largest independently owned OOH company in Texas; 2,600+ displays.",
        source="signad.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="BM Outdoor Media",
        company_type=TYPE_REGIONAL,
        primary_market="44 Texas cities + Phoenix",
        counties_served="Houston; Dallas; San Antonio; Phoenix",
        serves_palm_beach="No",
        website="https://bmoutdoor.com/",
        pricing_reference=_REF,
        notes="Billboards, digital, transit & street furniture across 44 TX cities and Phoenix.",
        source="bmoutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Lux Media",
        company_type=TYPE_MOBILE,
        primary_market="Dallas; Houston; Austin; San Antonio",
        counties_served="Houston; San Antonio; Dallas",
        serves_palm_beach="No",
        website="https://www.luxmediaads.com/",
        pricing_reference="Mobile LED truck — day/route rate, quote only",
        notes="Mobile LED billboard truck advertising across major TX metros.",
        source="luxmediaads.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Billboards America",
        company_type=TYPE_BROKER,
        primary_market="Texas (Dallas, Houston, Austin, San Antonio, Fort Worth)",
        counties_served="Houston; Dallas; San Antonio",
        serves_palm_beach="No",
        website="https://www.billboardsamerica.com/billboard-advertising-locations/texas",
        pricing_reference=_REF,
        notes="Brokerage with access to prime TX billboard locations.",
        source="billboardsamerica.com; WebSearch 2026-07-08",
        confidence="Low",
    ),
    Company(
        company_name="Premier Mobile Billboards",
        company_type=TYPE_MOBILE,
        primary_market="Houston metro",
        counties_served="Houston",
        serves_palm_beach="No",
        city="Houston",
        state="TX",
        website="https://premiermobilebillboards.com/houston/",
        pricing_reference="Mobile LED truck — quote only",
        notes="Digital billboard trucks; Houston + Woodlands, Sugar Land, Katy.",
        source="premiermobilebillboards.com; WebSearch 2026-07-08",
        confidence="Low",
    ),

    # ------------------------------------------------------------------ #
    # PHOENIX
    # ------------------------------------------------------------------ #
    Company(
        company_name="Arizona Billboard Company",
        company_type=TYPE_INDEPENDENT,
        primary_market="Phoenix / Arizona",
        counties_served="Phoenix",
        serves_palm_beach="No",
        city="Phoenix",
        state="AZ",
        website="https://arizonabillboardcompany.com/",
        pricing_reference=_REF,
        notes="30+ yrs; billboards, digital LED, buses, shelters, airports, stadiums.",
        source="arizonabillboardcompany.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),

    # ------------------------------------------------------------------ #
    # SAN DIEGO
    # ------------------------------------------------------------------ #
    Company(
        company_name="American Outdoor Advertising",
        company_type=TYPE_INDEPENDENT,
        primary_market="San Diego",
        counties_served="San Diego",
        serves_palm_beach="No",
        website="https://www.americanoutdoor.com/",
        pricing_reference=_REF,
        notes="Digital & static billboards on high-traffic San Diego routes.",
        source="americanoutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),

    # ------------------------------------------------------------------ #
    # JACKSONVILLE
    # ------------------------------------------------------------------ #
    Company(
        company_name="MediaLease OOH — Jacksonville",
        company_type=TYPE_REGIONAL,
        primary_market="Jacksonville",
        counties_served="Jacksonville",
        serves_palm_beach="No",
        website="https://www.medialeaseooh.com/jacksonville-fl/",
        pricing_reference=_REF,
        notes="Digital LED + traditional billboards, bus, rail, shelter ads in Jacksonville.",
        source="medialeaseooh.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
]


def load_national() -> List[Company]:
    return [Company(**{k: v for k, v in vars(c).items()}) for c in NATIONAL_SEED]
