# Validation index

Owns: the tracker of validation sessions. Does not own: the notes themselves → `7-validation/VAL-*.md`; evidence → `_engine/evidence.md`.

Every validation session in one table: what came in, what is still
unprocessed, and which profile is thin.

Files are not listed: they are derivable from the ID. `VAL-003` means
`VAL-003-<name>-<surname>[-<company>].md`, its sheet in `_prep/`, and its
recording or transcript in `_raw/`, all sharing that base name.

## Where we stand

- Target: Pending sessions. *(from `_engine/state.yaml`, `validations:`)*
- Done: Pending.
- Processed: Pending.
- **Unprocessed: Pending.** *(the Guide raises this before the validation debrief)*

## The table

| ID | Alias | Profile | Date | Status | Consent | Gaps |
|---|---|---|---|---|---|---|
| VAL-001 | Pending | Pending | Pending | raw | Pending | Pending |

## Statuses

- `raw`: the material is in `7-validation/_raw/`, nothing processed yet.
- `noted`: it has a structured note and minimum metadata.
- `evidence`: its evidence is in `_engine/evidence.md`.
- `ready`: it can be used in the validation debrief.
- `incomplete`: missing recording, notes, metadata or consent. Say which.

## Sample gaps

Which profile was not tested, and what that stops you from claiming.

- Pending.
