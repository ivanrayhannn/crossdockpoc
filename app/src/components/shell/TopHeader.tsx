import { useEffect, useState } from 'react';

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function formatClock(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${DAYS[d.getDay()]}, ${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

export function TopHeader() {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header style={{ height: 52, flexShrink: 0, background: '#2b3c5b', display: 'flex', alignItems: 'center', gap: 16, padding: '0 18px' }}>
      <span style={{ color: '#fff', display: 'flex' }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 6h18M3 12h18M3 18h18" />
        </svg>
      </span>
      <span style={{ color: '#fff', fontWeight: 700, fontSize: 16 }}>New Service Part System</span>
      <span style={{ marginLeft: 'auto', color: '#cfd6e0', fontSize: 13, fontVariantNumeric: 'tabular-nums' }}>{formatClock(now)}</span>
      <span style={{ color: '#cfd6e0', display: 'flex' }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4M12 8h.01" />
        </svg>
      </span>
      <span
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 7,
          background: '#dc3545',
          color: '#fff',
          padding: '0 14px',
          height: 52,
          marginRight: -18,
          fontSize: 12.5,
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" />
        </svg>
        Logout
      </span>
    </header>
  );
}
