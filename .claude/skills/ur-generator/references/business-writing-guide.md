# Business writing guide (UR in the UISS layout)

The UR uses the UISS sheets, but every cell is read by a business user. Ask for each sentence: *could the
Procurement / D/S / supplier user check this against their work without asking IT?*

## General rules

| Do | Don't |
|---|---|
| "Save the part in the Part List" | "Insert into TB_M_PART_CANDIDATE" |
| "Sync Status becomes No Sync" | "SYNC_STATUS = '0'" |
| "sorted by last update, newest first" | "ORDER BY CHANGED_DT DESC" |
| "the part can be registered only once" | "unique key PART_NO" |
| "System error: the part could not be saved" | "DB error on insert, rollback" |
| "Saved by / time" (one row) | CREATED_BY, CREATED_DT, CHANGED_BY, CHANGED_DT |
| Business object names: Part List, Destination Mapping, Customer Order, PO, ASN, Case | Table prefixes TB_M_, TB_R_, TB_H_, #TEMP |
| Function IDs as references: "the calculation (XD05)" | Batch internals: watermark, upsert, delta, commit |

Keep: menu / button / field names exactly as on the screen, message numbers, step numbers, dates DD-Mon-YYYY,
business codes users know (destination code, part number, PO number).

## Sheet by sheet

- **Revision**: same as UISS; description e.g. "Initial Draft: business version of UISS <file>".
- **Gen Desc**: first objective = the business purpose in one sentence (who, what, why). Buttons: what the button
  does for the user. Screen modes: unchanged (E / D).
- **Screen Flow / Func Flow**: same diagrams; node labels in business words ("Save the part", not "Insert record").
- **Screen Layout**: same screenshots; captions describe what the user sees.
- **Item Desc**: Item name as on screen; Source = "Entered by user", "System", or the business object
  ("Part Master"); Field / Length = `-`; Type = Text / Number / Date; Format only for dates; Validation and
  Description in business words.
- **Data Map**: destination = business object; operation = Add / Change / Remove; one row per business item
  (internal audit fields collapsed into "Saved by / time"); description says where the value comes from
  ("entered by the user", "Pcs/Case x Max Case/Day").
- **Operation / Functional Description**:
  - starts with **x.0 Business Rules** (ID, topic, rule);
  - steps in the UISS numbering, written as user action → system result;
  - ends with **Acceptance Criteria (UAT)**: Given / When / Then, linked BR, empty Result column;
  - no column definitions, no SQL, no table structures.
- **Display Message**: same IDs; cause and action in business words.
- **Logging Message**: same IDs; "System error" instead of DB error; say what the user / support should do.

## Vocabulary file (vocab.json)

Map every technical name of the project once and reuse it for all functions, e.g.

```json
{"TB_M_PART_CANDIDATE": "Part List", "TB_M_PART_CANDIDATE_DEST": "destination mapping",
 "TB_H_PART_CANDIDATE": "change history", "PART_STATUS": "status", "SYNC_STATUS": "Sync Status",
 "MAX_CASE_DAY": "Max Case/Day", "CHANGED_DT": "last update time"}
```

Names not in the vocab are humanised automatically (TB_M_PART_CANDIDATE → "Part Candidate"), which is readable
but not always the business term: prefer adding them to the vocab.

## extra.json

```json
{"purpose": "Give Procurement and the D/S team one place to manage ...",
 "business_rules": [["BR-01", "Part status", "A new part always starts as Candidate ..."]],
 "acceptance": [["AC-01", "Given a new part, when Procurement saves it, then ...", "BR-01, BR-03"]],
 "phrases": [["Insert the part into Part List with", "Save the part in the Part List with"]],
 "internal_fields": ["sync time", "sync message"]}
```
