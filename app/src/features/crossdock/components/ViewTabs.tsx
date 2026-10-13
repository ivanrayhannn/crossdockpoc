import type { TabView } from '../../../types';

const LABEL: Record<TabView, string> = {
  part: 'Part List',
  dest: 'Mapping per Destination',
};

/** Each account opens exactly one sub-menu (Procurement: Part List, D/S: Mapping per Destination),
 * so the tab is a wayfinding label only. */
export function ViewTabs({ view }: { view: TabView }) {
  const tabs: TabView[] = [view];
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, padding: '18px 0 0', borderBottom: '1px solid var(--color-divider)', margin: '0 28px' }}>
      {tabs.map((t) => {
        const active = t === view;
        return (
          <button
            key={t}
                        style={{
              cursor: 'default',
              border: 0,
              background: 'transparent',
              fontFamily: 'var(--font-body)',
              fontSize: 13.5,
              fontWeight: active ? 700 : 500,
              padding: '9px 16px',
              color: active ? 'var(--color-text)' : 'var(--color-neutral-600)',
              borderBottom: active ? '2px solid var(--color-neutral-800)' : '2px solid transparent',
              marginBottom: -1,
            }}
          >
            {LABEL[t]}
          </button>
        );
      })}
    </div>
  );
}
