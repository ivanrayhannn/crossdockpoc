"""User Requirement content of XD01 Cross Dock Part Master (business level; technical detail stays in the UISS)."""

INFO = {
    'id': 'XD01', 'name': 'Cross Dock Part Master', 'type': 'Screen',
    'related': 'XD02 / XD03 Upload, XD05 DAD Volume Calculation, XD06 / XD07 Interface to GTOPAS / AP POLE, XD13 Destination Master',
    'bpf': 'F1 Master Setup: M3, M8, M9, M10',
    'uiss': 'XD01_UISS_Screen_CrossDockPartMaster.xlsx',
}

PURPOSE = ('Give Procurement and the D/S team one place to manage which parts are handled by crossdock and how many cases per day '
           'go to each destination, and to send this master to GTOPAS and AP POLE.')

SCOPE_IN = ['Register and maintain crossdock candidate parts (tab Part List).',
            'Split the daily case capacity of each Active part per destination (tab Mapping per Destination).',
            'Upload / export in Excel and history of changes.',
            'Send the master to GTOPAS and AP POLE and follow the sending status.']
SCOPE_OUT = ['Calculation of Active / Inactive status and of the proposed split per destination (XD05); XD01 shows the result and can start a rerun.',
             'Customer orders, PO and ASN (XD08 – XD15).']

USERS = [('Procurement', 'Owner of the Part List', 'Part List: search, add, edit, upload, export, history, run calculation'),
         ('D/S Team', 'Owner of the mapping per destination', 'Mapping per Destination: search, edit, upload, export, Sync, run calculation'),
         ('Viewer', 'Other users who need the information', 'Search and export only')]

PROCESS = [('1', 'Procurement registers candidate parts (screen or Excel).', 'Procurement', 'M3'),
           ('2', 'The monthly calculation sets each part Active / Inactive and proposes the case/day split per destination.', 'System (XD05)', 'M6 – M7'),
           ('3', 'Procurement checks the status and history of the parts.', 'Procurement', 'M8'),
           ('4', 'D/S reviews and adjusts the split per destination.', 'D/S Team', 'M9'),
           ('5', 'D/S sends the master to GTOPAS and AP POLE and checks the result.', 'D/S Team', 'M10 – M11')]

# id, requirement, user, priority, business rules, BPF step
FR = [
    ('FR-01', 'The user can search the registered parts by Part No and status, and sort the list (newest change first by default).', 'Procurement', 'Must', '-', 'M8'),
    ('FR-02', 'The user can register a new candidate part with Part No, Min MAD, Pcs/Case, Max Case/Day and Effective Start Date. Part Name is shown from the part master.', 'Procurement', 'Must', 'BR-01, BR-03', 'M3'),
    ('FR-03', 'The user can change the data and the status of a registered part.', 'Procurement', 'Must', 'BR-02, BR-03, BR-05, BR-08', 'M3'),
    ('FR-04', 'The user can see the change history of a part: who changed what and when (before / after).', 'Procurement, D/S Team', 'Must', 'BR-12', 'M8'),
    ('FR-05', 'The user can add or change many parts at once with an Excel template (column upload: A = add, E = edit).', 'Procurement', 'Must', 'BR-11', 'M3'),
    ('FR-06', 'The system shows which parts have an incomplete mapping (no destination, or total not equal to the capacity).', 'Procurement, D/S Team', 'Should', 'BR-04', 'M8 / M9'),
    ('FR-07', 'The user can see and change the case/day per destination of each Active part for the current period; past periods are view-only.', 'D/S Team', 'Must', 'BR-04, BR-06, BR-07, BR-08', 'M9'),
    ('FR-08', 'The user can split the capacity evenly over the destinations of a part with one click.', 'D/S Team', 'Could', 'BR-04', 'M9'),
    ('FR-09', 'The user can upload and export the mapping in Excel (column upload: A = new destination, E = mapped destination).', 'D/S Team', 'Must', 'BR-06, BR-11', 'M9'),
    ('FR-10', 'The user can send all changed parts to GTOPAS and AP POLE with one action and see the result per part.', 'D/S Team', 'Must', 'BR-08, BR-09, BR-10', 'M10'),
    ('FR-11', 'The user can start the calculation again manually when the scheduled run failed, and sees the date of the last successful calculation.', 'Procurement, D/S Team', 'Must', '-', 'M6 – M7'),
    ('FR-12', 'The user can export the list to Excel; the export is also the base file for the next upload.', 'All users', 'Should', 'BR-11', 'M3 / M9'),
]

BR = [
    ('BR-01', 'Part status', 'A new part always starts as Candidate. Active / Inactive is decided by the monthly calculation: average MAD of the last months ≥ Min MAD → Active, otherwise Inactive.'),
    ('BR-02', 'Part status', 'The user may change Active ↔ Inactive, but a part can never go back to Candidate.'),
    ('BR-03', 'Effective Start Date', 'Default is tomorrow, it cannot be in the past, and it can only be changed while the part is Candidate. A part is calculated only from its Effective Start Date.'),
    ('BR-04', 'Capacity', 'The total case/day of all destinations must not exceed the Max Case/Day of the part. A lower total is allowed and shown as "n case/day left".'),
    ('BR-05', 'Capacity', 'Max Case/Day cannot be reduced below the case/day already mapped; the mapping has to be reduced first.'),
    ('BR-06', 'Destination', 'A destination appears only once per part and must exist in the destination master (GTOPAS).'),
    ('BR-07', 'Period', 'Each monthly calculation creates a new period that starts from the calculated proposal; previous periods are kept view-only.'),
    ('BR-08', 'Sending', 'Any change to a part or its mapping (screen or upload) marks the part "Not yet sent".'),
    ('BR-09', 'Sending', 'One Sync sends every Active part that is not yet sent or failed, plus the parts that became Inactive (sent as "stop crossdock").'),
    ('BR-10', 'Sending', 'A part is "Sent" only when both GTOPAS and AP POLE received it. If one target fails, the part is "Failed" with the reason; if it is changed while sending, it goes back to "Not yet sent".'),
    ('BR-11', 'Upload', 'An Excel upload is saved only when the whole file is valid; otherwise nothing is saved and the user gets a report with the rows to correct.'),
    ('BR-12', 'History', 'Every change is kept in the history for 24 months.'),
]

# caption, image (repo path), what the user sees
SCREENS = [
    ('Tab Part List', 'deliverables/uiss_screens/part_list/c_01_initial.png',
     'Search area, list of parts (Part No, Min MAD, Pcs/Case, Max Case/Day, Total Pcs/Day, status, last update), buttons Add, Upload, Export, Run calculation and the date of the last calculation.'),
    ('Add part', 'deliverables/uiss_screens/part_list/c_07_add_filled.png', 'New part: always Candidate, Effective Start Date tomorrow by default.'),
    ('Edit an Active part', 'deliverables/uiss_screens/part_list/c_10_edit_active.png', 'Effective Start Date is locked once the part is no longer Candidate.'),
    ('History', 'deliverables/uiss_screens/part_list/c_11_history.png', 'Who changed what and when.'),
    ('Tab Mapping per Destination', 'deliverables/uiss_screens/mapping/c_05_details_view.png',
     'Per part: capacity, allocated, %, sending status, and the destinations with their case/day.'),
    ('Edit mapping – over capacity', 'deliverables/uiss_screens/mapping/c_08_over_allocation.png', 'Save is blocked when the total exceeds the Max Case/Day.'),
    ('Sync', 'deliverables/uiss_screens/mapping/c_12_before_sync.png', 'Sync (n): the parts to send to GTOPAS and AP POLE.'),
]

MESSAGES = [
    ('Save mapping', 'Total case/day exceeds the Max Case/Day of the part.', 'BR-04'),
    ('Save part', 'Max Case/Day is lower than the mapped total – reduce the mapping first.', 'BR-05'),
    ('Edit part', 'Effective Start Date can only be changed while the part is Candidate.', 'BR-03'),
    ('Upload', 'File rejected: n rows need correction (see the result report).', 'BR-11'),
    ('Sync', 'Sync requested for n parts; they stay Waiting until GTOPAS and AP POLE have received them.', 'BR-10'),
    ('Search', 'No part matches the criteria.', '-'),
]

NFR = [
    ('Performance', 'The list of up to 5,000 parts is shown within an acceptable time (target TBC).'),
    ('Upload', 'Excel file up to 5 MB / 5,000 rows.'),
    ('Security', 'Access by user role (Procurement, D/S Team, Viewer).'),
    ('Audit', 'Every change keeps user and time (history 24 months).'),
]

# id, scenario (given / when / then), FR, BR
AC = [
    ('AC-01', 'Given a new part, when Procurement saves it, then its status is Candidate and the Effective Start Date is tomorrow unless changed.', 'FR-02', 'BR-01, BR-03'),
    ('AC-02', 'Given an Active part, when Procurement opens Edit, then the Effective Start Date is locked and the status can only be Active or Inactive.', 'FR-03', 'BR-02, BR-03'),
    ('AC-03', 'Given Max Case/Day 24 and destinations totalling 24, when D/S adds 1 case/day to a destination, then Save is blocked with the over-capacity message.', 'FR-07', 'BR-04'),
    ('AC-04', 'Given a part with 20 case/day mapped, when Procurement changes Max Case/Day to 18, then Save is blocked until the mapping is reduced.', 'FR-03', 'BR-05'),
    ('AC-05', 'Given 3 changed Active parts and 1 part that became Inactive, when D/S clicks Sync, then 4 parts are sent and the Inactive part is sent as "stop crossdock".', 'FR-10', 'BR-08, BR-09'),
    ('AC-06', 'Given GTOPAS receives a part and AP POLE fails, when the sending ends, then the part is Failed with the AP POLE reason.', 'FR-10', 'BR-10'),
    ('AC-07', 'Given an upload file with 1 invalid row out of 100, when validated, then nothing is saved and the report lists that row.', 'FR-05, FR-09', 'BR-11'),
    ('AC-08', 'Given the scheduled calculation failed 3 times, when the user clicks Run calculation, then the calculation runs and the last success date is updated.', 'FR-11', '-'),
]

OPEN = [
    ('OP-01', 'GTOPAS receives the master through the existing interface; field layout TBC with GTOPAS.', 'GTOPAS', 'Open'),
    ('OP-02', 'AP POLE receives a file by SFTP; server, folder and acknowledge TBC.', 'AP POLE', 'Open'),
    ('OP-03', 'Monthly schedule of the calculation (date / time).', 'User', 'Open'),
    ('OP-04', 'Performance target of the list.', 'User / IT', 'Open'),
]
