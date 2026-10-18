"""F08 Order Control Information to NSP Batch (ASN): replicated H0253 rows with ORDER_STATUS '7' (crossdock).
F12 Order Control Information to NSP Batch (Cancel): replicated H0253 rows with ORDER_STATUS '2' (cancel).
Both read TB_R_H0253_ORDER_CONTROL_PRE of DB Surrounding (replicated from G-TOPAS) and write separate NSP tables."""
from v2lib import batch_header, write
from h_tables import H0253_COLS  # noqa: E402  (path set by v2lib)

SRC_T = 'TB_R_H0253_ORDER_CONTROL_PRE'
SRC = SRC_T + ' (DB Surrounding)'
CAN = 'TB_R_H0253_ORDER_CANCEL_PRE'
LOG = 'Log'
NOTE = "Structure from the G-TOPAS I/F layout; physical names follow the existing table. Key (PK) = unique key of the I/F layout."
KEEP = {"HOLD_FLAG", "PO_MAPPED_FLAG"}
CHAIN = "Job chain (TBC): F12 -> F11 -> F08, after G-TOPAS has provided the data (1 time/day, 27:30)."


def h_spec(fid, status, dst_t, cols, keep, purpose, extra_obj, step2_extra, desc, proposed):
    dst = dst_t + ' (NSP)'
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [f"To replicate the rows of {SRC_T} (DB Surrounding) with ORDER_STATUS = '{status}' ({purpose}) into {dst_t} in NSP.",
                          "The NSP table is fully replaced every run (delete - insert). In case any error occurs, the run is rolled back and NSP keeps the data of the last successful run."]
                         + extra_obj,
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "Scheduler (job chain)", "type": "event"},
                {"id": "b", "label": f"Delete + insert {dst_t} (ORDER_STATUS = '{status}')", "type": "process"},
                {"id": "c", "label": "Commit / roll back, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}},
            "inputs": [{"name": SRC, "type": "DB", "description": f"Order control data, pre-order picking info (I/F H02-53, DVJO950); rows with ORDER_STATUS = '{status}'"}],
            "outputs": [{"name": dst, "type": "DB", "description": f"if successful: the source rows with ORDER_STATUS = '{status}'"},
                        {"name": LOG, "type": "DB", "description": "One record per run with status SUCCESS / FAILED"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["Order status", f"'{status}' ({purpose}); fixed in this batch"]]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", "Scheduler set in the system master (schedule TBC)."], ["Order", CHAIN]]}]},
        "func_flow": {
            "flow": {"direction": "TB", "nodes": [
                {"id": "p1", "label": "Start (scheduler)", "type": "process", "step": 1},
                {"id": "s", "label": SRC, "type": "db", "lane": "input"},
                {"id": "p2", "label": f"Delete all rows, insert source rows with ORDER_STATUS = '{status}'", "type": "process", "step": 2},
                {"id": "d", "label": dst, "type": "db", "lane": "output"},
                {"id": "p3", "label": "Commit or roll back, record Log", "type": "process", "step": 3},
                {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
             "edges": [{"from": "p1", "to": "p2"}, {"from": "s", "to": "p2"}, {"from": "p2", "to": "d"}, {"from": "p2", "to": "p3"}, {"from": "p3", "to": "log"}]},
            "steps": ["The scheduler starts the batch (job chain F12 -> F11 -> F08).",
                      f"Delete all rows of {dst} and insert the rows of {SRC} with ORDER_STATUS = '{status}' (same columns and values). " + step2_extra,
                      "No error: commit. Error: roll back step 2 (one transaction). Record the result in the Log. Exit."]},
        "data_map": {"blocks": [
            {"source": {"table": dst}, "destination": {"table": dst, "operation": "Delete", "description": "All rows (full replace)"},
             "mappings": [{"dest_field": x[0], "description": "Row is deleted"} for x in cols]},
            {"source": {"table": SRC, "keys": [{"field": "ORDER_STATUS", "value": f"'{status}'"}]},
             "destination": {"table": dst, "operation": "Insert", "description": f"Every source row with ORDER_STATUS = '{status}'"},
             "mappings": [{"dest_field": x[0], "description": "Value of the deleted NSP row with the same unique key; 'N' for a new key"} if x[0] in keep
                          else {"dest_field": x[0], "description": "Batch system date-time / batch user ID"} if x[0] in ('CREATE_DT', 'CREATE_BY', 'UPDATE_DT', 'UPDATE_BY') and dst_t == CAN
                          else {"source_field": x[0], "dest_field": x[0], "description": "Same value as the source"} for x in cols]},
            {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
             "mappings": [{"dest_field": "BATCH_ID", "description": f"'{fid}_H0253_{status}'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                          {"dest_field": "ROW_COUNT", "description": "Rows inserted (0 when FAILED)"}, {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                          {"dest_field": "START_DT", "description": "Start date and time"}, {"dest_field": "END_DT", "description": "End date and time"}]}]},
        "func_desc_layout": "full",
        "func_desc": [{"type": "bullets", "marker": "-", "level": 0, "items": desc}],
        "logging_messages": [
            {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": f"H0253 status {status} sync started.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": f"H0253 status {status} sync ended. Status <STATUS>, rows <ROW_COUNT>.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Copy table", "cause": "Read from DB Surrounding or insert into NSP fails", "type": "Error", "msg_id": "LOG3", "message": f"Cannot replicate H0253 status {status} into {dst_t}: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}},
            {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}],
        "appendix_layout": "full",
        "appendix": [],
        "tables": [{"name": dst_t, "kind": "transaction", "proposed": proposed,
                    "description": f"Rows of H0253 with ORDER_STATUS = '{status}' replicated from DB Surrounding. " + NOTE + ("" if not proposed else " Table name proposed."),
                    "columns": cols}]
    }
    return write(batch_header(fid) | spec, fid)


def build():
    keep_txt = ("HOLD_FLAG and PO_MAPPED_FLAG are NSP-only columns (set in ASN Cross Dock Creation F10): before the delete their values are kept "
                "per unique key and put back on the inserted rows; a new key gets 'N'.")
    f08 = h_spec('F08', '7', SRC_T, H0253_COLS, KEEP, 'cross dock orders, used for the ASN',
                 ["Only crossdock orders (status 7) are taken. Cancelled lines (status 2) are taken by F12 and processed by F11 before this batch runs."],
                 keep_txt,
                 ["Rows with ORDER_STATUS = '7' only; all columns are copied as they are, no conversion. " + keep_txt,
                  "A line cancelled in G-TOPAS leaves status 7 (fully or partly); F11 runs before this batch so that HOLD_FLAG and the status 7 qty before the cancel are still available.",
                  "Delete and insert run in one transaction (all-or-nothing). When the run fails, NSP keeps the data of the last successful run.",
                  "Read by F09 (Mapping Customer Order and PO) and F10 (ASN Cross Dock Creation). Table structure: see Appendix."],
                 False)
    can_cols = [c if c[0] not in ('CREATE_DT', 'CREATE_BY', 'UPDATE_DT', 'UPDATE_BY') else c for c in H0253_COLS if c[0] not in KEEP]
    f12 = h_spec('F12', '2', CAN, can_cols, set(), 'cancelled orders',
                 ["The table is read by F11 Cancel Crossdock Customer Order Batch, which processes the cancel of crossdock lines in NSP."],
                 "No NSP-only column: the cancel result is kept by F11 in its own table.",
                 ["Rows with ORDER_STATUS = '2' only; all source columns are copied as they are, no conversion. Lines of every order type are copied; F11 takes only the crossdock lines (TBC: filter crossdock lines already in this batch).",
                  f"Separate table from {SRC_T} (NSP), because F08 fully replaces that table with status 7 rows only.",
                  "Delete and insert run in one transaction (all-or-nothing). When the run fails, NSP keeps the data of the last successful run and F11 is not started.",
                  "Table structure: same columns as H0253 without HOLD_FLAG / PO_MAPPED_FLAG (see Appendix)."],
                 True)
    return [f08, f12]


if __name__ == '__main__':
    print('\n'.join(build()))
