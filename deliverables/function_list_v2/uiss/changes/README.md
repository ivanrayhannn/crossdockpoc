# UISS dengan highlight perubahan

Salinan review UISS Crossdock Master sampai kalkulasi volume. Sel **kuning** = isi yang baru atau berubah: logic, business rule, kolom atau tabel baru.
File UISS resmi ada di `../` dan tidak diberi warna.

| File | Dibanding dengan |
|---|---|
| `XD01_UISS_Screen_CrossDockPartMaster_changes.xlsx` | XD01 v8 dari user (`XD01_UISS_Screen_CrossDockPartMaster_8.xlsx`, sebelum perubahan 22-Nov) |
| `XD02_UISS_Batch_CrossDockPartMasterUpload_changes.xlsx` | Versi repo sebelum 22-Nov (commit `52ce4f2^`) |
| `XD03_UISS_Batch_PartDestinationMappingUpload_changes.xlsx` | Versi repo sebelum 22-Nov (commit `52ce4f2^`) |
| `XD05_UISS_Batch_DADVolumeCalculation_changes.xlsx` | Versi repo sebelum 22-Nov (commit `52ce4f2^`) |

Aturan highlight (`specs/highlight_changes.py`):
- Ganti nama saja **tidak** ditandai: Part List = Kanban Crossdock Master, Mapping per Destination = Export Crossdock Master, No Sync = Non Sync, nama file export.
- Teks yang hanya pindah baris, pindah kolom, atau ter-wrap ulang tidak ditandai. Nomor urut, label layout dan header dokumen (baris 1-4) juga tidak.
- Sheet contoh (Export / Upload ...): hanya judul kolom baru yang ditandai; isi baris contoh tidak.
- Baris judul grup yang di template berwarna kuning dibuat abu-abu muda di salinan ini, supaya kuning hanya berarti "berubah".
- Screen Layout dan Screen Flow (gambar / shape) tidak dibandingkan.
- Perubahan kata-kata pesan (Display Message) tetap ditandai: teks pesan yang dilihat user ikut berubah.

Build ulang:
```
python3 deliverables/function_list_v2/specs/highlight_changes.py OLD.xlsx NEW.xlsx OUT.xlsx
```
