"""Decisions of 21-Oct-26: XD09 pre-mapping in the receiving scan order of G-System and ASN options (blocks of supplier cases).
- Scan order of the H0253 lines = G-System allocation order with Allocation Priority = Customer Order Date: Allocation Priority, Customer Code,
  Customer Order No, Customer Order Date, Customer Order Time,
  Destination Code, Detailed Item No, Serial No; per Part Number + Customer Order Date (unit), units by Customer Order Date ascending (way B).
- The pcs are cut into supplier cases of PCS_CASE pcs in this order: a case can hold several lines and destinations. At receiving the scan
  allocates the pcs in this fixed order and the warehouse packs 1 case = 1 destination, so an ASN may only stop after a case where the
  cumulative qty of every destination is a multiple of PCS_CASE (valid cut). The cases up to a valid cut form a block (ASN option).
- A block is Ready when it and every earlier block have a PO: the supplier sends the first n Ready blocks, never skipping a block.
- A line can be sent over several ASNs: PO_MAPPED_FLAG = 'Y' only when the whole line is in TB_R_INSTRUCTION; XD09 takes the open qty.
Run after apply_2010.py (build_all_v2.sh)."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scan_pack import pack  # noqa: E402

H, I, PRA_M, PRA_P = 'TB_R_H0253_ORDER_CONTROL_PRE', 'TB_R_INSTRUCTION', 'TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_PRA_DAILY_ORDER_PART'
FLAG_RULE = f"manifests with {PRA_M}.CROSS_DOCK_FLAG = 'X'; their part data from {PRA_P} (join MANIFEST_NO)"
SCAN = ("1) Allocation Priority (= Customer Order Date), 2) Customer Code, 3) Customer Order No, 4) Customer Order Date, 5) Customer Order Time, 6) Destination Code, 7) Detailed Item No, 8) Serial No (order of G-System allocation)")
QUERY = """WITH MAPPED AS (SELECT CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO, SUM(QTY) AS MAPPED_QTY
                FROM TB_R_INSTRUCTION
                GROUP BY CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO),
OPEN_LINE AS (SELECT H.*, H.ORDER_DT AS ALLOCATION_PRIORITY,
                     H.ORDER_STATUS_QTY - COALESCE(M.MAPPED_QTY, 0) AS OPEN_ORDER_QTY
              FROM TB_R_H0253_ORDER_CONTROL_PRE H
              LEFT JOIN MAPPED M ON M.CUSTOMER_CD = H.CUSTOMER_CD AND M.CUSTOMER_ORDER_NO = H.CUSTOMER_ORDER_NO
                   AND M.ORDER_DT = H.ORDER_DT AND M.DESTINATION_CD = H.DESTINATION_CD
                   AND M.DETAILED_ITEM_NO = H.DETAILED_ITEM_NO AND M.SERIAL_NO = H.SERIAL_NO
              WHERE H.ORDER_STATUS = '7' AND H.HOLD_FLAG = 'N' AND H.PO_MAPPED_FLAG = 'N')
SELECT ROW_NUMBER() OVER (PARTITION BY SHIPPING_PART_NO, ORDER_DT
                          ORDER BY ALLOCATION_PRIORITY, CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME,
                                   DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO) AS SORT_SEQ,
       SHIPPING_PART_NO, ALLOCATION_PRIORITY, CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME,
       DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO, ORDER_STATUS_QTY, OPEN_ORDER_QTY
FROM OPEN_LINE
WHERE OPEN_ORDER_QTY > 0
ORDER BY SHIPPING_PART_NO, ALLOCATION_PRIORITY, CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME,
         DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO"""
OPEN = f"open qty = ORDER_STATUS_QTY - qty of the line already in {I}"


def load(fid):
    return json.load(open(os.path.join(HERE, f"{fid}_spec.json"), encoding='utf-8'))


def save(fid, s):
    json.dump(s, open(os.path.join(HERE, f"{fid}_spec.json"), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def col(name, typ, desc, pk='', null='N'):
    return [name, typ, pk, null, desc]


TEMP_COLS = [
    col('INSTRUCTION_ID', 'BIGINT', 'Running number within the session', 'Y'),
    col('SORT_SEQ', 'NUMBER(6)', 'Scan order of the line within the unit (refer 4.1)'),
    col('CUSTOMER_CD', 'VARCHAR(7)', 'H0253.CUSTOMER_CD (scan key 1)'),
    col('CUSTOMER_ORDER_NO', 'VARCHAR(8)', 'H0253.CUSTOMER_ORDER_NO (scan key 2)'),
    col('ORDER_DT', 'DATE', 'Customer Order Date (H0253.ORDER_DT; unit and scan key 3)'),
    col('ORDER_TIME', 'VARCHAR(6)', 'H0253.ORDER_TIME (scan key 4)'),
    col('DESTINATION_CD', 'VARCHAR(7)', 'H0253.DESTINATION_CD (scan key 5)'),
    col('DETAILED_ITEM_NO', 'VARCHAR(4)', 'H0253.DETAILED_ITEM_NO (scan key 6)'),
    col('SERIAL_NO', 'VARCHAR(7)', 'H0253.SERIAL_NO (scan key 7)'),
    col('PART_NO', 'VARCHAR(15)', 'Order part number (H0253.SHIPPING_PART_NO)'),
    col('ORDER_STATUS', 'VARCHAR(1)', "H0253.ORDER_STATUS ('7' Cross Dock)"),
    col('CUST_ORDER_QTY', 'NUMBER(8)', 'Order status qty of the customer order line (H0253.ORDER_STATUS_QTY)'),
    col('OPEN_ORDER_QTY', 'NUMBER(8)', f'Qty of the line not yet in {I} (sent or in an open Case List)'),
    col('ASSIGNED_QTY', 'NUMBER(8)', 'Qty of this slice (line x PO x supplier case)'),
    col('PO_NO', 'VARCHAR(TBD)', 'Supplier PO number (Pra Daily Order Manifest); NULL while not assigned', null='Y'),
    col('MANIFEST_NO', 'VARCHAR(TBD)', 'Manifest number', null='Y'),
    col('MANIFEST_ITEM', 'VARCHAR(TBD)', 'Manifest item number (Pra Daily Order Part)', null='Y'),
    col('PO_DT', 'DATE', 'Order date of the PO (PO Date)', null='Y'),
    col('ORDER_QTY', 'NUMBER(TBD)', 'Order qty of the PO part', null='Y'),
    col('SUPPLIER_CD', 'VARCHAR(TBD)', 'Supplier code', null='Y'),
    col('SUPPLIER_PLANT', 'VARCHAR(TBD)', 'Supplier plant', null='Y'),
    col('SUB_SUPPLIER_CD', 'VARCHAR(TBD)', 'Sub supplier code', null='Y'),
    col('SUB_SUPPLIER_PLANT', 'VARCHAR(TBD)', 'Sub supplier plant', null='Y'),
    col('ORDER_TYPE', 'VARCHAR(TBD)', 'Order type of the PO', null='Y'),
    col('DOCK_CD', 'VARCHAR(TBD)', 'Dock code', null='Y'),
    col('ETD_ORI', 'DATE', 'Original ETD', null='Y'),
    col('PCS_CASE', 'NUMBER(4)', 'Pcs per case of the part (TB_M_PART_CANDIDATE.PCS_CASE)'),
    col('CASE_SEQ', 'NUMBER(4)', 'Supplier case of the slice within the unit (PCS_CASE pcs in scan order)'),
    col('LINE_SEQ', 'NUMBER(4)', 'Sequence of the slice within the case'),
    col('CUM_DEST_QTY', 'NUMBER(8)', 'Cumulative qty of the destination within the unit up to this slice'),
    col('SEQ_QTY', 'NUMBER(4)', 'Fill of the warehouse case (1 case = 1 destination) of the destination after this slice: 1..PCS_CASE, starts again after PCS_CASE'),
    col('CUT_FLAG', 'VARCHAR(1)', "'Y' on the last slice of a case after which the ASN may stop (every destination a multiple of PCS_CASE)"),
    col('GROUP_SEQ', 'NUMBER(4)', 'Block (ASN option) of the slice: the cases up to and including a valid cut'),
    col('CROSSDOCK_STATUS', 'VARCHAR(1)', "Status of the block: '6' Ready (the block and every earlier block have a PO) / '7' Not Ready"),
]
TEMP_DESC = ("Temporary table of one Search run (session): the open qty of the customer order lines (H0253, order status 7, Hold Flag N) "
             "in scan order, pre-mapped to the supplier POs (Pra Daily Order) and cut into supplier cases and blocks. One row per line x PO x "
             "supplier case; PO_NO NULL for the qty still without a PO. Columns proposed.")

# ---- sample of the user (21-Oct): date 1 = 14-Oct (customer order), PO p1 released 15-Oct, p2 released 16-Oct
CUST = {'V01': 'CUST-A', 'T01': 'CUST-B', 'V02': 'CUST-C'}
LINES = [dict(CUSTOMER_CD=CUST[co], CUSTOMER_ORDER_NO=co, ORDER_DT='14-Oct-2026', ORDER_TIME='080000', DESTINATION_CD=d, DETAILED_ITEM_NO='0001',
              SERIAL_NO='0000001', PART_NO='PART-A', QTY=q) for co, d, q in (('V01', 'VN', 10), ('T01', 'TH', 6), ('V02', 'VN', 14))]
SAMPLE_COLS = ['Sort Seq', 'Customer Code', 'Cust Order No', 'Dest', 'Order Qty', 'PO No', 'Assigned Qty', 'Case', 'Cum Dest Qty', 'Seq Qty', 'Cut', 'Block',
               'Status']
SAMPLE_W = [8, 12, 12, 7, 9, 8, 11, 7, 12, 6, 7, 8]


def sample_rows(pos):
    return [[s['SORT_SEQ'], s['CUSTOMER_CD'], s['CUSTOMER_ORDER_NO'], s['DESTINATION_CD'], s['QTY'], s['PO_NO'] or '(none)', s['ASSIGNED_QTY'],
             s['CASE_SEQ'], s['CUM_DEST_QTY'], s['SEQ_QTY'], s['CUT_FLAG'], s['GROUP_SEQ'], s['CROSSDOCK_STATUS']] for s in pack(LINES, pos, 6)]


SAMPLE = {
    'title': 'Sample Input',
    'heading': 'Sample pre-mapping - scan order, supplier cases and ASN options (blocks)',
    'intro': [
        "Part PART-A, 6 pcs/case, Customer Order Date 14-Oct-2026 (one unit). H0253 lines (order status 7, Hold Flag N): V01 VN 10, T01 TH 6, "
        "V02 VN 14 (30 pcs). Dummy customer codes CUST-A / B / C give the scan order V01, T01, V02.",
        f"PO parts ({FLAG_RULE}): p1 24 pcs (released 15-Oct), p2 6 pcs (released 16-Oct).",
        "Cut check after each case: cumulative VN / TH = case 1: 6 / 0 valid; case 2: 10 / 2 not valid (VN short 2, TH short 4); case 3: 12 / 6 valid; "
        "case 4: 18 / 6 valid; case 5: 24 / 6 valid. Blocks: 1 = case 1; 2 = cases 2-3; 3 = case 4; 4 = case 5."],
    'sections': [
        {'title': 'A. [Search] on 15-Oct: only p1 (24 pcs) is released', 'columns': SAMPLE_COLS, 'widths': SAMPLE_W,
         'rows': sample_rows([['p1', 'M-0001', '0001', 24]])},
        {'title': 'B. ASN options on 15-Oct (the supplier chooses one; blocks are taken in order)', 'columns': ['Option', 'Blocks', 'Cases', 'Pcs', 'Scan order at receiving'],
         'widths': [8, 10, 10, 8, 70],
         'rows': [['1', '1', '1', 6, 'VN 6 (V01)'],
                  ['2', '1-2', '1-3', 18, 'VN 6, VN 4, TH 2 | TH 4, VN 2: VN 12 and TH 6 close their cases'],
                  ['3', '1-3', '1-4', 24, 'Option 2 + VN 6 (V02); p1 used up'],
                  ['4', '1-4', '1-5', 30, 'Not on 15-Oct: block 4 has no PO (status 7); possible from 16-Oct when p2 is released']]},
        {'title': 'C. [Search] on 16-Oct after the supplier sent option 3 on 15-Oct: open qty V02 6, p2 released',
         'columns': SAMPLE_COLS, 'widths': SAMPLE_W,
         'rows': [[r[0], r[1], r[2], r[3], 6, *r[5:]] for r in
                  [[s['SORT_SEQ'], s['CUSTOMER_CD'], s['CUSTOMER_ORDER_NO'], s['DESTINATION_CD'], s['QTY'], s['PO_NO'], s['ASSIGNED_QTY'], s['CASE_SEQ'],
                    s['CUM_DEST_QTY'], s['SEQ_QTY'], s['CUT_FLAG'], s['GROUP_SEQ'], s['CROSSDOCK_STATUS']]
                   for s in pack([dict(LINES[2], QTY=6)], [['p2', 'M-0002', '0001', 6]], 6)]]},
        {'title': 'D. Result on the screen', 'columns': ['No', 'Scenario', 'Expected result'], 'widths': [6, 50, 70],
         'rows': [['N1', 'A: blocks 1-3 Ready, block 4 Not Ready', 'PART-A 14-Oct: Case Qty 5, PO Readiness 4, ASN Status Partially Ready; ASN options 1 / 3 / 4 cases.'],
                  ['N2', 'Supplier sends option 1 only', 'Next [Search]: open qty V01 4, T01 6, V02 14 is cut again from case 1 in the same order (same cases).'],
                  ['N3', 'Block 2 without PO, block 3 with PO', 'Block 3 is Not Ready too: blocks are never skipped (scan order is fixed).'],
                  ['N4', 'C: all open qty pre-mapped', 'ASN Status Ready; one option (1 case).'],
                  ['N5', 'A destination is on hold (Hold Flag Y)', 'Its lines are not taken; the scan order and the blocks are computed without them.'],
                  ['E1', 'Database error', 'Nothing is kept in the temporary table; message on the screen, Log FAILED.']]},
    ]}


# ---- XD10 case check boxes (decided 21-Oct): example of the user, all cases with PO (p1 24 + p2 6)
_CASES = pack(LINES, [['p1', 'M-0001', '0001', 24], ['p2', 'M-0002', '0001', 6]], 6)


def _case_rows():
    rows = []
    for c in sorted({s['CASE_SEQ'] for s in _CASES}):
        sl = [s for s in _CASES if s['CASE_SEQ'] == c]
        rows.append([c, sum(s['ASSIGNED_QTY'] for s in sl), ' + '.join(f"{s['DESTINATION_CD']} {s['ASSIGNED_QTY']} ({s['CUSTOMER_ORDER_NO']})" for s in sl),
                     ', '.join(f"{po} {sum(s['ASSIGNED_QTY'] for s in sl if s['PO_NO'] == po)}" for po in dict.fromkeys(s['PO_NO'] for s in sl)),
                     sl[-1]['CUT_FLAG'], sl[-1]['CROSSDOCK_STATUS']])
    return rows


XD10_CASE_SECTIONS = [
    {'title': 'H. Case selection (decided 21-Oct): PART-A 14-Oct, all cases with PO (p1 24 + p2 6); one check box per supplier case',
     'columns': ['Case', 'Qty', 'Content (scan order)', 'PO', 'Can end here (CUT_FLAG)', 'PO Status'], 'widths': [6, 6, 34, 18, 20, 10],
     'rows': _case_rows()},
    {'title': 'I. Check box scenarios (cumulative VN / TH after the last ticked case)', 'columns': ['No', 'User action', 'Ticked cases', 'Result'],
     'widths': [6, 34, 14, 66],
     'rows': [['C1', 'Tick case 1', '1', 'VN 6 / TH 0: valid end; ASN 6 pcs.'],
              ['C2', 'Tick case 2 (or cases 1 and 2)', '1-3', 'Case 2 ends with VN 10 / TH 2 (CUT N): cases 1-2 alone are not possible; case 3 is ticked too '
               '(message no. 10) -> VN 12 / TH 6; ASN 18 pcs.'],
              ['C3', 'Tick case 3', '1-3', 'Cases 1-2 are ticked too; ASN 18 pcs.'],
              ['C4', 'Tick case 4', '1-4', 'VN 18 / TH 6: valid end; ASN 24 pcs.'],
              ['C5', 'Tick case 5 (or the unit check box)', '1-5', 'All cases; ASN 30 pcs.'],
              ['C6', 'From 1-4, untick case 3', '1', 'Cases 3-4 unticked; case 2 cannot be the last case, so it is unticked too (back to case 1).'],
              ['C7', 'p2 not released yet (case 5 without PO)', '1 / 1-3 / 1-4', 'Case 5 disabled (tooltip message no. 2); the user can end on case 1, 3 or 4.']]},
]


def xd09():
    s = load('XD09')
    g = s['general']
    g['objective'][0] = (f"To get the open qty of the crossdock customer orders (H0253, order status 7, Hold Flag N) in the receiving scan order of G-System, "
                         f"pre-map them to the crossdock supplier PO parts (Pra Daily Order: {FLAG_RULE}), cut them into supplier cases and blocks "
                         "(ASN options) into the temporary table #TEMP_INSTRUCTION.")
    g['objective'][1] = ("To give ASN Crossdock Creation (XD10) the delivery plan per Part Number + Customer Order Date with Case Qty, PO Readiness (case), "
                         "the ASN options (blocks that can be sent) and the status Ready / Partially Ready / Not Ready.")
    g['operation_flow']['flow']['nodes'][3]['label'] = 'Pre-map in scan order, cut cases and blocks'
    g['operation_flow']['flow']['nodes'][4]['label'] = 'Fill #TEMP_INSTRUCTION, block status'
    g['inputs'][1]['description'] = f"ORDER_STATUS = '7', HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'; {OPEN}; latest data (replicated by XD08)"
    g['inputs'] += [{'name': I, 'type': 'DB', 'description': 'Qty of each line already mapped (open Case List or submitted ASN)'},
                    {'name': 'TB_M_PART_CANDIDATE', 'type': 'DB', 'description': 'PCS_CASE of the part'}]
    g['outputs'][0]['description'] = 'One row per line x PO x supplier case; PO_NO NULL for the qty still without a PO'
    g['outputs'][1]['description'] = 'Delivery plan: Customer Order Date, Part Number, Case Qty, PO Readiness (case), ASN options, ASN Status'
    for t in g['extra_tables']:
        if t['title'] == 'Grouping Keys':
            t['rows'] = ['PART_NO + ORDER_DT (unit; units by ORDER_DT ascending)', 'Scan order: ORDER_DT (Allocation Priority), CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME, '
                         'DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO', 'CASE_SEQ (PCS_CASE pcs in scan order)', 'GROUP_SEQ (block up to a valid cut)']
    ff = s['func_flow']
    ff['flow']['nodes'][5]['label'] = 'Pre-map in scan order, cut cases and blocks'
    ff['flow']['nodes'][7]['label'] = 'Block status and return to screen'
    ff['steps'][1] = {'text': f'Get the customer order lines from {H}:', 'children': [
        f"ORDER_STATUS = '7' (Cross Dock), HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'; latest data; {OPEN} (> 0). Status '2' (cancel) is not taken.",
        "Get: Customer Code, Customer Order No, Order Date, Order Time, Destination Code, Detailed Item No, Serial No, Part Number, Order Status Qty; "
        "Pcs/Case of the part from TB_M_PART_CANDIDATE."]}
    ff['steps'][3] = {'text': 'Per unit (Part Number + Customer Order Date, oldest date first), pre-map in scan order (see 4.1 and 4.2) and insert the result in #TEMP_INSTRUCTION.', 'children': [
        f"Lines in scan order: {SCAN}.",
        "Each PO qty (PO_DT ascending) goes to the open qty in this order; a line may be split over several POs.",
        "The pcs are cut into supplier cases of PCS_CASE pcs in this order (a case can hold several lines and destinations); each slice line x PO x case is one row."]}
    ff['steps'][4] = {'text': 'Mark the valid cuts, number the blocks, set the status of each block and return the delivery plan to XD10 (see 4.3).', 'children': [
        'Error: clear the temporary table, show the error on the screen and record the Log (FAILED).']}
    m = s['data_map']['blocks'][0]
    m['source']['table'] = f'{H} + {PRA_M} / {PRA_P} + {I} + TB_M_PART_CANDIDATE'
    m['destination']['description'] = 'Line x PO x supplier case pre-mapping (temporary)'
    keep = {x['dest_field']: x for x in m['mappings']}
    new = {'SORT_SEQ': {'dest_field': 'SORT_SEQ', 'description': 'Scan order of the line in the unit'},
           'ORDER_TIME': {'source_field': 'H0253.ORDER_TIME', 'dest_field': 'ORDER_TIME'},
           'OPEN_ORDER_QTY': {'dest_field': 'OPEN_ORDER_QTY', 'description': f'H0253.ORDER_STATUS_QTY - SUM({I}.QTY) of the line'},
           'ASSIGNED_QTY': {'dest_field': 'ASSIGNED_QTY', 'description': 'Qty of the slice (line x PO x case)'},
           'PCS_CASE': {'source_field': 'TB_M_PART_CANDIDATE.PCS_CASE', 'dest_field': 'PCS_CASE'},
           'CASE_SEQ': {'dest_field': 'CASE_SEQ', 'description': 'Supplier case: running number every PCS_CASE pcs in scan order'},
           'LINE_SEQ': {'dest_field': 'LINE_SEQ', 'description': 'Sequence of the slice in the case'},
           'CUM_DEST_QTY': {'dest_field': 'CUM_DEST_QTY', 'description': 'Cumulative qty of the destination in the unit'},
           'SEQ_QTY': {'dest_field': 'SEQ_QTY', 'description': 'MOD(CUM_DEST_QTY - 1, PCS_CASE) + 1: fill of the warehouse case of the destination (refer 4.3)'},
           'CUT_FLAG': {'dest_field': 'CUT_FLAG', 'description': "'Y' when, after this case, every destination is a multiple of PCS_CASE (refer 4.3)"},
           'GROUP_SEQ': {'dest_field': 'GROUP_SEQ', 'description': 'Block number: +1 after each valid cut'},
           'CROSSDOCK_STATUS': {'dest_field': 'CROSSDOCK_STATUS', 'description': "'6' Ready when the block and every earlier block have no PO_NO NULL; else '7' (refer 4.3)"}}
    m['mappings'] = [new.get(c[0]) or keep[c[0]] for c in TEMP_COLS]
    s['func_desc'] = [
        {'type': 'text', 'level': 0, 'text': 'This function builds the delivery plan of ASN Crossdock Creation on demand. It only pre-maps: nothing permanent is changed; '
                                            'the real mapping is done by [Create ASN] (XD10).'},
        {'type': 'heading', 'text': '4.1 Scan Order'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            "At receiving, the scan allocates the delivered pcs to the customer orders in a fixed order that cannot be changed. XD09 uses the same order "
            f"(decided 21-Oct): {SCAN}.",
            "The order is applied per unit = Part Number + Customer Order Date (way B): the units of a part are processed by Customer Order Date ascending, "
            "so the POs go to the oldest date first.",
            f"The scan keys are the primary key of {H} (same columns, same order), so the replicate keeps the rows in scan order. The PK order is "
            "global (all parts, dates and statuses) and a read without ORDER BY has no guaranteed order: XD09 filters the unit and reads it with "
            "ORDER BY SHIPPING_PART_NO, Allocation Priority (ORDER_DT), then the PK columns (query: Appendix). SORT_SEQ = ROW_NUMBER() in this order per unit (it can be derived again at any time).",
            f"Lines with HOLD_FLAG = 'Y' are not taken. Only the open qty of a line is taken ({OPEN}): a line can be sent over several ASNs; "
            "PO_MAPPED_FLAG becomes 'Y' only when the whole line is in TB_R_INSTRUCTION."]},
        {'type': 'heading', 'text': '4.2 PO and Supplier Cases'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            "PO parts by PO_DT ascending; each PO qty goes to the open qty in scan order; a line may be split over several POs; qty without PO = PO_NO NULL.",
            "The pcs of the unit are cut into supplier cases of PCS_CASE pcs in scan order (e.g. 6 pcs/case: case 1 = V01 6; case 2 = V01 4 + T01 2). "
            "A supplier case can hold several lines and destinations. G-System releases each destination in multiples of PCS_CASE, so every case is full.",
            "A PO remainder without open line stays open for later customer orders."]},
        {'type': 'column_break'},
        {'type': 'heading', 'text': '4.3 Blocks (ASN Options) and Status'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            "In the warehouse the scanned pcs are packed 1 case = 1 destination (max PCS_CASE pcs). An ASN may therefore stop only after a case where the "
            "cumulative qty of every destination of the unit is a multiple of PCS_CASE (valid cut, CUT_FLAG 'Y'). SEQ_QTY = fill of the warehouse case of the destination (1..PCS_CASE, starts again after PCS_CASE): the cut is valid when the last SEQ_QTY of every destination = PCS_CASE. Example: after case 2 VN 10 / TH 2 is "
            "not valid (VN short 2, TH short 4); after case 3 VN 12 / TH 6 is valid.",
            "Block = the cases after the previous valid cut up to the next valid cut (GROUP_SEQ). A block is never split.",
            "CROSSDOCK_STATUS of a block: '6' Ready when the block and every earlier block are fully pre-mapped to a PO; '7' Not Ready otherwise. "
            "A later block with PO stays '7' while an earlier block has no PO (blocks are never skipped).",
            "ASN options of the unit = the first 1..n Ready blocks. Unit status on XD10: Ready (all blocks '6'), Partially Ready (first block '6', "
            "a later block '7'), Not Ready (first block '7'). Units without any pre-mapped case are not listed.",
            "The mapped qty per PO is kept in TB_R_PRA_DAILY_ORDER_MAPPED; it is updated by [Create ASN] on XD10, not by this function. "
            "Nothing is saved by this function: #TEMP_INSTRUCTION is the pre-mapping only."]}]
    s['sample_sheet'] = SAMPLE
    s['appendix'] = [{'type': 'text', 'level': 0, 'text': 'Sample pre-mapping: see sheet Sample Input.'},
                     {'type': 'heading', 'text': 'Query: H0253 lines in scan order (Allocation Priority = Customer Order Date)'},
                     *[{'type': 'text', 'level': 0, 'text': ln} for ln in QUERY.split('\n')]]
    for t in s['tables']:
        if t['name'] == '#TEMP_INSTRUCTION':
            t['description'], t['columns'] = TEMP_DESC, TEMP_COLS
    save('XD09', s)


def xd10():
    s = load('XD10')
    g = s['general']
    g['objective'][1] = ("To display the delivery plan per Part Number + Customer Order Date with the supplier cases in receiving scan order (Case Qty, "
                         "PO Readiness, ASN options, ASN Status Ready / Partially Ready / Not Ready). Units fully Created or without any pre-mapped case are not listed.")
    g['objective'][3] = ("To tick the supplier cases to send (check box per case, from case 1 up to a valid cut) of one Supplier Code + Supplier Plant, map them to their POs "
                         "(TB_R_INSTRUCTION), review the cases, download the case labels and submit the ASN.")
    g['buttons'][5]['function'] = ("Check that the selected units are of one supplier and not held, map the chosen blocks to their POs (insert TB_R_INSTRUCTION) "
                                   "and open the Case List sub screen.")
    g['screen_mode_remarks'][0] = ('1) Each unit row shows its supplier case rows in scan order (XD09). The check box of a case is enabled only when the case '
                                   'and every earlier case have a PO (Ready, message no. 2 as tooltip otherwise).')
    g['screen_mode_remarks'][1] = ("2) The ticked cases of a unit always start at case 1 and must end on a case with CUT_FLAG Y (every destination closes its "
                                   "warehouse case). Ticking case n also ticks the earlier cases and the later cases up to the next CUT_FLAG Y (message no. 10); "
                                   "unticking case n unticks it, the later cases and the earlier cases back to the previous CUT_FLAG Y. The unit check box ticks "
                                   "all Ready cases. Units of different Customer Order Dates and Part Numbers can be ticked together.")
    g['screen_mode_remarks'][2] = ("3) The supplier sees the unit rows and their case rows (with check box); the destination detail, customer orders and "
                                   "Hold / Release are shown to the D/S team only.")
    for m in g['screen_modes']:
        for sec in m['sections']:
            if sec['description'].startswith('Units of the login supplier'):
                sec['description'] = ('Units of the login supplier (Supplier Code + Plant) only; unit rows with their supplier case rows (check box per case); '
                                      'Part Number / Status filters')
    nodes = s['screen_flow'][1]['flow']['nodes']
    nodes[3]['label'] = 'First block Ready? (blocks in scan order)'
    nodes[5]['label'] = 'Tick cases (from case 1 up to a CUT_FLAG Y), Create ASN: insert TB_R_INSTRUCTION'
    it = s['items']
    it[9]['validation'] = 'Enabled when the first block of the unit is Ready'
    it[13]['description'] = ('Number of supplier cases of the unit: open qty / pcs/case, cut in scan order (e.g. 30 pcs, 6 pcs/case = 5 cases); '
                             'a case can hold several destinations.')
    it[15]['description'] = ("Ready (all blocks '6', green) / Partially Ready (first block '6', a later block '7', amber) / Not Ready (first block '7', "
                             "row highlighted) / On Hold (D/S only). Refer 5.2.")
    it[9]['description'] = 'Ticks / unticks all Ready cases of the unit (up to the last Ready CUT_FLAG Y; partly ticked when only some cases are ticked). Refer Screen Mode remark 2).'
    def item(name, src, field, typ, io, control, fmt, val, desc, just='Left', init='-', req='N'):
        return {"name": name, "source": src, "field": field, "type": typ, "len": "-", "io": io, "control": control, "justified": just,
                "initial": init, "required": req, "format": fmt, "validation": val, "description": desc}
    it[17:17] = [
        {"group": "<Supplier Cases of a Unit (scan order)>"},
        item('Select case (check box)', 'Key-in', '-', 'Char', 'I', 'CheckBox', '-', 'Enabled only when the case and every earlier case have a PO',
             'One check box per supplier case. The selection always starts at case 1 and ends on a case with CUT_FLAG Y: ticking case n also ticks '
             'the earlier cases and the later cases up to the next CUT_FLAG Y (message no. 10, e.g. tick case 2 -> cases 1-3); unticking case n '
             'unticks the later cases and goes back to the previous CUT_FLAG Y. Refer 5.4.', just='Center', init='<unchecked>'),
        item('Case', '#TEMP_INSTRUCTION', 'CASE_SEQ', 'Number', 'O', 'Label', 'Z9', '-', 'Supplier case number in scan order (PCS_CASE pcs).', just='Right'),
        item('Qty (pcs)', '#TEMP_INSTRUCTION', 'ASSIGNED_QTY', 'Number', 'O', 'Label', 'ZZZ9', '-', 'Pcs of the case (= PCS_CASE).', just='Right'),
        item('Content', '#TEMP_INSTRUCTION', 'DESTINATION_CD / CUSTOMER_ORDER_NO / ASSIGNED_QTY', 'Char', 'O', 'Label', '-', '-',
             'Slices of the case in scan order, e.g. VN 4 (V01) + TH 2 (T01).'),
        item('Can end here', '#TEMP_INSTRUCTION', 'CUT_FLAG', 'Char', 'O', 'Label', 'Y / N', '-',
             "Y: the ASN may stop after this case (every destination a multiple of PCS_CASE). N: the next cases up to a Y are ticked together."),
        item('PO Status', '#TEMP_INSTRUCTION', 'CROSSDOCK_STATUS', 'Char', 'O', 'Label', '-', '-',
             "'6' Ready (green) / '7' Not Ready (amber): the case or an earlier case has no PO yet."),
    ]
    for x in it:
        if x.get('name') == 'Part Number' and x.get('source') == I:
            x['description'] = 'Supplier case of PCS_CASE pcs in scan order; a case can hold several destinations.'
    b1 = s['data_map']['blocks'][1]
    b1['source'] = '#TEMP_INSTRUCTION (chosen blocks)'
    b1['destination']['description'] = '[Create ASN]: the lines of the chosen blocks'
    b1['destination']['keys'][0]['value'] = 'Lines of the chosen blocks'
    b1['mappings'][0]['description'] = (f"'Y' when the whole line is in {I} after this creation; stays 'N' when part of the line is in a later block; "
                                        "back to 'N' on Back / Cancel")
    for k in (2, 3):
        s['data_map']['blocks'][k]['source'] = '#TEMP_INSTRUCTION (chosen blocks)'
    s['data_map']['blocks'][2]['destination']['description'] = '[Create ASN]: one row per PO part used by the chosen blocks (insert when none yet)'
    s['data_map']['blocks'][2]['mappings'][0]['description'] = '+ ASSIGNED_QTY of the chosen blocks; - again on Back / Cancel'
    s['data_map']['blocks'][3]['mappings'][0]['description'] = 'Case sequence: selected unit, then CASE_SEQ of XD09 (scan order)'
    s['data_map']['blocks'][3]['mappings'][1]['description'] = 'LINE_SEQ of XD09 (sequence within the case)'
    op = s['operation']
    op[1]['items'][1] = ("[Search] runs XD09 Mapping Customer Order and PO Batch (UISS XD09): the open qty of the H0253 customer orders with order status 7 "
                         "and Hold Flag N, in the receiving scan order of G-System per Part Number + Customer Order Date, pre-mapped to the PO parts of the "
                         "Pra Daily Order (PO date order), cut into supplier cases and blocks in the temporary table #TEMP_INSTRUCTION (pre-mapping only; "
                         "nothing is saved yet). Supplier: units of the login Supplier Code + Plant; D/S team: all suppliers.")
    op[1]['items'][2] = ("The delivery plan shows one row per Part Number + Customer Order Date, sorted Ready, Partially Ready, Not Ready, then Part Number "
                         "ascending. Units without any pre-mapped case and units fully Created are not listed. Part Number and Status filters apply at once. "
                         "No row: message no. 3.")
    op[3]['items'] = [
        "Unit = Part Number + Customer Order Date. Scan order (decided 21-Oct): Allocation Priority (= Customer Order Date), Customer Code, Customer Order No, Customer Order Date, Customer Order Time, "
        "Destination Code, Detailed Item No, Serial No; at receiving the pcs are scanned in this fixed order.",
        "Supplier case = PCS_CASE pcs in scan order; a case can hold several customer orders, POs and destinations. Case Qty = number of supplier cases; "
        "PO Readiness (case) = cases whose whole qty is pre-mapped to a PO.",
        "The warehouse packs 1 case = 1 destination, so an ASN may stop only after a case where every destination of the unit is a multiple of "
        "PCS_CASE (valid cut). The cases up to a valid cut are a block = one ASN option step (e.g. VN 10, TH 6, VN 14: blocks case 1 | cases 2-3 | "
        "case 4 | case 5).",
        "A block is Ready ('6') when it and every earlier block have a PO; otherwise Not Ready ('7'): blocks are never skipped. Unit: Ready (all "
        "blocks), Partially Ready (the first k blocks), Not Ready (first block; check box disabled, message no. 2).",
        "Created: blocks in a submitted ASN are no longer in the delivery plan (shown in ASN Inquiry); the open qty of the unit is cut again from case 1 "
        "in the same order at the next [Search]."]
    op[6]['text'] = '5.4 Select Cases (CUT_FLAG) and Create ASN'
    op[7]['items'][0] = ("The user ticks the supplier cases to send with the check box of each case row. The ticked cases of a unit start at case 1 and "
                         "end on a case with CUT_FLAG Y, so that every destination closes its warehouse case at receiving: ticking a case with CUT_FLAG N "
                         "also ticks the following cases up to the next CUT_FLAG Y (message no. 10). Example: case 2 = VN 4 + TH 2 (CUT N) -> cases 1-3 are "
                         "ticked; cases 1-2 alone are not possible. Only Ready cases can be ticked. One ASN is for one Supplier Code + Supplier Plant "
                         "(existing rule): ticked units of more than one supplier give message no. 9 and nothing is created.")
    op[7]['items'][1] = ("[Create ASN] does the real mapping of the chosen blocks in one transaction: the slices inserted into TB_R_INSTRUCTION (case and "
                         "line sequence of XD09), MAPPED_QTY in the new table TB_R_PRA_DAILY_ORDER_MAPPED, and PO_MAPPED_FLAG = 'Y' on the H0253 lines "
                         "that are now completely in TB_R_INSTRUCTION. Then the Case List opens.")
    op[7]['items'][3] = ("[Back] / [Cancel] on the Case List cancel the creation: the rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to 'N' "
                         "and MAPPED_QTY reduced again, so the blocks can be selected again.")
    for m in s['display_messages']:
        if m.get('msg_id') == 'MSG2':
            m['message'] = 'Not Ready: case {n} of {Part No} / {Customer Order Date} (or an earlier case) is not assigned to a PO yet ({k} of {c} cases assigned)'
        if m.get('cause') == 'A selected unit is no longer Ready':
            m['cause'] = 'A chosen block is no longer Ready'
    for t in s['tables']:
        if t['name'] == '#TEMP_INSTRUCTION':
            t['description'], t['columns'] = TEMP_DESC, TEMP_COLS
        if t['name'] == I:
            t['description'] = ("Real mapping made by [Create ASN]: one row per supplier case x customer order line x PO of the chosen blocks "
                                "(case and line sequence of XD09). Rows are deleted by [Back] / [Cancel] on the Case List; [Submit ASN] (5.7) fills "
                                "ASN_NO and CASE_NO. Columns proposed.")
    for x in it:
        if x.get('name') == 'Selection summary':
            x['description'] = "'{n} units · {c} cases · {q} pcs selected · {units}'. Empty: hint that cases of different units / dates can go into one ASN."
        if x.get('name') == 'Clear selection':
            x['description'] = 'Unticks all cases.'
    msgs = s['display_messages']
    msgs.insert(msgs.index(next(m for m in msgs if m.get('msg_id') == 'MSG9')) + 1,
                {"event": "Tick a case with CUT_FLAG N", "cause": "The ASN cannot stop after this case (a destination would not close its case)", "type": "Info",
                 "msg_id": "MSG10", "message": "Case {n} cannot be the last case: {dest} would not complete a case. Cases {n}-{m} are selected together.",
                 "action": "Keep the selection (cases up to {m}) or untick."})
    s['sample_sheet']['sections'] += XD10_CASE_SECTIONS
    save('XD10', s)


xd09()
xd10()
