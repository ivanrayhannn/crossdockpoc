import { useCallback, useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import initSqlJs from 'sql.js';
import type { Database, QueryExecResult } from 'sql.js';
import wasmUrl from 'sql.js/dist/sql-wasm.wasm?url';
import { card, th, td } from '../asnCrossdock/styles';
import { SANDBOX } from './sandboxData';

/** Staging Sync SQL (prototype): SQLite in the browser with TB_H_PART_CANDIDATE_STG_SYNC and the RPA queries for AP POLE and GTOPAS. */
export function StagingSqlPage() {
  const dbRef = useRef<Database | null>(null);
  const [ready, setReady] = useState(false);
  const [sql, setSql] = useState(SANDBOX.queries[2].sql);
  const [active, setActive] = useState<number | null>(2);
  const [result, setResult] = useState<QueryExecResult[] | null>(null);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('Loading SQLite …');

  const load = useCallback((SQL: Awaited<ReturnType<typeof initSqlJs>>) => {
    dbRef.current?.close();
    const db = new SQL.Database();
    for (const t of SANDBOX.tables) {
      db.run(t.ddl);
      const st = db.prepare(`INSERT INTO ${t.name} VALUES (${t.cols.map(() => '?').join(',')})`);
      for (const r of t.rows) st.run(r);
      st.free();
    }
    dbRef.current = db;
  }, []);

  const sqlRef = useRef<Awaited<ReturnType<typeof initSqlJs>> | null>(null);

  const run = useCallback((text: string) => {
    const db = dbRef.current;
    if (!db) return;
    const t0 = performance.now();
    try {
      const res = db.exec(text);
      setResult(res);
      setError('');
      setStatus(`OK · ${res.reduce((n, r) => n + r.values.length, 0)} row(s) · ${Math.round(performance.now() - t0)} ms`);
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
      setStatus('Error');
    }
  }, []);

  useEffect(() => {
    let alive = true;
    initSqlJs({ locateFile: () => wasmUrl, useOldExtensionFunctions: false })
      .then((SQL) => {
        if (!alive) return;
        sqlRef.current = SQL;
        load(SQL);
        setReady(true);
        run(SANDBOX.queries[2].sql);
      })
      .catch((e: unknown) => setStatus('SQLite could not start: ' + (e instanceof Error ? e.message : String(e))));
    return () => {
      alive = false;
      dbRef.current?.close();
      dbRef.current = null;
    };
  }, [load, run]);

  const pick = (i: number) => {
    setActive(i);
    setSql(SANDBOX.queries[i].sql);
    run(SANDBOX.queries[i].sql);
  };

  const btn: CSSProperties = { textAlign: 'left', fontSize: 12.5, padding: '7px 10px', borderRadius: 6, cursor: 'pointer', border: '1px solid var(--color-divider)', lineHeight: 1.3 };

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>Staging Sync SQL</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3, maxWidth: 1000 }}>
          Prototype of the RPA queries on <b>TB_H_PART_CANDIDATE_STG_SYNC</b>: the bot reads only the staging (AP POLE upload files LLM9Q910 / LLM9Q880, GTOPAS compare).
          Data = the full flow simulation (Nov 2026 – Jan 2027, dummy parts). Parameters are in <code>WITH p AS (…)</code> at the top of each query.
          SQLite runs in this browser; Reset data restores the tables. SQLite dialect (SQL Server: <code>||</code> → <code>+</code>, SUBSTR → SUBSTRING, IFNULL → ISNULL, LENGTH → LEN).
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(240px, 300px) minmax(0, 1fr)', gap: 14, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ ...card, padding: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ fontWeight: 600, fontSize: 13 }}>Saved queries</div>
            {SANDBOX.queries.map((q, i) => (
              <button key={q.title} type="button" onClick={() => pick(i)}
                style={{ ...btn, background: active === i ? 'var(--color-primary, #123a6b)' : 'var(--color-neutral-100)', color: active === i ? '#fff' : 'inherit' }}>
                {q.title}
              </button>
            ))}
          </div>
          <div style={{ ...card, padding: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ fontWeight: 600, fontSize: 13 }}>Tables</div>
            {SANDBOX.tables.map((t) => (
              <details key={t.name} style={{ border: '1px solid var(--color-divider)', borderRadius: 6, padding: '6px 10px' }}>
                <summary style={{ cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: 11.5, fontWeight: 600 }}>{t.name} ({t.rows.length})</summary>
                <div style={{ fontSize: 11.5, color: 'var(--color-neutral-700)', marginTop: 4 }}>{t.note}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10.5, color: 'var(--color-neutral-600)', marginTop: 4 }}>{t.cols.join(', ')}</div>
                <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                  <button type="button" className="btn btn-secondary" style={{ padding: '2px 8px', fontSize: 11 }}
                    onClick={() => { const s = `SELECT * FROM ${t.name};`; setActive(null); setSql(s); run(s); }}>SELECT *</button>
                  <button type="button" className="btn btn-secondary" style={{ padding: '2px 8px', fontSize: 11 }}
                    onClick={() => { setActive(null); setSql(t.ddl); setResult(null); setError(''); setStatus('DDL shown (the table already exists here)'); }}>Show DDL</button>
                </div>
              </details>
            ))}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, minWidth: 0 }}>
          <textarea
            aria-label="SQL editor" spellCheck={false} value={sql}
            onChange={(e) => { setSql(e.target.value); setActive(null); }}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(sql); }
              if (e.key === 'Tab') {
                e.preventDefault();
                const el = e.currentTarget, s = el.selectionStart;
                const next = sql.slice(0, s) + '  ' + sql.slice(el.selectionEnd);
                setSql(next);
                requestAnimationFrame(() => { el.selectionStart = el.selectionEnd = s + 2; });
              }
            }}
            style={{ width: '100%', minHeight: 300, resize: 'vertical', fontFamily: 'var(--font-mono)', fontSize: 12.5, lineHeight: 1.55, padding: 12,
              border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-surface)', whiteSpace: 'pre', boxSizing: 'border-box' }}
          />
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <button type="button" className="btn btn-primary" disabled={!ready} onClick={() => run(sql)}>Run (Ctrl + Enter)</button>
            <button type="button" className="btn btn-secondary" disabled={!ready}
              onClick={() => { if (sqlRef.current) { load(sqlRef.current); setStatus('Data restored'); } }}>Reset data</button>
            <span role="status" style={{ fontSize: 12.5, color: error ? 'var(--color-danger, #b23b2e)' : 'var(--color-neutral-700)' }}>{status}</span>
          </div>
          {error && <pre style={{ margin: 0, padding: 10, borderRadius: 6, background: '#fbe3df', color: '#b23b2e', fontSize: 12, whiteSpace: 'pre-wrap' }}>{error}</pre>}
          {result && result.length === 0 && <div style={{ fontSize: 12.5 }}>Statement executed. No rows returned.</div>}
          {result?.map((r, k) => (
            <div key={k} style={{ ...card, overflow: 'auto', maxHeight: 520 }}>
              <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12 }}>
                <thead><tr>{r.columns.map((c) => <th key={c} style={{ ...th, position: 'sticky', top: 0, borderRight: '1px solid var(--color-divider)' }}>{c}</th>)}</tr></thead>
                <tbody>
                  {r.values.map((v, i) => (
                    <tr key={i}>
                      {v.map((x, j) => (
                        <td key={j} style={{ ...td, fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap', borderRight: '1px solid var(--color-divider)',
                          color: x === null ? 'var(--color-neutral-500)' : undefined, fontStyle: x === null ? 'italic' : undefined }}>
                          {x === null ? 'NULL' : String(x)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
