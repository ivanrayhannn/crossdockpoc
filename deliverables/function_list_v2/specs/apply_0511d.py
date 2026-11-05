"""05-Nov (2): audit columns of the Part List - on the screen 'Created Date', 'Created By', 'Updated Date', 'Updated By'
(instead of 'Last Update'), in the Excel files CREATED_DT, CREATED_BY, UPDATED_DT, UPDATED_BY (TB_M_PART_CANDIDATE
CREATED_* / CHANGED_*)."""
import json

with open('XD01_spec.json') as f:
    s = json.load(f)
items = []
for it in s['items']:
    if it.get('name') == 'Last Update' and it.get('field') == 'CHANGED_DT, CHANGED_BY':
        base = dict(it, control='Label', type='Datetime', format='DD-Mon-YYYY HH:MI')
        items += [dict(base, name='Created Date', field='CREATED_DT', description='Date-time the part was registered.'),
                  dict(base, name='Created By', field='CREATED_BY', type='Varchar', format='', description='User who registered the part.'),
                  dict(base, name='Updated Date', field='CHANGED_DT', description='Date-time of the last change of the part.'),
                  dict(base, name='Updated By', field='CHANGED_BY', type='Varchar', format='', description='User of the last change of the part.')]
        continue
    if isinstance(it.get('description'), str):
        it['description'] = it['description'].replace('(by Last Update)', '(by Updated Date)')
    items.append(it)
s['items'] = items
txt = json.dumps(s, ensure_ascii=False)
txt = txt.replace('Last Update (CHANGED_DT)', 'Updated Date (CHANGED_DT)')
txt = txt.replace('Status, Effective Start Date, Last Update. Information only.',
                  'Status, Effective Start Date, CREATED_DT, CREATED_BY, UPDATED_DT, UPDATED_BY. Information only.')
txt = txt.replace("UPDATED_BY. Information only. Sample: sheet 'Export Part List'.", "UPDATED_BY. Information only. Sample: 'Export Part List'.")
s = json.loads(txt)
with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
