import { useMemo } from 'react';
import { buildDeliveryPlan } from '../deliveryPlan';
import { niceD, plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { CaseHoles } from './CaseHoles';

export function DeliveryPlanTab({ state }: { state: CaseSimulationState }) {
  const {
    inputs,
    part,
    model,
    role,
    dpPage,
    dpFilter,
    setDpFilter,
    dpQuery,
    dpSel,
    dpVariable,
    dpSearch,
    dpReset,
    dpSelect,
    dpBack,
    dpToggleVariable,
    dpClearVariable,
    asnSelection,
    asnByCase,
    toggleAsnCase,
    sequenceOfCase,
    clearAsnSelection,
    openAsnDraft,
  } = state;
  const canSeeOrderDetail = role !== 'sup';

  const dp = useMemo(
    () => buildDeliveryPlan({ orders: inputs.orders, pcs: inputs.pcs, part, model, query: dpQuery, sel: dpSel, variable: dpVariable, asnByCase }),
    [inputs.orders, inputs.pcs, part, model, dpQuery, dpSel, dpVariable, asnByCase],
  );
  // One ASN = one Customer Order Date, so the selection is always the whole sequence.
  const selectedIds = Object.keys(asnSelection);
  const selectedSeq = selectedIds.length ? sequenceOfCase.get(selectedIds[0]) : undefined;

  if (dpPage === 'detail') {
    return (
      <>
        <div className="card mb-2">
          <div className="card-body py-2 d-flex align-items-center flex-wrap">
            <button type="button" className="btn btn-outline-secondary btn-sm mr-3" onClick={dpBack}>
              <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 6 9 12 15 18" />
              </svg>
              Back to Delivery Plan
            </button>
            <nav aria-label="breadcrumb">
              <ol className="breadcrumb bg-transparent p-0 mb-0">
                <li className="breadcrumb-item">Delivery Plan</li>
                <li className="breadcrumb-item">Customer Order Date</li>
                <li className="breadcrumb-item active text-monospace font-weight-bold" aria-current="page">
                  {dp.selLabel}
                </li>
              </ol>
            </nav>
            <small className="text-muted ml-auto">
              {dp.selPoNos} · {dp.meta}
            </small>
          </div>
        </div>

        <div className="card mb-2">
          <div className="card-header d-flex align-items-center flex-wrap">
            <h6 className="mb-0 mr-2">Customer Order Date · Detail</h6>
            <small className="text-muted">All cases of this order date, across its POs</small>
            {canSeeOrderDetail && <small className="text-muted ml-auto">Click a case to filter Detail in Detail</small>}
          </div>
          <div className="table-responsive">
            <table className="table table-sm table-hover text-nowrap mb-0">
              <thead className="thead-light">
                <tr>
                  <th style={{ width: 48 }} />
                  <th style={{ width: 48 }} />
                  <th style={{ width: 150 }}>PO Date</th>
                  <th style={{ width: 100 }}>Part No</th>
                  <th className="text-right" style={{ width: 80 }}>
                    Qty
                  </th>
                  <th style={{ width: 90 }}>PO No</th>
                  <th>Case No</th>
                  <th className="text-right" style={{ width: 200 }}>
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {dp.caseRows.map((r) => {
                  const checkId = `asn-case-${r.caseNo}`;
                  const inAsn = !!asnByCase[r.caseNo];
                  const otherDate = !!selectedSeq && selectedSeq.od !== dp.selOd;
                  const blocked = r.waiting || inAsn || !dp.selComplete || otherDate;
                  const hint = r.waiting
                    ? 'Not released yet'
                    : inAsn
                      ? 'Already in an ASN'
                      : !dp.selComplete
                        ? `Order date ${dp.selLabel} is not fully paired with a PO yet · view only`
                        : otherDate
                          ? 'One ASN = one Customer Order Date. Clear the current selection first'
                          : `Select all cases of order date ${dp.selLabel}`;
                  return (
                    <tr
                      key={r.v}
                      onClick={() => canSeeOrderDetail && !r.waiting && dpToggleVariable(r.v)}
                      className={r.selected ? 'table-primary' : undefined}
                      style={{ cursor: canSeeOrderDetail && !r.waiting ? 'pointer' : 'default' }}
                    >
                      <td className="align-middle" style={{ boxShadow: asnSelection[r.caseNo] ? 'inset 3px 0 0 var(--primary)' : undefined }}>
                        <div className="custom-control custom-checkbox" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="checkbox"
                            className="custom-control-input"
                            id={checkId}
                            checked={!!asnSelection[r.caseNo] || !!asnByCase[r.caseNo]}
                            disabled={blocked}
                            onChange={() => toggleAsnCase(r.caseNo)}
                          />
                          <label className="custom-control-label" htmlFor={checkId} title={hint}>
                            <span className="sr-only">Select {r.caseNo}</span>
                          </label>
                        </div>
                      </td>
                      <td className="align-middle">
                        <span className="badge badge-pill badge-primary">{r.v}</span>
                      </td>
                      <td className="align-middle">{r.date}</td>
                      <td className="align-middle font-weight-bold">{r.part}</td>
                      <td className="align-middle text-right font-weight-bold">{r.qty}</td>
                      <td className="align-middle text-monospace">{r.po}</td>
                      <td className="align-middle">
                        <span className="d-flex align-items-center">
                          <span className="text-monospace font-weight-bold mr-3" style={{ width: 74 }}>
                            {r.caseNo}
                          </span>
                          {canSeeOrderDetail && <CaseHoles holes={r.holes} size={20} fontSize={7.5} gap={4} pad="4px 8px" wrap={false} />}
                        </span>
                      </td>
                      <td className="align-middle text-right">
                        {r.waiting ? (
                          <span className="badge badge-warning">Waiting – case not full</span>
                        ) : (
                          <button type="button" className="btn btn-outline-secondary btn-sm" onClick={(e) => e.stopPropagation()}>
                            <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M12 3v12M7 10l5 5 5-5M5 21h14" />
                            </svg>
                            Download Case Label
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card shadow mb-2" style={{ position: 'sticky', bottom: 0, zIndex: 20 }}>
          <div className="card-body py-2 d-flex align-items-center flex-wrap">
            <span className={`badge badge-pill mr-3 ${selectedIds.length ? 'badge-primary' : 'badge-secondary'}`} style={{ fontSize: 13, minWidth: 28 }}>
              {selectedIds.length}
            </span>
            <div className="mr-3">
              <div className="font-weight-bold">
                {selectedSeq
                  ? `Order date ${niceD(selectedSeq.od)} · ${plural(selectedIds.length, 'case')} · ${selectedIds.length * inputs.pcs} pcs`
                  : 'No case selected'}
              </div>
              <small className="text-muted">
                {selectedSeq
                  ? `${selectedSeq.poNos.join(', ')} · all cases of this order date go into one ASN`
                  : 'Tick a case of a Complete order date to select all its cases. One ASN = one Customer Order Date. Cases already in an ASN are locked.'}
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

        {canSeeOrderDetail && (
          <div className="card">
            <div className="card-header d-flex align-items-center flex-wrap">
              <h6 className="mb-0 mr-2">Detail in Detail</h6>
              <small className="text-muted">Customer orders per case · {dp.orderMeta}</small>
              {dp.canClear && (
                <button type="button" className="btn btn-outline-secondary btn-sm ml-auto" onClick={dpClearVariable}>
                  Show all cases
                </button>
              )}
            </div>
            <div className="table-responsive">
              <table className="table table-sm table-hover text-nowrap mb-0">
                <thead className="thead-light">
                  <tr>
                    <th style={{ width: 125 }}>PO Date</th>
                    <th style={{ width: 110 }}>Case No</th>
                    <th style={{ width: 85 }}>Part No</th>
                    <th className="text-right" style={{ width: 60 }}>
                      Qty
                    </th>
                    <th className="text-right" style={{ width: 110 }}>
                      Customer Qty
                    </th>
                    <th style={{ width: 125 }}>Customer Order</th>
                    <th style={{ width: 150 }}>Destination</th>
                    <th style={{ width: 130 }}>Customer Order Date</th>
                    <th style={{ width: 80 }}>Variable</th>
                  </tr>
                </thead>
                <tbody>
                  {dp.orderRows.map((o, i) => (
                    <tr key={i}>
                      <td>{o.date}</td>
                      <td className="text-monospace text-muted">{o.caseNo}</td>
                      <td className="font-weight-bold">{o.part}</td>
                      <td className="text-right font-weight-bold">{o.qty}</td>
                      <td className="text-right text-muted">{o.total}</td>
                      <td>
                        <span className="d-inline-flex align-items-center">
                          <span className="d-inline-block rounded-circle mr-2" style={{ width: 10, height: 10, background: o.color }} />
                          <span className="text-monospace">{o.no}</span>
                        </span>
                      </td>
                      <td>{o.destination}</td>
                      <td>{o.od}</td>
                      <td>
                        <span className="badge badge-pill badge-primary">{o.v}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </>
    );
  }

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
              <label htmlFor="dp-po" className="d-block small text-muted mb-1">
                PO Number
              </label>
              <input
                id="dp-po"
                className="form-control text-monospace"
                value={dpFilter.po}
                onChange={(e) => setDpFilter((f) => ({ ...f, po: e.target.value }))}
                placeholder="e.g. PO3"
                style={{ width: 130 }}
              />
            </div>
            <div className="form-group col-auto">
              <label htmlFor="dp-status" className="d-block small text-muted mb-1">
                Status
              </label>
              <select id="dp-status" className="custom-select" value={dpFilter.st} onChange={(e) => setDpFilter((f) => ({ ...f, st: e.target.value as typeof f.st }))} style={{ width: 140 }}>
                <option value="all">All</option>
                <option value="complete">Complete (ready for ASN)</option>
                <option value="view">View only</option>
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

      <div className="card">
        <div className="card-header d-flex align-items-center flex-wrap">
          <h6 className="mb-0 mr-2">Delivery Plan</h6>
          <small className="text-muted">Header · 1 row per Customer Order Date</small>
          <small className="text-muted ml-auto">Click a row to open its POs and cases</small>
        </div>
        <div className="table-responsive">
          <table className="table table-sm table-hover text-nowrap mb-0">
            <thead className="thead-light">
              <tr>
                <th style={{ width: 200 }}>Customer Order Date</th>
                <th style={{ width: 260 }}>PO (PO Date)</th>
                <th style={{ width: 200 }}>ASN Number</th>
                <th style={{ width: 150 }}>Status</th>
                <th>Cases</th>
              </tr>
            </thead>
            <tbody>
              {dp.header.map((r) => (
                <tr key={r.key} onClick={() => dpSelect(r.key)} className={r.complete ? undefined : 'table-warning'} style={{ cursor: 'pointer' }}>
                  <td className="font-weight-bold">{r.date}</td>
                  <td>
                    {r.pos.length ? (
                      r.pos.map((p) => (
                        <span key={p.no} className="mr-3">
                          <span className="text-monospace font-weight-bold text-primary">{p.no}</span>
                          <small className="text-muted ml-1">{p.date}</small>
                        </span>
                      ))
                    ) : (
                      <span className="text-muted">-</span>
                    )}
                  </td>
                  <td className="text-monospace">{r.asn}</td>
                  <td>
                    <span className={`badge ${r.complete ? 'badge-success' : 'badge-warning'}`}>{r.complete ? 'Complete' : 'View only'}</span>
                  </td>
                  <td className="text-muted">{r.cases}</td>
                </tr>
              ))}
              {!dp.header.length && (
                <tr>
                  <td colSpan={5} className="text-muted">
                    No delivery plan matches this search.
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
