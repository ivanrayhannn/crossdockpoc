export type DestCode = 'VN' | 'JP' | 'TH';

export interface CustomerOrder {
  no: string;
  qty: number;
  /** ISO order date — always PO date − 1 (auto PO releases the day after the order). */
  date: string;
}

export interface AsnCase {
  id: string;
  caseNo: string;
  po: string;
  /** ISO PO date. */
  date: string;
  part: string;
  dest: DestCode;
  qty: number;
  orders: CustomerOrder[];
}

export interface RemainingOrder {
  date: string;
  no: string;
  part: string;
  dest: DestCode;
  qty: number;
  /** 'cap' — bumped by Max Case/Day on an already-released PO; 'next' — PO not released yet. */
  kind: 'cap' | 'next';
  po?: string;
  poDate?: string;
}

export interface AsnQuery {
  from: string;
  to: string;
  sup: string;
  po: string;
  part: string;
  dest: string;
  st: 'all' | 'avail' | 'asn';
}

export type AsnPageView = 'select' | 'draft';
export type AsnTab = 'cases' | 'rem';

export interface SubmittedAsn {
  no: string;
  ids: string[];
  dlv: string;
}
