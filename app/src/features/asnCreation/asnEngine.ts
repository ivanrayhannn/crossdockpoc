import { addDaysIso, CASES, DEST_LABEL, niceDate, REMAINING_ORDERS, SUPPLIER_CODE } from './data';
import type { AsnCase, AsnQuery, RemainingOrder } from './types';

export function plural(n: number, word: string): string {
  return `${n} ${word}${n === 1 ? '' : 's'}`;
}

export function orderSummary(c: AsnCase): string {
  return c.orders.map((o) => `${o.no} (${o.qty})`).join(', ');
}

export function sumQty(cases: AsnCase[]): number {
  return cases.reduce((sum, c) => sum + c.qty, 0);
}

export function uniqueBy<K extends keyof AsnCase>(cases: AsnCase[], key: K): AsnCase[K][] {
  return [...new Set(cases.map((c) => c[key]))];
}

/** Cases matching the applied search criteria — the Cases (PO released) tab. */
export function visibleCases(query: AsnQuery, asn: Record<string, string>): AsnCase[] {
  return CASES.filter(
    (c) =>
      query.sup === SUPPLIER_CODE &&
      c.date >= query.from &&
      c.date <= query.to &&
      (!query.po || c.po.toLowerCase().includes(query.po.trim().toLowerCase())) &&
      (query.part === 'all' || c.part === query.part) &&
      (query.dest === 'all' || c.dest === query.dest) &&
      (query.st === 'all' || (query.st === 'asn' ? !!asn[c.id] : !asn[c.id])),
  );
}

/** Customer orders without a PO yet, within the same window — ignores the PO Number filter
 * since these rows have no PO to match against. */
export function filteredRemainingOrders(query: AsnQuery): RemainingOrder[] {
  const from = addDaysIso(query.from, -1);
  return REMAINING_ORDERS.filter(
    (o) =>
      query.sup === SUPPLIER_CODE &&
      !query.po &&
      o.date >= from &&
      o.date <= query.to &&
      (query.part === 'all' || o.part === query.part) &&
      (query.dest === 'all' || o.dest === query.dest),
  );
}

export interface CaseRowView {
  case: AsnCase;
  checked: boolean;
  locked: boolean;
  expanded: boolean;
  status: string;
  statusBg: string;
  statusFg: string;
  rowBg: string;
  accentBd: string;
  textFg: string;
}

export interface PoGroupView {
  po: string;
  date: string;
  meta: string;
  selectedText: string;
  allChecked: boolean;
  toggleDisabled: boolean;
  availableIds: string[];
  rows: CaseRowView[];
}

/** Groups the visible cases by PO for the selection table, each PO acting as a "select all" row. */
export function groupCasesByPo(cases: AsnCase[], asn: Record<string, string>, sel: Record<string, boolean>, exp: Record<string, boolean>): PoGroupView[] {
  const pos = uniqueBy(cases, 'po');
  return pos.map((po) => {
    const inPo = cases.filter((c) => c.po === po);
    const available = inPo.filter((c) => !asn[c.id]);
    const nSelected = available.filter((c) => sel[c.id]).length;
    const allChecked = available.length > 0 && nSelected === available.length;
    const lockedCount = inPo.length - available.length;

    return {
      po,
      date: niceDate(inPo[0].date),
      meta: `${plural(inPo.length, 'case')} · ${sumQty(inPo)} pcs${lockedCount ? ` · ${lockedCount} in ASN` : ''}`,
      selectedText: nSelected ? `${nSelected} of ${available.length} selected` : '',
      allChecked,
      toggleDisabled: !available.length,
      availableIds: available.map((c) => c.id),
      rows: inPo.map((c): CaseRowView => {
        const locked = !!asn[c.id];
        const on = !!sel[c.id];
        return {
          case: c,
          checked: on || locked,
          locked,
          expanded: !!exp[c.id],
          status: locked ? `In ${asn[c.id]}` : on ? 'Selected' : 'Not in ASN',
          statusBg: locked ? 'var(--color-accent-2-200)' : on ? 'var(--color-accent-200)' : 'var(--color-neutral-200)',
          statusFg: locked ? 'var(--color-accent-2-800)' : on ? 'var(--color-accent-800)' : 'var(--color-neutral-700)',
          rowBg: on ? 'var(--color-accent-100)' : '#fff',
          accentBd: on ? 'var(--color-accent)' : 'transparent',
          textFg: locked ? 'var(--color-neutral-600)' : 'var(--color-text)',
        };
      }),
    };
  });
}

export interface PartGroupView {
  part: string;
  meta: string;
  rows: AsnCase[];
}

/** Groups the draft/submitted cases by part number for the ASN detail table. */
export function groupCasesByPart(cases: AsnCase[]): PartGroupView[] {
  const parts = uniqueBy(cases, 'part').sort();
  return parts.map((part) => {
    const rows = cases.filter((c) => c.part === part);
    return { part, meta: `${plural(rows.length, 'case')} · ${sumQty(rows)} pcs`, rows };
  });
}

export function destLabel(dest: AsnCase['dest']): string {
  return DEST_LABEL[dest];
}

export function remainingStatus(o: RemainingOrder): { label: string; bg: string; fg: string; reason: string } {
  if (o.kind === 'cap') {
    return {
      label: 'Waiting next PO',
      bg: 'var(--color-warn-bg)',
      fg: 'var(--color-warn-fg)',
      reason: `Max Case/Day was reached on ${o.po} (${niceDate(o.poDate ?? o.date)}). Goes first into the next PO, or a manual PO.`,
    };
  }
  return {
    label: 'PO not released yet',
    bg: 'var(--color-neutral-200)',
    fg: 'var(--color-neutral-700)',
    reason: `Auto PO releases on ${niceDate(addDaysIso(o.date, 1))} (Order Date + 1).`,
  };
}
