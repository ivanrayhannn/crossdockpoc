"""26-Nov (d): the robots read views only. New view V_GTOPAS_CROSSDOCK (rows of TB_H_STG_GTOPAS with SYNC_STATUS 1) for XD06 and the
count of the parent flow, next to V_APPOLE_UPLOAD_KANBAN / _EXPORT of XD07. The view definitions (columns, source) come from
build_table_proposal_v2.VIEWS and are added to the Tables of XD06 / XD07. Revisions XD06 1.3, XD07 1.5."""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = '26-Nov-26'
spec_ = importlib.util.spec_from_file_location('tp2', os.path.join(HERE, '..', 'erd', 'proposal_staging_sync', 'build_table_proposal_v2.py'))
tp = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(tp)
VIEW = {name: (purpose, desc, rows) for name, purpose, desc, rows in tp.VIEWS}
TEXT = [
    ("SELECT COUNT(*) FROM TB_H_STG_GTOPAS WHERE SYNC_STATUS = '1' AND SYNC_DT =", 'SELECT COUNT(*) FROM V_GTOPAS_CROSSDOCK WHERE SYNC_DT ='),
    ('Source data: only TB_H_STG_GTOPAS (read-only DB user)', 'Source data: only V_GTOPAS_CROSSDOCK (rows of TB_H_STG_GTOPAS with SYNC_STATUS 1; read-only DB user)'),
    ('Rows of TB_H_STG_GTOPAS of the run', 'Rows of V_GTOPAS_CROSSDOCK of the run'),
    ("Read TB_H_STG_GTOPAS (read-only DB user): rows with SYNC_STATUS '1' and SYNC_DT =", 'Read V_GTOPAS_CROSSDOCK (read-only DB user): rows with SYNC_DT ='),
    ('XD06 reads only TB_H_STG_GTOPAS:', 'XD06 reads only V_GTOPAS_CROSSDOCK (TB_H_STG_GTOPAS rows with SYNC_STATUS 1):'),
]
REV = {'XD06': ('1.3', ['V_GTOPAS_CROSSDOCK']), 'XD07': ('1.5', ['V_APPOLE_UPLOAD_KANBAN', 'V_APPOLE_UPLOAD_EXPORT'])}
NOTE = ('The robots read views only: new view V_GTOPAS_CROSSDOCK (TB_H_STG_GTOPAS rows with SYNC_STATUS 1) for XD06 and the parent flow; '
        'view definitions added to the Tables.')


def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v) for v in o]
    if isinstance(o, str):
        for a, b in TEXT:
            o = o.replace(a, b)
    return o


for fid, (no, views) in REV.items():
    p = os.path.join(HERE, f'{fid}_spec.json')
    s = json.load(open(p))
    if any(r['description'].startswith('The robots read views only') for r in s['revisions']):
        continue
    s = {k: (walk(v) if k not in ('revisions', 'tables', 'header') else v) for k, v in s.items()}
    if fid == 'XD06':
        for inp in s['general'].get('inputs', []):
            if inp.get('name') == 'TB_H_STG_GTOPAS':
                inp['name'] = 'V_GTOPAS_CROSSDOCK'
        for n in s['func_flow'].get('flow', {}).get('nodes', []):
            if n.get('label') == 'TB_H_STG_GTOPAS':
                n['label'] = 'V_GTOPAS_CROSSDOCK'
        for b in s['data_map']['blocks']:
            if isinstance(b['source'], dict) and b['source'].get('table') == 'TB_H_STG_GTOPAS':
                b['source']['table'] = 'V_GTOPAS_CROSSDOCK'
                for k in b['source'].get('keys', []):
                    if k['field'] == 'SYNC_DT':
                        k['value'] = 'SYNC_DT of the run'
    for name in views:
        purpose, desc, rows = VIEW[name]
        cols = [[c, typ, '', 'Y', (f'{file_col}: ' if file_col else 'Helper, not written: ') + (f'{d}. ' if d else '') + f'Source: {src}']
                for c, typ, src, file_col, d in rows]
        s['tables'] = [t for t in s['tables'] if t['name'] != name] + [
            {'name': name, 'kind': 'view', 'proposed': True, 'columns': cols, 'description': f'View ({purpose}). {desc}'}]
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': NOTE})
    s['header']['updated_date'] = D
    json.dump(s, open(p, 'w'), indent=1, ensure_ascii=False)
    print('patched', fid)
