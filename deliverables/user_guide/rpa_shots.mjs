// NSP screen for the RPA step documents (XD06 / XD07): Export Crossdock Master with the [Sync (n)] button marked (red box).
// Usage: node rpa_shots.mjs http://localhost:5179/crossdockpoc/ ./shots_rpa
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch();
const pg = await (await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 })).newPage();
await pg.goto(url + '#/crossdock'); await pg.waitForTimeout(900);
await pg.getByRole('button', { name: /^Export Crossdock Master/ }).click(); await pg.waitForTimeout(500);
const sync = pg.getByRole('button', { name: /^Sync \(/ });
await sync.evaluate((el) => { el.style.outline = '3px solid #e00000'; el.style.outlineOffset = '3px'; });
await pg.screenshot({ path: `${dir}/r01_nsp_sync.png`, clip: { x: 250, y: 52, width: 1340, height: 640 } });
await b.close();
