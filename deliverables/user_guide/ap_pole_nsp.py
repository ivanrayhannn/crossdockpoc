"""Sheets 0 and 3 of Crossdock_User_Guide_AP_POLE.xlsx: the source data in NSP (prototype Crossdock Master Setting) and every scenario
worked out from the exported Excel to the AP POLE values. Screenshots: guide_shots_ap.mjs; Excel extracts: render_ap.py (shots_ap/)."""

SOURCE = {
    'sheet': '0. Source Data (NSP)',
    'title': 'NSP: get the source data for AP POLE (Crossdock Master Setting)',
    'caption': 'Screens from the NSP prototype: header "Supplier System" is NSP; "Preview ... / Switch sub-menu" exists only in the prototype. '
               'Red box = the item to click. Excel pictures: orange header = column read for AP POLE, yellow rows = examples of sheet "3. Scenario Detail".',
    'meta': [('Function', 'XD01 Crossdock Master Setting ([Sync], Export Excel) as the source of XD07 RPA Cross Dock Master to AP POLE'),
             ('User', 'D/S team: only [Sync]. The RPA bot downloads the two files, fills a work sheet AP POLE Compare and works on AP POLE (17-Nov)'),
             ('Result', 'Crossdock_Export_Master_<Period>_YYYYMMDD.xlsx (sheet Export Crossdock Master) and '
                        'Crossdock_Kanban_Master_YYYYMMDD.xlsx (sheet Kanban Crossdock Master)')],
    'blocks': [
        ('step', 'D/S: open Crossdock Master Setting, tab Export Crossdock Master',
         'In the left menu click Master > Crossdock Master Setting. With the D/S account the screen opens on the tab Export Crossdock Master.', 'n1_map_menu.png'),
        ('step', 'D/S: search the ongoing period and click [Sync]',
         'Calculation period = the ongoing period (e.g. Sep 2026 (ongoing)), Sync Status = All, click [Search]. Click [Sync (n)]: every part with '
         'status Active (ongoing period) or Inactive and Sync Status No Sync becomes Sent (Candidate never). n = number of parts that will be sent to GTOPAS and AP POLE. '
         'The button is disabled when there is nothing to sync. [Sync] starts the RPA bot: the next steps are done by the bot.', 'n2_map_sync.png'),
        ('step', 'Bot: search the parts of the run (Sync Status = Sent)',
         'Sync Status = Sent, click [Search]. The parts of this run are the rows whose Last Sent = the send time of the run (rows sent '
         'earlier keep an older Last Sent and are not processed again). Whether AP POLE already has the part is found by the search on '
         'WLM9Q890 (found = Edit, not found = Add).', 'n3_map_waiting.png'),
        ('step', 'Destinations of a part (for checking only)',
         'Click the arrow > in front of the Part Number. Example PART-009: 3 destinations, Case/Day 7 + 7 + 5 = 19 = Max Case/Day (19 / 19, 100%). '
         'These rows become the Buyer-PD rows of WLM9Q860 in AP POLE.', 'n4_map_dest.png'),
        ('step', 'Bot: download Export Crossdock Master ([Export Excel], Sent)',
         'With Sync Status = Sent and Part Number empty, click [Export Excel]. The browser downloads '
         'Crossdock_Export_Master_Sep_2026_YYYYMMDD.xlsx (period of step 2, download date) and the bot opens it.', 'n5_map_export.png'),
        ('step', 'Bot: read sheet "Export Crossdock Master" (destination level)',
         'One row per part and destination of the parts of the run. Used for AP POLE WLM9Q860: Part Number, Destination Code (-> Buyer-PD), '
         'Dest Case/Day (-> Max Shipping Box Qty), Max Case/Day (quota) (-> Max Shipping Box Qty of the part) and Last Sent AP POLE. '
         'A part without mapping has one row with an empty Destination Code (e.g. PART-B).', 'x_map_waiting.png'),
        ('step', 'Bot: download the Kanban Crossdock Master (part level)',
         'The bot opens the tab Kanban Crossdock Master, clicks [Search] without a filter, then [Export Excel]. The browser downloads '
         'Crossdock_Kanban_Master_YYYYMMDD.xlsx.', 'n6_part_export.png'),
        ('step', 'Bot: read sheet "Kanban Crossdock Master" (parts of the run)',
         'The bot filters Sync Status = Sent and Last Sent AP POLE = the send time of the run. Used for AP POLE WLM9Q890: Part Number (-> Part No.), Pcs/Case (-> Shipping Box Qty), '
         'Max Case/Day (-> Max Shipping Box Qty) and Status. Status Inactive (e.g. PART-023) = delete in AP POLE. The same parts are Sent in both files.', 'x_part_waiting.png'),
    ],
    'notes': ['Change nothing in NSP from [Sync] until the RPA has finished: a part changed in between goes back to No Sync.',
              'The bot adds a work sheet AP POLE Compare to the downloaded file: per part / Buyer-PD the NSP value, the AP POLE value, the action '
              '(Add / Edit / Delete / Keep), Result and AP POLE message. The file stays as the evidence of the run.',
              'Sheet "Upload" of both files is not used for AP POLE (it is the upload format of NSP).',
              'No response from the RPA (20-Nov): NSP keeps Sent. The result comes by e-mail [Crossdock Sync][...][SUCCESS | FAILED]; when FAILED, click [Re-send last Sync].']}

# AP POLE screen, item, value for one example
ACT = ['Screen', 'Action / item', 'Value']

DETAIL = {
    'sheet': '3. Scenario Detail',
    'title': 'Scenario detail: from the NSP Excel to AP POLE',
    'caption': 'Examples with the data of the files of sheet "0. Source Data (NSP)" (prototype dummy data). Excel pictures are extracts of the sheet; '
               'orange header = the columns used. "AP POLE now" values are an example of what the screen can show.',
    'meta': [('Function', 'XD07 RPA Cross Dock Master to AP POLE'),
             ('Input', 'Sheets Kanban Crossdock Master (Sent) and Export Crossdock Master (Sent)'),
             ('Rule', 'Part level first (WLM9Q890), then destination level (WLM9Q860). On WLM9Q860: Delete, then Edit, then Add, so that Total '
                      'Shipping Allocated never goes above Max Shipping Box Qty of the part.')],
    'blocks': [
        ('heading', 'A. How to choose the scenario'),
        ('table', 'Part level (WLM9Q890)', ['No', 'In the NSP file', 'Search on WLM9Q890', 'Scenario and action'], [
            ['P1', 'Kanban Crossdock Master: Status Active, Sync Status Sent. part of the run', 'Part not found (never sent before)',
             'Candidate -> Active: [Add] Part No., Shipping Box Qty = Pcs/Case, Max Shipping Box Qty = Max Case/Day'],
            ['P2', 'Kanban Crossdock Master: Status Active, Sync Status Sent. part of the run', 'Part not found (deleted when it went Inactive)',
             'Inactive -> Active: [Add] as P1'],
            ['P3', 'Kanban Crossdock Master: Status Inactive, Sync Status Sent', 'Part found (not found: nothing to delete)', 'Active -> Inactive: tick the part, [Delete]'],
            ['P4', 'Kanban Crossdock Master: Status Active, Sync Status Sent', 'Part found',
             'Still Active: compare Shipping Box Qty with Pcs/Case and Max Shipping Box Qty with Max Case/Day; [Edit] when one differs, else no change'],
         ], [6, 52, 30, 52]),
        ('table', 'Destination level (WLM9Q860, [Maintain Cross Dock] of the part)', ['No', 'Export Crossdock Master vs Buyer-PD rows', 'Scenario', 'Action'], [
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
        ('text', 'NSP: Status Active, Sync Status Sent (this run), never sent before. Pcs/Case 5, Max Case/Day 19. Destinations 9722D10 = 7, '
                 '9811110 = 7, 9715310 = 5 (total 19). AP POLE now: WLM9Q890 [Search] Part No. PART-009 shows no data.'),
        ('image', 'Sheet Kanban Crossdock Master', 'x_ex1_part.png'),
        ('image', 'Sheet Export Crossdock Master', 'x_ex1_map.png'),
        ('table', 'Action in AP POLE', ACT, [
            ['WLM9Q890', '[Add] Part No.', 'PART-009'],
            ['WLM9Q890', 'Shipping Box Qty / Max Shipping Box Qty', '5 / 19 (Max Allowance Qty = 95, by AP POLE), [Save]'],
            ['WLM9Q890', '[Search] PART-009, tick, [Maintain Cross Dock]', ''],
            ['WLM9Q860', '[Add] Buyer-PD / Order Type / Transport Code / Max Shipping Box Qty', '9722D-10 / ** / 2 / 7'],
            ['WLM9Q860', '[Add]', '98111-10 / ** / 2 / 7'],
            ['WLM9Q860', '[Add]', '97153-10 / ** / 2 / 5'],
            ['WLM9Q860', 'Check Total Shipping Allocated, [Back]', '19 (= Max Shipping Box Qty 19)']], [20, 60, 60]),

        ('heading', 'C. Example 2: PART-F, synced before, values changed (P4 + D3 + D4 + D1)'),
        ('text', 'NSP: Status Active, Sync Status Sent (this run), sent before on 28-Aug-2026. Pcs/Case 40, Max Case/Day 26. Destinations 9715310 = 12, '
                 '9722D10 = 8, 9811110 = 6 (total 26). AP POLE now (example): Shipping Box Qty 40, Max Shipping Box Qty 24; Buyer-PD 97153-10 = 12, '
                 '9722D-10 = 10, 97101-10 = 2 (Total Shipping Allocated 24, full).'),
        ('image', 'Sheet Kanban Crossdock Master', 'x_ex2_part.png'),
        ('image', 'Sheet Export Crossdock Master', 'x_ex2_map.png'),
        ('table', 'Action in AP POLE (in this order)', ACT, [
            ['WLM9Q890', '[Search] PART-F: found, Max Shipping Box Qty 24 <> 26: tick, [Edit] (P4)', 'Shipping Box Qty 40, Max Shipping Box Qty 26, [Save]'],
            ['WLM9Q890', 'Tick, [Maintain Cross Dock]', ''],
            ['WLM9Q860', '97101-10 is not in the file: tick, [Delete] (D3)', 'Total Shipping Allocated 24 -> 22'],
            ['WLM9Q860', '9722D-10 10 <> 8: tick, [Edit] (D4)', 'Max Shipping Box Qty 8; total 22 -> 20'],
            ['WLM9Q860', '97153-10 12 = 12', 'No change'],
            ['WLM9Q860', '98111-10 has no row: [Add] (D1)', '98111-10 / ** / 2 / 6; total 20 -> 26'],
            ['WLM9Q860', 'Check Total Shipping Allocated, [Back]', '26 (= Max Shipping Box Qty 26)']], [20, 60, 60]),

        ('heading', 'D. Example 3: PART-023, Inactive part (P3)'),
        ('text', 'NSP: sheet Kanban Crossdock Master, Status Inactive, Sync Status Sent (went Inactive on 01-Oct-2026 after the last sync of 28-Sep-2026). '
                 'AP POLE now: the part with Buyer-PD 97153-10 and 9722D-10.'),
        ('image', 'Sheet Kanban Crossdock Master', 'x_ex3_part.png'),
        ('table', 'Action in AP POLE', ACT, [
            ['WLM9Q890', '[Search] PART-023: found', ''],
            ['WLM9Q890', 'Tick the part, [Delete]', 'The part is removed. Buyer-PD rows of the part: deleted with the part (TBC); when AP POLE refuses, '
                                                      'first [Maintain Cross Dock] and [Delete] 97153-10 and 9722D-10 on WLM9Q860']], [20, 60, 60]),

        ('heading', 'E. Example 4: PART-B, part without destination (P1, no D)'),
        ('text', 'NSP: Status Active, Sent (this run), never sent before, Pcs/Case 12, Max Case/Day 40, Destination Code empty (Total Case/Day 0 / 40). '
                 'AP POLE now: no data.'),
        ('image', 'Sheet Export Crossdock Master', 'x_ex4_map.png'),
        ('table', 'Action in AP POLE', ACT, [
            ['WLM9Q890', '[Add] Part No. / Shipping Box Qty / Max Shipping Box Qty', 'PART-B / 12 / 40, [Save]'],
            ['WLM9Q860', 'No destination in the file', 'Nothing to add. A part that was synced before and lost all destinations: [Delete] its Buyer-PD rows (D3)']], [20, 60, 60]),
    ],
    'notes': ['Inactive -> Active (P2) has no example in the dummy data: same as Example 1 (Add): the part is not found in AP POLE.',
              'Any error in AP POLE (message, time out) stops the run: the e-mail is FAILED; D/S clicks [Re-send last Sync].']}
