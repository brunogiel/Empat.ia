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

- `4-field/INT-00X-name-surname-company.md`: one structured note per interview.
- `4-field/_prep/`: the per-interview prep sheets.
- `4-field/_raw/`: one transcript per interview, plus photos, documents and consent notes.
- `4-field/0-index.md`: the tracker.

## Rules

- Preserve verbatim quotes.
- Don't mix users without identifying the source.
- Mark interviewer observations separately from what the user said.
- Live notes (taken during the call by whoever led or sat in) go **at the top of the transcript**, in the same file in `4-field/_raw/`, under a `## Live notes` heading. Never in the master guide, never in a separate document: the note stays attached to the conversation that produced it.
- Transcripts are Markdown (`-transcript.md`), not `.txt`: a header, `## Live notes`, `## Before the interview`, then `## Interview` (or `## Entrevista`), one turn per paragraph.
- Save name, date, profile, and context.
- Use the `interview-note` template for each interview.
- Record moments of tension, surprise, or emotion.
- Capture tools, documents, spaces, and workarounds.

## Process

1. Ask the user to drop all the material in `4-field/_raw/`.
2. Assign an ID and base name per interview: `INT-001-name-surname-company`.
3. Fill out `0-index.md` with metadata and status.
4. Keep one transcript per interview in `_raw/`, named after the base name.
5. Create a structured note in `4-field/` from the `interview-note` template.
6. Save materials and consent notes in `_raw/` under the same base name.
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
