#!/usr/bin/env python3
"""Run every check on everything that already left the team, in one command.

A fix made in the findings does not reach the page you sent last week. This script
reads the folder of shareable pieces (`share/` by default, plus `8-report/`) and
runs the same brakes on every file in it, at every gate, so a corrected finding
cannot stay alive in something that already went out.

One run does five things:

  1. Quotes. `verify_quotes.py` on each piece: a quote that the ledger marks as
     vetoed (VETOED, fails), a quote whose cut may flip the meaning (CUT?), a quote
     that is not in the person's own words (FAIL, fails). HTML goes through --file,
     anything else through --scan.
  2. Counts. `check_counts.py` on every piece: each "X of N" against the support
     table, every universal with its counterexample candidates, no success tick on
     two people or fewer.
  3. Internal marks. Whatever a canonical file marks as not for the report (see
     below) must not show up in a shared piece. The mark itself must not show up
     either. Verdict INTERNAL, fails.
  4. Internal codes. A shared piece is read by a person, so it holds no evidence IDs
     (INT-003-12, PAT-01, VAL-002), no hypothesis codes (A-023), no short codes
     (H04) and no working labels in capitals (TODO, WIP, GATE 2). Verdict CODE, fails.
     Speaker notes in a slide file (an aside with class "notes", data-notes) are
     listed as NOTES and fail too: the final piece leaves without them unless you
     pass --keep-notes.
  5. The log. The table "What already went out" of `5-debrief/verification-log.md`
     lists each file, to whom, when, what it claims and its state: `current`,
     `outdated` or `corrected and resent`. A piece in the folder that the table does
     not list is NOT_LOGGED; a listed piece marked `outdated` is OUTDATED. Both are
     for a person and fail only with --strict.

How a canonical file marks what is internal (verdict INTERNAL): add the tag
`[not for the report]` to a line or to a table row (in any cell), or wrap lines
between `<!-- not for the report -->` and `<!-- end not for the report -->`. The
text of each marked line, each marked table cell and each sentence of it (4 words
or more, compared without accents, case or punctuation) is searched in every
shared piece. Marks are read in every Markdown file of the discovery folder except
`_raw/` and the shared pieces themselves.

Codes: the patterns are fixed in this file (CODE_PATTERNS). The exceptions are
yours: --allow TOKEN (repeatable), `--allow "re:^ISO-\\d+$"` for a pattern, and one
entry per line in `_engine/share-allow.txt` (blank lines and # comments are
ignored). Use them for names that look like a code and are not, such as a product
called "H20".

A source file that holds codes on purpose (the Markdown the HTML is built from) is
named with --source: it gets the quote and count checks and skips the code,
internal and notes checks.

Exit code 1 if any check fails, 2 when an input is missing. Reuses
`verify_quotes.py` and `check_counts.py` by import; nothing is copied.

Usage:
  python3 scripts/check_share.py
  python3 scripts/check_share.py --share share --share 8-report
  python3 scripts/check_share.py --source 8-report/source.md --allow H20
  python3 scripts/check_share.py --strict
"""

from __future__ import annotations

import argparse
import contextlib
import html
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_counts  # noqa: E402
import verify_quotes  # noqa: E402

SHARED_DEFAULTS = ("share", "8-report")
EXTENSIONS = {".html", ".htm", ".md", ".txt"}
LOG_DEFAULT = Path("5-debrief") / "verification-log.md"
ALLOW_DEFAULT = Path("_engine") / "share-allow.txt"
LOG_HEADING = re.compile(r"what already went out", re.I)

FAILING = {"INTERNAL", "CODE", "NOTES", "FAIL", "VETOED", "MISMATCH", "BAD_FRACTION",
           "UNKNOWN_ID", "SMALL_N", "ORPHAN"}
SOFT = {"NOT_LOGGED", "OUTDATED"}

# What a person should never read. Case matters: "Gate 2" is a sentence, "GATE 2" is a label.
CODE_PATTERNS = [
    # Evidence, pattern, validation and observation IDs: INT-003-12, PAT-01, VAL-002b.
    r"\b(?:INT|VAL|OBS|PAT|INS|PRI|HMW|ASM|HYP|DEC|EV)-\d+(?:-\d+)?[a-z]?\b",
    # Any short code with a hyphen and 2 to 4 digits: A-023, H-04.
    r"\b[A-Z]{1,3}-\d{2,4}\b",
    # A letter and 2 or 3 digits: H04, C12.
    r"\b[A-Z]\d{2,3}\b",
    # Working labels in capitals.
    r"\b(?:TODO|TBD|WIP|FIXME|XXX|DRAFT|INTERNAL|VETOED|PENDING)\b",
    r"\b(?:GATE|STAGE|STEP|PHASE)\s+\d+[a-z]?\b",
]
CODE_RE = re.compile("|".join(f"(?:{p})" for p in CODE_PATTERNS))

LINE_MARK = re.compile(r"\[\s*not for the report\s*\]", re.I)
BLOCK_START = re.compile(r"<!--\s*not for the report\s*-->", re.I)
BLOCK_END = re.compile(r"<!--\s*end not for the report\s*-->", re.I)
MIN_MARKED_WORDS = 4

NOTES_HTML = re.compile(
    r"<aside\b[^>]*\bclass\s*=\s*[\"'][^\"']*\bnotes\b|"
    r"\bclass\s*=\s*[\"'][^\"']*\bspeaker-notes\b|\bdata-notes\s*=|<notes\b", re.I)
NOTES_TEXT = re.compile(r"^\s*(?:speaker notes?|notes?)\s*:\s*$", re.I | re.M)


def blank(match: re.Match) -> str:
    """Same length, same line breaks: line numbers survive."""
    return re.sub(r"[^\n]", " ", match.group(0))


def readable(path: Path) -> str:
    """What a person sees: no tags, no scripts, no styles. Text of comments stays."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() not in (".html", ".htm"):
        return text
    text = re.sub(r"<(script|style)\b.*?</\1\s*>", blank, text, flags=re.S | re.I)
    text = re.sub(r"<!--|-->", lambda m: " " * len(m.group(0)), text)
    text = re.sub(r"<[^>]*>", blank, text)
    return html.unescape(text)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


# ---- the exceptions to the code brake ---------------------------------------

def read_allow(tokens: list, path: Path):
    entries = list(tokens)
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                entries.append(line)
    exact, patterns = set(), []
    for entry in entries:
        if entry.startswith("re:"):
            patterns.append(re.compile(entry[3:]))
        else:
            exact.add(entry)
    return exact, patterns


def is_allowed(token: str, allow) -> bool:
    exact, patterns = allow
    return token in exact or any(p.search(token) for p in patterns)


# ---- what the canonical files marked as internal -----------------------------

def units_of(line: str):
    """The pieces of one marked line worth searching: each table cell, each sentence."""
    line = LINE_MARK.sub(" ", line).strip()
    if line.startswith("|"):
        parts = [c.strip() for c in line.strip("|").split("|")]
    else:
        parts = [re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)]
    out = []
    for part in parts:
        if re.fullmatch(r"[:\- ]*", part):
            continue
        candidates = [part] + re.split(r"(?<=[.!?;])\s+", part)
        for c in candidates:
            n = verify_quotes.norm(c)
            if len(n.split()) >= MIN_MARKED_WORDS:
                out.append((n, c.strip()))
    return out


def marked_units(files):
    """[(normalised, original, source file:line)] from every marked line or block."""
    found = []
    for path in files:
        inside = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if BLOCK_END.search(line):
                inside = False
                continue
            if BLOCK_START.search(line):
                inside = True
                continue
            if inside or LINE_MARK.search(line):
                for n, original in units_of(line):
                    found.append((n, original, f"{path.name}:{number}"))
    return found


def canonical_files(root: Path, skip: set):
    out = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).parts
        if "_raw" in rel or ".git" in rel or p.resolve() in skip:
            continue
        out.append(p)
    return out


# ---- the log of what went out -------------------------------------------------

def read_log(path: Path):
    """{file name: state} from the 'What already went out' table, or None if absent."""
    if not path.is_file():
        return None
    rows, inside, header = {}, False, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            inside = bool(LOG_HEADING.search(line))
            header = []
            continue
        if not inside or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header:
            header = [c.lower() for c in cells]
            continue
        if re.fullmatch(r"[:\- |]*", line):
            continue
        state_at = next((n for n, h in enumerate(header)
                         if h.startswith(("state", "status"))), len(cells) - 1)
        name = cells[0].strip("`")
        if name and name.lower() not in ("pending", "file"):
            rows[name] = cells[state_at].lower() if state_at < len(cells) else ""
    return rows


# ---- run the other two scripts, by import ------------------------------------

def run(main, argv):
    """Call another script's main(); return (exit code, its output lines)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = main(argv)
    return code, [ln for ln in buffer.getvalue().splitlines() if ln.strip()]


def verdict_of(line: str):
    m = re.match(r"([A-Z][A-Z_~?]+)\b", line)
    return m.group(1) if m else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run the checks on everything that already went out.")
    ap.add_argument("--root", default=".", help="discovery folder (default: current directory)")
    ap.add_argument("--share", action="append", metavar="DIR_OR_FILE",
                    help="shareable pieces, repeatable (default: <root>/share and <root>/8-report)")
    ap.add_argument("--source", action="append", default=[], metavar="FILE",
                    help="source file that may hold codes: quotes and counts only, repeatable")
    ap.add_argument("--allow", action="append", default=[], metavar="TOKEN",
                    help='exception to the code brake; "re:PATTERN" for a pattern, repeatable')
    ap.add_argument("--allow-file", help="exceptions, one per line (default: <root>/_engine/share-allow.txt)")
    ap.add_argument("--keep-notes", action="store_true", help="speaker notes are allowed in this piece")
    ap.add_argument("--log", help="verification log (default: <root>/5-debrief/verification-log.md)")
    ap.add_argument("--raw", help="interview transcripts folder (default: <root>/4-field/_raw)")
    ap.add_argument("--val-raw", help="validation transcripts folder (default: <root>/7-validation/_raw)")
    ap.add_argument("--person-label", default="System audio")
    ap.add_argument("--interviewer-label", default="Microphone")
    ap.add_argument("--no-midsentence", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="CUT?, UNIVERSAL, UNLINKED, NOT_LOGGED and OUTDATED fail the run too")
    a = ap.parse_args(argv)

    root = Path(a.root)
    folders = [Path(s) for s in a.share] if a.share else [
        root / d for d in SHARED_DEFAULTS if (root / d).exists()]
    shared: list = []
    for f in folders:
        if not f.exists():
            print(f"No such file or folder: {f}", file=sys.stderr)
            return 2
        shared += sorted(p for p in ([f] if f.is_file() else f.rglob("*"))
                         if p.is_file() and p.suffix.lower() in EXTENSIONS)
    sources = [Path(s) for s in a.source]
    for s in sources:
        if not s.is_file():
            print(f"No such file: {s}", file=sys.stderr)
            return 2
    if not shared and not sources:
        print("Nothing has gone out yet: no shareable pieces to check.")
        return 0

    allow = read_allow(a.allow, Path(a.allow_file) if a.allow_file else root / ALLOW_DEFAULT)
    skip = {p.resolve() for p in shared + sources}
    units = marked_units(canonical_files(root, skip))
    counts: dict = {}
    failures: list = []

    def report(verdict, where, detail):
        counts[verdict] = counts.get(verdict, 0) + 1
        print(f"{verdict:13} {where:28} {detail}")

    everything = shared + [s for s in sources if s not in shared]

    # 1. quotes
    forward = ["--root", str(root), "--person-label", a.person_label,
               "--interviewer-label", a.interviewer_label, "--only-problems"]
    for flag, value in (("--raw", a.raw), ("--val-raw", a.val_raw)):
        if value:
            forward += [flag, value]
    if a.no_midsentence:
        forward.append("--no-midsentence")
    plain = [p for p in everything if p.suffix.lower() not in (".html", ".htm")]
    calls = [["--file", str(p), *forward] for p in everything if p not in plain]
    if plain:
        calls.append(["--scan", *[str(p) for p in plain], *forward])
    for call in calls:
        code, lines = run(verify_quotes.main, call)
        if code == 2:
            print("\n".join(lines))
            return 2
        for ln in lines:
            v = verdict_of(ln)
            if v and v not in ("SUMMARY",):
                counts[v] = counts.get(v, 0) + 1
            if not ln.startswith("Summary:"):
                print(ln)

    # 2. counts
    count_args = [*[str(p) for p in everything], "--root", str(root),
                  "--person-label", a.person_label, "--interviewer-label", a.interviewer_label]
    for value in (a.raw, a.val_raw):
        if value:
            count_args += ["--raw", value]
    if a.strict:
        count_args.append("--strict")
    code, lines = run(check_counts.main, count_args)
    if code == 2:
        print("\n".join(lines))
        return 2
    for ln in lines:
        v = verdict_of(ln)
        if ln.startswith("Summary:") or ln.startswith("Note:"):
            continue
        if v:
            counts[v] = counts.get(v, 0) + 1
        print(ln)

    # 3, 4. internal marks, codes, speaker notes: only in what a person reads
    for path in shared:
        raw_text = path.read_text(encoding="utf-8")
        text = readable(path)
        folded = verify_quotes.norm(text)
        if LINE_MARK.search(raw_text) or BLOCK_START.search(raw_text) or BLOCK_END.search(raw_text):
            report("INTERNAL", path.name, "carries the 'not for the report' mark itself")
        for n, original, source in units:
            if verify_quotes.contains_words(folded, n):
                report("INTERNAL", path.name,
                       f"holds text marked not for the report in {source}: «{original[:80]}»")
        for m in CODE_RE.finditer(text):
            if not is_allowed(m.group(0), allow):
                report("CODE", f"{path.name}:{line_of(text, m.start())}",
                       f"internal code «{m.group(0)}»")
        if not a.keep_notes:
            for m in list(NOTES_HTML.finditer(raw_text)) + list(NOTES_TEXT.finditer(raw_text)):
                report("NOTES", f"{path.name}:{line_of(raw_text, m.start())}",
                       "speaker notes in a piece that leaves")

    # 5. the log
    log = read_log(Path(a.log) if a.log else root / LOG_DEFAULT)
    if log is not None:
        names = {p.name: p for p in shared}
        listed = {Path(k).name: v for k, v in log.items()}
        for name in sorted(names):
            if name not in listed:
                report("NOT_LOGGED", name, "not in the table 'What already went out'")
            elif listed[name].startswith("outdated"):
                report("OUTDATED", name,
                       "marked outdated: decide whether to resend, then mark it corrected and resent")
    elif shared:
        print("Note: no 'What already went out' table found in the verification log.")

    soft = (SOFT | {"CUT?", "UNIVERSAL", "UNLINKED"}) if a.strict else set()
    bad = FAILING | soft
    print("\nSummary:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "nothing flagged",
          f"| pieces checked {len(everything)} | marked internal units {len(units)}")
    return 1 if any(counts.get(v) for v in bad) else 0


if __name__ == "__main__":
    sys.exit(main())
