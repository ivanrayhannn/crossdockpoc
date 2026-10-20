# Concept ERD (Crossdock, function list v2)

`Crossdock_ERD.xlsx` dibuat oleh `build_erd.py` (`python3 build_erd.py` dari folder ini). Kolom diambil dari spec UISS XD01–XD15 (`../specs`); data relasi dan simulasi di `erd_data.py`.

| Sheet | Isi |
|---|---|
| ERD | 16 entitas sebagai blok sel (warna header: tabel baru Crossdock, replika DB Surrounding / G-TOPAS, existing NSP, temporary), PK / FK, garis relasi (shape) dengan kardinalitas 1 / N; garis putus-putus = relasi logis (tanpa FK) |
| Table List | Tabel, jenis, deskripsi, function yang memakai, jumlah baris simulasi |
| Relationship | 18 relasi: parent / child key, kardinalitas, arti |
| Column Definition | Semua kolom (tipe, PK, FK, Null, deskripsi) dari UISS, dengan filter |
| Simulation Data | Satu skenario konsisten antar tabel: PART-X / PART-Y / PART-Z, kalkulasi Oct-2026, mapping destinasi, sync, order H0253, pre-mapping, ASN-50221-261016-001 (5 case / 30 pcs), cancel CANCELLED dan CONFLICT |

## Struktur Pra Daily Order (20-Oct)
Dari `NSP_INSERT_TB_R_PRA_DAILY_ORDER_MANIFEST.sql` (54 kolom, 391 baris) dan `NSP_INSERT_TB_R_PRA_DAILY_ORDER_PART.sql` (38 kolom, 2353 baris). Hanya strukturnya yang disimpan (`pra_structure.json`: kolom, tipe hasil inferensi dari data, PK usulan); data aslinya tidak disimpan di repo.

| Temuan | Dampak ke desain |
|---|---|
| `CROSS_DOCK_FLAG` ada di **manifest** (`'X'` / NULL), bukan di part | XD09 mengambil PO part lewat join manifest `CROSS_DOCK_FLAG = 'X'` |
| Part: `MANIFEST_ITEM`, `ORDER_QTY`, `PO_ITEM`; manifest: `PO_DT` | Kolom tabel baru disamakan di ERD: `MANIFEST_ITEM_NO` → `MANIFEST_ITEM`, `PO_ORDER_QTY` → `ORDER_QTY`, `PO_ORDER_DT` → `PO_DT` (UISS XD09 / XD10 / XD11 masih nama lama) |
| `MANIFEST_NO` unik; 1 `PO_NO` bisa beberapa manifest; `PO_ITEM` bisa beda dengan `MANIFEST_ITEM` | Key PO line untuk mapping = `MANIFEST_NO + MANIFEST_ITEM` |
| Rute / rit: `DELIVERY_DT`, `SUB_ROUTE_CD`, `SUB_ROUTE_SEQ`, `SUB_ROUTE_DT` | Kandidat sumber Delivery Date / Rit di XD10 (TBC) |
| `SUPPLIER_CD` 4 karakter, `SUPPLIER_PLANT` bisa `X` | Data dummy `50221` di prototype / simulasi tetap dipakai (tidak sesuai panjang asli) |
