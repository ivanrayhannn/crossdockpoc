"""Decisions of 20-Oct-26: structure of the existing Pra Daily Order tables (NSP_INSERT_TB_R_PRA_DAILY_ORDER_MANIFEST / _PART.sql).
- The crossdock order is the manifest with TB_R_PRA_DAILY_ORDER_MANIFEST.CROSS_DOCK_FLAG = 'X'; its part data is taken from
  TB_R_PRA_DAILY_ORDER_PART (join on MANIFEST_NO).
- Columns of the new tables use the names of the existing tables: MANIFEST_ITEM, ORDER_QTY, PO_DT.
Run after apply_1910.py (build_all_v2.sh). Every replacement must match, otherwise the build stops."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAN, PART = 'TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_PRA_DAILY_ORDER_PART'
FLAG_RULE = (f"manifests with {MAN}.CROSS_DOCK_FLAG = 'X'; their part data from {PART} (join MANIFEST_NO)")


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


# column names of the new tables -> names of the existing Pra Daily Order columns (the existing ASN field 'PO_NO / MANIFEST_ITEM_NO' is kept)
RENAME = [('PO_NO / MANIFEST_ITEM_NO', '§KEEP§'), ('MANIFEST_ITEM_NO', 'MANIFEST_ITEM'), ('PO_ORDER_QTY', 'ORDER_QTY'), ('PO_ORDER_DT', 'PO_DT'),
          ('Manifest Item No', 'Manifest Item'), ('§KEEP§', 'PO_NO / MANIFEST_ITEM_NO')]

XD09 = [
    ("CROSSDOCK_FLAG = 'X'; latest data; open PO qty", f"{FLAG_RULE}; latest data; open PO qty"),
    ("CROSSDOCK_FLAG = 'X', latest data, by Order Date ascending", f"{FLAG_RULE}; latest data; by PO_DT ascending"),
    ("(Pra Daily Order, crossdock flag X)", f"(Pra Daily Order: {FLAG_RULE})"),
    ("PO parts of the Pra Daily Order (crossdock flag X)", f"PO parts of the Pra Daily Order ({FLAG_RULE})"),
]
SOURCE = {'PO Number': f'{PART}.PO_NO', 'Manifest Number': f'{PART}.MANIFEST_NO', 'Manifest Item': f'{PART}.MANIFEST_ITEM',
          'Order Date (PO)': f'{MAN}.PO_DT', 'PO Order Qty': f'{PART}.ORDER_QTY', 'Supplier Code': f'{MAN}.SUPPLIER_CD',
          'Supplier Plant': f'{MAN}.SUPPLIER_PLANT', 'Sub Supplier Code': f'{MAN}.SUB_SUPP_CD', 'Sub Supplier Plant': f'{MAN}.SUB_SUPP_PLANT',
          'Order Type': f'{MAN}.ORDER_TYPE', 'Dock Code': f'{PART}.DOCK_CD', 'ETD Ori': 'ETD Ori (source column TBC)'}


def main():
    s = rep(load('XD09'), XD09, 'XD09')
    s = rep(s, RENAME, 'XD09', must=False)
    for b in s['data_map']['blocks']:
        src = b['source']
        if isinstance(src, dict) and MAN in src.get('table', ''):
            src['keys'] = [{'field': 'H0253.SHIPPING_PART_NO', 'value': f'= {PART}.PART_NO'},
                           {'field': f'{PART}.MANIFEST_NO', 'value': f"= {MAN}.MANIFEST_NO with {MAN}.CROSS_DOCK_FLAG = 'X'"}]
            for m in b.get('mappings', b.get('fields', [])):
                if m.get('source_field') in SOURCE:
                    m['source_field'] = SOURCE[m['source_field']]
    s['general']['objective'].append(
        f"Crossdock PO (decided 20-Oct): the order is taken from the manifest with {MAN}.CROSS_DOCK_FLAG = 'X' and its part data from {PART} "
        "(MANIFEST_NO). The PO line is identified by MANIFEST_NO + MANIFEST_ITEM (PO_ITEM can differ from MANIFEST_ITEM; one PO can have several manifests).")
    save('XD09', s)
    for fid in ('XD10', 'XD11'):
        s = rep(load(fid), RENAME, fid, must=False)
        if fid == 'XD10':
            s = rep(s, [("Input: PO parts (Pra Daily Order, crossdock flag X)", f"Input: PO parts (Pra Daily Order: {FLAG_RULE})")], fid, must=False)
        save(fid, s)
    print('decisions 20-Oct applied')


if __name__ == '__main__':
    main()
