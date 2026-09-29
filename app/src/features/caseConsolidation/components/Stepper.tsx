/** The "− value +" pill used for Pcs/Case, Max Case/Day, and per-order quantity. */
export function Stepper({
  value,
  onDec,
  onInc,
  size = 'md',
}: {
  value: number;
  onDec: () => void;
  onInc: () => void;
  size?: 'md' | 'sm';
}) {
  const btnSize = size === 'md' ? 32 : 26;
  const valWidth = size === 'md' ? 44 : 30;
  const fontSize = size === 'md' ? 16 : 14;
  const valFontSize = size === 'md' ? 14 : 12.5;
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', border: '1px solid var(--color-neutral-400)', borderRadius: 4, overflow: 'hidden', background: 'var(--color-neutral-100)' }}>
      <button
        onClick={onDec}
        style={{ cursor: 'pointer', border: 0, background: 'var(--color-neutral-200)', width: btnSize, height: btnSize, fontSize, color: 'var(--color-neutral-800)' }}
      >
        −
      </button>
      <span style={{ width: valWidth, textAlign: 'center', fontWeight: 700, fontVariantNumeric: 'tabular-nums', fontSize: valFontSize }}>{value}</span>
      <button
        onClick={onInc}
        style={{ cursor: 'pointer', border: 0, background: 'var(--color-neutral-200)', width: btnSize, height: btnSize, fontSize, color: 'var(--color-neutral-800)' }}
      >
        +
      </button>
    </span>
  );
}
