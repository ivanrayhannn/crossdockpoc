/** The "− value +" input group used for Pcs/Case, Max Case/Day, and per-order quantity. */
export function Stepper({
  value,
  onDec,
  onInc,
  label,
  size = 'md',
}: {
  value: number;
  onDec: () => void;
  onInc: () => void;
  label: string;
  size?: 'md' | 'sm';
}) {
  return (
    <div className={`input-group${size === 'sm' ? ' input-group-sm' : ''}`} style={{ width: size === 'sm' ? 92 : 112 }}>
      <div className="input-group-prepend">
        <button type="button" className="btn btn-outline-secondary" onClick={onDec} aria-label={`Decrease ${label}`}>
          −
        </button>
      </div>
      <input type="text" className="form-control bg-white text-center font-weight-bold px-0" value={value} readOnly aria-label={label} />
      <div className="input-group-append">
        <button type="button" className="btn btn-outline-secondary" onClick={onInc} aria-label={`Increase ${label}`}>
          +
        </button>
      </div>
    </div>
  );
}
