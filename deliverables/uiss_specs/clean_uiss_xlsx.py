"""Remove template leftovers that make Excel repair UISS workbooks.

The TMAP template carries invalid / broken defined names (e.g. "???", #REF!, links to
external workbooks [1]..[6]) and the external link parts they point to. Keeps only the
print settings (_xlnm.Print_Area / _xlnm.Print_Titles). Gridlines are hidden on every sheet (view mode) and the
"Number Stored as Text" marker of Excel is switched off (numbering such as '1.' is text on purpose).
Usage: clean_uiss_xlsx.py FILE.xlsx ...
"""
import re, shutil, sys, tempfile, zipfile

def clean(path):
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out = []
    for info, data in items:
        name = info.filename
        if name.startswith('xl/externalLinks/'):
            continue
        if name == 'xl/workbook.xml':
            x = data.decode('utf-8')
            x = re.sub(r'<externalReferences>.*?</externalReferences>', '', x, flags=re.S)
            x = re.sub(r'<definedName (?![^>]*name="_xlnm\.)[^>]*?(?:/>|>.*?</definedName>)', '', x, flags=re.S)
            x = re.sub(r'<definedNames>\s*</definedNames>', '', x)
            data = x.encode('utf-8')
        elif name == 'xl/_rels/workbook.xml.rels':
            x = data.decode('utf-8')
            x = re.sub(r'<Relationship [^>]*Type="[^"]*/externalLink"[^>]*/>', '', x)
            data = x.encode('utf-8')
        elif re.match(r'xl/worksheets/sheet\d+\.xml$', name):
            x = data.decode('utf-8')
            x = re.sub(r'(<sheetView\b[^>]*?)\sshowGridLines="[^"]*"', r'\1', x)
            x = re.sub(r'<sheetView\b', '<sheetView showGridLines="0"', x)
            if 'numberStoredAsText' not in x:
                ign = '<ignoredErrors><ignoredError sqref="A1:XFD1048576" numberStoredAsText="1"/></ignoredErrors>'
                m = re.search(r'<(smartTags|drawing|legacyDrawing|legacyDrawingHF|picture|oleObjects|controls|webPublishItems|tableParts|extLst)\b|</worksheet>', x)
                x = x[:m.start()] + ign + x[m.start():]
            data = x.encode('utf-8')
        elif name == '[Content_Types].xml':
            x = data.decode('utf-8')
            x = re.sub(r'<Override [^>]*PartName="/xl/externalLinks/[^"]*"[^>]*/>', '', x)
            data = x.encode('utf-8')
        out.append((info, data))
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)
    shutil.move(tmp, path)

for p in sys.argv[1:]:
    clean(p)
    print('cleaned', p)
