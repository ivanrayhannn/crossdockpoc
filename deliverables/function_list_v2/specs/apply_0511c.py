"""05-Nov (FB-145): the upload templates use the column names of the export sheets (labels of the screen) and are read
by column name. Mapping upload: Part Number, Destination Code, Dest Case/Day, Total Case/Day (used), Max Case/Day
(quota), Upload (A/E) - used and quota are reference only. Part List upload: Part Number, Min MAD, Pcs/Case,
Max Case/Day, Status, Upload (A/E), Effective Start Date."""
import json
from colnames import rename, PART_LIST_COLS, MAPPING_COLS


def load(fid):
    with open(f'{fid}_spec.json') as f:
        return json.load(f)


def save(fid, s):
    with open(f'{fid}_spec.json', 'w') as f:
        json.dump(s, f, indent=1, ensure_ascii=False)


def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v) for v in o]
    if o == 'status':
        return 'Status'
    if o == 'upload':
        return 'Upload (A/E)'
    return rename(o)


def put(lst, old_start, new):
    for i, t in enumerate(lst):
        if isinstance(t, str) and t.startswith(old_start):
            lst[i] = new


# ---------- XD02 (Part List upload)
s = walk(load('XD02'))
s = json.loads(json.dumps(s).replace('Header has the 7 template columns (see Appendix). Extra columns are ignored.',
                                     'Header has the 7 template columns (see Appendix), found by column name (case and leading / trailing spaces '
                                     'ignored). Extra columns are ignored.'))
save('XD02', s)

# ---------- XD03 (Mapping upload)
s = walk(load('XD03'))
s = json.loads(json.dumps(s).replace('Header has the 5 template columns (see Appendix). Extra columns are ignored.',
                                     'Header has the 6 template columns (see Appendix), found by column name (case and leading / trailing spaces '
                                     'ignored). Extra columns are ignored.'))
for b in s['func_desc']:
    for i, t in enumerate(b.get('items', []) or []):
        if isinstance(t, str) and t.startswith('The column Max Case/Day (quota) is for reference only'):
            b['items'][i] = ('The columns Total Case/Day (used) and Max Case/Day (quota) are for reference only and are not read; '
                             'the limit is Max Case/Day of the part in TB_M_PART_CANDIDATE and used is calculated from Dest Case/Day.')
app = s['appendix'][1]
rows = {r[0]: r for r in app['rows']}
rows['Total Case/Day (used)'] = ['Total Case/Day (used)', 'Sum of Dest Case/Day of the part when the file is exported, for reference only '
                                 '(not read by the batch; the batch calculates it from Dest Case/Day).']
rows['Max Case/Day (quota)'][1] = 'Max Case/Day of the part in Part List, for reference only (not read by the batch).'
app['rows'] = [rows[c] for c in MAPPING_COLS]
for sec in s['sample_sheet']['sections']:
    cols = sec.get('columns', [])
    if 'Dest Case/Day' in cols and 'Upload (A/E)' in cols and 'Total Case/Day (used)' not in cols:
        iu, iq, ic, ip = cols.index('Upload (A/E)'), cols.index('Max Case/Day (quota)'), cols.index('Dest Case/Day'), cols.index('Part Number')
        sums = {}
        for r in sec['rows']:
            if isinstance(r[ic], (int, float)):
                sums[(r[0], r[ip])] = sums.get((r[0], r[ip]), 0) + r[ic]
        new_rows = []
        for r in sec['rows']:
            used = sums.get((r[0], r[ip]), '' if not isinstance(r[ic], (int, float)) else 0)
            new_rows.append(r[:iu] + [used, r[iq], r[iu]] + r[iq + 1:])
        sec['columns'] = cols[:iu] + ['Total Case/Day (used)', 'Max Case/Day (quota)', 'Upload (A/E)'] + cols[iq + 1:]
        sec['rows'] = new_rows
save('XD03', s)

# ---------- XD01 (references to the templates)
s = load('XD01')
for it in s['items']:
    d = it.get('description', '')
    if isinstance(d, str) and d.startswith(('part_no, min_mad', 'Part Number, Min MAD')):
        it['description'] = ', '.join(PART_LIST_COLS) + " (same names and order as sheet 'Upload' of Export Excel)."
    if isinstance(d, str) and d.startswith(('part_no, dest_code', 'Part Number, Destination Code')):
        it['description'] = ', '.join(MAPPING_COLS) + " (same names and order as sheet 'Upload' of Export Excel)."
for b in s['operation']:
    items = b.get('items', [])
    put(items, "Sheet 'Upload': every registered part",
        "Sheet 'Upload': every registered part, columns as sheet 1 (Part Number, Min MAD, Pcs/Case, "
        "Max Case/Day, Status, Upload (A/E) = E, Effective Start Date). Base file for Edit uploads.")
    put(items, 'The modal shows the template columns (',
        "The modal shows the 6 template columns (as sheet 'Upload' of Export Excel), the upload "
        "rules and the file area (.xlsx, max 5 MB, max 5,000 rows).")
    put(items, "Sheet 'Upload': every Active part of the ongoing period",
        "Sheet 'Upload': every Active part of the ongoing period, columns Part Number, Destination "
        "Code, Dest Case/Day, Total Case/Day (used), Max Case/Day (quota), Upload (A/E); "
        "one row per destination, and one blank row (Upload (A/E) = A) for a part without mapping. "
        "Empty for a past period or All periods. Upload (A/E) = E for a mapped destination.")
    for i, t in enumerate(items):
        if isinstance(t, str) and t.startswith("Sheet 'Mapping per Destination'"):
            items[i] = t.replace('Pcs/Case, Total Case/Day (used), Max Case/Day (quota), Pcs/Day, Percentage, Sync Status, Destination Code, Destination, '
                                 'Dest Case/Day, Dest Pcs/Day, Dest Percentage',
                                 'Pcs/Case, Destination Code, Destination, Dest Case/Day, Total Case/Day (used), Max Case/Day (quota), Pcs/Day, Percentage, '
                                 'Dest Pcs/Day, Dest Percentage, Sync Status')
s = json.loads(json.dumps(s, ensure_ascii=False).replace("Edit rows use sheet 'Upload' of the Part List Export Excel as base file (pre-filled with flag E).",
                                                         "Edit rows use sheet 'Upload' of the Part List Export Excel as base file (pre-filled with Upload (A/E) = E)."))
save('XD01', s)
