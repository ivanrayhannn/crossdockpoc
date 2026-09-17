const NAV_GROUPS: [string, string[]][] = [
  ['Ordering', ['Service Part Order']],
  ['ASN', ['Case Label Printing', 'ASN Creation', 'Delivery Note Creation', 'ASN Inquiry']],
  ['Transfer Posting', ['Stock Inquiry']],
  ['Timeline', ['Timeline']],
  ['Master', ['Sub Supplier Maintenance', 'Part Master Maintenance', 'Crossdock Master Setting']],
  ['Forecast', ['Forecast Inquiry']],
  ['Common', ['Log Monitoring', 'System Master Maintenance']],
  ['Inventory Taking', ['Intak Period Maintenance', 'Yellow Line and CY Stock']],
];

const ACTIVE_ITEM = 'Crossdock Master Setting';
const OPEN_GROUP = 'Master';

export function Sidebar() {
  return (
    <aside
      style={{
        width: 250,
        flexShrink: 0,
        background: '#fff',
        borderRight: '1px solid #e3e6ea',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div style={{ height: 52, display: 'flex', alignItems: 'center', gap: 10, padding: '0 14px', background: '#2b3c5b' }}>
        <span
          style={{
            width: 26,
            height: 26,
            borderRadius: 6,
            background: '#dc3545',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 700,
            fontSize: 13,
          }}
        >
          N
        </span>
        <span style={{ color: '#fff', fontWeight: 700, fontSize: 18, letterSpacing: '.02em' }}>NSP</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: 14, borderBottom: '1px solid #eef1f5' }}>
        <span
          style={{
            width: 34,
            height: 34,
            borderRadius: 999,
            background: '#e9edf2',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#8a97a6',
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21a8 8 0 0 1 16 0" />
          </svg>
        </span>
        <div style={{ lineHeight: 1.2 }}>
          <div style={{ fontSize: 11, color: '#8a97a6' }}>Welcome,</div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#3a4757' }}>NSP ADMIN</div>
        </div>
      </div>

      <nav style={{ padding: '8px 8px 20px' }}>
        {NAV_GROUPS.map(([label, items]) => {
          const open = label === OPEN_GROUP;
          return (
            <div key={label}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '9px 10px',
                  color: '#3a4757',
                  fontSize: 13.5,
                  borderRadius: 6,
                  marginTop: 2,
                  background: open ? '#f1f5f9' : 'transparent',
                }}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9aa6b3" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                </svg>
                <span style={{ flex: 1, fontWeight: 600 }}>{label}</span>
                <span style={{ color: '#aab4bf', fontSize: 12, transform: `rotate(${open ? -90 : 0}deg)` }}>›</span>
              </div>
              <div style={{ padding: '2px 0 4px 4px', display: open ? 'block' : 'none' }}>
                {items.map((item) => {
                  const active = item === ACTIVE_ITEM;
                  return (
                    <div
                      key={item}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 9,
                        padding: '7px 10px 7px 28px',
                        fontSize: 12.5,
                        borderRadius: 6,
                        marginTop: 1,
                        background: active ? '#dc3545' : 'transparent',
                        color: active ? '#fff' : '#5a6672',
                        fontWeight: active ? 600 : 400,
                      }}
                    >
                      <span style={{ width: 5, height: 5, borderRadius: 999, background: active ? '#fff' : '#c1c9d2' }} />
                      {item}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
