---
name: process-interview
description: Activate after a user-discovery interview is done and the user wants to process it: "process this interview", "I just finished interviewing X", "turn this transcript into a note", "what did we get from the call with Y", "extract the evidence", "what should I have asked", "improve the guide for next time", "interview retro". Takes one raw interview (transcript, recording, or notes the user points to) plus where to save it, and produces a structured note, atomic evidence, an index update, a guide-improvement retro, and the counted feedback on how the interview was conducted. It is the "after the interview" complement to phase 3 (the guide) and operationalizes step 4a of the Empat.ia method. Source-agnostic: it works from any transcript the assistant can read. Never invents data, preserves verbatim quotes, and never auto-edits the master guide (it proposes).
---

# Process Interview

Turn **one** raw interview into processed, traceable material, and close the loop back to the guide.

This is the symmetric partner of the interview-guides stage: that stage builds the questions *before*; this skill processes the answers *after*. It operationalizes **step 4a, interview capture**, and adds the two pieces the method implies but never made explicit: an **interview retro** that proposes what to ask next and how to sharpen the guide, and **feedback on how the interview was conducted**, which nothing in the method used to look at.

## When to use

- The user finished an interview and wants it captured, not synthesized prematurely.
- The user wants the takeaways, verbatim quotes, and evidence from one conversation.
- The user wants a retro: what they could have asked, what to change in the guide for the next interview.

Process **interview by interview**. Don't cross patterns here: that is phase 5, the debrief.

## Inputs (ask only what's missing, keep it to the minimum)

1. **The raw material.** A transcript, recording, or notes. Either the user drops it in `discovery/4-field/_raw/`, or they point you to where it lives (a file, a tool you can read). If you can't read it, ask them to paste or drop it.
2. **Who + profile + date.** Interviewee (anonymize per consent), profile (the segment from the sample), interview date.
3. **Which guide was used.** So the retro can compare planned vs covered. Default to the profile's master guide.
4. **Destination.** The active project's `discovery/` folder. If there's none, this skill still runs standalone: ask where to save the note and transcript.

## Flow

1. **[DET] Get the transcript.** Read it from `incoming/` or the pointer the user gave. If it's long, save it first and read it in chunks until you've read 100%. Never summarize from a partial read; if you couldn't read all of it, say so.
2. **[DET] Assign an ID** (`INT-00X`) and save a clean transcript to `discovery/4-field/_raw/`.
3. **[LATENT] Write the structured note** in `discovery/4-field/` using `templates/interview-note-template.md`. Fill it from the real material:
   - **Metadata** (interviewee anonymized per consent, profile, date, duration, modality, interviewer, recording, consent).
   - **Context** (who they are, where the problem happens, their role).
   - **Verbatim quotes** (exact words, with topic + moment). Preserve them; this is the raw gold.
   - **Narrated journey** (step / what they do / what they think-feel / friction / tools-people).
   - **Pains**, **motivations**, **behaviors and workarounds**, **decision process**, **current tools and alternatives**.
   - **Contradictions** (what they say vs. what they do, or internal tensions).
   - **Interviewer observations** (separate from interpretation).
   - **Moments of tension, surprise or emotion.**
   - **New questions** (what this opens for the next round).
   - **Co-pilot readings** (your inferences, clearly labeled, not facts).
4. **[LATENT] Extract atomic evidence** into `discovery/_engine/evidence.md`: one row per unit, typed (`quote`/`fact`/`observation`/`workaround`/`emotion`/`contradiction`/`material`/`open_question`/`copilot_reading`), each traceable to the interview ID and a location (transcript spot or note section). Keep insights out of the ledger; this is atomic evidence only.
5. **[DET] Update `discovery/4-field/0-index.md`**: metadata, files, status `done`, gaps left.
6. **[LATENT] Interview retro (the distinctive step).** Close the loop back to the guide. Produce three things, inside the note under a clear "Guide / method learnings" section:
   - **Questions left on the table.** Follow-ups the interviewee opened and you didn't pursue, sections of the guide that went uncovered (and whether that was fine because you followed the person, or a real miss).
   - **Concrete edits to the master guide** for the next interview (add / reword / reorder / drop a question; a technique that worked, like a closing recap). Be specific and quote the guide line.
   - **Part 2?** Default **no**: you learn more from new interviews than from re-interviewing. Only recommend a part 2 if a genuinely important theme was missed.
   If the user reflected out loud during or after the call (their own debrief), capture that verbatim into this section, it's often the sharpest input.
7. **[DET] Count what is countable.** Run
   `python3 {method-root}/scripts/count_interview.py <transcript> --interviewer "<name>" --guide <master guide> --product "<your product terms>"`.
   It returns words per speaker, questions, whys and chains, concrete anchors, product mentions,
   whether there was a closing recap, and which guide blocks came up. **No transcript, or no
   speaker labels: skip this and say so. Never estimate a number.**
8. **[LATENT] Write the feedback entry** in `discovery/4-field/0-interview-feedback.md`, using
   `references/interview-rubric.md`. Keep **Measured** and **Read** under separate headings: the
   first is reproducible, the second is judgement the user can argue with.
   - **Coverage is reported, never scored.** Leaving the guide for a better thread is often the
     right call; ask whether the detour earned its place.
   - **Never score a criterion out of ten.**
   - The entry is about the interviewer, not the interviewee. No insights here.
   - **If someone else ran the interview**, technique feedback naming them does not go into this
     file, which the team reads. Say it in conversation; write it only if they ask.
9. **[DET] Update `interviews.done` and `interviews.unprocessed`** in `_engine/state.yaml`. The
   Guide reads `unprocessed` before offering Advance into the debrief.
10. **[DET] Gate.** Close with a recommendation: `Advance` (enough material to cross patterns), `Deepen` (key interviews missing), `Question` (sampling or capture bias), or `Council` (strong contradictions). Update `_engine/state.yaml` if the method's state file exists.

## Hard rules

- **Preserve verbatim quotes.** Don't paraphrase what should be exact.
- **Don't invent.** Work only from what's in the material. If you infer, label it `Co-pilot reading`.
- **Separate observation from interpretation.** Both belong in the note, in different sections.
- **One interviewee per note.** Don't mix sources.
- **Never auto-edit the master guide.** The guide is living, but you *propose* edits in the retro; you only apply them if the user says so. The master guide is reused across interviews, so it doesn't get crossed out or rewritten silently.
- **Respect consent.** Anonymize per the consent on file; honor "do not use" on sensitive quotes.

## Expected output

- A clean transcript in `transcripts/`.
- A structured note in `notes/` (1:1 with the template), including the **Guide / method learnings** retro.
- New rows in `_engine/evidence.md`, traceable.
- An updated `index.md` (status + gaps).
- A gate recommendation. No master guide edited unless the user approved it.

## Success metrics

- Verbatim quotes are exact and attributed to a moment.
- Observation is never mixed with interpretation; inferences are labeled.
- Every evidence row traces back to the interview and a location.
- The retro gives the user at least one concrete, specific change to the guide (or an explicit "guide held up, no change").
- Nothing invented; gaps recorded honestly.
- Processed interview by interview, without jumping to cross-interview patterns.

## Notes

- This skill is part of the Empat.ia method bundle and reads its `templates/` (`interview-note-template.md`, `_engine/evidence.md`). In standalone use (no `discovery/` folder), it still produces the note + retro wherever the user points.
- Source-agnostic by design. If the user's transcripts live in a specific tool (a recorder, a meeting app), a project-level wrapper skill can handle fetching from that tool and then hand the raw transcript to this flow.
