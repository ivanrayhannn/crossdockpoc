"""05-Nov: FB-143 the Operation Description of XD01 points to the sample sheets added to the hand-tidied workbook
(Export Part List, Upload Part List, Export Mapping, Upload Mapping); the Mapping export shows Total Case/Day as
used plus Max Case/Day (quota), as on the screen."""
import json

with open('XD01_spec.json') as f:
    s = json.load(f)
ADD = [("Edit rows use sheet 'Upload' of the Part List Export Excel as base file (pre-filled with flag E).", " Sample: sheet 'Upload Part List'."),
       ("Effective Start Date, Last Update. Information only.", " Sample: sheet 'Export Part List'."),
       ("Dest Pcs/Day, Dest Percentage. Information only.", " Sample: sheet 'Export Mapping'."),
       ('"XD03 Part and Destination Mapping Upload Batch".', " Template sample: sheet 'Upload Mapping'.")]
for b in s['operation']:
    for i, t in enumerate(b.get('items', [])):
        if isinstance(t, str):
            for end, extra in ADD:
                if t.endswith(end) and extra not in t:
                    t = t + extra
            b['items'][i] = t
for b in s['operation']:
    for i, t in enumerate(b.get('items', [])):
        if isinstance(t, str) and t.startswith("Sheet 'Mapping per Destination'"):
            b['items'][i] = t.replace('Pcs/Case, Total Case/Day, Pcs/Day', 'Pcs/Case, Total Case/Day (used), Max Case/Day (quota), Pcs/Day')
with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
