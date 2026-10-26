import { useState } from 'react';
import { card, th, td } from '../asnCrossdock/styles';

/* Simulation of the H0253 scenarios with the rules of 23-Oct: one replicate table kept by XD08 (upsert of the rows changed since the
 * last run). ORDER_STATUS keeps the value of the first replication; a later change in T-System is written to UPD_STATUS:
 * '6' received / allocated, '2' cancel. Every run of XD08 releases all drafts (Create ASN not submitted). A cancel of qty already in a
 * submitted ASN is handled by the D/S team in Change Order Number (XD11): the qty is moved to received lines of the same part. */

type Lane = 'sup' | 'ds' | 'gt' | 'sys';
type Level = 'ok' | 'warn' | 'err';
type Status = '7' | '6' | '2';

interface SrcRow { order: string; serial: string; status: Status; qty: number; upd: string; changed?: boolean }
interface RepRow { order: string; serial: string; status: Status; qty: number; hold: 'Y' | 'N'; mapped: 'Y' | 'N'; upd: '-' | '2' | '6'; changed?: boolean }
interface Instr { order: string; serial: string; qty: number; po: string; asn: string; deleted?: boolean; added?: boolean }
interface Hist { asn: string; from: string; to: string; qty: number }
interface Step { lane: Lane; date: string; title: string; text: string; src: SrcRow[]; rep: RepRow[]; instr: Instr[]; hist?: Hist[]; flags: [Level, string][] }

const LANE: Record<Lane, { label: string; bg: string }> = {
  sup: { label: 'Supplier', bg: '#fff2cc' },
  ds: { label: 'D/S team', bg: '#fce4d6' },
  gt: { label: 'T-System (source H0253)', bg: '#e2efda' },
  sys: { label: 'Supplier System batch', bg: '#d9e1f2' },
};

const O = 'ID1H4571';
const O2 = 'ID1H4580';
const A = '0000001';
const B = '0000002 (new)';
const PO = 'PO-DMY-09001';
const C5 = 'CO-14115';

// 14-Oct: the line arrives with status 7 and is inserted by XD08
const SRC14: SrcRow[] = [{ order: O, serial: A, status: '7', qty: 8, upd: '14-Oct 03:30' }];
const REP14: RepRow[] = [{ order: O, serial: A, status: '7', qty: 8, hold: 'N', mapped: 'N', upd: '-', changed: true }];
const START: Step = {
  lane: 'sys', date: '14-Oct', title: 'XD08 inserts the new line (status 7)',
  text: 'T-System has the crossdock line ID1H4571 / 52119BZV60, 8 pcs, status 7. XD08 takes the rows changed since the last run (INTF_UPDATE_DT > watermark) and inserts the new key; HOLD_FLAG / PO_MAPPED_FLAG = N, UPD_STATUS empty.',
  src: SRC14, rep: REP14, instr: [], flags: [['ok', 'Upsert per unique key (incl. SERIAL_NO). Nothing is deleted, so the Supplier System columns are never lost.']],
};
const REP14_M: RepRow[] = [{ order: O, serial: A, status: '7', qty: 8, hold: 'N', mapped: 'Y', upd: '-' }];

const SCENARIOS: { key: string; name: string; tag: Level; summary: string; steps: Step[] }[] = [
  {
    key: '1', name: '1 · Normal (received: UPD_STATUS 6)', tag: 'ok',
    summary: 'Skenario #1: the line is shipped with an ASN and received; T-System updates the same row from status 7 to 6.',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Search, Create ASN and Submit',
        text: 'XD09 pre-maps the 8 pcs to the PO; Create ASN maps them (TB_R_INSTRUCTION) and Submit creates ASN-001.',
        src: SRC14, rep: REP14_M, instr: [{ order: O, serial: A, qty: 8, po: PO, asn: 'ASN-001' }],
        flags: [['ok', 'Line in ASN-001 (TB_R_INSTRUCTION.ASN_NO).']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'Received in T-System: same row status 6',
        text: 'The 8 pcs arrive and are allocated to the order. T-System updates the same row: status 6, qty 8, new INTF_UPDATE_DT.',
        src: [{ order: O, serial: A, status: '6', qty: 8, upd: '15-Oct 03:30', changed: true }], rep: REP14_M, instr: [{ order: O, serial: A, qty: 8, po: PO, asn: 'ASN-001' }],
        flags: [['ok', 'Normal flow; no cancel.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD08: UPD_STATUS 6',
        text: 'XD08 updates the row: ORDER_STATUS stays 7 (value of the first replication), UPD_STATUS = 6. A line with UPD_STATUS is no longer taken by XD09. All drafts are released (none here).',
        src: [{ order: O, serial: A, status: '6', qty: 8, upd: '15-Oct 03:30' }], rep: [{ order: O, serial: A, status: '7', qty: 8, hold: 'N', mapped: 'Y', upd: '6', changed: true }],
        instr: [{ order: O, serial: A, qty: 8, po: PO, asn: 'ASN-001' }],
        flags: [['ok', 'UPD_STATUS 6 = received / allocated in T-System.']],
      },
    ],
  },
  {
    key: '2', name: '2 · Partial cancel before any mapping', tag: 'ok',
    summary: 'Skenario #2: 2 of 8 pcs are cancelled before Create ASN; T-System splits the line into a new serial (2 pcs status 2) and keeps 6 pcs status 7.',
    steps: [START,
      {
        lane: 'gt', date: '15-Oct', title: 'T-System partial cancel: serial split',
        text: 'Row 0000001 becomes status 7 qty 6 and a new serial row is created with status 2 qty 2.',
        src: [{ order: O, serial: A, status: '7', qty: 6, upd: '15-Oct 03:30', changed: true }, { order: O, serial: B, status: '2', qty: 2, upd: '15-Oct 03:30', changed: true }],
        rep: REP14, instr: [], flags: [['ok', 'A cancel is allowed with or without hold flag.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD08 upserts the line',
        text: 'XD08 updates serial 0000001 (qty 8 → 6) and inserts the new serial (ORDER_STATUS 2, UPD_STATUS 2). The cancelled serial is never taken by XD09; the next Search pre-maps 6 pcs.',
        src: [{ order: O, serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { order: O, serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ order: O, serial: A, status: '7', qty: 6, hold: 'N', mapped: 'N', upd: '-', changed: true }, { order: O, serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', upd: '2', changed: true }],
        instr: [], flags: [['ok', 'Cancel without mapping: nothing else to do.']],
      },
    ],
  },
  {
    key: '3', name: '3 · Cancel of a draft (Create ASN not submitted)', tag: 'warn',
    summary: 'Skenario #3: the whole 8 pcs are cancelled while the Case List of the supplier is still a draft (Create ASN done, not submitted).',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Create ASN done, not submitted',
        text: 'Create ASN mapped the 8 pcs (TB_R_INSTRUCTION without ASN No, PO MAPPED_QTY 8, PO_MAPPED_FLAG Y). The Case List is left open without Submit.',
        src: SRC14, rep: REP14_M, instr: [{ order: O, serial: A, qty: 8, po: PO, asn: '— (draft)' }],
        flags: [['warn', 'Draft: not yet in an ASN.']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'T-System full cancel: same row status 2',
        text: 'Row 0000001 changes to status 2, qty 8.',
        src: [{ order: O, serial: A, status: '2', qty: 8, upd: '15-Oct 03:30', changed: true }], rep: REP14_M, instr: [{ order: O, serial: A, qty: 8, po: PO, asn: '— (draft)' }],
        flags: [['ok', 'Not in an ASN: the cancel is allowed.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD08: UPD_STATUS 2 and all drafts released',
        text: 'XD08 sets UPD_STATUS 2 (ORDER_STATUS stays 7) and releases every draft: the TB_R_INSTRUCTION rows without ASN No are deleted, MAPPED_QTY is reduced again and PO_MAPPED_FLAG goes back to N. The cases come back in the delivery plan; the cancelled line is no longer taken.',
        src: [{ order: O, serial: A, status: '2', qty: 8, upd: '15-Oct 03:30' }], rep: [{ order: O, serial: A, status: '7', qty: 8, hold: 'N', mapped: 'N', upd: '2', changed: true }],
        instr: [{ order: O, serial: A, qty: 8, po: PO, asn: '— (draft)', deleted: true }],
        flags: [['ok', 'Draft released by XD08.'], ['warn', '[Submit ASN] of the old Case List fails (re-check); the supplier searches and creates the ASN again.']],
      },
    ],
  },
  {
    key: '4', name: '4 · Cancel after ASN → Change Order Number', tag: 'err',
    summary: 'Abnormality: the line is already in a submitted ASN and T-System cancels 2 pcs. The D/S team moves the 2 pcs to a received line of the same part in Change Order Number (XD11).',
    steps: [START,
      {
        lane: 'sup', date: '14-Oct', title: 'Create ASN and Submit: ASN-001 (8 pcs)',
        text: 'The 8 pcs are in ASN-001 and shipped.',
        src: SRC14, rep: REP14_M, instr: [{ order: O, serial: A, qty: 8, po: PO, asn: 'ASN-001' }],
        flags: [['ok', 'Line in ASN: a cancel should be blocked (existing ASN feedback + SOP).']],
      },
      {
        lane: 'gt', date: '15-Oct', title: 'T-System cancels 2 pcs and receives line ID1H4580',
        text: 'Abnormality: T-System splits the line (0000001 status 7 qty 6, new serial status 2 qty 2). At receiving the 2 pcs are allocated to the open line ID1H4580 of the same part (status 6).',
        src: [{ order: O, serial: A, status: '7', qty: 6, upd: '15-Oct 03:30', changed: true }, { order: O, serial: B, status: '2', qty: 2, upd: '15-Oct 03:30', changed: true },
          { order: O2, serial: A, status: '6', qty: 2, upd: '15-Oct 03:30', changed: true }],
        rep: [...REP14_M, { order: O2, serial: A, status: '7', qty: 2, hold: 'N', mapped: 'N', upd: '-' }], instr: [{ order: O, serial: A, qty: 8, po: PO, asn: 'ASN-001' }],
        flags: [['err', 'Cancel of qty already in a submitted ASN.']],
      },
      {
        lane: 'sys', date: '15-Oct', title: 'XD08 upserts the lines',
        text: 'XD08: ID1H4571 serial 0000001 qty 6, new serial 0000002 UPD_STATUS 2; ID1H4580 UPD_STATUS 6. The cancelled 2 pcs are in ASN-001, so they are listed in Change Order Number; ID1H4580 (UPD_STATUS 6, PO_MAPPED_FLAG N, no ASN) is a candidate.',
        src: [{ order: O, serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { order: O, serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }, { order: O2, serial: A, status: '6', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ order: O, serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '-', changed: true }, { order: O, serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', upd: '2', changed: true },
          { order: O2, serial: A, status: '7', qty: 2, hold: 'N', mapped: 'N', upd: '6', changed: true }],
        instr: [{ order: O, serial: A, qty: 8, po: PO, asn: 'ASN-001' }], flags: [['warn', 'Listed in Change Order Number (XD11) until it is moved.']],
      },
      {
        lane: 'ds', date: '15-Oct', title: 'Change Order Number: 2 pcs → ID1H4580',
        text: 'The D/S team picks ID1H4580 (same part, 2 pcs; another destination would also be allowed). The TB_R_INSTRUCTION row of ASN-001 is split: 6 pcs stay with ID1H4571, 2 pcs move to ID1H4580 (same case, same PO). ID1H4580 PO_MAPPED_FLAG = Y; the change is written to TB_H_CROSSDOCK_ORDER_CHANGE.',
        src: [{ order: O, serial: A, status: '7', qty: 6, upd: '15-Oct 03:30' }, { order: O, serial: B, status: '2', qty: 2, upd: '15-Oct 03:30' }, { order: O2, serial: A, status: '6', qty: 2, upd: '15-Oct 03:30' }],
        rep: [{ order: O, serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '-' }, { order: O, serial: B, status: '2', qty: 2, hold: 'N', mapped: 'N', upd: '2' },
          { order: O2, serial: A, status: '7', qty: 2, hold: 'N', mapped: 'Y', upd: '6', changed: true }],
        instr: [{ order: O, serial: A, qty: 6, po: PO, asn: 'ASN-001' }, { order: O2, serial: A, qty: 2, po: PO, asn: 'ASN-001', added: true }],
        hist: [{ asn: 'ASN-001', from: `${O} (0000002)`, to: O2, qty: 2 }],
        flags: [['ok', 'ASN-001 and its case are not changed physically; only the record of the order lines changes.']],
      },
    ],
  },
  {
    key: '5', name: '5 · One line in 2 ASNs → partial receipt splits the serial (simulasi_asn CO-14115)', tag: 'warn',
    summary: 'Same data as simulasi_asn_rev.xlsx: CO-14115 VN 12 pcs (order date 19-Oct) goes in ASN0006 (case 1, T0409015) and ASN0007 (case 2, T0409016). On 21-Oct ASN0006 is received: T-System splits the line into serial 0000001 6 pcs status 6 and serial 0000002 6 pcs status 7. XD08 keeps each part linked to its ASN.',
    steps: [
      {
        lane: 'sys', date: '20-Oct', title: 'XD08 inserts CO-14115 (status 7, 12 pcs)',
        text: 'Order date 19-Oct: CO-14111 TH 6 + CO-14115 VN 12 = 18 pcs → PO T0409016 (PO date 20-Oct, 18). The 20-Oct Search cuts CO-14115 into case 1 (rest of T0409015) and case 2 (T0409016).',
        src: [{ order: C5, serial: A, status: '7', qty: 12, upd: '20-Oct 03:30', changed: true }],
        rep: [{ order: C5, serial: A, status: '7', qty: 12, hold: 'N', mapped: 'N', upd: '-', changed: true }], instr: [],
        flags: [['ok', 'One line of 12 pcs = 2 supplier cases.']],
      },
      {
        lane: 'sup', date: '20-Oct', title: 'ASN0006: case 1 (6 of 12 pcs, rit 1)',
        text: 'Create ASN + Submit for case 1. The line is not complete yet: PO_MAPPED_FLAG stays N, open qty 6.',
        src: [{ order: C5, serial: A, status: '7', qty: 12, upd: '20-Oct 03:30' }],
        rep: [{ order: C5, serial: A, status: '7', qty: 12, hold: 'N', mapped: 'N', upd: '-' }],
        instr: [{ order: C5, serial: A, qty: 6, po: 'T0409015', asn: 'ASN0006', added: true }],
        flags: [['ok', 'One line may be sent in several ASNs.']],
      },
      {
        lane: 'sup', date: '20-Oct', title: 'ASN0007: case 2 (6 pcs, rit 2)',
        text: 'Create ASN + Submit for case 2. The whole line is in TB_R_INSTRUCTION: PO_MAPPED_FLAG = Y. The replicate row now has 2 ASNs (ASN0006, ASN0007).',
        src: [{ order: C5, serial: A, status: '7', qty: 12, upd: '20-Oct 03:30' }],
        rep: [{ order: C5, serial: A, status: '7', qty: 12, hold: 'N', mapped: 'Y', upd: '-', changed: true }],
        instr: [{ order: C5, serial: A, qty: 6, po: 'T0409015', asn: 'ASN0006' }, { order: C5, serial: A, qty: 6, po: 'T0409016', asn: 'ASN0007', added: true }],
        flags: [['ok', 'One H0253 row, two TB_R_INSTRUCTION rows (two ASNs).']],
      },
      {
        lane: 'gt', date: '21-Oct', title: 'ASN0006 received: T-System splits the line',
        text: 'Only ASN0006 (6 pcs) is received. T-System keeps serial 0000001 with 6 pcs status 6 and creates serial 0000002 with the remaining 6 pcs status 7.',
        src: [{ order: C5, serial: A, status: '6', qty: 6, upd: '21-Oct 03:30', changed: true }, { order: C5, serial: B, status: '7', qty: 6, upd: '21-Oct 03:30', changed: true }],
        rep: [{ order: C5, serial: A, status: '7', qty: 12, hold: 'N', mapped: 'Y', upd: '-' }],
        instr: [{ order: C5, serial: A, qty: 6, po: 'T0409015', asn: 'ASN0006' }, { order: C5, serial: A, qty: 6, po: 'T0409016', asn: 'ASN0007' }],
        flags: [['warn', 'H0253 does not carry the received ASN No: NSP assumes the ASNs are received in the order they were sent (TBC with G-System).']],
      },
      {
        lane: 'sys', date: '21-Oct', title: 'Wrong: upsert only (no re-assignment)',
        text: 'If XD08 only upserted the rows: serial 0000001 has 12 pcs in TB_R_INSTRUCTION for qty 6, and serial 0000002 looks open (6 pcs, PO_MAPPED_FLAG N) → the 21-Oct Search would map the 6 pcs again with T0409016 although they are already in ASN0007.',
        src: [{ order: C5, serial: A, status: '6', qty: 6, upd: '21-Oct 03:30' }, { order: C5, serial: B, status: '7', qty: 6, upd: '21-Oct 03:30' }],
        rep: [{ order: C5, serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '6', changed: true }, { order: C5, serial: B, status: '7', qty: 6, hold: 'N', mapped: 'N', upd: '-', changed: true }],
        instr: [{ order: C5, serial: A, qty: 6, po: 'T0409015', asn: 'ASN0006' }, { order: C5, serial: A, qty: 6, po: 'T0409016', asn: 'ASN0007' }],
        flags: [['err', 'Double mapping: the 6 pcs of ASN0007 would be mapped again.']],
      },
      {
        lane: 'sys', date: '21-Oct', title: 'XD08 serial split: each part stays with its ASN',
        text: 'XD08 links the received part (serial 0000001, status 6) to the ASN sent first (ASN0006) and the remaining part (serial 0000002, status 7) to ASN0007. Only SERIAL_NO of the ASN0007 row changes; case, PO and ASN stay. Both serials are fully in TB_R_INSTRUCTION → PO_MAPPED_FLAG Y, the Search takes nothing. LOG7.',
        src: [{ order: C5, serial: A, status: '6', qty: 6, upd: '21-Oct 03:30' }, { order: C5, serial: B, status: '7', qty: 6, upd: '21-Oct 03:30' }],
        rep: [{ order: C5, serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '6', changed: true }, { order: C5, serial: B, status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '-', changed: true }],
        instr: [{ order: C5, serial: A, qty: 6, po: 'T0409015', asn: 'ASN0006' }, { order: C5, serial: A, qty: 6, po: 'T0409016', asn: 'ASN0007', deleted: true },
          { order: C5, serial: B, qty: 6, po: 'T0409016', asn: 'ASN0007', added: true }],
        flags: [['ok', 'Each part of the line stays linked to its ASN.']],
      },
      {
        lane: 'sys', date: '22-Oct', title: 'ASN0007 received: UPD_STATUS 6',
        text: 'T-System sets serial 0000002 to status 6; XD08 writes UPD_STATUS 6. The whole line is received.',
        src: [{ order: C5, serial: A, status: '6', qty: 6, upd: '21-Oct 03:30' }, { order: C5, serial: '0000002', status: '6', qty: 6, upd: '22-Oct 03:30', changed: true }],
        rep: [{ order: C5, serial: A, status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '6' }, { order: C5, serial: '0000002', status: '7', qty: 6, hold: 'N', mapped: 'Y', upd: '6', changed: true }],
        instr: [{ order: C5, serial: A, qty: 6, po: 'T0409015', asn: 'ASN0006' }, { order: C5, serial: '0000002', qty: 6, po: 'T0409016', asn: 'ASN0007' }],
        flags: [['ok', 'Normal end (see ASN Simulation 20–22 Oct for the full data).']],
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

/** Step-by-step simulation of the H0253 scenarios: XD08 (UPD_STATUS, draft release) and Change Order Number (XD11). */
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
          H0253 scenarios (skenario_h0253.xlsx, simulasi_asn.xlsx): Supplier System keeps one replicate table updated by XD08 (rows with INTF_UPDATE_DT after the last run).
          ORDER_STATUS keeps the first value; a change in T-System is written to UPD_STATUS (6 received, 2 cancel). Every XD08 run releases the drafts; a cancel after an ASN goes to Change Order Number (XD11).
        </div>
      </div>

      <div style={{ ...card, padding: '10px 14px', fontSize: 12, display: 'flex', flexWrap: 'wrap', gap: '6px 22px' }}>
        {(scen.key === '5'
          ? [['Customer', '9715300'], ['Customer Order No', 'CO-14115'], ['Order Date', '19-Oct-2026'], ['Destination', '9715310 (VN)'],
            ['Detailed Item No', '001'], ['Part Number', 'PART-X (6 pcs/case)'], ['Order Qty', '12 pcs']]
          : [['Customer', '9722D10'], ['Customer Order No', 'ID1H4571'], ['Order Date / Time', '31-Aug-2026 · 201241'], ['Destination', '9722D88'],
            ['Detailed Item No', '0004'], ['Part Number', '52119BZV60'], ['Original Shipping Qty', '8 pcs']]).map(([k, v]) => (
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
          cols={['CUSTOMER_ORDER_NO', 'SERIAL_NO', 'ORDER_STATUS', 'ORDER_STATUS_QTY', 'INTF_UPDATE_DT']}
          rows={step.src.map((r) => ({ cells: [r.order, r.serial, STATUS[r.status], r.qty, r.upd], bg: r.changed ? CHG : undefined }))} />
        <Table title="Supplier System: TB_R_H0253_ORDER_CONTROL_PRE (XD08 upsert)"
          cols={['CUSTOMER_ORDER_NO', 'SERIAL_NO', 'ORDER_STATUS', 'QTY', 'HOLD_FLAG', 'PO_MAPPED_FLAG', 'UPD_STATUS']}
          rows={step.rep.map((r) => ({ cells: [r.order, r.serial, STATUS[r.status], r.qty, r.hold, r.mapped, r.upd], bg: r.changed ? CHG : undefined }))} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 14 }}>
        <Table title="TB_R_INSTRUCTION (draft or ASN)" cols={['CUSTOMER_ORDER_NO', 'SERIAL_NO', 'QTY', 'PO', 'ASN No']} empty="No mapping"
          rows={step.instr.map((r) => ({ cells: [r.order, r.serial, r.qty, r.po, r.asn], strike: r.deleted, bg: r.deleted ? BAD : r.added ? GOOD : undefined }))} />
        <Table title="TB_H_CROSSDOCK_ORDER_CHANGE (Change Order Number)" cols={['ASN No', 'From', 'To', 'Qty']} empty="No order number changed"
          rows={(step.hist ?? []).map((h) => ({ cells: [h.asn, h.from, h.to, h.qty], bg: GOOD }))} />
      </div>

      <div style={{ ...card, padding: '12px 16px', fontSize: 12.5, lineHeight: 1.6 }}>
        <b>Rules (decided 23-Oct)</b>
        <ol style={{ margin: '4px 0 0', paddingLeft: 18 }}>
          <li>One replicate table kept by XD08 (one batch; upsert per unique key with the rows changed since the last run). ORDER_STATUS keeps the first value; UPD_STATUS = 6 (received) or 2 (cancel) from T-System.</li>
          <li>Lines with UPD_STATUS are not taken by XD09. A cancelled line without mapping needs nothing else.</li>
          <li>Every XD08 run releases all drafts (TB_R_INSTRUCTION without ASN No); [Submit ASN] re-checks the lines of the draft.</li>
          <li>A cancel of qty in a submitted ASN is listed in Change Order Number (D/S team) until it is moved to lines of the same part with UPD_STATUS 6, PO_MAPPED_FLAG N and no ASN (oldest first; several lines and another destination allowed; the qty must add up). The TB_R_INSTRUCTION row is split when needed; the history is kept in TB_H_CROSSDOCK_ORDER_CHANGE.</li>
          <li>Yellow rows = changed in this step; green = added.</li>
        </ol>
      </div>
    </div>
  );
}
