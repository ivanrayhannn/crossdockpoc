/* View-model builders for the "Visual simulation" tab: the customer-orders
   panel, the daily PO / case-packing panel, KPI tiles, and the flat
   allocation-result table. Kept separate from simulation.ts (the pure
   packing/release model) so the components stay thin. */

import { addDay, caseNo, colorOf, DEST, niceD, plural, shortD, shortOrder } from './simulation';
import type { Model, SeqItem, SortedOrder } from './simulation';

export interface Dot {
  bg: string;
  bd: string;
}

export interface OrderRow {
  id: number;
  no: string;
  date: string;
  qty: number;
  color: string;
  dots: Dot[];
  note: string;
  active: boolean;
  isPending: boolean;
}

export function buildOrderRows(model: Model, placed: number, done: boolean): OrderRow[] {
  const { sorted, seq, pending } = model;
  const next = seq[placed];
  return sorted.map((o) => {
    const idx: number[] = [];
    seq.forEach((x, g) => {
      if (x.o.id === o.id) idx.push(g);
    });
    const moved = idx.filter((g) => g < placed).length;
    const posSet = [...new Set(seq.filter((x) => x.o.id === o.id).map((x) => x.po))];
    const relSet = [...new Set(seq.filter((x) => x.o.id === o.id).map((x) => x.rel))];
    const pn = pending.filter((x) => x.id === o.id).length;
    const active = !done && next?.o.id === o.id;
    const color = colorOf(o.ci);
    const dots: Dot[] = idx
      .map((g) => (g < placed ? { bg: 'transparent', bd: 'var(--color-neutral-300)' } : { bg: color, bd: color }))
      .concat(Array.from({ length: pn }, () => ({ bg: 'oklch(0.97 0.03 80)', bd: 'oklch(0.72 0.12 70)' })));
    let note = idx.length ? `${relSet.join('+')} → ${posSet.join(' + ')}` : '';
    if (!done && moved && moved < idx.length) note = `${moved}/${idx.length} packed`;
    if (pn) note = `${note ? `${note} · ` : ''}${pn} remaining`;
    return { id: o.id, no: `${o.no} · ${o.dest}`, date: o.date, qty: o.qty, color, dots, note, active, isPending: pn > 0 };
  });
}

export interface CaseHole {
  bg: string;
  shadow: string;
  lbl: string;
  scale: number;
}

export interface ReleaseCase {
  caseNo: string;
  status: string;
  statusFg: string;
  holes: CaseHole[];
}

export interface ReleasePo {
  no: string;
  date: string;
  qty: string;
  orders: string;
  cases: ReleaseCase[];
}

export interface ReleaseRow {
  no: string;
  date: string;
  calc: string;
  splitText: string;
  splitBg: string;
  splitFg: string;
  pos: ReleasePo[];
}

export function buildReleaseRows(model: Model, placed: number, done: boolean, pcs: number): ReleaseRow[] {
  const { releases, seq } = model;
  return releases.map((r) => ({
    no: r.no,
    date: niceD(r.t),
    calc: `available ${plural(r.avail, 'case')}${r.backlogIn ? ` (backlog ${r.backlogIn} + new ${r.freshC})` : ''} · Max Case/Day ${r.cap}${r.take ? '' : ' · no PO'}`,
    splitText: r.left ? `Backlog ${plural(r.left, 'case')}` : 'No backlog',
    splitBg: r.left ? 'oklch(0.95 0.05 80)' : 'var(--color-accent-2-200)',
    splitFg: r.left ? 'oklch(0.42 0.1 65)' : 'var(--color-accent-2-800)',
    pos: r.pos.map((p) => {
      const ords = [...new Set(p.cases.flatMap((c) => seq.slice(c.start, c.start + pcs).map((x) => x.o.no)))];
      return {
        no: p.no,
        date: niceD(p.date),
        qty: `${p.cases.length * pcs} pcs · ${plural(p.cases.length, 'case')}`,
        orders: ords.join(', '),
        cases: p.cases.map((c) => {
          const filled = Math.max(0, Math.min(pcs, placed - c.start));
          return {
            caseNo: caseNo(c.n),
            status: `${DEST[c.dest].name} · ${shortD(c.od)}`,
            statusFg: addDay(c.od) < p.date ? 'oklch(0.45 0.11 65)' : filled === pcs ? 'var(--color-accent-2-800)' : 'var(--color-neutral-600)',
            holes: Array.from({ length: pcs }, (_, j) => {
              const g = c.start + j;
              const on = g < placed;
              const o = seq[g].o;
              return {
                bg: on ? colorOf(o.ci) : '#d6ccbd',
                shadow: on ? '0 2px 3px rgba(0,0,0,.25)' : 'inset 0 2px 4px rgba(80,50,20,.35)',
                lbl: on ? shortOrder(o) : '',
                scale: on && g === placed - 1 && !done ? 1.12 : 1,
              };
            }),
          };
        }),
      };
    }),
  }));
}

export interface WaitingInfo {
  show: boolean;
  dots: { bg: string; lbl: string }[];
  text: string;
}

export function buildWaiting(model: Model): WaitingInfo {
  const { pending } = model;
  const byId = new Map<number, SortedOrder>();
  pending.forEach((o) => byId.set(o.id, o));
  const pendOrders = [...byId.values()];
  return {
    show: pending.length > 0,
    dots: pending.map((o) => ({ bg: colorOf(o.ci), lbl: shortOrder(o) })),
    text: `${pendOrders.map((o) => `${o.no} ${pending.filter((x) => x.id === o.id).length} pcs`).join(', ')} remaining · waits for the next PO or a manual PO`,
  };
}

export interface KpiTile {
  k: string;
  v: string;
  s: string;
  c: string;
}

export function buildKpis(model: Model, pcs: number): KpiTile[] {
  const { sorted, rel, caseCount, poCount, pendingQty } = model;
  const total = sorted.reduce((a, o) => a + o.qty, 0);
  return [
    { k: 'Customer order qty', v: `${total} pcs`, s: `${plural(sorted.length, 'order')} · multiple of ${pcs} per destination`, c: 'var(--color-neutral-400)' },
    { k: 'In supplier PO', v: `${rel} pcs`, s: `${plural(caseCount, 'case')} · FIFO`, c: 'var(--color-accent-2-300)' },
    { k: 'Supplier PO', v: `${poCount} PO`, s: '1 PO per day · D+1', c: 'var(--color-accent)' },
    {
      k: 'Remaining',
      v: `${pendingQty} pcs`,
      s: pendingQty ? `${plural(Math.ceil(pendingQty / pcs), 'case')} · next PO or manual PO` : 'all orders in a PO',
      c: 'oklch(0.8 0.1 75)',
    },
  ];
}

export interface AllocRow {
  topBd: string;
  rel: string;
  po: string;
  poDate: string;
  poQty: string;
  caseNo: string;
  caseFg: string;
  part: string;
  no: string;
  date: string;
  qty: number;
  color: string;
  bg: string;
  note: string;
  noteFg: string;
}

export function buildAllocationRows(model: Model, placed: number, done: boolean, part: string, pcs: number): AllocRow[] {
  const { releases, seq, pending } = model;
  const rows: AllocRow[] = [];
  releases.forEach((r) => {
    r.pos.forEach((p, pi) => {
      p.cases.forEach((c, ci) => {
        const cap = Math.min(placed, c.start + pcs);
        const runs: { o: SeqItem['o']; n: number }[] = [];
        for (let g = c.start; g < cap; g++) {
          const o = seq[g].o;
          const last = runs[runs.length - 1];
          if (last && last.o.id === o.id) last.n++;
          else runs.push({ o, n: 1 });
        }
        runs.forEach((x, i) => {
          const posOf = [...new Set(seq.filter((q) => q.o.id === x.o.id).map((q) => q.po))];
          const poFirst = i === 0 && ci === 0;
          const relFirst = poFirst && pi === 0;
          rows.push({
            topBd: poFirst ? '2px solid var(--color-neutral-400)' : '0',
            rel: relFirst ? r.no : '',
            po: poFirst ? p.no : '',
            poDate: poFirst ? niceD(p.date) : '',
            poQty: poFirst ? `${p.cases.length * pcs} pcs` : '',
            caseNo: i === 0 ? caseNo(c.n) : '',
            caseFg: 'var(--color-accent-800)',
            part,
            no: x.o.no,
            date: niceD(x.o.date),
            qty: x.n,
            color: colorOf(x.o.ci),
            bg: 'var(--color-neutral-100)',
            note: x.n !== x.o.qty ? `${x.n} of ${x.o.qty} pcs${posOf.length > 1 ? ` · order spans ${posOf.join(' + ')}` : ''}` : '',
            noteFg: posOf.length > 1 ? 'var(--color-accent-700)' : 'var(--color-neutral-600)',
          });
        });
      });
    });
  });
  if (done && pending.length) {
    const byId = new Map<number, SortedOrder>();
    pending.forEach((o) => byId.set(o.id, o));
    [...byId.values()].forEach((o, i) => {
      const pn = pending.filter((x) => x.id === o.id).length;
      rows.push({
        topBd: i === 0 ? '2px solid var(--color-neutral-400)' : '0',
        rel: i === 0 ? '—' : '',
        po: i === 0 ? 'Not released' : '',
        poDate: '',
        poQty: '',
        caseNo: '',
        caseFg: 'oklch(0.45 0.11 65)',
        part,
        no: o.no,
        date: niceD(o.date),
        qty: pn,
        color: colorOf(o.ci),
        bg: 'oklch(0.985 0.015 80)',
        note: `Remaining ${pn} of ${o.qty} pcs · waits for the next PO or a manual PO`,
        noteFg: 'oklch(0.45 0.11 65)',
      });
    });
  }
  return rows;
}
