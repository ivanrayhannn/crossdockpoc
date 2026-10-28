"""Native, editable Excel flowchart shapes (DrawingML), laid out with Graphviz.

Graphviz (`dot -Tplain`) only computes node positions; every node becomes an Excel shape
(flowchart preset with its text) and every edge an Excel connector glued to the shapes, so the
user can move boxes, retype labels and the arrows follow - like a diagram drawn by hand.

openpyxl cannot write shapes, so they are collected while the workbook is built and injected
into the saved .xlsx afterwards (inject()).
"""
import math
import re
import shlex
import subprocess
import zipfile
from xml.sax.saxutils import escape

EMU_PX, EMU_PT = 9525, 12700
NS_XDR = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
DRAWING_CT = "application/vnd.openxmlformats-officedocument.drawing+xml"
DRAWING_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing"

# node type -> (preset geometry, fill, dashed, line width EMU)
PRESET = {
    "start": ("flowChartTerminator", "FFFFFF", False, 9525),
    "end": ("flowChartTerminator", "FFFFFF", False, 9525),
    "process": ("flowChartProcess", "FFFFFF", False, 9525),
    "decision": ("flowChartDecision", "FFFFFF", False, 9525),
    "screen": ("flowChartProcess", "EDEDED", False, 15875),
    "db": ("flowChartMagneticDisk", "FFFFFF", False, 9525),
    "file": ("flowChartDocument", "FFFFFF", False, 9525),
    "document": ("flowChartDocument", "FFFFFF", False, 9525),
    "io": ("flowChartInputOutput", "FFFFFF", False, 9525),
    "message": ("flowChartProcess", "FFFFFF", True, 9525),
    "subprocess": ("flowChartPredefinedProcess", "FFFFFF", False, 9525),
    "event": ("flowChartAlternateProcess", "FFF2CC", False, 9525),
    "note": ("foldedCorner", "FFFFE0", False, 9525),
}
SITE = {"t": 0, "l": 1, "b": 2, "r": 3}   # connection-site order used by these presets


def layout(dot_src):
    """Return (width_in, height_in, {node_id: (cx, cy, w, h)}) in inches, y measured from the top."""
    out = subprocess.run(["dot", "-Tplain"], input=dot_src.encode("utf-8"), capture_output=True, check=True).stdout
    W = H = 0.0
    nodes = {}
    for line in out.decode("utf-8").splitlines():
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if not parts:
            continue
        if parts[0] == "graph":
            W, H = float(parts[2]), float(parts[3])
        elif parts[0] == "node":
            nodes[parts[1]] = [float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])]
    for v in nodes.values():
        v[1] = H - v[1]
    return W, H, nodes


class SheetGeometry:
    """Absolute positions on a worksheet: columns in px, rows in pt."""

    def __init__(self, book, ws, default_row_pt):
        self.book, self.ws, self.default = book, ws, default_row_pt

    def row_pt(self, r):
        h = self.ws.row_dimensions[r].height
        return h if h else self.default

    def col_left_px(self, c):
        return sum(self.book.col_px(i) for i in range(1, c))

    def row_top_pt(self, r):
        return sum(self.row_pt(i) for i in range(1, r))

    def anchor(self, x_px, y_pt):
        c, left = 1, 0.0
        while left + self.book.col_px(c) <= x_px:
            left += self.book.col_px(c)
            c += 1
        r, top = 1, 0.0
        while top + self.row_pt(r) <= y_pt:
            top += self.row_pt(r)
            r += 1
        return c - 1, int((x_px - left) * EMU_PX), r - 1, int((y_pt - top) * EMU_PT)


def _anchor_xml(geo, x, y, w, h):
    """x, w in px; y, h in pt. twoCellAnchor that moves with cells but keeps its size."""
    c1, co1, r1, ro1 = geo.anchor(x, y)
    c2, co2, r2, ro2 = geo.anchor(x + w, y + h)
    return (f'<xdr:twoCellAnchor editAs="oneCell"><xdr:from><xdr:col>{c1}</xdr:col><xdr:colOff>{co1}</xdr:colOff>'
            f'<xdr:row>{r1}</xdr:row><xdr:rowOff>{ro1}</xdr:rowOff></xdr:from><xdr:to><xdr:col>{c2}</xdr:col>'
            f'<xdr:colOff>{co2}</xdr:colOff><xdr:row>{r2}</xdr:row><xdr:rowOff>{ro2}</xdr:rowOff></xdr:to>')


def _xfrm(x, y, w, h, flip_h=False, flip_v=False):
    fl = (' flipH="1"' if flip_h else "") + (' flipV="1"' if flip_v else "")
    return (f'<a:xfrm{fl}><a:off x="{int(x * EMU_PX)}" y="{int(y * EMU_PT)}"/>'
            f'<a:ext cx="{max(1, int(w * EMU_PX))}" cy="{max(1, int(h * EMU_PT))}"/></a:xfrm>')


def _text_body(lines, sz, anchor="ctr", align="ctr", ins=(36000, 18000)):
    paras = "".join(
        f'<a:p><a:pPr algn="{align}"/><a:r><a:rPr lang="en-US" sz="{sz}"><a:solidFill><a:srgbClr val="000000"/>'
        f'</a:solidFill><a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>{escape(t)}</a:t></a:r></a:p>'
        for t in lines) or '<a:p><a:endParaRPr lang="en-US"/></a:p>'
    return (f'<xdr:txBody><a:bodyPr vertOverflow="overflow" horzOverflow="overflow" wrap="square" '
            f'lIns="{ins[0]}" tIns="{ins[1]}" rIns="{ins[0]}" bIns="{ins[1]}" rtlCol="0" anchor="{anchor}"/>'
            f'<a:lstStyle/>{paras}</xdr:txBody>')


def _line(w, dashed, arrow=False):
    return (f'<a:ln w="{w}"><a:solidFill><a:srgbClr val="000000"/></a:solidFill>'
            + ('<a:prstDash val="dash"/>' if dashed else "")
            + ('<a:tailEnd type="triangle" w="med" len="med"/>' if arrow else "") + "</a:ln>")


def build(book, ws, spec, dot_src, wrap_label, col0, row0, width_px, max_h_pt=None, grow=False,
          default_row_pt=11.1, min_scale=0.5):
    """Lay out `spec` and return (anchor_xml_list, used_height_pt). The diagram's top-left is the
    top-left of cell (row0, col0)."""
    W, H, pos = layout(dot_src)
    if not pos:
        return [], 0
    Wpx, Hpt = W * 96, H * 72
    s = min(width_px / Wpx, 1.0)
    if max_h_pt and not grow and Hpt * s > max_h_pt:
        s = max(min_scale, max_h_pt / Hpt)
    geo = SheetGeometry(book, ws, default_row_pt)
    x0, y0 = geo.col_left_px(col0) + 4, geo.row_top_pt(row0) + 2
    sz = int(round(max(5.5, min(8.0, 10 * s)) * 2) / 2 * 100)

    nodes = {n["id"]: n for n in spec.get("nodes", [])}
    boxes = {}
    for nid, (cx, cy, w, h) in pos.items():
        nid = nid.strip('"')
        boxes[nid] = (x0 + (cx - w / 2) * 96 * s, y0 + (cy - h / 2) * 72 * s, w * 96 * s, h * 72 * s)

    out, ids, next_id = [], {}, [2]

    def new_id():
        next_id[0] += 1
        return next_id[0]

    for nid in boxes:
        ids[nid] = new_id()

    # connectors first (shapes are drawn on top of the line ends)
    direction = str(spec.get("direction", "TB")).upper()
    lr = direction in ("LR", "RL")
    edges = [e for e in spec.get("edges", []) if e.get("from") in boxes and e.get("to") in boxes]
    by_pair = {(e["from"], e["to"]): e for e in edges}

    def rel(a, b):
        ax, ay, aw, ah = boxes[a]
        bx, by, bw, bh = boxes[b]
        if lr:
            return "fwd" if bx >= ax + aw - 1 else ("back" if bx + bw <= ax + 1 else "side")
        return "fwd" if by >= ay + ah - 1 else ("back" if by + bh <= ay + 1 else "side")

    def site_pt(n, side):
        x, y, w, h = boxes[n]
        return {"t": (x + w / 2, y), "b": (x + w / 2, y + h), "l": (x, y + h / 2), "r": (x + w, y + h / 2)}[side]

    def label_box(lines, lx, ly):
        tid = new_id()
        target = labels_out
        lw = max(len(t) for t in lines) * (sz / 100) * 0.62 + 8
        lh = len(lines) * (sz / 100) * 1.25 + 3
        target.append(
            _anchor_xml(geo, lx, ly - lh / 2, lw, lh)
            + f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{tid}" name="Label {tid}"/>'
            f'<xdr:cNvSpPr txBox="1"/></xdr:nvSpPr><xdr:spPr>{_xfrm(lx, ly - lh / 2, lw, lh)}'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></xdr:spPr>'
            + _text_body(lines, max(500, sz - 100), anchor="t", align="l", ins=(9000, 0))
            + "</xdr:sp><xdr:clientData/></xdr:twoCellAnchor>")

    def connector(a, b, s1, s2, prst, xfrm_xml, bbox, dashed, both, arrow_at_start=False):
        cid = new_id()
        out.append(
            _anchor_xml(geo, *bbox)
            + f'<xdr:cxnSp macro=""><xdr:nvCxnSpPr><xdr:cNvPr id="{cid}" name="Connector {cid}"/><xdr:cNvCxnSpPr>'
            f'<a:stCxn id="{ids[a]}" idx="{SITE[s1]}"/><a:endCxn id="{ids[b]}" idx="{SITE[s2]}"/></xdr:cNvCxnSpPr></xdr:nvCxnSpPr>'
            f'<xdr:spPr>{xfrm_xml}<a:prstGeom prst="{prst[0]}">{prst[1]}</a:prstGeom>'
            f'<a:ln w="9525"><a:solidFill><a:srgbClr val="000000"/></a:solidFill>'
            + ('<a:prstDash val="dash"/>' if dashed else "")
            + ('<a:headEnd type="triangle" w="med" len="med"/>' if (both or arrow_at_start) else "")
            + ('<a:tailEnd type="triangle" w="med" len="med"/>' if (both or not arrow_at_start) else "")
            + '</a:ln></xdr:spPr></xdr:cxnSp><xdr:clientData/></xdr:twoCellAnchor>')

    done, loops, labels_out = set(), [0], []

    def polyline(points, dashed, both):
        """Free elbow line with arrow (renders identically everywhere; not glued to the shapes)."""
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        x, y = min(xs), min(ys)
        w, h = max(max(xs) - x, 1), max(max(ys) - y, 1)
        W, H = int(w * EMU_PX), int(h * EMU_PT)
        pts = [(int((px - x) * EMU_PX), int((py - y) * EMU_PT)) for px, py in points]
        path = f'<a:moveTo><a:pt x="{pts[0][0]}" y="{pts[0][1]}"/></a:moveTo>' + "".join(
            f'<a:lnTo><a:pt x="{px}" y="{py}"/></a:lnTo>' for px, py in pts[1:])
        lid = new_id()
        out.append(
            _anchor_xml(geo, x, y, w, h)
            + f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{lid}" name="Elbow Arrow {lid}"/><xdr:cNvSpPr/>'
            f'</xdr:nvSpPr><xdr:spPr>{_xfrm(x, y, w, h)}<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
            f'<a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="{W}" h="{H}" fill="none">{path}</a:path></a:pathLst>'
            f'</a:custGeom><a:noFill/><a:ln w="9525"><a:solidFill><a:srgbClr val="000000"/></a:solidFill>'
            + ('<a:prstDash val="dash"/>' if dashed else "")
            + ('<a:headEnd type="triangle" w="med" len="med"/>' if both else "")
            + '<a:tailEnd type="triangle" w="med" len="med"/></a:ln></xdr:spPr></xdr:sp><xdr:clientData/></xdr:twoCellAnchor>')

    def span_boxes(y1, y2, skip):
        lo, hi = min(y1, y2), max(y1, y2)
        return [bx for n, bx in boxes.items() if n not in skip and bx[1] < hi and bx[1] + bx[3] > lo]

    def blocked_tb(a, b):
        p1, p2 = site_pt(a, "b"), site_pt(b, "t")
        if p2[1] <= p1[1]:
            return False
        for n, (x, y, w, h) in boxes.items():
            if n in (a, b) or not (y > p1[1] - 1 and y + h < p2[1] + 1):
                continue
            t = ((y + h / 2) - p1[1]) / (p2[1] - p1[1])
            lx = p1[0] + (p2[0] - p1[0]) * t
            if x - 10 <= lx <= x + w + 10:
                return True
        return False

    def side_loop(a, b, side, dashed, both, lines):
        """Elbow from `side` of a to the same side of b, routed outside every box in between."""
        loops[0] += 1
        off = 12 + 8 * (loops[0] - 1)
        p1, p2 = site_pt(a, side), site_pt(b, side)
        between = span_boxes(p1[1], p2[1], ()) or [boxes[a], boxes[b]]
        xv = (max(bx[0] + bx[2] for bx in between) + off) if side == "r" else (min(bx[0] for bx in between) - off)
        polyline([p1, (xv, p1[1]), (xv, p2[1]), p2], dashed, both)
        if lines:
            lw_est = max(len(z) for z in lines) * (sz / 100) * 0.62 + 8
            label_box(lines, (xv + 3) if side == "r" else (xv - lw_est - 3), (p1[1] + p2[1]) / 2)

    fwd_mark, back_mark = ("\u2192 ", "\u2190 ") if lr else ("\u2193 ", "\u2191 ")
    for e in edges:
        a, b = e["from"], e["to"]
        if (a, b) in done:
            continue
        done.add((a, b))
        rev = by_pair.get((b, a)) if a != b else None
        dashed = e.get("style") == "dashed" or nodes.get(a, {}).get("lane") or nodes.get(b, {}).get("lane")
        labels = [e.get("label")] if e.get("label") else []
        both = False
        if rev is not None:
            done.add((b, a))
            if rel(a, b) == "back":            # draw the pair from the earlier node to the later one
                a, b, e, rev = b, a, rev, e
            both = True
            labels = [t for t in ((fwd_mark + e["label"]) if e.get("label") else None,
                                  (back_mark + rev["label"]) if rev.get("label") else None) if t]
        lines = [ln for t in labels for ln in wrap_label(t, 22).split("\n")]
        r = rel(a, b)
        if r == "back":
            loops[0] += 1
            off = 12 + 8 * (loops[0] - 1)
            if not lr:                          # loop on the right, outside the boxes in between
                loops[0] -= 1
                side_loop(a, b, "r", dashed, both, lines)
            else:                               # loop underneath the boxes in between
                p1, p2 = site_pt(a, "b"), site_pt(b, "b")
                lo, hi = min(p1[0], p2[0]), max(p1[0], p2[0])
                under = [bx for bx in boxes.values() if bx[0] < hi and bx[0] + bx[2] > lo] or [boxes[a], boxes[b]]
                yv = max(bx[1] + bx[3] for bx in under) + off
                polyline([p1, (p1[0], yv), (p2[0], yv), p2], dashed, both)
                if lines:
                    label_box(lines, (p1[0] + p2[0]) / 2, yv + 6)
            continue
        if r == "fwd" and not lr and blocked_tb(a, b):
            side_loop(a, b, "l", dashed, both, lines)
            continue
        if r == "fwd":
            s1, s2 = ("r", "l") if lr else ("b", "t")
        else:
            if lr:
                s1, s2 = ("b", "t") if boxes[b][1] >= boxes[a][1] else ("t", "b")
            else:
                s1, s2 = ("r", "l") if boxes[b][0] >= boxes[a][0] else ("l", "r")
        p1, p2 = site_pt(a, s1), site_pt(b, s2)
        x, y, w, h = min(p1[0], p2[0]), min(p1[1], p2[1]), abs(p2[0] - p1[0]), abs(p2[1] - p1[1])
        connector(a, b, s1, s2, ("straightConnector1", "<a:avLst/>"), _xfrm(x, y, w, h, p2[0] < p1[0], p2[1] < p1[1]),
                  (x, y, max(w, 1), max(h, 1)), dashed, both)
        if lines:
            # place the label toward the target end so labels of edges leaving one node do not pile up
            t = 0.62 if (both or r == "fwd") and abs(p2[1] - p1[1]) > 4 and abs(p2[0] - p1[0]) > 4 else 0.5
            lx, ly = p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t
            lw_est = max(len(z) for z in lines) * (sz / 100) * 0.62 + 8
            lh_est = len(lines) * (sz / 100) * 1.25 + 3
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            if abs(dx) > 4 and abs(dy) > 4:
                # keep the label clear of a diagonal line, on its left side: above-left of a rising
                # line, below-left of a falling one (screen coordinates)
                if dx * dy < 0:
                    label_box(lines, lx - lw_est - 4, ly - lh_est / 2 - 2)
                else:
                    label_box(lines, lx - lw_est - 4, ly + lh_est / 2 + 2)
            elif abs(dy) <= 4:   # horizontal: centred above
                label_box(lines, lx - lw_est / 2, ly - lh_est / 2 - 3)
            else:                # vertical: to the right
                label_box(lines, lx + 3, ly)

    for nid, (x, y, w, h) in boxes.items():
        n = nodes.get(nid, {"label": nid})
        t = n.get("type", "process")
        prst, fill, dashed, lw = PRESET.get(t, PRESET["process"])
        label = n.get("label", nid)
        if t == "screen" and n.get("screen_id"):
            label = f"[{n['screen_id']}]\n{label}"
        if n.get("step") is not None:
            label = f"({n['step']}) {label}"
        out.append(
            _anchor_xml(geo, x, y, w, h)
            + f'<xdr:sp macro="" textlink=""><xdr:nvSpPr><xdr:cNvPr id="{ids[nid]}" name="{escape(t.title())} {ids[nid]}"/>'
            f'<xdr:cNvSpPr/></xdr:nvSpPr><xdr:spPr>{_xfrm(x, y, w, h)}<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{_line(lw, dashed)}</xdr:spPr>'
            + _text_body(wrap_label(label).split("\n"), sz)
            + "</xdr:sp><xdr:clientData/></xdr:twoCellAnchor>")
    return out + labels_out, Hpt * s + 6


# --------------------------------------------------------------------------- injection
def _sheet_paths(z):
    wb = z.read("xl/workbook.xml").decode("utf-8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    rmap = {}
    for m in re.finditer(r"<Relationship\b([^>]*)/>", rels):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        rmap[attrs.get("Id")] = attrs.get("Target")
    out = {}
    for m in re.finditer(r"<sheet\b([^>]*)/>", wb):
        name = re.search(r'name="([^"]*)"', m.group(1)).group(1)
        rid = re.search(r'r:id="([^"]*)"', m.group(1)).group(1)
        t = rmap[rid].lstrip("/")
        out[_unescape(name)] = t if t.startswith("xl/") else "xl/" + t
    return out


def _unescape(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")


def inject(xlsx_path, sheet_shapes):
    """Add the collected shape anchors to the drawings of the given sheets (titles -> [xml])."""
    sheet_shapes = {k: v for k, v in sheet_shapes.items() if v}
    if not sheet_shapes:
        return
    with zipfile.ZipFile(xlsx_path) as z:
        files = {n: z.read(n) for n in z.namelist()}
    zin = zipfile.ZipFile(xlsx_path)
    paths = _sheet_paths(zin)
    zin.close()
    ct = files["[Content_Types].xml"].decode("utf-8")
    existing = [int(m) for m in re.findall(r"xl/drawings/drawing(\d+)\.xml", " ".join(files))]
    next_drawing = max(existing + [0]) + 1
    for title, anchors in sheet_shapes.items():
        sp = paths.get(title)
        if not sp:
            continue
        folder, fname = sp.rsplit("/", 1)
        rels_path = f"{folder}/_rels/{fname}.rels"
        rels = files.get(rels_path, b"").decode("utf-8")
        m = re.search(r'<Relationship\b[^>]*Type="' + re.escape(DRAWING_REL) + r'"[^>]*/>', rels)
        if m:
            target = re.search(r'Target="([^"]*)"', m.group(0)).group(1)
            dpath = "xl/" + target.replace("../", "") if target.startswith("../") else target.lstrip("/")
            dxml = files[dpath].decode("utf-8")
            max_id = max([int(i) for i in re.findall(r'<(?:xdr:)?cNvPr[^>]*\bid="(\d+)"', dxml)] + [1])
            body = _renumber("".join(anchors), max_id + 10)
            files[dpath] = dxml.replace("</xdr:wsDr>", body + "</xdr:wsDr>").encode("utf-8")
        else:
            dpath = f"xl/drawings/drawing{next_drawing}.xml"
            next_drawing += 1
            files[dpath] = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                            f'<xdr:wsDr xmlns:xdr="{NS_XDR}" xmlns:a="{NS_A}">' + "".join(anchors)
                            + "</xdr:wsDr>").encode("utf-8")
            ct = ct.replace("</Types>", f'<Override PartName="/{dpath}" ContentType="{DRAWING_CT}"/></Types>')
            ids = [int(i) for i in re.findall(r'Id="rId(\d+)"', rels)]
            rid = f"rId{max(ids + [0]) + 1}"
            rel = f'<Relationship Id="{rid}" Type="{DRAWING_REL}" Target="../drawings/{dpath.rsplit("/", 1)[1]}"/>'
            if rels:
                rels = rels.replace("</Relationships>", rel + "</Relationships>")
            else:
                rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                        + rel + "</Relationships>")
            files[rels_path] = rels.encode("utf-8")
            sx = files[sp].decode("utf-8")
            if 'xmlns:r="' not in sx[:600]:
                sx = re.sub(r"<worksheet\b", f'<worksheet xmlns:r="{NS_R}"', sx, count=1)
            tag = f'<drawing r:id="{rid}"/>'
            for nxt in ("<legacyDrawing", "<legacyDrawingHF", "<picture", "<oleObjects", "<controls",
                        "<webPublishItems", "<tableParts", "<extLst", "</worksheet>"):
                i = sx.find(nxt)
                if i >= 0:
                    sx = sx[:i] + tag + sx[i:]
                    break
            files[sp] = sx.encode("utf-8")
    files["[Content_Types].xml"] = ct.encode("utf-8")
    with zipfile.ZipFile(xlsx_path, "w", zipfile.ZIP_DEFLATED) as z:
        if "[Content_Types].xml" in files:
            z.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        for n, data in files.items():
            z.writestr(n, data)


def _renumber(xml, offset):
    """Shift shape ids (cNvPr id, stCxn/endCxn id) so they don't collide with existing ones."""
    return re.sub(r'(<(?:xdr:cNvPr|a:stCxn|a:endCxn)\b[^>]*?\bid=")(\d+)"',
                  lambda m: f'{m.group(1)}{int(m.group(2)) + offset}"', xml)
