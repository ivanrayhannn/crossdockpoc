"""Re-route connectors of a hand-edited BPF drawing: geometry is computed from the cell anchors of the connected shapes."""
import copy
from lxml import etree
from model import Grid, NS, EMU, shape
A = NS['a']; X = NS['xdr']
SITES = {'rect': {'T': 0, 'L': 1, 'B': 2, 'R': 3}, 'flowChartDecision': {'T': 0, 'L': 1, 'B': 2, 'R': 3},
         'can': {'T': 1, 'L': 2, 'B': 3, 'R': 4}, 'ellipse': {'L': 2, 'B': 4, 'R': 6, 'T': 0}}
PROCESS = '<a:ln xmlns:a="%s" w="12700"><a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:tailEnd type="triangle" w="med" len="med"/></a:ln>' % A
DATA = '<a:ln xmlns:a="%s" w="12700"><a:solidFill><a:srgbClr val="2E75B6"/></a:solidFill><a:prstDash val="dash"/><a:tailEnd type="triangle" w="med" len="med"/></a:ln>' % A

class Drawing:
    def __init__(self, drawing_xml, sheet_xml):
        self.path = drawing_xml
        self.tree = etree.parse(drawing_xml)
        self.g = Grid(sheet_xml)
        self.anc = {}
        for a in self.tree.getroot():
            sp = shape(a)
            if sp is not None:
                self.anc[sp.find('.//xdr:cNvPr', NS).get('id')] = a
    def save(self):
        self.tree.write(self.path, xml_declaration=True, encoding='UTF-8', standalone=True)
    # --- geometry
    def box(self, sid):
        a = self.anc[str(sid)]
        f, t = a.find('xdr:from', NS), a.find('xdr:to', NS)
        v = lambda e, k: int(e.find('xdr:' + k, NS).text)
        return (self.g.x(v(f, 'col'), v(f, 'colOff')), self.g.y(v(f, 'row'), v(f, 'rowOff')), self.g.x(v(t, 'col'), v(t, 'colOff')), self.g.y(v(t, 'row'), v(t, 'rowOff')))
    def set_box(self, sid, b):
        a = self.anc[str(sid)]
        x0, y0, x1, y1 = [int(round(v)) for v in b]
        for tag, (X_, Y_) in (('from', (x0, y0)), ('to', (x1, y1))):
            e = a.find('xdr:' + tag, NS)
            c, co = self.g.to_cell_x(X_); r, ro = self.g.to_cell_y(Y_)
            e.find('xdr:col', NS).text, e.find('xdr:colOff', NS).text = str(c), str(co)
            e.find('xdr:row', NS).text, e.find('xdr:rowOff', NS).text = str(r), str(ro)
        xf = shape(a).find('.//a:xfrm', NS)
        if xf is not None:
            xf.find('a:off', NS).set('x', str(x0)); xf.find('a:off', NS).set('y', str(y0))
            xf.find('a:ext', NS).set('cx', str(x1 - x0)); xf.find('a:ext', NS).set('cy', str(y1 - y0))
    def move(self, ids, dx=0, dy=0):
        for i in ids:
            x0, y0, x1, y1 = self.box(i); self.set_box(i, (x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    def geom(self, sid):
        g = shape(self.anc[str(sid)]).find('.//a:prstGeom', NS)
        return g.get('prst') if g is not None else 'rect'
    def pt(self, spec):
        sid, where = spec[0], spec[1:]
        x0, y0, x1, y1 = self.box(sid)
        if isinstance(where[0], str):
            fx, fy = {'T': (.5, 0), 'B': (.5, 1), 'L': (0, .5), 'R': (1, .5)}[where[0]]
            if len(where) > 1: fx, fy = (where[1], fy) if where[0] in 'TB' else (fx, where[1])
        else:
            fx, fy = where
        return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))
    def remove(self, sid):
        a = self.anc.pop(str(sid)); a.getparent().remove(a)
    def text(self, sid, paras):
        """Replace the text of a shape keeping the run style of the first runs: paras = list of [(text, rgb or None, bold)]."""
        sp = shape(self.anc[str(sid)])
        body = sp.find('xdr:txBody', NS)
        ps = body.findall('a:p', NS)
        tmpl_p = copy.deepcopy(ps[0]); runs = tmpl_p.findall('a:r', NS)
        rpr = copy.deepcopy(runs[-1].find('a:rPr', NS)) if runs and runs[-1].find('a:rPr', NS) is not None else None
        for p in ps: body.remove(p)
        for para in paras:
            p = copy.deepcopy(tmpl_p)
            for r in p.findall('a:r', NS) + p.findall('a:br', NS) + p.findall('a:fld', NS): p.remove(r)
            end = p.find('a:endParaRPr', NS)
            for txt, rgb, bold in para:
                r = etree.SubElement(p, '{%s}r' % A)
                rp = copy.deepcopy(rpr) if rpr is not None else etree.Element('{%s}rPr' % A)
                for f in rp.findall('a:solidFill', NS): rp.remove(f)
                if rgb:
                    sf = etree.SubElement(rp, '{%s}solidFill' % A); etree.SubElement(sf, '{%s}srgbClr' % A).set('val', rgb)
                    rp.insert(0, sf)
                rp.set('b', '1' if bold else '0')
                r.append(rp); etree.SubElement(r, '{%s}t' % A).text = txt
                if end is not None: p.remove(end); p.append(end)
            body.append(p)
    def clone(self, sid, new_id):
        a = copy.deepcopy(self.anc[str(sid)])
        nv = shape(a).find('.//xdr:cNvPr', NS); nv.set('id', str(new_id)); nv.set('name', 'Connector %s' % new_id)
        self.anc[str(sid)].addnext(a); self.anc[str(new_id)] = a
        return new_id
    # --- connectors
    def route(self, cid, start, end, kind, first=None, adj_x=None):
        """start / end = (shape id, side[, fraction]) or (shape id, fx, fy); first = 'h' / 'v' for an L route; adj_x = x of the vertical
        segment of a Z route (H-V-H). kind = 'p' (process) or 'd' (data)."""
        p0, p1 = self.pt(start), self.pt(end)
        cx = shape(self.anc[str(cid)])
        nv = cx.find('xdr:nvCxnSpPr', NS)
        cnv = nv.find('xdr:cNvCxnSpPr', NS)
        for k in list(cnv): cnv.remove(k)
        def cxn(tag, spec):
            if isinstance(spec[1], str) and spec[1] in 'TLBR' and len(spec) == 2:
                g = self.geom(spec[0])
                if g in SITES:
                    e = etree.SubElement(cnv, '{%s}%s' % (A, tag)); e.set('id', str(spec[0])); e.set('idx', str(SITES[g][spec[1]]))
        tail_at_end = True
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        if abs(dx) < 3 * EMU or abs(dy) < 3 * EMU:
            prst = 'straightConnector1'
            if abs(dx) < 3 * EMU: p1 = (p0[0], p1[1])
            else: p1 = (p1[0], p0[1])
            adj = None
            a0, a1 = start, end
        elif first in ('h', 'v'):
            prst, adj = 'bentConnector2', None
            if first == 'h': a0, a1 = start, end
            else: p0, p1, a0, a1, tail_at_end = p1, p0, end, start, False
        else:
            prst = 'bentConnector3'
            xm = adj_x if adj_x is not None else (p0[0] + p1[0]) / 2
            adj = int(round(abs(xm - p0[0]) / abs(p1[0] - p0[0]) * 100000))
            a0, a1 = start, end
        cxn('stCxn', a0); cxn('endCxn', a1)
        x0, x1 = sorted((p0[0], p1[0])); y0, y1 = sorted((p0[1], p1[1]))
        self.set_box(cid, (x0, y0, x1, y1))
        sppr = cx.find('xdr:spPr', NS)
        xf = sppr.find('a:xfrm', NS)
        for k in ('flipH', 'flipV', 'rot'):
            if k in xf.attrib: del xf.attrib[k]
        if p1[0] < p0[0]: xf.set('flipH', '1')
        if p1[1] < p0[1]: xf.set('flipV', '1')
        pg = sppr.find('a:prstGeom', NS)
        pg.set('prst', prst)
        av = pg.find('a:avLst', NS)
        if av is None: av = etree.SubElement(pg, '{%s}avLst' % A)
        for k in list(av): av.remove(k)
        if adj is not None:
            gd = etree.SubElement(av, '{%s}gd' % A); gd.set('name', 'adj1'); gd.set('fmla', 'val %d' % adj)
        old = sppr.find('a:ln', NS)
        new = etree.fromstring(PROCESS if kind == 'p' else DATA)
        if not tail_at_end:
            t = new.find('a:tailEnd', NS); t.tag = '{%s}headEnd' % A
        if old is not None: sppr.replace(old, new)
        else: sppr.append(new)
