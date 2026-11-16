"""16-Nov: table concept of XD09 from DR_XD09_UISS_Batch_MappingCustomerOrderPO.xlsx (DR by FID Zsi Zsi, 11-Nov).

The session table #TEMP_INSTRUCTION is replaced by two NSP tables:
- TB_T_INSTRUCTION_H: one row per unit (Customer Order Date + Part Number + supplier), with the open qty and the case qty;
- TB_T_INSTRUCTION_D: one row per pc (customer order line broken down to 1, PO qty broken down to 1) with its PO and CASE_NO.
Rows belong to the company of the login user (LEFT(CREATE_BY, 4)); the rows of the company are deleted and inserted again at each run.
The business rules of XD09 (H0253 order, pouring, case cut, holds) stay; columns the DR does not have but the rules need are marked
"(added)". Runs after apply_1311c and before apply_1611 (revisions).
"""
import json

H = 'TB_T_INSTRUCTION_H'
D = 'TB_T_INSTRUCTION_D'
DR = 'DR XD09 (11-Nov)'
AUDIT = [['CREATE_DT', 'TIMESTAMP', '', 'N', 'System date-time of the run'],
         ['CREATE_BY', 'VARCHAR(20)', '', 'N', 'Login user; LEFT(CREATE_BY, 4) = company code of the user (rows of the company)'],
         ['UPDATE_DT', 'TIMESTAMP', '', 'Y', 'Last update date-time'],
         ['UPDATE_BY', 'VARCHAR(20)', '', 'Y', 'Last update user']]
UNIT = [['ORDER_DT', 'DATE', 'Y', 'N', 'Customer Order Date (H0253.ORDER_DT)'],
        ['SHIPPING_PART_NO', 'VARCHAR(15)', 'Y', 'N', 'Part Number (H0253.SHIPPING_PART_NO)'],
        ['SUPPLIER_CD', 'VARCHAR(4)', 'Y', 'N', 'Supplier of the crossdock PO (TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_CD)'],
        ['SUPPLIER_PLANT', 'VARCHAR(1)', 'Y', 'N', 'Supplier plant (TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_PLANT)'],
        ['SUB_SUPP_CD', 'VARCHAR(4)', '', 'Y', 'Sub supplier (TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_CD)'],
        ['SUB_SUPP_PLANT', 'VARCHAR(1)', '', 'Y', 'Sub supplier plant (TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_PLANT)']]

T_H = {'name': H, 'kind': 'transaction', 'proposed': True,
       'description': f'Draft of ASN Crossdock, header ({DR}): one row per unit = Customer Order Date + Part Number + supplier. '
                      'Written by XD09 at [Search] of XD10 for the company of the login user: its rows (LEFT(CREATE_BY, 4) = company code) are '
                      'deleted and inserted again; company 1000 (TMMIN, D/S team) sees every supplier.',
       'columns': UNIT + [
           ['ORDER_STATUS_QTY', 'NUMBER(8)', '', 'N', 'Open qty of the unit = SUM(H0253.ORDER_STATUS_QTY) of the lines not on hold and not yet in TB_R_INSTRUCTION'],
           ['CASE', 'NUMBER(8)', '', 'N', 'Case Qty of the unit = number of supplier cases (CEILING(ORDER_STATUS_QTY / TB_M_PART_CANDIDATE.PCS_CASE))'],
           ['SUBMIT_ASN_STS', 'VARCHAR(1)', '', 'Y', "'Y' the unit has Ready cases that can go into an ASN / 'N' not (DR; also named GENERATE_ASN_STS in the DR Data Map, refer FB-193)"],
       ] + AUDIT}

T_D = {'name': D, 'kind': 'transaction', 'proposed': True,
       'description': f'Draft of ASN Crossdock, detail ({DR}): one row per pc. The customer order line is broken down to 1 pc per row '
                      '(ORDER_STATUS_QTY = 1) and the PO qty is broken down to 1 (PO_QTY = 1). The pcs of a supplier case share one CASE_NO. '
                      'Columns marked (added) are not in the DR but needed by the rules of 4.1-4.3.',
       'columns': UNIT + [
           ['SEQ_NO', 'NUMBER(6)', 'Y', 'N', '(added) Sequence of the pc in the unit in the H0253 order of 4.1; key of the row'],
           ['CUSTOMER_CD', 'VARCHAR(7)', '', 'N', '(added) H0253.CUSTOMER_CD (order key 1, needed for the H0253 order and TB_R_INSTRUCTION)'],
           ['CUSTOMER_ORDER_NO', 'VARCHAR(8)', '', 'N', 'H0253.CUSTOMER_ORDER_NO'],
           ['DESTINATION_CD', 'VARCHAR(7)', '', 'N', 'H0253.DESTINATION_CD'],
           ['DETAILED_ITEM_NO', 'VARCHAR(4)', '', 'N', 'H0253.DETAILED_ITEM_NO'],
           ['SERIAL_NO', 'VARCHAR(7)', '', 'N', 'H0253.SERIAL_NO (DR simulation: SERIAL_CARD_NO, refer FB-193)'],
           ['ORDER_STATUS_QTY', 'NUMBER(8)', '', 'N', 'Always 1 (customer order line broken down to 1 pc)'],
           ['PO_NO', 'VARCHAR(20)', '', 'Y', 'PO of the pc (pouring of 4.2: oldest PO first); NULL when no PO is left or the pc is held'],
           ['PO_ITEM', 'VARCHAR(4)', '', 'Y', 'TB_R_PRA_DAILY_ORDER_PART.PO_ITEM'],
           ['MANIFEST_NO', 'VARCHAR(20)', '', 'Y', 'TB_R_PRA_DAILY_ORDER_PART.MANIFEST_NO'],
           ['MANIFEST_ITEM', 'VARCHAR(4)', '', 'Y', 'TB_R_PRA_DAILY_ORDER_PART.MANIFEST_ITEM'],
           ['PO_QTY', 'NUMBER(8)', '', 'N', '1 when the pc has a PO (PO qty broken down to 1); 0 when PO_NO is NULL'],
           ['CASE_NO', 'VARCHAR(8)', '', 'Y', 'Supplier case (case label) of the pc: supplier (sub supplier when it exists) + plant + initial palletize code + '
                                              'next CASE_LABEL_LAST_SEQ of TB_R_CASE_LABEL_LAST_SEQ; the same CASE_NO for PCS_CASE pcs in H0253 order (DR); NULL for a held pc'],
           ['CUT_FLAG', 'VARCHAR(1)', '', 'Y', "(added) 'Y' on the pcs of a case after which the ASN may stop (every destination of the unit a multiple of PCS_CASE, 4.3)"],
           ['GROUP_SEQ', 'NUMBER(4)', '', 'Y', '(added) Case Group: the cases up to and including a valid cut; sent together'],
           ['CROSSDOCK_STATUS', 'VARCHAR(1)', '', 'Y', "(added) '6' Ready / '7' Not Ready / '8' On Hold (D/S) of the case group"],
           ['HOLD_STS', 'CHAR(1)', '', 'Y', "'Y' pc held by the D/S team (Hold per case, Part Number on hold): no PO, no CASE_NO; NULL otherwise"],
       ] + AUDIT}

OLD = '#TEMP_INSTRUCTION'


def swap_tables(s):
    out = []
    for t in s['tables']:
        if t['name'] == OLD:
            out += [T_H, T_D]
        else:
            out.append(t)
    s['tables'] = out


def replace_all(o, pairs):
    if isinstance(o, dict):
        return {k: replace_all(v, pairs) for k, v in o.items()}
    if isinstance(o, list):
        return [replace_all(v, pairs) for v in o]
    if isinstance(o, str):
        for a, b in pairs:
            o = o.replace(a, b)
    return o


# ---------------- XD09 ----------------
with open('XD09_spec.json') as fh:
    s = json.load(fh)
swap_tables(s)
g = s['general']
g['objective'] = [x.replace(OLD, f'{H} / {D}') for x in g['objective']]
g['objective'].append(f'Table concept from the {DR}: the draft is kept in {H} (one row per unit) and {D} (one row per pc), '
                      'per company of the login user.')
g['outputs'] = [{'name': H, 'type': 'DB', 'description': 'Draft header: one row per unit with open qty and case qty'},
                {'name': D, 'type': 'DB', 'description': 'Draft detail: one row per pc with PO, CASE_NO and hold status'}] + \
               [o for o in g['outputs'] if o['name'] != OLD]
g['inputs'].append({'name': 'TB_R_CASE_LABEL_LAST_SEQ', 'type': 'DB', 'description': 'Last case label sequence per supplier + plant (CASE_NO of the draft)'})
st = s['func_flow']['steps']
st[0] = ('The user clicks [Search] on ASN Crossdock Creation (XD10) with Delivery Date and Rit. '
         f'The rows of the company of the login user (LEFT(CREATE_BY, 4) = company code) are deleted from {H} and {D}; '
         'company 1000 (TMMIN) keeps the rows of the other companies (DR).')
blk = s['data_map']['blocks'][0]
src = blk['source']
s['data_map']['blocks'][0:1] = [
    {'source': src,
     'destination': {'table': H, 'operation': 'Delete / Insert', 'description': 'One row per unit (Customer Order Date + Part Number + supplier)',
                     'keys': [{'field': 'ORDER_DT + SHIPPING_PART_NO + SUPPLIER_CD + SUPPLIER_PLANT', 'value': 'Unit'}]},
     'mappings': [
         {'source_field': 'H0253.ORDER_DT', 'dest_field': 'ORDER_DT'},
         {'source_field': 'H0253.SHIPPING_PART_NO', 'dest_field': 'SHIPPING_PART_NO'},
         {'dest_field': 'ORDER_STATUS_QTY', 'description': 'SUM(H0253.ORDER_STATUS_QTY) GROUP BY SHIPPING_PART_NO, ORDER_DT (open qty, not held)'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_CD', 'dest_field': 'SUPPLIER_CD'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_PLANT', 'dest_field': 'SUPPLIER_PLANT'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_CD', 'dest_field': 'SUB_SUPP_CD'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_PLANT', 'dest_field': 'SUB_SUPP_PLANT'},
         {'dest_field': 'CASE', 'description': 'CEILING(ORDER_STATUS_QTY / TB_M_PART_CANDIDATE.PCS_CASE)'},
         {'dest_field': 'SUBMIT_ASN_STS', 'description': "'Y' when the unit has Ready cases, else 'N'"},
         {'dest_field': 'CREATE_DT', 'description': 'System date'},
         {'dest_field': 'CREATE_BY', 'description': 'Param.UserLogin'}]},
    {'source': src,
     'destination': {'table': D, 'operation': 'Delete / Insert', 'description': 'One row per pc (customer order line and PO qty broken down to 1)',
                     'keys': [{'field': 'ORDER_DT + SHIPPING_PART_NO + SUPPLIER_CD + SUPPLIER_PLANT + SEQ_NO', 'value': 'Pc of the unit'}]},
     'mappings': [
         {'source_field': 'H0253.ORDER_DT', 'dest_field': 'ORDER_DT'},
         {'source_field': 'H0253.SHIPPING_PART_NO', 'dest_field': 'SHIPPING_PART_NO'},
         {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT / SUB_SUPP_CD / SUB_SUPP_PLANT', 'description': 'From TB_R_PRA_DAILY_ORDER_MANIFEST'},
         {'dest_field': 'SEQ_NO', 'description': '(added) 1.. per unit in the H0253 order of 4.1'},
         {'source_field': 'H0253.CUSTOMER_CD', 'dest_field': 'CUSTOMER_CD', 'description': '(added)'},
         {'source_field': 'H0253.CUSTOMER_ORDER_NO', 'dest_field': 'CUSTOMER_ORDER_NO'},
         {'source_field': 'H0253.DESTINATION_CD', 'dest_field': 'DESTINATION_CD'},
         {'source_field': 'H0253.DETAILED_ITEM_NO', 'dest_field': 'DETAILED_ITEM_NO'},
         {'source_field': 'H0253.SERIAL_NO', 'dest_field': 'SERIAL_NO'},
         {'dest_field': 'ORDER_STATUS_QTY', 'description': 'Breakdown of H0253.ORDER_STATUS_QTY (open qty) to 1'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_PART.PO_NO', 'dest_field': 'PO_NO', 'description': 'Pouring of 4.2; NULL when no PO left or held'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_PART.PO_ITEM', 'dest_field': 'PO_ITEM'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_PART.MANIFEST_NO', 'dest_field': 'MANIFEST_NO'},
         {'source_field': 'TB_R_PRA_DAILY_ORDER_PART.MANIFEST_ITEM', 'dest_field': 'MANIFEST_ITEM'},
         {'dest_field': 'PO_QTY', 'description': 'Breakdown of the open PO qty to 1 (1 per pc with PO, 0 without)'},
         {'dest_field': 'CASE_NO', 'description': 'TB_R_CASE_LABEL_LAST_SEQ: supplier + plant + initial palletize code + last seq + 1; '
                                                  'same CASE_NO until PCS_CASE pcs (TB_M_PART_CANDIDATE.PCS_CASE); last seq updated'},
         {'dest_field': 'CUT_FLAG / GROUP_SEQ / CROSSDOCK_STATUS', 'description': '(added) Case cut and status of 4.3'},
         {'dest_field': 'HOLD_STS', 'description': "'Y' for the pcs held by the D/S team (TB_R_CROSSDOCK_CASE_HOLD / PART_HOLD), else NULL"},
         {'dest_field': 'CREATE_DT', 'description': 'System date'},
         {'dest_field': 'CREATE_BY', 'description': 'Param.UserLogin'}]}]
fd = s['func_desc']
fd[0]['text'] = (f'XD09 runs on [Search] of XD10 and writes the draft of the delivery plan in {H} / {D} (table concept of the {DR}). '
                 '[Create ASN] (XD10) writes TB_R_INSTRUCTION, PO_MAPPED_FLAG and MAPPED_QTY. Examples: simulasi_asn_rev.xlsx (sheet Sample Input).')
fd.insert(1, {'type': 'heading', 'text': '4.0 Draft tables (16-Nov, from the DR XD09)'})
fd.insert(2, {'type': 'bullets', 'items': [
    f'{H}: one row per unit (Customer Order Date + Part Number + supplier): ORDER_STATUS_QTY = open qty of the unit, CASE = Case Qty, SUBMIT_ASN_STS.',
    f'{D}: one row per pc. The customer order line is broken down to 1 (ORDER_STATUS_QTY 1) and the PO qty is broken down to 1 (PO_QTY 1 with PO_NO); '
    'a pc without PO keeps PO_NO NULL and PO_QTY 0. The qty of a line with a PO = number of its rows with that PO_NO.',
    'CASE_NO: the pcs are given a case label in the H0253 order of 4.1: supplier (sub supplier when it exists) + plant + initial palletize code + '
    'next CASE_LABEL_LAST_SEQ of TB_R_CASE_LABEL_LAST_SEQ; the same CASE_NO is used until PCS_CASE pcs. [Create ASN] / Submit use this CASE_NO.',
    'Rows of the company of the login user (LEFT(CREATE_BY, 4) = company code) are deleted and inserted again at each [Search]; '
    'company 1000 (TMMIN, D/S team) sees all suppliers and keeps the rows of the other companies.',
    "Held pcs (Hold per case, Part Number on hold) are written with HOLD_STS 'Y', PO_NO NULL and no CASE_NO.",
    'CUT_FLAG, GROUP_SEQ, CROSSDOCK_STATUS, SEQ_NO and CUSTOMER_CD are added to the DR table for the rules below.']})
s = replace_all(s, [
    (f'insert the result in {OLD}', f'insert the result in {H} / {D}'),
    ('The qty written in each row is ASSIGNED_QTY; the sum of ASSIGNED_QTY of a line = its open qty.',
     f'Each pc is one row of {D} with its PO (PO_QTY 1); the number of rows of a line = its open qty.'),
    ('PO (ASSIGNED_QTY)', 'PO (pcs)'),
    ('(CASE_SEQ from 1 per unit)', '(CASE_NO per case, in the H0253 order)'),
    ('ASSIGNED_QTY', 'Pcs'),
    ('Each table = #TEMP_INSTRUCTION of one [Search].', f'Each table = {D} of one [Search], shown per slice (rows of 1 pc summed).'),
    (OLD, D)])
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')

# ---------------- XD10 ----------------
with open('XD10_spec.json') as fh:
    s = json.load(fh)
swap_tables(s)
for it in s['items']:
    if it.get('source') in (OLD, f'{OLD} (XD09)'):
        it['source'] = f'{H}' if it.get('name') in ('Case Qty', 'Customer Order Date', 'Part Number') else D
    f = it.get('field', '')
    f = (f.replace('ASSIGNED_QTY (PO_NO NULL)', 'COUNT(pcs) with PO_NO NULL').replace('PO_NO / ASSIGNED_QTY', 'PO_NO / SUM(PO_QTY)')
          .replace('ASSIGNED_QTY', 'SUM(ORDER_STATUS_QTY)').replace('CASE_SEQ', 'CASE_NO'))
    if it.get('name') == 'Hold (D/S)':
        f = it.get('field', '')
    it['field'] = f
dm = s['data_map']['blocks']
for b in dm:
    if isinstance(b.get('source'), str):
        b['source'] = b['source'].replace(f'{OLD} (chosen blocks)', f'{D} (chosen case groups)')
    for m in b['mappings']:
        if m.get('description') == 'Case sequence: selected unit, then CASE_SEQ of XD09 (H0253 order)':
            m['description'] = f'Case sequence: selected unit, then the order of CASE_NO of {D} (H0253 order)'
        if m.get('dest_field') == 'MAPPED_QTY' and 'ASSIGNED_QTY' in m.get('description', ''):
            m['description'] = '+ SUM(PO_QTY) of the chosen case groups; - again on Back / Cancel'
        if m.get('source_field') == 'ASSIGNED_QTY':
            m['source_field'] = 'COUNT(pcs) per case x line x PO'
        if m.get('dest_field') == 'CASE_NO' and m.get('description', '').startswith('Auto generated per CASE_SEQ'):
            m['description'] = f'CASE_NO of {D} (case label made by XD09 from TB_R_CASE_LABEL_LAST_SEQ)'
        if m.get('dest_field') == 'CASE_NO' and m.get('description', '').startswith('NULL (filled by the submit'):
            m['description'] = f'CASE_NO of {D}'
        if m.get('description') == 'Case No of the CASE_SEQ':
            m['description'] = 'Not changed (CASE_NO of the draft)'
        if m.get('description') == 'Customer order line in the ticked case (#TEMP_INSTRUCTION)':
            m['description'] = f'Customer order line in the ticked case ({D})'
        if m.get('description', '').startswith('Pcs of the line in the ticked case (ASSIGNED_QTY)'):
            m['description'] = f'Pcs of the line in the ticked case (rows of {D}), added when the line is already held'
op = s['operation']
for sec in op:
    if sec.get('items'):
        sec['items'] = [x.replace(f'{OLD} is temporary (pre-mapping of [Search]).',
                                  f'{H} / {D} hold the draft of [Search] per company of the login user (table concept of the {DR}).') for x in sec['items']]
CASE_TXT = ('the case numbers come from CASE_NO of the draft (made by XD09 from TB_R_CASE_LABEL_LAST_SEQ, DR XD09)')
g = s['general']
g['objective'] = [x.replace('the ASN number and the case numbers (case label) are auto generated and their last sequence is saved in TB_R_CASE_LABEL_LAST_SEQ',
                            'the ASN number is auto generated (last sequence ASN_LAST_SEQ in TB_R_CASE_LABEL_LAST_SEQ); ' + CASE_TXT) for x in g['objective']]
for sec in op:
    if sec.get('items'):
        sec['items'] = [x.replace('and auto generate one Case No per case by checking the last sequence (TB_R_CASE_LABEL_LAST_SEQ; format as existing).',
                                  f'and take the Case No of each case from CASE_NO of {D} (made by XD09).')
                         .replace('the case number is auto generated by checking the last sequence kept in the TB_R_CASE_LABEL_LAST_SEQ (format as existing, not detailed here).',
                                  f'the case number is CASE_NO of {D}, made by XD09 from the last sequence in TB_R_CASE_LABEL_LAST_SEQ (16-Nov, DR XD09).')
                         .replace('Case number: the format follows the existing NSP case number; the last sequence is kept in the TB_R_CASE_LABEL_LAST_SEQ (note only, not detailed here).',
                                  'Case number: CASE_NO of the draft, made by XD09 at [Search] in the existing NSP format; the last sequence is kept in TB_R_CASE_LABEL_LAST_SEQ.')
                         for x in sec['items']]
for b in dm:
    if b['destination']['table'] == 'TB_R_CASE_LABEL_LAST_SEQ':
        for m in b['mappings']:
            if m.get('dest_field') == 'CASE_LABEL_LAST_SEQ':
                m['description'] = 'Not changed at submit: updated by XD09 when the CASE_NO of the draft are made'
for it in s['items']:
    if it.get('source') == H and it.get('field') == 'PART_NO':
        it['field'] = 'SHIPPING_PART_NO'
    if it.get('name') == 'Case Qty' and it.get('source') == 'Computed':
        it['source'], it['field'] = H, 'CASE'
s = replace_all(s, [(f'in the temporary table {OLD} (pre-mapping only; nothing is saved yet)', f'in the draft tables {H} / {D} (per company of the login user; nothing is mapped yet)'),
                   (f'pre-map to PO ({OLD})', f'pre-map to PO ({H} / {D})'), (f'({OLD})', f'({H} / {D})'), (OLD, D)])
with open('XD10_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD10_spec.json')
