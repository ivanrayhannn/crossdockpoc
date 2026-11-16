"""Simulation: hold per case with TB_R_CROSSDOCK_CASE_HOLD and the draft tables TB_T_INSTRUCTION_H / D (16-Nov).
PART-X, supplier 5001-1, 6 pcs/case, same data as the prototype. Shows that the hold needs no Case No: it is kept per customer order
line + HOLD_QTY, and the real Case No is made at Submit (proposal; the DR makes it at every Search).
Run: python3 build_sim_case_hold_table.py"""
import os
from openpyxl import Workbook
from build_sim_fb182 import BAD, FB, HOLD, OK, sheet, table

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD09_XD10_Simulation_Case_Hold_Table.xlsx')
PCS = 6
SUP, PLANT, PART = '5001', '1', 'PART-X'
KR, JP, TW, AU = '9715310 Korea', '9722D10 Japan', '9811110 Taiwan', '982220 Australia'
D17 = [('CO-14105', KR, 6), ('CO-14106', KR, 3), ('CO-14107', KR, 3), ('CO-14104', JP, 6), ('CO-14109', TW, 6), ('CO-14110', AU, 6)]
D18 = [('CO-14112', KR, 6), ('CO-14113', TW, 6), ('CO-14114', AU, 6)]
BLUE = HOLD.__class__('solid', fgColor='DDEBF7')


def draft(units, pos, hold=None, released=()):
    """units: [(order date, [(order, dest, open qty)])] oldest date first; pos: [[po, open qty]] oldest first (reduced in place).
    hold: {order: held qty}; released: orders put at the end of their date (FB-183).
    Returns (H rows, D rows); a D row = [date, seq, order, dest, qty 1, PO, case, hold_sts]."""
    hold = hold or {}
    H, D = [], []
    for dt, lines in units:
        free, held = [], []
        for o, d, q in lines:
            h = min(hold.get(o, 0), q)
            if q - h:
                free.append((o, d, q - h))
            if h:
                held.append((o, d, h))
        free = [x for x in free if x[0] not in released] + [x for x in free if x[0] in released]
        seq = 0
        for o, d, q in free:
            for _ in range(q):
                p = next((x for x in pos if x[1] > 0), None)
                if p:
                    p[1] -= 1
                seq += 1
                D.append([dt, seq, o, d, 1, p[0] if p else '-', (seq - 1) // PCS + 1, 'NULL'])
        for o, d, q in held:
            for _ in range(q):
                seq += 1
                D.append([dt, seq, o, d, 1, '-', '-', 'Y'])
        open_qty = sum(q for _, _, q in free)
        cases = -(-open_qty // PCS)
        rows = [r for r in D if r[0] == dt and r[7] != 'Y']
        ready = [c for c in range(1, cases + 1) if all(r[5] != '-' for r in rows if r[6] <= c)]
        H.append([dt, PART, SUP, PLANT, open_qty, cases, 'Y' if ready else 'N', f'{len(ready)} of {cases}'])
    return H, D


def case_view(D):
    """Per case: date, case, orders, dest, qty, PO, status (Ready when the case and the earlier cases of the date have a PO)."""
    out, fills, ok = [], {}, {}
    keys = []
    for r in D:
        k = (r[0], r[6])
        if k not in keys:
            keys.append(k)
    for dt, c in keys:
        rs = [r for r in D if r[0] == dt and r[6] == c]
        held = rs[0][7] == 'Y'
        orders = []
        for r in rs:
            if r[2] not in orders:
                orders.append(r[2])
        pos = []
        for r in rs:
            if r[5] not in pos:
                pos.append(r[5])
        if held:
            status = 'On Hold (D/S)'
        else:
            ok[dt] = ok.get(dt, True) and all(r[5] != '-' for r in rs)
            status = 'Ready' if ok[dt] else 'Not Ready'
        out.append([dt, 'On hold' if held else f'Case {c}', ', '.join(orders), rs[0][3], len(rs),
                    ', '.join(f'{p} {sum(1 for r in rs if r[5] == p)}' if p != '-' else '-' for p in pos), status])
        fills[len(out)] = HOLD if held else (OK if status == 'Ready' else BAD)
    return out, fills


def search_sheet(wb, title, heading, notes, units, pos, hold=None, released=(), outcome=()):
    ws, r = sheet(wb, title, heading, notes)
    H, D = draft(units, [list(p) for p in pos], hold, released)
    ws.cell(r - 1, 1, 'TB_T_INSTRUCTION_H (1 baris per unit)').font = FB
    r = table(ws, r, ['ORDER_DT', 'SHIPPING_PART_NO', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'ORDER_STATUS_QTY (open)', 'CASE', 'SUBMIT_ASN_STS', 'Ready case'],
              H, [14, 16, 12, 14, 20, 8, 15, 12])
    ws.cell(r - 1, 1, 'Tampilan layar XD10 (D digabung per case)').font = FB
    cv, fills = case_view(D)
    r = table(ws, r, ['Customer Order Date', 'Case', 'Customer Order No', 'Destination', 'Qty', 'PO', 'PO Status'], cv, [14, 16, 20, 18, 20, 18, 15], fills)
    if outcome:
        r = table(ws, r, ['Hasil'], [[x] for x in outcome], [14])
        for k in range(len(outcome) + 1):
            ws.merge_cells(start_row=r - len(outcome) - 2 + k, start_column=1, end_row=r - len(outcome) - 2 + k, end_column=7)
    ws.cell(r - 1, 1, 'TB_T_INSTRUCTION_D (1 baris per pc, ORDER_STATUS_QTY 1, PO_QTY 1 kalau ada PO)').font = FB
    dfill = {i: (HOLD if row[7] == 'Y' else (BAD if row[5] == '-' else None)) for i, row in enumerate(D, 1)}
    table(ws, r, ['ORDER_DT', 'SEQ_NO', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'ORDER_STATUS_QTY', 'PO_NO', 'Case (urutan)', 'HOLD_STS'],
          [x[:5] + [x[5], x[6], x[7]] for x in D], [14, 16, 20, 18, 20, 18, 15, 12], {k: v for k, v in dfill.items() if v})
    return H, D


def hold_sheet(wb, title, heading, notes, rows, outcome):
    ws, r = sheet(wb, title, heading, notes)
    ws.cell(r - 1, 1, 'TB_R_CROSSDOCK_CASE_HOLD').font = FB
    r = table(ws, r, ['PART_NO', 'ORDER_DT', 'SUPPLIER_CD', 'SUPPLIER_PLANT', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'HOLD_QTY', 'HOLD_FLAG'],
              rows, [14, 16, 12, 14, 20, 18, 20, 12], {i: HOLD for i in range(1, len(rows) + 1)})
    table(ws, r, ['Hasil'], [[x] for x in outcome], [14])
    for k in range(len(outcome) + 1):
        ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=8)


def main():
    wb = Workbook()
    wb.remove(wb.active)
    P18 = [('PO-0002', 6), ('PO-0003', 18)]

    ws, r = sheet(wb, '1. Penjelasan', 'Simulasi hold per case: TB_R_CROSSDOCK_CASE_HOLD + TB_T_INSTRUCTION_H / D', [
        'PART-X, supplier 5001-1, 6 pcs/case, data sama dengan prototype. Kuning = di-hold, merah = belum dapat PO, hijau = Ready.'])
    table(ws, r, ['Poin', 'Penjelasan'], [
        ['Masalah', 'Saat [Search], Case No asli belum ada (konsep lama) atau berubah setiap Search (konsep DR). Jadi hold tidak bisa disimpan per Case No.'],
        ['Jawaban', 'Hold disimpan per customer order line + HOLD_QTY di TB_R_CROSSDOCK_CASE_HOLD. Case di layar hanya urutan (1, 2, 3, ...) untuk memilih.'],
        ['[Save] hold', 'Case yang dicentang dipecah per order line: 1 baris per line dengan HOLD_QTY = pcs line itu di case tersebut, HOLD_FLAG Y.'],
        ['[Search]', 'XD09 baca TB_R_CROSSDOCK_CASE_HOLD: pcs HOLD_FLAG Y ditulis di TB_T_INSTRUCTION_D dengan HOLD_STS Y, tanpa PO dan tanpa case; '
                     'PO dituang ke pcs lain. HOLD_STS hanya hasil per run (tabel D dihapus dan diisi ulang setiap Search).'],
        ['Release', 'HOLD_FLAG N: line masuk urutan terakhir tanggal order-nya (FB-183). Baris hold dihapus setelah line masuk ASN atau di-cancel.'],
        ['Case No asli', 'Usulan: dibuat saat Create ASN / Submit dari TB_R_CASE_LABEL_LAST_SEQ, hanya untuk case yang dikirim (sheet 7).'],
        ['Sheet', '2. Search 18-Oct; 3. Hold case 4; 4. Search setelah hold; 5. Submit ASN case 1-4; 6. Release + Search 19-Oct; 7. Case No DR vs usulan; 8. Line terpecah 2 case.'],
    ], [18, 120])

    search_sheet(wb, '2. Search 18-Oct', 'Search 18-Oct, belum ada hold', ['PO: PO-0002 sisa 6 + PO-0003 18 = 24 pcs; order 17-Oct 30 pcs.'],
                 [('17-Oct', D17)], P18, outcome=['Case 1-4 Ready, case 5 (Australia) belum dapat PO.'])
    hold_sheet(wb, '3. Hold case 4', 'D/S centang Hold di case 4 (isi: CO-14109 Taiwan 6 pcs) lalu [Save]', [
        'Yang disimpan bukan "case 4", tapi order line di dalamnya.'],
        [[PART, '17-Oct', SUP, PLANT, 'CO-14109', TW, 6, 'Y']],
        ['1 baris: CO-14109 (kunci H0253 lengkap: CUSTOMER_CD, CUSTOMER_ORDER_NO, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO), HOLD_QTY 6, HOLD_FLAG Y.',
         'Tidak butuh Case No. Kalau nomor case bergeser di Search berikutnya, hold tetap di CO-14109.'])
    search_sheet(wb, '4. Search stlh hold', 'Search 18-Oct setelah hold', [
        'XD09 baca TB_R_CROSSDOCK_CASE_HOLD: 6 pcs CO-14109 HOLD_STS Y, tanpa PO. PO-0003 6 pcs pindah ke CO-14110 Australia.'],
        [('17-Oct', D17)], P18, hold={'CO-14109': 6},
        outcome=['Case 1-4 (Korea, Korea, Japan, Australia) semua Ready. Taiwan tampil di bawah sebagai On hold.',
                 'Di TB_T_INSTRUCTION_D: 24 pcs dengan PO dan urutan case 1-4, 6 pcs Taiwan HOLD_STS Y.'])

    ws, r = sheet(wb, '5. Submit ASN', 'Supplier centang case 1-4, Create ASN, Submit (usulan: Case No dibuat di sini)', [
        'Case No asli dibuat sekali, hanya untuk case yang dikirim. Format contoh (dummy): supplier + plant + palletize + seq.'])
    r = table(ws, r, ['Case (urutan)', 'Customer Order No', 'Destination', 'Qty', 'PO', 'CASE_NO (Submit)', 'CASE_LABEL_LAST_SEQ'], [
        ['Case 1', 'CO-14105', KR, 6, 'PO-0002 6', '50011A01', '01'],
        ['Case 2', 'CO-14106, CO-14107', KR, 6, 'PO-0003 6', '50011A02', '02'],
        ['Case 3', 'CO-14104', JP, 6, 'PO-0003 6', '50011A03', '03'],
        ['Case 4', 'CO-14110', AU, 6, 'PO-0003 6', '50011A04', '04'],
    ], [14, 20, 18, 8, 14, 18, 20], {i: OK for i in range(1, 5)})
    table(ws, r, ['Hasil'], [['TB_R_INSTRUCTION + ASN: 4 case, Case No 50011A01-04; last seq = 04. Taiwan tetap di TB_R_CROSSDOCK_CASE_HOLD (belum dikirim).']], [14])
    ws.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=7)

    hold_sheet(wb, '6a. Release Taiwan', 'D/S untick Taiwan lalu [Save] (19-Oct)', ['HOLD_FLAG jadi N (FB-183).'],
               [[PART, '17-Oct', SUP, PLANT, 'CO-14109', TW, 6, 'N']],
               ['CO-14109 masuk urutan terakhir 17-Oct; tetap lebih dulu dari order 18-Oct.', 'Baris ini dihapus setelah CO-14109 masuk ASN.'])
    search_sheet(wb, '6b. Search 19-Oct', 'Search 19-Oct: PO-0004 (12) dan PO-0005 (18) rilis; case 1-4 17-Oct sudah ASN', [
        'Yang tersisa dari 17-Oct hanya CO-14109 Taiwan (released). Order 18-Oct ikut.'],
        [('17-Oct', [('CO-14109', TW, 6)]), ('18-Oct', D18)], [('PO-0004', 12), ('PO-0005', 18)], released=('CO-14109',),
        outcome=['17-Oct: Taiwan dapat PO-0004 6 lebih dulu dari order 18-Oct (tanggal lama didahulukan).',
                 '18-Oct: CO-14112 PO-0004 6, CO-14113 dan CO-14114 PO-0005.'])

    ws, r = sheet(wb, '7. Case No DR vs usulan', 'Pemakaian nomor case label: DR (dibuat setiap Search) vs usulan (dibuat saat Submit)', [
        'Contoh 18-Oct: supplier klik [Search] 3 kali (refresh, hold, cek lagi) lalu Submit 4 case.'])
    r = table(ws, r, ['Kejadian', 'DR: CASE_NO dibuat XD09 setiap Search', 'Usulan: Case No dibuat saat Submit'], [
        ['Search ke-1 (5 case)', '50011A01-05 terpakai, last seq 05', 'Case 1-5 (urutan saja), last seq tetap 00'],
        ['Search ke-2 (hold, 4 case)', 'D dihapus, 50011A06-09 terpakai, last seq 09', 'Case 1-4 (urutan), last seq 00'],
        ['Search ke-3 (4 case)', '50011A10-13 terpakai, last seq 13', 'Case 1-4 (urutan), last seq 00'],
        ['Submit 4 case', 'ASN pakai 50011A10-13; 01-09 terbuang', 'ASN pakai 50011A01-04, last seq 04'],
        ['Hold per case', 'Tidak bisa per CASE_NO (berubah setiap Search); tetap perlu TB_R_CROSSDOCK_CASE_HOLD', 'TB_R_CROSSDOCK_CASE_HOLD (line + HOLD_QTY)'],
    ], [26, 50, 50])
    table(ws, r, ['FB', 'Status', 'Isi'], [
        ['FB-194', 'Perlu keputusan', 'Usulan: CASE_NO di TB_T_INSTRUCTION_D cukup urutan case per unit; Case No asli dibuat saat Create ASN / Submit.'],
    ], [9, 15, 110])

    ws, r = sheet(wb, '8. Line terpecah 2 case', 'Contoh line terpecah: CO-14115 Korea 12 pcs (19-Oct) = case 1 dan case 2', [
        'D/S hold case 2 saja: yang disimpan CO-14115 HOLD_QTY 6.'])
    r = table(ws, r, ['PART_NO', 'ORDER_DT', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'HOLD_QTY', 'HOLD_FLAG'],
              [[PART, '19-Oct', 'CO-14115', KR, 6, 'Y']], [14, 16, 20, 18, 12, 12], {1: HOLD})
    table(ws, r, ['Hasil Search berikutnya'], [
        ['6 pcs CO-14115 tetap di unit (case 1, dapat PO); 6 pcs terakhir di TB_T_INSTRUCTION_D dengan HOLD_STS Y (On hold).'],
        ['Kalau D/S hold case 1 juga: HOLD_QTY jadi 12 (ditambah), seluruh line di-hold.']], [14])

    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
