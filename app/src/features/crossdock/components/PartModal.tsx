import { MASTER_PARTS } from '../../../data/seed';
import { fmt, num } from '../../../lib/format';
import type { CrossdockState } from '../useCrossdockState';

type StepStyle = { bg: string; fg: string; bd: string; icon: string };

const DONE: StepStyle = { bg: 'var(--color-accent-2-200)', fg: 'var(--color-accent-2-800)', bd: 'var(--color-accent-2-300)', icon: '✓' };
const ACTIVE: StepStyle = { bg: 'var(--color-accent)', fg: '#fff', bd: 'var(--color-accent)', icon: '' };
const IDLE: StepStyle = { bg: 'var(--color-neutral-100)', fg: 'var(--color-neutral-600)', bd: 'var(--color-neutral-400)', icon: '' };

const YEARS = ['2025', '2026', '2027'];

function StepBadge({ n, style }: { n: number; style: StepStyle }) {
  return (
    <span
      style={{
        width: 28,
        height: 28,
        borderRadius: 999,
        display: 'grid',
        placeItems: 'center',
        fontSize: 12.5,
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
  const s2 = pc ? DONE : f.p ? ACTIVE : IDLE;
  const s3 = pc && mc ? DONE : pc ? ACTIVE : IDLE;
  const s4 = pc && mc ? DONE : IDLE;

  const maxLocked = ro || !pc;
  const maxBg = ro || !pc ? 'var(--color-neutral-200)' : 'var(--color-neutral-100)';
  const maxTitle = !pc ? 'Isi Pcs/Case terlebih dahulu' : 'Kapasitas maksimum case per hari';
  const totalPcsDay = pc && mc ? fmt(pc * mc) : '—';
  const totalFg = pc && mc ? 'var(--color-text)' : 'var(--color-neutral-500)';
  const totalFormula = pc && mc ? `${fmt(pc)} pcs/case × ${fmt(mc)} case/day` : !pc ? 'menunggu Pcs/Case' : 'menunggu Max Case/Day';

  const saveDisabled = !f.p || !pc || !mc;
  const saveTitle = !f.p ? 'Part No wajib diisi' : !pc ? 'Isi Pcs/Case dulu (langkah 2)' : !mc ? 'Isi Max Case/Day (langkah 3)' : 'Simpan data part';

  const partTitle = editId ? (ro ? 'Data part' : 'Edit data part') : 'Tambah part';

  const usedIds = new Set(parts.map((p) => p.p));
  const availableMaster = MASTER_PARTS.filter((m) => !usedIds.has(m.no) || m.no === f.p);

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, background: 'rgba(33,33,33,.55)', display: 'grid', placeItems: 'center', padding: 36 }}>
      <div style={{ width: 620, maxHeight: '90vh', overflow: 'auto', background: 'var(--color-neutral-100)', borderRadius: 10, boxShadow: 'var(--shadow-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '20px 26px 14px', borderBottom: '1px solid var(--color-divider)' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 style={{ fontSize: 21, margin: '0 0 2px' }}>{partTitle}</h3>
            <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)' }}>Area Procurement — identitas, Pcs/Case, lalu Max Case/Day. Pembagian ke destinasi dikerjakan tim D/S.</div>
          </div>
          <button onClick={closeModal} title="Tutup" style={{ flex: 'none', cursor: 'pointer', border: 0, background: 'var(--color-neutral-200)', width: 32, height: 32, borderRadius: 999, display: 'grid', placeItems: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
              <line x1="5" y1="5" x2="19" y2="19" />
              <line x1="19" y1="5" x2="5" y2="19" />
            </svg>
          </button>
        </div>

        <div style={{ padding: '20px 26px 6px' }}>
          {/* Step 1 — identity */}
          <div style={{ display: 'flex', gap: 14 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 28 }}>
              <StepBadge n={1} style={s1} />
              <span style={{ width: 2, flex: 1, background: 'var(--color-neutral-300)', margin: '4px 0' }} />
            </div>
            <div style={{ flex: 1, paddingBottom: 18 }}>
              <div style={{ fontSize: 13.5, fontWeight: 700, margin: '4px 0 1px' }}>Identitas part</div>
              <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)', marginBottom: 10 }}>Part No dicek ke master part pabrik; nama terisi otomatis.</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="field">
                  <label>
                    Part No <span style={{ color: 'var(--color-accent-700)' }}>*</span>
                  </label>
                  {editId ? (
                    <input className="input" value={f.p} readOnly style={{ fontFamily: 'var(--font-mono)', fontSize: 13, background: inputBg }} />
                  ) : (
                    <select
                      className="input"
                      value={f.p}
                      onChange={(e) => {
                        const sel = MASTER_PARTS.find((m) => m.no === e.target.value);
                        patch((x) => {
                          x.p = e.target.value;
                          x.n = sel ? sel.name : '';
                        });
                      }}
                      disabled={inputRO}
                      style={{ fontFamily: 'var(--font-mono)', fontSize: 13, background: inputBg, appearance: 'none' }}
                    >
                      <option value="">Pilih part…</option>
                      {availableMaster.map((m) => (
                        <option key={m.no} value={m.no}>
                          {m.no} — {m.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
                <div className="field">
                  <label>Part Name</label>
                  <input className="input" value={f.n} readOnly placeholder="Terisi otomatis dari Part No" style={{ background: inputBg }} />
                </div>
                <div className="field">
                  <label>Effective Start Date</label>
                  <input
                    className="input"
                    type="date"
                    value={f.effDate || ''}
                    onChange={(e) => patch((x) => { x.effDate = e.target.value; })}
                    readOnly={inputRO}
                    style={{ background: inputBg }}
                  />
                </div>
                <div className="field">
                  <label>Year</label>
                  <select
                    className="input"
                    value={f.effYear || YEARS[1]}
                    onChange={(e) => patch((x) => { x.effYear = e.target.value; })}
                    disabled={inputRO}
                    style={{ background: inputBg, appearance: 'none' }}
                  >
                    {YEARS.map((y) => (
                      <option key={y} value={y}>
                        {y}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>Minimum MAD</label>
                  <input
                    className="input"
                    value={String(f.minMad == null ? '' : f.minMad)}
                    onChange={(e) => patch((x) => { x.minMad = e.target.value; })}
                    readOnly={inputRO}
                    placeholder="0"
                    style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums', background: inputBg }}
                  />
                  <div style={{ fontSize: 11, color: 'var(--color-neutral-600)', marginTop: 4 }}>Batas MAD agar part layak crossdock. Di bawah batas, part disarankan Non-Crossdock.</div>
                </div>
              </div>
            </div>
          </div>

          {/* Step 2 — Pcs/Case */}
          <div style={{ display: 'flex', gap: 14 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 28 }}>
              <StepBadge n={2} style={s2} />
              <span style={{ width: 2, flex: 1, background: 'var(--color-neutral-300)', margin: '4px 0' }} />
            </div>
            <div style={{ flex: 1, paddingBottom: 18 }}>
              <div style={{ fontSize: 13.5, fontWeight: 700, margin: '4px 0 1px' }}>Isi Pcs/Case</div>
              <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)', marginBottom: 10 }}>Berapa pcs dalam satu case.</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <input
                  className="input"
                  value={String(f.pc)}
                  onChange={(e) => patch((x) => { x.pc = e.target.value; })}
                  readOnly={inputRO}
                  placeholder="0"
                  style={{ width: 150, textAlign: 'right', fontSize: 15, fontVariantNumeric: 'tabular-nums', background: inputBg }}
                />
                <span style={{ fontSize: 12.5, color: 'var(--color-neutral-700)' }}>pcs per case</span>
              </div>
            </div>
          </div>

          {/* Step 3 — Max Case/Day */}
          <div style={{ display: 'flex', gap: 14, opacity: pc ? 1 : 0.55 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 28 }}>
              <StepBadge n={3} style={s3} />
              <span style={{ width: 2, flex: 1, background: 'var(--color-neutral-300)', margin: '4px 0' }} />
            </div>
            <div style={{ flex: 1, paddingBottom: 18 }}>
              <div style={{ fontSize: 13.5, fontWeight: 700, margin: '4px 0 1px' }}>Isi Max Case/Day</div>
              <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)', marginBottom: 10 }}>Kapasitas maksimum satu part per hari. Dibagi ke destinasi lewat pop-up Mapping.</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <input
                  className="input"
                  value={String(f.mc)}
                  onChange={(e) => patch((x) => { x.mc = e.target.value; })}
                  readOnly={maxLocked}
                  placeholder="0"
                  title={maxTitle}
                  style={{ width: 150, textAlign: 'right', fontSize: 15, fontVariantNumeric: 'tabular-nums', background: maxBg }}
                />
                <span style={{ fontSize: 12.5, color: 'var(--color-neutral-700)' }}>case per hari</span>
                {!pc && !ro && (
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11.5, color: 'var(--color-neutral-700)', padding: '3px 10px', borderRadius: 999, background: 'var(--color-neutral-200)' }}>
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round">
                      <rect x="4" y="10.5" width="16" height="11" rx="3" />
                      <path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" />
                    </svg>
                    Isi Pcs/Case dulu
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Step 4 — total */}
          <div style={{ display: 'flex', gap: 14 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 'none', width: 28 }}>
              <span style={{ width: 28, height: 28, borderRadius: 999, display: 'grid', placeItems: 'center', background: s4.bg, color: s4.fg, border: `1.5px solid ${s4.bd}` }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <line x1="5" y1="7" x2="19" y2="7" />
                  <line x1="5" y1="17" x2="19" y2="17" />
                </svg>
              </span>
            </div>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 12, padding: '11px 15px', borderRadius: 14, background: 'var(--color-surface)', marginBottom: 14 }}>
              <div>
                <div style={{ fontSize: 10, letterSpacing: '.07em', textTransform: 'uppercase', color: 'var(--color-neutral-700)' }}>Total Pcs/Day</div>
                <div style={{ fontSize: 11, color: 'var(--color-neutral-600)' }}>{totalFormula}</div>
              </div>
              <div style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: 24, fontWeight: 500, lineHeight: 1.1, fontVariantNumeric: 'tabular-nums', color: totalFg }}>{totalPcsDay}</div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '14px 26px 18px', borderTop: '1px solid var(--color-divider)', background: 'var(--color-surface)', borderRadius: '0 0 26px 26px' }}>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={closeModal}>
              Batal
            </button>
            {!ro && (
              <button className="btn btn-primary" onClick={commit} disabled={saveDisabled} title={saveTitle}>
                Simpan
              </button>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}
