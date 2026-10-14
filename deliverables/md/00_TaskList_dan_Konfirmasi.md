# Task List & Daftar Konfirmasi – Crossdock Optimization

Status per **14-Oct-2026**. Sumber data: `deliverables/exec/project_items.py` (sama dengan Excel `deliverables/exec/Crossdock_Executive_Overview.xlsx`).

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
| X12 | Customer Order - PO Mapping | Batch | System | B. Daily operation | `X12_UISS_Batch_CustomerOrderPOMapping.xlsx` | X12_BATCH_CustomerOrder_PO_Mapping.md |
| X13 | ASN Inquiry | Screen | Supplier / D/S team | B. Daily operation | `X13_UISS_Screen_ASNInquiry.xlsx` | X13_SCREEN_ASNInquiry.md |

## Sudah selesai

- UISS 13 fungsi (X1-X13) versi 0.1 + file .md per fungsi
- Prototype Part List, Mapping per Destination, ASN Crossdock Creation, ASN Inquiry (GitHub Pages)
- Rumus kalkulasi DAD (X6) dan mapping destinasi (X7) termasuk aturan pembulatan, dikonfirmasi 14-Oct-26
- Struktur tabel H0202 / H0253 / H0125 dari I/F layout G-TOPAS, termasuk SERIAL_NO
- Alur ASN baru sesuai ASN_Flow_Normal.xlsx (unit Part + Customer Order Date, 1 case per destinasi, FIFO)
- Header delivery plan level case; detail destinasi & pcs hanya untuk tim D/S

## Task list (belum dikerjakan)

| No | Task | Function | Kategori | PIC | Tergantung | Status | Prioritas |
|---|---|---|---|---|---|---|---|
| 1 | Update UISS X8 / X13 setelah konfirmasi case label, nomor ASN, route master | X8 / X13 | Dokumen | FID Rayhan | Konfirmasi no. 1-8 | Waiting confirmation | High |
| 2 | Finalisasi logika FIFO dan struktur Pra Daily Order di UISS X12 | X12 | Dokumen | FID Rayhan | Konfirmasi no. 9 | Waiting confirmation | High |
| 3 | Isi jadwal & retry di Schedule sheet UISS X5, X9-X12 | X5, X9-X12 | Dokumen | FID Rayhan | Konfirmasi no. 10-12 | Waiting confirmation | Medium |
| 4 | Buat UISS-Batch RPA Sync (jika disetujui) | X3 | Dokumen | FID Rayhan | Konfirmasi no. 16-17 | Not started | Medium |
| 5 | Lengkapi panjang VARCHAR dan nama field di Appendix semua UISS | X1-X13 | Dokumen | FID Rayhan | Konfirmasi no. 20 | Waiting confirmation | Low |
| 6 | Review UISS X1-X13 versi 0.1 oleh user / reviewer | X1-X13 | Review | User | - | Not started | High |
| 7 | Tambah kolom SERIAL_NO di tabel / query H0253 sumber | X10 | Data | Tim DB Surrounding | Konfirmasi no. 15 | Not started | High |
| 8 | Konfirmasi struktur tabel Pra Daily Order dan route master | X8, X12 | Data | Tim NSP / IT | - | Not started | High |
| 9 | Prototype: Download Case Label sesuai format | X8 / X13 | Prototype | FID Rayhan | Konfirmasi no. 1 | Waiting confirmation | Medium |
| 10 | Prototype: Case List supplier level case & akses D/S | X8 | Prototype | FID Rayhan | Konfirmasi no. 4-5 | Waiting confirmation | Medium |
| 11 | Prototype: Cancel ASN di ASN Inquiry (jika diperlukan) | X13 | Prototype | FID Rayhan | Konfirmasi no. 8 | Waiting confirmation | Low |
| 12 | Susun testing strategy & test scenario (unit, integration, UAT) X1-X13 | X1-X13 | Testing | FID Rayhan | UISS final | Not started | High |
| 13 | Definisikan proses lanjutan setelah ASN (penerimaan di crossdock, pengiriman ke destinasi) | Next scope | Analisis | FID Rayhan / User | Arahan user | Not started | Medium |
| 14 | Susun BRD / TSD (jika dibutuhkan proyek) | All | Dokumen | FID Rayhan | Arahan user | Not started | Low |

## Perlu konfirmasi dari user

| No | Function | Topik | Pertanyaan | Usulan BSA | Dampak jika belum diputuskan |
|---|---|---|---|---|---|
| 1 | X8 / X13 | Case label | Format, isi, dan nama file case label (Download Case Label). | Ikuti format case label NSP existing. | Case label belum bisa dicetak; UISS X8 / X13 masih TBD. |
| 2 | X8 | Nomor ASN | Aturan nomor urut ASN. | ASN-{Supplier}-{YYMMDD Delivery Date}-{Seq 3 digit}, reset per hari per supplier. | Format ASN No di X8 / X13 masih usulan. |
| 3 | X8 | Isi 1 ASN | Apakah 1 ASN wajib 1 supplier / plant? | Ya, 1 ASN = 1 supplier + plant. | Validasi pilihan unit di Create ASN. |
| 4 | X8 | Case List supplier | Sub screen Case List untuk supplier juga level case saja (sembunyikan Customer Order No dan pcs)? | Ya, samakan dengan header (level case). | Kolom Case List di UISS X8. |
| 5 | X8 | Akses D/S | Apakah tim D/S juga boleh Create / Submit ASN, atau hanya melihat? | Hanya melihat (read only). | Hak akses tombol Create ASN. |
| 6 | X8 | Route master | Nama dan struktur tabel route master (Rit Cycle / Route). | Pakai route master NSP existing. | Combo Rit Cycle masih mock. |
| 7 | X8 / X13 | Tabel header ASN | Konfirmasi nama dan kolom TB_R_ASN_CROSSDOCK_H (usulan). | Pakai usulan di Appendix UISS X8. | Data mapping Submit ASN. |
| 8 | X13 | Cancel ASN | Perlu cancel / revisi ASN dari ASN Inquiry? | Perlu cancel selama barang belum dikirim. | Tambahan fungsi dan status ASN. |
| 9 | X12 | Pra Daily Order | Struktur fisik TB_R_PRA_DAILY_ORDER_MANIFEST / PART dan cara menandai PO yang sudah terpasang. | Tambah flag / qty terpakai di PART. | Logika FIFO X12 belum final. |
| 10 | X9-X12 | Jadwal & retry | Jadwal scheduler NSP untuk X9, X10, X11, X12 dan perlu auto retry seperti X6 / X7? | Setelah data G-TOPAS tersedia; auto retry 3x. | Schedule sheet di UISS masih TBC. |
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
| 23 | X1 | Effective Start Date | Kalimat "Effective Start Date" yang menggantung di Op Desc 5.4 a.4 (UISS X1): aturan apa yang dimaksud? | Default besok, minimum hari ini, wajib diisi. | Op Desc X1 belum lengkap. |
