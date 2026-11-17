"""17-Nov (2): XD07 is an RPA process on the AP POLE web screens (from Crossdock_ap_pole_guide.xlsx), no SFTP interface file.
Part level: WLM9Q890 Cross Dock Kanban Part Master (Add / Edit / Delete). Destination level: WLM9Q860 Export Customer Cross Dock
Master (opened with [Maintain Cross Dock]). Source: the XD01 Export Excel files (Part List, Mapping per Destination, sheet Active to
Inactive), parts that are not synced yet. Alternative: Common File Upload WLM98010 (LM9Q900 / LM9Q870). Runs after apply_1711."""
import json

INITIAL = {'revision': '0.1', 'author': 'FID Rayhan', 'date': '18-Oct-26', 'reviewed_by': '', 'description': 'Initial Draft'}
GUIDE = 'deliverables/user_guide/Crossdock_User_Guide_AP_POLE.xlsx'


def load(f):
    with open(f) as fh:
        return json.load(fh)


def save(f, s):
    with open(f, 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', f)


f = 'XD07_spec.json'
s = load(f)
s['header']['function_name'] = 'XD07 RPA Cross Dock Master to AP POLE'
g = s['general']
g['objective'] = [
    'To make the cross dock master of AP POLE equal to NSP by an RPA process on the AP POLE web screens (decided 17-Nov, replaces the SFTP '
    'interface file): part level on WLM9Q890 Cross Dock Kanban Part Master, destination level on WLM9Q860 Export Customer Cross Dock Master.',
    'Source data: the Export Excel files of XD01 (Part List: Status, Part Name, Pcs/Case, Max Case/Day; Mapping per Destination: Period, '
    'Destination Code, Dest Case/Day; sheet Active to Inactive), only the parts not synced yet (Sync Status No Sync / Waiting).',
    'Part level: a part that became Active is added (or edited when AP POLE still has it), an Active part with a new Pcs/Case or Max Case/Day '
    'is edited, a part that went Active -> Inactive is deleted. Destination level: destinations are added, deleted or edited so that AP POLE '
    'has the same Buyer-PD and Max Shipping Box Qty as NSP.',
    'Step by step guide with the AP POLE screens: ' + GUIDE + '.']
g['operation_flow']['flow'] = {'direction': 'TB', 'nodes': [
    {'id': 'a', 'label': '[Sync] on XD01', 'type': 'event'},
    {'id': 'b', 'label': 'RPA: read source (Part List, Mapping, Active to Inactive)', 'type': 'process'},
    {'id': 'c', 'label': 'WLM9Q890: search part, Add / Edit / Delete', 'type': 'process'},
    {'id': 'd', 'label': 'WLM9Q860 ([Maintain Cross Dock]): Add / Delete / Edit destinations', 'type': 'process'},
    {'id': 'e', 'label': 'Any error?', 'type': 'decision'},
    {'id': 'f', 'label': 'Success: APPOLE OK, LAST_SYNC_DT, Log', 'type': 'process'},
    {'id': 'h', 'label': 'Failed (try-catch): APPOLE Failed, Log', 'type': 'process'}],
    'edges': [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'}, {'from': 'd', 'to': 'e'},
              {'from': 'e', 'to': 'f', 'label': 'No'}, {'from': 'e', 'to': 'h', 'label': 'Yes'}]}
g['inputs'] = [
    {'name': 'XD01 Export Excel: Part List', 'type': 'File', 'description': 'Sheet Part List: Part Number, Part Name, Pcs/Case, Max Case/Day, Status, Sync Status'},
    {'name': 'XD01 Export Excel: Mapping per Destination', 'type': 'File', 'description': 'Sheet Mapping per Destination (ongoing period): Part Number, Destination Code, '
     'Dest Case/Day, Sync Status; sheet Active to Inactive: parts to delete'},
    {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Parts Waiting for 'APPOLE' (IF_STATUS = '3'), set by [Sync] on XD01; LAST_SYNC_DT"},
    {'name': 'AP POLE WLM9Q890 / WLM9Q860', 'type': 'System', 'description': 'Current part and destination rows of AP POLE, read by the bot (search per part)'}]
g['outputs'] = [
    {'name': 'AP POLE WLM9Q890 Cross Dock Kanban Part Master', 'type': 'System', 'description': 'Part added / edited / deleted by the bot (not in NSP scope)'},
    {'name': 'AP POLE WLM9Q860 Export Customer Cross Dock Master', 'type': 'System', 'description': 'Buyer-PD rows added / edited / deleted by the bot (not in NSP scope)'},
    {'name': 'TB_R_CROSSDOCK_IF_RESULT', 'type': 'DB', 'description': "Result of 'APPOLE' per Waiting part (1 / 2), run ID, message, LAST_SYNC_DT on Success"},
    {'name': 'TB_M_PART_CANDIDATE', 'type': 'DB', 'description': 'Overall SYNC_STATUS, SYNC_DT, SYNC_MESSAGE of the part'},
    {'name': 'TB_H_PART_CANDIDATE', 'type': 'DB', 'description': 'History record per part (event SYNC, source RPA)'},
    {'name': 'Log', 'type': 'DB', 'description': 'Start, counts (added / edited / deleted per screen), error and end messages'}]
g['extra_tables'] = [
    {'title': 'Parameters', 'columns': [{'title': 'Name', 'width': 14}, {'title': 'Description', 'width': 34}],
     'rows': [['Target system', "'APPOLE' (AP POLE, https://ap-pole.toyota-asia.com/lm9/)"],
              ['Method', 'RPA bot on the AP POLE web screens (decided 17-Nov; no SFTP interface file)'],
              ['User', 'RPA bot user with AP POLE login (Operator ID: TBC)'],
              ['Menu', 'Master Maintenance > Cross Dock Kanban Part Master'],
              ['Effective Month / Year', 'Search: Effective From = first day, To = last day of the month; Add: next month (auto by AP POLE)']]},
    {'title': 'AP POLE WLM9Q890 Cross Dock Kanban Part Master (part level)', 'columns': [{'title': 'AP POLE item', 'width': 18}, {'title': 'NSP source / rule', 'width': 30}],
     'rows': [['Effective Month / Year', 'Auto generated (next month) / auto generated'],
              ['Operator ID', 'TBC (e.g. P5, P6 on the AP POLE screen)'],
              ['Part No.', 'PART_NO (AP POLE shows it with "-", e.g. 52101-BZA40)'],
              ['Part Name', 'PART_NAME'],
              ['Shipping Box Qty', 'PCS_CASE (Pcs/Case)'],
              ['Max Shipping Box Qty', 'MAX_CASE_DAY (Max Case/Day)'],
              ['Max Allowance Qty', 'Calculated by AP POLE = Shipping Box Qty x Max Shipping Box Qty (e.g. 6 x 20 = 120)'],
              ['Buttons', '[Search], [Add], [Edit] (pop up WLM9Q891, [Save]), [Delete], [Maintain Cross Dock] (opens WLM9Q860 for the ticked part)']]},
    {'title': 'AP POLE WLM9Q860 Export Customer Cross Dock Master (destination level)', 'columns': [{'title': 'AP POLE item', 'width': 18}, {'title': 'NSP source / rule', 'width': 30}],
     'rows': [['Buyer-PD', 'DEST_CODE: 5-digit buyer code + "-" + 2-digit PD code (9722D88 -> 9722D-88)'],
              ['Order Type', "'**'"],
              ['Transport Code', "Always '2'"],
              ['Max Shipping Box Qty', 'CASE_DAY of the destination (Dest Case/Day)'],
              ['Max Allowance Qty', 'Calculated by AP POLE = Shipping Box Qty of the part x Max Shipping Box Qty'],
              ['Total Shipping Allocated (Export Supply)', 'Sum of Max Shipping Box Qty of the destinations; may not be more than Max Shipping Box Qty of the part'],
              ['Buttons', '[Add], [Edit], [Delete], [Back]']]}]

s['func_flow'] = {'flow': {'direction': 'TB', 'nodes': [
    {'id': 'p1', 'label': 'Start ([Sync] on XD01)', 'type': 'process', 'step': 1},
    {'id': 'src', 'label': 'XD01 Export Excel (Part List, Mapping, Active to Inactive)', 'type': 'db', 'lane': 'input'},
    {'id': 'p2', 'label': 'RPA: read the parts not synced yet', 'type': 'process', 'step': 2},
    {'id': 'p3', 'label': 'WLM9Q890: search the part', 'type': 'process', 'step': 3},
    {'id': 'p4', 'label': 'Part level: Add / Edit / Delete (4 scenarios)', 'type': 'process', 'step': 4},
    {'id': 'p5', 'label': 'WLM9Q860: destinations Add / Delete / Edit (4 scenarios)', 'type': 'process', 'step': 5},
    {'id': 'ap', 'label': 'AP POLE WLM9Q890 / WLM9Q860', 'type': 'db', 'lane': 'output'},
    {'id': 'd', 'label': 'Any error (try-catch)?', 'type': 'decision', 'step': 6},
    {'id': 'p7', 'label': 'Status per part, LAST_SYNC_DT, overall Sync Status, history', 'type': 'process', 'step': 7},
    {'id': 'o', 'label': 'TB_R_CROSSDOCK_IF_RESULT / TB_M_PART_CANDIDATE / TB_H_PART_CANDIDATE', 'type': 'db', 'lane': 'output'},
    {'id': 'p8', 'label': 'Log end, exit', 'type': 'process', 'step': 8},
    {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
    'edges': [{'from': 'p1', 'to': 'p2'}, {'from': 'src', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'p3', 'to': 'p4'},
              {'from': 'p4', 'to': 'p5'}, {'from': 'p4', 'to': 'ap'}, {'from': 'p5', 'to': 'ap'}, {'from': 'p5', 'to': 'd'},
              {'from': 'd', 'to': 'p7', 'label': 'No / Yes'}, {'from': 'p7', 'to': 'o'}, {'from': 'p7', 'to': 'p8'}, {'from': 'p8', 'to': 'log'}]},
    'steps': [
        "[Sync] on XD01 sets the parts to Waiting (SYNC_STATUS = '3', IF_STATUS = '3' for 'GTOPAS' and 'APPOLE') and starts the RPA bot. Write LOG1. "
        'The whole run is inside one try-catch.',
        {'text': 'The bot reads the source data: the XD01 Export Excel of Part List and of Mapping per Destination (ongoing period).',
         'children': ['Parts to process = Sync Status No Sync / Waiting (not synced since the last change). Part level from Part List (Status, Part Name, '
                      'Pcs/Case, Max Case/Day); destination level from Mapping per Destination (Destination Code, Dest Case/Day); parts to delete '
                      'from sheet Active to Inactive.']},
        {'text': 'AP POLE menu Master Maintenance > Cross Dock Kanban Part Master (WLM9Q890): Effective From = first day, To = last day of the month, '
                 'Part No. = part of the source, [Search].'},
        {'text': 'Part level (4.2): add, edit or delete the part on WLM9Q890.',
         'children': ['Add / Edit: Shipping Box Qty = PCS_CASE, Max Shipping Box Qty = MAX_CASE_DAY, [Save]. Delete: tick the part, [Delete].']},
        {'text': 'Destination level (4.3): tick the part, [Maintain Cross Dock] (opens WLM9Q860), compare the Buyer-PD rows with the NSP destinations '
                 'and add, delete or edit them; [Back].',
         'children': ['Add: Buyer-PD = DEST_CODE (5-2 format), Order Type **, Transport Code 2, Max Shipping Box Qty = Dest Case/Day.',
                      'Total Shipping Allocated may not be more than Max Shipping Box Qty of the part: delete the destinations not in NSP before adding.']},
        {'text': 'Try-catch: any error (login, screen not available, timeout, AP POLE error message, source file not readable) stops the bot at once.',
         'children': ['The whole run is Failed (one fails, all fail): LOG4 with the step, part and destination. Changes made before the error stay in '
                      'AP POLE (no rollback on the screen); the next run compares again and completes the rest.']},
        {'text': "Set the result of every Waiting part for 'APPOLE' in TB_R_CROSSDOCK_IF_RESULT and the overall Sync Status:",
         'children': ["No error: IF_STATUS = '1', IF_DT and LAST_SYNC_DT = now, IF_MESSAGE = 'part <added / edited / deleted>, dest added <n>, "
                      "deleted <n>, edited <n>'. Error: IF_STATUS = '2', IF_DT = now, LAST_SYNC_DT not changed.",
                      "TB_M_PART_CANDIDATE: CHANGED_DT changed since step 2 -> '0' (No Sync); else 'GTOPAS' and 'APPOLE' both '1' -> '1' (Success), "
                      "one '2' -> '2' (Failed), one still '3' -> stays '3'.",
                      "Insert TB_H_PART_CANDIDATE: event SYNC, source RPA, FIELD_NAME SYNC_STATUS, REMARK = 'APPOLE: ' + IF_MESSAGE."]},
        'Write LOG2 with the counts (parts added / edited / deleted, destinations added / deleted / edited) and the status. Exit.']}

bl = s['data_map']['blocks']
part = {'source': {'table': 'XD01 Export Excel Part List (read by the bot)', 'keys': [{'field': 'Sync Status', 'value': 'No Sync / Waiting'}]},
        'destination': {'table': 'AP POLE WLM9Q890 Cross Dock Kanban Part Master (by RPA)', 'operation': 'Insert / Update / Delete',
                        'description': 'Part level, scenarios of 4.2 (not in NSP scope; done on the screen)',
                        'keys': [{'field': 'Part No. + Effective Month / Year', 'value': 'Part of the source, current month'}]},
        'mappings': [{'source_field': '-', 'dest_field': 'Effective Month / Year', 'description': 'Auto generated by AP POLE (next month)'},
                     {'source_field': '-', 'dest_field': 'Operator ID', 'description': 'TBC'},
                     {'source_field': 'PART_NO', 'dest_field': 'Part No.', 'description': 'With "-" as shown by AP POLE'},
                     {'source_field': 'PART_NAME', 'dest_field': 'Part Name'},
                     {'source_field': 'PCS_CASE', 'dest_field': 'Shipping Box Qty'},
                     {'source_field': 'MAX_CASE_DAY', 'dest_field': 'Max Shipping Box Qty'},
                     {'source_field': '-', 'dest_field': 'Max Allowance Qty', 'description': 'Calculated by AP POLE'}]}
dest = {'source': {'table': 'XD01 Export Excel Mapping per Destination (read by the bot)', 'keys': [{'field': 'Period', 'value': 'Ongoing period'}]},
        'destination': {'table': 'AP POLE WLM9Q860 Export Customer Cross Dock Master (by RPA)', 'operation': 'Insert / Update / Delete',
                        'description': 'Destination level, scenarios of 4.3 (not in NSP scope; done on the screen)',
                        'keys': [{'field': 'Part No. + Buyer-PD', 'value': 'Destination of the part'}]},
        'mappings': [{'source_field': 'DEST_CODE', 'dest_field': 'Buyer-PD', 'description': '5-2 format with "-" (9722D88 -> 9722D-88)'},
                     {'source_field': '-', 'dest_field': 'Order Type', 'description': "'**'"},
                     {'source_field': '-', 'dest_field': 'Transport Code', 'description': "Always '2'"},
                     {'source_field': 'CASE_DAY', 'dest_field': 'Max Shipping Box Qty', 'description': 'Dest Case/Day'},
                     {'source_field': '-', 'dest_field': 'Max Allowance Qty', 'description': 'Calculated by AP POLE'}]}
s['data_map']['blocks'] = [part, dest] + bl[1:]

SCEN_PART = [['1', 'Candidate -> Active', 'Search the part; [Add]: Part No., Shipping Box Qty = Pcs/Case, Max Shipping Box Qty = Max Case/Day; [Save]'],
             ['2', 'Inactive -> Active', 'Search the part: not in AP POLE -> [Add]; in AP POLE -> [Edit] Pcs/Case and Max Case/Day'],
             ['3', 'Active -> Inactive', 'Search the part, tick it, [Delete] (source: sheet Active to Inactive)'],
             ['4', 'Active, Pcs/Case or Max Case/Day changed', 'Search the part, [Edit] Shipping Box Qty / Max Shipping Box Qty, [Save]']]
SCEN_DEST = [['1', 'Destination added, Total Shipping Allocated < Max Case/Day', '[Add]: Buyer-PD, Max Shipping Box Qty = Dest Case/Day'],
             ['2', 'Destination added, Total Shipping Allocated = Max Case/Day', 'Compare NSP and AP POLE; [Delete] the Buyer-PD not in NSP first, then [Add] the destinations of NSP not in AP POLE'],
             ['3', 'Destination removed', 'Compare NSP and AP POLE; [Delete] the Buyer-PD not in NSP'],
             ['4', 'Dest Case/Day changed', 'Compare NSP and AP POLE; [Edit] Max Shipping Box Qty to the NSP value']]
s['func_desc'] = [
    {'type': 'heading', 'text': '4.1 Business Process'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The Procurement team maintains the Part List and the D/S team the Mapping per Destination on XD01. Every change sets the part to No Sync.',
        'The D/S team clicks [Sync] when the changes are complete; the RPA bot makes AP POLE equal to NSP (XD07) and GTOPAS (XD06).',
        'RPA on the AP POLE web screens (decided 17-Nov): the SFTP interface file is no longer used. Part level on WLM9Q890, destination level on '
        'WLM9Q860 ([Maintain Cross Dock] of the ticked part).',
        'Source data: the XD01 Export Excel files (Part List, Mapping per Destination, sheet Active to Inactive), parts not synced yet. '
        'Steps with the AP POLE screens: ' + GUIDE + '.']},
    {'type': 'heading', 'text': '4.2 Part Level Scenarios (WLM9Q890 Cross Dock Kanban Part Master)'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'Common steps: Effective From = first day, To = last day of the month; Part No. = part of the source; [Search].']},
    {'type': 'table', 'level': 0, 'row_lines': 'all',
     'columns': [{'title': 'No', 'width': 4}, {'title': 'Status in the source', 'width': 22}, {'title': 'Action of the bot', 'width': 56}], 'rows': SCEN_PART},
    {'type': 'heading', 'text': '4.3 Destination Level Scenarios (WLM9Q860 Export Customer Cross Dock Master)'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'Common steps: search the part on WLM9Q890 (4.2), tick the part, [Maintain Cross Dock].',
        'Total Shipping Allocated (Export Supply) = sum of Max Shipping Box Qty of the destinations; it may not be more than Max Shipping Box Qty of the part.']},
    {'type': 'table', 'level': 0, 'row_lines': 'all',
     'columns': [{'title': 'No', 'width': 4}, {'title': 'Change in the source', 'width': 26}, {'title': 'Action of the bot', 'width': 52}], 'rows': SCEN_DEST},
    {'type': 'heading', 'text': '4.4 Try-Catch and Status'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The whole bot run is in one try-catch. Any error stops the run: login failed, screen not available, timeout, an AP POLE error message, '
        'source file not readable.',
        "One fails, all fail: every Waiting part gets 'APPOLE' IF_STATUS = '2' (Failed) and the overall Sync Status Failed; LAST_SYNC_DT is not changed. "
        'The D/S team clicks [Sync] again.',
        'Changes made before the error stay in AP POLE (no rollback on the screen). The next run compares again and completes the rest.',
        "On Success: IF_STATUS = '1', IF_DT and LAST_SYNC_DT = date-time of the result (used by the sheet Active to Inactive of XD01, 4.3a)."]},
    {'type': 'heading', 'text': '4.5 Alternative: Common File Upload (WLM98010)'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'AP POLE also accepts an upload: Report Type LM9Q900 - Upload Kanban Part Master (columns Effective Month, Effective Year, Operator ID, Part No., '
        'Part Name, Shipping Box Qty, Max Shipping Box Qty, Max Allowance Qty, ...) and LM9Q870 - Upload Export Customer Cross Dock Master (columns '
        'Effective Month, Effective Year, Part No., Buyer-PD, Order Type, Transport Code, Max Shipping Box (RCS), ...).',
        'Whether the bot uses the screens (4.2 / 4.3) or the upload is to be confirmed (refer 4.6).']},
    {'type': 'heading', 'text': '4.6 Open Points'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'Operator ID of the bot on AP POLE (P5, P6 seen on the screen) - TBC.',
        'Screen steps (4.2 / 4.3) or Common File Upload (4.5) - TBC.',
        'Source: XD01 Export Excel downloaded by the D/S team or a direct read of the NSP database (as XD06) - TBC.',
        'Effective Month of a new part: next month (auto by AP POLE); a change for the current month - TBC with the AP POLE team.']}]

s['logging_messages'] = [
    {'event': 'Batch start', 'cause': '[Sync] on XD01', 'type': 'Info', 'msg_id': 'LOG1',
     'message': 'RPA cross dock master to AP POLE started. <n> Waiting part(s).', 'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Batch end', 'cause': 'Bot finishes', 'type': 'Info', 'msg_id': 'LOG2',
     'message': 'RPA cross dock master to AP POLE ended. Parts added <a>, edited <e>, deleted <d>; destinations added <da>, deleted <dd>, edited <de>; status <STATUS>.',
     'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Change done', 'cause': 'Part or destination changed on the screen', 'type': 'Info', 'msg_id': 'LOG3',
     'message': '<ADD / EDIT / DELETE> <PART_NO> <BUYER_PD>: <AP POLE message>.', 'action': {'system': 'Write the log.', 'user': '-'}},
    {'event': 'Error (try-catch)', 'cause': 'Login, screen, timeout, AP POLE error message or source file error', 'type': 'Error', 'msg_id': 'LOG4',
     'message': 'RPA to AP POLE stopped at <STEP> <PART_NO> <BUYER_PD>: <ERROR_DETAIL>. All Waiting parts Failed.',
     'action': {'system': 'Stop the bot. IF_STATUS = 2 for every Waiting part.', 'user': 'Click [Sync] again; contact PIC if it persists.'}},
    {'event': 'Unexpected error', 'cause': 'Any other system error', 'type': 'Critical', 'msg_id': 'LOG5',
     'message': 'Unexpected error: <ERROR_DETAIL>.', 'action': {'system': 'Stop. STATUS = ERROR. All Waiting parts Failed.', 'user': 'User contact PIC'}}]
s['revisions'] = [INITIAL, {'revision': '0.2', 'author': 'FID Rayhan', 'date': '17-Nov-26', 'reviewed_by': '',
                            'description': 'RPA on the AP POLE screens WLM9Q890 / WLM9Q860 instead of the SFTP interface file; source = XD01 Export Excel; '
                                           'part and destination scenarios; LAST_SYNC_DT (from Crossdock_ap_pole_guide.xlsx).'}]
s['header']['updated_date'] = '17-Nov-26'
s['header']['updated_by'] = 'FID Rayhan'
s = json.loads(json.dumps(s, ensure_ascii=False).replace('Interface file to AP POLE (SFTP)', 'AP POLE screens (RPA)')
               .replace('"Name of the interface file"', '"RPA run ID (YYYYMMDDHHMMSS)"')
               .replace("'APPOLE: ' + 'sent <file name>' or IF_MESSAGE", "'APPOLE: ' + IF_MESSAGE"))
save(f, s)

# other specs: XD07 is no longer a file interface
import glob
for f in sorted(glob.glob('XD*_spec.json')):
    t = open(f).read()
    n = (t.replace('and XD07 sends the file to AP POLE', 'and XD07 updates AP POLE by RPA (screens WLM9Q890 / WLM9Q860)')
          .replace('Name of the interface file (AP POLE) or RPA run ID (GTOPAS)', 'RPA run ID (GTOPAS and AP POLE)')
          .replace('in AP POLE (XD07, SFTP file, part level)', 'in AP POLE (XD07, RPA, WLM9Q890 [Delete])')
          .replace('XD07 sends a file by SFTP.', 'XD07 is an RPA on the AP POLE screens WLM9Q890 / WLM9Q860.')
          .replace('file by SFTP to AP POLE (XD07)', 'RPA to AP POLE (XD07, screens WLM9Q890 / WLM9Q860)')
          .replace('The real output is the interface data sent to the target (AP POLE: file by SFTP; GTOPAS: RPA).',
                   'The real output is the change made by the RPA on the target screens (GTOPAS WVJA5204, AP POLE WLM9Q890 / WLM9Q860).'))
    if n != t:
        open(f, 'w').write(n)
        print('patched', f)
