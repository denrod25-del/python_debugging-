"""US metro marketing-market reference for the 42 metros in the OOH dataset.

Combines:
  * the scraped billboard/OOH data (companies, rate bands, per-metro coverage)
    imported live from ../florida-billboard-scraper/fbscraper/national.py, and
  * per-metro marketing-market facts below: Nielsen DMA rank (2024-25, approx),
    metro (MSA) population, dominant daily newspaper, and city business journal.

DMA ranks and populations are stable public reference figures (Nielsen 2024-25;
Census MSA estimates 2024) and are marked approximate. Newspapers / business
journals are the primary print advertising venues per market.
"""
from __future__ import annotations

import sys
import os

# Import the billboard dataset from the sibling project.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "florida-billboard-scraper"))
import fbscraper.national as nat  # noqa: E402

# Metro -> (DMA rank approx, MSA population, major daily newspaper, business journal)
METRO_MEDIA = {
    "New York":       (1,  "19.9M", "The New York Times / NY Post / Daily News", "Crain's New York Business"),
    "Los Angeles":    (2,  "13.0M", "Los Angeles Times", "Los Angeles Business Journal"),
    "Chicago":        (3,  "9.4M",  "Chicago Tribune / Sun-Times", "Crain's Chicago Business"),
    "San Francisco":  (10, "4.6M (Bay CSA ~9.7M)", "San Francisco Chronicle", "San Francisco Business Times"),
    "Atlanta":        (6,  "6.4M",  "The Atlanta Journal-Constitution", "Atlanta Business Chronicle"),
    "Washington DC":  (8,  "6.3M",  "The Washington Post", "Washington Business Journal"),
    "Boston":         (9,  "4.9M",  "The Boston Globe", "Boston Business Journal"),
    "Dallas":         (4,  "8.1M",  "The Dallas Morning News", "Dallas Business Journal"),
    "Houston":        (7,  "7.5M",  "Houston Chronicle", "Houston Business Journal"),
    "Miami":          (18, "6.2M",  "Miami Herald", "South Florida Business Journal"),
    "Philadelphia":   (5,  "6.2M",  "The Philadelphia Inquirer", "Philadelphia Business Journal"),
    "Detroit":        (15, "4.3M",  "Detroit Free Press / The Detroit News", "Crain's Detroit Business"),
    "Seattle":        (12, "4.0M",  "The Seattle Times", "Puget Sound Business Journal"),
    "Minneapolis":    (14, "3.7M",  "Star Tribune", "Minneapolis/St. Paul Business Journal"),
    "Phoenix":        (11, "5.1M",  "The Arizona Republic", "Phoenix Business Journal"),
    "Tampa":          (13, "3.3M",  "Tampa Bay Times", "Tampa Bay Business Journal"),
    "Denver":         (16, "3.0M",  "The Denver Post", "Denver Business Journal"),
    "Cleveland":      (19, "2.2M",  "The Plain Dealer / cleveland.com", "Crain's Cleveland Business"),
    "Sacramento":     (20, "2.4M",  "The Sacramento Bee", "Sacramento Business Journal"),
    "Orlando":        (17, "2.8M",  "Orlando Sentinel", "Orlando Business Journal"),
    "St. Louis":      (24, "2.8M",  "St. Louis Post-Dispatch", "St. Louis Business Journal"),
    "Pittsburgh":     (26, "2.4M",  "Pittsburgh Post-Gazette", "Pittsburgh Business Times"),
    "San Diego":      (29, "3.3M",  "The San Diego Union-Tribune", "San Diego Business Journal"),
    "Baltimore":      (28, "2.8M",  "The Baltimore Sun", "Baltimore Business Journal"),
    "Charlotte":      (21, "2.8M",  "The Charlotte Observer", "Charlotte Business Journal"),
    "Raleigh":        (23, "1.5M (Triangle ~2.1M)", "The News & Observer", "Triangle Business Journal"),
    "Indianapolis":   (25, "2.1M",  "The Indianapolis Star", "Indianapolis Business Journal"),
    "Cincinnati":     (35, "2.3M",  "The Cincinnati Enquirer", "Cincinnati Business Courier"),
    "Las Vegas":      (40, "2.3M",  "Las Vegas Review-Journal", "Vegas Inc / LVRJ Business Press"),
    "San Antonio":    (31, "2.6M",  "San Antonio Express-News", "San Antonio Business Journal"),
    "Portland":       (22, "2.5M",  "The Oregonian", "Portland Business Journal"),
    "Milwaukee":      (36, "1.6M",  "Milwaukee Journal Sentinel", "Milwaukee Business Journal"),
    "Columbus":       (32, "2.2M",  "The Columbus Dispatch", "Columbus Business First"),
    "Kansas City":    (34, "2.2M",  "The Kansas City Star", "Kansas City Business Journal"),
    "Nashville":      (27, "2.1M",  "The Tennessean", "Nashville Business Journal"),
    "Salt Lake City": (30, "1.3M",  "The Salt Lake Tribune / Deseret News", "Utah Business"),
    "New Orleans":    (50, "1.3M",  "The Times-Picayune / NOLA.com / The Advocate", "New Orleans CityBusiness"),
    "Oklahoma City":  (42, "1.5M",  "The Oklahoman", "The Journal Record"),
    "Memphis":        (46, "1.3M",  "The Commercial Appeal", "Memphis Business Journal"),
    "Richmond":       (56, "1.3M",  "Richmond Times-Dispatch", "Richmond BizSense"),
    "Austin":         (37, "2.5M",  "Austin American-Statesman", "Austin Business Journal"),
    "Jacksonville":   (45, "1.7M",  "The Florida Times-Union", "Jacksonville Business Journal"),
}


def metro_reference_rows():
    """Return list of dict rows for the US Metro Reference sheet (market-size order)."""
    comps = nat.load_national()
    rate = {c: (lo, hi, tier, note) for (r, c, st, tier, lo, hi, note) in
            [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in nat.CITY_MARKET]}
    state = {r[1]: r[2] for r in nat.CITY_MARKET}
    rows = []
    for i, city in enumerate(nat.TOP_CITIES, 1):
        lo, hi, tier, note = rate[city]
        n_ops = sum(1 for c in comps if city in nat.cities_for(c))
        dma, pop, paper, bizj = METRO_MEDIA.get(city, ("-", "-", "-", "-"))
        rows.append({
            "rank": i,
            "metro": city,
            "state": state.get(city, ""),
            "dma": dma,
            "pop": pop,
            "rate": f"${lo:,}-${hi:,}",
            "ops": n_ops,
            "paper": paper,
            "bizj": bizj,
            "note": note,
        })
    return rows


def metro_company_rows():
    """Return list of dict rows for the Metro OOH Companies sheet."""
    comps = nat.load_national()
    order = {c: i for i, c in enumerate(nat.TOP_CITIES)}

    def keyfn(c):
        served = nat.cities_for(c)
        first = min((order[m] for m in served), default=999)
        return (0 if (c.serves_palm_beach or "").lower() == "yes" else 1, first, c.company_name.lower())

    rows = []
    for c in sorted(comps, key=keyfn):
        served = nat.cities_for(c)
        # The billboard Company model defaults state to "FL"; only trust HQ when a
        # city is explicitly set (avoids showing a spurious "FL" for national brokers).
        hq = f"{c.city}, {c.state}".strip(", ") if c.city else ""
        rows.append({
            "company": c.company_name,
            "type": c.company_type,
            "metros": "; ".join(served) if len(served) <= 6 else f"Nationwide ({len(served)} metros)",
            "hq": hq,
            "website": c.website,
            "pricing": c.pricing_reference or c.pricing,
            "confidence": c.confidence,
        })
    return rows
