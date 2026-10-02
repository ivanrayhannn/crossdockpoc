import type { TabView } from '../../../types';

const LABEL: Record<TabView, string> = {
  part: 'Part List',
  dest: 'Mapping per Destination',
};

/** Only one sub-menu is ever reachable per account, so this is a wayfinding
 * label rather than a switcher — there is nothing else to click into. */
export function ViewTabs({ view }: { view: TabView }) {
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
        }}
      >
        {LABEL[view]}
      </span>
    </div>
  );
}
