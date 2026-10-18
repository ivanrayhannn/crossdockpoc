import { useSyncExternalStore } from 'react';

/** Sidebar groups and their items (shared by the Sidebar and the Menu Settings admin panel). */
export const NAV_GROUPS: [string, string[]][] = [
  ['Ordering', ['Service Part Order']],
  ['ASN', ['Case Label Printing', 'ASN Creation', 'Delivery Note Creation', 'Case Consolidation Simulation', 'ASN Inquiry', 'Cancel Order Simulation']],
  ['Transfer Posting', ['Stock Inquiry']],
  ['Timeline', ['Timeline']],
  ['Master', ['Sub Supplier Maintenance', 'Part Master Maintenance', 'Crossdock Master Setting']],
  ['Forecast', ['Forecast Inquiry']],
  ['Common', ['Log Monitoring', 'System Master Maintenance', 'Batch Process Simulation', 'Candidate Part Batch Flow', 'ASN Backend Process', 'Confirmation Points', 'Menu Settings']],
  ['Inventory Taking', ['Intak Period Maintenance', 'Yellow Line and CY Stock']],
];

/** The admin panel itself can never be hidden, otherwise hidden menus could not be shown again. */
export const LOCKED_ITEMS = new Set(['Menu Settings']);

const KEY = 'nsp.hiddenMenus';
const listeners = new Set<() => void>();

function load(): string[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    const v: unknown = raw ? JSON.parse(raw) : [];
    return Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : [];
  } catch {
    return [];
  }
}

let hidden: string[] = load();

export function setHiddenMenus(next: string[]): void {
  hidden = next.filter((i) => !LOCKED_ITEMS.has(i));
  try {
    window.localStorage.setItem(KEY, JSON.stringify(hidden));
  } catch {
    // storage unavailable: the setting stays for this page view only
  }
  listeners.forEach((l) => l());
}

function subscribe(l: () => void): () => void {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function useHiddenMenus(): string[] {
  return useSyncExternalStore(subscribe, () => hidden);
}
