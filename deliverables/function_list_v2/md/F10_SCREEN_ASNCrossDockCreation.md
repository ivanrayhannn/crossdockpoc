# F10 – ASN Cross Dock Creation Screen

Sumber: UISS `F10_UISS_Screen_ASNCrossDockCreation.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Isi layar sama dengan X8 (detail: `deliverables/md/X8_SCREEN_ASNCrossdockCreation.md`).
- **Digabung** dengan X14 ASN Submit: proses Submit ASN (Submit ID, insert TB_R_DAILY_ORDER_MANIFEST / PART, tulis ASN_NO / CASE_NO ke TB_R_INSTRUCTION, log existing) sekarang di **Operation Description 5.7**, Data Edit Mapping dan Logging Message **LOG2–LOG5** (LOG1 = error Create ASN).
- [Search] menjalankan **F09**. Cancel order tidak di NSP: lihat **F11 / F12**.
- Tabel: #TEMP_INSTRUCTION, TB_R_INSTRUCTION, TB_R_PRA_DAILY_ORDER_MAPPED, TB_R_DAILY_ORDER_MANIFEST, TB_R_DAILY_ORDER_PART.
