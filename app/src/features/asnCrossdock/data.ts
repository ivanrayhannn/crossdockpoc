/* ASN Crossdock — mock data of the Search pre-mapping (#TEMP_INSTRUCTION: customer order line ↔ supplier PO, FIFO by order date) and
   the rules of the ASN flow: the unit is Part Number + Customer Order Date, one case per
   Part + Customer Order Date + destination, and an ASN may hold several such units. */

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

/** One row of #TEMP_INSTRUCTION: a customer order line (H0253, order status 7) paired with a supplier PO. */
export interface InstrLine {
  id: string;
  custOrderNo: string;
  /** Customer Order Date (ISO). */
  orderDt: string;
  destCd: string;
  detailedItemNo: string;
  partNo: string;
  qty: number;
  /** Supplier PO the line is assigned to; null while not assigned yet. */
  poNo: string | null;
  /** PO Date (ISO). A PO dated after the business date is planned, not released yet. */
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

type Raw = [order: string, dest: string, qty: number, po: string | null, poDate: string | null];

const VN = '9715310';
const PH = '9811110';
const TH = '9722D10';

function lines(orderDt: string, partNo: string, raw: Raw[]): InstrLine[] {
  return raw.map(([order, dest, qty, po, poDate], i) => ({
    id: `${partNo}|${orderDt}|${i + 1}`,
    custOrderNo: order,
    orderDt,
    destCd: dest,
    detailedItemNo: String(i + 1).padStart(4, '0'),
    partNo,
    qty,
    poNo: po,
    poDate,
    manifestNo: po ? `M${po.replace('PO', '')}0${i % 3}` : null,
    manifestItemNo: po ? String((i % 3) + 1).padStart(3, '0') : null,
    supplier: PART_SUPPLIER[partNo],
  }));
}

/** Seed covering the three conditions of the flow (6 pcs / case):
 * - PART-A 13-Oct: condition 1, destinations in sequence (VN, VN, PH, TH, TH, TH).
 * - PART-B 13-Oct: condition 2, destinations not in sequence.
 * - PART-C 13-Oct: condition 3, assigned to POs of 14-Oct and 15-Oct: ready only from 15-Oct.
 * - 14-Oct units: PART-A ready from 15-Oct, PART-B (Vietnam 24 pcs = 4 cases) waits for the PO of 16-Oct, PART-C has no PO yet.
 * - Every destination qty is a multiple of pcs/case (G-TOPAS releases multiples of pcs/case).
 * - PART-A 12-Oct: already in an ASN. */
export const INSTRUCTIONS: InstrLine[] = [
  ...lines('2026-10-12', 'PART-A', [['CO-12001', VN, 6, 'PO0', '2026-10-13'], ['CO-12002', TH, 6, 'PO0', '2026-10-13']]),
  ...lines('2026-10-13', 'PART-A', [
    ['CO-13001', VN, 4, 'PO1', '2026-10-14'], ['CO-13002', VN, 2, 'PO1', '2026-10-14'], ['CO-13003', PH, 6, 'PO1', '2026-10-14'],
    ['CO-13004', TH, 2, 'PO1', '2026-10-14'], ['CO-13005', TH, 2, 'PO1', '2026-10-14'], ['CO-13006', TH, 2, 'PO1', '2026-10-14'],
  ]),
  ...lines('2026-10-13', 'PART-B', [
    ['CO-13001', VN, 4, 'PO1', '2026-10-14'], ['CO-13004', TH, 2, 'PO1', '2026-10-14'], ['CO-13003', PH, 6, 'PO1', '2026-10-14'],
    ['CO-13005', TH, 2, 'PO1', '2026-10-14'], ['CO-13002', VN, 2, 'PO1', '2026-10-14'], ['CO-13006', TH, 2, 'PO1', '2026-10-14'],
  ]),
  ...lines('2026-10-13', 'PART-C', [
    ['CO-13001', VN, 4, 'PO1', '2026-10-14'], ['CO-13004', TH, 2, 'PO1', '2026-10-14'], ['CO-13003', PH, 6, 'PO1', '2026-10-14'],
    ['CO-13005', TH, 2, 'PO2', '2026-10-15'], ['CO-13002', VN, 2, 'PO2', '2026-10-15'], ['CO-13006', TH, 2, 'PO2', '2026-10-15'],
  ]),
  ...lines('2026-10-14', 'PART-A', [['CO-14001', VN, 6, 'PO2', '2026-10-15'], ['CO-14002', TH, 6, 'PO2', '2026-10-15'], ['CO-14003', PH, 6, 'PO2', '2026-10-15']]),
  // Vietnam 24 pcs = 4 cases of 6 pcs: case 1-2 CO-14001, case 3 CO-14001 4 + CO-14006 2, case 4 CO-14006 2 (PO2) + CO-14007 4 (PO4); Thailand waits for PO3
  ...lines('2026-10-14', 'PART-B', [['CO-14001', VN, 16, 'PO2', '2026-10-15'], ['CO-14006', VN, 4, 'PO2', '2026-10-15'], ['CO-14007', VN, 4, 'PO4', '2026-10-15'], ['CO-14002', TH, 6, 'PO3', '2026-10-16']]),
  ...lines('2026-10-14', 'PART-C', [['CO-14004', TH, 2, null, null], ['CO-14005', TH, 4, null, null]]),
  // Second supplier (50330 plant 2): visible to the D/S team only; cannot share an ASN with supplier 50221
  ...lines('2026-10-13', 'PART-D', [['CO-13007', VN, 6, 'PO5', '2026-10-14'], ['CO-13008', TH, 4, 'PO5', '2026-10-14'], ['CO-13009', TH, 2, 'PO5', '2026-10-14']]),
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

/** A line counts as assigned only when its PO is released (PO Date on or before the business date). */
export function isAssigned(l: InstrLine, today: string): boolean {
  return !!l.poNo && !!l.poDate && l.poDate <= today;
}

export type UnitStatus = 'ready' | 'notReady' | 'created' | 'hold';

export interface Unit {
  /** Part Number + Customer Order Date. */
  key: string;
  partNo: string;
  /** Supplier Code + Plant key of SUPPLIERS. */
  supplier: string;
  orderDt: string;
  /** Order lines taken by Get Order (Hold Flag = N). */
  lines: InstrLine[];
  /** Order lines put on hold by the D/S team (Hold Flag = Y); shown in the D/S detail only. */
  heldLines: InstrLine[];
  qty: number;
  assignedQty: number;
  remainingQty: number;
  pos: string[];
  lastPoDate: string | null;
  /** Cases of the unit: per destination, qty / pcs/case. */
  caseCount: number;
  /** Cases (destinations) that still hold qty without a released PO. */
  notAssignedCases: number;
  /** PO Readiness: cases whose whole qty is assigned to a released PO. */
  readyCases: number;
  ready: boolean;
  asnNo: string | null;
  status: UnitStatus;
}

export function unitKey(partNo: string, orderDt: string): string {
  return `${partNo}|${orderDt}`;
}

const STATUS_ORDER: Record<UnitStatus, number> = { ready: 0, notReady: 1, hold: 2, created: 3 };

/** Get Order: customer orders (Hold Flag = N) pre-mapped to released POs, FIFO by order date. */
export function buildUnits(today: string, asnByUnit: Record<string, string>, hold: Record<string, boolean> = {}): Unit[] {
  const map = new Map<string, InstrLine[]>();
  for (const l of INSTRUCTIONS) {
    const k = unitKey(l.partNo, l.orderDt);
    map.set(k, [...(map.get(k) ?? []), l]);
  }
  return [...map.entries()]
    .map(([key, all]) => {
      const ls = all.filter((l) => !hold[l.id]);
      const qty = ls.reduce((a, l) => a + l.qty, 0);
      const assignedQty = ls.filter((l) => isAssigned(l, today)).reduce((a, l) => a + l.qty, 0);
      const poDates = ls.map((l) => l.poDate).filter((d): d is string => !!d).sort();
      const packed = byDestination(ls).flatMap(([, d]) => packCases(d));
      const caseCount = packed.length;
      const notAssignedCases = packed.filter((c) => c.some((l) => !isAssigned(l, today))).length;
      const asnNo = asnByUnit[key] ?? null;
      const ready = ls.length > 0 && qty === assignedQty;
      return {
        key,
        partNo: all[0].partNo,
        supplier: all[0].supplier,
        orderDt: all[0].orderDt,
        lines: ls,
        heldLines: all.filter((l) => hold[l.id]),
        qty,
        assignedQty,
        remainingQty: qty - assignedQty,
        pos: [...new Set(ls.map((l) => l.poNo).filter((p): p is string => !!p))],
        lastPoDate: poDates.length ? poDates[poDates.length - 1] : null,
        caseCount,
        notAssignedCases,
        readyCases: caseCount - notAssignedCases,
        ready,
        asnNo,
        status: (asnNo ? 'created' : !ls.length ? 'hold' : ready ? 'ready' : 'notReady') as UnitStatus,
      };
    })
    .sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status] || a.partNo.localeCompare(b.partNo) || a.orderDt.localeCompare(b.orderDt));
}

export interface AsnCase {
  seq: number;
  partNo: string;
  orderDt: string;
  destCd: string;
  lines: InstrLine[];
  qty: number;
}

/** Lines of a unit grouped by destination, in order of first appearance. */
export function byDestination(ls: InstrLine[]): [string, InstrLine[]][] {
  const m = new Map<string, InstrLine[]>();
  for (const l of ls) m.set(l.destCd, [...(m.get(l.destCd) ?? []), l]);
  return [...m.entries()];
}

/** Packs the lines of one destination into cases of PCS_PER_CASE pcs. A case can hold several customer order lines and POs;
 * a line larger than the free space is split over the next case. Releases are multiples of pcs/case, so every case is full. */
export function packCases(ls: InstrLine[]): InstrLine[][] {
  const cases: InstrLine[][] = [];
  let cur: InstrLine[] = [];
  let free = PCS_PER_CASE;
  for (const l of ls) {
    let left = l.qty;
    while (left > 0) {
      const take = Math.min(left, free);
      cur.push({ ...l, qty: take });
      left -= take;
      free -= take;
      if (free === 0) {
        cases.push(cur);
        cur = [];
        free = PCS_PER_CASE;
      }
    }
  }
  if (cur.length) cases.push(cur);
  return cases;
}

/** Cases per Part + Customer Order Date + destination (qty / pcs/case), numbered in order of first appearance. */
export function buildCases(units: Unit[]): AsnCase[] {
  const out: AsnCase[] = [];
  for (const u of units) {
    for (const [destCd, ls] of byDestination(u.lines)) {
      for (const c of packCases(ls)) {
        out.push({ seq: out.length + 1, partNo: u.partNo, orderDt: u.orderDt, destCd, lines: c, qty: c.reduce((a, l) => a + l.qty, 0) });
      }
    }
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

/** Mock PO order qty of a part: total qty of all lines assigned to the PO. */
export function poQtyOf(poNo: string, partNo: string): number {
  return INSTRUCTIONS.filter((l) => l.poNo === poNo && l.partNo === partNo).reduce((a, l) => a + l.qty, 0);
}
