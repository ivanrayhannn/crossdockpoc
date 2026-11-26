"""26-Nov (c), XD07 after the template LLM9Q910 (received 26-Nov) and the user's decisions:
- Effective Month and Effective Year are two template columns; the robot splits EFFECTIVE_MONTH_YEAR (MM/YYYY) of the view.
- Kanban Max Allowance Qty is not filled (AP POLE calculates it).
- Part No. of the Kanban file keeps "-" for now.
Template layout: row 1 title, row 3 header, data from row 4. Revision XD07 1.4."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = '26-Nov-26'
NOTE = ('Upload files after the template LLM9Q910: Effective Month and Effective Year in two columns (the robot splits EFFECTIVE_MONTH_YEAR '
        'of the view); Kanban Max Allowance Qty left empty (AP POLE calculates it); data from row 4 of the templates.')
SPLIT = [{'source_field': 'EFFECTIVE_MONTH_YEAR', 'dest_field': 'Effective Month', 'description': 'MM part of MM/YYYY, split by the robot'},
         {'source_field': 'EFFECTIVE_MONTH_YEAR', 'dest_field': 'Effective Year', 'description': 'YYYY part of MM/YYYY, split by the robot'}]
EMPTY_KAN = ('Packing/Pallet Type, Recv Area Code, Location No, Recv Contain Box Code, Store, Inner 1 / 2 / 3 / M-PKG Part No. / Location / Qty, '
             'Outer-PKG Part No. / Location / Qty')

p = os.path.join(HERE, 'XD07_spec.json')
s = json.load(open(p))
if not any(r['description'].startswith('Upload files after the template LLM9Q910') for r in s['revisions']):
    for b in s['data_map']['blocks'][:2]:
        out = []
        for m in b['mappings']:
            if m['source_field'] == 'EFFECTIVE_MONTH_YEAR':
                out += json.loads(json.dumps(SPLIT))
            elif m['source_field'] == 'MAX_ALLOWANCE_QTY':
                out.append({'source_field': '-', 'dest_field': 'Max Allowance Qty', 'description': 'Empty (AP POLE calculates it)'})
            else:
                out.append(m)
        b['mappings'] = out
    for t in s['general']['extra_tables']:
        if not t.get('title', '').startswith('LLM9Q'):
            continue
        rows = []
        for r in t['rows']:
            if r[0] == 'Effective Month / Year':
                rows += [['Effective Month', 'MM of EFFECTIVE_MONTH_YEAR (the robot splits MM/YYYY of the view)'],
                         ['Effective Year', 'YYYY of EFFECTIVE_MONTH_YEAR']]
            elif r[0] == 'Max Allowance Qty' and t['title'].startswith('LLM9Q910'):
                rows.append(['Max Allowance Qty', 'Empty (AP POLE calculates it)'])
            elif r[0] == 'Packing/Pallet Type ... Outer-Qty':
                rows.append([EMPTY_KAN, 'Empty'])
            else:
                rows.append(r)
        rows.append(['Layout', 'Row 1 title, row 3 header, data from row 4'])
        t['rows'] = rows
    for st in s['func_flow']['steps']:
        if isinstance(st, dict) and st.get('text', '').startswith('Fill the stored templates'):
            st['text'] = st['text'].replace('(Effective Month / Year per row)', '(Effective Month and Effective Year per row, split from MM/YYYY; data from row 4)')
    s['revisions'].append({'revision': '1.4', 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': NOTE})
    s['header']['updated_date'] = D
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched XD07')
