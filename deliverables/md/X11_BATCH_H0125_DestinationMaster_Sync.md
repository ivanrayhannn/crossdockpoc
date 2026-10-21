# Batch – Crossdock – Destination Master (H0125) Sync to NSP (X11)

Replikasi tabel **TB_M_H0125_DESTINATION** dari **DB Surrounding** ke **DB NSP**.
Sumber: UISS-Batch `X11_UISS_Batch_H0125DestinationMasterSync.xlsx` (0.1 Initial Draft). Struktur dari I/F layout G-System **H01-25 / DVJO820 (Destination Master)**; nama kolom dari contoh data tabel (20261014_tb_m_h0125_destination.xlsx).

## Poin utama
- Nama tabel di NSP sama dengan sumber.
- Cara simpan: **delete – insert** (isi tabel NSP diganti semua setiap jalan), semua kolom disalin apa adanya.
- **All-or-nothing**: gagal → roll back, NSP tetap berisi data run sukses terakhir.
- G-System mengirim data **1x/minggu (21:30)**; jadwal NSP di system master (**TBC**), setelah data tersedia. Hasil run dicatat di **Log**.
- PK = DESTINATION_CD (unique key di I/F layout).

## Struktur tabel (39 kolom)
| No | Kolom | Tipe | PK | Null | Keterangan |
|---|---|---|---|---|---|
| 1 | DESTINATION_CD | VARCHAR(7) | Y | N | Used by Crossdock (destination list, upload check, DEST_CODE). No.1 Destination Code |
| 2 | CUSTOMER_CD | VARCHAR(7) |  | N | No.2 Customer Code |
| 3 | DOMESTIC_OVERSEA_CLASS_CD | VARCHAR(1) |  | N | No.3 Domestic/Overseas Classification Code: '1': Domestic, '2': Overseas |
| 4 | ORDER_TRANSPORTATION_CD | VARCHAR(1) |  | N | No.4 Order Transportation Code: 1':AIR '2':SEA '3':LAND |
| 5 | BO_INSTRUCTION_CD | VARCHAR(1) |  | N | No.5 B/O Instruction Code: 'K': B/O Cancel, 'F': Follow-up, 'M': Follow-up(S/O only) |
| 6 | TARIFF_CD_INPUT_REQUIRED_FLAG | VARCHAR(1) |  | N | No.6 Tariff Code Input Required Flag: '0':Not check '1':check |
| 7 | QUP_PROCESS_CD | VARCHAR(1) |  | N | No.7 QUP Process Code: '1':Round-up '2':Not change '3':Round-down |
| 8 | DEPOT_DEST_JUDGMENT_FLAG | VARCHAR(1) |  | N | No.8 Depot Destination Judgment Flag: "0":Not Depot "1":Depot |
| 9 | REGION_CD | VARCHAR(2) |  | N | No.9 Region Code |
| 10 | REGION_NAME | VARCHAR(50) |  | Y | No.10 Region Name |
| 11 | DESTINATION_GROUPING_CD | VARCHAR(7) |  | N | No.11 Destination Grouping Code |
| 12 | FREIGHT_AGENT_CD_AIR | VARCHAR(3) |  | N | No.12 Freight Agent Code (Air) |
| 13 | FREIGHT_AGENT_CD_SEA | VARCHAR(3) |  | N | No.13 Freight Agent Code (Sea) |
| 14 | FREIGHT_AGENT_CD_LAND | VARCHAR(3) |  | N | No.14 Freight Agent Code (Land) |
| 15 | PACKING_TYPE_CD | VARCHAR(2) |  | N | No.15 Packing Type Code: '1': 40 feet (FCL) '2': 20 feet (FCL) '3': LCL |
| 16 | DESTINATION_OPERATOR_CD | VARCHAR(2) |  | Y | No.16 Destination Operator Code |
| 17 | DESTINATION_OPERATOR_NAME | VARCHAR(20) |  | Y | No.17 Destination Operator Name |
| 18 | DESTINATION_NAME_ENG | VARCHAR(50) |  | N | Used by Crossdock (shown with the code). No.18 Destination Name |
| 19 | DESTINATION_NAME_LOCAL | VARCHAR(75) |  | Y | No.19 Destination Name (Local Language) |
| 20 | COUNTRY_NAME_ENG | VARCHAR(36) |  | Y | No.20 Country Name |
| 21 | COUNTRY_NAME_LOCAL | VARCHAR(54) |  | Y | No.21 Country Name (Local Language) |
| 22 | POSTAL_CD_ENG | VARCHAR(10) |  | Y | No.22 Postal Code |
| 23 | POSTAL_CD_LOCAL | VARCHAR(15) |  | Y | No.23 Postal Code (Local Language) |
| 24 | STATE_CD_ENG | VARCHAR(6) |  | Y | No.24 State Code |
| 25 | STATE_CD_LOCAL | VARCHAR(9) |  | Y | No.25 State Code (Local Language) |
| 26 | DESTINATION_ADDR1_ENG | VARCHAR(50) |  | N | No.26 Destination Address1 |
| 27 | DESTINATION_ADDR2_ENG | VARCHAR(50) |  | Y | No.27 Destination Address2 |
| 28 | DESTINATION_ADDR1_LOCAL | VARCHAR(75) |  | Y | No.28 Destination Address1(Local Language) |
| 29 | DESTINATION_ADDR2_LOCAL | VARCHAR(75) |  | Y | No.29 Destination Address2(Local Language) |
| 30 | PHONE_NO | VARCHAR(20) |  | Y | No.30 Phone No. |
| 31 | FAX_NO | VARCHAR(20) |  | Y | No.31 Fax No. |
| 32 | REGISTRANT_ID | VARCHAR(13) |  | Y | No.32 Registrant ID |
| 33 | UPDATE_JOB_ID | VARCHAR(8) |  | Y | No.33 Update Job ID |
| 34 | UPDATE_OPERATOR_ID | VARCHAR(13) |  | Y | No.34 Update Operator ID |
| 35 | INTF_UPDATE_DT | TIMESTAMP |  | Y | No.35 Update Date & Time |
| 36 | CREATE_DT | TIMESTAMP |  | Y | Created date and time (NSP) |
| 37 | CREATE_BY | VARCHAR(TBD) |  | Y | Created by (NSP) |
| 38 | UPDATE_DT | TIMESTAMP |  | Y | Updated date and time (NSP) |
| 39 | UPDATE_BY | VARCHAR(TBD) |  | Y | Updated by (NSP) |

## Catatan
- Dipakai Crossdock: **DESTINATION_CD** (7 digit = grouping buyer code + PD code; dicek di X4 dan X7) dan **DESTINATION_NAME_ENG** (tampil bersama kode di X3).
- Dicek dengan contoh data: semua 6 kombinasi buyer code + PD code di TB_R_ACTUAL_DEMAND_SUMMARY ada di DESTINATION_CD.
- Kolom audit di tabel asli: **CREATE_DT, CREATE_BY, UPDATE_DT, UPDATE_BY** (sama seperti H0202 / H0253).
- Contoh kode: 9722D10 Toyota Motor Asia (Thailand), 9811110 Toyota Motor Philippines, 9715310 Toyota Motor Vietnam, 9618201 Abdul Latif Jameel (ALJ).

## Open points
- Jadwal scheduler NSP; perlu auto retry seperti X6 / X7?
