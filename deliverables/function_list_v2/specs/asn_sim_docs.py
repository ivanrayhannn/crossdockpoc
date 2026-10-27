"""UISS content of the ASN functions (XD08, XD10, XD11, XD15) written from the results of simulasi_asn_rev.xlsx (decided 27-Oct).
PART-X, 6 pcs/case, supplier 50221-1, 16-22 Oct; same data as the prototype (ASN Creation, ASN Simulation)."""

SRC = 'simulasi_asn_rev.xlsx'

# ---------------- XD08 ----------------
XD08_EXAMPLE = (f"Example ({SRC}, sheet Sample Input): 17-Oct CO-14101 → UPD_STATUS 6, CO-14102 (on hold, no ASN) → UPD_STATUS 2: nothing else; "
                "19-Oct CO-14104 → UPD_STATUS 2 although in case 3 of ASN0003 → LOG5, listed in XD11; 21-Oct CO-14111 → UPD_STATUS 6 without ASN "
                "(candidate) and CO-14115 (12 pcs in ASN0006 + ASN0007) split by G-System into serial 0000001 6 pcs (6) and 0000002 6 pcs (7): "
                "the ASN0007 row moves to serial 0000002 (LOG7).")
XD08_SAMPLE = {
    'title': 'Sample Input',
    'heading': f'Sample XD08 runs - {SRC} (PART-X, 16-22 Oct)',
    'intro': ['Rows of TB_R_H0253_ORDER_CONTROL_PRE (DB Surrounding) changed since the last run and the result in the NSP replicate. '
              'ORDER_STATUS of NSP keeps the first value (7); the change is written to UPD_STATUS. No draft is open at 03:30 in this data '
              '(drafts would be released by every run).'],
    'sections': [
        {'title': 'A. Runs (03:30) and result',
         'columns': ['Run', 'Source change (G-System)', 'NSP replicate', 'TB_R_INSTRUCTION / Log'], 'widths': [8, 40, 46, 40],
         'rows': [
             ['16-Oct', 'Order date 15-Oct: CO-14101 VN 6, CO-14102 TH 6 (status 7)', 'Insert; UPD_STATUS NULL, HOLD_FLAG N, PO_MAPPED_FLAG N', '-'],
             ['17-Oct', 'CO-14101 → 6, CO-14102 → 2; order date 16-Oct: CO-14103 TH 6', 'CO-14101 UPD_STATUS 6; CO-14102 UPD_STATUS 2 (PO_MAPPED_FLAG stays N); CO-14103 insert', 'CO-14102 has no ASN: nothing else'],
             ['18-Oct', 'CO-14103 → 6; order date 17-Oct: CO-14104 TH 6, CO-14105 VN 6, CO-14106 VN 3, CO-14107 VN 3, CO-14109 PH 6, CO-14110 982220 6',
              'CO-14103 UPD_STATUS 6; 6 lines insert', '-'],
             ['19-Oct', 'CO-14105 / 06 / 07 / 09 → 6 (ASN0003 received), CO-14104 → 2; order date 18-Oct: CO-14112 VN, CO-14113 PH, CO-14114 982220',
              'UPD_STATUS 6 / 2; 3 lines insert', 'CO-14104 is in ASN0003 case 3: LOG5, listed in XD11 (waiting for a candidate)'],
             ['20-Oct', 'CO-14110, CO-14112 / 13 / 14 → 6; order date 19-Oct: CO-14111 TH 6, CO-14115 VN 12', 'UPD_STATUS 6; 2 lines insert', '-'],
             ['21-Oct', 'CO-14111 → 6 (pcs of ASN0003 case 3); CO-14115 serial 0000001 → 6 qty 6 + new serial 0000002 qty 6 status 7',
              'CO-14111 UPD_STATUS 6 (candidate in XD11); CO-14115/0000001 qty 12 → 6, UPD_STATUS 6; CO-14115/0000002 insert, PO_MAPPED_FLAG Y',
              'Serial split: the ASN0007 row moves to serial 0000002 (ASN0006 stays on 0000001); LOG7'],
             ['22-Oct', 'CO-14115/0000002 → 6 (ASN0007 received)', 'UPD_STATUS 6', '-']]},
        {'title': 'B. Serial split of CO-14115 (one line in 2 ASNs) - TB_R_INSTRUCTION',
         'columns': ['INSTRUCTION_ID', 'Customer Order', 'Serial No before', 'Serial No after', 'Qty', 'PO', 'ASN_NO'], 'widths': [12, 14, 14, 14, 6, 10, 10],
         'rows': [[12, 'CO-14115', '0000001', '0000001', 6, 'T0409015', 'ASN0006'], [13, 'CO-14115', '0000001', '0000002', 6, 'T0409016', 'ASN0007']]},
    ],
}

# ---------------- XD10 ----------------
XD10_RULES = [
    {'type': 'heading', 'text': f'5.0 Behaviour shown by the simulation ({SRC})'},
    {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
        '18-Oct, delivery plan PART-X 17-Oct: 5 cases; PO check order 30 pcs vs PO T0409013 18 pcs → Short PO; cases 1-4 Ready (T0409012 rest 6 + T0409013), '
        'case 5 (CO-14110) Not Ready with Remaining Qty 6.',
        'The selection starts at case 1 and ends on a case with CUT_FLAG Y: ticking case 3 selects cases 1-3; case 5 is disabled. '
        'Per Part Number the oldest Customer Order Date first: on 19-Oct the cases of 18-Oct show "Wait: 17-Oct first" until case 1 of 17-Oct (CO-14110) is ticked.',
        '[Create ASN] with cases 1-4: 5 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y on the 5 lines that are complete (CO-14110 stays N), MAPPED_QTY T0409012 6, '
        'T0409013 18. [Submit ASN] gives ASN0003 with case numbers C-0003-01 … 04; only case 5 stays in the delivery plan.',
        'One line in two ASNs: CO-14115 12 pcs = case 1 (ASN0006, PO_MAPPED_FLAG N, open 6) and case 2 (ASN0007, PO_MAPPED_FLAG Y).',
        'D/S hold of Thailand (CO-14104) after the supplier ticked the unit: [Create ASN] fails (MSG8); the cases are computed again without Thailand. '
        'A draft not submitted is released by the next XD08 run ([Submit ASN] of the old draft: MSG11). A cancel after the ASN goes to XD11 '
        '(CO-14104 in ASN0003 case 3 → CO-14111).']},
]
XD10_OP_FIX = {
    '(e.g. VN 10, TH 6, VN 14: blocks case 1 | cases 2-3 | case 4 | case 5)': '(e.g. 18-Oct PART-X 17-Oct: every case ends on a cut, blocks case 1 | 2 | 3 | 4 | 5)',
    'Example: cases 2-3 belong together (D/S view: case 2 = VN 4 + TH 2) -> ticking case 2 gives cases 1-3; cases 1-2 alone are not possible.':
        'Example (18-Oct, PART-X 17-Oct): ticking case 3 gives cases 1-3; case 5 (no PO) cannot be ticked. When a case does not end on a cut '
        '(e.g. a case with VN 4 + TH 2), the cases up to the next cut are ticked with it.',
}
XD10_ITEM_FIX = {'e.g. VN 4 (V01) + TH 2 (T01).': 'e.g. VN 3 (CO-14106) + VN 3 (CO-14107).', 'e.g. PO-DMY-09021 2.': 'e.g. T0409013 6.'}
XD10_CASE_SECTIONS = [
    {'title': 'H. Case selection on 18-Oct (supplier view, PART-X 17-Oct): one check box per supplier case; Content shown to the D/S team only',
     'columns': ['Case', 'Qty', 'Remaining Qty (not assigned)', 'Content (D/S team only)', 'PO', 'CUT_FLAG', 'PO Status'], 'widths': [6, 6, 14, 30, 16, 8, 10],
     'rows': [['Case 1', 6, 0, 'VN 6 (CO-14105)', 'T0409012 6', 'Y', 'Ready'], ['Case 2', 6, 0, 'VN 3 (CO-14106) + VN 3 (CO-14107)', 'T0409013 6', 'Y', 'Ready'],
              ['Case 3', 6, 0, 'TH 6 (CO-14104)', 'T0409013 6', 'Y', 'Ready'], ['Case 4', 6, 0, 'PH 6 (CO-14109)', 'T0409013 6', 'Y', 'Ready'],
              ['Case 5', 6, 6, '982220 6 (CO-14110)', '—', 'Y', 'Not Ready']]},
    {'title': 'I. Check box scenarios (simulation)', 'columns': ['No', 'User action', 'Ticked cases', 'Result'], 'widths': [6, 34, 14, 66],
     'rows': [['C1', '18-Oct: tick case 1', '1', 'ASN 6 pcs.'],
              ['C2', '18-Oct: tick case 3', '1-3', 'Cases 1-2 are ticked too (the selection starts at case 1); ASN 18 pcs.'],
              ['C3', '18-Oct: tick the unit check box', '1-4', 'All Ready cases; case 5 (Not Ready) is not ticked; ASN 24 pcs = ASN0003.'],
              ['C4', 'From 1-4, untick case 2', '1', 'Cases 2-4 are unticked; back to case 1.'],
              ['C5', 'Case 5 (no PO)', '-', 'Disabled; tooltip message no. 2; Ready on 19-Oct with the split PO T0409014.'],
              ['C6', '19-Oct: tick case 1 of 18-Oct first', '-', 'Disabled (Wait: 17-Oct first); after case 1 of 17-Oct is ticked the cases of 18-Oct can be ticked.'],
              ['C7', 'Cases without a cut in between (message no. 10)', '-', 'Not in this data: every case of PART-X ends on a cut. When a case does not end on a cut, '
               'the next cases up to the cut are ticked together (MSG10).']]},
]

# ---------------- XD11 ----------------
XD11_CAPTION = ('1. List Mode: ASN0003 (CO-14104 cancelled after the ASN, candidate CO-14111), ASN00020 (partial cancel of CO-B, ERD SIM-6), '
                'ASN00031 (waiting for a candidate)')
XD11_SAMPLE = {
    'title': 'Sample Input',
    'heading': f'Sample Change Order Number - {SRC} (ASN0003, 21-Oct)',
    'intro': ['18-Oct: cases 1-4 of PART-X 17-Oct in ASN0003. 19-Oct: CO-14104 (TH 6, case 3) is cancelled in G-System (UPD_STATUS 2, LOG5): listed, waiting for a candidate. '
              '21-Oct: CO-14111 (TH 6, order date 19-Oct) is received in G-System with the pcs of case 3 (UPD_STATUS 6, PO_MAPPED_FLAG N, no ASN): candidate.'],
    'sections': [
        {'title': 'A. List and detail', 'columns': ['ASN No', 'Part', 'Cancelled order', 'Cancelled qty', 'Cases (from the last case)', 'Candidate', 'Status'],
         'widths': [10, 8, 16, 10, 18, 26, 18],
         'rows': [['ASN0003', 'PART-X', 'CO-14104 / 0000001', 6, 'C-0003-03: 6', 'CO-14111 TH 6 (19-Oct)', 'Candidate available']]},
        {'title': 'B. TB_R_INSTRUCTION (same row updated; case, PO and ASN not changed)',
         'columns': ['INSTRUCTION_ID', 'CASE_NO', 'Customer Order before', 'Customer Order after', 'Destination', 'Qty', 'PO', 'ASN_NO'], 'widths': [12, 11, 16, 16, 10, 6, 10, 9],
         'rows': [[6, 'C-0003-03', 'CO-14104', 'CO-14111', '9722D10', 6, 'T0409013', 'ASN0003']]},
        {'title': 'C. Other tables', 'columns': ['Table', 'Key', 'Column', 'Before', 'After'], 'widths': [26, 26, 16, 10, 10],
         'rows': [['TB_R_H0253_ORDER_CONTROL_PRE', 'CO-14111 / 0000001', 'PO_MAPPED_FLAG', 'N', 'Y'],
                  ['TB_R_H0253_ORDER_CONTROL_PRE', 'CO-14104 / 0000001', 'PO_MAPPED_FLAG', 'Y', 'Y (not changed)'],
                  ['TB_H_CROSSDOCK_ORDER_CHANGE', 'HIST_ID 1', '(new row)', '-', 'ASN0003, C-0003-03, CO-14104 → CO-14111, 6, instruction 6 → 6']]},
        {'title': 'D. Scenarios', 'columns': ['No', 'Scenario', 'Expected result'], 'widths': [6, 40, 70],
         'rows': [['N1', '19-Oct: CO-14104 cancelled, no candidate yet', 'Row listed with status Waiting for a candidate (no time limit).'],
                  ['N2', '21-Oct: tick CO-14111 and click [Change Order Number] → Yes', 'Sections B and C; the row leaves the list.'],
                  ['N3', 'Partial cancel (ERD SIM-6): CO-B 6 of 8 pcs in ASN00020', 'Moved from the last case backwards: case 2 4 pcs → CO-E, 2 of the 4 pcs of case 1 → CO-F (row split).'],
                  ['E1', 'The candidate was taken in another session', 'MSG4; nothing is saved; candidates refreshed.']]},
    ],
}

# ---------------- XD15 ----------------
XD15_SAMPLE = {
    'title': 'Sample Input',
    'heading': f'Sample ASN Crossdock Inquiry - {SRC} (supplier 50221-1)',
    'intro': ['ASNs of the simulation after 22-Oct (the prototype shows the ASNs created before the business date). Case numbers as in the prototype; '
              'the real format follows the existing numbering.'],
    'sections': [
        {'title': 'A. List Mode', 'columns': ['ASN No', 'Delivery Date', 'Rit · Route', 'Part / Customer Order Date', 'Cases', 'Qty', 'Status'], 'widths': [10, 12, 12, 26, 7, 6, 9],
         'rows': [['ASN0001', '16-Oct-2026', 'Rit 1 · SD01', 'PART-X / 15-Oct', 1, 6, 'Created'], ['ASN0002', '17-Oct-2026', 'Rit 1 · SD01', 'PART-X / 16-Oct', 1, 6, 'Created'],
                  ['ASN0003', '18-Oct-2026', 'Rit 1 · SD01', 'PART-X / 17-Oct', 4, 24, 'Created'], ['ASN0004', '19-Oct-2026', 'Rit 1 · SD01', 'PART-X / 17-Oct', 1, 6, 'Created'],
                  ['ASN0005', '19-Oct-2026', 'Rit 1 · SD01', 'PART-X / 18-Oct', 3, 18, 'Created'], ['ASN0006', '20-Oct-2026', 'Rit 1 · SD01', 'PART-X / 19-Oct', 1, 6, 'Created'],
                  ['ASN0007', '20-Oct-2026', 'Rit 2 · SD02', 'PART-X / 19-Oct', 1, 6, 'Created']]},
        {'title': 'B. Detail Mode of ASN0003 (after Change Order Number of 21-Oct)', 'columns': ['Case No', 'Part', 'Customer Order Date', 'Destination', 'Customer Order No', 'Qty', 'PO No'],
         'widths': [11, 8, 14, 12, 26, 6, 10],
         'rows': [['C-0003-01', 'PART-X', '17-Oct-2026', '9715310', 'CO-14105', 6, 'T0409012'], ['C-0003-02', 'PART-X', '17-Oct-2026', '9715310', 'CO-14106 3 + CO-14107 3', 6, 'T0409013'],
                  ['C-0003-03', 'PART-X', '17-Oct-2026', '9722D10', 'CO-14111 (was CO-14104)', 6, 'T0409013'], ['C-0003-04', 'PART-X', '17-Oct-2026', '9811110', 'CO-14109', 6, 'T0409013']]},
    ],
}
