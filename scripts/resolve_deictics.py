#!/usr/bin/env python3
"""Find what a participant was pointing at when they said "this" or "here".

In a screen-sharing session the participant says "this is confusing" or "here I
would click" and the transcript alone cannot say which part of the product they
meant. That weakens per-component evidence. This tool pairs each such phrase
with five frames of the shared screen around it and a glossary of the product's
components, so a model (or a person) can name the component, or say it cannot
be known.

The mechanical steps are code and run locally: clock offset, crop, candidate
phrases, frames, batches, the final sheet. Only the reading of the frames is
judgement, and it comes back as a JSON file per batch (see
templates/deictic-prompt.md). Naming the wrong component is worse than
abstaining, so "unknown" is always a valid answer.

Steps, in order (every one prints JSON or a short count):

  offset      video clock vs recorder clock, from local Whisper on 4 windows
  crop        the box of the shared screen, without black bars or the call's faces
  candidates  the participant's phrases that contain a demonstrative
  frames      a 5-frame strip per phrase (-4, -2, 0, +2, +4 s)
  batches     split the phrases into cases files for the reading step
  report      join candidates and answers into one Markdown sheet per session

Usage:
  python3 scripts/resolve_deictics.py offset VIDEO TRANSCRIPT
  python3 scripts/resolve_deictics.py crop VIDEO
  python3 scripts/resolve_deictics.py candidates TRANSCRIPT --offset 52.8 \\
      --duration 2400 --out work/VAL-002/candidates.json [--from-s 480] [--lang es|en]
  python3 scripts/resolve_deictics.py frames VIDEO work/VAL-002/candidates.json \\
      --crop 960:540:0:90 --out-dir work/VAL-002 [--masks masks.json]
  python3 scripts/resolve_deictics.py batches work/VAL-002 --size 28
  python3 scripts/resolve_deictics.py report work/VAL-002 --session VAL-002 \\
      --person "Ana" --offset 52.8 --glossary glossary.md --out VAL-002-deictics.md

Transcript format: recorder lines such as
  [12:03] System audio (Ana): this part here is confusing
  [12:09] Microphone: what do you expect to happen?
"System audio" is the participant and "Microphone" the interviewer; change them
with --person-label and --interviewer-label.

Needs ffmpeg and ffprobe on the PATH. Pillow and numpy are needed by `crop` and
`frames`, openai-whisper by `offset`; they are imported only by those steps.
Videos are personal data: keep them outside the repo and delete them when done.
"""

from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import statistics
import subprocess
import sys
import textwrap
import unicodedata
from pathlib import Path

LINE = re.compile(
    r"\[(\d+):(\d+)(?::(\d+))?\]\s*(Microphone|System audio)(?:\s*\(([^)]*)\))?:\s*(.*)")

DEMONSTRATIVES = {
    "es": r"esto|este|esta|eso|ese|esa|estos|esos|esas|estas|acá|ahí|aquí|aca|ahi|aqui",
    "en": r"this|that|these|those|here|there",
}
# Phrases where the demonstrative is a connector, not a pointer.
NOT_POINTING = {
    "es": r"por eso|por esto",
    "en": r"that's why|that is why|like that|and so on",
}
OFFSET_WINDOWS = (0.12, 0.35, 0.6, 0.85)
DELTAS = (-4, -2, 0, 2, 4)
BURST_SECONDS = 6          # one candidate per burst of phrases
MIN_WORDS_FOR_OFFSET = 6

# Codes any glossary may use besides its own components.
NOT_APPLICABLE = "NOT-APPLICABLE"
UNKNOWN = "UNKNOWN"

STRINGS = {
    "en": {
        "title": "{session} · {person}: what they were pointing at",
        "owns": ("Owns: for each phrase of {person} that points at something without naming it "
                 "(\"this\", \"here\"), what was on screen. Does not own: what they said and did "
                 "→ the session note; the patterns → findings."),
        "method": "- **Method:** {method}",
        "clock": ("- **Clock:** the video starts {amount} {when} than the recorder "
                  "(offset = {offset:.1f} s). Video clock = recorder clock − {offset:.1f} s."),
        "later": "later", "earlier": "earlier",
        "counts": ("- **Phrases:** {total} candidates with a demonstrative; {pointing} point at "
                   "something; {no} do not (dropped){other}; {missing} without an answer."),
        "other": "; {n} said by someone else (dropped)",
        "confidence": ("- **Confidence:** declared by the model, a weak signal. Review the rows "
                       "marked \"review\" first. Naming the wrong component is worse than "
                       "answering {unknown}."),
        "captures": ("- **Captures:** a strip of 5 frames (−4, −2, 0, +2, +4 s). Faces of the "
                     "call are masked. Components tagged [sensitive] get no capture because "
                     "they show personal data."),
        "head": "| # | Recorder | Video | Phrase | Component | Element | Confidence | Capture |",
        "no_sensitive": "no capture (personal data)",
        "no_outside": "no capture (not the product)",
        "review": " · **review**",
        "to_review": "**To review ({n}):** rows {rows}.",
        "none": "none",
        "strip": "strip",
    },
    "es": {
        "title": "{session} · {person}: qué señalaba",
        "owns": ("Owns: para cada frase de {person} que señala algo sin nombrarlo («esto», «acá»), "
                 "qué se veía en pantalla. Does not own: lo que dijo y lo que hizo → la nota de la "
                 "sesión; los patrones → findings."),
        "method": "- **Método:** {method}",
        "clock": ("- **Reloj:** el video arranca {amount} {when} que el grabador "
                  "(desfase = {offset:.1f} s). Reloj de video = reloj del grabador − {offset:.1f} s."),
        "later": "más tarde", "earlier": "más temprano",
        "counts": ("- **Frases:** {total} candidatas con un demostrativo; {pointing} señalan algo; "
                   "{no} no señalan (descartadas){other}; {missing} sin respuesta."),
        "other": "; {n} dichas por otra persona (descartadas)",
        "confidence": ("- **Confianza:** la declara el modelo, es una señal débil. Revisá primero "
                       "las filas marcadas «revisar». Nombrar mal el componente es peor que "
                       "contestar {unknown}."),
        "captures": ("- **Capturas:** tira de 5 cuadros (−4, −2, 0, +2, +4 s). Las caras de la "
                     "llamada van tapadas. Los componentes marcados [sensitive] no llevan captura "
                     "porque muestran datos personales."),
        "head": "| # | Grabador | Video | Frase | Componente | Elemento | Confianza | Captura |",
        "no_sensitive": "sin captura (datos personales)",
        "no_outside": "sin captura (no es el producto)",
        "review": " · **revisar**",
        "to_review": "**Para revisar ({n}):** filas {rows}.",
        "none": "ninguna",
        "strip": "tira",
    },
}


# ---------------------------------------------------------------- transcript

def clock_seconds(a: str, b: str, c: str | None) -> int:
    return int(a) * 60 + int(b) if c is None else int(a) * 3600 + int(b) * 60 + int(c)


def read_lines(path: str | Path, person_label="System audio", interviewer_label="Microphone"):
    """[(seconds, role, text)] with role 'person' or 'interviewer'."""
    rows = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        source = m.group(4)
        if source == person_label:
            role = "person"
        elif source == interviewer_label:
            role = "interviewer"
        else:
            continue
        rows.append((clock_seconds(m.group(1), m.group(2), m.group(3)), role, m.group(6)))
    return rows


def merge_turns(rows, gap=8):
    """Merge consecutive lines of the same role that are at most `gap` seconds apart."""
    turns = []
    for t, role, text in rows:
        if turns and turns[-1]["role"] == role and t - turns[-1]["t_end"] <= gap:
            turns[-1]["text"] += " " + text
            turns[-1]["t_end"] = t
        else:
            turns.append({"t": t, "t_end": t, "role": role, "text": text})
    return turns


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z ]", "", text)


def mmss(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


# ----------------------------------------------------------------- candidates

def find_candidates(rows, offset, duration, from_s=480, lang="es"):
    """The participant's lines with a demonstrative, one per burst of 6 s."""
    demonstrative = re.compile(r"\b(" + DEMONSTRATIVES[lang] + r")\b", re.I)
    connector = re.compile(r"\b(" + NOT_POINTING[lang] + r")\b", re.I)
    turns = merge_turns(rows)
    found = []
    for t, role, text in rows:
        if role != "person" or t < from_s:
            continue
        video_t = t - offset
        if video_t < 0 or video_t > duration - 5:
            continue
        if not demonstrative.search(connector.sub("", text)):
            continue
        if found and t - found[-1]["recorder_t"] <= BURST_SECONDS:
            continue
        found.append({"recorder_t": t, "video_t": video_t, "line": text})
    for i, cand in enumerate(found, 1):
        cand["id"] = f"C{i:03d}"
        person_idx = [k for k, turn in enumerate(turns) if turn["role"] == "person"]
        nearest = min(person_idx, key=lambda k: abs(turns[k]["t"] - cand["recorder_t"]))
        cand["context"] = [
            f"[{mmss(x['t'])}] {'P' if x['role'] == 'person' else 'I'}: {x['text'][:300]}"
            for x in turns[max(0, nearest - 2):nearest + 3]]
    return found


# --------------------------------------------------------------------- offset

def video_duration(video: str) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video]))


def estimate_offset(video, transcript, workdir, person_label, interviewer_label):
    """offset = recorder clock - video clock, median of matched windows."""
    import whisper  # local, nothing leaves the machine

    duration = video_duration(video)
    person = [(t, text) for t, role, text in read_lines(transcript, person_label, interviewer_label)
              if role == "person" and len(text.split()) >= MIN_WORDS_FOR_OFFSET]
    model = whisper.load_model("small")
    samples = []
    for fraction in OFFSET_WINDOWS:
        start = int(duration * fraction)
        wav = os.path.join(workdir, f"_window_{start}.wav")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-t", "90",
                        "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav, "-y"], check=True)
        result = model.transcribe(wav, fp16=False)
        os.remove(wav)
        for seg in result["segments"]:
            words = fold(seg["text"]).split()
            if len(words) < 7:
                continue
            heard = " ".join(words)
            best = None
            for t, text in person:
                ratio = difflib.SequenceMatcher(
                    None, heard, fold(text)[:len(heard) + 30]).ratio()
                if best is None or ratio > best[0]:
                    best = (ratio, t)
            if best and best[0] >= 0.75:
                samples.append(round(best[1] - (start + seg["start"]), 1))
    if not samples:
        return {"error": "no matches: check the person label or the audio"}
    median = statistics.median(samples)
    kept = [s for s in samples if abs(s - median) <= 4]
    return {"offset_s": round(statistics.median(kept), 1), "n": len(kept), "of": len(samples),
            "min": min(kept), "max": max(kept)}


# ----------------------------------------------------------------------- crop

def detect_crop(video, call_strip=0.25, threshold=4):
    """crop=W:H:X:Y of the shared screen. The call's faces live on the right edge."""
    import io

    import numpy as np
    from PIL import Image

    duration = video_duration(video)
    boxes = []
    for fraction in (0.2, 0.35, 0.5, 0.65, 0.8):
        raw = subprocess.check_output(
            ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(duration * fraction), "-i", video,
             "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"])
        gray = np.asarray(Image.open(io.BytesIO(raw)).convert("L")).astype(float)
        height, width = gray.shape
        left = gray[:, :int(width * (1 - call_strip))]
        rows = np.where(left.std(axis=1) > threshold)[0]
        cols = np.where(left.std(axis=0) > threshold)[0]
        if len(rows) < 50 or len(cols) < 50:
            continue
        boxes.append((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
    if not boxes:
        return None
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    return f"{(x1 - x0) // 2 * 2}:{(y1 - y0) // 2 * 2}:{x0}:{y0}"


# --------------------------------------------------------------------- frames

def active_masks(masks, video_t):
    return [m for m in masks
            if m["from_video_s"] <= video_t < m.get("to_video_s", float("inf"))]


def paint_masks(image, rects):
    """Rects are fractions [x0, y0, x1, y1] (0-1) of the cropped frame."""
    from PIL import ImageDraw

    width, height = image.size
    draw = ImageDraw.Draw(image)
    for x0, y0, x1, y1 in rects:
        draw.rectangle([x0 * width, y0 * height, x1 * width, y1 * height], fill=(0, 0, 0))
    return image


def build_strips(video, cands, crop, out_dir, masks):
    from concurrent.futures import ThreadPoolExecutor

    from PIL import Image, ImageDraw, ImageFont

    width, height, x, y = map(int, crop.split(":"))
    for sub in ("strips", "captures", "frames"):
        os.makedirs(os.path.join(out_dir, sub), exist_ok=True)

    def grab(job):
        cand, delta = job
        path = os.path.join(out_dir, "frames", f"{cand['id']}_{delta:+d}.jpg")
        if not os.path.exists(path):
            subprocess.run(
                ["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{max(cand['video_t'] + delta, 0):.2f}",
                 "-i", video, "-frames:v", "1", "-vf", f"crop={width}:{height}:{x}:{y},scale=960:-1",
                 "-q:v", "3", path, "-y"], check=True)
        return path

    with ThreadPoolExecutor(4) as pool:
        list(pool.map(grab, [(c, d) for c in cands for d in DELTAS]))

    tile_w = 640
    tile_h = int(tile_w * height / width)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 26)
    except OSError:
        font = ImageFont.load_default()

    def mosaic(cand, out, hide):
        sheet = Image.new("RGB", (3 * tile_w, 2 * tile_h), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        for i, delta in enumerate(DELTAS):
            frame = Image.open(os.path.join(out_dir, "frames", f"{cand['id']}_{delta:+d}.jpg")).convert("RGB")
            t = cand["video_t"] + delta
            if hide:
                frame = paint_masks(frame, [m["rect"] for m in active_masks(masks, t)])
            px, py = (i % 3) * tile_w, (i // 3) * tile_h
            sheet.paste(frame.resize((tile_w, tile_h)), (px, py))
            label = f"{delta:+d}s (video {mmss(t)})"
            draw.rectangle([px, py, px + len(label) * 15 + 10, py + 34], fill=(0, 0, 0))
            draw.text((px + 5, py + 3), label, fill=(255, 255, 0), font=font)
            draw.rectangle([px, py, px + tile_w - 1, py + tile_h - 1], outline=(200, 0, 0), width=2)
        sheet.save(out, quality=82)

    for cand in cands:
        mosaic(cand, os.path.join(out_dir, "strips", f"{cand['id']}.jpg"), hide=False)
        mosaic(cand, os.path.join(out_dir, "captures", f"{cand['id']}.jpg"), hide=True)
    return len(cands)


# -------------------------------------------------------------------- batches

def write_batches(work_dir, size):
    cands = json.loads(Path(work_dir, "candidates.json").read_text(encoding="utf-8"))
    count = 0
    for start in range(0, len(cands), size):
        count += 1
        cases = [{"id": c["id"], "key_phrase": c["line"][:300], "context": c["context"],
                  "image": os.path.join(work_dir, "strips", f"{c['id']}.jpg")}
                 for c in cands[start:start + size]]
        Path(work_dir, f"cases_{count}.json").write_text(
            json.dumps(cases, ensure_ascii=False, indent=1), encoding="utf-8")
    return count


# --------------------------------------------------------------------- report

def read_glossary(path):
    """{code: set(tags)} from lines like '- CODE [sensitive]: description'."""
    codes = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- ([A-Z][A-Za-z0-9-]*)((?:\s*\[[a-z-]+\])*)\s*:", line)
        if m:
            codes[m.group(1)] = set(re.findall(r"\[([a-z-]+)\]", m.group(2)))
    return codes


def read_ids(path):
    return set(Path(path).read_text().split()) if os.path.exists(path) else set()


def build_report(work_dir, session, person, offset, method, glossary, captures_rel, lang="en"):
    s = STRINGS[lang]
    cands = {c["id"]: c for c in json.loads(
        Path(work_dir, "candidates.json").read_text(encoding="utf-8"))}
    answers = {}
    for f in sorted(glob.glob(os.path.join(work_dir, "out_*.json"))):
        for r in json.loads(Path(f).read_text(encoding="utf-8")):
            answers[r["id"]] = r
    no_capture = read_ids(os.path.join(work_dir, "no_capture.txt"))
    other_speaker = read_ids(os.path.join(work_dir, "other_speaker.txt"))
    tags = read_glossary(glossary)

    rows, dropped, other, missing = [], 0, 0, []
    for cid, cand in sorted(cands.items(), key=lambda kv: kv[1]["recorder_t"]):
        answer = answers.get(cid)
        if not answer:
            missing.append(cid)
        elif cid in other_speaker:
            other += 1
        elif answer.get("points_at") == "no":
            dropped += 1
        else:
            rows.append((cand, answer))

    def clip(text, n=140):
        return text if len(text) <= n else textwrap.shorten(text, n, placeholder="…")

    def esc(text):
        return str(text).replace("|", "/").replace("\n", " ")

    amount = abs(offset)
    amount = f"{amount:.0f} s" if amount < 60 else f"{int(amount // 60)} min {int(amount % 60)} s"
    lines = [
        f"# {s['title'].format(session=session, person=person)}", "",
        s["owns"].format(person=person), "",
        s["method"].format(method=method),
        s["clock"].format(amount=amount, offset=offset,
                          when=s["later"] if offset > 0 else s["earlier"]),
        s["counts"].format(total=len(cands), pointing=len(rows), no=dropped,
                           other=s["other"].format(n=other) if other else "",
                           missing=len(missing)),
        s["confidence"].format(unknown=UNKNOWN),
        s["captures"], "", s["head"], "|---|---|---|---|---|---|---|---|"]
    review = []
    for i, (cand, ans) in enumerate(rows, 1):
        conf, comp = ans.get("confidence", "?"), ans.get("component", UNKNOWN)
        flag = (conf == "low" or ans.get("points_at") == "maybe" or comp == UNKNOWN)
        if flag:
            review.append(i)
        if "sensitive" in tags.get(comp, set()) or cand["id"] in no_capture:
            capture = s["no_sensitive"]
        elif "outside" in tags.get(comp, set()) or comp in (UNKNOWN, NOT_APPLICABLE):
            capture = s["no_outside"]
        else:
            capture = f"[{s['strip']}]({captures_rel}/{cand['id']}.jpg)"
        lines.append(
            f"| {i} | {mmss(cand['recorder_t'])} | {mmss(cand['video_t'])} | "
            f"«{esc(clip(cand['line']))}» | {comp} | {esc(ans.get('element', ''))[:90]} | "
            f"{conf}{s['review'] if flag else ''} | {capture} |")
    lines += ["", s["to_review"].format(
        n=len(review), rows=", ".join(map(str, review)) if review else s["none"])]
    return "\n".join(lines) + "\n", dict(
        rows=len(rows), dropped=dropped, other=other, missing=len(missing), review=len(review))


# ------------------------------------------------------------------------ cli

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="step", required=True)

    def labels(p):
        p.add_argument("--person-label", default="System audio")
        p.add_argument("--interviewer-label", default="Microphone")

    p = sub.add_parser("offset"); labels(p)
    p.add_argument("video"); p.add_argument("transcript")
    p.add_argument("--workdir", default=".")

    p = sub.add_parser("crop"); p.add_argument("video")

    p = sub.add_parser("candidates"); labels(p)
    p.add_argument("transcript")
    p.add_argument("--offset", type=float, required=True)
    p.add_argument("--duration", type=float, required=True, help="video length in seconds")
    p.add_argument("--out", required=True)
    p.add_argument("--from-s", type=float, default=480,
                   help="skip the warm-up: recorder seconds to start from (default 480)")
    p.add_argument("--lang", choices=sorted(DEMONSTRATIVES), default="es")

    p = sub.add_parser("frames")
    p.add_argument("video"); p.add_argument("candidates")
    p.add_argument("--crop", required=True, help="W:H:X:Y, from the crop step")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--masks", help="JSON: [{from_video_s, to_video_s, rect:[x0,y0,x1,y1] as 0-1 fractions}]")

    p = sub.add_parser("batches")
    p.add_argument("work_dir"); p.add_argument("--size", type=int, default=28)

    p = sub.add_parser("report")
    p.add_argument("work_dir"); p.add_argument("--session", required=True)
    p.add_argument("--person", required=True)
    p.add_argument("--offset", type=float, required=True)
    p.add_argument("--glossary", required=True)
    p.add_argument("--method", default="strip of 5 frames + 2 neighbouring lines + glossary")
    p.add_argument("--captures-rel", default="captures")
    p.add_argument("--lang", choices=sorted(STRINGS), default="en")
    p.add_argument("--out", required=True)

    args = parser.parse_args(argv)

    if args.step == "offset":
        result = estimate_offset(args.video, args.transcript, args.workdir,
                                 args.person_label, args.interviewer_label)
        print(json.dumps(result, ensure_ascii=False))
        return 1 if "error" in result else 0
    if args.step == "crop":
        crop = detect_crop(args.video)
        if not crop:
            print("no shared screen found", file=sys.stderr)
            return 1
        print(f"crop={crop}")
        return 0
    if args.step == "candidates":
        rows = read_lines(args.transcript, args.person_label, args.interviewer_label)
        found = find_candidates(rows, args.offset, args.duration, args.from_s, args.lang)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(found)} candidates")
        return 0
    if args.step == "frames":
        cands = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        masks = json.loads(Path(args.masks).read_text()) if args.masks else []
        print(f"{build_strips(args.video, cands, args.crop, args.out_dir, masks)} strips")
        return 0
    if args.step == "batches":
        print(f"{write_batches(args.work_dir, args.size)} batches")
        return 0
    text, stats = build_report(args.work_dir, args.session, args.person, args.offset,
                               args.method, args.glossary, args.captures_rel, args.lang)
    Path(args.out).write_text(text, encoding="utf-8")
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
