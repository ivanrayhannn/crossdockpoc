import { useMemo } from 'react';
import { plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { buildAllocationRows, buildKpis, buildOrderRows, buildReleaseRows, buildWaiting } from '../visual';
import { CaseHoles } from './CaseHoles';
import { Stepper } from './Stepper';

export function VisualSimulationTab({ state }: { state: CaseSimulationState }) {
  const { model, placed, done, inputs, part, updateOrder, removeOrder, addOrder } = state;
  const pcs = inputs.pcs;

  const orderRows = useMemo(() => buildOrderRows(model, placed, done), [model, placed, done]);
  const releaseRows = useMemo(() => buildReleaseRows(model, placed, done, pcs), [model, placed, done, pcs]);
  const waiting = useMemo(() => buildWaiting(model), [model]);
  const kpis = useMemo(() => buildKpis(model, pcs), [model, pcs]);
  const allocRows = useMemo(() => buildAllocationRows(model, placed, done, part, pcs), [model, placed, done, part, pcs]);

  const total = model.sorted.reduce((a, o) => a + o.qty, 0);
  const progress = `${placed} / ${model.rel} pcs packed`;
  const caseMeta = `${plural(model.releases.length, 'release')} · ${model.poCount} PO · ${plural(model.caseCount, 'case')}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 36px minmax(0,1.2fr)', gap: 0, alignItems: 'start' }}>
        <div style={{ background: 'var(--color-neutral-100)', border: '1px solid var(--color-divider)', borderRadius: 6, overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid var(--color-divider)' }}>
            <span style={{ fontSize: 14, fontWeight: 700 }}>Customer orders</span>
            <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>1 order per date · oldest first · total {total} pcs</span>
            <button className="btn btn-secondary" onClick={addOrder} style={{ marginLeft: 'auto', fontSize: 12, padding: '4px 10px' }}>
              + Add order
            </button>
          </div>
          {orderRows.map((o) => (
            <div
              key={o.id}
              style={{
                display: 'grid',
                gridTemplateColumns: '14px 70px 120px 84px minmax(120px,1fr) 26px',
                alignItems: 'center',
                gap: 8,
                padding: '9px 14px',
                borderBottom: '1px solid var(--color-neutral-300)',
                background: o.active ? 'var(--color-accent-100)' : 'var(--color-neutral-100)',
                borderLeft: `3px solid ${o.active ? 'var(--color-accent)' : 'transparent'}`,
              }}
            >
              <span style={{ width: 12, height: 12, borderRadius: 999, background: o.color }} />
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: 12.5 }}>{o.no}</span>
              <input
                className="input"
                type="date"
                value={o.date}
                onChange={(e) => {
                  const v = e.target.value;
                  if (v) updateOrder(o.id, (ord) => ({ ...ord, date: v }));
                }}
                style={{ width: 120, padding: '4px 6px', fontSize: 12 }}
              />
              <Stepper
                size="sm"
                value={o.qty}
                onDec={() => updateOrder(o.id, (ord) => ({ ...ord, qty: Math.max(1, ord.qty - 1) }))}
                onInc={() => updateOrder(o.id, (ord) => ({ ...ord, qty: Math.min(24, ord.qty + 1) }))}
              />
              <span style={{ display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
                {o.dots.map((d, i) => (
                  <span key={i} style={{ width: 13, height: 13, borderRadius: 999, boxSizing: 'border-box', background: d.bg, border: `2px solid ${d.bd}` }} />
                ))}
                <span style={{ fontSize: 11, color: o.isPending ? 'oklch(0.45 0.11 65)' : 'var(--color-neutral-600)', marginLeft: 4, whiteSpace: 'nowrap' }}>{o.note}</span>
              </span>
              <button
                onClick={() => removeOrder(o.id)}
                title="Remove order"
                style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 26, height: 26, borderRadius: 4, display: 'grid', placeItems: 'center', color: 'var(--color-neutral-600)' }}
                className="row-hover"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                </svg>
              </button>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 120, color: 'var(--color-neutral-500)' }}>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M13 6l6 6-6 6" />
          </svg>
        </div>

        <div style={{ background: 'var(--color-neutral-100)', border: '1px solid var(--color-divider)', borderRadius: 6, overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid var(--color-divider)' }}>
            <span style={{ fontSize: 14, fontWeight: 700 }}>Daily PO · D+1 · FIFO</span>
            <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>{caseMeta}</span>
            <span style={{ marginLeft: 'auto', fontSize: 12, fontVariantNumeric: 'tabular-nums', color: 'var(--color-neutral-700)' }}>{progress}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', padding: '4px 16px 12px' }}>
            {releaseRows.map((r) => (
              <div key={r.no} style={{ padding: '14px 0', borderBottom: '1px dashed var(--color-divider)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 11.5, fontWeight: 700, padding: '3px 10px', borderRadius: 999, background: 'var(--color-accent-2-200)', color: 'var(--color-accent-2-800)', whiteSpace: 'nowrap' }}>
                    {r.no}
                  </span>
                  <span style={{ fontSize: 13, fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>{r.date}</span>
                  <span style={{ fontSize: 12, color: 'var(--color-neutral-700)' }}>{r.calc}</span>
                  <span
                    style={{ marginLeft: 'auto', fontSize: 11.5, fontWeight: 700, padding: '2px 9px', borderRadius: 999, background: r.splitBg, color: r.splitFg, whiteSpace: 'nowrap' }}
                  >
                    {r.splitText}
                  </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12, margin: '11px 0 0 8px', paddingLeft: 14, borderLeft: '2px solid var(--color-accent-200)' }}>
                  {r.pos.map((p) => (
                    <div key={p.no}>
                      <div style={{ display: 'flex', alignItems: 'stretch', border: '1px solid var(--color-accent-300)', borderRadius: 6, overflow: 'hidden', background: 'var(--color-neutral-100)' }}>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flex: 'none',
                            width: 76,
                            padding: '0 12px',
                            background: 'var(--color-accent)',
                            color: '#fff',
                            fontFamily: 'var(--font-mono)',
                            fontWeight: 700,
                            fontSize: 15,
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {p.no}
                        </div>
                        <div style={{ padding: '7px 14px', borderRight: '1px solid var(--color-divider)', flex: 'none', width: 128, boxSizing: 'border-box' }}>
                          <div style={{ fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-600)', fontWeight: 600 }}>PO Date</div>
                          <div style={{ fontSize: 14, fontWeight: 700, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>{p.date}</div>
                        </div>
                        <div style={{ padding: '7px 14px', borderRight: '1px solid var(--color-divider)', flex: 'none', width: 180, boxSizing: 'border-box' }}>
                          <div style={{ fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-600)', fontWeight: 600 }}>PO Qty</div>
                          <div style={{ fontSize: 14, fontWeight: 700, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>{p.qty}</div>
                        </div>
                        <div style={{ padding: '7px 14px', flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-600)', fontWeight: 600 }}>Customer orders</div>
                          <div style={{ fontSize: 12.5, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.orders}</div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 9, marginTop: 9 }}>
                        {p.cases.map((c) => (
                          <div key={c.caseNo} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                            <div style={{ width: 96 }}>
                              <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 12.5 }}>{c.caseNo}</div>
                              <div style={{ fontSize: 11, color: c.statusFg, fontWeight: 600 }}>{c.status}</div>
                            </div>
                            <CaseHoles holes={c.holes} />
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {waiting.show && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                margin: '0 16px 14px',
                padding: '10px 14px',
                borderRadius: 999,
                border: '2px dashed oklch(0.8 0.1 75)',
                background: 'oklch(0.97 0.03 80)',
              }}
            >
              <span style={{ fontSize: 12, fontWeight: 700, color: 'oklch(0.42 0.1 65)', whiteSpace: 'nowrap' }}>Remaining</span>
              <span style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {waiting.dots.map((d, i) => (
                  <span key={i} style={{ width: 22, height: 22, borderRadius: 999, display: 'grid', placeItems: 'center', background: d.bg, fontSize: 8.5, fontWeight: 700, color: '#fff', opacity: 0.85 }}>
                    {d.lbl}
                  </span>
                ))}
              </span>
              <span style={{ marginLeft: 'auto', fontSize: 12, color: 'oklch(0.42 0.1 65)', textAlign: 'right' }}>{waiting.text}</span>
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,minmax(0,1fr))', gap: 12 }}>
        {kpis.map((k) => (
          <div key={k.k} style={{ padding: '12px 16px', background: 'var(--color-neutral-100)', border: '1px solid var(--color-divider)', borderRadius: 6, borderTop: `3px solid ${k.c}` }}>
            <div style={{ fontSize: 10, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-600)', fontWeight: 600 }}>{k.k}</div>
            <div style={{ fontSize: 22, fontWeight: 700, fontVariantNumeric: 'tabular-nums', marginTop: 2 }}>{k.v}</div>
            <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>{k.s}</div>
          </div>
        ))}
      </div>

      <div style={{ background: 'var(--color-neutral-100)', border: '1px solid var(--color-divider)', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid var(--color-divider)' }}>
          <span style={{ fontSize: 14, fontWeight: 700 }}>Allocation result</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>release batch → PO → case → customer order</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'var(--color-surface)' }}>
              {['PO Day', 'PO No', 'PO Date', 'PO Qty', 'Case No', 'Part No', 'Customer Order No', 'Order Date', 'Qty', 'Note'].map((h, i) => (
                <th
                  key={h}
                  style={{
                    textAlign: i === 3 || i === 8 ? 'right' : 'left',
                    padding: i === 0 || i === 9 ? '8px 16px' : '8px 12px',
                    fontSize: 10.5,
                    letterSpacing: '.05em',
                    textTransform: 'uppercase',
                    color: 'var(--color-neutral-700)',
                    borderBottom: '1px solid var(--color-divider)',
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {allocRows.map((a, i) => (
              <tr key={i} style={{ background: a.bg, borderTop: a.topBd }}>
                <td style={{ padding: '0 16px', height: 38, borderBottom: '1px solid var(--color-neutral-300)', fontWeight: 700, color: 'var(--color-accent-2-800)' }}>{a.rel}</td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)', fontFamily: 'var(--font-mono)', fontWeight: 700, color: a.caseFg }}>{a.po}</td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)', fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{a.poDate}</td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)', textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700, color: 'var(--color-accent-800)' }}>
                  {a.poQty}
                </td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{a.caseNo}</td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)' }}>{a.part}</td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)' }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7 }}>
                    <span style={{ width: 9, height: 9, borderRadius: 999, background: a.color }} />
                    <span style={{ fontFamily: 'var(--font-mono)' }}>{a.no}</span>
                  </span>
                </td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)', fontVariantNumeric: 'tabular-nums' }}>{a.date}</td>
                <td style={{ padding: '0 12px', borderBottom: '1px solid var(--color-neutral-300)', textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{a.qty}</td>
                <td style={{ padding: '0 16px', borderBottom: '1px solid var(--color-neutral-300)', fontSize: 12, color: a.noteFg }}>{a.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!allocRows.length && <div style={{ padding: 16, fontSize: 12.5, color: 'var(--color-neutral-600)' }}>Press Play, Step or Fill instantly to start dropping pcs into cases.</div>}
      </div>
    </div>
  );
}
