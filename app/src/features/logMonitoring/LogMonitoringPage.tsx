import { useState } from 'react';
import { useLogs } from '../asnCrossdock/asnStore';
import { Chip } from '../asnCrossdock/ui';
import { card, th, td } from '../asnCrossdock/styles';

/** Log Monitoring (prototype): batch runs started from the screens, e.g. the ASN submit batch (X14) by Submit ID. */
export function LogMonitoringPage() {
  const logs = useLogs();
  const [open, setOpen] = useState<Record<string, boolean>>({});

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>Log Monitoring</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          Prototype of the existing Supplier System log: one record per batch run with its messages. The ASN submit batch writes here with its Submit ID.
        </div>
      </div>
      <div style={{ ...card, overflow: 'hidden' }}>
        <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--color-divider)', fontSize: 12.5, fontWeight: 600 }}>
          Log list <span style={{ fontWeight: 400, color: 'var(--color-neutral-600)', fontSize: 11.5 }}>{logs.length} records (this browser session)</span>
        </div>
        {logs.length === 0 ? (
          <div style={{ padding: '40px 24px', textAlign: 'center', fontSize: 13 }}>No log yet. Submit an ASN in ASN Crossdock Creation to see the batch log here.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead><tr><th style={{ ...th, width: 34 }} />{['Submit ID', 'Function', 'Process', 'Status', 'User', 'Start', 'End'].map((h) => <th key={h} style={th}>{h}</th>)}</tr></thead>
            <tbody>
              {logs.map((l) => [
                <tr key={l.submitId}>
                  <td style={td}><button className="btn btn-secondary" title="Messages" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setOpen({ ...open, [l.submitId]: !open[l.submitId] })}>{open[l.submitId] ? '▾' : '▸'}</button></td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{l.submitId}</td>
                  <td style={td}>{l.functionId}</td>
                  <td style={td}>{l.process}</td>
                  <td style={td}><Chip tone={l.status === 'Success' ? 'ok' : l.status === 'Processing' ? 'warn' : 'neutral'}>{l.status}</Chip></td>
                  <td style={td}>{l.createdBy}</td>
                  <td style={td}>{l.startAt}</td>
                  <td style={td}>{l.endAt ?? '—'}</td>
                </tr>,
                open[l.submitId] && (
                  <tr key={`${l.submitId}-m`}>
                    <td colSpan={8} style={{ padding: '6px 16px 12px 50px', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-divider)' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                        <thead><tr>{['Time', 'Type', 'Message ID', 'Message'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                        <tbody>
                          {l.messages.map((m, i) => (
                            <tr key={i}><td style={td}>{m.time}</td><td style={td}>{m.type}</td><td style={td}>{m.msgId}</td><td style={td}>{m.text}</td></tr>
                          ))}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                ),
              ])}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
