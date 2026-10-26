"""Decisions of 23-Oct-26 (simulasi_asn.xlsx): UPD_STATUS, one H0253 batch, draft release and Change Order Number.
- TB_R_H0253_ORDER_CONTROL_PRE.UPD_STATUS: NULL / '6' received / '2' cancelled (ORDER_STATUS keeps the first value); XD08 is the only
  H0253 batch (XD12 merged); XD09 takes only lines with UPD_STATUS NULL.
- Every run of XD08 releases all drafts (TB_R_INSTRUCTION rows with ASN_NO NULL); [Submit ASN] re-checks the draft (XD10).
- XD11 is now the screen Change Order Number (D/S team); the history is TB_H_CROSSDOCK_ORDER_CHANGE.
- TB_R_INSTRUCTION gets DRAFT_ID (one per [Create ASN]).
Run after apply_2110.py (build_all_v2.sh)."""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INS, PMAP = 'TB_R_INSTRUCTION', 'TB_R_PRA_DAILY_ORDER_MAPPED'


def load(fid):
    return json.load(open(os.path.join(HERE, f"{fid}_spec.json"), encoding='utf-8'))


def save(fid, s):
    json.dump(s, open(os.path.join(HERE, f"{fid}_spec.json"), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def rep(s, pairs, fid, must=True):
    t = json.dumps(s, ensure_ascii=False)
    for a, b in pairs:
        a_j, b_j = json.dumps(a, ensure_ascii=False)[1:-1], json.dumps(b, ensure_ascii=False)[1:-1]
        if a_j not in t:
            if must:
                sys.exit(f"{fid}: text not found: {a[:80]}")
            continue
        t = t.replace(a_j, b_j)
    return json.loads(t)


DRAFT_COL = ["DRAFT_ID", "VARCHAR(20)", "", "Y", "Draft of one [Create ASN] (all rows of the creation); NULL after [Submit ASN] is not needed (ASN_NO filled). "
             "Every run of XD08 deletes the rows with ASN_NO NULL"]
UPD_FILTER = "UPD_STATUS IS NULL (no status change in G-System)"


def xd10():
    s = load('XD10')
    for t in s['tables']:
        if t['name'] == INS and not any(c[0] == 'DRAFT_ID' for c in t['columns']):
            i = next(k for k, c in enumerate(t['columns']) if c[0] == 'ASN_NO')
            t['columns'].insert(i, DRAFT_COL)
            t['description'] += (" Rows without ASN_NO are a draft: every run of XD08 releases all drafts (decided 23-Oct); a cancelled line in a submitted "
                                 "ASN is moved to other lines in Change Order Number (XD11).")
    for b in s['data_map']['blocks']:
        if b['destination'].get('table') == INS and b['destination'].get('operation') == 'Insert':
            if not any(m.get('dest_field') == 'DRAFT_ID' for m in b['mappings']):
                b['mappings'].insert(0, {"dest_field": "DRAFT_ID", "description": "New id per [Create ASN] (same for all rows of the creation)"})
    op = s['operation']
    for blk in op:
        if blk.get('type') == 'bullets':
            for i, x in enumerate(blk['items']):
                if x.startswith("[Back] / [Cancel] on the Case List cancel the creation"):
                    blk['items'][i] = (x + " A draft left open (no Submit, no Cancel) is released by the next run of XD08 (every run releases all drafts, "
                                           "decided 23-Oct): the cases come back in the delivery plan and the supplier ticks them again.")
    # [Submit ASN] re-check (5.7)
    for blk in op:
        if blk.get('type') == 'heading' and blk['text'].startswith('5.7'):
            nxt = op[op.index(blk) + 1]
            if nxt.get('type') == 'bullets':
                nxt['items'].insert(0, "Re-check before the submit: the draft must still exist (not released by XD08) and every line of it must still have UPD_STATUS NULL "
                                       "and the same qty. Otherwise nothing is submitted, the draft is released and message no. 11 is shown; the supplier searches again.")
    msgs = s['display_messages']
    if not any(m.get('msg_id') == 'MSG11' for m in msgs):
        msgs.append({"event": "Click [Submit ASN] / [Yes]", "cause": "The draft was released by XD08 or a line changed in G-System (UPD_STATUS, qty)", "type": "Error",
                     "msg_id": "MSG11", "message": "Some orders have changed. The draft is released; please Search and create the ASN again.",
                     "action": "Click [OK]; back to the delivery plan."})
    s = rep(s, [("refer XD11 / XD12", "refer XD08 / XD11"), ("Refer XD11 / XD12.", "Refer XD08 / XD11.")], 'XD10', must=False)
    save('XD10', s)
    return [t for t in s['tables'] if t['name'] in (INS, PMAP)]


def xd09():
    s = load('XD09')
    s = rep(s, [("ORDER_STATUS = '7', HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'", f"ORDER_STATUS = '7', {UPD_FILTER}, HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'"),
                ("ORDER_STATUS = '7' (Cross Dock), HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'", f"ORDER_STATUS = '7' (Cross Dock), {UPD_FILTER}, HOLD_FLAG = 'N', PO_MAPPED_FLAG = 'N'"),
                ("WHERE H.ORDER_STATUS = '7' AND H.HOLD_FLAG = 'N'", "WHERE H.ORDER_STATUS = '7' AND H.UPD_STATUS IS NULL AND H.HOLD_FLAG = 'N'"),
                ("Status '2' (cancel) is not taken.", "Lines changed in G-System (UPD_STATUS '6' / '2', set by XD08) are not taken.")], 'XD09', must=False)
    save('XD09', s)


def batch_tables(fid, extra):
    s = load(fid)
    names = {t['name'] for t in s['tables']}
    s['tables'] += [copy.deepcopy(t) for t in extra if t['name'] not in names]
    save(fid, s)


def xd15():
    s = load('XD15')
    s = rep(s, [("refer XD11 / XD12", "refer XD08 / XD11")], 'XD15', must=False)
    save('XD15', s)


BL_HEAD = "Business Logic ASN"
BL = ["Customer Order Date (today, D) → PO Date (tomorrow, D+1): one PO per Part Number per Customer Order Date.",
      "Total customer order qty of all destinations per Part Number and Customer Order Date = total PO qty of that PO. When the PO qty is lower: "
      "abnormality; the rest comes in a split PO, the customer orders without PO wait (Not Ready) until the next PO is issued.",
      "One customer order line can be in different ASNs (its cases split). When G-System receives them separately, the line is split in H0253 "
      "(new SERIAL_NO); each part stays linked to its ASN (XD08).",
      "PO_MAPPED_FLAG is set by [Create ASN] ('Y' when the whole line is in the ASN; a draft not submitted is released by XD08).",
      "Ready cases of the delivery plan are sent following the cut (CUT_FLAG): the supplier selects from case 1 up to a cut; the cases between two cuts are sent together."]


def business_logic(fid, key, num):
    s = load(fid)
    blocks = s[key]
    if not any(b.get('type') == 'heading' and b.get('text', '').endswith(BL_HEAD) for b in blocks):
        i = 1 if key == 'func_desc' else 0   # XD09: after the intro text
        blocks[i:i] = [{"type": "heading", "text": f"{num} {BL_HEAD}"},
                       {"type": "bullets", "marker": "1.", "level": 0, "items": BL}]
    save(fid, s)


CAPS_SIM = {  # screenshots of the prototype with the data of simulasi_asn_rev.xlsx (business date 18-Oct)
    'c_02_delivery_plan': '2. Delivery plan after Search (supplier view, 18-Oct, simulasi_asn_rev.xlsx): PART-X 17-Oct, cases 1-4 Ready, case 5 Not Ready '
                          '(Short PO: T0409013 18 of 30 pcs)',
    'c_04_ds_hold': '4. D/S team: Thailand (CO-14104) on hold; the scan order and the cases are computed again without it',
    'c_05_selected': '5. Case 3 of PART-X 17-Oct ticked: cases 1-3 are selected (the selection always starts at case 1)',
    'c_05e_supplier_conflict': '5d. D/S team: units of two suppliers ticked (PART-D of supplier 50330, prototype only), Create ASN: one supplier per ASN',
    'c_06_case_list': '6. Case List sub screen: cases 1-4 of PART-X 17-Oct = ASN0003',
    'c_10_list_after': '10. Delivery plan after submit: only case 5 (CO-14110) is left, Not Ready until the split PO T0409014'}


def captions():
    s = load('XD10')
    for sl in s['screen_layout']:
        k = os.path.splitext(os.path.basename(sl.get('image', '')))[0]
        if k in CAPS_SIM:
            sl['caption'] = CAPS_SIM[k]
    save('XD10', s)


def main():
    captions()
    business_logic('XD09', 'func_desc', '4.0')
    business_logic('XD10', 'operation', '5.0')
    tabs = xd10()
    xd09()
    batch_tables('XD08', tabs)
    batch_tables('XD11', tabs)
    xd15()
    p = os.path.join(HERE, 'XD12_spec.json')
    if os.path.exists(p):
        os.remove(p)
    print('decisions 23-Oct applied')


if __name__ == '__main__':
    main()
