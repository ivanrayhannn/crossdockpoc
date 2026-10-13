# Batch – Crossdock Master Setting – Mapping per Destination Upload

Ringkasan poin-poin batch upload Mapping per Destination: pemicu, alur, validasi, cara simpan, dan **semua tabel yang terlibat**.
Sumber: UISS-Batch `UISS_Batch_MappingUpload.xlsx` (0.1 Initial Draft) dan keputusan bisnis sampai 13-Oct-26.
Batch ID: **X4**.

---

## 1. Tujuan
- Memproses file Excel mapping yang diupload user D/S dari sub-menu **Mapping per Destination** sampai mapping **periode berjalan** tersimpan ke **TB_M_PART_CANDIDATE_DEST**.
- **All-or-nothing**: 1 error = tidak ada yang disimpan; error dicatat di Log dan dibuatkan result report.

## 2. Pemicu
- On demand: user klik **[Validate file]** di modal *Upload Excel – destination mapping*.
- Tombol Upload Excel hanya aktif kalau filter Calculation period = **periode berjalan** (disabled untuk periode past / All periods).
- Parameter: file yang diupload, login user. Grouping key: **part_no**.

## 3. Input / Output
| Arah | Nama | Jenis | Keterangan |
|---|---|---|---|
| Input | File Mapping (sheet **Upload**) | Excel | Hanya sheet "Upload". Max 5 MB, 5.000 baris |
| Input | TB_M_PART_CANDIDATE | DB | Status part (harus Active) dan Max Case/Day |
| Input | TB_M_PART_CANDIDATE_DEST | DB | Mapping sekarang periode berjalan (deteksi tanpa perubahan) |
| Input | TB_M_H0125 (Destination Master) | DB | Kode destinasi valid: 123 Thailand, 456 Japan, 789 Vietnam |
| Output | TB_M_PART_CANDIDATE_DEST | DB | Mapping part yang berubah di-**replace** (periode berjalan) |
| Output | TB_M_PART_CANDIDATE | DB | Sync Status = No Sync untuk part yang berubah |
| Output | TB_H_PART_CANDIDATE | DB | History per destinasi yang ditambah / diubah / dihapus (event MAPPING, source UPLOAD) |
| Output | Log (upload log) | DB | 1 record per upload |
| Output | Result report | Excel | Summary, Result, Re-upload, Changes |

## 4. Template file (sheet "Upload")
Diisi otomatis oleh **Export Excel** (periode berjalan dipilih): semua part **Active** periode berjalan, **1 baris per destinasi**; part tanpa mapping = 1 baris placeholder (dest_code & case_day kosong). Kosong untuk periode past / All periods.

| Kolom | Isi |
|---|---|
| part_no | Part Number part Active |
| dest_code | Kode destinasi (123 / 456 / 789), sekali per part |
| case_day | Case/Day destinasi, bilangan bulat > 0 |
| total_case_day | Max Case/Day part, **hanya referensi** (tidak dibaca batch) |

## 5. Alur proses
1. User klik [Validate file] (periode berjalan) → batch mulai.
2. **Cek file** (4.1). Gagal → REJECTED, ke langkah 7.
3. Baca semua baris, **kelompokkan per part_no**.
4. Cek setiap baris dan setiap part (4.2), kumpulkan semua error. Baris placeholder (keduanya kosong) di-skip.
5. Ada error → tolak seluruh file, tidak ada yang disimpan.
6. Semua valid → bandingkan tiap part dengan mapping sekarang:
   - Destinasi & Case/Day sama → **skip** (no change).
   - Berbeda → **replace** seluruh mapping part (periode berjalan) dengan isi file; Sync Status = No Sync.
   - Part yang barisnya kosong semua → **tidak diubah** (mapping tidak bisa dihapus total lewat upload, sama seperti layar).
7. Buat result report, catat hasil di Log, layar menampilkan hasil.

## 6. Validasi
### 4.1 Cek file
1. Ekstensi .xlsx. 2. ≤ 5 MB. 3. 1–5.000 baris data. 4. Sheet "Upload" ada. 5. Header 4 kolom template.

### 4.2 Cek baris / part
| No | Aturan | Kolom |
|---|---|---|
| 1 | Part No ada di TB_M_PART_CANDIDATE dan status **Active** | part_no |
| 2 | Kode destinasi ada di TB_M_H0125 (Destination Master) | dest_code |
| 3 | case_day bilangan bulat > 0 kalau dest_code diisi | case_day |
| 4 | Satu kode destinasi hanya sekali per part | dest_code |
| 5 | dest_code dan case_day **keduanya diisi atau keduanya kosong** (placeholder) | dest_code, case_day |
| 6 | Total case_day per part **≤ Max Case/Day** (TB_M_PART_CANDIDATE); kurang atau sama boleh | case_day |
| 7 | Hanya untuk periode berjalan | – |

## 7. Aturan simpan
- Part di file yang berubah: **hapus** semua baris part + periode berjalan di TB_M_PART_CANDIDATE_DEST, lalu **insert** baris dari file (destinasi baru ditambah, yang tidak ada di file terhapus).
- Part yang tidak ada di file: tidak diubah.
- TB_H_PART_CANDIDATE: satu record per destinasi yang ditambah / diubah / dihapus.
- TB_M_PART_CANDIDATE part yang berubah: SYNC_STATUS = 0, LAST_SOURCE = UPLOAD, LAST_UPLOAD_ID, CHANGED_BY/DT. Kolom lain tidak berubah.
- Pengiriman ke global system dilakukan **RPA** saat D/S klik [Sync] (lihat `BATCH_RPA_Sync.md`).

---

## 8. Tabel yang terlibat

### 8.1 TB_M_PART_CANDIDATE_DEST — *ditulis* (Mapping, level part number + periode + destinasi)
| Kolom | Tipe | PK | Null | Keterangan | Diisi saat upload |
|---|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | FK ke TB_M_PART_CANDIDATE | dari file |
| PERIOD | VARCHAR(TBD) | Y | N | Periode kalkulasi, mis. Sep 2026 (format TBD) | periode berjalan |
| DEST_CODE | VARCHAR(TBD) | Y | N | Kode destinasi; ada di TB_M_H0125 | dari file |
| CASE_DAY | INT | | N | Case/Day destinasi (> 0) | dari file |
| CREATED_BY | VARCHAR(TBD) | | N | User pembuat | login user |
| CREATED_DT | DATETIME | | N | Waktu dibuat | system date |
| CHANGED_BY | VARCHAR(TBD) | | N | User terakhir | login user |
| CHANGED_DT | DATETIME | | N | Waktu terakhir diubah | system date |

### 8.2 TB_M_PART_CANDIDATE — *dibaca & diupdate* (Part List, level part number)
| Kolom | Tipe | PK | Null | Keterangan | Saat upload mapping |
|---|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number | key |
| PART_NAME | VARCHAR(TBD) | | N | Dari part master | tidak berubah |
| MAD | INT | | Y | Hasil fungsi kalkulasi MAD | tidak berubah |
| PCS_CASE | INT | | N | Pieces per case | tidak berubah |
| MAX_CASE_DAY | INT | | N | Batas total mapping | **dibaca** (check 6) |
| TOTAL_PCS_DAY | INT | | N | PCS_CASE × MAX_CASE_DAY | tidak berubah |
| EFFECTIVE_START_DATE | DATE | | Y | Tanggal efektif | tidak berubah |
| PART_STATUS | VARCHAR(TBD) | | N | Candidate / Active / Inactive | **dibaca** (harus Active) |
| SYNC_STATUS | CHAR(1) | | N | 0 No Sync, 3 Waiting, 1 Success, 2 Failed | '0' kalau berubah |
| SYNC_DT | DATETIME | | Y | Hasil RPA terakhir | tidak berubah |
| SYNC_MESSAGE | VARCHAR(TBD) | | Y | Alasan Failed | tidak berubah |
| LAST_SOURCE | VARCHAR(TBD) | | N | CALC / SCREEN / UPLOAD | 'UPLOAD' |
| LAST_UPLOAD_ID | VARCHAR(TBD) | | Y | Upload terakhir | UPLOAD_ID |
| CREATED_BY / CREATED_DT | | | N | Audit | tidak berubah |
| CHANGED_BY / CHANGED_DT | | | N | Audit | login user / system date |

### 8.3 TB_M_H0125 (Destination Master) — *dibaca*
Isi yang diketahui: 123 Thailand, 456 Japan, 789 Vietnam (kode + nama).

### 8.4 Log (upload log) — *ditulis*
Di UISS ditulis **"Log"** saja. Struktur yang diketahui sama dengan Part List Upload (UPLOAD_ID, FUNCTION_ID = MAPPING, FILE_NAME, STATUS, jumlah baris, RESULT_FILE_PATH, START_DT/END_DT, audit). Untuk mapping: SAVED_ROWS = jumlah part yang di-replace, NO_CHANGE_ROWS = jumlah part yang di-skip.

### 8.5 TB_H_PART_CANDIDATE — *ditulis* (history)
Tabel history semua perubahan part. **Usulan** definisi fisik (insert only, satu record per field yang berubah; index PART_NO + CREATED_DT):

| Kolom | Tipe | PK | Null | Keterangan |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | VARCHAR(TBD) |  | Y | Calculation period for MAPPING / SYNC; NULL for ADD / EDIT (Part List has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / SYNC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / RPA |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | VARCHAR(TBD) |  | Y | Destination code for MAPPING; NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY, SYNC_STATUS |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text, e.g. SYNC_MESSAGE of a Failed sync |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (RPA user ID for SYNC) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

**Usulan retensi**: simpan 24 bulan online (berdasarkan CREATED_DT); housekeeping job bulanan menghapus record yang lebih lama. Periode bisa diatur di system master. Perlu konfirmasi.

| Event (EVENT_TYPE) | Source | Kapan | FIELD_NAME / nilai |
|---|---|---|---|
| ADD | SCREEN / UPLOAD | Part baru (Add Part di layar / flag A) | PCS_CASE, MAX_CASE_DAY, MAD, EFFECTIVE_START_DATE, PART_STATUS; OLD = NULL; PERIOD = NULL |
| EDIT | SCREEN / UPLOAD | Ubah data part (Edit di layar / flag E) | Field yang berubah; OLD → NEW; PERIOD = NULL |
| MAPPING | SCREEN / UPLOAD | Tambah / ubah / hapus destinasi (periode berjalan) | DEST_CODE terisi, FIELD_NAME = CASE_DAY; OLD NULL = ditambah, NEW NULL = dihapus |
| SYNC | RPA | Hasil Sync | FIELD_NAME = SYNC_STATUS; Waiting → Success / Failed (atau No Sync kalau berubah saat RPA jalan); REMARK = SYNC_MESSAGE |

UPLOAD_ID diisi untuk source UPLOAD (link ke Log).

Dibaca oleh modal *History setting* di Part List.

Di batch ini: event **MAPPING**, source **UPLOAD**, PERIOD = periode berjalan, UPLOAD_ID run ini, DEST_CODE + FIELD_NAME CASE_DAY, satu record per destinasi yang ditambah / diubah / dihapus.

---

## 9. Logging message
| No | Event | Tipe | Pesan |
|---|---|---|---|
| 1 | Batch start | Info | Mapping upload batch <UPLOAD_ID> started. |
| 2 | Batch end | Info | … ended. Status, total, saved parts, no change, error. |
| 3 | Receive file | Error | Uploaded file of <UPLOAD_ID> not found. |
| 4 | File check | Error | File check failed: <REASON>. |
| 5 | Row validation | Error | Row <ROW_NO> <COLUMN> : <RULE_MESSAGE>. |
| 6 | Part skipped | Info | Part No <PART_NO> has no mapping change. Skipped. |
| 7 | Save mapping | Error | Cannot save the mapping of Part No <PART_NO>. → User contact PIC |
| 8 | Result report | Warning | Result report of <UPLOAD_ID> cannot be created. |
| 9 | Unexpected error | Critical | Unexpected error: <ERROR_DETAIL>. → User contact PIC |

## 10. Contoh skenario (sheet *Sample Input*)
- Diterima: N1 ubah Case/Day, N2 hapus destinasi, N3 tambah destinasi, N4 mapping pertama dari placeholder, N5 placeholder dibiarkan kosong, N6 sama dengan master, N7 hanya sebagian part.
- Ditolak: E1 part tidak terdaftar, E2 part bukan Active, E3 destinasi tidak dikenal, E4 Case/Day 0, E5 destinasi dobel, E6 hanya salah satu kolom diisi, E7 total > Max Case/Day, E8 campuran valid+error.
- Error file: F1–F5.

## 11. Open points
- Format PERIOD dan cara periode dibuat; nama kolom di TB_M_H0125.
- Panjang VARCHAR; lokasi template & result report; retensi Log.
- Konfirmasi usulan kolom dan retensi TB_H_PART_CANDIDATE.
- ~~Batch ID dan MSG ID~~ → X4, LOG1–LOG9. ~~Persentase > 100%~~ → tidak perlu.
