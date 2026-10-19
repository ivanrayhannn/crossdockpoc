"""Editable diagram of the BPF level 2: the layout of the prototype page (BusinessProcessFlowPage.tsx) in Python, written as
- native Excel shapes (DrawingML, one drawing per flow sheet): boxes, lanes, timeline bands, arrows and abnormality tags;
- a draw.io file (one page per flow) whose arrows are glued to the boxes (can be exported to Visio / PNG in diagrams.net)."""
import math
from xml.sax.saxutils import escape

AXIS_W, LANE_W, BOX_W, HEADER_H, GAP = 150, 230, 200, 44, 38
EMU = 9525  # per pixel
LANE_COLOR = {'GT': ('EDEDED', '8C8C8C'), 'NB': ('DBE5F4', '5B7BB4'), 'PR': ('E3F1DF', '6A9F5B'),
              'DS': ('FDE4D4', 'D08A5C'), 'SP': ('FFF2CC', 'C9A63B'), 'AP': ('ECE4F5', '8A6FB5')}
NAVY, EDGE, RED = '1F3864', '4A5A75', 'C00000'


def _lines(s, per):
    return max(1, math.ceil(len(s) / per))


def box_h(s):
    h = 10 + 14 + _lines(s['title'], 31) * 12.5
    for lst in (s['read'], s['write']):
        if lst:
            h += 4 + sum(_lines(t, 33) * 11 for t in lst)
    return math.ceil(h + 8)


def label(s):
    return s['fn'] or ('Receive' if s['read'] else 'Source')


def layout(flow):
    start, n, bands = {}, 0, []
    for bid, text, slots in flow['bands']:
        start[bid] = n
        n += slots
        bands.append((bid, text, start[bid], n - 1))
    row = {s['id']: start[s['band']] + s['slot'] for s in flow['steps']}
    bh = {s['id']: box_h(s) for s in flow['steps']}
    rh = [56] * n
    for s in flow['steps']:
        rh[row[s['id']]] = max(rh[row[s['id']]], bh[s['id']])
    top, y = [], HEADER_H + GAP / 2 + 6
    for i in range(n):
        top.append(y)
        y += rh[i] + GAP
    boxes = {}
    for s in flow['steps']:
        li = flow['lanes'].index(s['lane'])
        boxes[s['id']] = (AXIS_W + li * LANE_W + (LANE_W - BOX_W) / 2, top[row[s['id']]], BOX_W, bh[s['id']])
    return dict(width=AXIS_W + len(flow['lanes']) * LANE_W, height=y - GAP / 2 + 6, top=top, rh=rh, row=row, bands=bands, boxes=boxes)


def edge_points(flow, L, a, b, k):
    la, lb = flow['lanes'].index(a['lane']), flow['lanes'].index(b['lane'])
    sx, tx = AXIS_W + la * LANE_W + LANE_W / 2, AXIS_W + lb * LANE_W + LANE_W / 2
    ra, rb = L['row'][a['id']], L['row'][b['id']]
    _, s_top, _, ha = L['boxes'][a['id']]
    hb = L['boxes'][b['id']][3]
    sb, tt = s_top + ha, L['top'][rb]
    if ra == rb:
        y = s_top + min(ha, hb) / 2
        return [(sx + BOX_W / 2 if lb > la else sx - BOX_W / 2, y), (tx - BOX_W / 2 if lb > la else tx + BOX_W / 2, y)]
    gap_below = L['top'][ra] + L['rh'][ra] + GAP / 2 + (k % 3) * 4 - 4
    gap_above = tt - GAP / 2 + (k % 3) * 4 - 4
    if rb == ra + 1:
        return [(sx, sb), (sx, tt)] if la == lb else [(sx, sb), (sx, gap_above), (tx, gap_above), (tx, tt)]
    edge = AXIS_W + la * LANE_W if lb < la else AXIS_W + (la + 1) * LANE_W
    cx = edge + (1 if lb < la else -1) * (5 + (k % 3) * 3)
    return [(sx, sb), (sx, gap_below), (cx, gap_below), (cx, gap_above), (tx, gap_above), (tx, tt)]


def edges(flow):
    by = {s['id']: s for s in flow['steps']}
    return [(s, by[t]) for s in flow['steps'] for t in s['next']]


# ------------------------------------------------------------------ Excel DrawingML
class _Drawing:
    def __init__(self, x0, y0):
        self.x0, self.y0, self.parts, self.n = x0, y0, [], 1

    def _anchor(self, x, y, w, h, body):
        e = lambda v: int(round(v * EMU))  # noqa: E731
        self.parts.append(f'<xdr:absoluteAnchor><xdr:pos x="{e(self.x0 + x)}" y="{e(self.y0 + y)}"/><xdr:ext cx="{max(e(w), 1)}" cy="{max(e(h), 1)}"/>'
                          f'{body}<xdr:clientData/></xdr:absoluteAnchor>')

    def _id(self):
        self.n += 1
        return self.n

    def shape(self, name, x, y, w, h, fill=None, line=None, dash=False, prst='rect', paras=(), anchor='t', ins=3, line_w=1.0):
        e = lambda v: int(round(v * EMU))  # noqa: E731
        geom = (f'<a:prstGeom prst="{prst}"><a:avLst>' + ('<a:gd name="adj" fmla="val 5000"/>' if prst == 'roundRect' else '') + '</a:avLst></a:prstGeom>')
        fill_x = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
        line_x = (f'<a:ln w="{int(line_w * 12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>' + ('<a:prstDash val="dash"/>' if dash else '') + '</a:ln>'
                  if line else '<a:ln><a:noFill/></a:ln>')
        txt = ''
        if paras:
            ps = ''
            for runs, algn in paras:
                rs = ''.join(f'<a:r><a:rPr lang="en-US" sz="{sz}" b="{1 if b else 0}" dirty="0"><a:solidFill><a:srgbClr val="{c}"/></a:solidFill>'
                             f'<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>{escape(t)}</a:t></a:r>' for t, sz, b, c in runs)
                ps += f'<a:p><a:pPr algn="{algn}"/>{rs}</a:p>'
            i = e(ins)
            txt = (f'<xdr:txBody><a:bodyPr vertOverflow="overflow" horzOverflow="overflow" wrap="square" lIns="{i}" tIns="{i}" rIns="{i}" bIns="{i}" anchor="{anchor}">'
                   f'<a:noAutofit/></a:bodyPr><a:lstStyle/>{ps}</xdr:txBody>')
        sid = self._id()
        body = (f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{sid}" name="{escape(name)}"/><xdr:cNvSpPr/></xdr:nvSpPr>'
                f'<xdr:spPr><a:xfrm><a:off x="{e(self.x0 + x)}" y="{e(self.y0 + y)}"/><a:ext cx="{max(e(w), 1)}" cy="{max(e(h), 1)}"/></a:xfrm>'
                f'{geom}{fill_x}{line_x}</xdr:spPr>{txt}</xdr:sp>')
        self._anchor(x, y, w, h, body)

    def path(self, name, pts, color=EDGE, arrow=True, dash=False, width=1.25):
        e = lambda v: int(round(v * EMU))  # noqa: E731
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x, y = min(xs), min(ys)
        w, h = max(max(xs) - x, 1), max(max(ys) - y, 1)
        seg = ''.join((f'<a:moveTo>' if i == 0 else '<a:lnTo>') + f'<a:pt x="{e(px - x)}" y="{e(py - y)}"/>' + ('</a:moveTo>' if i == 0 else '</a:lnTo>')
                      for i, (px, py) in enumerate(pts))
        sid = self._id()
        body = (f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{sid}" name="{escape(name)}"/><xdr:cNvSpPr/></xdr:nvSpPr>'
                f'<xdr:spPr><a:xfrm><a:off x="{e(self.x0 + x)}" y="{e(self.y0 + y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
                f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
                f'<a:pathLst><a:path w="{e(w)}" h="{e(h)}" fill="none">{seg}</a:path></a:pathLst></a:custGeom><a:noFill/>'
                f'<a:ln w="{int(width * 12700)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' + ('<a:prstDash val="dash"/>' if dash else '')
                + ('<a:tailEnd type="triangle" w="med" len="med"/>' if arrow else '') + '</a:ln></xdr:spPr></xdr:sp>')
        self._anchor(x, y, w, h, body)

    def xml(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">' + ''.join(self.parts) + '</xdr:wsDr>')


def excel_drawing(flow, lanes, y0):
    """DrawingML of one flow, drawn at y0 px from the top of the sheet. Returns (xml, height px)."""
    L = layout(flow)
    d = _Drawing(4, y0)
    W = L['width']
    for i, (bid, text, first, last) in enumerate(L['bands']):
        ya = L['top'][first] - GAP / 2
        yb = L['top'][last] + L['rh'][last] + GAP / 2
        d.shape(f'band {bid}', 0, ya, W, yb - ya, fill='F6F8FB' if i % 2 == 0 else 'FFFFFF', line='C4CCD8', line_w=0.5)
        d.shape(f'timeline {bid}', 0, ya, AXIS_W, yb - ya, fill=NAVY if i % 2 == 0 else '44546A',
                paras=[([(text, 800, True, 'FFFFFF')], 'l')], anchor='ctr', ins=6)
    d.shape('header timeline', 0, 4, AXIS_W - 4, HEADER_H - 8, fill=NAVY, prst='roundRect',
            paras=[([('Timeline ↓ / PIC →', 800, True, 'FFFFFF')], 'ctr')], anchor='ctr')
    for i, k in enumerate(flow['lanes']):
        bg, bd = LANE_COLOR[k]
        d.shape(f'lane {k}', AXIS_W + i * LANE_W + 2, 4, LANE_W - 4, HEADER_H - 8, fill=bg, line=bd, prst='roundRect',
                paras=[([(lanes[k], 900, True, '1F2A3D')], 'ctr')], anchor='ctr')
        if i:
            d.path(f'lane line {k}', [(AXIS_W + i * LANE_W, HEADER_H), (AXIS_W + i * LANE_W, L['height'])], color='B7C0CD', arrow=False, dash=True, width=0.75)
    for k, (a, b) in enumerate(edges(flow)):
        d.path(f'arrow {a["id"]}-{b["id"]}', edge_points(flow, L, a, b, k))
    for s in flow['steps']:
        x, y, w, h = L['boxes'][s['id']]
        bg, bd = LANE_COLOR[s['lane']]
        paras = [([(label(s) + '   ', 750, True, RED), (s['id'], 750, True, '6B7A90')], 'l'), ([(s['title'], 750, True, '1F2A3D')], 'l')]
        paras += [([('R: ' + t, 675, False, '2F5597')], 'l') for t in s['read']]
        paras += [([('W: ' + t, 675, False, '7B3F00')], 'l') for t in s['write']]
        d.shape(f'step {s["id"]}', x, y, w, h, fill=bg, line=bd, prst='roundRect', dash=s['fn'] in ('existing', 'manual'), paras=paras)
        for i, ab in enumerate(s['ab']):
            d.shape(f'tag {s["id"]} {ab}', x + w - 40 - i * 42, y - 9, 38, 14, fill=RED, prst='roundRect',
                    paras=[([(ab, 650, True, 'FFFFFF')], 'ctr')], anchor='ctr', ins=0)
    return d.xml(), L['height']


# ------------------------------------------------------------------ draw.io
def drawio(flows, lanes):
    pages = []
    for flow in flows:
        L = layout(flow)
        cells, n = ['<mxCell id="0"/><mxCell id="1" parent="0"/>'], [1]

        def cell(value, style, x, y, w, h, cid=None):
            n[0] += 1
            cid = cid or f'c{n[0]}'
            cells.append(f'<mxCell id="{cid}" value="{escape(value, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="1">'
                         f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
        W = L['width']
        for i, (bid, text, first, last) in enumerate(L['bands']):
            ya = L['top'][first] - GAP / 2
            yb = L['top'][last] + L['rh'][last] + GAP / 2
            cell('', f'rounded=0;whiteSpace=wrap;fillColor=#{"F6F8FB" if i % 2 == 0 else "FFFFFF"};strokeColor=#C4CCD8;', 0, ya, W, yb - ya)
            cell(text, f'rounded=0;whiteSpace=wrap;html=1;fillColor=#{NAVY if i % 2 == 0 else "44546A"};strokeColor=none;fontColor=#FFFFFF;'
                       'fontStyle=1;fontSize=11;align=left;spacingLeft=6;', 0, ya, AXIS_W, yb - ya)
        cell('Timeline ↓ / PIC →', f'rounded=1;whiteSpace=wrap;fillColor=#{NAVY};strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=11;', 0, 4, AXIS_W - 4, HEADER_H - 8)
        for i, k in enumerate(flow['lanes']):
            bg, bd = LANE_COLOR[k]
            cell(lanes[k], f'rounded=1;whiteSpace=wrap;fillColor=#{bg};strokeColor=#{bd};fontStyle=1;fontSize=12;', AXIS_W + i * LANE_W + 2, 4, LANE_W - 4, HEADER_H - 8)
        for s in flow['steps']:
            x, y, w, h = L['boxes'][s['id']]
            bg, bd = LANE_COLOR[s['lane']]
            v = (f'<div style="display:flex;justify-content:space-between"><b style="color:#C00000">{escape(label(s))}</b><b style="color:#6B7A90">{s["id"]}</b></div>'
                 f'<b>{escape(s["title"])}</b>'
                 + ''.join(f'<br><font style="font-size:9px" color="#2F5597">R: {escape(t)}</font>' for t in s['read'])
                 + ''.join(f'<br><font style="font-size:9px" color="#7B3F00">W: {escape(t)}</font>' for t in s['write']))
            dash = 'dashed=1;' if s['fn'] in ('existing', 'manual') else ''
            cell(v, f'rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=#{bg};strokeColor=#{bd};{dash}align=left;verticalAlign=top;'
                    'spacingLeft=6;spacingRight=6;spacingTop=2;fontSize=10;fontColor=#1F2A3D;', x, y, w, h, cid=f'{flow["id"]}_{s["id"]}')
            for i, ab in enumerate(s['ab']):
                cell(ab, 'rounded=1;arcSize=50;whiteSpace=wrap;fillColor=#C00000;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=9;',
                     x + w - 40 - i * 42, y - 9, 38, 14)
        for k, (a, b) in enumerate(edges(flow)):
            n[0] += 1
            same_row = L['row'][a['id']] == L['row'][b['id']]
            ports = 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;' if same_row and flow['lanes'].index(b['lane']) > flow['lanes'].index(a['lane']) else \
                    'exitX=0;exitY=0.5;entryX=1;entryY=0.5;' if same_row else 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'
            pts = edge_points(flow, L, a, b, k)[1:-1]
            geo = ('<Array as="points">' + ''.join(f'<mxPoint x="{px:.0f}" y="{py:.0f}"/>' for px, py in pts) + '</Array>') if pts else ''
            cells.append(f'<mxCell id="e{n[0]}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#{EDGE};{ports}" '
                         f'edge="1" parent="1" source="{flow["id"]}_{a["id"]}" target="{flow["id"]}_{b["id"]}">'
                         f'<mxGeometry relative="1" as="geometry">{geo}</mxGeometry></mxCell>')
        pages.append(f'<diagram id="{flow["id"]}" name="{escape(flow["id"] + " " + flow["title"])}"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" '
                     f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{int(W) + 40}" pageHeight="{int(L["height"]) + 40}" '
                     f'math="0" shadow="0"><root>{"".join(cells)}</root></mxGraphModel></diagram>')
    return '<mxfile host="build_bpf.py" type="device">' + ''.join(pages) + '</mxfile>'
