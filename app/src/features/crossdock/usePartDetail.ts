import { useCallback, useState } from 'react';
import { nowStamp, num } from '../../lib/format';
import type { Part, PartDetail } from '../../types';

const EDITOR = 'D. Anggraini';

/** Dummy TB_M_PART_CROSSDOCK_DTL rows: two out of three registered parts already have a detail record. */
function seedDetails(parts: Part[]): PartDetail[] {
  return parts
    .filter((_, i) => i % 3 !== 2)
    .map((p) => ({ p: p.p, minMad: num(p.minMad) || 100, cd: Math.max(1, Math.round(num(p.mc) * 0.75)), by: p.by, dt: p.dt }));
}

/** CRUD state of the Part Detail sub-menu (TB_M_PART_CROSSDOCK_DTL). */
export function usePartDetail(initialParts: Part[]) {
  const [details, setDetails] = useState<PartDetail[]>(() => seedDetails(initialParts));

  /** Inserts or updates the record of the part; the saved record goes to the top of the list. */
  const saveDetail = useCallback((d: Pick<PartDetail, 'p' | 'minMad' | 'cd'>) => {
    setDetails((prev) => [{ ...d, by: EDITOR, dt: nowStamp() }, ...prev.filter((x) => x.p !== d.p)]);
  }, []);

  const deleteDetail = useCallback((partNo: string) => {
    setDetails((prev) => prev.filter((x) => x.p !== partNo));
  }, []);

  return { details, saveDetail, deleteDetail };
}

export type PartDetailState = ReturnType<typeof usePartDetail>;
