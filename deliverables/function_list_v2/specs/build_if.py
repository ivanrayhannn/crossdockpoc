"""XD06 IF Cross Dock Master to GTOPAS and XD07 IF Cross Dock Master to AP POLE (new UISS-Batch).
In the first version one RPA sent the cross dock master to the global system (X3 Sync). Now there is one
interface function per target system, sending a file by SFTP (decided 18-Oct; topology to follow).
Source data: Part List (TB_M_PART_CANDIDATE) and Part Mapping per Destination (TB_M_PART_CANDIDATE_DEST).
TB_R_CROSSDOCK_IF_RESULT is a dummy table for the send status; the real output is the interface file."""
from build_xd01 import IFR, IFR_COLS, IFR_TABLE
from v2lib import batch_header, full_update, replace_all, table_of, write

T, D, H, LOG = 'TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE_DEST', 'TB_H_PART_CANDIDATE', 'Log'
COMMON_IF = [('RPA user ID', 'IF batch user ID'), ('SCREEN / UPLOAD / RPA / BATCH', 'SCREEN / UPLOAD / IF / BATCH'), ('RPA', 'IF function'),
             ('the global system', 'GTOPAS and AP POLE')]

# Interface data: one record per part x destination of the ongoing period (field, source, format, mandatory, business rule)
FIELDS = [
    ("SEND_ID", "Generated", "CHAR(14)", "Y", "Run of the send (YYYYMMDDHHMMSS); all records of one file have the same SEND_ID and are processed as one set"),
    ("PART_NO", f"{T}.PART_NO", "VARCHAR(TBD)", "Y", "Cross dock part. Only parts with PART_STATUS = Active and Sync Status Waiting are sent"),
    ("CROSSDOCK_FLAG", f"{T}.PART_STATUS", "CHAR(1)", "Y", "'Y' = the part is handled by crossdock (Active). TBC: send 'N' when a part became Inactive, so the target stops crossdock for it"),
    ("PCS_CASE", f"{T}.PCS_CASE", "NUMBER(TBD)", "Y", "Pieces per crossdock case; used to convert pieces to cases"),
    ("MAX_CASE_DAY", f"{T}.MAX_CASE_DAY", "NUMBER(TBD)", "Y", "Maximum cases per day of the part through crossdock (= total Case/Day of its destinations)"),
    ("EFFECTIVE_START_DATE", f"{T}.EFFECTIVE_START_DATE", "DATE (YYYYMMDD)", "Y", "Date from which the cross dock setting of the part applies"),
    ("PERIOD", f"{D}.PERIOD", "CHAR(6)", "Y", "Calculation period of the mapping (ongoing period, YYYYMM)"),
    ("DEST_CODE", f"{D}.DEST_CODE", "CHAR(7)", "Y", "Destination code (buyer code + PD code, TB_M_H0125_DESTINATION); one record per destination"),
    ("CASE_DAY", f"{D}.CASE_DAY", "NUMBER(TBD)", "Y", "Cases per day allocated to the destination (minimum 1; sum per part = MAX_CASE_DAY)"),
    ("SEND_DT", "Generated", "DATETIME", "Y", "Date-time the file is created"),
]
PURPOSE = {
    'GTOPAS': "GTOPAS (customer order side): which part and destination orders are handled by crossdock (order status 7) and how many cases per day per destination (assumption, TBC)",
    'APPOLE': "AP POLE (supplier PO side): which parts are ordered from the supplier as crossdock POs (crossdock flag of the Pra Daily Order), with pieces per case and the daily volume (assumption, TBC)",
}


def tables():
    t = replace_all(table_of('PartListUpload_v2_spec.json', T), COMMON_IF)
    d = table_of('MappingUpload_v3_spec.json', D)
    h = replace_all(table_of('PartListUpload_v2_spec.json', H), COMMON_IF)
    return t, d, h


def if_spec(fid, code, name, other_fid, other_name):
    t, d, h = tables()
    other_code = 'APPOLE' if code == 'GTOPAS' else 'GTOPAS'
    fname = f"XD_CDMASTER_{code}_<YYYYMMDDHHMMSS>.csv"
    out_file = f"Interface file to {name} (SFTP)"
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [
                f"To send the cross dock master of every Active part waiting for synchronisation to {name} as an interface file by SFTP: "
                f"Pcs/Case, Max Case/Day and Effective Start Date from the Part List ({T}) and all destinations with Case/Day of the ongoing period "
                f"from the Part Mapping per Destination ({D}).",
                f"Business purpose: {PURPOSE[code]}.",
                f"A part is sent as one complete set; {name} replaces the data of the part, so a change such as Philippines up and Thailand down, "
                "or a removed destination, arrives as one consistent update.",
                f"The send status per part is kept in {IFR} (dummy table); together with {other_fid} ({other_name}) it gives the overall Sync Status "
                "shown on the Cross Dock Part Master screen (XD01)."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "[Sync] on XD01 (Mapping per Destination tab)", "type": "event"},
                {"id": "b", "label": f"Read Waiting parts for {code}", "type": "process"},
                {"id": "c", "label": "Create interface file", "type": "process"},
                {"id": "e", "label": f"SFTP put to {name}", "type": "process"},
                {"id": "f", "label": "Send status, overall Sync Status, history, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "e"}, {"from": "e", "to": "f"}]}},
            "inputs": [
                {"name": IFR, "type": "DB", "description": f"Rows TARGET_SYSTEM = '{code}' with IF_STATUS = '3' (Waiting), set by [Sync] on XD01"},
                {"name": T, "type": "DB", "description": "Part List: PART_NO, PART_STATUS, PCS_CASE, MAX_CASE_DAY, EFFECTIVE_START_DATE"},
                {"name": D, "type": "DB", "description": "Part Mapping per Destination: PERIOD, DEST_CODE, CASE_DAY of the ongoing period"}],
            "outputs": [
                {"name": out_file, "type": "File", "description": f"{fname}: one record per part x destination (see Interface Data)"},
                {"name": IFR, "type": "DB", "description": f"Dummy table: send status of '{code}' per part (1 / 2), file name, message"},
                {"name": T, "type": "DB", "description": "Overall SYNC_STATUS, SYNC_DT, SYNC_MESSAGE of the part"},
                {"name": H, "type": "DB", "description": "History record per part (event SYNC, source IF)"},
                {"name": LOG, "type": "DB", "description": "Start, file, transfer and end messages"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["Target system", f"'{code}' ({name})"],
                          ["SFTP server / user / folder", f"{name} SFTP connection and inbound folder (TBC, from the topology)"],
                          ["Local folders", "Outbound folder (file created) and backup folder (file after transfer) (TBC)"],
                          ["Transfer retry", "Number of retries when the SFTP transfer fails (TBC, e.g. 3)"],
                          ["User", "IF batch user ID (TBC)"]]},
                {"title": "Interface File", "columns": [{"title": "Item", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["File name", f"{fname} (TBC)"],
                          ["Format", "CSV, comma separated, UTF-8, first row = field names (TBC: fixed length if required by the target)"],
                          ["Record unit", "One record per part x destination of the ongoing period; part fields are repeated on each record"],
                          ["Part without destination", "One record with DEST_CODE and CASE_DAY blank (TBC)"],
                          ["Trailer", "Record count for completeness check (TBC)"],
                          ["Transfer", f"SFTP put to the inbound folder of {name}; topology and result / acknowledge file TBC"]]},
                {"title": "Interface Data", "columns": [{"title": "Field", "width": 10}, {"title": "Source", "width": 13}, {"title": "Format", "width": 7},
                                                        {"title": "M", "width": 2}, {"title": "Business rule", "width": 16}],
                 "rows": [list(f) for f in FIELDS]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", f"On demand: [Sync] on XD01 (Mapping per Destination tab) starts {fid} and {other_fid}. No scheduler (TBC)."],
                          ["Method", f"Interface file by SFTP to {name}. Topology: to be provided by the user."],
                          ["Order", f"Independent of {other_fid}; both run after [Sync]."]]}]
        },
        "func_flow": {
            "flow": {"direction": "TB", "nodes": [
                {"id": "p1", "label": "Start ([Sync] on XD01)", "type": "process", "step": 1},
                {"id": "r", "label": IFR, "type": "db", "lane": "input"},
                {"id": "p2", "label": f"Select Waiting parts for {code}", "type": "process", "step": 2},
                {"id": "m", "label": f"{T} / {D}", "type": "db", "lane": "input"},
                {"id": "p3", "label": "Create interface file", "type": "process", "step": 3},
                {"id": "p4", "label": f"SFTP put to {name}, verify", "type": "process", "step": 4},
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
                {"text": f"Put the file by SFTP to the inbound folder of {name} and verify the transfer (file size / record count).", "children": [
                    "Transfer error: retry (parameter); still failing: LOG4.",
                    "Transfer OK: move the local file to the backup folder."]},
                {"text": f"Set the send status of every part of the file in {IFR}:", "children": [
                    "Transfer OK: IF_STATUS = '1', IF_DT = now, IF_FILE_NAME = file name, IF_MESSAGE blank.",
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
                f"{name} replaces the cross dock master of every part in the file with the content of the file (all destinations of the part)."]},
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
                "SFTP topology (server, folders, user), file format / naming and whether the target returns a result file.",
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
    return write(batch_header(fid) | spec, fid)


def build():
    return [if_spec('XD06', 'GTOPAS', 'GTOPAS', 'XD07', 'AP POLE'), if_spec('XD07', 'APPOLE', 'AP POLE', 'XD06', 'GTOPAS')]


if __name__ == '__main__':
    print('\n'.join(build()))
