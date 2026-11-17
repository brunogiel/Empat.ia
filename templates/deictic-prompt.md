# Prompt: what was the participant pointing at

Owns: the instruction for the reading step of `scripts/resolve_deictics.py`. Does not own: the glossary (`deictic-glossary.md`) or the cases (written by the `batches` step).

Give this text to a model that can open images, one batch at a time. Replace the three placeholders.
Use one model per batch and never let a batch see another batch's answers: the judgement of one
phrase must not leak into the next.

---

You are helping a user-research team. A participant (P) navigates a product in a video call and says
phrases with "this", "here", "that"... The interviewer is I. For each case, say whether the phrase
points at something the participant sees on screen without naming it, and if so, WHICH component of
the product it pointed at.

Each case has a STRIP of 5 frames of the participant's screen (field `image`; open it with Read and
look at it for real). The frames are in time order, left to right and top to bottom, at -4 s, -2 s,
0 s, +2 s and +4 s from the start of the key phrase; each frame carries its label. The mouse is a small
arrow. Comparing frames shows whether the page scrolled or changed, and where the mouse goes. Use the
transcript too (key phrase and context).

Use only the codes of the glossary (read it with Read): <GLOSSARY_PATH>

Rules:
- `points_at`: "yes" (it points at something on screen), "no" (the demonstrative does not point at the
  screen: it talks about their experience, another company, a connector) or "maybe".
- If `points_at` is "no", `component` = "NOT-APPLICABLE".
- Naming the wrong component is WORSE than saying it cannot be known. If neither the text nor the
  images are enough, `component` = "UNKNOWN".
- Do not invent what you do not see or read.
- For each case return: `id`, `points_at`, `component` (a glossary code, NOT-APPLICABLE or UNKNOWN),
  `element` (short free text: which concrete part, or ""), `confidence` ("high", "medium" or "low"),
  `reason` (one line).

Cases: <CASES_PATH> (a list of objects; read it with Read). The numbers in square brackets are
minutes:seconds of the recording clock.

Output: write with Write a JSON file (a list, one object per case, with those keys) at <OUT_PATH>
(by convention `out_1.json`, `out_2.json`... in the session's work folder). Your final message: only
"done" and, if something could not be done, one line saying what.
