# F06 – IF Cross Dock Master to GTOPAS

Sumber: UISS `F06_UISS_Batch_IFCrossDockMasterToGTOPAS.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

## Tujuan
- Mengirim cross dock master part **Active** yang menunggu sync ke **GTOPAS**: Pcs/Case dan Max Case/Day dari **Part List** (TB_M_PART_CANDIDATE) dan semua destinasi + Case/Day periode berjalan dari **Part Mapping per Destination** (TB_M_PART_CANDIDATE_DEST).
- Dulu satu RPA mengirim ke GTOPAS dan AP POLE sekaligus (X3 Sync). Sekarang dipisah: F06 hanya ke GTOPAS; F07 (AP POLE) mengirim data yang sama ke target lain.

## Alur
1. [Sync] di F01 (tab Mapping): part jadi Waiting, baris TB_R_CROSSDOCK_IF_RESULT untuk GTOPAS = 3, F06 dijalankan (LOG1).
2. Ambil part dengan TARGET_SYSTEM = 'GTOPAS' dan IF_STATUS = 3 yang masih Active; simpan CHANGED_DT.
3. Per part baca set lengkap (PCS_CASE, MAX_CASE_DAY, semua DEST_CODE + CASE_DAY periode berjalan).
4. **Replace** data part di GTOPAS (destinasi yang tidak ada di set ikut terhapus). Error hanya menghentikan part itu.
5. Tulis hasil GTOPAS: IF_STATUS 1 Success / 2 Failed (IF_MESSAGE, LOG3).
6. Update Sync Status gabungan di TB_M_PART_CANDIDATE (lihat F01) dan history TB_H_PART_CANDIDATE (event SYNC, source IF, REMARK = 'GTOPAS: …').
7. Part berikutnya; selesai → LOG2.

## Data yang dikirim
| Item | Sumber | Field GTOPAS |
|---|---|---|
| Part number | TB_M_PART_CANDIDATE.PART_NO | TBD |
| Pcs/Case | TB_M_PART_CANDIDATE.PCS_CASE | TBD |
| Max Case/Day | TB_M_PART_CANDIDATE.MAX_CASE_DAY | TBD |
| Periode | TB_M_PART_CANDIDATE_DEST.PERIOD (berjalan) | TBD |
| Destinasi (n baris) | TB_M_PART_CANDIDATE_DEST.DEST_CODE | TBD |
| Case/Day per destinasi | TB_M_PART_CANDIDATE_DEST.CASE_DAY | TBD |

## Tabel baru (usulan): TB_R_CROSSDOCK_IF_RESULT
PART_NO + TARGET_SYSTEM (PK, 'GTOPAS' / 'APPOLE'), PERIOD, IF_STATUS (3/1/2), IF_DT, IF_MESSAGE, audit.

## Log
LOG1 start, LOG2 end (sent / failed), LOG3 part ditolak GTOPAS, LOG4 GTOPAS tidak tersedia / timeout, LOG5 unexpected error.

## Open points
- Metode interface ke GTOPAS: RPA (desain awal) atau interface sistem; layar / field tujuan; perilaku kalau GTOPAS tidak tersedia.
- Part tanpa destinasi: dikirim dengan daftar destinasi kosong? (TBC)
- User ID batch.
