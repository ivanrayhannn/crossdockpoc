"""Simulation of ASSIGNED_QTY in #TEMP_INSTRUCTION (XD09 -> XD10), data of simulasi_asn_rev.xlsx (PART-X, 6 pcs/case).
Formulas show where ASSIGNED_QTY is used; the workbook is recalculated by LibreOffice so the values are cached.
Run: python3 build_sim_assigned_qty.py"""
import os, shutil, subprocess, tempfile
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'XD09_Simulation_ASSIGNED_QTY.xlsx')

HDR = PatternFill('solid', fgColor='DDEBF7')
KEY = PatternFill('solid', fgColor='FFF2CC')
OK = PatternFill('solid', fgColor='E2EFDA')
BAD = PatternFill('solid', fgColor='FCE4D6')
GREY = PatternFill('solid', fgColor='F2F2F2')
thin = Side(style='thin', color='999999')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F = Font(name='Arial', size=9)
FB = Font(name='Arial', size=9, bold=True)
WRAP = Alignment(wrap_text=True, vertical='top')


def new_sheet(wb, title, heading, notes):
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


def put(ws, r0, cols, rows, widths, fills=None, key_cols=()):
    for c, h in enumerate(cols, 1):
        x = ws.cell(r0, c, h)
        x.font, x.fill, x.border = FB, (KEY if h in key_cols else HDR), BOX
        x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    for i, row in enumerate(rows, 1):
        for c, v in enumerate(row, 1):
            x = ws.cell(r0 + i, c, v)
            x.font, x.border, x.alignment = F, BOX, WRAP
            if cols[c - 1] in key_cols:
                x.fill = KEY
            elif fills and fills.get(i):
                x.fill = fills[i]
    for c, w in enumerate(widths, 1):
        L = get_column_letter(c)
        ws.column_dimensions[L].width = max(ws.column_dimensions[L].width or 0, w)
    return r0 + len(rows) + 2


def main():
    wb = Workbook()
    wb.remove(wb.active)

    # ---------- 1. Penjelasan ----------
    ws, r = new_sheet(wb, '1. Penjelasan', 'Kenapa ada kolom ASSIGNED_QTY di #TEMP_INSTRUCTION', [
        'Data sama dengan simulasi_asn_rev.xlsx (PART-X, 6 pcs/case). Kolom kuning = ASSIGNED_QTY.'])
    put(ws, r, ['Poin', 'Penjelasan'], [
        ['1 baris = ?', '1 baris #TEMP_INSTRUCTION = 1 potongan: line customer order x PO x case supplier. Bukan 1 line customer order.'],
        ['OPEN_ORDER_QTY', 'Sisa qty SELURUH line customer order (H0253 ORDER_STATUS_QTY - qty line yang sudah di TB_R_INSTRUCTION). Sama di setiap potongan line itu.'],
        ['ASSIGNED_QTY', 'Qty POTONGAN INI saja: berapa pcs dari line itu yang masuk ke PO dan case di baris ini.'],
        ['Kenapa perlu', '1 case bisa berisi beberapa line (case 2 tgl 17-Oct = CO-14106 3 + CO-14107 3); 1 line bisa di beberapa case / PO (CO-14115 12 = case 1 PO-0005 6 + case 2 PO-0006 6); '
                         'qty tanpa PO tetap jadi baris dengan PO_NO kosong (CO-14110 6). OPEN_ORDER_QTY saja tidak bisa menunjukkan pembagian ini.'],
        ['Aturan cek', 'Jumlah ASSIGNED_QTY per line = OPEN_ORDER_QTY line itu; jumlah ASSIGNED_QTY per case = PCS_CASE (case penuh).'],
        ['Dipakai di', 'XD10: Qty per case, Remaining Qty (not assigned), kolom PO dan Content, status Ready / Not Ready. Create ASN: MAPPED_QTY per PO, QTY di TB_R_INSTRUCTION.'],
    ], [18, 140])

    # ---------- 2. Input ----------
    ws, r = new_sheet(wb, '2. Input', 'Input [Search] 18-Oct (order date 17-Oct) dan 20-Oct (order date 19-Oct)', [
        'Line H0253 yang diambil (ORDER_STATUS 7, UPD_STATUS NULL, HOLD N, PO_MAPPED N) dan PO crossdock yang masih ada sisa (urut PO date).'])
    ws.cell(r - 1, 1, 'A. Line customer order (urutan H0253)').font = FB
    r = put(ws, r, ['Search', 'SORT_SEQ', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'OPEN_ORDER_QTY'], [
        ['18-Oct', 1, 'CO-14105', '9715310', 6], ['18-Oct', 2, 'CO-14106', '9715310', 3], ['18-Oct', 3, 'CO-14107', '9715310', 3],
        ['18-Oct', 4, 'CO-14104', '9722D10', 6], ['18-Oct', 5, 'CO-14109', '9811110', 6], ['18-Oct', 6, 'CO-14110', '982220', 6],
        ['20-Oct', 1, 'CO-14115', '9715310', 12], ['20-Oct', 2, 'CO-14111', '9722D10', 6]], [10, 10, 18, 15, 16])
    ws.cell(r - 1, 1, 'B. PO crossdock yang masih ada sisa (open PO qty = ORDER_QTY - MAPPED_QTY)').font = FB
    put(ws, r, ['Search', 'PO_NO', 'PO_DT', 'ORDER_QTY', 'MAPPED_QTY', 'Open PO qty', 'Catatan'], [
        ['18-Oct', 'PO-0002', '17-Oct', 6, 0, 6, 'PO order date 16-Oct; masih open karena CO-14103 dibayar sisa PO-0001 (PO lebih lama)'],
        ['18-Oct', 'PO-0003', '18-Oct', 18, 0, 18, 'PO order date 17-Oct (18 pcs); total order 30 > PO tersedia 24 (6 + 18) = Short PO'],
        ['20-Oct', 'PO-0005', '19-Oct', 18, 12, 6, 'PO order date 18-Oct; 12 sudah dipakai CO-14113 + CO-14114, sisa 6'],
        ['20-Oct', 'PO-0006', '20-Oct', 18, 0, 18, 'PO order date 19-Oct']], [10, 12, 10, 11, 12, 12, 70])

    # ---------- 3. #TEMP_INSTRUCTION ----------
    ws, r = new_sheet(wb, '3. #TEMP_INSTRUCTION', 'Hasil XD09: line dipotong per PO dan per case 6 pcs', [
        'Qty line diberikan ke PO (urut PO date) lalu dipotong per case 6 pcs. Setiap potongan = 1 baris dengan ASSIGNED_QTY-nya sendiri.'])
    cols = ['Search', 'SORT_SEQ', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'OPEN_ORDER_QTY', 'ASSIGNED_QTY', 'PO_NO', 'CASE_SEQ', 'CUT_FLAG', 'CROSSDOCK_STATUS', 'Kenapa begini']
    rows = [
        ['18-Oct', 1, 'CO-14105', '9715310', 6, 6, 'PO-0002', 1, 'Y', 'Ready', 'Line 6 = 1 potongan: sisa PO-0002 6, case 1 penuh'],
        ['18-Oct', 2, 'CO-14106', '9715310', 3, 3, 'PO-0003', 2, 'N', 'Ready', 'Case 2 baru terisi 3 dari 6 -> belum boleh dipotong (CUT N)'],
        ['18-Oct', 3, 'CO-14107', '9715310', 3, 3, 'PO-0003', 2, 'Y', 'Ready', 'Case 2 = CO-14106 3 + CO-14107 3: 2 baris, 1 case'],
        ['18-Oct', 4, 'CO-14104', '9722D10', 6, 6, 'PO-0003', 3, 'Y', 'Ready', 'Case 3'],
        ['18-Oct', 5, 'CO-14109', '9811110', 6, 6, 'PO-0003', 4, 'Y', 'Ready', 'Case 4; PO-0003 habis (3+3+6+6 = 18)'],
        ['18-Oct', 6, 'CO-14110', '982220', 6, 6, None, 5, 'Y', 'Not Ready', 'PO tidak cukup (Short PO): baris tetap dibuat, PO_NO kosong'],
        ['20-Oct', 1, 'CO-14115', '9715310', 12, 6, 'PO-0005', 1, 'Y', 'Ready', '1 line 12 pcs -> potongan 1: sisa PO-0005 6 = case 1'],
        ['20-Oct', 1, 'CO-14115', '9715310', 12, 6, 'PO-0006', 2, 'Y', 'Ready', 'Potongan 2: PO-0006 6 = case 2 (OPEN 12 tetap sama di kedua baris)'],
        ['20-Oct', 2, 'CO-14111', '9722D10', 6, 6, 'PO-0006', 3, 'Y', 'Ready', 'Case 3'],
    ]
    fills = {i: (BAD if row[9] == 'Not Ready' else None) for i, row in enumerate(rows, 1)}
    t0 = r
    put(ws, r, cols, rows, [9, 9, 18, 14, 14, 13, 11, 9, 9, 13, 60], fills, key_cols=('ASSIGNED_QTY',))
    ws.freeze_panes = ws.cell(t0 + 1, 1)
    TI = "'3. #TEMP_INSTRUCTION'!"
    first, last = t0 + 1, t0 + len(rows)
    rng = lambda col: '%s$%s$%d:$%s$%d' % (TI, col, first, col, last)
    S, CO, OPEN, ASG, PO, CASE = rng('A'), rng('C'), rng('E'), rng('F'), rng('G'), rng('H')

    # ---------- 4. Cek ----------
    ws, r = new_sheet(wb, '4. Cek per line', 'Cek: jumlah ASSIGNED_QTY per line = OPEN_ORDER_QTY', ['Rumus SUMIFS dari kolom ASSIGNED_QTY sheet 3.'])
    lines = [('18-Oct', 'CO-14105', 6), ('18-Oct', 'CO-14106', 3), ('18-Oct', 'CO-14107', 3), ('18-Oct', 'CO-14104', 6), ('18-Oct', 'CO-14109', 6),
             ('18-Oct', 'CO-14110', 6), ('20-Oct', 'CO-14115', 12), ('20-Oct', 'CO-14111', 6)]
    rows = []
    for i, (s, co, op) in enumerate(lines):
        rr = r + 1 + i
        rows.append([s, co, op, '=COUNTIFS(%s,A%d,%s,B%d)' % (S, rr, CO, rr), '=SUMIFS(%s,%s,A%d,%s,B%d)' % (ASG, S, rr, CO, rr),
                     '=IF(E%d=C%d,"OK","SELISIH")' % (rr, rr)])
    put(ws, r, ['Search', 'CUSTOMER_ORDER_NO', 'OPEN_ORDER_QTY', 'Jumlah potongan', 'Total ASSIGNED_QTY', 'Cek'], rows, [9, 18, 15, 15, 17, 10], key_cols=('Total ASSIGNED_QTY',))

    # ---------- 5. XD10 per case ----------
    ws, r = new_sheet(wb, '5. XD10 per case', 'Tampilan XD10 per case dihitung dari ASSIGNED_QTY', [
        'Qty = SUM ASSIGNED_QTY case itu; Remaining Qty (not assigned) = SUM ASSIGNED_QTY yang PO_NO kosong; Ready kalau Remaining 0.'])
    cases = [('18-Oct', 1, 'PO-0002 6', 'CO-14105 9715310 6'), ('18-Oct', 2, 'PO-0003 6', 'CO-14106 9715310 3, CO-14107 9715310 3'),
             ('18-Oct', 3, 'PO-0003 6', 'CO-14104 9722D10 6'), ('18-Oct', 4, 'PO-0003 6', 'CO-14109 9811110 6'), ('18-Oct', 5, '-', 'CO-14110 982220 6'),
             ('20-Oct', 1, 'PO-0005 6', 'CO-14115 9715310 6'), ('20-Oct', 2, 'PO-0006 6', 'CO-14115 9715310 6'), ('20-Oct', 3, 'PO-0006 6', 'CO-14111 9722D10 6')]
    rows = []
    for i, (s, c, po, content) in enumerate(cases):
        rr = r + 1 + i
        rows.append([s, c, '=SUMIFS(%s,%s,A%d,%s,B%d)' % (ASG, S, rr, CASE, rr), '=SUMIFS(%s,%s,A%d,%s,B%d,%s,"")' % (ASG, S, rr, CASE, rr, PO, ),
                     po, content, '=IF(D%d=0,"Ready","Not Ready")' % rr])
    put(ws, r, ['Search', 'Case', 'Qty (pcs)', 'Remaining Qty (not assigned)', 'PO (supplier lihat)', 'Content (D/S team saja)', 'PO Status'], rows,
        [9, 7, 10, 16, 18, 40, 12], key_cols=('Qty (pcs)', 'Remaining Qty (not assigned)'))

    # ---------- 6. Create ASN ----------
    ws, r = new_sheet(wb, '6. Create ASN', 'Create ASN 18-Oct (case 1-4 dipilih, ASN0003): ASSIGNED_QTY dipakai untuk MAPPED_QTY dan TB_R_INSTRUCTION', [
        'Case 5 Not Ready (tanpa PO) tidak bisa dipilih.'])
    ws.cell(r - 1, 1, 'A. TB_R_PRA_DAILY_ORDER_MAPPED: MAPPED_QTY ditambah ASSIGNED_QTY per PO').font = FB
    pos = [('PO-0002', 6, 0), ('PO-0003', 18, 0)]
    rows = []
    for i, (po, oq, before) in enumerate(pos):
        rr = r + 1 + i
        rows.append([po, oq, before, '=SUMIFS(%s,%s,"18-Oct",%s,A%d,%s,"<=4")' % (ASG, S, PO, rr, CASE), '=C%d+D%d' % (rr, rr), '=B%d-E%d' % (rr, rr)])
    r = put(ws, r, ['PO_NO', 'ORDER_QTY', 'MAPPED_QTY sebelum', '+ ASSIGNED_QTY case 1-4', 'MAPPED_QTY sesudah', 'Open PO qty sesudah'], rows,
            [12, 11, 16, 20, 17, 17], key_cols=('+ ASSIGNED_QTY case 1-4',))
    ws.cell(r - 1, 1, 'B. TB_R_INSTRUCTION: 1 baris per potongan, QTY = ASSIGNED_QTY').font = FB
    rows = [['ASN0003', 1, 'CO-14105', '9715310', 'PO-0002', 6], ['ASN0003', 2, 'CO-14106', '9715310', 'PO-0003', 3],
            ['ASN0003', 2, 'CO-14107', '9715310', 'PO-0003', 3], ['ASN0003', 3, 'CO-14104', '9722D10', 'PO-0003', 6],
            ['ASN0003', 4, 'CO-14109', '9811110', 'PO-0003', 6]]
    r = put(ws, r, ['ASN_NO', 'CASE_NO', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'PO_NO', 'QTY (= ASSIGNED_QTY)'], rows, [10, 9, 18, 15, 12, 18],
            key_cols=('QTY (= ASSIGNED_QTY)',))
    ws.cell(r - 1, 1, 'C. Search berikutnya (19-Oct)').font = FB
    put(ws, r, ['Akibat', 'Penjelasan'], [
        ['Open qty line', 'Open qty = ORDER_STATUS_QTY - SUM(QTY TB_R_INSTRUCTION): CO-14105..CO-14109 jadi 0, tidak diambil lagi; CO-14110 tetap 6.'],
        ['Open PO', 'PO-0002 dan PO-0003 sisa 0 (lihat tabel A) -> tidak diambil lagi; CO-14110 menunggu split PO PO-0004.'],
        ['Kalau tanpa ASSIGNED_QTY', 'Tidak bisa tahu PO mana dapat berapa pcs (case 2 dibayar PO-0003 dari 2 line) dan bagian line mana yang sudah ada di ASN (CO-14115 case 1 di ASN0006, case 2 di ASN0007).'],
    ], [24, 120])

    tmp = tempfile.mkdtemp()
    raw = os.path.join(tmp, os.path.basename(OUT))
    wb.save(raw)
    # recalculate with LibreOffice so the formula values are cached (previews show them)
    subprocess.run(['soffice', '--headless', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', os.path.join(tmp, 'calc'), raw],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copy(os.path.join(tmp, 'calc', os.path.basename(OUT)), OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
