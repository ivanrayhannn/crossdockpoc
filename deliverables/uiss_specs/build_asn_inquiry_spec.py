"""Spec for X13_UISS_Screen_ASNInquiry.xlsx (UISS-Screen, ASN Inquiry)."""
import json, sys
from asn_common import ASND, ASND_TABLE, ASNH, ASNH_TABLE, btn, header, it, out, revisions

IMG = 'deliverables/uiss_screens/asn_crossdock'
B = ["Search", "Reset", "ASN No (link)", "Back", "Download Case Label"]


def modes(on):
    return {b: ("E" if b in on else "D") for b in B}


spec = {
 "doc_type": "screen",
 "header": header("X13", "Screen", "ASN Inquiry", '15-Oct-26'),
 "revisions": revisions('15-Oct-26'),
 "general": {
  "objective": ["To search the ASNs submitted in ASN Crossdock Creation (X8).", "To display the cases of one ASN (read only) and download its case labels."],
  "display_order": [{"section": "ASN list", "fields": [{"field": "Submit date-time (CREATED_DT)", "order": "Descending"}]},
                    {"section": "Cases", "fields": [{"field": "Case No", "order": "Ascending"}]}],
  "buttons": [
   {"name": "Search", "function": "Retrieve ASNs by ASN No, Delivery Date range and Part Number."},
   {"name": "Reset", "function": "Clear criteria and reset the screen to its initial value."},
   {"name": "ASN No (link)", "function": "Open the detail of the ASN."},
   {"name": "Back", "function": "Return from the detail to the ASN list."},
   {"name": "Download Case Label", "function": "Download the labels of all cases of the ASN. Label format follows the existing case label."}],
  "screen_modes": [
   {"mode": "List Mode", "sections": [
     {"section": "Search Criteria", "description": "Criteria blank; all ASNs listed", "buttons": modes(["Search", "Reset"])},
     {"section": "ASN list", "description": "One row per ASN", "buttons": modes(["ASN No (link)"])}]},
   {"mode": "Detail Mode", "sections": [
     {"section": "ASN summary", "description": "Delivery Date, Rit Cycle, units, cases / qty, created", "buttons": modes(["Back"])},
     {"section": "Cases", "description": "Read-only case list", "buttons": modes(["Download Case Label"])}]}]
 },
 "screen_flow": [
  {"title": "Screen Flow - ASN Inquiry", "flow": {"direction": "LR", "nodes": [
     {"id": "c", "label": "ASN Crossdock Creation (X8)", "type": "screen"},
     {"id": "l", "label": "ASN Inquiry - list", "type": "screen"},
     {"id": "d", "label": "ASN Inquiry - detail", "type": "screen"}],
    "edges": [{"from": "c", "to": "l", "label": "submitted ASN"}, {"from": "l", "to": "d", "label": "ASN No"}, {"from": "d", "to": "l", "label": "Back"}]}}],
 "screen_layout": [
  {"caption": "1. List Mode", "image": f"{IMG}/c_11_inquiry.png"},
  {"caption": "2. Detail Mode", "image": f"{IMG}/c_12_inquiry_detail.png"}],
 "items": [
  {"group": "<Search Criteria Section>"},
  it("ASN No", "Key-in", "-", "Char", "TBD", "I", "Text box", "Left", "Blank", "N", "-", "Contains, case-insensitive", "Enter = [Search]."),
  it("Delivery Date - From / To", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Blank", "N", "DD-Mon-YYYY", "-", "Range of Delivery Date, inclusive."),
  it("Part Number", "Key-in", "-", "Char", "15", "I", "Combo Box", "Left", "All", "N", "-", "-", "ASNs that contain the part."),
  btn("Search", "Refer Operation Description 5.1."), btn("Reset", "Refer Operation Description 5.1."),
  {"group": "<ASN List Section>"},
  out("ASN No", ASNH, "ASN_NO", "Char", "TBD", "Link", "Left", "-", "Opens Detail Mode."),
  out("Delivery Date", ASNH, "DELIVERY_DT", "Date", "-", "Label", "Left", "DD-Mon-YYYY", ""),
  out("Rit Cycle / Route", ASNH, "RIT_CYCLE / ROUTE", "Char", "TBD", "Label", "Left", "-", ""),
  out("Part / Customer Order Date", ASND, "PART_NO / ORDER_DT", "Char", "-", "Label", "Left", "-", "Units of the ASN."),
  out("Cases / Qty", ASNH, "TOTAL_CASE / TOTAL_QTY", "Number", "-", "Label", "Right", "ZZ9 / ZZ,ZZ9", ""),
  out("Status", ASNH, "ASN_STATUS", "Char", "TBD", "Label", "Left", "-", "'1' Created (green)."),
  out("Created", ASNH, "CREATED_BY / CREATED_DT", "Char", "-", "Label", "Left", "DD-Mon-YYYY HH:MM", "User and date-time of submit."),
  {"group": "<Detail Mode>"},
  btn("Back", "Returns to the ASN list."),
  out("ASN summary", ASNH, "-", "Char", "-", "Label", "Left", "-", "Delivery Date, Rit Cycle · Route, units, cases · qty, created."),
  btn("Download Case Label", "Downloads the labels of all cases (existing label format)."),
  out("Case No", ASND, "CASE_NO", "Char", "TBD", "Grid", "Left", "-", "Case number of the ASN."),
  out("Part Number / Customer Order Date / Destination", ASND, "PART_NO / ORDER_DT / DESTINATION_CD", "Char", "-", "Grid", "Left", "-", "Key of the case."),
  out("Customer Order No (qty) / PO No / Qty", ASND, "CUSTOMER_ORDER_NO / PO_NO / QTY", "Char", "-", "Grid", "Left", "-", "Order lines packed in the case; total of all cases.")],
 "data_map": {"blocks": []},
 "operation": [
  {"type": "heading", "text": "5.1 List Mode"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "On first display all crossdock ASNs of the existing table TB_R_DAILY_ORDER_MANIFEST are listed, newest first. Supplier: its own Supplier Code + Plant; D/S team: all suppliers.",
    "[Search] applies ASN No (contains), Delivery Date range and Part Number (ASNs whose cases contain the part). [Reset] clears them. No row: message no. 1.",
    "Clicking an ASN No opens Detail Mode."]},
  {"type": "heading", "text": "5.2 Detail Mode"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "Shows the ASN summary and its cases from the existing table TB_R_DAILY_ORDER_PART (rows with the ASN No), grouped by CASE_NO. All items are read only.",
    "[Download Case Label]: follows the existing case label of NSP. [Back] returns to the list in the current search state.",
    "The screen does not change data (display only). There is no Cancel ASN: an order is cancelled in the source (H0253 order status '2') for lines already on hold (HOLD_FLAG = 'Y'), not in NSP (refer X10)."]}],
 "display_messages": [
  {"group": "Search Operation"},
  {"event": "Click [Search] button", "cause": "No ASN matches", "type": "Info", "msg_id": "MSG1", "message": "No ASN matches this search.", "action": "Change the criteria."}],
 "logging_messages": [],
 "tables": [ASNH_TABLE, ASND_TABLE]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
