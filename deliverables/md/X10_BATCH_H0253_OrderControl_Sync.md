# Batch – Crossdock – Order Control Pre (H0253) Sync to NSP (X10)

Replikasi tabel **TB_R_H0253_ORDER_CONTROL_PRE** dari **DB Surrounding** ke **DB NSP**.
Sumber: UISS-Batch `X10_UISS_Batch_H0253OrderControlSync.xlsx` (0.1 Initial Draft).

## Poin utama
- Nama tabel di NSP sama dengan sumber.
- Cara simpan: **delete – insert** (isi tabel NSP diganti semua setiap jalan), semua kolom disalin apa adanya.
- **All-or-nothing**: gagal → roll back, NSP tetap berisi data run sukses terakhir.
- Jadwal: scheduler di system master (**TBC**). Hasil run dicatat di **Log**.

## Struktur tabel (47 kolom)
Tipe dan panjang mengikuti tabel sumber di DB Surrounding; PK **TBD**.

| No | Kolom | Tipe |
|---|---|---|
| 1 | CUSTOMER_CD | VARCHAR |
| 2 | CUSTOMER_ORDER_NO | VARCHAR |
| 3 | ORDER_DT | DATE |
| 4 | ORDER_TIME | VARCHAR |
| 5 | DESTINATION_CD | VARCHAR |
| 6 | DETAILED_ITEM_NO | VARCHAR |
| 7 | TOPAS_ORDER_TYPE | VARCHAR |
| 8 | DEMAND_HISTORY_UPDATE_DT | DATE |
| 9 | SHIPPING_MAKER_CD | VARCHAR |
| 10 | SHIPPING_PART_NO | VARCHAR |
| 11 | ORIGINAL_SHIPPING_QTY | NUMBER |
| 12 | ORDER_STATUS_QTY | NUMBER |
| 13 | ORDER_STATUS | VARCHAR |
| 14 | BO_INSTRUCTION_CD | VARCHAR |
| 15 | BO_RELEASE_DT | DATE |
| 16 | ORDER_GROUP | VARCHAR |
| 17 | DIRECT_DELIVERY_CD | VARCHAR |
| 18 | DIRECT_DELIVERY_FLAG | VARCHAR |
| 19 | CURRENCY_CD | VARCHAR |
| 20 | LANDED_COST | NUMBER |
| 21 | NET_PRICE | NUMBER |
| 22 | SALES_PRICE | NUMBER |
| 23 | EXPORT_SALES_PRICE | NUMBER |
| 24 | SPECIAL_PRICE_CD | VARCHAR |
| 25 | ORDER_DISCOUNT_CD | VARCHAR |
| 26 | ITEM_DISCOUNT_RATE | NUMBER |
| 27 | FIRST_ALLOCATION_DT | DATE |
| 28 | BO_HISTORY_CD | VARCHAR |
| 29 | ORDER_ERROR_CD | VARCHAR |
| 30 | RA_CD | VARCHAR |
| 31 | PENDING_ORDER_CD | VARCHAR |
| 32 | ORDER_PORTION_CD | VARCHAR |
| 33 | ORDER_STATUS_DT | DATE |
| 34 | SHIPPING_PROCESS_CTRL_CD | VARCHAR |
| 35 | PROCUREMENT_PROCESS_CTRL_CD | VARCHAR |
| 36 | DANGEROUS_GOODS_CLASS | VARCHAR |
| 37 | CREATE_DEMAND_FLAG | VARCHAR |
| 38 | SPECIAL_CUSTOMER_FLAG | VARCHAR |
| 39 | POSS_TRANSMISSION_JUDG_FLAG | VARCHAR |
| 40 | REGISTRANT_ID | VARCHAR |
| 41 | UPDATE_JOB_ID | VARCHAR |
| 42 | UPDATE_OPERATION_ID | VARCHAR |
| 43 | INTF_UPDATE_DT | TIMESTAMP |
| 44 | CREATE_DT | TIMESTAMP |
| 45 | CREATE_BY | VARCHAR |
| 46 | UPDATE_DT | TIMESTAMP |
| 47 | UPDATE_BY | VARCHAR |

## Open points
- Jadwal scheduler dan urutan terhadap batch lain.
- Primary key dan panjang kolom.
- Apakah perlu auto retry seperti X6 / X7.
