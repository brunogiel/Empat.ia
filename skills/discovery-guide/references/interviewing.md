# Interviewing

Method reference. The assistant reads this; it is **not** copied into the user's
`discovery/` folder. It is identical in every project, so it lives here once
instead of in every install.

What *is* project-specific goes to `3-guide/process.md` (how this team works)
and `3-guide/guide.md` (this project's questions).

## The principles

- The interviewee is the expert. These are their sixty minutes.
- One person leads the conversation, another takes notes. Do not swap roles mid-interview.
- Open questions, never yes/no. An open question is one that cannot be answered in a word.
- Move from context and day-to-day toward depth.
- Ask for stories, examples and recent situations, not opinions.
- Always ask why, even where it is not written. Chain it: ask why of several answers in a row.
- Leave silences. The best answer usually lands three seconds after you want to fill the gap.
- Play naive even if you are the expert, so they explain it to you.
- Do not sell, and do not validate a solution.
- Do not finish their sentences.
- Do not correct them. What they say *is*; you are here to understand their perception, not fix it.

## Coverage is worth less than depth

A guide is a direction, not a questionnaire. If a thread gets good, follow it
and drop the rest of the plan. Abandoning the guide can be the right call, and
a low coverage number is not by itself a bad interview.

This matters when reviewing an interview: **report which blocks were covered,
never score the interviewer on coverage.** Ask instead whether the detour earned
its place.

## Questions to avoid, and what to ask instead

| Avoid | Better ask |
|---|---|
| Would you like to use an app for this? | How do you solve this situation today? |
| Would you pay for this? | What does it cost today to solve it badly? |
| Does this seem useful to you? | At what specific moment would something like this have helped you? |
| Which feature do you want? | What part of the process creates the most friction for you? |
| Would you use my product if it did X? | What do you do today when that happens? |
| Do you think an app would solve that? | How do you imagine that could get better? |
| What would the ideal platform look like? | What would an ideal month look like? What would stop happening? |

Two traps survive good form. "Would you use my product" and "would an app solve
that" are open questions that still carry the answer inside them. And "the ideal
platform" asks the interviewee to design the solution for you: what comes back
is their product, not their problem. Ask about their ideal month instead, and if
they describe a product anyway, ask for the last time the problem behind it happened.

## Mistakes

- Asking closed questions.
- Leading the answer, even with an open question.
- Talking more than listening.
- Racing through the guide instead of going deeper.
- Validating a solution too early.
- Judging or arguing with what they said.
- Fishing for the answer you want to hear.
- Treating experts or benchmarks as a substitute for users.

## Naming

One base name per interview, shared by every file it produces:
`INT-00X-name-surname-company`, lowercase, no accents. Drop the company when it
is just the surname. The date lives in the index, not in the file name.

```text
4-field/INT-006-ana-lopez-acme.md
4-field/_prep/INT-006-ana-lopez-acme-prep.md
4-field/_raw/INT-006-ana-lopez-acme-transcript.txt
4-field/OBS-001-place.md
```

One transcript per interview. If the recorder mixed up speakers, the relabeled
version replaces the raw one in the same file, and the header says where the
original lives. Live notes taken in the room go at the top as `#` comments; the
interview itself starts at `# === INTERVIEW START ===` (any language's marker
the counting script knows). Nothing above that line is counted.

Use an alias instead of the name whenever privacy requires it. If consent is
missing, do not use identifiable quotes.

## What counts as evidence

A verbatim quote · a fact the person reported · an interviewer observation · a
concrete workaround · a moment of emotion, tension or surprise · a contradiction
· material shared with permission · an open question the field raised.

Rules that do not bend: do not turn loose notes into insights without a source,
do not erase contradictions, do not fill silences with inference, and label
every inference as a co-pilot reading rather than a fact.
