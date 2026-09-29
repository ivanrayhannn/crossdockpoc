import type { CSSProperties } from 'react';
import type { Hole } from '../deliveryPlan';
import type { CaseHole } from '../visual';

/** Round "case tray" with one hole per piece — the packing-crate visual used across this feature. */
export function CaseHoles({ holes, size = 28, fontSize = 9, gap = 8, pad = '9px 14px' }: { holes: (Hole | CaseHole)[]; size?: number; fontSize?: number; gap?: number; pad?: string }) {
  return (
    <span style={{ flex: 1, display: 'flex', flexWrap: 'wrap', gap, padding: pad, borderRadius: 999, background: '#e9e1d4', boxShadow: 'inset 0 2px 5px rgba(80,50,20,.22)' }}>
      {holes.map((h, i) => {
        const scale = 'scale' in h ? h.scale : 1;
        const shadow = 'shadow' in h ? h.shadow : '0 1px 2px rgba(0,0,0,.25)';
        const style: CSSProperties = {
          width: size,
          height: size,
          borderRadius: 999,
          display: 'grid',
          placeItems: 'center',
          background: h.bg,
          boxShadow: shadow,
          fontSize,
          fontWeight: 700,
          color: '#fff',
          transform: `scale(${scale})`,
          transition: 'transform .15s',
          flex: 'none',
        };
        return (
          <span key={i} style={style}>
            {h.lbl}
          </span>
        );
      })}
    </span>
  );
}
