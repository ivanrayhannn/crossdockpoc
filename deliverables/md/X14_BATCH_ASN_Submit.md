# Batch – ASN Submit (X14)

Sumber: UISS-Batch `X14_UISS_Batch_ASNSubmit.xlsx` (0.1 Initial Draft, 15-Oct-26). Dipanggil dari **[Submit ASN] → Yes** di ASN Crossdock Creation (X8).

## Poin utama
- Submit ASN dibuat **batch** supaya layar tidak menunggu. **Proses submit (Submit ID, pemanggilan batch, log) mengikuti ASN existing.** X8 membuat **Submit ID**, menyerahkan draft (#TEMP_ASN_DRAFT) ke batch, lalu kembali ke delivery plan dengan banner Submit ID.
- Batch mengambil **ASN No** dan **Case No** dari **penomoran existing** (last sequence table), lalu insert header + case.
- Hasil ditulis ke **log existing** (Log Monitoring) dengan Submit ID; **tidak ada popup sukses** di layar.
- **All-or-nothing**: gagal → roll back, mapping dari Create ASN dilepas (PO_MAPPED_FLAG kembali N, qty PO kembali), log error.
- Tanpa scheduler (on demand).

## Alur
1. X8: konfirmasi *"Submit ASN? {n} cases ({q} pcs) will be created into {ASN No}, delivery {Delivery Date} · {Rit}."* → Yes.
2. Buat Submit ID, tulis LOG1 (start), jalankan batch.
3. Ambil ASN No / Case No (existing) → insert TB_R_ASN_CROSSDOCK_H (ASN_STATUS `1` Created) dan TB_R_ASN_CROSSDOCK_D.
4. Commit → LOG2 (hasil) + LOG3 (end). Error → roll back + LOG4.

## Log message
| ID | Kapan | Pesan |
|---|---|---|
| LOG1 | Start | ASN submit started. Submit ID <SUBMIT_ID>, <n> cases. |
| LOG2 | ASN tersimpan | <ASN_NO> submitted with status Created. <n> cases are locked. Delivery <DELIVERY_DT> · <RIT>. The ASN is shown in ASN Inquiry. |
| LOG3 | End | ASN submit ended. Status <STATUS>. |
| LOG4 | Error | Failed to submit ASN, Submit ID <SUBMIT_ID>: <ERROR_DETAIL>. |

## TB_R_ASN_CROSSDOCK_H (usulan)
| Kolom | Tipe | Keterangan |
|---|---|---|
| ASN_NO | VARCHAR(TBD) | ASN number (existing numbering) |
| SUPPLIER_CD | VARCHAR(TBD) | Supplier of the cases |
| SUPPLIER_PLANT | VARCHAR(TBD) | Supplier plant |
| DELIVERY_DT | DATE | Delivery Date |
| RIT_CYCLE | VARCHAR(TBD) | Rit |
| ROUTE | VARCHAR(TBD) | Route of the Rit |
| TOTAL_CASE | NUMBER | Number of cases |
| TOTAL_QTY | NUMBER | Delivery Qty (total pieces) |
| ASN_STATUS | VARCHAR(1) | '1' Created (set on submit) |
| CREATED_BY | VARCHAR(TBD) | User who submitted the ASN |
| CREATED_DT | DATETIME | Submit date and time |
| CHANGED_BY | VARCHAR(TBD) | User who last changed the record |
| CHANGED_DT | DATETIME | Last changed date and time |

## TB_R_ASN_CROSSDOCK_D (usulan)
| Kolom | Tipe | Keterangan |
|---|---|---|
| ASN_NO | VARCHAR(TBD) | ASN number (TB_R_ASN_CROSSDOCK_H) |
| CASE_NO | VARCHAR(TBD) | Case number; format and sequence follow the existing numbering (last sequence table) |
| LINE_SEQ | NUMBER(4) | Order line x PO within the case |
| PART_NO | VARCHAR(15) | Part number of the case |
| ORDER_DT | DATE | Customer Order Date |
| DESTINATION_CD | VARCHAR(7) | Destination of the case |
| CUSTOMER_CD | VARCHAR(7) | Customer code |
| CUSTOMER_ORDER_NO | VARCHAR(8) | Customer order number |
| DETAILED_ITEM_NO | VARCHAR(4) | Detailed item number |
| SERIAL_NO | VARCHAR(7) | Serial number |
| QTY | NUMBER(8) | Qty of the line in the case |
| PO_NO | VARCHAR(TBD) | PO number |
| MANIFEST_NO | VARCHAR(TBD) | Manifest number |
| MANIFEST_ITEM_NO | VARCHAR(TBD) | Manifest item number |
| PO_ORDER_QTY | NUMBER(TBD) | PO qty |
| CREATED_BY | VARCHAR(TBD) | User who submitted the ASN |
| CREATED_DT | DATETIME | Submit date and time |
| CHANGED_BY | VARCHAR(TBD) | User who last changed the record |
| CHANGED_DT | DATETIME | Last changed date and time |

## Open points
- Konfirmasi TB_R_ASN_CROSSDOCK_H / _D atau pakai tabel ASN existing.
