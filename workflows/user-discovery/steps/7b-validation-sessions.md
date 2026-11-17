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
- **A session on a screen (a prototype, a wireframe, a form) is processed with its video. The video is not an extra.** The transcript says what was said; the video says what was clicked, skipped or misread. Read the video in the same pass as the transcript, session by session.
- **Sample the video so the clicks are seen.** One frame every 10 seconds misses a click that lasts a second. Take frames densely (one every 1 to 2 seconds) in the seconds around each moment of interaction: a task starting or ending, a prompt from the moderator, a phrase that points ("this", "here"), a long silence, a return to an earlier screen. Add a frame at every scene change (for example ffmpeg's `select='gt(scene,0.02)'` filter). Sparse frames are enough for the stretches between.
- **What the video did not show is deduced.** Write each action of the person on the screen as `seen` (you watched it in the frames) or `deduced` (it comes from the words, or from a frame that did not catch the click). A `deduced` action stays in the note and the count says how many of its rows were seen.
- **Test data, never the person's own.** In a session on a prototype or a form, the person types test data (a made-up name, a mailbox and a phone that belong to the project). Never ask them to enter their real data, and never share a screen that shows it. If a real one shows up anyway, the clip is cut or blurred before anyone else sees it.
- **Check every capture before it is used.** Open each screenshot and each clip at no fewer than three frames (start, middle, end). Anything sensitive in any of them is blurred: emails, phone numbers, passwords, names, chats and notifications of the call itself. A clip with something sensitive that cannot be blurred is not used.
- Don't cross sessions until each one is processed.

## Before each session: logistics checklist

Each item below cost a session minutes, or its evidence, at least once. Go through it with the
person or the contact who invites them, a day before and again when the call opens.

- [ ] **The right device.** If the task is for a desktop, the person joins from a computer, not the phone. Say it in the invitation, and check it in the first minute: a session started on a phone often has to restart.
- [ ] **The access travels with the link.** A password, a code or a test account is sent in the same message as the link, never separately and never asked for in the call. Open the link yourself from a clean window with that access, the same day.
- [ ] **Test data is ready.** The forms of the prototype hold made-up data, or the person gets a sheet of it to type from. Nobody enters their real data (see "Test data" above). Delete anything real that was entered anyway, and note it.
- [ ] **The call window does not cover the work.** The floating window of the video call, its toolbar and the chat sit over a corner of the shared screen. Move them before the first task, and ask the person to say if something on the prototype is hidden. Check the corner where the prototype keeps its buttons.
- [ ] **Time per task, with a cut.** Give each task a time box in the prep sheet. When a box runs out, say "let's move on" and mark the task `stuck` or `not finished`: do not let one task eat the last one or the closing. Decide in advance which task gives way if the session runs short.
- [ ] **Recording and consent** are on before the first task, per person (consent record in `2-profiling/recruiting.md`, see `3-guide/process.md`).

## The moderator's feedback

A session on a screen gets its own feedback page, not the interview one: the person talks
less and acts more, so the three scales of discovery (how much they tell, monologue, get to
the point) would compare things that are not alike. Create it with
`python3 <method-root>/scripts/init_project.py --project-root . --add validation-feedback-html --name VAL-001-...`
(`templates/moderator-feedback.html`). It has one row per task of the script with how far the
person got and how (`alone`, `guided`, `induced`), from where the person spoke (`person` as a user,
`trade` from their craft, the same `Voice` word as the evidence ledger), and what the moderator
did that helped or led. It lists what the moderator said that came back as the person's. Read the
recorder's automatic summary against the session before it is trusted: it tends to turn the
moderator's words into the person's findings.

## First, the file of this step

The files this step writes do not exist yet. That is the design: nothing is
created before its step starts.

1. **[DET]** Create the index and the evidence ledger:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation_capture`
   It creates `7-validation/0-index.md`, and `_engine/evidence.md` if it is not there.
2. **[DET]** Per session, create each file with a name:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation-note --name VAL-001-ana-lopez`
   Same for `validation-prep`, `validation-feedback` (the internal worksheet) and `validation-feedback-html` (the page the moderator receives). Never copy the templates by hand.
3. **[DET]** Write each one **in the language set in `_engine/state.yaml`**.
4. **[LATENT]** Pre-fill with what the project already knows.

## Optional: what did "this" and "here" point at?

When the sessions were screen-shared and the participant points without naming ("this is confusing"),
`scripts/resolve_deictics.py` pairs each phrase with five frames of the shared screen and a glossary
of the product's components. It is local, it needs the video, and it produces a sheet per session
with a confidence and a capture per row. Method, limits and privacy rules: `docs/deictic-resolver.md`.
Rows marked "review" are opened by a person before any of them is quoted in the findings.
The strips cover the phrases that point. A click made without a word needs the dense sampling above.

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
- `7-validation/feedback/`: how the sessions were run, one worksheet and one page per session.
- `7-validation/0-index.md`: the tracker.

## Process

1. Ask the user to drop the material in `7-validation/_raw/`.
2. Assign an ID and a base name per session: `VAL-001-name-surname`.
3. Fill out `0-index.md` with metadata and status.
4. Process each session with the `process-interview` skill: it handles `VAL-` too. For a session on a screen, read the video in the same pass (see the notes above).
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
