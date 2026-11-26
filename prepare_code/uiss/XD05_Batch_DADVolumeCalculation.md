# XD05 – DAD Volume Calculation Batch

> Generated from `deliverables/function_list_v2/specs/XD05_spec.json` (UISS `XD05_UISS_Batch_DADVolumeCalculation.xlsx`). Do not edit by hand: change the spec and run `python3 prepare_code/build_md.py`. Document names: GTOPAS / NSP (prototype: G-System / Supplier System).

| Phase | Project | Block | Function | Created | By | Type |
|---|---|---|---|---|---|---|
| DR | Crossdock Optimization | Batch | XD05 DAD Volume Calculation Batch | 18-Oct-26 | FID Rayhan | batch |

## Revision

| Rev | Author | Date | Reviewed by | Description |
|---|---|---|---|---|
| 0.1 | FID Rayhan | 18-Oct-26 |  | Initial Draft |
| 0.2 | FID Rayhan | 17-Nov-26 |  | SYNC_STATUS = 0 (No Sync) for every status change to or from Active (data edit mapping aligned with 4.3, FB-207); AP POLE delete by RPA (XD07, WLM9Q890) instead of SFTP file. |
| 0.3 | FID Rayhan | 18-Nov-26 |  | Sheet "Active to Inactive" removed (18-Nov): Inactive parts with No Sync / Failed are taken by [Sync] by their status. |
| 0.4 | FID Rayhan | 19-Nov-26 |  | Runs on day D and makes the Next period (Kanban and Export Crossdock Master); process 3 Period Rollover on day 1 (19-Nov). |
| 0.5 | FID Rayhan | 20-Nov-26 |  | Period Rollover writes GTOPAS_SYNC_DT, SYNC_RUN_ID, history SYNC and the run Log (TB_R_CROSSDOCK_IF_RESULT removed, 20-Nov). |
| 0.6 | FID Rayhan | 22-Nov-26 |  | Staging rows in TB_H_PART_CANDIDATE_STG_SYNC for the new period and Period Rollover by GTOPAS_SYNC_STATUS 0 + PERIOD (22-Nov). |
| 0.7 | FID Rayhan | 23-Nov-26 |  | Staging per target through SP_STG_WRITE (4.11); Period Rollover updates TB_H_STG_GTOPAS and starts the RPA parent flow (XD06 only). Effective Start Date removed: every part with a row in the period is calculated. |
| 0.8 | FID Rayhan | 24-Nov-26 |  | Data Map: ORDER_TYPE on TB_H_PART_CANDIDATE / TB_M_PART_CANDIDATE_DEST (Order Type per destination row). |
| 0.9 | FID Rayhan | 26-Nov-26 |  | Staging: no SYNC_RUN_ID, the run is SYNC_DT (one value per [Sync] click / rollover); one unsent row per key (a new change updates it, back to the sent value deletes it); SYNC_STATUS 0 / 1. SQL: prepare_code/sql/crossdock_staging_sync.sql. |
| 0.10 | FID Rayhan | 26-Nov-26 |  | TB_H_STG_APPOLE_KANBAN / _EXPORT: EFFECTIVE_MONTH_YEAR removed (same value as PERIOD); the views make Effective Month / Year (MM/YYYY of PERIOD) for the upload file. |

## 1. General

### Objective

- Process 1: To calculate the average MAD of every crossdock part over the range of months set in the system master and to set the part status in TB_M_PART_CANDIDATE: Active when the average MAD is equal to or above Min MAD, Inactive when it is below.
- Process 2: To create the new calculation period of Export Crossdock Master and split the Max Case/Day of every Active part over its destinations in proportion to the actual demand (MAD) of each destination (buyer code + PD code) over the range of months set in the system master.
- Each process is all-or-nothing and is retried automatically up to 3 times; after that it can be started manually from the Cross Dock Part Master screen (XD01).

### Operation flow

```mermaid
flowchart TB
  a>"Trigger: new data in TB_R_ACTUAL_DEMAND_SUMMARY / retry / XD01 [Run calculation]"]
  b["Process 1: average MAD vs Min MAD -> Active / Inactive"]
  c["Process 2: result MAD per destination -> Case/Day of the new period"]
  d["Save, Log"]
  a --> b
  b -->|success| c
  c --> d
```

### Input

| Name | Type | Description |
|---|---|---|
| TB_R_ACTUAL_DEMAND_SUMMARY (NSP) | DB | MAD per part, buyer code, PD code, order type and month (replicated by the Actual Demand Summary Sync); CREATE_DT later than DATA_DT of the last successful run = new data (trigger) |
| TB_M_PART_CANDIDATE | DB | Registered parts: Min MAD and status, every part with a row in the period |
| System master | DB | Range of months and schedule (not explained in this document) |
| TB_M_H0125_DESTINATION (Destination Master) | DB | Valid 7-digit destination codes |
| TB_M_PART_CANDIDATE_DEST | DB | Mapping of the previous period (to detect changes) |

### Output

| Name | Type | Description |
|---|---|---|
| TB_R_PART_DAD_RESULT | DB | if successful: average MAD and calculated status of every calculated part |
| TB_M_PART_CANDIDATE | DB | if successful: PART_STATUS of the parts whose status changes |
| TB_H_PART_CANDIDATE | DB | if successful: history record per status change (event CALC, source BATCH) |
| Log | DB | One record per run attempt (SUCCESS / FAILED); last success date |
| TB_M_PART_CANDIDATE_DEST | DB | if successful: mapping of the new period (run month) |

### Parameters

| Name | Description |
|---|---|
| Range of months (N) | Number of months before the run month, from the system master (e.g. 6) |
| Run month | Month of the run date, YYYYMM; = calculation period |
| User | Batch user ID (scheduler / retry) or login user (manual trigger) |
| New period | Run month YYYYMM (e.g. 202610) |

### Grouping Keys

| Field Name |
|---|
| PART_NO (process 1 and 2) |
| GROUPING_BUYER_CD + GROUPING_PD_CD (process 2) |

### Execution Schedule

| Item | Description |
|---|---|
| Trigger | The scheduler checks TB_R_ACTUAL_DEMAND_SUMMARY (NSP): XD05 starts when the table has rows with CREATE_DT later than DATA_DT of the last successful XD05 run (new data from XD04). No new data: XD05 is not started (decided 6-Nov). One run = process 1, then process 2. Check frequency set in the system master. |
| Auto retry | A failed process is retried automatically up to 3 times; process 2 starts only after process 1 has succeeded. |
| Manual trigger | [Run calculation (Kanban Crossdock Master)] on XD01 runs process 1 and then process 2; [Run calculation (Mapping)] on XD01 runs process 2 only. Each button is enabled only when its process and the 3 retries have failed. |
| Last success date | One date per process in the Log; process 1 shown on the Kanban Crossdock Master tab, process 2 on the Export Crossdock Master tab. |
| Order | Runs after XD04 has brought new data (scheduled run, retry or manual run outside NSP). When XD04 still fails, there is no new data and XD05 is not started (decided 6-Nov). |

## 2. Function flow

```mermaid
flowchart TB
  a_p1["1. Start: scheduler / retry / manual"]
  a_p2["2. Range of months"]
  a_p3["3. Select parts (rows of the period)"]
  a_m[("TB_M_PART_CANDIDATE")]
  a_p4["4. Average MAD per part"]
  a_ads[("TB_R_ACTUAL_DEMAND_SUMMARY")]
  a_p5["5. Compare with Min MAD"]
  a_p6["6. Save result, status, history"]
  a_o[("TB_R_PART_DAD_RESULT / TB_M_PART_CANDIDATE / TB_H_PART_CANDIDATE")]
  a_d{"7. Any error?"}
  a_p8["8. Commit, Log SUCCESS"]
  a_p9["9. Roll back, Log FAILED, retry"]
  a_log[("Log")]
  b_p1["10. Start: scheduler / retry / manual"]
  b_p2["11. Range of months, new period"]
  b_p3["12. Select Active parts"]
  b_m[("TB_M_PART_CANDIDATE")]
  b_p4["13. Result MAD per destination"]
  b_ads[("TB_R_ACTUAL_DEMAND_SUMMARY")]
  b_p5["14. Check destination master"]
  b_dm[("TB_M_H0125_DESTINATION")]
  b_p6["15. Sort, limit, allocate Case/Day"]
  b_p7["16. Save new period, Sync Status, history"]
  b_o[("TB_M_PART_CANDIDATE_DEST / TB_M_PART_CANDIDATE / TB_H_PART_CANDIDATE")]
  b_d{"17. Any error?"}
  b_p9["18. Commit, Log SUCCESS"]
  b_p10["19. Roll back, Log FAILED, retry"]
  b_log[("Log")]
  a_p1 --> a_p2
  a_p2 --> a_p3
  a_m --> a_p3
  a_p3 --> a_p4
  a_ads --> a_p4
  a_p4 --> a_p5
  a_p5 --> a_p6
  a_p6 --> a_o
  a_p6 --> a_d
  a_d -->|No| a_p8
  a_d -->|Yes| a_p9
  a_p8 --> a_log
  a_p9 --> a_log
  a_p8 -->|process 2| b_p1
  b_p1 --> b_p2
  b_p2 --> b_p3
  b_m --> b_p3
  b_p3 --> b_p4
  b_ads --> b_p4
  b_p4 --> b_p5
  b_dm --> b_p5
  b_p5 --> b_p6
  b_p6 --> b_p7
  b_p7 --> b_o
  b_p7 --> b_d
  b_d -->|No| b_p9
  b_d -->|Yes| b_p10
  b_p9 --> b_log
  b_p10 --> b_log
```

1. Process 1 (part status) starts when the trigger finds new data in TB_R_ACTUAL_DEMAND_SUMMARY (NSP) (CREATE_DT later than DATA_DT of the last successful run), from an automatic retry, or [Run calculation (Kanban Crossdock Master)] on XD01.
2. Get the range of months N from the system master.
  - MONTH_TO = month before the run month; MONTH_FROM = N months back. Example: run in Oct 2026, N = 6 -> 202604 to 202609.
3. Select every part of TB_M_PART_CANDIDATE (Candidate, Active and Inactive).
  - Take every part with a row in the Current period. A part registered for the next period before day D already has its next row: it is calculated and that row is kept (no second insert).
4. For each selected part, read TB_R_ACTUAL_DEMAND_SUMMARY rows of the part within the range and calculate (see 4.1):
  - TOTAL_MAD = sum of MAD of all buyer code / PD code / order type (N + S) rows in the range.
  - AVG_MAD = TOTAL_MAD / N. The divisor is always N; a month without data counts as 0.
5. Compare AVG_MAD with MIN_MAD of the part (see 4.2):
  - AVG_MAD >= MIN_MAD -> Active.
  - AVG_MAD < MIN_MAD -> Inactive.
6. Save (see 4.3):
  - Insert one result record per calculated part into TB_R_PART_DAD_RESULT.
  - When the calculated status differs from the current one: update PART_STATUS in TB_M_PART_CANDIDATE and insert a history record (event CALC, source BATCH).
7. Check whether any error occurred during steps 2 to 6.
8. No error: commit process 1, record SUCCESS of process 1 in the Log (END_DT = last success date). Continue with step 10 (process 2).
9. Error: roll back process 1, record FAILED in the Log; process 2 is not started.
  - The scheduler retries automatically up to 3 times. After the 3rd failed retry, [Run calculation (Kanban Crossdock Master)] is enabled on XD01. Exit.
10. Process 2 (destination mapping) starts after process 1 has succeeded, from an automatic retry of process 2, or [Run calculation (Mapping)] on XD01 (process 2 only). It uses the part status just set by process 1.
11. Get the range of months N from the system master; the new period = run month.
  - Example: run in Oct 2026, N = 6 -> months 202604 to 202609, new period 202610.
12. Select every part of TB_M_PART_CANDIDATE with PART_STATUS = Active.
13. For each part, read TB_R_ACTUAL_DEMAND_SUMMARY rows within the range and group them by GROUPING_BUYER_CD + GROUPING_PD_CD:
  - Destination code = GROUPING_BUYER_CD + GROUPING_PD_CD (7 digits, e.g. 9722D + 10 = 9722D10).
  - Result MAD = sum of MAD of the group (order types N + S). Groups with result MAD 0 are not used.
  - A part without any result MAD gets no destination (listed with Total Case/Day 0 on the screen).
14. Check every destination code in TB_M_H0125_DESTINATION (DESTINATION_CD).
  - Not found: error -> go to step 19 (all-or-nothing).
15. Allocate Case/Day per part (see 4.6):
  - Sort the destinations by result MAD, largest first, and keep at most Max Case/Day destinations.
  - Target = result MAD / sum of result MAD of the kept destinations x Max Case/Day.
  - Round down with a minimum of 1; adjust so the total equals Max Case/Day.
16. Save the new period in TB_M_PART_CANDIDATE_DEST (see 4.7):
  - Delete the rows of the new period if they exist (manual re-run), then insert the calculated rows.
  - Every row of the new period goes to the staging through SP_STG_WRITE: Export ADD per destination; DELETE (0) for a destination of the previous period not mapped any more and for every destination of an Inactive part still > 0; GTOPAS only for a destination that appears or disappears. A history record per added / changed / removed destination (event MAPPING, source BATCH).
17. Check whether any error occurred during steps 11 to 16.
18. No error: commit, record SUCCESS in the Log (END_DT = last success date). The new period becomes the ongoing period; the previous period becomes past (read only). Exit.
19. Error: roll back process 2, record FAILED of process 2 in the Log.
  - The scheduler retries process 2 automatically up to 3 times. After the 3rd failed retry, [Run calculation (Mapping)] is enabled on XD01. Process 1 stays committed. Exit.

## 3. Data edit mapping

#### 1. Insert TB_R_PART_DAD_RESULT – Process 1: Every calculated part
- Source: TB_R_ACTUAL_DEMAND_SUMMARY (keys: PART_NO = Selected part, DEMAND_MONTH_YEAR = MONTH_FROM to MONTH_TO)

| Source field | Destination field | Description |
|---|---|---|
|  | PERIOD | Run month YYYYMM |
| PART_NO | PART_NO |  |
|  | MONTH_FROM | First month of the range |
|  | MONTH_TO | Month before the run month |
|  | NUM_OF_MONTH | N (system master) |
| MAD | TOTAL_MAD | SUM(MAD) of the part within the range (all buyer / PD / order type rows) |
|  | AVG_MAD | TOTAL_MAD / NUM_OF_MONTH (2 decimals) |
|  | MIN_MAD | TB_M_PART_CANDIDATE.MIN_MAD |
|  | OLD_STATUS | TB_M_PART_CANDIDATE.PART_STATUS before the run |
|  | NEW_STATUS | 'Active' if AVG_MAD >= MIN_MAD, otherwise 'Inactive' |
|  | CREATED_BY | Batch user ID (login user when manual) |
|  | CREATED_DT | Server system date and time |

#### 2. Update TB_M_PART_CANDIDATE – Process 1: Parts whose status changes
- Source: TB_R_PART_DAD_RESULT (keys: NEW_STATUS = <> OLD_STATUS)
- Destination keys: PART_NO = Calculated part

| Source field | Destination field | Description |
|---|---|---|
|  | PART_NO | Key, not changed |
|  | PART_NAME | Not changed |
|  | MIN_MAD | Not changed |
|  | PCS_CASE | Not changed |
|  | MAX_CASE_DAY | Not changed |
|  | TOTAL_PCS_DAY | Not changed |
| NEW_STATUS | PART_STATUS | Active / Inactive |
|  | LAST_SOURCE | Set 'CALC' |
|  | LAST_UPLOAD_ID | Not changed |
|  | CREATED_BY | Not changed |
|  | CREATED_DT | Not changed |
|  | CHANGED_BY | Batch user ID (login user when manual) |
|  | CHANGED_DT | Server system date and time |

#### 3. Insert TB_H_PART_CANDIDATE – Process 1: Status change - history
- Source: TB_R_PART_DAD_RESULT (keys: NEW_STATUS = <> OLD_STATUS)

| Source field | Destination field | Description |
|---|---|---|
|  | HIST_ID | Auto (identity) |
|  | PART_NO | Part of the event |
|  | PERIOD | Run month YYYYMM |
|  | EVENT_TYPE | 'CALC' |
|  | SOURCE | 'BATCH' |
|  | UPLOAD_ID | NULL |
|  | DEST_CODE | NULL |
| ORDER_TYPE | ORDER_TYPE | Order Type of the destination row for MAPPING; NULL for other events |
|  | FIELD_NAME | 'PART_STATUS' |
|  | OLD_VALUE | OLD_STATUS |
|  | NEW_VALUE | NEW_STATUS |
|  | REMARK | 'Average MAD <AVG_MAD> vs Min MAD <MIN_MAD>' |
|  | CREATED_BY | Batch user ID (login user when manual) |
|  | CREATED_DT | Server system date and time |

#### 4. Insert Log – Process 1: One record per run attempt
- Source: Result of this run

| Source field | Destination field | Description |
|---|---|---|
|  | BATCH_ID | 'DAD_CALC' |
|  | RUN_TYPE | SCHEDULE / RETRY / MANUAL |
|  | RETRY_NO | 0 for the scheduled run, 1-3 for the auto retries |
|  | STATUS | SUCCESS / FAILED |
|  | DATA_DT | Max CREATE_DT of TB_R_ACTUAL_DEMAND_SUMMARY (NSP) used by this run (only when SUCCESS); the trigger compares new data with it |
|  | MESSAGE | Error message when FAILED |
|  | START_DT | Start date and time |
|  | END_DT | End date and time; END_DT of the latest SUCCESS = last success date |

#### 5. Delete TB_M_PART_CANDIDATE_DEST – Process 2: Rows of the new period, if any
- Source: TB_M_PART_CANDIDATE_DEST (keys: PERIOD = New period (manual re-run only))
- Destination keys: PERIOD = New period

| Source field | Destination field | Description |
|---|---|---|
|  | PART_NO | Row is deleted |
|  | PERIOD | Row is deleted |
|  | DEST_CODE | Row is deleted |
| ORDER_TYPE | ORDER_TYPE | Key of the row to delete |
|  | CASE_DAY | Row is deleted |
|  | CREATED_BY | Row is deleted |
|  | CREATED_DT | Row is deleted |
|  | CHANGED_BY | Row is deleted |
|  | CHANGED_DT | Row is deleted |

#### 6. Insert TB_M_PART_CANDIDATE_DEST – Process 2: One row per kept destination
- Source: TB_R_ACTUAL_DEMAND_SUMMARY (keys: PART_NO = Active part, DEMAND_MONTH_YEAR = Range of months)

| Source field | Destination field | Description |
|---|---|---|
| PART_NO | PART_NO |  |
|  | PERIOD | New period (run month YYYYMM) |
| GROUPING_BUYER_CD + GROUPING_PD_CD | DEST_CODE | 7-digit destination code; must exist in TB_M_H0125_DESTINATION |
| Order Type | ORDER_TYPE | Order Type of the row ('**', 'C', '9', 'V'; default '**') |
| MAD | CASE_DAY | Allocated Case/Day from SUM(MAD) of the destination (see 4.6) |
|  | CREATED_BY | Batch user ID (login user when manual) |
|  | CREATED_DT | Server system date and time |
|  | CHANGED_BY | Same as CREATED_BY |
|  | CHANGED_DT | Server system date and time |

#### 7. Update TB_M_PART_CANDIDATE – Process 2: Sync Status
- Source: Parts whose mapping differs from the previous period
- Destination keys: PART_NO = Changed part

| Source field | Destination field | Description |
|---|---|---|
|  | PART_NO | Key, not changed |
|  | PART_NAME | Not changed |
|  | MIN_MAD | Not changed |
|  | PCS_CASE | Not changed |
|  | MAX_CASE_DAY | Not changed |
|  | TOTAL_PCS_DAY | Not changed |
|  | PART_STATUS | Not changed |
|  | LAST_SOURCE | Set 'CALC' |
|  | LAST_UPLOAD_ID | Not changed |
|  | CREATED_BY | Not changed |
|  | CREATED_DT | Not changed |
|  | CHANGED_BY | Batch user ID (login user when manual) |
|  | CHANGED_DT | Server system date and time |

#### 8. Insert TB_H_PART_CANDIDATE – Process 2: Mapping change - history
- Source: Parts whose mapping differs from the previous period

| Source field | Destination field | Description |
|---|---|---|
|  | HIST_ID | Auto (identity) |
|  | PART_NO | Part of the event |
|  | PERIOD | New period |
|  | EVENT_TYPE | 'MAPPING' |
|  | SOURCE | 'BATCH' |
|  | UPLOAD_ID | NULL |
|  | DEST_CODE | Destination added, changed or removed |
| ORDER_TYPE | ORDER_TYPE | Order Type of the destination row for MAPPING; NULL for other events |
|  | FIELD_NAME | 'CASE_DAY' |
|  | OLD_VALUE | Case/Day of the previous period (NULL when added) |
|  | NEW_VALUE | Calculated Case/Day (NULL when removed) |
|  | REMARK | NULL |
|  | CREATED_BY | Batch user ID (login user when manual) |
|  | CREATED_DT | Server system date and time |

#### 9. Insert Log – Process 2: One record per run attempt
- Source: Result of this run

| Source field | Destination field | Description |
|---|---|---|
|  | BATCH_ID | 'MAPPING_CALC' |
|  | RUN_TYPE | SCHEDULE / RETRY / MANUAL |
|  | RETRY_NO | 0 for the scheduled run, 1-3 for the auto retries |
|  | STATUS | SUCCESS / FAILED |
|  | DATA_DT | Max CREATE_DT of TB_R_ACTUAL_DEMAND_SUMMARY (NSP) used by this run (only when SUCCESS); the trigger compares new data with it |
|  | MESSAGE | Error message when FAILED |
|  | START_DT | Start date and time |
|  | END_DT | End date and time; END_DT of the latest SUCCESS = last success date |

#### 10. Insert TB_H_STG_APPOLE_KANBAN – SP_STG_WRITE (KANBAN): changed Pcs/Case or Max Case/Day of an Active part, Candidate -> Active, part of a new period; header 5 when only the destinations changed (when the key has no unsent row yet)
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Identity |
| PERIOD | PERIOD | Period of the part row |
| - | ACTION | 'ADD' (new part, new period) / 'EDIT' / 'KEEP' (header 5) |
| PART_STATUS | PART_STATUS | Status of the part in the period |
| - | OPERATOR_ID | 'P6' |
| PART_NO | PART_NO | With "-" |
| PART_NAME | PART_NAME | From TB_M_PART_CANDIDATE |
| PCS_CASE | SHIPPING_BOX_QTY | Value after the change |
| MAX_CASE_DAY | MAX_SHIPPING_BOX_QTY | Value after the change |
| - | MAX_ALLOWANCE_QTY | PCS_CASE x MAX_CASE_DAY |
| - | OPERATION_TYPE | 1 Max down / 2 up / 3 same / 4 never sent, against the last Max sent (same period, else the latest earlier period); 5 header |
| - | SOURCE | 'SCREEN' / 'UPLOAD' / 'BATCH' (caller) |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD, else NULL |
| - | SYNC_STATUS | '0' |
| - | SYNC_DT | NULL |
| - | CREATED_BY | Login user (XD05: batch user ID) |
| - | CREATED_DT | Server date-time |
| - | CHANGED_BY | NULL |
| - | CHANGED_DT | NULL |

#### 11. Insert TB_H_STG_APPOLE_EXPORT – SP_STG_WRITE (EXPORT): one row per added, changed or removed destination + order type (when the key has no unsent row yet)
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Identity |
| PERIOD | PERIOD |  |
| PART_NO | NSP_PART_NO | With "-" |
| DEST_CODE | DEST_CODE | 7 digits |
| - | ACTION | 'ADD' / 'EDIT' / 'DELETE' |
| PART_NO | PART_NO | Without "-" |
| DEST_CODE | BUYER_PD | 5-2 format |
| ORDER_TYPE | ORDER_TYPE |  |
| - | TRANSPORT_CODE | '2' |
| CASE_DAY | MAX_SHIPPING_BOX_RCS | Value after the change; 0 for DELETE |
| - | SOURCE | 'SCREEN' / 'UPLOAD' / 'BATCH' (caller) |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD, else NULL |
| - | SYNC_STATUS | '0' |
| - | SYNC_DT | NULL |
| - | CREATED_BY | Login user (XD05: batch user ID) |
| - | CREATED_DT | Server date-time |
| - | CHANGED_BY | NULL |
| - | CHANGED_DT | NULL |

#### 12. Insert TB_H_STG_GTOPAS – SP_STG_WRITE (EXPORT branch): the destination appears or disappears for the part and GTOPAS does not have that state yet (when the key has no unsent row yet)
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Identity |
| PERIOD | PERIOD |  |
| - | ACTION | 'ADD' / 'DELETE' |
| - | DEPOT_CODE | '01' |
| PART_NO | P_NO | With "-" |
| DEST_CODE | DESTINATION_CODE |  |
| - | MAKER_CODE | 'A' |
| - | DOMESTIC_OVERSEAS | '2' |
| - | TOPAS_ORDER_TYPE | '3' |
| - | ORDER_TRANSPORTATION_CODE | '2' |
| - | SOURCE | 'SCREEN' / 'UPLOAD' / 'BATCH' (caller) |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD, else NULL |
| - | SYNC_STATUS | '0' |
| - | SYNC_DT | NULL |
| - | CREATED_BY | Login user (XD05: batch user ID) |
| - | CREATED_DT | Server date-time |
| - | CHANGED_BY | NULL |
| - | CHANGED_DT | NULL |

#### 13. Update TB_H_STG_APPOLE_KANBAN – SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | ACTION | 'EDIT' (ADD when the key was not sent in the period) |
| - | PART_STATUS | Status of the part |
| - | SHIPPING_BOX_QTY | New Pcs/Case |
| - | MAX_SHIPPING_BOX_QTY | New Max Case/Day |
| - | MAX_ALLOWANCE_QTY | Pcs/Case x Max Case/Day |
| - | OPERATION_TYPE | Again against the last Max sent (a header 5 becomes 1 to 4) |
| - | SOURCE | Caller of the last change |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD |
| - | CHANGED_BY | Login user (XD05: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 14. Delete TB_H_STG_APPOLE_KANBAN – SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period (Kanban: also the header 5 when no Export row of the part + period waits)
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Unsent row (SYNC_STATUS 0) of the key |

#### 15. Update TB_H_STG_APPOLE_EXPORT – SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | ACTION | 'ADD' / 'EDIT' / 'DELETE' against the last value sent |
| - | MAX_SHIPPING_BOX_RCS | New Case/Day; 0 for DELETE |
| - | SOURCE | Caller of the last change |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD |
| - | CHANGED_BY | Login user (XD05: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 16. Delete TB_H_STG_APPOLE_EXPORT – SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Unsent row (SYNC_STATUS 0) of the key |

#### 17. Update TB_H_STG_GTOPAS – SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | ACTION | 'ADD' / 'DELETE' (what the master needs) |
| - | SOURCE | Caller of the last change |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD |
| - | CHANGED_BY | Login user (XD05: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 18. Delete TB_H_STG_GTOPAS – SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period
- Source: XD05 process 1 / 2 (SP_STG_WRITE, SOURCE BATCH)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Unsent row (SYNC_STATUS 0) of the key |

#### 19. Update TB_H_STG_GTOPAS – Rows of the new Current period with SYNC_STATUS 0
- Source: XD05 process 3 Period Rollover

| Source field | Destination field | Description |
|---|---|---|
| - | SYNC_STATUS | '1' |
| - | SYNC_DT | Time of the [Sync] click / of the rollover: one value for every row of the run |
| - | CHANGED_BY | Login user (rollover: batch user ID) |
| - | CHANGED_DT | Server date-time |

## 4. Function description

One batch with two processes run in sequence: process 1 sets the part status from the average MAD (4.1 - 4.4); process 2 creates the destination mapping of the new period for the Active parts (4.5 - 4.8). Range of months and schedule are set in the system master (not explained in this document).

### 4.1 Process 1 - Average MAD

- Range: the N months before the run month (N from the system master). Example: run in Oct 2026 with N = 6 -> 202604 to 202609.
- Monthly MAD of a part = sum of MAD of all its rows in that month (all buyer codes, PD codes and order types N + S).
- AVG_MAD = total MAD of the range / N. The divisor is always N, whatever the data: a month without data counts as 0.
- A part without any demand row in the range gets AVG_MAD = 0.
- AVG_MAD is kept with 2 decimals and compared as it is (no rounding).

### 4.2 Process 1 - Status Rule

| Condition | New status |
|---|---|
| AVG_MAD >= MIN_MAD | Active |
| AVG_MAD < MIN_MAD | Inactive |

- Possible changes: Candidate -> Active / Inactive, Inactive -> Active, Active -> Inactive.
- Parts calculated: every part with a row in the Current period, and a part registered for the next period before day D (its next row exists already). A part takes effect from the period it is registered.
- The batch may overwrite a status changed manually by the user. The user may still change the status again afterwards by screen or upload.

### 4.3 Process 1 - Saving

- One record per calculated part is inserted into TB_R_PART_DAD_RESULT (also when the status does not change).
- Only parts whose status changes are updated in TB_M_PART_CANDIDATE (PART_STATUS, LAST_SOURCE = CALC, CHANGED_BY / CHANGED_DT) and get a history record (event CALC, source BATCH).
- Staging: process 1 calls SP_STG_WRITE (Kanban ADD) for every part of the new period, Inactive included, so the part stays in the AP POLE Kanban. OPERATION_TYPE compares the new Max with the Max sent for the previous period: 1 down, 2 up, 3 same, 4 never sent. PART_STATUS of the row is the new status.
- All-or-nothing: any error rolls back the whole run.
- Every status change is written to TB_H_PART_CANDIDATE (FIELD_NAME PART_STATUS, OLD_VALUE / NEW_VALUE, CREATED_DT = run date-time). An Inactive part gets EXPORT DELETE (0) rows for its destinations still > 0 in the previous period (process 2), so AP POLE gets Buyer-PD 0 and GTOPAS deletes the rows at the Period Rollover.

### 4.4 Process 1 - Retry and Manual Trigger

- A failed run is retried automatically up to 3 times by the scheduler (RUN_TYPE = RETRY, RETRY_NO 1-3 in the Log).
- After the 3rd failed retry, [Run calculation] is enabled on the Kanban Crossdock Master tab of XD01 (RUN_TYPE = MANUAL).
- The last success date (END_DT of the latest SUCCESS record in the Log) is shown on the Kanban Crossdock Master tab of XD01.

### 4.5 Process 2 - Destinations and Result MAD

- Only Active parts of TB_M_PART_CANDIDATE are calculated.
- Range: the N months before the run month (N from the system master).
- Destination code = GROUPING_BUYER_CD + GROUPING_PD_CD (7 digits). It must exist in TB_M_H0125_DESTINATION; otherwise the run fails (all-or-nothing).
- Result MAD = sum of MAD of the part for that destination within the range; order types N and S are summed. Destinations with result MAD 0 are not used.

### 4.6 Process 2 - Case/Day Allocation

1. Sort the destinations of the part by result MAD, largest first.
2. Keep at most Max Case/Day destinations (the ones with the largest result MAD); the others are not mapped.
3. Target = result MAD / sum of result MAD of the kept destinations x Max Case/Day. Same as the corrected formula of the simulation file: P10 / SUM(P10:P13) x N10 with fixed ranges.
4. Case/Day = target rounded down, with a minimum of 1 per destination.
5. While the total is below Max Case/Day: +1 to the destination with the largest fraction (equal fraction: higher result MAD first).
6. While the total is above Max Case/Day (because of the minimum 1): -1 from the destination with the smallest fraction that still has more than 1 case.
7. Result: every kept destination has at least 1 case and the total equals Max Case/Day.

### 4.7 Process 2 - Saving

- The new period = run month. On a manual re-run in the same month, the rows of that period are replaced.
- After a successful run the new period is the ongoing period; the previous period becomes past (read only).
- Each part is compared with its mapping of the previous period for the history (TB_H_PART_CANDIDATE, event MAPPING, source BATCH, LAST_SOURCE = CALC). For the sync, process 2 calls SP_STG_WRITE per destination of the new period (Export ADD) and per destination of the previous period not mapped any more (Export DELETE 0).
- An Active part without result MAD has no row in the new period; the D/S user assigns it on the screen or by upload.
- All-or-nothing: any error rolls back the whole run; the previous period stays the ongoing period.

### 4.8 Process 2 - Retry and Manual Trigger

- The batch has its own scheduler (system master). A failed run is retried automatically up to 3 times (RUN_TYPE = RETRY, RETRY_NO 1-3 in the Log).
- After the 3rd failed retry, [Run calculation] is enabled on the Export Crossdock Master tab of XD01 (RUN_TYPE = MANUAL).
- The last success date (END_DT of the latest SUCCESS record in the Log) is shown on the Export Crossdock Master tab of XD01.

### 4.9 Next Period and Period Rollover (19-Nov)

- Schedule: day D of every month (system master, before the end of the month). The new period = the month after the run month (e.g. run 27-Nov -> period 202612 = Next).
- Process 1: TB_R_PART_DAD_RESULT for the Next period, and one Kanban Crossdock Master row per part for the Next period: PART_STATUS from the result, Pcs/Case and Max Case/Day copied from the Current period. The Current period is not changed.
- Process 2: Export Crossdock Master rows of the Next period for the Active parts (Order Type '**'). The Next period is view only on the screen.
- Process 3 (day 1, 00:10): Period Rollover: Next becomes Current, Current becomes Past. The GTOPAS staging rows of the new Current period with SYNC_STATUS 0 get SYNC_STATUS 1 and SYNC_DT = time of the rollover; then the RPA parent flow runs XD06 only (RUN_TYPE ROLLOVER). AP POLE got the period earlier by [Sync] (Effective Month / Year).
- The manual [Run calculation] of the screen re-runs the Next period.

| When | What |
|---|---|
| Day D (e.g. 27-Nov) | Process 1 + 2: period 202612 (Next) made |
| Day D - end of month | D/S adjusts the Current period only |
| Day 1 (1-Dec) | Process 3: 202612 Current, 202611 Past; XD06 for the changed combinations |

### 4.10 Period Rollover: send data (20-Nov)

- GTOPAS WVJA5204 has no period: it always shows the Current month, so the Next period reaches GTOPAS only at the Period Rollover.
- Rows taken: TB_H_STG_GTOPAS with SYNC_STATUS 0 and PERIOD = the new Current period (no date condition). Update (SP_STG_ROLLOVER): SYNC_STATUS 1, SYNC_DT = rollover time, CHANGED_BY / CHANGED_DT; Log of the run; start the RPA parent flow with RUN_TYPE ROLLOVER.
- Rows of the old period still Non Sync are not sent any more (every selection has a PERIOD condition).

### 4.11 Staging rows of XD05

- Every save calls the stored procedure SP_STG_WRITE once per changed value, in the same transaction and after the master tables are updated. A save without a changed value writes nothing.
- Process 1 / 2 on day D: Kanban ADD (Pcs/Case, Max) for every part of the new period, OPERATION_TYPE against the Max sent for the previous period (AP POLE keeps the previous Effective Month active until a newer one comes). Active part: Export ADD per destination; DELETE (0) for a destination of the previous period not mapped any more. Inactive part: Export DELETE (0) per destination still > 0 in the previous period; in the later periods no row (AP POLE keeps the 0). GTOPAS rows only for a destination that appears or disappears. SOURCE BATCH, CREATED_BY batch user ID.
- A part registered for the next period before day D keeps its next row; XD05 writes no second row for it. A Candidate part writes no staging row.
- Process 3 Period Rollover: refer 4.10.
- One unsent row per key: a key has at most one row with SYNC_STATUS 0. A new change of the key updates that row (value, ACTION, OPERATION_TYPE, CHANGED_BY / CHANGED_DT); a change back to the value already sent for the period deletes it (nothing to send); a sent row (SYNC_STATUS 1) is never changed, the next change inserts a new row. Keys: Kanban PERIOD + PART_NO; Export PERIOD + NSP_PART_NO + DEST_CODE + ORDER_TYPE; GTOPAS PERIOD + P_NO + DESTINATION_CODE. TB_H_PART_CANDIDATE keeps every change.
- Rules and simulation: deliverables/function_list_v2/erd/proposal_staging_sync (Proposal_Tables_Staging_Per_Target.xlsx, simulation/Staging_Header_Order.html, simulation/Staging_Per_Target_Full_Flow_Simulation.xlsx).

## 5. Logging messages

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Process 1: Batch start | Batch is called | Info | DAD volume calculation started (<RUN_TYPE>, retry <RETRY_NO>). Range <MONTH_FROM> - <MONTH_TO>. | system: Write the log.; user: - |
| LOG2 | Process 1: Batch end | Batch finishes | Info | DAD volume calculation ended. Status <STATUS>, calculated <COUNT>, status changed <CHANGED>. | system: Write the log.; user: - |
| LOG3 | Process 1: Range of months | Range is not set in the system master | Error | Range of months for the DAD volume calculation is not set. | system: Stop. STATUS = FAILED.; user: User contact PIC |
| LOG4 | Process 1: Part skipped | Part registered for a later period | Info | Part No <PART_NO> skipped: registered for period <PERIOD>. | system: Continue.; user: - |
| LOG5 | Process 1: Save | Insert / update fails | Error | Cannot save the calculation of Part No <PART_NO>: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |
| LOG6 | Process 1: Retry exhausted | Scheduled run and 3 retries failed | Warning | DAD volume calculation failed 3 times. Manual run is enabled on Kanban Crossdock Master. | system: Enable [Run calculation] on Kanban Crossdock Master.; user: Check the cause, then click [Run calculation]. |
| LOG7 | Process 1: Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |
| LOG8 | Process 2: Batch start | Batch is called | Info | Mapping destination calculation started (<RUN_TYPE>, retry <RETRY_NO>). Period <PERIOD>, range <MONTH_FROM> - <MONTH_TO>. | system: Write the log.; user: - |
| LOG9 | Process 2: Batch end | Batch finishes | Info | Mapping destination calculation ended. Status <STATUS>, parts <COUNT>, mapping changed <CHANGED>. | system: Write the log.; user: - |
| LOG10 | Process 2: Range of months | Range is not set in the system master | Error | Range of months for the mapping destination calculation is not set. | system: Stop. STATUS = FAILED.; user: User contact PIC |
| LOG11 | Process 2: Destination check | Destination code not in TB_M_H0125_DESTINATION | Error | Destination code <DEST_CODE> of Part No <PART_NO> not found in TB_M_H0125_DESTINATION. | system: Roll back. STATUS = FAILED. Retry.; user: Register the destination in TB_M_H0125_DESTINATION, then run again. |
| LOG12 | Process 2: Destinations limited | More destinations than Max Case/Day | Info | Part No <PART_NO>: <COUNT> destinations, limited to Max Case/Day <MAX>. | system: Continue.; user: - |
| LOG13 | Process 2: Save | Insert / update fails | Error | Cannot save the mapping of Part No <PART_NO>, period <PERIOD>: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |
| LOG14 | Process 2: Retry exhausted | Scheduled run and 3 retries failed | Warning | Mapping destination calculation failed 3 times. Manual run is enabled on Export Crossdock Master. | system: Enable [Run calculation] on Export Crossdock Master.; user: Check the cause, then click [Run calculation]. |
| LOG15 | Process 2: Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |

## 6. Appendix

Calculation examples (process 1 and process 2), rounding and limit examples: see sheet Sample Input.

## 7. Tables

#### TB_R_PART_DAD_RESULT (transaction, proposed)
Result of the DAD Volume Calculation, one record per calculated part and period. Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PERIOD | CHAR(6) | Y | N | Period of the result = the new (Next) period, month after the run month (19-Nov) |
| PART_NO | VARCHAR(TBD) | Y | N | Part number |
| MONTH_FROM | CHAR(6) |  | N | First month of the range, YYYYMM |
| MONTH_TO | CHAR(6) |  | N | Last month of the range, YYYYMM |
| NUM_OF_MONTH | INT |  | N | Number of months of the range (divisor of the average) |
| TOTAL_MAD | NUMBER(TBD,2) |  | N | Sum of MAD of the part over the range |
| AVG_MAD | NUMBER(TBD,2) |  | N | TOTAL_MAD / NUM_OF_MONTH |
| MIN_MAD | INT |  | N | Min MAD of the part at calculation time (snapshot) |
| OLD_STATUS | VARCHAR(TBD) |  | N | Part status before the calculation |
| NEW_STATUS | VARCHAR(TBD) |  | N | Active (AVG_MAD >= MIN_MAD) / Inactive (AVG_MAD < MIN_MAD) |
| CREATED_BY | VARCHAR(TBD) |  | N | Batch user ID |
| CREATED_DT | DATETIME |  | N | Date and time of the calculation |

#### TB_M_PART_CANDIDATE (transaction, existing)
Kanban Crossdock Master: one record per part and calculation period (19-Nov; before: one record per part).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) | Y | N | Calculation period YYYYMM: one row per part and period. The first row of a part is the period it is registered in (Add Part: the ongoing period or the next one); the part takes effect from it. Current: screen and upload; Next: made by XD05 on day D, view only until day 1; Past: view only |
| PART_NAME | VARCHAR(TBD) |  | N | Retrieved from TB_M_PART_MASTER by PART_NO |
| MIN_MAD | INT |  | N | Minimum MAD (mandatory); reference compared with the average MAD of the DAD Volume Calculation |
| PCS_CASE | INT |  | N | Pieces per case (> 0) |
| MAX_CASE_DAY | INT |  | N | Total Case/Day of the part (> 0); limit of the mapping |
| TOTAL_PCS_DAY | INT |  | N | PCS_CASE x MAX_CASE_DAY |
| PART_STATUS | VARCHAR(TBD) |  | N | Candidate / Active / Inactive. Candidate -> Active: XD05 (new period) or Procurement on the screen (ongoing period). Active <-> Inactive: XD05 or Procurement (screen, upload). No part goes back to Candidate |
| LAST_SOURCE | VARCHAR(TBD) |  | N | CALC / SCREEN / UPLOAD |
| LAST_UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload that last changed the record |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_R_ACTUAL_DEMAND_SUMMARY (transaction, existing)
Actual demand summary replicated from DB Surrounding to NSP (same columns). Key (PK) proposed from the data; types follow the source table.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| GROUPING_BUYER_CD | VARCHAR(5) | Y | N | Grouping buyer code, e.g. 9722D. With GROUPING_PD_CD it forms the 7-digit destination code |
| GROUPING_PD_CD | VARCHAR(2) | Y | N | Grouping PD code, e.g. 10 |
| ORDER_TYPE_GROUP | CHAR(1) | Y | N | Order type group: N / S (both are summed by Crossdock) |
| DEMAND_MONTH_YEAR | CHAR(6) | Y | N | Demand month YYYYMM, e.g. 202604 |
| PART_NO | VARCHAR(TBD) | Y | N | Part number |
| MAD | NUMBER(TBD,2) |  | Y | Monthly average demand of the row; used by Crossdock |
| DAD | NUMBER(TBD,2) |  | Y | Daily average demand (not used by Crossdock) |
| CREATE_DT | TIMESTAMP |  | Y | Created date and time (from source) |
| CREATE_BY | VARCHAR(TBD) |  | Y | Created by (from source) |
| UPDATE_DT | TIMESTAMP |  | Y | Updated date and time (from source) |
| UPDATE_BY | VARCHAR(TBD) |  | Y | Updated by (from source) |
| N01_QTY | NUMBER |  | Y | Quantity month N-1 (not used by Crossdock) |
| N02_QTY | NUMBER |  | Y | Quantity month N-2 (not used by Crossdock) |
| N03_QTY | NUMBER |  | Y | Quantity month N-3 (not used by Crossdock) |
| N04_QTY | NUMBER |  | Y | Quantity month N-4 (not used by Crossdock) |
| N05_QTY | NUMBER |  | Y | Quantity month N-5 (not used by Crossdock) |
| N06_QTY | NUMBER |  | Y | Quantity month N-6 (not used by Crossdock) |
| NUM_OF_OLD_PART_NO | NUMBER |  | Y | Number of old part numbers (not used by Crossdock) |
| NUM_OF_WORKINGDAY_6M | NUMBER |  | Y | Working days in 6 months (not used by Crossdock) |
| EM_MS_FLAG | CHAR(1) |  | Y | EM / MS flag (not used by Crossdock) |

#### TB_H_PART_CANDIDATE (history, proposed)
History of every change of a crossdock part for the History setting of XD01 (Add / Edit by screen or upload, mapping changes, status changes and mappings made by the calculation batches). The sync to GTOPAS / AP POLE is not recorded here: it is in the staging tables (TB_H_STG_APPOLE_KANBAN, TB_H_STG_APPOLE_EXPORT, TB_H_STG_GTOPAS) (22-Nov). No retention limit.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM of the changed row (every event; Kanban and Export Crossdock Master are per period, 20-Nov) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
| ORDER_TYPE | VARCHAR(2) |  | Y | Order Type of the destination row for MAPPING (with DEST_CODE); NULL for other events (20-Nov) |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, CASE_DAY |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (batch user ID for BATCH) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

#### TB_H_STG_APPOLE_KANBAN (history, proposed)
AP POLE Kanban rows in the format of the upload file LLM9Q910, one row per Kanban change of a part + period (one unsent row at a time: a new change updates it), plus the header row (OPERATION_TYPE 5) when only the destinations changed. Written by SP_STG_WRITE (XD01, XD02, XD05); SYNC_STATUS and SYNC_DT set by SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_KANBAN and V_APPOLE_UPLOAD_EXPORT.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| STG_ID | BIGINT | Y | N | Running number: order of the inserts |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM. FK1 (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE. File column Effective Month / Year = MM/YYYY of PERIOD, made by the view (not stored) |
| ACTION | VARCHAR(6) |  | N | ADD (new part, new period) / EDIT (Pcs/Case or Max changed) / KEEP (header written by an Export save, Kanban unchanged) |
| PART_STATUS | VARCHAR(10) |  | N | Active / Inactive in the period when the row is written (an Inactive part stays in the AP POLE Kanban) |
| OPERATOR_ID | CHAR(2) |  | N | Always P6. File / screen column: Operator ID. Default 'P6' |
| PART_NO | VARCHAR(TBD) |  | N | Part number with "-" (NSP format); FK1. File / screen column: Part No. |
| PART_NAME | VARCHAR(TBD) |  | N | From TB_M_PART_CANDIDATE at the insert. File / screen column: Part Name |
| SHIPPING_BOX_QTY | NUMBER(5) |  | N | Pcs/Case. File / screen column: Shipping Box Qty |
| MAX_SHIPPING_BOX_QTY | NUMBER(5) |  | N | Max Case/Day. File / screen column: Max Shipping Box Qty |
| MAX_ALLOWANCE_QTY | NUMBER(9) |  | N | Shipping Box Qty x Max Shipping Box Qty. File / screen column: Max Allowance Qty |
| OPERATION_TYPE | NUMBER(1) |  | N | Header of the part, set by SP_STG_WRITE at the save: 1 = Max down, 2 = Max up, 3 = Max same (only Pcs/Case changed, or a new period with the same Max), 4 = never sent, 5 = Kanban unchanged, only the destinations changed (ACTION KEEP). 1 to 4 against the last Max sent: same period, else the latest earlier period. Upload: 1 -> the Export rows of the part in EXPORT_PRE before KANBAN; 2, 3, 4 -> KANBAN then EXPORT_POST; 5 -> EXPORT_POST only, the row is not in the KANBAN file |
| SOURCE | VARCHAR(6) |  | N | SCREEN / UPLOAD / BATCH (XD05) |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD |
| SYNC_STATUS | CHAR(1) |  | N | 0 = to send (written or updated by SP_STG_WRITE), 1 = sent (SP_STG_SYNC at [Sync], SP_STG_ROLLOVER for GTOPAS). One row with 0 per key at a time: a new change of the key updates it. Default '0' |
| SYNC_DT | DATETIME2(0) |  | Y | Time of the [Sync] click (or of the Period Rollover), the same value for every row of that click: the RPA reads the rows of a run by SYNC_DT; [Re-send last Sync] = MAX(SYNC_DT); Last Sent on the screen = latest value |
| CREATED_BY | VARCHAR(20) |  | N | User of the save / upload, or XD05BATCH |
| CREATED_DT | DATETIME |  | N | Time of the insert (same transaction as the master update) |
| CHANGED_BY | VARCHAR(20) |  | Y | User of the save that updated the unsent row, of [Sync], or XD05BATCH (Period Rollover) |
| CHANGED_DT | DATETIME |  | Y | Time of that update |

#### TB_H_STG_APPOLE_EXPORT (history, proposed)
AP POLE Export rows in the format of the upload file LLM9Q880, one row per added, changed or removed destination + order type of a part + period (one unsent row per key: a new change updates it). Written by SP_STG_WRITE (XD01, XD03, XD05); SYNC_STATUS and SYNC_DT set by SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_EXPORT.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| STG_ID | BIGINT | Y | N | Running number: order of the inserts |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM. FK1 (NSP_PART_NO, PERIOD) -> TB_M_PART_CANDIDATE. File column Effective Month / Year = MM/YYYY of PERIOD, made by the view (not stored) |
| NSP_PART_NO | VARCHAR(TBD) |  | N | Part number with "-" (key back to NSP); FK1 |
| DEST_CODE | CHAR(7) |  | N | Destination code, 7 digits. No FK: a DELETE row points to a removed destination |
| ACTION | VARCHAR(6) |  | N | ADD / EDIT / DELETE (DELETE = Max Shipping Box (RCS) 0) |
| PART_NO | VARCHAR(TBD) |  | N | Part number without "-". File / screen column: Part No. |
| BUYER_PD | CHAR(8) |  | N | DEST_CODE in 5-2 format. File / screen column: Buyer-PD |
| ORDER_TYPE | VARCHAR(2) |  | N | '**', 'C', '9', 'V' (system master). File / screen column: Order Type |
| TRANSPORT_CODE | CHAR(1) |  | N | Always 2. File / screen column: Transport Code. Default '2' |
| MAX_SHIPPING_BOX_RCS | NUMBER(5) |  | N | Case/Day of the destination; 0 = delete. File / screen column: Max Shipping Box (RCS) |
| SOURCE | VARCHAR(6) |  | N | SCREEN / UPLOAD / BATCH (XD05) |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD |
| SYNC_STATUS | CHAR(1) |  | N | 0 = to send (written or updated by SP_STG_WRITE), 1 = sent (SP_STG_SYNC at [Sync], SP_STG_ROLLOVER for GTOPAS). One row with 0 per key at a time: a new change of the key updates it. Default '0' |
| SYNC_DT | DATETIME2(0) |  | Y | Time of the [Sync] click (or of the Period Rollover), the same value for every row of that click: the RPA reads the rows of a run by SYNC_DT; [Re-send last Sync] = MAX(SYNC_DT); Last Sent on the screen = latest value |
| CREATED_BY | VARCHAR(20) |  | N | User of the save / upload, or XD05BATCH |
| CREATED_DT | DATETIME |  | N | Time of the insert (same transaction as the master update) |
| CHANGED_BY | VARCHAR(20) |  | Y | User of the save that updated the unsent row, of [Sync], or XD05BATCH (Period Rollover) |
| CHANGED_DT | DATETIME |  | Y | Time of that update |

#### TB_H_STG_GTOPAS (history, proposed)
GTOPAS WVJA5204 rows: a part + destination to add or delete, written by SP_STG_WRITE only when the destination appears or disappears for the part (any order type) and GTOPAS does not have that state yet (one unsent row per key). Sent by [Sync] (Current period) or the Period Rollover (new Current period). Read by XD06.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| STG_ID | BIGINT | Y | N | Running number: order of the inserts |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM (GTOPAS has no period: [Sync] sends the Current period, the Period Rollover the new Current). FK1 (P_NO, PERIOD) -> TB_M_PART_CANDIDATE |
| ACTION | VARCHAR(6) |  | N | ADD / DELETE: the destination appears or disappears for the part (any order type). No row for a Case/Day change or for a state GTOPAS already has. File / screen column: Add / Delete (MT = DEL) |
| DEPOT_CODE | CHAR(2) |  | N | Always 01. File / screen column: Depot Code. Default '01' |
| P_NO | VARCHAR(TBD) |  | N | Part number with "-"; FK1. File / screen column: P/No. |
| DESTINATION_CODE | CHAR(7) |  | N | 7-digit code, the same in NSP and GTOPAS. File / screen column: Destination Code |
| MAKER_CODE | CHAR(1) |  | N | Always A. File / screen column: Maker Code. Default 'A' |
| DOMESTIC_OVERSEAS | CHAR(1) |  | N | Always 2. File / screen column: Domestic/Overseas. Default '2' |
| TOPAS_ORDER_TYPE | CHAR(1) |  | N | Always 3. File / screen column: TOPAS Order Type. Default '3' |
| ORDER_TRANSPORTATION_CODE | CHAR(1) |  | N | Always 2. File / screen column: Order Transportation Code. Default '2' |
| SOURCE | VARCHAR(6) |  | N | SCREEN / UPLOAD / BATCH (XD05) |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD |
| SYNC_STATUS | CHAR(1) |  | N | 0 = to send (written or updated by SP_STG_WRITE), 1 = sent (SP_STG_SYNC at [Sync], SP_STG_ROLLOVER for GTOPAS). One row with 0 per key at a time: a new change of the key updates it. Default '0' |
| SYNC_DT | DATETIME2(0) |  | Y | Time of the [Sync] click (or of the Period Rollover), the same value for every row of that click: the RPA reads the rows of a run by SYNC_DT; [Re-send last Sync] = MAX(SYNC_DT); Last Sent on the screen = latest value |
| CREATED_BY | VARCHAR(20) |  | N | User of the save / upload, or XD05BATCH |
| CREATED_DT | DATETIME |  | N | Time of the insert (same transaction as the master update) |
| CHANGED_BY | VARCHAR(20) |  | Y | User of the save that updated the unsent row, of [Sync], or XD05BATCH (Period Rollover) |
| CHANGED_DT | DATETIME |  | Y | Time of that update |

#### TB_M_PART_CANDIDATE_DEST (transaction, existing)
Export Crossdock Master: one record per part, calculation period, destination and order type.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number (FK to TB_M_PART_CANDIDATE) |
| PERIOD | CHAR(6) | Y | N | Calculation period YYYYMM, e.g. 202610; displayed as 'Oct 2026' |
| DEST_CODE | CHAR(7) | Y | N | Destination code (buyer code + PD code, 7 digits); exists in TB_M_H0125_DESTINATION |
| ORDER_TYPE | VARCHAR(2) | Y | N | Order Type of the row (system master: '**', 'C', '9', 'V'; default '**'). One row per part, period, destination and order type (19-Nov) |
| CASE_DAY | INT |  | N | Allocated Case/Day of the destination (> 0). Every add / change / removal calls SP_STG_WRITE (Export staging row) in the same transaction |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_M_H0125_DESTINATION (master, existing)
Destination Master (existing NSP table, read only). Only the listed columns are relevant; full structure: XD13 Destination Master (H0125) Sync.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| DESTINATION_CD | VARCHAR(7) | Y | N | Destination code, 7 digits (buyer code + PD code), e.g. 9722D10. Used by Crossdock |
| CUSTOMER_CD | VARCHAR(7) |  | N | Customer code (reference only) |
| ORDER_TRANSPORTATION_CD | VARCHAR(1) |  | N | Order transportation code (reference only) |
| BO_INSTRUCTION_CD | VARCHAR(1) |  | N | B/O instruction code (reference only) |
| DESTINATION_NAME_ENG | VARCHAR(50) |  | N | Destination name. Used by Crossdock (shown with the code) |
| REGION_CD | VARCHAR(2) |  | N | Region code (reference only) |
| COUNTRY_NAME_ENG | VARCHAR(36) |  | Y | Country name (reference only) |
| POSTAL_CD_ENG | VARCHAR(10) |  | Y | Postal code (reference only) |
| STATE_CD_ENG | VARCHAR(6) |  | Y | State code (reference only) |
| DESTINATION_ADDR1_ENG | VARCHAR(50) |  | N | Destination address 1 (reference only) |
| DESTINATION_ADDR2_ENG | VARCHAR(50) |  | Y | Destination address 2 (reference only) |
| CREATE_BY | VARCHAR(TBD) |  | Y | User who created the record |
| CREATE_DT | TIMESTAMP |  | Y | Created date and time |
| UPDATE_BY | VARCHAR(TBD) |  | Y | User who last updated the record |
| UPDATE_DT | TIMESTAMP |  | Y | Last updated date and time |

## Sample Input

**Sample calculation - DAD Volume Calculation (process 1 and process 2)**

- Process 1: Run in Oct 2026 with range = 6 months (system master) -> months 202604 to 202609, divisor 6.
- Process 1: Monthly MAD of a part = sum of MAD of all buyer code / PD code / order type (N + S) rows of the part in that month (TB_R_ACTUAL_DEMAND_SUMMARY).
- Process 2: Run in Oct 2026 with range = 6 months (system master) -> months 202604 to 202609; new period = 202610.
- Process 2: Result MAD of a destination = sum of MAD of the part for that buyer code + PD code (order types N + S) within the range (TB_R_ACTUAL_DEMAND_SUMMARY).
- Process 2: Target = result MAD / sum of result MAD of the destinations used x Max Case/Day.

### Process 1 - A. Monthly MAD per part (from TB_R_ACTUAL_DEMAND_SUMMARY)

| Part No | 202604 | 202605 | 202606 | 202607 | 202608 | 202609 | Total | Average (/6) |
|---|---|---|---|---|---|---|---|---|
| 52119BZV60 | 498.67 | 473.83 | 498.32 | 521.17 | 572.16 | 526.34 | 3090.49 | 515.08 |
| PART-B | 600 | 600 | 0 | 600 | 0 | 600 | 2400 | 400 |
| PART-C | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### Process 1 - B. Scenarios

| No | Part No | Status before | Min MAD | Period registered | Average MAD | Result |
|---|---|---|---|---|---|---|
| N1 | 52119BZV60 | Candidate | 500 | 202609 | 515.08 | 515.08 >= 500 -> Active. History CALC/BATCH. Sync Status not changed. |
| N2 | 52119BZV60 | Active | 600 | 202609 | 515.08 | 515.08 < 600 -> Inactive. |
| N3 | 52119BZV60 | Inactive | 515 | 202609 | 515.08 | 515.08 >= 515 -> Active. |
| N4 | 52119BZV60 | Active | 500 | 202609 | 515.08 | Already Active: status not changed; result record still inserted, no history. |
| N5 | PART-B | Active | 500 | 202609 | 400 | Missing months count as 0 (divisor stays 6): 400 < 500 -> Inactive. |
| N6 | PART-C | Candidate | 0 | 202609 | 0 | No demand: average 0 >= Min MAD 0 -> Active. |
| N7 | PART-D | Candidate | 300 | 202609 |  | Registered for the next period after day D: not calculated in this run, no result record. |
| N8 | PART-E | Inactive | 300 | 202609 |  | Status was set to Inactive manually last week: the batch may overwrite it with the calculated status. |
| E1 | (all) |  |  |  |  | Database error while updating one part: whole run rolled back, Log FAILED, auto retry (max 3). |
| E2 | (all) |  |  |  |  | Scheduled run and 3 retries failed: [Run calculation] enabled in Kanban Crossdock Master; last success date unchanged. |

### Process 2 - A. Part 52119BZV60 (Active, Max Case/Day 16)

| Rank | Buyer code | PD code | Destination code | Result MAD | Ratio | Target | Rounded down (min 1) | +1 remainder | Case/Day |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9722D | 10 | 9722D10 | 1536.16 | 49.7% | 7.95 | 7 | +1 (0.95) | 8 |
| 2 | 98111 | 10 | 9811110 | 999.83 | 32.4% | 5.18 | 5 |  | 5 |
| 3 | 96182 | 01 | 9618201 | 448.66 | 14.5% | 2.32 | 2 |  | 2 |
| 4 | 97153 | 10 | 9715310 | 105.84 | 3.4% | 0.55 | 1 |  | 1 |
| Total |  |  |  | 3090.49 | 100% | 16.0 | 15 | 1 | 16 |

### Process 2 - B. Rounding and limit examples

| No | Case | Targets | Case/Day | Rule |
|---|---|---|---|---|
| R1 | Max 10, 4 destinations with equal MAD | 2.5 / 2.5 / 2.5 / 2.5 | 3 / 3 / 2 / 2 | Rounded down 2 each = 8; 2 left go +1 to the first two (equal fraction: higher result MAD / rank first). |
| R2 | Max 3, 5 destinations (MAD 500 / 300 / 100 / 60 / 40) | top 3 only: 1.67 / 1.00 / 0.33 | 1 / 1 / 1 | Limited to Max Case/Day destinations (top 3 by result MAD); each gets at least 1. |
| R3 | Max 5, 4 destinations (MAD 900 / 50 / 30 / 20) | 4.50 / 0.25 / 0.15 / 0.10 | 2 / 1 / 1 / 1 | Rounded down with min 1 = 4 + 1 + 1 + 1 = 7 > 5: take 1 from the destination with the smallest fraction that still has more than 1 case (repeat). |

### Process 2 - C. Scenarios

| No | Scenario | Expected result |
|---|---|---|
| N1 | Part 52119BZV60 (section A) | Period 202610 created: 9722D10 = 8, 9811110 = 5, 9618201 = 2, 9715310 = 1. Export staging ADD per destination (AP POLE Non Sync); GTOPAS rows only for the destinations that are new for the part; history MAPPING/BATCH per changed destination. |
| N2 | Active part without demand in the range | No destination row for 202610; the part is listed on Export Crossdock Master with Total Case/Day 0 (to be assigned by D/S). |
| N3 | Candidate or Inactive part | Not calculated (Active parts only). |
| N4 | Result equal to the mapping of the previous period | Rows inserted for the new period; Sync Status not changed; no history record. |
| N5 | Manual re-run in the same month | Rows of period 202610 deleted and calculated again (replace). |
| E1 | Destination code 9715310 not in TB_M_H0125_DESTINATION | Error: whole run rolled back (no new period), Log FAILED, auto retry (max 3). |
| E2 | Scheduled run and 3 retries failed | [Run calculation] enabled on Export Crossdock Master; last success date unchanged. |
