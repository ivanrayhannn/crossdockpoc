"""Build Crossdock_ERD.xlsx: concept ERD (entities as cell blocks, relationship lines as shapes), table list, relationships,
column definition and simulation data. Columns are taken from the UISS specs of function list v2.
Run: python3 build_erd.py (from this folder)."""
import glob, json, os, re, sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'bpf'))
from bpf_ref import Shapes  # noqa: E402
from build_bpf import add_drawings  # noqa: E402
from erd_data import KIND, PRA_NOTES, RENAME, LAYOUT, RELATIONS, SCENARIO, SHOW, SIM, TABLE_KIND  # noqa: E402

OUT = os.path.join(HERE, 'Crossdock_ERD.xlsx')
SPECS = os.path.join(HERE, '..', 'specs')
AUDIT = {'CREATED_BY', 'CREATED_DT', 'CHANGED_BY', 'CHANGED_DT', 'CREATE_BY', 'CREATE_DT', 'UPDATE_BY', 'UPDATE_DT', 'CREATED_BY / CREATED_DT'}
EXTRA_USED = {'TB_R_PRA_DAILY_ORDER_MANIFEST': ['XD09', 'XD10'], 'TB_R_PRA_DAILY_ORDER_PART': ['XD09', 'XD10']}
W_NAME, W_TYPE, W_KEY, W_GAP = 30, 13, 7, 7
R_COR, N_COR = 5, 8          # corridor rows for long relationship lines
EMU = 9525

thin = Side(style='thin', color='FF808080')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F = lambda sz=9, b=False, c='000000': Font(name='Arial', size=sz, bold=b, color='FF' + c)  # noqa: E731
FILL = lambda c: PatternFill('solid', fgColor='FF' + c)  # noqa: E731


def load_tables():
    tables, used = {}, {}
    for f in sorted(glob.glob(os.path.join(SPECS, 'XD*_spec.json'))):
        fid = os.path.basename(f)[:4]
        for t in json.load(open(f, encoding='utf-8'))['tables']:
            used.setdefault(t['name'], []).append(fid)
            cols = []
            for c in t['columns']:
                c = list(c[:5])
                if TABLE_KIND.get(t['name']) in ('new', 'temp') and c[0] in RENAME:
                    c[4] = f'{c[4]} (renamed from {c[0]} of the UISS to the name of the existing Pra Daily Order column)'
                    c[0] = RENAME[c[0]]
                cols.append(tuple(c))
            tables.setdefault(t['name'], (t['description'], cols))
    pra = json.load(open(os.path.join(HERE, 'pra_structure.json'), encoding='utf-8'))
    gt = json.load(open(os.path.join(HERE, 'gtopas_structure.json'), encoding='utf-8'))
    for name, (desc, notes) in PRA_NOTES.items():
        doc = {c[0]: c for c in gt[name]['columns']}
        cols = []
        for c in pra[name]['columns']:
            d = doc.get(c[0])
            typ, null = (d[1], d[3]) if d else (c[1] + ' (inferred)', c[3])
            cols.append((c[0], typ, c[2], null, '; '.join(x for x in (notes.get(c[0], ''), d[4] if d else 'not in the DB structure document', c[4]) if x)))
        tables[name] = (desc + ' Columns from the data export (20-Oct), types from GTOPAS_SPS_DB_Structure_20240423.', cols)
        used[name] = EXTRA_USED.get(name, [])
    for name in ('TB_R_DAILY_ORDER_MANIFEST', 'TB_R_DAILY_ORDER_PART', 'TB_R_CASE_LABEL_LAST_SEQ', 'TB_M_PART_MASTER'):
        desc = tables.get(name, ('',))[0] or ''
        tables[name] = (desc + f" Full structure: GTOPAS_SPS_DB_Structure_20240423 sheet {gt[name]['sheet']}.",
                        [tuple(c) for c in gt[name]['columns']])
    used['TB_M_PART_MASTER'] = sorted(set(used.get('TB_M_PART_MASTER', [])) | {'XD01', 'XD02'})
    return tables, used


def norm(col):
    return col.split(' / ')[0].split(' (')[0].strip()


def fk_columns(tables):
    fk = {}
    for parent, _, child, ccols, _, _ in RELATIONS:
        names = [norm(c) for c in re.split(r'[,+]', ccols)]
        cols = [norm(c[0]) for c in tables[child][1]]
        if ccols.startswith('unique key'):
            names = [norm(c[0]) for c in tables[child][1] if c[2] == 'Y']
        fk.setdefault(child, set()).update(n for n in names if n in cols)
    return fk


def shown(name, tables):
    cols = tables[name][1]
    if name in SHOW:
        keep = [c for c in cols if norm(c[0]) in SHOW[name]]
    else:
        keep = [c for c in cols if c[0] not in AUDIT]
    return keep, len(cols) - len(keep)


def table(ws, r, cols, widths, rows, head='1F3864'):
    for c, (t, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(r, c, t)
        cell.font, cell.fill, cell.border = F(9, True, 'FFFFFF'), FILL(head), BOX
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cur = ws.column_dimensions[get_column_letter(c)].width
        ws.column_dimensions[get_column_letter(c)].width = max(cur if cur and cur != 13 else 0, w)
    for row in rows:
        r += 1
        for c, v in enumerate(row, 1):
            cell = ws.cell(r, c, v)
            cell.font, cell.border = F(9), BOX
            cell.alignment = Alignment(wrap_text=True, vertical='top', horizontal='right' if isinstance(v, (int, float)) else 'left')
    return r


def erd_sheet(wb, tables, fk):
    ws = wb.active
    ws.title = 'ERD'
    ws.sheet_view.showGridLines = False
    ws['B1'] = 'Crossdock – Concept ERD (function list v2, XD01 – XD15)'
    ws['B1'].font = F(14, True, '1F3864')
    ws['B2'] = ('Entities = tables used by the Crossdock functions (columns from the UISS; audit columns and unused G-TOPAS columns are hidden, see sheet '
                'Column Definition). Lines = relationships (sheet Relationship); 1 / N at the line ends. Dashed line = logical relationship (no FK).')
    ws['B2'].font = F(9, False, '595959')
    # legend (row 3)
    for i, (kind, (label, fill, font)) in enumerate(KIND.items()):
        c = 2 + i * 4
        ws.merge_cells(start_row=3, start_column=c, end_row=3, end_column=c + 2)
        for cc in range(c, c + 3):
            ws.cell(3, cc).fill, ws.cell(3, cc).border = FILL(fill), BOX
        cell = ws.cell(3, c, label)
        cell.font, cell.alignment = F(8, True, font), Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell = ws.cell(3, 2 + len(KIND) * 4, 'PK = primary key · FK = foreign key (logical) · 1 / N = cardinality at the line ends')
    cell.font = F(8, False, '595959')
    ws.row_dimensions[3].height = 24

    widths = {1: W_GAP}
    gcol = []
    for g in range(len(LAYOUT)):
        c0 = 2 + g * 4
        gcol.append(c0)
        widths.update({c0: W_NAME, c0 + 1: W_TYPE, c0 + 2: W_KEY, c0 + 3: W_GAP})
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w
    for r in range(R_COR, R_COR + N_COR):
        ws.row_dimensions[r].height = 6
    r0 = R_COR + N_COR + 1
    pos, last_row = {}, r0                     # table -> (group, header row, {column: row})
    for g, names in enumerate(LAYOUT):
        r = r0
        c0 = gcol[g]
        for name in names:
            label, fill, font = KIND[TABLE_KIND[name]]
            cols, hidden = shown(name, tables)
            ws.merge_cells(start_row=r, start_column=c0, end_row=r, end_column=c0 + 2)
            cell = ws.cell(r, c0, name)
            cell.font, cell.alignment = F(9, True, font), Alignment(horizontal='center', vertical='center')
            for cc in range(c0, c0 + 3):
                ws.cell(r, cc).fill = FILL(fill)
                ws.cell(r, cc).border = BOX
            ws.row_dimensions[r].height = 18
            rows = {}
            for col in cols:
                r += 1
                n = norm(col[0])
                rows[n] = r
                key = ', '.join(k for k, on in (('PK', col[2] == 'Y'), ('FK', n in fk.get(name, ()))) if on)
                for cc, v in ((c0, col[0]), (c0 + 1, col[1]), (c0 + 2, key)):
                    cell = ws.cell(r, cc, v)
                    cell.font = F(8, cc == c0 and col[2] == 'Y', '7B3F00' if key.startswith('PK') else ('1F3864' if key else '000000'))
                    cell.border = BOX
                    cell.alignment = Alignment(vertical='center', horizontal='center' if cc == c0 + 2 else 'left')
                    if name == '#TEMP_INSTRUCTION':
                        cell.fill = FILL('F2F2F2')
            if hidden:
                r += 1
                ws.merge_cells(start_row=r, start_column=c0, end_row=r, end_column=c0 + 2)
                cell = ws.cell(r, c0, f'… {hidden} more columns (sheet Column Definition)')
                cell.font = F(8, False, '808080')
                for cc in range(c0, c0 + 3):
                    ws.cell(r, cc).border = BOX
            pos[name] = (g, rows)
            pos[name] = (g, pos[name][1], (r - len(cols) - (1 if hidden else 0), r))
            r += 3
        last_row = max(last_row, r)

    # geometry for the shapes
    col_x, x = {}, 0
    for col in range(1, gcol[-1] + 5):
        col_x[col] = x
        x += int((ws.column_dimensions[get_column_letter(col)].width or 8.43) * 7 + 5)
    row_y, y = {}, 0
    for r in range(1, last_row + 3):
        row_y[r] = y
        y += (ws.row_dimensions[r].height or 15) * 4 / 3
    sh = Shapes({'col_x': col_x, 'row_y': row_y})

    def side(name, right):
        g = pos[name][0]
        return col_x[gcol[g] + 3] if right else col_x[gcol[g]]

    def gap_mid(g, k):          # gap column right of group g (g = -1: column A)
        c = gcol[g] + 3 if g >= 0 else 1
        return col_x[c] + (col_x[c + 1] - col_x[c]) / 2 + (k % 3 - 1) * 5

    def key_row(name, cols_text):
        rows = pos[name][1]
        for n in [norm(c) for c in re.split(r'[,+]', cols_text)]:
            if n in rows:
                return rows[n]
        if cols_text.startswith(('unique key', 'order line')):
            return min(rows.values())
        return pos[name][2][0]

    corridor = 0
    for k, (parent, pcols, child, ccols, card, meaning) in enumerate(RELATIONS):
        gp, gc = pos[parent][0], pos[child][0]
        py = row_y[key_row(parent, pcols)] + 10
        cy = row_y[key_row(child, ccols)] + 10
        logical = 'logical' in meaning
        if gp == gc:
            xg = gap_mid(gp, k)
            pts = [(side(parent, True), py), (xg, py), (xg, cy), (side(child, True), cy)]
            p_end, c_end = (side(parent, True), py), (side(child, True), cy)
        elif abs(gp - gc) == 1:
            right = gc > gp
            xg = gap_mid(min(gp, gc), k)
            pts = [(side(parent, right), py), (xg, py), (xg, cy), (side(child, not right), cy)]
            p_end, c_end = pts[0], pts[-1]
        else:
            right = gc > gp
            xs = gap_mid(gp if right else gp - 1, k)
            xt = gap_mid(gc - 1 if right else gc, k)
            yc = row_y[R_COR + corridor % N_COR] + 4
            corridor += 1
            pts = [(side(parent, right), py), (xs, py), (xs, yc), (xt, yc), (xt, cy), (side(child, not right), cy)]
            p_end, c_end = pts[0], pts[-1]
        sh.path(f'rel {parent} - {child}', pts, color='2F5597' if not logical else '7F7F7F', lw=1, dash='dash' if logical else None, tail=False)
        many = card.split(':')[1].strip()
        for (ex, ey), text, toward in ((p_end, '1', pts[1][0]), (c_end, many, pts[-2][0])):
            dx = 3 if toward > ex else -27
            sh.shape(f'card {parent}-{child} {text}', ex + dx, ey - 13, 24, 11, fill=None, line=None,
                     paras=[([(text, 700, True, 'C00000')], 'ctr')], ins=0)
    ws.freeze_panes = 'A4'
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    return sh.xml()


def build():
    tables, used = load_tables()
    fk = fk_columns(tables)
    names = [n for g in LAYOUT for n in g]
    assert set(names) == set(tables), set(tables) ^ set(names)
    wb = Workbook()
    drawing = erd_sheet(wb, tables, fk)

    ws = wb.create_sheet('Table List')
    ws.sheet_view.showGridLines = False
    ws['A1'] = 'Table list'
    ws['A1'].font = F(14, True, '1F3864')
    sim_rows = {s[0]: len(s[3]) for s in SIM}
    table(ws, 3, ['No', 'Table', 'Kind', 'Description', 'Used by (function)', 'Rows in Simulation Data'], [5, 32, 26, 80, 26, 12],
          [[i + 1, n, KIND[TABLE_KIND[n]][0], tables[n][0], ', '.join(sorted(set(used[n]))) or '-', sim_rows.get(n, 0)] for i, n in enumerate(names)])
    ws.freeze_panes = 'A4'

    ws = wb.create_sheet('Relationship')
    ws.sheet_view.showGridLines = False
    ws['A1'] = 'Relationships'
    ws['A1'].font = F(14, True, '1F3864')
    table(ws, 3, ['No', 'Parent table', 'Parent key', 'Child table', 'Child key', 'Cardinality', 'Meaning'], [5, 30, 26, 30, 40, 11, 50],
          [[i + 1, *r] for i, r in enumerate(RELATIONS)])
    ws.freeze_panes = 'A4'

    ws = wb.create_sheet('Column Definition')
    ws.sheet_view.showGridLines = False
    ws['A1'] = 'Column definition (from the UISS of function list v2)'
    ws['A1'].font = F(14, True, '1F3864')
    rows = []
    for n in names:
        for i, c in enumerate(tables[n][1], 1):
            rows.append([n, i, c[0], c[1], 'Y' if c[2] == 'Y' else '', 'Y' if norm(c[0]) in fk.get(n, ()) else '', c[3], c[4]])
    table(ws, 3, ['Table', 'No', 'Column', 'Type', 'PK', 'FK', 'Null', 'Description'], [30, 5, 30, 14, 5, 5, 5, 90], rows)
    ws.freeze_panes = 'A4'
    ws.auto_filter.ref = f'A3:H{3 + len(rows)}'

    ws = wb.create_sheet('Simulation Data')
    ws.sheet_view.showGridLines = False
    ws['A1'] = 'Simulation data (one consistent scenario across the tables)'
    ws['A1'].font = F(14, True, '1F3864')
    r = 2
    for line in SCENARIO:
        ws.cell(r, 1, '• ' + line).font = F(9)
        r += 1
    for c in range(1, 20):
        ws.column_dimensions[get_column_letter(c)].width = 17
    for i, (name, source, cols, data) in enumerate(SIM, 1):
        r += 2
        ws.cell(r, 1, f'{i}. {name}').font = F(10, True, '1F3864')
        ws.cell(r, 4, f'Written by: {source}').font = F(8, False, '595959')
        head = KIND[TABLE_KIND[name]][1]
        r = table(ws, r + 1, cols, [17] * len(cols), data, head=head)
    ws.freeze_panes = 'A2'

    for w in wb.worksheets[1:]:
        w.page_setup.orientation = 'landscape'
        w.page_setup.fitToWidth, w.page_setup.fitToHeight = 1, 0
        w.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(OUT)
    add_drawings(OUT, [w.title for w in wb.worksheets], {'ERD': drawing})
    print('written', OUT)


if __name__ == '__main__':
    build()
