# XD03 – Part and Destination Mapping Upload Batch

Sumber: UISS `XD03_UISS_Batch_PartDestinationMappingUpload.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: GTOPAS / NSP.

- Isi sama dengan X4 Mapping per Destination Upload (detail: `deliverables/md/X4_BATCH_Mapping_Upload.md`).
- Dipanggil dari [Validate file] tab Mapping per Destination di **XD01**. Destination master dari **XD13**.

## Update 27-Oct (kolom upload)
- Kolom baru **`upload`** di template (sesudah case_day): **A** = destinasi baru untuk part, **E** = destinasi yang sudah di-mapping. Export Excel mengisi E, dan A untuk baris placeholder.
- Check 8 baru: A hanya untuk destinasi yang belum di-mapping, E hanya untuk yang sudah di-mapping (contoh error E9). Aturan replace per part tetap.
