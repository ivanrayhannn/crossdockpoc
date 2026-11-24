"""24-Nov (b): Export Crossdock Master list without Part Name and Last Sent columns; Sync Status shown as three states.
XD01 rev 0.13. Runs after apply_2411."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'XD01_spec.json')
s = json.load(open(p))
if not any(r['revision'] == '0.13' for r in s['revisions']):
    it = s['items']
    k = next(i for i, x in enumerate(it) if x.get('name') == 'Expand (arrow)')
    pn, name = it[k + 1], it[k + 2]
    assert pn['name'] == 'Part Number' and name['name'] == 'Part Name'
    pn['description'] = 'Tooltip: Part Name (PART_NAME of TB_M_PART_CANDIDATE).'
    del it[k + 2]
    st = next(x for x in it if x.get('name') == 'Sync Status' and x.get('field') == 'SYNC_STATUS (derived)')
    st['description'] = ('One line per target, AP POLE (Kanban or Export staging) and GTOPAS (GTOPAS staging), per part + period (refer 5.24): '
                         "'Non Sync' = amber chip with a dot (a row waits for [Sync]); 'Sync' = check mark with green text (every row sent); "
                         "'Not sent' = grey text (no staging row for the target yet). Tooltip: the state and the last send time (latest SYNC_DT). "
                         'Part Name and Last Sent are not columns of the list.')
    for o in s['operation']:
        if 'items' in o:
            o['items'] = [t.replace('Columns: Period, Part Number, Part Name, Destination Code, Pcs/Case', 'Columns: Period, Part Number, Part Name, Destination Code, Order Type, Pcs/Case') for t in o['items']]
    for c in s['screen_layout']:
        c['caption'] = c['caption'].replace('(Last Sent AP POLE / GTOPAS = time of the click)', '(tooltip Last Sent AP POLE / GTOPAS = time of the click)')
    s['revisions'].append({'revision': '0.13', 'author': 'FID Rayhan', 'date': '24-Nov-26', 'reviewed_by': '',
                           'description': 'Export Crossdock Master list: Part Name and Last Sent GTOPAS / AP POLE columns removed (tooltips); column rules; '
                                          'Sync Status as Non Sync chip / Sync check / Not sent.'})
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched XD01')
