"""Simulation (old table concept): H0253 replicate -> #TEMP_INSTRUCTION ([Search], session) -> TB_R_INSTRUCTION ([Create ASN])
-> Case No at Submit, with the hold per case in TB_R_CROSSDOCK_CASE_HOLD (order line + HOLD_QTY). PART-X, supplier 5001-1, 6 pcs/case.
Run: python3 build_sim_case_hold_old.py"""
import os
from openpyxl import Workbook
from build_sim_fb182 import BAD, FB, HOLD, OK, sheet, table

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD09_XD10_Simulation_Case_Hold_Old_Concept.xlsx')
PCS = 6
SUP, PLANT, PART = '5001', '1', 'PART-X'
KR, JP, TW, AU = '9715310', '9722D10', '9811110', '982220'
NAME = {KR: 'Korea', JP: 'Japan', TW: 'Taiwan', AU: 'Australia'}
CUST = {KR: '9715300', JP: '9722D00', TW: '9811100', AU: '982200'}
D17 = [('CO-14105', KR, 6), ('CO-14106', KR, 3), ('CO-14107', KR, 3), ('CO-14104', JP, 6), ('CO-14109', TW, 6), ('CO-14110', AU, 6)]
D18 = [('CO-14112', KR, 6), ('CO-14113', TW, 6), ('CO-14114', AU, 6)]
D19 = [('CO-14115', KR, 12)]
W = [12, 12, 16, 12, 12, 12, 12, 12, 12, 12, 16]


def search(units, pos, hold=None, released=()):
    """XD09 [Search] -> #TEMP_INSTRUCTION slices (line x PO x case). units oldest date first; pos [[po, open]] reduced in place."""
    hold = hold or {}
    rows = []
    for dt, lines in units:
        free, held = [], []
        for o, d, q in lines:
            h = min(hold.get(o, 0), q)
            if q - h:
                free.append((o, d, q - h))
            if h:
                held.append((o, d, h))
        free = [x for x in free if x[0] not in released] + [x for x in free if x[0] in released]
        pcs = []
        for o, d, q in free:
            for _ in range(q):
                p = next((x for x in pos if x[1] > 0), None)
                if p:
                    p[1] -= 1
                pcs.append((o, d, p[0] if p else None))
        cum, cases = {}, []
        for i, (o, d, po) in enumerate(pcs):
            case = i // PCS + 1
            cum[d] = cum.get(d, 0) + 1
            last_of_case = (i + 1) % PCS == 0 or i == len(pcs) - 1
            cut = last_of_case and all(v % PCS == 0 for v in cum.values())
            cases.append((case, o, d, po, cut and last_of_case))
        group, ready, gseq = {}, True, 1
        by_case = {}
        for case, o, d, po, cut in cases:
            by_case.setdefault(case, []).append((o, d, po, cut))
        case_group = {}
        for case in sorted(by_case):
            case_group[case] = gseq
            if any(x[3] for x in by_case[case]):
                gseq += 1
        gstatus = {}
        for g in sorted(set(case_group.values())):
            has = all(x[2] for c, gg in case_group.items() if gg == g for x in by_case[c])
            ready = ready and has
            gstatus[g] = '6' if ready else '7'
        seq = 0
        for case in sorted(by_case):
            sl = []
            for o, d, po, cut in by_case[case]:
                if sl and sl[-1][0] == o and sl[-1][2] == po:
                    sl[-1][3] += 1
                    sl[-1][4] = sl[-1][4] or cut
                else:
                    sl.append([o, d, po, 1, cut])
            for line_seq, (o, d, po, q, cut) in enumerate(sl, 1):
                seq += 1
                rows.append([dt, seq, o, f'{d} {NAME[d]}', q, po or 'NULL', case, line_seq, 'Y' if cut else 'N', case_group[case],
                             gstatus[case_group[case]]])
        for o, d, q in held:
            seq += 1
            rows.append([dt, seq, o, f'{d} {NAME[d]}', q, 'NULL', 'NULL', 'NULL', 'N', 'NULL', '8'])
    return rows


TEMP_HEAD = ['ORDER_DT', 'SORT_SEQ', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'ASSIGNED_QTY', 'PO_NO', 'CASE_SEQ', 'LINE_SEQ', 'CUT_FLAG', 'GROUP_SEQ',
             'CROSSDOCK_STATUS']


def temp_sheet(wb, title, heading, notes, units, pos, hold=None, released=(), outcome=()):
    ws, r = sheet(wb, title, heading, notes)
    rows = search(units, [list(p) for p in pos], hold, released)
    ws.cell(r - 1, 1, '#TEMP_INSTRUCTION (sesi [Search]: 1 baris per line x PO x case)').font = FB
    fills = {i: (HOLD if x[10] == '8' else OK if x[10] == '6' else BAD) for i, x in enumerate(rows, 1)}
    r = table(ws, r, TEMP_HEAD, rows, W, fills)
    if outcome:
        table(ws, r, ['Hasil'], [[x] for x in outcome], [12])
        for k in range(len(outcome) + 1):
            ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=11)
    return rows


def simple(wb, title, heading, notes, blocks, outcome=()):
    ws, r = sheet(wb, title, heading, notes)
    for name, head, rows, fill in blocks:
        ws.cell(r - 1, 1, name).font = FB
        r = table(ws, r, head, rows, W, {i: fill for i in range(1, len(rows) + 1)} if fill else None)
    if outcome:
        table(ws, r, ['Hasil'], [[x] for x in outcome], [12])
        for k in range(len(outcome) + 1):
            ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=11)


def h0253(lines, dt, mapped=(), hold_flag='N'):
    return [[CUST[d], o, dt, d, PART, q, '7', hold_flag, 'Y' if o in mapped else 'N', 'NULL'] for o, d, q in lines]


H0253_HEAD = ['CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD', 'SHIPPING_PART_NO', 'ORDER_STATUS_QTY', 'ORDER_STATUS', 'HOLD_FLAG',
              'PO_MAPPED_FLAG', 'UPD_STATUS']
HOLD_HEAD = ['PART_NO', 'ORDER_DT', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'HOLD_QTY', 'HOLD_FLAG']
INS_HEAD = ['INSTRUCTION_ID', 'CASE_SEQ', 'LINE_SEQ', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'QTY', 'PO_NO', 'ORDER_DT', 'ASN_NO', 'CASE_NO']


def main():
    wb = Workbook()
    wb.remove(wb.active)
    P18 = [('PO-0002', 6), ('PO-0003', 18)]

    ws, r = sheet(wb, '1. Penjelasan', 'Simulasi hold per case, konsep tabel lama: H0253 -> #TEMP_INSTRUCTION -> TB_R_INSTRUCTION', [
        'PART-X, supplier 5001-1, 6 pcs/case, data sama dengan prototype. Kuning = di-hold, merah = Not Ready, hijau = Ready.'])
    table(ws, r, ['Langkah', 'Tabel', 'Penjelasan'], [
        ['XD08 (27:30)', 'TB_R_H0253_ORDER_CONTROL_PRE', 'Replicate customer order H0253 (status 7) ke NSP, dengan HOLD_FLAG / PO_MAPPED_FLAG / UPD_STATUS.'],
        ['[Search] (XD09)', '#TEMP_INSTRUCTION', 'Tabel sementara per sesi. Pcs dituang PO, dipotong per case (CASE_SEQ = urutan 1, 2, 3...). Belum ada Case No asli.'],
        ['[Save] hold (XD10)', 'TB_R_CROSSDOCK_CASE_HOLD', 'Case yang dicentang disimpan sebagai order line + HOLD_QTY, bukan CASE_SEQ.'],
        ['[Search] berikutnya', '#TEMP_INSTRUCTION', 'Pcs yang di-hold tanpa PO dan tanpa CASE_SEQ (CROSSDOCK_STATUS 8); PO pindah ke line berikutnya.'],
        ['[Create ASN] (XD10)', 'TB_R_INSTRUCTION, TB_R_PRA_DAILY_ORDER_PART, H0253', 'Mapping nyata case yang dicentang; REMAIN_QTY PO turun; PO_MAPPED_FLAG Y untuk line yang sudah penuh. CASE_NO masih NULL.'],
        ['Submit ASN', 'TB_R_INSTRUCTION, TB_R_CASE_LABEL_LAST_SEQ', 'ASN_NO dan CASE_NO dibuat sekali, hanya untuk case yang dikirim.'],
    ], [22, 40, 90])

    simple(wb, '2. H0253 replicate', 'TB_R_H0253_ORDER_CONTROL_PRE setelah XD08 (order 17-Oct, 18-Oct, 19-Oct)', [
        'Order 17-Oct 30 pcs, 18-Oct 18 pcs, 19-Oct 12 pcs (CO-14115). Order tanggal D masuk NSP lewat XD08 di D+1, jadi baru muncul di [Search] D+1.'],
           [('TB_R_H0253_ORDER_CONTROL_PRE', H0253_HEAD, h0253(D17, '17-Oct') + h0253(D18, '18-Oct') + h0253(D19, '19-Oct'), None)])
    temp_sheet(wb, '3. Search 18-Oct', '[Search] 18-Oct: #TEMP_INSTRUCTION, belum ada hold', ['PO tersedia 18-Oct: PO-0002 sisa 6, PO-0003 18 (unit 18-Oct belum masuk: diambil H+1).'],
               [('17-Oct', D17)], P18, outcome=['Case 1-4 Ready (CROSSDOCK_STATUS 6), case 5 Australia tanpa PO (7).',
                                                'CASE_SEQ hanya urutan di sesi ini; Case No asli belum ada.'])
    simple(wb, '4. Hold case 4', 'D/S centang Hold di case 4 (CO-14109 Taiwan 6 pcs) lalu [Save]', ['Disimpan per order line, bukan CASE_SEQ.'],
           [('TB_R_CROSSDOCK_CASE_HOLD', HOLD_HEAD, [[PART, '17-Oct', SUP, PLANT, 'CO-14109', f'{TW} Taiwan', 6, 'Y']], HOLD)],
           ['Kunci lengkap H0253 (CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO) + HOLD_QTY 6.',
            '#TEMP_INSTRUCTION hilang setelah sesi selesai; hold tetap tersimpan di tabel ini.'])
    temp_sheet(wb, '5. Search stlh hold', '[Search] 18-Oct setelah hold', ['XD09 baca TB_R_CROSSDOCK_CASE_HOLD sebelum PO dituang.'],
               [('17-Oct', D17)], P18, hold={'CO-14109': 6},
               outcome=['Taiwan: PO NULL, CASE_SEQ NULL, CROSSDOCK_STATUS 8. Australia dapat PO-0003 dan jadi case 4.',
                        'Case 1-4 semua Ready.'])
    ins = [[1, 1, 1, 'CO-14105', KR, 6, 'PO-0002', '17-Oct', 'NULL', 'NULL'],
           [2, 2, 1, 'CO-14106', KR, 3, 'PO-0003', '17-Oct', 'NULL', 'NULL'],
           [3, 2, 2, 'CO-14107', KR, 3, 'PO-0003', '17-Oct', 'NULL', 'NULL'],
           [4, 3, 1, 'CO-14104', JP, 6, 'PO-0003', '17-Oct', 'NULL', 'NULL'],
           [5, 4, 1, 'CO-14110', AU, 6, 'PO-0003', '17-Oct', 'NULL', 'NULL']]
    simple(wb, '6. Create ASN', 'Supplier centang case 1-4, klik [Create ASN] (XD10)', ['Mapping nyata ditulis dari #TEMP_INSTRUCTION ke tabel tetap.'], [
        ('TB_R_INSTRUCTION (1 baris per case x line x PO)', INS_HEAD, ins, OK),
        ('TB_R_PRA_DAILY_ORDER_PART (update REMAIN_QTY)', ['PO_NO', 'MANIFEST_NO', 'ORDER_QTY', 'REMAIN_QTY sebelum', 'REMAIN_QTY sesudah'], [['PO-0002', 'MF-0002', 6, 6, 0], ['PO-0003', 'MF-0003', 18, 18, 0]], None),
        ('TB_R_H0253_ORDER_CONTROL_PRE (update)', H0253_HEAD, h0253(D17, '17-Oct', mapped=('CO-14105', 'CO-14106', 'CO-14107', 'CO-14104', 'CO-14110')), None),
    ], ['CASE_NO dan ASN_NO masih NULL. PO_MAPPED_FLAG Y untuk 5 line; CO-14109 Taiwan tetap N (di-hold, belum dikirim).'])
    simple(wb, '7. Submit ASN', 'Submit ASN: ASN_NO dan CASE_NO dibuat (format dummy)', ['Nomor case label dipakai sekali, hanya untuk 4 case yang dikirim.'], [
        ('TB_R_INSTRUCTION (update)', INS_HEAD, [x[:8] + ['ASN0003', f'50011A0{x[1]}'] for x in ins], OK),
        ('TB_R_CASE_LABEL_LAST_SEQ', ['SUPPLIER_CD', 'SUPPLIER_PLANT_CD', 'CASE_LABEL_LAST_SEQ', 'ASN_LAST_SEQ'], [[SUP, PLANT, '04', '0003']], None),
    ], ['Case 1-4 = 50011A01-04. Tidak ada nomor yang terbuang walaupun [Search] dijalankan berkali-kali.'])
    simple(wb, '8a. Release Taiwan', 'D/S untick Taiwan lalu [Save] (19-Oct)', ['HOLD_FLAG jadi N (FB-183).'],
           [('TB_R_CROSSDOCK_CASE_HOLD', HOLD_HEAD, [[PART, '17-Oct', SUP, PLANT, 'CO-14109', f'{TW} Taiwan', 6, 'N']], HOLD)],
           ['CO-14109 masuk urutan terakhir 17-Oct, tetap lebih dulu dari order 18-Oct.'])
    temp_sheet(wb, '8b. Search 19-Oct', '[Search] 19-Oct: PO-0004 (12) dan PO-0005 (18) rilis', [
        'H0253 yang masih open: CO-14109 (17-Oct, PO_MAPPED_FLAG N) dan order 18-Oct. PO-0002 / PO-0003 REMAIN_QTY 0.'],
        [('17-Oct', [('CO-14109', TW, 6)]), ('18-Oct', D18)], [('PO-0004', 12), ('PO-0005', 18)], released=('CO-14109',),
        outcome=['Taiwan dapat PO-0004 6 lebih dulu dari order 18-Oct. Setelah Taiwan masuk ASN, baris di TB_R_CROSSDOCK_CASE_HOLD dihapus.'])
    temp_sheet(wb, '9a. Search 20-Oct', '[Search] 20-Oct: order 19-Oct CO-14115 Korea 12 pcs muncul pertama kali', [
        'Order 17-Oct dan 18-Oct sudah dikirim (ASN 19-Oct). PO tersedia: PO-0005 sisa 6, PO-0006 12 (PO order date 19-Oct, rilis 20-Oct).',
        'CO-14115 12 pcs dipotong jadi 2 case: case 1 dibayar PO-0005 6, case 2 dibayar PO-0006 6.'],
        [('19-Oct', D19)], [('PO-0005', 6), ('PO-0006', 12)],
        outcome=['CO-14115 ada di case 1 dan case 2 (1 line terpecah ke 2 case). Keduanya Ready.'])
    simple(wb, '9b. Hold case 2', 'D/S centang Hold di case 2 saja (isi: CO-14115 6 pcs) lalu [Save]', ['Yang disimpan: line CO-14115 dengan HOLD_QTY 6 (bukan seluruh line).'],
           [('TB_R_CROSSDOCK_CASE_HOLD', HOLD_HEAD, [[PART, '19-Oct', SUP, PLANT, 'CO-14115', f'{KR} Korea', 6, 'Y']], HOLD)],
           ['HOLD_QTY = pcs CO-14115 di case 2 = 6. Kalau D/S hold case 1 juga, HOLD_QTY jadi 12 (seluruh line).'])
    temp_sheet(wb, '9c. Search stlh hold', '[Search] 20-Oct setelah hold case 2', ['6 pcs terakhir CO-14115 di-hold, 6 pcs pertama tetap jalan.'],
        [('19-Oct', D19)], [('PO-0005', 6), ('PO-0006', 12)], hold={'CO-14115': 6},
        outcome=['Case 1: CO-14115 6 pcs PO-0005, Ready. 6 pcs On hold (CROSSDOCK_STATUS 8), tanpa PO.',
                 'PO-0006 12 tidak terpakai: sisa untuk order berikutnya (REMAIN_QTY tetap 12).'])
    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
