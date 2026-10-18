"""Helpers for the UISS of the new function list (F01-F15). The specs of the first version (X1-X15) in
deliverables/uiss_specs are read only; every F spec is derived from them or written here."""
import copy, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.normpath(os.path.join(HERE, '..', '..', 'uiss_specs'))
sys.path.insert(0, OLD)

NAME, PROJ, DATE = 'FID Rayhan', 'Crossdock Optimization', '18-Oct-26'
NC = 'Not changed'

# New function list: id -> (title, block, output file)
FUNCS = {
    'F01': ('Cross Dock Part Master Screen', 'Screen', 'F01_UISS_Screen_CrossDockPartMaster.xlsx'),
    'F02': ('Cross Dock Part Master Upload Batch', 'Batch', 'F02_UISS_Batch_CrossDockPartMasterUpload.xlsx'),
    'F03': ('Part and Destination Mapping Upload Batch', 'Batch', 'F03_UISS_Batch_PartDestinationMappingUpload.xlsx'),
    'F04': ('Actual Demand Summary Synch to NSP', 'Batch', 'F04_UISS_Batch_ActualDemandSummarySync.xlsx'),
    'F05': ('DAD Volume Calculation Batch', 'Batch', 'F05_UISS_Batch_DADVolumeCalculation.xlsx'),
    'F06': ('IF Cross Dock Master to GTOPAS', 'Batch', 'F06_UISS_Batch_IFCrossDockMasterToGTOPAS.xlsx'),
    'F07': ('IF Cross Dock Master to AP POLE', 'Batch', 'F07_UISS_Batch_IFCrossDockMasterToAPPOLE.xlsx'),
    'F08': ('Order Control Information to NSP Batch (ASN)', 'Batch', 'F08_UISS_Batch_OrderControlInfoToNSP_ASN.xlsx'),
    'F09': ('Mapping Customer Order and PO Batch', 'Batch', 'F09_UISS_Batch_MappingCustomerOrderPO.xlsx'),
    'F10': ('ASN Cross Dock Creation Screen', 'Screen', 'F10_UISS_Screen_ASNCrossDockCreation.xlsx'),
    'F11': ('Cancel Crossdock Customer Order Batch', 'Batch', 'F11_UISS_Batch_CancelCrossdockCustomerOrder.xlsx'),
    'F12': ('Order Control Information to NSP Batch (Cancel)', 'Batch', 'F12_UISS_Batch_OrderControlInfoToNSP_Cancel.xlsx'),
    'F13': ('Destination Master Synch into NSP', 'Batch', 'F13_UISS_Batch_DestinationMasterSync.xlsx'),
    'F15': ('ASN Crossdock Inquiry Screen (Buffer)', 'Screen', 'F15_UISS_Screen_ASNCrossdockInquiry.xlsx'),
}

# First-version function id -> new id (X3 screen -> F01; its RPA part is now F06 / F07)
XMAP = {'X1': 'F01', 'X2': 'F02', 'X3': 'F01', 'X4': 'F03', 'X5': 'F04', 'X6': 'F05', 'X7': 'F05', 'X8': 'F10',
        'X10': 'F08', 'X11': 'F13', 'X12': 'F09', 'X13': 'F15', 'X14': 'F10'}

# Text replacements applied to every derived spec (order matters)
COMMON = [
    ('UISS-Batch "Crossdock Master Setting - Part List Upload"', 'UISS-Batch "F02 Cross Dock Part Master Upload Batch"'),
    ('UISS-Batch "Crossdock Master Setting - Mapping per Destination Upload"', 'UISS-Batch "F03 Part and Destination Mapping Upload Batch"'),
    ('UISS-Batch Part List Upload', 'UISS-Batch F02 Cross Dock Part Master Upload'),
    ('UISS-Batch Mapping per Destination Upload', 'UISS-Batch F03 Part and Destination Mapping Upload'),
    ('Crossdock Master Setting - Part List screen', 'Cross Dock Part Master screen (Part List tab)'),
    ('Crossdock Master Setting - Mapping per Destination screen', 'Cross Dock Part Master screen (Mapping per Destination tab)'),
    ('UISS-Batch Mapping Destination Calculation', 'UISS-Batch F05 DAD Volume Calculation (process 2)'),
    ('UISS-Batch DAD Volume Calculation', 'UISS-Batch F05 DAD Volume Calculation (process 1)'),
    ('RPA user ID', 'IF batch user ID'),
    ('source RPA', 'source IF'),
    ("'RPA'", "'IF'"),
    ('SCREEN / UPLOAD / RPA / BATCH', 'SCREEN / UPLOAD / IF / BATCH'),
    ('The RPA function', 'The IF functions F06 / F07'),
    ('the RPA function', 'the IF functions F06 / F07'),
    ('by the RPA', 'by the IF functions (F06 / F07)'),
    ('The RPA', 'The IF functions (F06 / F07)'),
    ('the RPA', 'the IF functions (F06 / F07)'),
    ('RPA', 'IF function'),
    ('the global system', 'GTOPAS and AP POLE'),
    ('global system', 'GTOPAS and AP POLE'),
]


def load(name):
    return copy.deepcopy(json.load(open(os.path.join(OLD, name), encoding='utf-8')))


def map_strings(obj, fn):
    """Apply fn to every string value (keys are kept)."""
    if isinstance(obj, dict):
        return {k: map_strings(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [map_strings(v, fn) for v in obj]
    if isinstance(obj, str):
        return fn(obj)
    return obj


def replace_all(obj, pairs):
    def fn(s):
        for a, b in pairs:
            s = s.replace(a, b)
        return s
    return map_strings(obj, fn)


def remap_ids(obj):
    return map_strings(obj, lambda s: re.sub(r'\bX(\d{1,2})\b', lambda m: XMAP.get(m.group(0), m.group(0)), s))


def derive(spec, extra=()):
    """Common replacements, then the function id remap."""
    return remap_ids(replace_all(spec, list(extra) + COMMON))


def set_header(spec, fid):
    title, block, _ = FUNCS[fid]
    spec['header'] = {"phase": "DR", "project_name": PROJ, "block_name": block, "function_name": f"{fid} {title}",
                      "created_date": DATE, "created_by": NAME}
    spec['revisions'] = [{"revision": "0.1", "author": NAME, "date": DATE, "reviewed_by": "", "description": "Initial Draft"}]
    return spec


def batch_header(fid):
    return set_header({}, fid)


def shift_numbers(text, pattern, off):
    """Shift the numbers captured by group 2 of pattern (group 1 is kept)."""
    return re.sub(pattern, lambda m: m.group(1) + re.sub(r'\d+', lambda n: str(int(n.group(0)) + off), m.group(2)), text)


def shift_msg_refs(obj, off):
    pat = r'([Mm]essages? no\. ?)(\d+(?:\s*(?:,|and)\s*\d+)*)'
    return map_strings(obj, lambda s: shift_numbers(s, pat, off))


def shift_section_refs(obj, major, off):
    """Shift references like 5.3 (major = '5') by off: 5.3 -> 5.(3+off)."""
    pat = r'\b' + major + r'\.(\d+)\b'
    return map_strings(obj, lambda s: re.sub(pat, lambda m: f"{major}.{int(m.group(1)) + off}", s))


def shift_ids(items, prefix, off):
    for m in items:
        mid = m.get('msg_id', '')
        mm = re.fullmatch(prefix + r'(\d+)', mid or '')
        if mm:
            m['msg_id'] = f"{prefix}{int(mm.group(1)) + off}"


def table_of(spec_name, table):
    s = json.load(open(os.path.join(OLD, spec_name), encoding='utf-8'))
    return copy.deepcopy(next(t for t in s['tables'] if t['name'] == table))


def full_update(mappings, columns):
    """Complete an Update block: every column not mapped is 'Not changed'."""
    have = {m['dest_field'] for m in mappings}
    return mappings + [{"dest_field": c[0], "description": NC} for c in columns if c[0] not in have]


def write(spec, fid):
    out = os.path.join(HERE, f"{fid}_spec.json")
    json.dump(spec, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return out
