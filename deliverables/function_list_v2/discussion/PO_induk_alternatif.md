# Diskusi (parkir): PO Number sebagai induk, customer order sebagai child

Status: **belum diputuskan** (20-Oct-26). Desain berjalan tetap: customer order line → PO (`#TEMP_INSTRUCTION`, `TB_R_INSTRUCTION`, `TB_R_PRA_DAILY_ORDER_MAPPED`). Dokumen (UISS, ERD, BPF, simulasi) belum diubah.

## Struktur
```
PO line (induk)                       → 1 baris per MANIFEST_NO + MANIFEST_ITEM (ORDER_QTY, ALLOCATED_QTY = jumlah child, OPEN_QTY)
 └─ Customer order allocation (child) → 1 baris per customer order line × case (CO key, QTY, CASE_SEQ, ASN_NO / CASE_NO setelah submit)
```
Induk menggantikan `TB_R_PRA_DAILY_ORDER_MAPPED`; child menggantikan `TB_R_INSTRUCTION`.

## SIM-2 (normal)
Induk: PO-0008 / MF-0008 / 0001 PART-X 12-12-0 · PO-0009 / MF-0009 PART-X 12-12-0 · PO-0010 / MF-0010 PART-Y 6-6-0

| Induk | Customer Order | Dest | QTY | Case |
|---|---|---|---|---|
| PO-0008 | CO-14101 | KR | 6 | 1 |
| | CO-14101 | KR | 4 | 2 |
| | CO-14102 | KR | 2 | 2 |
| PO-0009 | CO-14102 | KR | 2 | 3 |
| | CO-14103 | KR | 4 | 3 |
| | CO-14104 | JP | 6 | 4 |
| PO-0010 | CO-14105 | TW | 6 | 5 |

## Customer order tanpa PO (SIM-3)
Opsi: A dihitung (qty H0253 − jumlah child) · B induk dummy UNASSIGNED · C tabel pending · D hanya di tabel sementara saat Search.
**Usulan: A + D**: child permanen hanya dibuat saat Create ASN untuk unit Ready (unit utuh, A2), jadi child tidak pernah berisi order tanpa PO. Order tanpa PO hanya ada di `#TEMP` (PO kosong, MSG2) dan sebagai open order hasil hitung. Cancel order tanpa PO tidak melepas apa pun.

15-Oct: CO-14104 (JP 6) tanpa induk → unit Not Ready, tabel induk-child permanen kosong. 16-Oct: PO PO-0013 (6) masuk → Search → Ready → Create ASN: induk PO-0008 12/12, PO-0009 6/6, PO-0013 6/6; child CO-14104 6 di PO-0013 case 4.

## Perbandingan singkat
| Aspek | Sekarang | PO induk |
|---|---|---|
| Mapped qty per PO | Tabel `TB_R_PRA_DAILY_ORDER_MAPPED` | Di induk (jumlah child) |
| Order tanpa PO | Baris PO kosong di pre-mapping | Tidak disimpan; dihitung |
| ASN existing (per manifest) | Dikelompokkan saat submit | Lebih natural |
| Case per destinasi | Dari line per destinasi | Sama; `CASE_SEQ` di child (case bisa lintas PO) |
| Cancel (XD11) | Cari by key CO | Sama; kurangi ALLOCATED_QTY induk |

## Keputusan terbuka
1. PO baru selalu ke open order terlama (FIFO Customer Order Date)?
2. Perlu daftar open order (order tanpa PO) di luar layar ASN (view / report / tabel pending)?
3. Sisa PO tetap di induk sebagai OPEN_QTY untuk order berikutnya (sama dengan sekarang).
4. Kalau dipilih: gabung `TB_R_INSTRUCTION` + `TB_R_PRA_DAILY_ORDER_MAPPED` → induk-child; update XD09 / XD10 / XD11, ERD, simulasi.
