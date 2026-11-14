"""13-Nov: ASN Crossdock Creation (XD10) - D/S team holds (rev. 4)
1) Hold per Part Number (TB_R_CROSSDOCK_PART_HOLD) on the D/S sub screen [Hold per Part]: one row per Part Number with status,
   Hold check box and Edit / Save / Cancel; expanded to its customer orders (no PO information). A held part stays visible, On Hold,
   check boxes disabled, for every Customer Order Date.
2) Hold per case = check box Hold (D/S) next to PO Status (TB_R_CROSSDOCK_CASE_HOLD), changed with [Edit hold] / [Save] / [Cancel] at
   Part Number + Customer Order Date level (like Part List and Mapping). Rev. 5 (14-Nov): the pcs of the held case (its customer order
   lines) leave the unit before the PO pouring: they take no PO, the PO qty goes back to the next orders, the other cases keep their
   own readiness. The held lines are listed below the cases (On Hold) until released.
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
          'description': 'New table: customer order lines (pcs) of a supplier case held by the D/S team with the Hold check box (decided 14-Nov). The held pcs leave the unit before the PO pouring of XD09: they take no PO, the PO qty goes on to the next orders, the other cases stay Ready with their own PO. Row deleted when released (unticked). Name and columns proposed.',
          'columns': UNIT_KEY + [['CUSTOMER_CD', 'VARCHAR(TBD)', 'Y', 'N', 'Customer order line key (H0253)'],
                                 ['CUSTOMER_ORDER_NO', 'VARCHAR(TBD)', 'Y', 'N', 'Customer order line key (H0253)'],
                                 ['DESTINATION_CD', 'VARCHAR(7)', 'Y', 'N', 'Customer order line key (H0253)'],
                                 ['DETAILED_ITEM_NO', 'VARCHAR(TBD)', 'Y', 'N', 'Customer order line key (H0253)'],
                                 ['SERIAL_NO', 'VARCHAR(TBD)', 'Y', 'N', 'Customer order line key (H0253)'],
                                 ['HOLD_QTY', 'INT', '', 'N', 'Held pcs of the line (sum of the line pcs in the held cases); not more than the open qty of the line']] + AUDIT}


def item(name, src, field, typ, io, control, desc, initial='-', fmt='-', valid='-', required='N', just='Left', length='-'):
    return {'name': name, 'source': src, 'field': field, 'type': typ, 'len': length, 'io': io, 'control': control, 'justified': just,
            'initial': initial, 'required': required, 'format': fmt, 'validation': valid, 'description': desc}


with open('XD10_spec.json') as fh:
    s = json.load(fh)

# ---------- screen layout ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04_ds_hold.png'))
sl[k + 1:k + 1] = [
    {'caption': '4a. D/S team: [Edit hold] on PART-X 17-Oct, Hold (D/S) of case 4 (CO-14109 Taiwan) ticked, [Save] / [Cancel] shown; content split into Destination / Customer Order No / Order Qty', 'image': f'{IMG}/c_04a_ds_case_edit.png'},
    {'caption': '4b. After [Save]: CO-14109 Taiwan 6 pcs On Hold below the cases (PO released); its PO-0003 qty goes to CO-14110 Australia, so the 4 cases left are all Ready', 'image': f'{IMG}/c_04b_ds_reduce.png'},
    {'caption': '4c. Supplier view: cases 1-4 Ready, the held 6 pcs shown On Hold (D/S) and cannot be ticked', 'image': f'{IMG}/c_04c_supplier_reduce.png'},
    {'caption': '4d. D/S team: sub screen Hold per Part Number: one row per Part Number (status, Hold check box, [Edit]), expanded to its customer orders', 'image': f'{IMG}/c_04d_ds_supplier_hold.png'},
    {'caption': '4e. Sub screen: PART-X held ([Edit], tick Hold, [Save])', 'image': f'{IMG}/c_04f_ds_supplier_hold_on.png'},
    {'caption': '4f. Supplier view: the held part stays visible, On Hold, check boxes disabled (message no. 12)', 'image': f'{IMG}/c_04e_supplier_on_hold.png'}]

# ---------- buttons ----------
g = s['general']
bi = next(i for i, b in enumerate(g['buttons']) if b['name'] == 'Hold / Release (D/S)')
NEWB = [
    {'name': 'Hold per Part (D/S)', 'function': 'D/S team only: open the sub screen Hold per Part Number (one row per part, expanded to its customer orders).'},
    {'name': 'Edit / Save / Cancel (part, sub screen)', 'function': "Sub screen, D/S team only: [Edit] enables the Hold check box of the part; [Save] writes HOLD_FLAG 'Y' / 'N' in TB_R_CROSSDOCK_PART_HOLD; [Cancel] discards."},
    {'name': 'Edit hold / Save / Cancel (case, D/S)', 'function': 'Per Part Number + Customer Order Date, D/S team only: [Edit hold] enables the Hold (D/S) check boxes of its cases and of its held lines; [Save] writes TB_R_CROSSDOCK_CASE_HOLD (case ticked = its lines inserted / HOLD_QTY added, held line unticked = deleted); [Cancel] discards.'}]
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
pr['description'] = ('Ready cases: cases whose whole qty is pre-mapped to a PO; red when lower than Case Qty. '
                     'Pcs held by the D/S team (Hold per case) are not in the cases and not counted; the status shows "n pcs on hold (D/S), PO released".')
sc = next(i for i, x in enumerate(it) if x.get('group') == '<Supplier Cases of a Unit (H0253 order)>')
ps = next(i for i, x in enumerate(it[sc:], sc) if x.get('name') == 'PO Status')
it[ps + 1:ps + 1] = [
    item('Hold (D/S)', 'Key-in / TB_R_CROSSDOCK_CASE_HOLD', 'HOLD_QTY', 'Char', 'I', 'Check Box',
         'D/S team only, next to PO Status: enabled after [Edit hold] of the unit. Case row: tick = hold the case; after [Save] its pcs leave the unit (no PO) and are listed as held lines. '
         'Held line row (On Hold, ticked): untick = release; the pcs come back to the unit and take PO again at the next Search (refer 5.3).', initial='Unticked (case) / ticked (held line), disabled', just='Center'),
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
        x['description'] = (x.get('description', '') + " 'On Hold (D/S)' (grey) for a held line (Hold per case) or when the part is on hold; check box disabled (message no. 14 / 12).").strip()
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
    'Hold per case (decided 13-Nov, rev. 14-Nov): the case grid has a check box Hold (D/S) next to PO Status, changed with [Edit hold] / [Save] / [Cancel] of the Part Number + Customer Order Date. '
    '[Save] of a ticked case stores its customer order lines with their pcs (HOLD_QTY) in TB_R_CROSSDOCK_CASE_HOLD. At the next Search (XD09) the held pcs leave the unit before the PO pouring: '
    'they take no PO, so the PO qty they had goes on to the next lines of the part (same Customer Order Date, then the next dates). The other cases are cut again and keep their own readiness (no Ready end at the held case).',
    'Example: 18-Oct, PART-X 17-Oct, case 4 = CO-14109 Taiwan 6 pcs ticked -> Taiwan On Hold; PO-0003 6 pcs go to CO-14110 Australia (no PO before), so cases 1-4 (Korea, Korea, Japan, Australia) are all Ready. '
    'On 19-Oct the PO qty left after the 17-Oct lines goes to the 18-Oct orders.',
    'The held lines are listed below the cases (Case = On hold, PO = released, PO Status On Hold (D/S), message no. 14), for the supplier too, and cannot be ticked for an ASN. '
    'The hold is on the customer order line, so it does not move when other lines are cancelled or sent. Unticking a held line + [Save] deletes the row: the pcs come back to their place in the H0253 order and take PO at the next Search '
    '(they come first again, so PO not yet in an ASN can move back to them). A held line cancelled in GTOPAS -> row deleted. The D/S team sees the content of each case in the columns Destination, Customer Order No and Order Qty.',
    'Both holds are re-checked at [Create ASN] like the destination hold: a hold made after the units were ticked makes the whole create fail (message no. 8) and the delivery plan is refreshed.']
h2 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.2'))
op[h2 + 1]['items'].append("On Hold also when the Part Number is on hold (5.3). Pcs held with the Hold check box are not in the cases (On Hold, CROSSDOCK_STATUS '8') "
                           "and are not counted in PO Readiness; the other cases keep their own readiness.")

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
    {'source': '[Save] of Edit hold (cases and held lines of the unit)',
     'destination': {'table': 'TB_R_CROSSDOCK_CASE_HOLD', 'operation': 'Insert / Update / Delete',
                     'description': 'Ticked case: per customer order line in it, insert (or add its pcs to HOLD_QTY); unticked held line: delete',
                     'keys': [{'field': 'PART_NO + ORDER_DT + SUPPLIER_CD + SUPPLIER_PLANT + CUSTOMER_CD + CUSTOMER_ORDER_NO + DESTINATION_CD + DETAILED_ITEM_NO + SERIAL_NO', 'value': 'Customer order line in the case'}]},
     'mappings': [{'dest_field': 'PART_NO / ORDER_DT', 'description': 'Part number and Customer Order Date of the unit'},
                  {'dest_field': 'SUPPLIER_CD / SUPPLIER_PLANT', 'description': 'Supplier of the unit'},
                  {'dest_field': 'CUSTOMER_CD / CUSTOMER_ORDER_NO / DESTINATION_CD / DETAILED_ITEM_NO / SERIAL_NO', 'description': 'Customer order line in the ticked case (#TEMP_INSTRUCTION)'},
                  {'dest_field': 'HOLD_QTY', 'description': 'Pcs of the line in the ticked case (ASSIGNED_QTY), added when the line is already held'},
                  {'dest_field': 'CREATED_BY / CREATED_DT', 'description': 'Login user ID / server date-time (insert only)'},
                  {'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user ID / server date-time'}]}]

# ---------- messages ----------
dm = s['display_messages']
m2 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG2')
dm[m2 + 1:m2 + 1] = [
    {'event': 'Hover on disabled check box', 'cause': 'Part Number on hold (D/S)', 'type': 'Info', 'msg_id': 'MSG12',
     'message': '{Part No} is on hold by the D/S team', 'action': 'Contact the D/S team.'},
    {'event': 'Hover on a held line', 'cause': 'Customer order line held by the D/S team (Hold per case)', 'type': 'Info', 'msg_id': 'MSG14',
     'message': 'On hold by the D/S team: {Customer Order No} of {Part No} / {Customer Order Date}, {n} pcs; its PO qty is used by the next orders', 'action': 'Contact the D/S team.'}]

# ---------- 14-Nov: Save with confirmation + success + refresh; case grid with borders and merged cells ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04a_ds_case_edit.png'))
sl[k + 1:k + 1] = [
    {'caption': '4a-2. [Save]: confirmation (message no. 15) listing what is held / released', 'image': f'{IMG}/c_04g_ds_hold_confirm.png'},
    {'caption': '4a-3. [Yes, save]: saved message (message no. 16); the delivery plan is refreshed behind it', 'image': f'{IMG}/c_04h_ds_hold_saved.png'}]
for x in s['items']:
    n = x.get('name')
    if n == 'Edit hold / Save / Cancel':
        x['description'] = ('D/S team only, per Part Number + Customer Order Date (right of the PO check): [Edit hold] enables the Hold (D/S) check boxes; '
                            '[Save] asks for confirmation (message no. 15), stores the holds, shows message no. 16 and refreshes the delivery plan (the selection of the unit is cleared); '
                            '[Save] without a change just closes the edit; [Cancel] discards. Not shown for a part on hold. Refer 5.3.')
    elif n == 'Destination (D/S team)':
        x['description'] = 'D/S team only: destination code and name of the case, shown once per case (cell merged over its lines); a supplier case holds one destination.'
    elif n == 'Customer Order No (D/S team)':
        x['description'] = 'D/S team only: one row per customer order line in the case (the case-level cells are merged over these rows).'
    elif n == 'Order Qty (D/S team)':
        x['description'] = 'D/S team only: pcs of the line, one per row (sum = case qty).'
    elif n == 'PO':
        x['description'] = ('PO and assigned qty, e.g. PO-0003 · 6. Rows of the case with the same PO are merged into one cell; '
                            'supplier view: one row per PO of the case. Held line: "PO released".')
for b in s['general']['buttons']:
    if b.get('name') == 'Edit hold / Save / Cancel (case, D/S)':
        b['function'] += ' [Save] shows a confirmation (message no. 15) first, then message no. 16, and refreshes the delivery plan.'
op = s['operation']
h3 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.3'))
op[h3 + 1]['items'] += [
    'Saving a hold (case grid [Save] and sub screen [Save]): confirmation first (message no. 15, [No] keeps the edit open); [Yes, save] stores the change, '
    'shows message no. 16 and refreshes the delivery plan right away (Search again with the same Delivery Date / Rit, ticks of that unit cleared). No change = no message.',
    'Case grid: bordered cells. Case, Qty, Remaining Qty, Destination, PO Status and the check boxes are shown once per case (merged over its customer order lines); '
    'PO is merged over the lines of the same PO.']
dm = s['display_messages']
m14 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG14')
dm[m14 + 1:m14 + 1] = [
    {'event': 'Click [Save] of a hold (case grid or sub screen)', 'cause': 'Hold changed', 'type': 'Confirmation', 'msg_id': 'MSG15',
     'message': 'Hold of {Part No} / {Customer Order Date}? Save: hold case {n} ({Customer Order No}, {qty} pcs); release {Customer Order No} ({qty} pcs). Held pcs take no PO; their PO qty goes to the next orders.',
     'action': '[Yes, save] / [No]'},
    {'event': 'After [Yes, save]', 'cause': 'Hold saved', 'type': 'Info', 'msg_id': 'MSG16',
     'message': 'Hold of {Part No} / {Customer Order Date} saved. The delivery plan has been refreshed.', 'action': '[OK]'}]

# ---------- 14-Nov (b): PO check moved to an info pop up on the ASN status; bordered unit table; destination detail hidden ----------
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_02_delivery_plan.png'))
sl[k]['caption'] = ('2. Delivery plan after Search (supplier view, 18-Oct, simulasi_asn_rev.xlsx): PART-X 17-Oct, cases 1-4 Ready, case 5 Not Ready; '
                    'ASN Status Partially Ready + Short PO (click for the PO information)')
sl[k + 1:k + 1] = [{'caption': '2a. Click on the ASN status (Partially Ready / Short PO): PO information of the unit in Indonesian (message no. 17)', 'image': f'{IMG}/c_02a_po_info.png'}]
for x in sl:
    if x['image'].endswith(('c_03_ds_detail.png', 'c_04_ds_hold.png')):
        x['caption'] += ' [destination detail hidden on the screen for now, 14-Nov]'
for x in s['items']:
    n = x.get('name')
    if n == 'ASN Status':
        x['description'] += (' Partially Ready, Not Ready and Short PO are a button: a click opens the PO information of the unit (message no. 17): '
                             'customer order qty, regular / split PO with qty and date, Short PO and the qty still waiting, ready cases, pcs on hold. '
                             'The PO check line above the cases is no longer shown.')
    elif n == 'Edit hold / Save / Cancel':
        x['description'] = x['description'].replace('(right of the PO check)', '(above the cases, right side)')
for b in s['general']['buttons']:
    if b['name'] == 'Detail (expand, D/S)':
        b['function'] += ' Hidden on the screen for now (14-Nov, FB-184), with the destination Hold Flag; shown again on request.'
    if b['name'] == 'Hold / Release (D/S)':
        b['function'] += ' Hidden for now with the destination detail (FB-184).'
op = s['operation']
op[1]['items'][0] = ('18-Oct, delivery plan PART-X 17-Oct: 5 cases; order 30 pcs vs PO PO-0003 18 pcs -> Short PO (shown with the ASN status, details in the PO information pop up); '
                     'cases 1-4 Ready (PO-0002 rest 6 + PO-0003), case 5 (CO-14110) Not Ready with Remaining Qty 6.')
h3 = next(i for i, x in enumerate(op) if x.get('type') == 'heading' and x['text'].startswith('5.3'))
op[h3 + 1]['items'].append('Unit table and case grid: bordered cells (14-Nov). The destination detail with Hold Flag is hidden on the screen for now (FB-184).')
dm = s['display_messages']
m16 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG16')
dm[m16 + 1:m16 + 1] = [
    {'event': 'Click the ASN status (Partially Ready / Not Ready / Short PO)', 'cause': 'Not all cases have a PO, or PO qty < order qty', 'type': 'Info', 'msg_id': 'MSG17',
     'message': 'Info PO · {Part No} / {Customer Order Date}: Order customer tanggal {date}: {n} pcs (semua destinasi). PO reguler {PO No}: {qty} pcs, terbit {date}. '
                '[Split PO {PO No}: {qty} pcs, terbit {date}.] PO kurang dari order (Short PO): {n} pcs masih menunggu split PO. '
                '{a} dari {b} case sudah dapat PO dan siap dikirim; case lainnya menunggu PO. [{n} pcs di-hold tim D/S; PO-nya dipakai order berikutnya.]',
     'action': '[OK]'}]

# ---------- 14-Nov (c): Hold chip with hold information; plan summary line removed; save pop ups in Indonesian ----------
txt = json.dumps(s, ensure_ascii=False).replace('[Yes, save]', '[Ya, simpan]').replace('[No] keeps the edit open', '[Tidak] keeps the edit open')
s = json.loads(txt)
sl = s['screen_layout']
k = next(i for i, x in enumerate(sl) if x['image'].endswith('c_04b_ds_reduce.png'))
sl[k + 1:k + 1] = [{'caption': '4b-2. Click on the Hold chip next to the status: hold information of the unit in Indonesian (message no. 18)', 'image': f'{IMG}/c_04i_hold_info.png'}]
for x in s['items']:
    n = x.get('name')
    if n == 'PO Readiness (case)':
        x['description'] = ('Ready cases: cases whose whole qty is pre-mapped to a PO; red when lower than Case Qty. '
                            'Pcs held by the D/S team (Hold per case) are not in the cases and not counted (see the Hold chip of ASN Status).')
    elif n == 'ASN Status':
        x['description'] += (' A Hold chip (grey button) is shown next to the status when the unit has a hold (Part Number on hold, pcs held per case, '
                             'or a destination on hold for the D/S team); a click opens the hold information (message no. 18). '
                             'The text lines under the status (pcs on hold, Part Number on hold, destinations on hold) are no longer shown.')
op = s['operation']
op[3]['items'][2] += ' The heading shows only "Delivery plan" (no summary line with date, Rit, route, number of units and refresh time; decided 14-Nov).'
dm = s['display_messages']
for m in dm:
    if m.get('msg_id') == 'MSG15':
        m['message'] = ('Simpan hold {Part No} / {Customer Order Date}? Yang disimpan: hold case {n} ({Customer Order No}, {qty} pcs); lepas hold {Customer Order No} ({qty} pcs). '
                        'Pcs yang di-hold tidak dapat PO; PO-nya dipakai order berikutnya. '
                        '(Sub screen: Simpan hold {Part No}? {Part No} di-hold: belum bisa dibuat ASN untuk semua Customer Order Date sampai hold dilepas. / Hold {Part No} dilepas: case-nya bisa dikirim lagi.)')
        m['action'] = '[Ya, simpan] / [Tidak]'
    if m.get('msg_id') == 'MSG16':
        m['message'] = 'Tersimpan: Hold {Part No} / {Customer Order Date} sudah disimpan. Delivery plan sudah di-refresh.'
m17 = next(i for i, x in enumerate(dm) if x.get('msg_id') == 'MSG17')
dm[m17 + 1:m17 + 1] = [
    {'event': 'Click the Hold chip next to the ASN status', 'cause': 'The unit has a hold', 'type': 'Info', 'msg_id': 'MSG18',
     'message': 'Info hold · {Part No} / {Customer Order Date}: [Part Number {Part No} di-hold tim D/S: belum bisa dibuat ASN untuk semua Customer Order Date.] '
                '[{n} pcs di-hold tim D/S, PO-nya dilepas dan dipakai order berikutnya. {Customer Order No} · {Destination} (D/S team): {qty} pcs] '
                '[{n} destinasi di-hold (Hold Flag Y). (D/S team)]',
     'action': '[OK]'}]

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
    {'name': 'TB_R_CROSSDOCK_CASE_HOLD', 'type': 'DB', 'description': 'Customer order lines (HOLD_QTY pcs) held by the D/S team: taken out before the PO pouring'}]
fd = s['func_desc']
h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x.get('text', '').startswith('4.3'))
fd[h + 1]['items'] += [
    "Holds of the D/S team (XD10 5.3, decided 13-Nov): a Part Number with HOLD_FLAG Y in TB_R_CROSSDOCK_PART_HOLD -> every case of its units CROSSDOCK_STATUS '8' (On Hold).",
    "Lines held in TB_R_CROSSDOCK_CASE_HOLD (decided 14-Nov): HOLD_QTY pcs of the line are taken out of the open qty BEFORE the PO pouring (4.2) and the case cut: "
    "they take no PO, the PO qty goes on to the next lines of the part (same date, then the next Customer Order Dates); the held pcs are written with PO_NO NULL and CROSSDOCK_STATUS '8' (On Hold). "
    'The other cases are cut from the rest and keep their own readiness. Example 18-Oct: CO-14109 Taiwan 6 held -> PO-0003 6 goes to CO-14110 Australia; PART-X 17-Oct = 4 cases, all Ready.',
    'Held line no longer open (cancelled in GTOPAS or open qty 0) -> row deleted; HOLD_QTY > open qty -> only the open qty is held.']
pp = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x.get('text', '').startswith('4.2'))
fd[pp + 1]['items'].append('Pcs held by the D/S team (TB_R_CROSSDOCK_CASE_HOLD, 4.3) are not poured: the PO qty goes on to the next lines.')
for t in s['tables']:
    for c in t['columns']:
        if c[0] == 'CROSSDOCK_STATUS':
            c[4] = c[4].rstrip('.') + " / '8' On Hold (D/S: part on hold or case held)"
s['tables'] += [T_UNIT, T_CASE]
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')
