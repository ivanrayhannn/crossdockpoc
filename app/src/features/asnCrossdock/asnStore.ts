import { useSyncExternalStore } from 'react';
import { buildCases, buildUnits, niceDate, type SubmittedAsn } from './data';

/** Submitted ASNs shared by ASN Crossdock Creation and ASN Inquiry (two routes), kept for the browser session. */
let asns: SubmittedAsn[] = seed();
const listeners = new Set<() => void>();

function seed(): SubmittedAsn[] {
  const unit = buildUnits('2026-10-13', {}).find((u) => u.key === 'PART-A|2026-10-12');
  if (!unit) return [];
  return [{
    asnNo: 'ASN-50221-261013-001',
    deliveryDate: '2026-10-13',
    rit: { no: 'Rit 1', route: 'SD01' },
    unitKeys: [unit.key],
    cases: buildCases([unit]),
    createdBy: 'D. Anggraini',
    createdAt: '13-Oct-2026 08:14',
  }];
}

export function addAsn(a: SubmittedAsn): void {
  asns = [a, ...asns];
  listeners.forEach((l) => l());
}

function subscribe(l: () => void): () => void {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function useAsns(): SubmittedAsn[] {
  return useSyncExternalStore(subscribe, () => asns);
}

export function asnByUnitOf(list: SubmittedAsn[]): Record<string, string> {
  const out: Record<string, string> = {};
  list.forEach((a) => a.unitKeys.forEach((k) => (out[k] = a.asnNo)));
  return out;
}

/* ---- Submit ASN batch and its log (prototype of the existing NSP log) ---- */

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
