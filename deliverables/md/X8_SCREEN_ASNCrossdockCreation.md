# Screen – ASN Crossdock Creation (X8)

Sumber: UISS-Screen `X8_UISS_Screen_ASNCrossdockCreation.xlsx` (0.1 Initial Draft, update 15-Oct-26), mengikuti flow **ASN_Flow_Normal.xlsx** versi 15-Oct.
Prototype: menu **ASN → ASN Creation** (https://ivanrayhannn.github.io/crossdockpoc/#/asn-creation).

## Tujuan
- **Search**: ambil customer order untuk Delivery Date + Rit dan pre-mapping ke PO (fungsi **X12 Get Order**).
- Menampilkan delivery plan per **Part Number + Customer Order Date** (unit) di **level case**.
- Tim D/S: melihat detail destinasi dan **hold / release per destinasi**.
- Memilih unit **Ready**, **Create ASN** (mapping sebenarnya), cek Case List, Download Case Label, **Submit ASN** (status **Created**).

## Alur
```
Pilih Delivery Date (default hari ini, Route tampil) → pilih Rit → [Search] (X12: ambil order FIFO + pre-mapping PO)
  → Delivery plan: Ready / Not Ready (readiness 0 dan Created tidak tampil)
  → centang unit Ready → [Create ASN] (mapping ke PO + #TEMP_ASN_DRAFT) → Sub Screen Case List
  → Download Case Label → Submit?  N: tetap di Case List   Y: simpan ASN (status 1 Created) → notifikasi → ASN Inquiry (X13)
  (Back / Cancel di Case List: mapping dilepas, draft dihapus)
```

## Bagian layar
| Bagian | Isi |
|---|---|
| Delivery | Delivery Date (default **hari ini**), Rit (dari route master), Route (disabled), tombol **Search** |
| Filter | Part Number, Status (All / Ready / Not Ready; D/S juga On Hold), langsung berlaku |
| Header delivery plan | Customer Order Date, Part Number, **Case Qty**, **PO Readiness (case)**, **ASN Status** |
| Default sort | ASN Status: Ready → Not Ready, lalu Part Number ascending |
| Tidak ditampilkan | Unit dengan PO Readiness **0** dan unit yang sudah **Created** (lihat di ASN Inquiry) |
| Detail (D/S) | Per destinasi: Destination, Case, Qty (pcs), **Pcs/Case**, **Hold Flag**. Assignment dan Not Assigned (pcs) tidak ditampilkan |
| Detail customer order (D/S) | Expand dari destinasi: Customer Order No, Detailed Item No, Qty (pcs), PO No, PO Date (mis. order A 4 pcs + order B 2 pcs ke Vietnam) |
| Case List – ringkasan | ASN No (saat submit), Supplier · Plant, Delivery Date · Rit · Route (dari Search), **Delivery Qty** (pcs), jumlah case |
| Case List – tabel | **Case Number – Part Number – Qty**; expand: **PO No – Manifest No – Manifest Item No – PO Qty** |

Kolom PO No, Last PO Date, dan ASN No tidak ada lagi di header.

## Status
| Status | Arti |
|---|---|
| Ready (`6`) | Semua customer order unit sudah berhasil di-assign ke PO (pre-mapping) |
| Not Ready (`7`) | Masih ada customer order di customer order date yang sama yang belum dapat PO (checkbox disabled); tampil hanya kalau PO Readiness ≥ 1 |
| Created (ASN status `1`) | Setelah Submit ASN; tidak tampil lagi di layar ini (lihat ASN Inquiry) |
| On Hold | Semua destinasi unit di-hold (hanya terlihat oleh tim D/S) |

## Hold Flag (tim D/S)
- Kolom tambahan NSP di **TB_R_H0253_ORDER_CONTROL_PRE**; default **N** saat data masuk (X10), dipertahankan saat sync berikutnya.
- Tim D/S mengubahnya **per destinasi** di detail unit (**N · Hold** → Y, **Y · Release** → N); semua order line unit + destinasi itu ikut berubah.
- Destinasi dengan Hold Flag Y tidak diambil saat Search; unit dihitung tanpa destinasi itu.

## Create ASN dan Submit
- **Create ASN** (1 transaksi): **PO_MAPPED_FLAG = Y** di line H0253 unit terpilih, qty terpakai di Pra Daily Order Part, dan draft ke **#TEMP_ASN_DRAFT** (1 case per Part + Customer Order Date + destinasi). Sebelum mapping, unit yang dicentang **dicek ulang** (row lock line H0253): kalau ada line yang **di-hold tim D/S setelah unit dicentang** (sesi lain), create **gagal** untuk seluruh pilihan → **MSG8 (Hold)**, delivery plan di-refresh dan unit yang ter-hold otomatis tidak tercentang. Kalau unit tidak Ready karena sebab lain → MSG7.
- **Back / Cancel**: mapping dilepas (flag & qty dikembalikan), draft dihapus.
- **Submit ASN** dijalankan sebagai **batch X14** (lihat md X14): konfirmasi MSG4 → Yes → sistem membuat **Submit ID** dan menyerahkan draft ke batch. Layar kembali ke delivery plan dan menampilkan Submit ID (MSG6); **tidak ada popup sukses**. Hasilnya (insert **TB_R_ASN_CROSSDOCK_H** status `1` Created + **TB_R_ASN_CROSSDOCK_D**, ASN No & Case No penomoran existing) ditulis ke **log existing** (Log Monitoring) dengan Submit ID.

## Hak akses tampilan
| Pengguna | Header (level case) | Detail destinasi | Hold / Release (destinasi) | Create ASN |
|---|---|---|---|---|
| Supplier | Ya | Tidak | Tidak | Ya |
| Tim D/S | Ya | Ya | Ya | Ya (TBC) |

## Tabel
- **TB_R_H0253_ORDER_CONTROL_PRE** – dibaca lewat X12; diupdate HOLD_FLAG (D/S, per destinasi) dan PO_MAPPED_FLAG (Create ASN).
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

- **TB_R_ASN_CROSSDOCK_H / _D** (usulan) – ditulis oleh batch **X14** saat Submit ASN (struktur di md X14).

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
| MSG8 | Create ASN, ada order yang sudah di-hold D/S (sesi lain) | **Hold:** Some order has been already hold, please select other records |

Pesan sukses submit (*"{ASN No} submitted with status Created. {n} cases are locked. Delivery {Delivery Date} · {Rit}. The ASN is shown in ASN Inquiry."*) tidak lagi berupa popup; menjadi **LOG2** batch X14 di Log Monitoring.

## Simulasi di prototype
- **Konflik hold:** View as Supplier → Search → centang PART-A 13-Oct → pindah ke View as D/S team → expand PART-A 13-Oct → N · Hold salah satu destinasi → kembali ke Supplier (centang masih ada) → Create ASN → muncul pesan Hold, unit ter-uncheck, Case List tidak terbuka. Tiap View as punya seleksi sendiri (seperti 2 user).
- **Submit batch:** Create ASN → Submit ASN → Yes → banner Submit ID → hasil di menu **Log Monitoring**.
- Penjelasan backend lengkap: menu **Common → ASN Backend Process**.

## Catatan prototype
- Switch **Business date** (14 / 15 / 16-Oct) hanya untuk simulasi rilis PO (kondisi 3).
- Toggle **View as (Supplier / D/S team)** hanya untuk simulasi hak akses; di sistem asli dari role login.

## Open points
- Format label (Download Case Label); apakah 1 ASN harus 1 supplier / plant.
- Nama & struktur tabel route master (Rit / Route); konfirmasi TB_R_ASN_CROSSDOCK_H / _D (atau tabel ASN existing).
- Apakah tim D/S juga boleh Create / Submit ASN, atau hanya melihat + hold.
- Struktur Pra Daily Order Part untuk qty terpakai.
