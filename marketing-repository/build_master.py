#!/usr/bin/env python3
"""Build the expanded B. Symbolic marketing MASTER repository.

Reads the original workbook, preserves every existing tactic + the Legend and
PBC Priority Playbook, then appends expansion tactics to existing categories and
adds new categories (Email/SMS, Content & SEO, Video/CTV, Audio, Influencer,
Loyalty, Web/CRO, Sales Enablement, Analytics/MarTech, Branding, B2B/ABM, CSR).

Output: a workbook with Legend · Master List (everything) · one tab per category
· PBC Priority Playbook — styled to match the original.

    python build_master.py
"""
from __future__ import annotations

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

import expansion_data as X
try:
    import metro_reference as M
    HAVE_METRO = True
except Exception as _e:  # billboard dataset not importable -> skip metro tabs
    HAVE_METRO = False
    _METRO_ERR = _e

SRC = "data/BSymbolic_Marketing_Repository_ORIGINAL.xlsx"
OUT = "data/BSymbolic_Marketing_Master_Expanded.xlsx"

# ---- palette (matched to the original) ----------------------------------- #
TITLE_FILL = PatternFill("solid", fgColor="FF8F3437")   # maroon band
TITLE_FONT = Font(bold=True, size=14, color="FFFAF6F4")
HEAD_FILL = PatternFill("solid", fgColor="FF1F2A44")    # navy header
HEAD_FONT = Font(bold=True, color="FFFFFFFF")
REL_FILL = {
    "High": PatternFill("solid", fgColor="FFD4EDDA"),
    "Med": PatternFill("solid", fgColor="FFFFF3CD"),
    "Low": PatternFill("solid", fgColor="FFF2F2F2"),
}
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)
_THIN = Side(style="thin", color="E0E0E0")
BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

# ---- category order + display metadata ----------------------------------- #
# (master_name, source_tab_title, TITLE BAND, output_tab_title)
EXISTING = [
    ("Outdoor / OOH", "Outdoor - OOH", "OUTDOOR / OOH", "Outdoor - OOH"),
    ("Local & Direct", "Local and Direct", "LOCAL & DIRECT", "Local and Direct"),
    ("Print", "Print", "PRINT", "Print"),
    ("Broadcast", "Broadcast", "BROADCAST", "Broadcast"),
    ("Digital - Social Media", "Digital - Social Media", "DIGITAL - SOCIAL MEDIA", "Digital - Social Media"),
    ("Digital - Content & Owned", "Digital - Content and Owned", "DIGITAL - CONTENT & OWNED", "Digital - Content and Owned"),
    ("Digital - Search & Display", "Digital - Search and Display", "DIGITAL - SEARCH & DISPLAY", "Digital - Search and Display"),
    ("Digital - Other", "Digital - Other", "DIGITAL - OTHER", "Digital - Other"),
    ("Experiential & Event", "Experiential and Event", "EXPERIENTIAL & EVENT", "Experiential and Event"),
    ("Promotional & Tangible", "Promotional and Tangible", "PROMOTIONAL & TANGIBLE", "Promotional and Tangible"),
    ("PR & Earned", "PR and Earned", "PR & EARNED", "PR and Earned"),
    ("Partnership & Channel", "Partnership and Channel", "PARTNERSHIP & CHANNEL", "Partnership and Channel"),
    ("Emerging / Niche", "Emerging - Niche", "EMERGING / NICHE", "Emerging - Niche"),
]

CAT_HDR = ["#", "Channel / Tactic", "Cost", "Trades Relevance", "In-House?", "Notes"]
CAT_W = [5, 40, 7, 15, 10, 58]
MASTER_HDR = ["#", "Category", "Channel / Tactic", "Cost", "Trades Relevance",
              "In-House?", "Time-to-Impact", "Notes"]
MASTER_W = [5, 24, 40, 7, 15, 10, 13, 55]

TIME_FILL = {
    "Fast": REL_FILL["High"],
    "Medium": REL_FILL["Med"],
    "Slow": REL_FILL["Low"],
    "Enabler": PatternFill("solid", fgColor="FFD6E4F0"),  # light blue
}


def derive_time(category, tactic):
    """Heuristic Time-to-Impact: Fast (days-weeks) / Medium (1-3 months) /
    Slow (3+ months, compounds) / Enabler (infrastructure that powers the rest)."""
    t = tactic.lower()
    if any(k in t for k in ("crm", "analytic", "tracking", "tag manager", "dashboard",
                            "attribution", "pixel", "utm", "brand identity", "logo",
                            "style guide", "asset library", "consent", "platform",
                            "audit", "reporting", "warmup", "segmentation")):
        return "Enabler"
    if any(k in t for k in ("seo", "blog", "pillar", "content", "organic", "backlink",
                            "guest post", "youtube channel", "podcast (own", "launch your own",
                            "authority", "e-e-a-t", "glossary", "loyalty", "membership",
                            "community", "scholarship", "aeo", "generative engine")):
        return "Slow"
    if any(k in t for k in (" ads", "ads ", "ad)", "lsa", "local service", "retarget",
                            "remarketing", "geofenc", "sms", "text-back", "speed-to-lead",
                            "eddm", "door hanger", "yard sign", "flyer", "lead-form",
                            "marketplace", "angi", "thumbtack", "yelp", "mobile billboard",
                            "mobile led", "truck", "review request", "review-request",
                            "missed-call", "chat", "popup", "click-to-call", "blast")):
        return "Fast"
    cat = category.lower()
    if any(k in cat for k in ("search", "social", "email", "sms")):
        return "Fast"
    if any(k in cat for k in ("content", "loyalty", "cause", "b2b")):
        return "Slow"
    if any(k in cat for k in ("analytics", "branding", "sales enablement")):
        return "Enabler"
    return "Medium"


# Fallback notes for rows the original workbook left blank — honest one-liners
# aligned with the Legend's relevance definitions.
_NOTE_FALLBACK = {
    "High": "Worth testing for local trades - start small and track cost-per-lead.",
    "Med": "Situational - fits specific campaigns/audiences; test before committing.",
    "Low": "Scale/brand play - generally skip on a local trades budget.",
}


def derive_note(tactic, relevance):
    t = tactic.lower()
    rules = [
        (("billboard", "bulletin", "poster (", "wallscape", "spectacular"),
         "Sold in 4-week flights; price tracks traffic count + location - see metro rate bands."),
        (("transit", "bus ", "rail", "shelter", "subway"),
         "Bought via the transit contractor (often OUTFRONT/JCDecaux) for the metro."),
        (("radio", "audio ad"), "Buy through the ownership group's local cluster; dayparts matter."),
        (("tv ", " tv", "television", "cable"),
         "Zoned cable (Spectrum Reach/Effectv) makes this affordable locally."),
        (("magnet", "keychain", "pen", "sticker", "koozie", "opener", "calendar"),
         "Cheap keep-forever item; brand + phone + QR only."),
        (("banner", "sign", "decal", "wrap"), "Producible in-house with cutter/printer; place legally."),
        (("facebook", "instagram", "meta"), "Geo-target service-area ZIPs; pair with lead forms + fast follow-up."),
        (("tiktok", "reels", "shorts", "vertical"), "Short-form organic reach engine; repurpose one video everywhere."),
        (("linkedin",), "B2B only - property managers, GCs, facility managers."),
        (("email", "newsletter", "drip", "nurture"), "Owned audience; automation makes it near-zero marginal cost."),
        (("landing page", "microsite", "squeeze"), "One page per offer; measure conversion, not traffic."),
        (("influencer", "creator", "ambassador"), "Local nano/micro beats celebrity for trades; pay on performance where possible."),
        (("sponsor", "booth", "fair", "show", "expo", "event"),
         "Negotiate signage + lead capture, not just a logo; work the booth with demos."),
        (("press", "pitch", "media", "journalist", "haro"),
         "Local reporters need expert sources - offer data and availability, not ads."),
        (("referral", "partner", "cross-", "co-market", "alliance"),
         "Cheapest high-trust leads; formalize the incentive and track it."),
        (("ai ", "chatbot", "voice agent", "automation", "predictive"),
         "Build in-house - your moat; competitors rent this from agencies."),
    ]
    for keys, note in rules:
        if any(k in t for k in keys):
            return note
    return _NOTE_FALLBACK.get(relevance, "")


def extract_existing(src):
    """Return {master_name: [(tactic,cost,rel,inhouse,notes), ...]} from the original."""
    out = {}
    for master, src_tab, _band, _out in EXISTING:
        ws = src[src_tab]
        rows = []
        for r in range(3, ws.max_row + 1):
            tactic = ws.cell(r, 2).value
            if not tactic:
                continue
            rows.append((
                tactic,
                ws.cell(r, 3).value or "",
                ws.cell(r, 4).value or "",
                ws.cell(r, 5).value or "",
                ws.cell(r, 6).value or "",
            ))
        out[master] = rows
    return out


def style_title(ws, text, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(1, 1, text)
    c.font = TITLE_FONT
    c.fill = TITLE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center")
    for i in range(1, ncols + 1):
        ws.cell(1, i).fill = TITLE_FILL
    ws.row_dimensions[1].height = 24


def style_header(ws, headers):
    for i, h in enumerate(headers, 1):
        c = ws.cell(2, i, h)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
        c.alignment = CENTER
        c.border = BORDER


def write_category_sheet(wb, band, out_tab, rows):
    ws = wb.create_sheet(out_tab)
    style_title(ws, band, len(CAT_HDR))
    style_header(ws, CAT_HDR)
    for n, (tactic, cost, rel, inhouse, notes) in enumerate(rows, 1):
        r = n + 2
        ws.cell(r, 1, n).alignment = CENTER
        ws.cell(r, 2, tactic).alignment = LEFT
        ws.cell(r, 3, cost).alignment = CENTER
        rc = ws.cell(r, 4, rel); rc.alignment = CENTER
        if rel in REL_FILL:
            rc.fill = REL_FILL[rel]
        ws.cell(r, 5, inhouse).alignment = CENTER
        ws.cell(r, 6, notes).alignment = LEFT
        for i in range(1, 7):
            ws.cell(r, i).border = BORDER
    for i, w in enumerate(CAT_W, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:F{len(rows) + 2}"
    return ws


def write_master_sheet(wb, all_rows, sheet_name="Master List",
                       title="B. SYMBOLIC - MASTER MARKETING CHANNEL REPOSITORY"):
    ws = wb.create_sheet(sheet_name)
    style_title(ws, title, len(MASTER_HDR))
    style_header(ws, MASTER_HDR)
    for n, (cat, tactic, cost, rel, inhouse, notes) in enumerate(all_rows, 1):
        r = n + 2
        ws.cell(r, 1, n).alignment = CENTER
        ws.cell(r, 2, cat).alignment = LEFT
        ws.cell(r, 3, tactic).alignment = LEFT
        ws.cell(r, 4, cost).alignment = CENTER
        rc = ws.cell(r, 5, rel); rc.alignment = CENTER
        if rel in REL_FILL:
            rc.fill = REL_FILL[rel]
        ws.cell(r, 6, inhouse).alignment = CENTER
        tti = derive_time(cat, tactic)
        tc = ws.cell(r, 7, tti); tc.alignment = CENTER
        if tti in TIME_FILL:
            tc.fill = TIME_FILL[tti]
        ws.cell(r, 8, notes).alignment = LEFT
        for i in range(1, 9):
            ws.cell(r, i).border = BORDER
    for i, w in enumerate(MASTER_W, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:H{len(all_rows) + 2}"
    return ws


def copy_plain_sheet(wb, src_ws, title):
    """Copy Legend / PBC Playbook values with light re-styling (title band + widths)."""
    ws = wb.create_sheet(title)
    maxc = max(2, src_ws.max_column)
    for r in range(1, src_ws.max_row + 1):
        for c in range(1, maxc + 1):
            v = src_ws.cell(r, c).value
            if v is not None:
                ws.cell(r, c, v)
    # style row 1 as a title band across used columns
    ncols = maxc
    top = ws.cell(1, 1)
    if top.value:
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
        top.font = TITLE_FONT
        for i in range(1, ncols + 1):
            ws.cell(1, i).fill = TITLE_FILL
        top.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[1].height = 24
    # a sensible width per column
    widths = [26, 60, 26, 40][:ncols] + [24] * max(0, ncols - 4)
    for i in range(1, ncols + 1):
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
        for r in range(2, ws.max_row + 1):
            ws.cell(r, i).alignment = LEFT
    return ws


def write_metro_reference(wb):
    rows = M.metro_reference_rows()
    ws = wb.create_sheet("US Metro Reference")
    headers = ["Rank", "Metro", "State", "DMA Rank (approx)", "Metro Pop",
               "OOH Rate ($/mo)", "OOH Ops (#)", "Major Newspaper",
               "Business Journal", "Big-4 TV Affiliates", "Major Radio Groups",
               "Spanish-Language Media", "Notable Ad Agencies", "Market Notes"]
    style_title(ws, "US METRO MARKETING REFERENCE - 42 MARKETS + PBC", len(headers))
    style_header(ws, headers)
    for n, d in enumerate(rows, 1):
        r = n + 2
        vals = [d["rank"], d["metro"], d["state"], d["dma"], d["pop"], d["rate"],
                d["ops"], d["paper"], d["bizj"], d["tv"], d["radio"],
                d.get("spanish", "-"), d["agencies"], d["note"]]
        for i, v in enumerate(vals, 1):
            cell = ws.cell(r, i, v)
            cell.alignment = CENTER if i in (1, 3, 4, 5, 6, 7) else LEFT
            cell.border = BORDER
            if str(d["metro"]).startswith("Palm Beach"):
                cell.fill = REL_FILL["High"]
    for i, w in enumerate([6, 15, 7, 10, 16, 15, 9, 28, 26, 34, 36, 40, 34, 48], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:N{len(rows) + 2}"
    return ws


def write_quick_start(wb):
    rows = M.quick_start_rows()
    ws = wb.create_sheet("Quick-Start by Metro")
    headers = ["Rank", "Metro", "Metro Pop", "OOH Rate Band",
               "Top Local OOH Operators", "Big-4 TV", "Radio Groups",
               "Newspaper", "Agencies to Call"]
    style_title(ws, "US QUICK-START BY METRO - WHO TO CALL IN EACH MARKET", len(headers))
    style_header(ws, headers)
    # Universal-foundation note band under the header.
    note_row = 3 + len(rows) + 1
    for n, d in enumerate(rows, 1):
        r = n + 2
        vals = [d["rank"], d["metro"], d["pop"], d["ooh"], d["ops"], d["tv"],
                d["radio"], d["paper"], d["agencies"]]
        for i, v in enumerate(vals, 1):
            cell = ws.cell(r, i, v)
            cell.alignment = CENTER if i in (1, 3, 4) else LEFT
            cell.border = BORDER
            if str(d["metro"]).startswith("Palm Beach"):
                cell.fill = REL_FILL["High"]
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=len(headers))
    c = ws.cell(note_row, 1, "UNIVERSAL FOUNDATION (every metro, before any media buy): "
                             + M.QUICK_START_FOUNDATION)
    c.font = Font(bold=True, italic=True)
    c.alignment = LEFT
    ws.row_dimensions[note_row].height = 30
    for i, w in enumerate([6, 15, 14, 16, 38, 34, 36, 28, 34], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:I{len(rows) + 2}"
    return ws


def write_metro_companies(wb):
    rows = M.metro_company_rows()
    ws = wb.create_sheet("Metro OOH Companies")
    headers = ["#", "Company", "Type", "Metros Served", "HQ", "Website",
               "Pricing (availability)", "Confidence"]
    style_title(ws, "METRO OOH / BILLBOARD COMPANIES - 42 MARKETS", len(headers))
    style_header(ws, headers)
    for n, d in enumerate(rows, 1):
        r = n + 2
        vals = [n, d["company"], d["type"], d["metros"], d["hq"], d["website"],
                d["pricing"], d["confidence"]]
        for i, v in enumerate(vals, 1):
            cell = ws.cell(r, i, v)
            cell.alignment = CENTER if i in (1, 8) else LEFT
            cell.border = BORDER
    for i, w in enumerate([5, 34, 26, 40, 22, 40, 34, 11], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:H{len(rows) + 2}"
    return ws


BUDGETS = [
    # (channel, $2.5k, $5k, $10k, rationale)
    ("Google Local Services Ads", 800, 1500, 2000, "Best trades lead quality; pay-per-lead, Google Guaranteed."),
    ("Google Search ads", 400, 800, 1500, "Emergency + high-intent terms; call-only campaigns."),
    ("GBP / reviews / automation tools", 150, 250, 400, "CallRail, review software, missed-call text-back."),
    ("Meta / Nextdoor local ads", 300, 600, 1000, "Geo-targeted awareness + lead forms in service-area ZIPs."),
    ("Retargeting", 100, 200, 400, "Cheapest re-touch of site visitors and quote abandoners."),
    ("EDDM / direct mail", 300, 600, 1000, "Carrier-route saturation around completed jobs."),
    ("Yard signs / wraps / promo (materials)", 150, 250, 500, "In-house production; magnets + shutoff tags."),
    ("Email/SMS platform", 100, 150, 300, "Reminders, reactivation, review requests - runs itself."),
    ("Community sponsorships", 100, 250, 500, "Youth sports, chamber, local events."),
    ("SEO / content (contractor or time)", 0, 300, 800, "DIY at $2.5k; buy help as budget grows - compounds."),
    ("Local OOH / radio flight test", 0, 0, 1500, "Only at $10k+: one measured 4-week flight, one corridor."),
    ("Testing reserve", 100, 100, 100, "Always keep something for the next experiment."),
]

CALENDAR = [
    ("January", "Snowbird season peak; New Year home projects",
     "Maintenance plans, water-quality upgrades", "Email/SMS, GBP posts, EDDM to seasonal communities"),
    ("February", "Tax-refund window opens; South Florida Fair",
     "Bigger-ticket jobs with financing offers", "Search ads on financing terms, fair booth/sponsorship"),
    ("March", "Spring training; season population peak",
     "Spring maintenance specials", "Sponsorships, Nextdoor, direct mail"),
    ("April", "Snowbirds depart late April",
     "Pre-departure shutoff/home-watch services", "Email to seasonal list, partner property managers"),
    ("May", "Hurricane-prep education window; SunFest",
     "Hurricane plumbing-prep checklists", "PR pitches, content/SEO, event presence"),
    ("June", "Hurricane season opens June 1",
     "Prep packages, generator/backflow checks", "Search ads, emergency-magnet distribution, radio"),
    ("July", "Peak heat + daily storms",
     "Emergency response positioning", "LSA + call-only ads, after-hours AI chatbot capture"),
    ("August", "Peak hurricane threat builds; back-to-school",
     "Readiness campaigns; review pushes on slow days", "SMS blasts, review automation, retargeting"),
    ("September", "Statistical hurricane peak",
     "Storm response + restoration partnerships", "Standby PR, partner restoration/insurance channels"),
    ("October", "Season winds down; snowbirds return",
     "Returning-resident inspections", "EDDM wave, new-mover mail, GBP offers"),
    ("November", "Hurricane season ends Nov 30; holidays approach",
     "Guest-ready plumbing offers, Black Friday promo", "Email/SMS promo, social offers"),
    ("December", "Holiday hosting; year-end",
     "Gift-card/loyalty gifts; plan next year", "Customer-appreciation touches, year-in-review email"),
]


def write_budgets(wb):
    ws = wb.create_sheet("Sample Budgets")
    headers = ["Channel", "$2,500/mo", "$5,000/mo", "$10,000/mo", "Why"]
    style_title(ws, "SAMPLE MONTHLY BUDGET SPLITS - PBC TRADES BUSINESS", len(headers))
    style_header(ws, headers)
    r = 3
    for (ch, a, b, c, why) in BUDGETS:
        for i, v in enumerate([ch, a, b, c, why], 1):
            cell = ws.cell(r, i, v)
            cell.alignment = LEFT if i in (1, 5) else CENTER
            cell.border = BORDER
            if i in (2, 3, 4):
                cell.number_format = "$#,##0"
        r += 1
    # totals
    ws.cell(r, 1, "TOTAL").font = Font(bold=True)
    for i, col in enumerate((2, 3, 4), 1):
        total = sum(row[i] for row in BUDGETS)
        cell = ws.cell(r, col, total)
        cell.font = Font(bold=True)
        cell.number_format = "$#,##0"
        cell.alignment = CENTER
        cell.fill = REL_FILL["High"]
    for i, w in enumerate([38, 12, 12, 12, 62], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    return ws


def write_calendar(wb):
    ws = wb.create_sheet("Seasonal Calendar")
    headers = ["Month", "PBC Context", "What to Push", "Lead Channels"]
    style_title(ws, "PALM BEACH COUNTY SEASONAL MARKETING CALENDAR", len(headers))
    style_header(ws, headers)
    hurricane = {"June", "July", "August", "September", "October", "November"}
    for n, (m, ctx, push, ch) in enumerate(CALENDAR, 1):
        r = n + 2
        for i, v in enumerate([m, ctx, push, ch], 1):
            cell = ws.cell(r, i, v)
            cell.alignment = LEFT
            cell.border = BORDER
        if m in hurricane:
            ws.cell(r, 1).fill = REL_FILL["Med"]  # hurricane season shading
    for i, w in enumerate([12, 44, 44, 52], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    return ws


_INDEX_DESC = {
    "Legend": "How to use this workbook (cost / relevance / in-house keys)",
    "Master List": "All tactics, every category - filter by Cost, Relevance, In-House",
    "Quick Wins": "Auto-filtered: High relevance x $ cost x producible in-house",
    "US Metro Reference": "42 metros + PBC: DMA, population, OOH rates, media, agencies",
    "Metro OOH Companies": "110 scraped billboard/OOH operators by metro",
    "Quick-Start by Metro": "Who to call in each market + universal foundation",
    "Metro Category Contacts": "All 13 categories x every metro - filter to any city",
    "Sample Budgets": "$2.5k / $5k / $10k monthly allocation models for a trades business",
    "Seasonal Calendar": "PBC month-by-month: what to push and where (hurricane season shaded)",
    "PBC Priority Playbook": "What to actually do first in Palm Beach County",
}


def write_index(wb):
    ws = wb.create_sheet("Index")
    style_title(ws, "B. SYMBOLIC - US MARKETING MASTER REFERENCE - INDEX", 2)
    ws.cell(2, 1, "Sheet").font = HEAD_FONT
    ws.cell(2, 2, "What's on it").font = HEAD_FONT
    for i in (1, 2):
        ws.cell(2, i).fill = HEAD_FILL
        ws.cell(2, i).border = BORDER
    r = 3
    for name in wb.sheetnames:
        if name == "Index":
            continue
        cell = ws.cell(r, 1, name)
        cell.hyperlink = f"#'{name}'!A1"
        cell.font = Font(color="FF1F4E79", underline="single")
        cell.border = BORDER
        desc = _INDEX_DESC.get(name, "Category tactics - filter by Cost / Relevance / In-House")
        d = ws.cell(r, 2, desc)
        d.alignment = LEFT
        d.border = BORDER
        r += 1
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 70
    ws.freeze_panes = "A3"
    # Move Index to the front.
    wb.move_sheet("Index", offset=-(len(wb.sheetnames) - 1))
    return ws


def write_category_contacts(wb):
    rows = M.category_contacts_rows()
    ws = wb.create_sheet("Metro Category Contacts")
    headers = ["Rank", "Metro", "Category", "Scope", "Points of Contact / Where to Buy"]
    style_title(ws, "METRO x CATEGORY CONTACTS - ALL 13 CATEGORIES IN EVERY MARKET", len(headers))
    style_header(ws, headers)
    scope_fill = {"Metro": REL_FILL["High"], "Mixed": REL_FILL["Med"],
                  "Universal": REL_FILL["Low"]}
    for n, d in enumerate(rows, 1):
        r = n + 2
        vals = [d["rank"], d["metro"], d["category"], d["scope"], d["contacts"]]
        for i, v in enumerate(vals, 1):
            cell = ws.cell(r, i, v)
            cell.alignment = CENTER if i in (1, 4) else LEFT
            cell.border = BORDER
        if d["scope"] in scope_fill:
            ws.cell(r, 4).fill = scope_fill[d["scope"]]
        if str(d["metro"]).startswith("Palm Beach"):
            for i in (1, 2, 3):
                ws.cell(r, i).fill = REL_FILL["High"]
    for i, w in enumerate([6, 15, 24, 10, 110], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:E{len(rows) + 2}"
    return ws


def main():
    src = openpyxl.load_workbook(SRC, data_only=True)
    existing = extract_existing(src)

    # Assemble final per-category data (existing + expansions), preserving order.
    categories = []  # (master, band, out_tab, rows)
    for master, _src_tab, band, out_tab in EXISTING:
        rows = list(existing[master])
        rows += X.EXPANSIONS.get(master, [])
        categories.append((master, band, out_tab, rows))
    for master in X.NEW_CATEGORY_ORDER:
        out_tab, band = X.NEW_CATEGORY_META[master]
        categories.append((master, band, out_tab, X.NEW_CATEGORIES[master]))

    # Mark cross-category duplicates: a tactic already listed in an earlier
    # category gets a "Cross-listed under X." note instead of silently repeating.
    import re as _re
    _norm = lambda s: _re.sub(r"[^a-z0-9]", "", s.lower())
    seen_cat = {}
    marked = []
    for master, band, out_tab, rows in categories:
        new_rows = []
        for (tactic, cost, rel, ih, notes) in rows:
            k = _norm(tactic)
            if k in seen_cat and seen_cat[k] != master:
                tag = f"Cross-listed under {seen_cat[k]}."
                notes = f"{notes} {tag}".strip() if notes else tag
            else:
                seen_cat.setdefault(k, master)
            if not notes:  # fill blanks with an honest derived one-liner
                notes = derive_note(tactic, rel)
            new_rows.append((tactic, cost, rel, ih, notes))
        marked.append((master, band, out_tab, new_rows))
    categories = marked

    # Build output workbook.
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # 1) Legend (copied + refreshed count note)
    legend = copy_plain_sheet(wb, src["Legend"], "Legend")
    total = sum(len(rows) for *_h, rows in categories)
    legend.cell(3, 2,
                f"Master List = all {total} channels/tactics across {len(categories)} categories. "
                "One tab per category. PBC Priority Playbook = curated high-impact shortlist.")
    # add an 'Expanded' note row
    nr = legend.max_row + 2
    legend.cell(nr, 1, "Expanded").font = Font(bold=True)
    legend.cell(nr, 2,
                "This master extends the original OOH/local menu into ALL marketing: "
                "Email/SMS, Content & SEO, Video/CTV, Audio, Influencer, Loyalty, Web/CRO, "
                "Sales Enablement, Analytics/MarTech, Branding, B2B/ABM and Cause/CSR. "
                "Trades Relevance ratings keep the Palm Beach home-services lens.")
    legend.cell(nr, 2).alignment = LEFT
    if HAVE_METRO:
        nr2 = legend.max_row + 1
        legend.cell(nr2, 1, "US Metros").font = Font(bold=True)
        legend.cell(nr2, 2,
                    "US Metro Reference = 42 largest markets with DMA rank, population, "
                    "OOH rate band, # billboard operators, newspaper, business journal, "
                    "Big-4 TV affiliates, major radio groups & notable ad agencies. "
                    "Metro OOH Companies = 110 scraped billboard/OOH operators by metro. "
                    "Quick-Start by Metro = who to call in each market (top local OOH "
                    "operators, TV/radio/paper, agencies) + the universal foundation steps. "
                    "Metro Category Contacts = all 13 original categories x every metro "
                    "(546 rows): filter column B to any city to see its full contact card. "
                    "Scope column: Metro (green) = market-specific vendor; Universal (grey) "
                    "= same self-serve platform everywhere, just geo-target it. "
                    "TV/radio/agency/event data is reference-level - verify before buying.")
        legend.cell(nr2, 2).alignment = LEFT
        nr3 = legend.max_row + 1
        legend.cell(nr3, 1, "Derived fields").font = Font(bold=True)
        legend.cell(nr3, 2,
                    "Time-to-Impact (Master List / Quick Wins): Fast = days-weeks, "
                    "Medium = 1-3 months, Slow = 3+ months (compounds), Enabler = "
                    "infrastructure that powers other channels - derived by rule, not "
                    "hand-rated. Notes that were blank in the original are auto-derived "
                    "one-liners; hand-written notes were left untouched.")
        legend.cell(nr3, 2).alignment = LEFT

    # 2) Master List (aggregate of every category)
    master_rows = []
    for master, _band, _tab, rows in categories:
        for (tactic, cost, rel, inhouse, notes) in rows:
            master_rows.append((master, tactic, cost, rel, inhouse, notes))
    write_master_sheet(wb, master_rows)

    # 2b) Quick Wins — High relevance, low cost, producible in-house
    quick_wins = [r for r in master_rows
                  if r[3] == "High" and r[2] == "$" and r[4] == "Yes"]
    write_master_sheet(wb, quick_wins, sheet_name="Quick Wins",
                       title="QUICK WINS - HIGH RELEVANCE x LOW COST x IN-HOUSE")

    # 3) One tab per category
    for master, band, out_tab, rows in categories:
        write_category_sheet(wb, band, out_tab, rows)

    # 4) US Metro marketing reference (ties the tactics to real markets)
    if HAVE_METRO:
        write_metro_reference(wb)
        write_metro_companies(wb)
        write_quick_start(wb)
        write_category_contacts(wb)

    # 5) PBC Priority Playbook (preserved + lifecycle/measurement tiers appended)
    if "PBC Priority Playbook" in src.sheetnames:
        pb = copy_plain_sheet(wb, src["PBC Priority Playbook"], "PBC Priority Playbook")
        extra = [
            ("7 - Lifecycle & Automation (NEW)",
             "Missed-call text-back + speed-to-lead (<5 min)", "Sales Enablement",
             "Contact within 5 minutes multiplies close rate; auto-text every missed call. Your n8n stack."),
            ("7 - Lifecycle & Automation (NEW)",
             "Review-request automation after every job", "Email/SMS",
             "Compounds the GBP foundation - reviews are the #1 map-pack lever."),
            ("7 - Lifecycle & Automation (NEW)",
             "Maintenance reminders + dead-lead reactivation (email/SMS)", "Email/SMS",
             "Annual flush/filter reminders = recurring revenue; old quotes are a goldmine."),
            ("8 - Measure (NEW)",
             "GA4 + CallRail + Looker Studio ROI dashboard", "Analytics",
             "One-glance cost-per-lead by channel; kill what doesn't pay."),
        ]
        r = pb.max_row + 1
        for row in extra:
            for i, v in enumerate(row, 1):
                cell = pb.cell(r, i, v)
                cell.alignment = LEFT
                cell.fill = REL_FILL["High"]
            r += 1

    # 6) Budget models + seasonal calendar
    write_budgets(wb)
    write_calendar(wb)

    # 7) Index / table of contents, placed first
    write_index(wb)

    wb.save(OUT)

    # Report
    print(f"Wrote {OUT}")
    print(f"  {len(categories)} categories · {len(master_rows)} total tactics "
          f"(was 792; +{len(master_rows) - 792} new)")
    for master, _band, _tab, rows in categories:
        print(f"    {len(rows):4}  {master}")


if __name__ == "__main__":
    main()
