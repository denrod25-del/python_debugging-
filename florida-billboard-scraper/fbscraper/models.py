"""Data model for a Florida billboard / out-of-home advertising company."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


# Canonical column order used everywhere (Excel headers, CSV, dedupe).
COLUMNS = [
    "company_name",
    "company_type",
    "primary_market",
    "counties_served",
    "serves_palm_beach",
    "address",
    "city",
    "state",
    "zip_code",
    "phone",
    "email",
    "website",
    "pricing",
    "pricing_reference",
    "notes",
    "source",
    "confidence",
]

# Human-friendly headers for the spreadsheet.
HEADERS = {
    "company_name": "Company Name",
    "company_type": "Type",
    "primary_market": "Primary Market(s)",
    "counties_served": "Counties Served",
    "serves_palm_beach": "Serves Palm Beach Co.",
    "address": "Street Address",
    "city": "City",
    "state": "State",
    "zip_code": "ZIP",
    "phone": "Phone",
    "email": "Email",
    "website": "Website",
    "pricing": "Pricing (availability)",
    "pricing_reference": "Reference Rate (market avg)",
    "notes": "Notes",
    "source": "Source",
    "confidence": "Confidence",
}

# Company type taxonomy.
TYPE_NATIONAL = "National operator"
TYPE_REGIONAL = "Regional operator"
TYPE_INDEPENDENT = "Independent / local operator"
TYPE_MOBILE = "Mobile / LED-truck operator"
TYPE_BROKER = "Broker / agency / marketplace"


@dataclass
class Company:
    company_name: str
    company_type: str = ""
    primary_market: str = ""
    counties_served: str = ""
    serves_palm_beach: str = ""          # "Yes" / "No" / "Unknown"
    address: str = ""
    city: str = ""
    state: str = "FL"
    zip_code: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    pricing: str = "Quote only — request from company"
    pricing_reference: str = ""
    notes: str = ""
    source: str = ""
    confidence: str = "Medium"           # High / Medium / Low

    def key(self) -> str:
        """Dedupe key: normalized company name."""
        return "".join(ch for ch in self.company_name.lower() if ch.isalnum())

    def as_row(self) -> List[str]:
        d = asdict(self)
        return [str(d.get(c, "") or "") for c in COLUMNS]


def dedupe(companies: List[Company]) -> List[Company]:
    """Merge companies sharing a normalized-name key; later fields fill gaps."""
    merged: dict[str, Company] = {}
    for c in companies:
        k = c.key()
        if not k:
            continue
        if k not in merged:
            merged[k] = c
            continue
        existing = merged[k]
        for col in COLUMNS:
            if not getattr(existing, col, "") and getattr(c, col, ""):
                setattr(existing, col, getattr(c, col))
        # Keep the richer source trail.
        if c.source and c.source not in existing.source:
            existing.source = "; ".join(filter(None, [existing.source, c.source]))
    return list(merged.values())
