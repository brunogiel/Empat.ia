# 8a, Report

## Objective

Write the final report of the whole project, on one page, for someone who read
none of it. Every plan closes with it, whatever pieces it used.

## Method notes

- It covers every round that ran: the field and, when there was one, the
  ideation and the validation.
- It is a shorter view of material that already exists. It adds no new claim.
- It is the only shareable artefact of the method: no raw quotes without consent,
  no internal notes, no project logistics.
- A skipped piece gets one line: what we assume by not doing it.
- A piece done by someone else gets a link to their result.
- **No codes.** The report is for a human. It never uses internal IDs (hypothesis codes such as
  A-023, evidence IDs such as INT-004-07): it states the idea in words. IDs stay in the internal
  files (evidence log, notes), where they trace each claim.

- **Names depend on the audience.** `participant_names` in `_engine/state.yaml` says, for each audience (internal team, client, public), whether the piece shows names, only profiles or nothing, who authorized it and when. Read it before writing any piece. If an audience is empty or the block is missing, show profiles and ask before a name goes in. A quote, a name and a clip live in separate fields of the page, so each is checked on its own.
- **Consent and contract come before names and clips.** A name or a clip goes in only if the person's row in the "Consent record" (`2-profiling/recruiting.md`) allows that exact use, the audience allows it, and the contract with the client allows it. The narrowest of the three wins.
- **Captures and clips are checked before they are used.** Each one is opened at no fewer than three frames (start, middle, end). Emails, phone numbers, passwords, names and the chats of the call are blurred. Prototype sessions used test data; if a real person's data shows in a frame, the capture is cut or not used.
- **A clip is chosen against the title it illustrates, not by topic.** Read the title of the slide or the finding, then the words the clip says: they have to support that title. A clip chosen for its image or its tone can say another thing. Only a clip whose check gave `ok: true` is embedded; one that gave `false` is fixed (a new cut) or left out, never explained away.
- **Answer the client's requests, and report the sample as it was.** Every row of "What the client asked for" in `brief.md` is answered in the page or moved to the next round with one line. If a profile had a focus (for example, people who do not know the brand) and the sample did not meet it, the page says so.
- **Nothing internal, no speaker notes.** Whatever a canonical file marks `[not for the report]` stays out of the page. A deck built from the report leaves without speaker notes unless the researcher asks for them.
- **Written for the client in design-thinking language.** "What we saw suggests", "in these cases", "to test". Never conclusions stated as certain. Design hints go as "could", not "must". Use profiles, not names or codes, in anything that can be forwarded.
- **Before it is shared or sent on, it passes the two scripts (quotes and counts) and two checks:** cuali-to-cuanti (generalisations such as "most", rankings shown as measured, counts that do not match the sheets, the researcher's opinion presented as a finding) and the devil's advocate (the strongest case against the conclusion, from quotes only). Log both in `5-debrief/verification-log.md`. Write the text in a source `.md` and build the HTML from it; run the quote check on the final HTML.

## Optional, on request: clips

Two scripts make clips when the report is shown to someone and the person's own words say more than a paraphrase. They help most with a prototype shown on screen. They are not needed to close this step.

1. **[DET]** `python3 <method-root>/scripts/locate_quotes.py` finds the minute of each quote in the video's clock (the recorder's transcript can be off by minutes) and gives the coverage per word.
2. **[DET]** `python3 <method-root>/scripts/cut_clips.py` cuts each located quote with a margin, burns the captions into the picture (not as a text track, so every viewer shows them), listens to the finished file again and marks `ok: true` or `false` by the coverage of the quote, and makes a thumbnail (a still frame) for a piece in PDF.

`ok: true` says the words of the quote are in the clip. It does not say the clip supports the title: that is the context check in the process below. Open each clip at three frames and blur before it goes in. They need ffmpeg and a local speech-to-text, and exit with code 2 and a message when either is missing. Details, limits and privacy: `docs/quote-clips.md`.

## First, the file of this step

The file this step writes does not exist yet, and neither does its folder. That is
the design: `8-report/` is born with this step.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add report`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Older projects

A project made before this piece existed may hold its summary in
`5-debrief/output/summary.md`. Run
`python3 <method-root>/scripts/init_project.py --project-root . --migrate`:
it moves the file to `8-report/summary.md` and never overwrites a file that is
already there.

## Documents to touch

- `discovery/8-report/summary.md`
- `discovery/5-debrief/principles.md`
- `discovery/5-debrief/findings.md`
- `discovery/7-validation/findings.md` (if validation ran)
- `discovery/6-ideation/concepts.md` (if ideation ran)
- `discovery/1-desk-research/brief.md` (the plan)
- `discovery/_engine/state.yaml`

## Process

1. Read the plan in the brief: which pieces ran, which were skipped, which were external.
2. Fill the page from the pieces that ran. Link the external ones.
3. Check every quote, name and clip against the consent record, the audience in `participant_names` and the client's contract.
   Check every row of "What the client asked for" in `brief.md`: answered, or moved to the next round.
4. Check the page fits its budget in `_engine/budgets.yaml`.
5. **[DET]** Run the scripts on the source `.md` and on the final HTML, before any model reads it:
   `python3 <method-root>/scripts/verify_quotes.py --file <page.html>` (and `--scan` on the `.md`)
   for quotes, cut quotes and vetoed ones, and `python3 <method-root>/scripts/check_counts.py <page>`
   for every "X of N", every universal and every success tick on 2 people or fewer.
   Nothing leaves with an open MISMATCH, FAIL or VETOED.
   Then run `python3 <method-root>/scripts/check_share.py` on the whole folder (`share/` and
   `8-report/`; use `--source` for a Markdown source that holds codes on purpose). It runs the same two
   checks on **everything that already went out**, and adds two brakes: anything marked
   `[not for the report]` in a canonical file, and any internal code or working label in capitals.
   It fails if one is found. A correction made for the report that touches an earlier piece marks that
   piece `outdated` in the **What already went out** table of `5-debrief/verification-log.md`.
6. Run the cuali-to-cuanti and devil's-advocate checks (see Method notes) as a gate before sharing. Both are model checkers: each runs on a mid or strong model, after a copy with planted errors showed it catches them (see "Every model checker" in `5a-debrief.md`). Every quote and every video clip in the page also gets the ±6 lines of context: the words the clip says against the title or the finding it illustrates.
7. **[LATENT] Review panel.** Convene the standard report panel of `agents/council.md` (review mode): seven readings of the finished page, each reviewer alone and blind to the others. Hand every reviewer the list of closed decisions from `_engine/decisions.md`. The orchestrator crosses the seven answers, corrects what is a fact in the same step, and takes the judgement calls to the researcher.
8. Mark the `report` piece `done` in the plan, and run `python3 <method-root>/scripts/check_state.py`.

## Quality criteria

- Someone who read nothing else can say what was found and what happens next.
- Nothing in it is missing from the sources it summarises.
- No quote lacks consent, and no name or clip appears that the consent record, the audience or the contract does not allow.
- Every request of the client is answered or moved with a line, and a focus the sample did not meet is named.
- Every capture and clip was checked at three frames and shows nothing sensitive.
- Every clip in the page has `ok: true` and was chosen against the title it illustrates, not by topic.
- No internal ID appears anywhere in the page, and `check_share.py` passes on the folder.
- No claim is stated more strongly than the evidence ("suggests", not "proves"); the two checks ran, caught their seeded errors and are logged.
- The review panel ran, and each of its findings is applied, asked of the researcher, or discarded with a reason.

## Gate

Suggested action:

- `Advance` if the page is complete and every claim traces to a source file.
- `Deepen` if a piece that ran is missing from the page.
- `Question` if the page says more than the evidence does.
- `Council` if the report will inform a decision that is hard to reverse.
