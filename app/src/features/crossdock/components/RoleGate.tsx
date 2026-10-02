import type { UserRole } from '../../../types';

// Prototype-only entry screen: in the real system the sub-menu opens according to the logged-in account.
const SUB_MENUS: { key: UserRole; title: string; desc: string }[] = [
  { key: 'procurement', title: 'Part List', desc: 'Manage part identity: Part No, Pcs/Case, Max Case/Day, Min MAD.' },
  { key: 'ds', title: 'Mapping per Destination', desc: "Split each part's Max Case/Day across destinations (Thailand, Japan, Vietnam)." },
];

export function RoleGate({ onSelect }: { onSelect: (role: UserRole) => void }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '72px 24px', gap: 6 }}>
      <h2 style={{ fontSize: 22, margin: '0 0 4px' }}>Choose a sub-menu to preview</h2>
      <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: '0 0 30px', maxWidth: 480, textAlign: 'center' }}>
        Simulation only — in the real system the sub-menu opens according to the logged-in user account.
      </p>
      <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', justifyContent: 'center' }}>
        {SUB_MENUS.map((m) => (
          <button
            key={m.key}
            onClick={() => onSelect(m.key)}
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
            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>{m.title}</div>
            <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', lineHeight: 1.5 }}>{m.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
