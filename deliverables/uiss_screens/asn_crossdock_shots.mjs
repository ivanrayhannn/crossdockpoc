// Screenshots of ASN Crossdock Creation (XD10), ASN Inquiry and Log Monitoring from the prototype (decided 21-Oct: case check boxes).
// Usage: node asn_crossdock_shots.mjs http://localhost:5179/crossdockpoc/ ./asn_crossdock
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const pg = await b.newPage({ viewport: { width: 1440, height: 900 } });
const shot = async (name) => { await pg.waitForTimeout(250); await pg.screenshot({ path: `${dir}/${name}.png`, fullPage: true }); };
const unitRow = (part, date) => pg.locator('tbody > tr').filter({ has: pg.locator('td', { hasText: new RegExp(`^${part}$`) }) }).filter({ hasText: date });
const caseBox = (re) => pg.getByRole('checkbox', { name: re }).first();
const view = (who) => pg.getByRole('button', { name: who, exact: true }).click();
const search = () => pg.getByRole('button', { name: 'Search', exact: true }).click();

// data = simulasi_asn_rev.xlsx, business date 18-Oct (default): PART-X 17-Oct, 5 cases, cases 1-4 Ready, case 5 Short PO
const destHold = (code) => pg.locator('tr').filter({ has: pg.locator('td', { hasText: new RegExp(`^${code} · `) }) }).last().getByRole('button', { name: /Hold|Release/ });
await pg.goto(url + '#/asn-creation'); await pg.waitForTimeout(800);
await shot('c_01_initial');
await search(); await shot('c_02_delivery_plan');
// D/S team: destination detail and customer orders of PART-X 17-Oct
await view('D/S team'); await search();
await unitRow('PART-X', '17-Oct').getByTitle('Destination detail (D/S team)').click();
await pg.getByTitle('Customer orders').first().click(); await shot('c_03_ds_detail');
// hold Thailand (CO-14104) of PART-X 17-Oct: scan order and cases are computed again without TH
await destHold('9722D10').click(); await shot('c_04_ds_hold');
await destHold('9722D10').click();
// supplier: tick case 3 of PART-X 17-Oct → cases 1-3 selected
await view('Supplier'); await search();
await caseBox(/Case 3 can be sent alone/).check(); await shot('c_05_selected');
// D/S team (other session) holds Thailand of the ticked unit
await view('D/S team'); await search();
await unitRow('PART-X', '17-Oct').getByTitle('Destination detail (D/S team)').click();
await destHold('9722D10').click(); await shot('c_05a_ds_hold_other_session');
await view('Supplier');
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_05c_hold_conflict');
await pg.getByRole('button', { name: 'OK' }).click(); await shot('c_05d_after_refresh');
await view('D/S team');
await unitRow('PART-X', '17-Oct').getByTitle('Destination detail (D/S team)').click();
await destHold('9722D10').click();
// D/S team ticks units of two suppliers (PART-D of supplier 50330 is not in the workbook)
await search();
await unitRow('PART-X', '17-Oct').locator('input[type=checkbox]').first().check();
await unitRow('PART-D', '17-Oct').locator('input[type=checkbox]').first().check();
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_05e_supplier_conflict');
await pg.getByRole('button', { name: 'OK' }).click();
// supplier: cases 1-4 → case list, PO detail, confirm, submit = ASN0003 of the workbook
await view('Supplier'); await search();
await unitRow('PART-X', '17-Oct').locator('input[type=checkbox]').first().check();
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_06_case_list');
await pg.getByTitle('PO detail').nth(1).click(); await shot('c_07_case_expand');
await pg.getByRole('button', { name: 'Submit ASN' }).click(); await shot('c_08_confirm');
await pg.getByRole('button', { name: 'Yes, submit' }).click(); await pg.waitForTimeout(300);
await pg.screenshot({ path: `${dir}/c_09_submit_id.png`, clip: { x: 250, y: 0, width: 1190, height: 330 } });
await search(); await shot('c_10_list_after');
await pg.waitForTimeout(1700);
await pg.goto(url + '#/asn-inquiry'); await pg.waitForTimeout(600); await shot('c_11_inquiry');
await pg.locator('a', { hasText: 'ASN0003' }).click(); await shot('c_12_inquiry_detail');
await pg.goto(url + '#/log-monitoring'); await pg.waitForTimeout(600); await shot('c_13_log_monitoring');
// XD11 Change Order Number (D/S team)
await pg.goto(url + '#/change-order'); await pg.waitForTimeout(600); await shot('x_01_change_order_list');
await pg.getByTitle('Replacement').first().click(); await shot('x_02_change_order_detail');
await pg.getByRole('button', { name: 'Change Order Number', exact: true }).click(); await shot('x_03_change_order_confirm');
await pg.getByRole('button', { name: 'Yes, change' }).click(); await shot('x_04_change_order_after');
await b.close();
