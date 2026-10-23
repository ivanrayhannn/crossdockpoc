"""Decisions of 19-Oct-26 (Confirmation Points answered by FID Rayhan), applied to the generated XD specs.
Run after all builders (build_all_v2.sh). Every replacement must match once or more, otherwise the build stops."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHED_DAILY = "Scheduler, daily after G-System has provided the data (27:30); auto retry 3 times."


def load(fid):
    return json.load(open(os.path.join(HERE, f"{fid}_spec.json"), encoding='utf-8'))


def save(fid, s):
    json.dump(s, open(os.path.join(HERE, f"{fid}_spec.json"), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def rep(s, pairs, fid):
    t = json.dumps(s, ensure_ascii=False)
    for a, b in pairs:
        a_j, b_j = json.dumps(a, ensure_ascii=False)[1:-1], json.dumps(b, ensure_ascii=False)[1:-1]
        if a_j not in t:
            sys.exit(f"{fid}: text not found: {a[:80]}")
        t = t.replace(a_j, b_j)
    return json.loads(t)


def sched(s, rows):
    for t in s['general']['extra_tables']:
        if t['title'] == 'Execution Schedule':
            t['rows'] = rows


CASE = ("Case = destination x pcs/case: the qty of a destination is packed in cases of pcs/case (e.g. Vietnam 24 pcs, 6 pcs/case = 4 cases). "
        "G-System releases in multiples of pcs/case (a remainder stays pending and is not in H0253), so every case is full. "
        "A case can hold several customer orders and several POs of the same destination; a customer order line that does not fit "
        "in the remaining space of a case continues in the next case (e.g. case 3 = CO-14001 4 + CO-14006 2 of PO2; "
        "case 4 = CO-14006 2 of PO2 + CO-14007 4 of PO4).")

EDITS = {
    'XD10': [
        ("Case = one per destination; the qty of a destination is summed into one case (it never exceeds pcs/case, it may be split over several lines, e.g. 4 + 2).",
         CASE),
        ("Number of cases of the unit: the qty of each destination is summed into one case.",
         "Number of cases of the unit: per destination, qty / pcs/case (e.g. 24 pcs, 6 pcs/case = 4 cases)."),
        ("One row per destination (= one case); name from TB_M_H0125_DESTINATION.",
         "One row per destination with its number of cases (qty / pcs/case); name from TB_M_H0125_DESTINATION."),
        ("Label format follows the existing case label.",
         "Label format follows the existing case label: 1 case label = 1 case of 1 destination, may list several customer order numbers."),
    ],
    'XD09': [
        ("Case = one per destination of the unit: the qty of the destination is summed into one case (it never exceeds pcs/case).", CASE),
    ],
    'XD15': [
        ("Label format follows the existing case label.",
         "Label format follows the existing case label: 1 case label = 1 case of 1 destination, may list several customer order numbers."),
    ],
    'XD05': [
        ("SYNC_STATUS is not changed: only a change of Pcs/Case, Max Case/Day or the destination mapping requires a new Sync.",
         "SYNC_STATUS: a part that changes from Active to Inactive gets SYNC_STATUS = 0 (No Sync), so the next [Sync] sends it to G-System and AP POLE with "
         "CROSSDOCK_FLAG 'N' (decided 19-Oct). Other status changes do not change SYNC_STATUS."),
    ],
    'XD01': [
        ("for every Active part of the ongoing period with Sync Status No Sync or Failed, whatever the filter shows",
         "for every Active part of the ongoing period, and every part that became Inactive, with Sync Status No Sync or Failed, whatever the filter shows"),
        ("Sync is enabled only when at least one Active part of the ongoing period is No Sync or Failed (not limited to the listed rows).",
         "Sync is enabled only when at least one Active part of the ongoing period, or a part that became Inactive, is No Sync or Failed (not limited to the listed rows)."),
        ("n = Active parts of the ongoing period with Sync Status No Sync or Failed, whatever the filter.",
         "n = Active parts of the ongoing period and parts that became Inactive, with Sync Status No Sync or Failed, whatever the filter."),
        ("Select every Active part of the ongoing period with Sync Status No Sync or Failed, whatever the search criteria show (n of the button). Candidate and Inactive parts are never synchronised.",
         "Select every Active part of the ongoing period, and every part that became Inactive (set to No Sync by XD05), with Sync Status No Sync or Failed, whatever the search criteria show (n of the button). "
         "Inactive parts are sent with CROSSDOCK_FLAG 'N' so G-System and AP POLE change their status to inactive. Candidate parts are never synchronised."),
        ("A status change made by the batch does not change the Sync Status.",
         "A change from Active to Inactive made by the batch sets the part to No Sync (it is sent as inactive by the next [Sync]); other status changes made by the batch do not change the Sync Status."),
    ],
}


def main():
    for fid, pairs in EDITS.items():
        save(fid, rep(load(fid), pairs, fid))

    s = load('XD05')
    sched(s, [["Trigger", "Monthly scheduler (set in the system master; not detailed in this document). One run = process 1, then process 2."],
              ["Auto retry", "A failed process is retried automatically up to 3 times; process 2 starts only after process 1 has succeeded."],
              ["Manual trigger", "[Run calculation (Part List)] on XD01 runs process 1 and then process 2; [Run calculation (Mapping)] on XD01 runs process 2 only. "
                                 "Each button is enabled only when its process and the 3 retries have failed."],
              ["Last success date", "One date per process in the Log; process 1 shown on the Part List tab, process 2 on the Mapping per Destination tab."],
              ["Order", "Runs after XD04. If XD04 failed, XD05 still runs (with the actual demand data available in NSP) (decided 19-Oct)."]])
    save('XD05', s)

    s = load('XD04')
    sched(s, [["Trigger", "Monthly scheduler (set in the system master; not detailed in this document)."],
              ["Order", "Runs before XD05. A failure of XD04 does not stop XD05 (decided 19-Oct)."]])
    s['general']['objective'].append("All columns are replicated as they are, including DAD (not used by the calculation) (decided 19-Oct).")
    save('XD04', s)

    s = load('XD13')
    sched(s, [["Trigger", "Scheduler after G-System has provided the data (1 time/week, 21:30); auto retry 3 times."]])
    save('XD13', s)

    # SERIAL_NO is added to the source table by the DB Surrounding team (decided 19-Oct)
    for fid in ('XD08',):
        s = load(fid)
        for t in s['tables']:
            for c in t['columns']:
                if c[0] == 'SERIAL_NO' and 'not in the current table export' in c[4]:
                    c[4] = ("No.7 Serial No., Card No. Part of the key; distinguishes split records of the same order line. "
                            "Added to the source table by the DB Surrounding team (decided 19-Oct).")
        save(fid, s)
    print('decisions 19-Oct applied')


if __name__ == '__main__':
    main()
