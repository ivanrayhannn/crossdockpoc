"""Spec builder for the replication batches of H tables (UISS-Batch, structure only, no sample data):
  X9  TB_R_H0202_DEMAND_HISTORY_SUM  -> X9_UISS_Batch_H0202DemandHistorySync.xlsx
  X10 TB_R_H0253_ORDER_CONTROL_PRE   -> X10_UISS_Batch_H0253OrderControlSync.xlsx
Usage: build_h_sync_spec.py OUT.json H0202|H0253"""
import json, sys
from calc_common import LOG, header, revisions

NOTE = "Same columns as the source table; types and lengths follow DB Surrounding. Key (PK) TBD."
H2_COLS = [["CUSTOMER_CD", "VARCHAR(TBD)", "", "Y", ""], ["CUSTOMER_ORDER_NO", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_DT", "DATE", "", "Y", ""], ["ORDER_TIME", "VARCHAR(TBD)", "", "Y", ""], ["DESTINATION_CD", "VARCHAR(TBD)", "", "Y", ""], ["DETAILED_ITEM_NO", "VARCHAR(TBD)", "", "Y", ""], ["SERIAL_NO", "VARCHAR(TBD)", "", "Y", ""], ["DEMAND_HISTORY_UPDATE_CD", "VARCHAR(TBD)", "", "Y", ""], ["DEPOT_CD", "VARCHAR(TBD)", "", "Y", ""], ["DOMESTIC_OVERSEAS_CLASS_CD", "VARCHAR(TBD)", "", "Y", ""], ["REGION_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_MAKER_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_PART_NO", "VARCHAR(TBD)", "", "Y", ""], ["SHIPPING_PART_NO", "VARCHAR(TBD)", "", "Y", ""], ["DEMAND_HISTORY_DT", "DATE", "", "Y", ""], ["ORDER_TRANSPORTATION_CD", "VARCHAR(TBD)", "", "Y", ""], ["TOPAS_ORDER_TYPE", "VARCHAR(TBD)", "", "Y", ""], ["SUPPLIER_CD", "VARCHAR(TBD)", "", "Y", ""], ["CREATED_DEMAND_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_ERROR_CD", "VARCHAR(TBD)", "", "Y", ""], ["RA_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_PORTION_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_QTY_DEMAND_QTY", "NUMBER", "", "Y", ""], ["SHIPPING_QTY", "NUMBER", "", "Y", ""], ["REJECT_QTY", "NUMBER", "", "Y", ""], ["ETC_CANCEL_QTY", "NUMBER", "", "Y", ""], ["DIRECT_DELIVERY_QTY", "NUMBER", "", "Y", ""], ["FIRM_ORDER_QTY", "NUMBER", "", "Y", ""], ["CROSS_DOCK_QTY", "NUMBER", "", "Y", ""], ["PROCESS_QTY", "NUMBER", "", "Y", ""], ["BO_CANCEL_QTY", "NUMBER", "", "Y", ""], ["NON_TARGET_ORDER_QTY_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["REGISTRANT_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_JOB_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_OPERATOR_ID", "VARCHAR(TBD)", "", "Y", ""], ["INTF_UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_BY", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["UPDATE_BY", "VARCHAR(TBD)", "", "Y", ""]]
H3_COLS = [["CUSTOMER_CD", "VARCHAR(TBD)", "", "Y", ""], ["CUSTOMER_ORDER_NO", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_DT", "DATE", "", "Y", ""], ["ORDER_TIME", "VARCHAR(TBD)", "", "Y", ""], ["DESTINATION_CD", "VARCHAR(TBD)", "", "Y", ""], ["DETAILED_ITEM_NO", "VARCHAR(TBD)", "", "Y", ""], ["TOPAS_ORDER_TYPE", "VARCHAR(TBD)", "", "Y", ""], ["DEMAND_HISTORY_UPDATE_DT", "DATE", "", "Y", ""], ["SHIPPING_MAKER_CD", "VARCHAR(TBD)", "", "Y", ""], ["SHIPPING_PART_NO", "VARCHAR(TBD)", "", "Y", ""], ["ORIGINAL_SHIPPING_QTY", "NUMBER", "", "Y", ""], ["ORDER_STATUS_QTY", "NUMBER", "", "Y", ""], ["ORDER_STATUS", "VARCHAR(TBD)", "", "Y", ""], ["BO_INSTRUCTION_CD", "VARCHAR(TBD)", "", "Y", ""], ["BO_RELEASE_DT", "DATE", "", "Y", ""], ["ORDER_GROUP", "VARCHAR(TBD)", "", "Y", ""], ["DIRECT_DELIVERY_CD", "VARCHAR(TBD)", "", "Y", ""], ["DIRECT_DELIVERY_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["CURRENCY_CD", "VARCHAR(TBD)", "", "Y", ""], ["LANDED_COST", "NUMBER", "", "Y", ""], ["NET_PRICE", "NUMBER", "", "Y", ""], ["SALES_PRICE", "NUMBER", "", "Y", ""], ["EXPORT_SALES_PRICE", "NUMBER", "", "Y", ""], ["SPECIAL_PRICE_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_DISCOUNT_CD", "VARCHAR(TBD)", "", "Y", ""], ["ITEM_DISCOUNT_RATE", "NUMBER", "", "Y", ""], ["FIRST_ALLOCATION_DT", "DATE", "", "Y", ""], ["BO_HISTORY_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_ERROR_CD", "VARCHAR(TBD)", "", "Y", ""], ["RA_CD", "VARCHAR(TBD)", "", "Y", ""], ["PENDING_ORDER_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_PORTION_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_STATUS_DT", "DATE", "", "Y", ""], ["SHIPPING_PROCESS_CTRL_CD", "VARCHAR(TBD)", "", "Y", ""], ["PROCUREMENT_PROCESS_CTRL_CD", "VARCHAR(TBD)", "", "Y", ""], ["DANGEROUS_GOODS_CLASS", "VARCHAR(TBD)", "", "Y", ""], ["CREATE_DEMAND_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["SPECIAL_CUSTOMER_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["POSS_TRANSMISSION_JUDG_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["REGISTRANT_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_JOB_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_OPERATION_ID", "VARCHAR(TBD)", "", "Y", ""], ["INTF_UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_BY", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["UPDATE_BY", "VARCHAR(TBD)", "", "Y", ""]]

CFG = {"H0202": {"fid": "X9", "table": "TB_R_H0202_DEMAND_HISTORY_SUM", "title": "Demand History Summary (H0202) Sync to NSP",
                 "desc": "Demand history summary", "cols": H2_COLS},
       "H0253": {"fid": "X10", "table": "TB_R_H0253_ORDER_CONTROL_PRE", "title": "Order Control Pre (H0253) Sync to NSP",
                 "desc": "Order control (pre)", "cols": H3_COLS}}
c = CFG[sys.argv[2]]
T, COLS, KEY = c["table"], c["cols"], sys.argv[2]
SRC, DST = T + " (DB Surrounding)", T + " (NSP)"

spec = {
 "doc_type": "batch",
 "header": header(c["fid"], c["title"]),
 "revisions": revisions(),
 "general": {
  "objective": [
   f"To replicate {T} from DB Surrounding to the table with the same name in NSP.",
   "The NSP table is fully replaced every run (delete - insert). In case any error occurs, the run is rolled back and NSP keeps the data of the last successful run."],
  "operation_flow": {"flow": {"direction": "TB", "nodes": [
     {"id": "a", "label": "Scheduler", "type": "event"},
     {"id": "b", "label": "Delete + insert " + T, "type": "process"},
     {"id": "c", "label": "Commit / roll back, Log", "type": "process"}],
    "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}},
  "inputs": [{"name": SRC, "type": "DB", "description": c["desc"]}],
  "outputs": [{"name": DST, "type": "DB", "description": "if successful: same rows as the source"},
              {"name": LOG, "type": "DB", "description": "One record per run with status SUCCESS / FAILED"}],
  "extra_tables": [
   {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
    "rows": [["-", "No parameter. All rows of the source table are copied."]]},
   {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
    "rows": [["Trigger", "Scheduler set in the system master (schedule TBC)."]]}]
 },
 "func_flow": {
  "flow": {"direction": "TB", "nodes": [
     {"id": "p1", "label": "Start (scheduler)", "type": "process", "step": 1},
     {"id": "s", "label": SRC, "type": "db", "lane": "input"},
     {"id": "p2", "label": "Delete all rows, insert all source rows", "type": "process", "step": 2},
     {"id": "d", "label": DST, "type": "db", "lane": "output"},
     {"id": "p3", "label": "Commit or roll back, record Log", "type": "process", "step": 3},
     {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
   "edges": [{"from": "p1", "to": "p2"}, {"from": "s", "to": "p2"}, {"from": "p2", "to": "d"}, {"from": "p2", "to": "p3"}, {"from": "p3", "to": "log"}]},
  "steps": [
   "The scheduler starts the batch.",
   f"Delete all rows of {DST} and insert all rows of {SRC} (same columns and values).",
   "No error: commit. Error: roll back step 2 (one transaction). Record the result in the Log. Exit."]
 },
 "data_map": {"blocks": [
  {"source": {"table": DST}, "destination": {"table": DST, "operation": "Delete", "description": "All rows (full replace)"},
   "mappings": [{"dest_field": x[0], "description": "Row is deleted"} for x in COLS]},
  {"source": {"table": SRC}, "destination": {"table": DST, "operation": "Insert", "description": "Every source row"},
   "mappings": [{"source_field": x[0], "dest_field": x[0], "description": "Same value as the source"} for x in COLS]},
  {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
   "mappings": [{"dest_field": "BATCH_ID", "description": f"'{KEY}_SYNC'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                {"dest_field": "ROW_COUNT", "description": "Rows inserted (0 when FAILED)"}, {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                {"dest_field": "START_DT", "description": "Start date and time"}, {"dest_field": "END_DT", "description": "End date and time"}]}]},
 "func_desc_layout": "full",
 "func_desc": [
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Full replace (delete - insert); all columns are copied as they are, no conversion.",
    "Delete and insert run in one transaction (all-or-nothing). When the run fails, NSP keeps the data of the last successful run.",
    "Schedule is set in the system master (TBC). Table structure: see Appendix."]}],
 "logging_messages": [
  {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": f"{KEY} sync started.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": f"{KEY} sync ended. Status <STATUS>, rows <ROW_COUNT>.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Copy table", "cause": "Read from DB Surrounding or insert into NSP fails", "type": "Error", "msg_id": "LOG3", "message": f"Cannot replicate {T}: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
  {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}],
 "appendix_layout": "full",
 "appendix": [],
 "tables": [{"name": T, "kind": "transaction", "proposed": False, "description": c["desc"] + " replicated from DB Surrounding. " + NOTE, "columns": COLS}]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
