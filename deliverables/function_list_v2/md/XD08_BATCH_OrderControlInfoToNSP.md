# XD08 – Order Control Information to NSP Batch

Sumber: UISS `XD08_UISS_Batch_OrderControlInfoToNSP.xlsx` (0.1 Initial Draft). Nama sistem di UISS: G-System / NSP.

## Keputusan 23-Oct (simulasi_asn.xlsx)
- **Satu batch** untuk H0253: XD08 lama (status 7 / 6) dan XD12 (status 2) **digabung**. XD11 lama (cancel batch) diganti layar **Change Order Number** (XD11).
- Tabel source di DB Surrounding **insert / update**. NSP memakai **satu tabel replicate** `TB_R_H0253_ORDER_CONTROL_PRE`, di-**upsert** per unique key (termasuk SERIAL_NO). Hanya baris dengan **INTF_UPDATE_DT > watermark**.
- **ORDER_STATUS** di replicate = nilai saat pertama direplikasi (biasanya 7), tidak diubah lagi.
- **UPD_STATUS** (kolom NSP, sebelumnya CANCEL_STATUS): NULL = tidak ada perubahan; **'6'** = original ORDER_STATUS jadi 6 (received / allocated); **'2'** = original jadi 2 (cancel). Line dengan UPD_STATUS tidak diambil XD09.
- **Setiap run, semua draft dilepas**: baris `TB_R_INSTRUCTION` dengan ASN_NO NULL (Create ASN belum Submit) dihapus, MAPPED_QTY dikurangi, PO_MAPPED_FLAG = N. Case kembali muncul di delivery plan XD10, supplier centang ulang dan Create ASN lagi. Baris yang sudah punya ASN_NO tidak pernah dihapus.
- **Cancel setelah ASN** (UPD_STATUS 2 dan line punya baris TB_R_INSTRUCTION dengan ASN_NO): ASN tidak diubah; line muncul di **XD11 Change Order Number** (LOG5). Qty cancel tidak kelipatan pcs/case → LOG6 (abnormality).

## Alur
1. Scheduler harian setelah data G-System tersedia (27:30), retry 3x. LOG1.
2. Ambil baris source INTF_UPDATE_DT > watermark (line crossdock, status 7 / 6 / 2).
3. Upsert: key baru → insert (HOLD_FLAG / PO_MAPPED_FLAG = N, UPD_STATUS = NULL kalau status 7, selain itu = status source). Key lama → update kolom source kecuali ORDER_STATUS; UPD_STATUS = status source kalau 6 / 2.
4. Lepas semua draft TB_R_INSTRUCTION.
5. Cek line UPD_STATUS 2 yang ada di ASN → LOG5 (dan LOG6 kalau qty tidak kelipatan pcs/case).
6. Sukses → commit, watermark baru, LOG2. Gagal → rollback, watermark tetap, LOG3.

## Contoh (simulasi_asn.xlsx)
| Tanggal | Original | Replicate NSP |
|---|---|---|
| 15-Oct | CO-14101 VN 6, CO-14102 TH 6 (status 7) | insert, UPD_STATUS NULL; CO-14101 → ASN0001, CO-14102 di-hold D/S |
| 16-Oct | CO-14101 → 6, CO-14102 → 2, CO-14103 baru | CO-14101 UPD 6; CO-14102 UPD 2 (tanpa ASN → diabaikan, PO_MAPPED_FLAG tetap N); CO-14103 insert → ASN00002 |
| 17-Oct | CO-14103 → 6, CO-14104 TH & CO-14105 VN baru | CO-14103 UPD 6; CO-14104 → ASN00003 |
| 18-Oct | CO-14104 → 2, CO-14105 → 6 | CO-14104 UPD 2 padahal di ASN00003 → muncul di XD11; CO-14105 UPD 6, PO_MAPPED N, tanpa ASN → kandidat pengganti |
