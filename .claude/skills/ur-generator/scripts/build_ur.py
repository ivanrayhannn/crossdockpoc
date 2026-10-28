"""build_ur.py - render a User Requirement workbook: the TMAP UISS template (same sheets as UISS-Screen / Report / Batch)
with Phase "UR" and Document Name "User Requirement". The spec format is the UISS spec (references/spec-schema.md),
written in business wording (references/business-writing-guide.md).

Usage: python3 build_ur.py UR_SPEC.json -o UR_<ID>.xlsx"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_uiss  # noqa: E402


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
    print(json.dumps({k: v for k, v in res.items()}, indent=1, default=str))


if __name__ == '__main__':
    main()
