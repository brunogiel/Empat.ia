#!/usr/bin/env python3
"""Make the two copies of the master guide that people actually carry.

The master guide (`3-guide/guide.md`) is the one file. Two things are built from it
so they can never drift from it:

  --client [OUT]   An export "for the client": the sections table, the questions
                   and an annex that shows the exercise. Without the `Owns:`
                   line, without internal IDs, without the interviewer's notes
                   (the lines in italics) and without anything the guide keeps
                   after the exercise annex. Markdown by default, `--format html`
                   for a single printable page that loads nothing from outside.
                   Goes to `share/guide-for-client.<md|html>` unless you name a file.

  --prep NAME      The prep sheet of one session (`4-field/_prep/NAME-prep.md`,
                   NAME like INT-004-ana-lopez, or a path): the route table and
                   the questions copied word for word as checkboxes. The sheet is
                   made from `templates/interview-prep.md` if it does not exist.
                   If it exists, only the route and the questions are replaced, so
                   whatever you wrote in the other sections stays. A sheet that
                   already has marks (a checked box, a crossed-out line) is never
                   touched without --force.

What the script reads from the master, and nothing else:

  * the first table before the first section: `# | Section | Minutes | Priority |
    Covers`, in that column order, whatever language the headers are in;
  * the sections: a line `### 3. Title`;
  * questions: a bullet at the start of a line; a nested bullet is a follow-up;
  * notes for the interviewer: a line that is wholly in italics (`*like this*`),
    alone or inside a bullet. Never sent to the client;
  * the exercise annex: what sits between `<!-- annex ... -->` and
    `<!-- end annex -->` is what the client sees in the annex. A section with an
    annex is an exercise: its lines before the annex go in the body, the lines
    after it are for the interviewer only.

The client export fails (exit 1) if an internal code is left in it (INT-003, A-012,
PAT-01, T9, GATE 2...) after the codes that sit alone in parentheses are taken
out, so the fix goes in the master and not in the copy. `--allow WORD` lets a word
through (a product called H20). Standard library only.

Usage
  python3 export_guide.py --project-root . --client
  python3 export_guide.py --project-root . --client --format html
  python3 export_guide.py --project-root . --prep INT-004-ana-lopez
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import init_project  # noqa: E402
from check_share import CODE_RE  # noqa: E402

SECTION = re.compile(r"^###\s+(\d+[a-z]?)\.?\s+(.+?)\s*$")
BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
ANNEX_START = re.compile(r"<!--\s*annex\b[^>]*-->", re.I)
ANNEX_END = re.compile(r"<!--\s*end annex\s*-->", re.I)
# A short code that check_share does not know: T9, Q1.
EXTRA_CODE = re.compile(r"\b[A-Z]\d{1,3}\b")
PAREN = re.compile(r"\s*[\(\[]\s*[^()\[\]]*?[\)\]]")
START, END = "<!-- guide:start -->", "<!-- guide:end -->"
ROUTE_START, ROUTE_END = "<!-- route:start -->", "<!-- route:end -->"


@dataclass
class Item:
    kind: str          # question | note | text
    text: str
    depth: int = 0


@dataclass
class Section:
    num: str
    title: str
    items: list = field(default_factory=list)
    annex: list = field(default_factory=list)   # (label, value) pairs
    after_annex: list = field(default_factory=list)
    is_exercise: bool = False


@dataclass
class Guide:
    title: str
    rows: list         # [(num, section, minutes, priority, covers)]
    sections: list


def is_note(text: str) -> bool:
    """A line that is wholly in italics. Bold (**x**) is not a note."""
    t = text.strip()
    if len(t) < 3:
        return False
    return (t.startswith("*") and t.endswith("*") and not t.startswith("**")) or \
           (t.startswith("_") and t.endswith("_") and not t.startswith("__"))


def parse_table(lines: list[str]) -> list[tuple]:
    rows = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells + [""] * (5 - len(cells)))
    return [tuple(r[:5]) for r in rows[1:]]   # the first row is the header


def parse(text: str) -> Guide:
    lines = text.splitlines()
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "Interview guide")
    first = next((i for i, l in enumerate(lines) if SECTION.match(l)), None)
    if first is None:
        raise SystemExit("No sections found: the guide needs headings like '### 1. Start and consent'.")
    rows = parse_table(lines[:first])
    sections: list[Section] = []
    current: Section | None = None
    in_annex = False
    after = False
    for line in lines[first:]:
        m = SECTION.match(line)
        if m:
            current = Section(m.group(1), m.group(2).strip())
            sections.append(current)
            in_annex = after = False
            continue
        if line.startswith("## ") or line.startswith("# "):
            current = None
            continue
        if current is None:
            continue
        if ANNEX_START.search(line):
            in_annex, current.is_exercise = True, True
            continue
        if ANNEX_END.search(line):
            in_annex, after = False, True
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if in_annex:
            label, _, value = stripped.partition(":")
            current.annex.append((label.strip(), value.strip()) if value else ("", stripped))
            continue
        b = BULLET.match(line)
        if b:
            indent, body = len(b.group(1)), b.group(2).strip()
            kind = "note" if is_note(body) else "question"
            item = Item(kind, body, 1 if indent >= 2 else 0)
        elif is_note(stripped):
            item = Item("note", stripped)
        else:
            item = Item("text", stripped)
        (current.after_annex if after else current.items).append(item)
    return Guide(title, rows, sections)


def count_questions(guide: Guide) -> int:
    return sum(1 for s in guide.sections for i in s.items + s.after_annex if i.kind == "question")


# --------------------------------------------------------------------- client

def drop_codes_in_parens(text: str) -> str:
    """Take out '(T9)' and '[A-012, T3]': a group made only of codes."""
    def repl(m: re.Match) -> str:
        inner = m.group(0).strip()[1:-1]
        left = CODE_RE.sub("", EXTRA_CODE.sub("", inner))
        return "" if not re.sub(r"[\s,;·+/-]", "", left) else m.group(0)
    return PAREN.sub(repl, text)


def strip_inline_italics(text: str) -> str:
    return text


def client_items(section: Section) -> list[Item]:
    return [i for i in section.items if i.kind != "note"]


def render_client_md(guide: Guide) -> str:
    out = [f"# {guide.title}", ""]
    if guide.rows:
        total = 0
        out += ["| # | Section | Minutes |", "|---|---|---:|"]
        for num, name, minutes, _prio, _cov in guide.rows:
            out.append(f"| {num} | {name} | {minutes} |")
            m = re.match(r"\d+", minutes)
            total += int(m.group(0)) if m else 0
        out += [""] + ([f"Total: about {total} minutes.", ""] if total else [])
    annexes = []
    for s in guide.sections:
        out += [f"## {s.num}. {s.title}", ""]
        for item in client_items(s):
            if item.kind == "text":
                out += [item.text, ""]
        questions = [i for i in client_items(s) if i.kind == "question"]
        for q in questions:
            out.append(("  " * q.depth) + f"- {q.text}")
        if questions:
            out.append("")
        if s.is_exercise:
            letter = chr(ord("A") + len(annexes))
            annexes.append((letter, s))
            out += [f"This section is an exercise: see Annex {letter}.", ""]
    for letter, s in annexes:
        out += [f"## Annex {letter}. {s.title}", ""]
        for label, value in s.annex:
            head = f"**{label}:** " if label else ""
            if " · " in value:
                out += [head.strip(), ""] if head else []
                out += [f"- {v.strip()}" for v in value.split(" · ")]
                out.append("")
            else:
                out += [f"{head}{value}", ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).rstrip() + "\n"


CSS = """
:root{color-scheme:light dark;--fg:#1d2330;--bg:#fff;--muted:#5b6475;--line:#d9dde5}
@media (prefers-color-scheme:dark){:root{--fg:#e6e8ee;--bg:#14171f;--muted:#9aa3b5;--line:#2c3342}}
body{font:16px/1.55 system-ui,sans-serif;color:var(--fg);background:var(--bg);margin:0 auto;max-width:44rem;padding:1.5rem 1rem}
h1{font-size:1.6rem}h2{font-size:1.2rem;margin-top:2rem;border-bottom:1px solid var(--line);padding-bottom:.2rem}
table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid var(--line);padding:.35rem .5rem;text-align:left}
td:last-child,th:last-child{text-align:right}li{margin:.25rem 0}.muted{color:var(--muted)}
@media print{body{max-width:none;padding:0;font-size:11pt}h2{break-after:avoid}li,tr{break-inside:avoid}}
"""


def render_client_html(md: str) -> str:
    """The export is plain enough to turn into HTML line by line."""
    body, in_list, in_table = [], False, False

    def close():
        nonlocal in_list, in_table
        if in_list:
            body.append("</ul>")
            in_list = False
        if in_table:
            body.append("</tbody></table>")
            in_table = False

    def inline(t: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(t))

    for line in md.splitlines():
        if line.startswith("# "):
            close(); body.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            close(); body.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            if not in_table:
                close()
                body.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells)
                            + "</tr></thead><tbody>")
                in_table = True
            else:
                body.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
        elif re.match(r"^\s*- ", line):
            if not in_list:
                close(); body.append("<ul>"); in_list = True
            body.append(f"<li>{inline(line.strip()[2:])}</li>")
        elif line.strip():
            close(); body.append(f"<p>{inline(line.strip())}</p>")
    close()
    title = next((l[2:] for l in md.splitlines() if l.startswith("# ")), "Interview guide")
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>\n"
            + "\n".join(body) + "\n</body></html>\n")


def leftover_codes(text: str, allow: set[str]) -> list[tuple[int, str]]:
    found = []
    for n, line in enumerate(text.splitlines(), 1):
        for rx in (CODE_RE, EXTRA_CODE):
            for m in rx.finditer(line):
                if m.group(0) not in allow:
                    found.append((n, m.group(0)))
    if re.search(r"^\s*Owns:", text, re.M):
        found.append((0, "Owns:"))
    return found


# ----------------------------------------------------------------------- prep

def route_table(guide: Guide) -> str:
    out = ["| # | Block | Priority | Minutes |", "|---|---|---|---|"]
    rows = guide.rows or [(s.num, s.title, "Pending", "Pending", "") for s in guide.sections]
    for num, name, minutes, prio, _cov in rows:
        out.append(f"| {num} | {name} | {prio or 'Pending'} | {minutes or 'Pending'} |")
    return "\n".join(out)


def question_block(guide: Guide) -> str:
    out = []
    for s in guide.sections:
        out += [f"**{s.num}. {s.title}**", ""]
        for item in s.items:
            out += render_prep_item(item)
        if s.is_exercise:
            for label, value in s.annex:
                out.append(f"{label + ': ' if label else ''}{value}".rstrip())
            out.append("")
        for item in s.after_annex:
            out += render_prep_item(item)
        out.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).rstrip()


def render_prep_item(item: Item) -> list[str]:
    pad = "  " * item.depth
    if item.kind == "question":
        return [f"{pad}- [ ] {item.text}"]
    if item.kind == "note":
        return [f"{pad}  {item.text}"]
    return [item.text, ""]


def replace_between(text: str, start: str, end: str, block: str) -> str | None:
    i, j = text.find(start), text.find(end)
    if i == -1 or j == -1 or j < i:
        return None
    return text[:i + len(start)] + "\n" + block + "\n" + text[j:]


def section_span(text: str, heading: str) -> tuple[int, int] | None:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not m:
        return None
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    return m.end(), (m.end() + nxt.start() if nxt else len(text))


def join_body(lines: list[str], heading_follows: bool) -> str:
    """A section body back to text, with the blank line a following heading needs."""
    return "\n".join(lines).rstrip("\n") + ("\n\n" if heading_follows else "\n")


def build_prep(existing: str, guide: Guide) -> str:
    text = existing
    table = route_table(guide)
    new = replace_between(text, ROUTE_START, ROUTE_END, table)
    if new is None:
        span = section_span(text, "The route")
        if span is None:
            raise SystemExit("The prep sheet has no '## The route' section to fill.")
        body = text[span[0]:span[1]]
        lines = body.splitlines()
        rows = [i for i, l in enumerate(lines) if l.startswith("|")]
        if not rows:
            raise SystemExit("The prep sheet's route has no table to replace.")
        lines[rows[0]:rows[-1] + 1] = [ROUTE_START, table, ROUTE_END]
        new = text[:span[0]] + join_body(lines, span[1] < len(text)) + text[span[1]:]
    text = new
    block = question_block(guide)
    new = replace_between(text, START, END, block)
    if new is None:
        span = section_span(text, "The questions")
        if span is None:
            raise SystemExit("The prep sheet has no '## The questions' section to fill.")
        body = text[span[0]:span[1]]
        lines = body.splitlines()
        first = next((i for i, l in enumerate(lines) if l.lstrip().startswith("- [ ]")), None)
        if first is None:
            lines += ["", START, block, END, ""]
        else:
            lines[first:] = [START, block, END, ""]
        new = text[:span[0]] + join_body(lines, span[1] < len(text)) + text[span[1]:]
    return new


def has_marks(text: str) -> bool:
    i, j = text.find(START), text.find(END)
    chunk = text[i:j] if i != -1 and j > i else text
    return bool(re.search(r"- \[[xX]\]|~~.+?~~", chunk))


def prep_path(value: str, discovery: Path) -> Path:
    if "/" in value or value.endswith(".md"):
        return Path(value).expanduser()
    if not init_project.BASE_NAME.match(value):
        raise SystemExit(f"'--prep {value}' is neither a path nor a base name like INT-004-ana-lopez.")
    return discovery / "4-field" / "_prep" / f"{value}-prep.md"


def main() -> int:
    ap = argparse.ArgumentParser(description="Client export and prep sheet from the master guide.")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--folder", default=None, help="Name of the discovery folder.")
    ap.add_argument("--method-root", default=None)
    ap.add_argument("--guide", default=None, help="The master guide. Default: 3-guide/guide.md.")
    ap.add_argument("--client", nargs="?", const="", default=None, metavar="OUT",
                    help="Write the export for the client (default share/guide-for-client.md).")
    ap.add_argument("--format", choices=["md", "html"], default="md")
    ap.add_argument("--prep", metavar="NAME", default=None,
                    help="Write the prep sheet of one session (INT-004-ana-lopez, or a path).")
    ap.add_argument("--force", action="store_true", help="Rewrite a prep sheet that already has marks.")
    ap.add_argument("--allow", action="append", default=[], metavar="WORD",
                    help="A word that looks like a code and is not (repeatable).")
    args = ap.parse_args()
    if args.client is None and args.prep is None:
        ap.error("ask for something: --client, --prep NAME, or both.")

    root = Path(args.project_root).expanduser().resolve()
    discovery = root / init_project.resolve_folder(root, args.folder)
    method = Path(args.method_root).expanduser().resolve() if args.method_root \
        else Path(__file__).resolve().parents[1]
    guide_path = Path(args.guide).expanduser() if args.guide else discovery / "3-guide" / "guide.md"
    if not guide_path.exists():
        raise SystemExit(f"No guide at {guide_path}. Create it with "
                         f"`init_project.py --project-root {root} --add interview_guide`, "
                         "or point to it with --guide.")
    guide = parse(guide_path.read_text(encoding="utf-8"))
    questions = count_questions(guide)
    if questions == 0:
        raise SystemExit(f"{guide_path} has sections but no question (a bullet at the start of a line).")
    status = 0

    if args.client is not None:
        md = drop_codes_in_parens(render_client_md(guide))
        left = leftover_codes(md, set(args.allow))
        if left:
            print("Not written. The export for the client still has internal codes; fix them in the master guide:")
            for n, code in left[:20]:
                print(f"  line {n}: {code}")
            return 1
        ext = "html" if args.format == "html" else "md"
        out = Path(args.client).expanduser() if args.client else discovery / "share" / f"guide-for-client.{ext}"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_client_html(md) if args.format == "html" else md, encoding="utf-8")
        print(f"Client export: {out} ({len(guide.sections)} sections, {questions} questions, "
              f"{sum(1 for s in guide.sections if s.is_exercise)} exercise annex).")

    if args.prep is not None:
        path = prep_path(args.prep, discovery)
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if has_marks(text) and not args.force:
                print(f"Not written. {path} already has marks (a checked box or a crossed-out line). "
                      "Pass --force to rebuild it and lose them.")
                return 1
        else:
            template = method / "templates" / "interview-prep.md"
            if not template.exists():
                raise SystemExit(f"Template missing: {template}")
            text = template.read_text(encoding="utf-8")
            label = args.prep if "/" not in args.prep and not args.prep.endswith(".md") else path.stem
            text = text.replace("<name> · <date> · <time>", f"{label} · {dt.date.today().isoformat()}", 1)
        out_text = build_prep(text, guide)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out_text, encoding="utf-8")
        print(f"Prep sheet: {path} ({questions} questions copied word for word).")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
