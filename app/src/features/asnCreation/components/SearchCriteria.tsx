import { PART_NOS, SUPPLIER_CODES } from '../data';
import type { AsnCreationState } from '../useAsnCreation';

export function SearchCriteria({ state }: { state: AsnCreationState }) {
  const { filter, setFilterField, search, resetFilter } = state;

  return (
    <div style={{ background: '#fff', border: '1px solid #e3e6ea', borderRadius: 6 }}>
      <div style={{ padding: '10px 16px', borderBottom: '1px solid #e3e6ea', fontSize: 14, fontWeight: 700 }}>Searching Criteria</div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '12px 14px', padding: '12px 16px', flexWrap: 'wrap' }}>
        <div className="field">
          <label>Delivery Plan · From</label>
          <input className="input" type="date" value={filter.from} onChange={(e) => setFilterField('from', e.target.value)} style={{ width: 156 }} />
        </div>
        <div className="field">
          <label>To</label>
          <input className="input" type="date" value={filter.to} onChange={(e) => setFilterField('to', e.target.value)} style={{ width: 156 }} />
        </div>
        <div className="field">
          <label>Supplier Code</label>
          <select className="input" value={filter.sup} onChange={(e) => setFilterField('sup', e.target.value)} style={{ width: 120, fontFamily: 'var(--font-mono)', appearance: 'none' }}>
            {SUPPLIER_CODES.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>PO Number</label>
          <input
            className="input"
            value={filter.po}
            onChange={(e) => setFilterField('po', e.target.value)}
            placeholder="e.g. PO2"
            style={{ width: 120, fontFamily: 'var(--font-mono)' }}
          />
        </div>
        <div className="field">
          <label>Part No</label>
          <select className="input" value={filter.part} onChange={(e) => setFilterField('part', e.target.value)} style={{ width: 130, appearance: 'none' }}>
            <option value="all">All</option>
            {PART_NOS.map((part) => (
              <option key={part} value={part}>
                {part}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Destination</label>
          <select className="input" value={filter.dest} onChange={(e) => setFilterField('dest', e.target.value)} style={{ width: 160, appearance: 'none' }}>
            <option value="all">All</option>
            <option value="VN">Vietnam · 789</option>
            <option value="JP">Japan · 456</option>
            <option value="TH">Thailand · 123</option>
          </select>
        </div>
        <div className="field">
          <label>Case Status</label>
          <select className="input" value={filter.st} onChange={(e) => setFilterField('st', e.target.value as typeof filter.st)} style={{ width: 150, appearance: 'none' }}>
            <option value="all">All</option>
            <option value="avail">Not in ASN</option>
            <option value="asn">In ASN</option>
          </select>
        </div>
        <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary" onClick={resetFilter}>
            Reset
          </button>
          <button className="btn btn-primary" onClick={search}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" />
              <line x1="16.5" y1="16.5" x2="21" y2="21" />
            </svg>
            Search
          </button>
        </span>
      </div>
    </div>
  );
}
