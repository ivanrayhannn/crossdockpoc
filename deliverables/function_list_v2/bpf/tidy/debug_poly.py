"""Debug copy: every connector becomes a custom-geometry polyline drawn exactly like Excel's preset (for LibreOffice preview)."""
import sys, copy
from lxml import etree
from model import NS
A, Xn = NS['a'], NS['xdr']
for path in sys.argv[1:]:
    t = etree.parse(path)
    for cx in t.getroot().iter('{%s}cxnSp' % Xn):
        sppr = cx.find('xdr:spPr', NS); xf = sppr.find('a:xfrm', NS)
        w, h = int(xf.find('a:ext', NS).get('cx')), int(xf.find('a:ext', NS).get('cy'))
        fh, fv = xf.get('flipH') == '1', xf.get('flipV') == '1'
        pg = sppr.find('a:prstGeom', NS); prst = pg.get('prst')
        gd = pg.find('a:avLst/a:gd', NS); adj = int(gd.get('fmla').split()[1]) / 100000 if gd is not None else .5
        pts = {'straightConnector1': [(0, 0), (w, h)], 'line': [(0, 0), (w, h)], 'bentConnector2': [(0, 0), (w, 0), (w, h)],
               'bentConnector3': [(0, 0), (adj * w, 0), (adj * w, h), (w, h)]}[prst]
        pts = [((w - x) if fh else x, (h - y) if fv else y) for x, y in pts]
        for k in ('flipH', 'flipV'): xf.attrib.pop(k, None)
        cg = etree.Element('{%s}custGeom' % A)
        for tag in ('avLst', 'gdLst', 'ahLst', 'cxnLst'): etree.SubElement(cg, '{%s}%s' % (A, tag))
        etree.SubElement(cg, '{%s}rect' % A, l='0', t='0', r='r', b='b')
        pl = etree.SubElement(etree.SubElement(cg, '{%s}pathLst' % A), '{%s}path' % A, w=str(max(w, 1)), h=str(max(h, 1)), fill='none')
        for i, (x, y) in enumerate(pts):
            e = etree.SubElement(pl, '{%s}%s' % (A, 'moveTo' if i == 0 else 'lnTo'))
            etree.SubElement(e, '{%s}pt' % A, x=str(int(x)), y=str(int(y)))
        sppr.replace(pg, cg)
        # cxnSp -> sp so LibreOffice does not re-route it
        nv = cx.find('xdr:nvCxnSpPr', NS); cnv = nv.find('xdr:cNvPr', NS)
        sp = etree.Element('{%s}sp' % Xn, macro='', textlink='')
        nvs = etree.SubElement(sp, '{%s}nvSpPr' % Xn); nvs.append(copy.deepcopy(cnv)); etree.SubElement(nvs, '{%s}cNvSpPr' % Xn)
        sp.append(sppr)
        cx.getparent().replace(cx, sp)
    t.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)
