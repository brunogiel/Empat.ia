# 1e, Plan

## Objective

Decide which pieces of the method this project uses, in what order, and who does
each one. The brief closes with that plan, so the project does not walk five
phases by default: it walks the ones it needs.

## Method notes

- **The order is the plan's, not the folder numbers'.** The numbers only name the
  folders and never move.
- **This step can run at any moment, not only at the end of phase 1.** A project
  that enters in the middle ("I already did the interviews", "I just want the
  guide") runs it first, with what the user tells you. Re-planning halfway is the
  same step: you rewrite the same section.
- The default plan is a starting point. You propose it; you never present it as
  decided.
- Every piece is one of four things: `planned`, `skipped`, `external`, `done`.
- Ideation (6) and validation (7) are on demand. The report (8) is not: every
  plan closes with it.

## First, the file of this step

This step writes into `1-desk-research/brief.md` (the `## Plan` section), which
already exists: it is one of the two files installed on day one. It also writes
the `plan:` block of `_engine/state.yaml`. Write in the language set in
`_engine/state.yaml`.

`--add plan` creates nothing: it answers that the section already lives in the
brief.

## Documents to touch

- `discovery/1-desk-research/brief.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`
- `discovery/_engine/assumptions.md`

## Process

1. **[LATENT]** Propose the plan with what the brief already knows: the
   challenge, the maturity level, the time, who is available, what already exists.
   Start from the default plan in `state.yaml` and change it.
2. **[LATENT]** Show it. If the host can show inline visuals, show it as a widget
   with one box per piece, in order, each with its status and its owner. If not,
   show it as a table.
3. **[LATENT]** For every piece, ask the person two things if the brief does not say: **who
   does it (owner)** and **who validates it or helps (reviewers)**. Then ask or propose the
   **how** (kind of session, length, format, what is used) and the **done when** (the criterion
   to call it finished). Do not leave them blank.
4. **[LATENT]** Ask for approval. Change what the user changes.
5. **[DET]** Write the `plan:` block in `_engine/state.yaml` and the `## Plan`
   section of the brief. Both say the same thing.
6. **[DET]** For every piece that is `skipped` or `external`, log it in
   `_engine/decisions.md` as an assumption: what we assume by not doing it, or who
   does it and where their result lives.

## The plan is the contract

Every row carries `owner`, `reviewers`, `how` and `done_when`, in the `plan:` block and in the
brief's table. They are the agreement between the person, the assistant and whoever validates.

- **Before closing the gate of a piece**, check the piece against its `how` and `done_when`.
  If they are not met, do not close it in silence: recommend `Deepen` or log the deviation.
- **If the method of a piece changes** (a different kind of session, another length, someone
  else running it), log it in `_engine/decisions.md` as a course change: date, what changed,
  why. Then update the row. A method never changes in silence.

## The one-pager

When the plan is approved, offer a one-page shareable version to align a client or a team before
starting (see "Shareable snapshots" in the Guide's `SKILL.md`). It uses `templates/share-onepager.html`.

## What you tell the user about each state

Say it in the project's language, in plain words.

- **Skipped:** "We are not doing this one, and we write down what we assume by
  not doing it."
- **External:** "Someone outside does this one; here we only link their result."
- **Planned or done:** nothing to explain.

A `piece` is a phase or a step: a step of a phase counts as its own row. An external piece
with no link yet is valid: write "link pending" in `note`. If `plan:` is empty because the
brief already had its own `## Plan`, build `plan:` from that section: the brief wins.

A skipped piece gets its assumption in `note` and in `decisions.md`. An external
piece gets its owner and the link to their material in `owner` and `note`. No
folder is created for either. The status line counts an external piece, and an
external piece never blocks the next one.

## Entering in the middle

If the project starts at phase 4, the brief stays minimal and the plan marks
phases 1 to 3 as `skipped`, each with the assumption it stands on. Then move: you
recommend, you do not block.

## Quality checklist

- The order reads as the order of the work.
- Every `skipped` piece has an assumption, and every `external` piece has an owner
  and a link or a date.
- The report (8) is in the plan.
- A reader who sees only the plan table knows what the next step is and who does it.

## Gate

Suggested action:

- `Advance` if the plan is approved and every skipped or external piece is logged.
- `Deepen` if the user cannot say who does a piece or when.
- `Question` if a piece is skipped without a stated assumption.
- `Council` if the plan skips the field and the project depends on what users do.
