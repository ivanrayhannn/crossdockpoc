// Data of the SQL Studio: the simulation engine (engine.js, same rules as SP_STG_WRITE / SP_STG_SYNC and the views) runs the timeline
// (timeline.js: six [Sync] runs with OPERATION_TYPE 1 to 5, then changes still waiting) and writes studio_data.json.
// Run: node gen_data.cjs
const fs = require('fs'), path = require('path');
const src = ['engine.js', 'timeline.js'].map((f) => fs.readFileSync(path.join(__dirname, f), 'utf8')).join('\n') + '\nreturn OUT;';
const out = new Function(src)();
fs.writeFileSync(path.join(__dirname, 'studio_data.json'), JSON.stringify(out, null, 1));
console.log('runs', out.RUNS.length, 'kanban', out.K.length, 'export', out.E.length, 'gtopas', out.G.length);
