import { MASTER_PARTS } from '../../../data/seed';
import { fmt, num } from '../../../lib/format';
import type { PartStatus } from '../../../types';
import type { CrossdockState } from '../useCrossdockState';
import { PartNoCombobox } from './PartNoCombobox';

function todayStr(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

type StepStyle = { bg: string; fg: string; bd: string; icon: string };

const DONE: StepStyle = { bg: 'var(--color-accent-2-200)', fg: 'var(--color-accent-2-800)', bd: 'var(--color-accent-2-300)', icon: '✓' };
const ACTIVE: StepStyle = { bg: 'var(--color-accent)', fg: '#fff', bd: 'var(--color-accent)', icon: '' };
const IDLE: StepStyle = { bg: 'var(--color-neutral-100)', fg: 'var(--color-neutral-600)', bd: 'var(--color-neutral-400)', icon: '' };

function StepBadge({ n, style }: { n: number; style: StepStyle }) {
  return (
    <span
      style={{
        width: 23,
        height: 23,
        borderRadius: 999,
        display: 'grid',
        placeItems: 'center',
        fontSize: 11,
        fontWeight: 700,
        background: style.bg,
        color: style.fg,
        border: `1.5px solid ${style.bd}`,
      }}
    >
      {style.icon || n}
    </span>
  );
}

export function PartModal({ state }: { state: CrossdockState }) {
  const { form: f, ro, editId, parts, patch, closeModal, commit } = state;
  if (!f) return null;

  const pc = num(f.pc);
  const mc = num(f.mc);
  const inputRO = ro;
  const inputBg = ro ? 'var(--color-neutral-200)' : 'var(--color-neutral-100)';

  const s1 = f.p ? DONE : ACTIVE;
  const s2 = pc && mc ? DONE : f.p ? ACTIVE : IDLE;
  const s3 = pc && mc ? DONE : IDLE;

  const maxLocked = ro || !pc;
  const maxBg = ro || !pc ? 'var(--color-neutral-200)' : 'var(--color-neutral-100)';
  const maxTitle = !pc ? 'Enter Pcs/Case first' : 'Maximum cases per day';
  const totalPcsDay = pc && mc ? fmt(pc * mc) : '—';
  const totalFg = pc && mc ? 'var(--color-text)' : 'var(--color-neutral-500)';

  const saveDisabled = !f.p || !pc || !mc;
  const saveTitle = !f.p ? 'Part No is required' : !pc ? 'Enter Pcs/Case first (step 2)' : !mc ? 'Enter Max Case/Day (step 2)' : 'Save part data';

  // Effective Start Date stays editable while the saved part is still a Candidate; once it is
  // Active/Inactive the date has taken effect and is locked. A new part (Add form) is always open.
  const savedStatus = editId ? parts.find((p) => p.p === editId)?.st : undefined;
  const effDateLocked = inputRO || (!!editId && savedStatus !== 'Candidate');

  // A newly added part always starts as Candidate; the status only becomes
  // editable once the part exists.
  const statusLocked = inputRO || !editId;

  const partTitle = editId ? (ro ? 'Part data' : 'Edit part data') : 'Add Part Candidate Crossdock';

  const usedIds = new Set(parts.map((p) => p.p));
  const availableMaster = MASTER_PARTS.filter((m) => !usedIds.has(m.no) || m.no === f.p);

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
      <div style={{ width: 500, maxHeight: '90vh', overflow: 'auto', background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '15px 20px 11px', borderBottom: '1px solid var(--color-divider)' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 style={{ fontSize: 17, margin: '0 0 2px' }}>{partTitle}</h3>
          </div>
          <button onClick={closeModal} title="Close" style={{ flex: 'none', cursor: 'pointer', border: 0, background: 'var(--color-neutral-200)', width: 26, height: 26, borderRadius: 999, display: 'grid', placeItems: 'center' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
              <line x1="5" y1="5" x2="19" y2="19" />
              <line x1="19" y1="5" x2="5" y2="19" />
            </svg>
          </button>
        </div>

        <div style={{ padding: '15px 20px 4px' }}>
          {/* Step 1 — identity */}
          <div style={{ display: 'flex', gap: 11 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 23 }}>
              <StepBadge n={1} style={s1} />
              <span style={{ width: 2, flex: 1, background: 'var(--color-neutral-300)', margin: '4px 0' }} />
            </div>
            <div style={{ flex: 1, paddingBottom: 14 }}>
              <div style={{ fontSize: 12, fontWeight: 700, margin: '2px 0 1px' }}>Part Candidate</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div className="field" style={{ gridColumn: '1 / -1' }}>
                  <label>Status</label>
                  <select
                    className="input"
                    value={f.st}
                    onChange={(e) => patch((x) => { x.st = e.target.value as PartStatus; })}
                    disabled={statusLocked}
                    title={!editId ? 'New parts are automatically Candidate' : undefined}
                    style={{ background: statusLocked ? 'var(--color-neutral-200)' : inputBg, appearance: 'none' }}
                  >
                    <option value="Candidate">Candidate</option>
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
                </div>
                <div className="field">
                  <label>
                    Part No <span style={{ color: 'var(--color-accent-700)' }}>*</span>
                  </label>
                  {editId ? (
                    <input className="input" value={f.p} disabled style={{ fontFamily: 'var(--font-mono)', fontSize: 12, background: inputBg }} />
                  ) : (
                    <PartNoCombobox
                      value={f.p}
                      options={availableMaster}
                      disabled={inputRO}
                      background={inputBg}
                      placeholder="Select Part Number"
                      onSelect={(opt) =>
                        patch((x) => {
                          x.p = opt ? opt.no : '';
                          x.n = opt ? opt.name : '';
                        })
                      }
                    />
                  )}
                </div>
                <div className="field">
                  <label>
                    Part Name <span style={{ color: 'var(--color-accent-700)' }}>*</span>
                  </label>
                  <input className="input" value={f.n} disabled placeholder="Select Part No field" style={{ background: 'var(--color-neutral-200)' }} />
                </div>
                <div className="field">
                  <label>Effective Start Date</label>
                  <input
                    className="input"
                    type="date"
                    value={f.effDate || ''}
                    min={todayStr()}
                    onChange={(e) => patch((x) => { x.effDate = e.target.value; })}
                    disabled={effDateLocked}
                    title={effDateLocked && !inputRO ? 'Can only be changed while the status is still Candidate' : undefined}
                    style={{ background: effDateLocked ? 'var(--color-neutral-200)' : inputBg }}
                  />
                </div>
                <div className="field">
                  <label>Minimum MAD</label>
                  <input
                    className="input"
                    value={String(f.minMad == null ? '' : f.minMad)}
                    onChange={(e) => patch((x) => { x.minMad = e.target.value; })}
                    disabled={inputRO}
                    placeholder="0"
                    style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums', background: inputBg }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Step 2 — Pcs/Case & Max Case/Day */}
          <div style={{ display: 'flex', gap: 11 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 23 }}>
              <StepBadge n={2} style={s2} />
              <span style={{ width: 2, flex: 1, background: 'var(--color-neutral-300)', margin: '4px 0' }} />
            </div>
            <div style={{ flex: 1, paddingBottom: 14 }}>
              <div style={{ fontSize: 12, fontWeight: 700, margin: '2px 0 8px' }}>Fill in Pcs/Case & Max Case/Day</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div className="field">
                  <label>Pcs/Case</label>
                  <input
                    className="input"
                    value={String(f.pc)}
                    onChange={(e) => patch((x) => { x.pc = e.target.value; })}
                    disabled={inputRO}
                    placeholder="0"
                    style={{ textAlign: 'right', fontSize: 13, fontVariantNumeric: 'tabular-nums', background: inputBg }}
                  />
                </div>
                <div className="field" style={{ opacity: pc ? 1 : 0.55 }}>
                  <label>Max Case/Day</label>
                  <input
                    className="input"
                    value={String(f.mc)}
                    onChange={(e) => patch((x) => { x.mc = e.target.value; })}
                    disabled={maxLocked}
                    placeholder="0"
                    title={maxTitle}
                    style={{ textAlign: 'right', fontSize: 13, fontVariantNumeric: 'tabular-nums', background: maxBg }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Step 3 — total */}
          <div style={{ display: 'flex', gap: 11 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 23 }}>
              <span style={{ width: 23, height: 23, borderRadius: 999, display: 'grid', placeItems: 'center', background: s3.bg, color: s3.fg, border: `1.5px solid ${s3.bd}` }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <line x1="5" y1="7" x2="19" y2="7" />
                  <line x1="5" y1="17" x2="19" y2="17" />
                </svg>
              </span>
            </div>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10, padding: '9px 12px', borderRadius: 12, background: 'var(--color-surface)', marginBottom: 11 }}>
              <div>
                <div style={{ fontSize: 9, letterSpacing: '.07em', textTransform: 'uppercase', color: 'var(--color-neutral-700)' }}>Total Pcs/Day</div>
              </div>
              <div style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: 19, fontWeight: 500, lineHeight: 1.1, fontVariantNumeric: 'tabular-nums', color: totalFg }}>{totalPcsDay}</div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '11px 20px 15px', borderTop: '1px solid var(--color-divider)', background: 'var(--color-surface)', borderRadius: '0 0 26px 26px' }}>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={closeModal}>
              Cancel
            </button>
            {!ro && (
              <button className="btn btn-primary" onClick={commit} disabled={saveDisabled} title={saveTitle}>
                Save
              </button>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}
