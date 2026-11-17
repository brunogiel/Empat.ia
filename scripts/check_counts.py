#!/usr/bin/env python3
"""Check the counts and the universals in what you are about to hand out.

A count written by hand drifts. "4 of 5" in an insight, "2 people" in the pattern
it comes from, "most" in a summary: each one reads fine alone and none of them was
counted. This script counts, and it does it the same way every run. It does not
read tone. It reads numbers, tables and keywords.

What it checks, in files you name (findings, insights, principles, the report, the
HTML you share):

  1. Every "X of N" ("4 of 5", "four out of five", "4 de 5", "cuatro de cinco") is
     compared with the pattern it sits next to. The pattern is the nearest pattern
     ID (PAT-01...) within 200 characters. X has to equal the number of different
     people in that pattern's row of the support table.
  2. Universals are listed: nobody, no one, everyone, all of them, most, always,
     never, "5 of 5", and their Spanish forms (nadie, ninguno, todos, la mayoria,
     siempre, nunca). Each one comes with the transcript lines that could break it:
     for a negative claim ("nobody uses the discount code"), the turns that
     mention the same words; for a positive one ("everyone compares prices"), the
     interviews with no turn that does. Text inside quote marks is the person's
     voice, not your claim, and is skipped.
  3. An "X of N" with N of 2 or less never carries a success tick (a tick mark or
     the words worked / funcionó). Two people are an anecdote, not a result.
  4. With --orphans: every pattern held by 3 or more people (--min-people) hangs
     from an insight, or has a line saying why it does not.

The support table (documented here because it is the format): a Markdown table in
findings.md whose first column is a pattern ID, `PAT-01`, `PAT-02`..., and one
column whose header contains "Evidence". The people of a pattern are the different
interview or validation IDs written in that cell: INT-001-03 and INT-001-07 are one
person, INT-004-01 is another. Cells under other headers ("Who does not show it")
are not read as support. The prefix PAT can be changed with --pattern-prefix.

  | ID     | Pattern             | Evidence                 | Who does not show it |
  |--------|---------------------|--------------------------|----------------------|
  | PAT-01 | Compares before buying | INT-001-03, INT-002-01, INT-004-02 | INT-003 |

In the insights ("Prioritized insights" in findings.md, or a file you name with
--insights), a pattern "hangs from" an insight when its ID is written anywhere in
that section. A pattern with no insight is explained by one line that holds its
ID and the words "no insight" or "sin insight":
`PAT-07: no insight, because it only describes the setting.`

Verdicts:
  MISMATCH      "X of N" next to PAT-nn, and PAT-nn has a different number of people
  BAD_FRACTION  X is bigger than N
  UNKNOWN_ID    the nearest ID is not in the support table
  SMALL_N       N <= 2 with a success tick
  UNIVERSAL     a universal claim: look at the candidates it lists
  UNLINKED      an "X of N" with no pattern ID within 200 characters: nothing to compare
  ORPHAN        (--orphans) a strong pattern with no insight and no explanation

Exit code 1 if there is any MISMATCH, BAD_FRACTION, UNKNOWN_ID, SMALL_N or ORPHAN.
UNIVERSAL and UNLINKED are for a person; --strict makes them fail the run too.
Exit code 2 when an input file is missing.

Usage (run from inside the project's discovery/ folder, or pass --root):
  python3 <method-root>/scripts/check_counts.py 5-debrief/findings.md 5-debrief/principles.md
  python3 <method-root>/scripts/check_counts.py share/report.html --patterns 5-debrief/findings.md
  python3 <method-root>/scripts/check_counts.py --orphans
  python3 <method-root>/scripts/check_counts.py notes.md --raw path/to/_raw --person-label "Speaker 2"
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_quotes  # noqa: E402  (one transcript parser for the whole method)

DISTANCE = 200
MAX_CANDIDATES = 5
FAILING = {"MISMATCH", "BAD_FRACTION", "UNKNOWN_ID", "SMALL_N", "ORPHAN"}
SOFT = {"UNIVERSAL", "UNLINKED"}

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
    "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
}
_NUM = r"(\d{1,3}|" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + r")"
FRACTION = re.compile(rf"(?<![\w/]){_NUM}\s+(?:out\s+of|of|de)\s+{_NUM}(?![\w/])", re.I)
PERSON_ID = re.compile(r"\b(?:INT|VAL)-\d+[a-z]?(?!\w)")
TICK = re.compile(r"[✓✔✅☑]|\b(?:worked|works|funcion[oó]|funciona)\b", re.I)

NEGATIVE = [r"nobody", r"no one", r"none of them", r"none", r"not a single \w+",
            r"never", r"nadie", r"ninguno", r"ninguna", r"ningun", r"nunca", r"jamas",
            r"ni uno"]
POSITIVE = [r"everyone", r"everybody", r"all of them", r"all participants",
            r"all of the \w+", r"always",
            r"(?<!the )(?<!at )(?<!a )most(?! (?:important|common|likely|useful))",
            r"the majority", r"todos(?! modos)", r"todas", r"siempre", r"la mayoria",
            r"mayoria", r"la mayor parte"]
NEG_RE = re.compile(r"\b(?:" + "|".join(NEGATIVE) + r")\b")
POS_RE = re.compile(r"\b(?:" + "|".join(POSITIVE) + r")\b")

STOPWORDS = set("""
about after again against also been because before being between could does doing during
each even every from have having here into just like many more most much only other over
people person should since some such than that their them then there these they this
those through under until very were what when where which while will with would your cual cuales como cuando donde entre esta
estan este estos hacia hasta muy otra otro otros para pero porque quien sino sobre
solo tambien tiene tienen todo todos todas toda tras una unas unos nadie ninguno ninguna
nunca siempre jamas
""".split())


def fold_char(c: str) -> str:
    """One character in, one character out: lowercase, no accent. Offsets survive."""
    d = "".join(x for x in unicodedata.normalize("NFD", c.lower())
                if unicodedata.category(x) != "Mn")
    return d if len(d) == 1 else (c.lower()[:1] or c)


def fold(text: str) -> str:
    return "".join(fold_char(c) for c in text)


def mask_quotes(text: str) -> str:
    """Blank out what sits between quote marks: it is the person's voice."""
    def blank(m):
        return " " * (m.end() - m.start())
    for pattern in (r"«[^»]*»", r"“[^”]*”", r"\"[^\"\n]*\""):
        text = re.sub(pattern, blank, text)
    return text


def to_number(token: str) -> int:
    return int(token) if token.isdigit() else NUMBER_WORDS[fold(token)]


def read_patterns(path: Path, prefix: str):
    """{pattern ID: set of person IDs} from the support table."""
    id_re = re.compile(rf"{re.escape(prefix)}-\d+", re.I)
    lines = path.read_text(encoding="utf-8").splitlines()
    patterns: dict = {}
    headers: list = []
    for n, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        nxt = lines[n + 1].strip() if n + 1 < len(lines) else ""
        if re.match(r"^\|?\s*:?-{3,}", nxt):
            headers = [c.lower() for c in cells]
            continue
        if not cells or not id_re.match(cells[0]):
            continue
        evidence = next((i for i, h in enumerate(headers) if "evidence" in h), None)
        if evidence is not None and evidence < len(cells):
            text = cells[evidence]
        else:
            text = " ".join(c for i, c in enumerate(cells[1:], 1)
                            if not (i < len(headers) and re.search(r"not|except|exception", headers[i])))
        key = id_re.match(cells[0]).group(0).upper()
        patterns.setdefault(key, set()).update(PERSON_ID.findall(text))
    return patterns


def nearest_id(text: str, span: tuple, id_re) -> str | None:
    best, best_gap = None, DISTANCE + 1
    for m in id_re.finditer(text):
        gap = max(span[0] - m.end(), m.start() - span[1], 0)
        # The ID right before the claim wins a tie: it is the one being counted.
        if gap < best_gap or (gap == best_gap and m.end() <= span[0]):
            best, best_gap = m.group(0).upper(), gap
    return best


def line_of(text: str, pos: int):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    return text.count("\n", 0, pos) + 1, text[start:(end if end != -1 else len(text))]


def sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start), text.rfind("|", 0, start))
    right_candidates = [i for i in (text.find(".", end), text.find("\n", end), text.find("|", end)) if i != -1]
    right = min(right_candidates) if right_candidates else len(text)
    return re.sub(r"<[^>]+>|\s+", " ", text[left + 1:right]).strip()


def read_transcripts(folders, person_label: str, interviewer_label: str):
    """{person ID: [turn text, ...]}: the interviewee's turns only."""
    found: dict = {}
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in sorted(folder.iterdir()):
            m = re.match(r"((?:INT|VAL)-\d+[a-z]?)\b", path.name)
            if not m or not path.is_file() or m.group(1) in found:
                continue
            if "transcript" not in path.name.lower() and path.suffix.lower() not in (".txt", ".vtt"):
                continue
            turns = verify_quotes.read_turns(path.read_text(encoding="utf-8", errors="replace"),
                                             person_label, interviewer_label)
            found[m.group(1)] = [t for who, t in turns if who == "person"]
    return found


def keywords_of(sentence: str, universal: str) -> list:
    words = re.findall(r"[a-z]{4,}", fold(re.sub(r"\b(?:INT|VAL|PAT)-\d+\w*", " ", sentence)))
    skip = set(re.findall(r"[a-z]+", fold(universal))) | STOPWORDS
    out: list = []
    for w in words:
        if w not in skip and w not in out:
            out.append(w)
    return out[:8]


def search_transcripts(keys: list, transcripts: dict, negative: bool):
    """Turns that hold enough of the keywords (negative claim) or the interviews with none (positive)."""
    need = min(2, len(keys))
    stems = [k[:max(4, len(k) - 2)] for k in keys]  # "books" finds "book", "comparing" finds "compare"
    hits: dict = {}
    for person, turns in transcripts.items():
        for turn in turns:
            folded = fold(turn)
            if sum(1 for k in stems if k in folded) >= need:
                hits.setdefault(person, []).append(" ".join(turn.split()))
    if negative:
        return [(p, t[0][:140]) for p, t in sorted(hits.items())]
    return [(p, "") for p in sorted(transcripts) if p not in hits]


def check_file(path: Path, patterns: dict, id_re, transcripts: dict):
    text = path.read_text(encoding="utf-8")
    shown = mask_quotes(text)
    folded = fold(shown)
    findings = []

    def add(verdict, pos, claim, detail="", candidates=None):
        lineno, _ = line_of(text, pos)
        findings.append({"verdict": verdict, "where": f"{path.name}:{lineno}",
                         "claim": claim, "detail": detail, "candidates": candidates})

    counted = set()
    for m in FRACTION.finditer(shown):
        x, n = to_number(m.group(1)), to_number(m.group(2))
        counted.add(m.span())
        claim = m.group(0)
        _, whole_line = line_of(shown, m.start())
        if x > n:
            add("BAD_FRACTION", m.start(), claim, "the first number is bigger than the second")
            continue
        if n <= 2 and TICK.search(whole_line):
            add("SMALL_N", m.start(), claim,
                "two people or fewer: an anecdote, not something that 'worked'")
        target = nearest_id(shown, m.span(), id_re)
        if target is None:
            add("UNLINKED", m.start(), claim, f"no pattern ID within {DISTANCE} characters")
        elif target not in patterns:
            add("UNKNOWN_ID", m.start(), claim, f"{target} is not in the support table")
        elif len(patterns[target]) != x:
            people = ", ".join(sorted(patterns[target])) or "nobody"
            add("MISMATCH", m.start(), claim,
                f"{target} has {len(patterns[target])} in the support table ({people})")
        if x == n and n >= 3:
            add("UNIVERSAL", m.start(), claim, "everyone, said as a count",
                _candidates(sentence_around(shown, *m.span()), claim, transcripts, negative=False))

    for regex, negative in ((NEG_RE, True), (POS_RE, False)):
        for m in regex.finditer(folded):
            claim = shown[m.start():m.end()]
            sentence = sentence_around(shown, m.start(), m.end())
            add("UNIVERSAL", m.start(), claim, sentence[:160],
                _candidates(sentence, claim, transcripts, negative))
    return findings


def _candidates(sentence: str, universal: str, transcripts: dict, negative: bool):
    if not transcripts:
        return None
    keys = keywords_of(sentence, universal)
    if not keys:
        return []
    return search_transcripts(keys, transcripts, negative) + [("keys", ", ".join(keys))]


def insights_section(text: str, whole_if_missing: bool = True) -> str:
    """The insights part of a file.

    The insights live in findings.md under a heading that names them ("Prioritized
    insights"), next to the support table. Only that section counts: the table itself
    names every pattern, so reading the whole file would hide every orphan. A file
    with no such heading is read whole when it is a separate insights file, and as
    empty when it is the support table (no insights written yet: every strong pattern
    is then an orphan).
    """
    lines = text.splitlines()
    for n, line in enumerate(lines):
        head = re.match(r"^(#{1,6})\s+(.*)$", line)
        if head and re.search(r"insights?", head.group(2), re.I):
            level = len(head.group(1))
            end = len(lines)
            for m in range(n + 1, len(lines)):
                nxt = re.match(r"^(#{1,6})\s", lines[m])
                if nxt and len(nxt.group(1)) <= level:
                    end = m
                    break
            return "\n".join(lines[n:end])
    return text if whole_if_missing else ""


def orphans(patterns: dict, insights: Path, minimum: int, whole_if_missing: bool = True):
    text = insights_section(insights.read_text(encoding="utf-8"), whole_if_missing)
    out = []
    for pid, people in sorted(patterns.items()):
        if len(people) < minimum:
            continue
        mentions = [line for line in text.splitlines() if re.search(rf"\b{re.escape(pid)}\b", line, re.I)]
        explained = any(re.search(r"(no|sin|without)\s+insight", line, re.I) for line in mentions)
        if not mentions or (not explained and False):
            out.append((pid, len(people)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check counts and universals against the support table.")
    ap.add_argument("files", nargs="*", help="files to check (Markdown, text or HTML)")
    ap.add_argument("--root", default=".", help="discovery folder (default: current directory)")
    ap.add_argument("--patterns", help="support table (default: <root>/5-debrief/findings.md)")
    ap.add_argument("--pattern-prefix", default="PAT", help="prefix of the pattern IDs (default PAT)")
    ap.add_argument("--raw", action="append",
                    help="transcripts folder, repeatable (default: 4-field/_raw and 7-validation/_raw)")
    ap.add_argument("--person-label", default="System audio",
                    help="speaker label of the person interviewed (prefix match)")
    ap.add_argument("--interviewer-label", default="Microphone",
                    help="speaker label of the interviewer (prefix match)")
    ap.add_argument("--orphans", action="store_true",
                    help="list strong patterns with no insight and no explanation")
    ap.add_argument("--insights", help="file with the insights (default: the insights section of the support table, <root>/5-debrief/findings.md)")
    ap.add_argument("--min-people", type=int, default=3, help="a strong pattern (default 3)")
    ap.add_argument("--strict", action="store_true", help="UNIVERSAL and UNLINKED fail the run too")
    ap.add_argument("--only-problems", action="store_true", help="hide the summary of what passed")
    a = ap.parse_args(argv)

    if not a.files and not a.orphans:
        ap.error("name at least one file to check, or use --orphans")
    root = Path(a.root)
    table = Path(a.patterns) if a.patterns else root / "5-debrief" / "findings.md"
    patterns = read_patterns(table, a.pattern_prefix) if table.is_file() else {}
    if a.orphans and not table.is_file():
        print(f"No support table at {table}", file=sys.stderr)
        return 2
    id_re = re.compile(rf"\b{re.escape(a.pattern_prefix)}-\d+\b", re.I)
    folders = [Path(r) for r in a.raw] if a.raw else [root / "4-field" / "_raw",
                                                      root / "7-validation" / "_raw"]
    transcripts = read_transcripts(folders, a.person_label, a.interviewer_label)

    counts: dict = {}
    code = 0
    if a.files and not patterns:
        print(f"Note: no pattern rows found in {table}: counts cannot be compared, "
              "only listed.\n")
    for name in a.files:
        path = Path(name)
        if not path.is_file():
            print(f"No such file: {path}", file=sys.stderr)
            return 2
        for f in check_file(path, patterns, id_re, transcripts):
            counts[f["verdict"]] = counts.get(f["verdict"], 0) + 1
            print(f"{f['verdict']:13} {f['where']:22} «{f['claim']}»")
            if f["detail"]:
                print(f"{'':36}{f['detail']}")
            if f["candidates"] is not None and f["verdict"] == "UNIVERSAL":
                real = [c for c in f["candidates"] if c[0] != "keys"]
                keys = next((c[1] for c in f["candidates"] if c[0] == "keys"), "")
                label = ("counterexample candidates" if NEG_RE.search(fold(f["claim"]))
                         else "no support found in")
                if keys:
                    print(f"{'':36}searched for: {keys}")
                if real:
                    for who, snippet in real[:MAX_CANDIDATES]:
                        print(f"{'':36}{label}: {who}" + (f" «{snippet}»" if snippet else ""))
                    if len(real) > MAX_CANDIDATES:
                        print(f"{'':36}... and {len(real) - MAX_CANDIDATES} more")
                elif keys:
                    print(f"{'':36}no transcript line matches: the claim survives this search")
    if a.orphans:
        insights = Path(a.insights) if a.insights else table
        if not insights.is_file():
            print(f"No insights file at {insights}", file=sys.stderr)
            return 2
        for pid, n in orphans(patterns, insights, a.min_people, whole_if_missing=bool(a.insights)):
            counts["ORPHAN"] = counts.get("ORPHAN", 0) + 1
            print(f"{'ORPHAN':13} {pid:22} held by {n} people, no insight and no line saying why not")

    print("\nSummary:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "nothing flagged",
          f"| patterns in table {len(patterns)} | transcripts read {len(transcripts)}")
    failing = FAILING | (SOFT if a.strict else set())
    return 1 if any(counts.get(v) for v in failing) else code


if __name__ == "__main__":
    sys.exit(main())
