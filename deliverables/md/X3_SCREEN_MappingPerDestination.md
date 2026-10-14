# Screen – Crossdock Master Setting – Mapping per Destination

Ringkasan poin-poin layar Mapping per Destination: akses, kriteria, panel mapping, aturan Save, Sync via RPA, Upload / Export, pesan, dan **semua tabel yang terlibat**.
Sumber: UISS-Screen `X3_UISS_Screen_MappingPerDestination.xlsx` (0.1 Initial Draft) dan keputusan bisnis sampai 13-Oct-26.
Screen ID: **X3**.

---

## 1. Tujuan
- Membagi Max Case/Day setiap part **Active** ke destinasi (Thailand, Japan, Vietnam) untuk **periode kalkulasi berjalan**.
- Menampilkan mapping per part dan periode, termasuk periode lalu (read only).
- Menyerahkan part yang berubah ke **RPA** untuk dikirim ke global system dan menampilkan Sync Status.
- Export mapping ke Excel dan upload mapping periode berjalan dari Excel.

## 2. Akses
- Hanya user dengan akun **D/S**. Akun Procurement membuka sub-menu **Part List**.

## 3. Tampilan awal & kriteria
| Kriteria | Awal | Aturan |
|---|---|---|
| Calculation period | Periode berjalan, mis. "Sep 2026 (ongoing)" | All periods / tiap periode; label (ongoing) / (past) / (all) |
| Part Number | Kosong | Contains, case-insensitive |
| Sync Status | **No Sync** | All / No Sync / Waiting / Success / Failed |

- Kriteria diterapkan saat klik **[Search]** (atau Enter di Part Number); memilih kriteria saja tidak mengubah list. Upload Excel dan Export mengikuti periode yang sudah di-Search.
- Semua kriteria digabung **AND**. Tidak ada hasil → MSG1.
- **Periode berjalan**: semua part **Active** dari TB_M_PART_CANDIDATE + destinasinya (part tanpa destinasi tampil dengan Total Case/Day 0).
- **Periode lalu**: semua part yang punya baris di TB_M_PART_CANDIDATE_DEST untuk periode itu, apa pun statusnya sekarang. All periods = keduanya.
- Default No Sync → part Success / Failed tersembunyi sampai filter diubah.
- **Paging**: 25 baris per halaman (25 / 50 / 100), info "1–25 of N parts · page 1/n", tombol Prev / Next. Satu part (termasuk panel mapping-nya) = 1 baris. Search, Reset, dan ganti Rows per page → kembali ke halaman 1.
- Periode kalkulasi dibuat oleh **batch calculation**. Periode terakhir yang dibuat = periode berjalan; periode sebelumnya jadi periode lalu (read only).
- Periode baru **mulai kosong**: mapping periode sebelumnya tidak disalin. Semua part **Active** tetap muncul dengan jatah Max Case/Day dari Part List, tapi belum di-assign ke destinasi (Total Case/Day 0, 0%, panel "no destination yet") sampai user D/S mengisi lewat Edit mapping atau Upload Excel.

## 4. Result list
| Kolom | Keterangan |
|---|---|
| Period | Periode kalkulasi baris |
| Expand (panah) | Buka / tutup panel Destination Mapping |
| Part Number, Part Name, Pcs/Case | Dari TB_M_PART_CANDIDATE |
| Total Case/Day | Jumlah CASE_DAY semua destinasi part + periode |
| Pcs/Day | Pcs/Case × Total Case/Day |
| Percentage | Total Case/Day / Max Case/Day; tidak pernah > 100% (Save, upload, dan edit Max Case/Day di Part List diblok) |
| Sync Status | 0 No Sync (abu), 3 Waiting (kuning), 1 Success (hijau), 2 Failed (merah, tooltip SYNC_MESSAGE) |

Tombol di atas tabel: **[Sync (n)]**, **[Upload Excel]**, **[Export Excel]**.

## 5. Panel Destination Mapping
- Chip alokasi: merah (total > Max), abu (total < Max), hijau (sama).
- Catatan: "no destination yet" / "{n} case/day over" / "{n} case/day left" / "capacity fully allocated".
- Kolom: Destination (CD), Case/Day, Pcs/Day (= Pcs/Case × Case/Day), Percentage (= Case/Day / total Case/Day part).
- Periode berjalan → [Edit mapping]. Periode lalu → badge "Past period - read only" (MSG5).
- Part tanpa destinasi → MSG2.

## 6. Edit mapping & aturan Save
1. Klik [Edit mapping] → draft; Destination & Case/Day bisa diubah, ikon trash per baris, [Add destination].
2. Daftar Destination menyembunyikan destinasi yang sudah dipakai baris lain part yang sama (**satu destinasi sekali per part**).
3. [Add destination] → baris baru "Select destination", Case/Day 0.
4. [Split evenly] (> 1 baris): floor(Max Case/Day / jumlah baris), sisa +1 per baris dari baris pertama. Contoh 24/3 = 8/8/8; 25/3 = 9/8/8.
5. **[Save] disabled** kalau:
   - total Case/Day **>** Max Case/Day (MSG3);
   - part tidak punya baris destinasi; atau
   - ada baris tanpa destinasi (MSG4) — **ditolak, tidak bisa disimpan**.
   - Total **≤** Max Case/Day **boleh** (kurang ditampilkan "{n} case/day left").
6. Klik [Save]:
   - Mapping diubah user lain sejak edit dimulai → MSG8, stop.
   - **Replace** baris part + periode berjalan di TB_M_PART_CANDIDATE_DEST dengan isi draft.
   - TB_M_PART_CANDIDATE: **SYNC_STATUS = 0 (No Sync)**.
   - TB_H_PART_CANDIDATE: satu record per destinasi yang ditambah / diubah / dihapus (event **MAPPING**, source **SCREEN**).
   - Keluar edit mode.
7. [Cancel] / tutup panel → draft dibuang.

## 7. Sync (via RPA)
1. Klik **[Sync (n)]** (on demand). n = semua part **Active** periode berjalan dengan Sync Status **No Sync atau Failed**, **tidak tergantung filter**. Disabled kalau n = 0.
2. Part tersebut → **SYNC_STATUS = 3 (Waiting)**, fungsi RPA dijalankan, MSG10.
3. RPA per part Waiting: baca PCS_CASE, MAX_CASE_DAY + semua destinasi & CASE_DAY periode berjalan → **replace** di global system sebagai satu paket → tulis balik SYNC_STATUS 1 / 2, SYNC_DT, SYNC_MESSAGE.
4. Part diubah setelah dibaca RPA (CHANGED_DT beda) → SYNC_STATUS = 0, bukan Success.
5. Setiap hasil dicatat di **TB_H_PART_CANDIDATE** (event **SYNC**, source **RPA**).
6. Part Failed: tooltip MSG11, ikut lagi di Sync berikutnya. Candidate / Inactive tidak pernah di-sync.
Detail: `X3_RPA_Sync.md`.

## 7a. Run mapping calculation
- Header section menampilkan **Last mapping calculation** (tanggal sukses terakhir) dan badge **Scheduled run failed 3x** kalau jadwal + 3x auto retry gagal.
- Tombol **[Run calculation]** hanya aktif dalam kondisi gagal itu; selain itu disabled dengan tooltip MSG13.
- Klik → batch Mapping Destination Calculation jalan (membuat periode baru + mapping). Sukses → tanggal diperbarui, badge hilang, MSG12. Detail batch: `X5-X7_BATCH_Calculation_Functions.md`.

## 8. Upload Excel
- Aktif **hanya** kalau periode berjalan dipilih; periode lalu / All periods → disabled, tooltip MSG6.
- Kolom template: part_no, dest_code, case_day, total_case_day (referensi). File .xlsx, max 5 MB, max 5.000 baris.
- Base file: sheet **Upload** dari Export Excel (periode berjalan). Part di file → seluruh mapping di-replace; part yang tidak ada di file tidak berubah.
- [Validate file] = tombol simpan upload → batch Mapping per Destination Upload (all-or-nothing, Log). Detail: `X4_BATCH_Mapping_Upload.md`.
- Sukses → tutup modal, MSG7. Ditolak → hasil batch (daftar error). Part yang berubah → No Sync.

## 9. Export Excel
File `Crossdock_Mapping_per_Destination_<period>_YYYYMMDD.xlsx` (<period> mis. Sep_2026 / All_periods):
| Sheet | Isi |
|---|---|
| Mapping per Destination | Baris filter aktif, 1 baris per destinasi (part tanpa destinasi = 1 baris kosong): Period, Part Number, Part Name, Pcs/Case, Total Case/Day, Pcs/Day, Percentage, Sync Status, Destination Code, Destination, Dest Case/Day, Dest Pcs/Day, Dest Percentage. Informasi saja |
| Upload | Semua part Active periode berjalan: part_no, dest_code, case_day, total_case_day (= Max Case/Day); 1 baris per destinasi, part tanpa mapping = 1 baris placeholder. Kosong untuk periode lalu / All periods |

Gagal dibuat → MSG9.

---

## 10. Tabel yang terlibat

### 10.1 TB_M_PART_CANDIDATE_DEST — *dibaca & ditulis* (level part number + periode + destinasi)
| Kolom | PK | Keterangan | Saat Save mapping |
|---|---|---|---|
| PART_NO | Y | FK ke TB_M_PART_CANDIDATE | Part yang diedit |
| PERIOD | Y | Periode kalkulasi, CHAR(6) YYYYMM mis. 202609, tampil "Sep 2026" | Periode berjalan |
| DEST_CODE | Y | Kode destinasi (ada di TB_M_H0125) | Dari draft |
| CASE_DAY | | Case/Day destinasi (> 0) | Dari draft |
| CREATED_BY / CREATED_DT | | Audit | Login user / system date |
| CHANGED_BY / CHANGED_DT | | Audit, juga concurrency check | Login user / system date |

Cara simpan: hapus semua baris part + periode berjalan, lalu insert baris draft (replace).

### 10.2 TB_M_PART_CANDIDATE — *dibaca & diupdate* (level part number)
| Kolom | Peran di layar ini |
|---|---|
| PART_NO, PART_NAME, PCS_CASE | Ditampilkan |
| MAX_CASE_DAY | Batas total mapping, Percentage, Split evenly |
| PART_STATUS | Hanya **Active** ditampilkan di periode berjalan dan di-sync |
| SYNC_STATUS | Filter & chip; '0' saat Save mapping, '3' saat klik Sync, 1/2/0 oleh RPA |
| SYNC_DT, SYNC_MESSAGE | Diisi RPA; SYNC_MESSAGE jadi tooltip Failed |
| CHANGED_BY / CHANGED_DT | Diupdate saat Save; dibandingkan RPA |

### 10.3 TB_M_H0125 (Destination Master) — *dibaca*
Tabel master existing NSP, **hanya dibaca**. Kolom yang relevan (kolom lain diabaikan; nama fisik mengikuti tabel existing):

| Kolom | Dipakai Crossdock |
|---|---|
| Destination Code (PK) | **Ya** – list Destination (CD), cek upload no. 2, disimpan sebagai DEST_CODE |
| Customer Code | Referensi |
| Order Transportation Code | Referensi |
| B/O Instruction Code | Referensi |
| Destination Name | **Ya** – tampil bersama kode ("9722D10 - Thailand") dan di Export Excel |
| Region Code | Referensi |
| Country Name | Referensi |
| Postal Code | Referensi |
| State Code | Referensi |
| Destination Address 1 / 2 | Referensi |
| CREATED_BY | Audit – user pembuat |
| CREATED_DT | Audit – waktu dibuat |
| UPDATED_BY | Audit – user terakhir |
| UPDATED_DT | Audit – waktu terakhir diubah |

Contoh data: 9722D10 Thailand, 9811110 Japan, 9618201 Vietnam.

### 10.4 TB_H_PART_CANDIDATE — *ditulis* (history)
Tabel history semua perubahan part. **Usulan** definisi fisik (insert only, satu record per field yang berubah; index PART_NO + CREATED_DT):

| Kolom | Tipe | PK | Null | Keterangan |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | Y | Calculation period YYYYMM for MAPPING / SYNC; NULL for ADD / EDIT (Part List has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / SYNC / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / RPA / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
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
| CALC | BATCH | Status diubah DAD Volume Calculation | FIELD_NAME = PART_STATUS; OLD → NEW status; REMARK = rata-rata MAD vs Min MAD |
| MAPPING | BATCH | Mapping periode baru dari Mapping Destination Calculation | Sama dengan MAPPING di atas (OLD = periode sebelumnya) |

UPLOAD_ID diisi untuk source UPLOAD (link ke Log).

Di layar ini: event **MAPPING** source **SCREEN** saat Save (PERIOD = periode berjalan, DEST_CODE = destinasi, FIELD_NAME = CASE_DAY, OLD/NEW = Case/Day; hapus destinasi = NEW NULL), dan event **SYNC** source **RPA** dari hasil Sync. Dibaca di modal History setting Part List.

### 10.5 Tabel terkait
- **Log** – upload log, ditulis batch Mapping per Destination Upload.
- **Global system TMMIN** – tujuan RPA (tanpa interface).

---

## 11. Pesan layar (MSG1–MSG13; logging LOG1–LOG3)
| ID | Kapan | Tipe | Pesan |
|---|---|---|---|
| MSG1 | Filter tanpa hasil | Info | No parts match these filters - Change the period or sync status, or press Reset to show all parts. |
| MSG2 | Part tanpa destinasi | Info | No destination yet - Click Edit mapping and add at least one destination … |
| MSG3 | Total > Max Case/Day | Error | Allocation of {n} case/day exceeds Max Case/Day ({m}). Reduce one of the destinations. |
| MSG4 | Baris tanpa destinasi | Error | Select a destination for every row, or remove the empty row, before saving. |
| MSG5 | Panel periode lalu | Info | Past period - read only |
| MSG6 | Hover Upload disabled | Info | Past period - read only. Select the ongoing period to upload. |
| MSG7 | Upload sukses | Info | Saved successfully - Upload completed. … |
| MSG8 | Save, diubah user lain | Error | Error in Update because of concurrency check. |
| MSG9 | Export gagal | Error | Export Excel failed. Please try again. |
| MSG10 | Klik Sync | Info | Sync requested for {n} part(s). They stay Waiting until the RPA has sent them to the global system. |
| MSG11 | Hover chip Failed | Info | Sync failed: {SYNC_MESSAGE}. The part is sent again with the next Sync. |
| MSG12 | Run calculation sukses | Info | Calculation completed - Mapping destination calculation completed. … |
| MSG13 | Hover Run calculation disabled | Info | Enabled only when the scheduled run has failed 3 times |

## 12. Open points
- Detail fungsi RPA; batas waktu status Waiting.
- Konfirmasi usulan kolom dan retensi TB_H_PART_CANDIDATE (10.4).
