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
      .map((g) => (g < placed ? { bg: 'transparent', bd: '#dee2e6' } : { bg: color, bd: color }))
      .concat(Array.from({ length: pn }, () => ({ bg: '#fff3cd', bd: 'var(--warning)' })));
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

/** Bootstrap 4 contextual variant name, used as `badge-{v}`, `text-{v}` or `var(--{v})`. */
export type Variant = 'primary' | 'secondary' | 'success' | 'warning';

export interface ReleaseCase {
  caseNo: string;
  status: string;
  statusClass: string;
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
  splitVariant: Variant;
  pos: ReleasePo[];
}

export function buildReleaseRows(model: Model, placed: number, done: boolean, pcs: number): ReleaseRow[] {
  const { releases, seq } = model;
  return releases.map((r) => ({
    no: r.no,
    date: niceD(r.t),
    calc: `available ${plural(r.avail, 'case')}${r.backlogIn ? ` (backlog ${r.backlogIn} + new ${r.freshC})` : ''} · Max Case/Day ${r.cap}${r.take ? '' : ' · no PO'}`,
    splitText: r.left ? `Backlog ${plural(r.left, 'case')}` : 'No backlog',
    splitVariant: r.left ? 'warning' : 'success',
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
            statusClass: addDay(c.od) < p.date ? 'text-warning-dark' : filled === pcs ? 'text-success' : 'text-muted',
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
  variant: Variant;
}

export function buildKpis(model: Model, pcs: number): KpiTile[] {
  const { sorted, rel, caseCount, poCount, pendingQty } = model;
  const total = sorted.reduce((a, o) => a + o.qty, 0);
  return [
    { k: 'Customer order qty', v: `${total} pcs`, s: `${plural(sorted.length, 'order')} · multiple of ${pcs} per destination`, variant: 'secondary' },
    { k: 'In supplier PO', v: `${rel} pcs`, s: `${plural(caseCount, 'case')} · FIFO`, variant: 'success' },
    { k: 'Supplier PO', v: `${poCount} PO`, s: '1 PO per day · D+1', variant: 'primary' },
    {
      k: 'Remaining',
      v: `${pendingQty} pcs`,
      s: pendingQty ? `${plural(Math.ceil(pendingQty / pcs), 'case')} · next PO or manual PO` : 'all orders in a PO',
      variant: 'warning',
    },
  ];
}

export interface AllocRow {
  /** First row of a PO — drawn with a heavier top rule. */
  groupStart: boolean;
  rel: string;
  po: string;
  poDate: string;
  poQty: string;
  caseNo: string;
  caseClass: string;
  part: string;
  no: string;
  date: string;
  qty: number;
  color: string;
  rowClass: string;
  note: string;
  noteClass: string;
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
            groupStart: poFirst,
            rel: relFirst ? r.no : '',
            po: poFirst ? p.no : '',
            poDate: poFirst ? niceD(p.date) : '',
            poQty: poFirst ? `${p.cases.length * pcs} pcs` : '',
            caseNo: i === 0 ? caseNo(c.n) : '',
            caseClass: 'text-primary',
            part,
            no: x.o.no,
            date: niceD(x.o.date),
            qty: x.n,
            color: colorOf(x.o.ci),
            rowClass: '',
            note: x.n !== x.o.qty ? `${x.n} of ${x.o.qty} pcs${posOf.length > 1 ? ` · order spans ${posOf.join(' + ')}` : ''}` : '',
            noteClass: posOf.length > 1 ? 'text-primary' : 'text-muted',
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
        groupStart: i === 0,
        rel: i === 0 ? '—' : '',
        po: i === 0 ? 'Not released' : '',
        poDate: '',
        poQty: '',
        caseNo: '',
        caseClass: 'text-warning-dark',
        part,
        no: o.no,
        date: niceD(o.date),
        qty: pn,
        color: colorOf(o.ci),
        rowClass: 'table-warning',
        note: `Remaining ${pn} of ${o.qty} pcs · waits for the next PO or a manual PO`,
        noteClass: 'text-warning-dark',
      });
    });
  }
  return rows;
}
