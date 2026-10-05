/* Case Consolidation Simulation — pure model.
   Customer orders (a multiple of pcs/case per destination) are packed into
   cases, and one supplier PO is released per day (PO Date = Order Date + 1)
   holding at most Max Case/Day cases. Cases that do not fit wait in a FIFO
   backlog and go into the next PO first. */

export type DestKey = 'VN' | 'JP' | 'TH';

export interface Order {
  id: number;
  no: string;
  date: string;
  dest: DestKey;
  qty: number;
}

/** An order plus its index in the unsorted list (used to pick a stable colour). */
export interface SortedOrder extends Order {
  ci: number;
}

export const DORD: DestKey[] = ['VN', 'JP', 'TH'];

export const DEST: Record<DestKey, { name: string; code: string; c: string }> = {
  VN: { name: 'Vietnam', code: '789', c: 'var(--color-accent)' },
  JP: { name: 'Japan', code: '456', c: 'oklch(0.6 0.1 135)' },
  TH: { name: 'Thailand', code: '123', c: 'oklch(0.7 0.12 70)' },
};

const HUES = [250, 145, 70, 305, 190, 20, 110, 340, 45];
export const colorOf = (i: number) => `oklch(0.6 0.13 ${HUES[i % HUES.length]})`;

const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export const niceD = (iso: string) => {
  const [y, m, d] = iso.split('-');
  return `${d}-${MON[+m - 1]}-${y}`;
};
/** "18-Sep-2026" -> "18-Sep" */
export const shortD = (iso: string) => niceD(iso).slice(0, 6);
export const addDay = (iso: string) => {
  const t = new Date(`${iso}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() + 1);
  return t.toISOString().slice(0, 10);
};
export const caseNo = (n: number) => `50221X${String(n).padStart(2, '0')}`;
export const plural = (n: number, w: string) => `${n} ${w}${n > 1 ? 's' : ''}`;
/** "Order 12" -> "O12" */
export const shortOrder = (o: { no: string }) => `O${o.no.replace(/\D/g, '')}`;

const isoD = (n: number) => `2026-09-${String(n).padStart(2, '0')}`;

const SEED: Order[] = [
  { id: 1, no: 'Order 1', date: '2026-09-15', dest: 'VN', qty: 2 },
  { id: 2, no: 'Order 2', date: '2026-09-15', dest: 'VN', qty: 4 },
  { id: 3, no: 'Order 3', date: '2026-09-15', dest: 'JP', qty: 6 },
  { id: 4, no: 'Order 4', date: '2026-09-16', dest: 'VN', qty: 1 },
  { id: 5, no: 'Order 5', date: '2026-09-16', dest: 'VN', qty: 5 },
  { id: 6, no: 'Order 6', date: '2026-09-16', dest: 'JP', qty: 2 },
  { id: 7, no: 'Order 7', date: '2026-09-16', dest: 'JP', qty: 4 },
  { id: 8, no: 'Order 8', date: '2026-09-16', dest: 'TH', qty: 3 },
  { id: 9, no: 'Order 9', date: '2026-09-16', dest: 'TH', qty: 3 },
  { id: 10, no: 'Order 10', date: '2026-09-17', dest: 'VN', qty: 12 },
  { id: 11, no: 'Order 11', date: '2026-09-17', dest: 'TH', qty: 2 },
  { id: 12, no: 'Order 12', date: '2026-09-17', dest: 'TH', qty: 1 },
  { id: 13, no: 'Order 13', date: '2026-09-17', dest: 'TH', qty: 3 },
];

export type PresetKey = 'a' | 'b';

export interface SimInputs {
  preset: PresetKey;
  orders: Order[];
  /** Per-PO-date Max Case/Day overrides. */
  capOv: Record<string, number>;
  maxC: number;
  pcs: number;
}

interface Preset {
  label: string;
  maxC: number;
  capOv: Record<string, number>;
  orders: Order[];
}

export const PRESETS: Record<PresetKey, Preset> = {
  a: {
    label: '1 destination · 10 days',
    maxC: 2,
    capOv: { [isoD(17)]: 1, [isoD(18)]: 1, [isoD(19)]: 1 },
    orders: Array.from({ length: 10 }, (_, i) => ({ id: i + 1, no: `Order ${i + 1}`, date: isoD(15 + i), dest: 'VN' as const, qty: 12 })),
  },
  b: { label: '3 destinations', maxC: 2, capOv: {}, orders: SEED },
};

export const PRESET_KEYS = Object.keys(PRESETS) as PresetKey[];

export function presetInputs(k: PresetKey): SimInputs {
  const p = PRESETS[k];
  return { preset: k, orders: p.orders.map((o) => ({ ...o })), capOv: { ...p.capOv }, maxC: p.maxC, pcs: 6 };
}

export interface PoCase {
  n: number;
  start: number;
  dest: DestKey;
  od: string;
}

export interface Po {
  no: string;
  date: string;
  cases: PoCase[];
  rel: string;
}

export interface Release {
  no: string;
  t: string;
  cap: number;
  avail: number;
  backlogIn: number;
  freshC: number;
  take: number;
  left: number;
  over: boolean;
  pos: Po[];
}

/** One packed piece, in packing order. `seq[i]` is the i-th pc dropped into a case. */
export interface SeqItem {
  o: SortedOrder;
  po: string;
  poDate: string;
  cn: number;
  rel: string;
  relDate: string;
  dest: DestKey;
}

export interface Model {
  sorted: SortedOrder[];
  releases: Release[];
  seq: SeqItem[];
  rel: number;
  pending: SortedOrder[];
  pendingQty: number;
  poCount: number;
  caseCount: number;
  /** Customer Order Dates that still have something not paired with a PO (waiting cases or loose pcs). */
  openDates: string[];
}

/** All cases of one Customer Order Date. An ASN must hold a whole sequence, never part of it. */
export interface Sequence {
  /** Customer Order Date (ISO). */
  od: string;
  caseNos: string[];
  poNos: string[];
  /** True once every order of this date is paired with a released PO, so an ASN can be created. */
  complete: boolean;
}

interface QueuedCase {
  od: string;
  dest: DestKey;
  pieces: SortedOrder[];
}

export function buildModel({ orders, pcs, maxC, capOv }: Pick<SimInputs, 'orders' | 'pcs' | 'maxC' | 'capOv'>): Model {
  const sorted: SortedOrder[] = orders
    .map((o, ci) => ({ ...o, ci }))
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : DORD.indexOf(a.dest) - DORD.indexOf(b.dest) || a.id - b.id));
  const dates = [...new Set(sorted.map((o) => o.date))];

  // 1. Pack pieces into full cases per (order date, destination); leftovers carry over.
  const queue: QueuedCase[] = [];
  const carry: Partial<Record<DestKey, SortedOrder[]>> = {};
  dates.forEach((d) =>
    DORD.forEach((dc) => {
      const fresh: SortedOrder[] = [];
      sorted
        .filter((o) => o.date === d && o.dest === dc)
        .forEach((o) => {
          for (let i = 0; i < o.qty; i++) fresh.push(o);
        });
      const pool = (carry[dc] ?? []).concat(fresh);
      if (!pool.length) return;
      const nC = Math.floor(pool.length / pcs);
      for (let c = 0; c < nC; c++) queue.push({ od: d, dest: dc, pieces: pool.slice(c * pcs, (c + 1) * pcs) });
      carry[dc] = pool.slice(nC * pcs);
    }),
  );

  // 2. One PO per day (D+1), FIFO, capped at Max Case/Day.
  const releases: Release[] = [];
  const seq: SeqItem[] = [];
  let qi = 0;
  let poN = 0;
  let cN = 0;
  if (dates.length) {
    let t = addDay(dates[0]);
    let n = 0;
    const end = addDay(dates[dates.length - 1]);
    while (t <= end) {
      const cap = capOv[t] ?? maxC;
      const open = queue.slice(qi);
      const avail = open.filter((c) => addDay(c.od) <= t).length;
      const backlogIn = open.filter((c) => addDay(c.od) < t).length;
      const take = Math.min(cap, avail);
      const r: Release = { no: `PO day ${++n}`, t, cap, avail, backlogIn, freshC: avail - backlogIn, take, left: avail - take, over: t in capOv, pos: [] };
      if (take) {
        const po: Po = { no: `PO${++poN}`, date: t, cases: [], rel: r.no };
        for (let j = 0; j < take; j++) {
          const cs = queue[qi++];
          const cn = ++cN;
          po.cases.push({ n: cn, start: seq.length, dest: cs.dest, od: cs.od });
          cs.pieces.forEach((x) => seq.push({ o: x, po: po.no, poDate: t, cn, rel: r.no, relDate: cs.od, dest: cs.dest }));
        }
        r.pos.push(po);
      }
      releases.push(r);
      t = addDay(t);
    }
  }

  const pending = queue
    .slice(qi)
    .flatMap((c) => c.pieces)
    .concat(DORD.flatMap((dc) => carry[dc] ?? []));
  const openDates = [...new Set([...queue.slice(qi).map((c) => c.od), ...pending.map((o) => o.date)])];
  return { sorted, releases, seq, rel: seq.length, pending, pendingQty: pending.length, poCount: poN, caseCount: cN, openDates };
}

/** Group released cases by Customer Order Date, even when that date was split over several POs. */
export function buildSequences({ releases, openDates }: Pick<Model, 'releases' | 'openDates'>): Sequence[] {
  const byDate = new Map<string, Sequence>();
  releases.forEach((r) =>
    r.pos.forEach((po) =>
      po.cases.forEach((c) => {
        const q = byDate.get(c.od) ?? { od: c.od, caseNos: [], poNos: [], complete: !openDates.includes(c.od) };
        q.caseNos.push(caseNo(c.n));
        if (!q.poNos.includes(po.no)) q.poNos.push(po.no);
        byDate.set(c.od, q);
      }),
    ),
  );
  return [...byDate.values()].sort((a, b) => (a.od < b.od ? -1 : 1));
}
