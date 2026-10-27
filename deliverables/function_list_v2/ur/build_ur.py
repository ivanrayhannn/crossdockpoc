"""Build the User Requirement of one function: the same sheets as its UISS (Revision, Gen Desc, Screen Flow, Screen Layout,
Item Desc, Data Map, Operation Desc, Display Message, Logging Message) with business wording for business users.

Source: the UISS spec (deliverables/function_list_v2/specs/<id>_spec.json). Table / column names and status codes are
replaced by business terms (VOCAB), technical item attributes (field, length, format) are left out, and the business
rules / acceptance criteria of ur_<id>.py are added to the Operation Description.
Usage: python3 build_ur.py XD01   -> <id>_UR_<Name>.xlsx (+ <id>_UR_spec.json) in this folder."""
import copy, importlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SPECS = os.path.join(HERE, '..', 'specs')
sys.path.insert(0, HERE)

# technical name -> business term (longest names first when replacing)
VOCAB = {
    'TB_M_PART_CANDIDATE_DEST': 'destination mapping', 'TB_M_PART_CANDIDATE': 'Part List', 'TB_H_PART_CANDIDATE': 'change history',
    'TB_M_PART_MASTER': 'Part Master', 'TB_M_H0125_DESTINATION': 'Destination Master', 'TB_R_CROSSDOCK_IF_RESULT': 'sending result',
    'TB_R_PART_DAD_RESULT': 'calculation result', 'TB_R_ACTUAL_DEMAND_SUMMARY': 'actual demand summary',
    'PART_NO': 'Part No', 'PART_NAME': 'Part Name', 'MIN_MAD': 'Min MAD', 'PCS_CASE': 'Pcs/Case', 'MAX_CASE_DAY': 'Max Case/Day',
    'TOTAL_PCS_DAY': 'Total Pcs/Day', 'CASE_DAY': 'Case/Day', 'EFFECTIVE_START_DATE': 'Effective Start Date', 'PART_STATUS': 'status',
    'SYNC_STATUS': 'Sync Status', 'SYNC_MESSAGE': 'sync message', 'SYNC_DT': 'sync time', 'CHANGED_DT': 'last update time',
    'CHANGED_BY': 'updated by', 'CREATED_DT': 'created time', 'CREATED_BY': 'created by', 'DEST_CODE': 'destination code',
    'DESTINATION_CD': 'destination code', 'DESTINATION_NAME': 'destination name', 'CROSSDOCK_FLAG': 'crossdock flag (Y / N)',
    'IF_STATUS': 'sending status', 'IF_DT': 'sending time', 'IF_FILE_NAME': 'file name', 'IF_MESSAGE': 'sending message',
    'TARGET_SYSTEM': 'target system', 'EVENT_TYPE': 'event', 'FIELD_NAME': 'field', 'OLD_VALUE': 'old value', 'NEW_VALUE': 'new value',
    'HIST_ID': 'history no.', 'UPLOAD_ID': 'upload no.', 'LAST_SOURCE': 'last source', 'LAST_UPLOAD_ID': 'last upload no.',
    'PERIOD': 'period', 'SOURCE': 'source',
}
# technical sentences of the UISS -> business wording (applied after VOCAB)
PHRASES = [
    ('Retrieve all parts of Part List and display them', 'Show all parts of the Part List'),
    ("'Part No' lists parts of Part Master that are not yet registered in Part List, so can not register part into Crossdock master",
     "'Part No' lists the parts of the Part Master that are not yet in the Part List (a part can be registered only once)."),
    ('Insert the part into Part List with', 'Save the part in the Part List with'),
    ('Insert the change history when any register or update data in Part List', 'Record the change in the change history.'),
    ('Insert the change history when any register or update in Part List', 'Record the change in the change history.'),
    ('Update Part List and set', 'Save the changes in the Part List and set'),
    ('Check Max Case/Day against the mapped total of the ongoing period again on the server; if it is below',
     'Check again that Max Case/Day is not below the mapped total of the ongoing period; if it is'),
    ('History retrieved from inserted data when user add/modify part list data', 'The history shows every change made to the part.'),
    ('History is read from change history, which records every change of the part', 'The history records every change of the part'),
    ('Replace the rows of the part and the ongoing period in destination mapping by the rows of the draft', 'Save the new destination mapping of the part for the ongoing period'),
    ('Insert a history record per added, changed or removed destination in change history (event MAPPING, source SCREEN, destination code, field Case/Day, old / new Case/Day).',
     'Record every added, changed or removed destination in the change history (old and new Case/Day).'),
    ('set one row per part and target system (GTOPAS, AP POLE) to sending status Waiting in sending result, and start XD06 and XD07',
     'mark the sending to GTOPAS and AP POLE as Waiting, and start the interfaces XD06 (GTOPAS) and XD07 (AP POLE)'),
    ('the send status is written in the dummy table sending result (sending status 1 sent / 2 Failed, sending time, file name, sending message)',
     'the result (sent or failed, with the reason) is kept per target system'),
    ('Every result is recorded in change history (event SYNC, source IF, REMARK = target and message).', 'Every result is recorded in the change history.'),
    ('in the dummy table sending result', 'per target system'),
    ('Insert / update part record', 'Save the part'), ('(insert only)', '(first save only)'), ('on insert/update of', 'on saving'),
    ('Server system date-time', 'Date and time of saving'), ('Server system date', 'Date of saving'), ('Login user ID', 'User who saved'),
    ('(pre-filled with flag E)', '(pre-filled with upload = E)'), ('REMARK', 'remark'),
]
TYPES = {'Varchar': 'Text', 'Char': 'Text', 'Number': 'Number', 'Int': 'Number', 'Date': 'Date', 'Datetime': 'Date and time'}
OPS = {'Insert': 'Add', 'Update': 'Change', 'Delete': 'Remove', 'Insert / Update': 'Add / change'}


def biz(s):
    if not isinstance(s, str):
        return s
    for k in sorted(VOCAB, key=len, reverse=True):
        s = re.sub(rf'\b{k}\b', VOCAB[k], s)
    s = re.sub(r"(Sync Status|status|sending status)\s*=\s*'?\d'?\s*\(([^)]+)\)", r'\1 \2', s)   # SYNC_STATUS = 0 (No Sync) -> Sync Status No Sync
    s = re.sub(r"'?\b(\d)\b'? \((No Sync|Waiting|Success|Failed)\)", r'\2', s)
    s = re.sub(r'\bNULL\b', 'empty', s)
    s = re.sub(r'sorted by ([\w /]+?) descending', r'sorted by \1, newest first', s)
    s = s.replace('<DB error message>', '<error detail>').replace('Database error', 'System error').replace('refer Data Edit Mapping', 'see Data Edit Mapping')
    for k, v in PHRASES:
        s = s.replace(k, v)
    return s


def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v) for v in o]
    return biz(o)


def source_of(it):
    s = it.get('source') or ''
    if s.startswith('TB_'):
        return biz(s)
    return {'Key-in': 'Entered by user', 'System': 'System', '-': '-'}.get(s, biz(s))


def build(fid):
    d = importlib.import_module(f'ur_{fid.lower()}')
    spec = json.load(open(os.path.join(SPECS, f'{fid}_spec.json'), encoding='utf-8'))
    ur = {'doc_type': spec['doc_type']}
    ur['header'] = dict(spec['header'], phase='UR', document_name='User Requirement', created_date='28-Oct-26', created_by='FID Rayhan')
    ur['revisions'] = [{'revision': '0.1', 'author': 'FID Rayhan', 'date': '28-Oct-26', 'reviewed_by': '',
                        'description': f'Initial Draft: business version of UISS {d.INFO["uiss"]}'}]
    ur['general'] = walk(spec['general'])
    ur['general']['objective'] = [d.PURPOSE] + ur['general']['objective']
    ur['screen_flow'] = walk(spec['screen_flow'])
    ur['screen_layout'] = walk(spec['screen_layout'])
    # Item Description: what the user sees and enters; no physical field / length / format
    items = []
    for it in spec['items']:
        if 'group' in it and 'name' not in it:
            items.append(walk(it)); continue
        x = walk(it)
        x['source'], x['field'] = source_of(it), '-'
        x['type'] = TYPES.get(it.get('type'), biz(it.get('type', '')))
        x['len'] = '-'
        x['format'] = it.get('format') if it.get('format') in ('DD-Mon-YYYY', 'DD-Mon-YYYY HH:MM') else '-'
        items.append(x)
    ur['items'] = items
    # Data Map: what is saved where, in business names
    dm = walk(spec['data_map'])
    for b in dm.get('blocks', []):
        b['destination']['operation'] = OPS.get(b['destination'].get('operation'), b['destination'].get('operation'))
    internal = {'last source', 'last upload no.', 'sync time', 'sync message', 'created by', 'created time', 'updated by', 'last update time',
                'history no.', 'remark', 'upload no.'}
    for b in dm.get('blocks', []):
        maps = [m for m in b.get('mappings', []) if m.get('dest_field') not in internal]
        if len(maps) < len(b.get('mappings', [])):
            maps.append({'dest_field': 'Saved by / time', 'description': 'User who saved, date and time of saving'})
        for m in maps:
            t = re.sub(r"^NULL\b ?", '', m.get('description', '')).strip()
            if t.startswith('(') and t.endswith(')'):
                t = t[1:-1]
            m['description'] = t or '-'
            m['description'] = m['description'].replace("'SCREEN'", 'Screen')
        b['mappings'] = maps
    ur['data_map'] = dm
    # Operation Description: business rules first, then the steps, then the acceptance criteria
    rules = [{'type': 'heading', 'text': '5.0 Business Rules'},
             {'type': 'table', 'level': 1, 'columns': [{'title': 'ID', 'width': 6}, {'title': 'Topic', 'width': 12}, {'title': 'Rule', 'width': 80}],
              'rows': [list(r) for r in d.BR]}]
    accept = [{'type': 'page_break'}, {'type': 'heading', 'text': '6. Acceptance Criteria (UAT)'},
              {'type': 'table', 'level': 1, 'columns': [{'title': 'ID', 'width': 6}, {'title': 'Scenario (Given / When / Then)', 'width': 62},
                                                        {'title': 'Rule', 'width': 18}, {'title': 'Result', 'width': 10}],
               'rows': [[a[0], a[1], a[3], ''] for a in d.AC]}]
    ops = [b for b in walk(spec['operation']) if not str(b.get('text', '')).startswith(('change history (proposed)', 'Events: ADD'))
           and not (b.get('type') == 'table' and 'VARCHAR' in json.dumps(b))]   # column definitions stay in the UISS
    for b in ops:
        if str(b.get('text', '')).startswith('Proposed retention'):
            b['text'] = 'The history is kept for 24 months (to be confirmed).'
    ur['operation'] = rules + ops + accept
    ur['operation_layout'] = 'full'
    ur['display_messages'] = walk(spec['display_messages'])
    ur['logging_messages'] = walk(spec['logging_messages'])
    out_spec = os.path.join(HERE, f'{fid}_UR_spec.json')
    json.dump(ur, open(out_spec, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    out = os.path.join(HERE, f'{fid}_UR_{d.INFO["name"].replace(" ", "")}.xlsx')
    subprocess.run([sys.executable, os.path.join(ROOT, 'deliverables', 'uiss_specs', 'uiss_build.py'), out_spec, '-o', out],
                   check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    left = sorted(set(re.findall(r'\bTB_[A-Z0-9_]+|\b[A-Z]{2,}_[A-Z0-9_]{2,}\b', json.dumps(ur))))
    print('written', out, '| technical names left:', left)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'XD01')
