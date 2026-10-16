# Task List & Daftar Konfirmasi – Crossdock Optimization

Status per **16-Oct-2026**. Sumber data: `deliverables/exec/project_items.py` (sama dengan Excel `deliverables/exec/Crossdock_Executive_Overview.xlsx`).

## Index dokumen

| ID | Fungsi | Tipe | User | Fase | UISS | MD |
|---|---|---|---|---|---|---|
| X1 | Part List (Crossdock Master Setting) | Screen | Procurement | A. Master setup | `X1_UISS_Screen_PartList.xlsx` | X1_SCREEN_PartList.md |
| X2 | Part List Upload | Batch | Procurement | A. Master setup | `X2_UISS_Batch_PartListUpload.xlsx` | X2_BATCH_PartList_Upload.md |
| X3 | Mapping per Destination (+ Sync via RPA) | Screen | D/S team | A. Master setup | `X3_UISS_Screen_MappingPerDestination.xlsx` | X3_RPA_Sync.md, X3_SCREEN_MappingPerDestination.md |
| X4 | Mapping Upload | Batch | D/S team | A. Master setup | `X4_UISS_Batch_MappingUpload.xlsx` | X4_BATCH_Mapping_Upload.md |
| X5 | Actual Demand Summary Sync | Batch | System | A. Master setup | `X5_UISS_Batch_ActualDemandSummarySync.xlsx` | X5-X7_BATCH_Calculation_Functions.md |
| X6 | DAD Volume Calculation | Batch | System (manual run in X1) | A. Master setup | `X6_UISS_Batch_DADVolumeCalculation.xlsx` | X5-X7_BATCH_Calculation_Functions.md |
| X7 | Mapping Destination Calculation | Batch | System (manual run in X3) | A. Master setup | `X7_UISS_Batch_MappingDestinationCalculation.xlsx` | X5-X7_BATCH_Calculation_Functions.md |
| X8 | ASN Crossdock Creation | Screen | Supplier / D/S team (super admin) | B. Daily operation | `X8_UISS_Screen_ASNCrossdockCreation.xlsx` | X8_SCREEN_ASNCrossdockCreation.md |
| X9 | H0202 Demand History Sync | Batch | System | B. Daily operation | `X9_UISS_Batch_H0202DemandHistorySync.xlsx` | X9_BATCH_H0202_DemandHistory_Sync.md |
| X10 | H0253 Order Control Sync | Batch | System | B. Daily operation | `X10_UISS_Batch_H0253OrderControlSync.xlsx` | X10_BATCH_H0253_OrderControl_Sync.md |
| X11 | H0125 Destination Master Sync | Batch | System | A. Master setup | `X11_UISS_Batch_H0125DestinationMasterSync.xlsx` | X11_BATCH_H0125_DestinationMaster_Sync.md |
| X12 | Get Order - Customer Order PO Pre-mapping | Function | Supplier (button in X8) | B. Daily operation | `X12_UISS_Batch_GetOrderPOPreMapping.xlsx` | X12_FUNCTION_GetOrder_PO_PreMapping.md |
| X13 | ASN Inquiry | Screen | Supplier / D/S team | B. Daily operation | `X13_UISS_Screen_ASNInquiry.xlsx` | X13_SCREEN_ASNInquiry.md |
| X14 | ASN Submit | Batch | System ([Submit ASN] in X8) | B. Daily operation | `X14_UISS_Batch_ASNSubmit.xlsx` | X14_BATCH_ASN_Submit.md |
| X15 | Menu Settings (admin panel) | Screen | Admin | Common | `X15_UISS_Screen_MenuSettings.xlsx` | X15_SCREEN_MenuSettings.md |

## Sudah selesai

- UISS 15 fungsi (X1-X15) versi 0.1 + file .md per fungsi
- Prototype Part List, Mapping per Destination, ASN Crossdock Creation, ASN Inquiry (GitHub Pages)
- Rumus kalkulasi DAD (X6) dan mapping destinasi (X7) termasuk aturan pembulatan, dikonfirmasi 14-Oct-26
- Struktur tabel H0202 / H0253 / H0125 dari I/F layout G-TOPAS, termasuk SERIAL_NO
- Alur ASN baru sesuai ASN_Flow_Normal.xlsx (unit Part + Customer Order Date, 1 case per destinasi, FIFO)
- Header delivery plan level case; detail destinasi & pcs hanya untuk tim D/S
- ASN flow versi 15-Oct: Search (X12 on-demand pre-mapping), Hold Flag per destinasi oleh D/S, Create ASN (mapping), status Ready / Not Ready / Created
- Submit ASN sebagai batch X14 (Submit ID, hasil ke log), cek hold saat Create ASN, admin panel Menu Settings, menu ASN Backend Process
- Konfirmasi ASN 16-Oct diterapkan: case label & case number sesuai existing, 1 ASN = 1 Supplier + Plant, D/S super admin (semua supplier), route master existing, ASN ke TB_R_DAILY_ORDER_MANIFEST / PART, Create ASN → TB_R_INSTRUCTION (Back / Cancel hapus), tabel baru mapped qty, cancel dari source (status 2)

## Task list (belum dikerjakan)

| No | Task | Function | Kategori | PIC | Tergantung | Status | Prioritas |
|---|---|---|---|---|---|---|---|
| 1 | Review struktur tabel baru TB_R_INSTRUCTION dan TB_R_PRA_DAILY_ORDER_MAPPED (nama / kolom usulan) | X8, X12, X14 | Data | Tim NSP / IT (DBA) | - | Not started | High |
| 2 | Mapping kolom fisik ke TB_R_DAILY_ORDER_MANIFEST / PART, route master dan last sequence existing | X8, X13, X14 | Data | Tim NSP / IT | - | Not started | High |
| 3 | Isi jadwal & retry di Schedule sheet UISS X5, X9-X11 | X5, X9-X11 | Dokumen | FID Rayhan | Konfirmasi no. 1-3 | Waiting confirmation | Medium |
| 4 | Buat UISS-Batch RPA Sync X16 (jika disetujui) | X3 | Dokumen | FID Rayhan | Konfirmasi no. 7-8 | Not started | Medium |
| 5 | Lengkapi panjang VARCHAR dan nama field di Appendix semua UISS | X1-X15 | Dokumen | FID Rayhan | Konfirmasi no. 11 | Waiting confirmation | Low |
| 6 | Review UISS X1-X15 versi 0.1 oleh user / reviewer | X1-X15 | Review | User | - | Not started | High |
| 7 | Tambah kolom SERIAL_NO di tabel / query H0253 sumber | X10 | Data | Tim DB Surrounding | Konfirmasi no. 6 | Not started | High |
| 8 | Tambah kolom HOLD_FLAG / PO_MAPPED_FLAG di H0253 NSP, dipertahankan saat sync X10 (sudah diputuskan) | X10 | Data | Tim NSP / IT | - | Not started | High |
| 9 | Prototype: Download Case Label sesuai format existing | X8 / X13 | Prototype | FID Rayhan | Contoh label existing | Not started | Medium |
| 10 | Susun testing strategy & test scenario (unit, integration, UAT) X1-X15 | X1-X15 | Testing | FID Rayhan | UISS final | Not started | High |
| 11 | Definisikan proses lanjutan setelah ASN (penerimaan di crossdock, pengiriman ke destinasi) | Next scope | Analisis | FID Rayhan / User | Arahan user | Not started | Medium |
| 12 | Susun BRD / TSD (jika dibutuhkan proyek) | All | Dokumen | FID Rayhan | Arahan user | Not started | Low |

## Perlu konfirmasi dari user

| No | Function | Topik | Pertanyaan | Usulan BSA | Dampak jika belum diputuskan |
|---|---|---|---|---|---|
| 1 | X9-X11 | Jadwal & retry | Jadwal scheduler NSP untuk X9, X10, X11 dan perlu auto retry seperti X6 / X7? | Setelah data G-TOPAS tersedia; auto retry 3x. | Schedule sheet di UISS masih TBC. |
| 2 | X5 | Jadwal X5 | Tanggal / jam scheduler bulanan X5. | Tanggal 1 jam 01:00, sebelum X6. | Schedule sheet X5 / X6. |
| 3 | X5 / X6 | X5 gagal | Kalau X5 gagal, apakah X6 dibatalkan? | Ya, X6 tidak jalan. | Aturan dependensi batch. |
| 4 | X5 | Kolom DAD | Kolom DAD di Actual Demand Summary dipakai atau tidak? | Tidak dipakai (hanya MAD). | Mapping kolom X5. |
| 5 | X5 / X7 | Order type N + S | ORDER_TYPE_GROUP N dan S dijumlahkan (sementara). Final? | Tetap dijumlahkan. | Rumus MAD di X6 / X7. |
| 6 | X10 | SERIAL_NO | SERIAL_NO perlu ditambahkan di tabel / query H0253 sumber (DB Surrounding). | Tim surrounding menambah kolom. | Tanpa SERIAL_NO key H0253 tidak unik. |
| 7 | X3 | RPA Sync | Detail fungsi RPA: layar global system, urutan input, waktu proses, timeout, user ID RPA. | Perlu sesi dengan tim RPA. | UISS RPA belum bisa dibuat. |
| 8 | X3 | UISS RPA | Perlu UISS-Batch tersendiri untuk RPA Sync? | Ya, X16. | Tambahan dokumen. |
| 9 | X3 | Status Waiting | Apakah status Waiting (Sync) perlu batas waktu, lalu kembali ke Failed? | Ya, 30 menit. | Status sync bisa menggantung. |
| 10 | X1-X4 | History | Konfirmasi kolom dan retensi TB_H_PART_CANDIDATE (usulan 24 bulan). | Pakai usulan. | Appendix tabel history. |
| 11 | X1-X4 | Panjang kolom | Panjang VARCHAR kolom (PART_NO dll.) dan nama field Part Name di TB_M_PART_MASTER. | Ikuti TB_M_PART_MASTER. | Masih VARCHAR(TBD) di Appendix. |
| 12 | X2 / X4 | Template & log | Lokasi file template dan result report; retensi Log upload. | Shared folder NSP; retensi 12 bulan. | Operation description upload. |
| 13 | X1 | Akun read only | Definisi akun read-only ([View]) untuk Part List. | Role Viewer: hanya Search / Export. | Screen mode View. |
| 14 | X15 | Menu Settings | Pengaturan show / hide menu berlaku per role atau global, dan siapa yang boleh membuka layar ini? | Per role; hanya admin. | Struktur TB_M_MENU_VISIBILITY. |
| 15 | X1 | Effective Start Date | Kalimat "Effective Start Date" yang menggantung di Op Desc 5.4 a.4 (UISS X1): aturan apa yang dimaksud? | Default besok, minimum hari ini, wajib diisi. | Op Desc X1 belum lengkap. |
