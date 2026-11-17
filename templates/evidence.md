# Evidence Ledger

This document is the bridge between raw interviews and synthesis. Each row must be traceable back to an interview, a quote, an observation or a material.

Don't write closed insights here. This ledger holds atomic evidence and preliminary readings that are clearly labeled as such.

## How to use it

1. Process interview by interview.
2. Extract small units of evidence.
3. Keep the source and location.
4. Separate quote, fact, observation and inference.
5. Use tags to make clustering easier.
6. Only then bring patterns into `../5-debrief/findings.md`; principles come after, in `../5-debrief/principles.md`.

## Evidence IDs are per interview

`INT-00X-NN` for an interview, `OBS-00X-NN` for an observation: the number
restarts at `01` inside each interview, not a single global counter
(`EV-001`, `EV-002`...). Two interviews being processed at the same time never
collide on an ID this way.

A quote is copied **verbatim** from the transcript, transcription errors
included. Check it against the transcript before you rely on it: a recorder's
mis-hearing does not become gospel just because it landed in the ledger.

## Vetoed quotes

A quote that a context check throws out (induced by the question, cut so the
meaning flips, professional jargon in the person's voice, hypothetical) stays in
the ledger, so nobody finds it again and brings it back. Write `vetoed: <reason>`
in the **Use in synthesis** column of its row. Nothing else changes in the row.

- A vetoed quote is not support for anything. If an analyst brings one, the
  orchestrator takes it out; it is not argued.
- `scripts/verify_quotes.py` reads the column. It gives the verdict `VETOED`, and
  exits with an error, when a vetoed quote shows up in any file it checks: the case
  sheets, a JSON list, a report, `findings.md`, `principles.md` (`--scan`).
- The clean evidence you hand to analysts is the ledger **without** the vetoed rows.

## Who speaks, and how it came out

Two optional columns, `Voice` and `Induced`, sit at the end of the ledger. Leave them empty and a row reads as `person` and `none`; a project that started without them keeps working.

- **Voice.** `person`: the speaker answers as a user, from what happened to them. `trade`: the speaker answers from their craft, for example someone who works in the sector under study explaining how it should be done. A `trade` quote is expertise, not a user's experience: it can inform a hunch about the sector, and it does not support "people like this do or feel X".
- **Induced.** How much of the quote the interviewer put there:
  - `premise`: the answer takes for granted something the question asserted.
  - `hypothetical`: the answer is to "what would you do if...", not to something that happened.
  - `moderator`: the idea came from the moderator, in the call or in a session, and ended attributed to the person.
- A quote with a value in `Induced` is never the only support of a finding. Mark the row, and say in the finding that the idea was induced. If the check of context shows that the quote says nothing the person did not get from the question, write `vetoed: <reason>` in **Use in synthesis** instead.
- The marks come from the transcript, with the ±6 lines around the quote. They are a reading: label them as such.

## Internal, not for the report

Some rows and notes are for the team only: a recruiter's remark, a hunch, a name that identifies someone. Mark them where they live. Add the tag `[not for the report]` to the line, or to any cell of a table row; for several lines, wrap them between `<!-- not for the report -->` and `<!-- end not for the report -->`.

- `scripts/check_share.py` fails when text with that mark shows up in a shared piece (`share/`, `8-report/`), and when the tag itself does.
- The mark is the only place that says it. Nothing else has to be updated, and nothing marked is deleted.
- A marked row still counts as evidence for the synthesis. The mark controls what leaves, not what you may think.

## Types of evidence

- `quote`: the interviewee's exact words.
- `fact`: a reported fact or concrete piece of data.
- `observation`: something the interviewer saw.
- `workaround`: an informal solution being used today.
- `emotion`: tension, surprise, frustration, enthusiasm, fear.
- `contradiction`: a difference between what is said and what is done, or between interviewees.
- `material`: photo, screenshot, document or artifact.
- `open_question`: something to explore in another round.
- `copilot_reading`: a labeled interpretation, not raw evidence.

## Ledger

| Evidence ID | Interview | Profile | Type | Evidence | Location | Tags | Preliminary reading | Confidence | Use in synthesis | Voice | Induced |
|---|---|---|---|---|---|---|---|---|---|---|---|
| INT-001-01 | INT-001 | Pending | quote/fact/observation/workaround/emotion/contradiction/material/open_question/copilot_reading | Pending | transcript minute/line or note section | Pending | Pending | low/medium/high | yes/no/review/vetoed: reason | person/trade | none/premise/hypothetical/moderator |

## Contradictions to preserve

| ID | Evidence A | Evidence B | Why it matters | What's still to validate |
|---|---|---|---|---|
| Pending | INT-...-.. | INT-...-.. | Pending | Pending |

## Candidate quotes

| Quote | Interview | Topic | Why it might matter | Privacy restriction |
|---|---|---|---|---|
| Pending | INT-... | Pending | Pending | none/anonymize/do not use |

## New questions for upcoming interviews

| Question | Evidence that triggers it | Who to ask | Priority |
|---|---|---|---|
| Pending | INT-...-.. | Pending | low/medium/high |
