#!/usr/bin/env python3
"""Build this project's jev packs for the interviewer feedback, from its guide.

The depth pack asks jev which topic of the guide each exchange is about. Those
topics are the project's, not the method's: they come from the numbered blocks
of the master guide (`### 2. The journey of one purchase`) and from each block's
intent line (`Goal:`, `Intent:`, `Intención:`, `Objetivo:`). Everything else in
the pack is fixed wording, measured on the first real round.

Two more options always go in: one for logistics (greeting, consent, thanks,
goodbye) and one for "none of the topics", because a choice with no way out
forces the model to pick a wrong topic. Blocks that look like the opening or the
closing are folded into logistics; pass --logistics to say which they are.
Blocks that look like an exercise (a card sort, a board) are marked
`exercise`: the interviewer explaining the exercise is not a premise.

Output, in the project's `_engine/feedback/`:
  depth-pack.json      the depth pack with the guide's topics
  branches-pack.json   the "goes to the point" pack, copied as is

Read the topic list it prints. If a topic is wrong, fix the guide or edit the
pack by hand: the next run of this script overwrites it only with --force.

Usage
  python3 feedback_packs.py --guide discovery/3-guide/guide.md \\
      --subject "how small clinics book their patients" --lang es \\
      --out discovery/_engine/feedback
  python3 feedback_packs.py --guide G.md --subject "..." --logistics 0,6 --out ...
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_interview import fold  # noqa: E402

PACKS = Path(__file__).resolve().parent / "packs"

BLOCK = re.compile(r"^#{2,3}\s*(\d+)[️⃣]*[\.\)]?\s*(.+)$")
# Matched on the folded line, so "Intención:" and "**Goal:**" both count.
INTENT = re.compile(r"^[*_\s]*(goal|intent|intention|objective|intencion|objetivo)[*_\s]*:")
MINUTES = re.compile(r"\s*\(\s*\d+\s*(?:min)?\s*\)\s*$")

# Folded words that mark a block as the opening or the closing.
LOGISTICS_WORDS = ("apertura", "cierre", "bienvenida", "despedida", "saludo", "consentimiento",
                   "start", "opening", "rapport", "consent", "closing", "close", "wrap", "goodbye")
EXERCISE_WORDS = ("card", "sorting", "tarjeta", "ejercicio", "exercise", "board", "tablero")

FIXED = {
    "es": {
        "logistics": ("logistica_apertura_o_cierre",
                      "Saludo, presentacion del estudio, permiso para grabar, problemas tecnicos, "
                      "agradecimiento o despedida."),
        "none": ("ninguno_de_los_temas",
                 "Habla de algo sustantivo que no es ninguno de los temas anteriores."),
    },
    "en": {
        "logistics": ("logistics_opening_or_closing",
                      "Greeting, presenting the study, permission to record, technical problems, "
                      "thanks or goodbye."),
        "none": ("none_of_the_topics",
                 "They talk about something substantive that is none of the topics above."),
    },
}


def slug(text: str, limit: int = 40) -> str:
    words = re.findall(r"[a-z0-9]+", fold(text))
    out = ""
    for w in words:
        if len(out) + len(w) + 1 > limit:
            break
        out = f"{out}_{w}" if out else w
    return out or "topic"


def read_blocks(guide: Path):
    """[(number, title, intent)] for every numbered block of the guide."""
    lines = guide.read_text(encoding="utf-8").splitlines()
    blocks = []
    for i, line in enumerate(lines):
        match = BLOCK.match(line.strip())
        if not match:
            continue
        number, title = match.group(1), MINUTES.sub("", match.group(2)).strip()
        intent = ""
        for nxt in lines[i + 1:]:
            if BLOCK.match(nxt.strip()) or re.match(r"^#{1,3}\s", nxt.strip()):
                break
            if INTENT.match(fold(nxt.strip())):
                intent = nxt.split(":", 1)[1].strip().strip("*_").strip()
                break
        blocks.append((number, title, intent))
    return blocks


def looks_like(title: str, words) -> bool:
    folded = set(re.findall(r"[a-z]+", fold(title)))
    return any(w in folded for w in words)


def build(blocks, subject: str, lang: str, logistics: set[str] | None):
    template = json.loads((PACKS / f"depth.{lang}.json").read_text(encoding="utf-8"))
    log_key, log_text = FIXED[lang]["logistics"]
    none_key, none_text = FIXED[lang]["none"]
    criteria, topics = {}, []
    for number, title, intent in blocks:
        is_logistics = (number in logistics) if logistics is not None else looks_like(title, LOGISTICS_WORDS)
        if is_logistics:
            continue
        key = f"t{number}_{slug(title)}"
        criteria[key] = f"{title}. {intent[:1].upper()}{intent[1:]}" if intent else f"{title}."
        topics.append({"key": key, "number": number, "title": title, "intent": intent,
                       "exercise": looks_like(title, EXERCISE_WORDS)})
    if not topics:
        raise SystemExit("The guide has no numbered topic blocks left after the opening and "
                         "the closing. Expected headings like '### 2. The journey'.")
    criteria[log_key] = log_text
    criteria[none_key] = none_text

    block = template["preguntas"]["bloque"]
    block["criteria"] = criteria
    block["instructions"] = block["instructions"].replace("{SUBJECT}", subject)
    template["topics"] = topics
    template["logistics_key"] = log_key
    template["none_key"] = none_key
    template["lang"] = lang
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the feedback packs from the guide.")
    parser.add_argument("--guide", required=True, help="The master guide (3-guide/guide.md).")
    parser.add_argument("--subject", required=True,
                        help="What the interviews are about, as a phrase that follows "
                             "'an interview about ...'.")
    parser.add_argument("--lang", default="en", choices=sorted(FIXED),
                        help="Language of the packs. 'es' is the wording measured on the "
                             "first real round.")
    parser.add_argument("--out", required=True, help="Folder for the packs (_engine/feedback).")
    parser.add_argument("--logistics", default=None, metavar="N,N",
                        help="Block numbers that are opening or closing. Default: guessed "
                             "from the titles.")
    parser.add_argument("--force", action="store_true", help="Overwrite packs already there.")
    args = parser.parse_args()

    guide = Path(args.guide)
    if not guide.exists():
        raise SystemExit(f"Guide not found: {guide}")
    logistics = ({n.strip() for n in args.logistics.split(",") if n.strip()}
                 if args.logistics is not None else None)
    pack = build(read_blocks(guide), args.subject.strip(), args.lang, logistics)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    depth, branches = out / "depth-pack.json", out / "branches-pack.json"
    for path in (depth, branches):
        if path.exists() and not args.force:
            raise SystemExit(f"{path} is already there, maybe edited by hand. "
                             "Pass --force to rebuild it from the guide.")
    depth.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(PACKS / f"branches.{args.lang}.json", branches)

    print(f"Wrote {depth} and {branches}. Topics, from the guide:")
    for t in pack["topics"]:
        flag = "  (exercise)" if t["exercise"] else ""
        print(f"  {t['key']}: {t['title']}{flag}")
        if not t["intent"]:
            print("      no intent line under this block: jev only sees the title")
    print("Check them before classifying. Opening and closing go to logistics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
