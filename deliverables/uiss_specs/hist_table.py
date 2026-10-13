"""Proposed physical definition of TB_H_PART_CANDIDATE, shared by the Part List / Mapping specs.

One record per changed field. Insert only (never updated), so the table has CREATED_BY / CREATED_DT only.
"""

H = 'TB_H_PART_CANDIDATE'

RETENTION = ("Proposed retention: 24 months online by CREATED_DT; a monthly housekeeping job deletes older records "
             "(period configurable in system master). To be confirmed.")

COLUMNS = [
    ["HIST_ID", "BIGINT", "Y", "N", "Running number (identity)"],
    ["PART_NO", "VARCHAR(TBD)", "", "N", "Part number; length follows TB_M_PART_MASTER"],
    ["PERIOD", "CHAR(6)", "", "Y", "Calculation period YYYYMM for MAPPING / SYNC; NULL for ADD / EDIT (Part List has no period)"],
    ["EVENT_TYPE", "VARCHAR(10)", "", "N", "ADD / EDIT / MAPPING / SYNC"],
    ["SOURCE", "VARCHAR(10)", "", "N", "SCREEN / UPLOAD / RPA"],
    ["UPLOAD_ID", "VARCHAR(TBD)", "", "Y", "Upload of the change (Log); NULL when not from an upload"],
    ["DEST_CODE", "VARCHAR(TBD)", "", "Y", "Destination code for MAPPING; NULL for other events"],
    ["FIELD_NAME", "VARCHAR(30)", "", "N", "Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY, SYNC_STATUS"],
    ["OLD_VALUE", "VARCHAR(255)", "", "Y", "Value before the change; NULL for ADD or an added destination"],
    ["NEW_VALUE", "VARCHAR(255)", "", "Y", "Value after the change; NULL for a removed destination"],
    ["REMARK", "VARCHAR(500)", "", "Y", "Free text, e.g. SYNC_MESSAGE of a Failed sync"],
    ["CREATED_BY", "VARCHAR(20)", "", "N", "User who made the change (RPA user ID for SYNC)"],
    ["CREATED_DT", "DATETIME", "", "N", "Date and time of the change"],
]

TABLE = {"name": H, "kind": "history", "proposed": True,
         "description": "History of every change of a crossdock part (Add / Edit by screen or upload, mapping changes, Sync results). "
                        "Read by the History setting modal of Part List (index PART_NO, CREATED_DT). " + RETENTION,
         "columns": COLUMNS}


def op_table(level=2):
    """Column table for an Operation Description / Func Desc section."""
    return {"type": "table", "level": level, "row_lines": "all",
            "columns": [{"title": "Column", "width": 13}, {"title": "Type", "width": 10}, {"title": "PK", "width": 3, "align": "center"},
                        {"title": "Null", "width": 3, "align": "center"}, {"title": "Description", "width": 30}],
            "rows": COLUMNS}


def mappings(period, event, source, field, old, new, by, dt, upload_id="NULL", dest_code="NULL", remark="NULL", part="Part of the event"):
    """Data Map rows of one history insert, every column listed."""
    vals = {"HIST_ID": "Auto (identity)", "PART_NO": part, "PERIOD": period, "EVENT_TYPE": event, "SOURCE": source,
            "UPLOAD_ID": upload_id, "DEST_CODE": dest_code, "FIELD_NAME": field, "OLD_VALUE": old, "NEW_VALUE": new,
            "REMARK": remark, "CREATED_BY": by, "CREATED_DT": dt}
    return [{"dest_field": c[0], "description": vals[c[0]]} for c in COLUMNS]
