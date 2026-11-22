"""22-Nov: Function_Summary.html follows the sync with TB_H_PART_CANDIDATE_STG_SYNC (XD01-XD03, XD05-XD07) and the messages of the specs.
Run: python3 update_fs_2211.py (from this folder)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'Function_Summary.html')
SPECS = os.path.join(HERE, '..', 'specs')
s = open(P, encoding='utf-8').read()


def js(t):
    return "'" + t.replace('\\', '\\\\').replace("'", "\\'") + "'"


def line(prefix, new):
    """Replace the whole point line that starts with prefix (after the indent)."""
    global s
    i = s.index("'" + prefix)
    a = s.rindex('\n', 0, i) + 1
    b = s.index('\n', i)
    old = s[a:b]
    s = s[:a] + old[:old.index("'")] + js(new) + old[old.rindex("'") + 1:] + s[b:]


def block(start, end, new):
    """Replace the text between two markers (start kept, end kept)."""
    global s
    i = s.index(start)
    j = s.index(end, i)
    s = s[:i] + new + s[j:]


# ---------- XD01 ----------
line('DAD Calculation (XD05 proses 1)', 'DAD Calculation (XD05 proses 1): scheduler bulanan, auto retry 3×; [Run calculation] aktif hanya setelah gagal 3× (badge "Scheduled run failed 3x"). XD05 menulis baris staging untuk period baru.')
line('Aturan Sync Status (17-Nov)', 'Sync (22-Nov): setiap perubahan nilai menulis 1 baris di TB_H_PART_CANDIDATE_STG_SYNC (KANBAN: Pcs/Case, Max Case/Day; EXPORT: Case/Day per destinasi ADD / EDIT / DELETE). Min MAD, Effective Start Date, Candidate ↔ Inactive dan Save tanpa perubahan tidak menulis baris. TB_M_PART_CANDIDATE tidak punya kolom sync lagi.')
line('Status diubah manual Active → Inactive', 'Procurement ubah Active → Inactive: semua destinasi part ditulis EXPORT DELETE (nilai 0), part tetap ada di Kanban AP POLE. Inactive → Active: Procurement mapping ulang destinasinya di layar (EXPORT ADD).')
line('Buka menu: hanya akun D/S.', 'Buka menu: hanya akun D/S. Default periode ongoing, Sync Status Non Sync. Periode ongoing: semua part Active dengan destinasinya (tanpa destinasi: 0 / quota). Periode baru mulai kosong; periode lalu hanya bisa dilihat.')
line('[Sync (n)]:', '[Sync (n)]: part + period yang punya baris staging Non Sync (AP POLE: Current dan Next; GTOPAS: Current), tanpa melihat filter. Satu transaksi: ringkas per kunci (OLD pertama, NEW terakhir), baris terakhir 1 Sync + SEND_SEQ, baris sebelumnya 2 Superseded, run ID, LAST_SYNC_DATE_APPOLE; lalu XD07 dan XD06 jalan (msg 27).')
line('Tanpa response dari RPA (20-Nov)', 'Sync Status di layar dihitung dari staging per part + period: AP POLE dan GTOPAS Non Sync / Sync, Last Sent AP POLE / GTOPAS = waktu kirim terakhir. Hasil RPA datang lewat email; kalau FAILED klik [Re-send last Sync] (run ID terakhir dikirim ulang).')
# ---------- XD02 / XD03 ----------
line('Part baru No Sync;', 'Tiap nilai yang berubah dari part Active menulis baris staging (KANBAN, source UPLOAD, UPLOAD_ID); part baru (Candidate) tidak; Active → Inactive menulis EXPORT DELETE (0) per destinasi; history per field (ADD / EDIT, source UPLOAD); part yang tidak ada di file tidak berubah.')
line('Part yang destinasi / Case/Day-nya berubah jadi No Sync', 'Tiap destinasi yang ditambah / diubah / dihapus menulis baris staging (EXPORT ADD / EDIT / DELETE, GTOPAS 0 untuk ADD / DELETE); baris yang sama dengan mapping sekarang tidak menulis apa pun; history per destinasi (MAPPING, source UPLOAD). Result report dan upload log seperti XD02.')
# ---------- XD05 ----------
i = s.index("'Jadwal baru (19-Nov)")
line('Jadwal baru (19-Nov)', 'Jadwal (19-Nov): jalan di tanggal D (system master) dan membuat period berikutnya (Next) untuk Kanban dan Export Crossdock Master; Current tidak berubah. Proses 3 tanggal 1 jam 00:10: Period Rollover (Next jadi Current), baris staging period baru dengan GTOPAS 0 (tanpa tanggal) dikirim, lalu XD06 jalan otomatis.')
line('Simpan hasil di TB_R_PART_DAD_RESULT', 'Simpan hasil di TB_R_PART_DAD_RESULT; kalau status berubah, update Kanban Crossdock Master dan history (CALC). Staging: KANBAN ADD Pcs/Case dan Max Case/Day untuk semua part period baru (termasuk Inactive, part tetap di Kanban AP POLE).')
line('Simpan periode baru (re-run', 'Simpan periode baru (re-run menghapus data periode itu dulu). Staging: EXPORT ADD per destinasi part Active (GTOPAS 0); part Inactive: EXPORT DELETE (0) untuk destinasi yang bulan lalu masih > 0. History per destinasi (MAPPING, BATCH).')
# ---------- XD06 ----------
block("{ id: 'XD06', name: 'IF Cross Dock Master to GTOPAS', type: 'Batch (RPA)', trigger: ",
      "\n\n  { id: 'XD07'",
      "{ id: 'XD06', name: 'IF Cross Dock Master to GTOPAS', type: 'Batch (RPA)', trigger: '[Sync] di XD01 (period Current) dan Period Rollover tanggal 1 (period baru); bot baca staging (22-Nov)',\n"
      "    sections: [\n"
      "      { key: 'N', title: 'Proses normal', points: [\n"
      + ',\n'.join('        ' + js(x) for x in [
          'Sumber: hanya TB_H_PART_CANDIDATE_STG_SYNC (user DB read-only), part dari run ID. Bot tidak download Excel NSP lagi.',
          'Baris yang diambil: GTOPAS_SYNC_STATUS 0 + PERIOD, tanpa tanggal. [Sync] = period Current; Period Rollover = period yang baru jadi Current. Data Next tidak dikirim di tanggal D karena GTOPAS WVJA5204 tidak punya period (isinya selalu bulan berjalan).',
          'GTOPAS 0 hanya untuk baris EXPORT ADD / DELETE (destinasi muncul / hilang). Baris KANBAN dan EDIT Case/Day = NULL (GTOPAS tidak simpan quantity).',
          'Destinasi NSP per part: nilai staging terakhir per destinasi + order type ≥ 1; order type digabung jadi 1 baris GTOPAS.',
          'Bot buka WVJA5204 (Depot 01), baca baris part tersebut, bandingkan per P/No. (tanpa "-") + Destination Code: hanya di NSP → Add (Maker A, Dom/Os 2, TOPAS Order Type *, Trans 2); hanya di GTOPAS → Delete; ada di keduanya → Keep.',
          'Email notifikasi (Power Automate): 1 email per run, SUCCESS / FAILED. Bot tidak menulis balik ke NSP.']) + " ] },\n"
      "      { key: 'AB', title: 'Abnormality', points: [\n"
      "        { k: 'Error apa pun di bot (login, layar, timeout, pesan error GTOPAS)', d: 'LOG4', s: 'Try-catch: bot berhenti, email FAILED; baris yang sudah diproses tetap di GTOPAS', u: '[Re-send last Sync]; run berikutnya membandingkan ulang' },\n"
      "        { k: 'Error sistem lain', d: 'LOG5', s: 'Stop, ERROR, email FAILED', u: 'Hubungi PIC' } ] },\n"
      "      { key: 'C', title: 'Catatan terbuka', points: [\n"
      "        'FB-176: hanya part di run yang dibandingkan (21-Nov).' ] } ] },")
# ---------- XD07 ----------
block("{ id: 'XD07', name: 'RPA Cross Dock Master to AP POLE', type: 'Batch (RPA)', trigger: ",
      "\n\n  { id: 'XD08'",
      "{ id: 'XD07', name: 'RPA Cross Dock Master to AP POLE', type: 'Batch (RPA)', trigger: '[Sync] / [Re-send last Sync] di XD01: bot baca staging dan upload file LLM9Q880 / LLM9Q910 (22-Nov)',\n"
      "    sections: [\n"
      "      { key: 'N', title: 'Proses normal', points: [\n"
      + ',\n'.join('        ' + js(x) for x in [
          'Sumber: hanya TB_H_PART_CANDIDATE_STG_SYNC (user DB read-only), baris dengan APPOLE_SYNC_RUN_ID = run ID dan SEND_SEQ terisi. NSP sudah meringkas baris dan mengisi SEND_SEQ saat [Sync].',
          'Upload file dari template tersimpan (tidak download dari AP POLE): file 1 = Export (LLM9Q880) hanya untuk part yang Max-nya turun; file 2 = Kanban (LLM9Q910) semua perubahan induk dan part baru (Pcs dan Max 1 baris); file 3 = Export untuk part lainnya.',
          'Nama file <template>_<run ID>_<period>_<SEND_SEQ>.xls, 1 file per period + SEND_SEQ, Current dulu baru Next. File tanpa baris tidak dibuat. Bot upload satu per satu dan menunggu hasil tiap file.',
          'AP POLE cek per baris: total Max Shipping Box (RCS) ≤ Max Shipping Box Qty. Di dalam file Export, per part baris yang turun / dihapus dulu, baru yang naik / baru.',
          'Isi file: Operator ID P6, Transport Code 2, Part No. Kanban pakai "-", Export tanpa "-", Buyer-PD 5-2, hapus = 0 (Buyer-PD tetap ada dengan 0). Pasangan Pcs + Max diambil dari baris Sync terakhir tiap field.',
          'Email notifikasi (Power Automate): SUCCESS / FAILED per run. Bot tidak menulis balik ke NSP; kalau FAILED, D/S klik [Re-send last Sync].']) + " ] },\n"
      "      { key: 'AB', title: 'Abnormality', points: [\n"
      "        { k: 'Login / upload AP POLE gagal, timeout, error AP POLE di satu baris', d: 'LOG4', s: 'Bot berhenti di file itu, email FAILED; file sebelumnya tetap di AP POLE', u: '[Re-send last Sync]; hubungi PIC' },\n"
      "        { k: 'Error sistem lain', d: 'LOG5', s: 'Stop, ERROR', u: 'Hubungi PIC' } ] },\n"
      "      { key: 'C', title: 'Catatan terbuka', points: [ 'Langkah upload di layar AP POLE (Common File Upload) TBC dengan tim AP POLE.' ] } ] },")

for a_, b_ in (("Setelah Save: Sync Status No Sync, history ADD, part paling atas, msg 9.", "Setelah Save: history ADD, part paling atas, msg 9 (part Candidate belum dikirim, tidak ada baris staging)."),
               ("Setelah Save: No Sync, history per field, msg 9.", "Setelah Save: baris staging per nilai yang berubah (Non Sync), history per field, msg 9."),
               ("history per destinasi; part No Sync.", "history per destinasi; baris staging per destinasi yang berubah (Non Sync).")):
    s = s.replace(a_, b_)

# ---------- messages from the specs ----------
a = s.index('const MSGS = ')
b = s.index('};\n', a)
msgs = json.loads(s[a + len('const MSGS = '):b + 1])


def act(x):
    if isinstance(x, dict):
        t = 'system: ' + x.get('system', '-')
        if x.get('user') and x['user'] != '-':
            t += '; user: ' + x['user']
        return t
    return x


for fid in ('XD01', 'XD02', 'XD03', 'XD05', 'XD06', 'XD07'):
    sp = json.load(open(os.path.join(SPECS, f'{fid}_spec.json'), encoding='utf-8'))
    out = []
    for kind, lst in (('Display', sp.get('display_messages', [])), ('Log', sp.get('logging_messages', []))):
        for m in lst:
            if not m.get('msg_id') or m['msg_id'] == '-' or 'message' not in m:
                continue
            out.append({'id': m['msg_id'], 'kind': kind, 'type': m.get('type', ''), 'event': m.get('event', ''), 'cause': m.get('cause', ''),
                        'message': m['message'], 'action': act(m.get('action', ''))})
    msgs[fid] = out
s = s[:a] + 'const MSGS = ' + json.dumps(msgs, indent=0, ensure_ascii=False) + s[b + 1:]
open(P, 'w', encoding='utf-8').write(s)
print('updated')
