# XD01 – Cross Dock Part Master Screen

> Generated from `deliverables/function_list_v2/specs/XD01_spec.json` (UISS `XD01_UISS_Screen_CrossDockPartMaster.xlsx`). Do not edit by hand: change the spec and run `python3 prepare_code/build_md.py`. Document names: GTOPAS / NSP (prototype: G-System / Supplier System).

| Phase | Project | Block | Function | Created | By | Type |
|---|---|---|---|---|---|---|
| DR | Crossdock Optimization | Screen | XD01 Cross Dock Part Master Screen | 18-Oct-26 | FID Rayhan | screen |

## Revision

| Rev | Author | Date | Reviewed by | Description |
|---|---|---|---|---|
| 0.1 | FID Rayhan | 18-Oct-26 |  | Initial Draft |
| 0.2 | FID Rayhan | 17-Nov-26 |  | Sync Status rule: No Sync only when a value sent to GTOPAS / AP POLE changes; a manual Active -> Inactive is taken by [Sync] (FB-204 / FB-205). |
| 0.3 | FID Rayhan | 17-Nov-26 |  | [Sync] takes every part with status Active (ongoing period) or Inactive whose Sync Status is No Sync or Failed, whatever the filter shows (Candidate never). |
| 0.4 | FID Rayhan | 18-Nov-26 |  | Sheet "Active to Inactive" removed (18-Nov): Inactive parts with No Sync / Failed are taken by [Sync] by their status. Export Excel of Export Crossdock Master has 2 sheets again; column Last Sync stays. |
| 0.5 | FID Rayhan | 19-Nov-26 |  | Names Kanban / Export Crossdock Master; period on the Kanban Crossdock Master; Order Type per destination row; Max Case/Day down: destinations first (19-Nov). |
| 0.6 | FID Rayhan | 20-Nov-26 |  | Sync without response from the RPA: Sync Status No Sync / Sent, column Last Sent, button [Re-send last Sync] (20-Nov). |
| 0.7 | FID Rayhan | 20-Nov-26 |  | TB_R_CROSSDOCK_IF_RESULT removed: send time per target on TB_M_PART_CANDIDATE (GTOPAS_SYNC_DT, APPOLE_SYNC_DT, SYNC_RUN_ID); columns Last Sent GTOPAS / AP POLE; Log per run; history SYNC by NSP (20-Nov). |
| 0.8 | FID Rayhan | 22-Nov-26 |  | Sync with TB_H_PART_CANDIDATE_STG_SYNC (22-Nov): no sync column on TB_M_PART_CANDIDATE; staging rows per value change (screen); [Sync] sets status / SEND_SEQ / run ID; Sync Status AP POLE / GTOPAS worked out from the staging (5.24). |
| 0.9 | FID Rayhan | 22-Nov-26 |  | Copy review: decision dates removed from the body text (kept here), sentences with broken grammar rewritten, screen messages reworded (no rule changed). |
| 0.10 | FID Rayhan | 22-Nov-26 |  | New 5.25 Table changes per Save: Add / Edit / Delete per table for every save on the screen. |
| 0.11 | FID Rayhan | 23-Nov-26 |  | Staging per target: TB_H_STG_APPOLE_KANBAN / _EXPORT / TB_H_STG_GTOPAS replace TB_H_PART_CANDIDATE_STG_SYNC, SP_STG_WRITE at the save (OPERATION_TYPE 1-5, Superseded), SP_STG_SYNC at [Sync], RPA parent flow (5.24, 5.25). Effective Start Date replaced by Period (Add Part: ongoing or next period). Candidate part: Candidate or Active only. |
| 0.12 | FID Rayhan | 24-Nov-26 |  | Order Type per destination row on the Export Crossdock Master screen (item Order Type, message no. 31, Data Map ORDER_TYPE). |
| 0.13 | FID Rayhan | 24-Nov-26 |  | Export Crossdock Master list: Part Name and Last Sent GTOPAS / AP POLE columns removed (tooltips); column rules; Sync Status as Non Sync chip / Sync check / Not sent. |
| 0.14 | FID Rayhan | 24-Nov-26 |  | Export Crossdock Master list: column Used/Quota (Case) (was Total Case/Day (used / quota)); AP POLE Status and GTOPAS Status as two columns; narrower number columns. |
| 0.15 | FID Rayhan | 24-Nov-26 |  | Export Crossdock Master: Upload Excel and Export Excel moved to the page header, as on Kanban Crossdock Master. |
| 0.16 | FID Rayhan | 26-Nov-26 |  | Staging: no SYNC_RUN_ID, the run is SYNC_DT (one value per [Sync] click / rollover); one unsent row per key (a new change updates it, back to the sent value deletes it); SYNC_STATUS 0 / 1. SQL: prepare_code/sql/crossdock_staging_sync.sql. |
| 0.17 | FID Rayhan | 26-Nov-26 |  | TB_H_STG_APPOLE_KANBAN / _EXPORT: EFFECTIVE_MONTH_YEAR removed (same value as PERIOD); the views make Effective Month / Year (MM/YYYY of PERIOD) for the upload file. |

## 1. General

### Objective

- One screen with two tabs: Kanban Crossdock Master (part number level) and Export Crossdock Master (part + calculation period + destination level).
- Kanban Crossdock Master tab: To register crossdock candidate parts (Part No, Period, Min MAD, Pcs/Case, Max Case/Day).
- Kanban Crossdock Master tab: To search and display registered crossdock parts with their status and capacity.
- Kanban Crossdock Master tab: To change part data and part status (Candidate / Active / Inactive) of a registered part.
- Kanban Crossdock Master tab: To display the change history of a part.
- Kanban Crossdock Master tab: To export the Kanban Crossdock Master to Excel and upload part settings from Excel (Add and Edit).
- Kanban Crossdock Master tab: This sub-menu is opened only for users logged in with a Procurement account; users with a D/S account open the Export Crossdock Master sub-menu instead.
- Export Crossdock Master tab: To split the Max Case/Day of each Active part over destinations (Thailand, Philippines, Vietnam) for the ongoing calculation period.
- Export Crossdock Master tab: To display the destination mapping per part and calculation period, including past periods (read only).
- Export Crossdock Master tab: To send the changes of the Current and Next period to AP POLE (XD07) and GTOPAS (XD06) with [Sync], and show the Sync Status of each part (worked out from the staging tables).
- Export Crossdock Master tab: To export the mapping to Excel and upload the mapping of the ongoing period from Excel.
- Export Crossdock Master tab: This sub-menu is opened only for users logged in with a D/S account; users with a Procurement account open the Kanban Crossdock Master sub-menu instead.

### Display order – Kanban Crossdock Master - Result List (Sort by = Newer to Older, default)

| Field | Order |
|---|---|
| Updated Date (CHANGED_DT) | Descending |

### Display order – Kanban Crossdock Master - Result List (Sort by = Older to Newer)

| Field | Order |
|---|---|
| Updated Date (CHANGED_DT) | Ascending |

### Display order – Kanban Crossdock Master - Result List (Sort by = Default)

| Field | Order |
|---|---|
| Part Number | Ascending |

### Display order – Kanban Crossdock Master - History Setting modal

| Field | Order |
|---|---|
| Event date and time | Descending |

### Display order – Export Crossdock Master - Result List

| Field | Order |
|---|---|
| Part Number | Ascending (TBD) |

### Display order – Export Crossdock Master - Destination Mapping panel

| Field | Order |
|---|---|
| Order in which destinations were added | - |

### Buttons

| Button | Function |
|---|---|
| Tab (Kanban Crossdock Master / Export Crossdock Master) | Switch between the Kanban Crossdock Master tab and the Export Crossdock Master tab. |
| Add Part | Open the "Add Part Candidate Crossdock" modal (Add Mode), ready to register a new part. |
| Upload Excel (Kanban Crossdock Master) | Open the "Upload Excel: part settings" modal (Upload Mode). |
| Export Excel (Kanban Crossdock Master) | Download the Kanban Crossdock Master as .xlsx: sheet "Kanban Crossdock Master" (active filter) and sheet "Upload" (base file for Edit uploads). |
| Run calculation (Kanban Crossdock Master) | Start the DAD Volume Calculation batch manually. Enabled only when the scheduled run and its 3 auto retries have failed. |
| Reset | Clear criteria and reset the screen to its initial value. |
| Search | To retrieve records according to the specified criteria. The criteria are applied only when [Search] is clicked (or Enter is pressed in a text box); Sort by is applied at once. |
| Part Number link / Edit | Change the screen into edit mode to modify the selected row ("Edit part data" modal). |
| History | Open the "History setting" modal of the selected part. |
| Prev / Next | Move to the previous / next page of the result list. |
| Save | Kanban Crossdock Master tab: Save the part data entered in the Add / Edit modal.; Export Crossdock Master tab: Save the destination mapping of the part. |
| Cancel | Kanban Crossdock Master tab: Close the Add / Edit modal without saving.; Export Crossdock Master tab: Leave edit mode and discard all changes of the panel. |
| Close | Kanban Crossdock Master tab: Close the History setting / Upload Excel modal (also the X icon of every modal).; Export Crossdock Master tab: Close the Upload Excel modal without uploading. |
| Validate file | Save button of the upload: validate the uploaded file and save it (all-or-nothing), then show the success popup. |
| OK | Close the success popup. |
| Run calculation (Mapping) | Start process 2 (mapping destination) of the XD05 DAD Volume Calculation batch manually. Enabled only when the scheduled run and its 3 auto retries have failed. |
| Sync | Call SP_STG_SYNC (refer 5.24): the staging rows with SYNC_STATUS 0 (AP POLE: Current and Next period; GTOPAS: Current period) get SYNC_DT = time of the click, then the RPA parent flow starts with it. Whatever the filter shows. The label shows the number of parts, e.g. Sync (21). |
| Upload Excel (Mapping) | Open the "Upload Excel: destination mapping" modal. Enabled only when the ongoing calculation period is selected. |
| Export Excel (Mapping) | Download the mapping as .xlsx: sheet "Export Crossdock Master" (active filter) and sheet "Upload" (base file for the upload). |
| Expand (arrow) | Open / close the Destination Mapping panel of the part row. |
| Edit mapping | Change the Destination Mapping panel into edit mode (ongoing period only). |
| Split evenly | Divide Max Case/Day evenly over all destinations of the part. |
| Add destination | Add a new destination row (destination not selected, Case/Day 0). |
| Remove destination | Remove the destination row (trash icon). |

### Screen modes (E = enabled, D = disabled)

| Mode | Section | Description | Tab (Kanban Crossdock Master / Export Crossdock Master) | Add Part | Upload Excel (Kanban Crossdock Master) | Export Excel (Kanban Crossdock Master) | Run calculation (Kanban Crossdock Master) | Reset | Search | Part Number link / Edit | History | Prev / Next | Save | Cancel | Close | Validate file | OK | Run calculation (Mapping) | Sync | Upload Excel (Mapping) | Export Excel (Mapping) | Expand (arrow) | Edit mapping | Split evenly | Add destination | Remove destination |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kanban Crossdock Master - Initial Mode | Search Criteria | Part Number and Part Name blank, Status = All, Sort by = Newer to Older | E | E | E | E | D | E | E | E | E | E | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Initial Mode | Result List | All registered parts, 25 rows per page, page 1. Refer below 1) | E | E | E | E | D | E | E | E | E | E | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Search Result Mode | Result List | Parts matching all criteria (AND); page returns to 1 | E | E | E | E | D | E | E | E | E | E | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Search Result Mode | Empty State | No matching parts; table and paging hidden; [Reset filter] shown | E | E | E | E | D | E | E | D | D | D | D | D | D | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Add Mode (modal) | Part No not selected | Status locked to Candidate; Max Case/Day locked; Save disabled | E | D | D | D | D | D | D | D | D | D | D | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Add Mode (modal) | Part No selected, Pcs/Case blank | Part Name autofilled; Max Case/Day still locked; Save disabled | E | D | D | D | D | D | D | D | D | D | D | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Add Mode (modal) | All required items filled | Total Pcs/Day calculated; Save enabled | E | D | D | D | D | D | D | D | D | D | E | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Edit Mode (modal) | Saved status Candidate | Part No and Period locked; Status (Candidate or Active), Min MAD, Pcs/Case, Max Case/Day editable | E | D | D | D | D | D | D | D | D | D | E | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Edit Mode (modal) | Saved status Active / Inactive | Same as 4.a, Status Active or Inactive (no part goes back to Candidate) | E | D | D | D | D | D | D | D | D | D | E | E | E | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - History Mode (modal) | History setting | Change timeline of the selected part, read only | E | D | D | D | D | D | D | D | D | D | D | D | E | D | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Upload Mode (modal) | Upload Excel | Template columns, rules, file area | E | D | D | D | D | D | D | D | D | D | D | D | E | E | D | - | - | - | - | - | - | - | - | - |
| Kanban Crossdock Master - Upload Mode (modal) | Success popup | "Saved successfully" after Save or Validate file | E | D | D | D | D | D | D | D | D | D | D | D | D | D | E | - | - | - | - | - | - | - | - | - |
| Mapping - Initial Mode | Search Criteria | Calculation period = ongoing period, Part Number blank, Sync Status = Non Sync | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | D | D | D | D |
| Mapping - Initial Mode | Result List | Parts of the ongoing period with Non Sync staging rows. Refer below 1) | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | D | D | D | D |
| Mapping - Search Result Mode | Result List - ongoing period | Active parts matching all criteria | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | D | D | D | D |
| Mapping - Search Result Mode | Result List - past period / All periods | All parts of the period; Upload Excel disabled | E | - | - | - | - | E | E | - | - | D | D | D | D | D | D | D | E | D | E | E | D | D | D | D |
| Mapping - Search Result Mode | Empty State | No parts match the filters; table hidden | E | - | - | - | - | E | E | - | - | D | D | D | D | D | D | D | D | E | E | D | D | D | D | D |
| Mapping - Detail View Mode | Ongoing period | Panel read only; [Edit mapping] shown | E | - | - | - | - | E | E | - | - | E | D | D | D | D | D | E | E | E | E | E | E | D | D | D |
| Mapping - Detail View Mode | Past period | Panel read only; badge 'Past period: read only' instead of [Edit mapping] | E | - | - | - | - | E | E | - | - | D | D | D | D | D | D | D | E | D | E | E | D | D | D | D |
| Mapping - Edit Mapping Mode | Valid mapping | Destination and Case/Day editable; total <= Max Case/Day | E | - | - | - | - | E | E | - | - | E | E | E | D | D | D | E | E | E | E | E | D | E | E | E |
| Mapping - Edit Mapping Mode | Mapping cannot be saved | Total > Max Case/Day, no destination, or a row without destination; Save disabled | E | - | - | - | - | E | E | - | - | E | D | E | D | D | D | E | E | E | E | E | D | E | E | E |
| Mapping - Upload Mode (modal) | Upload Excel | Template columns, rules, file area | E | - | - | - | - | D | D | - | - | D | D | D | E | E | D | D | D | D | D | D | D | D | D | D |
| Mapping - Upload Mode (modal) | Success popup | 'Saved successfully' after Validate file | E | - | - | - | - | D | D | - | - | D | D | D | D | D | E | D | D | D | D | D | D | D | D | D |

- 1) Prev is disabled on the first page and Next on the last page.
- 2) A user logged in with a read-only account sees [View] instead of [Edit] and cannot use Add Part / Upload Excel / Save. TBD: which accounts are read-only is not defined yet.
- 3) Run calculation is shown as D (disabled) by default; it is enabled only when the scheduled DAD Volume Calculation has failed 3 times (auto retry).
- 4) Sync is enabled only when a staging table has a row with SYNC_STATUS 0 (AP POLE: Current / Next, GTOPAS: Current), not limited to the listed rows.
- 5) Split evenly is shown only in edit mode when the part has more than one destination row.
- 7) Prev is disabled on the first page and Next on the last page.
- 8) Run calculation is enabled only when the scheduled XD05 DAD Volume Calculation (process 2) has failed 3 times (auto retry); otherwise disabled with message no. 30 as tooltip.
- 6) A user logged in with a read-only account cannot use Edit mapping, Sync or Upload Excel. TBD: which accounts are read-only is not defined yet.
- 9) '-' = the button is not on the tab of the mode.

## 2. Screen flow

### Screen Flow for Cross Dock Part Master (tabs)

```mermaid
flowchart LR
  pl[["Kanban Crossdock Master tab"]]
  mp[["Export Crossdock Master tab"]]
  pl -->|Tab| mp
  mp -->|Tab| pl
```

### Screen Flow for Kanban Crossdock Master

```mermaid
flowchart LR
  list[["Kanban Crossdock Master"]]
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
- Cancel / Close / X on any modal returns to the Kanban Crossdock Master without saving.

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
  p1["Insert (Add) / update (Edit) part, staging rows by SP_STG_WRITE (Non Sync)"]
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
- Part data valid = Add: Part No selected, Min MAD filled (whole number, 0 or more), Pcs/Case > 0 and Max Case/Day > 0 (otherwise the tooltip shows message no. 5, 15, 6 or 7 for the first missing item). Edit: the same items and Max Case/Day not below the Case/Day already mapped in the ongoing period (message no. 14).
- The check runs on every change in the modal, so [Save] is already disabled before it can be clicked (see Operation Description 5.4 and 5.5).

### Screen Flow for Export Crossdock Master

```mermaid
flowchart LR
  list[["Export Crossdock Master list"]]
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
  p2["Staging rows by SP_STG_WRITE (Non Sync)"]
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

### 1. Initial Mode - Kanban Crossdock Master (Status = All, Sort by = Newer to Older)

![1. Initial Mode - Kanban Crossdock Master (Status = All, Sort by = Newer to Older)](../../deliverables/uiss_screens/part_list/c_01_initial.png)

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

### 9. Edit Mode - Candidate part (Status Candidate or Active)

![9. Edit Mode - Candidate part (Status Candidate or Active)](../../deliverables/uiss_screens/part_list/c_09_edit_candidate.png)

### 10. Edit Mode - Active part (Status Active or Inactive)

![10. Edit Mode - Active part (Status Active or Inactive)](../../deliverables/uiss_screens/part_list/c_10_edit_active.png)

### 11. Edit Mode - Max Case/Day below the mapped total (message no. 14, Save disabled)

![11. Edit Mode - Max Case/Day below the mapped total (message no. 14, Save disabled)](../../deliverables/uiss_screens/part_list/c_14_edit_below_mapped.png)

### 12. History Mode - History setting

![12. History Mode - History setting](../../deliverables/uiss_screens/part_list/c_11_history.png)

### 13. Upload Mode - Upload Excel modal

![13. Upload Mode - Upload Excel modal](../../deliverables/uiss_screens/part_list/c_12_upload.png)

### 14. Upload Mode - Saved successfully popup after Validate file

![14. Upload Mode - Saved successfully popup after Validate file](../../deliverables/uiss_screens/part_list/c_13_upload_success.png)

### 15. Initial Mode - ongoing period, Sync Status = Non Sync

![15. Initial Mode - ongoing period, Sync Status = Non Sync](../../deliverables/uiss_screens/mapping/c_01_default.png)

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

### 26. Before Sync - Sync (n): parts with Non Sync staging rows

![26. Before Sync - Sync (n): parts with Non Sync staging rows](../../deliverables/uiss_screens/mapping/c_12_before_sync.png)

### 27. After Sync - the parts are Sync (tooltip Last Sent AP POLE / GTOPAS = time of the click)

![27. After Sync - the parts are Sync (tooltip Last Sent AP POLE / GTOPAS = time of the click)](../../deliverables/uiss_screens/mapping/c_13_after_sync.png)

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
| 1 | Tab (Kanban Crossdock Master / Export Crossdock Master) |  |  |  |  | I | Tab | Left | Kanban Crossdock Master |  |  |  | Kanban Crossdock Master tab (default) / Export Crossdock Master tab. |
| **<Kanban Crossdock Master - Header Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Add Part |  |  |  |  | I | Button | Center |  |  |  |  | Opens the Add Part modal. Refer Operation Description 5.4. |
| 3 | Upload Excel (Kanban Crossdock Master) |  |  |  |  | I | Button | Center |  |  |  |  | Opens the Upload Excel modal. Refer Operation Description 5.7. |
| 4 | Export Excel (Kanban Crossdock Master) |  |  |  |  | I | Button | Center |  |  |  |  | Downloads Crossdock_Kanban_Master_YYYYMMDD.xlsx. Refer Operation Description 5.8. |
| **<Kanban Crossdock Master - Search Criteria Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Part Number | Key-in |  | Varchar | TBD | I | Text box with suggestion list | Left | Blank | N | X..TBD..X | Contains, case-insensitive | Suggestions = PART_NO of registered parts (TB_M_PART_CANDIDATE). Placeholder 'e.g. PART-B'. Combined with the other criteria by AND. |
| 6 | Part Name | Key-in |  | Varchar | TBD | I | Text box | Left | Blank | N | X..TBD..X | Contains, case-insensitive | Placeholder 'Part name'. Combined with the other criteria by AND. |
| 7 | Status | Key-in |  | Varchar |  | I | Combo Box | Left | All | N |  |  | Options: All / Candidate / Active / Inactive. Filters PART_STATUS. |
| 8 | Sort by | Key-in |  | Varchar |  | I | Combo Box | Left | Newer to Older | N |  |  | Options: Default (Part Number A-Z) / Newer to Older / Older to Newer (by Updated Date). |
| 9 | Reset |  |  |  |  | I | Button | Center |  |  |  |  | Returns every criterion to its initial value. |
| 10 | Search |  |  |  |  | I | Button | Center |  |  |  |  | Applies the criteria to the result list. Typing or selecting a criterion alone does not change the list; Enter in a text box = [Search]. |
| **<Kanban Crossdock Master - Result List Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 11 | Registered parts counter |  |  | Varchar |  | O | Label | Left |  |  | N parts |  | N = number of filtered rows (all pages). |
| 12 | Last DAD calculation |  |  | Datetime |  | O | Label | Left |  |  | DD-Mon-YYYY HH:MM |  | Date-time of the last successful run of the DAD Volume Calculation batch (one date per batch run, all-or-nothing). |
| 13 | Failed badge |  |  | Varchar |  | O | Label | Left |  |  |  |  | 'Scheduled run failed 3x'; shown when the scheduled run and its 3 auto retries have failed. |
| 14 | Run calculation (Kanban Crossdock Master) |  |  |  |  | I | Button | Center |  |  |  |  | Manual trigger of the DAD Volume Calculation batch. Enabled only when the scheduled run has failed 3 times; otherwise disabled with message no. 17 as tooltip. Refer Operation Description 5.9. |
| 15 | Part Number | TB_M_PART_CANDIDATE | PART_NO | Varchar | TBD | O | Hyperlink | Left |  |  | X..TBD..X |  | Click opens the Edit part data modal (same as [Edit]). |
| 16 | Part Name | TB_M_PART_CANDIDATE | PART_NAME | Varchar | TBD | O | Label | Left |  |  | X..TBD..X |  | Truncated with '...' when long; full name in tooltip. |
| 17 | Min MAD | TB_M_PART_CANDIDATE | MIN_MAD | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  | Minimum MAD of the part, entered by the user. Reference value compared with the MAD result of the calculation. |
| 18 | Pcs/Case | TB_M_PART_CANDIDATE | PCS_CASE | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  |  |
| 19 | Max Case/Day | TB_M_PART_CANDIDATE | MAX_CASE_DAY | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  |  |
| 20 | Total Pcs/Day | TB_M_PART_CANDIDATE | TOTAL_PCS_DAY | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  | Calculated: Pcs/Case x Max Case/Day. |
| 21 | Status | TB_M_PART_CANDIDATE | PART_STATUS | Varchar | TBD | O | Chip | Left |  |  |  |  | Candidate (blue) / Active (green) / Inactive (grey). |
| 22 | Created Date | TB_M_PART_CANDIDATE | CREATED_DT | Datetime |  | O | Label | Left |  |  | DD-Mon-YYYY HH:MI |  | Date-time the part was registered. |
| 23 | Created By | TB_M_PART_CANDIDATE | CREATED_BY | Varchar |  | O | Label | Left |  |  |  |  | User who registered the part. |
| 24 | Updated Date | TB_M_PART_CANDIDATE | CHANGED_DT | Datetime |  | O | Label | Left |  |  | DD-Mon-YYYY HH:MI |  | Date-time of the last change of the part. |
| 25 | Updated By | TB_M_PART_CANDIDATE | CHANGED_BY | Varchar |  | O | Label | Left |  |  |  |  | User of the last change of the part. |
| 26 | Edit |  |  |  |  | I | Button | Center |  |  |  |  | Opens the Edit part data modal of the row. Shown as [View] for a read-only account (TBD: read-only accounts not defined). |
| 27 | History (clock icon) |  |  |  |  | I | Button | Center |  |  |  |  | Opens the History setting modal of the row. |
| **<Kanban Crossdock Master - Footer Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 28 | Rows per page | Key-in |  | Number |  | I | Combo Box | Left | 25 | N |  |  | Options 25 / 50 / 100. Change returns to page 1. |
| 29 | Paging information |  |  | Varchar |  | O | Label | Right |  |  | a-b of N parts · page x/y |  |  |
| 30 | Prev / Next |  |  |  |  | I | Button | Center |  |  |  |  | Previous / next page. Refer Screen Mode remark 1). |
| **<Kanban Crossdock Master - Empty State Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 31 | Empty state message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 1 (filter result empty) or no. 2 (no part registered). |
| 32 | Reset filter |  |  |  |  | I | Button | Center |  |  |  |  | Same as [Reset]. Shown with message no. 1. |
| 33 | Upload Excel / Add one part |  |  |  |  | I | Button | Center |  |  |  |  | Shown with message no. 2; same as header [Upload Excel] / [Add Part]. |
| **<Kanban Crossdock Master - Add Part / Edit Part Data Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 34 | Modal title |  |  | Varchar |  | O | Label | Left | Add: 'Add Part Candidate Crossdock'; Edit: 'Edit part data' |  |  |  |  |
| 35 | Step indicator |  |  |  |  | O | Stepper | Left | Step 1 active |  |  |  | Step 1 Part Candidate (Part No), step 2 Pcs/Case & Max Case/Day, step 3 Total Pcs/Day; a step gets a check when its items are filled. |
| 36 | Status | TB_M_PART_CANDIDATE | PART_STATUS | Varchar | TBD | I/O | Combo Box | Left | Candidate | Y |  | Add: always Candidate. Edit of a Candidate part: Candidate or Active. Edit of an Active / Inactive part: Active or Inactive | Add: locked to Candidate (tooltip 'New parts are automatically Candidate'). Edit: a Candidate part can become Active (ongoing period); an Active or Inactive part can be Active or Inactive; no part goes back to Candidate. |
| 37 | Part No | TB_M_PART_MASTER (Add) / TB_M_PART_CANDIDATE (Edit) | PART_NO | Varchar | TBD | I/O | Combo Box with search | Left | Blank | Y | X..TBD..X | Must exist in TB_M_PART_MASTER and not yet be registered (no duplicate Part No) | Add: lists parts of TB_M_PART_MASTER not yet registered (Part No + name, contains search, arrow keys / Enter / Esc). Edit: locked. |
| 38 | Part Name | TB_M_PART_MASTER | PART_NAME (TBD) | Varchar | TBD | O | Text box (disabled) | Left | Blank |  | X..TBD..X |  | Autofilled from the selected Part No. |
| 39 | Period | TB_M_PART_CANDIDATE | PERIOD | Char | 6 | I/O | Combo Box | Left | Add: the ongoing period | Y | Mon YYYY (stored YYYYMM) | Add: the ongoing period or the next period. Edit: locked | Add: the ongoing period (default) or the next period, marked (ongoing) / (next); the part takes effect from it. Edit: locked (part of the key), tooltip message no. 10. A part of the next period is view only until that period becomes the ongoing one. |
| 40 | Min MAD | TB_M_PART_CANDIDATE | MIN_MAD | Number | TBD | I | Text box | Right | Blank | Y | ZZ,ZZ9 | Mandatory; whole number, 0 or more | Minimum MAD of the part, entered by the user. Reference value compared with the MAD result of the calculation. Mandatory on Add and Edit; tooltip of disabled [Save] = message no. 15. |
| 41 | Pcs/Case | TB_M_PART_CANDIDATE | PCS_CASE | Number | TBD | I | Text box | Right | Blank | Y | ZZ,ZZ9 | Whole number > 0 |  |
| 42 | Max Case/Day | TB_M_PART_CANDIDATE | MAX_CASE_DAY | Number | TBD | I | Text box | Right | Blank | Y | ZZ,ZZ9 | Whole number > 0 | Locked until Pcs/Case is filled (tooltip 'Enter Pcs/Case first'). Edit: cannot be less than the total Case/Day already mapped in the ongoing period (TB_M_PART_CANDIDATE_DEST); otherwise the field is marked red, message no. 14 is shown and [Save] is disabled. |
| 43 | Mapped Case/Day (current period) | TB_M_PART_CANDIDATE_DEST | CASE_DAY | Number | TBD | O | Label | Left |  |  | ZZ,ZZ9 |  | Edit mode, Active parts only (Candidate / Inactive parts have no mapping). Total Case/Day of all destinations of the part in the ongoing period (' · no destination yet' when none); red when Max Case/Day is below it. Shows the lowest allowed Max Case/Day before Save. |
| 44 | Total Pcs/Day |  |  | Number |  | O | Label | Right | '-' |  | ZZ,ZZ9 |  | Calculated: Pcs/Case x Max Case/Day, recalculated on every change. |
| 45 | Cancel |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal without saving. |
| 46 | Save |  |  |  |  | I | Button | Center |  |  |  |  | Enabled only when Part No, Min MAD, Pcs/Case > 0 and Max Case/Day > 0 are filled and, in Edit, Max Case/Day is not below the mapped total. Refer Operation Description 5.4 / 5.5. |
| 47 | Close (X) |  |  |  |  | I | Button | Center |  |  |  |  | Same as [Cancel]. |
| **<Kanban Crossdock Master - History Setting Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 48 | Part identity | TB_M_PART_CANDIDATE | PART_NO, PART_NAME | Varchar |  | O | Label | Left |  |  |  |  | Part No · Part Name of the selected row. |
| 49 | Event title | TB_H_PART_CANDIDATE | TBD | Varchar |  | O | Timeline | Left |  |  |  |  | e.g. 'Part registered', 'Status changed'. Latest event marked with a blue dot. |
| 50 | Event date-time | TB_H_PART_CANDIDATE | TBD | Datetime |  | O | Label | Right |  |  | DD-Mon-YYYY HH:MI |  |  |
| 51 | Changed field (old → new) | TB_H_PART_CANDIDATE | TBD | Varchar |  | O | Label | Left |  |  |  |  | Field name, old value struck through, new value. |
| 52 | User | TB_H_PART_CANDIDATE | TBD | Varchar |  | O | Label | Right |  |  |  |  | User who made the change. |
| 53 | Close |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal. |
| **<Kanban Crossdock Master - Upload Excel Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 54 | Template columns |  |  | Varchar |  | O | Label (chips) | Left |  |  |  |  | Part Number, Min MAD, Pcs/Case, Max Case/Day, Status, Upload (A/E), Period (same names and order as sheet 'Upload' of Export Excel). |
| 55 | Rules per upload value and status |  |  | Varchar |  | O | Label | Left |  |  |  |  | Add / Edit / Status rules; Candidate status cannot be changed by upload, Active <-> Inactive allowed, nothing can become Candidate. |
| 56 | Upload file | Key-in |  | File |  | I | Drag-and-drop area + [Choose file] | Center | Blank | Y | .xlsx | Max 5 MB, max 5,000 rows | File checks and row validation are done by the batch (UISS-Batch XD02 Cross Dock Part Master Upload). |
| 57 | Download template .xlsx |  |  |  |  | I | Button | Center |  |  |  |  | Downloads the empty upload template. TBD: template file location. |
| 58 | Close |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal without uploading. |
| 59 | Validate file |  |  |  |  | I | Button | Center |  |  |  |  | Save button of the upload. Refer Operation Description 5.7. |
| **<Kanban Crossdock Master - Saved Successfully Popup>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 60 | Success message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 9 (Add / Edit) or no. 11 (upload). |
| 61 | OK |  |  |  |  | I | Button | Center |  |  |  |  | Closes the popup. |
| **<Mapping - Header Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 62 | Upload Excel (Mapping) |  |  |  |  | I | Button | Center |  |  |  |  | Page header, right (same place as on Kanban Crossdock Master). Disabled for a past period or All periods (tooltip message no. 23). Refer Operation Description 5.17. |
| 63 | Export Excel (Mapping) |  |  |  |  | I | Button | Center |  |  |  |  | Page header, right (same place as on Kanban Crossdock Master). Refer Operation Description 5.18. |
| **<Mapping - Search Criteria Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 64 | Calculation period | Key-in |  | Varchar |  | I | Combo Box | Left | Ongoing period, e.g. 'Sep 2026 (ongoing)' | N | Mon YYYY |  | Options: All periods / every calculation period; the ongoing one is marked '(ongoing)', the next one '(next)'. The label shows (ongoing) / (past) / (all). Calculation periods are created by the calculation batch; the latest period created is the ongoing period and earlier ones become past. A new period starts empty: the mapping of the previous period is not copied. Every Active part is listed with its Max Case/Day from Kanban Crossdock Master (the quota) but no destination yet (Total Case/Day 0, 0%), until the D/S user assigns it by Edit mapping or Upload Excel. |
| 65 | Part Number | Key-in |  | Varchar | TBD | I | Text box with suggestion list | Left | Blank | N | X..TBD..X | Contains, case-insensitive | Suggestions = registered Part Numbers. Placeholder 'e.g. PART-B'. Combined with the other criteria by AND. |
| 66 | Sync Status | Key-in |  | Varchar |  | I | Combo Box | Left | Non Sync | N |  |  | Options: All / Non Sync / Sync. Non Sync = the part + period has a staging row with AP POLE or GTOPAS Non Sync. |
| 67 | Reset |  |  |  |  | I | Button | Center |  |  |  |  | Returns every criterion to its initial value (Calculation period = ongoing, Sync Status = Non Sync). |
| 68 | Search |  |  |  |  | I | Button | Center |  |  |  |  | Applies the criteria to the result list. Typing or selecting a criterion alone does not change the list; Enter in a text box = [Search]. |
| **<Mapping - Result List Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 69 | Section title |  |  | Varchar |  | O | Label | Left | 'Destination mapping per part' |  |  |  |  |
| 70 | Last mapping calculation |  |  | Datetime |  | O | Label | Left |  |  | DD-Mon-YYYY HH:MM |  | Date-time of the last successful run of process 2 (mapping destination) of the XD05 DAD Volume Calculation batch (one date per batch run). |
| 71 | Failed badge |  |  | Varchar |  | O | Label | Left |  |  |  |  | 'Scheduled run failed 3x'; shown when the scheduled run and its 3 auto retries have failed. |
| 72 | Run calculation (Mapping) |  |  |  |  | I | Button | Center |  |  |  |  | Manual trigger of process 2 (mapping destination) of the XD05 DAD Volume Calculation batch. Refer Operation Description 5.19 and Screen Mode remark 8). |
| 73 | Sync (n) |  |  |  |  | I | Button | Center |  |  |  |  | n = parts + periods with a row SYNC_STATUS 0 in the staging tables (AP POLE: Current and Next; GTOPAS: Current), whatever the filter. Disabled when n = 0. Refer Operation Description 5.24. |
| 74 | Period | TB_M_PART_CANDIDATE_DEST | PERIOD | Char | 6 | O | Label | Left |  |  | Mon YYYY |  | Calculation period of the row. Stored as YYYYMM (e.g. 202609), displayed as Mon YYYY. |
| 75 | Expand (arrow) |  |  |  |  | I | Button | Center |  |  |  |  | Opens / closes the Destination Mapping panel of the row. |
| 76 | Part Number | TB_M_PART_CANDIDATE | PART_NO | Varchar | TBD | O | Label | Left |  |  | X..TBD..X |  | Tooltip: Part Name (PART_NAME of TB_M_PART_CANDIDATE). |
| 77 | Pcs/Case | TB_M_PART_CANDIDATE | PCS_CASE | Number | TBD | O | Label | Right |  |  | ZZ,ZZ9 |  |  |
| 78 | Used/Quota (Case) | TB_M_PART_CANDIDATE_DEST / TB_M_PART_CANDIDATE | SUM(CASE_DAY) / MAX_CASE_DAY | Number |  | O | Label | Right |  |  | ZZ,ZZ9 / ZZ,ZZ9 |  | Used (bold) = sum of Case/Day of all destinations of the part and period; quota = Max Case/Day of the part in Kanban Crossdock Master. |
| 79 | Pcs/Day |  |  | Number |  | O | Label | Right |  |  | ZZ,ZZ9 |  | Calculated: Pcs/Case x Total Case/Day. |
| 80 | Percentage |  |  | Number |  | O | Label | Right |  |  | ZZ9% |  | Calculated: Total Case/Day / Max Case/Day (MAX_CASE_DAY). Never above 100%: Save, upload and the Max Case/Day edit in Kanban Crossdock Master are blocked above the limit. |
| 81 | AP POLE Status | TB_H_STG_APPOLE_KANBAN / TB_H_STG_APPOLE_EXPORT | SYNC_STATUS (derived) | Varchar |  | O | Chip | Left |  |  |  |  | Status of the part + period for AP POLE (Kanban or Export staging). 'Non Sync' = amber chip with a dot (a row waits for [Sync]); 'Sync' = check mark with green text (every row sent); 'Not sent' = grey text (no staging row for the target yet). Tooltip: the state and the last send time (latest SYNC_DT). Refer 5.24. |
| 82 | GTOPAS Status | TB_H_STG_GTOPAS | SYNC_STATUS (derived) | Varchar |  | O | Chip | Left |  |  |  |  | Status of the part + period for GTOPAS (GTOPAS staging). 'Non Sync' = amber chip with a dot (a row waits for [Sync]); 'Sync' = check mark with green text (every row sent); 'Not sent' = grey text (no staging row for the target yet). Tooltip: the state and the last send time (latest SYNC_DT). Refer 5.24. |
| **<Mapping - Footer Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 83 | Rows per page | Key-in |  | Number |  | I | Combo Box | Left | 25 | N |  |  | Options 25 / 50 / 100. Change returns to page 1. |
| 84 | Paging information |  |  | Varchar |  | O | Label | Right |  |  |  |  | '{from}-{to} of {n} parts · page {p}/{total}'. |
| 85 | Prev / Next |  |  |  |  | I | Button | Center |  |  |  |  | Previous / next page. Refer Screen Mode remark 7). |
| **<Mapping - Empty State Section>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 86 | Empty state message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 18. |
| **<Mapping - Destination Mapping Panel>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 87 | Allocation note |  |  | Varchar |  | O | Label | Left |  |  |  |  | 'no destination yet' / '{n} case/day over' / '{n} case/day left' / 'capacity fully allocated'. |
| 88 | Past period badge |  |  | Varchar |  | O | Badge | Left |  |  |  |  | Display message no. 22; shown instead of [Edit mapping] for a period that is not ongoing. |
| 89 | Split evenly |  |  |  |  | I | Button | Center |  |  |  |  | Refer Operation Description 5.15. |
| 90 | Edit mapping |  |  |  |  | I | Button | Center |  |  |  |  | Shown only for the ongoing period. |
| 91 | Cancel |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode; discards the changes. |
| 92 | Save |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode. Disabled while the mapping cannot be saved (Operation Description 5.15). |
| 93 | Destination (CD) | TB_M_PART_CANDIDATE_DEST | DEST_CODE | Varchar | TBD | I/O | Combo Box | Left | New row: 'Select destination' | Y | XXXXXXX - X..X | Destination + Order Type once per part | List = DESTINATION_CD - DESTINATION_NAME of TB_M_H0125_DESTINATION (Destination Master) (e.g. 9722D10 - Thailand, 9811110 - Philippines, 9715310 - Vietnam). The same destination may be chosen again with another Order Type. |
| 94 | Order Type | TB_M_PART_CANDIDATE_DEST | ORDER_TYPE | Varchar | 2 | I/O | Combo Box | Left | New row: '**' | Y | XX | '**', 'C', '9', 'V' (system master). Destination + Order Type once per part (message no. 31) | Order Type of the destination row, shown in view and edit mode; editable in edit mode only. The same destination may have two rows when the order type differs. |
| 95 | Case/Day | TB_M_PART_CANDIDATE_DEST | CASE_DAY | Number | TBD | I/O | Text box | Right | New row: 0 | Y | ZZ,ZZ9 | Whole number (TBD: upper limit) | Editable in edit mode only. |
| 96 | Pcs/Day |  |  | Number |  | O | Label | Right |  |  | ZZ,ZZ9 |  | Calculated: Pcs/Case x Case/Day of the destination. |
| 97 | Percentage |  |  | Number |  | O | Label | Right |  |  | ZZ9% |  | Calculated: Case/Day of the destination / total Case/Day of the part. |
| 98 | Remove destination (trash icon) |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode on every row. |
| 99 | Add destination |  |  |  |  | I | Button | Center |  |  |  |  | Shown in edit mode, with the hint 'New row: pick a destination from the destination master in the Destination (CD) column.' |
| 100 | No destination message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 19; shown when the part has no destination. |
| 101 | Validation banner |  |  | Varchar |  | O | Banner | Left |  |  |  |  | Display message no. 20 (over allocation) or no. 4 (row without destination). |
| **<Mapping - Upload Excel Modal>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 102 | Template columns |  |  | Varchar |  | O | Label (chips) | Left |  |  |  |  | Part Number, Destination Code, Dest Case/Day, Total Case/Day (used), Max Case/Day (quota), Upload (A/E) (same names and order as sheet 'Upload' of Export Excel). |
| 103 | Upload rules |  |  | Varchar |  | O | Label | Left |  |  |  |  | Rows / Replace / Limits / Base rules. Refer Operation Description 5.17. |
| 104 | Upload file | Key-in |  | File |  | I | Drag-and-drop area + [Choose file] | Center | Blank | Y | .xlsx | Max 5 MB, max 5,000 rows | File checks and row validation are done by the batch (UISS-Batch XD03 Part and Destination Mapping Upload). |
| 105 | Download template .xlsx |  |  |  |  | I | Button | Center |  |  |  |  | Downloads the empty upload template. TBD: template file location. |
| 106 | Close |  |  |  |  | I | Button | Center |  |  |  |  | Closes the modal without uploading. |
| 107 | Validate file |  |  |  |  | I | Button | Center |  |  |  |  | Save button of the upload. Refer Operation Description 5.17. |
| **<Mapping - Saved Successfully Popup>** |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 108 | Success message |  |  | Varchar |  | O | Label | Center |  |  |  |  | Display message no. 24. |
| 109 | OK |  |  |  |  | I | Button | Center |  |  |  |  | Closes the popup. |

## 5. Data edit mapping

#### 1. Insert TB_M_PART_CANDIDATE – Add Part modal - [Save]
- Source: Key-in from screen

| Source field | Destination field | Description |
|---|---|---|
| Part No | PART_NO |  |
| Period (Add Part) | PERIOD | Selected period: the ongoing period (default) or the next one |
| Part Name | PART_NAME | From TB_M_PART_MASTER by PART_NO |
| Min MAD | MIN_MAD | Mandatory; entered by the user |
| Pcs/Case | PCS_CASE |  |
| Max Case/Day | MAX_CASE_DAY |  |
|  | TOTAL_PCS_DAY | PCS_CASE x MAX_CASE_DAY |
|  | PART_STATUS | 'Candidate' (every new part) |
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
|  | LAST_SOURCE | 'SCREEN' |
|  | CHANGED_BY | Login user ID |
|  | CHANGED_DT | Server system date-time |

#### 3. Insert TB_H_PART_CANDIDATE – Add / Edit - [Save]
- Source: TB_M_PART_CANDIDATE (keys: PART_NO = Saved part)

| Source field | Destination field | Description |
|---|---|---|
|  | HIST_ID | Auto (identity) |
|  | PART_NO | Part of the event |
|  | PERIOD | NULL (Kanban Crossdock Master has no period) |
|  | EVENT_TYPE | 'ADD' (Add Part) / 'EDIT' (Edit part data) |
|  | SOURCE | 'SCREEN' |
|  | UPLOAD_ID | NULL |
|  | DEST_CODE | NULL |
| ORDER_TYPE | ORDER_TYPE | Order Type of the destination row for MAPPING; NULL for other events |
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
| ORDER_TYPE | ORDER_TYPE | Key of the row (not changed) |
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
| Order Type | ORDER_TYPE | Order Type of the row ('**', 'C', '9', 'V'; default '**') |
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
| ORDER_TYPE | ORDER_TYPE | Key of the row to delete |
|  | CASE_DAY | Row is deleted |

#### 7. Insert TB_H_PART_CANDIDATE – Edit mapping - [Save]
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
| ORDER_TYPE | ORDER_TYPE | Order Type of the destination row for MAPPING; NULL for other events |
|  | FIELD_NAME | 'CASE_DAY' |
|  | OLD_VALUE | Case/Day before (NULL when added) |
|  | NEW_VALUE | Case/Day after (NULL when removed) |
|  | REMARK | NULL |
|  | CREATED_BY | Login user ID |
|  | CREATED_DT | Server system date and time |

#### 8. Insert TB_H_STG_APPOLE_KANBAN – SP_STG_WRITE (KANBAN): changed Pcs/Case or Max Case/Day of an Active part, Candidate -> Active, part of a new period; header 5 when only the destinations changed (when the key has no unsent row yet)
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Identity |
| PERIOD | PERIOD | Period of the part row |
| - | ACTION | 'ADD' (new part, new period) / 'EDIT' / 'KEEP' (header 5) |
| PART_STATUS | PART_STATUS | Status of the part in the period |
| - | OPERATOR_ID | 'P6' |
| PART_NO | PART_NO | With "-" |
| PART_NAME | PART_NAME | From TB_M_PART_CANDIDATE |
| PCS_CASE | SHIPPING_BOX_QTY | Value after the change |
| MAX_CASE_DAY | MAX_SHIPPING_BOX_QTY | Value after the change |
| - | MAX_ALLOWANCE_QTY | PCS_CASE x MAX_CASE_DAY |
| - | OPERATION_TYPE | 1 Max down / 2 up / 3 same / 4 never sent, against the last Max sent (same period, else the latest earlier period); 5 header |
| - | SOURCE | 'SCREEN' / 'UPLOAD' / 'BATCH' (caller) |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD, else NULL |
| - | SYNC_STATUS | '0' |
| - | SYNC_DT | NULL |
| - | CREATED_BY | Login user (XD05: batch user ID) |
| - | CREATED_DT | Server date-time |
| - | CHANGED_BY | NULL |
| - | CHANGED_DT | NULL |

#### 9. Insert TB_H_STG_APPOLE_EXPORT – SP_STG_WRITE (EXPORT): one row per added, changed or removed destination + order type (when the key has no unsent row yet)
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Identity |
| PERIOD | PERIOD |  |
| PART_NO | NSP_PART_NO | With "-" |
| DEST_CODE | DEST_CODE | 7 digits |
| - | ACTION | 'ADD' / 'EDIT' / 'DELETE' |
| PART_NO | PART_NO | Without "-" |
| DEST_CODE | BUYER_PD | 5-2 format |
| ORDER_TYPE | ORDER_TYPE |  |
| - | TRANSPORT_CODE | '2' |
| CASE_DAY | MAX_SHIPPING_BOX_RCS | Value after the change; 0 for DELETE |
| - | SOURCE | 'SCREEN' / 'UPLOAD' / 'BATCH' (caller) |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD, else NULL |
| - | SYNC_STATUS | '0' |
| - | SYNC_DT | NULL |
| - | CREATED_BY | Login user (XD05: batch user ID) |
| - | CREATED_DT | Server date-time |
| - | CHANGED_BY | NULL |
| - | CHANGED_DT | NULL |

#### 10. Insert TB_H_STG_GTOPAS – SP_STG_WRITE (EXPORT branch): the destination appears or disappears for the part and GTOPAS does not have that state yet (when the key has no unsent row yet)
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Identity |
| PERIOD | PERIOD |  |
| - | ACTION | 'ADD' / 'DELETE' |
| - | DEPOT_CODE | '01' |
| PART_NO | P_NO | With "-" |
| DEST_CODE | DESTINATION_CODE |  |
| - | MAKER_CODE | 'A' |
| - | DOMESTIC_OVERSEAS | '2' |
| - | TOPAS_ORDER_TYPE | '3' |
| - | ORDER_TRANSPORTATION_CODE | '2' |
| - | SOURCE | 'SCREEN' / 'UPLOAD' / 'BATCH' (caller) |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD, else NULL |
| - | SYNC_STATUS | '0' |
| - | SYNC_DT | NULL |
| - | CREATED_BY | Login user (XD05: batch user ID) |
| - | CREATED_DT | Server date-time |
| - | CHANGED_BY | NULL |
| - | CHANGED_DT | NULL |

#### 11. Update TB_H_STG_APPOLE_KANBAN – SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | ACTION | 'EDIT' (ADD when the key was not sent in the period) |
| - | PART_STATUS | Status of the part |
| - | SHIPPING_BOX_QTY | New Pcs/Case |
| - | MAX_SHIPPING_BOX_QTY | New Max Case/Day |
| - | MAX_ALLOWANCE_QTY | Pcs/Case x Max Case/Day |
| - | OPERATION_TYPE | Again against the last Max sent (a header 5 becomes 1 to 4) |
| - | SOURCE | Caller of the last change |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD |
| - | CHANGED_BY | Login user (XD05: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 12. Delete TB_H_STG_APPOLE_KANBAN – SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period (Kanban: also the header 5 when no Export row of the part + period waits)
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Unsent row (SYNC_STATUS 0) of the key |

#### 13. Update TB_H_STG_APPOLE_EXPORT – SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | ACTION | 'ADD' / 'EDIT' / 'DELETE' against the last value sent |
| - | MAX_SHIPPING_BOX_RCS | New Case/Day; 0 for DELETE |
| - | SOURCE | Caller of the last change |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD |
| - | CHANGED_BY | Login user (XD05: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 14. Delete TB_H_STG_APPOLE_EXPORT – SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Unsent row (SYNC_STATUS 0) of the key |

#### 15. Update TB_H_STG_GTOPAS – SP_STG_WRITE: a new change of a key that already has an unsent row (SYNC_STATUS 0) updates that row
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | ACTION | 'ADD' / 'DELETE' (what the master needs) |
| - | SOURCE | Caller of the last change |
| - | UPLOAD_ID | Upload ID when SOURCE = UPLOAD |
| - | CHANGED_BY | Login user (XD05: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 16. Delete TB_H_STG_GTOPAS – SP_STG_WRITE: the unsent row of the key when the value is back to the value already sent for the period
- Source: Key-in from screen (SP_STG_WRITE)

| Source field | Destination field | Description |
|---|---|---|
| - | STG_ID | Unsent row (SYNC_STATUS 0) of the key |

#### 17. Update TB_H_STG_APPOLE_KANBAN – [Sync]: rows with SYNC_STATUS 0 (AP POLE: Current + Next, GTOPAS: Current)
- Source: [Sync] (SP_STG_SYNC)

| Source field | Destination field | Description |
|---|---|---|
| - | SYNC_STATUS | '1' |
| - | SYNC_DT | Time of the [Sync] click / of the rollover: one value for every row of the run |
| - | CHANGED_BY | Login user (rollover: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 18. Update TB_H_STG_APPOLE_EXPORT – [Sync]: rows with SYNC_STATUS 0 (AP POLE: Current + Next, GTOPAS: Current)
- Source: [Sync] (SP_STG_SYNC)

| Source field | Destination field | Description |
|---|---|---|
| - | SYNC_STATUS | '1' |
| - | SYNC_DT | Time of the [Sync] click / of the rollover: one value for every row of the run |
| - | CHANGED_BY | Login user (rollover: batch user ID) |
| - | CHANGED_DT | Server date-time |

#### 19. Update TB_H_STG_GTOPAS – [Sync]: rows with SYNC_STATUS 0 (AP POLE: Current + Next, GTOPAS: Current)
- Source: [Sync] (SP_STG_SYNC)

| Source field | Destination field | Description |
|---|---|---|
| - | SYNC_STATUS | '1' |
| - | SYNC_DT | Time of the [Sync] click / of the rollover: one value for every row of the run |
| - | CHANGED_BY | Login user (rollover: batch user ID) |
| - | CHANGED_DT | Server date-time |

## 6. Operation description

5.1 - 5.10: Kanban Crossdock Master tab. 5.11 - 5.20: Export Crossdock Master tab. 5.25: table changes of every save.

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
  1. Open the 'Add Part Candidate Crossdock' modal. 'Status' = Candidate and locked (a new part is always Candidate); 'Period' = the ongoing period (default) or the next period: the part takes effect from it.
  2. 'Part No' lists only parts of TB_M_PART_MASTER that are not registered in TB_M_PART_CANDIDATE yet, so a part cannot be registered twice.
  3. Selecting a Part No autofills 'Part Name'. 'Max Case/Day' is locked until 'Pcs/Case' is filled.
  4. [Save] is enabled only when Part No, Min MAD (whole number, 0 or more), Pcs/Case > 0 and Max Case/Day > 0 are filled; otherwise its tooltip shows message no. 5, 15, 6 or 7 for the first missing item.

- b. User clicks [Save].
  1. If the Part No was registered by another user in the meantime, display message no. 3. Stop.
  2. Insert the part into TB_M_PART_CANDIDATE with PART_STATUS = Candidate and PERIOD = the selected period. When the ongoing period is selected and XD05 has already made the next period (between day D and the Period Rollover), insert the same row for the next period too, so the next XD05 run calculates the part. A Candidate part is not sent (no staging row).
  3. Insert the change history in TB_H_PART_CANDIDATE (refer 5.6).
  4. Close the modal, reset the Part Number / Part Name / Status filters, sort Newer to Older and display message no. 9. The new part is shown at the top. Table changes: refer 5.25.

- c. User clicks [Cancel] or the X icon: close the modal without saving.

### 5.5 Edit Part Data

- a. User clicks the 'Part Number' link or [Edit] on a row.
  1. Open the 'Edit part data' modal with the saved values. 'Part No' and 'Period' are locked. 'Status': a Candidate part can stay Candidate or become Active; an Active or Inactive part can be Active or Inactive; no part goes back to Candidate.
  2. Only rows of the ongoing period can be edited. A part registered for the next period has no [Edit] until its period becomes the ongoing period.
  3. 'Min MAD' (mandatory, whole number 0 or more), 'Pcs/Case' and 'Max Case/Day' can be changed; 'Total Pcs/Day' is recalculated.
  4. Active part only: below Max Case/Day show 'Mapped Case/Day (current period): n' = total Case/Day of the part in TB_M_PART_CANDIDATE_DEST for the ongoing period (' · no destination yet' when none), so the user sees the lowest allowed Max Case/Day before Save.
  5. Max Case/Day cannot be less than the total Case/Day already mapped to destinations in the ongoing period (TB_M_PART_CANDIDATE_DEST); otherwise the field is marked red, message no. 14 is shown below Pcs/Case & Max Case/Day and [Save] is disabled. The user must first reduce the mapping in Export Crossdock Master (same rule as upload check 9).

- b. User clicks [Save].
  1. If the record was changed by another user after it was opened, display message no. 4. Stop.
  2. Check Max Case/Day against the mapped total of the ongoing period again on the server; if it is below, display message no. 14. Stop.
  3. Update TB_M_PART_CANDIDATE, CHANGED_BY and CHANGED_DT. Active -> Inactive also deletes the mapping of the period (TB_M_PART_CANDIDATE_DEST). Call SP_STG_WRITE for the staging rows (refer 5.24 and 5.25).
  4. Insert the change history in TB_H_PART_CANDIDATE (refer 5.6).
  5. Close the modal, move the part to the top of the list and display message no. 9. Table changes: refer 5.25.

### 5.6 History Setting

a. The history comes from the records inserted when a user adds or changes a part.
b. User clicks the clock icon on a row: open 'History setting' with the change timeline of the part, newest first.
c. Each event shows the title, date-time, field name, old value (struck through) → new value and user.
d. History is read from TB_H_PART_CANDIDATE, which records every change of the part: Add / Edit by screen, Upload, mapping changes (add, change or remove a destination) and the calculation. The sync is in the staging tables (not shown here). A part without history shows message no. 12.

TB_H_PART_CANDIDATE (proposed) - one record per changed field, insert only:

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | Y | Calculation period YYYYMM for MAPPING / CALC; NULL for ADD / EDIT (Kanban Crossdock Master has no period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, CASE_DAY |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (batch user ID for BATCH) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

Events: ADD / EDIT (source SCREEN or UPLOAD), MAPPING (source SCREEN or UPLOAD, PERIOD and DEST_CODE filled, FIELD_NAME CASE_DAY), CALC (source BATCH, FIELD_NAME PART_STATUS, status set by the DAD Volume Calculation) and MAPPING with source BATCH (XD05 process 2). The sync is not recorded here (refer 5.24).

Retention: the history of a part is kept; there is no housekeeping job.

### 5.7 Upload Excel

a. User clicks [Upload Excel]: open the modal with the template columns, the rules and the file area (.xlsx, max 5 MB, max 5,000 rows).
b. Edit rows use sheet 'Upload' of the Kanban Crossdock Master Export Excel as base file (pre-filled with Upload (A/E) = E). Sample: sheet 'Upload Kanban Crossdock Master'.
c. Status rule: a Candidate part's status cannot be changed by upload; Active <-> Inactive can be changed; no part can be changed to Candidate.
d. User clicks [Validate file] (save button of the upload): the file is passed to the upload batch; validation, saving (all-or-nothing) and logging follow UISS-Batch "XD02 Cross Dock Part Master Upload Batch".
e. When the upload is completed, close the modal and display message no. 11. When it is rejected, show the batch result (error list) - refer UISS-Batch.
f. Changed parts get staging rows and show Sync Status Non Sync.

### 5.8 Export Excel

a. User clicks [Export Excel]: download Crossdock_Kanban_Master_YYYYMMDD.xlsx.
b. Sheet 'Kanban Crossdock Master': rows of the active filter and sort (all pages) with Part Number, Part Name, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, Status, CREATED_DT, CREATED_BY, UPDATED_DT, UPDATED_BY. Information only. Sample: 'Export Kanban Crossdock Master'.
c. Sheet 'Upload': every registered part, columns as sheet 1 (Part Number, Min MAD, Pcs/Case, Max Case/Day, Status, Upload (A/E) = E, Period YYYYMM). Base file for Edit uploads.
d. If the file cannot be created, display message no. 13.

### 5.9 Run DAD Calculation

a. The DAD Volume Calculation batch runs on its own scheduler (set in system master) with 3 auto retries. It compares the average MAD of each part with Min MAD and sets the part status to Active or Inactive (refer UISS-Batch XD05 DAD Volume Calculation (process 1)).
b. The result list header shows 'Last DAD calculation' (last successful run) and, when the scheduled run and its 3 retries have failed, the badge 'Scheduled run failed 3x'.
c. [Run calculation] is enabled only in that failed state; otherwise it is disabled with message no. 17 as tooltip.
d. User clicks [Run calculation]: start the batch. When it completes, update 'Last DAD calculation', hide the badge, refresh the list and display message no. 16. When it fails, the batch logs the error (all-or-nothing) and the button stays enabled.
e. XD05 writes the staging rows of the new period through SP_STG_WRITE (refer UISS-Batch XD05 4.11); a change from Active to Inactive gives Export DELETE rows (0), so the part is sent by the next [Sync].

### 5.10 Status Definitions

| Status | Value | Definition |
|---|---|---|
| Part Status | Candidate | Newly registered part without MAD history. Initial status of every new part; cannot be chosen when adding. |
| Part Status | Active | Active part. Only Active parts can be mapped in the Export Crossdock Master sub-menu. |
| Part Status | Inactive | Inactive part. Not mapped in the Export Crossdock Master sub-menu. |
| Sync Status | Non Sync | The part + period has a row with SYNC_STATUS 0 in the AP POLE staging (Kanban, Export) or in the GTOPAS staging. |
| Sync Status | Sync | Every staging row of the part + period is sent (Last Sent = latest send time of the target). |

Active and Inactive parts are synchronised (not Candidate). A Save after [Sync] writes new staging rows: the part is Non Sync again until the next [Sync].

Sync Status rule: a part becomes Non Sync when SP_STG_WRITE writes a staging row, that is when a value AP POLE or GTOPAS holds changes: Pcs/Case or Max Case/Day (Kanban), a destination or its Case/Day (Export; GTOPAS only when a destination appears or disappears), Active -> Inactive (Export DELETE 0). Min MAD, a Candidate part and a save without change write no row.

| Change | Staging rows | Target |
|---|---|---|
| Status Candidate -> Active (screen, ongoing period, or XD05) | Kanban ADD, OPERATION_TYPE 4 (2 or 3 when the part was sent before) | Add in AP POLE; GTOPAS when mapped |
| Status Active -> Inactive (screen, upload or XD05) | Export DELETE (0) per destination, Kanban header 5, GTOPAS DELETE | Delete in GTOPAS; AP POLE Buyer-PD 0 (the part stays in the Kanban) |
| Status Inactive -> Active | Kanban EDIT only when Pcs/Case or Max changes; Export ADD when the destinations are mapped again | Add again |
| Pcs/Case or Max Case/Day of an Active part | Kanban EDIT, OPERATION_TYPE 1 / 2 / 3 | AP POLE Kanban; GTOPAS keeps (no quantity) |
| Destination or Case/Day of the mapping | Export ADD / EDIT / DELETE; GTOPAS when a destination appears or disappears; Kanban header 5 | AP POLE Export; GTOPAS Add / Delete |
| Min MAD | No row | Not sent to any target |
| Candidate part (Add, Edit) | No row | Never in GTOPAS / AP POLE |
| Save without change | No row | Nothing to send |

### 5.11 Initial Display

a. The sub-menu is opened only for users logged in with a D/S account.
b. Search criteria: 'Calculation period' = ongoing period, 'Part Number' blank, 'Sync Status' = Non Sync.
c. Ongoing period: list every Active part of TB_M_PART_CANDIDATE, with its destinations of TB_M_PART_CANDIDATE_DEST for that period (a part without destinations is listed with Total Case/Day 0).
d. A new period starts empty: the mapping of the previous period is not copied. Every Active part is listed with its Max Case/Day from Kanban Crossdock Master (the quota) but no destination yet (Total Case/Day 0, 0%), until the D/S user assigns it by Edit mapping or Upload Excel.
e. Past period: list every part that has rows in TB_M_PART_CANDIDATE_DEST for that period, whatever its current status. 'All periods' lists both.

### 5.12 Specifying Criteria

a. The criteria are applied when the user clicks [Search] (or presses Enter in 'Part Number'); changing a criterion alone does not change the list.
b. 'Part Number' matches by 'contains', case-insensitive; 'Calculation period' and 'Sync Status' match exactly. All criteria are combined with AND.
c. [Upload Excel] and Export Excel follow the period of the applied criteria.
d. If no row matches, hide the table and display message no. 18.
e. With the default Sync Status = Non Sync, parts already sent are hidden until the filter is changed.

### 5.13 Result List

a. Total Case/Day = used / quota (sum of CASE_DAY of the part and period / Max Case/Day); Pcs/Day = Pcs/Case x used.
b. Percentage = Total Case/Day / Max Case/Day; it never exceeds 100% because the total cannot go above Max Case/Day (Save, upload and the Max Case/Day edit in Kanban Crossdock Master are blocked).
c. The list is paged: 25 rows per page by default (25 / 50 / 100), with paging information and [Prev] / [Next]. A part with its Destination Mapping panel counts as one row. [Search], Reset and a change of Rows per page return to page 1.

### 5.14 Destination Mapping Panel

a. User clicks the arrow on a row: open the panel with the allocation note and the destination table (Destination, Case/Day, Pcs/Day, Percentage). All items are read only.
b. Ongoing period: show [Edit mapping]. Past period: show message no. 22 instead; the mapping cannot be changed.
c. A part without destination shows message no. 19.

### 5.15 Edit Mapping

- a. User clicks [Edit mapping].
  1. Copy the mapping into a draft; Destination and Case/Day become editable, a trash icon appears per row and [Add destination] is shown.
  2. The Destination list hides destinations already used by another row of the same part (one destination per part).
  3. [Add destination] adds a row with 'Select destination' and Case/Day 0.
  4. [Split evenly] (more than one row): Case/Day of each row = floor(Max Case/Day / number of rows); the remainder is added +1 per row from the first row. Example 24 / 3 = 8 / 8 / 8; 25 / 3 = 9 / 8 / 8.
  5. The allocation note is recalculated on every change.

- b. Save rules - [Save] is disabled while:
  - the total Case/Day is above Max Case/Day (show message no. 20);
  - the part has no destination row; or
  - a row has no destination selected (show message no. 21);
  - the same destination + order type is used twice (show message no. 31).
  - A total below or equal to Max Case/Day is allowed; below is shown as '{n} case/day left'.

- c. User clicks [Save].
  1. If the mapping was changed by another user after edit mode started, display message no. 25. Stop.
  2. Save the draft per destination in TB_M_PART_CANDIDATE_DEST: update the Case/Day of a kept one, insert a new one, delete a removed one (refer Data Edit Mapping).
  3. Call SP_STG_WRITE per added, changed or removed destination: Export ADD / EDIT / DELETE (0), a GTOPAS row when the destination appears or disappears for the part, the Kanban header (OPERATION_TYPE 5) when the Kanban did not change (refer 5.24). A Save without change writes no row. The total Case/Day may not exceed Max Case/Day (message no. 20).
  4. Insert a history record per added, changed or removed destination in TB_H_PART_CANDIDATE (event MAPPING, source SCREEN, DEST_CODE, FIELD_NAME CASE_DAY, old / new Case/Day).
  5. Leave edit mode and show the saved mapping. Table changes: refer 5.25.

- d. User clicks [Cancel] or closes the panel: discard the draft.

### 5.16 Sync

- a. User clicks [Sync (n)] (on demand).
  1. Call SP_STG_SYNC (refer 5.24): the AP POLE rows of the Current and Next period and the GTOPAS rows of the Current period with SYNC_STATUS 0 get SYNC_STATUS 1 and SYNC_DT = time of the click (one value for the click). Candidate parts are never sent.
  2. Start the RPA parent flow with SYNC_DT (refer UISS-Batch XD06 / XD07). Display message no. 27.
  3. With the default filter Non Sync the parts leave the list; select Sync Status = Sync or All to see them.

- b. Interface functions (one per target system; refer UISS-Batch XD06 and XD07).
  1. The parent flow checks the run: with GTOPAS rows (a part becomes Active or Inactive, a destination is added or removed) XD06 runs first and XD07 starts only when GTOPAS succeeded; without GTOPAS rows XD07 runs at once.
  2. XD06 adds or deletes the part + destination rows of the run on GTOPAS WVJA5204. XD07 uploads the files of the run from the views V_APPOLE_UPLOAD_EXPORT / _KANBAN in the order EXPORT_PRE, KANBAN, EXPORT_POST.
  3. The bots write nothing back to NSP; the result comes by the notification e-mail (SUCCESS / FAILED).

- c. When the e-mail says FAILED, the D/S team clicks [Re-send last Sync]: the rows of the last run (latest SYNC_DT) are sent again in the same order (the bot sets values, so a repeat is safe).
- d. Interface method: one Power Automate parent flow per run starts XD06 (RPA on GTOPAS WVJA5204) and XD07 (RPA upload of LLM9Q880 / LLM9Q910 to AP POLE); the RPA reads only the staging tables and the views (refer UISS-Batch XD06 / XD07).

### 5.17 Upload Excel

a. [Upload Excel] is enabled only when the ongoing calculation period is selected; otherwise it is disabled with message no. 23 as tooltip.
b. The modal shows the 6 template columns (as sheet 'Upload' of Export Excel), the upload rules and the file area (.xlsx, max 5 MB, max 5,000 rows).
c. Base file: sheet 'Upload' of Export Excel with the ongoing period selected. A part in the file gets its mapping updated per destination (refer XD03); parts not in the file are not changed.
d. User clicks [Validate file] (save button of the upload): the file is passed to the upload batch; validation, saving (all-or-nothing) and logging follow UISS-Batch "XD03 Part and Destination Mapping Upload Batch". Template sample: sheet 'Upload Mapping'.
e. When the upload is completed, close the modal and display message no. 24. When it is rejected, show the batch result (error list) - refer UISS-Batch.
f. Changed parts get staging rows and show Sync Status Non Sync.

### 5.18 Export Excel

a. User clicks [Export Excel]: download Crossdock_Export_Master_<period>_YYYYMMDD.xlsx (<period> e.g. Sep_2026 or All_periods).
b. Sheet 'Export Crossdock Master': rows of the active filter, one row per destination (a part without destination gives one row with blank destination columns). Columns: Period, Part Number, Part Name, Destination Code, Order Type, Pcs/Case, Dest Case/Day, Total Case/Day (used), Max Case/Day (quota), Dest Pcs/Day, Pcs/Day, Sync Status AP POLE, Sync Status GTOPAS, Last Sent AP POLE, Last Sent GTOPAS, CREATED_DT, CREATED_BY, UPDATED_DT, UPDATED_BY (audit of the mapping row). Information only. Sample: sheet 'Export Mapping'.
c. Sheet 'Upload': every Active part of the ongoing period, columns Part Number, Destination Code, Dest Case/Day, Total Case/Day (used), Max Case/Day (quota), Upload (A/E); one row per destination, and one blank row (Upload (A/E) = A) for a part without mapping. Empty for a past period or All periods. Upload (A/E) = E for a mapped destination.
d. If the file cannot be created, display message no. 26.

### 5.19 Run Mapping Calculation

a. The XD05 process 2 (mapping destination) batch runs on its own scheduler (set in system master) with 3 auto retries. It creates the new calculation period and its destination mapping (refer UISS-Batch XD05 DAD Volume Calculation (process 2)).
b. The section header shows 'Last mapping calculation' (last successful run) and, when the scheduled run and its 3 retries have failed, the badge 'Scheduled run failed 3x'.
c. [Run calculation] is enabled only in that failed state; otherwise it is disabled with message no. 30 as tooltip.
d. User clicks [Run calculation]: start the batch. When it completes, update 'Last mapping calculation', hide the badge and display message no. 29. When it fails, the batch logs the error (all-or-nothing) and the button stays enabled.

### 5.20 Data Level and Status Definitions

| Item | Value | Definition |
|---|---|---|
| Table | TB_M_PART_CANDIDATE | Kanban Crossdock Master data, part number + period level (key PART_NO, PERIOD). Holds Pcs/Case, Max Case/Day and status. |
| Table | TB_M_PART_CANDIDATE_DEST | Mapping data, part number + calculation period + destination level (key PART_NO, PERIOD, DEST_CODE). PERIOD = CHAR(6) YYYYMM, e.g. 202609; displayed as 'Sep 2026'. |
| Table | TB_M_H0125_DESTINATION | Destination Master (existing, read only). Crossdock uses DESTINATION_CD and DESTINATION_NAME only. |
| Part Status | Active | Only Active parts are mapped in the ongoing period. |
| Period | Ongoing / past | Created by the calculation batch. Ongoing (latest period): mapping can be edited and uploaded. Past: read only. |
| Table | TB_H_STG_APPOLE_KANBAN | AP POLE Kanban rows (LLM9Q910 format) and the header of the part (OPERATION_TYPE 1 to 5); refer 5.24. |
| Table | TB_H_STG_APPOLE_EXPORT | AP POLE Export rows (LLM9Q880 format); refer 5.24. |
| Table | TB_H_STG_GTOPAS | GTOPAS rows (part + destination Add / Delete); refer 5.24. |

The sync status is not kept on TB_M_PART_CANDIDATE: every value change is a row of TB_H_STG_APPOLE_KANBAN, TB_H_STG_APPOLE_EXPORT or TB_H_STG_GTOPAS with its SYNC_STATUS. TB_H_PART_CANDIDATE keeps the screen history.

### 5.21 Period, Order Type and names

- Names: sub-menu Part List = Kanban Crossdock Master (Procurement), sub-menu Mapping per Destination = Export Crossdock Master (D/S). Page title Crossdock Master. Export Excel: Crossdock_Kanban_Master_YYYYMMDD.xlsx (sheet Kanban Crossdock Master) and Crossdock_Export_Master_<Period>_YYYYMMDD.xlsx (sheet Export Crossdock Master).
- Kanban Crossdock Master (former Part List) has a period like the Export Crossdock Master: TB_M_PART_CANDIDATE is kept per PART_NO + PERIOD (Status, Pcs/Case and Max Case/Day of that month).
- Kanban Crossdock Master screen: new search criterion Calculation period (All periods / periods, default the ongoing period) and new first column Period. Rows of a past period: Part Number and [Edit] not available, [History] available. Add Part: into the ongoing period (default) or the next period.
- Periods: Past = view only; Current (M) = changed by screen and upload; Next (M+1) = made by XD05 on day D (system master), view only until day 1. On day 1 the Period Rollover (XD05 process 3) makes Next the Current period.
- Order Type per destination row (system master '**', 'C', '9', 'V'): the same destination may have two rows in a period when the order type differs; key PART_NO + PERIOD + DEST_CODE + ORDER_TYPE. Export Crossdock Master: new column Order Type (combobox of the system master) after Destination (CD); Save is blocked when a destination + order type is used twice ("The same destination is used twice with the same order type").
- Export Excel / Upload of the Export Crossdock Master: new column Order Type after Destination Code (sheet 1 and sheet Upload).
- Max Case/Day of a period may not be below the mapped total of that period (message 14): to lower it, D/S first reduces the destinations on the Export Crossdock Master, then changes Max Case/Day on the Kanban Crossdock Master.
- [Sync] and Sync Status are per part and period (TB_M_PART_CANDIDATE key PART_NO + TARGET_SYSTEM + PERIOD): XD07 sends the Current period first, then the Next period; XD06 uses the Current period only.

| Period | Kanban Crossdock Master | Export Crossdock Master |
|---|---|---|
| Past | View only | View only |
| Current (M) | Edit / Add Part / upload | Edit / upload |
| Next (M+1) | View only (made by XD05) | View only (made by XD05) |

### 5.24 Sync with the staging tables

- Every save calls the stored procedure SP_STG_WRITE once per changed value, in the same transaction and after the master tables are updated. A save without a changed value writes nothing.
- Kanban (TB_H_STG_APPOLE_KANBAN): a change of Pcs/Case or Max Case/Day of an Active part writes a row with the values after the change (ACTION EDIT); Candidate -> Active and a part of a new period write ACTION ADD. OPERATION_TYPE compares the new Max with the last Max sent to AP POLE (same period, else the latest earlier period): 1 = Max down, 2 = Max up, 3 = Max same, 4 = never sent.
- Export (TB_H_STG_APPOLE_EXPORT): one row per added (ADD), changed (EDIT) or removed (DELETE, Max Shipping Box (RCS) 0) destination + order type. Active -> Inactive writes DELETE (0) for every destination of the part.
- GTOPAS (TB_H_STG_GTOPAS): a row only when the destination appears or disappears for the part (any order type) and GTOPAS does not have that state yet. A Case/Day change or an order type change of a destination that stays writes no GTOPAS row.
- Header: an Export change of a part + period without an unsent Kanban row writes the Kanban header with ACTION KEEP and OPERATION_TYPE 5 (current Kanban values, not uploaded). So every part of a run has one Kanban row that sets its upload order. The header is deleted when no Export row of the part + period waits any more.
- One unsent row per key: a key has at most one row with SYNC_STATUS 0. A new change of the key updates that row (value, ACTION, OPERATION_TYPE, CHANGED_BY / CHANGED_DT); a change back to the value already sent for the period deletes it (nothing to send); a sent row (SYNC_STATUS 1) is never changed, the next change inserts a new row. Keys: Kanban PERIOD + PART_NO; Export PERIOD + NSP_PART_NO + DEST_CODE + ORDER_TYPE; GTOPAS PERIOD + P_NO + DESTINATION_CODE. TB_H_PART_CANDIDATE keeps every change.
- NSP keeps the end state valid before the save: total Case/Day of the destinations <= Max Case/Day of the part in the period (XD01 messages 14 and 20, XD02 / XD03 checks).
- [Sync] takes the time of the click once (SYNC_DT, to the second) and calls SP_STG_SYNC with it. It calculates nothing: it locks the staging tables for a moment (a save at the same time waits), sets SYNC_STATUS 0 -> 1 and SYNC_DT on the AP POLE rows of the Current and Next period and on the GTOPAS rows of the Current period, and sets the System Master parameter LAST_SYNC_DATE_APPOLE. Then it starts the RPA parent flow with the same SYNC_DT: the robots read the rows of that click.
- Upload files of AP POLE (views): EXPORT_PRE (LLM9Q880, order 1) = Export rows of the parts whose Kanban row of the run has OPERATION_TYPE 1; KANBAN (LLM9Q910, order 2) = Kanban rows of the run with OPERATION_TYPE 1 to 4; EXPORT_POST (LLM9Q880, order 3) = every other Export row of the run. Inside a file, per part, rows going down or DELETE (ROW_ORDER 1) come before rows going up or ADD (ROW_ORDER 2). An empty file is not made. File name <template>_<SYNC_DT YYYYMMDDHHMMSS>_<order>_<name>.xls.
- RPA parent flow: a run with GTOPAS rows (a part becomes Active or Inactive, a destination is added or removed) runs XD06 first and XD07 only when GTOPAS succeeded; a run without GTOPAS rows runs XD07 only. The Period Rollover runs XD06 only.
- The robots write nothing back to NSP; the result comes by the notification e-mail. When it says FAILED, the D/S team clicks [Re-send last Sync] before the next [Sync]: the same SYNC_DT, the same rows and order.
- Rows of a past period that were not sent before the Period Rollover are never taken again: every selection has a PERIOD condition.
- Sync Status per part + period: AP POLE Non Sync while TB_H_STG_APPOLE_KANBAN or TB_H_STG_APPOLE_EXPORT has a row with SYNC_STATUS 0, else Sync; GTOPAS Non Sync while TB_H_STG_GTOPAS has a row with SYNC_STATUS 0, else Sync. Last Sent = latest SYNC_DT of the target.
- Rules and simulation: deliverables/function_list_v2/erd/proposal_staging_sync (Proposal_Tables_Staging_Per_Target.xlsx, simulation/Staging_Header_Order.html, simulation/Staging_Per_Target_Full_Flow_Simulation.xlsx).

| OPERATION_TYPE | Meaning | Upload order of the part |
|---|---|---|
| 1 | Max down | EXPORT_PRE, then KANBAN |
| 2 | Max up | KANBAN, then EXPORT_POST |
| 3 | Max same (only Pcs/Case changed, or a new period with the same Max) | KANBAN, then EXPORT_POST |
| 4 | Never sent (new part) | KANBAN, then EXPORT_POST |
| 5 | Kanban unchanged, only the destinations changed (ACTION KEEP) | EXPORT_POST only |

### 5.25 Table changes per Save

Every save on the screen writes in one transaction. Add = insert a row, Edit = update a row, Delete = delete a row. A save without a changed value adds no history and no staging row. Columns: refer Data Map.

| Save (screen) | Table | Add / Edit / Delete | What is written |
|---|---|---|---|
| Add Part [Save] | TB_M_PART_CANDIDATE | Add | 1 row for the new part in the selected period (ongoing or next), PART_STATUS Candidate. When the ongoing period is selected after day D, 1 more row for the next period. |
|  | TB_H_PART_CANDIDATE | Add | EVENT_TYPE ADD, SOURCE SCREEN, OLD_VALUE NULL (history of the new part). |
|  | Staging tables | - | No row: a Candidate part is not sent. |
| Edit part data [Save] | TB_M_PART_CANDIDATE | Edit | The part row: Status, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, CHANGED_BY / CHANGED_DT. |
|  | TB_M_PART_CANDIDATE_DEST | Delete | Active -> Inactive: every destination of the part in the period. |
|  | TB_H_PART_CANDIDATE | Add | 1 row per changed field, EVENT_TYPE EDIT, SOURCE SCREEN, old and new value. |
|  | TB_H_STG_APPOLE_KANBAN | Add | Active part: 1 row with the new Pcs/Case and Max (EDIT, OPERATION_TYPE 1 / 2 / 3). Candidate -> Active: ADD (OPERATION_TYPE 4). Active -> Inactive: header (KEEP, 5). |
|  | TB_H_STG_APPOLE_EXPORT | Add | Active -> Inactive: 1 DELETE row (0) per destination. |
|  | TB_H_STG_GTOPAS | Add | Active -> Inactive: 1 DELETE row per destination GTOPAS has. |
| Edit mapping [Save] | TB_M_PART_CANDIDATE_DEST | Add | 1 row per new destination + order type of the part and period. |
|  | TB_M_PART_CANDIDATE_DEST | Edit | CASE_DAY of a kept destination whose Case/Day changed, CHANGED_BY / CHANGED_DT. |
|  | TB_M_PART_CANDIDATE_DEST | Delete | The row of a removed destination. |
|  | TB_H_PART_CANDIDATE | Add | 1 row per added, changed or removed destination, EVENT_TYPE MAPPING, FIELD_NAME CASE_DAY. |
|  | TB_H_STG_APPOLE_EXPORT | Add | 1 row per added (ADD), changed (EDIT) or removed (DELETE, 0) destination. |
|  | TB_H_STG_GTOPAS | Add | 1 row when a destination appears or disappears for the part (any order type). |
|  | TB_H_STG_APPOLE_KANBAN | Add | Header (KEEP, OPERATION_TYPE 5) when the part + period has no unsent Kanban row. |
| Every save above | Staging tables | Edit | The unsent row of the same key (SYNC_STATUS 0) takes the new value; it is deleted when the value is back to the value already sent. |
| [Sync] | Staging tables | Edit | SP_STG_SYNC: SYNC_STATUS 0 -> 1, SYNC_DT = time of the click (AP POLE Current + Next, GTOPAS Current). No row is added. |
|  | System Master | Edit | LAST_SYNC_DATE_APPOLE = time of the click. |
| [Re-send last Sync] | Staging tables | - | The rows of the last run (latest SYNC_DT) are sent again (refer 5.16 c). No row is added. |
| Upload Excel [Validate file] | Same tables as the Save above | Add / Edit / Delete | Written by the upload batch, SOURCE UPLOAD: XD02 for Kanban Crossdock Master, XD03 for Export Crossdock Master (refer UISS-Batch). |

## 7. Display messages

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| **Kanban Crossdock Master - Search Operation** |  |  |  |  |  |
| MSG1 | Change search criteria | No part matches the criteria | Info | No matching parts. Change the search criteria or reset the filters. | Change the criteria or click [Reset filter] |
| MSG2 | Open Kanban Crossdock Master | No part registered yet | Info | No crossdock part is registered yet. | Click [Upload Excel] or [Add one part] |
| **Kanban Crossdock Master - Add / Edit Operation** |  |  |  |  |  |
| MSG3 | Click [Save] button | Part No already registered (concurrent add) | Error | {Part No} is already registered. | Close the modal and search the part |
| MSG4 | Click [Save] button | Record changed by another user | Error | Another user changed this part after you opened it. Refresh and edit again. | Close the modal, refresh and edit again |
| MSG5 | Hover disabled [Save] | Part No not selected | Info | Part No is required | Select a Part No |
| MSG6 | Hover disabled [Save] | Pcs/Case not filled | Info | Enter Pcs/Case first (step 2) | Fill Pcs/Case |
| MSG7 | Hover disabled [Save] | Max Case/Day not filled | Info | Enter Max Case/Day (step 2) | Fill Max Case/Day |
| MSG8 | Type in 'Part No' | No unregistered part matches the text | Info | Part not found | Check the Part No |
| MSG9 | Click [Save] button | Part saved successfully | Info | Saved successfully: {Part No} · {Part Name} is saved and shown at the top of the Kanban Crossdock Master. | Click [OK] |
| MSG10 | Hover 'Period' in Edit | The part is registered | Info | The period cannot be changed after the part is registered. | - |
| **Kanban Crossdock Master - Upload Operation** |  |  |  |  |  |
| MSG11 | Click [Validate file] button | Upload validated and saved | Info | Saved successfully: the file passed validation and the part settings are saved to the Kanban Crossdock Master. | Click [OK] |
| **Kanban Crossdock Master - History Operation** |  |  |  |  |  |
| MSG12 | Click History icon | Part has no history | Info | No change history for this part yet. | Click [Close] |
| **Kanban Crossdock Master - Export Operation** |  |  |  |  |  |
| MSG13 | Click [Export Excel] button | Excel file cannot be created | Error | Export Excel failed. Please try again. | Click [Export Excel] again; contact administrator if it persists |
| MSG14 | Change 'Max Case/Day' in Edit / click [Save] | Max Case/Day below the total Case/Day mapped in the ongoing period | Error | Max Case/Day cannot be less than the mapped total of the ongoing period ({n} case/day). Reduce the mapping in Export Crossdock Master first. | Reduce the mapping in Export Crossdock Master first, or enter a higher Max Case/Day |
| MSG15 | Hover disabled [Save] | Min MAD blank or not a whole number | Info | Enter Min MAD (whole number, 0 or more) | Fill Min MAD |
| **Kanban Crossdock Master - Calculation Operation** |  |  |  |  |  |
| MSG16 | Click [Run calculation] button | DAD Volume Calculation completed | Info | Calculation completed: part statuses are updated from the average MAD against Min MAD. | Click [OK] |
| MSG17 | Hover disabled [Run calculation] | Scheduled run has not failed 3 times | Info | Enabled only when the scheduled run has failed 3 times | - |
| **Mapping - Search Operation** |  |  |  |  |  |
| MSG18 | Change search criteria | No part matches the criteria | Info | No parts match these filters. Change the period or sync status, or click [Reset] to show all parts. | Change the criteria or click [Reset] |
| **Mapping - Edit Mapping Operation** |  |  |  |  |  |
| MSG19 | Open Destination Mapping panel | Part has no destination | Info | No destination yet. Click [Edit mapping] and add at least one destination so the part is included in the volume calculation. | Click [Edit mapping] and add a destination |
| MSG20 | Change Case/Day in edit mode | Total Case/Day above Max Case/Day | Error | Allocation of {n} case/day exceeds Max Case/Day ({m}). Reduce one of the destinations. | Reduce Case/Day of a destination |
| MSG21 | Edit mode | A row has no destination selected | Error | Select a destination for every row, or remove the empty row, before saving. | Select a destination or remove the row |
| MSG22 | Open panel of a past period | Period is not ongoing | Info | Past period: read only | - |
| **Mapping - Upload Operation** |  |  |  |  |  |
| MSG23 | Hover disabled [Upload Excel] | Past period or All periods selected | Info | Past period: read only. Select the ongoing period to upload. | Select the ongoing period |
| MSG24 | Click [Validate file] button | Upload validated and saved | Info | Saved successfully: the file passed validation and the destination mapping is saved to Export Crossdock Master. | Click [OK] |
| **Mapping - Save Operation** |  |  |  |  |  |
| MSG25 | Click [Save] button | Mapping changed by another user | Error | Another user changed this mapping after you started editing. Refresh and edit again. | Cancel, refresh and edit again |
| **Mapping - Export Operation** |  |  |  |  |  |
| MSG26 | Click [Export Excel] button | Excel file cannot be created | Error | Export Excel failed. Please try again. | Click [Export Excel] again; contact administrator if it persists |
| **Mapping - Sync Operation** |  |  |  |  |  |
| MSG27 | Click [Sync] button | Parts handed to XD06 / XD07 | Info | Sync started for {n} part(s) to AP POLE and GTOPAS. The result comes by e-mail. | - |
| MSG28 | Hover a Sync Status chip | Part already sent | Info | Last sent {date-time}. | - |
| **Mapping - Calculation Operation** |  |  |  |  |  |
| MSG29 | Click [Run calculation] button | Mapping calculation (XD05 process 2) completed | Info | Calculation completed: the destination mapping of the new period is created. | Click [OK] |
| MSG30 | Hover disabled [Run calculation] | Scheduled run has not failed 3 times | Info | Enabled only when the scheduled run has failed 3 times | - |
| MSG31 | Click [Save] in Edit mapping | Destination + Order Type used twice for the part | Error | The same destination is used twice with the same order type. Choose another order type or remove the row. | Choose another order type or remove the row |

## 8. Logging messages

| ID | Event | Cause | Type | Message | Action | Exception |
|---|---|---|---|---|---|---|
| LOG1 | Click [Save] button | Database error on insert/update of TB_M_PART_CANDIDATE | Error | Failed to save part <PART_NO>: <DB error message>. | Show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG2 | Click [Export Excel] button | Excel file generation error | Error | Export Excel of Kanban Crossdock Master failed: <error message>. | Display Message no. 13 | Y |
| - | Click [Validate file] button | Upload processing | Info | Logging is handled by the Kanban Crossdock Master Upload batch (refer UISS-Batch "XD02 Cross Dock Part Master Upload Batch"). | - | N |
| LOG3 | Click [Save] button | Database error on save of TB_M_PART_CANDIDATE_DEST | Error | Failed to save mapping of part <PART_NO>, period <PERIOD>: <DB error message>. | Show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG4 | [Sync] / [Re-send last Sync] | XD06 / XD07 run | Error | Logging is done by XD06 / XD07 (refer UISS-Batch XD06 / XD07); the result comes by the notification e-mail. | Read the e-mail; FAILED: click [Re-send last Sync] | N |
| LOG5 | Click [Export Excel] button | Excel file generation error | Error | Export Excel of Export Crossdock Master failed: <error message>. | Display Message no. 26 | Y |
| - | Click [Validate file] button | Upload processing | Info | Logging is handled by the Export Crossdock Master Upload batch (refer UISS-Batch "XD03 Part and Destination Mapping Upload Batch"). | - | N |

## 9. Tables

#### TB_H_PART_CANDIDATE (history, proposed)
History of every change of a crossdock part for the History setting of XD01 (Add / Edit by screen or upload, mapping changes, status changes and mappings made by the calculation batches). The sync to GTOPAS / AP POLE is not recorded here: it is in the staging tables (TB_H_STG_APPOLE_KANBAN, TB_H_STG_APPOLE_EXPORT, TB_H_STG_GTOPAS). No retention limit.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| HIST_ID | BIGINT | Y | N | Running number (identity) |
| PART_NO | VARCHAR(TBD) |  | N | Part number; length follows TB_M_PART_MASTER |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM of the changed row (every event; Kanban and Export Crossdock Master are per period) |
| EVENT_TYPE | VARCHAR(10) |  | N | ADD / EDIT / MAPPING / CALC |
| SOURCE | VARCHAR(10) |  | N | SCREEN / UPLOAD / BATCH |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the change (Log); NULL when not from an upload |
| DEST_CODE | CHAR(7) |  | Y | Destination code (7 digits) for MAPPING; NULL for other events |
| ORDER_TYPE | VARCHAR(2) |  | Y | Order Type of the destination row for MAPPING (with DEST_CODE); NULL for other events |
| FIELD_NAME | VARCHAR(30) |  | N | Changed field: PCS_CASE, MAX_CASE_DAY, MIN_MAD, PART_STATUS, CASE_DAY |
| OLD_VALUE | VARCHAR(255) |  | Y | Value before the change; NULL for ADD or an added destination |
| NEW_VALUE | VARCHAR(255) |  | Y | Value after the change; NULL for a removed destination |
| REMARK | VARCHAR(500) |  | Y | Free text |
| CREATED_BY | VARCHAR(20) |  | N | User who made the change (batch user ID for BATCH) |
| CREATED_DT | DATETIME |  | N | Date and time of the change |

#### TB_H_STG_APPOLE_KANBAN (history, proposed)
AP POLE Kanban rows in the format of the upload file LLM9Q910, one row per Kanban change of a part + period (one unsent row at a time: a new change updates it), plus the header row (OPERATION_TYPE 5) when only the destinations changed. Written by SP_STG_WRITE (XD01, XD02, XD05); SYNC_STATUS and SYNC_DT set by SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_KANBAN and V_APPOLE_UPLOAD_EXPORT.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| STG_ID | BIGINT | Y | N | Running number: order of the inserts |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM. FK1 (PART_NO, PERIOD) -> TB_M_PART_CANDIDATE. File column Effective Month / Year = MM/YYYY of PERIOD, made by the view (not stored) |
| ACTION | VARCHAR(6) |  | N | ADD (new part, new period) / EDIT (Pcs/Case or Max changed) / KEEP (header written by an Export save, Kanban unchanged) |
| PART_STATUS | VARCHAR(10) |  | N | Active / Inactive in the period when the row is written (an Inactive part stays in the AP POLE Kanban) |
| OPERATOR_ID | CHAR(2) |  | N | Always P6. File / screen column: Operator ID. Default 'P6' |
| PART_NO | VARCHAR(TBD) |  | N | Part number with "-" (NSP format); FK1. File / screen column: Part No. |
| PART_NAME | VARCHAR(TBD) |  | N | From TB_M_PART_CANDIDATE at the insert. File / screen column: Part Name |
| SHIPPING_BOX_QTY | NUMBER(5) |  | N | Pcs/Case. File / screen column: Shipping Box Qty |
| MAX_SHIPPING_BOX_QTY | NUMBER(5) |  | N | Max Case/Day. File / screen column: Max Shipping Box Qty |
| MAX_ALLOWANCE_QTY | NUMBER(9) |  | N | Shipping Box Qty x Max Shipping Box Qty. File / screen column: Max Allowance Qty |
| OPERATION_TYPE | NUMBER(1) |  | N | Header of the part, set by SP_STG_WRITE at the save: 1 = Max down, 2 = Max up, 3 = Max same (only Pcs/Case changed, or a new period with the same Max), 4 = never sent, 5 = Kanban unchanged, only the destinations changed (ACTION KEEP). 1 to 4 against the last Max sent: same period, else the latest earlier period. Upload: 1 -> the Export rows of the part in EXPORT_PRE before KANBAN; 2, 3, 4 -> KANBAN then EXPORT_POST; 5 -> EXPORT_POST only, the row is not in the KANBAN file |
| SOURCE | VARCHAR(6) |  | N | SCREEN / UPLOAD / BATCH (XD05) |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD |
| SYNC_STATUS | CHAR(1) |  | N | 0 = to send (written or updated by SP_STG_WRITE), 1 = sent (SP_STG_SYNC at [Sync], SP_STG_ROLLOVER for GTOPAS). One row with 0 per key at a time: a new change of the key updates it. Default '0' |
| SYNC_DT | DATETIME2(0) |  | Y | Time of the [Sync] click (or of the Period Rollover), the same value for every row of that click: the RPA reads the rows of a run by SYNC_DT; [Re-send last Sync] = MAX(SYNC_DT); Last Sent on the screen = latest value |
| CREATED_BY | VARCHAR(20) |  | N | User of the save / upload, or XD05BATCH |
| CREATED_DT | DATETIME |  | N | Time of the insert (same transaction as the master update) |
| CHANGED_BY | VARCHAR(20) |  | Y | User of the save that updated the unsent row, of [Sync], or XD05BATCH (Period Rollover) |
| CHANGED_DT | DATETIME |  | Y | Time of that update |

#### TB_H_STG_APPOLE_EXPORT (history, proposed)
AP POLE Export rows in the format of the upload file LLM9Q880, one row per added, changed or removed destination + order type of a part + period (one unsent row per key: a new change updates it). Written by SP_STG_WRITE (XD01, XD03, XD05); SYNC_STATUS and SYNC_DT set by SP_STG_SYNC. Read by XD07 through V_APPOLE_UPLOAD_EXPORT.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| STG_ID | BIGINT | Y | N | Running number: order of the inserts |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM. FK1 (NSP_PART_NO, PERIOD) -> TB_M_PART_CANDIDATE. File column Effective Month / Year = MM/YYYY of PERIOD, made by the view (not stored) |
| NSP_PART_NO | VARCHAR(TBD) |  | N | Part number with "-" (key back to NSP); FK1 |
| DEST_CODE | CHAR(7) |  | N | Destination code, 7 digits. No FK: a DELETE row points to a removed destination |
| ACTION | VARCHAR(6) |  | N | ADD / EDIT / DELETE (DELETE = Max Shipping Box (RCS) 0) |
| PART_NO | VARCHAR(TBD) |  | N | Part number without "-". File / screen column: Part No. |
| BUYER_PD | CHAR(8) |  | N | DEST_CODE in 5-2 format. File / screen column: Buyer-PD |
| ORDER_TYPE | VARCHAR(2) |  | N | '**', 'C', '9', 'V' (system master). File / screen column: Order Type |
| TRANSPORT_CODE | CHAR(1) |  | N | Always 2. File / screen column: Transport Code. Default '2' |
| MAX_SHIPPING_BOX_RCS | NUMBER(5) |  | N | Case/Day of the destination; 0 = delete. File / screen column: Max Shipping Box (RCS) |
| SOURCE | VARCHAR(6) |  | N | SCREEN / UPLOAD / BATCH (XD05) |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD |
| SYNC_STATUS | CHAR(1) |  | N | 0 = to send (written or updated by SP_STG_WRITE), 1 = sent (SP_STG_SYNC at [Sync], SP_STG_ROLLOVER for GTOPAS). One row with 0 per key at a time: a new change of the key updates it. Default '0' |
| SYNC_DT | DATETIME2(0) |  | Y | Time of the [Sync] click (or of the Period Rollover), the same value for every row of that click: the RPA reads the rows of a run by SYNC_DT; [Re-send last Sync] = MAX(SYNC_DT); Last Sent on the screen = latest value |
| CREATED_BY | VARCHAR(20) |  | N | User of the save / upload, or XD05BATCH |
| CREATED_DT | DATETIME |  | N | Time of the insert (same transaction as the master update) |
| CHANGED_BY | VARCHAR(20) |  | Y | User of the save that updated the unsent row, of [Sync], or XD05BATCH (Period Rollover) |
| CHANGED_DT | DATETIME |  | Y | Time of that update |

#### TB_H_STG_GTOPAS (history, proposed)
GTOPAS WVJA5204 rows: a part + destination to add or delete, written by SP_STG_WRITE only when the destination appears or disappears for the part (any order type) and GTOPAS does not have that state yet (one unsent row per key). Sent by [Sync] (Current period) or the Period Rollover (new Current period). Read by XD06.

| Column | Type | PK | Null | Description |
|---|---|---|---|---|
| STG_ID | BIGINT | Y | N | Running number: order of the inserts |
| PERIOD | CHAR(6) |  | N | Calculation period YYYYMM (GTOPAS has no period: [Sync] sends the Current period, the Period Rollover the new Current). FK1 (P_NO, PERIOD) -> TB_M_PART_CANDIDATE |
| ACTION | VARCHAR(6) |  | N | ADD / DELETE: the destination appears or disappears for the part (any order type). No row for a Case/Day change or for a state GTOPAS already has. File / screen column: Add / Delete (MT = DEL) |
| DEPOT_CODE | CHAR(2) |  | N | Always 01. File / screen column: Depot Code. Default '01' |
| P_NO | VARCHAR(TBD) |  | N | Part number with "-"; FK1. File / screen column: P/No. |
| DESTINATION_CODE | CHAR(7) |  | N | 7-digit code, the same in NSP and GTOPAS. File / screen column: Destination Code |
| MAKER_CODE | CHAR(1) |  | N | Always A. File / screen column: Maker Code. Default 'A' |
| DOMESTIC_OVERSEAS | CHAR(1) |  | N | Always 2. File / screen column: Domestic/Overseas. Default '2' |
| TOPAS_ORDER_TYPE | CHAR(1) |  | N | Always 3. File / screen column: TOPAS Order Type. Default '3' |
| ORDER_TRANSPORTATION_CODE | CHAR(1) |  | N | Always 2. File / screen column: Order Transportation Code. Default '2' |
| SOURCE | VARCHAR(6) |  | N | SCREEN / UPLOAD / BATCH (XD05) |
| UPLOAD_ID | VARCHAR(TBD) |  | Y | Upload of the Kanban or Export Excel (Log); NULL when SOURCE is not UPLOAD |
| SYNC_STATUS | CHAR(1) |  | N | 0 = to send (written or updated by SP_STG_WRITE), 1 = sent (SP_STG_SYNC at [Sync], SP_STG_ROLLOVER for GTOPAS). One row with 0 per key at a time: a new change of the key updates it. Default '0' |
| SYNC_DT | DATETIME2(0) |  | Y | Time of the [Sync] click (or of the Period Rollover), the same value for every row of that click: the RPA reads the rows of a run by SYNC_DT; [Re-send last Sync] = MAX(SYNC_DT); Last Sent on the screen = latest value |
| CREATED_BY | VARCHAR(20) |  | N | User of the save / upload, or XD05BATCH |
| CREATED_DT | DATETIME |  | N | Time of the insert (same transaction as the master update) |
| CHANGED_BY | VARCHAR(20) |  | Y | User of the save that updated the unsent row, of [Sync], or XD05BATCH (Period Rollover) |
| CHANGED_DT | DATETIME |  | Y | Time of that update |
