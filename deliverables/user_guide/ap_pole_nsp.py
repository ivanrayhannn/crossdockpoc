"""Sheets 0 and 3 of Crossdock_User_Guide_AP_POLE.xlsx: the source data in NSP (prototype Crossdock Master Setting) and every scenario
worked out from the exported Excel to the AP POLE values. Screenshots: guide_shots_ap.mjs; Excel extracts: render_ap.py (shots_ap/)."""

SOURCE = {
    'sheet': '0. Source Data (NSP)',
    'title': 'NSP: get the source data for AP POLE (Crossdock Master Setting)',
    'caption': 'Screens from the NSP prototype: header "Supplier System" is NSP; "Preview ... / Switch sub-menu" exists only in the prototype. '
               'Red box = the item to click. Excel pictures: orange header = column read for AP POLE, yellow rows = examples of sheet "3. Scenario Detail".',
    'meta': [('Function', 'XD01 Crossdock Master Setting ([Sync], Export Excel) as the source of XD07 RPA Cross Dock Master to AP POLE'),
             ('User', 'D/S team ([Sync], Mapping per Destination) and Procurement team (Part List); the RPA reads the two files'),
             ('Result', 'Crossdock_Mapping_per_Destination_<Period>_YYYYMMDD.xlsx (sheets Mapping per Destination, Active to Inactive) and '
                        'Crossdock_Part_List_YYYYMMDD.xlsx (sheet Part List)')],
    'blocks': [
        ('step', 'Open Crossdock Master Setting, tab Mapping per Destination',
         'In the left menu click Master > Crossdock Master Setting. With the D/S account the screen opens on the tab Mapping per Destination.', 'n1_map_menu.png'),
        ('step', 'Search the ongoing period and click [Sync]',
         'Calculation period = the ongoing period (e.g. Sep 2026 (ongoing)), Sync Status = All, click [Search]. Click [Sync (n)]: every Active part '
         'of the ongoing period with Sync Status No Sync or Failed becomes Waiting. n = number of parts that will be sent to GTOPAS and AP POLE. '
         'The button is disabled when there is nothing to sync.', 'n2_map_sync.png'),
        ('step', 'Check the parts to process: Sync Status = Waiting',
         'Sync Status = Waiting, click [Search]. These are the parts the RPA processes in AP POLE. Column Last Sync: "Never" = the part was never '
         'synced, so AP POLE does not have it yet (Add); a date = the part was synced before, so AP POLE has it (Edit). Example PART-F: '
         'Last Sync 28-Aug-2026 10:05 (the run after it Failed, so the part is sent again).', 'n3_map_waiting.png'),
        ('step', 'Check the destinations of a part (optional)',
         'Click the arrow > in front of the Part Number. Example PART-009: 3 destinations, Case/Day 7 + 7 + 5 = 19 = Max Case/Day (19 / 19, 100%). '
         'These rows become the Buyer-PD rows of WLM9Q860 in AP POLE.', 'n4_map_dest.png'),
        ('step', 'Click [Export Excel] (Sync Status Waiting)',
         'With Sync Status = Waiting and Part Number empty, click [Export Excel]. The browser downloads '
         'Crossdock_Mapping_per_Destination_Sep_2026_YYYYMMDD.xlsx (period of step 2, download date). Open it in Excel.', 'n5_map_export.png'),
        ('step', 'Read sheet "Mapping per Destination" (destination level)',
         'One row per part and destination of the Waiting parts. Used for AP POLE WLM9Q860: Part Number, Destination Code (-> Buyer-PD), '
         'Dest Case/Day (-> Max Shipping Box Qty), Max Case/Day (quota) (-> Max Shipping Box Qty of the part) and Last Sync Date. '
         'A part without mapping has one row with an empty Destination Code (e.g. PART-B).', 'x_map_waiting.png'),
        ('step', 'Read sheet "Active to Inactive" (delete)',
         'Parts that went from Active to Inactive (monthly run of XD05) after their last successful sync: AP POLE still has them. One row per '
         'destination; Action = Delete in GTOPAS / AP POLE. Always every part of the master, whatever the search filter.', 'x_inactive.png'),
        ('step', 'Download the Part List (part level)',
         'Switch to the tab Part List (Procurement account), click [Search] without a filter, then [Export Excel]. The browser downloads '
         'Crossdock_Part_List_YYYYMMDD.xlsx.', 'n6_part_export.png'),
        ('step', 'Read sheet "Part List": filter Sync Status = Waiting',
         'In Excel: Data > Filter, column Sync Status = Waiting. Used for AP POLE WLM9Q890: Part Number (-> Part No.), Pcs/Case (-> Shipping Box Qty), '
         'Max Case/Day (-> Max Shipping Box Qty) and Status. The same parts are Waiting in both files.', 'x_part_waiting.png'),
    ],
    'notes': ['Download both files on the same day, after [Sync], and change nothing in NSP until the RPA has finished: a part changed after [Sync] goes back to No Sync.',
              'Sheet "Upload" of both files is not used for AP POLE (it is the upload format of NSP).',
              'When the RPA has finished, Sync Status becomes Success (Last Sync = the run date-time) or Failed (all parts of the run; click [Sync] again).']}

# AP POLE screen, item, value for one example
ACT = ['Screen', 'Action / item', 'Value']

DETAIL = {
    'sheet': '3. Scenario Detail',
    'title': 'Scenario detail: from the NSP Excel to AP POLE',
    'caption': 'Examples with the data of the files of sheet "0. Source Data (NSP)" (prototype dummy data). Excel pictures are extracts of the sheet; '
               'orange header = the columns used. "AP POLE now" values are an example of what the screen can show.',
    'meta': [('Function', 'XD07 RPA Cross Dock Master to AP POLE'),
             ('Input', 'Sheets Part List (Waiting), Mapping per Destination (Waiting) and Active to Inactive'),
             ('Rule', 'Part level first (WLM9Q890), then destination level (WLM9Q860). On WLM9Q860: Delete, then Edit, then Add, so that Total '
                      'Shipping Allocated never goes above Max Shipping Box Qty of the part.')],
    'blocks': [
        ('heading', 'A. How to choose the scenario'),
        ('table', 'Part level (WLM9Q890)', ['No', 'In the NSP file', 'Search on WLM9Q890', 'Scenario and action'], [
            ['P1', 'Part List: Status Active, Sync Status Waiting. Mapping: Last Sync Date empty (Never)', 'Part not found',
             'Candidate -> Active: [Add] Part No., Shipping Box Qty = Pcs/Case, Max Shipping Box Qty = Max Case/Day'],
            ['P2', 'Part List: Status Active, Sync Status Waiting. Mapping: Last Sync Date filled', 'Part not found (deleted when it went Inactive)',
             'Inactive -> Active: [Add] as P1'],
            ['P3', 'Sheet Active to Inactive', 'Part found', 'Active -> Inactive: tick the part, [Delete]'],
            ['P4', 'Part List: Status Active, Sync Status Waiting', 'Part found',
             'Still Active: compare Shipping Box Qty with Pcs/Case and Max Shipping Box Qty with Max Case/Day; [Edit] when one differs, else no change'],
         ], [6, 52, 30, 52]),
        ('table', 'Destination level (WLM9Q860, [Maintain Cross Dock] of the part)', ['No', 'Mapping per Destination vs Buyer-PD rows', 'Scenario', 'Action'], [
            ['D1', 'Destination Code in the file, no Buyer-PD row', 'Destination added', '[Add] Buyer-PD, Order Type **, Transport Code 2, Max Shipping Box Qty = Dest Case/Day'],
            ['D2', 'As D1, but Total Shipping Allocated = Max Shipping Box Qty (full)', 'Destination added, quota full', 'First D3 / D4 (free the quota), then D1'],
            ['D3', 'Buyer-PD row, Destination Code not in the file (also a part with an empty Destination Code)', 'Destination removed', 'Tick the row, [Delete]'],
            ['D4', 'Both, Max Shipping Box Qty <> Dest Case/Day', 'Dest Case/Day changed', '[Edit] Max Shipping Box Qty = Dest Case/Day'],
         ], [6, 52, 30, 52]),
        ('table', 'Buyer-PD from Destination Code', ['Destination Code (NSP)', 'Buyer-PD (AP POLE)', 'Rule'], [
            ['9722D10', '9722D-10', 'First 5 characters + "-" + last 2 characters'],
            ['9811110', '98111-10', ''],
            ['9715310', '97153-10', '']], [30, 30, 80]),

        ('heading', 'B. Example 1: PART-009, new part with 3 destinations (P1 + D1)'),
        ('text', 'NSP: Status Active, Sync Status Waiting, Last Sync Date empty (Never). Pcs/Case 5, Max Case/Day 19. Destinations 9722D10 = 7, '
                 '9811110 = 7, 9715310 = 5 (total 19). AP POLE now: WLM9Q890 [Search] Part No. PART-009 shows no data.'),
        ('image', 'Sheet Part List', 'x_ex1_part.png'),
        ('image', 'Sheet Mapping per Destination', 'x_ex1_map.png'),
        ('table', 'Action in AP POLE', ACT, [
            ['WLM9Q890', '[Add] Part No.', 'PART-009'],
            ['WLM9Q890', 'Shipping Box Qty / Max Shipping Box Qty', '5 / 19 (Max Allowance Qty = 95, by AP POLE), [Save]'],
            ['WLM9Q890', '[Search] PART-009, tick, [Maintain Cross Dock]', ''],
            ['WLM9Q860', '[Add] Buyer-PD / Order Type / Transport Code / Max Shipping Box Qty', '9722D-10 / ** / 2 / 7'],
            ['WLM9Q860', '[Add]', '98111-10 / ** / 2 / 7'],
            ['WLM9Q860', '[Add]', '97153-10 / ** / 2 / 5'],
            ['WLM9Q860', 'Check Total Shipping Allocated, [Back]', '19 (= Max Shipping Box Qty 19)']], [20, 60, 60]),

        ('heading', 'C. Example 2: PART-F, synced before, values changed (P4 + D3 + D4 + D1)'),
        ('text', 'NSP: Status Active, Sync Status Waiting, Last Sync Date 28-Aug-2026 10:05. Pcs/Case 40, Max Case/Day 26. Destinations 9715310 = 12, '
                 '9722D10 = 8, 9811110 = 6 (total 26). AP POLE now (example): Shipping Box Qty 40, Max Shipping Box Qty 24; Buyer-PD 97153-10 = 12, '
                 '9722D-10 = 10, 97101-10 = 2 (Total Shipping Allocated 24, full).'),
        ('image', 'Sheet Part List', 'x_ex2_part.png'),
        ('image', 'Sheet Mapping per Destination', 'x_ex2_map.png'),
        ('table', 'Action in AP POLE (in this order)', ACT, [
            ['WLM9Q890', '[Search] PART-F: found, Max Shipping Box Qty 24 <> 26: tick, [Edit] (P4)', 'Shipping Box Qty 40, Max Shipping Box Qty 26, [Save]'],
            ['WLM9Q890', 'Tick, [Maintain Cross Dock]', ''],
            ['WLM9Q860', '97101-10 is not in the file: tick, [Delete] (D3)', 'Total Shipping Allocated 24 -> 22'],
            ['WLM9Q860', '9722D-10 10 <> 8: tick, [Edit] (D4)', 'Max Shipping Box Qty 8; total 22 -> 20'],
            ['WLM9Q860', '97153-10 12 = 12', 'No change'],
            ['WLM9Q860', '98111-10 has no row: [Add] (D1)', '98111-10 / ** / 2 / 6; total 20 -> 26'],
            ['WLM9Q860', 'Check Total Shipping Allocated, [Back]', '26 (= Max Shipping Box Qty 26)']], [20, 60, 60]),

        ('heading', 'D. Example 3: PART-023, Active to Inactive (P3)'),
        ('text', 'NSP: sheet Active to Inactive, 2 rows (9715310, 9722D10), Status Changed Date 01-Oct-2026 02:00 later than Last Sync Date 28-Sep-2026 10:15. '
                 'AP POLE now: the part with Buyer-PD 97153-10 and 9722D-10.'),
        ('image', 'Sheet Active to Inactive', 'x_ex3_inactive.png'),
        ('table', 'Action in AP POLE', ACT, [
            ['WLM9Q890', '[Search] PART-023: found', ''],
            ['WLM9Q890', 'Tick the part, [Delete]', 'The part is removed. Buyer-PD rows of the part: deleted with the part (TBC); when AP POLE refuses, '
                                                      'first [Maintain Cross Dock] and [Delete] 97153-10 and 9722D-10 on WLM9Q860']], [20, 60, 60]),

        ('heading', 'E. Example 4: PART-B, part without destination (P1, no D)'),
        ('text', 'NSP: Status Active, Waiting, Never synced, Pcs/Case 12, Max Case/Day 40, Destination Code empty (Total Case/Day 0 / 40). '
                 'AP POLE now: no data.'),
        ('image', 'Sheet Mapping per Destination', 'x_ex4_map.png'),
        ('table', 'Action in AP POLE', ACT, [
            ['WLM9Q890', '[Add] Part No. / Shipping Box Qty / Max Shipping Box Qty', 'PART-B / 12 / 40, [Save]'],
            ['WLM9Q860', 'No destination in the file', 'Nothing to add. A part that was synced before and lost all destinations: [Delete] its Buyer-PD rows (D3)']], [20, 60, 60]),
    ],
    'notes': ['Inactive -> Active (P2) has no example in the dummy data: same as Example 1 (Add), only Last Sync Date is filled.',
              'Any error in AP POLE (message, time out) stops the run: every Waiting part becomes Failed in NSP and is sent again with the next [Sync].']}
