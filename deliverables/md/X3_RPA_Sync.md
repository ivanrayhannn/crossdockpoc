# Batch / RPA – Crossdock Master Setting – Sync ke Global System

Ringkasan poin-poin fungsi Sync lewat **RPA**: pemicu, data yang dikirim, status, write-back, dan **semua tabel yang terlibat**.
Sumber: UISS-Screen `X3_UISS_Screen_MappingPerDestination.xlsx` (Operation Description 5.6, Data Map) dan keputusan bisnis 13-Oct-26.
Belum ada UISS-Batch tersendiri untuk RPA ini (**TBD**).

---

## 1. Latar belakang
- Global system TMMIN **tidak punya interface**, sehingga data dimasukkan oleh **RPA** (robot) yang membaca 2 tabel NSP.
- Data yang dikirim per part: **Pcs/Case**, **Max Case/Day**, dan **mapping destinasi** (Case/Day per destinasi) periode berjalan.
- Perubahan bisa terjadi di mapping, mis. Japan naik → Thailand turun. Karena itu part dikirim **sebagai satu paket** supaya global system tidak pernah menerima data setengah jadi.

## 2. Pemicu
- **On demand**: user D/S klik **[Sync (n)]** di sub-menu Mapping per Destination.
- n = jumlah part **Active** periode berjalan dengan Sync Status **No Sync** atau **Failed**, **tidak tergantung filter** di layar.
- Part **Candidate** dan **Inactive** tidak pernah di-sync.

## 3. Status Sync (TB_M_PART_CANDIDATE.SYNC_STATUS)
| Nilai | Status | Arti | Diset oleh |
|---|---|---|---|
| 0 | No Sync | Belum dikirim / berubah sejak sync terakhir | Save Part List, Save mapping, Upload |
| 3 | Waiting | Sudah klik [Sync], menunggu RPA | Layar (klik Sync) |
| 1 | Success | RPA berhasil mengirim | RPA |
| 2 | Failed | RPA gagal; alasan di SYNC_MESSAGE; ikut lagi di [Sync] berikutnya | RPA |

Disimpan **per part** di TB_M_PART_CANDIDATE karena RPA mengirim part sebagai satu set. Riwayat (termasuk periode) dicatat di tabel history **TB_H_PART_CANDIDATE** (event SYNC).

## 4. Alur
1. User klik [Sync (n)] → semua part target diset **SYNC_STATUS = 3 (Waiting)**, fungsi RPA dijalankan. Pesan: "Sync requested for {n} part(s)…".
2. RPA, untuk setiap part Waiting:
   1. Baca **PCS_CASE, MAX_CASE_DAY** dari TB_M_PART_CANDIDATE.
   2. Baca **semua destinasi + CASE_DAY periode berjalan** dari TB_M_PART_CANDIDATE_DEST.
   3. **Replace** data part di global system dengan set lengkap ini (destinasi yang dihapus ikut terhapus).
   4. Tulis balik ke TB_M_PART_CANDIDATE: SYNC_STATUS = 1 / 2, SYNC_DT, SYNC_MESSAGE.
   5. Kalau part **diubah setelah dibaca RPA** (CHANGED_DT berbeda) → SYNC_STATUS = **0** (bukan Success), supaya data terbaru terkirim di Sync berikutnya.
   6. Catat ke **TB_H_PART_CANDIDATE**: event SYNC, source RPA, periode, waktu, hasil dan pesan.
3. Part Failed menampilkan SYNC_MESSAGE sebagai tooltip di chip status, dan ikut lagi di [Sync] berikutnya.
4. Save di Part List / Mapping saat part masih Waiting → kembali No Sync (hasil RPA untuk data lama tidak dianggap Success).

---

## 5. Tabel yang terlibat

### 5.1 TB_M_PART_CANDIDATE — *dibaca & diupdate*
| Kolom | Peran di Sync |
|---|---|
| PART_NO (PK) | Key part |
| PART_STATUS | Filter: hanya **Active** |
| PCS_CASE | **Dikirim** ke global system |
| MAX_CASE_DAY | **Dikirim** ke global system |
| SYNC_STATUS | 0 → 3 saat klik Sync; 3 → 1/2 (atau 0) oleh RPA |
| SYNC_DT | Diisi RPA: waktu hasil |
| SYNC_MESSAGE | Diisi RPA: alasan Failed (kosong kalau Success) |
| CHANGED_DT | Dibandingkan RPA untuk deteksi perubahan selama proses |

Kolom lain (lihat `X2_BATCH_PartList_Upload.md` 8.1): PART_NAME, MIN_MAD, TOTAL_PCS_DAY, EFFECTIVE_START_DATE, LAST_SOURCE, LAST_UPLOAD_ID, audit — tidak disentuh Sync.

### 5.2 TB_M_PART_CANDIDATE_DEST — *dibaca*
| Kolom | Peran di Sync |
|---|---|
| PART_NO | Part yang di-sync |
| PERIOD | Hanya **periode berjalan** |
| DEST_CODE | **Dikirim** (destinasi) |
| CASE_DAY | **Dikirim** (Case/Day destinasi) |

### 5.3 TB_H_PART_CANDIDATE — *ditulis oleh RPA* (history)
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

Dibaca oleh modal *History setting* di Part List.

Di Sync: event **SYNC**, source **RPA**, PERIOD = periode berjalan, FIELD_NAME = SYNC_STATUS, OLD = Waiting, NEW = Success / Failed / No Sync, REMARK = SYNC_MESSAGE, CREATED_BY = user ID RPA. (Menggantikan "Sync log" yang terpisah.)

### 5.4 Global system TMMIN — *tujuan*
Diakses lewat RPA (tanpa interface). Layar/field yang diisi RPA: **TBD**.

### 5.5 Tabel lain yang **tidak** dipakai Sync
- Log upload (hanya untuk proses upload).

---

## 6. Pesan
| Kapan | Tipe | Pesan |
|---|---|---|
| Klik [Sync] | Info | Sync requested for {n} part(s). They stay Waiting until the RPA has sent them to the global system. |
| Hover chip Failed | Info | Sync failed: {SYNC_MESSAGE}. The part is sent again with the next Sync. |
| RPA gagal per part (logging) | Error | Sync of part <PART_NO> failed: <SYNC_MESSAGE>. |

## 7. Open points
- Detail fungsi RPA: layar global system, urutan input, waktu proses, perilaku kalau RPA tidak tersedia / timeout.
- Konfirmasi usulan kolom dan retensi TB_H_PART_CANDIDATE; user ID yang dipakai RPA (CREATED_BY).
- Perlu UISS-Batch tersendiri untuk RPA function?
- Apakah status Waiting perlu batas waktu (mis. kembali ke Failed kalau RPA tidak merespons).
