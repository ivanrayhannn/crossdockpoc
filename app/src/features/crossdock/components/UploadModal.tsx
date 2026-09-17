import type { CrossdockState } from '../useCrossdockState';

const UP_COLS = ['part_no', 'part_name', 'pcs_case', 'max_case_day', 'destinasi', 'case_day', 'status'];

export function UploadModal({ state }: { state: CrossdockState }) {
  const { closeModal } = state;
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
      <div style={{ width: 720, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '24px 28px 22px' }}>
        <h3 style={{ fontSize: 22, margin: '0 0 3px' }}>Upload Excel — setting part</h3>
        <p style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', margin: '0 0 16px' }}>Satu baris = satu kombinasi part + destinasi. Pcs/Case dan Max Case/Day diambil dari baris pertama tiap part.</p>
        <div style={{ padding: '15px 16px', borderRadius: 16, background: 'var(--color-surface)', marginBottom: 13 }}>
          <div style={{ fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', marginBottom: 9 }}>Kolom template</div>
          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            {UP_COLS.map((c) => (
              <span key={c} style={{ fontFamily: 'var(--font-mono)', fontSize: 11.5, padding: '3px 10px', borderRadius: 999, background: 'var(--color-neutral-100)', border: '1px solid var(--color-divider)' }}>
                {c}
              </span>
            ))}
          </div>
        </div>
        <div style={{ padding: 30, borderRadius: 8, border: '2px dashed var(--color-neutral-400)', textAlign: 'center', marginBottom: 15 }}>
          <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 3 }}>Tarik file ke sini</div>
          <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginBottom: 13 }}>.xlsx maksimal 5 MB · maksimal 5.000 baris</div>
          <button className="btn btn-secondary">Pilih file</button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <button className="btn btn-ghost" style={{ color: 'var(--color-accent-700)', fontSize: 12.5 }}>
            Download template .xlsx
          </button>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={closeModal}>
              Tutup
            </button>
            <button className="btn btn-primary" onClick={closeModal}>
              Validasi file
            </button>
          </span>
        </div>
      </div>
    </div>
  );
}
