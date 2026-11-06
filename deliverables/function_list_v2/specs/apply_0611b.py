"""06-Nov (2): FB-161 the source never deletes rows, new data comes as new rows; FB-162 the delta column is CREATE_DT
(no INTERFACE_UPDATE_DT column); FB-163 XD05 starts automatically when its trigger finds new data in the replicated table."""
import glob, json

NEW_DATA = ('The scheduler checks TB_R_ACTUAL_DEMAND_SUMMARY (NSP): XD05 starts when the table has rows with CREATE_DT later than '
            'DATA_DT of the last successful XD05 run (new data from XD04). No new data: XD05 is not started (decided 6-Nov).')


def load(f):
    with open(f) as fh:
        return json.load(fh)


def save(f, s):
    with open(f, 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', f)


def rep(o, pairs):
    if isinstance(o, dict):
        return {k: rep(v, pairs) for k, v in o.items()}
    if isinstance(o, list):
        return [rep(v, pairs) for v in o]
    if isinstance(o, str):
        for a, b in pairs:
            o = o.replace(a, b)
    return o


def drop_if_col(s):
    ch = False
    for t in s.get('tables', []):
        if t['name'] == 'TB_R_ACTUAL_DEMAND_SUMMARY':
            n = len(t['columns'])
            t['columns'] = [c for c in t['columns'] if c[0] != 'INTERFACE_UPDATE_DT']
            ch = ch or n != len(t['columns'])
    return ch


# ---------- XD04 ----------
f = 'XD04_spec.json'
s = load(f)
drop_if_col(s)
s['data_map']['blocks'][0]['mappings'] = [m for m in s['data_map']['blocks'][0]['mappings'] if m['dest_field'] != 'INTERFACE_UPDATE_DT']
s = rep(s, [
    ('Only the rows changed since the last successful run are read (INTERFACE_UPDATE_DT > watermark) and upserted per key; the whole table is not read every run (decided 6-Nov).',
     'Only the new rows since the last successful run are read (CREATE_DT > watermark) and upserted per key; the whole table is not read every run. '
     'The source never deletes rows: new data always comes as new rows (decided 6-Nov).'),
    ('Delta: only the rows with INTERFACE_UPDATE_DT later than the watermark (max INTERFACE_UPDATE_DT taken by the last successful run) are read; the whole table is not read.',
     'Delta: only the rows with CREATE_DT later than the watermark (max CREATE_DT taken by the last successful run) are read; the whole table is not read.'),
    ('A row deleted in DB Surrounding is not deleted in NSP (delta read; to be confirmed).',
     'The source never deletes rows; its data is updated daily / weekly by adding new rows, so only rows not taken before are read (decided 6-Nov).'),
    ('XD05 DAD Volume Calculation starts only after XD04 has succeeded and calculates with the data just synced. XD04 failed after the retries: XD05 is not started.',
     'XD05 DAD Volume Calculation is started by its own trigger when the NSP table has new data (CREATE_DT later than the last XD05 run). XD04 failed after the retries: no new data, so XD05 is not started.'),
    ('No error: commit. The new watermark = max INTERFACE_UPDATE_DT of the rows read. Start XD05 DAD Volume Calculation.',
     'No error: commit. The new watermark = max CREATE_DT of the rows read. The new rows are picked up by the trigger of XD05.'),
    ('After the 3rd failed retry: LOG6, XD05 is not started; the run is handled manually outside NSP.',
     'After the 3rd failed retry: LOG6; the run is handled manually outside NSP. Without new rows XD05 is not started.'),
    ('Runs before XD05. XD05 starts only after XD04 has succeeded (scheduled run or retry) and uses the data just synced. '
     'When XD04 still fails after 3 retries, XD05 is not started (decided 6-Nov).',
     'Runs before XD05. XD05 is started by its trigger when the NSP table has new rows (CREATE_DT later than the last XD05 run), '
     'also after a manual run outside NSP. When XD04 still fails, there is no new data and XD05 is not started (decided 6-Nov).'),
    ('Commit, new watermark, Log SUCCESS, start XD05', 'Commit, new watermark, Log SUCCESS'),
    ("INTERFACE_UPDATE_DT is an example value", "CREATE_DT shown as example values"),
    ('Yes: MAD changed -> update', 'Yes: key exists -> update'),
    ('XD05 starts.', 'XD05 trigger finds new data.'),
    ('0 rows. Log SUCCESS, watermark unchanged. XD05 trigger finds new data.', '0 rows. Log SUCCESS, watermark unchanged. XD05 trigger finds no new data: XD05 is not started.'),
    ('LOG6: XD05 is not started; PIC handles the run manually outside NSP.',
     'LOG6: PIC handles the run manually outside NSP; when it succeeds, the XD05 trigger finds the new rows and starts XD05.'),
    ('Actual demand summary sync failed 3 times. DAD volume calculation is not started.',
     'Actual demand summary sync failed 3 times. Handle the run manually outside NSP.'),
    ('Do not start XD05.', 'Write the log. No new data for XD05.'),
    ('PIC handles the run manually outside NSP, then XD05 is run.', 'PIC handles the run manually outside NSP; XD05 then starts by its trigger.'),
    ('Read changed rows', 'Read new rows'), ('4 rows changed since', '4 new rows since'), ('No row changed since', 'No new row since'),
    ('INTERFACE_UPDATE_DT', 'CREATE_DT')])
# the sample table already shows CREATE_DT as its own column name
a = s['sample_sheet']['sections'][0]
a['columns'][7] = 'CREATE_DT'
save(f, s)

# ---------- XD05 and other specs ----------
for f in sorted(glob.glob('XD*_spec.json')):
    if f == 'XD04_spec.json':
        continue
    s = load(f)
    ch = drop_if_col(s)
    if f == 'XD05_spec.json':
        g = s['general']
        for t in g['extra_tables']:
            for r in t['rows']:
                if r[0] == 'Trigger':
                    r[1] = NEW_DATA + ' One run = process 1, then process 2. Check frequency set in the system master.'
                if r[0] == 'Order':
                    r[1] = ('Runs after XD04 has brought new data (scheduled run, retry or manual run outside NSP). '
                            'When XD04 still fails, there is no new data and XD05 is not started (decided 6-Nov).')
        g['operation_flow']['flow']['nodes'][0]['label'] = 'Trigger: new data in TB_R_ACTUAL_DEMAND_SUMMARY / retry / XD01 [Run calculation]'
        g['inputs'][0]['description'] += '; CREATE_DT later than DATA_DT of the last successful run = new data (trigger)'
        st = s['func_flow']['steps']
        st[0] = ('Process 1 (part status) starts when the trigger finds new data in TB_R_ACTUAL_DEMAND_SUMMARY (NSP) '
                 '(CREATE_DT later than DATA_DT of the last successful run), from an automatic retry, or [Run calculation (Part List)] on XD01.')
        for b in s['data_map']['blocks']:
            if b['destination']['table'] == 'Log':
                i = [m['dest_field'] for m in b['mappings']].index('STATUS')
                b['mappings'].insert(i + 1, {'dest_field': 'DATA_DT', 'description': 'Max CREATE_DT of TB_R_ACTUAL_DEMAND_SUMMARY (NSP) used by this run (only when SUCCESS); the trigger compares new data with it'})
        ch = True
    if ch:
        save(f, s)
