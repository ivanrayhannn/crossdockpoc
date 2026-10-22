"""XD08 Order Control Information to NSP Batch (ASN) and XD12 Order Control Information to NSP Batch (Cancel).
Decision 18-Oct (scenario file skenario_h0253.xlsx): the source TB_R_H0253_ORDER_CONTROL_PRE of DB Surrounding is
insert / update; a crossdock line starts with ORDER_STATUS 7 and can change to 6 (received / allocated) or 2 (reject /
cancel). A partial cancel splits the line into a new SERIAL_NO. NSP keeps ONE replicate table, updated by insert / update
(upsert) per unique key with the rows changed since the last run (INTF_UPDATE_DT):
  XD08: status 7 rows (insert new / update) and status 6 updates of known rows.
  XD12: status 2 rows of crossdock lines (insert split serial / update) + the other changed rows of the same line;
        UPD_STATUS = 'P' for XD11."""
from v2lib import batch_header, write
from h_tables import H0253_COLS  # noqa: E402  (path set by v2lib)

SRC_T = CTL = 'TB_R_H0253_ORDER_CONTROL_PRE'
SRC = SRC_T + ' (DB Surrounding)'
DST = CTL + ' (NSP)'
LOG = 'Log'
NOTE = ("Structure from the G-System I/F layout; physical names follow the existing table. Key (PK) = unique key of the I/F layout. "
        "NSP keeps the rows with status 7, 6 and 2 (insert / update); rows with status 6 / 2 are kept for tracking only (retention optional, TBC).")
CHAIN = "Job chain: XD12 -> XD11 -> XD08, after G-System has provided the data (1 time/day, 27:30)."
LINE_KEY = "CUSTOMER_CD + CUSTOMER_ORDER_NO + ORDER_DT + ORDER_TIME + DESTINATION_CD + DETAILED_ITEM_NO"
NSP_COLS = {"HOLD_FLAG", "PO_MAPPED_FLAG", "UPD_STATUS", "CREATE_DT", "CREATE_BY", "UPDATE_DT", "UPDATE_BY"}

# NSP table = H0253 columns + UPD_STATUS after PO_MAPPED_FLAG
CTL_COLS = []
for c in H0253_COLS:
    c = list(c)
    if c[0] == 'HOLD_FLAG':
        c[4] = "NSP column: hold by the D/S team in ASN Cross Dock Creation (XD10) ('Y' / 'N'); 'N' on insert, never changed by XD08 / XD12"
    if c[0] == 'PO_MAPPED_FLAG':
        c[4] = "NSP column: line mapped to a PO by [Create ASN] ('Y' / 'N'); 'N' on insert, never changed by XD08 / XD12"
    CTL_COLS.append(c)
    if c[0] == 'PO_MAPPED_FLAG':
        CTL_COLS.append(["UPD_STATUS", "VARCHAR(1)", "", "N",
                         "NSP column: '-' no cancel / 'P' cancel to be processed by XD11 (set by XD12) / 'D' processed by XD11"])
CTL_TABLE = {"name": CTL, "kind": "transaction", "proposed": False,
             "description": "Order control data, pre-order picking info (I/F H02-53, DVJO950) replicated from DB Surrounding by XD08 / XD12. " + NOTE
                            + " UPD_STATUS is a new NSP column (proposed).",
             "columns": CTL_COLS}

WATERMARK = "Last INTF_UPDATE_DT taken by the previous successful run of this batch (kept in the Log); first run: all rows"


def upsert_block(fid, rule_desc, cancel_desc):
    maps = []
    for c in CTL_COLS:
        n = c[0]
        if n in ('HOLD_FLAG', 'PO_MAPPED_FLAG'):
            maps.append({"dest_field": n, "description": "'N' on insert; not changed on update"})
        elif n == 'UPD_STATUS':
            maps.append({"dest_field": n, "description": cancel_desc})
        elif n in ('CREATE_DT', 'CREATE_BY'):
            maps.append({"dest_field": n, "description": "Batch system date-time / batch user ID on insert; not changed on update"})
        elif n in ('UPDATE_DT', 'UPDATE_BY'):
            maps.append({"dest_field": n, "description": "Batch system date-time / batch user ID"})
        else:
            maps.append({"source_field": n, "dest_field": n, "description": "Same value as the source (insert and update)"})
    return {"source": {"table": SRC, "keys": [{"field": "INTF_UPDATE_DT", "value": "> watermark"}, {"field": "ORDER_STATUS", "value": rule_desc}]},
            "destination": {"table": DST, "operation": "Insert / Update", "description": "Upsert per unique key (insert when the key is new, else update)",
                            "keys": [{"field": "Unique key (incl. SERIAL_NO)", "value": "Key of the source row"}]},
            "mappings": maps}


def log_block(fid):
    return {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
            "mappings": [{"dest_field": "BATCH_ID", "description": f"'{fid}_H0253'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                         {"dest_field": "ROW_COUNT", "description": "Rows inserted / updated (0 when FAILED)"},
                         {"dest_field": "WATERMARK", "description": "Max INTF_UPDATE_DT taken in this run (next watermark; only when SUCCESS)"},
                         {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                         {"dest_field": "START_DT / END_DT", "description": "Start and end date-time"}]}


def flow(fid, select_label):
    return {"flow": {"direction": "TB", "nodes": [
        {"id": "p1", "label": "Start (job chain)", "type": "process", "step": 1},
        {"id": "s", "label": SRC, "type": "db", "lane": "input"},
        {"id": "p2", "label": select_label, "type": "process", "step": 2},
        {"id": "p3", "label": "Insert new keys / update existing keys", "type": "process", "step": 3},
        {"id": "d", "label": DST, "type": "db", "lane": "output"},
        {"id": "p4", "label": "Commit or roll back, Log (watermark)", "type": "process", "step": 4},
        {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
        "edges": [{"from": "p1", "to": "p2"}, {"from": "s", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "p3", "to": "d"},
                  {"from": "p3", "to": "p4"}, {"from": "p4", "to": "log"}]}}


def spec_of(fid, objective, select_label, steps, blocks, desc, logs, extra_rows):
    return {
        "doc_type": "batch",
        "general": {
            "objective": objective,
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "Scheduler (job chain)", "type": "event"},
                {"id": "b", "label": select_label, "type": "process"},
                {"id": "c", "label": "Upsert into NSP, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}]}},
            "inputs": [{"name": SRC, "type": "DB", "description": "Order control data, pre-order picking info (I/F H02-53, DVJO950); insert / update table"},
                       {"name": DST, "type": "DB", "description": "Existing NSP rows (key check, NSP columns)"},
                       {"name": LOG, "type": "DB", "description": "Watermark of the last successful run"}],
            "outputs": [{"name": DST, "type": "DB", "description": "if successful: rows inserted / updated"},
                        {"name": LOG, "type": "DB", "description": "One record per run with status and watermark"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["Watermark", WATERMARK]] + extra_rows},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", "Scheduler set in the system master (schedule TBC)."], ["Order", CHAIN]]}]},
        "func_flow": dict(flow(fid, select_label), steps=steps),
        "data_map": {"blocks": blocks + [log_block(fid)]},
        "func_desc_layout": "full",
        "func_desc": desc,
        "logging_messages": logs,
        "appendix_layout": "full",
        "appendix": [],
        "tables": [CTL_TABLE],
    }


def logs(fid, what):
    return [
        {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": f"H0253 {what} sync started. Watermark <WATERMARK>.", "action": {"system": "Write the log.", "user": "-"}},
        {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": f"H0253 {what} sync ended. Status <STATUS>, inserted <INS>, updated <UPD>.", "action": {"system": "Write the log; save the new watermark when SUCCESS.", "user": "-"}},
        {"event": "Upsert", "cause": "Read from DB Surrounding or insert / update in NSP fails", "type": "Error", "msg_id": "LOG3", "message": f"Cannot replicate H0253 {what} rows: <ERROR_DETAIL>.", "action": {"system": "Roll back; watermark not changed (rows taken again next run). STATUS = FAILED.", "user": "User contact PIC"}},
        {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}]


def build():
    xd08 = spec_of(
        'XD08',
        [f"To keep {CTL} in NSP up to date with the crossdock customer order lines of G-System (replicated in DB Surrounding): rows with ORDER_STATUS = '7' "
         "are inserted (new key) or updated (existing key); rows that changed to '6' (received) are updated.",
         "Only the rows changed since the last successful run are taken (INTF_UPDATE_DT > watermark). Nothing is deleted, so the NSP columns "
         "HOLD_FLAG / PO_MAPPED_FLAG / UPD_STATUS keep their values.",
         "Rows with status '2' (cancel) are taken by XD12 and processed by XD11 before this batch runs."],
        "Rows changed since watermark: status 7 (all) and 6 (known keys)",
        ["The scheduler starts the batch after XD11 (job chain XD12 -> XD11 -> XD08). Write LOG1.",
         {"text": f"Read the rows of {SRC} with INTF_UPDATE_DT > watermark:", "children": [
             "ORDER_STATUS = '7': all rows (new crossdock lines, changed qty, split serials).",
             f"ORDER_STATUS = '6': only rows whose unique key already exists in {DST} (received / allocated; no further action in NSP).",
             "Other statuses are not taken; status '2' is taken by XD12."]},
         {"text": f"Upsert into {DST} per unique key (incl. SERIAL_NO):", "children": [
             "New key: insert all source columns; HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N', UPD_STATUS = '-'.",
             "Existing key: update all source columns; HOLD_FLAG, PO_MAPPED_FLAG and UPD_STATUS are not changed."]},
         "No error: commit, save the new watermark (max INTF_UPDATE_DT taken) in the Log, LOG2. Error: roll back, watermark not changed, LOG3. Exit."],
        [upsert_block('XD08', "'7' (all) / '6' (existing keys only)", "'-' on insert; not changed on update")],
        [{"type": "bullets", "marker": "-", "level": 0, "items": [
            "The source table is insert / update: a crossdock line starts with status 7 and can change to 6 (received / allocated) or 2 (reject / cancel). "
            "A partial cancel or receipt splits the line into a new SERIAL_NO (scenario file skenario_h0253.xlsx).",
            "Scenario 1 (normal): 14-Oct status 7, qty 8 -> 15-Oct the same row status 6, qty 8: XD08 updates the row; the line is no longer taken by XD09 (status 7 only).",
            "Only changed rows are read (INTF_UPDATE_DT > watermark); insert and update run in one transaction; the watermark is saved only when the run succeeds.",
            "Rows with status 6 / 2 stay in the table for tracking (retention optional, TBC).",
            "Read by XD09 (status 7 rows not mapped, not on hold), XD10 and XD11. Table structure: see Appendix."]}],
        logs('XD08', 'status 7 / 6'), [["Statuses", "'7' all rows; '6' existing keys only"]])
    xd12 = spec_of(
        'XD12',
        [f"To bring the cancels of crossdock customer order lines from G-System into {CTL} in NSP: rows with ORDER_STATUS = '2' of lines that exist in NSP "
         "are inserted (new split SERIAL_NO of a partial cancel) or updated (full cancel of the row), and marked UPD_STATUS = 'P' for XD11.",
         "In the same run the other changed rows of the same line are upserted too (e.g. the status 7 serial whose qty was reduced by the partial cancel), "
         "so XD11 sees the complete line. Only rows changed since the last successful run are taken (INTF_UPDATE_DT > watermark)."],
        "Status 2 rows of crossdock lines + other changed rows of the same lines",
        ["The scheduler starts the batch (first of the job chain XD12 -> XD11 -> XD08). Write LOG1.",
         {"text": f"Read the rows of {SRC} with INTF_UPDATE_DT > watermark and ORDER_STATUS = '2' whose line ({LINE_KEY}) exists in {DST}.", "children": [
             "Lines not in NSP (not crossdock) are ignored.",
             "Add the other rows of the same lines with INTF_UPDATE_DT > watermark (any status), so the whole line is current."]},
         {"text": f"Upsert into {DST} per unique key (incl. SERIAL_NO):", "children": [
             "Status 2 row, new key (partial cancel = new split serial): insert; HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N', UPD_STATUS = 'P'.",
             "Status 2 row, existing key (full cancel of the row): update the source columns; UPD_STATUS = 'P'; HOLD_FLAG / PO_MAPPED_FLAG not changed.",
             "Other rows of the line: update the source columns (e.g. status 7 qty 8 -> 6); NSP columns not changed."]},
         "No error: commit, save the new watermark in the Log, LOG2 (rows, lines). Error: roll back, watermark not changed, LOG3; XD11 is not started. Exit."],
        [upsert_block('XD12', "'2' of lines existing in NSP + other changed rows of these lines",
                      "'P' for status 2 rows (insert and update); other rows: '-' on insert, not changed on update")],
        [{"type": "bullets", "marker": "-", "level": 0, "items": [
            "Scenario 2 (partial cancel): 14-Oct one row status 7 qty 8 -> 15-Oct the row is split: serial A status 7 qty 6 (update) and serial B status 2 qty 2 (insert, UPD_STATUS 'P').",
            "Scenario 3 (full cancel): 14-Oct status 7 qty 8 -> 15-Oct the same row status 2 qty 8 (update, UPD_STATUS 'P').",
            "One table with XD08: no separate cancel table and no delete, so the NSP columns of a line are never lost.",
            "A cancel of qty already in a submitted ASN is normally blocked in G-System by the existing ASN feedback and by the SOP of the D/S team; "
            "if it still happens (abnormality), XD11 reports it as CONFLICT.",
            "Rows with status 2 stay in the table for tracking (retention optional, TBC). Table structure: see Appendix."]}],
        logs('XD12', 'status 2 (cancel)'), [["Statuses", "'2' of crossdock lines; other changed rows of the same lines"]])
    return [write(batch_header('XD08') | xd08, 'XD08'), write(batch_header('XD12') | xd12, 'XD12')]


if __name__ == '__main__':
    print('\n'.join(build()))
