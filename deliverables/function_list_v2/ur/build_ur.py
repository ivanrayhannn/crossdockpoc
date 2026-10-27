"""Build the User Requirement document of one function in the TMAP UISS template look
(header block on every sheet, Revision sheet, page frame), with business-level content from ur_<id>.py.

The pages reuse the "Operation Desc" page of the UISS screen template through the uiss-generator skill.
Usage: python3 build_ur.py XD01   -> XD01_UR_<Name>.xlsx in this folder."""
import glob, importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SKILL = glob.glob('/root/.claude/skills/synced/*/uiss-generator/scripts')
if not SKILL:
    raise SystemExit('uiss-generator skill not found')
sys.path.insert(0, SKILL[0])
sys.path.insert(0, HERE)
import build_uiss as B  # noqa: E402

SECTIONS = [('1 Overview', 'Overview'), ('2 Functional Req', 'Functional Requirement'), ('3 Business Rules', 'Business Rule'),
            ('4 Screen Overview', 'Screen Overview'), ('5 Messages', 'Message to User'), ('6 Non-Functional', 'Non-Functional Requirement'),
            ('7 Acceptance', 'Acceptance Criteria'), ('8 Open Points', 'Assumption and Open Point')]
for alias, title in SECTIONS:
    B.ALIASES[alias] = 'Operation Desc'
    B.TITLES[alias] = title


def col(title, width, align=None):
    c = {'title': title, 'width': width}
    if align:
        c['align'] = align
    return c


def tbl(columns, rows, level=1):
    return {'type': 'table', 'columns': columns, 'rows': [[str(v) for v in r] for r in rows], 'level': level}


def h(text, num=None):
    return {'type': 'heading', 'text': text, **({'num': num} if num else {})}


def txt(text, bold=False, level=1):
    return {'type': 'text', 'text': text, 'bold': bold, 'level': level}


def build(fid):
    d = importlib.import_module(f'ur_{fid.lower()}')
    i = d.INFO
    header = {'phase': 'UR', 'project_name': 'Crossdock Optimization', 'block_name': i['type'],
              'function_name': f'{i["id"]} {i["name"]}', 'document_name': 'User Requirement',
              'created_date': '28-Oct-26', 'created_by': 'FID Rayhan'}
    book = B.Book('screen', header)
    B.render_revision(book, {'revisions': [{'revision': '0.1', 'author': 'FID Rayhan', 'date': '28-Oct-26', 'reviewed_by': '',
                                            'description': 'Initial Draft'}]})
    pages = {
        '1 Overview': [
            h('Purpose', '1.1'), txt(d.PURPOSE),
            h('Scope', '1.2'),
            tbl([col('In / Out', 12), col('Description', 85)], [['In scope', x] for x in d.SCOPE_IN] + [['Out of scope', x] for x in d.SCOPE_OUT]),
            h('Users and access', '1.3'),
            tbl([col('User', 14), col('Can do', 50), col('Role', 33)], [[u[0], u[2], u[1]] for u in d.USERS]),
            h('Business process (BPF)', '1.4'),
            tbl([col('No', 5, 'center'), col('Activity', 60), col('Who', 18), col('BPF step', 14)], d.PROCESS),
            h('References', '1.5'),
            tbl([col('Item', 20), col('Reference', 77)], [['Related functions', i['related']], ['Business process', i['bpf']],
                                                         ['Technical design', f'UISS {i["uiss"]} (tables, fields, data mapping, log)']]),
            h('Approval', '1.6'),
            tbl([col('Role', 25), col('Name', 25), col('Signature', 30), col('Date', 17)],
                [['Procurement (user)', '', '', ''], ['D/S Team (user)', '', '', ''], ['Business System Analyst', 'FID Rayhan', '', '']]),
        ],
        '2 Functional Req': [
            txt('What the user must be able to do. Priority: Must / Should / Could.'),
            tbl([col('ID', 7), col('Requirement', 45), col('User', 15), col('Priority', 8, 'center'), col('Business rule', 13), col('BPF step', 9)],
                d.FR),
        ],
        '3 Business Rules': [
            txt('Rules the system must apply, in business wording.'),
            tbl([col('ID', 7), col('Topic', 13), col('Rule', 77)], d.BR),
        ],
        '4 Screen Overview': [txt('Screenshots of the prototype as illustration; the final layout is defined in the UISS.')],
        '5 Messages': [
            txt('Business wording; message IDs and the exact texts are in the UISS.'),
            tbl([col('When', 15), col('Message', 70), col('Business rule', 12)], d.MESSAGES),
        ],
        '6 Non-Functional': [tbl([col('Area', 15), col('Requirement', 82)], d.NFR)],
        '7 Acceptance': [
            txt('Given / When / Then; the base of the test scenarios (UAT).'),
            tbl([col('ID', 7), col('Scenario', 60), col('FR', 10), col('Business rule', 12), col('Result (UAT)', 8)], [list(a) + [''] for a in d.AC]),
        ],
        '8 Open Points': [tbl([col('ID', 7), col('Point', 68), col('PIC', 12), col('Status', 10)], d.OPEN)],
    }
    for n, (cap, img, desc) in enumerate(d.SCREENS, 1):
        pages['4 Screen Overview'] += ([{'type': 'page_break'}] if n > 1 else []) + [h(cap, f'4.{n}'), txt(desc),
                                       {'type': 'image', 'path': os.path.join(ROOT, img), 'max_rows': 34, 'level': 1}]
    for alias, _ in SECTIONS:
        B.Flow(book, alias, layout='full').blocks(pages[alias])
    out = os.path.join(HERE, f'{fid}_UR_{i["name"].replace(" ", "")}.xlsx')
    book.finalize(out)
    print('written', out)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'XD01')
