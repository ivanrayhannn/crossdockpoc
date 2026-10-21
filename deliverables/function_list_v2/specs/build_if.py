"""XD06 IF Cross Dock Master to G-System and XD07 IF Cross Dock Master to AP POLE (new UISS-Batch).
In the first version one RPA sent the cross dock master to the global system (X3 Sync). Now there is one
interface function per target system, sending a file by SFTP (decided 18-Oct; topology to follow).
Source data: Part List (TB_M_PART_CANDIDATE) and Part Mapping per Destination (TB_M_PART_CANDIDATE_DEST).
TB_R_CROSSDOCK_IF_RESULT is a dummy table for the send status; the real output is the interface file."""
from build_xd01 import IFR, IFR_COLS, IFR_TABLE
from v2lib import batch_header, full_update, replace_all, table_of, write

T, D, H, LOG = 'TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE_DEST', 'TB_H_PART_CANDIDATE', 'Log'
COMMON_IF = [('RPA user ID', 'IF batch user ID'), ('SCREEN / UPLOAD / RPA / BATCH', 'SCREEN / UPLOAD / IF / BATCH'), ('RPA', 'IF function'),
             ('the global system', 'G-System and AP POLE')]

# Interface data: one record per part x destination of the ongoing period (field, source, format, mandatory, business rule)
FIELDS = [
    ("SEND_ID", "Generated", "CHAR(14)", "Y", "Run of the send (YYYYMMDDHHMMSS); all records of one file have the same SEND_ID and are processed as one set"),
    ("PART_NO", f"{T}.PART_NO", "VARCHAR(TBD)", "Y", "Cross dock part with Sync Status Waiting: Active parts, and parts that became Inactive since the last send"),
    ("CROSSDOCK_FLAG", f"{T}.PART_STATUS", "CHAR(1)", "Y", "'Y' = Active (handled by crossdock) / 'N' = Inactive: the target changes the status of the part to inactive (decided 19-Oct)"),
    ("PCS_CASE", f"{T}.PCS_CASE", "NUMBER(TBD)", "Y", "Pieces per crossdock case; used to convert pieces to cases"),
    ("MAX_CASE_DAY", f"{T}.MAX_CASE_DAY", "NUMBER(TBD)", "Y", "Maximum cases per day of the part through crossdock (= total Case/Day of its destinations)"),
    ("EFFECTIVE_START_DATE", f"{T}.EFFECTIVE_START_DATE", "DATE (YYYYMMDD)", "Y", "Date from which the cross dock setting of the part applies"),
    ("PERIOD", f"{D}.PERIOD", "CHAR(6)", "Y", "Calculation period of the mapping (ongoing period, YYYYMM)"),
    ("DEST_CODE", f"{D}.DEST_CODE", "CHAR(7)", "Y", "Destination code (buyer code + PD code, TB_M_H0125_DESTINATION); one record per destination"),
    ("CASE_DAY", f"{D}.CASE_DAY", "NUMBER(TBD)", "Y", "Cases per day allocated to the destination (minimum 1; sum per part = MAX_CASE_DAY)"),
    ("SEND_DT", "Generated", "DATETIME", "Y", "Date-time the file is created"),
]
TARGET = {
    'G-System': {"side": "G-System side (owner TBC)", "tables": "cross dock master of G-System (tables TBC)",
               "note": "Option #3 of 'NSP Cross Dock Interfacing Data' is drawn for AP POLE; the same SFTP pattern is assumed for G-System (TBC)."},
    'APPOLE': {"side": "TMA", "tables": "Crossdock Kanban Part Master and Crossdock Export Part Master (AP POLE)",
               "note": "Option #3 of 'NSP Cross Dock Interfacing Data' (decided 18-Oct)."},
}
METHOD = {
    'G-System': "interface to G-System as existing (not SFTP); the method and the target tables are not detailed in this document.",
    'APPOLE': ("interface file by SFTP, Option #3 of 'NSP Cross Dock Interfacing Data': NSP Send IF -> TMMIN SFTP -> TMA SFTP -> receive IF (TMA) "
               "-> AP POLE master. SFTP details, file format and the AP POLE tables are not detailed in this document."),
}
PURPOSE = {
    'G-System': "G-System (customer order side): which part and destination orders are handled by crossdock (order status 7) and how many cases per day per destination (assumption, TBC)",
    'APPOLE': "AP POLE (supplier PO side): which parts are ordered from the supplier as crossdock POs (crossdock flag of the Pra Daily Order), with pieces per case and the daily volume (assumption, TBC)",
}


def tables():
    t = replace_all(table_of('PartListUpload_v2_spec.json', T), COMMON_IF)
    d = table_of('MappingUpload_v3_spec.json', D)
    h = replace_all(table_of('PartListUpload_v2_spec.json', H), COMMON_IF)
    return t, d, h


def if_spec(fid, code, name, other_fid, other_name):
    t, d, h = tables()
    other_code = 'APPOLE' if code == 'G-System' else 'G-System'
    fname = f"XD_CDMASTER_{code}_<YYYYMMDDHHMMSS>.csv"
    tg = TARGET[code]
    out_file = f"Interface file to {name} (SFTP)"
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [
                f"To send the cross dock master of every Active part waiting for synchronisation to {name} as an interface file by SFTP: "
                f"Pcs/Case, Max Case/Day and Effective Start Date from the Part List ({T}) and all destinations with Case/Day of the ongoing period "
                f"from the Part Mapping per Destination ({D}).",
                f"Business purpose: {PURPOSE[code]}.",
                f"Topology (Option #3, SFTP): NSP Send IF -> TMMIN SFTP server -> {tg['side']} SFTP server -> receive IF on the {tg['side']} -> insert / update "
                f"{tg['tables']}. NSP develops the generate and send of the IF xDock Part Master; the receive and insert into {name} are developed by the {tg['side']}. "
                + tg['note'],
                f"A part is sent as one complete set; {name} replaces the data of the part, so a change such as Philippines up and Thailand down, "
                "or a removed destination, arrives as one consistent update.",
                f"The send status per part is kept in {IFR} (dummy table); together with {other_fid} ({other_name}) it gives the overall Sync Status "
                "shown on the Cross Dock Part Master screen (XD01)."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "[Sync] on XD01 (Mapping per Destination tab)", "type": "event"},
                {"id": "b", "label": f"Read Waiting parts for {code}", "type": "process"},
                {"id": "c", "label": "Create interface file", "type": "process"},
                {"id": "e", "label": "SFTP put to TMMIN SFTP server", "type": "process"},
                {"id": "t", "label": f"{tg['side']} SFTP -> receive IF -> {name} master", "type": "process"},
                {"id": "f", "label": "Send status, overall Sync Status, history, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "e"}, {"from": "e", "to": "t", "label": "SFTP"},
                          {"from": "e", "to": "f"}]}},
            "inputs": [
                {"name": IFR, "type": "DB", "description": f"Rows TARGET_SYSTEM = '{code}' with IF_STATUS = '3' (Waiting), set by [Sync] on XD01"},
                {"name": T, "type": "DB", "description": "Part List: PART_NO, PART_STATUS, PCS_CASE, MAX_CASE_DAY, EFFECTIVE_START_DATE"},
                {"name": D, "type": "DB", "description": "Part Mapping per Destination: PERIOD, DEST_CODE, CASE_DAY of the ongoing period"}],
            "outputs": [
                {"name": out_file, "type": "File", "description": f"{fname}: one record per part x destination (see Interface Data), put on the TMMIN SFTP server"},
                {"name": f"{name}: {tg['tables']}", "type": "System", "description": f"Inserted / updated by the receive IF of the {tg['side']} (not in NSP scope)"},
                {"name": IFR, "type": "DB", "description": f"Dummy table: send status of '{code}' per part (1 / 2), file name, message"},
                {"name": T, "type": "DB", "description": "Overall SYNC_STATUS, SYNC_DT, SYNC_MESSAGE of the part"},
                {"name": H, "type": "DB", "description": "History record per part (event SYNC, source IF)"},
                {"name": LOG, "type": "DB", "description": "Start, file, transfer and end messages"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["Target system", f"'{code}' ({name})"],
                          ["TMMIN SFTP server", "Server, user and outbound folder where NSP puts the file (TBC)"],
                          [f"{tg['side']} SFTP server", f"Inbound folder of the {tg['side']}; transfer TMMIN SFTP -> {tg['side']} SFTP (TBC who runs it)"],
                          ["Local folders", "Outbound folder (file created) and backup folder (file after transfer) (TBC)"],
                          ["Transfer retry", "Number of retries when the SFTP transfer fails (TBC, e.g. 3)"],
                          ["User", "IF batch user ID (TBC)"]]},
                {"title": "Interface File", "columns": [{"title": "Item", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["File name", f"{fname} (TBC)"],
                          ["Format", "CSV, comma separated, UTF-8, first row = field names (TBC: fixed length if required by the target)"],
                          ["Record unit", "One record per part x destination of the ongoing period; part fields are repeated on each record"],
                          ["Part without destination", "One record with DEST_CODE and CASE_DAY blank (TBC)"],
                          ["Trailer", "Record count for completeness check (TBC)"],
                          ["Transfer", f"SFTP put to the TMMIN SFTP server, forwarded to the {tg['side']} SFTP server (Option #3); result / acknowledge file TBC"]]},
                {"title": "Interface Data", "columns": [{"title": "Field", "width": 10}, {"title": "Source", "width": 13}, {"title": "Format", "width": 7},
                                                        {"title": "M", "width": 2}, {"title": "Business rule", "width": 16}],
                 "rows": [list(f) for f in FIELDS]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", f"On demand: [Sync] on XD01 (Mapping per Destination tab) starts {fid} and {other_fid}. No scheduler (TBC)."],
                          ["Method", f"Option #3: interface file by SFTP (TMMIN SFTP -> {tg['side']} SFTP); receive IF and insert into {name} by the {tg['side']}."],
                          ["Order", f"Independent of {other_fid}; both run after [Sync]."]]}]
        },
        "func_flow": {
            "flow": {"direction": "TB", "nodes": [
                {"id": "p1", "label": "Start ([Sync] on XD01)", "type": "process", "step": 1},
                {"id": "r", "label": IFR, "type": "db", "lane": "input"},
                {"id": "p2", "label": f"Select Waiting parts for {code}", "type": "process", "step": 2},
                {"id": "m", "label": f"{T} / {D}", "type": "db", "lane": "input"},
                {"id": "p3", "label": "Create interface file", "type": "process", "step": 3},
                {"id": "p4", "label": "SFTP put to TMMIN SFTP server, verify", "type": "process", "step": 4},
                {"id": "x", "label": out_file, "type": "file", "lane": "output"},
                {"id": "d", "label": "Transfer OK?", "type": "decision", "step": 5},
                {"id": "p6", "label": "Send status per part, overall Sync Status, history", "type": "process", "step": 6},
                {"id": "o", "label": f"{IFR} / {T} / {H}", "type": "db", "lane": "output"},
                {"id": "p7", "label": "Log end, exit", "type": "process", "step": 7},
                {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
             "edges": [{"from": "p1", "to": "p2"}, {"from": "r", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "m", "to": "p3"},
                       {"from": "p3", "to": "p4"}, {"from": "p4", "to": "x"}, {"from": "p4", "to": "d"}, {"from": "d", "to": "p6", "label": "Yes / No"},
                       {"from": "p6", "to": "o"}, {"from": "p6", "to": "p7"}, {"from": "p7", "to": "log"}]},
            "steps": [
                f"[Sync] on XD01 sets the parts to Waiting (SYNC_STATUS = '3' in {T}, IF_STATUS = '3' for '{code}' and '{other_code}' in {IFR}) and starts {fid}. Write LOG1.",
                f"Select the parts with TARGET_SYSTEM = '{code}' and IF_STATUS = '3' in {IFR} whose PART_STATUS is still 'Active'. Keep CHANGED_DT of each part. No part: write LOG2 and exit.",
                {"text": f"Create the interface file {fname} in the outbound folder (see Interface File / Interface Data):", "children": [
                    f"Per part: PART_NO, CROSSDOCK_FLAG 'Y', PCS_CASE, MAX_CASE_DAY, EFFECTIVE_START_DATE from {T}.",
                    f"Per destination of the ongoing period: PERIOD, DEST_CODE, CASE_DAY from {D} (one record each).",
                    "Same SEND_ID and SEND_DT on every record; trailer with the record count (TBC). Error: LOG3, all parts Failed (step 6)."]},
                {"text": f"Put the file by SFTP on the TMMIN SFTP server (outbound folder) and verify the transfer (file size / record count). The file is forwarded to the {tg['side']} SFTP server, where the receive IF of the {tg['side']} inserts / updates {tg['tables']}.", "children": [
                    "Transfer error: retry (parameter); still failing: LOG4.",
                    "Transfer OK: move the local file to the backup folder."]},
                {"text": f"Set the send status of every part of the file in {IFR}:", "children": [
                    "Transfer OK (file on the TMMIN SFTP server): IF_STATUS = '1', IF_DT = now, IF_FILE_NAME = file name, IF_MESSAGE blank.",
                    "File or transfer error: IF_STATUS = '2', IF_DT = now, IF_MESSAGE = error (LOG3 / LOG4).",
                    f"TBC: if {name} returns a result / acknowledge file, the status per part is taken from it instead of the transfer result."]},
                {"text": f"Update the overall Sync Status of each part in {T} and record the history:", "children": [
                    "CHANGED_DT differs from step 2 (part changed while sending): SYNC_STATUS = '0' (No Sync).",
                    f"Else, status of '{code}' and of '{other_code}' in {IFR}: one still '3' -> SYNC_STATUS stays '3'; both '1' -> '1' (Success); one '2' -> '2' (Failed, SYNC_MESSAGE = target + reason).",
                    "SYNC_DT = now when SYNC_STATUS becomes 1 or 2.",
                    f"Insert {H}: event SYNC, source IF, FIELD_NAME SYNC_STATUS, REMARK = '{code}: ' + result / message."]},
                "Write LOG2 with the file name and the number of parts / records sent. Exit."]
        },
        "data_map": {"blocks": [
            {"source": {"table": f"{T} + {D}", "keys": [{"field": "PART_NO", "value": "Waiting part"}, {"field": "PERIOD", "value": "Ongoing period"}]},
             "destination": {"table": out_file, "operation": "Insert", "description": "One record per part x destination"},
             "mappings": [{"source_field": f[1].split('.')[-1] if '.' in f[1] else '-', "dest_field": f[0],
                           "description": ("'Y' (Active)" if f[0] == 'CROSSDOCK_FLAG' else f[4] if f[1] == 'Generated' else "Same value")} for f in FIELDS]},
            {"source": "Result of the file / transfer", "destination": {"table": IFR, "operation": "Update", "description": f"Dummy table: rows of the parts of the file for '{code}'",
                                                                       "keys": [{"field": "PART_NO + TARGET_SYSTEM", "value": f"Part of the file + '{code}'"}]},
             "mappings": full_update([{"dest_field": "IF_STATUS", "description": "'1' transfer OK / '2' file or transfer error"},
                                      {"dest_field": "IF_DT", "description": "Date-time of the result"},
                                      {"dest_field": "IF_FILE_NAME", "description": "Name of the interface file"},
                                      {"dest_field": "IF_MESSAGE", "description": "Error when '2'; blank when '1'"},
                                      {"dest_field": "CHANGED_BY", "description": "IF batch user ID"},
                                      {"dest_field": "CHANGED_DT", "description": "Server system date-time"}], IFR_COLS)},
            {"source": {"table": IFR, "keys": [{"field": "PART_NO", "value": "Part of the file (both target rows)"}]},
             "destination": {"table": T, "operation": "Update", "description": "Overall Sync Status of the part", "keys": [{"field": "PART_NO", "value": "Part of the file"}]},
             "mappings": full_update([{"dest_field": "SYNC_STATUS", "description": "'0' when CHANGED_DT changed; else '3' while a target is Waiting, '1' when both '1', '2' when a target is '2'"},
                                      {"dest_field": "SYNC_DT", "description": "Date-time when SYNC_STATUS becomes 1 or 2; else not changed"},
                                      {"dest_field": "SYNC_MESSAGE", "description": "Target + reason when Failed; blank when Success"}], t['columns'])},
            {"source": "Result of the part", "destination": {"table": H, "operation": "Insert", "description": "One record per part of the file"},
             "mappings": [{"dest_field": "HIST_ID", "description": "Auto (identity)"}, {"dest_field": "PART_NO", "description": "Part sent"},
                          {"dest_field": "PERIOD", "description": "Ongoing calculation period"}, {"dest_field": "EVENT_TYPE", "description": "'SYNC'"},
                          {"dest_field": "SOURCE", "description": "'IF'"}, {"dest_field": "UPLOAD_ID", "description": "NULL"},
                          {"dest_field": "DEST_CODE", "description": "NULL"}, {"dest_field": "FIELD_NAME", "description": "'SYNC_STATUS'"},
                          {"dest_field": "OLD_VALUE", "description": "'Waiting'"}, {"dest_field": "NEW_VALUE", "description": "New overall status (Waiting / Success / Failed / No Sync)"},
                          {"dest_field": "REMARK", "description": f"'{code}: ' + 'sent <file name>' or IF_MESSAGE"},
                          {"dest_field": "CREATED_BY", "description": "IF batch user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date-time"}]},
            {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "Messages of the run"},
             "mappings": [{"dest_field": "BATCH_ID", "description": f"'{fid}_IF_{code}'"}, {"dest_field": "STATUS", "description": "SUCCESS / ERROR"},
                          {"dest_field": "MESSAGE", "description": "LOG1 - LOG5"}, {"dest_field": "START_DT / END_DT", "description": "Start and end date-time"}]}]},
        "func_desc_layout": "full",
        "func_desc": [
            {"type": "heading", "text": "4.1 Business Process"},
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                "The D/S team maintains the cross dock master on XD01 (Part List: Pcs/Case, Max Case/Day, Effective Start Date; Mapping per Destination: "
                "Case/Day per destination of the ongoing period, created by XD05 process 2 and adjusted by screen or upload XD03).",
                "Every change sets the part to No Sync. The D/S team clicks [Sync] when the changes are complete; only Active parts are sent, Candidate and Inactive parts are not.",
                f"{fid} sends to {name}; {other_fid} sends the same data to {other_name}. Purpose for {name}: {PURPOSE[code]}.",
                f"{name} replaces the cross dock master of every part in the file with the content of the file (all destinations of the part).",
                f"Topology (Option #3): NSP Send IF -> TMMIN SFTP -> {tg['side']} SFTP -> receive IF ({tg['side']}) -> {tg['tables']}. " + tg['note']]},
            {"type": "heading", "text": "4.2 Field Rules"},
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                "Fields, source and business rule: see Interface Data (General Description). The field names on the side of the target are TBC (target layout).",
                "Sum of CASE_DAY of the records of a part = MAX_CASE_DAY (guaranteed by XD05 and the save checks of XD01 / XD03).",
                "PERIOD is always the ongoing period; past periods are never sent."]},
            {"type": "heading", "text": "4.3 Status and Dummy Table"},
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                f"{IFR} is a dummy table that keeps the send status per part and target; the real output of {fid} is the interface file sent to {name}.",
                "Overall SYNC_STATUS: Waiting while a target is Waiting, Success when both targets are sent, Failed when one target failed "
                "(the next [Sync] sends the part again to both targets; replace is repeatable).",
                "A part changed on XD01 or by upload while it is being sent gets SYNC_STATUS = No Sync, so the newer data is sent by the next [Sync]."]},
            {"type": "heading", "text": "4.4 Open Points"},
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                f"SFTP details (servers, folders, users, who forwards TMMIN SFTP -> {tg['side']} SFTP), file format / naming and whether the {tg['side']} returns a result file.",
                f"Which fields go to which {name} table ({tg['tables']}).",
                "Field names and lengths required by the target; part without destination.",
                "Parts that became Inactive (XD05) are not sent today: should the target receive CROSSDOCK_FLAG 'N' to stop crossdock?"]}],
        "logging_messages": [
            {"event": "Batch start", "cause": "[Sync] on XD01", "type": "Info", "msg_id": "LOG1", "message": f"IF cross dock master to {name} started. <n> part(s).", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": f"IF cross dock master to {name} ended. File <FILE_NAME>, parts <n>, records <r>, status <STATUS>.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Create file", "cause": "Interface file cannot be created", "type": "Error", "msg_id": "LOG3", "message": f"Cannot create the interface file to {name}: <ERROR_DETAIL>.", "action": {"system": "All parts of the run IF_STATUS = 2. Stop.", "user": "Click [Sync] again; contact PIC if it persists."}},
            {"event": "SFTP transfer", "cause": f"{name} SFTP not available / transfer fails after retry", "type": "Error", "msg_id": "LOG4", "message": f"SFTP transfer of <FILE_NAME> to {name} failed: <ERROR_DETAIL>.", "action": {"system": "All parts of the file IF_STATUS = 2. Keep the file in the outbound folder.", "user": "Click [Sync] again later; contact PIC if it persists."}},
            {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG5", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Stop. STATUS = ERROR.", "user": "User contact PIC"}}],
        "appendix_layout": "full",
        "appendix": [],
        "tables": [IFR_TABLE, t, d, h],
    }
    return write(batch_header(fid) | decide(spec, code, name), fid)


DETAIL_ROWS = ('TMMIN SFTP server', 'G-System side (owner TBC) SFTP server', 'TMA SFTP server', 'Local folders', 'Transfer retry')


def decide(spec, code, name):
    """Decisions of 19-Oct: Inactive parts are sent (CROSSDOCK_FLAG 'N'); G-System does not use SFTP; SFTP details, file format
    and the destination tables of the target are not detailed in this document."""
    g = spec['general']
    g['extra_tables'] = [t for t in g['extra_tables'] if t['title'] != 'Interface File']
    for t in g['extra_tables']:
        if t['title'] == 'Parameters':
            t['rows'] = [r for r in t['rows'] if r[0] not in DETAIL_ROWS] + [["Interface method", METHOD[code]]]
        if t['title'] == 'Execution Schedule':
            t['rows'] = [r if r[0] != 'Method' else ["Method", METHOD[code]] for r in t['rows']]
            t['rows'] = [[r[0], r[1].replace(' No scheduler (TBC).', ' No scheduler.')] for r in t['rows']]
    g['objective'][0] = (f"To send the cross dock master of the parts waiting for synchronisation to {name}: Active parts with Pcs/Case, Max Case/Day, "
                         f"Effective Start Date and all destinations with Case/Day of the ongoing period, and parts that became Inactive (CROSSDOCK_FLAG 'N', "
                         f"so {name} changes their status to inactive). Source: Part List ({T}) and Part Mapping per Destination ({D}).")
    g['objective'][2] = "Interface method: " + METHOD[code]
    g['objective'] = [o for o in g['objective'] if '(assumption, TBC)' not in o]
    if code == 'G-System':
        spec = replace_all(spec, [
            ("Create interface file", "Create interface data"), ("SFTP put to TMMIN SFTP server, verify", "Send to G-System (existing method)"),
            ("SFTP put to TMMIN SFTP server", "Send to G-System (existing method)"),
            ("G-System side (owner TBC) SFTP -> receive IF -> G-System master", "G-System master"),
            ("Interface file to G-System (SFTP)", "Interface data to G-System"),
            ("Transfer OK?", "Sent OK?"), ("Transfer OK (file on the TMMIN SFTP server)", "Sent OK"),
            ("File or transfer error", "Create or send error"), ("Result of the file / transfer", "Result of the send"),
            ("G-System SFTP not available / transfer fails after retry", "G-System not available / send fails after retry"),
            ("SFTP transfer of <FILE_NAME> to G-System failed", "Send of <SEND_ID> to G-System failed"), ("SFTP transfer", "Send"),
            ("G-System: cross dock master of G-System (tables TBC)", "G-System: cross dock master of the part"),
            ("Inserted / updated by the receive IF of the G-System side (owner TBC) (not in NSP scope)", "Updated in G-System (not in NSP scope)"),
            (": one record per part x destination (see Interface Data), put on the TMMIN SFTP server", ": one record per part x destination (see Interface Data)")])
        for st in spec['func_flow']['steps']:
            if isinstance(st, dict) and st['text'].startswith('Put the file by SFTP'):
                st['text'] = "Send the interface data to G-System by the existing interface method (not SFTP; not detailed in this document)."
                st['children'] = ["Send error: retry; still failing: LOG4.", "Sent OK: continue."]
            if isinstance(st, dict) and st['text'].startswith('Create the interface file'):
                st['text'] = st['text'].replace('Create the interface file', 'Create the interface data').replace(' in the outbound folder', '')
        for e in spec['func_flow']['flow']['edges'] + spec['general']['operation_flow']['flow']['edges']:
            if e.get('label') == 'SFTP':
                e['label'] = 'send'
    spec = replace_all(spec, [
        ("The field names on the side of the target are TBC (target layout).", "The field names on the side of the target follow the target layout."),
        ("IF batch user ID (TBC)", "IF batch user ID"),
        ("; trailer with the record count (TBC)", ""),
        ("TBC: if G-System returns a result / acknowledge file, the status per part is taken from it instead of the transfer result.", "The status is the result of the send."),
        ("TBC: if AP POLE returns a result / acknowledge file, the status per part is taken from it instead of the transfer result.", "The status is the result of the SFTP transfer.")])
    fd = spec['func_desc']
    for i, d in enumerate(fd):
        if d['type'] == 'bullets':
            d['items'] = [x for x in d['items'] if not x.startswith('Topology (Option #3)') and '(assumption, TBC)' not in x]
        if d['type'] == 'heading' and d['text'] == '4.4 Open Points':
            fd[i + 1]['items'] = ["Field names on the side of the target follow the target layout (not detailed in this document)."]
    fd.insert(2, {"type": "bullets", "marker": "-", "level": 0, "items": ["Interface method: " + METHOD[code],
              "Parts that became Inactive (XD05 process 1) are No Sync and are sent with CROSSDOCK_FLAG 'N' and without destinations; "
              f"{name} changes the status of the part to inactive."]})
    return spec


def build():
    return [if_spec('XD06', 'G-System', 'G-System', 'XD07', 'AP POLE'), if_spec('XD07', 'APPOLE', 'AP POLE', 'XD06', 'G-System')]


if __name__ == '__main__':
    print('\n'.join(build()))
