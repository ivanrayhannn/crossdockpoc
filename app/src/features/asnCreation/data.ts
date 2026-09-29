import type { AsnCase, AsnQuery, DestCode, RemainingOrder } from './types';

export const SUPPLIER_CODE = '50221';
export const SUPPLIER_NAME = 'PT Dummy Supplier Indonesia';
export const SUPPLIER_CODES = ['50221', '50222'];
export const PART_NOS = ['Part 1', 'Part 2', 'Part 3'];

export const DEST_LABEL: Record<DestCode, string> = {
  VN: 'Vietnam · 789',
  JP: 'Japan · 456',
  TH: 'Thailand · 123',
};

const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** Formats an ISO date as "DD-Mon-YYYY", matching the rest of the app's date display. */
export function niceDate(iso: string): string {
  const [y, m, d] = iso.split('-');
  return `${d}-${MON[Number(m) - 1]}-${y}`;
}

export function addDaysIso(iso: string, delta: number): string {
  const t = new Date(`${iso}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() + delta);
  return t.toISOString().slice(0, 10);
}

type RawOrder = [no: string, qty: number];
type RawCaseGroup = [part: string, dest: DestCode, orders: RawOrder[]];
type RawPo = [po: string, date: string, cases: RawCaseGroup[]];

/** One supplier PO per delivery plan day; each (part, destination) pair inside it is a case
 * (a case never mixes parts or destinations). Mirrors the Case Consolidation Simulation's
 * "PO Date = Order Date + 1" rule, so case order dates below are derived, not stored. */
const RAW: RawPo[] = [
  [
    'PO1',
    '2026-09-16',
    [
      ['Part 1', 'VN', [['Order 1', 2], ['Order 2', 4]]],
      ['Part 1', 'JP', [['Order 3', 6]]],
      ['Part 2', 'VN', [['Order 4', 3], ['Order 5', 3]]],
      ['Part 2', 'TH', [['Order 6', 6]]],
    ],
  ],
  [
    'PO2',
    '2026-09-17',
    [
      ['Part 1', 'VN', [['Order 7', 1], ['Order 8', 5]]],
      ['Part 1', 'TH', [['Order 9', 6]]],
      ['Part 2', 'JP', [['Order 10', 2], ['Order 11', 2], ['Order 12', 2]]],
      ['Part 3', 'VN', [['Order 13', 6]]],
    ],
  ],
  [
    'PO3',
    '2026-09-18',
    [
      ['Part 1', 'VN', [['Order 14', 6]]],
      ['Part 2', 'VN', [['Order 15', 4], ['Order 16', 2]]],
      ['Part 2', 'JP', [['Order 17', 6]]],
      ['Part 3', 'TH', [['Order 18', 3], ['Order 19', 3]]],
    ],
  ],
  [
    'PO4',
    '2026-09-19',
    [
      ['Part 1', 'JP', [['Order 20', 6]]],
      ['Part 3', 'VN', [['Order 21', 2], ['Order 22', 4]]],
      ['Part 3', 'JP', [['Order 23', 6]]],
    ],
  ],
];

function buildCases(): AsnCase[] {
  const pad = (n: number) => String(n).padStart(2, '0');
  const cases: AsnCase[] = [];
  let n = 0;
  for (const [po, date, groups] of RAW) {
    for (const [part, dest, orders] of groups) {
      n++;
      const id = `X${pad(n)}`;
      cases.push({
        id,
        caseNo: `${SUPPLIER_CODE}X${pad(n)}`,
        po,
        date,
        part,
        dest,
        qty: orders.reduce((sum, [, qty]) => sum + qty, 0),
        orders: orders.map(([no, qty]) => ({ no, qty, date: addDaysIso(date, -1) })),
      });
    }
  }
  return cases;
}

export const CASES: AsnCase[] = buildCases();

/** Customer orders that have not yet been released into a PO, so they have no case and cannot
 * go into an ASN yet — either they were bumped by Max Case/Day off an already-released PO
 * ('cap'), or their auto PO simply hasn't run yet ('next'). */
export const REMAINING_ORDERS: RemainingOrder[] = [
  { date: '2026-09-17', no: 'Order 24', part: 'Part 2', dest: 'TH', qty: 6, kind: 'cap', po: 'PO3', poDate: '2026-09-18' },
  { date: '2026-09-18', no: 'Order 25', part: 'Part 3', dest: 'JP', qty: 6, kind: 'cap', po: 'PO4', poDate: '2026-09-19' },
  { date: '2026-09-19', no: 'Order 26', part: 'Part 1', dest: 'VN', qty: 6, kind: 'next' },
  { date: '2026-09-19', no: 'Order 27', part: 'Part 2', dest: 'JP', qty: 4, kind: 'next' },
  { date: '2026-09-19', no: 'Order 28', part: 'Part 2', dest: 'JP', qty: 2, kind: 'next' },
];

/** Cases already locked into an earlier ASN, so this build shows a realistic mix of
 * available/locked rows instead of everything being selectable. */
export const PRE_EXISTING_ASN: Record<string, string> = {
  X01: 'ASN-50221-260916-001',
  X02: 'ASN-50221-260916-001',
};

export const DEFAULT_QUERY: AsnQuery = {
  from: '2026-09-16',
  to: '2026-09-19',
  sup: SUPPLIER_CODE,
  po: '',
  part: 'all',
  dest: 'all',
  st: 'all',
};

export const DEFAULT_DELIVERY_DATE = '2026-09-30';

export const TODAY_ISO = '2026-09-29';
