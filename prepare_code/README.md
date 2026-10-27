# Prepare code – UISS in Markdown

Markdown copy of every UISS of function list v2 (XD01–XD15), for developers and coding agents. Generated from the UISS specs; regenerate after any spec change:

```bash
python3 prepare_code/build_md.py   # also run by deliverables/function_list_v2/build_all_v2.sh
```

## Functions

| ID | Function | Type | File |
|---|---|---|---|
| XD01 | Cross Dock Part Master Screen | Screen | [uiss/XD01_Screen_CrossDockPartMaster.md](uiss/XD01_Screen_CrossDockPartMaster.md) |
| XD02 | Cross Dock Part Master Upload Batch | Batch | [uiss/XD02_Batch_CrossDockPartMasterUpload.md](uiss/XD02_Batch_CrossDockPartMasterUpload.md) |
| XD03 | Part and Destination Mapping Upload Batch | Batch | [uiss/XD03_Batch_PartDestinationMappingUpload.md](uiss/XD03_Batch_PartDestinationMappingUpload.md) |
| XD04 | Actual Demand Summary Synch to NSP | Batch | [uiss/XD04_Batch_ActualDemandSummarySync.md](uiss/XD04_Batch_ActualDemandSummarySync.md) |
| XD05 | DAD Volume Calculation Batch | Batch | [uiss/XD05_Batch_DADVolumeCalculation.md](uiss/XD05_Batch_DADVolumeCalculation.md) |
| XD06 | IF Cross Dock Master to GTOPAS | Batch | [uiss/XD06_Batch_IFCrossDockMasterToGTOPAS.md](uiss/XD06_Batch_IFCrossDockMasterToGTOPAS.md) |
| XD07 | IF Cross Dock Master to AP POLE | Batch | [uiss/XD07_Batch_IFCrossDockMasterToAPPOLE.md](uiss/XD07_Batch_IFCrossDockMasterToAPPOLE.md) |
| XD08 | Order Control Information to NSP Batch | Batch | [uiss/XD08_Batch_OrderControlInfoToNSP.md](uiss/XD08_Batch_OrderControlInfoToNSP.md) |
| XD09 | Mapping Customer Order and PO Batch | Batch | [uiss/XD09_Batch_MappingCustomerOrderPO.md](uiss/XD09_Batch_MappingCustomerOrderPO.md) |
| XD10 | ASN Cross Dock Creation Screen | Screen | [uiss/XD10_Screen_ASNCrossDockCreation.md](uiss/XD10_Screen_ASNCrossDockCreation.md) |
| XD11 | Change Order Number Screen | Screen | [uiss/XD11_Screen_ChangeOrderNumber.md](uiss/XD11_Screen_ChangeOrderNumber.md) |
| XD12 | Cancel Crossdock Customer Order Batch | – | removed 23-Oct (status 2 handled by XD08, qty in an ASN moved by XD11). |
| XD13 | Destination Master Synch into NSP | Batch | [uiss/XD13_Batch_DestinationMasterSync.md](uiss/XD13_Batch_DestinationMasterSync.md) |
| XD14 | DAD Volume Calculation Result Screen (Buffer) | – | not used (decision 19-Oct). |
| XD15 | ASN Crossdock Inquiry Screen (Buffer) | Screen | [uiss/XD15_Screen_ASNCrossdockInquiry.md](uiss/XD15_Screen_ASNCrossdockInquiry.md) |

## Shared references

- [tables.md](tables.md): all tables (new and existing) with columns, merged per table name.
- [messages.md](messages.md): display / logging messages per function.
- Business process flow: `deliverables/function_list_v2/bpf/Crossdock_BPF_Level2.xlsx` (F1 master, F2 daily order to ASN, F4 hold & cancel).
- ERD / DB structure: `deliverables/function_list_v2/erd/`.
- Simulation data (16–22 Oct, PART-X): `deliverables/simulasi_asn_rev.xlsx`; prototype: `app/` (menu ASN Simulation / ASN Creation).
- UR / business logic summary: `deliverables/function_list_v2/XD01-XD15_UR_Business_Logic_Summary.xlsx`.

## Business Logic ASN

1. Customer Order Date (D) → PO Date D+1: 1 PO per Part Number per Customer Order Date.
2. Total customer order qty of all destinations = PO qty; less → abnormality (Short PO), the rest waits for the split PO.
3. One customer order line can be in several ASNs; a separate receipt splits the H0253 line (new SERIAL_NO).
4. PO_MAPPED_FLAG is set by Create ASN (Y when the whole line is in TB_R_INSTRUCTION).
5. Ready cases are sent following CUT_FLAG (from case 1 up to a cut).
6. Per Part Number, the oldest Customer Order Date first (no skip); held lines are not counted.

## Conventions

- Flows are Mermaid diagrams converted from the UISS flowcharts; screenshots link to `deliverables/uiss_screens/`.
- Sections follow the UISS sheets: Screen = General, Screen Flow, Layout, Item, Data Map, Operation, Messages, Tables, Sample Input; Batch = General, Function Flow, Data Map, Function Description, Logging, Appendix, Tables, Sample Input.
