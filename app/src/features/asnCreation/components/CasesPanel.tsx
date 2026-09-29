import { useMemo } from 'react';
import { destLabel, groupCasesByPo, orderSummary, plural, sumQty, uniqueBy, visibleCases } from '../asnEngine';
import { niceDate } from '../data';
import type { AsnCreationState } from '../useAsnCreation';

const th: React.CSSProperties = {
  textAlign: 'left',
  padding: '8px 12px',
  fontSize: 10.5,
  letterSpacing: '.05em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  borderBottom: '1px solid #e3e6ea',
};
export function CasesPanel({ state }: { state: AsnCreationState }) {
  const { query, sel, exp, asn, cases, toggleCase, toggleCases, toggleExpand, clearSelection, goToDraft } = state;

  const visible = useMemo(() => visibleCases(query, asn), [query, asn]);
  const groups = useMemo(() => groupCasesByPo(visible, asn, sel, exp), [visible, asn, sel, exp]);
  const selectedCases = useMemo(() => cases.filter((c) => sel[c.id]), [cases, sel]);

  if (!visible.length) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 6, padding: '52px 20px', background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6 }}>
        <h3 style={{ fontSize: 16 }}>No cases match this filter</h3>
        <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: 0 }}>Change the delivery plan dates or reset the filter.</p>
        <button className="btn btn-secondary" onClick={state.resetFilter} style={{ marginTop: 8 }}>
          Reset filter
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea' }}>
          <span style={{ fontSize: 14, fontWeight: 700 }}>Cases</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>
            {plural(uniqueBy(visible, 'po').length, 'PO')} · {plural(visible.length, 'case')} · {niceDate(query.from)} – {niceDate(query.to)}
          </span>
          <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 14, fontSize: 12, color: 'var(--color-neutral-700)' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 8, height: 8, borderRadius: 999, background: 'var(--color-accent)' }} />
              Not in ASN · selectable
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 8, height: 8, borderRadius: 999, background: 'var(--color-accent-2-800)' }} />
              In ASN · locked
            </span>
          </span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'var(--color-surface)' }}>
              <th style={{ width: 46, borderBottom: '1px solid #e3e6ea' }} />
              <th style={{ width: 34, borderBottom: '1px solid #e3e6ea' }} />
              <th style={{ ...th, width: 120 }}>Case No</th>
              <th style={{ ...th, width: 90 }}>Part No</th>
              <th style={{ ...th, width: 150 }}>Destination</th>
              <th style={{ ...th, width: 70, textAlign: 'right' }}>Qty</th>
              <th style={th}>Customer Orders</th>
              <th style={{ ...th, width: 230, paddingRight: 16 }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {groups.map((g) => (
              <PoGroupRows key={g.po} group={g} onToggleAll={() => toggleCases(g.availableIds, !g.allChecked)} onToggle={toggleCase} onExpand={toggleExpand} />
            ))}
          </tbody>
        </table>
      </div>

      <div
        style={{
          position: 'sticky',
          bottom: 0,
          zIndex: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          padding: '12px 16px',
          margin: '0 -24px',
          background: '#fff',
          borderTop: '1px solid #e3e6ea',
          boxShadow: '0 -6px 18px rgba(20,40,70,.08)',
        }}
      >
        <span
          style={{
            display: 'inline-grid',
            placeItems: 'center',
            minWidth: 30,
            height: 30,
            padding: '0 8px',
            borderRadius: 999,
            background: selectedCases.length ? 'var(--color-accent)' : 'var(--color-neutral-200)',
            color: selectedCases.length ? '#fff' : 'var(--color-neutral-600)',
            fontWeight: 700,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {selectedCases.length}
        </span>
        <span style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.3 }}>
          <span style={{ fontSize: 13.5, fontWeight: 700 }}>
            {selectedCases.length ? `${plural(selectedCases.length, 'case')} selected · ${sumQty(selectedCases)} pcs` : 'No case selected'}
          </span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>
            {selectedCases.length ? `${plural(uniqueBy(selectedCases, 'part').length, 'part')} · ${uniqueBy(selectedCases, 'po').join(', ')}` : 'Tick cases or a whole PO. Cases already in an ASN are locked.'}
          </span>
        </span>
        <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary" onClick={clearSelection} disabled={!selectedCases.length}>
            Clear selection
          </button>
          <button className="btn btn-primary" onClick={goToDraft} disabled={!selectedCases.length}>
            Group into 1 ASN
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 6 15 12 9 18" />
            </svg>
          </button>
        </span>
      </div>
    </div>
  );
}

function PoGroupRows({
  group,
  onToggleAll,
  onToggle,
  onExpand,
}: {
  group: ReturnType<typeof groupCasesByPo>[number];
  onToggleAll: () => void;
  onToggle: (id: string) => void;
  onExpand: (id: string) => void;
}) {
  return (
    <>
      <tr style={{ background: 'var(--color-surface)' }}>
        <td onClick={onToggleAll} style={{ padding: '0 0 0 16px', height: 38, borderBottom: '1px solid #e3e6ea', cursor: group.toggleDisabled ? 'default' : 'pointer' }}>
          <input type="checkbox" checked={group.allChecked} disabled={group.toggleDisabled} readOnly style={{ pointerEvents: 'none' }} />
        </td>
        <td colSpan={7} style={{ padding: '0 16px 0 0', borderBottom: '1px solid #e3e6ea' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent-800)' }}>{group.po}</span>
            <span style={{ fontSize: 12.5, fontWeight: 600 }}>PO Date {group.date}</span>
            <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>{group.meta}</span>
            <span style={{ marginLeft: 'auto', fontSize: 12, fontWeight: 600, color: 'var(--color-accent-700)' }}>{group.selectedText}</span>
          </span>
        </td>
      </tr>
      {group.rows.map((r) => (
        <CaseRow key={r.case.id} row={r} onToggle={() => onToggle(r.case.id)} onExpand={() => onExpand(r.case.id)} />
      ))}
    </>
  );
}

function CaseRow({ row, onToggle, onExpand }: { row: ReturnType<typeof groupCasesByPo>[number]['rows'][number]; onToggle: () => void; onExpand: () => void }) {
  const c = row.case;
  return (
    <>
      <tr className={row.locked ? undefined : 'row-hover'} style={{ cursor: row.locked ? 'default' : 'pointer', background: row.rowBg }} onClick={() => !row.locked && onToggle()}>
        <td style={{ padding: '0 0 0 16px', height: 42, borderBottom: '1px solid #eef1f5', borderLeft: `3px solid ${row.accentBd}` }}>
          <input type="checkbox" checked={row.checked} disabled={row.locked} readOnly style={{ pointerEvents: 'none' }} />
        </td>
        <td style={{ borderBottom: '1px solid #eef1f5' }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onExpand();
            }}
            title="Customer orders in this case"
            className="icon-btn-hover"
            style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 22, height: 22, display: 'grid', placeItems: 'center', borderRadius: 4, color: 'var(--color-neutral-700)' }}
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              style={{ transform: `rotate(${row.expanded ? 90 : 0}deg)`, transition: 'transform .12s' }}
            >
              <polyline points="9 6 15 12 9 18" />
            </svg>
          </button>
        </td>
        <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', fontFamily: 'var(--font-mono)', fontWeight: 600, color: row.textFg }}>{c.caseNo}</td>
        <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', fontWeight: 600, color: row.textFg }}>{c.part}</td>
        <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', color: row.textFg }}>{destLabel(c.dest)}</td>
        <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700, color: row.textFg }}>{c.qty}</td>
        <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', fontSize: 12.5, color: 'var(--color-neutral-700)' }}>{orderSummary(c)}</td>
        <td style={{ padding: '0 16px 0 12px', borderBottom: '1px solid #eef1f5' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11.5, fontWeight: 700, padding: '2px 10px', borderRadius: 999, background: row.statusBg, color: row.statusFg, whiteSpace: 'nowrap' }}>
            {row.status}
          </span>
        </td>
      </tr>
      {row.expanded && (
        <tr>
          <td colSpan={8} style={{ padding: '4px 16px 12px 96px', borderBottom: '1px solid #e3e6ea', background: 'var(--color-accent-100)' }}>
            <table style={{ width: '100%', maxWidth: 640, borderCollapse: 'collapse', fontSize: 12.5, background: '#fff', border: '1px solid var(--color-accent-300)' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '6px 12px', fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', borderBottom: '1px solid #e3e6ea' }}>
                    Customer Order No
                  </th>
                  <th style={{ textAlign: 'left', padding: '6px 12px', fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', borderBottom: '1px solid #e3e6ea', width: 140 }}>
                    Order Date
                  </th>
                  <th style={{ textAlign: 'right', padding: '6px 12px', fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', borderBottom: '1px solid #e3e6ea', width: 90 }}>
                    Qty
                  </th>
                </tr>
              </thead>
              <tbody>
                {c.orders.map((o) => (
                  <tr key={o.no}>
                    <td style={{ padding: '0 12px', height: 30, borderBottom: '1px solid #eef1f5', fontFamily: 'var(--font-mono)' }}>{o.no}</td>
                    <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', fontVariantNumeric: 'tabular-nums' }}>{niceDate(o.date)}</td>
                    <td style={{ padding: '0 12px', borderBottom: '1px solid #eef1f5', textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{o.qty}</td>
                  </tr>
                ))}
                <tr style={{ background: 'var(--color-surface)' }}>
                  <td colSpan={2} style={{ padding: '0 12px', height: 30, fontSize: 11.5, fontWeight: 700, color: 'var(--color-neutral-700)' }}>
                    Σ = case qty
                  </td>
                  <td style={{ padding: '0 12px', textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700 }}>{c.qty}</td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      )}
    </>
  );
}
