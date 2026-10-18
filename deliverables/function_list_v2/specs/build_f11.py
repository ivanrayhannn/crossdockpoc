"""F11 Cancel Crossdock Customer Order Batch (new UISS-Batch, proposal from the cancel discussion of 16-Oct).
NSP never cancels an order: G-TOPAS cancels it (H0253 order status 2, replicated by F12). This batch applies the
cancel to the crossdock data of NSP: it releases the mapping that is not in a submitted ASN and detects a cancel
conflict when the cancelled qty is already in a submitted ASN (an ASN cannot be cancelled in NSP)."""
from build_h import CAN, CHAIN, SRC_T
from v2lib import batch_header, full_update, write
from h_tables import H0253_COLS  # noqa: E402
import asn_common as A  # noqa: E402

CTL = SRC_T
INS, PMAP = A.DRAFT, A.PRA_MAP
RES, LOG = 'TB_R_CROSSDOCK_CANCEL_RESULT', 'Log'
KEY = "CUSTOMER_CD + CUSTOMER_ORDER_NO + ORDER_DT + ORDER_TIME + DESTINATION_CD + DETAILED_ITEM_NO + SERIAL_NO"
RES_COLS = [
    ["CUSTOMER_CD", "VARCHAR(7)", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["CUSTOMER_ORDER_NO", "VARCHAR(8)", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["ORDER_DT", "DATE", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["ORDER_TIME", "VARCHAR(TBD)", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["DESTINATION_CD", "VARCHAR(7)", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["DETAILED_ITEM_NO", "VARCHAR(4)", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["SERIAL_NO", "VARCHAR(7)", "Y", "N", "Unique key of the cancelled line (H0253)"],
    ["ORDER_STATUS_DT", "DATE", "Y", "N", "Date of the status 2 (identifies one cancel of the line)"],
    ["PART_NO", "VARCHAR(15)", "", "N", "SHIPPING_PART_NO of the line"],
    ["LINE_QTY", "NUMBER(8)", "", "N", "Status 7 qty of the line before the cancel (NSP)"],
    ["CANCEL_QTY", "NUMBER(8)", "", "N", "ORDER_STATUS_QTY of the status 2 row"],
    ["QTY_IN_ASN", "NUMBER(8)", "", "N", "Qty of the line already in a submitted ASN (TB_R_INSTRUCTION with ASN_NO)"],
    ["RELEASED_QTY", "NUMBER(8)", "", "N", "Mapped qty released (rows of TB_R_INSTRUCTION without ASN_NO deleted)"],
    ["HOLD_FLAG", "VARCHAR(1)", "", "N", "HOLD_FLAG of the line at the time of the cancel"],
    ["RESULT", "VARCHAR(10)", "", "N", "'CANCELLED' / 'NO_HOLD' / 'CONFLICT'"],
    ["ASN_NO", "VARCHAR(TBD)", "", "Y", "ASN(s) that contain the line (CONFLICT); NULL otherwise"],
    ["MESSAGE", "VARCHAR(500)", "", "Y", "Explanation for the D/S team"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "Batch user ID"],
    ["CREATED_DT", "DATETIME", "", "N", "Processed date and time"]]
_T = {c[0]: c[1] for c in H0253_COLS}
for _c in RES_COLS:
    if _c[0] in _T and _c[0] != 'PART_NO':
        _c[1] = _T[_c[0]]
RES_TABLE = {"name": RES, "kind": "transaction", "proposed": True,
             "description": "New table: one record per cancelled crossdock line processed by F11 (also the exception list of the D/S team: RESULT = 'CONFLICT' / 'NO_HOLD'). Name and columns proposed.",
             "columns": RES_COLS}


def build():
    ctl_cols = H0253_COLS
    can_tbl = {"name": CAN, "kind": "transaction", "proposed": True, "description": "Rows of H0253 with ORDER_STATUS = '2' (F12).",
               "columns": [c for c in H0253_COLS if c[0] not in ('HOLD_FLAG', 'PO_MAPPED_FLAG')]}
    ctl_tbl = {"name": CTL, "kind": "transaction", "proposed": False, "description": "Rows of H0253 with ORDER_STATUS = '7' (F08), with the NSP columns HOLD_FLAG / PO_MAPPED_FLAG.",
               "columns": ctl_cols}
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [
                "To apply in NSP the cancel of crossdock customer order lines done in G-TOPAS (H0253 order status '2', replicated by F12). NSP does not cancel orders; it only holds them (HOLD_FLAG).",
                "Qty of the line that is not in a submitted ASN: the mapping is released (TB_R_INSTRUCTION rows without ASN No are deleted, MAPPED_QTY of the PO is reduced) so the PO qty can be used by the next orders.",
                "Qty already in a submitted ASN: the ASN is not changed (cannot be cancelled in NSP); the line is reported as a cancel conflict to the D/S team, who handles the shipped case at receiving.",
                "Rule (proposal): cancel qty <= line qty - qty in ASN, and the line is held in NSP before the cancel in G-TOPAS."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "Scheduler: after F12, before F08", "type": "event"},
                {"id": "b", "label": "Cancelled crossdock lines not yet processed", "type": "process"},
                {"id": "c", "label": "Qty in ASN vs cancel qty", "type": "decision"},
                {"id": "e", "label": "CANCELLED / NO_HOLD: release mapping", "type": "process"},
                {"id": "f", "label": "CONFLICT: release open mapping, report to D/S", "type": "process"},
                {"id": "g", "label": "Result, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "e", "label": "cancel <= line - ASN"},
                          {"from": "c", "to": "f", "label": "cancel > line - ASN"}, {"from": "e", "to": "g"}, {"from": "f", "to": "g"}]}},
            "inputs": [
                {"name": CAN, "type": "DB", "description": "Status 2 rows (F12): unique key, ORDER_STATUS_QTY = cancel qty, ORDER_STATUS_DT"},
                {"name": CTL, "type": "DB", "description": "Status 7 line before the cancel (F08 of the previous day): ORDER_STATUS_QTY, HOLD_FLAG, PO_MAPPED_FLAG"},
                {"name": INS, "type": "DB", "description": "Mapping rows of the line; ASN_NO filled = in a submitted ASN"},
                {"name": PMAP, "type": "DB", "description": "MAPPED_QTY per PO part"},
                {"name": RES, "type": "DB", "description": "Cancels already processed (not processed again)"}],
            "outputs": [
                {"name": INS, "type": "DB", "description": "Rows of the line without ASN_NO deleted"},
                {"name": PMAP, "type": "DB", "description": "MAPPED_QTY reduced by the released qty per PO"},
                {"name": CTL, "type": "DB", "description": "PO_MAPPED_FLAG = 'N' when no mapping row of the line is left"},
                {"name": RES, "type": "DB", "description": "One record per processed cancel (CANCELLED / NO_HOLD / CONFLICT)"},
                {"name": LOG, "type": "DB", "description": "Start, warnings (NO_HOLD, CONFLICT) and end messages"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["-", "No parameter."], ["User", "Batch user ID"]]},
                {"title": "Result Rule", "columns": [{"title": "Result", "width": 10}, {"title": "Condition", "width": 22}, {"title": "Action", "width": 18}],
                 "rows": [["CANCELLED", "CANCEL_QTY <= LINE_QTY - QTY_IN_ASN and HOLD_FLAG = 'Y'", "Release the open mapping"],
                          ["NO_HOLD", "CANCEL_QTY <= LINE_QTY - QTY_IN_ASN and HOLD_FLAG = 'N'", "Release the open mapping; warning to D/S (cancel without hold)"],
                          ["CONFLICT", "CANCEL_QTY > LINE_QTY - QTY_IN_ASN (part of the cancel is already in an ASN)", "Release the open mapping; ASN not changed; error to D/S"]]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", "Scheduler set in the system master (schedule TBC)."],
                          ["Order", CHAIN + " F11 runs only when F12 succeeded, and before F08 replaces the status 7 data."]]}]
        },
        "func_flow": {
            "flow": {"direction": "TB", "nodes": [
                {"id": "p1", "label": "Start (after F12)", "type": "process", "step": 1},
                {"id": "c", "label": f"{CAN} / {RES}", "type": "db", "lane": "input"},
                {"id": "p2", "label": "Select cancelled crossdock lines not processed", "type": "process", "step": 2},
                {"id": "k", "label": f"{CTL} / {INS}", "type": "db", "lane": "input"},
                {"id": "p3", "label": "Line qty, qty in ASN, open mapping", "type": "process", "step": 3},
                {"id": "d", "label": "Result rule", "type": "decision", "step": 4},
                {"id": "p5", "label": "Release open mapping", "type": "process", "step": 5},
                {"id": "o", "label": f"{INS} / {PMAP} / {CTL}", "type": "db", "lane": "output"},
                {"id": "p6", "label": "Write result, Log per line", "type": "process", "step": 6},
                {"id": "r", "label": RES, "type": "db", "lane": "output"},
                {"id": "p7", "label": "Next line / end, Log", "type": "process", "step": 7},
                {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
             "edges": [{"from": "p1", "to": "p2"}, {"from": "c", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "k", "to": "p3"},
                       {"from": "p3", "to": "d"}, {"from": "d", "to": "p5"}, {"from": "p5", "to": "o"}, {"from": "p5", "to": "p6"},
                       {"from": "p6", "to": "r"}, {"from": "p6", "to": "p7"}, {"from": "p7", "to": "log"}]},
            "steps": [
                "The scheduler starts the batch after F12 has finished successfully (job chain F12 -> F11 -> F08). Write LOG1.",
                {"text": f"Select the rows of {CAN} that are crossdock lines and not yet processed:", "children": [
                    f"Crossdock line: the same unique key ({KEY}) exists in {CTL} (status 7 data of the previous F08 run).",
                    f"Not processed: no record in {RES} with the same unique key and ORDER_STATUS_DT."]},
                {"text": "For each line, compute:", "children": [
                    f"LINE_QTY = ORDER_STATUS_QTY of the line in {CTL}; CANCEL_QTY = ORDER_STATUS_QTY of the status 2 row.",
                    f"QTY_IN_ASN = sum of QTY of the rows of the line in {INS} with ASN_NO filled.",
                    f"OPEN_QTY = sum of QTY of the rows of the line in {INS} without ASN_NO (mapped by [Create ASN], not submitted)."]},
                {"text": "Judge the result (see Result Rule):", "children": [
                    "CANCELLED: CANCEL_QTY <= LINE_QTY - QTY_IN_ASN and HOLD_FLAG = 'Y'.",
                    "NO_HOLD: CANCEL_QTY <= LINE_QTY - QTY_IN_ASN and HOLD_FLAG = 'N' (cancelled in G-TOPAS without hold in NSP). Write LOG3.",
                    "CONFLICT: CANCEL_QTY > LINE_QTY - QTY_IN_ASN (part of the cancelled qty is already in a submitted ASN). Write LOG4."]},
                {"text": "Release the open mapping of the line (all results):", "children": [
                    f"Delete the rows of the line in {INS} without ASN_NO. A Case List still open for these rows can no longer be submitted (the submit fails and the user creates the ASN again).",
                    f"Reduce MAPPED_QTY in {PMAP} by the qty of the deleted rows, per PO part.",
                    f"Set PO_MAPPED_FLAG = 'N' on the line in {CTL} when no row of the line is left in {INS}.",
                    "Rows with ASN_NO (submitted ASN) are never changed."]},
                f"Insert the result in {RES} (RELEASED_QTY = OPEN_QTY, ASN_NO for CONFLICT). Commit per line: an error stops only this line (LOG5), which is processed again by the next run.",
                "More lines: back to step 3. Else write LOG2 (counts per result). Exit."]
        },
        "data_map": {"blocks": [
            {"source": {"table": INS, "keys": [{"field": "Unique key of the line", "value": "Cancelled line"}, {"field": "ASN_NO", "value": "NULL"}]},
             "destination": {"table": INS, "operation": "Delete", "description": "Open mapping rows of the cancelled line"},
             "mappings": [{"dest_field": c[0], "description": "Row is deleted"} for c in A.DRAFT_COLS]},
            {"source": {"table": INS, "keys": [{"field": "PO_NO + MANIFEST_NO + MANIFEST_ITEM_NO", "value": "PO part of the deleted rows"}]},
             "destination": {"table": PMAP, "operation": "Update", "description": "PO parts of the deleted rows",
                             "keys": [{"field": "PO_NO + MANIFEST_NO + MANIFEST_ITEM_NO", "value": "PO part"}]},
             "mappings": full_update([{"dest_field": "MAPPED_QTY", "description": "MAPPED_QTY - sum of QTY of the deleted rows of this PO part"},
                                      {"dest_field": "CHANGED_BY", "description": "Batch user ID"},
                                      {"dest_field": "CHANGED_DT", "description": "Server system date-time"}], A.PRA_MAP_COLS)},
            {"source": {"table": INS, "keys": [{"field": "Unique key of the line", "value": "No row left"}]},
             "destination": {"table": CTL, "operation": "Update", "description": "Cancelled line without any mapping row left",
                             "keys": [{"field": KEY, "value": "Cancelled line"}]},
             "mappings": full_update([{"dest_field": "PO_MAPPED_FLAG", "description": "'N'"},
                                      {"dest_field": "UPDATE_BY", "description": "Batch user ID"},
                                      {"dest_field": "UPDATE_DT", "description": "Server system date-time"}], ctl_cols)},
            {"source": {"table": CAN}, "destination": {"table": RES, "operation": "Insert", "description": "One record per processed cancel"},
             "mappings": [{"source_field": k, "dest_field": k} for k in ("CUSTOMER_CD", "CUSTOMER_ORDER_NO", "ORDER_DT", "ORDER_TIME", "DESTINATION_CD", "DETAILED_ITEM_NO", "SERIAL_NO", "ORDER_STATUS_DT")]
                         + [{"source_field": "SHIPPING_PART_NO", "dest_field": "PART_NO"},
                            {"dest_field": "LINE_QTY", "description": f"ORDER_STATUS_QTY of the line in {CTL}"},
                            {"source_field": "ORDER_STATUS_QTY", "dest_field": "CANCEL_QTY"},
                            {"dest_field": "QTY_IN_ASN", "description": f"Sum of QTY with ASN_NO in {INS}"},
                            {"dest_field": "RELEASED_QTY", "description": "Sum of QTY of the deleted rows"},
                            {"dest_field": "HOLD_FLAG", "description": f"HOLD_FLAG of the line in {CTL}"},
                            {"dest_field": "RESULT", "description": "'CANCELLED' / 'NO_HOLD' / 'CONFLICT'"},
                            {"dest_field": "ASN_NO", "description": "ASN_NO(s) of the line for CONFLICT; else NULL"},
                            {"dest_field": "MESSAGE", "description": "Text of LOG3 / LOG4; NULL for CANCELLED"},
                            {"dest_field": "CREATED_BY", "description": "Batch user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date-time"}]},
            {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "Messages of the run"},
             "mappings": [{"dest_field": "BATCH_ID", "description": "'F11_CANCEL'"}, {"dest_field": "STATUS", "description": "SUCCESS / WARNING (NO_HOLD or CONFLICT) / ERROR"},
                          {"dest_field": "MESSAGE", "description": "LOG1 - LOG6"}, {"dest_field": "START_DT / END_DT", "description": "Start and end date-time"}]}]},
        "func_desc_layout": "full",
        "func_desc": [
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                "NSP never cancels a customer order and has no Cancel ASN. G-TOPAS cancels the order (status 2); this batch only applies the cancel to the crossdock data of NSP.",
                "Expected case (CANCELLED): the D/S team holds the line in NSP (F10) before the cancel in G-TOPAS, and cancels at most the qty not yet in an ASN. The released PO qty is taken by the next orders in the next F09 run (FIFO).",
                "NO_HOLD: the cancel came without hold in NSP. It is applied the same way and reported to the D/S team.",
                "CONFLICT: part of the cancelled qty is already in a submitted ASN (case shipped). The ASN stays as it is. The D/S team handles the case at receiving in G-TOPAS: allocate it to an open order with the same destination, otherwise move it to warehouse stock (refer prototype menu Cancel Order Simulation).",
                f"{RES} is the exception list for the D/S team (RESULT = NO_HOLD / CONFLICT); a screen for it is not in this scope (TBC). The messages are also in the Log (Log Monitoring).",
                "Option not in this draft (TBC): keep the released PO qty of a CONFLICT blocked until the D/S team closes the conflict, to avoid over-supply when the shipped case is allocated to another order before the next F08 run.",
                "Open points: partial cancel in G-TOPAS; one customer order line in more than one ASN (partial delivery); content of the case label (Customer Order No / destination)."]}],
        "logging_messages": [
            {"event": "Batch start", "cause": "After F12", "type": "Info", "msg_id": "LOG1", "message": "Cancel crossdock customer order started. <n> cancelled line(s) to process.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": "Cancel crossdock customer order ended. Cancelled <a>, no hold <b>, conflict <c>, error <d>.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Judge", "cause": "Cancelled in G-TOPAS without hold in NSP", "type": "Warning", "msg_id": "LOG3", "message": "Customer order <CUSTOMER_ORDER_NO> <PART_NO> cancelled without hold: <CANCEL_QTY> pcs, mapping released <RELEASED_QTY> pcs.", "action": {"system": "Continue.", "user": "D/S team checks the cancel."}},
            {"event": "Judge", "cause": "Cancel qty > qty not in ASN", "type": "Error", "msg_id": "LOG4", "message": "Cancel conflict <CUSTOMER_ORDER_NO> <PART_NO>: <CANCEL_QTY> pcs cancelled, <QTY_IN_ASN> pcs already in <ASN_NO>.", "action": {"system": "Release the open mapping; ASN not changed. Continue.", "user": "D/S team handles the shipped case at receiving."}},
            {"event": "Save", "cause": "Delete / update / insert of a line fails", "type": "Error", "msg_id": "LOG5", "message": "Cannot process the cancel of <CUSTOMER_ORDER_NO> <PART_NO>: <ERROR_DETAIL>.", "action": {"system": "Roll back the line; processed again by the next run.", "user": "User contact PIC if it persists"}},
            {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG6", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Stop. STATUS = ERROR. F08 is not started.", "user": "User contact PIC"}}],
        "appendix_layout": "full",
        "appendix": [],
        "tables": [RES_TABLE, can_tbl, ctl_tbl, A.DRAFT_TABLE, A.PRA_MAP_TABLE],
    }
    return write(batch_header('F11') | spec, 'F11')


if __name__ == '__main__':
    print(build())
