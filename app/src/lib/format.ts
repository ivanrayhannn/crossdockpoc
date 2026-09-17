/** Formats a number with thousands separators; non-numeric input renders as "0". */
export function fmt(v: number | string | undefined | null): string {
  const n = typeof v === 'number' ? v : Number(v);
  return (Number.isNaN(n) ? 0 : Math.round(n)).toLocaleString('en-US');
}

/** Parses a possibly-messy numeric input string into an integer, defaulting to 0. */
export function num(v: number | string | undefined | null): number {
  const n = parseInt(String(v ?? '').replace(/[^0-9]/g, ''), 10);
  return Number.isNaN(n) ? 0 : n;
}

export function madAvg(m: number[] | undefined): number {
  return m && m.length ? Math.round(m.reduce((a, x) => a + x, 0) / m.length) : 0;
}

const MON_IDX: Record<string, number> = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 };

/** Parses the app's "DD-Mon-YYYY HH:MM" timestamp string into a sortable
 * epoch value; unparsable/placeholder values (e.g. "sekarang") sort as now. */
export function parseDt(s: string): number {
  const m = /^(\d{2})-(\w{3})-(\d{4}) (\d{2}):(\d{2})$/.exec(s);
  if (!m) return Date.now();
  const [, dd, mon, yyyy, hh, mi] = m;
  return new Date(Number(yyyy), MON_IDX[mon] ?? 0, Number(dd), Number(hh), Number(mi)).getTime();
}

export interface SyncBadge {
  t: string;
  bg: string;
  fg: string;
}

export function syncBadge(gt: boolean, pole: boolean): SyncBadge {
  if (gt && pole) return { t: 'Both Sync', bg: 'var(--color-accent-2-200)', fg: 'var(--color-accent-2-800)' };
  if (gt) return { t: 'Sync GT', bg: 'var(--color-accent-200)', fg: 'var(--color-accent-800)' };
  if (pole) return { t: 'Sync POLE', bg: 'var(--color-accent-200)', fg: 'var(--color-accent-800)' };
  return { t: 'Not Sync', bg: 'var(--color-danger-bg)', fg: 'var(--color-danger)' };
}
