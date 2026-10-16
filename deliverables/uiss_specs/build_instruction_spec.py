"""Spec for X12_UISS_Batch_GetOrderPOPreMapping.xlsx (UISS-Batch format): the on-demand function behind [Search]
of ASN Crossdock Creation (X8). Customer orders are pre-mapped to supplier POs (FIFO) into the temporary #TEMP_INSTRUCTION."""
import json, sys
from asn_common import H0253, INSTR, INSTR_COLS, INSTR_TABLE, PRA_M, PRA_MAP, PRA_MAP_TABLE, PRA_P, header, revisions

SAMPLE = {
 "title": "Sample Input", "heading": "Sample pre-mapping - Get Order (FIFO by Customer Order Date)",
 "intro": ["Part PART-C, 6 pcs/case. Customer order lines of H0253 (order status 7, Hold Flag N, not mapped) and PO parts of the Pra Daily Order (crossdock flag X)."],
 "sections": [
  {"title": "A. Get Order on 14-Oct: PO1 (PO Date 14-Oct, 12 pcs of PART-C) is the only released PO",
   "columns": ["Customer Order Date", "Customer Order No", "Destination", "Order Qty", "PO No", "Assigned Qty", "Remaining Order Qty"], "widths": [18, 17, 14, 10, 8, 12, 18],
   "rows": [["13-Oct-2026", "CO-13001", "9715310", 4, "PO1", 4, 0], ["13-Oct-2026", "CO-13004", "9722D10", 2, "PO1", 2, 0],
            ["13-Oct-2026", "CO-13003", "9811110", 6, "PO1", 6, 0], ["13-Oct-2026", "CO-13005", "9722D10", 2, "(none)", 0, 2],
            ["13-Oct-2026", "CO-13002", "9715310", 2, "(none)", 0, 2], ["13-Oct-2026", "CO-13006", "9722D10", 2, "(none)", 0, 2]]},
  {"title": "B. Get Order on 15-Oct: PO2 (PO Date 15-Oct, 6 pcs of PART-C) covers the remaining lines",
   "columns": ["Customer Order Date", "Customer Order No", "Destination", "Order Qty", "PO No", "Assigned Qty", "Remaining Order Qty"], "widths": [18, 17, 14, 10, 8, 12, 18],
   "rows": [["13-Oct-2026", "CO-13001", "9715310", 4, "PO1", 4, 0], ["13-Oct-2026", "CO-13004", "9722D10", 2, "PO1", 2, 0],
            ["13-Oct-2026", "CO-13003", "9811110", 6, "PO1", 6, 0], ["13-Oct-2026", "CO-13005", "9722D10", 2, "PO2", 2, 0],
            ["13-Oct-2026", "CO-13002", "9715310", 2, "PO2", 2, 0], ["13-Oct-2026", "CO-13006", "9722D10", 2, "PO2", 2, 0]]},
  {"title": "C. Result on the screen", "columns": ["No", "Scenario", "Expected result"], "widths": [6, 50, 70],
   "rows": [["N1", "Get Order A", "PART-C 13-Oct: Case Qty 3, PO Readiness 1 (only PH complete), ASN Status Not Ready ('7')."],
            ["N2", "Get Order B", "All lines pre-mapped: PO Readiness 3, ASN Status Ready ('6'); the unit can be selected for Create ASN."],
            ["N3", "A destination is on hold (Hold Flag Y on its lines)", "Its lines are not taken; the unit is computed without it (it may become Ready)."],
            ["N4", "PO qty larger than the open order qty", "The PO remainder stays open for later customer orders (FIFO)."],
            ["E1", "Database error", "Nothing is kept in the temporary table; message on the screen, Log FAILED."]]}]}

spec = {
 "doc_type": "batch",
 "header": header("X12", "Function (on demand)", "Get Order - Customer Order PO Pre-mapping"),
 "revisions": revisions('15-Oct-26'),
 "general": {
  "objective": [
   f"To get the crossdock customer orders (H0253, order status 7, Hold Flag N, not yet mapped) and pre-map them to the crossdock supplier PO parts (Pra Daily Order, crossdock flag X), FIFO by order date, into the temporary table {INSTR}.",
   "To give ASN Crossdock Creation (X8) the delivery plan per Part Number + Customer Order Date with Case Qty, PO Readiness (case) and ASN Status Ready / Not Ready.",
   "It runs when the user clicks [Search] on X8; there is no scheduler. The real mapping is done later by [Create ASN] on X8."],
  "operation_flow": {"flow": {"direction": "TB", "nodes": [
     {"id": "a", "label": "[Search] on ASN Crossdock Creation", "type": "event"},
     {"id": "b", "label": "Get customer orders (H0253)", "type": "process"},
     {"id": "c", "label": "Get PO parts (Pra Daily Order)", "type": "process"},
     {"id": "d", "label": "Pre-map FIFO per part number", "type": "process"},
     {"id": "e", "label": "Fill #TEMP_INSTRUCTION, set status", "type": "process"}],
    "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}, {"from": "d", "to": "e"}]}},
  "inputs": [
   {"name": "Delivery Date, Rit, Route", "type": "Screen", "description": "From the Delivery section of X8 (carried to the ASN)"},
   {"name": H0253, "type": "DB", "description": "ORDER_STATUS = '7', HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N', latest data (replicated by X10)"},
   {"name": PRA_M + " / " + PRA_P, "type": "DB", "description": "CROSSDOCK_FLAG = 'X', latest data, by Order Date ascending"},
   {"name": PRA_MAP, "type": "DB", "description": "New table: MAPPED_QTY per PO part; open PO qty = PO_ORDER_QTY - MAPPED_QTY"}],
  "outputs": [
   {"name": INSTR, "type": "Temp", "description": "One row per line x PO; one row with PO_NO NULL for the qty still without a PO"},
   {"name": "ASN Crossdock Creation (X8)", "type": "Screen", "description": "Delivery plan: Customer Order Date, Part Number, Case Qty, PO Readiness (case), ASN Status"}],
  "extra_tables": [
   {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
    "rows": [["Delivery Date", "Chosen on X8; carried to the ASN"], ["Rit / Route", "Chosen on X8; carried to the ASN"], ["Supplier", "Supplier of the login user"]]},
   {"title": "Grouping Keys", "columns": [{"title": "Field Name", "width": 20}], "rows": ["PART_NO", "ORDER_DT (unit)", "DESTINATION_CD (case)"]},
   {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
    "rows": [["Trigger", "On demand: [Search] on ASN Crossdock Creation (X8). No scheduler."]]}]
 },
 "func_flow": {
  "flow": {"direction": "TB", "nodes": [
     {"id": "p1", "label": "Start ([Search])", "type": "process", "step": 1},
     {"id": "h", "label": H0253, "type": "db", "lane": "input"},
     {"id": "p2", "label": "Get customer order lines", "type": "process", "step": 2},
     {"id": "m", "label": PRA_M + " / " + PRA_P, "type": "db", "lane": "input"},
     {"id": "p3", "label": "Get PO parts", "type": "process", "step": 3},
     {"id": "p4", "label": "Pre-map FIFO per part number", "type": "process", "step": 4},
     {"id": "o", "label": INSTR, "type": "db", "lane": "output"},
     {"id": "p5", "label": "Unit status and return to screen", "type": "process", "step": 5}],
   "edges": [{"from": "p1", "to": "p2"}, {"from": "h", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "m", "to": "p3"}, {"from": "p3", "to": "p4"},
             {"from": "p4", "to": "o"}, {"from": "p4", "to": "p5"}]},
  "steps": [
   "The user clicks [Search] on ASN Crossdock Creation (X8) with Delivery Date and Rit. The previous content of the temporary table of the session is cleared.",
   {"text": f"Get the customer order lines from {H0253}:",
    "children": ["ORDER_STATUS = '7' (Cross Dock), HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'; latest data; earliest order date first per part number (FIFO, T-System key). Status '2' (cancel from the source) is not taken.",
                 "Get: Customer Code, Customer Order No, Order Date, Destination Code, Detailed Item No, Serial No, Part Number, Order Status Qty."]},
   {"text": f"Get the PO parts from {PRA_M} + {PRA_P}:",
    "children": ["CROSSDOCK_FLAG = 'X'; latest data; open PO qty = PO_ORDER_QTY - MAPPED_QTY of " + PRA_MAP + " (0 when no row) > 0; ordered by Order Date ascending (FIFO).",
                 "Get: PO Number, Manifest Number, Supplier Code / Plant, Sub Supplier Code / Plant, Order Type, Dock Code, PO Order Qty, Order Date, ETD Ori, Manifest Item No, Part Number."]},
   {"text": "Pre-map per part number, FIFO (see 4.1), and insert the result in " + INSTR + ".",
    "children": ["Each PO qty is given to the oldest open lines first; a line may be split over several POs; the open qty of a line is one row with PO_NO NULL."]},
   {"text": "Set the status of each unit (Part Number + Customer Order Date) and return the delivery plan to X8 (see 4.2).",
    "children": ["Error: clear the temporary table, show the error on the screen and record the Log (FAILED)."]}]
 },
 "data_map": {"blocks": [
  {"source": {"table": H0253 + " + " + PRA_M + " / " + PRA_P, "keys": [{"field": "PART_NO", "value": "Same part number"}]},
   "destination": {"table": INSTR, "operation": "Insert", "description": "Line x PO pre-mapping (temporary)"},
   "mappings": [
     {"dest_field": "INSTRUCTION_ID", "description": "Running number"},
     {"source_field": "H0253.CUSTOMER_CD", "dest_field": "CUSTOMER_CD"}, {"source_field": "H0253.CUSTOMER_ORDER_NO", "dest_field": "CUSTOMER_ORDER_NO"},
     {"source_field": "H0253.ORDER_DT", "dest_field": "ORDER_DT"}, {"source_field": "H0253.DESTINATION_CD", "dest_field": "DESTINATION_CD"},
     {"source_field": "H0253.DETAILED_ITEM_NO", "dest_field": "DETAILED_ITEM_NO"}, {"source_field": "H0253.SERIAL_NO", "dest_field": "SERIAL_NO"},
     {"source_field": "H0253.SHIPPING_PART_NO", "dest_field": "PART_NO"}, {"source_field": "H0253.ORDER_STATUS", "dest_field": "ORDER_STATUS"},
     {"source_field": "H0253.ORDER_STATUS_QTY", "dest_field": "CUST_ORDER_QTY"},
     {"dest_field": "ASSIGNED_QTY", "description": "Qty of the line given to this PO (FIFO); 0 for the PO_NO NULL row"},
     {"dest_field": "REMAINING_ORDER_QTY", "description": "Qty of the line still without a PO after this assignment"},
     {"source_field": "PO Number", "dest_field": "PO_NO", "description": "NULL for the open remainder"}, {"source_field": "Manifest Number", "dest_field": "MANIFEST_NO"},
     {"source_field": "Manifest Item No", "dest_field": "MANIFEST_ITEM_NO"}, {"source_field": "Order Date (PO)", "dest_field": "PO_ORDER_DT"},
     {"source_field": "PO Order Qty", "dest_field": "PO_ORDER_QTY"}, {"source_field": "Supplier Code", "dest_field": "SUPPLIER_CD"},
     {"source_field": "Supplier Plant", "dest_field": "SUPPLIER_PLANT"}, {"source_field": "Sub Supplier Code", "dest_field": "SUB_SUPPLIER_CD"},
     {"source_field": "Sub Supplier Plant", "dest_field": "SUB_SUPPLIER_PLANT"}, {"source_field": "Order Type", "dest_field": "ORDER_TYPE"},
     {"source_field": "Dock Code", "dest_field": "DOCK_CD"}, {"source_field": "ETD Ori", "dest_field": "ETD_ORI"},
     {"dest_field": "CROSSDOCK_STATUS", "description": "'6' Ready when no row of the unit has PO_NO NULL; else '7' Not Ready (refer 4.2)"}]}]},
 "func_desc_layout": "two",
 "func_desc": [
  {"type": "text", "level": 0, "text": "This function builds the delivery plan of ASN Crossdock Creation on demand. It only pre-maps: nothing permanent is changed; the real mapping is done by [Create ASN] (X8)."},
  {"type": "heading", "text": "4.1 FIFO Pre-mapping"},
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Per part number (H0253.SHIPPING_PART_NO = Pra Daily Order Part Number).",
    "Customer order lines by Customer Order Date (then Order Time, Customer Order No, Detailed Item No, Serial No); lines with HOLD_FLAG = 'Y' or PO_MAPPED_FLAG = 'Y' are not taken.",
    "PO parts by Order Date ascending; each PO qty goes to the oldest open lines first.",
    "A line may be split over several POs (one row per assignment); its open qty is one row with PO_NO NULL.",
    "A PO remainder without open line stays open for later customer orders."]},
  {"type": "column_break"},
  {"type": "heading", "text": "4.2 Unit and Status"},
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Unit = Part Number + Customer Order Date. Case = one per destination of the unit: the qty of the destination is summed into one case (it never exceeds pcs/case).",
    "Case Qty = number of destinations of the unit. PO Readiness (case) = cases whose whole qty is pre-mapped to a PO.",
    "CROSSDOCK_STATUS '6' Ready: every line of the unit is pre-mapped. '7' Not Ready: at least one line of the unit has no PO yet.",
    "Shown on X8 as ASN Status Ready / Not Ready. Units with PO Readiness 0 are not listed on X8; units already in a submitted ASN (ASN status '1' Created) are not taken (PO_MAPPED_FLAG = 'Y').",
    "The mapped qty is kept in the new table " + PRA_MAP + " (no new column in the Pra Daily Order); it is updated by [Create ASN] on X8, not by this function.",
    "Nothing is saved by this function: " + INSTR + " is the pre-mapping only; the real mapping is inserted into TB_R_INSTRUCTION by [Create ASN]."]}],
 "logging_messages": [
  {"event": "Get Order", "cause": "Read or insert fails", "type": "Error", "msg_id": "LOG1", "message": "Get Order failed for Delivery Date <DELIVERY_DT> <RIT>: <ERROR_DETAIL>.", "action": {"system": "Clear the temporary table.", "user": "Retry; contact PIC if it persists."}},
  {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG2", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Clear the temporary table.", "user": "User contact PIC"}}],
 "appendix_layout": "full",
 "appendix": [{"type": "text", "level": 0, "text": "Sample FIFO pre-mapping: see sheet Sample Input."}],
 "sample_sheet": SAMPLE,
 "tables": [INSTR_TABLE, PRA_MAP_TABLE]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
