"""FB-182 simulation (rev. 14-Nov): a held case leaves the unit before the PO pouring; its PO qty goes back to the next orders.
Data of PART-X 17-Oct / 18-Oct (6 pcs/case), as in the prototype.
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


def pour(units, pos):
    """units: [(order date, [(order, dest, qty)])] in H0253 order; pos: [[po, open]] shared and reduced in place (oldest PO first).
    Returns {order date: cases}; a case = {'seq', 'lines': [(order, dest, qty, po)]}."""
    out = {}
    for dt, lines in units:
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
        out[dt] = [{'seq': i + 1, 'lines': c} for i, c in enumerate(cases)]
    return out


def case_rows(dt, cases, held=()):
    """Rows: Order Date | Case | Customer Order No | Destination | Qty | PO | PO Status; held lines at the end."""
    rows, fills = [], {}
    ready = True
    for c in cases:
        ready = ready and all(l[3] != '-' for l in c['lines'])
        for j, (o, d, q, po) in enumerate(c['lines']):
            rows.append([dt if not rows else '', f'Case {c["seq"]}' if j == 0 else '', o, d, q, po, ('Ready' if ready else 'Not Ready') if j == 0 else ''])
            fills[len(rows)] = OK if ready else BAD
    for o, d, q in held:
        rows.append(['', 'On hold', o, d, q, '- (PO dilepas)', 'On Hold (D/S)'])
        fills[len(rows)] = HOLD
    return rows, fills


def po_rows(pos0, res):
    rows = []
    for po, qty in pos0:
        use = [f'{o} {q}' for cs in res.values() for c in cs for (o, d, q, p) in c['lines'] if p == po]
        used = sum(q for cs in res.values() for c in cs for (o, d, q, p) in c['lines'] if p == po)
        rows.append([po, qty, ', '.join(use) or '-', qty - used])
    return rows


def scenario(wb, title, heading, notes, units, pos0, held=None, outcome=None):
    held = held or {}
    ws, r = sheet(wb, title, heading, notes)
    res = pour(units, [list(p) for p in pos0])
    rows, fills = [], {}
    for dt, cs in res.items():
        rr, ff = case_rows(dt, cs, held.get(dt, ()))
        fills.update({k + len(rows): v for k, v in ff.items()})
        rows += rr
    r = table(ws, r, ['Customer Order Date', 'Case', 'Customer Order No', 'Destination', 'Qty', 'PO', 'PO Status'], rows, [14, 11, 18, 20, 7, 18, 15], fills)
    ws.cell(r - 1, 1, 'Pemakaian PO (dituang dari baris paling atas, PO paling lama dulu)').font = FB
    r = table(ws, r, ['PO', 'Qty PO', 'Dipakai oleh', 'Sisa'], po_rows(pos0, res), [14, 11, 18, 20])
    if outcome:
        table(ws, r, ['Hasil'], [[x] for x in outcome], [14])
        for k in range(len(outcome) + 1):
            ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=7)
            ws.row_dimensions[r + k].height = 28 if k else 16
    return res


def main():
    wb = Workbook()
    wb.remove(wb.active)
    KR, JP, TW, AU = '9715310 Korea', '9722D10 Japan', '9811110 Taiwan', '982220 Australia'
    D17 = [('CO-14105', KR, 6), ('CO-14106', KR, 3), ('CO-14107', KR, 3), ('CO-14104', JP, 6), ('CO-14109', TW, 6), ('CO-14110', AU, 6)]
    D18 = [('CO-14112', KR, 6), ('CO-14113', TW, 6), ('CO-14114', AU, 6)]
    no_tw = [l for l in D17 if l[0] != 'CO-14109']
    P18 = [('PO-0002', 6), ('PO-0003', 18)]
    P19 = P18 + [('PO-0004', 12), ('PO-0005', 18)]
    TWH = [('CO-14109', TW, 6)]

    ws, r = sheet(wb, '1. Penjelasan', 'FB-182 (rev. 14-Nov): hold per case - PO yang sudah ter-mapping dilepas untuk order berikutnya', [
        'Data PART-X, 6 pcs/case, sama dengan prototype. Hijau = Ready, merah = Not Ready, kuning = On Hold (D/S).'])
    table(ws, r, ['Poin', 'Penjelasan'], [
        ['Aturan', 'D/S centang Hold (D/S) di case lalu [Save]. Customer order line di case itu (dengan qty-nya) disimpan di TB_R_CROSSDOCK_CASE_HOLD.'],
        ['Saat Search (XD09)', 'Pcs yang di-hold dikeluarkan dari unit SEBELUM PO dituang. Pcs itu tidak dapat PO; PO qty-nya mengalir ke baris berikutnya '
                               '(tanggal yang sama, lalu Customer Order Date berikutnya). Case lain dipotong ulang dan tetap Ready sesuai PO-nya.'],
        ['Yang tidak lagi berlaku', 'Aturan lama "case yang di-hold dan semua case sesudahnya tidak Ready" dan aturan geser hold (cara 13-Nov) dihapus.'],
        ['Tampilan', 'Line yang di-hold tampil di bawah case: Case = On hold, PO = dilepas, PO Status = On Hold (D/S). Supplier juga melihatnya tapi tidak bisa memilihnya.'],
        ['Release', 'D/S untick line On hold lalu [Save]: line kembali ke posisinya di urutan H0253 dan dituang PO lagi di Search berikutnya.'],
        ['Sheet 2-5', '2. Search 18-Oct sebelum hold; 3. Hold Taiwan 18-Oct; 4. Search 19-Oct (PO Taiwan dipakai order 18-Oct); 5. Release Taiwan setelah ASN.'],
    ], [22, 120])

    scenario(wb, '2. Sebelum hold', 'Search 18-Oct, belum ada hold', ['PO tersedia: PO-0002 sisa 6 + PO-0003 18 = 24 pcs, order 17-Oct 30 pcs.'],
             [('17-Oct', D17)], P18, outcome=['Case 1-4 Ready (Taiwan di case 4 pakai PO-0003). Case 5 Australia belum dapat PO: Not Ready.'])
    scenario(wb, '3. Hold Taiwan 18-Oct', 'Search 18-Oct: D/S hold case 4 (CO-14109 Taiwan 6 pcs) lalu [Save]', [
        'Taiwan keluar dari unit sebelum PO dituang. PO-0003 6 pcs yang tadinya untuk Taiwan mengalir ke baris berikutnya: CO-14110 Australia.'],
             [('17-Oct', no_tw)], P18, {'17-Oct': TWH},
             outcome=['Case 1-4 (Korea, Korea, Japan, Australia) semua Ready. Taiwan On Hold (D/S), tidak pakai PO.',
                      'Australia sekarang dapat PO-0003 6 pcs dan bisa dikirim.'])
    scenario(wb, '4. Search 19-Oct', 'Search 19-Oct: Taiwan masih di-hold, CO-14104 Japan cancel, PO-0004 (split) dan PO-0005 rilis', [
        'Order 18-Oct ikut di-Search. PO-0003 yang dilepas Taiwan dipakai order berikutnya (CO-14112 Korea, 18-Oct).'],
             [('17-Oct', [l for l in no_tw if l[0] != 'CO-14104']), ('18-Oct', D18)], P19, {'17-Oct': TWH},
             outcome=['17-Oct: case 1-3 Ready, Taiwan On Hold. 18-Oct: CO-14112 pakai sisa PO-0003 (6 pcs bekas Taiwan), case 1-3 Ready.',
                      'Tanpa hold, PO-0003 habis di 17-Oct dan CO-14112 baru dapat PO-0004.'])
    scenario(wb, '5. Release Taiwan', 'Release Taiwan 18-Oct setelah supplier buat ASN case 1-4 17-Oct (Korea, Japan, Australia)', [
        'Case yang sudah masuk ASN tidak dituang ulang. Sisa PO 18-Oct = 0, jadi Taiwan yang kembali belum dapat PO.'],
             [('17-Oct', [('CO-14109', TW, 6)])], [('PO-0002 (sisa setelah ASN)', 0), ('PO-0003 (sisa setelah ASN)', 0)],
             outcome=['Taiwan kembali ke unit 17-Oct sebagai case 1 dan Not Ready sampai ada PO lagi: split PO PO-0004 (19-Oct).',
                      'Kalau di-release sebelum ASN dibuat, Taiwan ada di atas Australia di urutan H0253, jadi Taiwan dapat PO-0003 lagi dan Australia kembali Not Ready (lihat FB-183).'])

    ws, r = sheet(wb, '6. Tabel & FB', 'TB_R_CROSSDOCK_CASE_HOLD (rev. 14-Nov)', [])
    r = table(ws, r, ['Kolom', 'Isi'], [
        ['PART_NO, ORDER_DT, SUPPLIER_CD, SUPPLIER_PLANT', 'Unit (Part Number + Customer Order Date + supplier)'],
        ['CUSTOMER_CD, CUSTOMER_ORDER_NO, DESTINATION_CD, DETAILED_ITEM_NO, SERIAL_NO', 'Customer order line (H0253) di case yang dicentang'],
        ['HOLD_QTY', 'Pcs line itu di case yang dicentang (line 12 pcs terpecah 2 case, 1 case di-hold = 6)'],
        ['CREATED_BY/DT, CHANGED_BY/DT', 'Audit'],
        ['Hapus baris', 'Line di-untick + [Save], line di-cancel GTOPAS, atau open qty line = 0'],
    ], [48, 90])
    table(ws, r, ['FB', 'Status', 'Isi'], [
        ['FB-182', 'Done', '14-Nov: case yang di-hold tidak menahan case lain. PO-nya dilepas dan dipakai order berikutnya; case lain tetap Ready (sheet 3, 4).'],
        ['FB-183', 'Perlu konfirmasi', 'Saat Taiwan di-release dan case lain belum masuk ASN, Taiwan dapat PO lagi sesuai urutan H0253 (lebih dulu dari Australia), '
                                       'jadi Australia bisa kembali Not Ready. Setuju, atau line yang di-release masuk antrean paling belakang?'],
    ], [9, 15, 120])

    wb.save(OUT)
    print('saved', OUT)


if __name__ == '__main__':
    main()
