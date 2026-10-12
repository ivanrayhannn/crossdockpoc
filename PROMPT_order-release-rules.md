# Prompt: Terapkan business rules Order Release di Case Consolidation Simulation

## Konteks
Menu **Case Consolidation Simulation** (`app/src/features/caseConsolidation/`) mensimulasikan bagaimana
customer order menjadi case, lalu dirilis ke supplier PO per hari. Logika murninya ada di
`simulation.ts` (`buildModel`, `buildSequences`). Hasilnya dipakai oleh `deliveryPlan.ts`, `visual.ts`,
`useCaseSimulation.ts`, `OptionsBar.tsx`, `VisualSimulationTab.tsx`, `DeliveryPlanTab.tsx`, dan teks
penjelasan di `CaseConsolidationPage.tsx`.

Business rules di bawah sudah disetujui. Tugasmu: ubah simulasi supaya perilakunya sama dengan rules ini,
dan sesuaikan UI serta teks penjelasannya. Jangan mengubah hal lain di luar cakupan ini.

## Business rules (sumber kebenaran)

### A. Pembentukan case
- **OR-01** Customer order dikelompokkan berdasarkan Customer Order Date dan destination.
- **OR-02** Qty setiap order selalu **kelipatan Pcs/Case**, jadi order langsung menjadi case penuh.
  **Tidak ada pcs sisa dan tidak ada carry-over.**
- **OR-03** Satu case hanya berisi **satu destination**. Aturan ini berlaku juga di ASN Creation.
- **OR-04** Satu case hanya punya satu Customer Order Date.

### B. Pelepasan PO
- **OR-05** Satu PO supplier dirilis otomatis per hari, berisi semua part dan semua destination.
- **OR-06** PO Date = Customer Order Date + 1.
- **OR-07** Untuk setiap part, PO maksimal berisi **Max Case/Day** case dari part itu. **Max Case/Day
  berlaku per part**; part berbeda punya batas sendiri.
- **OR-08** Untuk setiap part, case tersedia = backlog part itu dari hari sebelumnya + case baru part itu.
  PO mengambil yang lebih kecil antara jumlah itu dan Max Case/Day part tersebut.
- **OR-09** Part tanpa case tersedia tidak masuk PO hari itu. Jika semua part kosong, tidak ada PO hari itu.
- **OR-10** Case di atas batas part masuk **backlog FIFO per part** dan masuk PO berikutnya lebih dulu.
  Backlog satu part tidak memakai kuota part lain.
- **OR-11** Perubahan Max Case/Day suatu part hanya berlaku untuk PO yang belum dirilis.
- **OR-12** Rilis berjalan setiap hari **tanpa tanggal akhir**. Order date di simulasi hanyalah data dummy.
  Sisa backlog dirilis di hari berikutnya, atau ditangani dengan manual PO.

### C. Status per order date
- **OR-13** **Ready to ASN** jika semua order (semua part) pada tanggal itu sudah dipasangkan dengan PO.
- **OR-14** Selain itu **Waiting Released**; ASN belum bisa dibuat.
- **OR-15** Satu tanggal bisa tersebar di beberapa PO. Satu ASN mencakup tepat satu order date beserta
  seluruh case-nya.
- **OR-16** Case yang sudah masuk ASN terkunci.

## Perilaku saat ini yang harus berubah
Baca `simulation.ts` dulu, lalu pastikan perbedaan berikut tertangani:

1. **Carry-over pcs sisa** (`carry`, `pending` yang berisi pcs lepas). Hapus. Dengan OR-02 tidak ada pcs
   sisa. Order yang bukan kelipatan Pcs/Case harus ditolak atau dibulatkan di input (lihat langkah 4).
2. **Satu `maxC` untuk semua PO dan satu antrean backlog bersama.** Ganti menjadi batas dan antrean
   backlog **per part** (OR-07, OR-08, OR-10). Key part memakai `partNoOf(order)`.
3. **Rilis berhenti di `end = addDay(dates terakhir)`.** Ubah agar rilis berlanjut sampai semua case
   terkirim (OR-12), tanpa loop tak terbatas. Beri batas pengaman yang jelas (mis. berhenti saat antrean
   kosong) dan jelaskan pilihanmu.
4. **Input order di UI** (`OptionsBar.tsx`, `useCaseSimulation.ts`: `updateOrder`, `addOrder`,
   `setPcs`): qty order bergerak dalam langkah Pcs/Case dan minimal 1 case. Saat Pcs/Case berubah, qty
   order disesuaikan agar tetap kelipatan.
5. **Preset** di `PRESETS` / `SEED`: preset `b` memakai qty yang bukan kelipatan 6 (2, 4, 1, 5, 3 ...).
   Ubah ke kelipatan Pcs/Case tanpa mengubah bentuk skenarionya (3 destination, beberapa tanggal, ada
   antrean). Periksa juga preset lain.
6. **Teks penjelasan** di `CaseConsolidationPage.tsx` dan `OptionsBar.tsx`: tulis ulang sesuai rules di
   atas, termasuk "Max Case/Day per part" dan "tidak ada carry-over".
7. **Tampilan**: `visual.ts` (`calc`, `splitText`, remaining/pending), `VisualSimulationTab.tsx`, dan
   `deliveryPlan.ts` harus menampilkan angka per part yang benar (cap, backlog, case dirilis). Teks yang
   menyebut "remaining pcs" disesuaikan, karena yang tersisa sekarang adalah **case**, bukan pcs.

## Keputusan desain (sudah ditetapkan)
- Input batas: tambahkan `partCap: Record<string, number>` di `SimInputs`. `maxC` yang ada menjadi default
  untuk part yang belum punya nilai sendiri. Sediakan kontrol UI untuk mengubahnya per part, dan tetap
  dalam rentang yang sudah dipakai stepper sekarang (1 sampai 6).
- `capOv` (override per tanggal PO) tetap ada sebagai alat testing. Ia **menggantikan** batas semua part
  pada tanggal PO itu. Beri label jelas di UI bahwa ini untuk testing saja.
- Dengan OR-02, setiap baris order menghasilkan case penuh dan satu case berisi satu baris order, sehingga
  satu case milik **satu part**. Hitung kuota part memakai part dari case tersebut. Jika nanti ada case
  yang berisi lebih dari satu part, tulis di laporan akhir bahwa ini belum ditangani.
- Urutan FIFO: order date, lalu urutan destination yang sudah ada (VN, JP, TH), lalu id order.

## Pertanyaan yang belum dijawab (jangan menebak diam-diam)
Apakah alokasi per destination di menu Mapping per Destination (Thailand/Japan/Vietnam) juga menjadi
batas rilis, atau hanya total Max Case/Day per part yang berlaku saat PO dirilis?
**Default untuk tugas ini: hanya total per part yang berlaku.** Jangan membangun batas per destination.
Tulis di laporan akhir bahwa ini asumsi, dan sebutkan bagian kode yang perlu diubah bila jawabannya
ternyata "ya".

## Di luar cakupan
- Jangan ubah `features/asnCreation/`, kecuali komentar di `data.ts` yang menyebut "never mixes parts or
  destinations": ubah menjadi "never mixes destinations".
- Jangan ubah menu Crossdock Master Setting dan Batch Process Simulation.
- Jangan tambah dependency baru.

## Cara memverifikasi
Proyek ini belum punya test runner. Jangan menambahkannya hanya untuk tugas ini.
1. Jalankan `npm run lint` dan `npm run build` di folder `app/`. Keduanya harus bersih.
2. Tulis skrip sementara (di luar repo, atau hapus setelah dipakai) yang memanggil `buildModel` dengan
   skenario berikut dan cetak per hari: available, take, left, dan PO yang terbentuk:
   - **S1** Satu part, Pcs/Case 6, cap 2, tiga order date masing-masing 3 case. Harapan: hari 1 rilis 2
     (backlog 1), hari 2 rilis 2 (backlog 2 setelah case baru: tersedia 4, ambil 2), dst. Backlog
     dirilis lebih dulu dan tidak ada case hilang.
   - **S2** Dua part dengan cap berbeda (mis. 1 dan 3) pada hari yang sama. Harapan: backlog satu part
     tidak memakai kuota part lain.
   - **S3** Satu hari tanpa case sama sekali. Harapan: tidak ada PO hari itu.
   - **S4** Order date terakhir dengan backlog tersisa. Harapan: rilis tetap berlanjut sampai antrean
     kosong.
   - **S5** Order date dengan dua part, satu part terkena batas. Harapan: tanggal itu `Waiting Released`
     sampai case part tersebut masuk PO.
3. Jalankan app (`npm run dev`), buka Case Consolidation Simulation, ganti tiap preset, tekan play, lalu
   cek tiga tab (Delivery Plan, Visual Simulation, ASN Draft). Pastikan tidak ada angka negatif, case
   yang hilang, atau teks lama yang masih menyebut carry-over atau pcs sisa.

## Laporan akhir
Singkat dan jujur: apa yang diubah (per file), hasil lint/build, hasil S1 sampai S5 (angka sebenarnya),
asumsi yang kamu ambil, dan hal yang belum dikerjakan. Jangan menyatakan "selesai" bila ada skenario yang
belum dijalankan.
