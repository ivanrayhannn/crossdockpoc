import { useEffect, useRef } from 'react';
import type { SaveNotice } from '../useCrossdockState';

/** Popup shown after a part is added or edited from the Part List form. */
export function SaveSuccessModal({ notice, onClose }: { notice: SaveNotice; onClose: () => void }) {
  const okRef = useRef<HTMLButtonElement>(null);
  useEffect(() => okRef.current?.focus(), []);

  const verb = notice.mode === 'add' ? 'added' : 'updated';

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="save-success-title"
      onKeyDown={(e) => e.key === 'Escape' && onClose()}
      style={{ position: 'fixed', inset: 0, zIndex: 110, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}
    >
      <div style={{ width: 380, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '26px 28px 20px', textAlign: 'center' }}>
        <span
          style={{ width: 52, height: 52, borderRadius: 999, margin: '0 auto 14px', display: 'grid', placeItems: 'center', background: 'var(--color-accent-2-200)', color: 'var(--color-accent-2-800)' }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="5 12.5 10 17.5 19 7.5" />
          </svg>
        </span>
        <h3 id="save-success-title" style={{ fontSize: 19, margin: '0 0 6px' }}>
          Saved successfully
        </h3>
        <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: '0 0 18px' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{notice.part}</span>
          {notice.name && ` · ${notice.name}`} has been {verb}. It is now at the top of the Part List.
        </p>
        <button ref={okRef} className="btn btn-primary" onClick={onClose} style={{ minWidth: 96 }}>
          OK
        </button>
      </div>
    </div>
  );
}
