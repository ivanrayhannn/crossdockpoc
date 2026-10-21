# XD12 – Order Control Information to NSP Batch (Cancel)

Sumber: UISS `XD12_UISS_Batch_OrderControlInfoToNSP_Cancel.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-System / NSP.

## Desain (keputusan 18-Oct)
- Tabel yang sama dengan XD08: `TB_R_H0253_ORDER_CONTROL_PRE` (upsert, delta INTF_UPDATE_DT). Tabel cancel terpisah **tidak dipakai lagi**.
- Kolom NSP baru **CANCEL_STATUS**: '-' tidak ada cancel / **'P'** menunggu XD11 / **'D'** sudah diproses XD11.

## Alur
1. Jalan pertama di job chain **XD12 → XD11 → XD08**.
2. Ambil baris source **status 2** dengan INTF_UPDATE_DT > watermark yang line-nya (unique key tanpa SERIAL_NO) ada di NSP (line crossdock). Line lain diabaikan.
3. Ikut ambil baris lain dari line yang sama yang juga berubah (misalnya serial status 7 yang qty-nya berkurang karena partial cancel), supaya XD11 melihat line lengkap.
4. Upsert:
   - status 2 key baru (partial cancel = serial baru) → insert, CANCEL_STATUS 'P';
   - status 2 key lama (full cancel) → update, CANCEL_STATUS 'P';
   - baris lain line itu → update kolom source.
5. Sukses → commit, watermark baru. Gagal → rollback, XD11 tidak jalan.

## Skenario
| Skenario | H0253 14-Oct → 15-Oct (skenario_h0253.xlsx) | NSP |
|---|---|---|
| 1 Normal | Status 7 qty 8 → baris yang sama status 6 qty 8 | XD08 update baris (diterima); tidak diambil XD09 lagi |
| 2 Partial cancel | Status 7 qty 8 → serial A status 7 qty 6 + serial B (baru) status 2 qty 2 | XD12 update A, insert B (CANCEL_STATUS 'P'); XD11: CANCEL 2, VALID 6 → CANCELLED |
| 3 Full cancel | Status 7 qty 8 → baris yang sama status 2 qty 8 | XD12 update baris ('P'); XD11: CANCEL 8, VALID 0 → CANCELLED |
| 4 Abnormality | 8 pcs sudah di ASN, lalu cancel (SOP tidak dijalankan) | XD11: QTY_IN_ASN > VALID_QTY → CONFLICT, ASN tetap |

## Pencegahan cancel qty yang sudah ASN
- **Existing**: data ASN sudah dikirim balik ke G-System (feedback), sehingga G-System memblok cancel line itu.
- **SOP** tim D/S sebelum cancel.
- Kalau tetap terjadi (abnormality) → XD11 mencatat **CONFLICT** (simulasi: menu prototype *Cancel Order Simulation*, skenario 4).

## Keputusan 19-Oct
- Jadwal: setelah data G-System tersedia (27:30), retry 3x; job chain XD12 → XD11 → XD08.
- SERIAL_NO ditambahkan ke tabel source oleh tim DB Surrounding.
