# Method Architecture

Empat.ia (Design with Empathy and AI) is an installable user discovery method for AI coding assistants. Its central deliverable is a set of **design principles** traceable to evidence: actionable decision rules the user applies to product choices, communication with users and strategic priorities.

## Layers

1. Main skill: `discovery-guide`.
2. Workflow steps: `workflows/user-discovery/steps/`.
3. Agents: `agents/`.
4. Templates: `templates/`.
5. Project initializer: `scripts/init_project.py`.

## State

Project state lives in `discovery/_system/state.yaml`.

Valid statuses:

- `not_started`
- `capturing`
- `drafted`
- `validated`
- `advanced_with_assumptions`

## Persistent Documents

The work lives in `discovery/`.

It has three zones, split by who opens a file and when:

- **Zone 1**, the root and `field-kit/`: what the user opens. Line-budgeted, kept short.
- **Zone 2**, `_system/`: state, assumptions, decisions, evidence, budgets. The assistant's workspace.
- **Zone 3**, `_sources/`: raw and long material. Consulted, not read.

`interviews/` keeps field material and belongs to none of the three.

Project state lives in `_system/state.yaml` and is never repeated in a second document.
Zone 1 files carry a line budget in `_system/budgets.yaml`; the `editor` enforces it at each gate
by moving the excess to `_sources/`, never by deleting it.

Documents:

- `README.md`: the map of the folder and what to open now.
- `challenge.md`: goal, maturity level, context, scope and the design challenge.
- `field-kit/cheatsheet.md`: one page, what the interviewer holds during the interview.
- `field-kit/modules.md`: per-profile variants as deltas against the base guide.
- `findings.md`: what is emerging, distilled, pointing at evidence IDs.
- `_system/budgets.yaml`: line budget per zone 1 file.
- `_system/state.yaml`: current step, status, available agents and recommended action.
- `_system/assumptions.md`: active, validated and discarded assumptions.
- `_system/decisions.md`: decisions and tradeoffs.
- `_sources/knowledge-base.md`: knowns, unknowns and learning goals.
- `_sources/market-research.md`: market research with sources.
- `who-to-talk-to.md`: roles, participant profiles and sample.
- `field-kit/guide.md`: the script, questions only.
- `recruiting.md`: outreach, channels and recruiting tracker.
- `field-kit/checklist.md`: before, during and after fieldwork.
- `field-kit/observation.md`: observation, experts, analogies and immersion.
- `principles.md`: the deliverable. Design principles traceable to evidence.
- `interviews/README.md`: intake and processing flow for field material.
- `interviews/index.md`: interview tracker, files, consent and gaps.
- `_system/evidence-ledger.md`: atomic evidence by interview before synthesis.
- `interviews/notes/_notes-template.md`: structured note template for each interview.

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
