import { num } from '../../lib/format';
import type { DestAllocation, Part } from '../../types';

/** Sync Status rule of a save (decided 17-Nov, FB-204 / 205): only a change that GTOPAS / AP POLE must receive sets No Sync.
 *  - Status Candidate -> Active, Inactive -> Active, Active -> Inactive: No Sync (Add / Delete in both targets; an Inactive part
 *    with No Sync is taken by the next [Sync]).
 *  - Active part with Pcs/Case or Max Case/Day changed: No Sync (AP POLE Edit; GTOPAS keeps no quantity).
 *  - Min MAD, Effective Start Date, Candidate <-> Inactive, Save without change: Sync Status unchanged (nothing is sent). */
export function syncAfterSave(prev: Part | undefined, next: Part): Part['syncStatus'] {
  if (!prev) return 0;
  const toOrFromActive = prev.st !== next.st && (prev.st === 'Active' || next.st === 'Active');
  const qtyChanged = next.st === 'Active' && (num(prev.pc) !== num(next.pc) || num(prev.mc) !== num(next.mc));
  return toOrFromActive || qtyChanged ? 0 : prev.syncStatus;
}

/** A destination save sets No Sync only when a destination or its Case/Day really changed. */
export function destsChanged(prev: DestAllocation[], next: DestAllocation[]): boolean {
  const key = (ds: DestAllocation[]) => ds.map((d) => `${d.cd || d.d}:${num(d.al)}`).sort().join('|');
  return key(prev) !== key(next);
}
