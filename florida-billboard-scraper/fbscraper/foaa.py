"""Scrape the Florida Outdoor Advertising Association (FOAA) member directory.

FOAA's member list is the best single directory of *active* Florida billboard
operators organized by region: https://www.foaa.org/member-companies-by-region

Like FDOT, the FOAA site (Wix-hosted) returns 403 to non-browser clients on some
networks. If `scrape()` comes back empty, run it from a normal network or fall
back to the seed dataset + FDOT.
"""
from __future__ import annotations

import time
from typing import List, Optional

import requests

from .models import Company, TYPE_REGIONAL

MEMBERS_URL = "https://www.foaa.org/member-companies-by-region"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape(retries: int = 4, timeout: int = 30) -> List[Company]:
    """Fetch the FOAA members-by-region page and parse company names/regions."""
    from bs4 import BeautifulSoup

    last: Optional[Exception] = None
    resp = None
    for attempt in range(retries):
        try:
            resp = requests.get(MEMBERS_URL, headers=_HEADERS, timeout=timeout)
            resp.raise_for_status()
            break
        except Exception as exc:  # noqa: BLE001
            last = exc
            wait = 2 ** attempt
            print(f"  [foaa] fetch failed ({exc}); retry in {wait}s")
            time.sleep(wait)
    if resp is None:
        print(f"  [foaa] giving up: {last}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    companies: List[Company] = []
    current_region = ""

    # FOAA groups members under region headings. Walk the DOM in order so each
    # company inherits the most recent heading as its region.
    for el in soup.find_all(["h1", "h2", "h3", "h4", "li", "p", "a"]):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        tag = el.name
        if tag in ("h1", "h2", "h3", "h4") and len(text) < 60:
            current_region = text
            continue
        # Heuristic: member entries usually carry OOH keywords.
        low = text.lower()
        if any(k in low for k in ("outdoor", "advertising", "media", "billboard", "sign")):
            link = el.get("href") if tag == "a" else ""
            companies.append(Company(
                company_name=text,
                company_type=TYPE_REGIONAL,
                primary_market=current_region,
                counties_served=current_region,
                serves_palm_beach="Yes" if "palm beach" in (current_region + low) else "Unknown",
                website=link or "",
                notes="FOAA member company.",
                source="foaa.org/member-companies-by-region",
                confidence="Medium",
            ))
    return companies
