# Verification log

Owns: what each verifier checked, at which gate, what it caught, what changed and what stayed and why, and what already went out and in which state. Does not own: the findings → `findings.md`.

The record that lets you defend what goes out. The literal check says a quote exists; the context check says whether it supports what is claimed. Only the second one finds reading errors.

## Gate · {{stage}} · {{date}}

### Deterministic check (quote script)

- Quotes checked, and how many came back OK / close match / said by the interviewer / failed: Pending.
- **Seeded-error control:** errors planted on a copy (a changed quote, an invented one, one from another person, one from the interviewer). Caught: Pending of Pending. If the check does not catch them, the gate is worth nothing.

### Model check: does the quote support the claim?

| Sheet or section | Reviewed | NO | PARTIAL | Verifier (model tier) | Seeds caught |
|---|---|---|---|---|---|
| Pending | Pending | Pending | Pending | Pending | Pending of Pending |

- **Every model checker is seeded, in any phase** (this one, the devil's advocate, cuali-to-cuanti, a clip or a guide check). Seeds caught: Pending of Pending. A checker that missed a seed counts for nothing: change the model tier or narrow the question, and seed again. Questions of sense go to a mid or strongest model; a small one misses exaggerations buried in long text and is only for inventory and binary questions.

### Context check (the key quotes, about 6 lines around)

Looks for led questions, cuts that change the meaning, contradictions with the person's own behavior and professional voice. Video and audio clips are read too: what the clip says against its caption and the finding it illustrates.

- Reviewed: Pending. With a problem: Pending.

### Qualitative to quantitative check

Looks for generalizations ("most"), rankings presented as measured, counts that do not close with the sheets, things nobody said and the researcher's opinion presented as a finding.

### Devil's advocate

The strongest case against the conclusion, using quotes only. Verdict: nothing / nuance / rewrite.

## What already went out

One row for each file that left the team, in any form. At every gate, `scripts/check_share.py` runs the checks on all of them. When a finding you corrected sits in a row, mark it `outdated` in the same step and decide whether to resend; after the new version goes, mark it `corrected and resent`.

| File | To whom | When | What it claims | State |
|---|---|---|---|---|
| Pending | Pending | Pending | Pending | current / outdated / corrected and resent |

## What changed and what stayed

| Item | What the check found | Decision | Why |
|---|---|---|---|
| Pending | Pending | changed / kept | Pending |
