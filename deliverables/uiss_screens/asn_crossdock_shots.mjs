// Screenshots of ASN Crossdock Creation (XD10), ASN Inquiry and Log Monitoring from the prototype (decided 21-Oct: case check boxes).
// Usage: node asn_crossdock_shots.mjs http://localhost:5179/crossdockpoc/ ./asn_crossdock
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const pg = await b.newPage({ viewport: { width: 1440, height: 900 } });
const shot = async (name) => { await pg.waitForTimeout(250); await pg.screenshot({ path: `${dir}/${name}.png`, fullPage: true }); };
const unitRow = (part, date) => pg.locator('tbody > tr').filter({ has: pg.locator('td', { hasText: new RegExp(`^${part}$`) }) }).filter({ hasText: date });
const caseBox = (title) => pg.locator(`input[type=checkbox][title^="${title}"]`).first();
const view = (who) => pg.getByRole('button', { name: who, exact: true }).click();
const search = () => pg.getByRole('button', { name: 'Search', exact: true }).click();
// Destination detail (Hold Flag per destination) is hidden on the screen for now; shown only for the steps of the destination hold.
const destDetail = (on) => pg.evaluate((v) => window.__axDestDetail(v), on);

// data = simulasi_asn_rev.xlsx, business date 18-Oct (default): PART-X 17-Oct, 5 cases, cases 1-4 Ready, case 5 Short PO
const destHold = (code) => pg.locator('tr').filter({ has: pg.locator('td', { hasText: new RegExp(`^${code} · `) }) }).last().getByRole('button', { name: /Hold|Release/ });
await pg.goto(url + '#/asn-creation'); await pg.waitForTimeout(800);
await shot('c_01_initial');
await search(); await shot('c_02_delivery_plan');
// click the ASN status of a partially ready unit: PO information in Indonesian
await pg.getByRole('button', { name: 'Info PO PART-X 17-Oct-2026' }).click(); await shot('c_02a_po_info');
await pg.getByRole('button', { name: 'OK', exact: true }).click();
// D/S team: destination detail and customer orders of PART-X 17-Oct
await view('D/S team'); await search(); await destDetail(true);
await unitRow('PART-X', '17-Oct').getByTitle('Destination detail (D/S team)').click();
await pg.getByTitle('Customer orders').first().click(); await shot('c_03_ds_detail');
// hold Japan (CO-14104) of PART-X 17-Oct: scan order and cases are computed again without TH
await destHold('9722D10').click(); await shot('c_04_ds_hold');
await destHold('9722D10').click(); await destDetail(false);
// D/S team: Hold per case with Edit / Save at Part Number + Customer Order Date level: Edit hold, tick case 4 (CO-14109 Taiwan), Save -> Taiwan On Hold, its PO goes to Australia (all 4 cases Ready)
// [Save] asks for confirmation, then shows the saved message; the delivery plan is refreshed behind it.
const confirmSave = async (askShot, doneShot) => {
  if (askShot) await shot(askShot);
  await pg.getByRole('button', { name: 'Yes, save' }).click();
  if (doneShot) await shot(doneShot);
  await pg.getByRole('button', { name: 'OK', exact: true }).click();
};
const saveCases = async (askShot, doneShot) => {
  await pg.locator('td').filter({ has: pg.getByRole('button', { name: 'Cancel', exact: true }) }).last().getByRole('button', { name: 'Save', exact: true }).click();
  await confirmSave(askShot, doneShot);
};
await pg.getByRole('button', { name: 'Edit hold of PART-X 17-Oct-2026' }).click();
await pg.getByRole('checkbox', { name: 'Hold case 4 of PART-X 17-Oct-2026' }).check(); await shot('c_04a_ds_case_edit');
await saveCases('c_04g_ds_hold_confirm', 'c_04h_ds_hold_saved'); await shot('c_04b_ds_reduce');
await view('Supplier'); await search(); await shot('c_04c_supplier_reduce');
await view('D/S team'); await search();
await pg.getByRole('button', { name: 'Edit hold of PART-X 17-Oct-2026' }).click();
await pg.getByRole('checkbox', { name: 'Hold CO-14109 of PART-X 17-Oct-2026' }).uncheck(); await saveCases();
// D/S team: sub screen Hold per Part Number: Edit, tick Hold, Save on PART-X (no PO information)
await pg.getByRole('button', { name: 'Hold per Part', exact: true }).click(); await shot('c_04d_ds_supplier_hold');
await pg.getByRole('button', { name: 'Edit hold of PART-X' }).click(); await pg.getByRole('checkbox', { name: 'Hold PART-X' }).check();
await pg.getByRole('button', { name: 'Save hold of PART-X' }).click(); await confirmSave(); await shot('c_04f_ds_supplier_hold_on');
await pg.getByRole('button', { name: /Back to ASN Crossdock Creation/ }).click();
await view('Supplier'); await search(); await shot('c_04e_supplier_on_hold');
await view('D/S team'); await pg.getByRole('button', { name: 'Hold per Part', exact: true }).click();
await pg.getByRole('button', { name: 'Edit hold of PART-X' }).click(); await pg.getByRole('checkbox', { name: 'Hold PART-X' }).uncheck();
await pg.getByRole('button', { name: 'Save hold of PART-X' }).click(); await confirmSave(); await pg.getByRole('button', { name: /Back to ASN Crossdock Creation/ }).click();
if (await pg.getByTitle('Destination detail (D/S team)').count()) { const r = unitRow('PART-X', '17-Oct'); if (await r.getByRole('button', { name: '▾' }).count()) await r.getByRole('button', { name: '▾' }).click(); }
// supplier: tick case 3 of PART-X 17-Oct → cases 1-3 selected
await view('Supplier'); await search();
await caseBox('Case 3 can be sent alone').check(); await shot('c_05_selected');
// D/S team (other session) holds Japan of the ticked unit
await view('D/S team'); await search(); await destDetail(true);
await unitRow('PART-X', '17-Oct').getByTitle('Destination detail (D/S team)').click();
await destHold('9722D10').click(); await shot('c_05a_ds_hold_other_session');
await view('Supplier');
await pg.getByRole('button', { name: 'Create ASN' }).click(); await shot('c_05c_hold_conflict');
await pg.getByRole('button', { name: 'OK' }).click(); await shot('c_05d_after_refresh');
await view('D/S team');
await unitRow('PART-X', '17-Oct').getByTitle('Destination detail (D/S team)').click();
await destHold('9722D10').click(); await destDetail(false);
// D/S team ticks units of two suppliers (PART-D of supplier 5002 is not in the workbook)
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
