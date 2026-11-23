"""23-Nov: Crossdock Master to the RPA (XD01, XD02, XD03, XD05, XD06, XD07; the ASN functions are not touched).
1. Staging per target replaces TB_H_PART_CANDIDATE_STG_SYNC: TB_H_STG_APPOLE_KANBAN (LLM9Q910 format, header of the part with OPERATION_TYPE 1-5),
   TB_H_STG_APPOLE_EXPORT (LLM9Q880 format), TB_H_STG_GTOPAS (WVJA5204). Every save calls SP_STG_WRITE (rules at the save), [Sync] calls
   SP_STG_SYNC (0 -> 1 only), views V_APPOLE_UPLOAD_KANBAN / _EXPORT give the files EXPORT_PRE, KANBAN, EXPORT_POST.
2. RPA: one Power Automate parent flow per run. Run with GTOPAS rows: XD06 first, XD07 only when GTOPAS succeeded. Run without GTOPAS rows: XD07 only.
   Period Rollover: XD06 only.
3. EFFECTIVE_START_DATE removed: a part takes effect from the period it is registered (Add Part: ongoing period by default, or the next period).
4. Edit part data: a Candidate part can become Active only; no part goes back to Candidate.
Sources: erd/proposal_staging_sync (Proposal_Tables_Staging_Per_Target.xlsx, simulation/Staging_Header_Order.html, Staging_Per_Target_Full_Flow.html).
Runs after apply_2211d."""
import glob
import importlib.util
import json
import os
import re

D = '23-Nov-26'
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = 'TB_H_PART_CANDIDATE_STG_SYNC'
K, E, G = 'TB_H_STG_APPOLE_KANBAN', 'TB_H_STG_APPOLE_EXPORT', 'TB_H_STG_GTOPAS'
REF = ('Rules and simulation: deliverables/function_list_v2/erd/proposal_staging_sync (Proposal_Tables_Staging_Per_Target.xlsx, '
       'simulation/Staging_Header_Order.html, simulation/Staging_Per_Target_Full_Flow_Simulation.xlsx).')

sp = importlib.util.spec_from_file_location('tp2', os.path.join(HERE, '..', 'erd', 'proposal_staging_sync', 'build_table_proposal_v2.py'))
tp = importlib.util.module_from_spec(sp)
sp.loader.exec_module(tp)


def conv(rows):
    out = []
    for name, typ, pk, null, default, file_col, d, _ in rows:
        text = d + (f'. File / screen column: {file_col}' if file_col else '') + (f'. Default {default}' if default and default != 'identity' else '')
        out.append([name, typ, pk, null, text])
    return out


TABLE = {
    K: {'name': K, 'kind': 'history', 'proposed': True, 'columns': conv(tp.KAN),
        'description': 'AP POLE Kanban rows in the format of the upload file LLM9Q910, one row per Kanban change of a part + period, plus the header '
                       'row (OPERATION_TYPE 5) when only the destinations changed. Written by SP_STG_WRITE (XD01, XD02, XD05); SYNC_STATUS set by '
                       'SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_KANBAN and V_APPOLE_UPLOAD_EXPORT.'},
    E: {'name': E, 'kind': 'history', 'proposed': True, 'columns': conv(tp.EXP),
        'description': 'AP POLE Export rows in the format of the upload file LLM9Q880, one row per added, changed or removed destination + order '
                       'type of a part + period. Written by SP_STG_WRITE (XD01, XD03, XD05); SYNC_STATUS set by SP_STG_SYNC. Read by XD07 through '
                       'V_APPOLE_UPLOAD_EXPORT.'},
    G: {'name': G, 'kind': 'history', 'proposed': True, 'columns': conv(tp.GTO),
        'description': 'GTOPAS WVJA5204 rows: a part + destination to add or delete, written by SP_STG_WRITE only when the destination appears or '
                       'disappears for the part (any order type) and GTOPAS does not have that state yet. Sent by [Sync] (Current period) or the '
                       'Period Rollover (new Current period). Read by XD06.'},
}

# ---------- rules shared by the UISS ----------
WRITE_RULES = [
    'Every save calls the stored procedure SP_STG_WRITE once per changed value, in the same transaction and after the master tables are '
    'updated. A save without a changed value writes nothing.',
    'Kanban (TB_H_STG_APPOLE_KANBAN): a change of Pcs/Case or Max Case/Day of an Active part writes a row with the values after the change '
    '(ACTION EDIT); Candidate -> Active and a part of a new period write ACTION ADD. OPERATION_TYPE compares the new Max with the last Max sent '
    'to AP POLE (same period, else the latest earlier period): 1 = Max down, 2 = Max up, 3 = Max same, 4 = never sent.',
    'Export (TB_H_STG_APPOLE_EXPORT): one row per added (ADD), changed (EDIT) or removed (DELETE, Max Shipping Box (RCS) 0) destination + order '
    'type. Active -> Inactive writes DELETE (0) for every destination of the part.',
    'GTOPAS (TB_H_STG_GTOPAS): a row only when the destination appears or disappears for the part (any order type) and GTOPAS does not have '
    'that state yet. A Case/Day change or an order type change of a destination that stays writes no GTOPAS row.',
    'Header: an Export change of a part + period without an unsent Kanban row writes the Kanban header with ACTION KEEP and OPERATION_TYPE 5 '
    '(current Kanban values, not uploaded). So every part of a run has one Kanban row that sets its upload order.',
    'Superseded: a new row of a key marks the older unsent row of the same key SYNC_STATUS 2. A value set back to the value already sent for the '
    'period gets SYNC_STATUS 2 too (nothing to send). Keys: Kanban PERIOD + PART_NO; Export PERIOD + NSP_PART_NO + DEST_CODE + ORDER_TYPE; '
    'GTOPAS PERIOD + P_NO + DESTINATION_CODE.',
    'NSP keeps the end state valid before the save: total Case/Day of the destinations <= Max Case/Day of the part in the period (XD01 messages '
    '14 and 20, XD02 / XD03 checks).',
]
SYNC_RULES = [
    '[Sync] calls SP_STG_SYNC with a new run ID (YYYYMMDDHHMMSS). It calculates nothing: it locks the staging tables for a moment (a save at the '
    'same time waits), sets SYNC_STATUS 0 -> 1 with SYNC_DT and SYNC_RUN_ID on the AP POLE rows of the Current and Next period and on the GTOPAS '
    'rows of the Current period, and sets the System Master parameter LAST_SYNC_DATE_APPOLE. Then it starts the RPA parent flow with the run ID.',
    'Upload files of AP POLE (views): EXPORT_PRE (LLM9Q880, order 1) = Export rows of the parts whose Kanban row of the run has OPERATION_TYPE 1; '
    'KANBAN (LLM9Q910, order 2) = Kanban rows of the run with OPERATION_TYPE 1 to 4; EXPORT_POST (LLM9Q880, order 3) = every other Export row of '
    'the run. Inside a file, per part, rows going down or DELETE (ROW_ORDER 1) come before rows going up or ADD (ROW_ORDER 2). An empty file is '
    'not made. File name <template>_<RUN_ID>_<order>_<name>.xls.',
    'RPA parent flow: a run with GTOPAS rows (a part becomes Active or Inactive, a destination is added or removed) runs XD06 first and XD07 '
    'only when GTOPAS succeeded; a run without GTOPAS rows runs XD07 only. The Period Rollover runs XD06 only.',
    'The robots write nothing back to NSP; the result comes by the notification e-mail. When it says FAILED, the D/S team clicks [Re-send last '
    'Sync] before the next [Sync]: the same run ID, the same rows and order.',
    'Rows of a past period that were not sent before the Period Rollover are never taken again: every selection has a PERIOD condition.',
]
SCREEN_RULE = ('Sync Status per part + period: AP POLE Non Sync while TB_H_STG_APPOLE_KANBAN or TB_H_STG_APPOLE_EXPORT has a row with '
               'SYNC_STATUS 0, else Sync; GTOPAS Non Sync while TB_H_STG_GTOPAS has a row with SYNC_STATUS 0, else Sync. Last Sent = latest '
               'SYNC_DT of the target.')
CODES = [['1', 'Max down', 'EXPORT_PRE, then KANBAN'], ['2', 'Max up', 'KANBAN, then EXPORT_POST'],
         ['3', 'Max same (only Pcs/Case changed, or a new period with the same Max)', 'KANBAN, then EXPORT_POST'],
         ['4', 'Never sent (new part)', 'KANBAN, then EXPORT_POST'], ['5', 'Kanban unchanged, only the destinations changed (ACTION KEEP)', 'EXPORT_POST only']]
CODE_TABLE = {'type': 'table', 'level': 0, 'row_lines': 'all',
              'columns': [{'title': 'OPERATION_TYPE', 'width': 8, 'align': 'center'}, {'title': 'Meaning', 'width': 26}, {'title': 'Upload order of the part', 'width': 20}],
              'rows': CODES}


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'


def tables(s, add):
    names = [t['name'] for t in s['tables']]
    k = names.index(OLD) if OLD in names else (names.index('TB_H_PART_CANDIDATE') + 1 if 'TB_H_PART_CANDIDATE' in names else len(names))
    s['tables'] = [t for t in s['tables'] if t['name'] not in (OLD, K, E, G)]
    for n, name in enumerate(add):
        s['tables'].insert(min(k + n, len(s['tables'])), json.loads(json.dumps(TABLE[name])))
    for t in s['tables']:
        if t['name'] == 'TB_M_PART_CANDIDATE':
            t['columns'] = [c for c in t['columns'] if c[0] != 'EFFECTIVE_START_DATE']
            for c in t['columns']:
                if c[0] == 'PERIOD':
                    c[4] = ('Calculation period YYYYMM: one row per part and period. The first row of a part is the period it is registered in '
                            '(Add Part: the ongoing period or the next one); the part takes effect from it. Current: screen and upload; Next: made by '
                            'XD05 on day D, view only until day 1; Past: view only')
                if c[0] == 'PART_STATUS':
                    c[4] = ('Candidate / Active / Inactive. Candidate -> Active: XD05 (new period) or Procurement on the screen (ongoing period). '
                            'Active <-> Inactive: XD05 or Procurement (screen, upload). No part goes back to Candidate')
        if t['name'] == 'TB_M_PART_CANDIDATE_DEST':
            for c in t['columns']:
                if c[0] == 'CASE_DAY':
                    c[4] = 'Allocated Case/Day of the destination (> 0). Every add / change / removal calls SP_STG_WRITE (Export staging row) in the same transaction'
        if t['name'] == 'TB_H_PART_CANDIDATE':
            t['description'] = re.sub(r'it is in TB_H_PART_CANDIDATE_STG_SYNC', 'it is in the staging tables (TB_H_STG_APPOLE_KANBAN, '
                                      'TB_H_STG_APPOLE_EXPORT, TB_H_STG_GTOPAS)', t['description'])
            for c in t['columns']:
                if c[0] == 'FIELD_NAME':
                    c[4] = 'Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, CASE_DAY'


def mp(cols, given, default=''):
    """Mappings for every column of a table: given = {column: (source, description)}."""
    out = []
    for c in cols:
        src, d = given.get(c[0], ('-', default or c[4]))
        out.append({'source_field': src, 'dest_field': c[0], 'description': d})
    return out


AUDIT_W = {'SOURCE': ('-', "'SCREEN' / 'UPLOAD' / 'BATCH' (caller)"), 'UPLOAD_ID': ('-', 'Upload ID when SOURCE = UPLOAD, else NULL'),
           'SYNC_STATUS': ('-', "'0'; '2' when the value equals the value already sent for the period"), 'SYNC_DT': ('-', 'NULL'),
           'SYNC_RUN_ID': ('-', 'NULL'), 'CREATED_BY': ('-', 'Login user (XD05: batch user ID)'), 'CREATED_DT': ('-', 'Server date-time'),
           'CHANGED_BY': ('-', 'NULL'), 'CHANGED_DT': ('-', 'NULL'), 'STG_ID': ('-', 'Identity')}


def write_blocks(source, which):
    kc, ec, gc = (TABLE[n]['columns'] for n in (K, E, G))
    blocks = []
    if 'K' in which:
        blocks.append({'source': source, 'destination': {'table': K, 'operation': 'Insert', 'description': 'SP_STG_WRITE (KANBAN): changed Pcs/Case or Max Case/Day of an Active part, Candidate -> Active, part of a new period; header 5 when only the destinations changed'},
                       'mappings': mp(kc, {**AUDIT_W, 'PERIOD': ('PERIOD', 'Period of the part row'), 'ACTION': ('-', "'ADD' (new part, new period) / 'EDIT' / 'KEEP' (header 5)"),
                                           'PART_STATUS': ('PART_STATUS', 'Status of the part in the period'), 'EFFECTIVE_MONTH_YEAR': ('PERIOD', 'MM/YYYY'),
                                           'OPERATOR_ID': ('-', "'P6'"), 'PART_NO': ('PART_NO', 'With "-"'), 'PART_NAME': ('PART_NAME', 'From TB_M_PART_CANDIDATE'),
                                           'SHIPPING_BOX_QTY': ('PCS_CASE', 'Value after the change'), 'MAX_SHIPPING_BOX_QTY': ('MAX_CASE_DAY', 'Value after the change'),
                                           'MAX_ALLOWANCE_QTY': ('-', 'PCS_CASE x MAX_CASE_DAY'),
                                           'OPERATION_TYPE': ('-', '1 Max down / 2 up / 3 same / 4 never sent, against the last Max sent (same period, else the latest earlier period); 5 header')})})
    if 'E' in which:
        blocks.append({'source': source, 'destination': {'table': E, 'operation': 'Insert', 'description': 'SP_STG_WRITE (EXPORT): one row per added, changed or removed destination + order type'},
                       'mappings': mp(ec, {**AUDIT_W, 'PERIOD': ('PERIOD', ''), 'NSP_PART_NO': ('PART_NO', 'With "-"'), 'DEST_CODE': ('DEST_CODE', '7 digits'),
                                           'ACTION': ('-', "'ADD' / 'EDIT' / 'DELETE'"), 'EFFECTIVE_MONTH_YEAR': ('PERIOD', 'MM/YYYY'), 'PART_NO': ('PART_NO', 'Without "-"'),
                                           'BUYER_PD': ('DEST_CODE', '5-2 format'), 'ORDER_TYPE': ('ORDER_TYPE', ''), 'TRANSPORT_CODE': ('-', "'2'"),
                                           'MAX_SHIPPING_BOX_RCS': ('CASE_DAY', 'Value after the change; 0 for DELETE')})})
    if 'G' in which:
        blocks.append({'source': source, 'destination': {'table': G, 'operation': 'Insert', 'description': 'SP_STG_WRITE (EXPORT branch): the destination appears or disappears for the part and GTOPAS does not have that state yet'},
                       'mappings': mp(gc, {**AUDIT_W, 'SYNC_STATUS': ('-', "'0'"), 'PERIOD': ('PERIOD', ''), 'ACTION': ('-', "'ADD' / 'DELETE'"), 'DEPOT_CODE': ('-', "'01'"),
                                           'P_NO': ('PART_NO', 'With "-"'), 'DESTINATION_CODE': ('DEST_CODE', ''), 'MAKER_CODE': ('-', "'A'"),
                                           'DOMESTIC_OVERSEAS': ('-', "'2'"), 'TOPAS_ORDER_TYPE': ('-', "'3'"), 'ORDER_TRANSPORTATION_CODE': ('-', "'2'")})})
    if 'S' in which:
        for n, cols, d in ((K, kc, 'Older unsent row of the same key'), (E, ec, 'Older unsent row of the same key'), (G, gc, 'Unsent row of the same part + destination')):
            blocks.append({'source': source, 'destination': {'table': n, 'operation': 'Update', 'description': f'SP_STG_WRITE: {d} -> Superseded'},
                           'mappings': [{'source_field': '-', 'dest_field': 'SYNC_STATUS', 'description': "'2'"},
                                        {'source_field': '-', 'dest_field': 'CHANGED_BY', 'description': 'Login user (XD05: batch user ID)'},
                                        {'source_field': '-', 'dest_field': 'CHANGED_DT', 'description': 'Server date-time'}]})
    return blocks


def sync_blocks(label, tables_, desc):
    out = []
    for n in tables_:
        out.append({'source': label, 'destination': {'table': n, 'operation': 'Update', 'description': desc},
                    'mappings': [{'source_field': '-', 'dest_field': 'SYNC_STATUS', 'description': "'1'"},
                                 {'source_field': '-', 'dest_field': 'SYNC_DT', 'description': 'Time of the click / rollover'},
                                 {'source_field': '-', 'dest_field': 'SYNC_RUN_ID', 'description': 'Run ID YYYYMMDDHHMMSS'},
                                 {'source_field': '-', 'dest_field': 'CHANGED_BY', 'description': 'Login user (rollover: batch user ID)'},
                                 {'source_field': '-', 'dest_field': 'CHANGED_DT', 'description': 'Server date-time'}]})
    return out


def is_old(b):
    def t(x):
        return x.get('table') if isinstance(x, dict) else x
    return OLD in str(t(b.get('destination'))) or OLD in str(t(b.get('source')))


def eff_to_period(blocks, src='Period'):
    for b in blocks:
        dest = b.get('destination')
        if isinstance(dest, dict) and dest.get('table') == 'TB_M_PART_CANDIDATE':
            maps = [m for m in b['mappings'] if m.get('dest_field') != 'EFFECTIVE_START_DATE']
            if dest.get('operation') == 'Insert' and not any(m.get('dest_field') == 'PERIOD' for m in maps):
                maps.insert(1, {'source_field': src, 'dest_field': 'PERIOD', 'description': 'Selected period: the ongoing period (default) or the next one'})
            b['mappings'] = maps


def section(lst, heading, new_items, extra=None):
    """Replace the bullets after a heading that starts like `heading`; returns the index."""
    for i, x in enumerate(lst):
        if x.get('type') == 'heading' and x['text'].split(' ')[0] == heading.split(' ')[0]:
            x['text'] = heading
            j = i + 1
            while j < len(lst) and lst[j].get('type') != 'heading':
                j += 1
            lst[i + 1:j] = [{'type': 'bullets', 'marker': '-', 'level': 0, 'items': new_items}] + (extra or [])
            return i
    raise KeyError(heading)


def put(lst, path_check, new):
    assert path_check in lst, path_check
    lst[lst.index(path_check)] = new


def fix_strings(o):
    """Generic replacements for what is left after the sections are rewritten."""
    if isinstance(o, dict):
        return {k: fix_strings(v) for k, v in o.items()}
    if isinstance(o, list):
        return [fix_strings(v) for v in o]
    if isinstance(o, str):
        o = o.replace('rows in TB_H_PART_CANDIDATE_STG_SYNC', 'rows in the staging tables').replace('a row in TB_H_PART_CANDIDATE_STG_SYNC', 'staging rows')
        o = o.replace('writes a row to TB_H_PART_CANDIDATE_STG_SYNC (LEVEL_TYPE EXPORT) in the same transaction (22-Nov)',
                      'writes the Export staging row through SP_STG_WRITE in the same transaction')
        o = o.replace('a staging row with APPOLE_SYNC_STATUS 0 (AP POLE) or GTOPAS_SYNC_STATUS 0 (GTOPAS)',
                      'a row with SYNC_STATUS 0 in the AP POLE staging (Kanban, Export) or in the GTOPAS staging')
        o = o.replace(', EFFECTIVE_START_DATE', '').replace(' (Effective Start Date removed, 23-Nov)', '').replace(' (23-Nov)', '')
        o = o.replace('TB_H_PART_CANDIDATE_STG_SYNC', 'the staging tables')
        return o
    return o


# ---------- XD01 ----------
def xd01(s):
    tables(s, [K, E, G])
    g = s['general']
    g['objective'] = [x.replace('(Part No, Min MAD, Pcs/Case, Max Case/Day, Effective Start Date)', '(Part No, Period, Min MAD, Pcs/Case, Max Case/Day)')
                      .replace('(worked out from TB_H_PART_CANDIDATE_STG_SYNC)', '(worked out from the staging tables)') for x in g['objective']]
    for b in g['buttons']:
        if b['function'].startswith('Prepare the run in TB_H_PART_CANDIDATE_STG_SYNC'):
            b['function'] = ('Call SP_STG_SYNC (refer 5.24): the staging rows with SYNC_STATUS 0 (AP POLE: Current and Next period; GTOPAS: Current '
                             'period) get the run ID, then the RPA parent flow starts. Whatever the filter shows. The label shows the number of parts, '
                             'e.g. Sync (21).')
    m3 = g['screen_modes'][3]['sections']
    m3[0]['description'] = 'Part No and Period locked; Status (Candidate or Active), Min MAD, Pcs/Case, Max Case/Day editable'
    m3[1]['description'] = 'Same as 4.a, Status Active or Inactive (no part goes back to Candidate)'
    g['screen_mode_remarks'] = [x if 'STG_SYNC' not in x else
                                '4) Sync is enabled only when a staging table has a row with SYNC_STATUS 0 (AP POLE: Current / Next, GTOPAS: Current), '
                                'not limited to the listed rows.' for x in g['screen_mode_remarks']]
    sf = s['screen_flow'][2]
    sf['notes'][0] = sf['notes'][0].replace(', Effective Start Date not before today while the part is Candidate (message no. 10), and', ' and')
    for n in s['screen_flow'][2]['flow']['nodes'] + s['screen_flow'][4]['flow']['nodes']:
        n['label'] = n['label'].replace('insert staging rows (Non Sync)', 'staging rows by SP_STG_WRITE (Non Sync)').replace('Insert staging rows (Non Sync)', 'Staging rows by SP_STG_WRITE (Non Sync)')
    s['screen_layout'][8]['caption'] = '9. Edit Mode - Candidate part (Status Candidate or Active)'
    s['screen_layout'][9]['caption'] = '10. Edit Mode - Active part (Status Active or Inactive)'
    it = s['items']
    for x in it:
        if x.get('field') == 'EFFECTIVE_START_DATE':
            x.update({'name': 'Period', 'field': 'PERIOD', 'type': 'Char', 'len': '6', 'io': 'I/O', 'control': 'Combo Box', 'justified': 'Left',
                      'initial': 'Add: the ongoing period', 'required': 'Y', 'format': 'Mon YYYY (stored YYYYMM)',
                      'validation': 'Add: the ongoing period or the next period. Edit: locked',
                      'description': 'Add: the ongoing period (default) or the next period, marked (ongoing) / (next); the part takes effect from it. '
                                     'Edit: locked (part of the key), tooltip message no. 10. A part of the next period is view only until that period '
                                     'becomes the ongoing one.'})
        if x.get('name') == 'Status' and x.get('control') == 'Combo Box' and x.get('source') == 'TB_M_PART_CANDIDATE':
            x['validation'] = 'Add: always Candidate. Edit of a Candidate part: Candidate or Active. Edit of an Active / Inactive part: Active or Inactive'
            x['description'] = ('Add: locked to Candidate (tooltip \'New parts are automatically Candidate\'). Edit: a Candidate part can become Active '
                                '(ongoing period); an Active or Inactive part can be Active or Inactive; no part goes back to Candidate.')
        if x.get('name') == 'Calculation period' and x.get('source') == 'Key-in':
            x['description'] = x['description'].replace("the ongoing one is marked '(ongoing)'", "the ongoing one is marked '(ongoing)', the next one '(next)'")
        if x.get('name') == 'Sync (n)':
            x['description'] = ('n = parts + periods with a row SYNC_STATUS 0 in the staging tables (AP POLE: Current and Next; GTOPAS: Current), '
                                'whatever the filter. Disabled when n = 0. Refer Operation Description 5.24.')
        if x.get('source') == OLD:
            x.update({'source': f'{K} / {E}, {G}', 'field': 'SYNC_STATUS (derived)',
                      'description': 'Two chips per row: AP POLE (Kanban or Export staging) and GTOPAS (GTOPAS staging), Non Sync (grey) / Sync (green), '
                                     'per part + period (refer 5.24). Tooltip: Last Sent AP POLE / GTOPAS (latest SYNC_DT).'})
        if isinstance(x.get('description'), str):
            x['description'] = x['description'].replace('Upload (A/E), Effective Start Date', 'Upload (A/E), Period')
    for d in s['display_messages']:
        if d.get('msg_id') == 'MSG10':
            d.update({'event': "Hover 'Period' in Edit", 'cause': 'The part is registered', 'message': 'The period cannot be changed after the part is registered.'})
    op = s['operation']
    for o in op:
        if 'items' not in o:
            continue
        new = []
        for t in o['items']:
            if t.startswith("Open the 'Add Part Candidate Crossdock' modal."):
                t = ("Open the 'Add Part Candidate Crossdock' modal. 'Status' = Candidate and locked (a new part is always Candidate); 'Period' = the "
                     "ongoing period (default) or the next period: the part takes effect from it.")
            elif t.startswith('Insert the part into TB_M_PART_CANDIDATE with PART_STATUS = Candidate'):
                t = ('Insert the part into TB_M_PART_CANDIDATE with PART_STATUS = Candidate and PERIOD = the selected period. When the ongoing period '
                     'is selected and XD05 has already made the next period (between day D and the Period Rollover), insert the same row for the next '
                     'period too, so the next XD05 run calculates the part. A Candidate part is not sent (no staging row).')
            elif t.startswith("Open the 'Edit part data' modal"):
                t = ("Open the 'Edit part data' modal with the saved values. 'Part No' and 'Period' are locked. 'Status': a Candidate part can stay "
                     "Candidate or become Active; an Active or Inactive part can be Active or Inactive; no part goes back to Candidate.")
            elif t.startswith("'Effective Start Date' is editable only"):
                t = ('Only rows of the ongoing period can be edited. A part registered for the next period has no [Edit] until its period becomes the '
                     'ongoing period.')
            elif t.startswith('Update TB_M_PART_CANDIDATE, CHANGED_BY and CHANGED_DT. Insert a staging row'):
                t = ('Update TB_M_PART_CANDIDATE, CHANGED_BY and CHANGED_DT. Active -> Inactive also deletes the mapping of the period '
                     '(TB_M_PART_CANDIDATE_DEST). Call SP_STG_WRITE for the staging rows (refer 5.24 and 5.25).')
            elif t.startswith('Insert a staging row in TB_H_PART_CANDIDATE_STG_SYNC per added, changed or removed destination'):
                t = ('Call SP_STG_WRITE per added, changed or removed destination: Export ADD / EDIT / DELETE (0), a GTOPAS row when the destination '
                     'appears or disappears for the part, the Kanban header (OPERATION_TYPE 5) when the Kanban did not change (refer 5.24). A Save '
                     'without change writes no row. The total Case/Day may not exceed Max Case/Day (message no. 20).')
            elif t.startswith('Prepare the run in TB_H_PART_CANDIDATE_STG_SYNC'):
                t = ('Call SP_STG_SYNC (refer 5.24): the AP POLE rows of the Current and Next period and the GTOPAS rows of the Current period with '
                     'SYNC_STATUS 0 get SYNC_STATUS 1, SYNC_DT and the run ID. Candidate parts are never sent.')
            elif t.startswith('Start XD07 (AP POLE) and XD06 (GTOPAS) with the run ID.'):
                t = 'Start the RPA parent flow with the run ID (refer UISS-Batch XD06 / XD07). Display message no. 27.'
            elif t.startswith('XD07 uploads to AP POLE the files LLM9Q880'):
                t = ('The parent flow checks the run: with GTOPAS rows (a part becomes Active or Inactive, a destination is added or removed) XD06 '
                     'runs first and XD07 starts only when GTOPAS succeeded; without GTOPAS rows XD07 runs at once.')
            elif t.startswith('XD06 compares, per part of the run'):
                t = ('XD06 adds or deletes the part + destination rows of the run on GTOPAS WVJA5204. XD07 uploads the files of the run from the '
                     'views V_APPOLE_UPLOAD_EXPORT / _KANBAN in the order EXPORT_PRE, KANBAN, EXPORT_POST.')
            elif 'Add Part: into the ongoing period.' in t:
                t = t.replace('Add Part: into the ongoing period.', 'Add Part: into the ongoing period (default) or the next period.')
            elif t.startswith('Sheet \'Kanban Crossdock Master\': rows of the active filter'):
                t = t.replace('Status, Effective Start Date, CREATED_DT', 'Status, CREATED_DT')
            elif t.startswith("Sheet 'Upload': every registered part"):
                t = t.replace('Upload (A/E) = E, Effective Start Date)', 'Upload (A/E) = E, Period YYYYMM)')
            elif t.startswith('XD05 writes the staging rows of the new period'):
                t = ('XD05 writes the staging rows of the new period through SP_STG_WRITE (refer UISS-Batch XD05 4.11); a change from Active to '
                     'Inactive gives Export DELETE rows (0), so the part is sent by the next [Sync].')
            new.append(t)
        o['items'] = new
    for o in op:
        if o.get('type') == 'item' and o['text'].startswith('Interface method: RPA to AP POLE'):
            o['text'] = ('Interface method: one Power Automate parent flow per run starts XD06 (RPA on GTOPAS WVJA5204) and XD07 (RPA upload of '
                         'LLM9Q880 / LLM9Q910 to AP POLE); the RPA reads only the staging tables and the views (refer UISS-Batch XD06 / XD07).')
        if o.get('type') == 'text' and o['text'].startswith('Sync Status rule: a part becomes Non Sync'):
            o['text'] = ('Sync Status rule: a part becomes Non Sync when SP_STG_WRITE writes a staging row, that is when a value AP POLE or GTOPAS '
                         'holds changes: Pcs/Case or Max Case/Day (Kanban), a destination or its Case/Day (Export; GTOPAS only when a destination '
                         'appears or disappears), Active -> Inactive (Export DELETE 0). Min MAD, a Candidate part and a save without change write no row.')
        if o.get('type') == 'text' and o['text'].startswith('The sync status is not kept on TB_M_PART_CANDIDATE'):
            o['text'] = (f'The sync status is not kept on TB_M_PART_CANDIDATE: every value change is a row of {K}, {E} or {G} with its SYNC_STATUS. '
                         'TB_H_PART_CANDIDATE keeps the screen history.')
        if o.get('type') == 'table' and o.get('rows') and o['rows'][0][0] == 'Status Candidate -> Active':
            o['columns'][1]['title'] = 'Staging rows'
            o['rows'] = [['Status Candidate -> Active (screen, ongoing period, or XD05)', 'Kanban ADD, OPERATION_TYPE 4 (2 or 3 when the part was sent before)', 'Add in AP POLE; GTOPAS when mapped'],
                         ['Status Active -> Inactive (screen, upload or XD05)', 'Export DELETE (0) per destination, Kanban header 5, GTOPAS DELETE', 'Delete in GTOPAS; AP POLE Buyer-PD 0 (the part stays in the Kanban)'],
                         ['Status Inactive -> Active', 'Kanban EDIT only when Pcs/Case or Max changes; Export ADD when the destinations are mapped again', 'Add again'],
                         ['Pcs/Case or Max Case/Day of an Active part', 'Kanban EDIT, OPERATION_TYPE 1 / 2 / 3', 'AP POLE Kanban; GTOPAS keeps (no quantity)'],
                         ['Destination or Case/Day of the mapping', 'Export ADD / EDIT / DELETE; GTOPAS when a destination appears or disappears; Kanban header 5', 'AP POLE Export; GTOPAS Add / Delete'],
                         ['Min MAD', 'No row', 'Not sent to any target'],
                         ['Candidate part (Add, Edit)', 'No row', 'Never in GTOPAS / AP POLE'],
                         ['Save without change', 'No row', 'Nothing to send']]
        if o.get('type') == 'table' and o.get('rows') and any(r[1] == OLD for r in o['rows'] if len(r) > 2) and o['rows'][0][0] == 'Table':
            i = next(k for k, r in enumerate(o['rows']) if r[1] == OLD)
            o['rows'][i:i + 1] = [['Table', K, 'AP POLE Kanban rows (LLM9Q910 format) and the header of the part (OPERATION_TYPE 1 to 5); refer 5.24.'],
                                  ['Table', E, 'AP POLE Export rows (LLM9Q880 format); refer 5.24.'],
                                  ['Table', G, 'GTOPAS rows (part + destination Add / Delete); refer 5.24.']]
        if o.get('type') == 'table' and o.get('rows') and o['rows'][0][0] == 'Add Part [Save]':
            o['rows'] = [
                ['Add Part [Save]', 'TB_M_PART_CANDIDATE', 'Add', '1 row for the new part in the selected period (ongoing or next), PART_STATUS Candidate. When the ongoing period is selected after day D, 1 more row for the next period.'],
                ['', 'TB_H_PART_CANDIDATE', 'Add', 'EVENT_TYPE ADD, SOURCE SCREEN, OLD_VALUE NULL (history of the new part).'],
                ['', 'Staging tables', '-', 'No row: a Candidate part is not sent.'],
                ['Edit part data [Save]', 'TB_M_PART_CANDIDATE', 'Edit', 'The part row: Status, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, CHANGED_BY / CHANGED_DT.'],
                ['', 'TB_M_PART_CANDIDATE_DEST', 'Delete', 'Active -> Inactive: every destination of the part in the period.'],
                ['', 'TB_H_PART_CANDIDATE', 'Add', '1 row per changed field, EVENT_TYPE EDIT, SOURCE SCREEN, old and new value.'],
                ['', K, 'Add', 'Active part: 1 row with the new Pcs/Case and Max (EDIT, OPERATION_TYPE 1 / 2 / 3). Candidate -> Active: ADD (OPERATION_TYPE 4). Active -> Inactive: header (KEEP, 5).'],
                ['', E, 'Add', 'Active -> Inactive: 1 DELETE row (0) per destination.'],
                ['', G, 'Add', 'Active -> Inactive: 1 DELETE row per destination GTOPAS has.'],
                ['Edit mapping [Save]', 'TB_M_PART_CANDIDATE_DEST', 'Add', '1 row per new destination + order type of the part and period.'],
                ['', 'TB_M_PART_CANDIDATE_DEST', 'Edit', 'CASE_DAY of a kept destination whose Case/Day changed, CHANGED_BY / CHANGED_DT.'],
                ['', 'TB_M_PART_CANDIDATE_DEST', 'Delete', 'The row of a removed destination.'],
                ['', 'TB_H_PART_CANDIDATE', 'Add', '1 row per added, changed or removed destination, EVENT_TYPE MAPPING, FIELD_NAME CASE_DAY.'],
                ['', E, 'Add', '1 row per added (ADD), changed (EDIT) or removed (DELETE, 0) destination.'],
                ['', G, 'Add', '1 row when a destination appears or disappears for the part (any order type).'],
                ['', K, 'Add', 'Header (KEEP, OPERATION_TYPE 5) when the part + period has no unsent Kanban row.'],
                ['Every save above', 'Staging tables', 'Edit', 'The older unsent row of the same key: SYNC_STATUS 2 (Superseded).'],
                ['[Sync]', 'Staging tables', 'Edit', 'SP_STG_SYNC: SYNC_STATUS 0 -> 1, SYNC_DT, SYNC_RUN_ID (AP POLE Current + Next, GTOPAS Current). No row is added.'],
                ['', 'System Master', 'Edit', 'LAST_SYNC_DATE_APPOLE = time of the click.'],
                ['[Re-send last Sync]', 'Staging tables', '-', 'The rows of the last run ID are sent again (refer 5.16 c). No row is added.'],
                ['Upload Excel [Validate file]', 'Same tables as the Save above', 'Add / Edit / Delete', 'Written by the upload batch, SOURCE UPLOAD: XD02 for Kanban Crossdock Master, XD03 for Export Crossdock Master (refer UISS-Batch).']]
    i = section(op, '5.24 Sync with the staging tables', WRITE_RULES + SYNC_RULES + [SCREEN_RULE, REF], [CODE_TABLE])
    s['data_map']['blocks'] = [b for b in s['data_map']['blocks'] if not is_old(b)]
    eff_to_period(s['data_map']['blocks'], 'Period (Add Part)')
    s['data_map']['blocks'] += write_blocks('Key-in from screen (SP_STG_WRITE)', 'KEGS')
    s['data_map']['blocks'] += sync_blocks('[Sync] (SP_STG_SYNC)', [K, E, G], '[Sync]: rows with SYNC_STATUS 0 (AP POLE: Current + Next, GTOPAS: Current)')
    rev(s, '0.11', 'Staging per target: TB_H_STG_APPOLE_KANBAN / _EXPORT / TB_H_STG_GTOPAS replace TB_H_PART_CANDIDATE_STG_SYNC, SP_STG_WRITE at the '
                   'save (OPERATION_TYPE 1-5, Superseded), SP_STG_SYNC at [Sync], RPA parent flow (5.24, 5.25). Effective Start Date replaced by '
                   'Period (Add Part: ongoing or next period). Candidate part: Candidate or Active only.')


# ---------- XD02 ----------
def xd02(s):
    tables(s, [K, E, G])
    st = s['func_flow']['steps'][5]
    st['children'] = [('Call SP_STG_WRITE per changed value: Kanban EDIT of an Active part (OPERATION_TYPE 1 / 2 / 3); Active -> Inactive: the '
                       'mapping of the period is deleted, Export DELETE (0) per destination, GTOPAS DELETE and the Kanban header (refer XD01 5.24). '
                       'A row without change writes nothing.') if 'STG_SYNC' in c else c for c in st['children']]
    fd = s['func_desc']
    for o in fd:
        if 'items' in o:
            o['items'] = [('Every changed value of an Active part goes to the staging tables through SP_STG_WRITE (SOURCE UPLOAD, UPLOAD_ID); the '
                           'part is sent by the next [Sync]. A new (Candidate) part gets no staging row.') if 'STG_SYNC' in t else t for t in o['items']]
        if o.get('type') == 'table' and o.get('rows') and o['rows'][0][0] in ('1', 1):
            for r in o['rows']:
                if r[0] == '7':
                    r[1], r[2] = ('Period is required for flag A and must be the ongoing period or the next period (YYYYMM). The part takes effect from it; '
                                  'when the ongoing period is given after day D, the row is also written for the next period.'), 'Period'
                if r[0] == '8':
                    r[1], r[2] = ('Flag E: Period must be the ongoing period (the period of the export). A part registered for the next period cannot be '
                                  'changed until its period becomes the ongoing period.'), 'Period'
    section(fd, '4.9 Staging rows for the sync', [WRITE_RULES[0], WRITE_RULES[1], WRITE_RULES[2], WRITE_RULES[3], WRITE_RULES[4], WRITE_RULES[5],
                                                  'SOURCE UPLOAD, UPLOAD_ID of the upload. The part is sent by the next [Sync] (refer XD01 5.24).', REF])
    for r in s['appendix'][1]['rows']:
        if r[0] == 'Effective Start Date':
            r[0], r[1] = 'Period', 'YYYYMM: the ongoing period or the next period (flag A); the ongoing period (flag E)'
    ss = s['sample_sheet']['sections']
    a = ss[0]
    a['columns'][5] = 'Period'
    for r in a['rows']:
        if r[5]:
            r[5] = '202609' if r[0] != 'PART-I' else '202609'
    for sec in ss[1:3]:
        ci = sec['columns'].index('Effective Start Date')
        sec['columns'][ci] = 'Period'
        for r in sec['rows']:
            r[ci] = '202609' if r[ci] else ''
    b = {r[0]: r for r in ss[1]['rows']}
    b['N1'][9] = 'Inserted in 202609. Status Candidate, Total Pcs/Day 300, no staging row (Candidate), Part Name from TB_M_PART_MASTER.'
    b['N2'][1], b['N2'][8], b['N2'][9] = 'Add another part into the next period', '202610', 'Inserted in 202610 (next period, view only until 1-Oct). Total Pcs/Day 480. N1 and N2 can be in one file.'
    b['N3'][1], b['N3'][9] = 'Edit a Candidate part, change values', 'Updated. Max Case/Day 20 -> 18, Total Pcs/Day 270. No staging row (Candidate part).'
    b['N4'][9] = 'Updated. Max Case/Day 24 -> 30, Total Pcs/Day 1,800. Kanban staging row EDIT, OPERATION_TYPE 2 (AP POLE Non Sync). Mapping is not changed.'
    b['N7'][9] = 'Updated. Max Case/Day 24 -> 20 (not below mapped 20). Kanban staging row EDIT, OPERATION_TYPE 1: its Export rows go before the Kanban file.'
    b['N8'][9] = ('Updated. Status Active -> Inactive, the mapping of the period is deleted: Export DELETE (0) per destination, GTOPAS DELETE, '
                  'Kanban header 5 (AP POLE and GTOPAS Non Sync). Inactive -> Active: no staging row until the destinations are mapped again.')
    c = {r[0]: r for r in ss[2]['rows'] if r[0] in ('E10', 'E11', 'E12')}
    ci = ss[2]['columns'].index('Period')
    c['E10'][1], c['E10'][ci], c['E10'][9] = 'Add without period', '', 'Check 7: Period is required for flag A.'
    c['E11'][1], c['E11'][ci], c['E11'][9] = 'Add into a past period', '202608', 'Check 7: Period must be the ongoing or the next period.'
    c['E12'][1], c['E12'][ci], c['E12'][9] = 'Edit with the next period', '202610', 'Check 8: flag E uses the ongoing period (202609).'
    s['sample_sheet']['intro'] = [x.replace('mapping of the ongoing calculation period = Sep 2026.', 'ongoing period = 202609 (Sep 2026), next period = 202610.')
                                  for x in s['sample_sheet']['intro']]
    s['data_map']['blocks'] = [b for b in s['data_map']['blocks'] if not is_old(b)]
    eff_to_period(s['data_map']['blocks'], 'Period (file)')
    s['data_map']['blocks'] += write_blocks('Upload file (SP_STG_WRITE, SOURCE UPLOAD)', 'KEGS')
    rev(s, '0.5', 'Staging per target through SP_STG_WRITE (4.9). Column Period replaces Effective Start Date: flag A ongoing or next period, flag E '
                  'ongoing period (checks 7, 8).')


# ---------- XD03 ----------
def xd03(s):
    tables(s, [K, E, G])
    for o in s['general']['outputs']:
        if 'STG_SYNC' in o['description']:
            o['description'] = 'if successful: staging rows (Export, GTOPAS when a destination appears or disappears, Kanban header 5) for each changed destination'
    st = s['func_flow']['steps'][5]
    st['children'] = [c.replace('and insert a staging row per added / changed / removed destination (EXPORT ADD / EDIT / DELETE).',
                                'and call SP_STG_WRITE per added / changed / removed destination (Export ADD / EDIT / DELETE).') for c in st['children']]
    fd = s['func_desc']
    for o in fd:
        if 'items' in o:
            o['items'] = [('Every added / changed / removed destination goes to the staging through SP_STG_WRITE (SOURCE UPLOAD, UPLOAD_ID): an Export '
                           'row, a GTOPAS row when the destination appears or disappears for the part, and the Kanban header (OPERATION_TYPE 5) when '
                           'the Kanban did not change. File rows equal to the current mapping write nothing. The part is sent by the next [Sync].')
                          if 'STG_SYNC' in t else t for t in o['items']]
    section(fd, '4.9 Staging rows for the sync', [WRITE_RULES[0], WRITE_RULES[2], WRITE_RULES[3], WRITE_RULES[4], WRITE_RULES[5], WRITE_RULES[6],
                                                  'SOURCE UPLOAD, UPLOAD_ID of the upload. The part is sent by the next [Sync] (refer XD01 5.24).', REF])
    for sec in s['sample_sheet']['sections']:
        for r in sec['rows']:
            r[-1] = (r[-1].replace('staging rows EXPORT (AP POLE Non Sync)', 'Export staging rows and Kanban header 5 (AP POLE Non Sync)')
                     .replace('no staging row.', 'no staging row.'))
    s['data_map']['blocks'] = [b for b in s['data_map']['blocks'] if not is_old(b)]
    eff_to_period(s['data_map']['blocks'])
    s['data_map']['blocks'] += write_blocks('Upload file (SP_STG_WRITE, SOURCE UPLOAD)', 'KEGS')
    rev(s, '0.5', 'Staging per target through SP_STG_WRITE: Export rows, GTOPAS rows, Kanban header 5 (4.9).')


# ---------- XD05 ----------
def xd05(s):
    tables(s, [K, E, G])
    g = s['general']
    for x in g['inputs']:
        if 'Effective Start Date' in x['description']:
            x['description'] = 'Registered parts: Min MAD and status, every part with a row in the period'
    ff = s['func_flow']
    for n in ff['flow']['nodes']:
        n['label'] = n['label'].replace('Select parts (Effective Start Date)', 'Select parts (rows of the period)')
    for st in ff['steps']:
        if isinstance(st, dict):
            st['children'] = [
                ('Take every part with a row in the Current period. A part registered for the next period before day D already has its next row: '
                 'it is calculated and that row is kept (no second insert).') if c.startswith('Skip a part whose EFFECTIVE_START_DATE') else
                ('Every row of the new period goes to the staging through SP_STG_WRITE: Export ADD per destination; DELETE (0) for a destination of '
                 'the previous period not mapped any more and for every destination of an Inactive part still > 0; GTOPAS only for a destination that '
                 'appears or disappears. A history record per added / changed / removed destination (event MAPPING, source BATCH).')
                if 'STG_SYNC' in c else c for c in st['children']]
    fd = s['func_desc']
    for o in fd:
        if 'items' not in o:
            continue
        new = []
        for t in o['items']:
            if t.startswith('Parts whose EFFECTIVE_START_DATE is after the run date'):
                t = ('Parts calculated: every part with a row in the Current period, and a part registered for the next period before day D (its next '
                     'row exists already). A part takes effect from the period it is registered (Effective Start Date removed, 23-Nov).')
            elif t.startswith('Staging (22-Nov): process 1 writes KANBAN ADD rows'):
                t = ('Staging: process 1 calls SP_STG_WRITE (Kanban ADD) for every part of the new period, Inactive included, so the part stays in '
                     'the AP POLE Kanban. OPERATION_TYPE compares the new Max with the Max sent for the previous period: 1 down, 2 up, 3 same, 4 never '
                     'sent. PART_STATUS of the row is the new status.')
            elif 'For the sync every destination of the new period is an EXPORT ADD row' in t:
                t = t.split(' For the sync')[0] + (' For the sync, process 2 calls SP_STG_WRITE per destination of the new period (Export ADD) and per '
                                                   'destination of the previous period not mapped any more (Export DELETE 0).')
            elif t.startswith('Process 3 (new, day 1, 00:10): Period Rollover'):
                t = ('Process 3 (day 1, 00:10): Period Rollover: Next becomes Current, Current becomes Past. The GTOPAS staging rows of the new '
                     'Current period with SYNC_STATUS 0 get SYNC_STATUS 1, SYNC_DT and a run ID; then the RPA parent flow runs XD06 only (RUN_TYPE '
                     'ROLLOVER). AP POLE got the period earlier by [Sync] (Effective Month / Year).')
            elif t.startswith('Rows taken: TB_H_PART_CANDIDATE_STG_SYNC with GTOPAS_SYNC_STATUS 0'):
                t = (f'Rows taken: {G} with SYNC_STATUS 0 and PERIOD = the new Current period (no date condition). Update: SYNC_STATUS 1, SYNC_DT = '
                     'rollover time, SYNC_RUN_ID, CHANGED_BY / CHANGED_DT; Log of the run; start the RPA parent flow with RUN_TYPE ROLLOVER.')
            new.append(t)
        o['items'] = new
    section(fd, '4.11 Staging rows of XD05', [WRITE_RULES[0],
        'Process 1 / 2 on day D: Kanban ADD (Pcs/Case, Max) for every part of the new period, OPERATION_TYPE against the Max sent for the previous '
        'period (AP POLE keeps the previous Effective Month active until a newer one comes). Active part: Export ADD per destination; DELETE (0) for '
        'a destination of the previous period not mapped any more. Inactive part: Export DELETE (0) per destination still > 0 in the previous period; '
        'in the later periods no row (AP POLE keeps the 0). GTOPAS rows only for a destination that appears or disappears. SOURCE BATCH, CREATED_BY '
        'batch user ID.',
        'A part registered for the next period before day D keeps its next row; XD05 writes no second row for it. A Candidate part writes no staging row.',
        'Process 3 Period Rollover: refer 4.10.', WRITE_RULES[5], REF])
    for m in s['logging_messages']:
        if 'Effective Start Date' in m.get('cause', ''):
            m['cause'] = 'Part registered for a later period'
            m['message'] = 'Part No <PART_NO> skipped: registered for period <PERIOD>.'
    sec = s['sample_sheet']['sections'][1]
    ci = sec['columns'].index('Effective Start Date')
    sec['columns'][ci] = 'Period registered'
    for r in sec['rows']:
        if r[ci]:
            r[ci] = '202609'
        r[-1] = r[-1].replace('Effective Start Date after the run date: not calculated, no result record.',
                              'Registered for the next period after day D: not calculated in this run, no result record.')
    for sec in s['sample_sheet']['sections']:
        for r in sec['rows']:
            if isinstance(r[-1], str): r[-1] = r[-1].replace('Staging EXPORT ADD per destination (AP POLE / GTOPAS Non Sync)', 'Export staging ADD per destination (AP POLE Non Sync); '
                                  'GTOPAS rows only for the destinations that are new for the part')
    s['data_map']['blocks'] = [b for b in s['data_map']['blocks'] if not is_old(b)]
    for b in s['data_map']['blocks']:
        b['mappings'] = [m for m in b['mappings'] if m.get('dest_field') != 'EFFECTIVE_START_DATE' and 'EFFECTIVE_START_DATE' not in str(m.get('source_field'))]
        src = b.get('source')
        if isinstance(src, dict):
            src['keys'] = [k for k in src.get('keys', []) if 'EFFECTIVE_START_DATE' not in str(k.get('field'))]
    s['data_map']['blocks'] += write_blocks('XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)', 'KEGS')
    s['data_map']['blocks'] += sync_blocks('XD05 process 3 Period Rollover', [G], 'Rows of the new Current period with SYNC_STATUS 0')
    rev(s, '0.7', 'Staging per target through SP_STG_WRITE (4.11); Period Rollover updates TB_H_STG_GTOPAS and starts the RPA parent flow (XD06 only). '
                  'Effective Start Date removed: every part with a row in the period is calculated.')


# ---------- XD06 / XD07 (RPA) ----------
PARENT = [
    'One Power Automate parent flow per run (CDX_SYNC_PARENT), started by NSP with RUN_ID and RUN_TYPE (SYNC, RESEND, ROLLOVER).',
    'Scenario 1 (run with GTOPAS rows: a part becomes Active or Inactive, a destination is added or removed): XD06 GTOPAS first; XD07 AP POLE '
    'starts only when every GTOPAS row succeeded. When GTOPAS fails, AP POLE stops: XD07 does not start and the e-mail says FAILED.',
    'Scenario 2 (run without GTOPAS rows: Max Case/Day, Pcs/Case, Case/Day, order type of a destination that stays): XD07 only.',
    'Period Rollover (RUN_TYPE ROLLOVER): XD06 only, for the GTOPAS rows of the new Current period.',
    'Choice of the scenario: SELECT COUNT(*) FROM TB_H_STG_GTOPAS WHERE SYNC_RUN_ID = run ID (> 0: scenario 1).',
]
FAIL = {'type': 'table', 'level': 0, 'row_lines': 'all',
        'columns': [{'title': 'Case', 'width': 16}, {'title': 'GTOPAS (XD06)', 'width': 14}, {'title': 'AP POLE (XD07)', 'width': 14}, {'title': 'D/S does', 'width': 16}],
        'rows': [['Scenario 1, GTOPAS fails on a row', 'Other rows still done; failed rows listed', 'Not started', '[Re-send last Sync]: GTOPAS again, then AP POLE'],
                 ['Scenario 1, GTOPAS OK, AP POLE rejects a row', 'Done', 'Stops at that row; next files not sent', '[Re-send last Sync]'],
                 ['Scenario 2, AP POLE rejects a row', 'Skipped', 'Stops at that row', '[Re-send last Sync]'],
                 ['Period Rollover, GTOPAS fails', 'Failed rows listed', 'Not part of the rollover', 'Re-send the rollover run'],
                 ['Robot or PC down before the start', 'Not started', 'Not started', '[Re-send last Sync]']]}


def flow(nodes, edges):
    return {'flow': {'direction': 'TB', 'nodes': nodes, 'edges': edges}}


def xd06(s):
    g = s['general']
    g['objective'] = [
        'To make the GTOPAS Crossdock Master (WVJA5204, Depot 01) follow NSP by an RPA: add the part + destination rows that appear in NSP and '
        'delete the rows that disappear.',
        f'Source data: only {G} (read-only DB user), rows of the run ID: [Sync] (Current period), [Re-send last Sync] or the Period Rollover (new '
        'Current period, XD05 process 3).',
        'Started by the RPA parent flow: in scenario 1 XD06 runs before XD07 and its result decides whether XD07 starts (refer 4.1).',
        'GTOPAS has no period: it always shows the Current month, so the Next period reaches GTOPAS only at the Period Rollover.',
        'The robot writes nothing back to NSP; the result comes by the notification e-mail.']
    g['inputs'] = [{'name': G, 'type': 'DB', 'description': 'Rows with SYNC_RUN_ID = run ID: ACTION ADD / DELETE per part + destination'},
                   {'name': 'GTOPAS WVJA5204', 'type': 'System', 'description': 'Rows of the parts of the run (Depot 01), read by the robot'}]
    g['outputs'] = [{'name': 'GTOPAS WVJA5204', 'type': 'System', 'description': 'Rows added / deleted by the robot (not in NSP scope)'},
                    {'name': 'Result to the parent flow', 'type': 'Variable', 'description': 'STATUS SUCCESS / FAILED and the failed rows'},
                    {'name': 'Log', 'type': 'DB', 'description': 'One record per run; notification e-mail'}]
    for t in g.get('extra_tables', []):
        for r in t.get('rows', []):
            if r[0] == 'Method':
                r[1] = ('RPA desktop flow CDX_XD06_GTOPAS started by the Power Automate parent flow CDX_SYNC_PARENT ([Sync], [Re-send last Sync], '
                        'Period Rollover); it works on GTOPAS screen Crossdock Master (23-Nov)')
            if r[0] == 'Compare key':
                r[1] = 'P/No. + Destination Code (one GTOPAS row per part + destination, whatever the order type)'
    g['operation_flow'] = flow(
        [{'id': 'a', 'label': '[Sync] / Re-send (scenario 1) or Period Rollover', 'type': 'event'},
         {'id': 'b', 'label': 'Parent flow starts XD06 with the run ID', 'type': 'process'},
         {'id': 'c', 'label': 'Rows of TB_H_STG_GTOPAS of the run', 'type': 'process'},
         {'id': 'd', 'label': 'Add / Delete on WVJA5204', 'type': 'process'},
         {'id': 'e', 'label': 'Every row OK?', 'type': 'decision'},
         {'id': 'f', 'label': 'SUCCESS: parent flow starts XD07 (not for the rollover)', 'type': 'process'},
         {'id': 'h', 'label': 'FAILED: XD07 not started, e-mail', 'type': 'process'}],
        [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'}, {'from': 'd', 'to': 'e'},
         {'from': 'e', 'to': 'f', 'label': 'Yes'}, {'from': 'e', 'to': 'h', 'label': 'No'}])['flow']
    s['func_flow'] = {**flow(
        [{'id': 'p1', 'label': 'Start (run ID, RUN_TYPE from the parent flow)', 'type': 'process', 'step': 1},
         {'id': 'src', 'label': G, 'type': 'db', 'lane': 'input'},
         {'id': 'p2', 'label': 'Rows of the run (ADD / DELETE)', 'type': 'process', 'step': 2},
         {'id': 'gi', 'label': 'GTOPAS WVJA5204', 'type': 'db', 'lane': 'input'},
         {'id': 'p3', 'label': 'Per row: Add or Delete (already done = OK)', 'type': 'process', 'step': 3},
         {'id': 'd', 'label': 'Every row OK?', 'type': 'decision', 'step': 4},
         {'id': 'p5', 'label': 'Result to the parent flow, e-mail, Log', 'type': 'process', 'step': 5},
         {'id': 'log', 'label': 'Log', 'type': 'db', 'lane': 'output'}],
        [{'from': 'p1', 'to': 'p2'}, {'from': 'src', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'gi', 'to': 'p3'}, {'from': 'p3', 'to': 'd'},
         {'from': 'd', 'to': 'p5', 'label': 'Yes / No'}, {'from': 'p5', 'to': 'log'}]),
        'steps': [
            'The parent flow starts XD06 with the run ID and RUN_TYPE (SYNC / RESEND: scenario 1; ROLLOVER). NSP has already set the rows to '
            'SYNC_STATUS 1 with this run ID. Write LOG1.',
            {'text': f'Read {G} (read-only DB user): rows with SYNC_RUN_ID = run ID, ordered by P_NO, DESTINATION_CODE.',
             'children': ['ACTION ADD: Depot 01, P/No., Destination Code, Maker A, Domestic/Overseas 2, TOPAS Order Type 3, Order Transportation Code 2.',
                          'ACTION DELETE: the row of P/No. + Destination Code (MT = DEL on the screen).']},
            {'text': 'Process every row on WVJA5204 (Depot 01). Write LOG3 per row.',
             'children': ['A row already in the wanted state (Add of an existing row, Delete of a missing row) counts as OK, so a re-send is safe.',
                          'A failed row is listed (LOG4) and the next rows are still processed: GTOPAS rows do not depend on each other.']},
            'Return STATUS to the parent flow: SUCCESS when every row is OK, else FAILED with the failed rows. In scenario 1 the parent flow starts '
            'XD07 only on SUCCESS.',
            'The parent flow sends one notification e-mail per run (GTOPAS result, and AP POLE result when XD07 ran). Write LOG6 and LOG2. The '
            'robot writes nothing to NSP.']}
    s['data_map'] = {'blocks': [
        {'source': {'table': G, 'keys': [{'field': 'SYNC_RUN_ID', 'value': 'Run ID'}, {'field': 'ACTION', 'value': "'ADD'"}]},
         'destination': {'table': 'GTOPAS Crossdock Master (WVJA5204, by RPA)', 'operation': 'Insert', 'description': 'Part + destination added (not in NSP scope; done on the screen)'},
         'mappings': [{'source_field': 'DEPOT_CODE', 'dest_field': 'Depot Code', 'description': "'01'"},
                      {'source_field': 'P_NO', 'dest_field': 'P/No.', 'description': 'With "-"'},
                      {'source_field': 'DESTINATION_CODE', 'dest_field': 'Destination Code', 'description': '7 digits, the same in NSP and GTOPAS'},
                      {'source_field': 'MAKER_CODE', 'dest_field': 'Maker Code', 'description': "'A'"},
                      {'source_field': 'DOMESTIC_OVERSEAS', 'dest_field': 'Domestic/Overseas', 'description': "'2'"},
                      {'source_field': 'TOPAS_ORDER_TYPE', 'dest_field': 'TOPAS Order Type', 'description': "'3'"},
                      {'source_field': 'ORDER_TRANSPORTATION_CODE', 'dest_field': 'Order Transportation Code', 'description': "'2'"}]},
        {'source': {'table': G, 'keys': [{'field': 'SYNC_RUN_ID', 'value': 'Run ID'}, {'field': 'ACTION', 'value': "'DELETE'"}]},
         'destination': {'table': 'GTOPAS Crossdock Master (WVJA5204, by RPA)', 'operation': 'Delete', 'description': 'Row of P/No. + Destination Code (MT = DEL)'},
         'mappings': [{'source_field': 'P_NO', 'dest_field': 'P/No.', 'description': 'Row to delete'},
                      {'source_field': 'DESTINATION_CODE', 'dest_field': 'Destination Code', 'description': 'Row to delete'},
                      {'source_field': '-', 'dest_field': 'MT', 'description': "'DEL'"}]},
        {'source': 'RPA run', 'destination': {'table': 'Log', 'operation': 'Insert', 'description': 'Messages of the run'},
         'mappings': [{'source_field': '-', 'dest_field': 'BATCH_ID', 'description': "'XD06_RPA_GTOPAS'"},
                      {'source_field': '-', 'dest_field': 'RUN_ID', 'description': 'Run ID'},
                      {'source_field': '-', 'dest_field': 'STATUS', 'description': 'SUCCESS / FAILED'},
                      {'source_field': '-', 'dest_field': 'MESSAGE', 'description': 'LOG1 - LOG6'},
                      {'source_field': '-', 'dest_field': 'START_DT / END_DT', 'description': 'Start and end date-time'}]}]}
    fd = s['func_desc']
    i_mail = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.4'))
    i_open = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.5'))
    mail = fd[i_mail:i_open]
    s['func_desc'] = [{'type': 'heading', 'text': '4.1 Parent Flow and Scenarios'}, {'type': 'bullets', 'marker': '-', 'level': 0, 'items': PARENT},
                      {'type': 'heading', 'text': '4.2 Rows and Rules'},
                      {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                          f'XD06 reads only {G}: one row per part + destination that appears (ADD) or disappears (DELETE) for the part, whatever the order '
                          'type. NSP writes the row at the save (SP_STG_WRITE) and sends it with SP_STG_SYNC (Current period) or the Period Rollover.',
                          'A Case/Day change or an order type change of a destination that stays writes no GTOPAS row.',
                          'Rows of the parts outside the run are not touched.', REF]},
                      {'type': 'heading', 'text': '4.3 Errors and Re-send'},
                      {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                          'A failed row is listed and the next rows are processed. The result goes back to the parent flow: FAILED stops AP POLE in '
                          'scenario 1.',
                          'When the e-mail says FAILED, the D/S team clicks [Re-send last Sync] before the next [Sync]: the same run ID; rows done '
                          'before are OK again (already in GTOPAS / already gone).']}, FAIL] + mail
    for x in s['func_desc']:
        if x.get('type') == 'heading' and x['text'].startswith('4.4'):
            x['text'] = '4.4 Notification Email (Power Automate)'
    s['tables'] = [json.loads(json.dumps(TABLE[G]))]
    rev(s, '1.1', f'Source {G} (rows ADD / DELETE of the run); started by the RPA parent flow: scenario 1 GTOPAS before AP POLE, a failed GTOPAS '
                  'stops AP POLE; Period Rollover XD06 only (23-Nov).')


def xd07(s):
    g = s['general']
    g['objective'] = [
        'To make the cross dock master of AP POLE follow NSP by an RPA that uploads the files Cross Dock Kanban Part Master (LLM9Q910) and Export '
        'Customer Cross Dock Master (LLM9Q880), filled from the stored templates.',
        'Source data: the views V_APPOLE_UPLOAD_KANBAN and V_APPOLE_UPLOAD_EXPORT on TB_H_STG_APPOLE_KANBAN / _EXPORT (read-only DB user), rows of the '
        'run ID of [Sync] / [Re-send last Sync]. NSP set every rule at the save; the views only read it.',
        'Order: EXPORT_PRE (Export rows of the parts whose Max goes down) -> KANBAN -> EXPORT_POST (every other Export row). AP POLE checks every row: '
        'total Max Shipping Box (RCS) of the part <= Max Shipping Box Qty.',
        'Started by the RPA parent flow: in scenario 1 only after XD06 succeeded; in scenario 2 at once (refer 4.1).',
        'The robot writes nothing back to NSP; the result comes by the notification e-mail.']
    g['inputs'] = [{'name': 'V_APPOLE_UPLOAD_EXPORT', 'type': 'DB view', 'description': 'Export rows of the run with FILE_NO (1 EXPORT_PRE / 3 EXPORT_POST) and ROW_ORDER'},
                   {'name': 'V_APPOLE_UPLOAD_KANBAN', 'type': 'DB view', 'description': 'Kanban rows of the run with OPERATION_TYPE 1 to 4 (file KANBAN)'},
                   {'name': 'Templates LLM9Q910 / LLM9Q880', 'type': 'File', 'description': 'Stored upload templates (not downloaded from AP POLE)'}]
    for t in g.get('extra_tables', []):
        for r in t.get('rows', []):
            if r[0] == 'Method':
                r[1] = 'RPA desktop flow CDX_XD07_APPOLE started by the Power Automate parent flow CDX_SYNC_PARENT; upload of LLM9Q910 / LLM9Q880 (23-Nov)'
        if 'title' in t:
            t['title'] = (t['title'].replace('(file 2)', '(file KANBAN, order 2)').replace('(files 1 and 3)', '(files EXPORT_PRE and EXPORT_POST, orders 1 and 3)'))
        for r in t.get('rows', []):
            if len(r) > 1 and isinstance(r[1], str):
                r[1] = (r[1].replace('NEW_VALUE (PCS_CASE)', 'SHIPPING_BOX_QTY').replace('NEW_VALUE (MAX_CASE_DAY)', 'MAX_SHIPPING_BOX_QTY')
                        .replace('NEW_VALUE (0 for DELETE)', 'MAX_SHIPPING_BOX_RCS (0 for DELETE)').replace('NEW_VALUE', 'MAX_SHIPPING_BOX_RCS'))
    g['operation_flow'] = flow(
        [{'id': 'a', 'label': '[Sync] / Re-send: scenario 1 after GTOPAS OK, or scenario 2', 'type': 'event'},
         {'id': 'b', 'label': 'Parent flow starts XD07 with the run ID', 'type': 'process'},
         {'id': 'c', 'label': 'Read the views: files of the run', 'type': 'process'},
         {'id': 'd', 'label': 'Upload EXPORT_PRE -> KANBAN -> EXPORT_POST', 'type': 'process'},
         {'id': 'e', 'label': 'Every file OK?', 'type': 'decision'},
         {'id': 'f', 'label': 'E-mail SUCCESS, Log', 'type': 'process'},
         {'id': 'h', 'label': 'Stop at the rejected file, e-mail FAILED, Log', 'type': 'process'}],
        [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'd'}, {'from': 'd', 'to': 'e'},
         {'from': 'e', 'to': 'f', 'label': 'Yes'}, {'from': 'e', 'to': 'h', 'label': 'No'}])['flow']
    s['func_flow'] = {**flow(
        [{'id': 'p1', 'label': 'Start (run ID from the parent flow)', 'type': 'process', 'step': 1},
         {'id': 'src', 'label': 'V_APPOLE_UPLOAD_EXPORT / _KANBAN', 'type': 'db', 'lane': 'input'},
         {'id': 'p2', 'label': 'Rows of the run per file', 'type': 'process', 'step': 2},
         {'id': 'p3', 'label': 'Fill the templates (empty file not made)', 'type': 'process', 'step': 3},
         {'id': 'p4', 'label': 'Upload in order, wait for each result', 'type': 'process', 'step': 4},
         {'id': 'd', 'label': 'File rejected?', 'type': 'decision', 'step': 5},
         {'id': 'p6', 'label': 'Result to the parent flow, e-mail, Log', 'type': 'process', 'step': 6},
         {'id': 'ap', 'label': 'AP POLE', 'type': 'db', 'lane': 'output'}],
        [{'from': 'p1', 'to': 'p2'}, {'from': 'src', 'to': 'p2'}, {'from': 'p2', 'to': 'p3'}, {'from': 'p3', 'to': 'p4'}, {'from': 'p4', 'to': 'ap'},
         {'from': 'p4', 'to': 'd'}, {'from': 'd', 'to': 'p6', 'label': 'No / Yes'}]),
        'steps': [
            'The parent flow starts XD07 with the run ID (scenario 1 after XD06 succeeded, scenario 2 at once). NSP has already set the rows to '
            'SYNC_STATUS 1 with this run ID. Write LOG1.',
            {'text': 'Read the views (read-only DB user) for the run ID:',
             'children': ['V_APPOLE_UPLOAD_EXPORT WHERE FILE_NO = 1 (EXPORT_PRE) and FILE_NO = 3 (EXPORT_POST), ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID.',
                          'V_APPOLE_UPLOAD_KANBAN (OPERATION_TYPE 1 to 4), ORDER BY PERIOD, PART_NO.']},
            {'text': 'Fill the stored templates: one file per kind, Current and Next period together (Effective Month / Year per row). Name '
                     '<template>_<run ID>_<order>_<name>.xls, e.g. LLM9Q880_20261204100000_1_EXPORT_PRE.xls. A file without rows is not made.',
             'children': ['Inside an Export file, per part: rows going down or DELETE (ROW_ORDER 1) first, then up or ADD (ROW_ORDER 2).']},
            {'text': 'Upload the files one at a time: 1 EXPORT_PRE -> 2 KANBAN -> 3 EXPORT_POST, and wait for each result. Write LOG3 per file.'},
            {'text': 'A rejected file stops the run (LOG4): the files already uploaded stay in AP POLE; the next files wait for [Re-send last Sync].'},
            'Return STATUS to the parent flow; the parent flow sends the notification e-mail (SUCCESS / FAILED). Write LOG6 and LOG2. The robot '
            'writes nothing to NSP.']}
    s['data_map'] = {'blocks': [
        {'source': {'table': 'V_APPOLE_UPLOAD_KANBAN', 'keys': [{'field': 'RUN_ID', 'value': 'Run ID'}]},
         'destination': {'table': 'LLM9Q910 Cross Dock Kanban Part Master (upload file)', 'operation': 'Insert', 'description': 'File KANBAN (order 2): one row per Kanban row of the run with OPERATION_TYPE 1 to 4'},
         'mappings': [{'source_field': 'EFFECTIVE_MONTH_YEAR', 'dest_field': 'Effective Month / Year', 'description': 'MM/YYYY'},
                      {'source_field': 'OPERATOR_ID', 'dest_field': 'Operator ID', 'description': "'P6'"},
                      {'source_field': 'PART_NO', 'dest_field': 'Part No.', 'description': 'With "-"'},
                      {'source_field': 'PART_NAME', 'dest_field': 'Part Name', 'description': ''},
                      {'source_field': 'SHIPPING_BOX_QTY', 'dest_field': 'Shipping Box Qty', 'description': 'Pcs/Case'},
                      {'source_field': 'MAX_SHIPPING_BOX_QTY', 'dest_field': 'Max Shipping Box Qty', 'description': 'Max Case/Day'},
                      {'source_field': 'MAX_ALLOWANCE_QTY', 'dest_field': 'Max Allowance Qty', 'description': 'Shipping Box Qty x Max Shipping Box Qty'}]},
        {'source': {'table': 'V_APPOLE_UPLOAD_EXPORT', 'keys': [{'field': 'RUN_ID', 'value': 'Run ID'}, {'field': 'FILE_NO', 'value': '1 (EXPORT_PRE) / 3 (EXPORT_POST)'}]},
         'destination': {'table': 'LLM9Q880 Export Customer Cross Dock Master (upload files)', 'operation': 'Insert', 'description': 'Files EXPORT_PRE and EXPORT_POST: one row per Export row of the run, ordered by ROW_ORDER per part'},
         'mappings': [{'source_field': 'EFFECTIVE_MONTH_YEAR', 'dest_field': 'Effective Month / Year', 'description': 'MM/YYYY'},
                      {'source_field': 'PART_NO', 'dest_field': 'Part No.', 'description': 'Without "-"'},
                      {'source_field': 'BUYER_PD', 'dest_field': 'Buyer-PD', 'description': '5-2 format'},
                      {'source_field': 'ORDER_TYPE', 'dest_field': 'Order Type', 'description': ''},
                      {'source_field': 'TRANSPORT_CODE', 'dest_field': 'Transport Code', 'description': "'2'"},
                      {'source_field': 'MAX_SHIPPING_BOX_RCS', 'dest_field': 'Max Shipping Box (RCS)', 'description': '0 for DELETE'}]},
        {'source': 'RPA run', 'destination': {'table': 'Log', 'operation': 'Insert', 'description': 'Messages of the run'},
         'mappings': [{'source_field': '-', 'dest_field': 'BATCH_ID', 'description': "'XD07_RPA_APPOLE'"},
                      {'source_field': '-', 'dest_field': 'RUN_ID', 'description': 'Run ID'},
                      {'source_field': '-', 'dest_field': 'STATUS', 'description': 'SUCCESS / FAILED'},
                      {'source_field': '-', 'dest_field': 'MESSAGE', 'description': 'LOG1 - LOG6'},
                      {'source_field': '-', 'dest_field': 'START_DT / END_DT', 'description': 'Start and end date-time'}]}]}
    fd = s['func_desc']
    heads = [i for i, x in enumerate(fd) if x.get('type') == 'heading']
    mail_i = next((i for i in heads if 'Email' in fd[i]['text'] or 'Notification' in fd[i]['text']), None)
    nxt = [i for i in heads if mail_i is not None and i > mail_i]
    mail = fd[mail_i:(nxt[0] if nxt else len(fd))] if mail_i is not None else []
    view_sql = ('View rules: FILE_NO = 1 (EXPORT_PRE) when the Kanban row of the same run, part and period has OPERATION_TYPE 1, else 3 '
                '(EXPORT_POST; every part of a run has its Kanban row, OPERATION_TYPE 1 to 5). ROW_ORDER = 1 when MAX_SHIPPING_BOX_RCS is lower than the '
                'value sent before for the key (same period, else the latest earlier period), else 2. V_APPOLE_UPLOAD_KANBAN leaves out OPERATION_TYPE 5.')
    s['func_desc'] = [{'type': 'heading', 'text': '4.1 Parent Flow and Scenarios'}, {'type': 'bullets', 'marker': '-', 'level': 0, 'items': PARENT},
                      {'type': 'heading', 'text': '4.2 Files and Order'},
                      {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [SYNC_RULES[1], view_sql,
                          'Why the order: AP POLE checks every uploaded row (total Max Shipping Box (RCS) of the part <= Max Shipping Box Qty). When Max goes '
                          'down the destinations come down first (EXPORT_PRE); when Max goes up, stays or is new the Max goes first (KANBAN). Inside a file the '
                          'total first goes down, then up to the end value, so it never passes the Max.',
                          'AP POLE keeps the rows of an Effective Month active until a newer month comes; NSP still sends every row of a new period.']},
                      CODE_TABLE,
                      {'type': 'heading', 'text': '4.3 Errors and Re-send'},
                      {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                          'A rejected file stops the run: the files already uploaded stay in AP POLE, the next files are not uploaded.',
                          'When the e-mail says FAILED, the D/S team clicks [Re-send last Sync] before the next [Sync]: the same run ID and the same files; '
                          'AP POLE sets the same values again, so a repeat is safe.', REF]}, FAIL] + mail
    for x in s['func_desc']:
        if x.get('type') == 'heading' and ('Email' in x['text'] or 'Notification' in x['text']):
            x['text'] = '4.4 Notification Email (Power Automate)'
    s['tables'] = [json.loads(json.dumps(TABLE[K])), json.loads(json.dumps(TABLE[E]))]
    rev(s, '1.1', 'Source: views V_APPOLE_UPLOAD_KANBAN / _EXPORT on TB_H_STG_APPOLE_KANBAN / _EXPORT; files EXPORT_PRE, KANBAN, EXPORT_POST from '
                  'OPERATION_TYPE; started by the RPA parent flow (scenario 1 after GTOPAS OK, scenario 2 at once) (23-Nov).')


def rpa_common(s, target):
    fd = s['func_desc']
    for x in fd:
        if x.get('type') == 'bullets' and x['items'] and x['items'][0].startswith('The cloud flow of the RPA sends one email'):
            x['items'] = ['The parent flow sends one email per run, so the user knows the result without opening NSP.',
                          "The email holds the result of every target of the run: GTOPAS and AP POLE in scenario 1 (AP POLE 'not started' when GTOPAS "
                          'failed), AP POLE only in scenario 2, GTOPAS only for the Period Rollover.',
                          'One email per run: the retries of the same run send no email; only the final result does.']
        if x.get('type') == 'bullets' and x['items'] and x['items'][0].startswith('Example subject'):
            x['items'][0] = 'Example subject: [Crossdock Sync][SYNC][FAILED] Run 20261127103000 - 12 part(s).'
        if x.get('type') == 'table' and x.get('rows') and x['rows'][0][0] == 'E1':
            x['rows'][0][2] = 'End of the run, after the last row / file of every target'
            x['rows'][-1] = ['-', 'No GTOPAS row in the run (scenario 2)' if target == 'GTOPAS' else 'No AP POLE row in the run (only a Period Rollover)',
                             'XD06 is not started; the email shows AP POLE only' if target == 'GTOPAS' else 'XD07 is not started; the email shows GTOPAS only', '-']
        if x.get('type') == 'table' and x.get('rows') and x['rows'][0][0] == 'Sender':
            for r in x['rows']:
                if r[0] == 'Subject':
                    r[1] = '[Crossdock Sync][SYNC | RESEND | ROLLOVER][SUCCESS | FAILED] Run <RUN_ID> - <n> part(s)'
                if r[0] == 'Body 1. Run':
                    r[1] = 'RUN_ID, RUN_TYPE, scenario, targets run, started / ended, [Sync] by <user> at <date-time>, period(s) sent'
    for m in s['logging_messages']:
        if m['msg_id'] == 'LOG1':
            m['cause'] = ('Parent flow: scenario 1 or Period Rollover' if target == 'GTOPAS' else 'Parent flow: scenario 1 after GTOPAS OK, or scenario 2')
            if target == 'GTOPAS':
                m['message'] = 'RPA cross dock master to GTOPAS started. Run <RUN_ID>, <n> row(s).'
        if m['msg_id'] == 'LOG2' and target == 'GTOPAS':
            m['message'] = 'RPA cross dock master to GTOPAS ended. Run <RUN_ID>, added <a>, deleted <d>, already done <k>, failed <f>, status <STATUS>.'
        if m['msg_id'] == 'LOG4':
            if target == 'GTOPAS':
                m['event'] = 'Row failed / error (try-catch)'
                m['message'] = 'RPA to GTOPAS failed at <STEP> <P_NO> <DEST_CODE>: <ERROR_DETAIL>.'
                m['action']['system'] = ('Row error: list the row and go to the next row. Login or screen error: stop. STATUS FAILED; in scenario 1 '
                                         'the parent flow does not start XD07.')
            else:
                m['action']['system'] = 'Stop the bot. STATUS FAILED; the next files are not uploaded.'
    for t in s['general'].get('extra_tables', []):
        for r in t.get('rows', []):
            if target == 'GTOPAS':
                if r[0] == 'User':
                    r[1] = 'RPA bot user (GTOPAS login); read-only DB user on NSP'
                if r[0] == 'Compare key':
                    r[0], r[1] = 'Row key', 'P/No. + Destination Code (one GTOPAS row per part + destination, whatever the order type)'
                if r[0] == 'Search: P/No., Destination Code, Maker Code, Dom/Os, TOPAS Order Type, Trans Code':
                    r[1] = 'P/No. + Destination Code to find the row of the run'
                if r[0] == '[Search] / [NextPage]':
                    r[1] = 'Check whether the row is there before the Add / Delete'
                if r[0] == 'Message':
                    r[1] = 'MZD34006FEI: Registration completed. Any other message = the row failed (listed, next row continues)'
            else:
                fix = {'Effective Month / Year': 'EFFECTIVE_MONTH_YEAR (MM/YYYY)', 'Shipping Box Qty': 'SHIPPING_BOX_QTY (Pcs/Case)',
                       'Max Shipping Box Qty': 'MAX_SHIPPING_BOX_QTY (Max Case/Day)', 'Max Allowance Qty': 'MAX_ALLOWANCE_QTY',
                       'Buyer-PD': 'BUYER_PD (DEST_CODE as 5-2, e.g. 9722D-10)', 'Order Type': 'ORDER_TYPE', 'Transport Code': "TRANSPORT_CODE '2'"}
                if r[0] in fix and t.get('title', '').startswith('LLM9Q'):
                    r[1] = fix[r[0]]
                if r[0] == 'Part No.' and t.get('title', '').startswith('LLM9Q910'):
                    r[1] = 'PART_NO with "-"'
                if r[0] == 'Part No.' and t.get('title', '').startswith('LLM9Q880'):
                    r[1] = 'PART_NO without "-"'
    if target == 'GTOPAS':
        s['general']['extra_tables'] = [t for t in s['general'].get('extra_tables', []) if not t.get('title', '').startswith('RPA work sheet')]


_x06, _x07 = xd06, xd07
xd06 = lambda s: (_x06(s), rpa_common(s, 'GTOPAS'))
xd07 = lambda s: (_x07(s), rpa_common(s, 'APPOLE'))

FUN = {'XD01': xd01, 'XD02': xd02, 'XD03': xd03, 'XD05': xd05, 'XD06': xd06, 'XD07': xd07}
for f in sorted(glob.glob(os.path.join(HERE, 'XD*_spec.json'))):
    fid = os.path.basename(f)[:4]
    if fid not in FUN:
        continue
    s = json.load(open(f))
    if any(r['date'] == D and r['description'].startswith(('Staging per target', 'Source ', 'Source:')) for r in s['revisions']):
        continue
    FUN[fid](s)
    s = {k: (fix_strings(v) if k not in ('revisions', 'tables', 'header') else v) for k, v in s.items()}
    json.dump(s, open(f, 'w'), indent=1, ensure_ascii=False)
    print('patched', fid)
