"""11-Nov: FB-172 the pouring of the PO qty (Part Number level) over the customer order lines, line by line from the top,
is written out in XD09 4.2 (rules, step table, sample section) and referenced from XD10."""
import json

POUR_RULES = [
    'One PO per Part Number per Customer Order Date: PO date = order date + 1, PO qty = total order qty of all destinations of that date. Open PO qty = ORDER_QTY - MAPPED_QTY.',
    'Pouring (Part Number level): the open PO qty of the part is poured over the customer order lines from the top of the list (order of 4.1, oldest unit first) down, like filling holes one after the other.',
    'Each line takes its qty from the oldest PO that still has qty left (PO_DT, then PO No). The PO is used up before the next PO is taken; what is left of a PO goes on to the next line, also of the next Customer Order Date.',
    'PO left < qty of the line: the line is split. The first part gets the rest of this PO; the rest goes on to the next PO (one row per PO). Example: line 6 pcs, PO A has 2 left, PO B has 10 -> 2 rows: PO A 2, PO B 4.',
    'No PO left: the rest of the line is still written, with PO_NO NULL (not skipped). Example: line 6 pcs, PO A has 2 left, no other PO -> 2 rows: PO A 2, PO_NO NULL 4. The lines below also get PO_NO NULL.',
    'The qty written in each row is ASSIGNED_QTY; the sum of ASSIGNED_QTY of a line = its open qty. A PO qty left by an order that is not sent goes to the next lines: PO-0001 (CO-14102 on hold, then cancelled) covers CO-14103; PO-0002 then covers CO-14105.',
    'PO qty lower than the order qty of the date (Short PO) is an abnormality: order date 17-Oct = 30 pcs, PO left 24 (PO-0002 6 + PO-0003 18); the last 6 pcs (CO-14110) have no PO (PO_NO NULL) and wait for the split PO PO-0004 of 19-Oct.',
]
STEPS = [  # line, qty, PO (assigned), PO-0002 left, PO-0003 left
    ['Start', '', '', '6', '18'],
    ['1 CO-14105 (9715310)', '6', 'PO-0002 6', '0', '18'],
    ['2 CO-14106 (9715310)', '3', 'PO-0003 3', '0', '15'],
    ['3 CO-14107 (9715310)', '3', 'PO-0003 3', '0', '12'],
    ['4 CO-14104 (9722D10)', '6', 'PO-0003 6', '0', '6'],
    ['5 CO-14109 (9811110)', '6', 'PO-0003 6', '0', '0'],
    ['6 CO-14110 (982220)', '6', 'PO_NO NULL 6', '0', '0'],
    ['Total', '30', '24 with PO + 6 without', '', ''],
]

with open('XD09_spec.json') as fh:
    s = json.load(fh)
fd = s['func_desc']
i = next(k for k, b in enumerate(fd) if b.get('type') == 'heading' and b.get('text', '').startswith('4.2'))
assert fd[i + 1]['type'] == 'bullets'
fd[i + 1]['items'] = POUR_RULES
cb = next(k for k, b in enumerate(fd) if b.get('type') == 'column_break')
fd.insert(cb + 1, {'type': 'heading', 'text': '4.2 PO Assignment - example of the pouring'})
fd.insert(cb + 2, {'type': 'text', 'level': 0, 'text': '18-Oct [Search], order date 17-Oct, PART-X: PO left of the part (PO-0002 6 + PO-0003 18 = 24) poured from the top line down; 30 pcs ordered.'})
fd.insert(cb + 3, {'type': 'table', 'level': 0, 'row_lines': 'all',
                  'columns': [{'title': 'Line (order of 4.1)', 'width': 15}, {'title': 'Qty', 'width': 4}, {'title': 'PO (ASSIGNED_QTY)', 'width': 11},
                              {'title': 'PO-0002 left', 'width': 7}, {'title': 'PO-0003 left', 'width': 7}],
                  'rows': STEPS})
st = s['func_flow']['steps'][3]
st['children'][1] = ('Pour the open PO qty of the part (PO_DT, then PO No) over the lines from the top down: each line takes from the oldest PO with qty left; '
                     'PO left < line qty -> the line is split per PO; no PO left -> the rest of the line gets PO_NO NULL (see 4.2).')
sec = {'title': 'C1. 18-Oct: pouring the PO qty of PART-X over the lines of order date 17-Oct (top line first)',
       'columns': ['Step', 'Customer Order No', 'Destination', 'Qty', 'PO taken', 'ASSIGNED_QTY', 'PO-0002 left (PO date 17-Oct)', 'PO-0003 left (PO date 18-Oct)'],
       'widths': [6, 16, 12, 6, 12, 13, 24, 24],
       'rows': [['Start', '', '', '', '', '', 6, 18],
                [1, 'CO-14105', '9715310', 6, 'PO-0002', 6, 0, 18],
                [2, 'CO-14106', '9715310', 3, 'PO-0003', 3, 0, 15],
                [3, 'CO-14107', '9715310', 3, 'PO-0003', 3, 0, 12],
                [4, 'CO-14104', '9722D10', 6, 'PO-0003', 6, 0, 6],
                [5, 'CO-14109', '9811110', 6, 'PO-0003', 6, 0, 0],
                [6, 'CO-14110', '982220', 6, '- (no PO left)', 6, 0, 0],
                ['Total', '', '', 30, '', '24 with PO, 6 PO_NO NULL', '', '']]}
secs = s['sample_sheet']['sections']
k = next(n for n, x in enumerate(secs) if x['title'].startswith('C. 18-Oct'))
secs.insert(k + 1, sec)
with open('XD09_spec.json', 'w') as fh:
    json.dump(s, fh, indent=1, ensure_ascii=False)
print('patched XD09_spec.json')

with open('XD10_spec.json') as fh:
    t = fh.read()
a = 'pre-mapped to the PO parts of the Pra Daily Order (PO date order)'
assert a in t
t = t.replace(a, 'pre-mapped to the PO parts of the Pra Daily Order (PO qty of the part poured over the lines from the top down, oldest PO first; refer UISS-Batch XD09 4.2)')
with open('XD10_spec.json', 'w') as fh:
    fh.write(t)
print('patched XD10_spec.json')
