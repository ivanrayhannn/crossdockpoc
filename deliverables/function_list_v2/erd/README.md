# Concept ERD (Crossdock, function list v2)

`Crossdock_ERD.xlsx` dibuat oleh `build_erd.py` (`python3 build_erd.py` dari folder ini). Kolom diambil dari spec UISS XD01–XD15 (`../specs`); data relasi dan simulasi di `erd_data.py`.

| Sheet | Isi |
|---|---|
| ERD | 16 entitas sebagai blok sel (warna header: tabel baru Crossdock, replika DB Surrounding / G-TOPAS, existing NSP, temporary), PK / FK, garis relasi (shape) dengan kardinalitas 1 / N; garis putus-putus = relasi logis (tanpa FK) |
| Table List | Tabel, jenis, deskripsi, function yang memakai, jumlah baris simulasi |
| Relationship | 18 relasi: parent / child key, kardinalitas, arti |
| Column Definition | Semua kolom (tipe, PK, FK, Null, deskripsi) dari UISS, dengan filter |
| Simulation Data | Satu skenario konsisten antar tabel: PART-X / PART-Y / PART-Z, kalkulasi Oct-2026, mapping destinasi, sync, order H0253, pre-mapping, ASN-50221-261016-001 (5 case / 30 pcs), cancel CANCELLED dan CONFLICT |
