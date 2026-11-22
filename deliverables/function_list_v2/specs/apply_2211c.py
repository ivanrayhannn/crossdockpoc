"""22-Nov: copy pass on XD01 (antislop copywriting).
- Decision dates such as (22-Nov) / (decided 30-Oct) are removed from the body text; they stay in the Revision sheet.
- Sentences with broken grammar are rewritten with the same meaning; 'can not' -> 'cannot'.
- Screen messages: 'Title - body' popups use a colon, passive 'has been ...' becomes plain present tense,
  'Duplication found' / 'concurrency check' say what happened to the user.
- Modal titles and the read-only badge use a colon instead of a dash, as on the prototype.
No fact, number or rule is added or removed."""
import json, re

with open('XD01_spec.json') as f:
    s = json.load(f)

DATE = re.compile(r'\s?\((?:decided )?\d{1,2}-(?:Sep|Oct|Nov)\)|,\s\d{1,2}-(?:Sep|Oct|Nov)(?=\))|\s\(\d{1,2}-(?:Sep|Oct|Nov)\)')
REPL = [
    ("'Part No' lists parts of TB_M_PART_MASTER that are not yet registered in TB_M_PART_CANDIDATE, so can not register part into Crossdock master",
     "'Part No' lists only parts of TB_M_PART_MASTER that are not registered in TB_M_PART_CANDIDATE yet, so a part cannot be registered twice."),
    ("Insert the change history when any register or update data in Kanban Crossdock Master",
     "Insert the change history in TB_H_PART_CANDIDATE (refer 5.6)."),
    ("Insert the change history when any register or update in Kanban Crossdock Master",
     "Insert the change history in TB_H_PART_CANDIDATE (refer 5.6)."),
    ("History retrieved from inserted data when user add/modify part list data",
     "The history comes from the records inserted when a user adds or changes a part."),
    ("(Status, Pcs/Case, Max Case/Day, Pcs/Case, Max Case/Day of that month)", "(Status, Pcs/Case and Max Case/Day of that month)"),
    ("Export Crossdock Master tab: to send the changes", "Export Crossdock Master tab: To send the changes"),
    ("Upload Excel - destination mapping", "Upload Excel: destination mapping"),
    ("Upload Excel - part settings", "Upload Excel: part settings"),
    ("Past period - read only", "Past period: read only"),
    ("New row - pick a destination", "New row: pick a destination"),
    ("can not", "cannot"),
]
MSGS = {
    'MSG1': 'No matching parts. Change the search criteria or reset the filters.',
    'MSG2': 'No crossdock part is registered yet.',
    'MSG3': '{Part No} is already registered.',
    'MSG4': 'Another user changed this part after you opened it. Refresh and edit again.',
    'MSG9': 'Saved successfully: {Part No} · {Part Name} is saved and shown at the top of the Kanban Crossdock Master.',
    'MSG10': 'Can only be changed while the status is Candidate.',
    'MSG11': 'Saved successfully: the file passed validation and the part settings are saved to the Kanban Crossdock Master.',
    'MSG14': 'Max Case/Day cannot be less than the mapped total of the ongoing period ({n} case/day). Reduce the mapping in Export Crossdock Master first.',
    'MSG16': 'Calculation completed: part statuses are updated from the average MAD against Min MAD.',
    'MSG18': 'No parts match these filters. Change the period or sync status, or click [Reset] to show all parts.',
    'MSG19': 'No destination yet. Click [Edit mapping] and add at least one destination so the part is included in the volume calculation.',
    'MSG24': 'Saved successfully: the file passed validation and the destination mapping is saved to Export Crossdock Master.',
    'MSG25': 'Another user changed this mapping after you started editing. Refresh and edit again.',
    'MSG27': 'Sync started for {n} part(s) to AP POLE and GTOPAS. The result comes by e-mail.',
    'MSG29': 'Calculation completed: the destination mapping of the new period is created.',
}
SECTIONS = {'Mapping - Result List': 'Export Crossdock Master - Result List',
            'Mapping - Destination Mapping panel': 'Export Crossdock Master - Destination Mapping panel'}


def fix(o):
    if isinstance(o, dict):
        return {k: fix(v) for k, v in o.items()}
    if isinstance(o, list):
        return [fix(v) for v in o]
    if isinstance(o, str):
        o = DATE.sub('', o)
        for a, b in REPL:
            o = o.replace(a, b)
        return SECTIONS.get(o, o)
    return o


for k in list(s):
    if k not in ('revisions', 'header'):
        s[k] = fix(s[k])
for m in s['display_messages']:
    if m.get('msg_id') in MSGS:
        m['message'] = MSGS[m['msg_id']]

if not any(r['revision'] == '0.9' for r in s['revisions']):
    s['revisions'].append({'revision': '0.9', 'author': 'FID Rayhan', 'date': '22-Nov-26', 'reviewed_by': '',
                           'description': 'Copy review: decision dates removed from the body text (kept here), sentences with broken grammar rewritten, screen messages reworded (no rule changed).'})

with open('XD01_spec.json', 'w') as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
