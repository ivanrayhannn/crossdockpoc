# Screen – ASN Crossdock Creation (X8)

Sumber: UISS-Screen `X8_UISS_Screen_ASNCrossdockCreation.xlsx` (0.1 Initial Draft), mengikuti flow **ASN_Flow_Normal.xlsx**.
Prototype: menu **ASN → ASN Creation**. Menggantikan UISS Delivery Plan + ASN Draft sebelumnya.

## Tujuan
- Menampilkan delivery plan part crossdock per **Part Number + Customer Order Date** (= *unit*) dari TB_R_INSTRUCTION.
- Memilih satu atau lebih unit **Ready to Delivery** (boleh beda tanggal / beda part) dan membuat **1 ASN**.
- Case List: cek case, isi Delivery Date + Rit Cycle, Download Case Label, Submit ASN.

## Alur (sesuai flow)
```
Screen ASN Crossdock Creation → pilih delivery plan (Customer Order Date + Part Number)
  → Check Ready Status?  N: Waiting for Next PO (Create ASN disabled)
                         Y: Ready to Delivery → centang → Create ASN (enabled)
  → Sub Screen Case List → Delivery Date, Rit Cycle, Download Case Label
  → Submit?  N: kembali ke Case List   Y: notifikasi sukses → Screen ASN Crossdock Creation → ASN Inquiry (X13)
```

## Aturan utama
| Aturan | Isi |
|---|---|
| Unit | **Part Number + Customer Order Date**; selalu masuk ASN **utuh** (tidak dipecah ke beberapa ASN) |
| Isi 1 ASN | Boleh beberapa unit, **beda tanggal / beda part**. Contoh: hari ini ASN-1 = Part A tgl 14; besok ASN-2 = Part B tgl 14 + Part C tgl 14 + Part A tgl 15 |
| Ready to Delivery | Semua order line unit sudah dapat PO (tidak ada sisa / PO_NO NULL) |
| Waiting for Next PO | Masih ada sisa order di Customer Order Date yang sama yang belum dapat PO; checkbox disabled; jumlah case tetap terlihat |
| Kondisi 1 & 2 | Semua line sudah dapat PO (urutan line berurutan / tidak) → bisa buat ASN, 1 case per destinasi |
| Kondisi 3 | Line unit tersebar ke beberapa PO beda PO Date → baru Ready di **PO Date terakhir** |
| Case | **1 case per Part Number + Customer Order Date + destinasi**; beda part = beda case. Qty H0253 per part + destinasi tidak melebihi pcs/case (boleh terpecah jadi beberapa line, mis. 4+2 atau 1+1+3) |
| Delivery Date / Rit Cycle | Default business date + 1; Minggu tidak ada rit cycle, Sabtu 1 rit cycle |
| Submit | Konfirmasi "Submit ASN?" → simpan TB_R_ASN_CROSSDOCK_H, isi ASN_NO & CASE_NO di TB_R_INSTRUCTION → unit jadi **In ASN** (terkunci) |

## Kolom delivery plan
Customer Order Date, Part Number/Name, Destinations (pcs), Qty, Not assigned, PO No, Last PO Date, Cases, Status (Ready to Delivery / Waiting for Next PO / In ASN), ASN No, expand order lines (Customer Order No, Detailed Item No, Destination, Qty, PO No, PO Date, Assignment).

## Tabel
- **TB_R_INSTRUCTION** – dibaca (delivery plan), diupdate ASN_NO & CASE_NO saat submit. Diisi batch **X12**.
- **TB_R_ASN_CROSSDOCK_H** (usulan) – header ASN, ditulis saat submit:

| Kolom | Tipe | Keterangan |
|---|---|---|
| ASN_NO | VARCHAR(TBD) | ASN-{Supplier}-{YYMMDD of Delivery Date}-{Seq} |
| SUPPLIER_CD | VARCHAR(TBD) | Supplier of the cases |
| SUPPLIER_PLANT | VARCHAR(TBD) | Supplier plant |
| DELIVERY_DT | DATE | Delivery Date |
| RIT_CYCLE | VARCHAR(TBD) | Rit Cycle |
| ROUTE | VARCHAR(TBD) | Route of the Rit Cycle |
| TOTAL_CASE | NUMBER | Number of cases |
| TOTAL_QTY | NUMBER | Total pieces |
| ASN_STATUS | VARCHAR(TBD) | 'SUBMITTED' |
| CREATED_BY | VARCHAR(TBD) | User who submitted the ASN |
| CREATED_DT | DATETIME | Submit date and time |
| CHANGED_BY | VARCHAR(TBD) | User who last changed the record |
| CHANGED_DT | DATETIME | Last changed date and time |

## Pesan
| ID | Kapan | Pesan |
|---|---|---|
| MSG1 | Hover checkbox, unit sudah di ASN | Already in {ASN No} |
| MSG2 | Hover checkbox, Waiting | Waiting for Next PO: {k} pcs of {Part No} / {Customer Order Date} are not assigned to a PO yet |
| MSG3 | Search tanpa hasil | No delivery plan matches this search. |
| MSG4 | Klik Submit ASN | Submit ASN? {n} cases ({q} pcs) will be locked into {ASN No} … |
| MSG5 | Tidak ada rit cycle | No rit cycle available for {Delivery Date}. Choose another delivery date. |
| MSG6 | Submit sukses | {ASN No} submitted. {n} cases are locked. … The ASN is shown in ASN Inquiry. |

## Catatan prototype
- Switch **Business date** (14 / 15 / 16-Oct) hanya untuk simulasi rilis PO (kondisi 3), bukan bagian layar asli.

## Open points
- Format label (Download Case Label); aturan nomor urut ASN; apakah 1 ASN harus 1 supplier / plant.
- Nama & struktur tabel route master (Rit Cycle) dan TB_R_ASN_CROSSDOCK_H.
