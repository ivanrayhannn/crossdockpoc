"""Simulation (19-Nov): period of the Crossdock Master. XD05 runs on day D (set in the system master, 27-Nov is only an example) and
creates the Next period (M+1); its status result is applied to the Part List only on day 1 by a new month-change step (Period Rollover).
Shows TB_M_PART_CANDIDATE, TB_R_PART_DAD_RESULT, TB_M_PART_CANDIDATE_DEST, TB_R_CROSSDOCK_IF_RESULT, GTOPAS WVJA5204 and AP POLE
WLM9Q890 / WLM9Q860 step by step. Decisions of the user: Next only by XD05; GTOPAS = Current, synced automatically on day 1; an edit of
Pcs/Case / Max Case/Day after day D goes to M and M+1 (4b); Max Case/Day below the Next total is maintained by hand.
Run: python3 build_sim_period_rollover.py"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from build_sim_fb182 import BAD, HOLD, OK, sheet, table

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD05_XD16_Simulation_Period_Rollover.xlsx')
NEW = HOLD                      # yellow = changed in this step
DEL = BAD                       # red = deleted / problem
KEEP = OK                       # green = kept / done
M, N = '202611', '202612'       # Current (Nov 2026) and Next (Dec 2026)
BP = {'9722D10': '9722D-10', '9811110': '98111-10', '9715310': '97153-10'}

PART_COLS = ['PART_NO', 'PART_STATUS', 'PCS_CASE', 'MAX_CASE_DAY', 'Next Status (screen, from DAD result)']
DAD_COLS = ['PERIOD', 'PART_NO', 'AVG_MAD', 'MIN_MAD', 'OLD_STATUS', 'NEW_STATUS', 'APPLIED_DT (new column)']
DEST_COLS = ['PART_NO', 'PERIOD', 'DEST_CODE', 'CASE_DAY', 'Period type']
IF_COLS = ['PART_NO', 'TARGET_SYSTEM', 'PERIOD', 'IF_STATUS', 'Note']
GT_COLS = ['P/No.', 'Destination Code', 'Action of XD06']
AP_PART_COLS = ['Eff. Month / Year', 'Part No.', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Action of XD07']
AP_DEST_COLS = ['Eff. Month / Year', 'Part No.', 'Buyer-PD', 'Max Shipping Box Qty', 'Action of XD07']
W = [14, 16, 16, 16, 34, 18, 18]


def block(ws, r, title, cols, rows, fills=None, note=None, widths=None):
    ws.cell(r, 1, title).font = Font(name='Arial', size=10, bold=True)
    if note:
        ws.cell(r, 3, note).font = Font(name='Arial', size=9, italic=True)
    return table(ws, r + 1, cols, rows, widths or W, fills)


def mark(rows, col, values):
    """Fill per row: values = {cell value: fill} on column col."""
    return {i: values[r[col]] for i, r in enumerate(rows, 1) if r[col] in values}


def step(ws, r, text):
    """Step heading inside a target sheet (one sheet per target, all steps one after the other)."""
    x = ws.cell(r, 1, text)
    x.font, x.fill = Font(name='Arial', size=11, bold=True), PatternFill('solid', fgColor='D9E1F2')
    for c in range(2, 8):
        ws.cell(r, c).fill = PatternFill('solid', fgColor='D9E1F2')
    return r + 2


def text(ws, r, lines):
    for t in lines:
        ws.cell(r, 1, t).font = Font(name='Arial', size=9, italic=True)
        r += 1
    return r + 1


def main():
    wb = Workbook()
    wb.remove(wb.active)

    # ---------- 0. rules ----------
    WIDE = [24, 48, 40, 34]
    ws, r = sheet(wb, '0. Rules', 'Period of the Crossdock Master: Current (M), Next (M+1), Period Rollover on day 1', [
        'Example: M = Nov 2026 (202611), M+1 = Dec 2026 (202612). Day D = run day of XD05 set in the system master (27-Nov is only an example).',
        'Yellow = changed in the step, red = deleted or problem, green = kept / done.'])
    r = block(ws, r, 'Who changes which period', ['Period', 'Example', 'Mapping changed by', 'Screen / upload'], [
        ['Past', 'Oct 2026 and before', '-', 'View only'],
        ['Current (M)', 'Nov 2026', 'Screen and upload (adjust of the running month)', 'Edit'],
        ['Next (M+1)', 'Dec 2026, exists from day D until day 1', 'XD05 only (also re-run by [Run calculation])', 'View only'],
    ], widths=WIDE)
    r = block(ws, r, 'Timeline', ['When', 'What', 'GTOPAS (no period)', 'AP POLE'], [
        ['1st - day D-1 of Nov', 'D/S adjusts Nov (screen / upload), [Sync]', 'Nov combinations', 'Eff. 11/26'],
        ['Day D (27-Nov)', 'XD05: DAD result period 202612 (status NOT applied to Part List), mapping 202612 for NEW_STATUS Active', 'No change',
         '[Sync]: Dec data, Eff. 12/26'],
        ['Day D - end of Nov', 'D/S adjusts Nov only. Pcs/Case / Max Case/Day edit -> AP POLE Eff. 11/26 and 12/26 (4b)', 'Nov combinations', 'Eff. 11/26 + 12/26'],
        ['1-Dec (Period Rollover, new)', 'NEW_STATUS of 202612 applied to Part List; Dec becomes Current, Nov Past; parts whose combination differs = No Sync; XD06 runs automatically',
         'Dec combinations (add / delete)', 'Nothing new (Dec sent on day D)'],
    ], widths=WIDE)
    r = block(ws, r, 'Answer: new table or column?', ['Item', 'Proposal'], [
        ['Status for M+1', 'No new table: TB_R_PART_DAD_RESULT already has PERIOD and NEW_STATUS. XD05 writes it on day D and does not change PART_STATUS.'],
        ['New column', 'TB_R_PART_DAD_RESULT.APPLIED_DT: NULL until the Period Rollover applies NEW_STATUS to TB_M_PART_CANDIDATE on day 1.'],
        ['New step', 'Period Rollover on day 1 (new batch, e.g. XD16, or XD05 process 3): apply status, Next -> Current, set No Sync, start XD06.'],
        ['Screen', 'Part List: info column "Next Status (Dec 2026)" from the DAD result with APPLIED_DT NULL.'],
    ], widths=WIDE)

    # ---------- data of the example ----------
    parts = [['P-A', 'Active', 10, 20, '-'], ['P-B', 'Active', 6, 10, '-'], ['P-C', 'Inactive', 5, 10, '-'], ['P-E', 'Active', 8, 30, '-']]
    nxt = {'P-A': 'Active', 'P-B': 'Inactive', 'P-C': 'Active', 'P-E': 'Active'}
    dest_m = [['P-A', M, '9722D10', 10, 'Current'], ['P-A', M, '9811110', 8, 'Current'], ['P-B', M, '9722D10', 6, 'Current'],
              ['P-E', M, '9722D10', 10, 'Current'], ['P-E', M, '9811110', 8, 'Current']]
    dest_n = [['P-A', N, '9722D10', 12, 'Next'], ['P-A', N, '9715310', 8, 'Next'], ['P-C', N, '9811110', 5, 'Next'],
              ['P-E', N, '9722D10', 15, 'Next'], ['P-E', N, '9811110', 10, 'Next']]
    dad = [[N, 'P-A', 26, 20, 'Active', 'Active', 'NULL'], [N, 'P-B', 12, 20, 'Active', 'Inactive', 'NULL'],
           [N, 'P-C', 31, 20, 'Inactive', 'Active', 'NULL'], [N, 'P-E', 40, 20, 'Active', 'Active', 'NULL']]
    gt = [['P-A', '9722D10'], ['P-A', '9811110'], ['P-B', '9722D10'], ['P-E', '9722D10'], ['P-E', '9811110']]

    # ================= 1. GTOPAS =================
    ws, r = sheet(wb, '1. GTOPAS', 'GTOPAS (XD06): the whole simulation - GTOPAS has no period and always holds the Current period', [
        'Compare key P/No. + Destination Code. Quantities are not sent. Day D = 27-Nov (example), Period Rollover = 1-Dec.'])
    r = step(ws, r, 'Step 1 - 20-Nov: before XD05 (Current = Nov, everything synced)')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE', PART_COLS, parts)
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (Nov)', DEST_COLS, dest_m)
    r = block(ws, r, 'GTOPAS WVJA5204 (Depot 01) = Nov combinations', GT_COLS[:2], gt)
    r = step(ws, r, 'Step 2 - 27-Nov (day D): XD05 creates Dec (Next)')
    r = text(ws, r, ['NSP gets the DAD result 202612 and the Dec mapping (see sheet 2 for the values). Part status is not changed yet.',
                     'GTOPAS: no change. Orders of Nov still use the Nov combinations; nothing is Waiting for GTOPAS.'])
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT (GTOPAS)', IF_COLS, [[p, 'GTOPAS', M, '3 Sent', 'No change on day D'] for p in ('P-A', 'P-B', 'P-E')],
              {1: KEEP, 2: KEEP, 3: KEEP})
    r = step(ws, r, 'Step 3 - 28-Nov / 29-Nov: Pcs/Case and Max Case/Day edits')
    r = text(ws, r, ['GTOPAS keeps no quantity: the edits of P-A (Pcs/Case) and P-E (Max Case/Day) give no change in GTOPAS (AP POLE only, sheet 2).'])
    r = step(ws, r, 'Step 4 - 1-Dec 00:10: Period Rollover')
    r = block(ws, r, '4.1 Apply NEW_STATUS of 202612 (TB_R_PART_DAD_RESULT -> TB_M_PART_CANDIDATE), APPLIED_DT filled', DAD_COLS,
              [x[:6] + ['01-Dec-2026 00:10'] for x in dad], {i: KEEP for i in range(1, 5)})
    r = block(ws, r, 'TB_M_PART_CANDIDATE after 4.1', PART_COLS, [[p, nxt[p], pc, mc, '-'] for p, _, pc, mc, _ in parts], {2: NEW, 3: NEW},
              'P-B Inactive, P-C Active from today')
    r = block(ws, r, '4.2 Dec becomes Current, Nov becomes Past', DEST_COLS,
              [x[:4] + ['Past'] for x in dest_m] + [x[:4] + ['Current'] for x in dest_n], {i: NEW for i in range(len(dest_m) + 1, len(dest_m) + len(dest_n) + 1)})
    keys = sorted({(x[0], x[2]) for x in dest_m} | {(x[0], x[2]) for x in dest_n})
    inm, inn = {(x[0], x[2]) for x in dest_m}, {(x[0], x[2]) for x in dest_n}
    cmp_rows = [[p, d, 'Y' if (p, d) in inm else 'N', 'Y' if (p, d) in inn else 'N',
                 'Same' if (p, d) in inm and (p, d) in inn else 'Added' if (p, d) in inn else 'Removed'] for p, d in keys]
    r = block(ws, r, '4.3 Compare the combinations Nov vs Dec per part', ['PART_NO', 'DEST_CODE', 'In Nov', 'In Dec', 'Result'], cmp_rows,
              mark(cmp_rows, 4, {'Same': KEEP, 'Added': NEW, 'Removed': DEL}))
    r = block(ws, r, '4.4 Parts with a different combination -> No Sync for GTOPAS (period 202612), then Sent', IF_COLS, [
        ['P-A', 'GTOPAS', N, '0 -> 3 Sent', '9811110 removed, 9715310 added'], ['P-B', 'GTOPAS', N, '0 -> 3 Sent', 'Inactive: all rows removed'],
        ['P-C', 'GTOPAS', N, '0 -> 3 Sent', 'Active: 9811110 added'], ['P-E', 'GTOPAS', N, '3 Sent (no change)', 'Same combinations']], {1: NEW, 2: NEW, 3: NEW, 4: KEEP})
    r = text(ws, r, ['4.5 XD06 starts automatically: the bot downloads the Export Excel (Dec, all Sync Status) and searches every P/No. sent by the rollover in GTOPAS.'])
    work = [['P-A', '9715310', 'Y', 'N', 'Add'], ['P-A', '9722D10', 'Y', 'Y', 'Keep'], ['P-A', '9811110', 'N', 'Y', 'Delete'],
            ['P-B', '9722D10', 'N (Inactive)', 'Y', 'Delete'], ['P-C', '9811110', 'Y', 'N', 'Add']]
    r = block(ws, r, '4.5 Sheet GTOPAS Compare (parts sent by the rollover)', ['P/No.', 'Destination Code', 'In NSP (Dec)', 'In GTOPAS', 'Action'], work,
              mark(work, 4, {'Keep': KEEP, 'Add': NEW, 'Delete': DEL}))
    gt_after = [['P-A', '9722D10', 'Keep'], ['P-A', '9811110', 'Delete (MT = DEL)'], ['P-A', '9715310', 'Add'], ['P-B', '9722D10', 'Delete (MT = DEL)'],
                ['P-C', '9811110', 'Add'], ['P-E', '9722D10', 'Not sent, not touched'], ['P-E', '9811110', 'Not sent, not touched']]
    r = block(ws, r, '4.6 GTOPAS WVJA5204 after XD06', GT_COLS, gt_after,
              {1: KEEP, 2: DEL, 3: NEW, 4: DEL, 5: NEW, 6: KEEP, 7: KEEP})
    block(ws, r, '4.6 TB_R_CROSSDOCK_IF_RESULT (GTOPAS, 202612)', IF_COLS, [[p, 'GTOPAS', N, '3 Sent', 'LAST_SYNC_DT 01-Dec'] for p in ('P-A', 'P-B', 'P-C')],
          {1: KEEP, 2: KEEP, 3: KEEP})

    # ================= 2. AP POLE =================
    ws, r = sheet(wb, '2. AP POLE', 'AP POLE (XD07): the whole simulation - one record per Effective Month / Year (MM/YY)', [
        'Next (Dec) is sent on day D with Eff. 12/26; an edit after day D goes to Eff. 11/26 and 12/26 (4b). Assumption (TBC): a part without a 12/26 record is not crossdock in Dec.'])
    r = step(ws, r, 'Step 1 - 20-Nov: before XD05 (Eff. 11/26 in AP POLE)')
    r = block(ws, r, 'AP POLE WLM9Q890 (part)', AP_PART_COLS, [['11/26', p, pc, mc, '-'] for p, s_, pc, mc, _ in parts if s_ == 'Active'])
    r = block(ws, r, 'AP POLE WLM9Q860 (Buyer-PD)', AP_DEST_COLS, [['11/26', p, BP[d], c, '-'] for p, _, d, c, _ in dest_m])
    r = step(ws, r, 'Step 2 - 27-Nov (day D): XD05 creates Dec, [Sync] -> XD07 sends Eff. 12/26')
    r = block(ws, r, 'NSP TB_R_PART_DAD_RESULT 202612 (status not applied yet)', DAD_COLS, dad, {i: NEW for i in range(1, 5)})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (Dec, Next)', DEST_COLS, dest_n, {i: NEW for i in range(1, 6)})
    ap_n = [['12/26', 'P-A', 10, 20, 'Add'], ['12/26', 'P-C', 5, 10, 'Add (Inactive -> Active for Dec)'], ['12/26', 'P-E', 8, 30, 'Add'],
            ['12/26', 'P-B', 6, 10, 'No record (Inactive for Dec)']]
    r = block(ws, r, 'AP POLE WLM9Q890 (part), Eff. 12/26', AP_PART_COLS, ap_n, {1: NEW, 2: NEW, 3: NEW, 4: DEL})
    r = block(ws, r, 'AP POLE WLM9Q860 (Buyer-PD), Eff. 12/26', AP_DEST_COLS, [['12/26', p, BP[d], c, 'Add'] for p, _, d, c, _ in dest_n],
              {i: NEW for i in range(1, 6)})
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT (APPOLE)', IF_COLS, [[p, 'APPOLE', N, '3 Sent', 'LAST_SYNC_DT 27-Nov'] for p in ('P-A', 'P-B', 'P-C', 'P-E')],
              {i: KEEP for i in range(1, 5)})
    r = step(ws, r, 'Step 3 - 28-Nov: Pcs/Case of P-A 10 -> 12 (after day D) -> Eff. 11/26 and 12/26 (4b)')
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT after the save', IF_COLS, [['P-A', 'APPOLE', M, '0 No Sync', 'Eff. 11/26'],
                                                                      ['P-A', 'APPOLE', N, '0 No Sync', 'Eff. 12/26']], {1: NEW, 2: NEW})
    r = block(ws, r, 'AP POLE WLM9Q890 after [Sync] (Current first, then Next)', AP_PART_COLS,
              [['11/26', 'P-A', 12, 20, 'Edit (1st)'], ['12/26', 'P-A', 12, 20, 'Edit (2nd)']], {1: NEW, 2: NEW})
    r = step(ws, r, 'Step 4 - 29-Nov: Max Case/Day of P-E 30 -> 20; Nov total 18 (save allowed), Dec total 25 (over)')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST of P-E (Dec)', DEST_COLS, [['P-E', N, '9722D10', 15, 'Next'], ['P-E', N, '9811110', 10, 'Next']],
              {1: DEL, 2: DEL}, 'Total 25 > new Max Case/Day 20')
    r = block(ws, r, 'AP POLE', ['Screen', 'What happens'], [
        ['WLM9Q890 Eff. 11/26', 'Edit Max Shipping Box Qty 30 -> 20: OK (Total Shipping Allocated 18).'],
        ['WLM9Q890 Eff. 12/26', 'Edit 30 -> 20 refused: Total Shipping Allocated 25 > 20. Maintained by hand (open point 1).']], {1: KEEP, 2: DEL}, widths=[24, 70])
    r = step(ws, r, 'Step 5 - 1-Dec: Period Rollover')
    block(ws, r, 'AP POLE', ['Screen', 'What happens'], [
        ['WLM9Q890 / WLM9Q860', 'Nothing new: the Dec data (Eff. 12/26) was sent on 27-Nov. From 1-Dec AP POLE uses the 12/26 records.']], {1: KEEP}, widths=[24, 70])

    # ---------- 7. open points ----------
    ws, r = sheet(wb, '3. Open points', 'Open points', [])
    block(ws, r, 'To decide', ['No', 'Point', 'Proposal'], [
        ['1', 'Max Case/Day below the Next total (step 5)', 'Option A: warning + Dec mapping of that part editable'],
        ['2', 'Period Rollover: new batch (XD16) or XD05 process 3', 'New batch: other schedule (day 1, 00:10)'],
        ['3', 'AP POLE keeps one record per effective month (step 3)', 'TBC with the AP POLE team'],
        ['4', 'Sync Status per part per period (Nov / Dec)', 'Screen shows the status of the period of the filter'],
        ['5', 'Day D: set in the system master (not fixed)', 'Before the last working day of the month'],
    ], widths=[6, 50, 50])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
