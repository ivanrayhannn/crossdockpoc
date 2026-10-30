"""30-Oct: XD06 sends the cross dock master to GTOPAS by RPA, destination list only (decided 30-Oct):
per Active part, a destination in NSP and not in GTOPAS is registered, one in both is ignored, one in GTOPAS and not in NSP
is deleted. Pcs/Case, Max Case/Day, Effective Start Date and Case/Day are not sent (GTOPAS keeps no Case/Day);
Inactive parts are not sent to GTOPAS. Function name unchanged. References in XD01 / XD05 / XD07 aligned."""
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


INPUT = 'XD_CDMASTER_GTOPAS_<YYYYMMDDHHMMSS>.csv'

# ---------- XD06
s = load('XD06')
g = s['general']
g['objective'] = [
    'To keep the cross dock destinations of each part in GTOPAS equal to NSP, by RPA: for every Active part waiting for '
    'synchronisation, the destinations of the ongoing period in Part Mapping per Destination (TB_M_PART_CANDIDATE_DEST) are '
    'compared with the destinations of the part in GTOPAS.',
    'Per destination: in NSP and not in GTOPAS -> registered in GTOPAS; in both -> ignored (no change); in GTOPAS and not in '
    'NSP -> deleted in GTOPAS. Only the destination list is maintained: Pcs/Case, Max Case/Day, Effective Start Date and '
    'Case/Day are not sent (GTOPAS keeps no Case/Day per destination).',
    'Parts that became Inactive are not sent: their destinations in GTOPAS are not changed.',
    'Method: RPA bot on the GTOPAS screen. XD06 prepares the RPA input (part x destination) and receives the result per part; '
    'the status per part is kept in TB_R_CROSSDOCK_IF_RESULT (dummy table) and, together with XD07 (AP POLE), gives the '
    'overall Sync Status shown on the Cross Dock Part Master screen (XD01).']
g['operation_flow'] = {'flow': {'direction': 'TB', 'nodes': [
    {'id': 'a', 'label': '[Sync] on XD01 (Mapping per Destination tab)', 'type': 'event'},
    {'id': 'b', 'label': 'Read Waiting Active parts for GTOPAS', 'type': 'process'},
    {'id': 'c', 'label': 'Create RPA input (part x destination)', 'type': 'process'},
    {'id': 'e', 'label': 'RPA: compare with GTOPAS per part', 'type': 'process'},
    {'id': 't', 'label': 'GTOPAS: register / delete destinations', 'type': 'process'},
    {'id': 'f', 'label': 'Result per part, overall Sync Status, history, Log', 'type': 'process'}],
    'edges': [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'e'},
              {'from': 'e', 'to': 't', 'label': 'RPA'}, {'from': 'e', 'to': 'f'}]}}
g['inputs'] = [
    {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Rows TARGET_SYSTEM = 'GTOPAS' with IF_STATUS = '3' (Waiting), set by [Sync] on XD01"},
    {'name': 'TB_M_PART_CANDIDATE', 'type': 'DB', 'description': 'Part List: PART_NO, PART_STATUS (only Active parts are sent), CHANGED_DT'},
    {'name': 'TB_M_PART_CANDIDATE_DEST', 'type': 'DB', 'description': 'Part Mapping per Destination: PERIOD, DEST_CODE of the ongoing period'},
    {'name': 'GTOPAS: destinations of the part', 'type': 'System', 'description': 'Read by the RPA bot on the GTOPAS screen'}]
g['outputs'] = [
    {'name': 'RPA input', 'type': 'File', 'description': INPUT + ': one record per part x destination (see RPA Input Data)'},
    {'name': 'GTOPAS: destinations of the part', 'type': 'System', 'description': 'Registered / deleted by the RPA bot (not in NSP scope)'},
    {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Dummy table: result of 'GTOPAS' per part (1 / 2), input file name, message"},
    {'name': 'TB_M_PART_CANDIDATE', 'type': 'DB', 'description': 'Overall SYNC_STATUS, SYNC_DT, SYNC_MESSAGE of the part'},
    {'name': 'TB_H_PART_CANDIDATE', 'type': 'DB', 'description': 'History record per part (event SYNC, source IF)'},
    {'name': 'Log', 'type': 'DB', 'description': 'Start, RPA, result and end messages'}]
g['extra_tables'] = [
    {'title': 'Parameters', 'columns': [{'title': 'Name', 'width': 14}, {'title': 'Description', 'width': 34}], 'rows': [
        ['Target system', "'GTOPAS' (GTOPAS)"],
        ['User', 'IF batch user ID (NSP); RPA bot user of GTOPAS'],
        ['Interface method', 'RPA bot on the GTOPAS screen; the screens and steps of the bot are detailed in the RPA design (not in this document).']]},
    {'title': 'RPA Input Data', 'columns': [{'title': 'Field', 'width': 10}, {'title': 'Source', 'width': 13}, {'title': 'Format', 'width': 7},
                                           {'title': 'M', 'width': 2}, {'title': 'Business rule', 'width': 16}], 'rows': [
        ['SEND_ID', 'Generated', 'CHAR(14)', 'Y', 'Run of XD06 (YYYYMMDDHHMMSS); all records of one input have the same SEND_ID'],
        ['PART_NO', 'TB_M_PART_CANDIDATE.PART_NO', 'VARCHAR(TBD)', 'Y', 'Active part with Sync Status Waiting for GTOPAS'],
        ['PERIOD', 'TB_M_PART_CANDIDATE_DEST.PERIOD', 'CHAR(6)', 'Y', 'Ongoing calculation period (YYYYMM)'],
        ['DEST_CODE', 'TB_M_PART_CANDIDATE_DEST.DEST_CODE', 'CHAR(7)', 'N', 'Destination code (buyer code + PD code); one record per destination. '
         'Blank when the part has no destination: the bot deletes all destinations of the part in GTOPAS (TBC)'],
        ['SEND_DT', 'Generated', 'DATETIME', 'Y', 'Date-time the input is created']]},
    {'title': 'RPA Result Data', 'columns': [{'title': 'Field', 'width': 10}, {'title': 'Format', 'width': 7}, {'title': 'Business rule', 'width': 31}], 'rows': [
        ['SEND_ID', 'CHAR(14)', 'SEND_ID of the input'],
        ['PART_NO', 'VARCHAR(TBD)', 'One result per part of the input'],
        ['RESULT', 'CHAR(2)', "'OK' = GTOPAS equal to NSP after the run / 'NG' = not done"],
        ['ADDED', 'VARCHAR(TBD)', 'Destination codes registered in GTOPAS (comma separated; blank when none)'],
        ['DELETED', 'VARCHAR(TBD)', 'Destination codes deleted in GTOPAS (comma separated; blank when none)'],
        ['MESSAGE', 'VARCHAR(255)', "Reason when 'NG' (e.g. part not found in GTOPAS, screen error)"]]}]

f = s['func_flow']
f['flow'] = {'direction': 'TB', 'nodes': [
    {'id': 'p1', 'label': 'Start ([Sync] on XD01)', 'type': 'process', 'step': 1},
    {'id': 'r', 'label': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'db', 'lane': 'input'},
    {'id': 'p2', 'label': 'Select Waiting parts for GTOPAS (Inactive: not sent)', 'type': 'process', 'step': 2},
    {'id': 'm', 'label': 'TB_M_PART_CANDIDATE / TB_M_PART_CANDIDATE_DEST', 'type': 'db', 'lane': 'input'},
    {'id': 'p3', 'label': 'Create RPA input', 'type': 'process', 'step': 3},
    {'id': 'x', 'label': 'RPA input', 'type': 'file', 'lane': 'output'},
    {'id': 'p4', 'label': 'RPA: register / ignore / delete per destination in GTOPAS', 'type': 'process', 'step': 4},
    {'id': 'd', 'label': 'Result OK?', 'type': 'decision', 'step': 5},
    {'id': 'p6', 'label': 'Status per part, overall Sync Status, history', 'type': 'process', 'step': 6},
    {'id': 'o', 'label': 'TB_R_CROSSDOCK_IF_RESULT / TB_M_PART_CANDIDATE / TB_H_PART_CANDIDATE', 'type': 'db', 'lane': 'output'},
    {'id': 'p7', 'label': 'Log end, exit', 'type': 'process', 'step': 7},
    {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
    'edges': [{'from': 'p1', 'to': 'p2'}, {'from': 'r', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'm', 'to': 'p3'},
              {'from': 'p3', 'to': 'x'}, {'from': 'p3', 'to': 'p4'}, {'from': 'p4', 'to': 'd'},
              {'from': 'd', 'to': 'p6', 'label': 'Yes / No'}, {'from': 'p6', 'to': 'o'}, {'from': 'p6', 'to': 'p7'}, {'from': 'p7', 'to': 'log'}]}
f['steps'] = [
    "[Sync] on XD01 sets the parts to Waiting (SYNC_STATUS = '3' in TB_M_PART_CANDIDATE, IF_STATUS = '3' for 'GTOPAS' and 'APPOLE' "
    'in TB_R_CROSSDOCK_IF_RESULT) and starts XD06. Write LOG1.',
    {'text': "Select the parts with TARGET_SYSTEM = 'GTOPAS' and IF_STATUS = '3' in TB_R_CROSSDOCK_IF_RESULT. Keep CHANGED_DT of each part.",
     'children': ["PART_STATUS Active: sent to the RPA (step 3).",
                  "PART_STATUS Inactive: not sent; IF_STATUS = '1', IF_MESSAGE = 'Inactive part: GTOPAS not changed' (step 6).",
                  'No Active part: go to step 6.']},
    {'text': f'Create the RPA input {INPUT} (see RPA Input Data):',
     'children': ['Per Active part, one record per destination of the ongoing period in TB_M_PART_CANDIDATE_DEST (PART_NO, PERIOD, DEST_CODE).',
                  'A part without destination: one record with DEST_CODE blank.',
                  'Same SEND_ID and SEND_DT on every record. Error: LOG3, all parts of the run Failed (step 6).']},
    {'text': 'Start the RPA bot with the input. Per part the bot opens the part in GTOPAS, reads its destinations and compares them with the input by DEST_CODE:',
     'children': ['In the input and not in GTOPAS: register the destination in GTOPAS.',
                  'In the input and in GTOPAS: ignore (no change).',
                  'In GTOPAS and not in the input: delete the destination in GTOPAS.',
                  'The bot returns one result per part (see RPA Result Data). Part NG: LOG6. Bot not available or no result within the time limit: LOG4, all parts of the run Failed.']},
    {'text': 'Set the status of every part of the run in TB_R_CROSSDOCK_IF_RESULT:',
     'children': ["RESULT 'OK': IF_STATUS = '1', IF_DT = now, IF_FILE_NAME = input file name, IF_MESSAGE = 'added <ADDED>; deleted <DELETED>' (blank when nothing changed).",
                  "RESULT 'NG', input or bot error: IF_STATUS = '2', IF_DT = now, IF_MESSAGE = reason (LOG3 / LOG4 / LOG6)."]},
    s['func_flow']['steps'][5],
    'Write LOG2 with the input file name and the number of parts sent, destinations added / deleted and parts failed. Exit.']
f['steps'][5] = replace_text(f['steps'][5], "'GTOPAS: ' + result / message", "'GTOPAS: ' + IF_MESSAGE")

dm = s['data_map']['blocks']
dm[0] = {'source': {'table': 'TB_M_PART_CANDIDATE + TB_M_PART_CANDIDATE_DEST',
                    'keys': [{'field': 'PART_NO', 'value': 'Waiting part'}, {'field': 'PART_STATUS', 'value': 'Active'},
                             {'field': 'PERIOD', 'value': 'Ongoing period'}]},
         'destination': {'table': 'RPA input', 'operation': 'Insert', 'description': 'One record per part x destination'},
         'mappings': [{'source_field': '-', 'dest_field': 'SEND_ID', 'description': 'Run of XD06 (YYYYMMDDHHMMSS); same on every record'},
                      {'source_field': 'PART_NO', 'dest_field': 'PART_NO', 'description': 'Same value'},
                      {'source_field': 'PERIOD', 'dest_field': 'PERIOD', 'description': 'Same value'},
                      {'source_field': 'DEST_CODE', 'dest_field': 'DEST_CODE', 'description': 'Same value; blank when the part has no destination'},
                      {'source_field': '-', 'dest_field': 'SEND_DT', 'description': 'Date-time the input is created'}]}
dm.insert(1, {'source': {'table': 'RPA input', 'keys': [{'field': 'PART_NO', 'value': 'Part of the input'}]},
              'destination': {'table': 'GTOPAS - destinations of the part (by RPA)', 'operation': 'Insert / Delete',
                              'description': 'Not in NSP scope; done by the RPA bot', 'keys': [{'field': 'PART_NO + DEST_CODE', 'value': 'Part + destination'}]},
              'mappings': [{'source_field': 'PART_NO', 'dest_field': 'PART_NO', 'description': 'Part of the input'},
                           {'source_field': 'DEST_CODE', 'dest_field': 'DEST_CODE', 'description': 'Registered when in the input and not in GTOPAS'},
                           {'dest_field': '', 'description': 'No change when in the input and in GTOPAS'},
                           {'dest_field': '', 'description': 'Deleted when in GTOPAS and not in the input'}]})
for b in dm:
    if b['destination'].get('table') == 'TB_R_CROSSDOCK_IF_RESULT':
        for m in b['mappings']:
            m['description'] = {'IF_STATUS': "'1' RPA OK or Inactive part (not sent) / '2' input, bot or part error",
                                'IF_FILE_NAME': 'Name of the RPA input file',
                                'IF_MESSAGE': "'added ...; deleted ...' when '1' ('Inactive part: GTOPAS not changed' for an Inactive part); reason when '2'"
                                }.get(m['dest_field'], m['description'])
    if b['destination'].get('table') == 'TB_H_PART_CANDIDATE':
        for m in b['mappings']:
            if m['dest_field'] == 'REMARK':
                m['description'] = "'GTOPAS: ' + IF_MESSAGE"

s['func_desc'] = [
    {'type': 'heading', 'text': '4.1 Business Process'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The D/S team maintains the destinations of each part on XD01 (Mapping per Destination of the ongoing period, created by XD05 '
        'process 2 and adjusted by screen or upload XD03).',
        'Every change sets the part to No Sync. The D/S team clicks [Sync] when the changes are complete; only Active parts are sent to GTOPAS.',
        'GTOPAS keeps the list of cross dock destinations per part (no Case/Day). The RPA bot makes this list equal to NSP: '
        'register a missing destination, ignore an existing one, delete one that is no longer in NSP.']},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'Method: RPA bot on the GTOPAS screen (decided 30-Oct); screens and steps of the bot are detailed in the RPA design.',
        "Parts that became Inactive (XD05 process 1) are not sent to GTOPAS and their destinations in GTOPAS are not changed (decided 30-Oct); "
        "their 'GTOPAS' row is set to '1', so the overall Sync Status follows XD07 (AP POLE)."]},
    {'type': 'heading', 'text': '4.2 Comparison Rules'},
    {'type': 'table', 'level': 0, 'row_lines': 'all', 'columns': [{'title': 'In NSP', 'width': 6, 'align': 'center'},
                                                                   {'title': 'In GTOPAS', 'width': 6, 'align': 'center'},
                                                                   {'title': 'Action of the bot', 'width': 30}],
     'rows': [['Y', 'N', 'Register the destination in GTOPAS'], ['Y', 'Y', 'Ignore (no change)'], ['N', 'Y', 'Delete the destination in GTOPAS']]},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'Compared per part by DEST_CODE; PERIOD is always the ongoing period, past periods are never sent.',
        'Pcs/Case, Max Case/Day, Effective Start Date and Case/Day are not sent. A change of Case/Day only gives no change in GTOPAS; '
        "the part still gets RESULT 'OK' (Success).",
        'An Active part without destination: all its destinations in GTOPAS are deleted (TBC).']},
    {'type': 'heading', 'text': '4.3 Status and Dummy Table'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'TB_R_CROSSDOCK_IF_RESULT is a dummy table that keeps the result per part and target; the real output of XD06 is the change made by the bot in GTOPAS.',
        'Overall SYNC_STATUS: Waiting while a target is Waiting, Success when both targets are done, Failed when one target failed '
        '(the next [Sync] sends the part again; the comparison is repeatable, a part without difference gives no change).',
        'A part changed on XD01 or by upload while it is being sent gets SYNC_STATUS = No Sync, so the newer data is sent by the next [Sync].']},
    {'type': 'heading', 'text': '4.4 Open Points'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'RPA design: GTOPAS screens, start of the bot by XD06, time limit, and how the result is returned (file or table) - TBC.',
        'Active part without destination: delete all its destinations in GTOPAS - TBC.']}]

logs = s['logging_messages']
logs[0]['message'] = 'RPA cross dock destinations to GTOPAS started. <n> part(s).'
logs[1]['message'] = 'RPA cross dock destinations to GTOPAS ended. Input <FILE_NAME>, parts <n>, added <a>, deleted <d>, failed <f>, status <STATUS>.'
logs[2].update(event='Create input', cause='RPA input cannot be created', message='Cannot create the RPA input to GTOPAS: <ERROR_DETAIL>.')
logs[3].update(event='RPA run', cause='RPA bot not available / no result within the time limit',
               message='RPA run of <SEND_ID> to GTOPAS failed: <ERROR_DETAIL>.')
logs[3]['action'] = dict(logs[3]['action'], system='All parts of the run IF_STATUS = 2. Keep the input file.')
if not any(m.get('msg_id') == 'LOG6' for m in logs):
    logs.append({'event': 'RPA result', 'cause': "The bot returns RESULT 'NG' for a part", 'type': 'Error', 'msg_id': 'LOG6',
                 'message': 'GTOPAS not updated for part <PART_NO>: <MESSAGE>.',
                 'action': {'system': 'IF_STATUS = 2 for the part; other parts continue.', 'user': 'Click [Sync] again; contact PIC if it persists'}})
for t in s['tables']:
    t.update(replace_text({k: v for k, v in t.items() if k != 'name'}, 'GTOPAS: existing interface', 'GTOPAS: RPA'))
    t.update(replace_text({k: v for k, v in t.items() if k != 'name'}, 'or send ID (GTOPAS)', 'or RPA input file (GTOPAS)'))
save('XD06', s)

# ---------- references
XD01 = [("Inactive parts are sent with CROSSDOCK_FLAG 'N' so GTOPAS and AP POLE change their status to inactive.",
         "Inactive parts are sent to AP POLE with CROSSDOCK_FLAG 'N'; GTOPAS is not changed for them (refer XD06)."),
        ('XD06 IF Cross Dock Master to GTOPAS and XD07 IF Cross Dock Master to AP POLE each send, per Waiting part, Pcs/Case and Max '
         'Case/Day (TB_M_PART_CANDIDATE) and all destinations with Case/Day of the ongoing period (TB_M_PART_CANDIDATE_DEST) as one complete set.',
         'XD06 IF Cross Dock Master to GTOPAS registers / deletes, by RPA, the destinations of each Waiting Active part in GTOPAS '
         '(destination list only; no Case/Day). XD07 IF Cross Dock Master to AP POLE sends Pcs/Case, Max Case/Day and all destinations '
         'with Case/Day of the ongoing period as one complete set.'),
        ('Each function creates an interface file and sends it by SFTP to its target; the send status',
         'XD06 hands the part x destination list to the RPA bot; XD07 sends a file by SFTP. The result'),
        ('Interface method: file by SFTP to GTOPAS (XD06) and AP POLE (XD07);', 'Interface method: RPA to GTOPAS (XD06), file by SFTP to AP POLE (XD07);'),
        ('Both XD06 (GTOPAS) and XD07 (AP POLE) sent Pcs/Case, Max Case/Day and the destination mapping of the ongoing period.',
         'XD06 updated the destinations in GTOPAS and XD07 sent the cross dock master to AP POLE (ongoing period).'),
        ('GTOPAS: existing interface', 'GTOPAS: RPA'), ('or send ID (GTOPAS)', 'or RPA input file (GTOPAS)')]
for fid, pairs in (('XD01', XD01),
                   ('XD05', [("so the next [Sync] sends it to GTOPAS and AP POLE with CROSSDOCK_FLAG 'N' (decided 19-Oct).",
                              "so the next [Sync] sends it to AP POLE with CROSSDOCK_FLAG 'N' (decided 19-Oct); GTOPAS is not changed for it (refer XD06, decided 30-Oct).")]),
                   ('XD07', [('GTOPAS: existing interface', 'GTOPAS: RPA'), ('or send ID (GTOPAS)', 'or RPA input file (GTOPAS)')])):
    s = load(fid)
    for old, new in pairs:
        s = replace_text(s, old, new)
    save(fid, s)
