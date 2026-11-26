# Crossdock Optimization – History dan Business Process

Dokumentasi project Crossdock, dari prototype pertama (17-Sep-2026) sampai desain sync terbaru (23-Nov-2026).
Isinya: ringkasan project, function list, riwayat keputusan per fase, evolusi desain sync, dan alur bisnis step by step sesuai desain sekarang.

Sumber: riwayat git repo ini (310 commit), `deliverables/function_list_v2/README.md`, UISS XD01–XD15, BPF Level 2, Function Summary, dan simulasi di `deliverables/function_list_v2/erd/proposal_staging_sync/simulation`.

---

## 1. Ringkasan project

**Tujuan.** Mengatur part crossdock: part dari supplier yang langsung diteruskan ke destinasi ekspor tanpa disimpan di gudang. Ada dua bagian besar:
1. **Crossdock Master.** Daftar part crossdock, kapasitas per hari (Max Case/Day), dan pembagian kapasitas per destinasi. Master ini dikirim ke GTOPAS dan AP POLE.
2. **ASN Crossdock.** Supplier membuat ASN dari customer order crossdock yang sudah punya PO, per case, dengan aturan urutan dan hold.

**Sistem**

| Sistem | Peran |
|---|---|
| NSP (Supplier System) | Sistem baru tempat semua fungsi XD dibangun |
| GTOPAS (G-System) | Sumber customer order (H0253), destination master (H0125), actual demand; menerima Crossdock Master (layar WVJA5204) lewat RPA |
| DB Surrounding | Replika data GTOPAS yang dibaca batch NSP |
| AP POLE | Menerima Cross Dock Kanban Part Master (LLM9Q910) dan Export Customer Cross Dock Master (LLM9Q880) lewat RPA upload |
| Power Automate | Parent flow RPA (cloud) dan child flow (desktop) XD06 / XD07, email notifikasi |

Nama di dokumen: **GTOPAS** dan **NSP**. Di prototype web dan simulasi: G-System dan Supplier System.

**Pengguna**

| Peran | Pekerjaan |
|---|---|
| Procurement | Kanban Crossdock Master: daftar part, Min MAD, Pcs/Case, Max Case/Day, status |
| D/S Team | Export Crossdock Master: mapping per destinasi, [Sync]; hold di ASN; Change Order Number |
| Supplier | Membuat dan submit ASN crossdock |
| Batch NSP | Sync data GTOPAS, kalkulasi DAD, kirim master lewat RPA |

**Deliverables utama**

| Deliverable | Lokasi |
|---|---|
| Prototype web (React, GitHub Pages) | `app/` |
| UISS XD01–XD15 (Excel) | `deliverables/function_list_v2/uiss/` (spec JSON + builder di `specs/`) |
| UISS dalam Markdown untuk coding | `prepare_code/` |
| User Requirement XD01 | `deliverables/function_list_v2/ur/` |
| UR & Business Logic Summary | `deliverables/function_list_v2/XD01-XD13_UR_Business_Logic_Summary.xlsx` |
| Business Process Flow Level 2 | `deliverables/function_list_v2/bpf/` |
| Concept ERD dan DB Structure | `deliverables/function_list_v2/erd/` |
| Function Summary (review per poin) | `deliverables/function_list_v2/summary/Function_Summary.html` |
| Simulasi ASN | `deliverables/simulasi_asn_rev.xlsx` |
| Simulasi staging dan RPA | `deliverables/function_list_v2/erd/proposal_staging_sync/simulation/` |
| User guide GTOPAS / AP POLE / download | `deliverables/user_guide/` |
| CR ASN existing (ASN03 / ASN04) | `deliverables/asn_existing/` |

---

## 2. Function list (sekarang)

| ID | Function | Tipe | Trigger |
|---|---|---|---|
| XD01 | Cross Dock Part Master Screen (tab Kanban Crossdock Master dan Export Crossdock Master) | Screen | User |
| XD02 | Cross Dock Part Master Upload Batch | Batch | [Validate file] di XD01 |
| XD03 | Part and Destination Mapping Upload Batch | Batch | [Validate file] di XD01 |
| XD04 | Actual Demand Summary Synch to NSP | Batch | Bulanan, retry 3× |
| XD05 | DAD Volume Calculation Batch (proses 1 status, proses 2 mapping, proses 3 Period Rollover) | Batch | Trigger data baru, tanggal D; rollover tanggal 1 |
| XD06 | IF Cross Dock Master to GTOPAS (RPA) | Batch (RPA) | Parent flow |
| XD07 | RPA Cross Dock Master to AP POLE | Batch (RPA) | Parent flow |
| XD08 | Order Control Information to NSP (H0253) | Batch | Harian 27:30, retry 3× |
| XD09 | Mapping Customer Order and PO Batch | Batch | [Search] di XD10 |
| XD10 | ASN Cross Dock Creation Screen (termasuk Submit ASN 5.7) | Screen | Supplier / D/S |
| XD11 | Change Order Number Screen | Screen | D/S |
| XD13 | Destination Master Synch into NSP (H0125) | Batch | Mingguan 21:30, retry 3× |

Tidak dipakai: X9 H0202 Demand History Sync, X15 Menu Settings, XD12 (digabung ke XD08 pada 23-Oct), XD14, XD15 ASN Crossdock Inquiry (9-Nov).

---

## 3. Riwayat per fase

### Fase 1 · 17–30 Sep · Prototype awal
- 17-Sep: prototype **Crossdock Master Setting** (Part List, Mapping per Destinasi), deploy GitHub Pages.
- 29-Sep: **Case Consolidation Simulation** dan **ASN Creation** di prototype (delivery plan, pemilihan case oleh supplier).
- 30-Sep: status part **Candidate** dengan Effective Date terkunci; status sync GTOPAS/AP POLE digabung jadi satu (lalu tiga status); combobox Part No.

### Fase 2 · 2–12 Oct · FSD dan UISS pertama
- 2-Oct: FSD Crossdock Master Setting dengan screenshot per state; UI ke Bahasa Inggris.
- 5-Oct: 1 ASN = 1 Customer Order Date; delivery plan dikelompokkan per Customer Order Date; draft UISS Delivery Plan / ASN Draft.
- 8–9-Oct: simulasi Candidate Part Batch Flow; UISS-Batch upload Part List dan Mapping. **Keputusan D5: upload ditolak kalau Max Case/Day di bawah total mapping.**
- 12-Oct: keputusan bisnis (FSD v0.3); kolom Status di template upload (Candidate tidak bisa diubah lewat upload); tabel **TB_M_PART_CANDIDATE / TB_M_PART_CANDIDATE_DEST**; nama project **Crossdock Optimization**, author FID Rayhan.

### Fase 3 · 13–16 Oct · Tabel, kalkulasi, alur ASN
- 13-Oct: sync lewat RPA (status Waiting); history **TB_H_PART_CANDIDATE** untuk semua perubahan; Min MAD wajib; PERIOD format **YYYYMM**; period kalkulasi dibuat batch dan dimulai tanpa mapping.
- 14-Oct: aturan kalkulasi dikonfirmasi: pembagi bulan tetap, top-N destinasi sejumlah Max Case/Day, kode destinasi 7 digit, mapping punya scheduler sendiri. Penomoran fungsi X1–X15; replikasi H0202, H0253 (SERIAL_NO bagian key) dan H0125; prototype ASN Crossdock Creation dan ASN Inquiry.
- 15-Oct: alur ASN: Get Order (X12, pre-mapping on demand), Hold Flag oleh D/S, Create ASN dengan mapping, Submit ASN sebagai batch X14 dengan Submit ID.
- 16-Oct: konfirmasi 1–9 ASN (aturan supplier / plant, D/S super admin, **TB_R_INSTRUCTION**, tabel ASN existing); simulasi cancel order.

### Fase 4 · 18–23 Oct · Function list v2 (XD01–XD15)
- 18-Oct: **function list v2** dengan prefix XD. XD01 = gabungan Part List + Mapping; XD05 = gabungan kalkulasi status + mapping; XD10 = ASN + Submit. XD07 ke AP POLE lewat file SFTP (Option #3); H0253 satu tabel upsert.
- 19-Oct: jawaban **Confirmation Points**: case dipecah per destinasi sesuai pcs/case, unit utuh per Part Number + Customer Order Date, 1 case label = 1 case 1 destinasi, jadwal XD08/XD13 27:30, Effective Start Date default besok. BPF Level 2 (PIC × timeline, tabel, abnormality).
- 20-Oct: **Concept ERD** dan DB Structure; PO crossdock dari Pra Daily Order (manifest CROSS_DOCK_FLAG X).
- 21-Oct: **urutan H0253 = urutan alokasi GTOPAS**; case supplier per PCS_CASE; **blok ASN di titik potong valid (CUT_FLAG)**, check box per case.
- 23-Oct: **UPD_STATUS** (6 received / 2 cancel); **XD08 satu batch H0253** (XD12 digabung) yang melepas semua draft; **XD11 Change Order Number** menggantikan cancel batch; riwayat TB_H_CROSSDOCK_ORDER_CHANGE.

### Fase 5 · 25–27 Oct · Simulasi ASN dan dokumen bisnis
- 25–26-Oct: `simulasi_asn_rev.xlsx` (PART-X, 16–22 Oct): 1 PO per order date, short PO, serial split (1 line di 2 ASN), Customer Order Date tertua dulu tanpa loncat. **Business Logic ASN** masuk UISS XD09 4.0 / XD10 5.0.
- 27-Oct: dokumen ASN mengikuti simulasi; BPF F2 (customer order D-2, PO D-1); kolom upload A/E; UISS dalam Markdown (`prepare_code/`); UR XD01 dengan layout UISS; skill **ur-generator**.

### Fase 6 · 28-Oct – 9-Nov · Review dan keputusan interface
- 29-Oct: mapping disimpan **per destinasi** (update / insert / delete), tidak lagi delete-all + insert.
- 30-Oct: **XD06 lewat RPA ke GTOPAS** (hanya daftar destinasi, tanpa Case/Day); part Inactive dihapus di GTOPAS dan AP POLE; AP POLE 1 baris per part.
- 4-Nov: Total Case/Day sebagai used / quota; halaman **Function Summary** dengan checkbox review per poin.
- 5-Nov: kolom export dan upload disamakan (FB-145); kolom audit CREATED/UPDATED.
- 6-Nov: **XD04 baca delta CREATE_DT > watermark, upsert, retry 3×**; XD05 jalan lewat trigger data baru; XD05 tidak jalan kalau XD04 gagal.
- 9-Nov: XD12 / XD14 / **XD15 tidak dipakai**; simulasi XD05 dengan data actual demand nyata.

### Fase 7 · 11–16 Nov · XD06 revisi dan hold ASN
- 11-Nov: simulasi ASSIGNED_QTY XD09; penuangan PO qty ke customer order line (FB-172); **XD06 revisi: RPA saja, bandingkan penuh dengan GTOPAS, try-catch**.
- 13-Nov: **hold oleh D/S** di XD10: hold per Part Number dan per case (Reduce PO Readiness), revisi 1–4 di hari yang sama; data dummy supplier / PO / manifest.
- 14-Nov: hold per case rev. 5: **case yang di-hold melepas PO-nya ke order berikutnya**; release masuk urutan terakhir tanggal itu (FB-183); popup info PO dan hold dalam Bahasa Indonesia; CR untuk ASN existing (ASN03 / ASN04).
- 16-Nov: XD09 memakai **TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D** (konsep DR); tidak ada tabel MAPPED baru, pakai REMAIN_QTY di TB_R_PRA_DAILY_ORDER_PART; tabel hold TB_R_CROSSDOCK_CASE_HOLD.

### Fase 8 · 17–20 Nov · RPA AP POLE dan period
- 17-Nov: **XD07 RPA di layar AP POLE** (WLM9Q890 / WLM9Q860) menggantikan SFTP; user guide AP POLE dan GTOPAS; [Sync] menjalankan RPA dari Excel yang di-download bot; aturan Sync Status (No Sync hanya kalau nilai yang dikirim berubah).
- 18-Nov: sheet Active to Inactive dihapus; part Inactive diambil [Sync] dari statusnya.
- 19-Nov: nama **Kanban Crossdock Master / Export Crossdock Master**; **period di Kanban Crossdock Master** (Past / Current / Next, Period Rollover tanggal 1); **Order Type** per baris destinasi; email notifikasi RPA; CR ASN03 / ASN04 rev 0.2.
- 20-Nov: **tidak ada response dari RPA (option C)**: Sync Status No Sync / Sent, Last Sent per target, **[Re-send last Sync]**; TB_R_CROSSDOCK_IF_RESULT dihapus.

### Fase 9 · 21–26 Nov · Staging sync
- 21-Nov: keputusan dasar staging: status sync keluar dari master, part Inactive tetap di Kanban AP POLE dengan Buyer-PD 0, parameter LAST_SYNC_DATE_APPOLE, sandbox SQL di prototype. XD01 rev 0.8–0.10 (antislop copy, 5.25 tabel per Save).
- 23-Nov (desain final):
  - **Staging per target**: TB_H_STG_APPOLE_KANBAN / _EXPORT / TB_H_STG_GTOPAS dengan format file upload; **SP_STG_WRITE** di Save (OPERATION_TYPE 1–5); **SP_STG_SYNC** di [Sync]; view file EXPORT_PRE / KANBAN / EXPORT_POST.
  - **Period menggantikan Effective Start Date** (Add Part: bulan berjalan atau Next).
  - Part Candidate hanya bisa jadi Active.
  - **RPA parent flow**: GTOPAS dulu; kalau GTOPAS gagal, AP POLE berhenti.
  - Simulasi full flow 24 langkah dengan semua kolom tabel.
- 24-Nov: Export Crossdock Master tanpa panel staging, Upload / Export di header; highlight perubahan UISS (`uiss/changes`); dokumen langkah RPA XD06 / XD07; file SP terpisah (`prepare_code/sql/crossdock_staging_sync.sql`).
- 26-Nov: **tanpa run ID** di staging: run = **SYNC_DT** (waktu klik [Sync] / rollover, diisi NSP, dikirim ke parent flow); bot baca `SYNC_STATUS = '1' AND SYNC_DT = :sync_dt`; Re-send = MAX(SYNC_DT). **SYNC_STATUS 0 / 1** saja: satu baris 0 per key, perubahan berikutnya meng-update baris itu, balik ke nilai terkirim = baris dihapus. XD01 0.16, XD02 0.7, XD03 0.7, XD05 0.9, XD06 / XD07 1.2.

---

## 4. Evolusi desain sync Crossdock Master

| Periode | Status sync | Pengiriman ke GTOPAS | Pengiriman ke AP POLE |
|---|---|---|---|
| 30-Sep – 12-Oct | Flag / 3 status di prototype | – | – |
| 13-Oct – 16-Nov | SYNC_STATUS per part di master (No Sync / Waiting / Success / Failed), hasil per target di tabel dummy | RPA (30-Oct), bandingkan penuh (11-Nov) | File SFTP CSV (18-Oct) |
| 17–20 Nov | Per part di master; sejak 20-Nov **No Sync / Sent** tanpa response | Bot download Excel NSP, bandingkan, Add / Delete | RPA di layar WLM9Q890 / WLM9Q860 |
| 23-Nov (sekarang, 26-Nov: run = SYNC_DT, satu baris belum terkirim per key) | 3 tabel staging per target dengan format file; aturan di `SP_STG_WRITE` saat Save | Parent flow: XD06 menjalankan ADD / DELETE dari TB_H_STG_GTOPAS | XD07 upload EXPORT_PRE → KANBAN → EXPORT_POST dari view |

Perubahan penting yang ikut terbawa:
- **Active → Inactive.** Sampai 20-Nov part dihapus dari Kanban AP POLE. Sekarang part tetap ada di Kanban dan destinasinya dikirim 0, karena AP POLE tetap memakai Effective Month lama sampai ada baris baru.
- **Effective Start Date** (default besok, minimal hari ini) dipakai sejak 30-Sep, lalu diganti **Period** pada 23-Nov.
- **Hasil RPA.** Sampai 19-Nov ditulis balik ke NSP. Sejak 20-Nov tidak ada response; hasil hanya lewat email.

### 4.1 Perbandingan desain awal (s/d 20-Nov) dan sekarang (23-Nov)

**Tempat status sync**

| Aspek | Awal | Sekarang |
|---|---|---|
| Status sync disimpan di | Kolom di TB_M_PART_CANDIDATE: SYNC_STATUS, GTOPAS_SYNC_DT / APPOLE_SYNC_DT, SYNC_RUN_ID | 3 tabel staging: TB_H_STG_APPOLE_KANBAN, TB_H_STG_APPOLE_EXPORT, TB_H_STG_GTOPAS |
| Unit sync | Per part (part dikirim utuh) | Per baris format file: Kanban per part + period, Export per destinasi + order type, GTOPAS per part + destinasi |
| Nilai status | No Sync / Waiting / Success / Failed; sejak 20-Nov No Sync / Sent | Per baris: 0 belum terkirim / 1 terkirim / 2 Superseded |
| Kapan jadi No Sync | Nilai yang dikirim berubah (status ke/dari Active, Pcs/Case, Max, destinasi, Case/Day) | `SP_STG_WRITE` menulis baris saat Save; kembali ke nilai terkirim → Superseded |
| Nilai yang dikirim | Tidak tersimpan (hanya status) | Tersimpan persis seperti di file upload |
| History sync | Event SYNC di TB_H_PART_CANDIDATE (No Sync → Sent) | Dari tabel staging; event SYNC tidak ditulis ke TB_H |
| Last Sent | GTOPAS_SYNC_DT / APPOLE_SYNC_DT di master | SYNC_DT terakhir per tabel staging |

**[Sync]**

| Aspek | Awal | Sekarang |
|---|---|---|
| Yang diambil | Part Active (Current / Next) dan Inactive dengan status No Sync | Baris SYNC_STATUS 0 (AP POLE: Current + Next; GTOPAS: Current) |
| Proses saat klik | Master jadi Sent + run ID + waktu kirim, history SYNC, jalankan XD06 dan XD07 | `SP_STG_SYNC` 0 → 1 + run ID, jalankan parent flow |
| Urutan upload AP POLE | Tidak diatur | OPERATION_TYPE (ditulis saat Save) → EXPORT_PRE / KANBAN / EXPORT_POST, ROW_ORDER |
| Re-send | Part dari run terakhir dikirim lagi | Run ID yang sama lewat parent flow (RESEND) |

**RPA**

| Aspek | Awal | Sekarang |
|---|---|---|
| Sumber data bot | Bot login ke NSP dan download Export Excel XD01 | Tabel staging dan view (user DB read-only) |
| XD06 GTOPAS | Baca semua baris WVJA5204, bandingkan dengan Excel NSP (sheet GTOPAS Compare), Add / Delete / Keep | Jalankan ACTION ADD / DELETE dari TB_H_STG_GTOPAS, tanpa membandingkan |
| XD07 AP POLE | RPA di layar WLM9Q890 (part) dan WLM9Q860 (destinasi), sheet AP POLE Compare | Upload file LLM9Q910 / LLM9Q880 dari template |
| Part jadi Inactive | Part dihapus dari Kanban AP POLE dan semua baris GTOPAS | Kanban tetap, Export DELETE (0), GTOPAS DELETE, header 5 |
| Cara jalan | XD06 dan XD07 jalan sendiri-sendiri | Parent flow: skenario 1 (GTOPAS dulu; kalau gagal, AP POLE berhenti), skenario 2 (AP POLE saja), Rollover (XD06 saja) |
| Error | Try-catch: satu error, seluruh run gagal | GTOPAS: baris gagal dicatat, baris lain tetap jalan. AP POLE: berhenti di file yang ditolak |
| Hasil ke NSP | Success / Failed ditulis balik; sejak 20-Nov tidak ada | Tidak ada; email |
| Email | 1 per target | 1 per run (GTOPAS + AP POLE) |

**Crossdock Master**

| Aspek | Awal | Sekarang |
|---|---|---|
| Mulai berlaku | Effective Start Date (default besok, minimal hari ini, bisa diubah selama Candidate) | Period bulan berjalan atau Next; terkunci setelah disimpan |
| Add Part | Ke period berjalan, SYNC_STATUS 0 | Bulan berjalan / Next; setelah tanggal D baris Next ikut dibuat; Candidate tidak menulis staging |
| Pilihan status Edit part Candidate | Candidate / Active / Inactive | Candidate / Active |
| Filter layar | Sync Status default No Sync (part Sent tersembunyi) | Chip AP POLE / GTOPAS dari staging |
| Export Excel | Kolom Sync Status dan Last Sent, dipakai bot sebagai sumber | Hanya informasi |
| Upload XD02 | Kolom Effective Start Date | Kolom Period (A: bulan berjalan / Next, E: bulan berjalan) |
| XD05 | Lewati part dengan Effective Start Date setelah tanggal run; status ke/dari Active atau mapping beda → No Sync | Semua part dengan baris di Current; Kanban ADD dengan OPERATION_TYPE, Export ADD / DELETE, GTOPAS hanya untuk destinasi yang muncul / hilang |
| Period Rollover | Part yang kombinasi part + destinasinya beda → GTOPAS Sent, XD06 jalan | Baris GTOPAS period baru 0 → 1, parent flow ROLLOVER |
| Kolom TB_M_PART_CANDIDATE | + EFFECTIVE_START_DATE, SYNC_STATUS, GTOPAS_SYNC_DT, APPOLE_SYNC_DT, SYNC_RUN_ID | Tanpa kolom itu |

**Alasan perubahan.** Status per part di master tidak menyimpan nilai apa yang dikirim. Akibatnya bot harus download Excel dan membandingkan sendiri, urutan upload ke AP POLE tidak bisa diatur, dan perubahan setelah [Sync] bercampur dengan status. Desain sekarang menyimpan baris dalam format file per target, menentukan urutan saat Save, dan menjalankan GTOPAS dulu supaya AP POLE tidak jalan kalau GTOPAS gagal.

---

## 5. Business process step by step (desain sekarang)

Period: **Past** (lihat saja), **Current** (bulan berjalan, bisa diedit), **Next** (dibuat XD05 di tanggal D, lihat saja sampai tanggal 1).
OPERATION_TYPE: **1** Max turun, **2** Max naik, **3** Max sama, **4** belum pernah dikirim, **5** hanya destinasi yang berubah (header, tidak diupload).

### F1 · Master setup (mingguan / bulanan / kapan saja)

| No | Siapa | Function | Langkah |
|---|---|---|---|
| M1 | GTOPAS | – | Destination master tersedia di DB Surrounding |
| M2 | NSP Batch | XD13 | Mingguan 21:30: TB_M_H0125_DESTINATION delete – insert, retry 3×. Gagal → rollback, master lama tetap dipakai |
| M3 | Procurement | XD01 / XD02 | Daftarkan part (layar Add Part atau upload flag A): Part No dari Part Master, **Period** bulan berjalan atau Next, Min MAD, Pcs/Case, Max Case/Day. Status selalu Candidate. Add bulan berjalan setelah tanggal D → baris Next ikut dibuat. Candidate belum dikirim (tidak ada baris staging) |
| M4 | Procurement | XD01 / XD02 | Ubah part (layar Edit atau upload flag E, bulan berjalan): Pcs/Case, Max Case/Day, Min MAD, status. Candidate → Active (Kanban ADD op 4). Active ↔ Inactive. Max tidak boleh di bawah total mapping (MSG14) |
| M5 | GTOPAS → NSP Batch | XD04 | Bulanan: actual demand dibaca delta CREATE_DT > watermark, upsert, retry 3×. Gagal → XD05 tidak jalan |
| M6 | NSP Batch | XD05 proses 1 | Tanggal D: buat period **Next** dari semua part yang punya baris di Current. Avg MAD (pembagi bulan tetap) ≥ Min MAD → Active, < Min MAD → Inactive |
| M7 | NSP Batch | XD05 proses 2 | Max Case/Day part Active dibagi ke destinasi menurut porsi MAD (top-N, minimal 1 case, total = Max). Staging: Kanban ADD per part, Export ADD per destinasi, DELETE (0) untuk destinasi yang hilang atau part Inactive, GTOPAS hanya untuk destinasi yang muncul / hilang |
| M8 | Procurement | XD01 | Cek status dan history part (TB_H_PART_CANDIDATE) |
| M9 | D/S | XD01 / XD03 | Review / ubah mapping Current (layar Edit mapping atau upload XD03): disimpan per destinasi. Total Case/Day ≤ Max (MSG20). Setiap perubahan → `SP_STG_WRITE`: Export ADD / EDIT / DELETE, GTOPAS kalau destinasi muncul / hilang, header 5 kalau Kanban tidak berubah |
| M10 | D/S | XD01 | **[Sync (n)]**: `SP_STG_SYNC` mengubah baris 0 → 1 dengan run ID (AP POLE: Current + Next; GTOPAS: Current), lalu menjalankan parent flow |
| M11 | Power Automate | Parent flow | Run punya baris GTOPAS → **skenario 1**: XD06 dulu, XD07 hanya kalau GTOPAS berhasil. Tidak punya → **skenario 2**: langsung XD07 |
| M12 | RPA | XD06 | GTOPAS WVJA5204 (Depot 01): ADD = daftarkan part + destinasi (Maker A, Dom/Os 2, TOPAS Order Type 3, Trans 2); DELETE = MT DEL. Sudah ada / sudah hilang = OK. Baris gagal dicatat, baris lain jalan |
| M13 | RPA | XD07 | Isi template dari view, upload satu per satu: **EXPORT_PRE** (Export part op 1) → **KANBAN** (op 1–4) → **EXPORT_POST**. Per part di file Export: turun / hapus dulu, baru naik / tambah. AP POLE cek total RCS ≤ Max per baris. File ditolak → berhenti |
| M14 | Power Automate | Parent flow | Satu email per run: SUCCESS / FAILED, hasil GTOPAS dan AP POLE |
| M15 | D/S | XD01 | Email FAILED → **[Re-send last Sync]** sebelum [Sync] berikutnya: run ID sama, baris sama |
| M16 | NSP Batch | XD05 proses 3 | Tanggal 1 jam 00:10: **Period Rollover** (Next jadi Current). Baris GTOPAS period baru 0 → 1, parent flow ROLLOVER (XD06 saja) |

### F2 · Daily order sampai ASN

| No | Siapa | Function | Langkah |
|---|---|---|---|
| D0–D1 | GTOPAS | existing | Customer order crossdock dirilis (D-2), ORDER_STATUS 7, kelipatan pcs/case |
| D2 | NSP | existing | PO supplier (D-1): 1 PO per Part per Customer Order Date, qty = total order semua destinasi, manifest CROSS_DOCK_FLAG X. Kurang → Short PO |
| D3 | NSP Batch | XD08 | 27:30: upsert H0253 yang berubah (delta INTF_UPDATE_DT); UPD_STATUS 6 / 2; serial split tetap terhubung ke ASN-nya; **lepas semua draft** |
| D5 | Supplier | XD10 | Pilih Delivery Date + Rit, [Search] |
| D6 | NSP Batch | XD09 | Isi TB_T_INSTRUCTION_H / _D untuk company user: line H0253 status 7, belum di-hold / belum di-map; urutan alokasi GTOPAS; PO dituang FIFO (REMAIN_QTY); pcs dipotong per case @ PCS_CASE; titik potong valid (CUT_FLAG); unit Ready / Partially Ready / Not Ready |
| D7 | Supplier | XD10 | Centang case dari case 1 sampai titik potong; per Part Number tanggal tertua dulu; 1 ASN = 1 Supplier Code + Plant; [Create ASN] |
| D8 | NSP | XD10 | Lock + cek ulang hold; insert TB_R_INSTRUCTION; REMAIN_QTY PO dikurangi; PO_MAPPED_FLAG Y untuk line yang masuk penuh |
| D9 | Supplier | XD10 | Case List: cek case, download case label, [Submit ASN] |
| D10 | NSP | XD10 5.7 | Submit process (Submit ID): ASN No dan Case No dari sequence existing; insert TB_R_DAILY_ORDER_MANIFEST / PART |
| D12–D14 | NSP → GTOPAS | existing | Interface ASN ke Surrounding dan GTOPAS; receiving di GTOPAS |
| D15 | GTOPAS | existing | H0253 ORDER_STATUS 6; receipt sebagian memecah line (SERIAL_NO baru), diambil XD08 berikutnya |

### F4 · Hold dan cancel

| No | Siapa | Function | Langkah |
|---|---|---|---|
| H1 | D/S | XD10 | Lihat detail delivery plan (semua supplier) |
| H2 | D/S | XD10 | **Hold per Part Number** (sub screen per supplier + plant, TB_R_CROSSDOCK_PART_HOLD): unit part itu On Hold di semua tanggal |
| H3 | D/S | XD10 | **Hold per case** ([Edit hold] → centang → [Save], TB_R_CROSSDOCK_CASE_HOLD): pcs case itu keluar dari unit sebelum PO dituang; PO-nya dipakai order berikutnya |
| H4 | NSP | XD09 | [Search] berikutnya tidak memakai baris yang di-hold |
| H5 | Supplier | XD10 | Hold setelah unit dicentang → [Create ASN] gagal seluruhnya, daftar di-refresh |
| H6 | D/S | XD10 | Release: baris masuk urutan terakhir Customer Order Date-nya, dapat PO berikutnya |
| C1 | GTOPAS | SOP | Hanya qty yang belum di ASN yang boleh di-cancel (cek feedback ASN) |
| C2 | GTOPAS | – | Cancel: ORDER_STATUS 2; cancel sebagian = SERIAL_NO baru |
| C3–C4 | NSP Batch | XD08 | UPD_STATUS 2; lepas semua draft (case kembali ke delivery plan) |
| C5 | NSP Batch | XD08 | Cancel atas qty di ASN yang sudah submit: LOG5, ASN tidak diubah, masuk Change Order Number |
| C6 | Supplier | XD10 | [Search] ulang; submit draft lama gagal (MSG11) |
| C7 | D/S | XD11 | Change Order Number: qty cancel dan kandidat (part sama, UPD_STATUS 6, PO_MAPPED N, belum di ASN, tertua dulu) |
| C8 | D/S | XD11 | Pindahkan qty dari case terakhir ke line kandidat (baris dipecah kalau perlu); riwayat TB_H_CROSSDOCK_ORDER_CHANGE |

### Abnormality utama

| Kode | Function | Kondisi | Penanganan |
|---|---|---|---|
| AB01 / AB03 / AB07 | XD13 / XD04 / XD08 | DB Surrounding tidak terbaca setelah 3 retry | Rollback, watermark tetap; run berikutnya mengambil lagi |
| AB02 | XD02 / XD03 | File upload tidak valid atau aturan baris gagal | Seluruh file ditolak, result report + sheet Re-upload |
| AB04 / AB05 | XD05 | Run dan 3 retry gagal; destinasi tidak ada di master | [Run calculation] aktif; daftarkan destinasi lewat GTOPAS → XD13 |
| AB06 | XD06 / XD07 | GTOPAS gagal (skenario 1) atau AP POLE menolak file | AP POLE tidak dikirim / berhenti di file itu; email FAILED; [Re-send last Sync] |
| AB08 / AB17 | XD09 / XD10 | Case tanpa PO, Short PO | Unit Partially Ready / Not Ready; tunggu PO |
| AB09–AB11 | XD10 | Hold setelah dicentang; blok tidak Ready lagi; lebih dari satu supplier | Create ASN gagal, tidak ada yang disimpan |
| AB12 / AB13 | XD08 / XD10 | Draft dilepas atau line berubah; submit gagal | MSG11; rollback, mapping dilepas |
| AB15 / AB16 | XD11 / XD08 | Kandidat diambil sesi lain; cancel qty yang sudah di ASN | MSG4; masuk Change Order Number |

---

## 6. Open points

1. Active → Inactive menghapus mapping period itu (TB_M_PART_CANDIDATE_DEST): belum dikonfirmasi.
2. Period Next: AP POLE dikirim di [Sync] setelah tanggal D, GTOPAS baru saat rollover. Kalau GTOPAS gagal saat rollover, AP POLE period itu sudah terkirim.
3. Cara NSP menjalankan parent flow: HTTP call dari [Sync], atau tabel run yang dipantau flow.
4. GTOPAS gagal: hentikan seluruh run (sekarang) atau hanya part yang gagal.
5. Langkah upload di AP POLE (Common File Upload) TBC dengan tim AP POLE.
6. AB19: sisa PO qty dari order yang di-cancel belum punya pemilik. AB20: qty cancel di ASN tanpa kandidat menunggu tanpa batas waktu.
7. Nama tabel staging dan konstanta yang disimpan per baris (Operator ID P6, Transport Code 2, dll.).

---

## 7. Cara build dokumen

```
bash deliverables/function_list_v2/build_all_v2.sh            # semua UISS v2 + prepare_code
python3 deliverables/function_list_v2/specs/merge_xd01_hand.py # XD01 hand-tidied workbook
python3 deliverables/function_list_v2/erd/build_erd.py         # Concept ERD
python3 deliverables/function_list_v2/erd/build_dbstructure.py # DB Structure
python3 deliverables/function_list_v2/ur/build_ur.py XD01      # User Requirement XD01
python3 deliverables/function_list_v2/summary/build_ur_summary.py
cd deliverables/function_list_v2/erd/proposal_staging_sync/simulation && node dump_stg_flow.cjs && python3 build_stg_flow_xlsx.py
```

Perubahan spec ditulis sebagai script `specs/apply_DDMM*.py` yang dijalankan berurutan di `build_all_v2.sh`; yang terbaru `apply_2611.py` (staging tanpa run ID: run = SYNC_DT, SYNC_STATUS 0/1, satu baris belum terkirim per key).

SQL staging (DDL, SP, view, query) di-generate: `python3 deliverables/function_list_v2/erd/proposal_staging_sync/build_staging_sql.py` → `prepare_code/sql/crossdock_staging_sync.sql`.

Dokumen langkah RPA: `cd deliverables/user_guide && python3 render_rpa.py && python3 build_rpa_steps.py`.
