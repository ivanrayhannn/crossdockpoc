# XD10 – ASN Cross Dock Creation Screen

> Generated from `deliverables/function_list_v2/specs/XD10_spec.json` (UISS `XD10_UISS_Screen_ASNCrossDockCreation.xlsx`). Do not edit by hand: change the spec and run `python3 prepare_code/build_md.py`. Document names: GTOPAS / NSP (prototype: G-System / Supplier System).

| Phase | Project | Block | Function | Created | By | Type |
|---|---|---|---|---|---|---|
| DR | Crossdock Optimization | Screen | XD10 ASN Cross Dock Creation Screen | 18-Oct-26 | FID Rayhan | screen |

## Revision

| Rev | Author | Date | Reviewed by | Description |
|---|---|---|---|---|
| 0.1 | FID Rayhan | 18-Oct-26 |  | Initial Draft |
| 0.2 | FID Rayhan | 11-Nov-26 |  | Pre-mapping refers to the pouring rule of XD09 4.2 (FB-172). |
| 0.3 | FID Rayhan | 13-Nov-26 |  | Sub screen [Hold per Part] (D/S team): one row per Part Number, Hold check box with Edit / Save / Cancel; expanded customer orders without PO information (TB_R_CROSSDOCK_PART_HOLD, MSG12). |
|  |  |  |  | Hold (D/S) check box per case next to PO Status, changed with [Edit hold] / [Save] / [Cancel] per Part Number + Customer Order Date (TB_R_CROSSDOCK_CASE_HOLD, MSG14). |
|  |  |  |  | Case content split into the columns Destination, Customer Order No and Order Qty. |
|  |  |  |  | Dummy data: supplier 5001-1 / 5002-1, PO-0001.., MF-0001.., destinations Korea / Japan / Taiwan / Australia. |
| 0.4 | FID Rayhan | 14-Nov-26 |  | Hold per case: the held pcs leave the unit and take no PO; their PO qty goes to the next orders; the other cases stay Ready. Held lines listed below the cases (On hold, PO released). |
|  |  |  |  | Release of a held line: goes to the end of its Customer Order Date, keeps priority over newer dates (FB-183, HOLD_FLAG). |
|  |  |  |  | [Save] of a hold: confirmation and success pop up in Indonesian (MSG15 / MSG16), delivery plan refreshed. |
|  |  |  |  | PO check line replaced by the PO information pop up on the ASN status (MSG17); Hold chip with hold information (MSG18). |
|  |  |  |  | Bordered unit table and case grid; destination once per case; same PO merged; summary line of the delivery plan removed. |
|  |  |  |  | Destination detail (Destination / pcs, Hold Flag) hidden on the screen for now (FB-184). |
| 0.5 | FID Rayhan | 16-Nov-26 |  | Source of the delivery plan: TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D (table concept of the DR XD09) instead of #TEMP_INSTRUCTION. |
|  |  |  |  | Case No of the ASN = CASE_NO of the draft made by XD09; Submit ASN no longer generates the case numbers (ASN number as existing). |
|  |  |  |  | No new table TB_R_PRA_DAILY_ORDER_MAPPED: [Create ASN] reduces REMAIN_QTY of TB_R_PRA_DAILY_ORDER_PART; Back / Cancel / submit error add it back. |

## 1. General

### Objective

- To get the crossdock customer orders for a Delivery Date and Rit and pre-map them to supplier POs ([Search], XD09 Mapping Customer Order and PO Batch).
- To display the delivery plan per Part Number + Customer Order Date with the supplier cases in H0253 order (Case Qty, PO Readiness, ASN options, ASN Status Ready / Partially Ready / Not Ready). Units fully Created or without any pre-mapped case are not listed.
- To let the D/S team (super admin) see the units of all suppliers, the destination detail and hold / release a destination of a unit.
- To tick the supplier cases to send (check box per case, from case 1, cases that belong together) of one Supplier Code + Supplier Plant, map them to their POs (TB_R_INSTRUCTION), review the cases, download the case labels and submit the ASN.
- Submit ASN runs in the background with a Submit ID and follows the existing ASN submit of NSP (refer 5.7).
- Submit ASN (decided 20-Oct, existing structure GTOPAS SPS DB): one TB_R_DAILY_ORDER_MANIFEST row per Pra Daily Order manifest of the cases (same ASN_NO) and one TB_R_DAILY_ORDER_PART row per manifest item and case; the ASN number is auto generated (last sequence ASN_LAST_SEQ in TB_R_CASE_LABEL_LAST_SEQ); the case numbers come from CASE_NO of the draft (made by XD09 from TB_R_CASE_LABEL_LAST_SEQ, DR XD09); PART_NAME from TB_M_PART_MASTER.

### Display order – Delivery plan

| Field | Order |
|---|---|
| ASN Status (Ready, Not Ready) | - |
| Part Number | Ascending |
| Customer Order Date | Ascending |

### Display order – Destination detail (D/S)

| Field | Order |
|---|---|
| Destination, by first appearance in the unit | - |

### Display order – Case List

| Field | Order |
|---|---|
| Selected unit (Part Number, Customer Order Date) | Ascending |
| Destination, by first appearance in the unit | - |

### Buttons

| Button | Function |
|---|---|
| Search | Run XD09 (Mapping Customer Order and PO): get the customer orders and pre-map them to POs for the chosen Delivery Date and Rit; display the delivery plan. |
| Detail (expand, D/S) | D/S team only: show / hide the destinations (cases) of a unit with Qty, Pcs/Case and Hold Flag. Hidden on the screen for now (14-Nov, FB-184), with the destination Hold Flag; shown again on request. |
| Customer orders (expand, D/S) | D/S team only: show / hide the customer order lines of a destination (Customer Order No, Detailed Item No, Qty, PO No, PO Date). |
| Hold / Release (D/S) | D/S team only: set HOLD_FLAG of every order line of the destination (part number + customer order date + destination) to 'Y' (hold) or 'N' (release). Hidden for now with the destination detail (FB-184). |
| Hold per Part (D/S) | D/S team only: open the sub screen Hold per Part Number (one row per part, expanded to its customer orders). |
| Edit / Save / Cancel (part, sub screen) | Sub screen, D/S team only: [Edit] enables the Hold check box of the part; [Save] writes HOLD_FLAG 'Y' / 'N' in TB_R_CROSSDOCK_PART_HOLD; [Cancel] discards. |
| Edit hold / Save / Cancel (case, D/S) | Per Part Number + Customer Order Date, D/S team only: [Edit hold] enables the Hold (D/S) check boxes of its cases and of its held lines; [Save] writes TB_R_CROSSDOCK_CASE_HOLD (case ticked = its lines inserted / HOLD_QTY added, held line unticked = deleted); [Cancel] discards. [Save] shows a confirmation (message no. 15) first, then message no. 16, and refreshes the delivery plan. |
| Clear selection | Untick all selected units. |
| Create ASN | Check that the selected units are of one supplier and not held, map the chosen blocks to their POs (insert TB_R_INSTRUCTION) and open the Case List sub screen. |
| Back | Return from the Case List to ASN Crossdock Creation without submitting; the rows of TB_R_INSTRUCTION are deleted and the mapping is released. |
| PO detail (expand) | Show / hide PO No, Manifest No, Manifest Item and PO Qty of a case. |
| Download Case Label | Download the labels of all cases of the ASN. Label format follows the existing case label: 1 case label = 1 case of 1 destination, may list several customer order numbers. |
| Cancel | Same as Back. |
| Submit ASN | Ask for confirmation, then hand the ASN to the submit process with a Submit ID (refer 5.7); the result is written to the log. |
| Yes / No | Confirmation of Submit ASN (Submit? Y / N). |
| OK | Close the success notification. |

### Screen modes (E = enabled, D = disabled)

| Mode | Section | Description | Search | Detail (expand, D/S) | Customer orders (expand, D/S) | Hold / Release (D/S) | Hold per Part (D/S) | Edit / Save / Cancel (part, sub screen) | Edit hold / Save / Cancel (case, D/S) | Clear selection | Create ASN | Back | PO detail (expand) | Download Case Label | Cancel | Submit ASN | Yes / No | OK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Initial Mode | Delivery | Delivery Date = today (business date); Rit = first rit of the date; Route displayed | E | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D |
| Initial Mode | Delivery plan | Empty: 'Choose the Delivery Date and Rit, then click Search.' Filters disabled | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D |
| List Mode - Supplier | Delivery | Refer 1.a | E | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D |
| List Mode - Supplier | Delivery plan | Units of the login supplier (Supplier Code + Plant) only; unit rows with their supplier case rows (check box per case, no destinations); Part Number / Status filters | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D |
| List Mode - Supplier | Selection bar | Enabled when Ready units are ticked | D | D | D | D | D | D | D | E | E | D | D | D | D | D | D | D |
| List Mode - D/S Team | Delivery plan | All suppliers (Supplier · Plant column) plus the destination detail with Hold Flag; a unit with all destinations on hold is listed as On Hold. The D/S team is super admin: it can also create and submit | D | E | E | E | E | E | E | D | D | D | D | D | D | D | D | D |
| List Mode - D/S Team | Selection bar | Refer 2.c | D | D | D | D | D | D | D | E | E | D | D | D | D | D | D | D |
| Case List Mode (sub screen) | ASN summary | ASN No (assigned on submit), supplier, Delivery Date · Rit · Route, Delivery Qty, cases | D | D | D | D | D | D | D | D | D | E | D | D | D | D | D | D |
| Case List Mode (sub screen) | Case list | Case Number, Part Number, Qty; expand PO detail | D | D | D | D | D | D | D | D | D | D | E | E | D | D | D | D |
| Case List Mode (sub screen) | Footer | Submit enabled when there are cases | D | D | D | D | D | D | D | D | D | D | D | D | E | E | D | D |
| Confirmation / Notification | Submit confirmation | 'Submit ASN?' Yes / No | D | D | D | D | D | D | D | D | D | D | D | D | D | D | E | D |
| Confirmation / Notification | Success notification | Submit ID banner on the delivery plan; result in Log Monitoring | D | D | D | D | D | D | D | D | D | D | D | D | D | D | D | E |

- 1) Each unit row shows its supplier case rows in H0253 order (XD09). The check box of a case is enabled only when the case and every earlier case have a PO (Ready, message no. 2 as tooltip otherwise).
- 2) Cases that belong together (Case Group = GROUP_SEQ of XD09, the cases up to a CUT_FLAG Y; not shown as a column) are always sent together, so that at receiving every destination completes its warehouse case. The ticked cases of a unit start at case 1: ticking case n ticks the earlier cases and the other cases of its group (message no. 10); unticking case n unticks its group and the later cases. The unit check box ticks all Ready cases. Units of different Customer Order Dates and Part Numbers can be ticked together.
- 3) The supplier sees the unit rows and their case rows (Case, Qty, Remaining Qty (not assigned), PO, PO Status, check box) without destinations; the Content of a case (destinations, customer orders), the destination detail and Hold / Release are shown to the D/S team only.
- 4) Search is enabled when Delivery Date is filled and a Rit is available (message no. 5 otherwise).
- 5) One ASN is for one Supplier Code + Supplier Plant: the D/S team may tick units of several suppliers, [Create ASN] then shows message no. 9.

## 2. Screen flow

### Screen Flow - ASN Crossdock

```mermaid
flowchart LR
  c[["ASN Crossdock Creation"]]
  l[["Case List (sub screen)"]]
  n>"Success notification"]
  i[["ASN Inquiry (XD15)"]]
  c -->|Create ASN| l
  l -->|Back / Cancel| c
  l -->|Submit? Y| n
  n -->|OK| c
  c -->|menu| i
```

### Screen Flow - Search, Check Ready Status and Create ASN

```mermaid
flowchart TB
  s(["START"])
  e>"Choose Delivery Date and Rit, click Search"]
  g["XD09: get customer orders, pre-map to PO (TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D)"]
  d{"First block Ready? (blocks in H0253 order)"}
  w>"Not Ready: check box disabled"]
  p["Tick cases (from case 1, cases that belong together), Create ASN: insert TB_R_INSTRUCTION"]
  l["Case List: Download Case Label"]
  d2{"Submit?"}
  p2["Save ASN (status 1 Created), show success"]
  db[("TB_R_DAILY_ORDER_MANIFEST / _PART")]
  x(["END"])
  s --> e
  e --> g
  g --> d
  d -->|N| w
  d -->|Y| p
  p --> l
  l --> d2
  d2 -->|N| l
  d2 -->|Y| p2
  p2 -.-> db
  p2 --> x
```

## 3. Screen layout

### 1. Initial Mode: choose Delivery Date and Rit, then Search

![1. Initial Mode: choose Delivery Date and Rit, then Search](../../deliverables/uiss_screens/asn_crossdock/c_01_initial.png)

### 2. Delivery plan after Search (supplier view, 18-Oct, simulasi_asn_rev.xlsx): PART-X 17-Oct, cases 1-4 Ready, case 5 Not Ready; ASN Status Partially Ready + Short PO (click for the PO information)

![2. Delivery plan after Search (supplier view, 18-Oct, simulasi_asn_rev.xlsx): PART-X 17-Oct, cases 1-4 Ready, case 5 Not Ready; ASN Status Partially Ready + Short PO (click for the PO information)](../../deliverables/uiss_screens/asn_crossdock/c_02_delivery_plan.png)

### 2a. Click on the ASN status (Partially Ready / Short PO): PO information of the unit in Indonesian (message no. 17)

![2a. Click on the ASN status (Partially Ready / Short PO): PO information of the unit in Indonesian (message no. 17)](../../deliverables/uiss_screens/asn_crossdock/c_02a_po_info.png)

### 3. D/S team: destination detail (warehouse cases, Hold Flag) and customer orders of a destination (open qty, cases, PO) [destination detail hidden on the screen for now, 14-Nov]

![3. D/S team: destination detail (warehouse cases, Hold Flag) and customer orders of a destination (open qty, cases, PO) [destination detail hidden on the screen for now, 14-Nov]](../../deliverables/uiss_screens/asn_crossdock/c_03_ds_detail.png)

### 4. D/S team: Japan (CO-14104) on hold; the H0253 order and the cases are computed again without it [destination detail hidden on the screen for now, 14-Nov]

![4. D/S team: Japan (CO-14104) on hold; the H0253 order and the cases are computed again without it [destination detail hidden on the screen for now, 14-Nov]](../../deliverables/uiss_screens/asn_crossdock/c_04_ds_hold.png)

### 4a. D/S team: [Edit hold] on PART-X 17-Oct, Hold (D/S) of case 4 (CO-14109 Taiwan) ticked, [Save] / [Cancel] shown; content split into Destination / Customer Order No / Order Qty

![4a. D/S team: [Edit hold] on PART-X 17-Oct, Hold (D/S) of case 4 (CO-14109 Taiwan) ticked, [Save] / [Cancel] shown; content split into Destination / Customer Order No / Order Qty](../../deliverables/uiss_screens/asn_crossdock/c_04a_ds_case_edit.png)

### 4a-2. [Save]: confirmation (message no. 15) listing what is held / released

![4a-2. [Save]: confirmation (message no. 15) listing what is held / released](../../deliverables/uiss_screens/asn_crossdock/c_04g_ds_hold_confirm.png)

### 4a-3. [Ya, simpan]: saved message (message no. 16); the delivery plan is refreshed behind it

![4a-3. [Ya, simpan]: saved message (message no. 16); the delivery plan is refreshed behind it](../../deliverables/uiss_screens/asn_crossdock/c_04h_ds_hold_saved.png)

### 4b. After [Save]: CO-14109 Taiwan 6 pcs On Hold below the cases (PO released); its PO-0003 qty goes to CO-14110 Australia, so the 4 cases left are all Ready

![4b. After [Save]: CO-14109 Taiwan 6 pcs On Hold below the cases (PO released); its PO-0003 qty goes to CO-14110 Australia, so the 4 cases left are all Ready](../../deliverables/uiss_screens/asn_crossdock/c_04b_ds_reduce.png)

### 4b-2. Click on the Hold chip next to the status: hold information of the unit in Indonesian (message no. 18)

![4b-2. Click on the Hold chip next to the status: hold information of the unit in Indonesian (message no. 18)](../../deliverables/uiss_screens/asn_crossdock/c_04i_hold_info.png)

### 4c. Supplier view: cases 1-4 Ready, the held 6 pcs shown On Hold (D/S) and cannot be ticked

![4c. Supplier view: cases 1-4 Ready, the held 6 pcs shown On Hold (D/S) and cannot be ticked](../../deliverables/uiss_screens/asn_crossdock/c_04c_supplier_reduce.png)

### 4d. D/S team: sub screen Hold per Part Number: one row per Part Number (status, Hold check box, [Edit]), expanded to its customer orders

![4d. D/S team: sub screen Hold per Part Number: one row per Part Number (status, Hold check box, [Edit]), expanded to its customer orders](../../deliverables/uiss_screens/asn_crossdock/c_04d_ds_supplier_hold.png)

### 4e. Sub screen: PART-X held ([Edit], tick Hold, [Save])

![4e. Sub screen: PART-X held ([Edit], tick Hold, [Save])](../../deliverables/uiss_screens/asn_crossdock/c_04f_ds_supplier_hold_on.png)

### 4f. Supplier view: the held part stays visible, On Hold, check boxes disabled (message no. 12)

![4f. Supplier view: the held part stays visible, On Hold, check boxes disabled (message no. 12)](../../deliverables/uiss_screens/asn_crossdock/c_04e_supplier_on_hold.png)

### 5. Case 3 of PART-X 17-Oct ticked: cases 1-3 are selected (the selection always starts at case 1)

![5. Case 3 of PART-X 17-Oct ticked: cases 1-3 are selected (the selection always starts at case 1)](../../deliverables/uiss_screens/asn_crossdock/c_05_selected.png)

### 5a. Other session (D/S team) holds a destination of a ticked unit

![5a. Other session (D/S team) holds a destination of a ticked unit](../../deliverables/uiss_screens/asn_crossdock/c_05a_ds_hold_other_session.png)

### 5b. Create ASN: hold message, the whole create fails

![5b. Create ASN: hold message, the whole create fails](../../deliverables/uiss_screens/asn_crossdock/c_05c_hold_conflict.png)

### 5c. Delivery plan refreshed automatically, all cases unticked

![5c. Delivery plan refreshed automatically, all cases unticked](../../deliverables/uiss_screens/asn_crossdock/c_05d_after_refresh.png)

### 5d. D/S team: units of two suppliers ticked (PART-D of supplier 5002, prototype only), Create ASN: one supplier per ASN

![5d. D/S team: units of two suppliers ticked (PART-D of supplier 5002, prototype only), Create ASN: one supplier per ASN](../../deliverables/uiss_screens/asn_crossdock/c_05e_supplier_conflict.png)

### 6. Case List sub screen: cases 1-4 of PART-X 17-Oct = ASN0003

![6. Case List sub screen: cases 1-4 of PART-X 17-Oct = ASN0003](../../deliverables/uiss_screens/asn_crossdock/c_06_case_list.png)

### 7. Case List: PO detail of a case

![7. Case List: PO detail of a case](../../deliverables/uiss_screens/asn_crossdock/c_07_case_expand.png)

### 8. Submit confirmation

![8. Submit confirmation](../../deliverables/uiss_screens/asn_crossdock/c_08_confirm.png)

### 9. Submit ID banner (result in Log Monitoring)

![9. Submit ID banner (result in Log Monitoring)](../../deliverables/uiss_screens/asn_crossdock/c_09_submit_id.png)

### 10. Delivery plan after submit: only case 5 (CO-14110) is left, Not Ready until the split PO PO-0004

![10. Delivery plan after submit: only case 5 (CO-14110) is left, Not Ready until the split PO PO-0004](../../deliverables/uiss_screens/asn_crossdock/c_10_list_after.png)

## 4. Item description

| No | Item | Source | Field | Type | Len | I/O | Control | Justified | Initial | Req | Format | Validation | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **<Delivery Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1 | Delivery Date | Key-in | - | Date | - | I | Date picker | Left | Today (business date) | Y | DD-Mon-YYYY | Mandatory; today or later | Changing it reloads the Rit list. |
| 2 | Rit | Route master (existing) | Rit (existing) | Char | - | I | Combo Box | Left | First rit of the date | Y | - | Mandatory | Rits of the Delivery Date; Sunday none ('No rit cycle'), Saturday one. |
| 3 | Route | Route master (existing) | Route (existing) | Char | - | O | Text box (disabled) | Left | - | N | - | - | Route of the Rit. |
| 4 | Search | - | - | - | - | I | Button | Center | Enabled | N | - | - | Refer Operation Description 5.1. |
| **<Delivery Plan Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Counter | Computed | - | Char | - | O | Label | Left | - | N | - | - | '{Delivery Date} · {Rit} · {Route} — {n} units · {r} ready · {w} not ready'. |
| 6 | Part Number (filter) | Key-in | - | Char | 15 | I | Combo Box | Left | All | N | - | - | Filters the delivery plan at once. |
| 7 | Status (filter) | Key-in | - | Char | - | I | Combo Box | Left | All | N | - | - | All / Ready / Not Ready (D/S team also On Hold). Filters at once. |
| 8 | Select (check box) | Key-in | - | Char | 1 | I | CheckBox | Center | <unchecked> | N | - | Enabled when the first block of the unit is Ready | Ticks / unticks all Ready cases of the unit (partly ticked when only some cases are ticked). Refer Screen Mode remark 2). |
| 9 | Supplier · Plant (D/S) | TB_T_INSTRUCTION_D | SUPPLIER_CD / SUPPLIER_PLANT | Char | - | O | Label | Left | - | N | {code} · {plant} | - | D/S team only (all suppliers). The supplier sees its own Supplier Code + Plant only. |
| 10 | Customer Order Date | TB_T_INSTRUCTION_H | ORDER_DT | Date | - | O | Label | Left | - | N | DD-Mon-YYYY | - | Customer Order Date of the unit. |
| 11 | Part Number | TB_T_INSTRUCTION_H | SHIPPING_PART_NO | Char | 15 | O | Label | Left | - | N | - | - | Part number of the unit (distinct per Customer Order Date). Part name is not shown. |
| 12 | Case Qty | TB_T_INSTRUCTION_H | CASE | Number | - | O | Label | Right | - | N | ZZ9 | - | Number of supplier cases of the unit: open qty / pcs/case, cut in H0253 order (e.g. 30 pcs, 6 pcs/case = 5 cases); a case can hold several destinations. |
| 13 | PO Readiness (case) | Computed | - | Number | - | O | Label | Right | - | N | ZZ9 | - | Ready cases: cases whose whole qty is pre-mapped to a PO; red when lower than Case Qty. Pcs held by the D/S team (Hold per case) are not in the cases and not counted (see the Hold chip of ASN Status). |
| 14 | ASN Status | TB_T_INSTRUCTION_D | CROSSDOCK_STATUS | Char | 1 | O | Label | Left | - | N | - | - | Ready (all blocks '6', green) / Partially Ready (first block '6', a later block '7', amber) / Not Ready (first block '7', row highlighted) / On Hold (D/S only). Refer 5.2. Partially Ready, Not Ready and Short PO are a button: a click opens the PO information of the unit (message no. 17): customer order qty, regular / split PO with qty and date, Short PO and the qty still waiting, ready cases, pcs on hold. The PO check line above the cases is no longer shown. A Hold chip (grey button) is shown next to the status when the unit has a hold (Part Number on hold, pcs held per case, or a destination on hold for the D/S team); a click opens the hold information (message no. 18). The text lines under the status (pcs on hold, Part Number on hold, destinations on hold) are no longer shown. |
| 15 | Detail (expand, D/S) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Shown to the D/S team only. Opens the destination detail. |
| **<Supplier Cases of a Unit (H0253 order)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 16 | Select case (check box) | Key-in | - | Char | - | I | CheckBox | Center | <unchecked> | N | - | Enabled only when the case and every earlier case have a PO | One check box per supplier case. The selection always starts at case 1 and takes the cases that belong together (Case Group = GROUP_SEQ of XD09, not shown on the screen): ticking case n ticks the earlier cases and the other cases of its group (message no. 10, e.g. tick case 2 -> cases 2-3 belong together, so cases 1-3); unticking case n unticks its group and the later cases. Refer 5.4. |
| 17 | Case | TB_T_INSTRUCTION_D | CASE_NO | Number | - | O | Label | Right | - | N | Z9 | - | Supplier case number in H0253 order (PCS_CASE pcs). |
| 18 | Qty (pcs) | TB_T_INSTRUCTION_D | SUM(ORDER_STATUS_QTY) | Number | - | O | Label | Right | - | N | ZZZ9 | - | Pcs of the case (= PCS_CASE). |
| 19 | Remaining Qty (not assigned) | TB_T_INSTRUCTION_D | COUNT(pcs) with PO_NO NULL | Number | - | O | Label | Right | - | N | ZZZ9 | - | Pcs of the case without a PO yet (sum of the slices with PO_NO NULL); 0 when the whole case is assigned; red when > 0. |
| 20 | Destination (D/S team) | TB_T_INSTRUCTION_D | DESTINATION_CD | Char | - | O | Grid | Left | - | N | - | - | D/S team only: destination code and name of the case, shown once per case (cell merged over its lines); a supplier case holds one destination. |
| 21 | Customer Order No (D/S team) | TB_T_INSTRUCTION_D | CUSTOMER_ORDER_NO | Char | - | O | Grid | Left | - | N | - | - | D/S team only: one row per customer order line in the case (the case-level cells are merged over these rows). |
| 22 | Order Qty (D/S team) | TB_T_INSTRUCTION_D | SUM(ORDER_STATUS_QTY) | Number | - | O | Grid | Right | - | N | - | - | D/S team only: pcs of the line, one per row (sum = case qty). |
| 23 | PO | TB_T_INSTRUCTION_D | PO_NO / SUM(PO_QTY) | Char | - | O | Label | Left | - | N | {PO No} {qty} | - | PO and assigned qty, e.g. PO-0003 · 6. Rows of the case with the same PO are merged into one cell; supplier view: one row per PO of the case. Held line: "PO released". |
| 24 | PO Status | TB_T_INSTRUCTION_D | CROSSDOCK_STATUS | Char | - | O | Label | Left | - | N | - | - | '6' Ready (green) / '7' Not Ready (amber): the case or an earlier case has no PO yet. 'On Hold (D/S)' (grey) for a held line (Hold per case) or when the part is on hold; check box disabled (message no. 14 / 12). |
| 25 | Hold (D/S) | Key-in / TB_R_CROSSDOCK_CASE_HOLD | HOLD_QTY | Char | - | I | Check Box | Center | Unticked (case) / ticked (held line), disabled | N | - | - | D/S team only, next to PO Status: enabled after [Edit hold] of the unit. Case row: tick = hold the case; after [Save] its pcs leave the unit (no PO) and are listed as held lines. Held line row (On Hold, ticked): untick = release; the pcs come back to the unit and take PO again at the next Search (refer 5.3). |
| 26 | Edit hold / Save / Cancel | - | - | - | - | I | Button | Center | Edit hold | N | - | - | D/S team only, per Part Number + Customer Order Date (above the cases, right side): [Edit hold] enables the Hold (D/S) check boxes; [Save] asks for confirmation (message no. 15), stores the holds, shows message no. 16 and refreshes the delivery plan (the selection of the unit is cleared); [Save] without a change just closes the edit; [Cancel] discards. Not shown for a part on hold. Refer 5.3. |
| **<Destination Detail (D/S team only)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 27 | Destination | TB_T_INSTRUCTION_D | DESTINATION_CD | Char | 7 | O | Grid | Left | - | N | {code} · {name} | - | One row per destination with its number of cases (qty / pcs/case); name from TB_M_H0125_DESTINATION. |
| 28 | Case | Computed | - | Number | - | O | Grid | Right | - | N | 9 | - | 1; 0 when the destination is on hold. |
| 29 | Qty (pcs) | TB_T_INSTRUCTION_D | CUST_ORDER_QTY | Number | 8 | O | Grid | Right | - | N | ZZ,ZZ9 | - | Sum of the order qty of the destination; '(on hold)' when held. |
| 30 | Pcs/Case | Part master | PCS_PER_CASE | Number | - | O | Grid | Right | - | N | ZZ9 | - | Pieces per case of the part (next to Qty). |
| 31 | Customer orders (expand, D/S) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Opens the customer order lines of the destination. |
| **<Customer Orders of a Destination (D/S team only)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 32 | Customer Order No / Detailed Item No | TB_T_INSTRUCTION_D | CUSTOMER_ORDER_NO / DETAILED_ITEM_NO | Char | - | O | Grid | Left | - | N | - | - | Original order row, e.g. order A 4 pcs and order B 2 pcs to Korea. |
| 33 | Qty (pcs) / PO No / PO Date | TB_T_INSTRUCTION_D | CUST_ORDER_QTY / PO_NO / PO_DT | Char | - | O | Grid | Left | - | N | - | - | Pre-mapping of the line. |
| 34 | Hold / Release (D/S) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Hold Flag of the destination: 'N · Hold' sets Y, 'Y · Release' sets N on every order line of the destination. Refer 5.3. |
| **<Selection Bar Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 35 | Selection summary | Computed | - | Char | - | O | Label | Left | - | N | - | - | '{n} units · {c} cases · {q} pcs selected · {units}'. Empty: hint that cases of different units / dates can go into one ASN. |
| 36 | Clear selection | - | - | - | - | I | Button | Center | Disabled | N | - | - | Unticks all cases. |
| 37 | Create ASN | - | - | - | - | I | Button | Center | Disabled | N | - | - | Refer Operation Description 5.4. |
| **<Case List Sub Screen - ASN Summary>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 38 | Back | - | - | - | - | I | Button | Center | Enabled | N | - | - | Returns to ASN Crossdock Creation without submitting; the draft mapping is released. |
| 39 | ASN No | TB_R_DAILY_ORDER_MANIFEST | ASN_NO | Char | TBD | O | Label | Left | - | N | - | - | Existing ASN numbering; 'auto · assigned on submit'. |
| 40 | Supplier · Plant | TB_T_INSTRUCTION_D | SUPPLIER_CD / SUPPLIER_PLANT | Char | TBD | O | Label | Left | - | N | - | - | Supplier of the cases (one Supplier Code + Plant per ASN). |
| 41 | Delivery Date · Rit · Route | TB_R_INSTRUCTION | DELIVERY_DT / RIT_CYCLE / ROUTE | Char | - | O | Label | Left | - | N | - | - | From the Search. |
| 42 | Delivery Qty | Computed | - | Number | - | O | Label | Left | - | N | ZZ,ZZ9 pcs | - | Total pieces of the ASN. |
| 43 | Cases | Computed | - | Number | - | O | Label | Left | - | N | N cases | - | Number of cases. |
| **<Case List Sub Screen - Case List>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 44 | Download Case Label | - | - | - | - | I | Button | Center | Enabled | N | - | - | Downloads the labels of all cases (existing label format). |
| 45 | PO detail (expand) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Opens the PO detail of the case. |
| 46 | Case Number | TB_R_INSTRUCTION | CASE_NO | Char | - | O | Grid | Left | - | N | Case {n} | - | Case sequence; the case number is auto generated on submit by checking the last sequence (existing table). |
| 47 | Part Number | TB_R_INSTRUCTION | PART_NO | Char | 15 | O | Grid | Left | - | N | - | - | Supplier case of PCS_CASE pcs in H0253 order; a case can hold several destinations. |
| 48 | Qty / Total | TB_R_INSTRUCTION | QTY | Number | - | O | Grid | Right | - | N | ZZ,ZZ9 | - | Pieces of the case; total of all cases. |
| 49 | PO No / Manifest No / Manifest Item / PO Qty | TB_R_INSTRUCTION | PO_NO / MANIFEST_NO / MANIFEST_ITEM / ORDER_QTY | Char | - | O | Grid | Left | - | N | - | - | Expanded PO detail of the case. |
| 50 | Cancel | - | - | - | - | I | Button | Center | Enabled | N | - | - | Same as Back. |
| 51 | Submit ASN | - | - | - | - | I | Button | Center | Enabled | N | - | - | Refer Operation Description 5.5. |
| 52 | No rit cycle message | Computed | - | Char | - | O | Label | Left | - | N | - | - | Message no. 5 when no rit is available. |
| **<Sub Screen Hold per Part Number (D/S team only)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 53 | Supplier Code · Plant | Supplier master | SUPPLIER_CD / SUPPLIER_PLANT | Char | - | O | Label | Left | - | N | - | - | One section per supplier + plant: supplier name and number of part numbers. |
| 54 | Part Number (row) | TB_T_INSTRUCTION_D | PART_NO | Char | - | O | Label | Left | - | N | - | - | One row per Part Number with open customer orders: number of customer orders, Customer Order Dates and pcs. Expand to see its customer orders. |
| 55 | Hold status | TB_R_CROSSDOCK_PART_HOLD | HOLD_FLAG | Char | - | O | Label | Left | - | N | - | - | 'On Hold' (row highlighted) / 'Not on hold'. |
| 56 | Hold (check box) | Key-in / TB_R_CROSSDOCK_PART_HOLD | HOLD_FLAG | Char | - | I | Check Box | Center | Saved value (disabled) | N | - | - | On the Part Number row; enabled after [Edit]. Saved with [Save]: Y = every customer order of the part (all Customer Order Dates) is On Hold (check boxes on the delivery plan disabled, message no. 12). |
| 57 | Edit / Save / Cancel | - | - | - | - | I | Button | Center | Edit | N | - | - | [Edit] enables the Hold check box of the part; [Save] stores it; [Cancel] discards. Refer 5.3. |
| 58 | Customer Order Date / Customer Order No / Destination / Qty / Case | TB_T_INSTRUCTION_D | ORDER_DT / CUSTOMER_ORDER_NO / DESTINATION_CD / SUM(ORDER_STATUS_QTY) / CASE_NO | Char | - | O | Grid | Left | - | N | - | - | Expanded list: one row per customer order line of the part (all Customer Order Dates, oldest first, not grouped); no PO information. |
| 59 | Back to ASN Crossdock Creation | - | - | - | - | I | Button | Center | Enabled | N | - | - | Closes the sub screen. |

## 5. Data edit mapping

#### 1. Update TB_R_H0253_ORDER_CONTROL_PRE – Every order line of the destination of the button
- Source: Hold / Release (D/S)
- Destination keys: SHIPPING_PART_NO + ORDER_DT + DESTINATION_CD = Unit and destination of the button

| Source field | Destination field | Description |
|---|---|---|
|  | HOLD_FLAG | 'Y' (hold) / 'N' (release) |
|  | PO_MAPPED_FLAG | Not changed |
|  | UPDATE_BY | Login user ID |
|  | UPDATE_DT | Server system date-time |
|  | CUSTOMER_CD | Not changed |
|  | CUSTOMER_ORDER_NO | Not changed |
|  | ORDER_DT | Not changed |
|  | ORDER_TIME | Not changed |
|  | DESTINATION_CD | Not changed |
|  | DETAILED_ITEM_NO | Not changed |
|  | SERIAL_NO | Not changed |
|  | TOPAS_ORDER_TYPE | Not changed |
|  | DEMAND_HISTORY_UPDATE_DT | Not changed |
|  | SHIPPING_MAKER_CD | Not changed |
|  | SHIPPING_PART_NO | Not changed |
|  | ORIGINAL_SHIPPING_QTY | Not changed |
|  | ORDER_STATUS_QTY | Not changed |
|  | ORDER_STATUS | Not changed |
|  | BO_INSTRUCTION_CD | Not changed |
|  | BO_RELEASE_DT | Not changed |
|  | ORDER_GROUP | Not changed |
|  | DIRECT_DELIVERY_CD | Not changed |
|  | DIRECT_DELIVERY_FLAG | Not changed |
|  | CURRENCY_CD | Not changed |
|  | LANDED_COST | Not changed |
|  | NET_PRICE | Not changed |
|  | SALES_PRICE | Not changed |
|  | EXPORT_SALES_PRICE | Not changed |
|  | SPECIAL_PRICE_CD | Not changed |
|  | ORDER_DISCOUNT_CD | Not changed |
|  | ITEM_DISCOUNT_RATE | Not changed |
|  | FIRST_ALLOCATION_DT | Not changed |
|  | BO_HISTORY_CD | Not changed |
|  | ORDER_ERROR_CD | Not changed |
|  | RA_CD | Not changed |
|  | PENDING_ORDER_CD | Not changed |
|  | ORDER_PORTION_CD | Not changed |
|  | ORDER_STATUS_DT | Not changed |
|  | SHIPPING_PROCESS_CTRL_CD | Not changed |
|  | PROCUREMENT_PROCESS_CTRL_CD | Not changed |
|  | DANGEROUS_GOODS_CLASS | Not changed |
|  | CREATE_DEMAND_FLAG | Not changed |
|  | SPECIAL_CUSTOMER_FLAG | Not changed |
|  | POSS_TRANSMISSION_JUDG_FLAG | Not changed |
|  | REGISTRANT_ID | Not changed |
|  | UPDATE_JOB_ID | Not changed |
|  | UPDATE_OPERATION_ID | Not changed |
|  | INTF_UPDATE_DT | Not changed |
|  | CREATE_DT | Not changed |
|  | CREATE_BY | Not changed |

#### 2. Insert / Update TB_R_CROSSDOCK_PART_HOLD – Part Number of the row (insert when no row yet)
- Source: [Save] of the part (sub screen)
- Destination keys: PART_NO + SUPPLIER_CD + SUPPLIER_PLANT = Part of the row

| Source field | Destination field | Description |
|---|---|---|
|  | PART_NO | Part number of the row |
|  | SUPPLIER_CD / SUPPLIER_PLANT | Supplier of the part |
|  | HOLD_FLAG | 'Y' (hold) / 'N' (release) |
|  | CREATED_BY / CREATED_DT | Login user ID / server date-time (insert only) |
|  | CHANGED_BY / CHANGED_DT | Login user ID / server date-time |

#### 3. Insert / Update / Delete TB_R_CROSSDOCK_CASE_HOLD – Ticked case: per customer order line in it, insert with HOLD_FLAG Y (or add its pcs to HOLD_QTY); unticked held line: HOLD_FLAG N (released, FB-183)
- Source: [Save] of Edit hold (cases and held lines of the unit)
- Destination keys: PART_NO + ORDER_DT + SUPPLIER_CD + SUPPLIER_PLANT + CUSTOMER_CD + CUSTOMER_ORDER_NO + DESTINATION_CD + DETAILED_ITEM_NO + SERIAL_NO = Customer order line in the case

| Source field | Destination field | Description |
|---|---|---|
|  | PART_NO / ORDER_DT | Part number and Customer Order Date of the unit |
|  | SUPPLIER_CD / SUPPLIER_PLANT | Supplier of the unit |
|  | CUSTOMER_CD / CUSTOMER_ORDER_NO / DESTINATION_CD / DETAILED_ITEM_NO / SERIAL_NO | Customer order line in the ticked case (TB_T_INSTRUCTION_D) |
|  | HOLD_QTY | Pcs of the line in the ticked case (rows of TB_T_INSTRUCTION_D), added when the line is already held |
|  | CREATED_BY / CREATED_DT | Login user ID / server date-time (insert only) |
|  | CHANGED_BY / CHANGED_DT | Login user ID / server date-time |
|  | HOLD_FLAG | 'Y' when ticked / 'N' when unticked (released) |

#### 4. Update TB_R_H0253_ORDER_CONTROL_PRE – [Create ASN]: the lines of the chosen blocks
- Source: TB_T_INSTRUCTION_D (chosen case groups)
- Destination keys: Unique key (customer order line incl. SERIAL_NO) = Lines of the chosen blocks

| Source field | Destination field | Description |
|---|---|---|
|  | PO_MAPPED_FLAG | 'Y' when the whole line is in TB_R_INSTRUCTION after this creation; stays 'N' when part of the line is in a later block; back to 'N' on Back / Cancel |
|  | HOLD_FLAG | Not changed |
|  | UPDATE_BY | Login user ID |
|  | UPDATE_DT | Server system date-time |
|  | CUSTOMER_CD | Not changed |
|  | CUSTOMER_ORDER_NO | Not changed |
|  | ORDER_DT | Not changed |
|  | ORDER_TIME | Not changed |
|  | DESTINATION_CD | Not changed |
|  | DETAILED_ITEM_NO | Not changed |
|  | SERIAL_NO | Not changed |
|  | TOPAS_ORDER_TYPE | Not changed |
|  | DEMAND_HISTORY_UPDATE_DT | Not changed |
|  | SHIPPING_MAKER_CD | Not changed |
|  | SHIPPING_PART_NO | Not changed |
|  | ORIGINAL_SHIPPING_QTY | Not changed |
|  | ORDER_STATUS_QTY | Not changed |
|  | ORDER_STATUS | Not changed |
|  | BO_INSTRUCTION_CD | Not changed |
|  | BO_RELEASE_DT | Not changed |
|  | ORDER_GROUP | Not changed |
|  | DIRECT_DELIVERY_CD | Not changed |
|  | DIRECT_DELIVERY_FLAG | Not changed |
|  | CURRENCY_CD | Not changed |
|  | LANDED_COST | Not changed |
|  | NET_PRICE | Not changed |
|  | SALES_PRICE | Not changed |
|  | EXPORT_SALES_PRICE | Not changed |
|  | SPECIAL_PRICE_CD | Not changed |
|  | ORDER_DISCOUNT_CD | Not changed |
|  | ITEM_DISCOUNT_RATE | Not changed |
|  | FIRST_ALLOCATION_DT | Not changed |
|  | BO_HISTORY_CD | Not changed |
|  | ORDER_ERROR_CD | Not changed |
|  | RA_CD | Not changed |
|  | PENDING_ORDER_CD | Not changed |
|  | ORDER_PORTION_CD | Not changed |
|  | ORDER_STATUS_DT | Not changed |
|  | SHIPPING_PROCESS_CTRL_CD | Not changed |
|  | PROCUREMENT_PROCESS_CTRL_CD | Not changed |
|  | DANGEROUS_GOODS_CLASS | Not changed |
|  | CREATE_DEMAND_FLAG | Not changed |
|  | SPECIAL_CUSTOMER_FLAG | Not changed |
|  | POSS_TRANSMISSION_JUDG_FLAG | Not changed |
|  | REGISTRANT_ID | Not changed |
|  | UPDATE_JOB_ID | Not changed |
|  | UPDATE_OPERATION_ID | Not changed |
|  | INTF_UPDATE_DT | Not changed |
|  | CREATE_DT | Not changed |
|  | CREATE_BY | Not changed |

#### 5. Update TB_R_PRA_DAILY_ORDER_PART – [Create ASN]: REMAIN_QTY of every PO part used by the chosen case groups
- Source: TB_T_INSTRUCTION_D (chosen case groups)
- Destination keys: MANIFEST_NO + MANIFEST_ITEM = PO part of the rows

| Source field | Destination field | Description |
|---|---|---|
|  | REMAIN_QTY | - qty of the chosen case groups (sum per PO part); + again on Back / Cancel / submit error |
|  | CHANGED_BY | Login user / batch user |
|  | CHANGED_DT | Server system date-time |

#### 6. Insert TB_R_INSTRUCTION – [Create ASN]: one row per case x line x PO
- Source: TB_T_INSTRUCTION_D (chosen case groups)

| Source field | Destination field | Description |
|---|---|---|
|  | DRAFT_ID | New id per [Create ASN] (same for all rows of the creation) |
|  | CASE_SEQ | Case sequence: selected unit, then the order of CASE_NO of TB_T_INSTRUCTION_D (H0253 order) |
|  | LINE_SEQ | LINE_SEQ of XD09 (sequence within the case) |
| PART_NO | PART_NO |  |
| ORDER_DT | ORDER_DT |  |
| DESTINATION_CD | DESTINATION_CD |  |
| CUSTOMER_CD | CUSTOMER_CD |  |
| CUSTOMER_ORDER_NO | CUSTOMER_ORDER_NO |  |
| DETAILED_ITEM_NO | DETAILED_ITEM_NO |  |
| SERIAL_NO | SERIAL_NO |  |
| PO_NO | PO_NO |  |
| MANIFEST_NO | MANIFEST_NO |  |
| MANIFEST_ITEM | MANIFEST_ITEM |  |
| ORDER_QTY | ORDER_QTY |  |
| COUNT(pcs) per case x line x PO | QTY |  |
| Delivery Date | DELIVERY_DT |  |
| Rit | RIT_CYCLE |  |
| Route | ROUTE |  |
|  | INSTRUCTION_ID | Running number (existing sequence) |
| SUPPLIER_CD | SUPPLIER_CD |  |
| SUPPLIER_PLANT | SUPPLIER_PLANT |  |
|  | ASN_NO | NULL (filled by the submit process, refer 5.7) |
|  | CASE_NO | CASE_NO of TB_T_INSTRUCTION_D |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date-time |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 7. Insert TB_R_DAILY_ORDER_MANIFEST – Submit ASN (5.7): one row per manifest of the cases; all rows of the submit share one ASN_NO
- Source: TB_R_INSTRUCTION + TB_R_PRA_DAILY_ORDER_MANIFEST (keys: MANIFEST_NO = Manifests of the cases of the submit)

| Source field | Destination field | Description |
|---|---|---|
|  | SUB_MANIFEST_NO | Sub manifest number as existing (sequence MANIFEST_LAST_SEQ of the Pra manifest) |
| TB_R_INSTRUCTION.MANIFEST_NO | MANIFEST_NO | One row per manifest of the cases |
|  | ASN_NO | Auto generated as existing; last sequence ASN_LAST_SEQ in TB_R_CASE_LABEL_LAST_SEQ (same ASN_NO for all manifests of the submit) |
|  | ASN_DATE | Submit date-time |
| TB_R_PRA_DAILY_ORDER_MANIFEST.DEPOT_CD | DEPOT_CD |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_CD | SUPPLIER_CD |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_PLANT | SUPPLIER_PLANT |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_CD | SUB_SUPP_CD |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_PLANT | SUB_SUPP_PLANT |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_NAME | SUPPLIER_NAME |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.PO_NO | PO_NO |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.PO_DT | PO_DATE |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.ORDER_TYPE | ORDER_TYPE |  |
| TB_R_PRA_DAILY_ORDER_MANIFEST.CROSS_DOCK_FLAG | CROSS_DOCK_FLAG | 'X' |
| TB_R_PRA_DAILY_ORDER_MANIFEST.DOCK_CD | DOCK_CD |  |
|  | TOTAL_ITEM | Number of manifest items of the manifest in this ASN |
|  | TOTAL_QTY | Sum of QTY of the manifest in this ASN |
| TB_R_INSTRUCTION.DELIVERY_DT | DELIVERY_DT_ORI | Delivery Date of the Search |
| TB_R_INSTRUCTION.ROUTE | SUB_ROUTE_CD | Route of the Search |
| TB_R_INSTRUCTION.RIT_CYCLE | SUB_ROUTE_SEQ | Rit of the Search |
| TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_ROUTE_DT | SUB_ROUTE_DT |  |
|  | STATUS | ASN status Created (code as existing) |
|  | CREATED_BY | User ID |
|  | CREATED_DT | Server system date-time |

#### 8. Insert TB_R_DAILY_ORDER_PART – Submit ASN (5.7): one row per manifest item and case
- Source: TB_R_INSTRUCTION + TB_R_PRA_DAILY_ORDER_PART + TB_M_PART_MASTER (keys: MANIFEST_NO + MANIFEST_ITEM + CASE_SEQ = One row per manifest item and case)

| Source field | Destination field | Description |
|---|---|---|
|  | SUB_MANIFEST_NO | Of the TB_R_DAILY_ORDER_MANIFEST row of the manifest |
| TB_R_INSTRUCTION.MANIFEST_NO | MANIFEST_NO |  |
| TB_R_INSTRUCTION.MANIFEST_ITEM | MANIFEST_ITEM |  |
|  | CASE_NO | CASE_NO of TB_T_INSTRUCTION_D (case label made by XD09 from TB_R_CASE_LABEL_LAST_SEQ) |
| TB_R_PRA_DAILY_ORDER_PART.PO_NO | PO_NO |  |
| TB_R_PRA_DAILY_ORDER_PART.PO_ITEM | PO_ITEM |  |
|  | ASN_NO | ASN_NO of the submit |
|  | ASN_DATE | Submit date-time |
| TB_R_PRA_DAILY_ORDER_PART.PART_NO | PART_NO |  |
| TB_M_PART_MASTER.PART_NAME | PART_NAME | By PART_NO |
| TB_R_PRA_DAILY_ORDER_PART.ORDER_QTY | PO_QTY |  |
|  | DELIVERY_QTY | Sum of TB_R_INSTRUCTION.QTY of the manifest item in the case |
| TB_R_PRA_DAILY_ORDER_PART.QTY_PER_CONTAINER | QTY_PER_CONTAINER |  |
| TB_R_INSTRUCTION.DELIVERY_DT | DELIVERY_DT_ORI |  |
| TB_R_PRA_DAILY_ORDER_PART.KANBAN_NO | KANBAN_NO |  |
| TB_R_PRA_DAILY_ORDER_PART.PART_BARCODE | PART_BARCODE | As existing |
|  | STATUS | As existing |
|  | CREATED_BY | User ID |
|  | CREATED_DT | Server system date-time |

#### 9. Update TB_R_INSTRUCTION – Submit ASN (5.7): Every row of the Submit ID
- Source: Result of the inserts
- Destination keys: INSTRUCTION_ID = Rows of the Submit ID

| Source field | Destination field | Description |
|---|---|---|
|  | ASN_NO | ASN No of the manifest |
|  | CASE_NO | Not changed (CASE_NO of the draft) |
|  | CHANGED_BY | User ID |
|  | CHANGED_DT | Server system date-time |
|  | INSTRUCTION_ID | Not changed |
|  | SUPPLIER_CD | Not changed |
|  | SUPPLIER_PLANT | Not changed |
|  | CASE_SEQ | Not changed |
|  | LINE_SEQ | Not changed |
|  | PART_NO | Not changed |
|  | ORDER_DT | Not changed |
|  | DESTINATION_CD | Not changed |
|  | CUSTOMER_CD | Not changed |
|  | CUSTOMER_ORDER_NO | Not changed |
|  | DETAILED_ITEM_NO | Not changed |
|  | SERIAL_NO | Not changed |
|  | QTY | Not changed |
|  | PO_NO | Not changed |
|  | MANIFEST_NO | Not changed |
|  | MANIFEST_ITEM | Not changed |
|  | ORDER_QTY | Not changed |
|  | DELIVERY_DT | Not changed |
|  | RIT_CYCLE | Not changed |
|  | ROUTE | Not changed |
|  | CREATED_BY | Not changed |
|  | CREATED_DT | Not changed |

#### 10. Insert Log (existing) – Submit ASN (5.7): Messages of the Submit ID (existing log columns)
- Source: Result of this run

| Source field | Destination field | Description |
|---|---|---|
|  | Process / Submit ID | Submit ID |
|  | Function ID | 'XD10' |
|  | Status | PROCESSING / SUCCESS / ERROR |
|  | Message ID / Message | LOG2 - LOG5 |
|  | User / Date-time | User ID, server system date-time |

#### 11. Update TB_R_CASE_LABEL_LAST_SEQ – Submit ASN (5.7): new last sequence of the supplier + plant
- Source: Last sequence of the submit
- Destination keys: SUPPLIER_CD + SUPPLIER_PLANT_CD = Supplier of the ASN

| Source field | Destination field | Description |
|---|---|---|
|  | ASN_LAST_SEQ | Last sequence used for the ASN number |
|  | CASE_LABEL_LAST_SEQ | Not changed at submit: updated by XD09 when the CASE_NO of the draft are made |
|  | CHANGED_BY | User ID |
|  | CHANGED_DT | Server system date-time |

## 6. Operation description

### 5.0 Behaviour shown by the simulation (simulasi_asn_rev.xlsx)

- 18-Oct, delivery plan PART-X 17-Oct: 5 cases; order 30 pcs vs PO PO-0003 18 pcs -> Short PO (shown with the ASN status, details in the PO information pop up); cases 1-4 Ready (PO-0002 rest 6 + PO-0003), case 5 (CO-14110) Not Ready with Remaining Qty 6.
- The selection starts at case 1 and ends on a case with CUT_FLAG Y: ticking case 3 selects cases 1-3; case 5 is disabled. Per Part Number the oldest Customer Order Date first: on 19-Oct the cases of 18-Oct show "Wait: 17-Oct first" until case 1 of 17-Oct (CO-14110) is ticked.
- [Create ASN] with cases 1-4: 5 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y on the 5 lines that are complete (CO-14110 stays N), REMAIN_QTY PO-0002 6 -> 0, PO-0003 18 -> 0. [Submit ASN] gives ASN0003 with case numbers C-0003-01 … 04; only case 5 stays in the delivery plan.
- One line in two ASNs: CO-14115 12 pcs = case 1 (ASN0006, PO_MAPPED_FLAG N, open 6) and case 2 (ASN0007, PO_MAPPED_FLAG Y).
- D/S hold of Japan (CO-14104) after the supplier ticked the unit: [Create ASN] fails (MSG8); the cases are computed again without Japan. A draft not submitted is released by the next XD08 run ([Submit ASN] of the old draft: MSG11). A cancel after the ASN goes to XD11 (CO-14104 in ASN0003 case 3 → CO-14111).

### 5.1 Initial Display and Search

a. On first display Delivery Date = today (business date), Rit = first rit of the date, Route displayed (disabled). The delivery plan is empty.
b. [Search] runs XD09 Mapping Customer Order and PO Batch (UISS XD09): the open qty of the H0253 customer orders with order status 7 and Hold Flag N, in the H0253 order per Part Number + Customer Order Date, pre-mapped to the PO parts of the Pra Daily Order (PO qty of the part poured over the lines from the top down, oldest PO first; refer UISS-Batch XD09 4.2), cut into supplier cases and blocks in the draft tables TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D (per company of the login user; nothing is mapped yet). Supplier: units of the login Supplier Code + Plant; D/S team: all suppliers.
c. The delivery plan shows one row per Part Number + Customer Order Date, sorted Ready, Partially Ready, Not Ready, then Part Number ascending. Units without any pre-mapped case and units fully Created are not listed. Part Number and Status filters apply at once. No row: message no. 3. The heading shows only "Delivery plan" (no summary line with date, Rit, route, number of units and refresh time; decided 14-Nov).
d. Delivery Date and Rit do not filter the orders; they are carried to the ASN. Rit and Route come from the existing route master table.

### 5.2 Status Rule

a. Unit = Part Number + Customer Order Date. H0253 order (decided 21-Oct): Allocation Priority (= Customer Order Date), Customer Code, Customer Order No, Customer Order Date, Customer Order Time, Destination Code, Detailed Item No, Serial No (fixed order).
b. Supplier case = PCS_CASE pcs in H0253 order; a case can hold several customer orders, POs and destinations. Case Qty = number of supplier cases; PO Readiness (case) = cases whose whole qty is pre-mapped to a PO.
c. The warehouse packs 1 case = 1 destination, so an ASN may stop only after a case where every destination of the unit is a multiple of PCS_CASE (valid cut). The cases up to a valid cut are a block = one ASN option step (e.g. 18-Oct PART-X 17-Oct: every case ends on a cut, blocks case 1 | 2 | 3 | 4 | 5).
d. A block is Ready ('6') when it and every earlier block have a PO; otherwise Not Ready ('7'): blocks are never skipped. Unit: Ready (all blocks), Partially Ready (the first k blocks), Not Ready (first block; check box disabled, message no. 2).
e. Created: blocks in a submitted ASN are no longer in the delivery plan (shown in ASN Inquiry); the open qty of the unit is cut again from case 1 in the same order at the next [Search].
f. On Hold also when the Part Number is on hold (5.3). Pcs held with the Hold check box are not in the cases (On Hold, CROSSDOCK_STATUS '8') and are not counted in PO Readiness; the other cases keep their own readiness.

### 5.3 Detail and Hold (D/S team)

a. The D/S team can expand a unit: one row per destination with Case, Qty (pcs), Pcs/Case and Hold Flag; each destination can be expanded to its customer order lines (Customer Order No, Detailed Item No, Qty, PO No, PO Date). The supplier sees the header only.
b. Hold / Release is done per destination: it updates HOLD_FLAG of every order line of the unit and destination in TB_R_H0253_ORDER_CONTROL_PRE (refer Data Edit Mapping). A held destination is not taken by Search; the unit is computed without it. A unit with all destinations on hold is shown as On Hold to the D/S team only.
c. HOLD_FLAG is 'N' when the line is first replicated (XD08) and is kept on the next replications.
d. Hold per Part Number (decided 13-Nov): [Hold per Part] opens a D/S sub screen with one section per supplier + plant and one row per Part Number (status, Hold check box, [Edit]). [Edit] enables the Hold check box, [Save] writes HOLD_FLAG in TB_R_CROSSDOCK_PART_HOLD, [Cancel] discards (same pattern as Part List and Mapping per Destination). Expanding a part lists its customer orders (Customer Order Date, Customer Order No, Destination, Qty, Case), not grouped by date, without PO information. A held part stays visible with status On Hold for every Customer Order Date, check boxes disabled (message no. 12), until saved as not on hold.
e. Hold per case (decided 13-Nov, rev. 14-Nov): the case grid has a check box Hold (D/S) next to PO Status, changed with [Edit hold] / [Save] / [Cancel] of the Part Number + Customer Order Date. [Save] of a ticked case stores its customer order lines with their pcs (HOLD_QTY) in TB_R_CROSSDOCK_CASE_HOLD. At the next Search (XD09) the held pcs leave the unit before the PO pouring: they take no PO, so the PO qty they had goes on to the next lines of the part (same Customer Order Date, then the next dates). The other cases are cut again and keep their own readiness (no Ready end at the held case).
f. Example: 18-Oct, PART-X 17-Oct, case 4 = CO-14109 Taiwan 6 pcs ticked -> Taiwan On Hold; PO-0003 6 pcs go to CO-14110 Australia (no PO before), so cases 1-4 (Korea, Korea, Japan, Australia) are all Ready. On 19-Oct the PO qty left after the 17-Oct lines goes to the 18-Oct orders.
g. The held lines are listed below the cases (Case = On hold, PO = released, PO Status On Hold (D/S), message no. 14), for the supplier too, and cannot be ticked for an ASN. The hold is on the customer order line, so it does not move when other lines are cancelled or sent. Unticking a held line + [Save] deletes the row: the pcs come back to their place in the H0253 order and take PO at the next Search (they come first again, so PO not yet in an ASN can move back to them). A held line cancelled in GTOPAS -> row deleted. The D/S team sees the content of each case in the columns Destination, Customer Order No and Order Qty.
h. Both holds are re-checked at [Create ASN] like the destination hold: a hold made after the units were ticked makes the whole create fail (message no. 8) and the delivery plan is refreshed.
i. Saving a hold (case grid [Save] and sub screen [Save]): confirmation first (message no. 15, [Tidak] keeps the edit open); [Ya, simpan] stores the change, shows message no. 16 and refreshes the delivery plan right away (Search again with the same Delivery Date / Rit, ticks of that unit cleared). No change = no message.
j. Case grid: bordered cells. Case, Qty, Remaining Qty, Destination, PO Status and the check boxes are shown once per case (merged over its customer order lines); PO is merged over the lines of the same PO.
k. Unit table and case grid: bordered cells (14-Nov). The destination detail with Hold Flag is hidden on the screen for now (FB-184).
l. Release of a held line (decided 14-Nov, FB-183): untick + [Save] sets HOLD_FLAG N. From the next Search the line is poured and cut at the END of its Customer Order Date: the lines of the same date that got the PO while it was held keep it (they stay Ready); the released line takes the next PO with qty left, and still comes before the newer Customer Order Dates (oldest date first). Example: 18-Oct Taiwan released after Australia took PO-0003 -> Australia stays Ready (case 4), Taiwan becomes case 5 Not Ready; 19-Oct the PO-0003 qty freed by the Japan cancel goes to Taiwan before the 18-Oct orders.

### 5.4 Select Cases and Create ASN

a. The user ticks the supplier cases to send with the check box of each case row. Cases that belong together (Case Group = GROUP_SEQ of XD09, not shown) are always sent together, so that at receiving every destination completes its warehouse case. The ticked cases of a unit start at case 1: ticking a case ticks the earlier cases and the other cases of its group (message no. 10). Example (18-Oct, PART-X 17-Oct): ticking case 3 gives cases 1-3; case 5 (no PO) cannot be ticked. When a case does not end on a cut (e.g. a case with KR 4 + JP 2), the cases up to the next cut are ticked with it. Only Ready cases can be ticked. One ASN is for one Supplier Code + Supplier Plant (existing rule): ticked units of more than one supplier give message no. 9 and nothing is created.
b. [Create ASN] does the real mapping of the chosen blocks in one transaction: the slices inserted into TB_R_INSTRUCTION (case and line sequence of XD09), REMAIN_QTY of TB_R_PRA_DAILY_ORDER_PART reduced, and PO_MAPPED_FLAG = 'Y' on the H0253 lines that are now completely in TB_R_INSTRUCTION. Then the Case List opens.
c. Before mapping, the ticked units are re-checked in the same transaction (row lock on the H0253 lines): if a line got HOLD_FLAG = 'Y' after the unit was ticked (e.g. the D/S team held a destination in another session), the creation fails for the whole selection (also the units that are not held): message no. 8 (Hold), the delivery plan is refreshed automatically and all ticked units are unticked. If a unit is no longer Ready for another reason (changed by another user), message no. 7.
d. [Back] / [Cancel] on the Case List cancel the creation: the rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to 'N' and REMAIN_QTY added back, so the blocks can be selected again. A draft left open (no Submit, no Cancel) is released by the next run of XD08 (every run releases all drafts, decided 23-Oct): the cases come back in the delivery plan and the supplier ticks them again.

### 5.5 Case List and Submit ASN

a. The summary shows ASN No (assigned on submit), supplier, Delivery Date · Rit · Route of the Search, Delivery Qty (pcs) and number of cases.
b. Each case shows Case Number, Part Number and Qty; the expand shows PO No, Manifest No, Manifest Item and PO Qty. Customer order data is not shown here.
c. [Download Case Label]: follows the existing case label of NSP.
d. [Submit ASN]: confirmation (message no. 4). Yes: the draft is handed with a Submit ID to the submit process (refer 5.7); the submit process follows the existing ASN. It reads TB_R_INSTRUCTION and inserts the existing tables TB_R_DAILY_ORDER_MANIFEST (status Created) and TB_R_DAILY_ORDER_PART; ASN No and Case No follow the existing numbering (case number auto generated by checking the last sequence). The screen returns to the delivery plan and shows the Submit ID (message no. 6); there is no success popup. The result message is written by the submit process (5.7) to the existing log (Log Monitoring).

### 5.6 Notes

- TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D hold the draft of [Search] per company of the login user (table concept of the DR XD09 (11-Nov)). TB_R_INSTRUCTION holds the mapping from [Create ASN] until submit or Back / Cancel. The open PO qty is REMAIN_QTY of the existing TB_R_PRA_DAILY_ORDER_PART (no new table). Submitted ASNs are in TB_R_DAILY_ORDER_MANIFEST / PART and shown in ASN Inquiry (XD15).
- Case number: CASE_NO of the draft, made by XD09 at [Search] in the existing NSP format; the last sequence is kept in TB_R_CASE_LABEL_LAST_SEQ.
- Cancel of an order is not done in NSP: it comes from the source (H0253 order status '2'); NSP only holds (HOLD_FLAG). Refer XD08 / XD11.
- The prototype has a 'Business date' switch (PO release) and a 'View as' switch (Supplier / D/S team); they are not part of the real screen.

### 5.7 Submit ASN Process (backend, follows the existing ASN)

a. Re-check before the submit: the draft must still exist (not released by XD08) and every line of it must still have UPD_STATUS NULL and the same qty. Otherwise nothing is submitted, the draft is released and message no. 11 is shown; the supplier searches again.
b. The screen generates the Submit ID, writes the start message to the log (LOG2) and starts the submit process. The screen returns to the delivery plan and shows the Submit ID.
c. Read the rows of the Submit ID from TB_R_INSTRUCTION (one Supplier Code + Plant). Take the ASN No from the existing numbering and take the Case No of each case from CASE_NO of TB_T_INSTRUCTION_D (made by XD09).
d. Insert TB_R_DAILY_ORDER_MANIFEST (status Created) and TB_R_DAILY_ORDER_PART (existing tables, refer Data Edit Mapping); write ASN_NO / CASE_NO back to TB_R_INSTRUCTION.
e. No error: commit, write the result (LOG3) and end (LOG4) messages. Error: roll back, release the mapping (delete the rows from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to 'N', REMAIN_QTY of TB_R_PRA_DAILY_ORDER_PART added back), write the error (LOG5). Exit.

- Submit ASN runs as a batch so the screen does not wait; the user sees the Submit ID and checks the result in Log Monitoring. No success popup is shown on the screen.
- The log follows the existing NSP log (same table and columns); the Submit ID is the key to find the run.
- All-or-nothing: on error nothing is saved and the mapping made by [Create ASN] is released (rows deleted from TB_R_INSTRUCTION), so the units can be selected again.
- The ASN is saved in the existing tables TB_R_DAILY_ORDER_MANIFEST / TB_R_DAILY_ORDER_PART; the case number is CASE_NO of TB_T_INSTRUCTION_D, made by XD09 from the last sequence in TB_R_CASE_LABEL_LAST_SEQ (16-Nov, DR XD09).
- The submit process (Submit ID, batch call, log) follows the existing ASN submit of NSP.

### 5.8 Sample Create ASN

- Dummy example of [Create ASN] (case packing, TB_R_INSTRUCTION rows, flags, Case List, scenarios): see sheet Sample Input.

## 7. Display messages

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| **Delivery Plan (tooltip of disabled check box)** |  |  |  |  |  |
| MSG1 | Hover on disabled check box | Unit is On Hold (D/S) | Info | All destinations are on hold | Release a destination. |
| MSG2 | Hover on disabled check box | Unit is Not Ready | Info | Not Ready: case {n} of {Part No} / {Customer Order Date} (or an earlier case) is not assigned to a PO yet ({k} of {c} cases assigned) | Wait for the next PO. |
| MSG12 | Hover on disabled check box | Part Number on hold (D/S) | Info | {Part No} is on hold by the D/S team | Contact the D/S team. |
| MSG14 | Hover on a held line | Customer order line held by the D/S team (Hold per case) | Info | On hold by the D/S team: {Customer Order No} of {Part No} / {Customer Order Date}, {n} pcs; its PO qty is used by the next orders | Contact the D/S team. |
| MSG15 | Click [Save] of a hold (case grid or sub screen) | Hold changed | Confirmation | Simpan hold {Part No} / {Customer Order Date}? Yang disimpan: hold case {n} ({Customer Order No}, {qty} pcs); lepas hold {Customer Order No} ({qty} pcs). Pcs yang di-hold tidak dapat PO; PO-nya dipakai order berikutnya. (Sub screen: Simpan hold {Part No}? {Part No} di-hold: belum bisa dibuat ASN untuk semua Customer Order Date sampai hold dilepas. / Hold {Part No} dilepas: case-nya bisa dikirim lagi.) | [Ya, simpan] / [Tidak] |
| MSG16 | After [Ya, simpan] | Hold saved | Info | Tersimpan: Hold {Part No} / {Customer Order Date} sudah disimpan. Delivery plan sudah di-refresh. | [OK] |
| MSG17 | Click the ASN status (Partially Ready / Not Ready / Short PO) | Not all cases have a PO, or PO qty < order qty | Info | Info PO · {Part No} / {Customer Order Date}: Order customer tanggal {date}: {n} pcs (semua destinasi). PO reguler {PO No}: {qty} pcs, terbit {date}. [Split PO {PO No}: {qty} pcs, terbit {date}.] PO kurang dari order (Short PO): {n} pcs masih menunggu split PO. {a} dari {b} case sudah dapat PO dan siap dikirim; case lainnya menunggu PO. [{n} pcs di-hold tim D/S; PO-nya dipakai order berikutnya.] | [OK] |
| MSG18 | Click the Hold chip next to the ASN status | The unit has a hold | Info | Info hold · {Part No} / {Customer Order Date}: [Part Number {Part No} di-hold tim D/S: belum bisa dibuat ASN untuk semua Customer Order Date.] [{n} pcs di-hold tim D/S, PO-nya dilepas dan dipakai order berikutnya. {Customer Order No} · {Destination} (D/S team): {qty} pcs] [{n} destinasi di-hold (Hold Flag Y). (D/S team)] | [OK] |
| **Search** |  |  |  |  |  |
| MSG3 | Click [Search] / change filter | No unit | Info | No customer order matches this filter. | Change the Delivery Date, Rit or filter. |
| MSG5 | Change [Delivery Date] | No rit on the date (Sunday) | Info | No rit cycle available for {Delivery Date}. Choose another delivery date. | Choose another Delivery Date. |
| **Create ASN / Case List** |  |  |  |  |  |
| MSG7 | Click [Create ASN] | A chosen block is no longer Ready | Error | {Part No} / {Customer Order Date} is no longer Ready. The delivery plan is refreshed. | Select again. |
| MSG4 | Click [Submit ASN] button | Confirmation | Confirm | Submit ASN? {n} cases ({q} pcs) will be created into {ASN No}, delivery {Delivery Date} · {Rit}. | Click [Yes, submit] or [No]. |
| MSG6 | Click [Yes, submit] | Submit handed to the submit process (5.7) | Info | Submit ID {Submit ID} is sent to the ASN submit batch. The result is written to Log Monitoring. | Check Log Monitoring. |
| MSG8 | Click [Create ASN] | A ticked unit has an order put on hold by the D/S team after it was ticked | Error | Some order has been already hold, please select other records. The delivery plan has been refreshed. | Click [OK]; the delivery plan is already refreshed and all units are unticked; select again. |
| MSG9 | Click [Create ASN] | Ticked units are of more than one Supplier Code + Supplier Plant (D/S team) | Error | One ASN is for one Supplier Code and Supplier Plant. Please select units of one supplier. | Click [OK]; untick the units of the other supplier. |
| MSG10 | Tick a case that belongs together with later cases | Cases that belong together (Case Group) are sent together | Info | Cases {a}-{b} are sent together. Cases 1-{b} of {Part No} / {Customer Order Date} are selected. | Keep the selection or untick. |
| MSG11 | Click [Submit ASN] / [Yes] | The draft was released by XD08 or a line changed in GTOPAS (UPD_STATUS, qty) | Error | Some orders have changed. The draft is released; please Search and create the ASN again. | Click [OK]; back to the delivery plan. |

## 8. Logging messages

| ID | Event | Cause | Type | Message | Action | Exception |
|---|---|---|---|---|---|---|
| LOG1 | Click [Create ASN] | Database error on mapping / draft | Error | Failed to create the ASN (TB_R_INSTRUCTION): <DB error message>. | Roll back; show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG2 | Submit ASN (5.7): Batch start | [Submit ASN] Yes | Info | ASN submit started. Submit ID <SUBMIT_ID>, <n> cases. | System: Write the log. User: - | N |
| LOG3 | Submit ASN (5.7): Save | ASN saved | Info | <ASN_NO> submitted with status Created. <n> cases are saved. Delivery <DELIVERY_DT> · <RIT>. The ASN is shown in ASN Inquiry. | System: Write the log. User: - | N |
| LOG4 | Submit ASN (5.7): Batch end | Batch finishes | Info | ASN submit ended. Status <STATUS>. | System: Write the log. User: - | N |
| LOG5 | Submit ASN (5.7): Error | Numbering or insert fails / any system error | Error | Failed to submit ASN, Submit ID <SUBMIT_ID>: <ERROR_DETAIL>. | System: Roll back; release the mapping. STATUS = ERROR. User: Create the ASN again; contact PIC if it persists. | Y |

## 9. Tables

#### TB_T_INSTRUCTION_H (transaction, proposed)
Draft of ASN Crossdock, header (DR XD09 (11-Nov)): one row per unit = Customer Order Date + Part Number + supplier. Written by XD09 at [Search] of XD10 for the company of the login user: its rows (LEFT(CREATE_BY, 4) = company code) are deleted and inserted again; company 1000 (TMMIN, D/S team) sees every supplier.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| ORDER_DT | DATE | Y | N | Customer Order Date (H0253.ORDER_DT) |
| SHIPPING_PART_NO | VARCHAR(15) | Y | N | Part Number (H0253.SHIPPING_PART_NO) |
| SUPPLIER_CD | VARCHAR(4) | Y | N | Supplier of the crossdock PO (TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_CD) |
| SUPPLIER_PLANT | VARCHAR(1) | Y | N | Supplier plant (TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_PLANT) |
| SUB_SUPP_CD | VARCHAR(4) |  | Y | Sub supplier (TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_CD) |
| SUB_SUPP_PLANT | VARCHAR(1) |  | Y | Sub supplier plant (TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_PLANT) |
| ORDER_STATUS_QTY | NUMBER(8) |  | N | Open qty of the unit = SUM(H0253.ORDER_STATUS_QTY) of the lines not on hold and not yet in TB_R_INSTRUCTION |
| CASE | NUMBER(8) |  | N | Case Qty of the unit = number of supplier cases (CEILING(ORDER_STATUS_QTY / TB_M_PART_CANDIDATE.PCS_CASE)) |
| SUBMIT_ASN_STS | VARCHAR(1) |  | Y | 'Y' the unit has Ready cases that can go into an ASN / 'N' not (DR; also named GENERATE_ASN_STS in the DR Data Map, refer FB-193) |
| CREATE_DT | TIMESTAMP |  | N | System date-time of the run |
| CREATE_BY | VARCHAR(20) |  | N | Login user; LEFT(CREATE_BY, 4) = company code of the user (rows of the company) |
| UPDATE_DT | TIMESTAMP |  | Y | Last update date-time |
| UPDATE_BY | VARCHAR(20) |  | Y | Last update user |

#### TB_T_INSTRUCTION_D (transaction, proposed)
Draft of ASN Crossdock, detail (DR XD09 (11-Nov)): one row per pc. The customer order line is broken down to 1 pc per row (ORDER_STATUS_QTY = 1) and the PO qty is broken down to 1 (PO_QTY = 1). The pcs of a supplier case share one CASE_NO. Columns marked (added) are not in the DR but needed by the rules of 4.1-4.3.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| ORDER_DT | DATE | Y | N | Customer Order Date (H0253.ORDER_DT) |
| SHIPPING_PART_NO | VARCHAR(15) | Y | N | Part Number (H0253.SHIPPING_PART_NO) |
| SUPPLIER_CD | VARCHAR(4) | Y | N | Supplier of the crossdock PO (TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_CD) |
| SUPPLIER_PLANT | VARCHAR(1) | Y | N | Supplier plant (TB_R_PRA_DAILY_ORDER_MANIFEST.SUPPLIER_PLANT) |
| SUB_SUPP_CD | VARCHAR(4) |  | Y | Sub supplier (TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_CD) |
| SUB_SUPP_PLANT | VARCHAR(1) |  | Y | Sub supplier plant (TB_R_PRA_DAILY_ORDER_MANIFEST.SUB_SUPP_PLANT) |
| SEQ_NO | NUMBER(6) | Y | N | (added) Sequence of the pc in the unit in the H0253 order of 4.1; key of the row |
| CUSTOMER_CD | VARCHAR(7) |  | N | (added) H0253.CUSTOMER_CD (order key 1, needed for the H0253 order and TB_R_INSTRUCTION) |
| CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | H0253.CUSTOMER_ORDER_NO |
| DESTINATION_CD | VARCHAR(7) |  | N | H0253.DESTINATION_CD |
| DETAILED_ITEM_NO | VARCHAR(4) |  | N | H0253.DETAILED_ITEM_NO |
| SERIAL_NO | VARCHAR(7) |  | N | H0253.SERIAL_NO (DR simulation: SERIAL_CARD_NO, refer FB-193) |
| ORDER_STATUS_QTY | NUMBER(8) |  | N | Always 1 (customer order line broken down to 1 pc) |
| PO_NO | VARCHAR(20) |  | Y | PO of the pc (pouring of 4.2: oldest PO first); NULL when no PO is left or the pc is held |
| PO_ITEM | VARCHAR(4) |  | Y | TB_R_PRA_DAILY_ORDER_PART.PO_ITEM |
| MANIFEST_NO | VARCHAR(20) |  | Y | TB_R_PRA_DAILY_ORDER_PART.MANIFEST_NO |
| MANIFEST_ITEM | VARCHAR(4) |  | Y | TB_R_PRA_DAILY_ORDER_PART.MANIFEST_ITEM |
| PO_QTY | NUMBER(8) |  | N | 1 when the pc has a PO (PO qty broken down to 1); 0 when PO_NO is NULL |
| CASE_NO | VARCHAR(8) |  | Y | Supplier case (case label) of the pc: supplier (sub supplier when it exists) + plant + initial palletize code + next CASE_LABEL_LAST_SEQ of TB_R_CASE_LABEL_LAST_SEQ; the same CASE_NO for PCS_CASE pcs in H0253 order (DR); NULL for a held pc |
| CUT_FLAG | VARCHAR(1) |  | Y | (added) 'Y' on the pcs of a case after which the ASN may stop (every destination of the unit a multiple of PCS_CASE, 4.3) |
| GROUP_SEQ | NUMBER(4) |  | Y | (added) Case Group: the cases up to and including a valid cut; sent together |
| CROSSDOCK_STATUS | VARCHAR(1) |  | Y | (added) '6' Ready / '7' Not Ready / '8' On Hold (D/S) of the case group |
| HOLD_STS | CHAR(1) |  | Y | 'Y' pc held by the D/S team (Hold per case, Part Number on hold): no PO, no CASE_NO; NULL otherwise |
| CREATE_DT | TIMESTAMP |  | N | System date-time of the run |
| CREATE_BY | VARCHAR(20) |  | N | Login user; LEFT(CREATE_BY, 4) = company code of the user (rows of the company) |
| UPDATE_DT | TIMESTAMP |  | Y | Last update date-time |
| UPDATE_BY | VARCHAR(20) |  | Y | Last update user |

#### TB_R_INSTRUCTION (transaction, proposed)
Real mapping made by [Create ASN]: one row per supplier case x customer order line x PO of the chosen blocks (case and line sequence of XD09). Rows are deleted by [Back] / [Cancel] on the Case List; [Submit ASN] (5.7) fills ASN_NO and CASE_NO. Columns proposed. Rows without ASN_NO are a draft: every run of XD08 releases all drafts (decided 23-Oct); a cancelled line in a submitted ASN is moved to other lines in Change Order Number (XD11).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| INSTRUCTION_ID | BIGINT | Y | N | Running number (identity) |
| SUPPLIER_CD | VARCHAR(TBD) |  | N | Supplier code (one ASN = one Supplier Code + Plant) |
| SUPPLIER_PLANT | VARCHAR(TBD) |  | N | Supplier plant |
| CASE_SEQ | NUMBER(4) |  | N | Case sequence of the Create ASN (Case 1, 2, ...) |
| LINE_SEQ | NUMBER(4) |  | N | Order line x PO within the case |
| PART_NO | VARCHAR(15) |  | N | Part number of the case |
| ORDER_DT | DATE |  | N | Customer Order Date of the case |
| DESTINATION_CD | VARCHAR(7) |  | N | Destination of the case |
| CUSTOMER_CD | VARCHAR(7) |  | N | Customer code |
| CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | Customer order number |
| DETAILED_ITEM_NO | VARCHAR(4) |  | N | Detailed item number |
| SERIAL_NO | VARCHAR(7) |  | N | Serial number |
| QTY | NUMBER(8) |  | N | Qty of the line mapped to the PO in this case |
| PO_NO | VARCHAR(TBD) |  | N | PO number |
| MANIFEST_NO | VARCHAR(TBD) |  | N | Manifest number of the Pra Daily Order |
| MANIFEST_ITEM | VARCHAR(TBD) |  | N | Manifest item number |
| ORDER_QTY | NUMBER(TBD) |  | N | PO qty |
| DELIVERY_DT | DATE |  | N | Delivery Date of the Search |
| RIT_CYCLE | VARCHAR(TBD) |  | N | Rit of the Search (route master, existing) |
| ROUTE | VARCHAR(TBD) |  | N | Route of the Rit (route master, existing) |
| DRAFT_ID | VARCHAR(20) |  | Y | Draft of one [Create ASN] (all rows of the creation); NULL after [Submit ASN] is not needed (ASN_NO filled). Every run of XD08 deletes the rows with ASN_NO NULL |
| ASN_NO | VARCHAR(TBD) |  | Y | ASN number; NULL until the ASN is submitted (5.7) |
| CASE_NO | VARCHAR(TBD) |  | Y | Case number; NULL until submitted (auto generated with the existing last sequence) |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_R_DAILY_ORDER_MANIFEST (transaction, existing)
Existing ASN manifest (GTOPAS SPS DB structure TR-01). Submit ASN: one row per Pra Daily Order manifest of the cases, all with the same ASN_NO. Only the columns used are listed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| DEPOT_CD | VARCHAR(20) |  | Y | Depot Code |
| SUPPLIER_CD | VARCHAR(4) |  | N | Supplier Code |
| SUPPLIER_PLANT | VARCHAR(1) |  | N | Supplier Plant Code |
| SUB_SUPP_CD | VARCHAR(4) |  | Y | Sub Supplier Code |
| SUB_SUPP_PLANT | VARCHAR(1) |  | Y | Sub Supplier Plant Code |
| SUPPLIER_NAME | VARCHAR(50) |  | Y | Supplier Name |
| PO_NO | VARCHAR(20) |  | N | PO Number |
| ASN_NO | VARCHAR(15) |  | N | ASN Number |
| PO_DATE | DATETIME |  | N | PO Date |
| ASN_DATE | DATETIME |  | N | ASN Date |
| SUB_MANIFEST_NO | VARCHAR(20) | Y | N | Sub Manifest Number |
| MANIFEST_NO | VARCHAR(16) | Y | N | Manifest Number |
| ORDER_TYPE | VARCHAR(1) |  | Y | Order Type |
| CROSS_DOCK_FLAG | VARCHAR(3) |  | Y | Cross Dock Flag |
| DOCK_CD | VARCHAR(2) |  | Y | Dock Code |
| TOTAL_ITEM | NUMERIC |  | N | Total Item |
| TOTAL_QTY | NUMERIC |  | N | Total Quantity |
| DELIVERY_DT_ORI | DATETIME |  | Y | Delivery Date Original |
| SUB_ROUTE_CD | VARCHAR(10) |  | N | Sub Route Code |
| SUB_ROUTE_SEQ | VARCHAR(2) |  | N | Sub Route Seq |
| SUB_ROUTE_DT | DATETIME |  | Y | Sub Route Date |
| STATUS | VARCHAR(3) |  | N | Status |
| CREATED_BY | VARCHAR(20) |  | N | Created By |
| CREATED_DT | DATETIME |  | N | Created Date |

#### TB_R_DAILY_ORDER_PART (transaction, existing)
Existing ASN part (TR-02). Submit ASN: one row per manifest item and case (a case can hold several manifest items). Only the columns used are listed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PO_NO | VARCHAR(20) |  | N | PO Number |
| PO_ITEM | VARCHAR(4) |  | N | PO Item |
| SUB_MANIFEST_NO | VARCHAR(20) | Y | N | Sub Manifest Number |
| MANIFEST_NO | VARCHAR(16) | Y | N | Manifest Number |
| MANIFEST_ITEM | NUMERIC | Y | N | Manifest Item |
| CASE_NO | VARCHAR(9) | Y | N | Case Number |
| ASN_NO | VARCHAR(15) |  | N | ASN Number |
| ASN_DATE | DATETIME |  | N | ASN Date |
| PART_NO | VARCHAR(20) |  | N | Part Number |
| PART_NAME | VARCHAR(50) |  | N | Part Name |
| PO_QTY | NUMERIC |  | N | PO Quantity |
| DELIVERY_QTY | NUMERIC |  | N | Delivery Quantity |
| QTY_PER_CONTAINER | NUMERIC |  | N | Quantity Per Container |
| DELIVERY_DT_ORI | DATETIME |  | Y | Delivery Date Original |
| KANBAN_NO | VARCHAR(4) |  | Y | Kanban Number |
| PART_BARCODE | VARCHAR(25) |  | Y | Part Barcode |
| STATUS | VARCHAR(3) |  | N | Status |
| CREATED_BY | VARCHAR(20) |  | N | Created By |
| CREATED_DT | DATETIME |  | N | Created Date |

#### TB_R_CASE_LABEL_LAST_SEQ (transaction, existing)
Existing last sequence per supplier + plant (TR-06): the case number (case label) and the ASN number are auto generated from it and the new last sequence is saved here.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| SUPPLIER_CD | VARCHAR(5) | Y | N | Supplier Code |
| SUPPLIER_PLANT_CD | VARCHAR(1) | Y | N | Supplier Plant Code |
| CASE_LABEL_LAST_SEQ | VARCHAR(3) |  | Y | Case Label Last Seq No |
| ASN_LAST_SEQ | VARCHAR(3) |  | Y | ASN Last Seq No |
| CHANGED_BY | VARCHAR(20) |  | Y | Changed By |
| CHANGED_DT | DATETIME |  | Y | Changed Date |

#### TB_M_PART_MASTER (master, existing)
Existing part master (MST-03); only PART_NAME is used (by PART_NO).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(15) | Y | N | Part No |
| PART_NAME | VARCHAR(100) |  | N | Part Name |
| SUPPLIER_CD | VARCHAR(4) | Y | N | Supplier Code |
| SUPPLIER_PLANT_CD | VARCHAR(1) | Y | N | Supplier Plabt Code |
| DOCK_CD | VARCHAR(2) | Y | N | Dock Code |
| VALID_FROM | DATETIME | Y | N | Valid From |
| VALID_TO | DATETIME |  | Y | Valid To |

#### TB_R_CROSSDOCK_PART_HOLD (transaction, proposed)
New table: Part Number put on hold by the D/S team on ASN Crossdock Creation (sub screen Hold per Part). HOLD_FLAG Y = no ASN can be created for the part, whatever the Customer Order Date. Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(15) | Y | N | Part number (H0253.SHIPPING_PART_NO) |
| SUPPLIER_CD | VARCHAR(TBD) | Y | N | Supplier code of the unit |
| SUPPLIER_PLANT | VARCHAR(TBD) | Y | N | Supplier plant of the unit |
| HOLD_FLAG | CHAR(1) |  | N | 'Y' on hold / 'N' released (no row = 'N') |
| CREATED_BY | VARCHAR(20) |  | N | Login user (D/S team) who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(20) |  | N | Login user (D/S team) who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_R_CROSSDOCK_CASE_HOLD (transaction, proposed)
New table: customer order lines (pcs) of a supplier case held by the D/S team with the Hold check box (decided 14-Nov). The held pcs leave the unit before the PO pouring of XD09: they take no PO, the PO qty goes on to the next orders, the other cases stay Ready with their own PO. Released (unticked) = HOLD_FLAG N, kept until the line is fully in an ASN or cancelled (FB-183). Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(15) | Y | N | Part number (H0253.SHIPPING_PART_NO) |
| ORDER_DT | DATE | Y | N | Customer Order Date of the unit |
| SUPPLIER_CD | VARCHAR(TBD) | Y | N | Supplier code of the unit |
| SUPPLIER_PLANT | VARCHAR(TBD) | Y | N | Supplier plant of the unit |
| CUSTOMER_CD | VARCHAR(TBD) | Y | N | Customer order line key (H0253) |
| CUSTOMER_ORDER_NO | VARCHAR(TBD) | Y | N | Customer order line key (H0253) |
| DESTINATION_CD | VARCHAR(7) | Y | N | Customer order line key (H0253) |
| DETAILED_ITEM_NO | VARCHAR(TBD) | Y | N | Customer order line key (H0253) |
| SERIAL_NO | VARCHAR(TBD) | Y | N | Customer order line key (H0253) |
| HOLD_QTY | INT |  | N | Held pcs of the line (sum of the line pcs in the held cases); not more than the open qty of the line |
| HOLD_FLAG | CHAR(1) |  | N | 'Y' on hold / 'N' released: the line goes to the end of its Customer Order Date in the PO pouring (FB-183) |
| CREATED_BY | VARCHAR(20) |  | N | Login user (D/S team) who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(20) |  | N | Login user (D/S team) who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |

#### TB_R_PRA_DAILY_ORDER_PART (transaction, existing)
Existing Pra Daily Order part (one row per manifest item). Crossdock uses ORDER_QTY and REMAIN_QTY of the parts of the manifests with CROSS_DOCK_FLAG = 'X': open PO qty = REMAIN_QTY (no new mapped-qty table, decided 16-Nov).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| MANIFEST_NO | VARCHAR(10+) | Y | N | Manifest number (TB_R_PRA_DAILY_ORDER_MANIFEST) |
| MANIFEST_ITEM | VARCHAR(4+) | Y | N | Item of the manifest |
| PO_NO | VARCHAR(8+) |  | N | PO number |
| PO_ITEM | VARCHAR(4+) |  | N | Item of the PO |
| PART_NO | VARCHAR(12+) |  | N | Part number |
| ORDER_QTY | NUMERIC |  | N | PO qty (pcs) |
| REMAIN_QTY | NUMERIC |  | N | Qty of the PO part not yet in an ASN: open PO qty of XD09; reduced by [Create ASN] (XD10), added back on Back / Cancel, submit error and XD08 release |
| CHANGED_BY | VARCHAR(20) |  | Y | Last change user |
| CHANGED_DT | DATETIME |  | Y | Last change date-time |

## Sample Input

**Sample Create ASN - ASN Cross Dock Creation (simulasi_asn_rev.xlsx, 18-Oct-2026)**

- Data of simulasi_asn_rev.xlsx (also in the prototype, business date 18-Oct). Supplier 5001 plant 1, Delivery Date 18-Oct-2026, Rit 1, Route SD01. PART-X, Pcs/Case = 6. ASN0001 (CO-14101) and ASN0002 (CO-14103) are already submitted, so the oldest open Customer Order Date is 17-Oct.
- Order date 17-Oct: 4 destinations, 30 pcs; PO PO-0003 (PO date 18-Oct) has only 18 pcs (Short PO, abnormality); the rest of PO-0002 (6) is taken first (older PO date). The split PO PO-0004 (12) comes on 19-Oct.
- The supplier ticks the unit PART-X 17-Oct (cases 1-4, case 5 is Not Ready) and clicks [Create ASN]; the submit gives ASN0003.

### A. Input: pre-mapping of XD09 (TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D) in H0253 order: Customer Order Date, Customer Code, Customer Order No, …

| Sort Seq | Customer Order No | Detailed Item No | Serial No | Destination | Open Qty | PO No | Assigned Qty | Case | Cut | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CO-14105 | 001 | 0000001 | 9715310 (Korea) | 6 | PO-0002 | 6 | 1 | Y | 6 |
| 2 | CO-14106 | 001 | 0000001 | 9715310 (Korea) | 3 | PO-0003 | 3 | 2 | N | 6 |
| 3 | CO-14107 | 001 | 0000001 | 9715310 (Korea) | 3 | PO-0003 | 3 | 2 | Y | 6 |
| 4 | CO-14104 | 001 | 0000001 | 9722D10 (Japan) | 6 | PO-0003 | 6 | 3 | Y | 6 |
| 5 | CO-14109 | 001 | 0000001 | 9811110 (Taiwan) | 6 | PO-0003 | 6 | 4 | Y | 6 |
| 6 | CO-14110 | 001 | 0000001 | 982220 | 6 | — | 6 | 5 | Y | 7 |

### B. Input: PO parts before [Create ASN] (Pra Daily Order: manifest with CROSS_DOCK_FLAG = 'X')

| PO No | Manifest No | Manifest Item | Part No | PO Qty (ORDER_QTY) | Remaining Qty (TB_R_PRA_DAILY_ORDER_PART.REMAIN_QTY) | Open Qty |
|---|---|---|---|---|---|---|
| PO-0002 | MF-0002 | 0001 | PART-X | 6 | 6 | 6 |
| PO-0003 | MF-0003 | 0001 | PART-X | 18 | 18 | 18 |

### C. Supplier cases (6 pcs in H0253 order; CUT_FLAG Y = the ASN may stop after the case)

| Case | Qty | Content (customer order qty (PO)) | CUT_FLAG | Status |
|---|---|---|---|---|
| Case 1 | 6 | CO-14105 6 (PO-0002) | Y | Ready |
| Case 2 | 6 | CO-14106 3 (PO-0003) + CO-14107 3 (PO-0003) | Y | Ready |
| Case 3 | 6 | CO-14104 6 (PO-0003) | Y | Ready |
| Case 4 | 6 | CO-14109 6 (PO-0003) | Y | Ready |
| Case 5 | 6 | CO-14110 6 (no PO) | Y | Not Ready |

### D. Result: rows inserted into TB_R_INSTRUCTION (cases 1-4; ASN_NO / CASE_NO filled on submit)

| INSTRUCTION_ID | CASE_SEQ | LINE_SEQ | PART_NO | ORDER_DT | DESTINATION_CD | CUSTOMER_ORDER_NO | DETAILED_ITEM_NO | SERIAL_NO | QTY | PO_NO | MANIFEST_NO | MANIFEST_ITEM | DELIVERY_DT | RIT_CYCLE | ROUTE | ASN_NO | CASE_NO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1 | PART-X | 17-Oct-2026 | 9715310 | CO-14105 | 001 | 0000001 | 6 | PO-0002 | MF-0002 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 4 | 2 | 1 | PART-X | 17-Oct-2026 | 9715310 | CO-14106 | 001 | 0000001 | 3 | PO-0003 | MF-0003 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 5 | 2 | 2 | PART-X | 17-Oct-2026 | 9715310 | CO-14107 | 001 | 0000001 | 3 | PO-0003 | MF-0003 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 6 | 3 | 1 | PART-X | 17-Oct-2026 | 9722D10 | CO-14104 | 001 | 0000001 | 6 | PO-0003 | MF-0003 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 7 | 4 | 1 | PART-X | 17-Oct-2026 | 9811110 | CO-14109 | 001 | 0000001 | 6 | PO-0003 | MF-0003 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |

### E. Result: other tables changed in the same transaction

| Table | Key | Column | Before | After |
|---|---|---|---|---|
| TB_R_H0253_ORDER_CONTROL_PRE | CO-14104, CO-14105, CO-14106, CO-14107, CO-14109 (whole line in the ASN) | PO_MAPPED_FLAG | N | Y |
| TB_R_H0253_ORDER_CONTROL_PRE | CO-14110 (case 5, not sent) | PO_MAPPED_FLAG | N | N |
| TB_R_PRA_DAILY_ORDER_PART | PO-0002 / MF-0002 / 0001 / PART-X | REMAIN_QTY | 6 | 0 |
| TB_R_PRA_DAILY_ORDER_PART | PO-0003 / MF-0003 / 0001 / PART-X | REMAIN_QTY | 18 | 0 |

### F. Result on the screen: Case List (Draft)

| Item | Value |
|---|---|
| ASN No | ASN0003 (auto, assigned on submit) |
| Supplier · Plant | 5001 · 1 |
| Delivery Date · Rit · Route | 18-Oct-2026 · Rit 1 · SD01 |
| Delivery Qty | 24 pcs |
| Cases | 4 cases |
| Case 1 .. Case 4 | Case Number, Part Number, Customer Order Date, Qty (6 each); the expand button shows the PO No, Manifest No, Manifest Item and PO Qty (Case 1: PO-0002; Cases 2-4: PO-0003) |
| [Submit ASN] | Confirmation: Submit ASN? 4 cases (24 pcs) will be created into ASN0003, delivery 18-Oct-2026 · Rit 1. |

### G. Scenarios

| No | Scenario | Expected result |
|---|---|---|
| N1 | Create ASN with the unit PART-X 17-Oct ticked (cases 1-4) | Sections C to F: 4 cases, 5 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y on 5 lines, REMAIN_QTY reduced; Case List opens. |
| N2 | [Submit ASN] and [Yes, submit] | Submit ID handed to the submit process (5.7); ASN0003 and CASE_NO are written back to the 5 rows; only case 5 (CO-14110, Not Ready) stays in the delivery plan. |
| N3 | [Back] / [Cancel] on the Case List | The 5 rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to N, REMAIN_QTY back to the PO qty; the unit is listed again. |
| N4 | 19-Oct: split PO PO-0004 released | Case 5 (CO-14110) is Ready → ASN0004; order date 18-Oct (3 destinations) → ASN0005. |
| E1 | The D/S team holds Japan (CO-14104) after the supplier ticked the unit | MSG8; the whole create fails, nothing is inserted, the delivery plan is refreshed and all units are unticked. |
| E2 | The unit is no longer Ready when [Create ASN] is clicked | MSG7; nothing is inserted; the delivery plan is refreshed. |
| E3 | D/S team ticks PART-X (supplier 5001-1) and a unit of supplier 5002-1 | MSG9; nothing is inserted. |
| E4 | No ASN yet on 22-Oct: the supplier wants order date 18-Oct first | Not possible: per Part Number the oldest Customer Order Date first (15-Oct, then 16-Oct, 17-Oct …); later dates are disabled (Wait: dd-Mon first). |
| E5 | Database error during the insert | Roll back: nothing is kept; error message on the screen and Log FAILED. |

### H. Case selection on 18-Oct (supplier view, PART-X 17-Oct): one check box per supplier case; Content shown to the D/S team only

| Case | Qty | Remaining Qty (not assigned) | Content (D/S team only) | PO | CUT_FLAG | PO Status |
|---|---|---|---|---|---|---|
| Case 1 | 6 | 0 | KR 6 (CO-14105) | PO-0002 6 | Y | Ready |
| Case 2 | 6 | 0 | KR 3 (CO-14106) + KR 3 (CO-14107) | PO-0003 6 | Y | Ready |
| Case 3 | 6 | 0 | JP 6 (CO-14104) | PO-0003 6 | Y | Ready |
| Case 4 | 6 | 0 | TW 6 (CO-14109) | PO-0003 6 | Y | Ready |
| Case 5 | 6 | 6 | 982220 6 (CO-14110) | — | Y | Not Ready |

### I. Check box scenarios (simulation)

| No | User action | Ticked cases | Result |
|---|---|---|---|
| C1 | 18-Oct: tick case 1 | 1 | ASN 6 pcs. |
| C2 | 18-Oct: tick case 3 | 1-3 | Cases 1-2 are ticked too (the selection starts at case 1); ASN 18 pcs. |
| C3 | 18-Oct: tick the unit check box | 1-4 | All Ready cases; case 5 (Not Ready) is not ticked; ASN 24 pcs = ASN0003. |
| C4 | From 1-4, untick case 2 | 1 | Cases 2-4 are unticked; back to case 1. |
| C5 | Case 5 (no PO) | - | Disabled; tooltip message no. 2; Ready on 19-Oct with the split PO PO-0004. |
| C6 | 19-Oct: tick case 1 of 18-Oct first | - | Disabled (Wait: 17-Oct first); after case 1 of 17-Oct is ticked the cases of 18-Oct can be ticked. |
| C7 | Cases without a cut in between (message no. 10) | - | Not in this data: every case of PART-X ends on a cut. When a case does not end on a cut, the next cases up to the cut are ticked together (MSG10). |
