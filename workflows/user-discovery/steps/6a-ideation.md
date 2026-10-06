# 6a, Ideation

## Objective

Go from the How Might We questions of the debrief to three to five concepts, and
choose one with criteria that trace back to the design principles. This is the
minimal version of ideation.

## Method notes

- The questions come from the debrief. Do not invent new ones here.
- Three to five concepts. A concept is one way of answering a How Might We
  question, not a feature list.
- Choose with criteria taken from the principles, not from taste.
- If the ideation is done by another team, link their material and stop. The plan
  marks the piece `external`.
- Don't make things up: a concept that rests on something the evidence does not
  show is labelled as a bet.

## First, the file of this step

The file this step writes does not exist yet, and neither does its folder. That is
the design: `6-ideation/` is born with this step.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add ideation`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/6-ideation/concepts.md`
- `discovery/5-debrief/principles.md`
- `discovery/_engine/assumptions.md`
- `discovery/_engine/decisions.md`
- `discovery/1-desk-research/brief.md` (the plan, if its state changes)
- `discovery/_engine/state.yaml`

## Process

1. **[LATENT]** Copy the How Might We questions from the debrief into the file.
2. **[LATENT]** Diverge: propose concepts with the user. Aim for three to five.
3. **[LATENT]** Take the criteria from the principles. Write the principle next to
   each criterion.
4. **[LATENT]** Score each concept with a word (`meets`, `partly`, `does not`), not
   a number.
5. **[LATENT]** Choose one. Say why it won and what the others lost on.
6. **[LATENT]** List what has to be true for it to work. Each one becomes a thing
   to test in phase 7, or an assumption.

## Quality criteria

- Every criterion traces to a principle.
- The concepts differ in the bet they make, not in details.
- The choice can be explained to someone who did not take part.

## Council

Suggest `Council` if the choice is close, or if the concepts all lean the same way.
Typical agents: `artist`, `uxer`, `economist`, `technologist`.

## Gate

Suggested action:

- `Advance` if one concept is chosen, with criteria traceable to the principles.
- `Deepen` if the concepts are variations of one idea.
- `Question` if the criteria are taste and not principles.
- `Council` if two concepts are tied.
