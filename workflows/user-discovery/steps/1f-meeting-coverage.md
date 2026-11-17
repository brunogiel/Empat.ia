# 1f, After a meeting with the client

## Objective

When a meeting with the client brings something new, decide where every point lands **before** any file is edited, and let the researcher approve that map.

## Method notes

- This step is on demand and repeats: run it after each meeting that brings new information, at any point of the project, not only in phase 1.
- It sits between "the minute exists" and "the files are edited". Skipping it has two usual results: the brief swells with the client's data, and a point said in passing never reaches the file that needed it.
- The matrix is the plan of edits. A file is touched only for a row the researcher has seen.
- A point can have one home. If it seems to belong in two files, one of them links to the other.
- It is not the debrief's `coverage-matrix.md`, which places findings against the challenge. This one places what was said in a meeting against the files of the project.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is created at install except phase 1's brief.

1. **[DET]** Create it, once:
   `python3 <method-root>/scripts/init_project.py --project-root . --add meeting_coverage`
   The file holds one block per meeting. For the next meeting you add a block; you do not run the command again.
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in the language of the repository.

## Documents to touch

- `discovery/_engine/meeting-coverage.md`
- Then, only for the approved rows, the file each row points at (`1-desk-research/brief.md`, `1-desk-research/knowledge.md`, `_engine/assumptions.md`, `_engine/decisions.md`, `1-desk-research/market.md`, `2-profiling/profiles.md`, `3-guide/guide.md`, and so on).
- `discovery/_engine/decisions.md`: one line per meeting.

## Process

1. **[DET]** Add the block for this meeting: date, who was there, where the minute or recording is kept.
2. **[LATENT]** Take the inventory. One row for every point the meeting brought: a fact, a figure, a request, a decision, a constraint, a correction to something we believed. Add one row for each thing the team was already thinking that the meeting touches, marked *carried*, so it gets a home too.
3. **[LATENT]** Give each row one destination: the file that owns that kind of content, read from its `Owns:` line. A client request goes to the brief's "What the client asked for" table, one row per request. Detail, figures and names of the client's systems go to `knowledge.md`, never the brief. A row that fits nowhere says "stays here".
4. **[LATENT]** Mark the tensions: every row that contradicts what a file says today, with the file and the line it contradicts. Do not settle a tension by editing. Put it in front of the researcher.
5. **[LATENT]** Show the matrix. If the host can show inline visuals, show it as a table with the status column. Wait for the researcher's OK, and change what they change.
6. **[DET]** Only then edit the destination files, row by row, and mark each row `done`. A row that cannot be absorbed stays `pending: why`.
7. **[DET]** Check that no row lacks a status, that no file changed for a point without a row, and that the brief stayed an index (its line budget is in `_engine/budgets.yaml`).
8. **[DET]** Log one line in `_engine/decisions.md`: the date, the rows done and pending, the tensions still open.

## Quality checklist

- Every point of the meeting has a row, including the ones that went by in passing.
- Every row has one destination or "stays here".
- Every tension names the file and line it contradicts.
- The researcher approved before the first edit.
- The brief gained requests and decisions, not the client's data.

## Gate

This step has no gate. Suggested action when you close a block:

- `Advance` if every row is `done` or `pending: why`.
- `Deepen` if a row has no home you can name.
- `Question` if a tension changes something already decided.
