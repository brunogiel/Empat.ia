# Interview rubric

What to look at after an interview, and how to say it. The Guide uses this; it
is not copied into the user's folder. The running log goes to
`4-field/0-interview-feedback.md`.

Every criterion below comes from the method's own sources, and each one says
where it comes from. None of them was invented for this file.

## Measured, not judged

These come from `scripts/count_interview.py` over the transcript. Run it twice,
get the same number. **A criterion that could not be counted is reported as
uncounted, never estimated.**

| Criterion | Where it comes from | What is counted |
|---|---|---|
| Let them talk | "Talking more than listening" is a named mistake | Share of words that were the interviewer's |
| Answers longer than a word | An open question is one that "requires a longer explanation than one word" | Mean length of the interviewee's answers |
| Asked why | "Always ask why", and chaining it across consecutive answers | Occurrences, and how many were chained |
| Anchored in a concrete last time | "How do you do it" gives an opinion; "tell me about the last time" gives a fact | Occurrences of last-time markers |
| Did not pitch the solution | "Would you use my app if it did X?" is a named error, distinct from a closed question | Mentions of the project's own product |
| Closed with a recap | Giving back what you understood makes them articulate their own why, and confirms you got it | Present or absent |
| Guide coverage | — | Which blocks were touched, **reported only** |

## Read, not measured

These are judgement. Say so, and let the user argue.

| Criterion | Why it cannot be counted |
|---|---|
| Did not lead the answer | "Do you think an app would solve that?" is open, well formed, and still carries the answer. Form does not reveal it |
| Did not judge, played naive | "What the user says *is*"; the interviewer asks rather than corrects |
| The detour earned its place | Leaving the guide is often right. Only reading the conversation tells you which it was |
| Roles held | Reported when two people were in the room: one leads, one takes notes, no swapping |

## The criterion that matters most

Three independent sources insist on the same thing: **do not impose your own
hypothesis**. A question can be perfectly open and still carry its answer
inside. It is the hardest to detect and the easiest to commit, so it gets read
carefully on every interview rather than waved through when the counts look fine.

## Coverage is reported, never scored

An interview that abandoned the guide ten minutes in can be the best one of the
project. If the review's verdict turns negative because coverage was low, the
rubric is wrong, not the interviewer.

Ask instead: what came up in place of the plan, and was it worth more than what
was skipped?

## What this never does

- Score a criterion out of ten. Numbers on a scale drift between runs and
  contradict each other in batches; counts do not.
- Blend measured and read. The entry keeps them under separate headings.
- Store insights. Those belong in the interview note and in
  `5-debrief/findings.md`.
- Write technique feedback naming a third person into a file the team reads.

## Still open

The method's own sources disagree on the **arc** of an interview: one says go
from general to specific, another says the opposite. Until that is settled, the
rubric does not evaluate the arc. Judging it with the wrong rule is worse than
not judging it.
