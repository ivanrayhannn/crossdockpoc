# Batch – Crossdock – Actual Demand Sync, DAD Volume Calculation, Mapping Destination Calculation

Draft catatan 3 fungsi batch yang menghitung status part dan mapping destinasi.
Sumber: penjelasan user 13-Oct-26 dan file referensi `20261013_tb_r_actual_demand_summary_since_january-2026.xlsx` (sheet *tb_r_actual_demand_summary* dan *simulasi*).
UISS-Batch (0.1 Initial Draft): **X6** `UISS_Batch_ActualDemandSummarySync.xlsx`, **X7** `UISS_Batch_DADVolumeCalculation.xlsx`, **X8** `UISS_Batch_MappingDestinationCalculation.xlsx`. Rumus dan aturan dikonfirmasi 14-Oct-26.

> Range bulan dan jadwal scheduler diatur di **system master** (tabel system master tidak dijelaskan di dokumen ini).

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
4. Hitung **rata-rata MAD per part** (disimpan 2 desimal, dibandingkan apa adanya) = total MAD ÷ **jumlah bulan di system master** (mis. 6). Pembagi selalu tetap, bulan tanpa data dihitung 0. Hasilnya disimpan ke tabel hasil (usulan nama TB_R_PART_DAD_RESULT).
5. Bandingkan dengan **Min MAD** di TB_M_PART_CANDIDATE:
   - rata-rata ≥ Min MAD → **Active**
   - rata-rata < Min MAD → **Inactive**
   - Perpindahan yang mungkin: Candidate → Active / Inactive, Inactive → Active, Active → Inactive.
6. Perubahan status dicatat di TB_H_PART_CANDIDATE (event **CALC**, source **BATCH**).

### Aturan
- **All-or-nothing**: kalau ada yang gagal, semua dibatalkan.
- **Status manual**: batch boleh menimpa status yang sebelumnya diubah manual. User tetap boleh mengubah status lagi lewat layar / upload setelah batch jalan (di luar kendali sistem).
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

### Tabel hasil TB_R_PART_DAD_RESULT (usulan nama, lihat Appendix UISS X7)
| Kolom | Keterangan |
|---|---|
| PERIOD (PK) | Periode kalkulasi YYYYMM |
| PART_NO (PK) | Part number |
| MONTH_FROM / MONTH_TO | Range bulan yang dihitung |
| AVG_MAD | Rata-rata MAD hasil kalkulasi |
| MIN_MAD | Min MAD saat dihitung (snapshot) |
| OLD_STATUS / NEW_STATUS | Status sebelum dan sesudah |
| CREATED_BY / CREATED_DT | Audit |

### Contoh bulan tanpa data (range 6 bulan)
Part B hanya punya data 4 bulan, masing-masing 600 → rata-rata = 2,400 ÷ **6** = **400** (bukan ÷ 4).

---

## Fungsi 3 – Calculation Mapping Destination

### Alur
1. Ambil TB_R_ACTUAL_DEMAND_SUMMARY, **range bulan dari system master**, hanya part **Active** di TB_M_PART_CANDIDATE. Order type N dan S dijumlahkan.
2. Kelompokkan per part + **GROUPING_BUYER_CD + GROUPING_PD_CD**, jumlahkan MAD → *result MAD*.
3. **Destination code** = GROUPING_BUYER_CD + GROUPING_PD_CD (7 digit, mis. `9722D` + `10` = `9722D10`). Cek ke Destination Code **TB_M_H0125**. Tidak ada di master → **error**.
4. Urutkan *result MAD* dari terbesar ke terkecil.
5. **Dibatasi Max Case/Day**: kalau jumlah destinasi lebih banyak dari Max Case/Day, hanya destinasi teratas (result MAD terbesar) sebanyak Max Case/Day yang dipakai; sisanya tidak di-mapping.
6. Case/Day destinasi = result MAD / Σ result MAD destinasi terpakai × **Max Case/Day**. Rumus Excel: `=P10/SUM($P$10:$P$13)*$N$10`.
7. Pembulatan (lihat di bawah); setiap destinasi **minimal 1 case**, total = Max Case/Day.
8. **Membuat periode baru** di TB_M_PART_CANDIDATE_DEST dan menyimpan mapping hasil kalkulasi. Periode sebelumnya jadi periode lalu (read only).
9. **All-or-nothing**: satu error (mis. destinasi tidak ada di master) → seluruh batch gagal, tidak ada yang disimpan.
10. **Scheduler sendiri** (diatur di system master), **auto retry 3x**, tombol **trigger manual di sub-menu Mapping per Destination**, aktif kalau 3x retry gagal; last success date disimpan dan ditampilkan di sub-menu itu.

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

**Pembulatan (dikonfirmasi 14-Oct-26)**: Case/Day harus bilangan bulat dan totalnya sama dengan Max Case/Day.
1. Target = result MAD / Σ result MAD × Max Case/Day (destinasi teratas, maks. sebanyak Max Case/Day).
2. Case/Day = target dibulatkan ke bawah, **minimal 1**.
3. Total masih kurang dari Max Case/Day → +1 ke destinasi dengan pecahan terbesar (pecahan sama: result MAD lebih besar dulu).
4. Total lebih dari Max Case/Day (karena minimal 1) → −1 dari destinasi dengan pecahan terkecil yang masih punya lebih dari 1 case.

Contoh: Max 5, MAD 900 / 50 / 30 / 20 → target 4.50 / 0.25 / 0.15 / 0.10 → 4 / 1 / 1 / 1 = 7 → dikurangi jadi **2 / 1 / 1 / 1** = 5.

Pembulatan biasa (0.1–0.4 ke bawah, 0.5–0.9 ke atas) tidak dipakai sendirian karena totalnya bisa melenceng. Contoh: Max Case/Day 10, 4 destinasi masing-masing 2.5 → dibulatkan 3 + 3 + 3 + 3 = 12. Dengan cara di atas hasilnya 3 + 3 + 2 + 2 = 10.

Contoh dengan range 6 bulan (202604–202609), Max Case/Day 16:

| Destination code | Result MAD (6 bulan) | Rasio × 16 | Case/Day |
|---|---|---|---|
| 9722D10 | 1,536.16 | 7.95 | 8 |
| 9811110 | 999.83 | 5.18 | 5 |
| 9618201 | 448.66 | 2.32 | 2 |
| 9715310 | 105.84 | 0.55 | 1 |
| **Total** | 3,090.49 | 16.00 | **16** |

### Catatan dari simulasi (sudah diputuskan)
- SUMIF di file menjumlahkan semua 8 bulan → di batch dipakai **range bulan dari system master**.
- SUMIF di file hanya per buyer code → di batch dikelompokkan per **buyer code + PD code**.
- Rasio dari jumlah total dan dari rata-rata hasilnya sama, selama semua buyer dihitung pada range bulan yang sama.
