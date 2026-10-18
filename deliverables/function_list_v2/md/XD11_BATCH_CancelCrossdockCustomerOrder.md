# XD11 – Cancel Crossdock Customer Order Batch

Sumber: UISS `XD11_UISS_Batch_CancelCrossdockCustomerOrder.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

**Status: usulan** (dari diskusi cancel 16-Oct dan menu prototype *Cancel Order Simulation*). Perlu konfirmasi.

## Tujuan
- NSP **tidak pernah cancel order** dan tidak punya Cancel ASN. Order bisa di-cancel **dengan atau tanpa Hold Flag Y** (keputusan 18-Oct); HOLD_FLAG hanya dicatat. G-TOPAS cancel order (H0253 status **2**, direplikasi oleh **XD12**); XD11 menerapkan cancel itu ke data crossdock NSP.
- Qty yang belum masuk ASN → mapping dilepas supaya PO bisa dipakai order berikutnya.
- Qty yang sudah masuk ASN → ASN tidak diubah; dilaporkan sebagai **cancel conflict** ke tim D/S.

## Alur
1. Jalan setelah XD12 berhasil, sebelum XD08 (job chain **XD12 → XD11 → XD08**).
2. Ambil baris TB_R_H0253_ORDER_CANCEL_PRE yang merupakan line crossdock (unique key ada di TB_R_H0253_ORDER_CONTROL_PRE) dan belum diproses (belum ada di TB_R_CROSSDOCK_CANCEL_RESULT dengan ORDER_STATUS_DT yang sama).
3. Hitung per line: LINE_QTY (qty status 7 sebelum cancel), CANCEL_QTY, QTY_IN_ASN (TB_R_INSTRUCTION dengan ASN_NO), OPEN_QTY (tanpa ASN_NO).
4. Tentukan hasil:

| Hasil | Kondisi | Aksi |
|---|---|---|
| CANCELLED | CANCEL_QTY ≤ LINE_QTY − QTY_IN_ASN (dengan atau tanpa Hold Flag Y) | Lepas mapping terbuka (LOG3) |
| CONFLICT | CANCEL_QTY > LINE_QTY − QTY_IN_ASN | Lepas mapping terbuka, ASN tetap + error ke D/S (LOG4) |

5. Lepas mapping terbuka: hapus baris TB_R_INSTRUCTION tanpa ASN_NO, kurangi MAPPED_QTY di TB_R_PRA_DAILY_ORDER_MAPPED per PO, PO_MAPPED_FLAG = N kalau tidak ada baris tersisa. Baris dengan ASN_NO tidak pernah diubah.
6. Simpan hasil ke **TB_R_CROSSDOCK_CANCEL_RESULT** (commit per line; line yang error diproses lagi di run berikutnya).
7. Log akhir dengan jumlah per hasil.

## Tabel baru (usulan): TB_R_CROSSDOCK_CANCEL_RESULT
Unique key line H0253 + ORDER_STATUS_DT (PK), PART_NO, LINE_QTY, CANCEL_QTY, QTY_IN_ASN, RELEASED_QTY, HOLD_FLAG, RESULT, ASN_NO, MESSAGE, audit. Sekaligus jadi **exception list** D/S (RESULT = CONFLICT).

## Penanganan CONFLICT (di luar sistem)
- Case yang sudah dikirim diterima di G-TOPAS tanpa order: tim D/S alokasikan manual ke order terbuka dengan **destinasi sama**; kalau tidak ada, masuk stok gudang.

## Open points
- Qty yang sudah masuk ASN harusnya tidak bisa di-cancel: dicegah di mana (G-TOPAS, SOP, atau kirim data ASN balik ke G-TOPAS)? Sementara XD11 mendeteksi sebagai CONFLICT. **Akan didiskusikan.**
- Desain tabel replicate H0253 (insert / update status 7, 6, 2) → lihat diskusi di README.
- Apakah G-TOPAS bisa partial cancel; 1 customer order line boleh di lebih dari 1 ASN (pengiriman bertahap)?
- Isi case label (Customer Order No / destinasi) → perlu relabel atau tidak.
- Opsi blok PO qty sampai conflict ditutup (skenario C simulasi) – butuh fungsi "close conflict".
- Layar untuk exception list (sementara lewat Log Monitoring).
