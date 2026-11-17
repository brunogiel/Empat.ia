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

It is numbered by phase, and it grows as the user goes. Eleven files exist at install and seven of them are the user's (the map, the brief, a short README in each of phases 2 to 5, and the field drawer `4-field/notes.md`); every other file is born when its step starts, written in the project's language:

- **Zone 1**, the root and `3-guide/`: what the user opens. Line-budgeted, kept short.
- **Zone 2**, `_engine/`: state, assumptions, decisions, evidence, budgets, project-level skills (`_engine/skills/`). The assistant's workspace.
- **Zone 3**, `_engine/sources/`: the assistant's own raw and long material (councils, data-reviews, guide-versions). Consulted, not read.

`1-desk-research/sources/` is a different thing: client material as-is (briefs, decks, canvases,
spreadsheets, whiteboards), kept so a human can see what the method was fed. `4-field/` keeps
field material and belongs to none of the three zones.

Project state lives in `_engine/state.yaml` and is never repeated in a second document.
Zone 1 files carry a line budget in `_engine/budgets.yaml`; the `editor` enforces it at each gate
by moving the excess to `_engine/sources/`, never by deleting it.

Documents:

- `README.md`: the map of the folder and what to open now.
- `1-desk-research/brief.md`: goal, maturity level, context, scope and the design challenge.
- `3-guide/guide.md`: one page, what the interviewer holds during the interview.
- `3-guide/guide.md`: per-profile variants are a whole copy of the guide each, never deltas.
- `5-debrief/findings.md`: what is emerging, distilled, pointing at evidence IDs.
- `_engine/budgets.yaml`: line budget per file the user opens. `3-guide/guide.md` is a hard cap.
- `_engine/state.yaml`: current step, status, available agents and recommended action.
- `_engine/assumptions.md`: active, validated and discarded assumptions.
- `_engine/decisions.md`: decisions and tradeoffs.
- `1-desk-research/knowledge.md`: knowns, unknowns and learning goals.
- `1-desk-research/market.md`: market research with sources.
- `2-profiling/profiles.md`: roles, participant profiles and sample.
- `3-guide/guide.md`: the script, questions only.
- `3-guide/expert-consult.md`: optional, the short guide for consulting experts (witnesses, not users); what comes out is a hypothesis for the field.
- `_engine/meeting-coverage.md`: step 1f, what each client meeting said and which file absorbs it, approved before anything is edited.
- `2-profiling/recruiting.md`: outreach, channels and recruiting tracker.
- `3-guide/process.md`: before, during and after fieldwork.
- `4-field/0-observation-plan.md`: observation, experts, analogies and immersion.
- `5-debrief/principles.md`: the deliverable. Design principles traceable to evidence.
- `5-debrief/presentation.md`: step 5b, on demand. The types of slide, the sample and its gate, and the client's questions against the deck.
- `5-debrief/meeting-claims.md`: optional. What the researcher said in a client meeting, set against the evidence.
- `4-field/0-index.md`: intake and processing flow for field material.
- `4-field/0-index.md`: interview tracker, files, consent and gaps.
- `_engine/evidence.md`: atomic evidence by interview before synthesis.
- `templates/interview-note.md`: structured note template for each interview.

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

**Two modes.** A council either generates (lateral voices produce readings and never review) or reviews (experts of the trade judge a piece and never invent). Review mode hands every reviewer the closed decisions of `_engine/decisions.md`: a reviewer may flag a decision's cost, never reopen it. The reviewer roles live inside `agents/council.md`, not as agent files.

## Model Checkers

Every check done by a model, in any phase, follows two rules. The full text lives in `workflows/user-discovery/steps/5a-debrief.md`, "Every model checker".

- **Seeded.** The checker first runs on a copy with planted errors. If it misses one, its verdict counts for nothing.
- **The right tier.** Inventory and binary questions go to a small fast model. Questions of sense (does the quote support the claim, is a "why" exaggerated, does a clip say what its caption says) go to a mid or strongest model. Synthesis is one author, the strongest model.

## Sub-stages And Owners

A step that runs in sub-stages (today the debrief, 5a.0 to 5a.4) keeps one mark per sub-stage under `substeps:` in `state.yaml`. Nothing in a sub-stage starts until the one before it is `done` or `skipped`. A piece worked by two threads has one owner of its structure, and the structure closes before anyone fills it. Two consecutive sub-stages may share one checkpoint (compressed mode) when it is declared in `_engine/decisions.md` first. The checkpoint can be a page: `templates/checkpoint.html`.

## Presentation, Pieces Built By Script And Rewrites

Step 5b shows the debrief to the client. It builds a sample (one slide of each type, real content) and the researcher accepts it before the deck exists. The report (8a) takes what the client already accepted as it was presented and adds the validation as a new layer.

A piece that is generated has a Markdown canonical, and a script builds the HTML or the deck from it: cuts by number or pattern, the map from IDs to titles by script, no vocabulary replacement on a literal quote, fidelity checked by `check_share.py` (`--titles-from`, and `--source` on the Markdown). If another model rewrites a text, it returns a table of changes (original, proposal, reason), never the file. The full text lives in `workflows/user-discovery/steps/5b-presentation.md`.

## Method Sources

See `docs/source-distillate.md` for the generalized method principles used to shape templates and workflow steps.
