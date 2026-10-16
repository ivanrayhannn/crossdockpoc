import { useState } from 'react';
import { card, th, td } from '../asnCrossdock/styles';

/* Simulation of a customer order cancelled in G-TOPAS (H0253 order status 2) after part of it is already in a submitted ASN.
 * Part PART-X, 6 pcs/case. All data is illustrative. */

type Lane = 'sup' | 'ds' | 'gt' | 'sys';
type Level = 'ok' | 'warn' | 'err';

interface Order { co: string; dt: string; dest: string; qty: number; st7: number; st2: number; hold: string; inAsn: number; po: string; bad?: boolean }
interface Po { po: string; dt: string; qty: number; mapped: number }
interface Instr { co: string; dest: string; qty: number; po: string; asn: string }
interface Recv { cs: string; label: string; qty: number; alloc: string; bad?: boolean; good?: boolean }
interface Step { lane: Lane; title: string; text: string; orders: Order[]; pos: Po[]; instr: Instr[]; recv: Recv[]; flags: [Level, string][] }

const LANE: Record<Lane, { label: string; bg: string }> = {
  sup: { label: 'Supplier', bg: '#fff2cc' },
  ds: { label: 'D/S team', bg: '#fce4d6' },
  gt: { label: 'G-TOPAS (source H0253)', bg: '#e2efda' },
  sys: { label: 'NSP backend', bg: '#d9e1f2' },
};

const A0: Order = { co: 'CO-A', dt: '13-Oct', dest: 'VN · Vietnam', qty: 24, st7: 24, st2: 0, hold: 'N', inAsn: 0, po: 'PO-1 (24)' };
const B0: Order = { co: 'CO-B', dt: '14-Oct', dest: 'TH · Thailand', qty: 12, st7: 12, st2: 0, hold: 'N', inAsn: 0, po: 'PO-2 (12)' };
const C0: Order = { co: 'CO-C', dt: '14-Oct', dest: 'PH · Philippines', qty: 6, st7: 6, st2: 0, hold: 'N', inAsn: 0, po: 'PO-2 (6)' };
const D0: Order = { co: 'CO-D', dt: '15-Oct', dest: 'VN · Vietnam', qty: 6, st7: 6, st2: 0, hold: 'N', inAsn: 0, po: '— (no PO yet)' };
const P1: Po = { po: 'PO-1', dt: '14-Oct', qty: 24, mapped: 24 };
const P2: Po = { po: 'PO-2', dt: '15-Oct', qty: 18, mapped: 18 };

const I_A6: Instr = { co: 'CO-A', dest: 'VN', qty: 6, po: 'PO-1', asn: 'ASN-001 · Case 1' };
const I_A18: Instr = { co: 'CO-A', dest: 'VN', qty: 18, po: 'PO-1', asn: '— (next rit)' };
const I_B: Instr = { co: 'CO-B', dest: 'TH', qty: 12, po: 'PO-2', asn: '—' };
const I_C: Instr = { co: 'CO-C', dest: 'PH', qty: 6, po: 'PO-2', asn: '—' };

const S1: Step = {
  lane: 'sys', title: 'Start: orders mapped to PO',
  text: 'PART-X, 6 pcs/case. CO-A (24 pcs, Vietnam) is mapped to PO-1 (24 pcs). CO-B and CO-C are mapped to PO-2. CO-D has no PO yet.',
  orders: [A0, B0, C0, D0], pos: [P1, P2], instr: [I_A6, I_A18, I_B, I_C], recv: [], flags: [['ok', 'All orders mapped FIFO. No issue.']],
};
const A_ASN: Order = { ...A0, inAsn: 6 };
const S2: Step = {
  lane: 'sup', title: 'ASN submitted for 6 pcs of CO-A',
  text: 'The supplier submits ASN-001 with Case 1 (6 pcs, label Vietnam / CO-A). The other 18 pcs of CO-A are still mapped and wait for the next rit. Case 1 is packed and shipped.',
  orders: [A_ASN, B0, C0, D0], pos: [P1, P2], instr: [I_A6, I_A18, I_B, I_C], recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
  flags: [['ok', 'ASN-001 Created (TB_R_DAILY_ORDER_MANIFEST / PART). ASN cannot be cancelled in NSP.']],
};

const SCENARIOS: { key: string; name: string; tag: Level; summary: string; steps: Step[] }[] = [
  {
    key: 'a', name: 'A · Cancel 24 without control (current risk)', tag: 'err',
    summary: 'G-TOPAS cancels the whole 24 pcs although 6 pcs are already in an ASN. The shipped case has no order any more.',
    steps: [S1, S2,
      {
        lane: 'gt', title: 'G-TOPAS cancels CO-A 24 pcs (status 2)',
        text: 'The cancel is done in the source system. CO-A is not on hold in NSP and nobody checked the qty already in the ASN.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, bad: true }, B0, C0, D0], pos: [P1, P2], instr: [I_A6, I_A18, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
        flags: [['err', 'Cancel qty 24 > qty not yet in ASN 18. 6 pcs are already shipped for this order.']],
      },
      {
        lane: 'sys', title: 'X10 sync: NSP takes status 2',
        text: 'NSP releases the 18 pcs still mapped (rows deleted from TB_R_INSTRUCTION, MAPPED_QTY of PO-1 back to 6). The next Search pre-maps the free 18 pcs of PO-1 FIFO: CO-D (Vietnam) 6 pcs.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, bad: true }, B0, C0, { ...D0, po: 'PO-1 (6)' }], pos: [{ ...P1, mapped: 12 }, P2], instr: [I_A6, I_B, I_C, { co: 'CO-D', dest: 'VN', qty: 6, po: 'PO-1', asn: '—' }],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
        flags: [['warn', 'ASN-001 (6 pcs) stays, but its order is cancelled. No alert in NSP.']],
      },
      {
        lane: 'gt', title: 'Case 1 received in G-TOPAS',
        text: 'The 6 pcs arrive. CO-A is fully cancelled, so G-TOPAS does not auto allocate them: they become stock without an order.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, bad: true }, B0, C0, { ...D0, po: 'PO-1 (6)' }], pos: [{ ...P1, mapped: 12 }, P2], instr: [I_A6, I_B, I_C, { co: 'CO-D', dest: 'VN', qty: 6, po: 'PO-1', asn: '—' }],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'Not allocated (no order)', bad: true }],
        flags: [['err', 'Orphan stock: 6 pcs with label Vietnam / CO-A and no order.']],
      },
      {
        lane: 'ds', title: 'Manual allocation to the next order (CO-B, Thailand)',
        text: 'The 6 pcs are allocated to the next open order of PART-X by FIFO: CO-B (Thailand). But CO-B is also mapped to PO-2 (12 pcs) in NSP, so it will get 12 more pcs from the supplier.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, bad: true }, { ...B0, st7: 6, po: 'PO-2 (12)', bad: true }, C0, { ...D0, po: 'PO-1 (6)' }], pos: [{ ...P1, mapped: 12 }, P2], instr: [I_A6, I_B, I_C, { co: 'CO-D', dest: 'VN', qty: 6, po: 'PO-1', asn: '—' }],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'CO-B · Thailand', bad: true }],
        flags: [
          ['err', 'Label mismatch: case labelled Vietnam goes to a Thailand order (re-label / re-pack needed).'],
          ['err', 'Over-supply: CO-B needs 12, gets 6 (Case 1) + 12 (PO-2) = 18 if the ASN of CO-B is made before the next X10 sync.'],
          ['warn', 'The orders below CO-B shift: their allocation no longer follows the cases that were packed for them.'],
        ],
      },
    ],
  },
  {
    key: 'b', name: 'B · Cancel only the qty not yet in ASN (proposal: prevention)', tag: 'ok',
    summary: 'Rule: cancel qty ≤ order qty − qty in ASN. D/S checks NSP, holds the remaining 18 pcs, and G-TOPAS cancels 18 pcs only.',
    steps: [S1, S2,
      {
        lane: 'ds', title: 'D/S checks NSP before the cancel and holds the rest',
        text: 'NSP shows per customer order: qty in ASN 6, can be cancelled 18. D/S holds the 18 pcs that are not in an ASN (HOLD_FLAG = Y). Their rows are deleted from TB_R_INSTRUCTION and PO-1 has 18 pcs free again.',
        orders: [{ ...A_ASN, hold: 'Y (18)', po: 'PO-1 (6)' }, B0, C0, D0], pos: [{ ...P1, mapped: 6 }, P2], instr: [I_A6, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
        flags: [['ok', 'Max cancel qty for CO-A = 24 − 6 = 18.']],
      },
      {
        lane: 'gt', title: 'G-TOPAS partial cancel: 18 pcs (status 2)',
        text: 'Only the held 18 pcs are cancelled. CO-A keeps 6 pcs in status 7, exactly the qty in ASN-001.',
        orders: [{ ...A_ASN, st7: 6, st2: 18, hold: 'Y (18)', po: 'PO-1 (6)' }, B0, C0, D0], pos: [{ ...P1, mapped: 6 }, P2], instr: [I_A6, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
        flags: [['ok', 'Cancel qty 18 = qty on hold. Consistent.']],
      },
      {
        lane: 'sys', title: 'X10 sync and next Search',
        text: 'NSP takes the status 2 qty; no conflict. The free 18 pcs of PO-1 are pre-mapped FIFO to the next order: CO-D (Vietnam) 6 pcs; 12 pcs of PO-1 stay open.',
        orders: [{ ...A_ASN, st7: 6, st2: 18, hold: 'Y (18)', po: 'PO-1 (6)' }, B0, C0, { ...D0, po: 'PO-1 (6)' }], pos: [{ ...P1, mapped: 12 }, P2], instr: [I_A6, I_B, I_C, { co: 'CO-D', dest: 'VN', qty: 6, po: 'PO-1', asn: '—' }],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
        flags: [['ok', 'No cancel conflict.']],
      },
      {
        lane: 'gt', title: 'Case 1 received in G-TOPAS',
        text: 'CO-A still has 6 pcs open, so G-TOPAS auto allocates Case 1 to CO-A. Label and destination match.',
        orders: [{ ...A_ASN, st7: 6, st2: 18, hold: 'Y (18)', po: 'PO-1 (6)' }, B0, C0, { ...D0, po: 'PO-1 (6)' }], pos: [{ ...P1, mapped: 12 }, P2], instr: [I_A6, I_B, I_C, { co: 'CO-D', dest: 'VN', qty: 6, po: 'PO-1', asn: '—' }],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'CO-A · Vietnam (auto)', good: true }],
        flags: [['ok', 'Case 1 goes to its own order. Orders below are not affected.']],
      },
    ],
  },
  {
    key: 'c', name: 'C · Cancel 24 still happens (proposal: detection in X10)', tag: 'warn',
    summary: 'Safety net when the rule is not followed: X10 detects the cancel conflict, releases the unshipped mapping and alerts D/S to handle the shipped case.',
    steps: [S1, S2,
      {
        lane: 'gt', title: 'G-TOPAS cancels CO-A 24 pcs (status 2)',
        text: 'The rule of scenario B is not followed: the whole order is cancelled.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, bad: true }, B0, C0, D0], pos: [P1, P2], instr: [I_A6, I_A18, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit' }],
        flags: [['err', 'Cancel qty 24 > qty not yet in ASN 18.']],
      },
      {
        lane: 'sys', title: 'X10 sync detects "cancel conflict"',
        text: 'X10 compares the status 2 qty with the rows of TB_R_INSTRUCTION that already have an ASN_NO. 6 pcs are in ASN-001 → cancel conflict: log + exception list for D/S. The 18 pcs not yet in ASN are released; the ASN is not changed.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, hold: 'Conflict', bad: true }, B0, C0, D0], pos: [{ ...P1, po: 'PO-1 (blocked)', mapped: 6 }, P2], instr: [I_A6, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'In transit · flagged' }],
        flags: [
          ['warn', 'Log: "Cancel conflict CO-A PART-X: 24 pcs cancelled, 6 pcs already in ASN-001 Case 1."'],
          ['ok', 'Free PO qty (18) is not given to other orders until D/S decides on Case 1 (avoids over-supply).'],
        ],
      },
      {
        lane: 'ds', title: 'D/S handles Case 1 at receiving',
        text: '(a) An open order with the same destination exists: CO-D (Vietnam, 6 pcs). D/S allocates Case 1 to CO-D in G-TOPAS; the label destination stays valid. (b) If none exists: Case 1 goes to normal warehouse stock.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, hold: 'Conflict' }, B0, C0, { ...D0, st7: 0, po: 'Filled by Case 1' }], pos: [{ ...P1, po: 'PO-1 (blocked)', mapped: 6 }, P2], instr: [I_A6, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'CO-D · Vietnam (manual)', good: true }],
        flags: [['ok', 'Same destination: no re-label of destination. CO-D status 7 qty becomes 0 at the next X10 sync, so NSP does not map it again.'], ['warn', 'Customer Order No on the label differs (CO-A → CO-D): confirm whether re-label is needed.']],
      },
      {
        lane: 'sys', title: 'Conflict closed, PO qty free again',
        text: 'After D/S closes the conflict, the 18 free pcs of PO-1 can be pre-mapped again FIFO to the next orders.',
        orders: [{ ...A_ASN, st7: 0, st2: 24, hold: 'Closed' }, B0, C0, { ...D0, st7: 0, po: 'Filled by Case 1' }], pos: [{ ...P1, mapped: 6 }, P2], instr: [I_A6, I_B, I_C],
        recv: [{ cs: 'Case 1', label: 'VN · CO-A', qty: 6, alloc: 'CO-D · Vietnam (manual)', good: true }],
        flags: [['ok', 'No over-supply; orders below CO-D keep their FIFO mapping.']],
      },
    ],
  },
];

const LEVEL: Record<Level, { bg: string; fg: string; icon: string }> = {
  ok: { bg: '#e2efda', fg: '#1e5e20', icon: '✓' },
  warn: { bg: '#fff2cc', fg: '#7a5a00', icon: '!' },
  err: { bg: '#f8d7da', fg: '#842029', icon: '✕' },
};

const BAD = '#fbe3e4';
const GOOD = '#e6f4ea';

function Table({ title, cols, rows }: { title: string; cols: string[]; rows: { cells: (string | number)[]; bg?: string }[] }) {
  return (
    <div style={{ ...card, overflow: 'hidden' }}>
      <div style={{ padding: '9px 12px', fontSize: 12.5, fontWeight: 600 }}>{title}</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead><tr>{cols.map((c) => <th key={c} style={th}>{c}</th>)}</tr></thead>
          <tbody>
            {rows.length ? rows.map((r, i) => (
              <tr key={i} style={{ background: r.bg }}>{r.cells.map((c, j) => <td key={j} style={td}>{c}</td>)}</tr>
            )) : <tr><td style={{ ...td, color: 'var(--color-neutral-700)' }} colSpan={cols.length}>—</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** Step-by-step simulation: customer order cancelled in G-TOPAS after part of it is in a submitted ASN. */
export function CancelOrderSimulationPage() {
  const [sc, setSc] = useState(0);
  const [st, setSt] = useState(0);
  const scen = SCENARIOS[sc];
  const step = scen.steps[st];
  const last = scen.steps.length - 1;

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>Cancel Order Simulation</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          Customer order CO-A (24 pcs) is cancelled in G-TOPAS (H0253 order status 2) after 6 pcs are already in a submitted ASN. NSP cannot cancel an ASN. Compare the current risk with the proposed prevention and detection. Data is illustrative (PART-X, 6 pcs/case).
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {SCENARIOS.map((s, i) => (
          <button key={s.key} className={`btn ${i === sc ? 'btn-primary' : 'btn-secondary'}`} onClick={() => { setSc(i); setSt(0); }}>
            <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 4, background: LEVEL[s.tag].fg, marginRight: 6 }} />{s.name}
          </button>
        ))}
      </div>

      <div style={{ ...card, padding: '12px 16px' }}>
        <div style={{ fontSize: 12.5, marginBottom: 10 }}>{scen.summary}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          {scen.steps.map((s, i) => (
            <button key={i} onClick={() => setSt(i)} title={s.title}
              style={{ border: '1px solid var(--color-neutral-400)', borderRadius: 14, padding: '3px 10px', fontSize: 11.5, cursor: 'pointer',
                background: i === st ? 'var(--color-primary, #0d6efd)' : i < st ? 'var(--color-surface)' : 'transparent', color: i === st ? '#fff' : 'inherit' }}>
              {i + 1}. {s.title}
            </button>
          ))}
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
            <button className="btn btn-secondary" disabled={st === 0} onClick={() => setSt(st - 1)}>Prev</button>
            <button className="btn btn-primary" disabled={st === last} onClick={() => setSt(st + 1)}>Next</button>
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 3fr) minmax(0, 2fr)', gap: 14 }}>
        <div style={{ ...card, padding: '12px 16px' }}>
          <div style={{ display: 'inline-block', fontSize: 11, padding: '2px 8px', borderRadius: 4, background: LANE[step.lane].bg, marginBottom: 6 }}>{LANE[step.lane].label}</div>
          <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Step {st + 1} · {step.title}</div>
          <div style={{ fontSize: 12.5, lineHeight: 1.6 }}>{step.text}</div>
        </div>
        <div style={{ ...card, padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ fontSize: 12.5, fontWeight: 600 }}>Check</div>
          {step.flags.map(([lv, t], i) => (
            <div key={i} style={{ display: 'flex', gap: 8, fontSize: 12, padding: '6px 8px', borderRadius: 6, background: LEVEL[lv].bg, color: LEVEL[lv].fg }}>
              <b>{LEVEL[lv].icon}</b><span>{t}</span>
            </div>
          ))}
        </div>
      </div>

      <Table title="Customer orders – TB_R_H0253_ORDER_CONTROL_PRE (PART-X, FIFO)"
        cols={['Customer Order', 'Order Date', 'Destination', 'Order Qty', 'Status 7 Qty', 'Status 2 Qty (cancel)', 'Hold Flag', 'Qty in ASN', 'Mapped PO']}
        rows={step.orders.map((o) => ({ cells: [o.co, o.dt, o.dest, o.qty, o.st7, o.st2, o.hold, o.inAsn, o.po], bg: o.bad ? BAD : undefined }))} />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 14 }}>
        <Table title="PO – Pra Daily Order + TB_R_PRA_DAILY_ORDER_MAPPED"
          cols={['PO', 'PO Date', 'PO Qty', 'Mapped Qty', 'Open Qty']}
          rows={step.pos.map((p) => ({ cells: [p.po, p.dt, p.qty, p.mapped, p.qty - p.mapped] }))} />
        <Table title="TB_R_INSTRUCTION (mapping)"
          cols={['Customer Order', 'Dest', 'Qty', 'PO', 'ASN / Case']}
          rows={step.instr.map((r) => ({ cells: [r.co, r.dest, r.qty, r.po, r.asn] }))} />
        <Table title="Shipment / receiving in G-TOPAS"
          cols={['Case', 'Label', 'Qty', 'Allocated to']}
          rows={step.recv.map((r) => ({ cells: [r.cs, r.label, r.qty, r.alloc], bg: r.bad ? BAD : r.good ? GOOD : undefined }))} />
      </div>

      <div style={{ ...card, padding: '12px 16px', fontSize: 12.5, lineHeight: 1.6 }}>
        <b>Proposal to confirm</b>
        <ol style={{ margin: '4px 0 0', paddingLeft: 18 }}>
          <li>Rule (SOP): cancel qty ≤ order qty − qty already in ASN; D/S holds the rest in NSP before the cancel in G-TOPAS (scenario B).</li>
          <li>NSP shows "qty in ASN / can be cancelled" per customer order for D/S.</li>
          <li>X10 detects a cancel conflict (status 2 qty &gt; qty not in ASN): log + exception list, release the unshipped mapping, keep the ASN, hold the free PO qty until D/S closes the conflict (scenario C).</li>
          <li>Shipped case without order: allocate manually to an open order with the same destination, otherwise move to warehouse stock.</li>
          <li>Open: can G-TOPAS cancel partially? Does the case label carry the Customer Order No?</li>
        </ol>
      </div>
    </div>
  );
}
