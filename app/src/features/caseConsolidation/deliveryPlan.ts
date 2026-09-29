import { addDay, caseNo, colorOf, DEST, niceD, plural, shortD, shortOrder } from './simulation';
import type { Model, Order, SortedOrder } from './simulation';

export interface DpQuery {
  from: string;
  to: string;
  po: string;
  st: 'all' | 'po' | 'rem';
}

export const EMPTY_QUERY: DpQuery = { from: '', to: '', po: '', st: 'all' };

/** Sentinel selection for the "Not released" header row. */
export const REM_KEY = 'REM';

export interface Hole {
  bg: string;
  lbl: string;
}

export interface DpHeaderRow {
  /** PO number, or REM_KEY for the not-released row. */
  key: string;
  date: string;
  po: string;
  asn: string;
  cases: string;
  remaining: boolean;
}

export interface DpCaseRow {
  /** Variable letter (a, b, c…) used to filter the order table. */
  v: string;
  date: string;
  part: string;
  qty: number;
  po: string;
  caseNo: string;
  holes: Hole[];
  selected: boolean;
  waiting: boolean;
}

export interface DpOrderRow {
  v: string;
  color: string;
  date: string;
  part: string;
  qty: number;
  total: number;
  no: string;
  od: string;
  caseNo: string;
}

export interface DeliveryPlanData {
  header: DpHeaderRow[];
  caseRows: DpCaseRow[];
  orderRows: DpOrderRow[];
  selLabel: string;
  selDate: string;
  meta: string;
  orderMeta: string;
  canClear: boolean;
}

const LETTERS = 'abcdefghijklmnopqrstuvwxyz';

interface Args {
  orders: Order[];
  pcs: number;
  part: string;
  model: Model;
  query: DpQuery;
  sel: string | null;
  variable: string | null;
}

export function buildDeliveryPlan({ orders, pcs, part, model, query: q, sel, variable: vf }: Args): DeliveryPlanData {
  const { releases, seq } = model;
  const pos =
    q.st === 'rem'
      ? []
      : releases
          .filter((r) => r.pos.length)
          .map((r) => r.pos[0])
          .filter((p) => (!q.from || p.date >= q.from) && (!q.to || p.date <= q.to) && (!q.po || p.no.toLowerCase().includes(q.po.trim().toLowerCase())));
  const selPo = pos.find((p) => p.no === sel) ?? pos[0];

  // Orders (or parts of orders) that did not make it into any PO.
  const remOrders = orders
    .map((o, ci) => ({ ...o, ci, rem: o.qty - seq.filter((x) => x.o.id === o.id).length }))
    .filter((o) => o.rem > 0)
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.id - b.id));
  const remQty = q.st === 'po' || q.po ? 0 : remOrders.reduce((a, o) => a + o.rem, 0);
  const isRem = sel === REM_KEY || (!pos.length && remQty > 0);

  const header: DpHeaderRow[] = pos.map((p) => ({
    key: p.no,
    date: niceD(p.date),
    po: p.no,
    asn: '-',
    cases: `${p.cases.length} case · ${p.cases.length * pcs} pcs`,
    remaining: false,
  }));
  if (remQty) {
    header.push({ key: REM_KEY, date: 'Not released', po: '-', asn: '-', cases: `${plural(remOrders.length, 'order')} · ${remQty} pcs remaining`, remaining: true });
  }

  if (isRem && remQty) {
    const groups: Record<string, { list: typeof remOrders }> = {};
    remOrders.forEach((o) => {
      (groups[o.date + o.dest] ??= { list: [] }).list.push(o);
    });
    return {
      header,
      caseRows: Object.values(groups).map((g) => ({
        v: '–',
        date: '-',
        part,
        qty: g.list.reduce((a, o) => a + o.rem, 0),
        po: '-',
        caseNo: 'Waiting',
        holes: g.list.flatMap((o) => Array.from({ length: o.rem }, () => ({ bg: colorOf(o.ci), lbl: shortOrder(o) }))),
        selected: false,
        waiting: true,
      })),
      orderRows: remOrders.map((o) => ({
        v: '–',
        color: colorOf(o.ci),
        date: '-',
        part,
        qty: o.rem,
        total: o.qty,
        no: `${o.no} · ${DEST[o.dest].name}`,
        od: shortD(o.date),
        caseNo: o.rem < o.qty ? 'rest in PO' : '-',
      })),
      selLabel: 'Not released',
      selDate: 'waiting for next PO or manual PO',
      meta: `${remQty} pcs remaining`,
      orderMeta: 'Remaining customer orders',
      canClear: false,
    };
  }

  if (!selPo) {
    return { header, caseRows: [], orderRows: [], selLabel: '-', selDate: '-', meta: 'no PO', orderMeta: '-', canClear: false };
  }

  const total = pcs * selPo.cases.length;
  const cs = selPo.cases.map((c, i) => ({ ...c, v: LETTERS[i % 26], pieces: seq.slice(c.start, c.start + pcs) }));
  const caseRows: DpCaseRow[] = cs.map((c) => ({
    v: c.v,
    date: niceD(selPo.date),
    part,
    qty: pcs,
    po: selPo.no,
    caseNo: caseNo(c.n),
    holes: c.pieces.map((x) => ({ bg: colorOf(x.o.ci), lbl: shortOrder(x.o) })),
    selected: vf === c.v,
    waiting: false,
  }));

  const orderRows: DpOrderRow[] = [];
  cs.filter((c) => !vf || c.v === vf).forEach((c) => {
    const runs: { o: SortedOrder; n: number }[] = [];
    c.pieces.forEach((x) => {
      const l = runs[runs.length - 1];
      if (l && l.o.id === x.o.id) l.n++;
      else runs.push({ o: x.o, n: 1 });
    });
    runs.forEach((r) =>
      orderRows.push({
        v: c.v,
        color: colorOf(r.o.ci),
        date: niceD(selPo.date),
        part,
        qty: r.n,
        total: r.o.qty,
        no: `${r.o.no} · ${DEST[r.o.dest].name}`,
        od: shortD(r.o.date),
        caseNo: caseNo(c.n),
      }),
    );
  });

  const cur = cs.find((c) => c.v === vf);
  return {
    header,
    caseRows,
    orderRows,
    selLabel: selPo.no,
    selDate: niceD(selPo.date),
    meta: `${cs.length} case · ${total} pcs`,
    orderMeta: cur ? `Case ${caseNo(cur.n)} (variable ${cur.v})` : `All cases in ${selPo.no}`,
    canClear: !!vf,
  };
}

/** True when a case was already waiting (backlog) by the time its PO was released. */
export const isBacklog = (od: string, poDate: string) => addDay(od) < poDate;
