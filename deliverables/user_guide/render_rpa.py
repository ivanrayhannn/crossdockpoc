"""Images for the RPA step documents XD06 (GTOPAS) and XD07 (AP POLE), Excel-like:
- query results of the bot (the staging tables / views of NSP, read-only DB user),
- the upload files the bot fills from the stored templates,
- an illustration of the GTOPAS register row (no screenshot of the register screen yet).
Data: the full flow simulation (erd/proposal_staging_sync/simulation/stg_flow_steps.json): [Sync] of 2026-11-10 11:00:00 (scenario 1) and
the Period Rollover of 2027-01-01 00:10:00. Dummy parts and destinations. Run: python3 render_rpa.py"""
import json
import os
import subprocess
import tempfile

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'shots_rpa')
SIM = os.path.join(HERE, '..', 'function_list_v2', 'erd', 'proposal_staging_sync', 'simulation', 'stg_flow_steps.json')
data = json.load(open(SIM))
STEPS, DEST = data['steps'], data['dest']
fill = lambda c: PatternFill('solid', fgColor=c)
HDR, HELP, SQLF, ILL = fill('D9E1F2'), fill('FFF2CC'), fill('F2F2F2'), fill('FCE4D6')
tmp = tempfile.mkdtemp()
TABLES = {}  # name -> query / file name, header, rows: written to shots_rpa/tables.json for the Markdown copy
my = lambda per: per[4:] + '/' + per[:4]
bpd = lambda d: DEST[d][:5] + '-' + DEST[d][5:]


def render(name, head, rows, sql=None, helper=(), note=None):
    """Excel-like picture: optional SQL line, header (yellow = helper column, not in the file), rows."""
    TABLES[name] = {'sql': sql, 'note': note, 'head': head, 'helper': list(helper), 'rows': rows}
    wb = openpyxl.Workbook()
    ws = wb.active
    r0 = 1
    for text, f in ((sql, SQLF), (note, ILL)):
        if text:
            x = ws.cell(r0, 1, text)
            x.font = Font(name='Consolas', size=10) if f is SQLF else Font(name='Calibri', size=11, bold=True, color='C00000')
            x.fill = f
            ws.merge_cells(start_row=r0, start_column=1, end_row=r0, end_column=len(head))
            r0 += 1
    for c, h in enumerate(head, 1):
        x = ws.cell(r0, c, h)
        x.font = Font(name='Calibri', size=11, bold=True)
        x.fill = HELP if h in helper else HDR
        ws.column_dimensions[get_column_letter(c)].width = max(9, len(h) + 3)
    for r, row in enumerate(rows, r0 + 1):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v).font = Font(name='Calibri', size=11)
            ws.column_dimensions[get_column_letter(c)].width = max(ws.column_dimensions[get_column_letter(c)].width, len(str(v)) + 3)
    ws.print_options.gridLines = True
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 8
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = ws.page_setup.fitToHeight = 1
    for side in ('left', 'right', 'top', 'bottom'):
        setattr(ws.page_margins, side, 0.2)
    p = os.path.join(tmp, name + '.xlsx')
    wb.save(p)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmp, p], capture_output=True)
    subprocess.run(['pdftoppm', '-r', '110', '-png', '-singlefile', os.path.join(tmp, name + '.pdf'), os.path.join(tmp, name)])
    im = Image.open(os.path.join(tmp, name + '.png')).convert('RGB')
    bbox = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()
    im = im.crop((max(0, bbox[0] - 8), max(0, bbox[1] - 8), min(im.width, bbox[2] + 8), min(im.height, bbox[3] + 8)))
    im.save(os.path.join(OUT, name + '.png'))
    print(name, im.size)


def step(run, label=None):
    return next(s for s in STEPS if s.get('rpa') and s['rpa']['run'] == run and (label is None or s['label'] == label))


# ---------- XD07: run 20261110110000 ----------
RUN = '20261110110000'
SDT = '2026-11-10 11:00:00'  # SYNC_DT of the run = time of the [Sync] click
s = step(RUN, '[Sync] · scenario 1')
f = s['files']
EXP_COLS = ['STG_ID', 'PERIOD', 'NSP_PART_NO', 'FILE_NO', 'ROW_ORDER', 'EFFECTIVE_MONTH_YEAR', 'PART_NO', 'BUYER_PD', 'ORDER_TYPE', 'TRANSPORT_CODE', 'MAX_SHIPPING_BOX_RCS']
EXP_HELP = ('STG_ID', 'PERIOD', 'NSP_PART_NO', 'FILE_NO', 'ROW_ORDER')
exp_row = lambda x, n: [x['r']['id'], x['r']['per'], x['r']['p'], n, x['ro'], my(x['r']['per']), x['r']['p'].replace('-', ''), bpd(x['r']['d']), x['r']['ot'], 2, x['r']['cd']]
render('r02_view_export_pre', EXP_COLS, [exp_row(x, 1) for x in f['pre']], helper=EXP_HELP,
       sql=f"SELECT * FROM V_APPOLE_UPLOAD_EXPORT WHERE SYNC_STATUS = '1' AND SYNC_DT = '{SDT}' AND FILE_NO = 1 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID")
KAN_COLS = ['STG_ID', 'PERIOD', 'OPERATION_TYPE', 'EFFECTIVE_MONTH_YEAR', 'OPERATOR_ID', 'PART_NO', 'PART_NAME', 'SHIPPING_BOX_QTY', 'MAX_SHIPPING_BOX_QTY', 'MAX_ALLOWANCE_QTY']
render('r03_view_kanban', KAN_COLS,
       [[x['r']['id'], x['r']['per'], x['r']['op'], my(x['r']['per']), 'P6', x['r']['p'], 'DUMMY PART ' + x['r']['p'][-3:], x['r']['pcs'], x['r']['max'], x['r']['pcs'] * x['r']['max']] for x in f['kan']],
       helper=('STG_ID', 'PERIOD', 'OPERATION_TYPE'),
       sql=f"SELECT * FROM V_APPOLE_UPLOAD_KANBAN WHERE SYNC_STATUS = '1' AND SYNC_DT = '{SDT}' ORDER BY PERIOD, PART_NO")
render('r04_view_export_post', EXP_COLS, [exp_row(x, 3) for x in f['post']], helper=EXP_HELP,
       sql=f"SELECT * FROM V_APPOLE_UPLOAD_EXPORT WHERE SYNC_STATUS = '1' AND SYNC_DT = '{SDT}' AND FILE_NO = 3 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID")
# template columns (LLM9Q880: row 3 header, data from row 4); grey columns stay empty
FILE_EXP = ['Effective Month', 'Effective Year', 'Part No.', 'Shipping Box Qty', 'Max Shipping Box by Part No.', 'Buyer-PD', 'Order Type', 'Transport Code',
            'Max Shipping Box (RCS)', 'Max Allowance Qty', 'Packing/Pallet Type']
file_exp = lambda x: [x['r']['per'][4:], x['r']['per'][:4], x['r']['p'].replace('-', ''), '', '', bpd(x['r']['d']), x['r']['ot'], 2, x['r']['cd'], '', '']
render('r05_file1_export_pre', FILE_EXP, [file_exp(x) for x in f['pre']], sql=f'LLM9Q880_{RUN}_1_EXPORT_PRE.xls (template LLM9Q880)')
render('r06_file2_kanban', ['Effective Month', 'Effective Year', 'Operator ID', 'Part No.', 'Part Name', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Max Allowance Qty', 'Packing/Pallet Type ... Outer-Qty'],
       [[x['r']['per'][4:], x['r']['per'][:4], 'P6', x['r']['p'], 'DUMMY PART ' + x['r']['p'][-3:], x['r']['pcs'], x['r']['max'], '', ''] for x in f['kan']],
       sql=f'LLM9Q910_{RUN}_2_KANBAN.xls (template LLM9Q910)')
render('r07_file3_export_post', FILE_EXP, [file_exp(x) for x in f['post']], sql=f'LLM9Q880_{RUN}_3_EXPORT_POST.xls (template LLM9Q880)')

# ---------- XD06 ----------
GT_COLS = ['STG_ID', 'PERIOD', 'ACTION', 'DEPOT_CODE', 'P_NO', 'DESTINATION_CODE', 'MAKER_CODE', 'DOMESTIC_OVERSEAS', 'TOPAS_ORDER_TYPE', 'ORDER_TRANSPORTATION_CODE']
gt_row = lambda g: [g['id'], g['per'], g['act'], '01', g['p'], DEST[g['d']], 'A', 2, 3, 2]
render('r10_gtopas_rows_add', GT_COLS, [gt_row(g) for g in s['gsent']], helper=('STG_ID', 'PERIOD', 'ACTION'),
       sql=f"SELECT * FROM TB_H_STG_GTOPAS WHERE SYNC_STATUS = '1' AND SYNC_DT = '{SDT}' ORDER BY P_NO, DESTINATION_CODE")
ro = step('20270101001000')
render('r11_gtopas_rows_rollover', GT_COLS, [gt_row(g) for g in ro['gsent']], helper=('STG_ID', 'PERIOD', 'ACTION'),
       sql="SELECT * FROM TB_H_STG_GTOPAS WHERE SYNC_STATUS = '1' AND SYNC_DT = '2027-01-01 00:10:00' ORDER BY P_NO, DESTINATION_CODE")
add = s['gsent'][0]
render('r12_gtopas_add_illustration',
       ['No', 'MT', 'R', 'Depot Code', 'Maker Code', 'P/No.', 'Domestic/Overseas', 'Destination Code', 'TOPAS Order Type', 'Order Transportation Code'],
       [['', '', '', '01', 'A', add['p'], 2, DEST[add['d']], 3, 2]],
       note='ILLUSTRATION, not a screenshot: register row on GTOPAS WVJA5204 (screenshot of the register screen to be added)')
json.dump(TABLES, open(os.path.join(OUT, 'tables.json'), 'w'), indent=1)
