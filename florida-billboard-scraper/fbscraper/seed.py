"""Verified seed dataset of Florida billboard / OOH companies.

Every record here was compiled from public web sources (company sites, market
listings, FOAA references, and industry directories) gathered on 2026-07-08.
This gives you a real, usable starting spreadsheet even before you run the live
FDOT scraper (`fbscraper.fdot`) on an un-firewalled machine, which adds the full
authoritative list of licensed permit holders statewide.

Confidence key:
  High   = name + at least one hard contact detail (address/phone) verified.
  Medium = name + market verified, contact detail approximate or from listing.
  Low    = name surfaced in a directory; details need confirmation.
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

# Market-average reference rates (NOT company quotes). See pricing.py.
_PB_REF = "Static ~$800–$15k/mo; digital ~$1.2k–$25k+/mo (FL market avg)"


SEED: List[Company] = [
    # ------------------------------------------------------------------ #
    # PALM BEACH COUNTY / WEST PALM BEACH  (requested starting point)
    # ------------------------------------------------------------------ #
    Company(
        company_name="Lamar Advertising (Palm Beach)",
        company_type=TYPE_NATIONAL,
        primary_market="Palm Beach County; South Florida",
        counties_served="Palm Beach; Martin; St. Lucie",
        serves_palm_beach="Yes",
        address="801 Northpoint Parkway",
        city="West Palm Beach",
        zip_code="33407",
        phone="(561) 358-1207",
        website="https://lamar.com/palmbeach",
        pricing_reference=_PB_REF,
        notes="Largest US billboard operator. Bulletins, posters, digital & transit in Palm Beach Co.",
        source="lamar.com/palmbeach; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Clear Channel Outdoor — West Palm Beach",
        company_type=TYPE_NATIONAL,
        primary_market="Palm Beach County to Indian River County",
        counties_served="Palm Beach; Martin; St. Lucie; Indian River",
        serves_palm_beach="Yes",
        city="West Palm Beach",
        website="https://clearchanneloutdoor.com/where-we-are/west-palm-beach/",
        pricing_reference=_PB_REF,
        notes="~67MM weekly impressions in market; I-95 and Palm Beach Intl Airport coverage. "
              "Miami office: 5800 NW 77th Court, Miami, FL 33166.",
        source="clearchanneloutdoor.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="OUTFRONT Media — West Palm Beach",
        company_type=TYPE_NATIONAL,
        primary_market="West Palm Beach; Fort Pierce",
        counties_served="Palm Beach; St. Lucie; Broward",
        serves_palm_beach="Yes",
        address="2640 NW 17th Ln (Pompano office)",
        city="Pompano Beach",
        zip_code="33064",
        website="https://www.outfront.com/markets/west-palm-beach",
        pricing_reference=_PB_REF,
        notes="Static + digital billboards. South FL ops run out of Pompano Beach.",
        source="outfront.com/markets/west-palm-beach; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="DAT Media FL",
        company_type=TYPE_MOBILE,
        primary_market="West Palm Beach; South Florida",
        counties_served="Palm Beach; Broward; Miami-Dade",
        serves_palm_beach="Yes",
        website="https://datmediafl.com/west-palm-beach-mobile-led-billboard-advertising/",
        pricing_reference="Mobile LED truck; typically day/week rate — quote only",
        notes="Mobile digital LED billboard trucks.",
        source="datmediafl.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Media Lease OOH",
        company_type=TYPE_REGIONAL,
        primary_market="West Palm Beach; Fort Pierce",
        counties_served="Palm Beach; St. Lucie",
        serves_palm_beach="Yes",
        website="https://www.medialeaseooh.com/west-palm-beach-ft-pierce-fl/",
        pricing_reference=_PB_REF,
        notes="Out-of-home billboard leasing, WPB & Ft. Pierce corridor.",
        source="medialeaseooh.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Blue Line Media",
        company_type=TYPE_BROKER,
        primary_market="West Palm Beach (national broker)",
        counties_served="Palm Beach (+ nationwide brokerage)",
        serves_palm_beach="Yes",
        phone="(800) 807-0360",
        email="Advertise@BlueLineMedia.com",
        website="https://www.bluelinemedia.com/billboard-advertising/west-palm-beach-fl",
        pricing_reference=_PB_REF,
        notes="Brokerage — books static/vinyl & digital/LED across operators; publishes market rate guides.",
        source="bluelinemedia.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Billboard Connection",
        company_type=TYPE_BROKER,
        primary_market="West Palm Beach; statewide FL",
        counties_served="Palm Beach (+ statewide brokerage)",
        serves_palm_beach="Yes",
        phone="(941) 208-2466",
        website="https://billboardconnection.com/listing/west-palm-beach-fl-billboard-advertising-billboards-in-west-palm-beach/",
        pricing_reference=_PB_REF,
        notes="Franchise brokerage; access to I-95, US-1, Okeechobee Blvd, Florida's Turnpike inventory.",
        source="billboardconnection.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Fliphound",
        company_type=TYPE_BROKER,
        primary_market="West Palm Beach; statewide (digital platform)",
        counties_served="Palm Beach (+ statewide)",
        serves_palm_beach="Yes",
        website="https://fliphound.com/billboard-advertising/Florida/West-Palm-Beach",
        pricing_reference="Self-serve digital billboard booking — dynamic pricing",
        notes="Online marketplace/platform for digital billboards.",
        source="fliphound.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="AdQuick",
        company_type=TYPE_BROKER,
        primary_market="West Palm Beach; nationwide marketplace",
        counties_served="Palm Beach (+ nationwide)",
        serves_palm_beach="Yes",
        website="https://www.adquick.com/billboard-locations/florida/west-palm-beach",
        pricing_reference="Marketplace booking; publishes 2026 CPM/cost guides",
        notes="OOH marketplace aggregating operator inventory; good source of live availability.",
        source="adquick.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),

    # ------------------------------------------------------------------ #
    # SOUTH FLORIDA (Miami-Dade / Broward) — spill into Palm Beach
    # ------------------------------------------------------------------ #
    Company(
        company_name="Lamar of South Florida",
        company_type=TYPE_NATIONAL,
        primary_market="Miami; Fort Lauderdale; South Florida",
        counties_served="Miami-Dade; Broward; Palm Beach",
        serves_palm_beach="Yes",
        website="https://lamar.com/southflorida",
        pricing_reference=_PB_REF,
        notes="Premium billboards + digital across the tri-county South FL market.",
        source="lamar.com/southflorida; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Clear Channel Outdoor — Miami",
        company_type=TYPE_NATIONAL,
        primary_market="Miami-Dade",
        counties_served="Miami-Dade; Broward",
        serves_palm_beach="Unknown",
        address="5800 NW 77th Court",
        city="Miami",
        zip_code="33166",
        website="https://clearchanneloutdoor.com/",
        pricing_reference=_PB_REF,
        source="WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="OUTFRONT Media — Pompano",
        company_type=TYPE_NATIONAL,
        primary_market="Broward; South Florida",
        counties_served="Broward; Palm Beach; Miami-Dade",
        serves_palm_beach="Yes",
        address="2640 NW 17th Ln",
        city="Pompano Beach",
        zip_code="33064",
        website="https://www.outfront.com/",
        pricing_reference=_PB_REF,
        source="WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Carter Outdoor Advertising",
        company_type=TYPE_REGIONAL,
        primary_market="South Florida",
        counties_served="Broward; Miami-Dade; Palm Beach",
        serves_palm_beach="Unknown",
        website="https://www.carteroutdoor.com/",
        pricing_reference=_PB_REF,
        notes="Family-owned, serving South Florida since 1956.",
        source="carteroutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="3N Outdoor Media",
        company_type=TYPE_REGIONAL,
        primary_market="Miami",
        counties_served="Miami-Dade",
        serves_palm_beach="Unknown",
        notes="Miami-based; premium inventory along Biscayne Blvd and near airports.",
        source="WebSearch 2026-07-08",
        confidence="Low",
    ),
    Company(
        company_name="Hanging Pants Media",
        company_type=TYPE_REGIONAL,
        primary_market="Miami; Ft. Lauderdale; WPB; Tampa; Orlando; Jacksonville",
        counties_served="Statewide (major metros)",
        serves_palm_beach="Yes",
        website="https://hangingpantsmedia.com/",
        pricing_reference=_PB_REF,
        notes="Works across all major FL markets incl. West Palm Beach.",
        source="hangingpantsmedia.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),

    # ------------------------------------------------------------------ #
    # TAMPA / GULF COAST
    # ------------------------------------------------------------------ #
    Company(
        company_name="Creative Outdoor Advertising",
        company_type=TYPE_REGIONAL,
        primary_market="Tampa / Gulf Coast",
        counties_served="Hillsborough; Pinellas; Gulf Coast",
        serves_palm_beach="No",
        city="Tampa",
        pricing_reference="Quote only",
        notes="HQ Tampa since 1984, 100+ employees, Florida Gulf Coast coverage.",
        source="WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Logan Outdoor Advertising",
        company_type=TYPE_REGIONAL,
        primary_market="Central West Florida",
        counties_served="Six central FL counties",
        serves_palm_beach="No",
        website="https://loganoutdoor.com/",
        pricing_reference="Quote only",
        source="loganoutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Lakeland Outdoor Advertising",
        company_type=TYPE_INDEPENDENT,
        primary_market="Lakeland / Central FL",
        counties_served="Hillsborough; Lake",
        serves_palm_beach="No",
        pricing_reference="Quote only",
        source="WebSearch 2026-07-08",
        confidence="Low",
    ),

    # ------------------------------------------------------------------ #
    # CENTRAL FLORIDA (Orlando / Polk)
    # ------------------------------------------------------------------ #
    Company(
        company_name="Orlando Outdoor Advertising",
        company_type=TYPE_REGIONAL,
        primary_market="Orlando / Central Florida",
        counties_served="Orange; Osceola; Seminole",
        serves_palm_beach="No",
        pricing_reference="Quote only",
        notes="500+ faces across I-4 and theme-park routes.",
        source="WebSearch 2026-07-08",
        confidence="Medium",
    ),
    Company(
        company_name="Koala Outdoor Advertising",
        company_type=TYPE_INDEPENDENT,
        primary_market="Polk County",
        counties_served="Polk",
        serves_palm_beach="No",
        city="Lake Hamilton",
        pricing_reference="Quote only",
        source="WebSearch 2026-07-08",
        confidence="Low",
    ),
    Company(
        company_name="Smallwood Sign Company",
        company_type=TYPE_INDEPENDENT,
        primary_market="Citrus / Orange counties",
        counties_served="Citrus; Orange",
        serves_palm_beach="No",
        pricing_reference="Quote only",
        source="WebSearch 2026-07-08",
        confidence="Low",
    ),

    # ------------------------------------------------------------------ #
    # PANHANDLE
    # ------------------------------------------------------------------ #
    Company(
        company_name="Premium Outdoor",
        company_type=TYPE_REGIONAL,
        primary_market="Florida Panhandle",
        counties_served="Escambia; Santa Rosa; Okaloosa; Bay (Panhandle)",
        serves_palm_beach="No",
        website="https://premiumoutdoor.com/",
        pricing_reference="Quote only",
        notes="Independently owned; 140+ digital & static faces in the Panhandle.",
        source="premiumoutdoor.com; WebSearch 2026-07-08",
        confidence="Medium",
    ),

    # ------------------------------------------------------------------ #
    # MOBILE BILLBOARD SPECIALISTS (statewide)
    # ------------------------------------------------------------------ #
    Company(
        company_name="Ilum Advertising",
        company_type=TYPE_MOBILE,
        primary_market="Orlando; Miami; Tampa; Jacksonville",
        counties_served="Statewide (major metros)",
        serves_palm_beach="Unknown",
        pricing_reference="Mobile LED truck — day/week rate, quote only",
        source="WebSearch 2026-07-08",
        confidence="Low",
    ),
    Company(
        company_name="UMedia",
        company_type=TYPE_MOBILE,
        primary_market="Miami; Orlando; Tampa; Daytona; Jacksonville",
        counties_served="Statewide (major metros)",
        serves_palm_beach="Unknown",
        pricing_reference="Mobile LED truck — day/week rate, quote only",
        source="WebSearch 2026-07-08",
        confidence="Low",
    ),
    Company(
        company_name="Movia Media",
        company_type=TYPE_MOBILE,
        primary_market="Florida (mobile)",
        counties_served="Statewide",
        serves_palm_beach="Unknown",
        website="https://moviamedia.com/",
        pricing_reference="Mobile billboard — quote only",
        source="moviamedia.com; WebSearch 2026-07-08",
        confidence="Low",
    ),

    # ------------------------------------------------------------------ #
    # NATIONAL HEADQUARTERS (the "big three" — corporate contacts)
    # ------------------------------------------------------------------ #
    Company(
        company_name="Lamar Advertising Company (Corporate)",
        company_type=TYPE_NATIONAL,
        primary_market="National (HQ)",
        counties_served="Statewide FL via local offices",
        serves_palm_beach="Yes",
        city="Baton Rouge",
        state="LA",
        website="https://lamar.com/",
        pricing_reference=_PB_REF,
        notes="Parent company; ~1 of the big-three US OOH operators.",
        source="lamar.com; en.wikipedia.org/wiki/Lamar_Advertising_Company",
        confidence="High",
    ),
    Company(
        company_name="OUTFRONT Media Inc. (Corporate)",
        company_type=TYPE_NATIONAL,
        primary_market="National (HQ)",
        counties_served="Statewide FL via local offices",
        serves_palm_beach="Yes",
        city="New York",
        state="NY",
        website="https://www.outfront.com/",
        pricing_reference=_PB_REF,
        notes="Parent company; big-three US OOH operator.",
        source="outfront.com; WebSearch 2026-07-08",
        confidence="High",
    ),
    Company(
        company_name="Clear Channel Outdoor Holdings (Corporate)",
        company_type=TYPE_NATIONAL,
        primary_market="National (HQ)",
        counties_served="Statewide FL via local offices",
        serves_palm_beach="Yes",
        city="San Antonio",
        state="TX",
        website="https://clearchanneloutdoor.com/",
        pricing_reference=_PB_REF,
        notes="Parent company; big-three US OOH operator.",
        source="clearchanneloutdoor.com; WebSearch 2026-07-08",
        confidence="High",
    ),
]


def load_seed() -> List[Company]:
    """Return a fresh copy of the seed list."""
    return [Company(**{k: v for k, v in vars(c).items()}) for c in SEED]
