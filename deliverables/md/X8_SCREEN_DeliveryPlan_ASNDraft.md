# Screen – Case Consolidation – Delivery Plan & ASN Draft (X8)

Ringkasan poin-poin layar Delivery Plan dan ASN Draft (satu UISS): tujuan, mode layar, aturan pilih tanggal, Submit ASN, pesan, dan data yang terlibat.
Sumber: UISS-Screen `X8_UISS_Screen_DeliveryPlan_ASNDraft.xlsx` (0.1 Initial Draft). Menggantikan dua UISS terpisah sebelumnya (Delivery Plan dan ASN Draft).
Prototype: menu **Case Consolidation Simulation** (tab Delivery Plan → ASN Draft).

---

## 1. Tujuan
- Menampilkan rencana kirim per **Customer Order Date** beserta status (Ready to ASN / Waiting Released), jumlah case & pcs, nomor PO supplier, dan ASN Number kalau sudah dibuat ASN.
- Menampilkan detail baris customer order untuk satu tanggal (Detail in Detail).
- Memilih **satu** tanggal Ready to ASN lalu membuka ASN Draft, supaya semua case tanggal itu digabung jadi **satu ASN**.
- Mengisi Delivery Date dan Rit, **Submit ASN** (semua case dikunci), lalu menampilkan ASN yang sudah submit (read only).

## 2. Alur layar
```
Delivery Plan Header ──View detail──▶ Detail in Detail ──Back──▶ Delivery Plan Header
        │
        └─Group into 1 ASN──▶ ASN Draft ──Submit ASN──▶ ASN Submitted ──Back──▶ Delivery Plan Header
                                  └─Cancel / Back──▶ Delivery Plan Header
```

## 3. Mode layar
| No | Mode | Isi |
|---|---|---|
| 1 | List Mode – No Selection | Kriteria kosong (Status = All), semua tanggal tampil, belum ada yang dicentang |
| 2 | List Mode – Date Selected | Satu tanggal Ready to ASN dicentang; Selection Bar aktif (Clear selection, Group into 1 ASN) |
| 3 | Detail Mode | Ringkasan tanggal + daftar baris customer order (read only) |
| 4 | ASN Draft Mode | Delivery Date & Rit bisa diisi; daftar case read only; Cancel / Submit ASN |
| 5 | ASN Submitted Mode | ASN No di judul, badge Submitted, semua read only, footer disembunyikan |

## 4. Delivery Plan Header
**Kriteria**: Customer Order Date From–To, Status (All / Ready to ASN / Waiting Released). Tombol Search dan Reset.

**Kolom**: check box, Customer Order Date, ASN Number, Status, Cases ("{n} cases · {pcs} pcs", plus "{k} pcs not released"), View detail. Counter: Dates, Ready, Waiting.

**Aturan status**
| Status | Arti | Check box | View detail |
|---|---|---|---|
| Ready to ASN | Semua order tanggal itu sudah dipasangkan ke PO supplier (case penuh, sudah di-release) | Aktif | Aktif |
| Ready to ASN, sudah di ASN | Semua case sudah masuk ASN | Tercentang, terkunci | Aktif |
| Waiting Released | Masih ada order / sisa pcs yang belum punya PO (baris kuning) | Disabled | Aktif |

**Pilih tanggal**
- Hanya **1 tanggal** boleh dicentang: **1 ASN = 1 Customer Order Date**. Tanggal yang terdiri dari beberapa PO ikut semua, tidak bisa dipecah.
- Selama satu tanggal dicentang, check box tanggal lain disabled (MSG3).
- Selection Bar menampilkan tanggal, jumlah case/pcs, nomor PO. **Group into 1 ASN** → ASN Draft.
- View detail disembunyikan untuk akun **Supplier** (TBD konfirmasi aturan role).
- From > To: hasil kosong + MSG4 (validasi khusus TBD).

## 5. Detail in Detail
- Ringkasan: tanggal, status, PO supplier, ringkasan case.
- Grid: Customer Order (titik warna per order), Destination, Customer Order Date, Customer Qty, Part No, Qty, PO No, PO Date, Case No.
- Urutan: baris yang sudah masuk case (urut PO) dulu, lalu baris **Waiting** (belum ada PO; PO No/Date "-", Case No badge "Waiting", baris disorot).
- Satu order bisa muncul di beberapa baris (terpecah ke beberapa case/PO). Tidak ada baris → MSG5. Hanya tampilan.

## 6. ASN Draft
**Tampilan awal**
- Daftar case = semua case tanggal yang dipilih, lintas PO, 1 baris per case + Part No. Tidak bisa tambah/kurang case.
- ASN No otomatis dari Delivery Date (`ASN-{Supplier}-{YYMMDD}-{Seq}`), baru ditetapkan saat submit (aturan nomor urut TBD).
- Delivery Date default **besok**; Rit = daftar Rit di tanggal itu (default Rit pertama); Route mengikuti Rit.
- Alert informasi selalu tampil (MSG9). Tidak ada case → MSG8.

**Delivery Date & Rit**
- Ganti Delivery Date → daftar Rit dimuat ulang; Rit sebelumnya dipertahankan kalau masih ada.
- **Minggu tidak ada Rit** ("No rit", Submit disabled, MSG7). **Sabtu hanya 1 Rit**.

**Submit ASN**
1. Ditolak kalau case bukan semua case satu tanggal, tanggal bukan Ready to ASN, atau Delivery Date / Rit kosong (pesan TBD).
2. ASN No dibuat dari Delivery Date.
3. Semua case tanggal itu **dikunci** ke ASN; ASN Header & Detail disimpan.
4. Pindah ke **ASN Submitted Mode** (MSG6), field read only, Cancel / Submit disembunyikan.
5. Di Delivery Plan, tanggal itu tampil terkunci dengan ASN Number.

**Download All Case Labels**: aktif kalau daftar case tidak kosong; format label **TBD**.

---

## 7. Data yang terlibat
Layar Delivery Plan dan Detail in Detail **hanya menampilkan** data. Penyimpanan hanya saat Submit ASN.

| Data | Dipakai | Nama tabel |
|---|---|---|
| Customer Order | Tanggal, order, Part No, qty, destinasi | TBD |
| Supplier PO | PO No, PO Date | TBD |
| Case | Case No, isi case | TBD |
| Route Master | Rit dan Route per Delivery Date | TBD (sekarang data dummy) |
| Supplier Master | Supplier · Plant | TBD |
| **ASN Header** – *ditulis* | ASN No, Delivery Date, Rit, Route, Supplier · Plant, Created By/Date | TBD |
| **ASN Detail** – *ditulis* | ASN No, Case No, PO No, Part No, Qty (1 baris per case + Part No) | TBD |

Customer order, PO supplier, dan case dibuat oleh proses PO release (di luar lingkup UISS ini).

## 8. Pesan layar
| ID | Kapan | Pesan |
|---|---|---|
| MSG1 | Hover check box, semua case sudah di ASN | Already in an ASN |
| MSG2 | Hover check box, Waiting Released | Waiting Released: some orders of this date are not paired with a PO yet |
| MSG3 | Hover check box, tanggal lain sudah dicentang | One ASN = one Customer Order Date. Clear the current selection first |
| MSG4 | Search tanpa hasil | No delivery plan matches this search. |
| MSG5 | View detail tanpa baris | No order lines for this Customer Order Date. |
| MSG6 | Submit ASN sukses | {ASN No} submitted. {n} cases are locked. Delivery {Delivery Date}. |
| MSG7 | Tidak ada Rit (Minggu) | No rit available for {Delivery Date}. Choose another delivery date. |
| MSG8 | Draft tanpa case | No cases in this ASN. Go back and select at least one case. |
| MSG9 | Info di Draft Mode | One ASN = one Customer Order Date. All {n} cases of order date {date} ({PO list}) are included and cannot be split into another ASN. |

Logging: LOG1 (gagal simpan ASN).

## 9. Open points
- Nama tabel fisik semua data di atas (Customer Order, Supplier PO, Case, ASN Header/Detail, Route Master, Supplier Master).
- Aturan nomor urut ASN No; format dan isi label (Download All Case Labels).
- Validasi From > To; pesan saat Submit ditolak.
- Aturan role untuk View detail (Supplier vs D/S vs Procurement).
