"""Build the User Requirement of one function with the ur-generator skill (.claude/skills/ur-generator):
the same sheets as its UISS, in business wording for business users.

Input : deliverables/function_list_v2/specs/<id>_spec.json (UISS spec), vocab_crossdock.json + phrases_crossdock.json
        (project terms), ur_<id>.py (purpose, business rules, acceptance criteria).
Output: <id>_UR_<Name>.xlsx and <id>_UR_spec.json in this folder.
Usage : python3 build_ur.py XD01"""
import importlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SKILL = os.path.join(ROOT, '.claude', 'skills', 'ur-generator', 'scripts')
sys.path.insert(0, HERE)
sys.path.insert(0, SKILL)
from to_business import convert  # noqa: E402


def build(fid):
    d = importlib.import_module(f'ur_{fid.lower()}')
    spec = json.load(open(os.path.join(HERE, '..', 'specs', f'{fid}_spec.json'), encoding='utf-8'))
    spec['header'] = dict(spec['header'], created_date='28-Oct-26', created_by='FID Rayhan')
    extra = {'purpose': d.PURPOSE, 'business_rules': [list(r) for r in d.BR], 'acceptance': [[a[0], a[1], a[3]] for a in d.AC],
             'internal_fields': ['sync time', 'sync message'],
             'phrases': json.load(open(os.path.join(HERE, 'phrases_crossdock.json'), encoding='utf-8')),
             'revisions': [{'revision': '0.1', 'author': 'FID Rayhan', 'date': '28-Oct-26', 'reviewed_by': '',
                            'description': f'Initial Draft: business version of UISS {d.INFO["uiss"]}'}]}
    ur, left = convert(spec, json.load(open(os.path.join(HERE, 'vocab_crossdock.json'), encoding='utf-8')), extra)
    # the history table structure stays in the UISS
    ur['operation'] = [b for b in ur['operation'] if not str(b.get('text', '')).startswith(('change history (proposed)', 'Events: ADD'))]
    for b in ur['operation']:
        if str(b.get('text', '')).startswith('Proposed retention'):
            b['text'] = 'The history is kept for 24 months (to be confirmed).'
    out_spec = os.path.join(HERE, f'{fid}_UR_spec.json')
    json.dump(ur, open(out_spec, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    out = os.path.join(HERE, f'{fid}_UR_{d.INFO["name"].replace(" ", "")}.xlsx')
    subprocess.run([sys.executable, os.path.join(ROOT, 'deliverables', 'uiss_specs', 'uiss_build.py'), out_spec, '-o', out],
                   check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    print('written', out, '| technical names left:', left)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'XD01')
