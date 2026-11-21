"""Generate the full-flow artifact: XD05 (day D) -> screen adjust -> [Sync] -> RPA AP POLE (upload files) -> Period Rollover -> RPA GTOPAS.
Design of 21-Nov: TB_M_PART_CANDIDATE has no sync columns; TB_H_PART_CANDIDATE_STG_SYNC keeps every change and the Sync Status of both targets."""
import html
import math
import os
import sys

sys.path.insert(0, '/home/user/crossdockpoc/deliverables/function_list_v2/erd')
from build_erd import load_tables  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
T = load_tables()[0]
REMOVED = {'SYNC_STATUS', 'GTOPAS_SYNC_DT', 'APPOLE_SYNC_DT', 'SYNC_RUN_ID'}
KCOLS = [c[0] for c in T['TB_M_PART_CANDIDATE'][1] if c[0] not in REMOVED]
DCOLS = [c[0] for c in T['TB_M_PART_CANDIDATE_DEST'][1]]
RCOLS = [c[0] for c in T['TB_R_PART_DAD_RESULT'][1]]
SCOLS = ['HIST_ID', 'PART_NO', 'PERIOD', 'PART_STATUS', 'LEVEL_TYPE', 'DEST_CODE', 'ORDER_TYPE', 'FIELD_NAME', 'ACTION', 'OLD_VALUE', 'NEW_VALUE', 'SOURCE', 'UPLOAD_ID',
         'APPOLE_SYNC_STATUS', 'APPOLE_SYNC_DT', 'SEND_SEQ', 'APPOLE_SYNC_RUN_ID', 'GTOPAS_SYNC_STATUS', 'GTOPAS_SYNC_DT', 'GTOPAS_SYNC_RUN_ID',
         'CREATED_BY', 'CREATED_DT', 'CHANGED_BY', 'CHANGED_DT']

CUR, NXT = '202611', '202612'
D5T, ADJ, SYNC, ROLL = '27-Nov-2026 02:00', '27-Nov-2026 09:00', '27-Nov-2026 10:00', '01-Dec-2026 00:10'
RUN_AP, RUN_GT = '20261127100000', '20261201001000'
DS, BATCH = 'D.Anggraini', 'XD05BATCH'
MONTHS = ['202605', '202606', '202607', '202608', '202609', '202610']
DEST = {'JAPAN': 'JAPAN', 'KOREA': 'KOREA', 'TAIWAN': 'TAIWAN', 'USA': 'USA'}   # dummy destinations (country names)
BP = dict((k, k) for k in DEST)
DORD = list(DEST)
PN = {'A': 'DUMMY-001', 'B': 'DUMMY-002', 'C': 'DUMMY-003', 'D': 'DUMMY-004'}
NAME = {p: f'DUMMY PART {PN[p][-3:]}' for p in PN}
PARTS = {'A': dict(min=300, pcs=6, max=12, st='Active', eff='01-Jun-2026'), 'B': dict(min=200, pcs=10, max=6, st='Candidate', eff='15-Nov-2026'),
         'C': dict(min=500, pcs=8, max=10, st='Active', eff='01-Jun-2026'), 'D': dict(min=100, pcs=4, max=8, st='Active', eff='01-Jun-2026')}
CUR_MAP = {('A', 'JAPAN', '**'): 6, ('A', 'KOREA', '**'): 6, ('C', 'KOREA', '**'): 10, ('D', 'JAPAN', '**'): 8}
DEMAND = [('A', 'JAPAN', 150, MONTHS), ('A', 'KOREA', 100, MONTHS), ('A', 'TAIWAN', 70, MONTHS), ('B', 'JAPAN', 140, MONTHS),
          ('B', 'USA', 90, MONTHS), ('C', 'KOREA', 200, MONTHS[3:]), ('D', 'JAPAN', 150, MONTHS)]


def e(x):
    return '' if x is None else html.escape(str(x))


def pill(t, cls):
    return f'<span class="pill {cls}">{e(t)}</span>'


ACT_CLS = {'ADD': 'p-add', 'EDIT': 'p-par', 'DELETE': 'p-del', 'Add': 'p-add', 'Down': 'p-down', 'Up': 'p-up', 'Delete': 'p-del', 'Edit': 'p-par',
           'Add part': 'p-add', 'Keep': 'p-ok', 'record': 'p-none', '-': 'p-none'}
LV = {'P': 'KANBAN', 'C': 'EXPORT'}   # LEVEL_TYPE values
ST = {'0': '0 Non Sync', '1': '1 Sync', '2': '2 Superseded', None: ''}


def table(cols, rows, cls=None, raw=(), sim=()):
    h = ''.join(f'<th class="th-sim">{e(c)}</th>' if j in sim else f'<th>{e(c)}</th>' for j, c in enumerate(cols))
    body = []
    for i, r in enumerate(rows):
        c = cls(r, i) if cls else ''
        body.append(f'<tr class="{c}">' + ''.join(f'<td>{v if j in raw else e(v)}</td>' for j, v in enumerate(r)) + '</tr>')
    if not rows:
        body.append(f'<tr><td colspan="{len(cols)}">(no rows)</td></tr>')
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


# ---------- data model ----------
def kan(p, per, st, pcs, mx, src, created, changed):
    d = PARTS[p]
    v = dict(PART_NO=PN[p], PERIOD=per, PART_NAME=NAME[p], MIN_MAD=d['min'], PCS_CASE=pcs, MAX_CASE_DAY=mx, TOTAL_PCS_DAY=pcs * mx,
             EFFECTIVE_START_DATE=d['eff'], PART_STATUS=st, LAST_SOURCE=src, LAST_UPLOAD_ID='', CREATED_BY=created[0], CREATED_DT=created[1],
             CHANGED_BY=changed[0], CHANGED_DT=changed[1])
    return [v.get(c, '') for c in KCOLS]


def dst(p, per, code, ot, cd, created, changed):
    v = dict(PART_NO=PN[p], PERIOD=per, DEST_CODE=code, ORDER_TYPE=ot, CASE_DAY=cd, CREATED_BY=created[0], CREATED_DT=created[1], CHANGED_BY=changed[0],
             CHANGED_DT=changed[1])
    return [v.get(c, '') for c in DCOLS]


STG = []


def stg(p, per, lvl, field, act, old, new, src, by, dt, code='', ot='', ap='0', gt=None, ps=None):
    r = dict(HIST_ID=101 + len(STG), p=p, PART_NO=PN[p], PERIOD=per, PART_STATUS=ps or (newst[p] if per == NXT else PARTS[p]['st']), LEVEL_TYPE=lvl, DEST_CODE=code, ORDER_TYPE=ot, FIELD_NAME=field, ACTION=act,
             OLD_VALUE=old, NEW_VALUE=new, SOURCE=src, UPLOAD_ID='', APPOLE_SYNC_STATUS=ap, APPOLE_SYNC_DT='', SEND_SEQ='', APPOLE_SYNC_RUN_ID='',
             GTOPAS_SYNC_STATUS=gt, GTOPAS_SYNC_DT='', GTOPAS_SYNC_RUN_ID='', CREATED_BY=by, CREATED_DT=dt, CHANGED_BY='', CHANGED_DT='')
    r['gt0'] = gt
    STG.append(r)
    return r


def fresh(r):
    """Row as it is right after the insert (the later [Sync] / Rollover fill these columns on the same dict)."""
    return dict(r, APPOLE_SYNC_STATUS='0', APPOLE_SYNC_DT='', SEND_SEQ='', APPOLE_SYNC_RUN_ID='', GTOPAS_SYNC_STATUS=r['gt0'], GTOPAS_SYNC_DT='',
                GTOPAS_SYNC_RUN_ID='', CHANGED_BY='', CHANGED_DT='')


def stg_rows(rows):
    out = [[LV.get(r[c], r[c]) if c == 'LEVEL_TYPE' else r[c] if c not in ('APPOLE_SYNC_STATUS', 'GTOPAS_SYNC_STATUS') else ST[r[c]] for c in SCOLS] for r in rows]
    ai = SCOLS.index('ACTION')
    for o in out:
        o[ai] = pill(o[ai], ACT_CLS[o[ai]])
    return out


def stg_table(rows):
    def cls(r, i):
        s = rows[i]['APPOLE_SYNC_STATUS']
        return {'0': 'r-pend', '1': 'r-ok', '2': 'r-sup'}[s]
    return table(SCOLS, stg_rows(rows), cls, raw={SCOLS.index('ACTION')})


def allocate(mads, mx):
    keep = sorted(mads, key=lambda x: -x[1])[:mx]
    tot = sum(m for _, m in keep)
    rows = [[d, m, m / tot * mx] for d, m in keep]
    for r in rows:
        r.append(max(1, math.floor(r[2])))
    while sum(r[3] for r in rows) < mx:
        r = max(rows, key=lambda x: (x[2] - math.floor(x[2]), x[1]))
        r[3] += 1
        r[2] = math.floor(r[2])
    return [(d, m, round(m / tot * mx, 3), c) for d, m, _, c in rows]


# ---------- step 0: before ----------
OLD = ('FID Rayhan', '01-Jun-2026 09:00')
kcur = {p: kan(p, CUR, PARTS[p]['st'], PARTS[p]['pcs'], PARTS[p]['max'], 'CALC' if p != 'B' else 'SCREEN',
               OLD if p != 'B' else (DS, '10-Nov-2026 09:15'), (DS, '27-Oct-2026 10:30') if p != 'B' else (DS, '10-Nov-2026 09:15')) for p in PARTS}
dcur = {k: dst(k[0], CUR, k[1], k[2], v, (BATCH, '27-Oct-2026 02:00'), (BATCH, '27-Oct-2026 02:00')) for k, v in CUR_MAP.items()}
gt_before = sorted({(PN[p], c) for (p, c, _) in CUR_MAP})
ap11 = {p: dict(pcs=PARTS[p]['pcs'], max=PARTS[p]['max'], ch={(c, o): v for (q, c, o), v in CUR_MAP.items() if q == p}) for p in 'ACD'}

# ---------- step 1: XD05 process 1 ----------
calc, dad, newst = [], [], {}
for p, d in PARTS.items():
    per_m = [sum(x[2] for x in DEMAND if x[0] == p and m in x[3]) for m in MONTHS]
    tot = sum(per_m)
    avg = round(tot / 6, 2)
    st = 'Active' if avg >= d['min'] else 'Inactive'
    newst[p] = st
    calc.append([PN[p], *per_m, tot, avg, d['min'], d['st'], st])
    v = dict(PERIOD=NXT, PART_NO=PN[p], MONTH_FROM=MONTHS[0], MONTH_TO=MONTHS[-1], NUM_OF_MONTH=6, TOTAL_MAD=tot, AVG_MAD=avg, MIN_MAD=d['min'],
             OLD_STATUS=d['st'], NEW_STATUS=st, CREATED_BY=BATCH, CREATED_DT=D5T)
    dad.append([v.get(c, '') for c in RCOLS])
knxt = {p: kan(p, NXT, newst[p], PARTS[p]['pcs'], PARTS[p]['max'], 'CALC', (BATCH, D5T), (BATCH, D5T)) for p in PARTS}
s1 = []
for p in PARTS:
    if True:   # Active and Inactive: the part stays in the AP POLE Kanban of the new month
        s1.append(stg(p, NXT, 'P', 'PCS_CASE', 'ADD', '', PARTS[p]['pcs'], 'BATCH', BATCH, D5T))
        s1.append(stg(p, NXT, 'P', 'MAX_CASE_DAY', 'ADD', '', PARTS[p]['max'], 'BATCH', BATCH, D5T))

# ---------- step 2: XD05 process 2 ----------
alloc, dnxt = [], {}
for p in PARTS:
    if newst[p] != 'Active':
        continue
    mads = {}
    for q, c, mad, months in DEMAND:
        if q == p:
            mads[c] = mads.get(c, 0) + mad * len(months)
    for c, m, tgt, cd in allocate(list(mads.items()), PARTS[p]['max']):
        alloc.append([PN[p], c, m, tgt, cd])
        dnxt[(p, c, '**')] = cd
s2 = [stg(p, NXT, 'C', 'CASE_DAY', 'ADD', '', cd, 'BATCH', BATCH, D5T, code=c, ot=o, gt='0') for (p, c, o), cd in sorted(dnxt.items(), key=lambda x: (x[0][0], DORD.index(x[0][1])))]
# Inactive part of the new period: every destination of the previous period -> DELETE (Buyer-PD 0 in file 1)
s2 += [stg(p, NXT, 'C', 'CASE_DAY', 'DELETE', v, 0, 'BATCH', BATCH, D5T, code=c, ot=o, gt='0') for (p, c, o), v in CUR_MAP.items() if newst[p] == 'Inactive']

# ---------- step 3: adjust Current A ----------
s3 = [stg('A', CUR, 'P', 'MAX_CASE_DAY', 'EDIT', 12, 11, 'SCREEN', DS, ADJ),
      stg('A', CUR, 'C', 'CASE_DAY', 'EDIT', 6, 7, 'SCREEN', DS, ADJ, code='JAPAN', ot='**'),
      stg('A', CUR, 'C', 'CASE_DAY', 'EDIT', 6, 4, 'SCREEN', DS, ADJ, code='KOREA', ot='**')]
kcur_adj = kan('A', CUR, 'Active', 6, 11, 'SCREEN', OLD, (DS, ADJ))
dcur_adj = [dst('A', CUR, 'JAPAN', '**', 7, (BATCH, '27-Oct-2026 02:00'), (DS, ADJ)), dst('A', CUR, 'KOREA', '**', 4, (BATCH, '27-Oct-2026 02:00'), (DS, ADJ))]

# ---------- step 4: [Sync] in NSP ----------
pending = [r for r in STG if r['APPOLE_SYNC_STATUS'] == '0']
groups = {}
for r in pending:
    groups.setdefault((r['PERIOD'], r['p'], r['LEVEL_TYPE'], r['DEST_CODE'], r['ORDER_TYPE'], r['FIELD_NAME']), []).append(r)
red = []
for key, g in groups.items():
    a, b = g[0]['OLD_VALUE'], g[-1]['NEW_VALUE']
    a = None if a == '' else a
    if key[5] == 'PART_STATUS':
        act, seq = 'record', ''
    elif a is None:
        act = 'Add'
        seq = 2 if key[2] == 'P' else 3
    elif g[-1]['ACTION'] == 'DELETE':
        act, seq = 'Delete', 1
    elif b < a:
        act, seq = 'Down', 1 if key[2] == 'C' else 2
    elif b > a:
        act, seq = 'Up', 3 if key[2] == 'C' else 2
    else:
        act, seq = '-', ''
    last = g[-1]
    for r in g:
        r['APPOLE_SYNC_STATUS'] = '1' if r is last else '2'
        r['APPOLE_SYNC_DT'], r['APPOLE_SYNC_RUN_ID'], r['CHANGED_BY'], r['CHANGED_DT'] = SYNC, RUN_AP, DS, SYNC
    last['SEND_SEQ'] = seq
    red.append(dict(per=key[0], p=key[1], lvl=key[2], code=key[3], ot=key[4], f=key[5], ids=[x['HIST_ID'] for x in g], ap=a, nsp=b, act=act, seq=seq,
                    last=last['HIST_ID']))
# EXPORT rows: file 1 (before the Kanban file) only for a part whose Max goes down; every other part (Max up, new part, no Kanban row)
# -> file 3 after the Kanban file. Inside a file: rows going down / deleted first, then up / added.
by_id = {r['HIST_ID']: r for r in STG}
maxdown = {(x['per'], x['p']) for x in red if x['lvl'] == 'P' and x['f'] == 'MAX_CASE_DAY' and x['act'] == 'Down'}
for x in red:
    if x['lvl'] == 'C' and x['seq'] != '':
        x['seq'] = 1 if (x['per'], x['p']) in maxdown else 3
        by_id[x['last']]['SEND_SEQ'] = x['seq']
# GTOPAS at [Sync]: Current rows with GTOPAS 0 -> none in this example (A Current only EDIT rows)
gt_cur_pending = [r for r in STG if r['GTOPAS_SYNC_STATUS'] == '0' and r['PERIOD'] == CUR]
after_sync = [dict(r) for r in STG]

# upload files
files = []
for per in (CUR, NXT):
    for seq in (1, 2, 3):
        rows = [x for x in red if x['per'] == per and x['seq'] == seq]
        if not rows:
            continue
        mm, yy = per[4:], per[:4]
        if seq == 2:
            out = []
            for p in sorted({x['p'] for x in rows}):
                pcs = next((x['nsp'] for x in red if x['per'] == per and x['p'] == p and x['f'] == 'PCS_CASE' and x['seq'] == 2), PARTS[p]['pcs'])
                mx = next((x['nsp'] for x in red if x['per'] == per and x['p'] == p and x['f'] == 'MAX_CASE_DAY' and x['seq'] == 2), PARTS[p]['max'])
                out.append([mm, yy, 'P6', PN[p], NAME[p], pcs, mx, pcs * mx, ''])
            files.append(dict(name=f'LLM9Q910_{RUN_AP}_{per}_2.xls', kind='Kanban', per=per, seq=seq, rows=out))
        else:
            out = [[mm, yy, PN[x['p']].replace('-', ''), '', '', BP[x['code']], x['ot'], '2', 0 if x['act'] == 'Delete' else x['nsp'], '', '']
                   for x in sorted(rows, key=lambda x: (x['p'], x['act'] not in ('Down', 'Delete'), DORD.index(x['code'])))]
            files.append(dict(name=f'LLM9Q880_{RUN_AP}_{per}_{seq}.xls', kind='Export', per=per, seq=seq, rows=out, red=rows))

# ---------- step 5: bot uploads (play row by row) ----------
ap = {CUR: {p: dict(pcs=v['pcs'], max=v['max'], ch=dict(v['ch'])) for p, v in ap11.items()}, NXT: {}}
play = []
for f in files:
    per = f['per']
    for row in f['rows']:
        if f['kind'] == 'Kanban':
            p = next(q for q in PN if PN[q] == row[3])
            rec = ap[per].setdefault(p, dict(pcs=None, max=None, ch={}))
            act = 'Edit' if rec['max'] is not None else 'Add part'
            frm = '-' if rec['max'] is None else f"Max {rec['max']}"
            rec['pcs'], rec['max'] = row[5], row[6]
            tot = sum(rec['ch'].values())
            play.append([f['name'], f'{per[4:]}/{per[:4]}', PN[p], '(part)', '', pill(act, ACT_CLS[act]), frm, f'Pcs {row[5]}, Max {row[6]}', rec['max'], tot,
                         pill('OK' if tot <= rec['max'] else 'NG', 'p-ok' if tot <= rec['max'] else 'p-ng')])
        else:
            p = next(q for q in PN if PN[q].replace('-', '') == row[2])
            code = next(c for c in BP if BP[c] == row[5])
            rec = ap[per].setdefault(p, dict(pcs=None, max=None, ch={}))
            old = rec['ch'].get((code, row[6]))
            if row[8] == 0:
                rec['ch'][(code, row[6])] = 0   # the Buyer-PD stays in AP POLE with 0
                act = 'Delete'
            else:
                rec['ch'][(code, row[6])] = row[8]
                act = 'Add' if old is None else ('Down' if row[8] < old else 'Up')
            tot = sum(rec['ch'].values())
            ok = tot <= rec['max'] if rec['max'] is not None else tot == 0
            play.append([f['name'], f'{per[4:]}/{per[:4]}', PN[p], row[5], row[6], pill(act, ACT_CLS[act]), '-' if old is None else old,
                         row[8], rec['max'], tot, pill('OK' if ok else 'NG', 'p-ok' if ok else 'p-ng')])

# ---------- step 6: Period Rollover + GTOPAS ----------
gt_pending = [r for r in STG if r['GTOPAS_SYNC_STATUS'] == '0' and r['PERIOD'] == NXT]
gt_parts = sorted({r['p'] for r in gt_pending})
nsp_dest = {(PN[p], c) for (p, c, o), v in dnxt.items() if v >= 1}
gts = set(gt_before)
compare = []
for p in gt_parts:
    for c in DORD:
        k = (PN[p], c)
        inn, ing = k in nsp_dest, k in gts
        if not (inn or ing):
            continue
        compare.append([PN[p], c, 'Y' if inn else 'N', 'Y' if ing else 'N', 'Keep' if inn and ing else 'Add' if inn else 'Delete'])
gt_after = sorted(nsp_dest | {k for k in gts if k[0] not in {PN[p] for p in gt_parts}})
for r in STG:
    if r['GTOPAS_SYNC_STATUS'] == '0' and r['PERIOD'] == NXT:
        r['GTOPAS_SYNC_STATUS'], r['GTOPAS_SYNC_DT'], r['GTOPAS_SYNC_RUN_ID'], r['CHANGED_BY'], r['CHANGED_DT'] = '1', ROLL, RUN_GT, BATCH, ROLL
after_roll = [dict(r) for r in STG]


# ---------- screen status (derived from the staging) ----------
def screen(rows_state, per, p):
    rs = [r for r in rows_state if r['PERIOD'] == per and r['p'] == p]
    ap_ns = any(r['APPOLE_SYNC_STATUS'] == '0' for r in rs)
    gt_ns = any(r['GTOPAS_SYNC_STATUS'] == '0' for r in rs)
    ap_dt = max([r['APPOLE_SYNC_DT'] for r in rs if r['APPOLE_SYNC_DT']], default='')
    gt_dt = max([r['GTOPAS_SYNC_DT'] for r in rs if r['GTOPAS_SYNC_DT']], default='')
    return ('Non Sync' if ap_ns else ('Sync' if ap_dt else '-')), ap_dt, ('Non Sync' if gt_ns else ('Sync' if gt_dt else '-')), gt_dt


def screen_table(state, pers, note_old=None):
    rows = []
    for per in pers:
        for p in PARTS:
            st = newst[p] if per == NXT else ('Active' if p != 'B' else 'Candidate')
            a, ad, g, gd = screen(state, per, p)
            if note_old and per == CUR and p != 'B' and not ad:
                ad = '27-Oct-2026 10:30 (earlier run)'
            if note_old and per == CUR and p != 'B' and not gd:
                gd = '01-Nov-2026 00:10 (earlier run)'
            if a == '-' and note_old and per == CUR and p != 'B':
                a = 'Sync'
            if g == '-' and note_old and per == CUR and p != 'B':
                g = 'Sync'
            rows.append([PN[p], per, st, a, ad, g, gd])

    def cls(r, i):
        return 'r-pend' if 'Non Sync' in (r[3], r[5]) else ''
    return table(['Part No', 'Period', 'Status', 'AP POLE Sync', 'Last Sent AP POLE', 'GTOPAS Sync', 'Last Sent GTOPAS'], rows, cls)


def ap_split(recs, per):
    """AP POLE as two menus: Kanban (parent, LLM9Q910) and Export (Buyer-PD, LLM9Q880)."""
    mm, yy = per[4:], per[:4]
    kan_rows = [[mm, yy, 'P6', PN[p], NAME[p], r['pcs'], r['max'], r['pcs'] * r['max']] for p, r in sorted(recs.items()) if r['max'] is not None]
    exp_rows = [[mm, yy, PN[p].replace('-', ''), BP[c], o, '2', v] for p, r in sorted(recs.items())
                for (c, o), v in sorted(r['ch'].items(), key=lambda x: DORD.index(x[0][0]))]
    return ('<div class="two"><div>' + h3(f'AP POLE Kanban (Cross Dock Kanban Part Master) · Eff. {mm}/{yy}') +
            table(['Effective Month', 'Effective Year', 'Operator ID', 'Part No.', 'Part Name', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty'],
                  kan_rows, lambda r, i: 'r-par') +
            '</div><div>' + h3(f'AP POLE Export (Export Customer Cross Dock Master) · Eff. {mm}/{yy}') +
            table(['Effective Month', 'Effective Year', 'Part No.', 'Buyer-PD', 'Order Type', 'Transport Code', 'Max Shipping Box (RCS)'], exp_rows,
                  lambda r, i: 'r-ng' if exp_rows[i][6] == 0 else '') + '</div></div>')


def ap_table(per):
    return ap_split(ap[per], per)


def ap_before_table():
    return ap_split(ap11, CUR)


EXP_COLS = ['Effective Month', 'Effective Year', 'Part No.', 'Shipping Box Qty', 'Max Shipping Box by Part No.', 'Buyer-PD', 'Order Type', 'Transport Code',
            'Max Shipping Box (RCS)', 'Max Allowance Qty', 'Packing/Pallet Type']
KAN_COLS = ['Effective Month', 'Effective Year', 'Operator ID', 'Part No.', 'Part Name', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty',
            'Packing/Pallet Type … Outer-Qty (empty)']


def sysm(ap_dt, gt_dt, ap_new=False, gt_new=False):
    return table(['Key', 'Value', 'Saved by'], [['APPOLE_LAST_SYNC_DT', ap_dt, '[Sync] / [Re-send last Sync] (XD07 run)'],
                                                ['GTOPAS_LAST_SYNC_DT', gt_dt, '[Sync] for Current / Period Rollover (XD06 run)']],
                 lambda r, i: 'r-pend' if (i == 0 and ap_new) or (i == 1 and gt_new) else '')


# ---------- HTML ----------
def step(no, sid, when, title, who, body):
    return f'''<section class="step" id="{sid}">
  <div class="step-head"><span class="no">{no}</span><div><div class="when">{e(when)} · {e(who)}</div><h2>{e(title)}</h2></div></div>
  <div class="step-body">{body}</div>
</section>'''


def h3(t):
    return f'<h3>{t}</h3>'


def note(t):
    return f'<p class="note">{t}</p>'


S = []
S.append(step(0, 'before', '20-Nov-2026', 'Before day D: only the Current period 202611', 'state', ''.join([
    note('Earlier runs are already sent (their staging rows are 1 Sync and not shown). TB_M_PART_CANDIDATE has no sync column; the screen reads the status from the staging.'),
    h3('TB_M_PART_CANDIDATE (Kanban Crossdock Master) · 202611'), table(KCOLS, list(kcur.values())),
    h3('TB_M_PART_CANDIDATE_DEST (Export Crossdock Master) · 202611'), table(DCOLS, list(dcur.values())),
    h3('GTOPAS WVJA5204 (Depot 01)'), table(['P/No.', 'Destination Code', 'Maker', 'Dom/Os', 'TOPAS Order Type', 'Trans'],
                                            [[a, b, 'A', '2', '*', '2'] for a, b in gt_before]),
    h3('AP POLE before: Eff. 11/2026'), ap_before_table(),
    h3('Screen: Sync status per part (from the staging)'), screen_table([], [CUR], note_old=True),
    h3('System master: last sync date per target'), sysm('27-Oct-2026 10:30', '01-Nov-2026 00:10')])))

S.append(step(1, 'xd05-p1', D5T, 'XD05 process 1: DAD calculation and the Kanban rows of the Next period 202612', 'XD05 batch (day D = 27, system master)', ''.join([
    note('Range = the 6 months before the run month (202605 – 202610). AVG_MAD = total / 6; AVG_MAD ≥ MIN_MAD → Active, else Inactive. A Candidate that passes becomes Active.'),
    h3('Calculation'), table(['Part No', *MONTHS, 'TOTAL_MAD', 'AVG_MAD', 'MIN_MAD', 'Status 202611', 'Status 202612'], calc,
                             lambda r, i: 'r-pend' if r[-1] != r[-2] else ''),
    h3('TB_R_PART_DAD_RESULT (inserted)'), table(RCOLS, dad),
    h3('TB_M_PART_CANDIDATE · 202612 (inserted)'), table(KCOLS, list(knxt.values()), lambda r, i: 'r-pend'),
    h3('TB_H_PART_CANDIDATE_STG_SYNC (inserted)'),
    note('Every staging row carries the PART_STATUS of the part in that period. Active parts get PCS_CASE and MAX_CASE_DAY ADD rows (Kanban, AP POLE file 2). '
         'The Inactive part (DUMMY-003) also gets its Kanban rows: it stays in the AP POLE Kanban of 12/2026. In process 2 its destinations get DELETE rows with PART_STATUS Inactive (Buyer-PD 0).'),
    stg_table([fresh(r) for r in s1])])))

S.append(step(2, 'xd05-p2', D5T, 'XD05 process 2: Export Crossdock Master 202612', 'XD05 batch', ''.join([
    note('Case/Day = share of the result MAD × Max Case/Day, rounded down (min 1), +1 to the largest fraction until the total = Max. Order Type of a new row = **.'),
    h3('Allocation'), table(['Part No', 'Destination', 'Result MAD', 'Target', 'CASE_DAY'], alloc),
    h3('TB_M_PART_CANDIDATE_DEST · 202612 (inserted)'), table(DCOLS, [dst(p, NXT, c, o, v, (BATCH, D5T), (BATCH, D5T)) for (p, c, o), v in dnxt.items()],
                                                             lambda r, i: 'r-pend'),
    h3('TB_H_PART_CANDIDATE_STG_SYNC (inserted)'), note('One C ADD row per destination of an Active part, and one C DELETE row per destination of the Inactive part DUMMY-003 (KOREA, from 202611: OLD 10, NEW 0 → 0 in file 1). AP POLE 0 and GTOPAS 0.'),
    stg_table([fresh(r) for r in s2]),
    h3('Result: TB_H_PART_CANDIDATE_STG_SYNC after XD05 (KANBAN rows + EXPORT rows, 202612)'),
    note('Rule of the PART_STATUS column: Active → the Kanban rows (PCS_CASE, MAX_CASE_DAY) and the Export rows ADD with their Case/Day; '
         'Inactive → the Kanban rows too (the part stays in AP POLE), but every Export row of the part is DELETE with NEW_VALUE 0 (the Buyer-PD stays with 0). Every row of the new period has GTOPAS 0, so the Period Rollover sends every part.'),
    stg_table(sorted([fresh(r) for r in s1 + s2], key=lambda r: (r['PART_NO'], r['LEVEL_TYPE'] != 'P', r['HIST_ID'])))])))

S.append(step(3, 'adjust', ADJ, 'D/S adjusts the Current period 202611 of part A on the screen', DS, ''.join([
    note('Max Case/Day 12 → 11 on the Kanban Crossdock Master; on the Export Crossdock Master JAPAN 6 → 7 and KOREA 6 → 4 (total 11). '
         'Only quantities change: AP POLE 0, GTOPAS NULL (the destinations stay the same).'),
    h3('TB_M_PART_CANDIDATE · 202611 A (updated)'), table(KCOLS, [kcur_adj], lambda r, i: 'r-pend'),
    h3('TB_M_PART_CANDIDATE_DEST · 202611 A (updated)'), table(DCOLS, dcur_adj, lambda r, i: 'r-pend'),
    h3('TB_H_PART_CANDIDATE_STG_SYNC (inserted)'), stg_table([fresh(r) for r in s3]),
    h3('Screen before [Sync]'),
    screen_table([fresh(r) for r in STG], [CUR, NXT], note_old=True)])))

red_rows = [[x['per'], PN[x['p']], LV[x['lvl']], x['code'], x['ot'], x['f'], ', '.join(map(str, x['ids'])),
             '–' if x['ap'] is None else x['ap'], x['nsp'], pill(x['act'], ACT_CLS[x['act']]), x['last'],
             f"<b>{x['seq']}</b>" if x['seq'] != '' else ('– (record only)' if x['f'] == 'PART_STATUS' else '–')] for x in red]
files_html = ''.join(
    f'<p class="note"><span class="pill {"p-down" if f["seq"] == 1 else "p-par" if f["seq"] == 2 else "p-up"}">{f["seq"]}</span> <code>{f["name"]}</code> · '
    f'{"Cross Dock Kanban Part Master" if f["kind"] == "Kanban" else "Export Customer Cross Dock Master"} · Eff. {f["per"][4:]}/{f["per"][:4]}</p>'
    + table(KAN_COLS if f['kind'] == 'Kanban' else EXP_COLS, f['rows'], lambda r, i, k=f['kind']: 'r-par' if k == 'Kanban' else '')
    for f in files)
S.append(step(4, 'sync', SYNC, '[Sync]: NSP reduces the staging, sets SEND_SEQ and makes the upload files', f'{DS} clicks [Sync] · run {RUN_AP}', ''.join([
    h3('Rows taken from the staging'),
    note('Rule: <b>CREATED_DT &gt; APPOLE_LAST_SYNC_DT</b> (27-Oct-2026 10:30, saved by the last run) <b>and CREATED_DT ≤ the click</b> (27-Nov-2026 10:00). '
         f'Here: HIST_ID {STG[0]["HIST_ID"]} – {s3[-1]["HIST_ID"]} (XD05 02:00 and the adjustment 09:00). After the files are made, NSP saves 27-Nov-2026 10:00 as the new APPOLE_LAST_SYNC_DT.'),
    sysm('27-Nov-2026 10:00', '01-Nov-2026 00:10', ap_new=True),
    note('Per key: AP POLE value = OLD of the first row, NSP value = NEW of the last row. '
         'SEND_SEQ = upload file: 1 Export → 2 Kanban → 3 Export. File 1: the EXPORT rows of a part whose Max goes down (before its Kanban row). '
         'File 3: the EXPORT rows of every other part (Max up, new part, or no Kanban row: moves between destinations, deletes, Inactive). '
         'Inside a file the rows of a part going down / deleted come first, then up / added. One file per period + SEND_SEQ, Current before Next.'),
    h3('Reduction per key'),
    table(['Period', 'Part No', 'Level', 'Buyer-PD', 'OT', 'Field', 'HIST_ID', 'AP POLE value', 'NSP value', 'Action', 'Last HIST_ID', 'SEND_SEQ'], red_rows,
          lambda r, i: 'r-par' if red[i]['lvl'] == 'P' else '', raw={9, 11}, sim={7, 8, 9}),
    note('Yellow headers (AP POLE value, NSP value, Action) help to read this simulation only: NSP works them out at [Sync] and does not store them. The table keeps ACTION (ADD / EDIT / DELETE), OLD_VALUE, NEW_VALUE and SEND_SEQ.'),
    h3('GTOPAS at this [Sync]'),
    note('Current 202611 has no row with GTOPAS_SYNC_STATUS 0 (part A changed only quantities) → XD06 does not run. '
         'The 202612 rows with GTOPAS 0 wait for the Period Rollover.' if not gt_cur_pending else ''),
    h3('TB_H_PART_CANDIDATE_STG_SYNC after [Sync] (before the bot starts)'), stg_table(after_sync),
    h3(f'Upload files made by NSP ({len(files)} files, from the stored templates)'), files_html])))

S.append(step(5, 'rpa-ap', SYNC, 'RPA AP POLE (XD07): uploads the files one at a time', 'Power Automate bot', ''.join([
    note('The bot uploads the files in the order of their names and waits for each result. AP POLE checks every row: total Max Shipping Box (RCS) of the part ≤ Max Shipping Box Qty.'),
    table(['File', 'Eff.', 'Part No', 'Buyer-PD', 'OT', 'Action', 'Before', 'After', 'Max in AP POLE', 'Total Buyer-PD', 'Check'], play,
          lambda r, i: 'r-par' if r[3] == '(part)' else '', raw={5, 10}),
    h3('AP POLE after the run: Eff. 11/2026'), ap_table(CUR),
    h3('AP POLE after the run: Eff. 12/2026 (DUMMY-003 Inactive: part kept in Kanban, KOREA 0 in Export)'), ap_table(NXT),
    note(f'E-mail: <b>[Crossdock Sync][AP POLE][SUCCESS] Run {RUN_AP}</b> – {len(files)} file(s), {len(play)} row(s). The bot writes nothing back to NSP.'),
    h3('Screen after [Sync]'), screen_table(after_sync, [CUR, NXT], note_old=True)])))

S.append(step(6, 'rollover', ROLL, 'Period Rollover (XD05 process 3) → RPA GTOPAS (XD06)', 'XD05 batch, then the bot', ''.join([
    note('202612 becomes Current, 202611 becomes Past. Every 202612 part with a staging row GTOPAS_SYNC_STATUS 0 is sent: '
         f'{", ".join(PN[p] for p in gt_parts)}. The bot takes the destinations with CASE_DAY ≥ 1 of 202612 and compares with GTOPAS (P/No. + Destination Code).'),
    note('Rows taken: <b>PERIOD = 202612 and CREATED_DT &gt; GTOPAS_LAST_SYNC_DT</b> (01-Nov-2026 00:10) and ≤ the rollover time. Then GTOPAS_LAST_SYNC_DT = 01-Dec-2026 00:10.'),
    sysm('27-Nov-2026 10:00', '01-Dec-2026 00:10', gt_new=True),
    '<p class="warn">Watch point: if a [Sync] had sent a Current GTOPAS change on 27-Nov 10:00, GTOPAS_LAST_SYNC_DT would be 27-Nov 10:00 and the 202612 rows of XD05 '
    '(created 27-Nov 02:00) would be skipped at the rollover. So the last sync date of GTOPAS is kept <b>per period</b> (or the rollover takes every GTOPAS row of the new period, '
    'whatever its date).</p>',
    h3('Work sheet GTOPAS Compare'),
    table(['P/No.', 'Destination Code', 'In NSP 202612', 'In GTOPAS', 'Action'], [r[:4] + [pill(r[4], ACT_CLS[r[4]] if r[4] != 'Delete' else 'p-del')] for r in compare],
          lambda r, i: {'Keep': 'r-ok', 'Add': 'r-pend', 'Delete': 'r-ng'}[compare[i][4]], raw={4}),
    '<div class="two">', '<div>', h3('GTOPAS WVJA5204 after XD06'),
    table(['P/No.', 'Destination Code', 'Maker', 'Dom/Os', 'TOPAS Order Type', 'Trans'], [[a, b, 'A', '2', '*', '2'] for a, b in gt_after],
          lambda r, i: '' if (r[0], r[1]) in set(gt_before) else 'r-pend'), '</div>', '</div>',
    h3('TB_H_PART_CANDIDATE_STG_SYNC: GTOPAS columns filled'),
    stg_table([r for r in after_roll if r['GTOPAS_SYNC_RUN_ID'] == RUN_GT]),
    h3(f'TB_H_PART_CANDIDATE_STG_SYNC: all rows from HIST_ID 101 after the rollover ({len(after_roll)} rows)'),
    note('Green = APPOLE_SYNC_STATUS 1 Sync. GTOPAS_SYNC_STATUS: 1 for the rows of 202612 sent by the rollover, empty (NULL) for rows that are not for GTOPAS (quantity changes).'),
    stg_table(sorted(after_roll, key=lambda r: r['HIST_ID'])),
    note(f'E-mail: <b>[Crossdock Sync][GTOPAS][SUCCESS] Run {RUN_GT}</b> – {len(gt_parts)} part(s): '
         f'{sum(1 for r in compare if r[4] == "Add")} Add, {sum(1 for r in compare if r[4] == "Delete")} Delete, {sum(1 for r in compare if r[4] == "Keep")} Keep.')])))

S.append(step(7, 'end', '01-Dec-2026', 'End state: 202612 is the Current period', 'state', ''.join([
    h3('Screen: Sync status per part (from the staging)'), screen_table(after_roll, [NXT]),
    h3('TB_H_PART_CANDIDATE_STG_SYNC (all rows of this example)'), stg_table(after_roll)])))

# ================= next month: December 2026 (Current 202612) -> XD05 makes 202701 -> rollover 01-Jan-2027 =================
C2, N2 = '202612', '202701'
T10, T15, S15 = '10-Dec-2026 09:00', '15-Dec-2026 09:00', '15-Dec-2026 10:00'
D27, S27 = '27-Dec-2026 02:00', '27-Dec-2026 10:00'
R1J = '01-Jan-2027 00:10'
RUN3, RUN4, RUN5 = '20261215100000', '20261227100000', '20270101001000'
ST2 = dict(newst)                               # status of 202612
mk = {p: dict(pcs=PARTS[p]['pcs'], max=PARTS[p]['max']) for p in PARTS}   # Kanban 202612 (from XD05)
md = dict(dnxt)                                  # Export 202612 (DUMMY-003 KOREA removed)


def run_ap(pending, state, run, dt, by):
    """[Sync] for AP POLE: reduction per key, SEND_SEQ, staging update, files, play row by row on `state` {period: {part: rec}}."""
    groups = {}
    for r in pending:
        groups.setdefault((r['PERIOD'], r['p'], r['LEVEL_TYPE'], r['DEST_CODE'], r['ORDER_TYPE'], r['FIELD_NAME']), []).append(r)
    red2 = []
    for key, g in groups.items():
        a, b = g[0]['OLD_VALUE'], g[-1]['NEW_VALUE']
        a = None if a == '' else a
        if g[-1]['ACTION'] == 'DELETE':
            act = '-' if a is None else 'Delete'
        elif a is None:
            act = 'Add'
        else:
            act = 'Down' if b < a else 'Up' if b > a else '-'
        red2.append(dict(per=key[0], p=key[1], lvl=key[2], code=key[3], ot=key[4], f=key[5], ids=[x['HIST_ID'] for x in g], ap=a, nsp=b, act=act,
                         last=g[-1]['HIST_ID'], seq='', rows=g))
    mdown = {(x['per'], x['p']) for x in red2 if x['lvl'] == 'P' and x['f'] == 'MAX_CASE_DAY' and x['act'] == 'Down'}
    for x in red2:
        if x['act'] != '-':
            x['seq'] = 2 if x['lvl'] == 'P' else (1 if (x['per'], x['p']) in mdown else 3)
        for r in x['rows']:
            r['APPOLE_SYNC_STATUS'] = '1' if r['HIST_ID'] == x['last'] else '2'
            r['APPOLE_SYNC_DT'], r['APPOLE_SYNC_RUN_ID'], r['CHANGED_BY'], r['CHANGED_DT'] = dt, run, by, dt
            if r['HIST_ID'] == x['last']:
                r['SEND_SEQ'] = x['seq']
    fl, pl = [], []
    for per in sorted({x['per'] for x in red2}):
        st = state.setdefault(per, {})
        for seq in (1, 2, 3):
            rows = [x for x in red2 if x['per'] == per and x['seq'] == seq]
            if not rows:
                continue
            mm, yy = per[4:], per[:4]
            if seq == 2:
                out = []
                for p in sorted({x['p'] for x in rows}):
                    out.append([mm, yy, 'P6', PN[p], NAME[p], mk2[per][p]['pcs'], mk2[per][p]['max'], mk2[per][p]['pcs'] * mk2[per][p]['max'], ''])
                    rec = st.setdefault(p, dict(pcs=None, max=None, ch={}))
                    act = 'Edit' if rec['max'] is not None else 'Add part'
                    frm = '-' if rec['max'] is None else f"Max {rec['max']}"
                    rec['pcs'], rec['max'] = mk2[per][p]['pcs'], mk2[per][p]['max']
                    tot = sum(rec['ch'].values())
                    pl.append([f'LLM9Q910_{run}_{per}_2.xls', f'{mm}/{yy}', PN[p], '(part)', '', pill(act, ACT_CLS[act]), frm,
                               f"Pcs {rec['pcs']}, Max {rec['max']}", rec['max'], tot, pill('OK' if tot <= rec['max'] else 'NG', 'p-ok' if tot <= rec['max'] else 'p-ng')])
                fl.append(dict(name=f'LLM9Q910_{run}_{per}_2.xls', kind='Kanban', per=per, seq=2, rows=out))
            else:
                rows = sorted(rows, key=lambda x: (x['p'], x['act'] not in ('Down', 'Delete'), DORD.index(x['code'])))
                out = []
                for x in rows:
                    v = 0 if x['act'] == 'Delete' else x['nsp']
                    out.append([mm, yy, PN[x['p']].replace('-', ''), '', '', BP[x['code']], x['ot'], '2', v, '', ''])
                    rec = st.setdefault(x['p'], dict(pcs=None, max=None, ch={}))
                    old = rec['ch'].get((x['code'], x['ot']))
                    rec['ch'][(x['code'], x['ot'])] = v
                    tot = sum(rec['ch'].values())
                    ok = rec['max'] is not None and tot <= rec['max']
                    pl.append([f'LLM9Q880_{run}_{per}_{seq}.xls', f'{mm}/{yy}', PN[x['p']], x['code'], x['ot'], pill(x['act'], ACT_CLS[x['act']]),
                               '-' if old is None else old, v, rec['max'], tot, pill('OK' if ok else 'NG', 'p-ok' if ok else 'p-ng')])
                fl.append(dict(name=f'LLM9Q880_{run}_{per}_{seq}.xls', kind='Export', per=per, seq=seq, rows=out))
    return red2, fl, pl


def run_gt(pending, dests, gts, run, dt, by):
    parts = sorted({r['p'] for r in pending})
    nsp = {(PN[p], c) for (p, c, o), v in dests.items() if v >= 1 and p in parts}
    cmp_ = []
    for p in parts:
        for c in DORD:
            k = (PN[p], c)
            if k in nsp or k in gts:
                cmp_.append([PN[p], c, 'Y' if k in nsp else 'N', 'Y' if k in gts else 'N', 'Keep' if k in nsp and k in gts else 'Add' if k in nsp else 'Delete'])
    after = sorted(nsp | {k for k in gts if k[0] not in {PN[p] for p in parts}})
    for r in pending:
        r['GTOPAS_SYNC_STATUS'], r['GTOPAS_SYNC_DT'], r['GTOPAS_SYNC_RUN_ID'], r['CHANGED_BY'], r['CHANGED_DT'] = '1', dt, run, by, dt
    return parts, cmp_, after


def red_table(rd):
    rows = [[x['per'], PN[x['p']], LV[x['lvl']], x['code'], x['ot'], x['f'], ', '.join(map(str, x['ids'])), '–' if x['ap'] is None else x['ap'], x['nsp'],
             pill(x['act'], ACT_CLS[x['act']]), x['last'], f"<b>{x['seq']}</b>" if x['seq'] != '' else '–'] for x in rd]
    return table(['Period', 'Part No', 'Level', 'Buyer-PD', 'OT', 'Field', 'HIST_ID', 'AP POLE value', 'NSP value', 'Action', 'Last HIST_ID', 'SEND_SEQ'], rows,
                 lambda r, i: 'r-par' if rd[i]['lvl'] == 'P' else '', raw={9, 11}, sim={7, 8, 9})


def files_table(fl):
    return ''.join(
        f'<p class="note"><span class="pill {"p-down" if f["seq"] == 1 else "p-par" if f["seq"] == 2 else "p-up"}">{f["seq"]}</span> <code>{f["name"]}</code> · '
        f'{"Cross Dock Kanban Part Master" if f["kind"] == "Kanban" else "Export Customer Cross Dock Master"} · Eff. {f["per"][4:]}/{f["per"][:4]}</p>'
        + table(KAN_COLS if f['kind'] == 'Kanban' else EXP_COLS, f['rows'], lambda r, i, k=f['kind']: 'r-par' if k == 'Kanban' else '') for f in fl)


def play_table(pl):
    return table(['File', 'Eff.', 'Part No', 'Buyer-PD', 'OT', 'Action', 'Before', 'After', 'Max in AP POLE', 'Total Buyer-PD', 'Check'], pl,
                 lambda r, i: 'r-par' if r[3] == '(part)' else '', raw={5, 10})


def ap_table2(st, per):
    return ap_split(st.get(per, {}), per)


def gt_table(rows, before):
    return table(['P/No.', 'Destination Code', 'Maker', 'Dom/Os', 'TOPAS Order Type', 'Trans'], [[a, b, 'A', '2', '*', '2'] for a, b in rows],
                 lambda r, i: '' if (r[0], r[1]) in set(before) else 'r-pend')


def cmp_table(c):
    return table(['P/No.', 'Destination Code', 'In NSP', 'In GTOPAS', 'Action'], [r[:4] + [pill(r[4], ACT_CLS[r[4]] if r[4] != 'Delete' else 'p-del')] for r in c],
                 lambda r, i: {'Keep': 'r-ok', 'Add': 'r-pend', 'Delete': 'r-ng'}[c[i][4]], raw={4})


def screen2(per, stat):
    rows = []
    for p in PARTS:
        rs = [r for r in STG if r['PERIOD'] == per and r['p'] == p]
        a0 = any(r['APPOLE_SYNC_STATUS'] == '0' for r in rs)
        g0 = any(r['GTOPAS_SYNC_STATUS'] == '0' for r in rs)
        ad = max([r['APPOLE_SYNC_DT'] for r in rs if r['APPOLE_SYNC_DT']], key=lambda d: (d[7:11], d[3:6] == 'Dec', d), default='')
        gd = max([r['GTOPAS_SYNC_DT'] for r in rs if r['GTOPAS_SYNC_DT']], key=lambda d: (d[7:11], d[3:6] == 'Dec', d), default='')
        rows.append([PN[p], per, stat[p], 'Non Sync' if a0 else 'Sync' if ad else '-', ad, 'Non Sync' if g0 else 'Sync' if gd else '-', gd])
    return table(['Part No', 'Period', 'Status', 'AP POLE Sync', 'Last Sent AP POLE', 'GTOPAS Sync', 'Last Sent GTOPAS'], rows,
                 lambda r, i: 'r-pend' if 'Non Sync' in (r[3], r[5]) else '')


# ---- 8: December changes on the Current period 202612 ----
e8 = [stg('B', C2, 'P', 'MAX_CASE_DAY', 'EDIT', 6, 8, 'SCREEN', DS, T10),
      stg('B', C2, 'C', 'CASE_DAY', 'EDIT', 2, 4, 'SCREEN', DS, T10, code='USA', ot='**'),
      stg('A', C2, 'C', 'CASE_DAY', 'EDIT', 4, 3, 'SCREEN', DS, T10, code='KOREA', ot='**'),
      stg('A', C2, 'C', 'CASE_DAY', 'EDIT', 2, 3, 'SCREEN', DS, T10, code='TAIWAN', ot='**'),
      stg('D', C2, 'P', 'MAX_CASE_DAY', 'EDIT', 8, 10, 'SCREEN', DS, T15),
      stg('D', C2, 'C', 'CASE_DAY', 'ADD', '', 2, 'SCREEN', DS, T15, code='KOREA', ot='**', gt='0')]
mk['B']['max'], mk['D']['max'] = 8, 10
md[('B', 'USA', '**')], md[('A', 'KOREA', '**')], md[('A', 'TAIWAN', '**')], md[('D', 'KOREA', '**')] = 4, 3, 3, 2
mk2 = {C2: mk}
snap8 = [fresh(r) for r in e8]

# ---- 9: [Sync] 15-Dec ----
pend9 = [r for r in STG if r['APPOLE_SYNC_STATUS'] == '0']
apst = {C2: {p: dict(pcs=v['pcs'], max=v['max'], ch=dict(v['ch'])) for p, v in ap[NXT].items()}}
red9, files9, play9 = run_ap(pend9, apst, RUN3, S15, DS)
gt_before9 = list(gt_after)
gpend9 = [r for r in STG if r['GTOPAS_SYNC_STATUS'] == '0' and r['PERIOD'] == C2]
gparts9, cmp9, gt_after9 = run_gt(gpend9, md, set(gt_before9), RUN3, S15, DS)
after9 = [dict(r) for r in STG if r['HIST_ID'] >= e8[0]['HIST_ID']]

# ---- 10: XD05 27-Dec: Next period 202701 ----
st3 = {'A': 'Active', 'B': 'Active', 'C': 'Inactive', 'D': 'Active'}
mk3 = {p: dict(mk[p]) for p in PARTS}
alloc3, d3 = [], {}
for p in PARTS:
    if st3[p] != 'Active':
        continue
    mads = {}
    for q, c, mad, months in DEMAND:
        if q == p:
            mads[c] = mads.get(c, 0) + mad * len(months)
    for c, m, tgt, cd in allocate(list(mads.items()), mk3[p]['max']):
        alloc3.append([PN[p], c, m, tgt, cd])
        d3[(p, c, '**')] = cd
s10 = []
for p in PARTS:
    s10.append(stg(p, N2, 'P', 'PCS_CASE', 'ADD', '', mk3[p]['pcs'], 'BATCH', BATCH, D27, ps=st3[p]))
    s10.append(stg(p, N2, 'P', 'MAX_CASE_DAY', 'ADD', '', mk3[p]['max'], 'BATCH', BATCH, D27, ps=st3[p]))
for (p, c, o), v in sorted(d3.items(), key=lambda x: (x[0][0], DORD.index(x[0][1]))):
    s10.append(stg(p, N2, 'C', 'CASE_DAY', 'ADD', '', v, 'BATCH', BATCH, D27, code=c, ot=o, gt='0', ps=st3[p]))
for (p, c, o), v in md.items():                 # Inactive part: only destinations still > 0 in the previous period -> DELETE (0)
    if st3[p] == 'Inactive' and v >= 1:
        s10.append(stg(p, N2, 'C', 'CASE_DAY', 'DELETE', v, 0, 'BATCH', BATCH, D27, code=c, ot=o, gt='0', ps=st3[p]))
snap10 = [fresh(r) for r in s10]
mk2[N2] = mk3

# ---- 11: [Sync] 27-Dec ----
pend11 = [r for r in STG if r['APPOLE_SYNC_STATUS'] == '0']
red11, files11, play11 = run_ap(pend11, apst, RUN4, S27, DS)

# ---- 12: rollover 01-Jan-2027 ----
gpend12 = [r for r in STG if r['GTOPAS_SYNC_STATUS'] == '0' and r['PERIOD'] == N2]
gparts12, cmp12, gt_after12 = run_gt(gpend12, d3, set(gt_after9), RUN5, R1J, BATCH)
after12 = [dict(r) for r in STG]

S.append(step(8, 'dec-adjust', '10 / 15-Dec-2026', 'Next month: changes on the Current period 202612', DS, ''.join([
    note('December: 202612 is Current. 10-Dec: DUMMY-002 Max 6 → 8 and USA 2 → 4 (Max goes up); DUMMY-001 KOREA 4 → 3 and TAIWAN 2 → 3 (move between destinations, '
         'no Kanban row). 15-Dec: DUMMY-004 Max 8 → 10 and a new destination KOREA = 2 (EXPORT ADD → GTOPAS 0).'),
    h3('TB_H_PART_CANDIDATE_STG_SYNC (inserted)'), stg_table(snap8),
    h3('Screen before [Sync]'), screen2(C2, ST2)])))

S.append(step(9, 'dec-sync', S15, '[Sync] 15-Dec: AP POLE 12/2026 and GTOPAS for the Current period', f'{DS} · run {RUN3}', ''.join([
    note('Rows taken: APPOLE_SYNC_STATUS 0 with CREATED_DT &gt; APPOLE_LAST_SYNC_DT (27-Nov-2026 10:00) and ≤ 15-Dec-2026 10:00. No part has its Max going down, '
         'so there is no file 1: the Kanban file goes first, then every EXPORT row in file 3 (per part: down first, then up / add).'),
    h3('Reduction per key'), red_table(red9),
    h3(f'Upload files ({len(files9)})'), files_table(files9),
    h3('RPA AP POLE: row by row'), play_table(play9),
    h3('AP POLE after the run: Eff. 12/2026'), ap_table2(apst, C2),
    h3('GTOPAS at the same [Sync] (Current period)'),
    note(f'Rows with GTOPAS_SYNC_STATUS 0 and PERIOD 202612: HIST {", ".join(str(r["HIST_ID"]) for r in gpend9)} (DUMMY-004 KOREA ADD). '
         'The bot compares the destinations with CASE_DAY ≥ 1 of these parts. Then GTOPAS_LAST_SYNC_DT = 15-Dec-2026 10:00.'),
    '<div class="two"><div>', h3('Work sheet GTOPAS Compare'), cmp_table(cmp9), '</div><div>', h3('GTOPAS WVJA5204 after XD06'), gt_table(gt_after9, gt_before9), '</div></div>',
    h3('TB_H_PART_CANDIDATE_STG_SYNC after [Sync]'), stg_table(after9),
    sysm('15-Dec-2026 10:00', '15-Dec-2026 10:00', ap_new=True, gt_new=True)])))

S.append(step(10, 'dec-xd05', D27, 'XD05 on day D: Next period 202701', 'XD05 batch', ''.join([
    note('Status of 202701 (calculation 202606 – 202611, assumed): DUMMY-001, 002, 004 Active, DUMMY-003 stays Inactive. Pcs/Case and Max Case/Day are taken from the '
         'Current master (202612), the Case/Day of each destination is calculated again. DUMMY-004 KOREA has no demand, so it is not in 202701. '
         'DUMMY-003 (Inactive) has no destination left in 202612 (KOREA was set to 0 last month), so it gets only its Kanban rows: '
         'AP POLE 01/2027 has the part without Buyer-PD, because no Export row is written for it.'),
    h3('Allocation 202701'), table(['Part No', 'Destination', 'Result MAD', 'Target', 'CASE_DAY'], alloc3),
    h3('TB_H_PART_CANDIDATE_STG_SYNC (inserted)'), stg_table(snap10)])))

S.append(step(11, 'dec-sync2', S27, '[Sync] 27-Dec: AP POLE 01/2027', f'{DS} · run {RUN4}', ''.join([
    note('Only the 202701 rows are Non Sync. Every part is new for Eff. 01/2027: file 2 (Kanban, Add part, DUMMY-003 included) then file 3 (Export). '
         'GTOPAS: no 202612 row with GTOPAS 0 → XD06 does not run; the 202701 rows wait for the rollover.'),
    h3('Reduction per key'), red_table(red11),
    h3(f'Upload files ({len(files11)})'), files_table(files11),
    h3('RPA AP POLE: row by row'), play_table(play11),
    h3('AP POLE after the run: Eff. 01/2027 (DUMMY-003 in Kanban only: no Buyer-PD)'), ap_table2(apst, N2)])))

S.append(step(12, 'jan-rollover', R1J, 'Period Rollover 01-Jan-2027 → RPA GTOPAS', 'XD05 batch, then the bot', ''.join([
    note(f'202701 becomes Current. Rows with GTOPAS 0 and PERIOD 202701: HIST {gpend12[0]["HIST_ID"]} – {gpend12[-1]["HIST_ID"]} → parts {", ".join(PN[p] for p in gparts12)}. '
         'DUMMY-003 has no GTOPAS row (Kanban rows only) and is already out of GTOPAS. The 202701 rows were created on 27-Dec 02:00, after GTOPAS_LAST_SYNC_DT (15-Dec 10:00).'),
    '<div class="two"><div>', h3('Work sheet GTOPAS Compare'), cmp_table(cmp12), '</div><div>', h3('GTOPAS WVJA5204 after XD06'), gt_table(gt_after12, gt_after9), '</div></div>',
    sysm('27-Dec-2026 10:00', '01-Jan-2027 00:10', gt_new=True)])))

S.append(step(13, 'jan-end', '01-Jan-2027', 'End state: 202701 is the Current period', 'state', ''.join([
    h3('Screen: Sync status per part'), screen2(N2, st3),
    h3(f'TB_H_PART_CANDIDATE_STG_SYNC: all rows ({len(after12)})'), stg_table(sorted(after12, key=lambda r: r['HIST_ID']))])))

NAV = [('before', '0 Before'), ('xd05-p1', '1 XD05 P1'), ('xd05-p2', '2 XD05 P2'), ('adjust', '3 Adjust'), ('sync', '4 [Sync]'), ('rpa-ap', '5 RPA AP POLE'),
       ('rollover', '6 Rollover + GTOPAS'), ('end', '7 End Nov'), ('dec-adjust', '8 Dec changes'), ('dec-sync', '9 [Sync] 15-Dec'), ('dec-xd05', '10 XD05 27-Dec'), ('dec-sync2', '11 [Sync] 27-Dec'), ('jan-rollover', '12 Rollover Jan'), ('jan-end', '13 End')]
css = open(os.path.join(HERE, '..', 'staging_sync', 'staging_sync.html')).read()
css = css[css.index('<style>') + 7:css.index('</style>')]
css += '''
.nav { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg); padding-block: 10px; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 6px; }
.nav a { font: 500 .82rem/1 var(--f-body); padding: 8px 11px; border-radius: 6px; border: 1px solid var(--line); color: var(--accent); text-decoration: none; background: var(--surface); }
.nav a:hover { background: var(--accent-soft); }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }
.step { display: grid; gap: 12px; scroll-margin-top: 70px; }
.step-head { display: flex; gap: 12px; align-items: center; }
.step-head .no { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; font: 700 1rem/1 var(--f-display); background: var(--accent); color: var(--surface); flex: none; }
.when { font: 600 .72rem/1.4 var(--f-body); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); }
.step-body { display: grid; gap: 10px; min-width: 0; padding-left: 46px; }
@media (max-width: 700px) { .step-body { padding-left: 0; } }
.th-sim { background: #fff1c2 !important; color: #6b4e00 !important; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 16px; }
@media (max-width: 460px) { .two { grid-template-columns: 1fr; } }
'''
page = f'''<title>Crossdock Full Sync Flow</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@600;700&display=swap">
<style>{css}</style>
<div class="wrap">
  <header>
    <span class="eyebrow">Crossdock Master · XD05 → [Sync] → XD07 AP POLE → Period Rollover → XD06 GTOPAS · proposal 21-Nov</span>
    <h1>Full sync flow with the staging table</h1>
    <p class="sub">Current period 202611, day D = 27-Nov-2026, Next period 202612, Period Rollover 01-Dec-2026. TB_M_PART_CANDIDATE has no sync column;
      <code>TB_H_PART_CANDIDATE_STG_SYNC</code> keeps every change with the Sync Status, date and run ID of AP POLE and GTOPAS.
      AP POLE gets upload files made by NSP (1 Export only for a part whose Max goes down → 2 Kanban → 3 Export for every other part); GTOPAS compares part + destinations.</p>
    <div class="tbl"><table><thead><tr><th>Part</th><th>Part No</th><th>Nov</th><th>Story</th></tr></thead><tbody>
      <tr><td>A</td><td>{PN["A"]}</td><td>Active</td><td class="wrap-txt">Stays Active. Nov adjusted on 27-Nov (Max 12 → 11, JAPAN 7, KOREA 4). Dec mapping changes (KOREA 4, TAIWAN added)</td></tr>
      <tr><td>B</td><td>{PN["B"]}</td><td>Candidate</td><td class="wrap-txt">Candidate → Active by XD05 for Dec: new part in AP POLE 12/2026 and in GTOPAS</td></tr>
      <tr><td>C</td><td>{PN["C"]}</td><td>Active</td><td class="wrap-txt">Active → Inactive by XD05 for Dec: stays in the AP POLE Kanban 12/2026 with Buyer-PD KOREA 0; deleted in GTOPAS on 1-Dec</td></tr>
      <tr><td>D</td><td>{PN["D"]}</td><td>Active</td><td class="wrap-txt">No change: AP POLE 12/2026 still added; GTOPAS compare Keep</td></tr>
    </tbody></table></div>
    <div class="legend">
      <span><i class="sw" style="background:var(--pend-soft)"></i>inserted / changed / Non Sync</span>
      <span><i class="sw" style="background:var(--ok-soft)"></i>Sync / Keep / OK</span>
      <span><i class="sw" style="background:var(--ng-soft)"></i>delete</span>
      <span><i class="sw" style="background:var(--parent-soft)"></i>parent (Kanban)</span>
    </div>
  </header>
  <nav class="nav" aria-label="Steps">{"".join(f'<a href="#{a}">{e(b)}</a>' for a, b in NAV)}</nav>
  {"".join(S)}
</div>'''
open(os.path.join(HERE, 'full_flow.html'), 'w').write(page)
print('ok', len(page), 'files', [f['name'] for f in files], 'ng', sum('p-ng' in r[10] for r in play))
