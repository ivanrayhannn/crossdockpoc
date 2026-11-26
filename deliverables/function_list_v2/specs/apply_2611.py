"""26-Nov: staging without run ID; one unsent row per key (XD01, XD02, XD03, XD05, XD06, XD07).
- SYNC_RUN_ID removed: the run is SYNC_DT, one value per [Sync] click (rollover: time of the rollover). NSP takes the time once, passes
  it to SP_STG_SYNC and to the RPA parent flow; the robots read WHERE SYNC_STATUS = '1' AND SYNC_DT = <SYNC_DT of the run>;
  [Re-send last Sync] = MAX(SYNC_DT).
- A key has at most one row with SYNC_STATUS 0: a new change of the key updates it; a change back to the value already sent for the
  period deletes it; a sent row (1) is never changed. SYNC_STATUS is 0 / 1 only (2 Superseded removed).
- Header 5 is deleted when no Export row of the part + period waits any more.
SQL: prepare_code/sql/crossdock_staging_sync.sql (erd/proposal_staging_sync/build_staging_sql.py). Runs after apply_2411b."""
import importlib.util
import json
import os
import re

D = '26-Nov-26'
HERE = os.path.dirname(os.path.abspath(__file__))
K, E, G = 'TB_H_STG_APPOLE_KANBAN', 'TB_H_STG_APPOLE_EXPORT', 'TB_H_STG_GTOPAS'
spec_ = importlib.util.spec_from_file_location('tp2', os.path.join(HERE, '..', 'erd', 'proposal_staging_sync', 'build_table_proposal_v2.py'))
tp = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(tp)


def conv(rows):
    out = []
    for name, typ, pk, null, default, file_col, d, _ in rows:
        text = d + (f'. File / screen column: {file_col}' if file_col else '') + (f'. Default {default}' if default and default != 'identity' else '')
        out.append([name, typ, pk, null, text])
    return out


DESC = {
    K: 'AP POLE Kanban rows in the format of the upload file LLM9Q910, one row per Kanban change of a part + period (one unsent row at a '
       'time: a new change updates it), plus the header row (OPERATION_TYPE 5) when only the destinations changed. Written by SP_STG_WRITE '
       '(XD01, XD02, XD05); SYNC_STATUS and SYNC_DT set by SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_KANBAN and V_APPOLE_UPLOAD_EXPORT.',
    E: 'AP POLE Export rows in the format of the upload file LLM9Q880, one row per added, changed or removed destination + order type of a '
       'part + period (one unsent row per key: a new change updates it). Written by SP_STG_WRITE (XD01, XD03, XD05); SYNC_STATUS and SYNC_DT '
       'set by SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_EXPORT.',
    G: 'GTOPAS WVJA5204 rows: a part + destination to add or delete, written by SP_STG_WRITE only when the destination appears or disappears '
       'for the part (any order type) and GTOPAS does not have that state yet (one unsent row per key). Sent by [Sync] (Current period) or the '
       'Period Rollover (new Current period). Read by XD06.',
}
COLS = {K: conv(tp.KAN), E: conv(tp.EXP), G: conv(tp.GTO)}

ONE_ROW = ('One unsent row per key: a key has at most one row with SYNC_STATUS 0. A new change of the key updates that row (value, ACTION, '
           'OPERATION_TYPE, CHANGED_BY / CHANGED_DT); a change back to the value already sent for the period deletes it (nothing to send); a '
           'sent row (SYNC_STATUS 1) is never changed, the next change inserts a new row. Keys: Kanban PERIOD + PART_NO; Export PERIOD + '
           'NSP_PART_NO + DEST_CODE + ORDER_TYPE; GTOPAS PERIOD + P_NO + DESTINATION_CODE. TB_H_PART_CANDIDATE keeps every change.')
SYNC_RULE = ('[Sync] takes the time of the click once (SYNC_DT, to the second) and calls SP_STG_SYNC with it. It calculates nothing: it locks '
             'the staging tables for a moment (a save at the same time waits), sets SYNC_STATUS 0 -> 1 and SYNC_DT on the AP POLE rows of the '
             'Current and Next period and on the GTOPAS rows of the Current period, and sets the System Master parameter LAST_SYNC_DATE_APPOLE. '
             'Then it starts the RPA parent flow with the same SYNC_DT: the robots read the rows of that click.')

TEXT = [
    # rules and sentences that changed meaning
    (re.compile(r'^Superseded: a new row of a key marks the older unsent row.*$'), ONE_ROW),
    (re.compile(r'^\[Sync\] calls SP_STG_SYNC with a new run ID.*$'), SYNC_RULE),
    ('The older unsent row of the same key: SYNC_STATUS 2 (Superseded).',
     'The unsent row of the same key (SYNC_STATUS 0) takes the new value; it is deleted when the value is back to the value already sent.'),
    ('SP_STG_SYNC: SYNC_STATUS 0 -> 1, SYNC_DT, SYNC_RUN_ID (AP POLE Current + Next, GTOPAS Current). No row is added.',
     'SP_STG_SYNC: SYNC_STATUS 0 -> 1, SYNC_DT = time of the click (AP POLE Current + Next, GTOPAS Current). No row is added.'),
    ('The rows of the last run ID are sent again (refer 5.16 c). No row is added.',
     'The rows of the last run (latest SYNC_DT) are sent again (refer 5.16 c). No row is added.'),
    ('Last sent {date-time} (run {run ID}).', 'Last sent {date-time}.'),
    ('get the run ID, then the RPA parent flow starts.', 'get SYNC_DT = time of the click, then the RPA parent flow starts with it.'),
    ('get SYNC_STATUS 1, SYNC_DT and the run ID.', 'get SYNC_STATUS 1 and SYNC_DT = time of the click (one value for the click).'),
    ('Start the RPA parent flow with the run ID', 'Start the RPA parent flow with SYNC_DT'),
    ('the rows of the last run ID are sent again in the same order', 'the rows of the last run (latest SYNC_DT) are sent again in the same order'),
    ('get SYNC_STATUS 1, SYNC_DT and a run ID;', 'get SYNC_STATUS 1 and SYNC_DT = time of the rollover;'),
    ('Update: SYNC_STATUS 1, SYNC_DT = rollover time, SYNC_RUN_ID, CHANGED_BY / CHANGED_DT;',
     'Update (SP_STG_ROLLOVER): SYNC_STATUS 1, SYNC_DT = rollover time, CHANGED_BY / CHANGED_DT;'),
    ('started by NSP with RUN_ID and RUN_TYPE (SYNC, RESEND, ROLLOVER).', 'started by NSP with SYNC_DT (the run) and RUN_TYPE (SYNC, RESEND, ROLLOVER).'),
    ('SELECT COUNT(*) FROM TB_H_STG_GTOPAS WHERE SYNC_RUN_ID = run ID (> 0: scenario 1).',
     "SELECT COUNT(*) FROM TB_H_STG_GTOPAS WHERE SYNC_STATUS = '1' AND SYNC_DT = <SYNC_DT of the run> (> 0: scenario 1)."),
    ('rows with SYNC_RUN_ID = run ID', "rows with SYNC_STATUS '1' and SYNC_DT = SYNC_DT of the run"),
    ('Rows with SYNC_RUN_ID = run ID:', "Rows with SYNC_STATUS '1' and SYNC_DT = SYNC_DT of the run:"),
    ('<template>_<RUN_ID>_<order>_<name>.xls', '<template>_<SYNC_DT YYYYMMDDHHMMSS>_<order>_<name>.xls'),
    ('<template>_<run ID>_<order>_<name>.xls', '<template>_<SYNC_DT YYYYMMDDHHMMSS>_<order>_<name>.xls'),
    ('Run <RUN_ID>', 'Run <SYNC_DT>'),
    ('run <RUN_ID>', 'run <SYNC_DT>'),
    ('RUN_ID, RUN_TYPE,', 'SYNC_DT, RUN_TYPE,'),
    ('So every part of a run has one Kanban row that sets its upload order.',
     'So every part of a run has one Kanban row that sets its upload order. The header is deleted when no Export row of the part + period waits any more.'),
    # remaining wording
    ('set the rows to SYNC_STATUS 1 with this run ID', 'set the rows to SYNC_STATUS 1 with this SYNC_DT'),
    ('the same run ID', 'the same SYNC_DT'),
    ('with the run ID and RUN_TYPE', 'with SYNC_DT and RUN_TYPE'),
    ('with the run ID', 'with SYNC_DT'),
    ('for the run ID', 'for the SYNC_DT of the run'),
    ('rows of the run ID', 'rows of the run (SYNC_DT)'),
    ('Start (run ID, RUN_TYPE from the parent flow)', 'Start (SYNC_DT, RUN_TYPE from the parent flow)'),
    ('Start (run ID from the parent flow)', 'Start (SYNC_DT from the parent flow)'),
    ('a run ID', 'SYNC_DT'),
    ('the run ID', 'SYNC_DT'),
    ('SYNC_RUN_ID', 'SYNC_DT'),
    ('2 Superseded', 'deleted'),
]


def fix(o):
    if isinstance(o, dict):
        return {k: fix(v) for k, v in o.items()}
    if isinstance(o, list):
        return [fix(v) for v in o]
    if isinstance(o, str):
        for a, b in TEXT:
            o = a.sub(b, o) if hasattr(a, 'sub') else o.replace(a, b)
        o = o.replace('SYNC_DT, SYNC_DT', 'SYNC_DT')
        return o
    return o


UPD = {K: [('ACTION', "'EDIT' (ADD when the key was not sent in the period)"), ('PART_STATUS', 'Status of the part'),
           ('SHIPPING_BOX_QTY', 'New Pcs/Case'), ('MAX_SHIPPING_BOX_QTY', 'New Max Case/Day'), ('MAX_ALLOWANCE_QTY', 'Pcs/Case x Max Case/Day'),
           ('OPERATION_TYPE', 'Again against the last Max sent (a header 5 becomes 1 to 4)')],
       E: [('ACTION', "'ADD' / 'EDIT' / 'DELETE' against the last value sent"), ('MAX_SHIPPING_BOX_RCS', 'New Case/Day; 0 for DELETE')],
       G: [('ACTION', "'ADD' / 'DELETE' (what the master needs)")]}


def blocks(s):
    out = []
    for b in s['data_map']['blocks']:
        dest = b.get('destination') or {}
        t, op, d = dest.get('table'), dest.get('operation'), dest.get('description', '')
        if t in (K, E, G) and 'Superseded' in d:
            src = b['source']
            out.append({'source': src, 'destination': {'table': t, 'operation': 'Update',
                        'description': 'SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row'},
                        'mappings': [{'source_field': '-', 'dest_field': f, 'description': x} for f, x in UPD[t]] +
                                    [{'source_field': '-', 'dest_field': 'SOURCE', 'description': 'Caller of the last change'},
                                     {'source_field': '-', 'dest_field': 'UPLOAD_ID', 'description': 'Upload ID when SOURCE = UPLOAD'},
                                     {'source_field': '-', 'dest_field': 'CHANGED_BY', 'description': 'Login user (XD05: batch user ID)'},
                                     {'source_field': '-', 'dest_field': 'CHANGED_DT', 'description': 'Server date-time'}]})
            out.append({'source': src, 'destination': {'table': t, 'operation': 'Delete',
                        'description': 'SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period'
                                       + (' (Kanban: also the header 5 when no Export row of the part + period waits)' if t == K else '')},
                        'mappings': [{'source_field': '-', 'dest_field': 'STG_ID', 'description': 'Unsent row (SYNC_STATUS 0) of the key'}]})
            continue
        if t in (K, E, G):
            b['mappings'] = [m for m in b['mappings'] if m.get('dest_field') not in ('SYNC_RUN_ID',)]
            for m in b['mappings']:
                if m.get('dest_field') == 'SYNC_STATUS':
                    m['description'] = "'0'" if op == 'Insert' else "'1'"
                if m.get('dest_field') == 'SYNC_DT' and op == 'Update':
                    m['description'] = 'Time of the [Sync] click / of the rollover: one value for every row of the run'
            if op == 'Insert' and 'SP_STG_WRITE' in d:
                dest['description'] = d + ' (when the key has no unsent row yet)'
        src = b.get('source')
        if isinstance(src, dict):
            for k in src.get('keys', []):
                if k.get('field') in ('SYNC_RUN_ID', 'RUN_ID'):
                    k['field'], k['value'] = 'SYNC_DT', 'SYNC_DT of the run (SYNC_STATUS 1)'
        for m in b['mappings']:
            if m.get('dest_field') == 'RUN_ID' and m.get('description') == 'Run ID':
                m['dest_field'], m['description'] = 'SYNC_DT', 'SYNC_DT of the run'
        out.append(b)
    s['data_map']['blocks'] = out


REV = {'XD01': '0.16', 'XD02': '0.7', 'XD03': '0.7', 'XD05': '0.9', 'XD06': '1.2', 'XD07': '1.2'}
NOTE = ('Staging: no SYNC_RUN_ID, the run is SYNC_DT (one value per [Sync] click / rollover); one unsent row per key (a new change updates '
        'it, back to the sent value deletes it); SYNC_STATUS 0 / 1. SQL: prepare_code/sql/crossdock_staging_sync.sql.')
for fid, no in REV.items():
    p = os.path.join(HERE, f'{fid}_spec.json')
    s = json.load(open(p))
    if any(r['date'] == D and r['description'].startswith('Staging: no SYNC_RUN_ID') for r in s['revisions']):
        continue
    for t in s['tables']:
        if t['name'] in COLS:
            t['columns'] = json.loads(json.dumps(COLS[t['name']]))
            t['description'] = DESC[t['name']]
    blocks(s)
    s = {k: (fix(v) if k not in ('revisions', 'tables', 'header') else v) for k, v in s.items()}
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': NOTE})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched', fid)
