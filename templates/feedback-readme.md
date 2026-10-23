# How the interviews are going

Owns: your feedback as interviewer, one HTML page per interview (`INT-00X-<name>-feedback.html`) and its internal worksheet (`INT-00X-<name>-feedback.md`). Does not own: what the person said → `4-field/INT-00X-<name>.md`; patterns across interviews → `5-debrief/findings.md`; the machine files → `_engine/feedback/`.

This is about **you**, not about what the interviewee said. No insights here.

**The yardstick: did the information we came for come out?** Not whether the guide was followed to
the letter. Changed wording, a double question or a detour are not faults. A question never asked,
a card left unplaced, a story left without its concrete case: those are.

## The three parts of the page

1. **How the person tells.** Three scales, with every interview of the round on the bar:
   - **How much they tell:** median words per exchange (short < 30 · medium 30-45 · long > 45).
   - **How much they monologue:** what part of everything they said came in answers of 200 words or
     more (< 30 % short stretches · 30-45 % stretches out · > 45 % monologues). A count, no model.
   - **How much they get to the point:** of every 10 answers to a real question, how many start by
     answering it (< 7 struggles · 7-7.5 sometimes goes around · > 7.5 gets to the point). Judged by
     jev, one call per exchange.
   - One bold sentence with the reading, and one or two literal examples.
   - The bands come from five interviews of one project: recalibrate with 8 or more.
2. **What came out of each topic.** One row per topic of the guide, with a verdict against what that
   topic was looking for, plus rows for information that did not come out. Thresholds by what the
   topic seeks: a topic after concrete cases is ✅ with 5 or more; one after reasons, ✅ with 5 or
   more; one after a case with a specific thing (a website, a document), ✅ with 2 or more; 🟡
   halfway; ❌ nothing. Opening topics and exercises are judged by reading.
3. **How you conducted it.** One row per thing you did, with a verdict: ✅ good · 🟡 to improve (it
   happened, but it does not change what can be claimed) · ❌ failed (something can no longer be
   claimed or will not be recovered). It includes the cases and reasons you asked for and that came
   out, whether you followed the tensions, and **four fixed biases**: an idea of yours for the person
   to confirm, a question that leads, a hypothetical question, your word before theirs.

It closes with **For the next session** and, if there is one, the question that is still missing.

## How it is made

Machine files live in `_engine/feedback/`; the method's scripts do the counting. Run them from
inside this discovery folder.

1. **Once per project, after the guide is closed:** build the packs from the guide.
   `python3 <method-root>/scripts/feedback_packs.py --guide 3-guide/guide.md --subject "<what the interviews are about>" --lang <es|en> --out _engine/feedback`
   The topics come from the guide's numbered blocks and their intent lines. Check the list it prints.
2. **Per interview:** cut the transcript into exchanges (your question plus everything the person
   says until the next one; an "ok" of three words or fewer does not cut).
   `python3 <method-root>/scripts/segment_interview.py 4-field/_raw/<base>-transcript.md --interviewer "<label>" --lang <es|en> --out _engine/feedback/<base>.jsonl`
3. **Optional, experimental:** judge each exchange with jev, twice (depth and branches packs).
   `python3 <method-root>/scripts/classify_exchanges.py --items _engine/feedback/<base>.jsonl --pack _engine/feedback/depth-pack.json --out _engine/feedback/<base>-depth.csv`
   and the same with `branches-pack.json` → `<base>-branches.csv`. About one US cent per interview.
   No key: it exits with code 2 and you go on without it.
4. `python3 <method-root>/scripts/feedback_scales.py _engine/feedback --lang <es|en>` writes, per
   interview, `<base>-data.json`, `<base>-scales.html` and `<base>-hand-count.md`.
5. **Count by hand** on `<base>-hand-count.md`: "you asked for a case / a reason, and it came out".
6. Write the page from the template and **check every quote** against the transcript
   (`verify_quotes.py`). Premise candidates go in only after a person confirms them.

## What is counted by hand, and why

- **"You asked for a case / a reason and it came out."** The judge that reads the interviewer's own
  question counted greetings, instructions and cut-off questions as requests, and missed by a lot
  (in one interview 7 of 19 by the judge, 11 of 13 by hand; in another, 7 of 17 against 11 of 15).
  The sheet lists every exchange with jev's reading of the answer pre-filled, which held up; you mark
  the question side. These numbers are not ranked across interviews.
- **Premises.** The judge proposes candidates; a person confirms them. They are right about half
  the time: many were confirmations of a fact the person had already said.

## jev is experimental

jev (typesafe.ai) answers closed questions about one exchange per call, with no batch and no
neighbours. It has run on one real round: the questions about the person's answer held up; the ones
about the interviewer's question did not. **The first run on a new project is checked by hand,
exchange by exchange, on at least one interview**, before its numbers go into a page. Its confidence
never ranks anything; the code cuts on fixed thresholds. Without a key, the two scales that are
plain counts still come out, over every exchange (the opening and the closing are not set apart),
and the rest is read by hand.

## Calibrating "gets to the point"

Before trusting the third scale on a new project, the interviewer labels about 20 exchanges by
hand (does the answer start by answering?) and compares them with jev's. Note the result in the
project's decisions.

> If someone else ran the interview, technique feedback naming them does not go in writing here. Say
> it in the conversation; write it only if that person, or the one who owns the file, says it can go
> in writing.
