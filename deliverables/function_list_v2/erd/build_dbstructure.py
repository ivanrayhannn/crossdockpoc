"""Build Crossdock_DB_Structure.xlsx in the layout of the DB Structure document (GTOPAS_SPS_DB_Structure): Revision, Table List and one
sheet per table (header block, Database Design / Name / Row Size / PK Row Size / Logging, Desc, field list). Columns come from the same
sources as the ERD (build_erd.load_tables). Run: python3 build_dbstructure.py (from this folder)."""
import os, re
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

from build_erd import load_tables, norm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Crossdock_DB_Structure.xlsx')

# id, physical name, logical name, design kind, description
TABLES = [
    ('MST-01', 'TB_M_PART_CANDIDATE', 'Crossdock Part Candidate', 'Master', 'Candidate / Active / Inactive crossdock part (Kanban Crossdock Master of XD01, per period).'),
    ('MST-02', 'TB_M_PART_CANDIDATE_DEST', 'Part Mapping per Destination', 'Master', 'Case/Day per part, period and destination (Export Crossdock Master of XD01, per order type).'),
    ('HIS-01', 'TB_H_PART_CANDIDATE', 'Part Candidate History', 'History', 'Every change of a crossdock part (screen, upload, calculation) for the History setting.'),
    ('HIS-03', 'TB_H_STG_APPOLE_KANBAN', 'Staging AP POLE Kanban', 'History', 'Kanban changes in the AP POLE Kanban upload format (LLM9Q910) and the header of the part (OPERATION_TYPE 1 to 5); read by XD07 (proposal 23-Nov).'),
    ('HIS-04', 'TB_H_STG_APPOLE_EXPORT', 'Staging AP POLE Export', 'History', 'Destination changes in the AP POLE Export upload format (LLM9Q880); read by XD07 (proposal 23-Nov).'),
    ('HIS-05', 'TB_H_STG_GTOPAS', 'Staging GTOPAS', 'History', 'Part + destination Add / Delete for GTOPAS WVJA5204; read by XD06 (proposal 23-Nov).'),
    ('VW-01', 'V_APPOLE_UPLOAD_KANBAN', 'View AP POLE Kanban Upload', 'View', 'File 2 KANBAN (LLM9Q910) of XD07: Kanban rows of a run with OPERATION_TYPE 1 to 4 (proposal 26-Nov).'),
    ('VW-02', 'V_APPOLE_UPLOAD_EXPORT', 'View AP POLE Export Upload', 'View', 'Files 1 EXPORT_PRE and 3 EXPORT_POST (LLM9Q880) of XD07: Export rows of a run with FILE_NO and ROW_ORDER (proposal 26-Nov).'),
    ('VW-03', 'V_GTOPAS_CROSSDOCK', 'View GTOPAS Crossdock', 'View', 'Rows of the GTOPAS screen WVJA5204 for XD06 and the count of the parent flow (proposal 26-Nov).'),
    ('HIS-02', 'TB_H_CROSSDOCK_ORDER_CHANGE', 'Crossdock Order Change History', 'History', 'Change Order Number (XD11): cancelled qty in an ASN moved to other lines.'),
    ('TR-01', 'TB_R_PART_DAD_RESULT', 'DAD Volume Calculation Result', 'Transaction', 'Result of XD05 process 1 per part and period.'),
    ('TR-03', 'TB_R_INSTRUCTION', 'Crossdock Instruction', 'Transaction', 'Real mapping of Create ASN: case x customer order line x PO.'),
    ('TR-05', 'TB_R_CROSSDOCK_CASE_HOLD', 'Crossdock Case Hold', 'Transaction', 'Customer order lines of a supplier case held by the D/S team on XD10 (Hold check box): the held pcs take no PO, the PO qty goes to the next orders (kept until released).'),
    ('TR-06', 'TB_R_CROSSDOCK_PART_HOLD', 'Crossdock Part Hold', 'Transaction', 'Part Number on hold by the D/S team on XD10 (no ASN for the part while HOLD_FLAG Y).'),
    ('TR-07', 'TB_T_INSTRUCTION_H', 'Crossdock ASN Draft Header', 'Transaction', 'Draft of [Search] per unit (Customer Order Date + Part Number + supplier), per company of the login user (DR XD09).'),
    ('TR-08', 'TB_T_INSTRUCTION_D', 'Crossdock ASN Draft Detail', 'Transaction', 'Draft of [Search] per pc: PO, CASE_NO and hold status (DR XD09).'),
    ('REP-01', 'TB_M_H0125_DESTINATION', 'Destination Master (H0125)', 'Replicated', 'Destination master replicated from DB Surrounding by XD13.'),
    ('REP-02', 'TB_R_ACTUAL_DEMAND_SUMMARY', 'Actual Demand Summary', 'Replicated', 'Actual demand replicated from DB Surrounding by XD04.'),
    ('REP-03', 'TB_R_H0253_ORDER_CONTROL_PRE', 'Order Control Info (H0253)', 'Replicated', 'Customer order lines replicated by XD08, with NSP columns HOLD_FLAG / PO_MAPPED_FLAG / UPD_STATUS (NULL / 6 / 2).'),
    ('EXT-01', 'TB_M_PART_MASTER', 'Part Master', 'Existing', 'Existing part master (reference; Crossdock uses PART_NAME).'),
    ('EXT-02', 'TB_R_PRA_DAILY_ORDER_MANIFEST', 'Pra Daily Order Manifest', 'Existing', 'Existing (reference): crossdock order = CROSS_DOCK_FLAG X.'),
    ('EXT-03', 'TB_R_PRA_DAILY_ORDER_PART', 'Pra Daily Order Part', 'Existing', 'Existing (reference): part data of the crossdock manifest.'),
    ('EXT-04', 'TB_R_DAILY_ORDER_MANIFEST', 'Daily Order Manifest', 'Existing', 'Existing (reference): ASN manifest written by Submit ASN.'),
    ('EXT-05', 'TB_R_DAILY_ORDER_PART', 'Daily Order Part', 'Existing', 'Existing (reference): ASN part x case written by Submit ASN.'),
    ('EXT-06', 'TB_R_CASE_LABEL_LAST_SEQ', 'Case Label Last Seq', 'Existing', 'Existing (reference): last sequence of the ASN number and the case label.'),
]
ID_FILL = {'VW': 'FFE699', 'MST': '92D050', 'HIS': 'B4C6E7', 'TR': 'F4B084', 'TMP': 'D9D9D9', 'REP': 'CCC0DA', 'EXT': 'BFBFBF'}
GREY = PatternFill('solid', fgColor='FFD9D9D9')
thin = Side(style='thin', color='FF000000')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F10, F10B, F8 = Font(name='Arial', size=10), Font(name='Arial', size=10, bold=True), Font(name='Arial', size=8)
SIZE = {'NUMERIC': 9, 'NUMBER': 9, 'INT': 4, 'BIGINT': 8, 'DATE': 3, 'DATETIME': 8, 'TIMESTAMP': 8}


def col(n):           # 1-based column number from a letter
    from openpyxl.utils import column_index_from_string
    return column_index_from_string(n)


def put(ws, r, a, b, value, label=False, font=None, align='left'):
    ca, cb = col(a), col(b)
    if cb > ca:
        ws.merge_cells(start_row=r, start_column=ca, end_row=r, end_column=cb)
    for c in range(ca, cb + 1):
        ws.cell(r, c).border = BOX
        if label:
            ws.cell(r, c).fill = GREY
    cell = ws.cell(r, ca, value)
    cell.font = font or F10
    cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=False, shrink_to_fit=True)


def parse_type(t):
    t = t.replace(' (inferred)', '').replace('+', '')
    m = re.match(r'^([A-Z#]+)\s*\(([^,)]*)(?:,\s*([^)]*))?\)', t)
    if m:
        ln = m.group(2)
        return m.group(1), int(ln) if ln.isdigit() else ln, m.group(3) or ''
    return t, '', ''


def size_of(typ, ln):
    if typ in ('VARCHAR', 'CHAR', 'NVARCHAR'):
        return ln if isinstance(ln, int) else None
    return SIZE.get(typ, None)


def logical(name, desc):
    if ';' in desc and len(desc.split(';')[0]) <= 40:
        return desc.split(';')[0].strip()
    return name.replace('_', ' ').title().replace(' Cd', ' Code').replace(' Dt', ' Date')


def header(ws, title, page):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 0.57
    for c in range(2, col('CW') + 1):
        ws.column_dimensions[L(c)].width = 1.43
    put(ws, 2, 'B', 'G', 'Phase', True)
    put(ws, 2, 'H', 'N', 'FSD', font=F10B)
    put(ws, 2, 'O', 'AA', 'Project Name', True)
    put(ws, 2, 'AB', 'CJ', 'Crossdock Optimization (NSP)')
    put(ws, 2, 'CK', 'CN', 'Page', True)
    put(ws, 2, 'CO', 'CV', page)
    for r, lab, val, lab2, d in ((3, 'Block Name', 'Crossdock', 'Created', '20-Oct-26'), (4, 'Document Name', 'DB Structure', 'Updated', '26-Nov-26')):
        put(ws, r, 'B', 'N', lab, True)
        put(ws, r, 'O', 'AH', val)
        put(ws, r, 'AI', 'AS', 'Function Name' if r == 3 else 'Title', True)
        put(ws, r, 'AT', 'BV', 'Crossdock (XD01 – XD15)' if r == 3 else title)
        put(ws, r, 'BW', 'CB', lab2, True)
        put(ws, r, 'CC', 'CJ', d)
        put(ws, r, 'CK', 'CN', 'By', True)
        put(ws, r, 'CO', 'CV', 'FID Rayhan')


REVISIONS = [
    ('0.1', '20-Oct-2026', 'Initial Draft: Crossdock tables (new, replicated, existing reference)'),
    ('0.2', '22-Nov-2026', 'TB_H_PART_CANDIDATE_STG_SYNC (staging of the sync); sync columns removed from TB_M_PART_CANDIDATE'),
    ('0.3', '23-Nov-2026', 'Staging per target: TB_H_PART_CANDIDATE_STG_SYNC replaced by TB_H_STG_APPOLE_KANBAN, TB_H_STG_APPOLE_EXPORT and TB_H_STG_GTOPAS; '
                           'EFFECTIVE_START_DATE removed from TB_M_PART_CANDIDATE (a part takes effect from its first registered period)'),
    ('0.4', '26-Nov-2026', 'Staging tables: SYNC_RUN_ID removed (the run is SYNC_DT, one value per [Sync] click); SYNC_STATUS 0 / 1 (one unsent row per key)'),
    ('0.5', '26-Nov-2026', 'TB_H_STG_APPOLE_KANBAN / _EXPORT: EFFECTIVE_MONTH_YEAR removed (same value as PERIOD); the views make Effective Month / Year for the upload file'),
    ('0.6', '26-Nov-2026', 'Views V_APPOLE_UPLOAD_KANBAN, V_APPOLE_UPLOAD_EXPORT and V_GTOPAS_CROSSDOCK (new) added: the robots read the views only'),
]


def proposal(tables, used):
    """Overlay of the 23-Nov proposal (proposal_staging_sync/build_table_proposal_v2.py) on the tables of the UISS specs."""
    import importlib.util
    sp = importlib.util.spec_from_file_location('tp2', os.path.join(HERE, 'proposal_staging_sync', 'build_table_proposal_v2.py'))
    tp = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(tp)
    desc, cols = tables['TB_M_PART_CANDIDATE']
    tables['TB_M_PART_CANDIDATE'] = (desc, [c for c in cols if c[0] != 'EFFECTIVE_START_DATE'])
    tables.pop('TB_H_PART_CANDIDATE_STG_SYNC', None)

    def conv(rows):
        out = []
        for name, typ, pk, null, default, file_col, d, _ in rows:
            label = file_col or name.replace('_', ' ').title().replace(' Dt', ' Date').replace(' Id', ' ID').replace('Stg ', 'Staging ').replace('Nsp ', 'NSP ')
            text = f'{label}; ' + d + (f' (default {default})' if default and default != 'identity' else '')
            out.append((name, typ, pk, null, text))
        return out
    for name, rows, d, fids in (
            ('TB_H_STG_APPOLE_KANBAN', tp.KAN, 'Kanban rows for AP POLE in the LLM9Q910 format', ['XD01', 'XD02', 'XD05', 'XD07']),
            ('TB_H_STG_APPOLE_EXPORT', tp.EXP, 'Export rows for AP POLE in the LLM9Q880 format', ['XD01', 'XD03', 'XD05', 'XD07']),
            ('TB_H_STG_GTOPAS', tp.GTO, 'Part + destination rows for GTOPAS WVJA5204', ['XD01', 'XD03', 'XD05', 'XD06'])):
        tables[name] = (d, conv(rows))
        used[name] = fids
    # views read by the robots: no key, no logging; the source of each column goes in the description
    for name, purpose, d, rows in tp.VIEWS:
        tables[name] = (d, [(c, typ, '', 'Y', f"{file_col or c.replace('_', ' ').title()}; {d2.rstrip('.') + '. ' if d2 else ''}Source: {src}."
                             + ('' if file_col else ' Helper column, not written to the file / screen.'))
                            for c, typ, src, file_col, d2 in rows])
        used[name] = ['XD06'] if 'GTOPAS' in name else ['XD07']


def build():
    tables, used = load_tables()
    proposal(tables, used)
    wb = Workbook()
    ws = wb.active
    ws.title = 'Revision'
    header(ws, 'Revision', '1')
    put(ws, 6, 'B', 'G', 'Rev', True)
    put(ws, 6, 'H', 'S', 'Date', True)
    put(ws, 6, 'T', 'CJ', 'Description', True)
    put(ws, 6, 'CK', 'CV', 'By', True)
    for i, (rev, d, text) in enumerate(REVISIONS):
        put(ws, 7 + i, 'B', 'G', rev, align='center')
        put(ws, 7 + i, 'H', 'S', d)
        put(ws, 7 + i, 'T', 'CJ', text)
        put(ws, 7 + i, 'CK', 'CV', 'FID Rayhan')

    tl = wb.create_sheet('Table List')
    header(tl, 'Table List', '2')
    heads = [('B', 'F', 'No'), ('G', 'V', 'Logical Table Name'), ('W', 'AN', 'Physical Table Name'), ('AO', 'AU', 'Row Size'), ('AV', 'BB', 'PK Row Size'),
             ('BC', 'BG', 'Logging'), ('BH', 'BL', 'Max Record'), ('BM', 'BR', 'Table Size'), ('BS', 'CV', 'Description')]
    for a, b, text in heads:
        put(tl, 6, a, b, text, True, align='center')
    for n, (tid, name, lname, kind, desc) in enumerate(TABLES, 1):
        cols = tables[name][1]
        sizes, pk_sizes, unknown = 0, 0, False
        for c in cols:
            typ, ln, _ = parse_type(c[1])
            s = size_of(typ, ln)
            if s is None:
                unknown = True
                continue
            sizes += s
            if c[2] == 'Y':
                pk_sizes += s
        r = 6 + n
        tl.cell(r, 1, n).font = F8
        put(tl, r, 'B', 'F', tid, font=F8)
        for c in range(col('B'), col('F') + 1):
            tl.cell(r, c).fill = PatternFill('solid', fgColor='FF' + ID_FILL[tid.split('-')[0]])
        put(tl, r, 'G', 'V', lname, font=F8)
        put(tl, r, 'W', 'AN', name, font=F8)
        put(tl, r, 'AO', 'AU', f'{sizes}{"*" if unknown else ""}', font=F8, align='right')
        put(tl, r, 'AV', 'BB', pk_sizes, font=F8, align='right')
        put(tl, r, 'BC', 'BG', 'No' if kind == 'View' else 'Yes', font=F8, align='center')
        put(tl, r, 'BH', 'BL', '', font=F8)
        put(tl, r, 'BM', 'BR', '', font=F8)
        put(tl, r, 'BS', 'CV', f'{kind}: {desc}', font=F8)
    r = 8 + len(TABLES)
    tl.cell(r, 2, '* Row Size without the columns whose length is still TBD.  MST / HIS / TR / TMP = new Crossdock table · REP = replicated from DB Surrounding · '
                  'EXT = existing NSP table (reference only, structure from GTOPAS_SPS_DB_Structure / data export)').font = Font(name='Arial', size=8, italic=True)

    for n, (tid, name, lname, kind, desc) in enumerate(TABLES, 3):
        ws = wb.create_sheet(tid)
        header(ws, lname, str(n))
        cols = tables[name][1]
        pk_order, sizes, pk_sizes = {}, 0, 0
        for c in cols:
            if c[2] == 'Y':
                pk_order[c[0]] = len(pk_order) + 1
            typ, ln, _ = parse_type(c[1])
            s = size_of(typ, ln) or 0
            sizes += s
            pk_sizes += s if c[2] == 'Y' else 0
        put(ws, 6, 'B', 'N', 'Database Design', True)
        put(ws, 6, 'O', 'AH', kind)
        put(ws, 6, 'AI', 'AN', 'Name', True)
        put(ws, 6, 'AO', 'BF', name)
        put(ws, 6, 'BG', 'BO', 'Row Size (B)', True)
        put(ws, 6, 'BP', 'BT', sizes, align='right')
        put(ws, 6, 'BU', 'CE', 'PK Row Size (B)', True)
        put(ws, 6, 'CF', 'CJ', pk_sizes, align='right')
        put(ws, 6, 'CK', 'CQ', 'Logging', True)
        put(ws, 6, 'CR', 'CV', 'No' if kind == 'View' else 'Yes', align='center')
        put(ws, 7, 'B', 'G', 'Desc', True)
        put(ws, 7, 'H', 'CV', f'{lname}: {desc} Used by: {", ".join(sorted(set(used.get(name, [])))) or "-"}.')
        heads = [('B', 'D', 'No.'), ('E', 'U', 'Field Name'), ('V', 'AL', 'Logical Name'), ('AM', 'AR', 'Type'), ('AS', 'AV', 'Len'), ('AW', 'AZ', 'Prec'),
                 ('BA', 'BC', 'PK'), ('BD', 'BF', 'N-N'), ('BG', 'BM', 'Default'), ('BN', 'CV', 'Description')]
        for a, b, text in heads:
            put(ws, 9, a, b, text, True, align='center')
        for i, c in enumerate(cols, 1):
            r = 9 + i
            typ, ln, prec = parse_type(c[1])
            desc_c = c[4].split(';', 1)[1].strip() if ';' in c[4] and len(c[4].split(';')[0]) <= 40 else c[4]
            values = [('B', 'D', f'{i:02d}', 'center'), ('E', 'U', c[0], 'left'), ('V', 'AL', logical(norm(c[0]), c[4]), 'left'), ('AM', 'AR', typ, 'left'),
                      ('AS', 'AV', ln, 'center'), ('AW', 'AZ', prec, 'center'), ('BA', 'BC', pk_order.get(c[0], ''), 'center'),
                      ('BD', 'BF', 'x' if c[3] == 'N' else '', 'center'), ('BG', 'BM', '', 'left'), ('BN', 'CV', desc_c, 'left')]
            for a, b, v, al in values:
                put(ws, r, a, b, v, font=F8, align=al)
        ws.page_setup.orientation = 'landscape'
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    for w in (wb['Revision'], tl):
        w.page_setup.orientation = 'landscape'
        w.page_setup.fitToWidth, w.page_setup.fitToHeight = 1, 0
        w.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(OUT)
    print('written', OUT)


if __name__ == '__main__':
    build()
