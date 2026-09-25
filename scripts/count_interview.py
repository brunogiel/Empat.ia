#!/usr/bin/env python3
"""Count what is countable in an interview transcript.

The numbers that go into 4-field/0-interview-feedback.md come from here, not
from a model reading the transcript and forming an impression. Two runs over the
same file return the same answer; that is the whole point. Judgement -- whether
a question led the answer, whether leaving the guide was worth it -- stays with
the Guide and is labelled as judgement.

Input
  A .txt or .md transcript with speaker labels at the start of a line:
      Bruno: ...           or      [Bruno] ...
  Who the interviewer is comes from --interviewer, never guessed.
  Timestamps are optional. Without them, interruptions are not counted and the
  report says so.

Output
  JSON on stdout. Anything that could not be counted lands in "unavailable"
  with the reason. Nothing is estimated.

Usage
  python3 count_interview.py TRANSCRIPT --interviewer "Bruno"
  python3 count_interview.py T.txt --interviewer Bruno --product "Empatia,la app"
  python3 count_interview.py T.txt --interviewer Bruno --guide discovery/3-guide/guide.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SPEAKER = re.compile(r"^\s*(?:\[(?P<b>[^\]]{1,40})\]|(?P<a>[^:\n]{1,40}):)\s*(?P<text>.*)$")
TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")


def fold(text: str) -> str:
    """Lowercase and strip accents, so 'por qué' and 'por que' are one thing."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def load_patterns(path: str | None):
    if path:
        namespace: dict = {}
        exec(Path(path).read_text(encoding="utf-8"), namespace)
        return namespace
    from patterns_es import (LANGUAGE, WHY, CONCRETE, RECAP,
                             CLOSED_OPENERS, LEADING_HINTS)
    return dict(LANGUAGE=LANGUAGE, WHY=WHY, CONCRETE=CONCRETE, RECAP=RECAP,
                CLOSED_OPENERS=CLOSED_OPENERS, LEADING_HINTS=LEADING_HINTS)


def parse(transcript: str):
    """Split into turns. Returns [] when there are no speaker labels.

    Two shapes in the wild, and both have to work:

      one turn per line          Bruno: ...
                                 Ana: ...

      the whole call on one line  Me: ...  Them: ...  Me: ...

    The second is what recorder exports look like. Parsing it line by line
    would fold an entire interview into a single interviewer turn and report a
    share of 100%, which is worse than reporting nothing.

    Labels are learned by frequency, not by position: a speaker repeats dozens
    of times, a colon inside prose does not repeat behind the same token. Going
    by position fails on exports where the second speaker never starts a line.
    """
    # Learn the speaker labels by frequency, not by position. A real label
    # repeats dozens of times; a colon inside prose does not repeat behind the
    # same token. Position alone fails on exports where the whole call sits on
    # one line and the second speaker never starts one.
    candidates: dict[str, int] = {}
    for match in re.finditer(r"(?:^|\s)(?:\[)?([^\s:\[\]][^:\[\]\n]{0,28})(?:\])?:\s", transcript):
        label = match.group(1).strip()
        if not label or len(label.split()) > 4 or label.endswith((".", ",", ";")):
            continue
        candidates[label] = candidates.get(label, 0) + 1
    if not candidates:
        return []

    top = max(candidates.values())
    labels = [label for label, n in candidates.items()
              if n >= 3 and n >= top * 0.05]
    if not labels:
        return []

    pattern = re.compile(
        r"(?:^|\s)(?:\[)?(" + "|".join(re.escape(l) for l in labels) + r")(?:\])?:\s",
        re.MULTILINE)

    turns = []
    matches = list(pattern.finditer(transcript))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(transcript)
        text = transcript[match.end():end].strip()
        if not text:
            continue
        if turns and turns[-1]["speaker"] == match.group(1):
            turns[-1]["text"] += " " + text
        else:
            turns.append({"speaker": match.group(1), "text": text})
    return turns


def questions_in(text: str):
    """Sentences ending in a question mark, plus Spanish inverted openers."""
    text = text.replace("¿", "")
    return [part.strip() for part in re.split(r"(?<=\?)\s*", text) if part.strip().endswith("?")]


def count(turns, interviewer, patterns, products, guide_blocks):
    mine = [t for t in turns if t["speaker"].lower() == interviewer.lower()]
    theirs = [t for t in turns if t["speaker"].lower() != interviewer.lower()]

    if not mine:
        raise SystemExit(
            f"No turns found for interviewer '{interviewer}'. "
            f"Speakers in this file: {sorted({t['speaker'] for t in turns})}")

    words_mine = sum(len(t["text"].split()) for t in mine)
    words_theirs = sum(len(t["text"].split()) for t in theirs)
    total = words_mine + words_theirs

    my_questions = [q for t in mine for q in questions_in(t["text"])]
    closed = [q for q in my_questions
              if any(fold(q).startswith(o) for o in patterns["CLOSED_OPENERS"])]

    def hits(needles, turns_):
        return sum(fold(t["text"]).count(n) for t in turns_ for n in needles)

    # Chained whys: consecutive interviewer turns that both ask why.
    asked_why = [any(n in fold(t["text"]) for n in patterns["WHY"]) for t in mine]
    chains = sum(1 for i in range(1, len(asked_why)) if asked_why[i] and asked_why[i - 1])

    # Recap: an interviewer turn inside the last tenth of the conversation.
    tail = mine[-max(1, len(mine) // 10):]
    recap = any(n in fold(t["text"]) for t in tail for n in patterns["RECAP"])

    unavailable = []
    if not any(TIMESTAMP.search(t["text"]) for t in turns):
        unavailable.append("interruptions and finished sentences: the transcript has no timestamps")
    if not products:
        unavailable.append("mentions of your own product: no product terms were given (--product)")
    if guide_blocks is None:
        unavailable.append(
            "guide coverage: no guide file was given, or its blocks could not be read. "
            "Blocks are expected as '## 1. Title' or '### 1. Title'.")

    result = {
        "language": patterns["LANGUAGE"],
        "interviewer": interviewer,
        "turns": {"interviewer": len(mine), "interviewee": len(theirs)},
        "words_by_speaker": {"interviewer": words_mine, "interviewee": words_theirs},
        "interviewer_share": round(words_mine / total, 3) if total else None,
        "mean_answer_words": round(words_theirs / len(theirs), 1) if theirs else None,
        "questions_total": len(my_questions),
        "questions_closed": len(closed),
        "questions_closed_note": "approximate: pattern matching cannot settle this reliably",
        "why_count": hits(patterns["WHY"], mine),
        "why_chains": chains,
        "concrete_anchors": hits(patterns["CONCRETE"], mine),
        "product_mentions": (sum(fold(t["text"]).count(fold(p)) for t in mine for p in products)
                             if products else None),
        "closing_recap": recap,
        "guide_blocks_hit": guide_blocks,
        "guide_blocks_note": ("approximate: matched by keyword overlap, so a long transcript "
                              "over-reports. Report the blocks, never score the interviewer "
                              "on them: leaving the guide for a better thread is often right."),
        "leading_candidates": [q for q in my_questions
                               if any(h in fold(q) for h in patterns["LEADING_HINTS"])],
        "leading_note": "candidates to read by hand, not a count. Form does not reveal leading.",
        "unavailable": unavailable,
    }
    return result


def guide_coverage(guide_path: str | None, turns):
    """Which numbered blocks of the guide came up. None when it cannot be read.

    An empty list would mean "the guide was fully skipped", which is a real and
    sometimes correct outcome. Failing to parse the guide is a different thing,
    and reporting it as zero coverage would be the exact mistake this tool is
    built to avoid.
    """
    if not guide_path:
        return None
    text = Path(guide_path).read_text(encoding="utf-8")
    blocks = re.findall(r"^#{2,3}\s*(\d+)[\uFE0F\u20E3]*[\.\)]?\s*(.+)$", text, re.M)
    if not blocks:
        return None
    whole = fold(" ".join(t["text"] for t in turns))
    hit = []
    for number, title in blocks:
        words = [w for w in fold(title).split() if len(w) > 4]
        if words and sum(1 for w in words if w in whole) >= max(1, len(words) // 2):
            hit.append(number)
    return hit


START_MARKERS = ("# === INTERVIEW START ===", "# === INICIO ENTREVISTA ===")


def interview_text(transcript: str) -> str:
    """The part of the file that gets counted.

    One file per interview holds everything: a header, the live notes taken in
    the room, the small talk before the interviewee joined, and the interview.
    Comment lines ('# ...') are never counted. If a start marker is
    present, only what follows it is counted, so the small talk before the
    interviewee joins does not inflate the interviewer's share.
    """
    lines = transcript.splitlines()
    for i, line in enumerate(lines):
        if line.strip() in START_MARKERS:
            lines = lines[i + 1:]
            break
    return "\n".join(l for l in lines if not is_comment(l))


def is_comment(line: str) -> bool:
    """A '#' followed by a space, or a bare '#'. Not '#1 priority' or '#hashtag':
    those are words someone said, and a turn can continue on such a line."""
    stripped = line.strip()
    return stripped == "#" or stripped.startswith("# ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Count an interview transcript.")
    parser.add_argument("transcript")
    parser.add_argument("--interviewer", required=True,
                        help="Speaker label of the interviewer. Never guessed.")
    parser.add_argument("--product", default="",
                        help="Comma-separated terms for your own product or solution.")
    parser.add_argument("--guide", default=None,
                        help="Master guide, to report which blocks came up.")
    parser.add_argument("--patterns", default=None,
                        help="Patterns module for another language. Defaults to Spanish.")
    args = parser.parse_args()

    path = Path(args.transcript)
    if not path.exists():
        raise SystemExit(f"Transcript not found: {path}")

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    patterns = load_patterns(args.patterns)
    turns = parse(interview_text(path.read_text(encoding="utf-8", errors="ignore")))

    if not turns:
        raise SystemExit(
            "No speaker labels found. This file cannot be counted.\n"
            "Expected lines like 'Name: ...' or '[Name] ...'.\n"
            "Write the feedback without numbers and say the transcript had no labels. "
            "Do not estimate.")

    products = [p.strip() for p in args.product.split(",") if p.strip()]
    result = count(turns, args.interviewer, patterns, products,
                   guide_coverage(args.guide, turns))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
