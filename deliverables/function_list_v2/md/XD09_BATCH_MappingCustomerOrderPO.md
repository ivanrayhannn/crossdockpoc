# XD09 – Mapping Customer Order and PO Batch

Sumber: UISS `XD09_UISS_Batch_MappingCustomerOrderPO.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: G-TOPAS / NSP.

- Isi sama dengan X12 (Get Order – pre-mapping FIFO customer order ↔ PO ke #TEMP_INSTRUCTION). Detail: `deliverables/md/X12_FUNCTION_GetOrder_PO_PreMapping.md`.
- Tetap **on demand** dari [Search] di **XD10** (tidak ada scheduler). Sumber order dari **XD08** (status 7, HOLD_FLAG N, PO_MAPPED_FLAG N); qty PO terbuka = PO qty − MAPPED_QTY (TB_R_PRA_DAILY_ORDER_MAPPED).
- Mapping sebenarnya tetap oleh [Create ASN] di XD10 (TB_R_INSTRUCTION).
