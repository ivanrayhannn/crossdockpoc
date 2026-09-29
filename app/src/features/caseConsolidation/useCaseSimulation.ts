import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { buildModel, presetInputs } from './simulation';
import type { Order, PresetKey, SimInputs } from './simulation';
import { EMPTY_QUERY } from './deliveryPlan';
import type { DpQuery } from './deliveryPlan';

export type ViewKey = 'dp' | 'sim';
export type SimulationRole = 'sup' | 'ds' | 'proc';

const STEP_MS = 240;

export function useCaseSimulation() {
  const [inputs, setInputs] = useState<SimInputs>(() => presetInputs('a'));
  const [part, setPart] = useState('Part 2');
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [view, setView] = useState<ViewKey>('dp');
  const [role, setRole] = useState<SimulationRole>('sup');
  const [nextId, setNextId] = useState(() => presetInputs('a').orders.length + 1);

  // Delivery Plan navigation/filter state.
  const [dpPage, setDpPage] = useState<'list' | 'detail'>('list');
  const [dpFilter, setDpFilter] = useState<DpQuery>(EMPTY_QUERY);
  const [dpQuery, setDpQuery] = useState<DpQuery | null>(null);
  const [dpSel, setDpSel] = useState<string | null>(null);
  const [dpVariable, setDpVariable] = useState<string | null>(null);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
  }, []);
  useEffect(() => stop, [stop]);

  const model = useMemo(() => buildModel(inputs), [inputs]);
  const placed = Math.min(step, model.rel);
  const done = placed >= model.rel;

  /** Reset the simulation playhead whenever the inputs (orders/pcs/capacity) change. */
  const edit = useCallback(
    (fn: (s: SimInputs) => SimInputs) => {
      stop();
      setPlaying(false);
      setStep(0);
      setInputs(fn);
    },
    [stop],
  );

  const applyPreset = useCallback(
    (k: PresetKey) => {
      const next = presetInputs(k);
      edit(() => next);
      setNextId(next.orders.length + 1);
    },
    [edit],
  );

  const reset = useCallback(() => edit((s) => presetInputs(s.preset)), [edit]);

  const setPcs = useCallback((fn: (n: number) => number) => edit((s) => ({ ...s, pcs: Math.max(2, Math.min(12, fn(s.pcs))) })), [edit]);
  const setMaxC = useCallback((fn: (n: number) => number) => edit((s) => ({ ...s, maxC: Math.max(1, Math.min(6, fn(s.maxC))) })), [edit]);

  const updateOrder = useCallback(
    (id: number, fn: (o: Order) => Order) => edit((s) => ({ ...s, orders: s.orders.map((o) => (o.id === id ? fn(o) : o)) })),
    [edit],
  );
  const removeOrder = useCallback((id: number) => edit((s) => ({ ...s, orders: s.orders.filter((o) => o.id !== id) })), [edit]);
  const addOrder = useCallback(() => {
    edit((s) => {
      const last = [...s.orders].sort((a, b) => (a.date < b.date ? -1 : 1)).pop();
      const id = nextId;
      const order: Order = { id, no: `Order ${id}`, date: last ? addDayIso(last.date) : '2026-09-15', dest: 'VN', qty: s.pcs };
      return { ...s, orders: [...s.orders, order] };
    });
    setNextId((n) => n + 1);
  }, [edit, nextId]);

  const stepOne = useCallback(() => setStep((n) => Math.min(model.rel, n + 1)), [model.rel]);
  const fillAll = useCallback(() => {
    stop();
    setPlaying(false);
    setStep(model.rel);
  }, [model.rel, stop]);

  const togglePlay = useCallback(() => {
    if (playing) {
      stop();
      setPlaying(false);
      return;
    }
    setPlaying(true);
    timerRef.current = setInterval(() => {
      setStep((n) => {
        if (n >= model.rel) {
          stop();
          setPlaying(false);
          return n;
        }
        return n + 1;
      });
    }, STEP_MS);
  }, [model.rel, playing, stop]);

  const dpSearch = useCallback(() => {
    setDpQuery({ ...dpFilter });
    setDpSel(null);
    setDpVariable(null);
    setDpPage('list');
  }, [dpFilter]);
  const dpReset = useCallback(() => {
    setDpQuery(null);
    setDpFilter(EMPTY_QUERY);
    setDpSel(null);
    setDpVariable(null);
    setDpPage('list');
  }, []);
  const dpSelect = useCallback((key: string) => {
    setDpSel(key);
    setDpVariable(null);
    setDpPage('detail');
  }, []);
  const dpBack = useCallback(() => {
    setDpPage('list');
    setDpVariable(null);
  }, []);
  const dpToggleVariable = useCallback((v: string) => setDpVariable((cur) => (cur === v ? null : v)), []);
  const dpClearVariable = useCallback(() => setDpVariable(null), []);

  return {
    inputs,
    part,
    setPart,
    model,
    step,
    placed,
    done,
    playing,
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
    dpQuery: dpQuery ?? EMPTY_QUERY,
    dpSel,
    dpVariable,
    dpSearch,
    dpReset,
    dpSelect,
    dpBack,
    dpToggleVariable,
    dpClearVariable,
  };
}

function addDayIso(iso: string) {
  const t = new Date(`${iso}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() + 1);
  return t.toISOString().slice(0, 10);
}

export type CaseSimulationState = ReturnType<typeof useCaseSimulation>;
