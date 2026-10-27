"""F2 (28-Oct): step numbers on the existing boxes, as in Step Detail: D0 AP POLE release, D12 / D13 interfaces, D14 / D15 receiving; AB18 on D15.
Usage: add_f2_badges.py <unzipped xlsx dir> <drawing of F2>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from router import Drawing, shape, NS
X, DRAW = sys.argv[1], sys.argv[2]
d = Drawing(f'{X}/xl/drawings/{DRAW}', f'{X}/xl/worksheets/sheet2.xml')
for i in [str(n) for n in range(501, 507)]:                 # re-create (idempotent)
    if i in d.anc: d.remove(i)
names = {shape(a).find('.//xdr:cNvPr', NS).get('name') for a in d.anc.values()}
step, badge = d.box(30), d.box(32)                      # D3 box and its number badge as template
dx, dy, w, h = badge[0] - step[0], badge[1] - step[1], badge[2] - badge[0], badge[3] - badge[1]
for new_id, (box, code) in zip(range(501, 506), [(24, 'D0'), (180, 'D12'), (64, 'D13'), (162, 'D14'), (201, 'D15')]):
    if f'no {code}' in names:
        continue
    d.clone(32, new_id)
    shape(d.anc[str(new_id)]).find('.//xdr:cNvPr', NS).set('name', f'no {code}')
    x0, y0 = d.box(box)[:2]
    d.set_box(new_id, (x0 + dx, y0 + dy, x0 + dx + w, y0 + dy + h))
    d.text(new_id, [[(code, 'FFFFFF', True)]])
# AB18 (partial receipt splits the line) also on D15, placed like AB18 on D3
if 'ab D15 AB18' not in names:
    ab, b3, b15 = d.box(167), d.box(30), d.box(201)
    d.clone(167, 506)
    shape(d.anc['506']).find('.//xdr:cNvPr', NS).set('name', 'ab D15 AB18')
    rx = ab[0] - b3[2]                                   # offset from the right edge of the box
    d.set_box(506, (b15[2] + rx, b15[1] + ab[1] - b3[1], b15[2] + rx + ab[2] - ab[0], b15[1] + ab[3] - b3[1]))
# badges on top of the boxes (last in the drawing = front)
root = d.tree.getroot()
for i in ['501', '502', '503', '504', '505', '506']:
    if i in d.anc:
        root.remove(d.anc[i]); root.append(d.anc[i])
d.save()
print('badges added')
