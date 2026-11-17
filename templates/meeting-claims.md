# What I said vs. the evidence

Owns: each claim the researcher made in a client meeting, set against the evidence, and the correction to bring back. Does not own: what the meeting decided about the files → `_engine/meeting-coverage.md`; the evidence itself → `_engine/evidence.md`; the findings → `findings.md`.

Run it after a meeting in which the researcher gave conclusions before the debrief was closed. The client keeps notes of what was said. A sentence that the evidence does not hold is corrected **with the client**, not only in the files.

## Claims

One row per sentence the researcher said about the people studied. Check each one against `findings.md` and `_engine/evidence.md`. Count people, not mentions.

| # | What was said | Evidence | Verdict | Correction for the client |
|---|---|---|---|---|
| 1 | Pending | Pending | holds / holds with a nuance / does not hold / to confirm | Pending |

## What the client asked and stayed open

Same scale. A question with no evidence yet says so and goes to the next round.

| Question | What the evidence says | Verdict | Next step |
|---|---|---|---|
| Pending | Pending | holds / holds with a nuance / does not hold / to confirm | Pending |

## A list the client voted or ranked

If the client voted or prioritised a list, compare against the **whole list as the client gave it**, not against what the draft already crossed. Every item has a row. An item the evidence does not cover is a row that says "no evidence", not a missing row.

| Item on the client's list | Client's vote | What the evidence shows | Reading |
|---|---|---|---|
| Pending | Pending | Pending | same / different / no evidence |

## Before it leaves

- A short page for the client built from this file, with profiles and no names.
- It goes through cuali-to-cuanti and `check_share.py` like any piece (see `workflows/user-discovery/steps/5a-debrief.md`).
- Log the correction and the date in `_engine/decisions.md`.
