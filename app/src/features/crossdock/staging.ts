import { num, parseDt } from '../../lib/format';
import type { DestAllocation, Part } from '../../types';

/** One row of TB_H_PART_CANDIDATE_STG_SYNC (22-Nov): every value change of the Kanban / Export Crossdock Master,
 * with the Sync Status of AP POLE and GTOPAS. The RPA reads only this table. */
export interface StgRow {
  id: number;
  p: string;
  n: string;
  per: string;
  ps: 'Active' | 'Inactive';
  lvl: 'KANBAN' | 'EXPORT';
  dest: string;
  ot: string;
  f: 'PCS_CASE' | 'MAX_CASE_DAY' | 'CASE_DAY';
  act: 'ADD' | 'EDIT' | 'DELETE';
  old: number | null;
  nw: number;
  src: 'SCREEN' | 'UPLOAD' | 'BATCH';
  /** 0 Non Sync, 1 Sync, 2 Superseded. */
  ap: 0 | 1 | 2;
  apDt: string | null;
  seq: 1 | 2 | 3 | null;
  apRun: string | null;
  /** null = not for GTOPAS, 0 Non Sync, 1 Sync. */
  gt: 0 | 1 | null;
  gtDt: string | null;
  gtRun: string | null;
  by: string;
  dt: string;
}

export type NewRow = Omit<StgRow, 'id' | 'ap' | 'apDt' | 'seq' | 'apRun' | 'gtDt' | 'gtRun'>;

const destKey = (d: DestAllocation) => `${d.cd || d.d}|${d.ot || '**'}`;

/** Kanban save: one KANBAN row per changed Pcs/Case or Max Case/Day of an Active part; Active -> Inactive: EXPORT DELETE (0) per destination. */
export function kanbanRows(prev: Part | undefined, next: Part, by: string, dt: string, src: NewRow['src'] = 'SCREEN'): NewRow[] {
  const base = { p: next.p, n: next.n, per: next.per, src, by, dt };
  if (!prev || next.st === 'Candidate') return [];
  if (prev.st === 'Active' && next.st === 'Inactive') {
    return prev.dests.filter((d) => num(d.al) > 0).map((d) => ({
      ...base, ps: 'Inactive' as const, lvl: 'EXPORT' as const, dest: d.cd || d.d, ot: d.ot || '**', f: 'CASE_DAY' as const, act: 'DELETE' as const,
      old: num(d.al), nw: 0, gt: 0 as const,
    }));
  }
  if (next.st !== 'Active') return [];
  if (prev.st === 'Candidate') {
    return (['PCS_CASE', 'MAX_CASE_DAY'] as const).map((f) => ({
      ...base, ps: 'Active' as const, lvl: 'KANBAN' as const, dest: '', ot: '', f, act: 'ADD' as const, old: null, nw: num(f === 'PCS_CASE' ? next.pc : next.mc), gt: null,
    }));
  }
  const out: NewRow[] = [];
  for (const [f, a, b] of [['PCS_CASE', prev.pc, next.pc], ['MAX_CASE_DAY', prev.mc, next.mc]] as const) {
    if (num(a) !== num(b)) out.push({ ...base, ps: 'Active', lvl: 'KANBAN', dest: '', ot: '', f, act: 'EDIT', old: num(a), nw: num(b), gt: null });
  }
  return out;
}

/** Export save: one EXPORT row per added / changed / removed destination (GTOPAS 0 for ADD / DELETE). */
export function exportRows(part: Part, prev: DestAllocation[], next: DestAllocation[], by: string, dt: string, src: NewRow['src'] = 'SCREEN'): NewRow[] {
  const base = { p: part.p, n: part.n, per: part.per, ps: 'Active' as const, lvl: 'EXPORT' as const, f: 'CASE_DAY' as const, src, by, dt };
  const a = new Map(prev.map((d) => [destKey(d), num(d.al)]));
  const b = new Map(next.map((d) => [destKey(d), num(d.al)]));
  const out: NewRow[] = [];
  for (const [k, v] of b) {
    const [dest, ot] = k.split('|');
    if (!a.has(k)) out.push({ ...base, dest, ot, act: 'ADD', old: null, nw: v, gt: 0 });
    else if (a.get(k) !== v) out.push({ ...base, dest, ot, act: 'EDIT', old: a.get(k) ?? null, nw: v, gt: null });
  }
  for (const [k, v] of a) {
    const [dest, ot] = k.split('|');
    if (!b.has(k)) out.push({ ...base, dest, ot, act: 'DELETE', old: v, nw: 0, gt: 0 });
  }
  return out;
}

export function addRows(stg: StgRow[], rows: NewRow[]): StgRow[] {
  let id = stg.reduce((m, r) => Math.max(m, r.id), 100);
  return stg.concat(rows.map((r) => ({ ...r, id: ++id, ap: 0, apDt: null, seq: null, apRun: null, gtDt: null, gtRun: null })));
}

export const runIdOf = (d: Date) => {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
};

/** [Sync]: AP POLE rows of the given periods and GTOPAS rows of the Current period are taken (XD01 5.24).
 * Per key: first OLD / last NEW; last row 1 + SEND_SEQ (1 Export before Kanban for a part whose Max goes down, 2 Kanban, 3 Export after),
 * earlier rows 2 Superseded. Returns the new staging and the number of parts sent. */
export function runSync(stg: StgRow[], apPeriods: string[], curPer: string, run: string, at: string): { stg: StgRow[]; parts: number } {
  const next = stg.map((r) => ({ ...r }));
  const pend = next.filter((r) => r.ap === 0 && apPeriods.includes(r.per));
  const groups = new Map<string, StgRow[]>();
  for (const r of pend) {
    const k = [r.per, r.p, r.lvl, r.dest, r.ot, r.f].join('|');
    groups.set(k, [...(groups.get(k) ?? []), r]);
  }
  const maxDown = new Set<string>();
  for (const g of groups.values()) {
    const first = g[0], last = g[g.length - 1];
    if (first.f === 'MAX_CASE_DAY' && first.old != null && last.nw < first.old) maxDown.add(`${first.per}|${first.p}`);
  }
  for (const g of groups.values()) {
    const first = g[0], last = g[g.length - 1];
    const same = last.act !== 'DELETE' && first.old != null && first.old === last.nw;
    for (const r of g) {
      r.ap = r === last ? 1 : 2;
      r.apDt = at;
      r.apRun = run;
    }
    last.seq = same ? null : last.lvl === 'KANBAN' ? 2 : maxDown.has(`${last.per}|${last.p}`) ? 1 : 3;
  }
  for (const r of next) {
    if (r.gt === 0 && r.per === curPer) {
      r.gt = 1;
      r.gtDt = at;
      r.gtRun = run;
    }
  }
  return { stg: next, parts: new Set(pend.map((r) => `${r.per}|${r.p}`)).size };
}

/** [Re-send last Sync]: the same rows go out again with the same run ID (only the send time changes). */
export function resendRun(stg: StgRow[], run: string, at: string): StgRow[] {
  return stg.map((r) => ({ ...r, ...(r.apRun === run ? { apDt: at } : {}), ...(r.gtRun === run ? { gtDt: at } : {}) }));
}

/** Sync Status of a part + period, worked out from the staging. */
export function syncOfPart(stg: StgRow[], p: string, per: string) {
  const rows = stg.filter((r) => r.p === p && r.per === per);
  const latest = (xs: (string | null)[]) => (xs.filter(Boolean) as string[]).sort((a, b) => parseDt(a) - parseDt(b)).pop() ?? null;
  return {
    ap: rows.some((r) => r.ap === 0) ? 0 : rows.length ? 1 : null,
    gt: rows.some((r) => r.gt === 0) ? 0 : rows.some((r) => r.gt === 1) ? 1 : null,
    apDt: latest(rows.map((r) => r.apDt)),
    gtDt: latest(rows.map((r) => r.gtDt)),
  } as { ap: 0 | 1 | null; gt: 0 | 1 | null; apDt: string | null; gtDt: string | null };
}

/** Seed: an earlier run for every part that was sent before, plus the pending rows of the parts shown Non Sync.
 * Past-period rows are all sent (a past period is never taken again). */
export function seedStaging(parts: Part[], curPer: string): StgRow[] {
  const rows: StgRow[] = [];
  let id = 0;
  const push = (r: Omit<StgRow, 'id'>) => rows.push({ ...r, id: ++id });
  const none = { ap: 0, apDt: null, seq: null, apRun: null, gtDt: null, gtRun: null } as const;
  for (const p of parts) {
    if (p.st === 'Candidate') continue;
    const past = p.per !== curPer;
    const sent = p.apSyncDt || p.lastSyncDt || (past ? '28-Aug-2026 10:05' : null);
    const pending = !past && p.syncStatus === 0;
    const ps = p.st === 'Inactive' ? 'Inactive' : 'Active';
    const base = { p: p.p, n: p.n, per: p.per, ps, src: 'BATCH', by: 'XD05BATCH', dt: '27-Aug-2026 02:00' } as const;
    const ok = (seq: 1 | 2 | 3) => (sent ? { ap: 1 as const, apDt: sent, seq, apRun: '20260828100500' } : { ap: 0 as const, apDt: null, seq: null, apRun: null });
    for (const f of ['PCS_CASE', 'MAX_CASE_DAY'] as const) {
      push({ ...base, lvl: 'KANBAN', dest: '', ot: '', f, act: 'ADD', old: null, nw: num(f === 'PCS_CASE' ? p.pc : p.mc), ...ok(2), gt: null, gtDt: null, gtRun: null });
    }
    if (p.st === 'Inactive') {
      // XD05 P2 gives no Export row to an Inactive part; one that was sent and is Non Sync now waits for its EXPORT DELETE (0).
      if (sent && pending) {
        for (const d of p.dests.filter((x) => num(x.al) > 0)) {
          push({ ...base, src: 'SCREEN', by: 'D. Anggraini', dt: '03-Sep-2026 08:30', lvl: 'EXPORT', dest: d.cd || d.d, ot: d.ot || '**', f: 'CASE_DAY', act: 'DELETE', old: num(d.al), nw: 0, ...none, gt: 0 });
        }
      }
      continue;
    }
    for (const d of p.dests) {
      push({ ...base, lvl: 'EXPORT', dest: d.cd || d.d, ot: d.ot || '**', f: 'CASE_DAY', act: 'ADD', old: null, nw: num(d.al), ...ok(3),
        gt: sent ? 1 : 0, gtDt: sent ? (p.lastSyncDt ?? sent) : null, gtRun: sent ? '20260901001000' : null });
    }
    // a sent part shown Non Sync: one change after the last send (Max Case/Day lowered by 1 on the screen)
    if (sent && pending) {
      push({ ...base, src: 'SCREEN', by: 'D. Anggraini', dt: '02-Sep-2026 09:00', lvl: 'KANBAN', dest: '', ot: '', f: 'MAX_CASE_DAY', act: 'EDIT',
        old: num(p.mc) + 1, nw: num(p.mc), ...none, gt: null });
    }
  }
  return rows;
}
