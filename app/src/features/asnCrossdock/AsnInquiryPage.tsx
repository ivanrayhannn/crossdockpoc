import { useState } from 'react';
import { useAsns } from './asnStore';
import { caseNoOf, niceDate, PART_NAME, type SubmittedAsn } from './data';
import { CaseTable, Chip, Modal } from './ui';
import { card, th, td } from './styles';

interface Query {
  asn: string;
  from: string;
  to: string;
  part: string;
}
const EMPTY: Query = { asn: '', from: '', to: '', part: '' };

function matches(a: SubmittedAsn, q: Query): boolean {
  if (q.asn && !a.asnNo.toLowerCase().includes(q.asn.toLowerCase())) return false;
  if (q.from && a.deliveryDate < q.from) return false;
  if (q.to && a.deliveryDate > q.to) return false;
  if (q.part && !a.cases.some((c) => c.partNo === q.part)) return false;
  return true;
}

function unitsOf(a: SubmittedAsn): string {
  return a.unitKeys.map((k) => { const [p, d] = k.split('|'); return `${p} · ${niceDate(d)}`; }).join(', ');
}

/** Screen ASN Inquiry: submitted ASNs with their cases (read only). */
export function AsnInquiryPage() {
  const asns = useAsns();
  const [filter, setFilter] = useState<Query>(EMPTY);
  const [query, setQuery] = useState<Query>(EMPTY);
  const [view, setView] = useState<SubmittedAsn | null>(null);
  const [labelNote, setLabelNote] = useState(false);
  const rows = asns.filter((a) => matches(a, query));

  if (view) {
    const qty = view.cases.reduce((s, c) => s + c.qty, 0);
    return (
      <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div><button className="btn btn-secondary" onClick={() => setView(null)} style={{ fontSize: 12, padding: '4px 12px' }}>← Back to ASN Inquiry</button></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h1 style={{ fontSize: 22, margin: 0, fontFamily: 'var(--font-mono)' }}>{view.asnNo}</h1>
          <Chip tone="ok">Created</Chip>
        </div>
        <div style={{ ...card, padding: 16, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, fontSize: 12.5 }}>
          <div><div className="ax-lbl">Delivery Date</div><b>{niceDate(view.deliveryDate)}</b></div>
          <div><div className="ax-lbl">Rit Cycle · Route</div><b>{view.rit.no} · {view.rit.route}</b></div>
          <div><div className="ax-lbl">Part / Customer Order Date</div><b>{unitsOf(view)}</b></div>
          <div><div className="ax-lbl">Cases · Qty · Created</div><b>{view.cases.length} cases · {qty} pcs</b><div className="ax-muted">{view.createdBy} · {view.createdAt}</div></div>
        </div>
        <div style={{ ...card }}>
          <div style={{ display: 'flex', alignItems: 'center', padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
            <span style={{ fontSize: 12.5, fontWeight: 600, marginRight: 'auto' }}>Cases in this ASN</span>
            <button className="btn btn-secondary" onClick={() => setLabelNote(true)}>Download Case Label</button>
          </div>
          <CaseTable cases={view.cases} caseLabel={(c) => caseNoOf(view.asnNo, c.seq)} />
        </div>
        {labelNote && (
          <Modal title="Download Case Label" onClose={() => setLabelNote(false)} actions={<button className="btn btn-primary" onClick={() => setLabelNote(false)}>OK</button>}>
            Label format and content are not defined yet (TBD). {view.cases.length} labels would be printed.
          </Modal>
        )}
      </div>
    );
  }

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>ASN Inquiry</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>Submitted ASNs created in ASN Crossdock Creation.</div>
      </div>
      <div style={{ ...card, padding: '14px 16px 16px' }}>
        <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase', marginBottom: 11 }}>Search criteria</div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13 }}>
          <div className="field" style={{ width: 220 }}><label>ASN No</label><input className="input" value={filter.asn} placeholder="e.g. ASN-50221" onChange={(e) => setFilter({ ...filter, asn: e.target.value })} onKeyDown={(e) => e.key === 'Enter' && setQuery(filter)} /></div>
          <div className="field" style={{ width: 160 }}><label>Delivery Date - From</label><input className="input" type="date" value={filter.from} onChange={(e) => setFilter({ ...filter, from: e.target.value })} /></div>
          <div className="field" style={{ width: 160 }}><label>To</label><input className="input" type="date" value={filter.to} onChange={(e) => setFilter({ ...filter, to: e.target.value })} /></div>
          <div className="field" style={{ width: 150 }}>
            <label>Part Number</label>
            <select className="input" value={filter.part} onChange={(e) => setFilter({ ...filter, part: e.target.value })}>
              <option value="">All</option>
              {Object.keys(PART_NAME).map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={() => { setFilter(EMPTY); setQuery(EMPTY); }}>Reset</button>
            <button className="btn btn-primary" onClick={() => setQuery(filter)}>Search</button>
          </span>
        </div>
      </div>
      <div style={{ ...card, overflow: 'hidden' }}>
        <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--color-divider)', fontSize: 12.5, fontWeight: 600 }}>ASN list <span style={{ fontWeight: 400, color: 'var(--color-neutral-600)', fontSize: 11.5 }}>{rows.length} ASN</span></div>
        {rows.length === 0 ? (
          <div style={{ padding: '40px 24px', textAlign: 'center', fontSize: 13 }}>No ASN matches this search.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead><tr>{['ASN No', 'Delivery Date', 'Rit Cycle', 'Route', 'Part / Customer Order Date', 'Cases', 'Qty', 'Status', 'Created'].map((h) => <th key={h} style={th}>{h}</th>)}</tr></thead>
            <tbody>
              {rows.map((a) => (
                <tr key={a.asnNo}>
                  <td style={td}><a href="#" onClick={(e) => { e.preventDefault(); setView(a); }} style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{a.asnNo}</a></td>
                  <td style={td}>{niceDate(a.deliveryDate)}</td>
                  <td style={td}>{a.rit.no}</td>
                  <td style={td}>{a.rit.route}</td>
                  <td style={td}>{unitsOf(a)}</td>
                  <td style={td}>{a.cases.length}</td>
                  <td style={td}>{a.cases.reduce((s, c) => s + c.qty, 0)}</td>
                  <td style={td}><Chip tone="ok">Created</Chip></td>
                  <td style={td}>{a.createdBy}<div className="ax-muted">{a.createdAt}</div></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
