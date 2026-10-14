# Batch – Customer Order – PO Mapping / TB_R_INSTRUCTION (X12)

Sumber: UISS-Batch `X12_UISS_Batch_CustomerOrderPOMapping.xlsx` (0.1 Initial Draft), bagian "Get Data → Insert result mapping Cust Order PO Supplier" di flow ASN.

## Alur
1. **Customer order** dari **TB_R_H0253_ORDER_CONTROL_PRE** (hasil X10, sumber H0253 di SRD): Order Status = **7** (Cross Dock), data terbaru, belum (penuh) terpasang ke PO.
2. **PO supplier** dari **TB_R_PRA_DAILY_ORDER_MANIFEST + TB_R_PRA_DAILY_ORDER_PART**: Crossdock Flag = **X**, data terbaru, belum terpasang ke customer order, urut Order Date naik.
3. Pasangkan **per part number, FIFO berdasarkan Customer Order Date** (lalu Order Time, Customer Order No, Detailed Item No, Serial No). Satu line boleh terpecah ke beberapa PO; sisa PO tetap terbuka untuk order berikutnya.
4. Simpan ke **TB_R_INSTRUCTION**: 1 baris per pasangan line × PO; sisa line tanpa PO = 1 baris dengan PO_NO NULL (REMAINING_ORDER_QTY), diganti saat ada PO berikutnya.
5. All-or-nothing; hasil dicatat di Log. Jadwal di system master (TBC), setelah X10 dan Pra Daily Order tersedia.

## Contoh (PART-C, 6 pcs/case)
- 14-Oct: PO1 12 pcs → CO-13001 (4), CO-13004 (2), CO-13003 (6) terpasang; 6 pcs sisa → **Waiting for Next PO**.
- 15-Oct: PO2 6 pcs → sisa line terpasang → unit PART-C 13-Oct **Ready to Delivery** di 15-Oct (kondisi 3).

## TB_R_INSTRUCTION (usulan struktur)
| Kolom | Tipe | Keterangan |
|---|---|---|
| INSTRUCTION_ID | BIGINT | Running number (identity) |
| CUSTOMER_CD | VARCHAR(7) | H0253.CUSTOMER_CD |
| CUSTOMER_ORDER_NO | VARCHAR(8) | H0253.CUSTOMER_ORDER_NO |
| ORDER_DT | DATE | Customer Order Date (H0253.ORDER_DT) |
| DESTINATION_CD | VARCHAR(7) | H0253.DESTINATION_CD (TB_M_H0125_DESTINATION) |
| DETAILED_ITEM_NO | VARCHAR(4) | H0253.DETAILED_ITEM_NO |
| SERIAL_NO | VARCHAR(7) | H0253.SERIAL_NO |
| PART_NO | VARCHAR(15) | Order part number (H0253.SHIPPING_PART_NO) |
| ORDER_STATUS | VARCHAR(1) | H0253.ORDER_STATUS ('7' Cross Dock) |
| CUST_ORDER_QTY | NUMBER(8) | Order status qty of the customer order line (H0253.ORDER_STATUS_QTY) |
| ASSIGNED_QTY | NUMBER(8) | Qty of the line assigned to this PO (0 for the not-assigned row) |
| REMAINING_ORDER_QTY | NUMBER(8) | Qty of the line still without a PO after this assignment |
| PO_NO | VARCHAR(TBD) | Supplier PO number (Pra Daily Order Manifest); NULL while not assigned |
| MANIFEST_NO | VARCHAR(TBD) | Manifest number |
| MANIFEST_ITEM_NO | VARCHAR(TBD) | Manifest item number (Pra Daily Order Part) |
| PO_ORDER_DT | DATE | Order date of the PO (PO Date) |
| PO_ORDER_QTY | NUMBER(TBD) | Order qty of the PO part |
| SUPPLIER_CD | VARCHAR(TBD) | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) | Supplier plant |
| SUB_SUPPLIER_CD | VARCHAR(TBD) | Sub supplier code |
| SUB_SUPPLIER_PLANT | VARCHAR(TBD) | Sub supplier plant |
| ORDER_TYPE | VARCHAR(TBD) | Order type of the PO |
| DOCK_CD | VARCHAR(TBD) | Dock code |
| ETD_ORI | DATE | Original ETD |
| ASN_NO | VARCHAR(TBD) | ASN number; filled by ASN Crossdock Creation [Submit ASN] |
| CASE_NO | VARCHAR(TBD) | Case number; filled by ASN Crossdock Creation [Submit ASN] |
| CREATED_BY | VARCHAR(TBD) | User who created the record |
| CREATED_DT | DATETIME | Created date and time |
| CHANGED_BY | VARCHAR(TBD) | User who last changed the record |
| CHANGED_DT | DATETIME | Last changed date and time |

ASN_NO dan CASE_NO diisi oleh X8 saat Submit ASN.

## Open points
- Struktur fisik TB_R_PRA_DAILY_ORDER_MANIFEST / PART dan cara menandai "sudah terpasang".
- Jadwal batch; perlu auto retry seperti X6 / X7?
