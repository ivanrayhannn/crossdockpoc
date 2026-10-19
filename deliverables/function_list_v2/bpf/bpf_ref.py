"""BPF level 2 in the house format of the reference BPF (BPF_E-DCL): document header block, title bar, timeline in columns,
PIC lanes in rows (two-level rotated labels), grid by cell borders; processes, DB storage (tables), tags, arrows and legend
as shapes anchored to the cells. The same geometry is written to draw.io (arrows glued to the shapes)."""
import math
from xml.sax.saxutils import escape
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ORDER = ['GT', 'NB', 'DB', 'PR', 'DS', 'SP', 'AP']
LANE_NAME = {'GT': 'G-TOPAS /\nDB Surrounding', 'NB': 'NSP System', 'DB': 'NSP Database', 'PR': 'Procurement', 'DS': 'D/S Team',
             'SP': 'Supplier', 'AP': 'AP POLE'}
GROUP = {'GT': 'External', 'NB': 'NSP', 'DB': 'NSP', 'PR': 'TMMIN', 'DS': 'TMMIN', 'SP': 'Supplier', 'AP': 'External'}
FILL = {'GT': 'E4DFEC', 'NB': 'DBE5F4', 'PR': 'FFFFFF', 'DS': 'FFFFFF', 'SP': 'FFFFFF', 'AP': 'E4DFEC'}
SYS_LANES = {'GT', 'AP'}                 # external: tables stay in the box text
W_GROUP, W_LANE, W_GAP, W_STEP = 3.6, 4.6, 3.2, 24
PT_TOP, PT_BOTTOM = 15, 9
R_HEAD, R_TITLE, R_SYS, R_TIME, R0 = 1, 5, 6, 7, 8
EMU = 9525


def col_px(w):
    return int(w * 7 + 5)


def _n(s, per):
    return max(1, math.ceil(len(s) / per))


def box_lines(s):
    text = [s['title']] + ((['W: ' + t for t in s['write']] + ['R: ' + t for t in s['read']]) if s['lane'] in SYS_LANES else [])
    return 1 + _n(s['title'], 30) + sum(_n(t, 36) for t in text[1:])


def db_lines(s):
    """NSP tables touched by the step: table names only (no Log, no read / write detail, no DB Surrounding source tables)."""
    out = []
    for t in s['write'] + s['read']:
        name = t.split(' (')[0].strip()
        if name == 'Log' or 'DB Surrounding' in t or not (name.startswith('TB_') or name.startswith('#')) or name in out:
            continue
        out.append(name)
    return out


def geometry(flow):
    lanes = [k for k in ORDER if k in flow['lanes'] or k == 'DB']
    cols = [(bid, k) for bid, _, slots in flow['bands'] for k in range(slots)]
    cidx = {c: j for j, c in enumerate(cols)}
    widths = {1: W_GROUP, 2: W_LANE}
    for j in range(len(cols)):
        widths[3 + 2 * j], widths[4 + 2 * j] = W_GAP, W_STEP
    last_col = 3 + 2 * len(cols)
    widths[last_col] = W_GAP
    step_col = {s['id']: 4 + 2 * cidx[(s['band'], s['slot'])] for s in flow['steps']}
    db = {s['id']: db_lines(s) for s in flow['steps'] if s['lane'] not in SYS_LANES and db_lines(s)}
    used = [step_col[i] for i in db]
    assert len(used) == len(set(used)), f'{flow["id"]}: two DB storages in one column'
    lane_pt = {}
    for k in lanes:
        if k == 'DB':
            n = max([sum(_n(t, 38) for t in v) for v in db.values()] + [2])
            lane_pt[k] = 30 + 10 * n
        else:
            lane_pt[k] = max([8 + 11 * box_lines(s) for s in flow['steps'] if s['lane'] == k] + [34])
    heights = {1: 14, 2: 14, 3: 14, 4: 6, R_TITLE: 20, R_SYS: 15, R_TIME: 18}
    lane_rows, r = {}, R0
    for k in lanes:
        lane_rows[k] = (r, r + 1, r + 2)
        heights[r], heights[r + 1], heights[r + 2] = PT_TOP, lane_pt[k], PT_BOTTOM
        r += 3
    last_row = r - 1
    heights[r], heights[r + 1], heights[r + 2] = 8, 34, 14     # spacer, legend, legend captions
    col_x, x = {}, 0
    for c in range(1, last_col + 2):
        col_x[c] = x
        x += col_px(widths.get(c, 8.43))
    row_y, y = {}, 0
    for rr in range(1, r + 4):
        row_y[rr] = y
        y += heights.get(rr, 15) * 4 / 3
    boxes, dbs = {}, {}
    for s in flow['steps']:
        c, rr = step_col[s['id']], lane_rows[s['lane']][1]
        boxes[s['id']] = (col_x[c] + 6, row_y[rr] + 3, col_x[c + 1] - col_x[c] - 12, row_y[rr + 1] - row_y[rr] - 6)
        if s['id'] in db:
            rd = lane_rows['DB'][1]
            dbs[s['id']] = (col_x[c] + 4, row_y[rd] + 2, col_x[c + 1] - col_x[c] - 8, row_y[rd + 1] - row_y[rd] - 4)
    band_cols = {}
    for bid, _, slots in flow['bands']:
        js = [cidx[(bid, k)] for k in range(slots)]
        band_cols[bid] = (3 + 2 * js[0], 4 + 2 * js[-1] + (1 if js[-1] == len(cols) - 1 else 0))
    return dict(lanes=lanes, widths=widths, heights=heights, last_col=last_col, last_row=last_row, legend_row=r + 1, lane_rows=lane_rows,
                col_x=col_x, row_y=row_y, boxes=boxes, dbs=dbs, db=db, step_col=step_col, band_cols=band_cols)


def routes(flow, G):
    """Orthogonal arrow points per process edge, through the empty gap columns and the top gap row of the target lane."""
    by = {s['id']: s for s in flow['steps']}
    out = []
    for k, (a, b) in enumerate((s, by[t]) for s in flow['steps'] for t in s['next']):
        ax, ay, aw, ah = G['boxes'][a['id']]
        bx, by_, bw, bh = G['boxes'][b['id']]
        ca, cb = G['step_col'][a['id']], G['step_col'][b['id']]
        off = (k % 3) * 5 - 5
        if ca == cb:
            pts = [(ax + aw / 2, ay + ah), (bx + bw / 2, by_)] if by_ > ay else [(ax + aw / 2, ay), (bx + bw / 2, by_ + bh)]
        else:
            assert cb > ca, f'{a["id"]} -> {b["id"]} goes back in time'
            gx_t = G['col_x'][cb - 1] + (G['col_x'][cb] - G['col_x'][cb - 1]) / 2 + off / 2
            ty = by_ + bh / 2 + off
            if cb == ca + 2:
                pts = [(ax + aw, ay + ah / 2), (gx_t, ay + ah / 2), (gx_t, ty), (bx, ty)]
            else:
                gx_s = G['col_x'][ca + 1] + (G['col_x'][ca + 2] - G['col_x'][ca + 1]) / 2 + off / 2
                top = G['lane_rows'][b['lane']][0]
                gy = G['row_y'][top] + (G['row_y'][top + 1] - G['row_y'][top]) / 2 + off / 2
                pts = [(ax + aw, ay + ah / 2), (gx_s, ay + ah / 2), (gx_s, gy), (gx_t, gy), (gx_t, ty), (bx, ty)]
        out.append((a, b, pts))
    return out


def dataflows(flow, G):
    """Dashed data flow between a step and its DB storage (same column): arrow to the DB = write, to the step = read."""
    out = []
    for s in flow['steps']:
        if s['id'] not in G['dbs']:
            continue
        bx, by_, bw, bh = G['boxes'][s['id']]
        dx, dy, dw, dh = G['dbs'][s['id']]
        x = bx + bw * 0.7
        pts = [(x, by_ + bh), (x, dy)] if dy > by_ else [(x, by_), (x, dy + dh)]
        out.append((s, pts, bool(s['write']), bool(s['read'])))
    return out


# ------------------------------------------------------------------ DrawingML
class Shapes:
    def __init__(self, G):
        self.G, self.parts, self.n = G, [], 1

    def _cell(self, px, py):
        c = max(cc for cc in self.G['col_x'] if self.G['col_x'][cc] <= px)
        r = max(rr for rr in self.G['row_y'] if self.G['row_y'][rr] <= py)
        return c - 1, int((px - self.G['col_x'][c]) * EMU), r - 1, int((py - self.G['row_y'][r]) * EMU)

    def _anchor(self, x, y, w, h, body):
        fc, fco, fr, fro = self._cell(x, y)
        tc, tco, tr, tro = self._cell(x + w, y + h)
        self.parts.append(f'<xdr:twoCellAnchor><xdr:from><xdr:col>{fc}</xdr:col><xdr:colOff>{fco}</xdr:colOff><xdr:row>{fr}</xdr:row><xdr:rowOff>{fro}</xdr:rowOff></xdr:from>'
                          f'<xdr:to><xdr:col>{tc}</xdr:col><xdr:colOff>{tco}</xdr:colOff><xdr:row>{tr}</xdr:row><xdr:rowOff>{tro}</xdr:rowOff></xdr:to>{body}<xdr:clientData/></xdr:twoCellAnchor>')

    def shape(self, name, x, y, w, h, prst='rect', fill='FFFFFF', line='000000', lw=0.75, dash=None, paras=(), anchor='ctr', flip_h=False, ins=2, rot=0):
        e = lambda v: int(round(v * EMU))  # noqa: E731
        self.n += 1
        fill_x = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
        line_x = (f'<a:ln w="{int(lw * 12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>' + (f'<a:prstDash val="{dash}"/>' if dash else '') + '</a:ln>'
                  if line else '<a:ln><a:noFill/></a:ln>')
        txt = ''
        if paras:
            ps = ''.join('<a:p><a:pPr algn="{}"/>{}</a:p>'.format(al, ''.join(
                f'<a:r><a:rPr lang="en-US" sz="{sz}" b="{int(b)}" dirty="0"><a:solidFill><a:srgbClr val="{c}"/></a:solidFill><a:latin typeface="Arial"/>'
                f'<a:cs typeface="Arial"/></a:rPr><a:t>{escape(t)}</a:t></a:r>' for t, sz, b, c in runs)) for runs, al in paras)
            txt = (f'<xdr:txBody><a:bodyPr vertOverflow="overflow" horzOverflow="overflow" wrap="square" lIns="{e(ins)}" tIns="{e(ins)}" rIns="{e(ins)}" '
                   f'bIns="{e(ins)}" anchor="{anchor}"><a:noAutofit/></a:bodyPr><a:lstStyle/>{ps}</xdr:txBody>')
        flip = ' flipH="1"' if flip_h else ''
        rot_x = f' rot="{rot * 60000}"' if rot else ''
        body = (f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{self.n}" name="{escape(name)}"/><xdr:cNvSpPr/></xdr:nvSpPr><xdr:spPr>'
                f'<a:xfrm{rot_x}{flip}><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{max(e(w), 1)}" cy="{max(e(h), 1)}"/></a:xfrm>'
                f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>{fill_x}{line_x}</xdr:spPr>{txt}</xdr:sp>')
        self._anchor(x, y, w, h, body)

    def path(self, name, pts, color='000000', lw=0.75, dash=None, head=False, tail=True):
        e = lambda v: int(round(v * EMU))  # noqa: E731
        self.n += 1
        x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
        w, h = max(max(p[0] for p in pts) - x0, 1), max(max(p[1] for p in pts) - y0, 1)
        seg = ''.join(('<a:moveTo>' if i == 0 else '<a:lnTo>') + f'<a:pt x="{e(px - x0)}" y="{e(py - y0)}"/>' + ('</a:moveTo>' if i == 0 else '</a:lnTo>')
                      for i, (px, py) in enumerate(pts))
        body = (f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{self.n}" name="{escape(name)}"/><xdr:cNvSpPr/></xdr:nvSpPr><xdr:spPr>'
                f'<a:xfrm><a:off x="{e(x0)}" y="{e(y0)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm><a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
                f'<a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="{e(w)}" h="{e(h)}" fill="none">{seg}</a:path></a:pathLst></a:custGeom><a:noFill/>'
                f'<a:ln w="{int(lw * 12700)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' + (f'<a:prstDash val="{dash}"/>' if dash else '')
                + ('<a:headEnd type="triangle" w="sm" len="sm"/>' if head else '') + ('<a:tailEnd type="triangle" w="sm" len="sm"/>' if tail else '')
                + '</a:ln></xdr:spPr></xdr:sp>')
        self._anchor(x0, y0, w, h, body)

    def xml(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">' + ''.join(self.parts) + '</xdr:wsDr>')


def process(sh, name, x, y, w, h, fill, paras, dash=None, corner=True):
    sh.shape(name, x, y, w, h, fill=fill, line='000000', lw=0.75, dash=dash, paras=paras, anchor='ctr', ins=3)
    if corner:
        sh.shape(name + ' corner', x + w - 11, y, 11, 11, prst='rtTriangle', fill='000000', line=None, rot=180)


def step_paras(s):
    paras = [([(s['fn'] or ('Receive' if s['read'] else 'Source'), 750, True, 'C00000')], 'ctr'), ([(s['title'], 750, False, '000000')], 'ctr')]
    if s['lane'] in SYS_LANES:
        paras += [([('W: ' + t, 650, False, '7B3F00')], 'ctr') for t in s['write']]
        paras += [([('R: ' + t, 650, False, '2F5597')], 'ctr') for t in s['read']]
    return paras


def draw_flow(ws, flow, lanes_label, header):
    """Write one flow sheet in the reference format. Returns the DrawingML of its shapes."""
    G = geometry(flow)
    for c, w in G['widths'].items():
        ws.column_dimensions[get_column_letter(c)].width = w
    for r, h in G['heights'].items():
        ws.row_dimensions[r].height = h
    thin, med = Side(style='thin', color='FF000000'), Side(style='medium', color='FF000000')
    grey = PatternFill('solid', fgColor='FFD9D9D9')
    f9, f9b = Font(name='Arial', size=8), Font(name='Arial', size=8, bold=True)
    lc = G['last_col']

    # header block (3 rows), like the reference: label cells grey
    # header units: columns A-B, then each gap + step column pair (the last gap joins the last pair)
    units = [(1, 2)] + [(3 + 2 * j, 4 + 2 * j) for j in range((lc - 3) // 2)]
    units[-1] = (units[-1][0], lc)
    ux = [G['col_x'][u[1] + 1] - G['col_x'][u[0]] for u in units]

    def alloc(segs):
        """Give each header segment whole units, proportional to its width, at least one unit each."""
        n, total = len(units), sum(ux)
        cum = [sum(ux[:k]) for k in range(n + 1)]
        ends, prev = [], 0
        for i, (_, _, b, _) in enumerate(segs):
            left = len(segs) - i - 1
            k = n if i == len(segs) - 1 else min(range(1, n + 1), key=lambda k: abs(cum[k] - b * total))
            k = max(k, prev + 1)
            k = min(k, n - left)
            ends.append((prev, k - 1))
            prev = k
        return [(units[s][0], units[e][1]) for s, e in ends]

    rows = [[('Phase', 0, .05, 1), (header['phase'], .05, .14, 0), ('Project Name', .14, .24, 1), (header['project'], .24, .62, 0),
             ('Page', .62, .70, 1), (header['page'], .70, 1, 0)],
            [('Block Name', 0, .14, 1), (header['block'], .14, .40, 0), ('Function Name', .40, .52, 1), (header['function'], .52, .70, 0),
             ('Created', .70, .78, 1), (header['created'], .78, .86, 0), ('By', .86, .90, 1), (header['by'], .90, 1, 0)],
            [('Document Name', 0, .14, 1), (header['document'], .14, .40, 0), ('Title', .40, .52, 1), (header['title'], .52, .70, 0),
             ('Updated', .70, .78, 1), (header['updated'], .78, .86, 0), ('By', .86, .90, 1), (header['by'], .90, 1, 0)]]
    for i, row in enumerate(rows):
        r = R_HEAD + i
        for (text, a, b, is_label), (ca, cb) in zip(row, alloc(row)):
            if cb > ca:
                ws.merge_cells(start_row=r, start_column=ca, end_row=r, end_column=cb)
            for c in range(ca, cb + 1):
                ws.cell(r, c).border = Border(top=thin, bottom=thin, left=thin if c == ca else None, right=thin if c == cb else None)
                if is_label:
                    ws.cell(r, c).fill = grey
            cell = ws.cell(r, ca, text)
            cell.font, cell.alignment = (f9b if is_label else f9), Alignment(vertical='center', shrink_to_fit=True)

    # title bar, system label, timeline header
    for r, text, fill, font in ((R_TITLE, header['level'], grey, Font(name='Arial', size=11, bold=True)),
                                (R_SYS, header['system'], None, f9b)):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=lc)
        for c in range(1, lc + 1):
            cell = ws.cell(r, c)
            cell.border = Border(top=med if r == R_TITLE else thin, bottom=thin, left=med if c == 1 else None, right=med if c == lc else None)
            if fill:
                cell.fill = fill
        cell = ws.cell(r, 1, text)
        cell.font, cell.alignment = font, Alignment(horizontal='right' if r == R_TITLE else 'center', vertical='center', indent=1)
    ws.merge_cells(start_row=R_TIME, start_column=1, end_row=R_TIME, end_column=2)
    for c in (1, 2):
        ws.cell(R_TIME, c).border = Border(left=med if c == 1 else None, top=thin, bottom=thin, right=thin if c == 2 else None)
    for bid, text, _ in flow['bands']:
        ca, cb = G['band_cols'][bid]
        ws.merge_cells(start_row=R_TIME, start_column=ca, end_row=R_TIME, end_column=cb)
        for c in range(ca, cb + 1):
            ws.cell(R_TIME, c).border = Border(top=thin, bottom=thin, left=thin if c == ca else None, right=(med if c == lc else thin) if c == cb else None)
        cell = ws.cell(R_TIME, ca, text)
        cell.font, cell.alignment = f9b, Alignment(horizontal='center', vertical='center', wrap_text=True)

    # lanes: group label (col A) and lane label (col B), rotated; borders between lanes (rows) and between timeline bands (columns)
    lanes, lr = G['lanes'], G['lane_rows']
    i = 0
    while i < len(lanes):
        j = i
        while j + 1 < len(lanes) and GROUP[lanes[j + 1]] == GROUP[lanes[i]]:
            j += 1
        r0, r1 = lr[lanes[i]][0], lr[lanes[j]][2]
        ws.merge_cells(start_row=r0, start_column=1, end_row=r1, end_column=1)
        cell = ws.cell(r0, 1, GROUP[lanes[i]])
        cell.font, cell.alignment = Font(name='Arial', size=9, bold=True), Alignment(text_rotation=90, horizontal='center', vertical='center', wrap_text=True)
        i = j + 1
    band_edges = {G['band_cols'][b][0] for b, _, _ in flow['bands']}
    for k in lanes:
        r0, _, r1 = lr[k]
        ws.merge_cells(start_row=r0, start_column=2, end_row=r1, end_column=2)
        cell = ws.cell(r0, 2, lanes_label.get(k, LANE_NAME[k]) if k != 'DB' else LANE_NAME['DB'])
        cell.font, cell.alignment = Font(name='Arial', size=8, bold=True), Alignment(text_rotation=90, horizontal='center', vertical='center', wrap_text=True)
        group_end = lanes.index(k) == len(lanes) - 1 or GROUP[lanes[lanes.index(k) + 1]] != GROUP[k]
        group_start = lanes.index(k) == 0 or GROUP[lanes[lanes.index(k) - 1]] != GROUP[k]
        for rr in range(r0, r1 + 1):
            for c in range(1, lc + 1):
                top = (med if k == lanes[0] else thin) if rr == r0 and (c > 1 or group_start) else None
                bottom = (med if k == lanes[-1] else thin) if rr == r1 and (c > 1 or group_end) else None
                left = med if c == 1 else (thin if c in (2, 3) or c in band_edges else None)
                right = med if c == lc else None
                ws.cell(rr, c).border = Border(top=top, bottom=bottom, left=left, right=right)

    sh = Shapes(G)
    # process flow arrows first (under the boxes), then data flows, boxes, DB storages, tags
    for a, b, pts in routes(flow, G):
        sh.path(f'flow {a["id"]}-{b["id"]}', pts, color='000000', lw=1)
    for s, pts, w, r in dataflows(flow, G):
        sh.path(f'data {s["id"]}', pts, color='2E75B6', lw=1, dash='dash', tail=True, head=False)
    for s in flow['steps']:
        x, y, w, h = G['boxes'][s['id']]
        dash = 'dash' if s['fn'] in ('existing', 'manual') else None
        process(sh, f'step {s["id"]}', x, y, w, h, FILL[s['lane']], step_paras(s), dash=dash)
        sh.shape(f'no {s["id"]}', x - 3, y - 7, 26, 12, fill='000000', line='C00000', lw=1, paras=[([(s['id'], 650, True, 'FFFFFF')], 'ctr')], ins=0)
        for i, ab in enumerate(s['ab']):
            sh.shape(f'ab {s["id"]} {ab}', x + w - 32 - i * 33, y - 7, 31, 12, fill='C00000', line=None, paras=[([(ab, 600, True, 'FFFFFF')], 'ctr')], ins=0)
    for sid, (x, y, w, h) in G['dbs'].items():
        lines = G['db'][sid]
        sh.shape(f'db {sid}', x, y, w, h, prst='can', fill='D9D9E8', line='595959', lw=0.75,
                 paras=[([(t, 650, False, '1F3864')], 'ctr') for t in lines], anchor='b', ins=3)

    # legend (light cyan band), like the reference
    rl = G['legend_row']
    ws.merge_cells(start_row=rl, start_column=1, end_row=rl + 1, end_column=2)
    for rr in (rl, rl + 1):
        for c in range(1, lc + 1):
            ws.cell(rr, c).fill = PatternFill('solid', fgColor='FFDDF6F8')
            ws.cell(rr, c).border = Border(top=thin if rr == rl else None, bottom=thin if rr == rl + 1 else None, left=thin if c == 1 else None,
                                           right=thin if c == lc else None)
    cell = ws.cell(rl, 1, 'Legend :')
    cell.font, cell.alignment = f9b, Alignment(horizontal='center', vertical='center', text_rotation=90)
    items = [('NSP System', 'proc', FILL['NB'], None), ('G-TOPAS / AP POLE', 'proc', FILL['GT'], None), ('User (manual / screen)', 'proc', 'FFFFFF', None),
             ('Existing / manual', 'proc', 'FFFFFF', 'dash'), ('DB Storage (table)', 'can', 'D9D9E8', None), ('Step No', 'no', None, None),
             ('Abnormality', 'ab', None, None), ('Process flow', 'flow', None, None), ('Data flow', 'data', None, None)]
    x0, y0 = G['col_x'][3] + 4, G['row_y'][rl] + 6
    span_w = (G['col_x'][lc] - x0) / len(items)
    for i, (text, kind, fill, dash) in enumerate(items):
        x = x0 + i * span_w + (span_w - 70) / 2
        if kind == 'proc':
            process(sh, f'legend {text}', x, y0, 70, 26, fill, [([('Label', 700, False, '000000')], 'ctr')], dash=dash)
        elif kind == 'can':
            sh.shape(f'legend {text}', x, y0 - 2, 70, 30, prst='can', fill=fill, line='595959', paras=[([('Label', 700, False, '000000')], 'ctr')])
        elif kind == 'no':
            sh.shape(f'legend {text}', x + 22, y0 + 7, 26, 12, fill='000000', line='C00000', lw=1, paras=[([('D7', 650, True, 'FFFFFF')], 'ctr')], ins=0)
        elif kind == 'ab':
            sh.shape(f'legend {text}', x + 20, y0 + 7, 31, 12, fill='C00000', line=None, paras=[([('AB09', 600, True, 'FFFFFF')], 'ctr')], ins=0)
        elif kind == 'flow':
            sh.path(f'legend {text}', [(x, y0 + 13), (x + 70, y0 + 13)], color='000000', lw=1)
        else:
            sh.path(f'legend {text}', [(x, y0 + 13), (x + 70, y0 + 13)], color='2E75B6', lw=1, dash='dash')
        sh.shape(f'legend caption {text}', x0 + i * span_w, G['row_y'][rl + 1] + 1, span_w, 16, fill=None, line=None,
                 paras=[([(text, 650, False, '000000')], 'ctr')], ins=0)
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = ws.cell(R0, 3)
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    return sh.xml()


# ------------------------------------------------------------------ draw.io (same geometry, arrows glued to the boxes)
def drawio(flows, lanes_label):
    pages = []
    for flow in flows:
        G = geometry(flow)
        cells, n = ['<mxCell id="0"/><mxCell id="1" parent="0"/>'], [1]
        ox, oy = 0, -G['row_y'][R_TIME]

        def v(value, style, x, y, w, h, cid=None):
            n[0] += 1
            cid = cid or f'c{n[0]}'
            cells.append(f'<mxCell id="{cid}" value="{escape(value, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="1">'
                         f'<mxGeometry x="{x + ox:.0f}" y="{y + oy:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
            return cid
        W = G['col_x'][G['last_col'] + 1]
        for bid, text, _ in flow['bands']:
            ca, cb = G['band_cols'][bid]
            v(text, 'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;fontStyle=1;fontSize=10;', G['col_x'][ca], G['row_y'][R_TIME], G['col_x'][cb + 1] - G['col_x'][ca],
              G['row_y'][R_TIME + 1] - G['row_y'][R_TIME])
        for k in G['lanes']:
            r0, _, r1 = G['lane_rows'][k]
            y, h = G['row_y'][r0], G['row_y'][r1 + 1] - G['row_y'][r0]
            v('', 'rounded=0;fillColor=none;strokeColor=#000000;', G['col_x'][2], y, W - G['col_x'][2], h)
            v(lanes_label.get(k, LANE_NAME[k]) if k != 'DB' else LANE_NAME['DB'], 'rounded=0;whiteSpace=wrap;html=1;horizontal=0;fontStyle=1;fontSize=10;fillColor=#FFFFFF;',
              G['col_x'][2], y, G['col_x'][3] - G['col_x'][2], h)
            v(GROUP[k], 'rounded=0;whiteSpace=wrap;html=1;horizontal=0;fontStyle=1;fontSize=10;fillColor=#FFFFFF;', 0, y, G['col_x'][2], h)
        for s in flow['steps']:
            x, y, w, h = G['boxes'][s['id']]
            val = '<br>'.join(f'<font color="#{c}">{"<b>" if b else ""}{escape(t)}{"</b>" if b else ""}</font>' for runs, _ in step_paras(s) for t, _, b, c in runs)
            dash = 'dashed=1;' if s['fn'] in ('existing', 'manual') else ''
            v(val, f'shape=card;flipH=1;size=10;whiteSpace=wrap;html=1;fillColor=#{FILL[s["lane"]]};strokeColor=#000000;{dash}fontSize=9;', x, y, w, h, cid=f'{flow["id"]}_{s["id"]}')
            v(s['id'], 'rounded=0;fillColor=#000000;strokeColor=#C00000;fontColor=#FFFFFF;fontStyle=1;fontSize=8;', x - 3, y - 7, 26, 12)
            for i, ab in enumerate(s['ab']):
                v(ab, 'rounded=0;fillColor=#C00000;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=8;', x + w - 32 - i * 33, y - 7, 31, 12)
        for sid, (x, y, w, h) in G['dbs'].items():
            val = '<br>'.join(escape(t) for t in G['db'][sid])
            v(val, 'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=8;fillColor=#D9D9E8;strokeColor=#595959;fontSize=8;align=left;spacingLeft=4;',
              x, y, w, h, cid=f'{flow["id"]}_db_{sid}')
        for a, b, pts in routes(flow, G):
            n[0] += 1
            geo = '<Array as="points">' + ''.join(f'<mxPoint x="{px + ox:.0f}" y="{py + oy:.0f}"/>' for px, py in pts[1:-1]) + '</Array>' if len(pts) > 2 else ''
            ports = 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;' if len(pts) == 2 else 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;'
            cells.append(f'<mxCell id="e{n[0]}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;{ports}" edge="1" parent="1" '
                         f'source="{flow["id"]}_{a["id"]}" target="{flow["id"]}_{b["id"]}"><mxGeometry relative="1" as="geometry">{geo}</mxGeometry></mxCell>')
        for s, pts, w, r in dataflows(flow, G):
            n[0] += 1
            cells.append(f'<mxCell id="d{n[0]}" style="edgeStyle=orthogonalEdgeStyle;dashed=1;html=1;strokeColor=#2E75B6;endArrow=block;startArrow=none;" '
                         f'edge="1" parent="1" source="{flow["id"]}_{s["id"]}" target="{flow["id"]}_db_{s["id"]}"><mxGeometry relative="1" as="geometry"/></mxCell>')
        pages.append(f'<diagram id="{flow["id"]}" name="{escape(flow["id"] + " " + flow["title"])}"><mxGraphModel grid="1" gridSize="10" guides="1" connect="1" arrows="1" '
                     f'page="1" pageWidth="{int(W) + 40}" pageHeight="{int(G["row_y"][G["last_row"] + 1] + oy) + 40}"><root>{"".join(cells)}</root></mxGraphModel></diagram>')
    return '<mxfile host="build_bpf.py" type="device">' + ''.join(pages) + '</mxfile>'
