"""Spec for X12_UISS_Batch_CustomerOrderPOMapping.xlsx (UISS-Batch, Customer Order - PO Mapping into TB_R_INSTRUCTION)."""
import json, sys
from asn_common import H0253, INSTR, INSTR_COLS, INSTR_TABLE, NC, PRA_M, PRA_P, header, revisions

LOG = 'Log'
B = ''
SAMPLE = {
 "title": "Sample Input", "heading": "Sample mapping - Customer Order - PO Mapping (FIFO by Customer Order Date)",
 "intro": ["Part PART-C, 6 pcs/case. Customer order lines of H0253 (order status 7) and PO parts of the Pra Daily Order (crossdock flag X)."],
 "sections": [
  {"title": "A. Run of 14-Oct: PO1 (PO Date 14-Oct, 12 pcs of PART-C)",
   "columns": ["Customer Order Date", "Customer Order No", "Destination", "Order Qty", "PO No", "Assigned Qty", "Remaining Order Qty"], "widths": [18, 17, 14, 10, 8, 12, 18],
   "rows": [["13-Oct-2026", "CO-13001", "9715310", 4, "PO1", 4, 0], ["13-Oct-2026", "CO-13004", "9722D10", 2, "PO1", 2, 0],
            ["13-Oct-2026", "CO-13003", "9811110", 6, "PO1", 6, 0], ["13-Oct-2026", "CO-13005", "9722D10", 2, "(none)", 0, 2],
            ["13-Oct-2026", "CO-13002", "9715310", 2, "(none)", 0, 2], ["13-Oct-2026", "CO-13006", "9722D10", 2, "(none)", 0, 2]]},
  {"title": "B. Run of 15-Oct: PO2 (PO Date 15-Oct, 6 pcs of PART-C) takes the oldest remaining lines first",
   "columns": ["Customer Order Date", "Customer Order No", "Destination", "Order Qty", "PO No", "Assigned Qty", "Remaining Order Qty"], "widths": [18, 17, 14, 10, 8, 12, 18],
   "rows": [["13-Oct-2026", "CO-13005", "9722D10", 2, "PO2", 2, 0], ["13-Oct-2026", "CO-13002", "9715310", 2, "PO2", 2, 0],
            ["13-Oct-2026", "CO-13006", "9722D10", 2, "PO2", 2, 0]]},
  {"title": "C. Result", "columns": ["No", "Scenario", "Expected result"], "widths": [6, 50, 70],
   "rows": [["N1", "After run A", "PART-C 13-Oct has 6 pcs without PO: Waiting for Next PO on ASN Crossdock Creation (cases already visible)."],
            ["N2", "After run B", "All lines assigned (PO1 + PO2): PART-C 13-Oct Ready to Delivery from 15-Oct (condition 3)."],
            ["N3", "PO qty larger than the open order qty", "The PO remainder stays open for later customer orders (FIFO)."],
            ["E1", "Database error while inserting", "Whole run rolled back, Log FAILED."]]}]}


def full(table_cols, given, default):
    names = {m["dest_field"] for m in given}
    return given + [{"dest_field": c[0], "description": default} for c in table_cols if c[0] not in names]


spec = {
 "doc_type": "batch",
 "header": header("X12", "Batch", "Customer Order - PO Mapping (TB_R_INSTRUCTION)"),
 "revisions": revisions(),
 "general": {
  "objective": [
   f"To pair the crossdock customer order lines (H0253, order status 7) with the crossdock supplier PO parts (Pra Daily Order, crossdock flag X), FIFO by Customer Order Date, and store the result in {INSTR}.",
   "The result is the delivery plan of ASN Crossdock Creation (X8). In case any error occurs, nothing is saved (all-or-nothing)."],
  "operation_flow": {"flow": {"direction": "TB", "nodes": [
     {"id": "a", "label": "Scheduler", "type": "event"},
     {"id": "b", "label": "Get open customer order lines (H0253)", "type": "process"},
     {"id": "c", "label": "Get open PO parts (Pra Daily Order)", "type": "process"},
     {"id": "d", "label": "Pair FIFO per part number", "type": "process"},
     {"id": "e", "label": "Insert / update TB_R_INSTRUCTION, Log", "type": "process"}],
    "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}, {"from": "d", "to": "e"}]}},
  "inputs": [
   {"name": H0253, "type": "DB", "description": "Customer order lines: ORDER_STATUS = '7' (Cross Dock), not (fully) mapped to a PO yet (replicated by X10)"},
   {"name": PRA_M + " / " + PRA_P, "type": "DB", "description": "Supplier PO / manifest and its parts: CROSSDOCK_FLAG = 'X', not (fully) mapped to a customer order yet"},
   {"name": INSTR, "type": "DB", "description": "Already mapped qty (open remainder of lines and POs)"}],
  "outputs": [
   {"name": INSTR, "type": "DB", "description": "if successful: one row per line x PO assignment; one row with PO_NO NULL for the qty still without a PO"},
   {"name": LOG, "type": "DB", "description": "One record per run with status SUCCESS / FAILED"}],
  "extra_tables": [
   {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
    "rows": [["-", "No parameter. All open customer order lines and PO parts are processed."]]},
   {"title": "Grouping Keys", "columns": [{"title": "Field Name", "width": 20}], "rows": ["PART_NO"]},
   {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
    "rows": [["Trigger", "Scheduler set in the system master (TBC); after the H0253 sync (X10) and the Pra Daily Order of the day are available."]]}]
 },
 "func_flow": {
  "flow": {"direction": "TB", "nodes": [
     {"id": "p1", "label": "Start (scheduler)", "type": "process", "step": 1},
     {"id": "h", "label": H0253, "type": "db", "lane": "input"},
     {"id": "p2", "label": "Get open customer order lines", "type": "process", "step": 2},
     {"id": "m", "label": PRA_M + " / " + PRA_P, "type": "db", "lane": "input"},
     {"id": "p3", "label": "Get open PO parts", "type": "process", "step": 3},
     {"id": "p4", "label": "Pair FIFO per part number", "type": "process", "step": 4},
     {"id": "p5", "label": "Insert / update result", "type": "process", "step": 5},
     {"id": "o", "label": INSTR, "type": "db", "lane": "output"},
     {"id": "p6", "label": "Commit or roll back, Log", "type": "process", "step": 6},
     {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
   "edges": [{"from": "p1", "to": "p2"}, {"from": "h", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "m", "to": "p3"}, {"from": "p3", "to": "p4"},
             {"from": "p4", "to": "p5"}, {"from": "p5", "to": "o"}, {"from": "p5", "to": "p6"}, {"from": "p6", "to": "log"}]},
  "steps": [
   "The scheduler starts the batch.",
   {"text": f"Get the open customer order lines from {H0253}:",
    "children": ["ORDER_STATUS = '7' (Cross Dock); latest data; lines with qty not yet mapped to a PO (new lines, or the PO_NO NULL row of TB_R_INSTRUCTION).",
                 "Get: Customer Code, Customer Order No, Order Date, Destination Code, Detailed Item No, Serial No, Part Number, Order Status Qty."]},
   {"text": f"Get the open PO parts from {PRA_M} + {PRA_P}:",
    "children": ["CROSSDOCK_FLAG = 'X'; latest data; PO qty not yet mapped to a customer order; ordered by Order Date ascending.",
                 "Get: PO Number, Manifest Number, Supplier Code / Plant, Sub Supplier Code / Plant, Order Type, Dock Code, PO Order Qty, Order Date, ETD Ori, Manifest Item No, Part Number."]},
   {"text": "Pair per part number, FIFO (see 4.1):",
    "children": ["Customer order lines sorted by Customer Order Date (then Order Time, Customer Order No, Detailed Item No, Serial No); PO parts sorted by Order Date.",
                 "Each PO qty is given to the oldest open lines first; a line may be split over several POs; a PO remainder stays open for the next lines."]},
   {"text": f"Save in {INSTR} (see 4.2).", "children": ["One row per line x PO assignment; the open remainder of a line is kept in one row with PO_NO NULL (REMAINING_ORDER_QTY)."]},
   "No error: commit, Log SUCCESS. Error: roll back everything, Log FAILED. Exit."]
 },
 "data_map": {"blocks": [
  {"source": {"table": H0253 + " + " + PRA_M + " / " + PRA_P, "keys": [{"field": "PART_NO", "value": "Same part number"}]},
   "destination": {"table": INSTR, "operation": "Insert", "description": "Line x PO assignment"},
   "mappings": full(INSTR_COLS, [
     {"dest_field": "INSTRUCTION_ID", "description": "Auto (identity)"},
     {"source_field": "H0253.CUSTOMER_CD", "dest_field": "CUSTOMER_CD"}, {"source_field": "H0253.CUSTOMER_ORDER_NO", "dest_field": "CUSTOMER_ORDER_NO"},
     {"source_field": "H0253.ORDER_DT", "dest_field": "ORDER_DT"}, {"source_field": "H0253.DESTINATION_CD", "dest_field": "DESTINATION_CD"},
     {"source_field": "H0253.DETAILED_ITEM_NO", "dest_field": "DETAILED_ITEM_NO"}, {"source_field": "H0253.SERIAL_NO", "dest_field": "SERIAL_NO"},
     {"source_field": "H0253.SHIPPING_PART_NO", "dest_field": "PART_NO"}, {"source_field": "H0253.ORDER_STATUS", "dest_field": "ORDER_STATUS"},
     {"source_field": "H0253.ORDER_STATUS_QTY", "dest_field": "CUST_ORDER_QTY"},
     {"dest_field": "ASSIGNED_QTY", "description": "Qty of the line given to this PO (FIFO)"},
     {"dest_field": "REMAINING_ORDER_QTY", "description": "Qty of the line still without a PO after this assignment"},
     {"source_field": "PO Number", "dest_field": "PO_NO"}, {"source_field": "Manifest Number", "dest_field": "MANIFEST_NO"},
     {"source_field": "Manifest Item No", "dest_field": "MANIFEST_ITEM_NO"}, {"source_field": "Order Date (PO)", "dest_field": "PO_ORDER_DT"},
     {"source_field": "PO Order Qty", "dest_field": "PO_ORDER_QTY"}, {"source_field": "Supplier Code", "dest_field": "SUPPLIER_CD"},
     {"source_field": "Supplier Plant", "dest_field": "SUPPLIER_PLANT"}, {"source_field": "Sub Supplier Code", "dest_field": "SUB_SUPPLIER_CD"},
     {"source_field": "Sub Supplier Plant", "dest_field": "SUB_SUPPLIER_PLANT"}, {"source_field": "Order Type", "dest_field": "ORDER_TYPE"},
     {"source_field": "Dock Code", "dest_field": "DOCK_CD"}, {"source_field": "ETD Ori", "dest_field": "ETD_ORI"},
     {"dest_field": "ASN_NO", "description": "NULL (filled by X8)"}, {"dest_field": "CASE_NO", "description": "NULL (filled by X8)"},
     {"dest_field": "CREATED_BY", "description": "Batch user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date and time"},
     {"dest_field": "CHANGED_BY", "description": "Batch user ID"}, {"dest_field": "CHANGED_DT", "description": "Server system date and time"}], NC)},
  {"source": {"table": H0253, "keys": [{"field": "Line", "value": "Qty not assigned to any PO"}]},
   "destination": {"table": INSTR, "operation": "Insert", "description": "Open remainder of a line (PO_NO NULL); replaced on the next run"},
   "mappings": full(INSTR_COLS, [
     {"dest_field": "INSTRUCTION_ID", "description": "Auto (identity)"},
     {"dest_field": "ASSIGNED_QTY", "description": "0"}, {"dest_field": "REMAINING_ORDER_QTY", "description": "Open qty of the line"},
     {"dest_field": "PO_NO", "description": "NULL"}, {"dest_field": "MANIFEST_NO", "description": "NULL"}, {"dest_field": "MANIFEST_ITEM_NO", "description": "NULL"},
     {"dest_field": "PO_ORDER_DT", "description": "NULL"}, {"dest_field": "PO_ORDER_QTY", "description": "NULL"},
     {"dest_field": "CREATED_BY", "description": "Batch user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date and time"},
     {"dest_field": "CHANGED_BY", "description": "Batch user ID"}, {"dest_field": "CHANGED_DT", "description": "Server system date and time"}],
     "Same as the line x PO block (customer order columns); PO columns NULL")},
  {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
   "mappings": [{"dest_field": "BATCH_ID", "description": "'CO_PO_MAPPING'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                {"dest_field": "ROW_COUNT", "description": "Rows inserted"}, {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                {"dest_field": "START_DT", "description": "Start date and time"}, {"dest_field": "END_DT", "description": "End date and time"}]}]},
 "func_desc_layout": "two",
 "func_desc": [
  {"type": "text", "level": 0, "text": "This batch builds the delivery plan of crossdock parts: which customer order lines are covered by which supplier PO. Schedule is set in the system master (not explained in this document)."},
  {"type": "heading", "text": "4.1 FIFO Pairing"},
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Pairing is done per part number (H0253.SHIPPING_PART_NO = Pra Daily Order Part Number).",
    "Customer order lines are taken FIFO by Customer Order Date (then Order Time, Customer Order No, Detailed Item No, Serial No).",
    "PO parts are taken by Order Date ascending. Each PO qty is given to the oldest open lines first.",
    "A line may be split over several POs (one row per assignment). Its open qty is kept as REMAINING_ORDER_QTY in a row with PO_NO NULL until a next PO covers it.",
    "A PO remainder that has no open line stays open for later customer orders."]},
  {"type": "column_break"},
  {"type": "heading", "text": "4.2 Saving and Use"},
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Existing assignment rows are not changed; the PO_NO NULL rows of the processed lines are replaced by the new assignments and, if still open, a new PO_NO NULL row.",
    "ASN_NO and CASE_NO stay NULL; they are filled by ASN Crossdock Creation (X8) when the ASN is submitted.",
    "A unit (Part Number + Customer Order Date) without any PO_NO NULL row is Ready to Delivery on X8; otherwise Waiting for Next PO. With POs of different PO Dates the unit becomes ready on the last PO Date (condition 3).",
    "All-or-nothing: any error rolls back the whole run.",
    "TBD: physical structure of TB_R_PRA_DAILY_ORDER_MANIFEST / PART and how 'not yet mapped' is flagged there."]}],
 "logging_messages": [
  {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": "Customer order - PO mapping started.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": "Customer order - PO mapping ended. Status <STATUS>, rows <ROW_COUNT>.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Save", "cause": "Insert / update of TB_R_INSTRUCTION fails", "type": "Error", "msg_id": "LOG3", "message": "Cannot save the mapping of Part No <PART_NO>: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
  {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}],
 "appendix_layout": "full",
 "appendix": [{"type": "text", "level": 0, "text": "Sample FIFO mapping: see sheet Sample Input."}],
 "sample_sheet": SAMPLE,
 "tables": [INSTR_TABLE]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
