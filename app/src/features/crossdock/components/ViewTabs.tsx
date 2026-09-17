import type { TabView } from '../../../types';

const INFO: Record<TabView, { label: string; badge: string }> = {
  part: { label: 'Daftar Part', badge: 'Procurement' },
  dest: { label: 'Mapping per Destinasi', badge: 'Tim D/S' },
};

/** Only one sub-menu is ever reachable per role, so this is a wayfinding
 * label rather than a switcher — there is nothing else to click into. */
export function ViewTabs({ view }: { view: TabView }) {
  const { label, badge } = INFO[view];
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, padding: '18px 0 0', borderBottom: '1px solid var(--color-divider)', margin: '0 28px' }}>
      <span
        style={{
          fontSize: 13.5,
          fontWeight: 700,
          padding: '9px 16px',
          color: 'var(--color-text)',
          borderBottom: '2px solid var(--color-neutral-800)',
          marginBottom: -1,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        {label}
        <span
          style={{
            fontSize: 9.5,
            fontWeight: 700,
            letterSpacing: '.06em',
            textTransform: 'uppercase',
            padding: '1px 7px',
            borderRadius: 999,
            background: 'var(--color-neutral-200)',
            color: 'var(--color-neutral-700)',
          }}
        >
          {badge}
        </span>
      </span>
    </div>
  );
}
