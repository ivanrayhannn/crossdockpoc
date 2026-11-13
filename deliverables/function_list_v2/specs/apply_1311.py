"""13-Nov: ASN Crossdock Creation (XD10) - D/S team holds
1) Hold per Supplier Code + Plant (TB_M_CROSSDOCK_SUPPLIER_HOLD): the units of the supplier stay visible, On Hold, check boxes disabled.
2) Hold per case = Reduce PO Readiness (case) per unit (TB_R_CROSSDOCK_CASE_HOLD): Ready n - reduce r -> the last cases are held;
   the Ready part is rounded down to the last valid cut; stored until the D/S team releases it.
XD09 applies both when it sets CROSSDOCK_STATUS ('8' = On Hold)."""
import json

IMG = 'deliverables/uiss_screens/asn_crossdock'
AUDIT = [['CREATED_BY', 'VARCHAR(20)', '', 'N', 'Login user (D/S team) who created the record'],
         ['CREATED_DT', 'DATETIME', '', 'N', 'Created date and time'],
         ['CHANGED_BY', 'VARCHAR(20)', '', 'N', 'Login user (D/S team) who last changed the record'],
         ['CHANGED_DT', 'DATETIME', '', 'N', 'Last changed date and time']]
T_SUP = {'name': 'TB_M_CROSSDOCK_SUPPLIER_HOLD', 'kind': 'master', 'proposed': True,
         'description': 'New table: Supplier Code + Plant put on hold by the D/S team on ASN Crossdock Creation. HOLD_FLAG Y = no ASN can be created for the supplier + plant. Name and columns proposed.',
         'columns': [['SUPPLIER_CD', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier code (as in the Pra Daily Order / supplier master)'],
                     ['SUPPLIER_PLANT', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier plant'],
                     ['HOLD_FLAG', 'CHAR(1)', '', 'N', "'Y' on hold / 'N' released (no row = 'N')"]] + AUDIT}
T_CASE = {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'kind': 'transaction', 'proposed': True,
          'description': 'New table: Reduce PO Readiness (case) of a unit (Part Number + Customer Order Date + Supplier Code + Plant) set by the D/S team: the last REDUCE_CASE Ready cases are held. Kept until the D/S team releases it (row deleted). Name and columns proposed.',
          'columns': [['PART_NO', 'VARCHAR(15)', 'Y', 'N', 'Part number (H0253.SHIPPING_PART_NO)'],
                      ['ORDER_DT', 'DATE', 'Y', 'N', 'Customer Order Date of the unit'],
                      ['SUPPLIER_CD', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier code of the unit'],
                      ['SUPPLIER_PLANT', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier plant of the unit'],
                      ['REDUCE_CASE', 'INT', '', 'N', 'Number of Ready cases held (1 .. PO Readiness); the Ready part is rounded down to the last valid cut']] + AUDIT}


def item(name, src, field, typ, io, control, desc, initial='-', fmt='-', valid='-', required='N', just='Left', length='-'):
    return {'name': name, 'source': src, 'field': field, 'type': typ, 'len': length, 'io': io, 'control': control, 'justified': just,
            'initial': initial, 'required': required, 'format': fmt, 'validation': valid, 'description': desc}


with open('XD10_spec.json') as fh:
    s = json.load(fh)

# ---------- screen layout ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04_ds_hold.png'))
sl[k + 1:k + 1] = [
    {'caption': '4a. D/S team: Reduce PO Readiness (case) 1 on PART-X 17-Oct: PO Readiness 4 - 1 = Ready 3, case 4 On Hold (D/S) until released', 'image': f'{IMG}/c_04b_ds_reduce.png'},
    {'caption': '4b. Supplier view of the reduced unit: case 4 On Hold (D/S), only cases 1-3 can be ticked', 'image': f'{IMG}/c_04c_supplier_reduce.png'},
    {'caption': '4c. D/S team: Hold per Supplier Code + Plant (supplier 50221 plant 1 on hold)', 'image': f'{IMG}/c_04d_ds_supplier_hold.png'},
    {'caption': '4d. Supplier view: its units stay visible, On Hold, check boxes disabled (message no. 12)', 'image': f'{IMG}/c_04e_supplier_on_hold.png'}]

# ---------- buttons ----------
g = s['general']
bi = next(i for i, b in enumerate(g['buttons']) if b['name'] == 'Hold / Release (D/S)')
g['buttons'][bi + 1:bi + 1] = [
    {'name': 'Hold / Release Supplier (D/S)', 'function': "D/S team only: set HOLD_FLAG of a Supplier Code + Plant in TB_M_CROSSDOCK_SUPPLIER_HOLD to 'Y' (hold) or 'N' (release)."},
    {'name': 'Save Reduce (D/S)', 'function': 'D/S team only: save Reduce PO Readiness (case) of the unit in TB_R_CROSSDOCK_CASE_HOLD (0 / blank = release).'},
    {'name': 'Release Reduce (D/S)', 'function': 'D/S team only: delete the Reduce PO Readiness (case) of the unit: all Ready cases can be selected again.'}]
for m in g['screen_modes']:
    for sec in m['sections']:
        bt = sec.get('buttons')
        if isinstance(bt, dict) and 'Hold / Release (D/S)' in bt:
            v = bt['Hold / Release (D/S)']
            new = {}
            for kk, vv in bt.items():
                new[kk] = vv
                if kk == 'Hold / Release (D/S)':
                    new['Hold / Release Supplier (D/S)'] = v
                    new['Save Reduce (D/S)'] = v
                    new['Release Reduce (D/S)'] = v
            sec['buttons'] = new

# ---------- items ----------
it = s['items']
pr = next(x for x in it if x.get('name') == 'PO Readiness (case)')
pr['description'] = ('Ready cases: cases whose whole qty is pre-mapped to a PO, minus the cases held by Reduce PO Readiness (case) (rounded down to the last valid cut); '
                     'red when lower than Case Qty. With a reduction the original readiness is shown below, e.g. "4 - 1 on hold".')
dp = next(i for i, x in enumerate(it) if x.get('group') == '<Delivery Plan Section>')
it[dp:dp] = [
    {'group': '<Hold per Supplier Code + Plant (D/S team only)>', 'description': ''},
    item('Supplier Code', 'TB_M_CROSSDOCK_SUPPLIER_HOLD / supplier master', 'SUPPLIER_CD', 'Char', 'O', 'Grid', 'Suppliers with crossdock parts.'),
    item('Plant', 'TB_M_CROSSDOCK_SUPPLIER_HOLD / supplier master', 'SUPPLIER_PLANT', 'Char', 'O', 'Grid', 'Supplier plant.'),
    item('Supplier Name', 'Supplier master', '-', 'Char', 'O', 'Grid', 'Name of the supplier.'),
    item('Hold Flag (button)', '-', 'HOLD_FLAG', 'Button', 'I', 'Button', "'N · Hold' sets Y, 'Y · Release' sets N. While Y every unit of the supplier + plant is On Hold (check boxes disabled, message no. 12). Refer 5.3.",
         initial='N · Hold', just='Center')]
dd = next(i for i, x in enumerate(it) if x.get('group') == '<Destination Detail (D/S team only)>')
it[dd + 1:dd + 1] = [
    item('Reduce PO Readiness (case)', 'Key-in / TB_R_CROSSDOCK_CASE_HOLD', 'REDUCE_CASE', 'Number', 'I', 'Text Box',
         'Number of Ready cases to hold (counted from the last Ready case). Ready = PO Readiness - reduce, rounded down to the last valid cut (CUT_FLAG Y). Kept until released.',
         initial='Saved value / blank', fmt='ZZ9', valid='Whole number 0 .. PO Readiness (message no. 13)', just='Right'),
    item('Save (Reduce)', '-', '-', '-', 'I', 'Button', 'Saves the reduction (0 / blank = release). Refer 5.3.', initial='Enabled', just='Center'),
    item('Release (Reduce)', '-', '-', '-', 'I', 'Button', 'Deletes the reduction of the unit; shown when a reduction is saved. Refer 5.3.', initial='Enabled when saved', just='Center')]
sc = next(i for i, x in enumerate(it) if x.get('group') == '<Supplier Cases of a Unit (H0253 order)>')
for x in it[sc + 1:]:
    if 'group' in x:
        break
    if x.get('name') == 'PO Status':
        x['description'] = (x.get('description', '') + " 'On Hold (D/S)' (grey) when the case is held by Reduce PO Readiness (case) or the supplier + plant is on hold; check box disabled (message no. 14 / 12).").strip()

# ---------- operation ----------
op = s['operation']
h = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.3'))
op[h + 1]['items'] += [
    'Hold per Supplier Code + Plant (decided 13-Nov): the D/S team sets HOLD_FLAG = Y of a supplier + plant in TB_M_CROSSDOCK_SUPPLIER_HOLD (button Hold / Release Supplier). '
    'Every unit of that supplier + plant stays visible to the supplier and the D/S team with status On Hold; the check boxes are disabled (message no. 12) and no ASN can be created until the D/S team releases it.',
    'Hold per case = Reduce PO Readiness (case) (decided 13-Nov): in the unit detail the D/S team enters the number of Ready cases to hold, e.g. PO Readiness 4, reduce 1 -> Ready 3, case 4 On Hold (D/S). '
    'The cases are held from the last Ready case backwards; the Ready part must end on a valid cut (CUT_FLAG Y), else it is rounded down to the previous valid cut '
    '(e.g. cases 3-4 belong together, reduce 1 -> Ready 2, cases 3-4 held). Input 0 .. PO Readiness, else message no. 13.',
    'The reduction is saved per unit (Part Number + Customer Order Date + Supplier Code + Plant) in TB_R_CROSSDOCK_CASE_HOLD and kept until the D/S team releases it (Release or 0): '
    'at every Search, Ready = PO Readiness of XD09 - reduce (a new PO raises the PO Readiness, the reduction stays). A held case shows PO Status On Hold (D/S) to the supplier too (message no. 14).',
    'Both holds are re-checked at [Create ASN] like the destination hold: a hold made after the units were ticked makes the whole create fail (message no. 8) and the delivery plan is refreshed.']
h2 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.2'))
op[h2 + 1]['items'].append("On Hold also when the Supplier Code + Plant of the unit is on hold (5.3); cases held by Reduce PO Readiness (case) are not Ready (CROSSDOCK_STATUS '8' On Hold) and are not counted in PO Readiness.")

# ---------- data map ----------
s['data_map']['blocks'][1:1] = [
    {'source': 'Hold / Release Supplier (D/S)',
     'destination': {'table': 'TB_M_CROSSDOCK_SUPPLIER_HOLD', 'operation': 'Insert / Update', 'description': 'Supplier Code + Plant of the button (insert when no row yet)',
                     'keys': [{'field': 'SUPPLIER_CD + SUPPLIER_PLANT', 'value': 'Supplier + plant of the button'}]},
     'mappings': [{'dest_field': 'SUPPLIER_CD', 'description': 'Supplier code'}, {'dest_field': 'SUPPLIER_PLANT', 'description': 'Supplier plant'},
                  {'dest_field': 'HOLD_FLAG', 'description': "'Y' (hold) / 'N' (release)"},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]},
    {'source': 'Save / Release Reduce (D/S)',
     'destination': {'table': 'TB_R_CROSSDOCK_CASE_HOLD', 'operation': 'Insert / Update / Delete',
                     'description': 'Reduce PO Readiness (case) of the unit: insert / update when > 0; delete when 0, blank or Release',
                     'keys': [{'field': 'PART_NO + ORDER_DT + SUPPLIER_CD + SUPPLIER_PLANT', 'value': 'Unit of the detail'}]},
     'mappings': [{'dest_field': 'PART_NO', 'description': 'Part number of the unit'}, {'dest_field': 'ORDER_DT', 'description': 'Customer Order Date of the unit'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the unit'},
                  {'dest_field': 'REDUCE_CASE', 'description': 'Input (1 .. PO Readiness)'},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]}]

# ---------- messages ----------
dm = s['display_messages']
m2 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG2')
dm[m2 + 1:m2 + 1] = [
    {'event': 'Hover on disabled check box', 'cause': 'Supplier Code + Plant on hold (D/S)', 'type': 'Info', 'msg_id': 'MSG12',
     'message': 'Supplier {Supplier Code} · Plant {Plant} is on hold by the D/S team', 'action': 'Contact the D/S team.'},
    {'event': 'Hover on disabled case check box', 'cause': 'Case held by Reduce PO Readiness (case)', 'type': 'Info', 'msg_id': 'MSG14',
     'message': 'On hold by the D/S team: Reduce PO Readiness (case) {n} of {Part No} / {Customer Order Date}', 'action': 'Contact the D/S team.'}]
dm.append({'event': 'Click [Save] (Reduce PO Readiness)', 'cause': 'Not a whole number or more than PO Readiness', 'type': 'Error', 'msg_id': 'MSG13',
           'message': 'Reduce PO Readiness (case) must be a whole number from 0 to {PO Readiness} (PO Readiness).', 'action': 'Correct the value.'})

# ---------- tables ----------
s['tables'] += [T_SUP, T_CASE]
with open('XD10_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD10_spec.json')

# ---------- XD09 ----------
with open('XD09_spec.json') as fh:
    s = json.load(fh)
s['general']['inputs'] += [
    {'name': 'TB_M_CROSSDOCK_SUPPLIER_HOLD', 'type': 'DB', 'description': 'Supplier Code + Plant on hold (HOLD_FLAG Y): every case of their units On Hold'},
    {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'type': 'DB', 'description': 'Reduce PO Readiness (case) per unit: the last Ready cases On Hold'}]
fd = s['func_desc']
h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x.get('text', '').startswith('4.3'))
fd[h + 1]['items'] += [
    "Holds of the D/S team (XD10 5.3, decided 13-Nov): supplier + plant with HOLD_FLAG Y in TB_M_CROSSDOCK_SUPPLIER_HOLD -> every case of its units CROSSDOCK_STATUS '8' (On Hold).",
    "Reduce PO Readiness (case) of the unit in TB_R_CROSSDOCK_CASE_HOLD: Ready end = last valid cut <= (Ready cases - REDUCE_CASE); the Ready cases after it get CROSSDOCK_STATUS '8' (On Hold). "
    'Example: Ready 4, reduce 1 -> cases 1-3 Ready, case 4 On Hold; if cases 3-4 belong together -> cases 1-2 Ready, cases 3-4 On Hold.']
for t in s['tables']:
    for c in t['columns']:
        if c[0] == 'CROSSDOCK_STATUS':
            c[4] = c[4].rstrip('.') + " / '8' On Hold (D/S: supplier + plant hold or Reduce PO Readiness)"
s['tables'] += [T_SUP, T_CASE]
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')
