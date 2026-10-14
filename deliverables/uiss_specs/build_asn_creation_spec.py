"""Spec for X8_UISS_Screen_ASNCrossdockCreation.xlsx (UISS-Screen, ASN Crossdock Creation with its Case List sub screen)."""
import json, sys
from asn_common import ASNH, ASNH_TABLE, DM, INSTR, INSTR_TABLE, btn, header, it, out, revisions

IMG = 'deliverables/uiss_screens/asn_crossdock'
B = ["Search", "Reset", "Detail (expand, D/S)", "Clear selection", "Create ASN", "Back", "Download Case Label", "Cancel", "Submit ASN", "Yes / No", "OK"]


def modes(on):
    return {b: ("E" if b in on else "D") for b in B}


spec = {
 "doc_type": "screen",
 "header": header("X8", "Screen", "ASN Crossdock Creation"),
 "revisions": revisions(),
 "general": {
  "objective": [
   "To display the delivery plan of crossdock parts per Part Number + Customer Order Date, with its status Ready to Delivery / Waiting for Next PO (from TB_R_INSTRUCTION).",
   "To select one or more Ready to Delivery units, also of different Customer Order Dates, and create one ASN with them.",
   "To review the cases of the ASN (one case per Part Number + Customer Order Date + destination), enter Delivery Date and Rit Cycle, download the case labels and submit the ASN."],
  "display_order": [
   {"section": "Delivery plan", "fields": [{"field": "Customer Order Date", "order": "Ascending"}, {"field": "Part Number", "order": "Ascending"}]},
   {"section": "Order lines", "fields": [{"field": "Detailed Item No", "order": "Ascending"}]},
   {"section": "Case List", "fields": [{"field": "Selected unit (Customer Order Date, Part Number)", "order": "Ascending"}, {"field": "Destination, by first appearance in the unit", "order": "-"}]}],
  "buttons": [
   {"name": "Search", "function": "Retrieve the delivery plan by Customer Order Date range, Part Number and Status."},
   {"name": "Reset", "function": "Clear criteria and reset the screen to its initial value."},
   {"name": "Detail (expand, D/S)", "function": "D/S team only: show / hide the destination detail (pcs) and the customer order lines of a unit with their PO assignment."},
   {"name": "Clear selection", "function": "Untick all selected units."},
   {"name": "Create ASN", "function": "Open the Case List sub screen with all cases of the selected units."},
   {"name": "Back", "function": "Return from the Case List to ASN Crossdock Creation without submitting."},
   {"name": "Download Case Label", "function": "Download the labels of all cases of the ASN. TBD: label format and content."},
   {"name": "Cancel", "function": "Same as Back."},
   {"name": "Submit ASN", "function": "Ask for confirmation, then submit the ASN and lock its units."},
   {"name": "Yes / No", "function": "Confirmation of Submit ASN (Submit? Y / N)."},
   {"name": "OK", "function": "Close the success notification."}],
  "screen_modes": [
   {"mode": "List Mode - No Selection", "sections": [
     {"section": "Search Criteria", "description": "Criteria blank (Status = All); all units listed", "buttons": modes(["Search", "Reset"])},
     {"section": "Delivery plan", "description": "One row per Part Number + Customer Order Date; nothing ticked", "buttons": modes(["Detail (expand, D/S)"])},
     {"section": "Selection bar", "description": "Hint text", "buttons": modes([])}]},
   {"mode": "List Mode - Units Selected", "sections": [
     {"section": "Search Criteria", "description": "Refer 1.a", "buttons": modes(["Search", "Reset"])},
     {"section": "Delivery plan", "description": "One or more Ready to Delivery units ticked", "buttons": modes(["Detail (expand, D/S)"])},
     {"section": "Selection bar", "description": "Units and cases selected", "buttons": modes(["Clear selection", "Create ASN"])}]},
   {"mode": "Case List Mode (sub screen)", "sections": [
     {"section": "ASN summary", "description": "ASN No auto ('assigned on submit'), supplier, units, cases / qty", "buttons": modes(["Back"])},
     {"section": "Case list", "description": "Delivery Date and Rit Cycle editable; cases read only", "buttons": modes(["Download Case Label"])},
     {"section": "Footer", "description": "Submit enabled when there are cases, a Delivery Date and a Rit Cycle", "buttons": modes(["Cancel", "Submit ASN"])}]},
   {"mode": "Confirmation / Notification", "sections": [
     {"section": "Submit confirmation", "description": "'Submit ASN?' Yes / No", "buttons": modes(["Yes / No"])},
     {"section": "Success notification", "description": "ASN submitted; back to the list", "buttons": modes(["OK"])}]}],
  "screen_mode_remarks": [
   "1) The check box of a unit is enabled only when its status is Ready to Delivery and it is not in an ASN yet (message no. 1 or 2 as tooltip otherwise).",
   "2) Units of different Customer Order Dates and Part Numbers can be ticked together; each unit always goes into the ASN as a whole.",
   "3) Submit ASN is enabled only when the case list is not empty, Delivery Date is filled and a Rit Cycle is available."]
 },
 "screen_flow": [
  {"title": "Screen Flow - ASN Crossdock", "flow": {"direction": "LR", "nodes": [
     {"id": "c", "label": "ASN Crossdock Creation", "type": "screen"},
     {"id": "l", "label": "Case List (sub screen)", "type": "screen"},
     {"id": "n", "label": "Success notification", "type": "message"},
     {"id": "i", "label": "ASN Inquiry (X13)", "type": "screen"}],
    "edges": [{"from": "c", "to": "l", "label": "Create ASN"}, {"from": "l", "to": "c", "label": "Back / Cancel / Submit? N"},
              {"from": "l", "to": "n", "label": "Submit? Y"}, {"from": "n", "to": "c", "label": "OK"}, {"from": "c", "to": "i", "label": "menu"}]}},
  {"title": "Screen Flow - Check Ready Status and Create ASN", "flow": {"direction": "TB", "nodes": [
     {"id": "s", "label": "START", "type": "start"},
     {"id": "e", "label": "Select delivery plan by Customer Order Date and Part Number", "type": "event"},
     {"id": "d", "label": "Ready to Delivery? (all orders of the unit assigned to a PO)", "type": "decision"},
     {"id": "w", "label": "Waiting for Next PO: Create ASN disabled", "type": "message"},
     {"id": "p", "label": "Tick unit(s): Create ASN enabled", "type": "process"},
     {"id": "l", "label": "Case List: Delivery Date, Rit Cycle, Download Case Label", "type": "process"},
     {"id": "d2", "label": "Submit?", "type": "decision"},
     {"id": "p2", "label": "Save ASN, lock units, show success", "type": "process"},
     {"id": "db", "label": "TB_R_ASN_CROSSDOCK_H / TB_R_INSTRUCTION", "type": "db"},
     {"id": "x", "label": "END", "type": "end"}],
    "edges": [{"from": "s", "to": "e"}, {"from": "e", "to": "d"}, {"from": "d", "to": "w", "label": "N"}, {"from": "d", "to": "p", "label": "Y"},
              {"from": "p", "to": "l"}, {"from": "l", "to": "d2"}, {"from": "d2", "to": "l", "label": "N"}, {"from": "d2", "to": "p2", "label": "Y"},
              {"from": "p2", "to": "db", "style": "dashed"}, {"from": "p2", "to": "x"}], "same_rank": [["p2", "db"]]}}],
 "screen_layout": [
  {"caption": "1. Delivery plan (business date 14-Oct): PART-C 13-Oct waits for the PO of 15-Oct (condition 3)", "image": f"{IMG}/c_01_list_bd14.png"},
  {"caption": "2. D/S team view: destination (pcs) and order line detail of a Waiting for Next PO unit", "image": f"{IMG}/c_02_ds_detail.png"},
  {"caption": "3. Delivery plan (business date 15-Oct): PART-C 13-Oct becomes Ready to Delivery", "image": f"{IMG}/c_03_list_bd15.png"},
  {"caption": "4. Units of different Customer Order Dates selected", "image": f"{IMG}/c_04_selected.png"},
  {"caption": "5. Case List sub screen", "image": f"{IMG}/c_05_case_list.png"},
  {"caption": "6. Submit confirmation", "image": f"{IMG}/c_06_confirm.png"},
  {"caption": "7. Success notification", "image": f"{IMG}/c_07_submitted.png"},
  {"caption": "8. Delivery plan after submit (units In ASN)", "image": f"{IMG}/c_08_list_after.png"}],
 "items": [
  {"group": "<Search Criteria Section>"},
  it("Customer Order Date - From / To", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Blank", "N", "DD-Mon-YYYY", "-", "Range of Customer Order Date, inclusive. Blank = no limit."),
  it("Part Number", "Key-in", "-", "Char", "15", "I", "Combo Box", "Left", "All", "N", "-", "-", "All / part numbers in TB_R_INSTRUCTION."),
  it("Status", "Key-in", "-", "Char", "-", "I", "Combo Box", "Left", "All", "N", "-", "-", "All / Ready to Delivery / Waiting for Next PO / In ASN."),
  btn("Search", "Refer Operation Description 5.1."), btn("Reset", "Refer Operation Description 5.1."),
  {"group": "<Delivery Plan Section>"},
  out("Counter", "Computed", "-", "Char", "-", "Label", "Left", "-", "'{n} units · {r} ready · {w} waiting'."),
  it("Select (check box)", "Key-in", "-", "Char", "1", "I", "CheckBox", "Center", "<unchecked>", "N", "-", "Enabled only for Ready to Delivery units not in an ASN", "Several units can be ticked. Ticked and disabled when the unit is in an ASN. Refer Screen Mode remark 1)."),
  out("Customer Order Date", INSTR, "ORDER_DT", "Date", "-", "Label", "Left", "DD-Mon-YYYY", "Customer Order Date of the unit."),
  out("Part Number / Part Name", INSTR, "PART_NO", "Char", "15", "Label", "Left", "-", "Part number of the unit; part name from the part master."),
  out("Case Qty", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of cases of the unit (one case per destination); also shown while waiting."),
  out("Not Assigned (case)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Cases (destinations) of the unit that still have qty without a released PO (REMAINING_ORDER_QTY > 0); '-' when 0."),
  out("PO No", INSTR, "PO_NO", "Char", "TBD", "Label", "Left", "-", "PO numbers of the unit, separated by ', '."),
  out("Last PO Date", INSTR, "PO_ORDER_DT", "Date", "-", "Label", "Left", "DD-Mon-YYYY", "Latest PO Date of the unit."),
  out("Status", "Computed", "-", "Char", "-", "Label", "Left", "-", "Ready to Delivery (green) / Waiting for Next PO (amber, row highlighted) / In ASN (grey). Refer 5.2."),
  out("ASN No", INSTR, "ASN_NO", "Char", "TBD", "Label", "Left", "-", "ASN of the unit; '-' when none."),
  btn("Detail (expand, D/S)", "Shown to the D/S team only; hidden for the supplier. Opens the detail below."),
  {"group": "<Delivery Plan Detail (D/S team only)>"},
  out("Destination", INSTR, "DESTINATION_CD", "Char", "7", "Grid", "Left", "{code} · {name}", "One row per destination (= one case); name from " + DM + "."),
  out("Case", "Computed", "-", "Number", "-", "Grid", "Right", "9", "Always 1 (one case per destination)."),
  out("Qty (pcs)", INSTR, "CUST_ORDER_QTY", "Number", "8", "Grid", "Right", "ZZ,ZZ9", "Sum of the order qty of the destination; the detail title shows the unit total."),
  out("Not Assigned (pcs)", INSTR, "REMAINING_ORDER_QTY", "Number", "8", "Grid", "Right", "ZZ,ZZ9", "Qty of the destination without a released PO; '-' when 0."),
  out("Order lines", INSTR, "CUSTOMER_ORDER_NO / DETAILED_ITEM_NO / DESTINATION_CD / CUST_ORDER_QTY / PO_NO / PO_ORDER_DT", "Char", "-", "Grid", "Left", "-", "Customer Order No, Detailed Item No, Destination, Qty, PO No, PO Date, Assignment (Assigned / Planned / Not assigned)."),
  {"group": "<Selection Bar Section>"},
  out("Selection summary", "Computed", "-", "Char", "-", "Label", "Left", "-", "'{n} units selected · {c} cases · {units}'. Empty: hint that units of different dates can go into one ASN."),
  btn("Clear selection", "Unticks all units.", "Disabled"), btn("Create ASN", "Opens the Case List sub screen. Refer 5.3.", "Disabled"),
  {"group": "<Case List Sub Screen - ASN Summary>"},
  btn("Back", "Returns to ASN Crossdock Creation without submitting."),
  out("ASN No", ASNH, "ASN_NO", "Char", "TBD", "Label", "Left", "ASN-{Supplier}-{YYMMDD}-{Seq}", "Generated from the Delivery Date; 'auto · assigned on submit'. Sequence rule TBD."),
  out("Supplier · Plant", INSTR, "SUPPLIER_CD / SUPPLIER_PLANT", "Char", "TBD", "Label", "Left", "-", "Supplier of the cases."),
  out("Part / Customer Order Date", "Computed", "-", "Char", "-", "Label", "Left", "-", "Selected units."),
  out("Cases · Qty", "Computed", "-", "Char", "-", "Label", "Left", "N cases · N pcs", "Number of cases and total pieces."),
  {"group": "<Case List Sub Screen - Case List>"},
  it("Delivery Date", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Business date + 1", "Y", "DD-Mon-YYYY", "Mandatory; today or later", "Changing it reloads the Rit Cycle list."),
  it("Rit Cycle", "TBD (Route Master)", "TBD", "Char", "TBD", "I", "Combo Box", "Left", "First rit cycle of the date", "Y", "-", "Mandatory", "Rit cycles of the Delivery Date; Sunday none ('No rit cycle'), Saturday one."),
  out("Route", "TBD (Route Master)", "TBD", "Char", "TBD", "Text box (disabled)", "Left", "-", "Route of the Rit Cycle."),
  btn("Download Case Label", "Downloads the labels of all cases. TBD format."),
  out("Case", "Computed", "-", "Char", "-", "Grid", "Left", "Case {n}", "Case sequence; case number assigned on submit."),
  out("Part Number / Customer Order Date / Destination", INSTR, "PART_NO / ORDER_DT / DESTINATION_CD", "Char", "-", "Grid", "Left", "-", "Key of the case (one case per Part Number + Customer Order Date + destination); destination name from " + DM + "."),
  out("Customer Order No (qty)", INSTR, "CUSTOMER_ORDER_NO / ASSIGNED_QTY", "Char", "-", "Grid", "Left", "-", "Order lines packed in the case."),
  out("PO No", INSTR, "PO_NO", "Char", "TBD", "Grid", "Left", "-", "PO numbers of the case."),
  out("Qty / Total", "Computed", "-", "Number", "-", "Grid", "Right", "ZZ,ZZ9", "Pieces of the case; total of all cases."),
  btn("Cancel", "Same as Back."), btn("Submit ASN", "Refer Operation Description 5.4 and Screen Mode remark 3)."),
  out("No rit cycle message", "Computed", "-", "Char", "-", "Label", "Left", "-", "Message no. 5 when no rit cycle is available.")],
 "data_map": {"blocks": [
  {"source": "Key-in from screen", "destination": {"table": ASNH, "operation": "Insert", "description": "Case List - [Submit ASN] Yes"},
   "mappings": [
     {"dest_field": "ASN_NO", "description": "Generated from the Delivery Date"},
     {"source_field": "Supplier", "dest_field": "SUPPLIER_CD"}, {"source_field": "Plant", "dest_field": "SUPPLIER_PLANT"},
     {"source_field": "Delivery Date", "dest_field": "DELIVERY_DT"}, {"source_field": "Rit Cycle", "dest_field": "RIT_CYCLE"},
     {"source_field": "Route", "dest_field": "ROUTE"}, {"dest_field": "TOTAL_CASE", "description": "Number of cases"},
     {"dest_field": "TOTAL_QTY", "description": "Sum of case qty"}, {"dest_field": "ASN_STATUS", "description": "'SUBMITTED'"},
     {"dest_field": "CREATED_BY", "description": "Login user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date-time"},
     {"dest_field": "CHANGED_BY", "description": "Login user ID"}, {"dest_field": "CHANGED_DT", "description": "Server system date-time"}]},
  {"source": "Case List (screen)", "destination": {"table": INSTR, "operation": "Update", "description": "Every line of the selected units",
                                                    "keys": [{"field": "PART_NO + ORDER_DT", "value": "Selected unit"}]},
   "mappings": [
     {"dest_field": "ASN_NO", "description": "ASN_NO of the header"},
     {"dest_field": "CASE_NO", "description": "{ASN No}-{case seq}; one case per Part Number + Customer Order Date + destination"},
     {"dest_field": "CHANGED_BY", "description": "Login user ID"}, {"dest_field": "CHANGED_DT", "description": "Server system date-time"}]}]},
 "operation": [
  {"type": "heading", "text": "5.1 Initial Display and Search"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "On first display all units of TB_R_INSTRUCTION are listed (criteria blank, Status = All), one row per Part Number + Customer Order Date, sorted by Customer Order Date then Part Number.",
    "[Search] applies the criteria (Customer Order Date range, Part Number, Status). [Reset] clears them. No row: message no. 3.",
    "The delivery plan header is at case level: Case Qty and Not Assigned (case). Pieces and destinations are not shown in the header.", "The detail of a unit (destination with Case, Qty (pcs), Not Assigned (pcs), and the order lines with Customer Order No, Detailed Item No, Destination, Qty, PO No, PO Date and Assignment) can be expanded by the D/S team only; for the supplier the expand button is hidden."]},
  {"type": "heading", "text": "5.2 Status Rule (Check Ready Status)"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "Unit = Part Number + Customer Order Date. It is 'Ready to Delivery' when every order line of the unit is assigned to a PO (no row with PO_NO NULL / REMAINING_ORDER_QTY > 0).",
    "Otherwise it is 'Waiting for Next PO': the unit still has remaining order qty with the same Customer Order Date not assigned to a PO; its check box is disabled (message no. 2). The planned cases are already shown.",
    "Condition 1 and 2: all lines of the unit assigned (in any line sequence): Ready to Delivery; one case per destination.",
    "Condition 3: the lines of the unit are assigned to several POs with different PO Dates: the unit is Ready to Delivery only from the last PO Date (when the last PO is released); before that Create ASN cannot use it, but its cases can be checked.",
    "A unit in an ASN shows 'In ASN' with its ASN No; it is ticked and locked."]},
  {"type": "heading", "text": "5.3 Select Units and Create ASN"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "The user ticks one or more Ready to Delivery units. Units of different Customer Order Dates and Part Numbers can be combined in one ASN (e.g. PART-B and PART-C of 13-Oct with PART-A of 14-Oct).",
    "A unit is never split: all its order lines go into the same ASN. Other parts of the same Customer Order Date do not have to be included.",
    "The selection bar shows the number of units, cases and pieces. [Create ASN] opens the Case List sub screen; [Clear selection] unticks all units."]},
  {"type": "heading", "text": "5.4 Case List and Submit ASN"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "Cases: one case per Part Number + Customer Order Date + destination. Different part numbers are never in the same case. The order lines of one destination may be in any sequence (conditions 1 and 2); their total is within one case (the qty of H0253 per part and destination does not exceed pcs/case, it may be split over several lines, e.g. 4 + 2 or 1 + 1 + 3).",
    "Cases are numbered in order of the selected units and the first appearance of each destination in the unit.",
    "Delivery Date defaults to business date + 1 (today or later). The Rit Cycle list depends on the Delivery Date; Sunday has none (message no. 5, Submit disabled), Saturday has one. Route follows the Rit Cycle.",
    "[Download Case Label]: TBD (format, file name, content).",
    "[Submit ASN]: confirmation 'Submit ASN?' (message no. 4). No: stay on the Case List. Yes: generate the ASN No from the Delivery Date, insert TB_R_ASN_CROSSDOCK_H, fill ASN_NO and CASE_NO of every line of the selected units in TB_R_INSTRUCTION (refer Data Edit Mapping), display message no. 6 and return to ASN Crossdock Creation, where the units show 'In ASN'.",
    "Reject the submit (message TBD) if a unit is no longer Ready to Delivery or already in an ASN (changed by another user)."]},
  {"type": "heading", "text": "5.5 Notes"},
  {"type": "bullets", "marker": "-", "level": 2, "items": [
    "TB_R_INSTRUCTION is filled by the batch X12 (Customer Order - PO Mapping, FIFO by Customer Order Date). Submitted ASNs are shown in ASN Inquiry (X13).",
    "The prototype has a 'Business date' switch to simulate the release of later POs (condition 3); it is not part of the real screen.",
    "Supplier rule for one ASN (one supplier / plant per ASN) is TBD."]}],
 "display_messages": [
  {"group": "Delivery Plan (tooltip of disabled check box)"},
  {"event": "Hover on disabled check box", "cause": "Unit already in an ASN", "type": "Info", "msg_id": "MSG1", "message": "Already in {ASN No}", "action": "None."},
  {"event": "Hover on disabled check box", "cause": "Unit is Waiting for Next PO", "type": "Info", "msg_id": "MSG2", "message": "Waiting for Next PO: {k} of {n} cases of {Part No} / {Customer Order Date} are not assigned to a released PO yet", "action": "Wait for the next PO."},
  {"group": "Search Operation"},
  {"event": "Click [Search] button", "cause": "No unit matches", "type": "Info", "msg_id": "MSG3", "message": "No delivery plan matches this search.", "action": "Change the criteria."},
  {"group": "Case List"},
  {"event": "Click [Submit ASN] button", "cause": "Confirmation", "type": "Confirm", "msg_id": "MSG4", "message": "Submit ASN? {n} cases ({q} pcs) will be locked into {ASN No}, delivery {Delivery Date} · {Rit Cycle}.", "action": "Click [Yes, submit] or [No]."},
  {"event": "Change [Delivery Date]", "cause": "No rit cycle on the date (Sunday)", "type": "Info", "msg_id": "MSG5", "message": "No rit cycle available for {Delivery Date}. Choose another delivery date.", "action": "Choose another Delivery Date."},
  {"event": "Click [Yes, submit]", "cause": "ASN submitted", "type": "Info", "msg_id": "MSG6", "message": "{ASN No} submitted. {n} cases are locked. Delivery {Delivery Date} · {Rit Cycle}. The ASN is shown in ASN Inquiry.", "action": "Click [OK]."}],
 "logging_messages": [
  {"event": "Click [Yes, submit]", "cause": "Database error on insert / update", "type": "Error", "msg_id": "LOG1", "message": "Failed to submit ASN <ASN_NO>: <DB error message>.", "exception": "Y", "action": "Show [Corresponding Screen Message] on screen (TBD)"}],
 "tables": [INSTR_TABLE, ASNH_TABLE]
}
# Update block on TB_R_INSTRUCTION: every other column is not changed
from asn_common import INSTR_COLS, NC
_blk = spec["data_map"]["blocks"][1]
_have = {m["dest_field"] for m in _blk["mappings"]}
_blk["mappings"] += [{"dest_field": c[0], "description": NC} for c in INSTR_COLS if c[0] not in _have]
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
