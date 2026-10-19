import { useState } from 'react';
import { card, th, td } from '../asnCrossdock/styles';

/* Simulation of the H0253 scenarios (skenario_h0253.xlsx): normal (7 -> 6), partial cancel (split serial), full cancel,
 * and the abnormality "cancel of qty already in an ASN" detected by XD11 as CONFLICT.
 * Supplier System keeps one replicate table (upsert by INTF_UPDATE_DT); job chain XD12 -> XD11 -> XD08. */

type Lane = 'sup' | 'ds' | 'gt' | 'sys';
type Level = 'ok' | 'warn' | 'err';
type Status = '7' | '6' | '2';

interface SrcRow { serial: string; status: Status; qty: number; upd: string; changed?: boolean }
interface RepRow { serial: string; status: Status; qty: number; hold: 'Y' | 'N'; mapped: 'Y' | 'N'; cancel: '-' | 'P' | 'D'; changed?: boolean }
interface Instr { serial: string; qty: number; po: string; asn: string; deleted?: boolean }
interface Fig { cancel: number; valid: number; inAsn: number; open: number; released: number; poMapped: number; result: '' | 'CANCELLED' | 'CONFLICT' }
interface Recv { what: string; qty: number; alloc: string; bad?: boolean; good?: boolean }
interface Step { lane: Lane; date: string; title: string; text: string; src: SrcRow[]; rep: RepRow[]; instr: Instr[]; fig?: Fig; recv?: Recv[]; flags: [Level, string][] }

const LANE: Record<Lane, { label: string; bg: string }> = {
  sup: { label: 'Supplier', bg: '#fff2cc' },
  ds: { label: 'D/S team', bg: '#fce4d6' },
  gt: { label: 'T-System (source H0253)', bg: '#e2efda' },
  sys: { label: 'Supplier System batch', bg: '#d9e1f2' },
};

const A = '0000001';
const B = '0000002 (new)';

// 14-Oct: the line arrives with status 7 and is inserted by XD08
const SRC14: SrcRow[] = [{ serial: A, status: '7', qty: 8, upd: '14-Oct 03:30' }];
const REP14: RepRow[] = [{ serial: A, status: '7', qty: 8, hold: 'N', mapped: 'N', cancel: '-', changed: true }];
const START: Step = {
  lane: 'sys', date: '14-Oct', title: 'XD08 inserts the new line (status 7)',
  text: 'T-System has the crossdock line ID1H4571 / 52119BZV60, 8 pcs, status 7. XD08 takes the rows changed since the last run (INTF_UPDATE_DT > watermark) and inserts the new key; HOLD_FLAG / PO_MAPPED_FLAG = N, CANCEL_STATUS = -.',
  src: SRC14, rep: REP14, instr: [], flags: [['ok', 'Upsert per unique key (incl. SERIAL_NO). Nothing is deleted, so the Supplier System columns are never lost.']],
};
const REP14_M: RepRow[] = [{ serial: A, status: '7', qty: 8, hold: 'N', mapped: 'Y', cancel: '-' }];

const SCENARIOS: { key: string; name: string; tag: Level; summary: string; steps: Step[] }[] = [
  {
    key: '1', name: '1 · Normal (7 → 6)', tag: 'ok',
    summary: 'Skenario #1: the line is shipped with an ASN and received; T-System updates the same row from status 7 to 6.',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Search, Create ASN and Submit',
        text: 'XD09 pre-maps the 8 pcs to PO-1; Create ASN maps them (TB_R_INSTRUCTION) and Submit creates ASN-001. The existing ASN feedback informs T-System.',
        src: SRC14, rep: REP14_M, instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        flags: [['ok', 'Line in ASN-001: T-System blocks a cancel of this line (existing ASN feedback).']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'Received in T-System: same row status 6',
        text: 'The 8 pcs arrive and are allocated to the order. T-System updates the same row: status 6, qty 8, new INTF_UPDATE_DT.',
        src: [{ serial: A, status: '6', qty: 8, upd: '15-Oct 03:30', changed: true }], rep: REP14_M, instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        flags: [['ok', 'Normal flow; no cancel.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'Job chain XD12 → XD11 → XD08',
        text: 'XD12: no status 2 row. XD11: nothing to do. XD08 updates row 0000001 to status 6 (Supplier System columns kept). The line is no longer taken by XD09 (status 7 only).',
        src: [{ serial: A, status: '6', qty: 8, upd: '15-Oct 03:30' }], rep: [{ serial: A, status: '6', qty: 8, hold: 'N', mapped: 'Y', cancel: '-', changed: true }],
        instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        flags: [['ok', 'Status 6 is kept for tracking only.']],
      },
    ],
  },
  {
    key: '2', name: '2 · Partial cancel (split serial)', tag: 'ok',
    summary: 'Skenario #2: 2 of 8 pcs are cancelled before any ASN; T-System splits the line into a new serial (2 pcs status 2) and keeps 6 pcs status 7.',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Search only (pre-mapping, no Create ASN yet)',
        text: 'XD09 pre-maps the 8 pcs to PO-1 in the temporary table. Nothing is saved yet (TB_R_INSTRUCTION empty).',
        src: SRC14, rep: REP14, instr: [], flags: [['ok', 'Pre-mapping only.']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'T-System partial cancel: serial split',
        text: 'Row 0000001 becomes status 7 qty 6 and a new serial row is created with status 2 qty 2 (ORIGINAL_SHIPPING_QTY 8 on both). Cancel without hold flag is allowed.',
        src: [{ serial: A, status: '7', qty: 6, upd: '15-Oct 03:30', changed: true }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30', changed: true }],
        rep: REP14, instr: [], flags: [['ok', 'Hold flag N: a cancel is allowed with or without hold.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD12 upserts the line (status 2 + other changed rows)',
        text: 'The line exists in Supplier System, so XD12 inserts the new serial (status 2, CANCEL_STATUS P) and also updates serial 0000001 (qty 8 → 6), so XD11 sees the complete line.',
        src: [{ serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ serial: A, status: '7', qty: 6, hold: 'N', mapped: 'N', cancel: '-', changed: true }, { serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', cancel: 'P', changed: true }],
        instr: [], flags: [['ok', 'CANCEL_STATUS P = to be processed by XD11.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD11: CANCELLED',
        text: 'Line figures: CANCEL 2, VALID (status 7 + 6) 6, in ASN 0, open mapping 0 → CANCELLED. Serial 0000002 → CANCEL_STATUS D. XD08 runs next; the next Search of XD09 pre-maps 6 pcs.',
        src: [{ serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ serial: A, status: '7', qty: 6, hold: 'N', mapped: 'N', cancel: '-' }, { serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', cancel: 'D', changed: true }],
        instr: [], fig: { cancel: 2, valid: 6, inAsn: 0, open: 0, released: 0, poMapped: 0, result: 'CANCELLED' },
        flags: [['ok', 'Only 6 pcs remain for the ASN.']],
      },
    ],
  },
  {
    key: '3', name: '3 · Full cancel (open mapping released)', tag: 'ok',
    summary: 'Skenario #3: the whole 8 pcs are cancelled; the same row changes to status 2. The supplier had already pressed Create ASN but not Submit.',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Create ASN done, not submitted',
        text: 'Create ASN mapped the 8 pcs to PO-1 (TB_R_INSTRUCTION without ASN No; PO-1 MAPPED_QTY 8). The Case List is left open without Submit.',
        src: SRC14, rep: REP14_M, instr: [{ serial: A, qty: 8, po: 'PO-1', asn: '— (not submitted)' }],
        flags: [['warn', 'Open mapping: not yet in an ASN.']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'T-System full cancel: same row status 2',
        text: 'Row 0000001 changes to status 2, qty 8.',
        src: [{ serial: A, status: '2', qty: 8, upd: '15-Oct 03:30', changed: true }], rep: REP14_M, instr: [{ serial: A, qty: 8, po: 'PO-1', asn: '— (not submitted)' }],
        flags: [['ok', 'Not in an ASN: the cancel is allowed.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD12 updates the row (CANCEL_STATUS P)',
        text: 'XD12 updates row 0000001 to status 2 and sets CANCEL_STATUS P. HOLD_FLAG / PO_MAPPED_FLAG are not changed.',
        src: [{ serial: A, status: '2', qty: 8, upd: '15-Oct 03:30' }], rep: [{ serial: A, status: '2', qty: 8, hold: 'N', mapped: 'Y', cancel: 'P', changed: true }],
        instr: [{ serial: A, qty: 8, po: 'PO-1', asn: '— (not submitted)' }], flags: [['ok', 'Line ready for XD11.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD11: release the open mapping, CANCELLED',
        text: 'Line figures: CANCEL 8, VALID 0, in ASN 0, open 8. The open mapping row is deleted, PO-1 MAPPED_QTY 8 → 0, PO_MAPPED_FLAG → N, CANCEL_STATUS → D. PO-1 is free for the next orders (XD09 FIFO).',
        src: [{ serial: A, status: '2', qty: 8, upd: '15-Oct 03:30' }], rep: [{ serial: A, status: '2', qty: 8, hold: 'N', mapped: 'N', cancel: 'D', changed: true }],
        instr: [{ serial: A, qty: 8, po: 'PO-1', asn: '— (not submitted)', deleted: true }],
        fig: { cancel: 8, valid: 0, inAsn: 0, open: 8, released: 8, poMapped: 0, result: 'CANCELLED' },
        flags: [['ok', 'Released 8 pcs.'], ['warn', 'The Case List still open can no longer be submitted (submit fails, the supplier creates the ASN again).']],
      },
    ],
  },
  {
    key: '4', name: '4 · Abnormality: cancel after ASN (CONFLICT)', tag: 'err',
    summary: 'Not allowed: the line is already in a submitted ASN. Normally blocked by the existing ASN feedback and the SOP; if it still happens, XD11 detects a CONFLICT.',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Create ASN and Submit: ASN-001 (8 pcs)',
        text: 'The 8 pcs are in ASN-001 and shipped. The existing ASN feedback informs T-System.',
        src: SRC14, rep: REP14_M, instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        flags: [['ok', 'Line in ASN: a cancel should be blocked.']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'T-System partial cancel 2 pcs anyway',
        text: 'Abnormality: the SOP was not followed (and the block did not apply). T-System splits the line: 0000001 status 7 qty 6, new serial status 2 qty 2.',
        src: [{ serial: A, status: '7', qty: 6, upd: '15-Oct 03:30', changed: true }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30', changed: true }],
        rep: REP14_M, instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        flags: [['err', 'Cancel of qty already in a submitted ASN.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD12 upserts the line',
        text: 'XD12 updates serial 0000001 (qty 6) and inserts the new serial with status 2, CANCEL_STATUS P.',
        src: [{ serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', cancel: '-', changed: true }, { serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', cancel: 'P', changed: true }],
        instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }], flags: [['ok', 'Line ready for XD11.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD11: CONFLICT (2 pcs)',
        text: 'Line figures: CANCEL 2, VALID 6, in ASN 8, open 0 → in ASN > valid → CONFLICT 2 pcs. ASN-001 is not changed (an ASN cannot be cancelled). Result CONFLICT in TB_R_CROSSDOCK_CANCEL_RESULT and LOG4 for the D/S team.',
        src: [{ serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', cancel: '-' }, { serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', cancel: 'D', changed: true }],
        instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        fig: { cancel: 2, valid: 6, inAsn: 8, open: 0, released: 0, poMapped: 8, result: 'CONFLICT' },
        flags: [['err', 'Log: "Cancel conflict ID1H4571 52119BZV60: 2 pcs of ASN-001 have no order after the cancel."']],
      },
      {
        lane: 'ds', date: '16-Oct', title: 'Receiving: 2 pcs without order',
        text: 'ASN-001 arrives with 8 pcs. 6 pcs are allocated to the order (row 0000001 → status 6, taken by XD08). The D/S team handles the other 2 pcs: allocate them to an open order (same destination 9722D88 or another destination), otherwise move them to warehouse stock.',
        src: [{ serial: A, status: '6', qty: 6, upd: '16-Oct 03:30', changed: true }, { serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ serial: A, status: '6', qty: 6, hold: 'N', mapped: 'Y', cancel: '-', changed: true }, { serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', cancel: 'D' }],
        instr: [{ serial: A, qty: 8, po: 'PO-1', asn: 'ASN-001' }],
        recv: [{ what: 'ASN-001 · 6 pcs', qty: 6, alloc: 'ID1H4571 (status 6)', good: true },
               { what: 'ASN-001 · 2 pcs', qty: 2, alloc: 'No order → D/S: open order (any destination) or warehouse stock', bad: true }],
        flags: [['warn', 'Manual handling by the D/S team (abnormality).'], ['ok', 'Prevention: existing ASN feedback to T-System + SOP of the D/S team.']],
      },
    ],
  },
];

const LEVEL: Record<Level, { bg: string; fg: string; icon: string }> = {
  ok: { bg: '#e2efda', fg: '#1e5e20', icon: '✓' },
  warn: { bg: '#fff2cc', fg: '#7a5a00', icon: '!' },
  err: { bg: '#f8d7da', fg: '#842029', icon: '✕' },
};
const CHG = '#fff7d6';
const BAD = '#fbe3e4';
const GOOD = '#e6f4ea';
const STATUS: Record<Status, string> = { '7': '7 Cross Dock', '6': '6 Received', '2': '2 Cancel' };

function Table({ title, cols, rows, empty = '—' }: { title: string; cols: string[]; rows: { cells: (string | number)[]; bg?: string; strike?: boolean }[]; empty?: string }) {
  return (
    <div style={{ ...card, overflow: 'hidden' }}>
      <div style={{ padding: '9px 12px', fontSize: 12.5, fontWeight: 600 }}>{title}</div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead><tr>{cols.map((c) => <th key={c} style={th}>{c}</th>)}</tr></thead>
          <tbody>
            {rows.length ? rows.map((r, i) => (
              <tr key={i} style={{ background: r.bg, textDecoration: r.strike ? 'line-through' : undefined }}>{r.cells.map((c, j) => <td key={j} style={td}>{c}</td>)}</tr>
            )) : <tr><td style={{ ...td, color: 'var(--color-neutral-700)' }} colSpan={cols.length}>{empty}</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/** Step-by-step simulation of the H0253 scenarios and the cancel handling of XD12 / XD11 / XD08. */
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
          H0253 scenarios (skenario_h0253.xlsx): the source table in T-System is insert / update; Supplier System keeps one replicate table updated by upsert
          (rows with INTF_UPDATE_DT after the last run). Job chain XD12 (status 2) → XD11 (cancel) → XD08 (status 7 / 6). A partial cancel splits the line into a new SERIAL_NO.
        </div>
      </div>

      <div style={{ ...card, padding: '10px 14px', fontSize: 12, display: 'flex', flexWrap: 'wrap', gap: '6px 22px' }}>
        {[['Customer', '9722D10'], ['Customer Order No', 'ID1H4571'], ['Order Date / Time', '31-Aug-2026 · 201241'], ['Destination', '9722D88'],
          ['Detailed Item No', '0004'], ['Part Number', '52119BZV60'], ['Original Shipping Qty', '8 pcs']].map(([k, v]) => (
          <span key={k}><span style={{ color: 'var(--color-neutral-700)' }}>{k}: </span><b>{v}</b></span>
        ))}
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
          <div style={{ display: 'flex', gap: 6, marginBottom: 6 }}>
            <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: LANE[step.lane].bg }}>{LANE[step.lane].label}</span>
            <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: 'var(--color-surface)' }}>{step.date}</span>
          </div>
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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: 14 }}>
        <Table title="T-System H0253 (DB Surrounding, insert / update)"
          cols={['SERIAL_NO', 'ORDER_STATUS', 'ORDER_STATUS_QTY', 'INTF_UPDATE_DT']}
          rows={step.src.map((r) => ({ cells: [r.serial, STATUS[r.status], r.qty, r.upd], bg: r.changed ? CHG : undefined }))} />
        <Table title="Supplier System: TB_R_H0253_ORDER_CONTROL_PRE (upsert)"
          cols={['SERIAL_NO', 'ORDER_STATUS', 'QTY', 'HOLD_FLAG', 'PO_MAPPED_FLAG', 'CANCEL_STATUS']}
          rows={step.rep.map((r) => ({ cells: [r.serial, STATUS[r.status], r.qty, r.hold, r.mapped, r.cancel], bg: r.changed ? CHG : undefined }))} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 14 }}>
        <Table title="TB_R_INSTRUCTION (mapping)" cols={['SERIAL_NO', 'QTY', 'PO', 'ASN No']} empty="No mapping"
          rows={step.instr.map((r) => ({ cells: [r.serial, r.qty, r.po, r.asn], strike: r.deleted, bg: r.deleted ? BAD : undefined }))} />
        <Table title="XD11 line figures (all serials)" cols={['Item', 'Value']} empty="XD11 not run in this step"
          rows={step.fig ? [
            { cells: ['CANCEL_QTY (status 2, P)', step.fig.cancel] },
            { cells: ['VALID_QTY (status 7 + 6)', step.fig.valid] },
            { cells: ['QTY_IN_ASN', step.fig.inAsn] },
            { cells: ['Open mapping / released', `${step.fig.open} / ${step.fig.released}`] },
            { cells: ['PO-1 MAPPED_QTY after XD11', step.fig.poMapped] },
            { cells: ['Result', step.fig.result], bg: step.fig.result === 'CONFLICT' ? BAD : GOOD }] : []} />
        <Table title="Receiving in T-System" cols={['Goods', 'Qty', 'Allocated to']} empty="—"
          rows={(step.recv ?? []).map((r) => ({ cells: [r.what, r.qty, r.alloc], bg: r.bad ? BAD : r.good ? GOOD : undefined }))} />
      </div>

      <div style={{ ...card, padding: '12px 16px', fontSize: 12.5, lineHeight: 1.6 }}>
        <b>Rules (decided 18-Oct)</b>
        <ol style={{ margin: '4px 0 0', paddingLeft: 18 }}>
          <li>One replicate table, upsert per unique key with the rows changed since the last run (INTF_UPDATE_DT); rows with status 6 / 2 are kept for tracking.</li>
          <li>A partial cancel splits the line into a new SERIAL_NO; XD11 calculates per line (all serials).</li>
          <li>A line can be cancelled with or without hold flag Y.</li>
          <li>Qty already in an ASN cannot be cancelled: existing ASN feedback to T-System + SOP of the D/S team. If it still happens (abnormality), XD11 reports a CONFLICT; the ASN is not changed.</li>
          <li>Yellow rows = changed in this step.</li>
        </ol>
      </div>
    </div>
  );
}
