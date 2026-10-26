"""simulasi_asn_rev.xlsx: one PO per customer order date (PO_DT = order date + 1, qty = total order qty of the date, all destinations);
PO qty < order qty = abnormality → rest in a split PO. 4 destinations; cancel of a middle row after ASN → Change Order Number."""
import sys, copy, datetime as dt, openpyxl
from openpyxl.styles import PatternFill, Font
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'function_list_v2', 'specs'))
from scan_pack import pack
SRC, OUT = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(SRC)
ws, s2 = wb['Sheet1'], wb['Sheet2']
YEL, RED = PatternFill('solid', fgColor='FFFFFF00'), PatternFill('solid', fgColor='FFF4B084')
D = lambda s: dt.datetime.strptime(s, '%Y-%m-%d')
VN, TH, PH, D4 = '9715310', '9722D10', '9811110', '982220'
CU = {VN: '9715300', TH: '9722D10', PH: '9811100', D4: '982200'}
O = {}  # customer order: (order date, destination, qty)
for co, od, de, q in [('CO-14101', '2026-10-15', VN, 6), ('CO-14102', '2026-10-15', TH, 6), ('CO-14103', '2026-10-16', TH, 6),
                      ('CO-14104', '2026-10-17', TH, 6), ('CO-14105', '2026-10-17', VN, 6), ('CO-14106', '2026-10-17', VN, 3),
                      ('CO-14107', '2026-10-17', VN, 3), ('CO-14109', '2026-10-17', PH, 6), ('CO-14110', '2026-10-17', D4, 6),
                      ('CO-14112', '2026-10-18', VN, 6), ('CO-14113', '2026-10-18', PH, 6), ('CO-14114', '2026-10-18', D4, 6),
                      ('CO-14111', '2026-10-19', TH, 6), ('CO-14115', '2026-10-19', VN, 12), ('CO-14115/0000002', '2026-10-19', VN, 6)]:
    O[co] = (od, de, q)
cust = lambda co: CU[O[co][1]]
cno = lambda co: co.split('/')[0]                                   # key 'CO-14115/0000002' = serial split by G-System
ser = lambda co: co.split('/')[1] if '/' in co else '0000001'
scan = lambda co: (O[co][0], cust(co), cno(co), ser(co))  # ORDER_DT (Allocation Priority), CUSTOMER_CD, CUSTOMER_ORDER_NO, SERIAL_NO
# one PO per order date (PO_DT = order date + 1); T0409014 = split PO of order date 17/10 (abnormal: 18 < 30)
POS = [('T0409011', '3126035911', '2026-10-16', '2026-10-15', 12), ('T0409012', '3126035912', '2026-10-17', '2026-10-16', 6),
       ('T0409013', '3126035913', '2026-10-18', '2026-10-17', 18), ('T0409014', '3126035914', '2026-10-19', '2026-10-17', 12),
       ('T0409015', '3126035915', '2026-10-19', '2026-10-18', 18), ('T0409016', '3126035916', '2026-10-20', '2026-10-19', 18)]
PO = {p[0]: p for p in POS}

# ---------- Sheet1 ----------
ST = {k: [copy.copy(ws.cell(r, c)._style) for c in range(1, 15)] for k, r in
      [('title', 1), ('date', 2), ('tab', 3), ('gh', 4), ('gd', 5), ('rh', 11), ('rd', 12)]}
GH = [ws.cell(4, c).value for c in range(1, 15)]
RH = [ws.cell(11, c).value for c in range(1, 15)]
RH[12] = 'ASN NO (dari TB_R_INSTRUCTION)'
ws.delete_rows(1, ws.max_row)
ws.merged_cells.ranges = set()
cur = [1]
def put(r, vals, sty):
    for c, v in enumerate(vals, 1):
        x = ws.cell(r, c, v); x._style = copy.copy(ST[sty][c - 1])
        if sty in ('gd', 'rd') and x.fill.fill_type and str(x.fill.fgColor.rgb) == 'FFFFFF00':
            x.fill = PatternFill()  # template highlight; changes are marked per cell below
def head(title, date, tab):
    r = cur[0]
    put(r, [title], 'title'); put(r + 1, [date], 'date'); put(r + 2, [tab], 'tab')
    return r + 3
prev_g, prev_r = {}, {}
def gsys(title, date, rows):
    """G-System (surrounding DB) as stored (not sorted): rows = [(co, status, note[, qty])]."""
    global prev_g
    r = head(title, date, 'TB_R_H0253_ORDER_CONTROL_PRE'); put(r, GH, 'gh'); new = {}
    for i, (co, s, note, *qq) in enumerate(rows):
        od, de, q = O[co]; q = qq[0] if qq else q
        put(r + 1 + i, [cust(co), cno(co), D(od), de, '001', ser(co), 'PART-X', q, s, None, None, None, note], 'gd')
        if prev_g.get(co, (None,))[0] != s: ws.cell(r + 1 + i, 9).fill = YEL
        if co in prev_g and prev_g[co][1] != q: ws.cell(r + 1 + i, 8).fill = YEL
        if co not in prev_g and '/' in co: ws.cell(r + 1 + i, 6).fill = YEL
        new[co] = (s, q)
    prev_g = new; cur[0] = r + len(rows) + 3
def rep(title, date, rows):
    """NSP replicate in H0253 order: rows = {co: (upd, hold, mapped, asn, note)}."""
    global prev_r
    r = head(title, date, 'NSP.TB_R_H0253_ORDER_CONTROL_PRE'); put(r, RH, 'rh')
    for i, co in enumerate(sorted(rows, key=scan)):
        od, de, q = O[co]; v = rows[co][:5]; q = rows[co][5] if len(rows[co]) > 5 else q
        put(r + 1 + i, [cust(co), cno(co), D(od), de, '001', ser(co), 'PART-X', q, '7', *v], 'rd')
        old = prev_r.get(co)
        if old is not None and (old[5] if len(old) > 5 else O[co][2]) != q: ws.cell(r + 1 + i, 8).fill = YEL
        for k in range(4):
            if (old is None and k in (1, 2)) or (old is not None and old[k] != v[k]): ws.cell(r + 1 + i, 10 + k).fill = YEL
        if old is None: ws.cell(r + 1 + i, 9).fill = YEL
    prev_r = {k: v for k, v in rows.items()}; cur[0] = r + len(rows) + 3
def upd(base, **kw):
    out = dict(base)
    for co, v in kw.items(): out[co.replace('_', '-')] = v
    return out

N, GS = 'NULL', 'Condition Data di Surrounding DB'
XR = 'Condition setelah XD08 replicate data (baris NSP diurutkan ORDER BY ORDER_DT (Allocation Priority), CUSTOMER_CD, CUSTOMER_ORDER_NO, …)'
gsys(GS + ' (order date 15/10 → 1 PO T0409011 PO_DT 16/10, qty 12)', '16/10/2026', [('CO-14101', '7', None), ('CO-14102', '7', None)])
R = {'CO-14101': (N, 'N', 'N', N, None), 'CO-14102': (N, 'N', 'N', N, None)}
rep('Condition baru pertama replicate data', '16/10/2026', R)
R = upd(R, CO_14101=(N, 'N', 'Y', 'ASN0001', 'Disubmit ASN (T0409011)'), CO_14102=(N, 'Y', 'N', N, 'Di Hold oleh D/S by screen; 6 pcs T0409011 tetap open'))
rep('Condition saat berhasil 1 data create ASN (CO-14101) dan 1 data di hold (CO-14102)', '16/10/2026', R)
gsys(GS + ' (order date 16/10 → 1 PO T0409012 PO_DT 17/10, qty 6)', '17/10/2026', [('CO-14101', '6', None), ('CO-14102', '2', None), ('CO-14103', '7', None)])
R = upd(R, CO_14101=('6', 'N', 'Y', 'ASN0001', '6 pcs received'), CO_14102=('2', 'Y', 'N', N, 'Cancel tanpa ASN: PO_MAPPED tetap N'),
        CO_14103=(N, 'N', 'N', N, 'Awal'))
rep(XR, '17/10/2026', R)
R = upd(R, CO_14103=(N, 'N', 'Y', 'ASN0002', 'ASN dengan sisa 6 pcs T0409011 (PO_DT lebih tua); T0409012 jadi open'))
rep('Condition saat berhasil create ASN (CO-14103)', '17/10/2026', R)
gsys(GS + ' (order date 17/10: 4 destinasi, total 30 pcs → T0409013 PO_DT 18/10 hanya 18 pcs = ABNORMAL)', '18/10/2026',
     [('CO-14101', '6', None), ('CO-14102', '2', None), ('CO-14103', '6', None), ('CO-14104', '7', None), ('CO-14105', '7', None), ('CO-14106', '7', None),
      ('CO-14107', '7', None), ('CO-14109', '7', None), ('CO-14110', '7', None)])
R = upd(R, CO_14103=('6', 'N', 'Y', 'ASN0002', '6 pcs received'),
        CO_14105=(N, 'N', 'N', N, 'Urutan ke-1 → Case 1 (T0409012)'), CO_14106=(N, 'N', 'N', N, 'Urutan ke-2 → Case 2 (T0409013)'),
        CO_14107=(N, 'N', 'N', N, 'Urutan ke-3 → Case 2 (T0409013)'), CO_14104=(N, 'N', 'N', N, 'Urutan ke-4 → Case 3 (T0409013), baris tengah'),
        CO_14109=(N, 'N', 'N', N, 'Urutan ke-5 → Case 4 (T0409013)'), CO_14110=(N, 'N', 'N', N, 'Urutan ke-6 → Case 5: PO kurang → Not Ready'))
rep(XR, '18/10/2026', R)
R = upd(R, **{c.replace('-', '_'): (N, 'N', 'Y', 'ASN0003', f'Udah ASN (Case {k})') for c, k in
              [('CO-14105', 1), ('CO-14106', 2), ('CO-14107', 2), ('CO-14104', 3), ('CO-14109', 4)]})
rep('Condition saat create ASN0003: Case 1-4 (Ready) dikirim; Case 5 CO-14110 menunggu split PO', '18/10/2026', R)
gsys(GS + ' (ASN0003 received; CO-14104 di baris tengah di-cancel; split PO T0409014 PO_DT 19/10 qty 12; order date 18/10: 3 destinasi → T0409015 PO_DT 19/10 qty 18)',
     '19/10/2026',
     [('CO-14101', '6', None), ('CO-14102', '2', None), ('CO-14103', '6', None), ('CO-14104', '2', 'Cancel (Case 3 ASN0003)'), ('CO-14105', '6', None),
      ('CO-14106', '6', None), ('CO-14107', '6', None), ('CO-14109', '6', None), ('CO-14110', '7', None),
      ('CO-14112', '7', 'Order date 18/10'), ('CO-14113', '7', 'Order date 18/10'), ('CO-14114', '7', 'Order date 18/10')])
R = upd(R, CO_14105=('6', 'N', 'Y', 'ASN0003', 'Received'), CO_14106=('6', 'N', 'Y', 'ASN0003', 'Received'), CO_14107=('6', 'N', 'Y', 'ASN0003', 'Received'),
        CO_14109=('6', 'N', 'Y', 'ASN0003', 'Received'),
        CO_14104=('2', 'N', 'Y', 'ASN0003', 'Cancel setelah ASN → LOG5, muncul di XD11 (Waiting for a candidate)'),
        CO_14110=(N, 'N', 'N', N, 'Sekarang Ready (split PO T0409014)'),
        CO_14112=(N, 'N', 'N', N, 'Order date 18/10 Case 1 (sisa T0409014)'), CO_14113=(N, 'N', 'N', N, 'Order date 18/10 Case 2 (T0409015)'),
        CO_14114=(N, 'N', 'N', N, 'Order date 18/10 Case 3 (T0409015)'))
rep(XR, '19/10/2026', R)
R = upd(R, CO_14110=(N, 'N', 'Y', 'ASN0004', 'Udah ASN (split PO T0409014)'),
        CO_14112=(N, 'N', 'Y', 'ASN0005', 'Udah ASN (Case 1, T0409014)'), CO_14113=(N, 'N', 'Y', 'ASN0005', 'Udah ASN (Case 2, T0409015)'),
        CO_14114=(N, 'N', 'Y', 'ASN0005', 'Udah ASN (Case 3, T0409015); sisa T0409015 6 pcs open'))
rep('Condition saat create ASN0004 (CO-14110) dan ASN0005 (order date 18/10, Case 1-3)', '19/10/2026', R)
gsys(GS + ' (ASN0004 & ASN0005 received; order date 19/10: CO-14111 TH 6 + CO-14115 VN 12 → T0409016 PO_DT 20/10 qty 18)', '20/10/2026',
     [('CO-14101', '6', None), ('CO-14102', '2', None), ('CO-14103', '6', None), ('CO-14104', '2', None), ('CO-14105', '6', None), ('CO-14106', '6', None),
      ('CO-14107', '6', None), ('CO-14109', '6', None), ('CO-14110', '6', None), ('CO-14112', '6', None), ('CO-14113', '6', None),
      ('CO-14114', '6', None), ('CO-14111', '7', None), ('CO-14115', '7', '1 line 12 pcs = 2 case')])
R = upd(R, CO_14110=('6', 'N', 'Y', 'ASN0004', 'Received'), CO_14112=('6', 'N', 'Y', 'ASN0005', 'Received'), CO_14113=('6', 'N', 'Y', 'ASN0005', 'Received'),
        CO_14114=('6', 'N', 'Y', 'ASN0005', 'Received'), CO_14115=(N, 'N', 'N', N, 'Urutan ke-1: Case 1 (sisa T0409015) + Case 2 (T0409016)'),
        CO_14111=(N, 'N', 'N', N, 'Urutan ke-2: Case 3 (T0409016), belum dikirim supplier'))
rep(XR, '20/10/2026', R)
R = upd(R, CO_14115=(N, 'N', 'N', 'ASN0006', 'Case 1 (6 dari 12) → ASN0006 rit 1; PO_MAPPED tetap N (line belum lengkap), open qty 6'))
rep('Condition saat create ASN0006 (Case 1 CO-14115, 6 pcs)', '20/10/2026', R)
R = upd(R, CO_14115=(N, 'N', 'Y', 'ASN0006, ASN0007', 'Case 2 (6 pcs) → ASN0007 rit 2; line lengkap → PO_MAPPED Y. 1 line di 2 ASN'))
rep('Condition saat create ASN0007 (Case 2 CO-14115): 1 line customer order ada di 2 ASN', '20/10/2026', R)
G21 = [('CO-14101', '6', None), ('CO-14102', '2', None), ('CO-14103', '6', None), ('CO-14104', '2', None), ('CO-14105', '6', None), ('CO-14106', '6', None),
       ('CO-14107', '6', None), ('CO-14109', '6', None), ('CO-14110', '6', None), ('CO-14112', '6', None), ('CO-14113', '6', None),
       ('CO-14114', '6', None), ('CO-14111', '6', 'Received tanpa ASN (barang Case 3 ASN0003)'),
       ('CO-14115', '6', 'ASN0006 received: line dipecah, serial lama = 6 pcs status 6', 6),
       ('CO-14115/0000002', '7', 'Serial baru: 6 pcs sisa (ASN0007 belum di-receive)')]
gsys(GS + ' (ASN0006 received → G-System memecah CO-14115 jadi 2 line; G-System alokasikan barang Case 3 ASN0003 ke CO-14111)', '21/10/2026', G21)
RW = upd(R, CO_14115=('6', 'N', 'Y', 'ASN0006, ASN0007', 'Qty 12 → 6, UPDT 6; TB_R_INSTRUCTION masih 12 pcs di serial ini (kelebihan 6)', 6))
RW['CO-14115/0000002'] = (N, 'N', 'N', N, 'Insert baru: open qty 6 → XD09 akan mapping lagi = DOUBLE (padahal sudah di ASN0007)')
RW = upd(RW, CO_14111=('6', 'N', 'N', N, 'Suggest buat gantiin CO-14104'))
keep = dict(prev_r)
rep('SALAH (contoh kalau TB_R_INSTRUCTION tidak ditata ulang): XD08 21/10 upsert saja', '21/10/2026', RW)
prev_r = keep
R = upd(R, CO_14111=('6', 'N', 'N', N, 'Suggest buat gantiin CO-14104 (UPDT 6, PO_MAPPED N, belum ASN, part & qty sama)'),
        CO_14115=('6', 'N', 'Y', 'ASN0006', 'Qty 12 → 6, UPDT 6; XD08 tata ulang: serial ini = ASN0006 (ASN paling dulu = yang di-receive)', 6))
R['CO-14115/0000002'] = (N, 'N', 'Y', 'ASN0007', 'Insert baru; XD08 tata ulang: baris ASN0007 pindah ke serial ini → PO_MAPPED Y, open qty 0')
rep('BENAR: XD08 21/10 upsert + tata ulang TB_R_INSTRUCTION (pecah serial). Change Order Number suggest CO-14111', '21/10/2026', R)
R = upd(R, CO_14104=('2', 'N', 'Y', N, 'PO_MAPPED tetap Y; baris TB_R_INSTRUCTION pindah ke CO-14111 (riwayat di TB_H)'),
        CO_14111=('6', 'N', 'Y', 'ASN0003', 'ASN0003 Case 3 dipindah dari CO-14104 (XD11)'))
rep('Condition setelah Change Order Number (ASN0003 Case 3: CO-14104 → CO-14111)', '21/10/2026', R)
gsys(GS + ' (ASN0007 received)', '22/10/2026', G21[:12] + [('CO-14111', '6', None), ('CO-14115', '6', None, 6), ('CO-14115/0000002', '6', 'ASN0007 received')])
R['CO-14115/0000002'] = ('6', 'N', 'Y', 'ASN0007', '6 pcs received')
R = upd(R, CO_14115=('6', 'N', 'Y', 'ASN0006', 'Received', 6))
rep(XR, '22/10/2026', R)

# ---------- Sheet2 ----------
KEY, OTH, DAT = [copy.copy(s2['B3']._style), copy.copy(s2['E3']._style), copy.copy(s2['C4']._style)]
for row in s2.iter_rows():
    for c in row: c.value = None; c.style = 'Normal'
def table(r, c, name, cols, rows, nkey=3, hl=(), fill=YEL):
    s2.cell(r, c).value = name; s2.cell(r, c).font = Font(bold=True)
    for j, h in enumerate(cols):
        x = s2.cell(r + 1, c + j, h); x._style = copy.copy(KEY if j < nkey else OTH)
    for i, vals in enumerate(rows):
        for j, v in enumerate(vals):
            x = s2.cell(r + 2 + i, c + j, v); x._style = copy.copy(DAT)
            if (i, cols[j]) in hl: x.fill = fill
    return r + 3 + len(rows)
tot = lambda od: sum(q for o, (d, _, q) in O.items() if d == od and '/' not in o)
chk = []
for od in sorted({p[3] for p in POS}):
    pq = [p for p in POS if p[3] == od]
    first = pq[0][4]
    chk.append([D(od), len({O[o][1] for o in O if O[o][0] == od}), tot(od), pq[0][0], D(pq[0][2]), first,
                'OK' if first >= tot(od) else f'ABNORMAL (kurang {tot(od) - first})',
                ', '.join(f'{p[0]} ({p[4]})' for p in pq[1:]) or '-'])
r = table(2, 2, 'Cek PO per customer order date (1 order date = 1 PO, PO_DT = order date + 1)',
          ['CUSTOMER_ORDER_DT', 'JML DESTINASI', 'TOTAL ORDER QTY', 'PO_NO', 'PO_DT', 'PO QTY', 'STATUS', 'SPLIT PO'], chk, nkey=1,
          hl={(i, 'STATUS') for i, x in enumerate(chk) if x[6] != 'OK'}, fill=RED)
PN = {'T0409011': '16/10 → CO-14101 6 (ASN0001); 6 pcs untuk CO-14102 (Hold, lalu cancel) → 17/10 dipakai CO-14103 (ASN0002)',
      'T0409012': 'Untuk CO-14103, tapi CO-14103 sudah dapat sisa T0409011 → 18/10 dipakai CO-14105 (Case 1 ASN0003)',
      'T0409013': 'ABNORMAL: 18 < 30 → Case 2-4 ASN0003 (CO-14106, CO-14107, CO-14104, CO-14109)',
      'T0409014': 'Split PO order date 17/10 → 19/10 CO-14110 (ASN0004); sisa 6 pcs (karena cancel CO-14104) → CO-14112 (ASN0005 Case 1)',
      'T0409015': 'Order date 18/10 (3 destinasi) → CO-14113, CO-14114 (ASN0005 Case 2-3); sisa 6 pcs → CO-14115 (ASN0006)',
      'T0409016': 'Order date 19/10 (CO-14111 6 + CO-14115 12) → CO-14115 6 (ASN0007); CO-14111 dapat Case 3 ASN0003 lewat Change Order Number → 12 pcs open'}
r = table(r, 2, 'TB_R_PRA_DAILY_ORDER_PART', ['Created', 'MANIFEST_NO', 'MANIFEST_ITEM', 'PO_NO', 'PO_ITEM', 'PART_NO', 'ORDER_QTY', 'PO_DT', 'Note'],
          [[p[2][8:] + '/10/2026', p[1], '0001', p[0], '0001', 'PART-X', p[4], D(p[2]), PN[p[0]]] for p in POS],
          hl={(2, 'ORDER_QTY'), (3, 'PO_NO')}, fill=RED)
MP = [('17/10/2026', 'T0409011', 12, '16/10: 6 (CO-14101), 17/10: +6 (CO-14103)'), ('18/10/2026', 'T0409012', 6, 'CO-14105'),
      ('18/10/2026', 'T0409013', 18, 'CO-14106, CO-14107, CO-14104, CO-14109; Change Order Number tidak mengubah MAPPED_QTY'),
      ('19/10/2026', 'T0409014', 12, 'CO-14110 (ASN0004), CO-14112 (ASN0005)'), ('20/10/2026', 'T0409015', 18, '19/10: CO-14113, CO-14114 (ASN0005); 20/10: +6 CO-14115 (ASN0006)'),
      ('20/10/2026', 'T0409016', 6, 'CO-14115 (ASN0007); 12 pcs masih open; pecah serial tidak mengubah MAPPED_QTY')]
r = table(r, 2, 'TB_R_PRA_DAILY_ORDER_MAPPED', ['Updated', 'PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'PART_NO', 'ORDER_QTY', 'MAPPED_QTY', 'Note'],
          [[u, p, PO[p][1], '0001', 'PART-X', PO[p][4], m, n] for u, p, m, n in MP], nkey=4)
INS = [('16/10/2026', 1, 'DRF-0001', 1, 1, 'CO-14101', 6, 'T0409011', 'ASN0001', None),
       ('17/10/2026', 2, 'DRF-0002', 1, 1, 'CO-14103', 6, 'T0409011', 'ASN0002', 'Sisa T0409011 (PO_DT 16/10 lebih tua dari T0409012)'),
       ('18/10/2026', 3, 'DRF-0003', 1, 1, 'CO-14105', 6, 'T0409012', 'ASN0003', 'ASN0003 = Case 1-4 order date 17/10'),
       ('18/10/2026', 4, 'DRF-0003', 2, 1, 'CO-14106', 3, 'T0409013', 'ASN0003', None),
       ('18/10/2026', 5, 'DRF-0003', 2, 2, 'CO-14107', 3, 'T0409013', 'ASN0003', 'Case 2 = CO-14106 3 + CO-14107 3 (destinasi sama)'),
       ('18/10/2026', 6, 'DRF-0003', 3, 1, 'CO-14104', 6, 'T0409013', 'ASN0003', 'Kondisi sebelum Change Order Number'),
       ('18/10/2026', 7, 'DRF-0003', 4, 1, 'CO-14109', 6, 'T0409013', 'ASN0003', None),
       ('19/10/2026', 8, 'DRF-0004', 1, 1, 'CO-14110', 6, 'T0409014', 'ASN0004', 'Split PO'),
       ('19/10/2026', 9, 'DRF-0005', 1, 1, 'CO-14112', 6, 'T0409014', 'ASN0005', 'ASN0005 = Case 1-3 order date 18/10; sisa split PO'),
       ('19/10/2026', 10, 'DRF-0005', 2, 1, 'CO-14113', 6, 'T0409015', 'ASN0005', None),
       ('19/10/2026', 11, 'DRF-0005', 3, 1, 'CO-14114', 6, 'T0409015', 'ASN0005', None),
       ('20/10/2026', 12, 'DRF-0006', 1, 1, 'CO-14115', 6, 'T0409015', 'ASN0006', 'Case 1 CO-14115 (rit 1)'),
       ('20/10/2026', 13, 'DRF-0007', 1, 1, 'CO-14115', 6, 'T0409016', 'ASN0007', 'Case 2 CO-14115 (rit 2): 1 line di 2 ASN'),
       ('21/10/2026 (update XD08)', 13, 'DRF-0007', 1, 1, 'CO-14115/0000002', 6, 'T0409016', 'ASN0007',
        'Pecah serial G-System: baris ASN0007 pindah ke serial 0000002 (ASN0006 = serial lama, status 6)'),
       ('21/10/2026 (update XD11)', 6, 'DRF-0003', 3, 1, 'CO-14111', 6, 'T0409013', 'ASN0003', 'Baris yang sama di-update: case, PO, ASN tetap')]
IC = ['Created', 'INSTRUCTION_ID', 'DRAFT_ID', 'CASE_SEQ', 'LINE_SEQ', 'PART_NO', 'CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'ORDER_DT', 'DESTINATION_CD',
      'DETAILED_ITEM_NO', 'SERIAL_NO', 'QTY', 'PO_NO', 'MANIFEST_NO', 'MANIFEST_ITEM', 'ASN_NO', 'CASE_NO', 'Note']
r = table(r, 2, 'TB_R_INSTRUCTION', IC, [[cr, i, dr, cs, ls, 'PART-X', cust(co), cno(co), D(O[co][0]), O[co][1], '001', ser(co), q, po, PO[po][1], '0001',
                                         asn, f'Case {cs}', n] for cr, i, dr, cs, ls, co, q, po, asn, n in INS],
          nkey=2, hl={(13, 'SERIAL_NO'), (14, 'CUSTOMER_ORDER_NO'), (14, 'ORDER_DT')})
table(r, 2, 'TB_H_CROSSDOCK_ORDER_CHANGE', ['Created', 'HIST_ID', 'ASN_NO', 'CASE_NO', 'PART_NO', 'FROM_CUSTOMER_ORDER_NO', 'FROM_SERIAL_NO',
      'TO_CUSTOMER_ORDER_NO', 'TO_DESTINATION_CD', 'QTY', 'FROM_INSTRUCTION_ID', 'TO_INSTRUCTION_ID', 'Note'],
      [['21/10/2026', 1, 'ASN0003', 'Case 3', 'PART-X', 'CO-14104', '0000001', 'CO-14111', TH, 6, 6, 6, 'Seluruh baris pindah (tidak dipecah)']], nkey=2)
for col, w in zip('BCDEFGHIJKLMNOPQRST', [22, 15, 15, 12, 12, 12, 22, 20, 14, 16, 14, 12, 12, 12, 14, 14, 12, 10, 40]):
    s2.column_dimensions[col].width = w

# ---------- #TEMP_INSTRUCTION ----------
st = wb.create_sheet('#TEMP_INSTRUCTION')
TC = ['SORT_SEQ', 'PART_NO', 'ORDER_DT', 'CUSTOMER_CD', 'CUSTOMER_ORDER_NO', 'DESTINATION_CD', 'OPEN_ORDER_QTY', 'ASSIGNED_QTY', 'PO_NO', 'MANIFEST_NO',
      'CASE_SEQ', 'CUM_DEST_QTY', 'SEQ_QTY', 'CUT_FLAG', 'GROUP_SEQ', 'CROSSDOCK_STATUS', 'Note']
st.cell(1, 1, 'Hasil XD09 [Search] per hari. PART-X 6 pcs/case. Urutan = ORDER_DT (Allocation Priority), CUSTOMER_CD, CUSTOMER_ORDER_NO, ...; '
        'PO urut PO_DT (sisa open qty). Hanya line UPDT_STATUS NULL, HOLD_FLAG N, PO_MAPPED_FLAG N. GROUP_SEQ hanya logic.').font = Font(italic=True)
INS_CHECK = {}
def search(r, title, units, pos, notes):
    st.cell(r, 1, title).font = Font(bold=True)
    for j, h in enumerate(TC):
        x = st.cell(r + 1, 1 + j, h); x._style = copy.copy(KEY if j < 1 else OTH)
    pos = [[p, PO[p][1], '0001', q] for p, q in pos]; out = []
    for cos in units:
        out += pack([dict(ORDER_DT=O[c][0], CUSTOMER_CD=cust(c), CUSTOMER_ORDER_NO=cno(c), ORDER_TIME='', DESTINATION_CD=O[c][1], DETAILED_ITEM_NO='001',
                          SERIAL_NO=ser(c), PART_NO='PART-X', QTY=O[c][2]) for c in cos], pos, 6)
    for i, s in enumerate(out):
        INS_CHECK.setdefault(s['CUSTOMER_ORDER_NO'], []).append((s['PO_NO'], s['CASE_SEQ'], s['ASSIGNED_QTY']))  # by customer order no
        vals = [s['SORT_SEQ'], 'PART-X', D(s['ORDER_DT']), s['CUSTOMER_CD'], s['CUSTOMER_ORDER_NO'], s['DESTINATION_CD'], s['QTY'], s['ASSIGNED_QTY'],
                s['PO_NO'], s['MANIFEST_NO'], s['CASE_SEQ'], s['CUM_DEST_QTY'], s['SEQ_QTY'], s['CUT_FLAG'], s['GROUP_SEQ'], s['CROSSDOCK_STATUS'],
                notes.get(s['CUSTOMER_ORDER_NO'])]
        for j, v in enumerate(vals):
            x = st.cell(r + 2 + i, 1 + j, v); x._style = copy.copy(DAT)
            if TC[j] == 'CUT_FLAG' and v == 'Y': x.fill = YEL
            if TC[j] == 'CROSSDOCK_STATUS' and v == '7': x.fill = RED
    return r + 3 + len(out)
O17 = ['CO-14104', 'CO-14105', 'CO-14106', 'CO-14107', 'CO-14109', 'CO-14110']
r = search(4, '16/10/2026 [Search] (CO-14102 Hold → tidak diambil)', [['CO-14101']], [('T0409011', 12)],
           {'CO-14101': 'Dipilih → ASN0001; T0409011 sisa 6 open'})
r = search(r, '17/10/2026 [Search]', [['CO-14103']], [('T0409011', 6), ('T0409012', 6)],
           {'CO-14103': 'Dapat sisa T0409011 (PO_DT 16/10 duluan) → ASN0002; T0409012 open'})
r = search(r, '18/10/2026 [Search]: order date 17/10, 4 destinasi, PO tersedia 24 dari 30 (abnormal)', [O17], [('T0409012', 6), ('T0409013', 18)],
           {'CO-14105': 'Case 1-4 Ready → ASN0003', 'CO-14104': 'Baris tengah (Case 3)', 'CO-14110': 'Not Ready: PO kurang (tunggu split PO)'})
r = search(r, '19/10/2026 [Search]: sisa order date 17/10 (CO-14104 UPDT 2, Case 1-4 sudah ASN → tidak diambil) + order date 18/10 (3 destinasi)',
           [['CO-14110'], ['CO-14112', 'CO-14113', 'CO-14114']], [('T0409014', 12), ('T0409015', 18)],
           {'CO-14110': 'Ready dengan split PO → ASN0004', 'CO-14112': 'Sisa T0409014 (PO_DT 19/10, PO no lebih kecil) → ASN0005 Case 1-3',
            'CO-14114': 'T0409015 sisa 6 open'})
r = search(r, '20/10/2026 [Search]: order date 19/10 (CO-14115 VN 12 = 2 case, CO-14111 TH 6)', [['CO-14111', 'CO-14115']], [('T0409015', 6), ('T0409016', 18)],
           {'CO-14115': 'Case 1 → ASN0006 (rit 1), Case 2 → ASN0007 (rit 2): 1 line di 2 ASN', 'CO-14111': 'Case 3 belum dikirim'})
r = search(r, '21/10/2026 [Search] SALAH (tanpa tata ulang TB_R_INSTRUCTION): serial 0000002 dianggap open 6 → mapping lagi', [['CO-14115/0000002']],
           [('T0409016', 12)], {'CO-14115': 'DOUBLE: 6 pcs ini sudah di ASN0007'})
st.cell(r, 1, '21/10/2026 [Search] BENAR (dengan tata ulang XD08): serial 0000001 = ASN0006, serial 0000002 = ASN0007 → open qty 0, tidak ada line diambil. '
        'CO-14111 UPDT 6 → tidak diambil; dapat Case 3 ASN0003 lewat Change Order Number.').font = Font(italic=True)
st.cell(r + 1, 1, 'Sisa PO open di akhir: T0409016 12 pcs = qty cancel CO-14102 + CO-14104.').font = Font(italic=True)
for col, w in zip('ABCDEFGHIJKLMNOPQ', [10, 10, 12, 13, 18, 15, 16, 14, 11, 13, 10, 14, 10, 10, 11, 18, 44]):
    st.column_dimensions[col].width = w
# consistency: the submitted rows equal the XD09 result of their Search
for cr, i, dr, cs, ls, co, q, po, asn, n in INS:
    if '(update' in cr: continue
    assert any(x[0] == po and x[2] == q for x in INS_CHECK[cno(co)]), (co, po, cs, INS_CHECK[cno(co)])
for sh in (s2, st):
    for row in sh.iter_rows():
        for c in row:
            if isinstance(c.value, dt.datetime): c.number_format = 'yyyy-mm-dd'
wb.save(OUT)
print('saved', OUT)
