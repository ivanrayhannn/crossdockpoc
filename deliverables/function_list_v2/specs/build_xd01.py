"""XD01 Cross Dock Part Master Screen = Part List (X1) + Mapping per Destination (X3) as two tabs of one screen.
The Sync of X3 no longer starts one RPA for the global system: it starts XD06 (GTOPAS) and XD07 (AP POLE)."""
import copy
from build_simple import CALC_POST
from v2lib import (derive, full_update, load, replace_all, set_header, shift_ids, shift_msg_refs, shift_section_refs,
                   map_strings, write)
import re

IFR = 'TB_R_CROSSDOCK_IF_RESULT'
IFR_COLS = [
    ["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part number (TB_M_PART_CANDIDATE)"],
    ["TARGET_SYSTEM", "VARCHAR(10)", "Y", "N", "'GTOPAS' (XD06) / 'APPOLE' (XD07)"],
    ["PERIOD", "CHAR(6)", "", "N", "Calculation period of the mapping sent (YYYYMM)"],
    ["IF_STATUS", "VARCHAR(1)", "", "N", "'3' Waiting / '1' Success / '2' Failed"],
    ["IF_DT", "DATETIME", "", "Y", "Date-time of the result of the target system"],
    ["IF_FILE_NAME", "VARCHAR(100)", "", "Y", "Name of the interface file (AP POLE) or send ID (GTOPAS)"],
    ["IF_MESSAGE", "VARCHAR(500)", "", "Y", "Reason when Failed; blank when Success"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
IFR_TABLE = {"name": IFR, "kind": "transaction", "proposed": True,
             "description": "Dummy table (proposed): send status of the cross dock master per part and target system (XD06 GTOPAS, XD07 AP POLE). "
                            "The real output is the interface data sent to the target (AP POLE: file by SFTP; GTOPAS: existing interface). The overall Sync Status of the part stays in TB_M_PART_CANDIDATE.",
             "columns": IFR_COLS}

SYNC_ROWS_PL = [
    ["Sync Status", "No Sync (0)", "Not sent yet, or changed since the last synchronisation. Set on every Save."],
    ["Sync Status", "Waiting (3)", "[Sync] clicked in the Mapping per Destination tab; waiting for XD06 (GTOPAS) and / or XD07 (AP POLE)."],
    ["Sync Status", "Success (1)", "Both XD06 (GTOPAS) and XD07 (AP POLE) sent Pcs/Case, Max Case/Day and the destination mapping of the ongoing period."],
    ["Sync Status", "Failed (2)", "XD06 or XD07 could not send the part (target and reason in SYNC_MESSAGE); sent again by the next [Sync]."]]


def patch_part_list(s):
    blk = s['data_map']['blocks'][0]['mappings']
    for m in blk:
        if m['dest_field'] in ('SYNC_DT', 'SYNC_MESSAGE'):
            m['description'] = 'NULL (written by XD06 / XD07)'
    s['operation'][30]['rows'][3:7] = SYNC_ROWS_PL
    s['operation'][31]['text'] = ("Only Active parts are synchronised. A Save while the part is Waiting returns it to No Sync, "
                                  "so the result of XD06 / XD07 for the old data is not kept as Success.")
    return s


def patch_mapping(s):
    s['general']['objective'][2] = ("To start the interfaces of the cross dock master to GTOPAS (XD06) and AP POLE (XD07) for changed parts, "
                                    "and show the Sync Status of each part.")
    for b in s['general']['buttons']:
        if b['name'] == 'Sync':
            b['function'] = ("Start XD06 (GTOPAS) and XD07 (AP POLE) for every Active part of the ongoing period with Sync Status No Sync or Failed, "
                             "whatever the filter shows; the parts become Waiting. The label shows the number of parts, e.g. Sync (9).")
    for n in s['screen_flow'][0]['flow']['nodes']:
        if n['id'] == 'tgt':
            n['label'] = 'XD06 -> GTOPAS / XD07 -> AP POLE'
    s['screen_layout'][12]['caption'] = '13. After Sync - the 9 parts are Waiting for XD06 / XD07 (viewed with Sync Status = All)'
    op = s['operation']
    op[18]['items'][1] = ("Set SYNC_STATUS = 3 (Waiting) for these parts in TB_M_PART_CANDIDATE, set one row per part and target system "
                          "(GTOPAS, AP POLE) to IF_STATUS = 3 (Waiting) in TB_R_CROSSDOCK_IF_RESULT, and start XD06 and XD07. Display message no. 10.")
    op[19]['text'] = "Interface functions (one per target system; refer UISS-Batch XD06 and XD07)."
    op[20]['items'] = [
        "XD06 IF Cross Dock Master to GTOPAS and XD07 IF Cross Dock Master to AP POLE each send, per Waiting part, Pcs/Case and Max Case/Day "
        "(TB_M_PART_CANDIDATE) and all destinations with Case/Day of the ongoing period (TB_M_PART_CANDIDATE_DEST) as one complete set.",
        "Each function creates an interface file and sends it by SFTP to its target; the send status is written in the dummy table TB_R_CROSSDOCK_IF_RESULT (IF_STATUS 1 sent / 2 Failed, IF_DT, IF_FILE_NAME, IF_MESSAGE).",
        "Overall SYNC_STATUS of the part: stays 3 (Waiting) while one target is still Waiting; 1 (Success) when both targets are Success; "
        "2 (Failed) when a target failed (SYNC_MESSAGE = target and reason); 0 (No Sync) when the part was changed after it was read.",
        "Every result is recorded in TB_H_PART_CANDIDATE (event SYNC, source IF, REMARK = target and message)."]
    op[21]['text'] = ("A Failed part shows SYNC_MESSAGE (target and reason) as tooltip on its chip (message no. 11) and is sent again to both "
                      "targets by the next [Sync] (replace is repeatable).")
    op[22]['text'] = "Interface method: file by SFTP to GTOPAS (XD06) and AP POLE (XD07); fields and topology refer UISS-Batch XD06 / XD07 (topology TBC)."
    op[30]['rows'][5:8] = [
        ["Sync Status", "Waiting (3)", "[Sync] clicked; waiting for XD06 (GTOPAS) and / or XD07 (AP POLE)."],
        ["Sync Status", "Success (1)", "The part was sent to GTOPAS and AP POLE."],
        ["Sync Status", "Failed (2)", "GTOPAS or AP POLE could not receive the part; target and reason in SYNC_MESSAGE; retried by the next [Sync]."]]
    op[31]['text'] = ("Sync Status is kept per part in TB_M_PART_CANDIDATE because a part is sent as one set (Pcs/Case, Max Case/Day and all destinations); "
                      "the result per target system is in TB_R_CROSSDOCK_IF_RESULT. Every mapping change and every Sync result is recorded in "
                      "TB_H_PART_CANDIDATE (with the period).")
    blocks = s['data_map']['blocks']
    blocks[4]['mappings'][0]['description'] = "'3' (Waiting); XD06 and XD07 are started"
    blocks[4:7] = [blocks[4], {
        "source": {"table": "TB_M_PART_CANDIDATE", "keys": [{"field": "SYNC_STATUS", "value": "'3' (set by this [Sync])"}]},
        "destination": {"table": IFR, "operation": "Insert / Update", "description": "[Sync]: one row per part and target system",
                        "keys": [{"field": "PART_NO + TARGET_SYSTEM", "value": "Each part to synchronise x 'GTOPAS' / 'APPOLE'"}]},
        "mappings": [{"source_field": "PART_NO", "dest_field": "PART_NO"}, {"dest_field": "TARGET_SYSTEM", "description": "'GTOPAS' and 'APPOLE'"},
                     {"dest_field": "PERIOD", "description": "Ongoing calculation period"}, {"dest_field": "IF_STATUS", "description": "'3' (Waiting)"},
                     {"dest_field": "IF_DT", "description": "NULL"}, {"dest_field": "IF_FILE_NAME", "description": "NULL"}, {"dest_field": "IF_MESSAGE", "description": "NULL"},
                     {"dest_field": "CREATED_BY", "description": "Login user ID (insert only)"}, {"dest_field": "CREATED_DT", "description": "Server system date-time (insert only)"},
                     {"dest_field": "CHANGED_BY", "description": "Login user ID"}, {"dest_field": "CHANGED_DT", "description": "Server system date-time"}]}]
    dm = s['display_messages']
    dm[15]['cause'] = 'Parts handed to XD06 / XD07'
    dm[15]['message'] = 'Sync requested for {n} part(s). They stay Waiting until GTOPAS and AP POLE have received them.'
    dm[16]['cause'] = 'GTOPAS or AP POLE could not receive the part'
    s['logging_messages'][1] = {"event": "XD06 / XD07", "cause": "GTOPAS or AP POLE rejects a part", "type": "Error", "msg_id": "LOG2",
                                "message": "Logging is done by XD06 / XD07 (refer UISS-Batch XD06 / XD07); the chip shows the result.",
                                "exception": "N", "action": "Status Failed; Display Message no. 11 on the chip"}
    return s


def rename_buttons(s, ren):
    for b in s['general']['buttons']:
        b['name'] = ren.get(b['name'], b['name'])
    for m in s['general']['screen_modes']:
        for sec in m['sections']:
            sec['buttons'] = {ren.get(k, k): v for k, v in sec.get('buttons', {}).items()}
    for it in s['items']:
        if it.get('name') in ren and it.get('control') == 'Button':
            it['name'] = ren[it['name']]


def prefix_groups(s, pre):
    for it in s['items']:
        if 'group' in it:
            it['group'] = it['group'].replace('<', f'<{pre} - ', 1)
    for m in s['display_messages']:
        if 'group' in m:
            m['group'] = f"{pre} - {m['group']}"
    for d in s['general']['display_order']:
        d['section'] = f"{pre} - {d['section']}"
    for m in s['general']['screen_modes']:
        m['mode'] = f"{pre} - {m['mode']}"


def build():
    pl = patch_part_list(replace_all(derive(load('PartListScreen_spec.json')), CALC_POST))
    mp = patch_mapping(replace_all(derive(load('MappingScreen_spec.json')), CALC_POST))
    n_op_mp = sum(1 for o in mp['operation'] if o['type'] == 'heading')

    # offsets for the Mapping tab: messages, logs, operation sections, remarks, layouts
    n_msg = max(int(m['msg_id'][3:]) for m in pl['display_messages'] if m.get('msg_id', '').startswith('MSG'))
    n_log = max(int(m['msg_id'][3:]) for m in pl['logging_messages'] if m.get('msg_id', '').startswith('LOG'))
    n_op = sum(1 for o in pl['operation'] if o['type'] == 'heading')
    n_rem = len(pl['general']['screen_mode_remarks'])
    n_lay = len(pl['screen_layout'])
    mp = shift_msg_refs(mp, n_msg)
    mp = shift_section_refs(mp, '5', n_op)
    shift_ids(mp['display_messages'], 'MSG', n_msg)
    shift_ids(mp['logging_messages'], 'LOG', n_log)
    mp = map_strings(mp, lambda t: re.sub(r'(remark )(\d)\)', lambda m: f"{m.group(1)}{int(m.group(2)) + n_rem})", t))
    mp['general']['screen_mode_remarks'] = [re.sub(r'^(\d)\)', lambda m: f"{int(m.group(1)) + n_rem})", r)
                                            for r in mp['general']['screen_mode_remarks']]
    for lay in mp['screen_layout']:
        lay['caption'] = re.sub(r'^(\d+)\.', lambda m: f"{int(m.group(1)) + n_lay}.", lay['caption'])

    ren_pl = {'Upload Excel': 'Upload Excel (Part List)', 'Export Excel': 'Export Excel (Part List)', 'Run calculation': 'Run calculation (Part List)'}
    ren_mp = {'Upload Excel': 'Upload Excel (Mapping)', 'Export Excel': 'Export Excel (Mapping)', 'Run calculation': 'Run calculation (Mapping)'}
    rename_buttons(pl, ren_pl)
    rename_buttons(mp, ren_mp)
    prefix_groups(pl, 'Part List')
    prefix_groups(mp, 'Mapping')

    # buttons: tab switch + union (same name -> one entry; functions joined when different)
    tab = {"name": "Tab (Part List / Mapping per Destination)", "function": "Switch between the Part List tab and the Mapping per Destination tab."}
    buttons, idx = [tab], {}
    for src, label in ((pl, 'Part List tab'), (mp, 'Mapping per Destination tab')):
        for b in src['general']['buttons']:
            if b['name'] in idx:
                e = idx[b['name']]
                if b['function'] != e['_f'][0][1]:
                    e['_f'].append((label, b['function']))
            else:
                e = {"name": b['name'], '_f': [(label, b['function'])]}
                idx[b['name']] = e
                buttons.append(e)
    for e in buttons[1:]:
        f = e.pop('_f')
        e['function'] = f[0][1] if len(f) == 1 else '; '.join(f"{lab}: {fn}" for lab, fn in f)
    names = [b['name'] for b in buttons]
    modes = []
    for src in (pl, mp):
        for m in src['general']['screen_modes']:
            for sec in m['sections']:
                st = sec.get('buttons', {})
                sec['buttons'] = {n: ('E' if n == tab['name'] else st.get(n, '-')) for n in names}
            modes.append(m)

    spec = {
        "doc_type": "screen",
        "general": {
            "objective": ["One screen with two tabs: Part List (part number level) and Mapping per Destination (part + calculation period + destination level)."]
                         + [f"Part List tab: {o}" for o in pl['general']['objective']]
                         + [f"Mapping per Destination tab: {o}" for o in mp['general']['objective']],
            "display_order": pl['general']['display_order'] + mp['general']['display_order'],
            "buttons": buttons,
            "screen_modes": modes,
            "screen_mode_remarks": pl['general']['screen_mode_remarks'] + mp['general']['screen_mode_remarks']
                                   + [f"{n_rem + len(mp['general']['screen_mode_remarks']) + 1}) '-' = the button is not on the tab of the mode."],
        },
        "screen_flow": [{"title": "Screen Flow for Cross Dock Part Master (tabs)", "flow": {"direction": "LR", "nodes": [
            {"id": "pl", "label": "Part List tab", "type": "screen"}, {"id": "mp", "label": "Mapping per Destination tab", "type": "screen"}],
            "edges": [{"from": "pl", "to": "mp", "label": "Tab"}, {"from": "mp", "to": "pl", "label": "Tab"}]}}]
                       + pl['screen_flow'] + mp['screen_flow'],
        "screen_layout": pl['screen_layout'] + mp['screen_layout'],
        "items": [{"group": "<Tab Bar>"}, {"name": tab['name'], "source": "", "field": "", "type": "", "len": "", "io": "I", "control": "Tab",
                                            "justified": "Left", "initial": "Part List", "required": "", "format": "", "validation": "",
                                            "description": "Part List tab (default) / Mapping per Destination tab."}]
                 + pl['items'] + mp['items'],
        "data_map": {"blocks": pl['data_map']['blocks'] + mp['data_map']['blocks']},
        "operation": [{"type": "text", "level": 1, "text": f"5.1 - 5.{n_op}: Part List tab. 5.{n_op + 1} - 5.{n_op + n_op_mp}: Mapping per Destination tab."}]
                     + pl['operation'] + mp['operation'],
        "display_messages": pl['display_messages'] + mp['display_messages'],
        "logging_messages": pl['logging_messages'] + mp['logging_messages'],
        "tables": [pl['tables'][0], IFR_TABLE],
    }
    # IF result block: complete the column list
    for b in spec['data_map']['blocks']:
        if b['destination']['table'] == IFR:
            b['mappings'] = full_update(b['mappings'], IFR_COLS)
    return write(set_header(spec, 'XD01'), 'XD01')


if __name__ == '__main__':
    print(build())
