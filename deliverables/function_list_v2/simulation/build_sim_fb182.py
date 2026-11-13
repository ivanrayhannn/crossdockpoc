"""FB-182 simulation: hold per case stored by CASE_SEQ (old) vs the rule decided 13-Nov (the hold follows its destination), data of PART-X 17-Oct (6 pcs/case).
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
    """Cara | Hasil (merged B:D) | Benar? in the 5 columns of the case table."""
    for c, h in ((1, 'Cara'), (2, 'Hasil'), (5, 'Benar?')):
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


def resolve(cases, seq, dest, order):
    """Rule decided 13-Nov (FB-182): 1) same Customer Order No + Destination; 2) same Destination nearest to the saved case number
    (lower on a tie); 3) destination gone: the case at the saved number, or the last case. None = no case left."""
    if not cases:
        return None
    own = next((c for c in cases if any(l[0] == order and l[1] == dest for l in c['lines'])), None)
    if own:
        return own['seq']
    same = [c for c in cases if any(l[1] == dest for l in c['lines'])]
    if same:
        return min(same, key=lambda c: (abs(c['seq'] - seq), c['seq']))['seq']
    return min(seq, len(cases))


def case_rows(cases, held_seq=None):
    rows, fills = [], {}
    for c in cases:
        for j, (o, d, q, po) in enumerate(c['lines']):
            rows.append([f'Case {c["seq"]}' + (' (hold)' if c['seq'] == held_seq and j == 0 else '') if j == 0 else '', o, d, q, po])
            if c['seq'] == held_seq:
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
        ['Kejadian C (sheet 5)', 'CO-14109 Taiwan sendiri di-cancel: tidak ada lagi line Taiwan di unit.'],
        ['Cara lama', 'TB_R_CROSSDOCK_CASE_HOLD hanya menyimpan CASE_SEQ. Hold ikut nomor, bukan isi.'],
        ['Aturan baru (disepakati 13-Nov)', 'Simpan juga DESTINATION_CD dan CUST_ORDER_NO dari line pertama case saat [Save]. Setiap Search hold dicocokkan lagi: '
                            '1) case yang masih berisi Customer Order No + Destination itu; 2) kalau tidak ada, case dengan Destination yang sama, paling dekat ke nomor case lama; '
                            '3) kalau destination itu sudah tidak ada, hold geser ke destination lain: case di nomor yang sama (atau case terakhir). '
                            'Baris hold di-update ke case hasil cocok. Aturan Ready tetap: case hold dan sesudahnya tidak Ready.'],
    ], [22, 120])

    # ---------- Search 18-Oct ----------
    ws, r = sheet(wb, '2. Search 18-Oct', 'Search 18-Oct: D/S hold case 4 (CO-14109 Taiwan)', [
        'PO tersedia: PO-0002 sisa 6 + PO-0003 18 = 24 pcs. Case 5 belum dapat PO.'])
    c18 = cut(L17, [('PO-0002', 6), ('PO-0003', 18)])
    rows, fills = case_rows(c18, held_seq=4)
    r = table(ws, r, cols, rows, W, fills)
    ws, r = sheet(wb, '2b. Isi tabel hold', 'Yang disimpan saat [Save] di Search 18-Oct', [])
    table(ws, r, ['Disimpan', 'Cara lama', 'Aturan baru'], [
        ['Isi tabel hold', 'PART-X / 17-Oct / 5001-1 / CASE_SEQ 4', 'PART-X / 17-Oct / 5001-1 / CASE_SEQ 4 / DESTINATION_CD 9811110 / CUST_ORDER_NO CO-14109'],
        ['Hasil', 'Case 1-3 Ready, case 4 On Hold, case 5 Not Ready', 'Sama: case 1-3 Ready, case 4 On Hold, case 5 Not Ready'],
    ], [18, 40, 60])

    # ---------- Kejadian A ----------
    ws, r = sheet(wb, '3. Kejadian A - cancel', 'Kejadian A: 19-Oct CO-14104 Japan di-cancel (UPD_STATUS 2), hold belum diubah', [
        'Line yang di-cancel tidak diambil Search. PO tersedia 19-Oct: PO-0002 6 + PO-0003 18 + split PO PO-0004 12.'])
    HS, HD, HO = 4, TW, 'CO-14109'
    LA = [l for l in L17 if l[0] != 'CO-14104']
    cA = cut(LA, [('PO-0002', 6), ('PO-0003', 18), ('PO-0004', 12)])
    ws.cell(r - 1, 1, 'Cara lama: hold tetap CASE_SEQ 4').font = FB
    rows, fills = case_rows(cA, held_seq=4)
    r = table(ws, r, cols, rows, W, fills)
    ws.cell(r - 1, 1, f'Aturan baru: langkah 1 (CO-14109 Taiwan masih ada) -> case {resolve(cA, HS, HD, HO)}').font = FB
    rows, fills = case_rows(cA, resolve(cA, HS, HD, HO))
    r = table(ws, r, cols, rows, W, fills)
    result(ws, r, [
        ['Cara lama', 'Case 4 sekarang CO-14110 Australia yang di-hold. Taiwan (case 3) jadi Ready dan bisa dikirim.', 'SALAH: hold pindah ke Australia'],
        ['Aturan baru', 'Case 3 (CO-14109 Taiwan) yang di-hold, case 4 Australia ikut tidak Ready (aturan: case sesudah hold). Baris hold di-update ke CASE_SEQ 3.', 'BENAR: tetap Taiwan'],
    ], {1: BAD, 2: OK})

    # ---------- Kejadian B ----------
    ws, r = sheet(wb, '4. Kejadian B - ASN', 'Kejadian B: supplier buat ASN case 1-2 (Korea 12 pcs), lalu Search lagi', [
        'Case yang sudah masuk ASN tidak muncul lagi; sisa unit dipotong ulang mulai case 1.'])
    LB = [l for l in L17 if l[0] not in ('CO-14105', 'CO-14106', 'CO-14107')]
    cB = cut(LB, [('PO-0003', 12)])
    ws.cell(r - 1, 1, 'Cara lama: hold tetap CASE_SEQ 4').font = FB
    rows, fills = case_rows(cB, held_seq=4)
    r = table(ws, r, cols, rows, W, fills)
    ws.cell(r - 1, 1, f'Aturan baru: langkah 1 (CO-14109 Taiwan masih ada) -> case {resolve(cB, HS, HD, HO)}').font = FB
    rows, fills = case_rows(cB, resolve(cB, HS, HD, HO))
    r = table(ws, r, cols, rows, W, fills)
    result(ws, r, [
        ['Cara lama', 'Sisa unit cuma 3 case, case 4 tidak ada: hold hilang, Taiwan (case 2) Ready dan bisa dikirim.', 'SALAH: hold hilang'],
        ['Aturan baru', 'Case 2 (CO-14109 Taiwan) di-hold, case 3 Australia ikut tidak Ready.', 'BENAR: tetap Taiwan'],
    ], {1: BAD, 2: OK})

    # ---------- Kejadian C ----------
    ws, r = sheet(wb, '5. Kejadian C - TW hilang', 'Kejadian C: 19-Oct CO-14109 Taiwan di-cancel, tidak ada line Taiwan lain di unit', [
        'Destination yang di-hold sudah tidak ada: hold geser ke destination lain (case di nomor yang sama).'])
    LC = [l for l in L17 if l[0] != 'CO-14109']
    cC = cut(LC, [('PO-0002', 6), ('PO-0003', 18), ('PO-0004', 12)])
    hc = resolve(cC, HS, HD, HO)
    ws.cell(r - 1, 1, f'Aturan baru: langkah 1 dan 2 tidak ketemu (Taiwan hilang) -> langkah 3, case {hc}').font = FB
    rows, fills = case_rows(cC, hc)
    r = table(ws, r, cols, rows, W, fills)
    result(ws, r, [
        ['Cara lama', 'Case 4 (CO-14110 Australia) di-hold.', 'Sama hasilnya'],
        ['Aturan baru', f'Taiwan sudah tidak ada, hold geser ke case {hc} (CO-14110 Australia, destination lain). Baris hold di-update ke 982220 / CO-14110. '
                        'D/S bisa lepas hold lewat [Edit hold] kalau tidak perlu lagi.', 'Sesuai keputusan 13-Nov'],
    ], {1: OK, 2: OK})

    # ---------- Usulan ----------
    ws, r = sheet(wb, '6. Keputusan', 'Perubahan TB_R_CROSSDOCK_CASE_HOLD (disepakati 13-Nov)', [])
    r = table(ws, r, ['Kolom', 'Cara lama', 'Aturan baru'], [
        ['Key unit', 'PART_NO, ORDER_DT, SUPPLIER_CD, SUPPLIER_PLANT', 'Sama'],
        ['Key hold', 'CASE_SEQ', 'CASE_SEQ (tetap 1 baris per case)'],
        ['Kolom tambahan', '-', 'DESTINATION_CD, CUST_ORDER_NO (line pertama case saat [Save])'],
        ['Tampilan check box', 'Dicentang kalau CASE_SEQ ada', 'Dicentang di case hasil pencocokan (langkah 1-3)'],
        ['Order di-cancel / case sudah ASN', 'Hold bisa pindah ke destination lain atau hilang (sheet 3, 4)', 'Hold tetap di destination yang sama (sheet 3, 4)'],
        ['Destination yang di-hold hilang', 'Hold di case nomor sama', 'Hold geser ke destination lain: case nomor sama atau case terakhir (sheet 5)'],
        ['Semua case unit sudah ASN', 'Baris tertinggal', 'Baris hold dihapus'],
    ], [34, 50, 80])
    table(ws, r, ['FB', 'Status', 'Keputusan'], [
        ['FB-182', 'Done', '13-Nov: hold 1 case geser ke destination yang sama kalau ada; kalau tidak ada baru geser ke destination lain. Sudah di XD10 5.3, XD09 4.3, ERD dan prototype.'],
    ], [9, 15, 120])

    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
