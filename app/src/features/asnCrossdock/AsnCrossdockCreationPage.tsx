import { useMemo, useState } from 'react';
import { addAsn, asnByUnitOf, useAsns } from './asnStore';
import {
  asnNoFor, BUSINESS_DATES, buildCases, buildUnits, DESTS, niceDate, PART_NAME, PCS_PER_CASE, poQtyOf,
  ritCyclesFor, SUPPLIER_CODE, SUPPLIER_NAME, SUPPLIER_PLANT, type AsnCase, type InstrLine, type Unit, type UnitStatus,
} from './data';
import { Chip, Modal } from './ui';
import { card, th, td } from './styles';

type ViewAs = 'sup' | 'ds';
type StatusFilter = 'all' | UnitStatus;

interface Loaded {
  deliveryDate: string;
  ritNo: string;
  route: string;
}

const STATUS_LABEL: Record<UnitStatus, string> = { ready: 'Ready', notReady: 'Not Ready', created: 'Created', hold: 'On Hold' };

function StatusChip({ s }: { s: UnitStatus }) {
  return <Chip tone={s === 'ready' ? 'ok' : s === 'notReady' ? 'warn' : 'neutral'}>{STATUS_LABEL[s]}</Chip>;
}

interface DestRow {
  destCd: string;
  qty: number;
  lines: InstrLine[];
}

/** Destination level of a unit (one case per destination); a held destination is listed but not counted. */
function destRows(u: Unit): DestRow[] {
  const m = new Map<string, DestRow>();
  for (const l of [...u.lines, ...u.heldLines]) {
    const r = m.get(l.destCd) ?? { destCd: l.destCd, qty: 0, lines: [] };
    r.lines.push(l);
    if (!u.heldLines.includes(l)) r.qty += l.qty;
    m.set(l.destCd, r);
  }
  return [...m.values()];
}

interface PoRow {
  poNo: string;
  manifestNo: string;
  manifestItemNo: string;
  poQty: number;
}

function poRowsOf(c: AsnCase): PoRow[] {
  const m = new Map<string, PoRow>();
  for (const l of c.lines) {
    if (!l.poNo) continue;
    const k = `${l.poNo}|${l.manifestNo}|${l.manifestItemNo}`;
    if (!m.has(k)) m.set(k, { poNo: l.poNo, manifestNo: l.manifestNo ?? '—', manifestItemNo: l.manifestItemNo ?? '—', poQty: poQtyOf(l.poNo, c.partNo) });
  }
  return [...m.values()];
}

/** Screen ASN Crossdock Creation: Search (X12 Get Order pre-mapping), delivery plan, Create ASN and the Case List sub screen. */
export function AsnCrossdockCreationPage() {
  const asns = useAsns();
  const [today, setToday] = useState('2026-10-15');
  const [viewAs, setViewAs] = useState<ViewAs>('sup');
  const isDs = viewAs === 'ds';
  const [deliveryDate, setDeliveryDate] = useState('2026-10-15');
  const [ritNo, setRitNo] = useState('');
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [partFilter, setPartFilter] = useState('');
  const [stFilter, setStFilter] = useState<StatusFilter>('all');
  const [hold, setHold] = useState<Record<string, boolean>>({});
  const [sel, setSel] = useState<Record<string, boolean>>({});
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const [openDest, setOpenDest] = useState<Record<string, boolean>>({});
  const [openCase, setOpenCase] = useState<Record<number, boolean>>({});
  const [page, setPage] = useState<'list' | 'cases'>('list');
  const [confirm, setConfirm] = useState(false);
  const [done, setDone] = useState<string | null>(null);
  const [labelNote, setLabelNote] = useState(false);

  const rits = ritCyclesFor(deliveryDate);
  const rit = rits.find((r) => r.no === ritNo) ?? rits[0];
  const units = useMemo(() => buildUnits(today, asnByUnitOf(asns), hold), [today, asns, hold]);
  // Created units and units without any ready case are not listed; a fully held unit only for the D/S team
  const visible = units.filter((u) => u.status !== 'created' && (u.readyCases > 0 || (isDs && u.status === 'hold')));
  const rows = visible.filter((u) => (!partFilter || u.partNo === partFilter) && (stFilter === 'all' || u.status === stFilter));
  const selected = units.filter((u) => sel[u.key] && u.status === 'ready');
  const cases = useMemo(() => buildCases(selected), [selected]);
  const selQty = selected.reduce((a, u) => a + u.qty, 0);
  const asnDate = loaded?.deliveryDate ?? deliveryDate;
  const nextAsnNo = asnNoFor(asnDate, asns.filter((a) => a.deliveryDate === asnDate).length + 1);

  const changeToday = (d: string) => {
    setToday(d);
    setSel({});
    setLoaded(null);
    setDeliveryDate(d);
    setRitNo('');
  };

  const getOrder = () => {
    if (!rit) return;
    setLoaded({ deliveryDate, ritNo: rit.no, route: rit.route });
    setSel({});
    setOpen({});
  };

  /** Hold Flag at destination level: sets the flag of every order line of the unit's destination. */
  const toggleHoldDest = (lines: InstrLine[], held: boolean) => {
    const next = { ...hold };
    lines.forEach((l) => (next[l.id] = !held));
    setHold(next);
    setSel({});
  };

  const submit = () => {
    if (!loaded) return;
    addAsn({
      asnNo: nextAsnNo, deliveryDate: loaded.deliveryDate, rit: { no: loaded.ritNo, route: loaded.route }, unitKeys: selected.map((u) => u.key), cases,
      createdBy: 'D. Anggraini', createdAt: `${niceDate(today)} ${new Date().toTimeString().slice(0, 5)}`,
    });
    setDone(`${nextAsnNo} submitted with status Created. ${cases.length} cases are locked. Delivery ${niceDate(loaded.deliveryDate)} · ${loaded.ritNo}.`);
    setConfirm(false);
    setSel({});
    setPage('list');
  };

  if (page === 'cases' && loaded) {
    return (
      <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div>
          <button className="btn btn-secondary" onClick={() => setPage('list')} style={{ fontSize: 12, padding: '4px 12px' }}>← Back to ASN Crossdock Creation</button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h1 style={{ fontSize: 22, margin: 0 }}>ASN Crossdock — Case List</h1>
          <Chip tone="neutral">Draft</Chip>
        </div>
        <div style={{ ...card, padding: '12px 16px', fontSize: 12.5, background: 'var(--color-accent-100, #eef4fb)' }}>
          The selected units are mapped to their POs. Each Part Number + Customer Order Date is included completely; one case per Part Number, Customer Order Date and destination (max {PCS_PER_CASE} pcs/case).
        </div>
        <div style={{ ...card, padding: 16, display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, fontSize: 12.5 }}>
          <div><div className="ax-lbl">ASN No</div><div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{nextAsnNo}</div><div className="ax-muted">auto · assigned on submit</div></div>
          <div><div className="ax-lbl">Supplier · Plant</div><div style={{ fontWeight: 600 }}>{SUPPLIER_CODE} · {SUPPLIER_PLANT}</div><div className="ax-muted">{SUPPLIER_NAME}</div></div>
          <div><div className="ax-lbl">Delivery Date · Rit · Route</div><div style={{ fontWeight: 600 }}>{niceDate(loaded.deliveryDate)} · {loaded.ritNo} · {loaded.route}</div></div>
          <div><div className="ax-lbl">Delivery Qty</div><div style={{ fontWeight: 600 }}>{selQty} pcs</div></div>
          <div><div className="ax-lbl">Cases</div><div style={{ fontWeight: 600 }}>{cases.length} cases</div></div>
        </div>
        <div style={{ ...card }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 13, padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
            <span style={{ fontSize: 12.5, fontWeight: 600, marginRight: 'auto' }}>Case list in this ASN</span>
            <button className="btn btn-secondary" disabled={!cases.length} onClick={() => setLabelNote(true)}>Download Case Label</button>
          </div>
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead><tr><th style={{ ...th, width: 34 }} /><th style={th}>Case Number</th><th style={th}>Part Number</th><th style={{ ...th, textAlign: 'right' }}>Qty</th></tr></thead>
            <tbody>
              {cases.map((c) => [
                <tr key={c.seq}>
                  <td style={td}><button className="btn btn-secondary" title="PO detail" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setOpenCase({ ...openCase, [c.seq]: !openCase[c.seq] })}>{openCase[c.seq] ? '▾' : '▸'}</button></td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>Case {c.seq}</td>
                  <td style={{ ...td, fontFamily: 'var(--font-mono)' }}>{c.partNo}</td>
                  <td style={{ ...td, textAlign: 'right', fontWeight: 600 }}>{c.qty}</td>
                </tr>,
                openCase[c.seq] && (
                  <tr key={`${c.seq}-d`}>
                    <td colSpan={4} style={{ padding: '6px 16px 10px 50px', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-divider)' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                        <thead><tr>{['PO No', 'Manifest No', 'Manifest Item No', 'PO Qty'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                        <tbody>
                          {poRowsOf(c).map((r) => (
                            <tr key={`${r.poNo}-${r.manifestNo}-${r.manifestItemNo}`}><td style={td}>{r.poNo}</td><td style={td}>{r.manifestNo}</td><td style={td}>{r.manifestItemNo}</td><td style={td}>{r.poQty}</td></tr>
                          ))}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                ),
              ])}
              <tr><td colSpan={3} style={{ ...td, textAlign: 'right', fontWeight: 600 }}>Total</td><td style={{ ...td, textAlign: 'right', fontWeight: 700 }}>{selQty}</td></tr>
            </tbody>
          </table>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '11px 16px', borderTop: '1px solid var(--color-divider)' }}>
            <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary" onClick={() => setPage('list')}>Cancel</button>
              <button className="btn btn-primary" disabled={!cases.length} onClick={() => setConfirm(true)}>Submit ASN</button>
            </span>
          </div>
        </div>
        {confirm && (
          <Modal title="Submit ASN?" onClose={() => setConfirm(false)}
            actions={<><button className="btn btn-secondary" onClick={() => setConfirm(false)}>No</button><button className="btn btn-primary" onClick={submit}>Yes, submit</button></>}>
            {cases.length} cases ({selQty} pcs) will be locked into {nextAsnNo}, delivery {niceDate(loaded.deliveryDate)} · {loaded.ritNo}.
          </Modal>
        )}
        {labelNote && (
          <Modal title="Download Case Label" onClose={() => setLabelNote(false)} actions={<button className="btn btn-primary" onClick={() => setLabelNote(false)}>OK</button>}>
            Label format and content are not defined yet (TBD). {cases.length} labels would be printed.
          </Modal>
        )}
      </div>
    );
  }

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
        <div style={{ marginRight: 'auto' }}>
          <h1 style={{ fontSize: 22, margin: 0 }}>ASN Crossdock Creation</h1>
          <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
            Choose the Delivery Date and Rit, then Search: customer orders are taken FIFO by order date and pre-mapped to supplier POs. A unit (Part Number + Customer Order Date) is Ready when all its cases are assigned to a PO.
          </div>
        </div>
        <div className="field">
          <label>View as (prototype)</label>
          <div style={{ display: 'flex' }}>
            {([['sup', 'Supplier'], ['ds', 'D/S team']] as const).map(([k, label], i) => (
              <button key={k} className={`btn ${viewAs === k ? 'btn-primary' : 'btn-secondary'}`} style={{ borderRadius: i ? '0 6px 6px 0' : '6px 0 0 6px', padding: '8px 14px', whiteSpace: 'nowrap' }}
                onClick={() => { setViewAs(k); if (k === 'sup') { setOpen({}); setOpenDest({}); } }}>{label}</button>
            ))}
          </div>
        </div>
        <div className="field" style={{ width: 180 }}>
          <label>Business date (prototype)</label>
          <select className="input" value={today} onChange={(e) => changeToday(e.target.value)}>
            {BUSINESS_DATES.map((d) => <option key={d} value={d}>{niceDate(d)}</option>)}
          </select>
        </div>
      </div>

      <div style={{ ...card, padding: '14px 16px 16px' }}>
        <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase', marginBottom: 11 }}>Delivery</div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13 }}>
          <div className="field" style={{ width: 170 }}>
            <label>Delivery Date *</label>
            <input className="input" type="date" value={deliveryDate} min={today} onChange={(e) => { setDeliveryDate(e.target.value); setRitNo(''); }} />
          </div>
          <div className="field" style={{ width: 150 }}>
            <label>Rit *</label>
            <select className="input" value={rit?.no ?? ''} disabled={!rits.length} onChange={(e) => setRitNo(e.target.value)}>
              {rits.length ? rits.map((r) => <option key={r.no} value={r.no}>{r.no}</option>) : <option value="">No rit cycle</option>}
            </select>
          </div>
          <div className="field" style={{ width: 100 }}>
            <label>Route</label>
            <input className="input" value={rit?.route ?? '—'} disabled />
          </div>
          {!rits.length && <span style={{ color: 'var(--color-danger)', fontSize: 12, alignSelf: 'center' }}>No rit cycle available for {niceDate(deliveryDate)}. Choose another delivery date.</span>}
          <span style={{ marginLeft: 'auto' }}>
            <button className="btn btn-primary" disabled={!deliveryDate || !rit} onClick={getOrder}>Search</button>
          </span>
        </div>
      </div>

      <div style={{ ...card, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13, padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
          <div style={{ marginRight: 'auto', alignSelf: 'center' }}>
            <span style={{ fontSize: 12.5, fontWeight: 600 }}>Delivery plan</span>{' '}
            {loaded && (
              <span style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>
                {niceDate(loaded.deliveryDate)} · {loaded.ritNo} · {loaded.route} — {rows.length} units · {rows.filter((u) => u.status === 'ready').length} ready · {rows.filter((u) => u.status === 'notReady').length} not ready
              </span>
            )}
          </div>
          <div className="field" style={{ width: 150 }}>
            <label>Part Number</label>
            <select className="input" value={partFilter} disabled={!loaded} onChange={(e) => setPartFilter(e.target.value)}>
              <option value="">All</option>
              {Object.keys(PART_NAME).map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="field" style={{ width: 150 }}>
            <label>Status</label>
            <select className="input" value={stFilter} disabled={!loaded} onChange={(e) => setStFilter(e.target.value as StatusFilter)}>
              <option value="all">All</option>
              <option value="ready">Ready</option>
              <option value="notReady">Not Ready</option>
              {isDs && <option value="hold">On Hold</option>}
            </select>
          </div>
        </div>
        {!loaded ? (
          <div style={{ padding: '40px 24px', textAlign: 'center', fontSize: 13, color: 'var(--color-neutral-700)' }}>Choose the Delivery Date and Rit, then click Search.</div>
        ) : rows.length === 0 ? (
          <div style={{ padding: '40px 24px', textAlign: 'center', fontSize: 13 }}>No customer order matches this filter.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead>
              <tr>
                <th style={{ ...th, width: 34 }} />
                <th style={th}>Customer Order Date</th>
                <th style={th}>Part Number</th>
                <th style={{ ...th, textAlign: 'right' }}>Case Qty</th>
                <th style={{ ...th, textAlign: 'right' }}>PO Readiness (case)</th>
                <th style={th}>ASN Status</th>
                <th style={{ ...th, width: 34 }} />
              </tr>
            </thead>
            <tbody>
              {rows.map((u) => {
                const enabled = u.status === 'ready';
                const tip = u.status === 'created' ? `Already in ${u.asnNo}` : u.status === 'notReady' ? `Not Ready: ${u.notAssignedCases} of ${u.caseCount} cases of ${u.partNo} / ${niceDate(u.orderDt)} are not assigned to a PO yet` : u.status === 'hold' ? 'All destinations are on hold' : 'Select to create an ASN';
                return [
                  <tr key={u.key} style={{ background: u.status === 'notReady' ? 'var(--color-warn-bg, #fff8e6)' : undefined }}>
                    <td style={td}><input type="checkbox" checked={u.status === 'created' || !!sel[u.key]} disabled={!enabled} title={tip} onChange={(e) => setSel({ ...sel, [u.key]: e.target.checked })} /></td>
                    <td style={{ ...td, fontWeight: 600 }}>{niceDate(u.orderDt)}</td>
                    <td style={{ ...td, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{u.partNo}</td>
                    <td style={{ ...td, textAlign: 'right', fontWeight: 600 }}>{u.caseCount}</td>
                    <td style={{ ...td, textAlign: 'right', color: u.readyCases < u.caseCount ? 'var(--color-danger)' : undefined }}>{u.readyCases}</td>
                    <td style={td} title={tip}><StatusChip s={u.status} />{u.heldLines.length > 0 && isDs && <div className="ax-muted">{new Set(u.heldLines.map((l) => l.destCd)).size} destination(s) on hold</div>}</td>
                    <td style={td}>{isDs && <button className="btn btn-secondary" title="Destination detail (D/S team)" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setOpen({ ...open, [u.key]: !open[u.key] })}>{open[u.key] ? '▾' : '▸'}</button>}</td>
                  </tr>,
                  isDs && open[u.key] && (
                    <tr key={`${u.key}-d`}>
                      <td colSpan={7} style={{ padding: '8px 16px 12px 50px', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-divider)' }}>
                        <div className="ax-lbl" style={{ marginBottom: 4 }}>Destination · {u.qty} pcs</div>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                          <thead><tr><th style={{ ...th, background: 'transparent', width: 30 }} />{['Destination', 'Case', 'Qty (pcs)', 'Pcs/Case', 'Hold Flag'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                          <tbody>
                            {destRows(u).map((r) => {
                              const held = r.lines.every((l) => hold[l.id]);
                              const dk = `${u.key}|${r.destCd}`;
                              return [
                                <tr key={dk} style={{ color: held ? 'var(--color-neutral-600)' : undefined }}>
                                  <td style={td}><button className="btn btn-secondary" title="Customer orders" style={{ padding: '1px 7px', fontSize: 10.5 }} onClick={() => setOpenDest({ ...openDest, [dk]: !openDest[dk] })}>{openDest[dk] ? '▾' : '▸'}</button></td>
                                  <td style={td}>{DESTS[r.destCd].code} · {DESTS[r.destCd].name}</td>
                                  <td style={td}>{held ? 0 : 1}</td>
                                  <td style={td}>{held ? `${r.lines.reduce((a, l) => a + l.qty, 0)} (on hold)` : r.qty}</td>
                                  <td style={td}>{PCS_PER_CASE}</td>
                                  <td style={td}>
                                    <button className="btn btn-secondary" style={{ padding: '1px 8px', fontSize: 11 }} onClick={() => toggleHoldDest(r.lines, held)}>
                                      {held ? 'Y · Release' : 'N · Hold'}
                                    </button>
                                  </td>
                                </tr>,
                                openDest[dk] && (
                                  <tr key={`${dk}-l`}>
                                    <td />
                                    <td colSpan={5} style={{ padding: '4px 0 10px' }}>
                                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5, background: 'var(--color-neutral-100)' }}>
                                        <thead><tr>{['Customer Order No', 'Detailed Item No', 'Qty (pcs)', 'PO No', 'PO Date'].map((h) => <th key={h} style={{ ...th, height: 28 }}>{h}</th>)}</tr></thead>
                                        <tbody>
                                          {r.lines.map((l) => (
                                            <tr key={l.id}>
                                              <td style={td}>{l.custOrderNo}</td><td style={td}>{l.detailedItemNo}</td><td style={td}>{l.qty}</td>
                                              <td style={td}>{l.poNo ?? '—'}</td><td style={td}>{niceDate(l.poDate)}</td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </td>
                                  </tr>
                                ),
                              ];
                            })}
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  ),
                ];
              })}
            </tbody>
          </table>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderTop: '1px solid var(--color-divider)', background: 'var(--color-surface)' }}>
          <span style={{ fontSize: 12.5 }}>
            {selected.length ? <><b>{selected.length} units selected</b> · {cases.length} cases · {selected.map((u) => `${u.partNo} ${niceDate(u.orderDt).slice(0, 6)}`).join(', ')}</> : 'Tick one or more Ready units. Units from different Customer Order Dates can go into the same ASN.'}
          </span>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" disabled={!selected.length} onClick={() => setSel({})}>Clear selection</button>
            <button className="btn btn-primary" disabled={!selected.length} onClick={() => { setOpenCase({}); setPage('cases'); }}>Create ASN</button>
          </span>
        </div>
      </div>

      {done && (
        <Modal title="ASN submitted" onClose={() => setDone(null)} actions={<button className="btn btn-primary" onClick={() => setDone(null)}>OK</button>}>
          {done} The ASN is shown in ASN Inquiry.
        </Modal>
      )}
    </div>
  );
}
