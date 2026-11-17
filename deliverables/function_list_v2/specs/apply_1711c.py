"""17-Nov (2): [Sync] runs the RPA from the download: the bot itself downloads the XD01 Export Excel, fills a work sheet in the file
(compare + action + result) and then works on the target screen. XD06 no longer reads the NSP database; XD07 open point on the source closed.
Runs after apply_1711b."""
import json

WORK_COLS = ('P/No., Destination Code, In NSP (Y/N), In GTOPAS (Y/N), Action (Keep / Add / Delete), Result (OK / Error), '
             'GTOPAS message, Done date-time')


def load(fid):
    with open(f'{fid}_spec.json') as fh:
        return json.load(fh)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', fid)


# ---------------- XD06 ----------------
s = load('XD06')
if not any(r['revision'] == '0.2' for r in s['revisions']):
    g = s['general']
    g['objective'][0] = ('To keep the Crossdock Master of GTOPAS equal to NSP by an RPA process (no interface file, decided 11-Nov): [Sync] on XD01 '
                         'starts the bot; the bot downloads the Export Excel of Mapping per Destination (ongoing period) from NSP, fills the work sheet '
                         '"GTOPAS Compare" in the file and maintains GTOPAS screen Crossdock Master (WVJA5204, menu Supply > Master > Crossdock Master) '
                         '(decided 17-Nov).')
    n = {x['id']: x for x in g['operation_flow']['flow']['nodes']}
    n['b']['label'] = 'RPA: download XD01 Export Excel (Mapping per Destination, ongoing period)'
    n['d']['label'] = 'Fill sheet GTOPAS Compare (Keep / Add / Delete), then add / delete on GTOPAS'
    g['inputs'] = [
        {'name': 'XD01 Export Excel: Mapping per Destination', 'type': 'File',
         'description': 'Downloaded by the bot after [Sync]: Calculation period = ongoing, Sync Status = All. Sheet Mapping per Destination '
                        '(Part Number, Destination Code, Sync Status) = NSP list; sheet Active to Inactive = parts to delete'},
        {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Parts Waiting for 'GTOPAS' (IF_STATUS = '3'), set by [Sync] on XD01"},
        {'name': 'GTOPAS Crossdock Master (WVJA5204)', 'type': 'System', 'description': 'All rows of Depot Code 01 (one row per part + destination), read by the bot page by page'}]
    g['outputs'].insert(1, {'name': 'RPA work file', 'type': 'File',
                            'description': 'The downloaded Excel with the new sheet GTOPAS Compare filled by the bot (' + WORK_COLS + '); kept as the evidence of the run'})
    for t in g['extra_tables']:
        if t['title'] == 'Parameters':
            for r in t['rows']:
                if r[0] == 'Method':
                    r[1] = ('RPA bot only (no interface file): [Sync] on XD01 starts it; it downloads the XD01 Export Excel, fills the work sheet '
                            'GTOPAS Compare and works on GTOPAS screen Crossdock Master (decided 11-Nov, source 17-Nov)')
                if r[0] == 'User':
                    r[1] = 'RPA bot user (NSP login for the download, GTOPAS login)'
    g['extra_tables'].append({'title': 'RPA work sheet GTOPAS Compare (added by the bot to the downloaded file)',
                              'columns': [{'title': 'Column', 'width': 14}, {'title': 'Content', 'width': 34}],
                              'rows': [['P/No.', 'Part Number (NSP) / P/No. without "-" (GTOPAS)'],
                                       ['Destination Code', 'Destination Code, 7 characters'],
                                       ['In NSP', 'Y when the key is in sheet Mapping per Destination'],
                                       ['In GTOPAS', 'Y when the key is in the GTOPAS list (Depot 01)'],
                                       ['Action', 'Keep (Y / Y), Add (Y / N), Delete (N / Y)'],
                                       ['Result', 'OK when the GTOPAS message is MZD34006FEI or Keep; Error otherwise (the run stops)'],
                                       ['GTOPAS message', 'Message of the screen after the action'],
                                       ['Done date-time', 'Date-time of the action']]})
    ff = s['func_flow']
    fn = {x['id']: x for x in ff['flow']['nodes']}
    fn['m']['label'] = 'XD01 Export Excel (downloaded by the bot)'
    fn['m']['type'] = 'db'
    fn['p2']['label'] = 'RPA: download Export Excel from NSP, read NSP list'
    fn['p4']['label'] = 'Fill sheet GTOPAS Compare, register / skip'
    ff['steps'][1] = {'text': 'The bot logs in to NSP, opens XD01 Crossdock Master Setting, tab Mapping per Destination, Calculation period = ongoing, '
                              'Sync Status = All, clicks [Search] and [Export Excel], and opens the downloaded file '
                              'Crossdock_Mapping_per_Destination_<Period>_YYYYMMDD.xlsx.',
                      'children': ['NSP list = rows of sheet Mapping per Destination with a Destination Code (Active parts of the ongoing period, one row '
                                   'per part + destination). A row with an empty Destination Code = Active part without destination. Waiting parts = '
                                   'Sync Status Waiting.',
                                   'Sheet Active to Inactive: parts that went Inactive after their last sync (not in the NSP list, their rows are deleted).']}
    st = ff['steps'][3]
    st['children'].append('The bot adds the sheet GTOPAS Compare to the file: one row per P/No. + Destination Code of NSP or GTOPAS with In NSP, '
                          'In GTOPAS and Action (Keep / Add / Delete); after each action it fills Result, GTOPAS message and Done date-time.')
    s = json.loads(json.dumps(s, ensure_ascii=False)
                   .replace('timeout, error message instead of MZD34006FEI, NSP database not available',
                            'timeout, error message instead of MZD34006FEI, NSP download failed or the Excel cannot be read')
                   .replace('an error message instead of MZD34006FEI, NSP database not available.',
                            'an error message instead of MZD34006FEI, NSP download failed or the Excel cannot be read.')
                   .replace('GTOPAS error message or NSP database error', 'GTOPAS error message, NSP download or Excel error'))
    fd = s['func_desc']
    fd[1]['items'][2] = ('RPA only (decided 11-Nov): the D/S team only clicks [Sync]. The bot downloads the XD01 Export Excel, fills the work sheet '
                         'GTOPAS Compare and works on GTOPAS screen Crossdock Master (WVJA5204); it does not read the NSP database (decided 17-Nov). '
                         'Steps with the screens: deliverables/user_guide/Crossdock_User_Guide_GTOPAS.xlsx.')
    b = s['data_map']['blocks'][0]
    b['source']['table'] = 'XD01 Export Excel Mapping per Destination (downloaded by the bot)'
    b['source']['keys'] = [{'field': 'Calculation period', 'value': 'Ongoing'}, {'field': 'Destination Code', 'value': 'Not empty'}]
    for m in b['mappings']:
        m['source_field'] = {'PART_NO': 'Part Number', 'DEST_CODE': 'Destination Code'}.get(m['source_field'], m['source_field'])
    s['revisions'].append({'revision': '0.2', 'author': 'FID Rayhan', 'date': '17-Nov-26', 'reviewed_by': '',
                           'description': '[Sync] runs the RPA from the download: the bot downloads the XD01 Export Excel (no direct read of the NSP '
                                          'database), fills the work sheet GTOPAS Compare and then adds / deletes on WVJA5204. User guide '
                                          'Crossdock_User_Guide_GTOPAS.xlsx.'})
    s['header']['updated_date'] = '17-Nov-26'
    s['header']['updated_by'] = 'FID Rayhan'
    save('XD06', s)

# ---------------- XD07 ----------------
s = load('XD07')
if not any(r['revision'] == '0.3' for r in s['revisions']):
    s['general']['objective'][1] = ('Source data: the Export Excel files of XD01, downloaded by the bot itself after [Sync] (decided 17-Nov): Part List '
                                    '(Status, Part Name, Pcs/Case, Max Case/Day), Mapping per Destination of the ongoing period (Destination Code, '
                                    'Dest Case/Day, Last Sync Date) and sheet Active to Inactive; only the parts with Sync Status Waiting.')
    st = s['func_flow']['steps'][1]
    txt = ('The bot logs in to NSP and downloads the XD01 Export Excel: Mapping per Destination (ongoing period, Sync Status = Waiting) and '
           'Part List; it reads them and sheet Active to Inactive. It adds the work sheet AP POLE Compare to the file (part / Buyer-PD, NSP value, '
           'AP POLE value, Action Add / Edit / Delete / Keep, Result, AP POLE message).')
    if isinstance(st, dict):
        st['text'] = txt
    else:
        s['func_flow']['steps'][1] = txt
    fd = s['func_desc']
    fd[1]['items'][1] = ('The D/S team clicks [Sync] when the changes are complete; that is the only manual step. The RPA bot downloads the Excel, '
                         'fills the work sheet and makes AP POLE equal to NSP (XD07) and GTOPAS (XD06).')
    fd[1]['items'][3] = ('Source data: the XD01 Export Excel files (Part List, Mapping per Destination, sheet Active to Inactive), downloaded by the bot '
                         'after [Sync]; parts with Sync Status Waiting. Steps with the screens: deliverables/user_guide/Crossdock_User_Guide_AP_POLE.xlsx.')
    s = json.loads(json.dumps(s, ensure_ascii=False)
                   .replace('Source: XD01 Export Excel downloaded by the D/S team or a direct read of the NSP database (as XD06) - TBC.',
                            'Source: the XD01 Export Excel, downloaded by the bot after [Sync] (decided 17-Nov, closed).')
                   .replace('XD01 Export Excel Part List (read by the bot)', 'XD01 Export Excel Part List (downloaded by the bot)')
                   .replace('XD01 Export Excel Mapping per Destination (read by the bot)', 'XD01 Export Excel Mapping per Destination (downloaded by the bot)'))
    for i in s['general']['inputs']:
        if i['name'].startswith('XD01 Export Excel'):
            i['description'] = 'Downloaded by the bot after [Sync]. ' + i['description']
    s['revisions'].append({'revision': '0.3', 'author': 'FID Rayhan', 'date': '17-Nov-26', 'reviewed_by': '',
                           'description': '[Sync] runs the RPA from the download: the bot downloads the XD01 Export Excel itself and fills the work '
                                          'sheet AP POLE Compare (source open point closed).'})
    save('XD07', s)
