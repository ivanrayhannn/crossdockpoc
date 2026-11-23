// Build: node build_addendum.js out.pptx  (TMMIN design system)
const tm = require(process.env.TM_THEME);
const { b, t, hl, red, C } = tm;
const deck = tm.createDeck({ title: "Cross Dock Implementation – Addendum" });
const P = deck.pres, S = deck.S, F = "Segoe UI";
const box = (s, x, y, w, h, text, o = {}) => s.addText(text, { x, y, w, h, fontFace: F, fontSize: o.fs || 10.5, color: o.color || C.body,
  bold: !!o.bold, align: o.align || "center", valign: o.valign || "middle", margin: o.margin ?? 4,
  shape: o.shape || S.RECTANGLE, fill: { color: o.fill || "FFFFFF" }, line: { color: o.line || "7F7F7F", width: o.lw || 1, dashType: o.dash || "solid" }, rectRadius: o.r });
const arrow = (s, x1, y1, x2, y2, o = {}) => s.addShape(S.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
  flipH: x2 < x1, flipV: y2 < y1, line: { color: o.color || "404040", width: o.w || 1.25, endArrowType: o.noHead ? undefined : "triangle", dashType: o.dash || "solid" } });

const s = deck.content("Cross Dock – Process Flow, Open Issue & ASN Sample");
deck.keyMessage(s, { lead: "Supplier packs 1 case = 1 destination", text: " (no W/H sorting); 2 AP POLE issues need answer from Jaturong san by 27 Nov", y: 0.7, h: 0.38, fontSize: 13 });
// ── Process flow (one row)
s.addText([b("Process flow")], { x: tm.MX, y: 1.15, w: 3, h: 0.22, fontFace: F, fontSize: 11, color: C.charcoal, margin: 0 });
deck.chevronFlow(s, { y: 1.4, h: 0.62, fontSize: 9.5, steps: [
  { label: "Register Part", sub: "Procurement" }, { label: "Map Destination", sub: "D/S" }, { label: "Sync Master", sub: "RPA → AP POLE" },
  { label: "Customer Order", sub: "AP POLE → NSP" }, { label: "Crossdock PO", sub: "NSP · order date+1" },
  { label: "ASN Creation", sub: "Supplier · per dest." }, { label: "Receive & Ship", sub: "PBOD W/H · no sorting" },
] });
s.addText("Master setting (once per period)  →  daily operation", { x: tm.MX, y: 2.03, w: 6, h: 0.18, fontFace: F, fontSize: 9, italic: true, color: C.muted, margin: 0 });

const TOP = 2.3, BOT = 6.72, LW = 6.15, RX = tm.MX + LW + 0.2, RW = tm.CW - LW - 0.2;
const head = (x, y, w, txt) => box(s, x, y, w, 0.3, txt, { fill: C.navy, color: "FFFFFF", bold: true, fs: 10.5, line: C.navy, align: "left", margin: 6 });
const ACC = { proc: "2E75B6", ds: "C55A11", sa: "595959" };
// ── Issue #1
{ const x = tm.MX, y = TOP, h = 2.15;
  head(x, y, LW, "Issue #1  RPA account & menu access (auto sync master)");
  s.addShape(S.RECTANGLE, { x, y: y + 0.3, w: LW, h: h - 0.3, fill: { color: "FFFFFF" }, line: { color: C.grayLine } });
  const accs = [["Procurement", ACC.proc], ["D/S", ACC.ds], ["Superadmin", ACC.sa]];
  accs.forEach(([n, c], k) => box(s, x + 0.1, y + 0.42 + k * 0.34, 1.05, 0.27, n + " acc", { fill: c, color: "FFFFFF", bold: true, fs: 8.5, line: c, margin: 2 }));
  accs.forEach((_, k) => arrow(s, x + 1.15, y + 0.555 + k * 0.34, x + 1.27, y + 0.555 + k * 0.34, { noHead: true, w: 1 }));
  arrow(s, x + 1.27, y + 0.555, x + 1.27, y + 1.235, { noHead: true, w: 1 });
  arrow(s, x + 1.27, y + 0.895, x + 1.42, y + 0.895, { w: 1 });
  box(s, x + 1.42, y + 0.7, 0.7, 0.4, "Login\n(Auth)", { fs: 8.5, bold: true, fill: C.panel, margin: 1 });
  const sx = x + 2.3, sw = LW - 2.4;
  arrow(s, x + 2.12, y + 0.9, sx, y + 0.9, { w: 1 });
  box(s, sx, y + 0.36, sw, 1.08, "", { line: "404040" });
  s.addText("AP POLE System", { x: sx + 0.06, y: y + 0.38, w: 2, h: 0.18, fontFace: F, fontSize: 8.5, bold: true, color: C.navy, margin: 0 });
  const menus = [["Upload Kanban", [ACC.proc, ACC.sa]], ["Kanban Part Master\n(WLM9Q890)", [ACC.proc, ACC.sa]], ["Upload Export", [ACC.ds, ACC.sa]], ["Export CD Master\n(WLM9Q860)", [ACC.ds, ACC.sa]]];
  const mw = (sw - 0.25) / 4;
  menus.forEach(([n, cs], k) => { const mx = sx + 0.05 + k * (mw + 0.05), my = y + 0.6;
    box(s, mx, my, mw, 0.78, "", {});
    cs.forEach((c, j) => s.addShape(S.RECTANGLE, { x: mx + mw - 0.17 - j * 0.15, y: my + 0.05, w: 0.12, h: 0.12, fill: { color: c }, line: { color: c } }));
    s.addText(n, { x: mx + 0.03, y: my + 0.2, w: mw - 0.06, h: 0.55, fontFace: F, fontSize: 8, color: C.body, margin: 0, valign: "top" }); });
  s.addText([t("■ ", { color: ACC.proc }), t("Procurement  "), t("■ ", { color: ACC.ds }), t("D/S  "), t("■ ", { color: ACC.sa }), t("Superadmin")],
    { x: x + 0.1, y: y + 1.47, w: 3.5, h: 0.16, fontFace: F, fontSize: 8, color: C.muted, margin: 0 });
  s.addText([b("Countermeasure: "), t("propose "), b("functional user account"), t(" (not personal) for RPA with access to all 4 menus.  "), b("PIC "), t("IS) Zaenal, IS) Rayhan · "), b("Due "), b("27 Nov")],
    { x: x + 0.1, y: y + 1.66, w: LW - 0.2, h: 0.45, fontFace: F, fontSize: 9, color: C.body, margin: 0, valign: "top" });
}
// ── Issue #2
{ const x = tm.MX, y = TOP + 2.27, h = BOT - (TOP + 2.27);
  head(x, y, LW, "Issue #2  Upload function (existing) – no log in AP POLE");
  s.addShape(S.RECTANGLE, { x, y: y + 0.3, w: LW, h: h - 0.3, fill: { color: "FFFFFF" }, line: { color: C.grayLine } });
  const bx = x + 0.6, bw = LW - 1.2;
  box(s, bx, y + 0.4, bw, 0.92, "", { line: "404040" });
  s.addText("AP POLE System", { x: bx + 0.06, y: y + 0.42, w: 2, h: 0.18, fontFace: F, fontSize: 8.5, bold: true, color: C.navy, margin: 0 });
  box(s, bx + 0.2, y + 0.66, 1.8, 0.55, "Upload function (existing)\nLM9Q900 / LM9Q870", { fs: 8.5, fill: C.panel, margin: 2 });
  box(s, bx + bw - 1.5, y + 0.66, 1.3, 0.55, "Log\n(result per row)", { fs: 8.5, fill: C.panel, margin: 2 });
  arrow(s, bx + 2.0, y + 0.935, bx + bw - 1.5, y + 0.935, { w: 1 });
  s.addText("✖", { x: bx + 2.0 + (bw - 3.5) / 2 - 0.2, y: y + 0.75, w: 0.4, h: 0.38, fontFace: F, fontSize: 18, color: C.red, bold: true, align: "center", margin: 0 });
  s.addText([red("Impact: "), t("success / error per row is not visible when testing the master upload. "), b("Countermeasure: "), t("under discussion with Jaturong san.  "),
    b("PIC "), t("IS) Zaenal, IS) Rayhan · "), b("Due "), b("27 Nov")],
    { x: x + 0.1, y: y + 1.4, w: LW - 0.2, h: h - 1.45, fontFace: F, fontSize: 9, color: C.body, margin: 0, valign: "top" });
}
// ── ASN sample
{ const x = RX, y = TOP, w = RW, h = BOT - TOP;
  head(x, y, w, "ASN Crossdock Creation – case grouped by destination (sample)");
  s.addShape(S.RECTANGLE, { x, y: y + 0.3, w, h: h - 0.3, fill: { color: "F4F6F9" }, line: { color: C.grayLine } });
  s.addText([t("Delivery ", { color: C.muted }), b("19-Oct-2026"), t("   Rit ", { color: C.muted }), b("1"), t("   Route ", { color: C.muted }), b("SD01"),
    t("   Supplier ", { color: C.muted }), b("5001 · 1")], { x: x + 0.1, y: y + 0.36, w: w - 0.2, h: 0.24, fontFace: F, fontSize: 9, color: C.body, margin: 0 });
  s.addText([b("Order date 17-Oct-2026 · PART-X"), t("  5 cases · 30 pcs · PO Readiness 4/5", { color: C.muted })],
    { x: x + 0.1, y: y + 0.62, w: w - 0.2, h: 0.22, fontFace: F, fontSize: 9, color: C.body, margin: 0 });
  const ch = (txt, o = {}) => ({ text: txt, options: o });
  const G = (txt) => ch(txt, { colspan: 6, bold: true, color: C.navy, fill: { color: "DEEBF7" }, align: "left" });
  const rd = (st) => ch(st, { color: st === "Ready" ? "2E7D32" : C.redDark, bold: true, align: "center" });
  const rows = [["☐", "Case", "Customer Order No", "Qty", "PO", "Status"],
    [G("Dest 9715310 – Korea · 2 cases · 12 pcs")],
    ["☑", "Case 1", "CO-14105 (6)", "6", "PO-0002", rd("Ready")],
    ["☑", "Case 2", "CO-14106 (3) + CO-14107 (3)", "6", "PO-0003", rd("Ready")],
    [G("Dest 9722D10 – Japan · 1 case · 6 pcs")],
    ["☑", "Case 3", "CO-14104 (6)", "6", "PO-0003", rd("Ready")],
    [G("Dest 9811110 – Taiwan · 1 case · 6 pcs")],
    ["☑", "Case 4", "CO-14109 (6)", "6", "PO-0003", rd("Ready")],
    [G("Dest 982220 – Australia · 1 case · 6 pcs")],
    [ch("☐", { color: "BFBFBF" }), "Case 5", "CO-14110 (6)", "6", "—", rd("Not Ready")]];
  const tw = w - 0.2;
  deck.table(s, rows, { x: x + 0.1, y: y + 0.9, w: tw, colW: [0.3, 0.6, tw - 3.15, 0.4, 0.8, 1.05], fontSize: 9, rowH: 0.27, headerH: 0.27,
    align: ["center", "left", "left", "right", "left", "center"] });
  s.addText([t("Selected "), b("4 cases · 24 pcs"), t(" – Case 5 waits for split PO")], { x: x + 0.1, y: y + 3.67, w: w - 1.4, h: 0.24, fontFace: F, fontSize: 9, color: C.body, margin: 0 });
  box(s, x + w - 1.2, y + 3.64, 1.1, 0.28, "Create ASN", { fill: "2F5597", color: "FFFFFF", line: "2F5597", fs: 9, bold: true, shape: S.ROUNDED_RECTANGLE, r: 0.05 });
  s.addText([b("Rules: "), t("1 case = 1 destination · a case can hold several orders of the same destination · label printed per destination · cases ticked from Case 1 · Not Ready case cannot be sent")],
    { x: x + 0.1, y: y + 3.98, w: w - 0.2, h: 0.42, fontFace: F, fontSize: 8.5, color: C.muted, margin: 0, valign: "top" });
}
deck.conclusion(s, [b("Request: "), t("Jaturong san to confirm "), b("RPA functional account"), t(" and "), b("upload log"), t(" by "), hl("27 Nov")], { h: 0.42, fontSize: 12 });
deck.save(process.argv[2]).then(() => console.log("saved"));
