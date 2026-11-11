"""11-Nov (2): XD06 is an RPA process only (no IF / input file). The bot reads the Active part + destination list of NSP from the DB,
reads the whole Crossdock Master of GTOPAS (WVJA5204, menu Supply > Master > Crossdock Master), registers the rows missing in GTOPAS,
skips the rows that exist and deletes the GTOPAS rows that are not in NSP. Try-catch: one error -> the whole run fails."""
import glob, json

KEY = 'P/No. (without "-") + Destination Code'


def load(f):
    with open(f) as fh:
        return json.load(fh)


def save(f, s):
    with open(f, 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', f)


f = 'XD06_spec.json'
s = load(f)
g = s['general']
g['objective'] = [
    'To keep the Crossdock Master of GTOPAS equal to NSP by an RPA process (no interface file, decided 11-Nov): the bot reads the Active parts and their destinations of the ongoing period directly from the NSP database and maintains GTOPAS screen Crossdock Master (WVJA5204, menu Supply > Master > Crossdock Master).',
    'Per part + destination: in NSP (Active) and not in GTOPAS -> registered; in both -> skipped (no change); in GTOPAS and not in NSP -> deleted. Parts that became Inactive are no longer in the NSP list, so their rows in GTOPAS are deleted.',
    'Only the part + destination list is maintained; Pcs/Case, Max Case/Day, Effective Start Date and Case/Day are not sent (GTOPAS keeps no Case/Day).',
    'The bot runs with try-catch: any error stops the run and the whole run is Failed (one fails, all fail). The result is kept per part in TB_R_CROSSDOCK_IF_RESULT and, together with XD07 (AP POLE), gives the overall Sync Status on XD01.']
g['operation_flow']['flow'] = {'direction': 'TB', 'nodes': [
    {'id': 'a', 'label': '[Sync] on XD01', 'type': 'event'},
    {'id': 'b', 'label': 'RPA: read Active part + destination list from NSP DB', 'type': 'process'},
    {'id': 'c', 'label': 'RPA: open GTOPAS Crossdock Master, read all rows', 'type': 'process'},
    {'id': 'd', 'label': 'Compare: register missing / skip existing / delete not in NSP', 'type': 'process'},
    {'id': 'e', 'label': 'Any error?', 'type': 'decision'},
    {'id': 'f', 'label': 'Success: all Waiting parts GTOPAS OK, Log', 'type': 'process'},
    {'id': 'h', 'label': 'Failed (try-catch): all Waiting parts GTOPAS Failed, Log', 'type': 'process'}],
    'edges': [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'}, {'from': 'd', 'to': 'e'},
              {'from': 'e', 'to': 'f', 'label': 'No'}, {'from': 'e', 'to': 'h', 'label': 'Yes'}]}
g['inputs'] = [
    {'name': 'TB_M_PART_CANDIDATE', 'type': 'DB', 'description': 'Read by the bot: parts with PART_STATUS = Active; CHANGED_DT'},
    {'name': 'TB_M_PART_CANDIDATE_DEST', 'type': 'DB', 'description': 'Read by the bot: DEST_CODE of the ongoing period of the Active parts'},
    {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Parts Waiting for 'GTOPAS' (IF_STATUS = '3'), set by [Sync] on XD01"},
    {'name': 'GTOPAS Crossdock Master (WVJA5204)', 'type': 'System', 'description': 'All rows of Depot Code 01 (one row per part + destination), read by the bot page by page'}]
g['outputs'] = [
    {'name': 'GTOPAS Crossdock Master (WVJA5204)', 'type': 'System', 'description': 'Rows registered / deleted by the bot (not in NSP scope)'},
    {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Result of 'GTOPAS' per Waiting part (1 / 2), run ID, message"},
    {'name': 'TB_M_PART_CANDIDATE', 'type': 'DB', 'description': 'Overall SYNC_STATUS, SYNC_DT, SYNC_MESSAGE of the part'},
    {'name': 'TB_H_PART_CANDIDATE', 'type': 'DB', 'description': 'History record per part (event SYNC, source RPA)'},
    {'name': 'Log', 'type': 'DB', 'description': 'Start, counts (registered / skipped / deleted), error and end messages'}]
g['extra_tables'] = [
    {'title': 'Parameters', 'columns': [{'title': 'Name', 'width': 14}, {'title': 'Description', 'width': 34}],
     'rows': [['Target system', "'GTOPAS'"],
              ['Method', 'RPA bot only (no interface file); reads the NSP database and works on GTOPAS screen Crossdock Master (decided 11-Nov)'],
              ['User', 'RPA bot user (NSP database read, GTOPAS login)'],
              ['Depot Code', "'01' (mandatory search condition of the GTOPAS screen)"],
              ['Compare key', KEY]]},
    {'title': 'GTOPAS Screen Crossdock Master (WVJA5204)', 'columns': [{'title': 'Item', 'width': 16}, {'title': 'Use by the bot', 'width': 32}],
     'rows': [['Menu', 'Supply > Master > Crossdock Master'],
              ['Search: Depot Code (*)', "'01'"],
              ['Search: P/No., Destination Code, Maker Code, Dom/Os, TOPAS Order Type, Trans Code', 'Blank to read all rows; P/No. + Destination Code to find one row'],
              ['[Search] / [NextPage]', 'Read all pages of the list'],
              ['List columns', 'No, MT, R, Depot Code, Maker Code, P/No. (e.g. 52119-BZV60), Domestic/Overseas, Destination Code, TOPAS Order Type, Order Transportation Code'],
              ['MT (maintenance type)', "'DEL' on a row = delete; register = new row (values TBC, see 4.4)"],
              ['Message', "MZD34006FEI: Registration completed. Any other error message = error (try-catch)"]]}]

s['func_flow'] = {'flow': {'direction': 'TB', 'nodes': [
    {'id': 'p1', 'label': 'Start ([Sync] on XD01)', 'type': 'process', 'step': 1},
    {'id': 'm', 'label': 'TB_M_PART_CANDIDATE / TB_M_PART_CANDIDATE_DEST', 'type': 'db', 'lane': 'input'},
    {'id': 'p2', 'label': 'RPA: read NSP list (Active part + destination)', 'type': 'process', 'step': 2},
    {'id': 'gi', 'label': 'GTOPAS Crossdock Master', 'type': 'db', 'lane': 'input'},
    {'id': 'p3', 'label': 'RPA: read all GTOPAS rows', 'type': 'process', 'step': 3},
    {'id': 'p4', 'label': 'Compare: register / skip', 'type': 'process', 'step': 4},
    {'id': 'p5', 'label': 'Delete GTOPAS rows not in NSP', 'type': 'process', 'step': 5},
    {'id': 'go', 'label': 'GTOPAS Crossdock Master', 'type': 'db', 'lane': 'output'},
    {'id': 'd', 'label': 'Any error (try-catch)?', 'type': 'decision', 'step': 6},
    {'id': 'p7', 'label': 'Status per part, overall Sync Status, history', 'type': 'process', 'step': 7},
    {'id': 'o', 'label': 'TB_R_CROSSDOCK_IF_RESULT / TB_M_PART_CANDIDATE / TB_H_PART_CANDIDATE', 'type': 'db', 'lane': 'output'},
    {'id': 'p8', 'label': 'Log end, exit', 'type': 'process', 'step': 8},
    {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
    'edges': [{'from': 'p1', 'to': 'p2'}, {'from': 'm', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'gi', 'to': 'p3'},
              {'from': 'p3', 'to': 'p4'}, {'from': 'p4', 'to': 'p5'}, {'from': 'p4', 'to': 'go'}, {'from': 'p5', 'to': 'go'},
              {'from': 'p5', 'to': 'd'}, {'from': 'd', 'to': 'p7', 'label': 'No / Yes'}, {'from': 'p7', 'to': 'o'},
              {'from': 'p7', 'to': 'p8'}, {'from': 'p8', 'to': 'log'}]},
    'steps': [
        "[Sync] on XD01 sets the parts to Waiting (SYNC_STATUS = '3', IF_STATUS = '3' for 'GTOPAS' and 'APPOLE' in TB_R_CROSSDOCK_IF_RESULT) and starts the RPA bot. Write LOG1. The whole bot run is inside one try-catch (step 6).",
        {'text': 'The bot reads the NSP list from the database: every part with PART_STATUS = Active and its DEST_CODE of the ongoing period (TB_M_PART_CANDIDATE_DEST).',
         'children': ['One record per part + destination. Candidate and Inactive parts are not in the list. Keep CHANGED_DT of the Waiting parts.']},
        {'text': 'The bot opens GTOPAS menu Supply > Master > Crossdock Master (WVJA5204), enters Depot Code 01 (other conditions blank), clicks [Search] and reads every page ([NextPage]).',
         'children': ['GTOPAS list = one row per P/No. + Destination Code. P/No. is shown with "-" (52119-BZV60): the bot removes "-" before comparing (52119BZV60).']},
        {'text': 'Compare per ' + KEY + ':',
         'children': ['In NSP and in GTOPAS: skip (no change).',
                      'In NSP and not in GTOPAS: register the row on the screen (Depot Code 01, P/No., Destination Code and the other values of 4.4); message MZD34006FEI = done.']},
        {'text': 'In GTOPAS and not in NSP: delete the row (MT = DEL); message MZD34006FEI = done.',
         'children': ['This covers destinations removed in NSP, parts that became Inactive (all their rows) and Active parts without destination.']},
        {'text': 'Try-catch: any error (login, screen not available, timeout, error message instead of MZD34006FEI, NSP database not available) stops the bot at once.',
         'children': ['The whole run is Failed (one fails, all fail): LOG4 with the step and the row of the error. The rows already registered / deleted before the error stay in GTOPAS (no rollback on the screen); the next [Sync] compares again and completes them.']},
        {'text': "Set the result of every Waiting part for 'GTOPAS' in TB_R_CROSSDOCK_IF_RESULT and the overall Sync Status:",
         'children': ["No error: IF_STATUS = '1', IF_MESSAGE = 'registered <n>, deleted <n>' of the part. Error: IF_STATUS = '2' for every Waiting part, IF_MESSAGE = error of LOG4.",
                      "TB_M_PART_CANDIDATE: CHANGED_DT changed since step 2 -> '0' (No Sync); else 'GTOPAS' and 'APPOLE' both '1' -> '1' (Success), one '2' -> '2' (Failed), one still '3' -> stays '3'. SYNC_DT = now when 1 or 2.",
                      "Insert TB_H_PART_CANDIDATE: event SYNC, source RPA, FIELD_NAME SYNC_STATUS, REMARK = 'GTOPAS: ' + IF_MESSAGE."]},
        'Write LOG2 with the counts (NSP rows, GTOPAS rows, registered, skipped, deleted) and the status. Exit.']}

bl = s['data_map']['blocks']
reg = {'source': {'table': 'TB_M_PART_CANDIDATE + TB_M_PART_CANDIDATE_DEST (read by the bot)',
                  'keys': [{'field': 'PART_STATUS', 'value': 'Active'}, {'field': 'PERIOD', 'value': 'Ongoing period'}]},
       'destination': {'table': 'GTOPAS Crossdock Master (WVJA5204, by RPA)', 'operation': 'Insert',
                       'description': 'Part + destination in NSP and not in GTOPAS (not in NSP scope; done on the screen)',
                       'keys': [{'field': 'P/No. + Destination Code', 'value': 'Not found in GTOPAS'}]},
       'mappings': [{'source_field': '-', 'dest_field': 'Depot Code', 'description': "'01'"},
                    {'source_field': 'PART_NO', 'dest_field': 'P/No.', 'description': 'Part number (GTOPAS shows it with "-")'},
                    {'source_field': 'DEST_CODE', 'dest_field': 'Destination Code', 'description': '7-digit destination code (code system TBC, see 4.4)'},
                    {'source_field': '-', 'dest_field': 'Maker Code', 'description': 'TBC (existing rows: A)'},
                    {'source_field': '-', 'dest_field': 'Domestic/Overseas', 'description': 'TBC (existing rows: 2)'},
                    {'source_field': '-', 'dest_field': 'TOPAS Order Type', 'description': 'TBC (existing rows: *)'},
                    {'source_field': '-', 'dest_field': 'Order Transportation Code', 'description': 'TBC (existing rows: 2)'}]}
dele = {'source': {'table': 'GTOPAS Crossdock Master (read by the bot)', 'keys': [{'field': 'Depot Code', 'value': "'01'"}]},
        'destination': {'table': 'GTOPAS Crossdock Master (WVJA5204, by RPA)', 'operation': 'Delete',
                        'description': 'Row in GTOPAS and not in the NSP list (not in NSP scope; MT = DEL on the screen)',
                        'keys': [{'field': 'P/No. + Destination Code', 'value': 'Not in the NSP list (Active part + destination)'}]},
        'mappings': [{'dest_field': 'MT', 'description': "'DEL'"},
                     {'dest_field': 'Row', 'description': 'Deleted: destination removed in NSP, part Inactive (all its rows), Active part without destination, part not in NSP'}]}
s['data_map']['blocks'] = [reg, dele] + bl[2:]

s = json.loads(json.dumps(s, ensure_ascii=False)
               .replace("Dummy table: rows of the parts of the file for 'GTOPAS'", "Rows of the Waiting parts for 'GTOPAS'")
               .replace('Part of the file + \'GTOPAS\'', "Waiting part + 'GTOPAS'")
               .replace('Part of the file (both target rows)', 'Waiting part (both target rows)')
               .replace('Part of the file', 'Waiting part')
               .replace('One record per part of the file', 'One record per Waiting part')
               .replace("'1' RPA OK / '2' input, bot or part error", "'1' run without error / '2' run stopped by an error (try-catch, all parts)")
               .replace('Name of the RPA input file', "RPA run ID (YYYYMMDDHHMMSS); file name only for AP POLE")
               .replace("'added ...; deleted ...' when '1' (Inactive part: 'deleted all <n> rows'); reason when '2'", "'registered <n>, deleted <n>' when '1'; error of the run when '2'")
               .replace("'XD06_IF_GTOPAS'", "'XD06_RPA_GTOPAS'"))
for b in s['data_map']['blocks']:
    if b['destination']['table'] == 'TB_H_PART_CANDIDATE':
        for m in b['mappings']:
            if m['dest_field'] == 'SOURCE':
                m['description'] = "'RPA'"
    if b['destination']['table'] == 'Log':
        for m in b['mappings']:
            if m['dest_field'] == 'MESSAGE':
                m['description'] = 'LOG1 - LOG5'

s['func_desc'] = [
    {'type': 'heading', 'text': '4.1 Business Process'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The D/S team maintains the destinations of each part on XD01 (Mapping per Destination of the ongoing period, created by XD05 process 2 and adjusted by screen or upload XD03). Every change sets the part to No Sync.',
        'The D/S team clicks [Sync] when the changes are complete; the RPA bot makes the Crossdock Master of GTOPAS equal to NSP, and XD07 sends the file to AP POLE.',
        'RPA only (decided 11-Nov): the bot reads the NSP database directly and works on GTOPAS screen Crossdock Master (WVJA5204); no interface or input file is created by NSP.',
        'The bot always compares the whole list (all Active parts of NSP with all rows of GTOPAS Depot 01), not only the Waiting parts, so a run that stopped earlier is completed by the next run.']},
    {'type': 'heading', 'text': '4.2 Comparison Rules'},
    {'type': 'table', 'level': 0, 'row_lines': 'all',
     'columns': [{'title': 'In NSP (Active part + destination, ongoing period)', 'width': 30}, {'title': 'In GTOPAS', 'width': 12}, {'title': 'Action of the bot', 'width': 40}],
     'rows': [['Y', 'Y', 'Skip (no change)'], ['Y', 'N', 'Register the row (Depot 01, P/No., Destination Code, values of 4.4)'],
              ['N', 'Y', 'Delete the row (MT = DEL)'], ['Part Inactive (not in the list)', 'Y', 'All rows of the part are deleted'],
              ['Active part without destination', 'Y', 'All rows of the part are deleted']]},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'Compare key: ' + KEY + '. GTOPAS shows P/No. with "-" (52119-BZV60), NSP without (52119BZV60).',
        'Pcs/Case, Max Case/Day, Effective Start Date and Case/Day are not sent. A change of Case/Day only gives no change in GTOPAS; the part still gets Success.',
        'Example: part 52119BZV60 in NSP with 9722D10, 9811110; in GTOPAS with 9811110, 9618274 -> register 9722D10, skip 9811110, delete 9618274.']},
    {'type': 'heading', 'text': '4.3 Try-Catch and Status'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The whole bot run is in one try-catch. Any error stops the run: login failed, screen not available, timeout, an error message instead of MZD34006FEI, NSP database not available.',
        "One fails, all fail: every Waiting part gets 'GTOPAS' IF_STATUS = '2' (Failed) with the error, and the overall Sync Status Failed; the D/S team clicks [Sync] again.",
        'Rows registered / deleted before the error stay in GTOPAS (the screen has no rollback). The next run compares again, skips them and completes the rest.',
        'A part changed on XD01 or by upload while the bot runs gets SYNC_STATUS = No Sync, so the newer data is sent by the next [Sync].',
        'TB_R_CROSSDOCK_IF_RESULT keeps the result per part and target (GTOPAS by XD06, AP POLE by XD07); the overall Sync Status needs both.']},
    {'type': 'heading', 'text': '4.4 Open Points'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'FB-173: GTOPAS shows Destination Code 9618274; NSP DEST_CODE is buyer code + PD code (e.g. 9618201). Same code system, or a conversion is needed? - TBC.',
        'FB-174: values to register Maker Code, Domestic/Overseas, TOPAS Order Type and Order Transportation Code (existing row: A, 2, *, 2) - fixed values or from a master? - TBC.',
        'FB-176: every GTOPAS row (Depot 01) not in NSP is deleted: at go-live all crossdock parts of GTOPAS must exist in NSP, else they are deleted by the first run - TBC.',
        'RPA design: login user, time limit and screen handling of the bot - detailed in the RPA design.']}]

s['logging_messages'] = [
    {'event': 'Batch start', 'cause': '[Sync] on XD01', 'type': 'Info', 'msg_id': 'LOG1',
     'message': 'RPA cross dock master to GTOPAS started. <n> Waiting part(s).', 'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Batch end', 'cause': 'Bot finishes', 'type': 'Info', 'msg_id': 'LOG2',
     'message': 'RPA cross dock master to GTOPAS ended. NSP rows <n>, GTOPAS rows <g>, registered <a>, skipped <k>, deleted <d>, status <STATUS>.',
     'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Register / delete', 'cause': 'Row registered or deleted on the screen', 'type': 'Info', 'msg_id': 'LOG3',
     'message': '<REGISTER / DELETE> <PART_NO> <DEST_CODE>: <GTOPAS message>.', 'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Error (try-catch)', 'cause': 'Login, screen, timeout, GTOPAS error message or NSP database error', 'type': 'Error',
     'msg_id': 'LOG4', 'message': 'RPA to GTOPAS stopped at <STEP> <PART_NO> <DEST_CODE>: <ERROR_DETAIL>. All Waiting parts Failed.',
     'action': {'system': "Stop the bot. IF_STATUS = 2 for every Waiting part.", 'user': 'Click [Sync] again; contact PIC if it persists.'}},
    {'event': 'Unexpected error', 'cause': 'Any other system error', 'type': 'Critical', 'msg_id': 'LOG5',
     'message': 'Unexpected error: <ERROR_DETAIL>.', 'action': {'system': 'Stop. STATUS = ERROR. All Waiting parts Failed.', 'user': 'User contact PIC'}}]
save(f, s)

# other specs: column description of IF_FILE_NAME
for f in sorted(glob.glob('XD*_spec.json')):
    t = open(f).read()
    n = (t.replace('Name of the interface file (AP POLE) or RPA input file (GTOPAS)', 'Name of the interface file (AP POLE) or RPA run ID (GTOPAS)')
          .replace('SCREEN / UPLOAD / IF / BATCH', 'SCREEN / UPLOAD / IF / RPA / BATCH'))
    if n != t:
        open(f, 'w').write(n)
        print('patched', f)
