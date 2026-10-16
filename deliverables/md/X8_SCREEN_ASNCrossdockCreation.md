# Screen – ASN Crossdock Creation (X8)

Sumber: UISS-Screen `X8_UISS_Screen_ASNCrossdockCreation.xlsx` (0.1 Initial Draft, update 15-Oct-26), mengikuti flow **ASN_Flow_Normal.xlsx** versi 15-Oct.
Prototype: menu **ASN → ASN Creation** (https://ivanrayhannn.github.io/crossdockpoc/#/asn-creation).

## Tujuan
- **Search**: ambil customer order untuk Delivery Date + Rit dan pre-mapping ke PO (fungsi **X12 Get Order**).
- Menampilkan delivery plan per **Part Number + Customer Order Date** (unit) di **level case**.
- Tim D/S (**super admin**): melihat unit **semua supplier**, detail destinasi dan **hold / release per destinasi**; juga boleh Create / Submit ASN.
- Memilih unit **Ready** dari **1 Supplier Code + Supplier Plant**, **Create ASN** (mapping sebenarnya → **TB_R_INSTRUCTION**), cek Case List, Download Case Label, **Submit ASN** (status **Created**).

## Alur
```
Pilih Delivery Date (default hari ini, Route tampil) → pilih Rit → [Search] (X12: ambil order FIFO + pre-mapping PO → #TEMP_INSTRUCTION)
  → Delivery plan: Ready / Not Ready (readiness 0 dan Created tidak tampil)
  → centang unit Ready → [Create ASN] (cek 1 supplier + hold, mapping ke PO → insert TB_R_INSTRUCTION) → Sub Screen Case List
  → Download Case Label → Submit?  N: tetap di Case List   Y: batch X14 simpan ASN ke TB_R_DAILY_ORDER_MANIFEST / PART (Created) → notifikasi → ASN Inquiry (X13)
  (Back / Cancel di Case List: baris TB_R_INSTRUCTION dihapus, mapping dilepas)
```

## Bagian layar
| Bagian | Isi |
|---|---|
| Delivery | Delivery Date (default **hari ini**), Rit & Route dari **tabel route master existing** (Route disabled), tombol **Search** |
| Filter | Part Number, Status (All / Ready / Not Ready; D/S juga On Hold), langsung berlaku |
| Header delivery plan | Customer Order Date, (D/S: **Supplier · Plant**), Part Number, **Case Qty**, **PO Readiness (case)**, **ASN Status** |
| Data supplier | Supplier: hanya unit Supplier Code + Plant login; tim D/S: semua supplier |
| Default sort | ASN Status: Ready → Not Ready, lalu Part Number ascending |
| Tidak ditampilkan | Unit dengan PO Readiness **0** dan unit yang sudah **Created** (lihat di ASN Inquiry) |
| Detail (D/S) | Per destinasi: Destination, Case, Qty (pcs), **Pcs/Case**, **Hold Flag**. Assignment dan Not Assigned (pcs) tidak ditampilkan |
| Detail customer order (D/S) | Expand dari destinasi: Customer Order No, Detailed Item No, Qty (pcs), PO No, PO Date (mis. order A 4 pcs + order B 2 pcs ke Vietnam) |
| Case List – ringkasan | ASN No (saat submit), Supplier · Plant, Delivery Date · Rit · Route (dari Search), **Delivery Qty** (pcs), jumlah case |
| Case List – tabel | **Case Number – Part Number – Qty**; expand: **PO No – Manifest No – Manifest Item No – PO Qty** |
| Case number | Format **sesuai existing**; di-generate otomatis saat submit dengan cek **last sequence** (disimpan di tabel last sequence existing — note saja, tidak didetailkan) |

Kolom PO No, Last PO Date, dan ASN No tidak ada lagi di header.

## Status
| Status | Arti |
|---|---|
| Ready (`6`) | Semua customer order unit sudah berhasil di-assign ke PO (pre-mapping) |
| Not Ready (`7`) | Masih ada customer order di customer order date yang sama yang belum dapat PO (checkbox disabled); tampil hanya kalau PO Readiness ≥ 1 |
| Created (ASN status `1`) | Setelah Submit ASN; tidak tampil lagi di layar ini (lihat ASN Inquiry) |
| On Hold | Semua destinasi unit di-hold (hanya terlihat oleh tim D/S) |

## Hold Flag (tim D/S)
- Kolom tambahan Supplier System di **TB_R_H0253_ORDER_CONTROL_PRE**; default **N** saat data masuk (X10), dipertahankan saat sync berikutnya.
- Tim D/S mengubahnya **per destinasi** di detail unit (**N · Hold** → Y, **Y · Release** → N); semua order line unit + destinasi itu ikut berubah.
- Destinasi dengan Hold Flag Y tidak diambil saat Search; unit dihitung tanpa destinasi itu.
- **Cancel tidak dilakukan di Supplier System**: cancel datang dari source H0253 dengan **order status `2`** (order crossdock status `7`). Supplier System hanya **hold**; cancel berlaku untuk order yang **HOLD_FLAG = Y** (lihat md X10).

## Create ASN dan Submit
- **1 ASN = 1 Supplier Code + Supplier Plant** (rule existing). Kalau tim D/S mencentang unit dari lebih dari 1 supplier → **MSG9**, tidak ada yang dibuat.
- **Create ASN** (1 transaksi): **PO_MAPPED_FLAG = Y** di line H0253 unit terpilih, **MAPPED_QTY** di tabel baru **TB_R_PRA_DAILY_ORDER_MAPPED**, dan baris mapping di-insert ke **TB_R_INSTRUCTION** (1 case per Part + Customer Order Date + destinasi). Sebelum mapping, unit yang dicentang **dicek ulang** (row lock line H0253): kalau ada line yang **di-hold tim D/S setelah unit dicentang** (sesi lain), create **gagal untuk seluruh pilihan** (termasuk unit yang tidak di-hold) → **MSG8 (Hold)**, delivery plan **otomatis di-refresh** dan semua centang dihapus; user memilih ulang. Kalau unit tidak Ready karena sebab lain → MSG7.
- **Back / Cancel**: baris dihapus dari **TB_R_INSTRUCTION**, PO_MAPPED_FLAG kembali N, MAPPED_QTY dikurangi lagi → unit bisa dipilih lagi.
- **Submit ASN** dijalankan sebagai **batch X14** (lihat md X14): konfirmasi MSG4 → Yes → baris TB_R_INSTRUCTION diserahkan ke batch dengan **Submit ID**; **proses submit mengikuti ASN existing**. Layar kembali ke delivery plan dan menampilkan Submit ID (MSG6); **tidak ada popup sukses**. Hasilnya (insert tabel existing **TB_R_DAILY_ORDER_MANIFEST** status Created + **TB_R_DAILY_ORDER_PART**, ASN No & Case No penomoran existing, ASN_NO/CASE_NO ditulis balik ke TB_R_INSTRUCTION) ditulis ke **log existing** (Log Monitoring) dengan Submit ID.

## Hak akses tampilan
| Pengguna | Header (level case) | Detail destinasi | Hold / Release (destinasi) | Create ASN |
|---|---|---|---|---|
| Supplier | Ya (supplier sendiri) | Tidak | Tidak | Ya |
| Tim D/S (super admin) | Ya (semua supplier) | Ya | Ya | Ya |

## Tabel
- **TB_R_H0253_ORDER_CONTROL_PRE** – dibaca lewat X12; diupdate HOLD_FLAG (D/S, per destinasi) dan PO_MAPPED_FLAG (Create ASN).
- **#TEMP_INSTRUCTION** (temporary) – hasil pre-mapping [Search] / X12, lihat md X12. Belum ada yang disimpan.
- **Route master (existing)** – sumber Rit & Route.
- **TB_R_INSTRUCTION** (transaksi, usulan struktur) – diisi saat **Create ASN**, dihapus saat **Back / Cancel**, ASN_NO / CASE_NO diisi X14 saat submit:

| Kolom | Tipe | Keterangan |
|---|---|---|
| INSTRUCTION_ID | BIGINT | Running number (identity) |
| SUPPLIER_CD | VARCHAR(TBD) | Supplier code (one ASN = one Supplier Code + Plant) |
| SUPPLIER_PLANT | VARCHAR(TBD) | Supplier plant |
| CASE_SEQ | NUMBER(4) | Case sequence of the Create ASN (Case 1, 2, ...) |
| LINE_SEQ | NUMBER(4) | Order line x PO within the case |
| PART_NO | VARCHAR(15) | Part number of the case |
| ORDER_DT | DATE | Customer Order Date of the case |
| DESTINATION_CD | VARCHAR(7) | Destination of the case |
| CUSTOMER_CD | VARCHAR(7) | Customer code |
| CUSTOMER_ORDER_NO | VARCHAR(8) | Customer order number |
| DETAILED_ITEM_NO | VARCHAR(4) | Detailed item number |
| SERIAL_NO | VARCHAR(7) | Serial number |
| QTY | NUMBER(8) | Qty of the line mapped to the PO in this case |
| PO_NO | VARCHAR(TBD) | PO number |
| MANIFEST_NO | VARCHAR(TBD) | Manifest number of the Pra Daily Order |
| MANIFEST_ITEM_NO | VARCHAR(TBD) | Manifest item number |
| PO_ORDER_QTY | NUMBER(TBD) | PO qty |
| DELIVERY_DT | DATE | Delivery Date of the Search |
| RIT_CYCLE | VARCHAR(TBD) | Rit of the Search (route master, existing) |
| ROUTE | VARCHAR(TBD) | Route of the Rit (route master, existing) |
| ASN_NO | VARCHAR(TBD) | ASN number; NULL until the ASN is submitted (X14) |
| CASE_NO | VARCHAR(TBD) | Case number; NULL until submitted (auto generated with the existing last sequence) |
| CREATED_BY | VARCHAR(TBD) | User who created the record |
| CREATED_DT | DATETIME | Created date and time |
| CHANGED_BY | VARCHAR(TBD) | User who last changed the record |
| CHANGED_DT | DATETIME | Last changed date and time |

- **TB_R_PRA_DAILY_ORDER_MAPPED** (tabel baru, usulan) – qty terpakai per PO part (bukan kolom baru di Pra Daily Order); open qty = PO_ORDER_QTY − MAPPED_QTY:

| Kolom | Tipe | Keterangan |
|---|---|---|
| PO_NO | VARCHAR(TBD) | PO number (Pra Daily Order Manifest) |
| MANIFEST_NO | VARCHAR(TBD) | Manifest number |
| MANIFEST_ITEM_NO | VARCHAR(TBD) | Manifest item number (Pra Daily Order Part) |
| PART_NO | VARCHAR(15) | Part number |
| SUPPLIER_CD | VARCHAR(TBD) | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) | Supplier plant |
| PO_ORDER_QTY | NUMBER(TBD) | PO qty of the part |
| MAPPED_QTY | NUMBER(TBD) | Qty already mapped to customer orders by [Create ASN]; open qty = PO_ORDER_QTY - MAPPED_QTY |
| CREATED_BY | VARCHAR(TBD) | User who created the record |
| CREATED_DT | DATETIME | Created date and time |
| CHANGED_BY | VARCHAR(TBD) | User who last changed the record |
| CHANGED_DT | DATETIME | Last changed date and time |

- **TB_R_DAILY_ORDER_MANIFEST / TB_R_DAILY_ORDER_PART** (existing) – ditulis oleh batch **X14** saat Submit ASN (lihat md X14).
- **Tabel last sequence (existing)** – dipakai untuk generate case number (tidak didetailkan).

## Pesan
| ID | Kapan | Pesan |
|---|---|---|
| MSG1 | Hover checkbox, unit On Hold (D/S) | All destinations are on hold |
| MSG2 | Hover checkbox, Not Ready | Not Ready: {k} of {n} cases of {Part No} / {Customer Order Date} are not assigned to a PO yet |
| MSG3 | Search / filter tanpa hasil | No customer order matches this filter. |
| MSG4 | Klik Submit ASN | Submit ASN? {n} cases ({q} pcs) will be created into {ASN No}, delivery {Delivery Date} · {Rit}. |
| MSG5 | Tidak ada rit | No rit cycle available for {Delivery Date}. Choose another delivery date. |
| MSG6 | Klik Yes, submit | Submit ID {Submit ID} is sent to the ASN submit batch. The result is written to Log Monitoring. |
| MSG7 | Create ASN, unit sudah tidak Ready | {Part No} / {Customer Order Date} is no longer Ready. The delivery plan is refreshed. |
| MSG8 | Create ASN, ada order yang sudah di-hold D/S (sesi lain) | **Hold:** Some order has been already hold, please select other records. The delivery plan has been refreshed. |
| MSG9 | Create ASN, unit dari lebih dari 1 supplier / plant (D/S) | **Supplier:** One ASN is for one Supplier Code and Supplier Plant. Please select units of one supplier. |

Pesan sukses submit (*"{ASN No} submitted with status Created. {n} cases are saved. Delivery {Delivery Date} · {Rit}. The ASN is shown in ASN Inquiry."*) tidak lagi berupa popup; menjadi **LOG2** batch X14 di Log Monitoring.

## Simulasi di prototype
- **Konflik hold:** View as Supplier → Search → centang PART-A 13-Oct → pindah ke View as D/S team → expand PART-A 13-Oct → N · Hold salah satu destinasi → kembali ke Supplier (centang masih ada) → Create ASN → muncul pesan Hold, Case List tidak terbuka, semua centang dihapus dan delivery plan otomatis di-refresh (lihat "refreshed hh:mm:ss" di sebelah counter). Tiap View as punya seleksi sendiri (seperti 2 user).
- **Konflik supplier:** View as D/S team → Search → centang PART-B 13-Oct (50221 · 1) dan PART-D 13-Oct (50330 · 2) → Create ASN → pesan Supplier (MSG9).
- **Submit batch:** Create ASN → Submit ASN → Yes → banner Submit ID → hasil di menu **Log Monitoring**.
- Penjelasan backend lengkap: menu **Common → ASN Backend Process**.

## Catatan prototype
- Switch **Business date** (14 / 15 / 16-Oct) hanya untuk simulasi rilis PO (kondisi 3).
- Toggle **View as (Supplier / D/S team)** hanya untuk simulasi hak akses; di sistem asli dari role login.

## Keputusan (konfirmasi 16-Oct)
- Case label / case number **sesuai existing**; case number auto generate dengan cek last sequence (tabel existing).
- 1 ASN = 1 Supplier Code + Supplier Plant.
- Tim D/S = super admin (boleh Create / Submit), view D/S melihat semua supplier.
- Rit / Route dari tabel route master existing.
- ASN setelah submit → TB_R_DAILY_ORDER_MANIFEST dan TB_R_DAILY_ORDER_PART.
- Search = pre-mapping (temp); Create ASN → TB_R_INSTRUCTION; Back / Cancel → keluar dari TB_R_INSTRUCTION.
- Qty terpakai Pra Daily Order → tabel baru TB_R_PRA_DAILY_ORDER_MAPPED.
- Cancel tidak di Supplier System (source H0253 status 2, untuk order HOLD_FLAG = Y); Supplier System hanya hold.

## Open points
- Nama fisik kolom TB_R_INSTRUCTION dan TB_R_PRA_DAILY_ORDER_MAPPED (usulan, perlu review DBA).
