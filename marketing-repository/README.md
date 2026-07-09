# B. Symbolic — US Marketing Master Reference (Expanded)

Expands the original **B. Symbolic Marketing Repository** (792 tactics, 13
categories — heavily OOH/local) into a near-complete marketing master list AND a
US market reference: **1,116 tactics across 25 categories** (+324 new) **plus a
42-metro market reference** — same schema and styling.

## Output

`data/BSymbolic_Marketing_Master_Expanded.xlsx` — 34 sheets:

- **Index** — clickable table of contents for every sheet
- **Legend** — how to use it (updated counts + notes)
- **Quick Wins** — auto-filtered 224 tactics: High relevance × $ cost × in-house
- **Palm Beach County ★** — the home market leads every metro sheet (rank 0,
  highlighted green) with its 17 verified PBC OOH operators and phone numbers
  pulled from the Florida billboard workbook
- **Master List** — all 1,116 tactics, filterable by Cost / Trades Relevance / In-House?
- **25 category tabs** — one per category
- **US Metro Reference** — the 42 largest US markets: market-size rank, Nielsen
  DMA rank (approx), metro population, OOH rate band ($/mo), # billboard operators,
  dominant daily newspaper, city business journal, **Big-4 TV affiliates, major
  radio ownership groups, notable ad agencies**, and market notes.
- **Metro OOH Companies** — 110 scraped billboard/OOH operators mapped to the
  metros they serve (type, HQ, website, pricing channel, confidence).
- **Quick-Start by Metro** — one row per market: OOH rate band, top *local*
  OOH operators (auto-selected from the scraped dataset), Big-4 TV, radio groups,
  newspaper, and agencies to call — plus the universal foundation steps (GBP +
  LSA + reviews → city pages/SEO → geofenced paid → local media).
- **Metro Category Contacts** — the searchable matrix: **all 13 original tactic
  categories × every metro = 546 rows**. Filter the Metro column to any city and
  you get its full contact card — local OOH operators, newspaper ad desk, big-4
  TV + cable ad sales, events/fairs/sports sponsorships, chamber of commerce,
  PR pitch targets. The Scope column marks each row **Metro** (green —
  market-specific vendor), **Mixed**, or **Universal** (grey — same self-serve
  platform everywhere, e.g. Google/Meta; you just geo-target it).
- **PBC Priority Playbook** — the original curated shortlist, preserved

> TV call signs are stable; radio is listed at ownership-group level; agency,
> event and chamber lists are flagship names per market — all reference-level,
> verify before buying.

The metro data is imported live from the sibling billboard project
(`../florida-billboard-scraper/fbscraper/national.py`) so the OOH companies and
rate bands stay in sync with that dataset. DMA ranks and populations are stable
public reference figures (Nielsen 2024-25; Census MSA 2024) marked approximate.

Every original tactic, the Legend, and the Playbook are preserved verbatim. The
schema is unchanged: **Cost** ($/$$/$$$), **Trades Relevance** (High/Med/Low,
color-coded), **In-House?** (Yes = producible with B. Symbolic's own printers /
AI / tools), **Notes**. Ratings keep the Palm Beach home-services lens.

## What was added

**Deepened existing categories** — Local & Direct (28→48: EDDM, direct mail,
canvassing, geofencing…), Digital-Other (25→37: retargeting, lead networks,
Waze…), Partnership & Channel (25→39: trade cross-referrals, co-op/MDF…),
Emerging/Niche (32→46: programmatic DOOH, AI creative, IoT…).

**12 brand-new categories** covering the rest of marketing:

| Category | # | Category | # |
|----------|---|----------|---|
| Email, SMS & Lifecycle | 33 | Web, CRO & UX | 20 |
| Content Marketing & SEO | 31 | Sales Enablement & Lead Mgmt | 20 |
| Video, CTV & Streaming | 24 | Analytics, Data & MarTech | 23 |
| Audio & Podcast | 20 | Branding, Creative & Design | 20 |
| Influencer & Creator | 18 | B2B & Account-Based | 20 |
| Loyalty, Retention & Community | 20 | Cause, Community & CSR | 15 |

## Rebuild

```bash
cd marketing-repository
python build_master.py     # reads data/…_ORIGINAL.xlsx, writes …_Expanded.xlsx
```

- `expansion_data.py` — all new tactics (edit here to add/adjust)
- `build_master.py` — merges original + expansion, applies matching styling
- `data/…_ORIGINAL.xlsx` — the source workbook (unchanged)

Requires `openpyxl` (`pip install openpyxl`).
