import os
import json, re, subprocess, html
T = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'erd4_tables.json')))
RELS = [l.split(' - ') for l in '''TB_M_H0125_DESTINATION - TB_M_PART_CANDIDATE_DEST
TB_M_H0125_DESTINATION - TB_R_ACTUAL_DEMAND_SUMMARY
TB_M_PART_CANDIDATE - TB_M_PART_CANDIDATE_DEST
TB_M_PART_CANDIDATE - TB_R_PART_DAD_RESULT
TB_M_PART_CANDIDATE - TB_H_PART_CANDIDATE
TB_M_PART_CANDIDATE - TB_R_CROSSDOCK_IF_RESULT
TB_M_PART_CANDIDATE - TB_R_ACTUAL_DEMAND_SUMMARY - dashed
TB_M_PART_CANDIDATE - TB_R_H0253_ORDER_CONTROL_PRE - dashed
TB_M_H0125_DESTINATION - TB_R_H0253_ORDER_CONTROL_PRE
TB_R_INSTRUCTION - TB_H_CROSSDOCK_ORDER_CHANGE
TB_R_H0253_ORDER_CONTROL_PRE - TB_R_INSTRUCTION
TB_R_H0253_ORDER_CONTROL_PRE - TB_T_INSTRUCTION
TB_R_PRA_DAILY_ORDER_MANIFEST - TB_R_PRA_DAILY_ORDER_PART
TB_R_PRA_DAILY_ORDER_PART - TB_R_PRA_DAILY_ORDER_MAPPED
TB_R_PRA_DAILY_ORDER_PART - TB_R_INSTRUCTION
TB_R_PRA_DAILY_ORDER_PART - TB_T_INSTRUCTION
TB_R_DAILY_ORDER_MANIFEST - TB_R_DAILY_ORDER_PART
TB_R_DAILY_ORDER_PART - TB_R_INSTRUCTION
TB_R_PRA_DAILY_ORDER_MANIFEST - TB_R_DAILY_ORDER_MANIFEST
TB_M_PART_MASTER - TB_M_PART_CANDIDATE - dashed
TB_R_CASE_LABEL_LAST_SEQ - TB_R_DAILY_ORDER_MANIFEST - dashed'''.split('\n')]
KIND = {'New table (Crossdock)': ('#123a6b', '#ffffff'), 'Replicated from DB Surrounding (GTOPAS)': ('#5b4a8b', '#ffffff'),
        'Existing NSP table': ('#595959', '#ffffff'), 'Temporary (session)': ('#a6a6a6', '#0f2540'), 'Temporary (upload)': ('#d9d9d9', '#0f2540')}
e = html.escape
nid = lambda n: 'n' + re.sub(r'\W', '_', n)
L = ['digraph ERD {', 'graph [bgcolor="transparent", splines=true, overlap=false, pad=0.3, outputorder=edgesfirst];',
     'node [shape=plaintext, fontname="IBM Plex Sans, Segoe UI, Arial, sans-serif", fontsize=10];',
     'edge [color="#4f6580", arrowsize=0.8, dir=both, arrowtail=tee, arrowhead=crow, penwidth=1.1];']
for t in T:
    bg, fg = KIND[t['kind']]
    keys = [c for c in t['cols'] if c[2]]
    rows = ''.join(f'<tr><td align="left">{e(c[0])}</td><td align="left"><font color="#4f6580">{e(c[1])}</font></td><td align="left"><b>{e(c[2])}</b></td></tr>' for c in keys)
    more = len(t['cols']) - len(keys)
    rows += f'<tr><td align="left" colspan="3"><font color="#4f6580">+ {more} other columns</font></td></tr>' if more else ''
    lab = (f'<<table border="1" cellborder="0" cellspacing="0" cellpadding="3" color="#c9dcef" bgcolor="#ffffff">'
           f'<tr><td colspan="3" align="left" bgcolor="{bg}"><font color="{fg}"><b>{e(t["name"])}</b></font></td></tr>{rows}</table>>')
    x, y = t['col'] * 330, -(t['row'] - 14) * 13
    L.append(f'{nid(t["name"])} [label={lab}, pos="{x},{y}!"];')
for r in RELS:
    a, b = r[0].strip(), r[1].strip()
    L.append(f'{nid(a)} -> {nid(b)}' + (' [style=dashed]' if len(r) > 2 else '') + ';')
L.append('}')
open('erd_latest.dot', 'w').write('\n'.join(L))
svg = subprocess.run(['neato', '-n2', '-Tsvg', 'erd_latest.dot'], capture_output=True, text=True, check=True).stdout
subprocess.run(['neato', '-n2', '-Tpng', '-Gdpi=60', 'erd_latest.dot', '-o', 'erd_latest.png'], check=True)
svg = svg[svg.index('<svg'):]
svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
svg = re.sub(r'<svg width="[^"]+" height="[^"]+"', '<svg role="img" aria-label="Concept ERD latest: 22 Crossdock tables and their relationships" style="min-width:1700px;width:100%;height:auto"', svg, count=1)
legend = ''.join(f'<span class="kchip"><i style="background:{bg}"></i>{e(k)}</span>' for k, (bg, _) in KIND.items())
cards = ''.join(
    f'<details class="tcard"><summary><i style="background:{KIND[t["kind"]][0]}"></i><b>{e(t["name"])}</b> <span class="note">{len(t["cols"])} columns · {e(t["kind"])}</span></summary>'
    f'<div class="tbl"><table><thead><tr><th>Column</th><th>Type</th><th>Key</th></tr></thead><tbody>'
    + ''.join(f'<tr><td>{e(c[0])}</td><td>{e(c[1])}</td><td>{e(c[2])}</td></tr>' for c in t['cols']) + '</tbody></table></div></details>'
    for t in sorted(T, key=lambda t: (list(KIND).index(t['kind']), t['name'])))
open('erd_latest_fragment.html', 'w').write(
    f'<div class="erdkinds">{legend}<span class="note">Line: 1 (bar) to N (crow foot); dashed = logical, no FK. Only PK / FK columns are drawn; open a table below for all columns.</span></div>'
    f'<div class="tbl erd">{svg}</div><h3>All columns ({len(T)} tables)</h3><div class="tcards">{cards}</div>')
print('ok', len(T))
