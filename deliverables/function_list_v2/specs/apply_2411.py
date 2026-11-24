"""24-Nov: Order Type on the Export Crossdock Master screen and in the documents (XD01, XD02, XD03, XD05).
- XD01: item Order Type in the destination table (combo box, default **); Destination (CD) unique per destination + order type;
  message no. 31 for a destination + order type used twice; Data Map ORDER_TYPE on TB_M_PART_CANDIDATE_DEST and TB_H_PART_CANDIDATE.
- XD03: template column Order Type after Destination Code; check 4 = destination + order type once per part; Sample Input with Order Type.
- XD02 / XD05: Data Map ORDER_TYPE on TB_H_PART_CANDIDATE (and TB_M_PART_CANDIDATE_DEST for XD05).
Runs after apply_2311."""
import json
import os

D = '24-Nov-26'
HERE = os.path.dirname(os.path.abspath(__file__))
DUP = 'The same destination is used twice with the same order type. Choose another order type or remove the row.'


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return False
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'
    return True


def ot_maps(s):
    for b in s['data_map']['blocks']:
        t, op = b['destination'].get('table'), b['destination'].get('operation')
        fields = [m['dest_field'] for m in b['mappings']]
        if 'ORDER_TYPE' in fields:
            continue
        if t == 'TB_M_PART_CANDIDATE_DEST':
            m = {'source_field': 'Order Type' if op == 'Insert' else 'ORDER_TYPE', 'dest_field': 'ORDER_TYPE',
                 'description': {'Insert': "Order Type of the row ('**', 'C', '9', 'V'; default '**')", 'Update': 'Key of the row (not changed)',
                                 'Delete': 'Key of the row to delete'}.get(op, 'Order Type of the row')}
            i = fields.index('DEST_CODE') + 1 if 'DEST_CODE' in fields else 0
            b['mappings'].insert(i, m)
        if t == 'TB_H_PART_CANDIDATE':
            i = fields.index('DEST_CODE') + 1 if 'DEST_CODE' in fields else len(fields)
            b['mappings'].insert(i, {'source_field': 'ORDER_TYPE', 'dest_field': 'ORDER_TYPE', 'description': 'Order Type of the destination row for MAPPING; NULL for other events'})


def xd01(s):
    it = s['items']
    k = next(i for i, x in enumerate(it) if x.get('name') == 'Destination (CD)')
    it[k]['validation'] = 'Destination + Order Type once per part'
    it[k]['description'] = it[k]['description'].replace('Destinations already used by another row of the same part are hidden.',
                                                        'The same destination may be chosen again with another Order Type.')
    if it[k + 1].get('name') != 'Order Type':
        it.insert(k + 1, {'name': 'Order Type', 'source': 'TB_M_PART_CANDIDATE_DEST', 'field': 'ORDER_TYPE', 'type': 'Varchar', 'len': '2', 'io': 'I/O',
                          'control': 'Combo Box', 'justified': 'Left', 'initial': "New row: '**'", 'required': 'Y', 'format': 'XX',
                          'validation': "'**', 'C', '9', 'V' (system master). Destination + Order Type once per part (message no. 31)",
                          'description': 'Order Type of the destination row, shown in view and edit mode; editable in edit mode only. '
                                         'The same destination may have two rows when the order type differs.'})
    if not any(m.get('msg_id') == 'MSG31' for m in s['display_messages']):
        s['display_messages'].append({'event': "Click [Save] in Edit mapping", 'cause': 'Destination + Order Type used twice for the part',
                                      'type': 'Error', 'msg_id': 'MSG31', 'message': DUP, 'action': 'Choose another order type or remove the row'})
    for o in s['operation']:
        if 'items' in o:
            o['items'] = [t.replace('a row has no destination selected (show message no. 21).',
                                    'a row has no destination selected (show message no. 21);') for t in o['items']]
            if 'a row has no destination selected (show message no. 21);' in o['items'] and not any('message no. 31' in t for t in o['items']):
                i = o['items'].index('a row has no destination selected (show message no. 21);')
                o['items'].insert(i + 1, 'the same destination + order type is used twice (show message no. 31).')
    ot_maps(s)
    return rev(s, '0.12', 'Order Type per destination row on the Export Crossdock Master screen (item Order Type, message no. 31, Data Map ORDER_TYPE).')


def xd03(s):
    for a in s['appendix']:
        if a.get('type') == 'table':
            rows = a['rows']
            if rows and rows[0][0] == 'Part Number' and not any(r[0] == 'Order Type' for r in rows):
                i = next(j for j, r in enumerate(rows) if r[0] == 'Destination Code')
                rows[i][1] = rows[i][1].replace('Once per part.', 'Destination + Order Type once per part.')
                rows.insert(i + 1, ['Order Type', "'**', 'C', '9' or 'V' (system master), mandatory when Destination Code is filled. The same destination may have two rows when the order type differs."])
    for x in s['func_desc']:
        if x.get('type') == 'table':
            for r in x['rows']:
                if r[0] == '4' and r[1].startswith('A destination code appears only once per part'):
                    r[1], r[2] = 'A destination code + order type appears only once per part in the file (the same destination with another order type is allowed).', 'Destination Code, Order Type'
    for sec in s['sample_sheet']['sections']:
        cols = sec['columns']
        if 'Destination Code' in cols and 'Order Type' not in cols:
            i = cols.index('Destination Code') + 1
            cols.insert(i, 'Order Type')
            for r in sec['rows']:
                r.insert(i, '**' if r[i - 1] else '')
            for r in sec['rows']:
                if r[1] == 'Same destination twice':
                    r[1] = 'Same destination + order type twice'
                    if r[-1]:
                        r[-1] = 'Check 4: Destination 9722D10 with order type ** appears more than once for this part.'
            if sec['title'].startswith('B.') and not any(r[0] == 'N9' for r in sec['rows']):
                n = len(cols)
                row = ['N9', 'Same destination, another order type', 'PART-C', '9715310', 'C', 6, 24, 30, 'A', '']
                row = row[:n - 1] + ['Accepted: 9715310 ** 18 stays, a second row 9715310 C 6 is added (total 24 ≤ 30). Export staging ADD for 9715310 C; no GTOPAS row (the destination is already there).']
                sec['rows'].append(row)
    ot_maps(s)
    return rev(s, '0.6', 'Order Type column in the upload template (after Destination Code); check 4 = destination + order type once per part; Sample Input with Order Type.')


def xd_other(s, no):
    ot_maps(s)
    return rev(s, no, 'Data Map: ORDER_TYPE on TB_H_PART_CANDIDATE / TB_M_PART_CANDIDATE_DEST (Order Type per destination row).')


FUN = {'XD01': xd01, 'XD03': xd03, 'XD02': lambda s: xd_other(s, '0.6'), 'XD05': lambda s: xd_other(s, '0.8')}
for fid, fn in FUN.items():
    p = os.path.join(HERE, f'{fid}_spec.json')
    s = json.load(open(p))
    if any(r['date'] == D for r in s['revisions']):
        continue
    fn(s)
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched', fid)
