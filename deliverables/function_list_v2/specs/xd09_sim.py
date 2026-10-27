"""XD09 Function Description and Sample Input written from the results of simulasi_asn_rev.xlsx (PART-X, 6 pcs/case, 16-20 Oct)."""
from scan_pack import pack

VN, TH, PH, D4 = '9715310', '9722D10', '9811110', '982220'
CU = {VN: '9715300', TH: '9722D10', PH: '9811100', D4: '982200'}
SH = {VN: 'VN', TH: 'TH', PH: 'PH', D4: '982220'}
MF = {f'T04090{n}': f'31260359{n}' for n in range(11, 17)}


def line(co, od, d, q):
    return dict(CUSTOMER_CD=CU[d], CUSTOMER_ORDER_NO=co, ORDER_DT=od, ORDER_TIME='080000', DESTINATION_CD=d, DETAILED_ITEM_NO='001',
                SERIAL_NO='0000001', PART_NO='PART-X', QTY=q)


O17 = [line('CO-14104', '2026-10-17', TH, 6), line('CO-14105', '2026-10-17', VN, 6), line('CO-14106', '2026-10-17', VN, 3),
       line('CO-14107', '2026-10-17', VN, 3), line('CO-14109', '2026-10-17', PH, 6), line('CO-14110', '2026-10-17', D4, 6)]
O18 = [line('CO-14112', '2026-10-18', VN, 6), line('CO-14113', '2026-10-18', PH, 6), line('CO-14114', '2026-10-18', D4, 6)]
O19 = [line('CO-14111', '2026-10-19', TH, 6), line('CO-14115', '2026-10-19', VN, 12)]
# [Search] of each day: (title, units, open PO qty in PO_DT order)
SEARCHES = [
    ('16-Oct: CO-14102 is on hold, only CO-14101 is taken; T0409011 keeps 6 pcs open', [[line('CO-14101', '2026-10-15', VN, 6)]], [('T0409011', 12)]),
    ('17-Oct: CO-14102 cancelled (UPD_STATUS 2); CO-14103 takes the rest of T0409011 (older PO date); T0409012 stays open', [[line('CO-14103', '2026-10-16', TH, 6)]],
     [('T0409011', 6), ('T0409012', 6)]),
    ('18-Oct: order date 17-Oct, 4 destinations, 30 pcs; PO 24 pcs (T0409012 rest 6 + T0409013 18): Short PO, case 5 Not Ready', [O17],
     [('T0409012', 6), ('T0409013', 18)]),
    ('19-Oct: rest of 17-Oct (CO-14104 cancelled, cases 1-4 in ASN0003) with the split PO T0409014, then order date 18-Oct', [[O17[-1]], O18],
     [('T0409014', 12), ('T0409015', 18)]),
    ('20-Oct: order date 19-Oct: CO-14115 12 pcs = 2 cases (one line in 2 ASNs), CO-14111', [O19], [('T0409015', 6), ('T0409016', 18)]),
]
COLS = ['Sort Seq', 'Order Date', 'Customer Code', 'Cust Order No', 'Dest', 'Open Qty', 'PO No', 'Assigned Qty', 'Case', 'Cum Dest Qty', 'Seq Qty', 'Cut', 'Status']
WIDTHS = [7, 10, 11, 12, 8, 8, 10, 10, 6, 10, 7, 5, 7]


def rows(units, pos):
    pos = [[p, MF[p], '0001', q] for p, q in pos]
    out = []
    for u in units:
        for s in pack(u, pos, 6):
            out.append([s['SORT_SEQ'], s['ORDER_DT'][8:] + '-Oct', s['CUSTOMER_CD'], s['CUSTOMER_ORDER_NO'], SH[s['DESTINATION_CD']], s['QTY'], s['PO_NO'] or '—',
                        s['ASSIGNED_QTY'], s['CASE_SEQ'], s['CUM_DEST_QTY'], s['SEQ_QTY'], s['CUT_FLAG'], 'Ready' if s['CROSSDOCK_STATUS'] == '6' else 'Not Ready'])
    return out


SAMPLE = {
    'title': 'Sample Input',
    'heading': 'Sample [Search] - simulasi_asn_rev.xlsx (PART-X, 6 pcs/case, 16-20 Oct)',
    'intro': [
        'Same data as simulasi_asn_rev.xlsx and the prototype (ASN Creation, business dates 16-20 Oct). One PO per Customer Order Date (PO date = order date + 1); '
        'the ASNs of the earlier days are already submitted (ASN0001 ... ASN0007).',
        'Each table = #TEMP_INSTRUCTION of one [Search]. Sort Seq and Case start again at 1 per unit (Part Number + Customer Order Date).',
    ],
    'sections': [{'title': f'{chr(65 + i)}. {t}', 'columns': COLS, 'widths': WIDTHS, 'rows': rows(u, p)} for i, (t, u, p) in enumerate(SEARCHES)] + [
        {'title': 'F. PO per Customer Order Date (PO date = order date + 1, qty = total order qty of all destinations)',
         'columns': ['Customer Order Date', 'Destinations', 'Total Order Qty', 'PO No', 'PO Date', 'PO Qty', 'Check', 'Split PO'], 'widths': [14, 10, 12, 10, 10, 8, 18, 18],
         'rows': [['15-Oct', 2, 12, 'T0409011', '16-Oct', 12, 'OK', '-'], ['16-Oct', 1, 6, 'T0409012', '17-Oct', 6, 'OK', '-'],
                  ['17-Oct', 4, 30, 'T0409013', '18-Oct', 18, 'Short PO (12 pcs)', 'T0409014 12 (19-Oct)'], ['18-Oct', 3, 18, 'T0409015', '19-Oct', 18, 'OK', '-'],
                  ['19-Oct', 2, 18, 'T0409016', '20-Oct', 18, 'OK', '-']]},
    ],
}

FUNC_DESC = [
    {'type': 'text', 'level': 0, 'text': 'XD09 runs on [Search] of XD10 and builds the delivery plan in #TEMP_INSTRUCTION. Nothing permanent is saved: '
                                        '[Create ASN] (XD10) writes TB_R_INSTRUCTION, PO_MAPPED_FLAG and MAPPED_QTY. Examples: simulasi_asn_rev.xlsx (sheet Sample Input).'},
    {'type': 'heading', 'text': '4.1 Customer Order Lines Taken'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The H0253 replicate has the lines of a Customer Order Date from the next day (XD08 run). A line is taken when ORDER_STATUS = 7, UPD_STATUS IS NULL, '
        'HOLD_FLAG = N and open qty > 0 (open qty = ORDER_STATUS_QTY - qty of the line in TB_R_INSTRUCTION).',
        'Not taken: a line on hold (CO-14102 on 16-Oct), a cancelled line (UPD_STATUS 2: CO-14102 from 17-Oct, CO-14104 from 19-Oct), a line received '
        'in GTOPAS (UPD_STATUS 6: CO-14111 on 21-Oct), the qty already in an ASN (CO-14115: open 6 after ASN0006, 0 after ASN0007).',
        'Order of the lines (ORDER BY): ORDER_DT (Allocation Priority), CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME, DESTINATION_CD, '
        'DETAILED_ITEM_NO, SERIAL_NO, per unit = Part Number + Customer Order Date, units of a part oldest date first. Example 18-Oct: CO-14105, CO-14106, '
        'CO-14107 (9715300), CO-14104 (9722D10), CO-14109 (9811100), CO-14110 (982200). SORT_SEQ = row number per unit.']},
    {'type': 'heading', 'text': '4.2 PO Assignment'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'One PO per Part Number per Customer Order Date: PO date = order date + 1, PO qty = total order qty of all destinations of that date. '
        'Open PO qty = ORDER_QTY - MAPPED_QTY.',
        'The open PO qty is given in PO date order (then PO No) to the lines in the order of 4.1, oldest unit first. A PO qty left by an order that is '
        'not sent goes to the next lines: T0409011 (CO-14102 on hold, then cancelled) covers CO-14103; T0409012 then covers CO-14105.',
        'PO qty lower than the order qty of the date (Short PO) is an abnormality: order date 17-Oct = 30 pcs, T0409013 = 18 pcs; the last 6 pcs '
        '(CO-14110) have no PO (PO_NO NULL) and wait for the split PO T0409014 of 19-Oct.']},
    {'type': 'column_break'},
    {'type': 'heading', 'text': '4.3 Supplier Cases and Cut'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'The pcs of a unit are cut into supplier cases of PCS_CASE pcs in the order of 4.1 (CASE_SEQ from 1 per unit). A case can hold several lines: '
        'case 2 of 17-Oct = CO-14106 3 + CO-14107 3. A line can be in several cases: CO-14115 12 pcs = cases 1 and 2.',
        'CUT_FLAG = Y after a case where the cumulative qty of every destination of the unit is a multiple of PCS_CASE (the warehouse packs 1 case = 1 destination); '
        'the ASN may stop only there. SEQ_QTY = fill of the warehouse case of the destination (1..PCS_CASE).',
        'A case is Ready (CROSSDOCK_STATUS 6) when it and every earlier case of the unit have a PO, else Not Ready (7). 18-Oct: cases 1-4 Ready, case 5 Not Ready '
        '→ unit Partially Ready, Short PO.']},
    {'type': 'heading', 'text': '4.4 Delivery Plan on XD10'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        'One row per unit with its cases (Case, Qty, Remaining Qty without PO, PO, status) and the PO check (order qty of the date vs PO qty). '
        'Units without a pre-mapped case and units fully in an ASN are not listed.',
        'Per Part Number the oldest Customer Order Date is sent first: on 19-Oct the cases of 18-Oct can be ticked only together with or after case 1 of '
        '17-Oct (CO-14110). A Not Ready case of an older date holds the later dates.',
        'After the receiving in GTOPAS XD08 sets UPD_STATUS 6 and the line is no longer taken; a partly received line is split into a new SERIAL_NO and '
        'each part stays with its ASN (CO-14115: serial 0000001 = ASN0006, serial 0000002 = ASN0007), so nothing is taken again.']},
]
