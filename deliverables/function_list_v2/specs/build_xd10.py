"""XD10 ASN Cross Dock Creation Screen = ASN Crossdock Creation (X8) + its Submit ASN batch (X14) as section 5.7."""
import re
from sample_xd10 import SAMPLE
from v2lib import derive, load, replace_all, set_header, write

PRE_X8 = [
    ('([Search], function X12 Get Order)', '([Search], XD09 Mapping Customer Order and PO Batch)'),
    ('Run X12 (Get Order)', 'Run XD09 (Mapping Customer Order and PO)'),
    ('hand the ASN to the batch X14 with a Submit ID; the result is written to the log.',
     'hand the ASN to the submit process with a Submit ID (refer 5.7); the result is written to the log.'),
    ('X12: get customer orders', 'XD09: get customer orders'),
    ('NULL (filled by X14 on submit)', 'NULL (filled by the submit process, refer 5.7)'),
    ('[Search] runs the function X12 Get Order (UISS X12)', '[Search] runs XD09 Mapping Customer Order and PO Batch (UISS XD09)'),
    ('to the batch X14 ASN Submit (UISS X14); the submit process follows the existing ASN. X14 reads',
     'to the submit process (refer 5.7); the submit process follows the existing ASN. It reads'),
    ('Submit handed to the batch X14', 'Submit handed to the submit process (5.7)'),
    ('[Submit ASN] (X14) fills', '[Submit ASN] (5.7) fills'),
    ('(X14)', '(5.7)'),
    ('Refer X10.', 'Refer XD08 / XD11.'),
    ('X14', 'the submit process (5.7)'),
]


def build():
    a = derive(replace_all(load('AsnCreation_spec.json'), PRE_X8))
    b = derive(replace_all(load('AsnSubmit_spec.json'), [('X8 generates', 'The screen generates'), ('on X8', 'on the screen'),
                                                         ('this batch', 'the submit process')]))
    # X14 logs follow LOG1 of the screen
    shift = len(a['logging_messages'])
    b = replace_all(b, [(f'LOG{i}', f'LOG#{i + shift}') for i in range(9, 0, -1)])
    b = replace_all(b, [('LOG#', 'LOG')])

    a['general']['objective'].append("Submit ASN runs in the background with a Submit ID and follows the existing ASN submit of NSP (refer 5.7).")
    a['operation'] += [
        {"type": "heading", "text": "5.7 Submit ASN Process (backend, follows the existing ASN)"},
        {"type": "bullets", "marker": "a.", "level": 2, "items": b['func_flow']['steps']},
        {"type": "bullets", "marker": "-", "level": 2, "items": b['func_desc'][0]['items']},
        {"type": "heading", "text": "5.8 Sample Create ASN"},
        {"type": "bullets", "marker": "-", "level": 2, "items": ["Dummy example of [Create ASN] (case packing, TB_R_INSTRUCTION rows, flags, Case List, scenarios): see sheet Sample Input."]}]
    for blk in b['data_map']['blocks']:
        blk['destination']['description'] = 'Submit ASN (5.7): ' + blk['destination'].get('description', '')
    a['data_map']['blocks'] += b['data_map']['blocks']
    for m in b['logging_messages']:
        act = m['action']
        a['logging_messages'].append({"event": "Submit ASN (5.7): " + m['event'], "cause": m['cause'], "type": m['type'], "msg_id": m['msg_id'],
                                      "message": m['message'], "exception": "Y" if m['type'] in ('Error', 'Critical') else "N",
                                      "action": f"System: {act['system']} User: {act['user']}" if isinstance(act, dict) else act})
    names = {t['name'] for t in a['tables']}
    a['tables'] += [t for t in b['tables'] if t['name'] not in names]
    leftover = re.findall(r'\bX\d+\b', str(a))
    assert not leftover, leftover
    a['sample_sheet'] = SAMPLE  # after the check: dummy POs PO-X1 / PO-X2 look like old X ids
    return write(set_header(a, 'XD10'), 'XD10')


if __name__ == '__main__':
    print(build())
