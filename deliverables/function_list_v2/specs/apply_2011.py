"""20-Nov: no response from the RPA to NSP (option C). NSP only knows that a part was sent: Sync Status No Sync / Sent. The result of
XD06 / XD07 reaches the user by the notification e-mail of Power Automate (4.x of XD06 / XD07); a failed run is sent again with
[Re-send last Sync]. Runs after apply_1911b."""
import glob
import json

D = '20-Nov-26'
SENT_RULE = ('No response from the RPA (20-Nov): NSP does not receive the result of XD06 / XD07. [Sync] sets the parts to Sent '
             "(SYNC_STATUS '3', IF_STATUS '3', IF_DT and LAST_SYNC_DT = send time); Success / Failed are not kept in NSP. The result comes by the "
             'notification e-mail of Power Automate (SUCCESS / FAILED with the work file). When the e-mail says FAILED, D/S clicks [Re-send last Sync].')


def rev(s, no, text):
    if any(r['revision'] == no for r in s['revisions']):
        return False
    s['revisions'].append({'revision': no, 'author': 'FID Rayhan', 'date': D, 'reviewed_by': '', 'description': text})
    s['header']['updated_date'] = D
    s['header']['updated_by'] = 'FID Rayhan'
    return True


def columns(s):
    for t in s.get('tables', []):
        for c in t['columns']:
            if t['name'] == 'TB_R_CROSSDOCK_IF_RESULT':
                if c[0] == 'IF_STATUS':
                    c[4] = "'0' No Sync / '3' Sent (20-Nov: no response from the RPA; the result comes by e-mail)"
                if c[0] == 'IF_DT':
                    c[4] = 'Date-time of the send to the RPA ([Sync] / [Re-send last Sync] / Period Rollover)'
                if c[0] == 'LAST_SYNC_DT':
                    c[4] = 'Date-time of the last send of the part for this target; shown as Last Sent on XD01 (20-Nov)'
                if c[0] == 'IF_FILE_NAME':
                    c[4] = 'Run ID of the send (YYYYMMDDHHMMSS); [Re-send last Sync] sends the parts of the last run ID again'
                if c[0] == 'IF_MESSAGE':
                    c[4] = 'Not used (20-Nov: no response from the RPA)'
            if t['name'] == 'TB_M_PART_CANDIDATE':
                if c[0] == 'SYNC_STATUS':
                    c[4] = "0 = No Sync, 3 = Sent (20-Nov: 1 Success / 2 Failed not used, no response from the RPA)"
                if c[0] == 'SYNC_DT':
                    c[4] = 'Date-time of the last send'
                if c[0] == 'SYNC_MESSAGE':
                    c[4] = 'Not used (20-Nov)'


for f in sorted(glob.glob('XD*_spec.json')):
    s = json.load(open(f))
    before = json.dumps(s, ensure_ascii=False)
    columns(s)
    fid = f[:4]
    if fid == 'XD01' and rev(s, '0.6', 'Sync without response from the RPA: Sync Status No Sync / Sent, column Last Sent, button [Re-send last Sync] (20-Nov).'):
        h = sum(1 for x in s['operation'] if x.get('type') == 'heading' and x['text'][:2] == '5.')
        s['operation'] += [
            {'type': 'heading', 'text': f'5.{h + 1} Sync without response from the RPA (20-Nov)'},
            {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                SENT_RULE,
                'Sync Status: No Sync (0, grey) / Sent (3). Search criterion Sync Status: All / No Sync / Sent. Column Last Sync is renamed Last Sent '
                '(LAST_SYNC_DT = time of the last send); Export Excel column Last Sent Date.',
                '[Sync (n)]: n = parts with status Active (ongoing / Next period) or Inactive and Sync Status No Sync. They become Sent; the run ID is '
                'kept in IF_FILE_NAME.',
                'New button [Re-send last Sync (n)] next to [Sync]: sends the n parts of the last run ID again (same rows, new send time). Disabled when '
                'there is no run yet. Used when the e-mail of the RPA says FAILED.',
                'Export Excel of the Kanban Crossdock Master: new column Last Sent Date after Sync Status (the bot of XD07 takes the parts of its run '
                'with it).',
                'A part changed after it was sent goes back to No Sync (Sync Status rule).']}]
    elif fid in ('XD06', 'XD07') and rev(s, '0.8', 'No response to NSP: the bot does not write TB_R_CROSSDOCK_IF_RESULT / TB_M_PART_CANDIDATE / '
                                                    'TB_H_PART_CANDIDATE; the result is the notification e-mail; [Re-send last Sync] (20-Nov).'):
        fd = s['func_desc']
        h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and 'Open Points' in x['text'])
        no = fd[h]['text'].split(' ')[0]
        major, minor = no.split('.')
        fd[h]['text'] = f'{major}.{int(minor) + 1} Open Points'
        fd[h:h] = [{'type': 'heading', 'text': f'{no} Result without response to NSP (20-Nov)'},
                   {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                       SENT_RULE,
                       'The bot writes nothing back to NSP: the steps "set the result in TB_R_CROSSDOCK_IF_RESULT", "overall Sync Status" and '
                       '"history SYNC" of the function flow and the data edit mapping of these tables are not used. NSP writes them when it '
                       'sends ([Sync] on XD01 or the Period Rollover of XD05).',
                       'Try-catch: an error stops the run and the e-mail is FAILED (E2 / E3). Rows already changed on the target screen stay; '
                       '[Re-send last Sync] compares again and completes them.',
                       'Parts of the run: NSP passes the send time (run ID) when it starts the flow; the bot takes the rows with Sync Status Sent and '
                       'Last Sent Date = that send time from the downloaded Export Excel (parts sent earlier are not processed again).',
                       'Evidence of a run: the e-mail and the work file (sheet Compare) with action, result and message per row.']}]
    if json.dumps(s, ensure_ascii=False) != before:
        with open(f, 'w') as fh:
            json.dump(s, fh, indent=1, ensure_ascii=False)
        print('patched', fid)
