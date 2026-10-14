# Batch – Crossdock – Order Control Pre (H0253) Sync to NSP (X10)

Replikasi tabel **TB_R_H0253_ORDER_CONTROL_PRE** dari **DB Surrounding** ke **DB NSP**.
Sumber: UISS-Batch `X10_UISS_Batch_H0253OrderControlSync.xlsx` (0.1 Initial Draft). Struktur dari I/F layout G-TOPAS **H02-53 / DVJO950 (Order Control Data File, Pre-order Picking Info)**.

## Poin utama
- Nama tabel di NSP sama dengan sumber.
- Cara simpan: **delete – insert** (isi tabel NSP diganti semua setiap jalan), semua kolom disalin apa adanya.
- **All-or-nothing**: gagal → roll back, NSP tetap berisi data run sukses terakhir.
- G-TOPAS mengirim data **1x/hari (27:30)**; jadwal NSP di system master (**TBC**), setelah data tersedia. Hasil run dicatat di **Log**.
- PK = unique key di I/F layout.

## Struktur tabel (48 kolom)
| No | Kolom | Tipe | PK | Null | Keterangan |
|---|---|---|---|---|---|
| 1 | CUSTOMER_CD | VARCHAR(7) | Y | N | No.1 Customer Code |
| 2 | CUSTOMER_ORDER_NO | VARCHAR(8) | Y | N | No.2 Customer Order No. |
| 3 | ORDER_DT | DATE | Y | N | No.3 Order Date |
| 4 | ORDER_TIME | VARCHAR(6) | Y | N | No.4 Order Time |
| 5 | DESTINATION_CD | VARCHAR(7) | Y | N | No.5 Destination Code |
| 6 | DETAILED_ITEM_NO | VARCHAR(4) | Y | N | No.6 Detailed Item No. |
| 7 | SERIAL_NO | VARCHAR(7) | Y | N | No.7 Serial No., Card No. Part of the key; distinguishes split records of the same order line (taken from the I/F layout, not in the current table export). |
| 8 | TOPAS_ORDER_TYPE | VARCHAR(1) |  | Y | No.8 TOPAS Order Type: '1': VOR, '2': E/O, '3': S/O, 'F': F/O |
| 9 | DEMAND_HISTORY_UPDATE_DT | DATE |  | Y | No.9 Demand History Update Date |
| 10 | SHIPPING_MAKER_CD | VARCHAR(1) |  | Y | No.10 Shipping Maker Code |
| 11 | SHIPPING_PART_NO | VARCHAR(15) |  | Y | No.11 Shipping P/No. |
| 12 | ORIGINAL_SHIPPING_QTY | NUMBER(8) |  | Y | No.12 Original Shipping Qty or Estimated Shipping Qty |
| 13 | ORDER_STATUS_QTY | NUMBER(8) |  | Y | No.13 Order Status Qty |
| 14 | ORDER_STATUS | VARCHAR(1) |  | Y | No.14 Order Status: '1': Pending '2': Reject/Cancel '3': B/O '4': Firm Order '5': Vender Direct '6': Allocation '7': Cross Dock |
| 15 | BO_INSTRUCTION_CD | VARCHAR(1) |  | Y | No.15 B/O Instruction Code: '1': B/O Cancel, '9': Follow-up |
| 16 | BO_RELEASE_DT | DATE |  | Y | No.16 B/O Release Date |
| 17 | ORDER_GROUP | VARCHAR(2) |  | Y | No.17 Order Group |
| 18 | DIRECT_DELIVERY_CD | VARCHAR(1) |  | Y | No.18 Direct Delivery Code: Blank: Not vendor direct delivery '1': Vendor direct delivery |
| 19 | DIRECT_DELIVERY_FLAG | VARCHAR(1) |  | Y | No.19 Direct Delivery Flag: '0': Not direct delivery, '1': Direct delivery |
| 20 | CURRENCY_CD | VARCHAR(3) |  | Y | No.20 Currency Code |
| 21 | LANDED_COST | NUMBER(14,3) |  | Y | No.21 Landed Cost: Constant '0' |
| 22 | NET_PRICE | NUMBER(14,3) |  | Y | No.22 Nett Price |
| 23 | SALES_PRICE | NUMBER(14,3) |  | Y | No.23 Sales Price |
| 24 | EXPORT_SALES_PRICE | NUMBER(14,3) |  | Y | No.24 Export Sales Price |
| 25 | SPECIAL_PRICE_CD | VARCHAR(1) |  | Y | No.25 Special Price Code: '1': Special price, Blank: Not applicable |
| 26 | ORDER_DISCOUNT_CD | VARCHAR(4) |  | Y | No.26 Order Discount Code |
| 27 | ITEM_DISCOUNT_RATE | NUMBER(6,1) |  | Y | No.27 Item Discount Rate |
| 28 | FIRST_ALLOCATION_DT | DATE |  | Y | No.28 1st Allocation Date |
| 29 | BO_HISTORY_CD | VARCHAR(1) |  | Y | No.29 B/O History Code: '0': Default, '1': B/O |
| 30 | ORDER_ERROR_CD | VARCHAR(2) |  | Y | No.30 Order Error Code |
| 31 | RA_CD | VARCHAR(2) |  | Y | No.31 R/A Code |
| 32 | PENDING_ORDER_CD | VARCHAR(2) |  | Y | No.32 Pending Order Code |
| 33 | ORDER_PORTION_CD | VARCHAR(1) |  | Y | No.33 Order Portion Code: '1': Reject '2': Alteration '3': Process '4': Amendment |
| 34 | ORDER_STATUS_DT | DATE |  | Y | No.34 Order Status Date |
| 35 | SHIPPING_PROCESS_CTRL_CD | VARCHAR(1) |  | Y | No.35 Shipping Process Control Code: Blank: No change '1': Higher priority to B/O |
| 36 | PROCUREMENT_PROCESS_CTRL_CD | VARCHAR(1) |  | Y | No.36 Procurement Process Control Code: '1': Skip substitution check '2': Skip large order division (including skipping irregular order check) '3': '2' + skip order taking check '4 |
| 37 | DANGEROUS_GOODS_CLASS | VARCHAR(4) |  | Y | No.37 Dangerous Goods Class |
| 38 | CREATE_DEMAND_FLAG | VARCHAR(1) |  | Y | No.38 Created Demand Flag: '0': Not created demand, '1': Created demand |
| 39 | SPECIAL_CUSTOMER_FLAG | VARCHAR(1) |  | Y | No.39 Special Customer Flag: '0': Regular, '1': Special |
| 40 | POSS_TRANSMISSION_JUDG_FLAG | VARCHAR(1) |  | Y | No.40 POSS Transmission Judgment Flag: '0': Out of target, '1': Transmission target |
| 41 | REGISTRANT_ID | VARCHAR(13) |  | Y | No.41 Registrant ID |
| 42 | UPDATE_JOB_ID | VARCHAR(8) |  | Y | No.42 Update Job ID |
| 43 | UPDATE_OPERATION_ID | VARCHAR(13) |  | Y | No.43 Update Operator ID |
| 44 | INTF_UPDATE_DT | TIMESTAMP |  | Y | No.44 Update Date & Time |
| 45 | CREATE_DT | TIMESTAMP |  | Y | Created date and time (NSP) |
| 46 | CREATE_BY | VARCHAR(TBD) |  | Y | Created by (NSP) |
| 47 | UPDATE_DT | TIMESTAMP |  | Y | Updated date and time (NSP) |
| 48 | UPDATE_BY | VARCHAR(TBD) |  | Y | Updated by (NSP) |

## Catatan
- **SERIAL_NO** (Serial No., Card No.) **dicantumkan** di tabel NSP: bagian dari unique key I/F (no. 7) untuk membedakan pecahan record dari baris order yang sama. Kolom ini tidak ada di export tabel saat ini; di contoh data, 118 kelompok baris punya 6 kolom kunci yang sama (mis. ID1H4571 item 0004 muncul 2x), jadi tanpa SERIAL_NO kunci tidak unik.
- Nama kolom no. 43 di tabel: UPDATE_OPERATION_ID (di H0202: UPDATE_OPERATOR_ID).

## Open points
- Jadwal scheduler NSP; perlu auto retry seperti X6 / X7?
