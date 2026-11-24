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

# (c) Used/Quota (Case) and one status column per target, narrow number columns. XD01 rev 0.14.
s = json.load(open(p))
if not any(r['revision'] == '0.14' for r in s['revisions']):
    it = s['items']
    for x in it:
        if x.get('name') == 'Total Case/Day (used / quota)':
            x['name'] = 'Used/Quota (Case)'
    k = next(i for i, x in enumerate(it) if x.get('name') == 'Sync Status' and x.get('field') == 'SYNC_STATUS (derived)')
    common = ("'Non Sync' = amber chip with a dot (a row waits for [Sync]); 'Sync' = check mark with green text (every row sent); "
              "'Not sent' = grey text (no staging row for the target yet). Tooltip: the state and the last send time (latest SYNC_DT). Refer 5.24.")
    ap = dict(it[k], name='AP POLE Status', field='SYNC_STATUS (derived)', source='TB_H_STG_APPOLE_KANBAN / TB_H_STG_APPOLE_EXPORT',
              description='Status of the part + period for AP POLE (Kanban or Export staging). ' + common)
    gt = dict(it[k], name='GTOPAS Status', field='SYNC_STATUS (derived)', source='TB_H_STG_GTOPAS',
              description='Status of the part + period for GTOPAS (GTOPAS staging). ' + common)
    it[k:k + 1] = [ap, gt]
    for o in s['operation']:
        if 'items' in o:
            o['items'] = [t.replace('Total Case/Day (used / quota)', 'Used/Quota (Case)') for t in o['items']]
        if 'text' in o:
            o['text'] = o['text'].replace('Total Case/Day (used / quota)', 'Used/Quota (Case)')
    s['revisions'].append({'revision': '0.14', 'author': 'FID Rayhan', 'date': '24-Nov-26', 'reviewed_by': '',
                           'description': "Export Crossdock Master list: column Used/Quota (Case) (was Total Case/Day (used / quota)); AP POLE Status and "
                                          'GTOPAS Status as two columns; narrower number columns.'})
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched XD01 (c)')

# (d) Export Crossdock Master: Upload / Export Excel in the page header (as Kanban Crossdock Master). XD01 rev 0.15.
s = json.load(open(p))
if not any(r['revision'] == '0.15' for r in s['revisions']):
    it = s['items']
    up = next(x for x in it if x.get('name') == 'Upload Excel (Mapping)')
    ex = next(x for x in it if x.get('name') == 'Export Excel (Mapping)')
    it.remove(up)
    it.remove(ex)
    up['description'] = 'Page header, right (same place as on Kanban Crossdock Master). ' + up['description']
    ex['description'] = 'Page header, right (same place as on Kanban Crossdock Master). ' + ex['description']
    k = next(i for i, x in enumerate(it) if x.get('group') == '<Mapping - Search Criteria Section>')
    it[k:k] = [{'group': '<Mapping - Header Section>'}, up, ex]
    s['revisions'].append({'revision': '0.15', 'author': 'FID Rayhan', 'date': '24-Nov-26', 'reviewed_by': '',
                           'description': 'Export Crossdock Master: Upload Excel and Export Excel moved to the page header, as on Kanban Crossdock Master.'})
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched XD01 (d)')
