import { useState } from 'react';
import { card, th, td } from '../asnCrossdock/styles';
import { SIM } from './simData';
import type { Mark, SimTable } from './types';

const MARK_BG: Record<'y' | 'r', string> = { y: '#fff3a3', r: '#f8cbad' };
const BAD = /SALAH/;

function Table({ t, sub }: { t: SimTable; sub?: string }) {
  const bad = BAD.test(t.title);
  return (
    <div style={{ ...card, overflow: 'hidden', borderColor: bad ? 'var(--color-danger)' : undefined }}>
      <div style={{ padding: '9px 12px', fontSize: 12.5, fontWeight: 600, color: bad ? 'var(--color-danger)' : undefined }}>
        {t.title}{sub && <span style={{ fontWeight: 400, color: 'var(--color-neutral-700)', marginLeft: 8 }}>{sub}</span>}
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
          <thead><tr>{t.headers.map((h, i) => <th key={i} style={{ ...th, whiteSpace: 'nowrap' }}>{h}</th>)}</tr></thead>
          <tbody>
            {t.rows.map((r, i) => (
              <tr key={i}>{r.cells.map((c, j) => {
                const m: Mark = r.mark[j];
                const note = /NOTE/i.test(t.headers[j] ?? '');
                return <td key={j} style={{ ...td, background: m ? MARK_BG[m] : undefined, whiteSpace: note ? 'normal' : 'nowrap', minWidth: note ? 340 : undefined }}>{c}</td>;
              })}</tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** simulasi_asn_rev.xlsx day by day: H0253 in G-System and in NSP (replicate), XD09 Search, and the NSP tables. */
export function AsnSimulationPage() {
  const tabs = [...SIM.days.map((d) => d.date), 'Tables'];
  const [tab, setTab] = useState(tabs[0]);
  const day = SIM.days.find((d) => d.date === tab);
  const searches = SIM.searches.filter((s) => s.date === tab);
  const notes = SIM.notes.filter((n) => n.startsWith(tab) || (tab === 'Tables' && !/^\d\d\//.test(n)));

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>ASN Simulation</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          Same data as <b>simulasi_asn_rev.xlsx</b> (PART-X, 6 pcs/case, 16–22 Oct): one PO per Customer Order Date (PO date = order date + 1), a short PO with split PO,
          4 destinations, a cancel of a middle row after ASN (Change Order Number) and one line in 2 ASNs with a serial split. Yellow = changed, orange = abnormality.
        </div>
      </div>

      <div style={{ ...card, padding: '10px 14px', display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {tabs.map((t) => (
          <button key={t} className={t === tab ? 'btn btn-primary' : 'btn btn-secondary'} style={{ padding: '4px 12px', fontSize: 12 }} onClick={() => setTab(t)}>
            {t === 'Tables' ? 'NSP tables (all days)' : t.slice(0, 5)}
          </button>
        ))}
      </div>

      {day && day.blocks.map((b, i) => <Table key={i} t={b} sub={b.table} />)}
      {searches.map((s, i) => <Table key={`s${i}`} t={s} sub="#TEMP_INSTRUCTION (XD09)" />)}
      {tab === 'Tables' && SIM.ref.map((t, i) => <Table key={`r${i}`} t={t} />)}
      {tab === 'Tables' && <div style={{ fontSize: 12, color: 'var(--color-neutral-700)' }}>{SIM.intro}</div>}
      {notes.map((n, i) => <div key={`n${i}`} style={{ ...card, padding: '8px 12px', fontSize: 12 }}>{n}</div>)}
    </div>
  );
}
