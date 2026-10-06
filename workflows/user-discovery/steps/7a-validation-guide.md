# 7a, Validation guide

## Objective

Build the task script for putting a prototype in front of people: what you ask
them to do, what you watch for, and what counts as stuck. Validation looks at what
people do, not at what they say.

Empat.ia guides the validation. It does not build the prototype.

## Method notes

- Give a situation, never the steps. Say nothing about how.
- Watch what they do first; ask why after.
- One task tests one bet from the ideation.
- Use the same kind of people as the field, so the two rounds can be compared.
- Don't lead: do not name the feature before they find it.

## First, the file of this step

The file this step writes does not exist yet, and neither does its folder. That is
the design: `7-validation/` is born with this step.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation_guide`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/7-validation/tasks.md`
- `discovery/6-ideation/concepts.md`
- `discovery/_engine/assumptions.md`
- `discovery/_engine/decisions.md`
- `discovery/_engine/state.yaml`

## Process

1. **[LATENT]** Take the bets from `6-ideation/concepts.md`, or from whoever did the
   ideation.
2. **[LATENT]** Write one task per bet, as a situation. For each: what to watch for,
   when it is done, and what a stuck person looks like.
3. **[DET]** Keep it inside 100 lines. This is a hard budget, like the master guide.
4. **[LATENT]** More than one profile? One whole script per profile, never deltas.
5. **[LATENT]** Set `validations.target` in `_engine/state.yaml`.

## Quality criteria

- A person who is not you can run a session from the script and its prep sheet.
- Every task tests a named bet.
- No task contains the steps.

## What does NOT go here

| If you wrote it in the tasks | It belongs in |
|---|---|
| The concept and why it was chosen | `6-ideation/concepts.md` |
| The assumptions being tested | `_engine/assumptions.md`, and the tasks link to them |
| Recruiting, scheduling, incentives | `2-profiling/recruiting.md` |
| Version history of the script | `_engine/sources/guide-versions/` |

## Gate

Suggested action:

- `Advance` if every task tests a bet and nobody needs the steps.
- `Deepen` if bets are missing a task.
- `Question` if a task leads the person.
- `Council` if the prototype could be read as the answer to a different question.
