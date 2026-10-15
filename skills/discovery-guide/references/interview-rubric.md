# Interview rubric

What to look at after an interview, and how to say it. The Guide uses this; it
is not copied into the user's folder. One feedback file per interview goes to
`4-field/feedback/`, explained by its own `0-README.md`.

Every criterion below comes from the method's own sources, and each one says
where it comes from. None of them was invented for this file.

## The yardstick: did the information come out?

The feedback is judged on whether the information we came for came out, **not on literal
adherence to the guide**. Do not flag changed wording, double questions or deviations from the
guide as faults. Flag information that did not come out: a follow-up that was never asked (for
example, after a card sort), cards left unplaced, a topic that stayed at the surface. Say what is
missing, in words.

The metrics below stay because they describe the conversation, not obedience: how long the
answers were (verbosity), how many questions, how many probes went deeper, and whether the
answers rested on a concrete episode.

## Reading the talk share: the interviewee's verbosity first

The talk share means nothing alone. The counter gives `mean_answer_words` and a label for the
interviewee, `interviewee_verbosity`, with provisional bands (seed calibration: about 30 words per
answer is normal, about 55 and up is very talkative):

| Label | Mean words per answer |
|---|---|
| brief | below 15 |
| normal | 15 to 44 |
| talkative | 45 to 54 |
| very talkative | 55 and up |

With a very talkative person the interviewer talks little by default, so a low share proves
little. With a normal one the interviewer has to probe more to get the same depth. Never call a
normal-verbosity person "brief" or "terse". The bands are marked *calibrating* in the JSON and
are constants at the top of `scripts/count_interview.py`, to adjust as more interviews are
counted. A recording that opens with the interviewer talking to someone else before the
participant joins is counted with `--skip-until-first-interviewee` (or `--start-line N`).

## Measured, not judged

These come from `scripts/count_interview.py` over the transcript. Run it twice,
get the same number. **A criterion that could not be counted is reported as
uncounted, never estimated.**

| Criterion | Where it comes from | What is counted |
|---|---|---|
| Let them talk | "Talking more than listening" is a named mistake | Share of words that were the interviewer's, **read against the interviewee's verbosity label** |
| Answers longer than a word | An open question is one that "requires a longer explanation than one word" | Mean length of the interviewee's answers |
| Went deeper | Probing past the first answer. "Always ask why" is one form, not the whole habit, and the direct "why" invites justifying more than telling | Questions that went deeper in any form, once each, and the same per answer of theirs |
| Anchored in a concrete last time | "How do you do it" gives an opinion; "tell me about the last time" gives a fact | Occurrences of last-time markers |
| Asked for the how or the signal | "How did you notice?" and "what would that be?" get at the criterion without asking for a justification | Occurrences |
| Contrast or "anything else" | Asking for the good and the bad, or for what else, opens the answer without leading it | Occurrences |
| Asked why, direct | The literal "why" asks the person to rationalize. Reported on its own to see whether it goes down while the anchors and the hows go up | Occurrences, and how many were chained |
| Did not pitch the solution | "Would you use my app if it did X?" is a named error, distinct from a closed question | Mentions of the project's own product |
| Closed with a recap | Giving back what you understood makes them articulate their own why, and confirms you got it | Present or absent |
| Guide coverage | — | Which blocks were touched, **reported only**, never a fault |

The probe rows are pattern counts: approximate, and the Guide checks a few by hand before
quoting one. **Never conclude that more is better.** A single literal "why" in an hour is not a
sign of an interviewer who does not probe, and the number says nothing about whether the
answer was true.

## Read, not measured

These are judgement. Say so, and let the user argue.

| Criterion | Why it cannot be counted |
|---|---|
| Did not lead the answer | "Do you think an app would solve that?" is open, well formed, and still carries the answer. Form does not reveal it |
| Did not judge, played naive | "What the user says *is*"; the interviewer asks rather than corrects |
| The detour earned its place | Leaving the guide is often right. Only reading the conversation tells you which it was. A detour is never a fault by itself: what counts is whether the information came out |
| Information that did not come out | Needs the guide's purpose next to the conversation: which question, card or follow-up never happened |
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
- Flag changed wording, double questions or deviations from the guide as faults.
- Put internal codes (hypothesis IDs, evidence IDs) in the report the interviewer receives. The
  idea goes in words; the IDs stay in the internal files.
- Deliver the markdown file as the feedback. The interviewer receives an HTML page
  (`--add interview-feedback-html --name <base>`); the markdown file is internal.

## Still open

The method's own sources disagree on the **arc** of an interview: one says go
from general to specific, another says the opposite. Until that is settled, the
rubric does not evaluate the arc. Judging it with the wrong rule is worse than
not judging it.

**Guide coverage is a keyword match, and it is wrong in both directions.** A
long transcript touches a block's title words by chance and over-reports; a
block that came up in different words than the guide's own title never matches
and under-reports. It is reported as a hint, never scored, and this is an open
issue, not a redesign: fixing keyword matching properly (semantic matching, or
asking the interviewer by hand) is out of scope here.
