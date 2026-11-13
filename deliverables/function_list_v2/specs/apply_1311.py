"""13-Nov: ASN Crossdock Creation (XD10) - D/S team holds (rev. 3)
1) Hold per Part Number + Customer Order Date (TB_R_CROSSDOCK_UNIT_HOLD) on the D/S sub screen [Hold per Part]: each part + date with
   its POs and the customer orders pre-mapped to them; a held unit stays visible, On Hold, check boxes disabled.
2) Hold per case = check box Hold (D/S) next to PO Status (TB_R_CROSSDOCK_CASE_HOLD): the held case and every later case of the unit are
   not Ready; the Ready part ends on the last valid cut before the first held case; stored until the D/S team unticks it.
3) Content of a case split into the columns Destination, Customer Order No and Order Qty.
XD09 sets CROSSDOCK_STATUS '8' (On Hold) for both."""
import json

IMG = 'deliverables/uiss_screens/asn_crossdock'
AUDIT = [['CREATED_BY', 'VARCHAR(20)', '', 'N', 'Login user (D/S team) who created the record'],
         ['CREATED_DT', 'DATETIME', '', 'N', 'Created date and time'],
         ['CHANGED_BY', 'VARCHAR(20)', '', 'N', 'Login user (D/S team) who last changed the record'],
         ['CHANGED_DT', 'DATETIME', '', 'N', 'Last changed date and time']]
UNIT_KEY = [['PART_NO', 'VARCHAR(15)', 'Y', 'N', 'Part number (H0253.SHIPPING_PART_NO)'],
            ['ORDER_DT', 'DATE', 'Y', 'N', 'Customer Order Date of the unit'],
            ['SUPPLIER_CD', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier code of the unit'],
            ['SUPPLIER_PLANT', 'VARCHAR(TBD)', 'Y', 'N', 'Supplier plant of the unit']]
T_UNIT = {'name': 'TB_R_CROSSDOCK_UNIT_HOLD', 'kind': 'transaction', 'proposed': True,
          'description': 'New table: Part Number + Customer Order Date (unit) put on hold by the D/S team on ASN Crossdock Creation. HOLD_FLAG Y = no ASN can be created for the unit. Name and columns proposed.',
          'columns': UNIT_KEY + [['HOLD_FLAG', 'CHAR(1)', '', 'N', "'Y' on hold / 'N' released (no row = 'N')"]] + AUDIT}
T_CASE = {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'kind': 'transaction', 'proposed': True,
          'description': 'New table: supplier case of a unit (Part Number + Customer Order Date + Supplier Code + Plant + case number) held by the D/S team with the Hold check box. The held case and every later case of the unit are not Ready (Ready part ends on the last valid cut before it). Row deleted when unticked. Name and columns proposed.',
          'columns': UNIT_KEY + [['CASE_SEQ', 'INT', 'Y', 'N', 'Case number of the unit (CASE_SEQ of #TEMP_INSTRUCTION, from 1 in H0253 order)']] + AUDIT}


def item(name, src, field, typ, io, control, desc, initial='-', fmt='-', valid='-', required='N', just='Left', length='-'):
    return {'name': name, 'source': src, 'field': field, 'type': typ, 'len': length, 'io': io, 'control': control, 'justified': just,
            'initial': initial, 'required': required, 'format': fmt, 'validation': valid, 'description': desc}


with open('XD10_spec.json') as fh:
    s = json.load(fh)

# ---------- screen layout ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04_ds_hold.png'))
sl[k + 1:k + 1] = [
    {'caption': '4a. D/S team: Hold (D/S) ticked on case 4 of PART-X 17-Oct: PO Readiness 4 - 1 = Ready 3, case 4 On Hold (D/S) until unticked; content split into Destination / Customer Order No / Order Qty', 'image': f'{IMG}/c_04b_ds_reduce.png'},
    {'caption': '4b. Supplier view of the reduced unit: case 4 On Hold (D/S), only cases 1-3 can be ticked', 'image': f'{IMG}/c_04c_supplier_reduce.png'},
    {'caption': '4c. D/S team: sub screen Hold per Part Number + Customer Order Date: POs of each part + date and the customer orders pre-mapped to them', 'image': f'{IMG}/c_04d_ds_supplier_hold.png'},
    {'caption': '4d. Sub screen: PART-X 17-Oct put on hold (On Hold, [Release hold])', 'image': f'{IMG}/c_04f_ds_supplier_hold_on.png'},
    {'caption': '4e. Supplier view: the held part + date stays visible, On Hold, check boxes disabled (message no. 12)', 'image': f'{IMG}/c_04e_supplier_on_hold.png'}]

# ---------- buttons ----------
g = s['general']
bi = next(i for i, b in enumerate(g['buttons']) if b['name'] == 'Hold / Release (D/S)')
NEWB = [
    {'name': 'Hold per Part (D/S)', 'function': 'D/S team only: open the sub screen Hold per Part Number + Customer Order Date (POs and the customer orders pre-mapped to them).'},
    {'name': 'Hold / Release hold (D/S)', 'function': "Sub screen, D/S team only: set HOLD_FLAG of a Part Number + Customer Order Date in TB_R_CROSSDOCK_UNIT_HOLD to 'Y' (hold) or 'N' (release)."},
    {'name': 'Hold case (check box, D/S)', 'function': 'Case grid, D/S team only: tick = insert the case in TB_R_CROSSDOCK_CASE_HOLD (case and later cases not Ready); untick = delete it.'}]
g['buttons'][bi + 1:bi + 1] = NEWB
for m in g['screen_modes']:
    for sec in m['sections']:
        bt = sec.get('buttons')
        if isinstance(bt, dict) and 'Hold / Release (D/S)' in bt:
            v = bt['Hold / Release (D/S)']
            new = {}
            for kk, vv in bt.items():
                new[kk] = vv
                if kk == 'Hold / Release (D/S)':
                    for b in NEWB:
                        new[b['name']] = v
            sec['buttons'] = new

# ---------- items ----------
it = s['items']
pr = next(x for x in it if x.get('name') == 'PO Readiness (case)')
pr['description'] = ('Ready cases: cases whose whole qty is pre-mapped to a PO, minus the cases held by the D/S team (Hold check box, from the first held case; rounded down to the last valid cut); '
                     'red when lower than Case Qty. With a hold the original readiness is shown below, e.g. "4 - 1 on hold".')
sc = next(i for i, x in enumerate(it) if x.get('group') == '<Supplier Cases of a Unit (H0253 order)>')
ps = next(i for i, x in enumerate(it[sc:], sc) if x.get('name') == 'PO Status')
it[ps + 1:ps + 1] = [
    item('Hold (D/S)', 'Key-in / TB_R_CROSSDOCK_CASE_HOLD', 'CASE_SEQ', 'Char', 'I', 'Check Box',
         'D/S team only, next to PO Status: tick = hold the case; the held case and every later case of the unit are not Ready (Ready part ends on the last valid cut before the first held case). '
         'Kept until unticked. Disabled for a case without PO or a unit on hold.', initial='Saved value', just='Center')]
ct = next(i for i, x in enumerate(it[sc:], sc) if x.get('name', '').startswith('Content'))
base = it[ct]
it[ct:ct + 1] = [
    item('Destination (D/S team)', '#TEMP_INSTRUCTION', 'DESTINATION_CD', 'Char', 'O', 'Grid', 'D/S team only: destination code and name of each customer order line in the case, one per line.'),
    item('Customer Order No (D/S team)', '#TEMP_INSTRUCTION', 'CUSTOMER_ORDER_NO', 'Char', 'O', 'Grid', 'D/S team only: customer order of each line in the case, one per line.'),
    item('Order Qty (D/S team)', '#TEMP_INSTRUCTION', 'ASSIGNED_QTY', 'Number', 'O', 'Grid', 'D/S team only: pcs of each line in the case, one per line (sum = case qty).', just='Right')]
for x in it[sc + 1:]:
    if 'group' in x:
        break
    if x.get('name') == 'PO Status':
        x['description'] = (x.get('description', '') + " 'On Hold (D/S)' (grey) when the case is held (Hold check box) or the part + date is on hold; check box disabled (message no. 14 / 12).").strip()
it.append({'group': '<Sub Screen Hold per Part Number + Customer Order Date (D/S team only)>', 'description': ''})
it += [
    item('Supplier Code · Plant', 'Supplier master', 'SUPPLIER_CD / SUPPLIER_PLANT', 'Char', 'O', 'Label', 'One section per supplier + plant: supplier name and number of part + dates.'),
    item('Part Number / Customer Order Date', '#TEMP_INSTRUCTION (XD09)', 'PART_NO / ORDER_DT', 'Char', 'O', 'Label', 'One row per unit with open qty: cases, cases with PO, POs and pcs.'),
    item('Hold status', 'TB_R_CROSSDOCK_UNIT_HOLD', 'HOLD_FLAG', 'Char', 'O', 'Label', "'On Hold' (HOLD_FLAG Y, row highlighted) / 'Not on hold'."),
    item('Hold / Release hold', '-', 'HOLD_FLAG', 'Button', 'I', 'Button', "[Hold] sets HOLD_FLAG Y, [Release hold] sets N. While Y the unit is On Hold (check boxes disabled, message no. 12). Refer 5.3.",
         initial='Hold', just='Center'),
    item('PO No / Manifest / Item / PO Date / PO Qty / Open Qty', 'TB_R_PRA_DAILY_ORDER_MANIFEST / PART / MAPPED', 'PO_NO / MANIFEST_NO / MANIFEST_ITEM / PO_DT / ORDER_QTY / ORDER_QTY - MAPPED_QTY', 'Char', 'O', 'Grid',
         'POs pre-mapped to the unit by the Search of today; the PO cells span their customer order rows.'),
    item('Customer Order No / Destination / Qty / Case', '#TEMP_INSTRUCTION (XD09)', 'CUSTOMER_ORDER_NO / DESTINATION_CD / ASSIGNED_QTY / CASE_SEQ', 'Char', 'O', 'Grid',
         'Customer orders pre-mapped to the PO (= what the hold stops); qty without a PO is listed as "No PO yet (waiting for a PO)".'),
    item('Back to ASN Crossdock Creation', '-', '-', '-', 'I', 'Button', 'Closes the sub screen.', initial='Enabled', just='Center')]

# ---------- operation ----------
op = s['operation']
h = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.3'))
op[h + 1]['items'] += [
    'Hold per Part Number + Customer Order Date (decided 13-Nov): [Hold per Part] opens a D/S sub screen with one section per supplier + plant and one row per part + date: '
    'hold status, [Hold] / [Release hold], and the POs pre-mapped to the unit (PO No, Manifest No, Item, PO Date, PO Qty, Open Qty) with their customer orders (Customer Order No, Destination, Qty, Case). '
    'Hold sets HOLD_FLAG = Y in TB_R_CROSSDOCK_UNIT_HOLD: the unit stays visible with status On Hold, check boxes disabled (message no. 12), until released.',
    'Hold per case (decided 13-Nov): the case grid has a check box Hold (D/S) next to PO Status. Ticking a case holds it: the held case and every later case of the unit are not Ready, '
    'and the Ready part ends on the last valid cut before the first held case (cases of the same block are held together). Example: PART-X 17-Oct, PO Readiness 4, case 4 ticked -> Ready 3, case 4 On Hold (D/S).',
    'The hold is saved per case in TB_R_CROSSDOCK_CASE_HOLD and kept until the D/S team unticks it. Case numbers come from the Search (H0253 order), so a hold follows the case number of the unit. '
    'A held case shows PO Status On Hold (D/S) to the supplier too (message no. 14). The D/S team sees the content of each case in the columns Destination, Customer Order No and Order Qty.',
    'Both holds are re-checked at [Create ASN] like the destination hold: a hold made after the units were ticked makes the whole create fail (message no. 8) and the delivery plan is refreshed.']
h2 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.2'))
op[h2 + 1]['items'].append("On Hold also when the Part Number + Customer Order Date is on hold (5.3); cases held with the Hold check box are not Ready "
                           "(CROSSDOCK_STATUS '8' On Hold) and are not counted in PO Readiness.")

# ---------- data map ----------
s['data_map']['blocks'][1:1] = [
    {'source': 'Hold / Release hold (D/S)',
     'destination': {'table': 'TB_R_CROSSDOCK_UNIT_HOLD', 'operation': 'Insert / Update', 'description': 'Part Number + Customer Order Date of the button (insert when no row yet)',
                     'keys': [{'field': 'PART_NO + ORDER_DT + SUPPLIER_CD + SUPPLIER_PLANT', 'value': 'Unit of the row'}]},
     'mappings': [{'dest_field': 'PART_NO / ORDER_DT', 'description': 'Part number and Customer Order Date of the unit'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the unit'},
                  {'dest_field': 'HOLD_FLAG', 'description': "'Y' (hold) / 'N' (release)"},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]},
    {'source': 'Hold case (check box, D/S)',
     'destination': {'table': 'TB_R_CROSSDOCK_CASE_HOLD', 'operation': 'Insert / Delete',
                     'description': 'Tick: insert the case; untick: delete it',
                     'keys': [{'field': 'PART_NO + ORDER_DT + SUPPLIER_CD + SUPPLIER_PLANT + CASE_SEQ', 'value': 'Case of the check box'}]},
     'mappings': [{'dest_field': 'PART_NO / ORDER_DT', 'description': 'Part number and Customer Order Date of the unit'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the unit'},
                  {'dest_field': 'CASE_SEQ', 'description': 'Case number of the check box'},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]}]

# ---------- messages ----------
dm = s['display_messages']
m2 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG2')
dm[m2 + 1:m2 + 1] = [
    {'event': 'Hover on disabled check box', 'cause': 'Part Number + Customer Order Date on hold (D/S)', 'type': 'Info', 'msg_id': 'MSG12',
     'message': '{Part No} / {Customer Order Date} is on hold by the D/S team', 'action': 'Contact the D/S team.'},
    {'event': 'Hover on disabled case check box', 'cause': 'Case held by the D/S team (Hold check box)', 'type': 'Info', 'msg_id': 'MSG14',
     'message': 'On hold by the D/S team: case {n} of {Part No} / {Customer Order Date} (Hold per case)', 'action': 'Contact the D/S team.'}]

# ---------- tables ----------
s['tables'] += [T_UNIT, T_CASE]
with open('XD10_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD10_spec.json')

# ---------- XD09 ----------
with open('XD09_spec.json') as fh:
    s = json.load(fh)
s['general']['inputs'] += [
    {'name': 'TB_R_CROSSDOCK_UNIT_HOLD', 'type': 'DB', 'description': 'Part Number + Customer Order Date on hold (HOLD_FLAG Y): every case of the unit On Hold'},
    {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'type': 'DB', 'description': 'Cases held by the D/S team: the first held case and later cases On Hold'}]
fd = s['func_desc']
h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x.get('text', '').startswith('4.3'))
fd[h + 1]['items'] += [
    "Holds of the D/S team (XD10 5.3, decided 13-Nov): a unit with HOLD_FLAG Y in TB_R_CROSSDOCK_UNIT_HOLD -> every case CROSSDOCK_STATUS '8' (On Hold).",
    "Cases held in TB_R_CROSSDOCK_CASE_HOLD: Ready end = last valid cut before the first held CASE_SEQ of the unit; the Ready cases after it get CROSSDOCK_STATUS '8' (On Hold). "
    'Example: Ready 4, case 4 held -> cases 1-3 Ready, case 4 On Hold; if cases 3-4 belong together -> cases 1-2 Ready, cases 3-4 On Hold.']
for t in s['tables']:
    for c in t['columns']:
        if c[0] == 'CROSSDOCK_STATUS':
            c[4] = c[4].rstrip('.') + " / '8' On Hold (D/S: part + date on hold or case held)"
s['tables'] += [T_UNIT, T_CASE]
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')
