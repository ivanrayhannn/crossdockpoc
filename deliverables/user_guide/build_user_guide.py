"""User guide: download the Crossdock Part List and the Mapping per Destination to Excel (XD01), from the menu to the opened file.
Two sheets, one per download. Screenshots: guide_shots.mjs (prototype) + the real exported files rendered per sheet.
Run: python3 build_user_guide.py"""
import math
import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, 'shots2')
OUT = os.path.join(HERE, 'Crossdock_User_Guide_Download_Part_List_Mapping.xlsx')
IMG_W = 940          # px shown in the sheet
ROW_PX = 20          # default row height (15 pt)
thin = Side(style='thin', color='A6A6A6')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
HEAD = PatternFill('solid', fgColor='DDEBF7')
STEP = PatternFill('solid', fgColor='F2F2F2')
NOTE = PatternFill('solid', fgColor='FFF2CC')
F = lambda size=10, bold=False, italic=False, color='000000': Font(name='Arial', size=size, bold=bold, italic=italic, color=color)
WRAP = Alignment(wrap_text=True, vertical='top')

COMMON_OPEN = [
    ('Open the downloaded file',
     'In the browser, open the download list (Chrome / Edge: the download icon at the top right, or Ctrl + J) and click the file. '
     'Or open File Explorer > Downloads and double-click the file. The file opens in Microsoft Excel.', None),
    ('Enable editing (only when you will change the file)',
     'If Excel shows the yellow bar PROTECTED VIEW, the file is read-only. To change data for an upload, click [Enable Editing]. '
     'To only read the data, no action is needed.', None),
]

GUIDES = [
    {'sheet': '1. Download Part List',
     'title': 'Download Crossdock Part List to Excel',
     'meta': [('Function', 'XD01 Crossdock Master Setting, sub-menu Part List'), ('User', 'Procurement team'),
              ('Result', 'File Crossdock_Part_List_YYYYMMDD.xlsx (YYYYMMDD = download date), 2 sheets: Part List and Upload')],
     'steps': [
         ('Open the menu',
          'In the left menu click Master > Crossdock Master Setting. With the Procurement account the screen opens on the tab Part List.', 'p1_menu'),
         ('Set the search criteria and click [Search] (optional)',
          'Fill Part Number, Part Name, Status or Sort by when only some parts are needed, then click [Search]. '
          'Sheet "Part List" of the file follows this filter. Without a filter every registered part is downloaded.', 'p2_search'),
         ('Click [Export Excel]',
          'Click [Export Excel] at the top right. The browser downloads Crossdock_Part_List_YYYYMMDD.xlsx to the Downloads folder.', 'p3_export'),
     ] + COMMON_OPEN + [
         ('Read sheet "Part List"',
          'The parts of the active filter with Part Name, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, Status, Effective Start Date and the '
          'created / updated information. For information only: this sheet is not read by the upload.', 'x_part_list'),
         ('Use sheet "Upload" for a change (optional)',
          'Every registered part in the upload format, Upload (A/E) = E with the current values. Change the values, save the file and upload it with '
          '[Upload Excel] on the same screen. Do not rename the sheet or the column headers: the upload reads them by name.', 'x_part_upload'),
     ],
     'notes': ['[Export Excel] needs no input; the button is always active.',
               'Sheet "Upload" always holds every registered part, also when a filter is used for sheet "Part List".']},
    {'sheet': '2. Download Mapping',
     'title': 'Download Crossdock Mapping per Destination to Excel',
     'meta': [('Function', 'XD01 Crossdock Master Setting, sub-menu Mapping per Destination'), ('User', 'D/S team'),
              ('Result', 'File Crossdock_Mapping_per_Destination_<Period>_YYYYMMDD.xlsx, 2 sheets: Mapping per Destination and Upload')],
     'steps': [
         ('Open the menu',
          'In the left menu click Master > Crossdock Master Setting. With the D/S account the screen opens on the tab Mapping per Destination.', 'm1_menu'),
         ('Choose the Calculation period and click [Search]',
          'Choose the period, for example Sep 2026 (ongoing). Fill Part Number or Sync Status when needed, then click [Search]. '
          'Choose the ongoing period when the file is used for an upload: for a past period or All periods the sheet "Upload" is empty.', 'm2_period'),
         ('Click [Export Excel]',
          'Click [Export Excel] above the table. The browser downloads Crossdock_Mapping_per_Destination_<Period>_YYYYMMDD.xlsx, '
          'for example Crossdock_Mapping_per_Destination_Sep_2026_20261117.xlsx.', 'm3_export'),
     ] + COMMON_OPEN + [
         ('Read sheet "Mapping per Destination"',
          'One row per part and destination of the chosen period and filter: Destination Code, Dest Case/Day, Total Case/Day (used), '
          'Max Case/Day (quota), Pcs/Day, Sync Status and the created / updated information. A part without mapping has one row without destination. '
          'For information only.', 'x_map_list'),
         ('Use sheet "Upload" for a change (optional)',
          'Every Active part of the ongoing period, one row per destination: Upload (A/E) = E for a current mapping, A for a part without mapping. '
          'Fill Destination Code and Dest Case/Day, save and upload with [Upload Excel]. Total Case/Day (used) and Max Case/Day (quota) are for '
          'reference and are not read by the upload. Do not rename the sheet or the column headers.', 'x_map_upload'),
     ],
     'notes': ['The period in the file name is the period chosen in step 2 (All_periods when All periods is chosen).',
               'The total Dest Case/Day of a part may not be more than its Max Case/Day.']},
]


def build_sheet(wb, g):
    ws = wb.create_sheet(g['sheet'])
    ws.sheet_view.showGridLines = False
    for col, w in (('A', 2), ('B', 6), ('C', 34), ('D', 100)):
        ws.column_dimensions[col].width = w
    ws['B2'] = g['title']
    ws['B2'].font = F(14, True)
    r = 4
    for k, v in [('Project', 'Crossdock Optimization (NSP)'), ('Document', 'User Guide')] + g['meta']:
        ws.cell(r, 2, k).font = F(9, True)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        ws.cell(r, 4, v).font = F(9)
        for c in (2, 3, 4):
            ws.cell(r, c).border = BOX
            ws.cell(r, c).fill = HEAD if c < 4 else PatternFill()
        r += 1
    r += 1
    ws.cell(r, 2, 'Screenshots are taken from the prototype: the header "Supplier System" is NSP; "Preview ... / Switch sub-menu" exists only in the prototype. '
                  'Red box = the item to click. Steps 4 and 5 happen in the browser and Excel on your PC (no screenshot).').font = F(9, italic=True, color='595959')
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    ws.cell(r, 2).alignment = WRAP
    ws.row_dimensions[r].height = 26
    r += 2
    for c, h in ((2, 'Step'), (3, 'Action'), (4, 'Detail')):
        x = ws.cell(r, c, h)
        x.font, x.fill, x.border = F(10, True), HEAD, BOX
    r += 1
    for n, (action, detail, img) in enumerate(g['steps'], 1):
        for c, v in ((2, n), (3, action), (4, detail)):
            x = ws.cell(r, c, v)
            x.font, x.fill, x.border, x.alignment = F(10, c < 4), STEP, BOX, WRAP
        ws.cell(r, 2).alignment = Alignment(horizontal='center', vertical='top')
        ws.row_dimensions[r].height = max(28, 13 * math.ceil(len(detail) / 105) + 6)
        r += 1
        if img:
            path = os.path.join(SHOTS, img + '.png')
            w, h = Image.open(path).size
            scale = IMG_W / w if w > IMG_W else 1
            pic = XLImage(path)
            pic.width, pic.height = int(w * scale), int(h * scale)
            ws.add_image(pic, f'C{r}')
            r += math.ceil(pic.height / ROW_PX) + 2
        else:
            r += 1
    ws.cell(r, 2, 'Notes').font = F(10, True)
    r += 1
    for note in g['notes']:
        x = ws.cell(r, 2, '- ' + note)
        x.font, x.fill = F(9), NOTE
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        r += 1
    ws.page_setup.orientation = 'portrait'
    ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0


def main():
    wb = Workbook()
    wb.remove(wb.active)
    for g in GUIDES:
        build_sheet(wb, g)
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
