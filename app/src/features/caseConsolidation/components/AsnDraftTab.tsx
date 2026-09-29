import { useMemo } from 'react';
import { caseNo, DEST, niceD, plural } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';

const th: React.CSSProperties = {
  textAlign: 'left',
  padding: '8px 12px',
  fontSize: 10.5,
  letterSpacing: '.05em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  borderBottom: '1px solid #e3e6ea',
};
const td: React.CSSProperties = { padding: '0 12px', height: 40, borderBottom: '1px solid #eef1f5' };

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, paddingBottom: 28 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="btn btn-secondary" onClick={backToDeliveryPlan} style={{ fontSize: 12.5, padding: '5px 12px' }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 6 9 12 15 18" /></svg>
          Back to PO Released · Detail
        </button>
        <h1 style={{ fontSize: 22 }}>{readOnly ? asnNo : 'ASN Draft'}</h1>
        <span style={{ fontSize: 11.5, fontWeight: 700, padding: '2px 10px', borderRadius: 999, background: readOnly ? 'var(--color-accent-2-200)' : 'var(--color-neutral-200)', color: readOnly ? 'var(--color-accent-2-800)' : 'var(--color-neutral-700)' }}>
          {readOnly ? 'Submitted' : 'Draft'}
        </span>
      </div>

      {readOnly && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 16px', borderRadius: 6, background: 'var(--color-accent-2-200)', border: '1px solid var(--color-accent-2-300)', color: 'var(--color-accent-2-800)', fontSize: 13 }}>
          <strong>{asnNo} submitted.</strong> {plural(draft.length, 'case')} are locked. Delivery {niceD(deliveryDate)}.
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, display: 'grid', gridTemplateColumns: 'repeat(3,minmax(0,1fr))' }}>
        <SummaryCell label="ASN No" value={asnNo} note={readOnly ? 'submitted' : 'auto · assigned on submit'} mono />
        <SummaryCell label="Supplier · Plant" value="50221 · P01" note="PT Dummy Supplier Indonesia" mono />
        <SummaryCell label="Cases · Qty" value={`${plural(draft.length, 'case')} · ${totalQty} pcs`} note="" />
      </div>

      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea', flexWrap: 'wrap' }}>
          <span style={{ fontSize: 14, fontWeight: 700 }}>Case list in this ASN</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Grouped by Part No</span>
          <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600, color: 'var(--color-neutral-700)', whiteSpace: 'nowrap' }}>
              Delivery Date <span style={{ color: 'var(--color-accent-700)', marginLeft: -5 }}>*</span>
              <input className="input" type="date" value={deliveryDate} onChange={(event) => setAsnDeliveryDate(event.target.value)} disabled={readOnly} style={{ width: 150, padding: '5px 9px' }} />
            </label>
            <span style={{ width: 1, height: 22, background: '#e3e6ea' }} />
            {!readOnly && (
              <button className="btn btn-secondary" onClick={backToDeliveryPlan}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
                Add cases
              </button>
            )}
            <button className="btn btn-secondary" disabled={!draft.length}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v12M7 10l5 5 5-5M5 21h14" /></svg>
              Download All Case Labels
            </button>
          </span>
        </div>

        {draft.length ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: 'var(--color-surface)' }}>
                <th style={{ ...th, width: 56, paddingLeft: 16 }}>Seq</th>
                <th style={{ ...th, width: 120 }}>Case No</th>
                <th style={{ ...th, width: 80 }}>PO No</th>
                <th style={{ ...th, width: 100 }}>Part No</th>
                <th style={{ ...th, width: 160 }}>Destination</th>
                <th style={{ ...th, textAlign: 'right' }}>Qty</th>
                <th style={{ ...th, width: 80, textAlign: 'right', paddingRight: 16 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ background: 'var(--color-surface)' }}>
                <td colSpan={7} style={{ padding: '7px 16px', borderBottom: '1px solid #e3e6ea' }}>
                  <strong>{part}</strong>
                  <span style={{ marginLeft: 10, fontSize: 12, color: 'var(--color-neutral-600)' }}>
                    {plural(draft.length, 'case')} · {totalQty} pcs
                  </span>
                </td>
              </tr>
              {draft.map((item, index) => (
                <tr key={item.id}>
                  <td style={{ ...td, paddingLeft: 16, color: 'var(--color-neutral-600)', fontVariantNumeric: 'tabular-nums' }}>{String(index + 1).padStart(2, '0')}</td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{item.id}</td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)', color: 'var(--color-accent-800)', fontWeight: 600 }}>{item.po}</td>
                  <td style={{ ...td, fontWeight: 600 }}>{item.part}</td>
                  <td style={td}>{item.destination}</td>
                  <td style={{ ...td, textAlign: 'right', fontWeight: 700 }}>{item.qty}</td>
                  <td style={{ ...td, textAlign: 'right', paddingRight: 16 }}>
                    {!readOnly && (
                      <button
                        type="button"
                        onClick={() => removeFromAsnDraft(item.id)}
                        title="Remove from ASN"
                        className="remove-btn-hover"
                        style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 30, height: 30, borderRadius: 4, display: 'grid', placeItems: 'center', color: 'var(--color-danger)' }}
                      >
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
        ) : (
          <div style={{ padding: '36px 20px', textAlign: 'center', fontSize: 13, color: 'var(--color-neutral-700)' }}>No cases in this ASN. Go back and select at least one case.</div>
        )}
      </div>

      {!readOnly && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'flex-end' }}>
          <span style={{ marginRight: 'auto', fontSize: 12, color: 'var(--color-neutral-600)' }}>1 ASN can contain several POs; each case holds one part.</span>
          <button className="btn btn-secondary" onClick={backToDeliveryPlan}>Cancel</button>
          <button className="btn btn-primary" onClick={submitAsn} disabled={!draft.length || !deliveryDate}>Submit ASN</button>
        </div>
      )}
    </div>
  );
}

function SummaryCell({ label, value, note, mono = false }: { label: string; value: string; note: string; mono?: boolean }) {
  return (
    <div style={{ padding: '12px 18px', borderRight: '1px solid #e3e6ea', display: 'flex', flexDirection: 'column', gap: 3 }}>
      <div style={{ fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', fontWeight: 600 }}>{label}</div>
      <div style={{ fontFamily: mono ? 'var(--font-mono)' : undefined, fontWeight: 700, fontSize: 14 }}>{value}</div>
      <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>{note}</div>
    </div>
  );
}
