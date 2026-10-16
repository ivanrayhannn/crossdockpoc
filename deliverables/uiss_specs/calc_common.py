"""Shared definitions for the three calculation batches (Actual Demand Summary Sync, DAD Volume Calculation,
Mapping Destination Calculation)."""

NAME, PROJ = 'FID Rayhan', 'Crossdock Optimization'
NC = 'Not changed'
T, D, ADS, DM, RES, LOG = ('TB_M_PART_CANDIDATE', 'TB_M_PART_CANDIDATE_DEST', 'TB_R_ACTUAL_DEMAND_SUMMARY',
                           'TB_M_H0125_DESTINATION', 'TB_R_PART_DAD_RESULT', 'Log')
SYSM = 'System master'
SYSM_NOTE = "Range of months and schedule are set in the system master (not explained in this document)."


def header(fid, title, date='14-Oct-26'):
    return {"phase": "DR", "project_name": PROJ, "block_name": "Batch", "function_name": f"{fid} Crossdock - {title}",
            "created_date": date, "created_by": NAME}


def revisions(date='14-Oct-26'):
    return [{"revision": "0.1", "author": NAME, "date": date, "reviewed_by": "", "description": "Initial Draft"}]


ADS_COLS = [
    ["GROUPING_BUYER_CD", "VARCHAR(5)", "Y", "N", "Grouping buyer code, e.g. 9722D. With GROUPING_PD_CD it forms the 7-digit destination code"],
    ["GROUPING_PD_CD", "VARCHAR(2)", "Y", "N", "Grouping PD code, e.g. 10"],
    ["ORDER_TYPE_GROUP", "CHAR(1)", "Y", "N", "Order type group: N / S (both are summed by Crossdock)"],
    ["DEMAND_MONTH_YEAR", "CHAR(6)", "Y", "N", "Demand month YYYYMM, e.g. 202604"],
    ["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part number"],
    ["MAD", "NUMBER(TBD,2)", "", "Y", "Monthly average demand of the row; used by Crossdock"],
    ["DAD", "NUMBER(TBD,2)", "", "Y", "Daily average demand (not used by Crossdock)"],
    ["CREATE_DT", "TIMESTAMP", "", "Y", "Created date and time (from source)"],
    ["CREATE_BY", "VARCHAR(TBD)", "", "Y", "Created by (from source)"],
    ["UPDATE_DT", "TIMESTAMP", "", "Y", "Updated date and time (from source)"],
    ["UPDATE_BY", "VARCHAR(TBD)", "", "Y", "Updated by (from source)"],
    ["N01_QTY", "NUMBER", "", "Y", "Quantity month N-1 (not used by Crossdock)"],
    ["N02_QTY", "NUMBER", "", "Y", "Quantity month N-2 (not used by Crossdock)"],
    ["N03_QTY", "NUMBER", "", "Y", "Quantity month N-3 (not used by Crossdock)"],
    ["N04_QTY", "NUMBER", "", "Y", "Quantity month N-4 (not used by Crossdock)"],
    ["N05_QTY", "NUMBER", "", "Y", "Quantity month N-5 (not used by Crossdock)"],
    ["N06_QTY", "NUMBER", "", "Y", "Quantity month N-6 (not used by Crossdock)"],
    ["NUM_OF_OLD_PART_NO", "NUMBER", "", "Y", "Number of old part numbers (not used by Crossdock)"],
    ["NUM_OF_WORKINGDAY_6M", "NUMBER", "", "Y", "Working days in 6 months (not used by Crossdock)"],
    ["EM_MS_FLAG", "CHAR(1)", "", "Y", "EM / MS flag (not used by Crossdock)"]]
ADS_TABLE = {"name": ADS, "kind": "transaction", "proposed": False,
             "description": "Actual demand summary replicated from DB Surrounding to Supplier System (same columns). Key (PK) proposed from the data; types follow the source table.",
             "columns": ADS_COLS}

T_COLS = [
    ["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part number; length follows TB_M_PART_MASTER"],
    ["PART_NAME", "VARCHAR(TBD)", "", "N", "Retrieved from TB_M_PART_MASTER by PART_NO"],
    ["MIN_MAD", "INT", "", "N", "Minimum MAD (mandatory); reference compared with the average MAD of the DAD Volume Calculation"],
    ["PCS_CASE", "INT", "", "N", "Pieces per case (> 0)"],
    ["MAX_CASE_DAY", "INT", "", "N", "Total Case/Day of the part (> 0); limit of the mapping"],
    ["TOTAL_PCS_DAY", "INT", "", "N", "PCS_CASE x MAX_CASE_DAY"],
    ["EFFECTIVE_START_DATE", "DATE", "", "Y", "Effective start date; a part is calculated only from this date"],
    ["PART_STATUS", "VARCHAR(TBD)", "", "N", "Candidate / Active / Inactive"],
    ["SYNC_STATUS", "CHAR(1)", "", "N", "0 = No Sync, 3 = Waiting, 1 = Success, 2 = Failed"],
    ["SYNC_DT", "DATETIME", "", "Y", "Date-time of the last RPA result"],
    ["SYNC_MESSAGE", "VARCHAR(TBD)", "", "Y", "Reason of the last Failed sync"],
    ["LAST_SOURCE", "VARCHAR(TBD)", "", "N", "CALC / SCREEN / UPLOAD"],
    ["LAST_UPLOAD_ID", "VARCHAR(TBD)", "", "Y", "Upload that last changed the record"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
T_TABLE = {"name": T, "kind": "transaction", "proposed": False,
           "description": "Candidate part setting, one record per part (Part List data, no calculation period).", "columns": T_COLS}

D_COLS = [
    ["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part number (FK to TB_M_PART_CANDIDATE)"],
    ["PERIOD", "CHAR(6)", "Y", "N", "Calculation period YYYYMM, e.g. 202610; displayed as 'Oct 2026'"],
    ["DEST_CODE", "CHAR(7)", "Y", "N", "Destination code (buyer code + PD code, 7 digits); exists in TB_M_H0125_DESTINATION"],
    ["CASE_DAY", "INT", "", "N", "Allocated Case/Day of the destination (> 0)"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]
D_TABLE = {"name": D, "kind": "transaction", "proposed": False,
           "description": "Destination mapping, one record per part, calculation period and destination (Mapping per Destination data).",
           "columns": D_COLS}

DM_COLS = [
    ["DESTINATION_CD", "TBD", "Y", "N", "Destination code, 7 digits (buyer code + PD code), e.g. 9722D10. Used by Crossdock"],
    ["CUSTOMER_CD", "TBD", "", "", "Customer code (reference only)"],
    ["ORDER_TRANSPORTATION_CD", "TBD", "", "", "Order transportation code (reference only)"],
    ["BO_INSTRUCTION_CD", "TBD", "", "", "B/O instruction code (reference only)"],
    ["DESTINATION_NAME_ENG", "TBD", "", "", "Destination name. Used by Crossdock (shown with the code)"],
    ["REGION_CD", "TBD", "", "", "Region code (reference only)"],
    ["COUNTRY_NAME_ENG", "TBD", "", "", "Country name (reference only)"],
    ["POSTAL_CD_ENG", "TBD", "", "", "Postal code (reference only)"],
    ["STATE_CD_ENG", "TBD", "", "", "State code (reference only)"],
    ["DESTINATION_ADDR1_ENG", "TBD", "", "", "Destination address 1 (reference only)"],
    ["DESTINATION_ADDR2_ENG", "TBD", "", "", "Destination address 2 (reference only)"],
    ["CREATE_BY", "TBD", "", "", "User who created the record"],
    ["CREATE_DT", "TBD", "", "", "Created date and time"],
    ["UPDATE_BY", "TBD", "", "", "User who last updated the record"],
    ["UPDATE_DT", "TBD", "", "", "Last updated date and time"]]
from h_tables import H0125_COLS as _H125
_T = {c[0]: c for c in _H125}
for _c in DM_COLS:
    if _c[0] in _T:
        _c[1], _c[3] = _T[_c[0]][1], _T[_c[0]][3]
DM_TABLE = {"name": DM, "kind": "master", "proposed": False,
            "description": "Destination Master (existing Supplier System table, read only). Only the listed columns are relevant; full structure: X11 Destination Master (H0125) Sync.",
            "columns": DM_COLS}

RES_COLS = [
    ["PERIOD", "CHAR(6)", "Y", "N", "Calculation period YYYYMM (month of the run)"],
    ["PART_NO", "VARCHAR(TBD)", "Y", "N", "Part number"],
    ["MONTH_FROM", "CHAR(6)", "", "N", "First month of the range, YYYYMM"],
    ["MONTH_TO", "CHAR(6)", "", "N", "Last month of the range, YYYYMM"],
    ["NUM_OF_MONTH", "INT", "", "N", "Number of months of the range (divisor of the average)"],
    ["TOTAL_MAD", "NUMBER(TBD,2)", "", "N", "Sum of MAD of the part over the range"],
    ["AVG_MAD", "NUMBER(TBD,2)", "", "N", "TOTAL_MAD / NUM_OF_MONTH"],
    ["MIN_MAD", "INT", "", "N", "Min MAD of the part at calculation time (snapshot)"],
    ["OLD_STATUS", "VARCHAR(TBD)", "", "N", "Part status before the calculation"],
    ["NEW_STATUS", "VARCHAR(TBD)", "", "N", "Active (AVG_MAD >= MIN_MAD) / Inactive (AVG_MAD < MIN_MAD)"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "Batch user ID"],
    ["CREATED_DT", "DATETIME", "", "N", "Date and time of the calculation"]]
RES_TABLE = {"name": RES, "kind": "transaction", "proposed": True,
             "description": "Result of the DAD Volume Calculation, one record per calculated part and period. Name and columns proposed.",
             "columns": RES_COLS}


def schedule_rows(screen):
    return [["Trigger", "Scheduler set in the system master (monthly; date and time TBC)."],
            ["Auto retry", "When the run fails, the scheduler retries automatically up to 3 times."],
            ["Manual trigger", f"[Run calculation] on the {screen} screen, enabled only when the scheduled run and its 3 retries have failed."],
            ["Last success date", f"Stored in the Log (one date per run, all-or-nothing) and shown on the {screen} screen."]]


def log_block(batch):
    return {"source": f"Result of this run", "destination": {"table": LOG, "operation": "Insert", "description": "One record per run attempt"},
            "mappings": [{"dest_field": "BATCH_ID", "description": f"'{batch}'"},
                         {"dest_field": "RUN_TYPE", "description": "SCHEDULE / RETRY / MANUAL"},
                         {"dest_field": "RETRY_NO", "description": "0 for the scheduled run, 1-3 for the auto retries"},
                         {"dest_field": "STATUS", "description": "SUCCESS / FAILED"},
                         {"dest_field": "MESSAGE", "description": "Error message when FAILED"},
                         {"dest_field": "START_DT", "description": "Start date and time"},
                         {"dest_field": "END_DT", "description": "End date and time; END_DT of the latest SUCCESS = last success date"}]}
