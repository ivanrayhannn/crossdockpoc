# XD10 – ASN Cross Dock Creation Screen

Sumber: UISS `XD10_UISS_Screen_ASNCrossDockCreation.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: GTOPAS / NSP.

- Isi layar sama dengan X8 (detail: `deliverables/md/X8_SCREEN_ASNCrossdockCreation.md`).
- **Digabung** dengan X14 ASN Submit: proses Submit ASN (Submit ID, insert TB_R_DAILY_ORDER_MANIFEST / PART, tulis ASN_NO / CASE_NO ke TB_R_INSTRUCTION, log existing) sekarang di **Operation Description 5.7**, Data Edit Mapping dan Logging Message **LOG2–LOG5** (LOG1 = error Create ASN).
- [Search] menjalankan **XD09**. Cancel order tidak di NSP: lihat **XD08** (UPD_STATUS, lepas draft) dan **XD11** (Change Order Number).
- Tabel: #TEMP_INSTRUCTION, TB_R_INSTRUCTION, TB_R_PRA_DAILY_ORDER_MAPPED, TB_R_DAILY_ORDER_MANIFEST, TB_R_DAILY_ORDER_PART.


## Simulasi (27-Oct, `simulasi_asn_rev.xlsx`)
UISS **5.0** = perilaku layar dari simulasi (18-Oct: 5 case, Short PO, case 1–4 → ASN0003; centang case 3 = case 1–3; 19-Oct order date 18 menunggu 17; CO-14115 di ASN0006 + ASN0007; hold TH → MSG8; draft dilepas XD08 → MSG11). Sample Input A–I semua dari simulasi (H–I = checkbox 18-Oct dan skenario C1–C7).

## Business Logic ASN (24–26 Oct; UISS Operation 5.0)
1. Customer Order Date (D) → PO Date D+1: 1 PO per Part Number per Customer Order Date.
2. Total customer order qty semua destinasi = PO qty. Kurang → abnormality (Short PO), sisanya di split PO; case tanpa PO menunggu.
3. 1 line customer order bisa di beberapa ASN; receive terpisah → line di H0253 dipecah (SERIAL_NO baru), tiap bagian tetap terhubung ke ASN-nya (XD08, asumsi urutan receive = urutan ASN, TBC).
4. PO_MAPPED_FLAG diisi oleh Create ASN (Y kalau seluruh line sudah di ASN).
5. Case Ready dikirim sesuai CUT_FLAG (dari case 1 sampai cut).
6. Per Part Number, Customer Order Date terlama dulu (tidak boleh loncat); case Not Ready di order date lama menahan order date berikutnya; line hold tidak dihitung.

Contoh lengkap: `deliverables/simulasi_asn_rev.xlsx` (16–22 Oct), prototype menu **ASN Simulation** dan **ASN Creation** (data sama).

Sample Input UISS (A–G) = Create ASN 18-Oct dari simulasi_asn_rev (PART-X 17-Oct, case 1–4 → ASN0003); H–I = contoh aturan case yang dikirim bersama (V01 / T01 / V02).

## Keputusan 19-Oct
- **Case:** per destinasi dipecah sesuai pcs/case (Vietnam 24 pcs, 6 pcs/case = 4 case). GTOPAS rilis kelipatan pcs/case, jadi case selalu penuh. 1 case boleh berisi beberapa Customer Order dan beberapa PO (Supplier) dari destinasi yang sama; line yang tidak muat lanjut ke case berikutnya.
- **Unit tetap utuh** (Part Number + Customer Order Date): kalau 1 line belum dapat PO, unit belum bisa di-ASN.
- **Case label:** 1 label = 1 case 1 destinasi, bisa berisi beberapa Customer Order No; format sesuai existing.

## Sample Create ASN (sheet Sample Input)
Contoh dummy PART-X / PART-Y (6 pcs/case, delivery 16-Oct Rit 1): input pre-mapping XD09 → case packing (Vietnam 18 pcs = 3 case, Thailand 1, Philippines 1; Case 2 = CO-14101 + CO-14102, Case 3 = CO-14102 + CO-14103) → 7 baris TB_R_INSTRUCTION, PO_MAPPED_FLAG Y, MAPPED_QTY → Case List → skenario N1–N3, E1–E4.

## Keputusan 20-Oct (struktur tabel existing, GTOPAS SPS DB Structure)
- Submit ASN menulis `TB_R_DAILY_ORDER_MANIFEST` (1 baris per manifest Pra Daily Order dari case, semua dengan `ASN_NO` yang sama) dan `TB_R_DAILY_ORDER_PART` (1 baris per manifest item x case).
- No ASN dan no case (case label) di-generate otomatis; last sequence-nya disimpan di `TB_R_CASE_LABEL_LAST_SEQ` (`ASN_LAST_SEQ`, `CASE_LABEL_LAST_SEQ` per supplier + plant).
- `PART_NAME` diambil dari `TB_M_PART_MASTER`.

## Keputusan 21-Oct (opsi ASN per blok)
- Delivery plan tetap 1 baris per Part No + Customer Order Date. Case Qty = jumlah **case supplier** (PCS_CASE pcs dalam urutan H0253, boleh campur destinasi).
- Status unit: **Ready** (semua blok '6'), **Partially Ready** (blok pertama '6', blok berikutnya '7'), **Not Ready** (blok pertama '7', check box disabled, MSG2).
- **Checkbox per case supplier**: kolom Case, Qty, **Remaining Qty (not assigned)** (pcs case yang belum punya PO), PO, PO Status. Case Group (GROUP_SEQ XD09 = case sampai CUT_FLAG Y) **tidak ditampilkan sebagai kolom**, hanya dipakai di logika: case yang satu group selalu dikirim bersama. Centang case n → case sebelumnya + case lain di group-nya ikut tercentang (info **MSG10** "Cases 2-3 are sent together. Cases 1-3 … are selected."). Uncentang → group itu dan case sesudahnya lepas. Case tanpa PO disabled (MSG2).
- **Content (destinasi / customer order) hanya untuk D/S team**; supplier tidak melihat destinasi (juga di Case List).
- [Create ASN] insert slice blok terpilih ke TB_R_INSTRUCTION (CASE_SEQ / LINE_SEQ dari XD09). PO_MAPPED_FLAG = 'Y' hanya untuk line yang sudah lengkap; sisa line ikut [Search] berikutnya dan dipotong ulang dari case 1 dengan urutan yang sama.
- Aturan lama "1 case per Part + Customer Order Date + destinasi" dan "unit selalu utuh (A2) / Kondisi 3" diganti aturan blok. Gambar layar di UISS masih dari prototype lama (belum ada kolom ASN Option).

## Keputusan 23-Oct (draft dan Submit)
- `TB_R_INSTRUCTION` dapat kolom **DRAFT_ID** (satu per Create ASN). Baris tanpa ASN_NO = draft.
- **Setiap run XD08 melepas semua draft**: case kembali ke delivery plan, supplier centang ulang dan Create ASN lagi.
- **[Submit ASN] cek ulang**: draft masih ada dan semua line masih UPD_STATUS NULL dengan qty sama; kalau tidak → draft dilepas, **MSG11** "Some orders have changed… Search and create the ASN again".
- Line yang di-cancel setelah Submit ditangani di **XD11 Change Order Number** (D/S).
