# XD01 – Cross Dock Part Master Screen

> Generated from `deliverables/function_list_v2/specs/XD01_spec.json` (UISS `XD01_UISS_Screen_CrossDockPartMaster.xlsx`). Do not edit by hand: change the spec and run `python3 prepare_code/build_md.py`. Document names: GTOPAS / NSP (prototype: G-System / Supplier System).

| Phase | Project | Block | Function | Created | By | Type |
|---|---|---|---|---|---|---|
| DR | Crossdock Optimization | Screen | XD01 Cross Dock Part Master Screen | 18-Oct-26 | FID Rayhan | screen |

## Revision

| Rev | Author | Date | Reviewed by | Description |
|---|---|---|---|---|
| 0.1 | FID Rayhan | 18-Oct-26 |  | Initial Draft |

## 1. General

### Objective

- One screen with two tabs: Part List (part number level) and Mapping per Destination (part + calculation period + destination level).
- Part List tab: To register crossdock candidate parts (Part No, Min MAD, Pcs/Case, Max Case/Day, Effective Start Date).
- Part List tab: To search and display registered crossdock parts with their status and capacity.
- Part List tab: To change part data and part status (Candidate / Active / Inactive) of a registered part.
- Part List tab: To display the change history of a part.
- Part List tab: To export the Part List to Excel and upload part settings from Excel (Add and Edit).
- Part List tab: This sub-menu is opened only for users logged in with a Procurement account; users with a D/S account open the Mapping per Destination sub-menu instead.
- Mapping per Destination tab: To split the Max Case/Day of each Active part over destinations (Thailand, Philippines, Vietnam) for the ongoing calculation period.
- Mapping per Destination tab: To display the destination mapping per part and calculation period, including past periods (read only).
- Mapping per Destination tab: To start the interfaces of the cross dock master to GTOPAS (XD06) and AP POLE (XD07) for changed parts, and show the Sync Status of each part.
- Mapping per Destination tab: To export the mapping to Excel and upload the mapping of the ongoing period from Excel.
- Mapping per Destination tab: This sub-menu is opened only for users logged in with a D/S account; users with a Procurement account open the Part List sub-menu instead.

### Display order – Part List - Result List (Sort by = Newer to Older, default)

| Field | Order |
|---|---|
| Last Update (CHANGED_DT) | Descending |

### Display order – Part List - Result List (Sort by = Older to Newer)

| Field | Order |
|---|---|
| Last Update (CHANGED_DT) | Ascending |

### Display order – Part List - Result List (Sort by = Default)

| Field | Order |
|---|---|
| Part Number | Ascending |

### Display order – Part List - History Setting modal

| Field | Order |
|---|---|
| Event date and time | Descending |

### Display order – Mapping - Result List

| Field | Order |
|---|---|
| Part Number | Ascending (TBD) |

### Display order – Mapping - Destination Mapping panel

| Field | Order |
|---|---|
| Order in which destinations were added | - |

### Buttons

| Button | Function |
|---|---|
| Tab (Part List / Mapping per Destination) | Switch between the Part List tab and the Mapping per Destination tab. |
| Add Part | Open the "Add Part Candidate Crossdock" modal (Add Mode), ready to register a new part. |
| Upload Excel (Part List) | Open the "Upload Excel - part settings" modal (Upload Mode). |
| Export Excel (Part List) | Download the Part List as .xlsx: sheet "Part List" (active filter) and sheet "Upload" (base file for Edit uploads). |
| Run calculation (Part List) | Start the DAD Volume Calculation batch manually. Enabled only when the scheduled run and its 3 auto retries have failed. |
| Reset | Clear criteria and reset the screen to its initial value. |
| Search | To retrieve records according to the specified criteria. The criteria are applied only when [Search] is clicked (or Enter is pressed in a text box); Sort by is applied at once. |
| Part Number link / Edit | Change the screen into edit mode to modify the selected row ("Edit part data" modal). |
| History | Open the "History setting" modal of the selected part. |
| Prev / Next | Move to the previous / next page of the result list. |
| Save | Part List tab: Save the part data entered in the Add / Edit modal.; Mapping per Destination tab: Save the destination mapping of the part. |
| Cancel | Part List tab: Close the Add / Edit modal without saving.; Mapping per Destination tab: Leave edit mode and discard all changes of the panel. |
| Close | Part List tab: Close the History setting / Upload Excel modal (also the X icon of every modal).; Mapping per Destination tab: Close the Upload Excel modal without uploading. |
| Validate file | Save button of the upload: validate the uploaded file and save it (all-or-nothing), then show the success popup. |
| OK | Close the success popup. |
| Run calculation (Mapping) | Start process 2 (mapping destination) of the XD05 DAD Volume Calculation batch manually. Enabled only when the scheduled run and its 3 auto retries have failed. |
| Sync | Start XD06 (GTOPAS) and XD07 (AP POLE) for every Active part of the ongoing period, and every part that became Inactive, with Sync Status No Sync or Failed, whatever the filter shows; the parts become Waiting. The label shows the number of parts, e.g. Sync (9). |
| Upload Excel (Mapping) | Open the "Upload Excel - destination mapping" modal. Enabled only when the ongoing calculation period is selected. |
| Export Excel (Mapping) | Download the mapping as .xlsx: sheet "Mapping per Destination" (active filter) and sheet "Upload" (base file for the upload). |
| Expand (arrow) | Open / close the Destination Mapping panel of the part row. |
| Edit mapping | Change the Destination Mapping panel into edit mode (ongoing period only). |
| Split evenly | Divide Max Case/Day evenly over all destinations of the part. |
| Add destination | Add a new destination row (destination not selected, Case/Day 0). |
| Remove destination | Remove the destination row (trash icon). |

### Screen modes (E = enabled, D = disabled)

| Mode | Section | Description | Tab (Part List / Mapping per Destination) | Add Part | Upload Excel (Part List) | Export Excel (Part List) | Run calculation (Part List) | Reset | Search | Part Number link / Edit | History | Prev / Next | Save | Cancel | Close | Validate file | OK | Run calculation (Mapping) | Sync | Upload Excel (Mapping) | Export Excel (Mapping) | Expand (arrow) | Edit mapping | Split evenly | Add destination | Remove destination |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Part List - Initial Mode | Search Criteria | Part Number and Part Name blank, Status = All, Sort by = Newer to Older | E | E | E | E | D | E | E | E | E | E | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Initial Mode | Result List | All registered parts, 25 rows per page, page 1. Refer below 1) | E | E | E | E | D | E | E | E | E | E | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Search Result Mode | Result List | Parts matching all criteria (AND); page returns to 1 | E | E | E | E | D | E | E | E | E | E | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Search Result Mode | Empty State | No matching parts; table and paging hidden; [Reset filter] shown | E | E | E | E | D | E | E | D | D | D | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Add Mode (modal) | Part No not selected | Status locked to Candidate; Max Case/Day locked; Save disabled | E | D | D | D | D | D | D | D | D | D | D | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Add Mode (modal) | Part No selected, Pcs/Case blank | Part Name autofilled; Max Case/Day still locked; Save disabled | E | D | D | D | D | D | D | D | D | D | D | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Add Mode (modal) | All required items filled | Total Pcs/Day calculated; Save enabled | E | D | D | D | D | D | D | D | D | D | E | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Edit Mode (modal) | Saved status Candidate | Part No locked; Status, Effective Start Date, Min MAD, Pcs/Case, Max Case/Day editable | E | D | D | D | D | D | D | D | D | D | E | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Edit Mode (modal) | Saved status Active / Inactive | Same as 4.a but Effective Start Date locked (it can only change while the status is Candidate) | E | D | D | D | D | D | D | D | D | D | E | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Part List - History Mode (modal) | History setting | Change timeline of the selected part, read only | E | D | D | D | D | D | D | D | D | D | D | D | E | D | D | - | - | - | - | - | - | - | - | - |
| Part List - Upload Mode (modal) | Upload Excel | Template columns, rules, file area | E | D | D | D | D | D | D | D | D | D | D | D | E | E | D | - | - | - | - | - | - | - | - | - |
| Part List - Upload Mode (modal) | Success popup | "Saved successfully" after Save or Validate file | E | D | D | D | D | D | D | D | D | D | D | D | D | D | E | - | - | - | - | - | - | - | - | - |
| Mapping - Initial Mode | Search Criteria | Calculation period = ongoing period, Part Number blank, Sync Status = No Sync | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | D | D | D | D |
| Mapping - Initial Mode | Result List | Parts of the ongoing period with Sync Status No Sync. Refer below 1) | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | D | D | D | D |
| Mapping - Search Result Mode | Result List - ongoing period | Active parts matching all criteria | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | D | D | D | D |
| Mapping - Search Result Mode | Result List - past period / All periods | All parts of the period; Upload Excel disabled | E | - | - | - | - | E | E | - | - | D | D | D | D | D | D | D | E | D | E | E | D | D | D | D |
| Mapping - Search Result Mode | Empty State | No parts match the filters; table hidden | E | - | - | - | - | E | E | - | - | D | D | D | D | D | D | D | D | E | E | D | D | D | D | D |
| Mapping - Detail View Mode | Ongoing period | Panel read only; [Edit mapping] shown | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | E | D | D | D |
| Mapping - Detail View Mode | Past period | Panel read only; badge 'Past period - read only' instead of [Edit mapping] | E | - | - | - | - | E | E | - | - | D | D | D | D | D | D | D | E | D | E | E | D | D | D | D |
| Mapping - Edit Mapping Mode | Valid mapping | Destination and Case/Day editable; total <= Max Case/Day | E | - | - | - | - | E | E | - | - | E | E | E | D | D | D | E | E | E | E | E | D | E | E | E |
| Mapping - Edit Mapping Mode | Mapping cannot be saved | Total > Max Case/Day, no destination, or a row without destination; Save disabled | E | - | - | - | - | E | E | - | - | E | D | E | D | D | D | E | E | E | E | E | D | E | E | E |
| Mapping - Upload Mode (modal) | Upload Excel | Template columns, rules, file area | E | - | - | - | - | D | D | - | - | D | D | D | E | E | D | D | D | D | D | D | D | D | D | D |
| Mapping - Upload Mode (modal) | Success popup | 'Saved successfully' after Validate file | E | - | - | - | - | D | D | - | - | D | D | D | D | D | E | D | D | D | D | D | D | D | D | D |

- 1) Prev is disabled on the first page and Next on the last page.
- 2) A user logged in with a read-only account sees [View] instead of [Edit] and cannot use Add Part / Upload Excel / Save. TBD: which accounts are read-only is not defined yet.
- 3) Run calculation is shown as D (disabled) by default; it is enabled only when the scheduled DAD Volume Calculation has failed 3 times (auto retry).
- 4) Sync is enabled only when at least one Active part of the ongoing period, or a part that became Inactive, is No Sync or Failed (not limited to the listed rows).
- 5) Split evenly is shown only in edit mode when the part has more than one destination row.
- 7) Prev is disabled on the first page and Next on the last page.
- 8) Run calculation is enabled only when the scheduled XD05 DAD Volume Calculation (process 2) has failed 3 times (auto retry); otherwise disabled with message no. 30 as tooltip.
- 6) A user logged in with a read-only account cannot use Edit mapping, Sync or Upload Excel. TBD: which accounts are read-only is not defined yet.
- 9) '-' = the button is not on the tab of the mode.

## 2. Screen flow

### Screen Flow for Cross Dock Part Master (tabs)

```mermaid
flowchart LR
  pl[["Part List tab"]]
  mp[["Mapping per Destination tab"]]
  pl -->|Tab| mp
  mp -->|Tab| pl
```

### Screen Flow for Part List

```mermaid
flowchart LR
  list[["Part List"]]
  add[["Add Part modal"]]
  edit[["Edit part data modal"]]
  hist[["History setting modal"]]
  up[["Upload Excel modal"]]
  ok>"Saved successfully popup"]
  xls[/"Excel file (.xlsx)"/]
  list -->|Add Part| add
  list -->|Part Number / Edit| edit
  list -->|History icon| hist
  list -->|Upload Excel| up
  list -->|Export Excel| xls
  add -->|Save| ok
  edit -->|Save| ok
  up -->|Validate file| ok
  ok -->|OK| list
```
- Cancel / Close / X on any modal returns to the Part List without saving.

### Screen Flow for Save (Add / Edit part data)

```mermaid
flowchart TB
  s(["START"])
  e1>"Enter / change part data in the Add Part or Edit part data modal"]
  d1{"Part data valid?"}
  m1>"Save disabled, show tooltip / message (no. 5 / 6 / 7 / 15; Edit: 10 / 14)"]
  m2>"Save enabled"]
  e2>"On Click of Save button"]
  d2{"Registered / changed by another user meanwhile?"}
  m3>"Show message no. 3 (Add) / 4 (Edit), stop"]
  p1["Insert (Add) / update (Edit) part, Sync Status = No Sync"]
  db[("TB_M_PART_CANDIDATE")]
  p2["Insert change history"]
  db2[("TB_H_PART_CANDIDATE")]
  m4>"Close modal, part on top, message no. 9"]
  x(["END"])
  s --> e1
  e1 --> d1
  d1 -->|No| m1
  m1 -->|correct the data| e1
  d1 -->|Yes| m2
  m2 --> e2
  e2 --> d2
  d2 -->|Yes| m3
  d2 -->|No| p1
  p1 -.-> db
  p1 --> p2
  p2 -.-> db2
  p2 --> m4
  m4 --> x
```
- Part data valid = Add: Part No selected, Min MAD filled (whole number, 0 or more), Pcs/Case > 0 and Max Case/Day > 0 (otherwise the tooltip shows message no. 5, 15, 6 or 7 for the first missing item). Edit: the same items, Effective Start Date not before today while the part is Candidate (message no. 10), and Max Case/Day not below the Case/Day already mapped in the ongoing period (message no. 14).
- The check runs on every change in the modal, so [Save] is already disabled before it can be clicked (see Operation Description 5.4 and 5.5).

### Screen Flow for Mapping per Destination

```mermaid
flowchart LR
  list[["Mapping per Destination list"]]
  view[["Destination Mapping panel (view)"]]
  edit[["Edit mapping mode"]]
  up[["Upload Excel modal"]]
  ok>"Saved successfully popup"]
  xls[/"Excel file (.xlsx)"/]
  tgt[("XD06 -> GTOPAS / XD07 -> AP POLE")]
  list -->|Expand| view
  view -->|Edit mapping| edit
  edit -->|Save / Cancel| view
  list -->|Upload Excel| up
  up -->|Validate file| ok
  ok -->|OK| list
  list -->|Export Excel| xls
  list -->|Sync| tgt
```
- Close on the Upload Excel modal returns to the list without uploading. Closing the panel while editing discards the changes.

### Screen Flow for Save (Edit mapping)

```mermaid
flowchart TB
  s(["START"])
  e1>"Change destination / Case/Day in edit mode"]
  d1{"Mapping valid?"}
  m1>"Save disabled, show banner (message no. 20 / 21)"]
  m2>"Save enabled"]
  e2>"On Click of Save button"]
  p1["Update / insert / delete mapping per destination (ongoing period)"]
  db[("TB_M_PART_CANDIDATE_DEST")]
  p2["Sync Status = No Sync"]
  db2[("TB_M_PART_CANDIDATE")]
  x(["Back to view mode"])
  s --> e1
  e1 --> d1
  d1 -->|No| m1
  m1 -->|correct the mapping| e1
  d1 -->|Yes| m2
  m2 --> e2
  e2 --> p1
  p1 -.-> db
  p1 --> p2
  p2 -.-> db2
  p2 --> x
```
- Mapping valid = all of: (1) total Case/Day of the part <= Max Case/Day (a lower total is allowed, shown as '{n} case/day left'); (2) the part has at least one destination row; (3) every row has a destination selected.
- The check runs on every change in edit mode, so [Save] is already disabled before it can be clicked (see Operation Description 5.15 Save rules).

## 3. Screen layout

### 1. Initial Mode - Part List (Status = All, Sort by = Newer to Older)

![1. Initial Mode - Part List (Status = All, Sort by = Newer to Older)](../../deliverables/uiss_screens/part_list/c_01_initial.png)

### 2. Search Result Mode - Status = Candidate

![2. Search Result Mode - Status = Candidate](../../deliverables/uiss_screens/part_list/c_02_filter_candidate.png)

### 3. Search Result Mode - no matching parts (empty state)

![3. Search Result Mode - no matching parts (empty state)](../../deliverables/uiss_screens/part_list/c_03_no_result.png)

### 4. Add Mode - empty form (Save disabled)

![4. Add Mode - empty form (Save disabled)](../../deliverables/uiss_screens/part_list/c_04_add_empty.png)

### 5. Add Mode - Part No list (only parts not yet registered)

![5. Add Mode - Part No list (only parts not yet registered)](../../deliverables/uiss_screens/part_list/c_05_add_partno_list.png)

### 6. Add Mode - Part No not found

![6. Add Mode - Part No not found](../../deliverables/uiss_screens/part_list/c_06_add_partno_notfound.png)

### 7. Add Mode - all required items filled (Save enabled)

![7. Add Mode - all required items filled (Save enabled)](../../deliverables/uiss_screens/part_list/c_07_add_filled.png)

### 8. Saved successfully popup after Save

![8. Saved successfully popup after Save](../../deliverables/uiss_screens/part_list/c_08_save_success.png)

### 9. Edit Mode - Candidate part (Effective Start Date editable)

![9. Edit Mode - Candidate part (Effective Start Date editable)](../../deliverables/uiss_screens/part_list/c_09_edit_candidate.png)

### 10. Edit Mode - Active part (Effective Start Date locked)

![10. Edit Mode - Active part (Effective Start Date locked)](../../deliverables/uiss_screens/part_list/c_10_edit_active.png)

### 11. Edit Mode - Max Case/Day below the mapped total (message no. 14, Save disabled)

![11. Edit Mode - Max Case/Day below the mapped total (message no. 14, Save disabled)](../../deliverables/uiss_screens/part_list/c_14_edit_below_mapped.png)

### 12. History Mode - History setting

![12. History Mode - History setting](../../deliverables/uiss_screens/part_list/c_11_history.png)

### 13. Upload Mode - Upload Excel modal

![13. Upload Mode - Upload Excel modal](../../deliverables/uiss_screens/part_list/c_12_upload.png)

### 14. Upload Mode - Saved successfully popup after Validate file

![14. Upload Mode - Saved successfully popup after Validate file](../../deliverables/uiss_screens/part_list/c_13_upload_success.png)

### 15. Initial Mode - ongoing period, Sync Status = No Sync

![15. Initial Mode - ongoing period, Sync Status = No Sync](../../deliverables/uiss_screens/mapping/c_01_default.png)

### 16. Search Result Mode - Sync Status = All

![16. Search Result Mode - Sync Status = All](../../deliverables/uiss_screens/mapping/c_02_sync_all.png)

### 17. Search Result Mode - past period (Upload Excel disabled)

![17. Search Result Mode - past period (Upload Excel disabled)](../../deliverables/uiss_screens/mapping/c_03_past_period.png)

### 18. Search Result Mode - no parts match the filters

![18. Search Result Mode - no parts match the filters](../../deliverables/uiss_screens/mapping/c_04_no_result.png)

### 19. Detail View Mode - ongoing period

![19. Detail View Mode - ongoing period](../../deliverables/uiss_screens/mapping/c_05_details_view.png)

### 20. Detail View Mode - past period (read only)

![20. Detail View Mode - past period (read only)](../../deliverables/uiss_screens/mapping/c_06_details_past.png)

### 21. Edit Mapping Mode

![21. Edit Mapping Mode](../../deliverables/uiss_screens/mapping/c_07_edit_mode.png)

### 22. Edit Mapping Mode - allocation above Max Case/Day (Save disabled)

![22. Edit Mapping Mode - allocation above Max Case/Day (Save disabled)](../../deliverables/uiss_screens/mapping/c_08_over_allocation.png)

### 23. Edit Mapping Mode - row without destination (Save disabled)

![23. Edit Mapping Mode - row without destination (Save disabled)](../../deliverables/uiss_screens/mapping/c_09_missing_destination.png)

### 24. Detail View Mode - part without destination

![24. Detail View Mode - part without destination](../../deliverables/uiss_screens/mapping/c_10_no_destination.png)

### 25. Edit Mapping Mode - after Split evenly

![25. Edit Mapping Mode - after Split evenly](../../deliverables/uiss_screens/mapping/c_11_split_evenly.png)

### 26. Before Sync - Sync (9): 4 No Sync + 5 Failed Active parts of the ongoing period

![26. Before Sync - Sync (9): 4 No Sync + 5 Failed Active parts of the ongoing period](../../deliverables/uiss_screens/mapping/c_12_before_sync.png)

### 27. After Sync - the 9 parts are Waiting for XD06 / XD07 (viewed with Sync Status = All)

![27. After Sync - the 9 parts are Waiting for XD06 / XD07 (viewed with Sync Status = All)](../../deliverables/uiss_screens/mapping/c_13_after_sync.png)

### 28. Upload Mode - Upload Excel modal

![28. Upload Mode - Upload Excel modal](../../deliverables/uiss_screens/mapping/c_14_upload.png)

### 29. Upload Mode - Saved successfully popup after Validate file

![29. Upload Mode - Saved successfully popup after Validate file](../../deliverables/uiss_screens/mapping/c_15_upload_success.png)

### 30. Run calculation - Calculation completed popup

![30. Run calculation - Calculation completed popup](../../deliverables/uiss_screens/mapping/c_16_calc_success.png)

## 4. Item description

| No | Item | Source | Field | Type | Len | I/O | Control | Justified | Initial | Req | Format | Validation | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **<Tab Bar>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1 | Tab (Part List / Mapping per Destination) |  |  |  |  | I | Tab | Left | Part List |  |  |  | Part List tab (default) / Mapping per Destination tab. |
| **<Part List - Header Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Add Part |  |  |  |  | I | Button | Center |  |  |  |  | Opens the Add Part modal. Refer Operation Description 5.4. |
| 3 | Upload Excel (Part List) |  |  |  |  | I | Button | Center |  |  |  |  | Opens the Upload Excel modal. Refer Operation Description 5.7. |
| 4 | Export Excel (Part List) |  |  |  |  | I | Button | Center |  |  |  |  | Downloads Crossdock_Part_List_YYYYMMDD.xlsx. Refer Operation Description 5.8. |
| **<Part List - Search Criteria Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Part Number | Key-in |  | Varchar | TBD | I | Text box with suggestion list | Left | Blank | N | X..TBD..X | Contains, case-insensitive | Suggestions = PART_NO of registered parts (TB_M_PART_CANDIDATE). Placeholder 'e.g. PART-B'. Combined with the other criteria by AND. |
| 6 | Part Name | Key-in |  | Varchar | TBD | I | Text box | Left | Blank | N | X..TBD..X | Contains, case-insensitive | Placeholder 'Part name'. Combined with the other criteria by AND. |
| 7 | Status | Key-in |  | Varchar |  | I | Combo Box | Left | All | N |  |  | Options: All / Candidate / Active / Inactive. Filters PART_STATUS. |
| 8 | Sort by | Key-in |  | Varchar |  | I | Combo Box | Left | Newer to Older | N |  |  | Options: Default (Part Number A-Z) / Newer to Older / Older to Newer (by Last Update). |
| 9 | Reset |  |  |  |  | I | Button | Center |  |  |  |  | Returns every criterion to its initial value. |
| 10 | Search |  |  |  |  | I | Button | Center |  |  |  |  | Applies the criteria to the result list. Typing or selecting a criterion alone does not change the list; Enter in a text box = [Search]. |
| **<Part List - Result List Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 11 | Registered parts counter |  |  | Varchar |  | O | Label | Left |  |  | N parts |  | N = number of filtered rows (all pages). |
| 12 | Last DAD calculation |  |  | Datetime |  | O | Label | Left |  |  | DD-Mon-YYYY HH:MM |  | Date-time of the last successful run of the DAD Volume Calculation batch (one date per batch run, all-or-nothing). |
| 13 | Failed badge |  |  | Varchar |  | O | Label | Left |  |  |  |  | 'Scheduled run failed 3x'; shown when the scheduled run and its 3 auto retries have failed. |
| 14 | Run calculation (Part List) |  |  |  |  | I | Button | Center |  |  |  |  | Manual trigger of the DAD Volume Calculation batch. Enabled only when the scheduled run has failed 3 times; otherwise disabled with message no. 17 as tooltip. Refer Operation Description 5.9. |
| 15 | Part Number | TB_M_PART_CANDIDATE | PART_NO | Varchar | TBD | O | Hyperlink | Left |  |  | X..TBD..X |  | Click opens the Edit part data modal (same as [Edit]). |
| 16 | Part Name | TB_M_PART_CANDIDATE | PART_NAME | Varchar | TBD | O | Label | Left |  |  | X..TBD..X |  | Truncated with '...' when long; full name in tooltip. |
| 17 | Min MAD | TB_M_PART_CANDIDATE | MIN_MAD | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  | Minimum MAD of the part, entered by the user. Reference value compared with the MAD result of the calculation. |
| 18 | Pcs/Case | TB_M_PART_CANDIDATE | PCS_CASE | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  |  |
| 19 | Max Case/Day | TB_M_PART_CANDIDATE | MAX_CASE_DAY | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  |  |
| 20 | Total Pcs/Day | TB_M_PART_CANDIDATE | TOTAL_PCS_DAY | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  | = Pcs/Case x Max Case/Day. |
| 21 | Status | TB_M_PART_CANDIDATE | PART_STATUS | Varchar | TBD | O | Chip | Left |  |  |  |  | Candidate (blue) / Active (green) / Inactive (grey). |
| 22 | Last Update | TB_M_PART_CANDIDATE | CHANGED_DT, CHANGED_BY | Datetime |  | O | Label (2 lines) | Left |  |  | DD-Mon-YYYY HH:MI |  | Line 1 date-time, line 2 user name of the last change. |
| 23 | Edit |  |  |  |  | I | Button | Center |  |  |  |  | Opens the Edit part data modal of the row. Shown as [View] for a read-only account (TBD: read-only accounts not defined). |
| 24 | History (clock icon) |  |  |  |  | I | Button | Center |  |  |  |  | Opens the History setting modal of the row. |
| **<Part List - Footer Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 25 | Rows per page | Key-in |  | Number |  | I | Combo Box | Left | 25 | N |  |  | Options 25 / 50 / 100. Change returns to page 1. |
| 26 | Paging information |  |  | Varchar |  | O | Label | Right |  |  | a-b of N parts · page x/y |  |  |
| 27 | Prev / Next |  |  |  |  | I | Button | Center |  |  |  |  | Previous / next page. Refer Screen Mode remark 1). |
| **<Part List - Empty State Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 28 | Empty state message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 1 (filter result empty) or no. 2 (no part registered). |
| 29 | Reset filter |  |  |  |  | I | Button | Center |  |  |  |  | Same as [Reset]. Shown with message no. 1. |
| 30 | Upload Excel / Add one part |  |  |  |  | I | Button | Center |  |  |  |  | Shown with message no. 2; same as header [Upload Excel] / [Add Part]. |
| **<Part List - Add Part / Edit Part Data Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 31 | Modal title |  |  | Varchar |  | O | Label | Left | Add: 'Add Part Candidate Crossdock'; Edit: 'Edit part data' |  |  |  |  |
| 32 | Step indicator |  |  |  |  | O | Stepper | Left | Step 1 active |  |  |  | Step 1 Part Candidate (Part No), step 2 Pcs/Case & Max Case/Day, step 3 Total Pcs/Day; a step gets a check when its items are filled. |
| 33 | Status | TB_M_PART_CANDIDATE | PART_STATUS | Varchar | TBD | I/O | Combo Box | Left | Candidate | Y |  | Add: always Candidate. Edit: Candidate / Active / Inactive | Add: locked to Candidate (tooltip 'New parts are automatically Candidate'). Edit: Candidate / Active / Inactive. |
| 34 | Part No | TB_M_PART_MASTER (Add) / TB_M_PART_CANDIDATE (Edit) | PART_NO | Varchar | TBD | I/O | Combo Box with search | Left | Blank | Y | X..TBD..X | Must exist in TB_M_PART_MASTER and not yet be registered (no duplicate Part No) | Add: lists parts of TB_M_PART_MASTER not yet registered (Part No + name, contains search, arrow keys / Enter / Esc). Edit: locked. |
| 35 | Part Name | TB_M_PART_MASTER | PART_NAME (TBD) | Varchar | TBD | O | Text box (disabled) | Left | Blank |  | X..TBD..X |  | Autofilled from the selected Part No. |
| 36 | Effective Start Date | TB_M_PART_CANDIDATE | EFFECTIVE_START_DATE | Date |  | I | Date picker | Left | Add: System date + 1 day | N (TBD: mandatory or not) | DD-Mon-YYYY | Today or later; editable only while the saved status is Candidate | Editable in Add, and in Edit only while the saved status is Candidate; otherwise locked with tooltip 'Can only be changed while the status is still Candidate'. |
| 37 | Min MAD | TB_M_PART_CANDIDATE | MIN_MAD | Number | TBD | I | Text box | Right | Blank | Y | ZZ,ZZ9 | Mandatory; whole number, 0 or more | Minimum MAD of the part, entered by the user. Reference value compared with the MAD result of the calculation. Mandatory on Add and Edit; tooltip of disabled [Save] = message no. 15. |
| 38 | Pcs/Case | TB_M_PART_CANDIDATE | PCS_CASE | Number | TBD | I | Text box | Right | Blank | Y | ZZ,ZZ9 | Whole number > 0 |  |
| 39 | Max Case/Day | TB_M_PART_CANDIDATE | MAX_CASE_DAY | Number | TBD | I | Text box | Right | Blank | Y | ZZ,ZZ9 | Whole number > 0 | Locked until Pcs/Case is filled (tooltip 'Enter Pcs/Case first'). Edit: can not be less than the total Case/Day already mapped in the ongoing period (TB_M_PART_CANDIDATE_DEST); otherwise the field is marked red, message no. 14 is shown and [Save] is disabled. |
| 40 | Mapped Case/Day (current period) | TB_M_PART_CANDIDATE_DEST | CASE_DAY | Number | TBD | O | Label | Left |  |  | ZZ,ZZ9 |  | Edit mode, Active parts only (Candidate / Inactive parts have no mapping). Total Case/Day of all destinations of the part in the ongoing period (' · no destination yet' when none); red when Max Case/Day is below it. Shows the lowest allowed Max Case/Day before Save. |
| 41 | Total Pcs/Day |  |  | Number |  | O | Label | Right | '-' |  | ZZ,ZZ9 |  | = Pcs/Case x Max Case/Day, recalculated on every change. |
| 42 | Cancel |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal without saving. |
| 43 | Save |  |  |  |  | I | Button | Center |  |  |  |  | Enabled only when Part No, Min MAD, Pcs/Case > 0 and Max Case/Day > 0 are filled and, in Edit, Max Case/Day is not below the mapped total. Refer Operation Description 5.4 / 5.5. |
| 44 | Close (X) |  |  |  |  | I | Button | Center |  |  |  |  | Same as [Cancel]. |
| **<Part List - History Setting Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 45 | Part identity | TB_M_PART_CANDIDATE | PART_NO, PART_NAME | Varchar |  | O | Label | Left |  |  |  |  | Part No · Part Name of the selected row. |
| 46 | Event title | TB_H_PART_CANDIDATE | TBD | Varchar |  | O | Timeline | Left |  |  |  |  | e.g. 'Part registered', 'Status changed'. Latest event marked with a blue dot. |
| 47 | Event date-time | TB_H_PART_CANDIDATE | TBD | Datetime |  | O | Label | Right |  |  | DD-Mon-YYYY HH:MI |  |  |
| 48 | Changed field (old → new) | TB_H_PART_CANDIDATE | TBD | Varchar |  | O | Label | Left |  |  |  |  | Field name, old value struck through, new value. |
| 49 | User | TB_H_PART_CANDIDATE | TBD | Varchar |  | O | Label | Right |  |  |  |  | User who made the change. |
| 50 | Close |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal. |
| **<Part List - Upload Excel Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 51 | Template columns |  |  | Varchar |  | O | Label (chips) | Left |  |  |  |  | part_no, min_mad, pcs_case, max_case_day, status, upload, effective_start_date (same order as sheet 'Upload' of Export Excel). |
| 52 | Rules per upload value and status |  |  | Varchar |  | O | Label | Left |  |  |  |  | Add / Edit / Status rules; Candidate status cannot be changed by upload, Active <-> Inactive allowed, nothing can become Candidate. |
| 53 | Upload file | Key-in |  | File |  | I | Drag-and-drop area + [Choose file] | Center | Blank | Y | .xlsx | Max 5 MB, max 5,000 rows | File checks and row validation are done by the batch (UISS-Batch XD02 Cross Dock Part Master Upload). |
| 54 | Download template .xlsx |  |  |  |  | I | Button | Center |  |  |  |  | Downloads the empty upload template. TBD: template file location. |
| 55 | Close |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal without uploading. |
| 56 | Validate file |  |  |  |  | I | Button | Center |  |  |  |  | Save button of the upload. Refer Operation Description 5.7. |
| **<Part List - Saved Successfully Popup>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 57 | Success message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 9 (Add / Edit) or no. 11 (upload). |
| 58 | OK |  |  |  |  | I | Button | Center |  |  |  |  | Closes the popup. |
| **<Mapping - Search Criteria Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 59 | Calculation period | Key-in |  | Varchar |  | I | Combo Box | Left | Ongoing period, e.g. 'Sep 2026 (ongoing)' | N | Mon YYYY |  | Options: All periods / every calculation period; the ongoing one is marked '(ongoing)'. The label shows (ongoing) / (past) / (all). Calculation periods are created by the calculation batch; the latest period created is the ongoing period and earlier ones become past. A new period starts empty: the mapping of the previous period is not copied. Every Active part is listed with its Max Case/Day from Part List (the quota) but no destination yet (Total Case/Day 0, 0%), until the D/S user assigns it by Edit mapping or Upload Excel. |
| 60 | Part Number | Key-in |  | Varchar | TBD | I | Text box with suggestion list | Left | Blank | N | X..TBD..X | Contains, case-insensitive | Suggestions = registered Part Numbers. Placeholder 'e.g. PART-B'. Combined with the other criteria by AND. |
| 61 | Sync Status | Key-in |  | Varchar |  | I | Combo Box | Left | No Sync | N |  |  | Options: All / No Sync / Waiting / Success / Failed. |
| 62 | Reset |  |  |  |  | I | Button | Center |  |  |  |  | Returns every criterion to its initial value (Calculation period = ongoing, Sync Status = No Sync). |
| 63 | Search |  |  |  |  | I | Button | Center |  |  |  |  | Applies the criteria to the result list. Typing or selecting a criterion alone does not change the list; Enter in a text box = [Search]. |
| **<Mapping - Result List Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 64 | Section title |  |  | Varchar |  | O | Label | Left | 'Destination mapping per part' |  |  |  |  |
| 65 | Last mapping calculation |  |  | Datetime |  | O | Label | Left |  |  | DD-Mon-YYYY HH:MM |  | Date-time of the last successful run of process 2 (mapping destination) of the XD05 DAD Volume Calculation batch (one date per batch run). |
| 66 | Failed badge |  |  | Varchar |  | O | Label | Left |  |  |  |  | 'Scheduled run failed 3x'; shown when the scheduled run and its 3 auto retries have failed. |
| 67 | Run calculation (Mapping) |  |  |  |  | I | Button | Center |  |  |  |  | Manual trigger of process 2 (mapping destination) of the XD05 DAD Volume Calculation batch. Refer Operation Description 5.19 and Screen Mode remark 8). |
| 68 | Sync (n) |  |  |  |  | I | Button | Center |  |  |  |  | n = Active parts of the ongoing period and parts that became Inactive, with Sync Status No Sync or Failed, whatever the filter. Disabled when n = 0. Refer Operation Description 5.16. |
| 69 | Upload Excel (Mapping) |  |  |  |  | I | Button | Center |  |  |  |  | Disabled for a past period or All periods (tooltip message no. 23). Refer Operation Description 5.17. |
| 70 | Export Excel (Mapping) |  |  |  |  | I | Button | Center |  |  |  |  | Refer Operation Description 5.18. |
| 71 | Period | TB_M_PART_CANDIDATE_DEST | PERIOD | Char | 6 | O | Label | Left |  |  | Mon YYYY |  | Calculation period of the row. Stored as YYYYMM (e.g. 202609), displayed as Mon YYYY. |
| 72 | Expand (arrow) |  |  |  |  | I | Button | Center |  |  |  |  | Opens / closes the Destination Mapping panel of the row. |
| 73 | Part Number | TB_M_PART_CANDIDATE | PART_NO | Varchar | TBD | O | Label | Left |  |  | X..TBD..X |  |  |
| 74 | Part Name | TB_M_PART_CANDIDATE | PART_NAME | Varchar | TBD | O | Label | Left |  |  | X..TBD..X |  |  |
| 75 | Pcs/Case | TB_M_PART_CANDIDATE | PCS_CASE | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  |  |
| 76 | Total Case/Day | TB_M_PART_CANDIDATE_DEST | SUM(CASE_DAY) | Number |  | O | Label | Right |  |  | ZZ,ZZ9 |  | Sum of Case/Day of all destinations of the part and period. |
| 77 | Pcs/Day |  |  | Number |  | O | Label | Right |  |  | ZZ,ZZ9 |  | = Pcs/Case x Total Case/Day. |
| 78 | Percentage |  |  | Number |  | O | Label | Right |  |  | ZZ9% |  | = Total Case/Day / Max Case/Day (MAX_CASE_DAY). Never above 100%: Save, upload and the Max Case/Day edit in Part List are blocked above the limit. |
| 79 | Sync Status | TB_M_PART_CANDIDATE | SYNC_STATUS | Char | 1 | O | Chip | Left |  |  |  |  | 0 = No Sync (grey), 3 = Waiting (amber), 1 = Success (green), 2 = Failed (red). The Failed chip shows SYNC_MESSAGE as tooltip (message no. 28). |
| **<Mapping - Footer Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 80 | Rows per page | Key-in |  | Number |  | I | Combo Box | Left | 25 | N |  |  | Options 25 / 50 / 100. Change returns to page 1. |
| 81 | Paging information |  |  | Varchar |  | O | Label | Right |  |  |  |  | '{from}-{to} of {n} parts · page {p}/{total}'. |
| 82 | Prev / Next |  |  |  |  | I | Button | Center |  |  |  |  | Previous / next page. Refer Screen Mode remark 7). |
| **<Mapping - Empty State Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 83 | Empty state message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 18. |
| **<Mapping - Destination Mapping Panel>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 84 | Allocation chip |  |  | Varchar |  | O | Chip | Left |  |  | {total} / {Max Case/Day} case/day used |  | Red when the total is above Max Case/Day, grey when below, green when equal. |
| 85 | Allocation note |  |  | Varchar |  | O | Label | Left |  |  |  |  | 'no destination yet' / '{n} case/day over' / '{n} case/day left' / 'capacity fully allocated'. |
| 86 | Past period badge |  |  | Varchar |  | O | Badge | Left |  |  |  |  | Display message no. 22; shown instead of [Edit mapping] for a period that is not ongoing. |
| 87 | Split evenly |  |  |  |  | I | Button | Center |  |  |  |  | Refer Operation Description 5.15. |
| 88 | Edit mapping |  |  |  |  | I | Button | Center |  |  |  |  | Shown only for the ongoing period. |
| 89 | Cancel |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode; discards the changes. |
| 90 | Save |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode. Disabled while the mapping cannot be saved (Operation Description 5.15). |
| 91 | Destination (CD) | TB_M_PART_CANDIDATE_DEST | DEST_CODE | Varchar | TBD | I/O | Combo Box | Left | New row: 'Select destination' | Y | XXXXXXX - X..X | Once per part | List = DESTINATION_CD - DESTINATION_NAME of TB_M_H0125_DESTINATION (Destination Master) (e.g. 9722D10 - Thailand, 9811110 - Philippines, 9715310 - Vietnam). Destinations already used by another row of the same part are hidden. |
| 92 | Case/Day | TB_M_PART_CANDIDATE_DEST | CASE_DAY | Number | TBD | I/O | Text box | Right | New row: 0 | Y | ZZ,ZZ9 | Whole number (TBD: upper limit) | Editable in edit mode only. |
| 93 | Pcs/Day |  |  | Number |  | O | Label | Right |  |  | ZZ,ZZ9 |  | = Pcs/Case x Case/Day of the destination. |
| 94 | Percentage |  |  | Number |  | O | Label | Right |  |  | ZZ9% |  | = Case/Day of the destination / total Case/Day of the part. |
| 95 | Remove destination (trash icon) |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode on every row. |
| 96 | Add destination |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode, with the hint 'New row - pick a destination from the destination master in the Destination (CD) column.' |
| 97 | No destination message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 19; shown when the part has no destination. |
| 98 | Validation banner |  |  | Varchar |  | O | Banner | Left |  |  |  |  | Display message no. 20 (over allocation) or no. 4 (row without destination). |
| **<Mapping - Upload Excel Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 99 | Template columns |  |  | Varchar |  | O | Label (chips) | Left |  |  |  |  | part_no, dest_code, case_day, upload, total_case_day (same order as sheet 'Upload' of Export Excel). |
| 100 | Upload rules |  |  | Varchar |  | O | Label | Left |  |  |  |  | Rows / Replace / Limits / Base rules. Refer Operation Description 5.17. |
| 101 | Upload file | Key-in |  | File |  | I | Drag-and-drop area + [Choose file] | Center | Blank | Y | .xlsx | Max 5 MB, max 5,000 rows | File checks and row validation are done by the batch (UISS-Batch XD03 Part and Destination Mapping Upload). |
| 102 | Download template .xlsx |  |  |  |  | I | Button | Center |  |  |  |  | Downloads the empty upload template. TBD: template file location. |
| 103 | Close |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal without uploading. |
| 104 | Validate file |  |  |  |  | I | Button | Center |  |  |  |  | Save button of the upload. Refer Operation Description 5.17. |
| **<Mapping - Saved Successfully Popup>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 105 | Success message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 24. |
| 106 | OK |  |  |  |  | I | Button | Center |  |  |  |  | Closes the popup. |

## 5. Data edit mapping

#### 1. Insert TB_M_PART_CANDIDATE – Add Part modal - [Save]
- Source: Key-in from screen

| Source field | Destination field | Description |
|---|---|---|
| Part No | PART_NO |  |
| Part Name | PART_NAME | From TB_M_PART_MASTER by PART_NO |
| Min MAD | MIN_MAD | Mandatory; entered by the user |
| Pcs/Case | PCS_CASE |  |
| Max Case/Day | MAX_CASE_DAY |  |
|  | TOTAL_PCS_DAY | PCS_CASE x MAX_CASE_DAY |
| Effective Start Date | EFFECTIVE_START_DATE |  |
|  | PART_STATUS | 'Candidate' (every new part) |
|  | SYNC_STATUS | '0' (No Sync) |
|  | SYNC_DT | NULL (written by XD06 / XD07) |
|  | SYNC_MESSAGE | NULL (written by XD06 / XD07) |
|  | LAST_SOURCE | 'SCREEN' |
|  | LAST_UPLOAD_ID | NULL |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date-time |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 2. Update TB_M_PART_CANDIDATE – Edit part data - [Save]
- Source: Key-in from screen
- Destination keys: PART_NO = Part No of the edited row

| Source field | Destination field | Description |
|---|---|---|
| Status | PART_STATUS |  |
| Min MAD | MIN_MAD | Mandatory; entered by the user |
| Pcs/Case | PCS_CASE |  |
| Max Case/Day | MAX_CASE_DAY |  |
|  | TOTAL_PCS_DAY | PCS_CASE x MAX_CASE_DAY |
| Effective Start Date | EFFECTIVE_START_DATE | Only while saved status is Candidate |
|  | SYNC_STATUS | '0' (No Sync) on every Save |
|  | LAST_SOURCE | 'SCREEN' |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 3. Insert TB_H_PART_CANDIDATE – Add / Edit - [Save]
- Source: TB_M_PART_CANDIDATE (keys: PART_NO = Saved part)

| Source field | Destination field | Description |
|---|---|---|
|  | HIST_ID | Auto (identity) |
|  | PART_NO | Part of the event |
|  | PERIOD | NULL (Part List has no period) |
|  | EVENT_TYPE | 'ADD' (Add Part) / 'EDIT' (Edit part data) |
|  | SOURCE | 'SCREEN' |
|  | UPLOAD_ID | NULL |
|  | DEST_CODE | NULL |
|  | FIELD_NAME | Changed field, e.g. PCS_CASE, MAX_CASE_DAY, PART_STATUS |
|  | OLD_VALUE | Value before Save (NULL for ADD) |
|  | NEW_VALUE | Value after Save |
|  | REMARK | NULL |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date-time |

#### 4. Update TB_M_PART_CANDIDATE_DEST – Edit mapping - [Save] - Case/Day changed
- Source: Key-in from screen
- Destination keys: PART_NO = Edited part, PERIOD = Ongoing period, DEST_CODE = In both, Case/Day differs

| Source field | Destination field | Description |
|---|---|---|
| Case/Day | CASE_DAY |  |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date and time |
|  | CREATED_BY | Not changed |
|  | CREATED_DT | Not changed |

#### 5. Insert TB_M_PART_CANDIDATE_DEST – Edit mapping - [Save] - new destination
- Source: Key-in from screen

| Source field | Destination field | Description |
|---|---|---|
| Part Number | PART_NO |  |
|  | PERIOD | Ongoing calculation period |
| Destination (CD) | DEST_CODE | Destination not yet in the table for the part and period |
| Case/Day | CASE_DAY |  |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date and time |
|  | CHANGED_BY | Same as CREATED_BY |
|  | CHANGED_DT | Server system date and time |

#### 6. Delete TB_M_PART_CANDIDATE_DEST – Edit mapping - [Save] - removed destination
- Source: TB_M_PART_CANDIDATE_DEST (keys: PART_NO = Edited part, PERIOD = Ongoing period, DEST_CODE = Not in the panel)
- Destination keys: PART_NO = Edited part, PERIOD = Ongoing period, DEST_CODE = Not in the panel

| Source field | Destination field | Description |
|---|---|---|
|  | PART_NO | Row is deleted |
|  | PERIOD | Row is deleted |
|  | DEST_CODE | Row is deleted |
|  | CASE_DAY | Row is deleted |

#### 7. Update TB_M_PART_CANDIDATE – Edit mapping - [Save]
- Source: Key-in from screen
- Destination keys: PART_NO = Edited part

| Source field | Destination field | Description |
|---|---|---|
|  | SYNC_STATUS | '0' (No Sync) |
|  | LAST_SOURCE | 'SCREEN' |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 8. Insert TB_H_PART_CANDIDATE – Edit mapping - [Save]
- Source: Key-in from screen

| Source field | Destination field | Description |
|---|---|---|
|  | HIST_ID | Auto (identity) |
|  | PART_NO | Part of the event |
|  | PERIOD | Ongoing calculation period |
|  | EVENT_TYPE | 'MAPPING' |
|  | SOURCE | 'SCREEN' |
|  | UPLOAD_ID | NULL |
|  | DEST_CODE | Destination added, changed or removed |
|  | FIELD_NAME | 'CASE_DAY' |
|  | OLD_VALUE | Case/Day before (NULL when added) |
|  | NEW_VALUE | Case/Day after (NULL when removed) |
|  | REMARK | NULL |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date and time |

#### 9. Update TB_M_PART_CANDIDATE – [Sync]
- Source: TB_M_PART_CANDIDATE (keys: PART_STATUS = 'Active', SYNC_STATUS = '0' or '2')
- Destination keys: PART_NO = Each part to synchronise

| Source field | Destination field | Description |
|---|---|---|
|  | SYNC_STATUS | '3' (Waiting); XD06 and XD07 are started |

#### 10. Insert / Update TB_R_CROSSDOCK_IF_RESULT – [Sync]: one row per part and target system
- Source: TB_M_PART_CANDIDATE (keys: SYNC_STATUS = '3' (set by this [Sync]))
- Destination keys: PART_NO + TARGET_SYSTEM = Each part to synchronise x 'GTOPAS' / 'APPOLE'

| Source field | Destination field | Description |
|---|---|---|
| PART_NO | PART_NO |  |
|  | TARGET_SYSTEM | 'GTOPAS' and 'APPOLE' |
|  | PERIOD | Ongoing calculation period |
|  | IF_STATUS | '3' (Waiting) |
|  | IF_DT | NULL |
|  | IF_FILE_NAME | NULL |
|  | IF_MESSAGE | NULL |
|  | CREATED_BY | Login user ID (insert only) |
|  | CREATED_DT | Server system date-time (insert only) |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

## 6. Operation description

5.1 - 5.10: Part List tab. 5.11 - 5.20: Mapping per Destination tab.

### 5.1 Initial Display

a. The sub-menu is opened only for users logged in with a Procurement account.
b. Search criteria: 'Part Number' and 'Part Name' blank, 'Status' = All, 'Sort by' = Newer to Older.
c. Retrieve all parts of TB_M_PART_CANDIDATE and display them sorted by CHANGED_DT descending, 25 rows per page, page 1.
d. If no part is registered at all, hide the table and display message no. 2 with [Upload Excel] and [Add one part].

### 5.2 Specifying Criteria

a. The criteria are applied when the user clicks [Search] (or presses Enter in 'Part Number' / 'Part Name'); changing a criterion alone does not change the list. 'Sort by' is applied at once.
b. 'Part Number' and 'Part Name' match by 'contains', case-insensitive; 'Status' matches exactly. All criteria are combined with AND.
c. Clicking [Search] or changing 'Sort by' or 'Rows per page' returns the list to page 1.
d. If no row matches, hide the table and paging and display message no. 1 with [Reset filter].

### 5.3 Result List

a. Counter 'N parts' is counted over the whole filtered result, not only the current page.
b. Total Pcs/Day = Pcs/Case x Max Case/Day.

### 5.4 Add Part

- a. User clicks [Add Part].
  1. Open the 'Add Part Candidate Crossdock' modal. 'Status' = Candidate and locked (a new part is always Candidate); 'Effective Start Date' = system date + 1 day, minimum today.
  2. 'Part No' lists parts of TB_M_PART_MASTER that are not yet registered in TB_M_PART_CANDIDATE, so can not register part into Crossdock master
  3. Selecting a Part No autofills 'Part Name'. 'Max Case/Day' is locked until 'Pcs/Case' is filled.
  4. [Save] is enabled only when Part No, Min MAD (whole number, 0 or more), Pcs/Case > 0 and Max Case/Day > 0 are filled; otherwise its tooltip shows message no. 5, 15, 6 or 7 for the first missing item.

- b. User clicks [Save].
  1. If the Part No was registered by another user in the meantime, display message no. 3. Stop.
  2. Insert the part into TB_M_PART_CANDIDATE with PART_STATUS = Candidate and SYNC_STATUS = 0 (No Sync) (refer Data Edit Mapping).
  3. Insert the change history when any register or update data in Part List
  4. Close the modal, reset the Part Number / Part Name / Status filters, sort Newer to Older and display message no. 9. The new part is shown at the top.

- c. User clicks [Cancel] or the X icon: close the modal without saving.

### 5.5 Edit Part Data

- a. User clicks the 'Part Number' link or [Edit] on a row.
  1. Open the 'Edit part data' modal with the saved values. 'Part No' is locked; 'Status' can be Candidate / Active / Inactive.
  2. 'Effective Start Date' is editable only while the saved status is Candidate (minimum today); otherwise locked with message no. 10 as tooltip.
  3. 'Min MAD' (mandatory, whole number 0 or more), 'Pcs/Case' and 'Max Case/Day' can be changed; 'Total Pcs/Day' is recalculated.
  4. Active part only: below Max Case/Day show 'Mapped Case/Day (current period): n' = total Case/Day of the part in TB_M_PART_CANDIDATE_DEST for the ongoing period (' · no destination yet' when none), so the user sees the lowest allowed Max Case/Day before Save.
  5. Max Case/Day can not be less than the total Case/Day already mapped to destinations in the ongoing period (TB_M_PART_CANDIDATE_DEST); otherwise the field is marked red, message no. 14 is shown below Pcs/Case & Max Case/Day and [Save] is disabled. The user must first reduce the mapping in Mapping per Destination (same rule as upload check 9).

- b. User clicks [Save].
  1. If the record was changed by another user after it was opened, display message no. 4. Stop.
  2. Check Max Case/Day against the mapped total of the ongoing period again on the server; if it is below, display message no. 14. Stop.
  3. Update TB_M_PART_CANDIDATE and set SYNC_STATUS = 0 (No Sync), CHANGED_BY and CHANGED_DT. Every Save returns the part to No Sync so the D/S user synchronises it again.
  4. Insert the change history when any register or update in Part List
  5. Close the modal, move the part to the top of the list and display message no. 9.

### 5.6 History Setting

a. History retrieved from inserted data when user add/modify part list data
b. User clicks the clock icon on a row: open 'History setting' with the change timeline of the part, newest first.
c. Each event shows the title, date-time, field name, old value (struck through) → new value and user.
d. History is read from TB_H_PART_CANDIDATE, which records every change of the part: Add / Edit by screen, Upload, mapping changes (add, change or remove a destination) and Sync results. A part without history shows message no. 12.

TB_H_PART_CANDIDATE (proposed) - one record per changed field, insert only:

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | Y | Calculation period YYYYMM for MAPPING / SYNC / CALC; NULL for ADD / EDIT (Part List has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / SYNC / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / IF / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY, SYNC_STATUS |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text, e.g. SYNC_MESSAGE of a Failed sync |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (IF batch user ID for SYNC, batch user ID for BATCH) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

Events: ADD / EDIT (source SCREEN or UPLOAD, PERIOD NULL), MAPPING (source SCREEN or UPLOAD, PERIOD and DEST_CODE filled, FIELD_NAME CASE_DAY), SYNC (source IF, FIELD_NAME SYNC_STATUS, REMARK = SYNC_MESSAGE). CALC (source BATCH, FIELD_NAME PART_STATUS, status set by the DAD Volume Calculation) and MAPPING with source BATCH (XD05 process 2 (mapping destination)).

Retention: the history of a part is kept; there is no housekeeping job (decided 30-Oct).

### 5.7 Upload Excel

a. User clicks [Upload Excel]: open the modal with the template columns, the rules and the file area (.xlsx, max 5 MB, max 5,000 rows).
b. Edit rows use sheet 'Upload' of the Part List Export Excel as base file (pre-filled with flag E).
c. Status rule: a Candidate part's status cannot be changed by upload; Active <-> Inactive can be changed; no part can be changed to Candidate.
d. User clicks [Validate file] (save button of the upload): the file is passed to the upload batch; validation, saving (all-or-nothing) and logging follow UISS-Batch "XD02 Cross Dock Part Master Upload Batch".
e. When the upload is completed, close the modal and display message no. 11. When it is rejected, show the batch result (error list) - refer UISS-Batch.
f. Changed parts show Sync Status No Sync.

### 5.8 Export Excel

a. User clicks [Export Excel]: download Crossdock_Part_List_YYYYMMDD.xlsx.
b. Sheet 'Part List': rows of the active filter and sort (all pages) with Part Number, Part Name, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, Status, Effective Start Date, Last Update. Information only.
c. Sheet 'Upload': every registered part with part_no, min_mad, pcs_case, max_case_day, status, upload = E, effective_start_date (DD-Mon-YYYY). Base file for Edit uploads.
d. If the file cannot be created, display message no. 13.

### 5.9 Run DAD Calculation

a. The DAD Volume Calculation batch runs on its own scheduler (set in system master) with 3 auto retries. It compares the average MAD of each part with Min MAD and sets the part status to Active or Inactive (refer UISS-Batch XD05 DAD Volume Calculation (process 1)).
b. The result list header shows 'Last DAD calculation' (last successful run) and, when the scheduled run and its 3 retries have failed, the badge 'Scheduled run failed 3x'.
c. [Run calculation] is enabled only in that failed state; otherwise it is disabled with message no. 17 as tooltip.
d. User clicks [Run calculation]: start the batch. When it completes, update 'Last DAD calculation', hide the badge, refresh the list and display message no. 16. When it fails, the batch logs the error (all-or-nothing) and the button stays enabled.
e. A change from Active to Inactive made by the batch sets the part to No Sync (it is sent as inactive by the next [Sync]); other status changes made by the batch do not change the Sync Status. The user may still change the status afterwards by screen or upload.

### 5.10 Status Definitions

| Status | Value | Definition |
|---|---|---|
| Part Status | Candidate | Newly registered part without MAD history. Initial status of every new part; cannot be chosen when adding. |
| Part Status | Active | Active part. Only Active parts can be mapped in the Mapping per Destination sub-menu. |
| Part Status | Inactive | Inactive part. Not mapped in the Mapping per Destination sub-menu. |
| Sync Status | No Sync (0) | Not sent yet, or changed since the last synchronisation. Set on every Save. |
| Sync Status | Waiting (3) | [Sync] clicked in the Mapping per Destination tab; waiting for XD06 (GTOPAS) and / or XD07 (AP POLE). |
| Sync Status | Success (1) | XD06 updated the destinations in GTOPAS and XD07 sent the cross dock master to AP POLE (ongoing period). |
| Sync Status | Failed (2) | XD06 or XD07 could not send the part (target and reason in SYNC_MESSAGE); sent again by the next [Sync]. |

Active and newly Inactive parts are synchronised (not Candidate). A Save while Waiting returns it to No Sync, so the result of XD06 / XD07 for the old data is not kept as Success.

### 5.11 Initial Display

a. The sub-menu is opened only for users logged in with a D/S account.
b. Search criteria: 'Calculation period' = ongoing period, 'Part Number' blank, 'Sync Status' = No Sync.
c. Ongoing period: list every Active part of TB_M_PART_CANDIDATE, with its destinations of TB_M_PART_CANDIDATE_DEST for that period (a part without destinations is listed with Total Case/Day 0).
d. A new period starts empty: the mapping of the previous period is not copied. Every Active part is listed with its Max Case/Day from Part List (the quota) but no destination yet (Total Case/Day 0, 0%), until the D/S user assigns it by Edit mapping or Upload Excel.
e. Past period: list every part that has rows in TB_M_PART_CANDIDATE_DEST for that period, whatever its current status. 'All periods' lists both.

### 5.12 Specifying Criteria

a. The criteria are applied when the user clicks [Search] (or presses Enter in 'Part Number'); changing a criterion alone does not change the list.
b. 'Part Number' matches by 'contains', case-insensitive; 'Calculation period' and 'Sync Status' match exactly. All criteria are combined with AND.
c. [Upload Excel] and Export Excel follow the period of the applied criteria.
d. If no row matches, hide the table and display message no. 18.
e. With the default Sync Status = No Sync, parts that are Success or Failed are hidden until the filter is changed.

### 5.13 Result List

a. Total Case/Day = sum of CASE_DAY of the part and period; Pcs/Day = Pcs/Case x Total Case/Day.
b. Percentage = Total Case/Day / Max Case/Day; it never exceeds 100% because the total can not go above Max Case/Day (Save, upload and the Max Case/Day edit in Part List are blocked).
c. The list is paged: 25 rows per page by default (25 / 50 / 100), with paging information and [Prev] / [Next]. A part with its Destination Mapping panel counts as one row. [Search], Reset and a change of Rows per page return to page 1.

### 5.14 Destination Mapping Panel

a. User clicks the arrow on a row: open the panel with the allocation chip, the note and the destination table (Destination, Case/Day, Pcs/Day, Percentage). All items are read only.
b. Ongoing period: show [Edit mapping]. Past period: show message no. 22 instead; the mapping cannot be changed.
c. A part without destination shows message no. 19.

### 5.15 Edit Mapping

- a. User clicks [Edit mapping].
  1. Copy the mapping into a draft; Destination and Case/Day become editable, a trash icon appears per row and [Add destination] is shown.
  2. The Destination list hides destinations already used by another row of the same part (one destination per part).
  3. [Add destination] adds a row with 'Select destination' and Case/Day 0.
  4. [Split evenly] (more than one row): Case/Day of each row = floor(Max Case/Day / number of rows); the remainder is added +1 per row from the first row. Example 24 / 3 = 8 / 8 / 8; 25 / 3 = 9 / 8 / 8.
  5. The allocation chip and note are recalculated on every change.

- b. Save rules - [Save] is disabled while:
  - the total Case/Day is above Max Case/Day (show message no. 20);
  - the part has no destination row; or
  - a row has no destination selected (show message no. 21).
  - A total below or equal to Max Case/Day is allowed; below is shown as '{n} case/day left'.

- c. User clicks [Save].
  1. If the mapping was changed by another user after edit mode started, display message no. 25. Stop.
  2. Save the draft per destination in TB_M_PART_CANDIDATE_DEST: update the Case/Day of a kept one, insert a new one, delete a removed one (refer Data Edit Mapping).
  3. Set SYNC_STATUS = 0 (No Sync) in TB_M_PART_CANDIDATE, so the D/S user synchronises the part again.
  4. Insert a history record per added, changed or removed destination in TB_H_PART_CANDIDATE (event MAPPING, source SCREEN, DEST_CODE, FIELD_NAME CASE_DAY, old / new Case/Day).
  5. Leave edit mode and show the saved mapping.

- d. User clicks [Cancel] or closes the panel: discard the draft.

### 5.16 Sync

- a. User clicks [Sync (n)] (on demand).
  1. Select every Active part of the ongoing period, and every part that became Inactive (set to No Sync by XD05), with Sync Status No Sync or Failed, whatever the search criteria show (n of the button). Inactive parts: all their rows are deleted in GTOPAS (XD06) and AP POLE (XD07). Candidate parts are never synchronised.
  2. Set SYNC_STATUS = 3 (Waiting) for these parts in TB_M_PART_CANDIDATE, set one row per part and target system (GTOPAS, AP POLE) to IF_STATUS = 3 (Waiting) in TB_R_CROSSDOCK_IF_RESULT, and start XD06 and XD07. Display message no. 27.
  3. With the default filter No Sync the parts leave the list; select Sync Status = Waiting or All to follow them.

- b. Interface functions (one per target system; refer UISS-Batch XD06 and XD07).
  1. XD06 IF Cross Dock Master to GTOPAS registers / deletes, by RPA, the destinations of each Waiting part in GTOPAS (Inactive: all rows). XD07 IF Cross Dock Master to AP POLE sends, per Active part, Pcs/Case, Max Case/Day and all destinations with Case/Day of the ongoing period (new part: added; existing: updated; Inactive: deleted).
  2. XD06 hands the part x destination list to the RPA bot; XD07 sends a file by SFTP. The result is written in the dummy table TB_R_CROSSDOCK_IF_RESULT (IF_STATUS 1 sent / 2 Failed, IF_DT, IF_FILE_NAME, IF_MESSAGE).
  3. Overall SYNC_STATUS of the part: stays 3 (Waiting) while one target is still Waiting; 1 (Success) when both targets are Success; 2 (Failed) when a target failed (SYNC_MESSAGE = target and reason); 0 (No Sync) when the part was changed after it was read.
  4. Every result is recorded in TB_H_PART_CANDIDATE (event SYNC, source IF, REMARK = target and message).

- c. A Failed part shows SYNC_MESSAGE (target and reason) as tooltip on its chip (message no. 28) and is sent again to both targets by the next [Sync] (repeatable: GTOPAS only gets the differences, AP POLE gets the complete set again).
- d. Interface method: RPA to GTOPAS (XD06), file by SFTP to AP POLE (XD07); fields and topology refer UISS-Batch XD06 / XD07 (topology TBC).

### 5.17 Upload Excel

a. [Upload Excel] is enabled only when the ongoing calculation period is selected; otherwise it is disabled with message no. 23 as tooltip.
b. The modal shows the template columns (part_no, dest_code, case_day, upload, total_case_day), the upload rules and the file area (.xlsx, max 5 MB, max 5,000 rows).
c. Base file: sheet 'Upload' of Export Excel with the ongoing period selected. A part in the file gets its mapping updated per destination (refer XD03); parts not in the file are not changed.
d. User clicks [Validate file] (save button of the upload): the file is passed to the upload batch; validation, saving (all-or-nothing) and logging follow UISS-Batch "XD03 Part and Destination Mapping Upload Batch".
e. When the upload is completed, close the modal and display message no. 24. When it is rejected, show the batch result (error list) - refer UISS-Batch.
f. Changed parts show Sync Status No Sync.

### 5.18 Export Excel

a. User clicks [Export Excel]: download Crossdock_Mapping_per_Destination_<period>_YYYYMMDD.xlsx (<period> e.g. Sep_2026 or All_periods).
b. Sheet 'Mapping per Destination': rows of the active filter, one row per destination (a part without destination gives one row with blank destination columns). Columns: Period, Part Number, Part Name, Pcs/Case, Total Case/Day, Pcs/Day, Percentage, Sync Status, Destination Code, Destination, Dest Case/Day, Dest Pcs/Day, Dest Percentage. Information only.
c. Sheet 'Upload': every Active part of the ongoing period with part_no, dest_code, case_day, upload, total_case_day (= Max Case/Day); one row per destination, and one row with dest_code and case_day blank for a part without mapping. Empty when a past period or All periods is selected. upload = E for a mapped destination, A for the blank row.
d. If the file cannot be created, display message no. 26.

### 5.19 Run Mapping Calculation

a. The XD05 process 2 (mapping destination) batch runs on its own scheduler (set in system master) with 3 auto retries. It creates the new calculation period and its destination mapping (refer UISS-Batch XD05 DAD Volume Calculation (process 2)).
b. The section header shows 'Last mapping calculation' (last successful run) and, when the scheduled run and its 3 retries have failed, the badge 'Scheduled run failed 3x'.
c. [Run calculation] is enabled only in that failed state; otherwise it is disabled with message no. 30 as tooltip.
d. User clicks [Run calculation]: start the batch. When it completes, update 'Last mapping calculation', hide the badge and display message no. 29. When it fails, the batch logs the error (all-or-nothing) and the button stays enabled.

### 5.20 Data Level and Status Definitions

| Item | Value | Definition |
|---|---|---|
| Table | TB_M_PART_CANDIDATE | Part List data, part number level (key PART_NO). Holds Max Case/Day, status and Sync Status. |
| Table | TB_M_PART_CANDIDATE_DEST | Mapping data, part number + calculation period + destination level (key PART_NO, PERIOD, DEST_CODE). PERIOD = CHAR(6) YYYYMM, e.g. 202609; displayed as 'Sep 2026'. |
| Table | TB_M_H0125_DESTINATION | Destination Master (existing, read only). Crossdock uses DESTINATION_CD and DESTINATION_NAME only. |
| Part Status | Active | Only Active parts are mapped in the ongoing period. |
| Sync Status | No Sync (0) | Not sent yet, or changed since the last synchronisation. |
| Sync Status | Waiting (3) | [Sync] clicked; waiting for XD06 (GTOPAS) and / or XD07 (AP POLE). |
| Sync Status | Success (1) | The part was sent to GTOPAS and AP POLE. |
| Sync Status | Failed (2) | GTOPAS or AP POLE could not receive the part; target and reason in SYNC_MESSAGE; retried by the next [Sync]. |
| Period | Ongoing / past | Created by the calculation batch. Ongoing (latest period): mapping can be edited and uploaded. Past: read only. |

Sync Status is kept per part in TB_M_PART_CANDIDATE because a part is synced as one unit (GTOPAS: destination list; AP POLE: Pcs/Case, Max Case/Day, destinations); the result per target system is in TB_R_CROSSDOCK_IF_RESULT. Every mapping change and every Sync result is recorded in TB_H_PART_CANDIDATE (with the period).

## 7. Display messages

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| **Part List - Search Operation** |  |  |  |  |  |
| MSG1 | Change search criteria | No part matches the criteria | Info | No matching parts - Loosen the search criteria or reset all filters. | Change the criteria or click [Reset filter] |
| MSG2 | Open Part List | No part registered yet | Info | No crossdock parts registered yet | Click [Upload Excel] or [Add one part] |
| **Part List - Add / Edit Operation** |  |  |  |  |  |
| MSG3 | Click [Save] button | Part No already registered (concurrent add) | Error | Duplication found for {Part No} | Close the modal and search the part |
| MSG4 | Click [Save] button | Record changed by another user | Error | Error in Update because of concurrency check. | Close the modal, refresh and edit again |
| MSG5 | Hover disabled [Save] | Part No not selected | Info | Part No is required | Select a Part No |
| MSG6 | Hover disabled [Save] | Pcs/Case not filled | Info | Enter Pcs/Case first (step 2) | Fill Pcs/Case |
| MSG7 | Hover disabled [Save] | Max Case/Day not filled | Info | Enter Max Case/Day (step 2) | Fill Max Case/Day |
| MSG8 | Type in 'Part No' | No unregistered part matches the text | Info | Part not found | Check the Part No |
| MSG9 | Click [Save] button | Part saved successfully | Info | Saved successfully - {Part No} · {Part Name} has been added/updated. It is now at the top of the Part List. | Click [OK] |
| MSG10 | Hover 'Effective Start Date' | Saved status is Active / Inactive | Info | Can only be changed while the status is still Candidate | - |
| **Part List - Upload Operation** |  |  |  |  |  |
| MSG11 | Click [Validate file] button | Upload validated and saved | Info | Saved successfully - Upload completed. The file has been validated and the part settings have been saved to the Part List. | Click [OK] |
| **Part List - History Operation** |  |  |  |  |  |
| MSG12 | Click History icon | Part has no history | Info | No change history for this part yet. | Click [Close] |
| **Part List - Export Operation** |  |  |  |  |  |
| MSG13 | Click [Export Excel] button | Excel file cannot be created | Error | Export Excel failed. Please try again. | Click [Export Excel] again; contact administrator if it persists |
| MSG14 | Change 'Max Case/Day' in Edit / click [Save] | Max Case/Day below the total Case/Day mapped in the ongoing period | Error | Max Case/Day can not be less than the mapped total ({n} case/day) of the ongoing period. Reduce the mapping in Mapping per Destination first. | Reduce the mapping in Mapping per Destination first, or enter a higher Max Case/Day |
| MSG15 | Hover disabled [Save] | Min MAD blank or not a whole number | Info | Enter Min MAD (whole number, 0 or more) | Fill Min MAD |
| **Part List - Calculation Operation** |  |  |  |  |  |
| MSG16 | Click [Run calculation] button | DAD Volume Calculation completed | Info | Calculation completed - DAD volume calculation completed. Part statuses have been updated from the average MAD against Min MAD. | Click [OK] |
| MSG17 | Hover disabled [Run calculation] | Scheduled run has not failed 3 times | Info | Enabled only when the scheduled run has failed 3 times | - |
| **Mapping - Search Operation** |  |  |  |  |  |
| MSG18 | Change search criteria | No part matches the criteria | Info | No parts match these filters - Change the period or sync status, or press Reset to show all parts. | Change the criteria or click [Reset] |
| **Mapping - Edit Mapping Operation** |  |  |  |  |  |
| MSG19 | Open Destination Mapping panel | Part has no destination | Info | No destination yet - Click Edit mapping and add at least one destination so the part is included in the volume calculation. | Click [Edit mapping] and add a destination |
| MSG20 | Change Case/Day in edit mode | Total Case/Day above Max Case/Day | Error | Allocation of {n} case/day exceeds Max Case/Day ({m}). Reduce one of the destinations. | Reduce Case/Day of a destination |
| MSG21 | Edit mode | A row has no destination selected | Error | Select a destination for every row, or remove the empty row, before saving. | Select a destination or remove the row |
| MSG22 | Open panel of a past period | Period is not ongoing | Info | Past period - read only | - |
| **Mapping - Upload Operation** |  |  |  |  |  |
| MSG23 | Hover disabled [Upload Excel] | Past period or All periods selected | Info | Past period - read only. Select the ongoing period to upload. | Select the ongoing period |
| MSG24 | Click [Validate file] button | Upload validated and saved | Info | Saved successfully - Upload completed. The file has been validated and the destination mapping has been saved to Mapping per Destination. | Click [OK] |
| **Mapping - Save Operation** |  |  |  |  |  |
| MSG25 | Click [Save] button | Mapping changed by another user | Error | Error in Update because of concurrency check. | Cancel, refresh and edit again |
| **Mapping - Export Operation** |  |  |  |  |  |
| MSG26 | Click [Export Excel] button | Excel file cannot be created | Error | Export Excel failed. Please try again. | Click [Export Excel] again; contact administrator if it persists |
| **Mapping - Sync Operation** |  |  |  |  |  |
| MSG27 | Click [Sync] button | Parts handed to XD06 / XD07 | Info | Sync requested for {n} part(s). They stay Waiting until GTOPAS and AP POLE have received them. | - |
| MSG28 | Hover a Failed Sync Status chip | GTOPAS or AP POLE could not receive the part | Info | Sync failed: {SYNC_MESSAGE}. The part is sent again with the next Sync. | Correct the cause if needed and click [Sync] |
| **Mapping - Calculation Operation** |  |  |  |  |  |
| MSG29 | Click [Run calculation] button | Mapping calculation (XD05 process 2) completed | Info | Calculation completed - Mapping destination calculation completed. The destination mapping of the new period has been created. | Click [OK] |
| MSG30 | Hover disabled [Run calculation] | Scheduled run has not failed 3 times | Info | Enabled only when the scheduled run has failed 3 times | - |

## 8. Logging messages

| ID | Event | Cause | Type | Message | Action | Exception |
|---|---|---|---|---|---|---|
| LOG1 | Click [Save] button | Database error on insert/update of TB_M_PART_CANDIDATE | Error | Failed to save part <PART_NO>: <DB error message>. | Show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG2 | Click [Export Excel] button | Excel file generation error | Error | Export Excel of Part List failed: <error message>. | Display Message no. 13 | Y |
| - | Click [Validate file] button | Upload processing | Info | Logging is handled by the Part List Upload batch (refer UISS-Batch "XD02 Cross Dock Part Master Upload Batch"). | - | N |
| LOG3 | Click [Save] button | Database error on save of TB_M_PART_CANDIDATE_DEST | Error | Failed to save mapping of part <PART_NO>, period <PERIOD>: <DB error message>. | Show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG4 | XD06 / XD07 | GTOPAS or AP POLE rejects a part | Error | Logging is done by XD06 / XD07 (refer UISS-Batch XD06 / XD07); the chip shows the result. | Status Failed; Display Message no. 28 on the chip | N |
| LOG5 | Click [Export Excel] button | Excel file generation error | Error | Export Excel of Mapping per Destination failed: <error message>. | Display Message no. 26 | Y |
| - | Click [Validate file] button | Upload processing | Info | Logging is handled by the Mapping per Destination Upload batch (refer UISS-Batch "XD03 Part and Destination Mapping Upload Batch"). | - | N |

## 9. Tables

#### TB_H_PART_CANDIDATE (history, proposed)
History of every change of a crossdock part (Add / Edit by screen or upload, mapping changes, Sync results, status changes and mappings made by the calculation batches). Read by the History setting modal of Part List (index PART_NO, CREATED_DT). No retention limit: the history is kept (no housekeeping job, decided 30-Oct).

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | Y | Calculation period YYYYMM for MAPPING / SYNC / CALC; NULL for ADD / EDIT (Part List has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / SYNC / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / IF / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, EFFECTIVE_START_DATE, CASE_DAY, SYNC_STATUS |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text, e.g. SYNC_MESSAGE of a Failed sync |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (IF batch user ID for SYNC, batch user ID for BATCH) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

#### TB_R_CROSSDOCK_IF_RESULT (transaction, proposed)
Dummy table (proposed): send status of the cross dock master per part and target system (XD06 GTOPAS, XD07 AP POLE). The real output is the interface data sent to the target (AP POLE: file by SFTP; GTOPAS: RPA). The overall Sync Status of the part stays in TB_M_PART_CANDIDATE.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| PART_NO | VARCHAR(TBD) | Y | N | Part number (TB_M_PART_CANDIDATE) |
| TARGET_SYSTEM | VARCHAR(10) | Y | N | 'GTOPAS' (XD06) / 'APPOLE' (XD07) |
| PERIOD | CHAR(6) |  | N | Calculation period of the mapping sent (YYYYMM) |
| IF_STATUS | VARCHAR(1) |  | N | '3' Waiting / '1' Success / '2' Failed |
| IF_DT | DATETIME |  | Y | Date-time of the result of the target system |
| IF_FILE_NAME | VARCHAR(100) |  | Y | Name of the interface file (AP POLE) or RPA input file (GTOPAS) |
| IF_MESSAGE | VARCHAR(500) |  | Y | Reason when Failed; blank when Success |
| CREATED_BY | VARCHAR(TBD) |  | N | User who created the record |
| CREATED_DT | DATETIME |  | N | Created date and time |
| CHANGED_BY | VARCHAR(TBD) |  | N | User who last changed the record |
| CHANGED_DT | DATETIME |  | N | Last changed date and time |
