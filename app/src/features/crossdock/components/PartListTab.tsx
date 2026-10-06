import { useEffect, useMemo, useState } from 'react';
import { fmt, madAvg, num, parseDt } from '../../../lib/format';
import type { Part, PartQuery, PartStatus } from '../../../types';
import { selectParts } from '../partList';

const STATUS_STYLE: Record<PartStatus, { bg: string; fg: string }> = {
  Active: { bg: 'var(--color-accent-2-200)', fg: 'var(--color-accent-2-800)' },
  Candidate: { bg: 'var(--color-accent-200)', fg: 'var(--color-accent-800)' },
  Inactive: { bg: 'var(--color-neutral-200)', fg: 'var(--color-neutral-700)' },
};

interface PartListTabProps {
  parts: Part[];
  q: PartQuery;
  setQ: (updater: (prev: PartQuery) => PartQuery) => void;
  resetQ: () => void;
  ro: boolean;
  onOpenPart: (id: string) => void;
  onOpenHistory: (id: string) => void;
  onAddPart: () => void;
  onOpenUpload: () => void;
}

const th: React.CSSProperties = {
  textAlign: 'left',
  padding: '0 10px',
  fontSize: 9.5,
  letterSpacing: '.06em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  background: 'var(--color-surface)',
  borderBottom: '1px solid var(--color-neutral-400)',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  height: 34,
  position: 'sticky',
  top: 0,
  zIndex: 1,
};

const td: React.CSSProperties = {
  padding: '0 10px',
  borderBottom: '1px solid var(--color-divider)',
  whiteSpace: 'nowrap',
  height: 44,
};

const PAGE_SIZE_OPTIONS = [25, 50, 100];

export function PartListTab({ parts, q, setQ, resetQ, ro, onOpenPart, onOpenHistory, onAddPart, onOpenUpload }: PartListTabProps) {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  const rowsSrc = useMemo(() => selectParts(parts, q), [parts, q]);

  useEffect(() => {
    setPage(1);
  }, [q, pageSize]);

  const empty = parts.length === 0;
  const noResult = !empty && rowsSrc.length === 0;
  const numberOptions = useMemo(() => {
    const latestByNumber = new Map<string, Part>();
    [...parts]
      .sort((a, b) => parseDt(b.dt) - parseDt(a.dt))
      .forEach((part) => latestByNumber.set(part.p, part));
    return [...latestByNumber.values()];
  }, [parts]);
  const incompleteCount = rowsSrc.filter((p) => !p.dests.length || p.dests.reduce((a, d) => a + num(d.al), 0) !== num(p.mc)).length;

  const totalPages = Math.max(1, Math.ceil(rowsSrc.length / pageSize));
  const pageClamped = Math.min(page, totalPages);
  const pageStart = (pageClamped - 1) * pageSize;
  const pageSrc = rowsSrc.slice(pageStart, pageStart + pageSize);

  const rows = pageSrc.map((p) => {
    const avg = madAvg(p.mad);
    // Candidate parts have no MAD history yet, so the Min MAD warning doesn't apply.
    const below = p.st !== 'Candidate' && avg < num(p.minMad);
    return {
      p,
      minMad: fmt(num(p.minMad)),
      minMadFg: below ? 'var(--color-warn-fg)' : 'var(--color-neutral-800)',
      minMadW: below ? 700 : 400,
      stBg: STATUS_STYLE[p.st].bg,
      stFg: STATUS_STYLE[p.st].fg,
    };
  });

  return (
    <>
      <div style={{ position: 'sticky', top: 0, zIndex: 10, padding: '16px 28px 0', background: '#eef1f5' }}>
        <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', padding: '14px 16px 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 11 }}>
            <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase' }}>Search criteria</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13 }}>
            <div className="field" style={{ width: 260 }}>
              <label>Part Number</label>
              <div style={{ position: 'relative' }}>
                <input
                  className="input"
                  value={q.part}
                  onChange={(e) => setQ((prev) => ({ ...prev, part: e.target.value }))}
                  placeholder="e.g. PART-B"
                  list="part-number-options"
                  role="combobox"
                  style={{ paddingLeft: 34, fontFamily: 'var(--font-mono)', fontSize: 13 }}
                />
                <datalist id="part-number-options">
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
            <div className="field" style={{ width: 260 }}>
              <label>Part Name</label>
              <input className="input" value={q.name} onChange={(e) => setQ((prev) => ({ ...prev, name: e.target.value }))} placeholder="Part name" />
            </div>
            <div className="field" style={{ width: 200 }}>
              <label>Status</label>
              <select className="input" value={q.st} onChange={(e) => setQ((prev) => ({ ...prev, st: e.target.value as typeof prev.st }))} style={{ appearance: 'none' }}>
                <option value="all">All</option>
                <option value="candidate">Candidate</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <div className="field" style={{ width: 200 }}>
              <label>Sort by</label>
              <select className="input" value={q.sort} onChange={(e) => setQ((prev) => ({ ...prev, sort: e.target.value as typeof prev.sort }))} style={{ appearance: 'none' }}>
                <option value="default">Default</option>
                <option value="dt_desc">Newer to Older</option>
                <option value="dt_asc">Older to Newer</option>
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
      </div>

      <div style={{ padding: '14px 28px 0' }}>
        <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', overflow: 'hidden', boxShadow: 'var(--shadow-sm)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
            <span style={{ fontSize: 12.5, fontWeight: 600 }}>Registered parts</span>
            <span style={{ fontSize: 11.5, color: 'var(--color-neutral-600)', fontVariantNumeric: 'tabular-nums' }}>
              {rowsSrc.length} {rowsSrc.length === 1 ? 'part' : 'parts'} · {incompleteCount} incomplete {incompleteCount === 1 ? 'mapping' : 'mappings'}
            </span>
            {ro && (
              <span
                style={{
                  marginLeft: 'auto',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 7,
                  fontSize: 11.5,
                  padding: '4px 11px',
                  borderRadius: 999,
                  background: 'var(--color-neutral-200)',
                  color: 'var(--color-neutral-800)',
                }}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                  <rect x="4" y="10.5" width="16" height="11" rx="3" />
                  <path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" />
                </svg>
                Read-only — you do not have permission to edit
              </span>
            )}
          </div>

          {!empty && !noResult && (
            <div style={{ overflowX: 'auto', overflowY: 'auto', maxHeight: 560 }}>
            <table style={{ width: '100%', minWidth: 1060, borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5, tableLayout: 'fixed' }}>
              <thead>
                <tr>
                  <th style={{ ...th, padding: '0 10px 0 16px', width: 130 }}>Part Number</th>
                  <th style={{ ...th, width: 220 }}>Part Name</th>
                  <th style={{ ...th, textAlign: 'right', width: 90 }}>Min MAD</th>
                  <th style={{ ...th, textAlign: 'right', width: 86 }}>Pcs/Case</th>
                  <th style={{ ...th, textAlign: 'right', width: 104 }}>Max Case/Day</th>
                  <th style={{ ...th, textAlign: 'right', width: 104 }}>Total Pcs/Day</th>
                  <th style={{ ...th, width: 84 }}>Status</th>
                  <th style={{ ...th, width: 128 }}>Last Update</th>
                  <th style={{ width: 112, background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)', position: 'sticky', top: 0, zIndex: 1 }} />
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => {
                  const p = r.p;
                  return (
                    <tr key={p.p} className="row-hover">
                      <td style={{ ...td, padding: '0 10px 0 16px', overflow: 'hidden' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12.5, fontWeight: 600 }}>{p.p}</span>
                      </td>
                      <td style={{ ...td, overflow: 'hidden', textOverflow: 'ellipsis' }} title={p.n}>{p.n}</td>
                      <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: r.minMadFg, fontWeight: r.minMadW }}>{r.minMad}</td>
                      <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{fmt(p.pc)}</td>
                      <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{fmt(p.mc)}</td>
                      <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: 'var(--color-neutral-700)' }}>{fmt(num(p.pc) * num(p.mc))}</td>
                      <td style={{ ...td, overflow: 'hidden' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 10.5, fontWeight: 700, padding: '2px 8px', borderRadius: 999, background: r.stBg, color: r.stFg }}>
                          {p.st}
                        </span>
                      </td>
                      <td style={{ ...td, fontSize: 11.5, color: 'var(--color-neutral-700)', overflow: 'hidden' }}>
                        <div style={{ fontVariantNumeric: 'tabular-nums' }}>{p.dt}</div>
                        <div style={{ fontSize: 10.5, overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.by}</div>
                      </td>
                      <td style={{ ...td, padding: '0 10px' }}>
                        <span style={{ display: 'flex', gap: 4, justifyContent: 'flex-end' }}>
                          <button className="btn btn-secondary" onClick={() => onOpenPart(p.p)} style={{ fontSize: 12, padding: '4px 12px', whiteSpace: 'nowrap' }}>
                            {ro ? 'View' : 'Edit'}
                          </button>
                          <button
                            onClick={() => onOpenHistory(p.p)}
                            title="History"
                            className="icon-btn-hover"
                            style={{ cursor: 'pointer', border: 0, background: 'transparent', width: 28, height: 28, borderRadius: 999, display: 'grid', placeItems: 'center', color: 'var(--color-neutral-800)' }}
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                              <circle cx="12" cy="12" r="9" />
                              <polyline points="12 7 12 12 15.5 14" />
                            </svg>
                          </button>
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            </div>
          )}

          {noResult && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '48px 24px 52px' }}>
              <h3 style={{ fontSize: 18, margin: '0 0 5px' }}>No matching parts</h3>
              <p style={{ fontSize: 12.5, maxWidth: 380, color: 'var(--color-neutral-700)', margin: '0 0 13px' }}>Loosen the search criteria or reset all filters.</p>
              <button className="btn btn-secondary" onClick={resetQ} style={{ fontSize: 13 }}>
                Reset filter
              </button>
            </div>
          )}

          {empty && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', padding: '64px 24px 68px' }}>
              <span style={{ width: 60, height: 60, borderRadius: 999, background: 'var(--color-surface)', display: 'grid', placeItems: 'center', marginBottom: 16 }}>
                <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="var(--color-neutral-700)" strokeWidth="2.75" strokeLinecap="round">
                  <path d="M4 7.5V19a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5" />
                  <path d="M3 4h18v3.5H3z" />
                  <line x1="12" y1="11" x2="12" y2="17" />
                  <polyline points="9 14 12 11 15 14" />
                </svg>
              </span>
              <h3 style={{ fontSize: 21, margin: '0 0 6px' }}>No crossdock parts registered yet</h3>
              <p style={{ fontSize: 13, maxWidth: 430, color: 'var(--color-neutral-700)', margin: '0 0 17px' }}>
                Start from the Excel template, or register a single part and map its Max Case/Day to Thailand, Japan and Vietnam.
              </p>
              <div style={{ display: 'flex', gap: 9 }}>
                <button className="btn btn-primary" onClick={onOpenUpload}>
                  Upload Excel
                </button>
                <button className="btn btn-secondary" onClick={onAddPart}>
                  Add one part
                </button>
              </div>
            </div>
          )}

          {!empty && !noResult && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 13, padding: '9px 16px', borderTop: '1px solid var(--color-divider)', fontSize: 12 }}>
              <span style={{ color: 'var(--color-neutral-700)' }}>Rows per page</span>
              <select className="input" value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))} style={{ width: 72, minHeight: 28, fontSize: 12, padding: '2px 10px' }}>
                {PAGE_SIZE_OPTIONS.map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
              <span style={{ marginLeft: 'auto', color: 'var(--color-neutral-700)', fontVariantNumeric: 'tabular-nums' }}>
                {pageStart + 1}–{Math.min(pageStart + pageSize, rowsSrc.length)} of {rowsSrc.length} {rowsSrc.length === 1 ? 'part' : 'parts'} · page {pageClamped}/{totalPages}
              </span>
              <span style={{ display: 'flex', gap: 3 }}>
                <button className="btn btn-secondary" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={pageClamped <= 1} style={{ fontSize: 12, padding: '3px 11px' }}>
                  Prev
                </button>
                <button className="btn btn-secondary" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={pageClamped >= totalPages} style={{ fontSize: 12, padding: '3px 11px' }}>
                  Next
                </button>
              </span>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
