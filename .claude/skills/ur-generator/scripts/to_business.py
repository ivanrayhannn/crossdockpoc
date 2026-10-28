"""to_business.py - turn a UISS spec (technical) into a User Requirement spec (business wording), same sheets.

Usage:
  python3 to_business.py UISS_SPEC.json -o UR_SPEC.json [--vocab vocab.json] [--extra extra.json]

vocab.json  (optional) {"TB_M_PART_CANDIDATE": "Part List", "PART_NO": "Part No", ...}  technical name -> business term.
            Names not in the vocab are humanised automatically (TB_M_PART_CANDIDATE -> "Part Candidate", MIN_MAD -> "min MAD").
extra.json  (optional) {"purpose": "...",
                        "business_rules": [["BR-01", "Topic", "Rule"], ...],
                        "acceptance": [["AC-01", "Given / When / Then", "BR-01"], ...],
                        "phrases": [["technical sentence", "business sentence"], ...],
                        "internal_fields": ["sync time", ...]}   (more fields collapsed into "Saved by / time")
The script prints the technical names that are still left so they can be added to the vocab."""
import argparse, json, re

TYPES = {'Varchar': 'Text', 'Char': 'Text', 'Nvarchar': 'Text', 'Number': 'Number', 'Int': 'Number', 'Decimal': 'Number',
         'Date': 'Date', 'Datetime': 'Date and time'}
OPS = {'Insert': 'Add', 'Update': 'Change', 'Delete': 'Remove', 'Insert / Update': 'Add / change', 'Upsert': 'Add / change'}
SOURCES = {'Key-in': 'Entered by user', 'Key in': 'Entered by user', 'System': 'System', '-': '-', '': '-'}
# generic technical phrases -> business wording
PHRASES = [
    ('<DB error message>', '<error detail>'), ('Database error', 'System error'), ('DB error', 'System error'),
    ('refer Data Edit Mapping', 'see Data Edit Mapping'), ('Server system date-time', 'Date and time of saving'),
    ('Server system date', 'Date of saving'), ('Login user ID', 'User who saved'), ('(insert only)', '(first save only)'),
    ('on insert/update of', 'on saving'), ('Insert / update', 'Save'),
]
INTERNAL = {'created by', 'created time', 'created date', 'updated by', 'changed by', 'last update time', 'changed date',
            'last source', 'last upload no.', 'upload no.', 'history no.', 'remark'}
DEFAULT_VOCAB = {'CREATED_BY': 'created by', 'CREATED_DT': 'created time', 'CHANGED_BY': 'updated by', 'CHANGED_DT': 'last update time',
                 'UPDATED_BY': 'updated by', 'UPDATED_DT': 'last update time', 'REMARK': 'remark'}


def humanise(name):
    if name.startswith('TB_'):
        parts = name.split('_')[2:] if len(name.split('_')) > 2 else name.split('_')[1:]
        return ' '.join(p.capitalize() if not p.isdigit() else p for p in parts)
    words = name.split('_')
    return ' '.join(w if len(w) <= 3 and w not in ('NO', 'DT', 'CD') else w.lower() for w in words) \
        .replace(' DT', ' time').replace(' CD', ' code').replace(' NO', ' no')


class Translator:
    def __init__(self, vocab, phrases):
        self.vocab = dict(DEFAULT_VOCAB, **vocab)
        self.phrases = phrases + PHRASES
        self.keys = sorted(self.vocab, key=len, reverse=True)

    def __call__(self, s):
        if not isinstance(s, str):
            return s
        for k, v in self.phrases:
            s = s.replace(k, v)
        for k in self.keys:
            s = re.sub(rf'\b{k}\b', self.vocab[k], s)
        s = re.sub(r'\b(TB_[A-Z0-9_]+|[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b', lambda m: humanise(m.group(1)), s)
        s = re.sub(r"'?\b(\d)\b'?\s*\(([A-Z][\w ]+)\)", r'\2', s)          # status code '0' (No Sync) -> No Sync
        s = re.sub(r'sorted by ([\w /]+?) descending', r'sorted by \1, newest first', s)
        s = re.sub(r'\bNULL\b', 'empty', s)
        for k, v in self.phrases:
            s = s.replace(k, v)
        return s

    def walk(self, o):
        if isinstance(o, dict):
            return {k: self.walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [self.walk(v) for v in o]
        return self(o)


def convert(spec, vocab=None, extra=None):
    extra = extra or {}
    t = Translator(vocab or {}, [tuple(p) for p in extra.get('phrases', [])])
    kind = spec.get('doc_type', 'screen')
    ur = {'doc_type': kind}
    ur['header'] = dict(spec.get('header') or {}, phase='UR', document_name='User Requirement')
    ur['revisions'] = extra.get('revisions') or [{'revision': '0.1', 'author': ur['header'].get('created_by', ''),
                                                  'date': ur['header'].get('created_date', ''), 'reviewed_by': '',
                                                  'description': 'Initial Draft: business version of the UISS'}]
    g = t.walk(spec.get('general') or {})
    if extra.get('purpose'):
        g['objective'] = [extra['purpose']] + list(g.get('objective', []))
    ur['general'] = g
    for key in ('screen_flow', 'screen_layout', 'func_flow', 'layout', 'display_messages', 'logging_messages'):
        if key in spec:
            ur[key] = t.walk(spec[key])
    # items: what the user sees / enters
    items = []
    for it in spec.get('items', []):
        if 'group' in it and 'name' not in it:
            items.append(t.walk(it)); continue
        x = t.walk(it)
        src = it.get('source') or ''
        x['source'] = SOURCES.get(src, t(src))
        x['field'] = '-'
        if 'type' in it:
            x['type'] = TYPES.get(it['type'], t(it['type']))
        if 'len' in it:
            x['len'] = '-'
        if 'format' in it:
            x['format'] = it['format'] if re.fullmatch(r'DD-Mon-YYYY( HH:MM)?', str(it['format'])) else '-'
        items.append(x)
    if items:
        ur['items'] = items
    # data map: business objects, Add / Change / Remove, internal fields as one row
    dm = t.walk(spec.get('data_map') or {})
    for b in dm.get('blocks', []):
        d = b.get('destination', {})
        d['operation'] = OPS.get(d.get('operation'), d.get('operation'))
        internal = INTERNAL | {x.lower() for x in extra.get('internal_fields', [])}
        maps = [m for m in b.get('mappings', []) if str(m.get('dest_field', '')).lower() not in internal]
        if len(maps) < len(b.get('mappings', [])):
            maps.append({'dest_field': 'Saved by / time', 'description': 'User who saved, date and time of saving'})
        for m in maps:
            s = str(m.get('description', '')).strip()
            if s.startswith('empty (') and s.endswith(')'):
                s = s[7:-1]
            m['description'] = s or '-'
        b['mappings'] = maps
    if dm:
        ur['data_map'] = dm
    # operation / function description: business rules first, acceptance criteria last; column definitions stay in the UISS
    key = 'operation' if kind != 'batch' else 'func_desc'
    blocks = [b for b in t.walk(spec.get(key) or []) if not (b.get('type') == 'table' and re.search(r'VARCHAR|NVARCHAR|\bINT\b', json.dumps(b)))]
    head = []
    if extra.get('business_rules'):
        head = [{'type': 'heading', 'text': f'{"5" if kind != "batch" else "4"}.0 Business Rules'},
                {'type': 'table', 'level': 1, 'columns': [{'title': 'ID', 'width': 6}, {'title': 'Topic', 'width': 12}, {'title': 'Rule', 'width': 80}],
                 'rows': [list(r) for r in extra['business_rules']]}]
    tail = []
    if extra.get('acceptance'):
        tail = [{'type': 'page_break'}, {'type': 'heading', 'text': 'Acceptance Criteria (UAT)'},
                {'type': 'table', 'level': 1, 'columns': [{'title': 'ID', 'width': 6}, {'title': 'Scenario (Given / When / Then)', 'width': 62},
                                                          {'title': 'Rule', 'width': 18}, {'title': 'Result', 'width': 10}],
                 'rows': [[a[0], a[1], a[2] if len(a) > 2 else '', ''] for a in extra['acceptance']]}]
    ur[key] = head + blocks + tail
    ur[key + '_layout'] = 'full' if kind != 'batch' else spec.get('func_desc_layout', 'two')
    if kind == 'batch' and spec.get('appendix'):
        ur['appendix'] = [b for b in t.walk(spec['appendix']) if not (b.get('type') == 'table' and 'VARCHAR' in json.dumps(b))]
    left = sorted(set(re.findall(r'\bTB_[A-Z0-9_]+|\b[A-Z]{2,}_[A-Z0-9_]{2,}\b', json.dumps(ur))))
    return ur, left


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--vocab')
    ap.add_argument('--extra')
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding='utf-8'))
    vocab = json.load(open(a.vocab, encoding='utf-8')) if a.vocab else {}
    extra = json.load(open(a.extra, encoding='utf-8')) if a.extra else {}
    ur, left = convert(spec, vocab, extra)
    json.dump(ur, open(a.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps({'output': a.out, 'technical_names_left': left}, indent=1))


if __name__ == '__main__':
    main()
