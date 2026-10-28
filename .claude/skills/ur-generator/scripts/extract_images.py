#!/usr/bin/env python3
"""
extract_images.py - pull embedded screenshots out of an existing FSD/spec so they can be reused
in Screen Layout / Report Layout.

Usage:
    python extract_images.py /mnt/user-data/uploads/FSD.xlsx -o /home/claude/img
    python extract_images.py FSD.xlsx -o img --id-regex "^([A-Z]\\d\\d)\\s"   # name by screen ID

.xlsx : every picture is saved as <ID>.png when a cell in column A at or above the picture's
        anchor matches --id-regex (default: codes like P01, M12, D21, SCR-01), otherwise as
        <sheet>_r<row>.png. Prints one line per image: file, sheet, anchor row, size, label.
.docx : every file in word/media is saved in document order as img_<n>.<ext>.
"""
import argparse
import io
import os
import re
import sys
import zipfile


def from_xlsx(path, out, id_regex):
    from openpyxl import load_workbook
    from PIL import Image
    rx = re.compile(id_regex)
    wb = load_workbook(path)
    for ws in wb.worksheets:
        labels = {}
        for r in range(1, ws.max_row + 1):
            v = ws.cell(r, 1).value
            if isinstance(v, str):
                m = rx.match(v.strip())
                if m:
                    labels[r] = (m.group(1), v.strip())
        for k, im in enumerate(ws._images):
            row = im.anchor._from.row + 1
            above = [r for r in labels if r <= row]
            if above:
                sid, text = labels[max(above)]
            else:
                sid, text = f"{re.sub(r'[^A-Za-z0-9]+', '_', ws.title)}_r{row}", ""
            name = sid
            n = 2
            while os.path.exists(os.path.join(out, name + ".png")):
                name = f"{sid}_{n}"
                n += 1
            img = Image.open(io.BytesIO(im._data()))
            dst = os.path.join(out, name + ".png")
            img.save(dst)
            print(f"{dst}\t{ws.title}\trow {row}\t{img.size[0]}x{img.size[1]}\t{text[:80]}")


def from_docx(path, out):
    with zipfile.ZipFile(path) as z:
        media = sorted([n for n in z.namelist() if n.startswith("word/media/")],
                       key=lambda s: int(re.sub(r"\D", "", s) or 0))
        for i, n in enumerate(media, 1):
            ext = os.path.splitext(n)[1]
            dst = os.path.join(out, f"img_{i}{ext}")
            with open(dst, "wb") as fh:
                fh.write(z.read(n))
            print(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--id-regex", default=r"^([A-Z]{1,3}-?\d{2,3})\b")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ext = os.path.splitext(a.source)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        from_xlsx(a.source, a.out, a.id_regex)
    elif ext == ".docx":
        from_docx(a.source, a.out)
    else:
        sys.exit("supported: .xlsx, .xlsm, .docx (convert .xls/.doc with LibreOffice first)")


if __name__ == "__main__":
    main()
