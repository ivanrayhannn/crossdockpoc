"""06-Nov: XD04 review comments (Function Summary).
- Delta read: only source rows with INTERFACE_UPDATE_DT > watermark (last value taken by the previous successful run), upsert per key.
- Failed run: rolled back, watermark not changed.
- Auto retry 3 times; after that the run is handled manually outside NSP (no NSP screen).
- XD05 starts only after XD04 has succeeded (uses the data just synced); XD04 failed -> XD05 is not started."""
import glob, json

KEYS = 'GROUPING_BUYER_CD + GROUPING_PD_CD + ORDER_TYPE_GROUP + DEMAND_MONTH_YEAR + PART_NO'
COLS = ['GROUPING_BUYER_CD', 'GROUPING_PD_CD', 'ORDER_TYPE_GROUP', 'DEMAND_MONTH_YEAR', 'PART_NO', 'MAD', 'DAD', 'CREATE_DT',
        'CREATE_BY', 'UPDATE_DT', 'UPDATE_BY', 'N01_QTY', 'N02_QTY', 'N03_QTY', 'N04_QTY', 'N05_QTY', 'N06_QTY',
        'NUM_OF_OLD_PART_NO', 'NUM_OF_WORKINGDAY_6M', 'EM_MS_FLAG', 'INTERFACE_UPDATE_DT']
IF_COL = ['INTERFACE_UPDATE_DT', 'TIMESTAMP', '', 'N',
          'Interface update date and time of the row in DB Surrounding; XD04 reads only rows changed since the last successful run (watermark)']
WM = 'Last INTERFACE_UPDATE_DT taken by the previous successful run of this batch (kept in the Log); first run: all rows'
ORDER = ('Runs before XD05. XD05 starts only after XD04 has succeeded (scheduled run or retry) and uses the data just synced. '
         'When XD04 still fails after 3 retries, XD05 is not started (decided 6-Nov).')


def load(f):
    with open(f) as fh:
        return json.load(fh)


def save(f, s):
    with open(f, 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', f)


def add_if_col(s):
    changed = False
    for t in s.get('tables', []):
        if t['name'] == 'TB_R_ACTUAL_DEMAND_SUMMARY' and not any(c[0] == 'INTERFACE_UPDATE_DT' for c in t['columns']):
            t['columns'].append(list(IF_COL))
            changed = True
    return changed


# ---------- XD04 ----------
f = 'XD04_spec.json'
s = load(f)
g = s['general']
g['objective'] = [
    'To replicate TB_R_ACTUAL_DEMAND_SUMMARY from DB Surrounding to the table with the same name in NSP, so the XD05 DAD Volume Calculation (process 1 and 2) reads the actual demand inside NSP.',
    'Only the rows changed since the last successful run are read (INTERFACE_UPDATE_DT > watermark) and upserted per key; the whole table is not read every run (decided 6-Nov).',
    'In case any error occurs, the run is rolled back and the watermark is not changed, so the next run reads the same rows again. A failed run is retried automatically up to 3 times.',
    'All columns are replicated as they are, including DAD (not used by the calculation) (decided 19-Oct).']
g['operation_flow']['flow'] = {'direction': 'TB', 'nodes': [
    {'id': 'a', 'label': 'Scheduler (monthly) / auto retry', 'type': 'event'},
    {'id': 'b', 'label': 'Read changed rows (INTERFACE_UPDATE_DT > watermark)', 'type': 'process'},
    {'id': 'c', 'label': 'Upsert per key', 'type': 'process'},
    {'id': 'd', 'label': 'Success?', 'type': 'decision'},
    {'id': 'e', 'label': 'Commit, new watermark, Log SUCCESS, start XD05', 'type': 'process'},
    {'id': 'f', 'label': 'Roll back, watermark not changed, Log FAILED, retry', 'type': 'process'}],
    'edges': [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'},
              {'from': 'd', 'to': 'e', 'label': 'Yes'}, {'from': 'd', 'to': 'f', 'label': 'No'}]}
g['inputs'] = [
    {'name': 'TB_R_ACTUAL_DEMAND_SUMMARY (DB Surrounding)', 'type': 'DB', 'description': 'Rows with INTERFACE_UPDATE_DT > watermark'},
    {'name': 'Log', 'type': 'DB', 'description': 'Watermark of the last successful run'}]
g['outputs'] = [
    {'name': 'TB_R_ACTUAL_DEMAND_SUMMARY (NSP)', 'type': 'DB', 'description': 'if successful: changed rows inserted (new key) or updated (existing key)'},
    {'name': 'Log', 'type': 'DB', 'description': 'One record per run attempt (SUCCESS / FAILED); new watermark only when SUCCESS'}]
g['extra_tables'] = [
    {'title': 'Parameters', 'columns': [{'title': 'Name', 'width': 14}, {'title': 'Description', 'width': 34}],
     'rows': [['Watermark', WM]]},
    {'title': 'Execution Schedule', 'columns': [{'title': 'Item', 'width': 12}, {'title': 'Description', 'width': 36}],
     'rows': [['Trigger', 'Monthly scheduler (set in the system master; not detailed in this document).'],
              ['Auto retry', 'A failed run is retried automatically up to 3 times. After the 3rd failed retry the run is handled manually outside NSP (no screen in NSP, not part of this function) (decided 6-Nov).'],
              ['Order', ORDER]]}]

s['func_flow'] = {'flow': {'direction': 'TB', 'nodes': [
    {'id': 'p1', 'label': 'Start (scheduler / retry)', 'type': 'process', 'step': 1},
    {'id': 'p2', 'label': 'Get watermark', 'type': 'process', 'step': 2},
    {'id': 'logi', 'label': 'Log', 'type': 'db', 'lane': 'input'},
    {'id': 'src', 'label': 'TB_R_ACTUAL_DEMAND_SUMMARY (DB Surrounding)', 'type': 'db', 'lane': 'input'},
    {'id': 'p3', 'label': 'Read changed rows', 'type': 'process', 'step': 3},
    {'id': 'p4', 'label': 'Upsert per key', 'type': 'process', 'step': 4},
    {'id': 'dst', 'label': 'TB_R_ACTUAL_DEMAND_SUMMARY (NSP)', 'type': 'db', 'lane': 'output'},
    {'id': 'd', 'label': 'Any error?', 'type': 'decision', 'step': 5},
    {'id': 'p6', 'label': 'Commit, new watermark', 'type': 'process', 'step': 6},
    {'id': 'p7', 'label': 'Roll back, retry', 'type': 'process', 'step': 7},
    {'id': 'p8', 'label': 'Record result in Log', 'type': 'process', 'step': 8},
    {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
    'edges': [{'from': 'p1', 'to': 'p2'}, {'from': 'logi', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'src', 'to': 'p3'},
              {'from': 'p3', 'to': 'p4'}, {'from': 'p4', 'to': 'dst'}, {'from': 'p4', 'to': 'd'},
              {'from': 'd', 'to': 'p6', 'label': 'No'}, {'from': 'd', 'to': 'p7', 'label': 'Yes'},
              {'from': 'p6', 'to': 'p8'}, {'from': 'p7', 'to': 'p8'}, {'from': 'p8', 'to': 'log'}]},
    'steps': [
        'The scheduler starts the batch (monthly, set in the system master) or an automatic retry starts it. Write LOG1.',
        {'text': 'Get the watermark: WATERMARK of the latest SUCCESS record of this batch in the Log.',
         'children': ['No SUCCESS record yet (first run): all rows are read.']},
        {'text': 'Read the rows of TB_R_ACTUAL_DEMAND_SUMMARY (DB Surrounding) with INTERFACE_UPDATE_DT > watermark.',
         'children': ['No row: nothing to upsert; the run ends with SUCCESS, 0 rows, and the watermark stays the same.']},
        {'text': 'Upsert into TB_R_ACTUAL_DEMAND_SUMMARY (NSP) per key (' + KEYS + '):',
         'children': ['New key: insert the row with all source columns.', 'Existing key: update all other columns with the source values.']},
        'Check whether any error occurred during steps 2 to 4.',
        'No error: commit. The new watermark = max INTERFACE_UPDATE_DT of the rows read. Start XD05 DAD Volume Calculation.',
        {'text': 'Error: roll back step 4; the watermark is not changed, so the next run reads the same rows again.',
         'children': ['The scheduler retries automatically up to 3 times (RUN_TYPE = RETRY, RETRY_NO 1-3).',
                      'After the 3rd failed retry: LOG6, XD05 is not started; the run is handled manually outside NSP.']},
        'Record the result (SUCCESS / FAILED, inserted / updated rows, watermark, error message) in the Log. Exit.']}

s['data_map'] = {'blocks': [
    {'source': {'table': 'TB_R_ACTUAL_DEMAND_SUMMARY (DB Surrounding)', 'keys': [{'field': 'INTERFACE_UPDATE_DT', 'value': '> watermark'}]},
     'destination': {'table': 'TB_R_ACTUAL_DEMAND_SUMMARY (NSP)', 'operation': 'Insert / Update',
                     'description': 'Upsert per key (insert when the key is new, else update)',
                     'keys': [{'field': KEYS, 'value': 'Key of the source row'}]},
     'mappings': [{'source_field': c, 'dest_field': c,
                   'description': 'Same value as the source (key: insert only)' if c in KEYS.split(' + ') else 'Same value as the source (insert and update)'}
                  for c in COLS]},
    {'source': 'Result of this run',
     'destination': {'table': 'Log', 'operation': 'Insert', 'description': 'One record per run attempt'},
     'mappings': [{'dest_field': 'BATCH_ID', 'description': "'ADS_SYNC'"},
                  {'dest_field': 'RUN_TYPE', 'description': 'SCHEDULE / RETRY'},
                  {'dest_field': 'RETRY_NO', 'description': '0 for the scheduled run, 1-3 for the auto retries'},
                  {'dest_field': 'STATUS', 'description': 'SUCCESS / FAILED'},
                  {'dest_field': 'ROW_COUNT', 'description': 'Rows inserted / updated (0 when FAILED)'},
                  {'dest_field': 'WATERMARK', 'description': 'Max INTERFACE_UPDATE_DT read in this run (next watermark; only when SUCCESS, else NULL)'},
                  {'dest_field': 'MESSAGE', 'description': 'Error message when FAILED'},
                  {'dest_field': 'START_DT / END_DT', 'description': 'Start and end date-time'}]}]}

fd = s['func_desc']
fd[0]['text'] = ('This batch copies the actual demand summary from DB Surrounding into NSP once a month. '
                 'The schedule is set in the system master (not explained in this document).')
fd[1]['items'] = [
    'Delta: only the rows with INTERFACE_UPDATE_DT later than the watermark (max INTERFACE_UPDATE_DT taken by the last successful run) are read; the whole table is not read.',
    'Upsert per key (' + KEYS + '): a new key is inserted, an existing key is updated. All columns are copied with the same names and values; no conversion is done.',
    'Upsert runs in one transaction (all-or-nothing). When the run fails it is rolled back and the watermark is not changed, so no changed row is skipped.',
    'Auto retry up to 3 times. After that the run is handled manually outside NSP (no NSP screen).',
    'XD05 DAD Volume Calculation starts only after XD04 has succeeded and calculates with the data just synced. XD04 failed after the retries: XD05 is not started.',
    'A row deleted in DB Surrounding is not deleted in NSP (delta read; to be confirmed).']

s['logging_messages'] = [
    {'event': 'Batch start', 'cause': 'Batch is called', 'type': 'Info', 'msg_id': 'LOG1',
     'message': 'Actual demand summary sync started (<RUN_TYPE>, retry <RETRY_NO>). Watermark <WATERMARK>.',
     'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Batch end', 'cause': 'Batch finishes', 'type': 'Info', 'msg_id': 'LOG2',
     'message': 'Actual demand summary sync ended. Status <STATUS>, inserted <INS>, updated <UPD>, new watermark <WATERMARK>.',
     'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Read source', 'cause': 'DB Surrounding cannot be reached or read', 'type': 'Error', 'msg_id': 'LOG3',
     'message': 'Cannot read TB_R_ACTUAL_DEMAND_SUMMARY from DB Surrounding: <ERROR_DETAIL>.',
     'action': {'system': 'Roll back. STATUS = FAILED. Watermark not changed. Retry.', 'user': '-'}},
    {'event': 'Upsert', 'cause': 'Insert / update of the NSP table fails', 'type': 'Error', 'msg_id': 'LOG4',
     'message': 'Cannot save TB_R_ACTUAL_DEMAND_SUMMARY into NSP: <ERROR_DETAIL>.',
     'action': {'system': 'Roll back. STATUS = FAILED. Watermark not changed. Retry.', 'user': '-'}},
    {'event': 'Unexpected error', 'cause': 'Any other system error', 'type': 'Critical', 'msg_id': 'LOG5',
     'message': 'Unexpected error: <ERROR_DETAIL>.',
     'action': {'system': 'Roll back. STATUS = FAILED. Watermark not changed. Retry.', 'user': '-'}},
    {'event': 'Retry exhausted', 'cause': 'Scheduled run and 3 retries failed', 'type': 'Warning', 'msg_id': 'LOG6',
     'message': 'Actual demand summary sync failed 3 times. DAD volume calculation is not started.',
     'action': {'system': 'Do not start XD05.', 'user': 'PIC handles the run manually outside NSP, then XD05 is run.'}}]

sm = s['sample_sheet']
sm['intro'] = ['Rows taken from the reference file 20261013_tb_r_actual_demand_summary_since_january-2026.xlsx (part 52119BZV60); INTERFACE_UPDATE_DT is an example value.',
               'Watermark of the last successful run = 2026-09-01 02:15:00: only rows with a later INTERFACE_UPDATE_DT are read and upserted.']
a = sm['sections'][0]
a['title'] = 'A. Source rows in DB Surrounding (excerpt)'
a['columns'] = a['columns'] + ['INTERFACE_UPDATE_DT', 'Read?']
a['widths'] = a['widths'][:7] + [21, 30]
ex = [('2026-10-01 01:10:00', 'Yes: new key -> insert'), ('2026-10-01 01:10:00', 'Yes: new key -> insert'),
      ('2026-10-01 01:10:00', 'Yes: new key -> insert'), ('2026-10-01 01:10:00', 'Yes: MAD changed -> update'),
      ('2026-08-01 01:05:00', 'No (not changed since watermark)'), ('2026-08-01 01:05:00', 'No (not changed since watermark)')]
a['rows'] = [r[:7] + list(e) for r, e in zip(a['rows'], ex)]
sm['sections'][1]['rows'] = [
    ['N1', 'Monthly run, 4 rows changed since the watermark 2026-09-01 02:15:00', '4 rows read: 3 inserted, 1 updated. Log SUCCESS, new watermark 2026-10-01 01:10:00. XD05 starts.'],
    ['N2', 'First run (no SUCCESS record in the Log)', 'All rows of the source are read and inserted. Log SUCCESS with the max INTERFACE_UPDATE_DT as watermark.'],
    ['N3', 'No row changed since the watermark', '0 rows. Log SUCCESS, watermark unchanged. XD05 starts.'],
    ['E1', 'DB Surrounding cannot be reached', 'Rolled back, watermark unchanged. Log FAILED, auto retry (max 3).'],
    ['E2', 'Upsert fails in the middle of the run', 'Rolled back (one transaction), watermark unchanged; the retry reads the same rows again.'],
    ['E3', 'Scheduled run and 3 retries failed', 'LOG6: XD05 is not started; PIC handles the run manually outside NSP.']]
add_if_col(s)
save(f, s)

# ---------- other specs: INTERFACE_UPDATE_DT column, XD05 order ----------
for f in sorted(glob.glob('XD*_spec.json')):
    if f == 'XD04_spec.json':
        continue
    s = load(f)
    ch = add_if_col(s)
    if f == 'XD05_spec.json':
        for t in s['general']['extra_tables']:
            for r in t['rows']:
                if r[0] == 'Order':
                    r[1] = ('Runs after XD04 has succeeded and calculates with the actual demand data just synced. '
                            'When XD04 still fails after its 3 retries, XD05 is not started (decided 6-Nov).')
                    ch = True
    if ch:
        save(f, s)
