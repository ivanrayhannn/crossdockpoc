import { useMemo, useState } from 'react';
import { addAsn, asnByUnitOf, useAsns } from './asnStore';
import {
  addDays, asnNoFor, BUSINESS_DATES, buildCases, buildUnits, DESTS, isAssigned, niceDate, PART_NAME, PCS_PER_CASE,
  ritCyclesFor, SUPPLIER_CODE, SUPPLIER_NAME, SUPPLIER_PLANT, type Unit,
} from './data';
import { CaseTable, Chip, Modal } from './ui';
import { card, th, td } from './styles';

interface Query {
  from: string;
  to: string;
  part: string;
  st: 'all' | 'ready' | 'waiting' | 'asn';
}
const EMPTY: Query = { from: '', to: '', part: '', st: 'all' };

function matches(u: Unit, q: Query): boolean {
  if (q.from && u.orderDt < q.from) return false;
  if (q.to && u.orderDt > q.to) return false;
  if (q.part && u.partNo !== q.part) return false;
  if (q.st === 'ready') return u.ready && !u.asnNo;
  if (q.st === 'waiting') return !u.ready;
  if (q.st === 'asn') return !!u.asnNo;
  return true;
}

interface DestRow {
  destCd: string;
  qty: number;
  notAssigned: number;
}

/** Destination level of a unit (one case per destination), shown in the D/S detail. */
function destRows(u: Unit, today: string): DestRow[] {
  const m = new Map<string, DestRow>();
  for (const l of u.lines) {
    const r = m.get(l.destCd) ?? { destCd: l.destCd, qty: 0, notAssigned: 0 };
    r.qty += l.qty;
    if (!isAssigned(l, today)) r.notAssigned += l.qty;
    m.set(l.destCd, r);
  }
  return [...m.values()];
}

type ViewAs = 'sup' | 'ds';

/** Screen ASN Crossdock Creation: delivery plan per Part Number + Customer Order Date, and its Case List sub screen. */
export function AsnCrossdockCreationPage() {
  const asns = useAsns();
  const [today, setToday] = useState('2026-10-15');
  const [filter, setFilter] = useState<Query>(EMPTY);
  const [query, setQuery] = useState<Query>(EMPTY);
  const [sel, setSel] = useState<Record<string, boolean>>({});
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const [page, setPage] = useState<'list' | 'cases'>('list');
  const [deliveryDate, setDeliveryDate] = useState(() => addDays('2026-10-15', 1));
  const [ritNo, setRitNo] = useState('');
  const [confirm, setConfirm] = useState(false);
  const [done, setDone] = useState<string | null>(null);
  const [labelNote, setLabelNote] = useState(false);
  const [viewAs, setViewAs] = useState<ViewAs>('sup');
  const isDs = viewAs === 'ds';

  const units = useMemo(() => buildUnits(today, asnByUnitOf(asns)), [today, asns]);
  const rows = units.filter((u) => matches(u, query));
  const selected = units.filter((u) => sel[u.key] && u.ready && !u.asnNo);
  const cases = useMemo(() => buildCases(selected), [selected]);
  const selQty = selected.reduce((a, u) => a + u.qty, 0);
  const rits = ritCyclesFor(deliveryDate);
  const rit = rits.find((r) => r.no === ritNo) ?? rits[0];
  const nextAsnNo = asnNoFor(deliveryDate || today, asns.filter((a) => a.deliveryDate === deliveryDate).length + 1);

  const changeToday = (d: string) => {
    setToday(d);
    setSel({});
    setDeliveryDate(addDays(d, 1));
  };

  const submit = () => {
    if (!rit) return;
    addAsn({
      asnNo: nextAsnNo, deliveryDate, rit, unitKeys: selected.map((u) => u.key), cases,
      createdBy: 'D. Anggraini', createdAt: `${niceDate(today)} ${new Date().toTimeString().slice(0, 5)}`,
    });
    setDone(`${nextAsnNo} submitted. ${cases.length} cases are locked. Delivery ${niceDate(deliveryDate)} · ${rit.no}.`);
    setConfirm(false);
    setSel({});
    setPage('list');
  };

  if (page === 'cases') {
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
          Each Part Number + Customer Order Date is included completely. One case per Part Number, Customer Order Date and destination (max {PCS_PER_CASE} pcs/case).
        </div>
        <div style={{ ...card, padding: 16, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, fontSize: 12.5 }}>
          <div><div className="ax-lbl">ASN No</div><div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{nextAsnNo}</div><div className="ax-muted">auto · assigned on submit</div></div>
          <div><div className="ax-lbl">Supplier · Plant</div><div style={{ fontWeight: 600 }}>{SUPPLIER_CODE} · {SUPPLIER_PLANT}</div><div className="ax-muted">{SUPPLIER_NAME}</div></div>
          <div><div className="ax-lbl">Part / Customer Order Date</div>{selected.map((u) => <div key={u.key} style={{ fontWeight: 600 }}>{u.partNo} · {niceDate(u.orderDt)}</div>)}</div>
          <div><div className="ax-lbl">Cases · Qty</div><div style={{ fontWeight: 600 }}>{cases.length} cases · {selQty} pcs</div></div>
        </div>
        <div style={{ ...card }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13, padding: '12px 16px', borderBottom: '1px solid var(--color-divider)' }}>
            <span style={{ fontSize: 12.5, fontWeight: 600, marginRight: 'auto', alignSelf: 'center' }}>Case list in this ASN</span>
            <div className="field" style={{ width: 170 }}>
              <label>Delivery Date *</label>
              <input className="input" type="date" value={deliveryDate} min={today} onChange={(e) => { setDeliveryDate(e.target.value); setRitNo(''); }} />
            </div>
            <div className="field" style={{ width: 150 }}>
              <label>Rit Cycle *</label>
              <select className="input" value={rit?.no ?? ''} disabled={!rits.length} onChange={(e) => setRitNo(e.target.value)}>
                {rits.length ? rits.map((r) => <option key={r.no} value={r.no}>{r.no}</option>) : <option value="">No rit cycle</option>}
              </select>
            </div>
            <div className="field" style={{ width: 90 }}>
              <label>Route</label>
              <input className="input" value={rit?.route ?? '—'} disabled />
            </div>
            <button className="btn btn-secondary" disabled={!cases.length} onClick={() => setLabelNote(true)}>Download Case Label</button>
          </div>
          <CaseTable cases={cases} caseLabel={(c) => `Case ${c.seq}`} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '11px 16px', borderTop: '1px solid var(--color-divider)' }}>
            {!rits.length && <span style={{ color: 'var(--color-danger)', fontSize: 12 }}>No rit cycle available for {niceDate(deliveryDate)}. Choose another delivery date.</span>}
            <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary" onClick={() => setPage('list')}>Cancel</button>
              <button className="btn btn-primary" disabled={!cases.length || !deliveryDate || !rit} onClick={() => setConfirm(true)}>Submit ASN</button>
            </span>
          </div>
        </div>
        {confirm && (
          <Modal title="Submit ASN?" onClose={() => setConfirm(false)}
            actions={<><button className="btn btn-secondary" onClick={() => setConfirm(false)}>No</button><button className="btn btn-primary" onClick={submit}>Yes, submit</button></>}>
            {cases.length} cases ({selQty} pcs) will be locked into {nextAsnNo}, delivery {niceDate(deliveryDate)} · {rit?.no}.
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
            Delivery plan per Part Number + Customer Order Date, in cases. A unit is Ready to Delivery when all its cases are assigned to a released PO; it then goes into one ASN as a whole. The destination and pcs detail is open to the D/S team.
          </div>
        </div>
        <div className="field">
          <label>View as (prototype)</label>
          <div style={{ display: 'flex' }}>
            {([['sup', 'Supplier'], ['ds', 'D/S team']] as const).map(([k, label], i) => (
              <button key={k} className={`btn ${viewAs === k ? 'btn-primary' : 'btn-secondary'}`} style={{ borderRadius: i ? '0 6px 6px 0' : '6px 0 0 6px', padding: '8px 14px', whiteSpace: 'nowrap' }}
                onClick={() => { setViewAs(k); if (k === 'sup') setOpen({}); }}>{label}</button>
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
        <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase', marginBottom: 11 }}>Search criteria</div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 13 }}>
          <div className="field" style={{ width: 170 }}><label>Customer Order Date - From</label><input className="input" type="date" value={filter.from} onChange={(e) => setFilter({ ...filter, from: e.target.value })} /></div>
          <div className="field" style={{ width: 170 }}><label>To</label><input className="input" type="date" value={filter.to} onChange={(e) => setFilter({ ...filter, to: e.target.value })} /></div>
          <div className="field" style={{ width: 160 }}>
            <label>Part Number</label>
            <select className="input" value={filter.part} onChange={(e) => setFilter({ ...filter, part: e.target.value })}>
              <option value="">All</option>
              {Object.keys(PART_NAME).map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="field" style={{ width: 200 }}>
            <label>Status</label>
            <select className="input" value={filter.st} onChange={(e) => setFilter({ ...filter, st: e.target.value as Query['st'] })}>
              <option value="all">All</option>
              <option value="ready">Ready to Delivery</option>
              <option value="waiting">Waiting for Next PO</option>
              <option value="asn">In ASN</option>
            </select>
          </div>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={() => { setFilter(EMPTY); setQuery(EMPTY); }}>Reset</button>
            <button className="btn btn-primary" onClick={() => setQuery(filter)}>Search</button>
          </span>
        </div>
      </div>

      <div style={{ ...card, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '10px 16px', borderBottom: '1px solid var(--color-divider)' }}>
          <span style={{ fontSize: 12.5, fontWeight: 600 }}>Delivery plan</span>
          <span style={{ fontSize: 11.5, color: 'var(--color-neutral-600)' }}>
            {rows.length} units · {rows.filter((u) => u.ready && !u.asnNo).length} ready · {rows.filter((u) => !u.ready).length} waiting
          </span>
        </div>
        {rows.length === 0 ? (
          <div style={{ padding: '40px 24px', textAlign: 'center', fontSize: 13 }}>No delivery plan matches this search.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0, fontSize: 12.5 }}>
            <thead>
              <tr>
                <th style={{ ...th, width: 34 }} />
                <th style={th}>Customer Order Date</th>
                <th style={th}>Part Number</th>
                <th style={{ ...th, textAlign: 'right' }}>Case Qty</th>
                <th style={{ ...th, textAlign: 'right' }}>Not Assigned (case)</th>
                <th style={th}>PO No</th>
                <th style={th}>Last PO Date</th>
                <th style={th}>Status</th>
                <th style={th}>ASN No</th>
                <th style={{ ...th, width: 34 }} />
              </tr>
            </thead>
            <tbody>
              {rows.map((u) => {
                const enabled = u.ready && !u.asnNo;
                const tip = u.asnNo ? `Already in ${u.asnNo}` : !u.ready ? `Waiting for Next PO: ${u.notAssignedCases} of ${u.caseCount} cases of ${u.partNo} / ${niceDate(u.orderDt)} are not assigned to a released PO yet` : 'Select to create an ASN';
                return [
                  <tr key={u.key} style={{ background: !u.ready ? 'var(--color-warn-bg, #fff8e6)' : undefined }}>
                    <td style={td}><input type="checkbox" checked={!!u.asnNo || !!sel[u.key]} disabled={!enabled} title={tip} onChange={(e) => setSel({ ...sel, [u.key]: e.target.checked })} /></td>
                    <td style={{ ...td, fontWeight: 600 }}>{niceDate(u.orderDt)}</td>
                    <td style={td}><span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{u.partNo}</span><div className="ax-muted">{PART_NAME[u.partNo]}</div></td>
                    <td style={{ ...td, textAlign: 'right', fontWeight: 600 }}>{u.caseCount}</td>
                    <td style={{ ...td, textAlign: 'right', color: u.notAssignedCases ? 'var(--color-danger)' : undefined }}>{u.notAssignedCases || '—'}</td>
                    <td style={td}>{u.pos.join(', ') || '—'}</td>
                    <td style={td}>{niceDate(u.lastPoDate)}</td>
                    <td style={td}>{u.asnNo ? <Chip tone="neutral">In ASN</Chip> : u.ready ? <Chip tone="ok">Ready to Delivery</Chip> : <Chip tone="warn">Waiting for Next PO</Chip>}</td>
                    <td style={{ ...td, fontFamily: 'var(--font-mono)', fontSize: 11.5 }}>{u.asnNo ?? '—'}</td>
                    <td style={td}>{isDs && <button className="btn btn-secondary" title="Destination and order line detail (D/S team)" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => setOpen({ ...open, [u.key]: !open[u.key] })}>{open[u.key] ? '▾' : '▸'}</button>}</td>
                  </tr>,
                  isDs && open[u.key] && (
                    <tr key={`${u.key}-d`}>
                      <td colSpan={10} style={{ padding: '8px 16px 12px 50px', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-divider)' }}>
                        <div className="ax-lbl" style={{ marginBottom: 4 }}>Destination · {u.qty} pcs{u.remainingQty ? ` · ${u.remainingQty} pcs not assigned` : ''}</div>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, marginBottom: 10 }}>
                          <thead><tr>{['Destination', 'Case', 'Qty (pcs)', 'Not Assigned (pcs)'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                          <tbody>
                            {destRows(u, today).map((r) => (
                              <tr key={r.destCd}>
                                <td style={td}>{DESTS[r.destCd].code} · {DESTS[r.destCd].name}</td><td style={td}>1</td><td style={td}>{r.qty}</td>
                                <td style={{ ...td, color: r.notAssigned ? 'var(--color-danger)' : undefined }}>{r.notAssigned || '—'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        <div className="ax-lbl" style={{ marginBottom: 4 }}>Order lines</div>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                          <thead><tr>{['Customer Order No', 'Detailed Item No', 'Destination', 'Qty', 'PO No', 'PO Date', 'Assignment'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
                          <tbody>
                            {u.lines.map((l) => (
                              <tr key={l.id}>
                                <td style={td}>{l.custOrderNo}</td><td style={td}>{l.detailedItemNo}</td>
                                <td style={td}>{DESTS[l.destCd].code} · {DESTS[l.destCd].name}</td><td style={td}>{l.qty}</td>
                                <td style={td}>{l.poNo ?? '—'}</td><td style={td}>{niceDate(l.poDate)}</td>
                                <td style={td}>{isAssigned(l, today) ? 'Assigned' : l.poNo ? `Planned (PO ${niceDate(l.poDate)})` : 'Not assigned'}</td>
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
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 16px', borderTop: '1px solid var(--color-divider)', background: 'var(--color-surface)' }}>
          <span style={{ fontSize: 12.5 }}>
            {selected.length ? <><b>{selected.length} units selected</b> · {cases.length} cases · {selected.map((u) => `${u.partNo} ${niceDate(u.orderDt).slice(0, 6)}`).join(', ')}</> : 'Tick one or more Ready to Delivery units. Units from different Customer Order Dates can go into the same ASN.'}
          </span>
          <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" disabled={!selected.length} onClick={() => setSel({})}>Clear selection</button>
            <button className="btn btn-primary" disabled={!selected.length} onClick={() => setPage('cases')}>Create ASN</button>
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

