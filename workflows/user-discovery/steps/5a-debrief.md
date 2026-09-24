# 5a, Debrief

## Objective

Turn interview material into **design principles** traceable to evidence. The principles are the central deliverable of Empat.ia: decision rules the user will apply to product, communication, and strategy.

Insights, patterns, HMWs, and top quotes are material that supports the principles, not the final output. If a principle can't be traced back to facts or quotes, it isn't a principle: it's an opinion.

## Method notes

- From data to insight, from insight to principle: every leap rests on evidence.
- Each insight and each principle must come from facts or quotes.
- Cross profiles.
- Identify strong patterns, weak signals, outliers, and contradictions.
- Derive design principles and HMWs from evidence.
- Principles are actionable design rules, not features or opinions.
- Don't make things up.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add findings`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/5-debrief/principles.md`
- `discovery/4-field/0-index.md`
- `discovery/_engine/evidence.md`
- `discovery/1-desk-research/brief.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`
- `discovery/_engine/assumptions.md`

## Process

1. Review `4-field/0-index.md` to see what material is ready and what gaps remain.
2. Review `_engine/evidence.md`.
3. Fill out a summary per interviewee only with processed interviews.
4. Group evidence by themes.
5. Cross profiles.
6. Identify patterns, outliers, and contradictions.
7. Write insights as readings, not as summaries.
8. Derive design principles.
9. Formulate HMWs.
10. List open questions.

## Quality criteria

- An insight is not a summary: it is a new perspective on the problem.
- Each insight needs a fact or quote traceable to `_engine/evidence.md`.
- The principles are design rules, not features.
- HMWs shouldn't carry a hidden solution.
- A good HMW lets you imagine several solutions quickly.
- If evidence is missing, say so instead of filling in.

## Required tables

| Evidence IDs | Pattern | Insight | Design Principle | HMW |
|---|---|---|---|---|

| Evidence gap | Impact on synthesis | Suggested action |
|---|---|---|

## Council

Suggest `Council` before closing if:

- There are weak insights.
- There are relevant contradictions.
- There are design principles without evidence.
- The `_engine/evidence.md` shows important gaps.
- The user wants to prioritize opportunities.

## Gate

Suggested action:

- `Advance` if the insights are traceable and useful.
- `Deepen` if quotes or interviews are missing.
- `Question` if conclusions are being invented.
- `Council` if the synthesis needs to be put under tension.
