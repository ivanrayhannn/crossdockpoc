# XD02 – Cross Dock Part Master Upload Batch

Sumber: UISS `XD02_UISS_Batch_CrossDockPartMasterUpload.xlsx` (0.1 Initial Draft, 18-Oct-26). Nama sistem di UISS: GTOPAS / NSP.

- Isi sama dengan X2 Part List Upload (detail: `deliverables/md/X2_BATCH_PartList_Upload.md`).
- Dipanggil dari [Validate file] tab Part List di **XD01**. Referensi diganti: screen → XD01, kalkulasi → XD05, Sync → XD06 / XD07.

## Update 27-Oct (kolom upload)
- Kolom template `flag_add_edit` diganti nama jadi **`upload`** (nilai A = Add, E = Edit; aturan tidak berubah). Check 1: upload = A atau E.
