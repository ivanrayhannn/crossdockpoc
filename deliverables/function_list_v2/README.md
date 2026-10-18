# Crossdock – Function List v2 (UISS F01–F15)

Folder ini berisi UISS sesuai **function list terbaru** (18-Oct-26). Dokumen versi pertama (X1–X15) di `deliverables/uiss`, `deliverables/uiss_specs` dan `deliverables/md` **tidak diubah**.

| Folder | Isi |
|---|---|
| `uiss/` | UISS Excel F01–F15 (0.1 Initial Draft, FID Rayhan, 18-Oct-26) |
| `md/` | Ringkasan per fungsi (Bahasa Indonesia) |
| `specs/` | Builder Python + spec JSON (dibuat dari spec versi pertama, tanpa mengubahnya) |
| `build_all_v2.sh` | Build ulang semua UISS v2 (jalankan dari root repo) |

Nama sistem di UISS tetap **G-TOPAS** dan **NSP** (rename T-System / Supplier System hanya di prototype web).

## Function list dan asal dokumen

| ID | Function | Tipe | Asal (versi pertama) | Perubahan |
|---|---|---|---|---|
| F01 | Cross Dock Part Master Screen | Screen | X1 Part List + X3 Mapping per Destination | **Digabung** jadi 1 screen dengan 2 tab. Sync sekarang menjalankan F06 + F07 |
| F02 | Cross Dock Part Master Upload Batch | Batch | X2 Part List Upload | Ganti ID / nama, referensi ke F01 / F05 |
| F03 | Part and Destination Mapping Upload Batch | Batch | X4 Mapping per Destination Upload | Ganti ID / nama |
| F04 | Actual Demand Summary Synch to NSP | Batch | X5 | Tetap replicate tabel Actual Demand Summary ke NSP (delete – insert) |
| F05 | DAD Volume Calculation Batch | Batch | X6 DAD Volume Calc + X7 Mapping Destination Calc | **Digabung**: proses 1 (status part) lalu proses 2 (mapping destinasi) |
| F06 | IF Cross Dock Master to GTOPAS | Batch | bagian RPA dari X3 (Sync) | **Baru / dipisah**: kirim Part List + Mapping per Destination ke GTOPAS |
| F07 | IF Cross Dock Master to AP POLE | Batch | bagian RPA dari X3 (Sync) | **Baru / dipisah**: data sama ke AP POLE |
| F08 | Order Control Information to NSP Batch (ASN) | Batch | X10 H0253 Sync | Sekarang hanya **ORDER_STATUS = 7** |
| F09 | Mapping Customer Order and PO Batch | Batch | X12 Get Order (pre-mapping) | Ganti ID / nama (tetap on demand dari [Search] di F10) |
| F10 | ASN Cross Dock Creation Screen | Screen | X8 + X14 ASN Submit | **Digabung**: proses Submit ASN jadi section 5.7 |
| F11 | Cancel Crossdock Customer Order Batch | Batch | – | **Baru** (usulan dari diskusi cancel 16-Oct) |
| F12 | Order Control Information to NSP Batch (Cancel) | Batch | – (pola X10) | **Baru**: H0253 **ORDER_STATUS = 2** ke tabel cancel |
| F13 | Destination Master Synch into NSP | Batch | X11 H0125 Sync | Ganti ID / nama |
| F14 | DAD Volume Calculation Result Screen (Buffer) | Screen | – | **Belum dibuat** (buffer, perlu penjelasan isi layar) |
| F15 | ASN Crossdock Inquiry Screen (Buffer) | Screen | X13 | Ganti ID / nama |

Tidak ada di function list baru (tidak dibawa ke v2): **X9** H0202 Demand History Sync, **X15** Menu Settings (admin panel prototype).

## Keputusan / asumsi yang saya ambil (perlu dikonfirmasi)
1. **F05** menggabungkan X6 dan X7 karena X7 tidak ada di list. Satu run = proses 1 lalu proses 2. [Run calculation (Part List)] menjalankan proses 1 + 2, [Run calculation (Mapping)] hanya proses 2.
2. **F06 / F07** memakai data yang sama (Pcs/Case, Max Case/Day, destinasi + Case/Day periode berjalan). Hasil per target disimpan di tabel baru **TB_R_CROSSDOCK_IF_RESULT**; Sync Status di F01 = gabungan (Success kalau dua-duanya Success, Failed kalau salah satu gagal). Metode interface (RPA atau interface sistem) **TBC**.
3. **F12** menulis ke tabel terpisah **TB_R_H0253_ORDER_CANCEL_PRE** (usulan), karena F08 full replace hanya status 7.
4. **Urutan job (TBC): F12 → F11 → F08**, supaya F11 masih bisa membaca HOLD_FLAG dan qty status 7 sebelum cancel.
5. **F11** dibuat dari usulan skenario B/C di menu *Cancel Order Simulation*: hasil per line CANCELLED / NO_HOLD / CONFLICT di tabel baru **TB_R_CROSSDOCK_CANCEL_RESULT**; ASN tidak pernah diubah. Opsi "blok PO qty sampai conflict ditutup" belum dimasukkan (TBC).
6. ID baru memakai prefix **F** (F01–F15) supaya tidak tertukar dengan X1–X15.

## Build
```
bash deliverables/function_list_v2/build_all_v2.sh
```
