"""Column mapping from the staging tables to the AP POLE upload files (LLM9Q910 Kanban, LLM9Q880 Export) and to the GTOPAS screen
WVJA5204, for the RPA developer. Source columns: build_table_proposal_v2.py; views: prepare_code/sql/crossdock_staging_sync.sql;
template columns: the AP POLE template LM9Q870 (user_guide/ap_pole_img/b05) and the Kanban upload columns of the AP POLE guide;
examples: the SQL Studio data (simulation/sql_studio/studio_data.json).
Output: Column_Mapping_Staging_To_Upload.xlsx (this folder) and prepare_code/rpa/Column_Mapping_Staging_To_Upload.md.
Run: python3 build_column_mapping.py"""
import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(HERE, 'Column_Mapping_Staging_To_Upload.xlsx')
MD = os.path.join(ROOT, 'prepare_code', 'rpa', 'Column_Mapping_Staging_To_Upload.md')
DATA = json.load(open(os.path.join(HERE, 'simulation', 'sql_studio', 'studio_data.json')))
DEST = {'JAPAN': '9722D10', 'KOREA': '9715310', 'TAIWAN': '9811110', 'USA': '9600110', 'THAILAND': '9655510'}
bpd = lambda d: DEST[d][:5] + '-' + DEST[d][5:]

# examples of the run 2026-12-10 11:00:00 (and 2026-12-08 for a DELETE)
k = next(r for r in DATA['K'] if r['run'] == '20261210110000' and r['op'] != 5 and r['p'] == 'DUMMY-004')
e = next(r for r in DATA['E'] if r['run'] == '20261210110000' and r['p'] == 'DUMMY-004' and r['d'] == 'KOREA')
ed = next(r for r in DATA['E'] if r['run'] == '20261208110000' and r['cd'] == 0)
ga = next(r for r in DATA['G'] if r['run'] == '20261210110000' and r['act'] == 'ADD')
gd = next(r for r in DATA['G'] if r['act'] == 'DELETE')
EX_RUN = '2026-12-10 11:00:00'

# ---------- Kanban: TB_H_STG_APPOLE_KANBAN -> V_APPOLE_UPLOAD_KANBAN -> LLM9Q910 ----------
HEAD = ['Col', 'File column (template)', 'Staging column', 'View column', 'Rule for the robot', f'Example (run {EX_RUN})', 'Remark']
TPL_EMPTY = ['Packing/Pallet Type', 'Recv Area Code', 'Location No', 'Recv Contain Box Code', 'Store', 'Inner 1-PKG Part No.', 'Inner 1-Location',
             'Inner 1-Qty', 'Inner 2-PKG Part No.', 'Inner 2-Location', 'Inner 2-Qty', 'Inner 3-PKG Part No.', 'Inner 3-Location', 'Inner 3-Qty',
             'Inner M-PKG Part No.', 'Inner M-Location', 'Inner M-Qty', 'Outer-PKG Part No.', 'Outer-Location', 'Outer-Qty']
KAN = [
    ['A', 'Effective Month', 'PERIOD', 'EFFECTIVE_MONTH_YEAR (MM/YYYY)', 'The robot splits EFFECTIVE_MONTH_YEAR: the part before "/" (decided 26-Nov)', int(k['per'][4:]), 'Number in the template sample (11)'],
    ['B', 'Effective Year', 'PERIOD', 'EFFECTIVE_MONTH_YEAR (MM/YYYY)', 'The robot splits EFFECTIVE_MONTH_YEAR: the part after "/"', int(k['per'][:4]), ''],
    ['C', 'Operator ID', 'OPERATOR_ID', 'OPERATOR_ID', "As is (always 'P6')", 'P6', 'Fixed value'],
    ['D', 'Part No.', 'PART_NO', 'PART_NO', 'As is, with "-" (NSP format, UISS XD07; kept for now, 26-Nov)', k['p'], 'The template sample has no "-" (52101BZA40): to check with AP POLE'],
    ['E', 'Part Name', 'PART_NAME', 'PART_NAME', 'As is', 'DUMMY PART ' + k['p'][-3:], 'Copied from TB_M_PART_CANDIDATE at the insert'],
    ['F', 'Shipping Box Qty', 'SHIPPING_BOX_QTY', 'SHIPPING_BOX_QTY', 'As is (Pcs/Case)', k['pcs'], ''],
    ['G', 'Max Shipping Box Qty', 'MAX_SHIPPING_BOX_QTY', 'MAX_SHIPPING_BOX_QTY', 'As is (Max Case/Day)', k['max'], ''],
    ['H', 'Max Allowance Qty', '-', '-', 'Leave empty (decided 26-Nov: not filled, AP POLE calculates it)', '', 'MAX_ALLOWANCE_QTY of the staging is not written'],
    ['I to AB', ', '.join(TPL_EMPTY), '-', '-', 'Leave empty', '', 'Not in NSP scope; the template sample has one space in these cells'],
]
KAN_HELP = [
    ['STG_ID', 'Order of the rows; not written'],
    ['PERIOD', 'Same month as EFFECTIVE_MONTH_YEAR; ORDER BY PERIOD, PART_NO'],
    ['MAX_ALLOWANCE_QTY', 'In the view but not written (Max Allowance Qty is left empty, 26-Nov)'],
    ['OPERATION_TYPE', 'The view returns 1 to 4 only (5 = header, not uploaded); decides the file of the Export rows of the part'],
    ['FILE_NO', 'Always 2 (file KANBAN, uploaded after EXPORT_PRE and before EXPORT_POST)'],
    ['SYNC_DT', "Filter of the run: WHERE SYNC_DT = :sync_dt (the view keeps SYNC_STATUS = '1' only)"],
    ['ACTION, PART_STATUS, SOURCE, UPLOAD_ID, SYNC_STATUS, CREATED_* / CHANGED_*', 'Table only, not in the view; not written'],
]

# ---------- Export: TB_H_STG_APPOLE_EXPORT -> V_APPOLE_UPLOAD_EXPORT -> LLM9Q880 ----------
EXP = [
    ['A', 'Effective Month', 'PERIOD', 'EFFECTIVE_MONTH_YEAR (MM/YYYY)', 'The robot splits EFFECTIVE_MONTH_YEAR: the part before "/" (decided 26-Nov)', e['per'][4:], 'The LM9Q870 sample shows 01'],
    ['B', 'Effective Year', 'PERIOD', 'EFFECTIVE_MONTH_YEAR (MM/YYYY)', 'The robot splits EFFECTIVE_MONTH_YEAR: the part after "/"', e['per'][:4], ''],
    ['C', 'Part No.', 'PART_NO', 'PART_NO', 'As is, without "-" (stored without "-")', e['p'].replace('-', ''), 'NSP_PART_NO (with "-") is the helper key'],
    ['D', 'Shipping Box Qty', '-', '-', 'Leave empty', '', 'Grey column of the template'],
    ['E', 'Max Shipping Box by Part No.', '-', '-', 'Leave empty', '', 'Grey column of the template'],
    ['F', 'Buyer-PD', 'BUYER_PD', 'BUYER_PD', 'As is (DEST_CODE as 5-2)', bpd(e['d']), f"DEST_CODE {DEST[e['d']]}"],
    ['G', 'Order Type', 'ORDER_TYPE', 'ORDER_TYPE', "As is ('**', 'C', '9', 'V')", e['ot'], 'Part of the AP POLE key: a change = DELETE (0) of the old + ADD of the new'],
    ['H', 'Transport Code', 'TRANSPORT_CODE', 'TRANSPORT_CODE', "As is (always '2')", '2', 'Fixed value'],
    ['I', 'Max Shipping Box (RCS)', 'MAX_SHIPPING_BOX_RCS', 'MAX_SHIPPING_BOX_RCS', 'As is (Case/Day of the destination); 0 = delete the destination', e['cd'], f"DELETE example (run 2026-12-08 11:00:00): {ed['p'].replace('-', '')} {bpd(ed['d'])} {ed['ot']} = 0"],
    ['J', 'Max Allowance Qty', '-', '-', 'Leave empty', '', 'Grey column of the template'],
    ['K', 'Packing/Pallet Type', '-', '-', 'Leave empty', '', 'Not in NSP scope'],
]
EXP_HELP = [
    ['STG_ID', 'Last sort key; not written'],
    ['PERIOD, NSP_PART_NO', 'Sort keys (ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID); not written'],
    ['FILE_NO / FILE_NAME', '1 EXPORT_PRE (header OPERATION_TYPE 1, before KANBAN) or 3 EXPORT_POST (2, 3, 4, 5, after KANBAN): one query per file'],
    ['ROW_ORDER', '1 = down or DELETE (0), 2 = up or ADD, against the value sent before; rows with 1 first inside each part'],
    ['SYNC_DT', 'Filter of the run: WHERE SYNC_DT = :sync_dt'],
    ['DEST_CODE, ACTION, SOURCE, UPLOAD_ID, SYNC_STATUS, CREATED_* / CHANGED_*', 'Table only, not in the view; not written'],
]

# ---------- GTOPAS: TB_H_STG_GTOPAS -> V_GTOPAS_CROSSDOCK -> screen WVJA5204 ----------
GHEAD = ['Screen field (WVJA5204)', 'Column (staging = view)', 'ACTION = ADD (register a row)', 'ACTION = DELETE (MT = DEL)', f'Example ADD (run {EX_RUN})', 'Example DELETE (run 2026-12-08 11:00:00)']
GTO = [
    ['Search: Depot Code (*)', 'DEPOT_CODE', "Search with '01'", "Search with '01'", '01', '01'],
    ['Search: P/No.', 'P_NO', 'Search, to check the row is not there yet', 'Search the row to delete', ga['p'], gd['p']],
    ['Search: Destination Code', 'DESTINATION_CODE', 'Search', 'Search', DEST[ga['d']], DEST[gd['d']]],
    ['MT', '(from ACTION)', 'New row (register)', "'DEL' on the row found", '(new row)', 'DEL'],
    ['Depot Code', 'DEPOT_CODE', "'01'", '-', '01', ''],
    ['Maker Code', 'MAKER_CODE', "'A'", '-', 'A', ''],
    ['P/No.', 'P_NO', 'As is, with "-"', '-', ga['p'], ''],
    ['Domestic/Overseas', 'DOMESTIC_OVERSEAS', "'2'", '-', '2', ''],
    ['Destination Code', 'DESTINATION_CODE', 'As is, 7 digits (same code in NSP and GTOPAS)', '-', DEST[ga['d']], ''],
    ['TOPAS Order Type', 'TOPAS_ORDER_TYPE', "'3'", '-', '3', ''],
    ['Order Transportation Code', 'ORDER_TRANSPORTATION_CODE', "'2'", '-', '2', ''],
    ['Result message', '-', 'MZD34006FEI = done; row already there = OK', 'MZD34006FEI = done; row not found = OK (already gone)', '', ''],
]
G_HELP = [
    ['STG_ID, PERIOD', 'Not on the screen; ORDER BY P_NO, DESTINATION_CODE'],
    ['ACTION', 'ADD = register the row, DELETE = MT DEL on the row'],
    ['SYNC_DT', 'Filter of the run: WHERE SYNC_DT = :sync_dt (the view keeps SYNC_STATUS 1 only)'],
    ['SOURCE, UPLOAD_ID, SYNC_STATUS, CREATED_* / CHANGED_*', 'Table only, not in the view'],
]

FILES = [
    ['1', 'EXPORT_PRE', 'LLM9Q880', 'LLM9Q880_<yyyymmddhhmmss of SYNC_DT>_1_EXPORT_PRE.xls', 'V_APPOLE_UPLOAD_EXPORT WHERE SYNC_DT = :sync_dt AND FILE_NO = 1 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID', 'Export rows of parts whose Max goes down (OPERATION_TYPE 1)'],
    ['2', 'KANBAN', 'LLM9Q910', 'LLM9Q910_<yyyymmddhhmmss>_2_KANBAN.xls', 'V_APPOLE_UPLOAD_KANBAN WHERE SYNC_DT = :sync_dt ORDER BY PERIOD, PART_NO', 'Kanban rows with OPERATION_TYPE 1 to 4'],
    ['3', 'EXPORT_POST', 'LLM9Q880', 'LLM9Q880_<yyyymmddhhmmss>_3_EXPORT_POST.xls', 'V_APPOLE_UPLOAD_EXPORT WHERE SYNC_DT = :sync_dt AND FILE_NO = 3 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID', 'Every other Export row (OPERATION_TYPE 2 to 5)'],
    ['-', 'GTOPAS (XD06)', 'Screen WVJA5204', '-', 'V_GTOPAS_CROSSDOCK WHERE SYNC_DT = :sync_dt ORDER BY P_NO, DESTINATION_CODE', 'Run before XD07 when the run has GTOPAS rows (scenario 1)'],
]
NOTES = [
    'Decided 26-Nov: Effective Month and Effective Year are two columns in both templates; the views keep EFFECTIVE_MONTH_YEAR (MM/YYYY) and the robot splits it.',
    'Decided 26-Nov: Kanban Max Allowance Qty is not filled (AP POLE calculates it). The template sample has 120 with Shipping Box Qty 6 and Max 24 (6 x 24 = 144), so it is not the simple product.',
    'Decided 26-Nov: Kanban Part No. keeps "-" as in the UISS for now. To check: the template sample has 52101BZA40 (no "-"), like the Export file.',
    'Template LLM9Q910 (received 26-Nov): Sheet1, row 1 title "Cross Dock Kanban Part Master Report", row 3 header (28 columns A to AB), data from row 4. Columns I to AB are empty; the sample has one space in them: blank or space, TBC with AP POLE.',
    'Template LLM9Q880 (picture of LM9Q870): row 1 title "Export Customer Cross Dock Master Report", header row 3, data from row 4; grey columns are empty.',
    'A file without rows is not made. Upload order 1 EXPORT_PRE, 2 KANBAN, 3 EXPORT_POST; an upload error stops the run.',
    'Header rows (Kanban OPERATION_TYPE 5) are not in any file: the view V_APPOLE_UPLOAD_KANBAN leaves them out.',
    'Example values are dummy data of the SQL Studio (Master > Staging Sync SQL in the web prototype).',
]

# ---------- workbook ----------
fill = lambda c: PatternFill('solid', fgColor=c)
HDR, HELP, TITLE = fill('D9E1F2'), fill('FFF2CC'), Font(name='Calibri', size=14, bold=True, color='1F3864')
thin = Side(style='thin', color='A6A6A6')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
wb = Workbook()
wb.remove(wb.active)


def sheet(name, title, sub):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws['A1'] = title
    ws['A1'].font = TITLE
    ws['A2'] = sub
    ws['A2'].font = Font(name='Calibri', size=10, italic=True, color='595959')
    return ws, 4


def table(ws, r, head, rows, widths=None, head_fill=HDR):
    for c, h in enumerate(head, 1):
        x = ws.cell(r, c, h)
        x.font, x.fill, x.border = Font(name='Calibri', size=11, bold=True), head_fill, BOX
        x.alignment = Alignment(wrap_text=True, vertical='center')
    for i, row in enumerate(rows, r + 1):
        for c, v in enumerate(row, 1):
            x = ws.cell(i, c, v)
            x.font, x.border = Font(name='Calibri', size=11), BOX
            x.alignment = Alignment(wrap_text=True, vertical='top')
    if widths:
        for c, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(c)].width = max(ws.column_dimensions[get_column_letter(c)].width or 0, w)
    return r + len(rows) + 2


def label(ws, r, text):
    ws.cell(r, 1, text).font = Font(name='Calibri', size=12, bold=True, color='1F3864')
    return r + 1


W = [7, 26, 24, 30, 52, 22, 48]
ws, r = sheet('1 Kanban LLM9Q910', 'TB_H_STG_APPOLE_KANBAN → V_APPOLE_UPLOAD_KANBAN → file LLM9Q910 (Cross Dock Kanban Part Master)',
              'File 2 KANBAN, Report Type LM9Q900 on AP POLE Common File Upload. Template LLM9Q910: row 3 header, one row per view row from row 4.')
r = table(ws, r, HEAD, KAN, W)
r = label(ws, r, 'Columns used by the robot but not written to the file')
table(ws, r, ['Column', 'Use'], KAN_HELP, head_fill=HELP)

ws, r = sheet('2 Export LLM9Q880', 'TB_H_STG_APPOLE_EXPORT → V_APPOLE_UPLOAD_EXPORT → file LLM9Q880 (Export Customer Cross Dock Master)',
              'Files 1 EXPORT_PRE and 3 EXPORT_POST, Report Type LM9Q870 on AP POLE Common File Upload. Template LLM9Q880: row 3 header, data from row 4.')
r = table(ws, r, HEAD, EXP, W)
r = label(ws, r, 'Columns used by the robot but not written to the file')
table(ws, r, ['Column', 'Use'], EXP_HELP, head_fill=HELP)

ws, r = sheet('3 GTOPAS WVJA5204', 'TB_H_STG_GTOPAS → V_GTOPAS_CROSSDOCK → GTOPAS screen Crossdock Master (WVJA5204)',
              'XD06: one screen action per row, Menu Supply > Master > Crossdock Master. No file: the robot works on the screen.')
r = table(ws, r, GHEAD, GTO, [28, 28, 40, 40, 24, 28])
r = label(ws, r, 'Columns used by the robot but not typed on the screen')
table(ws, r, ['Column', 'Use'], G_HELP, head_fill=HELP)

ws, r = sheet('4 Files and order', 'Files, queries and upload order of one run (one SYNC_DT)',
              'XD06 GTOPAS first when the run has GTOPAS rows (scenario 1), then XD07 files 1 → 2 → 3.')
table(ws, r, ['Order', 'File', 'Template / screen', 'File name', 'Query of the robot (read-only DB user)', 'Rows'], FILES, [7, 16, 18, 46, 70, 44])

ws, r = sheet('5 Notes TBC', 'Notes and points to confirm', '')
table(ws, r, ['No', 'Note'], [[i + 1, n] for i, n in enumerate(NOTES)], [6, 120])

for w in wb.worksheets:
    w.freeze_panes = 'A5'
    w.page_setup.orientation = 'landscape'
    w.sheet_properties.pageSetUpPr.fitToPage = True
    w.page_setup.fitToWidth, w.page_setup.fitToHeight = 1, 0
wb.save(OUT)
print('saved', os.path.relpath(OUT, ROOT))

# ---------- Markdown copy ----------
cell = lambda v: str(v).replace('|', '\\|').replace('*', '\\*')
mdt = lambda head, rows: '\n'.join(['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows]) + '\n'
L = ['# Column mapping: staging tables to the AP POLE files and the GTOPAS screen', '',
     '_Generated by deliverables/function_list_v2/erd/proposal_staging_sync/build_column_mapping.py (same content as Column_Mapping_Staging_To_Upload.xlsx); do not edit by hand._', '',
     '## 1. Kanban: TB_H_STG_APPOLE_KANBAN → V_APPOLE_UPLOAD_KANBAN → LLM9Q910 (file 2 KANBAN)', '', mdt(HEAD, KAN),
     'Not written to the file:', '', mdt(['Column', 'Use'], KAN_HELP),
     '## 2. Export: TB_H_STG_APPOLE_EXPORT → V_APPOLE_UPLOAD_EXPORT → LLM9Q880 (files 1 EXPORT_PRE, 3 EXPORT_POST)', '', mdt(HEAD, EXP),
     'Not written to the file:', '', mdt(['Column', 'Use'], EXP_HELP),
     '## 3. GTOPAS: TB_H_STG_GTOPAS → V_GTOPAS_CROSSDOCK → screen WVJA5204', '', mdt(GHEAD, GTO), 'Not typed on the screen:', '', mdt(['Column', 'Use'], G_HELP),
     '## 4. Files and order of one run', '', mdt(['Order', 'File', 'Template / screen', 'File name', 'Query of the robot', 'Rows'], FILES),
     '## 5. Notes and points to confirm', ''] + [f'{i + 1}. {n}' for i, n in enumerate(NOTES)] + ['']
open(MD, 'w', encoding='utf-8').write('\n'.join(L))
print('saved', os.path.relpath(MD, ROOT))
