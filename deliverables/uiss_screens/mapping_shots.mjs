// Screenshots of XD01 tab Mapping per Destination (UISS layout pages 15-30) from the prototype; content area only (sidebar clipped).
// Usage: node mapping_shots.mjs http://localhost:5179/crossdockpoc/ ./mapping
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const CLIP = { x: 250, y: 52, width: 1190, height: 848 };

async function page() {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(900);
  await pg.getByRole('button', { name: /^Mapping per Destination/ }).click(); await pg.waitForTimeout(500);
  return pg;
}
const shot = async (pg, name) => { await pg.waitForTimeout(350); await pg.screenshot({ path: `${dir}/${name}.png`, clip: CLIP }); await pg.context().close(); };
const period = (pg, v) => pg.locator('select').nth(0).selectOption({ label: v });
const sync = (pg, v) => pg.locator('select').nth(1).selectOption({ label: v });
const partNo = (pg, v) => pg.getByPlaceholder('e.g. PART-B').fill(v);
const search = async (pg) => { await pg.getByRole('button', { name: 'Search', exact: true }).click(); await pg.waitForTimeout(300); };
const expand = async (pg, i = 0) => { await pg.getByTitle('Destination details').nth(i).click(); await pg.waitForTimeout(300); };
const edit = async (pg) => { await pg.getByRole('button', { name: 'Edit mapping', exact: true }).first().click(); await pg.waitForTimeout(300); };
async function one(pg, part, s = 'All', per) { if (per) await period(pg, per); await sync(pg, s); await partNo(pg, part); await search(pg); await expand(pg); }

let pg = await page(); await shot(pg, 'c_01_default');
pg = await page(); await sync(pg, 'All'); await search(pg); await shot(pg, 'c_02_sync_all');
pg = await page(); await period(pg, 'Aug 2026'); await sync(pg, 'All'); await search(pg); await shot(pg, 'c_03_past_period');
pg = await page(); await sync(pg, 'All'); await partNo(pg, 'PART-ZZZ'); await search(pg); await shot(pg, 'c_04_no_result');
pg = await page(); await one(pg, 'PART-C'); await shot(pg, 'c_05_details_view');
pg = await page(); await one(pg, 'PART-B', 'No Sync', 'Aug 2026'); await shot(pg, 'c_06_details_past');
pg = await page(); await one(pg, 'PART-C'); await edit(pg); await shot(pg, 'c_07_edit_mode');
pg = await page(); await one(pg, 'PART-C'); await edit(pg); await pg.locator('td input.input').last().fill('50'); await shot(pg, 'c_08_over_allocation');
pg = await page(); await one(pg, 'PART-F'); await edit(pg); await pg.getByRole('button', { name: /Add destination/ }).click(); await shot(pg, 'c_09_missing_destination');
pg = await page(); await one(pg, 'PART-G'); await shot(pg, 'c_10_no_destination');
pg = await page(); await one(pg, 'PART-A'); await edit(pg); await pg.getByRole('button', { name: 'Split evenly' }).click(); await shot(pg, 'c_11_split_evenly');
pg = await page(); await expand(pg); await shot(pg, 'c_12_before_sync');
pg = await page(); await pg.getByRole('button', { name: /^Sync \(/ }).click(); await pg.waitForTimeout(600);
const ok = pg.getByRole('button', { name: 'OK', exact: true }); if (await ok.count()) await ok.first().click();
await sync(pg, 'All'); await search(pg); await expand(pg, 0); await expand(pg, 1); await shot(pg, 'c_13_after_sync');
pg = await page(); await sync(pg, 'All'); await partNo(pg, 'PART-ZZZ'); await search(pg); await pg.getByRole('button', { name: 'Upload Excel' }).first().click(); await shot(pg, 'c_14_upload');
pg = await page(); await sync(pg, 'All'); await partNo(pg, 'PART-ZZZ'); await search(pg); await pg.getByRole('button', { name: 'Upload Excel' }).first().click(); await pg.waitForTimeout(300); await pg.getByRole('button', { name: 'Validate file' }).click(); await shot(pg, 'c_15_upload_success');
pg = await page(); await sync(pg, 'All'); await partNo(pg, 'PART-ZZZ'); await search(pg); await pg.getByRole('button', { name: 'Run calculation' }).click(); await pg.waitForTimeout(1500); await shot(pg, 'c_16_calc_success');
await b.close();
