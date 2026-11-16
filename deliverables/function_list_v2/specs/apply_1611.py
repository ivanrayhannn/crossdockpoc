"""16-Nov: revision history of XD09, XD10 and XD11 (Revision sheet + Updated in the header). Runs last in the build chain.
One row per change; the revision number, author and date are on the first row of each revision."""
import json

AUTHOR = 'FID Rayhan'
INITIAL = {'revision': '0.1', 'author': AUTHOR, 'date': '18-Oct-26', 'reviewed_by': '', 'description': 'Initial Draft'}


def rev(no, date, lines):
    return [{'revision': no if i == 0 else '', 'author': AUTHOR if i == 0 else '', 'date': date if i == 0 else '',
             'reviewed_by': '', 'description': d} for i, d in enumerate(lines)]


REVISIONS = {
    'XD09': [INITIAL] + rev('0.2', '11-Nov-26', [
        '4.2 PO Assignment: pouring of the PO qty (Part Number level) over the customer order lines, top line first, oldest PO first; '
        'line split per PO; no PO left = PO_NO NULL (FB-172).',
    ]) + rev('0.3', '13-Nov-26', [
        'Dummy data: supplier 5001-1 / 5002-1, PO-0001.., MF-0001.., destinations Korea / Japan / Taiwan / Australia.',
        'Inputs TB_R_CROSSDOCK_PART_HOLD and TB_R_CROSSDOCK_CASE_HOLD (holds of the D/S team on XD10); CROSSDOCK_STATUS \'8\' On Hold.',
    ]) + rev('0.4', '14-Nov-26', [
        'Hold per case: the held pcs (customer order line + HOLD_QTY) are taken out before the PO pouring; '
        'their PO qty goes to the next lines; the other cases keep their own readiness.',
        'Released line (HOLD_FLAG N): poured and cut at the end of its Customer Order Date, before the newer dates (FB-183).',
    ]) + rev('0.5', '16-Nov-26', [
        'Table concept from the DR XD09 (11-Nov): #TEMP_INSTRUCTION replaced by TB_T_INSTRUCTION_H (one row per unit: open qty, Case Qty, '
        'SUBMIT_ASN_STS) and TB_T_INSTRUCTION_D (one row per pc: order qty and PO qty broken down to 1, PO, CASE_NO, HOLD_STS).',
        'Rows per company of the login user (LEFT(CREATE_BY, 4)), deleted and inserted again at each run; company 1000 sees all suppliers.',
        'CASE_NO made by XD09 from TB_R_CASE_LABEL_LAST_SEQ (same CASE_NO for PCS_CASE pcs); input TB_R_CASE_LABEL_LAST_SEQ added.',
        'Added to the DR table for the rules of 4.1-4.3: SEQ_NO, CUSTOMER_CD, CUT_FLAG, GROUP_SEQ, CROSSDOCK_STATUS.',
        'No new table TB_R_PRA_DAILY_ORDER_MAPPED: open PO qty = REMAIN_QTY of the existing TB_R_PRA_DAILY_ORDER_PART.',
    ]),
    'XD10': [INITIAL] + rev('0.2', '11-Nov-26', [
        'Pre-mapping refers to the pouring rule of XD09 4.2 (FB-172).',
    ]) + rev('0.3', '13-Nov-26', [
        'Sub screen [Hold per Part] (D/S team): one row per Part Number, Hold check box with Edit / Save / Cancel; '
        'expanded customer orders without PO information (TB_R_CROSSDOCK_PART_HOLD, MSG12).',
        'Hold (D/S) check box per case next to PO Status, changed with [Edit hold] / [Save] / [Cancel] per Part Number + '
        'Customer Order Date (TB_R_CROSSDOCK_CASE_HOLD, MSG14).',
        'Case content split into the columns Destination, Customer Order No and Order Qty.',
        'Dummy data: supplier 5001-1 / 5002-1, PO-0001.., MF-0001.., destinations Korea / Japan / Taiwan / Australia.',
    ]) + rev('0.4', '14-Nov-26', [
        'Hold per case: the held pcs leave the unit and take no PO; their PO qty goes to the next orders; the other cases stay Ready. '
        'Held lines listed below the cases (On hold, PO released).',
        'Release of a held line: goes to the end of its Customer Order Date, keeps priority over newer dates (FB-183, HOLD_FLAG).',
        '[Save] of a hold: confirmation and success pop up in Indonesian (MSG15 / MSG16), delivery plan refreshed.',
        'PO check line replaced by the PO information pop up on the ASN status (MSG17); Hold chip with hold information (MSG18).',
        'Bordered unit table and case grid; destination once per case; same PO merged; summary line of the delivery plan removed.',
        'Destination detail (Destination / pcs, Hold Flag) hidden on the screen for now (FB-184).',
    ]) + rev('0.5', '16-Nov-26', [
        'Source of the delivery plan: TB_T_INSTRUCTION_H / TB_T_INSTRUCTION_D (table concept of the DR XD09) instead of #TEMP_INSTRUCTION.',
        'Case No of the ASN = CASE_NO of the draft made by XD09; Submit ASN no longer generates the case numbers (ASN number as existing).',
        'No new table TB_R_PRA_DAILY_ORDER_MAPPED: [Create ASN] reduces REMAIN_QTY of TB_R_PRA_DAILY_ORDER_PART; Back / Cancel / submit error add it back.',
    ]),
    'XD11': [INITIAL] + rev('0.2', '13-Nov-26', [
        'Dummy data: supplier 5001-1 / 5002-1, PO-0001.., MF-0001.., destinations Korea / Japan / Taiwan / Australia.',
    ]) + rev('0.3', '16-Nov-26', [
        'Table TB_R_PRA_DAILY_ORDER_MAPPED removed from the table list: the PO qty is REMAIN_QTY of TB_R_PRA_DAILY_ORDER_PART.',
    ]),
}

for fid, revs in REVISIONS.items():
    path = f'{fid}_spec.json'
    with open(path) as fh:
        s = json.load(fh)
    s['revisions'] = revs
    last = [r for r in revs if r['revision']][-1]
    s['header']['updated_date'] = last['date']
    s['header']['updated_by'] = AUTHOR
    with open(path, 'w') as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    print('revisions', fid, last['revision'], last['date'])
