"""13-Nov: ASN Crossdock Creation (XD10) - D/S team holds
1) Hold per Supplier Code + Plant (TB_M_CROSSDOCK_SUPPLIER_HOLD): the units of the supplier stay visible, On Hold, check boxes disabled.
2) Hold per case = Reduce PO Readiness (case) per destination of a unit (TB_R_CROSSDOCK_CASE_HOLD): the last n warehouse cases
   (n x pcs/case) of the destination are held; Search does not take them and the unit is cut again without them; stored until released.
Both are set on D/S sub screens (13-Nov rev.): Hold per Supplier shows the open POs and the customer orders pre-mapped to them.
XD09 applies the reduction before the cut and sets CROSSDOCK_STATUS '8' (On Hold) for a supplier + plant on hold."""
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
          'description': 'New table: Reduce PO Readiness (case) per destination of a unit (Part Number + Customer Order Date + Destination + Supplier Code + Plant) set by the D/S team: the last REDUCE_CASE warehouse cases (REDUCE_CASE x pcs/case) of the destination are held. Kept until the D/S team releases it (row deleted). Name and columns proposed.',
          'columns': [['PART_NO', 'VARCHAR(15)', 'Y', 'N', 'Part number (H0253.SHIPPING_PART_NO)'],
                      ['ORDER_DT', 'DATE', 'Y', 'N', 'Customer Order Date of the unit'],
                      ['DESTINATION_CD', 'VARCHAR(7)', 'Y', 'N', 'Destination of the unit whose warehouse cases are held'],
                      ['SUPPLIER_CD', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier code of the unit'],
                      ['SUPPLIER_PLANT', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier plant of the unit'],
                      ['REDUCE_CASE', 'INT', '', 'N', 'Warehouse cases of the destination held (1 .. warehouse cases of the destination); held pcs = REDUCE_CASE x pcs/case, taken from the last lines of the destination in H0253 order']] + AUDIT}


def item(name, src, field, typ, io, control, desc, initial='-', fmt='-', valid='-', required='N', just='Left', length='-'):
    return {'name': name, 'source': src, 'field': field, 'type': typ, 'len': length, 'io': io, 'control': control, 'justified': just,
            'initial': initial, 'required': required, 'format': fmt, 'validation': valid, 'description': desc}


with open('XD10_spec.json') as fh:
    s = json.load(fh)

# ---------- screen layout ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04_ds_hold.png'))
sl[k + 1:k + 1] = [
    {'caption': '4a. D/S team: Reduce PO Readiness (case) per destination: Philippines 1 warehouse case held; its 6 pcs are not taken and the unit is cut again (4 cases, all Ready with the PO 24)', 'image': f'{IMG}/c_04b_ds_reduce.png'},
    {'caption': '4b. Supplier view of the reduced unit: 4 cases without the held Philippines pcs', 'image': f'{IMG}/c_04c_supplier_reduce.png'},
    {'caption': '4c. D/S team: sub screen Hold per Supplier Code + Plant: open POs of each supplier + plant and the customer orders pre-mapped to them', 'image': f'{IMG}/c_04d_ds_supplier_hold.png'},
    {'caption': '4d. Sub screen: supplier 50221 plant 1 put on hold (Hold Flag Y)', 'image': f'{IMG}/c_04f_ds_supplier_hold_on.png'},
    {'caption': '4e. Supplier view: its units stay visible, On Hold, check boxes disabled (message no. 12)', 'image': f'{IMG}/c_04e_supplier_on_hold.png'}]

# ---------- buttons ----------
g = s['general']
bi = next(i for i, b in enumerate(g['buttons']) if b['name'] == 'Hold / Release (D/S)')
g['buttons'][bi + 1:bi + 1] = [
    {'name': 'Hold per Supplier (D/S)', 'function': 'D/S team only: open the sub screen Hold per Supplier Code + Plant (open POs and the customer orders pre-mapped to them).'},
    {'name': 'Hold / Release Supplier (D/S)', 'function': "Sub screen, D/S team only: set HOLD_FLAG of a Supplier Code + Plant in TB_M_CROSSDOCK_SUPPLIER_HOLD to 'Y' (hold) or 'N' (release)."},
    {'name': 'Save Reduce (D/S)', 'function': 'Destination detail, D/S team only: save Reduce PO Readiness (case) of the destination in TB_R_CROSSDOCK_CASE_HOLD (0 / blank = release).'},
    {'name': 'Release Reduce (D/S)', 'function': 'Destination detail, D/S team only: delete the Reduce PO Readiness (case) of the destination: its pcs are taken again by Search.'}]
for m in g['screen_modes']:
    for sec in m['sections']:
        bt = sec.get('buttons')
        if isinstance(bt, dict) and 'Hold / Release (D/S)' in bt:
            v = bt['Hold / Release (D/S)']
            new = {}
            for kk, vv in bt.items():
                new[kk] = vv
                if kk == 'Hold / Release (D/S)':
                    new['Hold per Supplier (D/S)'] = v
                    new['Hold / Release Supplier (D/S)'] = v
                    new['Save Reduce (D/S)'] = v
                    new['Release Reduce (D/S)'] = v
            sec['buttons'] = new

# ---------- items ----------
it = s['items']
pr = next(x for x in it if x.get('name') == 'PO Readiness (case)')
pr['description'] = ('Cases whose whole qty is pre-mapped to a PO; red when lower than Case Qty. Pcs held by Reduce PO Readiness (case) of a destination are not counted '
                     '(the unit is cut again without them); the ASN Status shows "<n> warehouse case(s) on hold (reduce: <destination> <n>)" for the D/S team.')
it.append({'group': '<Sub Screen Hold per Supplier Code + Plant (D/S team only)>', 'description': ''})
it += [
    item('Supplier Code · Plant', 'TB_M_CROSSDOCK_SUPPLIER_HOLD / supplier master', 'SUPPLIER_CD / SUPPLIER_PLANT', 'Char', 'O', 'Label', 'One block per supplier + plant with crossdock parts; supplier name and number of open POs.'),
    item('Hold Flag (button)', '-', 'HOLD_FLAG', 'Button', 'I', 'Button', "'N · Hold' sets Y, 'Y · Release' sets N. While Y every unit of the supplier + plant is On Hold (check boxes disabled, message no. 12). Refer 5.3.",
         initial='N · Hold', just='Center'),
    item('PO No / Manifest No / Item / Part Number / PO Date', 'TB_R_PRA_DAILY_ORDER_MANIFEST / PART', 'PO_NO / MANIFEST_NO / MANIFEST_ITEM / PART_NO / PO_DT', 'Char', 'O', 'Grid',
         'Open crossdock POs of the supplier + plant (CROSS_DOCK_FLAG X, open PO qty > 0, released by today).'),
    item('PO Qty / Open Qty', 'TB_R_PRA_DAILY_ORDER_PART / TB_R_PRA_DAILY_ORDER_MAPPED', 'ORDER_QTY / ORDER_QTY - MAPPED_QTY', 'Number', 'O', 'Grid', 'PO qty and the qty not yet in an ASN.', just='Right'),
    item('Customer orders pre-mapped', '#TEMP_INSTRUCTION (XD09)', 'ORDER_DT / CUSTOMER_ORDER_NO / DESTINATION_CD / ASSIGNED_QTY / CASE_SEQ', 'Char', 'O', 'Grid',
         'Customer orders pre-mapped to the PO by the Search of today (Customer Order Date · Customer Order No · Destination · Qty · Case) = what the hold stops; "Not pre-mapped yet" when none.'),
    item('Back to ASN Crossdock Creation', '-', '-', '-', 'I', 'Button', 'Closes the sub screen.', initial='Enabled', just='Center')]
dd = next(i for i, x in enumerate(it) if x.get('group') == '<Destination Detail (D/S team only)>')
hb = next(i for i, x in enumerate(it) if x.get('name') == 'Hold / Release (D/S)')
it[hb + 1:hb + 1] = [
    item('Reduce PO Readiness (case)', 'Key-in / TB_R_CROSSDOCK_CASE_HOLD', 'REDUCE_CASE', 'Number', 'I', 'Text Box',
         'Per destination: number of warehouse cases of the destination to hold (n x pcs/case pcs from its last lines in H0253 order). Shown with "/ <warehouse cases>". Kept until released.',
         initial='Saved value / blank', fmt='ZZ9', valid='Whole number 0 .. warehouse cases of the destination (message no. 13)', just='Right'),
    item('Save (Reduce)', '-', '-', '-', 'I', 'Button', 'Saves the reduction of the destination (0 / blank = release). Refer 5.3.', initial='Enabled', just='Center'),
    item('Release (Reduce)', '-', '-', '-', 'I', 'Button', 'Deletes the reduction of the destination; shown when a reduction is saved. Refer 5.3.', initial='Enabled when saved', just='Center')]
sc = next(i for i, x in enumerate(it) if x.get('group') == '<Supplier Cases of a Unit (H0253 order)>')
for x in it[sc + 1:]:
    if 'group' in x:
        break
    if x.get('name') == 'PO Status':
        x['description'] = (x.get('description', '') + " 'On Hold (D/S)' (grey) when the supplier + plant is on hold; check box disabled (message no. 12).").strip()

# ---------- operation ----------
op = s['operation']
h = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.3'))
op[h + 1]['items'] += [
    'Hold per Supplier Code + Plant (decided 13-Nov): [Hold per Supplier] opens a D/S sub screen with one block per supplier + plant: Hold Flag button and the open crossdock POs '
    '(PO No, Manifest No, Item, Part Number, PO Date, PO Qty, Open Qty) with the customer orders pre-mapped to each PO by the Search of today (Customer Order Date, Customer Order No, Destination, Qty, Case). '
    'Hold sets HOLD_FLAG = Y in TB_M_CROSSDOCK_SUPPLIER_HOLD: every unit of the supplier + plant stays visible with status On Hold, check boxes disabled (message no. 12), until released.',
    'Hold per case = Reduce PO Readiness (case) per destination (decided 13-Nov): in the destination detail (D/S) each destination has an input "Reduce PO Readiness (case) / <warehouse cases>" with Save / Release. '
    'n = number of warehouse cases of the destination to hold: n x pcs/case pcs are taken from the last lines of the destination in H0253 order and are not taken by Search; '
    'the unit is cut again without them. Example: Philippines 6 pcs, reduce 1 -> its 6 pcs held; PART-X 17-Oct becomes 24 pcs = 4 cases, all Ready with the 24 pcs PO.',
    'The reduction is saved per unit and destination in TB_R_CROSSDOCK_CASE_HOLD and kept until the D/S team releases it (Release or 0). Input 0 .. warehouse cases of the destination, else message no. 13. '
    'A destination whose whole qty is held stays listed in the destination detail with qty 0 (+held qty).',
    'Both holds are re-checked at [Create ASN] like the destination hold: a hold made after the units were ticked makes the whole create fail (message no. 8) and the delivery plan is refreshed.']
h2 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.2'))
op[h2 + 1]['items'].append("On Hold also when the Supplier Code + Plant of the unit is on hold (5.3, CROSSDOCK_STATUS '8'). Pcs held by Reduce PO Readiness (case) are not in the cases at all (the unit is cut without them).")

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
                     'description': 'Reduce PO Readiness (case) of the destination: insert / update when > 0; delete when 0, blank or Release',
                     'keys': [{'field': 'PART_NO + ORDER_DT + DESTINATION_CD + SUPPLIER_CD + SUPPLIER_PLANT', 'value': 'Unit and destination of the row'}]},
     'mappings': [{'dest_field': 'PART_NO', 'description': 'Part number of the unit'}, {'dest_field': 'ORDER_DT', 'description': 'Customer Order Date of the unit'},
                  {'dest_field': 'DESTINATION_CD', 'description': 'Destination of the row'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the unit'},
                  {'dest_field': 'REDUCE_CASE', 'description': 'Input (1 .. warehouse cases of the destination)'},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]}]

# ---------- messages ----------
dm = s['display_messages']
m2 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG2')
dm[m2 + 1:m2 + 1] = [
    {'event': 'Hover on disabled check box', 'cause': 'Supplier Code + Plant on hold (D/S)', 'type': 'Info', 'msg_id': 'MSG12',
     'message': 'Supplier {Supplier Code} · Plant {Plant} is on hold by the D/S team', 'action': 'Contact the D/S team.'}]
dm.append({'event': 'Click [Save] (Reduce PO Readiness)', 'cause': 'Not a whole number or more than the warehouse cases of the destination', 'type': 'Error', 'msg_id': 'MSG13',
           'message': 'Reduce PO Readiness (case) must be a whole number from 0 to {n} (warehouse cases of the destination).', 'action': 'Correct the value.'})

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
    {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'type': 'DB', 'description': 'Reduce PO Readiness (case) per destination: warehouse cases (n x pcs/case) not taken'}]
fd = s['func_desc']
h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x.get('text', '').startswith('4.3'))
fd[h + 1]['items'] += [
    "Holds of the D/S team (XD10 5.3, decided 13-Nov): supplier + plant with HOLD_FLAG Y in TB_M_CROSSDOCK_SUPPLIER_HOLD -> every case of its units CROSSDOCK_STATUS '8' (On Hold).",
    'Reduce PO Readiness (case) per destination in TB_R_CROSSDOCK_CASE_HOLD (applied before the PO pouring and the cut): REDUCE_CASE x PCS_CASE pcs of the destination are taken off from its last lines in H0253 order '
    '(a line can be partly held); the rest is poured and cut as usual. Example 18-Oct: Philippines reduce 1 -> CO-14109 6 pcs held; 24 pcs = 4 cases, the 24 pcs PO covers all (CO-14110 Ready).']
for t in s['tables']:
    for c in t['columns']:
        if c[0] == 'CROSSDOCK_STATUS':
            c[4] = c[4].rstrip('.') + " / '8' On Hold (D/S: supplier + plant on hold)"
s['tables'] += [T_SUP, T_CASE]
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')
