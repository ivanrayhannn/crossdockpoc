// Screenshots for the user guide "Download Kanban Crossdock Master / Export Crossdock Master" from the prototype, with the real exported files.
// Usage: node guide_shots.mjs http://localhost:5179/crossdockpoc/ ./shots ./downloads
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir, dl] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
let pg;
const mark = async (loc) => { await loc.evaluate((el) => { el.dataset.guide = '1'; el.style.outline = '3px solid #D32F2F'; el.style.outlineOffset = '3px'; }); };
const unmark = () => pg.evaluate(() => document.querySelectorAll('[data-guide]').forEach((el) => { el.style.outline = ''; delete el.dataset.guide; }));
const shot = async (name) => { await pg.waitForTimeout(350); await pg.screenshot({ path: `${dir}/${name}.png` }); await unmark(); };
const exportBtn = () => pg.getByRole('button', { name: 'Export Excel', exact: true }).first();
// The prototype asks which sub-menu to preview (role); in NSP the account opens its own sub-menu directly.
async function open(sub) {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
  pg = await ctx.newPage();
  await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(1000);
  await pg.getByRole('button', { name: new RegExp('^' + sub) }).click(); await pg.waitForTimeout(600);
}
const tab = (sub) => pg.getByRole('button', { name: sub, exact: true });
async function download() {
  const [d] = await Promise.all([pg.waitForEvent('download'), exportBtn().click()]);
  await d.saveAs(`${dl}/${d.suggestedFilename()}`); console.log('downloaded', d.suggestedFilename());
}

// ---------- Kanban Crossdock Master (Procurement account) ----------
await open('Kanban Crossdock Master');
await mark(pg.getByText('Crossdock Master Setting', { exact: true }).first()); await mark(tab('Kanban Crossdock Master')); await shot('p1_menu');
await mark(pg.getByRole('button', { name: 'Search', exact: true })); await shot('p2_search');
await pg.getByRole('button', { name: 'Search', exact: true }).click(); await pg.waitForTimeout(400);
await mark(exportBtn()); await shot('p3_export');
await download();
await pg.context().close();

// ---------- Export Crossdock Master (D/S account) ----------
await open('Export Crossdock Master');
await mark(pg.getByText('Crossdock Master Setting', { exact: true }).first()); await mark(tab('Export Crossdock Master')); await shot('m1_menu');
const sel = pg.locator('select');
const ongoing = await sel.nth(0).locator('option').filter({ hasText: 'ongoing' }).first().getAttribute('value');
await sel.nth(0).selectOption(ongoing); await sel.nth(1).selectOption({ label: 'All' });
await mark(sel.nth(0)); await mark(pg.getByRole('button', { name: 'Search', exact: true })); await shot('m2_period');
await pg.getByRole('button', { name: 'Search', exact: true }).click(); await pg.waitForTimeout(400);
await mark(exportBtn()); await shot('m3_export');
await download();
await b.close();
