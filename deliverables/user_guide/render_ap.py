"""Renders parts of the exported NSP files (dl_ap/) as Excel-like images (shots_ap/x_*.png) for the AP POLE user guide.
Yellow rows = the example part; header cells in orange = the columns the RPA reads. Run: python3 render_ap.py"""
import glob, os, subprocess, tempfile
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
part = sorted(glob.glob(os.path.join(HERE, 'dl_ap', 'Crossdock_Kanban_Master_*.xlsx')))[-1]
mapping = sorted(glob.glob(os.path.join(HERE, 'dl_ap', 'Crossdock_Export_Master_*.xlsx')))[-1]
YEL, HDR, KEY = PatternFill('solid', fgColor='FFF2CC'), PatternFill('solid', fgColor='D9E1F2'), PatternFill('solid', fgColor='F8CBAD')
P_COLS = ['Part Number', 'Part Name', 'Pcs/Case', 'Max Case/Day', 'Status', 'Sync Status']
M_COLS = ['Part Number', 'Destination Code', 'Pcs/Case', 'Dest Case/Day', 'Total Case/Day (used)', 'Max Case/Day (quota)', 'Sync Status', 'Last Sent Date']
I_COLS = None
# name, file, sheet, keep row?, highlight row?, columns (None = all), key columns
def _run(src, sheet):
    """Send time of the run = latest Last Sent Date of the file (the parts of the [Sync] of the guide)."""
    rows = list(openpyxl.load_workbook(src)[sheet].iter_rows(values_only=True))
    i = rows[0].index('Last Sent Date')
    stamp = lambda v: datetime.strptime(v, '%d-%b-%Y %H:%M')
    return max((r[i] for r in rows[1:] if r[i]), key=stamp, default=None)


RUN_P, RUN_M = _run(part, 'Kanban Crossdock Master'), _run(mapping, 'Export Crossdock Master')
JOBS = [
    ('x_part_waiting', part, 'Kanban Crossdock Master', lambda r: r['Sync Status'] == 'Sent' and r['Last Sent Date'] == RUN_P, lambda r: r['Part Number'] in ('PART-009', 'PART-F', 'PART-023'), None,
     ['Part Number', 'Pcs/Case', 'Max Case/Day', 'Status', 'Sync Status']),
    ('x_map_waiting', mapping, 'Export Crossdock Master', lambda r: r['Last Sent Date'] == RUN_M, lambda r: r['Part Number'] in ('PART-009', 'PART-F', 'PART-B'), None,
     ['Part Number', 'Destination Code', 'Dest Case/Day', 'Max Case/Day (quota)', 'Sync Status', 'Last Sent Date']),
    ('x_ex1_part', part, 'Kanban Crossdock Master', lambda r: r['Part Number'] == 'PART-009', lambda r: True, P_COLS, ['Pcs/Case', 'Max Case/Day']),
    ('x_ex1_map', mapping, 'Export Crossdock Master', lambda r: r['Part Number'] == 'PART-009', lambda r: True, M_COLS, ['Destination Code', 'Dest Case/Day', 'Last Sent Date']),
    ('x_ex2_part', part, 'Kanban Crossdock Master', lambda r: r['Part Number'] == 'PART-F', lambda r: True, P_COLS, ['Pcs/Case', 'Max Case/Day']),
    ('x_ex2_map', mapping, 'Export Crossdock Master', lambda r: r['Part Number'] == 'PART-F', lambda r: True, M_COLS, ['Destination Code', 'Dest Case/Day', 'Last Sent Date']),
    ('x_ex3_part', part, 'Kanban Crossdock Master', lambda r: r['Part Number'] == 'PART-023', lambda r: True, P_COLS, ['Status', 'Sync Status']),
    ('x_ex4_map', mapping, 'Export Crossdock Master', lambda r: r['Part Number'] == 'PART-B', lambda r: True, M_COLS, ['Destination Code', 'Dest Case/Day']),
]
tmp = tempfile.mkdtemp()
for name, src, sheet, keep, hl, cols, keys in JOBS:
    ws0 = openpyxl.load_workbook(src)[sheet]
    rows = list(ws0.iter_rows(values_only=True))
    head = list(rows[0])
    widths = {head[i]: ws0.column_dimensions[get_column_letter(i + 1)].width or 12 for i in range(len(head))}
    cols = cols or head
    data = [dict(zip(head, r)) for r in rows[1:]]
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = sheet
    for c, h in enumerate(cols, 1):
        x = ws.cell(1, c, h); x.font = Font(name='Calibri', size=11, bold=True); x.fill = KEY if h in keys else HDR
        ws.column_dimensions[get_column_letter(c)].width = max(widths.get(h, 12), len(h) + 2)
    r = 2
    for d in data:
        if not keep(d):
            continue
        for c, h in enumerate(cols, 1):
            x = ws.cell(r, c, d.get(h)); x.font = Font(name='Calibri', size=11)
            if hl(d) and not name.startswith('x_ex'):
                x.fill = YEL
        r += 1
    ws.print_options.gridLines = True; ws.print_options.headings = True
    ws.page_setup.orientation = 'landscape'; ws.page_setup.paperSize = 8
    ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1
    for side in ('left', 'right', 'top', 'bottom'): setattr(ws.page_margins, side, 0.2)
    p = os.path.join(tmp, name + '.xlsx'); wb.save(p)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmp, p], capture_output=True)
    subprocess.run(['pdftoppm', '-r', '110', '-png', '-singlefile', os.path.join(tmp, name + '.pdf'), os.path.join(tmp, name)])
    im = Image.open(os.path.join(tmp, name + '.png')).convert('RGB')
    bbox = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()
    im = im.crop((max(0, bbox[0] - 8), max(0, bbox[1] - 8), min(im.width, bbox[2] + 8), min(im.height, bbox[3] + 8)))
    im.save(os.path.join(HERE, 'shots_ap', name + '.png')); print(name, im.size)
