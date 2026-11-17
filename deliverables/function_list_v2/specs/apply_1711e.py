"""17-Nov (4): definition of [Sync] (user): every part with status Active (ongoing period) or Inactive whose Sync Status is No Sync or Failed.
Inactive parts are deleted in GTOPAS / AP POLE; Candidate parts are never synchronised. Runs after apply_1711d."""
import json

DEF = ('every part with status Active (ongoing period) or Inactive whose Sync Status is No Sync or Failed, whatever the filter shows')

with open('XD01_spec.json') as fh:
    s = json.load(fh)
if not any(r['revision'] == '0.3' for r in s['revisions']):
    g = s['general']
    g['buttons'][16]['function'] = ('Start XD06 (GTOPAS) and XD07 (AP POLE) for ' + DEF + '; the parts become Waiting. The label shows the number '
                                    'of parts, e.g. Sync (21).')
    s['items'][82]['description'] = ('n = parts with status Active (ongoing period) or Inactive and Sync Status No Sync or Failed, whatever the filter. '
                                     'Disabled when n = 0. Refer Operation Description 5.16.')
    g['screen_mode_remarks'][3] = ('4) Sync is enabled only when at least one part with status Active (ongoing period) or Inactive is No Sync or '
                                   'Failed (not limited to the listed rows).')
    o = next(x for x in s['operation'] if x.get('items') and x['items'][0].startswith('Select every Active part of the ongoing period'))
    o['items'][0] = ('Select ' + DEF + ' (n of the button). Active parts: their part and destinations are added / changed in GTOPAS (XD06) and AP '
                     'POLE (XD07). Inactive parts: all their rows are deleted there (a part that was never synced has nothing to delete). '
                     'Candidate parts are never synchronised.')
    for b in s['data_map']['blocks']:
        src = b.get('source')
        if isinstance(src, dict) and any('listed in Active to Inactive' in k.get('value', '') for k in src.get('keys', [])):
            src['keys'] = [{'field': 'PART_STATUS', 'value': "'Active' (ongoing period) or 'Inactive'"},
                           {'field': 'SYNC_STATUS', 'value': "'0' (No Sync) or '2' (Failed)"}]
    s['revisions'].append({'revision': '0.3', 'author': 'FID Rayhan', 'date': '17-Nov-26', 'reviewed_by': '',
                           'description': '[Sync] takes ' + DEF + ' (Candidate never).'})
    with open('XD01_spec.json', 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched XD01')
