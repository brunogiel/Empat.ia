#!/usr/bin/env python3
"""Check that every quote exists in its interview transcript, in the person's own channel.

A quote that is only close to the transcript, or that the interviewer said, is
the kind of error a reader never catches by eye. This script catches it by
search, not by impression: the same input returns the same verdicts.

Sources of quotes (pick one):
  --evidence          every quote row of _engine/evidence.md
  --json FILE         [{"id": "...", "int": "INT-004", "quote": "..."}]
  --cases             every "quote" field (any depth) of 5-debrief/cases/INT-*.json
  --file FILE         HTML: quotes inside an element carrying data-int="INT-004"

Transcripts are found as <raw>/<INT-ID>-*transcript*. The person's words are the
lines labelled "System audio" and the interviewer's the lines labelled
"Microphone" (the recorder export format); change them with --person-label and
--interviewer-label. Speaker labels are read with count_interview.parse, so both
labelling shapes it understands work here too.

Verdicts:
  OK           found verbatim (ignoring accents, case and punctuation) in the person's channel
  LITERAL~     found with small differences (ratio >= 0.9); the real text is shown, you decide
  INTERVIEWER  found, but the interviewer said it
  FAIL         not found: drop it or fix it
  SHORT        fewer than 3 words: too short to verify, not counted as a problem
  NO_TRANSCRIPT  no transcript for that interview ID: reported, not guessed

A correction in square brackets inside a quote ("[Acme]") is ignored on both
sides. Never estimates. Exit code 1 if there is any FAIL.

Usage:
  python3 scripts/verify_quotes.py --evidence
  python3 scripts/verify_quotes.py --cases --only-problems
  python3 scripts/verify_quotes.py --json quotes.json --raw path/to/_raw
  python3 scripts/verify_quotes.py --file report.html --person-label "Speaker 2"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import count_interview  # noqa: E402  (speaker-label reading lives there, not here)

THRESHOLD = 0.9
MIN_WORDS = 3
PROBLEMS = {"LITERAL~", "INTERVIEWER", "FAIL", "NO_TRANSCRIPT"}
QUOTE_MARKS = re.compile(r"«([^»]+)»|“([^”]+)”|\"([^\"]+)\"")
ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\]|\[…\])\s*")


def norm(text: str) -> str:
    """Lowercase, no accents, no punctuation, no [bracketed corrections]."""
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_transcript(raw: Path, int_id: str):
    for pattern in (f"{int_id}-*transcript*", f"{int_id}-*.txt"):
        hits = sorted(p for p in raw.glob(pattern) if p.is_file())
        if hits:
            return hits[0]
    return None


def channels(path: Path, person_label: str, interviewer_label: str):
    """Return (person_text, interviewer_text), both normalised."""
    text = path.read_text(encoding="utf-8")
    p, i = person_label.lower(), interviewer_label.lower()
    person, interviewer = [], []
    turns = count_interview.parse(text)
    if turns:
        for turn in turns:
            speaker = turn["speaker"].lower()
            if speaker.startswith(p):
                person.append(turn["text"])
            elif speaker.startswith(i):
                interviewer.append(turn["text"])
    else:  # too few labelled turns for the frequency heuristic: plain line prefixes
        for line in text.splitlines():
            head, _, body = line.partition(":")
            if head.lower().startswith(p):
                person.append(body)
            elif head.lower().startswith(i):
                interviewer.append(body)
    return norm(" ".join(person)), norm(" ".join(interviewer))


def best_fuzzy(quote: str, corpus: str):
    q, words = quote.split(), corpus.split()
    n = len(q)
    if n == 0 or not words:
        return 0.0, ""
    best, best_txt = 0.0, ""
    for size in {max(1, n - 2), n, n + 2}:
        for start in range(0, max(1, len(words) - size + 1)):
            window = " ".join(words[start:start + size])
            ratio = SequenceMatcher(None, quote, window).ratio()
            if ratio > best:
                best, best_txt = ratio, window
    return best, best_txt


class Verifier:
    def __init__(self, raw: Path, person_label: str, interviewer_label: str):
        self.raw, self.person_label, self.interviewer_label = raw, person_label, interviewer_label
        self._cache: dict = {}

    def check(self, int_id: str, quote: str):
        q = norm(quote)
        if len(q.split()) < MIN_WORDS:
            return "SHORT", ""
        if int_id not in self._cache:
            path = find_transcript(self.raw, int_id)
            self._cache[int_id] = (channels(path, self.person_label, self.interviewer_label)
                                   if path else None)
        found = self._cache[int_id]
        if found is None:
            return "NO_TRANSCRIPT", f"nothing matching {int_id}-*transcript* in {self.raw}"
        person, interviewer = found
        if q in person:
            return "OK", ""
        if q in interviewer:
            return "INTERVIEWER", ""
        ratio, text = best_fuzzy(q, person)
        if ratio >= THRESHOLD:
            return "LITERAL~", f"{ratio:.2f} | real text: {text}"
        return "FAIL", f"best match {ratio:.2f}: {text[:120]}"


def pieces(fragment: str):
    for piece in ELLIPSIS.split(fragment):
        if piece.strip():
            yield piece.strip()


def from_evidence(path: Path):
    """Rows whose Type cell is 'quote' (or 'cita'). Columns: ID | Interview | Profile | Type | Evidence."""
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6 or not re.match(r"INT-\d", cells[2]):
            continue
        if cells[4].lower() not in ("quote", "cita"):
            continue
        marked = ["".join(m) for m in QUOTE_MARKS.findall(cells[5])]
        for fragment in marked or [cells[5]]:
            for piece in pieces(fragment):
                items.append({"id": cells[1], "int": cells[2], "quote": piece})
    return items


def from_cases(folder: Path):
    """Every 'quote' (or 'cita') string at any depth of each INT-*.json sheet."""
    items = []

    def walk(node, int_id, where):
        if isinstance(node, dict):
            for key in ("quote", "cita"):
                if isinstance(node.get(key), str) and node[key].strip():
                    tag = where + (" [induced]" if node.get("induced") or node.get("inducido") else "")
                    items.append({"id": tag, "int": int_id, "quote": node[key]})
            for key, value in node.items():
                walk(value, int_id, f"{where}.{key}")
        elif isinstance(node, list):
            for n, value in enumerate(node):
                walk(value, int_id, f"{where}[{n}]")

    for sheet in sorted(folder.glob("INT-*.json")):
        data = json.loads(sheet.read_text(encoding="utf-8"))
        walk(data, data.get("id", sheet.stem) if isinstance(data, dict) else sheet.stem, sheet.stem)
    return items


def from_file(path: Path):
    items = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r'data-int="(INT-[\w-]+)"[^>]*>(.*?)</', text, re.S):
        marked = ["".join(q) for q in QUOTE_MARKS.findall(m.group(2))]
        for fragment in marked or [m.group(2)]:
            items.append({"id": m.group(1), "int": m.group(1),
                          "quote": re.sub(r"<[^>]+>", "", fragment).strip()})
    return items


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify quotes against interview transcripts.")
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--evidence", action="store_true", help="quote rows of the evidence ledger")
    source.add_argument("--json", metavar="FILE", help="list of {id, int, quote}")
    source.add_argument("--cases", action="store_true", help="the case sheets")
    source.add_argument("--file", metavar="FILE", help="HTML with data-int markers")
    ap.add_argument("--root", default=".", help="discovery folder (default: current directory)")
    ap.add_argument("--raw", help="transcripts folder (default: <root>/4-field/_raw)")
    ap.add_argument("--evidence-file", help="ledger path (default: <root>/_engine/evidence.md)")
    ap.add_argument("--cases-dir", help="case sheets folder (default: <root>/5-debrief/cases)")
    ap.add_argument("--person-label", default="System audio",
                    help="speaker label of the person interviewed (prefix match)")
    ap.add_argument("--interviewer-label", default="Microphone",
                    help="speaker label of the interviewer (prefix match)")
    ap.add_argument("--only-problems", action="store_true", help="hide OK and SHORT")
    a = ap.parse_args(argv)

    root = Path(a.root)
    raw = Path(a.raw) if a.raw else root / "4-field" / "_raw"
    if a.evidence:
        items = from_evidence(Path(a.evidence_file) if a.evidence_file else root / "_engine" / "evidence.md")
    elif a.json:
        items = json.loads(Path(a.json).read_text(encoding="utf-8"))
    elif a.cases:
        items = from_cases(Path(a.cases_dir) if a.cases_dir else root / "5-debrief" / "cases")
    else:
        items = from_file(Path(a.file))

    verifier = Verifier(raw, a.person_label, a.interviewer_label)
    counts: dict = {}
    for item in items:
        verdict, detail = verifier.check(item["int"], item["quote"])
        counts[verdict] = counts.get(verdict, 0) + 1
        if a.only_problems and verdict not in PROBLEMS:
            continue
        print(f"{verdict:13} {item['id']:14} «{item['quote'][:90]}»"
              + (f"\n{'':28}{detail}" if detail else ""))
    print("\nSummary:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "no quotes found",
          f"| total {len(items)}")
    return 1 if counts.get("FAIL") else 0


if __name__ == "__main__":
    sys.exit(main())
