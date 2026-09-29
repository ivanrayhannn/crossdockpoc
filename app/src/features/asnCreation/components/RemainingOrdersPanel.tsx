import { useMemo } from 'react';
import { destLabel, filteredRemainingOrders, plural, remainingStatus } from '../asnEngine';
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
const td: React.CSSProperties = { padding: '0 12px', height: 42, borderBottom: '1px solid #eef1f5' };

export function RemainingOrdersPanel({ state }: { state: AsnCreationState }) {
  const rows = useMemo(() => filteredRemainingOrders(state.query), [state.query]);
  const qty = rows.reduce((sum, o) => sum + o.qty, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, paddingBottom: 28 }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 10,
          padding: '11px 16px',
          borderRadius: 6,
          background: 'var(--color-accent-100)',
          border: '1px solid var(--color-accent-300)',
          color: 'var(--color-accent-800)',
          fontSize: 13,
          lineHeight: 1.45,
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ flex: 'none', marginTop: 2 }}>
          <circle cx="12" cy="12" r="9" />
          <line x1="12" y1="11" x2="12" y2="16.5" />
          <line x1="12" y1="7.5" x2="12" y2="7.5" />
        </svg>
        <span>Read-only. These customer orders have no PO yet, so they have no case and cannot go into an ASN. They are picked up first (FIFO) by the next auto PO, or can be released through a manual PO.</span>
      </div>

      {rows.length ? (
        <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea' }}>
            <span style={{ fontSize: 14, fontWeight: 700 }}>Customer orders without PO</span>
            <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>
              {plural(rows.length, 'order')} · {qty} pcs
            </span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: 'var(--color-surface)' }}>
                <th style={{ ...th, width: 120, paddingLeft: 16 }}>Order Date</th>
                <th style={{ ...th, width: 150 }}>Customer Order No</th>
                <th style={{ ...th, width: 90 }}>Part No</th>
                <th style={{ ...th, width: 150 }}>Destination</th>
                <th style={{ ...th, width: 70, textAlign: 'right' }}>Qty</th>
                <th style={{ ...th, width: 190 }}>Status</th>
                <th style={{ ...th, paddingRight: 16 }}>Reason / next PO</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((o) => {
                const st = remainingStatus(o);
                return (
                  <tr key={o.no}>
                    <td style={{ ...td, paddingLeft: 16, fontVariantNumeric: 'tabular-nums' }}>{niceDate(o.date)}</td>
                    <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{o.no}</td>
                    <td style={{ ...td, fontWeight: 600 }}>{o.part}</td>
                    <td style={td}>{destLabel(o.dest)}</td>
                    <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700 }}>{o.qty}</td>
                    <td style={td}>
                      <span style={{ display: 'inline-flex', fontSize: 11.5, fontWeight: 700, padding: '2px 10px', borderRadius: 999, background: st.bg, color: st.fg, whiteSpace: 'nowrap' }}>
                        {st.label}
                      </span>
                    </td>
                    <td style={{ ...td, paddingRight: 16, fontSize: 12.5, color: 'var(--color-neutral-700)' }}>{st.reason}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 6, padding: '44px 20px', background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6 }}>
          <h3 style={{ fontSize: 16 }}>Every customer order has a PO</h3>
          <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: 0 }}>Nothing is waiting for this filter.</p>
        </div>
      )}
    </div>
  );
}
