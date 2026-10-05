import { useCallback, useEffect, useMemo, useState } from 'react';
import { addDay, asnNoFor, buildModel, buildSequences, presetInputs } from './simulation';
import type { Order, PresetKey, SimInputs } from './simulation';
import { EMPTY_QUERY } from './deliveryPlan';
import type { DpQuery } from './deliveryPlan';
import { ritsFor } from './rit';
import type { Rit } from './rit';

export type ViewKey = 'dp' | 'sim' | 'asn';
export type SimulationRole = 'sup' | 'ds' | 'proc';

const STEP_MS = 240;

export function useCaseSimulation() {
  const [inputs, setInputs] = useState<SimInputs>(() => presetInputs('c'));
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [view, setView] = useState<ViewKey>('dp');
  // Case selection and ASN grouping are the Demand Supply workflow shown by default.
  const [role, setRole] = useState<SimulationRole>('ds');

  // Delivery Plan navigation/filter state.
  const [dpPage, setDpPage] = useState<'list' | 'detail'>('list');
  const [dpFilter, setDpFilter] = useState<DpQuery>(EMPTY_QUERY);
  const [dpQuery, setDpQuery] = useState<DpQuery>(EMPTY_QUERY);
  const [dpSel, setDpSel] = useState<string | null>(null);

  // ASN draft state is intentionally kept in this simulation so users can
  // group cases directly from a delivery-plan detail.
  const [asnSelection, setAsnSelection] = useState<Record<string, boolean>>({});
  const [asnByCase, setAsnByCase] = useState<Record<string, string>>({});
  const [asnDeliveryDate, setAsnDeliveryDate] = useState(defaultDeliveryDate);
  const [asnRitNo, setAsnRit] = useState('');
  const [submittedAsn, setSubmittedAsn] = useState<{ no: string; ids: string[]; deliveryDate: string; rit: Rit } | null>(null);
  // Rits depend on the chosen delivery date; the first one is picked until the user chooses another.
  const asnRits = useMemo(() => ritsFor(asnDeliveryDate), [asnDeliveryDate]);
  const asnRit = asnRits.find((r) => r.no === asnRitNo) ?? asnRits[0];

  const model = useMemo(() => buildModel(inputs), [inputs]);
  const sequences = useMemo(() => buildSequences(model), [model]);
  const sequenceOfCase = useMemo(() => new Map(sequences.flatMap((q) => q.caseNos.map((id) => [id, q] as const))), [sequences]);
  const placed = Math.min(step, model.rel);
  const done = placed >= model.rel;
  // The timer stops by itself once everything is placed.
  const running = playing && !done;
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => setStep((n) => n + 1), STEP_MS);
    return () => clearInterval(timer);
  }, [running]);

  /**
   * Every input change (orders/pcs/capacity/preset) rebuilds the cases, and case numbers are just
   * their position, so the playhead and everything derived from old case numbers (Delivery Plan
   * selection, ASN draft, submitted ASNs) are reset together.
   */
  const edit = useCallback((fn: (s: SimInputs) => SimInputs) => {
    setPlaying(false);
    setStep(0);
    setInputs(fn);
    setDpSel(null);
    setDpPage('list');
    setAsnSelection({});
    setAsnByCase({});
    setSubmittedAsn(null);
    setView((v) => (v === 'asn' ? 'dp' : v));
  }, []);

  const applyPreset = useCallback((k: PresetKey) => edit(() => presetInputs(k)), [edit]);

  const reset = useCallback(() => edit((s) => presetInputs(s.preset)), [edit]);

  const setPcs = useCallback((fn: (n: number) => number) => edit((s) => ({ ...s, pcs: Math.max(2, Math.min(12, fn(s.pcs))) })), [edit]);
  const setMaxC = useCallback((fn: (n: number) => number) => edit((s) => ({ ...s, maxC: Math.max(1, Math.min(6, fn(s.maxC))) })), [edit]);

  const updateOrder = useCallback(
    (id: number, fn: (o: Order) => Order) => edit((s) => ({ ...s, orders: s.orders.map((o) => (o.id === id ? fn(o) : o)) })),
    [edit],
  );
  const removeOrder = useCallback((id: number) => edit((s) => ({ ...s, orders: s.orders.filter((o) => o.id !== id) })), [edit]);
  const addOrder = useCallback(
    () =>
      edit((s) => {
        const lastDate = s.orders.reduce((max, o) => (o.date > max ? o.date : max), '');
        const id = Math.max(0, ...s.orders.map((o) => o.id)) + 1;
        const order: Order = { id, no: `Order ${id}`, date: lastDate ? addDay(lastDate) : '2026-09-15', dest: 'VN', qty: s.pcs, part: `Part ${String(id).padStart(3, '0')}` };
        return { ...s, orders: [...s.orders, order] };
      }),
    [edit],
  );

  const stepOne = useCallback(() => setStep((n) => Math.min(model.rel, n + 1)), [model.rel]);
  const fillAll = useCallback(() => {
    setPlaying(false);
    setStep(model.rel);
  }, [model.rel]);
  const togglePlay = useCallback(() => setPlaying((p) => !p), []);

  const dpSearch = useCallback(() => {
    setDpQuery({ ...dpFilter });
    setDpSel(null);
    setDpPage('list');
  }, [dpFilter]);
  const dpReset = useCallback(() => {
    setDpQuery(EMPTY_QUERY);
    setDpFilter(EMPTY_QUERY);
    setDpSel(null);
    setDpPage('list');
  }, []);
  const dpSelect = useCallback((key: string) => {
    setDpSel(key);
    setDpPage('detail');
  }, []);
  const dpBack = useCallback(() => setDpPage('list'), []);

  /**
   * One ASN holds exactly one Customer Order Date. Ticking a date selects every case of it
   * (in all its POs); unticking clears the selection.
   */
  const toggleAsnDate = useCallback(
    (od: string) => {
      const q = sequences.find((x) => x.od === od);
      if (!q?.complete || q.caseNos.every((id) => asnByCase[id])) return;
      setAsnSelection((prev) => (q.caseNos.every((id) => prev[id]) ? {} : Object.fromEntries(q.caseNos.map((n) => [n, true]))));
    },
    [asnByCase, sequences],
  );
  const clearAsnSelection = useCallback(() => setAsnSelection({}), []);
  const openAsnDraft = useCallback(() => {
    if (!Object.keys(asnSelection).length) return;
    window.scrollTo(0, 0);
    setSubmittedAsn(null);
    setView('asn');
  }, [asnSelection]);
  const backToDeliveryPlan = useCallback(() => {
    window.scrollTo(0, 0);
    setView('dp');
    setDpPage('list');
  }, []);
  const submitAsn = useCallback(() => {
    const ids = Object.keys(asnSelection);
    const q = ids.length ? sequenceOfCase.get(ids[0]) : undefined;
    // The whole order date must go in one ASN: reject partial or mixed selections.
    if (!q?.complete || ids.length !== q.caseNos.length || !q.caseNos.every((id) => asnSelection[id]) || !asnDeliveryDate || !asnRit) return;
    const no = asnNoFor(asnDeliveryDate);
    setAsnByCase((prev) => ({ ...prev, ...Object.fromEntries(ids.map((id) => [id, no])) }));
    setSubmittedAsn({ no, ids, deliveryDate: asnDeliveryDate, rit: asnRit });
    setAsnSelection({});
  }, [asnDeliveryDate, asnRit, asnSelection, sequenceOfCase]);

  return {
    inputs,
    model,
    sequences,
    sequenceOfCase,
    step,
    placed,
    done,
    playing: running,
    view,
    setView,
    role,
    setRole,
    applyPreset,
    reset,
    setPcs,
    setMaxC,
    updateOrder,
    removeOrder,
    addOrder,
    stepOne,
    fillAll,
    togglePlay,
    dpPage,
    dpFilter,
    setDpFilter,
    dpQuery,
    dpSel,
    dpSearch,
    dpReset,
    dpSelect,
    dpBack,
    asnSelection,
    asnByCase,
    asnDeliveryDate,
    asnRits,
    asnRit,
    setAsnRit,
    setAsnDeliveryDate,
    submittedAsn,
    toggleAsnDate,
    clearAsnSelection,
    openAsnDraft,
    backToDeliveryPlan,
    submitAsn,
  };
}

/** Tomorrow in the user's local time (toISOString would shift it by the UTC offset). */
function defaultDeliveryDate() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export type CaseSimulationState = ReturnType<typeof useCaseSimulation>;
