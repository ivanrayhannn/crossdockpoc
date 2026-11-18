"""Renders the first rows of each sheet of the exported files (downloads/) as images (shots2/x_*.png), Excel-like (grid + headings).
Run: python3 render_sheets.py"""
import glob, os, subprocess, sys, tempfile
import openpyxl
from openpyxl.styles import Font, PatternFill
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
part = sorted(glob.glob(os.path.join(HERE, 'downloads', 'Crossdock_Part_List_*.xlsx')))[-1]
mapping = sorted(glob.glob(os.path.join(HERE, 'downloads', 'Crossdock_Mapping_per_Destination_*.xlsx')))[-1]
JOBS = [(part, 'Part List', 'x_part_list'), (part, 'Upload', 'x_part_upload'), (mapping, 'Mapping per Destination', 'x_map_list'),
        (mapping, 'Upload', 'x_map_upload')]
tmp = tempfile.mkdtemp()
for src, sheet, name in JOBS:
    ws0 = openpyxl.load_workbook(src)[sheet]
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = sheet
    for r in ws0.iter_rows(min_row=1, max_row=16):
        for c in r:
            n = ws.cell(c.row, c.column, c.value); n.font = Font(name='Calibri', size=11, bold=(c.row == 1))
            if c.row == 1: n.fill = PatternFill('solid', fgColor='D9E1F2')
    for k, d in ws0.column_dimensions.items():
        if d.width: ws.column_dimensions[k].width = d.width
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
    im.save(os.path.join(HERE, 'shots2', name + '.png')); print(name, im.size)
