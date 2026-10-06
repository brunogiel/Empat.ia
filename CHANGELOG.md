# Changelog

## Unreleased

### Added: the brief closes with a plan, and the map grows to eight pieces

No real project followed the five phases in a straight line: some skipped the market, some
entered after the interviews were done, some ran a round of validation, and all of them ended
with something to hand over. The method now matches that.

- **The brief closes with a `## Plan`**: which pieces the project uses, in what order, who does
  each, and when. `state.yaml` mirrors it under `plan:` as an ordered list of
  `{piece, status, owner, note}`, with status `planned`, `skipped`, `external` or `done`. **The
  order is the plan's, not the folder numbers'.** The step is `1e-plan.md` and it can run at any
  moment, including first, for a project that enters in the middle. A skipped or external piece
  is logged as an assumption. The default plan has the eight pieces, with 6 and 7 skipped.
- **Three new pieces**: `6-ideation/` (from the How Might We questions to three to five
  concepts, minimal), `7-validation/` (a task script, sessions `VAL-00X` with evidence
  `VAL-00X-NN`, and its own debrief) and `8-report/` (the final write-up). Phases 6 and 7 are on
  demand; the report is not. Their folders are not created at install: each is born with its
  first `--add`. `--add` takes `ideation`, `validation_guide`, `validation_capture`,
  `validation_debrief` and `report`, plus `validation-note|prep|feedback --name VAL-...`.
- **The ID prefix is checked by type**: `interview-*` needs `INT-`, `observation-*` needs
  `OBS-`, `validation-*` needs `VAL-`.
- `process-interview` also processes validation sessions and keeps a `validations` counter apart
  from `interviews`. `7-validation/tasks.md` is a second hard budget (100 lines), like the
  master guide.
- **One file, one job.** Every template opens with an `Owns:` / `Does not own:` line, and the
  editor routes by it. `profiles.md` keeps only the interview subject: the user vs. customer table
  moves to the brief ("Who is who"), the coverage plan to `knowledge.md` (a "who answers it"
  column) and the sample risks to `recruiting.md`. `--migrate` does not move sections of an
  existing project: the editor proposes it at the next gate.
- **The plan is a contract.** Each row of `plan:` and each row of the brief's `## Plan` table
  carries `owner`, `reviewers` (who validates or helps), `how` (the method in one line) and
  `done_when`. The Guide asks for them when it proposes the plan, checks a piece against its
  `how` and `done_when` before closing its gate (recommending `Deepen` or logging the deviation
  rather than closing in silence), and logs any change of method as a course change in
  `_engine/decisions.md`.
- **Shareable snapshots.** At every gate close and at the end of a session the Guide offers a
  single self-contained HTML in `share/YYYY-MM-DD-<slug>.html`, built only from project files
  (`templates/share.html`, plus a one-pager for the plan close). It never carries assumptions,
  co-pilot readings or quotes without consent. `share/` has no budget and is not routed.
- **`--migrate` leaves an old v3 folder fully upgraded.** It adds to `state.yaml` the `plan` step,
  phases 6-8 with their steps and the `validations:` counter, and to `budgets.yaml` the new
  budgets (the summary's budget is repointed to `8-report/`). Existing statuses and values are
  never changed. If the brief already has a `## Plan`, the default plan is not written: `plan:`
  stays empty and the Guide builds it from the brief, which wins on conflict. User files are not
  touched; the editor proposes the `Owns:` lines at the next gate.
- The plan's `piece` is a phase or a step; progress is `done` over the rows that are not
  `skipped`; the Guide checks `interviews.target` and `validations.target` against the plan.

### Changed

- **The one-page summary moves from `5-debrief/output/summary.md` to `8-report/summary.md`**, and
  now covers every round that ran, field and validation. `--add summary` is now `--add report`.
  **Migration:** run `init_project.py --migrate` on an existing v3 folder. It moves the file,
  repoints it in `state.yaml`, adds the default plan, never overwrites an existing
  `8-report/summary.md` and never deletes. Running it twice changes nothing.
- The Guide's status shows `Step {i}/{pieces in the plan, skipped excluded}`, not "N/10".
- Ideation and testing are no longer "coming": they exist, in minimal form.

### Earlier in this release

First real run of the method, second round of fixes.

### Changed

- Live notes taken during an interview go at the top of its transcript in `4-field/_raw/`, as a comment block. They used to end up at the bottom of the master guide or in a separate file, detached from the conversation they came from. `process-interview` reads them first.
- Every file of an interview shares one base name, `INT-00X-name-surname-company`. The date moves to the index. A reader of `4-field/` sees who each interview was with, not an alias and a date.
- One transcript per interview. A relabeled transcript replaces the raw one instead of sitting next to it; the first real run left three files for one conversation.
- `count_interview.py` skips `#` lines and starts at `# === INTERVIEW START ===` (or `# === INICIO ENTREVISTA ===`), so live notes and small talk live in the same file without being counted.
- The folder can be named `discovery-<project>/`. `init_project.py` takes `--folder`, and finds a single renamed folder without it.
- "What would the ideal platform look like?" joins the questions to avoid: it asks the interviewee to design the product. Ask about their ideal month.
- Step 4a described the v2 folder layout. It now describes `4-field/`.
- **Transcripts are Markdown, not `.txt`.** One file per interview,
  `4-field/_raw/INT-00X-name-surname-company-transcript.md`: a header, `## Live
  notes`, `## Before the interview`, then `## Interview` (or `## Entrevista`),
  one turn per paragraph. `count_interview.py` starts counting after the
  `## Interview` / `## Entrevista` line, never counts a markdown heading or a
  blockquote line, and still keeps a line like `#1 is speed` because it is
  something someone said. The old convention (`#` comments, `# === INTERVIEW
  START ===`) still counts the same way, so nothing written under the old
  rule needs rewriting.
- **Interview feedback is one file per interview**, not one accumulating log.
  `4-field/feedback/0-README.md` explains how to read them (measured vs read,
  coverage reported never scored, one shared Measured table so files compare
  side by side); `4-field/feedback/INT-00X-name-surname-feedback.md` holds
  each interview's entry. The single `0-interview-feedback.md` grew unwieldy
  the moment more than a couple of interviews were in, and made it easy to
  paste one interview's feedback under the wrong heading.
- **Client material now lands where a human can see it.** Briefs, decks,
  canvases, spreadsheets and whiteboards go to `1-desk-research/sources/`.
  `_engine/sources/` is reserved for the assistant's own working material
  (councils, data-reviews, guide-versions); mixing the two made it impossible
  to tell, from the folder alone, what the project had been fed versus what
  the assistant had produced along the way.
- **Evidence IDs are per interview**: `INT-00X-NN` (`OBS-00X-NN` for an
  observation), not a global `EV-NNN` counter. Two interviews can now be
  processed in parallel without their evidence rows colliding on an ID.
  `templates/evidence.md` also says plainly that a quote is copied verbatim
  from the transcript, transcription errors included, and should be checked
  against it.
- **Per-profile interview guides are one whole guide each, never deltas.**
  `3a-guide.md` said the opposite (deltas against a base guide) while
  `templates/guide.md` already said "one guide each, whole. Not deltas."; the
  step file now agrees with the template it ships. `docs/method-architecture.md`
  had the same stale claim and is fixed too.
- `templates/interview-note.md` no longer suggests a filename
  (`YYYY-MM-DD_profile_eXX_notes.md`): the file's name is the interview's base
  name, same as the transcript and the feedback file, and there is nothing to
  choose.
- `count_interview.py`'s `guide_blocks_note` and `interview-rubric.md` now say
  plainly that keyword-based guide coverage both over-reports (a long
  transcript touches a block's title words by chance) and under-reports (a
  block covered in different words never matches). This was already an
  approximation; now the failure mode is documented on both sides, as an open
  issue, not redesigned.
- `patterns_es.py`'s `CONCRETE` anchors only had feminine last-time forms
  ("la última vez"). Added the masculine and other common forms: "el último",
  "el otro día", "ayer", "la semana pasada".
- `templates/interview-prep.md` opens with a reminder to check whether the
  previous interview's retro (its note's "Guide / method learnings" section)
  proposed guide edits that are still not applied, matching the Guide's
  "moment 2" of feedback in `discovery-guide/SKILL.md`.

### Added

- `_engine/skills/`, for project-level wrapper skills (for example, one that
  fetches transcripts from the team's recorder). They belong to the assistant,
  not the human, so they never land in a numbered phase folder.
- `init_project.py --add <item> --name <base>` materialises a per-interview or
  per-observation file (`interview-note`, `interview-prep`,
  `interview-feedback`, `observation-note`) at its real destination
  (`4-field/<base>.md`, `4-field/_prep/<base>-prep.md`,
  `4-field/feedback/<base>-feedback.md`), validated against
  `^(INT|OBS)-\d{3}-[a-z0-9-]+$` and never overwriting an existing file.
  `PER_ITEM` existed since v3 but nothing ever called it; the Guide and
  `process-interview` copied templates by hand instead, with no protection
  against clobbering. `discovery-guide/SKILL.md`, `process-interview/SKILL.md`
  and `4a-interview-capture.md` now point at the command instead.
- `init_project.py --add` on an aggregate step (`interview_capture`,
  `debrief`, whose `file:` in `state.yaml` lists more than one path) now runs
  each concrete step it stands for and reports each one, instead of failing
  with a bare "Unknown step" that sent you back to read `state.yaml` by hand.
  `--add start` / `--add design_challenge` now say plainly that their file,
  `1-desk-research/brief.md`, is created at install, not via `--add`.
- `init_project.py --project-name` sets `project_name` in `state.yaml`
  directly; it used to always fall back to the project root's folder name,
  which is rarely the name the user gave the project.
- `templates/interview-note.md` gets a "Guide / method learnings" section
  (questions left on the table, concrete guide edits proposed not applied,
  whether a part 2 is warranted), matching what `process-interview`'s step 6
  already asked for but the template never had a place to hold.

### Fixed

- `count_interview.py`'s label-learning regex had no turn boundary, so a
  single-line export (the whole call on one line, or two-space-separated
  turns) could learn garbage labels from a colon inside prose, or silently
  fold the interview into one speaker at 0%/100% share. A candidate label now
  only counts at start of line, after a sentence ends (`.?!…` + whitespace),
  or after 2+ spaces, and cannot itself contain `.?!`. If parsing still finds
  only one distinct speaker, the script now exits with the same kind of clear
  error as "no labels found", instead of reporting numbers for one voice.

## 3.0.0 - 2026-09-24

Breaking. `discovery/` is numbered by phase and grows as you go. Existing projects migrate with
`python3 scripts/init_project.py --project-root <path> --migrate`, which moves files and never
deletes them. v1 and v2 folders are both handled.

### Why

The folder installed 21 files and 1,430 lines of blank forms, in English, with no indication of
when each one is used. A real run logged "the texts were moved to Spanish by hand" and "do not
run --force: it overwrites the Spanish". Two of the four problems were of the method's own
making: the language feature was announced in three places and built in none, and every install
carried ~400 lines of generic method text that is identical in every project.

### Added

- `tests/test_init.py`. Twenty checks, standard library only. The repository had no tests and no
  CI, which is how two breaking releases shipped in two days without either one running a clean
  install against itself.
- `scripts/count_interview.py` and `scripts/patterns_es.py`. The numbers behind interview
  feedback come from counting a transcript, so two runs agree. Anything that cannot be counted
  is reported as uncounted; nothing is estimated. Handles both one-turn-per-line transcripts and
  the single-line exports recorders produce.
- `references/interview-rubric.md` and `references/interviewing.md`. Eleven criteria, each
  sourced, plus the generic method text that used to be copied into every project.
- `AGENTS.md` and `CLAUDE.md` inside `discovery/`. Without them the method only worked when the
  skill was installed globally: a fresh session opening the user's project found an unexplained
  folder.
- `--add STEP`, so creating a phase's file is deterministic instead of copied by hand.
- `--overwrite-modified`. `--force` now only re-copies untouched files.
- `detect_version()`, replacing `looks_like_v1()`. The old function answered yes/no, so a v2
  folder read as "not v1" and got the new layout planted beside the old one silently.
- A fourth job for the `editor`: empty `notes.md` at every gate. An item bound for a phase that
  has not started stays put under a heading naming it.
- `4b-observation.md`. `state.yaml` declared eleven steps against ten files; `guide_context` had
  no file and lived buried in the field checklist.
- Interview feedback at three moments, given by the Guide. No new agent: the Guide's own
  contract already describes a coach, and its menu stays at four actions.

### Changed

- Six files install, and two of them are the user's. Everything else is born when its step
  starts, written in the project's language.
- Five numbered phases: desk research, profiling, the guide, the field, the debrief. Recruiting
  moves into phase 2, because it is the only step that takes days rather than hours.
- Observation moves out of the field kit and into the field, where it belongs, with `OBS-` notes
  alongside `INT-` ones feeding the same evidence ledger.
- `guide.md` cut from 125 to 93 lines: questions only, under a hard 100-line cap. It is the file
  that grew to 257 lines on the first external run.
- `principles.md` split four ways. It was five documents stapled together, and `findings.md` —
  added the day before — repeated four of its seven sections.
- Six interview trays collapse into `4-field/_raw/`. The field index goes from 14 columns to 7.
- The per-interview prep sheet replaces the one-page cheatsheet. It carries no line cap but must
  mark every block with a priority and a time box, which is what makes a long sheet usable under
  pressure.
- The README drops "The method won't let you skip", which contradicted the paragraph after it.
  Two named entry points replace it: "I just want the guide" and "I already did the interviews".

### Fixed

- `--force` overwrote hand-translated files with the English templates.
- The init planted v3 beside a v2 folder without a word.
- `state.yaml` declared eleven steps and shipped ten.
- `guide.md` told you to duplicate a section per profile while `modules.md` said that is never
  done. One mechanism now: one guide file per profile.
- `observation.md` was titled `# Context Guide` inside. Name and content never matched.
- The shipped guide template broke the line budget the method shipped alongside it.

### Planned, not in this release

- **Ideation** and **testing** as phases 6 and 7. Phase 5 already names the handoff; the
  method stops at the principles rather than pretending otherwise.

### Removed

- `field-kit/cheatsheet.md`, `field-kit/modules.md` and `interviews/README.md`. Migration
  archives the first two under `_engine/sources/` rather than deleting them.

## 2.0.0 - 2026-09-23

Breaking. The `discovery/` folder is reorganized into three zones. Existing projects migrate with
`python3 scripts/init_project.py --project-root <path> --migrate --lang <lang>`, which moves files
and never deletes them.

### Why

The first external run of the method produced a 257-line interview guide: it had absorbed the field
checklists, the recruiting logistics, the coding definitions and the assumption IDs, while the files
that own that content stayed empty. The guide was unusable in the room it was written for. Nothing
in the method routed the overflow or capped the growth.

### Added

- `field-kit/cheatsheet.md`. One page, hard budget, what the interviewer holds during the interview.
- `field-kit/modules.md`. Per-profile variants as deltas against the base guide.
- `findings.md`. The distilled layer between atomic evidence and design principles.
- `_system/budgets.yaml`. A line budget per zone 1 file.
- `agents/editor.md`. Runs at every gate: distills, routes misplaced content, trims by budget.
  It shows its plan, waits for an OK, and never deletes.
- A canonical path and an application ledger for council output. A council can return thirteen
  recommendations and have twelve applied; the ledger keeps the missing one visible.
- `language` in `state.yaml` and `--lang` on init.
  ⚠ **Corrected in 3.0.0.** This entry claimed the scaffolding was written in the project's
  language. It was not: `--lang` only stamped a string into `state.yaml` while the English
  templates were copied over it. The claim also appeared in `SKILL.md` and in a comment in
  `state.yaml`. Three places said it; no code did it.
- A field signal in `state.yaml`: from stage 07 on, zero interviews past `stale_after_days` is
  reported before anything else.
- `VERSION` and this changelog.

### Changed

- `discovery-document.md` is dissolved. Its summary moved to `challenge.md`, its index to
  `README.md`, its state to `_system/state.yaml`. State now lives in exactly one place.
- Renamed for clarity: `users-and-sample.md` to `who-to-talk-to.md`, `recruitment.md` to
  `recruiting.md`, `synthesis.md` to `principles.md`, `decision-log.md` to `decisions.md`,
  `interview-guides.md` to `field-kit/guide.md`, `field-checklist.md` to `field-kit/checklist.md`,
  `guide-context.md` to `field-kit/observation.md`.
- `evidence-ledger.md` moved from `interviews/` to `_system/`.
- Stage 06 gained a "What does NOT go here" routing table, a rule about renumbering reordered
  blocks, and gate questions about misplaced content.

### Fixed

- `SKILL.md` referenced `_template-notes.md`; the file has always been `_notes-template.md`.
- `inputs/` was created and documented nowhere. Removed; `interviews/incoming/` and `_sources/` cover it.
