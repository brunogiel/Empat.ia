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

The file this step writes does not exist yet. That is the design: a step's file is
born when the step starts, never at install.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add interview_guide`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## First, the structure

Structure comes before questions. A guide whose sections change after the questions are written
gets written twice.

1. **[DET]** Save the researcher's braindump first, as it came, untidied, in
   `_engine/sources/guide-braindump.md` (a section of the project notes is fine if you prefer).
   It is raw input, not a draft. The editor does not empty it.
2. **[LATENT]** Say what this step offers (structure, then questions, then the two copies of the
   guide), and let the researcher dump what they already think. Propose only after that.
3. **[LATENT]** Propose the **sections table**: which sections, in what order, with minutes and
   priority, each one saying which learning objective of `knowledge.md` and which client request
   (the brief's "What the client asked for") it answers. Think each section from how the
   conversation feels to the person, not from what we want out of it. The minutes add up to the
   length of the session. Mark where each section came from: the braindump, what the project
   already knows, or a council.
4. **[LATENT]** To widen the options, run a council in **generative mode** (`agents/council.md`):
   three to five agents each read what the project knows and the braindump, and each brings
   sections with minutes and questions from its own tension. Unify them with the braindump.
   That council generates; it does not review. The review council comes after the questions.
5. **[LATENT]** Ask for an OK on the table. Change what the researcher changes.
   Only then write the questions, section by section. If the researcher wants to go straight to the
   questions, go: the structure step is offered, it never blocks.

The table is written at the top of `3-guide/guide.md`, right under the `Owns:` line.

## Documents to touch

- `discovery/3-guide/guide.md`
- `discovery/3-guide/expert-consult.md` (only if experts are consulted, see below)
- `discovery/_engine/sources/guide-braindump.md`
- `discovery/1-desk-research/knowledge.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`

## Recommended structure

A starting point for the sections table. Change it freely.


- Start and consent.
- Context and daily life.
- Current journey.
- Pains, motivations, and decisions.
- Current tools and alternatives.
- Ideal scenario.
- Closing.

## Using the template

In `3-guide/guide.md`, under the sections table:

- Write the questions the way you will say them out loud.
- Map each learning objective to questions in your head. The objectives and who answers them live in `1-desk-research/knowledge.md`, not in the guide.
- One line of intent per block, no more.
- Review forbidden questions and rewordings.

The guide should feel conversational. Don't turn it into a survey.

In `3-guide/guide.md`: one page, and it stays one page. Blocks with their timing, the
opening question of each, the allowed follow-ups, the words not to say. Nothing else.
This is the page you hold during the interview. The guide is what you read the night before.

**More than one profile? One whole guide per profile, never deltas.** Copy the file,
`guide-owner.md`, `guide-operator.md`. Each one is complete on its own and keeps the same
100-line hard cap; nobody running an interview should have to hold the base guide plus a delta
sheet to know what to ask.

## Rules for writing the questions

Twelve rules, each one learned from a guide that needed rewriting without it. Examples use an
invented booking app for a small clinic.

1. **Write the opening and the transitions as running text, in the interviewer's own voice.** Not
   bullets, not a neutral voice. If the user has a writing-style guide, use it. A guide in a voice
   you would never use becomes a script you read, and the person hears it.
2. **Do not assume the behaviour you want to measure.** Not "Which link do you send to the clinic?";
   first "What place does the booking page have when you arrange a visit?". Ask first whether the
   thing is in their life at all.
3. **No yes/no question without its follow-up, and no double question.** Write
   `Did you cancel anything? → Which one? What happened?`. This is about how the guide is written;
   the principle of open questions is in the skill's `references/interviewing.md`, and
   the feedback on an interview judges what came out, not the exact wording said in the room.
4. **Do not seed the concept you are looking for.** A question the client wants answered, such as
   "Was it clear what the clinic is for?", does not go as written. Ask it open: "What did that page
   make you think? Tell it to me as you would tell a friend."
5. **The interviewer chooses the case, with a criterion written in the guide.** "Choose the last
   visit you booked for yourself, not the most memorable one." Interviews can be compared only if
   the cases were chosen the same way.
6. **The stages of the journey are a note for the interviewer, never said aloud.** Out loud: "Tell me
   that story from the start. → And then?". If you hand the stages over, the person recites them.
7. **Bound the follow-up loops.** One question for every point of the journey; the full set only at
   the points that matter to the challenge. A full set of questions at every point of a long journey
   never fits in the time.
8. **Add conditional notes so nothing is asked twice.** *If this came up in question 2, start from
   what they said.* A note, in italics, on the question it affects.
9. **Episode before opinion, and anchored in what they already told you** ("in the visit you
   described..."). A pure-opinion question is allowed when the researcher wants one: mark it as
   opinion, and ask it last in its section.
10. **The journey covers the returns.** "Did you go back to any of it later? What for?" A thing that
    matters after the first contact is lost if the guide stops at the first contact.
11. **Protect the exercises from being cut.** See "Exercises" below.
12. **Write it so it can be read on a phone.** The `Owns:` line stays on top as in every template,
    the sections table right under it, then the questions. Interviewer notes in italics, on their
    own line. No version history in the file: it goes to `_engine/sources/guide-versions/`.

## Exercises

A card sort, a ranking, a board, a task: any exercise inside the guide follows these rules.

- **Pilot it before the field**, with someone inside the team, and write down the real minutes. A
  sort planned for a few minutes takes several times that with a full deck. A pilot teaches more than
  any review on paper.
- **The prompt is fixed in writing before the first session and never changes live.** Each change
  costs minutes, and the sessions before it stop being comparable. If it must change, it is a new
  version of the prompt (`templates/card-sort.md` keeps them) and the sessions are counted apart.
- **Give it realistic minutes**, from the pilot, in the sections table. A screen-shared session
  needs more than the same exercise in a room.
- **An exercise that feeds a decision is never cut for time.** Cut something else. Inside the
  exercise, cut first what feeds no decision (a top three, a second pass). Say in the guide which is
  which, on the line `Feeds:`.
- **Declare the minimum.** Write in the guide how many sessions must complete the exercise for a
  pattern to count. Below it, the debrief says "not enough" and the exercise stays a lead (see
  `5a-debrief.md`, 5a.1).

## Consulting experts is another piece

Sometimes the people closest to the thing (inside the client, or from the trade) know a lot about
the people you study. They are **witnesses, not users**, and they only see whoever reaches them.
Consult them with `templates/expert-consult.md`, not with this guide:

`python3 <method-root>/scripts/init_project.py --project-root . --add expert_consult`

A handful of direct questions, thirty minutes, the sample bias named at the top. What they say
enters `_engine/assumptions.md` as a hypothesis for the field, never as a finding.

## Two copies of the guide, made from the master

Once the master is approved, nobody retypes it:

- **For the client:** `python3 <method-root>/scripts/export_guide.py --project-root . --client`
  (add `--format html` for one printable page). It leaves out the `Owns:` line, internal IDs, the
  interviewer's notes and everything after the exercise annex, and it ends with an annex that shows
  the exercise. It stops if a code is left in the text: fix it in the master.
- **For the session:** `python3 <method-root>/scripts/export_guide.py --project-root . --prep INT-004-ana-lopez`
  fills the route table and copies the questions word for word as checkboxes into the prep sheet.
  Run it again after the master changes; a sheet you already marked is not touched without `--force`.

To make that work, write the master the way the script reads it: the sections table first, one
`### N. Title` per section, a question per bullet at the start of a line, a follow-up as a nested
bullet, interviewer notes as a line wholly in italics, and an exercise's prompt and cards between
`<!-- annex -->` and `<!-- end annex -->`.

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
The council runs in review mode (`agents/council.md`) and receives the closed decisions of
`_engine/decisions.md`. The review of the guide is **blind**: each reviewer reads it alone and
never sees another reviewer's opinion before writing their own ("The blind panel" in `agents/council.md`).

If a model checks the guide for leading questions, it is a model checker like any other: plant a few
leading questions in a copy first, and if it misses one, its "no leading questions" counts for
nothing. The rule and the model tiers live in "Every model checker" in `5a-debrief.md`.

## Gate

Before closing, check:

- Does the guide have anything that belongs in another file?
- Does the guide fit its one-page hard budget?
- Can someone who is not you run this interview from the guide and its prep sheet alone?
- Was the structure approved before the questions, and does the sections table add up to the session?
- Does an exercise feed a decision? Then check it was piloted, its prompt is fixed in writing, its minutes are real and it is not the first thing to cut.
- Does every yes/no question have its follow-up, and does no question assume the behaviour it wants to measure?
- If a model checked it, did that checker catch its seeded errors?

Suggested action:

- `Advance` if the guide covers what we want to learn without leading.
- `Deepen` if topics are missing.
- `Question` if it looks like solution validation.
