export function Toast({ text }: { text: string }) {
  if (!text) return null;
  return (
    <div
      style={{
        position: 'fixed',
        right: 24,
        bottom: 84,
        zIndex: 210,
        display: 'flex',
        alignItems: 'center',
        gap: 9,
        padding: '10px 14px',
        borderRadius: 6,
        background: 'var(--color-neutral-900)',
        color: '#fff',
        fontSize: 12.5,
        boxShadow: 'var(--shadow-md)',
      }}
    >
      {text}
    </div>
  );
}
