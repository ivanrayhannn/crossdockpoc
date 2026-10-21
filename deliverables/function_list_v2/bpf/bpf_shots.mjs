// Diagram PNG per flow from the prototype page Business Process Flow, in document names (G-System / NSP).
// Usage: node bpf_shots.mjs http://localhost:5179/crossdockpoc/ ./shots
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [url, dir] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const pg = await b.newPage({ viewport: { width: 1700, height: 1000 }, deviceScaleFactor: 2 });
await pg.goto(url + '#/bpf'); await pg.waitForTimeout(800);
await pg.getByLabel('Names').selectOption('doc');
for (const id of ['F1', 'F2', 'F3']) {
  await pg.getByRole('button', { name: new RegExp(`^${id} `) }).click(); await pg.waitForTimeout(300);
  await pg.locator('#bpf-diagram').screenshot({ path: `${dir}/${id}.png` });
}
await pg.getByLabel('Names').selectOption('proto');
await pg.getByRole('button', { name: /^F2 / }).click(); await pg.waitForTimeout(200);
await pg.screenshot({ path: `${dir}/page_F2.png`, fullPage: true });
await b.close();
