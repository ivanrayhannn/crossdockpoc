// Dump the steps of Staging_Per_Target_Full_Flow.html (engine in the page) to stg_flow_steps.json.
// Run: node dump_stg_flow.cjs   (Playwright with Chromium)
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.route(/fonts\./, (r) => r.abort());
  await p.goto('file://' + path.join(__dirname, 'Staging_Per_Target_Full_Flow.html'));
  const data = await p.evaluate(() => ({ steps: STEPS, learn: LEARN, dest: DEST, user: USER }));
  fs.writeFileSync(path.join(__dirname, 'stg_flow_steps.json'), JSON.stringify(data, null, 1));
  await b.close();
})();
