import { useMemo } from 'react';
import { caseNo, DEST, niceD, plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';

interface DraftCase {
  id: string;
  po: string;
  part: string;
  destination: string;
  qty: number;
}

/** ASN draft reached directly from a selected delivery-plan case. */
export function AsnDraftTab({ state }: { state: CaseSimulationState }) {
  const { model, part, inputs, asnSelection, asnDeliveryDate, setAsnDeliveryDate, submittedAsn, backToDeliveryPlan, submitAsn, removeFromAsnDraft } = state;
  const readOnly = !!submittedAsn;
  const selectedIds = submittedAsn?.ids ?? Object.keys(asnSelection);
  const cases = useMemo<DraftCase[]>(
    () =>
      model.releases.flatMap((release) =>
        release.pos.flatMap((po) =>
          po.cases.map((c) => ({
            id: caseNo(c.n),
            po: po.no,
            part,
            destination: `${DEST[c.dest].name} · ${DEST[c.dest].code}`,
            qty: inputs.pcs,
          })),
        ),
      ),
    [inputs.pcs, model.releases, part],
  );
  const draft = cases.filter((item) => selectedIds.includes(item.id));
  const totalQty = draft.reduce((total, item) => total + item.qty, 0);
  const asnNo = submittedAsn?.no ?? `ASN-50221-${asnDeliveryDate.replaceAll('-', '').slice(2)}-001`;
  const deliveryDate = submittedAsn?.deliveryDate ?? asnDeliveryDate;

  return (
    <div className="pb-4">
      <div className="d-flex align-items-center flex-wrap mb-2">
        <button type="button" className="btn btn-outline-secondary btn-sm mr-3" onClick={backToDeliveryPlan}>
          <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 6 9 12 15 18" />
          </svg>
          Back to PO Released · Detail
        </button>
        <h1 className="h3 mb-0 mr-2">{readOnly ? asnNo : 'ASN Draft'}</h1>
        <span className={`badge ${readOnly ? 'badge-success' : 'badge-secondary'}`}>{readOnly ? 'Submitted' : 'Draft'}</span>
      </div>

      {readOnly && (
        <div className="alert alert-success" role="alert">
          <strong>{asnNo} submitted.</strong> {plural(draft.length, 'case')} are locked. Delivery {niceD(deliveryDate)}.
        </div>
      )}

      <div className="row">
        <SummaryCell label="ASN No" value={asnNo} note={readOnly ? 'submitted' : 'auto · assigned on submit'} mono />
        <SummaryCell label="Supplier · Plant" value="50221 · P01" note="PT Dummy Supplier Indonesia" mono />
        <SummaryCell label="Cases · Qty" value={`${plural(draft.length, 'case')} · ${totalQty} pcs`} note="" />
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
            {!readOnly && (
              <button type="button" className="btn btn-outline-secondary btn-sm mr-2" onClick={backToDeliveryPlan}>
                <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add cases
              </button>
            )}
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
                  <th style={{ width: 120 }}>Case No</th>
                  <th style={{ width: 90 }}>PO No</th>
                  <th style={{ width: 110 }}>Part No</th>
                  <th style={{ width: 170 }}>Destination</th>
                  <th className="text-right">Qty</th>
                  <th className="text-right" style={{ width: 80 }}>
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="table-light">
                  <td colSpan={7}>
                    <strong>{part}</strong>
                    <small className="text-muted ml-2">
                      {plural(draft.length, 'case')} · {totalQty} pcs
                    </small>
                  </td>
                </tr>
                {draft.map((item, index) => (
                  <tr key={item.id}>
                    <td className="align-middle text-muted">{String(index + 1).padStart(2, '0')}</td>
                    <td className="align-middle text-monospace font-weight-bold">{item.id}</td>
                    <td className="align-middle text-monospace font-weight-bold text-primary">{item.po}</td>
                    <td className="align-middle font-weight-bold">{item.part}</td>
                    <td className="align-middle">{item.destination}</td>
                    <td className="align-middle text-right font-weight-bold">{item.qty}</td>
                    <td className="align-middle text-right">
                      {!readOnly && (
                        <button type="button" className="btn btn-sm btn-outline-danger border-0" onClick={() => removeFromAsnDraft(item.id)} title="Remove from ASN" aria-label={`Remove ${item.id} from ASN`}>
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6" />
                          </svg>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card-body text-center text-muted py-5">No cases in this ASN. Go back and select at least one case.</div>
        )}
      </div>

      {!readOnly && (
        <div className="d-flex align-items-center justify-content-end">
          <small className="text-muted mr-auto">1 ASN can contain several POs; each case holds one part.</small>
          <button type="button" className="btn btn-outline-secondary mr-2" onClick={backToDeliveryPlan}>
            Cancel
          </button>
          <button type="button" className="btn btn-primary" onClick={submitAsn} disabled={!draft.length || !deliveryDate}>
            Submit ASN
          </button>
        </div>
      )}
    </div>
  );
}

function SummaryCell({ label, value, note, mono = false }: { label: string; value: string; note: string; mono?: boolean }) {
  return (
    <div className="col-md-4 mb-2">
      <div className="card h-100">
        <div className="card-body py-2">
          <div className="small text-muted text-uppercase font-weight-bold">{label}</div>
          <div className={`font-weight-bold${mono ? ' text-monospace' : ''}`}>{value}</div>
          <small className="text-muted">{note}</small>
        </div>
      </div>
    </div>
  );
}
