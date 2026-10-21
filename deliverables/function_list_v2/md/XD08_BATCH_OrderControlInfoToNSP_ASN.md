# XD08 – Order Control Information to NSP Batch (ASN)

Sumber: UISS `XD08_UISS_Batch_OrderControlInfoToNSP_ASN.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-System / NSP.

## Desain (keputusan 18-Oct)
- Tabel source di DB Surrounding **insert / update**. NSP memakai **satu tabel replicate** `TB_R_H0253_ORDER_CONTROL_PRE` yang di-**upsert** per unique key (termasuk SERIAL_NO). Tidak ada delete, jadi kolom NSP (HOLD_FLAG, PO_MAPPED_FLAG, CANCEL_STATUS) aman.
- Hanya baris yang berubah sejak run terakhir: **INTF_UPDATE_DT > watermark** (watermark = INTF_UPDATE_DT terakhir dari run sukses, disimpan di Log).

## Alur
1. Jalan terakhir di job chain **XD12 → XD11 → XD08**.
2. Ambil baris source dengan INTF_UPDATE_DT > watermark:
   - **status 7**: semua (line baru, qty berubah, serial hasil split);
   - **status 6**: hanya key yang sudah ada di NSP (diterima, tidak ada aksi lanjut);
   - status 2 diambil XD12.
3. Upsert: key baru → insert (HOLD_FLAG / PO_MAPPED_FLAG = N, CANCEL_STATUS = '-'); key lama → update kolom source, kolom NSP tidak diubah.
4. Sukses → commit, simpan watermark baru. Gagal → rollback, watermark tetap (diambil lagi run berikutnya).

## Skenario
| Skenario | H0253 14-Oct → 15-Oct (skenario_h0253.xlsx) | NSP |
|---|---|---|
| 1 Normal | Status 7 qty 8 → baris yang sama status 6 qty 8 | XD08 update baris (diterima); tidak diambil XD09 lagi |
| 2 Partial cancel | Status 7 qty 8 → serial A status 7 qty 6 + serial B (baru) status 2 qty 2 | XD12 update A, insert B (CANCEL_STATUS 'P'); XD11: CANCEL 2, VALID 6 → CANCELLED |
| 3 Full cancel | Status 7 qty 8 → baris yang sama status 2 qty 8 | XD12 update baris ('P'); XD11: CANCEL 8, VALID 0 → CANCELLED |
| 4 Abnormality | 8 pcs sudah di ASN, lalu cancel (SOP tidak dijalankan) | XD11: QTY_IN_ASN > VALID_QTY → CONFLICT, ASN tetap |

- Baris status 6 / 2 tetap disimpan untuk tracking (retensi opsional).
- Dibaca XD09 (status 7, belum mapping, tidak hold), XD10 dan XD11.

## Keputusan 19-Oct
- Jadwal: setelah data G-System tersedia (27:30), retry 3x; job chain XD12 → XD11 → XD08.
- SERIAL_NO ditambahkan ke tabel source oleh tim DB Surrounding.
