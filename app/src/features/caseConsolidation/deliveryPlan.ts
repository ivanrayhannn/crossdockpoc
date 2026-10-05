import { caseNo, colorOf, DEST, niceD, partNoOf, plural, shortD } from './simulation';
import type { Model, Order, Sequence } from './simulation';

/** Delivery Plan is grouped by Customer Order Date; one date can be spread over several POs. */
export interface DpQuery {
  /** Customer Order Date range. */
  from: string;
  to: string;
  /** Ready to ASN = Complete, Waiting Released = still has orders without a PO. */
  st: 'all' | 'ready' | 'waiting';
}

export const EMPTY_QUERY: DpQuery = { from: '', to: '', st: 'all' };

export interface Hole {
  bg: string;
  lbl: string;
}

export interface DpHeaderRow {
  /** Customer Order Date (ISO), also the selection key. */
  key: string;
  date: string;
  asn: string;
  cases: string;
  /** Every order of this date is paired with a PO (Ready to ASN). */
  complete: boolean;
  /** Every case of this date is already in an ASN. */
  asnLocked: boolean;
}

export interface DpOrderRow {
  color: string;
  /** PO Date. */
  date: string;
  part: string;
  qty: number;
  total: number;
  no: string;
  destination: string;
  od: string;
  /** PO No, or '-' while waiting. */
  po: string;
  /** Case No, or '-' while waiting. */
  caseNo: string;
  /** Not paired with a PO yet, so it has no case. */
  waiting: boolean;
}

export interface DeliveryPlanData {
  header: DpHeaderRow[];
  orderRows: DpOrderRow[];
  /** Selected Customer Order Date, e.g. "15-Sep-2026". */
  selLabel: string;
  /** Selected Customer Order Date (ISO). */
  selOd: string;
  selComplete: boolean;
  selPoNos: string;
  meta: string;
}

interface Args {
  orders: Order[];
  pcs: number;
  model: Model;
  /** `buildSequences(model)`, passed in so it is computed once per model. */
  sequences: Sequence[];
  query: DpQuery;
  sel: string | null;
  asnByCase: Record<string, string>;
}

export function buildDeliveryPlan({ orders, pcs, model, sequences, query: q, sel, asnByCase }: Args): DeliveryPlanData {
  const { releases, seq } = model;
  const allPos = releases.flatMap((r) => r.pos);
  const sequenceByDate = new Map(sequences.map((x) => [x.od, x]));
  const packedQty = new Map<number, number>();
  seq.forEach((x) => packedQty.set(x.o.id, (packedQty.get(x.o.id) ?? 0) + 1));

  // Orders (or parts of orders) that did not make it into any PO.
  const remOrders = orders
    .map((o, ci) => ({ ...o, ci, rem: o.qty - (packedQty.get(o.id) ?? 0) }))
    .filter((o) => o.rem > 0)
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.id - b.id));

  const dates = [...new Set([...orders.map((o) => o.date), ...sequenceByDate.keys()])].sort();
  const entries = dates
    .map((d) => {
      const sq = sequenceByDate.get(d);
      const pos = allPos.filter((po) => po.cases.some((c) => c.od === d));
      const rem = remOrders.filter((o) => o.date === d);
      return { d, sq, pos, rem, remQty: rem.reduce((a, o) => a + o.rem, 0), complete: !!sq?.complete };
    })
    .filter((e) => e.sq || e.remQty);

  const shown = entries.filter(
    (e) =>
      (!q.from || e.d >= q.from) &&
      (!q.to || e.d <= q.to) &&
      (q.st === 'all' || (q.st === 'ready' ? e.complete : !e.complete)),
  );

  const header: DpHeaderRow[] = shown.map((e) => {
    const asns = [...new Set((e.sq?.caseNos ?? []).map((id) => asnByCase[id]).filter(Boolean))];
    const released = e.sq ? `${plural(e.sq.caseNos.length, 'case')} · ${e.sq.caseNos.length * pcs} pcs` : 'no case released';
    return {
      key: e.d,
      date: niceD(e.d),
      asn: asns.join(', ') || '-',
      cases: e.remQty ? `${released} · ${e.remQty} pcs not released` : released,
      complete: e.complete,
      asnLocked: !!e.sq && e.sq.caseNos.every((id) => asnByCase[id]),
    };
  });

  const cur = shown.find((e) => e.d === sel) ?? shown[0];
  if (!cur) {
    return { header, orderRows: [], selLabel: '-', selOd: '', selComplete: false, selPoNos: '-', meta: 'no delivery plan' };
  }

  // Released cases of this order date, in PO order (a date can be split over several POs).
  const cs = cur.pos
    .flatMap((po) => po.cases.filter((c) => c.od === cur.d).map((c) => ({ ...c, po })))
    .map((c) => ({ ...c, pieces: seq.slice(c.start, c.start + pcs) }));

  const orderRows: DpOrderRow[] = [];
  cs.forEach((c) => {
    const runs: { o: (typeof c.pieces)[number]['o']; n: number }[] = [];
    c.pieces.forEach((x) => {
      const l = runs[runs.length - 1];
      if (l && l.o.id === x.o.id) l.n++;
      else runs.push({ o: x.o, n: 1 });
    });
    runs.forEach((r) =>
      orderRows.push({
        color: colorOf(r.o.ci),
        date: niceD(c.po.date),
        part: partNoOf(r.o),
        qty: r.n,
        total: r.o.qty,
        no: r.o.no,
        destination: `${DEST[r.o.dest].name} · ${DEST[r.o.dest].code}`,
        od: shortD(r.o.date),
        po: c.po.no,
        caseNo: caseNo(c.n),
        waiting: false,
      }),
    );
  });
  // Part of this date that has no PO yet.
  cur.rem.forEach((o) =>
    orderRows.push({
      color: colorOf(o.ci),
      date: '-',
      part: partNoOf(o),
      qty: o.rem,
      total: o.qty,
      no: o.no,
      destination: `${DEST[o.dest].name} · ${DEST[o.dest].code}`,
      od: shortD(o.date),
      po: '-',
      caseNo: '-',
      waiting: true,
    }),
  );

  return {
    header,
    orderRows,
    selLabel: niceD(cur.d),
    selOd: cur.d,
    selComplete: cur.complete,
    selPoNos: cur.pos.map((p) => p.no).join(', ') || '-',
    meta: `${plural(cs.length, 'case')} · ${cs.length * pcs} pcs${cur.remQty ? ` · ${cur.remQty} pcs not released` : ''}`,
  };
}
