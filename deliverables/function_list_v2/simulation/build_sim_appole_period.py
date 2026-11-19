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
# per period: (Max Case/Day of the part, [(Buyer-PD, Order Type, Case/Day)]); one row per Buyer PD + Order Type (decided 19-Nov)
PER = {'202610': (16, [('JPN', '**', 4), ('TH', '**', 4), ('US', '**', 4), ('PH', '**', 4)]),
       '202611': (18, [('JPN', '**', 4), ('TH', '**', 4), ('US', '**', 4), ('PH', '**', 4), ('PH', 'C', 2)]),
       '202612': (12, [('JPN', '**', 4), ('TH', '**', 4), ('US', '**', 4)])}
MM = {'202610': ('10', '2026'), '202611': ('11', '2026'), '202612': ('12', '2026')}
W = [14, 14, 12, 16, 20, 18, 14, 12, 14, 18, 18, 14]

KPM = ['Effective Month', 'Effective Year', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Action of XD07']
ECM = ['Effective Month', 'Effective Year', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Buyer PD', 'Order Type',
       'Transport Code', 'Max Shipping Box Qty (Buyer PD)', 'Max Allowance Qty (Buyer PD)']
PL = ['PART_NO', 'PERIOD', 'PART_STATUS', 'PCS_CASE', 'MAX_CASE_DAY', 'SYNC_STATUS', 'Made by']
MP = ['PART_NO', 'PERIOD', 'DEST_CODE (Buyer PD)', 'ORDER_TYPE', 'CASE_DAY', 'Made by']


def kpm(per, action='-', mx=None):
    mx = mx or PER[per][0]
    return [*MM[per], 'A', PCS, mx, PCS * mx, action]


def ecm(per, dests=None, mx=None, action=None):
    mx = mx or PER[per][0]
    return [[*MM[per], 'A', PCS, mx, PCS * mx, bp, ot, 2, c, PCS * c] + ([action] if action else []) for bp, ot, c in (dests or PER[per][1])]


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


def block(ws, r, title, cols, rows, fills=None, widths=None):
    ws.cell(r, 1, title).font = Font(name='Arial', size=10, bold=True)
    return table(ws, r + 1, cols, rows, widths or W, fills)


def allf(rows, fill):
    return {i: fill for i in range(1, len(rows) + 1)}


def main():
    wb = Workbook()
    wb.remove(wb.active)

    # ---------- 0. target ----------
    ws, r = sheet(wb, '0. Target output', 'Normal scenario: Part List with period -> AP POLE (target output of the user)', [
        'Part A, Pcs/Case 6. Max Allowance Qty = Shipping Box Qty x Max Shipping Box Qty (calculated by AP POLE).',
        'Effective Month / Year = the period of the NSP data (MM, YYYY as in the picture).'])
    r = block(ws, r, 'Kanban Crossdock Master = AP POLE Kanban Part Cross Dock Master (WLM9Q890)', KPM[:6], [kpm(p)[:6] for p in PER])
    r = block(ws, r, 'Export Crossdock Master = AP POLE Export Customer Cross Dock Master (WLM9Q860)', ECM, [x for p in PER for x in ecm(p)])
    block(ws, r, 'System Master (values used by the bot)', ['Column', 'Value', 'Use'], [
        ['Order Type', '**,C,9,V', "Bot registers '**' (TBC: what C, 9, V are for)"], ['Transport Code', '2', 'Always 2']])

    # ---------- 1. NSP tables ----------
    ws, r = sheet(wb, '1. NSP tables', 'NSP: Kanban Crossdock Master (Part List) and Export Crossdock Master (Mapping) per period (end state, 1-Dec)', [
        'New: TB_M_PART_CANDIDATE has PERIOD (key PART_NO + PERIOD), like TB_M_PART_CANDIDATE_DEST.'])
    pl = [['A', p, 'Active', PCS, PER[p][0], 'Success', 'XD05 on 27-' + {'202610': 'Sep', '202611': 'Oct', '202612': 'Nov'}[p]] for p in PER]
    r = block(ws, r, 'TB_M_PART_CANDIDATE (per period)', PL, pl)
    mp = [['A', p, bp, ot, c, 'D/S screen 05-Nov' if ot == 'C' else 'XD05'] for p in PER for bp, ot, c in PER[p][1]]
    block(ws, r, 'TB_M_PART_CANDIDATE_DEST (per period; key PART_NO + PERIOD + DEST_CODE + ORDER_TYPE)', MP, mp, {i: NEW for i, x in enumerate(mp, 1) if x[3] == 'C'})

    # ---------- 2. steps ----------
    ws, r = sheet(wb, '2. Steps', 'Step by step: NSP period data -> [Sync] -> AP POLE', [
        'Day D = 27th of the month (example; set in the system master). Yellow = added in the step.'])

    r = step(ws, r, 'Step 1 - 27-Sep: XD05 creates period 202610 (Next), D/S clicks [Sync]')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE (new row)', PL, [['A', '202610', 'Active', PCS, 16, 'No Sync', 'XD05']], {1: NEW})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (new rows)', MP, [['A', '202610', bp, ot, c, 'XD05'] for bp, ot, c in PER['202610'][1]], allf(PER['202610'][1], NEW))
    r = block(ws, r, 'AP POLE WLM9Q890: part A not found for 10/2026 -> Add', KPM, [kpm('202610', 'Add')], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q860 ([Maintain Cross Dock] of 10/2026): 4 Buyer PD -> Add', ECM, ecm('202610'), allf(PER['202610'][1], NEW))

    r = step(ws, r, 'Step 2 - 27-Oct: XD05 creates period 202611: Max Case/Day 18, 4 destinations x 4 = 16 (2 left)')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE (new row)', PL, [['A', '202611', 'Active', PCS, 18, 'No Sync', 'XD05']], {1: NEW})
    first4 = PER['202611'][1][:4]
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (new rows)', MP, [['A', '202611', bp, ot, c, 'XD05'] for bp, ot, c in first4], allf(first4, NEW))
    r = block(ws, r, 'AP POLE WLM9Q890: Add 11/2026', KPM, [kpm('202611', 'Add')], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q860 11/2026: 4 Buyer PD -> Add (Total Shipping Allocated 16 of 18)', ECM, ecm('202611', first4), allf(first4, NEW))
    r = note(ws, r, ['10/2026 in AP POLE is not changed (different effective month).'])

    r = step(ws, r, 'Step 3 - 05-Nov: D/S adjusts the Current period 202611 on Export Crossdock Master: PH again with Order Type C, Case/Day 2 (total 18)')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST 202611 (added row)', MP, [['A', '202611', 'PH', 'C', 2, 'D/S screen']], {1: NEW})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE 202611', PL, [['A', '202611', 'Active', PCS, 18, 'Success -> No Sync', 'D/S screen']], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q890 11/2026: found, values equal -> Keep', KPM, [kpm('202611', 'Keep')], {1: KEEP})
    r = block(ws, r, 'AP POLE WLM9Q860 11/2026: PH + Order Type C not found -> Add (Total Shipping Allocated 16 -> 18)', ECM, ecm('202611', [('PH', 'C', 2)]), {1: NEW})

    r = step(ws, r, 'Step 4 - 27-Nov: XD05 creates period 202612: Max Case/Day 12, PH not mapped any more')
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE (new row)', PL, [['A', '202612', 'Active', PCS, 12, 'No Sync', 'XD05']], {1: NEW})
    r = block(ws, r, 'NSP TB_M_PART_CANDIDATE_DEST (new rows)', MP, [['A', '202612', bp, ot, c, 'XD05'] for bp, ot, c in PER['202612'][1]], allf(PER['202612'][1], NEW))
    r = block(ws, r, 'AP POLE WLM9Q890: Add 12/2026', KPM, [kpm('202612', 'Add')], {1: NEW})
    r = block(ws, r, 'AP POLE WLM9Q860 12/2026: 3 Buyer PD -> Add (no PH row for 12/2026)', ECM, ecm('202612'), allf(PER['202612'][1], NEW))
    r = note(ws, r, ['PH (** and C) stays in 11/2026 (the Nov records are not touched); 12/2026 simply has no PH row.'])

    r = step(ws, r, 'Step 5 - 1-Dec: Period Rollover: 202612 becomes Current. AP POLE: nothing new (12/2026 sent on 27-Nov)')
    r = block(ws, r, 'AP POLE WLM9Q890 = target output', KPM[:6], [kpm(p)[:6] for p in PER], allf(PER, KEEP))
    r = block(ws, r, 'AP POLE WLM9Q860 = target output', ECM, [x for p in PER for x in ecm(p)], {i: KEEP for i in range(1, 13)})

    # ---------- scenario 2: Max Case/Day down in the same period ----------
    r = step(ws, r, 'Step 6 - 10-Dec (scenario 2): Max Case/Day of A for the Current period 202612 goes down 12 -> 8')
    r = note(ws, r, ['6.1 D/S first tries Kanban Crossdock Master: Max Case/Day 12 -> 8 is blocked (message 14: below the mapped total 12 of the period).',
                     '6.2 So D/S first reduces the destinations on Export Crossdock Master 202612 (here: US removed, total 12 -> 8) and saves.',
                     '6.3 Then D/S changes Max Case/Day 12 -> 8 on Kanban Crossdock Master 202612 and saves. [Sync].'])
    r = block(ws, r, '6.2 NSP TB_M_PART_CANDIDATE_DEST 202612', MP, [['A', '202612', 'JPN', '**', 4, 'Kept'], ['A', '202612', 'TH', '**', 4, 'Kept'],
                                                                   ['A', '202612', 'US', '**', 4, 'Removed by D/S']], {1: KEEP, 2: KEEP, 3: DEL})
    r = block(ws, r, '6.3 NSP TB_M_PART_CANDIDATE 202612', PL, [['A', '202612', 'Active', PCS, '12 -> 8', 'No Sync', 'D/S screen']], {1: NEW})
    r = note(ws, r, ['6.4 XD07 does the destination level first when Max Shipping Box Qty goes down (AP POLE refuses a part max below Total Shipping Allocated):'])
    r = block(ws, r, '6.4a AP POLE WLM9Q860 12/2026 (first): Delete US -> Total Shipping Allocated 12 -> 8', ECM + ['Action of XD07'],
              ecm('202612', [('JPN', '**', 4), ('TH', '**', 4)], action='Keep') + ecm('202612', [('US', '**', 4)], action='Delete'), {1: KEEP, 2: KEEP, 3: DEL})
    r = block(ws, r, '6.4b AP POLE WLM9Q890 12/2026 (second): Edit Max Shipping Box Qty 12 -> 8, Max Allowance 72 -> 48', KPM, [kpm('202612', 'Edit', 8)], {1: NEW})
    r = block(ws, r, 'AP POLE after scenario 2 - WLM9Q890', KPM[:6], [kpm('202610')[:6], kpm('202611')[:6], kpm('202612', mx=8)[:6]], {3: NEW})
    r = block(ws, r, 'AP POLE after scenario 2 - WLM9Q860', ECM, ecm('202610') + ecm('202611') + ecm('202612', [('JPN', '**', 4), ('TH', '**', 4)], mx=8),
              {10: NEW, 11: NEW})
    ws.cell(r, 1, 'Order rule of XD07 for a period').font = Font(name='Arial', size=10, bold=True)
    note(ws, r + 1, ['Max Case/Day goes down: 1. WLM9Q860 Delete / Edit the Buyer PD rows (total <= new max), 2. WLM9Q890 Edit Max Shipping Box Qty.',
                     'Max Case/Day goes up or stays: 1. WLM9Q890 Add / Edit the part, 2. WLM9Q860 Delete, Edit, then Add the Buyer PD rows.'])

    # ---------- 3. open points ----------
    ws, r = sheet(wb, '3. Open points', 'Open points of this simulation', [])
    table(ws, r, ['No', 'Point', 'Assumption in this file'], [
        ['1', 'Two PH rows for 11/2026 (Max Shipping Box 4 and 2)', 'Decided 19-Nov: the same Buyer PD / destination may have 2 rows in a period when the Order Type differs (PH ** and PH C)'],
        ['2', 'Effective Year', 'Decided 19-Nov: YYYY'],
        ['3', "Order Type '**,C,9,V'", 'Decided 19-Nov: the values a row may have; Order Type is set per destination row on Export Crossdock Master'],
        ['4', 'Max Shipping Box Qty of a Buyer PD = Dest Case/Day of NSP', 'Yes'],
        ['5', 'Part List with period: who edits the Next period (Dec) before 1-Dec', 'XD05 only (as Mapping)'],
    ], [6, 60, 60])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
