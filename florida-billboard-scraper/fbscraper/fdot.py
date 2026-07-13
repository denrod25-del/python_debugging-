"""Scrape the authoritative FDOT Outdoor Advertising (ODA) database.

The Florida Dept. of Transportation licenses every legal billboard in the state
and publishes the inventory of permit holders (licensees) and permitted
structures. This is THE definitive list of billboard companies in Florida,
with a county field so you can filter to Palm Beach first.

Primary sources (all public, no login):
  * Licensees report : https://oda.fdot.gov/EmbeddedReport/Licensees
  * Monthly data file : https://oda.fdot.gov/OdaDataFile   (Excel, all structures)
  * Legacy download   : https://www2.dot.state.fl.us/rightofway/DownloadData.aspx

NOTE ON RUNNING THIS:
  FDOT sits behind a WAF and many locked-down / cloud egress networks block
  *.fdot.gov entirely (including the sandbox this was authored in). Run this
  module from a normal machine or residential/office network. If you still get
  403s, the monthly Excel can be downloaded by hand from the pages above and
  fed to `parse_oda_workbook(path)`.
"""
from __future__ import annotations

import io
import time
from typing import List, Optional

import requests

from .models import Company, TYPE_NATIONAL

LICENSEES_URL = "https://oda.fdot.gov/EmbeddedReport/Licensees"
DATA_FILE_URL = "https://oda.fdot.gov/OdaDataFile"
LEGACY_DOWNLOAD = "https://www2.dot.state.fl.us/rightofway/DownloadData.aspx"

# County-code / name map is not needed to filter — the ODA file carries a
# textual county field. Palm Beach appears as "PALM BEACH".
PALM_BEACH = "PALM BEACH"

_HEADERS = {
    # A real browser UA gets past most of FDOT's basic bot rules.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}


def _get(url: str, retries: int = 4, timeout: int = 45) -> requests.Response:
    """GET with browser headers and exponential backoff."""
    last: Optional[Exception] = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as exc:  # noqa: BLE001 - network layer, want broad catch
            last = exc
            wait = 2 ** attempt
            print(f"  [fdot] {url} failed ({exc}); retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"FDOT request failed after {retries} tries: {url}") from last


def fetch_licensees() -> List[Company]:
    """Fetch and parse the FDOT Licensees report into Company records."""
    from bs4 import BeautifulSoup  # local import so seed-only runs need no bs4

    resp = _get(LICENSEES_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    companies: List[Company] = []

    # The embedded SSRS-style report renders as an HTML table. We read every
    # row and map the columns we recognise; the report layout is stable but we
    # stay defensive about header names.
    for table in soup.find_all("table"):
        header_cells = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if not header_cells:
            first_row = table.find("tr")
            if first_row:
                header_cells = [td.get_text(strip=True).lower()
                                for td in first_row.find_all(["td", "th"])]
        if not any("licens" in h or "name" in h for h in header_cells):
            continue

        def col(row_cells, *names):
            for i, h in enumerate(header_cells):
                if any(n in h for n in names) and i < len(row_cells):
                    return row_cells[i]
            return ""

        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if not cells or not any(cells):
                continue
            name = col(cells, "name", "licens").strip()
            if not name:
                continue
            companies.append(Company(
                company_name=name,
                company_type=TYPE_NATIONAL if any(
                    k in name.lower() for k in ("lamar", "clear channel", "outfront")
                ) else "Licensed operator (FDOT)",
                counties_served=col(cells, "county"),
                address=col(cells, "address", "street"),
                city=col(cells, "city"),
                zip_code=col(cells, "zip"),
                phone=col(cells, "phone"),
                notes="FDOT-licensed outdoor advertising business.",
                source="FDOT ODA Licensees report",
                confidence="High",
            ))
    return companies


def parse_oda_workbook(path_or_bytes) -> List[Company]:
    """Parse the monthly ODA structures Excel into unique company records.

    Accepts a filesystem path or raw bytes. The workbook has one row per
    permitted structure; we collapse to unique permit-holder/business names and
    record which counties each one operates in (Palm Beach flagged).
    """
    import openpyxl

    if isinstance(path_or_bytes, (bytes, bytearray)):
        wb = openpyxl.load_workbook(io.BytesIO(path_or_bytes), read_only=True, data_only=True)
    else:
        wb = openpyxl.load_workbook(path_or_bytes, read_only=True, data_only=True)
    ws = wb.active

    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip().lower() if h is not None else "" for h in next(rows)]

    def idx(*names):
        for i, h in enumerate(header):
            if any(n in h for n in names):
                return i
        return None

    i_name = idx("business", "permittee", "owner", "company", "name")
    i_county = idx("county")
    i_city = idx("city")
    i_addr = idx("address", "street")

    by_name: dict[str, Company] = {}
    for row in rows:
        if not row or i_name is None or i_name >= len(row):
            continue
        name = str(row[i_name] or "").strip()
        if not name:
            continue
        county = str(row[i_county] or "").strip() if i_county is not None else ""
        key = name.lower()
        if key not in by_name:
            by_name[key] = Company(
                company_name=name,
                company_type="Licensed operator (FDOT)",
                counties_served=county,
                city=str(row[i_city] or "").strip() if i_city is not None else "",
                address=str(row[i_addr] or "").strip() if i_addr is not None else "",
                notes="Holds FDOT outdoor-advertising permits.",
                source="FDOT ODA monthly data file",
                confidence="High",
            )
        else:
            existing = by_name[key]
            counties = {c.strip() for c in existing.counties_served.split(";") if c.strip()}
            if county:
                counties.add(county)
            existing.counties_served = "; ".join(sorted(counties))

    companies = list(by_name.values())
    for c in companies:
        if PALM_BEACH in c.counties_served.upper():
            c.serves_palm_beach = "Yes"
    return companies


def fetch_data_file() -> Optional[List[Company]]:
    """Download the monthly ODA Excel and parse it. Returns None on failure."""
    try:
        resp = _get(DATA_FILE_URL)
    except RuntimeError as exc:
        print(f"  [fdot] could not download ODA data file: {exc}")
        return None
    ctype = resp.headers.get("content-type", "")
    if "html" in ctype.lower():
        print("  [fdot] ODA data-file endpoint returned HTML (likely WAF/redirect); "
              "download the Excel by hand and use parse_oda_workbook().")
        return None
    return parse_oda_workbook(resp.content)


def scrape(county: Optional[str] = None) -> List[Company]:
    """Best-effort live FDOT scrape. `county` filters (e.g. 'PALM BEACH')."""
    companies: List[Company] = []
    try:
        companies.extend(fetch_licensees())
    except Exception as exc:  # noqa: BLE001
        print(f"  [fdot] licensees fetch failed: {exc}")

    data = fetch_data_file()
    if data:
        companies.extend(data)

    if county:
        cu = county.upper()
        companies = [c for c in companies if cu in (c.counties_served or "").upper()]
    return companies
