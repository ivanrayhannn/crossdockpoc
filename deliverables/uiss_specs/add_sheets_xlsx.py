"""Append the sheets of a source workbook to a (hand-edited) UISS workbook at XML level, so its images, shapes and
layout are kept (openpyxl load / save would drop them). Styles of the copied cells are remapped into the target
workbook, shared strings become inline strings. A sheet whose name already exists in the target is replaced.
Usage: add_sheets_xlsx.py TARGET.xlsx SOURCE.xlsx OUT.xlsx"""
import html, re, sys, zipfile

T, S, OUT = sys.argv[1:4]
zt, zs = zipfile.ZipFile(T), zipfile.ZipFile(S)
files = {i.filename: zt.read(i.filename) for i in zt.infolist()}
order = [i for i in zt.infolist()]


def txt(name, z=None):
    return (z.read(name) if z else files[name]).decode('utf-8')


def sheets(wb, rels):
    out = []
    for m in re.finditer(r'<sheet [^>]*?name="([^"]+)"[^>]*?r:id="([^"]+)"[^>]*/>', wb):
        t = re.search(rf'<Relationship [^>]*Id="{m.group(2)}"[^>]*>', rels).group(0)
        out.append((html.unescape(m.group(1)), m.group(2), 'xl/' + re.search(r'Target="([^"]+)"', t).group(1).lstrip('/').replace('xl/', '', 1), m.group(0)))
    return out


def section(st, tag):
    return re.search(rf'<{tag}\b[^>]*>(.*?)</{tag}>', st, re.S)


def items(body, tag):
    return re.findall(rf'<{tag}\b(?:[^>]*?/>|[^>]*?>.*?</{tag}>)', body, re.S)


# ---- styles
st, ss = txt('xl/styles.xml'), txt('xl/styles.xml', zs)
L = {tag: (items(section(st, tag).group(1), ch), items(section(ss, tag).group(1), ch))
     for tag, ch in (('fonts', 'font'), ('fills', 'fill'), ('borders', 'border'), ('cellXfs', 'xf'))}
nf = lambda s_: {int(i): html.unescape(c) for i, c in re.findall(r'<numFmt numFmtId="(\d+)" formatCode="([^"]*)"', s_)}
nt, ns = nf(st), nf(ss)
norm = lambda s_: re.sub(r'\s+', ' ', s_)


def get(tag, i):
    tt, sl = L[tag]
    x = sl[i]
    for k, y in enumerate(tt):
        if norm(y) == norm(x):
            return k
    tt.append(x)
    return len(tt) - 1


cache = {}


def mapxf(i):
    if i in cache:
        return cache[i]
    x = L['cellXfs'][1][i]
    a = lambda k: int(re.search(rf'\b{k}="(\d+)"', x).group(1)) if re.search(rf'\b{k}="(\d+)"', x) else 0
    n = a('numFmtId')
    if n >= 164:
        hit = [k for k, v in nt.items() if v == ns[n]]
        n = hit[0] if hit else max(list(nt) + [163]) + 1
        nt[n] = ns[a('numFmtId')]
    y = x
    for k, v in (('fontId', get('fonts', a('fontId'))), ('fillId', get('fills', a('fillId'))), ('borderId', get('borders', a('borderId'))),
                 ('numFmtId', n), ('xfId', 0)):
        y = re.sub(rf'\b{k}="\d+"', f'{k}="{v}"', y) if re.search(rf'\b{k}="', y) else y.replace('<xf ', f'<xf {k}="{v}" ', 1)
    tt = L['cellXfs'][0]
    for k, z in enumerate(tt):
        if norm(z) == norm(y):
            cache[i] = k
            return k
    tt.append(y)
    cache[i] = len(tt) - 1
    return cache[i]


sst = []
if 'xl/sharedStrings.xml' in zs.namelist():
    for si in re.findall(r'<si>(.*?)</si>', txt('xl/sharedStrings.xml', zs), re.S):
        sst.append(''.join(re.findall(r'<t[^>]*>(.*?)</t>', si, re.S)))

wb, rels, ct = txt('xl/workbook.xml'), txt('xl/_rels/workbook.xml.rels'), txt('[Content_Types].xml')
have = {n: (rid, p, tag) for n, rid, p, tag in sheets(wb, rels)}
for name, _, sp, _ in sheets(txt('xl/workbook.xml', zs), txt('xl/_rels/workbook.xml.rels', zs)):
    x = txt(sp, zs)
    x = re.sub(r'<c ([^>]*?)t="s"([^>]*)><v>(\d+)</v></c>',
               lambda m: f'<c {m.group(1)}t="inlineStr"{m.group(2)}><is><t xml:space="preserve">{sst[int(m.group(3))]}</t></is></c>', x)
    x = re.sub(r'(<c [^>]*?\bs=")(\d+)"', lambda m: f'{m.group(1)}{mapxf(int(m.group(2)))}"', x)
    x = re.sub(r'(<row [^>]*?\bs=")(\d+)"', lambda m: f'{m.group(1)}{mapxf(int(m.group(2)))}"', x)
    x = re.sub(r'(<col [^>]*?\bstyle=")(\d+)"', lambda m: f'{m.group(1)}{mapxf(int(m.group(2)))}"', x)
    x = re.sub(r'<sheetView ([^>]*?)tabSelected="1"', r'<sheetView \1', x)
    if name in have:
        files[have[name][1]] = x.encode()
        continue
    n = max(int(k) for k in re.findall(r'xl/worksheets/sheet(\d+)\.xml', ' '.join(files))) + 1
    path = f'xl/worksheets/sheet{n}.xml'
    rid = 'rId' + str(max(int(k) for k in re.findall(r'Id="rId(\d+)"', rels)) + 1)
    sid = max(int(k) for k in re.findall(r'sheetId="(\d+)"', wb)) + 1
    files[path] = x.encode()
    order.append(zipfile.ZipInfo(path))
    rels = rels.replace('</Relationships>', f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{n}.xml"/></Relationships>')
    wb = wb.replace('</sheets>', f'<sheet name="{html.escape(name)}" sheetId="{sid}" r:id="{rid}"/></sheets>')
    ct = ct.replace('</Types>', f'<Override PartName="/{path}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')


def rebuild(s_, tag, lst):
    m = section(s_, tag)
    head = re.sub(r'count="\d+"', f'count="{len(lst)}"', s_[m.start():m.start(1)])
    return s_[:m.start()] + head + ''.join(lst) + f'</{tag}>' + s_[m.end():]


for tag in ('fonts', 'fills', 'borders', 'cellXfs'):
    st = rebuild(st, tag, L[tag][0])
nfx = ''.join(f'<numFmt numFmtId="{k}" formatCode="{html.escape(v, quote=True)}"/>' for k, v in sorted(nt.items()))
if section(st, 'numFmts'):
    st = rebuild(st, 'numFmts', [nfx])
elif nt:
    st = st.replace('<fonts', f'<numFmts count="{len(nt)}">{nfx}</numFmts><fonts', 1)
files['xl/styles.xml'], files['xl/workbook.xml'] = st.encode(), wb.encode()
files['xl/_rels/workbook.xml.rels'], files['[Content_Types].xml'] = rels.encode(), ct.encode()
if 'docProps/app.xml' in files:   # sheet titles in the document properties are optional; drop them so they never disagree
    a = txt('docProps/app.xml')
    a = re.sub(r'<HeadingPairs>.*?</HeadingPairs>|<TitlesOfParts>.*?</TitlesOfParts>', '', a, flags=re.S)
    files['docProps/app.xml'] = a.encode()
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for i in order:
        zo.writestr(i.filename, files[i.filename])
print('sheets now:', [n for n, *_ in sheets(wb, rels)])
