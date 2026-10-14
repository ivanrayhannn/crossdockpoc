# Screen – ASN Inquiry (X13)

Sumber: UISS-Screen `X13_UISS_Screen_ASNInquiry.xlsx` (0.1 Initial Draft). Prototype: menu **ASN → ASN Inquiry**.

## Poin utama
- Daftar ASN yang sudah di-submit di **ASN Crossdock Creation (X8)**, terbaru di atas.
- Kriteria: ASN No (contains), Delivery Date From–To, Part Number. Search / Reset (Enter di ASN No = Search).
- Kolom: ASN No (link), Delivery Date, Rit Cycle, Route, Part / Customer Order Date, Cases, Qty, Status (Submitted), Created (user + waktu).
- Klik ASN No → **Detail**: ringkasan (Delivery Date, Rit Cycle · Route, unit, cases · qty, created) dan daftar case (Case No, Part Number, Customer Order Date, Destination, Customer Order No (qty), PO No, Qty) – read only.
- **Download Case Label** di detail (format TBD). Layar hanya menampilkan data.

## Tabel
- **TB_R_ASN_CROSSDOCK_H** – header ASN.
- **TB_R_INSTRUCTION** – case & line per ASN (ASN_NO, CASE_NO).

## Pesan
| ID | Kapan | Pesan |
|---|---|---|
| MSG1 | Search tanpa hasil | No ASN matches this search. |

## Open points
- Perlu cancel / revisi ASN dari layar ini? Format label.
