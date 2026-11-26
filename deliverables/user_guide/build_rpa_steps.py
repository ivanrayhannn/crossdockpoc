"""RPA step documents: one screenshot per step while the robot runs.
- XD07_RPA_Steps_AP_POLE.xlsx: get the data of the run from NSP, fill the files, upload them on AP POLE Common File Upload, check.
- XD06_RPA_Steps_GTOPAS.xlsx: get the data of the run from NSP, add / delete the rows on GTOPAS WVJA5204.
Pictures: AP POLE and GTOPAS screens given by the user (ap_pole_img, gtopas_img); NSP prototype (rpa_shots.mjs); query results and files
rendered from the full flow simulation (render_rpa.py). Run: python3 render_rpa.py && python3 build_rpa_steps.py
Also writes the Markdown copy for developers: prepare_code/rpa/XD06_RPA_Steps_GTOPAS.md, XD07_RPA_Steps_AP_POLE.md (screens in
prepare_code/rpa/img; query results and files as Markdown tables)."""
import json
import os
import shutil

from openpyxl import Workbook

from build_ap_pole_guide import build_sheet

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = '20261110110000'
CAP = ('AP POLE and GTOPAS pictures: screens given by the user (a red mark comes from the original picture). NSP picture: prototype. '
       f'Query results and files: example data of the full flow simulation (dummy parts DUMMY-00x, [Sync] of 2026-11-10 11:00:00); yellow header = helper '
       'column of NSP, not written to the file or the screen.')

XD07 = {
    'sheet': 'XD07 RPA steps',
    'title': 'XD07 RPA Cross Dock Master to AP POLE: steps of the robot',
    'caption': CAP,
    'meta': [('Function', 'XD07 RPA Cross Dock Master to AP POLE (desktop flow CDX_XD07_APPOLE, started by the parent flow CDX_SYNC_PARENT)'),
             ('Started by', 'D/S [Sync] or [Re-send last Sync] on NSP. Scenario 1: after XD06 GTOPAS succeeded. Scenario 2: at once.'),
             ('Input', 'SYNC_DT of the run (time of the [Sync] click, given by the parent flow); views V_APPOLE_UPLOAD_EXPORT / V_APPOLE_UPLOAD_KANBAN, rows with SYNC_STATUS 1 and that SYNC_DT (read-only DB user)'),
             ('Output', 'Files uploaded on AP POLE in the order 1 EXPORT_PRE, 2 KANBAN, 3 EXPORT_POST; e-mail SUCCESS / FAILED')],
    'blocks': [
        ('step', 'NSP: D/S clicks [Sync (n)]',
         'Export Crossdock Master, ongoing period. [Sync] sets the staging rows 0 -> 1 with SYNC_DT = time of the click and starts the parent flow with that SYNC_DT. '
         'This is the only manual step; everything below is the robot.', 'r01_nsp_sync.png'),
        ('step', 'Get data: file 1 EXPORT_PRE',
         'The robot reads the Export rows of the run for file 1: parts whose Max Case/Day goes down (OPERATION_TYPE 1). '
         'Per part, ROW_ORDER 1 (down or delete) comes before 2 (up or add).', 'r02_view_export_pre.png'),
        ('step', 'Get data: file 2 KANBAN',
         'The Kanban rows of the run with OPERATION_TYPE 1 to 4 (a header with 5 is not uploaded).', 'r03_view_kanban.png'),
        ('step', 'Get data: file 3 EXPORT_POST',
         'Every other Export row of the run (OPERATION_TYPE 2, 3, 4 or 5 on the Kanban row of the part).', 'r04_view_export_post.png'),
        ('step', 'Fill the template: file 1',
         'Copy of the stored template LLM9Q880, one row per Export row from row 4 (header on row 3), helper columns left out. Effective Month and '
         'Effective Year: the robot splits EFFECTIVE_MONTH_YEAR (MM/YYYY). Grey columns stay empty. A file without rows is not made.', 'r05_file1_export_pre.png'),
        ('step', 'Fill the template: file 2', 'Copy of the stored template LLM9Q910, one row per Kanban row from row 4. Max Allowance Qty and the columns after it stay empty '
         '(AP POLE calculates Max Allowance Qty).', 'r06_file2_kanban.png'),
        ('step', 'Fill the template: file 3', 'Copy of the stored template LLM9Q880, same columns as file 1.', 'r07_file3_export_post.png'),
        ('step', 'AP POLE: log in, menu Master',
         'The robot logs in to AP POLE (https://ap-pole.toyota-asia.com/lm9/) with the robot user and opens the menu Master.', 'a01_menu_master.png'),
        ('step', 'Upload file 1 EXPORT_PRE',
         'Common File Upload (WLM98010). Report Type = the Export Customer Cross Dock Master upload (LM9Q870), File Name = '
         f'LLM9Q880_{RUN}_1_EXPORT_PRE.xls, [Upload]. Wait for the result: an error stops the run (next files not uploaded).', 'b04_upload_lm9q870.png'),
        ('step', 'Upload file 2 KANBAN',
         f'Report Type = LM9Q900 - Upload Kanban Part Master, File Name = LLM9Q910_{RUN}_2_KANBAN.xls, [Upload]. Wait for the result.', 'a07_upload_lm9q900.png'),
        ('step', 'Upload file 3 EXPORT_POST',
         f'Report Type = LM9Q870 again, File Name = LLM9Q880_{RUN}_3_EXPORT_POST.xls, [Upload]. Wait for the result.', 'b04_upload_lm9q870.png'),
        ('step', 'Check: Cross Dock Kanban Part Master',
         'Master > Cross Dock Kanban Part Master (WLM9Q890), search the parts of the run: Shipping Box Qty and Max Shipping Box Qty '
         'of the effective month show the uploaded values.', 'a04_wlm9q890_result.jpg'),
        ('step', 'Check: Export Customer Cross Dock Master',
         'Tick the part, [Maintain Cross Dock] (WLM9Q860): the Buyer-PD rows show the uploaded Max Shipping Box (RCS); 0 = deleted.', 'b02_wlm9q860.jpg'),
        ('step', 'Result: e-mail',
         'The robot gives STATUS back to the parent flow; the parent flow sends one e-mail per run (SUCCESS / FAILED, file and row of an '
         'error). Nothing is written back to NSP. FAILED: D/S clicks [Re-send last Sync].', None),
    ],
    'notes': ['File names follow the templates decided for the staging (LLM9Q910 Kanban, LLM9Q880 Export). The Report Type names on the '
              'AP POLE screen are LM9Q900 / LM9Q870: which report type takes which template is TBC with the AP POLE team.',
              'The AP POLE screens are the screens given by the user (16-Nov), not taken during a robot run.',
              'Order of the files: EXPORT_PRE before KANBAN when Max goes down, so AP POLE never has destinations above the Max.',
              'Column mapping per template column: prepare_code/rpa/Column_Mapping_Staging_To_Upload.md (Column_Mapping_Staging_To_Upload.xlsx).',
              'One row per key: a part edited twice before [Sync] has one row with the last value (the unsent row is updated, not added). [Re-send last Sync] reads MAX(SYNC_DT).'],
}

XD06 = {
    'sheet': 'XD06 RPA steps',
    'title': 'XD06 RPA Cross Dock Master to GTOPAS: steps of the robot',
    'caption': CAP,
    'meta': [('Function', 'XD06 IF Cross Dock Master to GTOPAS (desktop flow CDX_XD06_GTOPAS, started by the parent flow CDX_SYNC_PARENT)'),
             ('Started by', 'Scenario 1 of [Sync] / [Re-send last Sync] (run with GTOPAS rows), or the Period Rollover on day 1 (00:10)'),
             ('Input', 'SYNC_DT of the run; table TB_H_STG_GTOPAS, rows with SYNC_STATUS 1 and that SYNC_DT (read-only DB user)'),
             ('Output', 'Rows added / deleted on GTOPAS WVJA5204 (Depot 01); STATUS to the parent flow; e-mail')],
    'blocks': [
        ('step', 'NSP: D/S clicks [Sync (n)] (or Period Rollover)',
         'The run has GTOPAS rows (a part became Active / Inactive, a destination was added / removed): the parent flow starts XD06 first. '
         'The Period Rollover starts XD06 by itself, no screen.', 'r01_nsp_sync.png'),
        ('step', 'Get data: rows of the run ([Sync])',
         'The robot reads TB_H_STG_GTOPAS with SYNC_STATUS 1 and the SYNC_DT of the run: one row per part + destination, ACTION ADD or DELETE. Example: run of 10-Nov, three ADD rows.',
         'r10_gtopas_rows_add.png'),
        ('step', 'Get data: rows of the run (Period Rollover)',
         'Example: rollover of 01-Jan, two DELETE rows (part became Inactive) and one ADD row (part became Active).', 'r11_gtopas_rows_rollover.png'),
        ('step', 'GTOPAS: open Crossdock Master and search the row',
         'Menu Supply > Master > Crossdock Master (WVJA5204). Depot Code = 01, P/No. and Destination Code of the row, [Search].', 'g01_wvja5204_delete.png'),
        ('step', 'DELETE row: MT = DEL',
         'On the row found, MT = DEL and confirm. GTOPAS shows "MZD34006FEI: Registration completed." = done. Row not found = already '
         'gone = OK. Any other message = the row failed: it is listed and the robot goes on with the next row.', 'g01_wvja5204_delete.png'),
        ('step', 'ADD row: register',
         'Register a new row: Depot Code 01, Maker Code A, P/No., Domestic/Overseas 2, Destination Code, TOPAS Order Type 3, Order '
         'Transportation Code 2. Message MZD34006FEI = done; row already there = OK. ILLUSTRATION below: no screenshot of the register screen yet.',
         'r12_gtopas_add_illustration.png'),
        ('step', 'Result: STATUS and e-mail',
         'SUCCESS when every row is OK, else FAILED with the failed rows. Scenario 1: the parent flow starts XD07 only on SUCCESS. One e-mail '
         'per run; nothing is written back to NSP. FAILED: D/S clicks [Re-send last Sync].', None),
    ],
    'notes': ['The GTOPAS screenshot is the screen given by the user (part 52119-BZV60, destination 9618274, a DEL row), not the dummy data of the '
              'example; it shows the search fields and the message of a delete.',
              'Screenshot of the register (ADD) screen of WVJA5204 to be added; TOPAS Order Type 3 or * is TBC (FB-203).',
              'GTOPAS has no period: the rows of the Next period go at the Period Rollover, not at [Sync].'],
}

MD_DIR = os.path.join(HERE, '..', '..', 'prepare_code', 'rpa')
TABLES = json.load(open(os.path.join(HERE, 'shots_rpa', 'tables.json')))
IMG_DIRS = ('ap_pole_img', 'shots_ap', 'shots_gt', 'gtopas_img', 'shots_rpa')
cell = lambda v: str(v).replace('|', '\\|').replace('*', '\\*')


def md_table(t):
    """Query (or file name) as code, then the rows; helper columns (NSP only, not in the file) marked with *."""
    out = []
    if t['note']:
        out.append(f"> {t['note']}\n")
    if t['sql']:
        out.append('```sql\n' + t['sql'] + '\n```\n' if t['sql'].upper().startswith('SELECT') else f"File: `{t['sql']}`\n")
    head = [h + ('*' if h in t['helper'] else '') for h in t['head']]
    out.append('| ' + ' | '.join(head) + ' |')
    out.append('|' + '---|' * len(head))
    out += ['| ' + ' | '.join(cell(v) for v in r) + ' |' for r in t['rows']]
    return '\n'.join(out) + '\n'


def write_md(fname, g):
    os.makedirs(os.path.join(MD_DIR, 'img'), exist_ok=True)
    L = [f"# {g['title']}", '', '_Generated by deliverables/user_guide/build_rpa_steps.py from the same content as the Excel file; do not edit by hand._', '']
    L += ['| Item | Value |', '|---|---|'] + [f'| {k} | {cell(v)} |' for k, v in g['meta']] + ['']
    L += [g['caption'].replace('yellow header', 'column name with *'), '', '## Steps', '']
    n = 0
    for kind, title, text, pic in g['blocks']:
        n += 1
        L += [f'### {n}. {title}', '', text, '']
        if not pic:
            continue
        key = os.path.splitext(pic)[0]
        if key in TABLES:
            L.append(md_table(TABLES[key]))
        else:
            src = next(os.path.join(HERE, d, pic) for d in IMG_DIRS if os.path.exists(os.path.join(HERE, d, pic)))
            shutil.copy(src, os.path.join(MD_DIR, 'img', pic))
            L += [f'![{title}](img/{pic})', '']
    L += ['## Notes', ''] + [f'- {x}' for x in g['notes']] + ['']
    open(os.path.join(MD_DIR, fname), 'w').write('\n'.join(L))
    print('saved prepare_code/rpa/' + fname)


for name, g in (('XD07_RPA_Steps_AP_POLE.xlsx', XD07), ('XD06_RPA_Steps_GTOPAS.xlsx', XD06)):
    wb = Workbook()
    wb.remove(wb.active)
    build_sheet(wb, g)
    wb.save(os.path.join(HERE, name))
    print('saved', name)
    write_md(name.replace('.xlsx', '.md'), g)
