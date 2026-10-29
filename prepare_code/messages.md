# Messages (XD01–XD15)

## XD01 – Cross Dock Part Master Screen

### Display

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

### Logging

| ID | Event | Cause | Type | Message | Action | Exception |
|---|---|---|---|---|---|---|
| LOG1 | Click [Save] button | Database error on insert/update of TB_M_PART_CANDIDATE | Error | Failed to save part <PART_NO>: <DB error message>. | Show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG2 | Click [Export Excel] button | Excel file generation error | Error | Export Excel of Part List failed: <error message>. | Display Message no. 13 | Y |
| - | Click [Validate file] button | Upload processing | Info | Logging is handled by the Part List Upload batch (refer UISS-Batch "XD02 Cross Dock Part Master Upload Batch"). | - | N |
| LOG3 | Click [Save] button | Database error on save of TB_M_PART_CANDIDATE_DEST | Error | Failed to save mapping of part <PART_NO>, period <PERIOD>: <DB error message>. | Show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG4 | XD06 / XD07 | GTOPAS or AP POLE rejects a part | Error | Logging is done by XD06 / XD07 (refer UISS-Batch XD06 / XD07); the chip shows the result. | Status Failed; Display Message no. 28 on the chip | N |
| LOG5 | Click [Export Excel] button | Excel file generation error | Error | Export Excel of Mapping per Destination failed: <error message>. | Display Message no. 26 | Y |
| - | Click [Validate file] button | Upload processing | Info | Logging is handled by the Mapping per Destination Upload batch (refer UISS-Batch "XD03 Part and Destination Mapping Upload Batch"). | - | N |

## XD02 – Cross Dock Part Master Upload Batch

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | Batch is called | Info | Upload batch <UPLOAD_ID> started. | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | Upload batch <UPLOAD_ID> ended. Status <STATUS>, total <TOTAL_ROWS>, saved <SAVED_ROWS>, no change <NO_CHANGE_ROWS>, error <ERROR_ROWS>. | system: Write the log.; user: - |
| LOG3 | Receive file | Uploaded file of <UPLOAD_ID> not found | Error | Uploaded file of <UPLOAD_ID> not found. | system: Stop the batch.; user: Upload the file again. |
| LOG4 | File check | Extension, size, row count, sheet Upload or header is invalid | Error | File check failed: <REASON>. | system: Set STATUS = REJECTED. Create the result report.; user: Download the file from the screen again and upload it. |
| LOG5 | Row validation | A validation rule in 4.2 fails | Error | Row <ROW_NO> <COLUMN> : <RULE_MESSAGE>. | system: Reject the whole file. Nothing is saved.; user: Correct the rows in sheet Re-upload of the result report, then upload again. |
| LOG6 | Row skipped | Edit row has the same values as the master | Info | Row <ROW_NO> Part No <PART_NO> has no change. Skipped. | system: Do not update the record.; user: - |
| LOG7 | Save to master | Insert or update TB_M_PART_CANDIDATE fails | Error | Cannot save Part No <PART_NO> to TB_M_PART_CANDIDATE. | system: Roll back. Set STATUS = REJECTED.; user: User contact PIC |
| LOG8 | Result report | Result report cannot be created | Warning | Result report of <UPLOAD_ID> cannot be created. | system: Continue. RESULT_FILE_PATH stays blank.; user: Contact system owner. |
| LOG9 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. Set STATUS = REJECTED.; user: User contact PIC |

## XD03 – Part and Destination Mapping Upload Batch

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | Batch is called | Info | Mapping upload batch <UPLOAD_ID> started. | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | Mapping upload batch <UPLOAD_ID> ended. Status <STATUS>, total <TOTAL_ROWS>, saved parts <SAVED_ROWS>, no change <NO_CHANGE_ROWS>, error <ERROR_ROWS>. | system: Write the log.; user: - |
| LOG3 | Receive file | Uploaded file of <UPLOAD_ID> not found | Error | Uploaded file of <UPLOAD_ID> not found. | system: Stop the batch.; user: Upload the file again. |
| LOG4 | File check | Extension, size, row count, sheet Upload or header is invalid | Error | File check failed: <REASON>. | system: Set STATUS = REJECTED. Create the result report.; user: Download the file from the screen again and upload it. |
| LOG5 | Row validation | A validation rule in 4.2 fails | Error | Row <ROW_NO> <COLUMN> : <RULE_MESSAGE>. | system: Reject the whole file. Nothing is saved.; user: Correct the rows in sheet Re-upload of the result report, then upload again. |
| LOG6 | Part skipped | Rows of the part equal the current mapping, or all rows are blank | Info | Part No <PART_NO> has no mapping change. Skipped. | system: Do not change the mapping or the part.; user: - |
| LOG7 | Save mapping | Save (update / insert / delete) of TB_M_PART_CANDIDATE_DEST or update of TB_M_PART_CANDIDATE fails | Error | Cannot save the mapping of Part No <PART_NO>. | system: Roll back. Set STATUS = REJECTED.; user: User contact PIC |
| LOG8 | Result report | Result report cannot be created | Warning | Result report of <UPLOAD_ID> cannot be created. | system: Continue. RESULT_FILE_PATH stays blank.; user: Contact system owner. |
| LOG9 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. Set STATUS = REJECTED.; user: User contact PIC |

## XD04 – Actual Demand Summary Synch to NSP

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | Batch is called | Info | Actual demand summary sync started. | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | Actual demand summary sync ended. Status <STATUS>, rows <ROW_COUNT>. | system: Write the log.; user: - |
| LOG3 | Read source | DB Surrounding cannot be reached or read | Error | Cannot read TB_R_ACTUAL_DEMAND_SUMMARY from DB Surrounding: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED.; user: User contact PIC |
| LOG4 | Insert | Insert into the NSP table fails | Error | Cannot insert TB_R_ACTUAL_DEMAND_SUMMARY into NSP: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED.; user: User contact PIC |
| LOG5 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED.; user: User contact PIC |

## XD05 – DAD Volume Calculation Batch

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Process 1: Batch start | Batch is called | Info | DAD volume calculation started (<RUN_TYPE>, retry <RETRY_NO>). Range <MONTH_FROM> - <MONTH_TO>. | system: Write the log.; user: - |
| LOG2 | Process 1: Batch end | Batch finishes | Info | DAD volume calculation ended. Status <STATUS>, calculated <COUNT>, status changed <CHANGED>. | system: Write the log.; user: - |
| LOG3 | Process 1: Range of months | Range is not set in the system master | Error | Range of months for the DAD volume calculation is not set. | system: Stop. STATUS = FAILED.; user: User contact PIC |
| LOG4 | Process 1: Part skipped | Effective Start Date after the run date | Info | Part No <PART_NO> skipped: effective start date <DATE>. | system: Continue.; user: - |
| LOG5 | Process 1: Save | Insert / update fails | Error | Cannot save the calculation of Part No <PART_NO>: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |
| LOG6 | Process 1: Retry exhausted | Scheduled run and 3 retries failed | Warning | DAD volume calculation failed 3 times. Manual run is enabled on Part List. | system: Enable [Run calculation] on Part List.; user: Check the cause, then click [Run calculation]. |
| LOG7 | Process 1: Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |
| LOG8 | Process 2: Batch start | Batch is called | Info | Mapping destination calculation started (<RUN_TYPE>, retry <RETRY_NO>). Period <PERIOD>, range <MONTH_FROM> - <MONTH_TO>. | system: Write the log.; user: - |
| LOG9 | Process 2: Batch end | Batch finishes | Info | Mapping destination calculation ended. Status <STATUS>, parts <COUNT>, mapping changed <CHANGED>. | system: Write the log.; user: - |
| LOG10 | Process 2: Range of months | Range is not set in the system master | Error | Range of months for the mapping destination calculation is not set. | system: Stop. STATUS = FAILED.; user: User contact PIC |
| LOG11 | Process 2: Destination check | Destination code not in TB_M_H0125_DESTINATION | Error | Destination code <DEST_CODE> of Part No <PART_NO> not found in TB_M_H0125_DESTINATION. | system: Roll back. STATUS = FAILED. Retry.; user: Register the destination in TB_M_H0125_DESTINATION, then run again. |
| LOG12 | Process 2: Destinations limited | More destinations than Max Case/Day | Info | Part No <PART_NO>: <COUNT> destinations, limited to Max Case/Day <MAX>. | system: Continue.; user: - |
| LOG13 | Process 2: Save | Insert / update fails | Error | Cannot save the mapping of Part No <PART_NO>, period <PERIOD>: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |
| LOG14 | Process 2: Retry exhausted | Scheduled run and 3 retries failed | Warning | Mapping destination calculation failed 3 times. Manual run is enabled on Mapping per Destination. | system: Enable [Run calculation] on Mapping per Destination.; user: Check the cause, then click [Run calculation]. |
| LOG15 | Process 2: Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED. Retry.; user: User contact PIC |

## XD06 – IF Cross Dock Master to GTOPAS

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | [Sync] on XD01 | Info | IF cross dock master to GTOPAS started. <n> part(s). | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | IF cross dock master to GTOPAS ended. File <FILE_NAME>, parts <n>, records <r>, status <STATUS>. | system: Write the log.; user: - |
| LOG3 | Create file | Interface file cannot be created | Error | Cannot create the interface file to GTOPAS: <ERROR_DETAIL>. | system: All parts of the run IF_STATUS = 2. Stop.; user: Click [Sync] again; contact PIC if it persists. |
| LOG4 | Send | GTOPAS not available / send fails after retry | Error | Send of <SEND_ID> to GTOPAS failed: <ERROR_DETAIL>. | system: All parts of the file IF_STATUS = 2. Keep the file in the outbound folder.; user: Click [Sync] again later; contact PIC if it persists. |
| LOG5 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Stop. STATUS = ERROR.; user: User contact PIC |

## XD07 – IF Cross Dock Master to AP POLE

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | [Sync] on XD01 | Info | IF cross dock master to AP POLE started. <n> part(s). | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | IF cross dock master to AP POLE ended. File <FILE_NAME>, parts <n>, records <r>, status <STATUS>. | system: Write the log.; user: - |
| LOG3 | Create file | Interface file cannot be created | Error | Cannot create the interface file to AP POLE: <ERROR_DETAIL>. | system: All parts of the run IF_STATUS = 2. Stop.; user: Click [Sync] again; contact PIC if it persists. |
| LOG4 | SFTP transfer | AP POLE SFTP not available / transfer fails after retry | Error | SFTP transfer of <FILE_NAME> to AP POLE failed: <ERROR_DETAIL>. | system: All parts of the file IF_STATUS = 2. Keep the file in the outbound folder.; user: Click [Sync] again later; contact PIC if it persists. |
| LOG5 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Stop. STATUS = ERROR.; user: User contact PIC |

## XD08 – Order Control Information to NSP Batch

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | Batch is called | Info | H0253 sync started. Watermark <WATERMARK>. | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | H0253 sync ended. Status <STATUS>, inserted <INS>, updated <UPD> (UPD_STATUS 6: <N6>, 2: <N2>), drafts released <DRAFTS>. | system: Write the log; save the new watermark when SUCCESS.; user: - |
| LOG5 | Cancel after ASN | A line with UPD_STATUS '2' has qty in a submitted ASN | Warning | <CUSTOMER_ORDER_NO> <PART_NO>: <QTY> pcs cancelled in <ASN_NO>; listed in Change Order Number (XD11). | system: Write the log; nothing is changed in the ASN.; user: D/S team: Change Order Number (XD11). |
| LOG6 | Cancel qty check | Cancelled qty of a line in a submitted ASN is not a multiple of pcs/case (should not happen in GTOPAS) | Error | <CUSTOMER_ORDER_NO> <PART_NO>: cancelled qty <QTY> is not a multiple of pcs/case <PCS>. | system: Write the log (abnormality); the line is still listed in XD11.; user: D/S team checks with GTOPAS. |
| LOG7 | Serial split | A line in TB_R_INSTRUCTION is split into a new SERIAL_NO by GTOPAS | Info | <CUSTOMER_ORDER_NO> item <DETAILED_ITEM_NO> split into serial <SERIAL_NO>: <QTY> pcs of <ASN_NO> moved to the new serial. | system: Write the log.; user: - |
| LOG3 | Upsert | Read from DB Surrounding, insert / update in NSP or draft release fails | Error | Cannot replicate H0253 rows: <ERROR_DETAIL>. | system: Roll back; watermark not changed (rows taken again next run). STATUS = FAILED.; user: User contact PIC |
| LOG4 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED.; user: User contact PIC |

## XD09 – Mapping Customer Order and PO Batch

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Mapping Customer Order and PO | Read or insert fails | Error | Mapping Customer Order and PO failed for Delivery Date <DELIVERY_DT> <RIT>: <ERROR_DETAIL>. | system: Clear the temporary table.; user: Retry; contact PIC if it persists. |
| LOG2 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Clear the temporary table.; user: User contact PIC |

## XD10 – ASN Cross Dock Creation Screen

### Display

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

### Logging

| ID | Event | Cause | Type | Message | Action | Exception |
|---|---|---|---|---|---|---|
| LOG1 | Click [Create ASN] | Database error on mapping / draft | Error | Failed to create the ASN (TB_R_INSTRUCTION): <DB error message>. | Roll back; show [Corresponding Screen Message] on screen (TBD) | Y |
| LOG2 | Submit ASN (5.7): Batch start | [Submit ASN] Yes | Info | ASN submit started. Submit ID <SUBMIT_ID>, <n> cases. | System: Write the log. User: - | N |
| LOG3 | Submit ASN (5.7): Save | ASN saved | Info | <ASN_NO> submitted with status Created. <n> cases are saved. Delivery <DELIVERY_DT> · <RIT>. The ASN is shown in ASN Inquiry. | System: Write the log. User: - | N |
| LOG4 | Submit ASN (5.7): Batch end | Batch finishes | Info | ASN submit ended. Status <STATUS>. | System: Write the log. User: - | N |
| LOG5 | Submit ASN (5.7): Error | Numbering or insert fails / any system error | Error | Failed to submit ASN, Submit ID <SUBMIT_ID>: <ERROR_DETAIL>. | System: Roll back; release the mapping. STATUS = ERROR. User: Create the ASN again; contact PIC if it persists. | Y |

## XD11 – Change Order Number Screen

### Display

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| **List** |  |  |  |  |  |
| MSG1 | Open the screen | No cancelled qty in a submitted ASN | Info | No cancelled qty in a submitted ASN. | - |
| **Change Order Number** |  |  |  |  |  |
| MSG2 | Tick candidates | Ticked qty differs from the cancelled qty | Info | Selected {n} of {q} pcs: the qty must add up to {q}. | Tick other candidates. |
| MSG3 | Click [Change Order Number] | Confirmation | Confirmation | {q} pcs of {Customer Order} in {ASN No} ({cases}) will be moved to {replacement lines}. | Yes / No. |
| MSG4 | Click [Yes] | A candidate was taken in the meantime | Error | {Customer Order} is no longer available. The candidates are refreshed. | Tick again. |

### Logging

_None._

## XD13 – Destination Master Synch into NSP

### Logging

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| LOG1 | Batch start | Batch is called | Info | H0125 sync started. | system: Write the log.; user: - |
| LOG2 | Batch end | Batch finishes | Info | H0125 sync ended. Status <STATUS>, rows <ROW_COUNT>. | system: Write the log.; user: - |
| LOG3 | Copy table | Read from DB Surrounding or insert into NSP fails | Error | Cannot replicate TB_M_H0125_DESTINATION: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED.; user: User contact PIC |
| LOG4 | Unexpected error | Any other system error | Critical | Unexpected error: <ERROR_DETAIL>. | system: Roll back. STATUS = FAILED.; user: User contact PIC |

## XD15 – ASN Crossdock Inquiry Screen (Buffer)

### Display

| ID | Event | Cause | Type | Message | Action |
|---|---|---|---|---|---|
| **Search Operation** |  |  |  |  |  |
| MSG1 | Click [Search] button | No ASN matches | Info | No ASN matches this search. | Change the criteria. |

### Logging

_None._
