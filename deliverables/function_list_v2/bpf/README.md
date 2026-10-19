# Business Process Flow Level 2 (Crossdock)

Excel / draw.io: timeline di kolom (X), PIC di baris (Y), sesuai referensi BPF. Prototype: PIC di kolom, timeline di baris. Tiap kotak berisi function (XD), aktivitas, tabel yang dibaca (R) / ditulis (W). Tag merah = kondisi abnormality.

| File | Isi |
|---|---|
| `Crossdock_BPF_Level2.xlsx` | Format mengikuti referensi BPF (E-DCL): F1 / F2 / F4 dengan header dokumen (Phase, Project, Block, Function, Document, Title, Created / Updated, By, Page), title bar Level 2, **timeline di kolom, PIC di baris** (label 2 level diputar), grid dari border sel; proses = shape dengan sudut hitam + tag nomor step, **DB Storage** (nama tabel NSP saja, tanpa Log / read / write) di lane NSP Database dengan data flow putus-putus, tag abnormality merah, legend; Step Detail; User Process (ilustrasi dengan screenshot); Abnormality (AB01–AB16) |
| `Crossdock_BPF_Level2.drawio` | Diagram yang sama (format referensi), 1 page per flow, panah menempel ke kotak; buka di diagrams.net / draw.io (export ke Visio .vsdx, PNG, PDF) |
| `bpf_data.py` | Satu sumber data (lane, timeline, step, tabel, abnormality) |
| `build_bpf.py`, `build_bpf.sh`, `bpf_shots.mjs` | Generator: data prototype → screenshot diagram → Excel |
| `bpf_ref.py` | Sheet flow format referensi (grid sel + shape ter-anchor ke sel) dan draw.io |
| `shots/` | Gambar preview diagram per flow dari prototype (nama dokumen G-TOPAS / NSP) |

Prototype: menu **Common → Business Process Flow** (`#/bpf`); pilihan nama Prototype (T-System / Supplier System) atau Document (G-TOPAS / NSP).

| Flow | Lane (PIC) | Timeline |
|---|---|---|
| F1 Master Setup | G-TOPAS / DB Surrounding, NSP Batch, Procurement, D/S Team, AP POLE | Weekly 21:30 (XD13) · kapan saja (XD01 / XD02) · bulanan (XD04 → XD05 P1 → P2) · setelah run bulanan (XD01 / XD03, [Sync] → XD06 / XD07) · setelah Sync (G-TOPAS, AP POLE) |
| F2 Daily Order to ASN | G-TOPAS, NSP Batch, Supplier | D-1 (H0253 status 7, PO harian) · 27:30 (XD08) · hari D (Search / XD09, Create, Submit 5.7) · setelah submit (XD15, ASN feedback, Log) |
| F4 Hold & Cancel | G-TOPAS, NSP Batch, D/S Team, Supplier | Hari D: Hold / Release destinasi (XD10), Search tanpa baris hold (XD09), Create ASN gagal kalau di-hold setelah dicentang · Kapan saja (SOP, cancel status 2) · 27:30 (XD12 → XD11 → XD08) · hari D (Search ulang, CONFLICT di Log, penanganan barang) |

Open point (TBC): AB14 – apakah XD08 tetap jalan kalau XD12 gagal (job chain).

**Edit manual (20-Oct):** sheet F1 dan F2 diedit langsung di Excel (decision, box Log, teks). `build_bpf.py` mempertahankan sheet di `KEEP = ['F1', 'F2']` apa adanya (sel dan shape) saat workbook di-build ulang; sheet lain (F4, Step Detail, User Process, Abnormality) dibuat ulang dari `bpf_data.py`. Teks F1 / F2 di `bpf_data.py` sudah disamakan untuk Step Detail, prototype dan draw.io (decision manual hanya ada di Excel).
