# 4a, Interview capture

## Objective

Organize notes, transcripts, and observations without synthesizing prematurely.

This stage exists so the user can drop in all the real field material, and the Guide turns it into a processable base, without losing the source or inventing conclusions.

## Method notes

- Find a comfortable way to drop in and read photos, ideas, interviews, and notes.
- Lay everything out visibly, person by person.
- First organize by interviewee; then cross profiles.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add field_index`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/4-field/`
- `discovery/4-field/0-index.md`
- `discovery/4-field/0-index.md`
- `discovery/_engine/evidence.md`
- `discovery/1-desk-research/knowledge.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/assumptions.md`

## Folder structure

- `incoming/`: raw material the user brings.
- `transcripts/`: clean transcripts per interview.
- `notes/`: structured notes per interview.
- `artifacts/`: photos, screenshots, documents, or shared materials.
- `consent/`: consent, restrictions, and privacy notes.
- `processed/`: auxiliary derivatives if needed.

## Rules

- Preserve verbatim quotes.
- Don't mix users without identifying the source.
- Mark interviewer observations separately from what the user said.
- Save name, date, profile, and context.
- Use `_notes-template.md` for each interview.
- Record moments of tension, surprise, or emotion.
- Capture tools, documents, spaces, and workarounds.

## Process

1. Ask the user to drop all the material in `incoming/`.
2. Assign an ID per interview: `INT-001`, `INT-002`, etc.
3. Fill out `index.md` with metadata, files, and status.
4. Copy or move clean transcripts to `transcripts/`.
5. Create a structured note in `notes/` using `_notes-template.md`.
6. Save materials in `artifacts/` and consents in `consent/`.
7. Extract atomic evidence into `_engine/evidence.md`.
8. Mark gaps before moving to synthesis.

## How to process each interview

Per interview, separate:

- Verbatim quotes.
- Reported facts.
- Interviewer observations.
- Workarounds.
- Moments of emotion, tension, or surprise.
- Contradictions.
- New questions.
- `Co-pilot reading` whenever there is inference.

Don't cross patterns until you have processed interview by interview.

## Gate

Suggested action:

- `Advance` if there is enough material to cross patterns.
- `Deepen` if key interviews are missing.
- `Question` if there is clear sampling or capture bias.
- `Council` if strong contradictions appear.

## Checklist before synthesizing

- Each interview has metadata.
- There are verbatim quotes.
- Observations are separated from interpretations.
- `index.md` lists files, consent, and gaps.
- `_engine/evidence.md` has evidence per interview.
- There are enough profiles to cross patterns, or gaps are recorded.
