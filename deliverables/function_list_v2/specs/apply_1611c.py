"""16-Nov: no new table TB_R_PRA_DAILY_ORDER_MAPPED. The existing TB_R_PRA_DAILY_ORDER_PART already has ORDER_QTY and REMAIN_QTY
per PO part: open PO qty = REMAIN_QTY; [Create ASN] reduces REMAIN_QTY, Back / Cancel / submit error / XD08 release add it back.
Runs after apply_1611b and before apply_1611 (revisions)."""
import json

MAPPED = 'TB_R_PRA_DAILY_ORDER_MAPPED'
PART = 'TB_R_PRA_DAILY_ORDER_PART'
T_PART = {'name': PART, 'kind': 'transaction', 'proposed': False,
          'description': 'Existing Pra Daily Order part (one row per manifest item). Crossdock uses ORDER_QTY and REMAIN_QTY of the parts of the '
                         "manifests with CROSS_DOCK_FLAG = 'X': open PO qty = REMAIN_QTY (no new mapped-qty table, decided 16-Nov).",
          'columns': [['MANIFEST_NO', 'VARCHAR(10+)', 'Y', 'N', 'Manifest number (TB_R_PRA_DAILY_ORDER_MANIFEST)'],
                      ['MANIFEST_ITEM', 'VARCHAR(4+)', 'Y', 'N', 'Item of the manifest'],
                      ['PO_NO', 'VARCHAR(8+)', '', 'N', 'PO number'],
                      ['PO_ITEM', 'VARCHAR(4+)', '', 'N', 'Item of the PO'],
                      ['PART_NO', 'VARCHAR(12+)', '', 'N', 'Part number'],
                      ['ORDER_QTY', 'NUMERIC', '', 'N', 'PO qty (pcs)'],
                      ['REMAIN_QTY', 'NUMERIC', '', 'N', 'Qty of the PO part not yet in an ASN: open PO qty of XD09; reduced by [Create ASN] (XD10), '
                                                         'added back on Back / Cancel, submit error and XD08 release'],
                      ['CHANGED_BY', 'VARCHAR(20)', '', 'Y', 'Last change user'],
                      ['CHANGED_DT', 'DATETIME', '', 'Y', 'Last change date-time']]}

PAIRS = [
    (f'open PO qty = ORDER_QTY - MAPPED_QTY of {MAPPED} (0 when', f'open PO qty = REMAIN_QTY of {PART} (as is when'),
    (f'MAPPED_QTY of {MAPPED} - their qty', f'REMAIN_QTY of {PART} + their qty'),
    (f'MAPPED_QTY in the new table {MAPPED}', f'REMAIN_QTY of {PART} reduced'),
    (f'MAPPED_QTY of {MAPPED} reduced again', f'REMAIN_QTY of {PART} added back'),
    ('MAPPED_QTY reduced again', 'REMAIN_QTY added back'),
    ('MAPPED_QTY back to 0', 'REMAIN_QTY back to the PO qty'),
    ('MAPPED_QTY PO-0002 6, PO-0003 18', 'REMAIN_QTY PO-0002 6 -> 0, PO-0003 18 -> 0'),
    ('PO_MAPPED_FLAG and MAPPED_QTY', 'PO_MAPPED_FLAG and REMAIN_QTY'),
    ('Open PO qty = ORDER_QTY - MAPPED_QTY.', f'Open PO qty = REMAIN_QTY of {PART}.'),
    ('mapped qty added', 'REMAIN_QTY reduced'),
    (f'{MAPPED} is a new table for the mapped qty.', f'The open PO qty is REMAIN_QTY of the existing {PART} (no new table).'),
    (f'Mapped Qty ({MAPPED})', f'Remaining Qty ({PART}.REMAIN_QTY)'),
    ('ORDER_QTY - MAPPED_QTY', 'REMAIN_QTY'),
]


def walk_replace(o, skip=()):
    if isinstance(o, dict):
        return {k: (v if k in skip else walk_replace(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [walk_replace(v) for v in o]
    if isinstance(o, str):
        for a, b in PAIRS:
            o = o.replace(a, b)
    return o


for fid in ('XD08', 'XD09', 'XD10', 'XD11'):
    path = f'{fid}_spec.json'
    with open(path) as fh:
        s = json.load(fh)
    # tables: the existing part table instead of the new mapped table
    tabs = [t for t in s['tables'] if t['name'] != MAPPED]
    if any(t['name'] == MAPPED for t in s['tables']) and not any(t['name'] == PART for t in tabs):
        tabs.append(T_PART)
    s['tables'] = tabs
    g = s['general']
    if fid == 'XD09':
        g['inputs'] = [i for i in g['inputs'] if i['name'] != MAPPED]
        for i in g['inputs']:
            if PART in i['name']:
                i['description'] = (i.get('description', '') + f' Open PO qty = REMAIN_QTY of {PART}.').strip()
    for o in g.get('outputs', []):
        if o['name'] == MAPPED:
            o['name'] = PART
            o['description'] = 'REMAIN_QTY of the released drafts given back (+ qty)'
    # data map: the mapped-qty block becomes an update of REMAIN_QTY
    for b in s['data_map']['blocks']:
        if b['destination']['table'] != MAPPED:
            continue
        add_back = fid != 'XD10'
        b['destination'] = {'table': PART, 'operation': 'Update',
                            'description': ('REMAIN_QTY given back for the released / moved rows' if add_back
                                            else '[Create ASN]: REMAIN_QTY of every PO part used by the chosen case groups'),
                            'keys': [{'field': 'MANIFEST_NO + MANIFEST_ITEM', 'value': 'PO part of the rows'}]}
        b['mappings'] = [
            {'dest_field': 'REMAIN_QTY', 'description': ('+ qty of the released rows (sum of TB_R_INSTRUCTION.QTY per PO part)' if add_back
                                                         else '- qty of the chosen case groups (sum per PO part); + again on Back / Cancel / submit error')},
            {'dest_field': 'CHANGED_BY', 'description': 'Login user / batch user'},
            {'dest_field': 'CHANGED_DT', 'description': 'Server system date-time'}]
    s = walk_replace(s, skip=('appendix',))
    if fid == 'XD10':
        sec = s['sample_sheet']['sections']
        b = sec[1]
        b['rows'] = [r[:5] + [r[4] - r[5], r[6]] for r in b['rows']]
        for r in sec[4]['rows']:
            if r[0] == MAPPED:
                po = r[1].split(' / ')[0]
                r[0], r[2] = PART, 'REMAIN_QTY'
                r[3], r[4] = (6, 0) if po == 'PO-0002' else (18, 0)
    s = json.loads(json.dumps(s, ensure_ascii=False).replace(MAPPED, PART))
    with open(path, 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', path)
