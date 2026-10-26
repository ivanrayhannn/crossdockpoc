"""XD08 Order Control Information to NSP Batch (one batch for H0253, decided 23-Oct; XD12 is merged into it).
The source TB_R_H0253_ORDER_CONTROL_PRE of DB Surrounding is insert / update: a crossdock line starts with ORDER_STATUS 7 and can
change to 6 (received / allocated) or 2 (cancel); a partial cancel / receipt splits the line into a new SERIAL_NO. NSP keeps ONE
replicate table, upserted per unique key with the rows changed since the last run (INTF_UPDATE_DT):
  - ORDER_STATUS keeps the value of the first replication; a later status 6 / 2 of the source is written to UPD_STATUS;
  - every run releases all drafts of TB_R_INSTRUCTION (Create ASN not submitted);
  - a cancel of qty already in a submitted ASN is left for Change Order Number (XD11)."""
from v2lib import batch_header, write
from h_tables import H0253_COLS  # noqa: E402  (path set by v2lib)

SRC_T = CTL = 'TB_R_H0253_ORDER_CONTROL_PRE'
SRC = SRC_T + ' (DB Surrounding)'
DST = CTL + ' (NSP)'
INS, PMAP, LOG = 'TB_R_INSTRUCTION', 'TB_R_PRA_DAILY_ORDER_MAPPED', 'Log'
NOTE = ("Structure from the G-System I/F layout; physical names follow the existing table. Key (PK) = unique key of the I/F layout. "
        "Rows with UPD_STATUS 6 / 2 are kept for tracking (retention optional, TBC).")
CHAIN = "One batch (decided 23-Oct): runs after G-System has provided the data (1 time/day, 27:30); XD12 is merged into XD08."
LINE_KEY = "CUSTOMER_CD + CUSTOMER_ORDER_NO + ORDER_DT + ORDER_TIME + DESTINATION_CD + DETAILED_ITEM_NO"
NSP_COLS = {"HOLD_FLAG", "PO_MAPPED_FLAG", "UPD_STATUS", "CREATE_DT", "CREATE_BY", "UPDATE_DT", "UPDATE_BY"}
UPD_DESC = ("NSP column: status change in G-System after the first replication: NULL = no change (status 7) / '6' = received or allocated "
            "(source ORDER_STATUS 6) / '2' = cancelled (source ORDER_STATUS 2). Set by XD08; lines with UPD_STATUS are not taken by XD09")

# NSP table = H0253 columns + UPD_STATUS after PO_MAPPED_FLAG
CTL_COLS = []
for c in H0253_COLS:
    c = list(c)
    if c[0] == 'ORDER_STATUS':
        c[4] = c[4] + " In NSP: value of the first replication (normally '7'); a later change is written to UPD_STATUS"
    if c[0] == 'HOLD_FLAG':
        c[4] = "NSP column: hold by the D/S team in ASN Cross Dock Creation (XD10) ('Y' / 'N'); 'N' on insert, never changed by XD08"
    if c[0] == 'PO_MAPPED_FLAG':
        c[4] = ("NSP column: 'Y' when the whole line is in TB_R_INSTRUCTION ([Create ASN] XD10, Change Order Number XD11); 'N' on insert; "
                "set back to 'N' by XD08 when a draft of the line is released")
    CTL_COLS.append(c)
    if c[0] == 'PO_MAPPED_FLAG':
        CTL_COLS.append(["UPD_STATUS", "VARCHAR(1)", "", "Y", UPD_DESC])
CTL_TABLE = {"name": CTL, "kind": "transaction", "proposed": False,
             "description": "Order control data, pre-order picking info (I/F H02-53, DVJO950) replicated from DB Surrounding by XD08. " + NOTE
                            + " UPD_STATUS is a new NSP column (proposed).",
             "columns": CTL_COLS}

WATERMARK = "Last INTF_UPDATE_DT taken by the previous successful run of this batch (kept in the Log); first run: all rows"


def upsert_block():
    maps = []
    for c in CTL_COLS:
        n = c[0]
        if n in ('HOLD_FLAG', 'PO_MAPPED_FLAG'):
            maps.append({"dest_field": n, "description": "'N' on insert; not changed on update (PO_MAPPED_FLAG: refer the draft release)"})
        elif n == 'UPD_STATUS':
            maps.append({"dest_field": n, "description": "Insert: NULL when the source status is 7, else the source status ('6' / '2'). "
                                                        "Update: source ORDER_STATUS when it is '6' or '2'; not changed when '7'"})
        elif n == 'ORDER_STATUS':
            maps.append({"source_field": n, "dest_field": n, "description": "Insert: same value as the source; update: not changed (first value kept)"})
        elif n in ('CREATE_DT', 'CREATE_BY'):
            maps.append({"dest_field": n, "description": "Batch system date-time / batch user ID on insert; not changed on update"})
        elif n in ('UPDATE_DT', 'UPDATE_BY'):
            maps.append({"dest_field": n, "description": "Batch system date-time / batch user ID"})
        else:
            maps.append({"source_field": n, "dest_field": n, "description": "Same value as the source (insert and update)"})
    return {"source": {"table": SRC, "keys": [{"field": "INTF_UPDATE_DT", "value": "> watermark"},
                                              {"field": "ORDER_STATUS", "value": "'7' / '6' / '2' of crossdock lines"}]},
            "destination": {"table": DST, "operation": "Insert / Update", "description": "Upsert per unique key (insert when the key is new, else update)",
                            "keys": [{"field": "Unique key (incl. SERIAL_NO)", "value": "Key of the source row"}]},
            "mappings": maps}


RELEASE_BLOCKS = [
    {"source": f"{INS} (rows with ASN_NO NULL = drafts)", "destination": {"table": INS, "operation": "Delete",
     "description": "Every run: all drafts (Create ASN not submitted) are released, whatever changed", "keys": [{"field": "ASN_NO", "value": "IS NULL"}]},
     "mappings": [{"dest_field": "(row)", "description": "Deleted"}]},
    {"source": f"{INS} drafts (sum of QTY per PO line)", "destination": {"table": PMAP, "operation": "Update",
     "description": "Mapped qty of the released drafts given back", "keys": [{"field": "PO_NO + MANIFEST_NO + MANIFEST_ITEM", "value": "PO lines of the drafts"}]},
     "mappings": [{"dest_field": "MAPPED_QTY", "description": "- QTY of the released rows"}, {"dest_field": "CHANGED_BY / CHANGED_DT", "description": "Batch user ID / system date-time"}]},
    {"source": f"{INS} drafts (lines)", "destination": {"table": DST, "operation": "Update",
     "description": "Lines of the released drafts", "keys": [{"field": "Unique key (incl. SERIAL_NO)", "value": "Lines of the released rows"}]},
     "mappings": [{"dest_field": "PO_MAPPED_FLAG", "description": "'N'"}, {"dest_field": "UPDATE_BY / UPDATE_DT", "description": "Batch user ID / system date-time"}]},
]


def log_block():
    return {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run"},
            "mappings": [{"dest_field": "BATCH_ID", "description": "'XD08_H0253'"}, {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                         {"dest_field": "ROW_COUNT", "description": "Rows inserted / updated (0 when FAILED)"},
                         {"dest_field": "DRAFT_COUNT", "description": "Draft rows of TB_R_INSTRUCTION released"},
                         {"dest_field": "WATERMARK", "description": "Max INTF_UPDATE_DT taken in this run (next watermark; only when SUCCESS)"},
                         {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                         {"dest_field": "START_DT / END_DT", "description": "Start and end date-time"}]}


LOGS = [
    {"event": "Batch start", "cause": "Batch is called", "type": "Info", "msg_id": "LOG1", "message": "H0253 sync started. Watermark <WATERMARK>.", "action": {"system": "Write the log.", "user": "-"}},
    {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2",
     "message": "H0253 sync ended. Status <STATUS>, inserted <INS>, updated <UPD> (UPD_STATUS 6: <N6>, 2: <N2>), drafts released <DRAFTS>.",
     "action": {"system": "Write the log; save the new watermark when SUCCESS.", "user": "-"}},
    {"event": "Cancel after ASN", "cause": "A line with UPD_STATUS '2' has qty in a submitted ASN", "type": "Warning", "msg_id": "LOG5",
     "message": "<CUSTOMER_ORDER_NO> <PART_NO>: <QTY> pcs cancelled in <ASN_NO>; listed in Change Order Number (XD11).",
     "action": {"system": "Write the log; nothing is changed in the ASN.", "user": "D/S team: Change Order Number (XD11)."}},
    {"event": "Cancel qty check", "cause": "Cancelled qty of a line in a submitted ASN is not a multiple of pcs/case (should not happen in G-System)", "type": "Error", "msg_id": "LOG6",
     "message": "<CUSTOMER_ORDER_NO> <PART_NO>: cancelled qty <QTY> is not a multiple of pcs/case <PCS>.",
     "action": {"system": "Write the log (abnormality); the line is still listed in XD11.", "user": "D/S team checks with G-System."}},
    {"event": "Upsert", "cause": "Read from DB Surrounding, insert / update in NSP or draft release fails", "type": "Error", "msg_id": "LOG3", "message": "Cannot replicate H0253 rows: <ERROR_DETAIL>.", "action": {"system": "Roll back; watermark not changed (rows taken again next run). STATUS = FAILED.", "user": "User contact PIC"}},
    {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG4", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Roll back. STATUS = FAILED.", "user": "User contact PIC"}}]


def build():
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [
                f"To keep {CTL} in NSP up to date with the crossdock customer order lines of G-System (replicated in DB Surrounding), in one batch "
                "(decided 23-Oct; the former XD12 is merged into XD08): the rows changed since the last successful run are inserted (new key) or updated.",
                "ORDER_STATUS keeps the value of the first replication; a later change in G-System is written to UPD_STATUS: '6' received / allocated, "
                "'2' cancelled. Lines with UPD_STATUS are not taken by XD09.",
                "Every run releases all drafts of TB_R_INSTRUCTION (Create ASN done, Submit not done): the cases come back in the delivery plan of XD10.",
                "A cancel of qty already in a submitted ASN is not changed by the batch: it is listed in Change Order Number (XD11) for the D/S team."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "Scheduler (daily)", "type": "event"},
                {"id": "b", "label": "Rows changed since watermark", "type": "process"},
                {"id": "c", "label": "Upsert, UPD_STATUS", "type": "process"},
                {"id": "d", "label": "Release all drafts, check cancels in ASN, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}]}},
            "inputs": [{"name": SRC, "type": "DB", "description": "Order control data, pre-order picking info (I/F H02-53, DVJO950); insert / update table"},
                       {"name": DST, "type": "DB", "description": "Existing NSP rows (key check, NSP columns)"},
                       {"name": INS, "type": "DB", "description": "Drafts (ASN_NO NULL) and submitted rows (cancel check)"},
                       {"name": LOG, "type": "DB", "description": "Watermark of the last successful run"}],
            "outputs": [{"name": DST, "type": "DB", "description": "Rows inserted / updated; PO_MAPPED_FLAG 'N' for the lines of released drafts"},
                        {"name": INS, "type": "DB", "description": "Draft rows deleted"},
                        {"name": PMAP, "type": "DB", "description": "MAPPED_QTY of the released drafts given back"},
                        {"name": LOG, "type": "DB", "description": "One record per run with status, counts and watermark; LOG5 / LOG6 per cancel in an ASN"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["Watermark", WATERMARK], ["Statuses", "'7' / '6' / '2' of crossdock lines; '6' / '2' go to UPD_STATUS"]]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", "Daily scheduler after G-System has provided the data (27:30); auto retry 3 times."], ["Order", CHAIN]]}]},
        "func_flow": {"flow": {"direction": "TB", "nodes": [
            {"id": "p1", "label": "Start (scheduler)", "type": "process", "step": 1},
            {"id": "s", "label": SRC, "type": "db", "lane": "input"},
            {"id": "p2", "label": "Rows changed since watermark", "type": "process", "step": 2},
            {"id": "p3", "label": "Insert new keys / update existing keys, UPD_STATUS", "type": "process", "step": 3},
            {"id": "d", "label": DST, "type": "db", "lane": "output"},
            {"id": "p4", "label": "Release all drafts", "type": "process", "step": 4},
            {"id": "i", "label": f"{INS} / {PMAP}", "type": "db", "lane": "output"},
            {"id": "p5", "label": "Check cancels in submitted ASNs", "type": "process", "step": 5},
            {"id": "p6", "label": "Commit or roll back, Log (watermark)", "type": "process", "step": 6},
            {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
            "edges": [{"from": "p1", "to": "p2"}, {"from": "s", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "p3", "to": "d"}, {"from": "p3", "to": "p4"},
                      {"from": "p4", "to": "i"}, {"from": "p4", "to": "p5"}, {"from": "p5", "to": "p6"}, {"from": "p6", "to": "log"}]},
            "steps": [
                "The scheduler starts the batch (daily, after G-System has provided the data). Write LOG1.",
                {"text": f"Read the rows of {SRC} with INTF_UPDATE_DT > watermark (crossdock lines, ORDER_STATUS '7', '6' or '2').", "children": [
                    "New crossdock lines, changed qty, split serials (partial cancel / receipt) and status changes."]},
                {"text": f"Upsert into {DST} per unique key (incl. SERIAL_NO):", "children": [
                    "New key: insert all source columns; HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'; UPD_STATUS = NULL when the source status is '7', else the source status.",
                    "Existing key: update the source columns except ORDER_STATUS (first value kept); UPD_STATUS = source ORDER_STATUS when it is '6' or '2'; "
                    "HOLD_FLAG / PO_MAPPED_FLAG not changed."]},
                {"text": f"Release all drafts of {INS} (rows with ASN_NO NULL), whatever changed:", "children": [
                    f"Delete the rows; MAPPED_QTY of {PMAP} - their qty; PO_MAPPED_FLAG = 'N' on their lines.",
                    "The cases come back in the delivery plan of XD10; the supplier ticks them again and creates the ASN again (lines with UPD_STATUS are no longer taken)."]},
                {"text": f"Check the lines with UPD_STATUS '2' that have rows in {INS} with ASN_NO (cancel of qty in a submitted ASN):", "children": [
                    "Write LOG5 per line and ASN; the line is listed in Change Order Number (XD11). Nothing is changed in the ASN.",
                    "Cancelled qty not a multiple of pcs/case: LOG6 (abnormality)."]},
                "No error: commit, save the new watermark (max INTF_UPDATE_DT taken) in the Log, LOG2. Error: roll back, watermark not changed, LOG3. Exit."]},
        "data_map": {"blocks": [upsert_block()] + RELEASE_BLOCKS + [log_block()]},
        "func_desc_layout": "full",
        "func_desc": [{"type": "bullets", "marker": "-", "level": 0, "items": [
            "One batch for H0253 (decided 23-Oct): the former XD08 (status 7 / 6) and XD12 (status 2) are merged; the old XD11 cancel batch is replaced by "
            "the screen Change Order Number (XD11).",
            "The source table is insert / update: a crossdock line starts with status 7 and can change to 6 (received / allocated) or 2 (cancel). "
            "A partial cancel or receipt splits the line into a new SERIAL_NO (scenario files skenario_h0253.xlsx, simulasi_asn.xlsx).",
            "UPD_STATUS: NULL = status 7 (no change); '6' = received / allocated in G-System; '2' = cancelled in G-System. ORDER_STATUS of NSP keeps the first value.",
            "Example (simulasi_asn.xlsx): 16-Oct CO-14101 / CO-14102 inserted (UPD_STATUS NULL); 17-Oct CO-14101 → UPD_STATUS 6 (received), CO-14102 → UPD_STATUS 2 "
            "(cancelled while on hold, no ASN: nothing else to do); 19-Oct CO-14104 (middle row of order date 17-Oct) → UPD_STATUS 2 although in case 3 of ASN0003 "
            "→ listed in XD11; 21-Oct CO-14111 → UPD_STATUS 6 without ASN (candidate for the replacement).",
            "Drafts: every run deletes all TB_R_INSTRUCTION rows with ASN_NO NULL (Create ASN not submitted), gives the mapped qty back and sets PO_MAPPED_FLAG 'N'; "
            "rows with ASN_NO are never deleted. [Submit ASN] of XD10 re-checks the draft too.",
            "Only changed rows are read (INTF_UPDATE_DT > watermark); upsert and draft release run in one transaction; the watermark is saved only when the run succeeds.",
            "Read by XD09 (lines with UPD_STATUS NULL, not mapped, not on hold), XD10 and XD11. Table structure: see Appendix."]}],
        "logging_messages": LOGS,
        "appendix_layout": "full",
        "appendix": [],
        "tables": [CTL_TABLE],
    }
    return [write(batch_header('XD08') | spec, 'XD08')]


if __name__ == '__main__':
    print('\n'.join(build()))
