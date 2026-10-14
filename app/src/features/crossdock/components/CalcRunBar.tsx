export interface CalcRun {
  /** Date-time of the last successful run. */
  lastSuccess: string;
  /** Failed scheduled attempts since the last success (auto retry stops at 3). */
  failedRetries: number;
}

/** Last success date of a calculation batch plus its manual trigger.
 * The trigger is enabled only after the scheduled run and its 3 auto retries have failed. */
export function CalcRunBar({ label, run, ro, onRun }: { label: string; run: CalcRun; ro: boolean; onRun: () => void }) {
  const failed = run.failedRetries >= 3;
  const enabled = failed && !ro;
  return (
    <span style={{ display: 'flex', alignItems: 'center', gap: 9, fontSize: 11.5, color: 'var(--color-neutral-700)' }}>
      <span>
        Last {label}: <span style={{ fontVariantNumeric: 'tabular-nums', color: 'var(--color-text)', fontWeight: 600 }}>{run.lastSuccess}</span>
      </span>
      {failed && (
        <span style={{ padding: '2px 9px', borderRadius: 999, fontSize: 11, fontWeight: 600, background: 'var(--color-danger-bg)', color: 'var(--color-danger)' }}>
          Scheduled run failed 3x
        </span>
      )}
      <button
        className="btn btn-secondary"
        onClick={onRun}
        disabled={!enabled}
        title={enabled ? `Run the ${label} now` : 'Enabled only when the scheduled run has failed 3 times'}
        style={{ fontSize: 12, padding: '4px 12px' }}
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="7 4 19 12 7 20 7 4" />
        </svg>
        Run calculation
      </button>
    </span>
  );
}
