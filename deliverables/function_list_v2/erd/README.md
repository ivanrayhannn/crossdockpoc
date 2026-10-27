# Concept ERD (Crossdock, function list v2)

`Crossdock_ERD.xlsx` dibuat oleh `build_erd.py` (`python3 build_erd.py` dari folder ini). Kolom diambil dari spec UISS XD01–XD15 (`../specs`); data relasi dan simulasi di `erd_data.py`.

| Sheet | Isi |
|---|---|
| ERD | 18 entitas sebagai blok sel dengan **semua kolom** (tanpa collapse), PK / FK, garis relasi (shape) dengan kardinalitas 1 / N; garis putus-putus = relasi logis |
| Table List / Relationship / Column Definition | Daftar tabel (function, sheet simulasi), 21 relasi, semua kolom dengan filter |
| Simulation Index + SIM-1 … SIM-9 | Satu sheet per skenario: SIM-1 master setup & kalkulasi bulanan, SIM-2 order → ASN normal, SIM-3 unit Not Ready (PO kurang) lalu Ready, SIM-4 hold destinasi, SIM-5 partial cancel sebelum submit (CANCELLED), SIM-6 cancel setelah ASN (CONFLICT). Highlight: baris NEW (hijau) / UPD (kuning, sel yang berubah oranye) / DEL (merah, coret) / READ (putih) / TEMP (abu); header kolom PK kuning; nilai status berwarna (Active, Ready, CONFLICT, HOLD_FLAG Y, …) |

`Crossdock_DB_Structure.xlsx` (`build_dbstructure.py`): format dokumen DB Structure (GTOPAS SPS): Revision, Table List (ID, logical / physical name, Row Size, PK Row Size, Logging) dan satu sheet per tabel (MST / HIS / TR / TMP = tabel baru Crossdock, REP = replika DB Surrounding, EXT = tabel existing sebagai referensi) dengan No / Field Name / Logical Name / Type / Len / Prec / PK / N-N / Default / Description. Data simulasi: `sim_data.py`.

## Struktur Pra Daily Order (20-Oct)
Dari `NSP_INSERT_TB_R_PRA_DAILY_ORDER_MANIFEST.sql` (54 kolom, 391 baris) dan `NSP_INSERT_TB_R_PRA_DAILY_ORDER_PART.sql` (38 kolom, 2353 baris). Hanya strukturnya yang disimpan (`pra_structure.json`: kolom, tipe hasil inferensi dari data, PK usulan); data aslinya tidak disimpan di repo.

| Temuan | Dampak ke desain |
|---|---|
| `CROSS_DOCK_FLAG` ada di **manifest** (`'X'` / NULL), bukan di part | XD09 mengambil PO part lewat join manifest `CROSS_DOCK_FLAG = 'X'` |
| Part: `MANIFEST_ITEM`, `ORDER_QTY`, `PO_ITEM`; manifest: `PO_DT` | Kolom tabel baru disamakan di ERD: `MANIFEST_ITEM_NO` → `MANIFEST_ITEM`, `PO_ORDER_QTY` → `ORDER_QTY`, `PO_ORDER_DT` → `PO_DT` (UISS XD09 / XD10 / XD11 masih nama lama) |
| `MANIFEST_NO` unik; 1 `PO_NO` bisa beberapa manifest; `PO_ITEM` bisa beda dengan `MANIFEST_ITEM` | Key PO line untuk mapping = `MANIFEST_NO + MANIFEST_ITEM` |
| Rute / rit: `DELIVERY_DT`, `SUB_ROUTE_CD`, `SUB_ROUTE_SEQ`, `SUB_ROUTE_DT` | Kandidat sumber Delivery Date / Rit di XD10 (TBC) |
| `SUPPLIER_CD` 4 karakter, `SUPPLIER_PLANT` bisa `X` | Data dummy `50221` di prototype / simulasi tetap dipakai (tidak sesuai panjang asli) |

## Struktur tabel existing dari GTOPAS_SPS_DB_Structure_20240423 (20-Oct)
`gsystem_structure.json` (hanya struktur): TR-03 / TR-04 Pra Daily Order (tipe data dipakai untuk kolom export SQL), TR-01 / TR-02 Daily Order Manifest / Part (submit ASN), MST-03 `TB_M_PART_MASTER` (hanya `PART_NAME`), TR-06 `TB_R_CASE_LABEL_LAST_SEQ` (last sequence ASN No dan case label per supplier + plant).

| Catatan | |
|---|---|
| `TB_R_DAILY_ORDER_MANIFEST` PK `SUB_MANIFEST_NO + MANIFEST_NO`, kolom `ASN_NO` | Satu ASN crossdock = beberapa baris manifest dengan `ASN_NO` sama |
| `TB_R_DAILY_ORDER_PART` PK `SUB_MANIFEST_NO + MANIFEST_NO + MANIFEST_ITEM + CASE_NO` | Satu baris per manifest item x case |
| `ASN_NO` VARCHAR(15), `CASE_NO` VARCHAR(9) | Prototype / simulasi memakai nomor contoh `ASN0001` / `C-0003-01`; format asli mengikuti numbering existing |
| Dokumen DB vs export SQL Pra Manifest | Dokumen: `PO_DATE`, `ORDER_RELEASE_DT`, `RE_EXPORT_CD`; export: `PO_DT`, `MANIFEST_LAST_SEQ`, `CANCEL_*`, `SEND_*_MDI` (ERD memakai kolom export) |

## Update 23-Oct
- `TB_R_CROSSDOCK_CANCEL_RESULT` diganti `TB_H_CROSSDOCK_ORDER_CHANGE` (riwayat Change Order Number XD11, DB Structure HIS-02). UPD_STATUS = NULL / 6 / 2.
- SIM-5 = simulasi_asn_rev.xlsx (16–21 Oct: 1 PO per order date, Short PO + split PO, 4 destinasi, cancel baris tengah setelah ASN → Change Order Number). SIM-10 = 1 line di 2 ASN, pecah serial (CO-14115). SIM-6 = draft dilepas XD08 + partial cancel di ASN diganti 2 line (CO-E 4 + CO-F 2, baris dipecah).
