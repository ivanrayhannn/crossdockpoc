# Batch – Crossdock – Actual Demand Sync, DAD Volume Calculation, Mapping Destination Calculation

Draft catatan 3 fungsi batch yang menghitung status part dan mapping destinasi.
Sumber: penjelasan user 13-Oct-26 dan file referensi `20261013_tb_r_actual_demand_summary_since_january-2026.xlsx` (sheet *tb_r_actual_demand_summary* dan *simulasi*).
Status: **draft**. UISS-Batch belum dibuat. Fungsi 3 masih menunggu konfirmasi rumus.

Urutan jalan setiap bulan: **Fungsi 1 → Fungsi 2 → Fungsi 3**.

---

## Fungsi 1 – Actual Demand Summary Sync to NSP

| Item | Keputusan |
|---|---|
| Tujuan | Menyalin TB_R_ACTUAL_DEMAND_SUMMARY dari DB Surrounding ke tabel yang sama di NSP |
| Cara simpan | **Delete – insert** (isi tabel NSP diganti semua setiap jalan) |
| Jadwal | Setiap bulan, **harus selesai sebelum Fungsi 2**. Jam/tanggal scheduler **TBC** |
| Gagal | TBD: apakah Fungsi 2 dibatalkan kalau Fungsi 1 gagal (usul: ya) |

Kolom TB_R_ACTUAL_DEMAND_SUMMARY (dari file referensi):

| Kolom | Contoh | Dipakai |
|---|---|---|
| GROUPING_BUYER_CD | 9722D | Fungsi 3 (destinasi) |
| GROUPING_PD_CD | 10 | Fungsi 3 (destinasi) |
| ORDER_TYPE_GROUP | N / S | TBD: apakah N dan S dijumlahkan (di simulasi: ya) |
| DEMAND_MONTH_YEAR | 202604 | Filter range bulan |
| PART_NO | 52119BZV60 | Join ke TB_M_PART_CANDIDATE |
| MAD | 239 | Fungsi 2 dan 3 |
| DAD | 0.05 | TBD: dipakai atau tidak |
| N01_QTY … N06_QTY, NUM_OF_OLD_PART_NO, NUM_OF_WORKINGDAY_6M, EM_MS_FLAG | | Tidak dipakai Crossdock (info) |
| CREATE_DT / CREATE_BY / UPDATE_DT / UPDATE_BY | | Audit |

---

## Fungsi 2 – DAD Volume Calculation Batch

### Alur
1. Ambil TB_R_ACTUAL_DEMAND_SUMMARY (NSP), **range bulan historis sebelum bulan berjalan** (jumlah bulan diatur di system master, misalnya 6).
2. Join ke **TB_M_PART_CANDIDATE**: semua part yang terdaftar, apa pun statusnya (Candidate, Active, Inactive).
3. Part yang **Effective Start Date-nya belum tiba tidak dihitung**.
4. Hitung **rata-rata MAD per part** selama range bulan. Hasilnya disimpan ke tabel hasil (usulan nama TB_R_PART_DAD_RESULT).
5. Bandingkan dengan **Min MAD** di TB_M_PART_CANDIDATE:
   - rata-rata ≥ Min MAD → **Active**
   - rata-rata < Min MAD → **Inactive**
   - Perpindahan yang mungkin: Candidate → Active / Inactive, Inactive → Active, Active → Inactive.
6. Perubahan status dicatat di TB_H_PART_CANDIDATE (usulan: event **CALC**, source **BATCH**).

### Aturan
- **All-or-nothing**: kalau ada yang gagal, semua dibatalkan.
- Scheduler diatur di system master, **auto retry 3x**.
- Tombol **trigger manual** di Part List, hanya aktif kalau 3x retry gagal.
- **Last success date** disimpan dan ditampilkan sebagai kolom tambahan di Part List.
- **Sync Status**: perubahan status oleh batch ini **tidak** membuat part jadi No Sync. No Sync hanya dipicu oleh perubahan **Pcs/Case, Max Case/Day, atau mapping destinasi**.

### Contoh (part 52119BZV60, range 6 bulan 202604–202609)
MAD part per bulan = jumlah MAD semua buyer / PD / order type di bulan itu:

| 202604 | 202605 | 202606 | 202607 | 202608 | 202609 | Rata-rata |
|---|---|---|---|---|---|---|
| 498.67 | 473.83 | 498.32 | 521.17 | 572.16 | 526.34 | **515.08** |

Jika Min MAD = 500 → Active. Jika Min MAD = 600 → Inactive.

### Usulan tabel hasil TB_R_PART_DAD_RESULT
| Kolom | Keterangan |
|---|---|
| PERIOD (PK) | Periode kalkulasi YYYYMM |
| PART_NO (PK) | Part number |
| MONTH_FROM / MONTH_TO | Range bulan yang dihitung |
| AVG_MAD | Rata-rata MAD hasil kalkulasi |
| MIN_MAD | Min MAD saat dihitung (snapshot) |
| OLD_STATUS / NEW_STATUS | Status sebelum dan sesudah |
| CREATED_BY / CREATED_DT | Audit |

### Masih terbuka
- Bulan yang tidak ada datanya: dihitung 0 atau dilewati?
- Kalau user mengubah status manual di Part List, apakah batch berikutnya boleh menimpanya?
- Kolom "last success date" di Part List: satu tanggal untuk seluruh batch (ditampilkan di atas tabel), atau per part?
- Aturan No Sync di atas berarti Save di Part List yang hanya mengubah status/Min MAD/Effective Start Date juga **tidak** membuat No Sync. Sekarang UISS Part List menulis "setiap Save → No Sync". Perlu diubah?

---

## Fungsi 3 – Calculation Mapping Destination

### Alur (sesuai sheet *simulasi*)
1. Ambil TB_R_ACTUAL_DEMAND_SUMMARY, range bulan, hanya part **Active** di TB_M_PART_CANDIDATE.
2. Kelompokkan per part + **GROUPING_BUYER_CD** (+ GROUPING_PD_CD), jumlahkan MAD → *result MAD*.
3. Urutkan *result MAD* dari terbesar ke terkecil.
4. Case/Day destinasi = result MAD / Σ result MAD part × **Max Case/Day**.
5. Destinasi (buyer code) dicek ke **TB_M_H0125**, lalu disimpan ke TB_M_PART_CANDIDATE_DEST untuk periode baru.

### Kenapa hasilnya melebihi Max Case/Day
Rumus di sheet *simulasi* kolom L memakai referensi relatif, jadi penyebutnya bergeser setiap baris:

| Baris | Rumus di file | Penyebut yang benar |
|---|---|---|
| L10 (96182) | P10/(P10+P11+P12+P13) | sama |
| L11 (98111) | P11/(P11+P12+P13+**P14**) | P10+P11+P12+P13 |
| L12 (9722D) | P12/(P12+P13+**P14+P15**) | P10+P11+P12+P13 |
| L13 (97153) | P13/(P13+**P14+P15+P16**) | P10+P11+P12+P13 |

P14–P16 kosong, jadi penyebut makin kecil dan rasio makin besar. Hasilnya total 39.31, padahal Max Case/Day 16.

| Buyer | Result MAD | Hasil file | Rasio benar × 16 | Dibulatkan |
|---|---|---|---|---|
| 9722D | 2,070.16 | 14.99 | 8.02 | 8 |
| 98111 | 1,309.50 | 5.95 | 5.07 | 5 |
| 96182 | 609.99 | 2.36 | 2.36 | 2 |
| 97153 | 139.34 | 16.00 | 0.54 | 1 |
| **Total** | 4,128.99 | **39.31** | **16.00** | **16** |

**Usulan perbaikan**
- Penyebut dikunci ke total semua buyer part itu: `=P10/SUM($P$10:$P$13)*$N$10`.
- Case/Day harus bilangan bulat. Usul metode *largest remainder*: bulatkan ke bawah, sisa case dibagikan +1 ke destinasi dengan pecahan terbesar. Dengan cara ini total selalu sama dengan Max Case/Day.

### Catatan lain dari simulasi
- SUMIF di kolom P menjumlahkan **semua bulan** (202603–202610, 8 bulan) dan **semua order type (N + S)**, belum memakai filter range bulan.
- SUMIF hanya per buyer code. PD code belum ikut dikelompokkan, padahal penjelasan menyebut buyer code + PD code distinct.
- Rasio dari jumlah total dan dari rata-rata hasilnya sama, selama semua buyer dihitung pada range bulan yang sama.

### Masih terbuka
- Konfirmasi rumus (penyebut dan pembulatan) — **menunggu user**.
- Destination Code di TB_M_H0125 = buyer code saja, atau buyer code + PD code?
- Buyer code yang tidak ada di TB_M_H0125: dilewati atau error?
- Buyer dengan rasio sangat kecil (mis. 0.54 case): tetap dapat 1 case, atau dibuang kalau di bawah batas tertentu?
- Apakah Fungsi 3 yang membuat periode baru di TB_M_PART_CANDIDATE_DEST?
