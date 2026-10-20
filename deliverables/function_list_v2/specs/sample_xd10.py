"""Sheet Sample Input of XD10: what [Create ASN] does with the pre-mapping of XD09 (dummy parts PART-X / PART-Y)."""

D, DT, RIT = '14-Oct-2026', '16-Oct-2026', 'Rit 1 · SD01'
VN, TH, PH = '9715310 (Vietnam)', '9722D10 (Thailand)', '9811110 (Philippines)'

# (customer order, detailed item, serial, part, destination, order qty, PO, manifest, manifest item, assigned qty)
PREMAP = [
    ('CO-14101', '001', '0000001', 'PART-X', VN, 10, 'T0409001', '3126035901', '0001', 10),
    ('CO-14102', '001', '0000001', 'PART-X', VN, 4, 'T0409001', '3126035901', '0001', 2),
    ('CO-14102', '001', '0000001', 'PART-X', VN, 4, 'T0409002', '3126035902', '0001', 2),
    ('CO-14103', '001', '0000001', 'PART-X', VN, 4, 'T0409002', '3126035902', '0001', 4),
    ('CO-14104', '001', '0000001', 'PART-X', TH, 6, 'T0409002', '3126035902', '0001', 6),
    ('CO-14105', '001', '0000001', 'PART-Y', PH, 6, 'T0409003', '3126035903', '0001', 6),
]

# case seq -> rows (pre-map index, qty in the case)
CASES = {1: [(0, 6)], 2: [(0, 4), (1, 2)], 3: [(2, 2), (3, 4)], 4: [(4, 6)], 5: [(5, 6)]}

WIDTHS_D = [12, 9, 9, 9, 11, 14, 17, 16, 10, 6, 7, 12, 16, 11, 10, 7, 8, 9]


def instruction_rows():
    rows, n = [], 0
    for seq, parts in CASES.items():
        for line, (i, qty) in enumerate(parts, 1):
            co, item, serial, part, dest, _, po, mf, mi, _ = PREMAP[i]
            n += 1
            rows.append([f'INS-{n:04d}', seq, line, part, D, dest.split()[0], co, item, serial, qty, po, mf, mi,
                         DT, '1', 'SD01', '(NULL)', '(NULL)'])
    return rows


def case_rows():
    rows = []
    for seq, parts in CASES.items():
        p = PREMAP[parts[0][0]]
        content = ' + '.join(f'{PREMAP[i][0]} {q} ({PREMAP[i][6]})' for i, q in parts)
        rows.append([f'Case {seq}', p[3], p[4], sum(q for _, q in parts), content])
    return rows


SAMPLE = {
    "title": "Sample Input",
    "heading": "Sample Create ASN - ASN Cross Dock Creation (case packing and real mapping)",
    "intro": [
        "Dummy data. Supplier 50221 plant 1, Delivery Date 16-Oct-2026, Rit 1, Route SD01. Pcs/Case = 6 for PART-X and PART-Y.",
        "The supplier ticks PART-X 14-Oct-2026 and PART-Y 14-Oct-2026 (both Ready) on the delivery plan and clicks [Create ASN].",
        "Rule: per Part Number + Customer Order Date + destination the order lines (FIFO, then by PO) are packed in cases of pcs/case. "
        "A case can hold several customer orders and several POs of the same destination; a line that does not fit continues in the next case.",
    ],
    "sections": [
        {"title": "A. Input: pre-mapping of the ticked units (XD09, #TEMP_INSTRUCTION, one row per customer order line x PO)",
         "columns": ["Customer Order No", "Detailed Item No", "Serial No", "Part No", "Destination", "Order Qty", "PO No", "Manifest No",
                     "Manifest Item", "Assigned Qty"],
         "spans": [1, 1, 1, 1, 2, 1, 1, 1, 1, 1],
         "rows": [list(r) for r in PREMAP]},
        {"title": "B. Input: PO parts before [Create ASN] (Pra Daily Order: manifest with CROSS_DOCK_FLAG = 'X', part data from TB_R_PRA_DAILY_ORDER_PART)",
         "columns": ["PO No", "Manifest No", "Manifest Item", "Part No", "PO Qty (ORDER_QTY)", "Mapped Qty (TB_R_PRA_DAILY_ORDER_MAPPED)", "Open Qty"],
         "spans": [1, 1, 1, 1, 1, 2, 1],
         "rows": [["T0409001", "3126035901", "0001", "PART-X", 12, 0, 12], ["T0409002", "3126035902", "0001", "PART-X", 12, 0, 12],
                  ["T0409003", "3126035903", "0001", "PART-Y", 6, 0, 6]]},
        {"title": "C. Case packing (Vietnam 18 pcs = 3 cases, Thailand 6 pcs = 1 case, Philippines 6 pcs = 1 case)",
         "columns": ["Case", "Part No", "Destination", "Case Qty", "Content (customer order qty (PO))"],
         "spans": [1, 1, 2, 1, 6],
         "rows": case_rows()},
        {"title": "D. Result: rows inserted into TB_R_INSTRUCTION (one row per case x customer order line x PO; ASN_NO / CASE_NO filled on submit)",
         "columns": ["INSTRUCTION_ID", "CASE_SEQ", "LINE_SEQ", "PART_NO", "ORDER_DT", "DESTINATION_CD", "CUSTOMER_ORDER_NO", "DETAILED_ITEM_NO",
                     "SERIAL_NO", "QTY", "PO_NO", "MANIFEST_NO", "MANIFEST_ITEM", "DELIVERY_DT", "RIT_CYCLE", "ROUTE", "ASN_NO", "CASE_NO"],
         "widths": WIDTHS_D,
         "rows": instruction_rows()},
        {"title": "E. Result: other tables changed in the same transaction",
         "columns": ["Table", "Key", "Column", "Before", "After"],
         "spans": [4, 3, 2, 1, 1],
         "rows": [["TB_R_H0253_ORDER_CONTROL_PRE", "CO-14101 .. CO-14105 (detailed item 001, serial 0000001)", "PO_MAPPED_FLAG", "N", "Y"],
                  ["TB_R_PRA_DAILY_ORDER_MAPPED", "T0409001 / 3126035901 / 0001 / PART-X", "MAPPED_QTY", 0, 12],
                  ["TB_R_PRA_DAILY_ORDER_MAPPED", "T0409002 / 3126035902 / 0001 / PART-X", "MAPPED_QTY", 0, 12],
                  ["TB_R_PRA_DAILY_ORDER_MAPPED", "T0409003 / 3126035903 / 0001 / PART-Y", "MAPPED_QTY", 0, 6]]},
        {"title": "F. Result on the screen: Case List (Draft)",
         "columns": ["Item", "Value"],
         "spans": [3, 12],
         "rows": [["ASN No", "ASN-50221-261016-001 (auto, assigned on submit)"], ["Supplier · Plant", "50221 · 1"],
                  ["Delivery Date · Rit · Route", f"{DT} · {RIT}"], ["Delivery Qty", "30 pcs"], ["Cases", "5 cases"],
                  ["Case 1 .. Case 5", "Case Number, Part Number, Qty (6 each); the expand button shows the PO No, Manifest No, Manifest Item and PO Qty of the case "
                                       "(Case 2: CO-14101 + CO-14102 of T0409001; Case 3: CO-14102 + CO-14103 of T0409002)"],
                  ["[Submit ASN]", "Confirmation: Submit ASN? 5 cases (30 pcs) will be created into ASN-50221-261016-001, delivery 16-Oct-2026 · Rit 1."]]},
        {"title": "G. Scenarios",
         "columns": ["No", "Scenario", "Expected result"],
         "spans": [1, 5, 12],
         "rows": [["N1", "Create ASN with PART-X 14-Oct and PART-Y 14-Oct ticked", "Sections C to F: 5 cases, 7 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y, mapped qty added; Case List opens."],
                  ["N2", "[Submit ASN] and [Yes, submit]", "Submit ID handed to the submit process (5.7); ASN_NO and CASE_NO (existing sequence) are written back to the 7 rows; "
                                                            "ASN status Created; PART-X / PART-Y 14-Oct are no longer listed."],
                  ["N3", "[Back] / [Cancel] on the Case List", "The 7 rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to N, MAPPED_QTY back to 0; "
                                                               "the units are listed again as Ready."],
                  ["E1", "The D/S team holds Thailand of PART-X 14-Oct after the supplier ticked it", "MSG8; the whole create fails (also PART-Y), nothing is inserted, "
                                                                                                      "the delivery plan is refreshed and all units are unticked."],
                  ["E2", "PART-X 14-Oct is no longer Ready (e.g. a PO was changed) when [Create ASN] is clicked", "MSG7; nothing is inserted; the delivery plan is refreshed."],
                  ["E3", "D/S team ticks PART-X (supplier 50221-1) and a unit of supplier 50330-2", "MSG9; nothing is inserted."],
                  ["E4", "Database error during the insert", "Roll back: nothing is kept; error message on the screen and Log FAILED."]]},
    ],
}
