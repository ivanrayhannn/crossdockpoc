"""User guide: keep the GTOPAS Crossdock Master equal to NSP (XD06, RPA on GTOPAS screen WVJA5204), same layout as the AP POLE guide.
Sheets: 0 source data in NSP (prototype screenshots, guide_shots_gt.mjs), 1 GTOPAS screen, 2 scenario detail (render_gt.py).
No screenshot of GTOPAS is available yet: the GTOPAS lists are illustrations with example data. Run: python3 build_gtopas_guide.py"""
import os
from openpyxl import Workbook
from build_ap_pole_guide import build_sheet

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Crossdock_User_Guide_GTOPAS.xlsx')
NSP_CAP = ('Screens from the NSP prototype: header "Supplier System" is NSP; "Preview ... / Switch sub-menu" exists only in the prototype. '
           'Red box = the item to click. Excel pictures: orange header = column used for GTOPAS, yellow rows = examples of sheet "2. Scenario Detail".')
GT_CAP = ('Screenshot of GTOPAS WVJA5204 given by the user (one row searched and deleted). The GTOPAS lists with several rows are '
          'illustrations of the same list with example data.')

SOURCE = {
    'sheet': '0. Source Data (NSP)',
    'title': 'NSP: get the source data for GTOPAS (Crossdock Master Setting)',
    'caption': NSP_CAP,
    'meta': [('Function', 'XD01 Crossdock Master Setting ([Sync], Export Excel) as the source of XD06 RPA Cross Dock Master to GTOPAS'),
             ('User', 'D/S team: only [Sync]. Everything after [Sync] is done by the RPA bot: download, Excel, GTOPAS (decided 17-Nov)'),
             ('Result', 'Crossdock_Mapping_per_Destination_<Period>_YYYYMMDD.xlsx, sheet Mapping per Destination (NSP list)'),
             ('NSP list', 'Every Active part of the ongoing period with its Destination Codes (one row per part + destination), whatever the Sync Status')],
    'blocks': [
        ('table', 'Who does what', ['No', 'Who', 'What'], [
            ['1', 'D/S team', 'Crossdock Master Setting, tab Mapping per Destination, ongoing period: click [Sync] (steps 1 and 2)'],
            ['2', 'RPA bot', 'Log in to NSP, [Export Excel] of Mapping per Destination (ongoing period, Sync Status All) and open the file (steps 3 to 5)'],
            ['3', 'RPA bot', 'GTOPAS WVJA5204: Search Depot 01, read every page (sheet "1. GTOPAS Crossdock Master")'],
            ['4', 'RPA bot', 'Add the sheet GTOPAS Compare to the file: Keep / Add / Delete per P/No. + Destination Code (sheet "2. Scenario Detail")'],
            ['5', 'RPA bot', 'Add / delete the rows in GTOPAS; write Result and GTOPAS message per row in GTOPAS Compare'],
            ['6', 'RPA bot', 'Write the result to NSP: Sync Status Success (Last Sync) or Failed; the file stays as evidence of the run']], [6, 34, 100]),
        ('step', 'D/S: open Crossdock Master Setting, tab Mapping per Destination',
         'In the left menu click Master > Crossdock Master Setting. With the D/S account the screen opens on the tab Mapping per Destination.', 'g1_map_menu.png'),
        ('step', 'D/S: search the ongoing period and click [Sync]',
         'Calculation period = the ongoing period (e.g. Sep 2026 (ongoing)), Sync Status = All, click [Search]. Click [Sync (n)]: every part with '
         'status Active (ongoing period) or Inactive and Sync Status No Sync or Failed becomes Waiting (Candidate never) and the RPA bot starts. This is the last manual step.', 'g2_map_sync.png'),
        ('step', 'Bot: download the Excel ([Export Excel], Sync Status All)',
         'The bot logs in to NSP, opens the same screen, ongoing period, Sync Status = All (GTOPAS keeps only Part + Destination Code, so the '
         'whole list is compared, not only the Waiting parts), Part Number empty, clicks [Search] and [Export Excel], and opens '
         'Crossdock_Mapping_per_Destination_Sep_2026_YYYYMMDD.xlsx.', 'g3_map_export.png'),
        ('step', 'Bot: read sheet "Mapping per Destination" = NSP list',
         'One row per Active part and Destination Code of the ongoing period. Only Part Number and Destination Code are used for GTOPAS '
         '(Dest Case/Day is not sent). A row with an empty Destination Code = Active part without destination: GTOPAS must have no row for it.',
         'x_gt_nsp_all.png'),
    ],
    'notes': ['Change nothing in NSP from [Sync] until the RPA has finished: a part changed in between goes back to No Sync.',
              'Sheet "Upload" of the file is not used for GTOPAS.',
              'When the RPA has finished, Sync Status becomes Success (Last Sync = run date-time) when AP POLE (XD07) is also done, or Failed.']}

SCREEN = {
    'sheet': '1. GTOPAS Crossdock Master',
    'title': 'GTOPAS: Crossdock Master (WVJA5204)',
    'caption': GT_CAP,
    'meta': [('Function', 'XD06 RPA Cross Dock Master to GTOPAS'),
             ('Screen', 'GTOPAS WVJA5204 Crossdock Master, menu Supply > Master > Crossdock Master'),
             ('User', 'RPA bot, started by [Sync] (the same steps can be done by the D/S team by hand as a fallback)'),
             ('Compare key', 'P/No. (without "-") + Destination Code. GTOPAS shows P/No. with "-" (52119-BZV60), NSP without (52119BZV60)')],
    'blocks': [
        ('step', 'Open Crossdock Master', 'Log in to GTOPAS and open the menu Supply > Master > Crossdock Master (WVJA5204).', None),
        ('step', 'Search Depot Code 01',
         'Depot Code = 01 (mandatory, yellow). Leave P/No., Destination Code, Maker Code, Dom/Os, TOPAS Order Type and Trans Code blank to list '
         'every row, or fill P/No. (without "-", e.g. 52119BZV60) + Destination Code (e.g. 9618274) to find one row. Click [Search]. '
         'The list shows P/No. with "-" (52119-BZV60).', 'g01_wvja5204_delete.png'),
        ('step', 'Read every page',
         'Click [NextPage] until the last page and note every row: P/No. + Destination Code (one row per part and destination).', None),
        ('image', 'GTOPAS list before the run (example of sheet "2. Scenario Detail")', 'x_gt_before.png'),
        ('step', 'Compare and fill the sheet GTOPAS Compare',
         'For every P/No. + Destination Code: in NSP and in GTOPAS = Keep; in NSP only = Add; in GTOPAS only = Delete. The bot writes the rows '
         'to the new sheet GTOPAS Compare of the downloaded file. Refer sheet "2. Scenario Detail".', None),
        ('step', 'Add a row (register)',
         'Add a new row with the fixed values of the table below and the P/No. + Destination Code of NSP. Register. Message MZD34006FEI '
         '"Registration completed" = done.', None),
        ('table', 'Values of a new row', ['GTOPAS item', 'Value', 'Source'], [
            ['Depot Code', '01', 'Fixed'],
            ['Maker Code', 'A', 'Fixed (decided 11-Nov)'],
            ['P/No.', 'Part Number of NSP', 'Mapping per Destination, Part Number (GTOPAS shows it with "-")'],
            ['Domestic/Overseas', '2', 'Fixed (decided 11-Nov)'],
            ['Destination Code', 'Destination Code of NSP', 'Mapping per Destination, Destination Code: the same 7 characters, no conversion'],
            ['TOPAS Order Type', '3', 'Fixed (decided 11-Nov). The screenshot shows "*" on an existing row: 3 or * TBC (FB-203)'],
            ['Order Transportation Code', '2', 'Fixed (decided 11-Nov)']], [40, 50, 50]),
        ('step', 'Delete a row',
         'Search the row (P/No. + Destination Code), set MT = DEL on the row and register. Message "MZD34006FEI: Registration completed." = done '
         '(screenshot of step 2: 52119-BZV60 + 9618274 deleted).', None),
        ('step', 'Check the result',
         'After each Add / Delete the bot writes Result (OK) and the GTOPAS message in GTOPAS Compare. At the end the GTOPAS list (Depot 01) has '
         'exactly the rows of the NSP list, and Sync Status in NSP becomes Success (when AP POLE is also done).', None),
        ('image', 'GTOPAS list after the run (example)', 'x_gt_after.png'),
    ],
    'notes': ['Column R of the list shows "O" on the row of the screenshot: meaning TBC (not used by the RPA).',
              'Any other message than MZD34006FEI (error, time out, screen not available) stops the RPA: the run is Failed for every Waiting part; '
              'rows already added or deleted stay, the next [Sync] compares again and completes the rest.',
              'FB-176: every GTOPAS row of Depot 01 that is not in NSP is deleted. At go-live all crossdock parts of GTOPAS must exist in NSP.']}

ACT = ['Screen', 'Action', 'P/No. + Destination Code']
DETAIL = {
    'sheet': '2. Scenario Detail',
    'title': 'Scenario detail: from the NSP Excel to GTOPAS',
    'caption': 'Examples with the data of the file of sheet "0. Source Data (NSP)" (prototype dummy data). ' + GT_CAP,
    'meta': [('Function', 'XD06 RPA Cross Dock Master to GTOPAS'),
             ('Input', 'Sheet Mapping per Destination (ongoing period, all Sync Status)'),
             ('Rule', 'Destination of the ongoing period in NSP: already in GTOPAS = keep; not in GTOPAS = add P/No. + Destination Code; '
                      'in GTOPAS but not in NSP = delete')],
    'blocks': [
        ('heading', 'A. How to choose the scenario'),
        ('table', 'Per P/No. + Destination Code', ['No', 'NSP list (ongoing period) vs GTOPAS (Depot 01)', 'Action'], [
            ['S1', 'In NSP and in GTOPAS', 'Keep: no change (also when only Dest Case/Day, Pcs/Case or Max Case/Day changed: GTOPAS keeps no quantity)'],
            ['S2', 'In NSP, not in GTOPAS (new Active part, new destination, Inactive -> Active)', 'Add the row: P/No., Destination Code + fixed values'],
            ['S3', 'In GTOPAS, not in NSP (destination removed in NSP)', 'Delete the row (MT = DEL)'],
            ['S3', 'Part Inactive (not in the sheet), Candidate, or not in NSP', 'Delete all rows of the part'],
            ['S3', 'Active part without destination (empty Destination Code)', 'Delete all rows of the part; nothing to add']], [6, 34, 100]),
        ('image', 'Comparison of the examples below (green = keep, blue = add, red = delete)', 'x_gt_compare.png'),
        ('image', 'The same rows in the sheet GTOPAS Compare, filled by the bot after the actions (Result, message, date-time)', 'x_gt_work.png'),

        ('heading', 'B. Example 1: PART-009, new part with 3 destinations (S2)'),
        ('text', 'NSP: 3 rows 9722D10, 9811110, 9715310 (Last Sync Date empty). GTOPAS now: [Search] P/No. PART-009 shows no data.'),
        ('image', 'Sheet Mapping per Destination', 'x_gt_ex1_nsp.png'),
        ('table', 'Action in GTOPAS', ACT, [
            ['WVJA5204', 'Add (S2)', 'PART-009 + 9722D10 (Depot 01, Maker A, Dom/Os 2, Order Type 3, Trans 2)'],
            ['WVJA5204', 'Add (S2)', 'PART-009 + 9811110'],
            ['WVJA5204', 'Add (S2)', 'PART-009 + 9715310']], [20, 60, 60]),

        ('heading', 'C. Example 2: PART-012, no change (S1)'),
        ('text', 'NSP: 9722D10, Sync Status Success. GTOPAS now: PART-012 + 9722D10.'),
        ('image', 'Sheet Mapping per Destination', 'x_gt_ex2_nsp.png'),
        ('image', 'GTOPAS now', 'x_gt_ex2_gt.png'),
        ('table', 'Action in GTOPAS', ACT, [['WVJA5204', 'Keep (S1), no action', 'PART-012 + 9722D10']], [20, 60, 60]),

        ('heading', 'D. Example 3: PART-F, destinations changed (S1 + S2 + S3)'),
        ('text', 'NSP: 9715310 (12), 9722D10 (8), 9811110 (6), Last Sync 28-Aug-2026. GTOPAS now (example): 9715310, 9722D10, 9710110. '
                 'The Case/Day values do not matter for GTOPAS.'),
        ('image', 'Sheet Mapping per Destination', 'x_gt_ex3_nsp.png'),
        ('image', 'GTOPAS now', 'x_gt_ex3_gt.png'),
        ('table', 'Action in GTOPAS', ACT, [
            ['WVJA5204', 'Keep (S1)', 'PART-F + 9715310'],
            ['WVJA5204', 'Keep (S1)', 'PART-F + 9722D10'],
            ['WVJA5204', 'Add (S2)', 'PART-F + 9811110'],
            ['WVJA5204', 'Delete (S3), MT = DEL', 'PART-F + 9710110']], [20, 60, 60]),

        ('heading', 'E. Example 4: PART-B, Active part without destination (S3)'),
        ('text', 'NSP: one row with an empty Destination Code. GTOPAS now: no row of PART-B. When GTOPAS still has rows of the part (e.g. a '
                 'destination removed in NSP), delete them all.'),
        ('image', 'Sheet Mapping per Destination', 'x_gt_ex4_nsp.png'),
        ('table', 'Action in GTOPAS', ACT, [['WVJA5204', 'Nothing to add; delete any row of the part (S3)', 'PART-B (none)']], [20, 60, 60]),

        ('heading', 'F. Example 5: PART-023, Inactive part (S3)'),
        ('text', 'NSP: PART-023 is Inactive (went Inactive on 01-Oct-2026), so it is not in sheet Mapping per Destination. '
                 'GTOPAS now: PART-023 + 9715310, PART-023 + 9722D10.'),
        ('image', 'GTOPAS now', 'x_gt_ex5_gt.png'),
        ('table', 'Action in GTOPAS', ACT, [
            ['WVJA5204', 'Delete (S3), MT = DEL', 'PART-023 + 9715310'],
            ['WVJA5204', 'Delete (S3), MT = DEL', 'PART-023 + 9722D10']], [20, 60, 60]),
        ('image', 'GTOPAS list after the run (examples only)', 'x_gt_after.png'),
    ],
    'notes': ['Part numbers of the prototype (PART-009) are dummy data; real P/No. are compared without "-" (GTOPAS 52119-BZV60 = NSP 52119BZV60).',
              'Destination Code is compared as is: the same 7 characters in NSP and GTOPAS (no "-" as in AP POLE Buyer-PD).']}


def main():
    wb = Workbook()
    wb.remove(wb.active)
    for g in (SOURCE, SCREEN, DETAIL):
        build_sheet(wb, g)
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
