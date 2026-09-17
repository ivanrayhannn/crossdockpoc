import { HIST_BY_PART } from '../../../data/seed';
import type { CrossdockState } from '../useCrossdockState';

export function HistoryModal({ state }: { state: CrossdockState }) {
  const { form: f, closeModal } = state;
  if (!f) return null;
  const hist = HIST_BY_PART[f.p] || [];

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 40 }}>
      <div style={{ width: 600, maxHeight: '86vh', overflow: 'auto', background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '24px 28px 22px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 13, marginBottom: 18 }}>
          <div>
            <h3 style={{ fontSize: 22, margin: '0 0 2px' }}>History setting</h3>
            <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{f.p}</span> · {f.n}
            </div>
          </div>
          <button
            onClick={closeModal}
            title="Tutup"
            style={{ marginLeft: 'auto', cursor: 'pointer', border: 0, background: 'var(--color-neutral-200)', width: 32, height: 32, borderRadius: 999, display: 'grid', placeItems: 'center' }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
              <line x1="5" y1="5" x2="19" y2="19" />
              <line x1="19" y1="5" x2="5" y2="19" />
            </svg>
          </button>
        </div>

        {hist.length === 0 && <p style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', margin: '0 0 18px' }}>Belum ada riwayat perubahan untuk part ini.</p>}

        {hist.map((h, i) => (
          <div key={i} style={{ display: 'flex', gap: 14 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 24 }}>
              <span style={{ width: 11, height: 11, borderRadius: 999, background: h.accent ? 'var(--color-accent)' : 'var(--color-neutral-400)' }} />
              <span style={{ width: 2, flex: 1, background: 'var(--color-neutral-300)' }} />
            </div>
            <div style={{ paddingBottom: 16, flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 5 }}>
                <span style={{ fontSize: 13, fontWeight: 700 }}>{h.t}</span>
                <span style={{ fontSize: 11.5, color: 'var(--color-neutral-600)', marginLeft: 'auto', fontVariantNumeric: 'tabular-nums' }}>{h.w}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontSize: 12.5, padding: '7px 11px', borderRadius: 12, background: 'var(--color-surface)', fontVariantNumeric: 'tabular-nums' }}>
                <span style={{ color: 'var(--color-neutral-700)' }}>{h.f}</span>
                <span style={{ textDecoration: 'line-through', color: 'var(--color-neutral-600)' }}>{h.o}</span>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--color-neutral-700)" strokeWidth="2.75" strokeLinecap="round">
                  <line x1="4" y1="12" x2="19" y2="12" />
                  <polyline points="14 7 19 12 14 17" />
                </svg>
                <span style={{ fontWeight: 700 }}>{h.n}</span>
                <span style={{ marginLeft: 'auto', fontSize: 11.5, color: 'var(--color-neutral-700)' }}>{h.by}</span>
              </div>
            </div>
          </div>
        ))}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button className="btn btn-primary" onClick={closeModal}>
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
}
