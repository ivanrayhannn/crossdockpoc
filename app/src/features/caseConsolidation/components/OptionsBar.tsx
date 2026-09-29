import { PRESETS, PRESET_KEYS } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { Stepper } from './Stepper';

export function OptionsBar({ state }: { state: CaseSimulationState }) {
  const { inputs, part, setPart, setPcs, setMaxC, applyPreset, reset, stepOne, fillAll, togglePlay, playing, done, model, role, setRole } = state;
  const disabled = done || !model.rel;

  return (
    <div style={{ background: 'var(--color-neutral-100)', border: '1px dashed var(--color-neutral-400)', borderRadius: 6 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 16px', borderBottom: '1px dashed var(--color-neutral-400)', background: 'var(--color-surface)', borderRadius: '6px 6px 0 0' }}>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 10.5,
            fontWeight: 700,
            letterSpacing: '.07em',
            textTransform: 'uppercase',
            padding: '2px 9px',
            borderRadius: 999,
            background: 'oklch(0.95 0.05 80)',
            color: 'oklch(0.42 0.1 65)',
          }}
        >
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 2v7.31L4.2 19.1A2 2 0 0 0 5.93 22h12.14a2 2 0 0 0 1.73-2.9L14 9.31V2" />
            <path d="M8.5 2h7" />
          </svg>
          Simulation only
        </span>
        <span style={{ fontSize: 14, fontWeight: 700 }}>Simulation options</span>
        <span style={{ fontSize: 12, color: 'var(--color-neutral-600)' }}>For testing scenarios only. Not part of the real screen.</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 18, padding: '12px 16px', flexWrap: 'wrap' }}>
        <div className="field">
          <label>View as</label>
          <span style={{ display: 'flex', padding: 2, borderRadius: 6, background: 'var(--color-neutral-200)' }}>
            {[
              ['sup', 'Supplier'],
              ['ds', 'Demand Supply'],
              ['proc', 'Procurement'],
            ].map(([key, label]) => {
              const active = role === key;
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => setRole(key as typeof role)}
                  style={{
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    fontFamily: 'var(--font-body)',
                    fontSize: 12,
                    fontWeight: 600,
                    padding: '6px 11px',
                    border: 0,
                    borderRadius: 4,
                    background: active ? '#fff' : 'transparent',
                    color: active ? 'var(--color-accent-800)' : 'var(--color-neutral-700)',
                    boxShadow: active ? '0 1px 3px rgba(20,40,70,.15)' : 'none',
                  }}
                >
                  {label}
                </button>
              );
            })}
          </span>
        </div>
        <div className="field">
          <label>Part No</label>
          <input className="input" value={part} onChange={(e) => setPart(e.target.value)} style={{ width: 130, fontFamily: 'var(--font-mono)' }} />
        </div>
        <div className="field">
          <label>Pcs / Case (part master)</label>
          <Stepper value={inputs.pcs} onDec={() => setPcs((n) => n - 1)} onInc={() => setPcs((n) => n + 1)} />
        </div>
        <div className="field">
          <label>Max Case/Day</label>
          <Stepper value={inputs.maxC} onDec={() => setMaxC((n) => n - 1)} onInc={() => setMaxC((n) => n + 1)} />
        </div>
        <span style={{ fontSize: 11.5, color: 'var(--color-neutral-600)', maxWidth: 260, lineHeight: 1.35, paddingBottom: 2 }}>
          Max Case/Day applies to every PO day. Extra cases wait for the next PO.
        </span>
        <span style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ display: 'inline-flex', border: '1px solid var(--color-neutral-400)', borderRadius: 4, overflow: 'hidden' }}>
            {PRESET_KEYS.map((k) => (
              <button
                key={k}
                onClick={() => applyPreset(k)}
                style={{
                  cursor: 'pointer',
                  border: 0,
                  fontFamily: 'var(--font-body)',
                  fontSize: 12.5,
                  fontWeight: 600,
                  padding: '7px 12px',
                  background: inputs.preset === k ? 'var(--color-accent)' : 'var(--color-neutral-100)',
                  color: inputs.preset === k ? '#fff' : 'var(--color-neutral-800)',
                }}
              >
                {PRESETS[k].label}
              </button>
            ))}
          </span>
          <button className="btn btn-secondary" onClick={reset}>
            Reset
          </button>
          <button className="btn btn-secondary" onClick={stepOne} disabled={disabled}>
            Step +1 pc
          </button>
          <button className="btn btn-secondary" onClick={fillAll} disabled={disabled}>
            Fill instantly
          </button>
          <button className="btn btn-primary" onClick={togglePlay} disabled={disabled}>
            {playing ? (
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="5" width="4" height="14" />
                <rect x="14" y="5" width="4" height="14" />
              </svg>
            ) : (
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 4.5v15l12-7.5z" />
              </svg>
            )}
            {playing ? 'Pause' : state.placed ? 'Resume' : 'Play'}
          </button>
        </span>
      </div>
    </div>
  );
}
