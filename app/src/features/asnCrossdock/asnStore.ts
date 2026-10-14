import { useSyncExternalStore } from 'react';
import { buildCases, buildUnits, type SubmittedAsn } from './data';

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
