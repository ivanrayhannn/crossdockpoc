# Business Process Flow Level 2 (Crossdock)

X = PIC (swimlane), Y = timeline. Tiap kotak berisi function (XD), aktivitas, tabel yang dibaca (R) / ditulis (W). Tag merah = kondisi abnormality.

| File | Isi |
|---|---|
| `Crossdock_BPF_Level2.xlsx` | Cover; F1 Master Setup, F2 Daily Order to ASN, F3 Cancel (swimlane dari **kolom/baris + border**, step = sel berwarna, hanya panah yang shape); Step Detail; **User Process** (ilustrasi proses business user dengan screenshot layar); Abnormality (AB01–AB16) |
| `Crossdock_BPF_Level2.drawio` | Diagram yang sama, 1 page per flow, panah menempel ke kotak; buka di diagrams.net / draw.io (bisa export ke Visio .vsdx, PNG, PDF) |
| `bpf_data.py` | Satu sumber data (lane, timeline, step, tabel, abnormality) |
| `build_bpf.py`, `build_bpf.sh`, `bpf_shots.mjs` | Generator: data prototype → screenshot diagram → Excel |
| `bpf_grid.py` | Sheet flow Excel berbasis sel (lane = kolom, timeline = baris, panah ter-anchor ke sel) |
| `bpf_shapes.py` | Layout diagram (sama dengan halaman prototype) → draw.io |
| `shots/` | Gambar preview diagram per flow dari prototype (nama dokumen G-TOPAS / NSP) |

Prototype: menu **Common → Business Process Flow** (`#/bpf`); pilihan nama Prototype (T-System / Supplier System) atau Document (G-TOPAS / NSP).

| Flow | Lane (PIC) | Timeline |
|---|---|---|
| F1 Master Setup | G-TOPAS / DB Surrounding, NSP Batch, Procurement, D/S Team, AP POLE | Weekly 21:30 (XD13) · kapan saja (XD01 / XD02) · bulanan (XD04 → XD05 P1 → P2) · setelah run bulanan (XD01 / XD03, [Sync] → XD06 / XD07) · setelah Sync (G-TOPAS, AP POLE) |
| F2 Daily Order to ASN | G-TOPAS, NSP Batch, D/S Team, Supplier | D-1 (H0253 status 7, PO harian) · 27:30 (XD08) · hari D (Hold, Search / XD09, Create, Submit 5.7) · setelah submit (XD15, ASN feedback, Log) |
| F3 Cancel | G-TOPAS, NSP Batch, D/S Team, Supplier | Kapan saja (SOP, cancel status 2) · 27:30 (XD12 → XD11 → XD08) · hari D (Search ulang, CONFLICT di Log, penanganan barang) |

Open point (TBC): AB14 – apakah XD08 tetap jalan kalau XD12 gagal (job chain).
