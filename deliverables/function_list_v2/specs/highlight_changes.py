"""Yellow highlight of the changes in a UISS workbook against an older version.
Every text sheet of NEW is compared with the sheet of the same name in OLD: a cell keeps its colour when its text is found in the
old sheet (read column by column, so a paragraph that only wrapped differently is not marked); otherwise it gets a yellow fill.
A row whose texts are all new is highlighted whole. Numbering cells such as '5.24' or '12' and short values are not compared alone. Sheets with pictures or shapes (Screen Layout, Screen Flow)
are not compared; they are copied as they are. The sheets are put back at XML level (add_sheets_xlsx.py), so images stay.
Usage: python3 highlight_changes.py OLD.xlsx NEW.xlsx OUT.xlsx"""
import re
import subprocess
import sys
import tempfile

import openpyxl
from openpyxl.styles import PatternFill

OLD, NEW, OUT = sys.argv[1:4]
SKIP = {'Screen Layout', 'Screen Flow'}
YELLOW = PatternFill('solid', fgColor='FFFF00')
NUMBERING = re.compile(r'^\(?\d+(\.\d+)*[.)]?$')


def norm(v):
    if v is None:
        return None
    t = re.sub(r'\s+', ' ', str(v)).strip()
    return t or None


def rows(ws):
    out = []
    for r in ws.iter_rows():
        cells = {c.column: norm(c.value) for c in r if norm(c.value) is not None}
        out.append((r[0].row if r else 0, cells))
    return out


old_wb = openpyxl.load_workbook(OLD)
new_wb = openpyxl.load_workbook(NEW)
total = {}
for ws in new_wb.worksheets:
    if ws.title in SKIP:
        continue
    old_ws = old_wb[ws.title] if ws.title in old_wb.sheetnames else None
    # old text per column, top to bottom: a wrapped paragraph reads as one string, so a re-wrapped line is still found in it
    old_text = ''
    if old_ws is not None:
        cols = {}
        for r in old_ws.iter_rows():
            for c in r:
                v = norm(c.value)
                if v is not None:
                    cols.setdefault(c.column, []).append(v)
        old_text = ' | '.join(' '.join(v) for v in cols.values())
    n = 0
    for rno, cells in rows(ws):
        key = {k: v for k, v in cells.items() if not NUMBERING.match(v)}
        if not key:
            continue
        long_ = {k: v for k, v in key.items() if len(v) > 3}
        changed = {k for k, v in long_.items() if v not in old_text}
        if long_ and len(changed) == len(long_):
            changed = set(key)  # new row: every cell
        for col in changed:
            ws.cell(rno, col).fill = YELLOW
            n += 1
    total[ws.title] = n
for name in [s for s in new_wb.sheetnames if s in SKIP]:
    del new_wb[name]
tmp = tempfile.mkdtemp()
new_wb.save(f'{tmp}/hl.xlsx')
subprocess.run([sys.executable, 'deliverables/uiss_specs/add_sheets_xlsx.py', NEW, f'{tmp}/hl.xlsx', OUT], check=True, stdout=subprocess.DEVNULL)
print('highlighted cells per sheet:', total)
print('saved', OUT)
