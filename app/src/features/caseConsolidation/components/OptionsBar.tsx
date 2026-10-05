import { PRESETS, PRESET_KEYS } from '../simulation';
import type { CaseSimulationState } from '../useCaseSimulation';
import { Stepper } from './Stepper';

const ROLES = [
  ['sup', 'Supplier'],
  ['ds', 'Demand Supply'],
  ['proc', 'Procurement'],
] as const;

export function OptionsBar({ state }: { state: CaseSimulationState }) {
  const { inputs, setPcs, setMaxC, applyPreset, reset, stepOne, fillAll, togglePlay, playing, done, model, role, setRole } = state;
  const disabled = done || !model.rel;

  return (
    <div className="card" style={{ borderStyle: 'dashed' }}>
      <div className="card-header d-flex align-items-center flex-wrap py-1">
        <span className="badge badge-warning text-uppercase mr-2">
          <svg className="mr-1" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.75" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 2v7.31L4.2 19.1A2 2 0 0 0 5.93 22h12.14a2 2 0 0 0 1.73-2.9L14 9.31V2" />
            <path d="M8.5 2h7" />
          </svg>
          Simulation only
        </span>
        <h6 className="mb-0 mr-2">Simulation options</h6>
        <small className="text-muted">For testing scenarios only, not part of the real screen. Customer Orders can share a number across multiple Part Nos; Max Case/Day applies to every PO day.</small>
      </div>

      <div className="card-body py-2">
        <div className="form-row align-items-end">
          <div className="form-group col-auto mb-0">
            <span className="d-block small text-muted mb-1">View as</span>
            <div className="btn-group btn-group-sm" role="group" aria-label="View as">
              {ROLES.map(([key, label]) => (
                <button key={key} type="button" className={`btn ${role === key ? 'btn-primary' : 'btn-outline-primary'}`} onClick={() => setRole(key)}>
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group col-auto mb-0">
            <span className="d-block small text-muted mb-1" title="Pcs per case, from the part master">
              Pcs / Case
            </span>
            <Stepper size="sm" label="Pcs / Case" value={inputs.pcs} onDec={() => setPcs((n) => n - 1)} onInc={() => setPcs((n) => n + 1)} />
          </div>

          <div className="form-group col-auto mb-0">
            <span className="d-block small text-muted mb-1">Max Case/Day</span>
            <Stepper size="sm" label="Max Case/Day" value={inputs.maxC} onDec={() => setMaxC((n) => n - 1)} onInc={() => setMaxC((n) => n + 1)} />
          </div>

          <div className="form-group col-auto ml-auto mb-0 d-flex align-items-center flex-wrap">
            <div className="btn-group btn-group-sm mr-1" role="group" aria-label="Scenario preset">
              {PRESET_KEYS.map((k) => (
                <button key={k} type="button" className={`btn ${inputs.preset === k ? 'btn-secondary' : 'btn-outline-secondary'}`} onClick={() => applyPreset(k)}>
                  {PRESETS[k].label}
                </button>
              ))}
            </div>
            <button type="button" className="btn btn-outline-secondary btn-sm mr-1" onClick={reset}>
              Reset
            </button>
            <button type="button" className="btn btn-outline-secondary btn-sm mr-1" onClick={stepOne} disabled={disabled}>
              Step +1 pc
            </button>
            <button type="button" className="btn btn-outline-secondary btn-sm mr-1" onClick={fillAll} disabled={disabled}>
              Fill instantly
            </button>
            <button type="button" className="btn btn-primary btn-sm" onClick={togglePlay} disabled={disabled}>
              {playing ? (
                <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="5" width="4" height="14" />
                  <rect x="14" y="5" width="4" height="14" />
                </svg>
              ) : (
                <svg className="mr-1" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M7 4.5v15l12-7.5z" />
                </svg>
              )}
              {playing ? 'Pause' : state.placed ? 'Resume' : 'Play'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
