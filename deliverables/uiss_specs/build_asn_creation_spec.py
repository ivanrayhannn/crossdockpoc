"""Spec for X8_UISS_Screen_ASNCrossdockCreation.xlsx (UISS-Screen, ASN Crossdock Creation with its Case List sub screen)."""
import json, sys
from asn_common import (ASNH, DM, DRAFT, DRAFT_COLS, DRAFT_TABLE, H0253, INSTR, INSTR_TABLE, NC, PRA_P,
                        btn, header, it, out, revisions)

IMG = 'deliverables/uiss_screens/asn_crossdock'
B = ["Search", "Detail (expand, D/S)", "Customer orders (expand, D/S)", "Hold / Release (D/S)", "Clear selection", "Create ASN",
     "Back", "PO detail (expand)", "Download Case Label", "Cancel", "Submit ASN", "Yes / No", "OK"]


def modes(on):
    return {b: ("E" if b in on else "D") for b in B}


H0253_FULL = [c[0] for c in __import__('h_tables').H0253_COLS]

spec = {
 "doc_type": "screen",
 "header": header("X8", "Screen", "ASN Crossdock Creation", '15-Oct-26'),
 "revisions": revisions('15-Oct-26'),
 "general": {
  "objective": [
   "To get the crossdock customer orders for a Delivery Date and Rit and pre-map them to supplier POs ([Search], function X12 Get Order).",
   "To display the delivery plan per Part Number + Customer Order Date at case level (Case Qty, PO Readiness, ASN Status Ready / Not Ready). Units already Created or without any ready case are not listed.",
   "To let the D/S team see the destination detail and hold / release a destination of a unit.",
   "To select one or more Ready units, map them to their POs, review the cases, download the case labels and submit the ASN."],
  "display_order": [
   {"section": "Delivery plan", "fields": [{"field": "ASN Status (Ready, Not Ready)", "order": "-"}, {"field": "Part Number", "order": "Ascending"}, {"field": "Customer Order Date", "order": "Ascending"}]},
   {"section": "Destination detail (D/S)", "fields": [{"field": "Destination, by first appearance in the unit", "order": "-"}]},
   {"section": "Case List", "fields": [{"field": "Selected unit (Part Number, Customer Order Date)", "order": "Ascending"}, {"field": "Destination, by first appearance in the unit", "order": "-"}]}],
  "buttons": [
   {"name": "Search", "function": "Run X12 (Get Order): get the customer orders and pre-map them to POs for the chosen Delivery Date and Rit; display the delivery plan."},
   {"name": "Detail (expand, D/S)", "function": "D/S team only: show / hide the destinations (cases) of a unit with Qty, Pcs/Case and Hold Flag."},
   {"name": "Customer orders (expand, D/S)", "function": "D/S team only: show / hide the customer order lines of a destination (Customer Order No, Detailed Item No, Qty, PO No, PO Date)."},
   {"name": "Hold / Release (D/S)", "function": "D/S team only: set HOLD_FLAG of every order line of the destination (part number + customer order date + destination) to 'Y' (hold) or 'N' (release)."},
   {"name": "Clear selection", "function": "Untick all selected units."},
   {"name": "Create ASN", "function": "Map the selected units to their POs, build the ASN draft and open the Case List sub screen."},
   {"name": "Back", "function": "Return from the Case List to ASN Crossdock Creation without submitting; the mapping of the draft is released."},
   {"name": "PO detail (expand)", "function": "Show / hide PO No, Manifest No, Manifest Item No and PO Qty of a case."},
   {"name": "Download Case Label", "function": "Download the labels of all cases of the ASN. TBD: label format and content."},
   {"name": "Cancel", "function": "Same as Back."},
   {"name": "Submit ASN", "function": "Ask for confirmation, then hand the ASN to the batch X14 with a Submit ID; the result is written to the log."},
   {"name": "Yes / No", "function": "Confirmation of Submit ASN (Submit? Y / N)."},
   {"name": "OK", "function": "Close the success notification."}],
  "screen_modes": [
   {"mode": "Initial Mode", "sections": [
     {"section": "Delivery", "description": "Delivery Date = today (business date); Rit = first rit of the date; Route displayed", "buttons": modes(["Search"])},
     {"section": "Delivery plan", "description": "Empty: 'Choose the Delivery Date and Rit, then click Search.' Filters disabled", "buttons": modes([])}]},
   {"mode": "List Mode - Supplier", "sections": [
     {"section": "Delivery", "description": "Refer 1.a", "buttons": modes(["Search"])},
     {"section": "Delivery plan", "description": "Header only (case level); Part Number / Status filters", "buttons": modes([])},
     {"section": "Selection bar", "description": "Enabled when Ready units are ticked", "buttons": modes(["Clear selection", "Create ASN"])}]},
   {"mode": "List Mode - D/S Team", "sections": [
     {"section": "Delivery plan", "description": "Same as supplier plus the destination detail with Hold Flag; a unit with all destinations on hold is listed as On Hold", "buttons": modes(["Detail (expand, D/S)", "Customer orders (expand, D/S)", "Hold / Release (D/S)"])},
     {"section": "Selection bar", "description": "Refer 2.c", "buttons": modes(["Clear selection", "Create ASN"])}]},
   {"mode": "Case List Mode (sub screen)", "sections": [
     {"section": "ASN summary", "description": "ASN No (assigned on submit), supplier, Delivery Date · Rit · Route, Delivery Qty, cases", "buttons": modes(["Back"])},
     {"section": "Case list", "description": "Case Number, Part Number, Qty; expand PO detail", "buttons": modes(["PO detail (expand)", "Download Case Label"])},
     {"section": "Footer", "description": "Submit enabled when there are cases", "buttons": modes(["Cancel", "Submit ASN"])}]},
   {"mode": "Confirmation / Notification", "sections": [
     {"section": "Submit confirmation", "description": "'Submit ASN?' Yes / No", "buttons": modes(["Yes / No"])},
     {"section": "Success notification", "description": "Submit ID banner on the delivery plan; result in Log Monitoring", "buttons": modes(["OK"])}]}],
  "screen_mode_remarks": [
   "1) The check box of a unit is enabled only when its ASN Status is Ready (message no. 1 or 2 as tooltip otherwise).",
   "2) Units of different Customer Order Dates and Part Numbers can be ticked together; each unit always goes into the ASN as a whole.",
   "3) The expand buttons and Hold / Release are shown to the D/S team only; the supplier sees the header (case level) only.",
   "4) Search is enabled when Delivery Date is filled and a Rit is available (message no. 5 otherwise)."]
 },
 "screen_flow": [
  {"title": "Screen Flow - ASN Crossdock", "flow": {"direction": "LR", "nodes": [
     {"id": "c", "label": "ASN Crossdock Creation", "type": "screen"},
     {"id": "l", "label": "Case List (sub screen)", "type": "screen"},
     {"id": "n", "label": "Success notification", "type": "message"},
     {"id": "i", "label": "ASN Inquiry (X13)", "type": "screen"}],
    "edges": [{"from": "c", "to": "l", "label": "Create ASN"}, {"from": "l", "to": "c", "label": "Back / Cancel"},
              {"from": "l", "to": "n", "label": "Submit? Y"}, {"from": "n", "to": "c", "label": "OK"}, {"from": "c", "to": "i", "label": "menu"}]}},
  {"title": "Screen Flow - Search, Check Ready Status and Create ASN", "flow": {"direction": "TB", "nodes": [
     {"id": "s", "label": "START", "type": "start"},
     {"id": "e", "label": "Choose Delivery Date and Rit, click Search", "type": "event"},
     {"id": "g", "label": "X12: get customer orders, pre-map to PO (#TB_R_INSTRUCTION)", "type": "process"},
     {"id": "d", "label": "ASN Status Ready? (all cases of the unit pre-mapped)", "type": "decision"},
     {"id": "w", "label": "Not Ready: check box disabled", "type": "message"},
     {"id": "p", "label": "Tick unit(s), Create ASN: map to PO, #TEMP_ASN_DRAFT", "type": "process"},
     {"id": "l", "label": "Case List: Download Case Label", "type": "process"},
     {"id": "d2", "label": "Submit?", "type": "decision"},
     {"id": "p2", "label": "Save ASN (status 1 Created), show success", "type": "process"},
     {"id": "db", "label": "TB_R_ASN_CROSSDOCK_H / _D", "type": "db"},
     {"id": "x", "label": "END", "type": "end"}],
    "edges": [{"from": "s", "to": "e"}, {"from": "e", "to": "g"}, {"from": "g", "to": "d"}, {"from": "d", "to": "w", "label": "N"}, {"from": "d", "to": "p", "label": "Y"},
              {"from": "p", "to": "l"}, {"from": "l", "to": "d2"}, {"from": "d2", "to": "l", "label": "N"}, {"from": "d2", "to": "p2", "label": "Y"},
              {"from": "p2", "to": "db", "style": "dashed"}, {"from": "p2", "to": "x"}], "same_rank": [["p2", "db"]]}}],
 "screen_layout": [
  {"caption": "1. Initial Mode: choose Delivery Date and Rit, then Search", "image": f"{IMG}/c_01_initial.png"},
  {"caption": "2. Delivery plan after Search (supplier view, case level)", "image": f"{IMG}/c_02_delivery_plan.png"},
  {"caption": "3. D/S team: destination detail (Pcs/Case, Hold Flag) and customer orders of a destination", "image": f"{IMG}/c_03_ds_detail.png"},
  {"caption": "4. D/S team: destination on hold; the unit is computed again (Ready)", "image": f"{IMG}/c_04_ds_hold.png"},
  {"caption": "5. Units of different Customer Order Dates selected", "image": f"{IMG}/c_05_selected.png"},
  {"caption": "5a. Other session (D/S team) holds a destination of a ticked unit", "image": f"{IMG}/c_05a_ds_hold_other_session.png"},
  {"caption": "5b. Create ASN: hold message, the whole create fails", "image": f"{IMG}/c_05c_hold_conflict.png"},
  {"caption": "5c. Delivery plan refreshed automatically, all units unticked", "image": f"{IMG}/c_05d_after_refresh.png"},
  {"caption": "6. Case List sub screen", "image": f"{IMG}/c_06_case_list.png"},
  {"caption": "7. Case List: PO detail of a case", "image": f"{IMG}/c_07_case_expand.png"},
  {"caption": "8. Submit confirmation", "image": f"{IMG}/c_08_confirm.png"},
  {"caption": "9. Submit ID banner (result in Log Monitoring)", "image": f"{IMG}/c_09_submit_id.png"},
  {"caption": "10. Delivery plan after submit (Created units are no longer listed)", "image": f"{IMG}/c_10_list_after.png"}],
 "items": [
  {"group": "<Delivery Section>"},
  it("Delivery Date", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Today (business date)", "Y", "DD-Mon-YYYY", "Mandatory; today or later", "Changing it reloads the Rit list."),
  it("Rit", "TBD (Route Master)", "TBD", "Char", "TBD", "I", "Combo Box", "Left", "First rit of the date", "Y", "-", "Mandatory", "Rits of the Delivery Date; Sunday none ('No rit cycle'), Saturday one."),
  out("Route", "TBD (Route Master)", "TBD", "Char", "TBD", "Text box (disabled)", "Left", "-", "Route of the Rit."),
  btn("Search", "Refer Operation Description 5.1."),
  {"group": "<Delivery Plan Section>"},
  out("Counter", "Computed", "-", "Char", "-", "Label", "Left", "-", "'{Delivery Date} · {Rit} · {Route} — {n} units · {r} ready · {w} not ready'."),
  it("Part Number (filter)", "Key-in", "-", "Char", "15", "I", "Combo Box", "Left", "All", "N", "-", "-", "Filters the delivery plan at once."),
  it("Status (filter)", "Key-in", "-", "Char", "-", "I", "Combo Box", "Left", "All", "N", "-", "-", "All / Ready / Not Ready (D/S team also On Hold). Filters at once."),
  it("Select (check box)", "Key-in", "-", "Char", "1", "I", "CheckBox", "Center", "<unchecked>", "N", "-", "Enabled only for Ready units", "Several units can be ticked. Refer Screen Mode remark 1)."),
  out("Customer Order Date", INSTR, "ORDER_DT", "Date", "-", "Label", "Left", "DD-Mon-YYYY", "Customer Order Date of the unit."),
  out("Part Number", INSTR, "PART_NO", "Char", "15", "Label", "Left", "-", "Part number of the unit (distinct per Customer Order Date). Part name is not shown."),
  out("Case Qty", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of cases of the unit: the qty of each destination is summed into one case."),
  out("PO Readiness (case)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Cases whose whole qty is pre-mapped to a PO; red when lower than Case Qty."),
  out("ASN Status", INSTR, "CROSSDOCK_STATUS", "Char", "1", "Label", "Left", "-", "'6' Ready (green) / '7' Not Ready (amber, row highlighted) / On Hold (D/S only). Refer 5.2."),
  btn("Detail (expand, D/S)", "Shown to the D/S team only. Opens the destination detail."),
  {"group": "<Destination Detail (D/S team only)>"},
  out("Destination", INSTR, "DESTINATION_CD", "Char", "7", "Grid", "Left", "{code} · {name}", "One row per destination (= one case); name from " + DM + "."),
  out("Case", "Computed", "-", "Number", "-", "Grid", "Right", "9", "1; 0 when the destination is on hold."),
  out("Qty (pcs)", INSTR, "CUST_ORDER_QTY", "Number", "8", "Grid", "Right", "ZZ,ZZ9", "Sum of the order qty of the destination; '(on hold)' when held."),
  out("Pcs/Case", "Part master", "PCS_PER_CASE", "Number", "-", "Grid", "Right", "ZZ9", "Pieces per case of the part (next to Qty)."),
  btn("Customer orders (expand, D/S)", "Opens the customer order lines of the destination."),
  {"group": "<Customer Orders of a Destination (D/S team only)>"},
  out("Customer Order No / Detailed Item No", INSTR, "CUSTOMER_ORDER_NO / DETAILED_ITEM_NO", "Char", "-", "Grid", "Left", "-", "Original order row, e.g. order A 4 pcs and order B 2 pcs to Vietnam."),
  out("Qty (pcs) / PO No / PO Date", INSTR, "CUST_ORDER_QTY / PO_NO / PO_ORDER_DT", "Char", "-", "Grid", "Left", "-", "Pre-mapping of the line."),
  btn("Hold / Release (D/S)", "Hold Flag of the destination: 'N · Hold' sets Y, 'Y · Release' sets N on every order line of the destination. Refer 5.3."),
  {"group": "<Selection Bar Section>"},
  out("Selection summary", "Computed", "-", "Char", "-", "Label", "Left", "-", "'{n} units selected · {c} cases · {units}'. Empty: hint that units of different dates can go into one ASN."),
  btn("Clear selection", "Unticks all units.", "Disabled"), btn("Create ASN", "Refer Operation Description 5.4.", "Disabled"),
  {"group": "<Case List Sub Screen - ASN Summary>"},
  btn("Back", "Returns to ASN Crossdock Creation without submitting; the draft mapping is released."),
  out("ASN No", ASNH, "ASN_NO", "Char", "TBD", "Label", "Left", "-", "Existing numbering; 'auto · assigned on submit'."),
  out("Supplier · Plant", INSTR, "SUPPLIER_CD / SUPPLIER_PLANT", "Char", "TBD", "Label", "Left", "-", "Supplier of the cases."),
  out("Delivery Date · Rit · Route", DRAFT, "DELIVERY_DT / RIT_CYCLE / ROUTE", "Char", "-", "Label", "Left", "-", "From the Search."),
  out("Delivery Qty", "Computed", "-", "Number", "-", "Label", "Left", "ZZ,ZZ9 pcs", "Total pieces of the ASN."),
  out("Cases", "Computed", "-", "Number", "-", "Label", "Left", "N cases", "Number of cases."),
  {"group": "<Case List Sub Screen - Case List>"},
  btn("Download Case Label", "Downloads the labels of all cases. TBD format."),
  btn("PO detail (expand)", "Opens the PO detail of the case."),
  out("Case Number", DRAFT, "CASE_SEQ", "Char", "-", "Grid", "Left", "Case {n}", "Case sequence; the case number (existing numbering) is assigned on submit."),
  out("Part Number", DRAFT, "PART_NO", "Char", "15", "Grid", "Left", "-", "One case per Part Number + Customer Order Date + destination."),
  out("Qty / Total", DRAFT, "QTY", "Number", "-", "Grid", "Right", "ZZ,ZZ9", "Pieces of the case; total of all cases."),
  out("PO No / Manifest No / Manifest Item No / PO Qty", DRAFT, "PO_NO / MANIFEST_NO / MANIFEST_ITEM_NO / PO_ORDER_QTY", "Char", "-", "Grid", "Left", "-", "Expanded PO detail of the case."),
  btn("Cancel", "Same as Back."), btn("Submit ASN", "Refer Operation Description 5.5."),
  out("No rit cycle message", "Computed", "-", "Char", "-", "Label", "Left", "-", "Message no. 5 when no rit is available.")],
 "data_map": {"blocks": [
  {"source": "Hold / Release (D/S)", "destination": {"table": H0253, "operation": "Update", "description": "Every order line of the destination of the button",
                                                      "keys": [{"field": "SHIPPING_PART_NO + ORDER_DT + DESTINATION_CD", "value": "Unit and destination of the button"}]},
   "mappings": [{"dest_field": "HOLD_FLAG", "description": "'Y' (hold) / 'N' (release)"}, {"dest_field": "PO_MAPPED_FLAG", "description": NC},
                {"dest_field": "UPDATE_BY", "description": "Login user ID"}, {"dest_field": "UPDATE_DT", "description": "Server system date-time"}]},
  {"source": INSTR + " (selected units)", "destination": {"table": H0253, "operation": "Update", "description": "[Create ASN]: every line of the selected units",
                                                          "keys": [{"field": "Unique key (customer order line incl. SERIAL_NO)", "value": "Lines of the selected units"}]},
   "mappings": [{"dest_field": "PO_MAPPED_FLAG", "description": "'Y' (mapped); back to 'N' on Back / Cancel"}, {"dest_field": "HOLD_FLAG", "description": NC},
                {"dest_field": "UPDATE_BY", "description": "Login user ID"}, {"dest_field": "UPDATE_DT", "description": "Server system date-time"}]},
  {"source": INSTR + " (selected units)", "destination": {"table": PRA_P, "operation": "Update", "description": "[Create ASN]: PO parts used by the selected units"},
   "mappings": [{"dest_field": "Mapped qty (column TBD)", "description": "+ ASSIGNED_QTY of the selected units; back on Back / Cancel"}]},
  {"source": INSTR + " (selected units)", "destination": {"table": DRAFT, "operation": "Insert", "description": "[Create ASN]: one row per case x line x PO"},
   "mappings": [{"dest_field": "CASE_SEQ", "description": "Case sequence: selected unit, then first appearance of the destination"},
                {"dest_field": "LINE_SEQ", "description": "Sequence within the case"}] +
               [{"source_field": c[0], "dest_field": c[0]} for c in DRAFT_COLS if c[0] in ("PART_NO", "ORDER_DT", "DESTINATION_CD", "CUSTOMER_CD", "CUSTOMER_ORDER_NO", "DETAILED_ITEM_NO", "SERIAL_NO", "PO_NO", "MANIFEST_NO", "MANIFEST_ITEM_NO", "PO_ORDER_QTY")] +
               [{"source_field": "ASSIGNED_QTY", "dest_field": "QTY"}, {"source_field": "Delivery Date", "dest_field": "DELIVERY_DT"},
                {"source_field": "Rit", "dest_field": "RIT_CYCLE"}, {"source_field": "Route", "dest_field": "ROUTE"}]}]},
 "operation": [
  {"type": "heading", "text": "5.1 Initial Display and Search"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "On first display Delivery Date = today (business date), Rit = first rit of the date, Route displayed (disabled). The delivery plan is empty.",
    "[Search] runs the function X12 Get Order (UISS X12): customer orders of H0253 with order status 7, Hold Flag N, not mapped, earliest order date first per part number (FIFO), pre-mapped to the PO parts of the Pra Daily Order (FIFO PO date) in the temporary table #TB_R_INSTRUCTION.",
    "The delivery plan shows one row per Part Number + Customer Order Date, sorted Ready, Not Ready, then Part Number ascending. Units with PO Readiness 0 and units already Created (in a submitted ASN) are not listed. Part Number and Status filters apply at once. No row: message no. 3.",
    "Delivery Date and Rit do not filter the orders; they are carried to the ASN."]},
  {"type": "heading", "text": "5.2 Status Rule"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "Unit = Part Number + Customer Order Date. Case = one per destination; the qty of a destination is summed into one case (it never exceeds pcs/case, it may be split over several lines, e.g. 4 + 2).",
    "Case Qty = number of destinations. PO Readiness (case) = cases whose whole qty is pre-mapped to a PO.",
    "Ready ('6'): every line of the unit is pre-mapped to a PO. Not Ready ('7'): at least one line of the unit has no PO yet (check box disabled, message no. 2). With POs of different PO Dates the unit becomes Ready when the last PO is available (condition 3).",
    "Created: the unit is in a submitted ASN (ASN status '1'); it is no longer listed (shown in ASN Inquiry)."]},
  {"type": "heading", "text": "5.3 Detail and Hold (D/S team)"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "The D/S team can expand a unit: one row per destination with Case, Qty (pcs), Pcs/Case and Hold Flag; each destination can be expanded to its customer order lines (Customer Order No, Detailed Item No, Qty, PO No, PO Date). The supplier sees the header only.",
    "Hold / Release is done per destination: it updates HOLD_FLAG of every order line of the unit and destination in TB_R_H0253_ORDER_CONTROL_PRE (refer Data Edit Mapping). A held destination is not taken by Search; the unit is computed without it. A unit with all destinations on hold is shown as On Hold to the D/S team only.",
    "HOLD_FLAG is 'N' when the line is first replicated (X10) and is kept on the next replications."]},
  {"type": "heading", "text": "5.4 Select Units and Create ASN"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "The user ticks one or more Ready units, also of different Customer Order Dates and Part Numbers. A unit is never split.",
    "[Create ASN] does the real mapping of the selected units in one transaction: PO_MAPPED_FLAG = 'Y' on their H0253 lines, mapped qty on the Pra Daily Order parts, and the ASN draft in #TEMP_ASN_DRAFT (one case per Part Number + Customer Order Date + destination). Then the Case List opens.",
    "Before mapping, the ticked units are re-checked in the same transaction (row lock on the H0253 lines): if a line got HOLD_FLAG = 'Y' after the unit was ticked (e.g. the D/S team held a destination in another session), the creation fails for the whole selection (also the units that are not held): message no. 8 (Hold), the delivery plan is refreshed automatically and all ticked units are unticked. If a unit is no longer Ready for another reason (changed by another user), message no. 7.",
    "[Back] / [Cancel] on the Case List release the mapping (flags and mapped qty back) and clear the draft."]},
  {"type": "heading", "text": "5.5 Case List and Submit ASN"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "The summary shows ASN No (assigned on submit), supplier, Delivery Date · Rit · Route of the Search, Delivery Qty (pcs) and number of cases.",
    "Each case shows Case Number, Part Number and Qty; the expand shows PO No, Manifest No, Manifest Item No and PO Qty. Customer order data is not shown here.",
    "[Download Case Label]: TBD (format, file name, content).",
    "[Submit ASN]: confirmation (message no. 4). Yes: the draft is handed with a Submit ID to the batch X14 ASN Submit (UISS X14); the submit process follows the existing ASN. X14 inserts TB_R_ASN_CROSSDOCK_H (ASN_STATUS '1' Created) and TB_R_ASN_CROSSDOCK_D with the existing ASN / case numbering. The screen returns to the delivery plan and shows the Submit ID (message no. 6); there is no success popup. The result message is written by X14 to the existing log (Log Monitoring)."]},
  {"type": "heading", "text": "5.6 Notes"},
  {"type": "bullets", "marker": "-", "level": 2, "items": [
    "#TB_R_INSTRUCTION and #TEMP_ASN_DRAFT are temporary tables. Submitted ASNs are shown in ASN Inquiry (X13).",
    "The prototype has a 'Business date' switch (PO release) and a 'View as' switch (Supplier / D/S team); they are not part of the real screen."]}],
 "display_messages": [
  {"group": "Delivery Plan (tooltip of disabled check box)"},
  {"event": "Hover on disabled check box", "cause": "Unit is On Hold (D/S)", "type": "Info", "msg_id": "MSG1", "message": "All destinations are on hold", "action": "Release a destination."},
  {"event": "Hover on disabled check box", "cause": "Unit is Not Ready", "type": "Info", "msg_id": "MSG2", "message": "Not Ready: {k} of {n} cases of {Part No} / {Customer Order Date} are not assigned to a PO yet", "action": "Wait for the next PO."},
  {"group": "Search"},
  {"event": "Click [Search] / change filter", "cause": "No unit", "type": "Info", "msg_id": "MSG3", "message": "No customer order matches this filter.", "action": "Change the Delivery Date, Rit or filter."},
  {"event": "Change [Delivery Date]", "cause": "No rit on the date (Sunday)", "type": "Info", "msg_id": "MSG5", "message": "No rit cycle available for {Delivery Date}. Choose another delivery date.", "action": "Choose another Delivery Date."},
  {"group": "Create ASN / Case List"},
  {"event": "Click [Create ASN]", "cause": "A selected unit is no longer Ready", "type": "Error", "msg_id": "MSG7", "message": "{Part No} / {Customer Order Date} is no longer Ready. The delivery plan is refreshed.", "action": "Select again."},
  {"event": "Click [Submit ASN] button", "cause": "Confirmation", "type": "Confirm", "msg_id": "MSG4", "message": "Submit ASN? {n} cases ({q} pcs) will be created into {ASN No}, delivery {Delivery Date} · {Rit}.", "action": "Click [Yes, submit] or [No]."},
  {"event": "Click [Yes, submit]", "cause": "Submit handed to the batch X14", "type": "Info", "msg_id": "MSG6", "message": "Submit ID {Submit ID} is sent to the ASN submit batch. The result is written to Log Monitoring.", "action": "Check Log Monitoring."},
  {"event": "Click [Create ASN]", "cause": "A ticked unit has an order put on hold by the D/S team after it was ticked", "type": "Error", "msg_id": "MSG8", "message": "Some order has been already hold, please select other records. The delivery plan has been refreshed.", "action": "Click [OK]; the delivery plan is already refreshed and all units are unticked; select again."}],
 "logging_messages": [
  {"event": "Click [Create ASN]", "cause": "Database error on mapping / draft", "type": "Error", "msg_id": "LOG1", "message": "Failed to create the ASN draft: <DB error message>.", "exception": "Y", "action": "Roll back; show [Corresponding Screen Message] on screen (TBD)"}],
 "tables": [INSTR_TABLE, DRAFT_TABLE]
}
# Update blocks on H0253: every other column is not changed
for blk in spec["data_map"]["blocks"][:2]:
    have = {m["dest_field"] for m in blk["mappings"]}
    blk["mappings"] += [{"dest_field": c, "description": NC} for c in H0253_FULL if c not in have]
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
