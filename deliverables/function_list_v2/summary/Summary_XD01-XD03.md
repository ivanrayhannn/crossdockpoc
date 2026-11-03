# Summary Proses, Fungsi dan Abnormality – XD01, XD02, XD03

Project: Crossdock Optimization (GTOPAS / NSP) · Author: FID Rayhan · Versi: 0.1 Initial Draft · Sumber: UISS XD01–XD03 (main, 3-Nov-26)

Istilah yang dipakai:

| Istilah | Arti |
|---|---|
| Part List | Data part crossdock (TB_M_PART_CANDIDATE), level part number |
| Mapping per Destination | Pembagian Case/Day per destinasi per periode (TB_M_PART_CANDIDATE_DEST) |
| History | Riwayat perubahan part (TB_H_PART_CANDIDATE), disimpan tanpa batas waktu (tanpa housekeeping) |
| Periode ongoing | Periode kalkulasi terbaru (dibuat XD05 proses 2); periode lalu hanya bisa dilihat |
| Sync Status | No Sync (0) · Waiting (3) · Success (1) · Failed (2) |

---

## XD01 – Cross Dock Part Master Screen

Satu screen dengan 2 tab: **Part List** (user Procurement) dan **Mapping per Destination** (user D/S).

### A. Tab Part List (Procurement)

#### Proses normal

1. **Buka menu**
   - Hanya bisa dibuka user dengan akun Procurement.
   - Default filter: Part Number dan Part Name kosong, Status = All, Sort by = Newer to Older (terbaru di atas), 25 baris per halaman.
   - Kalau belum ada part sama sekali: tabel disembunyikan, tampil msg 2 dengan tombol [Upload Excel] dan [Add one part].
2. **Cari part**
   - Filter Part Number / Part Name (sebagian kata, tidak membedakan huruf besar kecil), Status (Candidate / Active / Inactive); semua filter digabung (AND).
   - Filter diterapkan saat klik [Search] atau Enter; Sort by langsung diterapkan. Search, ganti Sort by atau Rows per page kembali ke halaman 1.
   - Tidak ada hasil: msg 1 dengan [Reset filter].
   - Counter "N parts" dihitung dari seluruh hasil filter. Total Pcs/Day = Pcs/Case × Max Case/Day.
3. **Add part baru** (tombol [Add Part])
   - Status otomatis **Candidate** dan terkunci (part baru selalu Candidate).
   - Yang diinput:
     - Part No: hanya part dari Part Master yang belum terdaftar di Part List.
     - Part Name: terisi otomatis dari Part Master.
     - Min MAD (wajib, bilangan bulat ≥ 0), Pcs/Case (> 0), Max Case/Day (> 0, terkunci sampai Pcs/Case diisi).
     - Effective Start Date: default besok, minimal hari ini.
   - [Save] aktif hanya kalau semua isian wajib terisi; kalau belum, tooltip menampilkan msg 5 / 15 / 6 / 7 untuk isian pertama yang kurang.
   - Setelah Save: part tersimpan dengan status Candidate dan Sync Status **No Sync**, history dicatat (event ADD), modal ditutup, filter direset, part tampil paling atas, msg 9.
4. **Edit part** (link Part Number atau [Edit])
   - Bisa untuk part berstatus Candidate, Active atau Inactive. Part No terkunci.
   - Yang bisa diedit: Min MAD, Pcs/Case, Max Case/Day (Total Pcs/Day dihitung ulang), Status (Candidate / Active / Inactive), Effective Start Date (hanya selama status tersimpan masih Candidate, minimal hari ini; selain itu terkunci dengan tooltip msg 10).
   - Part Active: muncul info **"Mapped Case/Day (current period): n"** (total Case/Day yang sudah di-mapping di periode ongoing; "· no destination yet" kalau belum ada). Max Case/Day tidak boleh di bawah angka ini (msg 14, Save diblok).
   - Setelah Save: data di-update, Sync Status jadi **No Sync**, history dicatat per field yang berubah (event EDIT), part pindah ke atas, msg 9.
5. **History** (ikon jam)
   - Menampilkan riwayat perubahan part, terbaru di atas: judul, waktu, field, nilai lama (dicoret) → nilai baru, user.
   - Isi history: Add / Edit (screen atau upload), perubahan mapping (tambah / ubah / hapus destinasi), hasil Sync, perubahan status oleh XD05.
   - Part tanpa history: msg 12.
6. **Download (Export Excel)** – file `Crossdock_Part_List_YYYYMMDD.xlsx`, 2 sheet:
   - **Part List**: baris sesuai filter dan sort (semua halaman), hanya informasi.
   - **Upload**: semua part terdaftar dengan kolom part_no, min_mad, pcs_case, max_case_day, status, upload = E, effective_start_date. Dipakai sebagai file dasar upload.
7. **Upload part list** ([Upload Excel] → [Validate file], diproses XD02)
   - Pakai sheet **Upload** dari hasil download; sheet lain diabaikan.
   - Kolom upload: **A** = part baru, **E** = edit part yang ada.
   - Aturan status: Candidate tidak bisa diubah lewat upload; Active ↔ Inactive boleh; tidak ada part yang bisa diubah menjadi Candidate.
   - All-or-nothing. Berhasil: msg 11; ditolak: daftar error dari XD02. Part yang berubah jadi No Sync.
8. **DAD Calculation** (XD05 proses 1)
   - Jalan otomatis lewat scheduler (auto retry 3×): bandingkan rata-rata MAD dengan Min MAD, status part jadi Active / Inactive.
   - Header menampilkan "Last DAD calculation"; kalau jadwal dan 3 retry gagal muncul badge "Scheduled run failed 3x" dan [Run calculation] aktif (selain itu nonaktif, tooltip msg 17). Selesai manual: msg 16.
   - Part Active yang berubah jadi Inactive oleh batch otomatis jadi **No Sync** (supaya dihapus di GTOPAS / AP POLE saat Sync).
9. **Sync Status**: setiap Add / Edit / Upload membuat part jadi **No Sync**, supaya dikirim ulang ke GTOPAS dan AP POLE lewat [Sync] di tab Mapping.

### B. Tab Mapping per Destination (D/S)

#### Proses normal

1. **Buka menu**
   - Hanya untuk user dengan akun D/S.
   - Default filter: Calculation period = periode ongoing, Part Number kosong, Sync Status = No Sync.
   - Periode ongoing: semua part **Active** beserta destinasinya; part tanpa destinasi tampil dengan Total Case/Day 0.
   - Periode baru dimulai kosong (mapping periode lalu tidak disalin) sampai diisi XD05 proses 2, Edit mapping atau Upload.
   - Periode lalu: part yang punya data di periode itu, hanya bisa dilihat. "All periods" menampilkan keduanya.
2. **Cari**: filter diterapkan saat [Search]; tidak ada hasil: msg 18.
3. **Kolom hitungan**: Total Case/Day = jumlah Case/Day semua destinasi; Pcs/Day = Pcs/Case × Total; Percentage = Total / Max Case/Day (maksimal 100%).
4. **Lihat detail** (panah di baris): panel destinasi (Destination, Case/Day, Pcs/Day, Percentage), read only.
   - Periode ongoing: tombol [Edit mapping]. Periode lalu: msg 22.
   - Part tanpa destinasi: msg 19.
5. **Edit mapping** (hanya periode ongoing)
   - Tambah destinasi ([Add destination]), ubah Case/Day, hapus destinasi (ikon sampah). Satu destinasi hanya sekali per part.
   - [Split evenly]: Max Case/Day dibagi rata (contoh 24 / 3 = 8 / 8 / 8; 25 / 3 = 9 / 8 / 8).
   - [Save] nonaktif selama: total Case/Day > Max Case/Day (msg 20), part tanpa baris destinasi, atau ada baris tanpa destinasi (msg 21). Total di bawah Max boleh ("{n} case/day left").
   - Disimpan **per destinasi**: Case/Day berubah → update (CREATED tetap), destinasi baru → insert, destinasi dihapus → delete, destinasi sama → tidak disentuh.
   - Part jadi **No Sync**; history dicatat per destinasi yang ditambah / diubah / dihapus (nilai lama dan baru).
   - [Cancel] / tutup panel: perubahan dibuang.
6. **Download (Export Excel)** – `Crossdock_Mapping_per_Destination_<period>_YYYYMMDD.xlsx`, 2 sheet:
   - **Mapping per Destination**: baris sesuai filter, satu baris per destinasi, hanya informasi.
   - **Upload**: part Active periode ongoing, satu baris per destinasi (upload = E) dan satu baris kosong (upload = A) untuk part tanpa mapping. Kosong kalau periode lalu / All periods dipilih.
7. **Upload mapping** ([Upload Excel] → [Validate file], diproses XD03)
   - Hanya untuk periode ongoing (selain itu tombol nonaktif, tooltip msg 23).
   - Pakai sheet **Upload** hasil download. Part di file disimpan per destinasi; part yang tidak ada di file tidak berubah.
   - All-or-nothing. Berhasil: msg 24; ditolak: daftar error dari XD03. Part yang berubah jadi No Sync.
8. **Mapping Calculation** (XD05 proses 2)
   - Jalan otomatis lewat scheduler (auto retry 3×): membuat periode baru beserta mapping destinasinya.
   - [Run calculation] aktif hanya kalau jadwal dan 3 retry gagal (selain itu tooltip msg 30). Selesai manual: msg 29.
9. **Sync** ([Sync (n)], on demand)
   - Yang dikirim: semua part **Active** periode ongoing dan part yang **baru jadi Inactive**, dengan Sync Status No Sync atau Failed, tanpa melihat filter (n = jumlahnya). Part Candidate tidak pernah di-sync.
   - Part jadi **Waiting**, satu baris status per part per sistem tujuan (GTOPAS, AP POLE), lalu XD06 dan XD07 dijalankan. Msg 27.
   - **GTOPAS (XD06, RPA)** – menu Supply > Master > Crossdock Master, search Part No (satu row per part + destinasi):
     - destinasi di NSP belum ada di GTOPAS → didaftarkan;
     - destinasi ada di keduanya → dibiarkan (GTOPAS tidak menyimpan Case/Day);
     - destinasi ada di GTOPAS tapi tidak di NSP → dihapus;
     - part Inactive atau part Active tanpa destinasi → semua row-nya dihapus.
   - **AP POLE (XD07, file SFTP)** – Cross Dock Kanban Part Master (satu row per part number), diproses receive IF TMA:
     - part baru (belum ada) → Add (Part No, Pcs/Case, Max Case/Day) lalu destinasi + Case/Day;
     - part sudah ada → Edit: Pcs/Case, Max Case/Day dan destinasi + Case/Day disamakan;
     - part Inactive (CROSSDOCK_FLAG N) → part dihapus.
   - Hasil akhir per part: **Success** kalau keduanya berhasil; **Failed** kalau salah satu gagal (alasan di tooltip msg 28, dikirim ulang di Sync berikutnya); **No Sync** kalau part diubah lagi saat proses kirim. Setiap hasil dicatat di history (event SYNC).

### C. Abnormality XD01

| No | Kondisi | Deteksi / pesan | Penanganan sistem | Tindakan user |
|---|---|---|---|---|
| 1 | Part sudah didaftarkan user lain saat Add | msg 3 | Simpan dibatalkan | Tutup modal, cari part |
| 2 | Data part diubah user lain saat Edit | msg 4 | Simpan dibatalkan | Refresh, edit ulang |
| 3 | Mapping diubah user lain saat Edit mapping | msg 25 | Simpan dibatalkan | Cancel, refresh, edit ulang |
| 4 | Max Case/Day di bawah total mapping periode ongoing | msg 14 | Save diblok (cek juga di server) | Kurangi mapping dulu di tab Mapping |
| 5 | Total Case/Day melebihi Max Case/Day | msg 20 | Save diblok | Kurangi Case/Day salah satu destinasi |
| 6 | Baris mapping tanpa destinasi / part tanpa destinasi | msg 21 | Save diblok | Pilih destinasi atau hapus baris |
| 7 | Gagal simpan ke database | LOG1 (part), LOG3 (mapping) | Rollback, pesan error di layar | Hubungi PIC |
| 8 | Export Excel gagal | msg 13 / LOG2 (Part List), msg 26 / LOG5 (Mapping) | File tidak dibuat | Coba lagi; hubungi admin kalau berulang |
| 9 | Upload ditolak | Daftar error (XD02 / XD03) | Tidak ada data yang disimpan | Perbaiki sheet Re-upload, upload ulang |
| 10 | Sync gagal di GTOPAS / AP POLE | Status Failed, msg 28 (LOG4; detail di XD06 / XD07) | Part tetap Failed, ikut di n berikutnya | Perbaiki penyebab, klik [Sync] lagi |
| 11 | Scheduler DAD / Mapping Calculation gagal 3× | Badge "Scheduled run failed 3x" | [Run calculation] aktif | Cek penyebab, klik [Run calculation] |

---

## XD02 – Cross Dock Part Master Upload Batch

Batch yang jalan saat Procurement klik [Validate file] di Upload Excel tab Part List (XD01).

### Proses normal

1. **Terima file** yang di-upload user.
2. **Cek file**
   - Format .xlsx, maksimal 5 MB, 1–5.000 baris data.
   - Sheet "Upload" harus ada; sheet lain diabaikan.
   - 7 kolom template: part_no, min_mad, pcs_case, max_case_day, status, upload, effective_start_date (kolom tambahan diabaikan).
3. **Cek setiap baris** – semua error dikumpulkan sekaligus supaya user cukup memperbaiki file satu kali:

   | No | Aturan |
   |---|---|
   | 1 | Kolom upload = A (Add) atau E (Edit) |
   | 2 | Part No ada di Part Master |
   | 3 | A: part belum terdaftar di Part List · E: part sudah terdaftar |
   | 4 | Part No hanya sekali di file |
   | 5 | Min MAD bilangan bulat ≥ 0; Pcs/Case dan Max Case/Day bilangan bulat > 0; ketiganya wajib |
   | 6 | Status: A harus kosong (part baru selalu Candidate); E: Candidate tetap Candidate, Active ↔ Inactive boleh, tidak boleh diubah jadi Candidate |
   | 7 | Effective Start Date wajib untuk part Candidate (selalu untuk A), minimal hari ini kalau baru / berubah |
   | 8 | E: Effective Start Date hanya boleh berubah selama part masih Candidate |
   | 9 | E: Max Case/Day tidak boleh di bawah total Case/Day yang sudah di-mapping di periode ongoing (contoh mapping 100, Max baru 80 → ditolak) |

4. **Simpan** (hanya kalau semua baris valid – all-or-nothing)
   - **A**: part baru disimpan sebagai Candidate; Part Name dari Part Master; Total Pcs/Day = Pcs/Case × Max Case/Day.
   - **E**: nilai yang berubah di-update (termasuk Active ↔ Inactive); baris tanpa perubahan dilewati.
   - Semua part yang tersimpan jadi **No Sync**; history dicatat per field yang berubah (event ADD / EDIT, source UPLOAD, nomor upload).
   - Part yang tidak ada di file tidak berubah.
5. **Hasil**: result report (.xlsx, sheet Summary, Result, Re-upload, Changes) dibuat untuk berhasil maupun ditolak; upload log mencatat status COMPLETED / REJECTED dan jumlah baris (total, tersimpan, tanpa perubahan, error).

### Abnormality XD02

| No | Kondisi | Log | Penanganan sistem | Tindakan user |
|---|---|---|---|---|
| 1 | File upload tidak ditemukan | LOG3 | Batch berhenti | Upload ulang |
| 2 | File tidak valid (format, ukuran, jumlah baris, sheet Upload, kolom template) | LOG4 | REJECTED, result report dibuat | Download ulang template, upload lagi |
| 3 | Baris tidak valid (aturan 1–9) | LOG5 | Seluruh file ditolak, tidak ada yang disimpan | Perbaiki baris di sheet Re-upload, upload ulang |
| 4 | Baris E tanpa perubahan | LOG6 (info) | Baris dilewati | – |
| 5 | Gagal simpan ke database | LOG7 | Rollback, REJECTED | Hubungi PIC |
| 6 | Result report gagal dibuat | LOG8 (warning) | Data tetap tersimpan, path report kosong | Hubungi system owner |
| 7 | Error sistem lain | LOG9 | Rollback, REJECTED | Hubungi PIC |

---

## XD03 – Part and Destination Mapping Upload Batch

Batch yang jalan saat D/S klik [Validate file] di Upload Excel tab Mapping per Destination (XD01).

### Proses normal

1. **Terima file** – hanya untuk **periode ongoing** (tombol upload nonaktif untuk periode lalu).
2. **Cek file**
   - Format .xlsx, maksimal 5 MB, 1–5.000 baris data, sheet "Upload" ada (sheet lain diabaikan).
   - 5 kolom template: part_no, dest_code, case_day, upload, total_case_day (total_case_day hanya referensi, tidak dibaca).
   - Satu baris per part × destinasi; semua baris satu part = mapping baru part itu.
3. **Cek setiap baris** – semua error dikumpulkan sekaligus (aturan 4 dan 6 dicek per part):

   | No | Aturan |
   |---|---|
   | 1 | Part terdaftar di Part List dan statusnya Active |
   | 2 | Kode destinasi ada di Destination Master |
   | 3 | case_day bilangan bulat > 0 kalau dest_code terisi |
   | 4 | Satu destinasi hanya sekali per part |
   | 5 | dest_code dan case_day terisi dua-duanya atau kosong dua-duanya (baris placeholder) |
   | 6 | Total case_day per part ≤ Max Case/Day part (di bawah boleh) |
   | 7 | Hanya untuk periode ongoing |
   | 8 | Kolom upload: A untuk destinasi yang belum di-mapping, E untuk destinasi yang sudah di-mapping; placeholder kosong dilewati |

4. **Simpan** (hanya kalau semua baris valid – all-or-nothing)
   - Setiap part dibandingkan dengan mapping sekarang; part tanpa perubahan dilewati (Sync Status dan last update tetap).
   - Part yang berubah disimpan **per destinasi** (key part + periode + destinasi):
     - Case/Day berubah → update (CREATED_BY / CREATED_DT tetap);
     - destinasi baru di file → insert;
     - destinasi yang tidak ada lagi di file → delete;
     - destinasi dengan Case/Day sama → tidak disentuh.
   - Part yang semua barisnya kosong (placeholder) tidak diubah: mapping tidak bisa dihapus total lewat upload (minimal 1 destinasi, sama seperti di layar).
   - Part yang berubah jadi **No Sync**; history dicatat per destinasi yang ditambah / diubah / dihapus (event MAPPING, source UPLOAD).
   - Part yang tidak ada di file tidak berubah.
5. **Hasil**: result report (.xlsx) dibuat untuk berhasil maupun ditolak; upload log mencatat COMPLETED / REJECTED dan jumlahnya.

Contoh: PART-A di DB D01 = 10, D02 = 5; file berisi D01 = 8, D03 = 7 → D01 di-update jadi 8, D03 di-insert, D02 di-delete; history 3 record; PART-A jadi No Sync.

### Abnormality XD03

| No | Kondisi | Log | Penanganan sistem | Tindakan user |
|---|---|---|---|---|
| 1 | File upload tidak ditemukan | LOG3 | Batch berhenti | Upload ulang |
| 2 | File tidak valid (format, ukuran, jumlah baris, sheet Upload, kolom template) | LOG4 | REJECTED, result report dibuat | Download ulang, upload lagi |
| 3 | Baris tidak valid (aturan 1–8) | LOG5 | Seluruh file ditolak, tidak ada yang disimpan | Perbaiki sheet Re-upload, upload ulang |
| 4 | Part tanpa perubahan / semua baris kosong | LOG6 (info) | Part dilewati | – |
| 5 | Gagal simpan mapping atau status part | LOG7 | Rollback, REJECTED | Hubungi PIC |
| 6 | Result report gagal dibuat | LOG8 (warning) | Data tetap tersimpan | Hubungi system owner |
| 7 | Error sistem lain | LOG9 | Rollback, REJECTED | Hubungi PIC |

---

## Catatan terbuka (dari review)

| No | Catatan |
|---|---|
| FB-119 / FB-120 | Judul 4.1 / 4.2 di UISS XD02 dan XD03 menyebut "log message no. 5 / 6"; yang benar LOG4 (file check) dan LOG5 (row validation) – belum diperbaiki |
| FB-128 | Bagian Tables UISS XD03 menulis TB_M_PART_CANDIDATE dan TB_M_PART_CANDIDATE_DEST sebagai "existing"; seharusnya tabel baru Crossdock – belum diperbaiki |
