import { useMemo, useState, type CSSProperties } from 'react';
import { fmt, num } from '../../../lib/format';
import type { Part, PartDetail } from '../../../types';
import type { PartDetailState } from '../usePartDetail';
import { PartNoCombobox } from './PartNoCombobox';

const th: CSSProperties = {
  textAlign: 'left',
  padding: '0 10px',
  height: 34,
  fontSize: 10,
  letterSpacing: '.06em',
  textTransform: 'uppercase',
  color: 'var(--color-neutral-700)',
  background: 'var(--color-surface)',
  borderBottom: '1px solid var(--color-neutral-400)',
  position: 'sticky',
  top: 0,
};
const td: CSSProperties = { padding: '0 10px', height: 44, borderBottom: '1px solid var(--color-divider)', fontSize: 12.5 };

/** Whole number check for the form inputs ('' is "not filled"). */
const isWhole = (v: string, min: number) => v.trim() !== '' && /^\d+$/.test(v.trim()) && Number(v) >= min;

interface FormState {
  mode: 'add' | 'edit';
  p: string;
  n: string;
  minMad: string;
  cd: string;
}

/** Part Detail sub-menu: CRUD of TB_M_PART_CROSSDOCK_DTL (Part Number, Minimum MAD, Case/Day). */
export function PartDetailTab({ parts, ro, detail }: { parts: Part[]; ro: boolean; detail: PartDetailState }) {
  const { details, saveDetail, deleteDetail } = detail;
  const [query, setQuery] = useState('');
  const [form, setForm] = useState<FormState | null>(null);
  const [toDelete, setToDelete] = useState<PartDetail | null>(null);
  const [done, setDone] = useState<string | null>(null);

  const nameOf = useMemo(() => new Map(parts.map((p) => [p.p, p.n])), [parts]);
  const rows = details.filter((d) => !query || d.p.toLowerCase().includes(query.toLowerCase()));
  // Only parts registered in Part List (TB_M_PART_CANDIDATE) that have no detail record yet can be added.
  const usedIds = new Set(details.map((d) => d.p));
  const options = parts.filter((p) => !usedIds.has(p.p)).map((p) => ({ no: p.p, name: p.n }));

  const openAdd = () => setForm({ mode: 'add', p: '', n: '', minMad: '', cd: '' });
  const openEdit = (d: PartDetail) => setForm({ mode: 'edit', p: d.p, n: nameOf.get(d.p) || '', minMad: String(d.minMad), cd: String(d.cd) });

  const madOk = form ? isWhole(form.minMad, 0) : false;
  const cdOk = form ? isWhole(form.cd, 1) : false;
  const saveTitle = !form?.p ? 'Part No is required' : !madOk ? 'Enter Minimum MAD (whole number, 0 or more)' : !cdOk ? 'Enter Case/Day (whole number, more than 0)' : 'Save part detail';
  const save = () => {
    if (!form || !form.p || !madOk || !cdOk) return;
    saveDetail({ p: form.p, minMad: num(form.minMad), cd: num(form.cd) });
    setDone(`${form.p} has been ${form.mode === 'add' ? 'added' : 'updated'}.`);
    setForm(null);
  };

  return (
    <div style={{ padding: '16px 28px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', padding: '14px 16px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 11 }}>
          <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase' }}>Search criteria</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>Minimum MAD and Case/Day per crossdock part</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13 }}>
          <div className="field" style={{ width: 260 }}>
            <label>Part Number</label>
            <input className="input" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g. PART-B" style={{ fontFamily: 'var(--font-mono)', fontSize: 13 }} />
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={() => setQuery('')}>
              Reset
            </button>
            <button className="btn btn-primary">Search</button>
          </div>
        </div>
      </div>

      <div style={{ border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', overflow: 'hidden', boxShadow: 'var(--shadow-sm)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
          <span style={{ fontSize: 12.5, fontWeight: 600 }}>Part detail</span>
          <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>
            {rows.length} {rows.length === 1 ? 'part' : 'parts'}
          </span>
          {!ro && (
            <button className="btn btn-primary" onClick={openAdd} disabled={!options.length} title={options.length ? 'Add a part detail' : 'Every registered part already has a detail'} style={{ marginLeft: 'auto', fontSize: 12, padding: '4px 12px' }}>
              + Add Detail
            </button>
          )}
        </div>
        {rows.length > 0 ? (
          <div style={{ maxHeight: 560, overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
              <thead>
                <tr>
                  <th style={{ ...th, padding: '0 10px 0 16px', width: 150 }}>Part Number</th>
                  <th style={th}>Part Name</th>
                  <th style={{ ...th, textAlign: 'right', width: 130 }}>Minimum MAD</th>
                  <th style={{ ...th, textAlign: 'right', width: 110 }}>Case/Day</th>
                  <th style={{ ...th, width: 170 }}>Last Update</th>
                  <th style={{ ...th, width: 120 }} />
                </tr>
              </thead>
              <tbody>
                {rows.map((d) => (
                  <tr key={d.p} className="row-hover">
                    <td style={{ ...td, padding: '0 10px 0 16px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{d.p}</td>
                    <td style={td}>{nameOf.get(d.p) || '—'}</td>
                    <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{fmt(d.minMad)}</td>
                    <td style={{ ...td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{fmt(d.cd)}</td>
                    <td style={{ ...td, fontSize: 11.5, color: 'var(--color-neutral-700)' }}>
                      <div>{d.dt}</div>
                      <div style={{ fontSize: 10.5 }}>{d.by}</div>
                    </td>
                    <td style={{ ...td, textAlign: 'right' }}>
                      <span style={{ display: 'inline-flex', gap: 6 }}>
                        <button className="btn btn-secondary" onClick={() => openEdit(d)} style={{ fontSize: 12, padding: '4px 12px' }}>
                          {ro ? 'View' : 'Edit'}
                        </button>
                        {!ro && (
                          <button className="btn btn-secondary" onClick={() => setToDelete(d)} title="Delete" style={{ fontSize: 12, padding: '4px 10px', color: 'var(--color-danger)' }}>
                            Delete
                          </button>
                        )}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '48px 24px 52px' }}>
            <h3 style={{ fontSize: 18, margin: '0 0 5px' }}>{details.length ? 'No matching parts' : 'No part detail registered yet'}</h3>
            <p style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', margin: 0 }}>{details.length ? 'Change the Part Number or press Reset.' : 'Click Add Detail to register Minimum MAD and Case/Day of a part.'}</p>
          </div>
        )}
      </div>

      {form && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
          <div style={{ width: 460, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)' }}>
            <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--color-divider)', fontSize: 17, fontWeight: 700 }}>{form.mode === 'add' ? 'Add Part Detail' : ro ? 'Part detail' : 'Edit part detail'}</div>
            <div style={{ padding: '18px 22px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div className="field">
                <label>Part No *</label>
                {form.mode === 'add' ? (
                  <PartNoCombobox value={form.p} options={options} background="var(--color-neutral-100)" placeholder="Select Part Number" onSelect={(o) => setForm({ ...form, p: o ? o.no : '', n: o ? o.name : '' })} />
                ) : (
                  <input className="input" value={form.p} disabled style={{ fontFamily: 'var(--font-mono)', fontSize: 12, background: 'var(--color-neutral-200)' }} />
                )}
              </div>
              <div className="field">
                <label>Part Name</label>
                <input className="input" value={form.n} disabled placeholder="Select Part No first" style={{ background: 'var(--color-neutral-200)' }} />
              </div>
              <div className="field">
                <label>Minimum MAD *</label>
                <input className="input" value={form.minMad} disabled={ro} onChange={(e) => setForm({ ...form, minMad: e.target.value })} placeholder="0" style={{ textAlign: 'right' }} />
              </div>
              <div className="field">
                <label>Case/Day *</label>
                <input className="input" value={form.cd} disabled={ro} onChange={(e) => setForm({ ...form, cd: e.target.value })} placeholder="0" style={{ textAlign: 'right' }} />
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, padding: '14px 22px', borderTop: '1px solid var(--color-divider)' }}>
              <button className="btn btn-secondary" onClick={() => setForm(null)}>
                Cancel
              </button>
              {!ro && (
                <button className="btn btn-primary" onClick={save} disabled={!form.p || !madOk || !cdOk} title={saveTitle}>
                  Save
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {toDelete && (
        <div role="dialog" aria-modal="true" style={{ position: 'fixed', inset: 0, zIndex: 110, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
          <div style={{ width: 380, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '24px 26px 20px', textAlign: 'center' }}>
            <h3 style={{ fontSize: 18, margin: '0 0 8px' }}>Delete part detail</h3>
            <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: '0 0 18px' }}>
              Are you sure you want to delete the record ? <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{toDelete.p}</span>
            </p>
            <span style={{ display: 'inline-flex', gap: 8 }}>
              <button className="btn btn-secondary" onClick={() => setToDelete(null)}>
                No
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  deleteDetail(toDelete.p);
                  setDone(`${toDelete.p} has been deleted.`);
                  setToDelete(null);
                }}
              >
                Yes, delete
              </button>
            </span>
          </div>
        </div>
      )}

      {done && (
        <div role="dialog" aria-modal="true" style={{ position: 'fixed', inset: 0, zIndex: 110, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
          <div style={{ width: 360, background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)', padding: '24px 26px 20px', textAlign: 'center' }}>
            <h3 style={{ fontSize: 18, margin: '0 0 6px' }}>Saved successfully</h3>
            <p style={{ fontSize: 13, color: 'var(--color-neutral-700)', margin: '0 0 18px' }}>{done}</p>
            <button className="btn btn-primary" onClick={() => setDone(null)} style={{ minWidth: 96 }}>
              OK
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
