"""19-Nov: notification email of the RPA (Power Automate) for XD06 (GTOPAS) and XD07 (AP POLE): when it is sent, to whom, subject,
body, attachment and retry. The cloud flow sends it with the Office 365 Outlook connector at the end of every run. Independent of the open
decision on the response to NSP (Waiting -> Success / Failed, or Sent + email). Runs after apply_1811b."""
import json

FLOW = {'XD06': ('GTOPAS', 'XD06_RPA_GTOPAS', 'registered / kept / deleted rows per P/No. + Destination Code', 'GTOPAS Compare'),
        'XD07': ('AP POLE', 'XD07_RPA_APPOLE', 'part added / edited / deleted, Buyer-PD added / edited / deleted', 'AP POLE Compare')}


def section(fid):
    tgt, bid, counts, sheet = FLOW[fid]
    when = {'type': 'table', 'level': 0,
            'columns': [{'title': 'No', 'width': 4}, {'title': 'Case', 'width': 16}, {'title': 'When the email is sent', 'width': 26},
                        {'title': 'Subject result', 'width': 10}],
            'rows': [['E1', 'Run without error', 'End of the run, after the last part', 'SUCCESS'],
                     ['E2', 'Run stopped by an error (try-catch)', 'After the automatic retries of the cloud flow are used up (retry count and '
                                                               'interval in the flow settings, proposal 2 times, 10 minutes)', 'FAILED'],
                     ['E3', 'Bot could not start (machine offline, login of NSP / ' + tgt + ' failed, desktop flow time out)',
                      'Cloud flow branch "run after = failed / timed out" of the desktop flow action', 'FAILED'],
                     ['-', 'Nothing to process (no part Waiting)', 'No email', '-']]}
    tmpl = {'type': 'table', 'level': 0,
            'columns': [{'title': 'Item', 'width': 12}, {'title': 'Content', 'width': 44}],
            'rows': [['Sender', 'Shared mailbox of the RPA (Office 365 Outlook connector "Send an email (V2)"), TBC'],
                     ['To', 'User who clicked [Sync] (e-mail sent by NSP in the request of the flow) + D/S team mailing list'],
                     ['Cc', 'RPA PIC; for FAILED also the NSP PIC'],
                     ['Subject', '[Crossdock Sync][' + tgt + '][SUCCESS | FAILED] Run <RUN_ID> - <n> part(s)'],
                     ['Body 1. Run', 'RUN_ID, target ' + tgt + ', started / ended, [Sync] by <user> at <date-time>, period(s) sent'],
                     ['Body 2. Summary', 'Parts processed; ' + counts],
                     ['Body 3. Error (FAILED)', 'Step, part, destination and message of the error (LOG4 / LOG5); parts not processed'],
                     ['Body 4. Action', 'SUCCESS: no action. FAILED: click [Sync] again on Crossdock Master Setting; contact the RPA PIC when it '
                                        'fails again'],
                     ['Body 5. Links', 'Folder of the RPA work file (SharePoint / OneDrive, TBC); link to the run in Power Automate (for the RPA PIC)'],
                     ['Attachment', 'The downloaded Excel with the work sheet ' + sheet + ' (action, result and message per row). Above the mail '
                                    'size limit: link only'],
                     ['Language', 'English']]}
    return [{'type': 'heading', 'text': 'Notification Email (Power Automate, 19-Nov)'},
            {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                'The cloud flow of the RPA sends one email per run of ' + fid + ' (' + tgt + '), so the user knows the result without opening NSP.',
                'One email per target: XD06 (GTOPAS) and XD07 (AP POLE) run as separate bots, so a [Sync] gives two emails.',
                'One email per run: the retries of the same run do not send an email; only the final result does.']},
            when, tmpl,
            {'type': 'bullets', 'marker': '-', 'level': 0, 'items': [
                'Example subject: [Crossdock Sync][' + tgt + '][FAILED] Run 20261127103000 - 12 part(s).',
                'Recipients (mailing list, RPA PIC, NSP PIC) are set in the flow settings, not in the code of the bot.',
                'LOG6 is written when the email is sent; when sending fails, the run result stays and the RPA PIC sees it in the Power Automate run history.']}]


for fid, (tgt, bid, _, _) in FLOW.items():
    with open(f'{fid}_spec.json') as fh:
        s = json.load(fh)
    if any(r['revision'] == '0.6' for r in s['revisions']):
        continue
    fd = s['func_desc']
    h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and 'Open Points' in x['text'])
    no = fd[h]['text'].split(' ')[0]                      # e.g. 4.4
    major, minor = no.split('.')
    sec = section(fid)
    sec[0]['text'] = f'{no} ' + sec[0]['text']
    fd[h]['text'] = f'{major}.{int(minor) + 1} Open Points'
    fd[h:h] = sec
    s['logging_messages'].append({'event': 'Notification email', 'cause': 'End of the run (SUCCESS / FAILED)', 'type': 'Info', 'msg_id': 'LOG6',
                                  'message': f'Notification email <SUCCESS / FAILED> of run <RUN_ID> sent to <recipients>.',
                                  'action': {'system': 'Write the log.', 'user': 'Read the email; FAILED: click [Sync] again.'}})
    s['revisions'].append({'revision': '0.6', 'author': 'FID Rayhan', 'date': '19-Nov-26', 'reviewed_by': '',
                           'description': f'Notification email of the RPA (Power Automate): cases SUCCESS / FAILED / bot not started, recipients, '
                                          f'subject, body, attachment, retry ({no}); LOG6.'})
    if fid == 'XD07':   # leftover of the SFTP version
        s = json.loads(json.dumps(s, ensure_ascii=False).replace("'1' transfer OK / '2' file or transfer error",
                                                                 "'1' run without error / '2' run stopped by an error (try-catch, all parts)"))
    s['header']['updated_date'] = '19-Nov-26'
    with open(f'{fid}_spec.json', 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', fid)
