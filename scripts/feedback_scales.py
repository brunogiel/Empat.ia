#!/usr/bin/env python3
"""The numbers of the interviewer feedback, and the three scales drawn as SVG.

Reads every interview of the round in one folder (`_engine/feedback/`):
  <base>.jsonl           exchanges, from segment_interview.py          (required)
  <base>-depth.csv       jev with depth-pack.json, classify_exchanges.py (optional)
  <base>-branches.csv    jev with branches-pack.json                    (optional)
  depth-pack.json        the project's topics, from feedback_packs.py   (optional)

Writes, per interview, next to them:
  <base>-data.json       the numbers the Guide writes the feedback from
  <base>-scales.html     the three scales, with every interview of the round on the bar
  <base>-hand-count.md   the sheet for what is counted by hand (never overwritten)

The three scales, about how the PERSON tells, not about the interviewer:
  How much they tell     median words per exchange (a count)
  How much they monologue  share of all their words said in answers of 200+ words (a count)
  How much they get to the point  of every 10 answers to a real question, how many start
                          by answering it (jev, "arranca_contestando")

Without jev the first two still come out, over every exchange (the opening and
the closing cannot be told apart, and the data says so); the third and the
per-topic table do not, and the Guide reads them by hand.

"You asked for a case / a reason and it came out" is counted BY HAND, on the
hand-count sheet: the judge that looks at the interviewer's question counts
greetings, instructions and cut-off questions as requests, and on the first real
round it was far off (7 of 19 by the judge, 11 of 13 by hand, in one interview).
The judge only pre-fills candidates.

Usage
  python3 feedback_scales.py discovery/_engine/feedback --lang es \\
      --label INT-004-ana-lopez=Ana --label INT-005-ben-ito=Ben
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segment_interview import answer_of, question_of  # noqa: E402

# --- Bands. PROVISIONAL: set on five interviews of the first real round. ----
# Recalibrate with 8 or more. Each scale is (axis_min, axis_max, [(edge, label)])
# where an edge is the upper end of its band. Nothing else depends on them.
MONOLOGUE_WORDS = 200          # an answer this long or longer is a monologue
GOES_TO_POINT_CUT = 0.5        # arranca_contestando_p at or above this = starts answering
YES = 0.5                      # a noul at or above this is a yes
PREMISE_CANDIDATE = 0.65       # premise candidates: judged at or above this, then read
NOT_TO_POINT_EXAMPLE = 0.3     # examples of "did not start by answering": below this

TELL_AXIS = (0, 80, [30, 45])          # corto < 30 · medio 30-45 · largo > 45
MONOLOGUE_AXIS = (0, 100, [30, 45])    # tramos cortos < 30 % · se extiende · monologa > 45 %
POINT_AXIS = (6, 8, [7, 7.5])          # le cuesta < 7 · a veces da vueltas · va al grano > 7,5

TEXT = {
    "es": {
        "tell": ("Cuánto cuenta", "Palabras por cada pregunta tuya (la mediana).",
                 "Palabras por respuesta", ["corto", "medio", "largo"]),
        "mono": ("Cuánto monologa",
                 f"Qué parte de todo lo que dijo fue en respuestas de {MONOLOGUE_WORDS} palabras o más.",
                 "Parte de lo dicho en monólogos",
                 ["cuenta en tramos cortos", "se extiende", "monologa"]),
        "point": ("Cuánto va al grano",
                  "De cada 10 respuestas a una pregunta tuya, cuántas arrancan contestando lo que preguntaste.",
                  "Respuestas que arrancan contestando",
                  ["le cuesta ir al grano", "a veces da vueltas", "va al grano"]),
        "of10": "de 10",
        "no_jev": "Sin jev no se juzga respuesta por respuesta: esta escala se lee a mano.",
    },
    "en": {
        "tell": ("How much they tell", "Words per question of yours (the median).",
                 "Words per answer", ["short", "medium", "long"]),
        "mono": ("How much they monologue",
                 f"What part of everything they said came in answers of {MONOLOGUE_WORDS} words or more.",
                 "Share said in monologues",
                 ["tells in short stretches", "stretches out", "monologues"]),
        "point": ("How much they get to the point",
                  "Of every 10 answers to a question of yours, how many start by answering what you asked.",
                  "Answers that start by answering",
                  ["struggles to get to the point", "sometimes goes around", "gets to the point"]),
        "of10": "of 10",
        "no_jev": "Without jev there is no answer-by-answer judgement: read this scale by hand.",
    },
}

BAND_FILL = {"tell": ["#eaf0fb", "#c9d8f2", "#8fb0e6"],
             "mono": ["#eaf0fb", "#c9d8f2", "#f3c9a6"],
             "point": ["#f3c9a6", "#eaf0fb", "#cfe9dc"]}

X0, X1 = 40, 720


def yes(row, key, cut=YES):
    try:
        return float(row.get(f"{key}_p") or 0) >= cut
    except ValueError:
        return False


def read_csv(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def label_of(base: str, labels: dict) -> str:
    if base in labels:
        return labels[base]
    parts = base.split("-")
    return parts[2].capitalize() if len(parts) > 2 else base


def measure(base: str, folder: Path, pack: dict | None):
    items = [json.loads(l) for l in (folder / f"{base}.jsonl").open(encoding="utf-8") if l.strip()]
    ex = {i["id"]: i["state"] for i in items}
    order = [i["id"] for i in items]
    depth = read_csv(folder / f"{base}-depth.csv")
    branches = read_csv(folder / f"{base}-branches.csv")
    words = {i: len(answer_of(ex[i]).split()) for i in order}

    log_key = (pack or {}).get("logistics_key")
    if depth:
        rows = [depth[i] for i in order if i in depth]
        substantive = [r["id"] for r in rows if r.get("bloque") != log_key]
    else:
        rows, substantive = [], list(order)
    total = sum(words[i] for i in substantive) or 1

    d = {
        "base": base,
        "judged_with_jev": bool(depth),
        "exchanges": len(order),
        "substantive_exchanges": len(substantive),
        "logistics_excluded": bool(depth),
        "median_words": st.median(words[i] for i in substantive) if substantive else 0,
        "monologue_pct": round(100 * sum(words[i] for i in substantive
                                         if words[i] >= MONOLOGUE_WORDS) / total),
        "monologues": sum(1 for i in substantive if words[i] >= MONOLOGUE_WORDS),
        "goes_to_point": None,
        "topics": {},
        "tensions_not_followed": [],
        "not_to_the_point_examples": [],
        "premise_candidates": [],
        "asked_case_candidates": [],
        "asked_reason_candidates": [],
    }

    if branches:
        with_question = [i for i in substantive if i in branches
                         and (not depth or depth[i].get("responde") != "no_habia_pregunta")]
        if with_question:
            d["goes_to_point"] = round(10 * sum(yes(branches[i], "arranca_contestando",
                                                    GOES_TO_POINT_CUT)
                                                for i in with_question) / len(with_question), 1)
            d["not_to_the_point_examples"] = [
                {"id": i, "question": question_of(ex[i])[-120:], "answer": answer_of(ex[i])[:160]}
                for i in with_question
                if float(branches[i].get("arranca_contestando_p") or 0) < NOT_TO_POINT_EXAMPLE][:8]

    if depth:
        topics = (pack or {}).get("topics") or []
        exercise = {t["key"] for t in topics if t.get("exercise")}
        for t in topics:
            rs = [r for r in rows if r.get("bloque") == t["key"]]
            d["topics"][t["key"]] = {
                "title": t["title"], "intent": t.get("intent", ""),
                "exchanges": len(rs),
                "concrete_cases": sum(yes(r, "episodio") for r in rs),
                "reasons": sum(yes(r, "motivo") for r in rs),
                "tensions": sum(yes(r, "tension") for r in rs),
                "generalisations": sum(yes(r, "generalizacion") for r in rs),
                "ids_with_case": [r["id"] for r in rs if yes(r, "episodio")],
                "ids_with_reason": [r["id"] for r in rs if yes(r, "motivo")],
            }
        none_key = (pack or {}).get("none_key")
        if none_key:
            d["outside_the_guide"] = sum(1 for r in rows if r.get("bloque") == none_key)
        d["tensions_not_followed"] = [
            rows[k]["id"] for k in range(len(rows) - 1)
            if yes(rows[k], "tension") and not yes(rows[k], "motivo")
            and not yes(rows[k + 1], "pide_motivo")]
        d["premise_candidates"] = [
            {"id": r["id"], "question": question_of(ex[r["id"]])[:200]}
            for r in rows if r.get("bloque") not in (log_key, *exercise)
            and yes(r, "premisa", PREMISE_CANDIDATE)]
        d["asked_case_candidates"] = [r["id"] for r in rows
                                      if r["id"] in substantive and yes(r, "pide_episodio")]
        d["asked_reason_candidates"] = [r["id"] for r in rows
                                        if r["id"] in substantive and yes(r, "pide_motivo")]
    return d, ex, depth


def position(value, axis):
    lo, hi, _ = axis
    value = min(max(value, lo), hi)
    return X0 + (value - lo) * (X1 - X0) / (hi - lo)


def fmt(v):
    return f"{v:g}".replace(".", ",")


def scale(kind, axis, values, me, lang, unit=""):
    title, sub, aria, band_labels = TEXT[lang][kind]
    lo, hi, edges = axis
    show = (lambda v: f"{fmt(v)}{unit}")
    s = (f'    <div class="scale">\n      <h3>{title}</h3>\n      <p class="small">{sub}</p>\n'
         f'      <svg viewBox="0 0 760 112" width="100%" role="img" aria-label="{aria}">\n')
    cuts = [lo] + edges + [hi]
    for k in range(3):
        a, b = position(cuts[k], axis), position(cuts[k + 1], axis)
        s += (f'        <rect x="{a:.0f}" y="52" width="{b - a:.0f}" height="12" '
              f'fill="{BAND_FILL[kind][k]}"/><text x="{(a + b) / 2:.0f}" y="84" font-size="12" '
              f'fill="#5b6675" text-anchor="middle">{band_labels[k]}</text>\n')
    tick_suffix = f" {TEXT[lang]['of10']}" if kind == "point" else unit
    for v in cuts:
        s += (f'        <text x="{position(v, axis):.0f}" y="104" font-size="11" fill="#5b6675" '
              f'text-anchor="middle">{fmt(v)}{tick_suffix}</text>\n')
    others = sorted(((k, v) for k, v in values.items() if k != me), key=lambda kv: kv[1])
    for _, v in others:
        s += f'        <rect x="{position(v, axis) - 1:.0f}" y="46" width="3" height="24" fill="#5b6675"/>\n'
    mx = position(values[me], axis)
    s += f'        <rect x="{mx - 2:.0f}" y="40" width="5" height="30" fill="#1f5fd1"/>\n'
    lower = [(k, v) for k, v in others if position(v, axis) < mx]
    upper = [(k, v) for k, v in others if position(v, axis) >= mx]
    if lower:
        x = max(110, sum(position(v, axis) for _, v in lower) / len(lower))
        s += (f'        <text x="{x:.0f}" y="18" font-size="12" fill="#5b6675" text-anchor="middle">'
              f'{" · ".join(f"{k} {show(v)}" for k, v in lower)}</text>\n')
    if upper:
        x = min(640, sum(position(v, axis) for _, v in upper) / len(upper))
        s += (f'        <text x="{x:.0f}" y="18" font-size="12" fill="#5b6675" text-anchor="middle">'
              f'{" · ".join(f"{k} {show(v)}" for k, v in upper)}</text>\n')
    s += (f'        <text x="{mx:.0f}" y="36" font-size="13" font-weight="700" fill="#1f5fd1" '
          f'text-anchor="middle">{me} · {show(values[me])}</text>\n      </svg>\n    </div>\n')
    return s


def scales_html(all_data, base, lang):
    names = {b: d["label"] for b, d in all_data.items()}
    me = names[base]
    tell = {names[b]: d["median_words"] for b, d in all_data.items()}
    mono = {names[b]: d["monologue_pct"] for b, d in all_data.items()}
    point = {names[b]: d["goes_to_point"] for b, d in all_data.items()
             if d["goes_to_point"] is not None}
    html = scale("tell", TELL_AXIS, tell, me, lang)
    html += scale("mono", MONOLOGUE_AXIS, mono, me, lang, unit=" %")
    if me in point:
        html += scale("point", POINT_AXIS, point, me, lang)
    else:
        title = TEXT[lang]["point"][0]
        html += (f'    <div class="scale">\n      <h3>{title}</h3>\n'
                 f'      <p class="small">{TEXT[lang]["no_jev"]}</p>\n    </div>\n')
    return html


HAND_COUNT = {
    "es": ("# Conteo a mano · {base}\n\n"
           "Owns: lo que se cuenta a mano del feedback: si pediste un caso o un motivo, y si salió. "
           "Does not own: el feedback → `4-field/feedback/{base}-feedback.html`.\n\n"
           "Leé **tu** pregunta en cada fila y marcá `x` si pediste un caso concreto o un motivo. "
           "Saludos, consignas y preguntas cortadas no cuentan. «Salió» lo prellena jev mirando la "
           "respuesta (eso sí se sostuvo); corregilo si no. «jev» marca las candidatas que vio el "
           "juez sobre tu pregunta: es un punto de partida, infla el total.\n\n"
           "| id | Tu pregunta | Pediste caso | ¿Salió? | Pediste motivo | ¿Salió? | jev |\n"
           "|---|---|---|---|---|---|---|\n"),
    "en": ("# Hand count · {base}\n\n"
           "Owns: what the feedback counts by hand: whether you asked for a case or a reason, and "
           "whether it came out. Does not own: the feedback → `4-field/feedback/{base}-feedback.html`.\n\n"
           "Read **your** question in each row and mark `x` if you asked for a concrete case or a "
           "reason. Greetings, instructions and cut-off questions do not count. \"Came out\" is "
           "pre-filled by jev from the answer (that part held up); fix it if wrong. \"jev\" marks "
           "the candidates the judge saw in your question: a starting point, it inflates the total.\n\n"
           "| id | Your question | Asked for case | Came out? | Asked for reason | Came out? | jev |\n"
           "|---|---|---|---|---|---|---|\n"),
}


def hand_count_sheet(d, ex, depth, lang):
    yes_word = "sí" if lang == "es" else "yes"
    out = HAND_COUNT[lang].format(base=d["base"])
    ids = [i for i in ex if not depth or i in depth]
    log_key = d.get("_log_key")
    for i in ids:
        row = depth.get(i) if depth else None
        if row is not None and row.get("bloque") == log_key:
            continue
        q = re.sub(r"\s+", " ", question_of(ex[i])).replace("|", "/")
        q = q if len(q) <= 160 else "…" + q[-159:]
        case = yes_word if row is not None and yes(row, "episodio") else ""
        reason = yes_word if row is not None and yes(row, "motivo") else ""
        marks = []
        if i in d["asked_case_candidates"]:
            marks.append("caso" if lang == "es" else "case")
        if i in d["asked_reason_candidates"]:
            marks.append("motivo" if lang == "es" else "reason")
        out += f"| {i} | {q} |  | {case} |  | {reason} | {', '.join(marks)} |\n"
    total = ("\n**Total:** pediste un caso __ veces, salió __ · pediste un motivo __ veces, salió __.\n"
             if lang == "es" else
             "\n**Total:** you asked for a case __ times, it came out __ · you asked for a reason "
             "__ times, it came out __.\n")
    return out + total


def main() -> int:
    parser = argparse.ArgumentParser(description="Numbers and scales of the interviewer feedback.")
    parser.add_argument("folder", help="_engine/feedback, with one <base>.jsonl per interview")
    parser.add_argument("--lang", default="en", choices=sorted(TEXT))
    parser.add_argument("--label", action="append", default=[], metavar="BASE=Name",
                        help="how an interview is named on the scales (repeatable)")
    args = parser.parse_args()

    folder = Path(args.folder)
    bases = sorted(p.stem for p in folder.glob("*.jsonl")
                   if re.match(r"^(INT|VAL)-\d{3}-[a-z0-9-]+$", p.stem))
    if not bases:
        raise SystemExit(f"No <base>.jsonl in {folder}. Run segment_interview.py first.")
    labels = dict(pair.split("=", 1) for pair in args.label if "=" in pair)
    pack_path = folder / "depth-pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8")) if pack_path.exists() else None

    all_data, raw = {}, {}
    for base in bases:
        d, ex, depth = measure(base, folder, pack)
        d["label"] = label_of(base, labels)
        d["_log_key"] = (pack or {}).get("logistics_key")
        all_data[base], raw[base] = d, (ex, depth)

    for base, d in all_data.items():
        (folder / f"{base}-scales.html").write_text(scales_html(all_data, base, args.lang),
                                                    encoding="utf-8")
        sheet = folder / f"{base}-hand-count.md"
        if not sheet.exists():
            sheet.write_text(hand_count_sheet(d, *raw[base], args.lang), encoding="utf-8")
        out = {k: v for k, v in d.items() if not k.startswith("_")}
        out["bands_status"] = "provisional: five interviews; recalibrate with 8 or more"
        (folder / f"{base}-data.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                                                  encoding="utf-8")

    print(json.dumps({d["label"]: {"median_words": d["median_words"],
                                   "monologue_pct": d["monologue_pct"],
                                   "goes_to_point": d["goes_to_point"],
                                   "judged_with_jev": d["judged_with_jev"]}
                      for d in all_data.values()}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
