# 7c, Validation debrief

## Objective

Turn the validation sessions into three answers: what people understood, where
they got stuck, and what to change. The debrief of the validation lives inside
phase 7; it does not reopen the field debrief.

## Method notes

- Every finding rests on evidence `VAL-00X-NN`.
- Report what people did. What they said they would do is a weaker signal: label it.
- Count: how many of how many, not "some". With 2 people or fewer, say what each did; do not mark it as having worked.
- Compare with the bets of the ideation: held, partly, did not.
- A task nobody got stuck on is a finding too.
- Don't make things up.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created before its step starts.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation_debrief`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/7-validation/findings.md`
- `discovery/7-validation/0-index.md`
- `discovery/_engine/evidence.md`
- `discovery/6-ideation/concepts.md`
- `discovery/_engine/decisions.md`
- `discovery/_engine/assumptions.md`
- `discovery/_engine/state.yaml`

## Process

1. Review `7-validation/0-index.md`: what is ready, what is missing.
2. Review the `VAL-` rows of `_engine/evidence.md`.
3. Group by task.
4. Write what they understood, where they got stuck, and what to change.
5. Check each bet of the ideation against the evidence.
6. List what you still do not know, such as a profile that was not tested.
7. **[DET]** Before the findings leave the team, run the two scripts:
   `python3 <method-root>/scripts/verify_quotes.py --cases` (or `--file` on the HTML) reads `VAL-`
   quotes against `7-validation/_raw`, and
   `python3 <method-root>/scripts/check_counts.py 7-validation/findings.md` lists every universal
   ("nobody", "everyone", "most") with the transcript lines that could break it, every "X of N"
   to check by hand against the evidence rows, and refuses a success tick on 2 people or fewer.
   Two people can show where someone got stuck. They cannot show that something worked.
8. **[DET]** Run `python3 <method-root>/scripts/check_share.py` on everything that already went out
   (`share/`, `8-report/`): it repeats the quote and count checks and adds the internal-marks and codes
   brakes. If a finding you changed here sits in a piece that already left, mark that row `outdated`
   in the **What already went out** table of `5-debrief/verification-log.md` and decide whether to
   resend. What the devil's advocate corrects goes into the findings in this same step.

## Quality criteria

- Each change points at the finding that asks for it, and says how big it is.
- Each finding has a count and an evidence ID.
- Contradictions stay visible.
- Nothing that already left still carries a finding this step changed, or it is marked `outdated` in the log.

## Council

Suggest `Council` if the sessions point to a different concept, or if the changes
undo a principle from the field debrief.

## Gate

Suggested action:

- `Advance` if the findings are traceable and the changes are clear.
- `Deepen` if sessions are missing.
- `Question` if conclusions go beyond the evidence.
- `Council` if the validation contradicts the principles.
