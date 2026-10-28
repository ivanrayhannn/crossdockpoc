---
name: "ur-generator"
description: Generate a User Requirement (UR) document for business users in the TMAP UISS Excel format — the same sheets as UISS-Screen / UISS-Report / UISS-Batch (Revision, Gen Desc, Screen Flow, Screen Layout, Item Desc, Data Map, Operation / Functional Description, Messages) but written in plain business language, with business rules and acceptance criteria (UAT). Use this skill whenever the user wants a User Requirement, URD, business requirement, "UR seperti UISS", "UISS versi bahasa bisnis", "dokumen untuk business user / user review / sign-off", or wants to convert an existing UISS (spec JSON or xlsx), FSD, BRD or meeting summary into a business-readable requirement in the UISS layout — even if they don't say "UR". Use uiss-generator instead when the reader is a developer (tables, fields, data mapping, log IDs).
---

# UR Generator (business-language UISS)

A duplicate of the UISS generator with one difference: **the reader is a business user** (Procurement, D/S team,
supplier, management). The workbook keeps every UISS sheet, header block, grid and colour, so business users and
developers look at the same structure; only the wording changes:

| UISS (developer) | UR (business user) |
|---|---|
| `TB_M_PART_CANDIDATE.SYNC_STATUS = '0' (No Sync)` | Sync Status of the part is No Sync |
| Insert into `TB_X` / Update / Delete | Save in the Part List / Change / Remove |
| Field, length, format `X..20..X`, `ZZ,ZZ9` | left out (`-`); dates stay `DD-Mon-YYYY` |
| CREATED_BY, CHANGED_DT, LAST_SOURCE … | one row "Saved by / time" |
| Column definitions (DDL) | left out (they stay in the UISS) |
| — | 5.0 Business Rules (BR-xx) and Acceptance Criteria (AC-xx, Given / When / Then) |

Message IDs, step numbers (5.1, 5.2 …), screen modes and screenshots stay the same as the UISS so every UR line
can be traced to the UISS line.

## Inputs

- **Existing UISS spec JSON** (best: the exact source of the UISS) or a UISS .xlsx, **or** a meeting summary /
  FSD / BRD / notes (Indonesian is fine; the document is written in English).
- Screenshots for Screen Layout (user supplied, never drawn).
- Header facts: project, function ID + name, author.
- Optional: purpose, business rules, acceptance criteria. If none are given, derive them from the content and
  mark unsure ones `TBD`.

## Workflow

1. **Read** `references/business-writing-guide.md` (how each sheet is phrased for business users) and, for the JSON
   format, `references/spec-schema.md` (identical to the UISS spec).
2. **Choose the path**
   - *From a UISS spec JSON* → write `vocab.json` (technical name → business term, e.g.
     `"TB_M_PART_CANDIDATE": "Part List"`) and `extra.json` (purpose, business_rules, acceptance, optional phrases),
     then convert:
     ```bash
     python3 <skill-dir>/scripts/to_business.py UISS_SPEC.json -o UR_SPEC.json --vocab vocab.json --extra extra.json
     ```
     The output lists `technical_names_left`: add them to the vocab (or to `phrases` for whole sentences) and run
     again until the list is empty. Then read the Operation Description of `UR_SPEC.json` and rewrite any sentence
     that still sounds technical (add it to `phrases`).
   - *From a UISS .xlsx* → read it (openpyxl / pandas), rebuild the spec, then as above.
   - *From notes / FSD* → write `UR_SPEC.json` directly in business wording, following the guide.
3. **Build**
   ```bash
   python3 <skill-dir>/scripts/build_ur.py UR_SPEC.json -o UR_<Type>_<ID>.xlsx
   ```
   (Phase "UR" and Document Name "User Requirement" are set by default.)
4. **Look at the result** (render to PDF and view Gen Desc, Item Desc, Data Map, Operation Desc):
   ```bash
   soffice --headless --convert-to pdf --outdir /tmp/ur UR_<Type>_<ID>.xlsx && pdftoppm -r 70 -png /tmp/ur/UR_<Type>_<ID>.pdf /tmp/ur/page
   ```
5. **Deliver** the workbook and reply in the user's language: sheets generated, number of business rules and
   acceptance criteria, terms that were translated, and open questions (every `TBD`), phrased for the business user.

## Rules

- Same sheets and numbering as the UISS; do not add or drop sheets.
- No physical table or column names, status codes, SQL, log internals or batch jargon in the UR text. Function IDs
  (XD05, XD06) may stay as references in brackets.
- Business rules: one rule per row, short, testable, with an ID (BR-01 …). Acceptance criteria: Given / When / Then,
  each linked to its BR.
- Keep facts; do not invent behaviour. Unknown → `TBD`.
- Do not change the UISS itself; the UR is a separate workbook.
