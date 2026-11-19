"""Simulation (19-Nov): period of the Crossdock Master. XD05 runs on day D (set in the system master, 27-Nov is only an example) and
creates the Next period (M+1); its status result is applied to the Part List only on day 1 by a new month-change step (Period Rollover).
Shows TB_M_PART_CANDIDATE, TB_R_PART_DAD_RESULT, TB_M_PART_CANDIDATE_DEST, TB_R_CROSSDOCK_IF_RESULT, GTOPAS WVJA5204 and AP POLE
WLM9Q890 / WLM9Q860 step by step. Decisions of the user: Next only by XD05; GTOPAS = Current, synced automatically on day 1; an edit of
Pcs/Case / Max Case/Day after day D goes to M and M+1 (4b); Max Case/Day below the Next total is maintained by hand.
Run: python3 build_sim_period_rollover.py"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font
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

    # parts used in the example (Nov)
    parts = [['P-A', 'Active', 10, 20, '-'], ['P-B', 'Active', 6, 10, '-'], ['P-C', 'Inactive', 5, 10, '-'], ['P-E', 'Active', 8, 30, '-']]
    dest_m = [['P-A', M, '9722D10', 10, 'Current'], ['P-A', M, '9811110', 8, 'Current'], ['P-B', M, '9722D10', 6, 'Current'],
              ['P-E', M, '9722D10', 10, 'Current'], ['P-E', M, '9811110', 8, 'Current']]
    gt = [['P-A', '9722D10'], ['P-A', '9811110'], ['P-B', '9722D10'], ['P-E', '9722D10'], ['P-E', '9811110']]

    # ---------- 1. before day D ----------
    ws, r = sheet(wb, '1. 20-Nov before D', 'Step 1 - 20-Nov: before XD05 (only Current Nov exists, everything synced)', [
        'P-A, P-B, P-E Active; P-C Inactive. GTOPAS and AP POLE hold the Nov data.'])
    r = block(ws, r, 'TB_M_PART_CANDIDATE', PART_COLS, parts)
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST', DEST_COLS, dest_m)
    r = block(ws, r, 'GTOPAS WVJA5204 (Depot 01)', GT_COLS[:2], gt)
    r = block(ws, r, 'AP POLE WLM9Q890 (part)', AP_PART_COLS, [['11/26', p, pc, mc, '-'] for p, s, pc, mc, _ in parts if s == 'Active'])
    block(ws, r, 'AP POLE WLM9Q860 (Buyer-PD)', AP_DEST_COLS, [['11/26', p, BP[d], c, '-'] for p, _, d, c, _ in dest_m])

    # ---------- 2. day D: XD05 ----------
    dad = [[N, 'P-A', 26, 20, 'Active', 'Active', 'NULL'], [N, 'P-B', 12, 20, 'Active', 'Inactive', 'NULL'],
           [N, 'P-C', 31, 20, 'Inactive', 'Active', 'NULL'], [N, 'P-E', 40, 20, 'Active', 'Active', 'NULL']]
    dest_n = [['P-A', N, '9722D10', 12, 'Next'], ['P-A', N, '9715310', 8, 'Next'], ['P-C', N, '9811110', 5, 'Next'],
              ['P-E', N, '9722D10', 15, 'Next'], ['P-E', N, '9811110', 10, 'Next']]
    parts_d = [[p, s, pc, mc, {'P-A': 'Active', 'P-B': 'Inactive', 'P-C': 'Active', 'P-E': 'Active'}[p]] for p, s, pc, mc, _ in parts]
    ws, r = sheet(wb, '2. 27-Nov XD05', 'Step 2 - Day D (27-Nov): XD05 creates the Next period 202612', [
        'Process 1: DAD result for 202612; PART_STATUS of TB_M_PART_CANDIDATE is NOT changed (applied on 1-Dec).',
        'Process 2: mapping 202612 for the parts with NEW_STATUS Active (P-A, P-C, P-E). P-B (Inactive for Dec) gets no Dec mapping.',
        'The Dec parts get No Sync for APPOLE period 202612. GTOPAS is not touched (Current is still Nov).'])
    r = block(ws, r, 'TB_R_PART_DAD_RESULT (inserted)', DAD_COLS, dad, {i: NEW for i in range(1, 5)})
    r = block(ws, r, 'TB_M_PART_CANDIDATE (status not changed; screen shows Next Status)', PART_COLS, parts_d,
              {2: DEL, 3: NEW}, 'P-B Active -> Inactive and P-C Inactive -> Active only from 1-Dec')
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST', DEST_COLS, dest_m + dest_n, {i: NEW for i in range(len(dest_m) + 1, len(dest_m) + len(dest_n) + 1)})
    block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT', IF_COLS, [[p, 'APPOLE', N, '0 No Sync', 'Dec data to send'] for p in ('P-A', 'P-B', 'P-C', 'P-E')] +
          [[p, 'GTOPAS', M, '1 Success', 'No change'] for p in ('P-A', 'P-B', 'P-E')], {1: NEW, 2: NEW, 3: NEW, 4: NEW})

    # ---------- 3. day D: [Sync] -> XD07 Dec ----------
    ws, r = sheet(wb, '3. 27-Nov Sync', 'Step 3 - Day D (27-Nov): [Sync], XD07 sends Dec to AP POLE (Eff. 12/26)', [
        'XD07 works on Current first (nothing Waiting for Nov here), then Next. XD06: nothing Waiting for GTOPAS (Current Nov unchanged).',
        'Assumption (TBC): AP POLE keeps one record per effective month; a part without a 12/26 record is not crossdock in Dec.'])
    ap_n = [['12/26', 'P-A', 10, 20, 'Add'], ['12/26', 'P-C', 5, 10, 'Add'], ['12/26', 'P-E', 8, 30, 'Add'], ['12/26', 'P-B', 6, 10, 'No record (Inactive in Dec)']]
    r = block(ws, r, 'AP POLE WLM9Q890 (part), Eff. 12/26', AP_PART_COLS, ap_n, {1: NEW, 2: NEW, 3: NEW, 4: DEL})
    r = block(ws, r, 'AP POLE WLM9Q860 (Buyer-PD), Eff. 12/26', AP_DEST_COLS, [['12/26', p, BP[d], c, 'Add'] for p, _, d, c, _ in dest_n],
              {i: NEW for i in range(1, 6)})
    block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT', IF_COLS, [[p, 'APPOLE', N, '1 Success', 'LAST_SYNC_DT 27-Nov'] for p in ('P-A', 'P-B', 'P-C', 'P-E')],
          {i: KEEP for i in range(1, 5)})

    # ---------- 4. 28-Nov: Pcs/Case edit (4b) ----------
    ws, r = sheet(wb, '4. 28-Nov Pcs-Case', 'Step 4 - 28-Nov: D/S changes Pcs/Case of P-A 10 -> 12 (after day D, before 1-Dec)', [
        'Decision 4b: the Next period exists, so the change goes to AP POLE for Eff. 11/26 and Eff. 12/26. GTOPAS keeps no quantity: no change.'])
    r = block(ws, r, 'TB_M_PART_CANDIDATE', PART_COLS, [['P-A', 'Active', 12, 20, 'Active']], {1: NEW})
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT after the save', IF_COLS, [['P-A', 'APPOLE', M, '0 No Sync', 'Eff. 11/26'],
                                                                      ['P-A', 'APPOLE', N, '0 No Sync', 'Eff. 12/26']], {1: NEW, 2: NEW})
    block(ws, r, 'AP POLE WLM9Q890 after [Sync] (Current first, then Next)', AP_PART_COLS,
          [['11/26', 'P-A', 12, 20, 'Edit (1st)'], ['12/26', 'P-A', 12, 20, 'Edit (2nd)']], {1: NEW, 2: NEW})

    # ---------- 5. 29-Nov: Max Case/Day below the Next total ----------
    ws, r = sheet(wb, '5. 29-Nov Max below', 'Step 5 - 29-Nov: D/S lowers Max Case/Day of P-E 30 -> 20; Dec mapping total = 25', [
        'Nov mapping of P-E = 18 <= 20: the screen allows the save (message 14 checks the Current period only). The Dec mapping made by XD05 = 25 > 20.',
        'Decision: maintained by hand. Next is view only, so a rule is needed (see the table).'])
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST of P-E', DEST_COLS, [['P-E', N, '9722D10', 15, 'Next'], ['P-E', N, '9811110', 10, 'Next']], {1: DEL, 2: DEL},
              'Total 25 > new Max Case/Day 20')
    r = block(ws, r, 'Problem in AP POLE', ['Screen', 'What happens'], [
        ['WLM9Q890 Eff. 12/26', 'Edit Max Shipping Box Qty 30 -> 20 is refused: Total Shipping Allocated 25 > 20 (AP POLE rule).'],
        ['Result', 'XD07 fails for P-E (and with "one fails, all fail" for the whole run).']], {1: DEL, 2: DEL})
    block(ws, r, 'Options for "maintain by hand" (to decide)', ['Option', 'How', 'Remark'], [
        ['A (proposal)', 'Save allowed with a warning; P-E gets "Over quota" for Dec; D/S may edit the Dec mapping of that part only', 'Small exception to "Next = XD05 only"'],
        ['B', 'Block Max Case/Day below the Next total (message); D/S changes it on 1-Dec when Dec is Current', 'Simple; the change waits until 1-Dec'],
        ['C', 'D/S runs XD05 again ([Run calculation]) after the change', 'Recalculates every part of Dec']], {1: KEEP})

    # ---------- 6. 1-Dec: Period Rollover ----------
    parts_r = [['P-A', 'Active', 12, 20, '-'], ['P-B', 'Inactive', 6, 10, '-'], ['P-C', 'Active', 5, 10, '-'], ['P-E', 'Active', 8, 30, '-']]
    ws, r = sheet(wb, '6. 1-Dec Rollover', 'Step 6 - 1-Dec: Period Rollover (new step) and automatic XD06', [
        'Apply NEW_STATUS of 202612 (APPLIED_DT NULL) to TB_M_PART_CANDIDATE, set APPLIED_DT; Dec becomes Current, Nov Past.',
        'Parts whose part + destination combination of Dec differs from Nov -> GTOPAS No Sync, then XD06 runs automatically. AP POLE: nothing (Dec sent on 27-Nov).'])
    r = block(ws, r, 'TB_R_PART_DAD_RESULT', DAD_COLS, [x[:6] + ['01-Dec-2026 00:10'] for x in dad], {i: KEEP for i in range(1, 5)})
    r = block(ws, r, 'TB_M_PART_CANDIDATE', PART_COLS, parts_r, {2: NEW, 3: NEW}, 'P-B Inactive, P-C Active from today')
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT (GTOPAS, period 202612)', IF_COLS, [
        ['P-A', 'GTOPAS', N, '0 -> 3 -> 1', '9811110 removed, 9715310 added'], ['P-B', 'GTOPAS', N, '0 -> 3 -> 1', 'Inactive: all rows deleted'],
        ['P-C', 'GTOPAS', N, '0 -> 3 -> 1', 'Active: 9811110 added'], ['P-E', 'GTOPAS', N, '1 (no change)', 'Same combinations as Nov']], {1: NEW, 2: NEW, 3: NEW, 4: KEEP})
    gt_after = [['P-A', '9722D10', 'Keep'], ['P-A', '9811110', 'Delete'], ['P-A', '9715310', 'Add'], ['P-B', '9722D10', 'Delete'],
                ['P-C', '9811110', 'Add'], ['P-E', '9722D10', 'Keep'], ['P-E', '9811110', 'Keep']]
    block(ws, r, 'GTOPAS WVJA5204 (XD06, automatic)', GT_COLS, gt_after, mark(gt_after, 2, {'Keep': KEEP, 'Add': NEW, 'Delete': DEL}))

    # ---------- 7. open points ----------
    ws, r = sheet(wb, '7. Open points', 'Open points', [])
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
