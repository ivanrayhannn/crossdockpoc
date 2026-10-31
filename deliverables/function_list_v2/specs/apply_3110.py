"""31-Oct: FB-101 the re-send after Failed is described with the current concept (GTOPAS gets only the differences,
AP POLE gets the complete set again) instead of 'replace is repeatable'."""
import json

NEW = '(repeatable: GTOPAS only gets the differences, AP POLE gets the complete set again)'


def replace_text(o, old, new):
    if isinstance(o, dict):
        return {k: replace_text(v, old, new) for k, v in o.items()}
    if isinstance(o, list):
        return [replace_text(v, old, new) for v in o]
    return o.replace(old, new) if isinstance(o, str) else o


for fid, pairs in (('XD01', [('(replace is repeatable)', NEW)]),
                   ('XD07', [('the next [Sync] sends the part again to both targets; replace is repeatable)',
                              'the next [Sync] sends the part again to both targets; repeatable, AP POLE gets the complete set again)')])):
    with open(f'{fid}_spec.json') as f:
        s = json.load(f)
    for old, new in pairs:
        s = replace_text(s, old, new)
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)
