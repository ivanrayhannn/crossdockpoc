import { useCallback, useState } from 'react';
import { blankPart, cloneSeedParts, CUR_PER } from '../../data/seed';
import { num } from '../../lib/format';
import type { DestAllocation, ModalKind, Part, PartQuery, TabView, UserRole } from '../../types';

const DEFAULT_Q: PartQuery = {
  part: '',
  name: '',
  dest: 'Thailand',
  st: 'all',
  sync: 'all',
  per: CUR_PER,
  sort: 'default',
};

const NOW = '12-Aug-2026 09:30';
const EDITOR = 'D. Anggraini';

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
  const [q, setQ] = useState<PartQuery>(DEFAULT_Q);

  // No auth backend in this build — always full read/write access.
  const ro = false;
  // Sub-menu is a straight function of the chosen role: Procurement only ever
  // sees Daftar Part, D/S only ever sees Mapping per Destinasi.
  const view: TabView = role === 'ds' ? 'dest' : 'part';
  const switchRole = useCallback(() => setRole(null), []);

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
          ? { ...p, dests: draftDests.map((d) => ({ ...d, al: num(d.al) })), by: EDITOR, dt: NOW }
          : p,
      );
    });
    setEditDest(null);
    setDraftDests(null);
  }, [editDest, draftDests]);

  const syncAll = useCallback(() => {
    setParts((prevParts) => prevParts.map((p) => (p.per === CUR_PER ? { ...p, gt: true, pole: true, dt: NOW } : p)));
  }, []);

  const closeModal = useCallback(() => {
    setModal(null);
    setForm(null);
    setEditId(null);
  }, []);

  /** Commits the in-progress form to the parts list and closes the modal. */
  const commit = useCallback(() => {
    if (!form) return;
    const f: Part = { ...form, pc: num(form.pc), mc: num(form.mc), minMad: num(form.minMad), by: EDITOR, dt: NOW };
    setParts((prevParts) => (editId ? prevParts.map((p) => (p.p === editId ? f : p)) : [f, ...prevParts]));
    setModal(null);
    setForm(null);
    setEditId(null);
  }, [form, editId]);

  const addPart = useCallback(() => openFor(null, 'part'), [openFor]);
  const openUpload = useCallback(() => setModal('upload'), []);

  const resetQ = useCallback(() => {
    setQ((prev) => ({ ...DEFAULT_Q, dest: prev.dest || 'Thailand' }));
  }, []);

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
    ro,
    openFor,
    patch,
    toggleExpand,
    startEditDest,
    cancelEditDest,
    patchDraft,
    saveDest,
    syncAll,
    closeModal,
    commit,
    addPart,
    openUpload,
    resetQ,
  };
}

export type CrossdockState = ReturnType<typeof useCrossdockState>;
