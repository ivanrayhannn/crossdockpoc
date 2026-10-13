"""Spec for UISS_Screen_PartDetail.xlsx (UISS-Screen, Crossdock Master Setting - Part Detail)."""
import json, sys

T, DTL = 'TB_M_PART_CANDIDATE', 'TB_M_PART_CROSSDOCK_DTL'
IMG = 'deliverables/uiss_screens/part_detail'
NAME, PROJ = 'FID Rayhan', 'Crossdock Optimization'


def it(name, source='', field='', type_='', len_='', io='', control='', just='', init='', req='', fmt='', val='', desc=''):
    return {"name": name, "source": source, "field": field, "type": type_, "len": len_, "io": io, "control": control,
            "justified": just, "initial": init, "required": req, "format": fmt, "validation": val, "description": desc}


def btn(name, desc):
    return it(name, '', '', '', '', 'I', 'Button', 'Center', '', '', '', '', desc)


B = ["Reset", "Search", "Add Detail", "Edit", "Delete", "Save", "Cancel", "Yes, delete", "No", "OK"]
LIST = ["Reset", "Search", "Add Detail", "Edit", "Delete"]


def modes(on):
    return {b: ("E" if b in on else "D") for b in B}


spec = {
 "doc_type": "screen",
 "header": {"phase": "DR", "project_name": PROJ, "block_name": "Screen",
            "function_name": "X5 Crossdock Master Setting - Part Detail", "created_date": "13-Oct-26", "created_by": NAME},
 "revisions": [{"revision": "0.1", "author": NAME, "date": "13-Oct-26", "reviewed_by": "", "description": "Initial Draft"}],
 "general": {
  "objective": [
   "To register, change and delete the Minimum MAD and Case/Day of a crossdock part (TB_M_PART_CROSSDOCK_DTL).",
   "To display the part details with search by Part Number.",
   "This sub-menu is opened by users logged in with a Procurement account, next to the Part List sub-menu."],
  "display_order": [{"section": "Result List", "fields": [{"field": "Last Update (CHANGED_DT)", "order": "Descending"}]}],
  "buttons": [
   {"name": "Reset", "function": "Clear criteria and reset the screen to its initial value."},
   {"name": "Search", "function": "To retrieve records according to the specified criteria. The criteria are applied only when [Search] is clicked (or Enter is pressed in a text box)."},
   {"name": "Add Detail", "function": "Open the 'Add Part Detail' modal (Add Mode), ready to add a new record."},
   {"name": "Edit", "function": "Change the screen into edit mode to modify the selected row ('Edit part detail' modal)."},
   {"name": "Delete", "function": "Delete the selected row after confirmation."},
   {"name": "Save", "function": "Save the record entered in the Add / Edit modal."},
   {"name": "Cancel", "function": "Close the Add / Edit modal without saving."},
   {"name": "Yes, delete", "function": "Confirm the deletion."},
   {"name": "No", "function": "Cancel the deletion."},
   {"name": "OK", "function": "Close the success popup."}],
  "screen_modes": [
   {"mode": "Initial Mode", "sections": [
     {"section": "Search Criteria", "description": "Part Number blank", "buttons": modes(LIST)},
     {"section": "Result List", "description": "All part details, newest change first", "buttons": modes(LIST)}]},
   {"mode": "Search Result Mode", "sections": [
     {"section": "Result List", "description": "Part details whose Part Number contains the text", "buttons": modes(LIST)},
     {"section": "Empty State", "description": "No matching parts; table hidden", "buttons": modes(["Reset", "Search", "Add Detail"])}]},
   {"mode": "Add Mode (modal)", "sections": [
     {"section": "Required items missing", "description": "Save disabled", "buttons": modes(["Cancel"])},
     {"section": "All required items filled", "description": "Save enabled", "buttons": modes(["Save", "Cancel"])}]},
   {"mode": "Edit Mode (modal)", "sections": [
     {"section": "Edit part detail", "description": "Part No locked; Minimum MAD and Case/Day editable", "buttons": modes(["Save", "Cancel"])}]},
   {"mode": "Delete Mode (dialog)", "sections": [
     {"section": "Delete confirmation", "description": "Confirmation of the selected row", "buttons": modes(["Yes, delete", "No"])}]},
   {"mode": "Result popup", "sections": [
     {"section": "Saved successfully", "description": "After Save or Delete", "buttons": modes(["OK"])}]}],
  "screen_mode_remarks": [
   "1) Add Detail is disabled when every part registered in Part List already has a detail record.",
   "2) A user logged in with a read-only account sees [View] instead of [Edit] and cannot use Add Detail, Delete or Save. TBD: which accounts are read-only is not defined yet."]
 },
 "screen_flow": [
  {"title": "Screen Flow for Part Detail", "flow": {"direction": "LR", "nodes": [
     {"id": "list", "label": "Part Detail list", "type": "screen"},
     {"id": "add", "label": "Add Part Detail modal", "type": "screen"},
     {"id": "edit", "label": "Edit part detail modal", "type": "screen"},
     {"id": "del", "label": "Delete confirmation", "type": "decision"},
     {"id": "ok", "label": "Saved successfully popup", "type": "message"},
     {"id": "db", "label": DTL, "type": "db"}],
   "edges": [
     {"from": "list", "to": "add", "label": "Add Detail"},
     {"from": "list", "to": "edit", "label": "Edit"},
     {"from": "list", "to": "del", "label": "Delete"},
     {"from": "add", "to": "ok", "label": "Save"},
     {"from": "edit", "to": "ok", "label": "Save"},
     {"from": "del", "to": "ok", "label": "Yes"},
     {"from": "ok", "to": "list", "label": "OK"},
     {"from": "ok", "to": "db", "style": "dashed"}]},
   "notes": ["Cancel on the modal and No on the confirmation return to the list without changes. The tab 'Part List' switches to the Part List sub-menu."]}],
 "screen_layout": [
  {"caption": "1. Initial Mode - Part Detail list", "image": f"{IMG}/c_01_list.png"},
  {"caption": "2. Search Result Mode - no matching parts", "image": f"{IMG}/c_02_no_result.png"},
  {"caption": "3. Add Mode - empty form (Save disabled)", "image": f"{IMG}/c_03_add_empty.png"},
  {"caption": "4. Add Mode - all required items filled", "image": f"{IMG}/c_04_add_filled.png"},
  {"caption": "5. Saved successfully popup", "image": f"{IMG}/c_05_saved.png"},
  {"caption": "6. Edit Mode - Part No locked", "image": f"{IMG}/c_06_edit.png"},
  {"caption": "7. Delete Mode - confirmation", "image": f"{IMG}/c_07_delete_confirm.png"}],
 "items": [
  {"group": "<Header Section>"},
  it("Sub-menu tabs", "", "", "", "", "I", "Tab", "Left", "Part Detail", "", "", "", "'Part List' / 'Part Detail'. Part List opens the Part List sub-menu."),
  {"group": "<Search Criteria Section>"},
  it("Part Number", "Key-in", "", "Varchar", "TBD", "I", "Text box", "Left", "Blank", "N", "X..TBD..X", "Contains, case-insensitive", "Placeholder 'e.g. PART-B'."),
  btn("Reset", "Clears Part Number."),
  btn("Search", "Applies the criteria to the result list. Typing or selecting a criterion alone does not change the list; Enter in a text box = [Search]."),
  {"group": "<Result List Section>"},
  it("Section title / counter", "", "", "Varchar", "", "O", "Label", "Left", "", "", "Part detail · N parts", "", "N = number of listed records."),
  btn("Add Detail", "Opens the Add Part Detail modal. Refer screen mode remark 1)."),
  it("Part Number", DTL, "PART_NO", "Varchar", "TBD", "O", "Label", "Left", "", "", "X..TBD..X", "", ""),
  it("Part Name", T, "PART_NAME", "Varchar", "TBD", "O", "Label", "Left", "", "", "X..TBD..X", "", "Name of the part in Part List."),
  it("Minimum MAD", DTL, "MIN_MAD", "Number", "TBD", "O", "Label", "Right", "", "", "ZZ,ZZ9", "", ""),
  it("Case/Day", DTL, "CASE_DAY", "Number", "TBD", "O", "Label", "Right", "", "", "ZZ,ZZ9", "", "Independent of Max Case/Day in Part List."),
  it("Last Update", DTL, "CHANGED_DT, CHANGED_BY", "Datetime", "", "O", "Label (2 lines)", "Left", "", "", "DD-Mon-YYYY HH:MI", "", "Line 1 date-time, line 2 user name."),
  btn("Edit", "Opens the Edit part detail modal of the row ([View] for a read-only account)."),
  btn("Delete", "Opens the delete confirmation of the row."),
  {"group": "<Empty State Section>"},
  it("Empty state message", "", "", "Varchar", "", "O", "Label", "Center", "", "", "", "", "Display message no. 1 or no. 2."),
  {"group": "<Add / Edit Part Detail Modal>"},
  it("Modal title", "", "", "Varchar", "", "O", "Label", "Left", "Add: 'Add Part Detail'; Edit: 'Edit part detail'", "", "", "", ""),
  it("Part No", f"{T} (Add) / {DTL} (Edit)", "PART_NO", "Varchar", "TBD", "I/O", "Combo Box with search", "Left", "Blank", "Y", "X..TBD..X", "Registered in Part List; once per part",
     f"Add: lists parts of {T} that have no record in {DTL} yet. Edit: locked."),
  it("Part Name", T, "PART_NAME", "Varchar", "TBD", "O", "Text box (disabled)", "Left", "Blank", "", "X..TBD..X", "", "Autofilled from the selected Part No."),
  it("Minimum MAD", DTL, "MIN_MAD", "Number", "TBD", "I", "Text box", "Right", "Blank", "Y", "ZZ,ZZ9", "Whole number, 0 or more", ""),
  it("Case/Day", DTL, "CASE_DAY", "Number", "TBD", "I", "Text box", "Right", "Blank", "Y", "ZZ,ZZ9", "Whole number, more than 0", ""),
  btn("Cancel", "Closes the modal without saving."),
  btn("Save", "Enabled only when Part No, Minimum MAD and Case/Day are valid (tooltip message no. 3, 4 or 5)."),
  {"group": "<Delete Confirmation Dialog>"},
  it("Confirmation text", "", "", "Varchar", "", "O", "Label", "Center", "", "", "", "", "Display message no. 7 with the Part No."),
  btn("No", "Closes the dialog without deleting."),
  btn("Yes, delete", "Deletes the record. Refer Operation Description 5.5."),
  {"group": "<Saved Successfully Popup>"},
  it("Success message", "", "", "Varchar", "", "O", "Label", "Center", "", "", "", "", "Display message no. 6 or no. 8."),
  btn("OK", "Closes the popup.")],
 "data_map": {"blocks": [
  {"source": "Key-in from screen",
   "destination": {"table": DTL, "operation": "Insert", "description": "Add Part Detail - [Save]"},
   "mappings": [
     {"source_field": "Part No", "dest_field": "PART_NO"},
     {"source_field": "Minimum MAD", "dest_field": "MIN_MAD"},
     {"source_field": "Case/Day", "dest_field": "CASE_DAY"},
     {"dest_field": "CREATED_BY", "description": "Login user ID"},
     {"dest_field": "CREATED_DT", "description": "Server system date-time"},
     {"dest_field": "CHANGED_BY", "description": "Login user ID"},
     {"dest_field": "CHANGED_DT", "description": "Server system date-time"}]},
  {"source": "Key-in from screen",
   "destination": {"table": DTL, "operation": "Update", "description": "Edit part detail - [Save]",
                   "keys": [{"field": "PART_NO", "value": "Part No of the edited row"}]},
   "mappings": [
     {"source_field": "Minimum MAD", "dest_field": "MIN_MAD"},
     {"source_field": "Case/Day", "dest_field": "CASE_DAY"},
     {"dest_field": "CHANGED_BY", "description": "Login user ID"},
     {"dest_field": "CHANGED_DT", "description": "Server system date-time"}]},
  {"source": "Selected row",
   "destination": {"table": DTL, "operation": "Delete", "description": "Delete - [Yes, delete]",
                   "keys": [{"field": "PART_NO", "value": "Part No of the selected row"}]},
   "mappings": [{"dest_field": "PART_NO", "description": "Record is deleted"}]}]},
 "operation": [
  {"type": "heading", "text": "5.1 Initial Display"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "The sub-menu is opened by users logged in with a Procurement account, from the tab 'Part Detail' next to 'Part List'.",
    f"Retrieve all records of {DTL} with the Part Name of {T}, sorted by CHANGED_DT descending.",
    "If there is no record at all, hide the table and display message no. 2."]},
  {"type": "heading", "text": "5.2 Specifying Criteria"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "'Part Number' matches by 'contains', case-insensitive.",
    "If no record matches, hide the table and display message no. 1."]},
  {"type": "heading", "text": "5.3 Add Part Detail"},
  {"type": "item", "marker": "a.", "level": 2, "text": "User clicks [Add Detail]."},
  {"type": "bullets", "marker": "1.", "level": 3, "items": [
    f"Open the 'Add Part Detail' modal. 'Part No' lists parts registered in {T} (Part List) that have no record in {DTL} yet, so a part cannot be added twice.",
    "Selecting a Part No autofills 'Part Name'.",
    "[Save] is enabled only when Part No is selected, 'Minimum MAD' is a whole number (0 or more) and 'Case/Day' is a whole number greater than 0; otherwise its tooltip shows message no. 3, 4 or 5 for the first missing item."]},
  {"type": "item", "marker": "b.", "level": 2, "text": "User clicks [Save]."},
  {"type": "bullets", "marker": "1.", "level": 3, "items": [
    "If the Part No was added by another user in the meantime, display message no. 9. Stop.",
    f"Insert the record into {DTL} (refer Data Edit Mapping).",
    "Close the modal, show the record at the top of the list and display message no. 6."]},
  {"type": "heading", "text": "5.4 Edit Part Detail"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "User clicks [Edit] on a row: open 'Edit part detail' with the saved values; 'Part No' is locked.",
    "User clicks [Save] (same checks as Add): if the record was changed by another user after it was opened, display message no. 10. Stop.",
    f"Update MIN_MAD, CASE_DAY, CHANGED_BY and CHANGED_DT in {DTL}; close the modal and display message no. 6."]},
  {"type": "heading", "text": "5.5 Delete Part Detail"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "User clicks [Delete] on a row: display the confirmation (message no. 7).",
    "User clicks [No]: close the dialog.",
    f"User clicks [Yes, delete]: if the record was changed or deleted by another user, display message no. 11. Stop. Otherwise delete the record from {DTL}, refresh the list and display message no. 8.",
    "The part itself stays in Part List; it can get a new detail record later."]},
  {"type": "heading", "text": "5.6 Table TB_M_PART_CROSSDOCK_DTL"},
  {"type": "text", "level": 2, "text": "Detail of a crossdock part, one record per part. Part numbers must be registered in TB_M_PART_CANDIDATE."},
  {"type": "table", "level": 2, "row_lines": "all", "columns": [{"title": "Column", "width": 13}, {"title": "Type", "width": 9}, {"title": "PK", "width": 3, "align": "center"}, {"title": "Null", "width": 3, "align": "center"}, {"title": "Description", "width": 18}], "rows": [
    ["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part number; FK to TB_M_PART_CANDIDATE"],
    ["MIN_MAD", "INT", "", "N", "Minimum MAD of the part (0 or more)"],
    ["CASE_DAY", "INT", "", "N", "Case/Day of the part (> 0); independent of MAX_CASE_DAY"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]},
  {"type": "text", "level": 2, "text": "TBD: which functions read MIN_MAD and CASE_DAY (e.g. the MAD calculation function) and whether a change must be logged in a history table."}],
 "display_messages": [
  {"group": "Search Operation"},
  {"event": "Change search criteria", "cause": "No record matches the criteria", "type": "Info", "msg_id": "MSG1",
   "message": "No matching parts - Change the Part Number or press Reset.", "action": "Change the criteria or click [Reset]"},
  {"event": "Open Part Detail", "cause": "No record registered yet", "type": "Info", "msg_id": "MSG2",
   "message": "No part detail registered yet - Click Add Detail to register Minimum MAD and Case/Day of a part.", "action": "Click [Add Detail]"},
  {"group": "Add / Edit Operation"},
  {"event": "Hover disabled [Save]", "cause": "Part No not selected", "type": "Info", "msg_id": "MSG3", "message": "Part No is required", "action": "Select a Part No"},
  {"event": "Hover disabled [Save]", "cause": "Minimum MAD blank or not a whole number", "type": "Info", "msg_id": "MSG4", "message": "Enter Minimum MAD (whole number, 0 or more)", "action": "Fill Minimum MAD"},
  {"event": "Hover disabled [Save]", "cause": "Case/Day blank or not greater than 0", "type": "Info", "msg_id": "MSG5", "message": "Enter Case/Day (whole number, more than 0)", "action": "Fill Case/Day"},
  {"event": "Click [Save] button", "cause": "Record saved", "type": "Info", "msg_id": "MSG6", "message": "Saved successfully - {Part No} has been added/updated.", "action": "Click [OK]"},
  {"group": "Delete Operation"},
  {"event": "Click [Delete] button", "cause": "Confirmation", "type": "Confirm", "msg_id": "MSTD0001ACFM", "message": "Are you sure you want to delete the record ? {Part No}", "action": "Click [Yes, delete] or [No]"},
  {"event": "Click [Yes, delete] button", "cause": "Record deleted", "type": "Info", "msg_id": "MSG7", "message": "Saved successfully - {Part No} has been deleted.", "action": "Click [OK]"},
  {"group": "Concurrency"},
  {"event": "Click [Save] button (Add)", "cause": "Part No added by another user", "type": "Error", "msg_id": "MSTD0039AERR", "message": "Duplication found for {Part No}", "action": "Close the modal and search the part"},
  {"event": "Click [Save] button (Edit)", "cause": "Record changed by another user", "type": "Error", "msg_id": "MSG8", "message": "Error in Update because of concurrency check.", "action": "Close the modal, refresh and edit again"},
  {"event": "Click [Yes, delete] button", "cause": "Record changed or deleted by another user", "type": "Error", "msg_id": "MSTD0115AERR", "message": "Error in Delete because of concurrency check.", "action": "Refresh the list and try again"}],
 "logging_messages": [
  {"event": "Click [Save] button", "cause": f"Database error on insert/update of {DTL}", "type": "Error", "msg_id": "LOG1",
   "message": "Failed to save part detail <PART_NO>: <DB error message>.", "exception": "Y", "action": "Show [Corresponding Screen Message] on screen (TBD)"},
  {"event": "Click [Yes, delete] button", "cause": f"Database error on delete of {DTL}", "type": "Error", "msg_id": "LOG2",
   "message": "Failed to delete part detail <PART_NO>: <DB error message>.", "exception": "Y", "action": "Show [Corresponding Screen Message] on screen (TBD)"}]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
