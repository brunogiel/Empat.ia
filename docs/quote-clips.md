# Finding quotes in the video and cutting clips

Owns: what `scripts/locate_quotes.py` and `scripts/cut_clips.py` do, when they are worth running and what they cannot promise. Does not own: the quote and context checks → `workflows/user-discovery/steps/5a-debrief.md`; the report → `workflows/user-discovery/steps/8a-report.md`.

Both tools are optional and run on request. No step of the method needs them. They pay off most when a prototype is shown on screen and the person's own words, played back, say more than a paraphrase.

## Why the clock matters

The tool that records a call also writes a transcript. Its clock can differ from the video's by a few seconds or by minutes. A clip cut at the transcript's minute shows another moment. So the canonical minute of a quote is the video's, and the evidence ledger keeps both: `t_transcript` (what the recorder says) and `t_video` (what the audio says). Their difference is the offset that `resolve_deictics.py offset` also estimates (video clock = recorder clock − offset), so one estimate serves both tools.

## `locate_quotes.py`: the minute in the video

1. Local speech-to-text (`faster-whisper` or `openai-whisper`) turns each recording into timed words, once, and keeps them in a cache folder.
2. For each quote, it looks for the window of heard words that covers the most of the quote's content words. Function words ("the", "de") and words under 3 letters are ignored, so chatter made of common words does not match. A heard word matches a quote word if both are equal, or if both have 5 letters or more and are close: a speech model misspells names and rare words.
3. It returns the start and end in the video's clock, the coverage (share of the quote's content words found) and a status: `located` at 0.8 or more, `weak` from 0.5, `not_found` below that.
4. If the transcript's minute is known, it also returns the offset. When a quote was said twice, the transcript's minute (minus the offset, if you give it) picks the repeat. `--window` limits the search around that minute.

It aligns by words on purpose. Comparing the whole quote as one string against the whole transcript produced false alarms: a long string of common words scores high against almost anything.

## `cut_clips.py`: the clip, its check and its thumbnail

1. Cuts the source with `ffmpeg`, from a margin before the quote to a margin after it, re-encoded small.
2. Burns the captions into the picture as images, not as a text track. Many viewers (a PDF reader, a slide tool, a phone preview) hide a text track; a burned caption always shows. This needs Pillow; `--no-subtitles` skips it.
3. Listens to the finished mp4 again and computes the coverage of the quote. `ok` is `true` only at 0.8 or more and for a file that opens.
4. Saves a still frame as a thumbnail, for pieces that cannot play a video.

Run `locate_quotes.py` first and pass its output: it carries the video minute and the end of each quote.

## What `ok: true` does not mean

- It means the words of the quote are in the clip. It does not mean the clip says what the slide or the finding says. That is the context check of `5a-debrief.md` (±6 lines, the clip against the title it illustrates), done by a mid or strong model after a seeded run. Choose each clip against the title of the slide or finding it illustrates, not by topic; `illustrates` in the input is carried to the output so the check has both.
- A quote cut short fails the coverage on purpose. Coverage does not catch a clip that starts a sentence late and flips its meaning: the context check does.
- Nothing is blurred. Open each clip at three frames (start, middle, end) and blur emails, phones, passwords, names and the chats of the call (see `7b` and `8a`). Consent comes first: the person's row in the consent record must allow a clip.

## Install and exit codes

`ffmpeg` and `ffprobe` on the PATH; `faster-whisper` or `openai-whisper`; Pillow for the captions. Missing any of them, a script exits with code 2 and says how to install it. Exit 1 means some quote is weak or not found, or some clip is not `ok`. Exit 0 means all passed.

## Privacy

Recordings, the cached words and the clips are personal data. Keep them in a folder outside the project, run everything locally and delete them when the piece is done. A clip goes into `share/` or `8-report/` only after it was checked at three frames.
