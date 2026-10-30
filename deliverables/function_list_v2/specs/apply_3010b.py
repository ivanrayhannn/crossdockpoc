"""30-Oct (2): a part that became Inactive is removed from GTOPAS by the RPA bot (all rows part + destination, menu
Supply > Master > Crossdock Master, search by Part No); AP POLE is not changed for it (XD07 no longer sends Inactive parts)."""
import json


def load(fid):
    with open(f'{fid}_spec.json') as f:
        return json.load(f)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)


def replace_text(o, old, new):
    if isinstance(o, dict):
        return {k: replace_text(v, old, new) for k, v in o.items()}
    if isinstance(o, list):
        return [replace_text(v, old, new) for v in o]
    return o.replace(old, new) if isinstance(o, str) else o


MENU = 'menu Supply > Master > Crossdock Master'

# ---------- XD06
s = load('XD06')
g = s['general']
g['objective'][2] = ("Parts that became Inactive: the bot deletes all rows of the part in GTOPAS (one row per part + destination, "
                     "e.g. 10 destinations -> 10 rows deleted). AP POLE is not changed for them (XD07).")
g['objective'][3] = g['objective'][3].replace('RPA bot on the GTOPAS screen.', f'RPA bot on GTOPAS ({MENU}, search by Part No).')
for n in g['operation_flow']['flow']['nodes']:
    n['label'] = {'b': 'Read Waiting parts for GTOPAS (Active / Inactive)',
                  't': 'GTOPAS Crossdock Master: register / delete rows'}.get(n['id'], n['label'])
for i in g['inputs']:
    if i['name'] == 'TB_M_PART_CANDIDATE':
        i['description'] = 'Part List: PART_NO, PART_STATUS (Active, or Inactive since the last send), CHANGED_DT'
    if i['name'].startswith('GTOPAS'):
        i['description'] = f'{MENU}: rows of the part (one per part + destination), read by the bot after search by Part No'
for t in g['extra_tables']:
    if t['title'] == 'Parameters':
        t['rows'][2][1] = f'RPA bot on GTOPAS ({MENU}); the steps of the bot are detailed in the RPA design (not in this document).'
    if t['title'] == 'RPA Input Data':
        rows = [r for r in t['rows'] if r[0] != 'CROSSDOCK_FLAG']
        for r in rows:
            if r[0] == 'PART_NO':
                r[4] = 'Part with Sync Status Waiting for GTOPAS: Active, or became Inactive since the last send'
            if r[0] == 'DEST_CODE':
                r[4] = ('Destination code (buyer code + PD code); one record per destination. Blank for an Inactive part '
                        '(one record) or an Active part without destination (TBC)')
        rows.insert(2, ['CROSSDOCK_FLAG', 'TB_M_PART_CANDIDATE.PART_STATUS', 'CHAR(1)', 'Y',
                        "'Y' = Active: make the destinations equal to NSP / 'N' = Inactive: delete all rows of the part in GTOPAS"])
        t['rows'] = rows
f = s['func_flow']
for n in f['flow']['nodes']:
    if n['id'] == 'p2':
        n['label'] = 'Select Waiting parts for GTOPAS'
    if n['id'] == 'p4':
        n['label'] = 'RPA (Crossdock Master): register / ignore / delete; Inactive: delete all rows'
f['steps'][1] = {'text': "Select the parts with TARGET_SYSTEM = 'GTOPAS' and IF_STATUS = '3' in TB_R_CROSSDOCK_IF_RESULT. Keep CHANGED_DT of each part.",
                 'children': ["PART_STATUS Active: sent with its destinations (CROSSDOCK_FLAG 'Y').",
                              "PART_STATUS Inactive: sent with CROSSDOCK_FLAG 'N' to delete the part in GTOPAS.",
                              'No part: write LOG2 and exit.']}
f['steps'][2] = {'text': 'Create the RPA input XD_CDMASTER_GTOPAS_<YYYYMMDDHHMMSS>.csv (see RPA Input Data):',
                 'children': ["Active part: one record per destination of the ongoing period in TB_M_PART_CANDIDATE_DEST (PART_NO, CROSSDOCK_FLAG 'Y', PERIOD, DEST_CODE); "
                              'without destination: one record with DEST_CODE blank.',
                              "Inactive part: one record with CROSSDOCK_FLAG 'N' and DEST_CODE blank.",
                              'Same SEND_ID and SEND_DT on every record. Error: LOG3, all parts of the run Failed (step 6).']}
f['steps'][3] = {'text': f'Start the RPA bot with the input. Per part the bot opens GTOPAS {MENU}, searches the Part No (one row per part + destination) and:',
                 'children': ["CROSSDOCK_FLAG 'Y': compares the rows with the input by DEST_CODE - in the input and not in GTOPAS: register; in both: ignore; "
                              'in GTOPAS and not in the input: delete.',
                              "CROSSDOCK_FLAG 'N' (Inactive): deletes all rows of the part (e.g. 10 destinations -> 10 rows deleted).",
                              'The bot returns one result per part (see RPA Result Data). Part NG: LOG6. Bot not available or no result within the time limit: '
                              'LOG4, all parts of the run Failed.']}
dm = s['data_map']['blocks']
dm[0]['source']['keys'][1]['value'] = 'Active / Inactive'
if not any(m['dest_field'] == 'CROSSDOCK_FLAG' for m in dm[0]['mappings']):
    dm[0]['mappings'].insert(2, {'source_field': 'PART_STATUS', 'dest_field': 'CROSSDOCK_FLAG', 'description': "'Y' Active / 'N' Inactive"})
for m in dm[0]['mappings']:
    if m['dest_field'] == 'DEST_CODE':
        m['description'] = 'Same value; blank for an Inactive part or a part without destination'
dm[1]['destination']['table'] = 'GTOPAS Crossdock Master (by RPA)'
dm[1]['mappings'] = [m for m in dm[1]['mappings'] if 'Inactive' not in m['description']] + \
    [{'dest_field': '', 'description': "All rows of the part deleted when CROSSDOCK_FLAG 'N' (Inactive)"}]
for b in dm:
    if b['destination'].get('table') == 'TB_R_CROSSDOCK_IF_RESULT':
        for m in b['mappings']:
            m['description'] = {'IF_STATUS': "'1' RPA OK / '2' input, bot or part error",
                                'IF_MESSAGE': "'added ...; deleted ...' when '1' (Inactive part: 'deleted all <n> rows'); reason when '2'"
                                }.get(m['dest_field'], m['description'])
fd = s['func_desc']
fd[1]['items'][1] = 'Every change sets the part to No Sync. The D/S team clicks [Sync] when the changes are complete; Active parts and parts that became Inactive are sent to GTOPAS.'
fd[2]['items'] = [f'Method: RPA bot on GTOPAS {MENU} (decided 30-Oct): search by Part No; the list has one row per part + destination. '
                  'The steps of the bot are detailed in the RPA design.',
                  "Parts that became Inactive (XD05 process 1) are sent with CROSSDOCK_FLAG 'N': the bot deletes all rows of the part in GTOPAS "
                  '(e.g. 10 destinations -> 10 rows deleted) (decided 30-Oct). AP POLE is not changed for them (XD07).']
for b in fd:
    if b.get('type') == 'table' and b['columns'][0]['title'] == 'In NSP':
        if not any('Inactive' in r[0] for r in b['rows']):
            b['rows'].append(['Inactive part', 'Y', 'Delete all rows of the part'])
for b in fd:
    if b.get('type') == 'bullets':
        b['items'] = [x.replace('RPA design: GTOPAS screens, start of the bot by XD06,', 'RPA design: start of the bot by XD06,') for x in b['items']]
save('XD06', s)

# ---------- XD07: Inactive parts are not sent to AP POLE
s = load('XD07')
s['general']['objective'][0] = s['general']['objective'][0].replace(
    ", and parts that became Inactive (CROSSDOCK_FLAG 'N', so AP POLE changes their status to inactive).",
    ". Parts that became Inactive are not sent: AP POLE is not changed for them (decided 30-Oct).")
for t in s['general']['extra_tables']:
    for r in t['rows']:
        if r[0] == 'PART_NO' and 'Inactive' in r[-1]:
            r[-1] = 'Active cross dock part with Sync Status Waiting'
        if r[0] == 'CROSSDOCK_FLAG':
            r[-1] = "'Y' = Active (handled by crossdock). Inactive parts are not sent to AP POLE (decided 30-Oct; GTOPAS deletes them, XD06)"
s['func_flow']['steps'][1] = {'text': "Select the parts with TARGET_SYSTEM = 'APPOLE' and IF_STATUS = '3' in TB_R_CROSSDOCK_IF_RESULT. Keep CHANGED_DT of each part.",
                              'children': ['PART_STATUS Active: sent (step 3).',
                                           "PART_STATUS Inactive: not sent; IF_STATUS = '1', IF_MESSAGE = 'Inactive part: AP POLE not changed' (step 6).",
                                           'No Active part: go to step 6.']}
for b in s['data_map']['blocks']:
    if b['destination'].get('table') == 'TB_R_CROSSDOCK_IF_RESULT':
        for m in b['mappings']:
            m['description'] = {'IF_STATUS': "'1' transfer OK or Inactive part (not sent) / '2' file or transfer error",
                                'IF_MESSAGE': "Error when '2'; 'Inactive part: AP POLE not changed' for an Inactive part; blank otherwise"
                                }.get(m['dest_field'], m['description'])
s = replace_text(s, "Parts that became Inactive (XD05 process 1) are No Sync and are sent with CROSSDOCK_FLAG 'N' and without destinations; AP POLE changes the status of the part to inactive.",
                 "Parts that became Inactive (XD05 process 1) are not sent to AP POLE (decided 30-Oct): their 'APPOLE' row is set to '1' "
                 "(IF_MESSAGE 'Inactive part: AP POLE not changed'); GTOPAS deletes all their rows (XD06).")
save('XD07', s)

# ---------- XD01 / XD05 references
for fid, pairs in (('XD01', [("Inactive parts are sent to AP POLE with CROSSDOCK_FLAG 'N'; GTOPAS is not changed for them (refer XD06).",
                              "Inactive parts: all their rows are deleted in GTOPAS (XD06); AP POLE is not changed for them."),
                             ('registers / deletes, by RPA, the destinations of each Waiting Active part in GTOPAS (destination list only; no Case/Day). '
                              'XD07 IF Cross Dock Master to AP POLE sends',
                              'registers / deletes, by RPA, the destinations of each Waiting part in GTOPAS (Inactive: all rows). '
                              'XD07 IF Cross Dock Master to AP POLE sends, per Active part,')]),
                   ('XD05', [("so the next [Sync] sends it to AP POLE with CROSSDOCK_FLAG 'N' (decided 19-Oct); GTOPAS is not changed for it (refer XD06, decided 30-Oct).",
                              "so the next [Sync] deletes all its rows in GTOPAS (XD06); AP POLE is not changed for it (decided 30-Oct).")])):
    s = load(fid)
    for old, new in pairs:
        s = replace_text(s, old, new)
    save(fid, s)
