"""Full sync flow simulation -> Excel: one sheet per step of Full_Sync_Flow.html (same tables, notes and colours).
Run: python3 build_full_sync_xlsx.py"""
import html
import os
import re
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'Full_Sync_Flow.html')
OUT = os.path.join(HERE, 'Full_Sync_Flow_Simulation.xlsx')
FILL = {'r-pend': 'FFF1D6', 'r-ok': 'E1F2E5', 'r-ng': 'FBE3DF', 'r-par': 'EEE8F7', 'r-sup': 'F2F2F2'}
HDR, SIM = PatternFill('solid', fgColor='DCEBFA'), PatternFill('solid', fgColor='FFF1C2')
thin = Side(style='thin', color='B7C9DB')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def text(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x))).strip()


def val(s):
    return int(s) if re.fullmatch(r'-?\d+', s) and not (len(s) > 1 and s.startswith('0')) and len(s) < 9 else s


page = open(SRC, encoding='utf-8').read()
NAVL = dict(re.findall(r'<a href="#([^"]+)">(.*?)</a>', page))
steps = re.findall(r'<section class="step" id="([^"]+)">(.*?)</section>', page, re.S)
wb = Workbook()
wb.remove(wb.active)
ov = wb.create_sheet('Steps')
ov['A1'] = 'Full sync flow with the staging table (TB_H_PART_CANDIDATE_STG_SYNC) – simulation, dummy parts'
ov['A1'].font = Font(name='Arial', size=12, bold=True)
ov.append([])
ov.append(['Sheet', 'When · who', 'Step'])
for c in ov[3]:
    c.font, c.fill, c.border = Font(name='Arial', size=9, bold=True), HDR, BOX
for sid, body in steps:
    no = text(re.search(r'<span class="no">(.*?)</span>', body).group(1))
    when = text(re.search(r'<div class="when">(.*?)</div>', body).group(1))
    title = text(re.search(r'<h2>(.*?)</h2>', body).group(1))
    name = text(NAVL.get(sid, f'{no} {title}'))[:31].replace('/', '-').replace(':', '').replace('[', '').replace(']', '')
    ov.append([name, when, title])
    for c in ov[ov.max_row]:
        c.font, c.border = Font(name='Arial', size=9), BOX
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws['A1'] = f'{no}. {title}'
    ws['A1'].font = Font(name='Arial', size=12, bold=True)
    ws['A2'] = when
    ws['A2'].font = Font(name='Arial', size=9, italic=True, color='4F6580')
    r = 4
    widths = {}
    sbody = body[body.index('<div class="step-body">'):]
    for m in re.finditer(r'<h3>(.*?)</h3>|<p class="(note|warn)">(.*?)</p>|<table>(.*?)</table>', sbody, re.S):
        if m.group(1) is not None:
            ws.cell(r, 1, text(m.group(1))).font = Font(name='Arial', size=10, bold=True, color='123A6B')
            r += 1
        elif m.group(2):
            c = ws.cell(r, 1, text(m.group(3)))
            c.font = Font(name='Arial', size=9, italic=m.group(2) == 'note', color='B23B2E' if m.group(2) == 'warn' else '4F6580')
            r += 1
        else:
            t = m.group(4)
            heads = re.findall(r'<th( class="th-sim")?>(.*?)</th>', t, re.S)
            for j, (sim, h) in enumerate(heads, 1):
                c = ws.cell(r, j, text(h))
                c.font, c.fill, c.border = Font(name='Arial', size=9, bold=True), SIM if sim else HDR, BOX
                c.alignment = Alignment(wrap_text=True, vertical='center')
                widths[j] = max(widths.get(j, 8), min(40, len(text(h)) + 2))
            r += 1
            for cls, row in re.findall(r'<tr class="([^"]*)">(.*?)</tr>', t, re.S):
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
                for j, x in enumerate(cells, 1):
                    v = text(x)
                    c = ws.cell(r, j, val(v))
                    c.font, c.border = Font(name='Arial', size=9), BOX
                    if cls.strip() in FILL:
                        c.fill = PatternFill('solid', fgColor=FILL[cls.strip()])
                    if cls.strip() == 'r-sup':
                        c.font = Font(name='Arial', size=9, color='7F8C99', strike=True)
                    widths[j] = max(widths.get(j, 8), min(40, len(v) + 2))
                r += 1
            r += 1
    for j, w in widths.items():
        ws.column_dimensions[get_column_letter(j)].width = w
for col, w in zip('ABC', (34, 34, 90)):
    ov.column_dimensions[col].width = w
legend = ['', 'Penjelasan istilah dan warna: lihat sheet Legend.']
for x in legend:
    ov.append([x])

# ---- Flow Process sheet (bahasa Indonesia) ----
from openpyxl.drawing.image import Image as XLImage  # noqa: E402
import subprocess  # noqa: E402
IMG = os.path.join(HERE, 'flow_img', 'sync_flow.png')
try:
    subprocess.run(['dot', '-Tpng', '-Gdpi=110', os.path.join(HERE, 'flow_img', 'sync_flow.dot'), '-o', IMG], check=True)
except (OSError, subprocess.CalledProcessError):
    pass                                         # keep the stored PNG
fp = wb.create_sheet('Flow Process', 1)
fp.sheet_view.showGridLines = False
fp['A1'] = 'Flow process: [Sync] AP POLE, Period Rollover dan GTOPAS'
fp['A1'].font = Font(name='Arial', size=12, bold=True)
fp['A2'] = 'Inti masalah: master GTOPAS (WVJA5204) tidak punya period, jadi data bulan depan baru boleh masuk GTOPAS saat Rollover tanggal 1.'
fp['A2'].font = Font(name='Arial', size=9, italic=True, color='B23B2E')
if os.path.exists(IMG):
    im = XLImage(IMG)
    im.width, im.height = int(im.width * 0.62), int(im.height * 0.62)
    fp.add_image(im, 'A4')
r = 26


def block_title(t):
    global r
    c = fp.cell(r, 1, t)
    c.font, c.fill = Font(name='Arial', size=10, bold=True, color='FFFFFF'), PatternFill('solid', fgColor='123A6B')
    for j in range(2, 8):
        fp.cell(r, j).fill = PatternFill('solid', fgColor='123A6B')
    r += 1


def grid(head, rows, hl=()):
    global r
    for j, h in enumerate(head, 1):
        c = fp.cell(r, j, h)
        c.font, c.fill, c.border = Font(name='Arial', size=9, bold=True), HDR, BOX
        c.alignment = Alignment(wrap_text=True, vertical='center')
    r += 1
    for i, row in enumerate(rows):
        for j, v in enumerate(row, 1):
            c = fp.cell(r, j, v)
            c.font, c.border = Font(name='Arial', size=9), BOX
            c.alignment = Alignment(wrap_text=True, vertical='top')
            if i in hl:
                c.fill = PatternFill('solid', fgColor='FFF1D6')
        r += 1
    r += 1


block_title('A. Alur per bulan (contoh: November 2026, Next = Desember 2026)')
grid(['No', 'Kapan', 'Trigger', 'Proses', 'Staging (TB_H_PART_CANDIDATE_STG_SYNC)', 'AP POLE (XD07)', 'GTOPAS (XD06)'], [
    [1, 'Sepanjang bulan', 'D/S / Procurement edit di screen atau upload', 'Ubah data period Current (202611)',
     'Insert baris PERIOD 202611. APPOLE 0. GTOPAS 0 kalau destinasi muncul / hilang, NULL kalau cuma angka', '-', '-'],
    [2, 'Kapan saja', 'User klik [Sync]', 'Kirim perubahan yang belum terkirim',
     'Ambil APPOLE 0 (CREATED_DT > LAST_SYNC_DATE_APPOLE, PERIOD Current/Next) dan GTOPAS 0 (PERIOD = Current). Isi status, SEND_SEQ, run ID',
     'Upload file 1 → 2 → 3 untuk Eff. 11/2026', 'Compare part 202611 yang punya baris GTOPAS 0'],
    [3, 'Hari D, 27-Nov 02:00', 'XD05 (batch)', 'Hitung DAD, buat period Next 202612',
     'Insert baris PERIOD 202612: KANBAN ADD (Pcs, Max) semua part, EXPORT ADD per destinasi (GTOPAS 0); part Inactive: EXPORT DELETE 0', 'Belum dikirim', 'Belum dikirim'],
    [4, '27-Nov s/d 30-Nov', 'User klik [Sync]', 'Kirim Current dan Next ke AP POLE',
     'Baris 202612 ikut APPOLE (status 1). GTOPAS baris 202612 TETAP 0 karena PERIOD bukan Current',
     'Upload Eff. 11/2026 dan Eff. 12/2026 (AP POLE punya Effective Month, jadi aman dikirim duluan)', 'Tidak kirim data 202612 (tunggu Rollover)'],
    [5, '01-Dec 00:10', 'XD05 Period Rollover (otomatis)', '202612 jadi Current, 202611 jadi Past',
     'Ambil GTOPAS 0 dengan PERIOD = 202612 (tanpa tanggal). Isi GTOPAS 1, GTOPAS_SYNC_DT, run ID', '-',
     'Compare semua part 202612: Add / Delete / Keep destinasi (CASE_DAY ≥ 1)'],
    [6, 'Setelah 01-Dec', '-', 'Baris 202611 yang masih status 0 (belum sempat di-[Sync])',
     'Dibiarkan, tidak diambil lagi karena semua query pakai syarat PERIOD', 'Tidak dikirim', 'Tidak dikirim (GTOPAS sudah disamakan dengan 202612 oleh Rollover)'],
], hl=(4,))

block_title('B. Kenapa GTOPAS harus lewat Rollover, sedangkan AP POLE tidak')
grid(['Hal', 'AP POLE', 'GTOPAS'], [
    ['Ada period di master?', 'Ada: Effective Month / Year di setiap baris (Kanban dan Export)', 'Tidak ada: hanya P/No. + Destination Code'],
    ['Data bulan depan bisa disimpan duluan?', 'Bisa, record Eff. 12/2026 terpisah dari Eff. 11/2026', 'Tidak bisa, satu record per part + destinasi berlaku untuk bulan berjalan'],
    ['Kapan data Next dikirim', 'Di [Sync] mana saja setelah hari D', 'Hanya saat Period Rollover tanggal 1'],
    ['Syarat ambil baris', 'APPOLE_SYNC_STATUS 0, CREATED_DT > LAST_SYNC_DATE_APPOLE dan ≤ waktu klik, PERIOD Current atau Next',
     'GTOPAS_SYNC_STATUS 0 dan PERIOD = Current ([Sync]) atau period baru (Rollover). Tanpa tanggal'],
    ['Kenapa tanpa tanggal untuk GTOPAS', '-', 'Kalau pakai tanggal, [Sync] Current di tgl 27 jam 10:00 bisa menggeser tanggal melewati baris Next dari XD05 (jam 02:00), lalu baris itu terlewat saat Rollover'],
    ['Yang dikirim bot', 'Hanya baris yang berubah (file 1 / 2 / 3)', 'Semua destinasi part yang berubah (nilai terakhir ≥ 1), lalu dibandingkan dengan layar GTOPAS'],
])

block_title('C. Contoh di simulasi ini')
grid(['Kapan', 'Kejadian', 'GTOPAS', 'Sheet'], [
    ['27-Nov 02:00', 'XD05 buat 202612 (HIST 101–115)', 'Baris EXPORT 202612 GTOPAS 0, menunggu', '1 XD05 P1, 2 XD05 P2'],
    ['27-Nov 10:00', '[Sync]: AP POLE 11/2026 dan 12/2026', 'Tidak jalan (tidak ada GTOPAS 0 di 202611)', '4 Sync, 5 RPA AP POLE'],
    ['01-Dec 00:10', 'Rollover 202612', 'Compare 4 part: TAIWAN Add, JAPAN/USA Add, KOREA DUMMY-003 Delete', '6 Rollover + GTOPAS'],
    ['15-Dec 10:00', '[Sync] Current 202612', 'Compare DUMMY-004: KOREA Add (destinasi baru bulan berjalan)', '9 Sync 15-Dec'],
    ['27-Dec 10:00', '[Sync]: AP POLE 01/2027', 'Tidak jalan; baris 202701 menunggu Rollover', '11 Sync 27-Dec'],
    ['01-Jan 00:10', 'Rollover 202701', 'Compare: DUMMY-004 KOREA Delete, lainnya Keep', '12 Rollover Jan'],
])
for col, w in zip('ABCDEFG', (16, 20, 26, 34, 52, 34, 34)):
    fp.column_dimensions[col].width = w

# ---- Legend sheet (bahasa Indonesia, ringkas) ----
LEG = [
    ('File upload ke AP POLE', None),
    ('File 1', 'File Export (LLM9Q880) yang di-upload SEBELUM file Kanban. Isinya destinasi dari part yang Max-nya turun, supaya total destinasi turun dulu sebelum Max diturunkan.'),
    ('File 2', 'File Kanban (LLM9Q910). Isinya perubahan induk: Shipping Box Qty (Pcs/Case) dan Max Shipping Box Qty (Max Case/Day), termasuk part baru (Add part). Pcs dan Max selalu satu baris.'),
    ('File 3', 'File Export (LLM9Q880) yang di-upload SESUDAH file Kanban. Isinya destinasi dari part lain: Max naik, part baru, atau cuma geser destinasi / hapus / Inactive.'),
    ('Nama file', '<template>_<run ID>_<period>_<nomor file>.xls, contoh LLM9Q880_20261127100000_202611_1.xls. Satu file per period + nomor file; kalau isinya kosong, file tidak dibuat.'),
    ('Urutan upload', 'Bot upload satu per satu sesuai nama file (Current dulu, baru Next). AP POLE cek per baris: total Max Shipping Box (RCS) semua Buyer-PD ≤ Max Shipping Box Qty part.'),
    ('Di dalam file Export', 'Per part, baris yang turun / dihapus duluan, baru yang naik / baru.'),
    ('Isi file AP POLE', None),
    ('LLM9Q910', 'Template upload Cross Dock Kanban Part Master (induk).'),
    ('LLM9Q880', 'Template upload Export Customer Cross Dock Master (destinasi / Buyer-PD).'),
    ('Operator ID P6', 'Nilai tetap di file Kanban.'),
    ('Transport Code 2', 'Nilai tetap di file Export.'),
    ('Part No.', 'Kanban pakai "-" (DUMMY-001), Export tanpa "-" (DUMMY001).'),
    ('Buyer-PD', 'Kode destinasi. Di simulasi pakai nama negara dummy (JAPAN, KOREA, ...).'),
    ('Max Shipping Box (RCS)', 'Case/Day per destinasi. Isi 0 = destinasi dihapus (Buyer-PD tetap ada di AP POLE dengan 0).'),
    ('Max Allowance Qty', 'Pcs/Case × Max Case/Day.'),
    ('Tabel staging TB_H_PART_CANDIDATE_STG_SYNC', None),
    ('HIST_ID', 'Nomor urut baris (urutan perubahan).'),
    ('PART_STATUS', 'Status part di period itu saat baris ditulis (Active / Inactive).'),
    ('LEVEL_TYPE', 'KANBAN = induk (Kanban Crossdock Master). EXPORT = destinasi (Export Crossdock Master).'),
    ('FIELD_NAME', 'Kolom yang berubah: PCS_CASE, MAX_CASE_DAY (KANBAN) atau CASE_DAY (EXPORT).'),
    ('ACTION', 'ADD = data baru, EDIT = nilai berubah, DELETE = destinasi dihapus (NEW_VALUE 0).'),
    ('OLD_VALUE / NEW_VALUE', 'Nilai sebelum / sesudah perubahan. OLD kosong kalau ADD.'),
    ('SOURCE', 'BATCH = XD05, SCREEN = edit di layar, UPLOAD = upload Excel.'),
    ('APPOLE_SYNC_STATUS', '0 Non Sync = belum dikirim. 1 Sync = sudah dikirim (baris terakhir per kunci). 2 Superseded = baris lama yang sudah ditimpa perubahan berikutnya, tidak dikirim.'),
    ('SEND_SEQ', 'Nomor file upload (1 / 2 / 3) untuk baris itu. Diisi NSP saat [Sync]. Kosong untuk Superseded atau nilai akhirnya sama dengan nilai awal.'),
    ('GTOPAS_SYNC_STATUS', 'NULL = tidak untuk GTOPAS (Pcs, Max, edit Case/Day). 0 = belum dikirim (destinasi muncul / hilang). 1 = sudah dikirim.'),
    ('Run ID (…_SYNC_RUN_ID)', 'ID satu kali kirim, format YYYYMMDDHHMMSS (contoh 20261127100000). Re-send pakai run ID terakhir.'),
    ('…_SYNC_DT', 'Waktu baris itu dikirim ke AP POLE / GTOPAS.'),
    ('CHANGED_BY / CHANGED_DT', 'Siapa dan kapan baris di-update oleh [Sync] / Rollover.'),
    ('Istilah proses', None),
    ('[Sync]', 'Tombol di layar. NSP update staging (status, SEND_SEQ, run ID), buat data file, lalu bot jalan.'),
    ('Kunci (key)', 'Part + period + LEVEL_TYPE + destinasi + order type + field. Satu kunci bisa punya beberapa baris kalau diubah berkali-kali.'),
    ('AP POLE value / NSP value', 'Kolom bantu simulasi (header kuning). AP POLE value = OLD baris pertama kunci (yang ada di AP POLE). NSP value = NEW baris terakhir. Tidak disimpan di tabel.'),
    ('Action (Down / Up / Add / Delete / skip)', 'Kolom bantu simulasi: arah perubahan dari AP POLE value ke NSP value. skip = nilainya sama, tidak dikirim.'),
    ('LAST_SYNC_DATE_APPOLE', 'Parameter System Master: waktu [Sync] AP POLE terakhir. [Sync] ambil baris dengan CREATED_DT > tanggal ini dan ≤ waktu klik.'),
    ('Current / Next / Past', 'Current = period bulan berjalan. Next = bulan depan (dibuat XD05 di hari D). Past = sudah lewat, cuma bisa dilihat.'),
    ('Hari D', 'Tanggal XD05 jalan (contoh 27). XD05 hitung DAD dan bikin data period Next.'),
    ('Period Rollover', 'Tanggal 1 jam 00:10: Next jadi Current, lalu XD06 (GTOPAS) jalan untuk period baru.'),
    ('XD05 / XD06 / XD07', 'XD05 = batch hitung DAD + Rollover. XD06 = RPA GTOPAS. XD07 = RPA AP POLE.'),
    ('GTOPAS compare', 'Bot bandingkan destinasi NSP (Case/Day ≥ 1) dengan layar GTOPAS: Add = ada di NSP saja, Delete = ada di GTOPAS saja, Keep = ada di dua-duanya.'),
    ('Warna', None),
    ('Kuning', 'Baris baru / berubah / Non Sync. Header kuning = kolom bantu simulasi.'),
    ('Hijau', 'Sync / Keep / OK.'),
    ('Merah', 'Delete / nilai 0 / NG.'),
    ('Ungu', 'Baris induk (Kanban).'),
    ('Abu dicoret', 'Superseded (baris lama yang tidak dikirim).'),
]
lg = wb.create_sheet('Legend', 2)
lg.sheet_view.showGridLines = False
lg['A1'] = 'Legend: istilah di simulasi'
lg['A1'].font = Font(name='Arial', size=12, bold=True)
r = 3
COL = {'Kuning': 'FFF1D6', 'Hijau': 'E1F2E5', 'Merah': 'FBE3DF', 'Ungu': 'EEE8F7', 'Abu dicoret': 'F2F2F2'}
for k, v in LEG:
    if v is None:
        r += 1 if r > 3 else 0
        c = lg.cell(r, 1, k)
        c.font, c.fill = Font(name='Arial', size=10, bold=True, color='FFFFFF'), PatternFill('solid', fgColor='123A6B')
        lg.cell(r, 2).fill = PatternFill('solid', fgColor='123A6B')
    else:
        a_, b_ = lg.cell(r, 1, k), lg.cell(r, 2, v)
        a_.font, b_.font = Font(name='Arial', size=9, bold=True), Font(name='Arial', size=9)
        a_.border = b_.border = BOX
        a_.alignment = Alignment(vertical='top', wrap_text=True)
        b_.alignment = Alignment(vertical='top', wrap_text=True)
        if k in COL:
            a_.fill = PatternFill('solid', fgColor=COL[k])
    r += 1
lg.column_dimensions['A'].width = 34
lg.column_dimensions['B'].width = 110
wb.save(OUT)
print('saved', OUT, len(steps), 'steps')
