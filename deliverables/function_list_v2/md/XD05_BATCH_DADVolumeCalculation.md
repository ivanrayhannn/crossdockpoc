# XD05 – DAD Volume Calculation Batch

Sumber: UISS `XD05_UISS_Batch_DADVolumeCalculation.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: GTOPAS / NSP.

## Ringkasan
- **Gabungan** X6 (DAD Volume Calculation) dan X7 (Mapping Destination Calculation) dalam 1 batch dengan 2 proses berurutan:

| Proses | Isi | Step UISS | Func Desc | Log |
|---|---|---|---|---|
| 1 – Status part | Rata-rata MAD vs Min MAD → Active / Inactive, simpan TB_R_PART_DAD_RESULT | 1–9 | 4.1–4.4 | LOG1–LOG7 |
| 2 – Mapping destinasi | Result MAD per buyer + PD → Case/Day periode baru (TB_M_PART_CANDIDATE_DEST) | 10–19 | 4.5–4.8 | LOG8–LOG15 |

- Rumus, pembulatan dan contoh tidak berubah (detail: `deliverables/md/X5-X7_BATCH_Calculation_Functions.md`). Sheet *Sample Input* berisi contoh proses 1 dan 2.

## Jadwal dan trigger (asumsi, TBC)
- Satu run terjadwal = proses 1 lalu proses 2; proses 2 hanya jalan kalau proses 1 berhasil. All-or-nothing **per proses**.
- Auto retry 3x per proses. Manual: [Run calculation (Part List)] di XD01 → proses 1 + 2; [Run calculation (Mapping)] → proses 2 saja.
- Last success date per proses (tab Part List / tab Mapping di XD01). Jalan setelah XD04.

## Keputusan 19-Oct
- Part yang berubah **Active → Inactive** di-set **No Sync**, supaya [Sync] berikutnya mengirimnya ke GTOPAS / AP POLE dengan CROSSDOCK_FLAG 'N'.
- Jadwal bulanan tidak didetailkan. Kalau XD04 gagal, XD05 **tetap jalan**.
- N + S dijumlahkan.
