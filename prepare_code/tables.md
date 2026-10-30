# Tables (XD01–XD15)

One definition per table (the most complete one among the UISS); "Used by" = functions that define it.

| Table | Kind | New / existing | Used by |
|---|---|---|---|
| #TEMP_INSTRUCTION | temp | proposed | XD09, XD10 |
| TB_H_CROSSDOCK_ORDER_CHANGE | history | proposed | XD11 |
| TB_H_PART_CANDIDATE | history | proposed | XD01, XD02, XD03, XD05, XD06, XD07 |
| TB_M_H0125_DESTINATION | master | existing | XD03, XD05, XD13 |
| TB_M_PART_CANDIDATE | transaction | existing | XD02, XD03, XD05, XD06, XD07 |
| TB_M_PART_CANDIDATE_DEST | transaction | existing | XD03, XD05, XD06, XD07 |
| TB_M_PART_MASTER | master | existing | XD10 |
| TB_R_ACTUAL_DEMAND_SUMMARY | transaction | existing | XD04, XD05 |
| TB_R_CASE_LABEL_LAST_SEQ | transaction | existing | XD10 |
| TB_R_CROSSDOCK_IF_RESULT | transaction | proposed | XD01, XD06, XD07 |
| TB_R_DAILY_ORDER_MANIFEST | transaction | existing | XD10, XD15 |
| TB_R_DAILY_ORDER_PART | transaction | existing | XD10, XD15 |
| TB_R_H0253_ORDER_CONTROL_PRE | transaction | existing | XD08 |
| TB_R_INSTRUCTION | transaction | proposed | XD08, XD10, XD11 |
| TB_R_PART_DAD_RESULT | transaction | proposed | XD05 |
| TB_R_PRA_DAILY_ORDER_MAPPED | transaction | proposed | XD08, XD09, XD10, XD11 |

#### #TEMP_INSTRUCTION (temp, proposed)
Used by: XD09, XD10

Temporary table of one Search run (session): the open qty of the customer order lines (H0253, order status 7, Hold Flag N) in H0253 order, pre-mapped to the supplier POs (Pra Daily Order) and cut into supplier cases and blocks. One row per line x PO x supplier case; PO_NO NULL for the qty still without a PO. Columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| INSTRUCTION_ID | BIGINT | Y | N | Running number within the session |
| SORT_SEQ | NUMBER(6) |  | N | H0253 order of the line within the unit (refer 4.1) |
| CUSTOMER_CD | VARCHAR(7) |  | N | H0253.CUSTOMER_CD (order key 1) |
| CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | H0253.CUSTOMER_ORDER_NO (order key 2) |
| ORDER_DT | DATE |  | N | Customer Order Date (H0253.ORDER_DT; unit and order key 3) |
| ORDER_TIME | VARCHAR(6) |  | N | H0253.ORDER_TIME (order key 4) |
| DESTINATION_CD | VARCHAR(7) |  | N | H0253.DESTINATION_CD (order key 5) |
| DETAILED_ITEM_NO | VARCHAR(4) |  | N | H0253.DETAILED_ITEM_NO (order key 6) |
| SERIAL_NO | VARCHAR(7) |  | N | H0253.SERIAL_NO (order key 7) |
| PART_NO | VARCHAR(15) |  | N | Order part number (H0253.SHIPPING_PART_NO) |
| ORDER_STATUS | VARCHAR(1) |  | N | H0253.ORDER_STATUS ('7' Cross Dock) |
| CUST_ORDER_QTY | NUMBER(8) |  | N | Order status qty of the customer order line (H0253.ORDER_STATUS_QTY) |
| OPEN_ORDER_QTY | NUMBER(8) |  | N | Qty of the line not yet in TB_R_INSTRUCTION (sent or in an open Case List) |
| ASSIGNED_QTY | NUMBER(8) |  | N | Qty of this slice (line x PO x supplier case) |
| PO_NO | VARCHAR(TBD) |  | Y | Supplier PO number (Pra Daily Order Manifest); NULL while not assigned |
| MANIFEST_NO | VARCHAR(TBD) |  | Y | Manifest number |
| MANIFEST_ITEM | VARCHAR(TBD) |  | Y | Manifest item number (Pra Daily Order Part) |
| PO_DT | DATE |  | Y | Order date of the PO (PO Date) |
| ORDER_QTY | NUMBER(TBD) |  | Y | Order qty of the PO part |
| SUPPLIER_CD | VARCHAR(TBD) |  | Y | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) |  | Y | Supplier plant |
| SUB_SUPPLIER_CD | VARCHAR(TBD) |  | Y | Sub supplier code |
| SUB_SUPPLIER_PLANT | VARCHAR(TBD) |  | Y | Sub supplier plant |
| ORDER_TYPE | VARCHAR(TBD) |  | Y | Order type of the PO |
| DOCK_CD | VARCHAR(TBD) |  | Y | Dock code |
| ETD_ORI | DATE |  | Y | Original ETD |
| PCS_CASE | NUMBER(4) |  | N | Pcs per case of the part (TB_M_PART_CANDIDATE.PCS_CASE) |
| CASE_SEQ | NUMBER(4) |  | N | Supplier case of the slice within the unit (PCS_CASE pcs in H0253 order) |
| LINE_SEQ | NUMBER(4) |  | N | Sequence of the slice within the case |
| CUM_DEST_QTY | NUMBER(8) |  | N | Cumulative qty of the destination within the unit up to this slice |
| SEQ_QTY | NUMBER(4) |  | N | Fill of the warehouse case (1 case = 1 destination) of the destination after this slice: 1..PCS_CASE, starts again after PCS_CASE |
| CUT_FLAG | VARCHAR(1) |  | N | 'Y' on the last slice of a case after which the ASN may stop (every destination a multiple of PCS_CASE) |
| GROUP_SEQ | NUMBER(4) |  | N | Case Group (block) of the slice: the cases up to and including a valid cut; the cases of a group are sent together |
| CROSSDOCK_STATUS | VARCHAR(1) |  | N | Status of the block: '6' Ready (the block and every earlier block have a PO) / '7' Not Ready |

#### TB_H_CROSSDOCK_ORDER_CHANGE (history, proposed)
Used by: XD11

New history table (replaces TB_R_CROSSDOCK_CANCEL_RESULT): one record per moved piece of qty (ASN case x cancelled line x replacement line) of Change Order Number (XD11). Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number |
| ASN_NO | VARCHAR(15) |  | N | ASN of the case |
| CASE_NO | VARCHAR(9) |  | N | Case of the moved qty |
| PART_NO | VARCHAR(15) |  | N | Part number |
| FROM_CUSTOMER_CD | VARCHAR(7) |  | N | Cancelled line: CUSTOMER_CD |
| FROM_CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | Cancelled line: CUSTOMER_ORDER_NO |
| FROM_ORDER_DT | DATE |  | N | Cancelled line: ORDER_DT |
| FROM_DESTINATION_CD | VARCHAR(7) |  | N | Cancelled line: DESTINATION_CD |
| FROM_DETAILED_ITEM_NO | VARCHAR(4) |  | N | Cancelled line: DETAILED_ITEM_NO |
| FROM_SERIAL_NO | VARCHAR(7) |  | N | Cancelled line: SERIAL_NO of the status 2 row |
| TO_CUSTOMER_CD | VARCHAR(7) |  | N | Replacement line: CUSTOMER_CD |
| TO_CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | Replacement line: CUSTOMER_ORDER_NO |
| TO_ORDER_DT | DATE |  | N | Replacement line: ORDER_DT |
| TO_DESTINATION_CD | VARCHAR(7) |  | N | Replacement line: DESTINATION_CD (may differ from the cancelled line) |
| TO_DETAILED_ITEM_NO | VARCHAR(4) |  | N | Replacement line: DETAILED_ITEM_NO |
| TO_SERIAL_NO | VARCHAR(7) |  | N | Replacement line: SERIAL_NO |
| QTY | NUMBER(8) |  | N | Moved qty |
| FROM_INSTRUCTION_ID | BIGINT |  | N | Row of TB_R_INSTRUCTION the qty was taken from |
| TO_INSTRUCTION_ID | BIGINT |  | N | Row of TB_R_INSTRUCTION of the replacement (same row when the whole row moved) |
| CREATED_BY | VARCHAR(20) |  | N | Login user ID (D/S team) |
| CREATED_DT | DATETIME |  | N | Server system date-time |

#### TB_H_PART_CANDIDATE (history, proposed)
Used by: XD01, XD02, XD03, XD05, XD06, XD07

History of every change of a crossdock part (Add / Edit by screen or upload, mapping changes, Sync results, status changes and mappings made by the calculation batches). Read by the History setting modal of Part List (index PART_NO, CREATED_DT). Retention: 24 months, counted from the later of CREATED_DT and the Effective Start Date of the part; a monthly housekeeping job deletes older records (period configurable in system master; job TBC).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | Y | Calculation period YYYYMM for MAPPING / SYNC / CALC; NULL for ADD / EDIT (Part List has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / SYNC / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / IF / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY, SYNC_STATUS |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text, e.g. SYNC_MESSAGE of a Failed sync |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (IF batch user ID for SYNC, batch user ID for BATCH) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

#### TB_M_H0125_DESTINATION (master, existing)
Used by: XD03, XD05, XD13

Destination master (I/F H01-25, DVJO820) replicated from DB Surrounding. Structure from the GTOPAS I/F layout; physical names follow the existing table. Key (PK) = unique key of the I/F layout.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| DESTINATION_CD | VARCHAR(7) | Y | N | Used by Crossdock (destination list, upload check, DEST_CODE). No.1 Destination Code |
| CUSTOMER_CD | VARCHAR(7) |  | N | No.2 Customer Code |
| DOMESTIC_OVERSEA_CLASS_CD | VARCHAR(1) |  | N | No.3 Domestic/Overseas Classification Code: '1': Domestic, '2': Overseas |
| ORDER_TRANSPORTATION_CD | VARCHAR(1) |  | N | No.4 Order Transportation Code: 1':AIR '2':SEA '3':LAND |
| BO_INSTRUCTION_CD | VARCHAR(1) |  | N | No.5 B/O Instruction Code: 'K': B/O Cancel, 'F': Follow-up, 'M': Follow-up(S/O only) |
| TARIFF_CD_INPUT_REQUIRED_FLAG | VARCHAR(1) |  | N | No.6 Tariff Code Input Required Flag: '0':Not check '1':check |
| QUP_PROCESS_CD | VARCHAR(1) |  | N | No.7 QUP Process Code: '1':Round-up '2':Not change '3':Round-down |
| DEPOT_DEST_JUDGMENT_FLAG | VARCHAR(1) |  | N | No.8 Depot Destination Judgment Flag: "0":Not Depot "1":Depot |
| REGION_CD | VARCHAR(2) |  | N | No.9 Region Code |
| REGION_NAME | VARCHAR(50) |  | Y | No.10 Region Name |
| DESTINATION_GROUPING_CD | VARCHAR(7) |  | N | No.11 Destination Grouping Code |
| FREIGHT_AGENT_CD_AIR | VARCHAR(3) |  | N | No.12 Freight Agent Code (Air) |
| FREIGHT_AGENT_CD_SEA | VARCHAR(3) |  | N | No.13 Freight Agent Code (Sea) |
| FREIGHT_AGENT_CD_LAND | VARCHAR(3) |  | N | No.14 Freight Agent Code (Land) |
| PACKING_TYPE_CD | VARCHAR(2) |  | N | No.15 Packing Type Code: '1': 40 feet (FCL) '2': 20 feet (FCL) '3': LCL |
| DESTINATION_OPERATOR_CD | VARCHAR(2) |  | Y | No.16 Destination Operator Code |
| DESTINATION_OPERATOR_NAME | VARCHAR(20) |  | Y | No.17 Destination Operator Name |
| DESTINATION_NAME_ENG | VARCHAR(50) |  | N | Used by Crossdock (shown with the code). No.18 Destination Name |
| DESTINATION_NAME_LOCAL | VARCHAR(75) |  | Y | No.19 Destination Name (Local Language) |
| COUNTRY_NAME_ENG | VARCHAR(36) |  | Y | No.20 Country Name |
| COUNTRY_NAME_LOCAL | VARCHAR(54) |  | Y | No.21 Country Name (Local Language) |
| POSTAL_CD_ENG | VARCHAR(10) |  | Y | No.22 Postal Code |
| POSTAL_CD_LOCAL | VARCHAR(15) |  | Y | No.23 Postal Code (Local Language) |
| STATE_CD_ENG | VARCHAR(6) |  | Y | No.24 State Code |
| STATE_CD_LOCAL | VARCHAR(9) |  | Y | No.25 State Code (Local Language) |
| DESTINATION_ADDR1_ENG | VARCHAR(50) |  | N | No.26 Destination Address1 |
| DESTINATION_ADDR2_ENG | VARCHAR(50) |  | Y | No.27 Destination Address2 |
| DESTINATION_ADDR1_LOCAL | VARCHAR(75) |  | Y | No.28 Destination Address1(Local Language) |
| DESTINATION_ADDR2_LOCAL | VARCHAR(75) |  | Y | No.29 Destination Address2(Local Language) |
| PHONE_NO | VARCHAR(20) |  | Y | No.30 Phone No. |
| FAX_NO | VARCHAR(20) |  | Y | No.31 Fax No. |
| REGISTRANT_ID | VARCHAR(13) |  | Y | No.32 Registrant ID |
| UPDATE_JOB_ID | VARCHAR(8) |  | Y | No.33 Update Job ID |
| UPDATE_OPERATOR_ID | VARCHAR(13) |  | Y | No.34 Update Operator ID |
| INTF_UPDATE_DT | TIMESTAMP |  | Y | No.35 Update Date & Time |
| CREATE_DT | TIMESTAMP |  | Y | Created date and time (NSP) |
| CREATE_BY | VARCHAR(TBD) |  | Y | Created by (NSP) |
| UPDATE_DT | TIMESTAMP |  | Y | Updated date and time (NSP) |
| UPDATE_BY | VARCHAR(TBD) |  | Y | Updated by (NSP) |

#### TB_M_PART_CANDIDATE (transaction, existing)
Used by: XD02, XD03, XD05, XD06, XD07

Candidate part setting, one record per part (Part List data, no calculation period). Target of a successful upload.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number; length follows TB_M_PART_MASTER |
| PART_NAME | VARCHAR(TBD) |  | N | Retrieved from TB_M_PART_MASTER by PART_NO |
| MIN_MAD | INT |  | N | Minimum MAD (mandatory); reference compared with the MAD result of the calculation |
| PCS_CASE | INT |  | N | Pieces per case (> 0) |
| MAX_CASE_DAY | INT |  | N | Total Case/Day of the part (> 0) |
| TOTAL_PCS_DAY | INT |  | N | PCS_CASE x MAX_CASE_DAY |
| EFFECTIVE_START_DATE | DATE |  | Y | Effective start date; required while the part is Candidate |
| PART_STATUS | VARCHAR(TBD) |  | N | Candidate / Active / Inactive |
| SYNC_STATUS | CHAR(1) |  | N | 0 = No Sync, 3 = Waiting, 1 = Success, 2 = Failed |
| SYNC_DT | DATETIME |  | Y | Date-time of the last IF function result |
| SYNC_MESSAGE | VARCHAR(TBD) |  | Y | Reason of the last Failed sync |
| LAST_SOURCE | VARCHAR(TBD) |  | N | CALC / SCREEN / UPLOAD |
| LAST_UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload that last changed the record |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_M_PART_CANDIDATE_DEST (transaction, existing)
Used by: XD03, XD05, XD06, XD07

Destination mapping, one record per part, calculation period and destination (Mapping per Destination data). Target of a successful upload.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number; FK to TB_M_PART_CANDIDATE |
| PERIOD | CHAR(6) | Y | N | Calculation period, YYYYMM e.g. 202609; displayed as Sep 2026 |
| DEST_CODE | CHAR(7) | Y | N | Destination code (buyer code + PD code, 7 digits); exists in TB_M_H0125_DESTINATION (Destination Master) |
| CASE_DAY | INT |  | N | Allocated Case/Day of the destination (> 0) |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_M_PART_MASTER (master, existing)
Used by: XD10

Existing part master (MST-03); only PART_NAME is used (by PART_NO).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(15) | Y | N | Part No |
| PART_NAME | VARCHAR(100) |  | N | Part Name |
| SUPPLIER_CD | VARCHAR(4) | Y | N | Supplier Code |
| SUPPLIER_PLANT_CD | VARCHAR(1) | Y | N | Supplier Plabt Code |
| DOCK_CD | VARCHAR(2) | Y | N | Dock Code |
| VALID_FROM | DATETIME | Y | N | Valid From |
| VALID_TO | DATETIME |  | Y | Valid To |

#### TB_R_ACTUAL_DEMAND_SUMMARY (transaction, existing)
Used by: XD04, XD05

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

#### TB_R_CASE_LABEL_LAST_SEQ (transaction, existing)
Used by: XD10

Existing last sequence per supplier + plant (TR-06): the case number (case label) and the ASN number are auto generated from it and the new last sequence is saved here.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| SUPPLIER_CD | VARCHAR(5) | Y | N | Supplier Code |
| SUPPLIER_PLANT_CD | VARCHAR(1) | Y | N | Supplier Plant Code |
| CASE_LABEL_LAST_SEQ | VARCHAR(3) |  | Y | Case Label Last Seq No |
| ASN_LAST_SEQ | VARCHAR(3) |  | Y | ASN Last Seq No |
| CHANGED_BY | VARCHAR(20) |  | Y | Changed By |
| CHANGED_DT | DATETIME |  | Y | Changed Date |

#### TB_R_CROSSDOCK_IF_RESULT (transaction, proposed)
Used by: XD01, XD06, XD07

Dummy table (proposed): send status of the cross dock master per part and target system (XD06 GTOPAS, XD07 AP POLE). The real output is the interface data sent to the target (AP POLE: file by SFTP; GTOPAS: RPA). The overall Sync Status of the part stays in TB_M_PART_CANDIDATE.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number (TB_M_PART_CANDIDATE) |
| TARGET_SYSTEM | VARCHAR(10) | Y | N | 'GTOPAS' (XD06) / 'APPOLE' (XD07) |
| PERIOD | CHAR(6) |  | N | Calculation period of the mapping sent (YYYYMM) |
| IF_STATUS | VARCHAR(1) |  | N | '3' Waiting / '1' Success / '2' Failed |
| IF_DT | DATETIME |  | Y | Date-time of the result of the target system |
| IF_FILE_NAME | VARCHAR(100) |  | Y | Name of the interface file (AP POLE) or RPA input file (GTOPAS) |
| IF_MESSAGE | VARCHAR(500) |  | Y | Reason when Failed; blank when Success |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_R_DAILY_ORDER_MANIFEST (transaction, existing)
Used by: XD10, XD15

Existing ASN manifest (GTOPAS SPS DB structure TR-01). Submit ASN: one row per Pra Daily Order manifest of the cases, all with the same ASN_NO. Only the columns used are listed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| DEPOT_CD | VARCHAR(20) |  | Y | Depot Code |
| SUPPLIER_CD | VARCHAR(4) |  | N | Supplier Code |
| SUPPLIER_PLANT | VARCHAR(1) |  | N | Supplier Plant Code |
| SUB_SUPP_CD | VARCHAR(4) |  | Y | Sub Supplier Code |
| SUB_SUPP_PLANT | VARCHAR(1) |  | Y | Sub Supplier Plant Code |
| SUPPLIER_NAME | VARCHAR(50) |  | Y | Supplier Name |
| PO_NO | VARCHAR(20) |  | N | PO Number |
| ASN_NO | VARCHAR(15) |  | N | ASN Number |
| PO_DATE | DATETIME |  | N | PO Date |
| ASN_DATE | DATETIME |  | N | ASN Date |
| SUB_MANIFEST_NO | VARCHAR(20) | Y | N | Sub Manifest Number |
| MANIFEST_NO | VARCHAR(16) | Y | N | Manifest Number |
| ORDER_TYPE | VARCHAR(1) |  | Y | Order Type |
| CROSS_DOCK_FLAG | VARCHAR(3) |  | Y | Cross Dock Flag |
| DOCK_CD | VARCHAR(2) |  | Y | Dock Code |
| TOTAL_ITEM | NUMERIC |  | N | Total Item |
| TOTAL_QTY | NUMERIC |  | N | Total Quantity |
| DELIVERY_DT_ORI | DATETIME |  | Y | Delivery Date Original |
| SUB_ROUTE_CD | VARCHAR(10) |  | N | Sub Route Code |
| SUB_ROUTE_SEQ | VARCHAR(2) |  | N | Sub Route Seq |
| SUB_ROUTE_DT | DATETIME |  | Y | Sub Route Date |
| STATUS | VARCHAR(3) |  | N | Status |
| CREATED_BY | VARCHAR(20) |  | N | Created By |
| CREATED_DT | DATETIME |  | N | Created Date |

#### TB_R_DAILY_ORDER_PART (transaction, existing)
Used by: XD10, XD15

Existing ASN part (TR-02). Submit ASN: one row per manifest item and case (a case can hold several manifest items). Only the columns used are listed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PO_NO | VARCHAR(20) |  | N | PO Number |
| PO_ITEM | VARCHAR(4) |  | N | PO Item |
| SUB_MANIFEST_NO | VARCHAR(20) | Y | N | Sub Manifest Number |
| MANIFEST_NO | VARCHAR(16) | Y | N | Manifest Number |
| MANIFEST_ITEM | NUMERIC | Y | N | Manifest Item |
| CASE_NO | VARCHAR(9) | Y | N | Case Number |
| ASN_NO | VARCHAR(15) |  | N | ASN Number |
| ASN_DATE | DATETIME |  | N | ASN Date |
| PART_NO | VARCHAR(20) |  | N | Part Number |
| PART_NAME | VARCHAR(50) |  | N | Part Name |
| PO_QTY | NUMERIC |  | N | PO Quantity |
| DELIVERY_QTY | NUMERIC |  | N | Delivery Quantity |
| QTY_PER_CONTAINER | NUMERIC |  | N | Quantity Per Container |
| DELIVERY_DT_ORI | DATETIME |  | Y | Delivery Date Original |
| KANBAN_NO | VARCHAR(4) |  | Y | Kanban Number |
| PART_BARCODE | VARCHAR(25) |  | Y | Part Barcode |
| STATUS | VARCHAR(3) |  | N | Status |
| CREATED_BY | VARCHAR(20) |  | N | Created By |
| CREATED_DT | DATETIME |  | N | Created Date |

#### TB_R_H0253_ORDER_CONTROL_PRE (transaction, existing)
Used by: XD08

Order control data, pre-order picking info (I/F H02-53, DVJO950) replicated from DB Surrounding by XD08. Structure from the GTOPAS I/F layout; physical names follow the existing table. Key (PK) = unique key of the I/F layout. Rows with UPD_STATUS 6 / 2 are kept for tracking (retention optional, TBC). UPD_STATUS is a new NSP column (proposed).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| CUSTOMER_CD | VARCHAR(7) | Y | N | No.1 Customer Code |
| CUSTOMER_ORDER_NO | VARCHAR(8) | Y | N | No.2 Customer Order No. |
| ORDER_DT | DATE | Y | N | No.3 Order Date |
| ORDER_TIME | VARCHAR(6) | Y | N | No.4 Order Time |
| DESTINATION_CD | VARCHAR(7) | Y | N | No.5 Destination Code |
| DETAILED_ITEM_NO | VARCHAR(4) | Y | N | No.6 Detailed Item No. |
| SERIAL_NO | VARCHAR(7) | Y | N | No.7 Serial No., Card No. Part of the key; distinguishes split records of the same order line. Added to the source table by the DB Surrounding team (decided 19-Oct). |
| TOPAS_ORDER_TYPE | VARCHAR(1) |  | Y | No.8 TOPAS Order Type: '1': VOR, '2': E/O, '3': S/O, 'F': F/O |
| DEMAND_HISTORY_UPDATE_DT | DATE |  | Y | No.9 Demand History Update Date |
| SHIPPING_MAKER_CD | VARCHAR(1) |  | Y | No.10 Shipping Maker Code |
| SHIPPING_PART_NO | VARCHAR(15) |  | Y | No.11 Shipping P/No. |
| ORIGINAL_SHIPPING_QTY | NUMBER(8) |  | Y | No.12 Original Shipping Qty or Estimated Shipping Qty |
| ORDER_STATUS_QTY | NUMBER(8) |  | Y | No.13 Order Status Qty |
| ORDER_STATUS | VARCHAR(1) |  | Y | No.14 Order Status: '1': Pending '2': Reject/Cancel '3': B/O '4': Firm Order '5': Vender Direct '6': Allocation '7': Cross Dock In NSP: value of the first replication (normally '7'); a later change is written to UPD_STATUS |
| BO_INSTRUCTION_CD | VARCHAR(1) |  | Y | No.15 B/O Instruction Code: '1': B/O Cancel, '9': Follow-up |
| BO_RELEASE_DT | DATE |  | Y | No.16 B/O Release Date |
| ORDER_GROUP | VARCHAR(2) |  | Y | No.17 Order Group |
| DIRECT_DELIVERY_CD | VARCHAR(1) |  | Y | No.18 Direct Delivery Code: Blank: Not vendor direct delivery '1': Vendor direct delivery |
| DIRECT_DELIVERY_FLAG | VARCHAR(1) |  | Y | No.19 Direct Delivery Flag: '0': Not direct delivery, '1': Direct delivery |
| CURRENCY_CD | VARCHAR(3) |  | Y | No.20 Currency Code |
| LANDED_COST | NUMBER(14,3) |  | Y | No.21 Landed Cost: Constant '0' |
| NET_PRICE | NUMBER(14,3) |  | Y | No.22 Nett Price |
| SALES_PRICE | NUMBER(14,3) |  | Y | No.23 Sales Price |
| EXPORT_SALES_PRICE | NUMBER(14,3) |  | Y | No.24 Export Sales Price |
| SPECIAL_PRICE_CD | VARCHAR(1) |  | Y | No.25 Special Price Code: '1': Special price, Blank: Not applicable |
| ORDER_DISCOUNT_CD | VARCHAR(4) |  | Y | No.26 Order Discount Code |
| ITEM_DISCOUNT_RATE | NUMBER(6,1) |  | Y | No.27 Item Discount Rate |
| FIRST_ALLOCATION_DT | DATE |  | Y | No.28 1st Allocation Date |
| BO_HISTORY_CD | VARCHAR(1) |  | Y | No.29 B/O History Code: '0': Default, '1': B/O |
| ORDER_ERROR_CD | VARCHAR(2) |  | Y | No.30 Order Error Code |
| RA_CD | VARCHAR(2) |  | Y | No.31 R/A Code |
| PENDING_ORDER_CD | VARCHAR(2) |  | Y | No.32 Pending Order Code |
| ORDER_PORTION_CD | VARCHAR(1) |  | Y | No.33 Order Portion Code: '1': Reject '2': Alteration '3': Process '4': Amendment |
| ORDER_STATUS_DT | DATE |  | Y | No.34 Order Status Date |
| SHIPPING_PROCESS_CTRL_CD | VARCHAR(1) |  | Y | No.35 Shipping Process Control Code: Blank: No change '1': Higher priority to B/O |
| PROCUREMENT_PROCESS_CTRL_CD | VARCHAR(1) |  | Y | No.36 Procurement Process Control Code: '1': Skip substitution check '2': Skip large order division (including skipping irregular order check) '3': '2' + skip order taking check '4 |
| DANGEROUS_GOODS_CLASS | VARCHAR(4) |  | Y | No.37 Dangerous Goods Class |
| CREATE_DEMAND_FLAG | VARCHAR(1) |  | Y | No.38 Created Demand Flag: '0': Not created demand, '1': Created demand |
| SPECIAL_CUSTOMER_FLAG | VARCHAR(1) |  | Y | No.39 Special Customer Flag: '0': Regular, '1': Special |
| POSS_TRANSMISSION_JUDG_FLAG | VARCHAR(1) |  | Y | No.40 POSS Transmission Judgment Flag: '0': Out of target, '1': Transmission target |
| REGISTRANT_ID | VARCHAR(13) |  | Y | No.41 Registrant ID |
| UPDATE_JOB_ID | VARCHAR(8) |  | Y | No.42 Update Job ID |
| UPDATE_OPERATION_ID | VARCHAR(13) |  | Y | No.43 Update Operator ID |
| INTF_UPDATE_DT | TIMESTAMP |  | Y | No.44 Update Date & Time |
| HOLD_FLAG | VARCHAR(1) |  | N | NSP column: hold by the D/S team in ASN Cross Dock Creation (XD10) ('Y' / 'N'); 'N' on insert, never changed by XD08 |
| PO_MAPPED_FLAG | VARCHAR(1) |  | N | NSP column: 'Y' when the whole line is in TB_R_INSTRUCTION ([Create ASN] XD10, Change Order Number XD11); 'N' on insert; set back to 'N' by XD08 when a draft of the line is released |
| UPD_STATUS | VARCHAR(1) |  | Y | NSP column: status change in GTOPAS after the first replication: NULL = no change (status 7) / '6' = received or allocated (source ORDER_STATUS 6) / '2' = cancelled (source ORDER_STATUS 2). Set by XD08; lines with UPD_STATUS are not taken by XD09 |
| CREATE_DT | TIMESTAMP |  | Y | Created date and time (NSP) |
| CREATE_BY | VARCHAR(TBD) |  | Y | Created by (NSP) |
| UPDATE_DT | TIMESTAMP |  | Y | Updated date and time (NSP) |
| UPDATE_BY | VARCHAR(TBD) |  | Y | Updated by (NSP) |

#### TB_R_INSTRUCTION (transaction, proposed)
Used by: XD08, XD10, XD11

Real mapping made by [Create ASN]: one row per supplier case x customer order line x PO of the chosen blocks (case and line sequence of XD09). Rows are deleted by [Back] / [Cancel] on the Case List; [Submit ASN] (5.7) fills ASN_NO and CASE_NO. Columns proposed. Rows without ASN_NO are a draft: every run of XD08 releases all drafts (decided 23-Oct); a cancelled line in a submitted ASN is moved to other lines in Change Order Number (XD11).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| INSTRUCTION_ID | BIGINT | Y | N | Running number (identity) |
| SUPPLIER_CD | VARCHAR(TBD) |  | N | Supplier code (one ASN = one Supplier Code + Plant) |
| SUPPLIER_PLANT | VARCHAR(TBD) |  | N | Supplier plant |
| CASE_SEQ | NUMBER(4) |  | N | Case sequence of the Create ASN (Case 1, 2, ...) |
| LINE_SEQ | NUMBER(4) |  | N | Order line x PO within the case |
| PART_NO | VARCHAR(15) |  | N | Part number of the case |
| ORDER_DT | DATE |  | N | Customer Order Date of the case |
| DESTINATION_CD | VARCHAR(7) |  | N | Destination of the case |
| CUSTOMER_CD | VARCHAR(7) |  | N | Customer code |
| CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | Customer order number |
| DETAILED_ITEM_NO | VARCHAR(4) |  | N | Detailed item number |
| SERIAL_NO | VARCHAR(7) |  | N | Serial number |
| QTY | NUMBER(8) |  | N | Qty of the line mapped to the PO in this case |
| PO_NO | VARCHAR(TBD) |  | N | PO number |
| MANIFEST_NO | VARCHAR(TBD) |  | N | Manifest number of the Pra Daily Order |
| MANIFEST_ITEM | VARCHAR(TBD) |  | N | Manifest item number |
| ORDER_QTY | NUMBER(TBD) |  | N | PO qty |
| DELIVERY_DT | DATE |  | N | Delivery Date of the Search |
| RIT_CYCLE | VARCHAR(TBD) |  | N | Rit of the Search (route master, existing) |
| ROUTE | VARCHAR(TBD) |  | N | Route of the Rit (route master, existing) |
| DRAFT_ID | VARCHAR(20) |  | Y | Draft of one [Create ASN] (all rows of the creation); NULL after [Submit ASN] is not needed (ASN_NO filled). Every run of XD08 deletes the rows with ASN_NO NULL |
| ASN_NO | VARCHAR(TBD) |  | Y | ASN number; NULL until the ASN is submitted (5.7) |
| CASE_NO | VARCHAR(TBD) |  | Y | Case number; NULL until submitted (auto generated with the existing last sequence) |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_R_PART_DAD_RESULT (transaction, proposed)
Used by: XD05

Result of the DAD Volume Calculation, one record per calculated part and period. Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PERIOD | CHAR(6) | Y | N | Calculation period YYYYMM (month of the run) |
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

#### TB_R_PRA_DAILY_ORDER_MAPPED (transaction, proposed)
Used by: XD08, XD09, XD10, XD11

New table: mapped qty per Pra Daily Order PO part (instead of a new column in the Pra Daily Order). Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PO_NO | VARCHAR(TBD) | Y | N | PO number (Pra Daily Order Manifest) |
| MANIFEST_NO | VARCHAR(TBD) | Y | N | Manifest number |
| MANIFEST_ITEM | VARCHAR(TBD) | Y | N | Manifest item number (Pra Daily Order Part) |
| PART_NO | VARCHAR(15) |  | N | Part number |
| SUPPLIER_CD | VARCHAR(TBD) |  | N | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) |  | N | Supplier plant |
| ORDER_QTY | NUMBER(TBD) |  | N | PO qty of the part |
| MAPPED_QTY | NUMBER(TBD) |  | N | Qty already mapped to customer orders by [Create ASN]; open qty = ORDER_QTY - MAPPED_QTY |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |
