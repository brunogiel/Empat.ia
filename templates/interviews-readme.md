# Interviews

This folder is the working tray for all field material: transcripts, notes, audio, photos, shared documents, consents and observations.

Central rule: raw material is preserved. Synthesis happens later, with traceability.

## Structure

```text
interviews/
├── README.md
├── index.md
├── evidence-ledger.md
├── incoming/
├── transcripts/
├── notes/
│   └── _notes-template.md
├── artifacts/
├── consent/
└── processed/
```

## For whoever is running the process

When you finish interviews or receive material, drop it into `incoming/` without worrying about making it perfect. It can come in as:

- a complete transcript,
- loose notes,
- the interviewer's summary,
- audio or video,
- photos of the context,
- screenshots,
- documents shared by the interviewee,
- consent or authorization.

Later the Guide organizes that material without losing the source.

## Recommended naming

Use a unique ID per interview.

```text
INT-001_name-or-alias_profile_date.ext
```

Examples:

```text
INT-001_maria_sme-admin_2026-05-14_transcript.md
INT-001_maria_sme-admin_2026-05-14_notes.md
INT-001_maria_sme-admin_2026-05-14_process-photo.jpg
```

If there is sensitive privacy, use an alias:

```text
INT-003_alias-a_shop-owner_2026-05-18_transcript.md
```

## Processing flow

1. Drop material into `incoming/`.
2. Register each interview in `index.md`.
3. Move or copy clean transcripts into `transcripts/`.
4. Create a structured note in `notes/` using `_notes-template.md`.
5. Save photos, documents or screenshots in `artifacts/`.
6. Save consent or restrictions in `consent/`.
7. Extract atomic evidence into `_system/evidence-ledger.md`.
8. Only then cross-reference patterns in `../principles.md`.

## What counts as evidence

- A verbatim quote.
- A fact reported by the interviewee.
- An interviewer observation.
- A concrete workaround.
- A moment of emotion, tension or surprise.
- A contradiction.
- Material shared with permission.
- An open question that surfaces from the field.

## Rules

- Don't mix interviews without IDs.
- Don't turn loose notes into insights without a source.
- Don't erase contradictions.
- Don't fill silences with inferences.
- If the Guide interprets something, label it as `Co-pilot reading`.
- If consent is missing, don't use identifiable quotes.
