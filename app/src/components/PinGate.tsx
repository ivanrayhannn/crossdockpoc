import { useState, type ReactNode } from 'react';
import { card } from '../features/asnCrossdock/styles';
import { sha256 } from '../lib/pin';

/* Light PIN gate for a menu of the prototype. Only the SHA-256 of the PIN is in the code; the unlock lasts for the
 * browser session. This is a client-side gate of a static site, not real access control. */

const SESSION_PREFIX = 'pin.unlocked.';


function isUnlocked(id: string): boolean {
  try { return window.sessionStorage.getItem(SESSION_PREFIX + id) === '1'; } catch { return false; }
}

export function PinGate({ id, title, hash, children }: { id: string; title: string; hash: () => string; children: ReactNode }) {
  const [ok, setOk] = useState(() => isUnlocked(id));
  const [pin, setPin] = useState('');
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(false);

  if (ok) return <>{children}</>;

  const submit = async () => {
    setBusy(true);
    const match = (await sha256(pin.trim())) === hash();
    setBusy(false);
    if (match) {
      try { window.sessionStorage.setItem(SESSION_PREFIX + id, '1'); } catch { /* session only in memory */ }
      setOk(true);
    } else {
      setError(true);
      setPin('');
    }
  };

  return (
    <div style={{ padding: '60px 24px', display: 'flex', justifyContent: 'center' }}>
      <form onSubmit={(e) => { e.preventDefault(); void submit(); }}
        style={{ ...card, padding: '24px 28px', width: 340, display: 'flex', flexDirection: 'column', gap: 12, textAlign: 'center' }}>
        <div style={{ fontSize: 28 }}>🔒</div>
        <div style={{ fontSize: 16, fontWeight: 600 }}>{title}</div>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)' }}>This menu needs a PIN.</div>
        <input autoFocus type="password" inputMode="numeric" value={pin} placeholder="PIN" aria-label="PIN"
          onChange={(e) => { setPin(e.target.value); setError(false); }}
          style={{ padding: '8px 10px', fontSize: 16, letterSpacing: '.3em', textAlign: 'center', borderRadius: 4,
            border: `1px solid ${error ? '#c0392b' : 'var(--color-neutral-400)'}` }} />
        {error && <div style={{ fontSize: 12, color: '#c0392b' }}>Wrong PIN. Try again.</div>}
        <button className="btn btn-primary" type="submit" disabled={!pin || busy}>Open</button>
      </form>
    </div>
  );
}
