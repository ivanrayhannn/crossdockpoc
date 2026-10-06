import writeExcelFile from 'write-excel-file/browser';
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

/** Downloads the given Part List rows as .xlsx, with the same columns as the table. */
export async function exportPartsXlsx(rows: Part[]): Promise<void> {
  const d = new Date();
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  await writeExcelFile(rows, {
    columns: [
      { header: { value: 'Part Number', ...HEADER }, cell: (p) => ({ value: p.p }), width: 18 },
      { header: { value: 'Part Name', ...HEADER }, cell: (p) => ({ value: p.n }), width: 32 },
      { header: { value: 'Min MAD', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.minMad), format: NUMBER_FORMAT }), width: 12 },
      { header: { value: 'Pcs/Case', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.pc), format: NUMBER_FORMAT }), width: 12 },
      { header: { value: 'Max Case/Day', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.mc), format: NUMBER_FORMAT }), width: 14 },
      { header: { value: 'Total Pcs/Day', ...HEADER, align: 'right' }, cell: (p) => ({ value: num(p.pc) * num(p.mc), format: NUMBER_FORMAT }), width: 15 },
      { header: { value: 'Status', ...HEADER }, cell: (p) => ({ value: p.st }), width: 12 },
      { header: { value: 'Last Update', ...HEADER }, cell: (p) => ({ value: `${p.dt} · ${p.by}` }), width: 32 },
    ],
  }).toFile(`Crossdock_Part_List_${stamp}.xlsx`);
}
