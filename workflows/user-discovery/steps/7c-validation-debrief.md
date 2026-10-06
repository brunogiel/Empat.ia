# 7c, Validation debrief

## Objective

Turn the validation sessions into three answers: what people understood, where
they got stuck, and what to change. The debrief of the validation lives inside
phase 7; it does not reopen the field debrief.

## Method notes

- Every finding rests on evidence `VAL-00X-NN`.
- Report what people did. What they said they would do is a weaker signal: label it.
- Count: how many of how many, not "some".
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

## Quality criteria

- Each change points at the finding that asks for it, and says how big it is.
- Each finding has a count and an evidence ID.
- Contradictions stay visible.

## Council

Suggest `Council` if the sessions point to a different concept, or if the changes
undo a principle from the field debrief.

## Gate

Suggested action:

- `Advance` if the findings are traceable and the changes are clear.
- `Deepen` if sessions are missing.
- `Question` if conclusions go beyond the evidence.
- `Council` if the validation contradicts the principles.
