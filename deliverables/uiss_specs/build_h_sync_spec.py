"""Spec for X9_UISS_Batch_DemandHistoryOrderControlSync.xlsx (UISS-Batch, Crossdock - Demand History and Order Control Sync to NSP).
Replicates TB_R_H0202_DEMAND_HISTORY_SUM and TB_R_H0253_ORDER_CONTROL_PRE from DB Surrounding to NSP (structure only, no sample data)."""
import json, sys
from calc_common import LOG, header, revisions

H2, H3 = 'TB_R_H0202_DEMAND_HISTORY_SUM', 'TB_R_H0253_ORDER_CONTROL_PRE'
NOTE = "Same columns as the source table; types and lengths follow DB Surrounding. Key (PK) TBD."
H2_COLS = [["CUSTOMER_CD", "VARCHAR(TBD)", "", "Y", ""], ["CUSTOMER_ORDER_NO", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_DT", "DATE", "", "Y", ""], ["ORDER_TIME", "VARCHAR(TBD)", "", "Y", ""], ["DESTINATION_CD", "VARCHAR(TBD)", "", "Y", ""], ["DETAILED_ITEM_NO", "VARCHAR(TBD)", "", "Y", ""], ["SERIAL_NO", "VARCHAR(TBD)", "", "Y", ""], ["DEMAND_HISTORY_UPDATE_CD", "VARCHAR(TBD)", "", "Y", ""], ["DEPOT_CD", "VARCHAR(TBD)", "", "Y", ""], ["DOMESTIC_OVERSEAS_CLASS_CD", "VARCHAR(TBD)", "", "Y", ""], ["REGION_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_MAKER_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_PART_NO", "VARCHAR(TBD)", "", "Y", ""], ["SHIPPING_PART_NO", "VARCHAR(TBD)", "", "Y", ""], ["DEMAND_HISTORY_DT", "DATE", "", "Y", ""], ["ORDER_TRANSPORTATION_CD", "VARCHAR(TBD)", "", "Y", ""], ["TOPAS_ORDER_TYPE", "VARCHAR(TBD)", "", "Y", ""], ["SUPPLIER_CD", "VARCHAR(TBD)", "", "Y", ""], ["CREATED_DEMAND_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_ERROR_CD", "VARCHAR(TBD)", "", "Y", ""], ["RA_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_PORTION_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_QTY_DEMAND_QTY", "NUMBER", "", "Y", ""], ["SHIPPING_QTY", "NUMBER", "", "Y", ""], ["REJECT_QTY", "NUMBER", "", "Y", ""], ["ETC_CANCEL_QTY", "NUMBER", "", "Y", ""], ["DIRECT_DELIVERY_QTY", "NUMBER", "", "Y", ""], ["FIRM_ORDER_QTY", "NUMBER", "", "Y", ""], ["CROSS_DOCK_QTY", "NUMBER", "", "Y", ""], ["PROCESS_QTY", "NUMBER", "", "Y", ""], ["BO_CANCEL_QTY", "NUMBER", "", "Y", ""], ["NON_TARGET_ORDER_QTY_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["REGISTRANT_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_JOB_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_OPERATOR_ID", "VARCHAR(TBD)", "", "Y", ""], ["INTF_UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_BY", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["UPDATE_BY", "VARCHAR(TBD)", "", "Y", ""]]
H3_COLS = [["CUSTOMER_CD", "VARCHAR(TBD)", "", "Y", ""], ["CUSTOMER_ORDER_NO", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_DT", "DATE", "", "Y", ""], ["ORDER_TIME", "VARCHAR(TBD)", "", "Y", ""], ["DESTINATION_CD", "VARCHAR(TBD)", "", "Y", ""], ["DETAILED_ITEM_NO", "VARCHAR(TBD)", "", "Y", ""], ["TOPAS_ORDER_TYPE", "VARCHAR(TBD)", "", "Y", ""], ["DEMAND_HISTORY_UPDATE_DT", "DATE", "", "Y", ""], ["SHIPPING_MAKER_CD", "VARCHAR(TBD)", "", "Y", ""], ["SHIPPING_PART_NO", "VARCHAR(TBD)", "", "Y", ""], ["ORIGINAL_SHIPPING_QTY", "NUMBER", "", "Y", ""], ["ORDER_STATUS_QTY", "NUMBER", "", "Y", ""], ["ORDER_STATUS", "VARCHAR(TBD)", "", "Y", ""], ["BO_INSTRUCTION_CD", "VARCHAR(TBD)", "", "Y", ""], ["BO_RELEASE_DT", "DATE", "", "Y", ""], ["ORDER_GROUP", "VARCHAR(TBD)", "", "Y", ""], ["DIRECT_DELIVERY_CD", "VARCHAR(TBD)", "", "Y", ""], ["DIRECT_DELIVERY_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["CURRENCY_CD", "VARCHAR(TBD)", "", "Y", ""], ["LANDED_COST", "NUMBER", "", "Y", ""], ["NET_PRICE", "NUMBER", "", "Y", ""], ["SALES_PRICE", "NUMBER", "", "Y", ""], ["EXPORT_SALES_PRICE", "NUMBER", "", "Y", ""], ["SPECIAL_PRICE_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_DISCOUNT_CD", "VARCHAR(TBD)", "", "Y", ""], ["ITEM_DISCOUNT_RATE", "NUMBER", "", "Y", ""], ["FIRST_ALLOCATION_DT", "DATE", "", "Y", ""], ["BO_HISTORY_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_ERROR_CD", "VARCHAR(TBD)", "", "Y", ""], ["RA_CD", "VARCHAR(TBD)", "", "Y", ""], ["PENDING_ORDER_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_PORTION_CD", "VARCHAR(TBD)", "", "Y", ""], ["ORDER_STATUS_DT", "DATE", "", "Y", ""], ["SHIPPING_PROCESS_CTRL_CD", "VARCHAR(TBD)", "", "Y", ""], ["PROCUREMENT_PROCESS_CTRL_CD", "VARCHAR(TBD)", "", "Y", ""], ["DANGEROUS_GOODS_CLASS", "VARCHAR(TBD)", "", "Y", ""], ["CREATE_DEMAND_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["SPECIAL_CUSTOMER_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["POSS_TRANSMISSION_JUDG_FLAG", "VARCHAR(TBD)", "", "Y", ""], ["REGISTRANT_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_JOB_ID", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_OPERATION_ID", "VARCHAR(TBD)", "", "Y", ""], ["INTF_UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_DT", "TIMESTAMP", "", "Y", ""], ["CREATE_BY", "VARCHAR(TBD)", "", "Y", ""], ["UPDATE_DT", "TIMESTAMP", "", "Y", ""], ["UPDATE_BY", "VARCHAR(TBD)", "", "Y", ""]]


def src(t):
    return t + ' (DB Surrounding)'


def dst(t):
    return t + ' (NSP)'


def copy_blocks(t, cols):
    return [{"source": {"table": dst(t)}, "destination": {"table": dst(t), "operation": "Delete", "description": "All rows (full replace)"},
             "mappings": [{"dest_field": c[0], "description": "Row is deleted"} for c in cols]},
            {"source": {"table": src(t)}, "destination": {"table": dst(t), "operation": "Insert", "description": "Every source row"},
             "mappings": [{"source_field": c[0], "dest_field": c[0], "description": "Same value as the source"} for c in cols]}]


spec = {
 "doc_type": "batch",
 "header": header("X9", "Demand History and Order Control Sync to NSP"),
 "revisions": revisions(),
 "general": {
  "objective": [
   f"To replicate {H2} and {H3} from DB Surrounding to the tables with the same names in NSP.",
   "Each NSP table is fully replaced every run (delete - insert). In case any error occurs, the run is rolled back and NSP keeps the data of the last successful run."],
  "operation_flow": {"flow": {"direction": "TB", "nodes": [
     {"id": "a", "label": "Scheduler", "type": "event"},
     {"id": "b", "label": "Replace " + H2, "type": "process"},
     {"id": "c", "label": "Replace " + H3, "type": "process"},
     {"id": "d", "label": "Commit / roll back, Log", "type": "process"}],
    "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}]}},
  "inputs": [{"name": src(H2), "type": "DB", "description": "Demand history summary"},
             {"name": src(H3), "type": "DB", "description": "Order control (pre)"}],
  "outputs": [{"name": dst(H2), "type": "DB", "description": "if successful: same rows as the source"},
              {"name": dst(H3), "type": "DB", "description": "if successful: same rows as the source"},
              {"name": LOG, "type": "DB", "description": "One record per run with status SUCCESS / FAILED"}],
  "extra_tables": [
   {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
    "rows": [["-", "No parameter. All rows of both source tables are copied."]]},
   {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
    "rows": [["Trigger", "Scheduler set in the system master (schedule TBC)."]]}]
 },
 "func_flow": {
  "flow": {"direction": "TB", "nodes": [
     {"id": "p1", "label": "Start (scheduler)", "type": "process", "step": 1},
     {"id": "s2", "label": src(H2), "type": "db", "lane": "input"},
     {"id": "p2", "label": "Delete + insert " + H2, "type": "process", "step": 2},
     {"id": "d2", "label": dst(H2), "type": "db", "lane": "output"},
     {"id": "s3", "label": src(H3), "type": "db", "lane": "input"},
     {"id": "p3", "label": "Delete + insert " + H3, "type": "process", "step": 3},
     {"id": "d3", "label": dst(H3), "type": "db", "lane": "output"},
     {"id": "p4", "label": "Commit or roll back, record Log", "type": "process", "step": 4},
     {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
   "edges": [{"from": "p1", "to": "p2"}, {"from": "s2", "to": "p2"}, {"from": "p2", "to": "d2"}, {"from": "p2", "to": "p3"},
             {"from": "s3", "to": "p3"}, {"from": "p3", "to": "d3"}, {"from": "p3", "to": "p4"}, {"from": "p4", "to": "log"}]},
  "steps": [
   "The scheduler starts the batch.",
   f"Delete all rows of {dst(H2)} and insert all rows of {src(H2)} (same columns and values).",
   f"Delete all rows of {dst(H3)} and insert all rows of {src(H3)} (same columns and values).",
   "No error: commit. Error: roll back steps 2 and 3 (one transaction). Record the result in the Log. Exit."]
 },
 "data_map": {"blocks": copy_blocks(H2, H2_COLS) + copy_blocks(H3, H3_COLS) + [
  {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
   "mappings": [{"dest_field": "BATCH_ID", "description": "'H0202_H0253_SYNC'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                {"dest_field": "ROW_COUNT", "description": "Rows inserted per table (0 when FAILED)"}, {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                {"dest_field": "START_DT", "description": "Start date and time"}, {"dest_field": "END_DT", "description": "End date and time"}]}]},
 "func_desc_layout": "full",
 "func_desc": [
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Full replace of both tables (delete - insert); all columns are copied as they are, no conversion.",
    "Both tables are replaced in one transaction (all-or-nothing). When the run fails, NSP keeps the data of the last successful run.",
    "Schedule is set in the system master (TBC). Table structures: see Appendix."]}],
 "logging_messages": [
  {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": "H0202 / H0253 sync started.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": "H0202 / H0253 sync ended. Status <STATUS>, rows H0202 <COUNT1>, H0253 <COUNT2>.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Copy table", "cause": "Read from DB Surrounding or insert into NSP fails", "type": "Error", "msg_id": "LOG3", "message": "Cannot replicate <TABLE>: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
  {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}],
 "appendix_layout": "full",
 "appendix": [],
 "tables": [{"name": H2, "kind": "transaction", "proposed": False, "description": "Demand history summary replicated from DB Surrounding. " + NOTE, "columns": H2_COLS},
            {"name": H3, "kind": "transaction", "proposed": False, "description": "Order control (pre) replicated from DB Surrounding. " + NOTE, "columns": H3_COLS}]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
