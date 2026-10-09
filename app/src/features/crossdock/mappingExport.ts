import writeExcelFile from 'write-excel-file/browser';
import { DCODE } from '../../data/seed';
import { num, syncBadge } from '../../lib/format';
import type { Part } from '../../types';

/** One exported line: a part repeated once per mapped destination (or once, blank, when it has none). */
interface MappingLine {
  part: Part;
  dest: Part['dests'][number] | null;
  /** Case/Day allocated across all destinations of the part. */
  allocated: number;
}

const HEADER = { fontWeight: 'bold', backgroundColor: '#e8ecf1' } as const;
const NUMBER_FORMAT = '#,##0';
const PERCENT_FORMAT = '0%';

/** A cell with the value and format, or an empty cell when there is no value. */
const cell = (value: string | number | null | undefined, format?: string) => (value == null || value === '' ? null : { value, format });

/** Downloads the Mapping per Destination rows as .xlsx: the table columns, then the destination mapping of each part. */
export async function exportMappingXlsx(rows: Part[], period: string): Promise<void> {
  const lines = rows.flatMap<MappingLine>((part) => {
    const allocated = part.dests.reduce((sum, d) => sum + num(d.al), 0);
    return part.dests.length ? part.dests.map((dest) => ({ part, dest, allocated })) : [{ part, dest: null, allocated }];
  });
  const share = (n: number, of: number) => (of ? n / of : null);

  const d = new Date();
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  const periodLabel = period === 'all' ? 'All_periods' : period.replace(' ', '_');

  await writeExcelFile(lines, {
    columns: [
      { header: { value: 'Period', ...HEADER }, cell: ({ part }) => cell(part.per), width: 12 },
      { header: { value: 'Part Number', ...HEADER }, cell: ({ part }) => cell(part.p), width: 18 },
      { header: { value: 'Part Name', ...HEADER }, cell: ({ part }) => cell(part.n), width: 30 },
      { header: { value: 'Pcs/Case', ...HEADER, align: 'right' }, cell: ({ part }) => cell(num(part.pc), NUMBER_FORMAT), width: 11 },
      { header: { value: 'Total Case/Day', ...HEADER, align: 'right' }, cell: ({ allocated }) => cell(allocated, NUMBER_FORMAT), width: 16 },
      { header: { value: 'Pcs/Day', ...HEADER, align: 'right' }, cell: ({ part, allocated }) => cell(num(part.pc) * allocated, NUMBER_FORMAT), width: 12 },
      { header: { value: 'Percentage', ...HEADER, align: 'right' }, cell: ({ part, allocated }) => cell(share(allocated, num(part.mc)), PERCENT_FORMAT), width: 12 },
      { header: { value: 'Sync Status', ...HEADER }, cell: ({ part }) => cell(syncBadge(part.syncStatus).t), width: 13 },
      { header: { value: 'Destination Code', ...HEADER }, cell: ({ dest }) => cell(dest && (dest.cd || DCODE[dest.d])), width: 17 },
      { header: { value: 'Destination', ...HEADER }, cell: ({ dest }) => cell(dest?.d), width: 16 },
      { header: { value: 'Dest Case/Day', ...HEADER, align: 'right' }, cell: ({ dest }) => cell(dest && num(dest.al), NUMBER_FORMAT), width: 15 },
      { header: { value: 'Dest Pcs/Day', ...HEADER, align: 'right' }, cell: ({ part, dest }) => cell(dest && num(part.pc) * num(dest.al), NUMBER_FORMAT), width: 14 },
      { header: { value: 'Dest Percentage', ...HEADER, align: 'right' }, cell: ({ dest, allocated }) => cell(dest && share(num(dest.al), allocated), PERCENT_FORMAT), width: 16 },
    ],
  }).toFile(`Crossdock_Mapping_per_Destination_${periodLabel}_${stamp}.xlsx`);
}
