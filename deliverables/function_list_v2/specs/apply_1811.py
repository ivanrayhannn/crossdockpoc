"""18-Nov: XD06 follows the [Sync] definition of XD01 (apply_1711e): the Waiting parts are every part with status Active (ongoing period)
or Inactive whose Sync Status is No Sync or Failed; Candidate never. Runs after apply_1711e."""
import json

DEF = ('every part with status Active (ongoing period) or Inactive whose Sync Status is No Sync or Failed, whatever the filter '
       '(Candidate never)')

with open('XD06_spec.json') as fh:
    s = json.load(fh)
if not any(r['revision'] == '0.4' for r in s['revisions']):
    s['general']['objective'][1] = ('Per part + destination: in NSP (Active) and not in GTOPAS -> registered; in both -> skipped (no change); in '
                                    'GTOPAS and not in NSP -> deleted. Inactive parts are not in the NSP list, so their rows in GTOPAS are deleted. '
                                    '[Sync] sends ' + DEF + ' (definition of XD01, 17-Nov).')
    for i in s['general']['inputs']:
        if i['name'] == 'TB_R_CROSSDOCK_IF_RESULT':
            i['description'] = "Parts Waiting for 'GTOPAS' (IF_STATUS = '3'), set by [Sync] on XD01: " + DEF
    ff = s['func_flow']['steps']
    ff[0] = {'text': "[Sync] on XD01 sets the parts to Waiting (SYNC_STATUS = '3', IF_STATUS = '3' for 'GTOPAS' and 'APPOLE' in "
                     "TB_R_CROSSDOCK_IF_RESULT) and starts the RPA bot. Write LOG1. The whole bot run is inside one try-catch (step 6).",
             'children': ['Waiting parts = ' + DEF + '.',
                          'Active part: its destinations of the ongoing period are registered / kept in GTOPAS. Inactive part: all its rows are '
                          'deleted (none to delete when it was never synced; it still gets Success).']}
    ff[1]['children'][0] = ('NSP list = rows of sheet Mapping per Destination with a Destination Code (Active parts of the ongoing period, one row '
                            'per part + destination). A row with an empty Destination Code = Active part without destination. Inactive parts are '
                            'not in this sheet.')
    ff[1]['children'][1] = ('Waiting parts = Sync Status Waiting in the file (Active and Inactive). Sheet Active to Inactive: parts that went '
                            'Inactive after their last sync, for checking; every Inactive part is deleted anyway because it is not in the NSP list.')
    fd = s['func_desc']
    fd[1]['items'][1] = ('The D/S team clicks [Sync] when the changes are complete. [Sync] sends ' + DEF + '. The RPA bot makes the Crossdock '
                         'Master of GTOPAS equal to NSP, and XD07 updates AP POLE by RPA (screens WLM9Q890 / WLM9Q860).')
    h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.2'))
    t = next(i for i in range(h + 1, len(fd)) if fd[i].get('type') == 'table')
    fd[t + 1:t + 1] = [{'type': 'table', 'level': 0,
                        'columns': [{'title': 'Part status', 'width': 12}, {'title': 'Sync Status before [Sync]', 'width': 16},
                                    {'title': 'Sent by [Sync]', 'width': 10}, {'title': 'Result in GTOPAS', 'width': 30}],
                        'rows': [['Active (ongoing period)', 'No Sync / Failed', 'Y (Waiting)', 'Destinations registered / kept; rows not in NSP deleted'],
                                 ['Inactive', 'No Sync / Failed', 'Y (Waiting)', 'All rows of the part deleted (none when never synced)'],
                                 ['Active / Inactive', 'Success / Waiting', 'N', 'Still compared in the full list (no change expected)'],
                                 ['Candidate', 'Any', 'N', 'Never in GTOPAS']]}]
    s['revisions'].append({'revision': '0.4', 'author': 'FID Rayhan', 'date': '18-Nov-26', 'reviewed_by': '',
                           'description': 'Waiting parts follow the [Sync] definition of XD01: ' + DEF + '; table of the part status in 4.2.'})
    s['header']['updated_date'] = '18-Nov-26'
    with open('XD06_spec.json', 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched XD06')
