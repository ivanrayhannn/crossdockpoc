import re, math
from lxml import etree
NS = {'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing', 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
EMU = 9525
def px_w(w): return math.trunc(((256 * w + math.trunc(128 / 7)) / 256) * 7)
class Grid:
    def __init__(self, sheet_xml):
        s = open(sheet_xml).read()
        self.cw = {}
        for m in re.finditer(r'<col min="(\d+)" max="(\d+)" width="([\d.]+)"', s):
            for c in range(int(m[1]), int(m[2]) + 1): self.cw[c - 1] = px_w(float(m[3]))
        dh = float(re.search(r'defaultRowHeight="([\d.]+)"', s)[1])
        self.rh = {}
        for m in re.finditer(r'<row r="(\d+)"[^>]*?ht="([\d.]+)"', s):
            self.rh[int(m[1]) - 1] = float(m[2])
        self.dh = dh
    def colw(self, c): return self.cw.get(c, 64) * EMU
    def rowh(self, r): return round(self.rh.get(r, self.dh) * 12700)
    def x(self, col, off): return sum(self.colw(c) for c in range(col)) + off
    def y(self, row, off): return sum(self.rowh(r) for r in range(row)) + off
    def to_cell_x(self, X):
        c = 0
        while X >= self.colw(c): X -= self.colw(c); c += 1
        return c, int(X)
    def to_cell_y(self, Y):
        r = 0
        while Y >= self.rowh(r): Y -= self.rowh(r); r += 1
        return r, int(Y)
def anchors(path):
    t = etree.parse(path)
    return t, list(t.getroot())
def anc_box(g, anc):
    f, t = anc.find('xdr:from', NS), anc.find('xdr:to', NS)
    g1 = lambda e, k: int(e.find('xdr:' + k, NS).text)
    return (g.x(g1(f, 'col'), g1(f, 'colOff')), g.y(g1(f, 'row'), g1(f, 'rowOff')), g.x(g1(t, 'col'), g1(t, 'colOff')), g.y(g1(t, 'row'), g1(t, 'rowOff')))
def shape(anc):
    for el in anc:
        if etree.QName(el).localname in ('sp', 'cxnSp', 'grpSp', 'pic'): return el
