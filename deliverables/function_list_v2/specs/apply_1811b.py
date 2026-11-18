"""18-Nov (2): sheet "Active to Inactive" of the Mapping per Destination Export Excel removed (user). Since the [Sync] definition of 17-Nov
every Inactive part with No Sync / Failed is sent: XD06 deletes it because it is not in sheet Mapping per Destination, XD07 deletes it from
sheet Part List (Status Inactive, Sync Status Waiting). LAST_SYNC_DT and column Last Sync stay (information). Runs after apply_1811."""
import json

LS_DESC = ('Date-time of the last Success of the part for this target (kept when a later run is Failed); NULL when never synced. '
           'Shown as Last Sync on XD01.')
DROP = 'Sheet "Active to Inactive" removed (18-Nov): Inactive parts with No Sync / Failed are taken by [Sync] by their status.'


def load(fid):
    with open(f'{fid}_spec.json') as fh:
        return json.load(fh)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', fid)


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return False
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': '18-Nov-26', 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = '18-Nov-26'
    s['header']['updated_by'] = 'FID Rayhan'
    return True


def last_sync_col(s):
    for t in s.get('tables', []):
        for c in t['columns']:
            if c[0] == 'LAST_SYNC_DT':
                c[4] = LS_DESC


def replace(s, pairs):
    t = json.dumps(s, ensure_ascii=False)
    for a, b in pairs:
        t = t.replace(json.dumps(a, ensure_ascii=False)[1:-1], json.dumps(b, ensure_ascii=False)[1:-1])
    return json.loads(t)


# ---------------- XD01 ----------------
s = load('XD01')
if rev(s, '0.4', DROP + ' Export Excel of Mapping per Destination has 2 sheets again; column Last Sync stays.'):
    last_sync_col(s)
    o = s['operation']
    for x in o:
        if x.get('text') == 'Last Sync and Active to Inactive (17-Nov)':
            x['text'] = 'Last Sync (17-Nov)'
        if x.get('type') == 'table':
            for r in x.get('rows', []):
                if r[1] == 'No Sync; listed in Active to Inactive; taken by [Sync]':
                    r[1] = 'No Sync; taken by [Sync]'
        if x.get('items') and any(i.startswith('Export Excel of Mapping per Destination: sheet 1 gets column Last Sync Date') for i in x['items']):
            x['items'] = [('Export Excel of Mapping per Destination: sheet 1 gets column Last Sync Date. ' + DROP)
                          if i.startswith('Export Excel of Mapping per Destination: sheet 1') else i for i in x['items']]
    s = replace(s, [('Status Active -> Inactive: the history record (FIELD_NAME PART_STATUS) gives the Status Changed Date of sheet Active to Inactive.',
                     'Status changes are written to the history (FIELD_NAME PART_STATUS).'),
                    ('a manual Active -> Inactive is listed in Active to Inactive and taken by [Sync] (FB-204 / FB-205).',
                     'a manual Active -> Inactive is taken by [Sync] (FB-204 / FB-205).')])
    save('XD01', s)

# ---------------- XD02 / XD05 ----------------
s = load('XD02')
if rev(s, '0.3', DROP):
    s = replace(s, [(' Status Active -> Inactive is listed in sheet Active to Inactive like the change of XD05.',
                     ' Status Active -> Inactive (No Sync) is taken by the next [Sync] like the change of XD05.')])
    save('XD02', s)
s = load('XD05')
if rev(s, '0.3', DROP):
    s = replace(s, [('Active -> Inactive is read by XD06 / XD07 and the Export Excel of XD01 (sheet "Active to Inactive", 17-Nov).',
                     'An Inactive part with No Sync is taken by the next [Sync]: XD06 / XD07 delete it in GTOPAS / AP POLE.')])
    save('XD05', s)

# ---------------- XD06 ----------------
s = load('XD06')
if rev(s, '0.5', DROP + ' Inactive parts are not in sheet Mapping per Destination, so their rows are deleted by the compare.'):
    last_sync_col(s)
    fd = s['func_desc']
    h = next((i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.3a')), None)
    if h is not None:
        del fd[h:h + 2]
    t = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.3 '))
    fd[t + 1]['items'].append('On Success of the run: IF_STATUS 1, IF_DT and LAST_SYNC_DT = date-time of the result for every Waiting part. '
                              'On Failed: IF_STATUS 2 and IF_DT only; LAST_SYNC_DT is not changed.')
    s = replace(s, [('; sheet Active to Inactive = parts to delete', ''),
                    ('Waiting parts = Sync Status Waiting in the file (Active and Inactive). Sheet Active to Inactive: parts that went Inactive after '
                     'their last sync, for checking; every Inactive part is deleted anyway because it is not in the NSP list.',
                     'Waiting parts = Sync Status Waiting in the file (Active and Inactive). Inactive parts are not in sheet Mapping per Destination, '
                     'so all their rows in GTOPAS are deleted by the compare.')])
    save('XD06', s)

# ---------------- XD07 ----------------
s = load('XD07')
if rev(s, '0.5', DROP + ' Parts to delete = sheet Part List, Status Inactive, Sync Status Waiting.'):
    last_sync_col(s)
    s = replace(s, [
        (' and sheet Active to Inactive; only the parts', '; only the parts'),
        ('RPA: read source (Part List, Mapping, Active to Inactive)', 'RPA: read source (Part List, Mapping per Destination)'),
        ('XD01 Export Excel (Part List, Mapping, Active to Inactive)', 'XD01 Export Excel (Part List, Mapping per Destination)'),
        ('; sheet Active to Inactive: parts to delete', ''),
        ('; it reads them and sheet Active to Inactive.', '; it reads them.'),
        ('; parts to delete from sheet Active to Inactive.', '; parts to delete = Part List rows with Status Inactive (Waiting).'),
        ('(Part List, Mapping per Destination, sheet Active to Inactive), downloaded', '(Part List, Mapping per Destination), downloaded'),
        ('[Delete] (source: sheet Active to Inactive)', '[Delete] (source: Part List, Status Inactive, Waiting)'),
        ('(used by the sheet Active to Inactive of XD01, 4.3a)', '(shown as Last Sync on XD01)')])
    save('XD07', s)
