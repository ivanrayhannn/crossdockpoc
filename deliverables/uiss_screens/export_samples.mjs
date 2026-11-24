// Export Excel files of XD01 from the prototype, used for the sample sheets of the XD01 UISS
// (Export / Upload Kanban Crossdock Master, Export / Upload Mapping).
// Usage: node export_samples.mjs http://localhost:5179/crossdockpoc/ <out dir>
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1740, height: 1120 }, acceptDownloads: true });
const pg = await ctx.newPage();
await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(900);
await pg.getByRole('button', { name: /^Kanban Crossdock Master/ }).click(); await pg.waitForTimeout(500);
async function exp(name) {
  const [dl] = await Promise.all([pg.waitForEvent('download'), pg.getByRole('button', { name: /^Export Excel/ }).first().click()]);
  await dl.saveAs(`${dir}/${name}.xlsx`);
}
await exp('kanban');
await pg.goto('about:blank'); await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(900);
await pg.getByRole('button', { name: /^Export Crossdock Master/ }).click(); await pg.waitForTimeout(500);
await pg.locator('select').nth(1).selectOption({ label: 'All' });
await pg.getByRole('button', { name: 'Search', exact: true }).click(); await pg.waitForTimeout(300);
await exp('mapping');
await b.close();
