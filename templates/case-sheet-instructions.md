# Case sheet instructions

Owns: the rules every agent follows when it writes one case sheet. Does not own: the sheet's shape → `case-sheet.json`; the analysis guide → `analysis-guide.md`.

One agent, one person, one sheet. Each agent reads only its own person, so one participant never contaminates another. These instructions live in one file and the prompt for each agent says only whose turn it is. If the platform allows subagents, run the sheets in parallel; otherwise run them one after another, each with a clean context.

## What you read (only this)

1. `5-debrief/analysis-guide.md`.
2. The full transcript of your person. Read 100%, in chunks if needed.
3. Their interview note, their card-sort record (`4-field/`) and their prep sheet.

Do not read other interviews, `findings.md` or `_engine/evidence.md`.

## Hard rules for quotes

- Every quote is an **exact copy** of a line from the participant's channel in the transcript, transcription errors included. Never paraphrase inside quotation marks.
- A quote may join consecutive lines of the same person. Cut it into pieces of 5 to 30 words.
- Every quote carries the transcript line number where it starts.
- If the interviewer said it and the person only agreed ("yes", "right"), it is not the person's quote. Mark it `"led_by_interviewer": true`.
- A datum with no quote gets `"quote": null` and a source of `note` or `inferred`. Never invent.
- A distorted name is fixed in brackets, never silently.

## What you return

One valid JSON file at `5-debrief/cases/{ID}.json`, following `case-sheet.json`. Empty fields are `null` or an empty list. Write it in the project's language.

## Two special focuses

1. **The journey and where the product studied sits in it.** Rebuild how this person went through the whole path, with their real episodes. At each stage ask: does the product studied show up? What for? Did it matter to decide? If it does not show up, say so. That is data too.
2. **Questions to return to.** Re-read for what stayed half-said: follow-ups that were missing, contradictions, ambiguous answers, things the interviewer led that deserve a clean re-ask, and any step of the card sort that was not done. At most 6, the ones worth most.

When you finish, answer in 5 lines: what you wrote, how many quotes, and the strongest observation about the product's place in this person's journey.
