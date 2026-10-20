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

# simulation data: sim_data.py (one sheet per scenario)
