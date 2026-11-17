"""17-Nov: list of the parts that went Active -> Inactive after their last successful sync (source for the RPA XD06 / XD07).
- TB_R_CROSSDOCK_IF_RESULT gets LAST_SYNC_DT (last Success per part and target, kept when a later run fails).
- XD06 / XD07: which parts are deleted, and LAST_SYNC_DT written on Success.
- XD01 (generated reference only; the hand-tidied XD01 workbook is not rebuilt): column Last Sync and sheet "Active to Inactive" of Export Excel.
- XD05: the Active -> Inactive change is written to TB_H_PART_CANDIDATE with its date (used as Status Changed Date).
Runs after apply_1611 (revisions)."""
import json

COL = ['LAST_SYNC_DT', 'DATETIME', '', 'Y', 'Date-time of the last Success of the part for this target (kept when a later run is Failed); '
       'NULL when never synced. A part is listed in "Active to Inactive" when it went Inactive after this date (17-Nov).']
RULE = ('Active to Inactive (17-Nov): a part whose status went from Active to Inactive (XD05, TB_H_PART_CANDIDATE OLD_STATUS Active, '
        'NEW_STATUS Inactive) after LAST_SYNC_DT of TB_R_CROSSDOCK_IF_RESULT is still Active in the target system: the RPA deletes its part + '
        'destination rows there. A part never synced (LAST_SYNC_DT NULL) is not listed. The list is also sheet "Active to Inactive" of the '
        'Mapping per Destination Export Excel (XD01).')


def load(fid):
    with open(f'{fid}_spec.json') as fh:
        return json.load(fh)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('patched', fid)


for fid in ('XD01', 'XD06', 'XD07'):
    s = load(fid)
    for t in s['tables']:
        if t['name'] == 'TB_R_CROSSDOCK_IF_RESULT' and not any(c[0] == 'LAST_SYNC_DT' for c in t['columns']):
            k = next(i for i, c in enumerate(t['columns']) if c[0] == 'IF_DT') + 1
            t['columns'].insert(k, COL)
    if fid in ('XD06', 'XD07'):
        fd = s['func_desc']
        h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.4'))
        fd[h:h] = [{'type': 'heading', 'text': '4.3a Active to Inactive since the last sync (17-Nov)'},
                   {'type': 'bullets', 'items': [
                       RULE,
                       'Source query: TB_M_PART_CANDIDATE (STATUS Inactive) + TB_H_PART_CANDIDATE (latest change Active -> Inactive, its CREATED_DT = '
                       'Status Changed Date) + TB_R_CROSSDOCK_IF_RESULT (TARGET_SYSTEM of this function, LAST_SYNC_DT); listed when Status Changed Date > LAST_SYNC_DT.',
                       'On Success of the run: IF_STATUS 1, IF_DT and LAST_SYNC_DT = date-time of the result, for every part sent and every part deleted. '
                       'On Failed: IF_STATUS 2 and IF_DT only; LAST_SYNC_DT is not changed, so the part stays in the list for the next run.']}]
    if fid == 'XD01':
        s.setdefault('general', {})
        txt = json.dumps(s, ensure_ascii=False)
        s['operation'] = s.get('operation', [])
        s['operation'].append({'type': 'heading', 'text': 'Last Sync and Active to Inactive (17-Nov)'})
        s['operation'].append({'type': 'bullets', 'items': [
            'Mapping per Destination: new column Last Sync after Sync Status = LAST_SYNC_DT of TB_R_CROSSDOCK_IF_RESULT (latest of GTOPAS / AP POLE); '
            '"Never" when the part was never synced.',
            'Export Excel of Mapping per Destination: sheet 1 gets column Last Sync Date; new sheet 3 "Active to Inactive" (Part Number, Part Name, '
            'Destination Code, Status Before, Status Now, Status Changed Date, Last Sync Date, Action "Delete in GTOPAS / AP POLE"), one row per '
            'destination, every part of the master whatever the filter. ' + RULE,
            'Export Excel of Part List: new column Sync Status after Status (No Sync / Waiting / Success / Failed): the RPA to AP POLE (XD07) takes '
            'the parts that are not synced yet from it.']})
    save(fid, s)

s = load('XD05')
fd = s['func_desc']
h = next(i for i, x in enumerate(fd) if x.get('type') == 'heading' and x['text'].startswith('4.3'))
fd[h + 1].setdefault('items', []).append('Every status change is written to TB_H_PART_CANDIDATE (OLD_STATUS / NEW_STATUS, CREATED_DT = run date-time). '
                                         'Active -> Inactive is read by XD06 / XD07 and the Export Excel of XD01 (sheet "Active to Inactive", 17-Nov).')
save('XD05', s)
