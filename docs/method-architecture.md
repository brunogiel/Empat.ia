# Method Architecture

Empat.ia (Design with Empathy and AI) is an installable user discovery method for AI coding assistants. Its central deliverable is a set of **design principles** traceable to evidence: actionable decision rules the user applies to product choices, communication with users and strategic priorities.

## Layers

1. Main skill: `discovery-guide`.
2. Workflow steps: `workflows/user-discovery/steps/`.
3. Agents: `agents/`.
4. Templates: `templates/`.
5. Project initializer: `scripts/init_project.py`.

## State

Project state lives in `discovery/_engine/state.yaml`.

Valid statuses:

- `not_started`
- `capturing`
- `drafted`
- `validated`
- `advanced_with_assumptions`

## Persistent Documents

The work lives in `discovery/`.

It is numbered by phase, and it grows as the user goes. Six files exist at install and only two of them are the user's; every other file is born when its step starts, written in the project's language:

- **Zone 1**, the root and `3-guide/`: what the user opens. Line-budgeted, kept short.
- **Zone 2**, `_engine/`: state, assumptions, decisions, evidence, budgets. The assistant's workspace.
- **Zone 3**, `_engine/sources/`: raw and long material. Consulted, not read.

`4-field/` keeps field material and belongs to none of the three.

Project state lives in `_engine/state.yaml` and is never repeated in a second document.
Zone 1 files carry a line budget in `_engine/budgets.yaml`; the `editor` enforces it at each gate
by moving the excess to `_engine/sources/`, never by deleting it.

Documents:

- `README.md`: the map of the folder and what to open now.
- `1-desk-research/brief.md`: goal, maturity level, context, scope and the design challenge.
- `3-guide/guide.md`: one page, what the interviewer holds during the interview.
- `3-guide/guide.md`: per-profile variants as deltas against the base guide.
- `5-debrief/findings.md`: what is emerging, distilled, pointing at evidence IDs.
- `_engine/budgets.yaml`: line budget per file the user opens. `3-guide/guide.md` is a hard cap.
- `_engine/state.yaml`: current step, status, available agents and recommended action.
- `_engine/assumptions.md`: active, validated and discarded assumptions.
- `_engine/decisions.md`: decisions and tradeoffs.
- `1-desk-research/knowledge.md`: knowns, unknowns and learning goals.
- `1-desk-research/market.md`: market research with sources.
- `2-profiling/profiles.md`: roles, participant profiles and sample.
- `3-guide/guide.md`: the script, questions only.
- `2-profiling/recruiting.md`: outreach, channels and recruiting tracker.
- `3-guide/process.md`: before, during and after fieldwork.
- `4-field/0-observation-plan.md`: observation, experts, analogies and immersion.
- `5-debrief/principles.md`: the deliverable. Design principles traceable to evidence.
- `4-field/0-index.md`: intake and processing flow for field material.
- `4-field/0-index.md`: interview tracker, files, consent and gaps.
- `_engine/evidence.md`: atomic evidence by interview before synthesis.
- `templates/interview-note-template.md`: structured note template for each interview.

## Gates

Each gate ends with a recommended action:

- Advance
- Deepen
- Question
- Council

The guide can recommend moving forward with assumptions, as long as the assumptions are recorded and visible.

## Council And Agents

Agents are selectable perspectives with clear contracts. Each agent defines:

- The tension it brings.
- Inputs it needs.
- Questions it asks.
- Expected output.
- Success metrics.

**The Guide proposes, the user decides.** For each council, the Guide suggests 3-5 agents with a short justification each. The user can confirm, add or remove agents before the council is convened. `sme-owner` is proposed when small business reality affects adoption, budget, operations or decision-making. `philosopher` is proposed when the council needs to question assumptions, sharpen definitions or surface ethical risks. `cab-driver` is proposed when the council needs lateral thinking, plain language, analogies or a non-expert perspective.

## Method Sources

See `docs/source-distillate.md` for the generalized method principles used to shape templates and workflow steps.
