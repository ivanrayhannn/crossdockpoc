import { useMemo } from 'react';
import { buildDeliveryPlan } from '../deliveryPlan';
import type { CaseSimulationState } from '../useCaseSimulation';
import { CaseHoles } from './CaseHoles';

const th: React.CSSProperties = {
  textAlign: 'left',
  padding: '8px 12px',
  fontSize: 10.5,
  letterSpacing: '.05em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  borderBottom: '1px solid #e3e6ea',
  whiteSpace: 'nowrap',
};
const td: React.CSSProperties = { padding: '0 12px', height: 38, borderBottom: '1px solid #eef1f5' };

export function DeliveryPlanTab({ state }: { state: CaseSimulationState }) {
  const { inputs, part, model, dpPage, dpFilter, setDpFilter, dpQuery, dpSel, dpVariable, dpSearch, dpReset, dpSelect, dpBack, dpToggleVariable, dpClearVariable } = state;

  const dp = useMemo(
    () => buildDeliveryPlan({ orders: inputs.orders, pcs: inputs.pcs, part, model, query: dpQuery, sel: dpSel, variable: dpVariable }),
    [inputs.orders, inputs.pcs, part, model, dpQuery, dpSel, dpVariable],
  );

  if (dpPage === 'detail') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px', background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6 }}>
          <button className="btn btn-secondary" onClick={dpBack} style={{ fontSize: 12.5, padding: '5px 12px' }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 6 9 12 15 18" />
            </svg>
            Back to Delivery Plan
          </button>
          <span style={{ fontSize: 13, color: 'var(--color-neutral-600)' }}>
            Delivery Plan <span style={{ color: 'var(--color-neutral-400)' }}>/</span>{' '}
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent-800)' }}>{dp.selLabel}</span>
          </span>
          <span style={{ marginLeft: 'auto', fontSize: 12.5, color: 'var(--color-neutral-700)' }}>
            {dp.selDate} · {dp.meta}
          </span>
        </div>

        <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea' }}>
            <span style={{ fontSize: 14, fontWeight: 700 }}>PO Released · Detail</span>
            <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Cases in this PO</span>
            <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--color-neutral-600)' }}>Click a case to filter Detail in Detail</span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: 'var(--color-surface)' }}>
                <th style={{ width: 44, borderBottom: '1px solid #e3e6ea' }} />
                <th style={{ ...th, width: 150 }}>Delivery Plan (PO)</th>
                <th style={{ ...th, width: 100 }}>Part No</th>
                <th style={{ ...th, width: 80, textAlign: 'right' }}>Qty</th>
                <th style={{ ...th, width: 90 }}>PO No</th>
                <th style={th}>Case No</th>
                <th style={{ ...th, width: 200, textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {dp.caseRows.map((r) => (
                <tr
                  key={r.v}
                  onClick={() => !r.waiting && dpToggleVariable(r.v)}
                  className={r.waiting ? undefined : 'row-hover'}
                  style={{ cursor: r.waiting ? 'default' : 'pointer', background: r.selected ? 'var(--color-accent-100)' : '#fff' }}
                >
                  <td style={{ ...td, paddingLeft: 14 }}>
                    <span style={{ display: 'inline-grid', placeItems: 'center', width: 22, height: 22, borderRadius: 999, background: 'var(--color-accent-200)', color: 'var(--color-accent-800)', fontSize: 11.5, fontWeight: 700 }}>
                      {r.v}
                    </span>
                  </td>
                  <td style={{ ...td, fontVariantNumeric: 'tabular-nums' }}>{r.date}</td>
                  <td style={{ ...td, fontWeight: 600 }}>{r.part}</td>
                  <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700 }}>{r.qty}</td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)' }}>{r.po}</td>
                  <td style={{ ...td, height: 44 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, width: 74 }}>{r.caseNo}</span>
                      <CaseHoles holes={r.holes} size={20} fontSize={7.5} gap={4} pad="4px 8px" />
                    </span>
                  </td>
                  <td style={{ ...td, textAlign: 'right' }}>
                    {r.waiting ? (
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'oklch(0.45 0.11 65)' }}>Waiting – case not full</span>
                    ) : (
                      <button className="btn btn-secondary" onClick={(e) => e.stopPropagation()} style={{ fontSize: 12, padding: '4px 11px' }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 3v12M7 10l5 5 5-5M5 21h14" />
                        </svg>
                        Download Case Label
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea' }}>
            <span style={{ fontSize: 14, fontWeight: 700 }}>Detail in Detail</span>
            <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Customer orders per case · {dp.orderMeta}</span>
            {dp.canClear && (
              <button className="btn btn-secondary" onClick={dpClearVariable} style={{ marginLeft: 'auto', fontSize: 12, padding: '4px 11px' }}>
                Show all cases
              </button>
            )}
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: 'var(--color-surface)' }}>
                <th style={{ ...th, width: 150 }}>Delivery Plan (PO)</th>
                <th style={{ ...th, width: 130 }}>Case No</th>
                <th style={{ ...th, width: 100 }}>Part No</th>
                <th style={{ ...th, width: 80, textAlign: 'right' }}>Qty</th>
                <th style={{ ...th, width: 100, textAlign: 'right' }}>Customer Qty</th>
                <th style={{ ...th, width: 150 }}>CUSTOMER ORDER</th>
                <th style={{ ...th, width: 120 }}>CUSTOMER DATE</th>
                <th style={th}>Variable</th>
              </tr>
            </thead>
            <tbody>
              {dp.orderRows.map((o, i) => (
                <tr key={i}>
                  <td style={{ ...td, fontVariantNumeric: 'tabular-nums' }}>{o.date}</td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)', color: 'var(--color-neutral-700)' }}>{o.caseNo}</td>
                  <td style={{ ...td, fontWeight: 600 }}>{o.part}</td>
                  <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700 }}>{o.qty}</td>
                  <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: 'var(--color-neutral-700)' }}>{o.total}</td>
                  <td style={td}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7 }}>
                      <span style={{ width: 10, height: 10, borderRadius: 999, background: o.color }} />
                      <span style={{ fontFamily: 'var(--font-mono)' }}>{o.no}</span>
                    </span>
                  </td>
                  <td style={{ ...td, fontVariantNumeric: 'tabular-nums' }}>{o.od}</td>
                  <td style={td}>
                    <span style={{ display: 'inline-grid', placeItems: 'center', width: 22, height: 22, borderRadius: 999, background: 'var(--color-accent-200)', color: 'var(--color-accent-800)', fontSize: 11.5, fontWeight: 700 }}>
                      {o.v}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6 }}>
        <div style={{ padding: '10px 16px', borderBottom: '1px solid #e3e6ea', fontSize: 14, fontWeight: 700 }}>Searching Criteria</div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 14, padding: '12px 16px', flexWrap: 'wrap' }}>
          <div className="field">
            <label>Delivery Plan · From</label>
            <input className="input" type="date" value={dpFilter.from} onChange={(e) => setDpFilter((f) => ({ ...f, from: e.target.value }))} style={{ width: 160 }} />
          </div>
          <div className="field">
            <label>To</label>
            <input className="input" type="date" value={dpFilter.to} onChange={(e) => setDpFilter((f) => ({ ...f, to: e.target.value }))} style={{ width: 160 }} />
          </div>
          <div className="field">
            <label>PO Number</label>
            <input className="input" value={dpFilter.po} onChange={(e) => setDpFilter((f) => ({ ...f, po: e.target.value }))} placeholder="e.g. PO3" style={{ width: 150, fontFamily: 'var(--font-mono)' }} />
          </div>
          <div className="field">
            <label>Status</label>
            <select className="input" value={dpFilter.st} onChange={(e) => setDpFilter((f) => ({ ...f, st: e.target.value as typeof f.st }))} style={{ width: 170, appearance: 'none' }}>
              <option value="all">All</option>
              <option value="po">PO released</option>
              <option value="rem">Not released</option>
            </select>
          </div>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={dpReset}>
              Reset
            </button>
            <button className="btn btn-primary" onClick={dpSearch}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <circle cx="11" cy="11" r="7" />
                <line x1="16.5" y1="16.5" x2="21" y2="21" />
              </svg>
              Search
            </button>
          </span>
        </div>
      </div>

      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea' }}>
          <span style={{ fontSize: 14, fontWeight: 700 }}>Delivery Plan</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Header · 1 row per PO</span>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--color-neutral-600)' }}>Click a PO to open its detail</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'var(--color-surface)' }}>
              <th style={{ ...th, width: 200 }}>Delivery Plan (PO)</th>
              <th style={{ ...th, width: 180 }}>PO Number</th>
              <th style={{ ...th, width: 200 }}>ASN Number</th>
              <th style={th}>Cases</th>
            </tr>
          </thead>
          <tbody>
            {dp.header.map((r) => (
              <tr key={r.key} onClick={() => dpSelect(r.key)} className="row-hover" style={{ cursor: 'pointer', background: '#fff' }}>
                <td style={{ ...td, borderLeft: `3px solid ${r.remaining ? 'oklch(0.72 0.12 70)' : 'transparent'}`, fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{r.date}</td>
                <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent-800)' }}>{r.po}</td>
                <td style={{ ...td, fontFamily: 'var(--font-mono)' }}>{r.asn}</td>
                <td style={{ ...td, color: 'var(--color-neutral-700)' }}>{r.cases}</td>
              </tr>
            ))}
            {!dp.header.length && (
              <tr>
                <td colSpan={4} style={{ padding: 16, fontSize: 12.5, color: 'var(--color-neutral-600)' }}>
                  No delivery plan matches this search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
