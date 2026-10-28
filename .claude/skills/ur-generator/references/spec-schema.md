# Spec schema for `scripts/build_uiss.py`

One JSON file = one workbook = one Screen ID or Report ID. All keys are optional except
`doc_type`; anything missing is rendered as an empty template area or `TBD`. Write every value in
English. Use `"TBD"` for unknown facts (never leave a guess unmarked).

Contents: 1 Common · 2 Screen keys · 3 Report keys · 4 Batch keys · 5 Flow blocks ·
6 Flowchart spec · 7 Minimal examples

## 1. Common keys

```json
{
  "doc_type": "screen",                      // "screen" | "report" | "batch"
  "header": {
    "phase": "DR",
    "project_name": "ELIPS Enhancement",
    "block_name": "Screen",                  // default "Screen" / "Report" / "Batch"
    "function_name": "WELP0210 Supplier Delivery Schedule Master",
    "created_date": "03-Oct-26",             // dd-mmm-yy, default today
    "created_by": "Ivan",
    "updated_date": "", "updated_by": ""
  },
  "revisions": [                             // default: one row 0.1 "Initial draft"
    {"revision": "0.1", "author": "Ivan", "date": "03-Oct-26", "reviewed_by": "",
     "description": "Initial draft based on meeting 01-Oct-26"}
  ],
  "omit_sheets": []                          // e.g. ["Data Map"] to drop a sheet entirely (rare)
}
```

## 2. Screen keys

```json
"general": {
  "objective": ["To ...", "To ..."],
  "display_order": [{"section": "Detail", "fields": [{"field": "Supplier Code", "order": "Ascending"}]}],
  "buttons": [{"name": "Search", "function": "To retrieve records according to the specified criteria."}],
  "screen_modes": [
    {"mode": "Initial Mode", "sections": [
      {"section": "Search Criteria", "description": "All criteria blank",
       "buttons": {"Search": "E", "Add": "E", "Edit": "D"}}      // E/D per button name; missing → TBD
    ]}
  ],
  "screen_mode_remarks": ["1) ..."]          // optional
},
"screen_flow": [                             // one entry per diagram (each on its own page)
  {"title": "Screen Flow for Search", "flow": { /* §6 */ }, "notes": ["optional text under it"]},
  {"title": "Existing flow", "image": "/mnt/user-data/uploads/flow.png"}
],
"screen_layout": [                           // user-supplied images only; one page each
  {"caption": "On Load Screen", "image": "/mnt/user-data/uploads/screen1.png", "notes": []},
  {"caption": "Add Mode"}                    // no image → "[SCREEN IMAGE HERE]" placeholder
],
"items": [
  {"group": "<Search Criteria Section>"},
  {"no": 1,                                   // optional; auto-numbered when omitted
   "name": "Supplier Code", "source": "TB_M_SUPPLIER", "field": "SUPPLIER_CD",
   "type": "Varchar", "len": 6, "io": "I", "control": "Text box", "justified": "Left",
   "initial": "Blank", "required": "N", "format": "X..6..X",
   "validation": "Wildcard (*) allowed", "description": "..."}
],
"data_map": {
  "note": "Not applicable - this screen does not insert/update data.",   // used when blocks empty
  "blocks": [
    {"source": "Key-in from screen",
     "destination": {"table": "TB_M_X", "operation": "Insert", "description": "Add mode - [Save]",
                     "keys": [{"field": "X_CD", "value": "Key-in X Code"}]},
     "mappings": [
       {"source_field": "Supplier Code", "dest_field": "SUPPLIER_CD"},
       {"dest_field": "CREATED_DT", "description": "Server system date"}]},
    {"source": {"table": "TB_M_X", "keys": [{"field": "X_CD", "value": "Key-in X Code"}]},
     "destination": {"table": "TB_H_X", "operation": "Insert", "description": "Keep history"},
     "mappings": [{"source_field": "X_CD", "dest_field": "X_CD"}]}
  ]
},
// Data Map header cells are single-row: keep destination.description short (~30 chars).
"operation": [ /* §5 blocks */ ],
"operation_layout": "two",                   // "two" (default, like the guide) | "full"
"display_messages": [
  {"group": "Search Operation"},
  {"event": "Click [Search] button", "cause": "Mandatory field are not fill all", "type": "Error",
   "msg_id": "MSTD0075AERR", "message": "Mandatory Field Not Entered",
   "action": "Fill all mandatory field and click search"}
],
"logging_messages": [
  {"event": "Click [Upload] button", "cause": "...", "type": "Error", "msg_id": "TBD",
   "message": "...", "exception": "Y", "action": "Display Message"}
]
```

## 3. Report keys

```json
"general": {
  "objective": ["To describe the layout and data source of ..."],
  "printing_order": [{"section": "Body", "fields": [{"field": "Plant", "order": "Ascending"}]}],
  "calling_screens": [{"screen_id": "WELP0300", "description": "Delivery Achievement Inquiry"}],
  "report_file": {"file_name": "Xxx_YYYYMMDDHHMISS.xlsx", "path": "TBD", "keeping_period": "Report files will be kept for one month."},
  "generation_keys": [{"section": "Daily Delivery Achievement Report",
                       "fields": [{"field": "Plant Code", "description": "Selected plant on calling screen"}]}]
},
"layout": {
  "attributes": [{"report_id": "RELP0300", "report_name": "...", "paper_size": "A4",
                  "form_type": "Blank", "paper_layout": "Landscape", "printer_type": "Laser",
                  "template_type": "Fixed", "template_by_user": "N", "type_application": "On-demand",
                  "type_business": "Summary", "need_screen": "Y", "file_type": "Excel",
                  "preview": "N", "direct_print": "N", "copies": "-", "signature": "Hand Writing"}],
  "figures": [{"caption": "Figure 1  Daily Delivery Achievement Report Template",
               "image": "/mnt/user-data/uploads/report_mockup.png",
               "notes": ["Header: displayed on every page", "Footer: displayed on first page"]}]
},
"items": [
  {"group": "<HEADER>"},
  {"name": "Report Title", "type": "Char", "len": 40, "justified": "Center", "format": "X..40..X",
   "source": "", "field": "", "condition": "", "remarks": "Fixed text \"...\""}
],
"operation": [ /* §5 blocks */ ],
"logging_messages": [
  {"event": "Connect to database server", "cause": "Cannot connect to database", "type": "Critical",
   "msg_id": "TBD", "message": "Database cannot be connected.", "exception": "Y",
   "action": {"system": "Stop report generation", "user": "Contact system administrator"}}
]
```

## 4. Batch keys

```json
"general": {
  "objective": ["To load ... into the staging table.", "In case of error, data is inserted into the parking table."],
  "operation_flow": {"flow": { /* §6, TB, <= 8 nodes */ },          // or {"image": path}
                     "note": "Operation flow image is from UR's Batch Function Outline document"},
  "inputs":  [{"name": "SDS_YYYYMMDDHHMISS.csv", "type": "CSV", "description": "one file per run"}],
  "outputs": [{"name": "TB_M_X", "type": "DB", "description": "if successful"},
              {"name": "TB_P_X", "type": "DB", "description": "if error occurs"}],
  "extra_tables": [                         // rendered as c., d. ... (No column added automatically)
    {"title": "Grouping Keys", "columns": [{"title": "Field Name", "width": 20}], "rows": ["DOC_NO", "DOC_TYPE"]},
    {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 30}],
     "rows": [["Trigger", "Job scheduler, daily 01:00"]]}],
  "constraints": ["..."]                    // optional list under the tables
},
"func_flow": {
  "flow": {"direction": "TB", "nodes": [
     {"id": "p2", "label": "Get interface config by File ID", "type": "process", "step": 2},
     {"id": "cfg", "label": "TB_M_INTERFACE_CONFIG", "type": "db", "lane": "input"},
     {"id": "base", "label": "TB_M_X", "type": "db", "lane": "output"}],
   "edges": [{"from": "cfg", "to": "p2"}, {"from": "p6", "to": "base"}]},   // or "image": path
  "steps": [                                // Description column, numbered automatically
    "Retrieve the File ID parameter.",
    {"text": "Retrieve status from TB_M_INTERFACE_CONFIG by File ID.",
     "children": ["If status is not Active, log message no. 2. Stop; otherwise proceed."]}]
},
"data_map": {"blocks": [
  {"source": {"table": "TB_S_X", "keys": [{"field": "FILE_ID", "value": "Parameter File ID"}]},
   "destination": {"table": "TB_M_X", "operation": "Insert", "description": "Valid group"},
   "mappings": [{"source_field": "SUPPLIER_CD", "dest_field": "SUPPLIER_CD"},
                {"dest_field": "CREATED_BY", "description": "'BELP0110' (batch ID)"}]},
  {"source": {"table": "TB_S_X"}, "destination": {"table": "TB_P_X", "operation": "Insert", "description": "Invalid group"},
   "source_fields": ["FILE_ID", "SUPPLIER_CD"],            // independent source list, no arrows
   "mappings": [{"dest_field": "ERROR_REASON", "description": "Validation message"}]}]},
"func_desc": [ /* §5 blocks */ ],
"func_desc_layout": "two",
"logging_messages": [                       // no Exception column in the batch template
  {"event": "Record validation", "cause": "Supplier not in master", "type": "Error", "msg_id": "TBD",
   "message": "Supplier Code <SUPPLIER_CD> not in Supplier Master on <Record PK>.",
   "action": {"system": "Move group to parking table", "user": "Correct master then reprocess"}}],
"appendix": [ /* §5 blocks, optional; sheet "Appendix" is added only when present */ ],
"appendix_layout": "full",
"tables": [                                 // every table the batch writes (uiss-batch-guide §12)
  {"name": "TB_R_CD_PART", "kind": "transaction", "proposed": true,      // kind: transaction|temp|history|log|staging|parking
   "description": "crossdock part setting (target of a successful upload)",
   "columns": [["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part Number; length follows TB_M_PART_MASTER"],
               ["PCS_CASE", "INT", "", "N", "Pieces per case (> 0)"],
               ["CREATED_BY", "VARCHAR(20)", "", "N", "User who created the record"]]}  // [name, type, PK, Null, description]
]
```
A plain string `source` in a batch block is treated as a DB/File name.
`tables` renders an Appendix "Table definitions" after any `appendix` blocks, and the build output lists
`data_map_missing_columns` when an Insert block (any table) or an Update/Delete block (transaction table)
does not mention every column of its destination.
Lane nodes with exactly one edge are drawn on the same row as their process (inputs left, outputs
right). A store used by several steps (e.g. a log table) can be repeated as separate nodes.

## 5. Flow blocks (`operation`, also usable for free text elsewhere)

Rendered top-to-bottom in the left column, then the right column, then a new page.
`level` = indent in grid columns (0 = section heading position).

| type | keys | use |
|---|---|---|
| `heading` | `text`, `level`=0, `num` (optional short number like "1.") | `5.1 Download Process` (bold, blank line before) |
| `text` | `text`, `level`=2, `bold`, `italic` | paragraph; bold for sub-headings like `5.1.1 Initial Display` |
| `item` | `marker`, `text`, `level`=2, `bold` | one lettered/numbered step, continuation lines aligned |
| `bullets` | `items`, `marker` ("-", "1.", "a."), `level` | auto-numbered list; an item may be `{"text":..., "children":[...], "child_marker":"-"}` |
| `table` | `columns` [{`title`,`width` (grid cols),`align`}], `rows`, `level`, `row_lines` ("all"/"group"), `group_cols` | small data examples, condition tables |
| `flow` | `spec` (§5), `caption`, `max_rows` | process flowchart rendered with graphviz |
| `image` | `path`, `caption`, `max_rows` | user-supplied picture |
| `spacer` | `rows` | blank rows |
| `column_break` / `page_break` | – | force next column / page |

Suggested levels: heading 0 → sub-heading text 1 (bold) → items `a.` level 2 → steps `1.` level 3
→ bullets `-` level 4. One column is ~48 grid columns (~85 characters).

## 6. Flowchart spec (`flow`)

```json
{"direction": "TB",                      // TB (top-bottom) or LR (left-right)
 "nodes": [
   {"id": "s", "label": "START", "type": "start"},
   {"id": "a", "label": "On Click of Search button", "type": "event"},
   {"id": "p", "label": "Retrieve data by criteria", "type": "process"},
   {"id": "d", "label": "Data found?", "type": "decision"},
   {"id": "t", "label": "TB_M_SUPPLIER", "type": "db"},
   {"id": "w", "label": "Search screen", "type": "screen", "screen_id": "WELP0210"},
   {"id": "e", "label": "END", "type": "end"}],
 "edges": [{"from": "s", "to": "a"}, {"from": "d", "to": "e", "label": "No"},
           {"from": "p", "to": "t", "style": "dashed"}],
 "same_rank": [["p", "t"]]}              // optional: keep nodes side by side
```
Node types: start, end, event, process, subprocess, decision, screen, db, file/document, io,
message, note. They are drawn as editable Excel shapes. Raw Graphviz is also accepted:
`{"dot": "digraph G { ... }"}` (rendered as a picture, not editable).
Keep labels short (≤ 6 words) and diagrams ≤ 10–12 nodes; the image is scaled to one page, so a big
diagram becomes unreadably small. Use TB for process flows; LR only for short screen-transition maps.

## 7. Minimal examples

Inquiry-only screen (no data writes):
```json
{"doc_type": "screen",
 "header": {"project_name": "ELIPS", "function_name": "WELP0300 Delivery Achievement Inquiry", "created_by": "Ivan"},
 "general": {"objective": ["To display delivery achievement per supplier and cycle."],
             "buttons": [{"name": "Search", "function": "To retrieve records according to the specified criteria."}]},
 "data_map": {"blocks": [], "note": "Not applicable - this screen does not insert/update data."}}
```
