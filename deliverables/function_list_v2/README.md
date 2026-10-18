# Crossdock – Function List v2 (UISS XD01–XD15)

Folder ini berisi UISS sesuai **function list terbaru** (18-Oct-26). Dokumen versi pertama (X1–X15) di `deliverables/uiss`, `deliverables/uiss_specs` dan `deliverables/md` **tidak diubah**.

| Folder | Isi |
|---|---|
| `uiss/` | UISS Excel XD01–XD15 (0.1 Initial Draft, FID Rayhan, 18-Oct-26) |
| `md/` | Ringkasan per fungsi (Bahasa Indonesia) |
| `specs/` | Builder Python + spec JSON (dibuat dari spec versi pertama, tanpa mengubahnya) |
| `build_all_v2.sh` | Build ulang semua UISS v2 (jalankan dari root repo) |

Nama sistem di UISS tetap **G-TOPAS** dan **NSP** (rename T-System / Supplier System hanya di prototype web).

## Function list dan asal dokumen

| ID | Function | Tipe | Asal (versi pertama) | Perubahan |
|---|---|---|---|---|
| XD01 | Cross Dock Part Master Screen | Screen | X1 Part List + X3 Mapping per Destination | **Digabung** jadi 1 screen dengan 2 tab. Sync sekarang menjalankan XD06 + XD07 |
| XD02 | Cross Dock Part Master Upload Batch | Batch | X2 Part List Upload | Ganti ID / nama, referensi ke XD01 / XD05 |
| XD03 | Part and Destination Mapping Upload Batch | Batch | X4 Mapping per Destination Upload | Ganti ID / nama |
| XD04 | Actual Demand Summary Synch to NSP | Batch | X5 | Tetap replicate tabel Actual Demand Summary ke NSP (delete – insert) |
| XD05 | DAD Volume Calculation Batch | Batch | X6 DAD Volume Calc + X7 Mapping Destination Calc | **Digabung**: proses 1 (status part) lalu proses 2 (mapping destinasi) |
| XD06 | IF Cross Dock Master to GTOPAS | Batch | bagian RPA dari X3 (Sync) | **Baru / dipisah**: file SFTP berisi Part List + Mapping per Destination ke GTOPAS |
| XD07 | IF Cross Dock Master to AP POLE | Batch | bagian RPA dari X3 (Sync) | **Baru / dipisah**: file SFTP dengan data sama ke AP POLE |
| XD08 | Order Control Information to NSP Batch (ASN) | Batch | X10 H0253 Sync | Sekarang hanya **ORDER_STATUS = 7** |
| XD09 | Mapping Customer Order and PO Batch | Batch | X12 Get Order (pre-mapping) | Ganti ID / nama (tetap on demand dari [Search] di XD10) |
| XD10 | ASN Cross Dock Creation Screen | Screen | X8 + X14 ASN Submit | **Digabung**: proses Submit ASN jadi section 5.7 |
| XD11 | Cancel Crossdock Customer Order Batch | Batch | – | **Baru** (usulan dari diskusi cancel 16-Oct) |
| XD12 | Order Control Information to NSP Batch (Cancel) | Batch | – (pola X10) | **Baru**: H0253 **ORDER_STATUS = 2** ke tabel cancel |
| XD13 | Destination Master Synch into NSP | Batch | X11 H0125 Sync | Ganti ID / nama |
| XD14 | DAD Volume Calculation Result Screen (Buffer) | Screen | – | **Belum dibuat** (buffer, perlu penjelasan isi layar) |
| XD15 | ASN Crossdock Inquiry Screen (Buffer) | Screen | X13 | Ganti ID / nama |

Tidak ada di function list baru (tidak dibawa ke v2): **X9** H0202 Demand History Sync, **X15** Menu Settings (admin panel prototype).

## Keputusan (konfirmasi 18-Oct)
| No | Topik | Keputusan |
|---|---|---|
| 1 | XD05 | **Disetujui**: X6 + X7 digabung. Satu run = proses 1 lalu proses 2; [Run calculation (Part List)] = proses 1 + 2, [Run calculation (Mapping)] = proses 2 saja |
| 2 | XD10 | **Disetujui**: X14 (Submit ASN) masuk ke XD10 (section 5.7) |
| 3 | XD06 / XD07 | Kirim lewat **file SFTP – Option #3** (NSP Send IF → SFTP TMMIN → SFTP TMA → receive IF → AP POLE Crossdock Kanban Part Master / Crossdock Export Part Master). **TB_R_CROSSDOCK_IF_RESULT = tabel dummy** untuk status kirim; output sebenarnya file ke GTOPAS (XD06) dan AP POLE (XD07). Field dan proses bisnis sudah didetailkan (Interface Data di UISS dan md). Sync Status gabungan **disetujui** |
| 4 | XD08 / XD12 / tabel H0253 | **Satu tabel replicate upsert** (delta INTF_UPDATE_DT, partial cancel = serial baru, status 6 / 2 disimpan untuk tracking); kolom baru CANCEL_STATUS; tabel cancel terpisah dihapus |
| 5 | Urutan job | **Disetujui**: XD12 → XD11 → XD08 |
| 6 | XD11 | Cancel bisa **dengan atau tanpa Hold Flag Y**. Perhitungan **per line (semua serial)**. Qty yang sudah ASN dicegah oleh feedback ASN existing ke G-TOPAS + SOP; kalau tetap terjadi → **CONFLICT** (abnormality, lihat simulasi skenario 4) |
| 7 | ID | Prefix **XD** (XD01–XD15) |

## Skenario H0253 (skenario_h0253.xlsx)
| Skenario | H0253 14-Oct → 15-Oct | NSP |
|---|---|---|
| 1 Normal | Status 7 qty 8 → status 6 qty 8 | XD08 update (diterima) |
| 2 Partial cancel | Status 7 qty 8 → serial A status 7 qty 6 + serial B status 2 qty 2 | XD12 → XD11 CANCELLED (VALID 6) |
| 3 Full cancel | Status 7 qty 8 → status 2 qty 8 | XD12 → XD11 CANCELLED (VALID 0) |
| 4 Abnormality | Sudah di ASN, lalu cancel (SOP tidak dijalankan) | XD11 CONFLICT |

Simulasi: menu prototype **ASN → Cancel Order Simulation**.

## Asumsi lain yang masih perlu dikonfirmasi
- XD11: opsi "blok PO qty sampai conflict ditutup" belum dimasukkan.
- Part yang jadi Inactive (XD05) tidak dikirim ke GTOPAS / AP POLE.

## Build
```
bash deliverables/function_list_v2/build_all_v2.sh
```
