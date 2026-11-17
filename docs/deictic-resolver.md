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

## Why a strip of frames

The strip was chosen against five other ways of getting the referent, on phrases whose answer a person
had checked in the video:

| Way | How it fails |
|---|---|
| Transcript only | it guesses, and a wrong guess comes without a warning |
| Nearest screenshot of the recorder | the nearest one can be far from the phrase |
| One frame | misses scrolls and mouse movement |
| **Strip of 5 frames** | **chosen**: the most exact answers and no wrong ones; a small model and a larger one agree |
| Short clips watched by a person | not scored; it costs a person many minutes per session |
| Scene-change timeline | some wrong answers come with high confidence |

The strip costs cents per session in API calls and a few minutes of a person's time. Measure both on
your own first session: the comparison was made on one product.

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
