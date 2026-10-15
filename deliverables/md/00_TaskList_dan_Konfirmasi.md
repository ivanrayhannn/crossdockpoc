# Task List & Daftar Konfirmasi – Crossdock Optimization

Status per **15-Oct-2026**. Sumber data: `deliverables/exec/project_items.py` (sama dengan Excel `deliverables/exec/Crossdock_Executive_Overview.xlsx`).

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
| X8 | ASN Crossdock Creation | Screen | Supplier (detail: D/S team) | B. Daily operation | `X8_UISS_Screen_ASNCrossdockCreation.xlsx` | X8_SCREEN_ASNCrossdockCreation.md |
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

## Task list (belum dikerjakan)

| No | Task | Function | Kategori | PIC | Tergantung | Status | Prioritas |
|---|---|---|---|---|---|---|---|
| 1 | Update UISS X8 / X13 setelah konfirmasi case label, isi 1 ASN, route master, tabel ASN | X8 / X13 | Dokumen | FID Rayhan | Konfirmasi no. 1-5 | Waiting confirmation | High |
| 2 | Finalisasi struktur Pra Daily Order (mapped qty) di UISS X8 / X12 | X8 / X12 | Dokumen | FID Rayhan | Konfirmasi no. 9 | Waiting confirmation | High |
| 3 | Isi jadwal & retry di Schedule sheet UISS X5, X9-X11 | X5, X9-X11 | Dokumen | FID Rayhan | Konfirmasi no. 10-12 | Waiting confirmation | Medium |
| 4 | Buat UISS-Batch RPA Sync (jika disetujui) | X3 | Dokumen | FID Rayhan | Konfirmasi no. 16-17 | Not started | Medium |
| 5 | Lengkapi panjang VARCHAR dan nama field di Appendix semua UISS | X1-X15 | Dokumen | FID Rayhan | Konfirmasi no. 20 | Waiting confirmation | Low |
| 6 | Review UISS X1-X15 versi 0.1 oleh user / reviewer | X1-X15 | Review | User | - | Not started | High |
| 7 | Tambah kolom SERIAL_NO di tabel / query H0253 sumber | X10 | Data | Tim DB Surrounding | Konfirmasi no. 15 | Not started | High |
| 8 | Tambah kolom HOLD_FLAG / PO_MAPPED_FLAG di H0253 NSP dan cara mempertahankannya saat sync | X10 | Data | Tim NSP / IT | Konfirmasi no. 7 | Not started | High |
| 9 | Konfirmasi struktur tabel Pra Daily Order dan route master | X8, X12 | Data | Tim NSP / IT | - | Not started | High |
| 10 | Prototype: Download Case Label sesuai format | X8 / X13 | Prototype | FID Rayhan | Konfirmasi no. 1 | Waiting confirmation | Medium |
| 11 | Prototype: Cancel ASN di ASN Inquiry (jika diperlukan) | X13 | Prototype | FID Rayhan | Konfirmasi no. 8 | Waiting confirmation | Low |
| 12 | Susun testing strategy & test scenario (unit, integration, UAT) X1-X15 | X1-X15 | Testing | FID Rayhan | UISS final | Not started | High |
| 13 | Definisikan proses lanjutan setelah ASN (penerimaan di crossdock, pengiriman ke destinasi) | Next scope | Analisis | FID Rayhan / User | Arahan user | Not started | Medium |
| 14 | Susun BRD / TSD (jika dibutuhkan proyek) | All | Dokumen | FID Rayhan | Arahan user | Not started | Low |

## Perlu konfirmasi dari user

| No | Function | Topik | Pertanyaan | Usulan BSA | Dampak jika belum diputuskan |
|---|---|---|---|---|---|
| 1 | X8 / X13 | Case label | Format, isi, dan nama file case label (Download Case Label). | Ikuti format case label NSP existing. | Case label belum bisa dicetak; UISS X8 / X13 masih TBD. |
| 2 | X8 | Isi 1 ASN | Apakah 1 ASN wajib 1 supplier / plant? | Ya, 1 ASN = 1 supplier + plant. | Validasi pilihan unit di Create ASN. |
| 3 | X8 | Akses D/S | Apakah tim D/S juga boleh Create / Submit ASN, atau hanya melihat + hold? | Hanya melihat + hold. | Hak akses tombol Create ASN. |
| 4 | X8 | Route master | Nama dan struktur tabel route master (Rit / Route). | Pakai route master NSP existing. | Combo Rit masih mock. |
| 5 | X8 / X13 | Tabel ASN | Konfirmasi TB_R_ASN_CROSSDOCK_H / _D (usulan) atau pakai tabel ASN existing. | Pakai usulan di Appendix UISS X8. | Data mapping Submit ASN. |
| 6 | X8 | Back / Cancel | Back / Cancel di Case List melepas mapping (PO_MAPPED_FLAG dan qty PO kembali). Setuju? | Ya. | Order bisa terkunci tanpa ASN. |
| 7 | X10 | Flag H0253 | HOLD_FLAG dan PO_MAPPED_FLAG dipertahankan per unique key saat delete - insert X10. Setuju? | Ya (cara teknis oleh tim IT). | Hold / mapping hilang setiap sync. |
| 8 | X13 | Cancel ASN | Perlu cancel / revisi ASN dari ASN Inquiry? | Perlu cancel selama barang belum dikirim. | Tambahan fungsi dan status ASN. |
| 9 | X8 / X12 | Pra Daily Order | Struktur fisik TB_R_PRA_DAILY_ORDER_MANIFEST / PART dan kolom qty terpakai (mapped qty). | Tambah kolom MAPPED_QTY di PART. | Logika FIFO X12 / Create ASN belum final. |
| 10 | X9-X11 | Jadwal & retry | Jadwal scheduler NSP untuk X9, X10, X11 dan perlu auto retry seperti X6 / X7? | Setelah data G-TOPAS tersedia; auto retry 3x. | Schedule sheet di UISS masih TBC. |
| 11 | X5 | Jadwal X5 | Tanggal / jam scheduler bulanan X5. | Tanggal 1 jam 01:00, sebelum X6. | Schedule sheet X5 / X6. |
| 12 | X5 / X6 | X5 gagal | Kalau X5 gagal, apakah X6 dibatalkan? | Ya, X6 tidak jalan. | Aturan dependensi batch. |
| 13 | X5 | Kolom DAD | Kolom DAD di Actual Demand Summary dipakai atau tidak? | Tidak dipakai (hanya MAD). | Mapping kolom X5. |
| 14 | X5 / X7 | Order type N + S | ORDER_TYPE_GROUP N dan S dijumlahkan (sementara). Final? | Tetap dijumlahkan. | Rumus MAD di X6 / X7. |
| 15 | X10 | SERIAL_NO | SERIAL_NO perlu ditambahkan di tabel / query H0253 sumber (DB Surrounding). | Tim surrounding menambah kolom. | Tanpa SERIAL_NO key H0253 tidak unik. |
| 16 | X3 | RPA Sync | Detail fungsi RPA: layar global system, urutan input, waktu proses, timeout, user ID RPA. | Perlu sesi dengan tim RPA. | UISS RPA belum bisa dibuat. |
| 17 | X3 | UISS RPA | Perlu UISS-Batch tersendiri untuk RPA Sync? | Ya, X14. | Tambahan dokumen. |
| 18 | X3 | Status Waiting | Apakah status Waiting (Sync) perlu batas waktu, lalu kembali ke Failed? | Ya, 30 menit. | Status sync bisa menggantung. |
| 19 | X1-X4 | History | Konfirmasi kolom dan retensi TB_H_PART_CANDIDATE (usulan 24 bulan). | Pakai usulan. | Appendix tabel history. |
| 20 | X1-X4 | Panjang kolom | Panjang VARCHAR kolom (PART_NO dll.) dan nama field Part Name di TB_M_PART_MASTER. | Ikuti TB_M_PART_MASTER. | Masih VARCHAR(TBD) di Appendix. |
| 21 | X2 / X4 | Template & log | Lokasi file template dan result report; retensi Log upload. | Shared folder NSP; retensi 12 bulan. | Operation description upload. |
| 22 | X1 | Akun read only | Definisi akun read-only ([View]) untuk Part List. | Role Viewer: hanya Search / Export. | Screen mode View. |
| 23 | X15 | Menu Settings | Pengaturan show / hide menu berlaku per role atau global, dan siapa yang boleh membuka layar ini? | Per role; hanya admin. | Struktur TB_M_MENU_VISIBILITY. |
| 24 | X1 | Effective Start Date | Kalimat "Effective Start Date" yang menggantung di Op Desc 5.4 a.4 (UISS X1): aturan apa yang dimaksud? | Default besok, minimum hari ini, wajib diisi. | Op Desc X1 belum lengkap. |
