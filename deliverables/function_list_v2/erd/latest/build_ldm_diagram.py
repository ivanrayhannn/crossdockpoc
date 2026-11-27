import os
import json, re, subprocess, html
T = {t['name']: t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'erd4_tables.json')))}
E = {  # physical -> logical entity, group
    'TB_M_PART_MASTER': ('Part Master', 'Existing'), 'TB_M_H0125_DESTINATION': ('Destination', 'Replicated'),
    'TB_R_ACTUAL_DEMAND_SUMMARY': ('Actual Demand Summary', 'Replicated'), 'TB_M_PART_CANDIDATE': ('Crossdock Part', 'New'),
    'TB_M_PART_CANDIDATE_DEST': ('Part Destination Mapping', 'New'), 'TB_R_PART_DAD_RESULT': ('DAD Volume Result', 'New'),
    'TB_H_PART_CANDIDATE': ('Crossdock Part History', 'New'), 'TB_R_CROSSDOCK_IF_RESULT': ('Interface Result', 'New'),
    'TB_R_H0253_ORDER_CONTROL_PRE': ('Customer Order Line', 'Replicated'), 'TB_R_INSTRUCTION': ('Crossdock Instruction', 'New'),
    'TB_H_CROSSDOCK_ORDER_CHANGE': ('Order Change History', 'New'), 'TB_R_PRA_DAILY_ORDER_MANIFEST': ('Supplier PO Manifest', 'Existing'),
    'TB_R_PRA_DAILY_ORDER_PART': ('Supplier PO Manifest Item', 'Existing'), 'TB_R_PRA_DAILY_ORDER_MAPPED': ('PO Mapped Quantity', 'New'),
    'TB_R_DAILY_ORDER_MANIFEST': ('ASN Manifest', 'Existing'), 'TB_R_DAILY_ORDER_PART': ('ASN Manifest Item', 'Existing'),
    'TB_R_CASE_LABEL_LAST_SEQ': ('Case Label Sequence', 'Existing'),
}
REL = [  # parent, child, verb (parent -> child), optional logical
    ('TB_M_PART_MASTER', 'TB_M_PART_CANDIDATE', 'is offered as', 1), ('TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE_DEST', 'is mapped to', 0),
    ('TB_M_H0125_DESTINATION', 'TB_M_PART_CANDIDATE_DEST', 'receives', 0), ('TB_M_PART_CANDIDATE', 'TB_R_PART_DAD_RESULT', 'is calculated in', 0),
    ('TB_M_PART_CANDIDATE', 'TB_H_PART_CANDIDATE', 'keeps changes in', 0), ('TB_M_PART_CANDIDATE', 'TB_R_CROSSDOCK_IF_RESULT', 'is sent as', 0),
    ('TB_M_H0125_DESTINATION', 'TB_R_ACTUAL_DEMAND_SUMMARY', 'has', 0), ('TB_M_PART_CANDIDATE', 'TB_R_ACTUAL_DEMAND_SUMMARY', 'is measured by', 1),
    ('TB_M_H0125_DESTINATION', 'TB_R_H0253_ORDER_CONTROL_PRE', 'orders', 0), ('TB_M_PART_CANDIDATE', 'TB_R_H0253_ORDER_CONTROL_PRE', 'is ordered in', 1),
    ('TB_R_H0253_ORDER_CONTROL_PRE', 'TB_R_INSTRUCTION', 'is packed by', 0), ('TB_R_INSTRUCTION', 'TB_H_CROSSDOCK_ORDER_CHANGE', 'is moved by', 0),
    ('TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_PRA_DAILY_ORDER_PART', 'contains', 0), ('TB_R_PRA_DAILY_ORDER_PART', 'TB_R_PRA_DAILY_ORDER_MAPPED', 'is used by', 0),
    ('TB_R_PRA_DAILY_ORDER_PART', 'TB_R_INSTRUCTION', 'supplies the PO of', 0), ('TB_R_PRA_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_MANIFEST', 'is shipped as', 0),
    ('TB_R_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_PART', 'contains', 0), ('TB_R_DAILY_ORDER_PART', 'TB_R_INSTRUCTION', 'carries', 0),
    ('TB_R_CASE_LABEL_LAST_SEQ', 'TB_R_DAILY_ORDER_MANIFEST', 'numbers', 1),
]
GROUP = {'New': ('#123a6b', '#ffffff'), 'Replicated': ('#5b4a8b', '#ffffff'), 'Existing': ('#595959', '#ffffff')}
AUDIT = re.compile(r'^(CREATED?_|CHANGED_|UPDATE_)')
attr = lambda c: c.replace('_CD', '_CODE').replace('_DT', '_DATE').replace('_NO', '_NO.').replace('_', ' ').title().replace(' No.', ' No.').replace('Asn', 'ASN').replace('Po ', 'PO ').replace('Dad', 'DAD').replace('Mad', 'MAD').replace('If ', 'IF ')
e = html.escape
L = ['digraph LDM {', 'graph [rankdir=LR, bgcolor="transparent", nodesep=0.5, ranksep=1.1, pad=0.3, splines=true];',
     'node [shape=plaintext, fontname="IBM Plex Sans, Segoe UI, Arial, sans-serif", fontsize=10];',
     'edge [fontname="IBM Plex Sans, Segoe UI, Arial, sans-serif", fontsize=9, color="#4f6580", fontcolor="#4f6580", dir=both, arrowtail=teetee, arrowhead=crow, arrowsize=0.8];']
for p, (name, g) in E.items():
    t = T[p]
    ids = [c for c in t['cols'] if 'PK' in c[2]]
    fks = [c for c in t['cols'] if 'FK' in c[2] and 'PK' not in c[2]]
    rest = [c for c in t['cols'] if not c[2] and not AUDIT.match(c[0])]
    shown = rest[:5]
    rows = ''.join(f'<tr><td align="left"><u>{e(attr(c[0]))}</u></td><td align="left"><font color="#4f6580">id{" · ref" if "FK" in c[2] else ""}</font></td></tr>' for c in ids)
    rows += ''.join(f'<tr><td align="left"><i>{e(attr(c[0]))}</i></td><td align="left"><font color="#4f6580">ref</font></td></tr>' for c in fks)
    rows += ''.join(f'<tr><td align="left">{e(attr(c[0]))}</td><td></td></tr>' for c in shown)
    more = len(rest) - len(shown)
    rows += f'<tr><td align="left" colspan="2"><font color="#4f6580">+ {more} more attributes</font></td></tr>' if more > 0 else ''
    bg, fg = GROUP[g]
    L.append(f'{p} [label=<<table border="1" cellborder="0" cellspacing="0" cellpadding="3" color="#c9dcef" bgcolor="#ffffff" style="rounded">'
             f'<tr><td colspan="2" align="left" bgcolor="{bg}"><font color="{fg}"><b>{e(name)}</b></font></td></tr>{rows}</table>>];')
for a, b, verb, logical in REL:
    L.append(f'{a} -> {b} [label="{verb}", arrowtail={"tee" if logical else "teetee"}' + (', style=dashed' if logical else '') + '];')
L.append('}')
open('ldm.dot', 'w').write('\n'.join(L))
svg = subprocess.run(['dot', '-Tsvg', 'ldm.dot'], capture_output=True, text=True, check=True).stdout
subprocess.run(['dot', '-Tpng', '-Gdpi=60', 'ldm.dot', '-o', 'ldm.png'], check=True)
svg = re.sub(r'<!--.*?-->', '', svg[svg.index('<svg'):], flags=re.S)
svg = re.sub(r'<svg width="[^"]+" height="[^"]+"', '<svg role="img" aria-label="Logical data model of Crossdock: 17 entities and their relationships" style="min-width:1500px;width:100%;height:auto"', svg, count=1)
rows = ''.join(f'<tr><td>{e(n)}</td><td>{e(p)}</td><td>{g}</td><td class="t">{e(", ".join(attr(c[0]) for c in T[p]["cols"] if "PK" in c[2]))}</td></tr>' for p, (n, g) in E.items())
excl = ', '.join(t for t in T if t not in E)
open('ldm_fragment.html', 'w').write(
    f'<p class="note">Entities by business name; underlined = identifier, italic = reference to another entity; no data types. '
    f'Line: bar-bar = exactly one, crow foot = many; dashed = logical link (no FK); the label reads from left to right. '
    f'Not in the LDM (working tables of a process, not business data): {e(excl)}. Audit columns (created / changed) left out.</p>'
    f'<div class="tbl erd">{svg}</div><h3>Entity to table</h3><div class="tbl"><table><thead><tr><th>Entity</th><th>Table</th><th>Group</th><th>Identifier</th></tr></thead><tbody>{rows}</tbody></table></div>')
print('ok', len(E))
