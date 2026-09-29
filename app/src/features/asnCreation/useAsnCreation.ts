import { useCallback, useEffect, useRef, useState } from 'react';
import { CASES, DEFAULT_DELIVERY_DATE, DEFAULT_QUERY, PRE_EXISTING_ASN } from './data';
import type { AsnPageView, AsnQuery, AsnTab, SubmittedAsn } from './types';

const ASN_NO = 'ASN-50221-260929-001';

export function useAsnCreation() {
  const [page, setPage] = useState<AsnPageView>('select');
  const [tab, setTab] = useState<AsnTab>('cases');
  const [filter, setFilter] = useState<AsnQuery>(DEFAULT_QUERY);
  const [query, setQuery] = useState<AsnQuery>(DEFAULT_QUERY);
  const [sel, setSel] = useState<Record<string, boolean>>({});
  const [exp, setExp] = useState<Record<string, boolean>>({});
  const [asn, setAsn] = useState<Record<string, string>>(PRE_EXISTING_ASN);
  const [dlv, setDlv] = useState(DEFAULT_DELIVERY_DATE);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [done, setDone] = useState<SubmittedAsn | null>(null);
  const [toast, setToast] = useState('');
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => { if (toastTimer.current) clearTimeout(toastTimer.current); }, []);

  const flash = useCallback((text: string) => {
    if (toastTimer.current) clearTimeout(toastTimer.current);
    setToast(text);
    toastTimer.current = setTimeout(() => setToast(''), 2200);
  }, []);

  const setFilterField = useCallback(<K extends keyof AsnQuery>(key: K, value: AsnQuery[K]) => {
    setFilter((prev) => ({ ...prev, [key]: value }));
  }, []);

  const search = useCallback(() => setQuery(filter), [filter]);
  const resetFilter = useCallback(() => {
    setFilter(DEFAULT_QUERY);
    setQuery(DEFAULT_QUERY);
  }, []);

  const toggleCase = useCallback((id: string) => {
    setSel((prev) => {
      const next = { ...prev };
      if (next[id]) delete next[id];
      else next[id] = true;
      return next;
    });
  }, []);

  const toggleCases = useCallback((ids: string[], select: boolean) => {
    setSel((prev) => {
      const next = { ...prev };
      ids.forEach((id) => {
        if (select) next[id] = true;
        else delete next[id];
      });
      return next;
    });
  }, []);

  const toggleExpand = useCallback((id: string) => {
    setExp((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const clearSelection = useCallback(() => setSel({}), []);

  const goToDraft = useCallback(() => {
    window.scrollTo(0, 0);
    setPage('draft');
  }, []);

  const goToSelect = useCallback(() => {
    window.scrollTo(0, 0);
    setPage('select');
  }, []);

  /** Discards the submitted ASN and returns to a blank selection screen, ready for a new ASN. */
  const startNewAsn = useCallback(() => {
    window.scrollTo(0, 0);
    setDone(null);
    setSel({});
    setDlv(DEFAULT_DELIVERY_DATE);
    setFilter(DEFAULT_QUERY);
    setQuery(DEFAULT_QUERY);
    setTab('cases');
    setPage('select');
  }, []);

  const backToList = useCallback(() => {
    if (done) startNewAsn();
    else goToSelect();
  }, [done, goToSelect, startNewAsn]);

  const removeFromDraft = useCallback(
    (id: string) => {
      toggleCase(id);
    },
    [toggleCase],
  );

  const openConfirm = useCallback(() => setConfirmOpen(true), []);
  const closeConfirm = useCallback(() => setConfirmOpen(false), []);

  const submitAsn = useCallback(() => {
    const ids = Object.keys(sel);
    setAsn((prev) => {
      const next = { ...prev };
      ids.forEach((id) => {
        next[id] = ASN_NO;
      });
      return next;
    });
    setDone({ no: ASN_NO, ids, dlv });
    setSel({});
    setConfirmOpen(false);
  }, [dlv, sel]);

  const downloadCaseLabel = useCallback((caseNo: string) => flash(`Case label ${caseNo}.pdf downloaded`), [flash]);
  const downloadAllLabels = useCallback(
    (count: number) => flash(`${done ? done.no : ASN_NO}_case_labels.pdf downloaded (${count} labels)`),
    [done, flash],
  );

  return {
    page,
    tab,
    setTab,
    filter,
    query,
    sel,
    exp,
    asn,
    dlv,
    setDlv,
    confirmOpen,
    done,
    toast,
    cases: CASES,
    setFilterField,
    search,
    resetFilter,
    toggleCase,
    toggleCases,
    toggleExpand,
    clearSelection,
    goToDraft,
    goToSelect,
    backToList,
    removeFromDraft,
    openConfirm,
    closeConfirm,
    submitAsn,
    downloadCaseLabel,
    downloadAllLabels,
  };
}

export type AsnCreationState = ReturnType<typeof useAsnCreation>;
