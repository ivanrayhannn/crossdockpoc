"""One-sheet UISS change: Delivery Note and Case Label (PDF downloaded from ASN Inquiry) get the DOCK code.
Before = PDFs given by the user (DN 0003121J26002, case labels of the same DN); after = pictures given by the user (26-Nov-2026),
the new item framed in yellow. Pictures in dock_img/. Run: python3 build_dock_change.py"""
import os

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'dock_img')
OUT = os.path.join(HERE, 'UISS_ASN_Inquiry_DN_CaseLabel_Dock.xlsx')
W = 360  # picture width in px
YELLOW, HDR = PatternFill('solid', fgColor='FFFF00'), PatternFill('solid', fgColor='D9E1F2')
thin = Side(style='thin', color='808080')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F, FB = Font(name='Calibri', size=11), Font(name='Calibri', size=11, bold=True)

ROWS = [
    ('Delivery Note', 'PDF, A4 portrait, one per DN', 'before_delivery_note.png', 'after_delivery_note.png',
     'New item DOCK : <dock code>, right side under the signature box PT. TMMIN / SUPPLIER.\n'
     'Dock code in large bold text inside a red frame (example S2).\n'
     'Value: dock code from the System Master.\n'
     'Other items unchanged: barcode DN No, DN No, DN Date, Delivery Date, Supp Code, Supp Name, Customer, '
     'detail Case No / Sub Manifest No / Order Type / Item / QTY.'),
    ('Case Label', 'PDF, A4 landscape, 4 labels per page (one label shown)', 'before_case_label.png', 'after_case_label.png',
     'New item DOCK with the dock code under the X mark, dock code in large bold text inside a red frame (example S2).\n'
     'Value: the same dock code as the Delivery Note, from the System Master.\n'
     'Other items unchanged: TMMIN - SP EXPORT, barcode Case No, Case No, X, Printed Date & Time.'),
]
NOTE = ('Note: the DOCK code (e.g. S2) is stored in the System Master. The Delivery Note and the Case Label read it from there; '
        'both PDFs are downloaded from the ASN Inquiry screen.')

wb = Workbook()
ws = wb.active
ws.title = 'Before After'
ws.sheet_view.showGridLines = False
ws['A1'] = 'UISS change: Delivery Note and Case Label, add DOCK code'
ws['A1'].font = Font(name='Calibri', size=14, bold=True, color='1F3864')
ws['A2'] = 'Screen: ASN Inquiry, download Delivery Note (PDF) and Case Label (PDF). Date 26-Nov-2026, by FID Rayhan. Yellow = change.'
ws['A2'].font = Font(name='Calibri', size=10, italic=True, color='595959')
for c, h in enumerate(['No', 'Report', 'Before', 'After', 'Change'], 1):
    x = ws.cell(4, c, h)
    x.font, x.fill, x.border = FB, HDR, BOX
    x.alignment = Alignment(horizontal='center', vertical='center')
for i, (name, fmt, before, after, change) in enumerate(ROWS, 1):
    r = 4 + i
    ws.cell(r, 1, i)
    ws.cell(r, 2, f'{name}\n({fmt})')
    ws.cell(r, 5, change).fill = YELLOW
    height = 0
    for col, pic in (('C', before), ('D', after)):
        p = os.path.join(IMG, pic)
        w, h = Image.open(p).size
        img = XLImage(p)
        img.width, img.height = W, int(h * W / w)
        img.anchor = f'{col}{r}'
        ws.add_image(img)
        height = max(height, img.height)
    ws.row_dimensions[r].height = height * 0.75 + 12
    for c in range(1, 6):
        x = ws.cell(r, c)
        x.border = BOX
        x.font = F
        x.alignment = Alignment(wrap_text=True, vertical='top')
ws.cell(7, 1, NOTE).font = Font(name='Calibri', size=11, bold=True, color='C00000')
ws.merge_cells('A7:E7')
for col, w in zip('ABCDE', (5, 22, 52, 52, 48)):
    ws.column_dimensions[col].width = w
ws.page_setup.orientation = 'landscape'
ws.page_setup.paperSize = 9
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 1
wb.save(OUT)
print('saved', OUT)
