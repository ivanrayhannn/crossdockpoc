"""F2: split the first band into D-2 (customer order, D1) and D-1 (PO, D2) by inserting two columns (gap + box) after column D.
Works on the xlsx XML so the hand-edited shapes stay editable."""
import re, sys, zipfile, shutil
src, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
files = {n: z.read(n) for n in z.namelist()}
wb = files['xl/workbook.xml'].decode()
rels = files['xl/_rels/workbook.xml.rels'].decode()
rid = re.search(r'<sheet [^>]*name="F2"[^>]*r:id="([^"]+)"', wb).group(1)
sheet = 'xl/' + re.search(r'Id="%s"[^>]*Target="([^"]+)"|Target="([^"]+)"[^>]*Id="%s"' % (rid, rid), rels).group(1 if re.search(r'Id="%s"[^>]*Target' % rid, rels) else 2).lstrip('/').replace('xl/', '')
srel = sheet.replace('worksheets/', 'worksheets/_rels/') + '.rels'
drawing = 'xl/drawings/' + re.search(r'Target="[^"]*drawings/([^"]+)"', files[srel].decode()).group(1)

def cn(col):  # letters -> number
    n = 0
    for ch in col: n = n * 26 + ord(ch) - 64
    return n
def cl(n):
    s = ''
    while n: n, r = divmod(n - 1, 26); s = chr(65 + r) + s
    return s

x = files[sheet].decode()
if 'D-1 &#183; PO' in x or 'D-1 · PO' in x:
    sys.exit('already split')
# columns
cols = re.search(r'<cols>(.*?)</cols>', x).group(1)
defs = re.findall(r'<col [^>]*/>', cols)
new = []
for d in defs:
    mn, mx = int(re.search(r'min="(\d+)"', d).group(1)), int(re.search(r'max="(\d+)"', d).group(1))
    if mn >= 5:
        d = re.sub(r'min="\d+"', f'min="{mn + 2}"', d); d = re.sub(r'max="\d+"', f'max="{mx + 2}"', d)
    new.append(d)
    if mx == 4:
        c3 = next(q for q in defs if 'min="3"' in q); c4 = d
        new.append(re.sub(r'min="\d+" max="\d+"', 'min="5" max="5"', c3)); new.append(re.sub(r'min="\d+" max="\d+"', 'min="6" max="6"', c4))
x = x.replace(cols, ''.join(new))
# cells: shift col >= 5, then add E / F copies of C / D (rows 1-6: style of D, empty)
def shift_ref(m):
    col, row = m.group(1), m.group(2)
    n = cn(col)
    return f'{cl(n + 2) if n >= 5 else col}{row}'
def fix_row(m):
    row_xml = m.group(0)
    if re.match(r'<row [^>]*/>', row_xml): return row_xml
    r = int(re.search(r'<row r="(\d+)"', row_xml).group(1))
    row_xml = re.sub(r'<c r="([A-Z]+)(\d+)"', lambda q: '<c r="' + shift_ref(q) + '"', row_xml)
    row_xml = re.sub(r'spans="1:\d+"', 'spans="1:25"', row_xml)
    style = {c: (re.search(r' s="(\d+)"', a).group(1) if ' s="' in a else None) for c, a in re.findall(r'<c r="([A-Z]+)\d+"([^>]*)>', row_xml)}
    sC, sD = style.get('C'), style.get('D')
    def cell(col, s, text=None):
        sa = f' s="{s}"' if s else ''
        if text: return f'<c r="{col}{r}"{sa} t="inlineStr"><is><t>{text}</t></is></c>'
        return f'<c r="{col}{r}"{sa}/>'
    if r <= 6: add = cell('E', sD) + cell('F', sD)
    elif r == 7: add = cell('E', sC, 'D-1 &#183; PO (existing)') + cell('F', sD)
    else: add = cell('E', sC) + cell('F', sD)
    # insert after the D cell (or before the first cell with col > D)
    md = re.search(r'<c r="D%d"[^>]*/>' % r, row_xml) or re.search(r'<c r="D%d"[^>]*>.*?</c>' % r, row_xml)
    if md: row_xml = row_xml[:md.end()] + add + row_xml[md.end():]
    else:
        mg = re.search(r'<c r="[G-Z]%d"' % r, row_xml)
        row_xml = row_xml[:mg.start()] + add + row_xml[mg.start():] if mg else row_xml.replace('</row>', add + '</row>')
    return row_xml
x = re.sub(r'<row [^>]*[^/]>.*?</row>', fix_row, x, flags=re.S)   # rows without cells (<row .../>) stay
# C7 label (shared string) -> inline
x = re.sub(r'<c r="C7"([^>]*?) t="s"><v>\d+</v></c>', r'<c r="C7"\1 t="inlineStr"><is><t>D-2 &#183; customer order</t></is></c>', x)
# merges
def shift_rng(m):
    a, b = m.group(1).split(':')
    ca, ra = re.match(r'([A-Z]+)(\d+)', a).groups(); cb, rb = re.match(r'([A-Z]+)(\d+)', b).groups()
    na, nb = cn(ca), cn(cb)
    if (ca, cb) in (('C', 'D'), ('A', 'D')) and int(ra) <= 3: nb += 2          # header cells widen over E / F
    else:
        na, nb = (na + 2 if na >= 5 else na), (nb + 2 if nb >= 5 else nb)
    return f'<mergeCell ref="{cl(na)}{ra}:{cl(nb)}{rb}"/>'
x = re.sub(r'<mergeCell ref="([A-Z]+\d+:[A-Z]+\d+)"/>', shift_rng, x)
x = re.sub(r'<mergeCells count="(\d+)">', lambda m: f'<mergeCells count="{int(m.group(1)) + 1}">', x)
x = x.replace('</mergeCells>', '<mergeCell ref="E7:F7"/></mergeCells>')
x = re.sub(r'<dimension ref="A1:[A-Z]+(\d+)"/>', r'<dimension ref="A1:Y\1"/>', x)
files[sheet] = x.encode()
# drawing: shift anchors
d = files[drawing].decode()
anchors = re.findall(r'<xdr:twoCellAnchor[^>]*>[\s\S]*?</xdr:twoCellAnchor>', d)
def box_x(text):
    a = next(a for a in anchors if f'<a:t>{text}</a:t>' in a and '<xdr:col>' in a)
    return int(re.search(r'<a:off x="(-?\d+)"', a).group(1))
D2 = next(t for t in re.findall(r'<a:t>([^<]*)</a:t>', d) if t.startswith('Release PO'))
D3 = next(t for t in re.findall(r'<a:t>([^<]*)</a:t>', d) if t.startswith('Upsert'))
delta = box_x(D3) - box_x(D2)
def moved(col, row):
    if row >= 23: return False                 # legend
    return col >= 4 or (col in (2, 3) and row >= 10)   # D2 and its table move with the new band
def fix_anchor(a):
    fr = re.search(r'<xdr:from><xdr:col>(\d+)</xdr:col>(.*?)<xdr:row>(\d+)</xdr:row>', a)
    to = re.search(r'<xdr:to><xdr:col>(\d+)</xdr:col>(.*?)<xdr:row>(\d+)</xdr:row>', a)
    mf, mt = moved(int(fr.group(1)), int(fr.group(3))), moved(int(to.group(1)), int(to.group(3)))
    if mf: a = a.replace(fr.group(0), f'<xdr:from><xdr:col>{int(fr.group(1)) + 2}</xdr:col>{fr.group(2)}<xdr:row>{fr.group(3)}</xdr:row>', 1)
    if mt: a = a.replace(to.group(0), f'<xdr:to><xdr:col>{int(to.group(1)) + 2}</xdr:col>{to.group(2)}<xdr:row>{to.group(3)}</xdr:row>', 1)
    def off(m):
        xx = int(m.group(1)); return f'<a:off x="{xx + delta if mf else xx}" y="{m.group(2)}"'
    def ext(m):
        cx = int(m.group(1)); cx = cx + delta if (mt and not mf) else cx - delta if (mf and not mt) else cx
        return f'<a:ext cx="{max(cx, 0)}" cy="{m.group(2)}"'
    a = re.sub(r'<a:off x="(-?\d+)" y="(-?\d+)"', off, a, count=1)
    a = re.sub(r'<a:ext cx="(-?\d+)" cy="(-?\d+)"', ext, a, count=1)
    if mt and not mf and '<a:custGeom>' in a:   # stretched elbow (D1 → D3): keep the bend next to the target, not over D2
        cx = int(re.search(r'<a:ext cx="(\d+)"', a).group(1))
        w = int(re.search(r'<a:path w="(\d+)"', a).group(1))
        xs = sorted({int(v) for v in re.findall(r'<a:pt x="(\d+)"', a)})
        bend = [v for v in xs if 0 < v < w]
        a = a.replace(f'<a:path w="{w}"', f'<a:path w="{cx}"')
        for v in bend: a = a.replace(f'<a:pt x="{v}"', f'<a:pt x="{cx - (w - v)}"')
        a = a.replace(f'<a:pt x="{w}"', f'<a:pt x="{cx}"')
    return a
for a in anchors:
    d = d.replace(a, fix_anchor(a), 1)
files[drawing] = d.encode()
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n in z.namelist():
        zo.writestr(z.getinfo(n), files[n])
print('F2 band split; delta', delta, sheet, drawing)
