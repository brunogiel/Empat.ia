# 5a, Debrief

## Objective

Turn interview material into **design principles** traceable to evidence. The principles are the central deliverable of Empat.ia: decision rules the user will apply to product, communication, and strategy.

Insights, patterns, HMWs, and top quotes are material that supports the principles, not the final output. If a principle can't be traced back to facts or quotes, it isn't a principle: it's an opinion.

The debrief runs in **sub-stages, each with its own gate**: 5a.0 analysis guide, 5a.1 evidence, 5a.2 patterns, 5a.3 insights, 5a.4 principles. Nothing reaches the end without passing through what came first.

## Method notes

- From data to insight, from insight to principle: every leap rests on evidence.
- Each insight and each principle must come from facts or quotes.
- Cross profiles.
- Identify strong patterns, weak signals, outliers, and contradictions.
- Derive design principles and HMWs from evidence.
- Principles are actionable design rules, not features or opinions.
- Don't make things up.
- **The checker filters, the researcher decides.** Every sub-stage ends with a human checkpoint. No sub-stage closes on the checker's verdict alone.
- **Fan out where there is independence or divergence; synthesise with one author.** One person per agent (case sheets, per-sheet checks) is independence. Lateral guests, a panel, a devil's advocate are divergence. The synthesis is written by one hand.
- **One owner per piece.** If two threads or agents work on the same piece (a table of patterns, the insights, the principles), its structure has one owner and is closed **before** anyone fills it. Two hands that fill a structure while it is still moving produce two versions that never merge.
- **One sub-stage at a time.** Nothing in a sub-stage starts until the one before it is `done` (or `skipped`) in `substeps:` of `_engine/state.yaml`. A number that reaches an analyst or the researcher before its checker has run goes marked **preliminary**, or does not go. At a gate, "if you don't decide, I'll continue" does not exist: no answer is not an Advance.

## First, the files of this step

The files this step writes do not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create what the sub-stage needs, with `--add`:
   `python3 <method-root>/scripts/init_project.py --project-root . --add findings`
   Keys: `findings`, `synthesis_log`, `analysis_guide`, `case_sheet`, `card_sort`,
   `coverage_matrix`, `verification_log`, `meeting_claims`.
2. **[DET]** Write each in the **language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/5-debrief/analysis-guide.md` (optional)
- `discovery/5-debrief/cases/` (`_case-sheet.json`, `_instructions.md`, then one `INT-*.json` case sheet per person)
- `discovery/5-debrief/findings.md`
- `discovery/_engine/synthesis-log.md`
- `discovery/5-debrief/coverage-matrix.md`
- `discovery/5-debrief/verification-log.md`
- `discovery/5-debrief/meeting-claims.md` (if the researcher gave conclusions in a client meeting)
- `discovery/5-debrief/principles.md`
- `discovery/4-field/card-sort.md` (if card sorting ran)
- `discovery/4-field/0-index.md`
- `discovery/_engine/evidence.md`
- `discovery/1-desk-research/brief.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`
- `discovery/_engine/assumptions.md`

## The standard checker

Every gate runs the same checker. Deterministic first; a model only where there is interpretation.

1. **[DET] Quotes exist.** `python3 <method-root>/scripts/verify_quotes.py` looks up each quote in the interviewee's own channel only. It reads interviews and validation sessions (`VAL-`), with or without a clock prefix on each line. Verdicts: OK, CUT? (the words are there, but a negation sits right before them, a "but" right after, or the fragment starts or ends mid-sentence: the real context is shown, you decide), LITERAL~ (close, shows the real text), INTERVIEWER (the interviewer said it), FAIL (discard), VETOED (the ledger marks it as vetoed: it must not be in the file you are checking). A literal pass is necessary and **not enough**: a fragment can match word for word and still say the opposite once the sentence around it is gone.
1b. **[DET] Counts and universals.** `python3 <method-root>/scripts/check_counts.py <every file that leaves>` runs after the quote check and before any model reads. It compares each "X of N" with the number of different people in the pattern it sits next to (the support table in `findings.md`, see 5a.2), lists every universal ("nobody", "everyone", "most", "always", "never", "5 of 5") with the transcript lines that could break it, and refuses a success tick on N of 2 or less. It also reads the transcripts, not only the evidence ledger, because a ledger inherits the gaps of whoever filled it. It runs on every file that leaves the team, the HTML included. Run it again on every file that already left whenever a gate changes a count or a pattern.
2. **[LATENT] Context, always ±6 lines.** For every quote that supports something that leaves the sub-stage, read the six lines before and after. Look for leading questions, cuts that change the meaning (every CUT? from step 1 first), contradictions with the person's own behaviour, and professional-jargon voice. **A video or audio clip is a quote.** Read the transcript lines around the cut (±6 lines) and compare what the clip actually says with the slide title or the finding it illustrates: a clip is chosen for its image or its tone, and it can say something else, or the opposite, once the surrounding lines are read. **A quote or clip that fails this check is vetoed.** Mark its row `vetoed: <reason>` in the Use column of `_engine/evidence.md`. A vetoed quote supports nothing: if an analyst brings it back, the orchestrator takes it out without arguing it. Step 1 turns that rule into an error: `verify_quotes.py` gives VETOED, and exits with a failure, when a vetoed quote shows up in a file it checks (`--scan` reads Markdown and HTML such as `findings.md`, `principles.md` and `share/`).
3. **[LATENT] Does the quote support the claim?** One checker per sheet or section. It is a model checker, so the two rules of "Every model checker" below apply: a seeded control that it catches, and a mid or strong model.
4. **[LATENT] Qualitative to quantitative, on everything that leaves.** Not just quotes: catch generalisations ("most"), rankings presented as measured, counts that do not match the sheets, assumptions nobody said, and the researcher's opinion presented as a finding.
5. **[LATENT] Devil's advocate before sharing.** The strongest case against the conclusion, using quotes only. Verdict: nothing / nuance / rewrite. The orchestrator discards the advocate's own exaggerations. Seeded and tiered like every model checker.
6. **[DET] Check what already went out.** `python3 <method-root>/scripts/check_share.py` runs the quote check (cut and vetoed quotes), the count check, the internal-marks brake and the codes brake on every file in `share/` (and `8-report/`) in one command. It exits with an error if any of them fails. Run it at **every gate**, not only before a new send: a fix made in `findings.md` does not reach a page that already left until this run finds it there. The brakes it adds:
   - **Internal marks.** A line or table row tagged `[not for the report]`, or a block between `<!-- not for the report -->` and `<!-- end not for the report -->`, in any canonical file (`evidence.md`, `findings.md`, the synthesis log) must not appear in a shared piece. The tag itself must not either.
   - **Codes.** A shared piece holds no evidence ID (`INT-003-12`, `PAT-01`), no hypothesis code (`A-023`), no short code (`H04`) and no working label in capitals (`TODO`, `GATE 2`). Names that only look like a code go in `_engine/share-allow.txt`.
   - **No speaker notes** in a slide file, unless you pass `--keep-notes`.
7. **[DET] Write it down** in `5-debrief/verification-log.md`: what each checker looked at, what it caught, what changed, what was kept and why. Then update the table **What already went out**: one row per file that left (file, to whom, when, what it claims, state). The state is `current`, `outdated` or `corrected and resent`. **If a finding you corrected at this gate appears in a row, mark that row `outdated` in the same step and decide whether to resend.** `check_share.py` lists the files that are missing from the table (NOT_LOGGED) and the ones still `outdated` (OUTDATED).
8. **Apply the devil's advocate in the same step.** What the advocate corrects (a count, a claim, a quote) goes into the findings at this gate, with the log row, before the checkpoint. A correction left for later is a correction the next send will not carry.

Not every project needs every step. A small project runs 1, 2 and 7; anything that leaves the team runs all, and step 6 runs at every gate once something has left.

### Every model checker: seeded, and the right tier

This is the one place where the rule lives. Steps 3, 4 and 5 above, and the model checkers of 7c, 8a and the guide gate (3a, 7a), all point here.

1. **No seed caught, no gate.** Before a model checker runs on the real material, plant known errors in a **copy** (a swapped quote, an exaggerated "why", a count that differs from its pattern, a clip that says something else than its caption). Run the checker on the copy. If it misses a seed, its verdict on the real material counts for nothing: change the checker (a stronger model, a narrower question) and seed again. Log, per checker, "seeds caught: X of Y" in `5-debrief/verification-log.md`. A gate whose checker has no seeded run is not closed, in any phase.
2. **The tier follows the kind of question.**

| Kind of question | Tier | Examples |
|---|---|---|
| Inventory and binary questions | small fast model | Is this name in the file? Does the quote contain "only", "always" or "never"? Is every sheet present? |
| Questions of sense | mid or strongest model | Does the quote support the claim? Is a "why" exaggerated? Does a clip say what its caption says? Does a rule follow from its insight? Cuali-to-cuanti. Devil's advocate. |
| Synthesis | strongest model, one author | Patterns across sheets, insights, principles. |

A small model never runs a check of sense: it misses an exaggeration buried in long text and says "OK" with the same confidence. If a small model must be used, cut the question until it is binary.

## Fan-out per sub-stage

If the platform allows subagents, run in parallel. Otherwise run the voices in series, each with a clean context (the shared instructions file plus only its own input).

| Sub-stage | Agents | Tier | Input | Isolation |
|---|---|---|---|---|
| 5a.1 case sheets | one per person | mid model | one transcript plus `templates/case-sheet-instructions.md` | each sees only its own person |
| 5a.1 quote and support checks | one per sheet | small fast model for the binary check, mid model for sense and exaggeration | one sheet plus its transcript | one sheet each |
| 5a.2 lateral guests (optional) | 2 to 3 | mid model | sheets or patterns, never raw transcripts | none sees the others |
| 5a.2 cross | 1 | strongest model | all sheets | single author |
| 5a.3 insights | 1 author | strongest model | patterns plus sheets | single author |
| 5a.3 lateral readings | 2 to 3 | mid model | the insights only | none sees the others |
| 5a.3 adversarial | 1 | mid model | insights plus quotes | does not see the author's reasoning |
| 5a.4 principles and HMW | 1 | strongest model | validated insights | single author |
| 5a.4 cold read | 2 to 3 readers | mid model, or people outside the project | one principle each time: title, rule and HMW only | none sees the rest of the debrief or the others |
| 5a.4 chain validation | 1 | mid model | patterns, insights and principles, plus the seeded copy | does not see the author's reasoning |

The Tier column follows the table in "Every model checker"; every row that checks something runs with its seeded copy. Shared instructions live in a file; the prompt of each agent only says whose turn it is. That saves tokens and avoids drift between agents. **Anti-pattern:** handing full transcripts to the lateral guests.

## Process

### 5a.0 Analysis guide (optional)

Before analysing, the researcher writes down, in `templates/analysis-guide.md`: what they learned in the field, what to look for, which biases to watch, and **the refuter**: the observation that would topple their own hypothesis. A reviewer then hunts for those quotes on purpose.

- **Checker:** [LATENT] a reviewer looks for the refuting quotes and reports what turned up. [DET] none.
- **Researcher sees:** the guide and the refuting quotes found.
- **Researcher decides:** keep, soften, or drop the hypothesis. Then Advance / Deepen / Question / Council.

### 5a.1 Evidence

1. Review `4-field/0-index.md`: what is ready, what is missing.
2. Fill `_engine/evidence.md` from processed interviews only.
3. **Case sheets, one person per isolated agent** (`templates/case-sheet.json`, instructions in `templates/case-sheet-instructions.md`). Every datum carries its quote and line number. Each sheet ends with questions to go back with.
4. **Card sort, read as triangulation, not ranking** (`templates/card-sort.md`). First what matters to the person and why (card to quote), then how they grouped. Three states per card: placed with a reason, placed silently, unplaced. Record who gave the meaning (the person or the interviewer), when it was said, their own vocabulary, cards added live, co-placement and what the deck lacked. Said is not placed. **Never average positions.** **Count first how many sessions completed the exercise, by prompt version, and compare with the minimum the guide declared.** Under the minimum the verdict is "not enough": the sort is written up as a lead for the next round and feeds no pattern, insight or principle.
5. Run the standard checker (steps 1 to 4).
6. Hand the analysts the **clean evidence**: `_engine/evidence.md` without the vetoed rows. A vetoed row stays in the ledger so nobody finds the quote again and brings it back; it never goes into the input of an affinity analyst or a lateral guest.

- **Researcher sees:** the sheets, the failed or doubtful quotes with their context, and the card-sort reading.
- **Researcher decides:** which quotes and sheets stand. Advance / Deepen (go back to the transcript or re-interview) / Question / Council.

### 5a.2 Patterns

1. **Inductive affinity first.** Group the evidence by what it says, before touching the research questions. Labelling straight against the questions groups with the frame you already had.
2. Only then map the groups to the research questions.
3. **Axes of divergence are mandatory.** Each is a tension with every person placed on it, each with a quote. Show them, never average them. Propose a profile only when two or more people fall in the same combination of axes.
4. Identify strong patterns, weak signals, outliers, and contradictions. Where it helps, build a mini-journey per case: where the person learns about the subject, in the order it appears, and where the studied product sits. Per case, not invented per profile.
5. **Optional lateral guests** (see Council): they see sheets or patterns only, generate readings, never judge. The orchestrator crosses their output with the sheets and keeps only what traces back.
6. Fill `5-debrief/coverage-matrix.md`: each finding placed in a part of the design challenge and a research question as answered / partial / gap. The gaps feed the next round.
7. Give every pattern an ID (`PAT-01`, `PAT-02`...) in the "Patterns that repeat" table of `findings.md`, and write its evidence in the Evidence column. That table is the **support table**: `check_counts.py` counts the different people in each row, and every "X of N" written anywhere else is checked against it.
8. Run the checker (steps 1, 1b, 2 and 4) on the patterns.

- **Researcher sees:** patterns, axes with people placed, the coverage matrix, the laterals' surviving readings.
- **Researcher decides:** which patterns hold, which axes are real. Advance / Deepen / Question / Council.

### 5a.3 Insights

1. **One author** writes the insights, as readings, not summaries.
2. **Laterals with other voices** read the insights, not the evidence, and push back.
3. **Adversarial:** a reviewer builds the strongest case against each insight from quotes.
4. **No strong pattern without an insight.** Every pattern held by 3 or more people hangs from an insight (the insight cites its `PAT-` ID), or carries one line saying why it does not: `PAT-07: no insight, because it only describes the setting.` **[DET]** `python3 <method-root>/scripts/check_counts.py --orphans` lists the patterns that have neither. A strong pattern nobody read is the kind of gap a reader finds and the checker of a single insight never does.
5. Run the full checker (steps 1 to 5) on everything that will leave the team.

- **Researcher sees:** the insights, the lateral and adversarial readings, the orphan patterns, the checker's table.
- **Researcher decides:** rewrite, soften or keep each insight. Advance / Deepen / Question / Council.

### 5a.4 Principles, HMW and the validation guide

1. Derive design principles. Give each an ID that `6-ideation/concepts.md` can cite.
2. Formulate HMWs, one per principle where it earns one.
3. List open questions and evidence gaps.
4. Close the coverage matrix. Its gaps become **objectives and ideas for the validation round**: what we set out to find out, entry scenarios, possible A/B comparisons, and what to keep in mind with a small n (one difference at a time, alternate the order, watch what people do).
5. Trace each principle to evidence IDs and run the checker (steps 1, 1b, 2, 4, 6 and 7).
6. **[LATENT] Cold read.** Before the principles close, two or three readers who have seen nothing else read each principle **alone**: title, rule and HMW, nothing around it. Pick people who are not in the project: someone from the client side, a designer, an editor who cares about clarity. Each says in their own words what the rule asks the team to do. A principle that needs the rest of the debrief to be understood, that two readers read differently, or that says what another principle already says, is rewritten or merged. Words only the team uses ("the scale", "the layer") are the usual cause.
7. **[LATENT] Seeded chain validation.** One checker walks the whole chain, facts to patterns to insights to principles. Each principle follows from its source insight, each insight from patterns, and the same thing carries the same number at all three levels. Control: plant known errors in a copy first (a principle with no source insight, an insight whose count differs from its pattern, a rule that contradicts the insight it cites). If the checker misses one, the check is worth nothing and nothing it passed counts.

- **Researcher sees:** the principles with their evidence, the HMWs, the cold readers' notes, the chain checker's table, the matrix with its gaps, the validation guide.
- **Researcher decides:** which principles are final. Advance / Deepen / Question / Council.

## Quality criteria

- An insight is not a summary: it is a new perspective on the problem.
- Each insight needs a fact or quote traceable to `_engine/evidence.md`.
- The principles are design rules, not features, and each one makes sense read alone.
- Every count is the number of different people in its pattern's row; no strong pattern is left without an insight.
- HMWs shouldn't carry a hidden solution.
- A good HMW lets you imagine several solutions quickly.
- If evidence is missing, say so instead of filling in.
- Nothing leaves a sub-stage without the researcher's checkpoint.

## Required tables

| Evidence IDs | Pattern | Insight | Design Principle | HMW |
|---|---|---|---|---|

| Evidence gap | Impact on synthesis | Suggested action |
|---|---|---|

## Council

Suggest `Council` before closing 5a.3 or 5a.4 if:

- There are weak insights.
- There are relevant contradictions.
- There are design principles without evidence.
- The `_engine/evidence.md` shows important gaps.
- The user wants to prioritize opportunities.

For the lateral guests of 5a.2 and 5a.3, use the "lateral guests" variant in `agents/council.md` (generative mode: they produce readings, they never review). When a council **reviews** something instead (the insights, the principles, the report), it runs in the review mode of the same file: expert roles, the closed decisions of `_engine/decisions.md` handed to every reviewer, and a synthesis that counts how many reviewers said each thing.

## Gate

Each sub-stage closes with the checkpoint above. Suggested action:

- `Advance` if the checker passed and the researcher agrees.
- `Deepen` if quotes, sheets or interviews are missing.
- `Question` if conclusions are being invented or the framing is off.
- `Council` if the synthesis needs to be put under tension.

Each time a sub-stage closes that answers something the client asked for (5a.3 and 5a.4 at least), check "What the client asked for" in `brief.md`: each row is answered, or moved to the next round with one line.

To show the debrief to the client, continue with `5b-presentation.md`: a sample first, then the deck.

Before the researcher sees the checker's table, the Guide may build it as a **checkpoint page**: `templates/checkpoint.html`, one file the researcher opens and answers with buttons (see "The checkpoint page" below).

Before closing a sub-stage, update `_engine/state.yaml`: **both marks** (`current_status` and `steps.debrief.status`), the sub-stage mark under `substeps:`, and `next`. Then run `python3 <method-root>/scripts/check_state.py`; it fails if two marks disagree, or if `next` still asks for something that is done. Before the debrief leaves the team in any form, the cuali-to-cuanti and devil's-advocate checks must have run and be logged.

**Compressed mode (optional, declared).** Two consecutive sub-stages, for example 5a.3 and 5a.4, may close with one joint checkpoint. Declare it **before** starting them, as a course change in `_engine/decisions.md`. Both sub-stages run in full, every checker and every seed included; only the pause between them goes. Both marks in `substeps:` change in the same edit, after the joint checkpoint. The researcher can ask to split them at any point.

## After a client meeting: what I said vs. the evidence

**On demand.** In a meeting with the client the researcher often gives conclusions before the debrief is closed, and the client writes them down. Some of them the evidence does not hold. This step finds them while the notes are still fresh. It runs after the meeting, whichever sub-stage the debrief is in; it is a separate matter from step 1f, which decides where the meeting's *new information* lands.

1. **[DET]** `python3 <method-root>/scripts/init_project.py --project-root . --add meeting_claims` creates `5-debrief/meeting-claims.md` from `templates/meeting-claims.md`.
2. **[LATENT]** List every sentence the researcher said about the people studied, from the minutes of the meeting. One row each, in the researcher's words.
3. **[LATENT]** Cross each one against `findings.md` and `_engine/evidence.md`: **holds**, **holds with a nuance**, **does not hold**, **to confirm**. Count people, not mentions. A sentence that the evidence only holds for some of the people says so with the number. A model checker here is seeded and runs on the mid or strong tier, like any check of sense (see "Every model checker").
4. **[LATENT]** What the client asked and the meeting left open goes in a second table, with the same scale.
5. **When the client voted or ranked a list, cross against the whole list.** Take the list as the client gave it, item by item, not the part the draft already crossed. An item the evidence does not cover is a row that says "no evidence"; a missing row is a hole. A comparison built from the draft alone leaves out whatever the draft did not mention.
6. **A sentence that does not hold is corrected with the client**, in a short page built from the file (profiles, no names), after it passes cuali-to-cuanti and `check_share.py`. Fixing the files and saying nothing leaves the client with the old note. Log the correction in `_engine/decisions.md`, and mark any piece that carried the sentence `outdated` in **What already went out**.

## The checkpoint page

The checkpoint can be a page instead of a chat message. The Guide builds it from `templates/checkpoint.html` into `_engine/sources/checkpoints/YYYY-MM-DD-<sub-stage>-<round>.html`, in the project's `language`. It is a working file of the team: it never goes into `share/`, and it may carry the internal references that `check_share.py` forbids in a shared piece.

1. **[LATENT]** One card per item the researcher must decide. Each card names what it is about, carries its **reference** (a slide number or a section ID, so the researcher finds the place at once) and offers the four buttons: Advance, Deepen, Question, Council. A comment box sits under each.
2. **[LATENT]** A section **Already corrected** lists what the Guide fixed at this gate without asking (a count, a failed quote, a clip that did not say what its caption said): the reference, what it said before, what it says now. The researcher accepts or reverts each one. Facts are corrected there. Only a matter of judgement becomes a card.
3. **[DET]** The button **Copy decisions** puts every choice and comment on the clipboard as plain text. The researcher pastes it into the conversation, and the Guide applies it, logs it in `5-debrief/verification-log.md` and in `_engine/decisions.md`, and moves the marks in `state.yaml`.
4. **The second round brings only what is new.** An item already decided does not come back. The next page holds the cards that changed because of the decisions, and the corrections made since.
