# XD13 – Destination Master Synch into NSP

Sumber: UISS `XD13_UISS_Batch_DestinationMasterSync.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: GTOPAS / NSP.

- Isi sama dengan X11: replicate **TB_M_H0125_DESTINATION** (H0125) dari DB Surrounding ke NSP (delete – insert). Detail: `deliverables/md/X11_BATCH_H0125_DestinationMaster_Sync.md`.
- Dipakai XD01 / XD03 (destinasi) dan XD05 proses 2 (cek destination code).

## Keputusan 19-Oct
- Jadwal: setelah data GTOPAS tersedia (1x/minggu, 21:30), retry 3x.
