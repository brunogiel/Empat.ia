# Method agents

Agents are selectable voices. **The Guide proposes, the user decides.** The Guide suggests 3-5 agents based on the project and the gate, with a short justification for each. The user confirms, adds, or removes before convening them.

Rules:

- Don't convene all of them by default.
- Never propose `editor` for convening: it's not a voice, it runs automatically at every gate, not on demand.
- Don't propose `technologist` if the project has no relevant technology.
- Configure `industry-expert` at runtime with the actual industry.
- Propose `sme-owner` if the project touches SMEs, shops, small teams, local providers, or B2B sales to small businesses.
- Propose `philosopher` when there are invisible assumptions, loose definitions, or ethical risks.
- Propose `data-scientist` when there is available data that can complement interviews, risk of sample bias, or hypotheses with high conviction and little quantitative evidence.
- Propose `cab-driver` when the council or the discussion becomes too abstract, expert, or aligned. Useful to bring it down to scenes, surface analogies and simple language.
- Each agent returns a compact opinion, disagreements, and a recommendation.
- Each agent must fulfill its contract: the tension they bring, inputs, questions, output, and success metrics.
- The Guide synthesizes, recommends an action to the user, and, with their confirmation, updates documents.

## Base prompt to convene an agent

```text
Act as the selected agent within Empat.ia.

Context:
I'll give you the real project context, the current state of discovery, and any relevant documents.

Question:
I'll give you a neutral question to create tension.

Respond only from your role. Don't invent data. Separate evidence, inferences, and doubts. If context is missing, say it's missing and propose how to get it.

Format:
- Main reading
- Risks or disagreements
- Questions to investigate
- Concrete recommendation
- Confidence: low/medium/high
```

When using this prompt, the user or the Guide pastes the real context and question below the block.

## Roster

- `guide`: orchestrator and facilitator.
- `editor`: keeps discovery files distilled, routed, and within budget. Not a council agent: it is never convened, it runs on its own at every gate, before the Guide offers `Advance`.
- `qualitative-researcher`: interviews, sample, and traceability.
- `deep-market-researcher`: web research with sources.
- `uxer`: journeys, needs, and experience.
- `sociologist`: social context and culture.
- `economist`: incentives, costs, and economic behavior.
- `growth`: demand, channels, and language.
- `artist`: divergence, analogies, and non-obvious possibilities.
- `philosopher`: assumptions, definitions, and ethics.
- `technologist`: digital feasibility and systems.
- `data-scientist`: instrumentation, sample bias, and translation of signals into metrics.
- `industry-expert`: dynamic expert tuned to the industry.
- `sme-owner`: operational reality, cash, time, and adoption in SMEs.
- `cab-driver`: lateral, non-expert view, analogies, simple language, common sense.

## How to pick agents

Rule of thumb: combine three different lenses to force useful disagreement. A technical-analytical profile, a human-qualitative profile, and a divergent or critical profile. Optionally, add a lateral non-expert view.

Examples:

- B2B SME project: `sme-owner`, `economist`, `growth`, `qualitative-researcher`, `industry-expert`.
- Tech project: add `technologist`.
- Sensitive or social project: add `sociologist` and `philosopher`.
- Synthesis gate: `qualitative-researcher`, `uxer`, `sociologist`, and, if applicable, `sme-owner`.
- Market gate: `deep-market-researcher`, `industry-expert`, `economist`, `growth`.
- Project with available data or quantitative hypotheses: add `data-scientist`.
- When everything sounds too expert or abstract: add `philosopher` to question definitions, `artist` to open analogies, and `cab-driver` to bring it down to concrete scenes.
