import { addDay, buildSequences, caseNo, colorOf, DEST, niceD, shortD, shortOrder } from './simulation';
import type { Model, Order } from './simulation';

/** Delivery Plan is grouped by Customer Order Date; one date can be spread over several POs. */
export interface DpQuery {
  /** Customer Order Date range. */
  from: string;
  to: string;
  po: string;
  st: 'all' | 'complete' | 'view';
}

export const EMPTY_QUERY: DpQuery = { from: '', to: '', po: '', st: 'all' };

export interface Hole {
  bg: string;
  lbl: string;
}

export interface DpPoTag {
  no: string;
  /** PO Date (= Customer Order Date + 1 for the first PO, later for backlog). */
  date: string;
}

export interface DpHeaderRow {
  /** Customer Order Date (ISO), also the selection key. */
  key: string;
  date: string;
  pos: DpPoTag[];
  asn: string;
  cases: string;
  /** Every order of this date is paired with a PO, so an ASN can be created. */
  complete: boolean;
}

export interface DpCaseRow {
  /** Variable letter (a, b, c…) used to filter the order table. */
  v: string;
  /** PO Date. */
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
  /** PO Date. */
  date: string;
  part: string;
  qty: number;
  total: number;
  no: string;
  destination: string;
  od: string;
  caseNo: string;
}

export interface DeliveryPlanData {
  header: DpHeaderRow[];
  caseRows: DpCaseRow[];
  orderRows: DpOrderRow[];
  /** Selected Customer Order Date, e.g. "15-Sep-2026". */
  selLabel: string;
  /** Selected Customer Order Date (ISO). */
  selOd: string;
  selComplete: boolean;
  selPoNos: string;
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
  asnByCase: Record<string, string>;
}

export function buildDeliveryPlan({ orders, pcs, part, model, query: q, sel, variable: vf, asnByCase }: Args): DeliveryPlanData {
  const { releases, seq } = model;
  const sequences = buildSequences(model);
  const allPos = releases.flatMap((r) => r.pos);

  // Orders (or parts of orders) that did not make it into any PO.
  const remOrders = orders
    .map((o, ci) => ({ ...o, ci, rem: o.qty - seq.filter((x) => x.o.id === o.id).length }))
    .filter((o) => o.rem > 0)
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.id - b.id));

  const dates = [...new Set([...orders.map((o) => o.date), ...sequences.map((s) => s.od)])].sort();
  const entries = dates
    .map((d) => {
      const sq = sequences.find((x) => x.od === d);
      const pos = allPos.filter((po) => po.cases.some((c) => c.od === d));
      const rem = remOrders.filter((o) => o.date === d);
      return { d, sq, pos, rem, remQty: rem.reduce((a, o) => a + o.rem, 0), complete: !!sq?.complete };
    })
    .filter((e) => e.sq || e.remQty);

  const shown = entries.filter(
    (e) =>
      (!q.from || e.d >= q.from) &&
      (!q.to || e.d <= q.to) &&
      (!q.po || e.pos.some((p) => p.no.toLowerCase().includes(q.po.trim().toLowerCase()))) &&
      (q.st === 'all' || (q.st === 'complete' ? e.complete : !e.complete)),
  );

  const header: DpHeaderRow[] = shown.map((e) => {
    const asns = [...new Set((e.sq?.caseNos ?? []).map((id) => asnByCase[id]).filter(Boolean))];
    const released = e.sq ? `${e.sq.caseNos.length} case · ${e.sq.caseNos.length * pcs} pcs` : 'no case released';
    return {
      key: e.d,
      date: niceD(e.d),
      pos: e.pos.map((p) => ({ no: p.no, date: shortD(p.date) })),
      asn: asns.join(', ') || '-',
      cases: e.remQty ? `${released} · ${e.remQty} pcs not released` : released,
      complete: e.complete,
    };
  });

  const cur = shown.find((e) => e.d === sel) ?? shown[0];
  if (!cur) {
    return { header, caseRows: [], orderRows: [], selLabel: '-', selOd: '', selComplete: false, selPoNos: '-', meta: 'no delivery plan', orderMeta: '-', canClear: false };
  }

  // Released cases of this order date, in PO order (a date can be split over several POs).
  const cs = cur.pos
    .flatMap((po) => po.cases.filter((c) => c.od === cur.d).map((c) => ({ ...c, po })))
    .map((c, i) => ({ ...c, v: LETTERS[i % 26], pieces: seq.slice(c.start, c.start + pcs) }));

  const caseRows: DpCaseRow[] = cs.map((c) => ({
    v: c.v,
    date: niceD(c.po.date),
    part,
    qty: pcs,
    po: c.po.no,
    caseNo: caseNo(c.n),
    holes: c.pieces.map((x) => ({ bg: colorOf(x.o.ci), lbl: shortOrder(x.o) })),
    selected: vf === c.v,
    waiting: false,
  }));

  // Part of this date that has no PO yet: shown as waiting rows, grouped by destination.
  const groups: Record<string, typeof cur.rem> = {};
  cur.rem.forEach((o) => (groups[o.dest] ??= []).push(o));
  Object.values(groups).forEach((list) =>
    caseRows.push({
      v: '–',
      date: '-',
      part,
      qty: list.reduce((a, o) => a + o.rem, 0),
      po: '-',
      caseNo: 'Waiting',
      holes: list.flatMap((o) => Array.from({ length: o.rem }, () => ({ bg: colorOf(o.ci), lbl: shortOrder(o) }))),
      selected: false,
      waiting: true,
    }),
  );

  const orderRows: DpOrderRow[] = [];
  cs.filter((c) => !vf || c.v === vf).forEach((c) => {
    const runs: { o: (typeof c.pieces)[number]['o']; n: number }[] = [];
    c.pieces.forEach((x) => {
      const l = runs[runs.length - 1];
      if (l && l.o.id === x.o.id) l.n++;
      else runs.push({ o: x.o, n: 1 });
    });
    runs.forEach((r) =>
      orderRows.push({
        v: c.v,
        color: colorOf(r.o.ci),
        date: niceD(c.po.date),
        part,
        qty: r.n,
        total: r.o.qty,
        no: r.o.no,
        destination: `${DEST[r.o.dest].name} · ${DEST[r.o.dest].code}`,
        od: shortD(r.o.date),
        caseNo: caseNo(c.n),
      }),
    );
  });
  if (!vf) {
    cur.rem.forEach((o) =>
      orderRows.push({
        v: '–',
        color: colorOf(o.ci),
        date: '-',
        part,
        qty: o.rem,
        total: o.qty,
        no: o.no,
        destination: `${DEST[o.dest].name} · ${DEST[o.dest].code}`,
        od: shortD(o.date),
        caseNo: o.rem < o.qty ? 'rest in PO' : 'Waiting',
      }),
    );
  }

  const sel_ = cs.find((c) => c.v === vf);
  return {
    header,
    caseRows,
    orderRows,
    selLabel: niceD(cur.d),
    selOd: cur.d,
    selComplete: cur.complete,
    selPoNos: cur.pos.map((p) => p.no).join(', ') || '-',
    meta: `${cs.length} case · ${cs.length * pcs} pcs${cur.remQty ? ` · ${cur.remQty} pcs not released` : ''}`,
    orderMeta: sel_ ? `Case ${caseNo(sel_.n)} (variable ${sel_.v})` : `All cases of ${niceD(cur.d)}`,
    canClear: !!vf,
  };
}

/** True when a case was already waiting (backlog) by the time its PO was released. */
export const isBacklog = (od: string, poDate: string) => addDay(od) < poDate;
