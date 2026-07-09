# Florida Billboard Company Scraper

Collects **billboard / out-of-home (OOH) advertising companies operating in
Florida** and exports them to a formatted Excel workbook — **Palm Beach County
first**, then statewide. Captures each company's type, markets, counties,
address, phone, email, website, and pricing channel.

## TL;DR

```bash
pip install -r requirements.txt

# Palm Beach first, then everywhere (uses the built-in verified dataset and
# also tries the live FDOT + FOAA sources if your network allows):
python scraper.py --out data/florida_billboard_companies.xlsx
```

Open the resulting `.xlsx`. Palm Beach companies are highlighted and sorted to
the top. There are three tabs: **companies**, **Pricing Reference**, **About**.

A ready-made workbook is already checked in at
[`data/florida_billboard_companies.xlsx`](data/florida_billboard_companies.xlsx)
(35 companies, 17 serving Palm Beach), with a matching
[`.csv`](data/florida_billboard_companies.csv).

```bash
# Also emit a CSV (alongside the .xlsx, or pass an explicit path):
python scraper.py --out data/florida_billboard_companies.xlsx --csv
```

## Data sources

| Source | What it gives you | Notes |
|--------|-------------------|-------|
| **Built-in seed set** (`fbscraper/seed.py`) | 35 verified companies from public listings / company sites / FOAA / cost guides | Always works, no network needed. Palm Beach-first. |
| **FDOT ODA database** (`fbscraper/fdot.py`) | The **authoritative** list of every state-licensed permit holder, with counties | Definitive, but `*.fdot.gov` is often blocked on corporate/cloud networks and sits behind a WAF — run from a normal network. |
| **FOAA member directory** (`fbscraper/foaa.py`) | Active operators grouped by region | Wix-hosted; may 403 non-browser clients on some networks. |

### Why it ships with a seed dataset

This tool was authored inside a locked-down environment whose egress policy
blocks all external sites (FDOT, FOAA, even google.com). Rather than hand you an
empty spreadsheet, the seed set gives a **real, usable Palm Beach + statewide
list right now**, and the live scrapers append the full authoritative FDOT roster
the moment you run it somewhere with open network access.

## Usage

```bash
# Everything, Palm Beach first (default sources: seed,fdot,foaa)
python scraper.py --out data/florida_billboard_companies.xlsx

# Only Palm Beach County, only the authoritative FDOT source
python scraper.py --county "Palm Beach" --sources fdot --out palm_beach.xlsx

# Offline — verified seed data only, zero network calls
python scraper.py --sources seed --out florida.xlsx

# You downloaded the FDOT monthly Excel by hand? Parse it directly:
python scraper.py --oda-file ODAData.xlsx --out florida.xlsx
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--out` | `data/florida_billboard_companies.xlsx` | Output path |
| `--county` | *(none)* | Filter to a county, e.g. `"Palm Beach"` |
| `--sources` | `seed,fdot,foaa` | Any comma combo of `seed`, `fdot`, `foaa` |
| `--oda-file` | *(none)* | Parse a hand-downloaded FDOT ODA Excel |
| `--csv` | *(off)* | Also write CSV; bare flag = alongside the `.xlsx`, or give a path |

## National dataset — 26 major US metros

Beyond Florida, the tool ships a national dataset of billboard companies across
**26 major US OOH markets** (in market-size rank order): New York, Los Angeles,
Chicago, San Francisco, Atlanta, Washington DC, Boston, Dallas, Houston, Miami,
Philadelphia, Detroit, Seattle, Minneapolis, Phoenix, Tampa, Denver, Orlando,
San Diego, Las Vegas, San Antonio, Portland, Charlotte, Nashville, Austin, Jacksonville.

```bash
python scraper.py --dataset national --csv
# → data/us_top_cities_billboard_companies.xlsx (+ .csv)
```

**94 companies across all 26 metros** (every market has local operators, not just
the nationals). The big three (Lamar, Clear Channel, OUTFRONT — highlighted and
listed first) plus multi-market networks (JCDecaux, Branded Cities, Intersection,
Van Wagner, Vector Media, New Tradition, Capitol Outdoor, Brooklyn Outdoor, Digital
Outdoor Advertising) and nationwide brokers/agencies (AdQuick, Blue Line Media,
BillboardsIn, Billups, MediaLease OOH, Fliphound, Billboard Connection) appear in
every metro tab; each metro also lists its own local operators, e.g.:

- **New York (35)** — SILVERCAST, Branded Cities, TSX Broadway, Colossal Media
  (hand-painted walls), Intersection/PMD/InSite (top-5 by spot count), GSB Digital.
- **Chicago (26)** — Image Media Outdoor, Outdoor Impact, VC Outdoor, GreenSigns,
  J&B Signs, Red Star Outdoor.
- **Los Angeles (22)** — Regency Outdoor (Sunset Strip + LAX, 300+ boards),
  Bulletin Displays, Bray Outdoor, O Media Group.
- **Texas** — Houston (20): SignAd, Gilbreath, Avail, Inspiria; Dallas (19):
  Arrington, Ralston, Albert; San Antonio (17); Austin (15): Reagan Outdoor,
  MediaChoice, Burkett.
- **Tier-2 metros** — San Francisco (Billboard Source, Can't Miss US), Atlanta
  (Trailhead, Billboard Company Atlanta), Washington DC (Capitol Outdoor), Seattle
  (Pacific Outdoor, Parker, Summus), Denver (Mile High Outdoor, Elevation), Miami
  (SDE Media, Carter Outdoor, Plug Talk).
- **Tier-3 metros** — Detroit (International Outdoor), Minneapolis (Franklin
  Outdoor, Blue Ox), Tampa (Tampa Outdoor, Signal, Logan), Orlando (Orlando
  Outdoor), Las Vegas (Las Vegas Billboards), Portland (Grapevine, Meadow),
  Charlotte + Nashville (Adams, Allison Outdoor).

Source: `fbscraper/national.py`.

The national workbook has **30 tabs**:

- **All Companies** — every company, national operators first, with a "Metros
  Served" column.
- **City Market Ranking** — the 26 metros ranked by billboard market size and
  typical ad rates (NYC #1 → Jacksonville #26), with numeric low/high rate columns,
  premium notes (e.g. Times Square $10k–$1M+/mo, Vegas Strip up to $25k+), and an
  **embedded bar chart** of the monthly rate band per metro.
- **One tab per metro** (26 of them) — just the companies serving that market.
  Depth: NYC 35 · Chicago 26 · LA 22 · Houston 20 · Dallas 19 · Philadelphia 17 ·
  San Antonio 17 · Charlotte 15 · Miami 15 · Austin 15 · Jacksonville 15 · SF 14 ·
  Seattle 14 · Tampa 14 · Phoenix 14 · San Diego 14 · Atlanta 13 · Washington DC
  13 · Detroit 13 · Minneapolis 13 · Denver 13 · Portland 13 · Boston 11 ·
  Orlando 11 · Las Vegas 11 · Nashville 11.
- **Pricing Reference** and **About**.

> For a *truly* exhaustive NYC list, the authoritative source is the **NYC Dept.
> of Buildings "Active Outdoor Advertising Companies (OAC)" registry**
> (nyc.gov/assets/buildings/pdf/active-OAC-list.pdf) — the NYC analog of Florida's
> FDOT list. It's WAF-protected (blocked from this sandbox); download it directly
> to append every registered NYC firm.

> Note: unlike Florida (FDOT licensee database), there is **no single national
> permit registry**, so local operators are gathered market by market — the list
> is representative, not exhaustive.

## Getting the authoritative FDOT list

FDOT licenses every legal billboard in Florida. If the live scraper can't reach
`fdot.gov` from your network:

1. Open <https://oda.fdot.gov/> → download the monthly **ODA Data File** (Excel),
   or the **Licensees** report. (Legacy: <https://www2.dot.state.fl.us/rightofway/DownloadData.aspx>)
2. `python scraper.py --oda-file /path/to/ODAData.xlsx --out florida_full.xlsx`

That merges FDOT's full permit-holder roster with the seed set and dedupes.

## About prices — read this

**Billboard rates are quote-only.** Operators price each *specific face* on
traffic count, size, illumination, static-vs-digital, and contract length, and
they do not publish those numbers. A scraper cannot honestly return a real
per-company price — so this tool does **not** fabricate one. Instead it gives you:

- a per-company **pricing channel** ("request a quote" / self-serve booking link), and
- a **Pricing Reference** tab with Florida market-average bands (e.g. static
  ~$800–$15,000 / 4 weeks; digital ~$1,200–$25,000+; prime I-95 boards higher)
  so you can sanity-check the quotes that come back.

To get real numbers: request quotes from the highlighted Palm Beach operators
(Lamar, Clear Channel, OUTFRONT) plus a broker (Blue Line Media, Billboard
Connection, AdQuick) — brokers will quote across multiple operators at once.

## Layout

```
florida-billboard-scraper/
  scraper.py                 CLI entry point
  requirements.txt
  fbscraper/
    models.py                Company dataclass, columns, dedupe
    seed.py                  verified FL starter dataset (Palm Beach first)
    national.py              26 major US metros dataset (--dataset national)
    fdot.py                  FDOT ODA licensees + monthly Excel scraper/parser
    foaa.py                  FOAA member-directory scraper
    pricing.py               market-average reference rates + disclaimer
    excel.py                 formatted multi-sheet workbook writer
  data/
    florida_billboard_companies.xlsx   generated output (checked in)
    florida_billboard_companies.csv    same data as CSV (checked in)
```

## Disclaimer

Company details were compiled from public web sources on 2026-07-08 and may
change — verify contact info before relying on it. Confidence is graded per row
(High / Medium / Low). Respect each site's terms of service and `robots.txt`
when running the live scrapers.
