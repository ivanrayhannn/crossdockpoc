"""FB-182 simulation: hold per case stored by CASE_SEQ (current) vs by customer order line, data of PART-X 17-Oct (6 pcs/case).
Run: python3 build_sim_fb182.py"""
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD10_Simulation_FB182_Case_Hold.xlsx')
HDR = PatternFill('solid', fgColor='DDEBF7')
HOLD = PatternFill('solid', fgColor='FFF2CC')
BAD = PatternFill('solid', fgColor='FCE4D6')
OK = PatternFill('solid', fgColor='E2EFDA')
thin = Side(style='thin', color='999999')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F = Font(name='Arial', size=9)
FB = Font(name='Arial', size=9, bold=True)
WRAP = Alignment(wrap_text=True, vertical='top')
PCS = 6


def sheet(wb, title, heading, notes):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws['A1'] = heading
    ws['A1'].font = Font(name='Arial', size=12, bold=True)
    r = 2
    for n in notes:
        ws.cell(r, 1, n).font = Font(name='Arial', size=9, italic=True)
        r += 1
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    return ws, r + 1


def table(ws, r0, cols, rows, widths, fills=None):
    for c, h in enumerate(cols, 1):
        x = ws.cell(r0, c, h)
        x.font, x.fill, x.border = FB, HDR, BOX
        x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    for i, row in enumerate(rows, 1):
        for c, v in enumerate(row, 1):
            x = ws.cell(r0 + i, c, v)
            x.font, x.border, x.alignment = F, BOX, WRAP
            if fills and fills.get(i):
                x.fill = fills[i]
    for c, w in enumerate(widths, 1):
        L = get_column_letter(c)
        ws.column_dimensions[L].width = max(ws.column_dimensions[L].width or 0, w)
    return r0 + len(rows) + 2


def cut(lines, pos):
    """lines: (order, dest, qty) in H0253 order; pos: [(po, open)] -> cases [{seq, lines:[(order, dest, qty, po)]}]."""
    pos = [list(p) for p in pos]
    cases, cur, room = [], [], PCS
    for order, dest, qty in lines:
        left = qty
        while left:
            p = next((x for x in pos if x[1] > 0), None)
            q = min(left, room, p[1] if p else left)
            if p:
                p[1] -= q
            cur.append((order, dest, q, p[0] if p else '-'))
            left -= q
            room -= q
            if room == 0:
                cases.append(cur)
                cur, room = [], PCS
    if cur:
        cases.append(cur)
    return [{'seq': i + 1, 'lines': c} for i, c in enumerate(cases)]


def result(ws, r0, rows, fills):
    """Opsi | Hasil (merged B:D) | Benar? in the 5 columns of the case table."""
    for c, h in ((1, 'Opsi'), (2, 'Hasil'), (5, 'Benar?')):
        x = ws.cell(r0, c, h)
        x.font, x.fill = FB, HDR
        x.alignment = Alignment(horizontal='center', vertical='center')
    ws.merge_cells(start_row=r0, start_column=2, end_row=r0, end_column=4)
    for i, (o, h, b) in enumerate(rows, 1):
        rr = r0 + i
        for c, v in ((1, o), (2, h), (5, b)):
            x = ws.cell(rr, c, v)
            x.font, x.alignment, x.fill = F, WRAP, fills[i]
        ws.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
        ws.row_dimensions[rr].height = 30
    for rr in range(r0, r0 + len(rows) + 1):
        for c in range(1, 6):
            ws.cell(rr, c).border = BOX
    return r0 + len(rows) + 2


def case_rows(cases, held_seq=None, held_orders=()):
    rows, fills = [], {}
    for c in cases:
        by_seq = held_seq is not None and c['seq'] == held_seq
        by_line = any(l[0] in held_orders for l in c['lines'])
        for j, (o, d, q, po) in enumerate(c['lines']):
            rows.append([f'Case {c["seq"]}' if j == 0 else '', o, d, q, po])
            if by_seq or by_line:
                fills[len(rows)] = HOLD
    return rows, fills


def main():
    wb = Workbook()
    wb.remove(wb.active)
    KR, JP, TW, AU = '9715310 Korea', '9722D10 Japan', '9811110 Taiwan', '982220 Australia'
    L17 = [('CO-14105', KR, 6), ('CO-14106', KR, 3), ('CO-14107', KR, 3), ('CO-14104', JP, 6), ('CO-14109', TW, 6), ('CO-14110', AU, 6)]
    cols = ['Case', 'Customer Order No', 'Destination', 'Qty', 'PO']
    W = [22, 18, 20, 8, 30]

    # ---------- Penjelasan ----------
    ws, r = sheet(wb, '1. Penjelasan', 'FB-182: hold per case disimpan per nomor case (CASE_SEQ), apakah bisa bergeser?', [
        'Data PART-X, Customer Order Date 17-Oct, 6 pcs/case (sama dengan simulasi ASN). Kuning = case yang di-hold.'])
    table(ws, r, ['Poin', 'Penjelasan'], [
        ['Masalah', 'Nomor case dihitung ulang setiap Search dari open qty dalam urutan H0253. Kalau ada line yang hilang dari unit (cancel, sudah masuk ASN, hold destinasi), '
                    'case di bawahnya naik nomor. Hold yang disimpan sebagai "case 4" lalu menunjuk ke isi yang lain.'],
        ['Niat D/S', 'Di Search 18-Oct D/S hold case 4 = CO-14109 Taiwan (barang Taiwan belum boleh dikirim).'],
        ['Kejadian A (sheet 3)', '19-Oct: CO-14104 Japan di-cancel GTOPAS (UPD_STATUS 2). Unit dipotong ulang: Taiwan jadi case 3, Australia jadi case 4.'],
        ['Kejadian B (sheet 4)', 'Supplier sudah buat ASN case 1-2 (Korea). Search berikutnya case dihitung lagi dari 1: Taiwan jadi case 2.'],
        ['Opsi A (sekarang)', 'TB_R_CROSSDOCK_CASE_HOLD menyimpan CASE_SEQ. Hold ikut nomor, bukan isi.'],
        ['Opsi B (usulan)', 'Simpan customer order line yang ada di case saat di-hold (CUSTOMER_CD, CUSTOMER_ORDER_NO, ORDER_DT, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO). '
                            'Setiap Search, case yang berisi line itu = On Hold (beserta case sesudahnya, aturan Ready tetap sama).'],
    ], [22, 120])

    # ---------- Search 18-Oct ----------
    ws, r = sheet(wb, '2. Search 18-Oct', 'Search 18-Oct: D/S hold case 4 (CO-14109 Taiwan)', [
        'PO tersedia: PO-0002 sisa 6 + PO-0003 18 = 24 pcs. Case 5 belum dapat PO.'])
    c18 = cut(L17, [('PO-0002', 6), ('PO-0003', 18)])
    rows, fills = case_rows(c18, held_seq=4)
    r = table(ws, r, cols, rows, W, fills)
    ws, r = sheet(wb, '2b. Isi tabel hold', 'Yang disimpan saat [Save] di Search 18-Oct', [])
    table(ws, r, ['Disimpan', 'Opsi A (CASE_SEQ)', 'Opsi B (customer order line)'], [
        ['Isi tabel hold', 'PART-X / 17-Oct / 5001-1 / CASE_SEQ 4', 'PART-X / 17-Oct / 5001-1 / CO-14109 (9811110, item 001, serial 0000001)'],
        ['Hasil', 'Case 1-3 Ready, case 4 On Hold, case 5 Not Ready', 'Sama: case 1-3 Ready, case 4 On Hold, case 5 Not Ready'],
    ], [18, 40, 60])

    # ---------- Kejadian A ----------
    ws, r = sheet(wb, '3. Kejadian A - cancel', 'Kejadian A: 19-Oct CO-14104 Japan di-cancel (UPD_STATUS 2), hold belum diubah', [
        'Line yang di-cancel tidak diambil Search. PO tersedia 19-Oct: PO-0002 6 + PO-0003 18 + split PO PO-0004 12.'])
    LA = [l for l in L17 if l[0] != 'CO-14104']
    cA = cut(LA, [('PO-0002', 6), ('PO-0003', 18), ('PO-0004', 12)])
    ws.cell(r - 1, 1, 'Opsi A: hold tetap CASE_SEQ 4').font = FB
    rows, fills = case_rows(cA, held_seq=4)
    r = table(ws, r, cols, rows, W, fills)
    ws.cell(r - 1, 1, 'Opsi B: hold tetap CO-14109').font = FB
    rows, fills = case_rows(cA, held_orders=('CO-14109',))
    r = table(ws, r, cols, rows, W, fills)
    result(ws, r, [
        ['A (CASE_SEQ)', 'Case 4 sekarang CO-14110 Australia yang di-hold. Taiwan (case 3) jadi Ready dan bisa dikirim.', 'SALAH: hold pindah ke Australia'],
        ['B (customer order line)', 'Case 3 (CO-14109 Taiwan) yang di-hold, case 4 Australia ikut tidak Ready (aturan: case sesudah hold).', 'BENAR: tetap Taiwan'],
    ], {1: BAD, 2: OK})

    # ---------- Kejadian B ----------
    ws, r = sheet(wb, '4. Kejadian B - ASN', 'Kejadian B: supplier buat ASN case 1-2 (Korea 12 pcs), lalu Search lagi', [
        'Case yang sudah masuk ASN tidak muncul lagi; sisa unit dipotong ulang mulai case 1.'])
    LB = [l for l in L17 if l[0] not in ('CO-14105', 'CO-14106', 'CO-14107')]
    cB = cut(LB, [('PO-0003', 12)])
    ws.cell(r - 1, 1, 'Opsi A: hold tetap CASE_SEQ 4').font = FB
    rows, fills = case_rows(cB, held_seq=4)
    r = table(ws, r, cols, rows, W, fills)
    ws.cell(r - 1, 1, 'Opsi B: hold tetap CO-14109').font = FB
    rows, fills = case_rows(cB, held_orders=('CO-14109',))
    r = table(ws, r, cols, rows, W, fills)
    result(ws, r, [
        ['A (CASE_SEQ)', 'Sisa unit cuma 3 case, case 4 tidak ada: hold hilang, Taiwan (case 2) Ready dan bisa dikirim.', 'SALAH: hold hilang'],
        ['B (customer order line)', 'Case 2 (CO-14109 Taiwan) di-hold, case 3 Australia ikut tidak Ready.', 'BENAR: tetap Taiwan'],
    ], {1: BAD, 2: OK})

    # ---------- Usulan ----------
    ws, r = sheet(wb, '5. Usulan', 'Usulan perubahan TB_R_CROSSDOCK_CASE_HOLD', [])
    r = table(ws, r, ['Kolom', 'Opsi A (sekarang)', 'Opsi B (usulan)'], [
        ['Key unit', 'PART_NO, ORDER_DT, SUPPLIER_CD, SUPPLIER_PLANT', 'Sama'],
        ['Key hold', 'CASE_SEQ', 'CUSTOMER_CD, CUSTOMER_ORDER_NO, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO (line H0253 di case saat [Save])'],
        ['Satu case berisi 2 line (case 2 = CO-14106 + CO-14107)', '1 baris (CASE_SEQ 2)', '2 baris (CO-14106 dan CO-14107)'],
        ['Line terpecah ke 2 case (CO-14115 12 pcs)', 'Hanya case yang dicentang', 'Kedua case yang berisi line itu On Hold'],
        ['Tampilan check box', 'Dicentang kalau CASE_SEQ ada', 'Dicentang kalau case berisi line yang di-hold'],
        ['Line di-cancel / sudah ASN', 'Hold bisa pindah atau hilang (sheet 3, 4)', 'Hold ikut line; line yang hilang dari unit tidak berpengaruh'],
    ], [34, 50, 80])
    table(ws, r, ['FB', 'Status', 'Pertanyaan'], [
        ['FB-182', 'Perlu keputusan', 'Ganti penyimpanan hold per case ke Opsi B (per customer order line), supaya hold tetap menempel di order yang sama walaupun nomor case berubah?'],
    ], [9, 15, 120])

    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
