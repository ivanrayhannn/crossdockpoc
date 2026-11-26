"""26-Nov (b): TB_H_STG_APPOLE_KANBAN / _EXPORT keep PERIOD only. EFFECTIVE_MONTH_YEAR is not stored: the views
V_APPOLE_UPLOAD_KANBAN / _EXPORT make it from PERIOD (MM/YYYY) for the upload file. Tables from the table proposal,
SP_STG_WRITE data maps without the column, XD07 file mapping from the view. Revisions XD01 0.17, XD02 0.8, XD03 0.8,
XD05 0.10, XD07 1.3."""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = '26-Nov-26'
spec_ = importlib.util.spec_from_file_location('tp2', os.path.join(HERE, '..', 'erd', 'proposal_staging_sync', 'build_table_proposal_v2.py'))
tp = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(tp)
PERIOD_DESC = {t: next(r[6] for r in rows if r[0] == 'PERIOD') for t, rows in (('TB_H_STG_APPOLE_KANBAN', tp.KAN), ('TB_H_STG_APPOLE_EXPORT', tp.EXP))}
VIEW_TXT = 'MM/YYYY of PERIOD, made by the view'
REV = {'XD01': '0.17', 'XD02': '0.8', 'XD03': '0.8', 'XD05': '0.10', 'XD07': '1.3'}
NOTE = ('TB_H_STG_APPOLE_KANBAN / _EXPORT: EFFECTIVE_MONTH_YEAR removed (same value as PERIOD); the views make Effective Month / Year '
        '(MM/YYYY of PERIOD) for the upload file.')


def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v) for v in o]
    if o == 'EFFECTIVE_MONTH_YEAR (MM/YYYY)':
        return 'EFFECTIVE_MONTH_YEAR of the view (MM/YYYY of PERIOD)'
    return o


for fid, no in REV.items():
    p = os.path.join(HERE, f'{fid}_spec.json')
    s = json.load(open(p))
    if any(r['description'].startswith('TB_H_STG_APPOLE_KANBAN / _EXPORT: EFFECTIVE_MONTH_YEAR removed') for r in s['revisions']):
        continue
    for t in s['tables']:
        if t['name'] in PERIOD_DESC:
            t['columns'] = [c for c in t['columns'] if c[0] != 'EFFECTIVE_MONTH_YEAR']
            for c in t['columns']:
                if c[0] == 'PERIOD':
                    c[-1] = PERIOD_DESC[t['name']]
    for b in s.get('data_map', {}).get('blocks', []):
        b['mappings'] = [m for m in b['mappings'] if m.get('dest_field') != 'EFFECTIVE_MONTH_YEAR']
        for m in b['mappings']:
            if m.get('source_field') == 'EFFECTIVE_MONTH_YEAR':
                m['description'] = VIEW_TXT
    s = {k: (walk(v) if k not in ('revisions', 'tables', 'header') else v) for k, v in s.items()}
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': NOTE})
    s['header']['updated_date'] = D
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched', fid)
