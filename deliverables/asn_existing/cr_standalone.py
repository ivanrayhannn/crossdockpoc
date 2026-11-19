"""Writes the CR Crossdock sheet as a document of its own (one sheet), same layout as the sheet added to the DR (add_cr_sheets.py)."""
import math
import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from add_cr_sheets import COLS, SHEET_NAME, STYLES, WIDTHS, lines

FONT = {'n': Font(name='Arial', size=10), 'b': Font(name='Arial', size=10, bold=True), 't': Font(name='Arial', size=14, bold=True),
        's': Font(name='Arial', size=11, bold=True), 'i': Font(name='Arial', size=9, italic=True, color='595959')}
FILL = {'none': None, 'head': PatternFill('solid', fgColor='DDEBF7'), 'meta': PatternFill('solid', fgColor='F2F2F2'),
        'new': PatternFill('solid', fgColor='FFF2CC')}
thin = Side(style='thin', color='999999')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def flow_sheet(wb, flows):
    """Sheet 'Business Flow': per (title, image, changes) the As-Is / To-Be picture and the list of changes."""
    ws = wb.create_sheet('Business Flow', 0)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 2
    ws.column_dimensions['B'].width = 6
    ws.column_dimensions['C'].width = 150
    r = 2
    for title, img, changes in flows:
        ws.cell(r, 2, title).font = FONT['s']
        r += 1
        w, h = Image.open(img).size
        k = min(1.0, 1150 / w)
        pic = XLImage(img)
        pic.width, pic.height = int(w * k), int(h * k)
        ws.add_image(pic, f'B{r}')
        r += math.ceil(pic.height / 20) + 1
        for n, c in enumerate(changes, 1):
            for col, v in ((2, n), (3, c)):
                x = ws.cell(r, col, v)
                x.font, x.border, x.alignment = FONT['n'], BOX, Alignment(vertical='top', wrap_text=True)
                x.fill = FILL['new']
            r += 1
        r += 2
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0


def write(path, rows, flows=None):
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME
    ws.sheet_view.showGridLines = False
    for c, w in WIDTHS.items():
        ws.column_dimensions[c].width = w
    widths = [WIDTHS[c] for c in COLS]
    span = sum(WIDTHS[c] for c in 'BCDEF')
    for r, row in enumerate(rows, 1):
        n = 1
        merged = len(row) == 1 and row[0] and row[0][0] in ('text', 'note')
        if merged:
            n = lines(row[0][1], span)
        elif row and any(cell and cell[0] not in ('title', 'sec') for cell in row):
            n = max(lines(cell[1], widths[c]) for c, cell in enumerate(row) if cell)
        for c, cell in enumerate(row):
            if cell is None:
                continue
            st, txt = cell
            font, fill, bordered = STYLES[st]
            x = ws[f'{COLS[c]}{r}']
            if txt != '':
                x.value = txt
            x.font = FONT[font]
            if FILL[fill]:
                x.fill = FILL[fill]
            if bordered:
                x.border = BOX
            x.alignment = Alignment(vertical='top', wrap_text=st not in ('title', 'sec'))
        if merged:
            ws.merge_cells(f'B{r}:F{r}')
        if n > 1:
            ws.row_dimensions[r].height = max(13.2, 12.6 * n + 2)
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    if flows:
        flow_sheet(wb, flows)
    wb.save(path)
    print('written', path)
