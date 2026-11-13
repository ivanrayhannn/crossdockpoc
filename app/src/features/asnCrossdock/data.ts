/* ASN Crossdock — mock data and the Search pre-mapping of XD09 (decided 21-Oct):
   - the open qty of the customer order lines (H0253, order status 7, Hold Flag N) is read in the H0253 order
     (Allocation Priority = Customer Order Date, Customer Code, Customer Order No, Order Date, Order Time, Destination, Detailed Item No, Serial No);
   - per unit (Part Number + Customer Order Date, oldest date first) the released POs are given in PO date order;
   - the pcs are cut into supplier cases of pcs/case (a case can hold several lines and destinations);
   - an ASN may stop only after a case where every destination of the unit is a multiple of pcs/case (CUT_FLAG Y), because the
     warehouse packs 1 case = 1 destination; a case is Ready when it and every earlier case have a released PO. */

export const PCS_PER_CASE = 6;
export interface Supplier {
  code: string;
  plant: string;
  name: string;
}

/** Supplier Code + Supplier Plant; one ASN is always for one of them (existing rule). */
export const SUPPLIERS: Record<string, Supplier> = {
  '5001-1': { code: '5001', plant: '1', name: 'PT Dummy Supplier Indonesia' },
  '5002-1': { code: '5002', plant: '1', name: 'PT Contoh Komponen' },
};

/** Supplier of the login user in the supplier view (the D/S team sees every supplier). */
export const LOGIN_SUPPLIER = '5001-1';

export interface Dest {
  code: string;
  short: string;
  name: string;
}

/** 7-digit destination code (TB_M_H0125_DESTINATION.DESTINATION_CD). */
export const DESTS: Record<string, Dest> = {
  '9715310': { code: '9715310', short: 'KR', name: 'Korea' },
  '9811110': { code: '9811110', short: 'TW', name: 'Taiwan' },
  '9722D10': { code: '9722D10', short: 'JP', name: 'Japan' },
  '982220': { code: '982220', short: 'AU', name: 'Australia' },
};

/** A customer order line of H0253 (order status 7); on a slice of #TEMP_INSTRUCTION the PO fields are filled and qty is the slice qty. */
export interface InstrLine {
  id: string;
  custCd: string;
  custOrderNo: string;
  /** Customer Order Date (ISO) = Allocation Priority. */
  orderDt: string;
  orderTime: string;
  destCd: string;
  detailedItemNo: string;
  serialNo: string;
  partNo: string;
  qty: number;
  /** Supplier PO of the slice; null while not assigned. */
  poNo: string | null;
  /** Release date of the PO (ISO). */
  poDate: string | null;
  manifestNo: string | null;
  manifestItemNo: string | null;
  /** Supplier Code + Plant key of SUPPLIERS. */
  supplier: string;
  /** Change in G-System written to UPD_STATUS by XD08 on date (a line with UPD_STATUS is not taken by XD09). */
  upd?: { status: '2' | '6'; date: string };
}

export const PART_NAME: Record<string, string> = {
  'PART-X': 'Dummy Part X',
  'PART-D': 'Dummy Part D',
};

/** Supplier of each part (PO supplier of the Pra Daily Order). */
export const PART_SUPPLIER: Record<string, string> = { 'PART-X': '5001-1', 'PART-D': '5002-1' };

const VN = '9715310';
const PH = '9811110';
const TH = '9722D10';
const D4 = '982220';
/** Customer code per destination (order key 2), as in simulasi_asn_rev.xlsx. */
const CUST: Record<string, string> = { [VN]: '9715300', [TH]: '9722D10', [PH]: '9811100', [D4]: '982200' };

type Raw = [order: string, dest: string, qty: number, upd?: { status: '2' | '6'; date: string }];

function lines(orderDt: string, partNo: string, raw: Raw[]): InstrLine[] {
  return raw.map(([order, dest, qty, upd]) => ({
    id: `${partNo}|${orderDt}|${order}|001`,
    custCd: CUST[dest],
    custOrderNo: order,
    orderDt,
    orderTime: '080000',
    destCd: dest,
    detailedItemNo: '001',
    serialNo: '0000001',
    partNo,
    qty,
    poNo: null,
    poDate: null,
    manifestNo: null,
    manifestItemNo: null,
    supplier: PART_SUPPLIER[partNo],
    upd,
  }));
}

/** H0253 lines = simulasi_asn_rev.xlsx (PART-X, 6 pcs/case). A line is replicated by XD08 the day after its Customer Order Date.
 * - 15-Oct CO-14101 VN 6 (ASN0001), CO-14102 TH 6 (hold, cancelled 17-Oct).
 * - 16-Oct CO-14103 TH 6 (ASN0002). 17-Oct: 4 destinations, 30 pcs, PO 18 (short) + split PO 12; CO-14104 cancelled 19-Oct after ASN0003.
 * - 18-Oct: 3 destinations (ASN0005). 19-Oct: CO-14111 TH 6 (received without ASN 21-Oct), CO-14115 VN 12 (ASN0006 + ASN0007).
 * PART-D of a second supplier is not in the workbook: it only shows the rule one ASN = one Supplier Code + Plant (D/S team). */
export const H0253: InstrLine[] = [
  ...lines('2026-10-15', 'PART-X', [['CO-14101', VN, 6], ['CO-14102', TH, 6, { status: '2', date: '2026-10-17' }]]),
  ...lines('2026-10-16', 'PART-X', [['CO-14103', TH, 6]]),
  ...lines('2026-10-17', 'PART-X', [['CO-14104', TH, 6, { status: '2', date: '2026-10-19' }], ['CO-14105', VN, 6], ['CO-14106', VN, 3],
    ['CO-14107', VN, 3], ['CO-14109', PH, 6], ['CO-14110', D4, 6]]),
  ...lines('2026-10-18', 'PART-X', [['CO-14112', VN, 6], ['CO-14113', PH, 6], ['CO-14114', D4, 6]]),
  ...lines('2026-10-19', 'PART-X', [['CO-14111', TH, 6, { status: '6', date: '2026-10-21' }], ['CO-14115', VN, 12]]),
  ...lines('2026-10-17', 'PART-D', [['CO-13007', VN, 6], ['CO-13008', TH, 4], ['CO-13009', TH, 2]]),
];

/** Hold Flag Y set by the D/S team before the first Search (CO-14102, 16-Oct). */
export const HOLD_INIT: Record<string, boolean> = { 'PART-X|2026-10-15|CO-14102|001': true };

/** Crossdock PO part of the Pra Daily Order (manifest with CROSS_DOCK_FLAG = 'X'); released on poDate.
 * Business logic: one PO per Part Number per Customer Order Date, PO date = order date + 1, qty = total order qty of all destinations;
 * a lower qty is an abnormality and the rest comes in a split PO later. */
export interface Po {
  poNo: string;
  manifestNo: string;
  manifestItemNo: string;
  partNo: string;
  qty: number;
  poDate: string;
  /** Customer Order Date the PO is for. */
  orderDt: string;
  /** Split PO: the rest of a short PO. */
  split?: boolean;
}

/** PO of simulasi_asn_rev.xlsx: one PO per Customer Order Date, PO date = order date + 1; PO-0004 = split PO of 17-Oct (PO-0003 18 < 30). */
export const POS: Po[] = [
  { poNo: 'PO-0001', manifestNo: 'MF-0001', manifestItemNo: '0001', partNo: 'PART-X', qty: 12, poDate: '2026-10-16', orderDt: '2026-10-15' },
  { poNo: 'PO-0002', manifestNo: 'MF-0002', manifestItemNo: '0001', partNo: 'PART-X', qty: 6, poDate: '2026-10-17', orderDt: '2026-10-16' },
  { poNo: 'PO-0003', manifestNo: 'MF-0003', manifestItemNo: '0001', partNo: 'PART-X', qty: 18, poDate: '2026-10-18', orderDt: '2026-10-17' },
  { poNo: 'PO-0004', manifestNo: 'MF-0004', manifestItemNo: '0001', partNo: 'PART-X', qty: 12, poDate: '2026-10-19', orderDt: '2026-10-17', split: true },
  { poNo: 'PO-0005', manifestNo: 'MF-0005', manifestItemNo: '0001', partNo: 'PART-X', qty: 18, poDate: '2026-10-19', orderDt: '2026-10-18' },
  { poNo: 'PO-0006', manifestNo: 'MF-0006', manifestItemNo: '0001', partNo: 'PART-X', qty: 18, poDate: '2026-10-20', orderDt: '2026-10-19' },
  { poNo: 'PO-0007', manifestNo: 'MF-0007', manifestItemNo: '0001', partNo: 'PART-D', qty: 12, poDate: '2026-10-18', orderDt: '2026-10-17' },
];

export const BUSINESS_DATES = ['2026-10-16', '2026-10-17', '2026-10-18', '2026-10-19', '2026-10-20', '2026-10-21', '2026-10-22'];

const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export function niceDate(iso: string | null): string {
  if (!iso) return '—';
  const [y, m, d] = iso.split('-');
  return `${d}-${MON[Number(m) - 1]}-${y}`;
}
export function addDays(iso: string, n: number): string {
  const t = new Date(`${iso}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() + n);
  return t.toISOString().slice(0, 10);
}

/** H0253 order key: Allocation Priority (= Customer Order Date), then the PK columns of the replicate. */
function scanKey(l: InstrLine): string {
  return [l.orderDt, l.custCd, l.custOrderNo, l.orderDt, l.orderTime, l.destCd, l.detailedItemNo, l.serialNo].join('|');
}

/** A supplier case of a unit: PCS_PER_CASE pcs in H0253 order. */
export interface UnitCase {
  seq: number;
  lines: InstrLine[];
  qty: number;
  /** CUT_FLAG: the ASN may stop after this case (every destination of the unit a multiple of pcs/case). */
  cut: boolean;
  /** Case Group (GROUP_SEQ): the cases up to a CUT_FLAG Y; the cases of a group are always sent together. */
  group: number;
  /** This case and every earlier case have a released PO. */
  ready: boolean;
  /** Destinations that would not close their warehouse case if the ASN stopped here. */
  openDests: string[];
  /** Has a PO but is not Ready because of a held case (this one or an earlier one of the unit). */
  heldByReduce: boolean;
  /** Ticked Hold (D/S): a saved case hold resolves to this case. */
  held: boolean;
}

/** Saved hold of a case (TB_R_CROSSDOCK_CASE_HOLD): case number and its first customer order line when saved. */
export interface CaseHoldRow { seq: number; destCd: string; custOrderNo: string }

/** FB-182: the case lines move when an order is cancelled or cases are sent, so a hold is matched again at each Search:
 * 1) the case that still has the same Customer Order No + Destination; 2) else the case of the same Destination nearest to the saved
 * case number (lower one on a tie); 3) else (destination gone) the case now at the saved case number, or the last case. */
export function resolveCaseHold(cases: UnitCase[], rows: CaseHoldRow[]): number[] {
  if (!cases.length) return [];
  return rows.map((r) => {
    const own = cases.find((c) => c.lines.some((l) => l.custOrderNo === r.custOrderNo && l.destCd === r.destCd));
    if (own) return own.seq;
    const same = cases.filter((c) => c.lines.some((l) => l.destCd === r.destCd));
    if (same.length) return same.reduce((a, c) => (Math.abs(c.seq - r.seq) < Math.abs(a.seq - r.seq) ? c : a)).seq;
    return Math.min(r.seq, cases.length);
  });
}

export type UnitStatus = 'ready' | 'partial' | 'notReady' | 'created' | 'hold';

export interface Unit {
  /** Part Number + Customer Order Date. */
  key: string;
  partNo: string;
  /** Supplier Code + Plant key of SUPPLIERS. */
  supplier: string;
  orderDt: string;
  /** Open order lines in H0253 order (Hold Flag = N, qty = open qty). */
  lines: InstrLine[];
  /** Order lines put on hold by the D/S team (Hold Flag = Y); shown in the D/S detail only. */
  heldLines: InstrLine[];
  /** Open qty of the unit. */
  qty: number;
  cases: UnitCase[];
  caseCount: number;
  /** PO Readiness: Ready cases (after Reduce PO Readiness). */
  readyCases: number;
  /** Ready cases before the reduction (cases 1..n with a PO). */
  rawReadyCases: number;
  /** Cases held by the D/S team (Hold check box per case, incl. the later cases of the same block onwards). */
  reduce: number;
  /** The Part Number of the unit is on hold by the D/S team (every Customer Order Date). */
  unitHold: boolean;
  /** Cases the user may end the selection on (CUT_FLAG Y and Ready). */
  validEnds: number[];
  /** Some qty of the unit is already in a submitted ASN. */
  sent: boolean;
  status: UnitStatus;
  /** PO check of the Customer Order Date (business logic 1-2). */
  poCheck: PoCheck;
}

export interface PoCheck {
  /** Total customer order qty of all destinations. */
  orderQty: number;
  /** Expected PO date (order date + 1). */
  due: string;
  /** Regular PO of the order date, released by the business date (null = not released yet). */
  regular: Po | null;
  /** Split POs released by the business date. */
  splits: Po[];
  /** Regular PO qty < order qty (abnormality). */
  short: boolean;
  /** Qty still without a released PO. */
  missing: number;
}

export function unitKey(partNo: string, orderDt: string): string {
  return `${partNo}|${orderDt}`;
}

const STATUS_ORDER: Record<UnitStatus, number> = { ready: 0, partial: 1, notReady: 2, hold: 3, created: 4 };

/** Cuts the open qty of one unit (lines in H0253 order) into supplier cases, taking the PO qty in order (pos are reduced in place). */
function cutCases(ls: InstrLine[], pos: { po: Po; open: number }[]): UnitCase[] {
  const slices: InstrLine[][] = [];
  let cur: InstrLine[] = [];
  let room = PCS_PER_CASE;
  for (const l of ls) {
    let left = l.qty;
    while (left > 0) {
      const p = pos.find((x) => x.open > 0);
      const q = Math.min(left, room, p ? p.open : left);
      if (p) p.open -= q;
      cur.push({ ...l, qty: q, poNo: p?.po.poNo ?? null, poDate: p?.po.poDate ?? null, manifestNo: p?.po.manifestNo ?? null, manifestItemNo: p?.po.manifestItemNo ?? null });
      left -= q;
      room -= q;
      if (room === 0) {
        slices.push(cur);
        cur = [];
        room = PCS_PER_CASE;
      }
    }
  }
  if (cur.length) slices.push(cur);
  const cum: Record<string, number> = {};
  let ready = true;
  let group = 1;
  return slices.map((c, i) => {
    c.forEach((s) => (cum[s.destCd] = (cum[s.destCd] ?? 0) + s.qty));
    ready = ready && c.every((s) => !!s.poNo);
    const openDests = Object.keys(cum).filter((d) => cum[d] % PCS_PER_CASE !== 0);
    const out = { seq: i + 1, lines: c, qty: c.reduce((a, s) => a + s.qty, 0), cut: openDests.length === 0, group, ready, openDests, heldByReduce: false, held: false };
    if (out.cut) group += 1;
    return out;
  });
}

/** XD09 [Search]: open qty (order qty - qty in submitted ASNs) of the lines not on hold, in H0253 order, pre-mapped to the POs released
 * by the business date (open PO qty = PO qty - qty in submitted ASNs), cut into supplier cases. Units of a part take the POs oldest date first. */
export function buildUnits(today: string, sentByLine: Record<string, number>, sentByPo: Record<string, number>, hold: Record<string, boolean> = {},
  noAsn = false, opts: { partHold?: Record<string, boolean>; caseHold?: Record<string, CaseHoldRow[]> } = {}): Unit[] {
  const units: Unit[] = [];
  for (const partNo of [...new Set(H0253.map((l) => l.partNo))]) {
    const released = POS.filter((p) => p.partNo === partNo && p.poDate <= today);
    const pos = [...released].sort((a, b) => a.poDate.localeCompare(b.poDate) || a.poNo.localeCompare(b.poNo))
      .map((po) => ({ po, open: po.qty - (sentByPo[po.poNo] ?? 0) }));
    // replicated by XD08 the day after the Customer Order Date
    const partLines = H0253.filter((l) => l.partNo === partNo && l.orderDt < today).sort((a, b) => scanKey(a).localeCompare(scanKey(b)));
    for (const orderDt of [...new Set(partLines.map((l) => l.orderDt))]) {
      const all = partLines.filter((l) => l.orderDt === orderDt);
      // lines with UPD_STATUS (changed in G-System) are not taken
      // without any ASN nothing can be received in G-System: only the cancels (status 2) apply
      const open = all.filter((l) => !(l.upd && l.upd.date <= today && (!noAsn || l.upd.status === '2'))).map((l) => ({ ...l, qty: l.qty - (sentByLine[l.id] ?? 0) })).filter((l) => l.qty > 0);
      const ls = open.filter((l) => !hold[l.id]);
      const cases = cutCases(ls, pos);
      const key = unitKey(partNo, orderDt);
      const rawReadyCases = cases.filter((c) => c.ready).length;
      // Hold per case (D/S check box): the first held case and every later case are not Ready; the Ready part ends on the last
      // valid cut before the first held case (cases of the same block are held together).
      const held = resolveCaseHold(cases, opts.caseHold?.[key] ?? []);
      cases.forEach((c) => { c.held = held.includes(c.seq); });
      if (held.length) {
        const first = Math.min(...held);
        const readyEnd = Math.max(0, ...cases.filter((c) => c.cut && c.seq < first).map((c) => c.seq));
        cases.forEach((c) => { if (c.ready && c.seq > readyEnd) { c.ready = false; c.heldByReduce = true; } });
      }
      const reduce = cases.filter((c) => c.heldByReduce).length;
      const readyCases = cases.filter((c) => c.ready).length;
      const unitHold = !!opts.partHold?.[partNo];
      const sent = all.some((l) => (sentByLine[l.id] ?? 0) > 0);
      const status: UnitStatus = !open.length ? 'created' : !ls.length || unitHold ? 'hold' : readyCases === cases.length ? 'ready'
        : cases.some((c) => c.ready && c.cut) ? 'partial' : 'notReady';
      const orderQty = all.reduce((a, l) => a + l.qty, 0);
      const forDate = released.filter((p) => p.orderDt === orderDt);
      const regular = forDate.find((p) => !p.split) ?? null;
      const splits = forDate.filter((p) => p.split);
      const poCheck: PoCheck = {
        orderQty, due: addDays(orderDt, 1), regular, splits, short: !!regular && regular.qty < orderQty,
        missing: Math.max(0, orderQty - forDate.reduce((a, p) => a + p.qty, 0)),
      };
      units.push({
        key, partNo, supplier: all[0].supplier, orderDt, lines: ls, heldLines: open.filter((l) => hold[l.id]),
        qty: ls.reduce((a, l) => a + l.qty, 0), cases, caseCount: cases.length, readyCases, rawReadyCases, reduce, unitHold,
        validEnds: unitHold ? [] : cases.filter((c) => c.ready && c.cut).map((c) => c.seq), sent, status, poCheck,
      });
    }
  }
  return units.sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status] || a.partNo.localeCompare(b.partNo) || a.orderDt.localeCompare(b.orderDt));
}

/** Cases of a Case Group of the unit. */
export function groupCases(u: Unit, group: number): UnitCase[] {
  return u.cases.filter((c) => c.group === group);
}

/** The selection of a unit always ends on the last case of a Case Group: ticking case n gives the first valid end >= n (null when none). */
export function endFor(u: Unit, n: number): number | null {
  return u.validEnds.find((e) => e >= n) ?? null;
}

/** Unticking case n goes back to the previous valid end (null = nothing ticked). */
export function endBefore(u: Unit, n: number): number | null {
  return [...u.validEnds].reverse().find((e) => e < n) ?? null;
}

export function contentOf(ls: InstrLine[]): string {
  return ls.map((l) => `${DESTS[l.destCd].short} ${l.qty} (${l.custOrderNo})`).join(' + ');
}

export interface AsnCase {
  seq: number;
  partNo: string;
  orderDt: string;
  lines: InstrLine[];
  qty: number;
}

/** Cases of an ASN: cases 1..end of each selected unit (supplier cases in H0253 order), numbered through the ASN. */
export function buildCases(sel: { unit: Unit; end: number }[]): AsnCase[] {
  const out: AsnCase[] = [];
  for (const { unit, end } of sel) {
    for (const c of unit.cases.slice(0, end)) out.push({ seq: out.length + 1, partNo: unit.partNo, orderDt: unit.orderDt, lines: c.lines, qty: c.qty });
  }
  return out;
}

export function caseNoOf(asnNo: string, seq: number): string {
  return `C-${asnNo.replace(/^ASN/, '')}-${String(seq).padStart(2, '0')}`;
}

/** ASN number as in simulasi_asn_rev.xlsx (ASN0001, ASN0002, ...). */
export function asnNoFor(seq: number): string {
  return `ASN${String(seq).padStart(4, '0')}`;
}

export interface RitCycle {
  no: string;
  route: string;
}

/** Mock route master: a holiday has no rit cycle, Saturday has one (the workbook days 16-22 Oct all have a rit). */
const NO_RIT = ['2026-10-25', '2026-11-01'];
export function ritCyclesFor(deliveryDate: string): RitCycle[] {
  if (!deliveryDate) return [];
  const day = new Date(`${deliveryDate}T00:00:00Z`).getUTCDay();
  const all = [{ no: 'Rit 1', route: 'SD01' }, { no: 'Rit 2', route: 'SD02' }, { no: 'Rit 3', route: 'SD03' }];
  if (NO_RIT.includes(deliveryDate)) return [];
  return day === 6 ? all.slice(0, 1) : all;
}

export interface SubmittedAsn {
  asnNo: string;
  /** Supplier Code + Plant key of SUPPLIERS (one ASN = one supplier + plant). */
  supplier: string;
  deliveryDate: string;
  rit: RitCycle;
  unitKeys: string[];
  cases: AsnCase[];
  createdBy: string;
  createdAt: string;
  /** Business date of the creation. */
  businessDate: string;
  /** ASN of simulasi_asn_rev.xlsx created before the business date. */
  seed?: boolean;
}

/** Qty already in submitted ASNs per H0253 line and per PO. */
export function sentQty(asns: SubmittedAsn[]): { byLine: Record<string, number>; byPo: Record<string, number> } {
  const byLine: Record<string, number> = {};
  const byPo: Record<string, number> = {};
  for (const a of asns) {
    for (const c of a.cases) {
      for (const l of c.lines) {
        byLine[l.id] = (byLine[l.id] ?? 0) + l.qty;
        if (l.poNo) byPo[l.poNo] = (byPo[l.poNo] ?? 0) + l.qty;
      }
    }
  }
  return { byLine, byPo };
}

/** PO order qty of the Pra Daily Order part. */
export function poQtyOf(poNo: string): number {
  return POS.find((p) => p.poNo === poNo)?.qty ?? 0;
}
