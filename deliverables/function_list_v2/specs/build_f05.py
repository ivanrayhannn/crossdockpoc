"""F05 DAD Volume Calculation Batch = DAD Volume Calculation (X6, process 1: part status) +
Mapping Destination Calculation (X7, process 2: destination mapping of the new period)."""
import re
from build_simple import CALC_POST
from v2lib import derive, load, map_strings, replace_all, set_header, shift_ids, shift_section_refs, write


def union(a, b, key='name'):
    out, seen = [], {}
    for x in a + b:
        k = x[key] if isinstance(x, dict) else (x[0] if isinstance(x, list) else x)
        if k in seen:
            continue
        seen[k] = True
        out.append(x)
    return out


def prefix_flow(flow, pre, step_off):
    for n in flow['nodes']:
        n['id'] = pre + n['id']
        if n.get('step'):
            n['step'] += step_off
    for e in flow['edges']:
        e['from'], e['to'] = pre + e['from'], pre + e['to']
    return flow


def build():
    tabs = [('on the Part List screen', 'on the Part List tab of F01'),
            ('on the Mapping per Destination screen', 'on the Mapping per Destination tab of F01'),
            ('from the Part List screen', 'from the Part List tab of F01'),
            ('from the Mapping per Destination screen', 'from the Mapping per Destination tab of F01')]
    a = replace_all(derive(load('DadCalc_spec.json')), tabs + CALC_POST)
    b = replace_all(derive(load('MapCalc_spec.json')), tabs + CALC_POST)
    na = len(a['func_flow']['steps'])
    for k in ('func_flow', 'func_desc', 'data_map'):
        b[k] = shift_section_refs(b[k], '4', 4)
        b[k] = map_strings(b[k], lambda s: re.sub(r'(steps? )(\d+)( to )?(\d+)?',
                                                  lambda m: m.group(1) + str(int(m.group(2)) + na)
                                                  + ((m.group(3) + str(int(m.group(4)) + na)) if m.group(4) else ''), s))
    shift_ids(b['logging_messages'], 'LOG', len(a['logging_messages']))

    # steps: process 1 hands over to process 2
    sa, sb = a['func_flow']['steps'], b['func_flow']['steps']
    sa[0] = "Process 1 (part status) starts from the scheduler, an automatic retry, or [Run calculation (Part List)] on F01."
    sa[7] = f"No error: commit process 1, record SUCCESS of process 1 in the Log (END_DT = last success date). Continue with step {na + 1} (process 2)."
    sa[8] = {"text": "Error: roll back process 1, record FAILED in the Log; process 2 is not started.",
             "children": ["The scheduler retries automatically up to 3 times. After the 3rd failed retry, [Run calculation (Part List)] is enabled on F01. Exit."]}
    sb[0] = ("Process 2 (destination mapping) starts after process 1 has succeeded, from an automatic retry of process 2, "
             "or [Run calculation (Mapping)] on F01 (process 2 only). It uses the part status just set by process 1.")
    last = sb[-1]
    if isinstance(last, dict):
        last['text'] = 'Error: roll back process 2, record FAILED of process 2 in the Log.'
        last['children'] = ["The scheduler retries process 2 automatically up to 3 times. After the 3rd failed retry, "
                            "[Run calculation (Mapping)] is enabled on F01. Process 1 stays committed. Exit."]

    fa = prefix_flow(a['func_flow']['flow'], 'a_', 0)
    fb = prefix_flow(b['func_flow']['flow'], 'b_', na)
    flow = {"direction": "TB", "nodes": fa['nodes'] + fb['nodes'],
            "edges": fa['edges'] + [{"from": "a_p8", "to": "b_p1", "label": "process 2"}] + fb['edges']}

    def heads(desc, label):
        return [dict(d, text=re.sub(r'^(4\.\d+) ', rf'\1 {label} - ', d['text'])) if d['type'] == 'heading' else d
                for d in desc if d['type'] != 'column_break']
    da, db = a['func_desc'], b['func_desc']
    func_desc = ([{"type": "text", "level": 0, "text": "One batch with two processes run in sequence: process 1 sets the part status from the "
                   "average MAD (4.1 - 4.4); process 2 creates the destination mapping of the new period for the Active parts (4.5 - 4.8). "
                   "Range of months and schedule are set in the system master (not explained in this document)."}]
                 + heads(da[1:], 'Process 1') + [{"type": "column_break"}] + heads(db[1:], 'Process 2'))

    for blk in a['data_map']['blocks']:
        blk['destination']['description'] = 'Process 1: ' + blk['destination'].get('description', '')
    for blk in b['data_map']['blocks']:
        blk['destination']['description'] = 'Process 2: ' + blk['destination'].get('description', '')

    ga, gb = a['general'], b['general']
    par = {t['title']: t for t in ga['extra_tables']}
    pbr = {t['title']: t for t in gb['extra_tables']}
    extra = [
        {"title": "Parameters", "columns": par['Parameters']['columns'],
         "rows": union(par['Parameters']['rows'], pbr['Parameters']['rows'])},
        {"title": "Grouping Keys", "columns": par['Grouping Keys']['columns'],
         "rows": [r + ' (process 1 and 2)' if r == 'PART_NO' else r + ' (process 2)' for r in union(par['Grouping Keys']['rows'], pbr['Grouping Keys']['rows'])]},
        {"title": "Execution Schedule", "columns": par['Execution Schedule']['columns'], "rows": [
            ["Trigger", "Scheduler set in the system master (monthly; date and time TBC). One run = process 1, then process 2."],
            ["Auto retry", "A failed process is retried automatically up to 3 times; process 2 starts only after process 1 has succeeded."],
            ["Manual trigger", "[Run calculation (Part List)] on F01 runs process 1 and then process 2; [Run calculation (Mapping)] on F01 runs process 2 only. "
                               "Each button is enabled only when its process and the 3 retries have failed."],
            ["Last success date", "One date per process in the Log (all-or-nothing per process); process 1 shown on the Part List tab, process 2 on the Mapping per Destination tab."],
            ["Order", "Runs after F04 Actual Demand Summary Synch has finished."]]}]

    spec = {
        "doc_type": "batch",
        "general": {
            "objective": ["Process 1: " + ga['objective'][0], "Process 2: " + gb['objective'][0],
                          "Each process is all-or-nothing and is retried automatically up to 3 times; after that it can be started manually "
                          "from the Cross Dock Part Master screen (F01)."],
            "operation_flow": {"flow": {"direction": "TB", "nodes": [
                {"id": "a", "label": "Scheduler / retry / F01 [Run calculation]", "type": "event"},
                {"id": "b", "label": "Process 1: average MAD vs Min MAD -> Active / Inactive", "type": "process"},
                {"id": "c", "label": "Process 2: result MAD per destination -> Case/Day of the new period", "type": "process"},
                {"id": "d", "label": "Save, Log", "type": "process"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c", "label": "success"}, {"from": "c", "to": "d"}]}},
            "inputs": union(ga['inputs'], gb['inputs']),
            "outputs": union(ga['outputs'], gb['outputs']),
            "extra_tables": extra},
        "func_flow": {"flow": flow, "steps": sa + sb},
        "data_map": {"blocks": a['data_map']['blocks'] + b['data_map']['blocks']},
        "func_desc_layout": "two",
        "func_desc": func_desc,
        "logging_messages": [dict(m, event='Process 1: ' + m['event']) for m in a['logging_messages']]
                            + [dict(m, event='Process 2: ' + m['event']) for m in b['logging_messages']],
        "appendix_layout": "full",
        "appendix": [{"type": "text", "level": 0, "text": "Calculation examples (process 1 and process 2), rounding and limit examples: see sheet Sample Input."}],
        "sample_sheet": {"title": "Sample Input", "heading": "Sample calculation - DAD Volume Calculation (process 1 and process 2)",
                         "intro": ["Process 1: " + x for x in a['sample_sheet']['intro']] + ["Process 2: " + x for x in b['sample_sheet']['intro']],
                         "sections": [dict(s, title='Process 1 - ' + s['title']) for s in a['sample_sheet']['sections']]
                                     + [dict(s, title='Process 2 - ' + s['title']) for s in b['sample_sheet']['sections']]},
        "tables": union(a['tables'], b['tables']),
    }
    return write(set_header(spec, 'F05'), 'F05')


if __name__ == '__main__':
    print(build())
