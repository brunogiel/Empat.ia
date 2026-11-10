# Interview rubric

What to look at after an interview, and how to say it. The Guide uses this; it
is not copied into the user's folder. One feedback file per interview goes to
`4-field/feedback/`, explained by its own `0-README.md`.

Every criterion below comes from the method's own sources or from a real round
of fieldwork, and says which. None of them was invented for this file.

## The yardstick: did the information come out?

The feedback is judged on whether the information we came for came out, **not on literal
adherence to the guide**. Do not flag changed wording, double questions or deviations from the
guide as faults. Flag information that did not come out: a follow-up that was never asked (for
example, after a card sort), cards left unplaced, a topic that stayed at the surface. Say what is
missing, in words.

## How the person tells: three scales, not the talk share

The interviewer's talk share means little on its own: the interviewer's words per turn are fairly
even, and the share moves with the person. So the feedback describes **how the person tells**, on
three scales with every interview of the round on the bar. The unit is the **exchange** (one real
question plus everything the person says until the next one), never the recorder's turn, which a
"great" or an "ok" cuts in two.

| Scale | What is counted | How |
|---|---|---|
| How much they tell | Median words per exchange | A count (`feedback_scales.py`) |
| How much they monologue | Share of all their words said in answers of 200 words or more | A count |
| How much they get to the point | Of every 10 answers to a real question, how many start by answering it | jev, one call per exchange (optional) |

Bands are provisional, set on five interviews of one project, and are constants at the top of
`scripts/feedback_scales.py`: short < 30 · medium 30-45 · long > 45 words; short stretches < 30 % ·
stretches out 30-45 % · monologues > 45 %; struggles < 7 · sometimes goes around 7-7.5 · gets to the
point > 7.5 of 10. Recalibrate with 8 or more interviews. A recording that opens with chatter is cut
with `--skip-until-first-interviewee` (or `--start-line N`).

## Depth is in the answer, not in the form of the question

What came out is read in what the person said, exchange by exchange: **a concrete case** (one
identifiable occasion of their own), **a reason** of their own, **a tension** (a dilemma, a cost,
something given up) or **a generalisation** (an opinion with no case under it). Each one is either
**brought** by the person or **provoked** by a question. These are judged by jev on the answer, in
its context, and counted per topic of the guide; the topics come from the project's own guide
(`feedback_packs.py`). Without jev, the Guide reads them.

## Counted by hand, never by the judge

| Criterion | Why by hand |
|---|---|
| You asked for a concrete case, and it came out | A judge reading the interviewer's question counts greetings, instructions and cut-off questions as requests: on the first real round it was far off (7 of 19 by the judge, 11 of 13 by hand). Not ranked across interviews |
| You asked for the reason or the signal, and it came out | Same. "How did you notice?" and "what would that be?" count; a literal "why" counts too |
| An idea of yours for the person to confirm (a premise) | The judge proposes candidates and is right about half the time. A person reads each one. An accepted premise that a summary attributes to the person is ❌; a contradicted one, 🟡 |

The worksheet for these is `_engine/feedback/<base>-hand-count.md`, with the judge's reading of
the answer pre-filled.

## Verdicts

Every row of the page carries one: ✅ good · 🟡 to improve (it happened, but it does not change what
can be claimed) · ❌ failed (something can no longer be claimed, or will not be recovered). Per topic,
the verdict is against what that topic was looking for (for example, ✅ with 5 or more concrete cases
in a topic after cases). Per conduct, the page always looks at four fixed biases: an idea of yours
for the person to confirm, a question that leads, a hypothetical question, your word before theirs.

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

The per-topic verdict is not coverage. It asks whether the information a topic
was looking for came out, wherever in the conversation it came out, detours
included. Which questions of the guide were asked is never scored.

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
- Count "you asked for a case / a reason" with the judge, or rank those hand counts across
  interviews.
- Put a premise on the page that no person has confirmed by reading it.
- Report the keyword counts of `count_interview.py` (probes, anchors, the literal "why", the
  talk share on its own). They measured the form of the questions, not what came out: on the
  first real round the interview that served least scored second. The script stays as an
  internal diagnostic.
- Deliver the markdown file as the feedback. The interviewer receives an HTML page
  (`--add interview-feedback-html --name <base>`); the markdown file is internal.

## Still open

The method's own sources disagree on the **arc** of an interview: one says go
from general to specific, another says the opposite. Until that is settled, the
rubric does not evaluate the arc. Judging it with the wrong rule is worse than
not judging it.

**Topics are assigned by jev, exchange by exchange**, against the topics and
intents of the project's guide. It reads meaning, not title words, but it has
run on one project only. The first run on a new project is checked by hand.
Without jev, the Guide assigns them by reading.

**"Gets to the point" is calibrated on one project.** Before trusting it on a
new one, the interviewer labels about 20 exchanges by hand and compares.
