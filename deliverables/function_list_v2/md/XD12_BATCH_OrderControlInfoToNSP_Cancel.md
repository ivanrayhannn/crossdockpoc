# XD12 – Order Control Information to NSP Batch (Cancel)

Sumber: UISS `XD12_UISS_Batch_OrderControlInfoToNSP_Cancel.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Replicate **TB_R_H0253_ORDER_CONTROL_PRE** (DB Surrounding) baris **ORDER_STATUS = '2'** (cancel) ke tabel NSP terpisah **TB_R_H0253_ORDER_CANCEL_PRE** (usulan nama), delete – insert, all-or-nothing.
- Tabel terpisah karena XD08 full replace TB_R_H0253_ORDER_CONTROL_PRE hanya dengan status 7.
- Kolom = kolom H0253 tanpa HOLD_FLAG / PO_MAPPED_FLAG.
- Semua order type ikut tersalin; XD11 hanya mengambil line crossdock (TBC: filter crossdock langsung di XD12).
- Urutan job (TBC): **XD12 → XD11 → XD08**. Kalau XD12 gagal, XD11 tidak jalan.

> **Open discussion (18-Oct):** tabel source di DB Surrounding bersifat insert / update (status line bisa berubah 7 → 6 diterima, atau 7 → 2 cancel). Desain tabel replicate di NSP masih didiskusikan: dua tabel full replace (draft ini) atau satu tabel insert / update. Lihat README.
