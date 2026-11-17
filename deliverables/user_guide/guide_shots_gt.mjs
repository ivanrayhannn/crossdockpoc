// Screenshots of the NSP prototype (Crossdock Master Setting) for the GTOPAS user guide (XD06): the whole list of the ongoing period.
// Usage: node guide_shots_gt.mjs http://localhost:5179/crossdockpoc/ ./shots_gt ./dl_gt
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir, dl] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
const pg = await ctx.newPage();
const mark = async (loc) => { await loc.evaluate((el) => { el.dataset.guide = '1'; el.style.outline = '3px solid #D32F2F'; el.style.outlineOffset = '3px'; }); };
const unmark = () => pg.evaluate(() => document.querySelectorAll('[data-guide]').forEach((el) => { el.style.outline = ''; delete el.dataset.guide; }));
const shot = async (name) => { await pg.waitForTimeout(350); await pg.screenshot({ path: `${dir}/${name}.png` }); await unmark(); };
const btn = (n) => pg.getByRole('button', { name: n, exact: true }).first();
await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(1000);
await pg.getByRole('button', { name: /^Mapping per Destination/ }).click(); await pg.waitForTimeout(600);
await mark(pg.getByText('Crossdock Master Setting', { exact: true }).first()); await mark(btn('Mapping per Destination')); await shot('g1_map_menu');
const sel = pg.locator('select');
const ongoing = await sel.nth(0).locator('option').filter({ hasText: 'ongoing' }).first().getAttribute('value');
await sel.nth(0).selectOption(ongoing); await sel.nth(1).selectOption('all');
await btn('Search').click(); await pg.waitForTimeout(500);
const syncBtn = pg.getByRole('button', { name: /^Sync/ }).first();
await mark(sel.nth(0)); await mark(sel.nth(1)); await mark(syncBtn); await shot('g2_map_sync');
await syncBtn.click(); await pg.waitForTimeout(400);
await btn('Search').click(); await pg.waitForTimeout(500);
await mark(pg.locator('th', { hasText: 'Sync Status' }).first()); await mark(btn('Export Excel')); await shot('g3_map_export');
const [d] = await Promise.all([pg.waitForEvent('download'), btn('Export Excel').click()]);
await d.saveAs(`${dl}/${d.suggestedFilename()}`); console.log('downloaded', d.suggestedFilename());
await b.close();
