"""Business flow As-Is / To-Be of ASN03 (ASN Creation screen) and ASN04 (ASN Upload batch) for the CR Crossdock (19-Nov).
Swimlanes: Supplier, NSP ASN (existing), NSP ASN Crossdock (new), Database. Yellow = changed / new in the To-Be, grey dashed = removed.
Drawn with Graphviz (dot) to flow_img/*.png. Run: python3 business_flow.py"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'flow_img')
CHG = 'fillcolor="#FFF2CC" color="#C55A11" penwidth=2'
DEL = 'fillcolor="#F2F2F2" color="#A6A6A6" fontcolor="#7F7F7F" style="rounded,filled,dashed"'
NEWL = 'fillcolor="#E2EFDA" color="#548235"'

HEAD = '''digraph G {
  graph [rankdir=LR, fontname="Helvetica", fontsize=11, nodesep=0.35, ranksep=0.45, pad=0.3, newrank=true, label="%s", labelloc=t, fontsize=14];
  node [shape=box, style="rounded,filled", fillcolor="#FFFFFF", color="#5B6B7F", fontname="Helvetica", fontsize=10, margin="0.12,0.06", width=1.6];
  edge [color="#5B6B7F", fontname="Helvetica", fontsize=9, arrowsize=0.7];
'''


def lane(name, label, color, body):
    return f'  subgraph cluster_{name} {{ label="{label}"; style="filled"; fillcolor="{color}"; color="#BFBFBF"; fontsize=11; labeljust=l;\n{body}  }}\n'


def db_nodes(extra=''):
    return ('    db_pm [shape=cylinder, label="TB_R_PRA_DAILY_ORDER_MANIFEST\\n(CROSS_DOCK_FLAG)"];\n'
            '    db_pp [shape=cylinder, label="TB_R_PRA_DAILY_ORDER_PART\\n(Palletize Code, remaining qty)"];\n'
            '    db_asn [shape=cylinder, label="TB_T_ASN\\n(draft)"];\n'
            '    db_dm [shape=cylinder, label="TB_R_DAILY_ORDER_MANIFEST"];\n'
            '    db_dp [shape=cylinder, label="TB_R_DAILY_ORDER_PART"];\n' + extra)


def asn03(to_be):
    title = 'ASN03 ASN Creation (screen) - ' + ('TO-BE (CR Crossdock)' if to_be else 'AS-IS')
    get = (f'    n2 [label="Get Data Manifest\\nsupplier, remaining qty\\nEXCLUDE CROSS_DOCK_FLAG X\\nand Palletize Code X", {CHG}];\n' if to_be else
           '    n2 [label="Get Data Manifest\\nsupplier, remaining qty\\n(regular + crossdock orders)"];\n')
    sup = ('    s1 [label="Open ASN Creation\\n(Add mode)"];\n'
           '    s2 [label="Pick Manifest No /\\nOrder Date / PO No,\\n[Search]"];\n'
           '    s3 [label="Choose part /\\nmanifest"];\n'
           '    s4 [label="Input qty and\\ndelivery date"];\n'
           '    s5 [label="[Submit]"];\n')
    nsp = (get + '    n3 [label="Show manifest"];\n'
           '    n4 [label="Insert to draft\\n(TB_T_ASN)"];\n'
           '    n5 [label="Submit: insert daily order\\nmanifest and part,\\nreduce qty of pra part"];\n')
    g = HEAD % title + lane('sup', 'Supplier', '#F7FBFF', sup)
    g += lane('nsp', 'NSP - ASN Creation (ASN03, regular orders' + (' only)' if to_be else ')'), '#FFFFFF', nsp)
    if to_be:
        g += lane('xd', 'Other screen: ASN Creation (Crossdock, XD10), crossdock orders', '#F4FAF0',
                  f'    x0 [label="Supplier opens\\nASN Creation (Crossdock)", {NEWL}];\n'
                  f'    x1 [label="ASN per Part +\\nCustomer Order Date\\n(own flow, XD09 / XD10)", {NEWL}];\n')
    g += lane('db', 'Database', '#FAFAFA', db_nodes())
    g += ('  s1 -> s2 -> n2 -> n3 -> s3 -> n4 -> s4 -> s5 -> n5;\n'
          + ('  db_pm -> n2 [style=dashed, label="read flag", constraint=false]; db_pp -> n2 [style=dashed, label="read Palletize", constraint=false];\n' if to_be else
             '  db_pm -> n2 [style=dashed, label="read", constraint=false]; db_pp -> n2 [style=dashed, label="read", constraint=false];\n') +
          '  n4 -> db_asn [style=dashed, label="insert", constraint=false];\n'
          '  n5 -> db_dm [style=dashed, label="insert", constraint=false]; n5 -> db_dp [style=dashed, label="insert", constraint=false];\n'
          '  n5 -> db_pp [style=dashed, label="reduce qty", constraint=false];\n'
          '  { rank=same; s2; n2; db_pm; } s2 -> n2 [style=invis]; n2 -> db_pm [style=invis];\n'
          '  { rank=same; n4; db_asn; } n4 -> db_asn [style=invis];\n'
          '  { rank=same; n5; db_dm; db_dp; } n5 -> db_dm [style=invis]; db_dm -> db_dp [style=invis];\n')
    if to_be:
        g += '  x0 -> x1;\n'
    return g + '}\n'


def asn04(to_be):
    title = 'ASN04 ASN Upload (batch) - ' + ('TO-BE (CR Crossdock)' if to_be else 'AS-IS')
    sup = ('    s1 [label="Fill upload template\\n(Manifest No, Part No, Qty,\\nPalletize Code, Case No...)"];\n'
           '    s2 [label="[Upload] on\\nASN Creation"];\n'
           '    s3 [label="Read result / log"];\n')
    nsp = ('    b1 [label="Format, mandatory\\nand duplication\\nchecks (4b)"];\n')
    if to_be:
        nsp += (f'    b2 [label="Palletize Code X?", shape=diamond, width=1.9, {CHG}];\n'
                f'    b3 [label="Manifest with\\nCROSS_DOCK_FLAG X?", shape=diamond, width=2.1, {CHG}];\n'
                f'    e12 [label="Validation error\\nmsg 12 (line)", {CHG}];\n'
                f'    e13 [label="Validation error\\nmsg 13 (line)", {CHG}];\n'
                f'    b4 [label="Crossdock checks\\nmsg 8 (delivery qty)\\nmsg 9 (case no / palletize)\\nDELETED", {DEL}];\n'
                '    b5 [label="Existing business\\nchecks"];\n'
                '    b6 [label="Any error?", shape=diamond, width=1.3];\n'
                '    b7 [label="Finished with error\\n(msg 7b), nothing saved"];\n'
                '    b8 [label="Insert temporary ->\\nTB_T_ASN draft;\\nSubmit as in ASN Creation"];\n')
    else:
        nsp += ('    b4 [label="Crossdock checks\\nmsg 8 (delivery qty)\\nmsg 9 (case no / palletize)"];\n'
                '    b5 [label="Existing business\\nchecks (all rows,\\nincl. Palletize X)"];\n'
                '    b6 [label="Error?", shape=diamond, width=1.2];\n'
                '    b7 [label="Finished with error\\n(msg 7b), nothing saved"];\n'
                '    b8 [label="Insert temporary ->\\nTB_T_ASN draft (all rows,\\nincl. crossdock);\\nSubmit as in ASN Creation"];\n')
    g = HEAD % title + lane('sup', 'Supplier', '#F7FBFF', sup + (f'    s4 [label="Remove crossdock rows;\\ntheir ASN on the other screen\\nASN Creation (Crossdock)", {NEWL}];\n' if to_be else ''))
    g += lane('nsp', 'NSP - ASN existing (ASN04 batch)', '#FFFFFF', nsp)
    if to_be:
        g += lane('xd', 'NSP - ASN Crossdock (new)', '#F4FAF0', f'    x1 [label="ASN Creation (Crossdock)\\n(XD10)", {NEWL}];\n')
    g += lane('db', 'Database', '#FAFAFA', db_nodes())
    if to_be:
        g += ('  s1 -> s2 -> b1 -> b2;\n  b2 -> e12 [label="Yes"]; b2 -> b3 [label="No"]; b3 -> e13 [label="Yes"]; b3 -> b5 [label="No"];\n'
              '  e12 -> b6; e13 -> b6; b5 -> b6; b6 -> b7 [label="Yes"]; b6 -> b8 [label="No"]; b7 -> s3; b8 -> s3;\n'
              '  s3 -> s4 [style=dashed, label="crossdock rows"]; s4 -> x1;\n'
              '  b4 -> b5 [style=invis];\n  db_pm -> b3 [style=dashed, label="read flag", constraint=false]; b8 -> db_asn [style=dashed, constraint=false];\n'
              '  { rank=same; b3; db_pm; } b3 -> db_pm [style=invis]; { rank=same; b8; db_asn; } b8 -> db_asn [style=invis]; { rank=same; b1; db_pp; } b1 -> db_pp [style=invis];\n')
    else:
        g += ('  s1 -> s2 -> b1 -> b4 -> b5 -> b6; b6 -> b7 [label="Yes"]; b6 -> b8 [label="No"]; b7 -> s3; b8 -> s3;\n'
              '  db_pm -> b5 [style=dashed, label="read", constraint=false]; b8 -> db_asn [style=dashed, constraint=false];\n'
              '  { rank=same; b5; db_pm; } b5 -> db_pm [style=invis]; { rank=same; b8; db_asn; } b8 -> db_asn [style=invis]; { rank=same; b1; db_pp; } b1 -> db_pp [style=invis];\n')
    return g + '}\n'


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, dot in (('asn03_as_is', asn03(False)), ('asn03_to_be', asn03(True)), ('asn04_as_is', asn04(False)), ('asn04_to_be', asn04(True))):
        src = os.path.join(OUT, name + '.dot')
        open(src, 'w').write(dot)
        subprocess.run(['dot', '-Tpng', '-Gdpi=110', src, '-o', os.path.join(OUT, name + '.png')], check=True)
        print('drawn', name)


if __name__ == '__main__':
    main()
