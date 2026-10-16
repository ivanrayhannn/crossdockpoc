# Batch – ASN Submit (X14)

Sumber: UISS-Batch `X14_UISS_Batch_ASNSubmit.xlsx` (0.1 Initial Draft, update 16-Oct-26). Dipanggil dari **[Submit ASN] → Yes** di ASN Crossdock Creation (X8).

## Poin utama
- Submit ASN dibuat **batch** supaya layar tidak menunggu. **Proses submit (Submit ID, pemanggilan batch, log) mengikuti ASN existing.** X8 membuat **Submit ID**, menyerahkan baris **TB_R_INSTRUCTION** (hasil Create ASN, 1 Supplier Code + Plant) ke batch, lalu kembali ke delivery plan dengan banner Submit ID.
- Batch mengambil **ASN No** dari penomoran existing dan **auto generate Case No** dengan cek **last sequence** (disimpan di tabel last sequence existing; format sesuai existing — note saja).
- Insert ke tabel ASN **existing**: **TB_R_DAILY_ORDER_MANIFEST** (status Created) dan **TB_R_DAILY_ORDER_PART**; ASN_NO / CASE_NO ditulis balik ke TB_R_INSTRUCTION.
- Hasil ditulis ke **log existing** (Log Monitoring) dengan Submit ID; **tidak ada popup sukses** di layar.
- **All-or-nothing**: gagal → roll back, mapping dilepas (baris TB_R_INSTRUCTION dihapus, PO_MAPPED_FLAG kembali N, MAPPED_QTY di TB_R_PRA_DAILY_ORDER_MAPPED dikurangi lagi), log error.
- Tanpa scheduler (on demand).

## Alur
1. X8: konfirmasi *"Submit ASN? {n} cases ({q} pcs) will be created into {ASN No}, delivery {Delivery Date} · {Rit}."* → Yes.
2. Buat Submit ID, tulis LOG1 (start), jalankan batch.
3. Baca TB_R_INSTRUCTION → ambil ASN No / Case No (existing, last sequence) → insert TB_R_DAILY_ORDER_MANIFEST + TB_R_DAILY_ORDER_PART → update ASN_NO / CASE_NO di TB_R_INSTRUCTION.
4. Commit → LOG2 (hasil) + LOG3 (end). Error → roll back, lepas mapping + LOG4.

## Log message
| ID | Kapan | Pesan |
|---|---|---|
| LOG1 | Start | ASN submit started. Submit ID <SUBMIT_ID>, <n> cases. |
| LOG2 | ASN tersimpan | <ASN_NO> submitted with status Created. <n> cases are saved. Delivery <DELIVERY_DT> · <RIT>. The ASN is shown in ASN Inquiry. |
| LOG3 | End | ASN submit ended. Status <STATUS>. |
| LOG4 | Error | Failed to submit ASN, Submit ID <SUBMIT_ID>: <ERROR_DETAIL>. |

## TB_R_DAILY_ORDER_MANIFEST (existing) – field yang dipakai
| Kolom | Tipe | Keterangan |
|---|---|---|
| MANIFEST_NO / ASN_NO | existing | ASN number (auto generated as today, existing numbering) |
| SUPPLIER_CD | existing | Supplier code |
| SUPPLIER_PLANT | existing | Supplier plant |
| DELIVERY_DT | existing | Delivery Date |
| RIT / ROUTE | existing | Rit and route (route master, existing) |
| TOTAL_CASE / TOTAL_QTY | existing | Number of cases / Delivery Qty |
| STATUS | existing | Created |
| CREATED_BY / CREATED_DT | existing | User and date-time of submit |

## TB_R_DAILY_ORDER_PART (existing) – field yang dipakai
| Kolom | Tipe | Keterangan |
|---|---|---|
| MANIFEST_NO / ASN_NO | existing | ASN number |
| CASE_NO | existing | Case number, auto generated with the existing last sequence |
| PART_NO | existing | Part number of the case |
| DESTINATION_CD | existing | Destination of the case |
| QTY | existing | Qty of the case |
| PO_NO / MANIFEST_ITEM_NO | existing | PO reference of the Pra Daily Order |
| CREATED_BY / CREATED_DT | existing | User and date-time of submit |

Nama kolom fisik mengikuti tabel existing. Struktur **TB_R_INSTRUCTION** (sumber batch ini) ada di md X8.

## Keputusan (konfirmasi 16-Oct)
- ASN setelah submit masuk ke TB_R_DAILY_ORDER_MANIFEST dan TB_R_DAILY_ORDER_PART.
- Case number auto generate dengan cek last sequence (tabel existing).
- 1 ASN = 1 Supplier Code + Supplier Plant.

## Open points
- Mapping kolom fisik ke TB_R_DAILY_ORDER_MANIFEST / PART (perlu cek struktur existing bersama tim IT).
