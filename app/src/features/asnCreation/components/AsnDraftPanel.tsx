import { Fragment, useMemo } from 'react';
import { destLabel, groupCasesByPart, plural, sumQty } from '../asnEngine';
import { niceDate, SUPPLIER_CODE, SUPPLIER_NAME, TODAY_ISO } from '../data';
import type { AsnCreationState } from '../useAsnCreation';
import { SubmitConfirmModal } from './SubmitConfirmModal';

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

export function AsnDraftPanel({ state }: { state: AsnCreationState }) {
  const { cases, sel, done, dlv, setDlv, backToList, goToSelect, openConfirm, removeFromDraft, downloadCaseLabel, downloadAllLabels, confirmOpen } = state;

  const ro = !!done;
  const draft = useMemo(() => (done ? cases.filter((c) => done.ids.includes(c.id)) : cases.filter((c) => sel[c.id])), [cases, done, sel]);
  const groups = useMemo(() => groupCasesByPart(draft), [draft]);
  const asnNo = done ? done.no : 'ASN-50221-260929-001';
  const effectiveDlv = done ? done.dlv : dlv;

  let seq = 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, paddingBottom: 28 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="btn btn-secondary" onClick={backToList} style={{ fontSize: 12.5, padding: '5px 12px' }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 6 9 12 15 18" />
          </svg>
          {ro ? 'Back to ASN Creation' : 'Back to case selection'}
        </button>
        <h1 style={{ fontSize: 22 }}>{ro ? asnNo : 'ASN Draft'}</h1>
        <span
          style={{
            fontSize: 11.5,
            fontWeight: 700,
            padding: '2px 10px',
            borderRadius: 999,
            background: ro ? 'var(--color-accent-2-200)' : 'var(--color-neutral-200)',
            color: ro ? 'var(--color-accent-2-800)' : 'var(--color-neutral-700)',
          }}
        >
          {ro ? 'Submitted' : 'Draft'}
        </span>
      </div>

      {ro && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '11px 16px',
            borderRadius: 6,
            background: 'var(--color-accent-2-200)',
            border: '1px solid var(--color-accent-2-300)',
            color: 'var(--color-accent-2-800)',
            fontSize: 13,
          }}
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9" />
            <polyline points="8 12.5 11 15.5 16 9.5" />
          </svg>
          <span>
            <strong>{asnNo} submitted.</strong> {plural(draft.length, 'case')} are locked. Delivery {niceDate(effectiveDlv)}.
          </span>
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,minmax(0,1fr))' }}>
          <div style={{ padding: '12px 18px', borderRight: '1px solid #e3e6ea', display: 'flex', flexDirection: 'column', gap: 3 }}>
            <div style={{ fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', fontWeight: 600 }}>ASN No</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 14 }}>{asnNo}</div>
            <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>{ro ? 'submitted' : 'auto · assigned on submit'}</div>
          </div>
          <div style={{ padding: '12px 18px', borderRight: '1px solid #e3e6ea', display: 'flex', flexDirection: 'column', gap: 3 }}>
            <div style={{ fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', fontWeight: 600 }}>Supplier · Plant</div>
            <div style={{ fontWeight: 700, fontSize: 14 }}>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{SUPPLIER_CODE}</span> · <span style={{ fontFamily: 'var(--font-mono)' }}>P01</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>{SUPPLIER_NAME}</div>
          </div>
          <div style={{ padding: '12px 18px', display: 'flex', flexDirection: 'column', gap: 3 }}>
            <div style={{ fontSize: 10, letterSpacing: '.05em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', fontWeight: 600 }}>Cases · Qty</div>
            <div style={{ fontWeight: 700, fontSize: 14, fontVariantNumeric: 'tabular-nums' }}>
              {plural(draft.length, 'case')} · {sumQty(draft)} pcs
            </div>
          </div>
        </div>
      </div>

      <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderBottom: '1px solid #e3e6ea', flexWrap: 'wrap' }}>
          <span style={{ fontSize: 14, fontWeight: 700 }}>Case list in this ASN</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Grouped by Part No · 1 case = 1 part</span>
          <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600, color: 'var(--color-neutral-700)', whiteSpace: 'nowrap' }}>
              Delivery Date <span style={{ color: 'var(--color-accent-700)', marginLeft: -5 }}>*</span>
              <input
                className="input"
                type="date"
                value={effectiveDlv}
                min={TODAY_ISO}
                onChange={(e) => setDlv(e.target.value)}
                disabled={ro}
                style={{ width: 150, padding: '5px 9px', borderColor: !ro && !dlv ? 'var(--color-danger)' : 'var(--color-neutral-400)' }}
              />
            </label>
            <span style={{ width: 1, height: 22, background: '#e3e6ea' }} />
            {!ro && (
              <button className="btn btn-secondary" onClick={goToSelect}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add cases
              </button>
            )}
            <button className="btn btn-secondary" onClick={() => downloadAllLabels(draft.length)} disabled={!draft.length}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v12M7 10l5 5 5-5M5 21h14" />
              </svg>
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
                <th style={{ ...th, width: 90 }}>Part No</th>
                <th style={{ ...th, width: 150 }}>Destination</th>
                <th style={{ ...th, width: 70, textAlign: 'right' }}>Qty</th>
                <th style={{ ...th, width: 110, textAlign: 'right', paddingRight: 16 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((g) => (
                <Fragment key={g.part}>
                  <tr style={{ background: 'var(--color-surface)' }}>
                    <td colSpan={7} style={{ padding: '7px 16px', borderBottom: '1px solid #e3e6ea' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontSize: 13, fontWeight: 700 }}>{g.part}</span>
                        <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>{g.meta}</span>
                      </span>
                    </td>
                  </tr>
                  {g.rows.map((c) => {
                    seq++;
                    return (
                      <tr key={c.id}>
                        <td style={{ ...td, paddingLeft: 16, fontVariantNumeric: 'tabular-nums', color: 'var(--color-neutral-600)' }}>{String(seq).padStart(2, '0')}</td>
                        <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{c.caseNo}</td>
                        <td style={{ ...td, fontFamily: 'var(--font-mono)', color: 'var(--color-accent-800)', fontWeight: 600 }}>{c.po}</td>
                        <td style={{ ...td, fontWeight: 600 }}>{c.part}</td>
                        <td style={td}>{destLabel(c.dest)}</td>
                        <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700 }}>{c.qty}</td>
                        <td style={{ ...td, paddingRight: 16, textAlign: 'right' }}>
                          <span style={{ display: 'inline-flex', gap: 4 }}>
                            <button
                              onClick={() => downloadCaseLabel(c.caseNo)}
                              title="Download case label"
                              className="icon-btn-hover"
                              style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 30, height: 30, borderRadius: 4, display: 'grid', placeItems: 'center', color: 'var(--color-neutral-800)' }}
                            >
                              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 3v12M7 10l5 5 5-5M5 21h14" />
                              </svg>
                            </button>
                            {!ro && (
                              <button
                                onClick={() => removeFromDraft(c.id)}
                                title="Remove from ASN"
                                className="remove-btn-hover"
                                style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 30, height: 30, borderRadius: 4, display: 'grid', placeItems: 'center', color: 'var(--color-danger)' }}
                              >
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6" />
                                </svg>
                              </button>
                            )}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </Fragment>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, padding: '36px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 14, fontWeight: 700 }}>No cases in this ASN</div>
            <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)' }}>Go back and select at least one case.</div>
          </div>
        )}
      </div>

      {!ro && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'flex-end' }}>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)', marginRight: 'auto' }}>
            {!dlv ? 'Fill in the delivery date to submit.' : '1 ASN can contain several part numbers and POs; each case holds one part.'}
          </span>
          <button className="btn btn-secondary" onClick={backToList}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={openConfirm} disabled={!draft.length || !dlv}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 2 11 13" />
              <path d="M22 2 15 22l-4-9-9-4z" />
            </svg>
            Submit ASN
          </button>
        </div>
      )}

      {confirmOpen && !ro && <SubmitConfirmModal state={state} draftCount={draft.length} draftQty={sumQty(draft)} groups={groups} dlvText={dlv ? niceDate(dlv) : '—'} />}
    </div>
  );
}
