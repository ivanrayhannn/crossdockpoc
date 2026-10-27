"""Convert the UISS specs of function list v2 (XD01-XD15) into Markdown for coding.

Source: deliverables/function_list_v2/specs/XDnn_spec.json (the same JSON that builds the UISS .xlsx).
Output (this folder):
  uiss/XDnn_<Type>_<Name>.md   one file per function, all UISS sheets in order
  tables.md                    every table definition, merged per table name (used by which function)
  messages.md                  every display / logging message per function
  README.md                    index
The functions are converted in parallel (one process per spec).
Run: python3 prepare_code/build_md.py (from the repository root)."""
import glob, json, os, re, sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPECS = os.path.join(ROOT, 'deliverables', 'function_list_v2', 'specs')
sys.path.insert(0, SPECS)
from v2lib import FUNCS  # noqa: E402  (id -> (name, type, uiss file))

OUT = os.path.join(HERE, 'uiss')
REMOVED = {'XD12': 'Cancel Crossdock Customer Order Batch – removed 23-Oct (status 2 handled by XD08, qty in an ASN moved by XD11).',
           'XD14': 'DAD Volume Calculation Result Screen (Buffer) – not used (decision 19-Oct).'}


# ---------- helpers
def esc(v):
    if v is None:
        return ''
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)
    return str(v).replace('|', '\\|').replace('\r', '').replace('\n', '<br>')


def table(headers, rows):
    out = ['| ' + ' | '.join(esc(h) for h in headers) + ' |', '|' + '---|' * len(headers)]
    for r in rows:
        r = list(r) + [''] * (len(headers) - len(r))
        out.append('| ' + ' | '.join(esc(c) for c in r[:len(headers)]) + ' |')
    return '\n'.join(out)


def mermaid(flow):
    if not flow:
        return ''
    if 'dot' in flow:
        return '```dot\n' + flow['dot'] + '\n```'
    shape = {'start': ('([', '])'), 'end': ('([', '])'), 'decision': ('{', '}'), 'db': ('[(', ')]'),
             'screen': ('[[', ']]'), 'event': ('>', ']'), 'file': ('[/', '/]'), 'document': ('[/', '/]'),
             'io': ('[/', '/]'), 'message': ('>', ']'), 'note': ('[', ']'), 'subprocess': ('[[', ']]')}
    lines = ['```mermaid', 'flowchart ' + flow.get('direction', 'TB')]
    for n in flow.get('nodes', []):
        a, b = shape.get(n.get('type'), ('[', ']'))
        label = (f"{n['step']}. " if n.get('step') else '') + str(n.get('label', n['id']))
        lines.append(f'  {n["id"]}{a}"{label.replace(chr(34), chr(39))}"{b}')
    for e in flow.get('edges', []):
        arrow = '-.->' if e.get('style') == 'dashed' else '-->'
        lab = f'|{e["label"]}|' if e.get('label') else ''
        lines.append(f'  {e["from"]} {arrow}{lab} {e["to"]}')
    lines.append('```')
    return '\n'.join(lines)


def image(path, caption=''):
    if not path:
        return f'*{caption}* (no image)'
    rel = os.path.relpath(os.path.join(ROOT, path), OUT) if not os.path.isabs(path) else path
    return f'![{caption}]({rel})'


def bullets(items, marker='-', level=0):
    out = []
    num = re.match(r'^(\d+|[a-z])\.$', marker or '')
    for i, it in enumerate(items):
        m = marker
        if num:
            m = f'{i + 1}.' if num.group(1).isdigit() else f'{chr(ord("a") + i)}.'
        pad = '  ' * level
        if isinstance(it, dict):
            out.append(f'{pad}{"-" if not num else m} {it.get("text", "")}')
            if it.get('children'):
                out += bullets(it['children'], it.get('child_marker', '-'), level + 1)
        else:
            out.append(f'{pad}{"-" if not num else m} {it}')
    return out


def blocks(bl):
    """Flow blocks (operation / func_desc / appendix)."""
    out = []
    for b in bl or []:
        if not isinstance(b, dict):
            out.append(str(b)); continue
        t, lv = b.get('type'), b.get('level', 0) or 0
        if t == 'heading':
            out.append(f'\n### {(b.get("num") + " ") if b.get("num") else ""}{b.get("text", "")}\n')
        elif t == 'text':
            txt = b.get('text', '')
            out.append(('**' + txt + '**') if b.get('bold') else ('*' + txt + '*') if b.get('italic') else txt)
            out.append('')
        elif t == 'item':
            out.append(f'{"  " * max(lv - 2, 0)}- {b.get("marker", "")} {b.get("text", "")}'.replace('-  ', '- '))
        elif t == 'bullets':
            out += bullets(b.get('items', []), b.get('marker', '-'), max(lv - 2, 0)); out.append('')
        elif t == 'table':
            out.append(table([c.get('title', '') if isinstance(c, dict) else c for c in b.get('columns', [])], b.get('rows', [])))
            out.append('')
        elif t == 'flow':
            if b.get('caption'): out.append(f'*{b["caption"]}*')
            out.append(mermaid(b.get('spec') or b.get('flow'))); out.append('')
        elif t == 'image':
            out.append(image(b.get('path'), b.get('caption', ''))); out.append('')
    return out


def messages(rows, logging=False):
    heads = ['ID', 'Event', 'Cause', 'Type', 'Message', 'Action'] + (['Exception'] if logging else [])
    out_rows = []
    for m in rows or []:
        if 'group' in m and 'msg_id' not in m:
            out_rows.append([f'**{m["group"]}**'] + [''] * (len(heads) - 1)); continue
        act = m.get('action', '')
        if isinstance(act, dict):
            act = '; '.join(f'{k}: {v}' for k, v in act.items())
        out_rows.append([m.get('msg_id', ''), m.get('event', ''), m.get('cause', ''), m.get('type', ''), m.get('message', ''), act]
                        + ([m.get('exception', '')] if logging else []))
    return table(heads, out_rows) if out_rows else '_None._'


def data_map(dm):
    if not dm:
        return ['_None._']
    out = []
    if dm.get('note') and not dm.get('blocks'):
        out.append(dm['note'])
    for i, b in enumerate(dm.get('blocks', []), 1):
        src = b.get('source')
        if isinstance(src, dict):
            keys = ', '.join(f'{k["field"]} = {k.get("value", "")}' for k in src.get('keys', []))
            src = src.get('table', '') + (f' (keys: {keys})' if keys else '')
        d = b.get('destination', {})
        dkeys = ', '.join(f'{k["field"]} = {k.get("value", "")}' for k in d.get('keys', []))
        out.append(f'#### {i}. {d.get("operation", "")} {d.get("table", "")}' + (f' – {d["description"]}' if d.get('description') else ''))
        out.append(f'- Source: {src}')
        if dkeys: out.append(f'- Destination keys: {dkeys}')
        if b.get('source_fields'): out.append('- Source fields: ' + ', '.join(b['source_fields']))
        out.append('')
        out.append(table(['Source field', 'Destination field', 'Description'],
                         [[m.get('source_field', ''), m.get('dest_field', ''), m.get('description', '')] for m in b.get('mappings', [])]))
        out.append('')
    return out


def table_defs(tables):
    out = []
    for t in tables or []:
        flags = ', '.join(x for x in [t.get('kind', ''), 'proposed' if t.get('proposed') else 'existing'] if x)
        out.append(f'#### {t["name"]} ({flags})')
        if t.get('description'): out.append(t['description'])
        out.append('')
        out.append(table(['Column', 'Type', 'PK', 'Null', 'Description'], t.get('columns', [])))
        out.append('')
    return out


def sample(s):
    if not s:
        return []
    out = [f'## {s.get("title", "Sample Input")}', '']
    if s.get('heading'): out += [f'**{s["heading"]}**', '']
    out += [f'- {x}' for x in s.get('intro', [])] + ['']
    for sec in s.get('sections', []):
        out += [f'### {sec.get("title", "")}', '', table(sec.get('columns', []), sec.get('rows', [])), '']
    return out


# ---------- one function
def convert(fid):
    name, ftype, xlsx = FUNCS[fid]
    s = json.load(open(os.path.join(SPECS, f'{fid}_spec.json'), encoding='utf-8'))
    h = s.get('header', {})
    out = [f'# {fid} – {name}', '',
           f'> Generated from `deliverables/function_list_v2/specs/{fid}_spec.json` (UISS `{xlsx}`). '
           'Do not edit by hand: change the spec and run `python3 prepare_code/build_md.py`. '
           'Document names: GTOPAS / NSP (prototype: G-System / Supplier System).', '',
           table(['Phase', 'Project', 'Block', 'Function', 'Created', 'By', 'Type'],
                 [[h.get('phase', ''), h.get('project_name', ''), h.get('block_name', ''), h.get('function_name', ''),
                   h.get('created_date', ''), h.get('created_by', ''), s.get('doc_type', '')]]), '',
           '## Revision', '',
           table(['Rev', 'Author', 'Date', 'Reviewed by', 'Description'],
                 [[r.get('revision'), r.get('author'), r.get('date'), r.get('reviewed_by'), r.get('description')] for r in s.get('revisions', [])]), '']
    g = s.get('general', {})
    out += ['## 1. General', '', '### Objective', ''] + [f'- {o}' for o in g.get('objective', [])] + ['']
    if s['doc_type'] == 'screen':
        for d in g.get('display_order', []):
            out += [f'### Display order – {d.get("section", "")}', '',
                    table(['Field', 'Order'], [[f.get('field'), f.get('order')] for f in d.get('fields', [])]), '']
        if g.get('buttons'):
            out += ['### Buttons', '', table(['Button', 'Function'], [[b.get('name'), b.get('function')] for b in g['buttons']]), '']
        if g.get('screen_modes'):
            names = []
            for m in g['screen_modes']:
                for sec in m.get('sections', []):
                    for k in (sec.get('buttons') or {}):
                        if k not in names: names.append(k)
            rows = [[m.get('mode'), sec.get('section'), sec.get('description')] + [(sec.get('buttons') or {}).get(k, '') for k in names]
                    for m in g['screen_modes'] for sec in m.get('sections', [])]
            out += ['### Screen modes (E = enabled, D = disabled)', '', table(['Mode', 'Section', 'Description'] + names, rows), '']
        out += [f'- {r}' for r in g.get('screen_mode_remarks', [])] + ['']
        out += ['## 2. Screen flow', '']
        for f in s.get('screen_flow', []):
            out += [f'### {f.get("title", "")}', '']
            out += [mermaid(f['flow'])] if f.get('flow') else [image(f.get('image'), f.get('title', ''))]
            out += [f'- {n}' for n in f.get('notes', [])] + ['']
        out += ['## 3. Screen layout', '']
        for l in s.get('screen_layout', []):
            out += [f'### {l.get("caption", "")}', '', image(l.get('image'), l.get('caption', ''))] + [f'- {n}' for n in l.get('notes', [])] + ['']
        out += ['## 4. Item description', '']
        rows, no = [], 0
        for it in s.get('items', []):
            if 'group' in it and 'name' not in it:
                rows.append([f'**{it["group"]}**'] + [''] * 13); continue
            no += 1
            rows.append([it.get('no', no), it.get('name'), it.get('source'), it.get('field'), it.get('type'), it.get('len'), it.get('io'),
                         it.get('control'), it.get('justified'), it.get('initial'), it.get('required'), it.get('format'), it.get('validation'), it.get('description')])
        out += [table(['No', 'Item', 'Source', 'Field', 'Type', 'Len', 'I/O', 'Control', 'Justified', 'Initial', 'Req', 'Format', 'Validation', 'Description'], rows), '']
        out += ['## 5. Data edit mapping', ''] + data_map(s.get('data_map'))
        out += ['## 6. Operation description', ''] + blocks(s.get('operation'))
        out += ['## 7. Display messages', '', messages(s.get('display_messages')), '']
        out += ['## 8. Logging messages', '', messages(s.get('logging_messages'), logging=True), '']
        out += ['## 9. Tables', ''] + table_defs(s.get('tables'))
    else:
        of = g.get('operation_flow') or {}
        if of:
            out += ['### Operation flow', '', mermaid(of['flow']) if of.get('flow') else image(of.get('image'), 'Operation flow')]
            if of.get('note'): out.append(f'*{of["note"]}*')
            out.append('')
        if g.get('inputs'):
            out += ['### Input', '', table(['Name', 'Type', 'Description'], [[i.get('name'), i.get('type'), i.get('description')] for i in g['inputs']]), '']
        if g.get('outputs'):
            out += ['### Output', '', table(['Name', 'Type', 'Description'], [[i.get('name'), i.get('type'), i.get('description')] for i in g['outputs']]), '']
        for x in g.get('extra_tables', []):
            cols = [c.get('title', '') if isinstance(c, dict) else c for c in x.get('columns', [])]
            rows = [r if isinstance(r, list) else [r] for r in x.get('rows', [])]
            out += [f'### {x.get("title", "")}', '', table(cols, rows), '']
        out += [f'- {c}' for c in g.get('constraints', [])] + ['']
        ff = s.get('func_flow', {})
        out += ['## 2. Function flow', '']
        if ff.get('flow'): out += [mermaid(ff['flow']), '']
        out += bullets(ff.get('steps', []), '1.') + ['']
        out += ['## 3. Data edit mapping', ''] + data_map(s.get('data_map'))
        out += ['## 4. Function description', ''] + blocks(s.get('func_desc'))
        out += ['## 5. Logging messages', '', messages(s.get('logging_messages')), '']
        if s.get('appendix'):
            out += ['## 6. Appendix', ''] + blocks(s.get('appendix'))
        out += ['## 7. Tables', ''] + table_defs(s.get('tables'))
    out += sample(s.get('sample_sheet'))
    fname = f'{fid}_{xlsx.split("_UISS_")[1].replace(".xlsx", "")}.md'
    text = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).rstrip() + '\n'
    with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as fh:
        fh.write(text)
    return fid, fname, name, ftype, s


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, '*.md')):
        os.remove(old)
    with ProcessPoolExecutor() as ex:
        res = sorted(ex.map(convert, sorted(FUNCS)))
    # merged table definitions
    tabs = {}
    for fid, _, _, _, s in res:
        for t in s.get('tables', []):
            e = tabs.setdefault(t['name'], {'def': t, 'used': []})
            e['used'].append(fid)
            if len(t.get('columns', [])) > len(e['def'].get('columns', [])):
                e['def'] = t
    out = ['# Tables (XD01–XD15)', '', 'One definition per table (the most complete one among the UISS); "Used by" = functions that define it.', '',
           table(['Table', 'Kind', 'New / existing', 'Used by'],
                 [[n, e['def'].get('kind', ''), 'proposed' if e['def'].get('proposed') else 'existing', ', '.join(e['used'])] for n, e in sorted(tabs.items())]), '']
    for n, e in sorted(tabs.items()):
        out += table_defs([e['def']])[:1] + [f'Used by: {", ".join(e["used"])}', ''] + table_defs([e['def']])[1:]
    open(os.path.join(HERE, 'tables.md'), 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
    # messages
    out = ['# Messages (XD01–XD15)', '']
    for fid, _, name, _, s in res:
        out += [f'## {fid} – {name}', '']
        if s.get('display_messages'):
            out += ['### Display', '', messages(s['display_messages']), '']
        out += ['### Logging', '', messages(s.get('logging_messages'), logging=s['doc_type'] == 'screen'), '']
    open(os.path.join(HERE, 'messages.md'), 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
    # index
    rows = [[fid, name, ftype, f'[uiss/{fn}](uiss/{fn})'] for fid, fn, name, ftype, _ in res]
    rows += [[k, v.split(' – ')[0], '–', v.split(' – ')[1]] for k, v in REMOVED.items()]
    rows.sort()
    out = ['# Prepare code – UISS in Markdown', '',
           'Markdown copy of every UISS of function list v2 (XD01–XD15), for developers and coding agents. '
           'Generated from the UISS specs; regenerate after any spec change:', '',
           '```bash', 'python3 prepare_code/build_md.py   # also run by deliverables/function_list_v2/build_all_v2.sh', '```', '',
           '## Functions', '', table(['ID', 'Function', 'Type', 'File'], rows), '',
           '## Shared references', '',
           '- [tables.md](tables.md): all tables (new and existing) with columns, merged per table name.',
           '- [messages.md](messages.md): display / logging messages per function.',
           '- Business process flow: `deliverables/function_list_v2/bpf/Crossdock_BPF_Level2.xlsx` (F1 master, F2 daily order to ASN, F4 hold & cancel).',
           '- ERD / DB structure: `deliverables/function_list_v2/erd/`.',
           '- Simulation data (16–22 Oct, PART-X): `deliverables/simulasi_asn_rev.xlsx`; prototype: `app/` (menu ASN Simulation / ASN Creation).',
           '- UR / business logic summary: `deliverables/function_list_v2/XD01-XD15_UR_Business_Logic_Summary.xlsx`.', '',
           '## Business Logic ASN', '',
           '1. Customer Order Date (D) → PO Date D+1: 1 PO per Part Number per Customer Order Date.',
           '2. Total customer order qty of all destinations = PO qty; less → abnormality (Short PO), the rest waits for the split PO.',
           '3. One customer order line can be in several ASNs; a separate receipt splits the H0253 line (new SERIAL_NO).',
           '4. PO_MAPPED_FLAG is set by Create ASN (Y when the whole line is in TB_R_INSTRUCTION).',
           '5. Ready cases are sent following CUT_FLAG (from case 1 up to a cut).',
           '6. Per Part Number, the oldest Customer Order Date first (no skip); held lines are not counted.', '',
           '## Conventions', '',
           '- Flows are Mermaid diagrams converted from the UISS flowcharts; screenshots link to `deliverables/uiss_screens/`.',
           '- Sections follow the UISS sheets: Screen = General, Screen Flow, Layout, Item, Data Map, Operation, Messages, Tables, Sample Input; '
           'Batch = General, Function Flow, Data Map, Function Description, Logging, Appendix, Tables, Sample Input.', '']
    open(os.path.join(HERE, 'README.md'), 'w', encoding='utf-8').write('\n'.join(out))
    for fid, fn, *_ in res:
        print('written', fn)


if __name__ == '__main__':
    main()
