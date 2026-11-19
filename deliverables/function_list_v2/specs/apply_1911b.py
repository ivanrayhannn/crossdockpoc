"""19-Nov (2): decisions of the user on the Crossdock Master.
- Names: Part List -> Kanban Crossdock Master, Mapping per Destination -> Export Crossdock Master (screens, Export Excel sheets and files).
- Period on the Kanban Crossdock Master: TB_M_PART_CANDIDATE per PART_NO + PERIOD (as TB_M_PART_CANDIDATE_DEST).
- Periods: Past (view only), Current (screen / upload), Next (made by XD05 on day D, view only). Period Rollover on day 1 (XD05 process 3).
- Order Type per destination row (system master **, C, 9, V): the same destination may have 2 rows in a period with another order type.
- XD07: Effective Month / Year = period (MM, YYYY); Current first, then Next; Max Case/Day down -> destinations first, then the part.
- XD06: GTOPAS has no period: always the Current period; synced automatically after the Period Rollover.
Runs after apply_1911 (last step of the chain)."""
import glob
import json

D = '19-Nov-26'
NAMES = [('Crossdock_Part_List_', 'Crossdock_Kanban_Master_'), ('Crossdock_Mapping_per_Destination_', 'Crossdock_Export_Master_'),
         ('Mapping per Destination', 'Export Crossdock Master'), ('Part List', 'Kanban Crossdock Master')]
PERIOD_COL = ['PERIOD', 'CHAR(6)', 'Y', 'N', 'Calculation period YYYYMM (19-Nov): one row per part and period. Current: screen / upload; '
              'Next: made by XD05 on day D (view only until day 1); Past: view only']
OT_COL = ['ORDER_TYPE', 'VARCHAR(2)', 'Y', 'N', "Order Type of the row (system master: '**', 'C', '9', 'V'; default '**'). One row per part, period, "
          'destination and order type (19-Nov)']
RULES = {
    'periods': ('Periods (19-Nov): Past = view only; Current (M) = changed by screen and upload; Next (M+1) = made by XD05 on day D (system master), '
                'view only until day 1. On day 1 the Period Rollover (XD05 process 3) makes Next the Current period.'),
    'kanban': ('Kanban Crossdock Master (former Part List) has a period like the Export Crossdock Master: TB_M_PART_CANDIDATE is kept per PART_NO + PERIOD '
               '(Status, Pcs/Case, Max Case/Day, Sync Status of that month).'),
    'order': ("Order Type per destination row (system master '**', 'C', '9', 'V'): the same destination may have two rows in a period when the order "
              'type differs; key PART_NO + PERIOD + DEST_CODE + ORDER_TYPE.'),
    'down': ('Max Case/Day of a period may not be below the mapped total of that period (message 14): to lower it, D/S first reduces the destinations '
             'on the Export Crossdock Master, then changes Max Case/Day on the Kanban Crossdock Master.'),
}


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return False
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'
    return True


def tables(s):
    for t in s.get('tables', []):
        names = [c[0] for c in t['columns']]
        if t['name'] == 'TB_M_PART_CANDIDATE' and 'PERIOD' not in names:
            t['columns'].insert(1, list(PERIOD_COL))
            t['description'] = 'Kanban Crossdock Master: one record per part and calculation period (19-Nov; before: one record per part).'
        if t['name'] == 'TB_M_PART_CANDIDATE_DEST' and 'ORDER_TYPE' not in names:
            t['columns'].insert(names.index('DEST_CODE') + 1, list(OT_COL))
            t['description'] = 'Export Crossdock Master: one record per part, calculation period, destination and order type.'
        if t['name'] == 'TB_R_CROSSDOCK_IF_RESULT':
            for c in t['columns']:
                if c[0] == 'PERIOD':
                    c[2] = 'Y'
                    c[4] = 'Calculation period of the data sent (YYYYMM); part of the key: one row per part, target and period (19-Nov)'
                if c[0] == 'IF_STATUS':
                    c[4] = "'0' No Sync / '3' Waiting / '1' Success / '2' Failed (per period, 19-Nov)"
        if t['name'] == 'TB_R_PART_DAD_RESULT':
            for c in t['columns']:
                if c[0] == 'PERIOD':
                    c[4] = 'Period of the result = the new (Next) period, month after the run month (19-Nov)'


def section(s, key, title, items, table=None):
    blk = [{'type': 'heading', 'text': title}, {'type': 'bullets', 'marker': '-', 'level': 0, 'items': items}]
    if table:
        blk.append(table)
    s[key] = s.get(key, []) + blk


def tab(cols, rows):
    return {'type': 'table', 'level': 0, 'columns': [{'title': c, 'width': w} for c, w in cols], 'rows': rows}


# ---------- every spec: names and tables ----------
for f in sorted(glob.glob('XD*_spec.json')):
    t = open(f).read()
    n = t
    for a, b in NAMES:
        n = n.replace(a, b)
    s = json.loads(n)
    tables(s)
    fid = f[:4]
    if fid == 'XD01' and rev(s, '0.5', 'Names Kanban / Export Crossdock Master; period on the Kanban Crossdock Master; Order Type per destination row; '
                                       'Max Case/Day down: destinations first (19-Nov).'):
        h = sum(1 for x in s['operation'] if x.get('type') == 'heading' and x['text'][:2] == '5.')
        section(s, 'operation', f'5.{h + 1} Period, Order Type and names (19-Nov)', [
            'Names: sub-menu Part List = Kanban Crossdock Master (Procurement), sub-menu Mapping per Destination = Export Crossdock Master (D/S). '
            'Page title Crossdock Master. Export Excel: Crossdock_Kanban_Master_YYYYMMDD.xlsx (sheet Kanban Crossdock Master) and '
            'Crossdock_Export_Master_<Period>_YYYYMMDD.xlsx (sheet Export Crossdock Master).',
            RULES['kanban'],
            'Kanban Crossdock Master screen: new search criterion Calculation period (All periods / periods, default the ongoing period) and new first column '
            'Period. Rows of a past period: Part Number and [Edit] not available, [History] available. Add Part: into the ongoing period.',
            RULES['periods'],
            RULES['order'] + ' Export Crossdock Master: new column Order Type (combobox of the system master) after Destination (CD); Save is blocked '
            'when a destination + order type is used twice ("The same destination is used twice with the same order type").',
            'Export Excel / Upload of the Export Crossdock Master: new column Order Type after Destination Code (sheet 1 and sheet Upload).',
            RULES['down'],
            '[Sync] and Sync Status are per part and period (TB_R_CROSSDOCK_IF_RESULT key PART_NO + TARGET_SYSTEM + PERIOD): XD07 sends the Current '
            'period first, then the Next period; XD06 uses the Current period only.'],
            tab([('Period', 14), ('Kanban Crossdock Master', 22), ('Export Crossdock Master', 22)], [
                ['Past', 'View only', 'View only'], ['Current (M)', 'Edit / Add Part / upload', 'Edit / upload'],
                ['Next (M+1)', 'View only (made by XD05)', 'View only (made by XD05)']]))
    elif fid == 'XD02' and rev(s, '0.4', 'Kanban Crossdock Master per period: the upload changes the ongoing period only (19-Nov).'):
        section(s, 'func_desc', '4.4 Period (19-Nov)', [RULES['kanban'], 'The upload changes the rows of the ongoing period only; Next (made by XD05) and '
                                                         'past periods are not changed.', RULES['down']])
    elif fid == 'XD03' and rev(s, '0.3', 'Column Order Type in the template; key part + destination + order type; ongoing period only (19-Nov).'):
        section(s, 'func_desc', '4.4 Order Type and Period (19-Nov)', [
            RULES['order'], "Template: new column Order Type after Destination Code (mandatory, '**', 'C', '9' or 'V'). A destination + order type "
                            'twice for a part in the file = row error (message of the duplicate check).',
            'The upload changes the ongoing period only; Next (made by XD05) and past periods are not changed.'])
    elif fid == 'XD05' and rev(s, '0.4', 'Runs on day D and makes the Next period (Kanban and Export Crossdock Master); process 3 Period Rollover on day 1 (19-Nov).'):
        section(s, 'func_desc', '4.9 Next Period and Period Rollover (19-Nov)', [
            'Schedule: day D of every month (system master, before the end of the month). The new period = the month after the run month '
            '(e.g. run 27-Nov -> period 202612 = Next).',
            'Process 1: TB_R_PART_DAD_RESULT for the Next period, and one Kanban Crossdock Master row per part for the Next period: PART_STATUS from the '
            'result, Pcs/Case and Max Case/Day copied from the Current period. The Current period is not changed.',
            "Process 2: Export Crossdock Master rows of the Next period for the Active parts (Order Type '**'). The Next period is view only on the screen.",
            'Process 3 (new, day 1, 00:10): Period Rollover: Next becomes Current, Current becomes Past. Parts whose part + destination combination differs '
            'from the previous period get GTOPAS No Sync, then XD06 starts automatically. AP POLE got the Next period already on day D (XD07).',
            'The manual [Run calculation] of the screen re-runs the Next period.'],
            tab([('When', 14), ('What', 40)], [['Day D (e.g. 27-Nov)', 'Process 1 + 2: period 202612 (Next) made'],
                                              ['Day D - end of month', 'D/S adjusts the Current period only'],
                                              ['Day 1 (1-Dec)', 'Process 3: 202612 Current, 202611 Past; XD06 for the changed combinations']]))
    elif fid == 'XD06' and rev(s, '0.7', 'GTOPAS = Current period; automatic run after the Period Rollover; several order types of a destination = one GTOPAS row (19-Nov).'):
        section(s, 'func_desc', '4.6 Period and Order Type (19-Nov)', [
            'GTOPAS has no period: the bot always compares with the Current period of the Export Crossdock Master. The Next period (made on day D) reaches '
            'GTOPAS only on day 1, after the Period Rollover (XD05 process 3), which starts XD06 automatically.',
            'Order Type: GTOPAS keeps one row per P/No. + Destination Code. A destination mapped with two order types in NSP is one GTOPAS row (Keep / Add once).',
            'Pcs/Case, Max Case/Day and Case/Day are not sent (no change for GTOPAS).'])
    elif fid == 'XD07' and rev(s, '0.7', 'Effective Month / Year = period (MM, YYYY); Current then Next; Order Type of the row; order of the screens when '
                                       'Max Case/Day goes down (19-Nov).'):
        section(s, 'func_desc', '4.8 Period, Order Type and Order of the Screens (19-Nov)', [
            'Effective Month / Year of WLM9Q890 and WLM9Q860 = the period of the NSP data: MM and YYYY (e.g. 202612 -> 12 / 2026).',
            'One [Sync] sends the Current period first, then the Next period. The Next period is sent on day D after XD05; on day 1 nothing new is sent.',
            "Order Type of a Buyer PD row = ORDER_TYPE of the Export Crossdock Master row ('**', 'C', '9', 'V'); key in AP POLE: Buyer PD + Order Type.",
            'Max Case/Day of the period goes down: 1. WLM9Q860 Delete / Edit the Buyer PD rows (Total Shipping Allocated <= new max), 2. WLM9Q890 Edit Max '
            'Shipping Box Qty. Goes up or stays: 1. WLM9Q890 Add / Edit the part, 2. WLM9Q860 Delete, Edit, then Add.',
            'Simulation: deliverables/function_list_v2/simulation/XD07_Simulation_AP_POLE_Period.xlsx.'])
    if s != json.loads(t):
        with open(f, 'w') as fh:
            json.dump(s, fh, indent=1, ensure_ascii=False)
        print('patched', fid)
