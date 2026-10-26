"""XD11 Change Order Number Screen (D/S team, sub menu of ASN; decided 23-Oct; replaces the former XD11 Cancel Crossdock Customer Order Batch).
A line of the H0253 replicate gets UPD_STATUS '2' from XD08 when G-System cancels it. When qty of the line is already in a submitted
ASN (rows of TB_R_INSTRUCTION with ASN_NO), the D/S team moves the cancelled qty to other lines of the same part with UPD_STATUS '6'
(received in G-System), PO_MAPPED_FLAG 'N' and no ASN, oldest Customer Order Date first. Several lines and another destination are
allowed as long as their qty adds up to the cancelled qty. The qty is taken from the last case backwards; a row of TB_R_INSTRUCTION is
split when needed (record only: the shipped case does not change). Every change is kept in TB_H_CROSSDOCK_ORDER_CHANGE."""
from build_h import CTL
from v2lib import set_header, write

INS, HIS = 'TB_R_INSTRUCTION', 'TB_H_CROSSDOCK_ORDER_CHANGE'
IMG = 'deliverables/uiss_screens/asn_crossdock/'
BUTTONS = ['Expand (replacement)', 'Candidate (check box)', 'Change Order Number', 'Yes / No']

HIS_TABLE = {"name": HIS, "kind": "history", "proposed": True,
             "description": "New history table (replaces TB_R_CROSSDOCK_CANCEL_RESULT): one record per moved piece of qty (ASN case x cancelled line x "
                            "replacement line) of Change Order Number (XD11). Name and columns proposed.",
             "columns": [
                 ["HIST_ID", "BIGINT", "Y", "N", "Running number"],
                 ["ASN_NO", "VARCHAR(15)", "", "N", "ASN of the case"],
                 ["CASE_NO", "VARCHAR(9)", "", "N", "Case of the moved qty"],
                 ["PART_NO", "VARCHAR(15)", "", "N", "Part number"],
                 ["FROM_CUSTOMER_CD", "VARCHAR(7)", "", "N", "Cancelled line: CUSTOMER_CD"],
                 ["FROM_CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "Cancelled line: CUSTOMER_ORDER_NO"],
                 ["FROM_ORDER_DT", "DATE", "", "N", "Cancelled line: ORDER_DT"],
                 ["FROM_DESTINATION_CD", "VARCHAR(7)", "", "N", "Cancelled line: DESTINATION_CD"],
                 ["FROM_DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "Cancelled line: DETAILED_ITEM_NO"],
                 ["FROM_SERIAL_NO", "VARCHAR(7)", "", "N", "Cancelled line: SERIAL_NO of the status 2 row"],
                 ["TO_CUSTOMER_CD", "VARCHAR(7)", "", "N", "Replacement line: CUSTOMER_CD"],
                 ["TO_CUSTOMER_ORDER_NO", "VARCHAR(8)", "", "N", "Replacement line: CUSTOMER_ORDER_NO"],
                 ["TO_ORDER_DT", "DATE", "", "N", "Replacement line: ORDER_DT"],
                 ["TO_DESTINATION_CD", "VARCHAR(7)", "", "N", "Replacement line: DESTINATION_CD (may differ from the cancelled line)"],
                 ["TO_DETAILED_ITEM_NO", "VARCHAR(4)", "", "N", "Replacement line: DETAILED_ITEM_NO"],
                 ["TO_SERIAL_NO", "VARCHAR(7)", "", "N", "Replacement line: SERIAL_NO"],
                 ["QTY", "NUMBER(8)", "", "N", "Moved qty"],
                 ["FROM_INSTRUCTION_ID", "BIGINT", "", "N", "Row of TB_R_INSTRUCTION the qty was taken from"],
                 ["TO_INSTRUCTION_ID", "BIGINT", "", "N", "Row of TB_R_INSTRUCTION of the replacement (same row when the whole row moved)"],
                 ["CREATED_BY", "VARCHAR(20)", "", "N", "Login user ID (D/S team)"],
                 ["CREATED_DT", "DATETIME", "", "N", "Server system date-time"]]}


def item(name, src, field, typ, io, control, desc, fmt='-', val='-', just='Left', init='-', req='N', ln='-'):
    return {"name": name, "source": src, "field": field, "type": typ, "len": ln, "io": io, "control": control, "justified": just,
            "initial": init, "required": req, "format": fmt, "validation": val, "description": desc}


def btns(**on):
    return {b: on.get(b, 'D') for b in BUTTONS}


def build():
    spec = set_header({"doc_type": "screen"}, 'XD11')
    spec.update({
        "general": {
            "objective": [
                "To list the customer order lines cancelled in G-System (UPD_STATUS '2', set by XD08) whose qty is already in a submitted ASN.",
                "To move the cancelled qty to order lines of the same part that G-System has received (UPD_STATUS '6', PO_MAPPED_FLAG 'N', not in an ASN), "
                "so that the cases of the ASN keep a valid customer order (decided 23-Oct; replaces the former XD11 cancel batch and the CONFLICT handling outside the system).",
                "D/S team only: sub menu of ASN (next to ASN Creation)."],
            "display_order": [{"section": "Cancelled qty", "fields": [{"field": "ASN No", "order": "Ascending"}, {"field": "Customer Order Date of the cancelled line", "order": "Ascending"}]},
                              {"section": "Replacement order lines", "fields": [{"field": "Customer Order Date", "order": "Ascending (oldest first)"},
                                                                                {"field": "Customer Order No", "order": "Ascending"}]}],
            "buttons": [{"name": "Expand (replacement)", "function": "Show the cases of the ASN (TB_R_INSTRUCTION) and the replacement order lines of a cancelled qty."},
                        {"name": "Candidate (check box)", "function": "Choose the replacement order lines; the qty of the ticked lines must add up to the cancelled qty."},
                        {"name": "Change Order Number", "function": "Enabled when the ticked qty equals the cancelled qty; opens the confirmation."},
                        {"name": "Yes / No", "function": "Yes: move the qty (TB_R_INSTRUCTION, PO_MAPPED_FLAG, history). No: close the confirmation."}],
            "screen_modes": [
                {"mode": "List Mode", "sections": [
                    {"section": "Cancelled qty in submitted ASNs", "description": "One row per cancelled line and ASN; status Candidate available / Waiting for a candidate",
                     "buttons": btns(**{"Expand (replacement)": "E"})},
                    {"section": "History", "description": "Changes of TB_H_CROSSDOCK_ORDER_CHANGE", "buttons": btns()}]},
                {"mode": "Detail Mode", "sections": [
                    {"section": "Cases of the ASN / Replacement order lines", "description": "Rows of the cancelled line highlighted; candidates oldest first, pre-ticked",
                     "buttons": btns(**{"Expand (replacement)": "E", "Candidate (check box)": "E", "Change Order Number": "E"})},
                    {"section": "Confirmation", "description": "Modal", "buttons": btns(**{"Yes / No": "E"})}]}],
            "screen_mode_remarks": [
                "1) Only the D/S team opens this screen (menu right in Menu Settings).",
                "2) A cancelled qty stays in the list until it is moved (no time limit); without candidate it is shown as Waiting for a candidate.",
                "3) [Change Order Number] is enabled only when the ticked qty equals the cancelled qty (message no. 2 otherwise)."]},
        "screen_flow": [{"title": "Screen Flow - Change Order Number", "flow": {"direction": "LR", "nodes": [
            {"id": "b", "label": "XD08 batch: UPD_STATUS 2 for a line in an ASN", "type": "process"},
            {"id": "l", "label": "Change Order Number - list", "type": "screen"},
            {"id": "d", "label": "Detail: cases + candidates", "type": "screen"},
            {"id": "c", "label": "Confirmation", "type": "screen"},
            {"id": "h", "label": "TB_R_INSTRUCTION / TB_H_CROSSDOCK_ORDER_CHANGE", "type": "db"}],
            "edges": [{"from": "b", "to": "l"}, {"from": "l", "to": "d", "label": "Expand"}, {"from": "d", "to": "c", "label": "Change Order Number"},
                      {"from": "c", "to": "h", "label": "Yes"}, {"from": "h", "to": "l", "label": "row removed"}]}}],
        "screen_layout": [
            {"caption": "1. List Mode with the detail of ASN00020 (partial cancel of CO-B: 6 of 8 pcs; candidates CO-E 4 + CO-F 2 pre-ticked, oldest first)", "image": IMG + "x_01_change_order_list.png"},
            {"caption": "2. Detail of ASN0003 (simulasi_asn.xlsx: CO-14104 cancelled after the ASN; candidate CO-14111, UPD_STATUS 6)", "image": IMG + "x_02_change_order_detail.png"},
            {"caption": "3. Confirmation", "image": IMG + "x_03_change_order_confirm.png"},
            {"caption": "4. After the change: row removed from the list, history written", "image": IMG + "x_04_change_order_after.png"}],
        "items": [
            {"group": "<Cancelled Qty in Submitted ASNs Section>"},
            item("Expand", "-", "-", "-", "I", "Button", "Opens the detail (cases and candidates) of the row.", just="Center", init="Enabled"),
            item("ASN No", INS, "ASN_NO", "Char", "O", "Label", "Submitted ASN that holds the cancelled qty.", ln="15"),
            item("Part Number", CTL, "SHIPPING_PART_NO", "Char", "O", "Label", "Part number of the cancelled line.", ln="15"),
            item("Cancelled Customer Order", CTL, "CUSTOMER_ORDER_NO / SERIAL_NO", "Char", "O", "Label", "Line with UPD_STATUS '2' (serial of the status 2 row)."),
            item("Destination", CTL, "DESTINATION_CD", "Char", "O", "Label", "Destination of the cancelled line.", ln="7"),
            item("Cancelled Qty", CTL, "ORDER_STATUS_QTY (UPD_STATUS 2)", "Number", "O", "Label", "Qty cancelled by G-System that is in the ASN.", fmt="ZZZ9", just="Right"),
            item("Cases (from the last case)", INS, "CASE_NO / QTY", "Char", "O", "Label",
                 "Proposal of the qty to move: from the last case of the ASN backwards (e.g. C-00020-02: 4, C-00020-01: 2); a row is split when only part of it is needed."),
            item("Status", "Computed", "-", "Char", "O", "Label", "Candidate available (amber) / Waiting for a candidate (grey)."),
            {"group": "<Detail: Cases of the ASN>"},
            item("Case No / Customer Order / Destination / Qty / PO No", INS, "CASE_NO, CUSTOMER_ORDER_NO, DESTINATION_CD, QTY, PO_NO", "Char", "O", "Grid",
                 "All rows of the ASN; rows of the cancelled line highlighted."),
            {"group": "<Detail: Replacement Order Lines>"},
            item("Candidate (check box)", "Key-in", "-", "Char", "I", "CheckBox",
                 "Lines of the same part with UPD_STATUS '6', PO_MAPPED_FLAG 'N' and no row in TB_R_INSTRUCTION; oldest Customer Order Date first. Pre-ticked: oldest lines "
                 "whose qty adds up to the cancelled qty. Another destination is allowed.", just="Center", init="<pre-ticked>"),
            item("Customer Order / Order Date / Destination / Qty", CTL, "CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, ORDER_STATUS_QTY", "Char", "O", "Grid", "Candidate line."),
            item("Selected qty", "Computed", "-", "Number", "O", "Label", "'Selected {n} of {q} pcs'; red text when it differs from the cancelled qty."),
            item("Change Order Number", "-", "-", "-", "I", "Button", "Refer Operation 5.2.", just="Center", init="Disabled"),
            {"group": "<History Section>"},
            item("Time / ASN No / Case No / Part / From Order / To Order / To Destination / Qty / By", HIS, "CREATED_DT, ASN_NO, CASE_NO, PART_NO, FROM_*, TO_*, QTY, CREATED_BY",
                 "Char", "O", "Grid", "Changes made (newest first).")],
        "data_map": {"blocks": [
            {"source": "Cases of the cancelled line (from the last case) + ticked candidates", "destination": {"table": INS, "operation": "Update / Insert",
             "description": "[Yes]: per case piece, the qty moves to the replacement line", "keys": [{"field": "INSTRUCTION_ID", "value": "Rows of the cancelled line in the ASN"}]},
             "mappings": [{"dest_field": "QTY", "description": "Whole row moved: not changed. Part of the row: reduced by the moved qty (the rest stays with the cancelled line)"},
                          {"dest_field": "CUSTOMER_CD / CUSTOMER_ORDER_NO / ORDER_DT / DESTINATION_CD / DETAILED_ITEM_NO / SERIAL_NO",
                           "description": "Whole row: replaced by the key of the replacement line. Part of the row: a new row is inserted with the key of the replacement line "
                                          "and the moved qty; ASN_NO, CASE_NO, CASE_SEQ, PO_NO, MANIFEST_NO, MANIFEST_ITEM copied"},
                          {"dest_field": "CHANGED_BY / CHANGED_DT", "description": "Login user ID / server system date-time"}]},
            {"source": "Ticked candidates", "destination": {"table": CTL, "operation": "Update", "description": "Replacement lines",
             "keys": [{"field": "Unique key (incl. SERIAL_NO)", "value": "Ticked lines"}]},
             "mappings": [{"dest_field": "PO_MAPPED_FLAG", "description": "'Y' (PO and ASN through the moved qty)"}, {"dest_field": "UPDATE_BY / UPDATE_DT", "description": "Login user ID / system date-time"}]},
            {"source": "Cancelled line", "destination": {"table": CTL, "operation": "-", "description": "Not changed: PO_MAPPED_FLAG stays 'Y', UPD_STATUS stays '2'",
             "keys": [{"field": "Unique key (incl. SERIAL_NO)", "value": "Cancelled line"}]}, "mappings": [{"dest_field": "PO_MAPPED_FLAG", "description": "Not changed"}]},
            {"source": "Each moved piece", "destination": {"table": HIS, "operation": "Insert", "description": "History of the change"},
             "mappings": [{"dest_field": c[0], "description": c[4]} for c in HIS_TABLE["columns"]]}]},
        "operation": [
            {"type": "heading", "text": "5.1 List Mode"},
            {"type": "bullets", "marker": "a.", "level": 2, "items": [
                "On display, every line with UPD_STATUS '2' that has rows in TB_R_INSTRUCTION with ASN_NO is listed, one row per line and ASN. Lines cancelled without "
                "ASN (no row, or drafts released by XD08) are not listed.",
                "Cancelled qty = qty of the status 2 row of the line in the ASN; the proposal of the cases is taken from the last case of the ASN backwards.",
                "Status: Candidate available when at least one candidate exists; else Waiting for a candidate (the row stays until a candidate appears). No row: message no. 1."]},
            {"type": "heading", "text": "5.2 Detail Mode and Change Order Number"},
            {"type": "bullets", "marker": "a.", "level": 2, "items": [
                "Candidates: lines of the same part with UPD_STATUS '6', PO_MAPPED_FLAG 'N' and no row in TB_R_INSTRUCTION, oldest Customer Order Date first. Another destination "
                "is allowed. The oldest lines whose qty adds up to the cancelled qty are pre-ticked; the D/S team can change the ticks.",
                "[Change Order Number] is enabled only when the ticked qty equals the cancelled qty (message no. 2 as hint otherwise). Confirmation message no. 3.",
                "[Yes], in one transaction: the cancelled qty is moved case by case (from the last case) to the ticked lines in their order; a TB_R_INSTRUCTION row "
                "is updated when it moves completely and split (new row) when only part of it moves. The ASN, its cases, CASE_NO and PO do not change. "
                "Replacement lines: PO_MAPPED_FLAG 'Y'. Cancelled line: not changed. One history record per moved piece. The row leaves the list.",
                "Re-check in the same transaction: when a candidate was taken in the meantime (PO_MAPPED_FLAG 'Y' or row in TB_R_INSTRUCTION), nothing is saved and "
                "message no. 4 is shown; the detail is refreshed."]},
            {"type": "heading", "text": "5.3 Example (simulasi_asn.xlsx)"},
            {"type": "bullets", "marker": "a.", "level": 2, "items": [
                "18-Oct: cases 1-4 of order date 17-Oct are sent in ASN0003 (case 3 = CO-14104, TH, 6 pcs, a middle row). 19-Oct: CO-14104 is cancelled (waiting for a "
                "candidate). 21-Oct: CO-14111 (TH, 6 pcs, order date 19-Oct) is received in G-System (UPD_STATUS 6, PO_MAPPED_FLAG N, no ASN). "
                "The D/S team moves the 6 pcs of case C-0003-03 to CO-14111.",
                "Partial cancel: CO-B 8 pcs in ASN00020 (case 1: 4, case 2: 4), 6 pcs cancelled: case 2 4 pcs + 2 of the 4 pcs of case 1 (row split) move to CO-E (4) and CO-F (2)."]}],
        "display_messages": [
            {"group": "List"},
            {"event": "Open the screen", "cause": "No cancelled qty in a submitted ASN", "type": "Info", "msg_id": "MSG1", "message": "No cancelled qty in a submitted ASN.", "action": "-"},
            {"group": "Change Order Number"},
            {"event": "Tick candidates", "cause": "Ticked qty differs from the cancelled qty", "type": "Info", "msg_id": "MSG2",
             "message": "Selected {n} of {q} pcs: the qty must add up to {q}.", "action": "Tick other candidates."},
            {"event": "Click [Change Order Number]", "cause": "Confirmation", "type": "Confirmation", "msg_id": "MSG3",
             "message": "{q} pcs of {Customer Order} in {ASN No} ({cases}) will be moved to {replacement lines}.", "action": "Yes / No."},
            {"event": "Click [Yes]", "cause": "A candidate was taken in the meantime", "type": "Error", "msg_id": "MSG4",
             "message": "{Customer Order} is no longer available. The candidates are refreshed.", "action": "Tick again."}],
        "logging_messages": [],
        "tables": [HIS_TABLE],
    })
    return [write(spec, 'XD11')]


if __name__ == '__main__':
    print('\n'.join(build()))
