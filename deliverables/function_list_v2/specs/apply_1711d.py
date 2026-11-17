"""17-Nov (3): Sync Status rule (FB-204 / FB-205 / FB-207, agreed by the user).
Only a change that GTOPAS / AP POLE must receive sets No Sync:
- Status to or from Active (Candidate -> Active, Inactive -> Active, Active -> Inactive), by screen, upload or XD05.
- Pcs/Case or Max Case/Day of an Active part; destinations or Case/Day of the mapping.
Min MAD, Effective Start Date, Candidate <-> Inactive and a Save without change keep the Sync Status.
A manual Active -> Inactive (screen / upload) is listed in "Active to Inactive" like the one of XD05 and is taken by [Sync].
Runs after apply_1711c."""
import glob
import json

RULE = ('Sync Status rule (17-Nov): No Sync (0) only when a value sent to GTOPAS / AP POLE changes: Status to or from Active '
        '(Candidate -> Active, Inactive -> Active, Active -> Inactive), Pcs/Case or Max Case/Day of an Active part, destinations or Case/Day '
        'of the mapping. Min MAD, Effective Start Date, Candidate <-> Inactive and a Save without change keep the Sync Status.')
RULE_ROWS = [['Status Candidate -> Active', 'No Sync', 'Add in GTOPAS (when mapped) and AP POLE'],
             ['Status Active -> Inactive (screen, upload or XD05)', 'No Sync; listed in Active to Inactive; taken by [Sync]', 'Delete in GTOPAS and AP POLE'],
             ['Status Inactive -> Active', 'No Sync', 'Add again'],
             ['Pcs/Case or Max Case/Day of an Active part', 'No Sync', 'AP POLE Edit; GTOPAS Keep (no quantity)'],
             ['Destination or Case/Day of the mapping', 'No Sync', 'GTOPAS Add / Delete; AP POLE Add / Edit / Delete'],
             ['Min MAD, Effective Start Date', 'Not changed', 'Not sent to any target'],
             ['Status Candidate <-> Inactive', 'Not changed', 'Never in GTOPAS / AP POLE'],
             ['Save without change', 'Not changed', 'Nothing to send']]
SENT = 'a value sent to GTOPAS / AP POLE changed (Status to or from Active, Pcs/Case or Max Case/Day of an Active part)'


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
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': '17-Nov-26', 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = '17-Nov-26'
    s['header']['updated_by'] = 'FID Rayhan'
    return True


# history columns are FIELD_NAME / OLD_VALUE / NEW_VALUE (no OLD_STATUS / NEW_STATUS); a manual change counts too
for f in sorted(glob.glob('XD*_spec.json')):
    t = open(f).read()
    n = (t.replace('(XD05, TB_H_PART_CANDIDATE OLD_STATUS Active, NEW_STATUS Inactive)',
                   '(XD05, Save on XD01 or upload XD02: TB_H_PART_CANDIDATE FIELD_NAME PART_STATUS, OLD_VALUE Active, NEW_VALUE Inactive)')
          .replace('TB_H_PART_CANDIDATE (OLD_STATUS / NEW_STATUS, CREATED_DT = run date-time)',
                   'TB_H_PART_CANDIDATE (FIELD_NAME PART_STATUS, OLD_VALUE / NEW_VALUE, CREATED_DT = run date-time)'))
    if n != t:
        open(f, 'w').write(n)
        print('history columns', f)

# ---------------- XD01 ----------------
s = load('XD01')
if rev(s, '0.2', 'Sync Status rule: No Sync only when a value sent to GTOPAS / AP POLE changes; a manual Active -> Inactive is listed in '
                  'Active to Inactive and taken by [Sync] (FB-204 / FB-205).'):
    s['data_map']['blocks'][1]['mappings'][6]['description'] = "'0' (No Sync) when " + SENT + '; else not changed'
    for b in s['data_map']['blocks']:
        src = b.get('source')
        if isinstance(src, dict) and any(k.get('field') == 'PART_STATUS' and "'Active'" in k.get('value', '') for k in src.get('keys', [])) \
                and '[Sync]' in b['destination'].get('description', ''):
            src['keys'] = [{'field': 'PART_STATUS', 'value': "'Active' (ongoing period), or Inactive and listed in Active to Inactive"},
                           {'field': 'SYNC_STATUS', 'value': "'0' or '2' (Active); not '3' (Inactive listed)"}]
    o = s['operation']
    o[17]['items'][2] = ('Update TB_M_PART_CANDIDATE, CHANGED_BY and CHANGED_DT. SYNC_STATUS = 0 (No Sync) only when ' + SENT +
                         '; a change of Min MAD or Effective Start Date only, or a Save without change, keeps the Sync Status. Status Active -> '
                         'Inactive: the history record (FIELD_NAME PART_STATUS) gives the Status Changed Date of sheet Active to Inactive.')
    for r in o[31]['rows']:
        if r[0] == 'Sync Status' and r[1].startswith('No Sync'):
            r[2] = 'Not sent yet, or a value sent to GTOPAS / AP POLE changed since the last synchronisation (refer Sync Status rule).'
    o[47]['items'][2] = ('When a destination or its Case/Day changed, set SYNC_STATUS = 0 (No Sync) in TB_M_PART_CANDIDATE, so the D/S user '
                         'synchronises the part again; a Save without change keeps the Sync Status.')
    o[51]['items'][0] = o[51]['items'][0].replace('(set to No Sync by XD05)', '(Active -> Inactive by XD05, a Save or an upload, listed in Active to Inactive)')
    k = next(i for i, x in enumerate(o) if x.get('text', '').startswith('Active and newly Inactive parts are synchronised')) + 1
    o[k:k] = [{'type': 'text', 'level': 2, 'text': RULE},
              {'type': 'table', 'level': 2, 'columns': [{'title': 'Change', 'width': 20}, {'title': 'Sync Status', 'width': 16}, {'title': 'Target', 'width': 20}],
               'rows': RULE_ROWS}]
    save('XD01', s)

# ---------------- XD02 ----------------
s = load('XD02')
if rev(s, '0.2', 'Sync Status = No Sync only when ' + SENT + '; else kept (Sync Status rule of XD01, 17-Nov).'):
    s['func_flow']['steps'][5]['children'][2] = ('A new part gets Sync Status = No Sync. An updated part gets No Sync only when ' + SENT +
                                                 '; otherwise the Sync Status is kept.')
    s['data_map']['blocks'][1]['mappings'][8]['description'] = "'0' (No Sync) when " + SENT + '; else not changed'
    s['func_desc'][7]['items'][4] = ('A new record gets Sync Status = No Sync; an updated record only when ' + SENT + '. It is sent to GTOPAS and '
                                     'AP POLE by the RPA (XD06 / XD07) when D/S clicks [Sync] in Mapping per Destination. Status Active -> Inactive '
                                     'is listed in sheet Active to Inactive like the change of XD05.')
    save('XD02', s)

# ---------------- XD03 ----------------
s = load('XD03')
if rev(s, '0.2', 'Sync Status = No Sync only when the destinations or Case/Day of the part changed (Sync Status rule of XD01, 17-Nov).'):
    s['data_map']['blocks'][3]['mappings'][10]['description'] = "'0' (No Sync) when a destination or its Case/Day changed; else not changed"
    s['func_desc'][7]['items'][5] = ('Every part whose destinations or Case/Day changed gets Sync Status = No Sync in TB_M_PART_CANDIDATE; file rows '
                                     'equal to the current mapping keep it. It is sent to GTOPAS and AP POLE by the RPA (XD06 / XD07) when D/S clicks '
                                     '[Sync] on the screen.')
    save('XD03', s)

# ---------------- XD05 ----------------
s = load('XD05')
if rev(s, '0.2', 'SYNC_STATUS = 0 (No Sync) for every status change to or from Active (data edit mapping aligned with 4.3, FB-207); '
                  'AP POLE delete by RPA (XD07, WLM9Q890) instead of SFTP file.'):
    s['data_map']['blocks'][1]['mappings'][8]['description'] = ("'0' (No Sync) when the status changes to or from Active (Candidate -> Active, "
                                                                "Inactive -> Active, Active -> Inactive); else not changed (decided 30-Oct / 17-Nov)")
    s['func_desc'][7]['items'][2] = ('SYNC_STATUS: a part whose status changes to or from Active gets SYNC_STATUS = 0 (No Sync): Active -> Inactive is '
                                     'deleted by the next [Sync] in GTOPAS (XD06, RPA, all rows) and in AP POLE (XD07, RPA, WLM9Q890 [Delete]) '
                                     '(decided 30-Oct); Candidate -> Active and Inactive -> Active are added. Other status changes do not change '
                                     'SYNC_STATUS (17-Nov).')
    save('XD05', s)

# ---------------- XD06 / XD07 ----------------
for fid, no in (('XD06', '0.3'), ('XD07', '0.4')):
    s = load(fid)
    if rev(s, no, 'Sync Status rule of XD01 (No Sync only for a value sent to the target); a manual Active -> Inactive is also listed in '
                  'Active to Inactive and deleted.'):
        s['func_desc'][1]['items'][0] = s['func_desc'][1]['items'][0].replace(
            'Every change sets the part to No Sync.', 'Every change of a value sent to GTOPAS / AP POLE sets the part to No Sync (Sync Status rule of XD01, 17-Nov).')
        save(fid, s)
