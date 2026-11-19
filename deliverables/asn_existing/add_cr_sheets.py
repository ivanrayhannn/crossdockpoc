"""Adds a sheet "CR Crossdock" to the existing DR UISS ASN03 (screen) and ASN04 (upload batch), from ASN_Existing.xlsx (14-Nov).

The sheet is added at XML level: every existing part (drawings, images, external links, VML, custom XML) is copied byte for byte.
Only workbook.xml, workbook.xml.rels, [Content_Types].xml and styles.xml get an appended entry.
Run: python3 add_cr_sheets.py  (reads source/, writes the files next to this script)
"""
import os
import re
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_NAME = 'CR Crossdock'
UPDATED = '19-Nov-2026'

# style keys -> (font, fill, border, alignment)
FONTS = {'n': '<font><sz val="10"/><name val="Arial"/></font>',
         'b': '<font><b/><sz val="10"/><name val="Arial"/></font>',
         't': '<font><b/><sz val="14"/><name val="Arial"/></font>',
         's': '<font><b/><sz val="11"/><name val="Arial"/></font>',
         'i': '<font><i/><sz val="9"/><color rgb="FF595959"/><name val="Arial"/></font>'}
FILLS = {'none': None,
         'head': '<fill><patternFill patternType="solid"><fgColor rgb="FFDDEBF7"/><bgColor indexed="64"/></patternFill></fill>',
         'meta': '<fill><patternFill patternType="solid"><fgColor rgb="FFF2F2F2"/><bgColor indexed="64"/></patternFill></fill>',
         'new': '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill>'}
BORDER = '<border><left style="thin"><color rgb="FF999999"/></left><right style="thin"><color rgb="FF999999"/></right><top style="thin"><color rgb="FF999999"/></top><bottom style="thin"><color rgb="FF999999"/></bottom><diagonal/></border>'
STYLES = {  # key: (font, fill, bordered)
    'title': ('t', 'none', False), 'sec': ('s', 'none', False), 'text': ('n', 'none', False), 'note': ('i', 'none', False),
    'th': ('b', 'head', True), 'td': ('n', 'none', True), 'tdb': ('b', 'none', True), 'tdnew': ('n', 'new', True),
    'mk': ('b', 'meta', True), 'mv': ('n', 'none', True)}


def add_styles(styles_xml):
    """Append fonts / fills / border / cellXfs for STYLES; returns (new xml, {key: xf index})."""
    def append(tag, items, xml):
        m = re.search(r'<%s count="(\d+)"[^>]*>' % tag, xml)
        start = int(m.group(1))
        end = xml.index('</%s>' % tag)
        xml = xml[:end] + ''.join(items) + xml[end:]
        xml = xml[:m.start()] + m.group(0).replace('count="%d"' % start, 'count="%d"' % (start + len(items))) + xml[m.end():]
        return xml, start
    keys_f = list(FONTS)
    styles_xml, f0 = append('fonts', [FONTS[k] for k in keys_f], styles_xml)
    keys_fill = [k for k in FILLS if FILLS[k]]
    styles_xml, fi0 = append('fills', [FILLS[k] for k in keys_fill], styles_xml)
    styles_xml, b0 = append('borders', [BORDER], styles_xml)
    xfs, idx = [], {}
    m = re.search(r'<cellXfs count="(\d+)"', styles_xml)
    x0 = int(m.group(1))
    for n, (k, (font, fill, bordered)) in enumerate(STYLES.items()):
        fid = f0 + keys_f.index(font)
        fill_id = fi0 + keys_fill.index(fill) if FILLS[fill] else 0
        bid = b0 if bordered else 0
        wrap = '' if k in ('title', 'sec') else ' wrapText="1"'
        xfs.append(f'<xf numFmtId="0" fontId="{fid}" fillId="{fill_id}" borderId="{bid}" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">'
                   f'<alignment vertical="top"{wrap}/></xf>')
        idx[k] = x0 + n
    styles_xml, _ = append('cellXfs', xfs, styles_xml)
    return styles_xml, idx


COLS = 'BCDEFG'
WIDTHS = {'A': 2, 'B': 7, 'C': 30, 'D': 46, 'E': 46, 'F': 30, 'G': 18}


def lines(txt, width):
    """Rough number of wrapped lines of a text in a column of this width (Arial 10)."""
    cap = max(1, int(width * 0.95))
    total = 0
    for part in str(txt).split('\n'):
        n, cur = 1, 0
        for word in part.split(' '):
            w = len(word)
            if cur and cur + 1 + w > cap:
                n, cur = n + 1, 0
            while w > cap:  # a long name without spaces breaks inside the word
                n, w = n + 1, w - cap
            cur = cur + (1 if cur else 0) + w
        total += n
    return total


def sheet_xml(rows, idx):
    """rows: list of rows; a row is a list of (style key, text) for columns B.. (None = empty).
    A row with one text / note cell is merged over B:F. Row heights are set from the wrapped text (Excel does not fit them on open)."""
    out, merges = [], []
    widths = [WIDTHS[c] for c in COLS]
    span = sum(WIDTHS[c] for c in 'BCDEF')
    for r, row in enumerate(rows, 1):
        n = 1
        if len(row) == 1 and row[0] and row[0][0] in ('text', 'note'):
            merges.append(f'B{r}:F{r}')
            n = lines(row[0][1], span)
        elif row and any(cell and cell[0] not in ('title', 'sec') for cell in row):
            n = max(lines(cell[1], widths[c]) for c, cell in enumerate(row) if cell)
        cells = []
        for c, cell in enumerate(row):
            if cell is None:
                continue
            st, txt = cell
            ref = f'{COLS[c]}{r}'
            if txt == '':
                cells.append(f'<c r="{ref}" s="{idx[st]}"/>')
            else:
                cells.append(f'<c r="{ref}" s="{idx[st]}" t="inlineStr"><is><t xml:space="preserve">{escape(str(txt))}</t></is></c>')
        ht = f' ht="{max(13.2, 12.6 * n + 2):.1f}" customHeight="1"' if n > 1 else (' ht="20" customHeight="1"' if row and row[0] and row[0][0] == 'title' else '')
        out.append(f'<row r="{r}"{ht}>{"".join(cells)}</row>' if cells else f'<row r="{r}"/>')
    cols = ''.join(f'<col min="{n}" max="{n}" width="{w}" customWidth="1"/>' for n, w in enumerate(WIDTHS.values(), 1))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>'
            '<sheetViews><sheetView showGridLines="0" workbookViewId="0"/></sheetViews>'
            '<sheetFormatPr defaultRowHeight="13.2"/>'
            f'<cols>{cols}</cols><sheetData>{"".join(out)}</sheetData>'
            + (f'<mergeCells count="{len(merges)}">' + ''.join(f'<mergeCell ref="{m}"/>' for m in merges) + '</mergeCells>' if merges else '') +
            '<pageMargins left="0.4" right="0.4" top="0.5" bottom="0.5" header="0.3" footer="0.3"/>'
            '<pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/>'
            '</worksheet>')


def add_sheet(src, dst, rows):
    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    nums = [int(m.group(1)) for n in names for m in [re.match(r'xl/worksheets/sheet(\d+)\.xml$', n)] if m]
    new_no = max(nums) + 1
    part = f'xl/worksheets/sheet{new_no}.xml'
    wb = zin.read('xl/workbook.xml').decode('utf-8')
    rels = zin.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    ct = zin.read('[Content_Types].xml').decode('utf-8')
    styles, idx = add_styles(zin.read('xl/styles.xml').decode('utf-8'))
    assert f'name="{SHEET_NAME}"' not in wb, 'sheet already there'
    rid_no = max(int(x) for x in re.findall(r'Id="rId(\d+)"', rels)) + 1
    sheet_id = max(int(x) for x in re.findall(r'<sheet [^>]*sheetId="(\d+)"', wb)) + 1
    wb = wb.replace('</sheets>', f'<sheet name="{SHEET_NAME}" sheetId="{sheet_id}" r:id="rId{rid_no}"/></sheets>')
    rels = rels.replace('</Relationships>', f'<Relationship Id="rId{rid_no}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{new_no}.xml"/></Relationships>')
    ct = ct.replace('</Types>', f'<Override PartName="/{part}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
    zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == 'xl/workbook.xml':
            data = wb.encode('utf-8')
        elif it.filename == 'xl/_rels/workbook.xml.rels':
            data = rels.encode('utf-8')
        elif it.filename == '[Content_Types].xml':
            data = ct.encode('utf-8')
        elif it.filename == 'xl/styles.xml':
            data = styles.encode('utf-8')
        zout.writestr(it, data)
    zout.writestr(part, sheet_xml(rows, idx).encode('utf-8'))
    zout.close()
    print('written', dst, part)


def header(function_name, doc, title):
    return [
        [('mk', 'Phase'), ('mv', 'DR'), ('mk', 'Project Name'), ('mv', 'G-TOPAS Local System'), ('mk', 'Updated'), ('mv', UPDATED)],
        [('mk', 'Block'), ('mv', 'ASN'), ('mk', 'Function Name'), ('mv', function_name), ('mk', 'By'), ('mv', '[Author]')],
        [('mk', 'Doc'), ('mv', doc), ('mk', 'Title'), ('mv', title), ('mk', 'Source'), ('mv', 'ASN_Existing.xlsx (14-Nov), decisions 19-Nov')],
        [],
    ]


def table(head, body, style='td'):
    while head and head[-1] == '':  # drop empty trailing columns
        head = head[:-1]
        body = [r[:-1] for r in body]
    rows = [[('th', h) for h in head]]
    for r in body:
        rows.append([(style if not isinstance(v, tuple) else v[0], v if not isinstance(v, tuple) else v[1]) for v in r])
    return rows + [[]]


X = "Palletize Code = 'X' or CROSS_DOCK_FLAG = 'X'"
BACKGROUND = [
    [('text', "Crossdock orders are the orders with CROSS_DOCK_FLAG = 'X' in TB_R_PRA_DAILY_ORDER_MANIFEST (column name as in the BCT logic flow) "
              "and Palletize Code 'X'. A Palletize Code 'X' is always a crossdock order with CROSS_DOCK_FLAG 'X' (decided 19-Nov). "
              'Their ASN is created in the new ASN Creation (Crossdock, XDOCK) screen, per Part Number + Customer Order Date.')],
    [('text', 'The existing ASN Creation (ASN03) and ASN Upload (ASN04) stay for regular (non-crossdock) orders: '
              'crossdock orders are not taken from the pra manifest / pra part; the rest of the existing flow does not change.')],
    [],
]


def revision(rows):
    return [[('sec', 'Revision')], *table(['Rev', 'Date', 'Description', 'By', ''], rows)]


ASN03 = header('ASN03_Delivery Note / ASN Creation (Screen)', 'UISS-Screen', 'CR Crossdock: crossdock orders out of ASN Creation') + [
    [('title', 'CR Crossdock: crossdock orders are not shown in ASN Creation (regular orders only)')], [],
    *revision([['0.1', '14-Nov-2026', 'First version from ASN_Existing.xlsx', '[Author]', ''],
               ['0.2', '19-Nov-2026', "Column CROSS_DOCK_FLAG (BCT logic flow); Palletize Code 'X' also excluded; no message for a typed crossdock "
                                      'Manifest / PO; draft ASN before go-live: existing behaviour; decisions of the open points', '[Author]', '']]),
    [('sec', '1. Background')], *BACKGROUND,
    [('sec', '2. Change summary')],
    *table(['No', 'Item', 'Current', 'To Be', 'Impacted sheet'], [
        ['1', 'Get Data Manifest (Add mode: Manifest No, Order Date, PO No, [Search] of the grid)',
         'Manifests of the login supplier with remaining qty (company_cd = supplier_cd and remaining_qty >= delivery_qty).',
         ('tdnew', "Same, plus: orders with CROSS_DOCK_FLAG = 'X' (pra manifest) or Palletize Code = 'X' (pra part) are excluded. "
                   'Crossdock orders are no longer shown in Get Manifest.'),
         'Operation Desc 2.a'],
        ['2', 'Upload mode ([Upload] calls ASN04)', 'Every manifest in the file is uploaded.',
         ('tdnew', 'Only the regular rows are uploaded; rows with ' + X + ' are skipped by ASN04 (refer CR ASN04).'), 'Operation Desc 1.a'],
        ['3', 'Save / Submit ASN', 'Existing flow.',
         'No change: TB_T_ASN -> ASN Submit Creation (existing flow) -> update TB_R_PRA_DAILY_ORDER_MANIFEST / TB_R_PRA_DAILY_ORDER_PART.', '-'],
    ]),
    [('sec', '3. Process flow')],
    *table(['Step', 'Input', 'Process', 'Output', ''], [
        ['1', 'TB_R_PRA_DAILY_ORDER_MANIFEST, TB_R_PRA_DAILY_ORDER_PART', ('tdnew', 'Get Data Manifest, exclude ' + X), 'Manifest list (regular orders only)', ''],
        ['2', 'Manifest list', 'ASN Creation: crossdock orders are not shown; the supplier picks regular orders and continues the existing flow', 'TB_T_ASN', ''],
        ['3', 'TB_T_ASN', 'ASN Submit Creation (existing flow)', 'TB_R_PRA_DAILY_ORDER_MANIFEST, TB_R_PRA_DAILY_ORDER_PART', ''],
    ]),
    [('sec', '4. Logic to add in Operation Desc 2.a (Add Mode, Search Mode Condition)')],
    *table(['No', 'Field / action', 'Current condition', 'To Be condition', ''], [
        ['1', 'Manifest No (textbox)', 'if a.company_cd == b.supplier_cd && c.remaining_qty >= c.delivery_qty',
         ('tdnew', "if a.company_cd == b.supplier_cd && c.remaining_qty >= c.delivery_qty && ISNULL(b.CROSS_DOCK_FLAG, '') <> 'X' "
                   "&& UPPER(ISNULL(c.PALLETIZE_CD, '')) <> 'X'"), ''],
        ['2', 'Order Date (combobox)', 'same as above + b.manifest_no', ('tdnew', 'same as above + both crossdock conditions'), ''],
        ['3', 'PO No (search criteria, rev. 1.3) and [Search] of the grid', 'existing filter', ('tdnew', 'existing filter + both crossdock conditions'), ''],
    ]),
    [('note', 'a = sc.tb_m_user, b = nsp.tb_r_pra_daily_order_manifest, c = nsp.tb_r_pra_daily_order_part (aliases of Operation Desc 2.a). '
              'PALLETIZE_CD: table and column as in the BCT logic flow (shown here on the pra part).')], [],
    [('sec', '5. Test scenarios')],
    *table(['TC', 'Scenario', 'Data', 'Expected result', ''], [
        ['1', 'Regular order', "CROSS_DOCK_FLAG NULL / blank, Palletize Code not 'X'", 'Shown in Manifest No, Order Date and the grid; ASN created as today', ''],
        ['2', 'Crossdock order', "CROSS_DOCK_FLAG = 'X' and Palletize Code 'X'", 'Not shown in Manifest No, Order Date, PO No and the grid', ''],
        ['3', 'Supplier types a crossdock Manifest No / PO No', "CROSS_DOCK_FLAG = 'X'", 'No data (no message)', ''],
        ['4', 'Same supplier and date, regular and crossdock orders', '1 regular + 1 crossdock', 'Only the regular order is listed', ''],
        ['5', 'Upload file with a crossdock row', X, 'Crossdock row skipped by ASN04, regular rows uploaded (CR ASN04)', ''],
        ['6', 'Submit a regular ASN', 'Regular order', 'Existing result: TB_T_ASN submitted, manifest and part tables updated', ''],
        ['7', 'Draft ASN of a crossdock order made before go-live', 'TB_T_ASN draft', 'Existing behaviour (no change)', ''],
    ]),
    [('sec', '6. Decisions (19-Nov)')],
    *table(['FB', 'Question', 'Decision', 'Status', ''], [
        ['FB-171', 'Column name of the crossdock flag', 'CROSS_DOCK_FLAG, as in the BCT logic flow', 'Done', ''],
        ['FB-185', 'Message when a crossdock Manifest / PO is typed', 'No message (no data)', 'Done', ''],
        ['FB-186', "Screen also excludes Palletize Code 'X'?", "Yes: CROSS_DOCK_FLAG 'X' and Palletize Code 'X' are excluded", 'Done', ''],
        ['FB-187', 'Draft ASN (TB_T_ASN) of crossdock orders before go-live', 'Existing behaviour, no rule', 'Done', ''],
        ['FB-190', "Is Palletize Code 'X' always crossdock?", "Yes, always crossdock with CROSS_DOCK_FLAG 'X'", 'Done', ''],
    ]),
]

ASN04 = header('ASN04_Sub Manifest(ASN) to Upload (Batch)', 'UISS-Batch', 'CR Crossdock: crossdock rows skipped in ASN Upload') + [
    [('title', 'CR Crossdock: ASN Upload uploads regular orders only (crossdock rows skipped)')], [],
    *revision([['0.1', '14-Nov-2026', 'First version from ASN_Existing.xlsx (crossdock rows rejected)', '[Author]', ''],
               ['0.2', '19-Nov-2026', 'Column CROSS_DOCK_FLAG (BCT logic flow); crossdock rows are skipped and the regular rows are uploaded '
                                      '(FB-188); messages 8 and 9 deleted (FB-189); decisions of the open points', '[Author]', '']]),
    [('sec', '1. Background')], *BACKGROUND,
    [('sec', '2. Change summary')],
    *table(['No', 'Item', 'Current', 'To Be', 'Impacted sheet'], [
        ['1', 'Business validation: crossdock row', "Palletize Code 'X' is uploaded (with the crossdock delivery qty check, message 8).",
         ('tdnew', 'Row with ' + X + ' is skipped: not taken from the pra manifest / pra part, not written to TB_T_ASN; warning log (message 12).'),
         'Func Flow, Logging Message'],
        ['2', 'Result of the upload', 'Existing: any error = finished with error (message 7b).',
         ('tdnew', 'The regular rows are uploaded to TB_T_ASN as today; the skipped crossdock rows do not make the upload fail. '
                   'The supplier creates the crossdock ASN in ASN Creation (Crossdock, XDOCK).'), 'Func Flow'],
        ['3', 'Messages 8 (delivery qty for crossdock order) and 9 (case no vs palletize code)', 'Existing crossdock checks',
         ('tdnew', 'Deleted: crossdock rows never reach these checks'), 'Func Flow, Logging Message'],
        ['4', 'Template Upload', 'Supplier Cd, Supplier Plant, Sub Supp Cd, Sub Supp Plant, Manifest No, Item No, Part No, Qty Delivery, Delivery Date, Palletize Code, Case No, Route, Rit, Supplier Ref No.1, No.2',
         'No change of columns; Palletize Code and Manifest No are used by the new check.', 'Template Upload'],
    ]),
    [('sec', '3. Process flow')],
    *table(['Step', 'Input', 'Process', 'Output', ''], [
        ['1', 'Upload file (template)', ('tdnew', 'Upload ASN, skip the rows with ' + X + ' (warning log)'), 'TB_T_ASN (regular rows only)', ''],
        ['2', 'TB_T_ASN', 'ASN Submit Creation (existing flow)', 'TB_R_PRA_DAILY_ORDER_MANIFEST, TB_R_PRA_DAILY_ORDER_PART', ''],
    ]),
    [('sec', '4. Logic (new business validation, after the duplication check (4b) and before insert into temporary (5a / 5b))')],
    *table(['No', 'Step', 'Logic', '', ''], [
        ['1', 'Insert info log', 'Insert info log into [Log Detail]: Executing {0} process, {0} = "Crossdock order checking"', '', ''],
        ['2', 'Crossdock row check', ('tdnew', "For each row: if UPPER(TRIM(PALLETIZE_CD)) = 'X', or CROSS_DOCK_FLAG of TB_R_PRA_DAILY_ORDER_MANIFEST "
                                               "(MANIFEST_NO = [row] Manifest No, supplier of the row) = 'X': insert warning log (message 12), "
                                               'mark the row as skipped and go to the next row.'), '', ''],
        ['3', 'Next process', 'The rows not skipped continue with the existing checks and the insert into temporary / TB_T_ASN. '
                              'Any error of the existing checks: existing rule (message 7b).', '', ''],
        ['4', 'All rows skipped', ('tdnew', 'Nothing is written to TB_T_ASN; finish with the existing "no data" result (message number of the BCT, TBC).'), '', ''],
    ]),
    [('sec', '5. Logging Message')],
    *table(['No', 'Event / Cause', 'Type', 'Log Message', 'System & User Action'], [
        ['8', 'Delivery qty for crossdock order', '-', ('tdnew', 'Deleted (FB-189)'), '-'],
        ['9', 'Case No vs Palletize Code', '-', ('tdnew', 'Deleted (FB-189)'), '-'],
        ['12', 'Event information / crossdock row', 'Warning',
         ('tdnew', 'Line {0} : Manifest No {1} is a crossdock order (Palletize Code X) and is not uploaded. Please create the ASN in ASN Creation (Crossdock).'
                   '\n{0} : Row num\n{1} : Manifest No'),
         'System: write into table log message, skip the row. User: create the ASN of this row in ASN Creation (Crossdock).'],
    ]),
    [('sec', '6. Test scenarios')],
    *table(['TC', 'Scenario', 'Data', 'Expected result', ''], [
        ['1', 'Regular rows only', "Palletize Code not X, CROSS_DOCK_FLAG blank", 'Uploaded as today (TB_T_ASN)', ''],
        ['2', 'Row with Palletize Code X', "PALLETIZE_CD = X (CROSS_DOCK_FLAG X)", 'Row skipped, warning 12; other rows uploaded', ''],
        ['3', 'Palletize Code in lower case', 'PALLETIZE_CD = x', 'Same as TC 2', ''],
        ['4', 'Regular and crossdock rows in one file', '2 regular + 1 crossdock', '2 regular rows uploaded; crossdock row skipped with warning 12', ''],
        ['5', 'Only crossdock rows', '2 crossdock rows', 'Nothing written to TB_T_ASN; 2 warnings 12 + "no data" result', ''],
        ['6', 'Regular row with an existing error', 'Regular row, wrong qty', 'Existing rule (message 7b)', ''],
    ]),
    [('sec', '7. Decisions (19-Nov) and open points')],
    *table(['FB', 'Question', 'Decision', 'Status', ''], [
        ['FB-171', 'Column name of the crossdock flag', 'CROSS_DOCK_FLAG, as in the BCT logic flow', 'Done', ''],
        ['FB-188', 'File with regular and crossdock rows', 'Upload the regular rows only; crossdock rows (Palletize X / CROSS_DOCK_FLAG X) skipped', 'Done', ''],
        ['FB-189', 'Existing crossdock messages 8 and 9', 'Deleted', 'Done', ''],
        ['FB-190', "Is Palletize Code 'X' always crossdock?", "Yes, always crossdock with CROSS_DOCK_FLAG 'X'", 'Done', ''],
        ['-', 'ASN_Existing.xlsx marks Supplier Cd, Supplier Plant, Sub Supp Cd, Sub Supp Plant in orange: any change for these columns?', '-', 'To confirm', ''],
        ['-', 'Result message when every row is skipped', 'Existing "no data" message of the BCT', 'To confirm', ''],
    ]),
]

if __name__ == '__main__':
    add_sheet(os.path.join(HERE, 'source', 'DR_UISS_ASN03_Delivery_Note_ASN_Creation_Screen.xlsx'),
              os.path.join(HERE, 'DR_UISS_ASN03_Delivery_Note_ASN_Creation_Screen.xlsx'), ASN03)
    add_sheet(os.path.join(HERE, 'source', 'DR_UISS_ASN04_Delivery_Note_ASN_Upload_Batch.xlsx'),
              os.path.join(HERE, 'DR_UISS_ASN04_Delivery_Note_ASN_Upload_Batch.xlsx'), ASN04)
    from cr_standalone import write
    img = lambda n: os.path.join(HERE, 'flow_img', n + '.png')
    write(os.path.join(HERE, 'CR_Crossdock_ASN03_ASN_Creation.xlsx'), ASN03, [
        ('AS-IS: ASN Creation lists regular and crossdock orders', img('asn03_as_is'), []),
        ('TO-BE: crossdock orders are not listed; their ASN is made in ASN Creation (Crossdock)', img('asn03_to_be'), [
            "Get Data Manifest excludes CROSS_DOCK_FLAG = 'X' (TB_R_PRA_DAILY_ORDER_MANIFEST) and Palletize Code = 'X' (TB_R_PRA_DAILY_ORDER_PART).",
            'A typed crossdock Manifest No / PO No gives no data (no message).',
            'The supplier creates the ASN of a crossdock order in ASN Creation (Crossdock, XD10). Save / Submit of regular orders: no change.'])])
    write(os.path.join(HERE, 'CR_Crossdock_ASN04_ASN_Upload.xlsx'), ASN04, [
        ('AS-IS: every row is uploaded, crossdock rows included (crossdock checks msg 8 / 9)', img('asn04_as_is'), []),
        ('TO-BE: crossdock rows are skipped, regular rows are uploaded', img('asn04_to_be'), [
            "New check after the duplication check: Palletize Code 'X' or CROSS_DOCK_FLAG 'X' -> row skipped, warning log 12.",
            'Regular rows continue with the existing checks and are written to TB_T_ASN; skipped rows do not make the upload fail.',
            'Crossdock checks msg 8 (delivery qty) and msg 9 (case no / palletize) are deleted.',
            'All rows skipped: nothing is saved, existing "no data" result (message number TBC).',
            'The supplier creates the ASN of the skipped rows in ASN Creation (Crossdock, XD10).'])])
