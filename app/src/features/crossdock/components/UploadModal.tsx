import type { CrossdockState } from '../useCrossdockState';

// Same columns and order as sheet "Upload" of the Part List Export Excel.
const UP_COLS = ['part_no', 'min_mad', 'pcs_case', 'max_case_day', 'status', 'flag_add_edit', 'effective_start_date'];

const UP_RULES: { label: string; cols: string }[] = [
  { label: 'Add', cols: 'part_no, min_mad, pcs_case, max_case_day, flag_add_edit = A and effective_start_date are required. Leave status blank — a new part is always Candidate.' },
  { label: 'Edit', cols: 'flag_add_edit = E. min_mad (required), pcs_case and max_case_day can be changed; effective_start_date only while the part status is still Candidate. Download Export Excel first: its sheet "Upload" is the base file (pre-filled with flag E) to edit and upload again.' },
  { label: 'Status', cols: 'The status of a Candidate part cannot be changed by upload (the row is rejected). An Active part can be changed to Inactive and an Inactive part to Active. No part can be changed to Candidate.' },
];

export function UploadModal({ state }: { state: CrossdockState }) {
  const { closeModal, submitUpload } = state;
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
      <div style={{ width: 720, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '24px 28px 22px' }}>
        <h3 style={{ fontSize: 22, margin: '0 0 3px' }}>Upload Excel — part settings</h3>
        <p style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', margin: '0 0 16px' }}>One row = one part. The flag_add_edit column marks the row as A = Add (new part) or E = Edit (already registered part).</p>
        <div style={{ padding: '15px 16px', borderRadius: 16, background: 'var(--color-surface)', marginBottom: 13 }}>
          <div style={{ fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', marginBottom: 9 }}>Template columns</div>
          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            {UP_COLS.map((c) => (
              <span key={c} style={{ fontFamily: 'var(--font-mono)', fontSize: 11.5, padding: '3px 10px', borderRadius: 999, background: 'var(--color-neutral-100)', border: '1px solid var(--color-divider)' }}>
                {c}
              </span>
            ))}
          </div>
        </div>
        <div style={{ padding: '13px 16px', borderRadius: 16, background: 'var(--color-surface)', marginBottom: 13, display: 'flex', flexDirection: 'column', gap: 9 }}>
          <div style={{ fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-neutral-700)' }}>Rules per flag_add_edit and status</div>
          {UP_RULES.map((r) => (
            <div key={r.label} style={{ display: 'flex', gap: 9, fontSize: 12, alignItems: 'flex-start' }}>
              <span style={{ flex: 'none', fontWeight: 700, fontFamily: 'var(--font-mono)', width: 48 }}>{r.label}</span>
              <span style={{ color: 'var(--color-neutral-700)' }}>{r.cols}</span>
            </div>
          ))}
        </div>
        <div style={{ padding: 30, borderRadius: 8, border: '2px dashed var(--color-neutral-400)', textAlign: 'center', marginBottom: 15 }}>
          <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 3 }}>Drag the file here</div>
          <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginBottom: 13 }}>.xlsx max 5 MB · max 5,000 rows</div>
          <button className="btn btn-secondary">Choose file</button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <button className="btn btn-ghost" style={{ color: 'var(--color-accent-700)', fontSize: 12.5 }}>
            Download template .xlsx
          </button>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={closeModal}>
              Close
            </button>
            <button className="btn btn-primary" onClick={() => submitUpload('part')} title="Validate the uploaded file and save it">
              Validate file
            </button>
          </span>
        </div>
      </div>
    </div>
  );
}
