// ---------- timeline of the SQL Studio data: several [Sync] runs, each with a mix of OPERATION_TYPE ----------
const DS = 'RSARI', PR = 'DANGGRAINI', XB = 'XD05BATCH';
const RUNS = [];
let cur = '202612', nxt = '202701';
const at = (t) => { now = t; };
function sync(run, label, ots) {
  now = sdtOf(run);
  spSync(run, cur, nxt, DS);
  RUNS.push({ sdt: sdtOf(run), label, ots, sc: rpa.sc, g: rpa.gRows });
  K.concat(E, G).forEach((r) => { if (r.run === run) { r.chb = DS; r.chd = now; } });
}
// XD05 day D (27-Nov) made 202612: three parts Active, DUMMY-004 and DUMMY-005 Candidate
M = { '202611': {}, '202612': {}, '202701': {} };
at('2026-11-27 02:00:00');
xd05('202611', '202612', {
  'DUMMY-001': { st: 'Active', pcs: 12, max: 20, d: { 'JAPAN|**': 12, 'KOREA|**': 8 } },
  'DUMMY-002': { st: 'Active', pcs: 10, max: 16, d: { 'TAIWAN|**': 10, 'USA|**': 6 } },
  'DUMMY-003': { st: 'Active', pcs: 8, max: 10, d: { 'THAILAND|**': 10 } },
  'DUMMY-004': { st: 'Candidate', pcs: 6, max: 20, d: {} },
  'DUMMY-005': { st: 'Candidate', pcs: 4, max: 12, d: {} },
});

sync('20261201090000', 'First sync of 202612: every part never sent', [4]);
// GTOPAS rows of 202612 were sent at the rollover of 01-Dec in reality; here they went with the first run (scenario 1)

at('2026-12-03 09:00:00'); saveMapping(cur, 'DUMMY-001', { 'JAPAN|**': 6, 'KOREA|**': 10 }, DS);
at('2026-12-03 09:30:00'); savePart(cur, 'DUMMY-001', { max: 16 }, PR);
at('2026-12-03 10:00:00'); savePart(cur, 'DUMMY-002', { max: 24 }, PR);
at('2026-12-03 10:20:00'); saveMapping(cur, 'DUMMY-002', { 'TAIWAN|**': 14, 'USA|**': 10 }, DS);
sync('20261203110000', 'DUMMY-001 Max down (1), DUMMY-002 Max up (2)', [1, 2]);

at('2026-12-05 08:30:00'); savePart(cur, 'DUMMY-003', { pcs: 10 }, PR);
at('2026-12-05 09:00:00'); savePart(cur, 'DUMMY-004', { st: 'Active' }, PR);
at('2026-12-05 09:15:00'); saveMapping(cur, 'DUMMY-004', { 'KOREA|**': 12, 'USA|**': 8 }, DS);
at('2026-12-05 09:40:00'); saveMapping(cur, 'DUMMY-002', { 'TAIWAN|**': 14, 'USA|**': 8, 'THAILAND|**': 2 }, DS);
sync('20261205110000', 'DUMMY-003 Pcs/Case only (3), DUMMY-004 new part (4), DUMMY-002 destinations only (5)', [3, 4, 5]);

at('2026-12-08 09:00:00'); saveMapping(cur, 'DUMMY-001', { 'JAPAN|C': 6, 'KOREA|**': 10 }, DS);
at('2026-12-08 09:30:00'); savePart(cur, 'DUMMY-003', { st: 'Inactive' }, PR);
sync('20261208110000', 'DUMMY-001 order type ** → C (5), DUMMY-003 Inactive (5)', [5]);

at('2026-12-10 08:00:00'); saveMapping(cur, 'DUMMY-002', { 'TAIWAN|**': 14, 'USA|**': 6, 'THAILAND|**': 2 }, DS);
at('2026-12-10 08:40:00'); saveMapping(cur, 'DUMMY-002', { 'TAIWAN|**': 14, 'USA|**': 7, 'THAILAND|**': 2 }, DS);
at('2026-12-10 09:00:00'); saveMapping(cur, 'DUMMY-004', { 'KOREA|**': 8, 'USA|**': 6 }, DS);
at('2026-12-10 09:20:00'); savePart(cur, 'DUMMY-004', { max: 14 }, PR);
at('2026-12-10 09:40:00'); savePart(cur, 'DUMMY-005', { st: 'Active' }, PR);
at('2026-12-10 09:50:00'); saveMapping(cur, 'DUMMY-005', { 'JAPAN|**': 7, 'TAIWAN|**': 5 }, DS);
sync('20261210110000', 'DUMMY-002 USA edited twice (5), DUMMY-004 Max down (1), DUMMY-005 new part (4)', [1, 4, 5]);

// XD05 day D 27-Dec: 202701 for every part; OPERATION_TYPE against the Max sent for 202612
at('2026-12-27 02:00:00');
xd05('202612', '202701', {
  'DUMMY-001': { st: 'Active', pcs: 12, max: 18, d: { 'JAPAN|C': 8, 'KOREA|**': 10 } },
  'DUMMY-002': { st: 'Active', pcs: 10, max: 20, d: { 'TAIWAN|**': 12, 'USA|**': 6, 'THAILAND|**': 2 } },
  'DUMMY-003': { st: 'Inactive', pcs: 10, max: 10, d: {} },
  'DUMMY-004': { st: 'Active', pcs: 6, max: 14, d: { 'KOREA|**': 8, 'USA|**': 6 } },
  'DUMMY-005': { st: 'Active', pcs: 4, max: 12, d: { 'JAPAN|**': 7, 'TAIWAN|**': 5 } },
});
sync('20261228100000', 'Next period 202701 by XD05: DUMMY-001 Max up (2), DUMMY-002 Max down (1), others same Max (3)', [1, 2, 3]);

// waiting for the next [Sync]: SYNC_STATUS 0, SYNC_DT NULL
at('2026-12-29 09:00:00'); savePart(cur, 'DUMMY-001', { max: 20 }, PR);
at('2026-12-29 09:20:00'); saveMapping(cur, 'DUMMY-001', { 'JAPAN|C': 8, 'KOREA|**': 12 }, DS);
at('2026-12-29 10:00:00'); saveMapping(cur, 'DUMMY-005', { 'JAPAN|**': 7, 'TAIWAN|**': 3, 'USA|**': 2 }, DS);
const OUT = { K, E, G, RUNS, cur, nxt };
