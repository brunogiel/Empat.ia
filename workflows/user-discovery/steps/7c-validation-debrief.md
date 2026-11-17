# 7c, Validation debrief

## Objective

Turn the validation sessions into three answers: what people understood, where
they got stuck, and what to change. The debrief of the validation lives inside
phase 7; it does not reopen the field debrief.

## Method notes

- Every finding rests on evidence `VAL-00X-NN`.
- Report what people did. What they said they would do is a weaker signal: label it.
- Every "what they did" carries one of three marks: **alone** (nobody pointed the way), **guided** (the moderator gave a hint or an answer first) or **induced** (the idea came from the moderator and ended attributed to the person). A task that someone finished only after a hint did not work alone.
- **The headline separates two things: where something happened and how it was reached.** "Five of seven reached the form" says where; "two did it alone, three guided" says how. Never put the first without the second in a title or a slide.
- **Say how much of it was seen.** In a session on a screen, a count of what people did also says how many of its rows were seen in the video and how many are `deduced` from the transcript (see `7b`). A deduced row can point to where to look; it does not carry a "worked" on its own.
- An `induced` row never supports "this worked". It is a lead for the next round.
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
3. Group by task, and inside each task by how it was reached (alone, guided, induced).
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

9. **[LATENT]** Every model check this step runs (does the quote support the finding, cuali-to-cuanti, the devil's advocate) follows "Every model checker" in `5a-debrief.md`: it runs first on a copy with planted errors and must catch them, it runs on a mid or strong model, and the log says "seeds caught: X of Y". Every quote or clip that supports a finding gets the ±6 lines of context (a clip against the finding it illustrates). A validation finding built on what a person said they would do, checked by a checker that missed its seeds, is not checked.
10. **[DET]** Update `substeps:` if the project uses it, and run `python3 <method-root>/scripts/check_state.py` before closing.

## Optional, on request: the minute and the clip

When the sessions were on a screen and the findings will play moments of them, two scripts help. `scripts/locate_quotes.py` finds the minute of each quote in the video (the recorder's transcript can be off by minutes). `scripts/cut_clips.py` cuts the clip, burns the captions in, checks that it says the quote and makes a thumbnail. Neither is needed to close this step; both pay off most with a prototype shown on screen. Choose each clip against the title of the finding it illustrates, not by topic, and use only a clip whose check gave `ok: true`. Method, limits and privacy: `docs/quote-clips.md`.

## Quality criteria

- Every request in "What the client asked for" (`brief.md`) is answered here or moved to the next round with one line.
- Every count says how many reached it alone, guided and induced.
- Every capture or clip used was checked at three frames and shows no sensitive data (see 7b).
- In a session on a screen, every count says how many rows were seen in the video and how many are deduced.
- Each change points at the finding that asks for it, and says how big it is.
- Each finding has a count and an evidence ID.
- Contradictions stay visible.
- Every model checker caught its seeded errors before its verdict counted, and the log says so.
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
