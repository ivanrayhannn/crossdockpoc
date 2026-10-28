// Screenshots of XD01 tab Part List (UISS layout pages 1-14) from the prototype; content area only (sidebar clipped).
// Usage: node part_list_shots.mjs http://localhost:5179/crossdockpoc/ ./part_list
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const CLIP = { x: 250, y: 52, width: 1190, height: 848 };

async function page() {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(900);
  await pg.getByRole('button', { name: /^Part List/ }).click(); await pg.waitForTimeout(500);
  return pg;
}
const shot = async (pg, name) => { await pg.waitForTimeout(350); await pg.screenshot({ path: `${dir}/${name}.png`, clip: CLIP }); await pg.context().close(); };
const search = (pg) => pg.getByRole('button', { name: 'Search', exact: true }).click();
const partNo = (pg, v) => pg.getByPlaceholder('e.g. PART-B').fill(v);
const openAdd = (pg) => pg.getByRole('button', { name: 'Add Part' }).first().click();
const modal = (pg) => pg.locator('div').filter({ hasText: /^(Add Part Candidate Crossdock|Edit part data)/ }).last();
const num = (pg, i) => pg.locator('input[placeholder="0"]').nth(i);

async function openEdit(pg, part) {
  await partNo(pg, part); await search(pg); await pg.waitForTimeout(300);
  await pg.getByRole('button', { name: 'Edit', exact: true }).first().click(); await pg.waitForTimeout(300);
}

let pg = await page(); await shot(pg, 'c_01_initial');
pg = await page(); await pg.locator('select').first().selectOption('candidate'); await search(pg); await shot(pg, 'c_02_filter_candidate');
pg = await page(); await partNo(pg, 'PART-ZZZ'); await search(pg); await shot(pg, 'c_03_no_result');
pg = await page(); await openAdd(pg); await shot(pg, 'c_04_add_empty');
pg = await page(); await openAdd(pg); await pg.getByPlaceholder('Select Part Number').click(); await shot(pg, 'c_05_add_partno_list');
pg = await page(); await openAdd(pg); await pg.getByPlaceholder('Select Part Number').fill('XYZ'); await shot(pg, 'c_06_add_partno_notfound');

async function addFilled(pg) {
  await openAdd(pg);
  const cb = pg.getByPlaceholder('Select Part Number'); await cb.click(); await cb.fill('PART-M01'); await pg.waitForTimeout(200);
  await pg.getByText('PART-M01', { exact: true }).last().click(); await pg.waitForTimeout(200);
  await num(pg, 0).fill('300'); await num(pg, 1).fill('20'); await num(pg, 2).fill('15');
}
pg = await page(); await addFilled(pg); await shot(pg, 'c_07_add_filled');
pg = await page(); await addFilled(pg); await pg.getByRole('button', { name: 'Save', exact: true }).click(); await shot(pg, 'c_08_save_success');
pg = await page(); await openEdit(pg, 'PART-I'); await shot(pg, 'c_09_edit_candidate');
pg = await page(); await openEdit(pg, 'PART-A'); await shot(pg, 'c_10_edit_active');
pg = await page(); await partNo(pg, 'PART-A'); await search(pg); await pg.getByTitle('History').first().click(); await shot(pg, 'c_11_history');
pg = await page(); await pg.getByRole('button', { name: 'Upload Excel' }).first().click(); await shot(pg, 'c_12_upload');
pg = await page(); await pg.getByRole('button', { name: 'Upload Excel' }).first().click(); await pg.getByRole('button', { name: 'Validate file' }).click(); await shot(pg, 'c_13_upload_success');
pg = await page(); await openEdit(pg, 'PART-A'); await num(pg, 2).fill('20'); await shot(pg, 'c_14_edit_below_mapped');
await b.close();
