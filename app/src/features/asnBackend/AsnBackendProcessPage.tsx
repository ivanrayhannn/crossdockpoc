import type { ReactNode } from 'react';
import { card, th, td } from '../asnCrossdock/styles';

function Section({ no, title, children }: { no: string; title: string; children: ReactNode }) {
  return (
    <div style={{ ...card, padding: '14px 18px 16px' }}>
      <h2 style={{ fontSize: 15, margin: '0 0 8px' }}><span style={{ color: '#dc3545', marginRight: 8 }}>{no}</span>{title}</h2>
      <div style={{ fontSize: 12.5, lineHeight: 1.6 }}>{children}</div>
    </div>
  );
}

function Steps({ rows }: { rows: [string, string, string][] }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, marginTop: 6 }}>
      <thead><tr>{['Step', 'Process (backend)', 'Table / result'].map((h) => <th key={h} style={{ ...th, background: 'transparent' }}>{h}</th>)}</tr></thead>
      <tbody>{rows.map(([a, b, c]) => <tr key={a}><td style={{ ...td, width: 40, fontWeight: 600 }}>{a}</td><td style={td}>{b}</td><td style={td}>{c}</td></tr>)}</tbody>
    </table>
  );
}

const LANE: Record<'sup' | 'ds' | 'sys', { label: string; bg: string }> = {
  sup: { label: 'Supplier session', bg: '#fff2cc' },
  ds: { label: 'D/S team session', bg: '#fce4d6' },
  sys: { label: 'Supplier System backend', bg: '#d9e1f2' },
};

const TIMELINE: ['sup' | 'ds' | 'sys', string][] = [
  ['sup', 'T1 · Search: delivery plan loaded; PART-A 13-Oct is Ready'],
  ['sup', 'T2 · Tick PART-A 13-Oct (held lines at tick time = 0)'],
  ['ds', 'T3 · Same delivery plan; Hold destination Vietnam of PART-A 13-Oct'],
  ['sys', 'T4 · HOLD_FLAG = Y on the Vietnam lines (TB_R_H0253_ORDER_CONTROL_PRE)'],
  ['sup', 'T5 · Click Create ASN'],
  ['sys', 'T6 · Re-check the ticked units in the same transaction: a line now has HOLD_FLAG = Y → stop, nothing is mapped'],
  ['sup', 'T7 · Message "Some order has been already hold, please select other records"; the delivery plan is refreshed automatically and all ticked units are unticked'],
];

/** Explanation of the backend of ASN Crossdock Creation: Search, Create ASN with the hold check, and the Submit ASN batch. */
export function AsnBackendProcessPage() {
  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>ASN Backend Process</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          What happens behind ASN Crossdock Creation (X8): Search (X12), Create ASN with the hold check, and Submit ASN as a batch (X14) with a Submit ID. Last section: how to simulate it in this prototype.
        </div>
      </div>

      <Section no="1" title="Search – Get Order (X12, on demand)">
        <Steps rows={[
          ['1', 'Read the open qty of the H0253 customer orders (ORDER_STATUS 7, HOLD_FLAG N; open qty = order qty minus the qty in TB_R_INSTRUCTION) in the receiving scan order: Allocation Priority (= Customer Order Date), Customer Code, Customer Order No, Order Date, Order Time, Destination, Detailed Item No, Serial No.', 'TB_R_H0253_ORDER_CONTROL_PRE, TB_R_INSTRUCTION'],
          ['2', 'Read PO parts of the Pra Daily Order: CROSS_DOCK_FLAG X; open qty = PO qty minus the mapped qty; by PO date.', 'TB_R_PRA_DAILY_ORDER_MANIFEST / PART, TB_R_PRA_DAILY_ORDER_MAPPED (new)'],
          ['3', 'Per unit (Part Number + Customer Order Date, oldest first) give the PO qty in scan order and cut the pcs into supplier cases of pcs/case (a case can hold several destinations). Mark CUT_FLAG Y after a case where every destination is a multiple of pcs/case; a case is Ready (6) when it and every earlier case have a PO (no permanent change).', '#TEMP_INSTRUCTION (temporary)'],
          ['4', 'Return the delivery plan with the case rows: the user ticks cases from case 1 up to a case with CUT_FLAG Y (MSG10 when the next cases are ticked together). Units without any pre-mapped case and units fully in an ASN are not listed.', 'Screen'],
        ]} />
      </Section>

      <Section no="2" title="Create ASN – real mapping with the hold check">
        <Steps rows={[
          ['1', 'Lock the H0253 lines of the ticked units (row lock in one transaction).', 'TB_R_H0253_ORDER_CONTROL_PRE'],
          ['2', 'Re-check each line: HOLD_FLAG must still be N; the ticked cases must still be Ready and end on CUT_FLAG Y.', 'If not: roll back, the whole create fails, message "Some order has been already hold, please select other records", the delivery plan is refreshed automatically and all units are unticked'],
          ['3', 'Check that all ticked units are of one Supplier Code + Plant (one ASN = one supplier + plant). Add the mapped qty per PO part; PO_MAPPED_FLAG = Y on the lines that are now completely mapped.', 'TB_R_H0253_ORDER_CONTROL_PRE, TB_R_PRA_DAILY_ORDER_MAPPED (new)'],
          ['4', 'Insert the real mapping of the ticked cases: one row per supplier case x order line x PO, case and line sequence of the Search (scan order). The rest of a line stays open for a later ASN.', 'TB_R_INSTRUCTION'],
          ['5', 'Commit and open the Case List. Back / Cancel deletes the rows from TB_R_INSTRUCTION and releases the flags and mapped qty.', 'Screen'],
        ]} />
      </Section>

      <Section no="3" title="Submit ASN – batch with Submit ID (X14)">
        <Steps rows={[
          ['1', 'Confirmation "Submit ASN? {n} cases ({q} pcs) will be created into {ASN No}, delivery {date} · {rit}." Yes → the draft is handed to the batch with a Submit ID; the submit process follows the existing ASN.', 'Submit request (existing)'],
          ['2', 'Batch: ASN No and Case No are generated automatically as today (existing): the last sequence is read from and saved in the existing last sequence table.', 'Existing last sequence table'],
          ['3', 'Batch: insert the ASN (status Created) into the existing ASN tables and write ASN_NO / CASE_NO back to TB_R_INSTRUCTION.', 'TB_R_DAILY_ORDER_MANIFEST / TB_R_DAILY_ORDER_PART, TB_R_INSTRUCTION'],
          ['4', 'Batch: write start, result and end messages with the Submit ID to the existing log; no success popup on the screen.', 'Log (existing) → Log Monitoring'],
          ['5', 'Error: roll back the batch, log the error with the Submit ID; the mapping in TB_R_INSTRUCTION is released.', 'Log (existing)'],
        ]} />
        <div style={{ marginTop: 8 }}>
          Log message on success: <i>"ASN-50221-261015-001 submitted with status Created. 3 cases are saved. Delivery 15-Oct-2026 · Rit 1. The ASN is shown in ASN Inquiry."</i>
        </div>
      </Section>

      <Section no="4" title="Concurrency: D/S hold while the supplier creates the ASN">
        <div style={{ display: 'grid', gridTemplateColumns: '170px 1fr', gap: 6, marginTop: 4 }}>
          {TIMELINE.map(([lane, text]) => [
            <div key={`${text}-l`} style={{ background: LANE[lane].bg, borderRadius: 6, padding: '6px 10px', fontWeight: 600, fontSize: 12 }}>{LANE[lane].label}</div>,
            <div key={text} style={{ background: LANE[lane].bg, borderRadius: 6, padding: '6px 10px', fontSize: 12, marginLeft: lane === 'sup' ? 0 : lane === 'ds' ? 40 : 80 }}>{text}</div>,
          ])}
        </div>
        <div style={{ marginTop: 10 }}>
          Rule: the hold always wins. The create fails for the whole selection (also the units that are not held); the user selects again from the refreshed list.
        </div>
      </Section>

      <Section no="5" title="Cancel of an order (not in Supplier System)">
        <Steps rows={[
          ['1', 'The order is cancelled in T-System (with or without hold flag Y): the H0253 row changes to ORDER_STATUS 2; a partial cancel splits the line into a new SERIAL_NO. Supplier System never cancels an order itself.', 'H0253 (T-System, insert / update)'],
          ['2', 'XD08 (one batch) upserts the rows changed since the last run (INTF_UPDATE_DT): ORDER_STATUS keeps the first value, UPD_STATUS = 2 (cancel) or 6 (received). Lines with UPD_STATUS are not taken by XD09.', 'TB_R_H0253_ORDER_CONTROL_PRE'],
          ['3', 'XD08 releases every draft (TB_R_INSTRUCTION without ASN No): rows deleted, MAPPED_QTY reduced, PO_MAPPED_FLAG N; the cases come back in the delivery plan. [Submit ASN] re-checks the draft as well.', 'TB_R_INSTRUCTION, TB_R_PRA_DAILY_ORDER_MAPPED'],
          ['4', 'A cancel of qty already in a submitted ASN (abnormality) is listed in Change Order Number (XD11, D/S team) until the qty is moved to received lines of the same part (UPD_STATUS 6, PO_MAPPED_FLAG N, no ASN; oldest first; several lines / another destination allowed). No Cancel ASN.', 'TB_R_INSTRUCTION, TB_H_CROSSDOCK_ORDER_CHANGE'],
          ['5', 'Simulation of the H0253 scenarios: menu Cancel Order Simulation; replacement: menu Change Order Number.', 'Prototype'],
        ]} />
      </Section>

      <Section no="6" title="How to simulate it in this prototype">
        <ol style={{ margin: '4px 0 0', paddingLeft: 20 }}>
          <li>Open <a href="#/asn-creation">ASN Creation</a>, keep <b>View as: Supplier</b>, click <b>Search</b>.</li>
          <li>Tick <b>PART-A 13-Oct-2026</b> (do not click Create yet).</li>
          <li>Switch to <b>View as: D/S team</b> — this is the other session. Expand PART-A 13-Oct and click <b>N · Hold</b> on one destination.</li>
          <li>Switch back to <b>View as: Supplier</b>: the tick is still there (the supplier did not refresh yet).</li>
          <li>Click <b>Create ASN</b>: the message <i>"Some order has been already hold, please select other records"</i> appears, the Case List does not open, all ticks are removed and the delivery plan is refreshed automatically (see "refreshed hh:mm:ss" next to the counter).</li>
          <li>One ASN = one Supplier Code + Plant: in View as D/S team (super admin, all suppliers) tick a PART-A unit (50221) and PART-D (50330) and click Create ASN → message "One ASN is for one Supplier Code and Supplier Plant".</li>
          <li>Tick another Ready unit, Create ASN and Submit: the Submit ID banner appears and the result is in <a href="#/log-monitoring">Log Monitoring</a>.</li>
        </ol>
        <div style={{ marginTop: 8, color: 'var(--color-neutral-600)', fontSize: 11.5 }}>
          Each View as keeps its own selection, so the two views act like two users on the same data.
        </div>
      </Section>
    </div>
  );
}
