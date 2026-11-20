"""Simulation (19 / 20-Nov) with the full tables of the ERD: Crossdock Master -> DAD calculation (XD05 process 1 + 2 on day D) -> [Sync]
AP POLE (XD07, Next period) -> Period Rollover on day 1 (XD05 process 3) -> automatic sync GTOPAS (XD06).
Columns are read from the specs (same source as the ERD / DB Structure: erd/build_erd.load_tables), so every column of each table is shown.
Example: Current period 202611, day D = 27-Nov-2026, Next period 202612, N = 6 months (202605 - 202610).
Run: python3 build_sim_full_flow.py"""
import math
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'erd'))
from build_erd import load_tables                      # noqa: E402
from build_sim_fb182 import BAD, HOLD, OK, sheet, table  # noqa: E402

OUT = os.path.join(HERE, 'XD05_XD06_XD07_Simulation_Full_Flow.xlsx')
NEW, DEL, KEEP = HOLD, BAD, OK
T = load_tables()[0]
COLS = {n: [c[0] for c in T[n][1]] for n in ('TB_R_ACTUAL_DEMAND_SUMMARY', 'TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE_DEST',
                                             'TB_R_PART_DAD_RESULT', 'TB_H_PART_CANDIDATE')}
LOG_COLS = ['BATCH_ID', 'RUN_ID', 'SEND_DT', 'SENT_BY', 'PERIOD', 'PARTS', 'STATUS']
# proposal (20-Nov, discussion, not yet in the UISS): one Sync Status per target instead of SYNC_STATUS
_k = [c for c in COLS['TB_M_PART_CANDIDATE'] if c not in ('SYNC_STATUS', 'GTOPAS_SYNC_DT', 'APPOLE_SYNC_DT', 'SYNC_RUN_ID')]
_i = _k.index('PART_STATUS') + 1
COLS['TB_M_PART_CANDIDATE'] = _k[:_i] + ['GTOPAS_SYNC_STATUS', 'GTOPAS_SYNC_DT', 'APPOLE_SYNC_STATUS', 'APPOLE_SYNC_DT', 'SYNC_RUN_ID'] + _k[_i:]
ST = {'0': '0 No Sync', '3': '3 Sent', '0>3': '0 No Sync -> 3 Sent'}
CUR, NXT, RUN, ROLL = '202611', '202612', '27-Nov-2026 02:00', '01-Dec-2026 00:10'
MONTHS = ['202605', '202606', '202607', '202608', '202609', '202610']
N = len(MONTHS)
DEST = {'9722D10': 'JPN', '9715310': 'KR', '9811110': 'TW', '9618201': 'US'}
BP = {'9722D10': '9722D-10', '9715310': '97153-10', '9811110': '98111-10', '9618201': '96182-01'}
BATCH, DS, RPA = 'XD05BATCH', 'D.Anggraini', 'RPABOT'

# parts in the Current period 202611 (Kanban Crossdock Master)
PARTS = {'A': dict(name='Part A', min=300, pcs=6, max=12, st='Active', eff='01-Jun-2026'),
         'B': dict(name='Part B', min=200, pcs=10, max=6, st='Candidate', eff='15-Nov-2026'),
         'C': dict(name='Part C', min=500, pcs=8, max=10, st='Active', eff='01-Jun-2026'),
         'D': dict(name='Part D', min=100, pcs=4, max=8, st='Active', eff='01-Jun-2026')}
CUR_MAP = [('A', '9722D10', '**', 6), ('A', '9715310', '**', 6), ('C', '9715310', '**', 10), ('D', '9722D10', '**', 8)]
# demand per month (part, dest, order type group, MAD) for every month of the range; C only 3 months
DEMAND = [('A', '9722D10', 'N', 150, MONTHS), ('A', '9715310', 'N', 100, MONTHS), ('A', '9811110', 'S', 70, MONTHS),
          ('B', '9722D10', 'N', 140, MONTHS), ('B', '9618201', 'N', 90, MONTHS), ('C', '9715310', 'N', 200, MONTHS[3:]),
          ('D', '9722D10', 'N', 150, MONTHS)]


def row(table_name, **v):
    return [v.get(c, '') for c in COLS[table_name]]


def kanban(p, per, st, gs, as_, src, by, dt, created=('FID Rayhan', '01-Jun-2026 09:00'), gt='', ap='', run=''):
    """gs / as_ = GTOPAS / AP POLE Sync Status ('0' No Sync, '3' Sent)."""
    d = PARTS[p]
    return row('TB_M_PART_CANDIDATE', PART_NO=p, PERIOD=per, PART_NAME=d['name'], MIN_MAD=d['min'], PCS_CASE=d['pcs'], MAX_CASE_DAY=d['max'],
               TOTAL_PCS_DAY=d['pcs'] * d['max'], EFFECTIVE_START_DATE=d['eff'], PART_STATUS=st, GTOPAS_SYNC_STATUS=ST[gs], GTOPAS_SYNC_DT=gt,
               APPOLE_SYNC_STATUS=ST[as_], APPOLE_SYNC_DT=ap, SYNC_RUN_ID=run,
               LAST_SOURCE=src, LAST_UPLOAD_ID='', CREATED_BY=created[0], CREATED_DT=created[1], CHANGED_BY=by, CHANGED_DT=dt)


def dest(p, per, code, ot, cd, by, dt, created=None):
    created = created or (by, dt)
    return row('TB_M_PART_CANDIDATE_DEST', PART_NO=p, PERIOD=per, DEST_CODE=code, ORDER_TYPE=ot, CASE_DAY=cd, CREATED_BY=created[0], CREATED_DT=created[1],
               CHANGED_BY=by, CHANGED_DT=dt)


HID = [100]


def hist(p, per, ev, src, field, old, new, remark='', code='', by=BATCH, dt=RUN):
    HID[0] += 1
    return row('TB_H_PART_CANDIDATE', HIST_ID=HID[0], PART_NO=p, PERIOD=per, EVENT_TYPE=ev, SOURCE=src, UPLOAD_ID='', DEST_CODE=code, ORDER_TYPE='**' if code else '',
               FIELD_NAME=field, OLD_VALUE=old, NEW_VALUE=new, REMARK=remark, CREATED_BY=by, CREATED_DT=dt)


def log(bid, run, dt, by, per, parts):
    """Log record of a send run (existing Log table, 20-Nov)."""
    return [bid, run, dt, by, per, parts, 'SENT']


def allocate(mads, mx):
    """XD05 4.6: keep at most mx destinations, target = share x mx, floor (min 1), +1 to the largest fraction until total = mx."""
    keep = sorted(mads, key=lambda x: -x[1])[:mx]
    tot = sum(m for _, m in keep)
    rows = [[d, m, m / tot * mx] for d, m in keep]
    for r in rows:
        r.append(max(1, math.floor(r[2])))
    while sum(r[3] for r in rows) < mx:
        r = max(rows, key=lambda x: (x[2] - math.floor(x[2]), x[1]))
        r[3] += 1
        r[2] = math.floor(r[2])            # fraction used once
    return [(d, m, round(m / tot * mx, 4), c) for d, m, _, c in rows]


def step(ws, r, txt):
    ws.cell(r, 1, txt).font = Font(name='Arial', size=11, bold=True)
    for c in range(1, 21):
        ws.cell(r, c).fill = PatternFill('solid', fgColor='D9E1F2')
    return r + 2


def note(ws, r, lines):
    for t in lines:
        ws.cell(r, 1, t).font = Font(name='Arial', size=9, italic=True)
        r += 1
    return r + 1


def block(ws, r, title, cols, rows, fills=None):
    ws.cell(r, 1, title).font = Font(name='Arial', size=10, bold=True)
    return table(ws, r + 1, cols, rows, [max(10, min(26, len(c) + 3)) for c in cols], fills)




AP_COLS = ['Eff. MM', 'Eff. YYYY', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Buyer PD', 'Order Type',
           'Max Shipping Box Qty (Buyer PD)', 'Max Allowance Qty (Buyer PD)', 'Action of XD07']
GT_COLS = ['P/No.', 'Destination Code', 'Maker', 'Dom/Os', 'TOPAS Order Type', 'Trans']
OLD = ('FID Rayhan', '01-Jun-2026 09:00')
T27, S27, R1 = '27-Nov-2026 09:00', '27-Nov-2026 10:00', '01-Dec-2026 00:10'
RUN27, RUN1 = '20261127100000', '20261201001000'


def ap_rows(mm, part, dests, action):
    d = PARTS[part]
    return [[mm, '2026', part, d['pcs'], d['max'], d['pcs'] * d['max'], BP[c], o, cd, d['pcs'] * cd, action] for c, o, cd in dests]


def main():
    wb = Workbook()
    wb.remove(wb.active)
    ax = [1]

    def fills(n, f):
        return {i: f for i in range(1, n + 1)}

    # ---------- 0. overview ----------
    ws, r = sheet(wb, '0. Overview', 'Full flow with the ERD tables: Crossdock Master -> DAD calculation -> AP POLE -> Period Rollover -> GTOPAS', [
        'Current period 202611 (Nov), day D = 27-Nov-2026 (XD05, system master), Next period 202612, Period Rollover 01-Dec-2026, N = 6 months 202605-202610.',
        'Every table shows all its columns (same source as the ERD / DB Structure). Yellow = inserted / changed in the step, red = deleted, green = kept / done.',
        'PROPOSAL (20-Nov, discussion, not yet in the UISS): one Sync Status per target on TB_M_PART_CANDIDATE: GTOPAS_SYNC_STATUS + GTOPAS_SYNC_DT, '
        'APPOLE_SYNC_STATUS + APPOLE_SYNC_DT (instead of one SYNC_STATUS). No response from the RPA: 0 No Sync / 3 Sent; the result comes by e-mail.'])
    r = block(ws, r, 'Rules of the two statuses', ['Change', 'GTOPAS', 'AP POLE'], [
        ['Status Active <-> Inactive, Candidate -> Active', 'No Sync', 'No Sync'],
        ['Destination added / removed', 'No Sync', 'No Sync'],
        ['Case/Day or Order Type of a destination, Pcs/Case, Max Case/Day', 'Not changed (no quantity in GTOPAS)', 'No Sync'],
        ['Min MAD, Effective Start Date, Save without change', 'Not changed', 'Not changed'],
        ['XD05 makes the Next row', 'Copied from Current when the part + destination combination and the status are equal (option b), else No Sync',
         'No Sync (AP POLE needs the record of the new Effective month)'],
        ['[Sync]', 'Current: No Sync -> Sent (XD06). Next: waits for the Period Rollover', 'No Sync -> Sent for Current and Next (XD07: Current first)'],
        ['Period Rollover (day 1)', 'Next rows No Sync -> Sent (XD06 starts)', 'Not touched: stays Sent']])
    r = block(ws, r, 'Steps', ['Sheet', 'When', 'Function'], [
        ['1', '-', 'Input: TB_R_ACTUAL_DEMAND_SUMMARY (XD04), destinations'], ['2', '20-Nov', 'Before day D: only 202611'],
        ['3', '27-Nov 02:00', 'XD05 process 1: DAD result, Kanban Crossdock Master 202612'], ['4', '27-Nov 02:00', 'XD05 process 2: Export Crossdock Master 202612'],
        ['5', '27-Nov 09:00', 'D/S adjusts the Current period 202611 on the screen (Case/Day of A)'],
        ['6', '27-Nov 10:00', '[Sync]: XD07 AP POLE 11/2026 (Current) then 12/2026 (Next); GTOPAS: nothing (no GTOPAS No Sync in Current)'],
        ['7', '01-Dec 00:10', 'Period Rollover -> XD06 GTOPAS for the Next rows with GTOPAS No Sync'], ['8', '01-Dec', 'End state']])
    block(ws, r, 'Parts of the example', ['Part', 'Nov status', 'Min MAD', 'Pcs/Case', 'Max Case/Day', 'Story'], [
        ['A', 'Active', 300, 6, 12, 'Stays Active; Nov adjusted on 27-Nov (Case/Day); Dec mapping changes (TW added)'],
        ['B', 'Candidate', 200, 10, 6, 'Candidate -> Active for Dec (new in GTOPAS and AP POLE)'],
        ['C', 'Active', 500, 8, 10, 'Active -> Inactive for Dec (deleted in GTOPAS on 1-Dec; no 12/2026 record in AP POLE)'],
        ['D', 'Active', 100, 4, 8, 'No change at all: GTOPAS status of Dec copied (Sent), AP POLE 12/2026 still sent']])

    # ---------- 1. input ----------
    ws, r = sheet(wb, '1. Input', 'Input: TB_R_ACTUAL_DEMAND_SUMMARY (from XD04) and the destination master', [
        'One row per buyer + PD + order type group + month + part. Columns not used by Crossdock stay empty.'])
    dem = []
    for p, code, og, mad, months in DEMAND:
        for m in months:
            dem.append(row('TB_R_ACTUAL_DEMAND_SUMMARY', GROUPING_BUYER_CD=code[:5], GROUPING_PD_CD=code[5:], ORDER_TYPE_GROUP=og, DEMAND_MONTH_YEAR=m,
                           PART_NO=p, MAD=mad, DAD=round(mad / 20, 2), CREATE_DT='01-' + m[4:] + '-2026', CREATE_BY='XD04'))
    r = block(ws, r, 'TB_R_ACTUAL_DEMAND_SUMMARY (range 202605 - 202610)', COLS['TB_R_ACTUAL_DEMAND_SUMMARY'], dem)
    block(ws, r, 'TB_M_H0125_DESTINATION (key columns used)', ['DESTINATION_CD', 'Name in this example', 'Buyer PD in AP POLE'],
          [[c, n, BP[c]] for c, n in DEST.items()])

    # ---------- 2. before ----------
    sent_nov = dict(gt='01-Nov-2026 00:10', ap='27-Oct-2026 10:30', run='20261027103000')
    ws, r = sheet(wb, '2. Before 20-Nov', 'Before day D: only the Current period 202611', [])
    kan_cur = {'A': kanban('A', CUR, 'Active', '3', '3', 'CALC', DS, '27-Oct-2026 10:30', **sent_nov),
               'B': kanban('B', CUR, 'Candidate', '0', '0', 'SCREEN', DS, '10-Nov-2026 09:15', (DS, '10-Nov-2026 09:15')),
               'C': kanban('C', CUR, 'Active', '3', '3', 'CALC', DS, '27-Oct-2026 10:30', **sent_nov),
               'D': kanban('D', CUR, 'Active', '3', '3', 'CALC', DS, '27-Oct-2026 10:30', **sent_nov)}
    r = block(ws, r, 'TB_M_PART_CANDIDATE (Kanban Crossdock Master)', COLS['TB_M_PART_CANDIDATE'], list(kan_cur.values()))
    dcur = [dest(p, CUR, c, o, cd, BATCH, '27-Oct-2026 02:00') for p, c, o, cd in CUR_MAP]
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST (Export Crossdock Master)', COLS['TB_M_PART_CANDIDATE_DEST'], dcur)
    r = block(ws, r, 'GTOPAS WVJA5204 (Depot 01)', GT_COLS, [[p, c, 'A', '2', '3', '2'] for p, c, _, _ in CUR_MAP])
    block(ws, r, 'AP POLE 11/2026', AP_COLS, [x for p in ('A', 'C', 'D') for x in ap_rows('11', p, [(c, o, cd) for q, c, o, cd in CUR_MAP if q == p], '-')])

    # ---------- 3. XD05 process 1 ----------
    ws, r = sheet(wb, '3. XD05 P1 27-Nov', 'XD05 process 1 (27-Nov 02:00, day D): average MAD and status for the Next period 202612', [
        'Range = the N = 6 months before the run month: 202605 - 202610. AVG_MAD = total MAD / 6. AVG_MAD >= MIN_MAD -> Active, else Inactive.'])
    calc, dad, newst = [], [], {}
    for p, d in PARTS.items():
        per_m = [sum(x[3] for x in DEMAND if x[0] == p and m in x[4]) for m in MONTHS]
        tot = sum(per_m)
        avg = round(tot / N, 2)
        st = 'Active' if avg >= d['min'] else 'Inactive'
        newst[p] = st
        calc.append([p, *per_m, tot, avg, d['min'], d['st'], st])
        dad.append(row('TB_R_PART_DAD_RESULT', PERIOD=NXT, PART_NO=p, MONTH_FROM=MONTHS[0], MONTH_TO=MONTHS[-1], NUM_OF_MONTH=N, TOTAL_MAD=tot,
                       AVG_MAD=avg, MIN_MAD=d['min'], OLD_STATUS=d['st'], NEW_STATUS=st, CREATED_BY=BATCH, CREATED_DT=RUN))
    r = block(ws, r, 'Calculation', ['PART_NO', *MONTHS, 'TOTAL_MAD', 'AVG_MAD', 'MIN_MAD', 'Status 202611', 'Status 202612'], calc, {2: NEW, 3: DEL})
    r = block(ws, r, 'TB_R_PART_DAD_RESULT (inserted)', COLS['TB_R_PART_DAD_RESULT'], dad, fills(len(dad), NEW))
    h_calc = [hist(p, NXT, 'CALC', 'BATCH', 'PART_STATUS', PARTS[p]['st'], newst[p]) for p in PARTS if PARTS[p]['st'] != newst[p]]
    r = block(ws, r, 'TB_H_PART_CANDIDATE (status changes)', COLS['TB_H_PART_CANDIDATE'], h_calc, fills(len(h_calc), NEW))
    r = note(ws, r, ['The Kanban rows of 202612 are inserted with process 2 (sheet 4), after the mapping is known (needed for the GTOPAS status copy).'])

    # ---------- 4. XD05 process 2 ----------
    ws, r = sheet(wb, '4. XD05 P2 27-Nov', 'XD05 process 2 (27-Nov 02:00): Export Crossdock Master 202612 and the Kanban rows 202612', [
        'Case/Day = share of Max Case/Day, rounded down (min 1), +1 to the largest fraction. Order Type of a new row = **.'])
    alloc_rows, dnxt = [], []
    for p in PARTS:
        if newst[p] != 'Active':
            continue
        mads = {}
        for q, code, _, mad, months in DEMAND:
            if q == p:
                mads[code] = mads.get(code, 0) + mad * len(months)
        for code, m, tgt, cd in allocate(list(mads.items()), PARTS[p]['max']):
            alloc_rows.append([p, code, DEST[code], m, tgt, cd])
            dnxt.append(dest(p, NXT, code, '**', cd, BATCH, RUN))
    r = block(ws, r, 'Allocation', ['PART_NO', 'DEST_CODE', 'Name', 'Result MAD', 'Target (share x Max)', 'CASE_DAY'], alloc_rows)
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST (inserted: 202612)', COLS['TB_M_PART_CANDIDATE_DEST'], dnxt, fills(len(dnxt), NEW))
    combo_cur = {p: {c for q, c, _, _ in CUR_MAP if q == p} for p in PARTS}
    combo_nxt = {p: {x[2] for x in dnxt if x[0] == p} for p in PARTS}
    same = {p: combo_cur[p] == combo_nxt[p] and PARTS[p]['st'] == newst[p] for p in PARTS}
    cmp_rows = [[p, PARTS[p]['st'], newst[p], ', '.join(sorted(DEST[c] for c in combo_cur[p])) or '-', ', '.join(sorted(DEST[c] for c in combo_nxt[p])) or '-',
                 'Equal: GTOPAS copied (Sent)' if same[p] else 'Different: GTOPAS No Sync', 'No Sync (new Effective month)'] for p in PARTS]
    r = block(ws, r, 'Status of the new rows (compare 202612 with 202611)', ['PART_NO', 'Status 202611', 'Status 202612', 'Destinations 202611',
                                                                             'Destinations 202612', 'GTOPAS_SYNC_STATUS', 'APPOLE_SYNC_STATUS'], cmp_rows,
              {i: (KEEP if same[x[0]] else NEW) for i, x in enumerate(cmp_rows, 1)})
    kan_nxt = {p: kanban(p, NXT, newst[p], '3' if same[p] else '0', '0', 'CALC', BATCH, RUN, (BATCH, RUN),
                         gt=sent_nov['gt'] if same[p] else '', run='') for p in PARTS}
    r = block(ws, r, 'TB_M_PART_CANDIDATE (inserted: Next period 202612)', COLS['TB_M_PART_CANDIDATE'], list(kan_nxt.values()), fills(len(PARTS), NEW))
    prev = {(p, c): cd for p, c, _, cd in CUR_MAP}
    nxt = {(x[0], x[2]): x[4] for x in dnxt}
    h_map = [hist(k[0], NXT, 'MAPPING', 'BATCH', 'CASE_DAY', prev.get(k, ''), nxt.get(k, ''), code=k[1],
                  remark='added' if k not in prev else 'removed' if k not in nxt else 'changed') for k in sorted(set(prev) | set(nxt)) if prev.get(k) != nxt.get(k)]
    block(ws, r, 'TB_H_PART_CANDIDATE (mapping compared with 202611)', COLS['TB_H_PART_CANDIDATE'], h_map, fills(len(h_map), NEW))

    # ---------- 5. adjust Current ----------
    ws, r = sheet(wb, '5. Adjust 27-Nov', 'D/S adjusts the Current period 202611 of part A on the Export Crossdock Master: JPN 6 -> 7, KR 6 -> 5', [
        'Only the Case/Day changes (same destinations): AP POLE No Sync for 202611; GTOPAS stays Sent (GTOPAS keeps no quantity).'])
    dadj = [dest('A', CUR, '9722D10', '**', 7, DS, T27, (BATCH, '27-Oct-2026 02:00')), dest('A', CUR, '9715310', '**', 5, DS, T27, (BATCH, '27-Oct-2026 02:00'))]
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST 202611 of A (updated)', COLS['TB_M_PART_CANDIDATE_DEST'], dadj, fills(2, NEW))
    kan_cur['A'] = kanban('A', CUR, 'Active', '3', '0', 'SCREEN', DS, T27, gt=sent_nov['gt'], ap=sent_nov['ap'], run=sent_nov['run'])
    r = block(ws, r, 'TB_M_PART_CANDIDATE 202611 of A (APPOLE_SYNC_STATUS -> No Sync)', COLS['TB_M_PART_CANDIDATE'], [kan_cur['A']], {1: NEW})
    block(ws, r, 'TB_H_PART_CANDIDATE', COLS['TB_H_PART_CANDIDATE'],
          [hist('A', CUR, 'MAPPING', 'SCREEN', 'CASE_DAY', 6, 7, code='9722D10', by=DS, dt=T27), hist('A', CUR, 'MAPPING', 'SCREEN', 'CASE_DAY', 6, 5, code='9715310', by=DS, dt=T27)],
          fills(2, NEW))

    # ---------- 6. Sync ----------
    ws, r = sheet(wb, '6. Sync 27-Nov', '[Sync] 27-Nov 10:00: rows with a target No Sync (Current and Next; GTOPAS of Next waits for 1-Dec)', [
        'GTOPAS: no Current row is GTOPAS No Sync -> XD06 does not run. AP POLE: 202611 A, then 202612 A, B, C, D -> XD07 (Current first, then Next).',
        'NSP writes the send before the bot starts; the bot writes nothing back (result by e-mail).'])
    shown = [kanban('A', CUR, 'Active', '3', '0>3', 'SCREEN', DS, S27, gt=sent_nov['gt'], ap=S27, run=RUN27)] + [
        kanban(p, NXT, newst[p], '3' if same[p] else '0', '0>3', 'CALC', DS, S27, (BATCH, RUN), gt=sent_nov['gt'] if same[p] else '', ap=S27, run=RUN27)
        for p in PARTS]
    r = block(ws, r, 'TB_M_PART_CANDIDATE: status before -> after [Sync] (202611 A and 202612 all)', COLS['TB_M_PART_CANDIDATE'], shown, fills(5, NEW))
    kan_cur['A'] = kanban('A', CUR, 'Active', '3', '3', 'SCREEN', DS, S27, gt=sent_nov['gt'], ap=S27, run=RUN27)
    for p in PARTS:
        kan_nxt[p] = kanban(p, NXT, newst[p], '3' if same[p] else '0', '3', 'CALC', DS, S27, (BATCH, RUN), gt=sent_nov['gt'] if same[p] else '', ap=S27, run=RUN27)
    sent_dest = dadj + [x for x in dnxt]
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST rows sent with these parts (read only; the Sync Status is kept on the part row above)',
              COLS['TB_M_PART_CANDIDATE_DEST'], sent_dest, fills(len(sent_dest), NEW))
    r = note(ws, r, ['The Export Crossdock Master (destinations) has no Sync Status of its own: a change of a destination (here A 202611 JPN 6 -> 7, '
                     'KR 6 -> 5 on sheet 5) sets the part row to AP POLE No Sync, and the bot sends the part with all its destinations of that period.'])
    r = block(ws, r, 'TB_H_PART_CANDIDATE (SYNC)', COLS['TB_H_PART_CANDIDATE'],
              [hist('A', CUR, 'SYNC', 'SCREEN', 'APPOLE_SYNC_STATUS', 'No Sync', 'Sent', 'APPOLE: ' + RUN27, by=DS, dt=S27)] +
              [hist(p, NXT, 'SYNC', 'SCREEN', 'APPOLE_SYNC_STATUS', 'No Sync', 'Sent', 'APPOLE: ' + RUN27, by=DS, dt=S27) for p in PARTS])
    r = block(ws, r, 'Log', LOG_COLS, [log('XD07_RPA_APPOLE', RUN27, S27, DS, '202611, 202612', 5)], {1: NEW})
    ap11 = ap_rows('11', 'A', [('9722D10', '**', 7)], 'Edit Max Shipping Box Qty 6 -> 7') + ap_rows('11', 'A', [('9715310', '**', 5)], 'Edit Max Shipping Box Qty 6 -> 5')
    r = block(ws, r, 'AP POLE 1st: Eff. 11/2026 (Current)', AP_COLS, ap11, fills(2, NEW))
    ap12 = []
    for p in PARTS:
        if newst[p] == 'Active':
            ap12 += ap_rows('12', p, [(x[2], x[3], x[4]) for x in dnxt if x[0] == p], 'Add')
    r = block(ws, r, 'AP POLE 2nd: Eff. 12/2026 (Next; C Inactive: no record)', AP_COLS, ap12, fills(len(ap12), NEW))
    note(ws, r, ['Result: e-mail [Crossdock Sync][AP POLE][SUCCESS] Run ' + RUN27 + ' - 5 part(s) with the work file AP POLE Compare.'])

    # ---------- 7. Rollover ----------
    ws, r = sheet(wb, '7. Rollover 1-Dec', 'Period Rollover (01-Dec 00:10): 202612 Current, 202611 Past; XD06 for the 202612 rows with GTOPAS No Sync', [
        'AP POLE status and date are not touched (stay Sent 27-Nov). D was copied (GTOPAS Sent) on day D, so it is not sent again.'])
    send = [p for p in PARTS if not same[p]]
    shown = [kanban(p, NXT, newst[p], '0>3', '3', 'CALC', BATCH, R1, (BATCH, RUN), gt=R1, ap=S27, run=RUN1) if p in send else kan_nxt[p] for p in PARTS]
    for p in send:
        kan_nxt[p] = kanban(p, NXT, newst[p], '3', '3', 'CALC', BATCH, R1, (BATCH, RUN), gt=R1, ap=S27, run=RUN1)
    r = block(ws, r, 'TB_M_PART_CANDIDATE 202612: GTOPAS before -> after (AP POLE unchanged: stays 3 Sent)', COLS['TB_M_PART_CANDIDATE'], shown,
              {i: (NEW if p in send else KEEP) for i, p in enumerate(PARTS, 1)})
    r = block(ws, r, 'TB_H_PART_CANDIDATE (SYNC)', COLS['TB_H_PART_CANDIDATE'],
              [hist(p, NXT, 'SYNC', 'BATCH', 'GTOPAS_SYNC_STATUS', 'No Sync', 'Sent', 'GTOPAS: ' + RUN1, by=BATCH, dt=R1) for p in send])
    r = block(ws, r, 'Log', LOG_COLS, [log('XD06_RPA_GTOPAS', RUN1, R1, BATCH, NXT, len(send))], {1: NEW})
    cur_c = {(p, c) for p, c, _, _ in CUR_MAP}
    nxt_c = {(x[0], x[2]) for x in dnxt}
    work = [[p, c, 'Y' if (p, c) in nxt_c else 'N', 'Y' if (p, c) in cur_c else 'N',
             'Keep' if (p, c) in cur_c and (p, c) in nxt_c else 'Add' if (p, c) in nxt_c else 'Delete'] for p, c in sorted(cur_c | nxt_c) if p in send]
    r = block(ws, r, 'Work sheet GTOPAS Compare (parts of the run: A, B, C)', ['P/No.', 'Destination Code', 'In NSP 202612', 'In GTOPAS', 'Action'], work,
              {i: {'Keep': KEEP, 'Add': NEW, 'Delete': DEL}[x[4]] for i, x in enumerate(work, 1)})
    gt_after = sorted(nxt_c)
    block(ws, r, 'GTOPAS WVJA5204 after XD06 (D not touched)', GT_COLS, [[p, c, 'A', '2', '3', '2'] for p, c in gt_after],
          {i: (KEEP if k in cur_c else NEW) for i, k in enumerate(gt_after, 1)})

    # ---------- 8. end state ----------
    ws, r = sheet(wb, '8. End state 1-Dec', 'End state after 1-Dec (202612 = Current, 202611 = Past)', [])
    r = block(ws, r, 'TB_M_PART_CANDIDATE', COLS['TB_M_PART_CANDIDATE'], list(kan_cur.values()) + list(kan_nxt.values()))
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST', COLS['TB_M_PART_CANDIDATE_DEST'],
              [x for x in dcur if x[0] != 'A'] + dadj + dnxt)
    r = block(ws, r, 'TB_R_PART_DAD_RESULT', COLS['TB_R_PART_DAD_RESULT'], dad)
    block(ws, r, 'Log', LOG_COLS, [log('XD07_RPA_APPOLE', '20261027103000', '27-Oct-2026 10:30', DS, CUR, 3),
                                   log('XD06_RPA_GTOPAS', '20261101001000', '01-Nov-2026 00:10', BATCH, CUR, 3),
                                   log('XD07_RPA_APPOLE', RUN27, S27, DS, '202611, 202612', 5),
                                   log('XD06_RPA_GTOPAS', RUN1, R1, BATCH, NXT, len(send))])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
