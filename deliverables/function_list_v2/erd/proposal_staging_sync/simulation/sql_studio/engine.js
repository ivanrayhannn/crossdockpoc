
// ---------- engine: the rules of SP_STG_WRITE, SP_STG_SYNC, the views and AP POLE ----------
const DEST = { JAPAN: '9722D10', KOREA: '9715310', TAIWAN: '9811110', USA: '9600110', THAILAND: '9655510' };
const NAME = (p) => 'DUMMY PART ' + p.slice(-3);
const my = (per) => per.slice(4) + '/' + per.slice(0, 4);
const clone = (o) => JSON.parse(JSON.stringify(o));
let M = {}, K = [], E = [], G = [], AP = { kan: {}, exp: {} }, GT = {}, ids = { k: 0, e: 0, g: 0 }, seq = 0;
let calls = [], touched = [], deleted = [], files = null, gsent = null, now = '', rpa = null;
// SYNC_DT of a run: 20261110110000 -> 2026-11-10 11:00:00 (the run is the time of the [Sync] click)
const sdtOf = (run) => `${run.slice(0, 4)}-${run.slice(4, 6)}-${run.slice(6, 8)} ${run.slice(8, 10)}:${run.slice(10, 12)}:${run.slice(12, 14)}`;

const byPerSeq = (a, b) => (a.per !== b.per ? (a.per < b.per ? -1 : 1) : (a.seq - b.seq) || (a.id - b.id));
function lastSent(arr, keyOf, key, per, beforeSeq) {
  return arr.filter((r) => r.st === 1 && keyOf(r) === key && r.per <= per && (beforeSeq == null || r.seq < beforeSeq)).sort(byPerSeq).pop();
}
const kKey = (r) => r.p, eKey = (r) => r.p + '|' + r.d + '|' + r.ot, gKey = (r) => r.p + '|' + r.d;

// one unsent row per key (26-Nov): a new change updates it, a change back to the value sent deletes it; no status 2
function delRow(arr, tag, r, why) {
  arr.splice(arr.indexOf(r), 1);
  deleted.push({ tag: tag + r.id, tbl: tag, row: clone(r), why });
  touched.push(tag + r.id);
}
function spKanban(act, per, p, by, src) {
  const m = M[per][p];
  const sent = lastSent(K, kKey, p, per);
  const pend = K.find((r) => r.p === p && r.per === per && r.st === 0);
  const op = !sent ? 4 : m.max < sent.max ? 1 : m.max > sent.max ? 2 : 3;
  const a = sent && sent.per === per ? 'EDIT' : 'ADD';
  const why = sent ? `last sent Max ${sent.max} in ${sent.per}` : 'never sent';
  let line = `SP_STG_WRITE('KANBAN', '${per}', '${p}', Pcs ${m.pcs}, Max ${m.max})\n  → `;
  if (sent && sent.per === per && sent.max === m.max && sent.pcs === m.pcs) {
    if (pend) { delRow(K, 'K', pend, 'back to the values sent'); line += `back to the values sent for ${per}: unsent K${pend.id} deleted (nothing to send)`; }
    else line += `same as the values sent for ${per}: no row`;
  } else if (pend) {
    Object.assign(pend, { act: a, ps: m.st, pcs: m.pcs, max: m.max, op, src });
    touched.push('K' + pend.id);
    line += `K${pend.id} updated (one unsent row per key): OPERATION_TYPE ${op} (${why})`;
  } else {
    const r = { id: ++ids.k, per, act: a, ps: m.st, p, pcs: m.pcs, max: m.max, op, st: 0, src, by, dt: now, run: null, sdt: null, seq: null };
    K.push(r); touched.push('K' + r.id);
    line += `K${r.id} inserted: OPERATION_TYPE ${op} (${why}), SYNC_STATUS 0`;
  }
  calls.push(line);
  header(per, p, by, src);
}
// header rule (code 5): a part + period with an unsent Export row always has one unsent Kanban row
function header(per, p, by, src) {
  const pe = E.filter((r) => r.per === per && r.p === p && r.st === 0).length;
  const pk = K.find((r) => r.per === per && r.p === p && r.st === 0);
  if (pe && !pk) {
    const m = M[per][p];
    const r = { id: ++ids.k, per, act: 'KEEP', ps: m.st, p, pcs: m.pcs, max: m.max, op: 5, st: 0, src, by, dt: now, run: null, sdt: null, seq: null };
    K.push(r); touched.push('K' + r.id);
    calls.push(`  header: no unsent Kanban row of ${p} ${per} → K${r.id} OPERATION_TYPE 5 (Kanban unchanged, current values, not uploaded)`);
  } else if (!pe && pk && pk.op === 5) {
    delRow(K, 'K', pk, 'header without Export row');
    calls.push(`  header: no unsent Export row of ${p} ${per} any more → header K${pk.id} deleted`);
  }
}
function spExport(act, per, p, d, ot, cd, by, src) {
  const key = p + '|' + d + '|' + ot;
  const sent = lastSent(E, eKey, key, per);
  const pend = E.find((r) => eKey(r) === key && r.per === per && r.st === 0);
  const a = cd === 0 ? 'DELETE' : sent && sent.per === per ? 'EDIT' : 'ADD';
  let line = `SP_STG_WRITE('EXPORT', '${per}', '${p}', ${d} ${ot}, ${cd})\n  → `;
  if ((sent && sent.per === per && sent.cd === cd) || (!sent && cd === 0)) {
    if (pend) { delRow(E, 'E', pend, 'back to the value sent'); line += `back to the value sent: unsent E${pend.id} deleted (nothing to send)`; }
    else line += 'same as the value sent: no row';
  } else if (pend) {
    Object.assign(pend, { act: a, cd, src });
    touched.push('E' + pend.id);
    line += `E${pend.id} updated to ${cd} (one unsent row per key)`;
  } else {
    const r = { id: ++ids.e, per, act: a, p, d, ot, cd, st: 0, src, by, dt: now, run: null, sdt: null, seq: null };
    E.push(r); touched.push('E' + r.id);
    line += `E${r.id} inserted, SYNC_STATUS 0`;
  }
  // GTOPAS: what the master needs for part + destination (any order type) against what GTOPAS has
  const need = Object.entries(M[per][p].d).some(([k, v]) => k.split('|')[0] === d && v > 0) ? 'ADD' : 'DELETE';
  const gs = lastSent(G, gKey, p + '|' + d, per);
  const gSent = gs ? gs.act : 'DELETE';
  const gp = G.find((r) => gKey(r) === p + '|' + d && r.per === per && r.st === 0);
  if (need === gSent) {
    if (gp) { delRow(G, 'G', gp, 'GTOPAS already has it'); line += `; GTOPAS G${gp.id} deleted (GTOPAS already has this state)`; }
    else line += '; GTOPAS: no change for ' + d;
  } else if (gp) {
    if (gp.act !== need) { gp.act = need; gp.src = src; touched.push('G' + gp.id); line += `; GTOPAS G${gp.id} updated to ${need}`; }
    else line += `; GTOPAS G${gp.id} ${need} already waits`;
  } else {
    const g = { id: ++ids.g, per, act: need, p, d, st: 0, src, by, dt: now, run: null, sdt: null, seq: null };
    G.push(g); touched.push('G' + g.id); line += `; GTOPAS G${g.id} ${need} inserted`;
  }
  calls.push(line);
  header(per, p, by, src);
}
function total(per, p) { return Object.values(M[per][p].d).reduce((a, b) => a + b, 0); }
function check(per, p, by) {
  const t = total(per, p), mx = M[per][p].max;
  if (t > mx) throw new Error(`NSP check failed ${p} ${per}: ${t} > ${mx}`);
  calls.push(`NSP check (${by}): ${p} ${per} total Case/Day ${t} ≤ Max ${mx} → save allowed`);
}
// screen / upload saves
function savePart(per, p, ch, by, src = 'SCREEN') {
  const m = M[per][p], old = clone(m);
  Object.assign(m, ch);
  if (old.st === 'Active' && m.st === 'Inactive') {
    const ds = Object.entries(m.d); m.d = {};
    calls.push(`${p} Active → Inactive: the mapping of ${per} is removed (TB_M_PART_CANDIDATE_DEST)`);
    ds.forEach(([k]) => { const [d, ot] = k.split('|'); spExport('DELETE', per, p, d, ot, 0, by, src); });
    return;
  }
  check(per, p, by);
  if (m.st !== 'Active') { calls.push(`${p} is ${m.st}: no staging row`); return; }
  if (old.st === 'Candidate') return spKanban('ADD', per, p, by, src);
  if (old.pcs !== m.pcs || old.max !== m.max) spKanban('EDIT', per, p, by, src);
  else calls.push(`${p}: Pcs/Case and Max unchanged → no Kanban change`);
}
function saveMapping(per, p, nd, by, src = 'SCREEN') {
  const m = M[per][p], od = m.d;
  m.d = clone(nd);
  check(per, p, by);
  Object.keys(od).filter((k) => !(k in nd)).forEach((k) => { const [d, ot] = k.split('|'); spExport('DELETE', per, p, d, ot, 0, by, src); });
  Object.entries(nd).forEach(([k, v]) => { const [d, ot] = k.split('|'); if (!(k in od)) spExport('ADD', per, p, d, ot, v, by, src); else if (od[k] !== v) spExport('EDIT', per, p, d, ot, v, by, src); });
}
function xd05(prevPer, per, spec) {
  M[per] = {};
  Object.entries(spec).forEach(([p, s]) => { M[per][p] = { st: s.st, pcs: s.pcs, max: s.max, d: clone(s.d || {}) }; });
  Object.entries(spec).forEach(([p, s]) => {
    if (s.st === 'Candidate') { calls.push(`${p} Candidate: no staging row`); return; }
    spKanban('ADD', per, p, 'XD05BATCH', 'BATCH');
    const prev = (M[prevPer][p] || { d: {} }).d;
    Object.entries(s.d || {}).forEach(([k, v]) => { const [d, ot] = k.split('|'); spExport('ADD', per, p, d, ot, v, 'XD05BATCH', 'BATCH'); });
    Object.entries(prev).filter(([k, v]) => v > 0 && !(k in (s.d || {}))).forEach(([k]) => { const [d, ot] = k.split('|'); spExport('DELETE', per, p, d, ot, 0, 'XD05BATCH', 'BATCH'); });
  });
}
// AP POLE
const eff = (mp, per) => { const ks = Object.keys(mp || {}).filter((x) => x <= per).sort(); return ks.length ? mp[ks[ks.length - 1]] : undefined; };
function apTotal(p, per) { return Object.values(AP.exp[p] || {}).reduce((a, mp) => a + (eff(mp, per) || 0), 0); }
function apRow(kind, r) {
  const month = r.per;
  if (kind === 'k') { (AP.kan[r.p] ||= {})[month] = { pcs: r.pcs, max: r.max }; }
  else { ((AP.exp[r.p] ||= {})[r.d + '|' + r.ot] ||= {})[month] = r.cd; }
  const t = apTotal(r.p, month), mx = (eff(AP.kan[r.p], month) || {}).max;
  return { t, mx, ok: mx != null && t <= mx };
}
function view(run) {
  const kr = K.filter((r) => r.st === 1 && r.run === run), er = E.filter((r) => r.st === 1 && r.run === run);
  const rows = er.map((e) => {
    const h = kr.find((k) => k.per === e.per && k.p === e.p);   // always found: code 5 when the Kanban did not change
    const prev = lastSent(E, eKey, eKey(e), e.per, e.seq);
    return { r: e, file: h && h.op === 1 ? 'PRE' : 'POST', ro: prev && e.cd < prev.cd ? 1 : 2, prev: prev ? prev.cd : null };
  });
  const sortE = (a, b) => (a.r.per !== b.r.per ? (a.r.per < b.r.per ? -1 : 1) : a.r.p !== b.r.p ? (a.r.p < b.r.p ? -1 : 1) : (a.ro - b.ro) || (a.r.id - b.r.id));
  return {
    pre: rows.filter((x) => x.file === 'PRE').sort(sortE),
    kan: kr.filter((r) => r.op !== 5).sort((a, b) => (a.per !== b.per ? (a.per < b.per ? -1 : 1) : a.p < b.p ? -1 : 1)).map((r) => ({ r })),
    post: rows.filter((x) => x.file === 'POST').sort(sortE),
  };
}
function upload(run) {
  const f = view(run);
  const kr = K.filter((r) => r.st === 1 && r.run === run);
  const parts = [...new Set(E.filter((r) => r.st === 1 && r.run === run).map((r) => r.per + '|' + r.p))].sort();
  calls.push('View, file of the Export rows per part (Kanban row with the same SYNC_DT, part and period):');
  parts.forEach((x) => {
    const [per, p] = x.split('|'); const h = kr.find((k) => k.per === per && k.p === p);
    calls.push(`  ${p} ${per}: header K${h.id}, OPERATION_TYPE ${h.op} → ` + (h.op === 1 ? 'EXPORT_PRE (before KANBAN)' : h.op === 5 ? 'EXPORT_POST only (header not in the KANBAN file)' : 'EXPORT_POST (after KANBAN)'));
  });
  if (!parts.length) calls.push('  no Export row in this run');
  const kf = kr.filter((k) => k.op !== 5);
  calls.push(kf.length ? `  KANBAN file (OPERATION_TYPE 1 to 4): ${kf.map((k) => 'K' + k.id).join(', ')}` : '  no Kanban row with OPERATION_TYPE 1 to 4 in this run → no KANBAN file');
  f.pre.forEach((x) => (x.chk = apRow('e', x.r)));
  f.kan.forEach((x) => (x.chk = apRow('k', x.r)));
  f.post.forEach((x) => (x.chk = apRow('e', x.r)));
  files = { run, ...f };
}
function gApply(rows) { rows.forEach((r) => { if (r.act === 'ADD') GT[r.p + '|' + r.d] = true; else delete GT[r.p + '|' + r.d]; }); gsent = rows; }
function spSync(run, cur, next, by, opt = {}) {
  seq += 1;
  const take = (arr, tag, pers) => arr.filter((r) => r.st === 0 && pers.includes(r.per)).forEach((r) => { r.st = 1; r.run = run; r.sdt = now; r.seq = seq; touched.push(tag + r.id); });
  take(K, 'K', [cur, next]); take(E, 'E', [cur, next]);
  const g = G.filter((r) => r.st === 0 && r.per === cur);
  take(G, 'G', [cur]);
  calls.push(`SP_STG_SYNC(SYNC_DT '${sdtOf(run)}', Current ${cur}, Next ${next}, ${by})\n  → AP POLE rows with SYNC_STATUS 0 of ${cur} and ${next} → 1 with SYNC_DT = time of the click; GTOPAS rows of ${cur} → 1; LAST_SYNC_DATE_APPOLE\n  → start the parent flow CDX_SYNC_PARENT (SYNC_DT ${sdtOf(run)}, RUN_TYPE SYNC)`);
  return parent(run, 'SYNC', opt);
}
function rollover(run, per, opt = {}) {
  seq += 1;
  const g = G.filter((r) => r.st === 0 && r.per === per);
  g.forEach((r) => { r.st = 1; r.run = run; r.sdt = now; r.seq = seq; touched.push('G' + r.id); });
  calls.push(`Period Rollover (XD05 process 3): ${per} becomes Current\n  → SP_STG_ROLLOVER: GTOPAS rows of ${per} with SYNC_STATUS 0 → 1 (${g.length} row(s)), SYNC_DT ${sdtOf(run)}\n  → start the parent flow CDX_SYNC_PARENT (RUN_TYPE ROLLOVER)`);
  return parent(run, 'ROLLOVER', opt);
}
function resend(run, opt = {}) {
  calls.push(`[Re-send last Sync]: last run = MAX(SYNC_DT) = ${sdtOf(run)}; the parent flow starts again with it (RUN_TYPE RESEND); nothing changes in the staging`);
  return parent(run, 'RESEND', opt);
}
// ---------- RPA parent flow: scenario 1 (GTOPAS rows in the run) or 2 (none); rollover = XD06 only ----------
function parent(run, type, opt) {
  const g = G.filter((r) => r.run === run && r.st === 1);
  const sc = type === 'ROLLOVER' ? 'Rollover' : g.length ? '1' : '2';
  rpa = { run, type, sc, gRows: g.length, g: 'skipped', gFail: [], ap: 'skipped', apFile: null };
  calls.push(`Parent flow: SELECT COUNT(*) FROM TB_H_STG_GTOPAS WHERE SYNC_STATUS = '1' AND SYNC_DT = '${sdtOf(run)}' → ${g.length}` +
    (type === 'ROLLOVER' ? ' → RUN_TYPE ROLLOVER: XD06 only' : g.length ? ' → scenario 1: XD06 first, XD07 only when GTOPAS succeeded' : ' → scenario 2: XD07 at once'));
  if (sc !== '2') {
    const fail = g.filter((r) => (opt.failG || []).includes(r.p + '|' + r.d));
    const done = g.filter((r) => !fail.includes(r));
    const before = done.filter((r) => (r.act === 'ADD') === !!GT[r.p + '|' + r.d]);
    gApply(done);
    gsent = g.map((r) => ({ ...r, res: fail.includes(r) ? 'FAILED' : before.includes(r) ? 'OK (already ' + (r.act === 'ADD' ? 'there' : 'gone') + ')' : 'OK' }));
    rpa.g = fail.length ? 'FAILED' : 'SUCCESS';
    rpa.gFail = fail.map((r) => r.p + ' ' + r.d);
    calls.push(`XD06 GTOPAS: ${g.length} row(s), ${done.length} OK` + (fail.length ? `, FAILED ${rpa.gFail.join(', ')}` : '') + (before.length ? ` (${before.length} already in the wanted state)` : ''));
    if (fail.length && type !== 'ROLLOVER') { rpa.ap = 'not started'; calls.push('GTOPAS FAILED → AP POLE stops: XD07 is not started. E-mail FAILED → D/S: [Re-send last Sync]'); return; }
  }
  if (type === 'ROLLOVER') { calls.push(`E-mail ${rpa.g}: GTOPAS result of the rollover`); return; }
  calls.push('XD07 AP POLE: read the views for the run');
  upload(run);
  const all = [['EXPORT_PRE', files.pre], ['KANBAN', files.kan], ['EXPORT_POST', files.post]];
  const bad = all.find(([, l]) => l.some((x) => !x.chk.ok));
  rpa.ap = bad ? 'FAILED' : 'SUCCESS'; rpa.apFile = bad ? bad[0] : null;
  rpa.files = all.filter(([, l]) => l.length).map(([n, l]) => n + ' (' + l.length + ')');
  calls.push(`XD07: ${rpa.files.join(' → ') || 'no file'} → ${rpa.ap}. E-mail ${rpa.g === 'FAILED' || rpa.ap === 'FAILED' ? 'FAILED' : 'SUCCESS'} (one per run)`);
}
// ---------- Add Part (XD01): Period = Current (default) or Next ----------
function addPart(per, p, v, by, opt = {}) {
  M[per] ||= {};
  M[per][p] = { st: 'Candidate', pcs: v.pcs, max: v.max, d: {} };
  calls.push(`INSERT TB_M_PART_CANDIDATE ${p} PERIOD ${per}, PART_STATUS Candidate, Pcs ${v.pcs}, Max ${v.max} (${opt.label || 'Add Part'})`);
  if (opt.next) { M[opt.next][p] = { st: 'Candidate', pcs: v.pcs, max: v.max, d: {} }; calls.push(`XD05 already made ${opt.next} (after day D) → INSERT the same row for ${opt.next}, so the next XD05 run calculates the part`); }
  calls.push(`${p} is Candidate: no staging row (not sent to AP POLE or GTOPAS)`);
}

