"""Proposal 23-Nov (staging per target, replaces TB_H_PART_CANDIDATE_STG_SYNC of 22-Nov; discussion, not yet in the UISS / DB Structure).
Tables: TB_M_PART_CANDIDATE, TB_M_PART_CANDIDATE_DEST, TB_H_STG_APPOLE_KANBAN, TB_H_STG_APPOLE_EXPORT, TB_H_STG_GTOPAS.
Existing columns are read from the specs (erd/build_erd.load_tables). Rules: simulation/Staging_Header_Order.html.
Run: python3 build_table_proposal_v2.py"""
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from build_erd import load_tables  # noqa: E402

OUT = os.path.join(HERE, 'Proposal_Tables_Staging_Per_Target.xlsx')
T = load_tables()[0]
HDR = PatternFill('solid', fgColor='DCEBFA')
HELP = PatternFill('solid', fgColor='FFF1C2')
FILL = {'New': PatternFill('solid', fgColor='E2EFDA'), 'Changed': PatternFill('solid', fgColor='FFF2CC'),
        'Removed': PatternFill('solid', fgColor='FCE4D6'), 'Existing': None}
thin = Side(style='thin', color='B7C9DB')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F, FB = Font(name='Arial', size=9), Font(name='Arial', size=9, bold=True)
COLS = ['No', 'Column', 'Type', 'PK', 'Null', 'Default', 'In upload file / screen', 'Description', 'Status']
WID = [5, 26, 14, 5, 6, 10, 22, 90, 10]
AUDIT = [
    ['SOURCE', 'VARCHAR(6)', '', 'N', '', '', 'SCREEN / UPLOAD / BATCH (XD05)', 'New'],
    ['UPLOAD_ID', 'VARCHAR(TBD)', '', 'Y', '', '', 'Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD', 'New'],
    ['SYNC_STATUS', 'CHAR(1)', '', 'N', "'0'", '', '0 = to send, 1 = sent, 2 = Superseded at the save (a newer row of the key, or back to the value already sent). Set by SP_STG_WRITE (0, 2) and SP_STG_SYNC / Period Rollover (1)', 'New'],
    ['SYNC_DT', 'DATETIME', '', 'Y', '', '', 'Time of the [Sync] / Period Rollover that sent the row; Last Sent on the screen = latest value', 'New'],
    ['SYNC_RUN_ID', 'VARCHAR(14)', '', 'Y', '', '', 'Run ID YYYYMMDDHHMMSS; [Re-send last Sync] sends the rows of the last run again', 'New'],
    ['CREATED_BY', 'VARCHAR(20)', '', 'N', '', '', 'User of the save / upload, or XD05BATCH', 'New'],
    ['CREATED_DT', 'DATETIME', '', 'N', '', '', 'Time of the insert (same transaction as the master update)', 'New'],
    ['CHANGED_BY', 'VARCHAR(20)', '', 'Y', '', '', 'User of the save that made the row Superseded, of [Sync], or XD05BATCH (Period Rollover)', 'New'],
    ['CHANGED_DT', 'DATETIME', '', 'Y', '', '', 'Time of that update', 'New'],
]


def existing(name):
    return [[c[0], c[1], 'Y' if c[2] == 'Y' else '', c[3], '', '', c[4], 'Existing'] for c in T[name][1]]


def kanban():
    moved = {'SYNC_STATUS': 'Removed: the Sync Status is SYNC_STATUS of the staging tables (AP POLE: Kanban and Export staging, GTOPAS: GTOPAS staging)',
             'GTOPAS_SYNC_DT': 'Removed: Last Sent GTOPAS = latest SYNC_DT of TB_H_STG_GTOPAS for the part',
             'APPOLE_SYNC_DT': 'Removed: Last Sent AP POLE = latest SYNC_DT of TB_H_STG_APPOLE_KANBAN / _EXPORT for the part',
             'SYNC_RUN_ID': 'Removed: SYNC_RUN_ID of the staging tables'}
    rows = []
    for r in existing('TB_M_PART_CANDIDATE'):
        n = r[0]
        if n in moved:
            rows.append(r[:6] + [moved[n], 'Removed'])
        elif n in ('PCS_CASE', 'MAX_CASE_DAY'):
            rows.append(r[:6] + [r[6] + '. A change of an Active part: SP_STG_WRITE (KANBAN) writes a row to TB_H_STG_APPOLE_KANBAN in the same transaction', 'Changed'])
        elif n == 'PART_STATUS':
            rows.append(r[:6] + ['Candidate / Active / Inactive. Candidate -> Active: Kanban ADD (OPERATION_TYPE 4). Active -> Inactive: Export DELETE (0) for every destination, '
                                 'Kanban header 5 (the part stays in AP POLE). Inactive -> Active: Procurement maps the destinations again', 'Changed'])
        else:
            rows.append(r)
    return rows


def dest():
    rows = existing('TB_M_PART_CANDIDATE_DEST')
    for r in rows:
        if r[0] == 'CASE_DAY':
            r[6] += ('. Every add / change / removal calls SP_STG_WRITE (EXPORT): a row in TB_H_STG_APPOLE_EXPORT, a row in TB_H_STG_GTOPAS when the destination '
                     'appears or disappears for the part, and the Kanban header (5) when the Kanban did not change')
            r[7] = 'Changed'
    return rows


KAN = [
    ['STG_ID', 'BIGINT', 'Y', 'N', 'identity', '', 'Running number: order of the inserts', 'New'],
    ['PERIOD', 'CHAR(6)', '', 'N', '', '', 'Calculation period YYYYMM. FK1 (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE', 'New'],
    ['ACTION', 'VARCHAR(6)', '', 'N', '', '', 'ADD (new part, new period) / EDIT (Pcs/Case or Max changed) / KEEP (header written by an Export save, Kanban unchanged)', 'New'],
    ['PART_STATUS', 'VARCHAR(10)', '', 'N', '', '', 'Active / Inactive in the period when the row is written (an Inactive part stays in the AP POLE Kanban)', 'New'],
    ['EFFECTIVE_MONTH_YEAR', 'CHAR(7)', '', 'N', '', 'Effective Month / Year', 'MM/YYYY of PERIOD', 'New'],
    ['OPERATOR_ID', 'CHAR(2)', '', 'N', "'P6'", 'Operator ID', 'Always P6', 'New'],
    ['PART_NO', 'VARCHAR(TBD)', '', 'N', '', 'Part No.', 'Part number with "-" (NSP format); FK1', 'New'],
    ['PART_NAME', 'VARCHAR(TBD)', '', 'N', '', 'Part Name', 'From TB_M_PART_CANDIDATE at the insert', 'New'],
    ['SHIPPING_BOX_QTY', 'NUMBER(5)', '', 'N', '', 'Shipping Box Qty', 'Pcs/Case', 'New'],
    ['MAX_SHIPPING_BOX_QTY', 'NUMBER(5)', '', 'N', '', 'Max Shipping Box Qty', 'Max Case/Day', 'New'],
    ['MAX_ALLOWANCE_QTY', 'NUMBER(9)', '', 'N', '', 'Max Allowance Qty', 'Shipping Box Qty x Max Shipping Box Qty', 'New'],
    ['OPERATION_TYPE', 'NUMBER(1)', '', 'N', '', '', 'Header of the part, set by SP_STG_WRITE at the save: 1 = Max down, 2 = Max up, 3 = Max same (only Pcs/Case changed, or a new period with the same Max), '
     '4 = never sent, 5 = Kanban unchanged, only the destinations changed (ACTION KEEP). 1 to 4 against the last Max sent: same period, else the latest earlier period. '
     'Upload: 1 -> the Export rows of the part in EXPORT_PRE before KANBAN; 2, 3, 4 -> KANBAN then EXPORT_POST; 5 -> EXPORT_POST only, the row is not in the KANBAN file', 'New'],
] + AUDIT

EXP = [
    ['STG_ID', 'BIGINT', 'Y', 'N', 'identity', '', 'Running number: order of the inserts', 'New'],
    ['PERIOD', 'CHAR(6)', '', 'N', '', '', 'Calculation period YYYYMM. FK1 (NSP_PART_NO, PERIOD) -> TB_M_PART_CANDIDATE', 'New'],
    ['NSP_PART_NO', 'VARCHAR(TBD)', '', 'N', '', '', 'Part number with "-" (key back to NSP); FK1', 'New'],
    ['DEST_CODE', 'CHAR(7)', '', 'N', '', '', 'Destination code, 7 digits. No FK: a DELETE row points to a removed destination', 'New'],
    ['ACTION', 'VARCHAR(6)', '', 'N', '', '', 'ADD / EDIT / DELETE (DELETE = Max Shipping Box (RCS) 0)', 'New'],
    ['EFFECTIVE_MONTH_YEAR', 'CHAR(7)', '', 'N', '', 'Effective Month / Year', 'MM/YYYY of PERIOD', 'New'],
    ['PART_NO', 'VARCHAR(TBD)', '', 'N', '', 'Part No.', 'Part number without "-"', 'New'],
    ['BUYER_PD', 'CHAR(8)', '', 'N', '', 'Buyer-PD', 'DEST_CODE in 5-2 format', 'New'],
    ['ORDER_TYPE', 'VARCHAR(2)', '', 'N', '', 'Order Type', "'**', 'C', '9', 'V' (system master)", 'New'],
    ['TRANSPORT_CODE', 'CHAR(1)', '', 'N', "'2'", 'Transport Code', 'Always 2', 'New'],
    ['MAX_SHIPPING_BOX_RCS', 'NUMBER(5)', '', 'N', '', 'Max Shipping Box (RCS)', 'Case/Day of the destination; 0 = delete', 'New'],
] + AUDIT

GTO = [
    ['STG_ID', 'BIGINT', 'Y', 'N', 'identity', '', 'Running number: order of the inserts', 'New'],
    ['PERIOD', 'CHAR(6)', '', 'N', '', '', 'Calculation period YYYYMM (GTOPAS has no period: [Sync] sends the Current period, the Period Rollover the new Current). FK1 (P_NO, PERIOD) -> TB_M_PART_CANDIDATE', 'New'],
    ['ACTION', 'VARCHAR(6)', '', 'N', '', 'Add / Delete (MT = DEL)', 'ADD / DELETE: the destination appears or disappears for the part (any order type). No row for a Case/Day change or for a state GTOPAS already has', 'New'],
    ['DEPOT_CODE', 'CHAR(2)', '', 'N', "'01'", 'Depot Code', 'Always 01', 'New'],
    ['P_NO', 'VARCHAR(TBD)', '', 'N', '', 'P/No.', 'Part number with "-"; FK1', 'New'],
    ['DESTINATION_CODE', 'CHAR(7)', '', 'N', '', 'Destination Code', '7-digit code, the same in NSP and GTOPAS', 'New'],
    ['MAKER_CODE', 'CHAR(1)', '', 'N', "'A'", 'Maker Code', 'Always A', 'New'],
    ['DOMESTIC_OVERSEAS', 'CHAR(1)', '', 'N', "'2'", 'Domestic/Overseas', 'Always 2', 'New'],
    ['TOPAS_ORDER_TYPE', 'CHAR(1)', '', 'N', "'3'", 'TOPAS Order Type', 'Always 3', 'New'],
    ['ORDER_TRANSPORTATION_CODE', 'CHAR(1)', '', 'N', "'2'", 'Order Transportation Code', 'Always 2', 'New'],
] + AUDIT


def sheet(wb, title, table, desc, rows, notes):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws['A1'] = table
    ws['A1'].font = Font(name='Arial', size=12, bold=True)
    ws['A2'] = desc
    ws['A2'].font = Font(name='Arial', size=9, italic=True)
    r0 = 4
    for c, h in enumerate(COLS, 1):
        x = ws.cell(r0, c, h)
        x.font, x.fill, x.border = FB, HDR, BOX
        x.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    new_table = all(r[7] == 'New' for r in rows)
    for i, row in enumerate(rows, 1):
        for c, v in enumerate([i] + row, 1):
            x = ws.cell(r0 + i, c, v)
            x.font, x.border = F, BOX
            x.alignment = Alignment(wrap_text=True, vertical='top')
            if new_table:
                if c == 2 and not row[5]:
                    x.fill = HELP   # helper column: not in the upload file / GTOPAS screen
            elif FILL[row[7]]:
                x.fill = FILL[row[7]]
            if row[7] == 'Removed' and c in (2, 3):
                x.font = Font(name='Arial', size=9, strike=True)
    for c, w in enumerate(WID, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    r = r0 + len(rows) + 2
    for n in notes:
        ws.cell(r, 1, n).font = F
        r += 1
    ws.freeze_panes = 'C5'


def summary(wb):
    ws = wb.create_sheet('0. Summary', 0)
    ws.sheet_view.showGridLines = False
    ws['A1'] = 'Staging per target: tables, procedures and views (proposal 23-Nov-2026)'
    ws['A1'].font = Font(name='Arial', size=12, bold=True)
    rows = [
        ['Object', 'Kind', 'Status', 'Purpose'],
        ['TB_M_PART_CANDIDATE', 'Table', 'Changed', 'Kanban Crossdock Master per part + period. Sync columns removed'],
        ['TB_M_PART_CANDIDATE_DEST', 'Table', 'Changed (description)', 'Export Crossdock Master per part + period + destination + order type'],
        ['TB_H_STG_APPOLE_KANBAN', 'Table', 'New', 'AP POLE Kanban rows in the LLM9Q910 format; header of the part (OPERATION_TYPE 1 to 5)'],
        ['TB_H_STG_APPOLE_EXPORT', 'Table', 'New', 'AP POLE Export rows in the LLM9Q880 format'],
        ['TB_H_STG_GTOPAS', 'Table', 'New', 'GTOPAS WVJA5204 rows (part + destination ADD / DELETE)'],
        ['TB_H_PART_CANDIDATE_STG_SYNC', 'Table', 'Removed (22-Nov proposal)', 'Replaced by the three tables above'],
        ['TB_H_PART_CANDIDATE', 'Table', 'Existing', 'Screen history, kept as it is'],
        ['SP_STG_WRITE', 'Stored procedure', 'New', 'Called by XD01 (screen), XD02 / XD03 (upload) and XD05 per changed value: insert, Superseded, OPERATION_TYPE, GTOPAS row'],
        ['SP_STG_HEADER', 'Stored procedure', 'New', 'Called by SP_STG_WRITE: Kanban header with OPERATION_TYPE 5 when only the destinations changed'],
        ['SP_STG_SYNC', 'Stored procedure', 'New', '[Sync]: 0 -> 1 with RUN_ID (AP POLE Current + Next, GTOPAS Current); LAST_SYNC_DATE_APPOLE'],
        ['V_APPOLE_UPLOAD_KANBAN', 'View', 'New', 'File KANBAN (order 2): Kanban rows of a run with OPERATION_TYPE 1 to 4'],
        ['V_APPOLE_UPLOAD_EXPORT', 'View', 'New', 'Files EXPORT_PRE (1) and EXPORT_POST (3) from the header OPERATION_TYPE; ROW_ORDER 1 down / 2 up'],
    ]
    for i, row in enumerate(rows, 3):
        for c, v in enumerate(row, 1):
            x = ws.cell(i, c, v)
            x.font, x.border = (FB if i == 3 else F), BOX
            if i == 3:
                x.fill = HDR
            x.alignment = Alignment(wrap_text=True, vertical='top')
    for c, w in enumerate([32, 18, 24, 100], 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    r = len(rows) + 4
    for n in ['Colours: green = new column, yellow fill on a new table = helper column (not in the upload file / GTOPAS screen), yellow row = changed description, red = removed (strike-through).',
              'Rules and simulation: simulation/Staging_Header_Order.html, simulation/Staging_Per_Target_Full_Flow.html, simulation/Staging_Per_Target_Full_Flow_Simulation.xlsx.',
              'Open points: table names; constants stored in every row (P6, 2, 01, A, 2 / 3 / 2); Active -> Inactive removes the mapping of the period (TB_M_PART_CANDIDATE_DEST).']:
        ws.cell(r, 1, n).font = F
        r += 1


def main():
    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, '1. TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE (Kanban Crossdock Master)', T['TB_M_PART_CANDIDATE'][0], kanban(), [
        'PK: PART_NO, PERIOD. No sync column left: Sync Status and Last Sent come from the staging tables.',
        'Green = new, yellow = changed description, red = removed (strike-through).'])
    sheet(wb, '2. TB_M_PART_CANDIDATE_DEST', 'TB_M_PART_CANDIDATE_DEST (Export Crossdock Master)', T['TB_M_PART_CANDIDATE_DEST'][0], dest(), [
        'PK: PART_NO, PERIOD, DEST_CODE, ORDER_TYPE. FK: (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE.',
        'No new column: a removed destination is deleted at once; the staging keeps the DELETE row until it is sent.'])
    sheet(wb, '3. TB_H_STG_APPOLE_KANBAN', 'TB_H_STG_APPOLE_KANBAN (new, AP POLE Kanban LLM9Q910)',
          'One row per Kanban change of a part + period in the format of the upload template, plus the header row (OPERATION_TYPE 5) when only the destinations changed. '
          'Insert by SP_STG_WRITE (XD01, XD02, XD05); SYNC_STATUS set by SP_STG_SYNC.', KAN, [
              'PK: STG_ID. FK1: (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE. Key of a change: PERIOD + PART_NO (one unsent row at a time).',
              'IX1: SYNC_STATUS, PERIOD, PART_NO (rows to send, header lookup at the save). IX2: SYNC_RUN_ID, PERIOD, PART_NO (files of a run, re-send).',
              'IX3: PART_NO, PERIOD, SYNC_STATUS, SYNC_DT (last sent Max for OPERATION_TYPE).',
              'Read by V_APPOLE_UPLOAD_KANBAN (OPERATION_TYPE 1 to 4) and by V_APPOLE_UPLOAD_EXPORT (file of the Export rows).'])
    sheet(wb, '4. TB_H_STG_APPOLE_EXPORT', 'TB_H_STG_APPOLE_EXPORT (new, AP POLE Export LLM9Q880)',
          'One row per added / changed / removed destination + order type of a part + period in the format of the upload template. '
          'Insert by SP_STG_WRITE (XD01, XD03, XD05); SYNC_STATUS set by SP_STG_SYNC.', EXP, [
              'PK: STG_ID. FK1: (NSP_PART_NO, PERIOD) -> TB_M_PART_CANDIDATE. Key of a change: PERIOD + NSP_PART_NO + DEST_CODE + ORDER_TYPE.',
              'IX1: SYNC_STATUS, PERIOD, NSP_PART_NO. IX2: SYNC_RUN_ID, PERIOD, NSP_PART_NO.',
              'IX3: NSP_PART_NO, DEST_CODE, ORDER_TYPE, PERIOD, SYNC_DT (last sent value: back-to-sent check at the save, ROW_ORDER in the view).',
              'No order column: the file comes from the Kanban header (OPERATION_TYPE), the order inside the file from the view (ROW_ORDER: down / DELETE before up / ADD).'])
    sheet(wb, '5. TB_H_STG_GTOPAS', 'TB_H_STG_GTOPAS (new, GTOPAS WVJA5204)',
          'One row when a destination appears (ADD) or disappears (DELETE) for a part, whatever the order type, and GTOPAS does not have that state yet. '
          'Insert by SP_STG_WRITE (EXPORT); sent by [Sync] (Current period) or the Period Rollover (new Current period).', GTO, [
              'PK: STG_ID. FK1: (P_NO, PERIOD) -> TB_M_PART_CANDIDATE. Key: PERIOD + P_NO + DESTINATION_CODE.',
              'IX1: SYNC_STATUS, PERIOD. IX2: P_NO, DESTINATION_CODE, PERIOD, SYNC_DT (last sent action).',
              'No MT column: the RPA deletes the row on WVJA5204 (MT = DEL) when ACTION = DELETE.'])
    summary(wb)
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
