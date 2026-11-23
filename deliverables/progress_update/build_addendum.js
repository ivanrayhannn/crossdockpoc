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

// ───────── Slide 1: Issue flow ─────────
{
  const s = deck.content("QA / Issue List – Flow Explanation");
  deck.keyMessage(s, { lead: "2 open issues", text: " need countermeasure from Jaturong san by 27 Nov (RPA account & upload log in AP POLE)", y: 0.72 });
  const top = 1.3, ph = 4.85, gap = 0.25, pw = (tm.CW - gap) / 2;
  const ACC = { proc: "2E75B6", ds: "C55A11", sa: "595959" };
  [0, 1].forEach(i => {
    const x = tm.MX + i * (pw + gap);
    box(s, x, top, pw, 0.36, i === 0 ? "#1  Account & menu access for RPA (auto synchronize master)" : "#2  Upload function (existing) – log not available",
      { fill: C.navy, color: "FFFFFF", bold: true, fs: 12, line: C.navy, align: "left", margin: 8 });
    s.addShape(S.RECTANGLE, { x, y: top + 0.36, w: pw, h: ph, fill: { color: "FFFFFF" }, line: { color: C.grayLine, width: 1 } });
  });
  // #1 diagram
  { const x0 = tm.MX + 0.2, y0 = top + 0.55;
    const accs = [["Procurement acc", ACC.proc], ["D/S acc", ACC.ds], ["Superadmin acc", ACC.sa]];
    accs.forEach(([n, c], k) => box(s, x0, y0 + 0.35 + k * 0.62, 1.45, 0.42, n, { fill: c, color: "FFFFFF", bold: true, fs: 10, line: c }));
    const lx = x0 + 1.75, ly = y0 + 0.82;
    accs.forEach((_, k) => { const yy = y0 + 0.56 + k * 0.62; arrow(s, x0 + 1.45, yy, x0 + 1.62, yy, { noHead: true }); });
    arrow(s, x0 + 1.62, y0 + 0.56, x0 + 1.62, y0 + 1.80, { noHead: true });
    arrow(s, x0 + 1.62, y0 + 1.18, lx, y0 + 1.18);
    box(s, lx, ly + 0.08, 0.95, 0.56, "Login\n(Auth)", { fs: 10, bold: true, fill: C.panel });
    const sx = lx + 1.2, sw = 2.95;
    box(s, sx, y0, sw, 2.45, "", { line: "404040" });
    s.addText("AP POLE System", { x: sx + 0.08, y: y0 + 0.03, w: 2, h: 0.25, fontFace: F, fontSize: 10, bold: true, color: C.navy, margin: 0 });
    arrow(s, lx + 0.95, y0 + 1.18, sx, y0 + 1.18);
    const menus = [["Upload\nKanban Part Master", [ACC.proc, ACC.sa]], ["Screen Kanban\nPart Master (WLM9Q890)", [ACC.proc, ACC.sa]],
                   ["Upload\nExport CD Master", [ACC.ds, ACC.sa]], ["Screen Export CD\nMaster (WLM9Q860)", [ACC.ds, ACC.sa]]];
    menus.forEach(([n, cs], k) => { const mx = sx + 0.12 + (k % 2) * 1.43, my = y0 + 0.4 + Math.floor(k / 2) * 1.0;
      box(s, mx, my, 1.32, 0.82, "", {});
      s.addText(n, { x: mx + 0.04, y: my + 0.24, w: 1.24, h: 0.55, fontFace: F, fontSize: 8.5, color: C.body, margin: 0, valign: "top" });
      cs.forEach((c, j) => s.addShape(S.RECTANGLE, { x: mx + 1.32 - 0.2 - j * 0.18, y: my + 0.06, w: 0.14, h: 0.14, fill: { color: c }, line: { color: c } })); });
    // legend
    s.addText([b("Access: "), t("■ ", { color: ACC.proc }), t("Procurement   "), t("■ ", { color: ACC.ds }), t("D/S   "), t("■ ", { color: ACC.sa }), t("Superadmin")],
      { x: x0, y: y0 + 2.75, w: pw - 0.4, h: 0.25, fontFace: F, fontSize: 9, color: C.muted, margin: 0 });
    deck.table(s, [["Issue", "Countermeasure"],
      ["NSP must auto-synchronize master to AP POLE & GTOPAS. RPA needs its own account; each menu is limited by role (Procurement / D/S / Superadmin).",
       [b("Propose functional user account"), t(" (not personal, e.g. not Zaenal) for RPA, with access to all 4 menus")]]],
      { x: x0, y: y0 + 3.15, w: pw - 0.4, colW: [(pw - 0.4) * 0.55, (pw - 0.4) * 0.45], variant: "light", fontSize: 9.5, rowH: 0.7, headerH: 0.28, align: ["left", "left"] });
    s.addText([b("PIC: "), t("IS) Zaenal, IS) Rayhan   "), b("Due: "), hl("27 Nov")], { x: x0, y: top + ph + 0.06, w: pw - 0.4, h: 0.24, fontFace: F, fontSize: 9.5, margin: 0 });
  }
  // #2 diagram
  { const x0 = tm.MX + pw + gap + 0.2, y0 = top + 0.55, w = pw - 0.4;
    box(s, x0 + 0.3, y0 + 0.1, w - 0.6, 1.6, "", { line: "404040" });
    s.addText("AP POLE System", { x: x0 + 0.4, y: y0 + 0.13, w: 2, h: 0.25, fontFace: F, fontSize: 10, bold: true, color: C.navy, margin: 0 });
    box(s, x0 + 0.6, y0 + 0.55, 1.9, 0.85, "Upload function\n(existing)\nLM9Q900 / LM9Q870", { fs: 9.5, fill: C.panel });
    box(s, x0 + w - 2.1, y0 + 0.55, 1.5, 0.85, "Log\n(result per row)", { fs: 9.5, fill: C.panel });
    arrow(s, x0 + 2.5, y0 + 0.97, x0 + w - 2.1, y0 + 0.97);
    s.addText("✖", { x: x0 + 2.5 + (w - 4.6) / 2 - 0.2, y: y0 + 0.72, w: 0.5, h: 0.5, fontFace: F, fontSize: 24, color: C.red, bold: true, align: "center", margin: 0 });
    s.addText([red("Impact: "), t("when user tests the master upload, success / error per row cannot be seen, so RPA cannot confirm the sync result.")],
      { x: x0, y: y0 + 1.85, w, h: 0.55, fontFace: F, fontSize: 10, color: C.body, margin: 0, valign: "top" });
    deck.table(s, [["Issue", "Countermeasure"],
      ["Upload function (existing) cannot produce the log in AP POLE when the user tests the master data upload.",
       [b("Under discussion"), t(" with Jaturong san (log output / result file per upload)")]]],
      { x: x0, y: y0 + 3.15, w, colW: [w * 0.55, w * 0.45], variant: "light", fontSize: 9.5, rowH: 0.7, headerH: 0.28, align: ["left", "left"] });
    s.addText([b("PIC: "), t("IS) Zaenal, IS) Rayhan   "), b("Due: "), hl("27 Nov")], { x: x0, y: top + ph + 0.06, w, h: 0.24, fontFace: F, fontSize: 9.5, margin: 0 });
  }
  deck.conclusion(s, [b("Request: "), t("Jaturong san to confirm the "), b("RPA functional account"), t(" and the "), b("upload log"), t(" solution by 27 Nov")], { h: 0.5, fontSize: 13 });
}

// ───────── Slide 2: Simple process flow ─────────
{
  const s = deck.content("Cross Dock – Process Flow (Simple)");
  deck.keyMessage(s, { lead: "Supplier packs 1 case = 1 destination", text: " so the warehouse receives and ships without manual sorting", y: 0.72 });
  deck.subHeading(s, "Master setting (once per period)", { y: 1.35, num: 1 });
  deck.chevronFlow(s, { y: 1.8, h: 0.95, fontSize: 10.5, steps: [
    { label: "Register Part", sub: "Procurement · Kanban CD Master" },
    { label: "Map Destination", sub: "D/S · Export CD Master" },
    { label: "Sync Master", sub: "RPA → AP POLE & GTOPAS" },
  ] });
  deck.subHeading(s, "Daily operation", { y: 3.0, num: 2 });
  deck.chevronFlow(s, { y: 3.45, h: 0.95, fontSize: 10.5, steps: [
    { label: "Customer Order", sub: "AP POLE → NSP" },
    { label: "Crossdock PO", sub: "NSP · order date + 1" },
    { label: "ASN Creation", sub: "Supplier · case per dest." },
    { label: "Receive", sub: "PBOD W/H · no sorting" },
    { label: "Packing & Vanning", sub: "GTOPAS" },
  ] });
  deck.table(s, [["Step", "Who", "Output"],
    ["Register Part / Map Destination", "Procurement / D/S", "Kanban & Export Crossdock Master (Max Case/Day per destination)"],
    ["Sync Master", "RPA (functional account)", "Same master in AP POLE (WLM9Q890 / WLM9Q860) and GTOPAS"],
    ["Crossdock PO → ASN", "NSP / Supplier", "1 PO per part per customer order date; ASN cases grouped by destination"],
  ], { y: 4.65, colW: [3.0, 2.6, tm.CW - 5.6], fontSize: 10.5, rowH: 0.45, headerH: 0.36, align: ["left", "left", "left"], labelCol: true });
  deck.conclusion(s, [b("Key point: "), t("destination is decided at "), hl("supplier case level"), t(" – W/H sort & repack activity is removed")], { h: 0.5, fontSize: 13 });
}

// ───────── Slide 3: ASN screen – cases grouped by destination ─────────
{
  const s = deck.content("ASN Crossdock Creation – Case Grouped by Destination");
  deck.keyMessage(s, { lead: "1 case = 1 destination", text: " – supplier sees which customer orders go into each case and prints the label per destination", y: 0.72 });
  const X = tm.MX, Y = 1.3, W = 8.9;
  // mock screen frame
  s.addShape(S.RECTANGLE, { x: X, y: Y, w: W, h: 5.25, fill: { color: "F4F6F9" }, line: { color: "BFBFBF", width: 1 } });
  box(s, X, Y, W, 0.32, "Supplier System   ›   ASN   ›   ASN Crossdock Creation", { fill: "2F3B52", color: "FFFFFF", line: "2F3B52", fs: 9.5, align: "left", margin: 8 });
  // filter bar
  const fy = Y + 0.42;
  s.addShape(S.RECTANGLE, { x: X + 0.1, y: fy, w: W - 0.2, h: 0.5, fill: { color: "FFFFFF" }, line: { color: "D9D9D9" } });
  [["Delivery Date", "19-Oct-2026"], ["Rit", "Rit 1"], ["Route", "SD01"], ["Supplier · Plant", "5001 · 1"]].forEach(([l, v], k) => {
    s.addText([t(l + "  ", { color: C.muted, fontSize: 8.5 }), b(v, { fontSize: 9.5 })], { x: X + 0.2 + k * 1.85, y: fy + 0.08, w: 1.8, h: 0.34, fontFace: F, margin: 0, color: C.body }); });
  box(s, X + W - 0.95, fy + 0.1, 0.75, 0.3, "Search", { fill: "2F5597", color: "FFFFFF", line: "2F5597", fs: 9, bold: true, shape: S.ROUNDED_RECTANGLE, r: 0.05 });
  // unit header
  const uy = fy + 0.6;
  s.addText([b("Customer Order Date 17-Oct-2026 · PART-X"), t("   5 cases · 30 pcs · PO Readiness 4 / 5", { color: C.muted })],
    { x: X + 0.12, y: uy, w: W - 0.3, h: 0.28, fontFace: F, fontSize: 10, margin: 0, color: C.body });
  const ch = (txt, o = {}) => ({ text: txt, options: o });
  const G = (txt) => ch(txt, { colspan: 7, bold: true, color: C.navy, fill: { color: "DEEBF7" }, fontSize: 9.5, align: "left" });
  const rd = (st) => ch(st, { color: st === "Ready" ? "2E7D32" : C.redDark, bold: true, align: "center" });
  const rows = [["☐", "Case", "Customer Order No", "Qty", "PO", "PO Status", "Case Label"],
    [G("Destination 9715310 – Korea   ·   2 cases · 12 pcs")],
    ["☑", "Case 1", "CO-14105 (6)", "6", "PO-0002", rd("Ready"), "9715310"],
    ["☑", "Case 2", "CO-14106 (3) + CO-14107 (3)", "6", "PO-0003", rd("Ready"), "9715310"],
    [G("Destination 9722D10 – Japan   ·   1 case · 6 pcs")],
    ["☑", "Case 3", "CO-14104 (6)", "6", "PO-0003", rd("Ready"), "9722D10"],
    [G("Destination 9811110 – Taiwan   ·   1 case · 6 pcs")],
    ["☑", "Case 4", "CO-14109 (6)", "6", "PO-0003", rd("Ready"), "9811110"],
    [G("Destination 982220 – Australia   ·   1 case · 6 pcs")],
    [ch("☐", { color: "BFBFBF" }), "Case 5", "CO-14110 (6)", "6", "—", rd("Not Ready"), "982220"],
  ];
  deck.table(s, rows, { x: X + 0.1, y: uy + 0.33, w: W - 0.2, colW: [0.35, 0.75, 2.75, 0.55, 1.0, 1.1, W - 0.2 - 6.5],
    fontSize: 9.5, rowH: 0.3, headerH: 0.3, align: ["center", "left", "left", "right", "left", "center", "center"] });
  s.addText([t("Selected: "), b("4 cases · 24 pcs"), t("  (Case 5 waits for split PO)")], { x: X + 0.15, y: Y + 4.8, w: 5, h: 0.3, fontFace: F, fontSize: 9.5, margin: 0, color: C.body });
  box(s, X + W - 1.3, Y + 4.78, 1.15, 0.33, "Create ASN", { fill: "2F5597", color: "FFFFFF", line: "2F5597", fs: 9.5, bold: true, shape: S.ROUNDED_RECTANGLE, r: 0.05 });
  s.addText("Illustration – sample data from the POC (PART-X, 6 pcs/case)", { x: X, y: Y + 5.28, w: W, h: 0.22, fontFace: F, fontSize: 9, italic: true, color: C.muted, margin: 0 });
  // rules panel
  deck.panel(s, { x: X + W + 0.2, y: Y, w: tm.CW - W - 0.2, h: 3.0, heading: "Grouping rules", fontSize: 10.5, body: [
    "Cases are grouped per Destination; one case never mixes destinations",
    "A case can hold several customer orders of the same destination (Case 2: 3 + 3 pcs)",
    "Case label shows the destination → W/H ships without sorting",
    "Cases are ticked from Case 1 in order; a Not Ready case (no PO yet) cannot be sent",
    "One ASN = one Supplier Code + Plant",
  ] });
  // case label sample
  { const lx = X + W + 0.2, lw = tm.CW - W - 0.2, ly = Y + 3.15;
    s.addText("Case label sample (Case 2)", { x: lx, y: ly, w: lw, h: 0.25, fontFace: F, fontSize: 10.5, bold: true, color: C.navy, margin: 0 });
    box(s, lx + 0.1, ly + 0.32, lw - 0.2, 1.7, [b("DEST  9715310", { fontSize: 16, breakLine: true }), t("Korea · Route SD01 · Rit 1", { breakLine: true }),
      t("PART-X · 6 pcs · Case 2 / 5", { breakLine: true }), t("CO-14106 (3) + CO-14107 (3)", { color: C.muted })], { fs: 10.5, line: "404040", lw: 1.5, dash: "dash" });
  }
  deck.conclusion(s, [b("Benefit: "), t("destination is fixed at "), hl("supplier packing"), t(" – no sort & repack at PBOD warehouse")], { h: 0.45, fontSize: 13 });
}
deck.save(process.argv[2]).then(() => console.log("saved"));
