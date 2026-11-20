// Screenshots of the NSP prototype (Crossdock Master Setting) for the AP POLE user guide: getting the source data of the RPA XD07.
// Usage: node guide_shots_ap.mjs http://localhost:5179/crossdockpoc/ ./shots_ap ./dl_ap
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir, dl] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
let pg;
const mark = async (loc) => { await loc.evaluate((el) => { el.dataset.guide = '1'; el.style.outline = '3px solid #D32F2F'; el.style.outlineOffset = '3px'; }); };
const unmark = () => pg.evaluate(() => document.querySelectorAll('[data-guide]').forEach((el) => { el.style.outline = ''; delete el.dataset.guide; }));
const shot = async (name) => { await pg.waitForTimeout(350); await pg.screenshot({ path: `${dir}/${name}.png` }); await unmark(); };
const btn = (n) => pg.getByRole('button', { name: n, exact: true }).first();
async function open(sub) {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
  pg = await ctx.newPage();
  await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(1000);
  await pg.getByRole('button', { name: new RegExp('^' + sub) }).click(); await pg.waitForTimeout(600);
}
async function download() {
  const [d] = await Promise.all([pg.waitForEvent('download'), btn('Export Excel').click()]);
  await d.saveAs(`${dl}/${d.suggestedFilename()}`); console.log('downloaded', d.suggestedFilename());
}
// 1) Export Crossdock Master (D/S account): [Sync] sets the parts to Waiting, then the file of the Waiting parts is exported
await open('Export Crossdock Master');
await mark(pg.getByText('Crossdock Master Setting', { exact: true }).first()); await mark(btn('Export Crossdock Master')); await shot('n1_map_menu');
const sel = pg.locator('select');
const ongoing = await sel.nth(0).locator('option').filter({ hasText: 'ongoing' }).first().getAttribute('value');
await sel.nth(0).selectOption(ongoing); await sel.nth(1).selectOption('all');
await btn('Search').click(); await pg.waitForTimeout(500);
const syncBtn = pg.getByRole('button', { name: /^Sync/ }).first();
await mark(sel.nth(0)); await mark(syncBtn); await shot('n2_map_sync');
await syncBtn.click(); await pg.waitForTimeout(400);
await sel.nth(1).selectOption('sent');
await btn('Search').click(); await pg.waitForTimeout(500);
await mark(sel.nth(1)); await mark(pg.locator('th', { hasText: 'Sync Status' }).first()); await mark(pg.locator('th', { hasText: 'Last Sent' }).last()); await shot('n3_map_waiting');
// open the destinations of PART-009
await sel.nth(1).selectOption('all'); await pg.getByPlaceholder(/PART/).first().fill('PART-009');
await btn('Search').click(); await pg.waitForTimeout(500);
await pg.locator('tr', { hasText: 'PART-009' }).first().getByTitle('Destination details').click(); await pg.waitForTimeout(500);
await shot('n4_map_dest');
await pg.getByPlaceholder(/PART/).first().fill(''); await sel.nth(1).selectOption('sent');
await btn('Search').click(); await pg.waitForTimeout(500);
await mark(btn('Export Excel')); await shot('n5_map_export');
await download();
// 2) Kanban Crossdock Master: Pcs/Case, Max Case/Day and Status of the parts (same session, so the parts stay Waiting)
await pg.getByRole('button', { name: 'Switch sub-menu' }).click(); await pg.waitForTimeout(500);
await pg.getByRole('button', { name: /^Kanban Crossdock Master/ }).click(); await pg.waitForTimeout(600);
await btn('Search').click(); await pg.waitForTimeout(400);
await mark(btn('Kanban Crossdock Master')); await mark(btn('Export Excel')); await shot('n6_part_export');
await download();
await b.close();
