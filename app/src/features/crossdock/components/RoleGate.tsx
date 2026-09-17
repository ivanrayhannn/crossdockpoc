import type { UserRole } from '../../../types';

const ROLES: { key: UserRole; title: string; desc: string; menu: string }[] = [
  { key: 'procurement', title: 'Procurement', desc: 'Kelola identitas part: Part No, Pcs/Case, Max Case/Day, Min MAD.', menu: 'Daftar Part' },
  { key: 'ds', title: 'Tim D/S', desc: 'Bagi Max Case/Day tiap part ke destinasi (Thailand, Jepang, Vietnam).', menu: 'Mapping per Destinasi' },
];

export function RoleGate({ onSelect }: { onSelect: (role: UserRole) => void }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '72px 24px', gap: 6 }}>
      <h2 style={{ fontSize: 22, margin: '0 0 4px' }}>Pilih role untuk simulasi</h2>
      <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: '0 0 30px', maxWidth: 480, textAlign: 'center' }}>
        Dummy simulasi — role menentukan sub-menu apa yang tampil. Procurement hanya melihat Daftar Part, Tim D/S hanya melihat Mapping per Destinasi.
      </p>
      <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', justifyContent: 'center' }}>
        {ROLES.map((r) => (
          <button
            key={r.key}
            onClick={() => onSelect(r.key)}
            style={{
              cursor: 'pointer',
              textAlign: 'left',
              width: 280,
              padding: '22px 20px',
              border: '1px solid var(--color-divider)',
              borderRadius: 14,
              background: 'var(--color-neutral-100)',
              fontFamily: 'var(--font-body)',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>{r.title}</div>
            <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginBottom: 14, lineHeight: 1.5 }}>{r.desc}</div>
            <span style={{ display: 'inline-flex', fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999, background: 'var(--color-accent-200)', color: 'var(--color-accent-800)' }}>
              {r.menu}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
