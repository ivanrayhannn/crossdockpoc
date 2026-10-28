#!/usr/bin/env python3
"""
build_uiss.py - render a TMAP-standard UISS workbook (UISS-Screen or UISS-Report)
from a JSON spec, using the clean templates in ../assets.

Usage:
    python build_uiss.py spec.json -o /mnt/user-data/outputs/UISS_Screen_WXXX0010.xlsx

The spec format is documented in ../references/spec-schema.md.
The script prints a JSON summary (sheets created + TBD count per sheet) to stdout.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from copy import copy

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string as CI
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.cell_range import MultiCellRange
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.merge import MergedCellRange
from openpyxl.worksheet.pagebreak import Break

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shapes  # noqa: E402  native editable flowchart shapes

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))
TEMPLATES = {"screen": "uiss_screen_template.xlsx", "report": "uiss_report_template.xlsx",
             "batch": "uiss_batch_template.xlsx"}

SHEETS = {
    "screen": ["Revision", "Gen Desc", "Screen Flow", "Screen Layout", "Item Desc",
               "Data Map", "Operation Desc", "Display Message", "Logging Message"],
    "report": ["Revision", "Gen Desc", "Layout", "Item Desc", "Operation Desc", "Logging Message"],
    "batch": ["Revision", "Gen Desc", "Func Flow", "Data Map", "Func Desc", "Logging Message", "Appendix"],
}
BLOCK_NAME = {"screen": "Screen", "report": "Report", "batch": "Batch"}
TITLE_ROWS = {"Func Flow": "1:7", "Data Map": "1:7", "Layout": "1:6"}
ALIASES = {"Appendix": "Func Desc"}   # extra sheet types that reuse another template page
TITLES = {
    "Revision": "", "Gen Desc": "General Description",
    "Screen Flow": "Screen Flow Diagram", "Screen Layout": "Screen Layout",
    "Item Desc": "Item Description", "Data Map": "Data Edit Mapping",
    "Operation Desc": "Operation Description", "Display Message": "Display Message",
    "Logging Message": "Logging Message", "Layout": "Report Layout",
    "Func Flow": "Functional Flow", "Func Desc": "Functional Description", "Appendix": "Appendix",
}

COL_FIRST, COL_LAST = 2, 102          # B .. CX : printable frame
BODY_TOP = 7                          # first row under the gray section-title bar
FLOW_TOP, FLOW_BOTTOM, PAGE_BOTTOM = 8, 47, 48
REGIONS_TWO = [(3, 51), (54, 101)]    # left C..AY | right BB..CW (divider on AZ)
REGION_FULL = [(3, 101)]
ROW_H = 11.1                          # pt, standard body row height
ROW_PX = ROW_H * 96 / 72

THIN, HAIR, DOUBLE = Side(style="thin"), Side(style="hair"), Side(style="double")
NOSIDE = Side(style=None)
F_BODY = Font(name="Arial", size=8)
F_BOLD = Font(name="Arial", size=8, bold=True)
F_ITAL = Font(name="Arial", size=8, italic=True)
FILL_NONE = PatternFill(fill_type=None)
FILL_ORANGE = PatternFill("solid", fgColor="FFFFCC99")   # table header (Gen Desc style)
FILL_YELLOW = PatternFill("solid", fgColor="FFFFFF00")   # operation group row (Display Message)

# Preformatted table sheets: rows already exist in the template, we fill them.
GRID = {
    "Revision": dict(first=8, last=49, cols=dict(
        revision="B", author="K", date="V", reviewed_by="AF", description="AQ"),
        center=["revision", "date"]),
    ("screen", "Item Desc"): dict(first=9, last=48, group_col="name", extend=True, cols=dict(
        no="B", name="D", source="S", field="AC", type="AJ", len="AP", io="AS",
        control="AV", justified="BC", initial="BH", required="BO", format="BS",
        validation="BZ", description="CK"),
        center=["no", "len", "io", "justified", "required"]),
    ("report", "Item Desc"): dict(first=9, last=48, group_col="name", extend=True, cols=dict(
        no="B", name="D", type="S", len="Y", justified="AB", format="AG",
        source="AO", field="AY", condition="BF", remarks="BW"),
        center=["no", "len", "justified"]),
    ("screen", "Display Message"): dict(first=9, last=49, group_col="event", extend=True, group_fill=True, cols=dict(
        no="B", event="E", cause="R", type="AJ", msg_id="AO", message="AW", action="CB"),
        center=["no", "type"], dv={"type": "Critical,Warning,Error,Info,Confirm"}),
    ("screen", "Logging Message"): dict(first=9, last=47, group_col="event", extend=True, cols=dict(
        no="B", event="E", cause="T", type="AL", msg_id="AQ", message="AX", exception="BW", action="CC"),
        center=["no", "type", "exception"],
        dv={"type": "Critical,Warning,Error,Info,Confirm,Debug", "exception": "Y,N"}),
    ("batch", "Logging Message"): dict(first=9, last=45, group_col="event", extend=True, cols=dict(
        no="B", event="E", cause="T", type="AL", msg_id="AQ", message="AX", action="BW"),
        center=["no", "type"], dv={"type": "Critical,Warning,Error,Info,Confirm,Debug"}),
    ("report", "Logging Message"): dict(first=9, last=45, group_col="event", extend=True, cols=dict(
        no="B", event="E", cause="T", type="AL", msg_id="AQ", message="AX", exception="BW", action="CC"),
        center=["no", "type", "exception"],
        dv={"type": "Critical,Warning,Error,Info,Confirm,Debug", "exception": "Y,N"}),
}

LAYOUT_COLS = dict(report_id="B", report_name="I", paper_size="T", form_type="Y", paper_layout="AE",
                   printer_type="AL", template_type="AS", template_by_user="AZ", type_application="BF",
                   type_business="BL", need_screen="BR", file_type="BW", preview="CB",
                   direct_print="CG", copies="CM", signature="CR")
LAYOUT_DV = dict(paper_size="A3,A4", form_type="Pre-print,Blank", paper_layout="Landscape,Portrait",
                 printer_type="Laser,Dot Matrix", template_type="Dynamic,Fixed",
                 type_application="Online,Scheduled,On-demand",
                 type_business="Transaction,Summary,Master Dump,Status Check",
                 file_type="Excel,PDF", signature="Hand Writing,Electronic",
                 template_by_user="Y,N", need_screen="Y,N", preview="Y,N", direct_print="Y,N")

# --------------------------------------------------------------------------- text metrics
_FONT_CACHE = {}
_FONT_FILES = {
    False: ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"],
    True: ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
           "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"],
}


def text_px(s, bold=False, size=8):
    key = (bold, size)
    if key not in _FONT_CACHE:
        font = None
        try:
            from PIL import ImageFont
            for path in _FONT_FILES[bold]:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, size * 96 / 72)
                    break
        except Exception:
            font = None
        _FONT_CACHE[key] = font
    font = _FONT_CACHE[key]
    if font is None:
        return len(s) * 5.4 * size / 8 * (1.08 if bold else 1)
    return font.getlength(s)


def usable_px(width_px):
    # Excel renders Arial 8pt ~3% wider than the 96-dpi metric and pads cells by a few px
    return max(width_px * 0.97 - 4, 10)


def wrap(text, width_px, bold=False):
    """Greedy word-wrap into lines that fit width_px. Over-long tokens (table names, IDs) are
    broken after '_', '.', '/', '-' where possible."""
    if text is None:
        return []
    text = str(text)
    if text == "":
        return []
    usable = usable_px(width_px)
    out = []
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            cand = w if not line else line + " " + w
            if text_px(cand, bold) <= usable:
                line = cand
                continue
            if line:
                out.append(line)
            while text_px(w, bold) > usable:
                cut = len(w)
                while cut > 1 and text_px(w[:cut], bold) > usable:
                    cut -= 1
                brk = max(w.rfind(ch, 0, cut) for ch in "_./-,")
                if brk >= max(1, int(cut * 0.4)):
                    cut = brk + 1
                out.append(w[:cut])
                w = w[cut:]
            line = w
        out.append(line)
    return out


def layout_text(value, width_px, bold=False):
    """Return (lines, shrink). A single token that is only slightly too wide (codes such as
    MSTD0075AERR) is kept on one line with shrink-to-fit instead of being broken."""
    if value is None or value == "":
        return [], False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [value], False
    v = str(value)
    if " " not in v and "\n" not in v:
        w = text_px(v, bold)
        if usable_px(width_px) < w <= (width_px - 2) * 1.25:
            return [v], True
    return wrap(v, width_px, bold), False


def tbd(v):
    return "TBD" if v is None else v


# --------------------------------------------------------------------------- book / pages
class Book:
    def __init__(self, kind, header):
        self.kind = kind
        self.header = header
        self.wb = load_workbook(os.path.join(ASSETS, TEMPLATES[kind]))
        self.src = {}
        for ws in list(self.wb.worksheets):
            name = ws.title
            ws.title = "__src_" + name
            self.src[name] = ws
        for alias, base in ALIASES.items():
            if base in self.src and alias not in self.src:
                self.src[alias] = self.src[base]
        ref = self.src["Gen Desc"]
        self._colw = {}
        for dim in ref.column_dimensions.values():
            if dim.min and dim.max:
                for c in range(dim.min, min(dim.max, 300) + 1):
                    self._colw[c] = dim.width or 1.41
        self.pages = []           # (base, ws)
        self.shapes = {}          # sheet title -> [drawing anchor xml] (editable flowcharts)
        self.frame_bottom = {}    # sheet title -> last row of the page frame when extended
        self.tmpdir = tempfile.mkdtemp(prefix="uiss_")
        self._hdr_cache = {}

    # ---- geometry
    def col_px(self, c):
        w = self._colw.get(c, 1.41)
        return int(((256 * w + int(128 / 7)) / 256) * 7)

    def span_px(self, c1, c2):
        return sum(self.col_px(c) for c in range(c1, c2 + 1))

    # ---- page creation
    def new_page(self, base, clear_from=None, clear_to=None):
        """Copy the template sheet `base`. If clear_from is given, rows clear_from..PAGE_BOTTOM are
        emptied (merges, values, styles) and redrawn as a blank frame."""
        src = self.src[base]
        ws = self.wb.copy_worksheet(src)
        n = sum(1 for b, _ in self.pages if b == base)
        ws.title = base if n == 0 else f"{base} ({n + 1})"
        # rebuild merges so they belong to the new sheet and keep edge styles
        ws.merged_cells = MultiCellRange()
        for m in src.merged_cells.ranges:
            self._merge_keep_style(ws, m.coord)
        for row in ws.iter_rows():
            for cell in row:
                if cell.comment is not None:
                    cell.comment = None
        ws.sheet_view.showGridLines = src.sheet_view.showGridLines
        ws.sheet_view.zoomScale = src.sheet_view.zoomScale
        ws.print_area = src.print_area if src.print_area else f"A1:CX{PAGE_BOTTOM}"
        if clear_from is not None:
            self.clear_rows(ws, clear_from, clear_to or PAGE_BOTTOM)
        if base in ALIASES:
            ws["B6"].value = TITLES.get(base, base)
        self.pages.append((base, ws))
        return ws

    @staticmethod
    def _merge_keep_style(ws, coord):
        mcr = MergedCellRange(ws, coord)
        ws.merged_cells.add(mcr)
        first = True
        for (r, c) in mcr.cells:
            if first:
                first = False
                continue
            old = ws._cells.get((r, c))
            mc = MergedCell(ws, row=r, column=c)
            if old is not None:
                mc._style = copy(old._style)
            ws._cells[(r, c)] = mc

    def clear_rows(self, ws, top, bottom, frame=True):
        for m in list(ws.merged_cells.ranges):
            if m.max_row >= top and m.min_row <= bottom:
                ws.unmerge_cells(m.coord)
        for r in range(top, bottom + 1):
            ws.row_dimensions[r].height = ROW_H
            for c in range(1, COL_LAST + 2):
                cell = ws.cell(r, c)
                cell.value = None
                cell.font = F_BODY
                cell.fill = FILL_NONE
                cell.border = Border()
                cell.alignment = Alignment(vertical="center")
        if frame:
            for r in range(top, bottom + 1):
                ws.cell(r, COL_FIRST).border = Border(left=THIN)
                ws.cell(r, COL_LAST).border = Border(right=THIN)
            if bottom == PAGE_BOTTOM:
                for c in range(COL_FIRST, COL_LAST + 1):
                    b = ws.cell(bottom, c).border
                    ws.cell(bottom, c).border = Border(left=b.left, right=b.right, bottom=THIN)

    def extend_frame(self, ws, new_bottom, extra_right_cols=(), title_rows="1:6"):
        """Grow a page downwards (single long sheet): move the frame's bottom border to new_bottom."""
        old = self.frame_bottom.get(ws.title, PAGE_BOTTOM)
        if new_bottom <= old:
            return
        for c in range(COL_FIRST, COL_LAST + 1):
            set_border(ws.cell(old, c), bottom=NOSIDE)
        for r in range(old + 1, new_bottom + 1):
            ws.row_dimensions[r].height = ROW_H
            for c in range(1, COL_LAST + 2):
                cell = ws.cell(r, c)
                cell.font = F_BODY
                cell.alignment = Alignment(vertical="center")
            set_border(ws.cell(r, COL_FIRST), left=THIN)
            set_border(ws.cell(r, COL_LAST), right=THIN)
            for c in extra_right_cols:
                set_border(ws.cell(r, c), right=THIN)
        for c in range(COL_FIRST, COL_LAST + 1):
            set_border(ws.cell(new_bottom, c), bottom=THIN)
        self.frame_bottom[ws.title] = new_bottom
        self.long_print(ws, new_bottom, title_rows)

    @staticmethod
    def long_print(ws, bottom, title_rows="1:6"):
        """Print setup for a sheet longer than one page: fit width, repeat header rows on every page."""
        ws.print_area = f"A1:CX{bottom}"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.print_title_rows = title_rows

    def clone_rows(self, src, r1, r2, ws, d1, with_values=True):
        off = d1 - r1
        for m in list(ws.merged_cells.ranges):
            if m.max_row >= d1 and m.min_row <= r2 + off:
                ws.unmerge_cells(m.coord)
        for m in src.merged_cells.ranges:
            if m.min_row >= r1 and m.max_row <= r2:
                ws.merge_cells(start_row=m.min_row + off, start_column=m.min_col,
                               end_row=m.max_row + off, end_column=m.max_col)
        for r in range(r1, r2 + 1):
            ws.row_dimensions[r + off].height = src.row_dimensions[r].height or ROW_H
            for c in range(1, COL_LAST + 1):
                s = src.cell(r, c)
                d = ws.cell(r + off, c)
                d._style = copy(s._style)
                if not isinstance(d, MergedCell):
                    d.value = s.value if (with_values and not isinstance(s, MergedCell)) else None

    # ---- header
    def header_cells(self, base):
        if base in self._hdr_cache:
            return self._hdr_cache[base]
        src = self.src[base]
        merges = [m for m in src.merged_cells.ranges if m.min_row <= 4]
        res = {}
        labels = {"Phase": "phase", "Project Name": "project_name", "Block Name": "block_name",
                  "Function Name": "function_name", "Document Name": "document_name", "Title": "title",
                  "Created": "created_date", "Updated": "updated_date", "Page": "page"}
        row_kind = {}
        for r in range(1, 5):
            for c in range(1, COL_LAST + 1):
                v = src.cell(r, c).value
                if not isinstance(v, str):
                    continue
                v = v.strip()
                if v in labels or v == "By":
                    end_c = c
                    for m in merges:
                        if m.min_row == r and m.min_col == c:
                            end_c = m.max_col
                    nxt = sorted([m for m in merges if m.min_row == r and m.min_col > end_c],
                                 key=lambda m: m.min_col)
                    if not nxt:
                        continue
                    coord = f"{CL(nxt[0].min_col)}{r}"
                    if v == "By":
                        key = "created_by" if row_kind.get(r) == "created" else "updated_by"
                    else:
                        key = labels[v]
                        if v == "Created":
                            row_kind[r] = "created"
                        if v == "Updated":
                            row_kind[r] = "updated"
                    res[key] = coord
        self._hdr_cache[base] = res
        return res

    def doc_name(self):
        src = self.src.get("Gen Desc")
        coord = self.header_cells("Gen Desc").get("document_name") if src else None
        return (src[coord].value if coord else None) or f"UISS-{BLOCK_NAME[self.kind]}"

    def finalize(self, out_path):
        from openpyxl.workbook.properties import CalcProperties
        total = len(self.pages)
        h = self.header
        has_rev = any(b == "Revision" for b, _ in self.pages)
        rev_cells = self.header_cells("Revision") if has_rev else {}
        self.wb.calculation = CalcProperties(fullCalcOnLoad=True)
        for i, (base, ws) in enumerate(self.pages, 1):
            cells = self.header_cells(base)
            vals = {
                "phase": h.get("phase", "DR"),
                "project_name": h.get("project_name", "TBD"),
                "block_name": h.get("block_name", BLOCK_NAME[self.kind]),
                "function_name": h.get("function_name", "TBD"),
                "title": TITLES.get(base, base),
                "created_date": h.get("created_date", ""),
                "created_by": h.get("created_by", ""),
                "updated_date": h.get("updated_date", ""),
                "updated_by": h.get("updated_by", ""),
                "page": f"{i}/{total}",
            }
            if h.get("document_name") and base != "Revision":
                vals["document_name"] = h["document_name"]
            if base == "Revision":
                # the Revision sheet holds the document-level values; its own title names the sheet
                vals["document_name"] = h.get("document_name") or self.doc_name()
                vals["title"] = "Revision Historical Record"
            elif rev_cells:
                for key, rc in rev_cells.items():
                    if key not in ("title", "page") and key in cells:
                        vals[key] = f'=IF(Revision!{rc}="","",Revision!{rc})'
            for key, coord in cells.items():
                if key in vals:
                    c = ws[coord]
                    c.value = vals[key]
                    al = copy(c.alignment)
                    al.shrink_to_fit = True
                    c.alignment = al
            ws.sheet_view.tabSelected = (i == 1)
        for ws in {id(w): w for w in self.src.values()}.values():   # aliases share a sheet
            self.wb.remove(ws)
        self.wb.active = 0
        self.wb.save(out_path)
        shapes.inject(out_path, self.shapes)

    def summary(self):
        tbd_count = {}
        for base, ws in self.pages:
            n = 0
            for row in ws.iter_rows(min_row=5):
                for c in row:
                    if isinstance(c.value, str) and "TBD" in c.value:
                        n += 1
            if n:
                tbd_count[ws.title] = n
        return {"sheets": [ws.title for _, ws in self.pages], "tbd_cells": tbd_count}


# --------------------------------------------------------------------------- cell helpers
def set_border(cell, top=None, bottom=None, left=None, right=None):
    b = cell.border
    cell.border = Border(top=b.top if top is None else top, bottom=b.bottom if bottom is None else bottom,
                         left=b.left if left is None else left, right=b.right if right is None else right)


def put(ws, r, c, value, font=F_BODY, h="left", wrap_text=False, shrink=False):
    cell = ws.cell(r, c)
    if isinstance(cell, MergedCell):
        return
    cell.value = value
    cell.font = font
    cell.alignment = Alignment(horizontal=h, vertical="center", wrap_text=wrap_text, shrink_to_fit=shrink)


def add_dv(ws, items, sqref):
    dv = DataValidation(type="list", formula1=f'"{items}"', allow_blank=True, showDropDown=False)
    dv.add(sqref)
    ws.add_data_validation(dv)


# --------------------------------------------------------------------------- grid tables
class GridTable:
    """Fill a preformatted table sheet (rows already styled in the template)."""

    def __init__(self, book, base, cfg):
        self.book, self.base, self.cfg = book, base, cfg
        self.src = book.src[base]
        self.ws = None
        self.spans = {}
        for key, letter in cfg["cols"].items():
            c = CI(letter)
            end = c
            for m in self.src.merged_cells.ranges:
                if m.min_row == cfg["first"] and m.min_col == c:
                    end = m.max_col
            self.spans[key] = (c, end)

    def _new_page(self):
        ws = self.book.new_page(self.base)
        f, l = self.cfg["first"], self.cfg["last"]
        for r in range(f, l + 1):
            ws.row_dimensions[r].height = 12.0 if self.base == "Revision" else ROW_H
            for c in range(COL_FIRST, COL_LAST + 1):
                cell = ws.cell(r, c)
                if not isinstance(cell, MergedCell):
                    cell.value = None
                cell.fill = FILL_NONE
                if cell.font.b:
                    cell.font = F_BODY
        for key, items in self.cfg.get("dv", {}).items():
            c1, c2 = self.spans[key]
            add_dv(ws, items, f"{CL(c1)}{f}:{CL(c2)}{l}")
        self.ws, self.row = ws, f
        # separator style used between records (hair for item lists, thin for messages)
        self.sep = ws.cell(f + 1, COL_FIRST).border.top
        if self.sep is None or self.sep.style is None:
            self.sep = HAIR

    def render(self, records, auto_number=True):
        self._new_page()
        n_auto, prepared = 0, []
        for rec in records:
            is_group = "group" in rec
            if is_group:
                key = self.cfg.get("group_col", list(self.cfg["cols"])[1])
                vals = {key: rec["group"]}
            else:
                vals = dict(rec)
                if auto_number and "no" in self.cfg["cols"] and vals.get("no") in (None, ""):
                    n_auto += 1
                    vals["no"] = n_auto
                act = vals.get("action")
                if isinstance(act, dict):
                    vals["action"] = f"System : {act.get('system', '-')}\nUser : {act.get('user', '-')}"
            lines, shrink = {}, {}
            for key, v in vals.items():
                if key not in self.spans or v is None:
                    continue
                c1, c2 = self.spans[key]
                lines[key], shrink[key] = layout_text(v, self.book.span_px(c1, c2), bold=is_group)
            n = max([len(x) for x in lines.values()] + [1])
            prepared.append((is_group, lines, shrink, n))
        last = self.cfg["last"]
        if self.cfg.get("extend"):
            # single sheet: grow the preformatted table downwards instead of adding "(2)" sheets
            need_last = self.cfg["first"] + sum(p[3] for p in prepared) - 1
            if need_last > last:
                for r in range(last + 1, need_last + 1):
                    self.book.clone_rows(self.src, self.cfg["first"] + 1, self.cfg["first"] + 1, self.ws, r,
                                         with_values=False)
                    self.ws.row_dimensions[r].height = ROW_H
                for c in range(COL_FIRST, COL_LAST + 1):
                    set_border(self.ws.cell(last, c), bottom=self.sep)
                    set_border(self.ws.cell(need_last, c), bottom=THIN)
                last = need_last
            self.book.long_print(self.ws, max(last, self.cfg["last"]), title_rows=f"1:{self.cfg['first'] - 1}")
        for is_group, lines, shrink, n in prepared:
            if self.row + n - 1 > last:
                self._new_page()
            for i in range(n):
                r = self.row + i
                for key, ls in lines.items():
                    if i < len(ls):
                        c1, _ = self.spans[key]
                        h = "center" if key in self.cfg.get("center", []) else "left"
                        put(self.ws, r, c1, ls[i], F_BOLD if is_group else F_BODY, h, shrink=shrink[key])
                if is_group and self.cfg.get("group_fill"):
                    for c in range(COL_FIRST, COL_LAST + 1):
                        self.ws.cell(r, c).fill = FILL_YELLOW
                # remove separators inside a multi-line record
                for c in range(COL_FIRST, COL_LAST + 1):
                    cell = self.ws.cell(r, c)
                    if i > 0:
                        set_border(cell, top=NOSIDE)
                    if i < n - 1:
                        set_border(cell, bottom=NOSIDE)
            self.row += n
        return self


# --------------------------------------------------------------------------- flow pages
class Flow:
    """Free-flow renderer: headings, text, items, tables, images in one or two columns."""

    def __init__(self, book, base, layout="two", divider=False, ws=None, start_row=None,
                 top=FLOW_TOP, bottom=FLOW_BOTTOM, on_new_page=None):
        self.book, self.base = book, base
        self.regions = REGIONS_TWO if layout == "two" else REGION_FULL
        self.divider = divider and layout == "two"
        self.top, self.bottom = top, bottom
        self.base_bottom = bottom
        self.base_top = top
        self.on_new_page = on_new_page
        self.title_rows = TITLE_ROWS.get(base, "1:6")
        if ws is not None:
            self.ws, self.ri, self.row = ws, 0, start_row or top
            self.dirty = True
        else:
            self.new_page()

    def _next_block(self, extra_cols=()):
        """Continue on the same sheet: append a page-sized block below the current frame."""
        old = self.book.frame_bottom.get(self.ws.title, PAGE_BOTTOM)
        new_bottom = old + (PAGE_BOTTOM - BODY_TOP + 1)
        self.book.extend_frame(self.ws, new_bottom, extra_right_cols=extra_cols, title_rows=self.title_rows)
        self.ws.row_breaks.append(Break(id=old))
        self.top = old + 1 + (self.base_top - BODY_TOP)
        self.bottom = new_bottom - (PAGE_BOTTOM - self.base_bottom)
        self.ri, self.row, self.dirty = 0, self.top, False

    def new_page(self):
        if getattr(self, "ws", None) is not None:
            self._next_block((52,) if self.divider else ())
            return
        ws = self.book.new_page(self.base, clear_from=BODY_TOP)
        self.book.long_print(ws, PAGE_BOTTOM, self.title_rows)
        if self.divider:
            for r in range(BODY_TOP, PAGE_BOTTOM + 1):
                set_border(ws.cell(r, 52), right=THIN)
        self.ws, self.ri, self.row, self.dirty = ws, 0, self.top, False
        self.bottom = self.base_bottom
        if self.on_new_page:
            self.row = self.on_new_page(self) or self.row

    @property
    def c0(self):
        return self.regions[self.ri][0]

    @property
    def c1(self):
        return self.regions[self.ri][1]

    def remaining(self):
        return self.bottom - self.row + 1

    def next_region(self):
        if self.ri + 1 < len(self.regions):
            self.ri += 1
            self.row = self.top
        else:
            self.new_page()

    def ensure(self, n):
        if self.remaining() < n:
            self.next_region()

    def gap(self, n=1):
        if self.row != self.top:
            self.row = min(self.row + n, self.bottom + 1)

    # ---- text blocks
    # Columns are always resolved *after* ensure(), because ensure() may move to the next column/page.
    def width_from(self, offset):
        return min(self.book.span_px(r0 + offset, r1) for r0, r1 in self.regions)

    def line(self, offset, text, font=F_BODY, h="left"):
        self.ensure(1)
        put(self.ws, self.row, self.c0 + offset, text, font, h)
        self.row += 1
        self.dirty = True

    def heading(self, text, num=None, level=0, gap=True):
        if gap:
            self.gap()
        self.ensure(6)  # keep the heading with the first lines of its content
        placed, off = [], level
        if num:
            nc = max(1, math.ceil((text_px(num, True) + 4) / 10))
            placed.append((0, off, num))
            off += nc
        for i, ln in enumerate(wrap(text, self.width_from(off), True)):
            placed.append((i, off, ln))
        start = self.row
        for (i, o, t) in placed:
            put(self.ws, start + i, self.c0 + o, t, F_BOLD)
        self.row = start + max(i for i, _o, _t in placed) + 1
        self.dirty = True
        self.last_heading = dict(ws=self.ws, ri=self.ri, start=start, end=self.row, placed=placed)

    def _carry_heading(self):
        """Go to the next region, taking along a heading that sits directly above the current row."""
        h = getattr(self, "last_heading", None)
        carry = h and h["ws"] is self.ws and h["ri"] == self.ri and h["end"] == self.row
        if carry:
            for (i, o, _t) in h["placed"]:
                self.ws.cell(h["start"] + i, self.c0 + o).value = None
        self.next_region()
        if carry:
            start = self.row
            for (i, o, t) in h["placed"]:
                put(self.ws, start + i, self.c0 + o, t, F_BOLD)
            self.row = start + max(i for i, _o, _t in h["placed"]) + 1
        self.last_heading = None

    def text(self, text, level=2, bold=False, italic=False):
        font = F_BOLD if bold else (F_ITAL if italic else F_BODY)
        for ln in wrap(text, self.width_from(level), bold):
            self.line(level, ln, font)

    def item(self, marker, text, level=2, bold=False):
        mc = max(1, math.ceil((text_px(str(marker)) + 3) / 10))
        lines = wrap(text, self.width_from(level + mc), bold) or [""]
        for i, ln in enumerate(lines):
            self.ensure(1)
            if i == 0:
                put(self.ws, self.row, self.c0 + level, marker, F_BODY)
            put(self.ws, self.row, self.c0 + level + mc, ln, F_BOLD if bold else F_BODY)
            self.row += 1
        self.dirty = True
        if bold and len(lines) == 1:
            # a bold item acts as a sub-heading: a table right after it carries it to the next column
            self.last_heading = dict(ws=self.ws, ri=self.ri, start=self.row - 1, end=self.row,
                                     placed=[(0, level, marker), (0, level + mc, lines[0])])

    def bullets(self, items, level=2, marker="-"):
        for i, it in enumerate(items):
            if marker in ("1.", "1)"):
                m = f"{i + 1}{marker[-1]}"
            elif marker in ("a.", "a)"):
                m = f"{chr(97 + i % 26)}{marker[-1]}"
            else:
                m = marker
            if isinstance(it, dict):
                self.item(it.get("marker", m), it.get("text", ""), level, it.get("bold", False))
                if it.get("children"):
                    self.bullets(it["children"], level + 1, it.get("child_marker", "-"))
            else:
                self.item(m, it, level)

    # ---- tables
    def table(self, columns, rows, level=2, fill=FILL_ORANGE, group_header=None, row_lines="all",
              stretch=False, min_rows=0, group_cols=0):
        """row_lines='all' draws a line above every record; 'group' only above records whose first
        cell is filled. group_cols=N keeps the first N columns grouped (line only at a new group)
        while the remaining columns get a line above every record."""
        x0 = self.c0 + level
        avail = self.c1 - x0 + 1
        want = [max(1, int(c.get("width", 4))) for c in columns]
        total = sum(want)
        if total > avail or stretch:
            scale = avail / total
            want = [max(1, int(w * scale)) for w in want]
            while sum(want) > avail:
                want[want.index(max(want))] -= 1
        spans = []

        def place():
            # (re)compute column spans for the current region (regions shift when the table breaks)
            spans.clear()
            x = self.c0 + level
            for w in want:
                spans.append((x, x + w - 1))
                x += w

        place()
        hdr_lay = [layout_text(c.get("title", ""), self.book.span_px(*spans[j]), True)
                   for j, c in enumerate(columns)]
        hdr_lines = max([len(ls) for ls, _ in hdr_lay] + [1])
        hdr_rows = hdr_lines + (1 if group_header else 0)

        def draw_header():
            r0 = self.row
            grouped = set()
            if group_header:
                for g in group_header:
                    a, b = spans[g["from"]][0], spans[g["to"]][1]
                    self._box(r0, a, r0, b, g["title"], F_BOLD, "center", fill, THIN, THIN)
                    grouped.update(range(g["from"], g["to"] + 1))
            for j, col in enumerate(columns):
                a, b = spans[j]
                sk = hdr_lay[j][1]
                if j in grouped:
                    self._box(r0 + 1, a, r0 + hdr_rows - 1, b, col.get("title", ""), F_BOLD, "center", fill,
                              THIN, THIN, shrink=sk)
                else:
                    self._box(r0, a, r0 + hdr_rows - 1, b, col.get("title", ""), F_BOLD, "center", fill,
                              THIN, THIN, shrink=sk)
            self.row += hdr_rows

        last_row_written = None
        all_rows = list(rows) + [[""] * len(columns)] * max(0, min_rows - len(rows))
        recs, lay = [], []
        for rec in all_rows:
            rec = list(rec) + [""] * (len(columns) - len(rec))
            cells, shr = [], []
            for j, v in enumerate(rec):
                ls, sk = layout_text(v, self.book.span_px(*spans[j]))
                cells.append(ls)
                shr.append(sk)
            recs.append(rec)
            lay.append((cells, shr))
        if row_lines == "group":
            # long group labels flow down into the following rows of the same group
            spill = range(max(1, group_cols))
            k = 0
            while k < len(recs):
                j = k + 1
                while j < len(recs) and recs[j][0] in (None, ""):
                    j += 1
                for col in spill:
                    first = lay[k][0][col]
                    hs = [max([len(c) for ci, c in enumerate(lay[i][0]) if ci not in spill] + [1])
                          for i in range(k, j)]
                    if len(first) > hs[0] and all(not lay[i][0][col] for i in range(k + 1, j)):
                        pos = 0
                        for idx, i in enumerate(range(k, j)):
                            lay[i][0][col] = first[pos:pos + hs[idx]]
                            pos += hs[idx]
                        if pos < len(first):
                            lay[j - 1][0][col] = lay[j - 1][0][col] + first[pos:]
                k = j
        heights = [max([len(c) for c in lay[k][0]] + [1]) for k in range(len(recs))]
        total = hdr_rows + sum(heights)
        region_rows = self.bottom - self.top + 1
        if total > self.remaining() and total <= min(region_rows, 24) and self.row != self.top:
            # small table: keep it together (with its heading) in the next column/page
            self._carry_heading()
        self.ensure(hdr_rows + 1)
        place()
        draw_header()
        for k, rec in enumerate(recs):
            cells, shr = lay[k]
            n = heights[k]
            if self.remaining() < n:
                if last_row_written:
                    self._hline(last_row_written, spans[0][0], spans[-1][1], bottom=THIN)
                self.next_region()
                place()
                self.ensure(hdr_rows + n)
                draw_header()
            group_start = row_lines == "all" or k == 0 or rec[0] not in (None, "")
            for i in range(n):
                r = self.row
                for j, (a, b) in enumerate(spans):
                    h = columns[j].get("align", "left")
                    txt = cells[j][i] if i < len(cells[j]) else None
                    line_here = group_start or (group_cols and j >= group_cols)
                    self._box(r, a, r, b, txt, F_BODY, h, None, THIN if (i == 0 and line_here) else None, None,
                              shrink=shr[j])
                self.row += 1
                last_row_written = r
        if last_row_written:
            self._hline(last_row_written, spans[0][0], spans[-1][1], bottom=THIN)
        self.dirty = True

    def _box(self, r1, c1, r2, c2, value, font, h, fill, top, bottom, shrink=False):
        ws = self.ws
        if (r1, c1) != (r2, c2):
            ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
        cell = ws.cell(r1, c1)
        cell.value = value
        cell.font = font
        cell.alignment = Alignment(horizontal=h, vertical="center", wrap_text=(r2 > r1 and not shrink),
                                   shrink_to_fit=shrink)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                x = ws.cell(r, c)
                if fill is not None:
                    x.fill = fill
                b = x.border
                x.border = Border(
                    left=THIN if c == c1 else b.left, right=THIN if c == c2 else b.right,
                    top=(top if (r == r1 and top is not None) else b.top),
                    bottom=(bottom if (r == r2 and bottom is not None) else b.bottom))

    def _hline(self, r, c1, c2, bottom):
        for c in range(c1, c2 + 1):
            set_border(self.ws.cell(r, c), bottom=bottom)

    # ---- images
    def image(self, path, caption=None, level=0, max_rows=None, fresh_page=False, upscale=1.6, frame=True):
        from PIL import Image as PILImage, ImageOps
        if fresh_page and self.dirty:
            self.new_page()
        if not path or not os.path.exists(path):
            self.placeholder(f"[IMAGE NOT FOUND: {os.path.basename(str(path))}]" if path else "[IMAGE HERE]",
                             caption)
            return
        im = PILImage.open(path)
        if frame or im.format not in ("PNG", "JPEG"):
            p2 = os.path.join(self.book.tmpdir, f"img_{len(os.listdir(self.book.tmpdir))}.png")
            im2 = im.convert("RGB")
            if frame:  # thin gray outline so a screenshot is clearly delimited on the sheet
                im2 = ImageOps.expand(im2, border=2, fill="#808080")
            im2.save(p2)
            path, im = p2, PILImage.open(p2)
        w, h = im.size
        cap_rows = 1 if caption else 0

        def fit(rows_avail):
            x0 = self.c0 + level
            width_px = self.book.span_px(x0, self.c1) - 6
            s = min(width_px / w, upscale)
            rows_avail -= cap_rows
            if max_rows:
                rows_avail = min(rows_avail, max_rows)
            if h * s > rows_avail * ROW_PX * 0.95:
                s = rows_avail * ROW_PX * 0.95 / h
            return s

        self.gap()
        s = fit(self.remaining())
        full = fit(self.bottom - self.top + 1)
        if s < 0.6 * full and self.row != self.top:
            self.next_region()
            s = fit(self.remaining())
        if caption:
            self.line(level, caption, F_BOLD)
        img = XLImage(path)
        img.width, img.height = int(w * s), int(h * s)
        self.ws.add_image(img, f"{CL(self.c0 + level)}{self.row}")
        self.row = min(self.row + math.ceil(img.height / ROW_PX) + 1, self.bottom + 1)
        self.dirty = True

    def placeholder(self, text, caption=None):
        if caption:
            self.line(0, caption, F_BOLD)
        mid = (self.c0 + self.c1) // 2
        r = min(self.row + 12, self.bottom)
        put(self.ws, r, mid, text, F_BODY, "center")
        self.row = r + 2
        self.dirty = True

    def flowchart(self, spec, caption=None, level=0, max_rows=None, fresh_page=False, grow=False,
                  divider_cols=()):
        """Editable flowchart: Excel shapes + glued connectors (raw DOT specs fall back to an image)."""
        if "dot" in spec or not spec.get("nodes"):
            png = render_flow(spec, self.book.tmpdir)
            self.image(png, caption, level, max_rows, fresh_page, upscale=1.0, frame=False)
            return
        if fresh_page and self.dirty:
            self.new_page()
        self.gap()
        dot = flow_dot(spec)
        W, H, _ = shapes.layout(dot)
        width_px = self.book.span_px(self.c0 + level, self.c1) - 8
        s_w = min(width_px / max(W * 96, 1), 1.0)
        cap_rows = 1 if caption else 0
        need_rows = math.ceil(H * 72 * s_w / ROW_H) + 1 + cap_rows
        if not grow:
            avail = self.remaining()
            full = self.bottom - self.top + 1
            if need_rows > avail and self.row != self.top and avail < 0.6 * min(need_rows, full):
                self.next_region()
            max_rows_avail = min(self.remaining(), max_rows or 999) - cap_rows
        else:
            # prefer one printed page: shrink down to 70% before growing the sheet
            page_rows = self.bottom - self.row + 1 - cap_rows
            s_page = page_rows * ROW_H / max(H * 72, 1)
            s_g = min(s_w, max(s_page, 0.7))
            need_rows = math.ceil(H * 72 * s_g / ROW_H) + 1 + cap_rows
            width_px = int(W * 96 * s_g) + 1
            if need_rows > self.remaining():
                new_bottom = self.row + need_rows
                self.book.extend_frame(self.ws, new_bottom + 1, extra_right_cols=divider_cols,
                                       title_rows=self.title_rows)
                self.bottom = new_bottom
            max_rows_avail = None
        if caption:
            self.line(self.c0 + level, caption, F_BOLD)
        xml, used_pt = shapes.build(self.book, self.ws, spec, dot, _wrap_label, self.c0 + level, self.row,
                                    width_px, max_h_pt=(max_rows_avail * ROW_H if max_rows_avail else None),
                                    grow=grow, default_row_pt=ROW_H)
        self.book.shapes.setdefault(self.ws.title, []).extend(xml)
        self.row = min(self.row + math.ceil(used_pt / ROW_H) + 1, self.bottom + 1)
        self.dirty = True

    # ---- generic block dispatcher (used by Operation Desc / free sections)
    def blocks(self, blocks):
        for b in blocks:
            t = b.get("type", "text")
            lv = b.get("level")
            if t == "heading":
                self.heading(b["text"], b.get("num"), lv or 0)
            elif t == "text":
                self.text(b["text"], 2 if lv is None else lv, b.get("bold", False), b.get("italic", False))
            elif t == "item":
                self.item(b.get("marker", "-"), b["text"], 2 if lv is None else lv, b.get("bold", False))
            elif t == "bullets":
                self.bullets(b["items"], 2 if lv is None else lv, b.get("marker", "-"))
            elif t == "table":
                self.table(b["columns"], b["rows"], 2 if lv is None else lv,
                           group_header=b.get("group_header"), row_lines=b.get("row_lines", "all"),
                           stretch=b.get("stretch", False), group_cols=b.get("group_cols", 0))
            elif t == "image":
                self.image(b.get("path"), b.get("caption"), lv or 0, b.get("max_rows"), b.get("fresh_page", False))
            elif t == "flow":
                self.flowchart(b["spec"], b.get("caption"), lv or 0, b.get("max_rows"), b.get("fresh_page", False))
            elif t == "spacer":
                self.row = min(self.row + int(b.get("rows", 1)), self.bottom + 1)
            elif t == "column_break":
                if self.row != self.top:
                    self.next_region()
            elif t == "page_break":
                if self.dirty:
                    self.new_page()
            else:
                raise ValueError(f"unknown block type: {t}")


# --------------------------------------------------------------------------- flowchart (graphviz)
SHAPES = {
    "start": 'shape=box, style="rounded,filled", fillcolor="#FFFFFF"',
    "end": 'shape=box, style="rounded,filled", fillcolor="#FFFFFF"',
    "process": 'shape=box',
    "decision": 'shape=diamond, margin="0.05,0.03"',
    "screen": 'shape=box, style="filled", fillcolor="#EDEDED", penwidth=1.3',
    "db": 'shape=cylinder',
    "file": 'shape=note',
    "document": 'shape=note',
    "io": 'shape=parallelogram',
    "message": 'shape=box, style="dashed,filled", fillcolor="#FFFFFF"',
    "subprocess": 'shape=box, peripheries=2',
    "event": 'shape=box, style="rounded,filled", fillcolor="#FFF2CC"',
    "note": 'shape=note, style="filled", fillcolor="#FFFFE0", fontsize=9',
}


def _q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _wrap_label(s, n=26):
    out = []
    for para in str(s).split("\n"):
        line = ""
        for w in para.split(" "):
            if line and len(line) + 1 + len(w) > n:
                out.append(line)
                line = w
            else:
                line = w if not line else line + " " + w
        out.append(line)
    return "\n".join(out)


def flow_dot(spec):
    if "dot" in spec:
        return spec["dot"]
    if True:
        d = spec.get("direction", "TB")
        lines = [
            "digraph G {", f"rankdir={d};",
            'graph [fontname="Liberation Sans", fontsize=10, nodesep=0.35, ranksep=0.4, bgcolor="transparent", pad=0.2];',
            'node [fontname="Liberation Sans", fontsize=10, shape=box, style="filled", fillcolor="white", '
            'color="black", penwidth=1.0, margin="0.12,0.05"];',
            'edge [fontname="Liberation Sans", fontsize=9, color="black", arrowsize=0.7];',
        ]
        nodes = {n["id"]: n for n in spec.get("nodes", [])}
        laned = any(n.get("lane") in ("input", "output") for n in nodes.values())

        def node_line(n):
            t = n.get("type", "process")
            label = n.get("label", n["id"])
            if t == "screen" and n.get("screen_id"):
                label = f"[{n['screen_id']}]\n{label}"
            if n.get("step") is not None:
                label = f"({n['step']}) {label}"
            return f'{_q(n["id"])} [label={_q(_wrap_label(label))}, {SHAPES.get(t, SHAPES["process"])}];'

        if laned:
            # three invisible clusters keep inputs left, process in the middle, outputs right
            lines.append("newrank=true;")
            for lane in ("input", None, "output"):
                members = [n for n in nodes.values() if (n.get("lane") if n.get("lane") in ("input", "output") else None) == lane]
                lines.append(f"subgraph cluster_{lane or 'process'} {{ style=invis;")
                lines.extend(node_line(n) for n in members)
                lines.append("}")
        else:
            lines.extend(node_line(n) for n in spec.get("nodes", []))
        for grp in spec.get("same_rank", []):
            lines.append("{rank=same; " + " ".join(_q(x) for x in grp) + "}")
        # lanes: a store with lane input/output and exactly one connection sits on the same row as
        # its process - inputs to the left, outputs to the right (Functional Flow style)
        conn = {}
        for e in spec.get("edges", []):
            conn.setdefault(e["from"], []).append(e)
            conn.setdefault(e["to"], []).append(e)
        flat = {}
        for nid, n in nodes.items():
            lane = n.get("lane")
            if lane in ("input", "output") and len(conn.get(nid, [])) == 1:
                e = conn[nid][0]
                other = e["to"] if e["from"] == nid else e["from"]
                lines.append("{rank=same; " + _q(nid) + " " + _q(other) + "}")
                flat[id(e)] = (nid, other) if lane == "input" else (other, nid)
        for e in spec.get("edges", []):
            if id(e) in flat:
                a, b_ = flat[id(e)]
                back = (a, b_) != (e["from"], e["to"])
                attrs = ["dir=back" if back else "dir=forward"]
                if e.get("label"):
                    attrs.append(f"label={_q(_wrap_label(e['label'], 20))}")
                attrs.append(f"style={e.get('style', 'dashed')}")
                lines.append(f'{_q(a)} -> {_q(b_)} [{", ".join(attrs)}];')
                continue
            attrs = []
            if e.get("label"):
                attrs.append(f"label={_q(_wrap_label(e['label'], 20))}")
            if e.get("style"):
                attrs.append(f"style={e['style']}")
            lines.append(f'{_q(e["from"])} -> {_q(e["to"])}' + (f" [{', '.join(attrs)}]" if attrs else "") + ";")
        lines.append("}")
        return "\n".join(lines)


def render_flow(spec, tmpdir):
    src = flow_dot(spec)
    out = os.path.join(tmpdir, f"flow_{len(os.listdir(tmpdir))}.png")
    subprocess.run(["dot", "-Tpng", "-Gdpi=160", "-Gbgcolor=transparent", "-o", out], input=src.encode("utf-8"), check=True)
    return out


# --------------------------------------------------------------------------- section renderers
def render_revision(book, spec):
    h = book.header
    revs = spec.get("revisions") or [{
        "revision": "0.1", "author": h.get("created_by", ""), "date": h.get("created_date", ""),
        "reviewed_by": "", "description": "Initial draft"}]
    GridTable(book, "Revision", GRID["Revision"]).render(revs, auto_number=False)


def render_gen_desc_screen(book, g):
    f = Flow(book, "Gen Desc", layout="two", divider=True)
    f.heading("OBJECTIVE", "1.", gap=False)
    for o in g.get("objective") or ["TBD"]:
        f.text(o, level=2)
    f.heading("DISPLAY CONTENTS", "2.")
    f.text("a. Display items", level=1, bold=True)
    f.text(g.get("display_items_note", 'Please refer to "Item Description" worksheet for details.'), level=2)
    f.row += 1
    f.text("b. Display Order:", level=1, bold=True)
    rows = []
    for sec in g.get("display_order") or [{"section": "TBD", "fields": [{"field": "TBD", "order": "TBD"}]}]:
        for i, fld in enumerate(sec.get("fields") or [{}]):
            rows.append([sec.get("section", "") if i == 0 else "", i + 1, fld.get("field", "TBD"),
                         fld.get("order", "Ascending")])
    f.table([{"title": "Section", "width": 14}, {"title": "No", "width": 2, "align": "center"},
             {"title": "Field Name", "width": 20}, {"title": "Order", "width": 8, "align": "center"}],
            rows, level=2, row_lines="group")
    f.heading("BUTTON FUNCTION", "3.")
    buttons = g.get("buttons") or []
    f.table([{"title": "No", "width": 2, "align": "center"}, {"title": "Button", "width": 10},
             {"title": "Function", "width": 34}],
            [[i + 1, b.get("name", ""), b.get("function", "TBD")] for i, b in enumerate(buttons)] or [["", "", ""]],
            level=1)
    # ---- right column
    f.blocks([{"type": "column_break"}])
    f.heading("BUTTON SETTINGS", "4.", gap=False)
    f.text("a. Screen Mode", level=1, bold=True)
    modes = g.get("screen_modes") or []
    mrows, matrix = [], []
    names = [b.get("name", "") for b in buttons]
    for i, m in enumerate(modes, 1):
        secs = m.get("sections") or [{"section": "", "description": ""}]
        for j, s in enumerate(secs):
            sub = chr(97 + j)
            mrows.append([i if j == 0 else "", m.get("mode", "") if j == 0 else "", sub,
                          s.get("section", ""), s.get("description", "")])
            st = s.get("buttons") or {}
            matrix.append([f"{i}.{sub}"] + [st.get(n, "TBD") for n in names])
    f.table([{"title": "No1", "width": 2, "align": "center"}, {"title": "Screen Mode", "width": 11},
             {"title": "No2", "width": 2, "align": "center"}, {"title": "Section", "width": 12},
             {"title": "Description", "width": 20}],
            mrows or [["", "", "", "", ""]], level=1, row_lines="group", group_cols=2)
    if g.get("screen_mode_remarks"):
        f.row += 1
        f.text("Remarks :", level=1, bold=True)
        for rm in g["screen_mode_remarks"]:
            f.text(rm, level=2)
    if names:
        chunks = math.ceil(len(names) / max(1, (REGIONS_TWO[1][1] - REGIONS_TWO[1][0] - 2) // 6))
        need = 3 + chunks * (len(matrix) + 4)
        if f.remaining() < need <= f.bottom - f.top + 1:
            f.next_region()
    f.heading("b. Button Control", None, level=1, gap=f.row != f.top)
    f.text("* explain availability according to screen mode      **No=No1.No2", level=2, italic=True)
    if names:
        avail = REGIONS_TWO[1][1] - (REGIONS_TWO[1][0] + 1) + 1
        # template: No = 2 grid columns, 5 per button; allow ~20% shrink-to-fit on long names
        single = [text_px(n, True) for n in names if " " not in n.strip()]
        multi = [text_px(w, True) for n in names if " " in n.strip() for w in n.split()]
        per = max(3, min(8, max(math.ceil((max(single or [0]) * 0.8 + 4) / 10),
                                math.ceil((max(multi or [0]) + 8) / 10))))
        if per * len(names) + 2 <= avail:
            per = max(per, min(5, (avail - 2) // len(names)))
        chunk = max(1, (avail - 2) // per)
        chunk = math.ceil(len(names) / math.ceil(len(names) / chunk))
        for k in range(0, len(names), chunk):
            part = names[k:k + chunk]
            cols = [{"title": "No", "width": 2, "align": "center"}] + \
                   [{"title": n, "width": per, "align": "center"} for n in part]
            rows = [[r[0]] + r[1 + k:1 + k + len(part)] for r in matrix] or [[""] * len(cols)]
            f.table(cols, rows, level=1,
                    group_header=[{"title": "Buttons  (E=Enable, D=Disable)", "from": 1, "to": len(part)}])
            f.row += 1


def render_gen_desc_report(book, g):
    f = Flow(book, "Gen Desc", layout="two", divider=True)
    f.heading("OBJECTIVE", "1.", gap=False)
    for o in g.get("objective") or ["TBD"]:
        f.text(o, level=2)
    f.heading("REPORT INFORMATION", "2.")
    f.item("a.", "General Information", level=1, bold=True)
    f.text('Please refer to "Report Layout" worksheet for details.', level=2)
    f.row += 1
    f.item("b.", "Report items", level=1, bold=True)
    f.text('Please refer to "Item Description" worksheet for details.', level=2)
    f.row += 1
    f.item("c.", "Printing Order", level=1, bold=True)
    rows = []
    for sec in g.get("printing_order") or [{"section": "TBD", "fields": [{"field": "TBD", "order": "TBD"}]}]:
        for i, fld in enumerate(sec.get("fields") or [{}]):
            rows.append([sec.get("section", "") if i == 0 else "", i + 1, fld.get("field", "TBD"),
                         fld.get("order", "Ascending")])
    f.table([{"title": "Section", "width": 14}, {"title": "No", "width": 2, "align": "center"},
             {"title": "Field Name", "width": 20}, {"title": "Order", "width": 8, "align": "center"}],
            rows, level=2, row_lines="group")
    f.row += 1
    f.item("d.", "Report Calling Screen", level=1, bold=True)
    cs = g.get("calling_screens") or [{"screen_id": "TBD", "description": ""}]
    f.table([{"title": "No", "width": 2, "align": "center"}, {"title": "Screen ID", "width": 13},
             {"title": "Description", "width": 31}],
            [[i + 1, c.get("screen_id", ""), c.get("description", "")] for i, c in enumerate(cs)], level=2)
    f.row += 1
    f.item("e.", "Report File", level=1, bold=True)
    rf = g.get("report_file") or {}
    f.table([{"title": "No", "width": 2, "align": "center"}, {"title": "Item", "width": 17},
             {"title": "Description", "width": 27}],
            [[1, "Report File Name", rf.get("file_name", "TBD")], [2, "Report Path", rf.get("path", "TBD")],
             [3, "Report File Keeping Period", rf.get("keeping_period", "TBD")]], level=2)
    f.blocks([{"type": "column_break"}])
    f.item("f.", "Report Generation Keys", level=1, bold=True)
    rows = []
    for sec in g.get("generation_keys") or [{"section": "TBD", "fields": [{"field": "TBD"}]}]:
        for i, fld in enumerate(sec.get("fields") or [{}]):
            rows.append([sec.get("section", "") if i == 0 else "", i + 1, fld.get("field", "TBD"),
                         fld.get("description", "")])
    f.table([{"title": "Section", "width": 8}, {"title": "No", "width": 2, "align": "center"},
             {"title": "Field", "width": 11}, {"title": "Description", "width": 25}],
            rows, level=2, row_lines="group")


def render_gen_desc_batch(book, g):
    f = Flow(book, "Gen Desc", layout="two", divider=True)
    f.heading("OBJECTIVE", "1.", gap=False)
    for o in g.get("objective") or ["TBD"]:
        f.text(o, level=2)
    f.heading("OPERATION FLOW", "2.")
    of = g.get("operation_flow") or {}
    if of.get("note"):
        f.text(of["note"], level=1, italic=True)
    if of.get("flow"):
        f.flowchart(of["flow"], of.get("caption"), level=1)
    elif of.get("image"):
        f.image(of["image"], of.get("caption"), level=1)
    elif not of.get("note"):
        f.text("Operation flow: TBD", level=1)
    f.blocks([{"type": "column_break"}])
    f.heading("INPUT/OUTPUT", "3.", gap=False)
    cols = [{"title": "No", "width": 2, "align": "center"}, {"title": "Data Source Name", "width": 14},
            {"title": "Type", "width": 4, "align": "center"}, {"title": "Description", "width": 26}]

    def io_rows(items):
        return [[i + 1, x.get("name", "TBD"), x.get("type", "TBD"), x.get("description", "")]
                for i, x in enumerate(items)] or [["", "", "", ""]]

    f.item("a.", "Input", level=1, bold=True)
    f.table(cols, io_rows(g.get("inputs") or []), level=1)
    f.row += 1
    f.item("b.", "Output", level=1, bold=True)
    out_cols = list(cols)
    out_cols[1] = {"title": "Output Name", "width": 14}
    f.table(out_cols, io_rows(g.get("outputs") or []), level=1)
    for k, t in enumerate(g.get("extra_tables") or []):
        f.row += 1
        f.item(f"{chr(99 + k)}.", t.get("title", ""), level=1, bold=True)
        tcols = [{"title": "No", "width": 2, "align": "center"}] + t.get("columns", [{"title": "Field Name", "width": 20}])
        trows = [[i + 1] + list(r if isinstance(r, (list, tuple)) else [r]) for i, r in enumerate(t.get("rows") or [])]
        f.table(tcols, trows or [[""] * len(tcols)], level=1)
    if g.get("constraints"):
        f.row += 1
        f.text("Concerns / Constraints :", level=1, bold=True)
        for c in g["constraints"]:
            f.item("-", c, level=2)


class FuncFlowPage(Flow):
    """Functional Flow: flowchart under the lane header (Input | Process | Output), numbered step
    descriptions in the right-hand Description column; descriptions continue on the next page."""
    started = False

    def new_page(self):
        if getattr(self, "ws", None) is not None:
            self._next_block((81,))
            self.ri = 1 if self.started else 0
            return
        ws = self.book.new_page(self.base, clear_from=8)
        self.book.long_print(ws, PAGE_BOTTOM, self.title_rows)
        for r in range(8, PAGE_BOTTOM + 1):
            set_border(ws.cell(r, 81), right=THIN)
        self.ws, self.row, self.dirty = ws, self.top, False
        self.bottom = self.base_bottom
        self.ri = 1 if self.started else 0

    def next_region(self):
        self.new_page()


def render_func_flow(book, ff):
    ff = ff or {}
    f = FuncFlowPage.__new__(FuncFlowPage)
    Flow.__init__(f, book, "Func Flow", layout="two", top=8)
    f.regions = [(3, 80), (83, 101)]
    f.ri = 0
    if ff.get("flow"):
        f.flowchart(ff["flow"], None, level=0, grow=True, divider_cols=(81,))
    elif ff.get("image"):
        f.image(ff["image"], None, level=0)
    else:
        f.placeholder("[FUNCTIONAL FLOW DIAGRAM - TBD]")
    f.started, f.ri, f.row = True, 1, f.top
    steps = ff.get("steps") or []
    width = book.span_px(83, 101)
    total = 0
    for st_ in steps:
        if isinstance(st_, dict):
            total += len(wrap(st_.get("text", ""), width)) + sum(
                len(wrap(c.get("text", "") if isinstance(c, dict) else c, width - 20)) for c in st_.get("children", []))
        else:
            total += len(wrap(st_, width))
    spaced = total + len(steps) <= f.bottom - f.top + 1
    for i, st_ in enumerate(steps, 1):
        if isinstance(st_, dict):
            f.item(st_.get("marker", f"{i}."), st_.get("text", ""), level=0)
            for ch in st_.get("children", []):
                f.item(ch.get("marker", "-") if isinstance(ch, dict) else "-",
                       ch.get("text", "") if isinstance(ch, dict) else ch, level=1)
        else:
            f.item(f"{i}.", st_, level=0)
        if spaced:
            f.row = min(f.row + 1, f.bottom + 1)


def render_screen_flow(book, diagrams):
    f = Flow(book, "Screen Flow", layout="full")
    if not diagrams:
        f.placeholder("[SCREEN FLOW DIAGRAM - TBD]")
        return
    for k, d in enumerate(diagrams):
        fresh = k > 0 and d.get("fresh_page", True)
        if fresh and f.dirty:
            f.new_page()
        if d.get("title"):
            f.heading(d["title"], level=1, gap=False)
        if d.get("flow"):
            f.flowchart(d["flow"], None, level=1, grow=True)
        else:
            f.image(d.get("image"), None, level=1)
        for n in d.get("notes", []):
            f.text(n, level=1)


def render_screen_layout(book, shots):
    """One sheet; screenshots stacked downwards (caption, image, notes), one printed page each."""
    from PIL import Image as PILImage, ImageOps
    ws = book.new_page("Screen Layout", clear_from=BODY_TOP)
    if not shots:
        put(ws, 20, 52, "[SCREEN IMAGE HERE]", F_BODY, "center")
        return
    c0, row = 4, FLOW_TOP
    width_px = book.span_px(c0, 101) - 6
    page_rows = FLOW_BOTTOM - FLOW_TOP + 1
    for k, s_ in enumerate(shots):
        if k > 0:
            ws.row_breaks.append(Break(id=row - 1))
        put(ws, row, c0, s_.get("caption") or f"Screen {k + 1}", F_BOLD)
        row += 1
        path = s_.get("image")
        notes = s_.get("notes", [])
        if path and os.path.exists(path):
            im = PILImage.open(path).convert("RGB")
            im = ImageOps.expand(im, border=2, fill="#808080")
            p2 = os.path.join(book.tmpdir, f"layout_{k}.png")
            im.save(p2)
            w, h = im.size
            max_h = (page_rows - 2 - len(notes)) * ROW_PX * 0.95
            sc = min(width_px / w, 1.6, max_h / h)
            img = XLImage(p2)
            img.width, img.height = int(w * sc), int(h * sc)
            ws.add_image(img, f"{CL(c0)}{row}")
            row += math.ceil(img.height / ROW_PX) + 1
        else:
            put(ws, row + 6, 52, "[SCREEN IMAGE HERE]", F_BODY, "center")
            row += 14
        for n in notes:
            for ln in wrap(n, width_px):
                put(ws, row, c0, ln, F_BODY)
                row += 1
        row += 1
    if row > PAGE_BOTTOM:
        book.extend_frame(ws, row)
    else:
        book.long_print(ws, PAGE_BOTTOM)


def render_data_map(book, dm):
    src = book.src["Data Map"]
    blocks = (dm or {}).get("blocks") or []
    state = {}

    def page():
        if state.get("ws") is not None:      # same sheet: grow by one page-sized block
            old = book.frame_bottom.get(state["ws"].title, PAGE_BOTTOM)
            book.extend_frame(state["ws"], old + 41, title_rows="1:7")
            state["ws"].row_breaks.append(Break(id=old))
            state["row"], state["bottom"] = old + 1, old + 40
            return
        ws = book.new_page("Data Map", clear_from=BODY_TOP)
        book.clone_rows(src, 7, 7, ws, 7)
        add_dv(ws, "Insert,Update,Delete", "BT8:BX47")
        book.long_print(ws, PAGE_BOTTOM, "1:7")
        state["ws"], state["row"], state["bottom"] = ws, 8, 47

    page()
    if not blocks:
        put(state["ws"], 9, 3, (dm or {}).get("note") or
            f"Not applicable - this {BLOCK_NAME[book.kind].lower()} does not insert/update data.",
            F_BODY)
        return
    for blk in blocks:
        source = blk.get("source", "Key-in from screen")
        if book.kind == "batch" and not isinstance(source, dict):
            source = {"table": source}          # batch sources are always a DB/File
        is_tbl = isinstance(source, dict)
        if book.kind == "batch":
            h1, h2, drow = 8, 10, 11
        else:
            h1, h2, drow = (22, 24, 25) if is_tbl else (8, 10, 11)
        dest = blk.get("destination", {})

        def header():
            ws, r = state["ws"], state["row"]
            book.clone_rows(src, h1, h2, ws, r)
            if is_tbl:
                put(ws, r, CI("K"), source.get("table", "TBD"), F_BODY, shrink=True)
            else:
                put(ws, r, CI("B"), source, F_BOLD, shrink=True)
            put(ws, r, CI("AX"), dest.get("table", "TBD"), F_BODY, shrink=True)
            put(ws, r, CI("BT"), dest.get("operation", "TBD"), F_BODY, "center", shrink=True)
            put(ws, r, CI("CF"), dest.get("description", ""), F_BODY, shrink=True)
            state["row"] += h2 - h1 + 1

        # build physical rows
        maps = blk.get("mappings") or []
        span = lambda a, b: book.span_px(CI(a), CI(b))
        phys = []
        sn = dn = 0
        for m in maps:
            sf = m.get("source_field")
            sl = wrap(sf, span("T", "AD") if is_tbl else span("D", "AD")) if sf else []
            dl = wrap(m.get("dest_field", "TBD"), span("AO", "AY"))
            el = wrap(m.get("description", ""), span("AZ", "CF"))
            n = max(len(sl), len(dl), len(el), 1)
            if sf:
                sn += 1
            dn += 1
            for i in range(n):
                phys.append(dict(sno=sn if (i == 0 and sf) else None, sf=sl[i] if i < len(sl) else None,
                                 dno=dn if i == 0 else None, df=dl[i] if i < len(dl) else None,
                                 desc=el[i] if i < len(el) else None, rel=(i == 0 and bool(sf))))
        def key_lines(keys, fa, fb, va, vb):
            out = []
            for k in keys or []:
                fl = wrap(k.get("field", ""), span(fa, fb))
                vl = wrap(k.get("value", ""), span(va, vb))
                for i in range(max(len(fl), len(vl), 1)):
                    out.append((fl[i] if i < len(fl) else None, vl[i] if i < len(vl) else None))
            return out

        if blk.get("source_fields"):
            # source listed independently of destination rows (staging -> base style); no arrows
            for p in phys:
                p.update(sno=None, sf=None, rel=False)
            sl_all = []
            for i, f_ in enumerate(blk["source_fields"], 1):
                for j, ln in enumerate(wrap(f_, span("T", "AD") if is_tbl else span("D", "AD"))):
                    sl_all.append((i if j == 0 else None, ln))
            while len(phys) < len(sl_all):
                phys.append({})
            for i, (no, ln) in enumerate(sl_all):
                phys[i]["sno"], phys[i]["sf"] = no, ln
        dkeys = key_lines(dest.get("keys"), "CG", "CQ", "CR", "CX")
        skeys = key_lines(source.get("keys") if is_tbl else [], "B", "J", "K", "Q")
        while len(phys) < max(len(dkeys), len(skeys), 1):
            phys.append({})
        for i, (kf, kv) in enumerate(dkeys):
            phys[i]["dk"], phys[i]["dv"] = kf, kv
        for i, (kf, kv) in enumerate(skeys):
            phys[i]["sk"], phys[i]["sv"] = kf, kv

        if state["row"] != 8:
            state["row"] += 1
        need = (h2 - h1 + 1) + len(phys)
        if state["row"] + (h2 - h1 + 1) > state["bottom"] or (
                state["row"] + need - 1 > state["bottom"] and need <= 40 and state["row"] > state["bottom"] - 39):
            page()
        header()
        for p in phys:
            if state["row"] > state["bottom"]:
                page()
                header()
            ws, r = state["ws"], state["row"]
            book.clone_rows(src, drow, drow, ws, r, with_values=False)
            if is_tbl:
                put(ws, r, CI("R"), p.get("sno"), F_BODY, "center")
                put(ws, r, CI("T"), p.get("sf"))
                put(ws, r, CI("B"), p.get("sk"))
                put(ws, r, CI("K"), p.get("sv"))
            else:
                put(ws, r, CI("B"), p.get("sno"), F_BODY, "center")
                put(ws, r, CI("D"), p.get("sf"))
            if p.get("rel"):
                ws.merge_cells(start_row=r, start_column=CI("AE"), end_row=r, end_column=CI("AL"))
                put(ws, r, CI("AE"), "\u2192", F_BODY, "center")
            put(ws, r, CI("AM"), p.get("dno"), F_BODY, "center")
            put(ws, r, CI("AO"), p.get("df"))
            put(ws, r, CI("AZ"), p.get("desc"))
            put(ws, r, CI("CG"), p.get("dk"))
            put(ws, r, CI("CR"), p.get("dv"))
            state["row"] += 1


def render_layout(book, lay):
    lay = lay or {}
    attrs = lay.get("attributes") or [{}]
    ws = book.new_page("Layout", clear_from=11)
    src = book.src["Layout"]
    for i, a in enumerate(attrs):
        r = 10 + i
        if i:
            book.clone_rows(src, 10, 10, ws, r, with_values=False)
        for c in range(COL_FIRST, COL_LAST + 1):
            cell = ws.cell(r, c)
            if not isinstance(cell, MergedCell):
                cell.value = None
            if i < len(attrs) - 1:
                set_border(cell, bottom=THIN)
        nmax = 1
        for key, col in LAYOUT_COLS.items():
            c = CI(col)
            end = c
            for m in src.merged_cells.ranges:
                if m.min_row == 10 and m.min_col == c:
                    end = m.max_col
            v = tbd(a.get(key))
            ls, sk = layout_text(v, book.span_px(c, end))
            nmax = max(nmax, len(ls))
            put(ws, r, c, "\n".join(str(x) for x in ls) if len(ls) > 1 else v, F_BODY, "center",
                wrap_text=len(ls) > 1, shrink=sk)
        ws.row_dimensions[r].height = ROW_H * nmax
    last = 10 + len(attrs) - 1
    for key, items in LAYOUT_DV.items():
        c = CI(LAYOUT_COLS[key])
        add_dv(ws, items, f"{CL(c)}10:{CL(c)}{last}")
    f = Flow(book, "Layout", layout="full", ws=ws, start_row=last + 2)
    figs = lay.get("figures") or []
    if not figs:
        f.placeholder("[REPORT LAYOUT IMAGE HERE]")
    for k, fig in enumerate(figs):
        cap = fig.get("caption") or f"Figure {k + 1}"
        if fig.get("image"):
            f.image(fig["image"], cap, level=1, fresh_page=k > 0 and fig.get("fresh_page", False))
        else:
            f.placeholder("[REPORT LAYOUT IMAGE HERE]", cap)
        for n in fig.get("notes", []):
            f.text(n, level=1)


TABLE_KINDS = {"transaction": "Transaction table", "temp": "Temporary table", "history": "History table",
               "log": "Log table", "master": "Master table", "staging": "Staging table", "parking": "Parking table"}


def _table_columns(t):
    cols = []
    for c in t.get("columns", []):
        if isinstance(c, dict):
            cols.append([c.get("name", ""), c.get("type", "TBD"), c.get("pk", ""), c.get("null", ""), c.get("description", "")])
        else:
            cols.append((list(c) + ["", "", "", "", ""])[:5])
    return cols


def table_definition_blocks(tables):
    """Appendix blocks for spec["tables"]: one definition table per table the batch writes."""
    if not tables:
        return []
    out = [{"type": "heading", "text": "Table definitions" + (" (proposed)" if any(t.get("proposed") for t in tables) else "")}]
    if any(t.get("proposed") for t in tables):
        out.append({"type": "text", "level": 1, "italic": True,
                    "text": "Names/lengths marked proposed or TBD must be aligned with the project naming convention and master tables before development."})
    for t in tables:
        kind = TABLE_KINDS.get(str(t.get("kind", "")).lower(), t.get("kind", ""))
        out += [{"type": "heading", "text": t["name"] + (" (proposed)" if t.get("proposed") else ""), "level": 1},
                {"type": "text", "level": 2, "text": " - ".join(x for x in (kind, t.get("description", "")) if x)},
                {"type": "table", "level": 2,
                 "columns": [{"title": "Column", "width": 16}, {"title": "Type", "width": 12},
                             {"title": "PK", "width": 3, "align": "center"}, {"title": "Null", "width": 4, "align": "center"},
                             {"title": "Description", "width": 58}],
                 "rows": _table_columns(t)}]
    return out


def data_map_coverage(spec):
    """Columns of defined tables missing from Data Map blocks: every Insert block must list all columns of
    its destination; Update/Delete blocks on transaction tables must list all columns too ("Not changed")."""
    tables = {t["name"]: t for t in spec.get("tables") or [] if t.get("name")}
    gaps = {}
    for i, blk in enumerate((spec.get("data_map") or {}).get("blocks") or [], 1):
        dest = blk.get("destination") or {}
        t = tables.get(dest.get("table"))
        if not t:
            continue
        op = str(dest.get("operation", "")).lower()
        if op != "insert" and str(t.get("kind", "")).lower() != "transaction":
            continue
        mapped = {str(m.get("dest_field", "")).strip() for m in blk.get("mappings") or []}
        missing = [c[0] for c in _table_columns(t) if c[0] not in mapped]
        if missing:
            gaps[f"block {i}: {dest.get('table')} ({dest.get('operation')})"] = missing
    return gaps


def render_operation(book, blocks, layout, base="Operation Desc"):
    f = Flow(book, base, layout=layout)
    if not blocks:
        f.text("TBD", level=1)
        return
    f.blocks(blocks)


# --------------------------------------------------------------------------- main
def build(spec, out_path):
    kind = spec.get("doc_type", "screen").lower()
    if kind not in SHEETS:
        raise SystemExit("doc_type must be 'screen', 'report' or 'batch'")
    header = dict(spec.get("header") or {})
    header.setdefault("created_date", dt.date.today().strftime("%d-%b-%y"))
    book = Book(kind, header)
    omit = set(spec.get("omit_sheets") or [])
    for base in SHEETS[kind]:
        if base in omit:
            continue
        if base == "Revision":
            render_revision(book, spec)
        elif base == "Gen Desc":
            {"screen": render_gen_desc_screen, "report": render_gen_desc_report,
             "batch": render_gen_desc_batch}[kind](book, spec.get("general") or {})
        elif base == "Func Flow":
            render_func_flow(book, spec.get("func_flow"))
        elif base == "Func Desc":
            render_operation(book, spec.get("func_desc") or [], spec.get("func_desc_layout", "two"), base="Func Desc")
        elif base == "Appendix":
            blocks = list(spec.get("appendix") or []) + table_definition_blocks(spec.get("tables") or [])
            if blocks:
                render_operation(book, blocks, spec.get("appendix_layout", "full"), base="Appendix")
        elif base == "Screen Flow":
            render_screen_flow(book, spec.get("screen_flow") or [])
        elif base == "Screen Layout":
            render_screen_layout(book, spec.get("screen_layout") or [])
        elif base == "Layout":
            render_layout(book, spec.get("layout"))
        elif base == "Item Desc":
            GridTable(book, base, GRID[(kind, base)]).render(spec.get("items") or [])
        elif base == "Data Map":
            render_data_map(book, spec.get("data_map"))
        elif base == "Operation Desc":
            render_operation(book, spec.get("operation") or [], spec.get("operation_layout", "two"))
        elif base == "Display Message":
            GridTable(book, base, GRID[(kind, base)]).render(spec.get("display_messages") or [])
        elif base == "Logging Message":
            GridTable(book, base, GRID[(kind, base)]).render(spec.get("logging_messages") or [])
    book.finalize(out_path)
    res = book.summary()
    gaps = data_map_coverage(spec)
    if gaps:
        res["data_map_missing_columns"] = gaps
    res["output"] = out_path
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path to the JSON spec")
    ap.add_argument("-o", "--out", required=True, help="output .xlsx path")
    a = ap.parse_args()
    with open(a.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    print(json.dumps(build(spec, a.out), indent=2))


if __name__ == "__main__":
    main()
