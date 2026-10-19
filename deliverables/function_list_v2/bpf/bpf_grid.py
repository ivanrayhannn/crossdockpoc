"""Flow sheet of the BPF level 2 drawn with cells: X = PIC lane (columns), Y = timeline (rows), lanes and timeline bands
separated by cell borders, every step is a filled cell. Only the arrows are shapes (anchored to the cells, they move with them)."""
import math
from xml.sax.saxutils import escape
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from bpf_shapes import LANE_COLOR, label

TIME_W, GAP_W, LANE_W = 22, 3, 32      # column widths (characters)
HEAD_ROW, GRID_ROW = 4, 5              # header row, first grid row
GAP_PT = 18                            # gap row between slots (arrows run here)
EMU_PX = 9525
NAVY, NAVY2 = '1F3864', '44546A'


def col_px(w):
    return int(w * 7 + 5)


def _lines(s, per):
    return max(1, math.ceil(len(s) / per))


def cell_pt(s):
    pt = 6 + 11 * (1 + _lines(s['title'], 38)) + 10 * sum(_lines(t, 44) for t in s['read'] + s['write'])
    return pt + (10 if s['ab'] else 0)


def rich(s):
    f = lambda sz, b, c: InlineFont(rFont='Arial', sz=sz, b=b, color='FF' + c)  # noqa: E731
    parts = [TextBlock(f(8, True, 'C00000'), label(s)), TextBlock(f(8, True, '6B7A90'), f'   {s["id"]}\n'), TextBlock(f(8, True, '1F2A3D'), s['title'])]
    parts += [TextBlock(f(7, False, '2F5597'), '\nR: ' + t) for t in s['read']]
    parts += [TextBlock(f(7, False, '7B3F00'), '\nW: ' + t) for t in s['write']]
    if s['ab']:
        parts.append(TextBlock(f(7, True, 'C00000'), '\n⚠ ' + ', '.join(s['ab'])))
    return CellRichText(parts)


def draw_flow(ws, flow, lanes):
    """Write the grid of one flow into ws (rows 4..). Returns (drawing xml of the arrows, first free row)."""
    thin, dash = Side(style='thin', color='FF8497B0'), Side(style='dashed', color='FFB7C0CD')
    band_line = Side(style='medium', color='FF8497B0')
    nl = len(flow['lanes'])
    # columns: A timeline, then per lane [gap, lane, gap]
    ws.column_dimensions['A'].width = TIME_W
    lane_col = {}
    for i, k in enumerate(flow['lanes']):
        c0 = 2 + i * 3
        lane_col[k] = c0 + 1
        for c, w in ((c0, GAP_W), (c0 + 1, LANE_W), (c0 + 2, GAP_W)):
            ws.column_dimensions[get_column_letter(c)].width = w
    last_col = 1 + nl * 3
    # rows: per band, per slot one gap row then one slot row; a closing gap row per band
    slot_row, band_rows, r = {}, [], GRID_ROW
    for bid, text, slots in flow['bands']:
        first = r
        for k in range(slots):
            ws.row_dimensions[r].height = GAP_PT
            slot_row[(bid, k)] = r + 1
            r += 2
        ws.row_dimensions[r].height = GAP_PT
        band_rows.append((bid, text, first, r))
        r += 1
    for (bid, k), sr in slot_row.items():
        steps = [s for s in flow['steps'] if s['band'] == bid and s['slot'] == k]
        ws.row_dimensions[sr].height = max([30] + [cell_pt(s) for s in steps])
    end_row = r - 1

    # header
    ws.row_dimensions[HEAD_ROW].height = 30
    hc = ws.cell(HEAD_ROW, 1, 'Timeline ↓ / PIC →')
    hc.font, hc.fill = Font(name='Arial', size=9, bold=True, color='FFFFFFFF'), PatternFill('solid', fgColor='FF' + NAVY)
    hc.alignment, hc.border = Alignment(horizontal='center', vertical='center', wrap_text=True), Border(left=thin, right=thin, top=thin, bottom=thin)
    for i, k in enumerate(flow['lanes']):
        c0 = 2 + i * 3
        ws.merge_cells(start_row=HEAD_ROW, start_column=c0, end_row=HEAD_ROW, end_column=c0 + 2)
        bg, bd = LANE_COLOR[k]
        for c in range(c0, c0 + 3):
            cell = ws.cell(HEAD_ROW, c)
            cell.fill = PatternFill('solid', fgColor='FF' + bg)
            cell.border = Border(top=thin, bottom=thin, left=thin if c == c0 else None, right=thin if c == c0 + 2 else None)
        cell = ws.cell(HEAD_ROW, c0, lanes[k])
        cell.font, cell.alignment = Font(name='Arial', size=10, bold=True, color='FF1F2A3D'), Alignment(horizontal='center', vertical='center', wrap_text=True)

    # bands: timeline cell merged, shading, borders between lanes (dashed) and between bands (medium)
    for i, (bid, text, first, last) in enumerate(band_rows):
        shade = PatternFill('solid', fgColor='FFF6F8FB' if i % 2 == 0 else 'FFFFFFFF')
        ws.merge_cells(start_row=first, start_column=1, end_row=last, end_column=1)
        for rr in range(first, last + 1):
            for c in range(1, last_col + 1):
                cell = ws.cell(rr, c)
                if c == 1:
                    cell.fill = PatternFill('solid', fgColor='FF' + (NAVY if i % 2 == 0 else NAVY2))
                else:
                    cell.fill = shade
                left = thin if c in (1, 2) else (dash if (c - 2) % 3 == 0 else None)
                right = thin if c in (1, last_col) else None
                cell.border = Border(left=left, right=right, top=band_line if rr == first else None, bottom=band_line if rr == last else None)
        tc = ws.cell(first, 1, text)
        tc.font = Font(name='Arial', size=9, bold=True, color='FFFFFFFF')
        tc.alignment = Alignment(vertical='center', wrap_text=True, indent=1)

    # steps
    for s in flow['steps']:
        rr, c = slot_row[(s['band'], s['slot'])], lane_col[s['lane']]
        bg, bd = LANE_COLOR[s['lane']]
        side = Side(style='mediumDashed' if s['fn'] in ('existing', 'manual') else 'medium', color='FF' + bd)
        cell = ws.cell(rr, c)
        cell.value = rich(s)
        cell.fill = PatternFill('solid', fgColor='FF' + bg)
        cell.border = Border(left=side, right=side, top=side, bottom=side)
        cell.alignment = Alignment(wrap_text=True, vertical='top')

    # geometry in px for the arrows
    col_x, x = {}, 0
    for c in range(1, last_col + 2):
        col_x[c] = x
        x += col_px(ws.column_dimensions[get_column_letter(c)].width or 8.43)
    row_y, y = {}, 0
    for rr in range(1, end_row + 2):
        row_y[rr] = y
        y += (ws.row_dimensions[rr].height or 15) * 4 / 3

    def anchor(px, py):
        c = max(cc for cc in col_x if col_x[cc] <= px)
        rr = max(r_ for r_ in row_y if row_y[r_] <= py)
        return c - 1, int((px - col_x[c]) * EMU_PX), rr - 1, int((py - row_y[rr]) * EMU_PX)

    def box(s):
        rr, c = slot_row[(s['band'], s['slot'])], lane_col[s['lane']]
        return col_x[c], row_y[rr], col_x[c + 1] - col_x[c], row_y[rr + 1] - row_y[rr], rr

    by = {s['id']: s for s in flow['steps']}
    slot_idx = {rr: i for i, rr in enumerate(sorted(slot_row.values()))}
    shapes, sid = [], 1
    for k, (a, b) in enumerate((s, by[t]) for s in flow['steps'] for t in s['next']):
        ax, ay, aw, ah, ar = box(a)
        bx, by_, bw, bh, br = box(b)
        la, lb = flow['lanes'].index(a['lane']), flow['lanes'].index(b['lane'])
        sx, tx = ax + aw / 2, bx + bw / 2
        off = (k % 3) * 4 - 4
        if ar == br:
            yy = ay + min(ah, bh) / 2
            pts = [(ax + aw, yy), (bx, yy)] if lb > la else [(ax, yy), (bx + bw, yy)]
        elif slot_idx[br] == slot_idx[ar] + 1:
            gy = row_y[br - 1] + (row_y[br] - row_y[br - 1]) / 2 + off
            pts = [(sx, ay + ah), (sx, by_)] if la == lb else [(sx, ay + ah), (sx, gy), (tx, gy), (tx, by_)]
        else:
            g1 = row_y[ar + 1] + (row_y[ar + 2] - row_y[ar + 1]) / 2 + off
            g2 = row_y[br - 1] + (row_y[br] - row_y[br - 1]) / 2 + off
            c = lane_col[a['lane']] + (-1 if lb < la else 1)
            cx = col_x[c] + (col_x[c + 1] - col_x[c]) / 2 + off / 2
            pts = [(sx, ay + ah), (sx, g1), (cx, g1), (cx, g2), (tx, g2), (tx, by_)]
        x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
        w, h = max(max(p[0] for p in pts) - x0, 1), max(max(p[1] for p in pts) - y0, 1)
        e = lambda v: int(v * EMU_PX)  # noqa: E731
        fc, fco, fr, fro = anchor(x0, y0)
        tc, tco, tr, tro = anchor(x0 + w, y0 + h)
        seg = ''.join(('<a:moveTo>' if i == 0 else '<a:lnTo>') + f'<a:pt x="{e(px - x0)}" y="{e(py - y0)}"/>' + ('</a:moveTo>' if i == 0 else '</a:lnTo>')
                      for i, (px, py) in enumerate(pts))
        sid += 1
        shapes.append(
            f'<xdr:twoCellAnchor><xdr:from><xdr:col>{fc}</xdr:col><xdr:colOff>{fco}</xdr:colOff><xdr:row>{fr}</xdr:row><xdr:rowOff>{fro}</xdr:rowOff></xdr:from>'
            f'<xdr:to><xdr:col>{tc}</xdr:col><xdr:colOff>{tco}</xdr:colOff><xdr:row>{tr}</xdr:row><xdr:rowOff>{tro}</xdr:rowOff></xdr:to>'
            f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{sid}" name="{escape(f"arrow {a["id"]}-{b["id"]}")}"/><xdr:cNvSpPr/></xdr:nvSpPr>'
            f'<xdr:spPr><a:xfrm><a:off x="{e(x0)}" y="{e(y0)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
            f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
            f'<a:pathLst><a:path w="{e(w)}" h="{e(h)}" fill="none">{seg}</a:path></a:pathLst></a:custGeom><a:noFill/>'
            f'<a:ln w="15875"><a:solidFill><a:srgbClr val="4A5A75"/></a:solidFill><a:tailEnd type="triangle" w="med" len="med"/></a:ln></xdr:spPr></xdr:sp>'
            f'<xdr:clientData/></xdr:twoCellAnchor>')
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">' + ''.join(shapes) + '</xdr:wsDr>')
    return xml, end_row + 2, last_col
