# Batch – Crossdock Master Setting – Part List Upload (X2)

Ringkasan poin-poin batch upload Part List: pemicu, alur, validasi, cara simpan, dan **semua tabel yang terlibat**.
Sumber: UISS-Batch `UISS_Batch_PartListUpload_v2.xlsx` (0.1 Initial Draft) dan keputusan bisnis sampai 13-Oct-26.

---

## 1. Tujuan
- Memproses file Excel yang diupload user Procurement dari sub-menu **Part List** sampai data tersimpan ke **TB_M_PART_CANDIDATE**.
- **All-or-nothing**: kalau ada 1 error (file atau baris), tidak ada data yang disimpan. Error dicatat di Log dan dibuatkan result report.

## 2. Pemicu
- On demand: user klik **[Validate file]** di modal *Upload Excel – part settings* (sub-menu Part List).
- Parameter: file yang diupload, login user.
- Tidak ada jadwal (bukan scheduler).

## 3. Input / Output
| Arah | Nama | Jenis | Keterangan |
|---|---|---|---|
| Input | File Part List (sheet **Upload**) | Excel | Hanya sheet "Upload" yang dibaca. Max 5 MB, 5.000 baris |
| Input | TB_M_PART_MASTER | DB | Cek Part No ada di part master, ambil Part Name |
| Input | TB_M_PART_CANDIDATE | DB | Data sekarang: cek duplikat, aturan status, pembanding Edit |
| Input | TB_M_PART_CANDIDATE_DEST | DB | Total Case/Day yang sudah di-mapping (check 9) |
| Output | TB_M_PART_CANDIDATE | DB | Insert (flag A) / Update (flag E) kalau semua valid |
| Output | TB_H_PART_CANDIDATE | DB | History per field yang berubah (event ADD / EDIT, source UPLOAD) |
| Output | Log (upload log) | DB | 1 record per upload: status, jumlah baris, error |
| Output | Result report | Excel | Selalu dibuat. Sheet: Summary, Result, Re-upload, Changes |

## 4. Template file (sheet "Upload")
Urutan kolom = sheet "Upload" hasil **Export Excel** Part List (prefill semua part dengan flag E).

| Kolom | Isi | Wajib |
|---|---|---|
| part_no | Part Number | Ya |
| min_mad | Minimum MAD (wajib, bilangan bulat ≥ 0); acuan pembanding hasil MAD dari calculation | Ya (≥ 0) |
| pcs_case | Pieces per case | Ya (> 0) |
| max_case_day | Max Case/Day | Ya (> 0) |
| status | Candidate / Active / Inactive | Lihat check 6 |
| flag_add_edit | A = Add, E = Edit | Ya |
| effective_start_date | DD-Mon-YYYY | Wajib selama status Candidate (selalu untuk flag A) |

## 5. Alur proses
1. User klik [Validate file] → batch mulai, terima file.
2. **Cek file** (4.1). Gagal → upload REJECTED, lompat ke langkah 7.
3. Baca semua baris sheet "Upload".
4. **Cek setiap baris** terhadap aturan 4.2, kumpulkan semua error (user cukup perbaiki file sekali).
5. Ada error → **tolak seluruh file**, tidak ada yang disimpan, error dicatat di Log.
6. Semua valid → simpan ke TB_M_PART_CANDIDATE:
   - Flag A: insert part baru dengan status **Candidate**.
   - Flag E: update nilai yang berubah (termasuk status Active ↔ Inactive). Baris tanpa perubahan **di-skip**.
   - Setiap part yang tersimpan → **Sync Status = No Sync (0)** dan history ke **TB_H_PART_CANDIDATE**.
7. Buat result report, catat hasil (COMPLETED / REJECTED) di Log, layar Part List menampilkan hasil.

## 6. Validasi
### 4.1 Cek file
1. Ekstensi **.xlsx**.
2. Ukuran ≤ **5 MB**.
3. Sheet Upload berisi **1–5.000** baris data.
4. Sheet **"Upload"** ada (sheet lain diabaikan).
5. Header berisi 7 kolom template (kolom tambahan diabaikan).

### 4.2 Cek baris
| No | Aturan | Kolom |
|---|---|---|
| 1 | flag_add_edit = A atau E | flag_add_edit |
| 2 | Part No ada di TB_M_PART_MASTER | part_no |
| 3 | Flag A: Part No **belum** ada di TB_M_PART_CANDIDATE. Flag E: **sudah** ada | part_no |
| 4 | Part No hanya muncul sekali dalam file | part_no |
| 5 | min_mad bilangan bulat ≥ 0, pcs_case dan max_case_day bilangan bulat > 0; ketiganya wajib | min_mad, pcs_case, max_case_day |
| 6 | Status: flag A harus kosong (part baru selalu Candidate). Flag E: part **Candidate tetap Candidate** (kosong/Candidate); Active ↔ Inactive **boleh**; tidak boleh diubah **menjadi Candidate** | status |
| 7 | Effective Start Date wajib selama status Candidate (selalu untuk flag A) dan ≥ hari ini kalau baru/berubah | effective_start_date |
| 8 | Flag E: Effective Start Date hanya bisa berubah selama status Candidate | effective_start_date |
| 9 | Flag E: Max Case/Day **tidak boleh di bawah** total Case/Day yang sudah di-mapping (periode berjalan, TB_M_PART_CANDIDATE_DEST). Kurangi mapping dulu di Mapping per Destination | max_case_day |

## 7. Aturan simpan
- Ada error → **tidak ada** yang tersimpan; status upload & error per baris dicatat di Log.
- Flag A → insert: PART_STATUS = Candidate, SYNC_STATUS = 0, LAST_SOURCE = UPLOAD, PART_NAME dari part master, TOTAL_PCS_DAY = PCS_CASE × MAX_CASE_DAY, MIN_MAD dari file.
- Flag E → update hanya kalau ada perubahan; status hanya Active ↔ Inactive.
- Status part **Candidate** hanya bisa diubah lewat modal *Edit part data* di layar, bukan upload.
- Part yang tersimpan dikirim ke global system oleh **RPA** saat D/S klik [Sync] di Mapping per Destination (lihat `BATCH_RPA_Sync.md`).

---

## 8. Tabel yang terlibat

### 8.1 TB_M_PART_CANDIDATE — *ditulis* (Part List, level part number)
Satu record per part, **tanpa periode**.

| Kolom | Tipe | PK | Null | Keterangan | Diisi saat upload |
|---|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number; panjang mengikuti TB_M_PART_MASTER | A: dari file; E: key |
| PART_NAME | VARCHAR(TBD) | | N | Dari TB_M_PART_MASTER | A: lookup; E: tidak berubah |
| MIN_MAD | INT | | N | Minimum MAD (wajib, bilangan bulat ≥ 0); acuan pembanding hasil MAD dari calculation | dari `min_mad` |
| PCS_CASE | INT | | N | Pieces per case (> 0) | dari file |
| MAX_CASE_DAY | INT | | N | Total Case/Day part (> 0) | dari file |
| TOTAL_PCS_DAY | INT | | N | PCS_CASE × MAX_CASE_DAY | dihitung |
| EFFECTIVE_START_DATE | DATE | | Y | Wajib selama Candidate | A: dari file; E: hanya selama Candidate |
| PART_STATUS | VARCHAR(TBD) | | N | Candidate / Active / Inactive | A: 'Candidate'; E: Active ↔ Inactive |
| SYNC_STATUS | CHAR(1) | | N | 0 No Sync, 3 Waiting, 1 Success, 2 Failed | '0' |
| SYNC_DT | DATETIME | | Y | Waktu hasil RPA terakhir | A: NULL; E: tidak berubah |
| SYNC_MESSAGE | VARCHAR(TBD) | | Y | Alasan sync Failed terakhir | A: NULL; E: tidak berubah |
| LAST_SOURCE | VARCHAR(TBD) | | N | CALC / SCREEN / UPLOAD | 'UPLOAD' |
| LAST_UPLOAD_ID | VARCHAR(TBD) | | Y | Upload terakhir yang mengubah record | UPLOAD_ID run ini |
| CREATED_BY | VARCHAR(TBD) | | N | User pembuat | A: login user |
| CREATED_DT | DATETIME | | N | Waktu dibuat | A: system date |
| CHANGED_BY | VARCHAR(TBD) | | N | User terakhir | login user |
| CHANGED_DT | DATETIME | | N | Waktu terakhir diubah | system date |

### 8.2 TB_M_PART_MASTER — *dibaca*
Part master existing NSP. Yang dipakai: **PART_NO** (cek keberadaan, check 2) dan **PART_NAME** (nama field TBD). Skema fisik lain TBD.

### 8.3 TB_M_PART_CANDIDATE_DEST — *dibaca*
Mapping per Destination, level **part number + periode + destinasi** (detail lihat `BATCH_Mapping_Upload.md`).
Dipakai di check 9: `SUM(CASE_DAY)` per PART_NO untuk **periode berjalan**.

### 8.4 Log (upload log) — *ditulis*
Di UISS cukup ditulis **"Log"** tanpa definisi tabel (sesuai arahan). Yang saya ketahui dari draft (nama fisik usulan: TB_R_CD_UPLOAD_LOG):

| Kolom | Tipe | Keterangan |
|---|---|---|
| UPLOAD_ID | VARCHAR(TBD) PK | ID upload dari layar |
| FUNCTION_ID | VARCHAR(TBD) | PART_LIST / MAPPING |
| FILE_NAME | VARCHAR(TBD) | Nama file |
| STATUS | VARCHAR(TBD) | PROCESSING / COMPLETED / REJECTED |
| TOTAL_ROWS / SAVED_ROWS / NO_CHANGE_ROWS / ERROR_ROWS | INT | Jumlah baris |
| RESULT_FILE_PATH | VARCHAR(TBD) | Lokasi result report |
| START_DT / END_DT | DATETIME | Mulai / selesai batch |
| CREATED_BY / CREATED_DT | | Audit |

### 8.5 TB_H_PART_CANDIDATE — *ditulis* (history)
Tabel history semua perubahan part. **Usulan** definisi fisik (insert only, satu record per field yang berubah; index PART_NO + CREATED_DT):

| Kolom | Tipe | PK | Null | Keterangan |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | Y | Calculation period YYYYMM for MAPPING / SYNC; NULL for ADD / EDIT (Part List has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / SYNC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / RPA |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | VARCHAR(TBD) |  | Y | Destination code for MAPPING; NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY, SYNC_STATUS |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text, e.g. SYNC_MESSAGE of a Failed sync |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (RPA user ID for SYNC) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

**Usulan retensi**: simpan 24 bulan online (berdasarkan CREATED_DT); housekeeping job bulanan menghapus record yang lebih lama. Periode bisa diatur di system master. Perlu konfirmasi.

| Event (EVENT_TYPE) | Source | Kapan | FIELD_NAME / nilai |
|---|---|---|---|
| ADD | SCREEN / UPLOAD | Part baru (Add Part di layar / flag A) | PCS_CASE, MAX_CASE_DAY, MIN_MAD, EFFECTIVE_START_DATE, PART_STATUS; OLD = NULL; PERIOD = NULL |
| EDIT | SCREEN / UPLOAD | Ubah data part (Edit di layar / flag E) | Field yang berubah; OLD → NEW; PERIOD = NULL |
| MAPPING | SCREEN / UPLOAD | Tambah / ubah / hapus destinasi (periode berjalan) | DEST_CODE terisi, FIELD_NAME = CASE_DAY; OLD NULL = ditambah, NEW NULL = dihapus |
| SYNC | RPA | Hasil Sync | FIELD_NAME = SYNC_STATUS; Waiting → Success / Failed (atau No Sync kalau berubah saat RPA jalan); REMARK = SYNC_MESSAGE |

UPLOAD_ID diisi untuk source UPLOAD (link ke Log).

Dibaca oleh modal *History setting* di Part List.

Di batch ini: event **ADD** (flag A) / **EDIT** (flag E), source **UPLOAD**, UPLOAD_ID run ini, satu record per field yang berubah.

---

## 9. Logging message
| No | Event | Tipe | Pesan |
|---|---|---|---|
| 1 | Batch start | Info | Upload batch <UPLOAD_ID> started. |
| 2 | Batch end | Info | Upload batch <UPLOAD_ID> ended. Status, total, saved, no change, error. |
| 3 | Receive file | Error | Uploaded file of <UPLOAD_ID> not found. |
| 4 | File check | Error | File check failed: <REASON>. |
| 5 | Row validation | Error | Row <ROW_NO> <COLUMN> : <RULE_MESSAGE>. |
| 6 | Row skipped | Info | Row <ROW_NO> Part No <PART_NO> has no change. Skipped. |
| 7 | Save to master | Error | Cannot save Part No <PART_NO> to TB_M_PART_CANDIDATE. → User contact PIC |
| 8 | Result report | Warning | Result report of <UPLOAD_ID> cannot be created. |
| 9 | Unexpected error | Critical | Unexpected error: <ERROR_DETAIL>. → User contact PIC |

MSG ID: LOG1–LOG9 (sesuai nomor).

## 10. Contoh skenario (sheet *Sample Input* di UISS)
- Diterima: N1–N8 (Add, Edit Candidate, naik Max Case/Day, tanpa perubahan, sebagian part, turunkan Max setelah mapping dikurangi, Active→Inactive).
- Ditolak: E1–E15 (flag salah, part tidak ada, duplikat, angka salah, ubah status Candidate, ubah ke Candidate, tanggal lampau, Max di bawah mapping, campuran valid+error, Add tanpa Min MAD).
- Error file: F1–F5.

## 11. Open points
- Panjang VARCHAR semua kolom dan nama field Part Name di TB_M_PART_MASTER.
- Lokasi file template & result report; retensi Log.
- Konfirmasi usulan kolom dan retensi TB_H_PART_CANDIDATE.
- ~~Batch ID dan MSG ID~~ → X2, LOG1–LOG9.
