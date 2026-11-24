"""Yellow highlight of the changes in a UISS workbook against an older version: logic, business rules and new tables, not renames.
- Text sheets: the words of every column are read top to bottom, so wrapped paragraphs read as one text. A word is unchanged when it
  stands next to the same word (before or after) anywhere in the old sheet, so text that only moved is not marked. A cell gets a yellow
  fill when it holds a new or changed word. Numbering and layout labels (No., a., 5.24, DB/File Name) are not compared. Before the compare, names that only changed
  label are made equal (Kanban Crossdock Master = Part List, Export Crossdock Master = Mapping per Destination, Non Sync = No Sync, the
  export file names), so a rename alone is not marked.
- Sample sheets (Export / Upload ...): only the header cells of new columns are marked; the sample rows are example data.
- Group titles that the UISS template fills yellow turn light grey in this copy, so yellow means "changed" only.
- Sheets with pictures or shapes (Screen Layout, Screen Flow) are not compared. Sheets are put back at XML level (add_sheets_xlsx.py),
  so images stay.
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
# the UISS template fills group titles with the same yellow: in the review copy they turn light grey, so yellow means "changed" only
HEADER_ROWS = 4  # document header block (phase, project, dates, page) is not content
TEMPLATE_GREY = PatternFill('solid', fgColor='E7E6E6')
# sheet of the new workbook -> sheet of the old workbook
SHEET_ALIAS = {'Export Kanban Crossdock Master': 'Export Part List', 'Upload Kanban Crossdock Master': 'Upload Part List'}
SAMPLE = re.compile(r'^(Export|Upload) ')
# label renames: word sequences made equal before the compare (new -> old wording)
RENAMES = [
    (['kanban', 'crossdock', 'master'], ['part', 'list']),
    (['export', 'crossdock', 'master'], ['mapping', 'per', 'destination']),
    (['non', 'sync'], ['no', 'sync']),
]
# numbering and layout labels are not content (No., a., 5.24, DB/File Name)
STRUCT = re.compile(r'^([a-z]|no|db/file|\d+(\.\d+)*)$')
WORD_RENAMES = [(re.compile(r'crossdock_kanban_master'), 'crossdock_part_list'), (re.compile(r'crossdock_export_master'), 'crossdock_mapping_per_destination')]


def key(word):
    w = word.lower().strip('.,;:()[]<>\'"')
    for rx, to in WORD_RENAMES:
        w = rx.sub(to, w)
    return w


def tokens(ws):
    """Words per column, top to bottom: {col: [(key, (row, col)), ...]}, with the renames applied."""
    cols = {}
    for r in ws.iter_rows():
        for c in r:
            if c.value is None:
                continue
            for w in str(c.value).split():
                seq = cols.setdefault(c.column, [])
                # an identifier wrapped after '_' (Crossdock_Kanban_ / Master_YYYYMMDD.xlsx) is read as one word
                if seq and seq[-1][2].endswith('_'):
                    k0, cell0, raw0 = seq.pop()
                    w = raw0 + w
                    k = key(w)
                    seq.append((k, cell0, w))
                    continue
                k = key(w)
                if k:
                    seq.append((k, (c.row, c.column), w))
    for col in cols:
        cols[col] = [(k, cell) for k, cell, _ in cols[col]]
    for col, seq in cols.items():
        out, i = [], 0
        while i < len(seq):
            for new, old in RENAMES:
                if [k for k, _ in seq[i:i + len(new)]] == new:
                    out += [(o, seq[i][1]) for o in old]
                    i += len(new)
                    break
            else:
                out.append(seq[i])
                i += 1
        cols[col] = out
    return cols


old_wb = openpyxl.load_workbook(OLD)
new_wb = openpyxl.load_workbook(NEW)
total = {}
for ws in new_wb.worksheets:
    if ws.title in SKIP:
        continue
    old_name = SHEET_ALIAS.get(ws.title, ws.title)
    old_ws = old_wb[old_name] if old_name in old_wb.sheetnames else None
    marked = set()
    for r in ws.iter_rows():
        for c in r:
            if c.fill is not None and c.fill.fill_type == 'solid' and str(c.fill.fgColor.rgb).upper().endswith('FFFF00'):
                c.fill = TEMPLATE_GREY
    if SAMPLE.match(ws.title):
        # example data: only new columns count (header row = first row with 3+ values after the note)
        def header(sheet):
            for r in sheet.iter_rows(min_row=3, max_row=8):
                vals = [c for c in r if c.value is not None]
                if len(vals) >= 3:
                    return vals
            return []
        old_heads = {' '.join(key(w) for w in str(c.value).split()) for c in header(old_ws)} if old_ws is not None else set()
        for c in header(ws):
            h = ' '.join(key(w) for w in str(c.value).split())
            for new, old in RENAMES:
                h = h.replace(' '.join(new), ' '.join(old))
            if h not in old_heads:
                marked.add((c.row, c.column))
    else:
        new_cols = tokens(ws)
        old_cols = tokens(old_ws) if old_ws is not None else {}
        # a word is unchanged when one of its word pairs (with the word before or after) is anywhere in the old sheet,
        # so a paragraph that moved to another column or row is not marked
        old_pairs, old_words = set(), set()
        for seq in old_cols.values():
            ks = [k for k, _ in seq]
            old_words.update(ks)
            old_pairs.update(zip(ks, ks[1:]))
        for col, seq in new_cols.items():
            ks = [k for k, _ in seq]
            for i, (k, cell) in enumerate(seq):
                if not re.search(r'[a-z]', k) or STRUCT.match(k) or k.startswith('=if('):
                    continue
                prev_ok = i > 0 and (ks[i - 1], k) in old_pairs
                next_ok = i + 1 < len(ks) and (k, ks[i + 1]) in old_pairs
                alone_ok = len(ks) == 1 and k in old_words
                if not (prev_ok or next_ok or alone_ok):
                    marked.add(cell)
    if not SAMPLE.match(ws.title):
        marked = {(r, c) for r, c in marked if r > HEADER_ROWS}
    for row, col in marked:
        ws.cell(row, col).fill = YELLOW
    total[ws.title] = len(marked)
for name in [s for s in new_wb.sheetnames if s in SKIP]:
    del new_wb[name]
tmp = tempfile.mkdtemp()
new_wb.save(f'{tmp}/hl.xlsx')
subprocess.run([sys.executable, 'deliverables/uiss_specs/add_sheets_xlsx.py', NEW, f'{tmp}/hl.xlsx', OUT], check=True, stdout=subprocess.DEVNULL)
print('highlighted cells per sheet:', total)
print('saved', OUT)
