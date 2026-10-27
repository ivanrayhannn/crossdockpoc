# XD10 – ASN Cross Dock Creation Screen

> Generated from `deliverables/function_list_v2/specs/XD10_spec.json` (UISS `XD10_UISS_Screen_ASNCrossDockCreation.xlsx`). Do not edit by hand: change the spec and run `python3 prepare_code/build_md.py`. Document names: GTOPAS / NSP (prototype: G-System / Supplier System).

| Phase | Project | Block | Function | Created | By | Type |
|---|---|---|---|---|---|---|
| DR | Crossdock Optimization | Screen | XD10 ASN Cross Dock Creation Screen | 18-Oct-26 | FID Rayhan | screen |

## Revision

| Rev | Author | Date | Reviewed by | Description |
|---|---|---|---|---|
| 0.1 | FID Rayhan | 18-Oct-26 |  | Initial Draft |

## 1. General

### Objective

- To get the crossdock customer orders for a Delivery Date and Rit and pre-map them to supplier POs ([Search], XD09 Mapping Customer Order and PO Batch).
- To display the delivery plan per Part Number + Customer Order Date with the supplier cases in H0253 order (Case Qty, PO Readiness, ASN options, ASN Status Ready / Partially Ready / Not Ready). Units fully Created or without any pre-mapped case are not listed.
- To let the D/S team (super admin) see the units of all suppliers, the destination detail and hold / release a destination of a unit.
- To tick the supplier cases to send (check box per case, from case 1, cases that belong together) of one Supplier Code + Supplier Plant, map them to their POs (TB_R_INSTRUCTION), review the cases, download the case labels and submit the ASN.
- Submit ASN runs in the background with a Submit ID and follows the existing ASN submit of NSP (refer 5.7).
- Submit ASN (decided 20-Oct, existing structure GTOPAS SPS DB): one TB_R_DAILY_ORDER_MANIFEST row per Pra Daily Order manifest of the cases (same ASN_NO) and one TB_R_DAILY_ORDER_PART row per manifest item and case; the ASN number and the case numbers (case label) are auto generated and their last sequence is saved in TB_R_CASE_LABEL_LAST_SEQ; PART_NAME from TB_M_PART_MASTER.

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
| Detail (expand, D/S) | D/S team only: show / hide the destinations (cases) of a unit with Qty, Pcs/Case and Hold Flag. |
| Customer orders (expand, D/S) | D/S team only: show / hide the customer order lines of a destination (Customer Order No, Detailed Item No, Qty, PO No, PO Date). |
| Hold / Release (D/S) | D/S team only: set HOLD_FLAG of every order line of the destination (part number + customer order date + destination) to 'Y' (hold) or 'N' (release). |
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

| Mode | Section | Description | Search | Detail (expand, D/S) | Customer orders (expand, D/S) | Hold / Release (D/S) | Clear selection | Create ASN | Back | PO detail (expand) | Download Case Label | Cancel | Submit ASN | Yes / No | OK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Initial Mode | Delivery | Delivery Date = today (business date); Rit = first rit of the date; Route displayed | E | D | D | D | D | D | D | D | D | D | D | D | D |
| Initial Mode | Delivery plan | Empty: 'Choose the Delivery Date and Rit, then click Search.' Filters disabled | D | D | D | D | D | D | D | D | D | D | D | D | D |
| List Mode - Supplier | Delivery | Refer 1.a | E | D | D | D | D | D | D | D | D | D | D | D | D |
| List Mode - Supplier | Delivery plan | Units of the login supplier (Supplier Code + Plant) only; unit rows with their supplier case rows (check box per case, no destinations); Part Number / Status filters | D | D | D | D | D | D | D | D | D | D | D | D | D |
| List Mode - Supplier | Selection bar | Enabled when Ready units are ticked | D | D | D | D | E | E | D | D | D | D | D | D | D |
| List Mode - D/S Team | Delivery plan | All suppliers (Supplier · Plant column) plus the destination detail with Hold Flag; a unit with all destinations on hold is listed as On Hold. The D/S team is super admin: it can also create and submit | D | E | E | E | D | D | D | D | D | D | D | D | D |
| List Mode - D/S Team | Selection bar | Refer 2.c | D | D | D | D | E | E | D | D | D | D | D | D | D |
| Case List Mode (sub screen) | ASN summary | ASN No (assigned on submit), supplier, Delivery Date · Rit · Route, Delivery Qty, cases | D | D | D | D | D | D | E | D | D | D | D | D | D |
| Case List Mode (sub screen) | Case list | Case Number, Part Number, Qty; expand PO detail | D | D | D | D | D | D | D | E | E | D | D | D | D |
| Case List Mode (sub screen) | Footer | Submit enabled when there are cases | D | D | D | D | D | D | D | D | D | E | E | D | D |
| Confirmation / Notification | Submit confirmation | 'Submit ASN?' Yes / No | D | D | D | D | D | D | D | D | D | D | D | E | D |
| Confirmation / Notification | Success notification | Submit ID banner on the delivery plan; result in Log Monitoring | D | D | D | D | D | D | D | D | D | D | D | D | E |

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
  g["XD09: get customer orders, pre-map to PO (#TEMP_INSTRUCTION)"]
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

### 2. Delivery plan after Search (supplier view, 18-Oct, simulasi_asn_rev.xlsx): PART-X 17-Oct, cases 1-4 Ready, case 5 Not Ready (Short PO: T0409013 18 of 30 pcs)

![2. Delivery plan after Search (supplier view, 18-Oct, simulasi_asn_rev.xlsx): PART-X 17-Oct, cases 1-4 Ready, case 5 Not Ready (Short PO: T0409013 18 of 30 pcs)](../../deliverables/uiss_screens/asn_crossdock/c_02_delivery_plan.png)

### 3. D/S team: destination detail (warehouse cases, Hold Flag) and customer orders of a destination (open qty, cases, PO)

![3. D/S team: destination detail (warehouse cases, Hold Flag) and customer orders of a destination (open qty, cases, PO)](../../deliverables/uiss_screens/asn_crossdock/c_03_ds_detail.png)

### 4. D/S team: Thailand (CO-14104) on hold; the H0253 order and the cases are computed again without it

![4. D/S team: Thailand (CO-14104) on hold; the H0253 order and the cases are computed again without it](../../deliverables/uiss_screens/asn_crossdock/c_04_ds_hold.png)

### 5. Case 3 of PART-X 17-Oct ticked: cases 1-3 are selected (the selection always starts at case 1)

![5. Case 3 of PART-X 17-Oct ticked: cases 1-3 are selected (the selection always starts at case 1)](../../deliverables/uiss_screens/asn_crossdock/c_05_selected.png)

### 5a. Other session (D/S team) holds a destination of a ticked unit

![5a. Other session (D/S team) holds a destination of a ticked unit](../../deliverables/uiss_screens/asn_crossdock/c_05a_ds_hold_other_session.png)

### 5b. Create ASN: hold message, the whole create fails

![5b. Create ASN: hold message, the whole create fails](../../deliverables/uiss_screens/asn_crossdock/c_05c_hold_conflict.png)

### 5c. Delivery plan refreshed automatically, all cases unticked

![5c. Delivery plan refreshed automatically, all cases unticked](../../deliverables/uiss_screens/asn_crossdock/c_05d_after_refresh.png)

### 5d. D/S team: units of two suppliers ticked (PART-D of supplier 50330, prototype only), Create ASN: one supplier per ASN

![5d. D/S team: units of two suppliers ticked (PART-D of supplier 50330, prototype only), Create ASN: one supplier per ASN](../../deliverables/uiss_screens/asn_crossdock/c_05e_supplier_conflict.png)

### 6. Case List sub screen: cases 1-4 of PART-X 17-Oct = ASN0003

![6. Case List sub screen: cases 1-4 of PART-X 17-Oct = ASN0003](../../deliverables/uiss_screens/asn_crossdock/c_06_case_list.png)

### 7. Case List: PO detail of a case

![7. Case List: PO detail of a case](../../deliverables/uiss_screens/asn_crossdock/c_07_case_expand.png)

### 8. Submit confirmation

![8. Submit confirmation](../../deliverables/uiss_screens/asn_crossdock/c_08_confirm.png)

### 9. Submit ID banner (result in Log Monitoring)

![9. Submit ID banner (result in Log Monitoring)](../../deliverables/uiss_screens/asn_crossdock/c_09_submit_id.png)

### 10. Delivery plan after submit: only case 5 (CO-14110) is left, Not Ready until the split PO T0409014

![10. Delivery plan after submit: only case 5 (CO-14110) is left, Not Ready until the split PO T0409014](../../deliverables/uiss_screens/asn_crossdock/c_10_list_after.png)

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
| 9 | Supplier · Plant (D/S) | #TEMP_INSTRUCTION | SUPPLIER_CD / SUPPLIER_PLANT | Char | - | O | Label | Left | - | N | {code} · {plant} | - | D/S team only (all suppliers). The supplier sees its own Supplier Code + Plant only. |
| 10 | Customer Order Date | #TEMP_INSTRUCTION | ORDER_DT | Date | - | O | Label | Left | - | N | DD-Mon-YYYY | - | Customer Order Date of the unit. |
| 11 | Part Number | #TEMP_INSTRUCTION | PART_NO | Char | 15 | O | Label | Left | - | N | - | - | Part number of the unit (distinct per Customer Order Date). Part name is not shown. |
| 12 | Case Qty | Computed | - | Number | - | O | Label | Right | - | N | ZZ9 | - | Number of supplier cases of the unit: open qty / pcs/case, cut in H0253 order (e.g. 30 pcs, 6 pcs/case = 5 cases); a case can hold several destinations. |
| 13 | PO Readiness (case) | Computed | - | Number | - | O | Label | Right | - | N | ZZ9 | - | Cases whose whole qty is pre-mapped to a PO; red when lower than Case Qty. |
| 14 | ASN Status | #TEMP_INSTRUCTION | CROSSDOCK_STATUS | Char | 1 | O | Label | Left | - | N | - | - | Ready (all blocks '6', green) / Partially Ready (first block '6', a later block '7', amber) / Not Ready (first block '7', row highlighted) / On Hold (D/S only). Refer 5.2. |
| 15 | Detail (expand, D/S) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Shown to the D/S team only. Opens the destination detail. |
| **<Supplier Cases of a Unit (H0253 order)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 16 | Select case (check box) | Key-in | - | Char | - | I | CheckBox | Center | <unchecked> | N | - | Enabled only when the case and every earlier case have a PO | One check box per supplier case. The selection always starts at case 1 and takes the cases that belong together (Case Group = GROUP_SEQ of XD09, not shown on the screen): ticking case n ticks the earlier cases and the other cases of its group (message no. 10, e.g. tick case 2 -> cases 2-3 belong together, so cases 1-3); unticking case n unticks its group and the later cases. Refer 5.4. |
| 17 | Case | #TEMP_INSTRUCTION | CASE_SEQ | Number | - | O | Label | Right | - | N | Z9 | - | Supplier case number in H0253 order (PCS_CASE pcs). |
| 18 | Qty (pcs) | #TEMP_INSTRUCTION | ASSIGNED_QTY | Number | - | O | Label | Right | - | N | ZZZ9 | - | Pcs of the case (= PCS_CASE). |
| 19 | Remaining Qty (not assigned) | #TEMP_INSTRUCTION | ASSIGNED_QTY (PO_NO NULL) | Number | - | O | Label | Right | - | N | ZZZ9 | - | Pcs of the case without a PO yet (sum of the slices with PO_NO NULL); 0 when the whole case is assigned; red when > 0. |
| 20 | Content (D/S team) | #TEMP_INSTRUCTION | DESTINATION_CD / CUSTOMER_ORDER_NO / ASSIGNED_QTY | Char | - | O | Label | Left | - | N | - | - | D/S team only (not shown to the supplier): slices of the case in H0253 order, e.g. VN 3 (CO-14106) + VN 3 (CO-14107). |
| 21 | PO | #TEMP_INSTRUCTION | PO_NO / ASSIGNED_QTY | Char | - | O | Label | Left | - | N | {PO No} {qty} | - | POs of the case with the assigned qty, e.g. T0409013 6. |
| 22 | PO Status | #TEMP_INSTRUCTION | CROSSDOCK_STATUS | Char | - | O | Label | Left | - | N | - | - | '6' Ready (green) / '7' Not Ready (amber): the case or an earlier case has no PO yet. |
| **<Destination Detail (D/S team only)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 23 | Destination | #TEMP_INSTRUCTION | DESTINATION_CD | Char | 7 | O | Grid | Left | - | N | {code} · {name} | - | One row per destination with its number of cases (qty / pcs/case); name from TB_M_H0125_DESTINATION. |
| 24 | Case | Computed | - | Number | - | O | Grid | Right | - | N | 9 | - | 1; 0 when the destination is on hold. |
| 25 | Qty (pcs) | #TEMP_INSTRUCTION | CUST_ORDER_QTY | Number | 8 | O | Grid | Right | - | N | ZZ,ZZ9 | - | Sum of the order qty of the destination; '(on hold)' when held. |
| 26 | Pcs/Case | Part master | PCS_PER_CASE | Number | - | O | Grid | Right | - | N | ZZ9 | - | Pieces per case of the part (next to Qty). |
| 27 | Customer orders (expand, D/S) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Opens the customer order lines of the destination. |
| **<Customer Orders of a Destination (D/S team only)>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 28 | Customer Order No / Detailed Item No | #TEMP_INSTRUCTION | CUSTOMER_ORDER_NO / DETAILED_ITEM_NO | Char | - | O | Grid | Left | - | N | - | - | Original order row, e.g. order A 4 pcs and order B 2 pcs to Vietnam. |
| 29 | Qty (pcs) / PO No / PO Date | #TEMP_INSTRUCTION | CUST_ORDER_QTY / PO_NO / PO_DT | Char | - | O | Grid | Left | - | N | - | - | Pre-mapping of the line. |
| 30 | Hold / Release (D/S) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Hold Flag of the destination: 'N · Hold' sets Y, 'Y · Release' sets N on every order line of the destination. Refer 5.3. |
| **<Selection Bar Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 31 | Selection summary | Computed | - | Char | - | O | Label | Left | - | N | - | - | '{n} units · {c} cases · {q} pcs selected · {units}'. Empty: hint that cases of different units / dates can go into one ASN. |
| 32 | Clear selection | - | - | - | - | I | Button | Center | Disabled | N | - | - | Unticks all cases. |
| 33 | Create ASN | - | - | - | - | I | Button | Center | Disabled | N | - | - | Refer Operation Description 5.4. |
| **<Case List Sub Screen - ASN Summary>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 34 | Back | - | - | - | - | I | Button | Center | Enabled | N | - | - | Returns to ASN Crossdock Creation without submitting; the draft mapping is released. |
| 35 | ASN No | TB_R_DAILY_ORDER_MANIFEST | ASN_NO | Char | TBD | O | Label | Left | - | N | - | - | Existing ASN numbering; 'auto · assigned on submit'. |
| 36 | Supplier · Plant | #TEMP_INSTRUCTION | SUPPLIER_CD / SUPPLIER_PLANT | Char | TBD | O | Label | Left | - | N | - | - | Supplier of the cases (one Supplier Code + Plant per ASN). |
| 37 | Delivery Date · Rit · Route | TB_R_INSTRUCTION | DELIVERY_DT / RIT_CYCLE / ROUTE | Char | - | O | Label | Left | - | N | - | - | From the Search. |
| 38 | Delivery Qty | Computed | - | Number | - | O | Label | Left | - | N | ZZ,ZZ9 pcs | - | Total pieces of the ASN. |
| 39 | Cases | Computed | - | Number | - | O | Label | Left | - | N | N cases | - | Number of cases. |
| **<Case List Sub Screen - Case List>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 40 | Download Case Label | - | - | - | - | I | Button | Center | Enabled | N | - | - | Downloads the labels of all cases (existing label format). |
| 41 | PO detail (expand) | - | - | - | - | I | Button | Center | Enabled | N | - | - | Opens the PO detail of the case. |
| 42 | Case Number | TB_R_INSTRUCTION | CASE_SEQ | Char | - | O | Grid | Left | - | N | Case {n} | - | Case sequence; the case number is auto generated on submit by checking the last sequence (existing table). |
| 43 | Part Number | TB_R_INSTRUCTION | PART_NO | Char | 15 | O | Grid | Left | - | N | - | - | Supplier case of PCS_CASE pcs in H0253 order; a case can hold several destinations. |
| 44 | Qty / Total | TB_R_INSTRUCTION | QTY | Number | - | O | Grid | Right | - | N | ZZ,ZZ9 | - | Pieces of the case; total of all cases. |
| 45 | PO No / Manifest No / Manifest Item / PO Qty | TB_R_INSTRUCTION | PO_NO / MANIFEST_NO / MANIFEST_ITEM / ORDER_QTY | Char | - | O | Grid | Left | - | N | - | - | Expanded PO detail of the case. |
| 46 | Cancel | - | - | - | - | I | Button | Center | Enabled | N | - | - | Same as Back. |
| 47 | Submit ASN | - | - | - | - | I | Button | Center | Enabled | N | - | - | Refer Operation Description 5.5. |
| 48 | No rit cycle message | Computed | - | Char | - | O | Label | Left | - | N | - | - | Message no. 5 when no rit is available. |

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

#### 2. Update TB_R_H0253_ORDER_CONTROL_PRE – [Create ASN]: the lines of the chosen blocks
- Source: #TEMP_INSTRUCTION (chosen blocks)
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

#### 3. Insert / Update TB_R_PRA_DAILY_ORDER_MAPPED – [Create ASN]: one row per PO part used by the chosen blocks (insert when none yet)
- Source: #TEMP_INSTRUCTION (chosen blocks)
- Destination keys: PO_NO + MANIFEST_NO + MANIFEST_ITEM = PO part of the pre-mapping

| Source field | Destination field | Description |
|---|---|---|
|  | MAPPED_QTY | + ASSIGNED_QTY of the chosen blocks; - again on Back / Cancel |
| PO_NO | PO_NO |  |
| MANIFEST_NO | MANIFEST_NO |  |
| MANIFEST_ITEM | MANIFEST_ITEM |  |
| PART_NO | PART_NO |  |
| SUPPLIER_CD | SUPPLIER_CD |  |
| SUPPLIER_PLANT | SUPPLIER_PLANT |  |
| ORDER_QTY | ORDER_QTY |  |
|  | CREATED_BY | Login user ID (insert only) |
|  | CREATED_DT | Server system date-time (insert only) |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 4. Insert TB_R_INSTRUCTION – [Create ASN]: one row per case x line x PO
- Source: #TEMP_INSTRUCTION (chosen blocks)

| Source field | Destination field | Description |
|---|---|---|
|  | DRAFT_ID | New id per [Create ASN] (same for all rows of the creation) |
|  | CASE_SEQ | Case sequence: selected unit, then CASE_SEQ of XD09 (H0253 order) |
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
| ASSIGNED_QTY | QTY |  |
| Delivery Date | DELIVERY_DT |  |
| Rit | RIT_CYCLE |  |
| Route | ROUTE |  |
|  | INSTRUCTION_ID | Running number (existing sequence) |
| SUPPLIER_CD | SUPPLIER_CD |  |
| SUPPLIER_PLANT | SUPPLIER_PLANT |  |
|  | ASN_NO | NULL (filled by the submit process, refer 5.7) |
|  | CASE_NO | NULL (filled by the submit process, refer 5.7) |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date-time |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 5. Insert TB_R_DAILY_ORDER_MANIFEST – Submit ASN (5.7): one row per manifest of the cases; all rows of the submit share one ASN_NO
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

#### 6. Insert TB_R_DAILY_ORDER_PART – Submit ASN (5.7): one row per manifest item and case
- Source: TB_R_INSTRUCTION + TB_R_PRA_DAILY_ORDER_PART + TB_M_PART_MASTER (keys: MANIFEST_NO + MANIFEST_ITEM + CASE_SEQ = One row per manifest item and case)

| Source field | Destination field | Description |
|---|---|---|
|  | SUB_MANIFEST_NO | Of the TB_R_DAILY_ORDER_MANIFEST row of the manifest |
| TB_R_INSTRUCTION.MANIFEST_NO | MANIFEST_NO |  |
| TB_R_INSTRUCTION.MANIFEST_ITEM | MANIFEST_ITEM |  |
|  | CASE_NO | Auto generated per CASE_SEQ (case label); last sequence CASE_LABEL_LAST_SEQ in TB_R_CASE_LABEL_LAST_SEQ |
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

#### 7. Update TB_R_INSTRUCTION – Submit ASN (5.7): Every row of the Submit ID
- Source: Result of the inserts
- Destination keys: INSTRUCTION_ID = Rows of the Submit ID

| Source field | Destination field | Description |
|---|---|---|
|  | ASN_NO | ASN No of the manifest |
|  | CASE_NO | Case No of the CASE_SEQ |
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

#### 8. Insert Log (existing) – Submit ASN (5.7): Messages of the Submit ID (existing log columns)
- Source: Result of this run

| Source field | Destination field | Description |
|---|---|---|
|  | Process / Submit ID | Submit ID |
|  | Function ID | 'XD10' |
|  | Status | PROCESSING / SUCCESS / ERROR |
|  | Message ID / Message | LOG2 - LOG5 |
|  | User / Date-time | User ID, server system date-time |

#### 9. Update TB_R_CASE_LABEL_LAST_SEQ – Submit ASN (5.7): new last sequence of the supplier + plant
- Source: Last sequence of the submit
- Destination keys: SUPPLIER_CD + SUPPLIER_PLANT_CD = Supplier of the ASN

| Source field | Destination field | Description |
|---|---|---|
|  | ASN_LAST_SEQ | Last sequence used for the ASN number |
|  | CASE_LABEL_LAST_SEQ | Last sequence used for the case numbers |
|  | CHANGED_BY | User ID |
|  | CHANGED_DT | Server system date-time |

## 6. Operation description

### 5.0 Behaviour shown by the simulation (simulasi_asn_rev.xlsx)

- 18-Oct, delivery plan PART-X 17-Oct: 5 cases; PO check order 30 pcs vs PO T0409013 18 pcs → Short PO; cases 1-4 Ready (T0409012 rest 6 + T0409013), case 5 (CO-14110) Not Ready with Remaining Qty 6.
- The selection starts at case 1 and ends on a case with CUT_FLAG Y: ticking case 3 selects cases 1-3; case 5 is disabled. Per Part Number the oldest Customer Order Date first: on 19-Oct the cases of 18-Oct show "Wait: 17-Oct first" until case 1 of 17-Oct (CO-14110) is ticked.
- [Create ASN] with cases 1-4: 5 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y on the 5 lines that are complete (CO-14110 stays N), MAPPED_QTY T0409012 6, T0409013 18. [Submit ASN] gives ASN0003 with case numbers C-0003-01 … 04; only case 5 stays in the delivery plan.
- One line in two ASNs: CO-14115 12 pcs = case 1 (ASN0006, PO_MAPPED_FLAG N, open 6) and case 2 (ASN0007, PO_MAPPED_FLAG Y).
- D/S hold of Thailand (CO-14104) after the supplier ticked the unit: [Create ASN] fails (MSG8); the cases are computed again without Thailand. A draft not submitted is released by the next XD08 run ([Submit ASN] of the old draft: MSG11). A cancel after the ASN goes to XD11 (CO-14104 in ASN0003 case 3 → CO-14111).

### 5.1 Initial Display and Search

a. On first display Delivery Date = today (business date), Rit = first rit of the date, Route displayed (disabled). The delivery plan is empty.
b. [Search] runs XD09 Mapping Customer Order and PO Batch (UISS XD09): the open qty of the H0253 customer orders with order status 7 and Hold Flag N, in the H0253 order per Part Number + Customer Order Date, pre-mapped to the PO parts of the Pra Daily Order (PO date order), cut into supplier cases and blocks in the temporary table #TEMP_INSTRUCTION (pre-mapping only; nothing is saved yet). Supplier: units of the login Supplier Code + Plant; D/S team: all suppliers.
c. The delivery plan shows one row per Part Number + Customer Order Date, sorted Ready, Partially Ready, Not Ready, then Part Number ascending. Units without any pre-mapped case and units fully Created are not listed. Part Number and Status filters apply at once. No row: message no. 3.
d. Delivery Date and Rit do not filter the orders; they are carried to the ASN. Rit and Route come from the existing route master table.

### 5.2 Status Rule

a. Unit = Part Number + Customer Order Date. H0253 order (decided 21-Oct): Allocation Priority (= Customer Order Date), Customer Code, Customer Order No, Customer Order Date, Customer Order Time, Destination Code, Detailed Item No, Serial No (fixed order).
b. Supplier case = PCS_CASE pcs in H0253 order; a case can hold several customer orders, POs and destinations. Case Qty = number of supplier cases; PO Readiness (case) = cases whose whole qty is pre-mapped to a PO.
c. The warehouse packs 1 case = 1 destination, so an ASN may stop only after a case where every destination of the unit is a multiple of PCS_CASE (valid cut). The cases up to a valid cut are a block = one ASN option step (e.g. 18-Oct PART-X 17-Oct: every case ends on a cut, blocks case 1 | 2 | 3 | 4 | 5).
d. A block is Ready ('6') when it and every earlier block have a PO; otherwise Not Ready ('7'): blocks are never skipped. Unit: Ready (all blocks), Partially Ready (the first k blocks), Not Ready (first block; check box disabled, message no. 2).
e. Created: blocks in a submitted ASN are no longer in the delivery plan (shown in ASN Inquiry); the open qty of the unit is cut again from case 1 in the same order at the next [Search].

### 5.3 Detail and Hold (D/S team)

a. The D/S team can expand a unit: one row per destination with Case, Qty (pcs), Pcs/Case and Hold Flag; each destination can be expanded to its customer order lines (Customer Order No, Detailed Item No, Qty, PO No, PO Date). The supplier sees the header only.
b. Hold / Release is done per destination: it updates HOLD_FLAG of every order line of the unit and destination in TB_R_H0253_ORDER_CONTROL_PRE (refer Data Edit Mapping). A held destination is not taken by Search; the unit is computed without it. A unit with all destinations on hold is shown as On Hold to the D/S team only.
c. HOLD_FLAG is 'N' when the line is first replicated (XD08) and is kept on the next replications.

### 5.4 Select Cases and Create ASN

a. The user ticks the supplier cases to send with the check box of each case row. Cases that belong together (Case Group = GROUP_SEQ of XD09, not shown) are always sent together, so that at receiving every destination completes its warehouse case. The ticked cases of a unit start at case 1: ticking a case ticks the earlier cases and the other cases of its group (message no. 10). Example (18-Oct, PART-X 17-Oct): ticking case 3 gives cases 1-3; case 5 (no PO) cannot be ticked. When a case does not end on a cut (e.g. a case with VN 4 + TH 2), the cases up to the next cut are ticked with it. Only Ready cases can be ticked. One ASN is for one Supplier Code + Supplier Plant (existing rule): ticked units of more than one supplier give message no. 9 and nothing is created.
b. [Create ASN] does the real mapping of the chosen blocks in one transaction: the slices inserted into TB_R_INSTRUCTION (case and line sequence of XD09), MAPPED_QTY in the new table TB_R_PRA_DAILY_ORDER_MAPPED, and PO_MAPPED_FLAG = 'Y' on the H0253 lines that are now completely in TB_R_INSTRUCTION. Then the Case List opens.
c. Before mapping, the ticked units are re-checked in the same transaction (row lock on the H0253 lines): if a line got HOLD_FLAG = 'Y' after the unit was ticked (e.g. the D/S team held a destination in another session), the creation fails for the whole selection (also the units that are not held): message no. 8 (Hold), the delivery plan is refreshed automatically and all ticked units are unticked. If a unit is no longer Ready for another reason (changed by another user), message no. 7.
d. [Back] / [Cancel] on the Case List cancel the creation: the rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to 'N' and MAPPED_QTY reduced again, so the blocks can be selected again. A draft left open (no Submit, no Cancel) is released by the next run of XD08 (every run releases all drafts, decided 23-Oct): the cases come back in the delivery plan and the supplier ticks them again.

### 5.5 Case List and Submit ASN

a. The summary shows ASN No (assigned on submit), supplier, Delivery Date · Rit · Route of the Search, Delivery Qty (pcs) and number of cases.
b. Each case shows Case Number, Part Number and Qty; the expand shows PO No, Manifest No, Manifest Item and PO Qty. Customer order data is not shown here.
c. [Download Case Label]: follows the existing case label of NSP.
d. [Submit ASN]: confirmation (message no. 4). Yes: the draft is handed with a Submit ID to the submit process (refer 5.7); the submit process follows the existing ASN. It reads TB_R_INSTRUCTION and inserts the existing tables TB_R_DAILY_ORDER_MANIFEST (status Created) and TB_R_DAILY_ORDER_PART; ASN No and Case No follow the existing numbering (case number auto generated by checking the last sequence). The screen returns to the delivery plan and shows the Submit ID (message no. 6); there is no success popup. The result message is written by the submit process (5.7) to the existing log (Log Monitoring).

### 5.6 Notes

- #TEMP_INSTRUCTION is temporary (pre-mapping of [Search]). TB_R_INSTRUCTION holds the mapping from [Create ASN] until submit or Back / Cancel. TB_R_PRA_DAILY_ORDER_MAPPED is a new table for the mapped qty. Submitted ASNs are in TB_R_DAILY_ORDER_MANIFEST / PART and shown in ASN Inquiry (XD15).
- Case number: the format follows the existing NSP case number; the last sequence is kept in the TB_R_CASE_LABEL_LAST_SEQ (note only, not detailed here).
- Cancel of an order is not done in NSP: it comes from the source (H0253 order status '2'); NSP only holds (HOLD_FLAG). Refer XD08 / XD11.
- The prototype has a 'Business date' switch (PO release) and a 'View as' switch (Supplier / D/S team); they are not part of the real screen.

### 5.7 Submit ASN Process (backend, follows the existing ASN)

a. Re-check before the submit: the draft must still exist (not released by XD08) and every line of it must still have UPD_STATUS NULL and the same qty. Otherwise nothing is submitted, the draft is released and message no. 11 is shown; the supplier searches again.
b. The screen generates the Submit ID, writes the start message to the log (LOG2) and starts the submit process. The screen returns to the delivery plan and shows the Submit ID.
c. Read the rows of the Submit ID from TB_R_INSTRUCTION (one Supplier Code + Plant). Take the ASN No from the existing numbering and auto generate one Case No per case by checking the last sequence (TB_R_CASE_LABEL_LAST_SEQ; format as existing).
d. Insert TB_R_DAILY_ORDER_MANIFEST (status Created) and TB_R_DAILY_ORDER_PART (existing tables, refer Data Edit Mapping); write ASN_NO / CASE_NO back to TB_R_INSTRUCTION.
e. No error: commit, write the result (LOG3) and end (LOG4) messages. Error: roll back, release the mapping (delete the rows from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to 'N', MAPPED_QTY of TB_R_PRA_DAILY_ORDER_MAPPED reduced again), write the error (LOG5). Exit.

- Submit ASN runs as a batch so the screen does not wait; the user sees the Submit ID and checks the result in Log Monitoring. No success popup is shown on the screen.
- The log follows the existing NSP log (same table and columns); the Submit ID is the key to find the run.
- All-or-nothing: on error nothing is saved and the mapping made by [Create ASN] is released (rows deleted from TB_R_INSTRUCTION), so the units can be selected again.
- The ASN is saved in the existing tables TB_R_DAILY_ORDER_MANIFEST / TB_R_DAILY_ORDER_PART; the case number is auto generated by checking the last sequence kept in the TB_R_CASE_LABEL_LAST_SEQ (format as existing, not detailed here).
- The submit process (Submit ID, batch call, log) follows the existing ASN submit of NSP.

### 5.8 Sample Create ASN

- Dummy example of [Create ASN] (case packing, TB_R_INSTRUCTION rows, flags, Case List, scenarios): see sheet Sample Input.

## 7. Display messages

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| **Delivery Plan (tooltip of disabled check box)** |  |  |  |  |  |
| MSG1 | Hover on disabled check box | Unit is On Hold (D/S) | Info | All destinations are on hold | Release a destination. |
| MSG2 | Hover on disabled check box | Unit is Not Ready | Info | Not Ready: case {n} of {Part No} / {Customer Order Date} (or an earlier case) is not assigned to a PO yet ({k} of {c} cases assigned) | Wait for the next PO. |
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

#### #TEMP_INSTRUCTION (temp, proposed)
Temporary table of one Search run (session): the open qty of the customer order lines (H0253, order status 7, Hold Flag N) in H0253 order, pre-mapped to the supplier POs (Pra Daily Order) and cut into supplier cases and blocks. One row per line x PO x supplier case; PO_NO NULL for the qty still without a PO. Columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| INSTRUCTION_ID | BIGINT | Y | N | Running number within the session |
| SORT_SEQ | NUMBER(6) |  | N | H0253 order of the line within the unit (refer 4.1) |
| CUSTOMER_CD | VARCHAR(7) |  | N | H0253.CUSTOMER_CD (order key 1) |
| CUSTOMER_ORDER_NO | VARCHAR(8) |  | N | H0253.CUSTOMER_ORDER_NO (order key 2) |
| ORDER_DT | DATE |  | N | Customer Order Date (H0253.ORDER_DT; unit and order key 3) |
| ORDER_TIME | VARCHAR(6) |  | N | H0253.ORDER_TIME (order key 4) |
| DESTINATION_CD | VARCHAR(7) |  | N | H0253.DESTINATION_CD (order key 5) |
| DETAILED_ITEM_NO | VARCHAR(4) |  | N | H0253.DETAILED_ITEM_NO (order key 6) |
| SERIAL_NO | VARCHAR(7) |  | N | H0253.SERIAL_NO (order key 7) |
| PART_NO | VARCHAR(15) |  | N | Order part number (H0253.SHIPPING_PART_NO) |
| ORDER_STATUS | VARCHAR(1) |  | N | H0253.ORDER_STATUS ('7' Cross Dock) |
| CUST_ORDER_QTY | NUMBER(8) |  | N | Order status qty of the customer order line (H0253.ORDER_STATUS_QTY) |
| OPEN_ORDER_QTY | NUMBER(8) |  | N | Qty of the line not yet in TB_R_INSTRUCTION (sent or in an open Case List) |
| ASSIGNED_QTY | NUMBER(8) |  | N | Qty of this slice (line x PO x supplier case) |
| PO_NO | VARCHAR(TBD) |  | Y | Supplier PO number (Pra Daily Order Manifest); NULL while not assigned |
| MANIFEST_NO | VARCHAR(TBD) |  | Y | Manifest number |
| MANIFEST_ITEM | VARCHAR(TBD) |  | Y | Manifest item number (Pra Daily Order Part) |
| PO_DT | DATE |  | Y | Order date of the PO (PO Date) |
| ORDER_QTY | NUMBER(TBD) |  | Y | Order qty of the PO part |
| SUPPLIER_CD | VARCHAR(TBD) |  | Y | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) |  | Y | Supplier plant |
| SUB_SUPPLIER_CD | VARCHAR(TBD) |  | Y | Sub supplier code |
| SUB_SUPPLIER_PLANT | VARCHAR(TBD) |  | Y | Sub supplier plant |
| ORDER_TYPE | VARCHAR(TBD) |  | Y | Order type of the PO |
| DOCK_CD | VARCHAR(TBD) |  | Y | Dock code |
| ETD_ORI | DATE |  | Y | Original ETD |
| PCS_CASE | NUMBER(4) |  | N | Pcs per case of the part (TB_M_PART_CANDIDATE.PCS_CASE) |
| CASE_SEQ | NUMBER(4) |  | N | Supplier case of the slice within the unit (PCS_CASE pcs in H0253 order) |
| LINE_SEQ | NUMBER(4) |  | N | Sequence of the slice within the case |
| CUM_DEST_QTY | NUMBER(8) |  | N | Cumulative qty of the destination within the unit up to this slice |
| SEQ_QTY | NUMBER(4) |  | N | Fill of the warehouse case (1 case = 1 destination) of the destination after this slice: 1..PCS_CASE, starts again after PCS_CASE |
| CUT_FLAG | VARCHAR(1) |  | N | 'Y' on the last slice of a case after which the ASN may stop (every destination a multiple of PCS_CASE) |
| GROUP_SEQ | NUMBER(4) |  | N | Case Group (block) of the slice: the cases up to and including a valid cut; the cases of a group are sent together |
| CROSSDOCK_STATUS | VARCHAR(1) |  | N | Status of the block: '6' Ready (the block and every earlier block have a PO) / '7' Not Ready |

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

#### TB_R_PRA_DAILY_ORDER_MAPPED (transaction, proposed)
New table: mapped qty per Pra Daily Order PO part (instead of a new column in the Pra Daily Order). Name and columns proposed.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PO_NO | VARCHAR(TBD) | Y | N | PO number (Pra Daily Order Manifest) |
| MANIFEST_NO | VARCHAR(TBD) | Y | N | Manifest number |
| MANIFEST_ITEM | VARCHAR(TBD) | Y | N | Manifest item number (Pra Daily Order Part) |
| PART_NO | VARCHAR(15) |  | N | Part number |
| SUPPLIER_CD | VARCHAR(TBD) |  | N | Supplier code |
| SUPPLIER_PLANT | VARCHAR(TBD) |  | N | Supplier plant |
| ORDER_QTY | NUMBER(TBD) |  | N | PO qty of the part |
| MAPPED_QTY | NUMBER(TBD) |  | N | Qty already mapped to customer orders by [Create ASN]; open qty = ORDER_QTY - MAPPED_QTY |
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

## Sample Input

**Sample Create ASN - ASN Cross Dock Creation (simulasi_asn_rev.xlsx, 18-Oct-2026)**

- Data of simulasi_asn_rev.xlsx (also in the prototype, business date 18-Oct). Supplier 50221 plant 1, Delivery Date 18-Oct-2026, Rit 1, Route SD01. PART-X, Pcs/Case = 6. ASN0001 (CO-14101) and ASN0002 (CO-14103) are already submitted, so the oldest open Customer Order Date is 17-Oct.
- Order date 17-Oct: 4 destinations, 30 pcs; PO T0409013 (PO date 18-Oct) has only 18 pcs (Short PO, abnormality); the rest of T0409012 (6) is taken first (older PO date). The split PO T0409014 (12) comes on 19-Oct.
- The supplier ticks the unit PART-X 17-Oct (cases 1-4, case 5 is Not Ready) and clicks [Create ASN]; the submit gives ASN0003.

### A. Input: pre-mapping of XD09 (#TEMP_INSTRUCTION) in H0253 order: Customer Order Date, Customer Code, Customer Order No, …

| Sort Seq | Customer Order No | Detailed Item No | Serial No | Destination | Open Qty | PO No | Assigned Qty | Case | Cut | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CO-14105 | 001 | 0000001 | 9715310 (Vietnam) | 6 | T0409012 | 6 | 1 | Y | 6 |
| 2 | CO-14106 | 001 | 0000001 | 9715310 (Vietnam) | 3 | T0409013 | 3 | 2 | N | 6 |
| 3 | CO-14107 | 001 | 0000001 | 9715310 (Vietnam) | 3 | T0409013 | 3 | 2 | Y | 6 |
| 4 | CO-14104 | 001 | 0000001 | 9722D10 (Thailand) | 6 | T0409013 | 6 | 3 | Y | 6 |
| 5 | CO-14109 | 001 | 0000001 | 9811110 (Philippines) | 6 | T0409013 | 6 | 4 | Y | 6 |
| 6 | CO-14110 | 001 | 0000001 | 982220 | 6 | — | 6 | 5 | Y | 7 |

### B. Input: PO parts before [Create ASN] (Pra Daily Order: manifest with CROSS_DOCK_FLAG = 'X')

| PO No | Manifest No | Manifest Item | Part No | PO Qty (ORDER_QTY) | Mapped Qty (TB_R_PRA_DAILY_ORDER_MAPPED) | Open Qty |
|---|---|---|---|---|---|---|
| T0409012 | 3126035912 | 0001 | PART-X | 6 | 0 | 6 |
| T0409013 | 3126035913 | 0001 | PART-X | 18 | 0 | 18 |

### C. Supplier cases (6 pcs in H0253 order; CUT_FLAG Y = the ASN may stop after the case)

| Case | Qty | Content (customer order qty (PO)) | CUT_FLAG | Status |
|---|---|---|---|---|
| Case 1 | 6 | CO-14105 6 (T0409012) | Y | Ready |
| Case 2 | 6 | CO-14106 3 (T0409013) + CO-14107 3 (T0409013) | Y | Ready |
| Case 3 | 6 | CO-14104 6 (T0409013) | Y | Ready |
| Case 4 | 6 | CO-14109 6 (T0409013) | Y | Ready |
| Case 5 | 6 | CO-14110 6 (no PO) | Y | Not Ready |

### D. Result: rows inserted into TB_R_INSTRUCTION (cases 1-4; ASN_NO / CASE_NO filled on submit)

| INSTRUCTION_ID | CASE_SEQ | LINE_SEQ | PART_NO | ORDER_DT | DESTINATION_CD | CUSTOMER_ORDER_NO | DETAILED_ITEM_NO | SERIAL_NO | QTY | PO_NO | MANIFEST_NO | MANIFEST_ITEM | DELIVERY_DT | RIT_CYCLE | ROUTE | ASN_NO | CASE_NO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1 | PART-X | 17-Oct-2026 | 9715310 | CO-14105 | 001 | 0000001 | 6 | T0409012 | 3126035912 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 4 | 2 | 1 | PART-X | 17-Oct-2026 | 9715310 | CO-14106 | 001 | 0000001 | 3 | T0409013 | 3126035913 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 5 | 2 | 2 | PART-X | 17-Oct-2026 | 9715310 | CO-14107 | 001 | 0000001 | 3 | T0409013 | 3126035913 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 6 | 3 | 1 | PART-X | 17-Oct-2026 | 9722D10 | CO-14104 | 001 | 0000001 | 6 | T0409013 | 3126035913 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |
| 7 | 4 | 1 | PART-X | 17-Oct-2026 | 9811110 | CO-14109 | 001 | 0000001 | 6 | T0409013 | 3126035913 | 0001 | 18-Oct-2026 | 1 | SD01 | (NULL) | (NULL) |

### E. Result: other tables changed in the same transaction

| Table | Key | Column | Before | After |
|---|---|---|---|---|
| TB_R_H0253_ORDER_CONTROL_PRE | CO-14104, CO-14105, CO-14106, CO-14107, CO-14109 (whole line in the ASN) | PO_MAPPED_FLAG | N | Y |
| TB_R_H0253_ORDER_CONTROL_PRE | CO-14110 (case 5, not sent) | PO_MAPPED_FLAG | N | N |
| TB_R_PRA_DAILY_ORDER_MAPPED | T0409012 / 3126035912 / 0001 / PART-X | MAPPED_QTY | 0 | 6 |
| TB_R_PRA_DAILY_ORDER_MAPPED | T0409013 / 3126035913 / 0001 / PART-X | MAPPED_QTY | 0 | 18 |

### F. Result on the screen: Case List (Draft)

| Item | Value |
|---|---|
| ASN No | ASN0003 (auto, assigned on submit) |
| Supplier · Plant | 50221 · 1 |
| Delivery Date · Rit · Route | 18-Oct-2026 · Rit 1 · SD01 |
| Delivery Qty | 24 pcs |
| Cases | 4 cases |
| Case 1 .. Case 4 | Case Number, Part Number, Customer Order Date, Qty (6 each); the expand button shows the PO No, Manifest No, Manifest Item and PO Qty (Case 1: T0409012; Cases 2-4: T0409013) |
| [Submit ASN] | Confirmation: Submit ASN? 4 cases (24 pcs) will be created into ASN0003, delivery 18-Oct-2026 · Rit 1. |

### G. Scenarios

| No | Scenario | Expected result |
|---|---|---|
| N1 | Create ASN with the unit PART-X 17-Oct ticked (cases 1-4) | Sections C to F: 4 cases, 5 rows in TB_R_INSTRUCTION, PO_MAPPED_FLAG Y on 5 lines, mapped qty added; Case List opens. |
| N2 | [Submit ASN] and [Yes, submit] | Submit ID handed to the submit process (5.7); ASN0003 and CASE_NO are written back to the 5 rows; only case 5 (CO-14110, Not Ready) stays in the delivery plan. |
| N3 | [Back] / [Cancel] on the Case List | The 5 rows are deleted from TB_R_INSTRUCTION, PO_MAPPED_FLAG back to N, MAPPED_QTY back to 0; the unit is listed again. |
| N4 | 19-Oct: split PO T0409014 released | Case 5 (CO-14110) is Ready → ASN0004; order date 18-Oct (3 destinations) → ASN0005. |
| E1 | The D/S team holds Thailand (CO-14104) after the supplier ticked the unit | MSG8; the whole create fails, nothing is inserted, the delivery plan is refreshed and all units are unticked. |
| E2 | The unit is no longer Ready when [Create ASN] is clicked | MSG7; nothing is inserted; the delivery plan is refreshed. |
| E3 | D/S team ticks PART-X (supplier 50221-1) and a unit of supplier 50330-2 | MSG9; nothing is inserted. |
| E4 | No ASN yet on 22-Oct: the supplier wants order date 18-Oct first | Not possible: per Part Number the oldest Customer Order Date first (15-Oct, then 16-Oct, 17-Oct …); later dates are disabled (Wait: dd-Mon first). |
| E5 | Database error during the insert | Roll back: nothing is kept; error message on the screen and Log FAILED. |

### H. Case selection on 18-Oct (supplier view, PART-X 17-Oct): one check box per supplier case; Content shown to the D/S team only

| Case | Qty | Remaining Qty (not assigned) | Content (D/S team only) | PO | CUT_FLAG | PO Status |
|---|---|---|---|---|---|---|
| Case 1 | 6 | 0 | VN 6 (CO-14105) | T0409012 6 | Y | Ready |
| Case 2 | 6 | 0 | VN 3 (CO-14106) + VN 3 (CO-14107) | T0409013 6 | Y | Ready |
| Case 3 | 6 | 0 | TH 6 (CO-14104) | T0409013 6 | Y | Ready |
| Case 4 | 6 | 0 | PH 6 (CO-14109) | T0409013 6 | Y | Ready |
| Case 5 | 6 | 6 | 982220 6 (CO-14110) | — | Y | Not Ready |

### I. Check box scenarios (simulation)

| No | User action | Ticked cases | Result |
|---|---|---|---|
| C1 | 18-Oct: tick case 1 | 1 | ASN 6 pcs. |
| C2 | 18-Oct: tick case 3 | 1-3 | Cases 1-2 are ticked too (the selection starts at case 1); ASN 18 pcs. |
| C3 | 18-Oct: tick the unit check box | 1-4 | All Ready cases; case 5 (Not Ready) is not ticked; ASN 24 pcs = ASN0003. |
| C4 | From 1-4, untick case 2 | 1 | Cases 2-4 are unticked; back to case 1. |
| C5 | Case 5 (no PO) | - | Disabled; tooltip message no. 2; Ready on 19-Oct with the split PO T0409014. |
| C6 | 19-Oct: tick case 1 of 18-Oct first | - | Disabled (Wait: 17-Oct first); after case 1 of 17-Oct is ticked the cases of 18-Oct can be ticked. |
| C7 | Cases without a cut in between (message no. 10) | - | Not in this data: every case of PART-X ends on a cut. When a case does not end on a cut, the next cases up to the cut are ticked together (MSG10). |
