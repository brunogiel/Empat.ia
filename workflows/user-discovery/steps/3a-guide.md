# 3a, The interview guide

## Objective

Build the field kit: what you actually take to a 45-60 minute interview.

## Method notes

- The interviewee is the expert.
- One person leads the conversation.
- Build one guide per type of user when the profiles are different.
- Context and daily life first; depth afterward.
- Ask about real experiences, not abstract opinions.
- Don't lead the answers.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add interview_guide`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/3-guide/guide.md`
- `discovery/3-guide/guide.md`
- `discovery/3-guide/guide.md`
- `discovery/1-desk-research/knowledge.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`

## Recommended structure

- Start and consent.
- Context and daily life.
- Current journey.
- Pains, motivations, and decisions.
- Current tools and alternatives.
- Ideal scenario.
- Closing.

## Using the template

In `3-guide/guide.md`:

- Write the questions the way you will say them out loud.
- Map each learning objective to questions. Keep that table: it is what makes the guide readable later.
- One line of intent per block, no more.
- Review forbidden questions and rewordings.

The guide should feel conversational. Don't turn it into a survey.

In `3-guide/guide.md`: one page, and it stays one page. Blocks with their timing, the
opening question of each, the allowed follow-ups, the words not to say. Nothing else.
This is the page you hold during the interview. The guide is what you read the night before.

In `3-guide/guide.md`: per-profile variants as deltas against the base guide, never a full
duplicated guide. Every block number a module references has to exist in `guide.md` today.

## What does NOT go here

The guide is the file that grows when nothing stops it. Everything below has its own home, and
leaving it in the guide means the file that owns it stays empty.

| If you wrote it in the guide | It belongs in |
|---|---|
| Pre-interview or field observation checklists | `3-guide/process.md` |
| Interview sequence, logistics, scheduling, incentives | `2-profiling/recruiting.md` |
| Coding definitions, how to classify evidence later | `_engine/evidence.md` |
| Assumptions and their IDs | `_engine/assumptions.md`, and the guide links to them |
| Version history, changelog, why the guide changed | `_engine/sources/guide-versions/` |
| Council output | `_engine/sources/councils/` |

Two more rules that come from real use:

- **If you reorder blocks, renumber them.** A guide that runs 1, 2, 3, 5a, 4, 5b reads fine on
  screen and traps you in the room. Modules that point at a block number break silently.
- **Assumption IDs are references, not content.** Write `A-012` and link. Don't paste what it says.

The `editor` runs at this gate and moves what is out of place. It never deletes.

## Council

Suggest `Council` if:

- The guide could lead responses.
- There is more than one profile.
- The challenge is sensitive or ethical.

Typical agents: `qualitative-researcher`, `uxer`, `sociologist`, `philosopher`. If you are interviewing SMEs, add `sme-owner`.

When a council reviews the guide, close it with the application ledger: a council can return
thirteen recommendations, twelve get applied, and the one left out is usually the structural one.

## Gate

Before closing, check:

- Does the guide have anything that belongs in another file?
- Does `cheatsheet.md` fit on one page?
- Can someone who is not you run this interview from these three files?

Suggested action:

- `Advance` if the guide covers what we want to learn without leading.
- `Deepen` if topics are missing.
- `Question` if it looks like solution validation.
