"""Simulation (19-Nov): Part List with a period (TB_M_PART_CANDIDATE per PART_NO + PERIOD) and the result in AP POLE (XD07), normal
scenario of the user: part A, periods Oct / Nov / Dec 2026. XD05 creates the Next period on day D (27th, example); D/S adjusts the Current
period by screen; [Sync] sends each period to AP POLE with Effective Month / Year = the period.
Target output = the user's picture: Kanban Part Cross Dock Master (WLM9Q890) and Export Cross Dock Master (WLM9Q860).
Run: python3 build_sim_appole_period.py"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from build_sim_fb182 import BAD, HOLD, OK, sheet, table

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD07_Simulation_AP_POLE_Period.xlsx')
NEW, DEL, KEEP = HOLD, BAD, OK
PCS = 6
# per period: (Max Case/Day of the part, [(Buyer-PD, Case/Day)])  - Buyer-PD names as in the picture of the user
PER = {'202610': (16, [('JPN', 4), ('TH', 4), ('US', 4), ('PH', 4)]),
       '202611': (18, [('JPN', 4), ('TH', 4), ('US', 4), ('PH', 4), ('PH-2', 2)]),
       '202612': (12, [('JPN', 4), ('TH', 4), ('US', 4)])}
MM = {'202610': ('10', '2026'), '202611': ('11', '2026'), '202612': ('12', '2026')}
W = [14, 14, 12, 16, 20, 18, 14, 12, 14, 18, 18]

KPM = ['Effective Month', 'Effective Year', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Action of XD07']
ECM = ['Effective Month', 'Effective Year', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Buyer PD', 'Order Type',
       'Transport Code', 'Max Shipping Box Qty (Buyer PD)', 'Max Allowance Qty (Buyer PD)']
PL = ['PART_NO', 'PERIOD', 'PART_STATUS', 'PCS_CASE', 'MAX_CASE_DAY', 'SYNC_STATUS', 'Made by']
MP = ['PART_NO', 'PERIOD', 'DEST_CODE (Buyer PD)', 'CASE_DAY', 'Made by']


def kpm(per, action='-'):
    mx = PER[per][0]
    return [*MM[per], 'A', PCS, mx, PCS * mx, action]


def ecm(per, dests=None):
    mx = PER[per][0]
    return [[*MM[per], 'A', PCS, mx, PCS * mx, bp, '**', 2, c, PCS * c] for bp, c in (dests or PER[per][1])]


def step(ws, r, txt):
    x = ws.cell(r, 1, txt)
    x.font = Font(name='Arial', size=11, bold=True)
    for c in range(1, 12):
        ws.cell(r, c).fill = PatternFill('solid', fgColor='D9E1F2')
    return r + 2


def note(ws, r, lines):
    for t in lines:
        ws.cell(r, 1, t).font = Font(name='Arial', size=9, italic=True)
        r += 1
    return r + 1


def block(ws, r, title, cols, rows, fills=None):
    ws.cell(r, 1, title).font = Font(name='Arial', size=10, bold=True)
    return table(ws, r + 1, cols, rows, W, fills)


def allf(rows, fill):
    return {i: fill for i in range(1, len(rows) + 1)}


def main():
    wb = Workbook()
    wb.remove(wb.active)

    # ---------- 0. target ----------
    ws, r = sheet(wb, '0. Target output', 'Normal scenario: Part List with period -> AP POLE (target output of the user)', [
        'Part A, Pcs/Case 6. Max Allowance Qty = Shipping Box Qty x Max Shipping Box Qty (calculated by AP POLE).',
        'Effective Month / Year = the period of the NSP data (MM, YYYY as in the picture).'])
    r = block(ws, r, 'Kanban Part Cross Dock Master (WLM9Q890)', KPM[:6], [kpm(p)[:6] for p in PER])
    r = block(ws, r, 'Export Cross Dock Master (WLM9Q860)', ECM, [x for p in PER for x in ecm(p)])
    block(ws, r, 'System Master (values used by the bot)', ['Column', 'Value', 'Use'], [
        ['Order Type', '**,C,9,V', "Bot registers '**' (TBC: what C, 9, V are for)"], ['Transport Code', '2', 'Always 2']])

    # ---------- 1. NSP tables ----------
    ws, r = sheet(wb, '1. NSP tables', 'NSP: Part List and Mapping per Destination per period (end state, 1-Dec)', [
        'New: TB_M_PART_CANDIDATE has PERIOD (key PART_NO + PERIOD), like TB_M_PART_CANDIDATE_DEST.'])
    pl = [['A', p, 'Active', PCS, PER[p][0], 'Success', 'XD05 on 27-' + {'202610': 'Sep', '202611': 'Oct', '202612': 'Nov'}[p]] for p in PER]
    r = block(ws, r, 'TB_M_PART_CANDIDATE (per period)', PL, pl)
    mp = [['A', p, bp, c, 'D/S screen 05-Nov' if bp == 'PH-2' else 'XD05'] for p in PER for bp, c in PER[p][1]]
    block(ws, r, 'TB_M_PART_CANDIDATE_DEST (per period)', MP, mp, {i: NEW for i, x in enumerate(mp, 1) if x[2] == 'PH-2'})

    # ---------- 2. steps ----------
    ws, r = sheet(wb, '2. Steps', 'Step by step: NSP period data -> [Sync] -> AP POLE', [
        'Day D = 27th of the month (example; set in the system master). Yellow = added in the step.'])

    r = step(ws, r, 'Step 1 - 27-Sep: XD05 creates period 202610 (Next), D/S clicks [Sync]')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE (new row)', PL, [['A', '202610', 'Active', PCS, 16, 'No Sync', 'XD05']], {1: NEW})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (new rows)', MP, [['A', '202610', bp, c, 'XD05'] for bp, c in PER['202610'][1]], allf(PER['202610'][1], NEW))
    r = block(ws, r, 'AP POLE WLM9Q890: part A not found for 10/2026 -> Add', KPM, [kpm('202610', 'Add')], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q860 ([Maintain Cross Dock] of 10/2026): 4 Buyer PD -> Add', ECM, ecm('202610'), allf(PER['202610'][1], NEW))

    r = step(ws, r, 'Step 2 - 27-Oct: XD05 creates period 202611: Max Case/Day 18, 4 destinations x 4 = 16 (2 left)')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE (new row)', PL, [['A', '202611', 'Active', PCS, 18, 'No Sync', 'XD05']], {1: NEW})
    first4 = PER['202611'][1][:4]
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (new rows)', MP, [['A', '202611', bp, c, 'XD05'] for bp, c in first4], allf(first4, NEW))
    r = block(ws, r, 'AP POLE WLM9Q890: Add 11/2026', KPM, [kpm('202611', 'Add')], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q860 11/2026: 4 Buyer PD -> Add (Total Shipping Allocated 16 of 18)', ECM, ecm('202611', first4), allf(first4, NEW))
    r = note(ws, r, ['10/2026 in AP POLE is not changed (different effective month).'])

    r = step(ws, r, 'Step 3 - 05-Nov: D/S adjusts the Current period 202611 by screen: new destination PH-2, Case/Day 2 (total 18)')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST 202611 (added row)', MP, [['A', '202611', 'PH-2', 2, 'D/S screen']], {1: NEW})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE 202611', PL, [['A', '202611', 'Active', PCS, 18, 'Success -> No Sync', 'D/S screen']], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q890 11/2026: found, values equal -> Keep', KPM, [kpm('202611', 'Keep')], {1: KEEP})
    r = block(ws, r, 'AP POLE WLM9Q860 11/2026: PH-2 not found -> Add (Total Shipping Allocated 16 -> 18)', ECM, ecm('202611', [('PH-2', 2)]), {1: NEW})

    r = step(ws, r, 'Step 4 - 27-Nov: XD05 creates period 202612: Max Case/Day 12, PH not mapped any more')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE (new row)', PL, [['A', '202612', 'Active', PCS, 12, 'No Sync', 'XD05']], {1: NEW})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (new rows)', MP, [['A', '202612', bp, c, 'XD05'] for bp, c in PER['202612'][1]], allf(PER['202612'][1], NEW))
    r = block(ws, r, 'AP POLE WLM9Q890: Add 12/2026', KPM, [kpm('202612', 'Add')], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q860 12/2026: 3 Buyer PD -> Add (no PH row for 12/2026)', ECM, ecm('202612'), allf(PER['202612'][1], NEW))
    r = note(ws, r, ['PH and PH-2 stay in 11/2026 (the Nov records are not touched); 12/2026 simply has no PH row.'])

    r = step(ws, r, 'Step 5 - 1-Dec: Period Rollover: 202612 becomes Current. AP POLE: nothing new (12/2026 sent on 27-Nov)')
    r = block(ws, r, 'AP POLE WLM9Q890 = target output', KPM[:6], [kpm(p)[:6] for p in PER], allf(PER, KEEP))
    block(ws, r, 'AP POLE WLM9Q860 = target output', ECM, [x for p in PER for x in ecm(p)], {i: KEEP for i in range(1, 13)})

    # ---------- 3. open points ----------
    ws, r = sheet(wb, '3. Open points', 'Open points of this simulation', [])
    table(ws, r, ['No', 'Point', 'Assumption in this file'], [
        ['1', 'Two PH rows for 11/2026 (Max Shipping Box 4 and 2) in the picture', 'Two different Buyer PD of the Philippines (PH and PH-2); one Buyer PD per row'],
        ['2', 'Effective Year: picture shows 2026 (4 digits); earlier answer was YY', 'YYYY as in the picture'],
        ['3', "System Master Order Type '**,C,9,V'", "Bot registers '**' only; meaning of C, 9, V to confirm"],
        ['4', 'Max Shipping Box Qty of a Buyer PD = Dest Case/Day of NSP', 'Yes'],
        ['5', 'Part List with period: who edits the Next period (Dec) before 1-Dec', 'XD05 only (as Mapping)'],
    ], [6, 60, 60])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
