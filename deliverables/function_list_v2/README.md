# Crossdock – Function List v2 (UISS XD01–XD15)

Folder ini berisi UISS sesuai **function list terbaru** (18-Oct-26). Dokumen versi pertama (X1–X15) di `deliverables/uiss`, `deliverables/uiss_specs` dan `deliverables/md` **tidak diubah**.

| Folder | Isi |
|---|---|
| `uiss/` | UISS Excel XD01–XD15 (0.1 Initial Draft, FID Rayhan, 18-Oct-26) |
| `md/` | Ringkasan per fungsi (Bahasa Indonesia) |
| `specs/` | Builder Python + spec JSON (dibuat dari spec versi pertama, tanpa mengubahnya) |
| `build_all_v2.sh` | Build ulang semua UISS v2 (jalankan dari root repo) |

Nama sistem di UISS tetap **G-System** dan **NSP** (rename T-System / Supplier System hanya di prototype web).

## Function list dan asal dokumen

| ID | Function | Tipe | Asal (versi pertama) | Perubahan |
|---|---|---|---|---|
| XD01 | Cross Dock Part Master Screen | Screen | X1 Part List + X3 Mapping per Destination | **Digabung** jadi 1 screen dengan 2 tab. Sync sekarang menjalankan XD06 + XD07 |
| XD02 | Cross Dock Part Master Upload Batch | Batch | X2 Part List Upload | Ganti ID / nama, referensi ke XD01 / XD05 |
| XD03 | Part and Destination Mapping Upload Batch | Batch | X4 Mapping per Destination Upload | Ganti ID / nama |
| XD04 | Actual Demand Summary Synch to NSP | Batch | X5 | Tetap replicate tabel Actual Demand Summary ke NSP (delete – insert) |
| XD05 | DAD Volume Calculation Batch | Batch | X6 DAD Volume Calc + X7 Mapping Destination Calc | **Digabung**: proses 1 (status part) lalu proses 2 (mapping destinasi) |
| XD06 | IF Cross Dock Master to G-System | Batch | bagian RPA dari X3 (Sync) | **Baru / dipisah**: file SFTP berisi Part List + Mapping per Destination ke G-System |
| XD07 | IF Cross Dock Master to AP POLE | Batch | bagian RPA dari X3 (Sync) | **Baru / dipisah**: file SFTP dengan data sama ke AP POLE |
| XD08 | Order Control Information to NSP Batch | Batch | X10 H0253 Sync | **Satu batch H0253** (23-Oct, XD12 digabung): status 7 / 6 / 2, UPD_STATUS, lepas semua draft |
| XD09 | Mapping Customer Order and PO Batch | Batch | X12 Get Order (pre-mapping) | Ganti ID / nama (tetap on demand dari [Search] di XD10) |
| XD10 | ASN Cross Dock Creation Screen | Screen | X8 + X14 ASN Submit | **Digabung**: proses Submit ASN jadi section 5.7 |
| XD11 | Change Order Number Screen | Screen | – | **Baru 23-Oct** (menggantikan Cancel Crossdock Customer Order Batch): layar D/S ganti order number untuk qty cancel di ASN |
| ~~XD12~~ | ~~Order Control Information to NSP Batch (Cancel)~~ | – | – | **Dihapus 23-Oct**, digabung ke XD08 |
| XD13 | Destination Master Synch into NSP | Batch | X11 H0125 Sync | Ganti ID / nama |
| XD14 | DAD Volume Calculation Result Screen (Buffer) | Screen | – | **Tidak dipakai** (keputusan 19-Oct) |
| XD15 | ASN Crossdock Inquiry Screen (Buffer) | Screen | X13 | Ganti ID / nama |

Tidak dipakai (dikonfirmasi 19-Oct): **X9** H0202 Demand History Sync, **X15** Menu Settings (hanya admin panel prototype), **XD14**.

## Keputusan (konfirmasi 18-Oct)
| No | Topik | Keputusan |
|---|---|---|
| 1 | XD05 | **Disetujui**: X6 + X7 digabung. Satu run = proses 1 lalu proses 2; [Run calculation (Part List)] = proses 1 + 2, [Run calculation (Mapping)] = proses 2 saja |
| 2 | XD10 | **Disetujui**: X14 (Submit ASN) masuk ke XD10 (section 5.7) |
| 3 | XD06 / XD07 | Kirim lewat **file SFTP – Option #3** (NSP Send IF → SFTP TMMIN → SFTP TMA → receive IF → AP POLE Crossdock Kanban Part Master / Crossdock Export Part Master). **TB_R_CROSSDOCK_IF_RESULT = tabel dummy** untuk status kirim; output sebenarnya file ke G-System (XD06) dan AP POLE (XD07). Field dan proses bisnis sudah didetailkan (Interface Data di UISS dan md). Sync Status gabungan **disetujui** |
| 4 | XD08 / XD12 / tabel H0253 | **Satu tabel replicate upsert** (delta INTF_UPDATE_DT, partial cancel = serial baru, status 6 / 2 disimpan untuk tracking); kolom baru UPD_STATUS; tabel cancel terpisah dihapus |
| 5 | Urutan job | **Disetujui**: XD12 → XD11 → XD08 |
| 6 | XD11 | Cancel bisa **dengan atau tanpa Hold Flag Y**. Perhitungan **per line (semua serial)**. Qty yang sudah ASN dicegah oleh feedback ASN existing ke G-System + SOP; kalau tetap terjadi → **CONFLICT** (abnormality, lihat simulasi skenario 4) |
| 7 | ID | Prefix **XD** (XD01–XD15) |

## Skenario H0253 (skenario_h0253.xlsx)
| Skenario | H0253 14-Oct → 15-Oct | NSP |
|---|---|---|
| 1 Normal | Status 7 qty 8 → status 6 qty 8 | XD08 update (diterima) |
| 2 Partial cancel | Status 7 qty 8 → serial A status 7 qty 6 + serial B status 2 qty 2 | XD12 → XD11 CANCELLED (VALID 6) |
| 3 Full cancel | Status 7 qty 8 → status 2 qty 8 | XD12 → XD11 CANCELLED (VALID 0) |
| 4 Abnormality | Sudah di ASN, lalu cancel (SOP tidak dijalankan) | XD11 CONFLICT |

Simulasi: menu prototype **ASN → Cancel Order Simulation**.

## Keputusan (Confirmation Points, 19-Oct)
| No | Function | Keputusan |
|---|---|---|
| A1 | ASN Cross Dock Creation Screen (XD10), Mapping Customer Order and PO Batch (XD09) | Case per destinasi dipecah sesuai pcs/case (Vietnam 24 pcs, 6 pcs/case = 4 case). G-System selalu rilis kelipatan pcs/case (sisa tetap pending, tidak muncul di H0253), jadi case selalu penuh |
| A2 | ASN Cross Dock Creation Screen (XD10) | Tetap utuh per unit (Part Number + Customer Order Date): kalau 1 line belum dapat PO, unit belum bisa di-ASN |
| A3 | ASN Cross Dock Creation Screen (XD10), ASN Crossdock Inquiry Screen (XD15) | 1 case label = 1 case 1 destinasi, bisa berisi beberapa Customer Order No; format sesuai label existing |
| A4 | Cancel Crossdock Customer Order Batch (XD11) | Barang CONFLICT boleh dialokasikan ke order destinasi lain juga, atau stok gudang |
| A5 | Cancel Crossdock Customer Order Batch (XD11) | PO qty tidak diblok |
| A6 | Cancel Crossdock Customer Order Batch (XD11) | Exception list = Log (Log Monitoring), tanpa layar khusus |
| A7 | DAD Volume Calculation Batch (XD05), IF Cross Dock Master to G-System / AP POLE (XD06 / XD07) | Part yang jadi Inactive dikirim (CROSSDOCK_FLAG 'N') supaya statusnya jadi inactive di G-System dan AP POLE; XD05 set part itu No Sync |
| A8 | IF Cross Dock Master to G-System (XD06) | G-System **tidak** pakai SFTP (interface existing, tidak didetailkan) |
| A9–A11 | IF Cross Dock Master to G-System / AP POLE (XD06 / XD07) | Tabel tujuan, detail SFTP dan format file **tidak didetailkan** |
| B1 | XD08, XD11, XD12, XD13 | Jadwal setelah data G-System tersedia (27:30), retry 3x |
| B2 | XD04, XD05 | Jadwal bulanan tidak didetailkan |
| B3 | XD04, XD05 | Kalau XD04 gagal, XD05 tetap jalan |
| B4 | XD08, XD12 | SERIAL_NO ditambahkan tim DB Surrounding |
| B5, B6 | – | H0202 Sync, Menu Settings (dokumen) dan XD14 tidak dipakai |
| C1 | XD04 | Kolom DAD tetap ikut di-replicate (tidak dipakai kalkulasi) |
| C2–C8 | XD01–XD05 | N + S dijumlahkan; retensi history 24 bulan; panjang kolom sesuai existing; template / log upload tidak didetailkan; Viewer = Search / Export; Effective Start Date default besok, min hari ini, wajib; label prototype dibiarkan |

## Keputusan 21-Oct (XD09 / XD10: urutan scan dan blok ASN)
- Urutan baris H0253 = urutan alokasi G-System, Allocation Priority = Customer Order Date: Allocation Priority → Customer Code → Customer Order No → Customer Order Date → Order Time → Destination → Detailed Item No → Serial No; per Part No + Customer Order Date (Cara B).
- Pcs dipotong jadi case supplier @ PCS_CASE (boleh campur destinasi). ASN hanya boleh berhenti di titik potong valid (qty kumulatif tiap destinasi kelipatan PCS_CASE, karena di gudang 1 case = 1 destinasi) → blok = opsi ASN. Blok harus berurutan (tidak boleh dilompati).
- Logika di `specs/scan_pack.py` (dipakai sample XD09 dan simulasi ERD); perubahan spec di `specs/apply_2110.py`; simulasi baru SIM-7.

## Keputusan 23-Oct (UPD_STATUS, satu batch H0253, Change Order Number)
- `CANCEL_STATUS` → **UPD_STATUS**: NULL / '6' received / '2' cancel dari H0253 original; ORDER_STATUS replicate tetap nilai pertama. XD09 hanya ambil UPD_STATUS NULL.
- **XD08** = satu batch H0253 (XD12 digabung, file XD12 dihapus). Setiap run **melepas semua draft** TB_R_INSTRUCTION (ASN_NO NULL); XD10 cek ulang saat Submit (MSG11); TB_R_INSTRUCTION + kolom DRAFT_ID.
- **XD11** = layar D/S **Change Order Number** (menggantikan cancel batch): qty cancel di ASN dipindah ke line part sama dengan UPD_STATUS 6, PO_MAPPED_FLAG N, tanpa ASN (tertua dulu, boleh beberapa line / destinasi lain, total qty sama); baris dipecah dari case terakhir; riwayat **TB_H_CROSSDOCK_ORDER_CHANGE** (pengganti TB_R_CROSSDOCK_CANCEL_RESULT).
- Logika di `specs/build_h.py`, `specs/build_xd11.py`, `specs/apply_2310.py`; simulasi SIM-5 / SIM-6 diganti (simulasi_asn.xlsx).

## Business Logic ASN (UISS XD09 4.0 / XD10 5.0)
1. Customer Order Date (hari ini, D) → PO Date (besok, D+1): 1 PO per Part Number per Customer Order Date.
2. Total customer order qty semua destinasi per Part Number = total PO qty dalam 1 PO. Kalau kurang → abnormality, sisanya di split PO; customer order yang belum dapat PO menunggu PO berikutnya.
3. 1 line customer order bisa ada di beberapa ASN; kalau receive-nya terpisah, line di H0253 ikut terpecah (SERIAL_NO baru) dan tiap bagian tetap terhubung ke ASN-nya.
4. PO_MAPPED_FLAG diisi saat Create ASN.
5. Case Ready di delivery plan dikirim sesuai CUT_FLAG (dari case 1 sampai cut; case di antara dua cut dikirim bersama).

## Business Process Flow Level 2
Lihat `bpf/README.md`: Excel `bpf/Crossdock_BPF_Level2.xlsx` (X = PIC, Y = timeline, sampai level tabel, abnormality AB01–AB16) dan menu prototype Common → Business Process Flow.

## Concept ERD
Lihat `erd/README.md`: `erd/Crossdock_ERD.xlsx` (ERD, Table List, Relationship, Column Definition, Simulation Data).

## Build
```
bash deliverables/function_list_v2/build_all_v2.sh
```
