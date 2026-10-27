"""Run once after a change of the F2 business logic: python3 patch_f2_manual.py Crossdock_BPF_Level2.xlsx (then build_bpf.py xlsx).
Patch the hand-edited F2 sheet of Crossdock_BPF_Level2.xlsx to the latest business logic (texts, band labels, D14 + badges)."""
import re, sys, zipfile, shutil
src = sys.argv[1]
tmp = src + '.tmp'
zin = zipfile.ZipFile(src)
items = {n: zin.read(n) for n in zin.namelist()}
d = items['xl/drawings/bpfdrawing2.xml'].decode()
T = {
    'Release PO Supplier (CROSSDOCK_FLAG X)': 'Release PO: 1 PO per Part + order date, PO date = D+1, qty = total order',
    'Upsert status 7 rows + status 6 of existing keys (delta INTF_UPDATE_DT)': 'Upsert changed rows; UPD_STATUS 6 / 2; serial split; release drafts',
    'Pre-map order lines to PO (FIFO); Case Qty, PO Readiness, Ready / Not Ready': 'Pre-map in H0253 order; supplier cases, CUT_FLAG; Ready / Not Ready; PO check (Short PO)',
    'Select Ready units ': 'Tick cases: oldest Customer Order Date first, from case 1 up to a cut ',
    'Lock + re-check; pack cases per destination by pcs/case; real mapping': 'Lock + re-check; insert the ticked cases; real mapping; PO_MAPPED_FLAG Y when the whole line is in the ASN',
}
for a, b in T.items():  # idempotent: texts already patched are skipped
    d = d.replace(f'<a:t>{a}</a:t>', f'<a:t>{b}</a:t>')
anchors = re.findall(r'<xdr:twoCellAnchor>[\s\S]*?</xdr:twoCellAnchor>', d)
def find(text):
    return next(a for a in anchors if f'<a:t>{text}</a:t>' in a)
def offx(a):
    return int(re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', a).group(1)), int(re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', a).group(2))
nid = [max(int(i) for i in re.findall(r'<xdr:cNvPr id="(\d+)"', d))]
def clone(a, dcol, drow, dx, dy, name, texts=None, drop_after=None):
    def col(m): return f'<xdr:col>{int(m.group(1)) + dcol}</xdr:col>'
    def row(m): return f'<xdr:row>{int(m.group(1)) + drow}</xdr:row>'
    b = re.sub(r'<xdr:col>(\d+)</xdr:col>', col, a)
    b = re.sub(r'<xdr:row>(\d+)</xdr:row>', row, b)
    b = re.sub(r'<a:off x="(-?\d+)" y="(-?\d+)"', lambda m: f'<a:off x="{int(m.group(1)) + dx}" y="{int(m.group(2)) + dy}"', b)
    nid[0] += 1
    b = re.sub(r'<xdr:cNvPr id="\d+" name="[^"]*"', f'<xdr:cNvPr id="{nid[0]}" name="{name}"', b, count=1)
    for x, y in (texts or {}).items():
        b = b.replace(f'<a:t>{x}</a:t>', f'<a:t>{y}</a:t>')
    if drop_after:  # remove the paragraph holding this text
        b = re.sub(r'<a:p>(?:(?!</a:p>)[\s\S])*?<a:t>' + re.escape(drop_after) + r'</a:t>[\s\S]*?</a:p>', '', b)
    return b
if 'step D14' not in d:
    box12, lab12 = find('ASN feedback: ASN qty known in GTOPAS (basis of the cancel SOP)'), find('D12')
    box13 = find('Check the submit result per Submit ID')
    corner12 = anchors[anchors.index(box12) + 1]       # small corner mark of the D12 box
    dx = offx(box13)[0] - offx(find('ASN Inquiry; download case label (1 label = 1 case of 1 destination)'))[0]
    new = [clone(box12, 2, 0, dx, 0, 'step D14', {'ASN feedback: ASN qty known in GTOPAS (basis of the cancel SOP)':
                 'Receive the ASN → ORDER_STATUS 6; a partial receipt splits the line (new SERIAL_NO); taken by the next XD08 run (D3)'}, drop_after='R: Existing ASN feedback'),
           clone(corner12, 2, 0, dx, 0, 'corner D14'), clone(lab12, 2, 0, dx, 0, 'no D14', {'D12': 'D14'})]
    ab13 = find('AB13')   # badge on D10 (col 17 row 10)
    lab10 = find('D10')
    lab3, ab7 = find('D3'), find('AB07')
    # AB18 on D14 (col 21, row 7), AB17 on D2 (col 3, row 10), AB18 on D3 (left of AB07)
    new.append(clone(ab13, 4, -3, offx(box13)[0] - offx(find('Submit process (Submit ID): ASN No / Case No by existing sequence, ASN Created'))[0],
                     offx(lab12)[1] - offx(lab10)[1], 'ab D14 AB18', {'AB13': 'AB18'}))
    new.append(clone(ab7, -2, 0, offx(find('D2'))[0] - offx(lab3)[0], 0, 'ab D2 AB17', {'AB07': 'AB17'}))
    new.append(clone(ab7, 0, 0, -320000, 0, 'ab D3 AB18', {'AB07': 'AB18'}))
    new[-1] = re.sub(r'(<xdr:from><xdr:col>5</xdr:col><xdr:colOff>)1285875', r'\g<1>965835', new[-1])
    new[-1] = re.sub(r'(<xdr:to><xdr:col>5</xdr:col><xdr:colOff>)1581150', r'\g<1>1261110', new[-1])
    d = d.replace('</xdr:wsDr>', ''.join(new) + '</xdr:wsDr>')
items['xl/drawings/bpfdrawing2.xml'] = d.encode()
s = items['xl/worksheets/sheet2.xml'].decode()
for a, b in [('D-1 &#183; during the day', 'D-1 &#183; customer order / D &#183; PO (existing)'),
             ('27:30 (D 03:30) &#183; job chain XD12 &#8594; XD11 &#8594; XD08', '27:30 (D 03:30) &#183; XD08 (one H0253 batch)'),
             ('Day D &#183; after submit</t>', 'Day D &#183; after submit / receiving</t>')]:
    if a in s: s = s.replace(a, b)
s = re.sub(r'(<c r="Q3"[^>]*><is><t>)[^<]*(</t>)', r'\g<1>27-Oct-26\2', s)
items['xl/worksheets/sheet2.xml'] = s.encode()
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(zin.getinfo(n), items[n])
zin.close()
shutil.move(tmp, src)
print('patched')
