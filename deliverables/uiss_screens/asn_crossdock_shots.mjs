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

await pg.goto(url + '#/asn-creation'); await pg.waitForTimeout(800);
await shot('c_01_initial');
await search(); await shot('c_02_delivery_plan');
// D/S team: destination detail and customer orders of PART-A 14-Oct
await view('D/S team'); await search();
await unitRow('PART-A', '14-Oct').getByTitle('Destination detail (D/S team)').click();
await pg.getByTitle('Customer orders').first().click(); await shot('c_03_ds_detail');
// hold Thailand of PART-A 14-Oct: scan order and cases are computed again without TH
await pg.getByRole('button', { name: 'N · Hold' }).nth(1).click(); await shot('c_04_ds_hold');
await pg.getByRole('button', { name: 'Y · Release' }).click();
// supplier: tick case 2 of PART-A (MSG10, cases 1-3) and the unit PART-C 13-Oct
await view('Supplier'); await search();
await unitRow('PART-C', '13-Oct').locator('input[type=checkbox]').first().check();
await caseBox(/Cases 2-3 are sent together/).check(); await shot('c_05_selected');
// D/S team (other session) holds Thailand of the ticked unit PART-A
await view('D/S team'); await search();
await unitRow('PART-A', '14-Oct').getByTitle('Destination detail (D/S team)').click();
await pg.getByRole('button', { name: 'N · Hold' }).nth(1).click(); await shot('c_05a_ds_hold_other_session');
await view('Supplier');
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_05c_hold_conflict');
await pg.getByRole('button', { name: 'OK' }).click(); await shot('c_05d_after_refresh');
await view('D/S team');
await unitRow('PART-A', '14-Oct').getByTitle('Destination detail (D/S team)').click();
await pg.getByRole('button', { name: 'Y · Release' }).click();
// D/S team ticks units of two suppliers
await search();
await unitRow('PART-C', '13-Oct').locator('input[type=checkbox]').first().check();
await unitRow('PART-D', '13-Oct').locator('input[type=checkbox]').first().check();
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_05e_supplier_conflict');
await pg.getByRole('button', { name: 'OK' }).click();
// supplier: case list, PO detail, confirm, submit
await view('Supplier'); await search();
await caseBox(/Cases 2-3 are sent together/).check();
await unitRow('PART-C', '13-Oct').locator('input[type=checkbox]').first().check();
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_06_case_list');
await pg.getByTitle('PO detail').nth(1).click(); await shot('c_07_case_expand');
await pg.getByRole('button', { name: 'Submit ASN' }).click(); await shot('c_08_confirm');
await pg.getByRole('button', { name: 'Yes, submit' }).click(); await pg.waitForTimeout(300);
await pg.screenshot({ path: `${dir}/c_09_submit_id.png`, clip: { x: 250, y: 0, width: 1190, height: 330 } });
await search(); await shot('c_10_list_after');
await pg.waitForTimeout(1700);
await pg.goto(url + '#/asn-inquiry'); await pg.waitForTimeout(600); await shot('c_11_inquiry');
await pg.locator('a', { hasText: 'ASN-50221-261015-001' }).click(); await shot('c_12_inquiry_detail');
await pg.goto(url + '#/log-monitoring'); await pg.waitForTimeout(600); await shot('c_13_log_monitoring');
// XD11 Change Order Number (D/S team)
await pg.goto(url + '#/change-order'); await pg.waitForTimeout(600); await shot('x_01_change_order_list');
await pg.getByTitle('Replacement').first().click(); await shot('x_02_change_order_detail');
await pg.getByRole('button', { name: 'Change Order Number', exact: true }).click(); await shot('x_03_change_order_confirm');
await pg.getByRole('button', { name: 'Yes, change' }).click(); await shot('x_04_change_order_after');
await b.close();
