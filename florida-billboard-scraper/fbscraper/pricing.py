"""Billboard pricing reference for Florida.

IMPORTANT — why there is no per-company "price" column full of numbers:

Billboard rates are NOT published. Operators quote per *specific face*, priced on
traffic count (impressions/DEC), board size, illumination, static vs. digital,
and contract length (a 4-week buy costs far more per week than a 52-week buy).
The same operator will quote wildly different numbers for two boards a mile
apart. So a scraper cannot return a real, honest "price" for a company — anyone
who tells you otherwise is publishing a marketing estimate, not a rate.

What we CAN provide, and do:
  * A per-company "Pricing (availability)" note = "Quote only — request from company"
    (plus the quote/booking channel where the company self-serves online).
  * Market-average REFERENCE ranges below, so you have a sanity-check band when
    quotes come back. These are Florida-market figures compiled 2026-07-08 from
    published cost guides (AdQuick, FitSmallBusiness, Carvertise, DashTwo, etc.).
"""
from __future__ import annotations

from typing import List, Tuple

# (segment, low, high, unit, note)
REFERENCE_RATES: List[Tuple[str, str, str, str, str]] = [
    ("Florida static billboard (overall)", "$800", "$15,000", "per 4 weeks",
     "Varies by market, size, traffic, illumination."),
    ("Florida digital billboard (overall)", "$1,200", "$25,000+", "per 4 weeks",
     "Roughly 30–50% above a comparable static face; rotating slot, no print cost."),
    ("US national average (any format)", "$3,953", "$3,953", "per 4 weeks",
     "2025 national average for a 4-week campaign."),
    ("Prime I-95 (e.g. Fort Lauderdale)", "$10,262", "$10,262", "per month",
     "Example premium-corridor rate; Miami/Ft. Lauderdale command premiums."),
    ("Static creative / vinyl production", "$850", "$850", "per creative",
     "One-time print & install per design; digital has none."),
    ("Mobile LED billboard truck", "—", "—", "per day / week",
     "Priced by hours/route, not monthly; always quote-only."),
]

PRICING_DISCLAIMER = (
    "Reference ranges are Florida market averages from public cost guides "
    "(2026-07-08), NOT quotes for any specific board. Always request a formal "
    "quote for the exact face, dates, and creative."
)
