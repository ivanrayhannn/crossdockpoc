# Batch – Crossdock – Actual Demand Sync, DAD Volume Calculation, Mapping Destination Calculation

Draft catatan 3 fungsi batch yang menghitung status part dan mapping destinasi.
Sumber: penjelasan user 13-Oct-26 dan file referensi `20261013_tb_r_actual_demand_summary_since_january-2026.xlsx` (sheet *tb_r_actual_demand_summary* dan *simulasi*).
Status: **draft**. UISS-Batch belum dibuat. Rumus Fungsi 3 sudah dikonfirmasi 14-Oct-26; aturan pembulatan masih perlu konfirmasi.

> Range bulan dan jadwal scheduler diatur di **system master** (tabel system master tidak dijelaskan di dokumen ini).

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
| ORDER_TYPE_GROUP | N / S | N dan S **dijumlahkan** (sementara) |
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
- **Last success date**: satu tanggal per batch run (karena all-or-nothing, semua part ikut berhasil atau gagal bersama). Ditampilkan di Part List.
- **Sync Status**: perubahan status oleh batch ini **tidak** membuat part jadi No Sync. Di layar Part List, **setiap Save** tetap membuat No Sync (tidak berubah).

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

---

## Fungsi 3 – Calculation Mapping Destination

### Alur
1. Ambil TB_R_ACTUAL_DEMAND_SUMMARY, **range bulan dari system master**, hanya part **Active** di TB_M_PART_CANDIDATE. Order type N dan S dijumlahkan.
2. Kelompokkan per part + **GROUPING_BUYER_CD + GROUPING_PD_CD**, jumlahkan MAD → *result MAD*.
3. Urutkan *result MAD* dari terbesar ke terkecil.
4. Cek setiap buyer code + PD code ke **TB_M_H0125** (Destination Code + PD code). Tidak ada di master → **error**.
5. Case/Day destinasi = result MAD / Σ result MAD part × **Max Case/Day** (**dikonfirmasi**). Rumus Excel: `=P10/SUM($P$10:$P$13)*$N$10`.
6. Setiap destinasi **tetap mendapat minimal 1 case**, walau porsinya kecil.
7. Simpan ke TB_M_PART_CANDIDATE_DEST untuk periode baru.

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

**Perbaikan (dikonfirmasi)**: penyebut dikunci ke total semua buyer + PD part itu: `=P10/SUM($P$10:$P$13)*$N$10`.

**Usulan pembulatan (perlu konfirmasi)**: Case/Day harus bilangan bulat dan totalnya sama dengan Max Case/Day.
1. Setiap destinasi diberi 1 case dulu (aturan minimal 1 case).
2. Sisa case (Max Case/Day − jumlah destinasi) dibagi sesuai rasio, dibulatkan ke bawah.
3. Case yang masih tersisa dibagikan +1 ke destinasi dengan pecahan terbesar.

Contoh dengan range 6 bulan (202604–202609), Max Case/Day 16:

| Buyer + PD | Result MAD (6 bulan) | Rasio × 16 | Case/Day |
|---|---|---|---|
| 9722D-10 | 1,536.16 | 7.95 | 8 |
| 98111-10 | 999.83 | 5.18 | 5 |
| 96182-01 | 448.66 | 2.32 | 2 |
| 97153-10 | 105.84 | 0.55 | 1 |
| **Total** | 3,090.49 | 16.00 | **16** |

### Catatan dari simulasi (sudah diputuskan)
- SUMIF di file menjumlahkan semua 8 bulan → di batch dipakai **range bulan dari system master**.
- SUMIF di file hanya per buyer code → di batch dikelompokkan per **buyer code + PD code**.
- Rasio dari jumlah total dan dari rata-rata hasilnya sama, selama semua buyer dihitung pada range bulan yang sama.

### Masih terbuka
- Aturan pembulatan di atas.
- Jumlah destinasi lebih banyak dari Max Case/Day (minimal 1 case tidak bisa dipenuhi): error atau dibatasi?
- PD code: kolom mana di TB_M_H0125 (belum ada di daftar kolom yang diterima)? Apakah TB_M_PART_CANDIDATE_DEST perlu kolom PD code, karena satu buyer bisa punya lebih dari satu PD code?
- Error buyer tidak ada di master: seluruh batch gagal (all-or-nothing seperti Fungsi 2)?
- Apakah Fungsi 3 yang membuat periode baru di TB_M_PART_CANDIDATE_DEST?
