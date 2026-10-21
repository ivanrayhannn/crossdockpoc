"""Pre-mapping of XD09 (decided 21-Oct): customer order lines in the receiving scan order of G-System, PO given in PO_DT order,
the pcs cut into supplier cases of PCS_CASE pcs, and the cases grouped into blocks (ASN options).
A cut after a case is valid when the cumulative qty of every destination of the unit is a multiple of PCS_CASE, so that the
warehouse can close its cases (1 case = 1 destination). A block is Ready ('6') when it and every earlier block of the unit have a PO."""

# Allocation Priority = Customer Order Date (ORDER_DT) first, then the G-System allocation keys
SCAN_KEYS = ['ORDER_DT', 'CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'ORDER_TIME', 'DESTINATION_CD', 'DETAILED_ITEM_NO', 'SERIAL_NO']


def pack(lines, pos, pcs):
    """lines: dicts with the SCAN_KEYS, PART_NO and QTY (open qty) of ONE unit (Part Number + Customer Order Date), any order.
    pos: list of [po_no, manifest_no, manifest_item, open_qty] in PO_DT order; open_qty is reduced in place (shared by later units).
    Returns one dict per slice (line x PO x case) with SORT_SEQ, ASSIGNED_QTY, PO_NO, MANIFEST_NO, MANIFEST_ITEM, CASE_SEQ, LINE_SEQ,
    CUM_DEST_QTY, CUT_FLAG, GROUP_SEQ and CROSSDOCK_STATUS."""
    lines = sorted(lines, key=lambda l: [str(l.get(k) or '') for k in SCAN_KEYS])
    out, case, room, line_seq = [], 1, pcs, 0
    for seq, l in enumerate(lines, 1):
        left = l['QTY']
        while left:
            po = next((p for p in pos if p[3] > 0), None)
            q = min(left, room, po[3] if po else left)
            if po:
                po[3] -= q
            line_seq += 1
            out.append(dict(l, SORT_SEQ=seq, ASSIGNED_QTY=q, PO_NO=po[0] if po else None, MANIFEST_NO=po[1] if po else None,
                            MANIFEST_ITEM=po[2] if po else None, CASE_SEQ=case, LINE_SEQ=line_seq))
            left -= q
            room -= q
            if room == 0:
                case, room, line_seq = case + 1, pcs, 0
    cum, group = {}, 1
    for i, s in enumerate(out):
        cum[s['DESTINATION_CD']] = cum.get(s['DESTINATION_CD'], 0) + s['ASSIGNED_QTY']
        s['CUM_DEST_QTY'] = cum[s['DESTINATION_CD']]
        last_of_case = i == len(out) - 1 or out[i + 1]['CASE_SEQ'] != s['CASE_SEQ']
        s['CUT_FLAG'] = 'Y' if last_of_case and all(v % pcs == 0 for v in cum.values()) else 'N'
        s['GROUP_SEQ'] = group
        if s['CUT_FLAG'] == 'Y':
            group += 1
    ready = True
    for g in sorted({s['GROUP_SEQ'] for s in out}):
        ready = ready and all(s['PO_NO'] for s in out if s['GROUP_SEQ'] == g)
        for s in out:
            if s['GROUP_SEQ'] == g:
                s['CROSSDOCK_STATUS'] = '6' if ready else '7'
    return out
