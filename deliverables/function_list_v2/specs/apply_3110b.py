"""31-Oct (2): FB-117 the receive IF of AP POLE adds a new part, updates an existing one (Pcs/Case, Max Case/Day and
destinations, FB-116) and deletes an Inactive one - written as a rule table in XD07; review fixes of XD01 (FB-111..114)
and of XD07 (FB-118: the total Case/Day of a part may be below Max Case/Day)."""
import json


def replace_text(o, old, new):
    if isinstance(o, dict):
        return {k: replace_text(v, old, new) for k, v in o.items()}
    if isinstance(o, list):
        return [replace_text(v, old, new) for v in o]
    return o.replace(old, new) if isinstance(o, str) else o


def edit(fid, pairs, fn=None):
    with open(f'{fid}_spec.json') as f:
        s = json.load(f)
    for old, new in pairs:
        s = replace_text(s, old, new)
    if fn:
        fn(s)
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)


# ---------- XD07
def xd07(s):
    fd = s['func_desc']
    if not any(b.get('type') == 'table' and b['columns'][0]['title'] == 'Part in the file' for b in fd):
        i = next(n for n, b in enumerate(fd) if b.get('text') == '4.2 Field Rules') + 1
        fd.insert(i, {'type': 'table', 'level': 0, 'row_lines': 'all', 'columns': [
            {'title': 'Part in the file', 'width': 10}, {'title': 'In AP POLE', 'width': 6, 'align': 'center'},
            {'title': 'Receive IF of the TMA (Cross Dock Kanban Part Master)', 'width': 30}],
            'rows': [["CROSSDOCK_FLAG 'Y'", 'N', 'Add the part (Part No, Pcs/Case, Max Case/Day), then add its destinations with Case/Day'],
                     ["CROSSDOCK_FLAG 'Y'", 'Y', 'Edit the part: update Pcs/Case and Max Case/Day, and make its destinations and Case/Day equal to the file'],
                     ["CROSSDOCK_FLAG 'N' (Inactive)", 'Y', 'Delete the part (one row per part number)']]})
    for b in fd:
        if b.get('type') == 'bullets' and b['items'][0].startswith('Field names on the side of the target'):
            if not any('Add / Edit / Delete' in x for x in b['items']):
                b['items'].append('Receive IF of the TMA: Add / Edit / Delete as in 4.2 - to be confirmed with the TMA.')


edit('XD07', [
    ('A part is sent as one complete set; AP POLE replaces the data of the part, so a change such as Philippines up and Thailand down, '
     'or a removed destination, arrives as one consistent update.',
     'A part is sent as one complete set: AP POLE adds a new part, updates an existing part (Pcs/Case, Max Case/Day and destinations) '
     'and deletes an Inactive part (see 4.2), so a change such as Philippines up and Thailand down, or a removed destination, arrives '
     'as one consistent update.'),
    ('AP POLE replaces the cross dock master of every part in the file with the content of the file (all destinations of the part).',
     'AP POLE adds a part that it does not have yet, updates an existing part (Pcs/Case, Max Case/Day and all destinations) and '
     'deletes an Inactive part (see 4.2).'),
    ('Sum of CASE_DAY of the records of a part = MAX_CASE_DAY (guaranteed by XD05 and the save checks of XD01 / XD03).',
     'Sum of CASE_DAY of the records of a part <= MAX_CASE_DAY (guaranteed by XD05 and the save checks of XD01 / XD03; a lower total is allowed).')], xd07)

# ---------- XD01
def xd01(s):
    for b in s['operation']:
        for i, t in enumerate(b.get('items', [])):
            if isinstance(t, str) and t.endswith('for the first missing item. Effective Start Date'):
                b['items'][i] = t[:-len(' Effective Start Date')]


edit('XD01', [
    ('message no. 5, 15, 16 or 7 for the first missing item', 'message no. 5, 15, 6 or 7 for the first missing item'),
    ('Save disabled, show tooltip / message (no. 5 / 7 / 15 / 16; Edit: 10 / 14)', 'Save disabled, show tooltip / message (no. 5 / 6 / 7 / 15; Edit: 10 / 14)'),
    ('Only Active parts are synchronised. A Save while the part is Waiting',
     'Active and newly Inactive parts are synchronised (not Candidate). A Save while Waiting'),
    ('because a part is sent as one set (Pcs/Case, Max Case/Day and all destinations);',
     'because a part is synced as one unit (GTOPAS: destination list; AP POLE: Pcs/Case, Max Case/Day, destinations);'),
    ('with Case/Day of the ongoing period as one complete set (Inactive: part deleted).',
     'with Case/Day of the ongoing period (new part: added; existing: updated; Inactive: deleted).')], xd01)
