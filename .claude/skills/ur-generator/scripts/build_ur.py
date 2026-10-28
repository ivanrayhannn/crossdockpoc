"""build_ur.py - render a User Requirement workbook: the TMAP UISS template (same sheets as UISS-Screen / Report / Batch)
with Phase "UR" and Document Name "User Requirement". The spec format is the UISS spec (references/spec-schema.md),
written in business wording (references/business-writing-guide.md).

Usage: python3 build_ur.py UR_SPEC.json -o UR_<ID>.xlsx"""
import argparse, json, os, re, shutil, sys, tempfile, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_uiss  # noqa: E402


def hide_gridlines(path):
    """Gridlines off on every sheet (view mode), like the delivered UISS files."""
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for info, data in items:
            if re.match(r'xl/worksheets/sheet\d+\.xml$', info.filename):
                x = re.sub(r'(<sheetView\b[^>]*?)\sshowGridLines="[^"]*"', r'\1', data.decode('utf-8'))
                data = re.sub(r'<sheetView\b', '<sheetView showGridLines="0"', x).encode('utf-8')
            z.writestr(info, data)
    shutil.move(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding='utf-8'))
    h = spec.setdefault('header', {})
    h.setdefault('phase', 'UR')
    h.setdefault('document_name', 'User Requirement')
    res = build_uiss.build(spec, a.out)
    hide_gridlines(a.out)
    print(json.dumps({k: v for k, v in res.items()}, indent=1, default=str))


if __name__ == '__main__':
    main()
