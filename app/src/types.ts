/** Candidate = just registered, no MAD history yet. Active/Inactive are
 * derived from average MAD vs Min MAD once history exists, though the
 * Setting Part form still exposes Status as an editable field. */
export type PartStatus = 'Candidate' | 'Active' | 'Inactive';
export type PartCategory = 'Crossdock' | 'Non-Crossdock';

export interface DestAllocation {
  /** Destination name, e.g. "Thailand". Empty string for a manually-added
   * row where only the destination code (cd) has been typed in. */
  d: string;
  /** Destination code override — used for manually-added rows in the
   * "Mapping per Destinasi" inline editor. */
  cd?: string;
  /** Allocation, case/day. String while an input is mid-edit. */
  al: number | string;
  st: PartStatus;
}

export interface Part {
  /** Part number, e.g. "PART-A". */
  p: string;
  /** Part name. */
  n: string;
  /** Pcs/Case. String while an input is mid-edit. */
  pc: number | string;
  /** Max Case/Day. String while an input is mid-edit. */
  mc: number | string;
  st: PartStatus;
  cat: PartCategory;
  /** MAD (Moving Average Demand) for the last 6 months. */
  mad: number[];
  minMad: number | string;
  by: string;
  dt: string;
  dests: DestAllocation[];
  /** Calculation period this part's mapping belongs to, e.g. "Sep 2026". */
  per: string;
  /** Whether this part's mapping has been synced. */
  synced: boolean;
  /** Date this part's data takes effect. Set from the add/edit form. */
  effDate?: string;
}

export interface PartQuery {
  part: string;
  name: string;
  dest: string;
  st: 'all' | 'active' | 'inactive' | 'candidate';
  sync: 'all' | 'notsync' | 'sync';
  /** Calculation period filter for "Mapping per Destinasi", e.g. "Sep 2026", or 'all'. */
  per: string;
  /** Last Update sort order for Daftar Part. */
  sort: 'default' | 'pn_asc' | 'dt_desc' | 'dt_asc';
}

export type ModalKind = 'part' | 'upload' | 'history' | null;
export type TabView = 'part' | 'dest';
export type UserRole = 'procurement' | 'ds';

export interface HistoryEvent {
  t: string;
  f: string;
  o: string;
  n: string;
  by: string;
  w: string;
  accent?: number;
}
