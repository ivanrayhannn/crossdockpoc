# XD11 – Cancel Crossdock Customer Order Batch

Sumber: UISS `XD11_UISS_Batch_CancelCrossdockCustomerOrder.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-System / NSP.

## Tujuan
- NSP **tidak pernah cancel order** dan tidak punya Cancel ASN. G-System cancel (status 2), XD12 membawanya ke NSP dengan UPD_STATUS 'P'; XD11 menerapkannya ke data crossdock NSP.
- Cancel bisa **dengan atau tanpa Hold Flag Y** (HOLD_FLAG hanya dicatat).
- Qty yang sudah ASN tidak boleh di-cancel: dicegah oleh **feedback ASN existing ke G-System** + **SOP**. Kalau tetap terjadi → **CONFLICT** (abnormality).

## Perhitungan per line (semua SERIAL_NO, karena partial cancel memecah serial)
| Angka | Cara hitung |
|---|---|
| CANCEL_QTY | Σ qty baris status 2 dengan UPD_STATUS 'P' |
| VALID_QTY | Σ qty baris status 7 + 6 |
| QTY_IN_ASN | Σ QTY TB_R_INSTRUCTION line dengan ASN_NO |
| QTY_OPEN | Σ QTY TB_R_INSTRUCTION line tanpa ASN_NO (Create ASN, belum submit) |
| CONFLICT_QTY | QTY_IN_ASN − VALID_QTY kalau positif |

## Alur
1. Jalan setelah XD12 berhasil, sebelum XD08.
2. Ambil line yang punya baris status 2 dengan UPD_STATUS 'P'; baca semua serial line itu.
3. Hitung angka di atas.
4. Lepas mapping terbuka line: hapus baris TB_R_INSTRUCTION tanpa ASN_NO, kurangi MAPPED_QTY per PO, PO_MAPPED_FLAG = N pada serial status 7 yang tidak punya mapping lagi → **sisa qty valid di-pre-mapping ulang oleh XD09**. Baris dengan ASN_NO tidak pernah diubah.
5. Hasil: **CANCELLED** (QTY_IN_ASN ≤ VALID_QTY) atau **CONFLICT** (QTY_IN_ASN > VALID_QTY).
6. UPD_STATUS = 'D' dan simpan hasil ke **TB_R_CROSSDOCK_CANCEL_RESULT** (commit per line).

## Skenario
| Skenario | H0253 14-Oct → 15-Oct (skenario_h0253.xlsx) | NSP |
|---|---|---|
| 1 Normal | Status 7 qty 8 → baris yang sama status 6 qty 8 | XD08 update baris (diterima); tidak diambil XD09 lagi |
| 2 Partial cancel | Status 7 qty 8 → serial A status 7 qty 6 + serial B (baru) status 2 qty 2 | XD12 update A, insert B (UPD_STATUS 'P'); XD11: CANCEL 2, VALID 6 → CANCELLED |
| 3 Full cancel | Status 7 qty 8 → baris yang sama status 2 qty 8 | XD12 update baris ('P'); XD11: CANCEL 8, VALID 0 → CANCELLED |
| 4 Abnormality | 8 pcs sudah di ASN, lalu cancel (SOP tidak dijalankan) | XD11: QTY_IN_ASN > VALID_QTY → CONFLICT, ASN tetap |

## Penanganan CONFLICT (di luar sistem)
- Case yang sudah dikirim diterima di G-System tanpa order: tim D/S alokasikan manual ke order terbuka dengan **destinasi sama**; kalau tidak ada, masuk stok gudang.

## Open points
- Opsi blok PO qty sampai conflict ditutup (belum di draft).
- Layar exception list (sementara lewat Log Monitoring).

## Keputusan 19-Oct
- Barang CONFLICT boleh dialokasikan ke order **destinasi lain** juga, atau stok gudang.
- PO qty **tidak diblok**.
- Exception list = **Log** (Log Monitoring); tidak ada layar khusus.
