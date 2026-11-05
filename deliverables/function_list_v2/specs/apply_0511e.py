"""05-Nov (3): FB-129 the replicated H0253 rows (UPD_STATUS 6 / 2) are kept without retention limit (no housekeeping);
FB-144 the prototype lists every Active part in the ongoing period: Sync (17) in the XD01 screen layout captions."""
import glob, json


def rep(o, pairs):
    if isinstance(o, dict):
        return {k: rep(v, pairs) for k, v in o.items()}
    if isinstance(o, list):
        return [rep(v, pairs) for v in o]
    if isinstance(o, str):
        for a, b in pairs:
            o = o.replace(a, b)
    return o


PAIRS = [('are kept for tracking (retention optional, TBC)', 'are kept for tracking, without retention limit (no housekeeping, decided 5-Nov)'),
         ('26. Before Sync - Sync (9): 4 No Sync + 5 Failed Active parts of the ongoing period',
          '26. Before Sync - Sync (17): 11 No Sync + 6 Failed Active parts of the ongoing period'),
         ('27. After Sync - the 9 parts are Waiting for XD06 / XD07', '27. After Sync - the 17 parts are Waiting for XD06 / XD07'),
         ('The label shows the number of parts, e.g. Sync (9).', 'The label shows the number of parts, e.g. Sync (17).')]
for f in sorted(glob.glob('XD*_spec.json')):
    with open(f) as fh:
        s = json.load(fh)
    t = rep(s, PAIRS)
    if t != s:
        with open(f, 'w') as fh:
            json.dump(t, fh, indent=1, ensure_ascii=False)
        print('patched', f)
