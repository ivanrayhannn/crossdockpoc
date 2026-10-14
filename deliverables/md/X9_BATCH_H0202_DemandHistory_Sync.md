# Batch – Crossdock – Demand History Summary (H0202) Sync to NSP (X9)

Replikasi tabel **TB_R_H0202_DEMAND_HISTORY_SUM** dari **DB Surrounding** ke **DB NSP**.
Sumber: UISS-Batch `X9_UISS_Batch_H0202DemandHistorySync.xlsx` (0.1 Initial Draft).

## Poin utama
- Nama tabel di NSP sama dengan sumber.
- Cara simpan: **delete – insert** (isi tabel NSP diganti semua setiap jalan), semua kolom disalin apa adanya.
- **All-or-nothing**: gagal → roll back, NSP tetap berisi data run sukses terakhir.
- Jadwal: scheduler di system master (**TBC**). Hasil run dicatat di **Log**.

## Struktur tabel (40 kolom)
Tipe dan panjang mengikuti tabel sumber di DB Surrounding; PK **TBD**.

| No | Kolom | Tipe |
|---|---|---|
| 1 | CUSTOMER_CD | VARCHAR |
| 2 | CUSTOMER_ORDER_NO | VARCHAR |
| 3 | ORDER_DT | DATE |
| 4 | ORDER_TIME | VARCHAR |
| 5 | DESTINATION_CD | VARCHAR |
| 6 | DETAILED_ITEM_NO | VARCHAR |
| 7 | SERIAL_NO | VARCHAR |
| 8 | DEMAND_HISTORY_UPDATE_CD | VARCHAR |
| 9 | DEPOT_CD | VARCHAR |
| 10 | DOMESTIC_OVERSEAS_CLASS_CD | VARCHAR |
| 11 | REGION_CD | VARCHAR |
| 12 | ORDER_MAKER_CD | VARCHAR |
| 13 | ORDER_PART_NO | VARCHAR |
| 14 | SHIPPING_PART_NO | VARCHAR |
| 15 | DEMAND_HISTORY_DT | DATE |
| 16 | ORDER_TRANSPORTATION_CD | VARCHAR |
| 17 | TOPAS_ORDER_TYPE | VARCHAR |
| 18 | SUPPLIER_CD | VARCHAR |
| 19 | CREATED_DEMAND_FLAG | VARCHAR |
| 20 | ORDER_ERROR_CD | VARCHAR |
| 21 | RA_CD | VARCHAR |
| 22 | ORDER_PORTION_CD | VARCHAR |
| 23 | ORDER_QTY_DEMAND_QTY | NUMBER |
| 24 | SHIPPING_QTY | NUMBER |
| 25 | REJECT_QTY | NUMBER |
| 26 | ETC_CANCEL_QTY | NUMBER |
| 27 | DIRECT_DELIVERY_QTY | NUMBER |
| 28 | FIRM_ORDER_QTY | NUMBER |
| 29 | CROSS_DOCK_QTY | NUMBER |
| 30 | PROCESS_QTY | NUMBER |
| 31 | BO_CANCEL_QTY | NUMBER |
| 32 | NON_TARGET_ORDER_QTY_FLAG | VARCHAR |
| 33 | REGISTRANT_ID | VARCHAR |
| 34 | UPDATE_JOB_ID | VARCHAR |
| 35 | UPDATE_OPERATOR_ID | VARCHAR |
| 36 | INTF_UPDATE_DT | TIMESTAMP |
| 37 | CREATE_DT | TIMESTAMP |
| 38 | CREATE_BY | VARCHAR |
| 39 | UPDATE_DT | TIMESTAMP |
| 40 | UPDATE_BY | VARCHAR |

Catatan: kolom *PO Number, PO Qty, Remaining Order Qty, ASN Number, Case Number* di file export tidak dimasukkan (bukan kolom tabel, terlihat seperti kolom simulasi).

## Open points
- Jadwal scheduler dan urutan terhadap batch lain.
- Primary key dan panjang kolom.
- Apakah perlu auto retry seperti X6 / X7.
