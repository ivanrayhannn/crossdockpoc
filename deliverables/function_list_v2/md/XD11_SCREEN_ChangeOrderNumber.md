# XD11 – Change Order Number Screen (D/S team)

Sumber: UISS `XD11_UISS_Screen_ChangeOrderNumber.xlsx` (0.1 Initial Draft). Sub menu ASN (di sebelah ASN Creation), hanya D/S team. Menggantikan XD11 lama (Cancel Crossdock Customer Order Batch) dan penanganan CONFLICT di luar sistem (keputusan 23-Oct).

## Kapan muncul
- Line H0253 replicate dengan **UPD_STATUS '2'** (di-cancel G-System, di-set XD08) yang qty-nya **sudah di ASN yang di-submit** (baris `TB_R_INSTRUCTION` dengan ASN_NO).
- Cancel tanpa ASN (contoh CO-14102) tidak muncul. Draft (belum Submit) sudah dilepas XD08.
- Baris tetap di daftar **sampai diganti** (tanpa batas waktu); tanpa kandidat = "Waiting for a candidate".

## Kandidat pengganti
- **Part sama**, **UPD_STATUS '6'** (sudah received / allocated di G-System), **PO_MAPPED_FLAG 'N'**, **tidak ada di TB_R_INSTRUCTION** (belum punya ASN).
- **Destinasi boleh beda**. Urutan: **Customer Order Date paling tua**.
- **Boleh beberapa line** asalkan total qty = qty cancel. Default tercentang: line paling tua yang jumlahnya pas.

## Proses [Change Order Number] → [Yes]
1. Qty cancel diambil **dari case terakhir mundur** (contoh CO-B 8 pcs di case 1: 4 dan case 2: 4, cancel 6 → case 2: 4 + case 1: 2).
2. Baris TB_R_INSTRUCTION yang pindah utuh → key customer order diganti; yang pindah sebagian → **dipecah** (baris baru untuk line pengganti). ASN, CASE_NO, PO tidak berubah (case fisik tetap).
3. Line pengganti: PO_MAPPED_FLAG = **Y**. Line yang di-cancel: tidak diubah (PO_MAPPED_FLAG tetap Y, UPD_STATUS 2).
4. Riwayat per potongan ke **TB_H_CROSSDOCK_ORDER_CHANGE** (pengganti TB_R_CROSSDOCK_CANCEL_RESULT).
5. Re-check di transaksi yang sama: kandidat yang sudah dipakai di sesi lain → MSG4, tidak ada yang disimpan.

## Contoh
- simulasi_asn.xlsx 19-Oct: CO-14104 (TH 6) di case 3 ASN0003 di-cancel → 6 pcs case C-0003-03 pindah ke **CO-14108** (TH 6, UPD 6).
- Partial cancel: CO-B 6 dari 8 pcs di ASN00020 → **CO-E 4 + CO-F 2** (dua line, destinasi PH dan VN).

## Pesan
| No | Kondisi | Pesan |
|---|---|---|
| MSG1 | Tidak ada data | No cancelled qty in a submitted ASN. |
| MSG2 | Qty tercentang ≠ qty cancel | Selected {n} of {q} pcs: the qty must add up to {q}. |
| MSG3 | Konfirmasi | {q} pcs of {order} in {ASN} ({cases}) will be moved to {lines}. |
| MSG4 | Kandidat sudah dipakai | {order} is no longer available. The candidates are refreshed. |
