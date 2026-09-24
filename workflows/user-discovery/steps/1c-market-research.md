# 1c, Market research

## Objective

Do deep market research when it applies, using current web and citable sources.

## Method notes

- Market research helps partially answer the design challenge.
- It can look at reports, trends, market size, players, benchmarks, and relevant geographies.
- It does not replace talking to users.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add market_research`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/1-desk-research/market.md`
- `discovery/1-desk-research/brief.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`

## Web rule

This step requires current web search. If there is no web, leave status as `not_started` or `capturing` and explain the blocker.

## Responsible agent

Delegate to `deep-market-researcher`.

Minimum output:

- Scope.
- Research questions.
- Market and trends.
- Players and alternatives.
- Customer/user behavior.
- Risks and constraints.
- Implications for interviews.
- Sources.

## Using the template

Fill out `1-desk-research/market.md` with tables of:

- Findings with data, source, and implication.
- Players, substitutes, and benchmarks.
- Assumptions to validate with users.

Don't close the stage until you turn the research into new questions for interviews.

## Gate

Suggested action:

- `Advance` if the research already guides user questions.
- `Deepen` if sources or scope are missing.
- `Question` if the research pushes a solution without user evidence.
- `Council` if the industry is complex or the data is contradictory.

If the target market is SMEs, add `sme-owner` to the council to translate market data into operational reality.
