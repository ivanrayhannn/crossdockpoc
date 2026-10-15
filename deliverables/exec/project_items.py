"""Single source for the Crossdock Optimization function map, task list and confirmation list.
Used by build_exec_overview.py (Excel) and to write deliverables/md/00_TaskList_dan_Konfirmasi.md."""

AS_OF = '15-Oct-2026'

# id, name, type, user / actor, phase, trigger / frequency, input, output, prototype
FUNCTIONS = [
    ('X1', 'Part List (Crossdock Master Setting)', 'Screen', 'Procurement', 'A. Master setup', 'On demand',
     'Part master', 'TB_M_PART_CANDIDATE, history', 'Yes'),
    ('X2', 'Part List Upload', 'Batch', 'Procurement', 'A. Master setup', 'Upload from X1',
     'Excel template', 'TB_M_PART_CANDIDATE, history, log', 'Yes'),
    ('X3', 'Mapping per Destination (+ Sync via RPA)', 'Screen', 'D/S team', 'A. Master setup', 'On demand',
     'Calculated mapping, destination master', 'TB_M_PART_CANDIDATE_DEST, Global System', 'Yes'),
    ('X4', 'Mapping Upload', 'Batch', 'D/S team', 'A. Master setup', 'Upload from X3',
     'Excel template', 'TB_M_PART_CANDIDATE_DEST, history, log', 'Yes'),
    ('X5', 'Actual Demand Summary Sync', 'Batch', 'System', 'A. Master setup', 'Monthly, before X6 (TBC)',
     'DB Surrounding TB_R_ACTUAL_DEMAND_SUMMARY', 'NSP TB_R_ACTUAL_DEMAND_SUMMARY', 'N/A'),
    ('X6', 'DAD Volume Calculation', 'Batch', 'System (manual run in X1)', 'A. Master setup', 'Monthly, after X5',
     'Actual demand, Min MAD', 'Part status Active / Inactive, TB_R_PART_DAD_RESULT', 'Yes (run bar)'),
    ('X7', 'Mapping Destination Calculation', 'Batch', 'System (manual run in X3)', 'A. Master setup', 'Own scheduler (TBC)',
     'Active parts, actual demand, Max Case/Day', 'New period mapping (case/day per destination)', 'Yes (run bar)'),
    ('X8', 'ASN Crossdock Creation', 'Screen', 'Supplier (detail: D/S team)', 'B. Daily operation', 'On demand',
     'Delivery Date, Rit; #TB_R_INSTRUCTION (X12)', 'H0253 flags, TB_R_ASN_CROSSDOCK_H / _D', 'Yes'),
    ('X9', 'H0202 Demand History Sync', 'Batch', 'System', 'B. Daily operation', 'Daily (TBC)',
     'G-TOPAS H0202', 'NSP TB_R_H0202', 'N/A'),
    ('X10', 'H0253 Order Control Sync', 'Batch', 'System', 'B. Daily operation', 'Daily (TBC)',
     'G-TOPAS H0253', 'NSP TB_R_H0253_ORDER_CONTROL_PRE', 'N/A'),
    ('X11', 'H0125 Destination Master Sync', 'Batch', 'System', 'A. Master setup', 'Weekly (TBC)',
     'G-TOPAS H0125', 'NSP TB_M_H0125_DESTINATION', 'N/A'),
    ('X12', 'Get Order - Customer Order PO Pre-mapping', 'Function', 'Supplier (button in X8)', 'B. Daily operation', 'On demand ([Get Order])',
     'H0253 (status 7, Hold N), Pra Daily Order', '#TB_R_INSTRUCTION (temp, FIFO)', 'Yes (in X8)'),
    ('X13', 'ASN Inquiry', 'Screen', 'Supplier / D/S team', 'B. Daily operation', 'On demand',
     'TB_R_ASN_CROSSDOCK_H / _D', 'Display, case label', 'Yes'),
]

# function, topic, question, proposal, impact if open
CONFIRMATIONS = [
    ('X8 / X13', 'Case label', 'Format, isi, dan nama file case label (Download Case Label).', 'Ikuti format case label NSP existing.', 'Case label belum bisa dicetak; UISS X8 / X13 masih TBD.'),
    ('X8', 'Isi 1 ASN', 'Apakah 1 ASN wajib 1 supplier / plant?', 'Ya, 1 ASN = 1 supplier + plant.', 'Validasi pilihan unit di Create ASN.'),
    ('X8', 'Akses D/S', 'Apakah tim D/S juga boleh Create / Submit ASN, atau hanya melihat + hold?', 'Hanya melihat + hold.', 'Hak akses tombol Create ASN.'),
    ('X8', 'Route master', 'Nama dan struktur tabel route master (Rit / Route).', 'Pakai route master NSP existing.', 'Combo Rit masih mock.'),
    ('X8 / X13', 'Tabel ASN', 'Konfirmasi TB_R_ASN_CROSSDOCK_H / _D (usulan) atau pakai tabel ASN existing.', 'Pakai usulan di Appendix UISS X8.', 'Data mapping Submit ASN.'),
    ('X8', 'Back / Cancel', 'Back / Cancel di Case List melepas mapping (PO_MAPPED_FLAG dan qty PO kembali). Setuju?', 'Ya.', 'Order bisa terkunci tanpa ASN.'),
    ('X10', 'Flag H0253', 'HOLD_FLAG dan PO_MAPPED_FLAG dipertahankan per unique key saat delete - insert X10. Setuju?', 'Ya (cara teknis oleh tim IT).', 'Hold / mapping hilang setiap sync.'),
    ('X13', 'Cancel ASN', 'Perlu cancel / revisi ASN dari ASN Inquiry?', 'Perlu cancel selama barang belum dikirim.', 'Tambahan fungsi dan status ASN.'),
    ('X8 / X12', 'Pra Daily Order', 'Struktur fisik TB_R_PRA_DAILY_ORDER_MANIFEST / PART dan kolom qty terpakai (mapped qty).', 'Tambah kolom MAPPED_QTY di PART.', 'Logika FIFO X12 / Create ASN belum final.'),
    ('X9-X11', 'Jadwal & retry', 'Jadwal scheduler NSP untuk X9, X10, X11 dan perlu auto retry seperti X6 / X7?', 'Setelah data G-TOPAS tersedia; auto retry 3x.', 'Schedule sheet di UISS masih TBC.'),
    ('X5', 'Jadwal X5', 'Tanggal / jam scheduler bulanan X5.', 'Tanggal 1 jam 01:00, sebelum X6.', 'Schedule sheet X5 / X6.'),
    ('X5 / X6', 'X5 gagal', 'Kalau X5 gagal, apakah X6 dibatalkan?', 'Ya, X6 tidak jalan.', 'Aturan dependensi batch.'),
    ('X5', 'Kolom DAD', 'Kolom DAD di Actual Demand Summary dipakai atau tidak?', 'Tidak dipakai (hanya MAD).', 'Mapping kolom X5.'),
    ('X5 / X7', 'Order type N + S', 'ORDER_TYPE_GROUP N dan S dijumlahkan (sementara). Final?', 'Tetap dijumlahkan.', 'Rumus MAD di X6 / X7.'),
    ('X10', 'SERIAL_NO', 'SERIAL_NO perlu ditambahkan di tabel / query H0253 sumber (DB Surrounding).', 'Tim surrounding menambah kolom.', 'Tanpa SERIAL_NO key H0253 tidak unik.'),
    ('X3', 'RPA Sync', 'Detail fungsi RPA: layar global system, urutan input, waktu proses, timeout, user ID RPA.', 'Perlu sesi dengan tim RPA.', 'UISS RPA belum bisa dibuat.'),
    ('X3', 'UISS RPA', 'Perlu UISS-Batch tersendiri untuk RPA Sync?', 'Ya, X14.', 'Tambahan dokumen.'),
    ('X3', 'Status Waiting', 'Apakah status Waiting (Sync) perlu batas waktu, lalu kembali ke Failed?', 'Ya, 30 menit.', 'Status sync bisa menggantung.'),
    ('X1-X4', 'History', 'Konfirmasi kolom dan retensi TB_H_PART_CANDIDATE (usulan 24 bulan).', 'Pakai usulan.', 'Appendix tabel history.'),
    ('X1-X4', 'Panjang kolom', 'Panjang VARCHAR kolom (PART_NO dll.) dan nama field Part Name di TB_M_PART_MASTER.', 'Ikuti TB_M_PART_MASTER.', 'Masih VARCHAR(TBD) di Appendix.'),
    ('X2 / X4', 'Template & log', 'Lokasi file template dan result report; retensi Log upload.', 'Shared folder NSP; retensi 12 bulan.', 'Operation description upload.'),
    ('X1', 'Akun read only', 'Definisi akun read-only ([View]) untuk Part List.', 'Role Viewer: hanya Search / Export.', 'Screen mode View.'),
    ('X1', 'Effective Start Date', 'Kalimat "Effective Start Date" yang menggantung di Op Desc 5.4 a.4 (UISS X1): aturan apa yang dimaksud?', 'Default besok, minimum hari ini, wajib diisi.', 'Op Desc X1 belum lengkap.'),
]

# task, function, category, PIC, depends on, status, priority
TASKS = [
    ('Update UISS X8 / X13 setelah konfirmasi case label, isi 1 ASN, route master, tabel ASN', 'X8 / X13', 'Dokumen', 'FID Rayhan', 'Konfirmasi no. 1-5', 'Waiting confirmation', 'High'),
    ('Finalisasi struktur Pra Daily Order (mapped qty) di UISS X8 / X12', 'X8 / X12', 'Dokumen', 'FID Rayhan', 'Konfirmasi no. 9', 'Waiting confirmation', 'High'),
    ('Isi jadwal & retry di Schedule sheet UISS X5, X9-X11', 'X5, X9-X11', 'Dokumen', 'FID Rayhan', 'Konfirmasi no. 10-12', 'Waiting confirmation', 'Medium'),
    ('Buat UISS-Batch RPA Sync (jika disetujui)', 'X3', 'Dokumen', 'FID Rayhan', 'Konfirmasi no. 16-17', 'Not started', 'Medium'),
    ('Lengkapi panjang VARCHAR dan nama field di Appendix semua UISS', 'X1-X13', 'Dokumen', 'FID Rayhan', 'Konfirmasi no. 20', 'Waiting confirmation', 'Low'),
    ('Review UISS X1-X13 versi 0.1 oleh user / reviewer', 'X1-X13', 'Review', 'User', '-', 'Not started', 'High'),
    ('Tambah kolom SERIAL_NO di tabel / query H0253 sumber', 'X10', 'Data', 'Tim DB Surrounding', 'Konfirmasi no. 15', 'Not started', 'High'),
    ('Tambah kolom HOLD_FLAG / PO_MAPPED_FLAG di H0253 NSP dan cara mempertahankannya saat sync', 'X10', 'Data', 'Tim NSP / IT', 'Konfirmasi no. 7', 'Not started', 'High'),
    ('Konfirmasi struktur tabel Pra Daily Order dan route master', 'X8, X12', 'Data', 'Tim NSP / IT', '-', 'Not started', 'High'),
    ('Prototype: Download Case Label sesuai format', 'X8 / X13', 'Prototype', 'FID Rayhan', 'Konfirmasi no. 1', 'Waiting confirmation', 'Medium'),
    ('Prototype: Cancel ASN di ASN Inquiry (jika diperlukan)', 'X13', 'Prototype', 'FID Rayhan', 'Konfirmasi no. 8', 'Waiting confirmation', 'Low'),
    ('Susun testing strategy & test scenario (unit, integration, UAT) X1-X13', 'X1-X13', 'Testing', 'FID Rayhan', 'UISS final', 'Not started', 'High'),
    ('Definisikan proses lanjutan setelah ASN (penerimaan di crossdock, pengiriman ke destinasi)', 'Next scope', 'Analisis', 'FID Rayhan / User', 'Arahan user', 'Not started', 'Medium'),
    ('Susun BRD / TSD (jika dibutuhkan proyek)', 'All', 'Dokumen', 'FID Rayhan', 'Arahan user', 'Not started', 'Low'),
]

DONE = [
    'UISS 13 fungsi (X1-X13) versi 0.1 + file .md per fungsi',
    'Prototype Part List, Mapping per Destination, ASN Crossdock Creation, ASN Inquiry (GitHub Pages)',
    'Rumus kalkulasi DAD (X6) dan mapping destinasi (X7) termasuk aturan pembulatan, dikonfirmasi 14-Oct-26',
    'Struktur tabel H0202 / H0253 / H0125 dari I/F layout G-TOPAS, termasuk SERIAL_NO',
    'Alur ASN baru sesuai ASN_Flow_Normal.xlsx (unit Part + Customer Order Date, 1 case per destinasi, FIFO)',
    'Header delivery plan level case; detail destinasi & pcs hanya untuk tim D/S',
    'ASN flow versi 15-Oct: Get Order (X12 on-demand pre-mapping), Hold Flag oleh D/S, Create ASN (mapping), status Ready / Not Ready / Created',
]
