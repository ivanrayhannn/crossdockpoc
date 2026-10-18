# XD08 – Order Control Information to NSP Batch (ASN)

Sumber: UISS `XD08_UISS_Batch_OrderControlInfoToNSP_ASN.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Replicate **TB_R_H0253_ORDER_CONTROL_PRE** (DB Surrounding) baris **ORDER_STATUS = '7'** (crossdock) ke tabel yang sama di NSP (delete – insert, all-or-nothing).
- Kolom NSP **HOLD_FLAG / PO_MAPPED_FLAG** dipertahankan per unique key (default 'N' untuk key baru).
- Line yang di-cancel (status 2) diambil oleh **XD12** dan diproses **XD11** sebelum XD08 jalan. Urutan job (TBC): **XD12 → XD11 → XD08**.
- Dibaca oleh XD09 dan XD10. Struktur tabel: `deliverables/md/X10_BATCH_H0253_OrderControl_Sync.md`.

> **Open discussion (18-Oct):** tabel source di DB Surrounding bersifat insert / update (status line bisa berubah 7 → 6 diterima, atau 7 → 2 cancel). Desain tabel replicate di NSP masih didiskusikan: dua tabel full replace (draft ini) atau satu tabel insert / update. Lihat README.
