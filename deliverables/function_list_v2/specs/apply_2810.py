"""28-Oct (FB-024 / FB-025 / FB-051 / FB-062 / FB-063): Part List shows no incomplete-mapping counter or row marker (mapping completeness is followed
by D/S in Mapping per Destination); the Edit part data modal shows the Case/Day already mapped in the current period."""
import json

with open('XD01_spec.json') as f:
    s = json.load(f)
g = s['general']
g['objective'] = [o.replace('with their status, capacity and mapping completeness.', 'with their status and capacity.') for o in g['objective']]
items = []
for it in s['items']:
    if it.get('name') == 'Incomplete mapping marker':
        continue
    if it.get('name') == 'Registered parts counter':
        it['format'] = 'N parts'
        it['description'] = 'N = number of filtered rows (all pages).'
    items.append(it)
    if it.get('name') == 'Max Case/Day' and it.get('io') == 'I' and not any(x.get('name') == 'Mapped Case/Day (current period)' for x in s['items']):
        items.append({'name': 'Mapped Case/Day (current period)', 'source': 'TB_M_PART_CANDIDATE_DEST', 'field': 'CASE_DAY', 'type': 'Number',
                      'len': 'TBD', 'io': 'O', 'control': 'Label', 'justified': 'Left', 'initial': '', 'required': '', 'format': 'ZZ,ZZ9',
                      'validation': '', 'description': "Edit mode, Active parts only (Candidate / Inactive parts have no mapping). Total Case/Day of all destinations of the part in the ongoing period "
                      "(' · no destination yet' when none); red when Max Case/Day is below it. Shows the lowest allowed Max Case/Day before Save."})
s['items'] = items
ops = s['operation']
for i, b in enumerate(ops):
    if b.get('type') == 'heading' and b['text'] == '5.3 Result List':
        ops[i + 1]['items'] = ["Counter 'N parts' is counted over the whole filtered result, not only the current page.",
                               'Total Pcs/Day = Pcs/Case x Max Case/Day.']
    if b.get('type') == 'heading' and b['text'] == '5.5 Edit Part Data':
        lst = ops[i + 2]['items']
        new = ("Active part only: below Max Case/Day show 'Mapped Case/Day (current period): n' = total Case/Day of the part in TB_M_PART_CANDIDATE_DEST for the "
               "ongoing period (' · no destination yet' when none), so the user sees the lowest allowed Max Case/Day before Save.")
        if new not in lst:
            lst.insert(3, new)
with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)

# FB-062 / FB-063: Save (Edit mapping) flow - the check runs while editing (Save is disabled before the click);
# short decision label, the three conditions in the note under the diagram.
with open('XD01_spec.json') as f:
    s = json.load(f)
for fl in s['screen_flow']:
    if fl['title'] == 'Screen Flow for Save (Edit mapping)':
        fl['flow'] = {'direction': 'TB', 'nodes': [
            {'id': 's', 'label': 'START', 'type': 'start'},
            {'id': 'e1', 'label': 'Change destination / Case/Day in edit mode', 'type': 'event'},
            {'id': 'd1', 'label': 'Mapping valid?', 'type': 'decision'},
            {'id': 'm1', 'label': 'Save disabled, show banner (message no. 20 / 21)', 'type': 'message'},
            {'id': 'm2', 'label': 'Save enabled', 'type': 'message'},
            {'id': 'e2', 'label': 'On Click of Save button', 'type': 'event'},
            {'id': 'p1', 'label': 'Replace mapping of part and ongoing period', 'type': 'process'},
            {'id': 'db', 'label': 'TB_M_PART_CANDIDATE_DEST', 'type': 'db'},
            {'id': 'p2', 'label': 'Sync Status = No Sync', 'type': 'process'},
            {'id': 'db2', 'label': 'TB_M_PART_CANDIDATE', 'type': 'db'},
            {'id': 'x', 'label': 'Back to view mode', 'type': 'end'}],
            'edges': [{'from': 's', 'to': 'e1'}, {'from': 'e1', 'to': 'd1'}, {'from': 'd1', 'to': 'm1', 'label': 'No'},
                      {'from': 'm1', 'to': 'e1', 'label': 'correct the mapping'}, {'from': 'd1', 'to': 'm2', 'label': 'Yes'},
                      {'from': 'm2', 'to': 'e2'}, {'from': 'e2', 'to': 'p1'}, {'from': 'p1', 'to': 'db', 'style': 'dashed'},
                      {'from': 'p1', 'to': 'p2'}, {'from': 'p2', 'to': 'db2', 'style': 'dashed'}, {'from': 'p2', 'to': 'x'}],
            'same_rank': [['p1', 'db'], ['p2', 'db2']]}
        fl['notes'] = ['Mapping valid = all of: (1) total Case/Day of the part <= Max Case/Day (a lower total is allowed, shown as '
                       "'{n} case/day left'); (2) the part has at least one destination row; (3) every row has a destination selected.",
                       'The check runs on every change in edit mode, so [Save] is already disabled before it can be clicked '
                       '(see Operation Description 5.15 Save rules).']
with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
