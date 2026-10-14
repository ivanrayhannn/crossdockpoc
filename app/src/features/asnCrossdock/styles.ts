import type { CSSProperties } from 'react';

export const card: CSSProperties = { border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', boxShadow: 'var(--shadow-sm)' };

export const th: CSSProperties = {
  textAlign: 'left', padding: '0 10px', height: 32, fontSize: 9.5, letterSpacing: '.06em', textTransform: 'uppercase',
  color: 'var(--color-neutral-700)', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-neutral-400)', whiteSpace: 'nowrap',
};

export const td: CSSProperties = { padding: '7px 10px', borderBottom: '1px solid var(--color-divider)', verticalAlign: 'top' };
