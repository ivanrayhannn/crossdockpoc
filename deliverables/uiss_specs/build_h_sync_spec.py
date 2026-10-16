"""Spec builder for the replication batches of G-TOPAS tables (UISS-Batch, structure only, no sample data):
  X9  TB_R_H0202_DEMAND_HISTORY_SUM  -> X9_UISS_Batch_H0202DemandHistorySync.xlsx
  X10 TB_R_H0253_ORDER_CONTROL_PRE   -> X10_UISS_Batch_H0253OrderControlSync.xlsx
  X11 TB_M_H0125_DESTINATION (Destination Master) -> X11_UISS_Batch_H0125DestinationMasterSync.xlsx
Usage: build_h_sync_spec.py OUT.json H0202|H0253|H0125"""
import json, sys
from calc_common import LOG, header, revisions

from h_tables import H0125_COLS, H0202_COLS, H0253_COLS

NOTE = "Structure from the G-TOPAS I/F layout; physical names follow the existing table. Key (PK) = unique key of the I/F layout."

CFG = {"H0202": {"fid": "X9", "table": "TB_R_H0202_DEMAND_HISTORY_SUM", "title": "Demand History Summary (H0202) Sync to NSP",
                 "desc": "Demand history summary (I/F H02-02, DVJO250)", "cols": H0202_COLS, "kind": "transaction",
                 "freq": "G-TOPAS provides the data 1 time/day (26:00)."},
       "H0253": {"fid": "X10", "table": "TB_R_H0253_ORDER_CONTROL_PRE", "title": "Order Control Pre (H0253) Sync to NSP",
                 "desc": "Order control data, pre-order picking info (I/F H02-53, DVJO950)", "cols": H0253_COLS, "kind": "transaction",
                 "freq": "G-TOPAS provides the data 1 time/day (27:30)."},
       "H0125": {"fid": "X11", "table": "TB_M_H0125_DESTINATION", "title": "Destination Master (H0125) Sync to NSP",
                 "desc": "Destination master (I/F H01-25, DVJO820)", "cols": H0125_COLS, "kind": "master",
                 "freq": "G-TOPAS provides the data 1 time/week (21:30)."}}
c = CFG[sys.argv[2]]
T, COLS, KEY = c["table"], c["cols"], sys.argv[2]
# NSP-only columns of H0253 (set in ASN Crossdock Creation); they survive the full replace
KEEP = {"HOLD_FLAG", "PO_MAPPED_FLAG"} if KEY == "H0253" else set()
KEEP_TXT = ("HOLD_FLAG and PO_MAPPED_FLAG are NSP-only columns (set in ASN Crossdock Creation): before the delete their values are kept per unique key "
            "and put back on the inserted rows; a new key gets 'N'. Cancel is not done in NSP: the source sends the cancelled order with ORDER_STATUS '2' "
            "(crossdock orders have '7'); NSP only holds, so a cancel applies to lines already on hold (HOLD_FLAG = 'Y'). Lines with status '2' are not taken by X12.") if KEEP else ""

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
    "rows": [["Trigger", "Scheduler set in the system master (schedule TBC), after the data is available."], ["Source", c["freq"]]]}]
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
   f"Delete all rows of {DST} and insert all rows of {SRC} (same columns and values)." + (" " + KEEP_TXT if KEEP else ""),
   "No error: commit. Error: roll back step 2 (one transaction). Record the result in the Log. Exit."]
 },
 "data_map": {"blocks": [
  {"source": {"table": DST}, "destination": {"table": DST, "operation": "Delete", "description": "All rows (full replace)"},
   "mappings": [{"dest_field": x[0], "description": "Row is deleted"} for x in COLS]},
  {"source": {"table": SRC}, "destination": {"table": DST, "operation": "Insert", "description": "Every source row"},
   "mappings": [{"dest_field": x[0], "description": "Value of the deleted NSP row with the same unique key; 'N' for a new key"} if x[0] in KEEP
                else {"source_field": x[0], "dest_field": x[0], "description": "Same value as the source"} for x in COLS]},
  {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
   "mappings": [{"dest_field": "BATCH_ID", "description": f"'{KEY}_SYNC'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                {"dest_field": "ROW_COUNT", "description": "Rows inserted (0 when FAILED)"}, {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                {"dest_field": "START_DT", "description": "Start date and time"}, {"dest_field": "END_DT", "description": "End date and time"}]}]},
 "func_desc_layout": "full",
 "func_desc": [
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Full replace (delete - insert); all columns are copied as they are, no conversion." + (" " + KEEP_TXT if KEEP else ""),
    "Delete and insert run in one transaction (all-or-nothing). When the run fails, NSP keeps the data of the last successful run.",
    "Schedule is set in the system master (TBC). Table structure: see Appendix."]}],
 "logging_messages": [
  {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": f"{KEY} sync started.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": f"{KEY} sync ended. Status <STATUS>, rows <ROW_COUNT>.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Copy table", "cause": "Read from DB Surrounding or insert into NSP fails", "type": "Error", "msg_id": "LOG3", "message": f"Cannot replicate {T}: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
  {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}],
 "appendix_layout": "full",
 "appendix": [],
 "tables": [{"name": T, "kind": c["kind"], "proposed": False, "description": c["desc"] + " replicated from DB Surrounding. " + NOTE, "columns": COLS}]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
