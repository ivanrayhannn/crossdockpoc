"""28-Oct (FB-024 / FB-025): Part List shows no incomplete-mapping counter or row marker (mapping completeness is followed
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
