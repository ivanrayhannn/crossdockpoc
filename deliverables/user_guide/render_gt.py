"""Images for the GTOPAS user guide (XD06), Excel-like: extracts of the exported NSP file (dl_gt/) and example lists of the GTOPAS screen
Crossdock Master (WVJA5204). The GTOPAS lists are illustrations (example data), not screenshots. Run: python3 render_gt.py"""
import glob, os, subprocess, tempfile
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'shots_gt')
mapping = sorted(glob.glob(os.path.join(HERE, 'dl_gt', 'Crossdock_Export_Master_*.xlsx')))[-1]
fill = lambda c: PatternFill('solid', fgColor=c)
HDR, KEY, YEL = fill('D9E1F2'), fill('F8CBAD'), fill('FFF2CC')
ACT = {'Keep': fill('E2EFDA'), 'Add': fill('DDEBF7'), 'Delete': fill('FADBD8')}
tmp = tempfile.mkdtemp()


def render(name, head, rows, keys=(), row_fill=None, widths=None):
    wb = openpyxl.Workbook(); ws = wb.active
    for c, h in enumerate(head, 1):
        x = ws.cell(1, c, h); x.font = Font(name='Calibri', size=11, bold=True); x.fill = KEY if h in keys else HDR
        ws.column_dimensions[get_column_letter(c)].width = (widths or {}).get(h, max(10, len(h) + 3))
    for r, row in enumerate(rows, 2):
        f = row_fill(row) if row_fill else None
        for c, v in enumerate(row, 1):
            x = ws.cell(r, c, v); x.font = Font(name='Calibri', size=11)
            if f:
                x.fill = f
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
    im.save(os.path.join(OUT, name + '.png')); print(name, im.size)


wb = openpyxl.load_workbook(mapping)
def sheet(n):
    rows = list(wb[n].iter_rows(values_only=True))
    return list(rows[0]), [dict(zip(rows[0], r)) for r in rows[1:]]
mh, mrows = sheet('Export Crossdock Master')
EX = ('PART-009', 'PART-012', 'PART-F', 'PART-B')
MC = ['Period', 'Part Number', 'Destination Code', 'Dest Case/Day', 'Sync Status', 'Last Sent GTOPAS']

# NSP list (whole sheet, examples in yellow) and the extracts per example
render('x_gt_nsp_all', MC, [[d[h] for h in MC] for d in mrows], ['Part Number', 'Destination Code'],
       lambda r: YEL if r[1] in EX else None, {'Last Sent GTOPAS': 18, 'Sync Status': 12})
for i, p in enumerate(EX, 1):
    render(f'x_gt_ex{i}_nsp', MC, [[d[h] for h in MC] for d in mrows if d['Part Number'] == p], ['Part Number', 'Destination Code'],
           widths={'Last Sent GTOPAS': 18})
# GTOPAS screen Crossdock Master (WVJA5204): list before the run (example data)
GH = ['No', 'MT', 'Depot Code', 'Maker Code', 'P/No.', 'Domestic/Overseas', 'Destination Code', 'TOPAS Order Type', 'Order Transportation Code']
g = lambda p, d: ['', '', '01', 'A', p, '2', d, '3', '2']
BEFORE = {'PART-012': ['9722D10'], 'PART-F': ['9715310', '9722D10', '9710110'], 'PART-023': ['9715310', '9722D10']}
before = [g(p, d) for p, ds in BEFORE.items() for d in ds]
for i, r in enumerate(before, 1):
    r[0] = i
render('x_gt_before', GH, before, ['P/No.', 'Destination Code'], widths={'P/No.': 12, 'Order Transportation Code': 26})
for i, p in ((2, 'PART-012'), (3, 'PART-F'), (5, 'PART-023')):
    rows = [r for r in before if r[4] == p]
    render(f'x_gt_ex{i}_gt', GH, rows, ['P/No.', 'Destination Code'], widths={'P/No.': 12, 'Order Transportation Code': 26})

# comparison of the examples
nsp = {(d['Part Number'], d['Destination Code']) for d in mrows if d['Part Number'] in EX + ('PART-023',) and d['Destination Code']}
gt = {(r[4], r[6]) for r in before}
order = ['PART-009', 'PART-012', 'PART-F', 'PART-B', 'PART-023']
CH = ['Part Number', 'Destination Code', 'In NSP', 'In GTOPAS', 'Action']
comp = []
for p in order:
    keys = sorted({k for k in nsp | gt if k[0] == p})
    if not keys:
        comp.append([p, '(none)', 'Y, no destination', 'N', 'Nothing'])
    for k in keys:
        a = 'Keep' if k in nsp and k in gt else 'Add' if k in nsp else 'Delete'
        comp.append([p, k[1], 'Y' if k in nsp else 'N (Inactive)' if p == 'PART-023' else 'N', 'Y' if k in gt else 'N', a])
render('x_gt_compare', CH, comp, ['Part Number', 'Destination Code', 'Action'], lambda r: ACT.get(r[4]), {'In NSP': 18, 'Action': 10})

# the same rows as the bot writes them in the work sheet GTOPAS Compare of the downloaded file
WH = ['P/No.', 'Destination Code', 'In NSP', 'In GTOPAS', 'Action', 'Result', 'GTOPAS message', 'Done date-time']
work, t = [], 0
for r in comp:
    if r[4] == 'Nothing':
        continue
    t += 1
    msg = '' if r[4] == 'Keep' else 'MZD34006FEI: Registration completed.'
    work.append([r[0], r[1], r[2][0], r[3], r[4], 'OK', msg, f'17-Nov-2026 08:{t:02d}'])
render('x_gt_work', WH, work, ['Action', 'Result'], lambda r: ACT.get(r[4]),
       {'GTOPAS message': 36, 'Done date-time': 18, 'Destination Code': 17})

# GTOPAS list after the run
after = [g(*k) for k in sorted(nsp)]
for i, r in enumerate(after, 1):
    r[0] = i
render('x_gt_after', GH, after, ['P/No.', 'Destination Code'], widths={'P/No.': 12, 'Order Transportation Code': 26})
