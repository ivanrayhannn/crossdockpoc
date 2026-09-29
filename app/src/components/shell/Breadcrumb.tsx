import type { ReactNode } from 'react';

/** Generic "Home / group / label" trail, with an optional right-aligned slot (used by BreadcrumbBar for the role switcher). */
export function Breadcrumb({ group, label, right }: { group: string; label: string; right?: ReactNode }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 24px', background: '#fff', borderBottom: '1px solid #e3e6ea' }}>
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#6c757d" strokeWidth="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
        <path d="M9 22V12h6v10" />
      </svg>
      <a href="#home">Home</a>
      <span style={{ color: '#c1c9d2' }}>/</span>
      <span style={{ color: '#6c757d' }}>{group}</span>
      <span style={{ color: '#c1c9d2' }}>/</span>
      <span style={{ color: '#3a4757', fontWeight: 700 }}>{label}</span>
      {right && <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12, fontSize: 12, color: '#6c757d' }}>{right}</span>}
    </div>
  );
}
