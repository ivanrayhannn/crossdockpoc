/** Data of simulasi_asn_rev.xlsx (exported by deliverables/simulasi_asn/export_web.py). mark: 'y' = changed (yellow), 'r' = abnormality (orange). */
export type Mark = 'y' | 'r' | null;
export interface SimRow { cells: string[]; mark: Mark[] }
export interface SimTable { title: string; headers: string[]; rows: SimRow[] }
export interface SimBlock extends SimTable { table: string; kind: 'gsys' | 'rep' }
export interface SimDay { date: string; blocks: SimBlock[] }
export interface SimSearch extends SimTable { date: string }
export interface SimData { intro: string; days: SimDay[]; searches: SimSearch[]; ref: SimTable[]; notes: string[] }
