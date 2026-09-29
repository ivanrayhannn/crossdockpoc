import { useMemo } from 'react';
import { filteredRemainingOrders, plural, visibleCases } from './asnEngine';
import { SUPPLIER_CODE, SUPPLIER_NAME } from './data';
import { AsnDraftPanel } from './components/AsnDraftPanel';
import { CasesPanel } from './components/CasesPanel';
import { RemainingOrdersPanel } from './components/RemainingOrdersPanel';
import { SearchCriteria } from './components/SearchCriteria';
import { Toast } from './components/Toast';
import { useAsnCreation } from './useAsnCreation';

const TABS: [tab: 'cases' | 'rem', label: string][] = [
  ['cases', 'Cases (PO released)'],
  ['rem', 'Customer orders without PO'],
];

export function AsnCreationPage() {
  const state = useAsnCreation();
  const { page, tab, setTab, query, asn, toast } = state;

  const visible = useMemo(() => visibleCases(query, asn), [query, asn]);
  const rem = useMemo(() => filteredRemainingOrders(query), [query]);
  const remQty = rem.reduce((sum, o) => sum + o.qty, 0);
  const counts: Record<'cases' | 'rem', number> = { cases: visible.length, rem: rem.length };

  return (
    <div style={{ padding: '18px 24px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
      {page === 'select' ? (
        <>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
            <div>
              <h1 style={{ fontSize: 22 }}>ASN Creation</h1>
              <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
                Select the cases to ship. All selected cases are grouped into one ASN on the next screen.
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'var(--color-neutral-700)', textAlign: 'right', paddingTop: 2 }}>
              Supplier <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-neutral-800)', fontWeight: 600 }}>{SUPPLIER_CODE}</span> · {SUPPLIER_NAME}
            </div>
          </div>

          <SearchCriteria state={state} />

          <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--color-divider)' }}>
            {TABS.map(([k, label]) => (
              <button
                key={k}
                onClick={() => setTab(k)}
                style={{
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  fontFamily: 'var(--font-body)',
                  fontSize: 13,
                  fontWeight: 600,
                  padding: '9px 14px',
                  marginBottom: -1,
                  background: 'transparent',
                  border: 0,
                  borderBottom: `2px solid ${tab === k ? 'var(--color-accent)' : 'transparent'}`,
                  color: tab === k ? 'var(--color-accent-800)' : 'var(--color-neutral-700)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                {label}
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '0 7px',
                    borderRadius: 999,
                    background: tab === k ? 'var(--color-accent-200)' : k === 'rem' && rem.length ? 'var(--color-warn-bg)' : 'var(--color-neutral-200)',
                    color: tab === k ? 'var(--color-accent-800)' : k === 'rem' && rem.length ? 'var(--color-warn-fg)' : 'var(--color-neutral-700)',
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {counts[k]}
                </span>
              </button>
            ))}
          </div>

          {tab === 'cases' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14, paddingBottom: 28 }}>
              {rem.length > 0 && (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '9px 14px',
                    borderRadius: 6,
                    background: 'var(--color-warn-bg)',
                    border: '1px solid var(--color-neutral-400)',
                    color: 'var(--color-warn-fg)',
                    fontSize: 12.5,
                  }}
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <circle cx="12" cy="12" r="9" />
                    <line x1="12" y1="8" x2="12" y2="13" />
                    <line x1="12" y1="16.5" x2="12" y2="16.5" />
                  </svg>
                  <span>
                    {plural(rem.length, 'customer order')} ({remQty} pcs) in this period have no PO yet, so they are not in the case list.
                  </span>
                  <button
                    onClick={() => setTab('rem')}
                    style={{ marginLeft: 'auto', cursor: 'pointer', border: 0, background: 'transparent', fontFamily: 'var(--font-body)', fontSize: 12.5, fontWeight: 700, color: 'var(--color-accent-700)', textDecoration: 'underline' }}
                  >
                    View customer orders
                  </button>
                </div>
              )}
              <CasesPanel state={state} />
            </div>
          ) : (
            <RemainingOrdersPanel state={state} />
          )}
        </>
      ) : (
        <AsnDraftPanel state={state} />
      )}

      <Toast text={toast} />
    </div>
  );
}
