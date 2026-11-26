"""Simulation per OPERATION_TYPE in the columns of the AP POLE files: per scenario of Staging_To_Upload_Files.html the saves, AP POLE
before the run, the staging rows of the run, the files EXPORT_PRE / KANBAN / EXPORT_POST in the template columns (LLM9Q880 / LLM9Q910,
header as in the template: green = filled, grey = left empty) and the AP POLE check per uploaded row, plus a wrong upload order.
Run: node dump_files_per_ot.cjs && python3 build_files_per_ot.py  ->  Simulation_Files_Per_Operation_Type.xlsx"""
import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Simulation_Files_Per_Operation_Type.xlsx')
D = json.load(open(os.path.join(HERE, 'files_per_ot.json')))
DEST, SDT, RUN = D['dest'], D['sdt'], D['run']
fill = lambda c: PatternFill('solid', fgColor=c)
GREEN, GREY, HDR, HELP, OK, NG, NOTE = fill('99FF99'), fill('A6A6A6'), fill('D9E1F2'), fill('FFF2CC'), fill('E2EFDA'), fill('FBE3DF'), fill('EAF1FB')
F1, F2, F3 = fill('E4D7F0'), fill('D6E2F2'), fill('D5EDEA')
FILE_FILL = {1: F1, 2: F2, 3: F3}
thin = Side(style='thin', color='808080')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F, FB = Font(name='Calibri', size=10), Font(name='Calibri', size=10, bold=True)
bpd = lambda d: DEST[d][:5] + '-' + DEST[d][5:]

# sheet name, short Indonesian text per scenario id
SHEETS = {
    'max-down': ('OT1 Max turun', 'Max DUMMY-001 turun 20 → 16. D/S turunkan destinasi dulu (JAPAN 12 → 6, KOREA 8 → 10), baru Procurement turunkan Max.',
                 'AP POLE masih punya Max 20 sampai file KANBAN masuk. Jadi destinasi dikirim dulu di EXPORT_PRE (yang turun dulu, baru yang naik), baru KANBAN dengan Max 16.'),
    'max-up': ('OT2 Max naik', 'Max DUMMY-002 naik 16 → 24, lalu D/S pakai ruangnya: TAIWAN 10 → 14, USA 6 → 10.',
               'Max baru dikirim dulu (KANBAN), baru destinasi (EXPORT_POST). Kalau dibalik, TAIWAN 14 + USA 6 = 20 lebih dari Max lama 16, ditolak.'),
    'pcs-only': ('OT3 Max sama', 'Pcs/Case DUMMY-003 berubah 8 → 10, Max tetap 10, mapping tidak berubah.',
                 'Max sama, jadi urutan tidak berpengaruh ke cek. Part ini tidak punya baris Export di run: cuma file 2 KANBAN yang dibuat.'),
    'new-part': ('OT4 Part baru', 'DUMMY-004 dari Candidate jadi Active (belum pernah dikirim), lalu dimapping KOREA 12, USA 8.',
                 'AP POLE belum kenal part ini, jadi KANBAN dulu, baru EXPORT_POST. Ada destinasi baru: GTOPAS ADD, skenario 1 (XD06 dulu).'),
    'dest-only': ('OT5 Destinasi', 'Cuma destinasi DUMMY-002 yang berubah: USA 6 → 4, THAILAND baru 2. Pcs/Case dan Max tetap.',
                  'SP_STG_WRITE tulis header ACTION KEEP (5) dengan nilai Kanban sekarang. Header tidak diupload: cuma EXPORT_POST, USA (turun) sebelum THAILAND (baru).'),
    'order-type': ('OT5 Order Type', 'Order Type DUMMY-001 JAPAN diganti ** → C, nilai tetap 12.',
                   'Order Type bagian dari key AP POLE: DELETE (0) JAPAN ** dulu, baru ADD JAPAN C, di file yang sama. GTOPAS tidak berubah (key part + destinasi).'),
    'inactive': ('OT5 Inactive', 'DUMMY-003 jadi Inactive, mapping THAILAND dihapus.',
                 'Kanban tetap ada di AP POLE (header 5, tidak diupload); semua destinasi dikirim 0 di EXPORT_POST. GTOPAS DELETE THAILAND.'),
    'twice': ('OT5 Edit 2x', 'D/S ubah DUMMY-002 USA 6 → 4 lalu 4 → 5, dan TAIWAN 10 → 8 lalu balik ke 10, semua sebelum [Sync].',
              'Satu baris belum terkirim per key: baris USA di-update jadi 5. TAIWAN balik ke nilai terkirim, barisnya dihapus. Yang dikirim cuma USA 5.'),
    'mixed': ('Campuran OT1-4', 'Perubahan OT1 sampai OT4 di atas disimpan di hari yang sama dan dikirim satu [Sync].',
              'File baris Export ikut OPERATION_TYPE part-nya: DUMMY-001 (1) di EXPORT_PRE, DUMMY-002 (2) dan DUMMY-004 (4) di EXPORT_POST. KANBAN isi keempat part.'),
}
KAN_HEAD = [('Effective Month', 1), ('Effective Year', 1), ('Operator ID', 1), ('Part No.', 1), ('Part Name', 1), ('Shipping Box Qty', 1),
            ('Max Shipping Box Qty', 1), ('Max Allowance Qty', 0), ('Packing/Pallet Type ... Outer-Qty (20 kolom)', 0)]
EXP_HEAD = [('Effective Month', 1), ('Effective Year', 1), ('Part No.', 1), ('Shipping Box Qty', 0), ('Max Shipping Box by Part No.', 0), ('Buyer-PD', 1),
            ('Order Type', 1), ('Transport Code', 1), ('Max Shipping Box (RCS)', 1), ('Max Allowance Qty', 0), ('Packing/Pallet Type', 0)]
WRONG = {'KANBAN before the Export rows': 'KANBAN sebelum baris Export', 'Export rows before KANBAN': 'baris Export sebelum KANBAN',
         'up / ADD rows before down / DELETE rows (ROW_ORDER ignored)': 'yang naik / ADD sebelum yang turun / DELETE (ROW_ORDER diabaikan)'}


class Sheet:
    def __init__(self, ws):
        self.ws, self.r = ws, 1
        ws.sheet_view.showGridLines = False

    def title(self, text, sub=None):
        self.ws.cell(self.r, 1, text).font = Font(name='Calibri', size=14, bold=True, color='1F3864')
        self.r += 1
        if sub:
            self.ws.cell(self.r, 1, sub).font = Font(name='Calibri', size=10, italic=True, color='595959')
            self.r += 1
        self.r += 1

    def h(self, text):
        self.ws.cell(self.r, 1, text).font = Font(name='Calibri', size=12, bold=True, color='1F3864')
        self.r += 1

    def note(self, text, f=NOTE, bold=False):
        c = self.ws.cell(self.r, 1, text)
        c.font, c.fill = Font(name='Calibri', size=10, bold=bold), f
        c.alignment = Alignment(wrap_text=True, vertical='top')
        self.ws.merge_cells(start_row=self.r, start_column=1, end_row=self.r, end_column=11)
        self.ws.row_dimensions[self.r].height = 30
        self.r += 2

    def table(self, head, rows, fills=None, head_fills=None):
        for c, h in enumerate(head, 1):
            x = self.ws.cell(self.r, c, h)
            x.font, x.border, x.fill = FB, BOX, (head_fills[c - 1] if head_fills else HDR)
            x.alignment = Alignment(wrap_text=True, vertical='center')
        self.r += 1
        for i, row in enumerate(rows):
            for c, v in enumerate(row, 1):
                x = self.ws.cell(self.r, c, v)
                x.font, x.border = F, BOX
                x.alignment = Alignment(wrap_text=True, vertical='top')
                if fills and fills[i]:
                    x.fill = fills[i]
            self.r += 1
        self.r += 1


def ap_before(x):
    """AP POLE before the run for the parts of the scenario: Kanban Max and the active destinations."""
    parts = sorted({r['p'] for r in x['K'] + x['E']} | {d['row']['p'] for d in x['deleted']})
    rows = []
    for p in parts:
        k = (x['apBefore']['kan'].get(p) or {}).get('202612')
        dests = (x['apBefore']['exp'].get(p) or {})
        ds = ', '.join(f"{bpd(key.split('|')[0])} ({key.split('|')[1]}) {v['202612']}" for key, v in dests.items() if v.get('202612'))
        tot = sum(v['202612'] for v in dests.values() if v.get('202612'))
        rows.append([p, k['pcs'] if k else 'belum ada', k['max'] if k else 'belum ada', ds or '-', tot])
    return rows


def row_name(kind, v):
    r = v['r']
    return f"{r['p']} Kanban Max {r['max']}" if kind == 'k' else f"{r['p']} {bpd(r['d'])} ({r['ot']}) = {r['cd']}"


wb = Workbook()
lg = Sheet(wb.active)
lg.ws.title = 'Legend'
lg.title('Simulasi file AP POLE per OPERATION_TYPE',
         f'Semua skenario mulai dari kondisi yang sama (period 202612 sudah terkirim), user simpan perubahan, lalu D/S klik [Sync] (SYNC_DT {SDT}). Data dummy.')
lg.h('OPERATION_TYPE (header di TB_H_STG_APPOLE_KANBAN)')
lg.table(['Kode', 'Artinya', 'Urutan upload part itu'], [
    [1, 'Max turun (dibanding Max terakhir yang terkirim: period sama, atau period sebelumnya)', 'EXPORT_PRE → KANBAN'],
    [2, 'Max naik', 'KANBAN → EXPORT_POST'],
    [3, 'Max sama (cuma Pcs/Case berubah, atau period baru dengan Max sama)', 'KANBAN → EXPORT_POST'],
    [4, 'Part belum pernah dikirim', 'KANBAN → EXPORT_POST'],
    [5, 'Kanban nggak berubah, cuma destinasi (header ACTION KEEP, nggak diupload)', 'EXPORT_POST aja']])
lg.h('Sheet skenario')
srows = []
for x in D['res']:
    name, story, _ = SHEETS[x['s']['id']]
    made = [n for n, k in ((f'1 EXPORT_PRE ({len(x["f"]["pre"])})', 'pre'), (f'2 KANBAN ({len(x["f"]["kan"])})', 'kan'), (f'3 EXPORT_POST ({len(x["f"]["post"])})', 'post')) if x['f'][k]]
    srows.append([name, ', '.join(map(str, x['s']['ot'])), story, ' → '.join(made) or '-'])
lg.table(['Sheet', 'OPERATION_TYPE', 'Skenario', 'File yang dibuat (jumlah baris)'], srows)
lg.h('Warna')
lg.table(['Warna', 'Artinya'], [['', 'Header hijau: kolom template yang diisi'], ['', 'Header abu-abu: kolom template yang dikosongkan'],
                                 ['', 'Header kuning: kolom bantu NSP, nggak ditulis ke file'], ['', 'Cek AP POLE OK'], ['', 'Ditolak AP POLE (total di atas Max)']],
         fills=[GREEN, GREY, HELP, OK, NG])
for c, w in zip('ABCD', (18, 16, 90, 44)):
    lg.ws.column_dimensions[c].width = w

for x in D['res']:
    name, story, why = SHEETS[x['s']['id']]
    sh = Sheet(wb.create_sheet(name))
    sh.title(name, f"OPERATION_TYPE {', '.join(map(str, x['s']['ot']))} · run SYNC_DT {SDT}")
    sh.note(story, bold=True)
    sh.h('1. Yang disimpan user')
    sh.table(['Jam', 'User', 'Save'], [a for a in x['s']['acts']])
    sh.h('2. AP POLE sebelum run (Effective Month 12/2026)')
    sh.table(['Part', 'Shipping Box Qty', 'Max Shipping Box Qty', 'Buyer-PD (Order Type) RCS', 'Total RCS'], ap_before(x))
    sh.h(f'3. Baris staging di run (SYNC_STATUS 1, SYNC_DT {SDT})')
    hdr = {k['p']: k for k in x['K']}
    sh.table(['STG_ID', 'PERIOD', 'ACTION', 'PART_NO', 'SHIPPING_BOX_QTY', 'MAX_SHIPPING_BOX_QTY', 'OPERATION_TYPE', 'Masuk file 2?'],
             [[k['id'], k['per'], k['act'], k['p'], k['pcs'], k['max'], k['op'], 'Tidak (header 5)' if k['op'] == 5 else 'Ya'] for k in x['K']] or [['-'] * 8])
    ex = sorted(x['f']['pre'] + x['f']['post'], key=lambda v: v['r']['id'])
    sh.table(['STG_ID', 'PERIOD', 'NSP_PART_NO', 'BUYER_PD', 'ORDER_TYPE', 'ACTION', 'MAX_SHIPPING_BOX_RCS', 'Nilai terkirim sebelumnya', 'ROW_ORDER', 'FILE_NO'],
             [[v['r']['id'], v['r']['per'], v['r']['p'], bpd(v['r']['d']), v['r']['ot'], v['r']['act'], v['r']['cd'], v['prev'] if v['prev'] is not None else 'baru',
               v['ro'], 1 if hdr[v['r']['p']]['op'] == 1 else 3] for v in ex] or [['-'] * 10])
    if x['deleted']:
        sh.note('Baris yang dihapus SP_STG_WRITE sebelum [Sync] (nggak dikirim): ' + '; '.join(
            f"{d['tag']} {d['row']['p']} {bpd(d['row']['d']) if 'd' in d['row'] else ''} ({d['why']})" for d in x['deleted']))
    sh.h('4. File upload AP POLE (urutan upload)')
    sh.note(why)
    for key, n, nm, tpl in (('pre', 1, 'EXPORT_PRE', 'LLM9Q880'), ('kan', 2, 'KANBAN', 'LLM9Q910'), ('post', 3, 'EXPORT_POST', 'LLM9Q880')):
        rows = x['f'][key]
        c = sh.ws.cell(sh.r, 1, f'File {n} · {tpl}_{RUN}_{n}_{nm}.xls' + ('' if rows else ' · tidak dibuat (tidak ada baris)'))
        c.font, c.fill = FB, FILE_FILL[n]
        sh.ws.merge_cells(start_row=sh.r, start_column=1, end_row=sh.r, end_column=11)
        sh.r += 1
        if not rows:
            sh.r += 1
            continue
        head = KAN_HEAD if key == 'kan' else EXP_HEAD
        data = ([[v['r']['per'][4:], v['r']['per'][:4], 'P6', v['r']['p'], 'DUMMY PART ' + v['r']['p'][-3:], v['r']['pcs'], v['r']['max'], '', ''] for v in rows]
                if key == 'kan' else
                [[v['r']['per'][4:], v['r']['per'][:4], v['r']['p'].replace('-', ''), '', '', bpd(v['r']['d']), v['r']['ot'], '2', v['r']['cd'], '', ''] for v in rows])
        sh.table([h for h, _ in head], data, head_fills=[GREEN if on else GREY for _, on in head])
    sh.h('5. Cek AP POLE setelah tiap baris diupload (total RCS semua Buyer-PD part ≤ Max)')
    ok = [('e', v, 1) for v in x['f']['pre']] + [('k', v, 2) for v in x['f']['kan']] + [('e', v, 3) for v in x['f']['post']]
    sh.table(['#', 'File', 'Baris', 'Total RCS part', 'Max di AP POLE', 'Hasil'],
             [[i + 1, n, row_name(kd, v), v['chk']['t'], v['chk'].get('mx') if v['chk'].get('mx') is not None else '- (part belum ada)', 'OK' if v['chk']['ok'] else 'Ditolak']
              for i, (kd, v, n) in enumerate(ok)], fills=[OK if v['chk']['ok'] else NG for _, v, _ in ok])
    for w in x['wrong']:
        sh.h(f"Kalau urutannya salah: {WRONG.get(w['label'], w['label'])}")
        sh.table(['#', 'File', 'Baris', 'Total RCS part', 'Max di AP POLE', 'Hasil'],
                 [[i + 1, 'KANBAN' if y['kind'] == 'k' else 'Export', row_name(y['kind'], y['x'])] + (['', '', 'tidak diupload (run berhenti)'] if y.get('skip') else
                  [y['chk']['t'], y['chk'].get('mx') if y['chk'].get('mx') is not None else '- (part belum ada)', 'OK' if y['chk']['ok'] else 'Ditolak'])
                  for i, y in enumerate(w['rows'])],
                 fills=[None if y.get('skip') else (OK if y['chk']['ok'] else NG) for y in w['rows']])
    r = x['rpa']
    sh.h('6. RPA')
    sh.note(('Skenario 1: ada baris GTOPAS, XD06 jalan dulu, XD07 jalan kalau XD06 berhasil.' if r['sc'] == '1' else 'Skenario 2: nggak ada baris GTOPAS, langsung XD07.')
            + f" Hasil: XD06 {r['g']}, XD07 {r['ap']}." + (' GTOPAS: ' + ', '.join(f"{g['act']} {g['p']} {DEST[g['d']]}" for g in x['gsent']) if x['gsent'] else ''))
    for c, w in zip('ABCDEFGHIJK', (14, 14, 30, 18, 22, 16, 18, 16, 20, 16, 18)):
        sh.ws.column_dimensions[c].width = w
    sh.ws.freeze_panes = 'A4'
wb.save(OUT)
print('saved', OUT, [ws.title for ws in wb.worksheets])
