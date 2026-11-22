"""22-Nov: Sync with the staging table TB_H_PART_CANDIDATE_STG_SYNC (decisions 21-Nov, deliverables/function_list_v2/erd/proposal_staging_sync).
- TB_M_PART_CANDIDATE keeps no sync column (SYNC_STATUS, GTOPAS_SYNC_DT, APPOLE_SYNC_DT, SYNC_RUN_ID removed).
- Every value change (XD01 screen, XD02 / XD03 upload, XD05) inserts a row in TB_H_PART_CANDIDATE_STG_SYNC with the Sync Status of AP POLE and GTOPAS.
- [Sync]: NSP reduces the staging (first OLD / last NEW per key), sets SEND_SEQ (1 Export before Kanban, 2 Kanban, 3 Export after Kanban), run ID,
  dates and LAST_SYNC_DATE_APPOLE; the RPA reads only the staging. XD07 uploads the files LLM9Q880 / LLM9Q910; XD06 compares part + destinations.
- GTOPAS: rows with GTOPAS_SYNC_STATUS 0 + PERIOD (Current at [Sync], the new period at the Period Rollover), no date.
Runs after apply_2011b."""
import glob
import json

D = '22-Nov-26'
STG = 'TB_H_PART_CANDIDATE_STG_SYNC'
DROP = {'SYNC_STATUS', 'GTOPAS_SYNC_DT', 'APPOLE_SYNC_DT', 'SYNC_RUN_ID', 'SYNC_DT', 'SYNC_MESSAGE'}
REF = 'Decisions and simulation: deliverables/function_list_v2/erd/proposal_staging_sync (Summary_Staging_Sync_Decisions.md, simulation/Full_Sync_Flow_Simulation.xlsx).'

STG_TABLE = {
    'name': STG, 'kind': 'history', 'proposed': True,
    'description': 'Staging of every value change of the Kanban / Export Crossdock Master for the sync to AP POLE (XD07) and GTOPAS (XD06) (22-Nov). '
                   'Inserted by XD01 (screen), XD02 / XD03 (upload) and XD05 in the same transaction as the master update; updated only by [Sync], '
                   '[Re-send last Sync] and the Period Rollover. The RPA reads only this table. TB_H_PART_CANDIDATE (screen history) is kept as it is.',
    'columns': [
        ['HIST_ID', 'BIGINT', 'Y', 'N', 'Running number (identity): order of the changes'],
        ['PART_NO', 'VARCHAR(TBD)', '', 'N', 'Part number (NSP format, with "-"); FK1 (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE'],
        ['PART_NAME', 'VARCHAR(TBD)', '', 'N', 'Part Name copied from TB_M_PART_CANDIDATE at the insert (Part Name of the Kanban upload file)'],
        ['PERIOD', 'CHAR(6)', '', 'N', 'Calculation period YYYYMM; Effective Month / Year of the AP POLE upload'],
        ['PART_STATUS', 'VARCHAR(10)', '', 'N', 'Status of the part in this period when the row is written (Active / Inactive). Inactive: the part stays in the '
                                              'AP POLE Kanban, its Export rows are DELETE with NEW_VALUE 0'],
        ['LEVEL_TYPE', 'VARCHAR(6)', '', 'N', 'KANBAN = parent (Kanban Crossdock Master), EXPORT = destination (Export Crossdock Master)'],
        ['DEST_CODE', 'CHAR(7)', '', 'Y', 'EXPORT only: destination code. No FK (a DELETE row points to a removed destination)'],
        ['ORDER_TYPE', 'VARCHAR(2)', '', 'Y', "EXPORT only: '**', 'C', '9', 'V'"],
        ['FIELD_NAME', 'VARCHAR(30)', '', 'N', 'KANBAN: PCS_CASE, MAX_CASE_DAY. EXPORT: CASE_DAY'],
        ['ACTION', 'VARCHAR(6)', '', 'N', 'ADD / EDIT / DELETE'],
        ['OLD_VALUE', 'VARCHAR(10)', '', 'Y', 'Value before the change; NULL on ADD'],
        ['NEW_VALUE', 'VARCHAR(10)', '', 'Y', 'Value after the change; 0 on DELETE'],
        ['SOURCE', 'VARCHAR(6)', '', 'N', 'BATCH (XD05) / SCREEN / UPLOAD'],
        ['UPLOAD_ID', 'VARCHAR(TBD)', '', 'Y', 'Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD'],
        ['APPOLE_SYNC_STATUS', 'CHAR(1)', '', 'N', "0 = Non Sync (default), 1 = Sync, 2 = Superseded (an earlier row of the same key, not sent). The part + period "
                                                   "is AP POLE Non Sync while it has a row with 0"],
        ['APPOLE_SYNC_DT', 'DATETIME', '', 'Y', 'Time of the [Sync] that sent the row to AP POLE (status 1 and 2); Last Sent AP POLE = latest value'],
        ['SEND_SEQ', 'NUMBER(1)', '', 'Y', 'Upload file: 1 = Export (LLM9Q880) before the Kanban file, only for a part whose Max goes down; 2 = Kanban (LLM9Q910); '
                                          '3 = Export after the Kanban file (every other part). Set at [Sync] on the last row of each key; NULL for 2 and for a key '
                                          'that ends on its first value'],
        ['APPOLE_SYNC_RUN_ID', 'VARCHAR(14)', '', 'Y', 'AP POLE run ID YYYYMMDDHHMMSS; [Re-send last Sync] takes the rows of the last run'],
        ['GTOPAS_SYNC_STATUS', 'CHAR(1)', '', 'Y', 'NULL = not for GTOPAS (KANBAN rows, EXPORT EDIT). 0 = Non Sync: EXPORT ADD / DELETE (destination appears / '
                                                   'disappears). 1 = Sync: [Sync] for the Current period, the Period Rollover for the new period'],
        ['GTOPAS_SYNC_DT', 'DATETIME', '', 'Y', 'Time of the [Sync] / Period Rollover that sent the row to GTOPAS; Last Sent GTOPAS = latest value'],
        ['GTOPAS_SYNC_RUN_ID', 'VARCHAR(14)', '', 'Y', 'GTOPAS run ID ([Sync], [Re-send last Sync] or the Period Rollover)'],
        ['CREATED_BY', 'VARCHAR(20)', '', 'N', 'User of the save / upload, or XD05BATCH'],
        ['CREATED_DT', 'DATETIME', '', 'N', 'Time of the insert (same transaction as the master update)'],
        ['CHANGED_BY', 'VARCHAR(20)', '', 'Y', 'User of [Sync] / [Re-send last Sync], XD05BATCH for the Period Rollover'],
        ['CHANGED_DT', 'DATETIME', '', 'Y', 'Time of that update'],
    ]}

KEY = 'Key of a change = PART_NO + PERIOD + LEVEL_TYPE + DEST_CODE + ORDER_TYPE + FIELD_NAME.'
INSERT_RULES = [
    'Every value change inserts a row in TB_H_PART_CANDIDATE_STG_SYNC in the same transaction as the master update (a save without a value change '
    'writes no row): PART_NO, PART_NAME, PERIOD, PART_STATUS, LEVEL_TYPE, DEST_CODE / ORDER_TYPE (EXPORT), FIELD_NAME, ACTION, OLD_VALUE, NEW_VALUE, '
    'SOURCE, UPLOAD_ID, APPOLE_SYNC_STATUS 0, CREATED_BY / CREATED_DT.',
    'KANBAN rows (Kanban Crossdock Master): EDIT of PCS_CASE / MAX_CASE_DAY per changed field; GTOPAS_SYNC_STATUS NULL.',
    'EXPORT rows (Export Crossdock Master): ADD / EDIT / DELETE of CASE_DAY per destination + order type. ADD and DELETE (destination appears / '
    'disappears) get GTOPAS_SYNC_STATUS 0; EDIT gets NULL. DELETE: NEW_VALUE 0.',
    'Status change by Procurement (Kanban Crossdock Master): Active -> Inactive writes a DELETE (NEW 0) for every destination of the part, '
    'PART_STATUS column Inactive (no row for the status itself; the part stays in the AP POLE Kanban). Inactive -> Active: Procurement maps the '
    'destinations again on the screen (EXPORT ADD rows, PART_STATUS Active).',
    'Total Case/Day of the destinations > Max Case/Day of the part (same period): error on save, nothing is saved (message no. 14 / 20). To lower Max, '
    'the user lowers the destinations first (Export), then Max (Kanban).',
    KEY,
]
SYNC_RULES = [
    '[Sync] (Export Crossdock Master) runs in one transaction before the bots start:',
    'AP POLE: take the staging rows with APPOLE_SYNC_STATUS 0, PERIOD = Current or Next, CREATED_DT > System Master parameter LAST_SYNC_DATE_APPOLE '
    'and <= the time of the click. Per key: AP POLE value = OLD_VALUE of the first row, NSP value = NEW_VALUE of the last row. Last row of the key -> '
    'APPOLE_SYNC_STATUS 1 with SEND_SEQ; earlier rows -> 2 Superseded; a key that ends on its first value -> 1 without SEND_SEQ. All rows taken: '
    'APPOLE_SYNC_DT, APPOLE_SYNC_RUN_ID, CHANGED_BY / CHANGED_DT. Then LAST_SYNC_DATE_APPOLE = time of the click.',
    'SEND_SEQ (position against the Kanban file): 1 = EXPORT rows of a part whose Max goes down (Export before Kanban), 2 = every KANBAN change and '
    'new part, 3 = EXPORT rows of every other part (Max up, new part, or no KANBAN row). AP POLE checks every uploaded row (total Max Shipping Box '
    '(RCS) of the part <= Max Shipping Box Qty), so inside a file the rows of a part going down / deleted come first, then up / added.',
    'GTOPAS: take the staging rows with GTOPAS_SYNC_STATUS 0 and PERIOD = Current (no date condition) -> GTOPAS_SYNC_STATUS 1, GTOPAS_SYNC_DT, '
    'GTOPAS_SYNC_RUN_ID. The Next period waits for the Period Rollover (GTOPAS has no period).',
    'Then NSP starts XD07 (AP POLE) and XD06 (GTOPAS) with the run ID. The bots read only TB_H_PART_CANDIDATE_STG_SYNC and write nothing back; the '
    'result comes by the notification e-mail. [Re-send last Sync] starts them again with the run ID of the last run.',
    'Rows of a past period still Non Sync (changed but not sent before the rollover) are never taken again: every selection has a PERIOD condition.',
]
SCREEN_RULES = [
    'Sync Status on the screen is worked out from the staging per part + period: AP POLE Non Sync while the part + period has a row with '
    'APPOLE_SYNC_STATUS 0, else Sync (Last Sent AP POLE = latest APPOLE_SYNC_DT); GTOPAS Non Sync while it has a row with GTOPAS_SYNC_STATUS 0, else '
    'Sync (Last Sent GTOPAS = latest GTOPAS_SYNC_DT). A past period can show Non Sync for rows not sent before the rollover (view only).',
]


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return False
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'
    return True


def tables(s):
    names = [t['name'] for t in s['tables']]
    for t in s['tables']:
        if t['name'] == 'TB_M_PART_CANDIDATE':
            t['columns'] = [c for c in t['columns'] if c[0] not in DROP]
            for c in t['columns']:
                if c[0] == 'PART_STATUS':
                    c[4] = ('Candidate / Active / Inactive. Candidate -> Active: XD05 (Next period). Active -> Inactive and Inactive -> Active: Procurement on '
                            'the Kanban Crossdock Master. The sync status of the part is in TB_H_PART_CANDIDATE_STG_SYNC (22-Nov)')
        if t['name'] == 'TB_M_PART_CANDIDATE_DEST':
            for c in t['columns']:
                if c[0] == 'CASE_DAY' and 'STG_SYNC' not in c[4]:
                    c[4] += '. Every add / change / removal writes a row to TB_H_PART_CANDIDATE_STG_SYNC (LEVEL_TYPE EXPORT) in the same transaction (22-Nov)'
        if t['name'] == 'TB_H_PART_CANDIDATE':
            t['description'] = ('History of every change of a crossdock part for the History setting of XD01 (Add / Edit by screen or upload, mapping changes, '
                                'status changes and mappings made by the calculation batches). The sync to GTOPAS / AP POLE is not recorded here: it is in '
                                'TB_H_PART_CANDIDATE_STG_SYNC (22-Nov). No retention limit.')
            for c in t['columns']:
                if c[0] == 'EVENT_TYPE':
                    c[4] = 'ADD / EDIT / MAPPING / CALC'
                if c[0] == 'SOURCE':
                    c[4] = 'SCREEN / UPLOAD / BATCH'
                if c[0] == 'FIELD_NAME':
                    c[4] = 'Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY'
                if c[0] == 'REMARK':
                    c[4] = 'Free text'
                if c[0] == 'CREATED_BY':
                    c[4] = 'User who made the change (batch user ID for BATCH)'
    if STG not in names:
        k = names.index('TB_H_PART_CANDIDATE') + 1 if 'TB_H_PART_CANDIDATE' in names else len(names)
        s['tables'].insert(k, json.loads(json.dumps(STG_TABLE)))


def clean_maps(s):
    """Remove the sync columns of TB_M_PART_CANDIDATE from every data map block; drop blocks left without mapping."""
    blocks = []
    for b in s['data_map']['blocks']:
        dest = b.get('destination')
        if isinstance(dest, dict) and dest.get('table') == 'TB_M_PART_CANDIDATE':
            b['mappings'] = [m for m in b['mappings'] if m.get('dest_field') not in DROP and m.get('dest_field') != 'e-mail message']
            src = b.get('source')
            if isinstance(src, dict):
                src['keys'] = [k for k in src.get('keys', []) if k.get('field') not in DROP]
            if not [m for m in b['mappings'] if m.get('dest_field') not in ('LAST_SOURCE', 'CHANGED_BY', 'CHANGED_DT')]:
                continue
        blocks.append(b)
    s['data_map']['blocks'] = blocks


def split(maps):
    """'A / B' destination fields -> one mapping per column (the UISS checks every column of the table)."""
    out = []
    for m in maps:
        parts = m['dest_field'].split(' / ')
        if len(parts) > 1 and all(x.replace('_', '').isalnum() and x.isupper() for x in parts):
            out += [dict(m, dest_field=x) for x in parts]
        else:
            out.append(m)
    return out


def stg_block(source, desc, rows):
    return {'source': source, 'destination': {'table': STG, 'operation': 'Insert', 'description': desc},
            'mappings': split([{'source_field': a, 'dest_field': b, 'description': c} for a, b, c in rows])}


COMMON_INS = [('-', 'HIST_ID', 'Identity'), ('PART_NO', 'PART_NO', 'Part of the change'), ('PART_NAME', 'PART_NAME', 'From TB_M_PART_CANDIDATE'),
              ('PERIOD', 'PERIOD', 'Period of the changed row'), ('PART_STATUS', 'PART_STATUS', 'Status of the part in the period')]
TAIL_INS = [('-', 'APPOLE_SYNC_STATUS', "'0' (Non Sync)"), ('-', 'APPOLE_SYNC_DT / SEND_SEQ / APPOLE_SYNC_RUN_ID', 'NULL'),
            ('-', 'GTOPAS_SYNC_DT / GTOPAS_SYNC_RUN_ID', 'NULL'), ('-', 'CREATED_BY', 'Login user (XD05: batch user ID)'), ('-', 'CREATED_DT', 'System date-time'),
            ('-', 'CHANGED_BY / CHANGED_DT', 'NULL')]


def kanban_block(source, src_name, desc):
    return stg_block(source, desc, COMMON_INS + [
        ('-', 'LEVEL_TYPE', "'KANBAN'"), ('-', 'DEST_CODE / ORDER_TYPE', 'NULL'), ('-', 'FIELD_NAME', "'PCS_CASE' / 'MAX_CASE_DAY' (one row per changed field)"),
        ('-', 'ACTION', "'ADD' (new part / new period) / 'EDIT'"), ('Value before', 'OLD_VALUE', 'NULL on ADD'), ('Value after', 'NEW_VALUE', 'New value'),
        ('-', 'SOURCE', src_name), ('-', 'UPLOAD_ID', 'Upload ID when SOURCE = UPLOAD, else NULL'), ('-', 'GTOPAS_SYNC_STATUS', 'NULL (not for GTOPAS)')] + TAIL_INS)


def export_block(source, src_name, desc):
    return stg_block(source, desc, COMMON_INS + [
        ('-', 'LEVEL_TYPE', "'EXPORT'"), ('DEST_CODE', 'DEST_CODE', 'Destination of the changed row'), ('ORDER_TYPE', 'ORDER_TYPE', 'Order Type of the row'),
        ('-', 'FIELD_NAME', "'CASE_DAY'"), ('-', 'ACTION', "'ADD' (new destination) / 'EDIT' (Case/Day) / 'DELETE' (removed, Inactive)"),
        ('Case/Day before', 'OLD_VALUE', 'NULL on ADD'), ('Case/Day after', 'NEW_VALUE', '0 on DELETE'), ('-', 'SOURCE', src_name),
        ('-', 'UPLOAD_ID', 'Upload ID when SOURCE = UPLOAD, else NULL'), ('-', 'GTOPAS_SYNC_STATUS', "'0' for ADD / DELETE, NULL for EDIT")] + TAIL_INS)


def sync_block():
    return {'source': {'table': STG, 'keys': [{'field': 'APPOLE_SYNC_STATUS', 'value': "'0', PERIOD Current / Next, CREATED_DT > LAST_SYNC_DATE_APPOLE and <= click"},
                                              {'field': 'GTOPAS_SYNC_STATUS', 'value': "'0', PERIOD = Current"}]},
            'destination': {'table': STG, 'operation': 'Update', 'description': '[Sync] / [Re-send last Sync] (before XD06 / XD07 start)'},
            'mappings': [{'source_field': '-', 'dest_field': 'APPOLE_SYNC_STATUS', 'description': "'1' last row of each key, '2' earlier rows (Superseded)"},
                         {'source_field': '-', 'dest_field': 'SEND_SEQ', 'description': '1 / 2 / 3 on the last row of each key (refer 5.24); NULL when the key ends on its first value'},
                         {'source_field': '-', 'dest_field': 'APPOLE_SYNC_DT / APPOLE_SYNC_RUN_ID', 'description': 'Time of the click / run ID YYYYMMDDHHMMSS'},
                         {'source_field': '-', 'dest_field': 'GTOPAS_SYNC_STATUS', 'description': "'1' for the GTOPAS rows of the Current period"},
                         {'source_field': '-', 'dest_field': 'GTOPAS_SYNC_DT / GTOPAS_SYNC_RUN_ID', 'description': 'Time of the click / run ID'},
                         {'source_field': '-', 'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Login user / system date-time'},
                         {'source_field': '-', 'dest_field': 'System Master LAST_SYNC_DATE_APPOLE', 'description': 'Time of the click'}]}


def _fix_sync(b):
    b['mappings'] = split(b['mappings'])
    return b


def section(fd, title, items, before=None):
    heads = [i for i, x in enumerate(fd) if x.get('type') == 'heading' and title.split(' ', 1)[1] in x.get('text', '')]
    if heads:
        return
    blk = [{'type': 'heading', 'text': title}, {'type': 'bullets', 'marker': '-', 'level': 0, 'items': items}]
    if before is not None:
        fd[before:before] = blk
    else:
        fd += blk


def sub(o, pairs):
    t = json.dumps(o, ensure_ascii=False)
    for a, b in pairs:
        t = t.replace(a, b)
    return json.loads(t)


# ------------------------------------------------------------------ XD01
def xd01(s):
    g = s['general']
    g['objective'][9] = ('Export Crossdock Master tab: to send the changes of the Current and Next period to AP POLE (XD07) and GTOPAS (XD06) with [Sync], '
                         'and show the Sync Status of each part (worked out from TB_H_PART_CANDIDATE_STG_SYNC).')
    g['buttons'][16]['function'] = ('Prepare the run in TB_H_PART_CANDIDATE_STG_SYNC (refer 5.24) and start XD07 (AP POLE) and XD06 (GTOPAS) for every part + period '
                                    'with a Non Sync staging row (AP POLE: Current and Next; GTOPAS: Current), whatever the filter shows. The label shows the '
                                    'number of parts, e.g. Sync (21).')
    for sec in g['screen_modes'][6]['sections']:
        sec['description'] = sec['description'].replace('Sync Status = No Sync', 'Sync Status = Non Sync').replace('Sync Status No Sync', 'Non Sync staging rows')
    g['screen_mode_remarks'] = [r.replace('4) Sync is enabled only when at least one part with status Active (ongoing period) or Inactive is No Sync or Failed (not limited to the listed rows).',
                                          '4) Sync is enabled only when TB_H_PART_CANDIDATE_STG_SYNC has a Non Sync row (AP POLE: Current / Next, GTOPAS: Current), not limited to the listed rows.')
                                for r in g['screen_mode_remarks']]
    s['screen_flow'][2]['flow']['nodes'][8]['label'] = 'Insert (Add) / update (Edit) part, insert staging rows (Non Sync)'
    s['screen_flow'][4]['flow']['nodes'][8]['label'] = 'Insert staging rows (Non Sync)'
    s['screen_layout'][25]['caption'] = '26. Before Sync - Sync (n): parts with Non Sync staging rows'
    s['screen_layout'][26]['caption'] = '27. After Sync - the parts are Sync (Last Sent AP POLE / GTOPAS = time of the click)'
    it = s['items']
    it[74].update({'initial': 'Non Sync', 'description': 'Options: All / Non Sync / Sync. Non Sync = the part + period has a staging row with AP POLE or GTOPAS Non Sync.'})
    it[75]['description'] = 'Returns every criterion to its initial value (Calculation period = ongoing, Sync Status = Non Sync).'
    it[82]['description'] = ('n = parts + periods with a Non Sync row in TB_H_PART_CANDIDATE_STG_SYNC (AP POLE: Current and Next; GTOPAS: Current), whatever '
                             'the filter. Disabled when n = 0. Refer Operation Description 5.24.')
    it[93].update({'source': 'TB_H_PART_CANDIDATE_STG_SYNC', 'field': 'APPOLE_SYNC_STATUS / GTOPAS_SYNC_STATUS (derived)', 'type': 'Varchar', 'len': '',
                   'description': 'Two chips per row: AP POLE and GTOPAS, Non Sync (grey) / Sync (green), worked out per part + period from the staging '
                                  '(refer 5.24). Tooltip: Last Sent AP POLE / GTOPAS (latest APPOLE_SYNC_DT / GTOPAS_SYNC_DT).'})
    clean_maps(s)
    blocks = s['data_map']['blocks']
    # [Sync] block of TB_M_PART_CANDIDATE removed by clean_maps; add the staging blocks
    blocks += [kanban_block('Key-in from screen', "'SCREEN'", 'Add Part / Edit part data - [Save]: one row per changed Pcs/Case, Max Case/Day'),
               export_block('Key-in from screen', "'SCREEN'", 'Edit mapping - [Save], status change Active <-> Inactive by Procurement'),
               _fix_sync(sync_block())]
    op = s['operation']
    op[11]['items'][1] = 'Insert the part into TB_M_PART_CANDIDATE with PART_STATUS = Candidate (refer Data Edit Mapping). A Candidate part is not sent (no staging row).'
    op[17]['items'][2] = ('Update TB_M_PART_CANDIDATE, CHANGED_BY and CHANGED_DT. Insert a staging row in TB_H_PART_CANDIDATE_STG_SYNC per changed Pcs/Case or '
                          'Max Case/Day of an Active part, and for Active <-> Inactive the EXPORT rows of 5.24 (refer Data Edit Mapping).')
    op[19]['items'][3] = ('History is read from TB_H_PART_CANDIDATE, which records every change of the part: Add / Edit by screen, Upload, mapping changes (add, '
                          'change or remove a destination) and the calculation. The sync is in TB_H_PART_CANDIDATE_STG_SYNC (not shown here). A part without '
                          'history shows message no. 12.')
    op[21] = sub(op[21], [('Calculation period YYYYMM for MAPPING / SYNC / CALC', 'Calculation period YYYYMM for MAPPING / CALC'), ('ADD / EDIT / MAPPING / SYNC / CALC', 'ADD / EDIT / MAPPING / CALC'),
                          ('SCREEN / UPLOAD / IF / RPA / BATCH', 'SCREEN / UPLOAD / BATCH'), (', CASE_DAY, SYNC_STATUS', ', CASE_DAY'), (' (IF batch user ID for SYNC, batch user ID for BATCH)', ' (batch user ID for BATCH)')])
    op[22]['text'] = ('Events: ADD / EDIT (source SCREEN or UPLOAD), MAPPING (source SCREEN or UPLOAD, PERIOD and DEST_CODE filled, FIELD_NAME CASE_DAY), CALC '
                      '(source BATCH, FIELD_NAME PART_STATUS, status set by the DAD Volume Calculation) and MAPPING with source BATCH (XD05 process 2). '
                      'The sync is not recorded here (refer 5.24).')
    op[25]['items'][5] = 'Changed parts get staging rows and show Sync Status Non Sync.'
    op[29]['items'][4] = ('XD05 writes the staging rows of the new period (refer UISS-Batch XD05); a change from Active to Inactive gives EXPORT DELETE rows (0), so the '
                          'part is sent by the next [Sync].')
    op[31]['rows'] = [r for r in op[31]['rows'] if r[0] != 'Sync Status'] + [
        ['Sync Status', 'Non Sync', 'The part + period has a staging row with APPOLE_SYNC_STATUS 0 (AP POLE) or GTOPAS_SYNC_STATUS 0 (GTOPAS).'],
        ['Sync Status', 'Sync', 'Every staging row of the part + period is sent (Last Sent = latest send time of the target).']]
    op[32]['text'] = 'Active and Inactive parts are synchronised (not Candidate). A Save after [Sync] writes new staging rows: the part is Non Sync again until the next [Sync].'
    op[33]['text'] = ('Sync Status rule (22-Nov): a part becomes Non Sync when a staging row is written, i.e. when a value sent to AP POLE / GTOPAS changes: '
                      'Pcs/Case or Max Case/Day (AP POLE), destinations or Case/Day (AP POLE; GTOPAS only when a destination appears / disappears), '
                      'Active <-> Inactive (EXPORT rows). Min MAD, Effective Start Date, Candidate <-> Inactive and a Save without change write no row.')
    op[34] = sub(op[34], [('"Sync Status"', '"Staging rows (Sync Status)"'), ('"No Sync; taken by [Sync]"', '"EXPORT DELETE (0) per destination: AP POLE and GTOPAS Non Sync"'),
                          ('"No Sync"', '"Non Sync"'), ('"Not changed"', '"No row"')])
    op[36]['items'][1] = "Search criteria: 'Calculation period' = ongoing period, 'Part Number' blank, 'Sync Status' = Non Sync."
    op[38]['items'][4] = 'With the default Sync Status = Non Sync, parts already sent are hidden until the filter is changed.'
    op[49]['items'][2] = ('Insert a staging row in TB_H_PART_CANDIDATE_STG_SYNC per added, changed or removed destination (EXPORT ADD / EDIT / DELETE, refer 5.24); '
                          'a Save without change writes no row. The total Case/Day may not exceed Max Case/Day (message no. 20).')
    op[53]['items'] = ['Prepare the run in TB_H_PART_CANDIDATE_STG_SYNC (refer 5.24): AP POLE rows of the Current and Next period, GTOPAS rows of the Current period. '
                       'Candidate parts are never sent.',
                       'Start XD07 (AP POLE) and XD06 (GTOPAS) with the run ID. Display message no. 27.',
                       'With the default filter Non Sync the parts leave the list; select Sync Status = Sync or All to see them.']
    op[55]['items'] = ['XD07 uploads to AP POLE the files LLM9Q880 (Export) and LLM9Q910 (Kanban) built from the staging rows of the run, in the order of SEND_SEQ.',
                       'XD06 compares, per part of the run, every destination with Case/Day >= 1 (latest staging value) with GTOPAS WVJA5204: Add / Delete / Keep.',
                       'The bots write nothing back to NSP; the result comes by the notification e-mail (SUCCESS / FAILED).']
    op[56]['text'] = 'When the e-mail says FAILED, the D/S team clicks [Re-send last Sync]: the rows of the last run ID are sent again in the same order (the bot sets values, so a repeat is safe).'
    op[57]['text'] = ('Interface method: RPA to AP POLE by upload files LLM9Q880 / LLM9Q910 (XD07), RPA to GTOPAS on WVJA5204 (XD06); the RPA reads only '
                      'TB_H_PART_CANDIDATE_STG_SYNC (refer UISS-Batch XD06 / XD07).')
    op[59]['items'][5] = 'Changed parts get staging rows and show Sync Status Non Sync.'
    op[61]['items'][1] = op[61]['items'][1].replace('Pcs/Day, Sync Status,', 'Pcs/Day, Sync Status AP POLE, Sync Status GTOPAS, Last Sent AP POLE, Last Sent GTOPAS,')
    op[65]['rows'] = [r for r in op[65]['rows'] if r[0] != 'Sync Status'] + [
        ['Table', STG, 'Staging of every value change for the sync (refer 5.24). Sync Status AP POLE / GTOPAS per part + period is worked out from it.']]
    op[65]['rows'][0][2] = 'Kanban Crossdock Master data, part number + period level (key PART_NO, PERIOD). Holds Pcs/Case, Max Case/Day and status.'
    op[66]['text'] = ('The sync status is not kept on TB_M_PART_CANDIDATE: every value change is a row of TB_H_PART_CANDIDATE_STG_SYNC with the Sync Status of '
                      'AP POLE and GTOPAS (22-Nov). TB_H_PART_CANDIDATE keeps the screen history.')
    # superseded sections of 17 / 20-Nov
    keep = []
    skip = False
    for x in op:
        if x.get('type') == 'heading':
            skip = x['text'] in ('Last Sync (17-Nov)', '5.22 Sync without response from the RPA (20-Nov)', '5.23 Send data without TB_R_CROSSDOCK_IF_RESULT (20-Nov)')
        if not skip:
            keep.append(x)
    s['operation'] = keep
    s['operation'] = sub(s['operation'], [('Sync Status of that month', 'Pcs/Case, Max Case/Day of that month')])
    section(s['operation'], '5.24 Sync with TB_H_PART_CANDIDATE_STG_SYNC (22-Nov)', INSERT_RULES + SYNC_RULES + SCREEN_RULES + [
        'Buttons: [Sync (n)] and [Re-send last Sync]. Columns of the Export Crossdock Master and its Export Excel: Sync Status AP POLE, Sync Status GTOPAS, '
        'Last Sent AP POLE, Last Sent GTOPAS. The RPA does not download the Export Excel any more.', REF])
    s['screen_layout'][14]['caption'] = '15. Initial Mode - ongoing period, Sync Status = Non Sync'
    for r in s['operation'][21]['rows']:
        if r[0] == 'REMARK':
            r[4] = 'Free text'
    for m in s['logging_messages']:
        if m.get('msg_id') == 'LOG4' and 'XD06' in m.get('event', ''):
            m.update({'event': '[Sync] / [Re-send last Sync]', 'cause': 'XD06 / XD07 run',
                      'message': 'Logging is done by XD06 / XD07 (refer UISS-Batch XD06 / XD07); the result comes by the notification e-mail.',
                      'action': 'Read the e-mail; FAILED: click [Re-send last Sync]'})
    for m in s['display_messages']:
        if m.get('msg_id') == 'MSG27':
            m['message'] = 'Sync started for {n} part(s): AP POLE and GTOPAS. The result comes by e-mail.'
        if m.get('msg_id') == 'MSG28':
            m.update({'event': 'Hover a Sync Status chip', 'cause': 'Part already sent', 'message': 'Last sent {date-time} (run {run ID}).', 'action': '-'})
    rev(s, '0.8', 'Sync with TB_H_PART_CANDIDATE_STG_SYNC (22-Nov): no sync column on TB_M_PART_CANDIDATE; staging rows per value change (screen); '
                  '[Sync] sets status / SEND_SEQ / run ID; Sync Status AP POLE / GTOPAS worked out from the staging (5.24).')


# ------------------------------------------------------------------ XD02 / XD03 (uploads)
def xd02(s):
    clean_maps(s)
    s['data_map']['blocks'].append(kanban_block('Upload file (valid rows)', "'UPLOAD'", 'One row per changed Pcs/Case, Max Case/Day of an Active part; '
                                                                                    'Active <-> Inactive: EXPORT rows of XD01 5.24'))
    s['func_flow']['steps'][5]['children'][2] = ('Insert a staging row in TB_H_PART_CANDIDATE_STG_SYNC per changed Pcs/Case or Max Case/Day of an Active part; '
                                                 'Active -> Inactive also writes an EXPORT DELETE (0) per destination (refer XD01 5.24). A row without change writes nothing.')
    s['func_desc'][7]['items'][4] = ('Every changed value of an Active part gets a staging row (TB_H_PART_CANDIDATE_STG_SYNC, SOURCE UPLOAD, UPLOAD_ID); the part '
                                     'is sent by the next [Sync]. A new (Candidate) part gets no staging row.')
    s['func_desc'] = sub(s['func_desc'], [('Status, Pcs/Case, Max Case/Day, Sync Status', 'Status, Pcs/Case, Max Case/Day')])
    s['sample_sheet'] = sub(s['sample_sheet'], [(', Sync Status No Sync.', ', staging rows MAX_CASE_DAY (AP POLE Non Sync).'),
                                                ('Sync Status Success -> No Sync', 'staging row MAX_CASE_DAY 24 -> 30 (AP POLE Non Sync)'),
                                                ('Sync Status and last update stay', 'no staging row'),
                                                ('Sync Status No Sync. Inactive -> Active works the same way.', 'EXPORT DELETE (0) per destination in the staging. Inactive -> Active: Procurement maps the destinations again.'),
                                                ('Total Pcs/Day 300, Sync Status No Sync,', 'Total Pcs/Day 300, no staging row (Candidate),')])
    section(s['func_desc'], '4.9 Staging rows for the sync (22-Nov)', INSERT_RULES + [REF])
    rev(s, '0.4', 'Staging rows in TB_H_PART_CANDIDATE_STG_SYNC instead of the Sync Status of TB_M_PART_CANDIDATE (22-Nov).')


def xd03(s):
    clean_maps(s)
    s['data_map']['blocks'].append(export_block('Upload file (valid rows)', "'UPLOAD'", 'One row per added / changed / removed destination of the part'))
    s['general']['outputs'][1]['description'] = 'if successful: staging rows in TB_H_PART_CANDIDATE_STG_SYNC for each changed destination'
    s['func_flow']['steps'][5]['children'][1] = ('Otherwise: update / insert / delete the destinations of the part so that its mapping matches the rows of the '
                                                 'file, and insert a staging row per added / changed / removed destination (EXPORT ADD / EDIT / DELETE).')
    s['func_desc'][7]['items'][5] = ('Every added / changed / removed destination gets a staging row in TB_H_PART_CANDIDATE_STG_SYNC (SOURCE UPLOAD, UPLOAD_ID; '
                                     'GTOPAS 0 for ADD / DELETE); file rows equal to the current mapping write nothing. The part is sent by the next [Sync].')
    s['sample_sheet'] = sub(s['sample_sheet'], [('Sync Status No Sync.', 'staging rows EXPORT (AP POLE Non Sync).'), ('Sync Status and last update stay', 'no staging row')])
    section(s['func_desc'], '4.9 Staging rows for the sync (22-Nov)', INSERT_RULES + [REF])
    rev(s, '0.4', 'Staging rows in TB_H_PART_CANDIDATE_STG_SYNC instead of the Sync Status of TB_M_PART_CANDIDATE (22-Nov).')


# ------------------------------------------------------------------ XD05
def xd05(s):
    clean_maps(s)
    s['data_map']['blocks'] += [
        kanban_block('Result of process 1 (new period)', "'BATCH'", 'Process 1: ADD PCS_CASE and ADD MAX_CASE_DAY for every part of the new period, Inactive included'),
        export_block('Result of process 2 (new period)', "'BATCH'", 'Process 2: ADD per destination of an Active part; Inactive part: DELETE (OLD = previous value, NEW 0) per destination still > 0'),
        {'source': {'table': STG, 'keys': [{'field': 'GTOPAS_SYNC_STATUS', 'value': "'0'"}, {'field': 'PERIOD', 'value': 'Period that becomes Current'}]},
         'destination': {'table': STG, 'operation': 'Update', 'description': 'Process 3 Period Rollover (day 1 00:10), then XD06 starts'},
         'mappings': [{'source_field': '-', 'dest_field': 'GTOPAS_SYNC_STATUS', 'description': "'1'"},
                      {'source_field': '-', 'dest_field': 'GTOPAS_SYNC_DT / GTOPAS_SYNC_RUN_ID', 'description': 'Rollover time / run ID'},
                      {'source_field': '-', 'dest_field': 'CHANGED_BY / CHANGED_DT', 'description': 'Batch user ID / system date-time'}]}]
    s['data_map']['blocks'][-1]['mappings'] = split(s['data_map']['blocks'][-1]['mappings'])
    s['func_flow']['steps'][15]['children'][1] = ('Every row of the new period is written to TB_H_PART_CANDIDATE_STG_SYNC (EXPORT ADD per destination, GTOPAS 0; '
                                                  'Inactive part: DELETE 0 per destination still > 0) and a history record per added / changed / removed '
                                                  'destination (event MAPPING, source BATCH).')
    fd = s['func_desc']
    fd[7]['items'][2] = ('Staging (22-Nov): process 1 writes KANBAN ADD rows (PCS_CASE, MAX_CASE_DAY) for every part of the new period, Inactive included, so the '
                         'part stays in the AP POLE Kanban; the PART_STATUS column of the staging rows is the new status.')
    fd[7]['items'][4] = ('Every status change is written to TB_H_PART_CANDIDATE (FIELD_NAME PART_STATUS, OLD_VALUE / NEW_VALUE, CREATED_DT = run date-time). '
                         'An Inactive part gets EXPORT DELETE (0) rows for its destinations still > 0 in the previous period (process 2), so AP POLE gets '
                         'Buyer-PD 0 and GTOPAS deletes the rows at the Period Rollover.')
    fd[16]['items'][2] = ('Each part is compared with its mapping of the previous period for the history (TB_H_PART_CANDIDATE, event MAPPING, source BATCH, '
                          'LAST_SOURCE = CALC). For the sync every destination of the new period is an EXPORT ADD row of TB_H_PART_CANDIDATE_STG_SYNC (GTOPAS 0).')
    fd[20]['items'][3] = ('Process 3 (new, day 1, 00:10): Period Rollover: Next becomes Current, Current becomes Past. The staging rows of the new Current period '
                          'with GTOPAS_SYNC_STATUS 0 (no date condition) are sent: GTOPAS_SYNC_STATUS 1, GTOPAS_SYNC_DT, run ID; then XD06 starts automatically. '
                          'AP POLE got the period earlier by [Sync] (Effective Month).')
    i = next(k for k, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.10 Period Rollover'))
    fd[i + 1]['items'] = ['GTOPAS WVJA5204 has no period: it always shows the Current month, so the Next period reaches GTOPAS only at the Period Rollover.',
                          'Rows taken: TB_H_PART_CANDIDATE_STG_SYNC with GTOPAS_SYNC_STATUS 0 and PERIOD = the new Current period (no date, so rows written on '
                          'day D are not skipped by a [Sync] of the old Current period). Update: GTOPAS_SYNC_STATUS 1, GTOPAS_SYNC_DT = rollover time, '
                          'GTOPAS_SYNC_RUN_ID, CHANGED_BY / CHANGED_DT; Log of the run; start XD06.',
                          'Rows of the old period still Non Sync are not sent any more (every selection has a PERIOD condition).']
    s['sample_sheet'] = sub(s['sample_sheet'], [('Mapping differs from 202609 -> Sync Status No Sync; history MAPPING/BATCH per destination.',
                                                 'Staging EXPORT ADD per destination (AP POLE / GTOPAS Non Sync); history MAPPING/BATCH per changed destination.')])
    section(fd, '4.11 Staging rows of XD05 (22-Nov)', INSERT_RULES[:3] + [
        'Process 1 / 2 on day D: KANBAN ADD (PCS_CASE, MAX_CASE_DAY) for every part of the new period; EXPORT ADD per destination of an Active part '
        '(GTOPAS 0); Inactive part: EXPORT DELETE (NEW 0) per destination still > 0 in the previous period (a destination already 0 gets no row). '
        'SOURCE BATCH, CREATED_BY batch user ID.',
        'Process 3 Period Rollover: refer 4.10.', KEY, REF])
    rev(s, '0.6', 'Staging rows in TB_H_PART_CANDIDATE_STG_SYNC for the new period and Period Rollover by GTOPAS_SYNC_STATUS 0 + PERIOD (22-Nov).')


# ------------------------------------------------------------------ XD07 (AP POLE)
def xd07(s):
    g = s['general']
    g['objective'] = [
        'To make the cross dock master of AP POLE equal to NSP by an RPA that uploads files (22-Nov): Cross Dock Kanban Part Master (LLM9Q910) and '
        'Export Customer Cross Dock Master (LLM9Q880), filled from the stored templates.',
        'Source data: only TB_H_PART_CANDIDATE_STG_SYNC (read-only DB user), rows of the run ID passed by [Sync] / [Re-send last Sync]. NSP has '
        'reduced the rows and set SEND_SEQ before the bot starts.',
        'Order: SEND_SEQ 1 Export (parts whose Max goes down) -> 2 Kanban -> 3 Export (every other part); Current period first, then Next. AP POLE '
        'checks every row: total Max Shipping Box (RCS) of the part <= Max Shipping Box Qty.',
        'The bot writes nothing back to NSP; the result comes by the notification e-mail.']
    g['operation_flow'] = {'flow': {'direction': 'TB', 'nodes': [
        {'id': 'a', 'label': '[Sync] / [Re-send last Sync] on XD01 (run ID)', 'type': 'event'},
        {'id': 'b', 'label': 'RPA: read the staging rows of the run (SEND_SEQ)', 'type': 'process'},
        {'id': 'c', 'label': 'Fill the upload files per period + SEND_SEQ', 'type': 'process'},
        {'id': 'd', 'label': 'Upload file by file (1 -> 2 -> 3), Current then Next', 'type': 'process'},
        {'id': 'e', 'label': 'Any error?', 'type': 'decision'},
        {'id': 'f', 'label': 'E-mail SUCCESS, Log', 'type': 'process'},
        {'id': 'h', 'label': 'Stop at the failed file, e-mail FAILED, Log', 'type': 'process'}],
        'edges': [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'}, {'from': 'd', 'to': 'e'},
                  {'from': 'e', 'to': 'f', 'label': 'No'}, {'from': 'e', 'to': 'h', 'label': 'Yes'}]}}
    g['inputs'] = [{'name': STG, 'type': 'DB', 'description': 'Rows with APPOLE_SYNC_RUN_ID = run ID and SEND_SEQ not NULL; Kanban pair Pcs/Case + Max '
                                                              'Case/Day from the latest Sync row of each field (refer 4.3)'},
                   {'name': 'Templates LLM9Q910 / LLM9Q880', 'type': 'File', 'description': 'Stored upload templates (not downloaded from AP POLE)'}]
    g['outputs'] = [{'name': 'AP POLE Cross Dock Kanban Part Master', 'type': 'System', 'description': 'Uploaded file LLM9Q910 (not in NSP scope)'},
                    {'name': 'AP POLE Export Customer Cross Dock Master', 'type': 'System', 'description': 'Uploaded files LLM9Q880 (not in NSP scope)'},
                    {'name': 'Log', 'type': 'DB', 'description': 'One record per run; notification e-mail'}]
    for t in g.get('extra_tables', []):
        if t['title'] == 'Parameters':
            t['rows'] = [['Target system', "'APPOLE' (AP POLE, https://ap-pole.toyota-asia.com/lm9/)"],
                         ['Method', 'RPA upload of LLM9Q910 / LLM9Q880 (22-Nov; no screen steps, no SFTP file)'],
                         ['User', 'RPA bot user with AP POLE login; read-only DB user on NSP'],
                         ['Operator ID', "'P6' (fixed) in LLM9Q910"], ['Transport Code', "'2' (fixed) in LLM9Q880"]]
    g['extra_tables'] = [t for t in g.get('extra_tables', []) if t['title'] == 'Parameters'] + [
        {'title': 'LLM9Q910 Cross Dock Kanban Part Master (file 2)', 'columns': [{'title': 'Column', 'width': 18}, {'title': 'NSP source / rule', 'width': 30}],
         'rows': [['Effective Month / Year', 'PERIOD (MM / YYYY)'], ['Operator ID', "'P6'"], ['Part No.', 'PART_NO with "-"'], ['Part Name', 'PART_NAME'],
                  ['Shipping Box Qty', 'PCS_CASE (latest Sync row)'], ['Max Shipping Box Qty', 'MAX_CASE_DAY (latest Sync row)'],
                  ['Max Allowance Qty', 'Shipping Box Qty x Max Shipping Box Qty'], ['Packing/Pallet Type ... Outer-Qty', 'Empty']]},
        {'title': 'LLM9Q880 Export Customer Cross Dock Master (files 1 and 3)', 'columns': [{'title': 'Column', 'width': 18}, {'title': 'NSP source / rule', 'width': 30}],
         'rows': [['Effective Month / Year', 'PERIOD (MM / YYYY)'], ['Part No.', 'PART_NO without "-"'], ['Buyer-PD', 'DEST_CODE as 5-2 (e.g. 9722D-10)'],
                  ['Order Type', 'ORDER_TYPE'], ['Transport Code', "'2'"], ['Max Shipping Box (RCS)', 'NEW_VALUE (0 for DELETE)'],
                  ['Shipping Box Qty, Max Shipping Box by Part No., Max Allowance Qty, Packing/Pallet Type', 'Empty']]}]
    s['func_flow'] = {'flow': {'direction': 'TB', 'nodes': [
        {'id': 'p1', 'label': 'Start (run ID from [Sync] / [Re-send last Sync])', 'type': 'process', 'step': 1},
        {'id': 'src', 'label': STG, 'type': 'db', 'lane': 'input'},
        {'id': 'p2', 'label': 'Read the rows of the run (SEND_SEQ not NULL)', 'type': 'process', 'step': 2},
        {'id': 'p3', 'label': 'Fill LLM9Q880 / LLM9Q910 per period + SEND_SEQ', 'type': 'process', 'step': 3},
        {'id': 'p4', 'label': 'Upload the files in name order, wait for each result', 'type': 'process', 'step': 4},
        {'id': 'ap', 'label': 'AP POLE Kanban / Export Cross Dock Master', 'type': 'db', 'lane': 'output'},
        {'id': 'd', 'label': 'Any error (try-catch)?', 'type': 'decision', 'step': 5},
        {'id': 'p6', 'label': 'Notification e-mail, Log end', 'type': 'process', 'step': 6},
        {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
        'edges': [{'from': 'p1', 'to': 'p2'}, {'from': 'src', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'p3', 'to': 'p4'}, {'from': 'p4', 'to': 'ap'},
                  {'from': 'p4', 'to': 'd'}, {'from': 'd', 'to': 'p6', 'label': 'No / Yes'}, {'from': 'p6', 'to': 'log'}]},
        'steps': [
            'NSP starts the flow with the run ID after [Sync] / [Re-send last Sync] (the staging is already updated). Write LOG1. The whole run is inside one try-catch.',
            {'text': 'Read TB_H_PART_CANDIDATE_STG_SYNC (read-only DB user): rows with APPOLE_SYNC_RUN_ID = run ID and SEND_SEQ not NULL.',
             'children': ['Kanban rows (SEND_SEQ 2): one row per part + period; Pcs/Case and Max Case/Day = NEW_VALUE of the latest row with '
                          'APPOLE_SYNC_STATUS 1 of each field (this run or an earlier one), so the pair is complete when only one field changed.',
                          'Export rows (SEND_SEQ 1 / 3): Max Shipping Box (RCS) = NEW_VALUE (0 for DELETE).']},
            {'text': 'Fill the stored templates: one file per period + SEND_SEQ, name <template>_<run ID>_<period>_<SEND_SEQ>.xls (e.g. LLM9Q880_20261127100000_202611_1.xls). '
                     'A file without rows is not made.',
             'children': ['Inside an Export file: per part the rows going down / deleted first, then up / added (AP POLE checks row by row).']},
            {'text': 'Upload the files one at a time in the order of their names (Current period first, then Next) and wait for each result. Write LOG3 per file.',
             'children': ['File 1 (Export, only parts whose Max goes down) -> file 2 (Kanban) -> file 3 (Export, every other part).']},
            {'text': 'Any error (try-catch): stop at the failed file, write LOG4. The files already uploaded stay in AP POLE; the other files wait for [Re-send last Sync].'},
            'Send the notification e-mail (SUCCESS / FAILED), write LOG6 and LOG2. The bot writes nothing to NSP.']}
    s['data_map']['blocks'] = [
        {'source': {'table': STG, 'keys': [{'field': 'APPOLE_SYNC_RUN_ID', 'value': 'Run ID'}, {'field': 'SEND_SEQ', 'value': '2'}]},
         'destination': {'table': 'LLM9Q910 Cross Dock Kanban Part Master (upload file)', 'operation': 'Insert', 'description': 'One row per part + period (file 2)'},
         'mappings': [{'source_field': 'PERIOD', 'dest_field': 'Effective Month / Year', 'description': 'MM / YYYY'},
                      {'source_field': '-', 'dest_field': 'Operator ID', 'description': "'P6'"},
                      {'source_field': 'PART_NO', 'dest_field': 'Part No.', 'description': 'With "-"'},
                      {'source_field': 'PART_NAME', 'dest_field': 'Part Name', 'description': ''},
                      {'source_field': 'NEW_VALUE (PCS_CASE)', 'dest_field': 'Shipping Box Qty', 'description': 'Latest row with APPOLE_SYNC_STATUS 1 of PCS_CASE for the part + period'},
                      {'source_field': 'NEW_VALUE (MAX_CASE_DAY)', 'dest_field': 'Max Shipping Box Qty', 'description': 'Latest row with APPOLE_SYNC_STATUS 1 of MAX_CASE_DAY'},
                      {'source_field': '-', 'dest_field': 'Max Allowance Qty', 'description': 'Shipping Box Qty x Max Shipping Box Qty'}]},
        {'source': {'table': STG, 'keys': [{'field': 'APPOLE_SYNC_RUN_ID', 'value': 'Run ID'}, {'field': 'LEVEL_TYPE / SEND_SEQ', 'value': "'EXPORT' / 1 or 3"}]},
         'destination': {'table': 'LLM9Q880 Export Customer Cross Dock Master (upload files)', 'operation': 'Insert', 'description': 'One row per destination + order type (files 1 and 3)'},
         'mappings': [{'source_field': 'PERIOD', 'dest_field': 'Effective Month / Year', 'description': 'MM / YYYY'},
                      {'source_field': 'PART_NO', 'dest_field': 'Part No.', 'description': 'Without "-"'},
                      {'source_field': 'DEST_CODE', 'dest_field': 'Buyer-PD', 'description': '5-2 format'},
                      {'source_field': 'ORDER_TYPE', 'dest_field': 'Order Type', 'description': ''},
                      {'source_field': '-', 'dest_field': 'Transport Code', 'description': "'2'"},
                      {'source_field': 'NEW_VALUE', 'dest_field': 'Max Shipping Box (RCS)', 'description': '0 for DELETE'}]},
        {'source': 'Result of this run', 'destination': {'table': 'Log', 'operation': 'Insert', 'description': 'Messages of the run'},
         'mappings': [{'dest_field': 'BATCH_ID', 'description': "'XD07_RPA_APPOLE'"}, {'dest_field': 'RUN_ID', 'description': 'Run ID'},
                      {'dest_field': 'STATUS', 'description': 'SUCCESS / ERROR'}, {'dest_field': 'MESSAGE', 'description': 'LOG1 - LOG6'},
                      {'dest_field': 'START_DT / END_DT', 'description': 'Start and end date-time'}]}]
    fd = s['func_desc']
    email = []
    on = False
    for x in fd:
        if x.get('type') == 'heading':
            on = x['text'].startswith('4.6 Notification Email')
        if on:
            email.append(x)
    email = sub(email, [('4.6 Notification Email', '4.5 Notification Email'), ('Nothing to process (no part Waiting)', 'Nothing to send (no row with SEND_SEQ in the run)'),
                        ('click [Sync] again on Crossdock Master Setting', 'click [Re-send last Sync] on Crossdock Master Setting'),
                        ('The downloaded Excel with the work sheet AP POLE Compare (action, result and message per row)', 'The upload files of the run with the AP POLE result per file')])
    s['func_desc'] = [
        {'type': 'heading', 'text': '4.1 Business Process'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'Procurement maintains the Kanban Crossdock Master and the D/S team the Export Crossdock Master on XD01; XD05 makes the Next period on day D. '
            'Every value change is a row of TB_H_PART_CANDIDATE_STG_SYNC (refer XD01 5.24).',
            'The D/S team clicks [Sync]: NSP reduces the Non Sync rows of the Current and Next period (first OLD / last NEW per key), sets SEND_SEQ, the '
            'run ID and LAST_SYNC_DATE_APPOLE, then starts this bot.', REF]},
        {'type': 'heading', 'text': '4.2 Upload Files and Order'},
        {'type': 'table', 'level': 0, 'row_lines': 'all', 'columns': [{'title': 'SEND_SEQ', 'width': 6}, {'title': 'File', 'width': 16}, {'title': 'Rows', 'width': 30}],
         'rows': [['1', 'LLM9Q880 Export, before Kanban', 'EXPORT rows of a part whose Max Case/Day goes down (destinations lowered first)'],
                  ['2', 'LLM9Q910 Kanban', 'Every KANBAN change and new part (Pcs/Case and Max in one row)'],
                  ['3', 'LLM9Q880 Export, after Kanban', 'EXPORT rows of every other part: Max up, new part, no KANBAN row (moves, deletes, Inactive)']]},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'File name <template>_<run ID>_<period>_<SEND_SEQ>.xls; one file per period + SEND_SEQ; Current first, then Next. A file without rows is not made.',
            'AP POLE checks every row: total Max Shipping Box (RCS) of the part <= Max Shipping Box Qty. Inside an Export file the rows of a part going '
            'down / deleted come first, then up / added.',
            'Delete of a Buyer-PD = Max Shipping Box (RCS) 0 (the row stays in AP POLE with 0). An Inactive part stays in the Kanban with its Buyer-PD 0; '
            'in the following months it has no Export row.']},
        {'type': 'heading', 'text': '4.3 Data from the Staging'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'Rows of the run: APPOLE_SYNC_RUN_ID = run ID and SEND_SEQ not NULL (Superseded rows and keys ending on their first value have no SEND_SEQ).',
            'Kanban row: Pcs/Case and Max Case/Day = NEW_VALUE of the latest row with APPOLE_SYNC_STATUS 1 of each field for the part + period (this run '
            'or an earlier one; XD05 always writes both on day D).', 'Part Name from the staging (PART_NAME column).',
            'Queries: deliverables/function_list_v2/erd/proposal_staging_sync/sql/staging_sync_queries.sql (Kanban file, Export files).']},
        {'type': 'heading', 'text': '4.4 Try-Catch and Re-send'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'The whole run is in one try-catch. Any error (login, upload screen, AP POLE error of a row, timeout) stops the run at that file.',
            'Files uploaded before the error stay in AP POLE. The D/S team clicks [Re-send last Sync]: the files of the last run are made and uploaded '
            'again in the same order (the values are set, so a repeat is safe).',
            'NSP does not receive the result (no response); the staging stays Sync. The e-mail tells SUCCESS / FAILED.']}] + email + [
        {'type': 'heading', 'text': '4.6 Open Points'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': ['Upload screen of AP POLE for LLM9Q910 / LLM9Q880 (Common File Upload) - steps of the bot TBC with the AP POLE team.']}]
    s['logging_messages'] = [
        {'event': 'Batch start', 'cause': '[Sync] / [Re-send last Sync] on XD01', 'type': 'Info', 'msg_id': 'LOG1', 'message': 'RPA cross dock master to AP POLE started. Run <RUN_ID>, <n> file(s).', 'action': {'system': 'Write the log.', 'user': '-'}},
        {'event': 'Batch end', 'cause': 'Bot finishes', 'type': 'Info', 'msg_id': 'LOG2', 'message': 'RPA cross dock master to AP POLE ended. Run <RUN_ID>, files uploaded <f>, rows <r>, status <STATUS>.', 'action': {'system': 'Write the log.', 'user': '-'}},
        {'event': 'File uploaded', 'cause': 'AP POLE accepted the file', 'type': 'Info', 'msg_id': 'LOG3', 'message': '<FILE_NAME> uploaded: <n> row(s).', 'action': {'system': 'Write the log.', 'user': '-'}},
        {'event': 'Error (try-catch)', 'cause': 'Login, upload screen, AP POLE error of a row, timeout', 'type': 'Error', 'msg_id': 'LOG4', 'message': 'RPA to AP POLE stopped at <FILE_NAME> row <n>: <ERROR_DETAIL>. Files not uploaded: <list>.', 'action': {'system': 'Stop the bot.', 'user': 'Click [Re-send last Sync]; contact PIC if it persists.'}},
        {'event': 'Unexpected error', 'cause': 'Any other system error', 'type': 'Critical', 'msg_id': 'LOG5', 'message': 'Unexpected error: <ERROR_DETAIL>.', 'action': {'system': 'Stop. STATUS = ERROR.', 'user': 'User contact PIC'}},
        {'event': 'Notification email', 'cause': 'End of the run (SUCCESS / FAILED)', 'type': 'Info', 'msg_id': 'LOG6', 'message': 'Notification email <SUCCESS / FAILED> of run <RUN_ID> sent to <recipients>.', 'action': {'system': 'Write the log.', 'user': 'Read the email; FAILED: click [Re-send last Sync].'}}]
    s['tables'] = [t for t in s['tables'] if t['name'] in (STG,)] or [json.loads(json.dumps(STG_TABLE))]
    rev(s, '1.0', 'Upload files LLM9Q910 / LLM9Q880 instead of the screen steps; source = TB_H_PART_CANDIDATE_STG_SYNC only; SEND_SEQ order 1 / 2 / 3 (22-Nov).')


# ------------------------------------------------------------------ XD06 (GTOPAS)
def xd06(s):
    g = s['general']
    g['objective'] = [
        'To make the GTOPAS Crossdock Master (WVJA5204, Depot 01) equal to NSP by an RPA, per part of the run: destination in NSP and not in GTOPAS -> '
        'Add; in both -> Keep; in GTOPAS and not in NSP -> Delete.',
        'Source data: only TB_H_PART_CANDIDATE_STG_SYNC (read-only DB user), parts of the run ID: [Sync] (Current period) or the Period Rollover (new '
        'Current period, started by XD05 process 3).',
        'GTOPAS has no period: it always shows the Current month, so the Next period is sent only at the Period Rollover.',
        'The bot writes nothing back to NSP; the result comes by the notification e-mail.']
    g['operation_flow'] = {'flow': {'direction': 'TB', 'nodes': [
        {'id': 'a', 'label': '[Sync] (Current) or Period Rollover (new period)', 'type': 'event'},
        {'id': 'b', 'label': 'RPA: parts of the run, destinations with Case/Day >= 1 (staging)', 'type': 'process'},
        {'id': 'c', 'label': 'Read GTOPAS rows of these parts, compare', 'type': 'process'},
        {'id': 'd', 'label': 'Add / Delete on WVJA5204', 'type': 'process'},
        {'id': 'e', 'label': 'Any error?', 'type': 'decision'},
        {'id': 'f', 'label': 'E-mail SUCCESS, Log', 'type': 'process'},
        {'id': 'h', 'label': 'E-mail FAILED, Log', 'type': 'process'}],
        'edges': [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'}, {'from': 'd', 'to': 'e'},
                  {'from': 'e', 'to': 'f', 'label': 'No'}, {'from': 'e', 'to': 'h', 'label': 'Yes'}]}}
    g['inputs'] = [{'name': STG, 'type': 'DB', 'description': 'Parts with GTOPAS_SYNC_RUN_ID = run ID; destinations = latest EXPORT value per destination + '
                                                              'order type of the part + period (CREATED_DT <= GTOPAS_SYNC_DT) >= 1'},
                   {'name': 'GTOPAS WVJA5204', 'type': 'System', 'description': 'Current rows of the parts (Depot 01), read by the bot'}]
    g['outputs'] = [{'name': 'GTOPAS WVJA5204', 'type': 'System', 'description': 'Rows added / deleted by the bot (not in NSP scope)'},
                    {'name': 'Log', 'type': 'DB', 'description': 'One record per run; notification e-mail'}]
    s['func_flow'] = {'flow': {'direction': 'TB', 'nodes': [
        {'id': 'p1', 'label': 'Start (run ID from [Sync] / Period Rollover)', 'type': 'process', 'step': 1},
        {'id': 'src', 'label': STG, 'type': 'db', 'lane': 'input'},
        {'id': 'p2', 'label': 'Parts of the run, NSP destinations (Case/Day >= 1)', 'type': 'process', 'step': 2},
        {'id': 'gi', 'label': 'GTOPAS WVJA5204', 'type': 'db', 'lane': 'input'},
        {'id': 'p3', 'label': 'Read GTOPAS rows of the parts', 'type': 'process', 'step': 3},
        {'id': 'p4', 'label': 'Compare: Add / Delete / Keep', 'type': 'process', 'step': 4},
        {'id': 'd', 'label': 'Any error (try-catch)?', 'type': 'decision', 'step': 5},
        {'id': 'p6', 'label': 'Notification e-mail, Log end', 'type': 'process', 'step': 6},
        {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
        'edges': [{'from': 'p1', 'to': 'p2'}, {'from': 'src', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'gi', 'to': 'p3'}, {'from': 'p3', 'to': 'p4'},
                  {'from': 'p4', 'to': 'd'}, {'from': 'd', 'to': 'p6', 'label': 'No / Yes'}, {'from': 'p6', 'to': 'log'}]},
        'steps': [
            'NSP starts the flow with the run ID: after [Sync] (rows of the Current period) or after the Period Rollover (XD05 process 3, rows of the new '
            'Current period). The staging is already updated (GTOPAS_SYNC_STATUS 1). Write LOG1. The whole run is inside one try-catch.',
            {'text': 'Read TB_H_PART_CANDIDATE_STG_SYNC (read-only DB user): parts = distinct PART_NO + PERIOD with GTOPAS_SYNC_RUN_ID = run ID.',
             'children': ['NSP destinations of a part: latest EXPORT row (largest HIST_ID, CREATED_DT <= GTOPAS_SYNC_DT) per destination + order type of '
                          'the part + period with NEW_VALUE >= 1; order types together (one GTOPAS row per P/No. + Destination Code).']},
            'Search the parts on WVJA5204 (Depot 01) and read their rows.',
            {'text': 'Compare per P/No. (without "-") + Destination Code and fill the work sheet GTOPAS Compare:',
             'children': ['In NSP only: Add (Depot 01, Maker A, Dom/Os 2, TOPAS Order Type *, Trans 2). In GTOPAS only: Delete. In both: Keep (nothing).']},
            'Any error (try-catch): stop, write LOG4; rows done before the error stay. [Re-send last Sync] or the next run compares again.',
            'Send the notification e-mail (SUCCESS / FAILED), write LOG6 and LOG2. The bot writes nothing to NSP.']}
    blocks = [b for b in s['data_map']['blocks'] if isinstance(b.get('destination'), dict) and 'GTOPAS' in b['destination'].get('table', '')]
    blocks = sub(blocks, [('XD01 Export Excel Export Crossdock Master (downloaded by the bot)', STG)])
    for b in blocks:
        if isinstance(b.get('source'), dict):
            b['source']['keys'] = [{'field': 'GTOPAS_SYNC_RUN_ID', 'value': 'Run ID (parts of the run)'},
                                   {'field': 'NEW_VALUE (latest EXPORT row per destination)', 'value': '>= 1'}]
    blocks.append({'source': 'Result of this run', 'destination': {'table': 'Log', 'operation': 'Insert', 'description': 'Messages of the run'},
                   'mappings': [{'dest_field': 'BATCH_ID', 'description': "'XD06_RPA_GTOPAS'"}, {'dest_field': 'RUN_ID', 'description': 'Run ID'},
                                {'dest_field': 'STATUS', 'description': 'SUCCESS / ERROR'}, {'dest_field': 'MESSAGE', 'description': 'LOG1 - LOG6'},
                                {'dest_field': 'START_DT / END_DT', 'description': 'Start and end date-time'}]})
    s['data_map']['blocks'] = blocks
    fd = s['func_desc']
    email = []
    on = False
    for x in fd:
        if x.get('type') == 'heading':
            on = x['text'].startswith('4.4 Notification Email')
        if on:
            email.append(x)
    email = sub(email, [('Nothing to process (no part Waiting)', 'Nothing to send (no part in the run)'),
                        ('click [Sync] again on Crossdock Master Setting', 'click [Re-send last Sync] on Crossdock Master Setting')])
    cmp_rules = next((x for x in fd if x.get('type') == 'table' and 'In NSP' in json.dumps(x)), None)
    s['func_desc'] = [
        {'type': 'heading', 'text': '4.1 Business Process'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'Every value change of the Kanban / Export Crossdock Master is a row of TB_H_PART_CANDIDATE_STG_SYNC (refer XD01 5.24). GTOPAS_SYNC_STATUS 0 '
            'only for an EXPORT ADD / DELETE (a destination appears or disappears); quantities are not sent to GTOPAS.',
            '[Sync]: the GTOPAS rows of the Current period (GTOPAS_SYNC_STATUS 0 + PERIOD = Current, no date) are set to 1 and this bot starts. The rows of '
            'the Next period wait.',
            'Period Rollover (XD05 process 3, day 1 00:10): the rows of the new Current period with GTOPAS_SYNC_STATUS 0 are set to 1 and this bot starts. '
            'XD05 writes EXPORT rows for every destination of the new period, so every part of the period is compared.', REF]},
        {'type': 'heading', 'text': '4.2 Comparison Rules'}] + ([cmp_rules] if cmp_rules else []) + [
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'Compare key: P/No. (without "-") + Destination Code; the order types of a destination are one GTOPAS row.',
            'NSP destinations = latest staging value >= 1 of the part + period of the run; only the parts of the run are compared.',
            'Why the rollover: WVJA5204 has no period. Sending the Next period on day D would change GTOPAS for the month still running; AP POLE has an '
            'Effective Month, so it gets the Next period earlier by [Sync].']},
        {'type': 'heading', 'text': '4.3 Try-Catch and Re-send'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
            'The whole run is in one try-catch; any error stops the run (LOG4). Rows added / deleted before the error stay in GTOPAS.',
            'NSP does not receive the result; the staging stays Sync. [Re-send last Sync] (or the next run) compares again and completes the rest.']}] + email + [
        {'type': 'heading', 'text': '4.5 Open Points'},
        {'type': 'bullets', 'marker': '-', 'level': 0, 'items': ['FB-176: rows of GTOPAS (Depot 01) of parts outside the run are not compared (decided 21-Nov: only the parts of the run).']}]
    s['func_desc'] = sub(s['func_desc'], [('"4.4 Notification Email', '"4.4 Notification Email')])
    s['logging_messages'] = [
        {'event': 'Batch start', 'cause': '[Sync] / Period Rollover', 'type': 'Info', 'msg_id': 'LOG1', 'message': 'RPA cross dock master to GTOPAS started. Run <RUN_ID>, <n> part(s).', 'action': {'system': 'Write the log.', 'user': '-'}},
        {'event': 'Batch end', 'cause': 'Bot finishes', 'type': 'Info', 'msg_id': 'LOG2', 'message': 'RPA cross dock master to GTOPAS ended. Run <RUN_ID>, added <a>, deleted <d>, kept <k>, status <STATUS>.', 'action': {'system': 'Write the log.', 'user': '-'}},
        {'event': 'Row changed', 'cause': 'Add / Delete on WVJA5204', 'type': 'Info', 'msg_id': 'LOG3', 'message': '<ADD / DELETE> <P_NO> <DEST_CODE>.', 'action': {'system': 'Write the log.', 'user': '-'}},
        {'event': 'Error (try-catch)', 'cause': 'Login, screen, timeout or GTOPAS error message', 'type': 'Error', 'msg_id': 'LOG4', 'message': 'RPA to GTOPAS stopped at <STEP> <P_NO> <DEST_CODE>: <ERROR_DETAIL>.', 'action': {'system': 'Stop the bot.', 'user': 'Click [Re-send last Sync]; contact PIC if it persists.'}},
        {'event': 'Unexpected error', 'cause': 'Any other system error', 'type': 'Critical', 'msg_id': 'LOG5', 'message': 'Unexpected error: <ERROR_DETAIL>.', 'action': {'system': 'Stop. STATUS = ERROR.', 'user': 'User contact PIC'}},
        {'event': 'Notification email', 'cause': 'End of the run (SUCCESS / FAILED)', 'type': 'Info', 'msg_id': 'LOG6', 'message': 'Notification email <SUCCESS / FAILED> of run <RUN_ID> sent to <recipients>.', 'action': {'system': 'Write the log.', 'user': 'Read the email; FAILED: click [Re-send last Sync].'}}]
    s['tables'] = [json.loads(json.dumps(STG_TABLE))]
    rev(s, '1.0', 'Source = TB_H_PART_CANDIDATE_STG_SYNC only; parts of the run by GTOPAS_SYNC_STATUS 0 + PERIOD ([Sync] Current, Period Rollover new period), '
                  'no date condition (22-Nov).')


FUN = {'XD01': xd01, 'XD02': xd02, 'XD03': xd03, 'XD05': xd05, 'XD06': xd06, 'XD07': xd07}
for f in sorted(glob.glob('XD*_spec.json')):
    fid = f[:4]
    if fid not in FUN:
        continue
    s = json.load(open(f))
    if any(r['date'] == D and r['description'].startswith(('Sync with TB_H', 'Staging rows', 'Upload files', 'Source = TB_H')) for r in s['revisions']):
        continue
    if fid not in ('XD06', 'XD07'):
        tables(s)
    FUN[fid](s)
    json.dump(s, open(f, 'w'), indent=1, ensure_ascii=False)
    print('patched', fid)
