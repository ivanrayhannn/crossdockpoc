# Batch – Crossdock – Demand History Summary (H0202) Sync to NSP (X9)

Replikasi tabel **TB_R_H0202_DEMAND_HISTORY_SUM** dari **DB Surrounding** ke **DB NSP**.
Sumber: UISS-Batch `X9_UISS_Batch_H0202DemandHistorySync.xlsx` (0.1 Initial Draft). Struktur dari I/F layout G-TOPAS **H02-02 / DVJO250 (Demand History Summary File)**.

## Poin utama
- Nama tabel di NSP sama dengan sumber.
- Cara simpan: **delete – insert** (isi tabel NSP diganti semua setiap jalan), semua kolom disalin apa adanya.
- **All-or-nothing**: gagal → roll back, NSP tetap berisi data run sukses terakhir.
- G-TOPAS mengirim data **1x/hari (26:00)**; jadwal NSP di system master (**TBC**), setelah data tersedia. Hasil run dicatat di **Log**.
- PK = unique key di I/F layout.

## Struktur tabel (40 kolom)
| No | Kolom | Tipe | PK | Null | Keterangan |
|---|---|---|---|---|---|
| 1 | CUSTOMER_CD | VARCHAR(7) | Y | N | No.1 Customer Code |
| 2 | CUSTOMER_ORDER_NO | VARCHAR(8) | Y | N | No.2 Customer Order No. |
| 3 | ORDER_DT | DATE | Y | N | No.3 Order Date |
| 4 | ORDER_TIME | VARCHAR(6) | Y | N | No.4 Order Time |
| 5 | DESTINATION_CD | VARCHAR(7) | Y | N | No.5 Destination Code |
| 6 | DETAILED_ITEM_NO | VARCHAR(4) | Y | N | No.6 Detailed Item No. |
| 7 | SERIAL_NO | VARCHAR(7) | Y | N | No.7 Serial No. |
| 8 | DEMAND_HISTORY_UPDATE_CD | VARCHAR(2) | Y | N | No.8 Demand History Update Code: '01': Reject Records Update '02': Irregular Order P Cancel Update '03': Vendor Direct Shipment Update '05': Firm Order History Update '06':  |
| 9 | DEPOT_CD | VARCHAR(2) |  | Y | No.9 Depot Code |
| 10 | DOMESTIC_OVERSEAS_CLASS_CD | VARCHAR(1) |  | Y | No.10 Domestic/Overseas Classification Code: '1': Domestic, '2': Overseas |
| 11 | REGION_CD | VARCHAR(2) |  | Y | No.11 Region Code |
| 12 | ORDER_MAKER_CD | VARCHAR(1) |  | Y | No.12 Order Maker Code |
| 13 | ORDER_PART_NO | VARCHAR(15) |  | Y | No.13 Order P/No. |
| 14 | SHIPPING_PART_NO | VARCHAR(15) |  | Y | No.14 Shipping P/No. |
| 15 | DEMAND_HISTORY_DT | DATE |  | Y | No.15 Demand History Date |
| 16 | ORDER_TRANSPORTATION_CD | VARCHAR(1) |  | Y | No.16 Order Transportation Code: '1': AIR, '2': SEA, '3': LAND |
| 17 | TOPAS_ORDER_TYPE | VARCHAR(1) |  | Y | No.17 TOPAS Order Type: '1': VOR, '2': E/O, '3': S/O, 'F': F/O |
| 18 | SUPPLIER_CD | VARCHAR(5) |  | Y | No.18 Supplier Code |
| 19 | CREATED_DEMAND_FLAG | VARCHAR(1) |  | Y | No.19 Created Demand Flag: '0': No created demand, '1': Created demand |
| 20 | ORDER_ERROR_CD | VARCHAR(2) |  | Y | No.20 Order Error Code |
| 21 | RA_CD | VARCHAR(2) |  | Y | No.21 R/A Code |
| 22 | ORDER_PORTION_CD | VARCHAR(1) |  | Y | No.22 Order Portion Code: '1': Reject '2': Alteration '3': Process '4': Amendment |
| 23 | ORDER_QTY_DEMAND_QTY | NUMBER(8) |  | Y | No.23 Order Qty , Demand Qty |
| 24 | SHIPPING_QTY | NUMBER(8) |  | Y | No.24 Original Shipping Qty or Estimated Shipping Qty |
| 25 | REJECT_QTY | NUMBER(8) |  | Y | No.25 Reject Qty |
| 26 | ETC_CANCEL_QTY | NUMBER(8) |  | Y | No.26 ETC Cancel Qty |
| 27 | DIRECT_DELIVERY_QTY | NUMBER(8) |  | Y | No.27 Direct Delivery Qty |
| 28 | FIRM_ORDER_QTY | NUMBER(8) |  | Y | No.28 Firm Order Qty |
| 29 | CROSS_DOCK_QTY | NUMBER(8) |  | Y | No.29 Cross Dock Qty |
| 30 | PROCESS_QTY | NUMBER(8) |  | Y | No.30 Process Qty |
| 31 | BO_CANCEL_QTY | NUMBER(8) |  | Y | No.31 B/O Cancel Qty |
| 32 | NON_TARGET_ORDER_QTY_FLAG | VARCHAR(1) |  | Y | No.32 Non-Target of Cumulative Order Qty Flag: '0':Target of cumulation (Regular or 1st division of large order division) '1': Non-target of cumulation (2nd or later divisions of large or |
| 33 | REGISTRANT_ID | VARCHAR(13) |  | Y | No.33 Registrant ID |
| 34 | UPDATE_JOB_ID | VARCHAR(8) |  | Y | No.34 Update Job ID |
| 35 | UPDATE_OPERATOR_ID | VARCHAR(13) |  | Y | No.35 Update Operator ID |
| 36 | INTF_UPDATE_DT | TIMESTAMP |  | Y | No.36 Update Date & Time |
| 37 | CREATE_DT | TIMESTAMP |  | Y | Created date and time (NSP) |
| 38 | CREATE_BY | VARCHAR(TBD) |  | Y | Created by (NSP) |
| 39 | UPDATE_DT | TIMESTAMP |  | Y | Updated date and time (NSP) |
| 40 | UPDATE_BY | VARCHAR(TBD) |  | Y | Updated by (NSP) |

## Catatan
- Kolom *PO Number, PO Qty, Remaining Order Qty, ASN Number, Case Number* di file export tidak dimasukkan (tidak ada di I/F layout).

## Open points
- Jadwal scheduler NSP; perlu auto retry seperti X6 / X7?
