# Screen – ASN Crossdock Creation (X8)

Sumber: UISS-Screen `X8_UISS_Screen_ASNCrossdockCreation.xlsx` (0.1 Initial Draft, update 15-Oct-26), mengikuti flow **ASN_Flow_Normal.xlsx** versi 15-Oct.
Prototype: menu **ASN → ASN Creation** (https://ivanrayhannn.github.io/crossdockpoc/#/asn-creation).

## Tujuan
- **Get Order**: ambil customer order untuk Delivery Date + Rit dan pre-mapping ke PO (fungsi **X12**).
- Menampilkan delivery plan per **Part Number + Customer Order Date** (unit) di **level case**.
- Tim D/S: melihat detail destinasi & order line, dan **hold / release** order line.
- Memilih unit **Ready**, **Create ASN** (mapping sebenarnya), cek Case List, Download Case Label, **Submit ASN** (status **Created**).

## Alur
```
Pilih Delivery Date (Route tampil) → pilih Rit → [Get Order] (X12: ambil order FIFO + pre-mapping PO)
  → Delivery plan: Ready / Not Ready / Created
  → centang unit Ready → [Create ASN] (mapping ke PO + #TEMP_ASN_DRAFT) → Sub Screen Case List
  → Download Case Label → Submit?  N: tetap di Case List   Y: simpan ASN (status 1 Created) → notifikasi → ASN Inquiry (X13)
  (Back / Cancel di Case List: mapping dilepas, draft dihapus)
```

## Bagian layar
| Bagian | Isi |
|---|---|
| Delivery | Delivery Date (default besok), Rit (dari route master), Route (disabled), tombol **Get Order** |
| Filter | Part Number, Status (All / Ready / Not Ready / Created; D/S juga On Hold), langsung berlaku |
| Header delivery plan | Customer Order Date, Part Number, **Case Qty**, **PO Readiness (case)**, **ASN Status** |
| Default sort | ASN Status: Ready → Not Ready → Created, lalu Part Number ascending |
| Detail (D/S) | Per destinasi: Destination, Case, Qty (pcs), Not Assigned (pcs) |
| Detail in detail (D/S) | Expand dari destinasi: order asli per Detailed Item No (mis. order A 4 pcs Vietnam, order B 2 pcs Vietnam), PO No, PO Date, Assignment, **Hold Flag** |
| Case List – ringkasan | ASN No (saat submit), Supplier · Plant, Delivery Date · Rit · Route (dari Get Order), **Delivery Qty** (pcs), jumlah case |
| Case List – tabel | **Case Number – Part Number – Qty**; expand: **PO No – Manifest No – Manifest Item No – PO Qty** |

Kolom PO No, Last PO Date, dan ASN No tidak ada lagi di header.

## Status
| Status | Arti |
|---|---|
| Ready (`6`) | Semua customer order unit sudah berhasil di-assign ke PO (pre-mapping) |
| Not Ready (`7`) | Masih ada customer order di customer order date yang sama yang belum dapat PO (checkbox disabled) |
| Created (ASN status `1`) | Setelah Submit ASN; checkbox tercentang dan terkunci |
| On Hold | Semua line unit di-hold (hanya terlihat oleh tim D/S) |

## Hold Flag (tim D/S)
- Kolom tambahan NSP di **TB_R_H0253_ORDER_CONTROL_PRE**; default **N** saat data masuk (X10), dipertahankan saat sync berikutnya.
- Tim D/S mengubahnya per order line di layar ini (**N · Hold** → Y, **Y · Release** → N).
- Line dengan Hold Flag Y tidak diambil Get Order; unit dihitung tanpa line itu.

## Create ASN dan Submit
- **Create ASN** (1 transaksi): **PO_MAPPED_FLAG = Y** di line H0253 unit terpilih, qty terpakai di Pra Daily Order Part, dan draft ke **#TEMP_ASN_DRAFT** (1 case per Part + Customer Order Date + destinasi). Kalau unit sudah tidak Ready → MSG7.
- **Back / Cancel**: mapping dilepas (flag & qty dikembalikan), draft dihapus.
- **Submit ASN**: insert **TB_R_ASN_CROSSDOCK_H** (ASN_STATUS `1` Created) dan **TB_R_ASN_CROSSDOCK_D** dari draft. ASN No dan Case No mengikuti **penomoran existing** (last sequence table).

## Hak akses tampilan
| Pengguna | Header (level case) | Detail destinasi & order line | Hold / Release | Create ASN |
|---|---|---|---|---|
| Supplier | Ya | Tidak | Tidak | Ya |
| Tim D/S | Ya | Ya | Ya | Ya (TBC) |

## Tabel
- **TB_R_H0253_ORDER_CONTROL_PRE** – dibaca lewat X12; diupdate HOLD_FLAG (D/S) dan PO_MAPPED_FLAG (Create ASN).
- **TB_R_PRA_DAILY_ORDER_PART** – qty terpakai diupdate saat Create ASN (kolom TBD).
- **#TB_R_INSTRUCTION** (temporary) – hasil pre-mapping X12, lihat md X12.
- **#TEMP_ASN_DRAFT** (temporary, usulan):

| Kolom | Tipe | Keterangan |
|---|---|---|
| CASE_SEQ | NUMBER(4) | Case sequence in the draft (Case 1, 2, ...) |
| LINE_SEQ | NUMBER(4) | Order line x PO within the case |
| PART_NO | VARCHAR(15) | Part number of the case |
| ORDER_DT | DATE | Customer Order Date of the case |
| DESTINATION_CD | VARCHAR(7) | Destination of the case |
| CUSTOMER_CD | VARCHAR(7) | Customer code |
| CUSTOMER_ORDER_NO | VARCHAR(8) | Customer order number |
| DETAILED_ITEM_NO | VARCHAR(4) | Detailed item number |
| SERIAL_NO | VARCHAR(7) | Serial number |
| QTY | NUMBER(8) | Qty of the line in the case (mapped to the PO) |
| PO_NO | VARCHAR(TBD) | PO number |
| MANIFEST_NO | VARCHAR(TBD) | Manifest number |
| MANIFEST_ITEM_NO | VARCHAR(TBD) | Manifest item number |
| PO_ORDER_QTY | NUMBER(TBD) | PO qty |
| DELIVERY_DT | DATE | Delivery Date of the Get Order |
| RIT_CYCLE | VARCHAR(TBD) | Rit of the Get Order |
| ROUTE | VARCHAR(TBD) | Route of the Rit |

- **TB_R_ASN_CROSSDOCK_H** (usulan) – header ASN:

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

- **TB_R_ASN_CROSSDOCK_D** (usulan) – case ASN:

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

## Pesan
| ID | Kapan | Pesan |
|---|---|---|
| MSG1 | Hover checkbox, unit Created | Already in {ASN No} |
| MSG2 | Hover checkbox, Not Ready | Not Ready: {k} of {n} cases of {Part No} / {Customer Order Date} are not assigned to a PO yet |
| MSG3 | Get Order / filter tanpa hasil | No customer order matches this filter. |
| MSG4 | Klik Submit ASN | Submit ASN? {n} cases ({q} pcs) will be locked into {ASN No}, delivery {Delivery Date} · {Rit}. |
| MSG5 | Tidak ada rit | No rit cycle available for {Delivery Date}. Choose another delivery date. |
| MSG6 | Submit sukses | {ASN No} submitted with status Created. {n} cases are locked. The ASN is shown in ASN Inquiry. |
| MSG7 | Create ASN, unit sudah tidak Ready | {Part No} / {Customer Order Date} is no longer Ready. The delivery plan is refreshed. |

## Catatan prototype
- Switch **Business date** (14 / 15 / 16-Oct) hanya untuk simulasi rilis PO (kondisi 3).
- Toggle **View as (Supplier / D/S team)** hanya untuk simulasi hak akses; di sistem asli dari role login.

## Open points
- Format label (Download Case Label); apakah 1 ASN harus 1 supplier / plant.
- Nama & struktur tabel route master (Rit / Route); konfirmasi TB_R_ASN_CROSSDOCK_H / _D (atau tabel ASN existing).
- Apakah tim D/S juga boleh Create / Submit ASN, atau hanya melihat + hold.
- Struktur Pra Daily Order Part untuk qty terpakai.
