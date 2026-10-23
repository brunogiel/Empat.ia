#!/usr/bin/env python3
"""Cut an interview transcript into exchanges, the unit the feedback measures.

An exchange is one real question from the interviewer plus everything the
person says until the next real question. A turn is the wrong unit: the
recorder cuts it, and every "great" or "ok" from the interviewer split an
answer in two. On the first real round that moved the "how much they tell"
scale by about 45 %.

A question is real when it has a question mark or more than three words. The
short acknowledgements ("ok", "sure", "great") do not cut the exchange: they
stay inside the answer as `[interviewer: ok]`, so the reader still sees them.

Input
  The same transcripts count_interview.py reads: speaker labels at the start of
  a line (or the one-line recorder exports), counting from the '## Interview'
  line when there is one. Who the interviewer is comes from --interviewer.

Output
  JSONL, one exchange per line, ready for classify_exchanges.py:
      {"id": "x001", "state": {"interviewer_question": "...", "interviewee_answer": "..."}}
  With --lang es the state keys are Spanish, the wording the packs were
  measured with.

Usage
  python3 segment_interview.py discovery/4-field/_raw/INT-004-ana-transcript.md \\
      --interviewer "Bruno" --out discovery/_engine/feedback/INT-004-ana.jsonl
  python3 segment_interview.py T.md --interviewer Microphone --lang es \\
      --skip-until-first-interviewee --out INT-004-ana.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import count_interview as ci  # noqa: E402

# The keys of each exchange's state, by language. jev reads them as part of the
# context, so they say plainly who said what.
STATE_KEYS = {
    "en": ("interviewer_question", "interviewee_answer"),
    "es": ("pregunta_entrevistador", "respuesta_entrevistado"),
}
SHORT_LABEL = {"en": "interviewer", "es": "entrevistador"}

# Recorder exports name the other side "System audio (Name)" on most lines and
# plain "System audio" on a few. Learned as two speakers, the rare one falls
# under the label threshold and its words get glued to the interviewer's turn.
RECORDER_LABEL = re.compile(r"(?m)^(\s*)System audio\s*\([^)\n]*\):")

# A question with more than this many words, or with a question mark, opens a
# new exchange. Three or fewer and no mark is an acknowledgement.
ACK_MAX_WORDS = 3


def question_of(state: dict) -> str:
    """The interviewer's question of an exchange, whatever language its keys are in."""
    for q, _ in STATE_KEYS.values():
        if q in state:
            return state[q]
    return ""


def answer_of(state: dict) -> str:
    """The person's answer of an exchange, whatever language its keys are in."""
    for _, a in STATE_KEYS.values():
        if a in state:
            return state[a]
    return ""


def is_real_question(text: str) -> bool:
    return "?" in text or len(text.split()) > ACK_MAX_WORDS


def segment(turns, interviewer: str, lang: str = "en"):
    """[(question, answer)] from merged turns. The first exchange can have an
    empty question when the person spoke before the interviewer asked anything."""
    label = SHORT_LABEL.get(lang, "interviewer")
    exchanges, question, answer = [], None, []
    for turn in turns:
        text = turn["text"].strip()
        if turn["speaker"].lower() == interviewer.lower():
            if is_real_question(text):
                if question is not None or answer:
                    exchanges.append((question or "", answer))
                question, answer = text, []
            elif answer:
                answer.append(f"[{label}: {text}]")
        else:
            answer.append(text)
    if question is not None or answer:
        exchanges.append((question or "", answer))
    return [(q, " ".join(a).strip()) for q, a in exchanges]


def to_items(exchanges, lang: str = "en"):
    q_key, a_key = STATE_KEYS.get(lang, STATE_KEYS["en"])
    return [{"id": f"x{i:03d}", "state": {q_key: q, a_key: a}}
            for i, (q, a) in enumerate(exchanges, 1)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Cut a transcript into exchanges.")
    parser.add_argument("transcript")
    parser.add_argument("--interviewer", required=True,
                        help="Speaker label of the interviewer. Never guessed.")
    parser.add_argument("--out", required=True, help="JSONL to write.")
    parser.add_argument("--lang", default="en", choices=sorted(STATE_KEYS),
                        help="Language of the state keys; match the packs' language.")
    parser.add_argument("--skip-until-first-interviewee", action="store_true",
                        help="Start at the first turn of anyone who is not the interviewer.")
    parser.add_argument("--start-line", type=int, default=None, metavar="N",
                        help="Start at line N of the file (1-based).")
    args = parser.parse_args()

    path = Path(args.transcript)
    if not path.exists():
        raise SystemExit(f"Transcript not found: {path}")
    raw = ci.trim_start(path.read_text(encoding="utf-8", errors="ignore"), args.start_line)
    turns = ci.parse(RECORDER_LABEL.sub(r"\1System audio:", ci.interview_text(raw)))
    if args.skip_until_first_interviewee:
        turns, _ = ci.skip_until_first_interviewee(turns, args.interviewer)
    if not turns:
        raise SystemExit("No speaker labels found. This file cannot be cut into exchanges.")
    speakers = {t["speaker"].lower() for t in turns}
    if args.interviewer.lower() not in speakers:
        raise SystemExit(f"No turns found for interviewer '{args.interviewer}'. "
                         f"Speakers in this file: {sorted({t['speaker'] for t in turns})}")

    items = to_items(segment(turns, args.interviewer, args.lang), args.lang)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"{len(items)} exchanges -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
