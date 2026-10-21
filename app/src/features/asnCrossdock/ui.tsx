import type { ReactNode } from 'react';
import { DESTS, niceDate, type AsnCase } from './data';
import { th, td } from './styles';

const TONES = {
  ok: { bg: 'var(--color-accent-2-200)', fg: 'var(--color-accent-2-800)' },
  warn: { bg: 'var(--color-warn-bg, #fff1cc)', fg: 'var(--color-warn-fg, #7a5300)' },
  neutral: { bg: 'var(--color-neutral-200)', fg: 'var(--color-neutral-800)' },
} as const;

export function Chip({ tone, children }: { tone: keyof typeof TONES; children: ReactNode }) {
  return <span style={{ display: 'inline-block', padding: '2px 9px', borderRadius: 999, fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap', background: TONES[tone].bg, color: TONES[tone].fg }}>{children}</span>;
}

export function Modal({ title, children, actions, onClose }: { title: string; children: ReactNode; actions: ReactNode; onClose: () => void }) {
  return (
    <div role="dialog" aria-modal="true" onKeyDown={(e) => e.key === 'Escape' && onClose()} style={{ position: 'fixed', inset: 0, zIndex: 110, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
      <div style={{ width: 420, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '22px 24px 18px' }}>
        <h3 style={{ fontSize: 18, margin: '0 0 8px' }}>{title}</h3>
        <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: '0 0 18px' }}>{children}</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>{actions}</div>
      </div>
    </div>
  );
}

/** Cases of an ASN: supplier cases of pcs/case in scan order (a case can hold several destinations). */
export function CaseTable({ cases, caseLabel }: { cases: AsnCase[]; caseLabel: (c: AsnCase) => string }) {
  const total = cases.reduce((a, c) => a + c.qty, 0);
  return (
    <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
      <thead>
        <tr>
          <th style={th}>Case</th><th style={th}>Part Number</th><th style={th}>Customer Order Date</th><th style={th}>Destination</th>
          <th style={th}>Customer Order No (qty)</th><th style={th}>PO No</th><th style={{ ...th, textAlign: 'right' }}>Qty</th>
        </tr>
      </thead>
      <tbody>
        {cases.map((c) => (
          <tr key={c.seq}>
            <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{caseLabel(c)}</td>
            <td style={{ ...td, fontFamily: 'var(--font-mono)' }}>{c.partNo}</td>
            <td style={td}>{niceDate(c.orderDt)}</td>
            <td style={td}>{[...new Set(c.lines.map((l) => DESTS[l.destCd].short))].join(' + ')}</td>
            <td style={td}>{c.lines.map((l) => `${l.custOrderNo} (${l.qty})`).join(', ')}</td>
            <td style={td}>{[...new Set(c.lines.map((l) => l.poNo))].join(', ')}</td>
            <td style={{ ...td, textAlign: 'right', fontWeight: 600 }}>{c.qty}</td>
          </tr>
        ))}
        <tr>
          <td colSpan={6} style={{ ...td, textAlign: 'right', fontWeight: 600 }}>Total</td>
          <td style={{ ...td, textAlign: 'right', fontWeight: 700 }}>{total}</td>
        </tr>
      </tbody>
    </table>
  );
}
