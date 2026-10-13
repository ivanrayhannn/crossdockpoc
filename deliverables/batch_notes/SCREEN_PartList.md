# Screen – Crossdock Master Setting – Part List (X1)

Ringkasan poin-poin layar Part List: akses, item, aturan Add / Edit, History, Upload / Export, pesan, dan **semua tabel yang terlibat**.
Sumber: UISS-Screen `UISS_Screen_PartList.xlsx` (X1, 0.1 Initial Draft) dan keputusan bisnis sampai 13-Oct-26.

---

## 1. Tujuan
- Mendaftarkan part kandidat crossdock (Part No, Min MAD, Pcs/Case, Max Case/Day, Effective Start Date).
- Mencari dan menampilkan part terdaftar dengan status, kapasitas, dan kelengkapan mapping.
- Mengubah data dan status part (Candidate / Active / Inactive).
- Menampilkan history perubahan part.
- Export Part List ke Excel dan upload setting part dari Excel (Add dan Edit).

## 2. Akses
- Hanya user dengan akun **Procurement**. Akun D/S membuka sub-menu **Mapping per Destination**.

## 3. Tampilan awal & kriteria
| Kriteria | Awal | Aturan |
|---|---|---|
| Part Number | Kosong | Contains, case-insensitive; saran dari PART_NO terdaftar |
| Part Name | Kosong | Contains, case-insensitive |
| Status | All | All / Candidate / Active / Inactive |
| Sort by | Newer to Older | Default (Part Number A-Z) / Newer to Older / Older to Newer (Last Update) |

- Kriteria baru diterapkan saat klik **[Search]** (atau Enter di text box). Mengetik / memilih kriteria saja **tidak** mengubah list. **Sort by** langsung diterapkan.
- Semua kriteria digabung **AND**; klik Search / ubah sort / rows per page → kembali ke halaman 1.
- 25 baris per halaman (25 / 50 / 100), Prev / Next.
- Tidak ada hasil → MSG1 + [Reset filter]. Belum ada part sama sekali → MSG2 + [Upload Excel] / [Add one part].

## 4. Result list
| Kolom | Keterangan |
|---|---|
| Part Number | Link → modal Edit (sama dengan [Edit]) |
| Part Name | Terpotong '...' kalau panjang, tooltip nama lengkap |
| Min MAD | Minimum MAD (wajib, bilangan bulat ≥ 0); acuan pembanding hasil MAD dari calculation |
| Pcs/Case, Max Case/Day | Dari TB_M_PART_CANDIDATE |
| Total Pcs/Day | Pcs/Case × Max Case/Day |
| Status | Candidate (biru) / Active (hijau) / Inactive (abu) |
| Last Update | Tanggal-jam + user perubahan terakhir |
| Edit / History | Tombol [Edit] dan ikon jam (History) |

- Counter **"N parts · M incomplete mappings"** dihitung dari seluruh hasil filter (semua halaman).
- **Incomplete mapping**: part tanpa destinasi di TB_M_PART_CANDIDATE_DEST, atau total CASE_DAY ≠ MAX_CASE_DAY → bar biru di baris.

## 5. Add Part
1. Klik [Add Part] → modal *Add Part Candidate Crossdock*.
2. Status = **Candidate** dan terkunci (part baru selalu Candidate).
3. Part No: daftar part di TB_M_PART_MASTER yang **belum** terdaftar di TB_M_PART_CANDIDATE. Pilih → Part Name terisi otomatis.
4. Effective Start Date = system date + 1 hari, minimum hari ini.
5. **Min MAD wajib** (bilangan bulat ≥ 0), acuan untuk dibandingkan dengan hasil MAD dari calculation.
6. Max Case/Day terkunci sampai Pcs/Case diisi. Total Pcs/Day dihitung ulang setiap perubahan.
7. [Save] aktif hanya kalau Part No, Min MAD, Pcs/Case > 0, Max Case/Day > 0 terisi; tooltip MSG5 / MSG15 / MSG6 / MSG7.
7. Save:
   - Part No sudah didaftarkan user lain → MSG3, stop.
   - Insert TB_M_PART_CANDIDATE (PART_STATUS Candidate, SYNC_STATUS 0, LAST_SOURCE SCREEN).
   - Insert history TB_H_PART_CANDIDATE (event **ADD**, source **SCREEN**).
   - Tutup modal, reset filter, sort Newer to Older, MSG9; part baru di paling atas.

## 6. Edit Part Data
1. Klik link Part Number atau [Edit] → modal *Edit part data* dengan nilai tersimpan.
2. Part No terkunci; Status bisa Candidate / Active / Inactive.
3. **Effective Start Date hanya bisa diubah selama status tersimpan Candidate** (minimum hari ini); selain itu terkunci dengan tooltip MSG10.
4. Min MAD (wajib), Pcs/Case, Max Case/Day bisa diubah.
5. **Max Case/Day tidak boleh lebih kecil dari total Case/Day yang sudah di-mapping** di periode berjalan (TB_M_PART_CANDIDATE_DEST). Kalau lebih kecil: field merah, MSG14 tampil, [Save] disabled. User harus kurangi mapping dulu di Mapping per Destination (aturan sama dengan upload check 9). Dicek lagi di server saat Save.
6. Save:
   - Data diubah user lain setelah dibuka → MSG4, stop.
   - Max Case/Day < total mapping → MSG14, stop.
   - Update TB_M_PART_CANDIDATE, **SYNC_STATUS = 0 (No Sync)** setiap Save, CHANGED_BY/DT.
   - Insert history TB_H_PART_CANDIDATE (event **EDIT**, source **SCREEN**), satu record per field yang berubah.
   - Tutup modal, part pindah ke atas, MSG9.

## 7. History setting
- Klik ikon jam → timeline perubahan part, terbaru di atas.
- Tiap event: judul, tanggal-jam, nama field, nilai lama (dicoret) → nilai baru, user.
- Dibaca dari **TB_H_PART_CANDIDATE**: semua event part (Add / Edit layar, Upload, Mapping, Sync).
- Tidak ada history → MSG12.

## 8. Upload Excel
- Modal menampilkan kolom template, aturan, dan area file (.xlsx, max 5 MB, max 5.000 baris).
- Kolom: part_no, min_mad (wajib), pcs_case, max_case_day, status, flag_add_edit (A/E), effective_start_date.
- Base file Edit = sheet **Upload** dari Export Excel (flag E sudah terisi).
- Aturan status: Candidate **tidak bisa diubah** lewat upload; Active ↔ Inactive boleh; tidak ada yang bisa diubah ke Candidate.
- [Validate file] = tombol simpan upload → batch Part List Upload (validasi, simpan all-or-nothing, Log). Detail: `BATCH_PartList_Upload.md`.
- Sukses → tutup modal, MSG11. Ditolak → hasil batch (daftar error).
- Part yang berubah → Sync Status No Sync.

## 9. Export Excel
File `Crossdock_Part_List_YYYYMMDD.xlsx`:
| Sheet | Isi |
|---|---|
| Part List | Baris filter aktif (semua halaman): Part Number, Part Name, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, Status, Effective Start Date, Last Update. Informasi saja |
| Upload | Semua part terdaftar: part_no, min_mad, pcs_case, max_case_day, status, flag_add_edit = E, effective_start_date (DD-Mon-YYYY). Base file upload Edit |

Gagal dibuat → MSG13.

## 10. Status
| Status | Nilai | Arti |
|---|---|---|
| Part | Candidate | Part baru tanpa history MAD; status awal semua part baru |
| Part | Active | Hanya part Active yang di-mapping dan di-sync |
| Part | Inactive | Tidak di-mapping |
| Sync | 0 No Sync | Belum dikirim / berubah sejak sync terakhir; diset setiap Save |
| Sync | 3 Waiting | [Sync] diklik di Mapping per Destination, menunggu RPA |
| Sync | 1 Success | RPA berhasil mengirim |
| Sync | 2 Failed | RPA gagal (alasan di SYNC_MESSAGE), ikut lagi di Sync berikutnya |

Save saat part masih Waiting → kembali No Sync.

---

## 11. Tabel yang terlibat

### 11.1 TB_M_PART_CANDIDATE — *dibaca, insert, update* (level part number)
| Kolom | Add (Insert) | Edit (Update) |
|---|---|---|
| PART_NO (PK) | Dari layar | Key |
| PART_NAME | Dari TB_M_PART_MASTER | Tidak berubah |
| MIN_MAD | Dari layar (wajib) | Dari layar (wajib) |
| PCS_CASE | Dari layar | Dari layar |
| MAX_CASE_DAY | Dari layar | Dari layar |
| TOTAL_PCS_DAY | PCS_CASE × MAX_CASE_DAY | Dihitung ulang |
| EFFECTIVE_START_DATE | Dari layar | Hanya selama status tersimpan Candidate |
| PART_STATUS | 'Candidate' | Dari layar |
| SYNC_STATUS | '0' | '0' setiap Save |
| SYNC_DT / SYNC_MESSAGE | NULL (diisi RPA) | Tidak berubah |
| LAST_SOURCE | 'SCREEN' | 'SCREEN' |
| LAST_UPLOAD_ID | NULL | Tidak berubah |
| CREATED_BY / CREATED_DT | Login user / system date | Tidak berubah |
| CHANGED_BY / CHANGED_DT | Login user / system date | Login user / system date (juga untuk concurrency check) |

### 11.2 TB_M_PART_MASTER — *dibaca*
Sumber daftar Part No (yang belum terdaftar) dan Part Name.

### 11.3 TB_M_PART_CANDIDATE_DEST — *dibaca*
Untuk menghitung **incomplete mapping** (tanpa destinasi atau total CASE_DAY ≠ MAX_CASE_DAY) dan cek Max Case/Day ≥ total mapping periode berjalan di Edit. Tidak diubah dari layar ini.

### 11.4 TB_H_PART_CANDIDATE — *ditulis & dibaca* (history)
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

Di layar ini: **ditulis** event ADD / EDIT dengan source SCREEN (PERIOD NULL, Part List tidak punya periode); **dibaca** semua event untuk modal History setting (urut CREATED_DT terbaru).

### 11.5 Tabel terkait (tidak diubah layar ini)
- **Log** – upload log, ditulis oleh batch Part List Upload.

---

## 12. Pesan layar
| ID | Kapan | Tipe | Pesan |
|---|---|---|---|
| MSG1 | Filter tanpa hasil | Info | No matching parts - Loosen the search criteria or reset all filters. |
| MSG2 | Belum ada part | Info | No crossdock parts registered yet |
| MSG3 | Save Add, part sudah terdaftar | Error | Duplication found for {Part No} |
| MSG4 | Save, diubah user lain | Error | Error in Update because of concurrency check. |
| MSG5 | Hover Save, Part No kosong | Info | Part No is required |
| MSG6 | Hover Save, Pcs/Case kosong | Info | Enter Pcs/Case first (step 2) |
| MSG7 | Hover Save, Max Case/Day kosong | Info | Enter Max Case/Day (step 2) |
| MSG8 | Ketik Part No, tidak ketemu | Info | Part not found |
| MSG9 | Save sukses | Info | Saved successfully - {Part No} · {Part Name} has been added/updated. It is now at the top of the Part List. |
| MSG10 | Hover Effective Start Date terkunci | Info | Can only be changed while the status is still Candidate |
| MSG11 | Upload sukses | Info | Saved successfully - Upload completed. … |
| MSG12 | History kosong | Info | No change history for this part yet. |
| MSG13 | Export gagal | Error | Export Excel failed. Please try again. |
| MSG15 | Hover Save, Min MAD kosong / bukan bilangan bulat | Info | Enter Min MAD (whole number, 0 or more) |
| MSG14 | Edit, Max Case/Day < total mapping | Error | Max Case/Day can not be less than the mapped total ({n} case/day) of the ongoing period. Reduce the mapping in Mapping per Destination first. |

Logging message: LOG1 (gagal simpan), LOG2 (gagal export).

## 13. Open points
- Kalimat Effective Start Date yang menggantung di Op Desc 5.4 a.4.
- Akun read-only ([View]) belum didefinisikan.
- Konfirmasi usulan kolom dan retensi TB_H_PART_CANDIDATE (11.4).
- Lokasi template upload; panjang VARCHAR.
