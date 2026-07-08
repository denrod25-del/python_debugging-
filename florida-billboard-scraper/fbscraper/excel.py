"""Write the collected companies to a formatted, multi-sheet Excel workbook."""
from __future__ import annotations

import csv
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from .models import Company, COLUMNS, HEADERS
from .pricing import REFERENCE_RATES, PRICING_DISCLAIMER

# Palette
_HEADER_FILL = PatternFill("solid", fgColor="1F3864")   # deep navy
_HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
_PB_FILL = PatternFill("solid", fgColor="FCE4D6")        # highlight Palm Beach rows
_TITLE_FONT = Font(bold=True, size=16, color="1F3864")
_SUB_FONT = Font(italic=True, size=10, color="595959")
_THIN = Side(style="thin", color="D0D0D0")
_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

# Reasonable widths per column key.
_WIDTHS = {
    "company_name": 34, "company_type": 26, "primary_market": 30,
    "counties_served": 26, "serves_palm_beach": 12, "address": 26,
    "city": 16, "state": 6, "zip_code": 8, "phone": 16, "email": 26,
    "website": 44, "pricing": 30, "pricing_reference": 42, "notes": 50,
    "source": 34, "confidence": 11,
}


def _style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _BORDER


def _companies_sheet(ws, companies: List[Company], title: str):
    ncols = len(COLUMNS)
    # Title band
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    ws.cell(row=1, column=1, value=title).font = _TITLE_FONT
    ws.cell(row=1, column=1).alignment = Alignment(vertical="center")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    ws.cell(row=2, column=1,
            value=f"{len(companies)} companies · Palm Beach County first · "
                  "prices are quote-only (see Pricing Reference tab)").font = _SUB_FONT

    header_row = 4
    for i, key in enumerate(COLUMNS, start=1):
        ws.cell(row=header_row, column=i, value=HEADERS[key])
    _style_header(ws, ncols, row=header_row)

    for r, comp in enumerate(companies, start=header_row + 1):
        row = comp.as_row()
        is_pb = (comp.serves_palm_beach or "").strip().lower() == "yes"
        for i, val in enumerate(row, start=1):
            cell = ws.cell(row=r, column=i, value=val)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = _BORDER
            if is_pb:
                cell.fill = _PB_FILL

    # Widths + freeze + autofilter
    for i, key in enumerate(COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = _WIDTHS.get(key, 18)
    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(ncols)}{header_row + len(companies)}"


def _pricing_sheet(ws):
    ws.cell(row=1, column=1, value="Florida Billboard Pricing — Reference Ranges").font = _TITLE_FONT
    ws.merge_cells("A1:E1")
    ws.cell(row=2, column=1, value=PRICING_DISCLAIMER).font = _SUB_FONT
    ws.merge_cells("A2:E2")
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[2].height = 42

    headers = ["Segment", "Low", "High", "Unit", "Note"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=4, column=i, value=h)
    _style_header(ws, len(headers), row=4)

    for r, (seg, lo, hi, unit, note) in enumerate(REFERENCE_RATES, start=5):
        for i, val in enumerate([seg, lo, hi, unit, note], start=1):
            cell = ws.cell(row=r, column=i, value=val)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = _BORDER

    for i, w in enumerate([38, 12, 12, 16, 60], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _about_sheet(ws, notes: List[str]):
    ws.cell(row=1, column=1, value="About this workbook").font = _TITLE_FONT
    ws.column_dimensions["A"].width = 110
    for r, line in enumerate(notes, start=3):
        cell = ws.cell(row=r, column=1, value=line)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.font = Font(size=11)


def sort_companies(companies: List[Company]) -> List[Company]:
    """Palm Beach first, then by confidence, then name."""
    conf_rank = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(
        companies,
        key=lambda c: (
            0 if (c.serves_palm_beach or "").lower() == "yes" else 1,
            conf_rank.get(c.confidence, 3),
            c.company_name.lower(),
        ),
    )


def write_csv(companies: List[Company], path: str) -> str:
    """Write companies to a UTF-8 CSV (same column order as the workbook)."""
    companies = sort_companies(companies)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow([HEADERS[c] for c in COLUMNS])
        for comp in companies:
            writer.writerow(comp.as_row())
    return path


def write_workbook(companies: List[Company], path: str, about: List[str] | None = None):
    """Write companies + pricing + about sheets to `path`."""
    companies = sort_companies(companies)

    wb = Workbook()
    ws = wb.active
    ws.title = "FL Billboard Companies"
    _companies_sheet(ws, companies, "Florida Billboard / Outdoor Advertising Companies")

    _pricing_sheet(wb.create_sheet("Pricing Reference"))

    if about:
        _about_sheet(wb.create_sheet("About"), about)

    wb.save(path)
    return path
