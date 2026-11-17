# 5b, Presentation of the debrief

## Objective

Tell the client what the debrief found, in a deck or a page, without writing a second debrief. The presentation is a shorter view of material that already passed 5a: it adds no claim, and nothing in it is missing from its sources.

It is on demand: a project that never shows the debrief to anyone outside the team skips it. It starts after 5a.3 at the earliest (insights) and after 5a.4 when principles are shown. Whatever leaves goes through `check_share.py`, like every piece (see "Check what already went out" in `5a-debrief.md`).

## Method notes

- **A sample before the deck, always.** The whole deck is never built first. The researcher sees one slide of each type, with **real content**, and decides the format. Format changes come out of the sample, which costs minutes. They are expensive once the deck is full.
- **Draft, not mock-up.** An empty layout is a mock-up. A layout that already carries real data is a **draft**: call it that, and list what is still pending as concrete finishing work (clips, a priority, the annex, the checks). The researcher can decide on "draft, four things to finish". "A mock-up we still have to fill" says nothing.
- **A count is not a slide.** The method is qualitative. A count such as "3 of 5" does not appear as a chart, as filled circles, as a big number or as a headline. It goes to the annex or to the project's working notes (the support table in `5-debrief/findings.md`), never to the speaker notes of the final piece. The slide says what the people did and why it matters, in words. What the sample could not show goes to a section "what is left to measure", never into a figure that looks like a measurement.
- **The client's questions come first.** Every row of "What the client asked for" in `brief.md` is answered in the deck or moved to the next round with one line.
- **The client who runs the recruiting decides what is asked of them.** If the sample is already chosen, a question about "who should we recruit" is a closed matter and is not put to the client in the deck. The profile is asked as a **focus of the analysis** ("which of these people should the next round weigh most?"), never as a sample to redefine.
- **The deck says nothing the canonical files do not say.** Titles, rules and HMWs are copied word for word. Quotes are literal. Names follow `participant_names` in `_engine/state.yaml` and the consent record, as in `8a-report.md`.
- **No codes.** The deck holds no evidence ID, pattern ID or working label. They stay in the source (see "Pieces built by script").

## First, the file of this step

1. **[DET]** `python3 <method-root>/scripts/init_project.py --project-root . --add presentation` creates `5-debrief/presentation.md`: the types of slide, the sample and its gate, the coverage table and the list of what is pending.
2. **[DET]** Write it in the language set in `_engine/state.yaml`.
3. **[LATENT]** Pre-fill it from the brief and the debrief. An empty template is not a finished step.

## Documents to touch

- `discovery/5-debrief/presentation.md`
- `discovery/_engine/sources/presentation/` (the source Markdown and the generator script)
- `discovery/share/` (the deck, when it leaves)
- `discovery/5-debrief/verification-log.md`
- `discovery/1-desk-research/brief.md` (the rows of "What the client asked for")
- `discovery/_engine/decisions.md`
- `discovery/_engine/state.yaml`

## Process

1. **[LATENT] List the types of slide.** One row per kind of slide the deck will have (cover, context, a finding, an insight, a principle with its HMW, a quote, a decision for the client, the annex). Write the list in `presentation.md`, with the number of slides of each type.
2. **[LATENT] Build the sample.** One slide of each type, filled with real content taken from the canonical files, in the final format. It is a draft: say so, and list the pending work. A slide type with no real content yet is not in the sample: it is listed as not ready.
3. **[LATENT] Sample gate, with the researcher.** Show the sample (the checkpoint page of 5a works: `templates/checkpoint.html`, one card per slide type). Ask about the form of telling, not only the look: if two formats are offered, say whether they change **what the deck says and in what order** or only how it looks. Record the decision in `_engine/decisions.md`. **The rest of the deck does not start until the sample is accepted.** A format change after the gate is a course change, logged.
4. **[DET] Build the deck by script** from the source Markdown (see "Pieces built by script"). The script is run again after each edit; the deck is never edited by hand.
5. **[LATENT] Coverage check, before presenting.** Put the questions of the client (the rows of "What the client asked for" in `brief.md`, plus the questions asked in meetings, from `_engine/meeting-coverage.md`) against the deck, in the table of `presentation.md`: **question, found in slide, left out**. A question with no slide is either answered, or moved to the next round with one line, or left out on purpose with the reason. The same pass lists what the deck shows that nobody asked (an open hypothesis, a weak signal with no slide) so the researcher decides whether it stays. Never close it on "most questions are covered".
6. **[DET] Check the piece.** Run the scripts on the source and on the final piece:
   - `python3 <method-root>/scripts/check_share.py --share <deck-folder>` on the folder of the deck (quotes, counts, internal marks, codes, speaker notes), with `--titles-from 5-debrief/findings.md` so a title edited by hand in one slide and not in another is caught (TITLE_DRIFT).
   - `python3 <method-root>/scripts/check_share.py --source <source.md>` on the Markdown the deck is built from. The final piece has no pattern IDs, so `check_counts.py` cannot link its counts to a support table and says UNLINKED. The source does carry the IDs, so the count check has its full force there. Run both.
   Nothing leaves with an open MISMATCH, FAIL, VETOED or TITLE_DRIFT.
7. **[LATENT] Checks of sense.** Cuali-to-cuanti, devil's advocate and the ±6 lines of context of every quote and clip, as in "The standard checker" and "Every model checker" of `5a-debrief.md`. Both are seeded and run on the right tier.
8. **[LATENT] Simulated panel (optional).** Three or four voices read the deck, each alone: the client reader, an editor, someone from the studied audience. Hand every voice the closed decisions of `_engine/decisions.md`. **What two or more voices repeat is applied. What contradicts a decision of the researcher is reported, not applied** (a panel that asks for fewer slides does not reopen the format the researcher approved at the gate). The panel gives hypotheses; the researcher decides.
9. **Log and close.** Write the checks in `5-debrief/verification-log.md`, add the deck to the table **What already went out**, and mark the step in `_engine/state.yaml` (both marks) and run `python3 <method-root>/scripts/check_state.py`.

## Pieces built by script

A piece that is generated (a deck, a page, a one-pager) follows five rules. They hold in 8a too.

1. **The canonical is a Markdown file.** The deck or the HTML is generated from it by a script. The generated file is never the place where something is corrected: the correction goes to the Markdown, and the script runs again.
2. **Cuts are made by number or by pattern, never by hand.** The generator finds the section of a finding by its number or by a regular expression, not by the exact text of its title, and assigns a drawing or a layout by what the section contains, not by its position. A generator tied to the title or to the order breaks when someone reorders the findings or changes a word.
3. **The map from IDs to titles is made by script.** When findings are renumbered, a script writes the table "old ID, new ID" and rewrites every reference from it. A number does not go in a file name. Nobody renumbers by hand.
4. **A vocabulary replacement never runs on a literal quote.** Changing a term across the piece is a replacement that skips what is between quotation marks and what comes from a transcript. After it, a sentence that was true can turn false without containing the old word: search for the claim, not only for the word.
5. **Fidelity to the canonical is checked by script.** The titles of the piece against the canonical (`check_share.py --titles-from`), the quotes against the transcripts (`verify_quotes.py`), the counts against the support table (`check_counts.py`, run on the source). A reading by eye is not a check.

## When another model rewrites a text

Sometimes a second model rewrites the text of a deck or a report to improve the prose. A model that is asked for "the better version" returns a file that loses what the first one had: counts, profiles, instructions given to the participants, and decisions already closed.

1. The second model returns a **table of changes**, never the file: **original text, proposal, reason**. The orchestrator applies what is accepted, by script or by hand, in the canonical Markdown.
2. **[DET]** Quotes and numbers are checked by script, on the table: every number and every quoted fragment of the original must still be in the proposal, or the row says why it went.
3. **A change that loses a datum, or that reopens a closed decision, is not applied.** A closed decision is anything in `_engine/decisions.md` (a wording the researcher chose, a canonical HMW, a contrast the researcher kept). The researcher can reopen it; the rewriter cannot.
4. The table of changes is kept in `_engine/sources/`, with what was applied and what was not.

## Quality criteria

- The sample was shown, with real content, and accepted before the rest of the deck was built.
- A draft is called a draft, and what is pending is listed as finishing work.
- No count appears as a chart, a figure, circles or a headline. What could not be seen is in "what is left to measure".
- Every question of the client is found in a slide or moved with one line; what the deck leaves out is listed.
- The deck is built from a Markdown by a script, and `check_share.py` passes on the piece and on the source.
- A text rewritten by another model came back as a table of changes, and nothing in it lost a datum or reopened a decision.

## Gate

Suggested action:

- `Advance` if the sample was accepted, the coverage table has no open row and the checks passed.
- `Deepen` if a question of the client has no slide and no line saying where it goes.
- `Question` if the deck says more than the debrief does.
- `Council` if the deck feeds a decision that is hard to reverse.
