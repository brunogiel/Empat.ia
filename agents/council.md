# Council

## Role

Procedure to convene agents at important gates of the method.

The council exists so hard decisions are made under real pressure, not just with the opinion of whoever is at the wheel. Like an IDEO team, we mix profiles that don't usually think the same way: an economist who looks at incentives, an artist who questions the form, a philosopher who fights over the definitions, an SME owner who brings the street, and even a cab driver who brings the abstraction down to earth when everything gets too expert. Each voice brings a different tension. It doesn't replace the Guide's or the user's judgment. It surfaces the angles you can't see on your own.

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

## Guide's synthesis

- Agreements:
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
