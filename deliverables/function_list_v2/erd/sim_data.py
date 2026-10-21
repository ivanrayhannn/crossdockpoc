"""Simulation scenarios of the Crossdock tables (one sheet per scenario in Crossdock_ERD.xlsx).
Each step shows the rows of a table with their state: ref (read, not changed), new (insert), upd (update; changed columns highlighted),
del (delete), temp (temporary table). Dummy data: supplier 50221 plant 1, pcs/case 6."""

VN, TH, PH = '9715310', '9722D10', '9811110'
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
    'TB_R_H0253_ORDER_CONTROL_PRE': ['CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD', 'DETAILED_ITEM_NO', 'SERIAL_NO', 'SHIPPING_PART_NO', 'ORDER_STATUS_QTY',
                                     'ORDER_STATUS', 'HOLD_FLAG', 'PO_MAPPED_FLAG', 'CANCEL_STATUS'],
    'TB_R_PRA_DAILY_ORDER_MANIFEST': ['MANIFEST_NO', 'PO_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_DT', 'CROSS_DOCK_FLAG', 'TOTAL_QTY', 'DELIVERY_DT', 'SUB_ROUTE_CD'],
    'TB_R_PRA_DAILY_ORDER_PART': ['MANIFEST_NO', 'MANIFEST_ITEM', 'PO_NO', 'PO_ITEM', 'PART_NO', 'ORDER_QTY'],
    '#TEMP_INSTRUCTION': ['INSTRUCTION_ID', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'SERIAL_NO', 'PART_NO', 'CUST_ORDER_QTY', 'ASSIGNED_QTY', 'REMAINING_ORDER_QTY',
                          'PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CROSSDOCK_STATUS'],
    'TB_R_INSTRUCTION': ['INSTRUCTION_ID', 'CASE_SEQ', 'LINE_SEQ', 'PART_NO', 'DESTINATION_CD', 'CUSTOMER_ORDER_NO', 'SERIAL_NO', 'QTY', 'PO_NO', 'MANIFEST_NO',
                         'MANIFEST_ITEM', 'ASN_NO', 'CASE_NO'],
    'TB_R_PRA_DAILY_ORDER_MAPPED': ['PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'PART_NO', 'ORDER_QTY', 'MAPPED_QTY'],
    'TB_R_DAILY_ORDER_MANIFEST': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'ASN_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_NO', 'CROSS_DOCK_FLAG', 'TOTAL_ITEM', 'TOTAL_QTY',
                                  'DELIVERY_DT_ORI', 'SUB_ROUTE_CD', 'STATUS'],
    'TB_R_DAILY_ORDER_PART': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CASE_NO', 'PO_NO', 'PO_ITEM', 'ASN_NO', 'PART_NO', 'PART_NAME', 'PO_QTY', 'DELIVERY_QTY'],
    'TB_R_CASE_LABEL_LAST_SEQ': ['SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ'],
    'TB_R_CROSSDOCK_CANCEL_RESULT': ['CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'SERIAL_NO', 'PART_NO', 'CANCEL_QTY', 'VALID_QTY', 'QTY_IN_ASN', 'RELEASED_QTY',
                                     'CONFLICT_QTY', 'RESULT', 'ASN_NO'],
}

# value highlight (column, value) -> fill
VALUE_FILL = {
    ('PART_STATUS', 'Active'): 'C6EFCE', ('PART_STATUS', 'Inactive'): 'D9D9D9', ('PART_STATUS', 'Candidate'): 'DDEBF7',
    ('NEW_STATUS', 'Active'): 'C6EFCE', ('NEW_STATUS', 'Inactive'): 'D9D9D9',
    ('SYNC_STATUS', '0'): 'FCE4D6', ('SYNC_STATUS', '1'): 'C6EFCE', ('SYNC_STATUS', '2'): 'FF7C80',
    ('CROSSDOCK_STATUS', '6'): 'C6EFCE', ('CROSSDOCK_STATUS', '7'): 'FF7C80',
    ('ORDER_STATUS', '2'): 'FF7C80', ('ORDER_STATUS', '6'): 'DDEBF7', ('HOLD_FLAG', 'Y'): 'FF7C80',
    ('CANCEL_STATUS', 'P'): 'F4B084', ('CANCEL_STATUS', 'D'): 'C6EFCE',
    ('RESULT', 'CONFLICT'): 'FF7C80', ('RESULT', 'CANCELLED'): 'F4B084', ('CROSS_DOCK_FLAG', 'X'): 'FFE699',
}

PRA_MAN = {'1': ['3126035901', 'T0409001', '50221', '1', '2026-10-15', 'X', 12, '2026-10-16', 'SD01'],
           '2': ['3126035902', 'T0409002', '50221', '1', '2026-10-15', 'X', 12, '2026-10-16', 'SD01'],
           '3': ['3126035903', 'T0409003', '50221', '1', '2026-10-15', 'X', 6, '2026-10-16', 'SD01']}
PRA_PART = {'1': ['3126035901', '0001', 'T0409001', '0001', 'PART-X', 12], '2': ['3126035902', '0001', 'T0409002', '0001', 'PART-X', 12],
            '3': ['3126035903', '0001', 'T0409003', '0001', 'PART-Y', 6]}


def h(co, d, serial, part, qty, st='7', hold='N', mapped='N', cancel='-', od=OD, item='001'):
    return [co, od, d, item, serial, part, qty, st, hold, mapped, cancel]


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
                  'Supplier searches delivery 16-Oct Rit 1: PART-X (VN 18 pcs = 3 cases, TH 6 = 1 case) and PART-Y (PH 6 = 1 case) are Ready; Create ASN and Submit.',
                  'Result: one ASN with 5 cases / 30 pcs, 3 ASN manifests (one per Pra manifest), 5 ASN part rows (manifest item x case).'],
        'steps': [
            ('1. XD08 27:30: status 7 rows (insert)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('new', h('CO-14101', VN, '0000001', 'PART-X', 10)), ('new', h('CO-14102', VN, '0000001', 'PART-X', 4)),
                ('new', h('CO-14103', VN, '0000001', 'PART-X', 4)), ('new', h('CO-14104', TH, '0000001', 'PART-X', 6)),
                ('new', h('CO-14105', PH, '0000001', 'PART-Y', 6))]),
            ('2. Existing daily order: crossdock manifests and their parts', 'TB_R_PRA_DAILY_ORDER_MANIFEST', [('ref', PRA_MAN[k]) for k in '123']),
            ('', 'TB_R_PRA_DAILY_ORDER_PART', [('ref', PRA_PART[k]) for k in '123']),
            ('3. [Search] → XD09 pre-mapping FIFO (session)', '#TEMP_INSTRUCTION', [
                ('temp', [1, 'CO-14101', VN, '0000001', 'PART-X', 10, 10, 0, 'T0409001', '3126035901', '0001', '6']),
                ('temp', [2, 'CO-14102', VN, '0000001', 'PART-X', 4, 2, 2, 'T0409001', '3126035901', '0001', '6']),
                ('temp', [3, 'CO-14102', VN, '0000001', 'PART-X', 4, 2, 0, 'T0409002', '3126035902', '0001', '6']),
                ('temp', [4, 'CO-14103', VN, '0000001', 'PART-X', 4, 4, 0, 'T0409002', '3126035902', '0001', '6']),
                ('temp', [5, 'CO-14104', TH, '0000001', 'PART-X', 6, 6, 0, 'T0409002', '3126035902', '0001', '6']),
                ('temp', [6, 'CO-14105', PH, '0000001', 'PART-Y', 6, 6, 0, 'T0409003', '3126035903', '0001', '6'])]),
            ('4. [Create ASN]: real mapping, flags, mapped qty', 'TB_R_INSTRUCTION', [
                ('new', [i + 1, c, l, p, d, co, '0000001', q, po, m, '0001', None, None]) for i, (c, l, p, d, co, q, po, m) in enumerate((
                    (1, 1, 'PART-X', VN, 'CO-14101', 6, 'T0409001', '3126035901'), (2, 1, 'PART-X', VN, 'CO-14101', 4, 'T0409001', '3126035901'),
                    (2, 2, 'PART-X', VN, 'CO-14102', 2, 'T0409001', '3126035901'), (3, 1, 'PART-X', VN, 'CO-14102', 2, 'T0409002', '3126035902'),
                    (3, 2, 'PART-X', VN, 'CO-14103', 4, 'T0409002', '3126035902'), (4, 1, 'PART-X', TH, 'CO-14104', 6, 'T0409002', '3126035902'),
                    (5, 1, 'PART-Y', PH, 'CO-14105', 6, 'T0409003', '3126035903')))]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [
                ('new', ['T0409001', '3126035901', '0001', 'PART-X', 12, 12]), ('new', ['T0409002', '3126035902', '0001', 'PART-X', 12, 12]),
                ('new', ['T0409003', '3126035903', '0001', 'PART-Y', 6, 6])]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h(co, d, '0000001', p, q, mapped='Y'), ['PO_MAPPED_FLAG']) for co, d, p, q in (
                    ('CO-14101', VN, 'PART-X', 10), ('CO-14102', VN, 'PART-X', 4), ('CO-14103', VN, 'PART-X', 4), ('CO-14104', TH, 'PART-X', 6),
                    ('CO-14105', PH, 'PART-Y', 6))]),
            ('5. [Submit ASN] (5.7): ASN tables, last sequence, write back', 'TB_R_DAILY_ORDER_MANIFEST', [
                ('new', [f'{m}A1', m, ASN, '50221', '1', po, 'X', 1, q, '2026-10-16', 'SD01', 'Created'])
                for m, po, q in (('3126035901', 'T0409001', 12), ('3126035902', 'T0409002', 12), ('3126035903', 'T0409003', 6))]),
            ('', 'TB_R_DAILY_ORDER_PART', [
                ('new', [f'{m}A1', m, '0001', c, po, '0001', ASN, p, f'DUMMY {p.replace("-", " ")}', pq, 6]) for m, c, po, p, pq in (
                    ('3126035901', 'C-0001', 'T0409001', 'PART-X', 12), ('3126035901', 'C-0002', 'T0409001', 'PART-X', 12),
                    ('3126035902', 'C-0003', 'T0409002', 'PART-X', 12), ('3126035902', 'C-0004', 'T0409002', 'PART-X', 12),
                    ('3126035903', 'C-0005', 'T0409003', 'PART-Y', 6))]),
            ('', 'TB_R_CASE_LABEL_LAST_SEQ', [('upd', ['50221', '1', '005', '001'], ['CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ'], '000 / 000 → 005 / 001')]),
            ('', 'TB_R_INSTRUCTION', [
                ('upd', [i + 1, c, l, p, d, co, '0000001', q, po, m, '0001', ASN, f'C-{c:04d}'], ['ASN_NO', 'CASE_NO']) for i, (c, l, p, d, co, q, po, m) in enumerate((
                    (1, 1, 'PART-X', VN, 'CO-14101', 6, 'T0409001', '3126035901'), (2, 1, 'PART-X', VN, 'CO-14101', 4, 'T0409001', '3126035901'),
                    (2, 2, 'PART-X', VN, 'CO-14102', 2, 'T0409001', '3126035901'), (3, 1, 'PART-X', VN, 'CO-14102', 2, 'T0409002', '3126035902'),
                    (3, 2, 'PART-X', VN, 'CO-14103', 4, 'T0409002', '3126035902'), (4, 1, 'PART-X', TH, 'CO-14104', 6, 'T0409002', '3126035902'),
                    (5, 1, 'PART-Y', PH, 'CO-14105', 6, 'T0409003', '3126035903')))]),
        ]},
    {
        'id': 'SIM-3', 'title': 'Unit Not Ready (PO short), Ready the next day', 'flow': 'BPF F2 / AB08', 'functions': 'XD09, XD10',
        'story': ['PART-X 14-Oct needs 24 pcs (VN 18, TH 6) but only 18 pcs of crossdock PO are released on 15-Oct (T0409001 12 + T0409002 6).',
                  'FIFO: CO-14104 (TH 6) gets no PO → 1 of 4 cases not assigned → the whole unit is Not Ready (the unit stays whole, decision A2).',
                  'On 16-Oct a new crossdock manifest (T0410001, 6 pcs) is released → [Search] again → all lines assigned → Ready.'],
        'steps': [
            ('1. Crossdock PO of 15-Oct (only 18 pcs)', 'TB_R_PRA_DAILY_ORDER_PART', [
                ('ref', PRA_PART['1']), ('ref', ['3126035902', '0001', 'T0409002', '0001', 'PART-X', 6])]),
            ('2. [Search] 15-Oct → XD09: CO-14104 without PO, unit Not Ready', '#TEMP_INSTRUCTION', [
                ('temp', [1, 'CO-14101', VN, '0000001', 'PART-X', 10, 10, 0, 'T0409001', '3126035901', '0001', '7']),
                ('temp', [2, 'CO-14102', VN, '0000001', 'PART-X', 4, 2, 2, 'T0409001', '3126035901', '0001', '7']),
                ('temp', [3, 'CO-14102', VN, '0000001', 'PART-X', 4, 2, 0, 'T0409002', '3126035902', '0001', '7']),
                ('temp', [4, 'CO-14103', VN, '0000001', 'PART-X', 4, 4, 0, 'T0409002', '3126035902', '0001', '7']),
                ('temp', [5, 'CO-14104', TH, '0000001', 'PART-X', 6, 0, 6, None, None, None, '7'], ['ASSIGNED_QTY', 'REMAINING_ORDER_QTY', 'PO_NO'],
                 'No PO left: tooltip MSG2 "1 of 4 cases not assigned"')]),
            ('3. New crossdock manifest released 16-Oct', 'TB_R_PRA_DAILY_ORDER_MANIFEST', [
                ('new', ['3126036001', 'T0410001', '50221', '1', '2026-10-16', 'X', 6, '2026-10-17', 'SD01'])]),
            ('', 'TB_R_PRA_DAILY_ORDER_PART', [('new', ['3126036001', '0001', 'T0410001', '0001', 'PART-X', 6])]),
            ('4. [Search] 16-Oct → XD09: all lines assigned, Ready', '#TEMP_INSTRUCTION', [
                ('temp', [5, 'CO-14104', TH, '0000001', 'PART-X', 6, 6, 0, 'T0410001', '3126036001', '0001', '6'], ['ASSIGNED_QTY', 'PO_NO', 'CROSSDOCK_STATUS'],
                 'Other rows of the unit also become 6 (Ready)')]),
        ]},
    {
        'id': 'SIM-4', 'title': 'Hold a destination (D/S team)', 'flow': 'BPF F4 / AB09', 'functions': 'XD10 (D/S view), XD09, XD10 Create ASN',
        'story': ['The D/S team holds Thailand of PART-X 14-Oct: HOLD_FLAG Y on CO-14104.',
                  'XD09 does not take held lines: the unit is computed with Vietnam only (18 pcs = 3 cases) and is Ready.',
                  'If the supplier had ticked the unit before the hold, [Create ASN] fails for the whole selection (MSG8): nothing is inserted.'],
        'steps': [
            ('1. D/S Hold Thailand (XD10)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('ref', h('CO-14101', VN, '0000001', 'PART-X', 10)), ('ref', h('CO-14102', VN, '0000001', 'PART-X', 4)),
                ('ref', h('CO-14103', VN, '0000001', 'PART-X', 4)),
                ('upd', h('CO-14104', TH, '0000001', 'PART-X', 6, hold='Y'), ['HOLD_FLAG'], 'Hold by D/S')]),
            ('2. [Search] → XD09 without the held line', '#TEMP_INSTRUCTION', [
                ('temp', [1, 'CO-14101', VN, '0000001', 'PART-X', 10, 10, 0, 'T0409001', '3126035901', '0001', '6']),
                ('temp', [2, 'CO-14102', VN, '0000001', 'PART-X', 4, 2, 2, 'T0409001', '3126035901', '0001', '6']),
                ('temp', [3, 'CO-14102', VN, '0000001', 'PART-X', 4, 2, 0, 'T0409002', '3126035902', '0001', '6']),
                ('temp', [4, 'CO-14103', VN, '0000001', 'PART-X', 4, 4, 0, 'T0409002', '3126035902', '0001', '6'])]),
            ('3. Hold placed after the supplier ticked the unit → [Create ASN] fails (MSG8)', 'TB_R_INSTRUCTION', [
                ('ref', [None, None, None, None, None, None, None, None, None, None, None, None, None], [], 'No row inserted (roll back); delivery plan refreshed')]),
            ('4. D/S Release Thailand', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14104', TH, '0000001', 'PART-X', 6, hold='N'), ['HOLD_FLAG'], 'Released: taken again by the next [Search]')]),
        ]},
    {
        'id': 'SIM-5', 'title': 'Partial cancel before submit (CANCELLED)', 'flow': 'BPF F4', 'functions': 'G-System, XD12, XD11, XD08',
        'story': ['CO-14110 (PART-Y, Philippines, 12 pcs) is in an open Case List (Create ASN done, not submitted).',
                  'G-System cancels 6 pcs: the line is split into serial 0000001 (status 7, 6 pcs) and serial 0000002 (status 2, 6 pcs).',
                  'XD12 marks the cancel (P); XD11: CANCEL 6, VALID 6, IN ASN 0, OPEN 12 → the open mapping is released → CANCELLED; XD08 updates serial 1.'],
        'steps': [
            ('1. Before: open mapping of CO-14110', 'TB_R_INSTRUCTION', [
                ('ref', [21, 1, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'T0409004', '3126035904', '0001', None, None]),
                ('ref', [22, 2, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'T0409004', '3126035904', '0001', None, None])]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('ref', ['T0409004', '3126035904', '0001', 'PART-Y', 12, 12])]),
            ('2. XD12 27:30: status 2 row of the line (CANCEL_STATUS P)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('ref', h('CO-14110', PH, '0000001', 'PART-Y', 12, mapped='Y', od='2026-10-15')),
                ('new', h('CO-14110', PH, '0000002', 'PART-Y', 6, st='2', mapped='N', cancel='P', od='2026-10-15'), [], 'Cancelled part (new serial)')]),
            ('3. XD11: release the open mapping', 'TB_R_INSTRUCTION', [
                ('del', [21, 1, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'T0409004', '3126035904', '0001', None, None], [], 'Deleted (no ASN_NO)'),
                ('del', [22, 2, 1, 'PART-Y', PH, 'CO-14110', '0000001', 6, 'T0409004', '3126035904', '0001', None, None], [], 'Deleted (no ASN_NO)')]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('upd', ['T0409004', '3126035904', '0001', 'PART-Y', 12, 0], ['MAPPED_QTY'], '12 → 0')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14110', PH, '0000001', 'PART-Y', 12, mapped='N', od='2026-10-15'), ['PO_MAPPED_FLAG'], 'Pre-mapped again by the next XD09'),
                ('upd', h('CO-14110', PH, '0000002', 'PART-Y', 6, st='2', mapped='N', cancel='D', od='2026-10-15'), ['CANCEL_STATUS'], 'P → D')]),
            ('', 'TB_R_CROSSDOCK_CANCEL_RESULT', [('new', ['CO-14110', PH, '0000002', 'PART-Y', 6, 6, 0, 12, 0, 'CANCELLED', None])]),
            ('4. XD08: valid qty of serial 1 (status 7, 6 pcs)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14110', PH, '0000001', 'PART-Y', 6, mapped='N', od='2026-10-15'), ['ORDER_STATUS_QTY'], '12 → 6')]),
        ]},
    {
        'id': 'SIM-6', 'title': 'Cancel after ASN (CONFLICT, abnormality AB16)', 'flow': 'BPF F4 / AB16', 'functions': 'G-System, XD12, XD11, Log Monitoring',
        'story': ['CO-14103 (PART-X, Vietnam, 4 pcs) is already in ASN-50221-261016-001, case C-0003.',
                  'G-System cancels the line although it is in an ASN (SOP not followed): status 2.',
                  'XD11: CANCEL 4, VALID 0, IN ASN 4 → CONFLICT 4; the ASN is not changed (no Cancel ASN); D/S handles case C-0003 at receiving.'],
        'steps': [
            ('1. Before: the line is in the ASN', 'TB_R_INSTRUCTION', [
                ('ref', [5, 3, 2, 'PART-X', VN, 'CO-14103', '0000001', 4, 'T0409002', '3126035902', '0001', ASN, 'C-0003'])]),
            ('2. XD12 27:30: status 2 (CANCEL_STATUS P)', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14103', VN, '0000001', 'PART-X', 4, st='2', mapped='Y', cancel='P'), ['ORDER_STATUS', 'CANCEL_STATUS'], 'Cancelled in G-System')]),
            ('3. XD11: CONFLICT, ASN not changed', 'TB_R_INSTRUCTION', [
                ('ref', [5, 3, 2, 'PART-X', VN, 'CO-14103', '0000001', 4, 'T0409002', '3126035902', '0001', ASN, 'C-0003'], [], 'Not changed (has ASN_NO)')]),
            ('', 'TB_R_PRA_DAILY_ORDER_MAPPED', [('ref', ['T0409002', '3126035902', '0001', 'PART-X', 12, 12], [], 'Not changed (PO qty not blocked)')]),
            ('', 'TB_R_H0253_ORDER_CONTROL_PRE', [
                ('upd', h('CO-14103', VN, '0000001', 'PART-X', 4, st='2', mapped='Y', cancel='D'), ['CANCEL_STATUS'], 'P → D')]),
            ('', 'TB_R_CROSSDOCK_CANCEL_RESULT', [('new', ['CO-14103', VN, '0000001', 'PART-X', 4, 0, 4, 0, 4, 'CONFLICT', ASN], [], 'Log LOG4 → Log Monitoring')]),
        ]},
]
