"""F06 IF Cross Dock Master to GTOPAS and F07 IF Cross Dock Master to AP POLE (new UISS-Batch).
In the first version one RPA sent the cross dock master to the global system (X3 Sync). Now there is one
interface function per target system. Source data: Part List (TB_M_PART_CANDIDATE) and Part Mapping per
Destination (TB_M_PART_CANDIDATE_DEST)."""
from build_f01 import IFR, IFR_COLS, IFR_TABLE
from v2lib import batch_header, full_update, replace_all, table_of, write

T, D, H, LOG = 'TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE_DEST', 'TB_H_PART_CANDIDATE', 'Log'
COMMON_IF = [('RPA user ID', 'IF batch user ID'), ('SCREEN / UPLOAD / RPA / BATCH', 'SCREEN / UPLOAD / IF / BATCH'), ('RPA', 'IF function'),
             ('the global system', 'GTOPAS and AP POLE')]


def tables():
    t = replace_all(table_of('PartListUpload_v2_spec.json', T), COMMON_IF)
    d = table_of('MappingUpload_v3_spec.json', D)
    h = replace_all(table_of('PartListUpload_v2_spec.json', H), COMMON_IF)
    return t, d, h


def if_spec(fid, code, name, other_fid, other_name):
    t, d, h = tables()
    other_code = 'APPOLE' if code == 'GTOPAS' else 'GTOPAS'
    tgt = f"{name} (target system)"
    spec = {
        "doc_type": "batch",
        "general": {
            "objective": [
                f"To send the cross dock master of every Active part that is waiting for synchronisation to {name}: Pcs/Case and Max Case/Day "
                f"from the Part List ({T}) and all destinations with Case/Day of the ongoing period from the Part Mapping per Destination ({D}).",
                f"A part is sent as one complete set and replaces the data of the part in {name}, so a change such as Philippines up and "
                f"Thailand down, or a removed destination, arrives as one consistent update.",
                f"The result is kept per part for {name} in {IFR}; together with the result of {other_fid} ({other_name}) it gives the overall "
                f"Sync Status shown on the Cross Dock Part Master screen (F01)."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "[Sync] on F01 (Mapping per Destination tab)", "type": "event"},
                {"id": "b", "label": f"Read Waiting parts for {code}", "type": "process"},
                {"id": "c", "label": f"Send part set to {name}", "type": "process"},
                {"id": "d", "label": "Write result, overall Sync Status, history, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "d"}]}},
            "inputs": [
                {"name": IFR, "type": "DB", "description": f"Rows TARGET_SYSTEM = '{code}' with IF_STATUS = '3' (Waiting), set by [Sync] on F01"},
                {"name": T, "type": "DB", "description": "Part List: PCS_CASE, MAX_CASE_DAY of Active parts with SYNC_STATUS = '3'"},
                {"name": D, "type": "DB", "description": "Part Mapping per Destination: DEST_CODE, CASE_DAY of the ongoing period"}],
            "outputs": [
                {"name": tgt, "type": "System", "description": "Cross dock master of the part replaced (screens / fields TBD)"},
                {"name": IFR, "type": "DB", "description": f"Result for '{code}': IF_STATUS 1 / 2, IF_DT, IF_MESSAGE"},
                {"name": T, "type": "DB", "description": "Overall SYNC_STATUS, SYNC_DT, SYNC_MESSAGE of the part"},
                {"name": H, "type": "DB", "description": "History record per part (event SYNC, source IF)"},
                {"name": LOG, "type": "DB", "description": "Start, result per part and end messages"}],
            "extra_tables": [
                {"title": "Parameters", "columns": [{"title": "Name", "width": 14}, {"title": "Description", "width": 34}],
                 "rows": [["Target system", f"'{code}' ({name})"], ["User", "IF batch user ID (TBD)"]]},
                {"title": "Interface Data (per part)", "columns": [{"title": "Item", "width": 14}, {"title": "Source", "width": 18}, {"title": f"{name} field", "width": 16}],
                 "rows": [["Part number", f"{T}.PART_NO", "TBD"], ["Pcs/Case", f"{T}.PCS_CASE", "TBD"], ["Max Case/Day", f"{T}.MAX_CASE_DAY", "TBD"],
                          ["Calculation period", f"{D}.PERIOD (ongoing)", "TBD"], ["Destination code (n rows)", f"{D}.DEST_CODE", "TBD"],
                          ["Case/Day per destination (n rows)", f"{D}.CASE_DAY", "TBD"]]},
                {"title": "Execution Schedule", "columns": [{"title": "Item", "width": 12}, {"title": "Description", "width": 36}],
                 "rows": [["Trigger", f"On demand: [Sync] on F01 (Mapping per Destination tab) starts {fid} and {other_fid}. No scheduler (TBC)."],
                          ["Method", f"Interface method to {name} TBC: RPA as in the first design (the target has no interface) or a system interface."],
                          ["Order", f"Independent of {other_fid}; both run after [Sync]."]]}]
        },
        "func_flow": {
            "flow": {"direction": "TB", "nodes": [
                {"id": "p1", "label": "Start ([Sync] on F01)", "type": "process", "step": 1},
                {"id": "r", "label": IFR, "type": "db", "lane": "input"},
                {"id": "p2", "label": f"Select Waiting parts for {code}", "type": "process", "step": 2},
                {"id": "m", "label": f"{T} / {D}", "type": "db", "lane": "input"},
                {"id": "p3", "label": "Read part set", "type": "process", "step": 3},
                {"id": "p4", "label": f"Replace part data in {name}", "type": "process", "step": 4},
                {"id": "x", "label": tgt, "type": "db", "lane": "output"},
                {"id": "p5", "label": f"Write result for {code}", "type": "process", "step": 5},
                {"id": "p6", "label": "Overall Sync Status, history", "type": "process", "step": 6},
                {"id": "o", "label": f"{IFR} / {T} / {H}", "type": "db", "lane": "output"},
                {"id": "d", "label": "More parts?", "type": "decision", "step": 7},
                {"id": "p8", "label": "Log end, exit", "type": "process", "step": 8},
                {"id": "log", "label": LOG, "type": "db", "lane": "output"}],
             "edges": [{"from": "p1", "to": "p2"}, {"from": "r", "to": "p2"}, {"from": "p2", "to": "p3"}, {"from": "m", "to": "p3"},
                       {"from": "p3", "to": "p4"}, {"from": "p4", "to": "x"}, {"from": "p4", "to": "p5"}, {"from": "p5", "to": "p6"},
                       {"from": "p6", "to": "o"}, {"from": "p6", "to": "d"}, {"from": "d", "to": "p3", "label": "Yes"},
                       {"from": "d", "to": "p8", "label": "No"}, {"from": "p8", "to": "log"}]},
            "steps": [
                f"[Sync] on F01 sets the parts to Waiting (SYNC_STATUS = '3' in {T}, IF_STATUS = '3' for '{code}' and '{other_code}' in {IFR}) and starts {fid}. Write the start message (LOG1).",
                f"Select the parts with TARGET_SYSTEM = '{code}' and IF_STATUS = '3' in {IFR} whose PART_STATUS is still 'Active'. Keep CHANGED_DT of each part.",
                {"text": "For each part, read the complete set:", "children": [
                    f"PCS_CASE, MAX_CASE_DAY from {T}.",
                    f"All rows of the ongoing period (DEST_CODE, CASE_DAY) from {D}. A part without destination is sent with an empty destination list (TBC)."]},
                f"Replace the cross dock master of the part in {name} with this set (destinations not in the set are removed in {name}). One part = one unit of work: an error stops only this part.",
                {"text": f"Write the result of '{code}' in {IFR}:", "children": [
                    "Success: IF_STATUS = '1', IF_DT = now, IF_MESSAGE = blank.",
                    f"Failed: IF_STATUS = '2', IF_DT = now, IF_MESSAGE = reason from {name}. Write LOG3."]},
                {"text": f"Update the overall Sync Status of the part in {T} and record the history:", "children": [
                    "CHANGED_DT differs from step 2 (part changed while sending): SYNC_STATUS = '0' (No Sync).",
                    f"Else, result of '{code}' and of the other target in {IFR}: one still '3' -> SYNC_STATUS stays '3'; both '1' -> '1' (Success); one '2' -> '2' (Failed, SYNC_MESSAGE = target + reason).",
                    "SYNC_DT = now when SYNC_STATUS becomes 1 or 2.",
                    f"Insert {H}: event SYNC, source IF, FIELD_NAME SYNC_STATUS, REMARK = '{code}: ' + result / message."]},
                "More Waiting parts: back to step 3.",
                "Write the end message (LOG2) with the number of parts sent / failed. Exit."]
        },
        "data_map": {"blocks": [
            {"source": "Result of the target system", "destination": {"table": IFR, "operation": "Update", "description": f"Row of the part for '{code}'",
                                                                    "keys": [{"field": "PART_NO + TARGET_SYSTEM", "value": f"Part sent + '{code}'"}]},
             "mappings": full_update([{"dest_field": "IF_STATUS", "description": "'1' Success / '2' Failed"},
                                      {"dest_field": "IF_DT", "description": "Date-time of the result"},
                                      {"dest_field": "IF_MESSAGE", "description": f"Reason from {name} when Failed; blank when Success"},
                                      {"dest_field": "CHANGED_BY", "description": "IF batch user ID"},
                                      {"dest_field": "CHANGED_DT", "description": "Server system date-time"}], IFR_COLS)},
            {"source": {"table": IFR, "keys": [{"field": "PART_NO", "value": "Part sent (both target rows)"}]},
             "destination": {"table": T, "operation": "Update", "description": "Overall Sync Status of the part", "keys": [{"field": "PART_NO", "value": "Part sent"}]},
             "mappings": full_update([{"dest_field": "SYNC_STATUS", "description": "'0' when CHANGED_DT changed; else '3' while a target is Waiting, '1' when both Success, '2' when a target Failed"},
                                      {"dest_field": "SYNC_DT", "description": "Date-time when SYNC_STATUS becomes 1 or 2; else not changed"},
                                      {"dest_field": "SYNC_MESSAGE", "description": "Target + reason when Failed; blank when Success"}], t['columns'])},
            {"source": "Result of this part", "destination": {"table": H, "operation": "Insert", "description": "One record per part sent"},
             "mappings": [{"dest_field": "HIST_ID", "description": "Auto (identity)"}, {"dest_field": "PART_NO", "description": "Part sent"},
                          {"dest_field": "PERIOD", "description": "Ongoing calculation period"}, {"dest_field": "EVENT_TYPE", "description": "'SYNC'"},
                          {"dest_field": "SOURCE", "description": "'IF'"}, {"dest_field": "UPLOAD_ID", "description": "NULL"},
                          {"dest_field": "DEST_CODE", "description": "NULL"}, {"dest_field": "FIELD_NAME", "description": "'SYNC_STATUS'"},
                          {"dest_field": "OLD_VALUE", "description": "'Waiting'"}, {"dest_field": "NEW_VALUE", "description": "New overall status (Waiting / Success / Failed / No Sync)"},
                          {"dest_field": "REMARK", "description": f"'{code}: ' + 'Success' or IF_MESSAGE"},
                          {"dest_field": "CREATED_BY", "description": "IF batch user ID"}, {"dest_field": "CREATED_DT", "description": "Server system date-time"}]},
            {"source": "Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "Messages of the run"},
             "mappings": [{"dest_field": "BATCH_ID", "description": f"'{fid}_IF_{code}'"}, {"dest_field": "STATUS", "description": "SUCCESS / ERROR (any part failed)"},
                          {"dest_field": "MESSAGE", "description": "LOG1 - LOG5"}, {"dest_field": "START_DT / END_DT", "description": "Start and end date-time"}]}]},
        "func_desc_layout": "full",
        "func_desc": [
            {"type": "bullets", "marker": "-", "level": 0, "items": [
                f"Source data: Part List ({T}: Pcs/Case, Max Case/Day) and Part Mapping per Destination ({D}: destinations and Case/Day of the ongoing period). "
                "Only Active parts are sent; Candidate and Inactive parts are never sent.",
                f"{fid} sends to {name} only; {other_fid} sends the same data to {other_name}. The first version had one RPA for both targets.",
                f"Result per target: {IFR} (new table). Overall SYNC_STATUS in {T}: Waiting while a target is Waiting, Success when both targets are Success, "
                "Failed when one target failed (the next [Sync] sends the part again to both targets; replace is repeatable).",
                "A part changed on F01 or by upload while it is being sent gets SYNC_STATUS = No Sync, so the newer data is sent by the next [Sync].",
                f"Interface method, {name} screens / fields and behaviour when {name} is not available: TBC."]}],
        "logging_messages": [
            {"event": "Batch start", "cause": "[Sync] on F01", "type": "Info", "msg_id": "LOG1", "message": f"IF cross dock master to {name} started. <n> part(s).", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Batch end", "cause": "Batch finishes", "type": "Info", "msg_id": "LOG2", "message": f"IF cross dock master to {name} ended. Sent <OK>, failed <NG>.", "action": {"system": "Write the log.", "user": "-"}},
            {"event": "Send part", "cause": f"{name} rejects the part", "type": "Error", "msg_id": "LOG3", "message": f"Part No <PART_NO> not accepted by {name}: <IF_MESSAGE>.", "action": {"system": "IF_STATUS = 2; continue with the next part.", "user": "Correct the cause and click [Sync] on F01."}},
            {"event": "Connection", "cause": f"{name} not available / timeout", "type": "Error", "msg_id": "LOG4", "message": f"{name} is not available: <ERROR_DETAIL>. Remaining parts stay Failed.", "action": {"system": "IF_STATUS = 2 for the remaining parts. Stop.", "user": "Click [Sync] again later; contact PIC if it persists."}},
            {"event": "Unexpected error", "cause": "Any other system error", "type": "Critical", "msg_id": "LOG5", "message": "Unexpected error: <ERROR_DETAIL>.", "action": {"system": "Stop. STATUS = ERROR.", "user": "User contact PIC"}}],
        "appendix_layout": "full",
        "appendix": [],
        "tables": [IFR_TABLE, t, d, h],
    }
    return write(batch_header(fid) | spec, fid)


def build():
    return [if_spec('F06', 'GTOPAS', 'GTOPAS', 'F07', 'AP POLE'), if_spec('F07', 'APPOLE', 'AP POLE', 'F06', 'GTOPAS')]


if __name__ == '__main__':
    print('\n'.join(build()))
