import type { CrossdockState } from '../useCrossdockState';

// Same columns and order as sheet "Upload" of the Mapping per Destination Export Excel.
const UP_COLS = ['part_no', 'dest_code', 'case_day', 'total_case_day'];

const UP_RULES: { label: string; cols: string }[] = [
  { label: 'Rows', cols: 'One row = one destination of a part in the ongoing calculation period. Only Active parts can be uploaded; past periods are read only.' },
  { label: 'Replace', cols: 'A part in the file gets its whole mapping replaced by its rows: destinations not in the file are removed. Parts not in the file are not changed.' },
  { label: 'Limits', cols: 'dest_code from the destination master, once per part. case_day is a whole number greater than 0. The total case_day of a part may not exceed its Max Case/Day (total_case_day is shown for reference and is not read).' },
  { label: 'Base', cols: 'Download Export Excel first with the ongoing period selected: its sheet "Upload" is the base file. A part without mapping has one row with dest_code and case_day blank — fill both to map it, or leave both blank to skip it.' },
];

export function MappingUploadModal({ state }: { state: CrossdockState }) {
  const { closeModal, submitUpload } = state;
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
      <div style={{ width: 720, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '24px 28px 22px' }}>
        <h3 style={{ fontSize: 22, margin: '0 0 3px' }}>Upload Excel — destination mapping</h3>
        <p style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', margin: '0 0 16px' }}>Splits the Max Case/Day of each Active part over destinations for the ongoing calculation period.</p>
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
          <div style={{ fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-neutral-700)' }}>Upload rules</div>
          {UP_RULES.map((r) => (
            <div key={r.label} style={{ display: 'flex', gap: 9, fontSize: 12, alignItems: 'flex-start' }}>
              <span style={{ flex: 'none', fontWeight: 700, fontFamily: 'var(--font-mono)', width: 58 }}>{r.label}</span>
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
            <button className="btn btn-primary" onClick={() => submitUpload('mapping')} title="Validate the uploaded file and save it">
              Validate file
            </button>
          </span>
        </div>
      </div>
    </div>
  );
}
