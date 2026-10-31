import { useEffect, useMemo, useState } from 'react';
import { card } from '../asnCrossdock/styles';

/* Confirmation points of the Crossdock function list v2 (XD01-XD15). The user answers each point and submits:
 * the answers are shown as a summary that can be copied or downloaded (Markdown / JSON) and sent back. */

const FN: Record<string, string> = {
  XD01: 'Cross Dock Part Master Screen',
  XD02: 'Cross Dock Part Master Upload Batch',
  XD03: 'Part and Destination Mapping Upload Batch',
  XD04: 'Actual Demand Summary Synch to NSP',
  XD05: 'DAD Volume Calculation Batch',
  XD06: 'IF Cross Dock Master to G-System',
  XD07: 'IF Cross Dock Master to AP POLE',
  XD08: 'Order Control Information to NSP Batch (H0253, merged with XD12 on 23-Oct)',
  XD09: 'Mapping Customer Order and PO Batch',
  XD10: 'ASN Cross Dock Creation Screen',
  XD11: 'Change Order Number Screen (D/S, was Cancel Crossdock Customer Order Batch until 23-Oct)',
  XD12: 'Order Control Information to NSP Batch (Cancel) — merged into XD08 (23-Oct)',
  XD13: 'Destination Master Synch into NSP',
  XD14: 'DAD Volume Calculation Result Screen (Buffer)',
  XD15: 'ASN Crossdock Inquiry Screen (Buffer)',
};

type Group = 'A' | 'B' | 'C';
interface Item { id: string; group: Group; fns: string[]; topic: string; question: string; proposal: string }

const GROUPS: Record<Group, { title: string; hint: string }> = {
  A: { title: 'A. Tinggi', hint: 'Menentukan isi UISS ASN, cancel dan interface' },
  B: { title: 'B. Sedang', hint: 'Jadwal dan data' },
  C: { title: 'C. Rendah', hint: 'Usulan bisa langsung dipakai' },
};

const ITEMS: Item[] = [
  { id: 'A1', group: 'A', fns: ['XD10'], topic: 'Pemecahan case', question: 'Kalau qty per destinasi lebih besar dari pcs/case (mis. 24 pcs, 6 pcs/case), apakah dipecah jadi beberapa case? Rule sekarang "1 case per destinasi".', proposal: 'Ya, per destinasi dipecah sesuai pcs/case (24 pcs = 4 case)' },
  { id: 'A2', group: 'A', fns: ['XD10', 'XD11'], topic: 'Pengiriman bertahap', question: 'Apakah 1 customer order line boleh dikirim bertahap (sebagian di ASN ini, sisanya di ASN berikutnya)? Saat ini satu unit selalu utuh di 1 ASN.', proposal: 'Tidak, tetap utuh per unit' },
  { id: 'A3', group: 'A', fns: ['XD10', 'XD15'], topic: 'Isi case label', question: 'Apakah case label memuat Customer Order No dan/atau destinasi? Menentukan perlu relabel atau tidak saat CONFLICT.', proposal: 'Dicek di label existing' },
  { id: 'A4', group: 'A', fns: ['XD11'], topic: 'Penanganan barang CONFLICT', question: 'Barang yang sudah dikirim tapi order-nya di-cancel: dialokasikan manual ke order terbuka dengan destinasi sama, kalau tidak ada masuk stok gudang?', proposal: 'Setuju' },
  { id: 'A5', group: 'A', fns: ['XD11'], topic: 'Blok PO qty saat CONFLICT', question: 'Apakah PO qty yang dilepas perlu diblok sampai tim D/S menutup conflict? Kalau ya, perlu fungsi "close conflict".', proposal: 'Tidak perlu diblok (abnormality, dimonitor lewat log)' },
  { id: 'A6', group: 'A', fns: ['XD11'], topic: 'Exception list', question: 'Hasil CONFLICT cukup dilihat di Log Monitoring, atau perlu layar sendiri?', proposal: 'Cukup Log Monitoring dulu' },
  { id: 'A7', group: 'A', fns: ['XD05', 'XD06', 'XD07'], topic: 'Part yang jadi Inactive', question: 'Part yang berubah jadi Inactive (oleh DAD Volume Calculation) sekarang tidak pernah dikirim. Perlu dikirim dengan CROSSDOCK_FLAG = N supaya G-System / AP POLE berhenti memprosesnya sebagai crossdock?', proposal: 'Diputuskan 30-Oct: dihapus di G-System (RPA, semua row part + destinasi) dan di AP POLE (file SFTP, CROSSDOCK_FLAG N, 1 row per part)' },
  { id: 'A8', group: 'A', fns: ['XD06'], topic: 'Metode ke G-System', question: 'Bagaimana cross dock master dikirim ke G-System?', proposal: 'Diputuskan 30-Oct: RPA di menu Supply > Master > Crossdock Master (search Part No); hanya daftar destinasi, tanpa Case/Day' },
  { id: 'A9', group: 'A', fns: ['XD07'], topic: 'Tabel tujuan AP POLE', question: 'Field mana yang masuk ke Crossdock Kanban Part Master dan mana ke Crossdock Export Part Master?', proposal: 'Konfirmasi ke TMA' },
  { id: 'A10', group: 'A', fns: ['XD07'], topic: 'Detail SFTP', question: 'Server, folder, user, siapa yang meneruskan file dari SFTP TMMIN ke SFTP TMA, dan apakah ada file hasil / acknowledge balik?', proposal: 'Konfirmasi ke tim IT dan TMA' },
  { id: 'A11', group: 'A', fns: ['XD06', 'XD07'], topic: 'Format file interface', question: 'CSV atau fixed length? Nama file? Part tanpa destinasi dikirim atau tidak?', proposal: 'CSV, XD_CDMASTER_<target>_<timestamp>.csv (G-System: input RPA). Part Active tanpa destinasi: semua destinasinya di G-System dihapus (diputuskan 30-Oct)' },
  { id: 'B1', group: 'B', fns: ['XD12', 'XD11', 'XD08', 'XD13'], topic: 'Jadwal job harian', question: 'Jadwal job chain (Cancel → Cancel Crossdock Customer Order → ASN) dan Destination Master Synch. Perlu auto retry?', proposal: 'Setelah data G-System tersedia (27:30); retry 3x' },
  { id: 'B2', group: 'B', fns: ['XD04', 'XD05'], topic: 'Jadwal bulanan', question: 'Tanggal / jam Actual Demand Summary Synch dan DAD Volume Calculation.', proposal: 'Tanggal 1 jam 01:00, lalu DAD Volume Calculation' },
  { id: 'B3', group: 'B', fns: ['XD04', 'XD05'], topic: 'Dependensi batch', question: 'Kalau Actual Demand Summary Synch gagal, apakah DAD Volume Calculation dibatalkan?', proposal: 'Ya' },
  { id: 'B4', group: 'B', fns: ['XD08', 'XD12'], topic: 'Kolom SERIAL_NO', question: 'SERIAL_NO belum ada di export tabel H0253 (file skenario juga tanpa SERIAL_NO). Apakah tim DB Surrounding menambahkannya? Tanpa kolom ini partial cancel tidak bisa dibedakan.', proposal: 'Ya, tim surrounding menambah kolom' },
  { id: 'B5', group: 'B', fns: [], topic: 'Fungsi lama yang tidak dibawa', question: 'H0202 Demand History Sync dan Menu Settings memang tidak dipakai lagi?', proposal: 'Ya, tidak dipakai' },
  { id: 'B6', group: 'B', fns: ['XD14'], topic: 'Isi layar hasil DAD', question: 'Isi layar DAD Volume Calculation Result (buffer).', proposal: 'Daftar hasil per periode: Avg MAD vs Min MAD, status lama → baru' },
  { id: 'C1', group: 'C', fns: ['XD04'], topic: 'Kolom DAD', question: 'Kolom DAD di Actual Demand Summary dipakai?', proposal: 'Tidak, hanya MAD' },
  { id: 'C2', group: 'C', fns: ['XD05'], topic: 'Order type N + S', question: 'ORDER_TYPE_GROUP N dan S dijumlahkan, final?', proposal: 'Tetap dijumlahkan' },
  { id: 'C3', group: 'C', fns: ['XD01', 'XD02', 'XD03'], topic: 'Retensi history', question: 'Retensi history part (TB_H_PART_CANDIDATE).', proposal: '24 bulan' },
  { id: 'C4', group: 'C', fns: ['XD01', 'XD02', 'XD03'], topic: 'Panjang kolom', question: 'Panjang VARCHAR dan nama field Part Name.', proposal: 'Ikuti TB_M_PART_MASTER' },
  { id: 'C5', group: 'C', fns: ['XD02', 'XD03'], topic: 'Template & log upload', question: 'Lokasi template / result report dan retensi log upload.', proposal: 'Shared folder NSP; retensi 12 bulan' },
  { id: 'C6', group: 'C', fns: ['XD01'], topic: 'Akun read only', question: 'Definisi akun read only.', proposal: 'Role Viewer: hanya Search / Export' },
  { id: 'C7', group: 'C', fns: ['XD01'], topic: 'Effective Start Date', question: 'Aturan Effective Start Date.', proposal: 'Default besok, minimal hari ini, wajib diisi' },
  { id: 'C8', group: 'C', fns: [], topic: 'Label prototype', question: 'Label "Supplier System backend" di prototype dibiarkan atau disingkat "SS"?', proposal: 'Dibiarkan' },
];

type Choice = '' | 'agree' | 'revise' | 'unknown';
interface Answer { choice: Choice; note: string }
const CHOICES: { v: Choice; label: string; color: string }[] = [
  { v: 'agree', label: 'Setuju usulan', color: '#1e7e34' },
  { v: 'revise', label: 'Tidak / revisi', color: '#c0392b' },
  { v: 'unknown', label: 'Belum tahu', color: '#8a6d00' },
];
const KEY = 'xd.confirmation.v1';

function loadDraft(): Record<string, Answer> {
  try {
    const v: unknown = JSON.parse(window.localStorage.getItem(KEY) ?? '{}');
    return v && typeof v === 'object' ? (v as Record<string, Answer>) : {};
  } catch {
    return {};
  }
}

const fnLabel = (ids: string[]) => (ids.length ? ids.map((id) => `${FN[id]} (${id})`).join(', ') : 'Umum');

export function ConfirmationPage() {
  const [ans, setAns] = useState<Record<string, Answer>>(loadDraft);
  const [name, setName] = useState('FID Rayhan');
  const [submitted, setSubmitted] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    try { window.localStorage.setItem(KEY, JSON.stringify(ans)); } catch { /* storage unavailable */ }
  }, [ans]);

  const set = (id: string, patch: Partial<Answer>) => setAns((a) => ({ ...a, [id]: { ...(a[id] ?? { choice: '' as Choice, note: '' }), ...patch } }));
  const done = ITEMS.filter((i) => ans[i.id]?.choice).length;
  const needNote = ITEMS.filter((i) => ans[i.id]?.choice === 'revise' && !ans[i.id]?.note.trim());

  const markdown = useMemo(() => {
    const lines = [`# Jawaban Konfirmasi Crossdock (Function List v2)`, '', `Dijawab oleh: ${name}  `, `Waktu submit: ${submitted ?? '-'}`, ''];
    (Object.keys(GROUPS) as Group[]).forEach((g) => {
      lines.push(`## ${GROUPS[g].title}`, '', '| No | Function | Topik | Jawaban | Catatan |', '|---|---|---|---|---|');
      ITEMS.filter((i) => i.group === g).forEach((i) => {
        const a = ans[i.id];
        const c = CHOICES.find((x) => x.v === a?.choice);
        const jawab = c ? (c.v === 'agree' ? `Setuju: ${i.proposal}` : c.label) : 'Belum dijawab';
        lines.push(`| ${i.id} | ${fnLabel(i.fns)} | ${i.topic} | ${jawab} | ${(a?.note ?? '').replace(/\n/g, ' ')} |`);
      });
      lines.push('');
    });
    return lines.join('\n');
  }, [ans, name, submitted]);

  const json = useMemo(() => JSON.stringify({ answeredBy: name, submittedAt: submitted, answers: ITEMS.map((i) => ({
    no: i.id, functions: i.fns.map((id) => ({ id, name: FN[id] })), topic: i.topic, question: i.question, proposal: i.proposal,
    answer: ans[i.id]?.choice || null, note: ans[i.id]?.note || '',
  })) }, null, 2), [ans, name, submitted]);

  const download = (text: string, file: string, type: string) => {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const a = document.createElement('a');
    a.href = url; a.download = file; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: '18px 24px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1 style={{ fontSize: 22, margin: 0 }}>Confirmation Points</h1>
        <div style={{ fontSize: 12.5, color: 'var(--color-neutral-700)', marginTop: 3 }}>
          Pilih jawaban untuk setiap poin, tambahkan catatan kalau perlu, lalu klik Submit. Hasilnya bisa di-copy atau di-download lalu dikirim balik. Jawaban tersimpan sementara di browser ini.
        </div>
      </div>

      <div style={{ ...card, padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', fontSize: 12.5 }}>
        <label>Dijawab oleh <input value={name} onChange={(e) => setName(e.target.value)} style={{ marginLeft: 6, padding: '4px 8px', border: '1px solid var(--color-neutral-400)', borderRadius: 4 }} /></label>
        <span><b>{done}</b> / {ITEMS.length} dijawab</span>
        <div style={{ flex: 1, minWidth: 120, height: 6, background: 'var(--color-surface)', borderRadius: 3 }}>
          <div style={{ width: `${(done / ITEMS.length) * 100}%`, height: '100%', background: '#1e7e34', borderRadius: 3 }} />
        </div>
        <button className="btn btn-secondary" onClick={() => setAns(Object.fromEntries(ITEMS.filter((i) => i.group === 'C').map((i) => [i.id, { choice: 'agree' as Choice, note: ans[i.id]?.note ?? '' }]).concat(Object.entries(ans).filter(([k]) => !k.startsWith('C')))))}>
          Setuju semua grup C
        </button>
        <button className="btn btn-secondary" onClick={() => { setAns({}); setSubmitted(null); }}>Reset</button>
      </div>

      {(Object.keys(GROUPS) as Group[]).map((g) => (
        <div key={g} style={{ ...card, overflow: 'hidden' }}>
          <div style={{ padding: '10px 14px', fontSize: 14, fontWeight: 600, borderBottom: '1px solid var(--color-divider)' }}>
            {GROUPS[g].title} <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--color-neutral-700)' }}>— {GROUPS[g].hint}</span>
          </div>
          {ITEMS.filter((i) => i.group === g).map((i) => {
            const a = ans[i.id] ?? { choice: '', note: '' };
            return (
              <div key={i.id} style={{ padding: '12px 14px', borderBottom: '1px solid var(--color-divider)', display: 'grid', gridTemplateColumns: 'minmax(0, 3fr) minmax(0, 2fr)', gap: 16 }}>
                <div style={{ fontSize: 12.5, lineHeight: 1.55 }}>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'baseline', flexWrap: 'wrap' }}>
                    <b style={{ color: '#dc3545' }}>{i.id}</b><b>{i.topic}</b>
                  </div>
                  <div style={{ fontSize: 11.5, color: 'var(--color-neutral-700)', margin: '2px 0 4px' }}>Function: {fnLabel(i.fns)}</div>
                  <div>{i.question}</div>
                  <div style={{ marginTop: 4, padding: '4px 8px', background: 'var(--color-surface)', borderRadius: 4 }}><b>Usulan:</b> {i.proposal}</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {CHOICES.map((c) => (
                      <button key={c.v} onClick={() => set(i.id, { choice: c.v })}
                        style={{ padding: '4px 10px', fontSize: 12, borderRadius: 14, cursor: 'pointer', border: `1px solid ${c.color}`,
                          background: a.choice === c.v ? c.color : 'transparent', color: a.choice === c.v ? '#fff' : c.color }}>
                        {c.label}
                      </button>
                    ))}
                  </div>
                  <textarea value={a.note} onChange={(e) => set(i.id, { note: e.target.value })} rows={2}
                    placeholder={a.choice === 'revise' ? 'Wajib: tulis jawaban / revisi' : 'Catatan (opsional)'}
                    style={{ width: '100%', fontSize: 12, padding: 6, border: `1px solid ${a.choice === 'revise' && !a.note.trim() ? '#c0392b' : 'var(--color-neutral-400)'}`, borderRadius: 4, resize: 'vertical' }} />
                </div>
              </div>
            );
          })}
        </div>
      ))}

      <div style={{ ...card, padding: '12px 14px', display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', fontSize: 12.5 }}>
        {needNote.length > 0 && <span style={{ color: '#c0392b' }}>Isi catatan untuk jawaban "Tidak / revisi": {needNote.map((i) => i.id).join(', ')}</span>}
        <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <button className="btn btn-primary" disabled={done === 0 || needNote.length > 0}
            onClick={() => setSubmitted(new Date().toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }))}>
            Submit
          </button>
        </span>
      </div>

      {submitted && (
        <div style={{ ...card, padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <b style={{ fontSize: 14 }}>Jawaban ter-submit ({submitted})</b>
            <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary" onClick={() => { void navigator.clipboard?.writeText(markdown).then(() => setCopied(true)); }}>{copied ? 'Copied' : 'Copy'}</button>
              <button className="btn btn-secondary" onClick={() => download(markdown, 'Konfirmasi_Crossdock.md', 'text/markdown')}>Download .md</button>
              <button className="btn btn-secondary" onClick={() => download(json, 'Konfirmasi_Crossdock.json', 'application/json')}>Download .json</button>
            </span>
          </div>
          <pre style={{ margin: 0, fontSize: 11.5, whiteSpace: 'pre-wrap', background: 'var(--color-surface)', padding: 10, borderRadius: 4, maxHeight: 360, overflow: 'auto' }}>{markdown}</pre>
        </div>
      )}
    </div>
  );
}
