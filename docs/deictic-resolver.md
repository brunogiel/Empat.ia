# Resolving "this" and "here" in screen-shared sessions

Owns: what `scripts/resolve_deictics.py` does, when to use it and what it cannot promise. Does not own: the validation steps → `workflows/user-discovery/steps/7b-validation-sessions.md`.

## The problem

In a validation session the participant shares their screen and says "this is confusing", "here I
would click". The transcript keeps the words and loses the referent. Evidence that cannot say which
component a comment was about is weak evidence per component.

## The method

Five mechanical steps run locally, one judgement step reads the frames.

1. **offset**: the recorder clock and the video clock differ. Local Whisper transcribes four windows
   of the audio; they are matched to the transcript and the median is the offset (a ±4 s filter drops
   bad matches). Video clock = recorder clock − offset.
2. **crop**: finds the box of the shared screen, without black bars or the call's faces.
3. **candidates**: the participant's lines that contain a demonstrative, one per burst of 6 seconds,
   from a start point that skips the warm-up. Connectors such as "that's why" are ignored.
4. **frames**: for each phrase, a strip of 5 frames at −4, −2, 0, +2 and +4 s. A second copy hides
   the faces of the call (masks, by time range) and is the only one that is shared.
5. **batches**: the phrases go to a reading step in groups of about 28, one model per batch.
6. **report** (after the reading step): one Markdown sheet per session with the phrase, both clocks,
   the component, the element, the confidence and the capture.

The reading step uses `templates/deictic-prompt.md` and a glossary of the product's components
(`templates/deictic-glossary.md`, one per product). The model answers with a JSON file per batch.

## What was compared

Six ways of getting the referent were tried on one session, on 20 phrases whose answer a person had
checked in the video. Exact answers out of 20, with wrong answers in brackets:

| Way | Exact (wrong) | Note |
|---|---|---|
| Transcript only | 12 (2) | the 2 wrong answers did not warn |
| Nearest screenshot of the recorder | 13 (2) | the nearest one was over 45 s away in 7 of 20 cases |
| One frame | 17 (0) | misses scrolls and mouse movement |
| **Strip of 5 frames** | **18 to 19 (0)** | **chosen**; small model and larger model within one phrase |
| 13 s clips watched by a person | not scored | 13 to 25 minutes of a person per session |
| Scene-change timeline | 13 (4) | 3 of the 4 wrong answers came with high confidence |

Cost per session was between a few cents and about 40 cents at assumed API prices (not verified),
and the person's time between 3 and 7 minutes for the strip. Treat these as orders of magnitude, from
one session and one product.

## What it cannot promise

- **The confidence is declared by the model.** Treat it as a weak signal. Rows marked "review" are
  the ones to open first.
- **The check was partly circular.** The reference answers were produced by looking at the same
  strips the model reads. A person must open the flagged captures before any of them is quoted.
- **Naming the wrong component is worse than abstaining.** The prompt says so; `UNKNOWN` is a valid
  answer and goes to review.
- **The glossary is per product.** A new wireframe needs a new glossary.
- **The burst rule drops some phrases.** Two demonstratives within 6 seconds produce one candidate.
  Lower `BURST_SECONDS` in the script if that loses cases you care about.

## Privacy

Recordings are personal data. Download them to a folder outside the project, run everything locally
(ffmpeg, Whisper), and delete them at the end. Do not send frames to any cloud service you did not
agree with the participant.

- Faces of the call are masked in the shared copy. Pass `--masks` for the time ranges they appear in.
- Screens that show personal data (forms, confirmation pages) are tagged `[sensitive]` in the
  glossary and get no capture in the sheet. A person must still look at the captures before sharing:
  a mail address can appear in a place nobody tagged.
- Only the sheets and the masked captures belong in the project. Strips without masks, frames and
  videos stay out.
