# XD01 – Cross Dock Part Master Screen

Sumber: UISS `XD01_UISS_Screen_CrossDockPartMaster.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-System / NSP.

## Ringkasan
- **Gabungan** X1 (Part List) dan X3 (Mapping per Destination) menjadi **1 screen dengan 2 tab**. Prototype: menu *Crossdock Master Setting* (tab Part List / Mapping per Destination).
- Isi tiap tab sama dengan versi pertama (detail: `deliverables/md/X1_SCREEN_PartList.md`, `X3_SCREEN_MappingPerDestination.md`).
- Penomoran di UISS gabungan:
  - Operation Description **5.1–5.10** = tab Part List, **5.11–5.20** = tab Mapping per Destination.
  - Pesan **MSG1–MSG17** = Part List, **MSG18–MSG30** = Mapping. Log **LOG1–LOG2** = Part List, **LOG3–LOG5** = Mapping.
  - Screen mode diberi awalan "Part List -" / "Mapping -"; tombol yang namanya sama tapi beda fungsi diberi akhiran: *Upload Excel (Part List)* / *(Mapping)*, *Export Excel*, *Run calculation*. Di matriks tombol, "-" = tombol tidak ada di tab mode itu.

## Perubahan Sync (dulu 1 RPA ke global system)
- [Sync (n)] di tab Mapping: SYNC_STATUS = 3 (Waiting) dan 1 baris per part × target (**G-System**, **APPOLE**) di tabel baru **TB_R_CROSSDOCK_IF_RESULT** (IF_STATUS = 3), lalu menjalankan **XD06** (G-System) dan **XD07** (AP POLE).
- Sync Status part = gabungan dua target:

| Kondisi | SYNC_STATUS |
|---|---|
| Salah satu target masih Waiting | 3 Waiting |
| Dua target Success | 1 Success |
| Salah satu target Failed | 2 Failed (SYNC_MESSAGE = target + alasan) |
| Part diubah saat sedang dikirim | 0 No Sync |

- [Run calculation] tab Part List → XD05 proses 1 + 2; tab Mapping → XD05 proses 2 saja.

## Tabel
- TB_M_PART_CANDIDATE, TB_M_PART_CANDIDATE_DEST, TB_H_PART_CANDIDATE (history, SOURCE sekarang SCREEN / UPLOAD / IF / BATCH), **TB_R_CROSSDOCK_IF_RESULT** (tabel dummy untuk status kirim; output sebenarnya file SFTP ke G-System / AP POLE).

## Open points
- Topology SFTP dan nama field di G-System / AP POLE (detail field sumber ada di md XD06 / XD07).
- Open points versi pertama X1 / X3 tetap berlaku (akun read only, Effective Start Date, dll.).

## Keputusan 19-Oct
- [Sync] juga mengirim part yang jadi **Inactive** (CROSSDOCK_FLAG 'N').
- Viewer = hanya Search / Export. Effective Start Date: default besok, minimal hari ini, wajib. Panjang kolom sesuai existing; retensi history 24 bulan.
