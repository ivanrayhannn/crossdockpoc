"""Simulation (19-Nov) with the full tables of the ERD: Crossdock Master -> DAD calculation (XD05 process 1 + 2 on day D) -> [Sync]
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
                                             'TB_R_PART_DAD_RESULT', 'TB_H_PART_CANDIDATE', 'TB_R_CROSSDOCK_IF_RESULT')}
CUR, NXT, RUN, ROLL = '202611', '202612', '27-Nov-2026 02:00', '01-Dec-2026 00:10'
MONTHS = ['202605', '202606', '202607', '202608', '202609', '202610']
N = len(MONTHS)
DEST = {'9722D10': 'JPN', '9715310': 'KR', '9811110': 'TW', '9618201': 'US'}
BP = {'9722D10': '9722D-10', '9715310': '97153-10', '9811110': '98111-10', '9618201': '96182-01'}
BATCH, DS, RPA = 'XD05BATCH', 'D.Anggraini', 'RPABOT'

# parts in the Current period 202611 (Kanban Crossdock Master)
PARTS = {'A': dict(name='Part A', min=300, pcs=6, max=12, st='Active', eff='01-Jun-2026'),
         'B': dict(name='Part B', min=200, pcs=10, max=6, st='Candidate', eff='15-Nov-2026'),
         'C': dict(name='Part C', min=500, pcs=8, max=10, st='Active', eff='01-Jun-2026')}
CUR_MAP = [('A', '9722D10', '**', 6), ('A', '9715310', '**', 6), ('C', '9715310', '**', 10)]
# demand per month (part, dest, order type group, MAD) for every month of the range; C only 3 months
DEMAND = [('A', '9722D10', 'N', 150, MONTHS), ('A', '9715310', 'N', 100, MONTHS), ('A', '9811110', 'S', 70, MONTHS),
          ('B', '9722D10', 'N', 140, MONTHS), ('B', '9618201', 'N', 90, MONTHS), ('C', '9715310', 'N', 200, MONTHS[3:])]


def row(table_name, **v):
    return [v.get(c, '') for c in COLS[table_name]]


def kanban(p, per, st, sync, src, by, dt, created=('FID Rayhan', '01-Jun-2026 09:00')):
    d = PARTS[p]
    return row('TB_M_PART_CANDIDATE', PART_NO=p, PERIOD=per, PART_NAME=d['name'], MIN_MAD=d['min'], PCS_CASE=d['pcs'], MAX_CASE_DAY=d['max'],
               TOTAL_PCS_DAY=d['pcs'] * d['max'], EFFECTIVE_START_DATE=d['eff'], PART_STATUS=st, SYNC_STATUS=sync, SYNC_DT='', SYNC_MESSAGE='',
               LAST_SOURCE=src, LAST_UPLOAD_ID='', CREATED_BY=created[0], CREATED_DT=created[1], CHANGED_BY=by, CHANGED_DT=dt)


def dest(p, per, code, ot, cd, by, dt):
    return row('TB_M_PART_CANDIDATE_DEST', PART_NO=p, PERIOD=per, DEST_CODE=code, ORDER_TYPE=ot, CASE_DAY=cd, CREATED_BY=by, CREATED_DT=dt,
               CHANGED_BY=by, CHANGED_DT=dt)


HID = [100]


def hist(p, per, ev, src, field, old, new, remark='', code='', by=BATCH, dt=RUN):
    HID[0] += 1
    return row('TB_H_PART_CANDIDATE', HIST_ID=HID[0], PART_NO=p, PERIOD=per, EVENT_TYPE=ev, SOURCE=src, UPLOAD_ID='', DEST_CODE=code,
               FIELD_NAME=field, OLD_VALUE=old, NEW_VALUE=new, REMARK=remark, CREATED_BY=by, CREATED_DT=dt)


def ifr(p, tgt, per, st, dt='', last='', run='', msg='', by=DS, cdt=RUN):
    return row('TB_R_CROSSDOCK_IF_RESULT', PART_NO=p, TARGET_SYSTEM=tgt, PERIOD=per, IF_STATUS=st, IF_DT=dt, LAST_SYNC_DT=last, IF_FILE_NAME=run,
               IF_MESSAGE=msg, CREATED_BY=by, CREATED_DT=cdt, CHANGED_BY=by, CHANGED_DT=cdt)


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


def main():
    wb = Workbook()
    wb.remove(wb.active)

    # ---------- 0. overview ----------
    ws, r = sheet(wb, '0. Overview', 'Full flow with the ERD tables: Crossdock Master -> DAD calculation -> AP POLE -> Period Rollover -> GTOPAS', [
        'Current period 202611 (Nov), day D = 27-Nov-2026 (XD05, system master), Next period 202612, Period Rollover 01-Dec-2026, N = 6 months 202605-202610.',
        'Every table shows all its columns (same source as the ERD / DB Structure). Yellow = inserted / changed in the step, red = deleted, green = kept / done. '
        'No response from the RPA (20-Nov): Sync Status / IF_STATUS 0 No Sync or 3 Sent; the result comes by e-mail.'])
    r = block(ws, r, 'Steps', ['Sheet', 'When', 'Function', 'Tables written'], [
        ['1', '-', 'Input', 'TB_R_ACTUAL_DEMAND_SUMMARY (XD04), destination master'],
        ['2', '20-Nov', 'Before', 'TB_M_PART_CANDIDATE / _DEST 202611, TB_R_CROSSDOCK_IF_RESULT 202611, GTOPAS, AP POLE 11/2026'],
        ['3', '27-Nov 02:00', 'XD05 process 1 (DAD / status)', 'TB_R_PART_DAD_RESULT, TB_M_PART_CANDIDATE 202612, TB_H_PART_CANDIDATE (CALC)'],
        ['4', '27-Nov 02:00', 'XD05 process 2 (mapping)', 'TB_M_PART_CANDIDATE_DEST 202612, TB_H_PART_CANDIDATE (MAPPING), TB_R_CROSSDOCK_IF_RESULT (APPOLE 202612)'],
        ['5', '27-Nov 10:00', '[Sync] -> XD07 AP POLE (Next)', 'TB_R_CROSSDOCK_IF_RESULT, TB_M_PART_CANDIDATE, TB_H_PART_CANDIDATE (SYNC); AP POLE 12/2026'],
        ['6', '01-Dec 00:10', 'XD05 process 3 Period Rollover -> XD06 GTOPAS', 'TB_R_CROSSDOCK_IF_RESULT (GTOPAS 202612), TB_H_PART_CANDIDATE (SYNC); GTOPAS'],
        ['7', '01-Dec', 'End state', 'All tables']])
    block(ws, r, 'Parts of the example', ['Part', 'Nov status', 'Min MAD', 'Pcs/Case', 'Max Case/Day', 'Story'], [
        ['A', 'Active', 300, 6, 12, 'Stays Active; Dec mapping changes (TW added, JPN / KR Case/Day changed)'],
        ['B', 'Candidate', 200, 10, 6, 'Candidate -> Active for Dec (new in GTOPAS and AP POLE)'],
        ['C', 'Active', 500, 8, 10, 'Active -> Inactive for Dec (deleted in GTOPAS on 1-Dec; no 12/2026 record in AP POLE)']])

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
    ws, r = sheet(wb, '2. Before 20-Nov', 'Before day D: only the Current period 202611', [])
    kan_cur = [kanban('A', CUR, 'Active', '3', 'CALC', BATCH, '27-Oct-2026 02:00'), kanban('B', CUR, 'Candidate', '0', 'SCREEN', DS, '10-Nov-2026 09:15',
                                                                                           (DS, '10-Nov-2026 09:15')),
               kanban('C', CUR, 'Active', '3', 'CALC', BATCH, '27-Oct-2026 02:00')]
    r = block(ws, r, 'TB_M_PART_CANDIDATE (Kanban Crossdock Master)', COLS['TB_M_PART_CANDIDATE'], kan_cur)
    dcur = [dest(p, CUR, c, o, cd, BATCH, '27-Oct-2026 02:00') for p, c, o, cd in CUR_MAP]
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST (Export Crossdock Master)', COLS['TB_M_PART_CANDIDATE_DEST'], dcur)
    ifcur = [ifr(p, t, CUR, '3', '27-Oct-2026 10:30', '27-Oct-2026 10:30' if t == 'APPOLE' else '01-Nov-2026 00:40', 'RUN' + ('20261027103000' if t == 'APPOLE' else '20261101004000'),
                 by=RPA, cdt='27-Oct-2026 10:30') for p in ('A', 'C') for t in ('GTOPAS', 'APPOLE')]
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT', COLS['TB_R_CROSSDOCK_IF_RESULT'], ifcur)
    r = block(ws, r, 'GTOPAS WVJA5204 (Depot 01)', ['P/No.', 'Destination Code', 'Maker', 'Dom/Os', 'TOPAS Order Type', 'Trans'],
              [[p, c, 'A', '2', '3', '2'] for p, c, _, _ in CUR_MAP])
    block(ws, r, 'AP POLE 11/2026 (WLM9Q890 part / WLM9Q860 Buyer PD)', ['Eff. MM', 'Eff. YYYY', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty',
                                                                      'Buyer PD', 'Order Type', 'Max Shipping Box Qty (Buyer PD)'],
          [['11', '2026', p, PARTS[p]['pcs'], PARTS[p]['max'], BP[c], o, cd] for p, c, o, cd in CUR_MAP])

    # ---------- 3. XD05 process 1 ----------
    ws, r = sheet(wb, '3. XD05 P1 27-Nov', 'XD05 process 1 (27-Nov 02:00, day D): average MAD and status for the Next period 202612', [
        'Range = the N = 6 months before the run month: 202605 - 202610. AVG_MAD = total MAD / 6 (a month without data counts as 0).',
        'Status rule: AVG_MAD >= MIN_MAD -> Active, else Inactive. Candidate B is calculated (Effective Start 15-Nov <= run date).'])
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
    r = block(ws, r, 'Calculation (monthly MAD = all destinations and order types)', ['PART_NO', *MONTHS, 'TOTAL_MAD', 'AVG_MAD', 'MIN_MAD', 'Status 202611', 'Status 202612'],
              calc, {2: NEW, 3: DEL})
    r = block(ws, r, 'TB_R_PART_DAD_RESULT (inserted)', COLS['TB_R_PART_DAD_RESULT'], dad, {1: NEW, 2: NEW, 3: NEW})
    kan_nxt = [kanban(p, NXT, newst[p], '0', 'CALC', BATCH, RUN, (BATCH, RUN)) for p in PARTS]
    r = block(ws, r, 'TB_M_PART_CANDIDATE (inserted: Next period 202612; status from the result, Pcs/Case and Max Case/Day copied from 202611)',
              COLS['TB_M_PART_CANDIDATE'], kan_nxt, {1: NEW, 2: NEW, 3: NEW})
    h_calc = [hist(p, NXT, 'CALC', 'BATCH', 'PART_STATUS', PARTS[p]['st'], newst[p]) for p in PARTS if PARTS[p]['st'] != newst[p]]
    r = block(ws, r, 'TB_H_PART_CANDIDATE (status changes)', COLS['TB_H_PART_CANDIDATE'], h_calc, {i: NEW for i in range(1, len(h_calc) + 1)})
    note(ws, r, ['The Current period 202611 is not changed: B stays Candidate and C stays Active until 1-Dec.'])

    # ---------- 4. XD05 process 2 ----------
    ws, r = sheet(wb, '4. XD05 P2 27-Nov', 'XD05 process 2 (27-Nov 02:00): Export Crossdock Master of the Next period 202612 (Active parts only)', [
        'Result MAD per destination = sum of MAD of the range (order types N + S). Case/Day = share of Max Case/Day, rounded down (min 1), '
        '+1 to the largest fraction until the total = Max Case/Day. Order Type of a new row = **.'])
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
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST (inserted: Next period 202612)', COLS['TB_M_PART_CANDIDATE_DEST'], dnxt, {i: NEW for i in range(1, len(dnxt) + 1)})
    prev = {(p, c): cd for p, c, _, cd in CUR_MAP}
    nxt = {(x[0], x[2]): x[4] for x in dnxt}
    h_map = []
    for k in sorted(set(prev) | set(nxt)):
        if prev.get(k) != nxt.get(k):
            h_map.append(hist(k[0], NXT, 'MAPPING', 'BATCH', 'CASE_DAY', prev.get(k, ''), nxt.get(k, ''), code=k[1],
                              remark='added' if k not in prev else 'removed' if k not in nxt else 'changed'))
    r = block(ws, r, 'TB_H_PART_CANDIDATE (mapping compared with 202611)', COLS['TB_H_PART_CANDIDATE'], h_map, {i: NEW for i in range(1, len(h_map) + 1)})
    if_n = [ifr(p, 'APPOLE', NXT, '0', by=BATCH) for p in PARTS]
    block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT (inserted: APPOLE 202612 = No Sync; GTOPAS 202612 only on 1-Dec)', COLS['TB_R_CROSSDOCK_IF_RESULT'], if_n,
          {1: NEW, 2: NEW, 3: NEW})

    # ---------- 5. Sync -> XD07 ----------
    ws, r = sheet(wb, '5. XD07 27-Nov', '[Sync] 27-Nov 10:00 -> XD07 RPA AP POLE: Next period 202612 = Effective 12/2026', [
        'Current 202611 has nothing to send, so the bot works on 202612 only. C is Inactive for Dec: no 12/2026 record is made.'])
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT after [Sync] (Sent; no response from the RPA, 20-Nov)', COLS['TB_R_CROSSDOCK_IF_RESULT'], [ifr(p, 'APPOLE', NXT, '3', '27-Nov-2026 10:00', '27-Nov-2026 10:00', 'RUN20261127100000', cdt='27-Nov-2026 10:00')
                                                                                                         for p in PARTS], {1: NEW, 2: NEW, 3: NEW})
    apc = []
    for p in PARTS:
        if newst[p] == 'Active':
            apc.append([p, '-', 'Part', f"{PARTS[p]['pcs']} / {PARTS[p]['max']}", 'not found', 'Add'])
            apc += [[p, BP[x[2]], 'Buyer PD', x[4], 'not found', 'Add'] for x in dnxt if x[0] == p]
        else:
            apc.append([p, '-', 'Part', '(Inactive)', 'not found', 'Nothing'])
    r = block(ws, r, 'Work sheet AP POLE Compare (Eff. 12/2026)', ['Part', 'Buyer PD', 'Level', 'NSP value', 'AP POLE 12/2026', 'Action'], apc,
              {i: (NEW if x[5] == 'Add' else KEEP) for i, x in enumerate(apc, 1)})
    r = block(ws, r, 'AP POLE after XD07 (Eff. 12 / 2026)', ['Eff. MM', 'Eff. YYYY', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty',
                                                              'Buyer PD', 'Order Type', 'Transport Code', 'Max Shipping Box Qty (Buyer PD)', 'Max Allowance Qty (Buyer PD)'],
              [['12', '2026', x[0], PARTS[x[0]]['pcs'], PARTS[x[0]]['max'], PARTS[x[0]]['pcs'] * PARTS[x[0]]['max'], BP[x[2]], x[3], 2, x[4],
                PARTS[x[0]]['pcs'] * x[4]] for x in dnxt], {i: NEW for i in range(1, len(dnxt) + 1)})
    run7 = 'RUN20261127100000'
    r = block(ws, r, 'TB_M_PART_CANDIDATE 202612 (SYNC_STATUS 3 Sent at [Sync])', COLS['TB_M_PART_CANDIDATE'],
              [kanban(p, NXT, newst[p], '3', 'CALC', DS, '27-Nov-2026 10:00', (BATCH, RUN)) for p in PARTS], {1: NEW, 2: NEW, 3: NEW})
    r = block(ws, r, 'TB_H_PART_CANDIDATE (SYNC, written by NSP at [Sync])', COLS['TB_H_PART_CANDIDATE'],
              [hist(p, NXT, 'SYNC', 'SCREEN', 'SYNC_STATUS', 'No Sync', 'Sent', 'APPOLE: ' + run7, by=DS, dt='27-Nov-2026 10:00') for p in PARTS])
    note(ws, r, ['No response from the RPA (20-Nov): the bot writes nothing back to NSP. The result is the e-mail '
                 '[Crossdock Sync][AP POLE][SUCCESS] Run 20261127100000 - 3 part(s) with the work file. When FAILED: [Re-send last Sync].'])

    # ---------- 6. Rollover + XD06 ----------
    ws, r = sheet(wb, '6. Rollover 1-Dec', 'XD05 process 3 Period Rollover (01-Dec 00:10) -> automatic XD06 RPA GTOPAS', [
        '202612 becomes Current, 202611 Past. Parts whose part + destination combination of 202612 differs from 202611 get GTOPAS No Sync, then Sent (XD06 starts).'])
    cur_c = {(p, c) for p, c, _, _ in CUR_MAP}
    nxt_c = {(x[0], x[2]) for x in dnxt}
    cmp_rows = [[p, c, 'Y' if (p, c) in cur_c else 'N', 'Y' if (p, c) in nxt_c else 'N',
                 'Same' if (p, c) in cur_c and (p, c) in nxt_c else 'Added' if (p, c) in nxt_c else 'Removed'] for p, c in sorted(cur_c | nxt_c)]
    r = block(ws, r, 'Compare 202611 vs 202612 (part + destination)', ['PART_NO', 'DEST_CODE', 'In 202611', 'In 202612', 'Result'], cmp_rows,
              {i: {'Same': KEEP, 'Added': NEW, 'Removed': DEL}[x[4]] for i, x in enumerate(cmp_rows, 1)})
    changed = sorted({x[0] for x in cmp_rows if x[4] != 'Same'})
    r = block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT (inserted: GTOPAS 202612 -> Sent, written by the Period Rollover)', COLS['TB_R_CROSSDOCK_IF_RESULT'],
              [ifr(p, 'GTOPAS', NXT, '0 -> 3', '01-Dec-2026 00:10', '01-Dec-2026 00:10', 'RUN20261201001000', by=BATCH, cdt=ROLL) for p in changed], {i: NEW for i in range(1, len(changed) + 1)})
    gt_before = sorted(cur_c)
    work = []
    for p, c in sorted(cur_c | nxt_c):
        if p not in changed:
            continue
        a = 'Keep' if (p, c) in cur_c and (p, c) in nxt_c else 'Add' if (p, c) in nxt_c else 'Delete'
        work.append([p, c, 'Y' if (p, c) in nxt_c else 'N', 'Y' if (p, c) in cur_c else 'N', a])
    r = block(ws, r, 'Work sheet GTOPAS Compare (search per P/No. of the parts sent by the rollover)', ['P/No.', 'Destination Code', 'In NSP 202612', 'In GTOPAS', 'Action'], work,
              {i: {'Keep': KEEP, 'Add': NEW, 'Delete': DEL}[x[4]] for i, x in enumerate(work, 1)})
    gt_after = sorted(nxt_c)
    r = block(ws, r, 'GTOPAS WVJA5204 after XD06', ['P/No.', 'Destination Code', 'Maker', 'Dom/Os', 'TOPAS Order Type', 'Trans'],
              [[p, c, 'A', '2', '3', '2'] for p, c in gt_after], {i: (KEEP if k in cur_c else NEW) for i, k in enumerate(gt_after, 1)})
    run6 = 'RUN20261201001000'
    block(ws, r, 'TB_H_PART_CANDIDATE (SYNC, written by the Period Rollover)', COLS['TB_H_PART_CANDIDATE'],
          [hist(p, NXT, 'SYNC', 'BATCH', 'SYNC_STATUS', 'No Sync', 'Sent', 'GTOPAS: ' + run6, by=BATCH, dt=ROLL) for p in changed])
    note(ws, r + len(changed) + 3, ['The result of XD06 is the e-mail [Crossdock Sync][GTOPAS][SUCCESS | FAILED]; NSP keeps Sent.'])

    # ---------- 7. end state ----------
    ws, r = sheet(wb, '7. End state 1-Dec', 'End state after 1-Dec (202612 = Current, 202611 = Past)', [])
    r = block(ws, r, 'TB_M_PART_CANDIDATE', COLS['TB_M_PART_CANDIDATE'], kan_cur + [kanban(p, NXT, newst[p], '3', 'CALC', DS, '27-Nov-2026 10:00', (BATCH, RUN))
                                                                                for p in PARTS])
    r = block(ws, r, 'TB_M_PART_CANDIDATE_DEST', COLS['TB_M_PART_CANDIDATE_DEST'], dcur + dnxt)
    r = block(ws, r, 'TB_R_PART_DAD_RESULT', COLS['TB_R_PART_DAD_RESULT'], dad)
    block(ws, r, 'TB_R_CROSSDOCK_IF_RESULT', COLS['TB_R_CROSSDOCK_IF_RESULT'], ifcur +
          [ifr(p, 'APPOLE', NXT, '3', '27-Nov-2026 10:00', '27-Nov-2026 10:00', run7, cdt='27-Nov-2026 10:00') for p in PARTS] +
          [ifr(p, 'GTOPAS', NXT, '3', '01-Dec-2026 00:10', '01-Dec-2026 00:10', run6, by=BATCH, cdt=ROLL) for p in changed])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
