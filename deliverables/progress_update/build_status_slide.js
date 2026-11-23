// One-slide status: "1. Cross Dock Implementation" + process flow + issue flow + ASN sample.
// Build: TM_THEME=<skill>/scripts/tmmin_theme.js node build_status_slide.js out.pptx
const tm = require(process.env.TM_THEME);
const { b, t, hl, red, C } = tm;
const deck = tm.createDeck({ title: "Cross Dock Implementation" });
const S = deck.S, F = "Segoe UI";
const s = deck.content("1. Cross Dock Implementation");
const T = (txt, o) => s.addText(txt, { fontFace: F, margin: 0, color: C.body, valign: "middle", ...o });
const R = (o) => s.addShape(S.RECTANGLE, { line: { color: C.grayLine, width: 0.75 }, fill: { color: "FFFFFF" }, ...o });
const BX = (x, y, w, h, txt, o = {}) => s.addText(txt, { x, y, w, h, fontFace: F, fontSize: o.fs || 7.5, bold: !!o.bold, color: o.color || C.body, align: o.align || "center",
  valign: o.valign || "middle", margin: o.m ?? 1, shape: o.shape || S.RECTANGLE, fill: { color: o.fill || "FFFFFF" }, line: { color: o.line || "7F7F7F", width: o.lw || 0.75 } });
const LN = (x1, y1, x2, y2, head = true, color = "404040") => s.addShape(S.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
  line: { color, width: 0.9, endArrowType: head ? "triangle" : undefined } });
const H = (x, y, w, txt, extra) => T([b(txt, { color: C.title }), ...(extra || [])], { x, y, w, h: 0.2, fontSize: 11 });
const tbl = (rows, o) => s.addTable(rows, { fontFace: F, fontSize: 8, margin: [0, 0.04, 0, 0.04], valign: "middle", border: { type: "solid", color: "BFBFBF", pt: 0.5 }, autoPage: false, ...o });
const hd = (txt, o = {}) => ({ text: txt, options: { bold: true, color: "FFFFFF", fill: { color: C.navy }, align: "center", ...o } });

deck.keyMessage(s, { lead: "DR phase on schedule", text: [t(" — 24 of 42 DR tasks done (57%), follow-up issue remaining "), hl("27 Nov")], y: 0.66, h: 0.3, fontSize: 12 });

// ── Process flow strip
const PY = 1.02, PH = 0.4;
BX(tm.MX, PY, 0.95, PH, "Process\nFlow", { fill: C.navy, color: "FFFFFF", bold: true, fs: 9, line: C.navy });
deck.chevronFlow(s, { x: tm.MX + 1.0, y: PY, w: tm.CW - 1.0, h: PH, fontSize: 8.5, steps: [
  { label: "Register Part", sub: "Procurement" }, { label: "Map Destination", sub: "D/S" }, { label: "Sync Master", sub: "RPA → AP POLE / GTOPAS" },
  { label: "Customer Order", sub: "AP POLE → NSP" }, { label: "Crossdock PO", sub: "NSP · order date + 1" },
  { label: "ASN Creation", sub: "Supplier · case per dest." }, { label: "Receive & Ship", sub: "PBOD W/H · no sorting" } ] });

const LX = tm.MX, LW = 6.4, RX = 6.85, RW = tm.MX + tm.CW - 6.85;

// ── Project Information / Status
{ const y = 1.52, h = 0.8, sw = 2.3, iw = LW - sw - 0.06;
  BX(LX, y, iw, 0.24, "Project Information", { fill: C.navy, color: C.highlight, bold: true, fs: 11, line: C.navy });
  BX(LX + iw + 0.06, y, sw, 0.24, "Project Status", { fill: C.navy, color: C.highlight, bold: true, fs: 11, line: C.navy });
  R({ x: LX, y: y + 0.24, w: iw, h: h - 0.24 }); R({ x: LX + iw + 0.06, y: y + 0.24, w: sw, h: h - 0.24 });
  const kv = (k, v) => [t(k + " : ", { color: C.muted }), b(v, { color: C.title, breakLine: true })];
  T([...kv("Vendor", "FID"), ...kv("PM (Vendor)", "Andri G"), ...kv("PM (ISTD)", "Zaenal")], { x: LX + 0.1, y: y + 0.27, w: iw / 2, h: h - 0.3, fontSize: 9 });
  T([...kv("QA Team", "FID"), ...kv("Go-Live", "02-Apr-27")], { x: LX + iw / 2, y: y + 0.27, w: iw / 2 - 0.1, h: h - 0.3, fontSize: 9 });
  const sx = LX + iw + 0.06;
  T([t("Phase  Plan : ", { color: C.muted }), b("DR", { breakLine: true }), t("        Actual : ", { color: C.muted }), b("DR")], { x: sx + 0.08, y: y + 0.27, w: 1.25, h: h - 0.3, fontSize: 9 });
  [["Delivery", "G"], ["Quality", "G"], ["Cost", "-"]].forEach(([k, v], i) => { const yy = y + 0.3 + i * 0.16;
    T(k, { x: sx + 1.35, y: yy, w: 0.6, h: 0.15, fontSize: 8, color: C.muted });
    if (v === "G") s.addShape(S.OVAL, { x: sx + 1.98, y: yy + 0.015, w: 0.12, h: 0.12, fill: { color: C.greenOk }, line: { color: C.greenOk } });
    else T("–", { x: sx + 1.98, y: yy, w: 0.15, h: 0.15, fontSize: 8, color: C.muted }); });
}

// ── Gantt (compact, hand-drawn)
{ const y = 2.58, lw = 1.35, gx = LX + lw, gw = LW - lw;
  const periods = [["Oct–Nov'26", ["26","2","9","16","23","30"]], ["Dec'26", ["7","14","21","28"]], ["Jan'27", ["4","11","18","25"]],
                   ["Feb'27", ["1","8","15","22"]], ["Mar'27", ["1","8","15","22","29"]], ["Apr'27", ["5","12","19"]]];
  const N = 26, cw = gw / N, h1 = 0.2, h2 = 0.17, rh = 0.21, top = y + h1 + h2;
  BX(LX, y, lw, h1 + h2, "Activity", { fill: C.navy, color: "FFFFFF", bold: true, fs: 9.5, line: "FFFFFF" });
  let ci = 0;
  periods.forEach(([p, subs]) => { BX(gx + ci * cw, y, subs.length * cw, h1, p, { fill: C.navy, color: "FFFFFF", bold: true, fs: 8.5, line: "FFFFFF" });
    subs.forEach((d, k) => BX(gx + (ci + k) * cw, y + h1, cw, h2, d, { fill: C.navy, color: "FFFFFF", fs: 6.5, line: "FFFFFF", m: 0 })); ci += subs.length; });
  const rows = [["DR", "DR Document", [[0, 0.9, "UR", "done"], [0.9, 6, "DR", "plan"]]], ["PU", "PG & PT", [[6, 10, "PG + PT Exec"]]],
    ["ST", "IFT · BCT · N-BCT", [[11, 12.4, "IFT"], [12.5, 14.6, "(N-)BCT"]]], ["UT", "Prep · Exec", [[15.5, 20.5, "UT Prep + Exec"]]], ["IP", "Go-Live 02-Apr", [[22.6, 23.4, "IP"]]]];
  R({ x: LX, y: top, w: LW, h: rows.length * rh });
  for (let k = 1; k < N; k++) s.addShape(S.LINE, { x: gx + k * cw, y: top, w: 0, h: rows.length * rh, line: { color: C.grayLine, width: 0.4, dashType: "sysDot" } });
  rows.forEach(([code, name, bars], i) => { const ry = top + i * rh;
    if (i) s.addShape(S.LINE, { x: LX, y: ry, w: LW, h: 0, line: { color: C.grayLine, width: 0.5 } });
    T([b(code + "  "), t(name)], { x: LX + 0.05, y: ry, w: lw - 0.05, h: rh, fontSize: 8, color: C.title });
    bars.forEach(([f, to, lab, st]) => BX(gx + f * cw, ry + 0.03, (to - f) * cw, rh - 0.06, lab, { shape: S.PENTAGON, fs: 6.5, fill: st === "done" ? C.blueLight : "FFFFFF", bold: st === "done", line: st === "done" ? C.navy : "404040", m: 0 })); });
  s.addShape(S.STAR_5_POINT, { x: gx + 23.45 * cw, y: top + 4 * rh + 0.02, w: 0.16, h: 0.16, fill: { color: "FF0000" }, line: { color: "FF0000" } });
  const tx = gx + 4.1 * cw;
  BX(tx - 0.25, y - 0.2, 0.5, 0.15, "Today", { fill: C.redDark, color: "FFFFFF", bold: true, fs: 7, line: C.redDark, m: 0 });
  s.addShape(S.LINE, { x: tx, y: y - 0.05, w: 0, h: h1 + h2 + rows.length * rh + 0.05, line: { color: C.redDark, width: 1.75 } });
  T([b("Holiday weeks: "), t("28-Dec, 01-Mar, 08-Mar")], { x: LX, y: top + rows.length * rh + 0.01, w: 3, h: 0.14, fontSize: 7, italic: true, color: C.muted });
}

// ── QA / Request / Issue List with flow
{ const y = 4.2;
  H(LX, y, LW, "QA / Request / Issue List");
  const cw = [0.25, 1.5, 2.55, 1.04, 0.64, 0.42], rh = 1.29, ty = y + 0.23, hh = 0.2;
  const cell = (txt, o = {}) => ({ text: txt, options: { valign: "middle", ...o } });
  tbl([[hd("No"), hd("Issue Description"), hd("Flow"), hd("Countermeasure"), hd("PIC"), hd("Due")],
    [cell("1", { align: "center" }), cell([b("Requirement. "), t("Auto synchronize when user maintains master in NSP → synchron to AP POLE & GTOPAS. Account AP POLE & GTOPAS for RPA (this dedicated account maintains master AP POLE & GTOPAS by RPA)")]), "",
     cell("Propose user functional account (not Zaenal) to Jaturong san"), cell("IS) Zaenal\nIS) Rayhan"), cell([hl("27 Nov")], { align: "center", bold: true })],
    [cell("2", { align: "center" }), cell([b("Requirement. "), t("Upload function (existing) unable to get the log in AP POLE when user tests uploading master data in AP POLE")]), "",
     cell("Under discussion with Jaturong san"), cell("IS) Zaenal\nIS) Rayhan"), cell([hl("27 Nov")], { align: "center", bold: true })]],
    { x: LX, y: ty, w: LW, colW: cw, rowH: [hh, rh, rh], fontSize: 7.5 });
  const fx = LX + cw[0] + cw[1] + 0.05, fw = cw[2] - 0.1;
  // Flow #1: accounts → login → AP POLE menus
  { const y0 = ty + hh + 0.05, A = [["Procurement", "2E75B6"], ["D/S", "C55A11"], ["Superadmin", "595959"]];
    A.forEach(([n, c], k) => BX(fx, y0 + 0.2 + k * 0.27, 0.62, 0.2, n, { fill: c, color: "FFFFFF", bold: true, fs: 6.5, line: c, m: 0 }));
    A.forEach((_, k) => LN(fx + 0.62, y0 + 0.3 + k * 0.27, fx + 0.68, y0 + 0.3 + k * 0.27, false));
    LN(fx + 0.68, y0 + 0.3, fx + 0.68, y0 + 0.84, false); LN(fx + 0.68, y0 + 0.57, fx + 0.74, y0 + 0.57);
    BX(fx + 0.74, y0 + 0.43, 0.38, 0.28, "Login\n(Auth)", { fs: 6.5, bold: true, fill: C.panel, m: 0 });
    const ax = fx + 1.2, aw = fw - 1.2; LN(fx + 1.12, y0 + 0.57, ax, y0 + 0.57);
    BX(ax, y0, aw, 1.12, "", { line: "404040" });
    T("AP POLE System", { x: ax + 0.03, y: y0 + 0.02, w: aw, h: 0.13, fontSize: 6.5, bold: true, color: C.navy });
    const M = [["Upload\nKanban", ["2E75B6", "595959"]], ["Screen\nKanban Master", ["2E75B6", "595959"]], ["Upload\nExport", ["C55A11", "595959"]], ["Screen\nExport Master", ["C55A11", "595959"]]];
    const mw = (aw - 0.09) / 2;
    M.forEach(([n, cs], k) => { const mx = ax + 0.03 + (k % 2) * (mw + 0.03), my = y0 + 0.17 + Math.floor(k / 2) * 0.47;
      BX(mx, my, mw, 0.43, "", {});
      cs.forEach((c, j) => s.addShape(S.RECTANGLE, { x: mx + mw - 0.12 - j * 0.1, y: my + 0.03, w: 0.08, h: 0.08, fill: { color: c }, line: { color: c } }));
      T(n, { x: mx + 0.03, y: my + 0.12, w: mw - 0.04, h: 0.3, fontSize: 6.5, valign: "top" }); });
    T([t("■", { color: "2E75B6" }), t(" Proc  "), t("■", { color: "C55A11" }), t(" D/S  "), t("■", { color: "595959" }), t(" Superadmin")], { x: fx, y: y0 + 1.07, w: 1.2, h: 0.14, fontSize: 6, color: C.muted });
  }
  // Flow #2: upload → ✖ → log
  { const y0 = ty + hh + rh + 0.25;
    BX(fx, y0, fw, 0.85, "", { line: "404040" });
    T("AP POLE System", { x: fx + 0.04, y: y0 + 0.03, w: 1.5, h: 0.14, fontSize: 6.5, bold: true, color: C.navy });
    BX(fx + 0.1, y0 + 0.25, 0.95, 0.45, "Upload function\n(existing)", { fs: 7, fill: C.panel });
    BX(fx + fw - 0.75, y0 + 0.25, 0.65, 0.45, "Log", { fs: 7.5, fill: C.panel });
    LN(fx + 1.05, y0 + 0.475, fx + fw - 0.75, y0 + 0.475);
    T("✖", { x: fx + 1.05 + (fw - 1.8) / 2 - 0.12, y: y0 + 0.35, w: 0.24, h: 0.25, fontSize: 13, bold: true, color: "FF0000", align: "center" });
  }
}

// ── DR Summary + this week
{ const y = 1.52, tw = 4.0;
  H(RX, y, RW, "DR Summary", [t("    Overall : "), b("On schedule", { color: "016338" })]);
  const g = (v) => ({ text: v, options: { fill: { color: "E2EFDA" }, align: "center" } }), c = (v) => ({ text: v, options: { align: "center" } });
  tbl([[hd("DR Task"), hd("Total"), hd("Plan (Acc.)"), hd("Actual (Acc.)"), hd("Achieve")],
    ["DR Start", c("14"), c("9"), g("9"), c("9")], ["DR Finish", c("14"), c("9"), g("9"), c("9")], ["DR Review", c("14"), c("6"), g("6"), c("6")],
    [{ text: "Total", options: { bold: true } }, { text: "42", options: { bold: true, align: "center" } }, { text: "24", options: { bold: true, align: "center" } }, g("24"), c("24")]],
    { x: RX, y: y + 0.23, w: tw, colW: [0.9, 0.6, 0.8, 0.9, 0.8], rowH: 0.18 });
  BX(RX + tw + 0.12, y + 0.23, RW - tw - 0.12, 0.9, [b("This week :", { color: C.navy, breakLine: true }), t("DR Creation", { breakLine: true }), b("Next week :", { color: C.navy, breakLine: true }), t("DR Creation and Review")],
    { fill: C.tintSoft, line: "BDD7EE", align: "left", fs: 9, m: 5 });
}

// ── Detail Functions (two halves)
{ const y = 2.72;
  H(RX, y, RW, "Detail Functions", [t("   ● Completion  ▲ On progress  – Not started   (Master: 1–4, Transaction: 5–14)", { color: C.muted, fontSize: 7.5, bold: false })]);
  const F14 = [["Cross Dock Part Master", "Screen", "●", "●"], ["Cross Dock Part Master Upload", "Batch", "●", "●"], ["Cross Dock Part Dest. Upload", "Batch", "●", "●"],
    ["Dest. Master Synch into NSP", "Batch", "●", "●"], ["Actual Demand Summary to NSP", "Batch", "●", "●"], ["Order Control Info to NSP", "Batch", "●", "●"],
    ["DAD Volume Calculation", "Batch", "●", "-"], ["Mapping Customer Order and PO", "Batch", "●", "-"], ["ASN Cross Dock Creation", "Screen", "▲", "-"],
    ["Change Order Number", "Screen", "-", "-"], ["IF Cross Dock Master to GTOPAS", "Batch", "-", "-"], ["IF Cross Dock Master to AP POLE", "Batch", "-", "-"],
    ["ASN Creation (Existing)", "Screen", "-", "-"], ["ASN Upload (Existing)", "Batch", "-", "-"]];
  const mk = (v) => ({ text: v, options: { align: "center", bold: v !== "-", color: v === "●" ? "00B050" : v === "▲" ? "FFC000" : C.muted } });
  const hw = (RW - 0.08) / 2;
  [0, 7].forEach((st, half) => tbl([[hd("#"), hd("Function Name"), hd("Type"), hd("Cr."), hd("Rv.")],
    ...F14.slice(st, st + 7).map((r, i) => [{ text: String(st + i + 1), options: { align: "center", fill: { color: st + i < 4 ? "DEEBF7" : "FFFFFF" } } }, r[0], { text: r[1], options: { align: "center" } }, mk(r[2]), mk(r[3])])],
    { x: RX + half * (hw + 0.08), y: y + 0.23, w: hw, colW: [0.2, hw - 1.22, 0.42, 0.3, 0.3], rowH: 0.18, fontSize: 7 }));
}

// ── ASN sample (case grouped by destination)
{ const y = 4.42;
  H(RX, y, RW, "ASN Crossdock Creation – case grouped by destination", [t("  (sample)", { color: C.muted, fontSize: 7.5, bold: false })]);
  const G = (txt) => ({ text: txt, options: { colspan: 6, bold: true, color: C.navy, fill: { color: "DEEBF7" } } });
  const st = (v) => ({ text: v, options: { align: "center", bold: true, color: v === "Ready" ? "2E7D32" : C.redDark } });
  const c = (v) => ({ text: v, options: { align: "center" } });
  tbl([[hd("☐"), hd("Case"), hd("Customer Order No"), hd("Qty"), hd("PO"), hd("PO Status")],
    [G("Dest 9715310 – Korea · 2 cases · 12 pcs")],
    [c("☑"), "Case 1", "CO-14105 (6)", c("6"), "PO-0002", st("Ready")], [c("☑"), "Case 2", "CO-14106 (3) + CO-14107 (3)", c("6"), "PO-0003", st("Ready")],
    [G("Dest 9722D10 – Japan · 1 case · 6 pcs")], [c("☑"), "Case 3", "CO-14104 (6)", c("6"), "PO-0003", st("Ready")],
    [G("Dest 9811110 – Taiwan · 1 case · 6 pcs")], [c("☑"), "Case 4", "CO-14109 (6)", c("6"), "PO-0003", st("Ready")],
    [G("Dest 982220 – Australia · 1 case · 6 pcs")], [c("☐"), "Case 5", "CO-14110 (6)", c("6"), "—", st("Not Ready")]],
    { x: RX, y: y + 0.23, w: RW, colW: [0.3, 0.6, RW - 2.9, 0.4, 0.75, 0.85], rowH: 0.19 });
  T([b("1 case = 1 destination"), t(" → label per destination, W/H ships without sorting. Selected "), b("4 cases · 24 pcs"), t(" (Case 5 waits for split PO).")],
    { x: RX, y: y + 0.23 + 10 * 0.19 + 0.05, w: RW, h: 0.26, fontSize: 7.5, color: C.muted, valign: "top" });
}
deck.save(process.argv[2]).then(() => console.log("saved"));
