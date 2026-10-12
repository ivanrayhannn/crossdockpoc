import writeExcelFile, { getSheetData, type Column } from 'write-excel-file/browser';
import { num, parseDt } from '../../lib/format';
import type { Part, PartQuery } from '../../types';

/** Rows of the Part List table for a query: filtered, then sorted. Shared by the table and Export Excel. */
export function selectParts(parts: Part[], q: PartQuery): Part[] {
  const part = q.part.toLowerCase();
  const name = q.name.toLowerCase();
  const filtered = parts.filter(
    (p) => (!part || p.p.toLowerCase().includes(part)) && (!name || p.n.toLowerCase().includes(name)) && (q.st === 'all' || p.st.toLowerCase() === q.st),
  );
  if (q.sort === 'default' || q.sort === 'pn_asc') return filtered.sort((a, b) => a.p.localeCompare(b.p));
  if (q.sort === 'dt_desc') return filtered.sort((a, b) => parseDt(b.dt) - parseDt(a.dt));
  if (q.sort === 'dt_asc') return filtered.sort((a, b) => parseDt(a.dt) - parseDt(b.dt));
  return filtered;
}

const HEADER = { fontWeight: 'bold', backgroundColor: '#e8ecf1' } as const;
const NUMBER_FORMAT = '#,##0';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** "2026-06-17" → "17-Jun-2026", the date format of the upload template. */
function uploadDate(iso: string | undefined): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  return m ? `${m[3]}-${MONTHS[Number(m[2]) - 1]}-${m[1]}` : '';
}

/** Sheet 1: the Part List as shown on the screen, plus Effective Start Date. Information only. */
const LIST_COLUMNS: (Column<Part> & { width: number })[] = [
  { header: { value: 'Part Number', ...HEADER }, cell: (p) => ({ value: p.p }), width: 18 },
  { header: { value: 'Part Name', ...HEADER }, cell: (p) => ({ value: p.n }), width: 32 },
  { header: { value: 'Min MAD', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.minMad), format: NUMBER_FORMAT }), width: 12 },
  { header: { value: 'Pcs/Case', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.pc), format: NUMBER_FORMAT }), width: 12 },
  { header: { value: 'Max Case/Day', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.mc), format: NUMBER_FORMAT }), width: 14 },
  { header: { value: 'Total Pcs/Day', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.pc) * num(p.mc), format: NUMBER_FORMAT }), width: 15 },
  { header: { value: 'Status', ...HEADER }, cell: (p) => ({ value: p.st }), width: 12 },
  { header: { value: 'Effective Start Date', ...HEADER }, cell: (p) => ({ value: uploadDate(p.effDate) }), width: 20 },
  { header: { value: 'Last Update', ...HEADER }, cell: (p) => ({ value: `${p.dt} · ${p.by}` }), width: 32 },
];

/** Sheet 2 "Upload": the upload template (column order of FSD Crossdock Upload Batch) pre-filled with current values (flag E), the base file for Edit uploads. */
const UPLOAD_COLUMNS: (Column<Part> & { width: number })[] = [
  { header: { value: 'part_no', ...HEADER }, cell: (p) => ({ value: p.p }), width: 18 },
  { header: { value: 'minimum_mad', ...HEADER }, cell: (p) => ({ value: num(p.minMad) }), width: 14 },
  { header: { value: 'pcs_case', ...HEADER }, cell: (p) => ({ value: num(p.pc) }), width: 11 },
  { header: { value: 'max_case_day', ...HEADER }, cell: (p) => ({ value: num(p.mc) }), width: 14 },
  { header: { value: 'status', ...HEADER }, cell: (p) => ({ value: p.st }), width: 12 },
  { header: { value: 'flag_add_edit', ...HEADER }, cell: () => ({ value: 'E' }), width: 14 },
  { header: { value: 'effective_start_date', ...HEADER }, cell: (p) => ({ value: uploadDate(p.effDate) }), width: 20 },
];

/**
 * Downloads the Part List as .xlsx: sheet 1 holds the rows of the active filter (information only),
 * sheet "Upload" holds every registered part in the upload template, ready to edit and upload again.
 */
export async function exportPartsXlsx(rows: Part[], allParts: Part[]): Promise<void> {
  const d = new Date();
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  const uploadRows = [...allParts].sort((a, b) => a.p.localeCompare(b.p));
  await writeExcelFile([
    { sheet: 'Part List', data: getSheetData(rows, LIST_COLUMNS), columns: LIST_COLUMNS.map((c) => ({ width: c.width })) },
    { sheet: 'Upload', data: getSheetData(uploadRows, UPLOAD_COLUMNS), columns: UPLOAD_COLUMNS.map((c) => ({ width: c.width })) },
  ]).toFile(`Crossdock_Part_List_${stamp}.xlsx`);
}
