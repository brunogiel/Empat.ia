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

## First, the files of this step

The files this step writes do not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create what the sub-stage needs, with `--add`:
   `python3 <method-root>/scripts/init_project.py --project-root . --add findings`
   Keys: `findings`, `synthesis_log`, `analysis_guide`, `case_sheet`, `card_sort`,
   `coverage_matrix`, `verification_log`.
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

1. **[DET] Quotes exist.** `python3 <method-root>/scripts/verify_quotes.py` looks up each quote in the interviewee's own channel only. Verdicts: OK, LITERAL~ (close, shows the real text), INTERVIEWER (the interviewer said it), FAIL (discard). A literal pass is necessary and **not enough**.
2. **[LATENT] Context, always ±6 lines.** For every quote that supports something that leaves the sub-stage, read the six lines before and after. Look for leading questions, cuts that change the meaning, contradictions with the person's own behaviour, and professional-jargon voice.
3. **[LATENT] Does the quote support the claim?** One checker per sheet or section, with a seeded control: plant a few known errors in a copy (a swapped quote, an exaggerated "why"). If the checker misses them, the gate is worthless. Use a mid model; a small one misses exaggerations buried in long text. Or ask a narrower question ("does the quote say 'only', 'always' or 'never'?").
4. **[LATENT] Qualitative to quantitative, on everything that leaves.** Not just quotes: catch generalisations ("most"), rankings presented as measured, counts that do not match the sheets, assumptions nobody said, and the researcher's opinion presented as a finding.
5. **[LATENT] Devil's advocate before sharing.** The strongest case against the conclusion, using quotes only. Verdict: nothing / nuance / rewrite. The orchestrator discards the advocate's own exaggerations.
6. **[DET] Write it down** in `5-debrief/verification-log.md`: what each checker looked at, what it caught, what changed, what was kept and why.

Not every project needs every step. A small project runs 1, 2 and 6; anything that leaves the team runs all.

## Fan-out per sub-stage

If the platform allows subagents, run in parallel. Otherwise run the voices in series, each with a clean context (the shared instructions file plus only its own input).

| Sub-stage | Agents | Tier | Input | Isolation |
|---|---|---|---|---|
| 5a.1 case sheets | one per person | mid model | one transcript plus `templates/case-sheet-instructions.md` | each sees only its own person |
| 5a.1 quote and support checks | one per sheet | small fast model for the binary check, mid model for exaggeration | one sheet plus its transcript | one sheet each |
| 5a.2 lateral guests (optional) | 2 to 3 | mid model | sheets or patterns, never raw transcripts | none sees the others |
| 5a.2 cross | 1 | strongest model | all sheets | single author |
| 5a.3 insights | 1 author | strongest model | patterns plus sheets | single author |
| 5a.3 lateral readings | 2 to 3 | mid model | the insights only | none sees the others |
| 5a.3 adversarial | 1 | mid model | insights plus quotes | does not see the author's reasoning |
| 5a.4 principles and HMW | 1 | strongest model | validated insights | single author |

Shared instructions live in a file; the prompt of each agent only says whose turn it is. That saves tokens and avoids drift between agents. **Anti-pattern:** handing full transcripts to the lateral guests.

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
4. **Card sort, read as triangulation, not ranking** (`templates/card-sort.md`). First what matters to the person and why (card to quote), then how they grouped. Three states per card: placed with a reason, placed silently, unplaced. Record who gave the meaning (the person or the interviewer), when it was said, their own vocabulary, cards added live, co-placement and what the deck lacked. Said is not placed. **Never average positions.**
5. Run the standard checker (steps 1 to 4).

- **Researcher sees:** the sheets, the failed or doubtful quotes with their context, and the card-sort reading.
- **Researcher decides:** which quotes and sheets stand. Advance / Deepen (go back to the transcript or re-interview) / Question / Council.

### 5a.2 Patterns

1. **Inductive affinity first.** Group the evidence by what it says, before touching the research questions. Labelling straight against the questions groups with the frame you already had.
2. Only then map the groups to the research questions.
3. **Axes of divergence are mandatory.** Each is a tension with every person placed on it, each with a quote. Show them, never average them. Propose a profile only when two or more people fall in the same combination of axes.
4. Identify strong patterns, weak signals, outliers, and contradictions. Where it helps, build a mini-journey per case: where the person learns about the subject, in the order it appears, and where the studied product sits. Per case, not invented per profile.
5. **Optional lateral guests** (see Council): they see sheets or patterns only, generate readings, never judge. The orchestrator crosses their output with the sheets and keeps only what traces back.
6. Fill `5-debrief/coverage-matrix.md`: each finding placed in a part of the design challenge and a research question as answered / partial / gap. The gaps feed the next round.
7. Run the checker (steps 1, 2 and 4) on the patterns.

- **Researcher sees:** patterns, axes with people placed, the coverage matrix, the laterals' surviving readings.
- **Researcher decides:** which patterns hold, which axes are real. Advance / Deepen / Question / Council.

### 5a.3 Insights

1. **One author** writes the insights, as readings, not summaries.
2. **Laterals with other voices** read the insights, not the evidence, and push back.
3. **Adversarial:** a reviewer builds the strongest case against each insight from quotes.
4. Run the full checker (steps 1 to 5) on everything that will leave the team.

- **Researcher sees:** the insights, the lateral and adversarial readings, the checker's table.
- **Researcher decides:** rewrite, soften or keep each insight. Advance / Deepen / Question / Council.

### 5a.4 Principles, HMW and the validation guide

1. Derive design principles. Give each an ID that `6-ideation/concepts.md` can cite.
2. Formulate HMWs, one per principle where it earns one.
3. List open questions and evidence gaps.
4. Close the coverage matrix. Its gaps become **objectives and ideas for the validation round**: what we set out to find out, entry scenarios, possible A/B comparisons, and what to keep in mind with a small n (one difference at a time, alternate the order, watch what people do).
5. Trace each principle to evidence IDs and run the checker (steps 1, 2, 4 and 6).

- **Researcher sees:** the principles with their evidence, the HMWs, the matrix with its gaps, the validation guide.
- **Researcher decides:** which principles are final. Advance / Deepen / Question / Council.

## Quality criteria

- An insight is not a summary: it is a new perspective on the problem.
- Each insight needs a fact or quote traceable to `_engine/evidence.md`.
- The principles are design rules, not features.
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

For the lateral guests of 5a.2 and 5a.3, use the "lateral guests" variant in `agents/council.md`.

## Gate

Each sub-stage closes with the checkpoint above. Suggested action:

- `Advance` if the checker passed and the researcher agrees.
- `Deepen` if quotes, sheets or interviews are missing.
- `Question` if conclusions are being invented or the framing is off.
- `Council` if the synthesis needs to be put under tension.

Before closing a sub-stage, update `_engine/state.yaml`. Before the debrief leaves the team in any form, the cuali-to-cuanti and devil's-advocate checks must have run and be logged.
