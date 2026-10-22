/* ASN Crossdock — mock data and the Search pre-mapping of XD09 (decided 21-Oct):
   - the open qty of the customer order lines (H0253, order status 7, Hold Flag N) is read in the receiving scan order of G-System
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
  '50221-1': { code: '50221', plant: '1', name: 'PT Dummy Supplier Indonesia' },
  '50330-2': { code: '50330', plant: '2', name: 'PT Contoh Komponen' },
};

/** Supplier of the login user in the supplier view (the D/S team sees every supplier). */
export const LOGIN_SUPPLIER = '50221-1';

export interface Dest {
  code: string;
  short: string;
  name: string;
}

/** 7-digit destination code (TB_M_H0125_DESTINATION.DESTINATION_CD). */
export const DESTS: Record<string, Dest> = {
  '9715310': { code: '9715310', short: 'VN', name: 'Vietnam' },
  '9811110': { code: '9811110', short: 'PH', name: 'Philippines' },
  '9722D10': { code: '9722D10', short: 'TH', name: 'Thailand' },
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
}

export const PART_NAME: Record<string, string> = {
  'PART-A': 'Dummy Part A',
  'PART-B': 'Dummy Part B',
  'PART-C': 'Dummy Part C',
  'PART-D': 'Dummy Part D',
};

/** Supplier of each part (PO supplier of the Pra Daily Order). */
const PART_SUPPLIER: Record<string, string> = { 'PART-A': '50221-1', 'PART-B': '50221-1', 'PART-C': '50221-1', 'PART-D': '50330-2' };

const VN = '9715310';
const PH = '9811110';
const TH = '9722D10';
/** Dummy customer code per destination (scan key 2). */
const CUST: Record<string, string> = { [VN]: '9715300', [TH]: '9722D00', [PH]: '9811100' };

type Raw = [order: string, dest: string, qty: number, cust?: string, item?: string, time?: string];

function lines(orderDt: string, partNo: string, raw: Raw[]): InstrLine[] {
  return raw.map(([order, dest, qty, cust, item, time]) => ({
    id: `${partNo}|${orderDt}|${order}|${item ?? '0001'}`,
    custCd: cust ?? CUST[dest],
    custOrderNo: order,
    orderDt,
    orderTime: time ?? '080000',
    destCd: dest,
    detailedItemNo: item ?? '0001',
    serialNo: '0000001',
    partNo,
    qty,
    poNo: null,
    poDate: null,
    manifestNo: null,
    manifestItemNo: null,
    supplier: PART_SUPPLIER[partNo],
  }));
}

/** H0253 lines (6 pcs / case). Every destination qty of a unit is a multiple of pcs/case (G-System releases multiples of pcs/case).
 * - PART-A 12-Oct: already in an ASN.
 * - PART-A 14-Oct: V01 VN 10, T01 TH 6, V02 VN 14 (SIM-7 / SIM-9): case 2 = VN 4 + TH 2 cannot be the last case.
 * - PART-B 14-Oct: SIM-8 (A-0101 two items, B-0102 TH, C-0103 of a second VN customer); PART-B 15-Oct A-0201 is the next unit.
 * - PART-C 13-Oct: normal unit, all cases Ready.
 * - PART-D 13-Oct: second supplier (D/S team only). */
export const H0253: InstrLine[] = [
  ...lines('2026-10-12', 'PART-A', [['CO-12001', VN, 6], ['CO-12002', TH, 6]]),
  ...lines('2026-10-14', 'PART-A', [['V01', VN, 10, 'CUST-A'], ['T01', TH, 6, 'CUST-B'], ['V02', VN, 14, 'CUST-C']]),
  ...lines('2026-10-14', 'PART-B', [['C-0103', VN, 14, '9730000', '0001', '070000'], ['B-0102', TH, 6, undefined, '0001', '090000'],
    ['A-0101', VN, 2, undefined, '0002'], ['A-0101', VN, 8, undefined, '0001']]),
  ...lines('2026-10-15', 'PART-B', [['A-0201', VN, 6]]),
  ...lines('2026-10-13', 'PART-C', [['CO-13001', VN, 4], ['CO-13002', VN, 8], ['CO-13003', PH, 6]]),
  ...lines('2026-10-13', 'PART-D', [['CO-13007', VN, 6], ['CO-13008', TH, 4], ['CO-13009', TH, 2]]),
];

/** Crossdock PO part of the Pra Daily Order (manifest with CROSS_DOCK_FLAG = 'X'); released on poDate. */
export interface Po {
  poNo: string;
  manifestNo: string;
  manifestItemNo: string;
  partNo: string;
  qty: number;
  poDate: string;
}

export const POS: Po[] = [
  { poNo: 'PO-DMY-09000', manifestNo: 'MF-DMY-09000', manifestItemNo: '0001', partNo: 'PART-A', qty: 12, poDate: '2026-10-13' },
  { poNo: 'PO-DMY-09011', manifestNo: 'MF-DMY-09011', manifestItemNo: '0001', partNo: 'PART-A', qty: 24, poDate: '2026-10-15' },
  { poNo: 'PO-DMY-10011', manifestNo: 'MF-DMY-10011', manifestItemNo: '0001', partNo: 'PART-A', qty: 6, poDate: '2026-10-16' },
  { poNo: 'PO-DMY-09021', manifestNo: 'MF-DMY-09021', manifestItemNo: '0001', partNo: 'PART-B', qty: 20, poDate: '2026-10-15' },
  { poNo: 'PO-DMY-10021', manifestNo: 'MF-DMY-10021', manifestItemNo: '0001', partNo: 'PART-B', qty: 10, poDate: '2026-10-16' },
  { poNo: 'PO-DMY-09031', manifestNo: 'MF-DMY-09031', manifestItemNo: '0001', partNo: 'PART-C', qty: 18, poDate: '2026-10-14' },
  { poNo: 'PO-DMY-09041', manifestNo: 'MF-DMY-09041', manifestItemNo: '0001', partNo: 'PART-D', qty: 12, poDate: '2026-10-14' },
];

export const BUSINESS_DATES = ['2026-10-14', '2026-10-15', '2026-10-16'];

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

/** Scan order key: Allocation Priority (= Customer Order Date), then the G-System allocation keys. */
function scanKey(l: InstrLine): string {
  return [l.orderDt, l.custCd, l.custOrderNo, l.orderDt, l.orderTime, l.destCd, l.detailedItemNo, l.serialNo].join('|');
}

/** A supplier case of a unit: PCS_PER_CASE pcs in scan order. */
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
}

export type UnitStatus = 'ready' | 'partial' | 'notReady' | 'created' | 'hold';

export interface Unit {
  /** Part Number + Customer Order Date. */
  key: string;
  partNo: string;
  /** Supplier Code + Plant key of SUPPLIERS. */
  supplier: string;
  orderDt: string;
  /** Open order lines in scan order (Hold Flag = N, qty = open qty). */
  lines: InstrLine[];
  /** Order lines put on hold by the D/S team (Hold Flag = Y); shown in the D/S detail only. */
  heldLines: InstrLine[];
  /** Open qty of the unit. */
  qty: number;
  cases: UnitCase[];
  caseCount: number;
  /** PO Readiness: Ready cases. */
  readyCases: number;
  /** Cases the user may end the selection on (CUT_FLAG Y and Ready). */
  validEnds: number[];
  /** Some qty of the unit is already in a submitted ASN. */
  sent: boolean;
  status: UnitStatus;
}

export function unitKey(partNo: string, orderDt: string): string {
  return `${partNo}|${orderDt}`;
}

const STATUS_ORDER: Record<UnitStatus, number> = { ready: 0, partial: 1, notReady: 2, hold: 3, created: 4 };

/** Cuts the open qty of one unit (lines in scan order) into supplier cases, taking the PO qty in order (pos are reduced in place). */
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
    const out = { seq: i + 1, lines: c, qty: c.reduce((a, s) => a + s.qty, 0), cut: openDests.length === 0, group, ready, openDests };
    if (out.cut) group += 1;
    return out;
  });
}

/** XD09 [Search]: open qty (order qty - qty in submitted ASNs) of the lines not on hold, in scan order, pre-mapped to the POs released
 * by the business date (open PO qty = PO qty - qty in submitted ASNs), cut into supplier cases. Units of a part take the POs oldest date first. */
export function buildUnits(today: string, sentByLine: Record<string, number>, sentByPo: Record<string, number>, hold: Record<string, boolean> = {}): Unit[] {
  const units: Unit[] = [];
  for (const partNo of [...new Set(H0253.map((l) => l.partNo))]) {
    const pos = POS.filter((p) => p.partNo === partNo && p.poDate <= today).sort((a, b) => a.poDate.localeCompare(b.poDate))
      .map((po) => ({ po, open: po.qty - (sentByPo[po.poNo] ?? 0) }));
    const partLines = H0253.filter((l) => l.partNo === partNo).sort((a, b) => scanKey(a).localeCompare(scanKey(b)));
    for (const orderDt of [...new Set(partLines.map((l) => l.orderDt))]) {
      const all = partLines.filter((l) => l.orderDt === orderDt);
      const open = all.map((l) => ({ ...l, qty: l.qty - (sentByLine[l.id] ?? 0) })).filter((l) => l.qty > 0);
      const ls = open.filter((l) => !hold[l.id]);
      const cases = cutCases(ls, pos);
      const readyCases = cases.filter((c) => c.ready).length;
      const sent = all.some((l) => (sentByLine[l.id] ?? 0) > 0);
      const status: UnitStatus = !open.length ? 'created' : !ls.length ? 'hold' : readyCases === cases.length ? 'ready'
        : cases.some((c) => c.ready && c.cut) ? 'partial' : 'notReady';
      units.push({
        key: unitKey(partNo, orderDt), partNo, supplier: all[0].supplier, orderDt, lines: ls, heldLines: open.filter((l) => hold[l.id]),
        qty: ls.reduce((a, l) => a + l.qty, 0), cases, caseCount: cases.length, readyCases,
        validEnds: cases.filter((c) => c.ready && c.cut).map((c) => c.seq), sent, status,
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

/** Cases of an ASN: cases 1..end of each selected unit (supplier cases in scan order), numbered through the ASN. */
export function buildCases(sel: { unit: Unit; end: number }[]): AsnCase[] {
  const out: AsnCase[] = [];
  for (const { unit, end } of sel) {
    for (const c of unit.cases.slice(0, end)) out.push({ seq: out.length + 1, partNo: unit.partNo, orderDt: unit.orderDt, lines: c.lines, qty: c.qty });
  }
  return out;
}

export function caseNoOf(asnNo: string, seq: number): string {
  return `${asnNo.replace('ASN-', 'C-')}-${String(seq).padStart(2, '0')}`;
}

export function asnNoFor(supplier: string, deliveryDate: string, seq: number): string {
  return `ASN-${SUPPLIERS[supplier].code}-${deliveryDate.slice(2).replace(/-/g, '')}-${String(seq).padStart(3, '0')}`;
}

export interface RitCycle {
  no: string;
  route: string;
}

/** Mock route master: Sunday has no rit cycle, Saturday has one. */
export function ritCyclesFor(deliveryDate: string): RitCycle[] {
  if (!deliveryDate) return [];
  const day = new Date(`${deliveryDate}T00:00:00Z`).getUTCDay();
  const all = [{ no: 'Rit 1', route: 'SD01' }, { no: 'Rit 2', route: 'SD02' }, { no: 'Rit 3', route: 'SD03' }];
  if (day === 0) return [];
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
