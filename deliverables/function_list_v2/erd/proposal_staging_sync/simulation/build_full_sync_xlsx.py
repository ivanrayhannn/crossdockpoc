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
lg = wb.create_sheet('Legend', 1)
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
