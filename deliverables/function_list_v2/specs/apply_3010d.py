"""30-Oct (4): FB-098 an Active part without destination deletes all its destinations in GTOPAS (decided);
FB-070 no housekeeping job: the change history is kept without retention limit;
FB-068 Screen Flow for Save (Add / Edit part data) redrawn like the Edit mapping one (validation before the click,
concurrency check, history). The Edit mapping flow shows the per-destination save (FB-085)."""
import json

KEEP_TABLE = 'No retention limit: the history is kept (no housekeeping job, decided 30-Oct).'
KEEP_OP = 'Retention: the history of a part is kept; there is no housekeeping job (decided 30-Oct).'
OLD_TABLE = ('Proposed retention: 24 months online by CREATED_DT; a monthly housekeeping job deletes older records '
             '(period configurable in system master). To be confirmed.')
RET_2910 = ('Retention: 24 months, counted from the later of CREATED_DT and the Effective Start Date of the part; '
            'a monthly housekeeping job deletes older records (period configurable in system master; job TBC).')


def load(fid):
    with open(f'{fid}_spec.json') as f:
        return json.load(f)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)


def replace_text(o, old, new):
    if isinstance(o, dict):
        return {k: replace_text(v, old, new) for k, v in o.items()}
    if isinstance(o, list):
        return [replace_text(v, old, new) for v in o]
    return o.replace(old, new) if isinstance(o, str) else o


# ---------- FB-070 (all functions with the history table)
for fid in ('XD01', 'XD02', 'XD03', 'XD05', 'XD06', 'XD07'):
    s = load(fid)
    s = replace_text(replace_text(s, OLD_TABLE, KEEP_TABLE), RET_2910, KEEP_TABLE)
    for b in s.get('operation', []):
        if str(b.get('text', '')).startswith('Retention:'):
            b['text'] = KEEP_OP
    save(fid, s)

# ---------- FB-098 (XD06)
s = load('XD06')
s = replace_text(s, 'or an Active part without destination (TBC)', 'or an Active part without destination (all its destinations in GTOPAS are deleted)')
s = replace_text(s, 'An Active part without destination: all its destinations in GTOPAS are deleted (TBC).',
                 'An Active part without destination: all its destinations in GTOPAS are deleted (decided 30-Oct).')
for b in s['func_desc']:
    if b.get('type') == 'bullets':
        b['items'] = [x for x in b['items'] if not x.startswith('Active part without destination: delete all')]
save('XD06', s)

# ---------- FB-068 / FB-085 (XD01 screen flows)
s = load('XD01')
for fl in s['screen_flow']:
    if fl['title'] == 'Screen Flow for Save (Add / Edit part data)':
        fl['flow'] = {'direction': 'TB', 'nodes': [
            {'id': 's', 'label': 'START', 'type': 'start'},
            {'id': 'e1', 'label': 'Enter / change part data in the Add Part or Edit part data modal', 'type': 'event'},
            {'id': 'd1', 'label': 'Part data valid?', 'type': 'decision'},
            {'id': 'm1', 'label': 'Save disabled, show tooltip / message (no. 5 / 7 / 15 / 16; Edit: 10 / 14)', 'type': 'message'},
            {'id': 'm2', 'label': 'Save enabled', 'type': 'message'},
            {'id': 'e2', 'label': 'On Click of Save button', 'type': 'event'},
            {'id': 'd2', 'label': 'Registered / changed by another user meanwhile?', 'type': 'decision'},
            {'id': 'm3', 'label': 'Show message no. 3 (Add) / 4 (Edit), stop', 'type': 'message'},
            {'id': 'p1', 'label': 'Insert (Add) / update (Edit) part, Sync Status = No Sync', 'type': 'process'},
            {'id': 'db', 'label': 'TB_M_PART_CANDIDATE', 'type': 'db'},
            {'id': 'p2', 'label': 'Insert change history', 'type': 'process'},
            {'id': 'db2', 'label': 'TB_H_PART_CANDIDATE', 'type': 'db'},
            {'id': 'm4', 'label': 'Close modal, part on top, message no. 9', 'type': 'message'},
            {'id': 'x', 'label': 'END', 'type': 'end'}],
            'edges': [{'from': 's', 'to': 'e1'}, {'from': 'e1', 'to': 'd1'}, {'from': 'd1', 'to': 'm1', 'label': 'No'},
                      {'from': 'm1', 'to': 'e1', 'label': 'correct the data'}, {'from': 'd1', 'to': 'm2', 'label': 'Yes'},
                      {'from': 'm2', 'to': 'e2'}, {'from': 'e2', 'to': 'd2'}, {'from': 'd2', 'to': 'm3', 'label': 'Yes'},
                      {'from': 'd2', 'to': 'p1', 'label': 'No'}, {'from': 'p1', 'to': 'db', 'style': 'dashed'},
                      {'from': 'p1', 'to': 'p2'}, {'from': 'p2', 'to': 'db2', 'style': 'dashed'}, {'from': 'p2', 'to': 'm4'},
                      {'from': 'm4', 'to': 'x'}],
            'same_rank': [['p1', 'db'], ['p2', 'db2']]}
        fl['notes'] = ['Part data valid = Add: Part No selected, Min MAD filled (whole number, 0 or more), Pcs/Case > 0 and Max Case/Day > 0 '
                       '(otherwise the tooltip shows message no. 5, 15, 16 or 7 for the first missing item). Edit: the same items, Effective '
                       'Start Date not before today while the part is Candidate (message no. 10), and Max Case/Day not below the Case/Day already '
                       'mapped in the ongoing period (message no. 14).',
                       'The check runs on every change in the modal, so [Save] is already disabled before it can be clicked '
                       '(see Operation Description 5.4 and 5.5).']
    if fl['title'] == 'Screen Flow for Save (Edit mapping)':
        for n in fl['flow']['nodes']:
            if n['id'] == 'p1':
                n['label'] = 'Update / insert / delete mapping per destination (ongoing period)'
save('XD01', s)
