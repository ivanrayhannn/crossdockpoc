"""23-Nov: Function_Summary.html follows staging per target (TB_H_STG_APPOLE_KANBAN / _EXPORT / TB_H_STG_GTOPAS), Period instead of
Effective Start Date, the RPA parent flow, and the messages of the specs. Run: python3 update_fs_2311.py (from this folder)."""
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
line('Add part baru: status otomatis Candidate', 'Add part baru: status otomatis Candidate (terkunci). Input Part No (dari Part Master, belum terdaftar), Part Name otomatis, Period (default bulan berjalan, atau Next), Min MAD (≥ 0), Pcs/Case (> 0), Max Case/Day (> 0). Part berlaku mulai period itu. Pilih bulan berjalan setelah tanggal D: baris Next juga dibuat, supaya ikut kalkulasi berikutnya. [Save] aktif kalau isian wajib lengkap (tooltip msg 5 / 15 / 6 / 7). Setelah Save: history ADD, part paling atas, msg 9 (part Candidate belum dikirim, tidak ada baris staging).')
line('Edit part (Candidate / Active / Inactive)', 'Edit part: Part No dan Period terkunci (tooltip msg 10). Status: part Candidate bisa tetap Candidate atau jadi Active; part Active / Inactive bisa Active atau Inactive; tidak ada yang balik ke Candidate. Part Next hanya bisa dilihat sampai period-nya jadi bulan berjalan. Part Active menampilkan "Mapped Case/Day (current period)"; Max Case/Day tidak boleh di bawahnya (msg 14). Setelah Save: baris staging per nilai yang berubah (Non Sync), history per field, msg 9.')
line('Sync (22-Nov)', 'Staging per target: TB_H_STG_APPOLE_KANBAN (format LLM9Q910), TB_H_STG_APPOLE_EXPORT (LLM9Q880), TB_H_STG_GTOPAS (WVJA5204). Setiap Save memanggil SP_STG_WRITE: Kanban baris nilai baru + OPERATION_TYPE (1 Max turun, 2 naik, 3 sama, 4 belum pernah dikirim, 5 header kalau hanya destinasi yang berubah); Export ADD / EDIT / DELETE (0); GTOPAS hanya kalau destinasi muncul / hilang. Baris lama yang belum dikirim jadi 2 Superseded. Min MAD, part Candidate dan Save tanpa perubahan tidak menulis baris.')
line('Procurement ubah Active → Inactive', 'Procurement ubah Active → Inactive: mapping period dihapus, tiap destinasi ditulis Export DELETE (0) + GTOPAS DELETE, Kanban header 5; part tetap ada di Kanban AP POLE. Inactive → Active: Procurement mapping ulang destinasinya (Export ADD, GTOPAS ADD).')
line('[Sync (n)]:', '[Sync (n)]: part + period yang punya baris SYNC_STATUS 0 (AP POLE: Current dan Next; GTOPAS: Current), tanpa melihat filter. SP_STG_SYNC hanya mengubah 0 → 1 + SYNC_DT + run ID dan LAST_SYNC_DATE_APPOLE (aturan sudah ditulis saat Save), lalu parent flow RPA jalan (msg 27).')
line('Sync Status di layar dihitung dari staging', 'Sync Status di layar per part + period: AP POLE Non Sync kalau staging Kanban / Export masih punya baris 0; GTOPAS Non Sync kalau staging GTOPAS masih punya baris 0. Last Sent = SYNC_DT terakhir. Hasil RPA datang lewat email; kalau FAILED klik [Re-send last Sync] (run ID yang sama dikirim ulang).')
# ---------- XD02 / XD03 ----------
line('Cek file: .xlsx, maksimal 5 MB', 'Cek file: .xlsx, maksimal 5 MB, 1–5.000 baris, sheet "Upload" ada (sheet lain diabaikan), 7 kolom template dengan nama sama seperti sheet export, dibaca berdasarkan nama kolom: Part Number, Min MAD, Pcs/Case, Max Case/Day, Status, Upload (A/E), Period.')
line('Tiap nilai yang berubah dari part Active', 'Tiap nilai yang berubah dari part Active lewat SP_STG_WRITE (source UPLOAD, UPLOAD_ID): Kanban EDIT dengan OPERATION_TYPE; part baru (Candidate) tidak; Active → Inactive: mapping period dihapus, Export DELETE (0) per destinasi, GTOPAS DELETE, Kanban header 5. History per field (ADD / EDIT, source UPLOAD); part yang tidak ada di file tidak berubah.')
line('Effective Start Date wajib untuk part Candidate', 'A: Period wajib, bulan berjalan atau Next (YYYYMM); part berlaku mulai period itu.')
line('E: Effective Start Date hanya boleh berubah', 'E: Period = bulan berjalan. Part yang didaftarkan untuk Next belum bisa diubah sampai period-nya jadi bulan berjalan.')
line('Tiap destinasi yang ditambah / diubah / dihapus', 'Tiap destinasi yang ditambah / diubah / dihapus lewat SP_STG_WRITE: Export ADD / EDIT / DELETE (0), GTOPAS kalau destinasi muncul / hilang untuk part itu, Kanban header 5 kalau Kanban tidak berubah. Baris yang sama dengan mapping sekarang tidak menulis apa pun; history per destinasi (MAPPING, source UPLOAD). Result report dan upload log seperti XD02.')
# ---------- XD05 ----------
line('Semua part (Candidate, Active, Inactive); part dengan Effective Start Date', 'Semua part yang punya baris di period Current (Candidate, Active, Inactive). Part yang didaftarkan untuk Next sebelum tanggal D sudah punya baris Next: ikut dihitung, tidak dibuat dua kali.')
line('Jadwal (19-Nov)', 'Jadwal: jalan di tanggal D (system master) dan membuat period berikutnya (Next) untuk Kanban dan Export Crossdock Master; Current tidak berubah. Proses 3 tanggal 1 jam 00:10: Period Rollover (Next jadi Current), baris staging GTOPAS period baru 0 → 1 dengan run ID, lalu parent flow RPA jalan dengan XD06 saja.')
line('Simpan hasil di TB_R_PART_DAD_RESULT', 'Simpan hasil di TB_R_PART_DAD_RESULT; kalau status berubah, update Kanban Crossdock Master dan history (CALC). Staging lewat SP_STG_WRITE: Kanban ADD untuk semua part period baru (termasuk Inactive, part tetap di Kanban AP POLE), OPERATION_TYPE dibanding Max yang dikirim untuk period sebelumnya.')
line('Simpan periode baru (re-run', 'Simpan periode baru (re-run menghapus data periode itu dulu). Staging: Export ADD per destinasi part Active; DELETE (0) untuk destinasi period lalu yang tidak di-mapping lagi dan untuk destinasi part Inactive yang masih > 0; GTOPAS hanya untuk destinasi yang muncul / hilang. History per destinasi (MAPPING, BATCH).')
PARENT = ['Satu parent flow Power Automate per run (CDX_SYNC_PARENT), dijalankan NSP dengan RUN_ID dan RUN_TYPE (SYNC, RESEND, ROLLOVER).',
          'Skenario 1, run punya baris GTOPAS (part jadi Active / Inactive, destinasi ditambah / dihapus): XD06 GTOPAS dulu; XD07 AP POLE jalan hanya kalau GTOPAS berhasil. GTOPAS gagal → AP POLE tidak jalan.',
          'Skenario 2, run tanpa baris GTOPAS (Max Case/Day, Pcs/Case, Case/Day, order type destinasi yang tetap): langsung XD07.',
          'Period Rollover: XD06 saja untuk baris GTOPAS period yang baru jadi Current.']
block("{ id: 'XD06', name: 'IF Cross Dock Master to GTOPAS', type: 'Batch (RPA)', trigger: ",
      "\n\n  { id: 'XD07'",
      "{ id: 'XD06', name: 'IF Cross Dock Master to GTOPAS', type: 'Batch (RPA)', trigger: 'Parent flow RPA: [Sync] / [Re-send last Sync] skenario 1, atau Period Rollover tanggal 1',\n"
      "    sections: [\n"
      "      { key: 'N', title: 'Proses normal', points: [\n"
      + ',\n'.join('        ' + js(x) for x in PARENT + [
          'Sumber: hanya TB_H_STG_GTOPAS (user DB read-only), baris dengan SYNC_RUN_ID = run ID: ACTION ADD / DELETE per part + destinasi. Bot tidak membandingkan lagi; NSP sudah menentukan saat Save.',
          'GTOPAS tidak punya period (selalu bulan berjalan): [Sync] mengirim period Current, Next dikirim saat Period Rollover.',
          'Bot buka WVJA5204 (Depot 01): ADD = daftar baris (Maker A, Dom/Os 2, TOPAS Order Type 3, Trans 2); DELETE = MT DEL. Baris yang sudah ada (ADD) atau sudah hilang (DELETE) dihitung OK, jadi kirim ulang aman.',
          'Email notifikasi dikirim parent flow: 1 email per run berisi hasil GTOPAS dan AP POLE. Bot tidak menulis balik ke NSP.']) + " ] },\n"
      "      { key: 'AB', title: 'Abnormality', points: [\n"
      "        { k: 'Satu baris gagal (pesan error GTOPAS)', d: 'LOG4', s: 'Baris dicatat, baris berikutnya tetap diproses; hasil FAILED, XD07 tidak jalan (skenario 1)', u: '[Re-send last Sync]: GTOPAS lagi, lalu AP POLE' },\n"
      "        { k: 'Login / layar / timeout', d: 'LOG4', s: 'Bot berhenti, FAILED, XD07 tidak jalan', u: '[Re-send last Sync]' },\n"
      "        { k: 'Error sistem lain', d: 'LOG5', s: 'Stop, ERROR, email FAILED', u: 'Hubungi PIC' } ] },\n"
      "      { key: 'C', title: 'Catatan terbuka', points: [\n"
      "        'Cara NSP menjalankan parent flow (HTTP trigger) TBC dengan tim RPA.' ] } ] },")
block("{ id: 'XD07', name: 'RPA Cross Dock Master to AP POLE', type: 'Batch (RPA)', trigger: ",
      "\n\n  { id: 'XD08'",
      "{ id: 'XD07', name: 'RPA Cross Dock Master to AP POLE', type: 'Batch (RPA)', trigger: 'Parent flow RPA: skenario 1 setelah GTOPAS OK, atau skenario 2 langsung',\n"
      "    sections: [\n"
      "      { key: 'N', title: 'Proses normal', points: [\n"
      + ',\n'.join('        ' + js(x) for x in PARENT[:3] + [
          'Sumber: view V_APPOLE_UPLOAD_KANBAN dan V_APPOLE_UPLOAD_EXPORT (user DB read-only) untuk run ID. View hanya membaca aturan yang ditulis saat Save.',
          'Urutan file: EXPORT_PRE (LLM9Q880, Export part yang Kanban-nya OPERATION_TYPE 1) → KANBAN (LLM9Q910, OPERATION_TYPE 1–4) → EXPORT_POST (Export lainnya). Header 5 tidak di-upload. File tanpa baris tidak dibuat.',
          'Nama file <template>_<run ID>_<urutan>_<nama>.xls, Current dan Next dalam satu file (Effective Month / Year per baris). Bot upload satu per satu dan menunggu hasil tiap file.',
          'AP POLE cek per baris: total Max Shipping Box (RCS) ≤ Max Shipping Box Qty. Di dalam file Export, per part baris turun / hapus dulu (ROW_ORDER 1), baru naik / baru (ROW_ORDER 2).',
          'Isi file: Operator ID P6, Transport Code 2, Part No. Kanban pakai "-", Export tanpa "-", Buyer-PD 5-2, hapus = 0.',
          'Email notifikasi dari parent flow: SUCCESS / FAILED per run. Bot tidak menulis balik ke NSP; kalau FAILED, D/S klik [Re-send last Sync].']) + " ] },\n"
      "      { key: 'AB', title: 'Abnormality', points: [\n"
      "        { k: 'AP POLE menolak file / login atau upload gagal / timeout', d: 'LOG4', s: 'Bot berhenti di file itu, FAILED; file sebelumnya tetap di AP POLE', u: '[Re-send last Sync]: run ID dan file yang sama' },\n"
      "        { k: 'Error sistem lain', d: 'LOG5', s: 'Stop, ERROR', u: 'Hubungi PIC' } ] },\n"
      "      { key: 'C', title: 'Catatan terbuka', points: [ 'Langkah upload di layar AP POLE (Common File Upload) TBC dengan tim AP POLE.' ] } ] },")

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
