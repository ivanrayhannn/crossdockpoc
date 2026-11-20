"""20-Nov (2): TB_R_CROSSDOCK_IF_RESULT removed (user). Without a response from the RPA it only repeated the Sync Status of the
Kanban Crossdock Master. The send time per target stays on TB_M_PART_CANDIDATE (per part + period): GTOPAS_SYNC_DT, APPOLE_SYNC_DT,
SYNC_RUN_ID; one Log record per run (run ID, target, send time, number of parts). TB_H_PART_CANDIDATE: SYNC history written by NSP when
it sends, PERIOD filled for every event, new column ORDER_TYPE. Runs after apply_2011."""
import glob
import json

D = '20-Nov-26'
NEW_COLS = [
    ['GTOPAS_SYNC_DT', 'DATETIME', '', 'Y', 'Date-time of the last send of the part (this period) to GTOPAS: [Sync], [Re-send last Sync] or the '
                                            'Period Rollover (XD05 process 3); shown as Last Sent GTOPAS'],
    ['APPOLE_SYNC_DT', 'DATETIME', '', 'Y', 'Date-time of the last send of the part (this period) to AP POLE: [Sync] or [Re-send last Sync]; '
                                            'shown as Last Sent AP POLE. XD07 takes the parts whose APPOLE_SYNC_DT = send time of its run'],
    ['SYNC_RUN_ID', 'VARCHAR(20)', '', 'Y', 'Run ID (YYYYMMDDHHMMSS) of the last send; [Re-send last Sync] sends the rows of the last run ID again'],
]
H_OT = ['ORDER_TYPE', 'VARCHAR(2)', '', 'Y', 'Order Type of the destination row for MAPPING (with DEST_CODE); NULL for other events (20-Nov)']
RUN_LOG = ('Log (existing table, one record per send run, 20-Nov): BATCH_ID XD06_RPA_GTOPAS / XD07_RPA_APPOLE, RUN_ID, send time, sent by (user '
           'of [Sync] / [Re-send last Sync] or the Period Rollover), number of parts, period(s). [Re-send last Sync] repeats the targets of the last run.')
TEXT = [('TB_R_CROSSDOCK_IF_RESULT', 'TB_M_PART_CANDIDATE'), ('LAST_SYNC_DT', 'GTOPAS_SYNC_DT / APPOLE_SYNC_DT'),
        ('IF_FILE_NAME', 'SYNC_RUN_ID'), ('IF_STATUS', 'SYNC_STATUS'), ('IF_MESSAGE', 'e-mail message'), ('IF_DT', 'send time'),
        ('SYNC_MESSAGE', 'e-mail message')]


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return False
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'
    return True


for f in sorted(glob.glob('XD*_spec.json')):
    s = json.load(open(f))
    before = json.dumps(s, ensure_ascii=False)
    fid = f[:4]
    had = 'TB_R_CROSSDOCK_IF_RESULT' in before
    # tables
    s['tables'] = [t for t in s.get('tables', []) if t['name'] != 'TB_R_CROSSDOCK_IF_RESULT']
    for t in s['tables']:
        names = [c[0] for c in t['columns']]
        if t['name'] == 'TB_M_PART_CANDIDATE' and 'GTOPAS_SYNC_DT' not in names:
            t['columns'] = [c for c in t['columns'] if c[0] not in ('SYNC_DT', 'SYNC_MESSAGE')]
            k = [c[0] for c in t['columns']].index('SYNC_STATUS') + 1
            t['columns'][k:k] = [list(c) for c in NEW_COLS]
        if t['name'] == 'TB_H_PART_CANDIDATE':
            for c in t['columns']:
                if c[0] == 'PERIOD':
                    c[3] = 'N'
                    c[4] = 'Calculation period YYYYMM of the changed row (every event; Kanban and Export Crossdock Master are per period, 20-Nov)'
                if c[0] == 'SOURCE':
                    c[4] = 'SCREEN / UPLOAD / BATCH (SYNC: SCREEN for [Sync] / [Re-send last Sync], BATCH for the Period Rollover)'
                if c[0] == 'REMARK':
                    c[4] = "Free text; SYNC: target(s) + run ID, e.g. 'GTOPAS, APPOLE: 20261127100000'"
            if 'ORDER_TYPE' not in names:
                k = names.index('DEST_CODE') + 1
                t['columns'].insert(k, list(H_OT))
    # data maps, inputs and outputs of the removed table
    if isinstance(s.get('data_map'), dict):
        s['data_map']['blocks'] = [b for b in s['data_map']['blocks'] if 'TB_R_CROSSDOCK_IF_RESULT' not in json.dumps(b.get('destination', ''))]
    for k in ('inputs', 'outputs'):
        if k in s.get('general', {}):
            s['general'][k] = [i for i in s['general'][k] if i['name'] != 'TB_R_CROSSDOCK_IF_RESULT']
    # remaining text
    t = json.dumps(s, ensure_ascii=False)
    for a, b in TEXT:
        t = t.replace(a, b)
    s = json.loads(t)
    if fid == 'XD01' and rev(s, '0.7', 'TB_R_CROSSDOCK_IF_RESULT removed: send time per target on TB_M_PART_CANDIDATE (GTOPAS_SYNC_DT, APPOLE_SYNC_DT, '
                                       'SYNC_RUN_ID); columns Last Sent GTOPAS / AP POLE; Log per run; history SYNC by NSP (20-Nov).'):
        h = sum(1 for x in s['operation'] if x.get('type') == 'heading' and x['text'][:2] == '5.')
        s['operation'] += [
            {'type': 'heading', 'text': f'5.{h + 1} Send data without TB_R_CROSSDOCK_IF_RESULT (20-Nov)'},
            {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                '[Sync] / [Re-send last Sync] update TB_M_PART_CANDIDATE of every part sent (row of the period sent): SYNC_STATUS = 3 (Sent), '
                'GTOPAS_SYNC_DT and APPOLE_SYNC_DT = send time (the targets of the run), SYNC_RUN_ID = run ID, CHANGED_BY / CHANGED_DT.',
                'Insert TB_H_PART_CANDIDATE per part sent: EVENT_TYPE SYNC, SOURCE SCREEN, FIELD_NAME SYNC_STATUS, OLD_VALUE No Sync, NEW_VALUE Sent, '
                'REMARK = targets + run ID.',
                RUN_LOG,
                'Export Crossdock Master: columns Last Sent GTOPAS and Last Sent AP POLE (instead of Last Sent); Export Excel of both sub-menus: '
                'Last Sent GTOPAS and Last Sent AP POLE.',
                'Example period Next 202612: APPOLE_SYNC_DT is filled on day D by [Sync]; GTOPAS_SYNC_DT on day 1 by the Period Rollover.',
                'History: PERIOD is filled for every event (ADD / EDIT with the period of the row); MAPPING rows also keep ORDER_TYPE.']}]
    elif fid == 'XD05' and rev(s, '0.5', 'Period Rollover writes GTOPAS_SYNC_DT, SYNC_RUN_ID, history SYNC and the run Log (TB_R_CROSSDOCK_IF_RESULT removed, 20-Nov).'):
        s['func_desc'] += [
            {'type': 'heading', 'text': '4.10 Period Rollover: send data (20-Nov)'},
            {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                'For each part whose part + destination combination of the new Current period differs from the previous period: TB_M_PART_CANDIDATE '
                '(new Current row) SYNC_STATUS = 3 (Sent), GTOPAS_SYNC_DT = rollover time, SYNC_RUN_ID = run ID; TB_H_PART_CANDIDATE SYNC '
                '(SOURCE BATCH, REMARK GTOPAS + run ID); then XD06 starts.',
                RUN_LOG,
                'History of process 1 / 2: PERIOD = Next period; MAPPING rows keep ORDER_TYPE.']}]
    elif fid in ('XD06', 'XD07') and rev(s, '0.9', 'TB_R_CROSSDOCK_IF_RESULT removed; the parts of the run come from the send time on TB_M_PART_CANDIDATE '
                                                    '(GTOPAS_SYNC_DT / APPOLE_SYNC_DT) and SYNC_RUN_ID (20-Nov).'):
        col = 'GTOPAS_SYNC_DT' if fid == 'XD06' else 'APPOLE_SYNC_DT'
        fd = s['func_desc']
        h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and 'Open Points' in x['text'])
        no = fd[h]['text'].split(' ')[0]
        major, minor = no.split('.')
        fd[h]['text'] = f'{major}.{int(minor) + 1} Open Points'
        fd[h:h] = [{'type': 'heading', 'text': f'{no} Parts of the run (20-Nov)'},
                   {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                       f'TB_R_CROSSDOCK_IF_RESULT is removed. NSP writes the send on TB_M_PART_CANDIDATE before the bot starts: SYNC_STATUS 3 Sent, {col} = '
                       'send time, SYNC_RUN_ID = run ID; the bot gets the run ID and the send time when the flow starts.',
                       f'Parts of the run = rows with SYNC_RUN_ID = run ID (in the Export Excel: Last Sent {"GTOPAS" if fid == "XD06" else "AP POLE"} = send time).',
                       'The bot writes nothing to NSP; the result is the notification e-mail. ' + RUN_LOG]}]
    after = json.dumps(s, ensure_ascii=False)
    if after != before:
        with open(f, 'w') as fh:
            json.dump(s, fh, indent=1, ensure_ascii=False)
        print('patched', fid, '(had IF_RESULT)' if had else '')
