import { useMemo } from 'react';
import { CUR_PER, DCODE, DOTS, MASTER_DESTS, PERIODS } from '../../../data/seed';
import { fmt, num, syncBadge } from '../../../lib/format';
import type { DestAllocation, Part } from '../../../types';
import type { CrossdockState } from '../useCrossdockState';

const th: React.CSSProperties = {
  textAlign: 'left',
  padding: '0 12px',
  fontSize: 9,
  letterSpacing: '.07em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  background: 'var(--color-surface)',
  borderBottom: '1px solid var(--color-neutral-400)',
  position: 'sticky',
  top: 0,
  zIndex: 1,
};

const td: React.CSSProperties = {
  padding: '0 12px',
  borderBottom: '1px solid var(--color-divider)',
  height: 40,
};

function exportMappingExcel(rows: Part[], per: string) {
  let x = '<table border="1"><tr><th>Part No</th><th>Part Name</th><th>Period</th><th>Pcs/Case</th><th>Sync Status</th><th>Dest Code</th><th>Case/Day</th><th>Pcs/Day</th><th>Percentage</th></tr>';
  rows.forEach((p) => {
    const a = p.dests.reduce((s, d) => s + num(d.al), 0);
    const sb = syncBadge(p.syncStatus).t;
    const ds = p.dests.length ? p.dests : [{ d: '', cd: '', al: 0, st: 'Active' as const }];
    ds.forEach((d) => {
      const code = d.cd || DCODE[d.d] || '';
      x += `<tr><td>${p.p}</td><td>${p.n}</td><td>${p.per}</td><td>${p.pc}</td><td>${sb}</td><td>${code}</td><td>${d.al}</td><td>${num(p.pc) * num(d.al)}</td><td>${a ? Math.round((num(d.al) / a) * 100) + '%' : ''}</td></tr>`;
    });
  });
  x += '</table>';
  const blob = new Blob(['﻿' + x], { type: 'application/vnd.ms-excel' });
  const url = URL.createObjectURL(blob);
  const el = document.createElement('a');
  el.href = url;
  el.download = `crossdock-mapping-${per.replace(' ', '-')}.xls`;
  el.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function DestMappingTab({ state }: { state: CrossdockState }) {
  const { parts, q, setQ, resetQ, ro, expand, editDest, draftDests, toggleExpand, startEditDest, cancelEditDest, patchDraft, saveDest, syncParts } = state;

  const destRowsSrc = useMemo(
    () =>
      parts.filter(
        (p) =>
          // Mapping per Destination only ever works with parts that are marked Active.
          p.st === 'Active' &&
          (q.per === 'all' || p.per === q.per) &&
          (!q.part || p.p.toLowerCase().includes(q.part.toLowerCase())) &&
          (q.sync === 'all' ||
            (q.sync === 'notsync' && p.syncStatus === 0) ||
            (q.sync === 'success' && p.syncStatus === 1) ||
            (q.sync === 'failed' && p.syncStatus === 2)),
      ),
    [parts, q],
  );

  // Sync only ever targets rows that aren't already a confirmed success.
  const syncableCount = destRowsSrc.filter((p) => p.syncStatus === 0 || p.syncStatus === 2).length;

  const numberOptions = useMemo(() => {
    const seen = new Set<string>();
    return parts.filter((p) => (seen.has(p.p) ? false : (seen.add(p.p), true)));
  }, [parts]);

  return (
    <div style={{ padding: '16px 28px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', padding: '14px 16px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 11 }}>
          <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase' }}>Search criteria</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Case/day mapping per destination for each part, per calculation period</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13, flexWrap: 'wrap' }}>
          <div className="field" style={{ width: 190 }}>
            <label>
              Calculation period <span style={{ color: 'var(--color-neutral-500)', textTransform: 'none', letterSpacing: 0 }}>({q.per === CUR_PER ? 'ongoing' : q.per === 'all' ? 'all' : 'past'})</span>
            </label>
            <select className="input" value={q.per} onChange={(e) => setQ((prev) => ({ ...prev, per: e.target.value }))} style={{ appearance: 'none' }}>
              <option value="all">All periods</option>
              {PERIODS.map((per) => (
                <option key={per} value={per}>
                  {per}
                  {per === CUR_PER ? ' (ongoing)' : ''}
                </option>
              ))}
            </select>
          </div>
          <div className="field" style={{ width: 260 }}>
            <label>Part Number</label>
            <div style={{ position: 'relative' }}>
              <input
                className="input"
                value={q.part}
                onChange={(e) => setQ((prev) => ({ ...prev, part: e.target.value }))}
                placeholder="e.g. PART-B"
                list="dest-part-number-options"
                role="combobox"
                style={{ paddingLeft: 34, fontFamily: 'var(--font-mono)', fontSize: 13 }}
              />
              <datalist id="dest-part-number-options">
                {numberOptions.map((part) => <option key={part.p} value={part.p} />)}
              </datalist>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--color-neutral-600)"
                strokeWidth="2.75"
                strokeLinecap="round"
                style={{ position: 'absolute', left: 13, top: 11 }}
              >
                <circle cx="11" cy="11" r="7" />
                <line x1="16.5" y1="16.5" x2="21" y2="21" />
              </svg>
            </div>
          </div>
          <div className="field" style={{ width: 210 }}>
            <label>Sync Status</label>
            <select className="input" value={q.sync} onChange={(e) => setQ((prev) => ({ ...prev, sync: e.target.value as typeof prev.sync }))} style={{ appearance: 'none' }}>
              <option value="all">All</option>
              <option value="notsync">No Sync</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={resetQ}>
              Reset
            </button>
            <button className="btn btn-primary">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                <circle cx="11" cy="11" r="7" />
                <line x1="16.5" y1="16.5" x2="21" y2="21" />
              </svg>
              Search
            </button>
          </div>
        </div>
      </div>

      <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', overflow: 'hidden', boxShadow: 'var(--shadow-sm)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
          <span style={{ fontSize: 12.5, fontWeight: 600 }}>Destination mapping per part</span>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button
              className="btn btn-secondary"
              onClick={() => syncParts(destRowsSrc.filter((p) => p.syncStatus === 0 || p.syncStatus === 2).map((p) => p.p))}
              disabled={!syncableCount}
              style={{ fontSize: 12, padding: '4px 12px' }}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <path d="M21 12a9 9 0 1 1-3-6.7" />
                <path d="M21 4v5h-5" />
              </svg>
              Sync{syncableCount ? ` (${syncableCount})` : ''}
            </button>
            <button className="btn btn-primary" onClick={() => exportMappingExcel(destRowsSrc, q.per)} style={{ fontSize: 12, padding: '4px 12px' }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <path d="M12 3v12M7 10l5 5 5-5M5 21h14" />
              </svg>
              Export Excel
            </button>
          </span>
        </div>

        {destRowsSrc.length > 0 && (
          <div style={{ maxHeight: 560, overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12 }}>
              <thead>
                <tr>
                  <th style={{ ...th, padding: '0 16px', width: 150, height: 32 }}>Part Number</th>
                  <th style={th}>Part Name</th>
                  <th style={{ ...th, width: 124 }}>Period</th>
                  <th style={{ ...th, textAlign: 'right', width: 86 }}>Pcs/Case</th>
                  <th style={{ ...th, textAlign: 'right', width: 128 }}>Total Case/Day</th>
                  <th style={{ ...th, textAlign: 'right', width: 110 }}>Pcs/Day</th>
                  <th style={{ ...th, textAlign: 'right', width: 150 }}>Percentage</th>
                  <th style={{ ...th, width: 120 }}>Sync Status</th>
                </tr>
              </thead>
              <tbody>
                {destRowsSrc.map((p) => (
                  <DestRow
                    key={p.p}
                    p={p}
                    ro={ro}
                    isOpen={!!expand[p.p] || editDest === p.p}
                    isEditing={editDest === p.p}
                    draftDests={editDest === p.p ? draftDests : null}
                    onToggleExpand={() => toggleExpand(p.p)}
                    onStartEdit={() => startEditDest(p.p)}
                    onCancelEdit={cancelEditDest}
                    onSave={saveDest}
                    onPatchDraft={patchDraft}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}

        {destRowsSrc.length === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '48px 24px 52px' }}>
            <h3 style={{ fontSize: 18, margin: '0 0 5px' }}>No parts match these filters</h3>
            <p style={{ fontSize: 12.5, maxWidth: 400, color: 'var(--color-neutral-700)', margin: 0 }}>Change the period or sync status, or press Reset to show all parts.</p>
          </div>
        )}
      </div>
    </div>
  );
}

interface DestRowProps {
  p: Part;
  ro: boolean;
  isOpen: boolean;
  isEditing: boolean;
  draftDests: DestAllocation[] | null;
  onToggleExpand: () => void;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSave: () => void;
  onPatchDraft: (fn: (d: DestAllocation[]) => void) => void;
}

function DestRow({ p, ro, isOpen, isEditing, draftDests, onToggleExpand, onStartEdit, onCancelEdit, onSave, onPatchDraft }: DestRowProps) {
  const m = num(p.mc);
  const a = p.dests.reduce((x, d) => x + num(d.al), 0);
  const sb = syncBadge(p.syncStatus);
  const edok = p.per === CUR_PER && !ro;
  const dList = isEditing && draftDests ? draftDests : p.dests;
  const dAlloc = dList.reduce((x, d) => x + num(d.al), 0);
  const dOver = dAlloc > m;
  const dUnder = dAlloc < m;
  const share = m ? `${Math.round((a / m) * 100)}%` : '—';
  const sharePct = m ? Math.min(100, Math.round((a / m) * 100)) : 0;

  const editViewDisp = ro || isEditing || !edok ? 'none' : 'inline-flex';
  const roPerDisp = !edok && !ro ? 'inline-flex' : 'none';
  const editingDisp = isEditing ? 'inline-flex' : 'none';
  const splitDisp = isEditing && dList.length > 1 ? 'inline-flex' : 'none';

  const splitEven = () =>
    onPatchDraft((x) => {
      const n = x.length;
      const base = Math.floor(m / n);
      const rem = m - base * n;
      x.forEach((d, i) => {
        d.al = base + (i < rem ? 1 : 0);
      });
    });

  return (
    <>
      <tr className="row-hover">
        <td style={{ ...td, padding: '0 16px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              onClick={onToggleExpand}
              title="Destination details"
              style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 20, height: 20, flex: 'none', display: 'grid', placeItems: 'center', color: 'var(--color-neutral-700)' }}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" style={{ transform: `rotate(${isOpen ? 90 : 0}deg)`, transition: 'transform .12s' }}>
                <polyline points="9 6 15 12 9 18" />
              </svg>
            </button>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 600 }}>{p.p}</span>
          </span>
        </td>
        <td style={td}>{p.n}</td>
        <td style={td}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 10.5,
              fontWeight: 700,
              padding: '2px 10px',
              borderRadius: 999,
              background: edok ? 'var(--color-accent-200)' : 'var(--color-neutral-200)',
              color: edok ? 'var(--color-accent-800)' : 'var(--color-neutral-700)',
              whiteSpace: 'nowrap',
            }}
          >
            <span style={{ width: 5, height: 5, borderRadius: 999, background: edok ? 'var(--color-accent-800)' : 'var(--color-neutral-700)' }} />
            {p.per}
          </span>
        </td>
        <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{fmt(p.pc)}</td>
        <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{fmt(a)}</td>
        <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: 'var(--color-neutral-700)' }}>{fmt(num(p.pc) * a)}</td>
        <td style={{ ...td, textAlign: 'right' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 64, height: 5, borderRadius: 999, background: 'var(--color-neutral-300)', overflow: 'hidden' }}>
              <span style={{ display: 'block', height: 5, borderRadius: 999, background: 'var(--color-accent)', width: `${sharePct}%` }} />
            </span>
            <span style={{ fontSize: 11, color: 'var(--color-neutral-800)', fontVariantNumeric: 'tabular-nums', width: 40, textAlign: 'right', fontWeight: 600 }}>{share}</span>
          </span>
        </td>
        <td style={td}>
          <span style={{ display: 'inline-flex', fontSize: 10, fontWeight: 700, padding: '2px 9px', borderRadius: 999, background: sb.bg, color: sb.fg, whiteSpace: 'nowrap' }}>{sb.t}</span>
        </td>
      </tr>
      <tr style={{ display: isOpen ? 'table-row' : 'none' }}>
        <td colSpan={8} style={{ padding: '0 16px 16px 46px', borderBottom: '1px solid var(--color-divider)', background: 'var(--color-surface)', position: 'relative' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '11px 0 10px' }}>
            <span style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-accent-2-800)' }}>Destination mapping</span>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 7,
                fontSize: 12,
                padding: '3px 11px',
                borderRadius: 999,
                background: dOver ? 'var(--color-danger-bg)' : dUnder ? 'var(--color-neutral-200)' : 'var(--color-accent-2-200)',
                color: dOver ? 'var(--color-danger)' : dUnder ? 'var(--color-neutral-700)' : 'var(--color-accent-2-800)',
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              <span style={{ width: 6, height: 6, borderRadius: 999, background: dOver ? 'var(--color-danger)' : dUnder ? 'var(--color-neutral-700)' : 'var(--color-accent-2-800)' }} />
              {fmt(dAlloc)} / {fmt(m)} case/day used
            </span>
            <span style={{ fontSize: 11.5, color: dOver ? 'var(--color-danger)' : 'var(--color-neutral-700)', fontVariantNumeric: 'tabular-nums' }}>
              {!dList.length ? 'no destination yet' : dOver ? `${fmt(dAlloc - m)} case/day over` : dUnder ? `${fmt(m - dAlloc)} case/day left` : 'capacity fully allocated'}
            </span>
            <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ display: roPerDisp, alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 999, background: 'var(--color-neutral-200)', color: 'var(--color-neutral-700)' }}>
                Past period — read only
              </span>
              <button className="btn btn-ghost" onClick={splitEven} style={{ display: splitDisp, color: 'var(--color-accent-700)', fontSize: 12, padding: '4px 10px' }}>
                Split evenly
              </button>
              <button className="btn btn-secondary" onClick={onStartEdit} style={{ display: editViewDisp, fontSize: 12, padding: '4px 14px' }}>
                Edit mapping
              </button>
              <button className="btn btn-ghost" onClick={onCancelEdit} style={{ display: editingDisp, fontSize: 12, padding: '4px 12px' }}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={onSave} disabled={dOver || !dList.length} style={{ display: editingDisp, fontSize: 12, padding: '4px 16px' }}>
                Save
              </button>
            </span>
          </div>

          <div style={{ border: '1px solid var(--color-divider)', borderRadius: 14, overflow: 'hidden', background: 'var(--color-neutral-100)' }}>
            {dList.length > 0 && (
              <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '7px 16px', fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)' }}>
                      Destination (CD)
                    </th>
                    <th style={{ textAlign: 'right', padding: '7px 14px', width: 160, fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)' }}>
                      Case/Day
                    </th>
                    <th style={{ textAlign: 'right', padding: '7px 14px', width: 120, fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)' }}>
                      Pcs/Day
                    </th>
                    <th style={{ textAlign: 'right', padding: '7px 14px', width: 150, fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--color-neutral-700)', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)' }}>
                      PERCENTAGE
                    </th>
                    <th style={{ width: 48, background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)' }} />
                  </tr>
                </thead>
                <tbody>
                  {dList.map((d, i) => {
                    const dot = DOTS[d.d] || 'var(--color-neutral-500)';
                    const pcsDay = fmt(num(p.pc) * num(d.al));
                    const rowShare = dAlloc ? `${Math.round((num(d.al) / dAlloc) * 100)}%` : '0%';
                    const barPct = dAlloc ? Math.min(100, (num(d.al) / dAlloc) * 100) : 0;
                    const inputBg = isEditing ? 'var(--color-neutral-100)' : 'var(--color-surface)';
                    return (
                      <tr key={i}>
                        <td style={{ padding: '0 16px', height: 44, borderBottom: '1px solid var(--color-divider)' }}>
                          <span style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                            <span style={{ width: 7, height: 7, borderRadius: 999, background: dot }} />
                            <select
                              className="input"
                              value={d.d}
                              onChange={(e) => onPatchDraft((x) => {
                                const sel = MASTER_DESTS.find((m) => m.name === e.target.value);
                                x[i].d = e.target.value;
                                x[i].cd = sel ? sel.code : '';
                              })}
                              disabled={!isEditing}
                              style={{ width: 150, minHeight: 32, padding: '2px 8px', fontSize: 13, fontFamily: 'var(--font-mono)', fontWeight: 600, background: inputBg, appearance: 'none' }}
                            >
                              <option value="">Select destination</option>
                              {MASTER_DESTS.filter((m) => m.name === d.d || !dList.some((row, ri) => ri !== i && row.d === m.name)).map((m) => (
                                <option key={m.name} value={m.name}>
                                  {m.code} — {m.name}
                                </option>
                              ))}
                            </select>
                          </span>
                        </td>
                        <td style={{ padding: '0 14px', borderBottom: '1px solid var(--color-divider)', textAlign: 'right' }}>
                          <input
                            className="input"
                            value={String(d.al)}
                            onChange={(e) => onPatchDraft((x) => { x[i].al = e.target.value; })}
                            readOnly={!isEditing}
                            style={{ width: 108, minHeight: 32, padding: '2px 12px', fontSize: 13, textAlign: 'right', fontVariantNumeric: 'tabular-nums', background: inputBg }}
                          />
                        </td>
                        <td style={{ padding: '0 14px', borderBottom: '1px solid var(--color-divider)', textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: 'var(--color-neutral-800)' }}>{pcsDay}</td>
                        <td style={{ padding: '0 14px', borderBottom: '1px solid var(--color-divider)', textAlign: 'right' }}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ width: 64, height: 5, borderRadius: 999, background: 'var(--color-neutral-300)', overflow: 'hidden' }}>
                              <span style={{ display: 'block', height: 5, borderRadius: 999, background: dot, width: `${barPct}%` }} />
                            </span>
                            <span style={{ fontSize: 12, color: 'var(--color-neutral-700)', fontVariantNumeric: 'tabular-nums', width: 34, textAlign: 'right' }}>{rowShare}</span>
                          </span>
                        </td>
                        <td style={{ padding: '0 10px', borderBottom: '1px solid var(--color-divider)', textAlign: 'right' }}>
                          {isEditing && (
                            <button
                              onClick={() => onPatchDraft((x) => { x.splice(i, 1); })}
                              title="Remove destination"
                              className="remove-btn-hover"
                              style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 30, height: 30, borderRadius: 8, display: 'grid', placeItems: 'center', color: 'var(--color-danger)' }}
                            >
                              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6" />
                              </svg>
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}

            {dList.length === 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '24px 20px', gap: 3 }}>
                <div style={{ fontSize: 13.5, fontWeight: 700 }}>No destination yet</div>
                <div style={{ fontSize: 12, color: 'var(--color-neutral-700)', maxWidth: 380 }}>Click Edit mapping and add at least one destination so the part is included in the volume calculation.</div>
              </div>
            )}

            {isEditing && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '11px 16px', borderTop: '1px solid var(--color-divider)', background: 'var(--color-surface)' }}>
                <button
                  onClick={() => onPatchDraft((x) => { x.push({ d: '', cd: '', al: 0, st: 'Active' }); })}
                  className="add-dest-row"
                  style={{ cursor: 'pointer', fontFamily: 'var(--font-body)', display: 'inline-flex', alignItems: 'center', gap: 7, fontSize: 12.5, padding: '6px 13px', borderRadius: 8, border: '1px dashed var(--color-accent)', background: 'var(--color-accent-100)', color: 'var(--color-accent-800)', fontWeight: 600 }}
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                  Add destination
                </button>
                <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>New row — pick a destination from the destination master in the Destination (CD) column.</span>
              </div>
            )}
          </div>

          {dOver && (
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 11, padding: '11px 14px', borderRadius: 13, background: 'var(--color-accent-100)', border: '1px solid var(--color-accent-300)', marginTop: 11, fontSize: 12.5, color: 'var(--color-accent-800)' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" style={{ flex: 'none', marginTop: 1 }}>
                <line x1="12" y1="8" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12" y2="17" />
                <circle cx="12" cy="12" r="9" />
              </svg>
              <span>
                Allocation of {fmt(dAlloc)} case/day exceeds Max Case/Day ({fmt(m)}). Reduce one of the destinations.
              </span>
            </div>
          )}
        </td>
      </tr>
    </>
  );
}
