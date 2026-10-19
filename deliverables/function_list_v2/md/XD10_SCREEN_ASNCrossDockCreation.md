# XD10 – ASN Cross Dock Creation Screen

Sumber: UISS `XD10_UISS_Screen_ASNCrossDockCreation.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Isi layar sama dengan X8 (detail: `deliverables/md/X8_SCREEN_ASNCrossdockCreation.md`).
- **Digabung** dengan X14 ASN Submit: proses Submit ASN (Submit ID, insert TB_R_DAILY_ORDER_MANIFEST / PART, tulis ASN_NO / CASE_NO ke TB_R_INSTRUCTION, log existing) sekarang di **Operation Description 5.7**, Data Edit Mapping dan Logging Message **LOG2–LOG5** (LOG1 = error Create ASN).
- [Search] menjalankan **XD09**. Cancel order tidak di NSP: lihat **XD11 / XD12**.
- Tabel: #TEMP_INSTRUCTION, TB_R_INSTRUCTION, TB_R_PRA_DAILY_ORDER_MAPPED, TB_R_DAILY_ORDER_MANIFEST, TB_R_DAILY_ORDER_PART.

## Keputusan 19-Oct
- **Case:** per destinasi dipecah sesuai pcs/case (Vietnam 24 pcs, 6 pcs/case = 4 case). G-TOPAS rilis kelipatan pcs/case, jadi case selalu penuh.
- **Unit tetap utuh** (Part Number + Customer Order Date): kalau 1 line belum dapat PO, unit belum bisa di-ASN.
- **Case label:** 1 label = 1 case 1 destinasi, bisa berisi beberapa Customer Order No; format sesuai existing.
