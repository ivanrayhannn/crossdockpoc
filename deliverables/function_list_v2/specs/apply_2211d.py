"""22-Nov: XD01 5.25 Table changes per Save: for every save on the screen, which table gets a row added, edited or deleted.
Taken from the save steps (5.4, 5.5, 5.15, 5.16), 5.10 and 5.24 and the Data Map; no new rule."""
import json

with open('XD01_spec.json') as f:
    s = json.load(f)
op = s['operation']

if not any(o.get('text', '').startswith('5.25 ') for o in op):
    rows = [
        ['Add Part [Save]', 'TB_M_PART_CANDIDATE', 'Add', '1 row for the new part, PART_STATUS = Candidate, CREATED / CHANGED = login user and server time.'],
        ['', 'TB_H_PART_CANDIDATE', 'Add', 'EVENT_TYPE ADD, SOURCE SCREEN, OLD_VALUE NULL (history of the new part).'],
        ['', 'TB_H_PART_CANDIDATE_STG_SYNC', '-', 'No row: a Candidate part is not sent.'],
        ['Edit part data [Save]', 'TB_M_PART_CANDIDATE', 'Edit', 'The part row: Status, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, Effective Start Date (Candidate only), CHANGED_BY / CHANGED_DT.'],
        ['', 'TB_H_PART_CANDIDATE', 'Add', '1 row per changed field, EVENT_TYPE EDIT, SOURCE SCREEN, old and new value.'],
        ['', 'TB_H_PART_CANDIDATE_STG_SYNC', 'Add', 'Active part: 1 KANBAN EDIT row per changed Pcs/Case or Max Case/Day. Candidate -> Active: KANBAN ADD rows. Active -> Inactive: 1 EXPORT DELETE row (NEW_VALUE 0) per destination. Min MAD, Effective Start Date and Candidate <-> Inactive: no row.'],
        ['Edit mapping [Save]', 'TB_M_PART_CANDIDATE_DEST', 'Add', '1 row per new destination + order type of the part and period.'],
        ['', 'TB_M_PART_CANDIDATE_DEST', 'Edit', 'CASE_DAY of a kept destination whose Case/Day changed, CHANGED_BY / CHANGED_DT.'],
        ['', 'TB_M_PART_CANDIDATE_DEST', 'Delete', 'The row of a removed destination.'],
        ['', 'TB_H_PART_CANDIDATE', 'Add', '1 row per added, changed or removed destination, EVENT_TYPE MAPPING, FIELD_NAME CASE_DAY.'],
        ['', 'TB_H_PART_CANDIDATE_STG_SYNC', 'Add', '1 EXPORT row per added (ADD), changed (EDIT) or removed (DELETE, NEW_VALUE 0) destination.'],
        ['[Sync]', 'TB_H_PART_CANDIDATE_STG_SYNC', 'Edit', 'The rows taken by the run: sync status, SEND_SEQ, sync date and run ID of AP POLE / GTOPAS (refer 5.24). No row is added.'],
        ['', 'System Master', 'Edit', 'LAST_SYNC_DATE_APPOLE = time of the click.'],
        ['[Re-send last Sync]', 'TB_H_PART_CANDIDATE_STG_SYNC', '-', 'The rows of the last run ID are sent again (refer 5.16 c). No row is added.'],
        ['Upload Excel [Validate file]', 'Same tables as the Save above', 'Add / Edit', 'Written by the upload batch, SOURCE UPLOAD: XD02 for Kanban Crossdock Master, XD03 for Export Crossdock Master (refer UISS-Batch).'],
    ]
    op += [
        {'type': 'heading', 'text': '5.25 Table changes per Save'},
        {'type': 'text', 'level': 2, 'text': 'Every save on the screen writes in one transaction. Add = insert a row, Edit = update a row, Delete = delete a row. A save without a changed value adds no history and no staging row. Columns: refer Data Map.'},
        {'type': 'table', 'level': 2, 'row_lines': 'all',
         'columns': [{'title': 'Save (screen)', 'width': 11}, {'title': 'Table', 'width': 15}, {'title': 'Add / Edit / Delete', 'width': 6, 'align': 'center'}, {'title': 'What is written', 'width': 27}],
         'rows': rows},
    ]

REF = {
    "Close the modal, reset the Part Number / Part Name / Status filters, sort Newer to Older and display message no. 9. The new part is shown at the top.":
        "Close the modal, reset the Part Number / Part Name / Status filters, sort Newer to Older and display message no. 9. The new part is shown at the top. Table changes: refer 5.25.",
    "Close the modal, move the part to the top of the list and display message no. 9.":
        "Close the modal, move the part to the top of the list and display message no. 9. Table changes: refer 5.25.",
    "Leave edit mode and show the saved mapping.": "Leave edit mode and show the saved mapping. Table changes: refer 5.25.",
    "5.1 - 5.10: Kanban Crossdock Master tab. 5.11 - 5.20: Export Crossdock Master tab.":
        "5.1 - 5.10: Kanban Crossdock Master tab. 5.11 - 5.20: Export Crossdock Master tab. 5.25: table changes of every save.",
}
for o in op:
    if 'items' in o:
        o['items'] = [REF.get(i, i) for i in o['items']]
    if 'text' in o:
        o['text'] = REF.get(o['text'], o['text'])

if not any(r['revision'] == '0.10' for r in s['revisions']):
    s['revisions'].append({'revision': '0.10', 'author': 'FID Rayhan', 'date': '22-Nov-26', 'reviewed_by': '',
                           'description': 'New 5.25 Table changes per Save: Add / Edit / Delete per table for every save on the screen.'})

with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
