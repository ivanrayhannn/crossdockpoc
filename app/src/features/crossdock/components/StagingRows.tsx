import { useState } from 'react';
import type { StgRow } from '../staging';

const th: React.CSSProperties = {
  textAlign: 'left',
  padding: '6px 8px',
  fontSize: 9,
  letterSpacing: '.05em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  background: 'var(--color-surface)',
  borderBottom: '1px solid var(--color-neutral-400)',
  borderRight: '1px solid var(--color-divider)',
  position: 'sticky',
  top: 0,
  whiteSpace: 'nowrap',
};
const td: React.CSSProperties = { padding: '4px 8px', borderBottom: '1px solid var(--color-divider)', borderRight: '1px solid var(--color-divider)', whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums' };

const ST: Record<string, { t: string; bg: string; fg: string }> = {
  '0': { t: '0 Non Sync', bg: 'var(--color-neutral-200)', fg: 'var(--color-neutral-800)' },
  '1': { t: '1 Sync', bg: 'var(--color-accent-2-200)', fg: 'var(--color-accent-2-800)' },
  '2': { t: '2 Superseded', bg: 'var(--color-neutral-100)', fg: 'var(--color-neutral-600)' },
};
const chip = (v: number | null) =>
  v == null ? (
    <span style={{ color: 'var(--color-neutral-500)' }}>NULL</span>
  ) : (
    <span style={{ fontSize: 10, fontWeight: 700, padding: '1px 7px', borderRadius: 999, background: ST[v].bg, color: ST[v].fg }}>{ST[v].t}</span>
  );

/** Prototype view of TB_H_PART_CANDIDATE_STG_SYNC: the rows NSP writes on every save and that [Sync] / the RPA read (XD01 5.24, XD06, XD07). */
export function StagingRows({ stg, per, part }: { stg: StgRow[]; per: string; part: string }) {
  const [open, setOpen] = useState(false);
  const [onlyPending, setOnlyPending] = useState(false);
  const rows = stg
    .filter((r) => (per === 'all' || r.per === per) && (!part || r.p.toLowerCase().includes(part.toLowerCase())) && (!onlyPending || r.ap === 0 || r.gt === 0))
    .sort((a, b) => b.id - a.id);
  const pending = stg.filter((r) => r.ap === 0 || r.gt === 0).length;
  return (
    <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', overflow: 'hidden', marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 16px', borderBottom: open ? '1px solid var(--color-divider)' : 0 }}>
        <button className="btn btn-ghost" onClick={() => setOpen(!open)} style={{ fontSize: 12, padding: '3px 8px', fontWeight: 600 }}>
          {open ? '▾' : '▸'} Staging rows <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>TB_H_PART_CANDIDATE_STG_SYNC</span>
        </button>
        <span style={{ fontSize: 11.5, color: 'var(--color-neutral-700)' }}>
          {rows.length} row(s) for the criteria · {pending} waiting for [Sync] · prototype view, the RPA reads only this table
        </span>
        {open && (
          <label style={{ marginLeft: 'auto', fontSize: 11.5, display: 'flex', gap: 6, alignItems: 'center' }}>
            <input type="checkbox" checked={onlyPending} onChange={(e) => setOnlyPending(e.target.checked)} /> Status 0 only
          </label>
        )}
      </div>
      {open && (
        <div style={{ maxHeight: 420, overflow: 'auto' }}>
          <table style={{ borderCollapse: 'separate', borderSpacing: 0, fontSize: 11.5, minWidth: '100%' }}>
            <thead>
              <tr>
                {['HIST_ID', 'PART_NO', 'PART_NAME', 'PERIOD', 'PART_STATUS', 'LEVEL_TYPE', 'DEST_CODE', 'ORDER_TYPE', 'FIELD_NAME', 'ACTION', 'OLD_VALUE', 'NEW_VALUE', 'SOURCE',
                  'APPOLE_SYNC_STATUS', 'APPOLE_SYNC_DT', 'SEND_SEQ', 'APPOLE_SYNC_RUN_ID', 'GTOPAS_SYNC_STATUS', 'GTOPAS_SYNC_DT', 'GTOPAS_SYNC_RUN_ID', 'CREATED_BY', 'CREATED_DT'].map((h) => (
                  <th key={h} style={th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.slice(0, 300).map((r) => (
                <tr key={r.id} className="row-hover">
                  <td style={td}>{r.id}</td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{r.p}</td>
                  <td style={td}>{r.n}</td>
                  <td style={td}>{r.per}</td>
                  <td style={td}>{r.ps}</td>
                  <td style={td}>{r.lvl}</td>
                  <td style={td}>{r.dest || <span style={{ color: 'var(--color-neutral-500)' }}>NULL</span>}</td>
                  <td style={td}>{r.ot || <span style={{ color: 'var(--color-neutral-500)' }}>NULL</span>}</td>
                  <td style={td}>{r.f}</td>
                  <td style={{ ...td, fontWeight: 600 }}>{r.act}</td>
                  <td style={{ ...td, textAlign: 'right' }}>{r.old ?? <span style={{ color: 'var(--color-neutral-500)' }}>NULL</span>}</td>
                  <td style={{ ...td, textAlign: 'right' }}>{r.nw}</td>
                  <td style={td}>{r.src}</td>
                  <td style={td}>{chip(r.ap)}</td>
                  <td style={td}>{r.apDt ?? ''}</td>
                  <td style={{ ...td, textAlign: 'center' }}>{r.seq ?? ''}</td>
                  <td style={td}>{r.apRun ?? ''}</td>
                  <td style={td}>{chip(r.gt)}</td>
                  <td style={td}>{r.gtDt ?? ''}</td>
                  <td style={td}>{r.gtRun ?? ''}</td>
                  <td style={td}>{r.by}</td>
                  <td style={td}>{r.dt}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length > 300 && <div style={{ padding: 8, fontSize: 11.5, color: 'var(--color-neutral-700)' }}>First 300 rows shown, newest first. Filter by Part Number to see more.</div>}
        </div>
      )}
    </div>
  );
}
