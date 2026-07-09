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
MASTER_HDR = ["#", "Category", "Channel / Tactic", "Cost", "Trades Relevance", "In-House?", "Notes"]
MASTER_W = [5, 24, 40, 7, 15, 10, 55]


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


def write_master_sheet(wb, all_rows):
    ws = wb.create_sheet("Master List")
    style_title(ws, "B. SYMBOLIC - MASTER MARKETING CHANNEL REPOSITORY", len(MASTER_HDR))
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
        ws.cell(r, 7, notes).alignment = LEFT
        for i in range(1, 8):
            ws.cell(r, i).border = BORDER
    for i, w in enumerate(MASTER_W, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:G{len(all_rows) + 2}"
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
               "Business Journal", "Market Notes"]
    style_title(ws, "US METRO MARKETING REFERENCE - 42 MARKETS", len(headers))
    style_header(ws, headers)
    for n, d in enumerate(rows, 1):
        r = n + 2
        vals = [d["rank"], d["metro"], d["state"], d["dma"], d["pop"], d["rate"],
                d["ops"], d["paper"], d["bizj"], d["note"]]
        for i, v in enumerate(vals, 1):
            cell = ws.cell(r, i, v)
            cell.alignment = CENTER if i in (1, 3, 4, 5, 6, 7) else LEFT
            cell.border = BORDER
    for i, w in enumerate([6, 15, 7, 10, 16, 15, 9, 30, 30, 55], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:J{len(rows) + 2}"
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
                    "OOH rate band, # billboard operators, dominant newspaper & business "
                    "journal. Metro OOH Companies = 110 scraped billboard/OOH operators by "
                    "metro. Turns the tactic menu into a US market reference.")
        legend.cell(nr2, 2).alignment = LEFT

    # 2) Master List (aggregate of every category)
    master_rows = []
    for master, _band, _tab, rows in categories:
        for (tactic, cost, rel, inhouse, notes) in rows:
            master_rows.append((master, tactic, cost, rel, inhouse, notes))
    write_master_sheet(wb, master_rows)

    # 3) One tab per category
    for master, band, out_tab, rows in categories:
        write_category_sheet(wb, band, out_tab, rows)

    # 4) US Metro marketing reference (ties the tactics to real markets)
    if HAVE_METRO:
        write_metro_reference(wb)
        write_metro_companies(wb)

    # 5) PBC Priority Playbook (preserved)
    if "PBC Priority Playbook" in src.sheetnames:
        copy_plain_sheet(wb, src["PBC Priority Playbook"], "PBC Priority Playbook")

    wb.save(OUT)

    # Report
    print(f"Wrote {OUT}")
    print(f"  {len(categories)} categories · {len(master_rows)} total tactics "
          f"(was 792; +{len(master_rows) - 792} new)")
    for master, _band, _tab, rows in categories:
        print(f"    {len(rows):4}  {master}")


if __name__ == "__main__":
    main()
