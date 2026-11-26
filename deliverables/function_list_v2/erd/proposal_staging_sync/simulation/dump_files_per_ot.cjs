// Dump the scenarios of Staging_To_Upload_Files.html (engine in the page) to files_per_ot.json for build_files_per_ot.py.
// Run: node dump_files_per_ot.cjs   (Playwright with Chromium)
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.route(/fonts\./, (r) => r.abort());
  await p.goto('file://' + path.join(__dirname, 'Staging_To_Upload_Files.html'));
  const data = await p.evaluate(() => ({ res: RES.map((x) => ({ ...x, s: { ...x.s, acts: x.s.acts.map((a) => a.slice(0, 3)) } })), dest: DEST, run: RUN, sdt: sdtOf(RUN) }));
  fs.writeFileSync(path.join(__dirname, 'files_per_ot.json'), JSON.stringify(data, null, 1));
  await b.close();
})();
