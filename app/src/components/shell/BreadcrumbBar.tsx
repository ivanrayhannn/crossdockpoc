export function BreadcrumbBar({ roleLabel, onSwitchRole }: { roleLabel: string; onSwitchRole?: () => void }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 24px', background: '#fff', borderBottom: '1px solid #e3e6ea' }}>
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6c757d" strokeWidth="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
        <path d="M9 22V12h6v10" />
      </svg>
      <a href="#home">Home</a>
      <span style={{ color: '#c1c9d2' }}>/</span>
      <span style={{ color: '#6c757d' }}>Master</span>
      <span style={{ color: '#c1c9d2' }}>/</span>
      <span style={{ color: '#3a4757', fontWeight: 700 }}>Crossdock Master Setting</span>
      <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12, fontSize: 12, color: '#6c757d' }}>
        <span>
          Role <span style={{ fontFamily: 'var(--font-mono)', color: '#3a4757', fontWeight: 600 }}>{roleLabel}</span>
        </span>
        {onSwitchRole && (
          <button onClick={onSwitchRole} className="btn btn-secondary" style={{ fontSize: 11.5, padding: '3px 11px' }}>
            Ganti role
          </button>
        )}
      </span>
    </div>
  );
}
