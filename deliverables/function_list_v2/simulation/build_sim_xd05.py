"""XD05 DAD Volume Calculation simulation (process 1 and 2) on real actual demand data.

Source: 20261013_tb_r_actual_demand_summary_since_january-2026.xlsx (349,225 rows), extract of 9 parts in
xd05_demand_extract.csv and the list of loads (CREATE_DT) in xd05_loads.csv.
Rules follow UISS XD04 / XD05 (decisions up to 6-Nov). Run: python3 build_sim_xd05.py
"""
import csv, math, os
from collections import defaultdict, OrderedDict
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD05_Simulation_DAD_Volume_Calculation.xlsx')

N = 6
RUN_DATE = '01-Nov-2026'
RUN_MONTH = '202611'
RANGE = ['202605', '202606', '202607', '202608', '202609', '202610']
PREV = '202610'

# Part List before the run (TB_M_PART_CANDIDATE); scenario per part
PARTS = OrderedDict([
    ('52119BZV60', dict(st='Candidate', min=300, pcs=6, max=16, eff='01-Apr-2026', scen='Candidate with enough demand: becomes Active, first mapping')),
    ('527060K040', dict(st='Active', min=100, pcs=12, max=8, eff='01-Jan-2026', scen='Stays Active; mapping equal to the previous period (no change)')),
    ('485108Z195', dict(st='Active', min=120, pcs=10, max=6, eff='01-Jan-2026', scen='Average below Min MAD: Active -> Inactive (No Sync, deleted at next Sync)')),
    ('53100YP320', dict(st='Inactive', min=10, pcs=4, max=3, eff='01-Jan-2026', scen='Inactive -> Active again')),
    ('17752BZ090', dict(st='Active', min=5, pcs=6, max=3, eff='01-Jan-2026', scen='4 destinations but Max Case/Day 3: only the top 3 kept; minimum 1 case (FB-157)')),
    ('464100K020', dict(st='Active', min=30, pcs=6, max=5, eff='01-Jan-2026', scen='One dominant destination; minimum 1 case makes the total too high (FB-157)')),
    ('90404T0002', dict(st='Candidate', min=200, pcs=1, max=10, eff='01-May-2026', scen='Demand in 1 month only: missing months count as 0')),
    ('52155BZ190', dict(st='Candidate', min=50, pcs=6, max=4, eff='15-Nov-2026', scen='Effective Start Date after the run date: not calculated')),
    ('1661106010', dict(st='Active', min=1, pcs=10, max=2, eff='01-Jan-2026', scen='No demand at all: average 0 -> Inactive')),
])

# Mapping of the previous period 202610 (TB_M_PART_CANDIDATE_DEST), assumed from the previous run / D/S edits
PREV_MAP = {
    '527060K040': {},          # filled with the calculated result below (equal = no change)
    '485108Z195': {'9722D10': 4, '9811110': 2},
    '53100YP320': {},
    '17752BZ090': {'9722D10': 1, '9715310': 1, '9811110': 1},
    '464100K020': {'9618201': 4, '9722D10': 1},
    '1661106010': {'9722D10': 2},
}

HDR = PatternFill('solid', fgColor='DDEBF7')
NOTE = PatternFill('solid', fgColor='FFF2CC')
OK = PatternFill('solid', fgColor='E2EFDA')
BAD = PatternFill('solid', fgColor='FCE4D6')
GREY = PatternFill('solid', fgColor='F2F2F2')
thin = Side(style='thin', color='999999')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical='top')
F = Font(name='Arial', size=9)
FB = Font(name='Arial', size=9, bold=True)


def load_demand():
    rows = []
    with open(os.path.join(HERE, 'xd05_demand_extract.csv')) as f:
        for r in csv.DictReader(f):
            r['MAD'] = float(r['MAD'])
            rows.append(r)
    return rows


def parse_dt(s):
    return datetime.strptime(s.replace('.000000000', ''), '%d-%b-%y %I.%M.%S %p')


def allocate(dest_mad, maxcd):
    """UISS XD05 4.6. dest_mad: {dest: result MAD}. Returns rows with all steps."""
    srt = sorted([(d, m) for d, m in dest_mad.items() if m > 0], key=lambda x: -x[1])
    kept, dropped = srt[:maxcd], srt[maxcd:]
    tot = sum(m for _, m in kept)
    res = []
    for rank, (d, m) in enumerate(kept, 1):
        tgt = m / tot * maxcd
        base = max(1, math.floor(tgt))
        res.append(dict(rank=rank, dest=d, mad=m, ratio=m / tot, tgt=tgt, frac=tgt - math.floor(tgt), base=base, adj=0))
    total = sum(r['base'] for r in res)
    while total < maxcd:
        r = sorted([x for x in res if x['adj'] == 0], key=lambda x: (-x['frac'], -x['mad']))[0]
        r['adj'] += 1
        total += 1
    while total > maxcd:
        cand = [x for x in res if x['base'] + x['adj'] > 1]
        r = sorted(cand, key=lambda x: (x['frac'], x['mad']))[0]
        r['adj'] -= 1
        total -= 1
    for r in res:
        r['case'] = r['base'] + r['adj']
    return res, [(d, m) for d, m in dropped]


def allocate_option_b(dest_mad, maxcd):
    """FB-157 option B: drop the smallest destination until the minimum 1 case fits, then the same rounding."""
    srt = sorted([(d, m) for d, m in dest_mad.items() if m > 0], key=lambda x: -x[1])[:maxcd]
    while True:
        tot = sum(m for _, m in srt)
        base = [max(1, math.floor(m / tot * maxcd)) for _, m in srt]
        if sum(base) <= maxcd or len(srt) == 1:
            break
        srt = srt[:-1]
    res, _ = allocate(dict(srt), maxcd)
    return res


def sheet(wb, title, heading, notes):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws['A1'] = heading
    ws['A1'].font = Font(name='Arial', size=12, bold=True)
    r = 2
    for n in notes:
        ws.cell(r, 1, n).font = Font(name='Arial', size=9, italic=True)
        r += 1
    return ws, r + 1


def table(ws, r0, cols, rows, widths=None, fills=None):
    for c, h in enumerate(cols, 1):
        x = ws.cell(r0, c, h)
        x.font, x.fill, x.border = FB, HDR, BOX
        x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    for i, row in enumerate(rows, 1):
        for c, v in enumerate(row, 1):
            x = ws.cell(r0 + i, c, v)
            x.font, x.border, x.alignment = F, BOX, WRAP
            if isinstance(v, float):
                x.number_format = '#,##0.00'
            if fills and fills.get(i):
                x.fill = fills[i]
    if widths:
        for c, w in enumerate(widths, 1):
            cur = ws.column_dimensions[get_column_letter(c)].width or 0
            ws.column_dimensions[get_column_letter(c)].width = max(cur, w)
    return r0 + len(rows) + 2


def page(ws):
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


def main():
    dem = load_demand()
    run_dt = datetime(2026, 11, 1)

    # ---------- process 1 ----------
    monthly = defaultdict(float)
    for r in dem:
        if r['DEMAND_MONTH_YEAR'] in RANGE:
            monthly[(r['PART_NO'], r['DEMAND_MONTH_YEAR'])] += r['MAD']
    p1 = []
    for p, s in PARTS.items():
        eff = datetime.strptime(s['eff'], '%d-%b-%Y')
        if eff > run_dt:
            p1.append(dict(part=p, skip=True, **s))
            continue
        mm = [round(monthly[(p, m)], 2) for m in RANGE]
        tot = round(sum(mm), 2)
        avg = round(tot / N, 2)
        new = 'Active' if avg >= s['min'] else 'Inactive'
        p1.append(dict(part=p, skip=False, mm=mm, tot=tot, avg=avg, new=new, **s))
    status_after = {x['part']: (x['st'] if x['skip'] else x['new']) for x in p1}

    # ---------- process 2 ----------
    destmad = defaultdict(lambda: defaultdict(float))
    for r in dem:
        if r['DEMAND_MONTH_YEAR'] in RANGE:
            destmad[r['PART_NO']][r['GROUPING_BUYER_CD'] + r['GROUPING_PD_CD']] += r['MAD']
    p2 = OrderedDict()
    for p, s in PARTS.items():
        if status_after[p] != 'Active':
            continue
        p2[p] = allocate(destmad[p], s['max'])
    PREV_MAP['527060K040'] = {r['dest']: r['case'] for r in p2['527060K040'][0]}
    PREV_MAP['53100YP320'] = {}

    wb = Workbook()
    wb.remove(wb.active)

    # ---------- Overview ----------
    ws, r = sheet(wb, 'Overview', 'XD05 DAD Volume Calculation - simulation on real actual demand data', [
        'Source: 20261013_tb_r_actual_demand_summary_since_january-2026.xlsx (349,225 rows, 19,997 parts, 6 destination codes). 9 parts selected to cover the scenarios.',
        'Rules: UISS XD04 / XD05 (decisions up to 6-Nov). Values are calculated by the batch rule (no Excel formula), so they also show in previews.'])
    r = table(ws, r, ['Item', 'Value'], [
        ['Run date', RUN_DATE + ' (XD04 monthly run on the 1st brings the new rows; XD05 trigger finds new data the same day)'],
        ['Range of months N (system master)', '%d -> %s to %s' % (N, RANGE[0], RANGE[-1])],
        ['New period', RUN_MONTH + ' (Nov 2026); previous period ' + PREV + ' becomes past (read only)'],
        ['Process 1', 'Average MAD = total MAD of the range / N (missing month = 0) -> Active if >= Min MAD, else Inactive'],
        ['Process 2', 'Active parts only: result MAD per destination (buyer + PD code), top Max Case/Day destinations, Case/Day in proportion, min 1, total = Max Case/Day'],
    ], [34, 120])
    rows = []
    for x in p1:
        if x['skip']:
            res = 'Not calculated (Effective Start Date %s)' % x['eff']
        else:
            res = '%s -> %s (avg %.2f vs Min MAD %d)' % (x['st'], x['new'], x['avg'], x['min'])
        rows.append([x['part'], x['scen'], res])
    ws.cell(r - 1, 1, 'Parts and result').font = FB
    r = table(ws, r, ['Part No', 'Scenario', 'Result process 1'], rows, [34, 70, 50])
    ws.cell(r - 1, 1, 'Sheets').font = FB
    table(ws, r, ['Sheet', 'Content'], [
        ['1. Input', 'Part List before the run, previous period mapping, system master'],
        ['2. Demand', 'Rows of TB_R_ACTUAL_DEMAND_SUMMARY for the 9 parts (real data, months 202601-202610)'],
        ['3. Process 1', 'Monthly MAD per part, average, status'],
        ['4. Process 2', 'Result MAD per destination, ranking, limit, allocation step by step'],
        ['5. Output tables', 'Rows written by the run: TB_R_PART_DAD_RESULT, TB_M_PART_CANDIDATE, TB_M_PART_CANDIDATE_DEST, TB_H_PART_CANDIDATE, Log'],
        ['6. Trigger timeline', 'When XD04 / XD05 run with the real loads of 2026 (FB-163 / FB-164)'],
        ['7. FB-157 option B', 'Current rounding rule vs dropping the smallest destination'],
        ['8. Findings', 'Points found by the simulation'],
    ], [34, 120])
    page(ws)

    # ---------- Input ----------
    ws, r = sheet(wb, '1. Input', 'Input before the run (%s)' % RUN_DATE, ['TB_M_PART_CANDIDATE (Part List) and TB_M_PART_CANDIDATE_DEST of the previous period %s.' % PREV])
    r = table(ws, r, ['Part No', 'Status', 'Min MAD', 'Pcs/Case', 'Max Case/Day', 'Effective Start Date', 'Scenario'],
              [[p, s['st'], s['min'], s['pcs'], s['max'], s['eff'], s['scen']] for p, s in PARTS.items()], [14, 11, 9, 9, 11, 14, 70])
    ws.cell(r - 1, 1, 'Mapping of the previous period %s' % PREV).font = FB
    prow = []
    for p, m in PREV_MAP.items():
        if not m:
            prow.append([p, '-', '-', 'No row (part was %s)' % PARTS[p]['st']])
        for d, c in m.items():
            prow.append([p, d, c, ''])
    for p in PARTS:
        if p not in PREV_MAP:
            prow.append([p, '-', '-', 'No row (part was %s)' % PARTS[p]['st']])
    table(ws, r, ['Part No', 'Destination Code', 'Case/Day', 'Note'], prow, [14, 14, 9, 40])
    page(ws)

    # ---------- Demand ----------
    ws, r = sheet(wb, '2. Demand', 'TB_R_ACTUAL_DEMAND_SUMMARY (NSP) - rows of the 9 parts', [
        'Real rows from the reference file. Highlighted = inside the range %s-%s used by this run.' % (RANGE[0], RANGE[-1])])
    drows, fills = [], {}
    for i, d in enumerate(sorted(dem, key=lambda x: (list(PARTS).index(x['PART_NO']), x['DEMAND_MONTH_YEAR'], x['GROUPING_BUYER_CD'], x['ORDER_TYPE_GROUP'])), 1):
        drows.append([d['PART_NO'], d['GROUPING_BUYER_CD'], d['GROUPING_PD_CD'], d['GROUPING_BUYER_CD'] + d['GROUPING_PD_CD'], d['ORDER_TYPE_GROUP'],
                      d['DEMAND_MONTH_YEAR'], round(d['MAD'], 2), d['CREATE_DT']])
        if d['DEMAND_MONTH_YEAR'] in RANGE:
            fills[i] = OK
    table(ws, r, ['PART_NO', 'GROUPING_BUYER_CD', 'GROUPING_PD_CD', 'Destination Code', 'ORDER_TYPE_GROUP', 'DEMAND_MONTH_YEAR', 'MAD', 'CREATE_DT'],
          drows, [13, 12, 10, 12, 10, 12, 10, 30], fills)
    ws.freeze_panes = ws.cell(r + 1, 1)
    page(ws)

    # ---------- Process 1 ----------
    ws, r = sheet(wb, '3. Process 1', 'Process 1 - average MAD and part status', [
        'Monthly MAD = sum of MAD of all buyer / PD / order type (N + S) rows of the part in the month. Average = total / %d (always %d, missing month = 0).' % (N, N)])
    rows, fills = [], {}
    for i, x in enumerate(p1, 1):
        if x['skip']:
            rows.append([x['part'], x['st'], x['min']] + ['-'] * (N + 2) + ['Not calculated', 'Effective Start Date %s is after the run date: no result record (LOG4)' % x['eff']])
            fills[i] = GREY
            continue
        chg = x['new'] != x['st']
        note = []
        if chg:
            note.append('Status changed: PART_STATUS updated, history CALC / BATCH')
            if x['st'] == 'Active' and x['new'] == 'Inactive':
                note.append('Active -> Inactive: SYNC_STATUS = 0 (No Sync); next [Sync] deletes it in GTOPAS (XD06) and AP POLE (XD07)')
        else:
            note.append('Status not changed: result record only, no history')
        if sum(1 for v in x['mm'] if v == 0) and x['tot'] > 0:
            note.append('%d month(s) without demand count as 0' % sum(1 for v in x['mm'] if v == 0))
        rows.append([x['part'], x['st'], x['min']] + x['mm'] + [x['tot'], x['avg'], x['new'], '; '.join(note)])
        fills[i] = BAD if x['new'] == 'Inactive' else OK
    table(ws, r, ['Part No', 'Status before', 'Min MAD'] + RANGE + ['Total', 'Average (/6)', 'New status', 'Note'],
          rows, [13, 11, 8] + [9] * N + [10, 10, 11, 70], fills)
    page(ws)

    # ---------- Process 2 ----------
    ws, r = sheet(wb, '4. Process 2', 'Process 2 - Case/Day per destination, new period %s' % RUN_MONTH, [
        'Active parts after process 1. Result MAD = sum of MAD of the destination (N + S) in the range. Sort largest first, keep at most Max Case/Day destinations.',
        'Target = result MAD / sum of kept result MAD x Max Case/Day. Rounded down with min 1; +1 to the largest fraction while the total is short; -1 from the smallest fraction (> 1 case) while it is over.'])
    for p, (res, dropped) in p2.items():
        s = PARTS[p]
        ws.cell(r - 1, 1, '%s - Max Case/Day %d, Pcs/Case %d (%s)' % (p, s['max'], s['pcs'], s['scen'])).font = FB
        rows = []
        for x in res:
            step = []
            if x['base'] > math.floor(x['tgt']):
                step.append('min 1')
            if x['adj'] > 0:
                step.append('+1 (fraction %.2f)' % x['frac'])
            if x['adj'] < 0:
                step.append('%d (total over Max)' % x['adj'])
            rows.append([x['rank'], x['dest'], round(x['mad'], 2), '%.1f%%' % (x['ratio'] * 100), round(x['tgt'], 2), x['base'], ', '.join(step), x['case'], x['case'] * s['pcs']])
        for d, m in dropped:
            rows.append(['-', d, round(m, 2), '', '', '', 'Not mapped: beyond Max Case/Day destinations (LOG12)', 0, 0])
        rows.append(['Total', '', round(sum(x['mad'] for x in res), 2), '100%', round(sum(x['tgt'] for x in res), 2), sum(x['base'] for x in res), '',
                     sum(x['case'] for x in res), sum(x['case'] for x in res) * s['pcs']])
        fills = {len(rows): GREY}
        r = table(ws, r + 0, ['Rank', 'Destination Code', 'Result MAD', 'Ratio', 'Target', 'Rounded down (min 1)', 'Adjustment', 'Case/Day', 'Pcs/Day'],
                  rows, [7, 14, 11, 8, 9, 12, 40, 9, 9], fills) + 1
    page(ws)

    # ---------- Output tables ----------
    ws, r = sheet(wb, '5. Output tables', 'Rows written by the run (all-or-nothing per process)', ['Batch user = BATCH_XD05; date-time = 01-Nov-2026 01:30.'])
    ws.cell(r - 1, 1, 'TB_R_PART_DAD_RESULT (insert, one per calculated part)').font = FB
    r = table(ws, r, ['PERIOD', 'PART_NO', 'MONTH_FROM', 'MONTH_TO', 'NUM_OF_MONTH', 'TOTAL_MAD', 'AVG_MAD', 'MIN_MAD', 'OLD_STATUS', 'NEW_STATUS'],
              [[RUN_MONTH, x['part'], RANGE[0], RANGE[-1], N, x['tot'], x['avg'], x['min'], x['st'], x['new']] for x in p1 if not x['skip']],
              [9, 13, 11, 10, 11, 11, 10, 9, 11, 11])
    ws.cell(r - 1, 1, 'TB_M_PART_CANDIDATE (update)').font = FB
    upd, hist = [], []
    for x in p1:
        if x['skip']:
            continue
        if x['new'] != x['st']:
            sync = '0 (No Sync)' if (x['st'] == 'Active' and x['new'] == 'Inactive') else 'not changed by process 1'
            upd.append([x['part'], 'Process 1', 'PART_STATUS %s -> %s' % (x['st'], x['new']), sync, 'CALC'])
            hist.append([x['part'], RUN_MONTH, 'CALC', 'BATCH', '', 'PART_STATUS', x['st'], x['new'], 'Average MAD %.2f vs Min MAD %d' % (x['avg'], x['min'])])
    for p, (res, _) in p2.items():
        new = {x['dest']: x['case'] for x in res}
        old = PREV_MAP.get(p, {})
        if new != old:
            upd.append([p, 'Process 2', 'Mapping differs from %s' % PREV, '0 (No Sync)', 'CALC'])
            for d in sorted(set(new) | set(old)):
                if new.get(d) != old.get(d):
                    hist.append([p, RUN_MONTH, 'MAPPING', 'BATCH', d, 'CASE_DAY', old.get(d, 'NULL'), new.get(d, 'NULL'), ''])
        else:
            upd.append([p, 'Process 2', 'Mapping equal to %s: no update' % PREV, 'not changed', '-'])
    r = table(ws, r, ['PART_NO', 'By', 'Change', 'SYNC_STATUS', 'LAST_SOURCE'], upd, [13, 11, 40, 22, 12])
    ws.cell(r - 1, 1, 'TB_M_PART_CANDIDATE_DEST (insert, period %s)' % RUN_MONTH).font = FB
    r = table(ws, r, ['PART_NO', 'PERIOD', 'DEST_CODE', 'CASE_DAY'],
              [[p, RUN_MONTH, x['dest'], x['case']] for p, (res, _) in p2.items() for x in res], [13, 9, 11, 9])
    ws.cell(r - 1, 1, 'TB_H_PART_CANDIDATE (insert, history)').font = FB
    r = table(ws, r, ['PART_NO', 'PERIOD', 'EVENT_TYPE', 'SOURCE', 'DEST_CODE', 'FIELD_NAME', 'OLD_VALUE', 'NEW_VALUE', 'REMARK'], hist,
              [13, 9, 11, 9, 11, 12, 11, 11, 34])
    ws.cell(r - 1, 1, 'Log').font = FB
    n_calc = sum(1 for x in p1 if not x['skip'])
    n_chg = sum(1 for x in p1 if not x['skip'] and x['new'] != x['st'])
    n_map = sum(1 for p, (res, _) in p2.items() if {x['dest']: x['case'] for x in res} != PREV_MAP.get(p, {}))
    table(ws, r, ['BATCH_ID', 'RUN_TYPE', 'RETRY_NO', 'STATUS', 'DATA_DT', 'Message'], [
        ['ADS_SYNC (XD04)', 'SCHEDULE', 0, 'SUCCESS', '-', 'LOG2: inserted 29,176 (month 202610), updated 0, new watermark 13-OCT-26 02.44.28'],
        ['DAD_CALC', 'SCHEDULE', 0, 'SUCCESS', '13-OCT-26 02.44.28', 'LOG2: calculated %d, status changed %d; LOG4: 52155BZ190 skipped' % (n_calc, n_chg)],
        ['MAPPING_CALC', 'SCHEDULE', 0, 'SUCCESS', '13-OCT-26 02.44.28', 'LOG9: parts %d, mapping changed %d; LOG12: 17752BZ090 4 destinations limited to 3' % (len(p2), n_map)],
    ], [18, 11, 9, 10, 20, 80])
    page(ws)

    # ---------- Trigger timeline ----------
    loads = []
    with open(os.path.join(HERE, 'xd05_loads.csv')) as f:
        for x in csv.DictReader(f):
            loads.append((parse_dt(x['CREATE_DT']), x['CREATE_DT'], int(x['ROWS']), x['MONTHS']))
    loads.sort()
    ws, r = sheet(wb, '6. Trigger timeline', 'When XD04 and XD05 run with the real loads of 2026', [
        'Each row = one load in DB Surrounding (distinct CREATE_DT). Option A = XD04 monthly on the 1st (current spec). Option B = XD04 daily (if the schedule follows the source updates).',
        'XD05 trigger (FB-163): runs when TB_R_ACTUAL_DEMAND_SUMMARY (NSP) has rows with CREATE_DT later than DATA_DT of the last successful XD05 run.'])
    rows, fills = [], {}
    for i, (dt, raw, n, months) in enumerate(loads, 1):
        nxt = datetime(dt.year + (dt.month == 12), dt.month % 12 + 1, 1)
        a = 'Picked up by XD04 on %s -> XD05 the same day: period %s, range ends %s' % (nxt.strftime('%d-%b'), nxt.strftime('%Y%m'), dt.strftime('%Y%m'))
        prev_m = '%d%02d' % ((dt.year, dt.month - 1) if dt.month > 1 else (dt.year - 1, 12))
        b = 'XD05 on %s: period %s, range ends %s' % (dt.strftime('%d-%b'), dt.strftime('%Y%m'), prev_m)
        if months.split()[-1] == dt.strftime('%Y%m'):
            b += ' -> the month just loaded (%s) is NOT in the range' % dt.strftime('%Y%m')
            fills[i] = BAD
        rows.append([raw, n, months, a, b])
    table(ws, r, ['CREATE_DT (load)', 'Rows', 'DEMAND_MONTH_YEAR', 'Option A: XD04 monthly on the 1st', 'Option B: XD04 daily'], rows, [32, 9, 14, 62, 70], fills)
    page(ws)

    # ---------- FB-157 ----------
    ws, r = sheet(wb, '7. FB-157 option B', 'Rounding: current rule vs option B (drop the smallest destination)', [
        'Real parts where one destination has most of the demand: the minimum 1 case per kept destination takes cases away from it.'])
    cmp = {}
    for p in ('464100K020', '17752BZ090', '90404T0002', '52119BZV60'):
        cur = {x['dest']: x['case'] for x in p2[p][0]}
        ob = {x['dest']: x['case'] for x in allocate_option_b(destmad[p], PARTS[p]['max'])}
        cmp[p] = (cur, ob)
        ws.cell(r - 1, 1, '%s - Max Case/Day %d' % (p, PARTS[p]['max'])).font = FB
        rows = []
        for x in p2[p][0]:
            rows.append([x['dest'], round(x['mad'], 2), '%.1f%%' % (x['ratio'] * 100), round(x['tgt'], 2), cur.get(x['dest'], 0), ob.get(x['dest'], 0)])
        rows.append(['Total', round(sum(x['mad'] for x in p2[p][0]), 2), '100%', PARTS[p]['max'], sum(cur.values()), sum(ob.values())])
        r = table(ws, r, ['Destination Code', 'Result MAD', 'Ratio', 'Target', 'Current rule (min 1 each)', 'Option B (drop smallest)'], rows,
                  [14, 11, 8, 9, 20, 20], {len(rows): GREY}) + 1
    page(ws)

    # ---------- Findings ----------
    ws, r = sheet(wb, '8. Findings', 'Findings of the simulation', [])
    table(ws, r, ['FB', 'Status', 'Finding', 'Proposal'], [
        ['FB-167', 'Perlu keputusan',
         'The source loads one month at the end of that month (e.g. 31-May 02:44 = 202605). If XD04 runs daily (option B), the XD05 trigger fires on the load day itself: '
         'the run month is still the loaded month, so the range ends one month earlier and the new data is not used; on the 1st of the next month there is no new data, so the new period is never created.',
         'Keep XD04 monthly on the 1st (option A): one XD04 + one XD05 per month, and the range includes the month just loaded. FB-164 (several runs a month) then does not happen.'],
        ['FB-168', 'Info',
         'Small extra loads in the middle of a month exist (11-Feb 1 row, 19-Feb 2, 26-May 1, 28-May 1, 27-Aug 2 rows). With option A they are picked up with the month-end load on the 1st.',
         '-'],
        ['FB-157', 'Perlu keputusan',
         '; '.join('%s: %s has %.0f%% of the demand (target %.2f) but gets %d of %d cases' % (p, p2[p][0][0]['dest'], p2[p][0][0]['ratio'] * 100, p2[p][0][0]['tgt'],
                                                                                          p2[p][0][0]['case'], PARTS[p]['max']) for p in ('464100K020', '17752BZ090', '90404T0002'))
         + '. Cause: every kept destination gets at least 1 case.',
         'Option B (drop the smallest destination until the minimum fits): ' + '; '.join('%s -> %s' % (p, ' / '.join(str(v) for v in cmp[p][1].values() if v)) for p in ('464100K020', '17752BZ090', '90404T0002'))],
        ['FB-153', 'Perlu keputusan',
         '485108Z195 Active -> Inactive gets No Sync (4.3). The previous mapping 202610 has 2 destinations; process 2 creates no row for 202611. On [Sync] XD06 deletes all rows, XD07 sends Delete.',
         'Fix Data Map #2 (SYNC_STATUS) as proposed in FB-153.'],
        ['FB-169', 'Info',
         '90404T0002 has demand in 1 month only (202610), still Active because 535.25 >= 200: one big month is enough when Min MAD is low.',
         'Divisor always N (decided); no change.'],
        ['FB-170', 'Info',
         'Real data: 6 destination codes in total (9722D10, 9715310, 9811110, 9618201, 9811162, 9811163); 9811162 / 9811163 have very small demand. All must exist in TB_M_H0125_DESTINATION, otherwise the whole run fails (LOG11).',
         'Check the 6 codes in the Destination Master before go-live.'],
    ], [9, 15, 90, 60])
    page(ws)

    wb.save(OUT)
    print('saved', OUT)
    for x in p1:
        print(x['part'], 'skip' if x['skip'] else (x['avg'], x['st'], '->', x['new']))
    for p, (res, d) in p2.items():
        print(p, [(x['dest'], round(x['tgt'], 2), x['case']) for x in res], d)


if __name__ == '__main__':
    main()
