# XD10 – ASN Cross Dock Creation Screen

Sumber: UISS `XD10_UISS_Screen_ASNCrossDockCreation.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-System / NSP.

- Isi layar sama dengan X8 (detail: `deliverables/md/X8_SCREEN_ASNCrossdockCreation.md`).
- **Digabung** dengan X14 ASN Submit: proses Submit ASN (Submit ID, insert TB_R_DAILY_ORDER_MANIFEST / PART, tulis ASN_NO / CASE_NO ke TB_R_INSTRUCTION, log existing) sekarang di **Operation Description 5.7**, Data Edit Mapping dan Logging Message **LOG2–LOG5** (LOG1 = error Create ASN).
- [Search] menjalankan **XD09**. Cancel order tidak di NSP: lihat **XD11 / XD12**.
- Tabel: #TEMP_INSTRUCTION, TB_R_INSTRUCTION, TB_R_PRA_DAILY_ORDER_MAPPED, TB_R_DAILY_ORDER_MANIFEST, TB_R_DAILY_ORDER_PART.

## Keputusan 19-Oct
- **Case:** per destinasi dipecah sesuai pcs/case (Vietnam 24 pcs, 6 pcs/case = 4 case). G-System rilis kelipatan pcs/case, jadi case selalu penuh. 1 case boleh berisi beberapa Customer Order dan beberapa PO (Supplier) dari destinasi yang sama; line yang tidak muat lanjut ke case berikutnya.
- **Unit tetap utuh** (Part Number + Customer Order Date): kalau 1 line belum dapat PO, unit belum bisa di-ASN.
- **Case label:** 1 label = 1 case 1 destinasi, bisa berisi beberapa Customer Order No; format sesuai existing.

## Sample Create ASN (sheet Sample Input)
Contoh dummy PART-X / PART-Y (6 pcs/case, delivery 16-Oct Rit 1): input pre-mapping XD09 → case packing (Vietnam 18 pcs = 3 case, Thailand 1, Philippines 1; Case 2 = CO-14101 + CO-14102, Case 3 = CO-14102 + CO-14103) → 7 baris TB_R_INSTRUCTION, PO_MAPPED_FLAG Y, MAPPED_QTY → Case List → skenario N1–N3, E1–E4.

## Keputusan 20-Oct (struktur tabel existing, G-System SPS DB Structure)
- Submit ASN menulis `TB_R_DAILY_ORDER_MANIFEST` (1 baris per manifest Pra Daily Order dari case, semua dengan `ASN_NO` yang sama) dan `TB_R_DAILY_ORDER_PART` (1 baris per manifest item x case).
- No ASN dan no case (case label) di-generate otomatis; last sequence-nya disimpan di `TB_R_CASE_LABEL_LAST_SEQ` (`ASN_LAST_SEQ`, `CASE_LABEL_LAST_SEQ` per supplier + plant).
- `PART_NAME` diambil dari `TB_M_PART_MASTER`.

## Keputusan 21-Oct (opsi ASN per blok)
- Delivery plan tetap 1 baris per Part No + Customer Order Date. Case Qty = jumlah **case supplier** (PCS_CASE pcs dalam urutan scan, boleh campur destinasi).
- Status unit: **Ready** (semua blok '6'), **Partially Ready** (blok pertama '6', blok berikutnya '7'), **Not Ready** (blok pertama '7', check box disabled, MSG2).
- Item baru **ASN Option** (dropdown per unit yang dicentang): pilih n blok Ready pertama, contoh "1 case (6 pcs) / 3 cases (18 pcs) / 4 cases (24 pcs)"; default semua blok Ready. Blok tidak dipecah dan tidak dilompati.
- [Create ASN] insert slice blok terpilih ke TB_R_INSTRUCTION (CASE_SEQ / LINE_SEQ dari XD09). PO_MAPPED_FLAG = 'Y' hanya untuk line yang sudah lengkap; sisa line ikut [Search] berikutnya dan dipotong ulang dari case 1 dengan urutan yang sama.
- Aturan lama "1 case per Part + Customer Order Date + destinasi" dan "unit selalu utuh (A2) / Kondisi 3" diganti aturan blok. Gambar layar di UISS masih dari prototype lama (belum ada kolom ASN Option).
