import { useMemo, useState } from 'react';
import { card, th, td } from '../asnCrossdock/styles';
import { BPF } from './bpfData';
import type { BpfFlow, BpfStep } from './types';

/* Business Process Flow level 2: X = PIC lane, Y = timeline; boxes down to table level, red tags = abnormality.
 * Data is generated from deliverables/function_list_v2/bpf/bpf_data.py (also used for the Excel). */

const AXIS_W = 150;
const LANE_W = 230;
const BOX_W = 200;
const HEADER_H = 44;
const GAP = 38;

const LANE_COLOR: Record<string, { bg: string; bd: string }> = {
  GT: { bg: '#ededed', bd: '#8c8c8c' },
  NB: { bg: '#dbe5f4', bd: '#5b7bb4' },
  PR: { bg: '#e3f1df', bd: '#6a9f5b' },
  DS: { bg: '#fde4d4', bd: '#d08a5c' },
  SP: { bg: '#fff2cc', bd: '#c9a63b' },
  AP: { bg: '#ece4f5', bd: '#8a6fb5' },
};

type Names = 'proto' | 'doc';

function rename(s: string, names: Names): string {
  if (names === 'doc') return s;
  return s.replace(/G-TOPAS/g, 'T-System').replace(/NSP Batch \(System\)/g, 'Supplier System (Batch)').replace(/\bNSP\b/g, 'Supplier System');
}

const lines = (s: string, perLine: number) => Math.max(1, Math.ceil(s.length / perLine));

function boxHeight(s: BpfStep): number {
  let h = 10 + 14 + lines(s.title, 31) * 12.5;
  for (const list of [s.read, s.write]) if (list.length) h += 4 + list.reduce((a, t) => a + lines(t, 33) * 11, 0);
  return Math.ceil(h + 8);
}

interface Layout {
  width: number;
  height: number;
  rowTop: number[];
  rowH: number[];
  rowOf: (s: BpfStep) => number;
  bandRows: { id: string; label: string; first: number; last: number }[];
  boxH: Record<string, number>;
}

function layout(flow: BpfFlow): Layout {
  const bandStart: Record<string, number> = {};
  let n = 0;
  const bandRows = flow.bands.map((b) => {
    bandStart[b.id] = n;
    n += b.slots;
    return { id: b.id, label: b.label, first: bandStart[b.id], last: n - 1 };
  });
  const rowOf = (s: BpfStep) => bandStart[s.band] + s.slot;
  const boxH: Record<string, number> = {};
  const rowH = Array.from({ length: n }, () => 56);
  for (const s of flow.steps) {
    boxH[s.id] = boxHeight(s);
    rowH[rowOf(s)] = Math.max(rowH[rowOf(s)], boxH[s.id]);
  }
  const rowTop: number[] = [];
  let y = HEADER_H + GAP / 2 + 6;
  for (let i = 0; i < n; i++) {
    rowTop.push(y);
    y += rowH[i] + GAP;
  }
  return { width: AXIS_W + flow.lanes.length * LANE_W, height: y - GAP / 2 + 6, rowTop, rowH, rowOf, bandRows, boxH };
}

function edgePath(flow: BpfFlow, L: Layout, a: BpfStep, b: BpfStep, k: number): string {
  const la = flow.lanes.indexOf(a.lane);
  const lb = flow.lanes.indexOf(b.lane);
  const sx = AXIS_W + la * LANE_W + LANE_W / 2;
  const tx = AXIS_W + lb * LANE_W + LANE_W / 2;
  const ra = L.rowOf(a);
  const rb = L.rowOf(b);
  const sTop = L.rowTop[ra];
  const sb = sTop + L.boxH[a.id];
  const tt = L.rowTop[rb];
  if (ra === rb) {
    const y = sTop + Math.min(L.boxH[a.id], L.boxH[b.id]) / 2;
    const x1 = lb > la ? sx + BOX_W / 2 : sx - BOX_W / 2;
    const x2 = lb > la ? tx - BOX_W / 2 : tx + BOX_W / 2;
    return `M${x1},${y} H${x2}`;
  }
  const gapBelow = L.rowTop[ra] + L.rowH[ra] + GAP / 2 + (k % 3) * 4 - 4;
  const gapAbove = tt - GAP / 2 + (k % 3) * 4 - 4;
  if (rb === ra + 1) return la === lb ? `M${sx},${sb} V${tt}` : `M${sx},${sb} V${gapAbove} H${tx} V${tt}`;
  const edge = lb < la ? AXIS_W + la * LANE_W : AXIS_W + (la + 1) * LANE_W;
  const cx = edge + (lb < la ? 1 : -1) * (5 + (k % 3) * 3);
  return `M${sx},${sb} V${gapBelow} H${cx} V${gapAbove} H${tx} V${tt}`;
}

function Diagram({ flow, names, selected, onSelect }: { flow: BpfFlow; names: Names; selected: string | null; onSelect: (id: string) => void }) {
  const L = useMemo(() => layout(flow), [flow]);
  const byId = Object.fromEntries(flow.steps.map((s) => [s.id, s]));
  const edges = flow.steps.flatMap((s) => s.next.map((t) => [s, byId[t]] as const));
  return (
    <svg id="bpf-diagram" width={L.width} height={L.height} viewBox={`0 0 ${L.width} ${L.height}`}
      style={{ display: 'block', background: '#fff', fontFamily: 'Arial, sans-serif' }}>
      <defs>
        <marker id="bpf-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#4a5a75" />
        </marker>
      </defs>
      {L.bandRows.map((b, i) => {
        const y0 = L.rowTop[b.first] - GAP / 2;
        const y1 = L.rowTop[b.last] + L.rowH[b.last] + GAP / 2;
        return (
          <g key={b.id}>
            <rect x={0} y={y0} width={L.width} height={y1 - y0} fill={i % 2 ? '#ffffff' : '#f6f8fb'} />
            <line x1={0} x2={L.width} y1={y1} y2={y1} stroke="#c4ccd8" />
            <rect x={0} y={y0} width={AXIS_W} height={y1 - y0} fill="#1f3864" opacity={0.92 - (i % 2) * 0.12} />
            <foreignObject x={6} y={y0} width={AXIS_W - 12} height={y1 - y0}>
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', color: '#fff', fontSize: 11, fontWeight: 700, lineHeight: 1.3 }}>
                {rename(b.label, names)}
              </div>
            </foreignObject>
          </g>
        );
      })}
      {flow.lanes.map((k, i) => (
        <g key={k}>
          <rect x={AXIS_W + i * LANE_W + 2} y={4} width={LANE_W - 4} height={HEADER_H - 8} rx={4} fill={LANE_COLOR[k].bg} stroke={LANE_COLOR[k].bd} />
          <text x={AXIS_W + i * LANE_W + LANE_W / 2} y={HEADER_H / 2 + 4} textAnchor="middle" fontSize={12} fontWeight={700} fill="#1f2a3d">
            {rename(BPF.lanes[k], names)}
          </text>
          {i > 0 && <line x1={AXIS_W + i * LANE_W} x2={AXIS_W + i * LANE_W} y1={HEADER_H} y2={L.height} stroke="#b7c0cd" strokeDasharray="4 4" />}
        </g>
      ))}
      <rect x={0} y={4} width={AXIS_W - 4} height={HEADER_H - 8} rx={4} fill="#1f3864" />
      <text x={(AXIS_W - 4) / 2} y={HEADER_H / 2 + 4} textAnchor="middle" fontSize={11} fontWeight={700} fill="#fff">Timeline ↓ / PIC →</text>
      {edges.map(([a, b], k) => (
        <path key={`${a.id}-${b.id}`} d={edgePath(flow, L, a, b, k)} fill="none" stroke="#4a5a75" strokeWidth={1.4} markerEnd="url(#bpf-arrow)" />
      ))}
      {flow.steps.map((s) => {
        const li = flow.lanes.indexOf(s.lane);
        const x = AXIS_W + li * LANE_W + (LANE_W - BOX_W) / 2;
        const y = L.rowTop[L.rowOf(s)];
        const h = L.boxH[s.id];
        const c = LANE_COLOR[s.lane];
        return (
          <g key={s.id} onClick={() => onSelect(s.id)} style={{ cursor: 'pointer' }}>
            <rect x={x} y={y} width={BOX_W} height={h} rx={5} fill={c.bg} stroke={selected === s.id ? '#c00000' : c.bd}
              strokeWidth={selected === s.id ? 2.5 : 1.2} strokeDasharray={s.fn === 'existing' || s.fn === 'manual' ? '5 3' : undefined} />
            <foreignObject x={x + 6} y={y + 5} width={BOX_W - 12} height={h - 8}>
              <div style={{ fontSize: 10, lineHeight: '12.5px', color: '#1f2a3d' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, marginBottom: 1 }}>
                  <span style={{ color: '#c00000' }}>{s.fn || (s.read.length ? 'Receive' : 'Source')}</span><span style={{ color: '#6b7a90' }}>{s.id}</span>
                </div>
                <div style={{ fontWeight: 600 }}>{rename(s.title, names)}</div>
                {s.read.length > 0 && <div style={{ marginTop: 4, fontSize: 9, lineHeight: '11px', color: '#2f5597' }}>{s.read.map((t) => <div key={t}>R: {rename(t, names)}</div>)}</div>}
                {s.write.length > 0 && <div style={{ marginTop: 4, fontSize: 9, lineHeight: '11px', color: '#7b3f00' }}>{s.write.map((t) => <div key={t}>W: {rename(t, names)}</div>)}</div>}
              </div>
            </foreignObject>
            {s.ab.map((a, i) => (
              <g key={a}>
                <rect x={x + BOX_W - 40 - i * 42} y={y - 9} width={38} height={14} rx={7} fill="#c00000" />
                <text x={x + BOX_W - 21 - i * 42} y={y + 1.5} textAnchor="middle" fontSize={9} fontWeight={700} fill="#fff">{a}</text>
              </g>
            ))}
          </g>
        );
      })}
    </svg>
  );
}

function AbnormalityTable({ ids, names }: { ids: string[] | null; names: Names }) {
  const rows = BPF.abnormality.filter((a) => !ids || ids.includes(a.id));
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
      <thead><tr>{['ID', 'Flow', 'Step', 'Function', 'Condition', 'Detection', 'System handling', 'PIC', 'PIC action'].map((h) => <th key={h} style={th}>{h}</th>)}</tr></thead>
      <tbody>
        {rows.map((a) => (
          <tr key={a.id}>
            <td style={{ ...td, fontWeight: 700, color: '#c00000' }}>{a.id}</td><td style={td}>{a.flow}</td><td style={td}>{a.step}</td><td style={td}>{a.fn}</td>
            <td style={td}>{rename(a.condition, names)}</td><td style={td}>{rename(a.detection, names)}</td><td style={td}>{rename(a.system, names)}</td>
            <td style={td}>{a.pic}</td><td style={td}>{rename(a.action, names)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function BusinessProcessFlowPage() {
  const [tab, setTab] = useState<string>(BPF.flows[0].id);
  const [names, setNames] = useState<Names>('proto');
  const [selected, setSelected] = useState<string | null>(null);
  const flow = BPF.flows.find((f) => f.id === tab);
  const step = flow?.steps.find((s) => s.id === selected);
  const flowAb = flow ? [...new Set(flow.steps.flatMap((s) => s.ab))].sort() : null;

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>Business Process Flow</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          Level 2: X = PIC (swimlane), Y = timeline. Each box shows the function, the activity and the tables read (R) / written (W). Red tags = abnormality; click a box for its detail.
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        {[...BPF.flows.map((f) => [f.id, `${f.id} ${f.title}`]), ['AB', 'Abnormality list']].map(([id, label]) => (
          <button key={id} className={`btn ${tab === id ? 'btn-primary' : 'btn-outline-secondary'}`} onClick={() => { setTab(id); setSelected(null); }}>{label}</button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: 12 }}>
          Names:{' '}
          <select aria-label="Names" value={names} onChange={(e) => setNames(e.target.value as Names)} style={{ fontSize: 12, padding: '3px 6px' }}>
            <option value="proto">Prototype (T-System / Supplier System)</option>
            <option value="doc">Document (G-TOPAS / NSP)</option>
          </select>
        </span>
      </div>

      {flow ? (
        <>
          <div style={{ ...card, padding: 12 }}>
            <div style={{ fontSize: 12.5, marginBottom: 8 }}><b>{flow.id} {flow.title}.</b> {rename(flow.desc, names)}</div>
            <div style={{ overflowX: 'auto' }}>
              <Diagram flow={flow} names={names} selected={selected} onSelect={setSelected} />
            </div>
            <div style={{ fontSize: 11, color: 'var(--color-neutral-700)', marginTop: 8 }}>
              Arrow = order of the process · dashed box = existing / manual activity · R = table read · W = table written · red tag = abnormality condition
            </div>
          </div>
          {step && (
            <div style={{ ...card, padding: '12px 16px', fontSize: 12.5 }}>
              <div style={{ fontWeight: 700, marginBottom: 6 }}>{step.id} · {step.fn || (step.read.length ? 'Receive' : 'Source')} · {rename(BPF.lanes[step.lane], names)} · {rename(flow.bands.find((b) => b.id === step.band)?.label ?? '', names)}</div>
              <div style={{ marginBottom: 6 }}>{rename(step.title, names)}</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div><b>Read</b><ul style={{ margin: '2px 0 0', paddingLeft: 18 }}>{step.read.length ? step.read.map((t) => <li key={t}>{rename(t, names)}</li>) : <li>-</li>}</ul></div>
                <div><b>Write</b><ul style={{ margin: '2px 0 0', paddingLeft: 18 }}>{step.write.length ? step.write.map((t) => <li key={t}>{rename(t, names)}</li>) : <li>-</li>}</ul></div>
              </div>
              {step.ab.length > 0 && <div style={{ marginTop: 8 }}><AbnormalityTable ids={step.ab} names={names} /></div>}
            </div>
          )}
          <div style={{ ...card, padding: '12px 16px' }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>Abnormality in this flow</div>
            <AbnormalityTable ids={flowAb} names={names} />
          </div>
        </>
      ) : (
        <div style={{ ...card, padding: '12px 16px' }}><AbnormalityTable ids={null} names={names} /></div>
      )}
    </div>
  );
}
