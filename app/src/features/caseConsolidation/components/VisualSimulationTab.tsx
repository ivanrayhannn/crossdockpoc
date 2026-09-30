import { useMemo } from 'react';
import { plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { buildAllocationRows, buildKpis, buildOrderRows, buildReleaseRows, buildWaiting } from '../visual';
import { CaseHoles } from './CaseHoles';
import { Stepper } from './Stepper';

const ALLOC_HEADERS = ['PO Day', 'PO No', 'PO Date', 'PO Qty', 'Case No', 'Part No', 'Customer Order No', 'Order Date', 'Qty', 'Note'];

/** One inline "label value" cell in a PO strip; without a width it takes the remaining space and lets long text truncate. */
function PoField({ label, width, children }: { label: string; width?: number; children: React.ReactNode }) {
  return (
    <div className={`px-2 py-1 d-flex align-items-baseline${width ? ' border-right flex-shrink-0' : ' flex-grow-1'}`} style={width ? { width } : { minWidth: 0 }}>
      <span className="small text-muted mr-1 flex-shrink-0">{label}</span>
      {children}
    </div>
  );
}

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
    <>
      <div className="row mb-2">
        <div className="col-lg-5 mb-2 mb-lg-0 align-self-lg-start" style={{ position: 'sticky', top: 8 }}>
          <div className="card">
            <div className="card-header d-flex align-items-center flex-wrap">
              <h6 className="mb-0 mr-2">Customer orders</h6>
              <small className="text-muted">1 order per date · oldest first · total {total} pcs</small>
              <button type="button" className="btn btn-outline-primary btn-sm ml-auto" onClick={addOrder}>
                + Add order
              </button>
            </div>
            <ul className="list-group list-group-flush">
              {orderRows.map((o) => (
                <li key={o.id} className={`list-group-item${o.active ? ' list-group-item-primary' : ''}`}>
                  <div className="d-flex align-items-center">
                    <span className="d-inline-block rounded-circle flex-shrink-0 mr-2" style={{ width: 10, height: 10, background: o.color }} />
                    <span className="text-monospace font-weight-bold small text-nowrap mr-2" style={{ width: 84 }}>
                      {o.no}
                    </span>
                    <input
                      className="form-control form-control-sm mr-2"
                      type="date"
                      aria-label={`Order date ${o.no}`}
                      value={o.date}
                      onChange={(e) => {
                        const v = e.target.value;
                        if (v) updateOrder(o.id, (ord) => ({ ...ord, date: v }));
                      }}
                      style={{ width: 128 }}
                    />
                    <Stepper
                      size="sm"
                      label={`Qty ${o.no}`}
                      value={o.qty}
                      onDec={() => updateOrder(o.id, (ord) => ({ ...ord, qty: Math.max(1, ord.qty - 1) }))}
                      onInc={() => updateOrder(o.id, (ord) => ({ ...ord, qty: Math.min(24, ord.qty + 1) }))}
                    />
                    <button type="button" className="btn btn-sm btn-outline-secondary border-0 ml-auto" onClick={() => removeOrder(o.id)} title="Remove order" aria-label={`Remove order ${o.no}`}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                      </svg>
                    </button>
                  </div>
                  <div className="d-flex flex-wrap align-items-center mt-1" style={{ gap: 3, paddingLeft: 18 }}>
                    {o.dots.map((d, i) => (
                      <span key={i} className="d-inline-block rounded-circle" style={{ width: 11, height: 11, background: d.bg, border: `2px solid ${d.bd}` }} />
                    ))}
                    <small className={`ml-1 ${o.isPending ? 'text-warning-dark' : 'text-muted'}`}>{o.note}</small>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="col-lg-7">
          <div className="card">
            <div className="card-header d-flex align-items-center flex-wrap">
              <h6 className="mb-0 mr-2">Daily PO · D+1 · FIFO</h6>
              <small className="text-muted">{caseMeta}</small>
              <small className="text-muted ml-auto">{progress}</small>
            </div>
            <ul className="list-group list-group-flush">
              {releaseRows.map((r) => (
                <li key={r.no} className="list-group-item">
                  <div className="d-flex align-items-center flex-wrap mb-1">
                    <span className="badge badge-success mr-2">{r.no}</span>
                    <strong className="mr-2">{r.date}</strong>
                    <small className="text-muted">{r.calc}</small>
                    <span className={`badge badge-${r.splitVariant} ml-auto`}>{r.splitText}</span>
                  </div>
                  <div className="ml-1 pl-2" style={{ borderLeft: '2px solid rgba(0, 123, 255, 0.35)' }}>
                    {r.pos.map((p, pi) => (
                      <div key={p.no} className={pi ? 'mt-2' : undefined}>
                        <div className="d-flex align-items-stretch border rounded overflow-hidden bg-white">
                          <div className="bg-primary text-white d-flex align-items-center justify-content-center px-2 font-weight-bold text-monospace flex-shrink-0" style={{ width: 52 }}>
                            {p.no}
                          </div>
                          <PoField label="PO Date" width={158}>
                            <strong className="text-nowrap">{p.date}</strong>
                          </PoField>
                          <PoField label="PO Qty" width={170}>
                            <strong className="text-nowrap">{p.qty}</strong>
                          </PoField>
                          <PoField label="Customer orders">
                            <strong className="small text-truncate">{p.orders}</strong>
                          </PoField>
                        </div>
                        <div className="mt-1" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(270px, 1fr))', gap: '4px 12px' }}>
                          {p.cases.map((c) => (
                            <div key={c.caseNo} className="d-flex align-items-center">
                              <div className="flex-shrink-0 mr-2" style={{ width: 104 }}>
                                <div className="text-monospace font-weight-bold small">{c.caseNo}</div>
                                <div className={`small text-nowrap ${c.statusClass}`}>{c.status}</div>
                              </div>
                              <CaseHoles holes={c.holes} size={20} fontSize={7.5} gap={4} pad="4px 9px" />
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </li>
              ))}
              {waiting.show && (
                <li className="list-group-item">
                  <div className="alert alert-warning d-flex align-items-center flex-wrap mb-0" style={{ borderStyle: 'dashed' }}>
                    <strong className="mr-3">Remaining</strong>
                    <span className="d-flex flex-wrap" style={{ gap: 4 }}>
                      {waiting.dots.map((d, i) => (
                        <span key={i} className="d-inline-flex align-items-center justify-content-center rounded-circle text-white font-weight-bold" style={{ width: 20, height: 20, background: d.bg, fontSize: 7.5, opacity: 0.85 }}>
                          {d.lbl}
                        </span>
                      ))}
                    </span>
                    <small className="ml-auto text-right">{waiting.text}</small>
                  </div>
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>

      <div className="row">
        {kpis.map((k) => (
          <div key={k.k} className="col-6 col-lg-3 mb-2">
            <div className="card h-100" style={{ borderTop: `3px solid var(--${k.variant})` }}>
              <div className="card-body py-2">
                <div className="small text-muted text-uppercase font-weight-bold">{k.k}</div>
                <div className="h4 mb-0">{k.v}</div>
                <small className="text-muted">{k.s}</small>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header d-flex align-items-center flex-wrap">
          <h6 className="mb-0 mr-2">Allocation result</h6>
          <small className="text-muted">release batch → PO → case → customer order</small>
        </div>
        <div className="table-responsive">
          <table className="table table-sm table-hover text-nowrap mb-0">
            <thead className="thead-light">
              <tr>
                {ALLOC_HEADERS.map((h, i) => (
                  <th key={h} className={i === 3 || i === 8 ? 'text-right' : undefined}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allocRows.map((a, i) => (
                <tr key={i} className={a.rowClass || undefined} style={a.groupStart ? { borderTop: '2px solid var(--secondary)' } : undefined}>
                  <td className="font-weight-bold text-success">{a.rel}</td>
                  <td className={`text-monospace font-weight-bold ${a.caseClass}`}>{a.po}</td>
                  <td className="font-weight-bold">{a.poDate}</td>
                  <td className="text-right font-weight-bold text-primary">{a.poQty}</td>
                  <td className="text-monospace font-weight-bold">{a.caseNo}</td>
                  <td>{a.part}</td>
                  <td>
                    <span className="d-inline-flex align-items-center">
                      <span className="d-inline-block rounded-circle mr-2" style={{ width: 9, height: 9, background: a.color }} />
                      <span className="text-monospace">{a.no}</span>
                    </span>
                  </td>
                  <td>{a.date}</td>
                  <td className="text-right font-weight-bold">{a.qty}</td>
                  <td className={`small text-wrap ${a.noteClass}`}>{a.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!allocRows.length && <div className="card-body text-muted">Press Play, Step or Fill instantly to start dropping pcs into cases.</div>}
      </div>
    </>
  );
}
