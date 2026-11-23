"""Staging per target (3 tables, header OPERATION_TYPE, SP_STG_WRITE) full flow simulation -> Excel.
Source: stg_flow_steps.json (node dump_stg_flow.cjs, from Staging_Per_Target_Full_Flow.html) and the SQL of Staging_Header_Order.html.
Run: python3 build_stg_flow_xlsx.py"""
import html
import json
import os
import re
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Staging_Per_Target_Full_Flow_Simulation.xlsx')
data = json.load(open(os.path.join(HERE, 'stg_flow_steps.json'), encoding='utf-8'))
STEPS, DEST = data['steps'], data['dest']
doc = open(os.path.join(HERE, 'Staging_Header_Order.html'), encoding='utf-8').read()
SQL = [html.unescape(x) for x in re.findall(r'<pre[^>]*>(.*?)</pre>', doc, re.S)]

F = lambda **k: Font(name='Arial', size=k.pop('size', 9), **k)
HDR, HELP = PatternFill('solid', fgColor='DCEBFA'), PatternFill('solid', fgColor='FFF1C2')
ST_FILL = {0: PatternFill('solid', fgColor='FFF1D6'), 1: PatternFill('solid', fgColor='E1F2E5'), 2: PatternFill('solid', fgColor='F2F2F2')}
OK, NG = PatternFill('solid', fgColor='E1F2E5'), PatternFill('solid', fgColor='FBE3DF')
TOUCH = PatternFill('solid', fgColor='123A6B')
thin = Side(style='thin', color='B7C9DB')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
my = lambda per: per[4:] + '/' + per[:4]
name = lambda p: 'DUMMY PART ' + p[-3:]
bpd = lambda d: DEST[d][:5] + '-' + DEST[d][5:]


class Sheet:
    def __init__(self, ws):
        self.ws, self.r, self.w = ws, 1, {}
        ws.sheet_view.showGridLines = False

    def title(self, t, sub=None):
        self.ws.cell(self.r, 1, t).font = F(size=12, bold=True)
        self.r += 1
        if sub:
            self.ws.cell(self.r, 1, sub).font = F(italic=True, color='4F6580')
            self.r += 1
        self.r += 1

    def h(self, t):
        self.ws.cell(self.r, 1, t).font = F(size=10, bold=True, color='123A6B')
        self.r += 1

    def note(self, t, color='4F6580', italic=True):
        for line in t.split('\n'):
            self.ws.cell(self.r, 1, line).font = F(italic=italic, color=color)
            self.r += 1

    def table(self, cols, rows, fills=None, marks=None):
        """cols: [(title, helper?)]; rows: lists; fills: per row fill or None; marks: per row True = changed in the step."""
        for j, (c, hp) in enumerate(cols, 1):
            x = self.ws.cell(self.r, j, c)
            x.font, x.fill, x.border = F(bold=True), HELP if hp else HDR, BOX
            x.alignment = Alignment(wrap_text=True, vertical='center')
            self.w[j] = max(self.w.get(j, 6), min(36, len(str(c)) + 2))
        self.r += 1
        for i, row in enumerate(rows):
            for j, v in enumerate(row, 1):
                x = self.ws.cell(self.r, j, v)
                x.font, x.border = F(), BOX
                if fills and fills[i]:
                    x.fill = fills[i]
                if isinstance(v, str) and len(v) > 40:
                    x.alignment = Alignment(wrap_text=True, vertical='top')
                self.w[j] = max(self.w.get(j, 6), min(60, len(str(v)) + 2))
            if marks and marks[i]:
                self.ws.cell(self.r, 1).font = F(bold=True, color='123A6B')
            self.r += 1
        self.r += 1

    def done(self):
        for j, w in self.w.items():
            self.ws.column_dimensions[self.ws.cell(1, j).column_letter].width = w


def eff(mp, per):
    ks = sorted(k for k in (mp or {}) if k <= per)
    return mp[ks[-1]] if ks else None


wb = Workbook()
wb.remove(wb.active)

# ---------- Steps ----------
ov = Sheet(wb.create_sheet('Steps'))
ov.title('Staging per target: full flow simulation (dummy parts)',
         'TB_H_STG_APPOLE_KANBAN / _EXPORT / TB_H_STG_GTOPAS, SP_STG_WRITE at the save, SP_STG_SYNC at [Sync], views V_APPOLE_UPLOAD_*. Period Current / Next, RPA parent flow. Proposal 23-Nov-2026.')
rows = []
for i, s in enumerate(STEPS):
    f = s['files']
    made = ', '.join(n for n, k in (('EXPORT_PRE', 'pre'), ('KANBAN', 'kan'), ('EXPORT_POST', 'post')) if f and f[k])
    if s['gsent']:
        made += (', ' if made else '') + 'GTOPAS'
    r = s.get('rpa')
    scn = '-' if not r else ('Rollover' if r['sc'] == 'Rollover' else 'Scenario ' + r['sc']) + f" · GTOPAS {r['g']} · AP POLE {r['ap']}"
    rows.append([f'S{i:02d}', s['t'], s['actor'], s['label'], scn, made or '-', s['story']])
ov.table([('Sheet', 0), ('When', 0), ('Who', 0), ('Step', 0), ('RPA parent flow', 0), ('Files sent', 0), ('What happens', 0)], rows)
for row in ov.ws.iter_rows(min_row=5, min_col=7, max_col=7):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical='top')
ov.done()
ov.ws.column_dimensions['E'].width = 40
ov.ws.column_dimensions['G'].width = 110

# ---------- Flow Process (Indonesian, casual) ----------
fp = Sheet(wb.create_sheet('Flow Process'))
fp.title('Alur proses (dari save sampai AP POLE dan GTOPAS)')
fp.table([('No', 0), ('Proses', 0), ('Siapa', 0), ('Yang terjadi', 0)], [
    [0, 'Add Part (XD01 / XD02 flag A)', 'Procurement', 'Part baru selalu Candidate. Period dipilih: bulan berjalan (default) atau Next; part berlaku mulai period itu. Pilih bulan berjalan setelah tanggal D: baris Next ikut dibuat. Candidate belum dikirim, jadi nggak ada baris staging.'],
    [1, 'Save di screen / upload (XD01, XD02, XD03)', 'Procurement, D/S', 'Master di-update dulu, lalu SP_STG_WRITE dipanggil per nilai yang berubah. SP nulis baris ke tabel staging (status 0), nandain baris lama yang belum terkirim jadi 2 (Superseded), dan ngisi OPERATION_TYPE di baris Kanban.'],
    [2, 'XD05 day D (period baru)', 'Batch', 'Bikin period Next. Kanban ADD buat semua part (OPERATION_TYPE dibanding Max period sebelumnya), Export ADD per destinasi, DELETE (0) buat destinasi period lalu yang udah nggak dipakai atau part yang jadi Inactive.'],
    [3, 'Cuma Export yang berubah', 'SP_STG_WRITE', 'Kalau part + period belum punya baris Kanban status 0, SP nulis header ACTION KEEP dengan OPERATION_TYPE 5 (nilai Kanban yang lagi berlaku). Header ini nggak ikut diupload.'],
    [4, '[Sync]', 'D/S', 'SP_STG_SYNC cuma ngubah status 0 jadi 1 + RUN_ID (AP POLE: period Current dan Next, GTOPAS: Current aja). Nggak ada aturan yang dihitung di sini. Habis itu parent flow RPA jalan.'],
    [4.5, 'Parent flow RPA', 'Power Automate', 'Cek ada baris GTOPAS di run atau nggak. Ada (part jadi Active / Inactive, destinasi ditambah / dihapus): skenario 1, XD06 dulu, XD07 jalan cuma kalau GTOPAS berhasil. Nggak ada: skenario 2, langsung XD07. Period Rollover: XD06 aja.'],
    [5, 'View', 'NSP (database)', 'Nentuin file: header OPERATION_TYPE 1 → Export part itu masuk EXPORT_PRE (sebelum KANBAN), selain itu EXPORT_POST. Header 5 nggak masuk file KANBAN. Di dalam file, baris yang turun / DELETE dulu baru yang naik / ADD (ROW_ORDER).'],
    [6, 'XD07 (RPA AP POLE)', 'Bot', 'Upload per run: EXPORT_PRE → KANBAN → EXPORT_POST. File yang kosong nggak dibikin. Nama file: <template>_<RUN_ID>_<urutan>_<nama>.xls.'],
    [7, 'XD06 (RPA GTOPAS)', 'Bot', 'Nambah / hapus part + destinasi di WVJA5204 sesuai ACTION. Baris yang udah ada / udah hilang dihitung OK. Baris gagal dicatat, baris lain tetap jalan; hasil FAILED bikin XD07 nggak jalan. GTOPAS nggak punya period, jadi period Next nunggu Period Rollover.'],
    [8, 'Period Rollover (tanggal 1)', 'Batch', 'Period Next jadi Current. Baris GTOPAS period itu yang masih status 0 jadi 1 dan dikirim ke XD06.'],
    [9, 'E-mail FAILED', 'D/S', 'Klik [Re-send last Sync]: run ID sama, GTOPAS dulu (kalau ada), lalu file AP POLE dengan urutan sama. Re-send dulu sebelum [Sync] berikutnya.'],
])
fp.h('Business rules')
fp.note('\n'.join([
    '1. NSP ngecek tiap save (screen dan upload): total Case/Day destinasi ≤ Max Case/Day part di period itu. Jadi hasil akhir tiap run selalu valid.',
    '2. Max turun (OPERATION_TYPE 1): destinasi dulu (EXPORT_PRE), baru Max (KANBAN).',
    '3. Max naik / sama / part baru (2 / 3 / 4): Max dulu (KANBAN), baru destinasi (EXPORT_POST).',
    '4. Cuma destinasi yang berubah (5): EXPORT_POST aja.',
    '5. Di dalam satu file, per part: yang turun atau DELETE (0) dulu, baru yang naik atau ADD.',
    '6. Ganti destinasi atau ganti Order Type: DELETE (0) dulu, baru ADD, di file yang sama.',
    '7. Active → Inactive: DELETE (0) semua destinasi, Kanban tetap di AP POLE (header 5).',
    '8. Period baru: AP POLE tetap pakai data period lama sampai ada baris baru, jadi NSP selalu nambahin baris period baru.',
    '9. Nilai diubah lalu balik ke nilai yang udah terkirim sebelum [Sync]: nggak ada yang dikirim (Superseded).',
    '10. GTOPAS cuma dapat baris kalau destinasi muncul atau hilang buat part itu (order type apa pun).',
    '11. GTOPAS gagal di skenario 1: AP POLE nggak dikirim sama sekali sampai Re-send berhasil.',
    '12. Candidate bisa jadi Active lewat layar (Procurement) atau XD05; nggak ada yang balik ke Candidate.',
]), color='0F2540', italic=False)
fp.done()
fp.ws.column_dimensions['D'].width = 110

# ---------- Legend (Indonesian, casual) ----------
lg = Sheet(wb.create_sheet('Legend'))
lg.title('Legend')
lg.h('Warna')
lg.table([('Warna', 0), ('Artinya', 0)], [['', 'Header biru: kolom yang ada di file upload / layar GTOPAS'], ['', 'Header kuning: kolom bantu (cuma di NSP, nggak ikut file)'],
                                         ['', 'SYNC_STATUS 0: belum terkirim'], ['', 'SYNC_STATUS 1: udah terkirim'], ['', 'SYNC_STATUS 2: Superseded, nggak dikirim'],
                                         ['', 'Cek AP POLE OK'], ['', 'Cek AP POLE ditolak / GTOPAS FAILED / e-mail FAILED'], ['▶', 'Baris yang ditulis / diubah di langkah ini (kolom Changed)']],
         fills=[HDR, HELP, ST_FILL[0], ST_FILL[1], ST_FILL[2], OK, NG, None])
lg.h('OPERATION_TYPE (header di TB_H_STG_APPOLE_KANBAN)')
lg.table([('Kode', 0), ('Artinya', 0), ('Urutan upload part itu', 0)], [
    [1, 'Max turun (dibanding Max terakhir yang terkirim: period sama, atau period sebelumnya)', 'EXPORT_PRE → KANBAN'],
    [2, 'Max naik', 'KANBAN → EXPORT_POST'],
    [3, 'Max sama (cuma Pcs/Case berubah, atau period baru dengan Max sama)', 'KANBAN → EXPORT_POST'],
    [4, 'Part belum pernah dikirim', 'KANBAN → EXPORT_POST'],
    [5, 'Kanban nggak berubah, cuma destinasi (header ACTION KEEP, nggak diupload)', 'EXPORT_POST aja'],
])
lg.h('Kolom lain')
lg.table([('Kolom', 0), ('Isi', 0)], [
    ['ACTION', 'ADD / EDIT / DELETE; KEEP = header kode 5'],
    ['ROW_ORDER (view)', '1 = turun atau DELETE (0), 2 = naik atau ADD, dibanding nilai terakhir yang terkirim buat key itu'],
    ['SYNC_RUN_ID', 'Run [Sync] / Rollover / Re-send (YYYYMMDDHHMMSS)'],
    ['File', 'EXPORT_PRE (LLM9Q880, urutan 1), KANBAN (LLM9Q910, urutan 2), EXPORT_POST (LLM9Q880, urutan 3)'],
    ['Cek AP POLE', 'Total Max Shipping Box (RCS) part di bulan itu ≤ Max Shipping Box Qty, dicek habis tiap baris diupload'],
    ['Destinasi (dummy)', ', '.join(f'{k} {v}' for k, v in DEST.items())],
])
lg.done()

# ---------- one sheet per step ----------
for i, s in enumerate(STEPS):
    sh = Sheet(wb.create_sheet(f'S{i:02d} ' + re.sub(r'[\[\]:/\\?*]', '', s['label'])[:26]))
    sh.title(f'Step {i}. {s["label"]}', f'{s["t"]} · {s["actor"]}')
    sh.note(s['story'], color='0F2540', italic=False)
    sh.r += 1
    sh.h('What NSP does')
    sh.note('\n'.join(s['calls']), color='0F2540', italic=False)
    for row in sh.ws.iter_rows(min_row=sh.r - len('\n'.join(s['calls']).split('\n')), max_row=sh.r - 1, max_col=1):
        for c in row:
            c.font = Font(name='Consolas', size=9)
    sh.r += 1
    r = s.get('rpa')
    if r:
        mail = 'FAILED' if 'FAILED' in (r['g'], r['ap']) else 'SUCCESS'
        sh.h(f"RPA parent flow · run {r['run']} · " + ('Rollover (XD06 only)' if r['sc'] == 'Rollover' else 'Scenario ' + r['sc']))
        sh.table([('RUN_TYPE', 0), ('GTOPAS rows in the run', 0), ('XD06 GTOPAS', 0), ('XD07 AP POLE', 0), ('E-mail', 0)], [[r['type'], r['gRows'], r['g'], r['ap'], mail]],
                 fills=[NG if mail == 'FAILED' else OK])
    if s['gsent']:
        sh.h('XD06 · GTOPAS WVJA5204')
        sh.table([('Action on WVJA5204', 1), ('Depot Code', 0), ('P/No.', 0), ('Destination Code', 0), ('Maker Code', 0), ('Domestic/Overseas', 0), ('TOPAS Order Type', 0), ('Order Transportation Code', 0), ('Result', 1)],
                 [['Delete (MT = DEL)' if g['act'] == 'DELETE' else 'Add', '01', g['p'], DEST[g['d']] + ' ' + g['d'], 'A', 2, 3, 2, g.get('res', 'OK')] for g in s['gsent']],
                 fills=[NG if g.get('res') == 'FAILED' else OK for g in s['gsent']])
    f = s['files']
    chk = lambda c: f"{'OK' if c['ok'] else 'Rejected'}: total {c['t']} {'≤' if c['ok'] else '>'} Max {c['mx']}"
    if f:
        run = f['run']
        for title, key in ((f'XD07 · 1 EXPORT_PRE · LLM9Q880_{run}_1_EXPORT_PRE.xls', 'pre'), (f'XD07 · 3 EXPORT_POST · LLM9Q880_{run}_3_EXPORT_POST.xls', 'post')):
            if key == 'post' and f['kan']:
                sh.h(f'XD07 · 2 KANBAN · LLM9Q910_{run}_2_KANBAN.xls')
                sh.table([('Effective Month / Year', 0), ('Operator ID', 0), ('Part No.', 0), ('Part Name', 0), ('Shipping Box Qty', 0), ('Max Shipping Box Qty', 0), ('Max Allowance Qty', 0), ('OPERATION_TYPE', 1), ('AP POLE check', 1)],
                         [[my(x['r']['per']), 'P6', x['r']['p'], name(x['r']['p']), x['r']['pcs'], x['r']['max'], x['r']['pcs'] * x['r']['max'], x['r']['op'], chk(x['chk'])] for x in f['kan']],
                         fills=[OK if x['chk']['ok'] else NG for x in f['kan']])
            if f[key]:
                sh.h(title)
                sh.table([('Effective Month / Year', 0), ('Part No.', 0), ('Buyer-PD', 0), ('Order Type', 0), ('Transport Code', 0), ('Max Shipping Box (RCS)', 0), ('Destination', 1), ('ROW_ORDER (view)', 1), ('AP POLE check', 1)],
                         [[my(x['r']['per']), x['r']['p'].replace('-', ''), bpd(x['r']['d']), x['r']['ot'], 2, x['r']['cd'], x['r']['d'], f"{x['ro']} {'down' if x['ro'] == 1 else 'up'} ({'was ' + str(x['prev']) if x['prev'] is not None else 'new'})", chk(x['chk'])] for x in f[key]],
                         fills=[OK if x['chk']['ok'] else NG for x in f[key]])
        if key == 'post' and f['kan'] and not f['post']:
            pass
    # master
    sh.h('NSP master after the step (TB_M_PART_CANDIDATE + _DEST)')
    mrows = []
    for per in sorted(s['M']):
        for p, m in s['M'][per].items():
            mrows.append([per, p, m['st'], m['pcs'], m['max'], ', '.join(f"{k.replace('|', ' ')} {v}" for k, v in m['d'].items()) or '-', sum(m['d'].values())])
    sh.table([('Period', 0), ('Part', 0), ('Status', 0), ('Pcs/Case', 0), ('Max', 0), ('Destinations (Case/Day)', 0), ('Total', 0)], mrows)
    # AP POLE
    sh.h('AP POLE after the step (value active per Effective Month)')
    arows, afill = [], []
    months = sorted({mo for mp in s['AP']['kan'].values() for mo in mp})
    for mo in months:
        for p in sorted(s['AP']['kan']):
            k = eff(s['AP']['kan'][p], mo)
            if not k:
                continue
            ds = [(key, eff(mp, mo)) for key, mp in (s['AP']['exp'].get(p) or {}).items()]
            ds = [(key, v) for key, v in ds if v is not None]
            t = sum(v for _, v in ds)
            arows.append([my(mo), p, k['pcs'], k['max'], ', '.join(f"{key.replace('|', ' ')} {v}" for key, v in ds) or '-', t])
            afill.append(OK if t <= k['max'] else NG)
    sh.table([('Eff. month', 0), ('Part', 0), ('Shipping Box', 0), ('Max', 0), ('Buyer-PD active (RCS)', 0), ('Total', 0)], arows, fills=afill)
    sh.h('GTOPAS WVJA5204 after the step (part + destination)')
    sh.table([('P/No.', 0), ('Destination Code', 0)], [[k.split('|')[0], DEST[k.split('|')[1]] + ' ' + k.split('|')[1]] for k in sorted(s['GT'])])
    # staging
    st_txt = {0: '0', 1: '1', 2: '2'}
    sh.h('TB_H_STG_APPOLE_KANBAN')
    sh.table([('Changed', 1), ('STG_ID', 1), ('PERIOD', 1), ('ACTION', 1), ('PART_STATUS', 1), ('EFFECTIVE MONTH / YEAR', 0), ('OPERATOR ID', 0), ('PART NO.', 0), ('PART NAME', 0), ('SHIPPING BOX QTY', 0), ('MAX SHIPPING BOX QTY', 0), ('MAX ALLOWANCE QTY', 0), ('OPERATION_TYPE', 1), ('SOURCE', 1), ('SYNC_STATUS', 1), ('SYNC_RUN_ID', 1), ('CREATED_BY', 1), ('CREATED_DT', 1)],
             [['▶' if 'K%d' % r['id'] in s['touched'] else '', 'K%d' % r['id'], r['per'], r['act'], r['ps'], my(r['per']), 'P6', r['p'], name(r['p']), r['pcs'], r['max'], r['pcs'] * r['max'], r['op'], r['src'], st_txt[r['st']], r['run'] or '', r['by'], r['dt']] for r in s['K']],
             fills=[ST_FILL[r['st']] for r in s['K']])
    sh.h('TB_H_STG_APPOLE_EXPORT')
    sh.table([('Changed', 1), ('STG_ID', 1), ('PERIOD', 1), ('NSP_PART_NO', 1), ('DEST_CODE', 1), ('ACTION', 1), ('EFFECTIVE MONTH / YEAR', 0), ('PART NO.', 0), ('BUYER-PD', 0), ('ORDER TYPE', 0), ('TRANSPORT CODE', 0), ('MAX SHIPPING BOX (RCS)', 0), ('SOURCE', 1), ('SYNC_STATUS', 1), ('SYNC_RUN_ID', 1), ('CREATED_BY', 1), ('CREATED_DT', 1)],
             [['▶' if 'E%d' % r['id'] in s['touched'] else '', 'E%d' % r['id'], r['per'], r['p'], DEST[r['d']] + ' ' + r['d'], r['act'], my(r['per']), r['p'].replace('-', ''), bpd(r['d']), r['ot'], 2, r['cd'], r['src'], st_txt[r['st']], r['run'] or '', r['by'], r['dt']] for r in s['E']],
             fills=[ST_FILL[r['st']] for r in s['E']])
    sh.h('TB_H_STG_GTOPAS')
    sh.table([('Changed', 1), ('STG_ID', 1), ('PERIOD', 1), ('ACTION', 1), ('DEPOT CODE', 0), ('P/NO.', 0), ('DESTINATION CODE', 0), ('MAKER CODE', 0), ('DOMESTIC / OVERSEAS', 0), ('TOPAS ORDER TYPE', 0), ('ORDER TRANSPORTATION CODE', 0), ('SOURCE', 1), ('SYNC_STATUS', 1), ('SYNC_RUN_ID', 1), ('CREATED_DT', 1)],
             [['▶' if 'G%d' % r['id'] in s['touched'] else '', 'G%d' % r['id'], r['per'], r['act'], '01', r['p'], DEST[r['d']] + ' ' + r['d'], 'A', 2, 3, 2, r['src'], st_txt[r['st']], r['run'] or '', r['dt']] for r in s['G']],
             fills=[ST_FILL[r['st']] for r in s['G']])
    sh.done()
    sh.ws.column_dimensions['A'].width = max(sh.ws.column_dimensions['A'].width or 0, 22)

# ---------- SQL ----------
sq = Sheet(wb.create_sheet('SQL'))
sq.title('Stored procedures and views (draft, T-SQL style)', 'From Staging_Header_Order.html')
for block in SQL:
    for line in block.split('\n'):
        c = sq.ws.cell(sq.r, 1, line)
        c.font = Font(name='Consolas', size=9)
        sq.r += 1
    sq.r += 2
sq.ws.column_dimensions['A'].width = 140

wb.save(OUT)
print('saved', OUT)
