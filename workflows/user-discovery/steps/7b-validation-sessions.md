# 7b, Validation sessions

## Objective

Capture each validation session as it happened and turn it into evidence, one
session at a time, without synthesising yet.

## Method notes

- One note per session, one prep sheet, one recording or transcript.
- Session IDs are `VAL-00X`, never `INT-` or `OBS-`.
- Record what they did, in order, before what they said.
- Mark moments where they stopped, went back, or asked for help.
- For each task, mark **how far they got and how**: `alone` (nobody said anything that pointed the way), `guided` (the moderator answered a question or gave a hint first), or `induced` (the idea or the word came from the moderator and ended attributed to the person). Mark it while you watch; it is hard to rebuild later.
- **Test data, never the person's own.** In a session on a prototype or a form, the person types test data (a made-up name, a mailbox and a phone that belong to the project). Never ask them to enter their real data, and never share a screen that shows it. If a real one shows up anyway, the clip is cut or blurred before anyone else sees it.
- **Check every capture before it is used.** Open each screenshot and each clip at no fewer than three frames (start, middle, end). Anything sensitive in any of them is blurred: emails, phone numbers, passwords, names, chats and notifications of the call itself. A clip with something sensitive that cannot be blurred is not used.
- Don't cross sessions until each one is processed.

## First, the file of this step

The files this step writes do not exist yet. That is the design: nothing is
created before its step starts.

1. **[DET]** Create the index and the evidence ledger:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation_capture`
   It creates `7-validation/0-index.md`, and `_engine/evidence.md` if it is not there.
2. **[DET]** Per session, create each file with a name:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation-note --name VAL-001-ana-lopez`
   Same for `validation-prep` and `validation-feedback`. Never copy the templates by hand.
3. **[DET]** Write each one **in the language set in `_engine/state.yaml`**.
4. **[LATENT]** Pre-fill with what the project already knows.

## Optional: what did "this" and "here" point at?

When the sessions were screen-shared and the participant points without naming ("this is confusing"),
`scripts/resolve_deictics.py` pairs each phrase with five frames of the shared screen and a glossary
of the product's components. It is local, it needs the video, and it produces a sheet per session
with a confidence and a capture per row. Method, limits and privacy rules: `docs/deictic-resolver.md`.
Rows marked "review" are opened by a person before any of them is quoted in the findings.

## Documents to touch

- `discovery/7-validation/`
- `discovery/7-validation/0-index.md`
- `discovery/_engine/evidence.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/assumptions.md`

## Folder structure

- `7-validation/VAL-00X-name-surname.md`: one structured note per session.
- `7-validation/_prep/`: the per-session prep sheets, copies of the task script.
- `7-validation/_raw/`: the recording or transcript, and consent notes, under the same base name.
- `7-validation/feedback/`: how the sessions were run, one file per session.
- `7-validation/0-index.md`: the tracker.

## Process

1. Ask the user to drop the material in `7-validation/_raw/`.
2. Assign an ID and a base name per session: `VAL-001-name-surname`.
3. Fill out `0-index.md` with metadata and status.
4. Process each session with the `process-interview` skill: it handles `VAL-` too.
5. Extract atomic evidence into `_engine/evidence.md`, with IDs `VAL-00X-NN`.
6. Update `validations` in `_engine/state.yaml`.
7. Mark gaps before moving to the debrief.

## Gate

Suggested action:

- `Advance` if there is enough material to write the findings.
- `Deepen` if a profile or a task has no sessions.
- `Question` if the person was helped through the tasks.
- `Council` if the sessions contradict each other.

Before offering `Advance`, if `validations.unprocessed` in `state.yaml` is above
zero, say so and offer to process them first.
