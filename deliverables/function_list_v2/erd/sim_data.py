"""Simulation scenarios of the Crossdock tables (one sheet per scenario in Crossdock_ERD.xlsx).
Each step shows the rows of a table with their state: ref (read, not changed), new (insert), upd (update; changed columns highlighted),
del (delete), temp (temporary table). Dummy data: supplier 50221 plant 1, pcs/case 6."""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'specs'))
from scan_pack import pack  # noqa: E402

VN, TH, PH, D4 = '9715310', '9722D10', '9811110', '982220'
CUST = {VN: '9715300', TH: '9722D00', PH: '9811100', D4: '982200'}  # dummy customer code per destination (scan key 1)
OD, T = '2026-10-14', '080000'
ASN = 'ASN-50221-261016-001'

# columns shown per table in the simulation sheets
COLS = {
    'TB_M_H0125_DESTINATION': ['DESTINATION_CD', 'CUSTOMER_CD', 'DESTINATION_NAME_ENG', 'COUNTRY_NAME_ENG'],
    'TB_M_PART_MASTER': ['PART_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'DOCK_CD', 'VALID_FROM', 'PART_NAME'],
    'TB_M_PART_CANDIDATE': ['PART_NO', 'PART_NAME', 'MIN_MAD', 'PCS_CASE', 'MAX_CASE_DAY', 'TOTAL_PCS_DAY', 'PART_STATUS', 'SYNC_STATUS', 'LAST_SOURCE'],
    'TB_R_ACTUAL_DEMAND_SUMMARY': ['GROUPING_BUYER_CD', 'GROUPING_PD_CD', 'ORDER_TYPE_GROUP', 'DEMAND_MONTH_YEAR', 'PART_NO', 'MAD'],
    'TB_R_PART_DAD_RESULT': ['PERIOD', 'PART_NO', 'MONTH_FROM', 'MONTH_TO', 'NUM_OF_MONTH', 'TOTAL_MAD', 'AVG_MAD', 'MIN_MAD', 'OLD_STATUS', 'NEW_STATUS'],
    'TB_M_PART_CANDIDATE_DEST': ['PART_NO', 'PERIOD', 'DEST_CODE', 'CASE_DAY'],
    'TB_H_PART_CANDIDATE': ['HIST_ID', 'PART_NO', 'PERIOD', 'EVENT_TYPE', 'SOURCE', 'DEST_CODE', 'FIELD_NAME', 'OLD_VALUE', 'NEW_VALUE', 'CREATED_BY'],
    'TB_R_CROSSDOCK_IF_RESULT': ['PART_NO', 'TARGET_SYSTEM', 'PERIOD', 'IF_STATUS', 'IF_FILE_NAME', 'IF_MESSAGE'],
    'TB_R_H0253_ORDER_CONTROL_PRE': ['CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD', 'DETAILED_ITEM_NO', 'SERIAL_NO', 'SHIPPING_PART_NO', 'ORDER_STATUS_QTY',
                                     'ORDER_STATUS', 'HOLD_FLAG', 'PO_MAPPED_FLAG', 'UPD_STATUS'],
    'TB_R_PRA_DAILY_ORDER_MANIFEST': ['MANIFEST_NO', 'PO_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_DT', 'CROSS_DOCK_FLAG', 'TOTAL_QTY', 'DELIVERY_DT', 'SUB_ROUTE_CD'],
    'TB_R_PRA_DAILY_ORDER_PART': ['MANIFEST_NO', 'MANIFEST_ITEM', 'PO_NO', 'PO_ITEM', 'PART_NO', 'ORDER_QTY'],
    '#TEMP_INSTRUCTION': ['SORT_SEQ', 'CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'PART_NO', 'OPEN_ORDER_QTY', 'PO_NO', 'ASSIGNED_QTY',
                          'CASE_SEQ', 'CUM_DEST_QTY', 'SEQ_QTY', 'CUT_FLAG', 'GROUP_SEQ', 'CROSSDOCK_STATUS'],
    'TB_R_INSTRUCTION': ['INSTRUCTION_ID', 'CASE_SEQ', 'LINE_SEQ', 'PART_NO', 'DESTINATION_CD', 'CUSTOMER_ORDER_NO', 'SERIAL_NO', 'QTY', 'PO_NO', 'MANIFEST_NO',
                         'MANIFEST_ITEM', 'ASN_NO', 'CASE_NO'],
    'TB_R_PRA_DAILY_ORDER_MAPPED': ['PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'PART_NO', 'ORDER_QTY', 'MAPPED_QTY'],
    'TB_R_DAILY_ORDER_MANIFEST': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'ASN_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_NO', 'CROSS_DOCK_FLAG', 'TOTAL_ITEM', 'TOTAL_QTY',
                                  'DELIVERY_DT_ORI', 'SUB_ROUTE_CD', 'STATUS'],
    'TB_R_DAILY_ORDER_PART': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CASE_NO', 'PO_NO', 'PO_ITEM', 'ASN_NO', 'PART_NO', 'PART_NAME', 'PO_QTY', 'DELIVERY_QTY'],
    'TB_R_CASE_LABEL_LAST_SEQ': ['SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ'],
    'TB_H_CROSSDOCK_ORDER_CHANGE': ['HIST_ID', 'ASN_NO', 'CASE_NO', 'PART_NO', 'FROM_CUSTOMER_ORDER_NO', 'FROM_SERIAL_NO', 'TO_CUSTOMER_ORDER_NO',
                                    'TO_DESTINATION_CD', 'QTY', 'FROM_INSTRUCTION_ID', 'TO_INSTRUCTION_ID'],
}

# value highlight (column, value) -> fill
VALUE_FILL = {
    ('PART_STATUS', 'Active'): 'C6EFCE', ('PART_STATUS', 'Inactive'): 'D9D9D9', ('PART_STATUS', 'Candidate'): 'DDEBF7',
    ('NEW_STATUS', 'Active'): 'C6EFCE', ('NEW_STATUS', 'Inactive'): 'D9D9D9',
    ('SYNC_STATUS', '0'): 'FCE4D6', ('SYNC_STATUS', '1'): 'C6EFCE', ('SYNC_STATUS', '2'): 'FF7C80',
    ('CUT_FLAG', 'Y'): 'BDD7EE', ('CROSSDOCK_STATUS', '6'): 'C6EFCE', ('CROSSDOCK_STATUS', '7'): 'FF7C80',
    ('ORDER_STATUS', '2'): 'FF7C80', ('ORDER_STATUS', '6'): 'DDEBF7', ('HOLD_FLAG', 'Y'): 'FF7C80',
    ('UPD_STATUS', '2'): 'FF7C80', ('UPD_STATUS', '6'): 'C6EFCE',
    ('RESULT', 'CONFLICT'): 'FF7C80', ('RESULT', 'CANCELLED'): 'F4B084', ('CROSS_DOCK_FLAG', 'X'): 'FFE699',
}

PRA_MAN = {'1': ['MF-DMY-09001', 'PO-DMY-09001', '50221', '1', '2026-10-15', 'X', 12, '2026-10-16', 'SD01'],
           '2': ['MF-DMY-09002', 'PO-DMY-09002', '50221', '1', '2026-10-15', 'X', 12, '2026-10-16', 'SD01'],
           '3': ['MF-DMY-09003', 'PO-DMY-09003', '50221', '1', '2026-10-15', 'X', 6, '2026-10-16', 'SD01']}
PRA_PART = {'1': ['MF-DMY-09001', '0001', 'PO-DMY-09001', '0001', 'PART-X', 12], '2': ['MF-DMY-09002', '0001', 'PO-DMY-09002', '0001', 'PART-X', 12],
            '3': ['MF-DMY-09003', '0001', 'PO-DMY-09003', '0001', 'PART-Y', 6]}


def h(co, d, serial, part, qty, st='7', hold='N', mapped='N', upd=None, od=OD, item='001', cust=None):
    return [cust or CUST[d], co, od, d, item, serial, part, qty, st, hold, mapped, upd]


def line(co, d, part, qty, cust=None, serial='0000001', item='001', od=OD, time=T):
    return dict(CUSTOMER_CD=cust or CUST[d], CUSTOMER_ORDER_NO=co, ORDER_DT=od, ORDER_TIME=time, DESTINATION_CD=d, DETAILED_ITEM_NO=item,
                SERIAL_NO=serial, PART_NO=part, QTY=qty)


def tmp(units, pos, pcs=6, changed=None, notes=None):
    """XD09 pre-mapping rows (scan_pack): units = list of line lists (one per Part + Customer Order Date), pos = [po, manifest, item, qty].
    changed / notes: {(customer order no, case seq): [columns] / note}."""
    pos = [list(p) for p in pos]
    rows = []
    for u in units:
        for s in pack(u, pos, pcs):
            k = (s['CUSTOMER_ORDER_NO'], s['CASE_SEQ'])
            row = [s['SORT_SEQ'], s['CUSTOMER_CD'], s['CUSTOMER_ORDER_NO'], s['DESTINATION_CD'], s['PART_NO'], s['QTY'], s['PO_NO'], s['ASSIGNED_QTY'],
                   s['CASE_SEQ'], s['CUM_DEST_QTY'], s['SEQ_QTY'], s['CUT_FLAG'], s['GROUP_SEQ'], s['CROSSDOCK_STATUS']]
            rows.append(('temp', row, (changed or {}).get(k, []), (notes or {}).pop(k, '')))  # note on the first slice only
    return rows


PX = [line('CO-14101', VN, 'PART-X', 10), line('CO-14102', VN, 'PART-X', 4), line('CO-14103', VN, 'PART-X', 4), line('CO-14104', TH, 'PART-X', 6)]
PY = [line('CO-14105', PH, 'PART-Y', 6)]
VN2 = '9730000'  # second dummy customer of Vietnam (customer code > TH)
SB = [line('A-0101', VN, 'PART-B', 8, item='001', time='080000'), line('A-0101', VN, 'PART-B', 2, item='002', time='080000'),
      line('B-0102', TH, 'PART-B', 6, time='090000'), line('C-0103', VN, 'PART-B', 14, cust=VN2, time='070000')]
SB2 = [line('A-0201', VN, 'PART-B', 6, od='2026-10-15')]
SA = [line('V01', VN, 'PART-A', 10, 'CUST-A'), line('T01', TH, 'PART-A', 6, 'CUST-B'), line('V02', VN, 'PART-A', 14, 'CUST-C')]
P1, P2, P3 = ['PO-DMY-09001', 'MF-DMY-09001', '0001', 12], ['PO-DMY-09002', 'MF-DMY-09002', '0001', 12], ['PO-DMY-09003', 'MF-DMY-09003', '0001', 6]


SCENARIOS = [
    {
        'id': 'SIM-1', 'title': 'Master setup and monthly calculation', 'flow': 'BPF F1', 'functions': 'XD13, XD01 / XD02, XD04, XD05, XD01 [Sync], XD06 / XD07',
        'story': ['Destination master is synchronised weekly; Procurement registers PART-Y; the monthly run (Oct 2026) uses the actual demand of Jul – Sep.',
                  'XD05: PART-X stays Active (avg MAD 315 ≥ 300), PART-Y becomes Active (130 ≥ 100), PART-Z becomes Inactive (35 < 50) and is set to No Sync.',
                  'Mapping: PART-X Max Case/Day 10 split by MAD share VN 60 % / TH 30 % / PH 10 % = 6 / 3 / 1. D/S clicks [Sync]: PART-Z is sent with CROSSDOCK_FLAG N.'],
        'steps': [
            ('1. XD13 weekly destination sync (delete – insert)', 'TB_M_H0125_DESTINATION', [
                ('new', [VN, '97153', 'DUMMY DESTINATION VIETNAM', 'VIETNAM']), ('new', [TH, '9722D', 'DUMMY DESTINATION THAILAND', 'THAILAND']),
                ('new', [PH, '98111', 'DUMMY DESTINATION PHILIPPINES', 'PHILIPPINES'])]),
            ('2. Procurement adds PART-Y (XD01); part name from the part master', 'TB_M_PART_MASTER', [
                ('ref', ['PART-X', '50221', '1', 'S1', '2026-01-01', 'DUMMY PART X']), ('ref', ['PART-Y', '50221', '1', 'S1', '2026-01-01', 'DUMMY PART Y']),
                ('ref', ['PART-Z', '50221', '1', 'S1', '2026-01-01', 'DUMMY PART Z'])]),
            ('', 'TB_M_PART_CANDIDATE', [
                ('ref', ['PART-X', 'DUMMY PART X', 300, 6, 10, 60, 'Active', '1', 'CALC']),
                ('new', ['PART-Y', 'DUMMY PART Y', 100, 6, 2, 12, 'Candidate', '0', 'SCREEN']),
                ('ref', ['PART-Z', 'DUMMY PART Z', 50, 6, 4, 24, 'Active', '1', 'CALC'])]),
            ('3. XD04 monthly actual demand (delete – insert)', 'TB_R_ACTUAL_DEMAND_SUMMARY', [
                ('new', [b, p, 'N', m, part, q]) for part, b, p, qs in (('PART-X', '97153', '10', (180, 190, 200)), ('PART-X', '9722D', '10', (90, 95, 100)),
                                                                        ('PART-X', '98111', '10', (30, 30, 30)), ('PART-Y', '98111', '10', (120, 130, 140)),
                                                                        ('PART-Z', '97153', '10', (40, 35, 30)))
                for m, q in zip(('202607', '202608', '202609'), qs)]),
            ('4. XD05 process 1: status by average MAD', 'TB_R_PART_DAD_RESULT', [
                ('new', ['202610', 'PART-X', '202607', '202609', 3, 945, 315, 300, 'Active', 'Active']),
                ('new', ['202610', 'PART-Y', '202607', '202609', 3, 390, 130, 100, 'Candidate', 'Active']),
                ('new', ['202610', 'PART-Z', '202607', '202609', 3, 105, 35, 50, 'Active', 'Inactive'])]),
            ('', 'TB_M_PART_CANDIDATE', [
                ('ref', ['PART-X', 'DUMMY PART X', 300, 6, 10, 60, 'Active', '1', 'CALC']),
                ('upd', ['PART-Y', 'DUMMY PART Y', 100, 6, 2, 12, 'Active', '0', 'CALC'], ['PART_STATUS', 'LAST_SOURCE'], 'Candidate → Active'),
                ('upd', ['PART-Z', 'DUMMY PART Z', 50, 6, 4, 24, 'Inactive', '0', 'CALC'], ['PART_STATUS', 'SYNC_STATUS'], 'Active → Inactive, set No Sync')]),
            ('5. XD05 process 2: mapping per destination, history', 'TB_M_PART_CANDIDATE_DEST', [
                ('new', ['PART-X', '202610', VN, 6]), ('new', ['PART-X', '202610', TH, 3]), ('new', ['PART-X', '202610', PH, 1]), ('new', ['PART-Y', '202610', PH, 2])]),
            ('', 'TB_H_PART_CANDIDATE', [
                ('new', [1002, 'PART-Y', '202610', 'CALC', 'BATCH', None, 'PART_STATUS', 'Candidate', 'Active', 'XD05']),
                ('new', [1003, 'PART-Z', '202610', 'CALC', 'BATCH', None, 'PART_STATUS', 'Active', 'Inactive', 'XD05']),
                ('new', [1004, 'PART-X', '202610', 'MAPPING', 'BATCH', VN, 'CASE_DAY', '5', '6', 'XD05'])]),
            ('6. D/S [Sync] → XD06 (G-System) / XD07 (AP POLE)', 'TB_R_CROSSDOCK_IF_RESULT', [
                ('new', ['PART-Y', 'G-System', '202610', '1', 'SEND-20261002-01', 'OK']), ('new', ['PART-Y', 'APPOLE', '202610', '1', 'XDOCK_MASTER_20261002.csv', 'OK']),
                ('new', ['PART-Z', 'G-System', '202610', '1', 'SEND-20261002-01', 'OK (CROSSDOCK_FLAG N)']),
                ('new', ['PART-Z', 'APPOLE', '202610', '1', 'XDOCK_MASTER_20261002.csv', 'OK (CROSSDOCK_FLAG N)'])]),
            ('', 'TB_M_PART_CANDIDATE', [
                ('upd', ['PART-Y', 'DUMMY PART Y', 100, 6, 2, 12, 'Active', '1', 'CALC'], ['SYNC_STATUS'], 'No Sync → Success'),
                ('upd', ['PART-Z', 'DUMMY PART Z', 50, 6, 4, 24, 'Inactive', '1', 'CALC'], ['SYNC_STATUS'], 'No Sync → Success (inactive in G-System / AP POLE)')]),
        ]},
    {
        'id': 'SIM-2', 'title': 'Daily order to ASN (normal)', 'flow': 'BPF F2', 'functions': 'XD08, XD09, XD10 (Create ASN, Submit 5.7)',
        'story': ['G-System releases crossdock orders 14-Oct (status 7); the supplier POs of 15-Oct are crossdock manifests (CROSS_DOCK_FLAG X).',
                  'Supplier searches delivery 16-Oct Rit 1: PART-X (VN 18 + TH 6 = 4 cases in scan order, 4 blocks) and PART-Y (PH 6 = 1 case) are Ready; all blocks are chosen, Create ASN and Submit.',
                  'Result: one ASN with 5 cases / 30 pcs, 3 ASN manifests (one per Pra manifest), 5 ASN part rows (manifest item x case).'],
        'steps': [
            ('1. XD08 27:30: status 7 rows (insert)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('new', h('CO-14101', VN, '0000001', 'PART-X', 10)), ('new', h('CO-14102', VN, '0000001', 'PART-X', 4)),
                ('new', h('CO-14103', VN, '0000001', 'PART-X', 4)), ('new', h('CO-14104', TH, '0000001', 'PART-X', 6)),
                ('new', h('CO-14105', PH, '0000001', 'PART-Y', 6))]),
            ('2. Existing daily order: crossdock manifests and their parts', 'TB_R_PRA_DAILY_ORDER_MANIFEST', [('ref', PRA_MAN[k]) for k in '123']),
            ('', 'TB_R_PRA_DAILY_ORDER_PART', [('ref', PRA_PART[k]) for k in '123']),
            ('3. [Search] → XD09 pre-mapping in scan order: cases and blocks (session)', '#TEMP_INSTRUCTION',
             tmp([PX], [P1, P2]) + tmp([PY], [P3])),
            ('4. [Create ASN]: real mapping, flags, mapped qty', 'TB_R_INSTRUCTION', [
                ('new', [i + 1, c, l, p, d, co, '0000001', q, po, m, '0001', None, None]) for i, (c, l, p, d, co, q, po, m) in enumerate((
                    (1, 1, 'PART-X', VN, 'CO-14101', 6, 'PO-DMY-09001', 'MF-DMY-09001'), (2, 1, 'PART-X', VN, 'CO-14101', 4, 'PO-DMY-09001', 'MF-DMY-09001'),
                    (2, 2, 'PART-X', VN, 'CO-14102', 2, 'PO-DMY-09001', 'MF-DMY-09001'), (3, 1, 'PART-X', VN, 'CO-14102', 2, 'PO-DMY-09002', 'MF-DMY-09002'),
                    (3, 2, 'PART-X', VN, 'CO-14103', 4, 'PO-DMY-09002', 'MF-DMY-09002'), (4, 1, 'PART-X', TH, 'CO-14104', 6, 'PO-DMY-09002', 'MF-DMY-09002'),
                    (5, 1, 'PART-Y', PH, 'CO-14105', 6, 'PO-DMY-09003', 'MF-DMY-09003')))]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [
                ('new', ['PO-DMY-09001', 'MF-DMY-09001', '0001', 'PART-X', 12, 12]), ('new', ['PO-DMY-09002', 'MF-DMY-09002', '0001', 'PART-X', 12, 12]),
                ('new', ['PO-DMY-09003', 'MF-DMY-09003', '0001', 'PART-Y', 6, 6])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h(co, d, '0000001', p, q, mapped='Y'), ['PO_MAPPED_FLAG']) for co, d, p, q in (
                    ('CO-14101', VN, 'PART-X', 10), ('CO-14102', VN, 'PART-X', 4), ('CO-14103', VN, 'PART-X', 4), ('CO-14104', TH, 'PART-X', 6),
                    ('CO-14105', PH, 'PART-Y', 6))]),
            ('5. [Submit ASN] (5.7): ASN tables, last sequence, write back', 'TB_R_DAILY_ORDER_MANIFEST', [
                ('new', [f'{m}A1', m, ASN, '50221', '1', po, 'X', 1, q, '2026-10-16', 'SD01', 'Created'])
                for m, po, q in (('MF-DMY-09001', 'PO-DMY-09001', 12), ('MF-DMY-09002', 'PO-DMY-09002', 12), ('MF-DMY-09003', 'PO-DMY-09003', 6))]),
            ('', 'TB_R_DAILY_ORDER_PART', [
                ('new', [f'{m}A1', m, '0001', c, po, '0001', ASN, p, f'DUMMY {p.replace("-", " ")}', pq, 6]) for m, c, po, p, pq in (
                    ('MF-DMY-09001', 'C-0001', 'PO-DMY-09001', 'PART-X', 12), ('MF-DMY-09001', 'C-0002', 'PO-DMY-09001', 'PART-X', 12),
                    ('MF-DMY-09002', 'C-0003', 'PO-DMY-09002', 'PART-X', 12), ('MF-DMY-09002', 'C-0004', 'PO-DMY-09002', 'PART-X', 12),
                    ('MF-DMY-09003', 'C-0005', 'PO-DMY-09003', 'PART-Y', 6))]),
            ('', 'TB_R_CASE_LABEL_LAST_SEQ', [('upd', ['50221', '1', '005', '001'], ['CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ'], '000 / 000 → 005 / 001')]),
            ('', 'TB_R_INSTRUCTION', [
                ('upd', [i + 1, c, l, p, d, co, '0000001', q, po, m, '0001', ASN, f'C-{c:04d}'], ['ASN_NO', 'CASE_NO']) for i, (c, l, p, d, co, q, po, m) in enumerate((
                    (1, 1, 'PART-X', VN, 'CO-14101', 6, 'PO-DMY-09001', 'MF-DMY-09001'), (2, 1, 'PART-X', VN, 'CO-14101', 4, 'PO-DMY-09001', 'MF-DMY-09001'),
                    (2, 2, 'PART-X', VN, 'CO-14102', 2, 'PO-DMY-09001', 'MF-DMY-09001'), (3, 1, 'PART-X', VN, 'CO-14102', 2, 'PO-DMY-09002', 'MF-DMY-09002'),
                    (3, 2, 'PART-X', VN, 'CO-14103', 4, 'PO-DMY-09002', 'MF-DMY-09002'), (4, 1, 'PART-X', TH, 'CO-14104', 6, 'PO-DMY-09002', 'MF-DMY-09002'),
                    (5, 1, 'PART-Y', PH, 'CO-14105', 6, 'PO-DMY-09003', 'MF-DMY-09003')))]),
        ]},
    {
        'id': 'SIM-3', 'title': 'Unit Partially Ready (PO short), Ready the next day', 'flow': 'BPF F2 / AB08', 'functions': 'XD09, XD10',
        'story': ['PART-X 14-Oct needs 24 pcs (VN 18, TH 6) but only 18 pcs of crossdock PO are released on 15-Oct (PO-DMY-09001 12 + PO-DMY-09002 6).',
                  'Scan order VN (CO-14101..14103) then TH (CO-14104): cases 1-3 (VN) have a PO, case 4 (TH) has none. Every case ends a valid cut, so '
                  'blocks 1-3 are Ready and block 4 Not Ready: the unit is Partially Ready (ASN options 1 / 2 / 3 cases).',
                  'In this simulation the supplier waits: on 16-Oct a new crossdock manifest (PO-DMY-10001, 6 pcs) is released → [Search] again → block 4 Ready.'],
        'steps': [
            ('1. Crossdock PO of 15-Oct (only 18 pcs)', 'TB_R_PRA_DAILY_ORDER_PART', [
                ('ref', PRA_PART['1']), ('ref', ['MF-DMY-09002', '0001', 'PO-DMY-09002', '0001', 'PART-X', 6])]),
            ('2. [Search] 15-Oct → XD09: block 4 (TH) without PO', '#TEMP_INSTRUCTION',
             tmp([PX], [P1, ['PO-DMY-09002', 'MF-DMY-09002', '0001', 6]], notes={('CO-14104', 4): 'No PO left: block 4 Not Ready, blocks 1-3 Ready'})),
            ('3. New crossdock manifest released 16-Oct', 'TB_R_PRA_DAILY_ORDER_MANIFEST', [
                ('new', ['MF-DMY-10001', 'PO-DMY-10001', '50221', '1', '2026-10-16', 'X', 6, '2026-10-17', 'SD01'])]),
            ('', 'TB_R_PRA_DAILY_ORDER_PART', [('new', ['MF-DMY-10001', '0001', 'PO-DMY-10001', '0001', 'PART-X', 6])]),
            ('4. [Search] 16-Oct → XD09: all blocks Ready', '#TEMP_INSTRUCTION',
             tmp([PX], [P1, ['PO-DMY-09002', 'MF-DMY-09002', '0001', 6], ['PO-DMY-10001', 'MF-DMY-10001', '0001', 6]],
                 changed={('CO-14104', 4): ['PO_NO', 'CROSSDOCK_STATUS']}, notes={('CO-14104', 4): 'PO PO-DMY-10001: unit Ready'})),
        ]},
    {
        'id': 'SIM-4', 'title': 'Hold a destination (D/S team)', 'flow': 'BPF F4 / AB09', 'functions': 'XD10 (D/S view), XD09, XD10 Create ASN',
        'story': ['The D/S team holds Thailand of PART-X 14-Oct: HOLD_FLAG Y on CO-14104.',
                  'XD09 does not take held lines: the scan order and the blocks are computed with Vietnam only (18 pcs = 3 cases, 3 blocks) and the unit is Ready.',
                  'If the supplier had ticked the unit before the hold, [Create ASN] fails for the whole selection (MSG8): nothing is inserted.'],
        'steps': [
            ('1. D/S Hold Thailand (XD10)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('ref', h('CO-14101', VN, '0000001', 'PART-X', 10)), ('ref', h('CO-14102', VN, '0000001', 'PART-X', 4)),
                ('ref', h('CO-14103', VN, '0000001', 'PART-X', 4)),
                ('upd', h('CO-14104', TH, '0000001', 'PART-X', 6, hold='Y'), ['HOLD_FLAG'], 'Hold by D/S')]),
            ('2. [Search] → XD09 without the held line (VN only: 3 cases, 3 blocks)', '#TEMP_INSTRUCTION', tmp([PX[:3]], [P1, P2])),
            ('3. Hold placed after the supplier ticked the unit → [Create ASN] fails (MSG8)', 'TB_R_INSTRUCTION', [
                ('ref', [None, None, None, None, None, None, None, None, None, None, None, None, None], [], 'No row inserted (roll back); delivery plan refreshed')]),
            ('4. D/S Release Thailand', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14104', TH, '0000001', 'PART-X', 6, hold='N'), ['HOLD_FLAG'], 'Released: taken again by the next [Search]')]),
        ]},
    {
        'id': 'SIM-5', 'title': 'One PO per order date (short PO → split PO); cancel of a middle row after ASN → Change Order Number (simulasi_asn.xlsx)',
        'flow': 'BPF F2 / F4', 'functions': 'XD08, XD09, XD10, XD11 (Change Order Number)',
        'story': ['PART-X, 6 pcs/case. One PO per customer order date: PO_DT = order date + 1, qty = total order qty of the date (all destinations). '
                  'PO qty < order qty is an abnormality: the rest comes in a split PO. ORDER_STATUS of the replicate keeps 7; changes go to UPD_STATUS.',
                  'Order date 15-Oct (12) → PO-DMY-09011; CO-14102 on hold then cancelled, so its 6 pcs of PO-DMY-09011 go to CO-14103 (older PO_DT first).',
                  'Order date 17-Oct: 4 destinations, 30 pcs, PO-DMY-09013 only 18 (abnormal) → case 5 Not Ready until the split PO-DMY-09014 (12, 19-Oct). '
                  'Cases 1-4 → ASN0003; CO-14104 (middle row, case 3) is cancelled after the ASN. Order date 18-Oct: 3 destinations, 18 pcs, PO-DMY-09015 18 (OK) → ASN0005.',
                  '21-Oct G-System allocates the pcs of case 3 to CO-14111 (UPD_STATUS 6, no ASN): the D/S team moves case 3 to CO-14111 (XD11). '
                  'Open PO qty at the end (12) = cancelled qty (CO-14102 + CO-14104).'],
        'steps': [
            ('1. 16-Oct XD08 (order date 15-Oct; PO-DMY-09011 PO_DT 16-Oct, 12)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('new', h('CO-14101', VN, '0000001', 'PART-X', 6, od='2026-10-15')),
                ('new', h('CO-14102', TH, '0000001', 'PART-X', 6, od='2026-10-15', cust=TH))]),
            ('2. 16-Oct D/S holds CO-14102; CO-14101 → ASN0001', 'TB_R_INSTRUCTION', [
                ('new', [1, 1, 1, 'PART-X', VN, 'CO-14101', '0000001', 6, 'PO-DMY-09011', 'MF-DMY-09011', '0001', 'ASN0001', 'C-0001-01'])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14101', VN, '0000001', 'PART-X', 6, mapped='Y', od='2026-10-15'), ['PO_MAPPED_FLAG']),
                ('upd', h('CO-14102', TH, '0000001', 'PART-X', 6, hold='Y', od='2026-10-15', cust=TH), ['HOLD_FLAG'], '6 pcs of PO-DMY-09011 stay open')]),
            ('3. 17-Oct XD08: CO-14101 → 6, CO-14102 → 2, CO-14103 new (PO-DMY-09012 PO_DT 17-Oct, 6)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14101', VN, '0000001', 'PART-X', 6, mapped='Y', upd='6', od='2026-10-15'), ['UPD_STATUS'], 'Received'),
                ('upd', h('CO-14102', TH, '0000001', 'PART-X', 6, hold='Y', upd='2', od='2026-10-15', cust=TH), ['UPD_STATUS'], 'Cancelled, no ASN (PO_MAPPED_FLAG stays N)'),
                ('new', h('CO-14103', TH, '0000001', 'PART-X', 6, od='2026-10-16', cust=TH))]),
            ('4. 17-Oct CO-14103 → ASN0002 with the rest of PO-DMY-09011 (older PO_DT)', 'TB_R_INSTRUCTION', [
                ('new', [2, 1, 1, 'PART-X', TH, 'CO-14103', '0000001', 6, 'PO-DMY-09011', 'MF-DMY-09011', '0001', 'ASN0002', 'C-0002-01'], [], 'PO-DMY-09012 stays open')]),
            ('5. 18-Oct XD08: order date 17-Oct, 4 destinations, 30 pcs; PO-DMY-09013 only 18 (abnormal)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14103', TH, '0000001', 'PART-X', 6, mapped='Y', upd='6', od='2026-10-16', cust=TH), ['UPD_STATUS'], 'Received'),
                ('new', h('CO-14105', VN, '0000001', 'PART-X', 6, od='2026-10-17')),
                ('new', h('CO-14106', VN, '0000001', 'PART-X', 3, od='2026-10-17')),
                ('new', h('CO-14107', VN, '0000001', 'PART-X', 3, od='2026-10-17')),
                ('new', h('CO-14104', TH, '0000001', 'PART-X', 6, od='2026-10-17', cust=TH), [], 'Middle row'),
                ('new', h('CO-14109', PH, '0000001', 'PART-X', 6, od='2026-10-17')),
                ('new', h('CO-14110', D4, '0000001', 'PART-X', 6, od='2026-10-17'))]),
            ('6. 18-Oct [Search] → XD09: 24 of 30 pcs with PO, case 5 Not Ready', '#TEMP_INSTRUCTION', tmp(
                [[line('CO-14104', TH, 'PART-X', 6, cust=TH, od='2026-10-17'), line('CO-14105', VN, 'PART-X', 6, od='2026-10-17'),
                  line('CO-14106', VN, 'PART-X', 3, od='2026-10-17'), line('CO-14107', VN, 'PART-X', 3, od='2026-10-17'),
                  line('CO-14109', PH, 'PART-X', 6, od='2026-10-17'), line('CO-14110', D4, 'PART-X', 6, od='2026-10-17')]],
                [['PO-DMY-09012', 'MF-DMY-09012', '0001', 6], ['PO-DMY-09013', 'MF-DMY-09013', '0001', 18]],
                notes={('CO-14105', 1): 'Cases 1-4 ticked → ASN0003', ('CO-14104', 3): 'Middle row', ('CO-14110', 5): 'Not Ready (PO short)'})),
            ('7. 18-Oct ASN0003 = cases 1-4', 'TB_R_INSTRUCTION', [
                ('new', [3, 1, 1, 'PART-X', VN, 'CO-14105', '0000001', 6, 'PO-DMY-09012', 'MF-DMY-09012', '0001', 'ASN0003', 'C-0003-01']),
                ('new', [4, 2, 1, 'PART-X', VN, 'CO-14106', '0000001', 3, 'PO-DMY-09013', 'MF-DMY-09013', '0001', 'ASN0003', 'C-0003-02']),
                ('new', [5, 2, 2, 'PART-X', VN, 'CO-14107', '0000001', 3, 'PO-DMY-09013', 'MF-DMY-09013', '0001', 'ASN0003', 'C-0003-02']),
                ('new', [6, 3, 1, 'PART-X', TH, 'CO-14104', '0000001', 6, 'PO-DMY-09013', 'MF-DMY-09013', '0001', 'ASN0003', 'C-0003-03']),
                ('new', [7, 4, 1, 'PART-X', PH, 'CO-14109', '0000001', 6, 'PO-DMY-09013', 'MF-DMY-09013', '0001', 'ASN0003', 'C-0003-04'])]),
            ('8. 19-Oct XD08: ASN0003 received, CO-14104 → 2 (middle row, in case 3); split PO-DMY-09014 (PO_DT 19-Oct, 12); order date 18-Oct new', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14104', TH, '0000001', 'PART-X', 6, mapped='Y', upd='2', od='2026-10-17', cust=TH), ['UPD_STATUS'],
                 'Cancel after ASN: LOG5, listed in XD11 (waiting for a candidate)')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('new', h('CO-14112', VN, '0000001', 'PART-X', 6, od='2026-10-18'), [], 'Order date 18-Oct, 3 destinations (PO-DMY-09015, PO_DT 19-Oct, 18)'),
                ('new', h('CO-14113', PH, '0000001', 'PART-X', 6, od='2026-10-18')),
                ('new', h('CO-14114', D4, '0000001', 'PART-X', 6, od='2026-10-18'))]),
            ('9. 19-Oct [Search] → XD09: rest of 17-Oct with the split PO, then 18-Oct', '#TEMP_INSTRUCTION', tmp(
                [[line('CO-14110', D4, 'PART-X', 6, od='2026-10-17')],
                 [line('CO-14112', VN, 'PART-X', 6, od='2026-10-18'), line('CO-14113', PH, 'PART-X', 6, od='2026-10-18'),
                  line('CO-14114', D4, 'PART-X', 6, od='2026-10-18')]],
                [['PO-DMY-09014', 'MF-DMY-09014', '0001', 12], ['PO-DMY-09015', 'MF-DMY-09015', '0001', 18]],
                notes={('CO-14110', 1): '→ ASN0004', ('CO-14112', 1): 'Rest of the split PO; cases 1-3 → ASN0005'})),
            ('10. 19-Oct ASN0004 (CO-14110) and ASN0005 (order date 18-Oct, cases 1-3)', 'TB_R_INSTRUCTION', [
                ('new', [8, 1, 1, 'PART-X', D4, 'CO-14110', '0000001', 6, 'PO-DMY-09014', 'MF-DMY-09014', '0001', 'ASN0004', 'C-0004-01'], [], 'Split PO'),
                ('new', [9, 1, 1, 'PART-X', VN, 'CO-14112', '0000001', 6, 'PO-DMY-09014', 'MF-DMY-09014', '0001', 'ASN0005', 'C-0005-01']),
                ('new', [10, 2, 1, 'PART-X', PH, 'CO-14113', '0000001', 6, 'PO-DMY-09015', 'MF-DMY-09015', '0001', 'ASN0005', 'C-0005-02']),
                ('new', [11, 3, 1, 'PART-X', D4, 'CO-14114', '0000001', 6, 'PO-DMY-09015', 'MF-DMY-09015', '0001', 'ASN0005', 'C-0005-03'], [], '6 pcs of PO-DMY-09015 stay open')]),
            ('11. 20-Oct XD08: CO-14111 new (order date 19-Oct, PO-DMY-09016); 21-Oct → 6 (pcs of case 3 allocated by G-System)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14111', TH, '0000001', 'PART-X', 6, upd='6', od='2026-10-19', cust=TH), ['UPD_STATUS'], 'Received without ASN: candidate')]),
            ('12. 21-Oct XD11 Change Order Number: ASN0003 case 3 → CO-14111', 'TB_R_INSTRUCTION', [
                ('upd', [6, 3, 1, 'PART-X', TH, 'CO-14111', '0000001', 6, 'PO-DMY-09013', 'MF-DMY-09013', '0001', 'ASN0003', 'C-0003-03'],
                 ['CUSTOMER_ORDER_NO'], 'Whole row moved; case, PO and ASN not changed')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('ref', h('CO-14104', TH, '0000001', 'PART-X', 6, mapped='Y', upd='2', od='2026-10-17', cust=TH), [], 'Not changed (PO_MAPPED_FLAG stays Y)'),
                ('upd', h('CO-14111', TH, '0000001', 'PART-X', 6, mapped='Y', upd='6', od='2026-10-19', cust=TH), ['PO_MAPPED_FLAG'], 'PO and ASN through ASN0003')]),
            ('', 'TB_H_CROSSDOCK_ORDER_CHANGE', [('new', [1, 'ASN0003', 'C-0003-03', 'PART-X', 'CO-14104', '0000001', 'CO-14111', TH, 6, 6, 6])]),
        ]},
    {
        'id': 'SIM-6', 'title': 'Draft released by XD08; partial cancel after ASN replaced by two lines', 'flow': 'BPF F2 / F4',
        'functions': 'XD10 (Create ASN), XD08, XD11 (Change Order Number)',
        'story': ['A: CO-14110 (PART-Y, PH, 12 pcs) is in a draft (Create ASN done, not submitted). The next run of XD08 releases every draft, whatever changed: '
                  'the rows are deleted, the mapped qty is given back and the cases come back in the delivery plan.',
                  'B: CO-B (PART-Y, VN, 8 pcs) is in ASN00020: case 1 = CO-A 2 + CO-B 4, case 2 = CO-B 4 + CO-C 2. G-System cancels 6 pcs (new serial 0000002, status 2).',
                  'Candidates (UPD_STATUS 6, PO_MAPPED_FLAG N, no ASN, oldest first): CO-E PH 4, CO-F VN 2. From the last case: case 2 CO-B 4 → CO-E; case 1: '
                  '2 of the 4 pcs → CO-F (row split), 2 pcs stay with CO-B.'],
        'steps': [
            ('A1. 17-Oct draft of CO-14110 (no ASN_NO)', 'TB_R_INSTRUCTION', [
                ('new', [21, 1, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'PO-DMY-09004', 'MF-DMY-09004', '0001', None, None]),
                ('new', [22, 2, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'PO-DMY-09004', 'MF-DMY-09004', '0001', None, None])]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('new', ['PO-DMY-09004', 'MF-DMY-09004', '0001', 'PART-Y', 12, 12])]),
            ('A2. 18-Oct XD08: all drafts released', 'TB_R_INSTRUCTION', [
                ('del', [21, 1, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'PO-DMY-09004', 'MF-DMY-09004', '0001', None, None], [], 'Draft deleted'),
                ('del', [22, 2, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'PO-DMY-09004', 'MF-DMY-09004', '0001', None, None], [], 'Draft deleted')]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('upd', ['PO-DMY-09004', 'MF-DMY-09004', '0001', 'PART-Y', 12, 0], ['MAPPED_QTY'], '12 → 0')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14110', PH, '0000001', 'PART-Y', 12, od='2026-10-15'), ['PO_MAPPED_FLAG'], 'Y → N: back in the delivery plan')]),
            ('B1. ASN00020 before the cancel', 'TB_R_INSTRUCTION', [
                ('ref', [41, 1, 1, 'PART-Y', VN, 'CO-A', '0000001', 2, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-01']),
                ('ref', [42, 1, 2, 'PART-Y', VN, 'CO-B', '0000001', 4, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-01']),
                ('ref', [43, 2, 1, 'PART-Y', VN, 'CO-B', '0000001', 4, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-02']),
                ('ref', [44, 2, 2, 'PART-Y', VN, 'CO-C', '0000001', 2, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-02'])]),
            ('B2. XD08: CO-B partial cancel 6 (split serial), CO-E / CO-F received', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-B', VN, '0000001', 'PART-Y', 2, mapped='Y', od='2026-10-16'), ['ORDER_STATUS_QTY'], '8 → 2 (still valid)'),
                ('new', h('CO-B', VN, '0000002', 'PART-Y', 6, st='2', mapped='N', upd='2', od='2026-10-16'), [], 'Cancelled 6 pcs in ASN00020 → XD11'),
                ('upd', h('CO-E', PH, '0000001', 'PART-Y', 4, upd='6', od='2026-10-16'), ['UPD_STATUS'], 'Candidate 1 (oldest)'),
                ('upd', h('CO-F', VN, '0000001', 'PART-Y', 2, upd='6', od='2026-10-17'), ['UPD_STATUS'], 'Candidate 2')]),
            ('B3. XD11: 6 pcs → CO-E 4 + CO-F 2 (from the last case)', 'TB_R_INSTRUCTION', [
                ('ref', [41, 1, 1, 'PART-Y', VN, 'CO-A', '0000001', 2, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-01']),
                ('upd', [42, 1, 2, 'PART-Y', VN, 'CO-B', '0000001', 2, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-01'], ['QTY'], '4 → 2 (row split)'),
                ('new', [45, 1, 3, 'PART-Y', VN, 'CO-F', '0000001', 2, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-01'], [], 'Split part → CO-F'),
                ('upd', [43, 2, 1, 'PART-Y', PH, 'CO-E', '0000001', 4, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-02'],
                 ['DESTINATION_CD', 'CUSTOMER_ORDER_NO'], 'Whole row → CO-E (another destination)'),
                ('ref', [44, 2, 2, 'PART-Y', VN, 'CO-C', '0000001', 2, 'PO-DMY-10041', 'MF-DMY-10041', '0001', 'ASN00020', 'C-0020-02'])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-E', PH, '0000001', 'PART-Y', 4, mapped='Y', upd='6', od='2026-10-16'), ['PO_MAPPED_FLAG']),
                ('upd', h('CO-F', VN, '0000001', 'PART-Y', 2, mapped='Y', upd='6', od='2026-10-17'), ['PO_MAPPED_FLAG'])]),
            ('', 'TB_H_CROSSDOCK_ORDER_CHANGE', [
                ('new', [2, 'ASN00020', 'C-0020-02', 'PART-Y', 'CO-B', '0000002', 'CO-E', PH, 4, 43, 43]),
                ('new', [3, 'ASN00020', 'C-0020-01', 'PART-Y', 'CO-B', '0000002', 'CO-F', VN, 2, 42, 45])]),
        ]},
    {
        'id': 'SIM-7', 'title': 'Scan order, supplier cases and ASN options (two ASNs)', 'flow': 'BPF F2', 'functions': 'XD09, XD10 (ASN Option, Create ASN)',
        'story': ['PART-A 14-Oct, 6 pcs/case: V01 VN 10, T01 TH 6, V02 VN 14 (dummy customer codes CUST-A / B / C give this scan order).',
                  'p1 (24 pcs) is released 15-Oct, p2 (6 pcs) 16-Oct. Cuts are valid after cases 1, 3, 4 and 5 (VN / TH multiples of 6): blocks case 1 | 2-3 | 4 | 5.',
                  '15-Oct: blocks 1-3 Ready, the supplier chooses option 4 cases (blocks 1-3, 24 pcs). 16-Oct: the open 6 pcs of V02 get p2 and go in a second ASN.'],
        'steps': [
            ('1. Customer order lines of the unit (XD08)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('ref', h('V01', VN, '0000001', 'PART-A', 10, cust='CUST-A')), ('ref', h('T01', TH, '0000001', 'PART-A', 6, cust='CUST-B')),
                ('ref', h('V02', VN, '0000001', 'PART-A', 14, cust='CUST-C'))]),
            ('', 'TB_R_PRA_DAILY_ORDER_PART', [('ref', ['MF-DMY-09011', '0001', 'PO-DMY-09011', '0001', 'PART-A', 24], [], 'p1, released 15-Oct')]),
            ('2. [Search] 15-Oct → XD09: 5 cases, 4 blocks; block 4 without PO', '#TEMP_INSTRUCTION',
             tmp([SA], [['PO-DMY-09011', 'MF-DMY-09011', '0001', 24]], notes={('V01', 2): 'Case 2 = VN 4 + TH 2: no cut (VN 10, TH 2)',
                                                                        ('V02', 3): 'Cut: VN 12, TH 6', ('V02', 5): 'No PO yet: block 4 Not Ready'})),
            ('3. Supplier chooses option 4 cases (blocks 1-3) → [Create ASN]', 'TB_R_INSTRUCTION', [
                ('new', [i + 1, c, l, 'PART-A', d, co, '0000001', q, 'PO-DMY-09011', 'MF-DMY-09011', '0001', None, None]) for i, (c, l, d, co, q) in enumerate((
                    (1, 1, VN, 'V01', 6), (2, 1, VN, 'V01', 4), (2, 2, TH, 'T01', 2), (3, 1, TH, 'T01', 4), (3, 2, VN, 'V02', 2), (4, 1, VN, 'V02', 6)))]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('new', ['PO-DMY-09011', 'MF-DMY-09011', '0001', 'PART-A', 24, 24])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('V01', VN, '0000001', 'PART-A', 10, mapped='Y', cust='CUST-A'), ['PO_MAPPED_FLAG'], 'Whole line mapped (10)'),
                ('upd', h('T01', TH, '0000001', 'PART-A', 6, mapped='Y', cust='CUST-B'), ['PO_MAPPED_FLAG'], 'Whole line mapped (6)'),
                ('ref', h('V02', VN, '0000001', 'PART-A', 14, cust='CUST-C'), [], '8 of 14 mapped: stays N, open qty 6')]),
            ('4. p2 released 16-Oct', 'TB_R_PRA_DAILY_ORDER_PART', [('new', ['MF-DMY-10011', '0001', 'PO-DMY-10011', '0001', 'PART-A', 6])]),
            ('5. [Search] 16-Oct → XD09: open qty of V02 (6) cut again from case 1', '#TEMP_INSTRUCTION',
             tmp([[dict(SA[2], QTY=6)]], [['PO-DMY-10011', 'MF-DMY-10011', '0001', 6]], notes={('V02', 1): 'OPEN_ORDER_QTY = 14 - 8 in TB_R_INSTRUCTION'})),
            ('6. [Create ASN] (second ASN)', 'TB_R_INSTRUCTION', [
                ('new', [7, 1, 1, 'PART-A', VN, 'V02', '0000001', 6, 'PO-DMY-10011', 'MF-DMY-10011', '0001', None, None])]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('new', ['PO-DMY-10011', 'MF-DMY-10011', '0001', 'PART-A', 6, 6])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('V02', VN, '0000001', 'PART-A', 14, mapped='Y', cust='CUST-C'), ['PO_MAPPED_FLAG'], 'Whole line mapped (8 + 6)')]),
        ]},
    {
        'id': 'SIM-8', 'title': 'SORT_SEQ: H0253 lines into scan order, partial send and re-cut', 'flow': 'BPF F2', 'functions': 'XD09, XD10 (ASN Option, Create ASN)',
        'story': ['PART-B, 6 pcs/case. Scan order = G-System allocation order with Allocation Priority = Customer Order Date: 1) Allocation Priority, '
                  '2) Customer Code, 3) Customer Order No, 4) Order Date, 5) Order Time, 6) Destination, 7) Detailed Item No, 8) Serial No. Keys 2-8 are the PK '
                  'of the H0253 replicate; XD09 reads with ORDER BY Part, Allocation Priority + the PK columns (query in XD09 Appendix). SORT_SEQ = row number per unit.',
                  'Unit 14-Oct: A-0101 item 001 VN 8 (seq 1), A-0101 item 002 VN 2 (seq 2), B-0102 TH 6 (seq 3), C-0103 VN 14 of a second VN customer '
                  '9730000 (seq 4). Order Time 07:00 of C-0103 does not move it up: Customer Code and Order No come first. A-0201 (15-Oct) comes after all '
                  '14-Oct lines (Allocation Priority) and is the next unit.',
                  '15-Oct: PO1 20 pcs → blocks 1-2 Ready, block 3 (case 4) only 2 of 6 pcs with PO → Not Ready. The supplier sends option 1 case only.',
                  '16-Oct: PO2 10 pcs. The open qty (24) is cut again from case 1 in the same SORT_SEQ: the cases are the same as before. Unit 15-Oct '
                  '(A-0201) comes after unit 14-Oct (way B), so it gets no PO yet.'],
        'steps': [
            ('1. H0253 lines in scan order: ORDER BY Part, Allocation Priority (= Order Date), PK columns', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('ref', h('A-0101', VN, '0000001', 'PART-B', 8, item='001'), [], 'Priority 14-Oct · SORT_SEQ 1'),
                ('ref', h('A-0101', VN, '0000001', 'PART-B', 2, item='002'), [], 'Priority 14-Oct · SORT_SEQ 2'),
                ('ref', h('B-0102', TH, '0000001', 'PART-B', 6), [], 'Priority 14-Oct · SORT_SEQ 3'),
                ('ref', h('C-0103', VN, '0000001', 'PART-B', 14, cust=VN2), [], 'Priority 14-Oct · SORT_SEQ 4'),
                ('ref', h('A-0201', VN, '0000001', 'PART-B', 6, od='2026-10-15'), [], 'Priority 15-Oct: after all 14-Oct lines (unit 15-Oct, SORT_SEQ 1)')]),
            ('2. [Search] 15-Oct (PO1 20 pcs) → XD09: SORT_SEQ, cases, blocks', '#TEMP_INSTRUCTION',
             tmp([SB], [['PO-DMY-09021', 'MF-DMY-09021', '0001', 20]],
                 notes={('A-0101', 1): 'SORT_SEQ 1 = 9715300 / A-0101 / item 001', ('B-0102', 2): 'Case 2 = VN 2 + VN 2 + TH 2: no cut (VN 10, TH 2)',
                        ('C-0103', 3): 'Cut: VN 12, TH 6', ('C-0103', 4): 'Case 4: only 2 of 6 pcs with PO1 → block 3 Not Ready, block 4 too'})),
            ('3. Supplier chooses option 1 case → [Create ASN]', 'TB_R_INSTRUCTION', [
                ('new', [1, 1, 1, 'PART-B', VN, 'A-0101', '0000001', 6, 'PO-DMY-09021', 'MF-DMY-09021', '0001', None, None], [], 'Item 001: 6 of 8, open 2')]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('new', ['PO-DMY-09021', 'MF-DMY-09021', '0001', 'PART-B', 20, 6])]),
            ('4. [Search] 16-Oct (PO1 open 14 + PO2 10) → open qty cut again from case 1', '#TEMP_INSTRUCTION',
             tmp([[dict(SB[0], QTY=2)] + SB[1:], SB2], [['PO-DMY-09021', 'MF-DMY-09021', '0001', 14], ['PO-DMY-10021', 'MF-DMY-10021', '0001', 10]],
                 notes={('A-0101', 1): 'Open qty 8 - 6 = 2; case 1 = the same physical case as case 2 on 15-Oct', ('C-0103', 4): 'Unit 14-Oct: all 3 blocks Ready (options 2 / 3 / 4 cases)',
                        ('A-0201', 1): 'Unit 15-Oct after unit 14-Oct (way B): no PO left'})),
        ]},
    {
        'id': 'SIM-9', 'title': 'XD10 case check boxes: cases 1-2 not possible, 1-3 sent', 'flow': 'BPF F2', 'functions': 'XD09, XD10 (Select case, Create ASN)',
        'story': ['Same unit as SIM-7 (PART-A 14-Oct: V01 VN 10, T01 TH 6, V02 VN 14; 6 pcs/case) but all 5 cases have a PO (p1 24 + p2 6).',
                  'XD10 shows one check box per supplier case. The supplier wants cases 1 and 2 only: case 2 = VN 4 + TH 2 ends with VN 10 / TH 2 '
                  '(CUT_FLAG N), so the warehouse could not close the VN and TH cases. XD10 ticks case 3 too (message no. 10): cases 1-3 = 18 pcs.',
                  '[Create ASN] inserts the slices of cases 1-3; V01 and T01 are complete (PO_MAPPED_FLAG Y), V02 keeps 12 pcs open for a later ASN.'],
        'steps': [
            ('1. [Search] → XD09: all cases with PO; CUT_FLAG Y after cases 1, 3, 4, 5', '#TEMP_INSTRUCTION',
             tmp([SA], [['PO-DMY-09011', 'MF-DMY-09011', '0001', 24], ['PO-DMY-10011', 'MF-DMY-10011', '0001', 6]],
                 notes={('V01', 2): 'Case 2 = VN 4 + TH 2: CUT N (VN 10, TH 2) → cannot be the last case',
                        ('V02', 3): 'Case 3: CUT Y (VN 12, TH 6) → ticked together with case 2'})),
            ('2. Supplier ticks cases 1-2 → XD10 ticks case 3 too (MSG10) → [Create ASN] cases 1-3', 'TB_R_INSTRUCTION', [
                ('new', [i + 1, c, l, 'PART-A', d, co, '0000001', q, 'PO-DMY-09011', 'MF-DMY-09011', '0001', None, None]) for i, (c, l, d, co, q) in enumerate((
                    (1, 1, VN, 'V01', 6), (2, 1, VN, 'V01', 4), (2, 2, TH, 'T01', 2), (3, 1, TH, 'T01', 4), (3, 2, VN, 'V02', 2)))]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('new', ['PO-DMY-09011', 'MF-DMY-09011', '0001', 'PART-A', 24, 18], [], '18 of 24 used; 6 left for case 4')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('V01', VN, '0000001', 'PART-A', 10, mapped='Y', cust='CUST-A'), ['PO_MAPPED_FLAG'], 'Whole line in cases 1-2'),
                ('upd', h('T01', TH, '0000001', 'PART-A', 6, mapped='Y', cust='CUST-B'), ['PO_MAPPED_FLAG'], 'Whole line in cases 2-3'),
                ('ref', h('V02', VN, '0000001', 'PART-A', 14, cust='CUST-C'), [], '2 of 14 sent: stays N, open qty 12 (cases 4-5 at the next Search)')]),
        ]},
    {
        'id': 'SIM-10', 'title': 'One line in 2 ASNs; partial receipt splits the serial → XD08 re-assigns TB_R_INSTRUCTION (simulasi_asn.xlsx)', 'flow': 'BPF F2',
        'functions': 'XD09, XD10, XD08 (serial split)',
        'story': ['CO-14115 VN 12 pcs (order date 19-Oct), 6 pcs/case: case 1 → ASN0006 (rit 1), case 2 → ASN0007 (rit 2). One H0253 row, two TB_R_INSTRUCTION rows.',
                  '21-Oct ASN0006 received: G-System splits the line into serial 0000001 6 pcs status 6 and serial 0000002 6 pcs status 7.',
                  'Upsert alone: serial 0000001 has 12 pcs in TB_R_INSTRUCTION for qty 6 and serial 0000002 looks open (6) → XD09 would map it again (double). '
                  'XD08 re-assigns the rows: serial 0000001 = ASN0006 (oldest ASN = received), serial 0000002 = ASN0007; both PO_MAPPED_FLAG Y.'],
        'steps': [
            ('1. 20-Oct ASN0006 (case 1) and ASN0007 (case 2): one line in 2 ASNs', 'TB_R_INSTRUCTION', [
                ('new', [12, 1, 1, 'PART-X', VN, 'CO-14115', '0000001', 6, 'PO-DMY-09015', 'MF-DMY-09015', '0001', 'ASN0006', 'C-0006-01']),
                ('new', [13, 1, 1, 'PART-X', VN, 'CO-14115', '0000001', 6, 'PO-DMY-09016', 'MF-DMY-09016', '0001', 'ASN0007', 'C-0007-01'])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14115', VN, '0000001', 'PART-X', 12, mapped='Y', od='2026-10-19'), ['PO_MAPPED_FLAG'], 'N after ASN0006 (6 of 12), Y after ASN0007')]),
            ('2. 21-Oct XD08 upsert: ASN0006 received, G-System split the line', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14115', VN, '0000001', 'PART-X', 6, mapped='Y', upd='6', od='2026-10-19'), ['ORDER_STATUS_QTY', 'UPD_STATUS'], '12 → 6, received'),
                ('new', h('CO-14115', VN, '0000002', 'PART-X', 6, od='2026-10-19'), [], 'New serial, status 7: without step 3 open qty 6 = double mapping')]),
            ('3. 21-Oct XD08 serial split: rows re-assigned (LOG7)', 'TB_R_INSTRUCTION', [
                ('ref', [12, 1, 1, 'PART-X', VN, 'CO-14115', '0000001', 6, 'PO-DMY-09015', 'MF-DMY-09015', '0001', 'ASN0006', 'C-0006-01'], [], 'Oldest ASN → serial with status 6'),
                ('upd', [13, 1, 1, 'PART-X', VN, 'CO-14115', '0000002', 6, 'PO-DMY-09016', 'MF-DMY-09016', '0001', 'ASN0007', 'C-0007-01'], ['SERIAL_NO'],
                 'Next ASN → serial with status 7; case, PO, ASN not changed')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14115', VN, '0000002', 'PART-X', 6, mapped='Y', od='2026-10-19'), ['PO_MAPPED_FLAG'], 'Fully in TB_R_INSTRUCTION: not taken by XD09')]),
            ('4. 22-Oct XD08: ASN0007 received', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14115', VN, '0000002', 'PART-X', 6, mapped='Y', upd='6', od='2026-10-19'), ['UPD_STATUS'], 'Received')]),
        ]},
]
