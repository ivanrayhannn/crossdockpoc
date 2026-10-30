"""30-Oct (3): a part that became Inactive is also deleted in AP POLE, at part level, still by the SFTP interface file:
it is sent with CROSSDOCK_FLAG 'N' and the receive IF of the TMA deletes the part in Cross Dock Kanban Part Master
(same as [Delete] on AP POLE screen WLM9Q890)."""
import json

SCREEN = 'Cross Dock Kanban Part Master (same as [Delete] on AP POLE screen WLM9Q890)'


def load(fid):
    with open(f'{fid}_spec.json') as f:
        return json.load(f)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)


def replace_text(o, old, new):
    if isinstance(o, dict):
        return {k: replace_text(v, old, new) for k, v in o.items()}
    if isinstance(o, list):
        return [replace_text(v, old, new) for v in o]
    return o.replace(old, new) if isinstance(o, str) else o


# ---------- XD07
s = load('XD07')
g = s['general']
g['objective'][0] = g['objective'][0].replace(
    'Parts that became Inactive are not sent: AP POLE is not changed for them (decided 30-Oct).',
    f"Parts that became Inactive are sent with CROSSDOCK_FLAG 'N' (one record, no destination): AP POLE deletes the part at part "
    f"level in {SCREEN} (decided 30-Oct).")
for o in g['outputs']:
    if o['type'] == 'System':
        o['description'] = "Inserted / updated by the receive IF of the TMA; the part is deleted when CROSSDOCK_FLAG 'N' (not in NSP scope)"
for t in g['extra_tables']:
    for r in t['rows']:
        if r[0] == 'PART_NO' and t['title'] != 'Parameters':
            r[-1] = 'Cross dock part with Sync Status Waiting: Active parts, and parts that became Inactive since the last send'
        if r[0] == 'CROSSDOCK_FLAG':
            r[-1] = (f"'Y' = Active / 'N' = Inactive: the receive IF deletes the part in {SCREEN}, which has one row per part number; "
                     "only PART_NO, CROSSDOCK_FLAG, SEND_ID and SEND_DT are filled (decided 30-Oct)")
st = s['func_flow']['steps']
st[1] = {'text': "Select the parts with TARGET_SYSTEM = 'APPOLE' and IF_STATUS = '3' in TB_R_CROSSDOCK_IF_RESULT. Keep CHANGED_DT of each part.",
         'children': ["PART_STATUS Active: sent with its destinations (CROSSDOCK_FLAG 'Y').",
                      "PART_STATUS Inactive: sent with CROSSDOCK_FLAG 'N' so AP POLE deletes the part.",
                      'No part: write LOG2 and exit.']}
if isinstance(st[2], dict) and not any("'N'" in c for c in st[2]['children']):
    st[2]['children'].insert(2, "Inactive part: one record with PART_NO and CROSSDOCK_FLAG 'N'; the other fields of the part and destination are blank.")
for b in s['data_map']['blocks']:
    for m in b['mappings']:
        if m.get('dest_field') == 'CROSSDOCK_FLAG':
            m['description'] = "'Y' Active / 'N' Inactive (AP POLE deletes the part; other fields blank)"
    if b['destination'].get('table') == 'TB_R_CROSSDOCK_IF_RESULT':
        for m in b['mappings']:
            m['description'] = {'IF_STATUS': "'1' transfer OK / '2' file or transfer error",
                                'IF_MESSAGE': "Error when '2'; blank when '1'"}.get(m['dest_field'], m['description'])
s = replace_text(s, "Parts that became Inactive (XD05 process 1) are not sent to AP POLE (decided 30-Oct): their 'APPOLE' row is set to '1' "
                    "(IF_MESSAGE 'Inactive part: AP POLE not changed'); GTOPAS deletes all their rows (XD06).",
                 "Parts that became Inactive (XD05 process 1) are sent with CROSSDOCK_FLAG 'N' and without destinations: the receive IF of the "
                 f"TMA deletes the part (one row per part number) in {SCREEN} (decided 30-Oct). GTOPAS deletes all their rows too (XD06, RPA).")
s = replace_text(s, 'only Active parts are sent, Candidate and Inactive parts are not.',
                 'Active parts and parts that became Inactive are sent; Candidate parts are not.')
for b in s['func_desc']:
    if b.get('type') == 'bullets':
        b['items'] = [x for x in b['items'] if not x.startswith("Receive IF of the TMA for CROSSDOCK_FLAG 'N'")]
save('XD07', s)

# ---------- references
for fid, pairs in (('XD06', [('AP POLE is not changed for them (XD07).', "In AP POLE they are deleted at part level by XD07 (SFTP file, CROSSDOCK_FLAG 'N').")]),
                   ('XD05', [('deletes all its rows in GTOPAS (XD06); AP POLE is not changed for it (decided 30-Oct).',
                              'deletes it in GTOPAS (XD06, RPA, all rows) and in AP POLE (XD07, SFTP file, part level) (decided 30-Oct).')]),
                   ('XD01', [('Inactive parts: all their rows are deleted in GTOPAS (XD06); AP POLE is not changed for them.',
                              'Inactive parts: all their rows are deleted in GTOPAS (XD06) and AP POLE (XD07).'),
                             ('with Case/Day of the ongoing period as one complete set.',
                              'with Case/Day of the ongoing period as one complete set (Inactive: part deleted).')])):
    s = load(fid)
    for old, new in pairs:
        s = replace_text(s, old, new)
    save(fid, s)
