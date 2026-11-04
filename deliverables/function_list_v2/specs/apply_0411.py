"""04-Nov: XD01 Mapping per Destination - the list column shows Total Case/Day as used / quota (quota = Max Case/Day of
Part List); the allocation chip '{total} / {max} case/day used' of the Destination Mapping panel is removed (the note stays).
Item descriptions no longer start with '=' (Excel turned them into formulas, #NAME?)."""
import json

with open('XD01_spec.json') as f:
    s = json.load(f)

items = []
for it in s['items']:
    if it.get('name') == 'Allocation chip':
        continue
    d = it.get('description')
    if isinstance(d, str) and d.startswith('= '):
        it['description'] = 'Calculated: ' + d[2:]
    if it.get('name') == 'Total Case/Day' and it.get('source') == 'TB_M_PART_CANDIDATE_DEST':
        it.update(name='Total Case/Day (used / quota)', source='TB_M_PART_CANDIDATE_DEST / TB_M_PART_CANDIDATE',
                  field='SUM(CASE_DAY) / MAX_CASE_DAY', format='ZZ,ZZ9 / ZZ,ZZ9',
                  description='Used (bold) = sum of Case/Day of all destinations of the part and period; quota = Max Case/Day of the part in Part List.')
    items.append(it)
s['items'] = items

REP = [('Total Case/Day = sum of CASE_DAY of the part and period; Pcs/Day = Pcs/Case x Total Case/Day.',
        'Total Case/Day = used / quota (sum of CASE_DAY of the part and period / Max Case/Day); Pcs/Day = Pcs/Case x used.'),
       ('open the panel with the allocation chip, the note and the destination table',
        'open the panel with the allocation note and the destination table'),
       ('The allocation chip and note are recalculated on every change.', 'The allocation note is recalculated on every change.')]
for b in s['operation']:
    for k in ('items',):
        for i, t in enumerate(b.get(k, [])):
            if isinstance(t, str):
                for old, new in REP:
                    t = t.replace(old, new)
                b[k][i] = t

with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
