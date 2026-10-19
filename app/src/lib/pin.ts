import { useSyncExternalStore } from 'react';

/** SHA-256 of the menu PIN (default 1810). Prototype only: a client-side gate, not real access control. */
export const DEFAULT_PIN_HASH = '1a09807a0e6928a66d91025ed5fccd713c9edb101e72a1bbcb8a01cd9a53cb51';
const HASH_KEY = 'nsp.pinHash';

export async function sha256(text: string): Promise<string> {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Current PIN hash: changed in Menu Settings (kept in this browser), else the default (1810). */
export function getPinHash(): string {
  try { return window.localStorage.getItem(HASH_KEY) || DEFAULT_PIN_HASH; } catch { return DEFAULT_PIN_HASH; }
}

/** Change the PIN after checking the current one. Returns an error text or null when saved. */
export async function changePin(current: string, next: string): Promise<string | null> {
  if ((await sha256(current.trim())) !== getPinHash()) return 'Current PIN is wrong.';
  if (!/^\d{4,8}$/.test(next.trim())) return 'New PIN must be 4-8 digits.';
  try { window.localStorage.setItem(HASH_KEY, await sha256(next.trim())); } catch { return 'Cannot save in this browser.'; }
  return null;
}

export function resetPin(): void {
  try { window.localStorage.removeItem(HASH_KEY); } catch { /* storage unavailable */ }
}

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
