"""Sample sheets of the XD01 UISS (Export / Upload Kanban Crossdock Master, Export / Upload Mapping) from the Export Excel
files of the prototype (deliverables/uiss_screens/export_samples, made by deliverables/uiss_screens/export_samples.mjs).
The four sheets of the hand-tidied workbook are replaced at XML level (add_sheets_xlsx.py), so images and shapes stay.
Run from the repository root: python3 deliverables/function_list_v2/specs/xd01_samples.py"""
import shutil
import subprocess
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

V = 'deliverables/function_list_v2'
HAND = f'{V}/uiss/XD01_UISS_Screen_CrossDockPartMaster.xlsx'
EXP = 'deliverables/uiss_screens/export_samples'
STG = 'TB_H_STG_APPOLE_KANBAN / TB_H_STG_APPOLE_EXPORT / TB_H_STG_GTOPAS'
SHEETS = [
    ('Export Kanban Crossdock Master', 'kanban', 'Kanban Crossdock Master',
     "Sample of [Export Excel] on Kanban Crossdock Master: file Crossdock_Kanban_Master_YYYYMMDD.xlsx, sheet 'Kanban Crossdock Master' (rows of the "
     f"active filter, information only). Period = calculation period of the row. Sync Status AP POLE / GTOPAS and Last Sent come from {STG}. "
     'CREATED_DT / CREATED_BY / UPDATED_DT / UPDATED_BY = audit of the row.'),
    ('Upload Kanban Crossdock Master', 'kanban', 'Upload',
     "Upload template of Kanban Crossdock Master = sheet 'Upload' of the export: every part of the period with Upload (A/E) = E; add a row with A for a "
     'new part. Period YYYYMM: flag A = the ongoing or the next period, flag E = the ongoing period. Read by XD02 by column name.'),
    ('Export Mapping', 'mapping', 'Export Crossdock Master',
     "Sample of [Export Excel] on Export Crossdock Master (Sync Status = All): sheet 'Export Crossdock Master' (information only), one row per "
     'destination + order type. Dest Case/Day next to Total Case/Day (used) and Max Case/Day (quota) = used / quota of the screen. '
     f'Sync Status AP POLE / GTOPAS and Last Sent come from {STG}. CREATED_DT / CREATED_BY / UPDATED_DT / UPDATED_BY = audit of the mapping row.'),
    ('Upload Mapping', 'mapping', 'Upload',
     "Upload template of Export Crossdock Master = sheet 'Upload' of the export with the ongoing period: same column names as the export. XD03 reads "
     'Part Number, Destination Code, Order Type, Dest Case/Day and Upload (A/E); Total Case/Day (used, value at export time) and Max Case/Day '
     '(quota) are reference only.'),
]
thin = Side(style='thin', color='000000')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR = PatternFill('solid', fgColor='DDEBF7')

out = openpyxl.Workbook()
out.remove(out.active)
for name, f, src_sheet, note in SHEETS:
    src = openpyxl.load_workbook(f'{EXP}/{f}.xlsx')[src_sheet]
    ws = out.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws['A1'] = name
    ws['A1'].font = Font(name='Arial', size=10, bold=True)
    ws['A2'] = note
    ws['A2'].font = Font(name='Arial', size=9)
    rows = list(src.iter_rows(values_only=True))
    widths = {}
    for i, row in enumerate(rows):
        for j, v in enumerate(row, 1):
            c = ws.cell(4 + i, j, v)
            c.border = BOX
            if i == 0:
                c.font, c.fill = Font(name='Arial', size=9, bold=True), HDR
                c.alignment = Alignment(wrap_text=True, vertical='center')
            else:
                c.font = Font(name='Arial', size=9)
                if isinstance(v, (int, float)):
                    c.number_format = '#,##0'
            widths[j] = max(widths.get(j, 8), min(30, len(str(v or '')) + 2))
    for j, w in widths.items():
        ws.column_dimensions[ws.cell(4, j).column_letter].width = w
    ws.freeze_panes = 'A5'
tmp = tempfile.mkdtemp()
out.save(f'{tmp}/samples.xlsx')
subprocess.run([sys.executable, 'deliverables/uiss_specs/add_sheets_xlsx.py', HAND, f'{tmp}/samples.xlsx', f'{tmp}/merged.xlsx'], check=True, stdout=subprocess.DEVNULL)
shutil.copy(f'{tmp}/merged.xlsx', HAND)
print('updated', HAND)
