# F08 – Order Control Information to NSP Batch (ASN)

Sumber: UISS `F08_UISS_Batch_OrderControlInfoToNSP_ASN.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Replicate **TB_R_H0253_ORDER_CONTROL_PRE** (DB Surrounding) baris **ORDER_STATUS = '7'** (crossdock) ke tabel yang sama di NSP (delete – insert, all-or-nothing).
- Kolom NSP **HOLD_FLAG / PO_MAPPED_FLAG** dipertahankan per unique key (default 'N' untuk key baru).
- Line yang di-cancel (status 2) diambil oleh **F12** dan diproses **F11** sebelum F08 jalan. Urutan job (TBC): **F12 → F11 → F08**.
- Dibaca oleh F09 dan F10. Struktur tabel: `deliverables/md/X10_BATCH_H0253_OrderControl_Sync.md`.
