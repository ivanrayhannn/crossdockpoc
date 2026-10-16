# Screen – ASN Inquiry (X13)

Sumber: UISS-Screen `X13_UISS_Screen_ASNInquiry.xlsx` (0.1 Initial Draft, update 16-Oct-26). Prototype: menu **ASN → ASN Inquiry**.

## Poin utama
- Daftar ASN crossdock yang sudah di-submit di **ASN Crossdock Creation (X8)**, terbaru di atas. Supplier: hanya Supplier Code + Plant sendiri; tim D/S: semua supplier.
- Kriteria: ASN No (contains), Delivery Date From–To, Part Number. Search / Reset (Enter di ASN No = Search).
- Kolom: ASN No (link), Delivery Date, Rit Cycle, Route, Part / Customer Order Date, Cases, Qty, Status (Created), Created (user + waktu).
- Klik ASN No → **Detail**: ringkasan (Delivery Date, Rit Cycle · Route, unit, cases · qty, created) dan daftar case (Case No, Part Number, Customer Order Date, Destination, Customer Order No (qty), PO No, Qty) – read only.
- **Download Case Label** di detail (format **sesuai existing**). Layar hanya menampilkan data.
- **Tidak ada Cancel ASN** di layar ini: cancel tidak dilakukan di Supplier System. Cancel datang dari source H0253 dengan **order status `2`** untuk order yang sudah **HOLD_FLAG = Y**; Supplier System hanya hold (lihat md X10).

## Tabel
- **TB_R_DAILY_ORDER_MANIFEST** (existing) – ASN (header), diisi batch X14 saat Submit ASN di X8.
- **TB_R_DAILY_ORDER_PART** (existing) – case per ASN (ASN No, Case No).
- Nama kolom fisik mengikuti tabel existing.

## Pesan
| ID | Kapan | Pesan |
|---|---|---|
| MSG1 | Search tanpa hasil | No ASN matches this search. |

## Keputusan (konfirmasi 16-Oct)
- Tabel ASN = TB_R_DAILY_ORDER_MANIFEST / TB_R_DAILY_ORDER_PART (existing).
- Cancel ASN tidak dibuat di Supplier System (dari source, status 2).
