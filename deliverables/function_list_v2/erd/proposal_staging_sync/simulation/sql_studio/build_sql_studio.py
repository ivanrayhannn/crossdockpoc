"""SQL Studio of the staging tables: the tables and views of prepare_code/sql/crossdock_staging_sync.sql in SQLite (sql.js in the
browser), filled with the simulation data (studio_data.json: six [Sync] runs with OPERATION_TYPE 1 to 5 and rows still waiting),
plus saved queries: the robot queries of XD06 / XD07, queries that explain the file order, checks and the [Sync] update.
Run: node gen_data.cjs && python3 build_sql_studio.py   ->  ../Staging_SQL_Studio.html"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *['..'] * 6))
TSQL = open(os.path.join(ROOT, 'prepare_code', 'sql', 'crossdock_staging_sync.sql'), encoding='utf-8').read()
DATA = json.load(open(os.path.join(HERE, 'studio_data.json')))
OUT = os.path.join(HERE, '..', 'Staging_SQL_Studio.html')
DEST = {'JAPAN': '9722D10', 'KOREA': '9715310', 'TAIWAN': '9811110', 'USA': '9600110', 'THAILAND': '9655510'}


# ---------- DDL: T-SQL of the SQL file -> SQLite ----------
def batches(kind):
    return [b.strip() for b in TSQL.split('\nGO') if re.search(rf'^\s*CREATE {kind}\b', b, re.M)]


def to_sqlite_table(b):
    b = b[b.index('CREATE TABLE'):]
    b = re.sub(r'STG_ID\s+BIGINT IDENTITY\(1,1\) NOT NULL', 'STG_ID                     INTEGER PRIMARY KEY', b)
    b = re.sub(r',\s*\n\s*CONSTRAINT PK_\w+ PRIMARY KEY \(STG_ID\)', '', b)
    return b.replace('DATETIME2(0)', 'DATETIME') + ';' if not b.endswith(';') else b.replace('DATETIME2(0)', 'DATETIME')


def strip_comments_before(b, word):
    return b[b.index(word):]


tables = [to_sqlite_table(b) for b in batches('TABLE')]
indexes = [strip_comments_before(b, 'CREATE INDEX') for b in batches('INDEX')]
# T-SQL string functions of the views -> SQLite
views = [re.sub(r"SUBSTRING\((\w)\.PERIOD, 5, 2\) \+ '/' \+ LEFT\((\w)\.PERIOD, 4\)", r"substr(\1.PERIOD, 5, 2) || '/' || substr(\2.PERIOD, 1, 4)",
                strip_comments_before(b, 'CREATE VIEW')) for b in batches('VIEW')]
assert all('SUBSTRING' not in v for v in views)
assert len(tables) == 3 and len(views) == 3, (len(tables), len(views))
DDL = '\n\n'.join(tables + indexes + views)


# ---------- data ----------
def q(v):
    if v is None:
        return 'NULL'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


sdt = lambda run: f'{run[:4]}-{run[4:6]}-{run[6:8]} {run[8:10]}:{run[10:12]}:{run[12:14]}' if run else None
my = lambda per: per[4:] + '/' + per[:4]
bpd = lambda d: DEST[d][:5] + '-' + DEST[d][5:]
ins = []
for r in DATA['K']:
    ins.append('INSERT INTO TB_H_STG_APPOLE_KANBAN VALUES (' + ', '.join(q(v) for v in [
        r['id'], r['per'], r['act'], r['ps'], 'P6', r['p'], 'DUMMY PART ' + r['p'][-3:], r['pcs'], r['max'], r['pcs'] * r['max'],
        r['op'], r['src'], None, str(r['st']), sdt(r['run']), r['by'], r['dt'], r.get('chb'), r.get('chd')]) + ');')
for r in DATA['E']:
    ins.append('INSERT INTO TB_H_STG_APPOLE_EXPORT VALUES (' + ', '.join(q(v) for v in [
        r['id'], r['per'], r['p'], DEST[r['d']], r['act'], r['p'].replace('-', ''), bpd(r['d']), r['ot'], '2', r['cd'],
        r['src'], None, str(r['st']), sdt(r['run']), r['by'], r['dt'], r.get('chb'), r.get('chd')]) + ');')
for r in DATA['G']:
    ins.append('INSERT INTO TB_H_STG_GTOPAS VALUES (' + ', '.join(q(v) for v in [
        r['id'], r['per'], r['act'], '01', r['p'], DEST[r['d']], 'A', '2', '3', '2', r['src'], None, str(r['st']), sdt(r['run']),
        r['by'], r['dt'], r.get('chb'), r.get('chd')]) + ');')
SEED = '\n'.join(ins)
RUNS = [{'sdt': r['sdt'], 'label': r['label'], 'ots': r['ots'], 'sc': r['sc'], 'g': r['g']} for r in DATA['RUNS']]
DEF_RUN = '2026-12-10 11:00:00'

# ---------- saved queries ({{RUN}} = the run picked on the page) ----------
K, E, G = 'TB_H_STG_APPOLE_KANBAN', 'TB_H_STG_APPOLE_EXPORT', 'TB_H_STG_GTOPAS'
OT_TXT = {1: 'Max down: the Export rows of the part go in EXPORT_PRE, before KANBAN',
          2: 'Max up: KANBAN first, then the Export rows in EXPORT_POST',
          3: 'Max same (only Pcs/Case, or a new period with the same Max): KANBAN, then EXPORT_POST',
          4: 'Never sent: KANBAN first, so AP POLE knows the part, then EXPORT_POST',
          5: 'Kanban unchanged, only the destinations: header row (ACTION KEEP), not in the KANBAN file; EXPORT_POST only'}
OT_SQL = lambda n: f"""-- OPERATION_TYPE {n}: {OT_TXT[n]}
-- Every Kanban row with this code in every run, the Max sent before it, and where its Export rows go
SELECT k.SYNC_DT, k.PERIOD, k.PART_NO, k.ACTION, k.PREV_MAX, k.MAX_SHIPPING_BOX_QTY AS MAX_NOW,
       k.SHIPPING_BOX_QTY, k.OPERATION_TYPE,
       CASE WHEN k.OPERATION_TYPE = 5 THEN 'not in file 2' ELSE 'file 2 KANBAN' END AS KANBAN_FILE,
       (SELECT COUNT(*) FROM V_APPOLE_UPLOAD_EXPORT v
         WHERE v.SYNC_DT = k.SYNC_DT AND v.PERIOD = k.PERIOD AND v.NSP_PART_NO = k.PART_NO) AS EXPORT_ROWS,
       (SELECT GROUP_CONCAT(DISTINCT v.FILE_NAME) FROM V_APPOLE_UPLOAD_EXPORT v
         WHERE v.SYNC_DT = k.SYNC_DT AND v.PERIOD = k.PERIOD AND v.NSP_PART_NO = k.PART_NO) AS EXPORT_FILE
FROM  (SELECT x.*, LAG(x.MAX_SHIPPING_BOX_QTY) OVER (PARTITION BY x.PART_NO ORDER BY x.PERIOD, x.SYNC_DT, x.STG_ID) AS PREV_MAX
       FROM {K} x WHERE x.SYNC_STATUS = '1') k
WHERE  k.OPERATION_TYPE = {n}
ORDER BY k.SYNC_DT, k.PERIOD, k.PART_NO;"""

QUERIES = [
    ('Robot (read-only DB user)', 'Parent flow: scenario 1 or 2', 'More than 0 GTOPAS rows in the run: scenario 1, XD06 first, XD07 only when XD06 succeeded. 0: scenario 2, XD07 only.',
     "SELECT COUNT(*) AS GTOPAS_ROWS\nFROM   V_GTOPAS_CROSSDOCK\nWHERE  SYNC_DT = '{{RUN}}';"),
    ('Robot (read-only DB user)', 'XD06: GTOPAS rows of the run', 'One row per part + destination, ACTION ADD or DELETE on WVJA5204.',
     f"SELECT STG_ID, ACTION, DEPOT_CODE, P_NO, DESTINATION_CODE, MAKER_CODE,\n       DOMESTIC_OVERSEAS, TOPAS_ORDER_TYPE, ORDER_TRANSPORTATION_CODE\nFROM   V_GTOPAS_CROSSDOCK\nWHERE  SYNC_DT = '{{{{RUN}}}}'\nORDER BY P_NO, DESTINATION_CODE;"),
    ('Robot (read-only DB user)', 'XD07 file 1: EXPORT_PRE', 'Export rows of parts whose Max goes down (header OPERATION_TYPE 1). Template LLM9Q880. No row = file not made.',
     "SELECT * FROM V_APPOLE_UPLOAD_EXPORT\nWHERE  SYNC_DT = '{{RUN}}' AND FILE_NO = 1\nORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;"),
    ('Robot (read-only DB user)', 'XD07 file 2: KANBAN', 'Kanban rows with OPERATION_TYPE 1 to 4 (a header 5 is not uploaded). Template LLM9Q910.',
     "SELECT * FROM V_APPOLE_UPLOAD_KANBAN\nWHERE  SYNC_DT = '{{RUN}}'\nORDER BY PERIOD, PART_NO;"),
    ('Robot (read-only DB user)', 'XD07 file 3: EXPORT_POST', 'Every other Export row of the run (header 2, 3, 4 or 5). Template LLM9Q880.',
     "SELECT * FROM V_APPOLE_UPLOAD_EXPORT\nWHERE  SYNC_DT = '{{RUN}}' AND FILE_NO = 3\nORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;"),
    ('Robot (read-only DB user)', 'XD07: the three files in upload order', 'One list of every row the robot uploads, file by file, in the columns of the templates.',
     """SELECT FILE_NO, FILE_NAME, ROW_ORDER, EFFECTIVE_MONTH_YEAR, PART_NO, BUYER_PD AS BUYER_PD_OR_OPERATOR,
       ORDER_TYPE, CAST(MAX_SHIPPING_BOX_RCS AS TEXT) AS VALUE_UPLOADED, PERIOD, NSP_PART_NO, STG_ID
FROM   V_APPOLE_UPLOAD_EXPORT WHERE SYNC_DT = '{{RUN}}'
UNION ALL
SELECT FILE_NO, 'KANBAN', NULL, EFFECTIVE_MONTH_YEAR, PART_NO, OPERATOR_ID,
       NULL, 'Pcs ' || SHIPPING_BOX_QTY || ' / Max ' || MAX_SHIPPING_BOX_QTY, PERIOD, PART_NO, STG_ID
FROM   V_APPOLE_UPLOAD_KANBAN WHERE SYNC_DT = '{{RUN}}'
ORDER BY FILE_NO, PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;"""),
    ('Robot (read-only DB user)', '[Re-send last Sync]: last run', 'NSP takes the last SYNC_DT and starts the parent flow with it again. Nothing changes in the tables.',
     f"""SELECT MAX(SYNC_DT) AS LAST_RUN FROM (
  SELECT SYNC_DT FROM {K} WHERE SYNC_STATUS = '1'
  UNION ALL SELECT SYNC_DT FROM {E} WHERE SYNC_STATUS = '1'
  UNION ALL SELECT SYNC_DT FROM {G} WHERE SYNC_STATUS = '1') s;"""),
    ('Explain the run', 'Runs: what each [Sync] sent', 'One line per SYNC_DT: the Kanban headers with their OPERATION_TYPE, the number of Export and GTOPAS rows.',
     f"""SELECT k.SYNC_DT,
       GROUP_CONCAT(k.PART_NO || ' ' || k.PERIOD || ' = ' || k.OPERATION_TYPE, ', ') AS HEADERS,
       (SELECT COUNT(*) FROM {E} e WHERE e.SYNC_DT = k.SYNC_DT) AS EXPORT_ROWS,
       (SELECT COUNT(*) FROM {G} g WHERE g.SYNC_DT = k.SYNC_DT) AS GTOPAS_ROWS
FROM   {K} k
WHERE  k.SYNC_STATUS = '1'
GROUP BY k.SYNC_DT
ORDER BY k.SYNC_DT;"""),
    ('Explain the run', 'Headers of the run and the file of their Export rows', 'Each part of the run has one Kanban row (1 to 5). It decides the file of all Export rows of that part.',
     f"""SELECT k.PERIOD, k.PART_NO, k.ACTION, k.OPERATION_TYPE,
       CASE k.OPERATION_TYPE WHEN 1 THEN 'EXPORT_PRE -> KANBAN'
                             WHEN 5 THEN 'EXPORT_POST only (header not uploaded)'
                             ELSE 'KANBAN -> EXPORT_POST' END AS UPLOAD_ORDER,
       (SELECT COUNT(*) FROM {E} e WHERE e.SYNC_DT = k.SYNC_DT AND e.PERIOD = k.PERIOD AND e.NSP_PART_NO = k.PART_NO) AS EXPORT_ROWS
FROM   {K} k
WHERE  k.SYNC_STATUS = '1' AND k.SYNC_DT = '{{{{RUN}}}}'
ORDER BY k.PERIOD, k.PART_NO;"""),
    ('Explain the run', 'ROW_ORDER: value sent before vs. now', 'The CTE of V_APPOLE_UPLOAD_EXPORT with PREV_RCS shown: down or 0 = ROW_ORDER 1, up or new = 2.',
     f"""WITH e AS (
  SELECT x.*, LAG(x.MAX_SHIPPING_BOX_RCS) OVER (
           PARTITION BY x.NSP_PART_NO, x.DEST_CODE, x.ORDER_TYPE
           ORDER BY x.PERIOD, x.SYNC_DT, x.STG_ID) AS PREV_RCS
  FROM   {E} x
  WHERE  x.SYNC_STATUS = '1'
)
SELECT e.STG_ID, e.PERIOD, e.NSP_PART_NO, e.BUYER_PD, e.ORDER_TYPE, e.ACTION,
       e.PREV_RCS, e.MAX_SHIPPING_BOX_RCS AS RCS_NOW,
       CASE WHEN e.PREV_RCS IS NOT NULL AND e.MAX_SHIPPING_BOX_RCS < e.PREV_RCS THEN 1 ELSE 2 END AS ROW_ORDER
FROM   e
WHERE  e.SYNC_DT = '{{{{RUN}}}}'
ORDER BY e.PERIOD, e.NSP_PART_NO, ROW_ORDER, e.STG_ID;"""),
] + [('OPERATION_TYPE examples', f'OPERATION_TYPE {n}', OT_TXT[n], OT_SQL(n)) for n in range(1, 6)] + [
    ('Checks', 'Rows waiting for the next [Sync]', 'SYNC_STATUS 0, SYNC_DT NULL: written or updated by SP_STG_WRITE after the last [Sync].',
     f"""SELECT 'KANBAN' AS TBL, STG_ID, PERIOD, PART_NO AS PART, ACTION, 'Max ' || MAX_SHIPPING_BOX_QTY || ', OT ' || OPERATION_TYPE AS VALUE, CREATED_DT
FROM {K} WHERE SYNC_STATUS = '0'
UNION ALL
SELECT 'EXPORT', STG_ID, PERIOD, NSP_PART_NO, ACTION, BUYER_PD || ' ' || ORDER_TYPE || ' = ' || MAX_SHIPPING_BOX_RCS, CREATED_DT
FROM {E} WHERE SYNC_STATUS = '0'
UNION ALL
SELECT 'GTOPAS', STG_ID, PERIOD, P_NO, ACTION, DESTINATION_CODE, CREATED_DT
FROM {G} WHERE SYNC_STATUS = '0'
ORDER BY CREATED_DT;"""),
    ('Checks', 'One unsent row per key (expect no row)', 'A key with two rows SYNC_STATUS 0 breaks the rule of SP_STG_WRITE.',
     f"""SELECT 'KANBAN' AS TBL, PERIOD, PART_NO AS KEY_VALUE, COUNT(*) AS UNSENT_ROWS FROM {K}
WHERE SYNC_STATUS = '0' GROUP BY PERIOD, PART_NO HAVING COUNT(*) > 1
UNION ALL
SELECT 'EXPORT', PERIOD, NSP_PART_NO || ' ' || DEST_CODE || ' ' || ORDER_TYPE, COUNT(*) FROM {E}
WHERE SYNC_STATUS = '0' GROUP BY PERIOD, NSP_PART_NO, DEST_CODE, ORDER_TYPE HAVING COUNT(*) > 1
UNION ALL
SELECT 'GTOPAS', PERIOD, P_NO || ' ' || DESTINATION_CODE, COUNT(*) FROM {G}
WHERE SYNC_STATUS = '0' GROUP BY PERIOD, P_NO, DESTINATION_CODE HAVING COUNT(*) > 1;"""),
    ('Checks', 'Export row without header (expect no row)', 'Every Export row needs a Kanban row of the same part, period and SYNC_DT (or both still 0), or the view drops it.',
     f"""SELECT e.STG_ID, e.PERIOD, e.NSP_PART_NO, e.DEST_CODE, e.SYNC_STATUS, e.SYNC_DT
FROM   {E} e
WHERE  NOT EXISTS (SELECT 1 FROM {K} k
                   WHERE k.PART_NO = e.NSP_PART_NO AND k.PERIOD = e.PERIOD AND k.SYNC_STATUS = e.SYNC_STATUS
                     AND (k.SYNC_DT = e.SYNC_DT OR (k.SYNC_DT IS NULL AND e.SYNC_DT IS NULL)));"""),
    ('Checks', 'AP POLE total ≤ Max after each run', 'Per run and part: the latest Max Shipping Box (RCS) of every Buyer-PD active in the month, against the latest Max. Effective Month: the newest PERIOD ≤ the month counts.',
     f"""WITH runs AS (SELECT DISTINCT SYNC_DT AS RUN, PERIOD, NSP_PART_NO AS PART_NO FROM {E} WHERE SYNC_STATUS = '1'),
ex AS (
  SELECT r.RUN, r.PERIOD, r.PART_NO, x.DEST_CODE, x.ORDER_TYPE, x.MAX_SHIPPING_BOX_RCS AS RCS,
         ROW_NUMBER() OVER (PARTITION BY r.RUN, r.PERIOD, r.PART_NO, x.DEST_CODE, x.ORDER_TYPE
                            ORDER BY x.PERIOD DESC, x.SYNC_DT DESC, x.STG_ID DESC) AS RN
  FROM runs r JOIN {E} x ON x.NSP_PART_NO = r.PART_NO AND x.PERIOD <= r.PERIOD
                         AND x.SYNC_STATUS = '1' AND x.SYNC_DT <= r.RUN),
km AS (
  SELECT r.RUN, r.PERIOD, r.PART_NO, k.MAX_SHIPPING_BOX_QTY AS MAX_QTY,
         ROW_NUMBER() OVER (PARTITION BY r.RUN, r.PERIOD, r.PART_NO
                            ORDER BY k.PERIOD DESC, k.SYNC_DT DESC, k.STG_ID DESC) AS RN
  FROM runs r JOIN {K} k ON k.PART_NO = r.PART_NO AND k.PERIOD <= r.PERIOD
                         AND k.SYNC_STATUS = '1' AND k.SYNC_DT <= r.RUN)
SELECT t.RUN, t.PERIOD, t.PART_NO, t.TOTAL_RCS, km.MAX_QTY,
       CASE WHEN t.TOTAL_RCS <= km.MAX_QTY THEN 'OK' ELSE 'ABOVE MAX' END AS RESULT
FROM  (SELECT RUN, PERIOD, PART_NO, SUM(RCS) AS TOTAL_RCS FROM ex WHERE RN = 1 GROUP BY RUN, PERIOD, PART_NO) t
JOIN   km ON km.RUN = t.RUN AND km.PERIOD = t.PERIOD AND km.PART_NO = t.PART_NO AND km.RN = 1
ORDER BY t.RUN, t.PERIOD, t.PART_NO;"""),
    ('Try a change', 'SP_STG_WRITE: same key changed again', 'DUMMY-005 TAIWAN already waits (3). A new save of the same key updates that row: no new row. Run it, then run "Rows waiting for the next [Sync]".',
     f"""-- what SP_STG_WRITE does for a key that already has a row with SYNC_STATUS 0
UPDATE {E}
   SET MAX_SHIPPING_BOX_RCS = 4, CHANGED_BY = 'RSARI', CHANGED_DT = '2026-12-29 11:00:00'
 WHERE NSP_PART_NO = 'DUMMY-005' AND DEST_CODE = '{DEST['TAIWAN']}' AND ORDER_TYPE = '**'
   AND PERIOD = '202612' AND SYNC_STATUS = '0';"""),
    ('Try a change', 'SP_STG_SYNC: click [Sync] now', 'SQLite version of SP_STG_SYNC: rows 0 -> 1 with one SYNC_DT. Then pick the new run at the top and run the robot queries.',
     f"""-- SP_STG_SYNC @SYNC_DT = '2026-12-30 11:00:00', @CUR = '202612', @NEXT = '202701', @USER_ID = 'RSARI'
UPDATE {K} SET SYNC_STATUS = '1', SYNC_DT = '2026-12-30 11:00:00', CHANGED_BY = 'RSARI', CHANGED_DT = '2026-12-30 11:00:00'
 WHERE SYNC_STATUS = '0' AND PERIOD IN ('202612', '202701');
UPDATE {E} SET SYNC_STATUS = '1', SYNC_DT = '2026-12-30 11:00:00', CHANGED_BY = 'RSARI', CHANGED_DT = '2026-12-30 11:00:00'
 WHERE SYNC_STATUS = '0' AND PERIOD IN ('202612', '202701');
UPDATE {G} SET SYNC_STATUS = '1', SYNC_DT = '2026-12-30 11:00:00', CHANGED_BY = 'RSARI', CHANGED_DT = '2026-12-30 11:00:00'
 WHERE SYNC_STATUS = '0' AND PERIOD = '202612';   -- GTOPAS: Current only"""),
    ('Tables', 'TB_H_STG_APPOLE_KANBAN', 'All rows.', f'SELECT * FROM {K} ORDER BY STG_ID;'),
    ('Tables', 'TB_H_STG_APPOLE_EXPORT', 'All rows.', f'SELECT * FROM {E} ORDER BY STG_ID;'),
    ('Tables', 'TB_H_STG_GTOPAS', 'All rows.', f'SELECT * FROM {G} ORDER BY STG_ID;'),
]
QUERIES = [dict(g=g, t=t, d=d, sql=s.replace('{{{{RUN}}}}', '{{RUN}}')) for g, t, d, s in QUERIES]

# ---------- get queries of the robot per OPERATION_TYPE (same SQL text in the Studio and in SSMS) ----------
GET_RUN = {1: '2026-12-03 11:00:00', 2: '2026-12-03 11:00:00', 3: '2026-12-28 10:00:00', 4: '2026-12-05 11:00:00', 5: '2026-12-08 11:00:00'}
GET_WHY = {
    1: 'Max down. File 1 EXPORT_PRE first (the destinations go down while AP POLE still has the old Max), then file 2 KANBAN with the new Max. No EXPORT_POST row for the part.',
    2: 'Max up. File 2 KANBAN first (the new Max), then file 3 EXPORT_POST (the destinations use it).',
    3: 'Max same (only Pcs/Case, or a new period with the same Max). File 2 KANBAN, then file 3 EXPORT_POST when the part has Export rows.',
    4: 'Never sent. File 2 KANBAN first so AP POLE knows the part, then file 3 EXPORT_POST.',
    5: 'Only the destinations changed. The Kanban row is a header (ACTION KEEP) and is not uploaded: the Kanban query returns no row. File 3 EXPORT_POST only.',
}
UPLOAD = {1: '1 EXPORT_PRE -> 2 KANBAN', 2: '2 KANBAN -> 3 EXPORT_POST', 3: '2 KANBAN -> 3 EXPORT_POST', 4: '2 KANBAN -> 3 EXPORT_POST', 5: '3 EXPORT_POST only'}


def get_sql(n, run):
    """Get queries of one OPERATION_TYPE in one run: Kanban rows (file 2) and Export rows (file 1 or 3) in the order of the template
    columns, helper columns last. run = a literal or @SYNC_DT."""
    head = f"-- OPERATION_TYPE {n}: {GET_WHY[n]}\n-- Upload order of these parts: {UPLOAD[n]}\n"
    kan = f"""-- Kanban rows -> file 2 KANBAN (LLM9Q910){'; returns no row for 5 (header not uploaded)' if n == 5 else ''}
SELECT k.FILE_NO, k.EFFECTIVE_MONTH_YEAR, k.OPERATOR_ID, k.PART_NO, k.PART_NAME,
       k.SHIPPING_BOX_QTY, k.MAX_SHIPPING_BOX_QTY,
       k.OPERATION_TYPE, k.PERIOD, k.STG_ID                          -- helper columns, not written
FROM   V_APPOLE_UPLOAD_KANBAN k
WHERE  k.SYNC_DT = {run} AND k.OPERATION_TYPE = {n}
ORDER BY k.PERIOD, k.PART_NO;"""
    exp = f"""-- Export rows -> file {'1 EXPORT_PRE' if n == 1 else '3 EXPORT_POST'} (LLM9Q880); OPERATION_TYPE from the header of the part
SELECT e.FILE_NO, e.FILE_NAME, e.EFFECTIVE_MONTH_YEAR, e.PART_NO, e.BUYER_PD, e.ORDER_TYPE,
       e.TRANSPORT_CODE, e.MAX_SHIPPING_BOX_RCS,
       h.OPERATION_TYPE, e.ROW_ORDER, e.PERIOD, e.NSP_PART_NO, e.STG_ID   -- helper columns, not written
FROM   V_APPOLE_UPLOAD_EXPORT e
JOIN   TB_H_STG_APPOLE_KANBAN h
       ON  h.SYNC_DT = e.SYNC_DT AND h.PERIOD = e.PERIOD
       AND h.PART_NO = e.NSP_PART_NO AND h.SYNC_STATUS = '1'
WHERE  e.SYNC_DT = {run} AND h.OPERATION_TYPE = {n}
ORDER BY e.FILE_NO, e.PERIOD, e.NSP_PART_NO, e.ROW_ORDER, e.STG_ID;"""
    hdr = f"""-- The header rows (5) of the run, for information
SELECT h.PERIOD, h.PART_NO, h.ACTION, h.PART_STATUS, h.SHIPPING_BOX_QTY, h.MAX_SHIPPING_BOX_QTY, h.OPERATION_TYPE
FROM   TB_H_STG_APPOLE_KANBAN h
WHERE  h.SYNC_STATUS = '1' AND h.SYNC_DT = {run} AND h.OPERATION_TYPE = 5
ORDER BY h.PERIOD, h.PART_NO;""" if n == 5 else ''
    return head + '\n'.join(x for x in (kan, exp, hdr) if x)


ALL_SQL = lambda run: f"""-- Every row the robot uploads in the run, with the OPERATION_TYPE of its part, in upload order
SELECT e.FILE_NO, e.FILE_NAME, h.OPERATION_TYPE, e.NSP_PART_NO AS PART, e.PERIOD, e.ROW_ORDER,
       e.EFFECTIVE_MONTH_YEAR, e.BUYER_PD, e.ORDER_TYPE, e.MAX_SHIPPING_BOX_RCS AS RCS, NULL AS SHIPPING_BOX_QTY, NULL AS MAX_SHIPPING_BOX_QTY
FROM   V_APPOLE_UPLOAD_EXPORT e
JOIN   TB_H_STG_APPOLE_KANBAN h
       ON h.SYNC_DT = e.SYNC_DT AND h.PERIOD = e.PERIOD AND h.PART_NO = e.NSP_PART_NO AND h.SYNC_STATUS = '1'
WHERE  e.SYNC_DT = {run}
UNION ALL
SELECT k.FILE_NO, 'KANBAN', k.OPERATION_TYPE, k.PART_NO, k.PERIOD, NULL,
       k.EFFECTIVE_MONTH_YEAR, NULL, NULL, NULL, k.SHIPPING_BOX_QTY, k.MAX_SHIPPING_BOX_QTY
FROM   V_APPOLE_UPLOAD_KANBAN k
WHERE  k.SYNC_DT = {run}
ORDER BY FILE_NO, PERIOD, PART, ROW_ORDER;"""

QUERIES += [dict(g='Get data per OPERATION_TYPE', t=f'Get OPERATION_TYPE {n}', run=GET_RUN[n],
                 d=f'{GET_WHY[n]} Example run {GET_RUN[n]} (picked when you open the query).', sql=get_sql(n, "'{{RUN}}'")) for n in range(1, 6)]
QUERIES.append(dict(g='Get data per OPERATION_TYPE', t='Get every row of the run with its OPERATION_TYPE',
                    d='All three files of the run in upload order, each row with the OPERATION_TYPE of its part.', sql=ALL_SQL("'{{RUN}}'")))

GET_OUT = os.path.join(ROOT, 'prepare_code', 'sql', 'crossdock_staging_get_by_operation_type.sql')
G = ['-- =====================================================================================================',
     '-- Crossdock staging: get queries of the robot XD07 per OPERATION_TYPE (SQL Server)',
     '-- Generated by deliverables/function_list_v2/erd/proposal_staging_sync/simulation/sql_studio/build_sql_studio.py',
     '-- Read-only DB user. @SYNC_DT = SYNC_DT of the run, given by the parent flow. The robot itself reads the three files with',
     '-- FILE_NO (see crossdock_staging_sync.sql, section 5); these queries split the same rows per OPERATION_TYPE to check a run.',
     '-- Columns in the order of the templates (LLM9Q910 / LLM9Q880), helper columns last. EFFECTIVE_MONTH_YEAR (MM/YYYY):',
     '-- the robot splits it into Effective Month and Effective Year. Example runs: data of crossdock_staging_simulation.sql.',
     '--   OPERATION_TYPE  example run           upload order',
     ] + [f"--   {n}               {GET_RUN[n]}   {UPLOAD[n]}" for n in range(1, 6)] + [
     '-- =====================================================================================================', '']
for n in range(1, 6):
    G += [f"-- ----- OPERATION_TYPE {n} -----", f"DECLARE @SYNC_DT DATETIME2(0) = '{GET_RUN[n]}';", get_sql(n, '@SYNC_DT'), 'GO', '']
G += ['-- ----- every row of a run with its OPERATION_TYPE -----', "DECLARE @SYNC_DT DATETIME2(0) = '2026-12-10 11:00:00';", ALL_SQL('@SYNC_DT'), 'GO', '']
open(GET_OUT, 'w', encoding='utf-8').write('\n'.join(G))
print('saved', os.path.relpath(GET_OUT, ROOT))

page = open(os.path.join(HERE, 'studio_page.html'), encoding='utf-8').read()
payload = json.dumps({'ddl': DDL, 'seed': SEED, 'runs': RUNS, 'defRun': DEF_RUN, 'queries': QUERIES}, ensure_ascii=False).replace('</', '<\\/')
page = page.replace('/*__DATA__*/null', payload)
open(OUT, 'w', encoding='utf-8').write(page)
print('saved', os.path.relpath(OUT, HERE), len(page), 'bytes;', len(QUERIES), 'queries;', len(ins), 'rows')


# ---------- the same data for SQL Server Management Studio (T-SQL) ----------
def tsql_cols(b):
    return [c for c in re.findall(r'^\s{2}(\w+)\s+[A-Z]', b[b.index('('):], re.M) if c != 'CONSTRAINT']


TSQL_OUT = os.path.join(ROOT, 'prepare_code', 'sql', 'crossdock_staging_simulation.sql')
t_tables = [b[b.index('CREATE TABLE'):] for b in batches('TABLE')]
t_indexes = [b[b.index('CREATE INDEX'):] for b in batches('INDEX')]
t_views = [b[b.index('CREATE VIEW'):] for b in batches('VIEW')]
lines = ['-- =====================================================================================================',
         '-- Crossdock staging: simulation data for SQL Server Management Studio',
         '-- Generated by deliverables/function_list_v2/erd/proposal_staging_sync/simulation/sql_studio/build_sql_studio.py',
         '-- Run it in an empty test database. It creates the staging tables and views of crossdock_staging_sync.sql,',
         '-- inserts six [Sync] runs (OPERATION_TYPE 1 to 5) and the rows still waiting, then shows the queries of the robots.',
         '-- Same data as Staging_SQL_Studio.html. Dummy parts and destinations.',
         '-- Runs (SYNC_DT):'] + [f"--   {r['sdt']}  OT {', '.join(map(str, r['ots']))}  {r['label']}" for r in RUNS] + [
         '--   SYNC_STATUS 0 (SYNC_DT NULL): changes of 29-Dec waiting for the next [Sync]',
         '-- =====================================================================================================', '',
         "IF OBJECT_ID('V_APPOLE_UPLOAD_EXPORT', 'V') IS NOT NULL DROP VIEW V_APPOLE_UPLOAD_EXPORT;",
         "IF OBJECT_ID('V_APPOLE_UPLOAD_KANBAN', 'V') IS NOT NULL DROP VIEW V_APPOLE_UPLOAD_KANBAN;",
         "IF OBJECT_ID('V_GTOPAS_CROSSDOCK', 'V') IS NOT NULL DROP VIEW V_GTOPAS_CROSSDOCK;",
         "IF OBJECT_ID('TB_H_STG_GTOPAS', 'U') IS NOT NULL DROP TABLE TB_H_STG_GTOPAS;",
         "IF OBJECT_ID('TB_H_STG_APPOLE_EXPORT', 'U') IS NOT NULL DROP TABLE TB_H_STG_APPOLE_EXPORT;",
         "IF OBJECT_ID('TB_H_STG_APPOLE_KANBAN', 'U') IS NOT NULL DROP TABLE TB_H_STG_APPOLE_KANBAN;", 'GO', '',
         '-- 1. Tables, indexes, views (as in crossdock_staging_sync.sql)']
for b in t_tables + t_indexes + t_views:
    lines += [b, 'GO', '']
lines.append('-- 2. Data')
by_table = {}
for stmt in ins:
    by_table.setdefault(stmt.split()[2], []).append(stmt)
for b in t_tables:
    name = re.search(r'CREATE TABLE (\w+)', b).group(1)
    cols = ', '.join(tsql_cols(b))
    lines += [f'SET IDENTITY_INSERT {name} ON;']
    lines += [s.replace(f'INSERT INTO {name} VALUES', f'INSERT INTO {name} ({cols}) VALUES') for s in by_table[name]]
    lines += [f'SET IDENTITY_INSERT {name} OFF;', 'GO', '']
lines += ['-- 3. Queries. Change @SYNC_DT to look at another run.',
          "DECLARE @SYNC_DT DATETIME2(0) = '" + DEF_RUN + "';", '',
          '-- Parent flow: > 0 = scenario 1 (XD06 then XD07), 0 = scenario 2 (XD07 only)',
          "SELECT COUNT(*) AS GTOPAS_ROWS FROM V_GTOPAS_CROSSDOCK WHERE SYNC_DT = @SYNC_DT;", '',
          '-- XD06 GTOPAS',
          f"SELECT STG_ID, ACTION, DEPOT_CODE, P_NO, DESTINATION_CODE, MAKER_CODE, DOMESTIC_OVERSEAS, TOPAS_ORDER_TYPE, ORDER_TRANSPORTATION_CODE\nFROM V_GTOPAS_CROSSDOCK WHERE SYNC_DT = @SYNC_DT ORDER BY P_NO, DESTINATION_CODE;", '',
          '-- XD07 file 1 EXPORT_PRE, file 2 KANBAN, file 3 EXPORT_POST (a file without rows is not made)',
          'SELECT * FROM V_APPOLE_UPLOAD_EXPORT WHERE SYNC_DT = @SYNC_DT AND FILE_NO = 1 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;',
          'SELECT * FROM V_APPOLE_UPLOAD_KANBAN WHERE SYNC_DT = @SYNC_DT ORDER BY PERIOD, PART_NO;',
          'SELECT * FROM V_APPOLE_UPLOAD_EXPORT WHERE SYNC_DT = @SYNC_DT AND FILE_NO = 3 ORDER BY PERIOD, NSP_PART_NO, ROW_ORDER, STG_ID;', '',
          '-- Headers of the run: OPERATION_TYPE decides the file of the Export rows of the part',
          f"""SELECT k.PERIOD, k.PART_NO, k.ACTION, k.OPERATION_TYPE,
       CASE k.OPERATION_TYPE WHEN 1 THEN 'EXPORT_PRE -> KANBAN' WHEN 5 THEN 'EXPORT_POST only (header not uploaded)'
                             ELSE 'KANBAN -> EXPORT_POST' END AS UPLOAD_ORDER
FROM {K} k WHERE k.SYNC_STATUS = '1' AND k.SYNC_DT = @SYNC_DT ORDER BY k.PERIOD, k.PART_NO;""", '',
          '-- Every run: Kanban headers and their OPERATION_TYPE (SQL Server 2017 or later for STRING_AGG)',
          f"""SELECT k.SYNC_DT, STRING_AGG(CONCAT(k.PART_NO, ' ', k.PERIOD, ' = ', k.OPERATION_TYPE), ', ') AS HEADERS
FROM {K} k WHERE k.SYNC_STATUS = '1' GROUP BY k.SYNC_DT ORDER BY k.SYNC_DT;""", '',
          '-- Every Kanban row per OPERATION_TYPE with the Max sent before it',
          f"""SELECT k.OPERATION_TYPE, k.SYNC_DT, k.PERIOD, k.PART_NO, k.ACTION,
       LAG(k.MAX_SHIPPING_BOX_QTY) OVER (PARTITION BY k.PART_NO ORDER BY k.PERIOD, k.SYNC_DT, k.STG_ID) AS PREV_MAX,
       k.MAX_SHIPPING_BOX_QTY AS MAX_NOW, k.SHIPPING_BOX_QTY
FROM {K} k WHERE k.SYNC_STATUS = '1' ORDER BY k.OPERATION_TYPE, k.SYNC_DT, k.PART_NO;""", '',
          '-- Rows waiting for the next [Sync]',
          f"SELECT 'KANBAN' AS TBL, STG_ID, PERIOD, PART_NO AS PART, ACTION FROM {K} WHERE SYNC_STATUS = '0'\nUNION ALL SELECT 'EXPORT', STG_ID, PERIOD, NSP_PART_NO, ACTION FROM {E} WHERE SYNC_STATUS = '0'\nUNION ALL SELECT 'GTOPAS', STG_ID, PERIOD, P_NO, ACTION FROM {G} WHERE SYNC_STATUS = '0';", '',
          '-- Check: one unsent row per key (expect no row)',
          f"SELECT PERIOD, NSP_PART_NO, DEST_CODE, ORDER_TYPE, COUNT(*) AS UNSENT FROM {E} WHERE SYNC_STATUS = '0'\nGROUP BY PERIOD, NSP_PART_NO, DEST_CODE, ORDER_TYPE HAVING COUNT(*) > 1;", '',
          '-- [Re-send last Sync]',
          f"SELECT MAX(SYNC_DT) AS LAST_RUN FROM (SELECT SYNC_DT FROM {K} WHERE SYNC_STATUS = '1' UNION ALL SELECT SYNC_DT FROM {E} WHERE SYNC_STATUS = '1'\n  UNION ALL SELECT SYNC_DT FROM {G} WHERE SYNC_STATUS = '1') s;", 'GO', '']
open(TSQL_OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('saved', os.path.relpath(TSQL_OUT, ROOT))

# ---------- copy for the web app (menu Master > Staging Sync SQL): sql.js served with the app, not from the CDN ----------
APP_SIM = os.path.join(ROOT, 'app', 'public', 'simulations')
if os.path.isdir(APP_SIM):
    open(os.path.join(APP_SIM, 'staging-sql-studio.html'), 'w', encoding='utf-8').write(
        page.replace('https://cdn.jsdelivr.net/npm/sql.js@1.10.2/dist/sql-asm.js', 'sql-asm.js'))
    print('saved app/public/simulations/staging-sql-studio.html')
