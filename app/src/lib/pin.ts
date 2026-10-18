import { useSyncExternalStore } from 'react';

/** SHA-256 of the menu PIN (default 1810). Prototype only: a client-side gate, not real access control. */
export const PIN_HASH = '1a09807a0e6928a66d91025ed5fccd713c9edb101e72a1bbcb8a01cd9a53cb51';

/** Menus that always need the PIN (the admin panel itself). */
export const ALWAYS_PIN = new Set(['Menu Settings']);

const KEY = 'nsp.pinMenus';
const DEFAULT = ['Confirmation Points'];
const listeners = new Set<() => void>();

function load(): string[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    const v: unknown = raw ? JSON.parse(raw) : DEFAULT;
    return Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : DEFAULT;
  } catch {
    return DEFAULT;
  }
}

let pinned: string[] = load();

export function setPinMenus(next: string[]): void {
  pinned = next.filter((i) => !ALWAYS_PIN.has(i));
  try { window.localStorage.setItem(KEY, JSON.stringify(pinned)); } catch { /* storage unavailable */ }
  listeners.forEach((l) => l());
}

function subscribe(l: () => void): () => void {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function usePinMenus(): string[] {
  return useSyncExternalStore(subscribe, () => pinned);
}

export const needsPin = (item: string, list: string[]) => ALWAYS_PIN.has(item) || list.includes(item);
