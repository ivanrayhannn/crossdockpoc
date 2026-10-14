import { useCallback, useState } from 'react';
import { blankPart, cloneSeedParts, CUR_PER } from '../../data/seed';
import { nowStamp, num } from '../../lib/format';
import type { DestAllocation, ModalKind, Part, PartQuery, TabView, UserRole } from '../../types';
import type { CalcRun } from './components/CalcRunBar';

const DEFAULT_Q: PartQuery = {
  part: '',
  name: '',
  dest: 'Thailand',
  st: 'all',
  sync: 'notsync',
  per: CUR_PER,
  sort: 'dt_desc',
};

const EDITOR = 'D. Anggraini';

/** Shown in the success popup after a part is saved from the Add/Edit form, or after an upload is saved. */
export type SaveNotice =
  | { mode: 'add' | 'edit'; part: string; name: string }
  | { mode: 'upload'; target: 'part' | 'mapping' }
  | { mode: 'calc'; target: 'dad' | 'mapping' };

/** Deep-ish clone of a part's destination list, so edits inside a modal/draft
 * never mutate the committed `parts` array until explicitly saved. */
function cloneDests(dests: DestAllocation[]): DestAllocation[] {
  return dests.map((d) => ({ ...d }));
}

export function useCrossdockState() {
  const [parts, setParts] = useState<Part[]>(() => cloneSeedParts());
  const [modal, setModal] = useState<ModalKind>(null);
  const [form, setForm] = useState<Part | null>(null);
  const [editId, setEditId] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [expand, setExpand] = useState<Record<string, boolean>>({});
  const [editDest, setEditDest] = useState<string | null>(null);
  const [draftDests, setDraftDests] = useState<DestAllocation[] | null>(null);
  // q = criteria being typed; aq = criteria applied by [Search]. Lists filter on aq only.
  const [q, setQ] = useState<PartQuery>(DEFAULT_Q);
  const [aq, setAq] = useState<PartQuery>(DEFAULT_Q);
  const [notice, setNotice] = useState<SaveNotice | null>(null);
  // Demo states: the DAD calculation ran fine; the mapping calculation failed 3 scheduled attempts.
  const [dadRun, setDadRun] = useState<CalcRun>({ lastSuccess: '01-Oct-2026 02:00', failedRetries: 0 });
  const [mapRun, setMapRun] = useState<CalcRun>({ lastSuccess: '01-Sep-2026 03:00', failedRetries: 3 });

  // No auth backend in this build — always full read/write access.
  const ro = false;
  // Prototype-only preview switch: the real system opens exactly one sub-menu
  // (Part List or Mapping per Destination) according to the logged-in account.
  const view: TabView = role === 'ds' ? 'dest' : 'part';
  const switchRole = useCallback(() => {
    setRole(null);
  }, []);

  const openFor = useCallback(
    (id: string | null, modalKind: ModalKind, mutate?: (f: Part) => void) => {
      const src = id ? parts.find((p) => p.p === id) : null;
      const f: Part = src ? { ...src, dests: cloneDests(src.dests) } : blankPart();
      if (mutate) mutate(f);
      setForm(f);
      setModal(modalKind);
      setEditId(id);
    },
    [parts],
  );

  const patch = useCallback((fn: (f: Part) => void) => {
    setForm((prev) => {
      if (!prev) return prev;
      const next: Part = { ...prev, dests: cloneDests(prev.dests) };
      fn(next);
      return next;
    });
  }, []);

  const toggleExpand = useCallback(
    (pid: string) => {
      setExpand((prevExpand) => {
        const open = !prevExpand[pid];
        const closingWhileEditing = !open && editDest === pid;
        if (closingWhileEditing) {
          setEditDest(null);
          setDraftDests(null);
        }
        return { ...prevExpand, [pid]: open };
      });
    },
    [editDest],
  );

  const startEditDest = useCallback(
    (pid: string) => {
      const p = parts.find((x) => x.p === pid);
      if (!p) return;
      setExpand((prevExpand) => ({ ...prevExpand, [pid]: true }));
      setEditDest(pid);
      setDraftDests(cloneDests(p.dests));
    },
    [parts],
  );

  const cancelEditDest = useCallback(() => {
    setEditDest(null);
    setDraftDests(null);
  }, []);

  const patchDraft = useCallback((fn: (d: DestAllocation[]) => void) => {
    setDraftDests((prev) => {
      if (!prev) return prev;
      const next = cloneDests(prev);
      fn(next);
      return next;
    });
  }, []);

  const saveDest = useCallback(() => {
    setParts((prevParts) => {
      if (!editDest || !draftDests) return prevParts;
      return prevParts.map((p) =>
        p.p === editDest
          // A mapping edit invalidates whatever was last synced, so it drops back to No Sync.
          ? { ...p, dests: draftDests.map((d) => ({ ...d, al: num(d.al) })), by: EDITOR, dt: nowStamp(), syncStatus: 0 }
          : p,
      );
    });
    setEditDest(null);
    setDraftDests(null);
  }, [editDest, draftDests]);

  // The RPA writes Success / Failed back later; the prototype stops at Waiting.
  const syncParts = useCallback((ids: string[]) => {
    const idSet = new Set(ids);
    setParts((prevParts) => prevParts.map((p) => (idSet.has(p.p) ? { ...p, syncStatus: 3 } : p)));
  }, []);

  const closeModal = useCallback(() => {
    setModal(null);
    setForm(null);
    setEditId(null);
  }, []);

  /** Commits the in-progress form to the parts list and closes the modal. */
  const commit = useCallback(() => {
    if (!form) return;
    // Any change at the part-number level invalidates the current mapping sync.
    const f: Part = { ...form, pc: num(form.pc), mc: num(form.mc), minMad: num(form.minMad), by: EDITOR, dt: nowStamp(), syncStatus: 0 };
    // The saved part goes to the top of the list, whether it was added or edited.
    setParts((prevParts) => [f, ...prevParts.filter((p) => p.p !== f.p)]);
    // Show it right away: drop filters that could hide it and sort newest first.
    const showSaved = (prev: PartQuery): PartQuery => ({ ...prev, part: '', name: '', st: 'all', sort: 'dt_desc' });
    setQ(showSaved);
    setAq(showSaved);
    setNotice({ mode: editId ? 'edit' : 'add', part: f.p, name: f.n });
    setModal(null);
    setForm(null);
    setEditId(null);
  }, [form, editId]);

  const dismissNotice = useCallback(() => setNotice(null), []);

  const addPart = useCallback(() => openFor(null, 'part'), [openFor]);
  const openUpload = useCallback(() => setModal('upload'), []);
  const openMappingUpload = useCallback(() => setModal('upload-mapping'), []);

  /** "Validate file" is the save button of the upload: it closes the modal and confirms the save (OP-02).
   * The prototype does not read the file, so the Part List itself stays unchanged. */
  const submitUpload = useCallback((target: 'part' | 'mapping') => {
    setModal(null);
    setNotice({ mode: 'upload', target });
  }, []);

  /** [Search] applies the criteria; Sort by is not a filter and applies at once (see sortedQ). */
  const runSearch = useCallback(() => setAq(q), [q]);

  /** Manual trigger of a calculation batch (prototype: always succeeds). */
  const runCalc = useCallback((target: 'dad' | 'mapping') => {
    const done: CalcRun = { lastSuccess: nowStamp(), failedRetries: 0 };
    if (target === 'dad') setDadRun(done);
    else setMapRun(done);
    setNotice({ mode: 'calc', target });
  }, []);

  const resetQ = useCallback(() => {
    const reset = (prev: PartQuery): PartQuery => ({ ...DEFAULT_Q, dest: prev.dest || 'Thailand' });
    setQ(reset);
    setAq(reset);
  }, []);

  // Applied filters with the current sort order.
  const sortedQ: PartQuery = { ...aq, sort: q.sort };

  return {
    parts,
    modal,
    form,
    editId,
    role,
    setRole,
    switchRole,
    view,
    expand,
    editDest,
    draftDests,
    q,
    setQ,
    aq: sortedQ,
    runSearch,
    notice,
    dismissNotice,
    dadRun,
    mapRun,
    runCalc,
    ro,
    openFor,
    patch,
    toggleExpand,
    startEditDest,
    cancelEditDest,
    patchDraft,
    saveDest,
    syncParts,
    closeModal,
    commit,
    addPart,
    openUpload,
    openMappingUpload,
    submitUpload,
    resetQ,
  };
}

export type CrossdockState = ReturnType<typeof useCrossdockState>;
