import { useMemo } from 'react';
import { asnNoFor, caseNo, DEST, niceD, partNoOf, plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { BackToDeliveryPlanButton } from './BackToDeliveryPlanButton';

interface DraftCase {
  id: string;
  po: string;
  part: string;
  destination: string;
  qty: number;
}

/** ASN draft reached directly from a selected delivery-plan case. */
export function AsnDraftTab({ state }: { state: CaseSimulationState }) {
  const { model, inputs, asnSelection, asnDeliveryDate, setAsnDeliveryDate, asnRits, asnRit, setAsnRit, submittedAsn, backToDeliveryPlan, submitAsn, sequenceOfCase } = state;
  const readOnly = !!submittedAsn;
  const selectedIds = useMemo(() => submittedAsn?.ids ?? Object.keys(asnSelection), [submittedAsn, asnSelection]);
  const draft = useMemo<DraftCase[]>(() => {
    const selected = new Set(selectedIds);
    return model.releases.flatMap((release) =>
      release.pos.flatMap((po) =>
        po.cases
          .filter((c) => selected.has(caseNo(c.n)))
          .flatMap((c) => {
            const qtyByPart = new Map<string, number>();
            model.seq.slice(c.start, c.start + inputs.pcs).forEach((piece) => {
              const part = partNoOf(piece.o);
              qtyByPart.set(part, (qtyByPart.get(part) ?? 0) + 1);
            });
            return [...qtyByPart].map(([part, qty]) => ({
              id: caseNo(c.n),
              po: po.no,
              part,
              destination: `${DEST[c.dest].name} · ${DEST[c.dest].code}`,
              qty,
            }));
          }),
      ),
    );
  }, [inputs.pcs, model.releases, model.seq, selectedIds]);
  const draftCaseCount = new Set(draft.map((item) => item.id)).size;
  const totalQty = draft.reduce((total, item) => total + item.qty, 0);
  const sequence = draft.length ? sequenceOfCase.get(draft[0].id) : undefined;
  const sequenceNote = sequence ? `Order date ${niceD(sequence.od)} · ${sequence.poNos.join(', ')}` : '';
  const asnNo = submittedAsn?.no ?? asnNoFor(asnDeliveryDate);
  const deliveryDate = submittedAsn?.deliveryDate ?? asnDeliveryDate;
  const rit = submittedAsn?.rit ?? asnRit;
  const noRit = !rit;

  return (
    <div className="pb-4">
      <div className="d-flex align-items-center flex-wrap mb-2">
        <BackToDeliveryPlanButton onClick={backToDeliveryPlan} />
        <h1 className="h3 mb-0 mr-2">{readOnly ? asnNo : 'ASN Draft'}</h1>
        <span className={`badge ${readOnly ? 'badge-success' : 'badge-secondary'}`}>{readOnly ? 'Submitted' : 'Draft'}</span>
      </div>

      {readOnly && (
        <div className="alert alert-success" role="alert">
          <strong>{asnNo} submitted.</strong> {plural(draftCaseCount, 'case')} are locked. Delivery {niceD(deliveryDate)}.
        </div>
      )}

      {!readOnly && sequence && (
        <div className="alert alert-info py-2" role="alert">
          <strong>One ASN = one Customer Order Date.</strong> All {plural(sequence.caseNos.length, 'case')} of order date {niceD(sequence.od)}
          {sequence.poNos.length > 1 ? ` (spread over ${sequence.poNos.join(', ')})` : ''} are included and cannot be split into another ASN.
        </div>
      )}

      <div className="row">
        <div className="col-md-8 mb-2">
          <div className="card h-100">
            <div className="card-body py-2 d-flex flex-wrap">
              <div className="mr-5">
                <div className="small text-muted text-uppercase font-weight-bold">ASN No</div>
                <div className="font-weight-bold text-monospace">{asnNo}</div>
                <small className="text-muted">{readOnly ? 'submitted' : 'auto · assigned on submit'}</small>
              </div>
              <div>
                <div className="small text-muted text-uppercase font-weight-bold">Supplier · Plant</div>
                <div className="font-weight-bold text-monospace">50221 · P01</div>
                <small className="text-muted">PT Dummy Supplier Indonesia</small>
              </div>
            </div>
          </div>
        </div>
        <SummaryCell label="Cases · Qty" value={`${plural(draftCaseCount, 'case')} · ${totalQty} pcs`} note={sequenceNote} />
      </div>

      <div className="card mb-2">
        <div className="card-header d-flex align-items-center flex-wrap">
          <h6 className="mb-0 mr-2">Case list in this ASN</h6>
          <small className="text-muted">Grouped by Part No</small>
          <div className="ml-auto d-flex align-items-center flex-wrap">
            <label htmlFor="asn-delivery-date" className="small font-weight-bold mb-0 mr-2 text-nowrap">
              Delivery Date <span className="text-danger">*</span>
            </label>
            <input
              id="asn-delivery-date"
              className="form-control form-control-sm mr-3"
              type="date"
              value={deliveryDate}
              onChange={(event) => setAsnDeliveryDate(event.target.value)}
              disabled={readOnly}
              style={{ width: 150 }}
            />
            <label htmlFor="asn-rit" className="small font-weight-bold mb-0 mr-2 text-nowrap">
              Rit <span className="text-danger">*</span>
            </label>
            <select
              id="asn-rit"
              className="custom-select custom-select-sm mr-3"
              value={rit?.no ?? ''}
              onChange={(event) => setAsnRit(event.target.value)}
              disabled={readOnly || noRit}
              style={{ width: 130 }}
            >
              {noRit ? (
                <option value="">No rit</option>
              ) : (
                asnRits.map((r) => (
                  <option key={r.no} value={r.no}>
                    {r.no}
                  </option>
                ))
              )}
            </select>
            <button type="button" className="btn btn-outline-secondary btn-sm" disabled={!draft.length}>
              <svg className="mr-1" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v12M7 10l5 5 5-5M5 21h14" />
              </svg>
              Download All Case Labels
            </button>
          </div>
        </div>

        {draft.length ? (
          <div className="table-responsive">
            <table className="table table-sm table-hover text-nowrap mb-0">
              <thead className="thead-light">
                <tr>
                  <th style={{ width: 64 }}>Seq</th>
                  <th style={{ width: 130 }}>Case No</th>
                  <th style={{ width: 90 }}>PO No</th>
                  <th style={{ width: 120 }}>Part No</th>
                  <th style={{ width: 180 }}>Destination</th>
                  <th style={{ width: 110 }}>Route</th>
                  <th className="text-right pr-3">Qty</th>
                </tr>
              </thead>
              <tbody>
                <tr className="table-light">
                  <td colSpan={7}>
                    <strong>Part breakdown</strong>
                    <small className="text-muted ml-2">
                      {plural(draftCaseCount, 'case')} · {totalQty} pcs
                    </small>
                  </td>
                </tr>
                {draft.map((item, index) => (
                  <tr key={`${item.id}-${item.part}`}>
                    <td className="align-middle text-muted">{String(index + 1).padStart(2, '0')}</td>
                    <td className="align-middle text-monospace font-weight-bold">{item.id}</td>
                    <td className="align-middle text-monospace font-weight-bold text-primary">{item.po}</td>
                    <td className="align-middle font-weight-bold">{item.part}</td>
                    <td className="align-middle">{item.destination}</td>
                    <td className="align-middle">
                      <input
                        className="form-control form-control-sm text-monospace"
                        value={rit?.route ?? ''}
                        placeholder="-"
                        aria-label={`Route for ${item.id}`}
                        disabled
                        style={{ width: 80 }}
                      />
                    </td>
                    <td className="align-middle text-right font-weight-bold pr-3">{item.qty}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="table-light">
                  <td colSpan={6} className="text-right text-muted">
                    Total
                  </td>
                  <td className="text-right font-weight-bold pr-3">{totalQty}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        ) : (
          <div className="card-body text-center text-muted py-5">No cases in this ASN. Go back and select at least one case.</div>
        )}
      </div>

      {!readOnly && (
        <div className="d-flex align-items-center justify-content-end">
          {noRit && <small className="text-danger mr-auto">No rit available for {niceD(deliveryDate)}. Choose another delivery date.</small>}
          <button type="button" className="btn btn-outline-secondary mr-2" onClick={backToDeliveryPlan}>
            Cancel
          </button>
          <button type="button" className="btn btn-primary" onClick={submitAsn} disabled={!draft.length || !deliveryDate || noRit}>
            Submit ASN
          </button>
        </div>
      )}
    </div>
  );
}

function SummaryCell({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="col-md-4 mb-2">
      <div className="card h-100">
        <div className="card-body py-2">
          <div className="small text-muted text-uppercase font-weight-bold">{label}</div>
          <div className="font-weight-bold">{value}</div>
          <small className="text-muted">{note}</small>
        </div>
      </div>
    </div>
  );
}
