import type { TabView } from '../../../types';

const LABEL: Record<TabView, string> = {
  part: 'Part List',
  detail: 'Part Detail',
  dest: 'Mapping per Destination',
};

/** Procurement opens two sub-menus (Part List, Part Detail) and can switch between them;
 * D/S only opens Mapping per Destination, so its tab is a wayfinding label. */
export function ViewTabs({ view, onChange }: { view: TabView; onChange?: (v: 'part' | 'detail') => void }) {
  const tabs: TabView[] = view === 'dest' ? ['dest'] : ['part', 'detail'];
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, padding: '18px 0 0', borderBottom: '1px solid var(--color-divider)', margin: '0 28px' }}>
      {tabs.map((t) => {
        const active = t === view;
        return (
          <button
            key={t}
            onClick={() => t !== 'dest' && onChange?.(t)}
            style={{
              cursor: t === 'dest' ? 'default' : 'pointer',
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
