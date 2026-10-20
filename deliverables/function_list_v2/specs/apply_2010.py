"""Decisions of 20-Oct-26: structure of the existing Pra Daily Order tables (NSP_INSERT_TB_R_PRA_DAILY_ORDER_MANIFEST / _PART.sql).
- The crossdock order is the manifest with TB_R_PRA_DAILY_ORDER_MANIFEST.CROSS_DOCK_FLAG = 'X'; its part data is taken from
  TB_R_PRA_DAILY_ORDER_PART (join on MANIFEST_NO).
- Columns of the new tables use the names of the existing tables: MANIFEST_ITEM, ORDER_QTY, PO_DT.
- Existing tables from GTOPAS_SPS_DB_Structure_20240423.xlsx (erd/gtopas_structure.json): Submit ASN writes TB_R_DAILY_ORDER_MANIFEST
  (one row per manifest, same ASN_NO) and TB_R_DAILY_ORDER_PART (one row per manifest item and case); ASN_LAST_SEQ / CASE_LABEL_LAST_SEQ are
  kept in TB_R_CASE_LABEL_LAST_SEQ; part name from TB_M_PART_MASTER.
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


GT = json.load(open(os.path.join(HERE, '..', 'erd', 'gtopas_structure.json'), encoding='utf-8'))
USED = {
    'TB_R_DAILY_ORDER_MANIFEST': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'ASN_NO', 'ASN_DATE', 'DEPOT_CD', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'SUB_SUPP_CD',
                                  'SUB_SUPP_PLANT', 'SUPPLIER_NAME', 'PO_NO', 'PO_DATE', 'ORDER_TYPE', 'CROSS_DOCK_FLAG', 'DOCK_CD', 'TOTAL_ITEM', 'TOTAL_QTY',
                                  'DELIVERY_DT_ORI', 'SUB_ROUTE_CD', 'SUB_ROUTE_SEQ', 'SUB_ROUTE_DT', 'STATUS', 'CREATED_BY', 'CREATED_DT'],
    'TB_R_DAILY_ORDER_PART': ['SUB_MANIFEST_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'CASE_NO', 'PO_NO', 'PO_ITEM', 'ASN_NO', 'ASN_DATE', 'PART_NO', 'PART_NAME',
                              'PO_QTY', 'DELIVERY_QTY', 'QTY_PER_CONTAINER', 'DELIVERY_DT_ORI', 'KANBAN_NO', 'PART_BARCODE', 'STATUS', 'CREATED_BY', 'CREATED_DT'],
    'TB_R_CASE_LABEL_LAST_SEQ': ['SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ', 'CHANGED_BY', 'CHANGED_DT'],
    'TB_M_PART_MASTER': ['PART_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'DOCK_CD', 'VALID_FROM', 'PART_NAME', 'VALID_TO'],
}
TDESC = {
    'TB_R_DAILY_ORDER_MANIFEST': 'Existing ASN manifest (GTOPAS SPS DB structure TR-01). Submit ASN: one row per Pra Daily Order manifest of the cases, all with the same ASN_NO. Only the columns used are listed.',
    'TB_R_DAILY_ORDER_PART': 'Existing ASN part (TR-02). Submit ASN: one row per manifest item and case (a case can hold several manifest items). Only the columns used are listed.',
    'TB_R_CASE_LABEL_LAST_SEQ': 'Existing last sequence per supplier + plant (TR-06): the case number (case label) and the ASN number are auto generated from it and the new last sequence is saved here.',
    'TB_M_PART_MASTER': 'Existing part master (MST-03); only PART_NAME is used (by PART_NO).',
}


def gt_table(name):
    cols = [c for c in GT[name]['columns'] if c[0] in USED[name]]
    return {'name': name, 'kind': 'master' if name.startswith('TB_M') else 'transaction', 'proposed': False, 'description': TDESC[name],
            'columns': [[c[0], c[1], c[2], c[3], c[4]] for c in cols]}


MAN_MAP = [('SUB_MANIFEST_NO', None, 'Sub manifest number as existing (sequence MANIFEST_LAST_SEQ of the Pra manifest)'),
           ('MANIFEST_NO', 'TB_R_INSTRUCTION.MANIFEST_NO', 'One row per manifest of the cases'),
           ('ASN_NO', None, 'Auto generated as existing; last sequence ASN_LAST_SEQ in TB_R_CASE_LABEL_LAST_SEQ (same ASN_NO for all manifests of the submit)'),
           ('ASN_DATE', None, 'Submit date-time'),
           ('DEPOT_CD', f'{MAN}.DEPOT_CD', ''), ('SUPPLIER_CD', f'{MAN}.SUPPLIER_CD', ''), ('SUPPLIER_PLANT', f'{MAN}.SUPPLIER_PLANT', ''),
           ('SUB_SUPP_CD', f'{MAN}.SUB_SUPP_CD', ''), ('SUB_SUPP_PLANT', f'{MAN}.SUB_SUPP_PLANT', ''), ('SUPPLIER_NAME', f'{MAN}.SUPPLIER_NAME', ''),
           ('PO_NO', f'{MAN}.PO_NO', ''), ('PO_DATE', f'{MAN}.PO_DT', ''), ('ORDER_TYPE', f'{MAN}.ORDER_TYPE', ''),
           ('CROSS_DOCK_FLAG', f'{MAN}.CROSS_DOCK_FLAG', "'X'"), ('DOCK_CD', f'{MAN}.DOCK_CD', ''),
           ('TOTAL_ITEM', None, 'Number of manifest items of the manifest in this ASN'), ('TOTAL_QTY', None, 'Sum of QTY of the manifest in this ASN'),
           ('DELIVERY_DT_ORI', 'TB_R_INSTRUCTION.DELIVERY_DT', 'Delivery Date of the Search'),
           ('SUB_ROUTE_CD', 'TB_R_INSTRUCTION.ROUTE', 'Route of the Search'), ('SUB_ROUTE_SEQ', 'TB_R_INSTRUCTION.RIT_CYCLE', 'Rit of the Search'),
           ('SUB_ROUTE_DT', f'{MAN}.SUB_ROUTE_DT', ''), ('STATUS', None, 'ASN status Created (code as existing)'),
           ('CREATED_BY', None, 'User ID'), ('CREATED_DT', None, 'Server system date-time')]
PART_MAP = [('SUB_MANIFEST_NO', None, 'Of the TB_R_DAILY_ORDER_MANIFEST row of the manifest'),
            ('MANIFEST_NO', 'TB_R_INSTRUCTION.MANIFEST_NO', ''), ('MANIFEST_ITEM', 'TB_R_INSTRUCTION.MANIFEST_ITEM', ''),
            ('CASE_NO', None, 'Auto generated per CASE_SEQ (case label); last sequence CASE_LABEL_LAST_SEQ in TB_R_CASE_LABEL_LAST_SEQ'),
            ('PO_NO', f'{PART}.PO_NO', ''), ('PO_ITEM', f'{PART}.PO_ITEM', ''), ('ASN_NO', None, 'ASN_NO of the submit'), ('ASN_DATE', None, 'Submit date-time'),
            ('PART_NO', f'{PART}.PART_NO', ''), ('PART_NAME', 'TB_M_PART_MASTER.PART_NAME', 'By PART_NO'),
            ('PO_QTY', f'{PART}.ORDER_QTY', ''), ('DELIVERY_QTY', None, 'Sum of TB_R_INSTRUCTION.QTY of the manifest item in the case'),
            ('QTY_PER_CONTAINER', f'{PART}.QTY_PER_CONTAINER', ''), ('DELIVERY_DT_ORI', 'TB_R_INSTRUCTION.DELIVERY_DT', ''),
            ('KANBAN_NO', f'{PART}.KANBAN_NO', ''), ('PART_BARCODE', f'{PART}.PART_BARCODE', 'As existing'),
            ('STATUS', None, 'As existing'), ('CREATED_BY', None, 'User ID'), ('CREATED_DT', None, 'Server system date-time')]


def mapping(rows):
    out = []
    for dest, src, desc in rows:
        m = {'dest_field': dest}
        if src:
            m['source_field'] = src
        if desc:
            m['description'] = desc
        out.append(m)
    return out


def existing_tables(s, names):
    s['tables'] = [t for t in s['tables'] if t['name'] not in names] + [gt_table(n) for n in names]


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
            s = rep(s, [("existing last sequence table", "TB_R_CASE_LABEL_LAST_SEQ")], fid, must=False)
            existing_tables(s, ['TB_R_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_PART', 'TB_R_CASE_LABEL_LAST_SEQ', 'TB_M_PART_MASTER'])
            for b in s['data_map']['blocks']:
                d = b['destination']
                if d.get('table') == 'TB_R_DAILY_ORDER_MANIFEST':
                    b['source'] = {'table': f'TB_R_INSTRUCTION + {MAN}', 'keys': [{'field': 'MANIFEST_NO', 'value': 'Manifests of the cases of the submit'}]}
                    d['description'] = 'Submit ASN (5.7): one row per manifest of the cases; all rows of the submit share one ASN_NO'
                    b['mappings'] = mapping(MAN_MAP)
                elif d.get('table') == 'TB_R_DAILY_ORDER_PART':
                    b['source'] = {'table': f'TB_R_INSTRUCTION + {PART} + TB_M_PART_MASTER',
                                   'keys': [{'field': 'MANIFEST_NO + MANIFEST_ITEM + CASE_SEQ', 'value': 'One row per manifest item and case'}]}
                    d['description'] = 'Submit ASN (5.7): one row per manifest item and case'
                    b['mappings'] = mapping(PART_MAP)
            b = {'source': 'Last sequence of the submit', 'destination': {'table': 'TB_R_CASE_LABEL_LAST_SEQ', 'operation': 'Update',
                 'description': 'Submit ASN (5.7): new last sequence of the supplier + plant', 'keys': [{'field': 'SUPPLIER_CD + SUPPLIER_PLANT_CD', 'value': 'Supplier of the ASN'}]},
                 'mappings': mapping([('ASN_LAST_SEQ', None, 'Last sequence used for the ASN number'), ('CASE_LABEL_LAST_SEQ', None, 'Last sequence used for the case numbers'),
                                      ('CHANGED_BY', None, 'User ID'), ('CHANGED_DT', None, 'Server system date-time')])}
            if not any(x['destination'].get('table') == 'TB_R_CASE_LABEL_LAST_SEQ' for x in s['data_map']['blocks']):
                s['data_map']['blocks'].append(b)
            s['general']['objective'].append(
                'Submit ASN (decided 20-Oct, existing structure GTOPAS SPS DB): one TB_R_DAILY_ORDER_MANIFEST row per Pra Daily Order manifest of the cases '
                '(same ASN_NO) and one TB_R_DAILY_ORDER_PART row per manifest item and case; the ASN number and the case numbers (case label) are auto generated '
                'and their last sequence is saved in TB_R_CASE_LABEL_LAST_SEQ; PART_NAME from TB_M_PART_MASTER.')
        save(fid, s)
    s = load('XD15')
    existing_tables(s, ['TB_R_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_PART'])
    save('XD15', s)
    print('decisions 20-Oct applied')


if __name__ == '__main__':
    main()
