# XD09 – Mapping Customer Order and PO Batch

Sumber: UISS `XD09_UISS_Batch_MappingCustomerOrderPO.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-System / NSP.

- Isi sama dengan X12 (Get Order – pre-mapping FIFO customer order ↔ PO ke #TEMP_INSTRUCTION). Detail: `deliverables/md/X12_FUNCTION_GetOrder_PO_PreMapping.md`.
- Tetap **on demand** dari [Search] di **XD10** (tidak ada scheduler). Sumber order dari **XD08** (status 7, HOLD_FLAG N, PO_MAPPED_FLAG N); qty PO terbuka = PO qty − MAPPED_QTY (TB_R_PRA_DAILY_ORDER_MAPPED).
- Mapping sebenarnya tetap oleh [Create ASN] di XD10 (TB_R_INSTRUCTION).

## Business Logic ASN (24–26 Oct; UISS Func Desc 4.0)
1. Customer Order Date (D) → PO Date D+1: 1 PO per Part Number per Customer Order Date.
2. Total customer order qty semua destinasi = PO qty. Kurang → abnormality (Short PO), sisanya di split PO; case tanpa PO menunggu.
3. 1 line customer order bisa di beberapa ASN; receive terpisah → line di H0253 dipecah (SERIAL_NO baru), tiap bagian tetap terhubung ke ASN-nya (XD08, asumsi urutan receive = urutan ASN, TBC).
4. PO_MAPPED_FLAG diisi oleh Create ASN (Y kalau seluruh line sudah di ASN).
5. Case Ready dikirim sesuai CUT_FLAG (dari case 1 sampai cut).
6. Per Part Number, Customer Order Date terlama dulu (tidak boleh loncat); case Not Ready di order date lama menahan order date berikutnya; line hold tidak dihitung.

Contoh lengkap: `deliverables/simulasi_asn_rev.xlsx` (16–22 Oct), prototype menu **ASN Simulation** dan **ASN Creation** (data sama).

## Keputusan 19-Oct
- Jumlah case per destinasi = qty / pcs/case (selalu kelipatan pcs/case). PO Readiness dihitung per case. 1 case boleh berisi beberapa Customer Order dan beberapa PO dari destinasi yang sama.

## Keputusan 20-Oct (struktur Pra Daily Order)
- Order crossdock diambil dari **manifest** dengan `TB_R_PRA_DAILY_ORDER_MANIFEST.CROSS_DOCK_FLAG = 'X'`; data part-nya dari `TB_R_PRA_DAILY_ORDER_PART` (join `MANIFEST_NO`).
- Baris PO = `MANIFEST_NO + MANIFEST_ITEM` (`PO_ITEM` bisa beda; 1 PO bisa beberapa manifest). Open qty = `ORDER_QTY - MAPPED_QTY`, urut `PO_DT`.
- Nama kolom tabel baru disamakan: `MANIFEST_ITEM_NO` → `MANIFEST_ITEM`, `PO_ORDER_QTY` → `ORDER_QTY`, `PO_ORDER_DT` → `PO_DT` (juga di XD10 / XD11).

## Keputusan 21-Oct (urutan scan, case supplier, blok ASN)
- Urutan baris H0253 = urutan alokasi G-System dengan **Allocation Priority = Customer Order Date**: **Allocation Priority (Customer Order Date) → Customer Code → Customer Order No → Customer Order Date → Customer Order Time → Destination Code → Detailed Item No → Serial No**. Di receiving, scan mengalokasikan pcs dengan urutan ini dan urutannya **fixed**.
- Diproses **per Part No + Customer Order Date** (Cara B): unit diproses dari tanggal paling lama, lalu di dalam unit pakai urutan scan.
- PO diberikan berurutan (PO_DT), lalu pcs dipotong jadi **case supplier @ PCS_CASE** (`TB_M_PART_CANDIDATE.PCS_CASE`). Satu case supplier boleh berisi beberapa line dan destinasi.
- Di gudang tetap **1 case = 1 destinasi**, jadi ASN hanya boleh berhenti setelah case di mana **qty kumulatif setiap destinasi kelipatan PCS_CASE** (CUT_FLAG Y). Case sampai titik potong valid = **blok** (GROUP_SEQ) = langkah opsi ASN.
- Blok **Ready ('6')** kalau blok itu dan semua blok sebelumnya punya PO. Blok **tidak boleh dilompati**: kalau blok 2 belum punya PO, blok 3 ikut Not Ready.
- Line bisa terkirim di beberapa ASN: XD09 ambil **open qty** = ORDER_STATUS_QTY − qty line di TB_R_INSTRUCTION. PO_MAPPED_FLAG = 'Y' hanya kalau seluruh line sudah di TB_R_INSTRUCTION.
- `#TEMP_INSTRUCTION`: grain **line × PO × case supplier**; kolom baru SORT_SEQ, ORDER_TIME, OPEN_ORDER_QTY, PCS_CASE, CASE_SEQ, LINE_SEQ, CUM_DEST_QTY, SEQ_QTY (isi case gudang destinasi 1..PCS_CASE, reset setelah PCS_CASE), CUT_FLAG, GROUP_SEQ; CROSSDOCK_STATUS per blok; REMAINING_ORDER_QTY dihapus.
- Contoh (sheet Sample Input): V01 VN 10, T01 TH 6, V02 VN 14, 6 pcs/case, p1 24 (15-Oct), p2 6 (16-Oct) → blok: case 1 | case 2–3 | case 4 | case 5; opsi 15-Oct: 1 / 3 / 4 case, opsi 5 case mulai 16-Oct.
- Urutan scan = **urutan PK** `TB_R_H0253_ORDER_CONTROL_PRE` (7 key yang sama, urutan sama), jadi replicate sudah menyimpan baris dalam urutan scan. XD09 tetap memfilter unit dan membaca dengan `ORDER BY SHIPPING_PART_NO, ORDER_DT, <kolom PK>` (urutan PK global untuk semua part / tanggal, dan baca tanpa ORDER BY tidak dijamin urut). SORT_SEQ = `ROW_NUMBER()` per unit dalam urutan ini (opsional, bisa diturunkan ulang).

### Query urutan baris H0253 (Appendix UISS XD09)
```sql
WITH MAPPED AS (SELECT CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO, SUM(QTY) AS MAPPED_QTY
                FROM TB_R_INSTRUCTION
                GROUP BY CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO),
OPEN_LINE AS (SELECT H.*, H.ORDER_DT AS ALLOCATION_PRIORITY,
                     H.ORDER_STATUS_QTY - COALESCE(M.MAPPED_QTY, 0) AS OPEN_ORDER_QTY
              FROM TB_R_H0253_ORDER_CONTROL_PRE H
              LEFT JOIN MAPPED M ON M.CUSTOMER_CD = H.CUSTOMER_CD AND M.CUSTOMER_ORDER_NO = H.CUSTOMER_ORDER_NO
                   AND M.ORDER_DT = H.ORDER_DT AND M.DESTINATION_CD = H.DESTINATION_CD
                   AND M.DETAILED_ITEM_NO = H.DETAILED_ITEM_NO AND M.SERIAL_NO = H.SERIAL_NO
              WHERE H.ORDER_STATUS = '7' AND H.HOLD_FLAG = 'N' AND H.PO_MAPPED_FLAG = 'N')
SELECT ROW_NUMBER() OVER (PARTITION BY SHIPPING_PART_NO, ORDER_DT
                          ORDER BY ALLOCATION_PRIORITY, CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME,
                                   DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO) AS SORT_SEQ,
       SHIPPING_PART_NO, ALLOCATION_PRIORITY, CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME,
       DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO, ORDER_STATUS_QTY, OPEN_ORDER_QTY
FROM OPEN_LINE
WHERE OPEN_ORDER_QTY > 0
ORDER BY SHIPPING_PART_NO, ALLOCATION_PRIORITY, CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, ORDER_TIME,
         DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO;
```

## Keputusan 23-Oct
- Line yang diambil: ORDER_STATUS 7 **dan UPD_STATUS NULL** (line yang berubah di G-System, UPD_STATUS 6 / 2, tidak diambil), HOLD_FLAG N, open qty > 0. Query di Appendix ikut ditambah `H.UPD_STATUS IS NULL`.
