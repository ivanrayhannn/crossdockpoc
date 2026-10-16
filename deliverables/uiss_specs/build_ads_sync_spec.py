"""Spec for UISS_Batch_ActualDemandSummarySync.xlsx (UISS-Batch, Crossdock - Actual Demand Summary Sync to Supplier System)."""
import json, sys
from calc_common import ADS, ADS_COLS, ADS_TABLE, LOG, SYSM_NOTE, header, revisions

SRC = ADS + ' (DB Surrounding)'
DST = ADS + ' (Supplier System)'

SAMPLE = {
 "title": "Sample Input", "heading": "Sample data - Actual Demand Summary Sync to Supplier System",
 "intro": ["Rows taken from the reference file 20261013_tb_r_actual_demand_summary_since_january-2026.xlsx (part 52119BZV60).",
           "The batch copies every row of the source table; the Supplier System table is emptied first (delete - insert)."],
 "sections": [
  {"title": "A. Source rows in DB Surrounding (excerpt)",
   "columns": ["GROUPING_BUYER_CD", "GROUPING_PD_CD", "ORDER_TYPE_GROUP", "DEMAND_MONTH_YEAR", "PART_NO", "MAD", "DAD"],
   "widths": [18, 15, 17, 18, 14, 10, 8],
   "rows": [["9722D", "10", "N", "202604", "52119BZV60", 239, "-"],
            ["98111", "10", "N", "202604", "52119BZV60", 156.17, "-"],
            ["96182", "01", "N", "202604", "52119BZV60", 77.33, "-"],
            ["97153", "10", "N", "202604", "52119BZV60", 23.17, "-"],
            ["98111", "10", "S", "202604", "52119BZV60", 2, "-"],
            ["9722D", "10", "S", "202604", "52119BZV60", 1, "-"]]},
  {"title": "B. Scenarios", "columns": ["No", "Scenario", "Expected result"], "widths": [6, 50, 60],
   "rows": [["N1", "Monthly run, source has 349,225 rows", "Supplier System table emptied, 349,225 rows inserted. Log STATUS = SUCCESS."],
            ["N2", "A row was deleted in the source since the last run", "The row no longer exists in Supplier System (full replace)."],
            ["E1", "DB Surrounding cannot be reached", "Rolled back: Supplier System keeps the data of the last successful run. Log STATUS = FAILED."],
            ["E2", "Insert fails in the middle of the run", "Rolled back (delete and insert in one transaction). Log STATUS = FAILED."]]}]}

spec = {
 "doc_type": "batch",
 "header": header("X5", "Actual Demand Summary Sync to Supplier System"),
 "revisions": revisions(),
 "general": {
  "objective": [
   f"To replicate {ADS} from DB Surrounding to the table with the same name in Supplier System, so the DAD Volume Calculation and the Mapping Destination Calculation read the actual demand inside Supplier System.",
   "The Supplier System table is fully replaced every run (delete - insert). In case any error occurs, the run is rolled back and Supplier System keeps the data of the last successful run."],
  "operation_flow": {"flow": {"direction": "TB", "nodes": [
     {"id": "a", "label": "Scheduler (monthly)", "type": "event"},
     {"id": "b", "label": "Read source table", "type": "process"},
     {"id": "c", "label": "Delete Supplier System table + insert all rows", "type": "process"},
     {"id": "d", "label": "Success?", "type": "decision"},
     {"id": "e", "label": "Commit, Log SUCCESS", "type": "process"},
     {"id": "f", "label": "Roll back, Log FAILED", "type": "process"}],
    "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"},
              {"from": "d", "to": "e", "label": "Yes"}, {"from": "d", "to": "f", "label": "No"}]}},
  "inputs": [{"name": SRC, "type": "DB", "description": "All rows of the actual demand summary"}],
  "outputs": [{"name": DST, "type": "DB", "description": "if successful: same rows as the source (delete - insert)"},
              {"name": LOG, "type": "DB", "description": "One record per run with status SUCCESS / FAILED"}],
  "extra_tables": [
   {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
    "rows": [["-", "No parameter. All rows of the source table are copied."]]},
   {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
    "rows": [["Trigger", "Scheduler set in the system master: monthly (date and time TBC)."],
             ["Order", "Must finish before the DAD Volume Calculation runs."]]}]
 },
 "func_flow": {
  "flow": {"direction": "TB", "nodes": [
     {"id": "p1", "label": "Start (scheduler)", "type": "process", "step": 1},
     {"id": "src", "label": SRC, "type": "db", "lane": "input"},
     {"id": "p2", "label": "Read all source rows", "type": "process", "step": 2},
     {"id": "p3", "label": "Delete all rows of Supplier System table", "type": "process", "step": 3},
     {"id": "p4", "label": "Insert all rows", "type": "process", "step": 4},
     {"id": "dst", "label": DST, "type": "db", "lane": "output"},
     {"id": "d", "label": "Any error?", "type": "decision", "step": 5},
     {"id": "p6", "label": "Commit", "type": "process", "step": 6},
     {"id": "p7", "label": "Roll back", "type": "process", "step": 6},
     {"id": "p8", "label": "Record result in Log", "type": "process", "step": 7},
     {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
   "edges": [{"from": "p1", "to": "p2"}, {"from": "src", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "p3", "to": "p4"},
             {"from": "p4", "to": "dst"}, {"from": "p4", "to": "d"}, {"from": "d", "to": "p6", "label": "No"},
             {"from": "d", "to": "p7", "label": "Yes"}, {"from": "p6", "to": "p8"}, {"from": "p7", "to": "p8"}, {"from": "p8", "to": "log"}]},
  "steps": [
   "The scheduler starts the batch (monthly, set in the system master).",
   f"Read all rows of {SRC}.",
   f"Delete all rows of {DST}.",
   "Insert every source row with the same column values (see Data Map).",
   "Check whether any error occurred during steps 2 to 4.",
   {"text": "No error: commit. Error: roll back steps 3 and 4.",
    "children": ["Delete and insert run in one transaction, so a failed run never leaves the Supplier System table empty or half filled."]},
   "Record the result (SUCCESS / FAILED, row count, error message) in the Log. Exit."]
 },
 "data_map": {"blocks": [
  {"source": {"table": DST}, "destination": {"table": DST, "operation": "Delete", "description": "All rows (full replace)"},
   "mappings": [{"dest_field": c[0], "description": "Row is deleted"} for c in ADS_COLS]},
  {"source": {"table": SRC}, "destination": {"table": DST, "operation": "Insert", "description": "Every source row"},
   "mappings": [{"source_field": c[0], "dest_field": c[0], "description": "Same value as the source"} for c in ADS_COLS]},
  {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
   "mappings": [{"dest_field": "BATCH_ID", "description": "'ADS_SYNC'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                {"dest_field": "ROW_COUNT", "description": "Rows inserted (0 when FAILED)"}, {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                {"dest_field": "START_DT", "description": "Start date and time"}, {"dest_field": "END_DT", "description": "End date and time"}]}]},
 "func_desc_layout": "two",
 "func_desc": [
  {"type": "text", "level": 0, "text": f"This batch copies the actual demand summary from DB Surrounding into Supplier System once a month. {SYSM_NOTE}"},
  {"type": "bullets", "marker": "-", "level": 0, "items": [
    "Full replace: all rows of the Supplier System table are deleted and all source rows are inserted (delete - insert). No row is compared or merged.",
    "All columns are copied with the same names and values; no conversion is done.",
    "Delete and insert run in one transaction (all-or-nothing). When the run fails, Supplier System keeps the data of the last successful run.",
    "The batch must finish before the DAD Volume Calculation starts."]},
  {"type": "column_break"},
  {"type": "heading", "text": "Columns used by Crossdock"},
  {"type": "table", "level": 0, "row_lines": "all", "columns": [{"title": "Column", "width": 18}, {"title": "Used by", "width": 28}], "rows": [
    ["GROUPING_BUYER_CD + GROUPING_PD_CD", "Mapping Destination Calculation (7-digit destination code)"],
    ["ORDER_TYPE_GROUP", "N and S are summed"],
    ["DEMAND_MONTH_YEAR", "Range of months (system master)"],
    ["PART_NO", "Join to TB_M_PART_CANDIDATE"],
    ["MAD", "DAD Volume Calculation and Mapping Destination Calculation"]]}],
 "logging_messages": [
  {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": "Actual demand summary sync started.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": "Actual demand summary sync ended. Status <STATUS>, rows <ROW_COUNT>.", "action": {"system": "Write the log.", "user": "-"}},
  {"event": "Read source", "cause": "DB Surrounding cannot be reached or read", "type": "Error", "msg_id": "LOG3", "message": "Cannot read TB_R_ACTUAL_DEMAND_SUMMARY from DB Surrounding: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
  {"event": "Insert", "cause": "Insert into the Supplier System table fails", "type": "Error", "msg_id": "LOG4", "message": "Cannot insert TB_R_ACTUAL_DEMAND_SUMMARY into Supplier System: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
  {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG5", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}],
 "appendix_layout": "full",
 "appendix": [{"type": "text", "level": 0, "text": "Sample rows and scenarios: see sheet Sample Input."}],
 "sample_sheet": SAMPLE,
 "tables": [ADS_TABLE]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
