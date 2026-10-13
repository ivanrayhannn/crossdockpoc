# Screen – Crossdock Master Setting – Mapping per Destination

Ringkasan poin-poin layar Mapping per Destination: akses, kriteria, panel mapping, aturan Save, Sync via RPA, Upload / Export, pesan, dan **semua tabel yang terlibat**.
Sumber: UISS-Screen `UISS_Screen_MappingPerDestination.xlsx` (0.1 Initial Draft) dan keputusan bisnis sampai 13-Oct-26.
Screen ID: **TBD** (usulan X3).

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

- Semua kriteria digabung **AND**. Tidak ada hasil → pesan no. 1.
- **Periode berjalan**: semua part **Active** dari TB_M_PART_CANDIDATE + destinasinya (part tanpa destinasi tampil dengan Total Case/Day 0).
- **Periode lalu**: semua part yang punya baris di TB_M_PART_CANDIDATE_DEST untuk periode itu, apa pun statusnya sekarang. All periods = keduanya.
- Default No Sync → part Success / Failed tersembunyi sampai filter diubah.
- Tabel scroll di dalam section (tanpa paging). **TBD**: perlu paging?; filter saat mengetik vs [Search]; cara periode dibuat.

## 4. Result list
| Kolom | Keterangan |
|---|---|
| Period | Periode kalkulasi baris |
| Expand (panah) | Buka / tutup panel Destination Mapping |
| Part Number, Part Name, Pcs/Case | Dari TB_M_PART_CANDIDATE |
| Total Case/Day | Jumlah CASE_DAY semua destinasi part + periode |
| Pcs/Day | Pcs/Case × Total Case/Day |
| Percentage | Total Case/Day / Max Case/Day (**TBD**: data lama > 100%) |
| Sync Status | 0 No Sync (abu), 3 Waiting (kuning), 1 Success (hijau), 2 Failed (merah, tooltip SYNC_MESSAGE) |

Tombol di atas tabel: **[Sync (n)]**, **[Upload Excel]**, **[Export Excel]**.

## 5. Panel Destination Mapping
- Chip alokasi: merah (total > Max), abu (total < Max), hijau (sama).
- Catatan: "no destination yet" / "{n} case/day over" / "{n} case/day left" / "capacity fully allocated".
- Kolom: Destination (CD), Case/Day, Pcs/Day (= Pcs/Case × Case/Day), Percentage (= Case/Day / total Case/Day part).
- Periode berjalan → [Edit mapping]. Periode lalu → badge "Past period - read only" (pesan no. 5).
- Part tanpa destinasi → pesan no. 2.

## 6. Edit mapping & aturan Save
1. Klik [Edit mapping] → draft; Destination & Case/Day bisa diubah, ikon trash per baris, [Add destination].
2. Daftar Destination menyembunyikan destinasi yang sudah dipakai baris lain part yang sama (**satu destinasi sekali per part**).
3. [Add destination] → baris baru "Select destination", Case/Day 0.
4. [Split evenly] (> 1 baris): floor(Max Case/Day / jumlah baris), sisa +1 per baris dari baris pertama. Contoh 24/3 = 8/8/8; 25/3 = 9/8/8.
5. **[Save] disabled** kalau:
   - total Case/Day **>** Max Case/Day (pesan no. 3);
   - part tidak punya baris destinasi; atau
   - ada baris tanpa destinasi (pesan no. 4) — **ditolak, tidak bisa disimpan**.
   - Total **≤** Max Case/Day **boleh** (kurang ditampilkan "{n} case/day left").
6. Klik [Save]:
   - Mapping diubah user lain sejak edit dimulai → pesan no. 8, stop.
   - **Replace** baris part + periode berjalan di TB_M_PART_CANDIDATE_DEST dengan isi draft.
   - TB_M_PART_CANDIDATE: **SYNC_STATUS = 0 (No Sync)**.
   - TB_H_PART_CANDIDATE: satu record per destinasi yang ditambah / diubah / dihapus (event **MAPPING**, source **SCREEN**).
   - Keluar edit mode.
7. [Cancel] / tutup panel → draft dibuang.

## 7. Sync (via RPA)
1. Klik **[Sync (n)]** (on demand). n = semua part **Active** periode berjalan dengan Sync Status **No Sync atau Failed**, **tidak tergantung filter**. Disabled kalau n = 0.
2. Part tersebut → **SYNC_STATUS = 3 (Waiting)**, fungsi RPA dijalankan, pesan no. 10.
3. RPA per part Waiting: baca PCS_CASE, MAX_CASE_DAY + semua destinasi & CASE_DAY periode berjalan → **replace** di global system sebagai satu paket → tulis balik SYNC_STATUS 1 / 2, SYNC_DT, SYNC_MESSAGE.
4. Part diubah setelah dibaca RPA (CHANGED_DT beda) → SYNC_STATUS = 0, bukan Success.
5. Setiap hasil dicatat di **TB_H_PART_CANDIDATE** (event **SYNC**, source **RPA**).
6. Part Failed: tooltip pesan no. 11, ikut lagi di Sync berikutnya. Candidate / Inactive tidak pernah di-sync.
Detail: `BATCH_RPA_Sync.md`.

## 8. Upload Excel
- Aktif **hanya** kalau periode berjalan dipilih; periode lalu / All periods → disabled, tooltip pesan no. 6.
- Kolom template: part_no, dest_code, case_day, total_case_day (referensi). File .xlsx, max 5 MB, max 5.000 baris.
- Base file: sheet **Upload** dari Export Excel (periode berjalan). Part di file → seluruh mapping di-replace; part yang tidak ada di file tidak berubah.
- [Validate file] = tombol simpan upload → batch Mapping per Destination Upload (all-or-nothing, Log). Detail: `BATCH_Mapping_Upload.md`.
- Sukses → tutup modal, pesan no. 7. Ditolak → hasil batch (daftar error). Part yang berubah → No Sync.

## 9. Export Excel
File `Crossdock_Mapping_per_Destination_<period>_YYYYMMDD.xlsx` (<period> mis. Sep_2026 / All_periods):
| Sheet | Isi |
|---|---|
| Mapping per Destination | Baris filter aktif, 1 baris per destinasi (part tanpa destinasi = 1 baris kosong): Period, Part Number, Part Name, Pcs/Case, Total Case/Day, Pcs/Day, Percentage, Sync Status, Destination Code, Destination, Dest Case/Day, Dest Pcs/Day, Dest Percentage. Informasi saja |
| Upload | Semua part Active periode berjalan: part_no, dest_code, case_day, total_case_day (= Max Case/Day); 1 baris per destinasi, part tanpa mapping = 1 baris placeholder. Kosong untuk periode lalu / All periods |

Gagal dibuat → pesan no. 9.

---

## 10. Tabel yang terlibat

### 10.1 TB_M_PART_CANDIDATE_DEST — *dibaca & ditulis* (level part number + periode + destinasi)
| Kolom | PK | Keterangan | Saat Save mapping |
|---|---|---|---|
| PART_NO | Y | FK ke TB_M_PART_CANDIDATE | Part yang diedit |
| PERIOD | Y | Periode kalkulasi (format TBD) | Periode berjalan |
| DEST_CODE | Y | Kode destinasi (master TBD) | Dari draft |
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

### 10.3 Destination master — *dibaca*
Nama tabel **TBD**. Isi diketahui: 123 Thailand, 456 Japan, 789 Vietnam.

### 10.4 TB_H_PART_CANDIDATE — *ditulis* (history)
Tabel history semua perubahan part. Kolom fisik **belum ditentukan (TBD)**; field logis: PART_NO, PERIOD, EVENT, SOURCE, FIELD_NAME, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGED_DT (satu record per field yang berubah).

| Event | Source | Kapan | Contoh FIELD_NAME / nilai |
|---|---|---|---|
| ADD | SCREEN / UPLOAD | Part baru (Add Part di layar / flag A) | PCS_CASE, MAX_CASE_DAY, … (OLD kosong) |
| EDIT | SCREEN / UPLOAD | Ubah data part (Edit di layar / flag E) | PCS_CASE, MAX_CASE_DAY, PART_STATUS, MAD, EFFECTIVE_START_DATE |
| MAPPING | SCREEN / UPLOAD | Tambah / ubah / hapus destinasi (periode berjalan) | Kode destinasi; OLD/NEW = Case/Day |
| SYNC | RPA | Hasil Sync | SYNC_STATUS: Waiting → Success / Failed + pesan |

Di layar ini: event **MAPPING** source **SCREEN** saat Save (PERIOD = periode berjalan, FIELD_NAME = kode destinasi, OLD/NEW = Case/Day; hapus destinasi = NEW kosong), dan event **SYNC** source **RPA** dari hasil Sync. Dibaca di modal History setting Part List.

### 10.5 Tabel terkait
- **Log** – upload log, ditulis batch Mapping per Destination Upload.
- **Global system TMMIN** – tujuan RPA (tanpa interface).

---

## 11. Pesan layar (MSG ID TBD)
| No | Kapan | Tipe | Pesan |
|---|---|---|---|
| 1 | Filter tanpa hasil | Info | No parts match these filters - Change the period or sync status, or press Reset to show all parts. |
| 2 | Part tanpa destinasi | Info | No destination yet - Click Edit mapping and add at least one destination … |
| 3 | Total > Max Case/Day | Error | Allocation of {n} case/day exceeds Max Case/Day ({m}). Reduce one of the destinations. |
| 4 | Baris tanpa destinasi | Error | Select a destination for every row, or remove the empty row, before saving. |
| 5 | Panel periode lalu | Info | Past period - read only |
| 6 | Hover Upload disabled | Info | Past period - read only. Select the ongoing period to upload. |
| 7 | Upload sukses | Info | Saved successfully - Upload completed. … |
| 8 | Save, diubah user lain | Error | Error in Update because of concurrency check. |
| 9 | Export gagal | Error | Export Excel failed. Please try again. |
| 10 | Klik Sync | Info | Sync requested for {n} part(s). They stay Waiting until the RPA has sent them to the global system. |
| 11 | Hover chip Failed | Info | Sync failed: {SYNC_MESSAGE}. The part is sent again with the next Sync. |

## 12. Open points
- Screen ID final dan penomoran MSG ID.
- Nama tabel destination master; format PERIOD dan cara periode dibuat.
- Tampilan Percentage untuk data lama > 100%.
- Paging untuk data besar; filter saat mengetik vs [Search].
- Detail fungsi RPA; batas waktu status Waiting.
- Kolom fisik dan retensi TB_H_PART_CANDIDATE.
