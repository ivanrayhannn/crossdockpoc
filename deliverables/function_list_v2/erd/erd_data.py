"""Concept ERD of Crossdock (function list v2) and one consistent set of simulation data.
Columns come from the UISS specs (deliverables/function_list_v2/specs); the two Pra Daily Order tables are existing NSP tables
that the UISS only reference, so their key columns are listed here."""

# kind -> (label, header fill, header font)
KIND = {
    'new': ('New table (Crossdock)', '1F3864', 'FFFFFF'),
    'replica': ('Replicated from DB Surrounding (G-TOPAS)', '5B4A8B', 'FFFFFF'),
    'existing': ('Existing NSP table', '595959', 'FFFFFF'),
    'temp': ('Temporary (session)', 'A6A6A6', 'FFFFFF'),
}

# group (column of the diagram) -> tables top to bottom
LAYOUT = [
    ['TB_M_H0125_DESTINATION', 'TB_R_ACTUAL_DEMAND_SUMMARY'],
    ['TB_M_PART_MASTER', 'TB_M_PART_CANDIDATE_DEST', 'TB_R_PART_DAD_RESULT'],
    ['TB_M_PART_CANDIDATE', 'TB_H_PART_CANDIDATE', 'TB_R_CROSSDOCK_IF_RESULT'],
    ['TB_R_H0253_ORDER_CONTROL_PRE', 'TB_R_CROSSDOCK_CANCEL_RESULT'],
    ['TB_R_INSTRUCTION', '#TEMP_INSTRUCTION'],
    ['TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_PRA_DAILY_ORDER_PART', 'TB_R_PRA_DAILY_ORDER_MAPPED'],
    ['TB_R_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_PART', 'TB_R_CASE_LABEL_LAST_SEQ'],
]

TABLE_KIND = {
    'TB_M_H0125_DESTINATION': 'replica', 'TB_R_ACTUAL_DEMAND_SUMMARY': 'replica', 'TB_R_H0253_ORDER_CONTROL_PRE': 'replica',
    'TB_M_PART_CANDIDATE': 'new', 'TB_M_PART_CANDIDATE_DEST': 'new', 'TB_H_PART_CANDIDATE': 'new', 'TB_R_PART_DAD_RESULT': 'new',
    'TB_R_CROSSDOCK_IF_RESULT': 'new', 'TB_R_CROSSDOCK_CANCEL_RESULT': 'new', 'TB_R_INSTRUCTION': 'new', 'TB_R_PRA_DAILY_ORDER_MAPPED': 'new',
    '#TEMP_INSTRUCTION': 'temp',
    'TB_R_PRA_DAILY_ORDER_MANIFEST': 'existing', 'TB_R_PRA_DAILY_ORDER_PART': 'existing', 'TB_R_DAILY_ORDER_MANIFEST': 'existing',
    'TB_R_DAILY_ORDER_PART': 'existing', 'TB_M_PART_MASTER': 'existing', 'TB_R_CASE_LABEL_LAST_SEQ': 'existing',
}

# Pra Daily Order tables (existing NSP): structure from NSP_INSERT_TB_R_PRA_DAILY_ORDER_MANIFEST / _PART.sql (20-Oct), saved in
# pra_structure.json (columns, type inferred from the sample data, PK proposed from the data); descriptions of the columns used by Crossdock:
PRA_NOTES = {
    'TB_R_PRA_DAILY_ORDER_MANIFEST': ('Existing Pra Daily Order manifest (supplier PO per manifest, 391 sample rows). MANIFEST_NO is unique; one PO_NO can have '
                                      'several manifests. CROSS_DOCK_FLAG is on the manifest.', {
        'MANIFEST_NO': 'Manifest number (unique in the sample)', 'PO_NO': 'PO number; one PO can be split over several manifests',
        'SUPPLIER_CD': 'Supplier code (4 characters in the sample)', 'SUPPLIER_PLANT': 'Supplier plant', 'PO_DT': 'PO date',
        'ORDER_TYPE': "Order type ('3', 'C' in the sample)", 'CROSS_DOCK_FLAG': "'X' = crossdock manifest (its parts are taken by XD09); NULL otherwise",
        'DOCK_CD': 'Receiving dock', 'TOTAL_ITEM': 'Number of items of the manifest', 'TOTAL_QTY': 'Total order qty of the manifest',
        'DELIVERY_DT': 'Delivery date', 'SUB_ROUTE_CD': 'Route of the delivery (e.g. DS18)', 'SUB_ROUTE_SEQ': 'Sequence (rit) of the route',
        'SUB_ROUTE_DT': 'Date and time of the route', 'STATUS': "Manifest status ('0', '2' in the sample)"}),
    'TB_R_PRA_DAILY_ORDER_PART': ('Existing Pra Daily Order part (one row per manifest item, 2353 sample rows). Key MANIFEST_NO + MANIFEST_ITEM '
                                  '(also PO_NO + PO_ITEM is unique; PO_ITEM can differ from MANIFEST_ITEM).', {
        'MANIFEST_NO': 'Manifest number (TB_R_PRA_DAILY_ORDER_MANIFEST)', 'MANIFEST_ITEM': 'Item of the manifest (0001 ...)',
        'PO_NO': 'PO number', 'PO_ITEM': 'Item of the PO (can differ from MANIFEST_ITEM)', 'PART_NO': 'Part number',
        'PART_NAME': 'Part name', 'QTY_PER_CONTAINER': 'Qty per container of the PO (mostly 1; not the crossdock pcs/case)',
        'ORDER_QTY': 'PO qty (pcs) — basis of the open qty for XD09 (ORDER_QTY - MAPPED_QTY)', 'DELIVERY_QTY': 'Delivered qty',
        'REMAIN_QTY': 'Remaining qty', 'DOCK_CD': 'Receiving dock', 'STATUS': "Status ('0' in the sample)"}),
}

# new-table columns renamed to the names of the existing Pra Daily Order tables (UISS still uses the old names)
RENAME = {'MANIFEST_ITEM_NO': 'MANIFEST_ITEM', 'PO_ORDER_QTY': 'ORDER_QTY', 'PO_ORDER_DT': 'PO_DT'}

# columns shown in the diagram for the big tables (others: all columns without audit columns)
SHOW = {
    'TB_R_DAILY_ORDER_MANIFEST': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'ASN_NO', 'ASN_DATE', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_NO', 'CROSS_DOCK_FLAG',
                                  'DOCK_CD', 'TOTAL_ITEM', 'TOTAL_QTY', 'DELIVERY_DT_ORI', 'SUB_ROUTE_CD', 'SUB_ROUTE_SEQ', 'STATUS'],
    'TB_R_DAILY_ORDER_PART': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CASE_NO', 'PO_NO', 'PO_ITEM', 'ASN_NO', 'PART_NO', 'PART_NAME', 'PO_QTY',
                              'DELIVERY_QTY'],
    'TB_M_PART_MASTER': ['PART_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'DOCK_CD', 'VALID_FROM', 'PART_NAME', 'VALID_TO'],
    'TB_R_CASE_LABEL_LAST_SEQ': ['SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ'],
    'TB_R_PRA_DAILY_ORDER_MANIFEST': ['MANIFEST_NO', 'PO_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_DT', 'ORDER_TYPE', 'CROSS_DOCK_FLAG', 'DOCK_CD',
                                      'TOTAL_QTY', 'DELIVERY_DT', 'SUB_ROUTE_CD', 'SUB_ROUTE_SEQ', 'STATUS'],
    'TB_R_PRA_DAILY_ORDER_PART': ['MANIFEST_NO', 'MANIFEST_ITEM', 'PO_NO', 'PO_ITEM', 'PART_NO', 'QTY_PER_CONTAINER', 'ORDER_QTY', 'DELIVERY_QTY',
                                  'REMAIN_QTY', 'DOCK_CD', 'STATUS'],
    'TB_R_H0253_ORDER_CONTROL_PRE': ['CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'ORDER_TIME', 'DESTINATION_CD', 'DETAILED_ITEM_NO', 'SERIAL_NO',
                                     'SHIPPING_PART_NO', 'ORDER_STATUS_QTY', 'ORDER_STATUS', 'INTF_UPDATE_DT', 'HOLD_FLAG', 'PO_MAPPED_FLAG', 'CANCEL_STATUS'],
    'TB_R_ACTUAL_DEMAND_SUMMARY': ['GROUPING_BUYER_CD', 'GROUPING_PD_CD', 'ORDER_TYPE_GROUP', 'DEMAND_MONTH_YEAR', 'PART_NO', 'MAD', 'DAD'],
    'TB_M_H0125_DESTINATION': ['DESTINATION_CD', 'CUSTOMER_CD', 'DESTINATION_NAME_ENG', 'REGION_CD', 'COUNTRY_NAME_ENG'],
    '#TEMP_INSTRUCTION': ['INSTRUCTION_ID', 'CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD', 'DETAILED_ITEM_NO', 'SERIAL_NO', 'PART_NO',
                          'ASSIGNED_QTY', 'PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CROSSDOCK_STATUS'],
    'TB_R_INSTRUCTION': ['INSTRUCTION_ID', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'CASE_SEQ', 'LINE_SEQ', 'PART_NO', 'ORDER_DT', 'DESTINATION_CD', 'CUSTOMER_CD',
                         'CUSTOMER_ORDER_NO', 'DETAILED_ITEM_NO', 'SERIAL_NO', 'QTY', 'PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'DELIVERY_DT', 'ASN_NO', 'CASE_NO'],
}

# parent table, parent columns, child table, child columns, cardinality, meaning
RELATIONS = [
    ('TB_M_H0125_DESTINATION', 'DESTINATION_CD', 'TB_M_PART_CANDIDATE_DEST', 'DEST_CODE', '1 : N', 'Destination of a mapping row'),
    ('TB_M_H0125_DESTINATION', 'DESTINATION_CD', 'TB_R_ACTUAL_DEMAND_SUMMARY', 'GROUPING_BUYER_CD + GROUPING_PD_CD', '1 : N', 'Destination of the actual demand (5 + 2 digits)'),
    ('TB_M_PART_CANDIDATE', 'PART_NO', 'TB_M_PART_CANDIDATE_DEST', 'PART_NO', '1 : N', 'Mapping per period and destination'),
    ('TB_M_PART_CANDIDATE', 'PART_NO', 'TB_R_PART_DAD_RESULT', 'PART_NO', '1 : N', 'Monthly calculation result (XD05 process 1)'),
    ('TB_M_PART_CANDIDATE', 'PART_NO', 'TB_H_PART_CANDIDATE', 'PART_NO', '1 : N', 'History of every change'),
    ('TB_M_PART_CANDIDATE', 'PART_NO', 'TB_R_CROSSDOCK_IF_RESULT', 'PART_NO', '1 : 0..2', 'Send status per target system (GTOPAS / APPOLE)'),
    ('TB_M_PART_CANDIDATE', 'PART_NO', 'TB_R_ACTUAL_DEMAND_SUMMARY', 'PART_NO', '1 : N', 'Actual demand of the part (logical, no FK)'),
    ('TB_M_PART_CANDIDATE', 'PART_NO', 'TB_R_H0253_ORDER_CONTROL_PRE', 'SHIPPING_PART_NO', '1 : N', 'Crossdock customer order lines of an Active part (logical)'),
    ('TB_M_H0125_DESTINATION', 'DESTINATION_CD', 'TB_R_H0253_ORDER_CONTROL_PRE', 'DESTINATION_CD', '1 : N', 'Destination of the customer order'),
    ('TB_R_H0253_ORDER_CONTROL_PRE', 'unique key (7 columns)', 'TB_R_CROSSDOCK_CANCEL_RESULT', 'unique key (7 columns)', '1 : 0..1', 'Result of a cancelled row (status 2), XD11'),
    ('TB_R_H0253_ORDER_CONTROL_PRE', 'order line + SERIAL_NO', 'TB_R_INSTRUCTION', 'CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO',
     '1 : N', 'Real mapping: a line can be split over cases and POs'),
    ('TB_R_H0253_ORDER_CONTROL_PRE', 'order line + SERIAL_NO', '#TEMP_INSTRUCTION', 'CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO',
     '1 : N', 'Pre-mapping of one [Search]'),
    ('TB_R_PRA_DAILY_ORDER_MANIFEST', 'MANIFEST_NO', 'TB_R_PRA_DAILY_ORDER_PART', 'MANIFEST_NO', '1 : N', 'Items of a manifest (existing); crossdock when the manifest has CROSS_DOCK_FLAG X'),
    ('TB_R_PRA_DAILY_ORDER_PART', 'MANIFEST_NO + MANIFEST_ITEM', 'TB_R_PRA_DAILY_ORDER_MAPPED', 'MANIFEST_NO + MANIFEST_ITEM', '1 : 0..1', 'Mapped qty of a crossdock PO line'),
    ('TB_R_PRA_DAILY_ORDER_PART', 'MANIFEST_NO + MANIFEST_ITEM', 'TB_R_INSTRUCTION', 'MANIFEST_NO + MANIFEST_ITEM', '1 : N', 'PO line of a mapping row'),
    ('TB_R_PRA_DAILY_ORDER_PART', 'MANIFEST_NO + MANIFEST_ITEM', '#TEMP_INSTRUCTION', 'MANIFEST_NO + MANIFEST_ITEM', '1 : N', 'PO line of a pre-mapping row'),
    ('TB_R_DAILY_ORDER_MANIFEST', 'SUB_MANIFEST_NO + MANIFEST_NO', 'TB_R_DAILY_ORDER_PART', 'SUB_MANIFEST_NO + MANIFEST_NO', '1 : N', 'Items x cases of an ASN manifest (existing)'),
    ('TB_R_DAILY_ORDER_PART', 'MANIFEST_NO + MANIFEST_ITEM + CASE_NO', 'TB_R_INSTRUCTION', 'MANIFEST_NO + MANIFEST_ITEM + CASE_NO', '1 : N',
     'Customer order lines of a manifest item in a case (CASE_NO / ASN_NO filled on submit)'),
    ('TB_R_PRA_DAILY_ORDER_MANIFEST', 'MANIFEST_NO', 'TB_R_DAILY_ORDER_MANIFEST', 'MANIFEST_NO', '1 : N', 'ASN manifest created from the Pra manifest on submit'),
    ('TB_M_PART_MASTER', 'PART_NO', 'TB_M_PART_CANDIDATE', 'PART_NO', '1 : 0..1', 'Part name and existence check (logical)'),
    ('TB_R_CASE_LABEL_LAST_SEQ', 'SUPPLIER_CD + SUPPLIER_PLANT_CD', 'TB_R_DAILY_ORDER_MANIFEST', 'SUPPLIER_CD + SUPPLIER_PLANT', '1 : N',
     'Last sequence of the ASN number and the case numbers per supplier + plant (logical)'),
]

# ------------------------------------------------------------------ simulation data
SCENARIO = [
    'One consistent data set for supplier 50221 plant 1, pcs/case = 6, calculation period Oct 2026 (202610), delivery 16-Oct-2026 Rit 1 (route SD01).',
    'PART-X: Active, mapped to Vietnam / Thailand / Philippines. PART-Y: Candidate → Active this month. PART-Z: Active → Inactive this month (sent with CROSSDOCK_FLAG N).',
    'ASN: PART-X 14-Oct (Vietnam 18 pcs = 3 cases, Thailand 6 pcs = 1 case) and PART-Y 14-Oct (Philippines 6 pcs = 1 case) → ASN-50221-261016-001, 5 cases, 30 pcs.',
    'Cancel: CO-14110 (PART-Y, 12 pcs) partially cancelled 6 pcs before any ASN → CANCELLED. CO-14103 (4 pcs, already in the ASN) cancelled → CONFLICT (abnormality AB16).',
]

VN, TH, PH = '9715310', '9722D10', '9811110'
OD, T = '2026-10-14', '080000'

SIM = [
    ('TB_M_H0125_DESTINATION', 'XD13 (weekly, delete – insert from DB Surrounding)',
     ['DESTINATION_CD', 'CUSTOMER_CD', 'DESTINATION_NAME_ENG', 'REGION_CD', 'COUNTRY_NAME_ENG'],
     [[VN, '97153', 'DUMMY DESTINATION VIETNAM', 'ASIA', 'VIETNAM'], [TH, '9722D', 'DUMMY DESTINATION THAILAND', 'ASIA', 'THAILAND'],
      [PH, '98111', 'DUMMY DESTINATION PHILIPPINES', 'ASIA', 'PHILIPPINES']]),
    ('TB_R_ACTUAL_DEMAND_SUMMARY', 'XD04 (monthly, delete – insert). Range of XD05: Jul–Sep 2026 (3 months)',
     ['GROUPING_BUYER_CD', 'GROUPING_PD_CD', 'ORDER_TYPE_GROUP', 'DEMAND_MONTH_YEAR', 'PART_NO', 'MAD'],
     [[b, p, 'N', m, part, q] for part, b, p, qs in (('PART-X', '97153', '10', (180, 190, 200)), ('PART-X', '9722D', '10', (90, 95, 100)),
                                                     ('PART-X', '98111', '10', (30, 30, 30)), ('PART-Y', '98111', '10', (120, 130, 140)),
                                                     ('PART-Z', '97153', '10', (40, 35, 30)))
      for m, q in zip(('202607', '202608', '202609'), qs)]),
    ('TB_M_PART_CANDIDATE', 'XD01 / XD02 (Procurement); PART_STATUS by XD05; SYNC_STATUS by XD03 / XD05 / XD06 / XD07',
     ['PART_NO', 'PART_NAME', 'MIN_MAD', 'PCS_CASE', 'MAX_CASE_DAY', 'TOTAL_PCS_DAY', 'EFFECTIVE_START_DATE', 'PART_STATUS', 'SYNC_STATUS', 'SYNC_DT', 'LAST_SOURCE'],
     [['PART-X', 'DUMMY PART X', 300, 6, 10, 60, '2026-09-01', 'Active', '1', '2026-10-02 09:15', 'CALC'],
      ['PART-Y', 'DUMMY PART Y', 100, 6, 2, 12, '2026-10-01', 'Active', '1', '2026-10-02 09:15', 'CALC'],
      ['PART-Z', 'DUMMY PART Z', 50, 6, 4, 24, '2026-05-01', 'Inactive', '1', '2026-10-02 09:15', 'CALC']]),
    ('TB_R_PART_DAD_RESULT', 'XD05 process 1 (01-Oct-2026): AVG_MAD = TOTAL_MAD / NUM_OF_MONTH, Active when AVG_MAD ≥ MIN_MAD',
     ['PERIOD', 'PART_NO', 'MONTH_FROM', 'MONTH_TO', 'NUM_OF_MONTH', 'TOTAL_MAD', 'AVG_MAD', 'MIN_MAD', 'OLD_STATUS', 'NEW_STATUS'],
     [['202610', 'PART-X', '202607', '202609', 3, 945, 315, 300, 'Active', 'Active'],
      ['202610', 'PART-Y', '202607', '202609', 3, 390, 130, 100, 'Candidate', 'Active'],
      ['202610', 'PART-Z', '202607', '202609', 3, 105, 35, 50, 'Active', 'Inactive']]),
    ('TB_M_PART_CANDIDATE_DEST', 'XD05 process 2 (Max Case/Day by MAD share: VN 60 %, TH 30 %, PH 10 %); D/S may adjust (XD01 / XD03)',
     ['PART_NO', 'PERIOD', 'DEST_CODE', 'CASE_DAY'],
     [['PART-X', '202610', VN, 6], ['PART-X', '202610', TH, 3], ['PART-X', '202610', PH, 1], ['PART-Y', '202610', PH, 2]]),
    ('TB_H_PART_CANDIDATE', 'XD01 / XD02 / XD03 / XD05 / XD06 / XD07 (insert only, one row per changed field)',
     ['HIST_ID', 'PART_NO', 'PERIOD', 'EVENT_TYPE', 'SOURCE', 'DEST_CODE', 'FIELD_NAME', 'OLD_VALUE', 'NEW_VALUE', 'REMARK', 'CREATED_BY', 'CREATED_DT'],
     [[1001, 'PART-Y', None, 'ADD', 'SCREEN', None, 'MIN_MAD', None, '100', None, 'PROC01', '2026-09-20 10:05'],
      [1002, 'PART-Y', '202610', 'CALC', 'BATCH', None, 'PART_STATUS', 'Candidate', 'Active', None, 'XD05', '2026-10-01 03:10'],
      [1003, 'PART-Z', '202610', 'CALC', 'BATCH', None, 'PART_STATUS', 'Active', 'Inactive', None, 'XD05', '2026-10-01 03:10'],
      [1004, 'PART-Z', '202610', 'CALC', 'BATCH', None, 'SYNC_STATUS', '1', '0', 'Became Inactive: to be sent with flag N', 'XD05', '2026-10-01 03:10'],
      [1005, 'PART-X', '202610', 'MAPPING', 'BATCH', VN, 'CASE_DAY', '5', '6', None, 'XD05', '2026-10-01 03:20'],
      [1006, 'PART-X', '202610', 'SYNC', 'IF', None, 'SYNC_STATUS', '0', '1', 'GTOPAS: OK', 'XD06', '2026-10-02 09:15'],
      [1007, 'PART-X', '202610', 'SYNC', 'IF', None, 'SYNC_STATUS', '0', '1', 'APPOLE: OK', 'XD07', '2026-10-02 09:15']]),
    ('TB_R_CROSSDOCK_IF_RESULT', 'XD06 / XD07 after [Sync] (dummy table, one row per part and target)',
     ['PART_NO', 'TARGET_SYSTEM', 'PERIOD', 'IF_STATUS', 'IF_DT', 'IF_FILE_NAME', 'IF_MESSAGE'],
     [['PART-X', 'GTOPAS', '202610', '1', '2026-10-02 09:15', 'SEND-20261002-01', 'OK'],
      ['PART-X', 'APPOLE', '202610', '1', '2026-10-02 09:15', 'XDOCK_MASTER_20261002_0915.csv', 'OK'],
      ['PART-Z', 'GTOPAS', '202610', '1', '2026-10-02 09:15', 'SEND-20261002-01', 'OK (CROSSDOCK_FLAG N)'],
      ['PART-Z', 'APPOLE', '202610', '1', '2026-10-02 09:15', 'XDOCK_MASTER_20261002_0915.csv', 'OK (CROSSDOCK_FLAG N)']]),
    ('TB_R_H0253_ORDER_CONTROL_PRE', 'XD08 / XD12 upsert from DB Surrounding; HOLD_FLAG by XD10 (D/S), PO_MAPPED_FLAG by [Create ASN], CANCEL_STATUS by XD12 / XD11. State after 16-Oct 27:30',
     ['CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'ORDER_TIME', 'DESTINATION_CD', 'DETAILED_ITEM_NO', 'SERIAL_NO', 'SHIPPING_PART_NO', 'ORDER_STATUS_QTY',
      'ORDER_STATUS', 'INTF_UPDATE_DT', 'HOLD_FLAG', 'PO_MAPPED_FLAG', 'CANCEL_STATUS'],
     [['97153', 'CO-14101', OD, T, VN, '001', '0000001', 'PART-X', 10, '7', '2026-10-14 20:00', 'N', 'Y', '-'],
      ['97153', 'CO-14102', OD, T, VN, '001', '0000001', 'PART-X', 4, '7', '2026-10-14 20:00', 'N', 'Y', '-'],
      ['97153', 'CO-14103', OD, T, VN, '001', '0000001', 'PART-X', 4, '2', '2026-10-16 18:00', 'N', 'Y', 'D'],
      ['9722D', 'CO-14104', OD, T, TH, '001', '0000001', 'PART-X', 6, '7', '2026-10-14 20:00', 'N', 'Y', '-'],
      ['98111', 'CO-14105', OD, T, PH, '001', '0000001', 'PART-Y', 6, '7', '2026-10-14 20:00', 'N', 'Y', '-'],
      ['98111', 'CO-14110', '2026-10-15', T, PH, '001', '0000001', 'PART-Y', 6, '7', '2026-10-16 18:00', 'N', 'N', '-'],
      ['98111', 'CO-14110', '2026-10-15', T, PH, '001', '0000002', 'PART-Y', 6, '2', '2026-10-16 18:00', 'N', 'N', 'D']]),
    ('TB_R_PRA_DAILY_ORDER_MANIFEST', 'Existing daily order (supplier PO per manifest); CROSS_DOCK_FLAG X = crossdock manifest',
     ['MANIFEST_NO', 'PO_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_DT', 'ORDER_TYPE', 'CROSS_DOCK_FLAG', 'DOCK_CD', 'TOTAL_ITEM', 'TOTAL_QTY', 'DELIVERY_DT',
      'SUB_ROUTE_CD', 'SUB_ROUTE_SEQ', 'STATUS'],
     [['3126035901', 'T0409001', '50221', '1', '2026-10-15', '3', 'X', 'S1', 1, 12, '2026-10-16', 'SD01', '1', '0'],
      ['3126035902', 'T0409002', '50221', '1', '2026-10-15', '3', 'X', 'S1', 1, 12, '2026-10-16', 'SD01', '1', '0'],
      ['3126035903', 'T0409003', '50221', '1', '2026-10-15', '3', 'X', 'S1', 1, 6, '2026-10-16', 'SD01', '1', '0']]),
    ('TB_R_PRA_DAILY_ORDER_PART', 'Existing daily order (one row per manifest item)',
     ['MANIFEST_NO', 'MANIFEST_ITEM', 'PO_NO', 'PO_ITEM', 'PART_NO', 'PART_NAME', 'QTY_PER_CONTAINER', 'ORDER_QTY', 'DELIVERY_QTY', 'REMAIN_QTY', 'DOCK_CD', 'STATUS'],
     [['3126035901', '0001', 'T0409001', '0001', 'PART-X', 'DUMMY PART X', 1, 12, 0, 12, 'S1', '0'],
      ['3126035902', '0001', 'T0409002', '0001', 'PART-X', 'DUMMY PART X', 1, 12, 0, 12, 'S1', '0'],
      ['3126035903', '0001', 'T0409003', '0001', 'PART-Y', 'DUMMY PART Y', 1, 6, 0, 6, 'S1', '0']]),
    ('#TEMP_INSTRUCTION', 'XD09 on [Search] 16-Oct (session only): order line x PO, FIFO',
     ['INSTRUCTION_ID', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD', 'SERIAL_NO', 'PART_NO', 'CUST_ORDER_QTY', 'ASSIGNED_QTY', 'PO_NO', 'MANIFEST_NO',
      'MANIFEST_ITEM', 'CROSSDOCK_STATUS'],
     [[1, 'CO-14101', OD, VN, '0000001', 'PART-X', 10, 10, 'T0409001', '3126035901', '0001', '6'],
      [2, 'CO-14102', OD, VN, '0000001', 'PART-X', 4, 2, 'T0409001', '3126035901', '0001', '6'],
      [3, 'CO-14102', OD, VN, '0000001', 'PART-X', 4, 2, 'T0409002', '3126035902', '0001', '6'],
      [4, 'CO-14103', OD, VN, '0000001', 'PART-X', 4, 4, 'T0409002', '3126035902', '0001', '6'],
      [5, 'CO-14104', OD, TH, '0000001', 'PART-X', 6, 6, 'T0409002', '3126035902', '0001', '6'],
      [6, 'CO-14105', OD, PH, '0000001', 'PART-Y', 6, 6, 'T0409003', '3126035903', '0001', '6']]),
    ('TB_R_INSTRUCTION', '[Create ASN] + Submit (XD10 5.7): one row per case x order line x PO; ASN_NO / CASE_NO filled on submit',
     ['INSTRUCTION_ID', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'CASE_SEQ', 'LINE_SEQ', 'PART_NO', 'ORDER_DT', 'DESTINATION_CD', 'CUSTOMER_ORDER_NO', 'SERIAL_NO', 'QTY',
      'PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'DELIVERY_DT', 'RIT_CYCLE', 'ROUTE', 'ASN_NO', 'CASE_NO'],
     [[i + 1, '50221', '1', c, l, p, OD, d, co, '0000001', q, po, m, '0001', '2026-10-16', '1', 'SD01', 'ASN-50221-261016-001', f'C-{c:04d}']
      for i, (c, l, p, d, co, q, po, m) in enumerate((
          (1, 1, 'PART-X', VN, 'CO-14101', 6, 'T0409001', '3126035901'), (2, 1, 'PART-X', VN, 'CO-14101', 4, 'T0409001', '3126035901'),
          (2, 2, 'PART-X', VN, 'CO-14102', 2, 'T0409001', '3126035901'), (3, 1, 'PART-X', VN, 'CO-14102', 2, 'T0409002', '3126035902'),
          (3, 2, 'PART-X', VN, 'CO-14103', 4, 'T0409002', '3126035902'), (4, 1, 'PART-X', TH, 'CO-14104', 6, 'T0409002', '3126035902'),
          (5, 1, 'PART-Y', PH, 'CO-14105', 6, 'T0409003', '3126035903')))]),
    ('TB_R_PRA_DAILY_ORDER_MAPPED', '[Create ASN] adds the mapped qty per PO line (released by XD11 only for rows without ASN_NO)',
     ['PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'PART_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'ORDER_QTY', 'MAPPED_QTY'],
     [['T0409001', '3126035901', '001', 'PART-X', '50221', '1', 12, 12], ['T0409002', '3126035902', '001', 'PART-X', '50221', '1', 12, 12],
      ['T0409003', '3126035903', '001', 'PART-Y', '50221', '1', 6, 6]]),
    ('TB_R_DAILY_ORDER_MANIFEST', 'Submit (XD10 5.7): one row per Pra manifest of the cases, same ASN_NO (SUB_MANIFEST_NO dummy, numbering as existing)',
     ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'ASN_NO', 'ASN_DATE', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'PO_NO', 'CROSS_DOCK_FLAG', 'DOCK_CD', 'TOTAL_ITEM', 'TOTAL_QTY',
      'DELIVERY_DT_ORI', 'SUB_ROUTE_CD', 'SUB_ROUTE_SEQ', 'STATUS'],
     [['3126035901A1', '3126035901', 'ASN-50221-261016-001', '2026-10-16 09:30', '50221', '1', 'T0409001', 'X', 'S1', 1, 12, '2026-10-16', 'SD01', '1', 'Created'],
      ['3126035902A1', '3126035902', 'ASN-50221-261016-001', '2026-10-16 09:30', '50221', '1', 'T0409002', 'X', 'S1', 1, 12, '2026-10-16', 'SD01', '1', 'Created'],
      ['3126035903A1', '3126035903', 'ASN-50221-261016-001', '2026-10-16 09:30', '50221', '1', 'T0409003', 'X', 'S1', 1, 6, '2026-10-16', 'SD01', '1', 'Created']]),
    ('TB_R_DAILY_ORDER_PART', 'Submit (XD10 5.7): one row per manifest item and case',
     ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CASE_NO', 'PO_NO', 'PO_ITEM', 'ASN_NO', 'PART_NO', 'PART_NAME', 'PO_QTY', 'DELIVERY_QTY'],
     [['3126035901A1', '3126035901', '0001', 'C-0001', 'T0409001', '0001', 'ASN-50221-261016-001', 'PART-X', 'DUMMY PART X', 12, 6],
      ['3126035901A1', '3126035901', '0001', 'C-0002', 'T0409001', '0001', 'ASN-50221-261016-001', 'PART-X', 'DUMMY PART X', 12, 6],
      ['3126035902A1', '3126035902', '0001', 'C-0003', 'T0409002', '0001', 'ASN-50221-261016-001', 'PART-X', 'DUMMY PART X', 12, 6],
      ['3126035902A1', '3126035902', '0001', 'C-0004', 'T0409002', '0001', 'ASN-50221-261016-001', 'PART-X', 'DUMMY PART X', 12, 6],
      ['3126035903A1', '3126035903', '0001', 'C-0005', 'T0409003', '0001', 'ASN-50221-261016-001', 'PART-Y', 'DUMMY PART Y', 6, 6]]),
    ('TB_R_CASE_LABEL_LAST_SEQ', 'Submit (XD10 5.7): new last sequence of supplier 50221 plant 1 (5 case labels and 1 ASN number generated)',
     ['SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ', 'CHANGED_DT'],
     [['50221', '1', '005', '001', '2026-10-16 09:30']]),
    ('TB_M_PART_MASTER', 'Existing part master (only PART_NAME is used)',
     ['PART_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'DOCK_CD', 'VALID_FROM', 'PART_NAME'],
     [['PART-X', '50221', '1', 'S1', '2026-01-01', 'DUMMY PART X'], ['PART-Y', '50221', '1', 'S1', '2026-01-01', 'DUMMY PART Y'],
      ['PART-Z', '50221', '1', 'S1', '2026-01-01', 'DUMMY PART Z']]),
    ('TB_R_CROSSDOCK_CANCEL_RESULT', 'XD11 on 16-Oct 27:30: one row per cancelled row (status 2) with the figures of its line',
     ['CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD', 'SERIAL_NO', 'PART_NO', 'CANCEL_QTY', 'VALID_QTY', 'QTY_IN_ASN', 'RELEASED_QTY', 'CONFLICT_QTY',
      'HOLD_FLAG', 'RESULT', 'ASN_NO', 'MESSAGE'],
     [['CO-14110', '2026-10-15', PH, '0000002', 'PART-Y', 6, 6, 0, 0, 0, 'N', 'CANCELLED', None, 'Partial cancel, no open mapping'],
      ['CO-14103', OD, VN, '0000001', 'PART-X', 4, 0, 4, 0, 4, 'N', 'CONFLICT', 'ASN-50221-261016-001',
       'Qty already in ASN cancelled (SOP not followed): handle case C-0003 at receiving']]),
]
