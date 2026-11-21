-- TB_H_PART_CANDIDATE_STG_SYNC: DDL and RPA queries (SQLite dialect; SQL Server: || -> +, SUBSTR -> SUBSTRING, IFNULL -> ISNULL, LENGTH -> LEN)

CREATE TABLE TB_H_PART_CANDIDATE_STG_SYNC (
  HIST_ID INTEGER PRIMARY KEY,
  PART_NO VARCHAR(15) NOT NULL,
  PART_NAME VARCHAR(60) NOT NULL,
  PERIOD CHAR(6) NOT NULL,
  PART_STATUS VARCHAR(10) NOT NULL,
  LEVEL_TYPE VARCHAR(6) NOT NULL,
  DEST_CODE CHAR(7),
  ORDER_TYPE VARCHAR(2),
  FIELD_NAME VARCHAR(30) NOT NULL,
  ACTION VARCHAR(6) NOT NULL,
  OLD_VALUE VARCHAR(10),
  NEW_VALUE VARCHAR(10),
  SOURCE VARCHAR(6) NOT NULL,
  UPLOAD_ID VARCHAR(20),
  APPOLE_SYNC_STATUS CHAR(1) NOT NULL DEFAULT '0',
  APPOLE_SYNC_DT DATETIME,
  SEND_SEQ NUMBER(1),
  APPOLE_SYNC_RUN_ID VARCHAR(14),
  GTOPAS_SYNC_STATUS CHAR(1),
  GTOPAS_SYNC_DT DATETIME,
  GTOPAS_SYNC_RUN_ID VARCHAR(14),
  CREATED_BY VARCHAR(20) NOT NULL,
  CREATED_DT DATETIME NOT NULL,
  CHANGED_BY VARCHAR(20),
  CHANGED_DT DATETIME
);

-- ============================================================
-- 1. [Sync]: rows taken for AP POLE
-- ============================================================
-- Rows NSP takes when the user clicks [Sync].
-- Change the click time and the periods to try. Here: the click of 15-Dec-2026 10:00, before that run
-- (the rows are already Sync in the sandbox, so the status condition is replaced by the run to show what was taken).
WITH p AS (SELECT '2026-11-27 10:00:00' AS last_sync,   -- LAST_SYNC_DATE_APPOLE before the click
                  '2026-12-15 10:00:00' AS click_time,
                  '202612' AS cur_period, '202701' AS next_period)
SELECT s.HIST_ID, s.PART_NO, s.PERIOD, s.LEVEL_TYPE, s.DEST_CODE, s.ORDER_TYPE, s.FIELD_NAME, s.ACTION, s.OLD_VALUE, s.NEW_VALUE, s.CREATED_DT
FROM TB_H_PART_CANDIDATE_STG_SYNC s, p
WHERE s.PERIOD IN (p.cur_period, p.next_period)
  AND s.CREATED_DT >  p.last_sync
  AND s.CREATED_DT <= p.click_time
  -- in production also: AND s.APPOLE_SYNC_STATUS = '0'
ORDER BY s.HIST_ID;

-- ============================================================
-- 2. [Sync]: reduction per key (first OLD, last NEW, SEND_SEQ)
-- ============================================================
-- Per key of one run: AP POLE value = OLD of the first row, NSP value = NEW of the last row.
WITH p AS (SELECT '20261215100000' AS run),
r AS (SELECT s.* FROM TB_H_PART_CANDIDATE_STG_SYNC s, p WHERE s.APPOLE_SYNC_RUN_ID = p.run),
k AS (SELECT PART_NO, PERIOD, LEVEL_TYPE, IFNULL(DEST_CODE, '') AS DEST_CODE, IFNULL(ORDER_TYPE, '') AS ORDER_TYPE, FIELD_NAME,
             MIN(HIST_ID) AS FIRST_ID, MAX(HIST_ID) AS LAST_ID, COUNT(*) AS N_ROWS
      FROM r GROUP BY PART_NO, PERIOD, LEVEL_TYPE, IFNULL(DEST_CODE, ''), IFNULL(ORDER_TYPE, ''), FIELD_NAME)
SELECT k.PART_NO, k.PERIOD, k.LEVEL_TYPE, k.DEST_CODE, k.ORDER_TYPE, k.FIELD_NAME, k.N_ROWS,
       f.OLD_VALUE AS APPOLE_VALUE, l.NEW_VALUE AS NSP_VALUE,
       CASE WHEN l.ACTION = 'DELETE' THEN 'Delete'
            WHEN f.OLD_VALUE IS NULL THEN 'Add'
            WHEN CAST(l.NEW_VALUE AS INT) < CAST(f.OLD_VALUE AS INT) THEN 'Down'
            WHEN CAST(l.NEW_VALUE AS INT) > CAST(f.OLD_VALUE AS INT) THEN 'Up' ELSE '-' END AS DIRECTION,
       l.HIST_ID AS LAST_HIST_ID, l.SEND_SEQ
FROM k JOIN r f ON f.HIST_ID = k.FIRST_ID JOIN r l ON l.HIST_ID = k.LAST_ID
ORDER BY k.PERIOD, l.SEND_SEQ, k.PART_NO, k.LEVEL_TYPE DESC, k.DEST_CODE;

-- ============================================================
-- 3. RPA AP POLE: Kanban file (LLM9Q910)
-- ============================================================
-- One row per part + period with SEND_SEQ 2 in the run.
-- Pcs/Case and Max Case/Day: latest Sync row of each field (this run or an earlier one), so the pair is complete
-- even when only one of them changed. Everything comes from the staging.
WITH p AS (SELECT '20261215100000' AS run),
parts AS (SELECT DISTINCT s.PART_NO, s.PERIOD, s.PART_NAME
          FROM TB_H_PART_CANDIDATE_STG_SYNC s, p
          WHERE s.APPOLE_SYNC_RUN_ID = p.run AND s.SEND_SEQ = 2),
v AS (SELECT s.PART_NO, s.PERIOD, s.FIELD_NAME, CAST(s.NEW_VALUE AS INT) AS VAL,
             ROW_NUMBER() OVER (PARTITION BY s.PART_NO, s.PERIOD, s.FIELD_NAME ORDER BY s.HIST_ID DESC) AS RN
      FROM TB_H_PART_CANDIDATE_STG_SYNC s, p
      WHERE s.LEVEL_TYPE = 'KANBAN' AND s.APPOLE_SYNC_STATUS = '1' AND s.APPOLE_SYNC_RUN_ID <= p.run)
SELECT 'LLM9Q910_' || p.run || '_' || x.PERIOD || '_2.xls' AS FILE_NAME,
       SUBSTR(x.PERIOD, 5, 2) AS "Effective Month", SUBSTR(x.PERIOD, 1, 4) AS "Effective Year",
       'P6' AS "Operator ID", x.PART_NO AS "Part No.", x.PART_NAME AS "Part Name",
       pc.VAL AS "Shipping Box Qty", mx.VAL AS "Max Shipping Box Qty", pc.VAL * mx.VAL AS "Max Allowance Qty"
FROM parts x, p
JOIN v pc ON pc.PART_NO = x.PART_NO AND pc.PERIOD = x.PERIOD AND pc.FIELD_NAME = 'PCS_CASE'     AND pc.RN = 1
JOIN v mx ON mx.PART_NO = x.PART_NO AND mx.PERIOD = x.PERIOD AND mx.FIELD_NAME = 'MAX_CASE_DAY' AND mx.RN = 1
ORDER BY x.PERIOD, x.PART_NO;

-- ============================================================
-- 4. RPA AP POLE: Export files (LLM9Q880)
-- ============================================================
-- EXPORT rows of the run with SEND_SEQ 1 or 3. One file per period + SEND_SEQ.
-- Inside a file: per part the rows going down / deleted first, then up / added.
WITH p AS (SELECT '20261215100000' AS run),
r AS (SELECT s.* FROM TB_H_PART_CANDIDATE_STG_SYNC s, p WHERE s.APPOLE_SYNC_RUN_ID = p.run AND s.LEVEL_TYPE = 'EXPORT'),
f AS (SELECT PART_NO, PERIOD, DEST_CODE, ORDER_TYPE, MIN(HIST_ID) AS FIRST_ID FROM r GROUP BY PART_NO, PERIOD, DEST_CODE, ORDER_TYPE)
SELECT 'LLM9Q880_' || p.run || '_' || l.PERIOD || '_' || l.SEND_SEQ || '.xls' AS FILE_NAME,
       SUBSTR(l.PERIOD, 5, 2) AS "Effective Month", SUBSTR(l.PERIOD, 1, 4) AS "Effective Year",
       REPLACE(l.PART_NO, '-', '') AS "Part No.", '' AS "Shipping Box Qty", '' AS "Max Shipping Box by Part No.",
       CASE WHEN LENGTH(l.DEST_CODE) = 7 THEN SUBSTR(l.DEST_CODE, 1, 5) || '-' || SUBSTR(l.DEST_CODE, 6, 2) ELSE l.DEST_CODE END AS "Buyer-PD",
       l.ORDER_TYPE AS "Order Type", '2' AS "Transport Code", CAST(l.NEW_VALUE AS INT) AS "Max Shipping Box (RCS)",
       '' AS "Max Allowance Qty", '' AS "Packing/Pallet Type"
FROM r l, p
JOIN f ON f.PART_NO = l.PART_NO AND f.PERIOD = l.PERIOD AND f.DEST_CODE = l.DEST_CODE AND f.ORDER_TYPE = l.ORDER_TYPE
JOIN r fo ON fo.HIST_ID = f.FIRST_ID
WHERE l.SEND_SEQ IS NOT NULL
ORDER BY l.PERIOD, l.SEND_SEQ, l.PART_NO,
         CASE WHEN l.ACTION = 'DELETE' OR CAST(l.NEW_VALUE AS INT) < CAST(fo.OLD_VALUE AS INT) THEN 0 ELSE 1 END,
         l.DEST_CODE, l.ORDER_TYPE;

-- ============================================================
-- 5. RPA GTOPAS: destinations to compare
-- ============================================================
-- Parts of the GTOPAS run; for each part every destination whose latest value (staging) is >= 1.
-- Runs: 20261201001000 (rollover Dec), 20261215100000 ([Sync] Current), 20270101001000 (rollover Jan).
WITH p AS (SELECT '20270101001000' AS run),
parts AS (SELECT DISTINCT s.PART_NO, s.PERIOD, s.GTOPAS_SYNC_DT
          FROM TB_H_PART_CANDIDATE_STG_SYNC s, p WHERE s.GTOPAS_SYNC_RUN_ID = p.run),
lastv AS (SELECT s.PART_NO, s.PERIOD, s.DEST_CODE, s.ORDER_TYPE, CAST(s.NEW_VALUE AS INT) AS VAL,
                 ROW_NUMBER() OVER (PARTITION BY s.PART_NO, s.PERIOD, s.DEST_CODE, s.ORDER_TYPE ORDER BY s.HIST_ID DESC) AS RN
          FROM TB_H_PART_CANDIDATE_STG_SYNC s
          JOIN parts x ON x.PART_NO = s.PART_NO AND x.PERIOD = s.PERIOD
          WHERE s.LEVEL_TYPE = 'EXPORT' AND s.CREATED_DT <= x.GTOPAS_SYNC_DT)
SELECT DISTINCT REPLACE(PART_NO, '-', '') AS "P/No.", DEST_CODE AS "Destination Code",
       '01' AS "Depot", 'A' AS "Maker", '2' AS "Dom/Os", '*' AS "TOPAS Order Type", '2' AS "Trans"
FROM lastv WHERE RN = 1 AND VAL >= 1
ORDER BY 1, 2;

-- ============================================================
-- 6. GTOPAS compare with the screen (demo)
-- ============================================================
-- Add / Delete / Keep against the GTOPAS screen sample (SCR_GTOPAS_WVJA5204 = before the rollover of 01-Jan-2027).
WITH p AS (SELECT '20270101001000' AS run),
parts AS (SELECT DISTINCT s.PART_NO, s.PERIOD, s.GTOPAS_SYNC_DT FROM TB_H_PART_CANDIDATE_STG_SYNC s, p WHERE s.GTOPAS_SYNC_RUN_ID = p.run),
lastv AS (SELECT s.PART_NO, s.DEST_CODE, CAST(s.NEW_VALUE AS INT) AS VAL,
                 ROW_NUMBER() OVER (PARTITION BY s.PART_NO, s.PERIOD, s.DEST_CODE, s.ORDER_TYPE ORDER BY s.HIST_ID DESC) AS RN
          FROM TB_H_PART_CANDIDATE_STG_SYNC s JOIN parts x ON x.PART_NO = s.PART_NO AND x.PERIOD = s.PERIOD
          WHERE s.LEVEL_TYPE = 'EXPORT' AND s.CREATED_DT <= x.GTOPAS_SYNC_DT),
nsp AS (SELECT DISTINCT REPLACE(PART_NO, '-', '') AS P_NO, DEST_CODE FROM lastv WHERE RN = 1 AND VAL >= 1),
scr AS (SELECT g.* FROM SCR_GTOPAS_WVJA5204 g WHERE g.P_NO IN (SELECT REPLACE(PART_NO, '-', '') FROM parts))
SELECT n.P_NO, n.DEST_CODE, 'Y' AS IN_NSP, CASE WHEN g.P_NO IS NULL THEN 'N' ELSE 'Y' END AS IN_GTOPAS,
       CASE WHEN g.P_NO IS NULL THEN 'Add' ELSE 'Keep' END AS ACTION
FROM nsp n LEFT JOIN scr g ON g.P_NO = n.P_NO AND g.DEST_CODE = n.DEST_CODE
UNION ALL
SELECT g.P_NO, g.DEST_CODE, 'N', 'Y', 'Delete'
FROM scr g LEFT JOIN nsp n ON n.P_NO = g.P_NO AND n.DEST_CODE = g.DEST_CODE WHERE n.P_NO IS NULL
ORDER BY 1, 2;

-- ============================================================
-- 7. Screen: Sync status per part + period
-- ============================================================
-- What the Kanban / Export Crossdock Master shows, worked out from the staging.
SELECT PART_NO, PERIOD,
       CASE WHEN SUM(APPOLE_SYNC_STATUS = '0') > 0 THEN 'Non Sync' ELSE 'Sync' END AS APPOLE_SYNC,
       MAX(APPOLE_SYNC_DT) AS LAST_SENT_APPOLE,
       CASE WHEN SUM(GTOPAS_SYNC_STATUS = '0') > 0 THEN 'Non Sync'
            WHEN MAX(GTOPAS_SYNC_DT) IS NULL THEN '-' ELSE 'Sync' END AS GTOPAS_SYNC,
       MAX(GTOPAS_SYNC_DT) AS LAST_SENT_GTOPAS
FROM TB_H_PART_CANDIDATE_STG_SYNC
GROUP BY PART_NO, PERIOD
ORDER BY PERIOD, PART_NO;

-- ============================================================
-- 8. Staging: all rows
-- ============================================================
SELECT * FROM TB_H_PART_CANDIDATE_STG_SYNC ORDER BY HIST_ID;
