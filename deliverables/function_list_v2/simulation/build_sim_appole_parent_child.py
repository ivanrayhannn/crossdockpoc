"""Simulation (20-Nov, discussion, not yet in the UISS): XD07 reads TB_M_PART_CANDIDATE (parent) and TB_M_PART_CANDIDATE_DEST (child)
directly (TB_H_PART_CANDIDATE is an update table, history only). New columns decide the order of the changes in AP POLE:
  TB_M_PART_CANDIDATE      APPOLE_FIRST (P = parent first, C = child first), APPOLE_SENT_PCS_CASE, APPOLE_SENT_MAX_CASE_DAY
  TB_M_PART_CANDIDATE_DEST APPOLE_SENT_CASE_DAY, DELETE_FLAG
Rule: at every step the total Case/Day of the children in AP POLE <= Max Shipping Box Qty of the parent.
Run: python3 build_sim_appole_parent_child.py"""
import os
import sys
from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'erd'))
from build_erd import load_tables                      # noqa: E402
from build_sim_fb182 import BAD, HOLD, OK, sheet, table  # noqa: E402

OUT = os.path.join(HERE, 'XD07_Simulation_AP_POLE_Parent_Child.xlsx')
T = load_tables()[0]
PART, PER, MM = 'PART-X', '202611', '11'
BP = {'9722D10': '9722D-10', '9715310': '97153-10', '9811110': '98111-10', '9618201': '96182-01', '9533101': '95331-01'}
NAME = {'9722D10': 'D1 JPN', '9715310': 'D2 KR', '9811110': 'D3 TW', '9618201': 'D4 US', '9533101': 'D5 TH'}
D1, D2, D3, D4, D5 = BP.keys()
SENT_DT, SAVE_DT, SYNC_DT = '27-Oct-2026 10:30', '27-Nov-2026 09:00', '27-Nov-2026 10:00'

KAN_COLS = ['PART_NO', 'PERIOD', 'PCS_CASE', 'MAX_CASE_DAY', 'APPOLE_SYNC_STATUS', 'APPOLE_SYNC_DT', 'APPOLE_FIRST', 'APPOLE_SENT_PCS_CASE',
            'APPOLE_SENT_MAX_CASE_DAY', 'CHANGED_BY', 'CHANGED_DT']
DEST_COLS = ['PART_NO', 'PERIOD', 'DEST_CODE', 'ORDER_TYPE', 'CASE_DAY', 'APPOLE_SENT_CASE_DAY', 'DELETE_FLAG', 'Action (Export Excel)', 'Step']
STEP_COLS = ['No', 'Step', 'Level', 'Buyer PD', 'Order Type', 'Action', 'From', 'To', 'Max in AP POLE', 'Total children in AP POLE', 'Check total <= Max']
AP_COLS = ['Eff. MM', 'Eff. YYYY', 'Part No', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Buyer PD', 'Order Type',
           'Max Shipping Box Qty (Buyer PD)', 'Max Allowance Qty (Buyer PD)']


def fills(n, f):
    return {i: f for i in range(1, n + 1)}


def first(sent_max, new_max):
    """APPOLE_FIRST: P for a new period (nothing sent) or Max up; C for Max down or Max equal (children only / Pcs/Case only)."""
    return 'P' if sent_max is None or new_max > sent_max else 'C'


def child_action(sent, new, deleted):
    if deleted:
        return 'Delete'
    if sent is None:
        return 'Add'
    return 'Down' if new < sent else 'Up' if new > sent else '-'


class Case:
    """sent: (pcs, max, {(dest, ot): case}) as in AP POLE; new: (pcs, max, {(dest, ot): case}) in NSP after the save."""

    def __init__(self, title, story, sent, new, period=PER, mm=MM, notes=()):
        self.title, self.story, self.sent, self.new, self.period, self.mm, self.notes = title, story, sent, new, period, mm, list(notes)
        s_pcs, s_max, s_ch = sent if sent else (None, None, {})
        n_pcs, n_max, n_ch = new
        self.first = first(s_max, n_max)
        self.rows = []      # (key, sent, new, deleted, action)
        for k in sorted(set(s_ch) | set(n_ch), key=lambda x: (list(BP).index(x[0]), x[1] != '**')):
            dl = k not in n_ch
            a = child_action(s_ch.get(k), n_ch.get(k), dl)
            self.rows.append((k, s_ch.get(k), n_ch.get(k, s_ch.get(k)), dl, a))
        parent_changed = sent is None or (s_pcs, s_max) != (n_pcs, n_max)
        down = [x for x in self.rows if x[4] in ('Down', 'Delete')]
        up = [x for x in self.rows if x[4] in ('Up', 'Add')]
        order = ([('parent',)] if parent_changed else []) + down + up if self.first == 'P' else down + ([('parent',)] if parent_changed else []) + up
        self.step_of = {}
        st, prev = 0, None
        for x in order:
            grp = 'parent' if x[0] == 'parent' else ('down' if x[4] in ('Down', 'Delete') else 'up')
            if grp != prev:
                st, prev = st + 1, grp
            self.step_of[x[0] if x[0] == 'parent' else x[0]] = st
        self.order = order
        # play the steps in AP POLE
        ap_pcs, ap_max, ap = s_pcs, s_max, dict(s_ch)
        self.steps = []
        for i, x in enumerate(order, 1):
            if x[0] == 'parent':
                act = 'Add part' if sent is None else 'Edit'
                frm = '-' if sent is None else (f'Max {s_max}' + (f', Pcs {s_pcs}' if s_pcs != n_pcs else ''))
                to = f'Max {n_max}' + (f', Pcs {n_pcs}' if sent is None or s_pcs != n_pcs else '')
                ap_pcs, ap_max = n_pcs, n_max
                lvl, bp, ot = 'Parent', '-', '-'
            else:
                k, sv, nv, dl, act = x
                frm, to = ('-' if sv is None else sv), ('-' if dl else nv)
                if dl:
                    ap.pop(k)
                else:
                    ap[k] = nv
                lvl, bp, ot = 'Child', f'{BP[k[0]]} ({NAME[k[0]]})', k[1]
            tot = sum(ap.values())
            self.steps.append([i, self.step_of[x[0]], lvl, bp, ot, act, frm, to, ap_max, tot, 'OK' if ap_max is not None and tot <= ap_max else 'NG'])
        self.ap_after = (ap_pcs, ap_max, ap)


def build_case(wb, no, c):
    ws, r = sheet(wb, f'{no}. {c.title}'[:31], f'{no}. {c.title}', [c.story])
    s_pcs, s_max, s_ch = c.sent if c.sent else (None, None, {})
    n_pcs, n_max, n_ch = c.new
    # before
    if c.sent:
        ws.cell(r + 1, 1, 'Before: TB_M_PART_CANDIDATE (as sent to AP POLE, APPOLE_SYNC_STATUS 1)')
        r = table(ws, r + 2, KAN_COLS, [[PART, c.period, s_pcs, s_max, 1, SENT_DT, None, s_pcs, s_max, 'D.Anggraini', SENT_DT]], [14] * len(KAN_COLS))
        ws.cell(r, 1, 'Before: TB_M_PART_CANDIDATE_DEST')
        r = table(ws, r + 1, DEST_COLS[:7], [[PART, c.period, k[0], k[1], v, v, None] for k, v in s_ch.items()], [14] * 7)
    # after save
    by = 'XD05BATCH' if not c.sent else 'D.Anggraini'
    krow = [PART, c.period, n_pcs, n_max, 0, SENT_DT if c.sent else None, c.first, s_pcs, s_max, by, SAVE_DT if c.sent else '27-Nov-2026 02:00']
    r += 0 if c.sent else 1
    ws.cell(r, 1, ('After XD05' if not c.sent else 'After the save') + ': TB_M_PART_CANDIDATE (APPOLE_FIRST set by NSP: Max ' + (f'{n_max} vs SENT {s_max}' if c.sent else 'new period, nothing sent')
            + f' -> {c.first})')
    r = table(ws, r + 1, KAN_COLS, [krow], [14] * len(KAN_COLS), {1: HOLD})
    drows, df = [], {}
    for i, (k, sv, nv, dl, a) in enumerate(c.rows, 1):
        drows.append([PART, c.period, k[0], k[1], nv, sv, 'Y' if dl else None, a, c.step_of.get(k, '-')])
        df[i] = BAD if dl else HOLD if a != '-' else OK
    ws.cell(r, 1, 'After the save: TB_M_PART_CANDIDATE_DEST (+ columns computed in the Export Excel for the bot)')
    r = table(ws, r + 1, DEST_COLS, drows, [14] * len(DEST_COLS), df)
    # bot steps
    ws.cell(r, 1, f'XD07 bot in AP POLE Eff. {c.mm}/2026 (APPOLE_FIRST = {c.first}: '
            + ('parent -> children down -> children up' if c.first == 'P' else 'children down -> parent -> children up') + ')')
    r = table(ws, r + 1, STEP_COLS, c.steps, [6, 6, 8, 20, 10, 10, 12, 12, 12, 14, 12],
              {i: (OK if x[10] == 'OK' else BAD) for i, x in enumerate(c.steps, 1)})
    # AP POLE after
    a_pcs, a_max, ap = c.ap_after
    aprows = [[c.mm, '2026', PART, a_pcs, a_max, a_pcs * a_max, BP[k[0]], k[1], v, a_pcs * v] for k, v in ap.items()]
    ws.cell(r, 1, f'AP POLE Eff. {c.mm}/2026 after the run (total children {sum(ap.values())} <= Max {a_max})')
    r = table(ws, r + 1, AP_COLS, aprows, [10] * 6 + [12, 10, 14, 14])
    # after sync
    ws.cell(r, 1, 'After [Sync]: TB_M_PART_CANDIDATE (status 1, SENT = values sent, APPOLE_FIRST cleared)')
    r = table(ws, r + 1, KAN_COLS, [[PART, c.period, n_pcs, n_max, 1, SYNC_DT, None, n_pcs, n_max, 'D.Anggraini', SYNC_DT]], [14] * len(KAN_COLS), {1: OK})
    keep = [x for x in c.rows if not x[3]]
    ws.cell(r, 1, 'After [Sync]: TB_M_PART_CANDIDATE_DEST (SENT = CASE_DAY; rows with DELETE_FLAG Y physically deleted)')
    r = table(ws, r + 1, DEST_COLS[:7], [[PART, c.period, k[0], k[1], nv, nv, None] for k, sv, nv, dl, a in keep], [14] * 7, fills(len(keep), OK))
    for n in c.notes:
        ws.cell(r, 1, n)
        r += 1


def base(mx=20):
    return (6, mx, {(D1, '**'): 5, (D2, '**'): 5, (D3, '**'): 5, (D4, '**'): 5})


def chg(b, mx=None, pcs=None, **ch):
    pcs0, mx0, c = b
    c = dict(c)
    for k, v in ch.items():
        d, ot = k.split('_')
        key = ({'D1': D1, 'D2': D2, 'D3': D3, 'D4': D4, 'D5': D5}[d], '**' if ot == 'S' else ot)
        if v is None:
            c.pop(key, None)
        else:
            c[key] = v
    return (pcs if pcs is not None else pcs0, mx if mx is not None else mx0, c)


CASES = [
    Case('3a Child down and up', 'Max 20 stays. D1 5 -> 4, D2 5 -> 6 (total stays 20).', base(), chg(base(), D1_S=4, D2_S=6)),
    Case('3b Max down', 'Max 20 -> 18; D4 5 -> 3 so that the total is 18. Children first, then the parent.', base(), chg(base(), mx=18, D4_S=3)),
    Case('3c Max up', 'Max 20 -> 22, children unchanged (total 20, 2 remaining). The parent goes up directly.', base(), chg(base(), mx=22)),
    Case('3d New dest, full', 'Max 20 is fully mapped. New D5 = 2: D4 5 -> 3 first, then D5 added.', base(), chg(base(), D4_S=3, D5_S=2)),
    Case('3e New dest, remaining', 'Max 22, total children 20 (2 remaining, sent before). New D5 = 2: added directly.', base(22), chg(base(22), D5_S=2)),
    Case('3f Dest removed', 'D4 removed on the screen: the row stays with DELETE_FLAG Y until it is sent; the bot deletes Buyer PD 96182-01.',
         base(), chg(base(), D4_S=None)),
    Case('3g Order Type split', 'D4 ** 5 -> ** 3 + C 2 (new row with Order Type C). ** goes down first, then C is added.', base(), chg(base(), D4_S=3, D4_C=2)),
    Case('Mixed', 'Max 20 -> 18; D2 ** 5 -> 4 + C 1, D3 5 -> 4, D4 5 -> 3, new D5 = 1 (total 18).', base(),
         chg(base(), mx=18, D2_S=4, D2_C=1, D3_S=4, D4_S=3, D5_S=1)),
    Case('Two saves before Sync', 'Save 1: Max 20 -> 18, D4 5 -> 3. Save 2 (before [Sync]): Max 18 -> 19, D4 3 -> 4. APPOLE_FIRST compares with '
         'APPOLE_SENT_MAX_CASE_DAY 20 (what AP POLE has), not with 18 of save 1: 19 < 20 -> C. Compared with save 1 it would wrongly be P.',
         base(), chg(base(), mx=19, D4_S=4),
         notes=['If the bot took the parent first (P), AP POLE would get Max 19 while the children still total 20 -> rejected (NG). '
                'With C the child D4 goes 5 -> 4 first (total 19), then Max 20 -> 19.']),
    Case('New period XD05', 'XD05 day D makes 202612: nothing sent yet (SENT empty) -> APPOLE_FIRST = P: the part (parent) is added first, then '
         'every Buyer PD.', None, (6, 20, {(D1, '**'): 6, (D2, '**'): 6, (D3, '**'): 4, (D4, '**'): 4}), period='202612', mm='12'),
]


def main():
    wb = Workbook()
    wb.remove(wb.active)
    ws, r = sheet(wb, '0. Rules', 'XD07 AP POLE: order of the parent (Kanban) and the children (Export) from TB_M_PART_CANDIDATE / _DEST', [
        'PROPOSAL (20-Nov, discussion, not yet in the UISS). The bot reads the master tables (via the Export Excel), not TB_H_PART_CANDIDATE '
        '(update table, history only).',
        'Rule of AP POLE: at every step the total Case/Day of the Buyer PD rows <= Max Shipping Box Qty of the part. Example part ' + PART +
        ', Pcs/Case 6, Current period 202611 (Eff. 11/2026).'])
    r = table(ws, r + 1, ['Table', 'New column', 'Type', 'Value / rule'], [
        ['TB_M_PART_CANDIDATE', 'APPOLE_FIRST', 'VARCHAR(1)', 'P = parent first, C = child first. Set by NSP when the part becomes AP POLE Non Sync; '
         'cleared after [Sync]'],
        ['TB_M_PART_CANDIDATE', 'APPOLE_SENT_PCS_CASE', 'NUMBER', 'Pcs/Case last sent to AP POLE (filled by [Sync])'],
        ['TB_M_PART_CANDIDATE', 'APPOLE_SENT_MAX_CASE_DAY', 'NUMBER', 'Max Case/Day last sent to AP POLE (filled by [Sync]); APPOLE_FIRST compares with it'],
        ['TB_M_PART_CANDIDATE_DEST', 'APPOLE_SENT_CASE_DAY', 'NUMBER', 'Case/Day last sent to AP POLE for the destination + order type (filled by [Sync])'],
        ['TB_M_PART_CANDIDATE_DEST', 'DELETE_FLAG', 'VARCHAR(1)', 'Y = removed on the screen / upload; the row stays (hidden, not in the totals) '
         'until it is sent, then it is deleted']], [26, 26, 12, 90], fills(5, HOLD))
    r = table(ws, r, ['Condition (NSP, on save / XD05)', 'APPOLE_FIRST', 'Order of the bot'], [
        ['New period (XD05, nothing sent: SENT empty)', 'P', '1 Add part -> 2 Add every Buyer PD'],
        ['MAX_CASE_DAY > APPOLE_SENT_MAX_CASE_DAY', 'P', '1 Parent -> 2 Children down / delete -> 3 Children up / add'],
        ['MAX_CASE_DAY < APPOLE_SENT_MAX_CASE_DAY', 'C', '1 Children down / delete -> 2 Parent -> 3 Children up / add'],
        ['MAX_CASE_DAY = APPOLE_SENT_MAX_CASE_DAY (children or Pcs/Case only)', 'C', '1 Children down / delete -> 2 Parent (if Pcs/Case changed) -> '
         '3 Children up / add']], [60, 14, 80])
    r = table(ws, r, ['Child row (TB_M_PART_CANDIDATE_DEST)', 'Action in the Export Excel'], [
        ['APPOLE_SENT_CASE_DAY empty', 'Add'], ['DELETE_FLAG = Y', 'Delete'], ['CASE_DAY < APPOLE_SENT_CASE_DAY', 'Down'],
        ['CASE_DAY > APPOLE_SENT_CASE_DAY', 'Up'], ['CASE_DAY = APPOLE_SENT_CASE_DAY', '- (skip)']], [60, 30])
    r = table(ws, r, ['After [Sync] (NSP writes before the bot starts)', 'Value'], [
        ['APPOLE_SYNC_STATUS / APPOLE_SYNC_DT / SYNC_RUN_ID', '1 / send time / run ID'],
        ['APPOLE_SENT_PCS_CASE, APPOLE_SENT_MAX_CASE_DAY, APPOLE_SENT_CASE_DAY', '= values sent'],
        ['Rows with DELETE_FLAG Y', 'Deleted'], ['APPOLE_FIRST', 'Cleared'],
        ['Run failed (e-mail FAILED)', '[Re-send last Sync]: the Export Excel of the run keeps the actions and APPOLE_FIRST of the run, the bot sends it again']],
        [60, 90])
    r = table(ws, r, ['Sheet', 'Scenario', 'APPOLE_FIRST', 'Result'],
              [[i, c.title, c.first, 'OK' if all(s[10] == 'OK' for s in c.steps) else 'NG'] for i, c in enumerate(CASES, 1)], [8, 30, 14, 10],
              fills(len(CASES), OK))
    ws.cell(r, 1, 'GTOPAS (XD06) does not use these columns: GTOPAS only adds / deletes the part + destination, without quantity.')
    for i, c in enumerate(CASES, 1):
        build_case(wb, i, c)
    wb.save(OUT)
    print('saved', OUT)
    for i, c in enumerate(CASES, 1):
        print(i, c.title, c.first, [s[1:3] + s[5:11] for s in c.steps])


if __name__ == '__main__':
    main()
