# Business Process Flow Level 2 (Crossdock)

Excel / draw.io: timeline di kolom (X), PIC di baris (Y), sesuai referensi BPF. Prototype: PIC di kolom, timeline di baris. Tiap kotak berisi function (XD), aktivitas, tabel yang dibaca (R) / ditulis (W). Tag merah = kondisi abnormality.

| File | Isi |
|---|---|
| `Crossdock_BPF_Level2.xlsx` | Format mengikuti referensi BPF (E-DCL): F1 / F2 / F4 dengan header dokumen (Phase, Project, Block, Function, Document, Title, Created / Updated, By, Page), title bar Level 2, **timeline di kolom, PIC di baris** (label 2 level diputar), grid dari border sel; proses = shape dengan sudut hitam + tag nomor step, **DB Storage** (nama tabel NSP saja, tanpa Log / read / write) di lane NSP Database dengan data flow putus-putus, tag abnormality merah, legend; Step Detail; User Process (ilustrasi dengan screenshot); Abnormality (AB01–AB16) |
| `Crossdock_BPF_Level2.drawio` | Diagram yang sama (format referensi), 1 page per flow, panah menempel ke kotak; buka di diagrams.net / draw.io (export ke Visio .vsdx, PNG, PDF) |
| `bpf_data.py` | Satu sumber data (lane, timeline, step, tabel, abnormality) |
| `build_bpf.py`, `build_bpf.sh`, `bpf_shots.mjs` | Generator: data prototype → screenshot diagram → Excel |
| `bpf_ref.py` | Sheet flow format referensi (grid sel + shape ter-anchor ke sel) dan draw.io |
| `shots/` | Gambar preview diagram per flow dari prototype (nama dokumen GTOPAS / NSP) |

Prototype: menu **Common → Business Process Flow** (`#/bpf`); pilihan nama Prototype (G-System / Supplier System) atau Document (GTOPAS / NSP).

| Flow | Lane (PIC) | Timeline |
|---|---|---|
| F1 Master Setup | GTOPAS / DB Surrounding, NSP Batch, Procurement, D/S Team, AP POLE | Weekly 21:30 (XD13) · kapan saja (XD01 / XD02) · bulanan (XD04 → XD05 P1 → P2) · setelah run bulanan (XD01 / XD03, [Sync] → XD06 / XD07) · setelah Sync (GTOPAS, AP POLE) |
| F2 Daily Order to ASN | GTOPAS, NSP Batch, Supplier | D-2 (customer order H0253 status 7) · D-1 (PO) · 27:30 (XD08) · daily (Search / XD09, Create, Submit 5.7) · setelah submit / receiving (XD15, Receive ASN, Log) |
| F4 Hold & Cancel | GTOPAS, NSP Batch, D/S Team, Supplier | Hari D: Hold / Release destinasi (XD10), Search tanpa baris hold (XD09), Create ASN gagal kalau di-hold setelah dicentang. Cancel (23-Oct): GTOPAS cancel → XD08 (satu batch) set UPD_STATUS 2 dan melepas semua draft; cancel qty yang sudah di ASN → D/S pindahkan ke line UPD_STATUS 6 di Change Order Number (XD11), riwayat TB_H_CROSSDOCK_ORDER_CHANGE |

Open point AB14 (XD08 jalan kalau XD12 gagal) tidak berlaku lagi: XD12 digabung ke XD08 (23-Oct).

Sheet **F1 / F2** diedit manual di Excel (tidak di-generate ulang). Update 27-Oct: diagram F2 dipatch dengan `patch_f2_manual.py` (teks D2 / D3 / D6 / D7 / D8, step baru **D14 receiving**, badge AB17 / AB18, label band XD08 satu batch). Update 27-Oct (file user `_6`): band pertama dipecah jadi **D-2 · customer order** (D1) dan **D-1 · PO (existing)** (D2) dengan menyisipkan 2 kolom (`f2_insert_band.py`); shape tetap shape Excel (editable), edit user (Phase BPF, label band, D12 Receive ASN) dipertahankan.

**Edit manual (20-Oct):** sheet F1 dan F2 diedit langsung di Excel (decision, box Log, teks). `build_bpf.py` mempertahankan sheet di `KEEP = ['F1', 'F2']` apa adanya (sel dan shape) saat workbook di-build ulang; sheet lain (F4, Step Detail, User Process, Abnormality) dibuat ulang dari `bpf_data.py`. Teks F1 / F2 di `bpf_data.py` sudah disamakan untuk Step Detail, prototype dan draw.io (decision manual hanya ada di Excel).
