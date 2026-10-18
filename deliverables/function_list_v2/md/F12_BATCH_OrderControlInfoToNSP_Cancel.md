# F12 – Order Control Information to NSP Batch (Cancel)

Sumber: UISS `F12_UISS_Batch_OrderControlInfoToNSP_Cancel.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Replicate **TB_R_H0253_ORDER_CONTROL_PRE** (DB Surrounding) baris **ORDER_STATUS = '2'** (cancel) ke tabel NSP terpisah **TB_R_H0253_ORDER_CANCEL_PRE** (usulan nama), delete – insert, all-or-nothing.
- Tabel terpisah karena F08 full replace TB_R_H0253_ORDER_CONTROL_PRE hanya dengan status 7.
- Kolom = kolom H0253 tanpa HOLD_FLAG / PO_MAPPED_FLAG.
- Semua order type ikut tersalin; F11 hanya mengambil line crossdock (TBC: filter crossdock langsung di F12).
- Urutan job (TBC): **F12 → F11 → F08**. Kalau F12 gagal, F11 tidak jalan.
