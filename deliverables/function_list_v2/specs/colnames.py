"""Template column names of the Part List and Mapping uploads (FB-145, 05-Nov): the upload sheets use the same names
as the export sheets (labels of the screen). rename() turns the former technical names into the labels."""
import re

PART_LIST_COLS = ['Part Number', 'Min MAD', 'Pcs/Case', 'Max Case/Day', 'Status', 'Upload (A/E)', 'Effective Start Date']
MAPPING_COLS = ['Part Number', 'Destination Code', 'Dest Case/Day', 'Total Case/Day (used)', 'Max Case/Day (quota)', 'Upload (A/E)']

_MAP = [('max_case_day', 'Max Case/Day'), ('total_case_day', 'Max Case/Day (quota)'), ('case_day', 'Dest Case/Day'),
        ('dest_code', 'Destination Code'), ('part_no', 'Part Number'), ('min_mad', 'Min MAD'), ('pcs_case', 'Pcs/Case'),
        ('effective_start_date', 'Effective Start Date')]


def rename(s):
    if not isinstance(s, str):
        return s
    for old, new in _MAP:
        s = re.sub(rf'(?<![A-Za-z_]){old}(?![A-Za-z_])', new, s)
    s = re.sub(r'\bupload = ([AE])\b', r'Upload (A/E) = \1', s)
    s = re.sub(r'\bupload ([AE])\b', r'Upload (A/E) \1', s)
    return s
