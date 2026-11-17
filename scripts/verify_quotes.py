#!/usr/bin/env python3
"""Check that every quote exists in its interview transcript, in the person's own channel.

A quote that is only close to the transcript, or that the interviewer said, is
the kind of error a reader never catches by eye. This script catches it by
search, not by impression: the same input returns the same verdicts.

Sources of quotes (pick one):
  --evidence          every quote row of _engine/evidence.md
  --json FILE         [{"id": "...", "int": "INT-004", "quote": "..."}]
  --cases             every "quote" field (any depth) of 5-debrief/cases/INT-*.json
                      (and VAL-*.json)
  --file FILE         HTML: quotes inside an element carrying data-int="INT-004"
                      (or data-int="VAL-001"); every other quoted fragment of the
                      file is still checked against the vetoed list
  --scan FILE [...]   any text, Markdown or HTML: only look for vetoed quotes

Transcripts are found as <raw>/<ID>-*transcript*. Interviews (INT-) are read from
4-field/_raw and validation sessions (VAL-) from 7-validation/_raw; --raw and
--val-raw change the folders (--raw alone serves both kinds). The person's words
are the lines labelled "System audio" and the interviewer's the lines labelled
"Microphone" (the recorder export format); change them with --person-label and
--interviewer-label. Speaker labels are read with count_interview.parse, so both
labelling shapes it understands work here too. A clock prefix ("[3:05]",
"[1:02:03]", "(3:05)") is dropped before reading, and a line with no speaker label
belongs to whoever spoke last.

Verdicts:
  OK           found verbatim (ignoring accents, case and punctuation) in the person's channel
  CUT?         found verbatim AND the cut may change the meaning: a negation right before
               the fragment, "but" / "pero" right after it, or the fragment starts or ends
               in the middle of a sentence. The real context is shown; you decide
  LITERAL~     found with small differences (ratio >= 0.9); the real text is shown, you decide
  INTERVIEWER  found, but the interviewer said it
  FAIL         not found: drop it or fix it
  VETOED       the evidence ledger marks this quote as vetoed (Use column): it must not
               appear in what you are checking
  SHORT        fewer than 3 words: too short to verify, not counted as a problem
  NO_TRANSCRIPT  no transcript for that interview ID: reported, not guessed

Negations and contrast words are read in English and Spanish. A transcript with
almost no sentence punctuation switches the mid-sentence rule off (it would flag
everything); --no-midsentence switches it off by hand.

A correction in square brackets inside a quote ("[Acme]") is ignored on both
sides. Never estimates. Exit code 1 if there is any FAIL or VETOED; CUT? is for a
person to judge and does not fail the run.

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
PROBLEMS = {"LITERAL~", "INTERVIEWER", "FAIL", "NO_TRANSCRIPT", "CUT?", "VETOED"}
FAILS = {"FAIL", "VETOED"}
QUOTE_MARKS = re.compile(r"«([^»]+)»|“([^”]+)”|\"([^\"]+)\"")
ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\]|\[…\])\s*")
ITEM_ID = r"(?:INT|VAL)-\d"

# How far around a fragment the cut check looks.
WORDS_BEFORE = 8
# Below this share of sentence-ending marks the transcript has no usable
# punctuation, so "starts or ends mid-sentence" would flag every quote.
MIN_PUNCTUATION = 1 / 60

# Words read after normalisation: lowercase, no accents ("jamás" is "jamas"),
# apostrophes split ("don't" is "don" + "t").
NEGATIONS = {
    # English
    "no", "not", "never", "nor", "neither", "none", "nobody", "nothing", "nowhere",
    "without", "hardly", "barely", "cannot", "cant", "dont", "doesnt", "didnt",
    "isnt", "arent", "wasnt", "werent", "wont", "wouldnt", "couldnt", "shouldnt",
    "havent", "hasnt", "hadnt", "aint",
    # Spanish
    "nunca", "jamas", "ni", "tampoco", "sin", "nada", "nadie", "ningun", "ninguno",
    "ninguna", "apenas",
}
NEGATION_STEMS = {"don", "doesn", "didn", "isn", "aren", "wasn", "weren", "won",
                  "wouldn", "couldn", "shouldn", "can", "haven", "hasn", "hadn",
                  "ain", "mustn", "needn"}  # the word before a lone "t"
CONTRASTS = {"but", "although", "though", "except", "however", "yet", "unless",
             "pero", "aunque", "sino", "salvo", "excepto"}

# A clock before a line or a label: "[3:05] Name: ...", "(1:02:03) Name: ...",
# "3:05 Name: ...", "Name [3:05]: ...", or a line holding only a clock.
_CLOCK = r"\d{1,2}:\d{2}(?::\d{2})?"
_LABEL_AHEAD = r"(?=\[?[^\s:\[\].?!][^:\[\].?!\n]{0,48}\]?:\s)"
CLOCK_ALONE = re.compile(rf"^[ \t]*[\[(]?{_CLOCK}[\])]?[ \t]*$\n?", re.M)
CLOCK_LEAD = re.compile(rf"^[ \t]*[\[(]{_CLOCK}[\])][ \t]*[-\u2013\u2014]?[ \t]*", re.M)
CLOCK_LEAD_BARE = re.compile(rf"^[ \t]*{_CLOCK}[ \t]+{_LABEL_AHEAD}", re.M)
CLOCK_AFTER_LABEL = re.compile(rf"[ \t]*[\[(]{_CLOCK}[\])](?=:)")
SENTENCE_END = re.compile(r"[.?!\u2026][\"'\u201d\u2019\u00bb)\]]*$")


def norm(text: str) -> str:
    """Lowercase, no accents, no punctuation, no [bracketed corrections]."""
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_clocks(text: str) -> str:
    """Drop the time prefixes some exports put before every line."""
    text = text.replace("\r\n", "\n")
    text = CLOCK_ALONE.sub("", text)
    text = CLOCK_LEAD.sub("", text)
    text = CLOCK_LEAD_BARE.sub("", text)
    return CLOCK_AFTER_LABEL.sub("", text)


def raw_folder_for(root: Path, int_id: str) -> Path:
    """Where the transcripts of this kind of session live by default."""
    if int_id.upper().startswith("VAL-"):
        return root / "7-validation" / "_raw"
    return root / "4-field" / "_raw"


def find_transcript(raw: Path, int_id: str):
    for pattern in (f"{int_id}-*transcript*", f"{int_id}-*.txt"):
        hits = sorted(p for p in raw.glob(pattern) if p.is_file())
        if hits:
            return hits[0]
    return None


def read_turns(text: str, person_label: str, interviewer_label: str):
    """[(who, text)] with who in person / interviewer / other.

    A line with no speaker label is the continuation of whoever spoke last, in
    both the frequency parser and the plain-prefix fallback."""
    text = strip_clocks(text)
    p, i = person_label.lower(), interviewer_label.lower()

    def who_is(speaker: str) -> str:
        speaker = speaker.lower().strip()
        if speaker.startswith(p):
            return "person"
        if speaker.startswith(i):
            return "interviewer"
        return "other"

    turns = count_interview.parse(text)
    if turns:
        return [(who_is(t["speaker"]), t["text"]) for t in turns]
    # Too few labelled turns for the frequency heuristic: plain line prefixes.
    out: list = []
    for line in text.splitlines():
        head, sep, body = line.partition(":")
        label_like = bool(sep) and 0 < len(head) <= 50 and not re.search(r"[.?!]", head)
        who = who_is(head) if label_like else None
        if who in ("person", "interviewer"):
            out.append([who, body])
        elif label_like and len(head.split()) <= 3 and head[:1].isupper() and out:
            out.append(["other", body])  # a third speaker, not a continuation
        elif out:
            out[-1][1] += " " + line  # no label: whoever spoke last is still talking
    return [(who, t) for who, t in out]


class Channel:
    """One speaker's words, with the marks the cut check needs."""

    def __init__(self, turns):
        self.words: list = []
        self.sentence_end: list = []
        self.turn_start: list = []
        for turn in turns:
            first = True
            for raw in re.sub(r"\[[^\]]*\]", " ", turn).split():
                pieces = norm(raw).split()
                if not pieces:  # punctuation only: it can still close a sentence
                    if self.sentence_end and SENTENCE_END.search(raw):
                        self.sentence_end[-1] = True
                    continue
                for piece in pieces:
                    self.words.append(piece)
                    self.sentence_end.append(False)
                    self.turn_start.append(first)
                    first = False
                if SENTENCE_END.search(raw):
                    self.sentence_end[-1] = True
        self.text = " ".join(self.words)
        self.punctuated = (sum(self.sentence_end) / len(self.words) >= MIN_PUNCTUATION
                           if self.words else False)

    def occurrences(self, quote_words: list):
        n = len(quote_words)
        return [s for s in range(len(self.words) - n + 1)
                if self.words[s:s + n] == quote_words]

    def cut_reasons(self, start: int, end: int, midsentence: bool = True):
        """Why the fragment words[start:end] may mean something else in context."""
        reasons = []
        before = []
        for k in range(start - 1, max(0, start - WORDS_BEFORE) - 1, -1):
            if self.sentence_end[k]:
                break
            before.insert(0, self.words[k])
            if self.turn_start[k]:
                break
        for n, word in enumerate(before):
            if word in NEGATIONS or (word == "t" and n and before[n - 1] in NEGATION_STEMS):
                reasons.append(f"negation before the fragment: \"{word}\"")
                break
        after = []
        if end < len(self.words) and not self.turn_start[end]:
            after = self.words[end:end + 4]
            if after and after[0] in CONTRASTS:
                reasons.append(f"contrast right after the fragment: \"{after[0]}\"")
        if midsentence and self.punctuated:
            if start > 0 and not self.turn_start[start] and not self.sentence_end[start - 1]:
                reasons.append("starts in the middle of a sentence")
            if end < len(self.words) and not self.turn_start[end] and not self.sentence_end[end - 1]:
                reasons.append("ends in the middle of a sentence")
        context = f"...{' '.join(before)} [QUOTE] {' '.join(after)}..."
        return reasons, context


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


def contains_words(haystack: str, needle: str) -> bool:
    """Whole-word substring: 'mean' is not inside 'meaning'."""
    return f" {needle} " in f" {haystack} "


class Verifier:
    def __init__(self, raw: Path, person_label: str, interviewer_label: str,
                 val_raw: Path | None = None, vetoed: dict | None = None,
                 midsentence: bool = True):
        self.raw, self.val_raw = raw, val_raw or raw
        self.person_label, self.interviewer_label = person_label, interviewer_label
        self.vetoed = vetoed or {}  # normalised quote -> reason
        self.midsentence = midsentence
        self._cache: dict = {}

    def folder_for(self, int_id: str) -> Path:
        return self.val_raw if int_id.upper().startswith("VAL-") else self.raw

    def channels_of(self, int_id: str):
        if int_id not in self._cache:
            path = find_transcript(self.folder_for(int_id), int_id)
            if path is None:
                self._cache[int_id] = None
            else:
                turns = read_turns(path.read_text(encoding="utf-8"),
                                   self.person_label, self.interviewer_label)
                self._cache[int_id] = (
                    Channel([t for who, t in turns if who == "person"]),
                    Channel([t for who, t in turns if who == "interviewer"]))
        return self._cache[int_id]

    def vetoed_reason(self, q: str):
        """The reason, if the normalised quote q is, or contains, or sits inside, a vetoed one."""
        for veto, reason in self.vetoed.items():
            if contains_words(q, veto) or contains_words(veto, q):
                return reason or "no reason given"
        return None

    def check(self, int_id: str, quote: str):
        q = norm(quote)
        if len(q.split()) < MIN_WORDS:
            return "SHORT", ""
        reason = self.vetoed_reason(q)
        if reason is not None:
            return "VETOED", f"marked vetoed in the ledger: {reason}"
        found = self.channels_of(int_id)
        if found is None:
            return "NO_TRANSCRIPT", f"nothing matching {int_id}-*transcript* in {self.folder_for(int_id)}"
        person, interviewer = found
        spots = person.occurrences(q.split())
        if spots:
            n = len(q.split())
            verdicts = [person.cut_reasons(s, s + n, self.midsentence) for s in spots]
            if any(not reasons for reasons, _ in verdicts):
                return "OK", ""
            reasons, context = verdicts[0]
            return "CUT?", "literal match, but " + "; ".join(reasons) + f"\n{'':28}{context}"
        if contains_words(interviewer.text, q):
            return "INTERVIEWER", ""
        ratio, text = best_fuzzy(q, person.text)
        if ratio >= THRESHOLD:
            return "LITERAL~", f"{ratio:.2f} | real text: {text}"
        return "FAIL", f"best match {ratio:.2f}: {text[:120]}"


def pieces(fragment: str):
    for piece in ELLIPSIS.split(fragment):
        if piece.strip():
            yield piece.strip()


def read_ledger(path: Path):
    """Rows of the evidence ledger that carry a quote.

    Columns: ID | Interview | Profile | Type | Evidence | ... | Use in synthesis.
    The Use column is found by its header, so a ledger with fewer or more columns
    still works. Its value 'vetoed' (or 'vetoed: reason') marks the row as vetoed;
    the Spanish 'vetada' is read too."""
    rows, use_at = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        lowered = [c.lower() for c in cells]
        if "type" in lowered:
            use_at = next((n for n, c in enumerate(lowered)
                           if re.match(r"(use|uso)\b", c)), None)
            continue
        if len(cells) < 6 or not re.match(ITEM_ID, cells[2]):
            continue
        if cells[4].lower() not in ("quote", "cita"):
            continue
        use = cells[use_at] if use_at is not None and use_at < len(cells) else ""
        match = re.match(r"(vetoed|vetada)\b\s*:?\s*(.*)", use, re.I)
        rows.append({"id": cells[1], "int": cells[2], "cell": cells[5],
                     "vetoed": bool(match), "reason": match.group(2).strip() if match else ""})
    return rows


def quotes_of(cell: str):
    marked = ["".join(m) for m in QUOTE_MARKS.findall(cell)]
    for fragment in marked or [cell]:
        yield from pieces(fragment)


def from_evidence(path: Path):
    """Quote rows that are in use. Vetoed rows are listed in the ledger on purpose
    and are not checked here; they are what the other sources are checked against."""
    return [{"id": r["id"], "int": r["int"], "quote": piece}
            for r in read_ledger(path) if not r["vetoed"] for piece in quotes_of(r["cell"])]


def vetoed_quotes(path: Path):
    """{normalised quote: reason} for every vetoed row of the ledger."""
    found = {}
    for row in read_ledger(path):
        if row["vetoed"]:
            for piece in quotes_of(row["cell"]):
                n = norm(piece)
                if len(n.split()) >= MIN_WORDS:
                    found[n] = row["reason"]
    return found


def from_cases(folder: Path):
    """Every 'quote' (or 'cita') string at any depth of each INT-*.json / VAL-*.json sheet."""
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

    for sheet in sorted(list(folder.glob("INT-*.json")) + list(folder.glob("VAL-*.json"))):
        data = json.loads(sheet.read_text(encoding="utf-8"))
        walk(data, data.get("id", sheet.stem) if isinstance(data, dict) else sheet.stem, sheet.stem)
    return items


def from_file(path: Path):
    items = []
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r'data-int="((?:INT|VAL)-[\w-]+)"[^>]*>(.*?)</', text, re.S):
        marked = ["".join(q) for q in QUOTE_MARKS.findall(m.group(2))]
        for fragment in marked or [m.group(2)]:
            items.append({"id": m.group(1), "int": m.group(1),
                          "quote": re.sub(r"<[^>]+>", "", fragment).strip()})
    return items


def quoted_fragments(path: Path):
    """Every quoted fragment of any text, Markdown or HTML file, for the vetoed check."""
    text = re.sub(r"<[^>]+>", "", path.read_text(encoding="utf-8"))
    return [{"id": path.name, "int": "-", "quote": piece}
            for m in QUOTE_MARKS.findall(text) for piece in pieces("".join(m))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify quotes against interview transcripts.")
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--evidence", action="store_true", help="quote rows of the evidence ledger")
    source.add_argument("--json", metavar="FILE", help="list of {id, int, quote}")
    source.add_argument("--cases", action="store_true", help="the case sheets")
    source.add_argument("--file", metavar="FILE", help="HTML with data-int markers")
    source.add_argument("--scan", metavar="FILE", nargs="+",
                        help="any text, Markdown or HTML file: look for vetoed quotes only")
    ap.add_argument("--root", default=".", help="discovery folder (default: current directory)")
    ap.add_argument("--raw", help="interview transcripts folder (default: <root>/4-field/_raw)")
    ap.add_argument("--val-raw", help="validation transcripts folder "
                                      "(default: <root>/7-validation/_raw, or --raw when that is given)")
    ap.add_argument("--evidence-file", help="ledger path (default: <root>/_engine/evidence.md)")
    ap.add_argument("--cases-dir", help="case sheets folder (default: <root>/5-debrief/cases)")
    ap.add_argument("--person-label", default="System audio",
                    help="speaker label of the person interviewed (prefix match)")
    ap.add_argument("--interviewer-label", default="Microphone",
                    help="speaker label of the interviewer (prefix match)")
    ap.add_argument("--no-midsentence", action="store_true",
                    help="CUT? only for a negation before or a contrast word after the fragment")
    ap.add_argument("--only-problems", action="store_true", help="hide OK and SHORT")
    a = ap.parse_args(argv)

    root = Path(a.root)
    raw = Path(a.raw) if a.raw else root / "4-field" / "_raw"
    val_raw = Path(a.val_raw) if a.val_raw else (raw if a.raw else root / "7-validation" / "_raw")
    ledger = Path(a.evidence_file) if a.evidence_file else root / "_engine" / "evidence.md"
    vetoed = vetoed_quotes(ledger) if ledger.is_file() else {}

    if a.evidence:
        if not ledger.is_file():
            print(f"No evidence ledger at {ledger}", file=sys.stderr)
            return 2
        items = from_evidence(ledger)
    elif a.json:
        items = json.loads(Path(a.json).read_text(encoding="utf-8"))
    elif a.cases:
        items = from_cases(Path(a.cases_dir) if a.cases_dir else root / "5-debrief" / "cases")
    elif a.scan:
        items = [i for f in a.scan for i in quoted_fragments(Path(f))]
    else:
        items = from_file(Path(a.file))
        seen = {norm(i["quote"]) for i in items}
        items += [i for i in quoted_fragments(Path(a.file)) if norm(i["quote"]) not in seen]

    verifier = Verifier(raw, a.person_label, a.interviewer_label, val_raw, vetoed,
                        midsentence=not a.no_midsentence)
    counts: dict = {}
    for item in items:
        if a.scan or item["int"] == "-":  # no transcript to read: only the vetoed list applies
            q = norm(item["quote"])
            reason = verifier.vetoed_reason(q) if len(q.split()) >= MIN_WORDS else None
            if reason is None:
                continue
            verdict, detail = "VETOED", f"marked vetoed in the ledger: {reason}"
        else:
            verdict, detail = verifier.check(item["int"], item["quote"])
        counts[verdict] = counts.get(verdict, 0) + 1
        if a.only_problems and verdict not in PROBLEMS:
            continue
        print(f"{verdict:13} {item['id']:14} «{item['quote'][:90]}»"
              + (f"\n{'':28}{detail}" if detail else ""))
    print("\nSummary:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "no quotes found",
          f"| total {sum(counts.values())}")
    return 1 if any(counts.get(v) for v in FAILS) else 0


if __name__ == "__main__":
    sys.exit(main())
