"""27-Oct: upload column of the XD01 templates.
Part List: flag_add_edit renamed to upload (A / E). Mapping: new column upload (A = new destination of the part, E = mapped destination)."""
import json

UP_MAP = ('A = Add (destination not yet mapped for the part in the ongoing period), '
          'E = Edit (destination already mapped; case_day can be changed). Export Excel pre-fills E, and A for the blank row of a part without mapping.')
MAPPED = {('PART-A', '9722D10'), ('PART-A', '9811110'), ('PART-A', '9715310'), ('PART-C', '9715310')}


def load(fid):
    with open(f'{fid}_spec.json') as f:
        return json.load(f)


def save(fid, spec):
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(spec, f, indent=1, ensure_ascii=False)


def walk(o, fn):
    if isinstance(o, dict):
        return {k: walk(v, fn) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v, fn) for v in o]
    return fn(o) if isinstance(o, str) else o


def part_list(s):
    return s.replace('Rules per flag_add_edit and status', 'Rules per upload value and status').replace('flag_add_edit', 'upload')


def xd01(s):
    s = part_list(s)
    s = s.replace('part_no, dest_code, case_day, total_case_day', 'part_no, dest_code, case_day, upload, total_case_day')
    if s.startswith("Sheet 'Upload': every Active part of the ongoing period") and 'upload =' not in s:
        s += ' upload = E for a mapped destination, A for the blank row.'
    return s


def xd03(spec):
    spec = walk(spec, lambda s: s.replace('Header has the 4 template columns', 'Header has the 5 template columns'))
    # template description (Appendix)
    for blk in spec['appendix']:
        rows = blk.get('rows') if isinstance(blk, dict) else None
        if rows and any(r and r[0] == 'total_case_day' for r in rows) and not any(r[0] == 'upload' for r in rows):
            i = next(i for i, r in enumerate(rows) if r[0] == 'total_case_day')
            rows.insert(i, ['upload', UP_MAP])
    # row check 8
    for blk in spec['func_desc']:
        rows = blk.get('rows') if isinstance(blk, dict) else None
        if rows and rows[0][1].startswith('Part No exists in TB_M_PART_CANDIDATE') and not any(r[2] == 'upload' for r in rows):
            rows.append(['8', 'upload is A or E. A only for a destination that is not yet mapped for the part, E only for a destination '
                         'that is already mapped (ongoing period). A placeholder row left blank is skipped.', 'upload'])
    # sample sheet: column upload before total_case_day
    for sec in spec['sample_sheet']['sections']:
        cols = sec['columns']
        if 'total_case_day' not in cols or 'upload' in cols:
            continue
        i, ip, idc = cols.index('total_case_day'), cols.index('part_no'), cols.index('dest_code')
        cols.insert(i, 'upload')
        sec['widths'].insert(i, 8)
        for r in sec['rows']:
            r.insert(i, 'E' if (r[ip], r[idc]) in MAPPED else 'A')
        if sec['title'].startswith('C.'):
            sec['rows'].append(['E9', 'upload E for a destination that is not mapped yet', 'PART-C', '9811110', 12, 'E', 30,
                                'Check 8: Destination 9811110 is not mapped for PART-C yet; use upload A.'])
    return spec


save('XD01', walk(load('XD01'), xd01))
save('XD02', walk(load('XD02'), part_list))
save('XD03', xd03(load('XD03')))
