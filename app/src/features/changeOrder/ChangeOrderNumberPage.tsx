import { useMemo, useState } from 'react';
import { DESTS, niceDate } from '../asnCrossdock/data';
import { Chip, Modal } from '../asnCrossdock/ui';
import { card, th, td } from '../asnCrossdock/styles';

/* XD11 Change Order Number (D/S team, decided 23-Oct). A customer order line of the H0253 replicate gets UPD_STATUS '2' when G-System
   cancels it (original ORDER_STATUS 2) and '6' when G-System has received / allocated it (original ORDER_STATUS 6). A cancelled line
   whose qty is already in a submitted ASN (rows of TB_R_INSTRUCTION with ASN_NO) is listed here until the D/S team moves the cancelled
   qty to other lines of the same part: UPD_STATUS '6', PO_MAPPED_FLAG 'N', not in any ASN, oldest Customer Order Date first. Several
   lines (also of another destination) can replace one cancel, as long as their qty adds up to the cancelled qty. The cancelled qty is
   taken from the last case backwards; a row of TB_R_INSTRUCTION is split when needed (record only, the physical case does not change). */

const VN = '9715310';
const TH = '9722D10';
const PH = '9811110';

interface Line {
  custOrderNo: string;
  orderDt: string;
  destCd: string;
  partNo: string;
  qty: number;
  updStatus: '2' | '6' | null;
  poMapped: boolean;
  serialNo: string;
}

/** A row of TB_R_INSTRUCTION of a submitted ASN. */
interface Slice {
  id: number;
  asnNo: string;
  caseNo: string;
  caseSeq: number;
  partNo: string;
  custOrderNo: string;
  serialNo: string;
  destCd: string;
  qty: number;
  poNo: string;
}

/** A cancelled qty in a submitted ASN (H0253 line UPD_STATUS '2' with rows in TB_R_INSTRUCTION). */
interface Open {
  key: string;
  asnNo: string;
  partNo: string;
  custOrderNo: string;
  serialNo: string;
  destCd: string;
  cancelQty: number;
}

interface History {
  at: string;
  asnNo: string;
  caseNo: string;
  partNo: string;
  fromOrder: string;
  toOrder: string;
  toDest: string;
  qty: number;
  by: string;
}

const LINES: Line[] = [
  // simulasi_asn.xlsx: CO-14104 (TH) cancelled after ASN0003 (case 3), CO-14111 (TH) received in G-System (UPD_STATUS 6)
  { custOrderNo: 'CO-14104', orderDt: '2026-10-17', destCd: TH, partNo: 'PART-X', qty: 6, updStatus: '2', poMapped: true, serialNo: '0000001' },
  { custOrderNo: 'CO-14111', orderDt: '2026-10-19', destCd: TH, partNo: 'PART-X', qty: 6, updStatus: '6', poMapped: false, serialNo: '0000001' },
  // partial cancel: CO-B 8 pcs in ASN00020 (case 1: 4, case 2: 4); G-System cancels 6 (split serial 0000002, status 2)
  { custOrderNo: 'CO-B', orderDt: '2026-10-16', destCd: VN, partNo: 'PART-Y', qty: 6, updStatus: '2', poMapped: true, serialNo: '0000002' },
  { custOrderNo: 'CO-E', orderDt: '2026-10-16', destCd: PH, partNo: 'PART-Y', qty: 4, updStatus: '6', poMapped: false, serialNo: '0000001' },
  { custOrderNo: 'CO-F', orderDt: '2026-10-17', destCd: VN, partNo: 'PART-Y', qty: 2, updStatus: '6', poMapped: false, serialNo: '0000001' },
  { custOrderNo: 'CO-G', orderDt: '2026-10-18', destCd: TH, partNo: 'PART-Y', qty: 6, updStatus: '6', poMapped: false, serialNo: '0000001' },
  // no candidate yet: CO-14120 cancelled after ASN00031, no PART-Z line received in G-System yet
  { custOrderNo: 'CO-14120', orderDt: '2026-10-18', destCd: PH, partNo: 'PART-Z', qty: 6, updStatus: '2', poMapped: true, serialNo: '0000001' },
];

const SLICES: Slice[] = [
  { id: 3, asnNo: 'ASN0003', caseNo: 'C-0003-01', caseSeq: 1, partNo: 'PART-X', custOrderNo: 'CO-14105', serialNo: '0000001', destCd: VN, qty: 6, poNo: 'PO-DMY-09012' },
  { id: 4, asnNo: 'ASN0003', caseNo: 'C-0003-02', caseSeq: 2, partNo: 'PART-X', custOrderNo: 'CO-14106', serialNo: '0000001', destCd: VN, qty: 3, poNo: 'PO-DMY-09013' },
  { id: 5, asnNo: 'ASN0003', caseNo: 'C-0003-02', caseSeq: 2, partNo: 'PART-X', custOrderNo: 'CO-14107', serialNo: '0000001', destCd: VN, qty: 3, poNo: 'PO-DMY-09013' },
  { id: 6, asnNo: 'ASN0003', caseNo: 'C-0003-03', caseSeq: 3, partNo: 'PART-X', custOrderNo: 'CO-14104', serialNo: '0000001', destCd: TH, qty: 6, poNo: 'PO-DMY-09013' },
  { id: 7, asnNo: 'ASN0003', caseNo: 'C-0003-04', caseSeq: 4, partNo: 'PART-X', custOrderNo: 'CO-14109', serialNo: '0000001', destCd: PH, qty: 6, poNo: 'PO-DMY-09013' },
  { id: 41, asnNo: 'ASN00020', caseNo: 'C-00020-01', caseSeq: 1, partNo: 'PART-Y', custOrderNo: 'CO-A', serialNo: '0000001', destCd: VN, qty: 2, poNo: 'PO-DMY-10041' },
  { id: 42, asnNo: 'ASN00020', caseNo: 'C-00020-01', caseSeq: 1, partNo: 'PART-Y', custOrderNo: 'CO-B', serialNo: '0000001', destCd: VN, qty: 4, poNo: 'PO-DMY-10041' },
  { id: 43, asnNo: 'ASN00020', caseNo: 'C-00020-02', caseSeq: 2, partNo: 'PART-Y', custOrderNo: 'CO-B', serialNo: '0000001', destCd: VN, qty: 4, poNo: 'PO-DMY-10041' },
  { id: 44, asnNo: 'ASN00020', caseNo: 'C-00020-02', caseSeq: 2, partNo: 'PART-Y', custOrderNo: 'CO-C', serialNo: '0000001', destCd: VN, qty: 2, poNo: 'PO-DMY-10041' },
  { id: 51, asnNo: 'ASN00031', caseNo: 'C-00031-01', caseSeq: 1, partNo: 'PART-Z', custOrderNo: 'CO-14120', serialNo: '0000001', destCd: PH, qty: 6, poNo: 'PO-DMY-10051' },
];

const OPEN: Open[] = [
  { key: 'ASN0003|CO-14104', asnNo: 'ASN0003', partNo: 'PART-X', custOrderNo: 'CO-14104', serialNo: '0000001', destCd: TH, cancelQty: 6 },
  { key: 'ASN00020|CO-B', asnNo: 'ASN00020', partNo: 'PART-Y', custOrderNo: 'CO-B', serialNo: '0000002', destCd: VN, cancelQty: 6 },
  { key: 'ASN00031|CO-14120', asnNo: 'ASN00031', partNo: 'PART-Z', custOrderNo: 'CO-14120', serialNo: '0000001', destCd: PH, cancelQty: 6 },
];

const dest = (d: string) => `${DESTS[d].short} (${d})`;

/** Cancelled qty taken from the last case backwards; a slice is split when only part of it is needed. */
function takeFromCases(slices: Slice[], o: Open): { caseNo: string; qty: number }[] {
  const own = slices.filter((s) => s.asnNo === o.asnNo && s.custOrderNo === o.custOrderNo).sort((a, b) => b.caseSeq - a.caseSeq);
  const out: { caseNo: string; qty: number }[] = [];
  let left = o.cancelQty;
  for (const s of own) {
    if (!left) break;
    const q = Math.min(left, s.qty);
    out.push({ caseNo: s.caseNo, qty: q });
    left -= q;
  }
  return out;
}

/** Candidates: same part, UPD_STATUS '6', PO_MAPPED_FLAG 'N', not in any ASN; oldest Customer Order Date first. */
function candidatesOf(lines: Line[], slices: Slice[], o: Open): Line[] {
  return lines
    .filter((l) => l.partNo === o.partNo && l.updStatus === '6' && !l.poMapped && !slices.some((s) => s.custOrderNo === l.custOrderNo))
    .sort((a, b) => a.orderDt.localeCompare(b.orderDt) || a.custOrderNo.localeCompare(b.custOrderNo));
}

/** Default choice: oldest candidates first until their qty adds up to the cancelled qty. */
function suggest(cands: Line[], qty: number): Record<string, number> {
  const out: Record<string, number> = {};
  let left = qty;
  for (const c of cands) {
    if (!left) break;
    if (c.qty <= left) {
      out[c.custOrderNo] = c.qty;
      left -= c.qty;
    }
  }
  return left ? {} : out;
}

/** Screen Change Order Number (D/S team): cancelled qty in submitted ASNs and its replacement by received order lines. */
export function ChangeOrderNumberPage() {
  const [lines, setLines] = useState<Line[]>(LINES);
  const [slices, setSlices] = useState<Slice[]>(SLICES);
  const [open, setOpen] = useState<Open[]>(OPEN);
  const [history, setHistory] = useState<History[]>([]);
  const [expanded, setExpanded] = useState<string | null>('ASN00020|CO-B');
  const [pick, setPick] = useState<Record<string, Record<string, number>>>({});
  const [confirm, setConfirm] = useState<Open | null>(null);
  const [nextId, setNextId] = useState(100);

  const rows = useMemo(() => open.map((o) => {
    const cands = candidatesOf(lines, slices, o);
    return { o, cands, cases: takeFromCases(slices, o), chosen: pick[o.key] ?? suggest(cands, o.cancelQty) };
  }), [open, lines, slices, pick]);

  const save = (o: Open, chosen: Record<string, number>) => {
    const parts = takeFromCases(slices, o);
    const repl = Object.entries(chosen).flatMap(([co, q]) => Array.from({ length: q }, () => co));
    let ns = [...slices];
    let id = nextId;
    const hist: History[] = [];
    let k = 0;
    for (const p of parts) {
      const src = ns.find((s) => s.asnNo === o.asnNo && s.custOrderNo === o.custOrderNo && s.caseNo === p.caseNo);
      if (!src) continue;
      // pieces of this case per replacement order
      const per: Record<string, number> = {};
      for (let i = 0; i < p.qty; i += 1) per[repl[k + i]] = (per[repl[k + i]] ?? 0) + 1;
      k += p.qty;
      ns = ns.map((s) => (s.id === src.id ? { ...s, qty: s.qty - p.qty } : s)).filter((s) => s.qty > 0);
      for (const [co, q] of Object.entries(per)) {
        const l = lines.find((x) => x.custOrderNo === co)!;
        ns.push({ ...src, id: id++, custOrderNo: co, serialNo: l.serialNo, destCd: l.destCd, qty: q });
        hist.push({ at: new Date().toTimeString().slice(0, 5), asnNo: o.asnNo, caseNo: p.caseNo, partNo: o.partNo, fromOrder: o.custOrderNo, toOrder: co, toDest: l.destCd, qty: q, by: 'D/S team' });
      }
    }
    setSlices(ns.sort((a, b) => a.asnNo.localeCompare(b.asnNo) || a.caseSeq - b.caseSeq || a.id - b.id));
    setLines(lines.map((l) => (chosen[l.custOrderNo] ? { ...l, poMapped: true } : l)));
    setOpen(open.filter((x) => x.key !== o.key));
    setHistory([...hist, ...history]);
    setNextId(id);
    setConfirm(null);
    setExpanded(null);
  };

  const confirmRow = confirm ? rows.find((r) => r.o.key === confirm.key) : undefined;

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>Change Order Number <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-neutral-600)' }}>· D/S team</span></h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          Customer orders cancelled in G-System (UPD_STATUS 2) whose qty is already in a submitted ASN. Move the cancelled qty to order lines of the same part that G-System has received (UPD_STATUS 6, PO_MAPPED_FLAG N, not in an ASN); several lines and another destination are allowed when the qty adds up.
        </div>
      </div>

      <div style={{ ...card, overflow: 'hidden' }}>
        <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--color-divider)', fontSize: 12.5 }}>
          <b>Cancelled qty in submitted ASNs</b> <span className="ax-muted">· {open.length} open · {open.filter((o) => !candidatesOf(lines, slices, o).length).length} waiting for a candidate</span>
        </div>
        {open.length === 0 ? (
          <div style={{ padding: '30px 24px', textAlign: 'center', fontSize: 13 }}>No cancelled qty in a submitted ASN.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead><tr>{['', 'ASN No', 'Part Number', 'Cancelled Customer Order', 'Destination', 'Cancelled Qty', 'Cases (from the last case)', 'Status'].map((h, i) => <th key={i} style={th}>{h}</th>)}</tr></thead>
            <tbody>
              {rows.map(({ o, cands, cases, chosen }) => {
                const total = Object.values(chosen).reduce((a, b) => a + b, 0);
                const isOpen = expanded === o.key;
                return [
                  <tr key={o.key}>
                    <td style={td}><button className="btn btn-secondary" title="Replacement" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setExpanded(isOpen ? null : o.key)}>{isOpen ? '▾' : '▸'}</button></td>
                    <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{o.asnNo}</td>
                    <td style={{ ...td, fontFamily: 'var(--font-mono)' }}>{o.partNo}</td>
                    <td style={td}>{o.custOrderNo} <span className="ax-muted">serial {o.serialNo}</span></td>
                    <td style={td}>{dest(o.destCd)}</td>
                    <td style={{ ...td, fontWeight: 600 }}>{o.cancelQty}</td>
                    <td style={td}>{cases.map((c) => `${c.caseNo}: ${c.qty}`).join(', ')}</td>
                    <td style={td}>{cands.length ? <Chip tone="warn">Candidate available</Chip> : <Chip tone="neutral">Waiting for a candidate</Chip>}</td>
                  </tr>,
                  isOpen && (
                    <tr key={`${o.key}-d`}>
                      <td colSpan={8} style={{ padding: '8px 16px 14px 50px', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-divider)' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                          <div>
                            <div className="ax-lbl" style={{ marginBottom: 4 }}>Cases of {o.asnNo} (TB_R_INSTRUCTION)</div>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                              <thead><tr>{['Case No', 'Customer Order', 'Destination', 'Qty', 'PO No'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                              <tbody>
                                {slices.filter((s) => s.asnNo === o.asnNo).map((s) => (
                                  <tr key={s.id} style={{ background: s.custOrderNo === o.custOrderNo ? 'var(--color-warn-bg, #fff8e6)' : undefined }}>
                                    <td style={td}>{s.caseNo}</td><td style={td}>{s.custOrderNo}</td><td style={td}>{dest(s.destCd)}</td><td style={td}>{s.qty}</td><td style={td}>{s.poNo}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                          <div>
                            <div className="ax-lbl" style={{ marginBottom: 4 }}>Replacement order lines (same part, UPD_STATUS 6, PO_MAPPED_FLAG N, no ASN; oldest first)</div>
                            {cands.length === 0 ? (
                              <div className="ax-muted" style={{ fontSize: 12, padding: '8px 0' }}>No candidate yet. The cancelled qty stays in this list until G-System receives an order line of {o.partNo}.</div>
                            ) : (
                              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                                <thead><tr><th style={{ ...th, background: 'transparent', width: 30 }} />{['Customer Order', 'Order Date', 'Destination', 'Qty'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                                <tbody>
                                  {cands.map((c) => (
                                    <tr key={c.custOrderNo}>
                                      <td style={td}><input type="checkbox" checked={!!chosen[c.custOrderNo]} onChange={(e) => {
                                        const next = { ...chosen };
                                        if (e.target.checked) next[c.custOrderNo] = c.qty; else delete next[c.custOrderNo];
                                        setPick({ ...pick, [o.key]: next });
                                      }} /></td>
                                      <td style={td}>{c.custOrderNo}</td><td style={td}>{niceDate(c.orderDt)}</td><td style={td}>{dest(c.destCd)}</td><td style={td}>{c.qty}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                            {cands.length > 0 && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 10, fontSize: 12.5 }}>
                                <span>Selected <b>{total}</b> of <b>{o.cancelQty}</b> pcs{total !== o.cancelQty && <span style={{ color: 'var(--color-danger)' }}> · the qty must add up to {o.cancelQty}</span>}</span>
                                <button className="btn btn-primary" style={{ marginLeft: 'auto' }} disabled={total !== o.cancelQty} onClick={() => setConfirm(o)}>Change Order Number</button>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  ),
                ];
              })}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ ...card, overflow: 'hidden' }}>
        <div style={{ padding: '10px 16px', borderBottom: '1px solid var(--color-divider)', fontSize: 12.5 }}><b>History</b> <span className="ax-muted">· TB_H_CROSSDOCK_ORDER_CHANGE</span></div>
        {history.length === 0 ? (
          <div style={{ padding: '20px 24px', textAlign: 'center', fontSize: 12.5, color: 'var(--color-neutral-600)' }}>No order number changed in this session.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead><tr>{['Time', 'ASN No', 'Case No', 'Part Number', 'From Order', 'To Order', 'To Destination', 'Qty', 'By'].map((h) => <th key={h} style={th}>{h}</th>)}</tr></thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={i}><td style={td}>{h.at}</td><td style={td}>{h.asnNo}</td><td style={td}>{h.caseNo}</td><td style={td}>{h.partNo}</td><td style={td}>{h.fromOrder}</td><td style={td}>{h.toOrder}</td><td style={td}>{dest(h.toDest)}</td><td style={td}>{h.qty}</td><td style={td}>{h.by}</td></tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {confirm && confirmRow && (
        <Modal title="Change Order Number?" onClose={() => setConfirm(null)}
          actions={<><button className="btn btn-secondary" onClick={() => setConfirm(null)}>No</button><button className="btn btn-primary" onClick={() => save(confirm, confirmRow.chosen)}>Yes, change</button></>}>
          {confirm.cancelQty} pcs of {confirm.custOrderNo} in {confirm.asnNo} ({confirmRow.cases.map((c) => `${c.caseNo}: ${c.qty}`).join(', ')}) will be moved to {Object.entries(confirmRow.chosen).map(([co, q]) => `${co} (${q})`).join(' + ')}.
        </Modal>
      )}
    </div>
  );
}
