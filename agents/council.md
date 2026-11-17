# Council

## Role

Procedure to convene agents at important gates of the method.

The council exists so hard decisions are made under real pressure, not just with the opinion of whoever is at the wheel. Like an IDEO team, we mix profiles that don't usually think the same way: an economist who looks at incentives, an artist who questions the form, a philosopher who fights over the definitions, an SME owner who brings the street, and even a cab driver who brings the abstraction down to earth when everything gets too expert. Each voice brings a different tension. It doesn't replace the Guide's or the user's judgment. It surfaces the angles you can't see on your own.

## Two modes

A council runs in one of two modes. Never mix them in the same session.

| | Generative | Review |
|---|---|---|
| Used for | Opening ideas: readings, questions, analogies | Judging a piece that exists: a guide, insights, a report |
| Who sits | Lateral voices: artist, cab driver, philosopher, small-shop owner | Experts of the trade, and the simulated validator |
| What they do | **Generate.** They never review. | **Review.** They never invent new content. |
| Input | Sheets or patterns only | The piece, plus the closed decisions of the project |
| Section | "Variant: lateral guests" | "Review mode" |

A lateral voice that is asked to review gives a taste, not a check. An expert that is asked to generate repeats the field's habits. Keep each in its mode.

## Flow

1. The Guide formulates a neutral question.
2. **The Guide proposes 3-5 relevant agents with a short justification for each. The user confirms, adds, or removes before convening.** The rule: combine at least three different lenses (technical-analytical, human-qualitative, divergent or critical, optionally lateral non-expert).
3. Each agent answers independently following their file: tension, inputs, questions, output, and success metrics.
4. If there is significant disagreement, the Guide can ask for a short second round.
5. The Guide synthesizes:
   - agreements,
   - disagreements,
   - risks,
   - assumptions to log,
   - quality metrics that aren't being met,
   - recommendation,
   - suggested action.
6. The Guide updates `_engine/state.yaml`, `_engine/decisions.md`, or `_engine/assumptions.md`.

## Variant: lateral guests (generative mode)

A council variant for the debrief (5a.2 patterns, 5a.3 insights). The guests are lateral figures (a cab driver, a small-shop owner, a recruiter at a small firm) who see the material from outside the field. They **generate; they do not judge.**

Rules:

- **Restricted input.** Each guest sees only case sheets or patterns, never raw transcripts or the Guide's reasoning.
- **Isolated.** No guest sees another guest. If the platform allows subagents, run them in parallel; otherwise run them in series, each with a clean context.
- **A role with a restriction and a quota.** Give each guest one constraint on how they read (for example: only what a newcomer would notice) and a fixed number of outputs (for example: 3 readings, no more).
- **They produce readings and questions.** They never rank, approve or reject the researcher's findings.
- **The orchestrator does the crossing.** The Guide compares each reading with the sheets and keeps **only what traces back to evidence**. A reading that nothing supports is dropped and logged, not argued.
- Note in `5-debrief/verification-log.md` how many lateral readings survived the crossing. That number tells you whether the guests earn their cost.

## Review mode

The roles below are **roles inside this file**, not agent files. They are played by whoever runs the council, one clean context each. The Guide does not add a file to `agents/` for a reviewer.

### The closed decisions

Every reviewer receives, with the piece, the list of **closed decisions and discards of the project** from `_engine/decisions.md` (and the assumptions marked discarded in `_engine/assumptions.md`). The reviewer:

- **May flag the cost** of a closed decision ("this choice leaves X unanswered").
- **Never reopens it.** A review that argues again a question the researcher already closed is noise, and the orchestrator drops that part and says so.

### The expert roles

| Role | Reads for | Notes |
|---|---|---|
| Senior design researcher | Whether each insight and principle follows from the evidence, whether the leaps are marked, whether the rule can drive a design decision | Strongest model |
| Qualitative researcher | Sample, leading questions, quotes that carry more than they say, counts over people (`agents/qualitative-researcher.md`) | Strongest model |
| UX researcher of the domain | Whether the reading matches how the experience works in this domain, and what a practitioner would find naive (`agents/uxer.md`, set to the domain) | Mid model or stronger |
| Simulated client validator | The person who will approve the piece: would they sign it, what would they ask, what would make them stop reading | Mid model or stronger |

**A simulated role gives hypotheses, not evidence.** What the simulated validator says is a question to take to the real client; it never replaces the client's approval, and it never counts as a finding.

### The standard panel for the final report

For the report (8a), run seven readings, each by one reviewer alone:

| Reading | Looks for |
|---|---|
| Client reader | Someone from the client who saw nothing of the project. Can they say what was found and what happens next? |
| Editor | What can go: repetitions, hedges, anything that does not change a decision |
| Designer | Whether the page can be read at a glance, and whether the evidence is shown or only claimed |
| Person from the studied audience | Whether the people described would recognise themselves, and whether anything is said about them that they would not say |
| Verifier | Counts, quotes, dates and claims against their sources |
| Finder of the forgotten | What the evidence holds that the page leaves out: a pattern with no insight, a closed gap, a contradiction that vanished |
| Clip reviewer | Each video clip: what it says against its caption and the finding it illustrates (±6 lines of context) |

### The blind panel

When the panel reviews a script or a page before the field or the client (7a, 8a), it runs **blind**: no reviewer sees another reviewer's opinion, and none sees the Guide's reasoning. The orchestrator does the crossing. What several roles flag independently is the signal; what only one says is a lead to check.

### The synthesis

- Write "**N reviewers said this**" next to every point, so a point from one voice is not read as a consensus.
- Split the points in two. **Fact** (a wrong count, a quote that does not say that, a clip that says something else): the Guide corrects it, and lists it as corrected. **Judgement** (what to emphasise, what to cut, whether the tone fits): the Guide takes it to the researcher as a question and does not decide it.
- If the review uses a model to check facts, that model is seeded first (see "Every model checker" in `workflows/user-discovery/steps/5a-debrief.md`).

## Convening prompt

```text
Act as the agent convened within the Council.

Neutral question:
I'll give you a neutral question.

Available context:
I'll give you the available project context.

Respond from your specific tension. Don't seek consensus. Don't invent data. Separate evidence, inferences, and doubts. Flag any assumption that should be logged.

Format:
- Main reading
- Disagreement or tension
- Evidence used
- Assumptions or doubts
- Questions worth asking
- Concrete recommendation
- Confidence: low/medium/high
```

In review mode, add to the prompt:

```text
Closed decisions of this project (do not reopen; you may say what one costs):
I'll give you the list from _engine/decisions.md.

Mark each point as FACT (checkable against a source) or JUDGEMENT (a matter of taste or priority).
```

## Output

Save the synthesis to `discovery/_engine/sources/councils/{YYYY-MM-DD}-{n}.md`, where `{n}` is the count of councils held that day (the first is `1`, the second `2`, and so on).

```markdown
## Question

...

## Agents convened

- ...

## Perspectives

### Agent

...

## Closed decisions handed to the reviewers (review mode)

- ...

## Guide's synthesis

- Agreements (with "N reviewers said this"):
- Disagreements:
- Risks:
- Assumptions to log:
- Success metrics at risk:
- Recommendation:
- Suggested action:

## Application ledger

| Recommendation | Applied? | Where | If not: why |
|---|---|---|---|
```

A council can close with 13 recommendations and only 12 get applied. Without this ledger, the one left out disappears silently, and it's usually the most structural one. The Guide fills the table in as it applies or discards each recommendation, not at council time.

## Quality criteria

A good council doesn't seek quick consensus. It must:

- Show useful disagreements.
- Identify what evidence is missing.
- Recommend an action, not an endless list.
- Update documents if the state of the process changes.
- Keep the voices distinguishable without turning them into theater.
- In review mode, never reopen a closed decision, and never present one reviewer's point as a consensus.
