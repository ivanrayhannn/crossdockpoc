import { useEffect, useId, useMemo, useRef, useState } from 'react';

export interface PartOption {
  no: string;
  name: string;
}

interface Props {
  /** Selected Part No, or '' when nothing is picked yet. */
  value: string;
  options: PartOption[];
  disabled?: boolean;
  background: string;
  /** Called with the picked option, or null once the user edits the text and the previous pick no longer applies. */
  onSelect: (option: PartOption | null) => void;
}

/** Type-to-filter Part No picker. The input only ever holds the Part No itself. */
export function PartNoCombobox({ value, options, disabled, background, onSelect }: Props) {
  const [query, setQuery] = useState(value);
  const [open, setOpen] = useState(false);
  const [hi, setHi] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const listId = useId();

  // Right after a pick the input equals the selection — show the whole catalog
  // then, and only narrow down once the user actually types something else.
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q || query === value) return options;
    return options.filter((o) => o.no.toLowerCase().includes(q) || o.name.toLowerCase().includes(q));
  }, [options, query, value]);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery(value);
      }
    };
    document.addEventListener('mousedown', onDown);
    return () => document.removeEventListener('mousedown', onDown);
  }, [open, value]);

  useEffect(() => {
    if (open) listRef.current?.children[hi]?.scrollIntoView({ block: 'nearest' });
  }, [open, hi]);

  const pick = (opt: PartOption) => {
    onSelect(opt);
    setQuery(opt.no);
    setOpen(false);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!open) setOpen(true);
      else setHi((h) => Math.min(h + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHi((h) => Math.max(h - 1, 0));
    } else if (e.key === 'Enter') {
      if (open && filtered[hi]) {
        e.preventDefault();
        pick(filtered[hi]);
      }
    } else if (e.key === 'Escape' && open) {
      e.stopPropagation();
      setOpen(false);
      setQuery(value);
    }
  };

  return (
    <div ref={rootRef} style={{ position: 'relative' }}>
      <input
        className="input"
        role="combobox"
        aria-expanded={open}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={open && filtered[hi] ? `${listId}-${hi}` : undefined}
        autoComplete="off"
        value={query}
        disabled={disabled}
        placeholder="Ketik atau pilih Part No"
        onChange={(e) => {
          setQuery(e.target.value);
          setHi(0);
          setOpen(true);
          if (value) onSelect(null);
        }}
        onFocus={() => setOpen(true)}
        onClick={() => setOpen(true)}
        onKeyDown={onKeyDown}
        style={{ fontFamily: 'var(--font-mono)', fontSize: 12, background, paddingRight: 30 }}
      />
      <svg
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ position: 'absolute', right: 11, top: 12, pointerEvents: 'none', color: 'var(--color-neutral-600)' }}
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>

      {open && !disabled && (
        <ul
          ref={listRef}
          id={listId}
          role="listbox"
          style={{
            position: 'absolute',
            zIndex: 10,
            top: '100%',
            left: 0,
            right: 0,
            marginTop: 2,
            padding: 4,
            listStyle: 'none',
            maxHeight: 200,
            overflowY: 'auto',
            background: '#fff',
            border: '1px solid var(--color-neutral-400)',
            borderRadius: 4,
            boxShadow: 'var(--shadow-md)',
          }}
        >
          {filtered.length === 0 && <li style={{ padding: '8px 10px', fontSize: 12, color: 'var(--color-neutral-600)' }}>Part tidak ditemukan</li>}
          {filtered.map((o, i) => (
            <li
              key={o.no}
              id={`${listId}-${i}`}
              role="option"
              aria-selected={o.no === value}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => pick(o)}
              onMouseEnter={() => setHi(i)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
                padding: '6px 10px',
                borderRadius: 3,
                cursor: 'pointer',
                background: i === hi ? 'var(--color-accent-200)' : 'transparent',
                fontWeight: o.no === value ? 700 : 400,
              }}
            >
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{o.no}</span>
              <span style={{ fontSize: 11, color: 'var(--color-neutral-600)', fontWeight: 400 }}>{o.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
