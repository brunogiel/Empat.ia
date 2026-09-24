# 1d, Knowledge base

## Objective

Organize what the user brings: what we know, what we don't know, and what we want to learn.

## Method notes

- Preserve the entirety of relevant content.
- Separate facts, opinions, hypotheses, and assumptions.
- Don't turn raw material into closed insights.
- Keep redundancies if they support traceability.
- Allow contradictions.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add knowledge_base`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/1-desk-research/knowledge.md`
- `discovery/_engine/assumptions.md`
- `discovery/1-desk-research/brief.md`
- `discovery/_engine/state.yaml`

## Structure

- What we know.
- What we don't know.
- What we want to learn.
- Contradictions or tensions.
- Co-pilot readings.
- Pending raw material.

## Using the template

In `1-desk-research/knowledge.md`, use tables with IDs:

- `S-*` for things we know.
- `NS-*` for things we don't know.
- Assumptions that must also move to `_engine/assumptions.md`.

Don't synthesize prematurely. This stage clears the ground.

## Gate

Suggested action:

- `Advance` if there are clear questions for research.
- `Deepen` if material is missing or there is vagueness.
- `Question` if assumptions are being treated as facts.
- `Council` if the contradictions define the focus.
