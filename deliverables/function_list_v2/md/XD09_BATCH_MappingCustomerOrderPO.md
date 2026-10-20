# XD09 – Mapping Customer Order and PO Batch

Sumber: UISS `XD09_UISS_Batch_MappingCustomerOrderPO.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Isi sama dengan X12 (Get Order – pre-mapping FIFO customer order ↔ PO ke #TEMP_INSTRUCTION). Detail: `deliverables/md/X12_FUNCTION_GetOrder_PO_PreMapping.md`.
- Tetap **on demand** dari [Search] di **XD10** (tidak ada scheduler). Sumber order dari **XD08** (status 7, HOLD_FLAG N, PO_MAPPED_FLAG N); qty PO terbuka = PO qty − MAPPED_QTY (TB_R_PRA_DAILY_ORDER_MAPPED).
- Mapping sebenarnya tetap oleh [Create ASN] di XD10 (TB_R_INSTRUCTION).

## Keputusan 19-Oct
- Jumlah case per destinasi = qty / pcs/case (selalu kelipatan pcs/case). PO Readiness dihitung per case. 1 case boleh berisi beberapa Customer Order dan beberapa PO dari destinasi yang sama.

## Keputusan 20-Oct (struktur Pra Daily Order)
- Order crossdock diambil dari **manifest** dengan `TB_R_PRA_DAILY_ORDER_MANIFEST.CROSS_DOCK_FLAG = 'X'`; data part-nya dari `TB_R_PRA_DAILY_ORDER_PART` (join `MANIFEST_NO`).
- Baris PO = `MANIFEST_NO + MANIFEST_ITEM` (`PO_ITEM` bisa beda; 1 PO bisa beberapa manifest). Open qty = `ORDER_QTY - MAPPED_QTY`, urut `PO_DT`.
- Nama kolom tabel baru disamakan: `MANIFEST_ITEM_NO` → `MANIFEST_ITEM`, `PO_ORDER_QTY` → `ORDER_QTY`, `PO_ORDER_DT` → `PO_DT` (juga di XD10 / XD11).
