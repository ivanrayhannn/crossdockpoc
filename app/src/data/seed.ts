import type { HistoryEvent, Part } from '../types';

export const DESTS = ['Thailand', 'Jepang', 'Vietnam'];

export const DOTS: Record<string, string> = {
  Thailand: 'var(--color-accent)',
  Jepang: 'var(--color-accent-2-500)',
  Vietnam: 'var(--color-neutral-500)',
};

export const DCODE: Record<string, string> = {
  Thailand: '123',
  Jepang: '456',
  Vietnam: '789',
};

export const CUR_PER = 'Sep 2026';

/** Periods available in the simulated data, oldest first — drives the
 * "Periode" filter on the Mapping per Destinasi sub-screen. */
export const PERIODS = ['Aug 2026', 'Sep 2026'];

const EDITORS = ['A. Wibowo', 'R. Pratama', 'S. Hartono', 'D. Anggraini', 'L. Kusuma', 'M. Santoso', 'F. Rahman', 'N. Puspita'];

/** Dummy master-part catalog for the "Tambah part" Part No dropdown — Part
 * Name auto-fills from whichever entry is picked. */
export const MASTER_PARTS: { no: string; name: string }[] = [
  { no: 'PART-M01', name: 'Bracket Mounting M01' },
  { no: 'PART-M02', name: 'Gasket Seal M02' },
  { no: 'PART-M03', name: 'Sensor Housing M03' },
  { no: 'PART-M04', name: 'Bearing Assembly M04' },
  { no: 'PART-M05', name: 'Valve Body M05' },
  { no: 'PART-M06', name: 'Hose Connector M06' },
  { no: 'PART-M07', name: 'Relay Switch M07' },
  { no: 'PART-M08', name: 'Spring Coil M08' },
  { no: 'PART-M09', name: 'Cover Plate M09' },
  { no: 'PART-M10', name: 'Filter Cartridge M10' },
  { no: 'PART-M11', name: 'Clamp Ring M11' },
  { no: 'PART-M12', name: 'Nozzle Tip M12' },
  { no: 'PART-M13', name: 'Panel Frame M13' },
  { no: 'PART-M14', name: 'Pump Rotor M14' },
  { no: 'PART-M15', name: 'Mount Base M15' },
];

const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function fmtDate(d: Date): string {
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${dd}-${MON[d.getMonth()]}-${d.getFullYear()} ${hh}:${mi}`;
}

/** Small deterministic PRNG so the simulated dataset is stable across reloads. */
function mulberry32(seed: number) {
  let s = seed;
  return function rnd() {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashStr(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return h >>> 0;
}

function makeRng(seed: number) {
  const rnd = mulberry32(seed);
  return {
    int(min: number, max: number) {
      return Math.floor(rnd() * (max - min + 1)) + min;
    },
    pick<T>(arr: T[]): T {
      return arr[Math.floor(rnd() * arr.length)];
    },
    chance(p: number) {
      return rnd() < p;
    },
  };
}

export const MONTHS = ['Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu'];

interface SeedPart {
  p: string;
  n: string;
  pc: number;
  mc: number;
  st: 'Active' | 'Inactive';
  cat: 'Crossdock' | 'Non-Crossdock';
  mad: number[];
  minMad: number;
  by: string;
  dt: string;
  dests: { d: string; al: number; st: 'Active' | 'Inactive' }[];
  per: string;
  gt: boolean;
  pole: boolean;
}

const SEED: SeedPart[] = [
  {
    p: 'PART-A', n: 'Dummy Part A', pc: 60, mc: 24, st: 'Active', cat: 'Crossdock',
    mad: [1180, 1240, 1310, 1290, 1420, 1380], minMad: 800, by: 'A. Wibowo', dt: '05-Aug-2026 09:12',
    dests: [{ d: 'Thailand', al: 12, st: 'Active' }, { d: 'Jepang', al: 8, st: 'Active' }, { d: 'Vietnam', al: 4, st: 'Active' }],
    per: 'Sep 2026', gt: true, pole: true,
  },
  {
    p: 'PART-B', n: 'Dummy Part B', pc: 12, mc: 40, st: 'Active', cat: 'Crossdock',
    mad: [640, 700, 720, 810, 760, 790], minMad: 500, by: 'R. Pratama', dt: '11-Aug-2026 16:41',
    dests: [{ d: 'Jepang', al: 25, st: 'Active' }, { d: 'Vietnam', al: 15, st: 'Active' }],
    per: 'Aug 2026', gt: true, pole: false,
  },
  {
    p: 'PART-C', n: 'Dummy Part C', pc: 10, mc: 30, st: 'Active', cat: 'Crossdock',
    mad: [220, 260, 240, 300, 280, 310], minMad: 200, by: 'R. Pratama', dt: '12-Aug-2026 08:05',
    dests: [{ d: 'Vietnam', al: 18, st: 'Active' }],
    per: 'Sep 2026', gt: false, pole: false,
  },
  {
    p: 'PART-D', n: 'Dummy Part D', pc: 24, mc: 36, st: 'Active', cat: 'Crossdock',
    mad: [980, 1020, 940, 1100, 1060, 1150], minMad: 800, by: 'A. Wibowo', dt: '05-Aug-2026 09:12',
    dests: [{ d: 'Thailand', al: 20, st: 'Active' }, { d: 'Jepang', al: 16, st: 'Active' }],
    per: 'Aug 2026', gt: false, pole: true,
  },
  {
    p: 'PART-E', n: 'Dummy Part E', pc: 4, mc: 45, st: 'Active', cat: 'Non-Crossdock',
    mad: [140, 120, 90, 110, 80, 60], minMad: 200, by: 'S. Hartono', dt: '05-Aug-2026 09:12',
    dests: [{ d: 'Jepang', al: 25, st: 'Active' }, { d: 'Thailand', al: 20, st: 'Active' }],
    per: 'Aug 2026', gt: true, pole: true,
  },
  {
    p: 'PART-F', n: 'Dummy Part F', pc: 40, mc: 26, st: 'Active', cat: 'Crossdock',
    mad: [480, 520, 560, 540, 610, 650], minMad: 400, by: 'R. Pratama', dt: '08-Aug-2026 11:03',
    dests: [{ d: 'Vietnam', al: 12, st: 'Active' }, { d: 'Thailand', al: 8, st: 'Active' }, { d: 'Jepang', al: 6, st: 'Inactive' }],
    per: 'Sep 2026', gt: true, pole: false,
  },
  {
    p: 'PART-G', n: 'Dummy Part G', pc: 50, mc: 22, st: 'Active', cat: 'Non-Crossdock',
    mad: [60, 40, 70, 30, 20, 10], minMad: 150, by: 'R. Pratama', dt: '12-Aug-2026 08:11',
    dests: [],
    per: 'Sep 2026', gt: false, pole: false,
  },
  {
    p: 'PART-H', n: 'Dummy Part H', pc: 10, mc: 32, st: 'Inactive', cat: 'Crossdock',
    mad: [860, 900, 840, 780, 820, 800], minMad: 600, by: 'S. Hartono', dt: '05-Aug-2026 09:12',
    dests: [{ d: 'Thailand', al: 20, st: 'Active' }, { d: 'Jepang', al: 12, st: 'Inactive' }],
    per: 'Sep 2026', gt: true, pole: true,
  },
];

/** Fabricates PART-009..PART-050 so the Daftar Part list has ~50 rows (2 pages
 * at 25/page) to exercise pagination and per-period filtering realistically. */
function generateBulkParts(): SeedPart[] {
  const rng = makeRng(20260901);
  const out: SeedPart[] = [];
  for (let i = 9; i <= 50; i++) {
    const id = String(i).padStart(3, '0');
    const cat: SeedPart['cat'] = rng.chance(0.7) ? 'Crossdock' : 'Non-Crossdock';
    const st: SeedPart['st'] = rng.chance(0.85) ? 'Active' : 'Inactive';
    const pc = rng.int(4, 60);
    const mc = rng.int(15, 50);
    const minMad = rng.int(100, 900);
    const madBase = rng.int(80, 1400);
    const mad = Array.from({ length: 6 }, () => Math.max(0, madBase + rng.int(-140, 140)));
    const per = rng.chance(0.6) ? CUR_PER : 'Aug 2026';
    const gt = rng.chance(0.55);
    const pole = rng.chance(0.5);
    const by = rng.pick(EDITORS);
    const dtMonth = per === CUR_PER ? 8 : 7; // Sep-period parts were last touched in Aug; Aug-period parts in Jul
    const dt = fmtDate(new Date(2026, dtMonth, rng.int(1, 27), rng.int(8, 17), rng.int(0, 59)));

    const destCount = rng.pick([0, 1, 1, 2, 2, 2, 3]);
    const chosen = [...DESTS].sort(() => rng.int(0, 1) - 0.5).slice(0, destCount);
    const mode = rng.pick(['match', 'under', 'over']);
    const target = mode === 'match' ? mc : mode === 'under' ? Math.max(0, mc - rng.int(2, 10)) : mc + rng.int(2, 10);
    const dests: SeedPart['dests'] = [];
    let remaining = target;
    chosen.forEach((d, idx) => {
      const isLast = idx === chosen.length - 1;
      const al = isLast ? Math.max(0, remaining) : Math.max(0, Math.round(remaining / (chosen.length - idx) + rng.int(-3, 3)));
      remaining -= al;
      dests.push({ d, al, st: rng.chance(0.9) ? 'Active' : 'Inactive' });
    });

    out.push({
      p: `PART-${id}`,
      n: `Dummy Part ${id}`,
      pc, mc, st, cat, mad, minMad, by, dt, dests, per, gt, pole,
    });
  }
  return out;
}

const ALL_SEED: SeedPart[] = [...SEED, ...generateBulkParts()];

/** Builds a plausible change history for one part, newest-first — status
 * flips, Pcs/Case / Min MAD / Max Case/Day edits, and the Total Pcs/Day
 * that falls out of Pcs/Case × Max Case/Day whenever either one moves. */
function genHistoryFor(part: SeedPart): HistoryEvent[] {
  const rng = makeRng(hashStr(part.p) ^ 0x9e3779b9);
  const monthCap = part.per === CUR_PER ? 8 : 7; // never later than the part's own last-touched month
  const genesisDate = new Date(2026, 5, rng.int(1, 27), rng.int(8, 17), rng.int(0, 59));
  const events: { date: Date; t: string; f: string; o: string; n: string; by: string }[] = [];

  events.push({ date: genesisDate, t: 'Part didaftarkan', f: 'Status', o: '—', n: 'Active', by: rng.pick(EDITORS) });

  const dayBetween = () => new Date(2026, rng.int(6, monthCap), rng.int(1, 26), rng.int(8, 17), rng.int(0, 59));

  const pcChanged = rng.chance(0.5);
  const mcChanged = rng.chance(0.55);
  const minMadChanged = rng.chance(0.4);
  const stChanged = part.st === 'Inactive' ? true : rng.chance(0.15);

  if (pcChanged) {
    const oldPc = Math.max(1, part.pc + (rng.chance(0.5) ? 1 : -1) * rng.int(2, 10));
    events.push({ date: dayBetween(), t: 'Pcs/Case diubah', f: 'Pcs/Case', o: String(oldPc), n: String(part.pc), by: rng.pick(EDITORS) });
  }

  if (mcChanged) {
    const oldMc = Math.max(5, part.mc + (rng.chance(0.5) ? 1 : -1) * rng.int(2, 12));
    events.push({ date: dayBetween(), t: 'Max Case/Day diubah', f: 'Max Case/Day', o: String(oldMc), n: String(part.mc), by: rng.pick(EDITORS) });
  }

  if (minMadChanged) {
    const oldMinMad = Math.max(50, part.minMad + (rng.chance(0.5) ? 1 : -1) * rng.int(50, 200));
    events.push({ date: dayBetween(), t: 'Min MAD diubah', f: 'Min MAD', o: String(oldMinMad), n: String(part.minMad), by: rng.pick(EDITORS) });
  }

  if (stChanged) {
    const o = part.st === 'Inactive' ? 'Active' : 'Inactive';
    events.push({ date: dayBetween(), t: 'Status diubah', f: 'Status', o, n: part.st, by: rng.pick(EDITORS) });
  }

  events.sort((a, b) => a.date.getTime() - b.date.getTime());
  return events
    .map((e, i): HistoryEvent => ({ t: e.t, f: e.f, o: e.o, n: e.n, by: e.by, w: fmtDate(e.date), accent: i === events.length - 1 ? 1 : 0 }))
    .reverse();
}

export const HIST_BY_PART: Record<string, HistoryEvent[]> = Object.fromEntries(ALL_SEED.map((p) => [p.p, genHistoryFor(p)]));

/** Fresh copy of the seed data, as the mockup's clone() did. */
export function cloneSeedParts(): Part[] {
  return ALL_SEED.map((p) => ({
    ...p,
    dests: p.dests.map((d) => ({ ...d, cd: DCODE[d.d] || '' })),
  }));
}

export function blankPart(): Part {
  return {
    p: '', n: '', pc: '', mc: '', st: 'Active', cat: 'Crossdock', mad: [], minMad: '',
    per: CUR_PER, gt: false, pole: false, by: 'D. Anggraini', dt: 'sekarang', dests: [],
  };
}
