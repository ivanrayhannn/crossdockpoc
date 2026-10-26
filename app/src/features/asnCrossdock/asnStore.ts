import { useSyncExternalStore } from 'react';
import { buildCases, buildUnits, HOLD_INIT, niceDate, sentQty, type SubmittedAsn } from './data';

/** ASNs of simulasi_asn_rev.xlsx in creation order: [ASN No, business date, rit, units (Part + Customer Order Date, cases 1..end)]. */
const SEED_PLAN: [string, string, string, [string, number][]][] = [
  ['ASN0001', '2026-10-16', 'Rit 1', [['PART-X|2026-10-15', 1]]],
  ['ASN0002', '2026-10-17', 'Rit 1', [['PART-X|2026-10-16', 1]]],
  ['ASN0003', '2026-10-18', 'Rit 1', [['PART-X|2026-10-17', 4]]],
  ['ASN0004', '2026-10-19', 'Rit 1', [['PART-X|2026-10-17', 1]]],
  ['ASN0005', '2026-10-19', 'Rit 1', [['PART-X|2026-10-18', 3]]],
  ['ASN0006', '2026-10-20', 'Rit 1', [['PART-X|2026-10-19', 1]]],
  ['ASN0007', '2026-10-20', 'Rit 2', [['PART-X|2026-10-19', 1]]],
];

/** Builds the ASNs of the workbook with the same Search (XD09) as the screen, one after the other. */
function seed(): SubmittedAsn[] {
  const out: SubmittedAsn[] = [];
  for (const [asnNo, date, rit, picks] of SEED_PLAN) {
    const s = sentQty(out);
    const units = buildUnits(date, s.byLine, s.byPo, HOLD_INIT);
    const sel = picks.map(([key, end]) => ({ unit: units.find((u) => u.key === key), end })).filter((x) => x.unit && x.unit.validEnds.includes(x.end));
    if (sel.length !== picks.length) console.warn(`seed ${asnNo}: unit or case not available`);
    const ok = sel as { unit: NonNullable<(typeof sel)[number]['unit']>; end: number }[];
    out.push({
      asnNo, supplier: '50221-1', deliveryDate: date, rit: { no: rit, route: rit === 'Rit 2' ? 'SD02' : 'SD01' }, unitKeys: ok.map((x) => x.unit.key),
      cases: buildCases(ok), createdBy: 'D. Anggraini', createdAt: `${date.slice(8)}-Oct-2026 08:${rit === 'Rit 2' ? '40' : '14'}`, businessDate: date, seed: true,
    });
  }
  return out;
}

const SEEDS = seed();
let businessDate = '2026-10-18';
let created: SubmittedAsn[] = [];
let asns: SubmittedAsn[] = [];
const listeners = new Set<() => void>();

/** ASNs visible on the business date: those of the workbook created before it, and those created in this session. */
function refresh(): void {
  asns = [...created, ...SEEDS.filter((a) => a.businessDate < businessDate).reverse()];
  listeners.forEach((l) => l());
}
refresh();

export function addAsn(a: SubmittedAsn): void {
  created = [a, ...created];
  refresh();
}

/** Business date of the prototype; a new date starts again from the workbook state (ASNs created in the session are dropped). */
export function setBusinessDate(d: string): void {
  businessDate = d;
  created = [];
  refresh();
}

function subscribe(l: () => void): () => void {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function useAsns(): SubmittedAsn[] {
  return useSyncExternalStore(subscribe, () => asns);
}

export function useBusinessDate(): string {
  return useSyncExternalStore(subscribe, () => businessDate);
}

/* ---- Submit ASN batch and its log (prototype of the existing Supplier System log) ---- */

export interface LogMessage {
  time: string;
  type: 'Info' | 'Error';
  msgId: string;
  text: string;
}

export interface LogRecord {
  submitId: string;
  functionId: string;
  process: string;
  status: 'Processing' | 'Success' | 'Error';
  createdBy: string;
  startAt: string;
  endAt: string | null;
  messages: LogMessage[];
}

let logs: LogRecord[] = [];
const logListeners = new Set<() => void>();
let submitSeq = 0;

function stamp(): string {
  const d = new Date();
  return `${d.toISOString().slice(0, 10)} ${d.toTimeString().slice(0, 8)}`;
}

function emitLogs(): void {
  logs = [...logs];
  logListeners.forEach((l) => l());
}

/**
 * [Submit ASN] Yes: the ASN is handed to the batch X14 with a Submit ID. The units are locked at once; the batch
 * writes the result to the log (no success popup on the screen).
 */
export function submitAsnBatch(a: SubmittedAsn, businessDate: string): string {
  submitSeq += 1;
  const submitId = `ASNSUB-${businessDate.replace(/-/g, '')}-${String(submitSeq).padStart(4, '0')}`;
  const rec: LogRecord = {
    submitId, functionId: 'X14', process: 'ASN Submit', status: 'Processing', createdBy: a.createdBy, startAt: stamp(), endAt: null,
    messages: [{ time: stamp(), type: 'Info', msgId: 'LOG1', text: `ASN submit started. Submit ID ${submitId}, ${a.cases.length} cases.` }],
  };
  logs = [rec, ...logs];
  addAsn(a);
  emitLogs();
  const qty = a.cases.reduce((s, c) => s + c.qty, 0);
  window.setTimeout(() => {
    rec.messages.push({
      time: stamp(), type: 'Info', msgId: 'LOG2',
      text: `${a.asnNo} submitted with status Created. ${a.cases.length} cases (${qty} pcs) are locked. Delivery ${niceDate(a.deliveryDate)} · ${a.rit.no}. The ASN is shown in ASN Inquiry.`,
    });
    rec.messages.push({ time: stamp(), type: 'Info', msgId: 'LOG3', text: `ASN submit ended. Status SUCCESS.` });
    rec.status = 'Success';
    rec.endAt = stamp();
    emitLogs();
  }, 1500);
  return submitId;
}

function subscribeLogs(l: () => void): () => void {
  logListeners.add(l);
  return () => logListeners.delete(l);
}

export function useLogs(): LogRecord[] {
  return useSyncExternalStore(subscribeLogs, () => logs);
}
