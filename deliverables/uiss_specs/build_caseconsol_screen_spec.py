"""Spec for X8_UISS_Screen_DeliveryPlan_ASNDraft.xlsx (UISS-Screen, Case Consolidation - Delivery Plan and ASN Draft).
Merges the former separate UISS-Screens Delivery Plan and ASN Draft into one document."""
import json, sys

IMG = 'deliverables/uiss_screens/case_consolidation'
NAME, PROJ = 'FID Rayhan', 'Crossdock Optimization'


def it(name, source='', field='', type_='', len_='', io='', control='', just='', init='', req='', fmt='', val='', desc=''):
    return {"name": name, "source": source, "field": field, "type": type_, "len": len_, "io": io, "control": control,
            "justified": just, "initial": init, "required": req, "format": fmt, "validation": val, "description": desc}


def btn(name, desc, init='Enabled'):
    return it(name, '-', '-', '-', '-', 'I', 'Button', 'Center', init, 'N', '-', '-', desc)


def out(name, source, field, type_, len_, control, just, fmt, desc, init='-'):
    return it(name, source, field, type_, len_, 'O', control, just, init, 'N', fmt, '-', desc)


B = ["Search", "Reset", "View detail", "Clear selection", "Group into 1 ASN", "Back to Delivery Plan",
     "Download All Case Labels", "Cancel", "Submit ASN"]


def modes(on):
    return {b: ("E" if b in on else "D") for b in B}


CO = 'TBD (Customer Order)'
PO = 'TBD (Supplier PO)'

spec = {
 "doc_type": "screen",
 "header": {"phase": "DR", "project_name": PROJ, "block_name": "Screen",
            "function_name": "X8 Case Consolidation - Delivery Plan and ASN Draft", "created_date": "05-Oct-26", "created_by": NAME},
 "revisions": [{"revision": "0.1", "author": NAME, "date": "05-Oct-26", "reviewed_by": "", "description": "Initial Draft"}],
 "general": {
  "objective": [
   "To display the delivery plan per Customer Order Date with its status (Ready to ASN / Waiting Released), the cases and pieces released to supplier POs, and the ASN number when the cases are already grouped.",
   "To display, for one selected Customer Order Date, the customer-order lines with Part No, quantity, supplier PO and case (Detail in Detail).",
   "To select one Ready to ASN Customer Order Date and open the ASN Draft, so that all cases of that date are grouped into one ASN.",
   "To enter the Delivery Date and Rit of the ASN, submit it (all cases of the date are locked) and display the submitted ASN read only."],
  "display_order": [
   {"section": "Delivery Plan Header", "fields": [{"field": "Customer Order Date", "order": "Ascending"}]},
   {"section": "Detail in Detail", "fields": [{"field": "Released cases (PO No, then Case No)", "order": "Ascending"},
                                              {"field": "Lines Waiting (not paired with a PO yet), after the released cases", "order": "Ascending"}]},
   {"section": "ASN Draft - Case list", "fields": [{"field": "PO No / Case No (release order)", "order": "Ascending"},
                                                   {"field": "Part No inside a case", "order": "Ascending"}]}],
  "buttons": [
   {"name": "Search", "function": "To retrieve the Delivery Plan Header according to the Customer Order Date range and Status."},
   {"name": "Reset", "function": "Clear criteria and reset the screen to its initial value."},
   {"name": "View detail", "function": "Change the screen into Detail Mode to display the Detail in Detail of the selected Customer Order Date. Not available to the Supplier."},
   {"name": "Clear selection", "function": "To clear the selected Customer Order Date."},
   {"name": "Group into 1 ASN", "function": "To open the ASN Draft with all cases of the selected Customer Order Date."},
   {"name": "Back to Delivery Plan", "function": "To return to the Delivery Plan Header (from Detail Mode or from the ASN Draft without submitting)."},
   {"name": "Download All Case Labels", "function": "To download the labels of all cases in the ASN. TBD: function and label format are not defined yet."},
   {"name": "Cancel", "function": "To discard the ASN Draft and return to the Delivery Plan Header."},
   {"name": "Submit ASN", "function": "To submit the ASN for all cases of the Customer Order Date and lock them."}],
  "screen_modes": [
   {"mode": "List Mode - No Selection", "sections": [
     {"section": "Searching Criteria", "description": "Criteria blank (Status = All); all dates listed on first display", "buttons": modes(["Search", "Reset"])},
     {"section": "Delivery Plan Header", "description": "One row per Customer Order Date; no date ticked", "buttons": modes(["View detail"])},
     {"section": "Selection Bar", "description": "No order date selected", "buttons": modes([])}]},
   {"mode": "List Mode - Date Selected", "sections": [
     {"section": "Searching Criteria", "description": "Refer 1.a", "buttons": modes(["Search", "Reset"])},
     {"section": "Delivery Plan Header", "description": "One Ready to ASN date ticked; check boxes of all other dates disabled", "buttons": modes(["View detail"])},
     {"section": "Selection Bar", "description": "Selected date, cases, pieces and supplier PO numbers", "buttons": modes(["Clear selection", "Group into 1 ASN"])}]},
   {"mode": "Detail Mode", "sections": [
     {"section": "Date Summary", "description": "Customer Order Date, status, supplier POs and case summary", "buttons": modes(["Back to Delivery Plan"])},
     {"section": "Detail in Detail", "description": "Read-only list of the customer-order lines of the date", "buttons": modes([])}]},
   {"mode": "ASN Draft Mode", "sections": [
     {"section": "ASN Summary", "description": "ASN No auto ('assigned on submit'); Supplier / Plant and Cases / Qty read only", "buttons": modes(["Back to Delivery Plan"])},
     {"section": "Case list in this ASN", "description": "Delivery Date and Rit editable; case list read only", "buttons": modes(["Download All Case Labels"])},
     {"section": "Footer", "description": "Submit available when there are cases, a Delivery Date and a Rit", "buttons": modes(["Cancel", "Submit ASN"])}]},
   {"mode": "ASN Submitted Mode", "sections": [
     {"section": "ASN Summary", "description": "ASN No in the title; success alert displayed", "buttons": modes(["Back to Delivery Plan"])},
     {"section": "Case list in this ASN", "description": "All fields read only", "buttons": modes(["Download All Case Labels"])},
     {"section": "Footer", "description": "Footer buttons hidden", "buttons": modes([])}]}],
  "screen_mode_remarks": [
   "1) The check box of a Customer Order Date is enabled only when its status is Ready to ASN, its cases are not yet in an ASN and no other date is ticked (message no. 1 to 3 as tooltip of a disabled check box).",
   "2) 'View detail' is hidden for the Supplier role, who only sees the Delivery Plan Header. Demand Supply and Procurement see the button (TBD: confirm role rule with business user).",
   "3) Search and Reset return the screen to the Delivery Plan Header and clear the Detail Mode selection.",
   "4) 'Download All Case Labels' is enabled only when the case list is not empty.",
   "5) 'Submit ASN' is enabled only when the case list is not empty, 'Delivery Date' is filled and a Rit is available.",
   "6) In ASN Submitted Mode the footer (Cancel, Submit ASN) is hidden; 'Back to Delivery Plan' in the title bar is used to leave the screen."]
 },
 "screen_flow": [
  {"title": "Screen Flow - Delivery Plan and ASN Draft", "flow": {"direction": "LR", "nodes": [
     {"id": "list", "label": "Delivery Plan Header", "type": "screen"},
     {"id": "det", "label": "Detail in Detail", "type": "screen"},
     {"id": "draft", "label": "ASN Draft", "type": "screen"},
     {"id": "sub", "label": "ASN Submitted", "type": "screen"}],
    "edges": [{"from": "list", "to": "det", "label": "View detail"}, {"from": "det", "to": "list", "label": "Back to Delivery Plan"},
              {"from": "list", "to": "draft", "label": "Group into 1 ASN"}, {"from": "draft", "to": "list", "label": "Cancel / Back"},
              {"from": "draft", "to": "sub", "label": "Submit ASN"}, {"from": "sub", "to": "list", "label": "Back to Delivery Plan"}]},
   "notes": ["Search, Reset, ticking a date and Clear selection stay on the Delivery Plan Header."]},
  {"title": "Screen Flow - Select Date and Group into ASN", "flow": {"direction": "TB", "nodes": [
     {"id": "s", "label": "START", "type": "start"},
     {"id": "e", "label": "User ticks a Customer Order Date", "type": "event"},
     {"id": "d1", "label": "Ready to ASN, not in ASN, no other date ticked?", "type": "decision"},
     {"id": "m1", "label": "Check box disabled (message no. 1-3)", "type": "message"},
     {"id": "p1", "label": "Select all cases of the date (all POs), show Selection Bar", "type": "process"},
     {"id": "e2", "label": "On Click of Group into 1 ASN", "type": "event"},
     {"id": "p2", "label": "Open ASN Draft with all cases of the date", "type": "process"},
     {"id": "x", "label": "END", "type": "end"}],
    "edges": [{"from": "s", "to": "e"}, {"from": "e", "to": "d1"}, {"from": "d1", "to": "m1", "label": "No"},
              {"from": "d1", "to": "p1", "label": "Yes"}, {"from": "p1", "to": "e2"}, {"from": "e2", "to": "p2"}, {"from": "p2", "to": "x"}]}},
  {"title": "Screen Flow - Submit ASN", "flow": {"direction": "TB", "nodes": [
     {"id": "s", "label": "START", "type": "start"},
     {"id": "e", "label": "On Click of Submit ASN", "type": "event"},
     {"id": "d1", "label": "All cases of one Ready to ASN date, Delivery Date and Rit filled?", "type": "decision"},
     {"id": "m1", "label": "Reject (message TBD)", "type": "message"},
     {"id": "p1", "label": "Generate ASN No, lock cases, insert ASN Header / Detail", "type": "process"},
     {"id": "db", "label": "ASN Header / ASN Detail (TBD)", "type": "db"},
     {"id": "m2", "label": "ASN Submitted Mode (message no. 6)", "type": "message"},
     {"id": "x", "label": "END", "type": "end"}],
    "edges": [{"from": "s", "to": "e"}, {"from": "e", "to": "d1"}, {"from": "d1", "to": "m1", "label": "No"},
              {"from": "d1", "to": "p1", "label": "Yes"}, {"from": "p1", "to": "db", "style": "dashed"}, {"from": "p1", "to": "m2"}, {"from": "m2", "to": "x"}],
    "same_rank": [["p1", "db"]]}}],
 "screen_layout": [
  {"caption": "1. List Mode - No Selection (initial display)", "image": f"{IMG}/c_01_list_no_selection.png"},
  {"caption": "2. List Mode - Date Selected", "image": f"{IMG}/c_02_list_date_selected.png"},
  {"caption": "3. List Mode - After Search (Status = Waiting Released)", "image": f"{IMG}/c_03_list_after_search.png"},
  {"caption": "4. Detail Mode - Ready to ASN date (View detail)", "image": f"{IMG}/c_04_detail_ready.png"},
  {"caption": "5. Detail Mode - Waiting Released date (View detail)", "image": f"{IMG}/c_05_detail_waiting.png"},
  {"caption": "6. ASN Draft Mode", "image": f"{IMG}/c_06_asn_draft.png"},
  {"caption": "7. ASN Submitted Mode", "image": f"{IMG}/c_07_asn_submitted.png"}],
 "items": [
  {"group": "<Searching Criteria Section>"},
  it("Customer Order Date - From", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Blank", "N", "TBD", "TBD", "Lower limit of Customer Order Date, inclusive. Blank = no lower limit."),
  it("Customer Order Date - To", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Blank", "N", "TBD", "TBD (From > To not handled yet, see Operation Description 5.1.2 b)", "Upper limit of Customer Order Date, inclusive. Blank = no upper limit."),
  it("Status", "Key-in", "-", "Char", "-", "I", "Combo Box", "Left", "All", "N", "-", "-", "Options: All, Ready to ASN, Waiting Released. Ready to ASN = every order of the date is paired with a PO. Waiting Released = at least one order (or part of it) of the date has no PO yet."),
  btn("Search", "Refer Operation Description 5.1.2."),
  btn("Reset", "Refer Operation Description 5.1.2."),
  {"group": "<Delivery Plan Header Section>"},
  out("Dates (count)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of Customer Order Dates in the result.", "0"),
  out("Ready (count)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of dates with status Ready to ASN in the result.", "0"),
  out("Waiting (count)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of dates with status Waiting Released in the result.", "0"),
  it("Select (check box)", "Key-in", "-", "Char", "1", "I", "CheckBox", "Center", "<unchecked>", "N", "-", "Enabled only for a Ready to ASN date not yet in an ASN and when no other date is ticked",
     "Ticking selects all cases of the Customer Order Date, across all of its supplier POs. Only one date can be ticked (one ASN = one Customer Order Date). If all cases of the date are already in an ASN the box is ticked and disabled. See Screen Mode remark 1)."),
  out("Customer Order Date", CO, "TBD", "Date", "-", "Label", "Left", "DD-Mon-YYYY", "One row per Customer Order Date that has released cases or orders not yet released. Bold. Sorted ascending."),
  out("ASN Number", "TBD (ASN)", "TBD", "Char", "TBD", "Label", "Left", "-", "ASN numbers of the cases of this date, separated by ', '. '-' when no case is in an ASN yet."),
  out("Status (status pill)", "Computed", "-", "Char", "-", "Label", "Left", "-", "'Ready to ASN' (green) when every order of the date is paired with a supplier PO; otherwise 'Waiting Released' (amber). See Operation Description 5.1.3."),
  out("Cases", "Computed", "-", "Char", "-", "Label", "Left", "N cases . N pcs", "'{n} cases . {pcs} pcs' where pcs = cases x Pcs/Case. When some pieces are not released: ' . {k} pcs not released'. When no case is released: 'no case released'."),
  btn("View detail", "Opens Detail Mode of the row's Customer Order Date. Hidden for the Supplier role."),
  {"group": "<Selection Bar Section>"},
  out("Selected date count", "Computed", "-", "Number", "-", "Badge", "Center", "9", "1 when a date is ticked, otherwise 0.", "0"),
  out("Selection summary", "Computed", "-", "Char", "-", "Label", "Left", "-", "'Order date {DD-Mon-YYYY} . {n} cases . {pcs} pcs'; second line lists the supplier PO numbers of the date. Empty state: 'Tick a Ready to ASN date. One ASN = one Customer Order Date, even when it is spread over several POs.'", "No order date selected"),
  btn("Clear selection", "Unticks the selected date.", "Disabled"),
  btn("Group into 1 ASN", "Opens the ASN Draft with all cases of the selected date.", "Disabled"),
  {"group": "<Detail Mode - Date Summary Section>"},
  btn("Back to Delivery Plan", "Returns to the Delivery Plan Header."),
  out("Customer Order Date", CO, "TBD", "Date", "-", "Label", "Left", "DD-Mon-YYYY", "Date selected on the Delivery Plan Header."),
  out("Status (status pill)", "Computed", "-", "Char", "-", "Label", "Left", "-", "Same rule as the Header status."),
  out("Supplier PO", PO, "TBD", "Char", "TBD", "Label", "Right", "-", "PO numbers that contain cases of this date, separated by ', '. '-' when no PO yet."),
  out("Case summary", "Computed", "-", "Char", "-", "Label", "Right", "N cases . N pcs", "'{n} cases . {pcs} pcs' plus ' . {k} pcs not released' when applicable."),
  {"group": "<Detail in Detail Section>"},
  out("Customer Orders (count)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of distinct Customer Order numbers in the grid.", "0"),
  out("Part Nos (count)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of distinct Part No in the grid.", "0"),
  out("Cases (count)", "Computed", "-", "Number", "-", "Label", "Right", "ZZ9", "Number of distinct cases in the grid. Waiting lines have no case and are not counted.", "0"),
  out("Customer Order", CO, "TBD", "Char", "TBD", "Grid", "Left", "-", "Customer Order number with a colour dot that identifies the order across rows. One order can appear in several rows."),
  out("Destination", CO, "TBD", "Char", "TBD", "Grid", "Left", "{Name} . {Code}", "Destination of the order line. A case never mixes destinations."),
  out("Customer Order Date", CO, "TBD", "Date", "-", "Grid", "Left", "DD-Mon", "Customer Order Date of the line (day and month only)."),
  out("Customer Qty", CO, "TBD", "Number", "TBD", "Grid", "Right", "ZZ,ZZ9", "Total ordered quantity of the customer-order line."),
  out("Part No", CO, "TBD", "Char", "TBD", "Grid", "Left", "-", "Part number of the line. Bold."),
  out("Qty", "Computed", "-", "Number", "TBD", "Grid", "Right", "ZZ,ZZ9", "Quantity of this Part No / customer order packed into the case on this row (or still waiting for a PO)."),
  out("PO No", PO, "TBD", "Char", "TBD", "Grid", "Left", "-", "Supplier PO that contains the case. Em dash for a Waiting line."),
  out("PO Date", PO, "TBD", "Date", "-", "Grid", "Left", "DD-Mon-YYYY", "Date of the supplier PO. '-' for a Waiting line."),
  out("Case No", "TBD (Case)", "TBD", "Char", "TBD", "Grid", "Left", "TBD", "Case number of the line. Badge 'Waiting' when the line has no PO yet; Waiting rows are highlighted."),
  {"group": "<ASN Draft - ASN Header Section>"},
  out("Title / ASN No", "TBD (ASN)", "TBD", "Char", "TBD", "Label", "Left", "ASN-{Supplier}-{YYMMDD}-{Seq}", "Draft Mode shows the fixed text 'ASN Draft'; Submitted Mode shows the ASN No.", "ASN Draft"),
  out("Status badge", "Computed", "-", "Char", "-", "Label", "Left", "-", "'Draft' (grey) or 'Submitted' (green).", "Draft"),
  out("Information alert", "Computed", "-", "Char", "-", "Label", "Left", "-", "Draft Mode: message no. 9. Submitted Mode: message no. 6."),
  out("ASN No", "TBD (ASN)", "TBD", "Char", "TBD", "Label", "Left", "ASN-{Supplier}-{YYMMDD}-{Seq}", "Generated from the Delivery Date; note 'auto . assigned on submit' in Draft Mode, 'submitted' afterwards. Running sequence rule TBD.", "ASN-{Supplier}-{YYMMDD}-001"),
  out("Supplier . Plant", "TBD (Supplier Master)", "TBD", "Char", "TBD", "Label", "Left", "{Supplier Code} . {Plant}", "Supplier code and plant followed by the supplier name. Read only."),
  out("Cases . Qty", "Computed", "-", "Char", "-", "Label", "Left", "N cases . N pcs", "Number of cases and total pieces of the ASN. Second line: 'Order date {date} . {PO list}'."),
  {"group": "<ASN Draft - Case List Section>"},
  it("Delivery Date", "Key-in", "-", "Date", "-", "I", "Date picker", "Left", "Tomorrow (user local date)", "Y", "TBD", "Mandatory", "Delivery date of the ASN. Editable in Draft Mode only. Changing it reloads the Rit list."),
  it("Rit", "TBD (Route Master)", "TBD", "Char", "TBD", "I", "Combo Box", "Left", "First Rit of the Delivery Date", "Y", "-", "Mandatory; list depends on Delivery Date",
     "Rits available on the Delivery Date, each belonging to a route (e.g. Rit 1 = SD01). Sunday has no Rit ('No rit', disabled); Saturday has one Rit. Editable in Draft Mode only. Route master is mock data (TBD)."),
  btn("Download All Case Labels", "Downloads the labels of all cases in the ASN. Function TBD. Refer Screen Mode remark 4)."),
  out("Seq", "Computed", "-", "Number", "2", "Grid", "Left", "99", "Running number of the row (one row per case and Part No)."),
  out("Case No", "TBD (Case)", "TBD", "Char", "TBD", "Grid", "Left", "TBD", "Case number, bold."),
  out("PO No", PO, "TBD", "Char", "TBD", "Grid", "Left", "-", "Supplier PO that contains the case."),
  out("Part No", CO, "TBD", "Char", "TBD", "Grid", "Left", "-", "Part number inside the case. A case with several Part Nos is shown as several rows."),
  out("Destination", CO, "TBD", "Char", "TBD", "Grid", "Left", "{Name} . {Code}", "Destination of the case."),
  out("Route", "TBD (Route Master)", "TBD", "Char", "TBD", "Text box (disabled)", "Left", "-", "Route of the selected Rit, same for every row. '-' when there is no Rit.", "Route of the chosen Rit"),
  out("Qty", "Computed", "-", "Number", "TBD", "Grid", "Right", "ZZ,ZZ9", "Pieces of the Part No in the case."),
  out("Total", "Computed", "-", "Number", "-", "Grid footer", "Right", "ZZ,ZZ9", "Sum of Qty of all rows.", "0"),
  {"group": "<ASN Draft - Footer Section>"},
  btn("Cancel", "Returns to the Delivery Plan without submitting. Hidden in Submitted Mode."),
  btn("Submit ASN", "Submits the ASN. Hidden in Submitted Mode. Refer Screen Mode remark 5)."),
  out("No Rit message", "Computed", "-", "Char", "-", "Label", "Left", "-", "Shown in red at the left of the footer when no Rit is available (message no. 7).")],
 "data_map": {"blocks": [
  {"source": "Key-in from screen", "destination": {"table": "ASN Header (TBD)", "operation": "Insert", "description": "ASN Draft - [Submit ASN]"},
   "mappings": [
     {"source_field": "ASN No", "dest_field": "ASN No (TBD)", "description": "Generated from the Delivery Date"},
     {"source_field": "Delivery Date", "dest_field": "Delivery Date (TBD)"},
     {"source_field": "Rit", "dest_field": "Rit No (TBD)"},
     {"source_field": "Route", "dest_field": "Route (TBD)"},
     {"source_field": "Supplier / Plant", "dest_field": "Supplier . Plant (TBD)", "description": "Supplier . Plant of the cases"},
     {"dest_field": "Created By / Created Date (TBD)", "description": "Login user ID / server system date"}]},
  {"source": {"table": "Case list in this ASN (screen)", "keys": [{"field": "Case No", "value": "Cases of the Customer Order Date"}]},
   "destination": {"table": "ASN Detail (TBD)", "operation": "Insert", "description": "One row per case / Part No"},
   "mappings": [
     {"source_field": "ASN No", "dest_field": "ASN No (TBD)"},
     {"source_field": "Case No", "dest_field": "Case No (TBD)"},
     {"source_field": "PO No", "dest_field": "PO No (TBD)"},
     {"source_field": "Part No", "dest_field": "Part No (TBD)"},
     {"source_field": "Qty", "dest_field": "Qty (TBD)"}]}]},
 "operation": [
  {"type": "heading", "text": "5.1 Delivery Plan Header"},
  {"type": "heading", "text": "5.1.1 Initial Display", "level": 2},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "On first display the screen is in 'List Mode - No Selection'. 'Customer Order Date' From / To are blank and 'Status' is 'All'; all Customer Order Dates are listed without clicking 'Search'.",
    "A Customer Order Date is listed when it has at least one case released to a supplier PO, or has quantity that is not released yet.",
    "Rows are sorted by 'Customer Order Date' ascending. Header counts 'Dates', 'Ready' and 'Waiting' summarise the rows shown.",
    "Rows with status Waiting Released are highlighted in amber and cannot be ticked."]},
  {"type": "heading", "text": "5.1.2 Button Operation", "level": 2},
  {"type": "item", "marker": "a.", "level": 2, "text": "User clicks 'Search' button."},
  {"type": "bullets", "marker": "1.", "level": 3, "items": [
    "Keep the entered criteria as the active search and clear any date opened in Detail Mode.",
    "Retrieve the Customer Order Dates with 'Customer Order Date' >= From (if filled) and <= To (if filled).",
    "If 'Status' = 'Ready to ASN' keep only Ready to ASN dates; if 'Waiting Released' keep only Waiting Released dates; if 'All' keep both.",
    "If no date is found, display message no. 4. Otherwise display the Delivery Plan Header."]},
  {"type": "item", "marker": "b.", "level": 2, "text": "If From is later than To the result is empty and message no. 4 is displayed (TBD: validation message to be confirmed)."},
  {"type": "item", "marker": "c.", "level": 2, "text": "User clicks 'Reset' button: clear From / To, set 'Status' to 'All', display all dates and return to the Delivery Plan Header."},
  {"type": "item", "marker": "d.", "level": 2, "text": "User ticks the check box of a Customer Order Date."},
  {"type": "bullets", "marker": "1.", "level": 3, "items": [
    "Select all cases of that date, across all of its supplier POs. If every case of the date is already in an ASN, or the status is Waiting Released, the check box is disabled (message no. 1 or 2 as tooltip).",
    "While one date is ticked, the check boxes of the other dates are disabled (message no. 3 as tooltip).",
    "Show the Selection Bar with the date, number of cases, pieces and PO numbers, and enable 'Clear selection' and 'Group into 1 ASN'.",
    "Unticking the same date clears the selection."]},
  {"type": "item", "marker": "e.", "level": 2, "text": "User clicks 'Clear selection': untick the date and disable 'Clear selection' and 'Group into 1 ASN'."},
  {"type": "item", "marker": "f.", "level": 2, "text": "User clicks 'Group into 1 ASN': open the ASN Draft with all cases of the selected Customer Order Date (5.3)."},
  {"type": "item", "marker": "g.", "level": 2, "text": "User clicks 'View detail' of a row: change to Detail Mode for that Customer Order Date (5.2). The button is not shown to the Supplier role."},
  {"type": "heading", "text": "5.1.3 Status Rule", "level": 2},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "A Customer Order Date is 'Ready to ASN' when every customer order of that date is paired with a supplier PO: all of its quantity is packed into full cases and every case is released in a PO. A date may be spread over several POs.",
    "Otherwise the date is 'Waiting Released': some cases wait for a PO, or some pieces cannot form a full case yet. 'Cases' then shows the pieces not released.",
    "One ASN covers exactly one Customer Order Date. A ready date is always grouped as a whole and cannot be split into another ASN.",
    "Cases already in an ASN show the ASN number in 'ASN Number'. Once all cases of the date are in an ASN, the date is ticked and locked."]},
  {"type": "table", "level": 2, "row_lines": "all", "columns": [{"title": "Status", "width": 16}, {"title": "Check box", "width": 10}, {"title": "View detail", "width": 10}],
   "rows": [["Ready to ASN", "Enabled", "Enabled"], ["Ready to ASN, already in ASN", "Ticked, disabled", "Enabled"], ["Waiting Released", "Disabled", "Enabled"]]},
  {"type": "heading", "text": "5.2 Detail in Detail"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "Displayed when the user clicks 'View detail'. The Searching Criteria and Delivery Plan Header are hidden.",
    "The summary shows 'Customer Order Date', status, supplier PO numbers and the case summary of the selected date.",
    "The grid lists the customer-order lines of the date: first the lines assigned to cases (in PO order), then the lines Waiting for a PO.",
    "One row per customer order and Part No inside each case. The same customer order may appear in several rows when split over several cases or POs.",
    "For a Waiting line 'PO No' and 'PO Date' show '-' and 'Case No' shows 'Waiting'; the row is highlighted.",
    "If there is no line, display message no. 5.",
    "User clicks 'Back to Delivery Plan': return to the Delivery Plan Header in the current search state.",
    "Detail in Detail is display only; no data is changed."]},
  {"type": "heading", "text": "5.3 ASN Draft"},
  {"type": "heading", "text": "5.3.1 Initial Display", "level": 2},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "Opened from the Delivery Plan by 'Group into 1 ASN'. The scroll position goes to the top and the screen is in ASN Draft Mode.",
    "The case list contains all cases of the selected Customer Order Date, across all of its POs, one row per case and Part No. Cases cannot be added or removed.",
    "'ASN No' shows the number generated from the Delivery Date (note: 'auto . assigned on submit').",
    "'Delivery Date' defaults to tomorrow (user local date). 'Rit' lists the Rits of that date and defaults to the first one; 'Route' shows the route of the chosen Rit.",
    "The information alert shows message no. 9. If there is no case, display message no. 8."]},
  {"type": "heading", "text": "5.3.2 Specifying Delivery Date and Rit", "level": 2},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "When 'Delivery Date' is changed the Rit list is reloaded. The previous Rit is kept if it still exists on the new date; otherwise the first Rit is used.",
    "Sunday has no Rit: 'Rit' shows 'No rit' and is disabled, 'Submit ASN' is disabled and message no. 7 is shown. Saturday has one Rit only."]},
  {"type": "heading", "text": "5.3.3 Button Operation", "level": 2},
  {"type": "item", "marker": "a.", "level": 2, "text": "User clicks 'Back to Delivery Plan' or 'Cancel': leave the draft without submitting and display the Delivery Plan Header."},
  {"type": "item", "marker": "b.", "level": 2, "text": "User clicks 'Submit ASN'."},
  {"type": "bullets", "marker": "1.", "level": 3, "items": [
    "Reject the submission if the cases are not all the cases of one Customer Order Date, if the date is not Ready to ASN, or if Delivery Date / Rit is empty (message TBD).",
    "Generate the ASN No from the Delivery Date.",
    "Lock all cases of the Customer Order Date into the ASN and insert the ASN data (refer Data Edit Mapping).",
    "Switch to ASN Submitted Mode: ASN No in the title, badge 'Submitted', message no. 6, Delivery Date and Rit read only, Cancel / Submit ASN hidden.",
    "Clear the selection of the Delivery Plan. The date is shown as locked with its ASN Number in the Delivery Plan Header."]},
  {"type": "item", "marker": "c.", "level": 2, "text": "User clicks 'Download All Case Labels': TBD - format, file name and content are not defined yet."},
  {"type": "heading", "text": "5.4 Notes"},
  {"type": "bullets", "marker": "-", "level": 2, "items": [
    "One ASN holds exactly one Customer Order Date, even when that date is spread over several POs. A case already in an ASN cannot be selected again.",
    "Customer orders, supplier POs and cases are created by the PO release process, which is out of scope of this UISS.",
    "Physical table and field names (Customer Order, Supplier PO, Case, ASN Header / Detail, Route Master) are TBD and must be confirmed by the project."]}],
 "display_messages": [
  {"group": "Delivery Plan Header (tooltip of disabled check box)"},
  {"event": "Hover on disabled check box", "cause": "All cases of the date are already in an ASN", "type": "Info", "msg_id": "MSG1", "message": "Already in an ASN", "action": "None. The date cannot be grouped again."},
  {"event": "Hover on disabled check box", "cause": "Status is Waiting Released", "type": "Info", "msg_id": "MSG2", "message": "Waiting Released: some orders of this date are not paired with a PO yet", "action": "Wait until all orders of the date are paired with a PO."},
  {"event": "Hover on disabled check box", "cause": "Another Customer Order Date is already ticked", "type": "Info", "msg_id": "MSG3", "message": "One ASN = one Customer Order Date. Clear the current selection first", "action": "Click [Clear selection], then tick another date."},
  {"group": "Search Operation"},
  {"event": "Click [Search] button", "cause": "No Customer Order Date matches the criteria", "type": "Info", "msg_id": "MSG4", "message": "No delivery plan matches this search.", "action": "Change the criteria and click Search again."},
  {"group": "View Detail Operation"},
  {"event": "Click [View detail] button", "cause": "The date has no order line", "type": "Info", "msg_id": "MSG5", "message": "No order lines for this Customer Order Date.", "action": "Click [Back to Delivery Plan]."},
  {"group": "ASN Draft - Submit Operation"},
  {"event": "Click [Submit ASN] button", "cause": "ASN submitted successfully", "type": "Info", "msg_id": "MSG6", "message": "{ASN No} submitted. {n} cases are locked. Delivery {Delivery Date}.", "action": "None. The ASN is now read only."},
  {"event": "Change [Delivery Date] / Display screen", "cause": "No Rit exists on the Delivery Date (Sunday)", "type": "Info", "msg_id": "MSG7", "message": "No rit available for {Delivery Date}. Choose another delivery date.", "action": "Choose another Delivery Date."},
  {"event": "Display screen", "cause": "The draft has no case", "type": "Info", "msg_id": "MSG8", "message": "No cases in this ASN. Go back and select at least one case.", "action": "Click [Back to Delivery Plan] and select a Customer Order Date."},
  {"group": "ASN Draft - Information (always displayed in Draft Mode)"},
  {"event": "Display screen", "cause": "Draft contains a whole Customer Order Date", "type": "Info", "msg_id": "MSG9", "message": "One ASN = one Customer Order Date. All {n} cases of order date {date} ({PO list}) are included and cannot be split into another ASN.", "action": "None."}],
 "logging_messages": [
  {"event": "Click [Submit ASN] button", "cause": "Database error on insert of ASN Header / Detail", "type": "Error", "msg_id": "LOG1", "message": "Failed to submit ASN <ASN_NO>: <DB error message>.", "exception": "Y", "action": "Show [Corresponding Screen Message] on screen (TBD)"}]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
