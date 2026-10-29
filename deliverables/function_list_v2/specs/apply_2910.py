"""29-Oct: mapping of a part is saved per destination (update / insert / delete) instead of delete-all + insert
(FB-084 / FB-085), in XD03 (upload) and XD01 (Edit mapping [Save]). CREATED_BY / CREATED_DT of a kept destination stay."""
import json

RET = ('Retention: 24 months, counted from the later of CREATED_DT and the Effective Start Date of the part; '
       'a monthly housekeeping job deletes older records (period configurable in system master; job TBC).')
COMPARE = ('compared with {src} by destination code (key PART_NO + PERIOD + DEST_CODE): a destination in both with a different '
           'Case/Day is updated (CASE_DAY, CHANGED_BY, CHANGED_DT; CREATED_BY / CREATED_DT are kept), a destination only in {src2} '
           'is inserted, a destination only in the table is deleted, and a destination with the same Case/Day is not touched. '
           'All changes are saved in one transaction.')


def dest_blocks(src, keys_src, desc, src_fields, who):
    """Update / Insert / Delete blocks of TB_M_PART_CANDIDATE_DEST for one save."""
    pf, df, cf = src_fields
    k = lambda dest_val: [{'field': 'PART_NO', 'value': keys_src}, {'field': 'PERIOD', 'value': 'Ongoing period'},
                          {'field': 'DEST_CODE', 'value': dest_val}]
    upd = {'source': src, 'destination': {'table': 'TB_M_PART_CANDIDATE_DEST', 'operation': 'Update',
                                          'description': f'{desc} - Case/Day changed', 'keys': k('In both, Case/Day differs')},
           'mappings': [{'source_field': cf, 'dest_field': 'CASE_DAY'},
                        {'dest_field': 'CHANGED_BY', 'description': who},
                        {'dest_field': 'CHANGED_DT', 'description': 'Server system date and time'},
                        {'dest_field': 'CREATED_BY', 'description': 'Not changed'},
                        {'dest_field': 'CREATED_DT', 'description': 'Not changed'}]}
    ins = {'source': src, 'destination': {'table': 'TB_M_PART_CANDIDATE_DEST', 'operation': 'Insert',
                                          'description': f'{desc} - new destination'},
           'mappings': [{'source_field': pf, 'dest_field': 'PART_NO'},
                        {'dest_field': 'PERIOD', 'description': 'Ongoing calculation period'},
                        {'source_field': df, 'dest_field': 'DEST_CODE', 'description': 'Destination not yet in the table for the part and period'},
                        {'source_field': cf, 'dest_field': 'CASE_DAY'},
                        {'dest_field': 'CREATED_BY', 'description': who},
                        {'dest_field': 'CREATED_DT', 'description': 'Server system date and time'},
                        {'dest_field': 'CHANGED_BY', 'description': 'Same as CREATED_BY'},
                        {'dest_field': 'CHANGED_DT', 'description': 'Server system date and time'}]}
    dele = {'source': {'table': 'TB_M_PART_CANDIDATE_DEST', 'keys': k('Not in the ' + ('file' if 'Excel' in str(src) else 'panel'))},
            'destination': {'table': 'TB_M_PART_CANDIDATE_DEST', 'operation': 'Delete',
                            'description': f'{desc} - removed destination', 'keys': k('Not in the ' + ('file' if 'Excel' in str(src) else 'panel'))},
            'mappings': [{'dest_field': f, 'description': 'Row is deleted'} for f in
                         ('PART_NO', 'PERIOD', 'DEST_CODE', 'CASE_DAY')]}
    return [upd, ins, dele]


def is_dest(b, op):
    d = b['destination']
    return d.get('table') == 'TB_M_PART_CANDIDATE_DEST' and d.get('operation') == op


def replace_blocks(blocks, new):
    i = next(n for n, b in enumerate(blocks) if is_dest(b, 'Delete') or is_dest(b, 'Update'))
    rest = [b for b in blocks if b['destination'].get('table') != 'TB_M_PART_CANDIDATE_DEST']
    return rest[:i] + new + rest[i:]


# ---------- XD03 upload batch
with open('XD03_spec.json') as f:
    s = json.load(f)
src = s['data_map']['blocks'][[b['destination'].get('operation') for b in s['data_map']['blocks']].index('Insert')]['source'] \
    if any(is_dest(b, 'Insert') for b in s['data_map']['blocks']) else None
s['data_map']['blocks'] = replace_blocks(s['data_map']['blocks'], dest_blocks(
    src, 'Changed part', 'Changed part', ('part_no', 'dest_code', 'case_day'), 'Login name of the user who uploaded'))
g = s['general']
for n in g['operation_flow']['flow']['nodes'] + s['func_flow']['flow']['nodes']:
    n['label'] = n['label'].replace('Replace mapping of changed parts', 'Update / insert / delete mapping of changed parts')
g['outputs'][0]['description'] = 'if successful: mapping of each changed part updated per destination (ongoing period)'
s['func_flow']['steps'][5]['children'][1] = ('Otherwise: update / insert / delete the destinations of the part so that its mapping '
                                             'matches the rows of the file, and set Sync Status = No Sync.')
for b in s['data_map']['blocks']:
    for m in b['mappings']:
        if m.get('description') == 'Parts whose mapping was replaced':
            m['description'] = 'Parts whose mapping was changed'
s['func_desc'][0]['text'] = s['func_desc'][0]['text'].replace('replaces the mapping', 'updates the mapping')
s['func_desc'][7]['items'][2] = 'For a changed part, its rows of the ongoing period in TB_M_PART_CANDIDATE_DEST are ' + \
    COMPARE.format(src='the rows of the file', src2='the file')
s['logging_messages'][6]['cause'] = 'Save (update / insert / delete) of TB_M_PART_CANDIDATE_DEST or update of TB_M_PART_CANDIDATE fails'
for r in s['sample_sheet']['sections'][1]['rows']:
    if isinstance(r[7], str):
        r[7] = r[7].replace('Replaced.', 'Changed.').replace(' removed.', ' deleted.').replace(' added.', ' inserted.')
for t in s['tables']:
    if 'Proposed retention' in t.get('description', ''):
        t['description'] = t['description'][:t['description'].index('Proposed retention')] + RET
with open('XD03_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)

# ---------- XD01 Edit mapping [Save]
with open('XD01_spec.json') as f:
    s = json.load(f)
s['data_map']['blocks'] = replace_blocks(s['data_map']['blocks'], dest_blocks(
    'Key-in from screen', 'Edited part', 'Edit mapping - [Save]', ('Part Number', 'Destination (CD)', 'Case/Day'), 'Login user ID'))
for b in s['operation']:
    for i, t in enumerate(b.get('items', [])):
        if isinstance(t, str) and t.startswith('Replace the rows of the part and the ongoing period'):
            b['items'][i] = ('Save the draft per destination in TB_M_PART_CANDIDATE_DEST: update the Case/Day of a '
                             'kept one, insert a new one, delete a removed one (refer Data Edit Mapping).')
        elif isinstance(t, str) and 'gets its whole mapping replaced' in t:
            b['items'][i] = t.replace('gets its whole mapping replaced',
                                      'gets its mapping updated per destination (refer XD03)')
for m in s['logging_messages']:
    if m.get('cause') == 'Database error on replace of TB_M_PART_CANDIDATE_DEST':
        m['cause'] = 'Database error on save of TB_M_PART_CANDIDATE_DEST'
for t in s.get('tables', []):
    if 'Proposed retention' in t.get('description', ''):
        t['description'] = t['description'][:t['description'].index('Proposed retention')] + RET
with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
