# XD06 – IF Cross Dock Master to GTOPAS

Sumber: UISS `XD06_UISS_Batch_IFCrossDockMasterToGTOPAS.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

## Tujuan
- Mengirim cross dock master part **Active** yang menunggu sync ke **GTOPAS** sebagai **file interface lewat SFTP** (keputusan 18-Oct; contoh topology menyusul dari user).
- Sumber: **Part List** (TB_M_PART_CANDIDATE) dan **Part Mapping per Destination** (TB_M_PART_CANDIDATE_DEST, periode berjalan).
- Dulu satu RPA mengirim ke GTOPAS dan AP POLE sekaligus (X3 Sync). Sekarang dipisah: XD06 ke GTOPAS, XD07 ke AP POLE (data sama).

## Proses bisnis
1. Tim D/S mengubah cross dock master di **XD01** (Part List: Pcs/Case, Max Case/Day, Effective Start Date; Mapping: Case/Day per destinasi hasil XD05 proses 2 atau edit / upload XD03). Setiap perubahan → part jadi **No Sync**.
2. Setelah perubahan lengkap, tim D/S klik **[Sync]** → part Active (No Sync / Failed) jadi Waiting dan XD06 + XD07 dijalankan.
3. GTOPAS mengganti (replace) data cross dock part dengan isi file (semua destinasi part).
- Kegunaan untuk GTOPAS: GTOPAS (customer order side): which part and destination orders are handled by crossdock (order status 7) and how many cases per day per destination (assumption, TBC).

## Alur batch
1. Start dari [Sync] XD01 (LOG1).
2. Ambil part dengan TARGET_SYSTEM = 'GTOPAS' dan IF_STATUS = 3 yang masih Active; simpan CHANGED_DT.
3. Buat file `XD_CDMASTER_GTOPAS_<YYYYMMDDHHMMSS>.csv` di folder outbound (1 record per part × destinasi). Gagal → LOG3.
4. **SFTP put** ke folder inbound GTOPAS, cek ukuran / jumlah record; gagal → retry, lalu LOG4. Berhasil → file dipindah ke folder backup.
5. Status kirim per part di tabel dummy: 1 = terkirim, 2 = gagal (TBC: kalau GTOPAS mengembalikan file hasil / acknowledge, status diambil dari file itu).
6. Sync Status gabungan di TB_M_PART_CANDIDATE (Success kalau GTOPAS dan AP POLE dua-duanya terkirim, Failed kalau salah satu gagal, No Sync kalau part berubah saat dikirim) + history (event SYNC, source IF).
7. LOG2 (nama file, jumlah part / record).

## Field yang dikirim (Interface Data)
| No | Field | Sumber | Format | Aturan bisnis |
|---|---|---|---|---|
| 1 | SEND_ID | Generated | CHAR(14) | Run of the send (YYYYMMDDHHMMSS); all records of one file have the same SEND_ID and are processed as one set |
| 2 | PART_NO | TB_M_PART_CANDIDATE.PART_NO | VARCHAR(TBD) | Cross dock part. Only parts with PART_STATUS = Active and Sync Status Waiting are sent |
| 3 | CROSSDOCK_FLAG | TB_M_PART_CANDIDATE.PART_STATUS | CHAR(1) | 'Y' = the part is handled by crossdock (Active). TBC: send 'N' when a part became Inactive, so the target stops crossdock for it |
| 4 | PCS_CASE | TB_M_PART_CANDIDATE.PCS_CASE | NUMBER(TBD) | Pieces per crossdock case; used to convert pieces to cases |
| 5 | MAX_CASE_DAY | TB_M_PART_CANDIDATE.MAX_CASE_DAY | NUMBER(TBD) | Maximum cases per day of the part through crossdock (= total Case/Day of its destinations) |
| 6 | EFFECTIVE_START_DATE | TB_M_PART_CANDIDATE.EFFECTIVE_START_DATE | DATE (YYYYMMDD) | Date from which the cross dock setting of the part applies |
| 7 | PERIOD | TB_M_PART_CANDIDATE_DEST.PERIOD | CHAR(6) | Calculation period of the mapping (ongoing period, YYYYMM) |
| 8 | DEST_CODE | TB_M_PART_CANDIDATE_DEST.DEST_CODE | CHAR(7) | Destination code (buyer code + PD code, TB_M_H0125_DESTINATION); one record per destination |
| 9 | CASE_DAY | TB_M_PART_CANDIDATE_DEST.CASE_DAY | NUMBER(TBD) | Cases per day allocated to the destination (minimum 1; sum per part = MAX_CASE_DAY) |
| 10 | SEND_DT | Generated | DATETIME | Date-time the file is created |

Nama field di sisi GTOPAS: **TBC** (menunggu layout target).

## File interface
| Item | Usulan |
|---|---|
| Nama | `XD_CDMASTER_GTOPAS_<YYYYMMDDHHMMSS>.csv` (TBC) |
| Format | CSV, koma, UTF-8, baris pertama nama field (TBC: fixed length kalau target minta) |
| Unit record | 1 record per part × destinasi periode berjalan; data part diulang di setiap record |
| Part tanpa destinasi | 1 record dengan DEST_CODE / CASE_DAY kosong (TBC) |
| Trailer | Jumlah record (TBC) |

## Tabel dummy: TB_R_CROSSDOCK_IF_RESULT
Hanya untuk menyimpan **status kirim** per part × target (PART_NO + TARGET_SYSTEM, PERIOD, IF_STATUS, IF_DT, IF_FILE_NAME, IF_MESSAGE). Output sebenarnya adalah **file ke GTOPAS**.

## Open points
- Topology SFTP (server, folder, user), format / nama file, file hasil dari target.
- Nama dan panjang field di GTOPAS.
- Part yang jadi **Inactive** (XD05) saat ini tidak dikirim → perlu kirim CROSSDOCK_FLAG 'N' supaya target berhenti crossdock?
