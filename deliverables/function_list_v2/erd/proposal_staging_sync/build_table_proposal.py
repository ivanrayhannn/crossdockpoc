"""Proposal (21-Nov, discussion, not yet in the UISS / DB Structure): TB_M_PART_CANDIDATE, TB_M_PART_CANDIDATE_DEST and the new
TB_H_PART_CANDIDATE_STG_SYNC for the AP POLE sync (XD07). Existing columns are read from the specs (erd/build_erd.load_tables).
Run: python3 build_table_proposal.py"""
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from build_erd import load_tables  # noqa: E402

OUT = os.path.join(HERE, 'Proposal_Tables_Staging_Sync.xlsx')
T = load_tables()[0]
HDR = PatternFill('solid', fgColor='DCEBFA')
FILL = {'New': PatternFill('solid', fgColor='E2EFDA'), 'Changed': PatternFill('solid', fgColor='FFF2CC'),
        'Removed': PatternFill('solid', fgColor='FCE4D6'), 'Existing': None}
thin = Side(style='thin', color='B7C9DB')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F, FB = Font(name='Arial', size=9), Font(name='Arial', size=9, bold=True)
COLS = ['No', 'Column', 'Type', 'PK', 'Null', 'Default', 'Description', 'Status']
WID = [5, 26, 16, 5, 6, 10, 95, 10]


def existing(name):
    return [[c[0], c[1], 'Y' if c[2] == 'Y' else '', c[3], '', c[4], 'Existing'] for c in T[name][1]]


def kanban():
    moved = {'SYNC_STATUS': 'Removed: one status for both targets; replaced by APPOLE_SYNC_STATUS and GTOPAS_SYNC_STATUS on TB_H_PART_CANDIDATE_STG_SYNC',
             'GTOPAS_SYNC_DT': 'Removed: moved to TB_H_PART_CANDIDATE_STG_SYNC.GTOPAS_SYNC_DT. Last Sent GTOPAS on the screen = latest GTOPAS_SYNC_DT of the staging rows',
             'APPOLE_SYNC_DT': 'Removed: moved to TB_H_PART_CANDIDATE_STG_SYNC.APPOLE_SYNC_DT. Last Sent AP POLE on the screen = latest APPOLE_SYNC_DT of the staging rows',
             'SYNC_RUN_ID': 'Removed: moved to TB_H_PART_CANDIDATE_STG_SYNC (APPOLE_SYNC_RUN_ID, GTOPAS_SYNC_RUN_ID)'}
    rows = []
    for r in existing('TB_M_PART_CANDIDATE'):
        n = r[0]
        if n in moved:
            rows.append(r[:5] + [moved[n], 'Removed'])
        elif n == 'PART_STATUS':
            rows.append(r[:5] + ['Candidate / Active / Inactive. Candidate -> Active: XD05 (Next period). Active -> Inactive and Inactive -> Active: '
                                 'Procurement on the Kanban Crossdock Master (writes DELETE / ADD CASE_DAY rows with this status to the staging)', 'Changed'])
        else:
            rows.append(r)
    return rows


def dest():
    rows = existing('TB_M_PART_CANDIDATE_DEST')
    for r in rows:
        if r[0] == 'CASE_DAY':
            r[5] += '. Every add / change / removal writes a row to TB_H_PART_CANDIDATE_STG_SYNC (LEVEL_TYPE EXPORT) in the same transaction'
            r[6] = 'Changed'
    return rows


STG = [
    ['HIST_ID', 'BIGINT', 'Y', 'N', 'identity', 'Running number: order of the changes', 'New'],
    ['PART_NO', 'VARCHAR(TBD)', '', 'N', '', 'Part number (NSP format, with "-"); FK1 (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE', 'New'],
    ['PERIOD', 'CHAR(6)', '', 'N', '', 'Calculation period YYYYMM; FK1. Effective Month / Year of the AP POLE upload', 'New'],
    ['PART_STATUS', 'VARCHAR(10)', '', 'N', '', 'Status of the part in this period when the row is written. Active: ADD / EDIT rows. Inactive: no Kanban row; every Export row of the part is DELETE with NEW_VALUE 0 (XD05 for a new Inactive part, Procurement for Active -> Inactive)', 'New'],
    ['LEVEL_TYPE', 'VARCHAR(6)', '', 'N', '', 'KANBAN = parent (Kanban Crossdock Master), EXPORT = child (Export Crossdock Master destination)', 'New'],
    ['DEST_CODE', 'CHAR(7)', '', 'Y', '', 'EXPORT only: destination code (buyer + PD, 7 digits); Buyer-PD 5-2 in the upload file. No FK: a DELETE row points to a removed destination', 'New'],
    ['ORDER_TYPE', 'VARCHAR(2)', '', 'Y', '', "EXPORT only: '**', 'C', '9', 'V'", 'New'],
    ['FIELD_NAME', 'VARCHAR(30)', '', 'N', '', 'KANBAN: PCS_CASE, MAX_CASE_DAY · EXPORT: CASE_DAY', 'New'],
    ['ACTION', 'VARCHAR(6)', '', 'N', '', 'ADD / EDIT / DELETE', 'New'],
    ['OLD_VALUE', 'VARCHAR(10)', '', 'Y', '', 'Value before the change; NULL on ADD', 'New'],
    ['NEW_VALUE', 'VARCHAR(10)', '', 'Y', '', 'Value after the change; 0 on DELETE (0 in the upload file)', 'New'],
    ['SOURCE', 'VARCHAR(6)', '', 'N', '', 'BATCH (XD05) / SCREEN / UPLOAD', 'New'],
    ['UPLOAD_ID', 'VARCHAR(TBD)', '', 'Y', '', 'Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD', 'New'],
    ['APPOLE_SYNC_STATUS', 'CHAR(1)', '', 'N', "'0'", '0 = Non Sync, 1 = Sync, 2 = Superseded (an earlier row of the same key; not sent). '
     'The part + period is AP POLE Non Sync while it has a row with 0', 'New'],
    ['APPOLE_SYNC_DT', 'DATETIME', '', 'Y', '', 'Time of the [Sync] that sent the row to AP POLE (status 1 and 2)', 'New'],
    ['SEND_SEQ', 'NUMBER(1)', '', 'Y', '', 'Upload file: 1 = Export (LLM9Q880) down / delete, 2 = Kanban (LLM9Q910), 3 = Export up / add. Set by NSP at [Sync] on the last '
     'row of each key; NULL for 2 Superseded and a key that ends on its first value', 'New'],
    ['APPOLE_SYNC_RUN_ID', 'VARCHAR(14)', '', 'Y', '', 'AP POLE run ID YYYYMMDDHHMMSS; [Re-send last Sync] takes the rows of the last run', 'New'],
    ['GTOPAS_SYNC_STATUS', 'CHAR(1)', '', 'Y', '', 'NULL = not for GTOPAS (Pcs/Case, Max Case/Day, Case/Day EDIT). 0 = Non Sync: an EXPORT row ADD or DELETE '
     '(the destination appears / disappears, also from a status change; every row of a new period from XD05). 1 = Sync: [Sync] for the Current period, the Period Rollover for the Next period. '
     'The part + period is GTOPAS Non Sync while it has a row with 0', 'New'],
    ['GTOPAS_SYNC_DT', 'DATETIME', '', 'Y', '', 'Time of the [Sync] / Period Rollover that sent the row to GTOPAS', 'New'],
    ['GTOPAS_SYNC_RUN_ID', 'VARCHAR(14)', '', 'Y', '', 'GTOPAS run ID YYYYMMDDHHMMSS ([Sync], [Re-send last Sync] or the Period Rollover)', 'New'],
    ['CREATED_BY', 'VARCHAR(20)', '', 'N', '', 'User of the save / upload, or XD05BATCH', 'New'],
    ['CREATED_DT', 'DATETIME', '', 'N', '', 'Time of the insert (same transaction as the master update)', 'New'],
    ['CHANGED_BY', 'VARCHAR(20)', '', 'Y', '', 'User of [Sync] / [Re-send last Sync]', 'New'],
    ['CHANGED_DT', 'DATETIME', '', 'Y', '', 'Time of the update by [Sync] / [Re-send last Sync]', 'New'],
]


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
    for i, row in enumerate(rows, 1):
        vals = [i] + row
        for c, v in enumerate(vals, 1):
            x = ws.cell(r0 + i, c, v)
            x.font, x.border = F, BOX
            x.alignment = Alignment(wrap_text=True, vertical='top')
            if FILL[row[6]]:
                x.fill = FILL[row[6]]
            if row[6] == 'Removed' and c in (2, 3):
                x.font = Font(name='Arial', size=9, strike=True)
    for c, w in enumerate(WID, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    r = r0 + len(rows) + 2
    for n in notes:
        ws.cell(r, 1, n).font = F
        r += 1
    ws.freeze_panes = 'C5'


def main():
    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, '1. TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE (Kanban Crossdock Master)', T['TB_M_PART_CANDIDATE'][0], kanban(), [
        'PK: PART_NO, PERIOD. No sync column left: the Sync Status and date of both targets are on TB_H_PART_CANDIDATE_STG_SYNC.',
        'Green = new, yellow = changed description, red = removed (strike-through).'])
    sheet(wb, '2. TB_M_PART_CANDIDATE_DEST', 'TB_M_PART_CANDIDATE_DEST (Export Crossdock Master)', T['TB_M_PART_CANDIDATE_DEST'][0], dest(), [
        'PK: PART_NO, PERIOD, DEST_CODE, ORDER_TYPE. FK: (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE.',
        'No new column: a removed destination is deleted at once (no DELETE_FLAG); the staging keeps the DELETE row until it is sent.'])
    sheet(wb, '3. TB_H_PART_CANDIDATE_STG_SYNC', 'TB_H_PART_CANDIDATE_STG_SYNC (new, AP POLE and GTOPAS)',
          'Staging of every value change for the sync to AP POLE (XD07) and GTOPAS (XD06): insert by XD05, the screen and the upload of the Kanban / Export Crossdock Master; '
          'updated only by [Sync] / [Re-send last Sync]. TB_H_PART_CANDIDATE (existing history, update per part + period) is kept as it is.', STG, [
              'PK: HIST_ID. FK1: (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE.',
              'IX1: APPOLE_SYNC_STATUS, PERIOD, PART_NO and IX4: GTOPAS_SYNC_STATUS, PERIOD, PART_NO (rows to send at [Sync] / the Period Rollover).',
              'IX2: APPOLE_SYNC_RUN_ID, PERIOD, SEND_SEQ, PART_NO (upload files, [Re-send last Sync]).',
              'IX3: PART_NO, PERIOD, LEVEL_TYPE, DEST_CODE, ORDER_TYPE, FIELD_NAME, HIST_ID (first OLD / last NEW per key).',
              'Key of a change = LEVEL_TYPE + DEST_CODE + ORDER_TYPE + FIELD_NAME within PART_NO + PERIOD.',
              'AP POLE: [Sync] takes the rows with APPOLE_SYNC_STATUS 0 and HIST_ID <= the last HIST_ID at the click; last row per key -> 1 + SEND_SEQ, earlier rows -> 2.',
              'GTOPAS: [Sync] (Current) / Period Rollover (Next) takes the part + period with a row GTOPAS_SYNC_STATUS 0; the bot gets every destination of the part '
              'with CASE_DAY >= 1 in TB_M_PART_CANDIDATE_DEST (P/No. + Destination Code, all order types together) and compares with GTOPAS WVJA5204: '
              'in NSP only -> Add, in GTOPAS only -> Delete, both -> Keep. Rows -> GTOPAS_SYNC_STATUS 1.'])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
