"""13-Nov: ASN Crossdock Creation (XD10) - D/S team holds (rev. 4)
1) Hold per Part Number (TB_R_CROSSDOCK_PART_HOLD) on the D/S sub screen [Hold per Part]: one row per Part Number with status,
   Hold check box and Edit / Save / Cancel; expanded to its customer orders (no PO information). A held part stays visible, On Hold,
   check boxes disabled, for every Customer Order Date.
2) Hold per case = check box Hold (D/S) next to PO Status (TB_R_CROSSDOCK_CASE_HOLD), changed with [Edit hold] / [Save] / [Cancel] at
   Part Number + Customer Order Date level (like Part List and Mapping): the held case and every later case of the unit are not Ready;
   the Ready part ends on the last valid cut before the first held case.
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
T_UNIT = {'name': 'TB_R_CROSSDOCK_PART_HOLD', 'kind': 'transaction', 'proposed': True,
          'description': 'New table: Part Number put on hold by the D/S team on ASN Crossdock Creation (sub screen Hold per Part). HOLD_FLAG Y = no ASN can be created for the part, whatever the Customer Order Date. Name and columns proposed.',
          'columns': [UNIT_KEY[0], UNIT_KEY[2], UNIT_KEY[3], ['HOLD_FLAG', 'CHAR(1)', '', 'N', "'Y' on hold / 'N' released (no row = 'N')"]] + AUDIT}
T_CASE = {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'kind': 'transaction', 'proposed': True,
          'description': 'New table: supplier case of a unit (Part Number + Customer Order Date + Supplier Code + Plant + case number) held by the D/S team with the Hold check box. The held case and every later case of the unit are not Ready (Ready part ends on the last valid cut before it). Row deleted when unticked. The hold follows its destination when cases move (FB-182). Name and columns proposed.',
          'columns': UNIT_KEY + [['CASE_SEQ', 'INT', 'Y', 'N', 'Case number of the unit (CASE_SEQ of #TEMP_INSTRUCTION, from 1 in H0253 order); updated when the hold moves (FB-182)'],
                                 ['DESTINATION_CD', 'VARCHAR(7)', '', 'N', 'Destination of the first customer order line of the held case: the hold stays on this destination when cases move'],
                                 ['CUST_ORDER_NO', 'VARCHAR(TBD)', '', 'N', 'Customer Order No of the first line of the held case']] + AUDIT}


def item(name, src, field, typ, io, control, desc, initial='-', fmt='-', valid='-', required='N', just='Left', length='-'):
    return {'name': name, 'source': src, 'field': field, 'type': typ, 'len': length, 'io': io, 'control': control, 'justified': just,
            'initial': initial, 'required': required, 'format': fmt, 'validation': valid, 'description': desc}


with open('XD10_spec.json') as fh:
    s = json.load(fh)

# ---------- screen layout ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04_ds_hold.png'))
sl[k + 1:k + 1] = [
    {'caption': '4a. D/S team: [Edit hold] on PART-X 17-Oct, Hold (D/S) of case 4 ticked, [Save] / [Cancel] shown; content split into Destination / Customer Order No / Order Qty', 'image': f'{IMG}/c_04a_ds_case_edit.png'},
    {'caption': '4b. After [Save]: PO Readiness 4 - 1 = Ready 3, case 4 On Hold (D/S) until changed again', 'image': f'{IMG}/c_04b_ds_reduce.png'},
    {'caption': '4c. Supplier view of the unit: case 4 On Hold (D/S), only cases 1-3 can be ticked', 'image': f'{IMG}/c_04c_supplier_reduce.png'},
    {'caption': '4d. D/S team: sub screen Hold per Part Number: one row per Part Number (status, Hold check box, [Edit]), expanded to its customer orders', 'image': f'{IMG}/c_04d_ds_supplier_hold.png'},
    {'caption': '4e. Sub screen: PART-X held ([Edit], tick Hold, [Save])', 'image': f'{IMG}/c_04f_ds_supplier_hold_on.png'},
    {'caption': '4f. Supplier view: the held part stays visible, On Hold, check boxes disabled (message no. 12)', 'image': f'{IMG}/c_04e_supplier_on_hold.png'}]

# ---------- buttons ----------
g = s['general']
bi = next(i for i, b in enumerate(g['buttons']) if b['name'] == 'Hold / Release (D/S)')
NEWB = [
    {'name': 'Hold per Part (D/S)', 'function': 'D/S team only: open the sub screen Hold per Part Number (one row per part, expanded to its customer orders).'},
    {'name': 'Edit / Save / Cancel (part, sub screen)', 'function': "Sub screen, D/S team only: [Edit] enables the Hold check box of the part; [Save] writes HOLD_FLAG 'Y' / 'N' in TB_R_CROSSDOCK_PART_HOLD; [Cancel] discards."},
    {'name': 'Edit hold / Save / Cancel (case, D/S)', 'function': 'Per Part Number + Customer Order Date, D/S team only: [Edit hold] enables the Hold (D/S) check boxes of its cases; [Save] writes TB_R_CROSSDOCK_CASE_HOLD (ticked = insert, unticked = delete); [Cancel] discards.'}]
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
         'D/S team only, next to PO Status: enabled after [Edit hold] of the unit; tick = hold the case; the held case and every later case of the unit are not Ready (Ready part ends on the last valid cut before the first held case). '
         'Saved with [Save], kept until changed; it stays on the same destination when cases move (refer 5.3). Disabled for a case without PO.', initial='Saved value (disabled)', just='Center'),
    item('Edit hold / Save / Cancel', '-', '-', '-', 'I', 'Button', 'D/S team only, per Part Number + Customer Order Date (right of the PO check): [Edit hold] enables the Hold (D/S) check boxes; [Save] stores them; [Cancel] discards. Not shown for a part on hold. Refer 5.3.',
         initial='Edit hold', just='Center')]
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
it.append({'group': '<Sub Screen Hold per Part Number (D/S team only)>', 'description': ''})
it += [
    item('Supplier Code · Plant', 'Supplier master', 'SUPPLIER_CD / SUPPLIER_PLANT', 'Char', 'O', 'Label', 'One section per supplier + plant: supplier name and number of part numbers.'),
    item('Part Number (row)', '#TEMP_INSTRUCTION (XD09)', 'PART_NO', 'Char', 'O', 'Label', 'One row per Part Number with open customer orders: number of customer orders, Customer Order Dates and pcs. Expand to see its customer orders.'),
    item('Hold status', 'TB_R_CROSSDOCK_PART_HOLD', 'HOLD_FLAG', 'Char', 'O', 'Label', "'On Hold' (row highlighted) / 'Not on hold'."),
    item('Hold (check box)', 'Key-in / TB_R_CROSSDOCK_PART_HOLD', 'HOLD_FLAG', 'Char', 'I', 'Check Box',
         'On the Part Number row; enabled after [Edit]. Saved with [Save]: Y = every customer order of the part (all Customer Order Dates) is On Hold (check boxes on the delivery plan disabled, message no. 12).',
         initial='Saved value (disabled)', just='Center'),
    item('Edit / Save / Cancel', '-', '-', '-', 'I', 'Button', '[Edit] enables the Hold check box of the part; [Save] stores it; [Cancel] discards. Refer 5.3.', initial='Edit', just='Center'),
    item('Customer Order Date / Customer Order No / Destination / Qty / Case', '#TEMP_INSTRUCTION (XD09)', 'ORDER_DT / CUSTOMER_ORDER_NO / DESTINATION_CD / ASSIGNED_QTY / CASE_SEQ', 'Char', 'O', 'Grid',
         'Expanded list: one row per customer order line of the part (all Customer Order Dates, oldest first, not grouped); no PO information.'),
    item('Back to ASN Crossdock Creation', '-', '-', '-', 'I', 'Button', 'Closes the sub screen.', initial='Enabled', just='Center')]

# ---------- operation ----------
op = s['operation']
h = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.3'))
op[h + 1]['items'] += [
    'Hold per Part Number (decided 13-Nov): [Hold per Part] opens a D/S sub screen with one section per supplier + plant and one row per Part Number (status, Hold check box, [Edit]). '
    '[Edit] enables the Hold check box, [Save] writes HOLD_FLAG in TB_R_CROSSDOCK_PART_HOLD, [Cancel] discards (same pattern as Part List and Mapping per Destination). '
    'Expanding a part lists its customer orders (Customer Order Date, Customer Order No, Destination, Qty, Case), not grouped by date, without PO information. '
    'A held part stays visible with status On Hold for every Customer Order Date, check boxes disabled (message no. 12), until saved as not on hold.',
    'Hold per case (decided 13-Nov): the case grid has a check box Hold (D/S) next to PO Status, changed with [Edit hold] / [Save] / [Cancel] of the Part Number + Customer Order Date. '
    'A held case and every later case of the unit are not Ready, '
    'and the Ready part ends on the last valid cut before the first held case (cases of the same block are held together). Example: PART-X 17-Oct, PO Readiness 4, case 4 ticked -> Ready 3, case 4 On Hold (D/S).',
    'The hold is saved per case in TB_R_CROSSDOCK_CASE_HOLD with [Save] and kept until changed again. Case numbers come from the Search (H0253 order). '
    'A hold is matched again to the cases at each Search (decided 13-Nov, FB-182), because cases move when an order is cancelled or earlier cases are sent: 1) the case that still has the saved Customer Order No + Destination; 2) else the case of the same Destination nearest to the saved case number (the lower one when equally near); 3) else (destination no longer in the unit) the case now at the saved case number, or the last case. The row is then updated to the matched case. No case left in the unit = the row is deleted. Example: case 4 = CO-14109 Taiwan held; CO-14104 cancelled -> the hold moves to case 3 (still CO-14109 Taiwan); CO-14109 cancelled and no other Taiwan line -> the hold stays on case 4 (now Australia). '
    'A held case shows PO Status On Hold (D/S) to the supplier too (message no. 14). The D/S team sees the content of each case in the columns Destination, Customer Order No and Order Qty.',
    'Both holds are re-checked at [Create ASN] like the destination hold: a hold made after the units were ticked makes the whole create fail (message no. 8) and the delivery plan is refreshed.']
h2 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.2'))
op[h2 + 1]['items'].append("On Hold also when the Part Number is on hold (5.3); cases held with the Hold check box are not Ready "
                           "(CROSSDOCK_STATUS '8' On Hold) and are not counted in PO Readiness.")

# ---------- data map ----------
s['data_map']['blocks'][1:1] = [
    {'source': '[Save] of the part (sub screen)',
     'destination': {'table': 'TB_R_CROSSDOCK_PART_HOLD', 'operation': 'Insert / Update', 'description': 'Part Number of the row (insert when no row yet)',
                     'keys': [{'field': 'PART_NO + SUPPLIER_CD + SUPPLIER_PLANT', 'value': 'Part of the row'}]},
     'mappings': [{'dest_field': 'PART_NO', 'description': 'Part number of the row'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the part'},
                  {'dest_field': 'HOLD_FLAG', 'description': "'Y' (hold) / 'N' (release)"},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]},
    {'source': '[Save] of Edit hold (cases of the unit)',
     'destination': {'table': 'TB_R_CROSSDOCK_CASE_HOLD', 'operation': 'Insert / Delete',
                     'description': 'Per case of the unit: ticked and not yet held = insert; unticked and held = delete',
                     'keys': [{'field': 'PART_NO + ORDER_DT + SUPPLIER_CD + SUPPLIER_PLANT + CASE_SEQ', 'value': 'Case of the check box'}]},
     'mappings': [{'dest_field': 'PART_NO / ORDER_DT', 'description': 'Part number and Customer Order Date of the unit'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the unit'},
                  {'dest_field': 'CASE_SEQ', 'description': 'Case number of the check box'},
                  {'dest_field': 'DESTINATION_CD / CUST_ORDER_NO', 'description': 'Destination and Customer Order No of the first line of the case'},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]}]

# ---------- messages ----------
dm = s['display_messages']
m2 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG2')
dm[m2 + 1:m2 + 1] = [
    {'event': 'Hover on disabled check box', 'cause': 'Part Number on hold (D/S)', 'type': 'Info', 'msg_id': 'MSG12',
     'message': '{Part No} is on hold by the D/S team', 'action': 'Contact the D/S team.'},
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
    {'name': 'TB_R_CROSSDOCK_PART_HOLD', 'type': 'DB', 'description': 'Part Number on hold (HOLD_FLAG Y): every case of its units On Hold'},
    {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'type': 'DB', 'description': 'Cases held by the D/S team: the first held case and later cases On Hold'}]
fd = s['func_desc']
h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x.get('text', '').startswith('4.3'))
fd[h + 1]['items'] += [
    "Holds of the D/S team (XD10 5.3, decided 13-Nov): a Part Number with HOLD_FLAG Y in TB_R_CROSSDOCK_PART_HOLD -> every case of its units CROSSDOCK_STATUS '8' (On Hold).",
    "Cases held in TB_R_CROSSDOCK_CASE_HOLD: Ready end = last valid cut before the first held CASE_SEQ of the unit; the Ready cases after it get CROSSDOCK_STATUS '8' (On Hold). "
    'Example: Ready 4, case 4 held -> cases 1-3 Ready, case 4 On Hold; if cases 3-4 belong together -> cases 1-2 Ready, cases 3-4 On Hold.',
    'Before this, each hold row is matched to the cases of the run (FB-182): same Customer Order No + Destination, else the same Destination nearest to CASE_SEQ, else the case at CASE_SEQ (or the last case); CASE_SEQ / DESTINATION_CD / CUST_ORDER_NO are updated to the matched case; no case left -> row deleted.']
for t in s['tables']:
    for c in t['columns']:
        if c[0] == 'CROSSDOCK_STATUS':
            c[4] = c[4].rstrip('.') + " / '8' On Hold (D/S: part on hold or case held)"
s['tables'] += [T_UNIT, T_CASE]
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')
