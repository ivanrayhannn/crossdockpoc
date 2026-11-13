"""13-Nov: destination country names are dummies (Vietnam -> Korea, Thailand -> Japan, Philippines -> Taiwan,
'Destination 982220' -> Australia; short codes VN / TH / PH -> KR / JP / TW). The 7-digit destination codes are unchanged.
Applied last to every spec, so text taken from the first-version specs is covered too."""
import glob, json, re

NAMES = [('Philippines', 'Taiwan'), ('Thailand', 'Japan'), ('Vietnam', 'Korea'), ('Destination 982220', 'Australia')]
SHORT = {'VN': 'KR', 'TH': 'JP', 'PH': 'TW'}


def rep(o):
    if isinstance(o, dict):
        return {k: rep(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rep(v) for v in o]
    if isinstance(o, str):
        for a, b in NAMES:
            o = o.replace(a, b)
        return re.sub(r'\b(VN|TH|PH)\b', lambda m: SHORT[m.group(1)], o)
    return o


for f in sorted(glob.glob('XD*_spec.json')):
    with open(f) as fh:
        s = json.load(fh)
    t = rep(s)
    if t != s:
        with open(f, 'w') as fh:
            json.dump(t, fh, indent=1, ensure_ascii=False)
        print('patched', f)
