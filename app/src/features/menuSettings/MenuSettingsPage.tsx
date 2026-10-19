import { LOCKED_ITEMS, NAV_GROUPS, setHiddenMenus, useHiddenMenus } from '../../lib/nav';
import { useState } from 'react';
import { ALWAYS_PIN, changePin, resetPin, setPinMenus, usePinMenus } from '../../lib/pin';
import { ROUTE_BY_NAV_ITEM } from '../../routes';

const card = { border: '1px solid var(--color-divider)', borderRadius: 8, background: 'var(--color-neutral-100)', boxShadow: 'var(--shadow-sm)' };

function ChangePinCard() {
  const [cur, setCur] = useState('');
  const [next, setNext] = useState('');
  const [again, setAgain] = useState('');
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const inp = { padding: '5px 8px', fontSize: 13, width: 110, letterSpacing: '.2em', border: '1px solid var(--color-neutral-400)', borderRadius: 4 };
  const save = async () => {
    if (next !== again) { setMsg({ ok: false, text: 'New PIN and confirmation are different.' }); return; }
    const err = await changePin(cur, next);
    setMsg(err ? { ok: false, text: err } : { ok: true, text: 'PIN changed. It is used for every menu with 🔒 PIN.' });
    if (!err) { setCur(''); setNext(''); setAgain(''); }
  };
  return (
    <div style={{ ...card, padding: '12px 14px', display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', fontSize: 12.5 }}>
      <b style={{ fontSize: 13.5 }}>🔒 Menu PIN</b>
      <label>Current PIN <input type="password" inputMode="numeric" aria-label="Current PIN" value={cur} onChange={(e) => setCur(e.target.value)} style={inp} /></label>
      <label>New PIN <input type="password" inputMode="numeric" aria-label="New PIN" value={next} onChange={(e) => setNext(e.target.value)} style={inp} /></label>
      <label>Confirm <input type="password" inputMode="numeric" aria-label="Confirm new PIN" value={again} onChange={(e) => setAgain(e.target.value)} style={inp} /></label>
      <button className="btn btn-primary" disabled={!cur || !next || !again} onClick={() => { void save(); }}>Change PIN</button>
      <button className="btn btn-secondary" onClick={() => { resetPin(); setMsg({ ok: true, text: 'PIN reset to the default.' }); }}>Reset to default</button>
      {msg && <span style={{ color: msg.ok ? '#1e7e34' : '#c0392b' }}>{msg.text}</span>}
      <span style={{ flexBasis: '100%', fontSize: 11.5, color: 'var(--color-neutral-600)' }}>One PIN for Menu Settings and every menu with 🔒 PIN (4-8 digits). Kept in this browser (prototype).</span>
    </div>
  );
}

/** Admin panel: choose which sidebar menus are shown. Saved at once in this browser (prototype). */
export function MenuSettingsPage() {
  const hidden = useHiddenMenus();
  const pins = usePinMenus();
  const togglePin = (item: string) => setPinMenus(pins.includes(item) ? pins.filter((p) => p !== item) : [...pins, item]);
  const all = NAV_GROUPS.flatMap(([, items]) => items);
  const shown = all.filter((i) => !hidden.includes(i)).length;

  const toggle = (item: string) => setHiddenMenus(hidden.includes(item) ? hidden.filter((h) => h !== item) : [...hidden, item]);
  const setGroup = (items: string[], show: boolean) =>
    setHiddenMenus(show ? hidden.filter((h) => !items.includes(h)) : [...new Set([...hidden, ...items])]);

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
        <div style={{ marginRight: 'auto' }}>
          <h1 style={{ fontSize: 22, margin: 0 }}>Menu Settings</h1>
          <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
            Admin panel: choose which menus are shown in the sidebar and which menus need the PIN (🔒). Changes apply at once. Menu Settings itself is always shown and always needs the PIN.
          </div>
        </div>
        <span style={{ fontSize: 12.5, alignSelf: 'center' }}><b>{shown}</b> of {all.length} menus shown · <b>{pins.length + ALWAYS_PIN.size}</b> with PIN</span>
        <button className="btn btn-secondary" disabled={!hidden.length} onClick={() => setHiddenMenus([])}>Show all</button>
      </div>
      <ChangePinCard />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 }}>
        {NAV_GROUPS.map(([group, items]) => {
          const free = items.filter((i) => !LOCKED_ITEMS.has(i));
          const groupShown = items.filter((i) => !hidden.includes(i)).length;
          return (
            <div key={group} style={card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', borderBottom: '1px solid var(--color-divider)' }}>
                <span style={{ fontWeight: 600, fontSize: 13.5, marginRight: 'auto' }}>{group}</span>
                <span style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>{groupShown}/{items.length}</span>
                <button className="btn btn-secondary" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setGroup(free, true)}>Show all</button>
                <button className="btn btn-secondary" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setGroup(free, false)}>Hide all</button>
              </div>
              <div style={{ padding: '6px 14px 10px' }}>
                {items.map((item) => {
                  const locked = LOCKED_ITEMS.has(item);
                  const on = !hidden.includes(item);
                  const pinFixed = ALWAYS_PIN.has(item);
                  const pinOn = pinFixed || pins.includes(item);
                  const routed = Boolean(ROUTE_BY_NAV_ITEM[item]);
                  return (
                    <div key={item} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0', fontSize: 12.5 }}>
                      <input type="checkbox" aria-label={`Show ${item}`} title="Show in sidebar" checked={on} disabled={locked} onChange={() => toggle(item)} />
                      <span style={{ flex: 1, color: on ? undefined : 'var(--color-neutral-600)' }}>{item}</span>
                      {locked && <span style={{ fontSize: 10.5, color: 'var(--color-neutral-600)' }}>always shown</span>}
                      {!routed && !locked && <span style={{ fontSize: 10.5, color: 'var(--color-neutral-600)' }}>existing menu</span>}
                      <label title={pinFixed ? 'Always needs the PIN' : routed ? 'Needs the PIN' : 'Existing menu: no page in the prototype'}
                        style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11.5, cursor: pinFixed || !routed ? 'default' : 'pointer',
                          color: pinOn ? '#8a4b00' : 'var(--color-neutral-600)' }}>
                        <input type="checkbox" aria-label={`PIN for ${item}`} checked={pinOn} disabled={pinFixed || !routed} onChange={() => togglePin(item)} />
                        🔒 PIN
                      </label>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>
        Prototype: the settings are kept in this browser; the PIN is checked in the browser (light gate, not real access control). In Supplier System it would be saved per role in the system master (TBD).
      </div>
    </div>
  );
}
