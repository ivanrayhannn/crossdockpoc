# Function – Get Order: Customer Order – PO Pre-mapping (X12)

Sumber: UISS-Batch `X12_UISS_Batch_GetOrderPOPreMapping.xlsx` (0.1 Initial Draft, update 15-Oct-26), bagian "Get Data → Insert result mapping Cust Order PO Supplier → temp #TB_R_INSTRUCTION" di flow ASN.
**Bukan batch terjadwal**: fungsi ini jalan saat user klik **[Get Order]** di layar ASN Crossdock Creation (X8).

## Alur
1. User memilih **Delivery Date** dan **Rit** di X8 (Route tampil otomatis), lalu klik **[Get Order]**. Delivery Date / Rit **tidak memfilter** order, hanya dibawa ke ASN.
2. **Customer order** dari **TB_R_H0253_ORDER_CONTROL_PRE** (hasil X10): Order Status = **7**, **HOLD_FLAG = N**, **PO_MAPPED_FLAG = N**, data terbaru; order date paling awal dulu per part number (FIFO, key G-TOPAS).
3. **PO supplier** dari **TB_R_PRA_DAILY_ORDER_MANIFEST + TB_R_PRA_DAILY_ORDER_PART**: Crossdock Flag = **X**, data terbaru, qty PO yang belum terpakai, urut Order Date naik (FIFO).
4. **Pre-mapping** per part number, FIFO berdasarkan Customer Order Date (lalu Order Time, Customer Order No, Detailed Item No, Serial No). Satu line boleh terpecah ke beberapa PO; sisa PO tetap terbuka.
5. Hasil disimpan ke tabel temporary **#TB_R_INSTRUCTION** (per sesi): 1 baris per line × PO; sisa line tanpa PO = 1 baris dengan PO_NO NULL.
6. Status unit (Part Number + Customer Order Date) dihitung lalu dikembalikan ke X8.

Pre-mapping **tidak mengubah data permanen**. Mapping sebenarnya dilakukan oleh **[Create ASN]** di X8.

## Unit, case, dan status
| Item | Aturan |
|---|---|
| Unit | Part Number + Customer Order Date |
| Case | 1 case per destinasi; qty per destinasi dijumlahkan jadi 1 case (tidak melebihi pcs/case, boleh dari beberapa line mis. 4 + 2) |
| Case Qty | Jumlah destinasi unit |
| PO Readiness (case) | Jumlah case yang seluruh qty-nya sudah dapat PO |
| CROSSDOCK_STATUS `6` Ready | Semua line unit sudah dapat PO |
| CROSSDOCK_STATUS `7` Not Ready | Masih ada minimal 1 line unit (customer order date yang sama) yang belum dapat PO |
| Created (ASN status `1`) | Setelah Submit ASN di X8 |

## Contoh (PART-C, 6 pcs/case)
- Get Order 14-Oct: hanya PO1 (12 pcs) yang ada → CO-13001 (4), CO-13004 (2), CO-13003 (6) dapat PO; 6 pcs sisa → Case Qty 3, PO Readiness 1, **Not Ready**.
- Get Order 15-Oct: PO2 (6 pcs) ada → semua line dapat PO → PO Readiness 3, **Ready**.
- Line dengan HOLD_FLAG = Y tidak diambil; unit dihitung tanpa line itu.

## #TB_R_INSTRUCTION (temporary, usulan struktur)
| Kolom | Tipe | Keterangan |
|---|---|---|
| INSTRUCTION_ID | BIGINT | Running number within the session |
| CUSTOMER_CD | VARCHAR(7) | H0253.CUSTOMER_CD |
| CUSTOMER_ORDER_NO | VARCHAR(8) | H0253.CUSTOMER_ORDER_NO |
| ORDER_DT | DATE | Customer Order Date (H0253.ORDER_DT) |
| DESTINATION_CD | VARCHAR(7) | H0253.DESTINATION_CD (TB_M_H0125_DESTINATION) |
| DETAILED_ITEM_NO | VARCHAR(4) | H0253.DETAILED_ITEM_NO |
| SERIAL_NO | VARCHAR(7) | H0253.SERIAL_NO |
| PART_NO | VARCHAR(15) | Order part number (H0253.SHIPPING_PART_NO) |
| ORDER_STATUS | VARCHAR(1) | H0253.ORDER_STATUS ('7' Cross Dock) |
| CUST_ORDER_QTY | NUMBER(8) | Order status qty of the customer order line (H0253.ORDER_STATUS_QTY) |
| ASSIGNED_QTY | NUMBER(8) | Qty of the line pre-mapped to this PO (0 for the not-assigned row) |
| REMAINING_ORDER_QTY | NUMBER(8) | Qty of the line still without a PO after this assignment |
| PO_NO | VARCHAR(TBD) | Supplier PO number (Pra Daily Order Manifest); NULL while not assigned |
| MANIFEST_NO | VARCHAR(TBD) | Manifest number |
| MANIFEST_ITEM_NO | VARCHAR(TBD) | Manifest item number (Pra Daily Order Part) |
| PO_ORDER_DT | DATE | Order date of the PO (PO Date) |
| PO_ORDER_QTY | NUMBER(TBD) | Order qty of the PO part |
| SUPPLIER_CD | VARCHAR(TBD) | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) | Supplier plant |
| SUB_SUPPLIER_CD | VARCHAR(TBD) | Sub supplier code |
| SUB_SUPPLIER_PLANT | VARCHAR(TBD) | Sub supplier plant |
| ORDER_TYPE | VARCHAR(TBD) | Order type of the PO |
| DOCK_CD | VARCHAR(TBD) | Dock code |
| ETD_ORI | DATE | Original ETD |
| CROSSDOCK_STATUS | VARCHAR(1) | Status of the unit (Part Number + Customer Order Date): '6' Ready / '7' Not Ready |

## Pesan (log)
| ID | Kapan | Pesan |
|---|---|---|
| LOG1 | Gagal baca / insert | Get Order failed for Delivery Date <DELIVERY_DT> <RIT>: <ERROR_DETAIL>. |
| LOG2 | Error lain | Unexpected error: <ERROR_DETAIL>. |

## Open points
- Struktur fisik TB_R_PRA_DAILY_ORDER_MANIFEST / PART dan kolom qty terpakai (mapped qty).
