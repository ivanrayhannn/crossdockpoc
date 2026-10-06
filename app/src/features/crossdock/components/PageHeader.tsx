import type { TabView } from '../../../types';

interface PageHeaderProps {
  ro: boolean;
  view: TabView;
  onAddPart: () => void;
  onOpenUpload: () => void;
  onExport: () => void;
}

export function PageHeader({ ro, view, onAddPart, onOpenUpload, onExport }: PageHeaderProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 24, padding: '20px 28px 0' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 11.5, color: 'var(--color-neutral-600)', marginBottom: 5 }}>
          <span>Master</span>
          <span>/</span>
          <span>Crossdock</span>
          <span>/</span>
          <span style={{ color: 'var(--color-text)' }}>Setting Part</span>
        </div>
        <h1 style={{ fontSize: 31, margin: '0 0 4px' }}>Crossdock Master — Setting Part</h1>
      </div>
      <div style={{ marginLeft: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 10 }}>
        {view === 'part' && (
          <div style={{ display: 'flex', gap: 8 }}>
            {!ro && (
              <button className="btn btn-primary" onClick={onAddPart} style={{ fontSize: 13 }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add Part
              </button>
            )}
            {!ro && (
              <button className="btn btn-secondary" onClick={onOpenUpload} style={{ fontSize: 13 }}>
                Upload Excel
              </button>
            )}
            <button className="btn btn-secondary" onClick={onExport} style={{ fontSize: 13 }}>
              Export Excel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
