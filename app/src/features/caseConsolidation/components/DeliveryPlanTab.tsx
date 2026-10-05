import { useMemo } from 'react';
import { buildDeliveryPlan } from '../deliveryPlan';
import type { DeliveryPlanData } from '../deliveryPlan';
import { niceD, plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { BackToDeliveryPlanButton } from './BackToDeliveryPlanButton';
import './DeliveryPlanTab.css';

interface PanelProps {
  state: CaseSimulationState;
  dp: DeliveryPlanData;
}

export function DeliveryPlanTab({ state }: { state: CaseSimulationState }) {
  const { inputs, model, sequences, dpPage, dpQuery, dpSel, asnByCase } = state;

  const dp = useMemo(
    () => buildDeliveryPlan({ orders: inputs.orders, pcs: inputs.pcs, model, sequences, query: dpQuery, sel: dpSel, asnByCase }),
    [inputs.orders, inputs.pcs, model, sequences, dpQuery, dpSel, asnByCase],
  );

  return dpPage === 'detail' ? <DeliveryPlanDetail state={state} dp={dp} /> : <DeliveryPlanList state={state} dp={dp} />;
}

function StatusPill({ complete, className = '' }: { complete: boolean; className?: string }) {
  return (
    <span className={`dp-status-pill ${complete ? 'dp-status-ready' : 'dp-status-waiting'} ${className}`.trim()}>
      <span className="dp-status-dot" />
      {complete ? 'Ready to ASN' : 'Waiting Released'}
    </span>
  );
}

/** Detail in Detail: the customer-order lines of one Customer Order Date. */
function DeliveryPlanDetail({ state, dp }: PanelProps) {
  const orderCount = new Set(dp.orderRows.map((row) => row.no)).size;
  const partCount = new Set(dp.orderRows.map((row) => row.part)).size;
  const caseCount = new Set(dp.orderRows.filter((row) => !row.waiting).map((row) => row.caseNo)).size;

  return (
    <>
      <div className="card dp-detail-summary mb-2">
        <div className="card-body d-flex align-items-center flex-wrap dp-detail-summary-body">
          <BackToDeliveryPlanButton onClick={state.dpBack} />
          <div className="dp-detail-date">
            <small className="text-muted text-uppercase font-weight-bold">Customer Order Date</small>
            <h2 className="mb-0 font-weight-bold">{dp.selLabel}</h2>
          </div>
          <StatusPill complete={dp.selComplete} className="ml-3" />
          <div className="dp-po-summary ml-auto">
            <small className="text-muted text-uppercase font-weight-bold">Supplier PO</small>
            <strong className="text-monospace">{dp.selPoNos}</strong>
            <small className="text-muted">{dp.meta}</small>
          </div>
        </div>
      </div>

      <div className="card dp-detail-card">
        <div className="card-header dp-detail-card-header">
          <div>
            <h6 className="mb-1">Detail in Detail</h6>
            <small className="text-muted">Customer-order lines assigned to supplier POs and cases</small>
          </div>
          <div className="dp-detail-metrics ml-auto">
            <span>
              <strong>{orderCount}</strong> Customer Orders
            </span>
            <span>
              <strong>{partCount}</strong> Part Nos
            </span>
            <span>
              <strong>{caseCount}</strong> Cases
            </span>
          </div>
        </div>
        <div className="table-responsive">
          <table className="table table-sm table-hover text-nowrap mb-0 dp-data-table">
            <thead className="thead-light">
              <tr>
                <th style={{ width: 125 }}>Customer Order</th>
                <th style={{ width: 150 }}>Destination</th>
                <th style={{ width: 130 }}>Customer Order Date</th>
                <th className="text-right" style={{ width: 110 }}>
                  Customer Qty
                </th>
                <th style={{ width: 85 }}>Part No</th>
                <th className="text-right" style={{ width: 60 }}>
                  Qty
                </th>
                <th style={{ width: 90 }}>PO No</th>
                <th style={{ width: 125 }}>PO Date</th>
                <th style={{ width: 110 }}>Case No</th>
              </tr>
            </thead>
            <tbody>
              {dp.orderRows.map((o, i) => (
                <tr key={`${o.caseNo}-${o.no}-${o.part}-${i}`} className={o.waiting ? 'dp-line-waiting' : undefined}>
                  <td>
                    <span className="d-inline-flex align-items-center">
                      <span className="d-inline-block rounded-circle mr-2 dp-order-dot" style={{ background: o.color }} />
                      <span className="text-monospace">{o.no}</span>
                    </span>
                  </td>
                  <td>{o.destination}</td>
                  <td>{o.od}</td>
                  <td className="text-right text-muted">{o.total}</td>
                  <td className="font-weight-bold">{o.part}</td>
                  <td className="text-right font-weight-bold">{o.qty}</td>
                  <td className="text-monospace font-weight-bold text-primary">{o.waiting ? <span className="text-muted">—</span> : o.po}</td>
                  <td>{o.date}</td>
                  <td className="text-monospace text-muted">{o.waiting ? <span className="dp-case-waiting">Waiting</span> : o.caseNo}</td>
                </tr>
              ))}
              {!dp.orderRows.length && (
                <tr>
                  <td colSpan={9} className="text-center text-muted py-4">
                    No order lines for this Customer Order Date.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

/** Searching Criteria + Delivery Plan Header + the ASN selection bar. */
function DeliveryPlanList({ state, dp }: PanelProps) {
  const { inputs, role, dpFilter, setDpFilter, dpSearch, dpReset, dpSelect, asnSelection, toggleAsnDate, sequenceOfCase, clearAsnSelection, openAsnDraft } = state;
  // Supplier only sees the delivery plan; order-to-PO tracking is for Demand Supply / Procurement.
  const canSeeOrderDetail = role !== 'sup';

  // One ASN = one Customer Order Date, so the selection is always the whole sequence.
  const selectedIds = Object.keys(asnSelection);
  const selectedSeq = selectedIds.length ? sequenceOfCase.get(selectedIds[0]) : undefined;
  const readyCount = dp.header.filter((row) => row.complete).length;
  const waitingCount = dp.header.length - readyCount;

  return (
    <>
      <div className="card mb-2">
        <div className="card-header">
          <h6 className="mb-0">Searching Criteria</h6>
        </div>
        <div className="card-body pb-1">
          <div className="form-row align-items-end">
            <div className="form-group col-auto">
              <label htmlFor="dp-from" className="d-block small text-muted mb-1">
                Customer Order Date · From
              </label>
              <input id="dp-from" className="form-control" type="date" value={dpFilter.from} onChange={(e) => setDpFilter((f) => ({ ...f, from: e.target.value }))} style={{ width: 150 }} />
            </div>
            <div className="form-group col-auto">
              <label htmlFor="dp-to" className="d-block small text-muted mb-1">
                To
              </label>
              <input id="dp-to" className="form-control" type="date" value={dpFilter.to} onChange={(e) => setDpFilter((f) => ({ ...f, to: e.target.value }))} style={{ width: 150 }} />
            </div>
            <div className="form-group col-auto">
              <label htmlFor="dp-status" className="d-block small text-muted mb-1">
                Status
              </label>
              <select id="dp-status" className="custom-select" value={dpFilter.st} onChange={(e) => setDpFilter((f) => ({ ...f, st: e.target.value as typeof f.st }))} style={{ width: 220 }}>
                <option value="all">All</option>
                <option value="ready">Ready to ASN</option>
                <option value="waiting">Waiting Released</option>
              </select>
            </div>
            <div className="form-group col-auto ml-auto">
              <button type="button" className="btn btn-outline-secondary mr-2" onClick={dpReset}>
                Reset
              </button>
              <button type="button" className="btn btn-primary" onClick={dpSearch}>
                <svg className="mr-1" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <circle cx="11" cy="11" r="7" />
                  <line x1="16.5" y1="16.5" x2="21" y2="21" />
                </svg>
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-2 dp-plan-card">
        <div className="card-header dp-plan-card-header">
          <div>
            <h6 className="mb-1">Delivery Plan Header</h6>
            <small className="text-muted">One row per Customer Order Date · select a ready date to view its cases</small>
          </div>
          <div className="dp-header-summary ml-auto" aria-label="Delivery plan status counts">
            <span className="dp-summary-count">
              <strong>{dp.header.length}</strong> Dates
            </span>
            <span className="dp-summary-count dp-summary-ready">
              <strong>{readyCount}</strong> Ready
            </span>
            <span className="dp-summary-count dp-summary-waiting">
              <strong>{waitingCount}</strong> Waiting
            </span>
          </div>
        </div>
        <div className="table-responsive">
          <table className="table table-sm table-hover text-nowrap mb-0 dp-data-table dp-header-table">
            <thead className="thead-light">
              <tr>
                <th style={{ width: 48 }} />
                <th style={{ width: 200 }}>Customer Order Date</th>
                <th style={{ width: 200 }}>ASN Number</th>
                <th style={{ width: 170 }}>Status</th>
                <th>Cases</th>
                {canSeeOrderDetail && (
                  <th className="text-right" style={{ width: 110 }}>
                    Action
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {dp.header.map((r) => {
                const checkId = `asn-date-${r.key}`;
                const isSelected = selectedSeq?.od === r.key;
                const otherDate = !!selectedSeq && !isSelected;
                const blocked = !r.complete || r.asnLocked || otherDate;
                const hint = r.asnLocked
                  ? 'Already in an ASN'
                  : !r.complete
                    ? 'Waiting Released: some orders of this date are not paired with a PO yet'
                    : otherDate
                      ? 'One ASN = one Customer Order Date. Clear the current selection first'
                      : `Select all cases of ${r.date}`;
                return (
                  <tr key={r.key} className={`${r.complete ? 'dp-row-ready' : 'dp-row-waiting'}${isSelected ? ' dp-row-selected' : ''}`}>
                    <td className="align-middle" style={{ boxShadow: isSelected ? 'inset 3px 0 0 var(--primary)' : undefined }}>
                      <div className="custom-control custom-checkbox">
                        <input type="checkbox" className="custom-control-input" id={checkId} checked={isSelected || r.asnLocked} disabled={blocked} onChange={() => toggleAsnDate(r.key)} />
                        <label className="custom-control-label" htmlFor={checkId} title={hint}>
                          <span className="sr-only">Select {r.date}</span>
                        </label>
                      </div>
                    </td>
                    <td className="align-middle font-weight-bold dp-header-date">{r.date}</td>
                    <td className="align-middle text-monospace">{r.asn === '-' ? <span className="text-muted">—</span> : r.asn}</td>
                    <td className="align-middle">
                      <StatusPill complete={r.complete} />
                    </td>
                    <td className="align-middle dp-case-summary">{r.cases}</td>
                    {canSeeOrderDetail && (
                      <td className="align-middle text-right">
                        <button type="button" className="btn btn-outline-primary btn-sm dp-detail-button" onClick={() => dpSelect(r.key)}>
                          View detail
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
              {!dp.header.length && (
                <tr>
                  <td colSpan={canSeeOrderDetail ? 6 : 5} className="text-center text-muted py-4">
                    No delivery plan matches this search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card shadow mb-2" style={{ position: 'sticky', bottom: 0, zIndex: 20 }}>
        <div className="card-body py-2 d-flex align-items-center flex-wrap">
          <span className={`badge badge-pill mr-3 ${selectedSeq ? 'badge-primary' : 'badge-secondary'}`} style={{ fontSize: 13, minWidth: 28 }}>
            {selectedSeq ? 1 : 0}
          </span>
          <div className="mr-3">
            <div className="font-weight-bold">
              {selectedSeq ? `Order date ${niceD(selectedSeq.od)} · ${plural(selectedIds.length, 'case')} · ${selectedIds.length * inputs.pcs} pcs` : 'No order date selected'}
            </div>
            <small className="text-muted">
              {selectedSeq
                ? `${selectedSeq.poNos.join(', ')} · all cases of this order date go into one ASN`
                : 'Tick a Ready to ASN date. One ASN = one Customer Order Date, even when it is spread over several POs.'}
            </small>
          </div>
          <div className="ml-auto">
            <button type="button" className="btn btn-outline-secondary btn-sm mr-2" onClick={clearAsnSelection} disabled={!selectedIds.length}>
              Clear selection
            </button>
            <button type="button" className="btn btn-primary btn-sm" onClick={openAsnDraft} disabled={!selectedIds.length}>
              Group into 1 ASN
              <svg className="ml-1" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 6 15 12 9 18" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
