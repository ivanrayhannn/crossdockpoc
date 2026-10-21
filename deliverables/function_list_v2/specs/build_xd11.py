"""XD11 Cancel Crossdock Customer Order Batch (new UISS-Batch).
NSP never cancels an order: G-System cancels it (H0253 order status 2). XD12 brings the status 2 rows into
TB_R_H0253_ORDER_CONTROL_PRE with CANCEL_STATUS 'P'. XD11 applies the cancel per line (all serials of the line,
because a partial cancel splits the line into a new SERIAL_NO): it releases the open mapping and reports a
CONFLICT when qty already in a submitted ASN is cancelled (abnormality: SOP not followed)."""
from build_h import CHAIN, CTL, CTL_COLS, CTL_TABLE, LINE_KEY
from v2lib import batch_header, full_update, write
from h_tables import H0253_COLS  # noqa: E402
import asn_common as A  # noqa: E402

INS, PMAP = A.DRAFT, A.PRA_MAP
RES, LOG = 'TB_R_CROSSDOCK_CANCEL_RESULT', 'Log'
KEYS = ("CUSTOMER_CD", "CUSTOMER_ORDER_NO", "ORDER_DT", "ORDER_TIME", "DESTINATION_CD", "DETAILED_ITEM_NO", "SERIAL_NO")
_T = {c[0]: c[1] for c in H0253_COLS}
RES_COLS = [[k, _T[k], "Y", "N", "Unique key of the cancelled row (status 2) of H0253"] for k in KEYS] + [
    ["ORDER_STATUS_DT", "DATE", "", "Y", "Date of the status 2"],
    ["PART_NO", "VARCHAR(15)", "", "N", "SHIPPING_PART_NO of the line"],
    ["CANCEL_QTY", "NUMBER(8)", "", "N", "Status 2 qty of the line processed in this run"],
    ["VALID_QTY", "NUMBER(8)", "", "N", "Qty of the line still valid after the cancel (status 7 + 6, all serials)"],
    ["QTY_IN_ASN", "NUMBER(8)", "", "N", "Qty of the line in a submitted ASN (TB_R_INSTRUCTION with ASN_NO)"],
    ["RELEASED_QTY", "NUMBER(8)", "", "N", "Open mapping released (rows of TB_R_INSTRUCTION without ASN_NO deleted)"],
    ["CONFLICT_QTY", "NUMBER(8)", "", "N", "QTY_IN_ASN - VALID_QTY when positive (shipped without order); else 0"],
    ["HOLD_FLAG", "VARCHAR(1)", "", "N", "HOLD_FLAG of the line at the time of the cancel (info only)"],
    ["RESULT", "VARCHAR(10)", "", "N", "'CANCELLED' / 'CONFLICT'"],
    ["ASN_NO", "VARCHAR(TBD)", "", "Y", "ASN(s) of the line for CONFLICT; else NULL"],
    ["MESSAGE", "VARCHAR(500)", "", "Y", "Explanation for the D/S team"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "Batch user ID"],
    ["CREATED_DT", "DATETIME", "", "N", "Processed date and time"]]
RES_TABLE = {"name": RES, "kind": "transaction", "proposed": True,
             "description": "New table: one record per cancelled row (status 2) processed by XD11, with the figures of its line; "
                            "also the exception list of the D/S team (RESULT = 'CONFLICT'). Name and columns proposed.",
             "columns": RES_COLS}


def build():
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [
                "To apply in NSP the cancel of crossdock customer order lines done in G-System (status '2', brought in by XD12 with CANCEL_STATUS 'P'). "
                "NSP does not cancel orders; a line can be cancelled with or without HOLD_FLAG = 'Y'.",
                "Per line (all SERIAL_NO of the line, because a partial cancel splits the line): the open mapping of the line (mapped by [Create ASN], not submitted) "
                "is released, so the remaining valid qty is pre-mapped again by XD09.",
                "Qty already in a submitted ASN cannot be cancelled: G-System blocks it by the existing ASN feedback and the D/S team follows the SOP. "
                "If it still happens (abnormality), the ASN is not changed and the line is reported as CONFLICT to the D/S team."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "Scheduler: after XD12, before XD08", "type": "event"},
                {"id": "b", "label": "Lines with CANCEL_STATUS 'P'", "type": "process"},
                {"id": "c", "label": "Release open mapping of the line", "type": "process"},
                {"id": "d", "label": "Qty in ASN > valid qty?", "type": "decision"},
                {"id": "e", "label": "CANCELLED", "type": "process"},
                {"id": "f", "label": "CONFLICT: report to D/S", "type": "process"},
                {"id": "g", "label": "CANCEL_STATUS 'D', result, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}, {"from": "d", "to": "e", "label": "No"},
                          {"from": "d", "to": "f", "label": "Yes"}, {"from": "e", "to": "g"}, {"from": "f", "to": "g"}]}},
            "inputs": [
                {"name": CTL, "type": "DB", "description": "Status 2 rows with CANCEL_STATUS 'P' (XD12) and all other rows of the same lines (status 7 / 6)"},
                {"name": INS, "type": "DB", "description": "Mapping rows of the line; ASN_NO filled = in a submitted ASN"},
                {"name": PMAP, "type": "DB", "description": "MAPPED_QTY per PO part"}],
            "outputs": [
                {"name": INS, "type": "DB", "description": "Open mapping rows of the line deleted"},
                {"name": PMAP, "type": "DB", "description": "MAPPED_QTY reduced by the released qty per PO"},
                {"name": CTL, "type": "DB", "description": "CANCEL_STATUS 'D' on the processed rows; PO_MAPPED_FLAG 'N' on rows of the line without mapping left"},
                {"name": RES, "type": "DB", "description": "One record per processed status 2 row (CANCELLED / CONFLICT)"},
                {"name": LOG, "type": "DB", "description": "Start, cancel per line, conflicts and end messages"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["-", "No parameter."], ["User", "Batch user ID"]]},
                {"title": "Line Figures", "columns": [{"title": "Name", "width": 12}, {"title": "Calculation (per line, all serials)", "width": 36}],
                 "rows": [["Line", LINE_KEY + " (unique key without SERIAL_NO)"],
                          ["CANCEL_QTY", "Sum of ORDER_STATUS_QTY of the status 2 rows with CANCEL_STATUS 'P'"],
                          ["VALID_QTY", "Sum of ORDER_STATUS_QTY of the rows with status 7 or 6"],
                          ["QTY_IN_ASN", f"Sum of QTY of the rows of the line in {INS} with ASN_NO"],
                          ["QTY_OPEN", f"Sum of QTY of the rows of the line in {INS} without ASN_NO"],
                          ["CONFLICT_QTY", "QTY_IN_ASN - VALID_QTY when positive, else 0"]]},
                {"title": "Result Rule", "columns": [{"title": "Result", "width": 10}, {"title": "Condition", "width": 20}, {"title": "Action", "width": 18}],
                 "rows": [["CANCELLED", "QTY_IN_ASN <= VALID_QTY (with or without hold)", "Open mapping released; valid qty mapped again by XD09"],
                          ["CONFLICT", "QTY_IN_ASN > VALID_QTY (abnormality: cancel of qty already in an ASN)", "Open mapping released; ASN not changed; error to D/S"]]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", "Scheduler set in the system master (schedule TBC)."],
                          ["Order", CHAIN + " XD11 runs only when XD12 succeeded."]]}]
        },
        "func_flow": {
            "flow": {"direction": "TB", "nodes": [
                {"id": "p1", "label": "Start (after XD12)", "type": "process", "step": 1},
                {"id": "c", "label": CTL, "type": "db", "lane": "input"},
                {"id": "p2", "label": "Lines with CANCEL_STATUS 'P'", "type": "process", "step": 2},
                {"id": "k", "label": INS, "type": "db", "lane": "input"},
                {"id": "p3", "label": "Line figures", "type": "process", "step": 3},
                {"id": "p4", "label": "Release open mapping", "type": "process", "step": 4},
                {"id": "o", "label": f"{INS} / {PMAP} / {CTL}", "type": "db", "lane": "output"},
                {"id": "d", "label": "Result rule", "type": "decision", "step": 5},
                {"id": "p6", "label": "CANCEL_STATUS 'D', result, Log per line", "type": "process", "step": 6},
                {"id": "r", "label": RES, "type": "db", "lane": "output"},
                {"id": "p7", "label": "Next line / end, Log", "type": "process", "step": 7},
                {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
             "edges": [{"from": "p1", "to": "p2"}, {"from": "c", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "k", "to": "p3"},
                       {"from": "p3", "to": "p4"}, {"from": "p4", "to": "o"}, {"from": "p4", "to": "d"}, {"from": "d", "to": "p6"},
                       {"from": "p6", "to": "r"}, {"from": "p6", "to": "p7"}, {"from": "p7", "to": "log"}]},
            "steps": [
                "The scheduler starts the batch after XD12 has finished successfully (job chain XD12 -> XD11 -> XD08). Write LOG1.",
                f"Select the lines ({LINE_KEY}) that have rows with ORDER_STATUS = '2' and CANCEL_STATUS = 'P' in {CTL}. Read all rows of these lines (every SERIAL_NO).",
                {"text": "For each line, compute the line figures (see Line Figures):", "children": [
                    "CANCEL_QTY (status 2 rows 'P'), VALID_QTY (status 7 + 6 rows), QTY_IN_ASN and QTY_OPEN from TB_R_INSTRUCTION."]},
                {"text": "Release the open mapping of the line (when QTY_OPEN > 0):", "children": [
                    f"Delete the rows of the line in {INS} without ASN_NO. A Case List still open for these rows can no longer be submitted (the submit fails; the user creates the ASN again).",
                    f"Reduce MAPPED_QTY in {PMAP} by the qty of the deleted rows, per PO part.",
                    f"Set PO_MAPPED_FLAG = 'N' on the status 7 rows of the line that have no row left in {INS}: their valid qty is pre-mapped again by the next XD09 run.",
                    "Rows with ASN_NO (submitted ASN) are never changed."]},
                {"text": "Judge the result (see Result Rule):", "children": [
                    "CANCELLED: QTY_IN_ASN <= VALID_QTY. Write LOG3.",
                    "CONFLICT: QTY_IN_ASN > VALID_QTY; CONFLICT_QTY pcs were shipped (or will be) without order. Write LOG4."]},
                f"Set CANCEL_STATUS = 'D' on the processed status 2 rows and insert one record per row in {RES} (with the line figures). Commit per line: an error stops only this line (LOG5); its rows stay 'P' and are processed by the next run.",
                "More lines: back to step 3. Else write LOG2 (counts per result). Exit."]
        },
        "data_map": {"blocks": [
            {"source": {"table": INS, "keys": [{"field": "Line", "value": "Line with cancel"}, {"field": "ASN_NO", "value": "NULL"}]},
             "destination": {"table": INS, "operation": "Delete", "description": "Open mapping rows of the line"},
             "mappings": [{"dest_field": c[0], "description": "Row is deleted"} for c in A.DRAFT_COLS]},
            {"source": {"table": INS, "keys": [{"field": "PO_NO + MANIFEST_NO + MANIFEST_ITEM_NO", "value": "PO part of the deleted rows"}]},
             "destination": {"table": PMAP, "operation": "Update", "description": "PO parts of the deleted rows",
                             "keys": [{"field": "PO_NO + MANIFEST_NO + MANIFEST_ITEM_NO", "value": "PO part"}]},
             "mappings": full_update([{"dest_field": "MAPPED_QTY", "description": "MAPPED_QTY - sum of QTY of the deleted rows of this PO part"},
                                      {"dest_field": "CHANGED_BY", "description": "Batch user ID"},
                                      {"dest_field": "CHANGED_DT", "description": "Server system date-time"}], A.PRA_MAP_COLS)},
            {"source": {"table": CTL, "keys": [{"field": "Line", "value": "Line with cancel"}]},
             "destination": {"table": CTL, "operation": "Update", "description": "Status 2 rows 'P' -> 'D'; status 7 rows without mapping left -> PO_MAPPED_FLAG 'N'",
                             "keys": [{"field": "Unique key (incl. SERIAL_NO)", "value": "Row of the line"}]},
             "mappings": full_update([{"dest_field": "CANCEL_STATUS", "description": "'D' for the processed status 2 rows; not changed for other rows"},
                                      {"dest_field": "PO_MAPPED_FLAG", "description": "'N' for status 7 rows of the line without mapping row left; else not changed"},
                                      {"dest_field": "UPDATE_BY", "description": "Batch user ID"},
                                      {"dest_field": "UPDATE_DT", "description": "Server system date-time"}], CTL_COLS)},
            {"source": {"table": CTL, "keys": [{"field": "ORDER_STATUS / CANCEL_STATUS", "value": "'2' / 'P'"}]},
             "destination": {"table": RES, "operation": "Insert", "description": "One record per processed status 2 row"},
             "mappings": [{"source_field": k, "dest_field": k} for k in KEYS + ("ORDER_STATUS_DT",)]
                         + [{"source_field": "SHIPPING_PART_NO", "dest_field": "PART_NO"},
                            {"dest_field": "CANCEL_QTY", "description": "Line figure"}, {"dest_field": "VALID_QTY", "description": "Line figure"},
                            {"dest_field": "QTY_IN_ASN", "description": "Line figure"}, {"dest_field": "RELEASED_QTY", "description": "Sum of QTY of the deleted rows"},
                            {"dest_field": "CONFLICT_QTY", "description": "Line figure"},
                            {"source_field": "HOLD_FLAG", "dest_field": "HOLD_FLAG", "description": "Info only"},
                            {"dest_field": "RESULT", "description": "'CANCELLED' / 'CONFLICT'"},
                            {"dest_field": "ASN_NO", "description": "ASN_NO(s) of the line for CONFLICT; else NULL"},
                            {"dest_field": "MESSAGE", "description": "Text of LOG3 / LOG4"},
                            {"dest_field": "CREATED_BY", "description": "Batch user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date-time"}]},
            {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "Messages of the run"},
             "mappings": [{"dest_field": "BATCH_ID", "description": "'XD11_CANCEL'"}, {"dest_field": "STATUS", "description": "SUCCESS / WARNING (CONFLICT) / ERROR"},
                          {"dest_field": "MESSAGE", "description": "LOG1 - LOG6"}, {"dest_field": "START_DT / END_DT", "description": "Start and end date-time"}]}]},
        "func_desc_layout": "full",
        "func_desc": [
            {"type": "heading", "text": "4.1 Scenarios (skenario_h0253.xlsx, part 52119BZV60, order ID1H4571, qty 8)"},
            {"type": "table", "level": 0, "row_lines": "all",
             "columns": [{"title": "Scenario", "width": 10}, {"title": "H0253 14-Oct -> 15-Oct", "width": 18}, {"title": "NSP (XD08 / XD12 / XD11)", "width": 24}],
             "rows": [["1 Normal", "Status 7 qty 8 -> same row status 6 qty 8", "XD08 updates the row (received). No cancel, XD11 not involved."],
                      ["2 Partial cancel", "Status 7 qty 8 -> serial A status 7 qty 6 + serial B status 2 qty 2", "XD12 updates A, inserts B ('P'). XD11: CANCEL 2, VALID 6; not in ASN -> CANCELLED; open mapping released, 6 pcs mapped again by XD09."],
                      ["3 Full cancel", "Status 7 qty 8 -> same row status 2 qty 8", "XD12 updates the row ('P'). XD11: CANCEL 8, VALID 0; not in ASN -> CANCELLED; open mapping released."],
                      ["4 Abnormality", "8 pcs already in a submitted ASN, then cancel (SOP not followed)", "XD11: QTY_IN_ASN 8 > VALID_QTY -> CONFLICT; ASN not changed; D/S handles the case at receiving."]]},
            {"type": "heading", "text": "4.2 Rules"},
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                "NSP never cancels a customer order and has no Cancel ASN. A line can be cancelled with or without hold; HOLD_FLAG is only recorded.",
                "The calculation is per line (all SERIAL_NO), because G-System splits a partially cancelled line into a new serial.",
                "Prevention of a cancel of qty in an ASN: existing ASN feedback to G-System + SOP of the D/S team. XD11 only detects the abnormality (CONFLICT).",
                "CONFLICT: the D/S team handles the shipped case at receiving in G-System: allocate it to an open order with the same destination, otherwise move it to warehouse stock (prototype menu Cancel Order Simulation).",
                f"{RES} is the exception list for the D/S team (RESULT = CONFLICT); a screen for it is not in this scope (TBC). The messages are also in the Log (Log Monitoring).",
                "Option not in this draft (TBC): keep the released PO qty of a CONFLICT blocked until the D/S team closes the conflict."]}],
        "logging_messages": [
            {"event": "Batch start", "cause": "After XD12", "type": "Info", "msg_id": "LOG1", "message": "Cancel crossdock customer order started. <n> line(s) with cancel.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": "Cancel crossdock customer order ended. Cancelled <a>, conflict <c>, error <d>.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Judge", "cause": "Cancel applied (qty in ASN <= valid qty)", "type": "Info", "msg_id": "LOG3", "message": "Customer order <CUSTOMER_ORDER_NO> <PART_NO> cancelled <CANCEL_QTY> pcs; valid <VALID_QTY> pcs; mapping released <RELEASED_QTY> pcs.", "action": {"system": "Continue.", "user": "-"}},
            {"event": "Judge", "cause": "Qty in ASN > valid qty (abnormality)", "type": "Error", "msg_id": "LOG4", "message": "Cancel conflict <CUSTOMER_ORDER_NO> <PART_NO>: <CONFLICT_QTY> pcs of <ASN_NO> have no order after the cancel.", "action": {"system": "Release the open mapping; ASN not changed. Continue.", "user": "D/S team handles the shipped case at receiving."}},
            {"event": "Save", "cause": "Delete / update / insert of a line fails", "type": "Error", "msg_id": "LOG5", "message": "Cannot process the cancel of <CUSTOMER_ORDER_NO> <PART_NO>: <ERROR_DETAIL>.", "action": {"system": "Roll back the line; rows stay 'P' and are processed by the next run.", "user": "User contact PIC if it persists"}},
            {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG6", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Stop. STATUS = ERROR. XD08 is not started.", "user": "User contact PIC"}}],
        "appendix_layout": "full",
        "appendix": [],
        "tables": [RES_TABLE, CTL_TABLE, A.DRAFT_TABLE, A.PRA_MAP_TABLE],
    }
    return write(batch_header('XD11') | spec, 'XD11')


if __name__ == '__main__':
    print(build())
