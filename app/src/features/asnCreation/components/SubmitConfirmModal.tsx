import type { PartGroupView } from '../asnEngine';
import { plural } from '../asnEngine';
import type { AsnCreationState } from '../useAsnCreation';

export function SubmitConfirmModal({
  state,
  draftCount,
  draftQty,
  groups,
  dlvText,
}: {
  state: AsnCreationState;
  draftCount: number;
  draftQty: number;
  groups: PartGroupView[];
  dlvText: string;
}) {
  const { closeConfirm, submitAsn } = state;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(20,30,45,.45)', display: 'grid', placeItems: 'center' }}>
      <div style={{ width: 520, background: '#fff', borderRadius: 8, boxShadow: 'var(--shadow-lg)', overflow: 'hidden' }}>
        <div style={{ padding: '18px 22px 6px' }}>
          <h3 style={{ fontSize: 18 }}>Submit ASN?</h3>
          <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 4 }}>
            {plural(draftCount, 'case')} · {draftQty} pcs · delivery {dlvText}
          </div>
        </div>
        <div style={{ padding: '8px 22px 0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
            <tbody>
              {groups.map((g) => (
                <tr key={g.part}>
                  <td style={{ padding: '6px 0', borderBottom: '1px solid #eef1f5', fontWeight: 600 }}>{g.part}</td>
                  <td style={{ padding: '6px 0', borderBottom: '1px solid #eef1f5', color: 'var(--color-neutral-700)' }}>{g.meta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div
          style={{
            margin: '14px 22px 0',
            display: 'flex',
            gap: 9,
            padding: '10px 12px',
            borderRadius: 6,
            background: 'var(--color-warn-bg)',
            border: '1px solid var(--color-neutral-400)',
            color: 'var(--color-warn-fg)',
            fontSize: 12.5,
            lineHeight: 1.45,
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ flex: 'none', marginTop: 1 }}>
            <rect x="5" y="11" width="14" height="10" rx="2" />
            <path d="M8 11V8a4 4 0 0 1 8 0v3" />
          </svg>
          <span>After submitting, these cases are locked in this ASN and cannot be selected for another ASN.</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, padding: '16px 22px 18px' }}>
          <button className="btn btn-secondary" onClick={closeConfirm}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={submitAsn}>
            Submit ASN
          </button>
        </div>
      </div>
    </div>
  );
}
