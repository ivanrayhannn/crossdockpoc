# Crossdock Sync with the Staging Table: Summary of Decisions (21-Nov-2026)

Input for the UISS update of XD01 / XD02 / XD03 (Kanban and Export Crossdock Master), XD05 (DAD calculation, Period Rollover),
XD06 (RPA GTOPAS) and XD07 (RPA AP POLE). Status: agreed in discussion, not yet in the UISS / DB Structure.

> Replaced by the staging per target (23-Nov) and the decision of 26-Nov: no run ID column, the run is SYNC_DT (time of the
> [Sync] click), SYNC_STATUS 0 / 1, one unsent row per key. See Proposal_Tables_Staging_Per_Target.xlsx and
> prepare_code/sql/crossdock_staging_sync.sql. This file stays as the record of 21-Nov.

References:
- Full flow simulation: https://claude.ai/artifact/34QuqNRQW79UK3M4ttMXeJ
- Staging scenarios: https://claude.ai/artifact/LGxUkmQQcvHZb8UGq5BgWF
- Table proposal: `Proposal_Tables_Staging_Sync.xlsx` (this folder)

---

## 1. Tables

### 1.1 TB_M_PART_CANDIDATE (Kanban Crossdock Master, PK PART_NO + PERIOD)
- **Removed:** SYNC_STATUS, GTOPAS_SYNC_DT, APPOLE_SYNC_DT, SYNC_RUN_ID. No sync column is left on the master.
- PART_STATUS: Candidate -> Active by **XD05** (Next period). Active -> Inactive and Inactive -> Active by **Procurement** on the Kanban Crossdock Master.

### 1.2 TB_M_PART_CANDIDATE_DEST (Export Crossdock Master, PK PART_NO + PERIOD + DEST_CODE + ORDER_TYPE)
- No new column. A removed destination is deleted from the master at once (no DELETE_FLAG); the staging keeps the DELETE row until it is sent.
- Every add / change / removal writes a row to the staging in the same transaction.

### 1.3 TB_H_PART_CANDIDATE (existing history)
- Kept as it is: history of the parent, one row per PART_NO + PERIOD, overwritten (update). Used for the screen history only, not by the RPA.

### 1.4 TB_H_PART_CANDIDATE_STG_SYNC (new, AP POLE and GTOPAS)
One row per changed value. Inserted by XD05, the screen save and the upload; updated only by [Sync] / [Re-send last Sync] / Period Rollover.

| No | Column | Type | Null | Description |
|---|---|---|---|---|
| 1 | HIST_ID | BIGINT (identity) | N | PK, order of the changes |
| 2 | PART_NO | VARCHAR(TBD) | N | FK1 (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE; NSP format with "-" |
| 2a | PART_NAME | VARCHAR(TBD) | N | Copied from TB_M_PART_CANDIDATE at the insert (Part Name of the Kanban upload file) |
| 3 | PERIOD | CHAR(6) | N | YYYYMM; Effective Month / Year of the AP POLE upload |
| 4 | PART_STATUS | VARCHAR(10) | N | Status of the part in this period when the row is written (Active / Inactive) |
| 5 | LEVEL_TYPE | VARCHAR(6) | N | KANBAN = parent (Kanban Crossdock Master), EXPORT = child (Export destination) |
| 6 | DEST_CODE | CHAR(7) | Y | EXPORT only. No FK (a DELETE row points to a removed destination) |
| 7 | ORDER_TYPE | VARCHAR(2) | Y | EXPORT only: `**`, C, 9, V |
| 8 | FIELD_NAME | VARCHAR(30) | N | KANBAN: PCS_CASE, MAX_CASE_DAY. EXPORT: CASE_DAY |
| 9 | ACTION | VARCHAR(6) | N | ADD / EDIT / DELETE |
| 10 | OLD_VALUE | VARCHAR(10) | Y | Value before the change; NULL on ADD |
| 11 | NEW_VALUE | VARCHAR(10) | Y | Value after the change; **0 on DELETE** |
| 12 | SOURCE | VARCHAR(6) | N | BATCH (XD05) / SCREEN / UPLOAD |
| 13 | UPLOAD_ID | VARCHAR(TBD) | Y | Only when SOURCE = UPLOAD |
| 14 | APPOLE_SYNC_STATUS | CHAR(1) | N | 0 Non Sync (default), 1 Sync, 2 Superseded |
| 15 | APPOLE_SYNC_DT | DATETIME | Y | Time of the [Sync] that sent the row |
| 16 | SEND_SEQ | NUMBER(1) | Y | Position against the Kanban file: 1 = Export before Kanban, 2 = Kanban, 3 = Export after Kanban |
| 17 | APPOLE_SYNC_RUN_ID | VARCHAR(14) | Y | AP POLE run ID YYYYMMDDHHMMSS |
| 18 | GTOPAS_SYNC_STATUS | CHAR(1) | Y | NULL = not for GTOPAS, 0 Non Sync, 1 Sync |
| 19 | GTOPAS_SYNC_DT | DATETIME | Y | Time of the [Sync] / Period Rollover that sent the row to GTOPAS |
| 20 | GTOPAS_SYNC_RUN_ID | VARCHAR(14) | Y | GTOPAS run ID |
| 21 | CREATED_BY | VARCHAR(20) | N | User of the save / upload, or XD05BATCH |
| 22 | CREATED_DT | DATETIME | N | Time of the insert |
| 23 | CHANGED_BY | VARCHAR(20) | Y | User of [Sync] / [Re-send last Sync] (XD05BATCH for the rollover) |
| 24 | CHANGED_DT | DATETIME | Y | Time of that update |

Indexes:
- IX1 (APPOLE_SYNC_STATUS, PERIOD, PART_NO)
- IX2 (APPOLE_SYNC_RUN_ID, PERIOD, SEND_SEQ, PART_NO)
- IX3 (PART_NO, PERIOD, LEVEL_TYPE, DEST_CODE, ORDER_TYPE, FIELD_NAME, HIST_ID)
- IX4 (GTOPAS_SYNC_STATUS, PERIOD, PART_NO)

Key of a change = PART_NO + PERIOD + LEVEL_TYPE + DEST_CODE + ORDER_TYPE + FIELD_NAME.

---

## 2. Insert rules (who writes the staging)

The insert is in the same transaction as the master update. A save without a value change writes no row.

| Source | Menu | LEVEL_TYPE | Rows inserted |
|---|---|---|---|
| XD05 process 1 (day D) | Kanban, Next period | KANBAN | ADD PCS_CASE and ADD MAX_CASE_DAY for **every** part of the new period, Inactive included (the part stays in the AP POLE Kanban) |
| XD05 process 2 (day D) | Export, Next period | EXPORT | Active part: ADD CASE_DAY per destination + order type. Inactive part: DELETE (OLD = Current value, NEW 0, GTOPAS 0) per destination of the previous period. A destination already set to 0 earlier is not carried: the new month has no Export row for it, so AP POLE has the part without that Buyer-PD |
| XD05 re-run (same day D) | Kanban + Export, Next | KANBAN, EXPORT | EDIT / ADD / DELETE against the Next values it replaces |
| User save / upload | Kanban Crossdock Master | KANBAN | EDIT PCS_CASE / MAX_CASE_DAY per changed field |
| User save / upload | Export Crossdock Master | EXPORT | ADD / EDIT / DELETE CASE_DAY per destination + order type |
| Procurement: Active -> Inactive | Kanban Crossdock Master | EXPORT | DELETE (NEW 0) for every destination; PART_STATUS column = Inactive. No row for the status itself |
| Procurement: Inactive -> Active | Kanban Crossdock Master | EXPORT | ADD for every destination mapped again; PART_STATUS column = Active |

PART_STATUS column: Active -> ADD / EDIT rows. Inactive -> the part stays in the AP POLE Kanban; every Export row of the part is DELETE with NEW_VALUE 0, so the Buyer-PD stays in AP POLE with 0.

### GTOPAS_SYNC_STATUS at the insert

| LEVEL_TYPE | ACTION | GTOPAS_SYNC_STATUS | Reason |
|---|---|---|---|
| KANBAN | ADD / EDIT | NULL | GTOPAS keeps no Pcs/Case or Max |
| EXPORT | ADD | 0 | Destination appears: GTOPAS Add |
| EXPORT | DELETE | 0 | Destination disappears (0): GTOPAS Delete |
| EXPORT | EDIT | NULL | Only Case/Day changes; nothing changes in GTOPAS |

APPOLE_SYNC_STATUS is always 0 at the insert.

---

## 3. [Sync] and RPA AP POLE (XD07)

### 3.1 Rows taken by NSP
- `APPOLE_SYNC_STATUS = 0`
- `CREATED_DT > LAST_SYNC_DATE_APPOLE` (saved by the last run) and `CREATED_DT <= time of the click` (HIST_ID <= the last HIST_ID at the click). Rows inserted while the run is made wait for the next [Sync].
- PERIOD = Current and Next.

### 3.2 Reduction per key
- AP POLE value = OLD_VALUE of the first row (smallest HIST_ID). NSP value = NEW_VALUE of the last row (largest HIST_ID).
- Direction (worked out at [Sync], not stored): ACTION of the last row DELETE -> Delete; no AP POLE value -> Add; smaller -> Down; bigger -> Up; equal -> nothing to send.
- Last row of each key -> APPOLE_SYNC_STATUS 1 with SEND_SEQ. Earlier rows of the key -> 2 Superseded. A key that ends on its first value -> 1 without SEND_SEQ.
- All rows taken get APPOLE_SYNC_DT, APPOLE_SYNC_RUN_ID, CHANGED_BY / CHANGED_DT. Then LAST_SYNC_DATE_APPOLE = time of the click.

### 3.3 SEND_SEQ (position against the Kanban file)

| SEND_SEQ | File | Rows |
|---|---|---|
| 1 | Export (LLM9Q880), before Kanban | EXPORT rows of a part **whose Max goes down** |
| 2 | Kanban (LLM9Q910) | Every KANBAN change and new part (Pcs/Case and Max in one row) |
| 3 | Export (LLM9Q880), after Kanban | EXPORT rows of every other part: Max goes up, new part, or no Kanban row (moves between destinations, deletes, Inactive) |

- AP POLE checks every uploaded row one by one (total Max Shipping Box (RCS) of the part <= Max Shipping Box Qty).
- Inside a file, the rows of a part going down / deleted come first, then the rows going up / added.
- Only a Max going down needs its destinations lowered before the Kanban row; everything else is safe after it.

### 3.4 Upload files (made by NSP from the stored templates; no download from AP POLE)
- Name: `<template>_<run ID>_<period>_<SEND_SEQ>.xls`, e.g. `LLM9Q880_20261127100000_202611_1.xls`. One file per period + SEND_SEQ; a file with no rows is not made.
- **LLM9Q910 Cross Dock Kanban Part Master:**
  - Effective Month / Year from PERIOD.
  - Operator ID **P6** (fixed).
  - Part No. **with "-"**, Part Name.
  - Shipping Box Qty = PCS_CASE, Max Shipping Box Qty = MAX_CASE_DAY, Max Allowance Qty = PCS_CASE x MAX_CASE_DAY. Pcs and Max are taken from TB_M_PART_CANDIDATE, so the row is complete even when only one of them changed.
  - Packing/Pallet Type ... Outer-Qty left empty.
- **LLM9Q880 Export Customer Cross Dock Master:**
  - Effective Month / Year.
  - Part No. **without "-"**.
  - Buyer-PD (5-2), Order Type.
  - Transport Code **2** (fixed).
  - Max Shipping Box (RCS) = NEW_VALUE (**0 for a removed destination or an Inactive part**).
  - Shipping Box Qty, Max Shipping Box by Part No., Max Allowance Qty, Packing/Pallet Type left empty.

### 3.5 Bot
- Uploads the files one at a time in the order of their names (Current period first, then Next) and waits for each result.
- Stops at the first failed file; the e-mail FAILED names the file.
- Writes nothing back to NSP. The result comes by e-mail (SUCCESS / FAILED / bot not started).
- [Re-send last Sync] runs the rows of the last APPOLE_SYNC_RUN_ID again in the same order. This is safe because the bot sets values; it does not add or subtract.

---

## 4. RPA GTOPAS (XD06)

- Trigger: [Sync] for the Current period, Period Rollover (XD05 process 3, day 1 00:10) for the new Current period.
- Rows taken: `GTOPAS_SYNC_STATUS = 0` and PERIOD = Current ([Sync]) or PERIOD = the period that becomes Current (rollover).
- Data for the bot: the distinct PART_NO of those rows; for each part every destination of TB_M_PART_CANDIDATE_DEST of that period with **CASE_DAY >= 1** (DEST_CODE distinct, order types together).
- Fixed values: Depot 01, Maker A, Dom/Os 2, TOPAS Order Type `*`, Trans 2.
- Compare with GTOPAS WVJA5204 (P/No. without "-" + Destination Code): in NSP only -> Add; in GTOPAS only -> Delete; both -> Keep.
- No date condition for GTOPAS (decided 21-Nov): status 0 already means not sent, so the rows written by XD05 on day D are never skipped by a [Sync] of the Current period before the rollover.
- Update: rows -> GTOPAS_SYNC_STATUS 1, GTOPAS_SYNC_DT, GTOPAS_SYNC_RUN_ID, CHANGED_BY / CHANGED_DT.
- No SEND_SEQ and no Superseded for GTOPAS: the bot compares the latest state.

---

## 5. Screen (Kanban / Export Crossdock Master)
- AP POLE Sync: Non Sync while the part + period has a staging row with APPOLE_SYNC_STATUS 0; else Sync. Last Sent AP POLE = latest APPOLE_SYNC_DT.
- GTOPAS Sync: Non Sync while the part + period has a staging row with GTOPAS_SYNC_STATUS 0; else Sync. Last Sent GTOPAS = latest GTOPAS_SYNC_DT.

---

## 6. Example (full flow simulation)
- Next month (Dec 2026 -> Jan 2027): a destination that is not in the new calculation (DUMMY-004 KOREA) or already 0 (DUMMY-003 KOREA) gets no Export row in the new month, so AP POLE of the new month has no Buyer-PD row for it.
- Day D 27-Nov 02:00, XD05:
  - 202612 Kanban rows HIST 101–108 (4 parts incl. Inactive DUMMY-003).
  - Export rows 109–115 (ADD, and DELETE KOREA 10 -> 0 for DUMMY-003).
- 27-Nov 09:00, D/S on DUMMY-001 202611: Max 12 -> 11 (116), JAPAN 6 -> 7 (117), KOREA 6 -> 4 (118).
- 27-Nov 10:00 [Sync], 4 files:
  1. `LLM9Q880_…_202611_1`: KOREA 4, then JAPAN 7.
  2. `LLM9Q910_…_202611_2`: Max 11.
  3. `LLM9Q910_…_202612_2`: Add part DUMMY-001..004.
  4. `LLM9Q880_…_202612_3`: Add Buyer-PD, DUMMY-003 KOREA 0.
  - All rows OK.
- 01-Dec 00:10 Rollover: XD06 takes HIST 109–115.
  - Compare: DUMMY-001 TAIWAN Add, DUMMY-002 JAPAN / USA Add, DUMMY-003 KOREA Delete, others Keep.

---

## 7. Decided on 21-Nov (after the open points)
1. The last sync date of AP POLE is a System Master parameter **LAST_SYNC_DATE_APPOLE**, saved by [Sync] / [Re-send last Sync]. GTOPAS has no last sync date.
2. GTOPAS takes the rows with **GTOPAS_SYNC_STATUS = 0 and PERIOD** (Current for [Sync], the new Current period for the rollover), with no date condition.
3. Inactive -> Active: **Procurement** maps the destinations again by hand on the screen (EXPORT ADD rows, CREATED_BY Procurement). The part record stays in the AP POLE Kanban while it is Inactive.
4. Rows of the Current period still Non Sync at the Period Rollover (changed but no [Sync] before day 1) are **not sent later and keep their status**. They are never taken again because every selection has a PERIOD condition: AP POLE takes Current and Next only, GTOPAS takes Current ([Sync]) or the new Current (rollover). On the screen the Past period can show Non Sync for these parts (view only). GTOPAS is aligned anyway by the rollover with the destinations of the new period.
5. Total Case/Day > Max Case/Day of the part (same period): **error on save**, nothing is saved. Checked at the screen save of the Kanban Crossdock Master (new Max >= total Case/Day of the destinations), the screen save of the Export Crossdock Master (total Case/Day incl. a new destination <= Max), the Kanban upload (per row) and the Export upload (per part after the whole file is read). Not checked for XD05 (the allocation always equals Max). To lower Max the user lowers the destinations first (Export), then Max (Kanban).

No open point left.

## 9. RPA reads the staging only (21-Nov)
- The bot connects to the NSP database (read-only user) and reads **only TB_H_PART_CANDIDATE_STG_SYNC**, not TB_M_PART_CANDIDATE / _DEST. NSP updates the staging (status, SEND_SEQ, run ID, dates, LAST_SYNC_DATE_APPOLE) at the click of [Sync], before the bot starts.
- Kanban file: the pair Pcs/Case + Max Case/Day = the latest row with APPOLE_SYNC_STATUS 1 of each field for the part + period (this run or an earlier one), so the row is complete when only one field changed.
- GTOPAS: per part of the GTOPAS run, every destination whose latest staging value (CREATED_DT <= GTOPAS_SYNC_DT) is >= 1.
- Queries (SQLite dialect, notes for SQL Server inside): `sql/staging_sync_queries.sql`. SQL sandbox to try them: https://claude.ai/artifact/SUTKyVSyXR7Qer32d2jUr5
