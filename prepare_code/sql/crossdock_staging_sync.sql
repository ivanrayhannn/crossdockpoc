-- =====================================================================================================
-- Crossdock Master: staging per target for the sync to AP POLE and GTOPAS
-- Draft, T-SQL style. Source: UISS XD01 5.24 / 5.25, XD02 / XD03 4.9, XD05 4.10 / 4.11, XD06, XD07.
-- Rules and simulation: deliverables/function_list_v2/erd/proposal_staging_sync (Staging_Header_Order.html,
-- Staging_Per_Target_Full_Flow.html).
--
-- Who calls what
--   SP_STG_WRITE     XD01 save (screen), XD02 / XD03 upload, XD05 day D: once per changed value, inside the caller's
--                    transaction, after TB_M_PART_CANDIDATE / TB_M_PART_CANDIDATE_DEST are updated. Not called for a
--                    Candidate part or a save without change.
--   SP_STG_HEADER    SP_STG_WRITE only (header OPERATION_TYPE 5 when only the destinations changed).
--   SP_STG_SYNC      XD01 [Sync]: rows 0 -> 1 with the run ID, then NSP starts the RPA parent flow with RUN_ID.
--   SP_STG_ROLLOVER  XD05 process 3 (Period Rollover, day 1): GTOPAS rows of the new Current period 0 -> 1.
--   Views            read by XD07 (AP POLE files); TB_H_STG_GTOPAS read by XD06.
--
-- SYNC_STATUS: 0 = to send, 1 = sent (run ID filled by NSP), 2 = Superseded (never sent).
-- OPERATION_TYPE (Kanban row = header of the part in a run):
--   1 Max down -> EXPORT_PRE before KANBAN   2 Max up / 3 Max same / 4 never sent -> KANBAN before EXPORT_POST
--   5 Kanban unchanged, only destinations   -> EXPORT_POST only (header, not uploaded)
--
-- TBD before build: column lengths marked (30) were TBD (follow TB_M_PART_MASTER / upload log); the System Master table
-- name and the column names PARAM / VALUE in SP_STG_SYNC; constants (P6, 2, 01, A, 3) kept per row as in the upload files.
-- =====================================================================================================

-- =====================================================================================================
-- 1. Tables
-- =====================================================================================================
CREATE TABLE TB_H_STG_APPOLE_KANBAN (
  STG_ID                       BIGINT IDENTITY(1,1) NOT NULL,
  PERIOD                       CHAR(6) NOT NULL,
  ACTION                       VARCHAR(6) NOT NULL,
  PART_STATUS                  VARCHAR(10) NOT NULL,
  EFFECTIVE_MONTH_YEAR         CHAR(7) NOT NULL,
  OPERATOR_ID                  CHAR(2) NOT NULL DEFAULT 'P6',
  PART_NO                      VARCHAR(30) NOT NULL,
  PART_NAME                    VARCHAR(30) NOT NULL,
  SHIPPING_BOX_QTY             NUMERIC(5) NOT NULL,
  MAX_SHIPPING_BOX_QTY         NUMERIC(5) NOT NULL,
  MAX_ALLOWANCE_QTY            NUMERIC(9) NOT NULL,
  OPERATION_TYPE               NUMERIC(1) NOT NULL,
  SOURCE                       VARCHAR(6) NOT NULL,
  UPLOAD_ID                    VARCHAR(30),
  SYNC_STATUS                  CHAR(1) NOT NULL DEFAULT '0',
  SYNC_DT                      DATETIME,
  SYNC_RUN_ID                  VARCHAR(14),
  CREATED_BY                   VARCHAR(20) NOT NULL,
  CREATED_DT                   DATETIME NOT NULL,
  CHANGED_BY                   VARCHAR(20),
  CHANGED_DT                   DATETIME,
  CONSTRAINT PK_TB_H_STG_APPOLE_KANBAN PRIMARY KEY (STG_ID)
);
GO

CREATE INDEX IX_STG_KANBAN_KEY ON TB_H_STG_APPOLE_KANBAN (PART_NO, PERIOD, SYNC_STATUS);
GO

CREATE INDEX IX_STG_KANBAN_RUN ON TB_H_STG_APPOLE_KANBAN (SYNC_RUN_ID);
GO


CREATE TABLE TB_H_STG_APPOLE_EXPORT (
  STG_ID                       BIGINT IDENTITY(1,1) NOT NULL,
  PERIOD                       CHAR(6) NOT NULL,
  NSP_PART_NO                  VARCHAR(30) NOT NULL,
  DEST_CODE                    CHAR(7) NOT NULL,
  ACTION                       VARCHAR(6) NOT NULL,
  EFFECTIVE_MONTH_YEAR         CHAR(7) NOT NULL,
  PART_NO                      VARCHAR(30) NOT NULL,
  BUYER_PD                     CHAR(8) NOT NULL,
  ORDER_TYPE                   VARCHAR(2) NOT NULL,
  TRANSPORT_CODE               CHAR(1) NOT NULL DEFAULT '2',
  MAX_SHIPPING_BOX_RCS         NUMERIC(5) NOT NULL,
  SOURCE                       VARCHAR(6) NOT NULL,
  UPLOAD_ID                    VARCHAR(30),
  SYNC_STATUS                  CHAR(1) NOT NULL DEFAULT '0',
  SYNC_DT                      DATETIME,
  SYNC_RUN_ID                  VARCHAR(14),
  CREATED_BY                   VARCHAR(20) NOT NULL,
  CREATED_DT                   DATETIME NOT NULL,
  CHANGED_BY                   VARCHAR(20),
  CHANGED_DT                   DATETIME,
  CONSTRAINT PK_TB_H_STG_APPOLE_EXPORT PRIMARY KEY (STG_ID)
);
GO

CREATE INDEX IX_STG_EXPORT_KEY ON TB_H_STG_APPOLE_EXPORT (NSP_PART_NO, DEST_CODE, ORDER_TYPE, PERIOD, SYNC_STATUS);
GO

CREATE INDEX IX_STG_EXPORT_RUN ON TB_H_STG_APPOLE_EXPORT (SYNC_RUN_ID);
GO


CREATE TABLE TB_H_STG_GTOPAS (
  STG_ID                       BIGINT IDENTITY(1,1) NOT NULL,
  PERIOD                       CHAR(6) NOT NULL,
  ACTION                       VARCHAR(6) NOT NULL,
  DEPOT_CODE                   CHAR(2) NOT NULL DEFAULT '01',
  P_NO                         VARCHAR(30) NOT NULL,
  DESTINATION_CODE             CHAR(7) NOT NULL,
  MAKER_CODE                   CHAR(1) NOT NULL DEFAULT 'A',
  DOMESTIC_OVERSEAS            CHAR(1) NOT NULL DEFAULT '2',
  TOPAS_ORDER_TYPE             CHAR(1) NOT NULL DEFAULT '3',
  ORDER_TRANSPORTATION_CODE    CHAR(1) NOT NULL DEFAULT '2',
  SOURCE                       VARCHAR(6) NOT NULL,
  UPLOAD_ID                    VARCHAR(30),
  SYNC_STATUS                  CHAR(1) NOT NULL DEFAULT '0',
  SYNC_DT                      DATETIME,
  SYNC_RUN_ID                  VARCHAR(14),
  CREATED_BY                   VARCHAR(20) NOT NULL,
  CREATED_DT                   DATETIME NOT NULL,
  CHANGED_BY                   VARCHAR(20),
  CHANGED_DT                   DATETIME,
  CONSTRAINT PK_TB_H_STG_GTOPAS PRIMARY KEY (STG_ID)
);
GO

CREATE INDEX IX_STG_GTOPAS_KEY ON TB_H_STG_GTOPAS (P_NO, DESTINATION_CODE, PERIOD, SYNC_STATUS);
GO

CREATE INDEX IX_STG_GTOPAS_RUN ON TB_H_STG_GTOPAS (SYNC_RUN_ID);
GO


-- =====================================================================================================
-- 2. Stored procedures: save and [Sync]
-- =====================================================================================================
CREATE PROCEDURE SP_STG_WRITE
  @LEVEL        VARCHAR(6),     -- 'KANBAN' or 'EXPORT' (GTOPAS rows are written by the EXPORT branch)
  @ACTION       VARCHAR(6),     -- ADD / EDIT / DELETE
  @PERIOD       CHAR(6),        -- YYYYMM
  @PART_NO      VARCHAR(15),    -- NSP format, with '-'
  @PART_STATUS  VARCHAR(10),    -- Active / Inactive
  @PCS_CASE     INT = NULL,     -- KANBAN: Shipping Box Qty
  @MAX_CASE_DAY INT = NULL,     -- KANBAN: Max Shipping Box Qty
  @DEST_CODE    CHAR(7) = NULL, -- EXPORT
  @ORDER_TYPE   VARCHAR(2) = NULL,
  @CASE_DAY     INT = NULL,     -- EXPORT: Max Shipping Box (RCS); 0 on DELETE
  @SOURCE       VARCHAR(6),     -- SCREEN / UPLOAD / BATCH
  @UPLOAD_ID    VARCHAR(20) = NULL,
  @USER_ID      VARCHAR(20)
AS
BEGIN
  DECLARE @NOW DATETIME = GETDATE(), @EFF CHAR(7) = RIGHT(@PERIOD, 2) + '/' + LEFT(@PERIOD, 4);

  IF @LEVEL = 'KANBAN'
  BEGIN
    DECLARE @SENT_MAX INT, @SENT_PCS INT, @SENT_PERIOD CHAR(6);
    -- 1. last sent Kanban row: same period, else the latest earlier period (still active in AP POLE)
    SELECT TOP 1 @SENT_MAX = MAX_SHIPPING_BOX_QTY, @SENT_PCS = SHIPPING_BOX_QTY, @SENT_PERIOD = PERIOD
    FROM   TB_H_STG_APPOLE_KANBAN WITH (UPDLOCK)
    WHERE  PART_NO = @PART_NO AND PERIOD <= @PERIOD AND SYNC_STATUS = '1'
    ORDER  BY PERIOD DESC, SYNC_DT DESC, STG_ID DESC;

    -- 2. older unsent row of the part + period -> 2 Superseded
    UPDATE TB_H_STG_APPOLE_KANBAN
    SET    SYNC_STATUS = '2', CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
    WHERE  PART_NO = @PART_NO AND PERIOD = @PERIOD AND SYNC_STATUS = '0';

    -- 3. OPERATION_TYPE: 1 Max down, 2 Max up, 3 Max same, 4 never sent
    DECLARE @OP TINYINT = CASE WHEN @SENT_MAX IS NULL THEN 4
                               WHEN @MAX_CASE_DAY < @SENT_MAX THEN 1
                               WHEN @MAX_CASE_DAY > @SENT_MAX THEN 2 ELSE 3 END;

    -- 4. back to the values sent for this period -> nothing to send (row kept as 2)
    DECLARE @ST CHAR(1) = CASE WHEN @SENT_PERIOD = @PERIOD AND @MAX_CASE_DAY = @SENT_MAX
                                    AND @PCS_CASE = @SENT_PCS THEN '2' ELSE '0' END;

    INSERT INTO TB_H_STG_APPOLE_KANBAN
      (PERIOD, ACTION, PART_STATUS, EFFECTIVE_MONTH_YEAR, OPERATOR_ID, PART_NO, PART_NAME,
       SHIPPING_BOX_QTY, MAX_SHIPPING_BOX_QTY, MAX_ALLOWANCE_QTY, OPERATION_TYPE,
       SYNC_STATUS, SOURCE, UPLOAD_ID, CREATED_BY, CREATED_DT)
    SELECT @PERIOD, @ACTION, @PART_STATUS, @EFF, 'P6', @PART_NO, m.PART_NAME,
           @PCS_CASE, @MAX_CASE_DAY, @PCS_CASE * @MAX_CASE_DAY, @OP,
           @ST, @SOURCE, @UPLOAD_ID, @USER_ID, @NOW
    FROM   TB_M_PART_CANDIDATE m WHERE m.PART_NO = @PART_NO AND m.PERIOD = @PERIOD;

    -- 5. back to the sent values while Export rows wait: header 5 again: a part + period with an unsent Export row keeps one unsent Kanban row
    EXEC SP_STG_HEADER @PERIOD, @PART_NO, @SOURCE, @UPLOAD_ID, @USER_ID, @NOW;
  END

  IF @LEVEL = 'EXPORT'
  BEGIN
    DECLARE @SENT_RCS INT, @SENT_RCS_PERIOD CHAR(6);
    -- 1. last sent value of the key (same period, else the latest earlier period)
    SELECT TOP 1 @SENT_RCS = MAX_SHIPPING_BOX_RCS, @SENT_RCS_PERIOD = PERIOD
    FROM   TB_H_STG_APPOLE_EXPORT WITH (UPDLOCK)
    WHERE  NSP_PART_NO = @PART_NO AND DEST_CODE = @DEST_CODE AND ORDER_TYPE = @ORDER_TYPE
      AND  PERIOD <= @PERIOD AND SYNC_STATUS = '1'
    ORDER  BY PERIOD DESC, SYNC_DT DESC, STG_ID DESC;

    -- 2. older unsent row of the key -> 2 Superseded
    UPDATE TB_H_STG_APPOLE_EXPORT
    SET    SYNC_STATUS = '2', CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
    WHERE  PERIOD = @PERIOD AND NSP_PART_NO = @PART_NO AND DEST_CODE = @DEST_CODE
      AND  ORDER_TYPE = @ORDER_TYPE AND SYNC_STATUS = '0';

    -- 3. insert; back to the value sent for this period -> 2
    INSERT INTO TB_H_STG_APPOLE_EXPORT
      (PERIOD, NSP_PART_NO, DEST_CODE, ACTION, EFFECTIVE_MONTH_YEAR, PART_NO, BUYER_PD,
       ORDER_TYPE, TRANSPORT_CODE, MAX_SHIPPING_BOX_RCS, SYNC_STATUS, SOURCE, UPLOAD_ID, CREATED_BY, CREATED_DT)
    VALUES
      (@PERIOD, @PART_NO, @DEST_CODE, @ACTION, @EFF, REPLACE(@PART_NO, '-', ''),
       LEFT(@DEST_CODE, 5) + '-' + RIGHT(@DEST_CODE, 2), @ORDER_TYPE, '2', @CASE_DAY,
       CASE WHEN @SENT_RCS_PERIOD = @PERIOD AND @CASE_DAY = @SENT_RCS THEN '2' ELSE '0' END,
       @SOURCE, @UPLOAD_ID, @USER_ID, @NOW);

    -- 4. GTOPAS keeps part + destination (any order type): what the master needs against what GTOPAS gets
    DECLARE @NEED VARCHAR(6) = CASE WHEN EXISTS (SELECT 1 FROM TB_M_PART_CANDIDATE_DEST
                                 WHERE PART_NO = @PART_NO AND PERIOD = @PERIOD AND DEST_CODE = @DEST_CODE AND CASE_DAY > 0)
                               THEN 'ADD' ELSE 'DELETE' END;
    DECLARE @G_SENT VARCHAR(6) = ISNULL((SELECT TOP 1 ACTION FROM TB_H_STG_GTOPAS WITH (UPDLOCK)
                                   WHERE P_NO = @PART_NO AND DESTINATION_CODE = @DEST_CODE AND PERIOD <= @PERIOD AND SYNC_STATUS = '1'
                                   ORDER BY PERIOD DESC, SYNC_DT DESC, STG_ID DESC), 'DELETE');
    DECLARE @G_PEND VARCHAR(6) = (SELECT ACTION FROM TB_H_STG_GTOPAS
                                   WHERE P_NO = @PART_NO AND DESTINATION_CODE = @DEST_CODE AND PERIOD = @PERIOD AND SYNC_STATUS = '0');
    IF @NEED <> ISNULL(@G_PEND, @G_SENT)
    BEGIN
      UPDATE TB_H_STG_GTOPAS SET SYNC_STATUS = '2', CHANGED_BY = @USER_ID, CHANGED_DT = @NOW   -- unsent opposite row
      WHERE  PERIOD = @PERIOD AND P_NO = @PART_NO AND DESTINATION_CODE = @DEST_CODE AND SYNC_STATUS = '0';
      IF @NEED <> @G_SENT                                                                     -- else GTOPAS already has it
        INSERT INTO TB_H_STG_GTOPAS
          (PERIOD, ACTION, DEPOT_CODE, P_NO, DESTINATION_CODE, MAKER_CODE, DOMESTIC_OVERSEAS,
           TOPAS_ORDER_TYPE, ORDER_TRANSPORTATION_CODE, SYNC_STATUS, SOURCE, UPLOAD_ID, CREATED_BY, CREATED_DT)
        VALUES
          (@PERIOD, @NEED, '01', @PART_NO, @DEST_CODE, 'A', '2', '3', '2', '0', @SOURCE, @UPLOAD_ID, @USER_ID, @NOW);
    END

    -- 5. header rule: a part + period with an unsent Export row keeps one unsent Kanban row
    EXEC SP_STG_HEADER @PERIOD, @PART_NO, @SOURCE, @UPLOAD_ID, @USER_ID, @NOW;
  END
END;
GO


-- Header of the part (called by SP_STG_WRITE): OPERATION_TYPE 5 = Kanban unchanged, only the destinations changed
CREATE PROCEDURE SP_STG_HEADER
  @PERIOD CHAR(6), @PART_NO VARCHAR(15), @SOURCE VARCHAR(6), @UPLOAD_ID VARCHAR(20), @USER_ID VARCHAR(20), @NOW DATETIME
AS
BEGIN
  DECLARE @PEND_E INT = (SELECT COUNT(*) FROM TB_H_STG_APPOLE_EXPORT
                         WHERE NSP_PART_NO = @PART_NO AND PERIOD = @PERIOD AND SYNC_STATUS = '0');
  DECLARE @PEND_K TINYINT = (SELECT OPERATION_TYPE FROM TB_H_STG_APPOLE_KANBAN
                             WHERE PART_NO = @PART_NO AND PERIOD = @PERIOD AND SYNC_STATUS = '0');
  IF @PEND_E > 0 AND @PEND_K IS NULL                       -- Export waits, no header yet: write 5 with the current values
    INSERT INTO TB_H_STG_APPOLE_KANBAN
      (PERIOD, ACTION, PART_STATUS, EFFECTIVE_MONTH_YEAR, OPERATOR_ID, PART_NO, PART_NAME,
       SHIPPING_BOX_QTY, MAX_SHIPPING_BOX_QTY, MAX_ALLOWANCE_QTY, OPERATION_TYPE,
       SYNC_STATUS, SOURCE, UPLOAD_ID, CREATED_BY, CREATED_DT)
    SELECT @PERIOD, 'KEEP', m.PART_STATUS, RIGHT(@PERIOD, 2) + '/' + LEFT(@PERIOD, 4), 'P6', @PART_NO, m.PART_NAME,
           m.PCS_CASE, m.MAX_CASE_DAY, m.PCS_CASE * m.MAX_CASE_DAY, 5,
           '0', @SOURCE, @UPLOAD_ID, @USER_ID, @NOW
    FROM   TB_M_PART_CANDIDATE m WHERE m.PART_NO = @PART_NO AND m.PERIOD = @PERIOD;
  ELSE IF @PEND_E = 0 AND @PEND_K = 5                       -- every Export change went back to the sent value
    UPDATE TB_H_STG_APPOLE_KANBAN SET SYNC_STATUS = '2', CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
    WHERE  PART_NO = @PART_NO AND PERIOD = @PERIOD AND SYNC_STATUS = '0';
END;
GO


-- [Sync] (XD01): no rule, only 0 -> 1. One transaction; a save waits for the lock.
CREATE PROCEDURE SP_STG_SYNC @RUN_ID VARCHAR(14), @CUR CHAR(6), @NEXT CHAR(6), @USER_ID VARCHAR(20)
AS
BEGIN
  DECLARE @NOW DATETIME = GETDATE();
  UPDATE TB_H_STG_APPOLE_KANBAN WITH (TABLOCKX)
     SET SYNC_STATUS = '1', SYNC_DT = @NOW, SYNC_RUN_ID = @RUN_ID, CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
   WHERE SYNC_STATUS = '0' AND PERIOD IN (@CUR, @NEXT);
  UPDATE TB_H_STG_APPOLE_EXPORT WITH (TABLOCKX)
     SET SYNC_STATUS = '1', SYNC_DT = @NOW, SYNC_RUN_ID = @RUN_ID, CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
   WHERE SYNC_STATUS = '0' AND PERIOD IN (@CUR, @NEXT);
  UPDATE TB_H_STG_GTOPAS WITH (TABLOCKX)              -- GTOPAS: Current only; Next waits for the Period Rollover
     SET SYNC_STATUS = '1', SYNC_DT = @NOW, SYNC_RUN_ID = @RUN_ID, CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
   WHERE SYNC_STATUS = '0' AND PERIOD = @CUR;
  UPDATE TB_M_SYSTEM_MASTER SET VALUE   -- table / column names TBD (System Master)
      = CONVERT(VARCHAR(19), @NOW, 120)
   WHERE PARAM = 'LAST_SYNC_DATE_APPOLE';
END;
GO


-- =====================================================================================================
-- 3. Stored procedure: Period Rollover
-- =====================================================================================================
-- Period Rollover (XD05 process 3, day 1 00:10): the GTOPAS rows of the period that becomes Current go 0 -> 1 with a run ID.
-- AP POLE got this period already by [Sync] after day D. The parent flow then runs XD06 only (RUN_TYPE ROLLOVER).
CREATE PROCEDURE SP_STG_ROLLOVER @RUN_ID VARCHAR(14), @PERIOD CHAR(6), @USER_ID VARCHAR(20)
AS
BEGIN
  DECLARE @NOW DATETIME = GETDATE();
  UPDATE TB_H_STG_GTOPAS WITH (TABLOCKX)
     SET SYNC_STATUS = '1', SYNC_DT = @NOW, SYNC_RUN_ID = @RUN_ID, CHANGED_BY = @USER_ID, CHANGED_DT = @NOW
   WHERE SYNC_STATUS = '0' AND PERIOD = @PERIOD;
END;
GO


-- =====================================================================================================
-- 4. Views of the AP POLE upload files (XD07)
-- =====================================================================================================
-- KANBAN (order 2): Kanban rows of a run
CREATE VIEW V_APPOLE_UPLOAD_KANBAN AS
SELECT k.SYNC_RUN_ID AS RUN_ID, 2 AS FILE_NO, k.PERIOD, k.OPERATION_TYPE,
       k.EFFECTIVE_MONTH_YEAR, k.OPERATOR_ID, k.PART_NO, k.PART_NAME,
       k.SHIPPING_BOX_QTY, k.MAX_SHIPPING_BOX_QTY, k.MAX_ALLOWANCE_QTY
FROM   TB_H_STG_APPOLE_KANBAN k
WHERE  k.SYNC_STATUS = '1'
  AND  k.OPERATION_TYPE <> 5;                              -- 5 = header only, Kanban unchanged
GO


-- EXPORT_PRE (1) and EXPORT_POST (3): Export rows of a run, file from the header, row order from the last sent value
CREATE VIEW V_APPOLE_UPLOAD_EXPORT AS
WITH e AS (
  SELECT x.*,
         LAG(x.MAX_SHIPPING_BOX_RCS) OVER (
           PARTITION BY x.NSP_PART_NO, x.DEST_CODE, x.ORDER_TYPE
           ORDER BY x.PERIOD, x.SYNC_DT, x.STG_ID) AS PREV_RCS
           -- value sent before this run: same period, or the latest earlier period
           -- (AP POLE keeps a row active until a newer Effective Month / Year)
  FROM   TB_H_STG_APPOLE_EXPORT x
  WHERE  x.SYNC_STATUS = '1'                               -- 2 Superseded rows are never sent
)
SELECT e.SYNC_RUN_ID AS RUN_ID,
       CASE WHEN k.OPERATION_TYPE = 1 THEN 1 ELSE 3 END AS FILE_NO,   -- 2, 3, 4, 5: after the Kanban file
       CASE WHEN k.OPERATION_TYPE = 1 THEN 'EXPORT_PRE' ELSE 'EXPORT_POST' END AS FILE_NAME,
       CASE WHEN e.PREV_RCS IS NOT NULL AND e.MAX_SHIPPING_BOX_RCS < e.PREV_RCS THEN 1 ELSE 2 END AS ROW_ORDER,
       e.PERIOD, e.NSP_PART_NO, e.STG_ID,
       e.EFFECTIVE_MONTH_YEAR, e.PART_NO, e.BUYER_PD, e.ORDER_TYPE, e.TRANSPORT_CODE, e.MAX_SHIPPING_BOX_RCS
FROM   e
JOIN   TB_H_STG_APPOLE_KANBAN k                              -- every part of the run has its header (1 to 5)
       ON  k.SYNC_RUN_ID = e.SYNC_RUN_ID AND k.PERIOD = e.PERIOD
       AND k.PART_NO = e.NSP_PART_NO   AND k.SYNC_STATUS = '1';
GO


-- =====================================================================================================
-- 5. Queries of the robots (read-only DB user). :run = RUN_ID given by the parent flow
-- =====================================================================================================
-- Parent flow: scenario 1 (GTOPAS first) when > 0, scenario 2 (AP POLE only) when 0
SELECT COUNT(*) FROM TB_H_STG_GTOPAS WHERE SYNC_RUN_ID = :run;

-- XD06 GTOPAS: rows to add / delete on WVJA5204
SELECT * FROM TB_H_STG_GTOPAS WHERE SYNC_RUN_ID = :run ORDER BY P_NO, DESTINATION_CODE;

-- XD07 AP POLE: files in this order (a file without rows is not made)
SELECT * FROM V_APPOLE_UPLOAD_EXPORT WHERE RUN_ID = :run AND FILE_NO = 1 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;  -- 1 EXPORT_PRE (LLM9Q880)
SELECT * FROM V_APPOLE_UPLOAD_KANBAN WHERE RUN_ID = :run ORDER BY PERIOD, PART_NO;                                        -- 2 KANBAN (LLM9Q910)
SELECT * FROM V_APPOLE_UPLOAD_EXPORT WHERE RUN_ID = :run AND FILE_NO = 3 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;  -- 3 EXPORT_POST (LLM9Q880)
