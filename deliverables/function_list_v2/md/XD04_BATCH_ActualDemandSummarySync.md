# XD04 – Actual Demand Summary Synch to NSP

Sumber: UISS `XD04_UISS_Batch_ActualDemandSummarySync.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: GTOPAS / NSP.

- **Replicate** TB_R_ACTUAL_DEMAND_SUMMARY dari DB Surrounding ke tabel yang sama di NSP (delete – insert, all-or-nothing). Tidak ada kalkulasi.
- Harus selesai sebelum **XD05** (proses 1 dan 2). Detail kolom: `deliverables/md/X5-X7_BATCH_Calculation_Functions.md` (Fungsi 1).

## Keputusan 19-Oct
- Semua kolom di-replicate, termasuk DAD (tidak dipakai kalkulasi). Jadwal tidak didetailkan; kegagalan XD04 tidak menghentikan XD05.
