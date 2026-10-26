"""Sheet Sample Input of XD10: [Create ASN] of simulasi_asn_rev.xlsx on 18-Oct-2026 (PART-X 17-Oct, cases 1-4 → ASN0003)."""
from scan_pack import pack

D, DT, RIT = '17-Oct-2026', '18-Oct-2026', 'Rit 1 · SD01'
NAME = {'9715310': '9715310 (Vietnam)', '9722D10': '9722D10 (Thailand)', '9811110': '9811110 (Philippines)', '982220': '982220'}
CUST = {'9715310': '9715300', '9722D10': '9722D10', '9811110': '9811100', '982220': '982200'}
MF = {'T0409012': '3126035912', 'T0409013': '3126035913'}
LINES = [dict(CUSTOMER_CD=CUST[d], CUSTOMER_ORDER_NO=co, ORDER_DT='2026-10-17', ORDER_TIME='080000', DESTINATION_CD=d, DETAILED_ITEM_NO='001',
              SERIAL_NO='0000001', PART_NO='PART-X', QTY=q)
         for co, d, q in [('CO-14104', '9722D10', 6), ('CO-14105', '9715310', 6), ('CO-14106', '9715310', 3), ('CO-14107', '9715310', 3),
                          ('CO-14109', '9811110', 6), ('CO-14110', '982220', 6)]]
SLICES = pack(LINES, [['T0409012', MF['T0409012'], '0001', 6], ['T0409013', MF['T0409013'], '0001', 18]], 6)
SENT = [s for s in SLICES if s['CASE_SEQ'] <= 4]   # the supplier ticks the unit: cases 1-4 (case 5 Not Ready)

WIDTHS_D = [12, 9, 9, 9, 11, 14, 17, 16, 10, 6, 7, 12, 16, 11, 10, 7, 8, 9]


def premap_rows():
    return [[s['SORT_SEQ'], s['CUSTOMER_ORDER_NO'], s['DETAILED_ITEM_NO'], s['SERIAL_NO'], NAME[s['DESTINATION_CD']], s['QTY'], s['PO_NO'] or '—',
             s['ASSIGNED_QTY'], s['CASE_SEQ'], s['CUT_FLAG'], s['CROSSDOCK_STATUS']] for s in SLICES]


def case_rows():
    rows = []
    for c in sorted({s['CASE_SEQ'] for s in SLICES}):
        sl = [s for s in SLICES if s['CASE_SEQ'] == c]
        rows.append([f'Case {c}', sum(s['ASSIGNED_QTY'] for s in sl), ' + '.join(f"{s['CUSTOMER_ORDER_NO']} {s['ASSIGNED_QTY']} ({s['PO_NO'] or 'no PO'})" for s in sl),
                     sl[-1]['CUT_FLAG'], 'Ready' if sl[-1]['CROSSDOCK_STATUS'] == '6' else 'Not Ready'])
    return rows


def instruction_rows():
    rows = []
    for n, s in enumerate(SENT, 1):
        rows.append([n + 2, s['CASE_SEQ'], s['LINE_SEQ'], 'PART-X', D, s['DESTINATION_CD'], s['CUSTOMER_ORDER_NO'], s['DETAILED_ITEM_NO'], s['SERIAL_NO'],
                     s['ASSIGNED_QTY'], s['PO_NO'], s['MANIFEST_NO'], s['MANIFEST_ITEM'], DT, '1', 'SD01', '(NULL)', '(NULL)'])
    return rows


SAMPLE = {
    "title": "Sample Input",
    "heading": "Sample Create ASN - ASN Cross Dock Creation (simulasi_asn_rev.xlsx, 18-Oct-2026)",
    "intro": [
        "Data of simulasi_asn_rev.xlsx (also in the prototype, business date 18-Oct). Supplier 50221 plant 1, Delivery Date 18-Oct-2026, Rit 1, Route SD01. "
        "PART-X, Pcs/Case = 6. ASN0001 (CO-14101) and ASN0002 (CO-14103) are already submitted, so the oldest open Customer Order Date is 17-Oct.",
        "Order date 17-Oct: 4 destinations, 30 pcs; PO T0409013 (PO date 18-Oct) has only 18 pcs (Short PO, abnormality); the rest of T0409012 (6) is "
        "taken first (older PO date). The split PO T0409014 (12) comes on 19-Oct.",
        "The supplier ticks the unit PART-X 17-Oct (cases 1-4, case 5 is Not Ready) and clicks [Create ASN]; the submit gives ASN0003.",
    ],
    "sections": [
        {"title": "A. Input: pre-mapping of XD09 (#TEMP_INSTRUCTION) in scan order: Customer Order Date, Customer Code, Customer Order No, …",
         "columns": ["Sort Seq", "Customer Order No", "Detailed Item No", "Serial No", "Destination", "Open Qty", "PO No", "Assigned Qty", "Case", "Cut", "Status"],
         "spans": [1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1],
         "rows": premap_rows()},
        {"title": "B. Input: PO parts before [Create ASN] (Pra Daily Order: manifest with CROSS_DOCK_FLAG = 'X')",
         "columns": ["PO No", "Manifest No", "Manifest Item", "Part No", "PO Qty (ORDER_QTY)", "Mapped Qty (TB_R_PRA_DAILY_ORDER_MAPPED)", "Open Qty"],
         "spans": [1, 1, 1, 1, 1, 2, 1],
         "rows": [["T0409012", MF['T0409012'], "0001", "PART-X", 6, 0, 6], ["T0409013", MF['T0409013'], "0001", "PART-X", 18, 0, 18]]},
        {"title": "C. Supplier cases (6 pcs in scan order; CUT_FLAG Y = the ASN may stop after the case)",
         "columns": ["Case", "Qty", "Content (customer order qty (PO))", "CUT_FLAG", "Status"],
         "spans": [1, 1, 8, 1, 2],
         "rows": case_rows()},
        {"title": "D. Result: rows inserted into TB_R_INSTRUCTION (cases 1-4; ASN_NO / CASE_NO filled on submit)",
         "columns": ["INSTRUCTION_ID", "CASE_SEQ", "LINE_SEQ", "PART_NO", "ORDER_DT", "DESTINATION_CD", "CUSTOMER_ORDER_NO", "DETAILED_ITEM_NO",
                     "SERIAL_NO", "QTY", "PO_NO", "MANIFEST_NO", "MANIFEST_ITEM", "DELIVERY_DT", "RIT_CYCLE", "ROUTE", "ASN_NO", "CASE_NO"],
         "widths": WIDTHS_D,
         "rows": instruction_rows()},
        {"title": "E. Result: other tables changed in the same transaction",
         "columns": ["Table", "Key", "Column", "Before", "After"],
         "spans": [4, 3, 2, 1, 1],
         "rows": [["TB_R_H0253_ORDER_CONTROL_PRE", "CO-14104, CO-14105, CO-14106, CO-14107, CO-14109 (whole line in the ASN)", "PO_MAPPED_FLAG", "N", "Y"],
                  ["TB_R_H0253_ORDER_CONTROL_PRE", "CO-14110 (case 5, not sent)", "PO_MAPPED_FLAG", "N", "N"],
                  ["TB_R_PRA_DAILY_ORDER_MAPPED", f"T0409012 / {MF['T0409012']} / 0001 / PART-X", "MAPPED_QTY", 0, 6],
                  ["TB_R_PRA_DAILY_ORDER_MAPPED", f"T0409013 / {MF['T0409013']} / 0001 / PART-X", "MAPPED_QTY", 0, 18]]},
        {"title": "F. Result on the screen: Case List (Draft)",
         "columns": ["Item", "Value"],
         "spans": [3, 12],
         "rows": [["ASN No", "ASN0003 (auto, assigned on submit)"], ["Supplier · Plant", "50221 · 1"],
                  ["Delivery Date · Rit · Route", f"{DT} · {RIT}"], ["Delivery Qty", "24 pcs"], ["Cases", "4 cases"],
                  ["Case 1 .. Case 4", "Case Number, Part Number, Customer Order Date, Qty (6 each); the expand button shows the PO No, Manifest No, Manifest Item and PO Qty "
                                       "(Case 1: T0409012; Cases 2-4: T0409013)"],
                  ["[Submit ASN]", "Confirmation: Submit ASN? 4 cases (24 pcs) will be created into ASN0003, delivery 18-Oct-2026 · Rit 1."]]},
        {"title": "G. Scenarios",
         "columns": ["No", "Scenario", "Expected result"],
         "spans": [1, 5, 12],
         "rows": [["N1", "Create ASN with the unit PART-X 17-Oct ticked (cases 1-4)", "Sections C to F: 4 cases, 5 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y on 5 lines, mapped qty added; Case List opens."],
                  ["N2", "[Submit ASN] and [Yes, submit]", "Submit ID handed to the submit process (5.7); ASN0003 and CASE_NO are written back to the 5 rows; "
                                                            "only case 5 (CO-14110, Not Ready) stays in the delivery plan."],
                  ["N3", "[Back] / [Cancel] on the Case List", "The 5 rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to N, MAPPED_QTY back to 0; "
                                                               "the unit is listed again."],
                  ["N4", "19-Oct: split PO T0409014 released", "Case 5 (CO-14110) is Ready → ASN0004; order date 18-Oct (3 destinations) → ASN0005."],
                  ["E1", "The D/S team holds Thailand (CO-14104) after the supplier ticked the unit", "MSG8; the whole create fails, nothing is inserted, "
                                                                                                         "the delivery plan is refreshed and all units are unticked."],
                  ["E2", "The unit is no longer Ready when [Create ASN] is clicked", "MSG7; nothing is inserted; the delivery plan is refreshed."],
                  ["E3", "D/S team ticks PART-X (supplier 50221-1) and a unit of supplier 50330-2", "MSG9; nothing is inserted."],
                  ["E4", "No ASN yet on 22-Oct: the supplier wants order date 18-Oct first", "Not possible: per Part Number the oldest Customer Order Date first "
                                                                                             "(15-Oct, then 16-Oct, 17-Oct …); later dates are disabled (Wait: dd-Mon first)."],
                  ["E5", "Database error during the insert", "Roll back: nothing is kept; error message on the screen and Log FAILED."]]},
    ],
}
