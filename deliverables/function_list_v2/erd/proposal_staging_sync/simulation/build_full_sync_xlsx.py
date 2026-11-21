"""Full sync flow simulation -> Excel: one sheet per step of Full_Sync_Flow.html (same tables, notes and colours).
Run: python3 build_full_sync_xlsx.py"""
import html
import os
import re
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'Full_Sync_Flow.html')
OUT = os.path.join(HERE, 'Full_Sync_Flow_Simulation.xlsx')
FILL = {'r-pend': 'FFF1D6', 'r-ok': 'E1F2E5', 'r-ng': 'FBE3DF', 'r-par': 'EEE8F7', 'r-sup': 'F2F2F2'}
HDR, SIM = PatternFill('solid', fgColor='DCEBFA'), PatternFill('solid', fgColor='FFF1C2')
thin = Side(style='thin', color='B7C9DB')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def text(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x))).strip()


def val(s):
    return int(s) if re.fullmatch(r'-?\d+', s) and not (len(s) > 1 and s.startswith('0')) and len(s) < 9 else s


page = open(SRC, encoding='utf-8').read()
NAVL = dict(re.findall(r'<a href="#([^"]+)">(.*?)</a>', page))
steps = re.findall(r'<section class="step" id="([^"]+)">(.*?)</section>', page, re.S)
wb = Workbook()
wb.remove(wb.active)
ov = wb.create_sheet('Steps')
ov['A1'] = 'Full sync flow with the staging table (TB_H_PART_CANDIDATE_STG_SYNC) – simulation, dummy parts'
ov['A1'].font = Font(name='Arial', size=12, bold=True)
ov.append([])
ov.append(['Sheet', 'When · who', 'Step'])
for c in ov[3]:
    c.font, c.fill, c.border = Font(name='Arial', size=9, bold=True), HDR, BOX
for sid, body in steps:
    no = text(re.search(r'<span class="no">(.*?)</span>', body).group(1))
    when = text(re.search(r'<div class="when">(.*?)</div>', body).group(1))
    title = text(re.search(r'<h2>(.*?)</h2>', body).group(1))
    name = text(NAVL.get(sid, f'{no} {title}'))[:31].replace('/', '-').replace(':', '').replace('[', '').replace(']', '')
    ov.append([name, when, title])
    for c in ov[ov.max_row]:
        c.font, c.border = Font(name='Arial', size=9), BOX
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws['A1'] = f'{no}. {title}'
    ws['A1'].font = Font(name='Arial', size=12, bold=True)
    ws['A2'] = when
    ws['A2'].font = Font(name='Arial', size=9, italic=True, color='4F6580')
    r = 4
    widths = {}
    sbody = body[body.index('<div class="step-body">'):]
    for m in re.finditer(r'<h3>(.*?)</h3>|<p class="(note|warn)">(.*?)</p>|<table>(.*?)</table>', sbody, re.S):
        if m.group(1) is not None:
            ws.cell(r, 1, text(m.group(1))).font = Font(name='Arial', size=10, bold=True, color='123A6B')
            r += 1
        elif m.group(2):
            c = ws.cell(r, 1, text(m.group(3)))
            c.font = Font(name='Arial', size=9, italic=m.group(2) == 'note', color='B23B2E' if m.group(2) == 'warn' else '4F6580')
            r += 1
        else:
            t = m.group(4)
            heads = re.findall(r'<th( class="th-sim")?>(.*?)</th>', t, re.S)
            for j, (sim, h) in enumerate(heads, 1):
                c = ws.cell(r, j, text(h))
                c.font, c.fill, c.border = Font(name='Arial', size=9, bold=True), SIM if sim else HDR, BOX
                c.alignment = Alignment(wrap_text=True, vertical='center')
                widths[j] = max(widths.get(j, 8), min(40, len(text(h)) + 2))
            r += 1
            for cls, row in re.findall(r'<tr class="([^"]*)">(.*?)</tr>', t, re.S):
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
                for j, x in enumerate(cells, 1):
                    v = text(x)
                    c = ws.cell(r, j, val(v))
                    c.font, c.border = Font(name='Arial', size=9), BOX
                    if cls.strip() in FILL:
                        c.fill = PatternFill('solid', fgColor=FILL[cls.strip()])
                    if cls.strip() == 'r-sup':
                        c.font = Font(name='Arial', size=9, color='7F8C99', strike=True)
                    widths[j] = max(widths.get(j, 8), min(40, len(v) + 2))
                r += 1
            r += 1
    for j, w in widths.items():
        ws.column_dimensions[get_column_letter(j)].width = w
for col, w in zip('ABC', (34, 34, 90)):
    ov.column_dimensions[col].width = w
legend = ['', 'Colours: yellow = inserted / changed / Non Sync, green = Sync / Keep / OK, red = delete / 0, purple = parent (Kanban), grey struck = Superseded; '
              'yellow header = helper column of the simulation (worked out at [Sync], not stored).']
for x in legend:
    ov.append([x])
wb.save(OUT)
print('saved', OUT, len(steps), 'steps')
