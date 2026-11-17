#!/usr/bin/env python3
"""Cut a short clip for each quote, check it says the quote, and give it a thumbnail.

Optional and on request. A clip earns its cost when a piece is shown to someone (a slide, a
report, a review of a prototype on screen) and the words of the person are stronger than a
paraphrase. Nothing here is needed to process a debrief.

For each clip:
  1. Cut the source with ffmpeg, from `t_video - margin` to the end of the quote + margin.
     Re-encoded small (960 px wide, H.264, mono AAC), so the file travels.
  2. Burn the subtitles into the picture as images, not as a text track: a track is hidden by
     many viewers (a PDF viewer, a slide tool, a phone preview), a burned caption is not.
     The captions come from listening to the cut itself, locally.
  3. Listen to the finished mp4 again and compute the coverage: the share of the quote's
     content words found in what the clip says (same word rule as locate_quotes.py).
     `ok` is true only if the coverage reaches 0.8 and the file opens.
  4. Save a still frame as a thumbnail, for pieces that cannot play a video (a PDF).

`ok: true` means the clip contains the words of the quote. It does not mean the clip says what
the slide or finding says: that is the context check (+-6 lines, "Every model checker" in
steps/5a-debrief.md). Only a clip with `ok: true` goes into a piece. Before any clip is shown,
open it at three frames (start, middle, end) and blur what is sensitive (steps/7b and 8a); the
tool does not blur anything.

Input: a JSON list, or the output of locate_quotes.py (its "results" are read, and anything not
"located" is skipped unless --include-weak). Each clip:
  {"id", "quote", "session" or "media", "t_video_s" or "t_video" (where the quote starts, in the
   video's clock), "end_s" or "t_end" (optional), "illustrates" (optional: the title of the slide
   or finding the clip is for; carried to the output for the context check)}

Usage:
  python3 scripts/cut_clips.py clips.json --out-dir ../clips --media-dir ../recordings
  python3 scripts/cut_clips.py located.json --out-dir ../clips --media INT-001=a.mp4 --dry-run

Writes <out-dir>/<id>.mp4, <id>.jpg and clips-cut.json. Exit codes: 0 every clip ok; 1 some
clip is not ok; 2 no ffmpeg, no local speech-to-text, no Pillow (needed for the burned
captions; --no-subtitles skips them) or a bad input. Recordings and clips are personal data:
keep them outside the project until each clip is checked.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import locate_quotes as lq  # noqa: E402  (same word rule, same clock, same speech-to-text)

COVERAGE_OK = lq.LOCATED
WORDS_PER_SECOND = 2.6          # to guess where a quote ends when the end is not given
FONT_CANDIDATES = (
    "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf",
)

NO_FFMPEG = ("ffmpeg and ffprobe were not found on the PATH. Install them, for example:\n"
             "  macOS: brew install ffmpeg      Debian/Ubuntu: sudo apt install ffmpeg")
NO_PILLOW = ("Pillow is needed to burn the captions as images (pip install pillow). "
             "To cut without captions, pass --no-subtitles.")


# ------------------------------------------------------------------ pure logic

def safe_name(clip_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", clip_id).strip("-") or "clip"


def plan_window(start_s, end_s, quote, margin_before=3.0, margin_after=2.0,
                min_len=6.0, max_len=60.0, media_duration=None):
    """(start, end) of the clip in the video's clock.

    The quote's own span plus the margins. When the end is unknown it is guessed from the
    number of words. Never shorter than min_len, never longer than max_len (a cut longer
    than that is trimmed at the end, and the coverage check then says if the quote lost
    words), never outside the recording."""
    if end_s is None or end_s <= start_s:
        end_s = start_s + max(len(lq.norm_tokens(quote)) / WORDS_PER_SECOND, 2.0)
    start = max(0.0, start_s - margin_before)
    end = end_s + margin_after
    if end - start < min_len:
        end = start + min_len
    if end - start > max_len:
        end = start + max_len
    if media_duration is not None:
        end = min(end, media_duration)
        start = min(start, max(0.0, end - min_len))
    return round(start, 3), round(end, 3)


def group_captions(words, max_words=8, max_seconds=3.2, max_gap=0.7) -> list:
    """Short caption cards [{"start", "end", "text"}] from timed words. A card closes when it
    has enough words, runs long, or the speaker pauses."""
    cards, cur = [], []

    def close():
        if cur:
            text = " ".join(w["word"].strip() for w in cur).strip()
            if text:
                cards.append({"start": float(cur[0]["start"]), "end": float(cur[-1]["end"]),
                              "text": text})
            cur.clear()

    for w in words:
        if cur and (len(cur) >= max_words
                    or float(w["end"]) - float(cur[0]["start"]) > max_seconds
                    or float(w["start"]) - float(cur[-1]["end"]) > max_gap):
            close()
        cur.append(w)
    close()
    return cards


def build_cut_command(ffmpeg, src, start, duration, dst, overlays=(), width=960, fps=10, crf=32):
    """The ffmpeg call that cuts one clip. `overlays` are caption images:
    [{"png", "t0", "t1"}], times relative to the clip. Captions are pictures laid over the
    video; the output has no subtitle stream."""
    graph = f"[0:v]fps={fps},scale={width}:-2[v0]"
    last = "v0"
    for k, ov in enumerate(overlays, 1):
        graph += (f";[{last}][{k}:v]overlay=(main_w-overlay_w)/2:main_h-overlay_h-24:"
                  f"enable='between(t,{ov['t0']:.2f},{ov['t1']:.2f})'[v{k}]")
        last = f"v{k}"
    cmd = [ffmpeg, "-nostdin", "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}",
           "-i", str(src)]
    for ov in overlays:
        cmd += ["-i", str(ov["png"])]
    cmd += ["-filter_complex", graph, "-map", f"[{last}]", "-map", "0:a:0?", "-sn",
            "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ac", "1", "-b:a", "48k", "-movflags", "+faststart", str(dst)]
    return cmd


def build_thumb_command(ffmpeg, src, at, dst, width=960):
    """One still frame of the source at second `at`."""
    return [ffmpeg, "-nostdin", "-v", "error", "-y", "-ss", f"{at:.3f}", "-i", str(src),
            "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", str(dst)]


def judge(coverage: float, duration: float, max_len: float = 60.0) -> dict:
    """The verdict of one clip. ok needs the quote's words in the clip and a file that opens."""
    opens = duration > 0
    reasons = []
    if not opens:
        reasons.append("the file does not open or has no duration")
    if coverage < COVERAGE_OK:
        reasons.append(f"coverage {coverage:.2f} is below {COVERAGE_OK}")
    if opens and duration > max_len + 1:
        reasons.append(f"longer than {max_len:.0f} s")
    return {"ok": not reasons, "reasons": reasons}


def read_clips(path: Path, include_weak=False) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["results"] if isinstance(data, dict) and "results" in data else data
    clips, skipped = [], []
    for n, r in enumerate(rows, 1):
        if not r.get("quote"):
            raise ValueError(f"item {n} has no 'quote'")
        status = r.get("status")
        if status is not None and status != "located" and not (include_weak and status == "weak"):
            skipped.append(r.get("id", n))
            continue
        start = lq.parse_time(r.get("t_video_s", r.get("t_video")))
        if start is None:
            raise ValueError(f"item {r.get('id', n)} has no 't_video' (run locate_quotes.py first)")
        clips.append({"id": r.get("id") or f"C{n:03d}", "quote": r["quote"],
                      "session": r.get("session"), "media": r.get("media"),
                      "start_s": start, "end_s": lq.parse_time(r.get("end_s", r.get("t_end"))),
                      "illustrates": r.get("illustrates")})
    return clips, skipped


# ------------------------------------------------------------------ doing it

def find_font(explicit=None):
    for path in ([explicit] if explicit else []) + list(FONT_CANDIDATES):
        if path and Path(path).is_file():
            return path
    return None


def render_caption_png(text, path, width=960, font_path=None, size=26) -> None:
    """A caption card as a transparent image: white text on a dark rounded band."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default(size)
    except (OSError, TypeError):
        font = ImageFont.load_default()
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and font.getlength(trial) > width - 80:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    lines = lines[-2:]
    line_h = size + 8
    h = 18 + line_h * len(lines)
    w = int(max(font.getlength(ln) for ln in lines)) + 40
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=6, fill=(0, 0, 0, 170))
    for i, ln in enumerate(lines):
        draw.text((w / 2 - font.getlength(ln) / 2, 9 + line_h * i), ln, font=font,
                  fill=(255, 255, 255, 255))
    image.save(path)


def probe_duration(ffprobe, path) -> float:
    out = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def make_clip(clip, src, out_dir, cfg, run, transcribe, probe, render_png, workdir):
    """Cut, caption, listen again and judge one clip. The side effects come in as functions
    (run a command, transcribe a file, probe a duration, draw a card) so the logic can be tried
    without ffmpeg or a speech model."""
    name = safe_name(clip["id"])
    dst, thumb = Path(out_dir) / f"{name}.mp4", Path(out_dir) / f"{name}.jpg"
    media_len = probe(src)
    start, end = plan_window(clip["start_s"], clip["end_s"], clip["quote"], cfg["before"],
                             cfg["after"], cfg["min_len"], cfg["max_len"], media_len or None)
    duration = end - start
    overlays = []
    if cfg["subtitles"]:
        raw = Path(workdir) / f"{name}-raw.mp4"
        run(build_cut_command(cfg["ffmpeg"], src, start, duration, raw, (), cfg["width"]))
        for k, card in enumerate(group_captions(transcribe(raw))):
            png = Path(workdir) / f"{name}-c{k:03d}.png"
            render_png(card["text"], png)
            overlays.append({"png": png, "t0": card["start"], "t1": card["end"]})
    run(build_cut_command(cfg["ffmpeg"], src, start, duration, dst, overlays, cfg["width"]))
    heard = transcribe(dst)
    heard_text = " ".join(w["word"].strip() for w in heard)
    coverage = lq.coverage_in_tokens(clip["quote"], lq.norm_tokens(heard_text))
    length = probe(dst)
    verdict = judge(coverage, length, cfg["max_len"])
    run(build_thumb_command(cfg["ffmpeg"], src, min(clip["start_s"] + 0.5, max(end - 0.1, start)),
                            thumb, cfg["width"]))
    return {"id": clip["id"], "session": clip["session"], "quote": clip["quote"],
            "illustrates": clip["illustrates"], "file": dst.name, "thumbnail": thumb.name,
            "source_start_s": round(start, 2), "source_end_s": round(end, 2),
            "source_start": lq.mmss(start), "duration_s": round(length, 1),
            "coverage": round(coverage, 2), "ok": verdict["ok"], "reasons": verdict["reasons"],
            "heard": heard_text[:400]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cut a clip per quote, check it, caption it, thumbnail it.")
    ap.add_argument("clips", help="JSON: a clip list, or the output of locate_quotes.py")
    ap.add_argument("--out-dir", required=True, help="where clips, thumbnails and clips-cut.json go")
    ap.add_argument("--media", action="append", metavar="SESSION=PATH")
    ap.add_argument("--media-dir", help="folder with recordings named after the session ID")
    ap.add_argument("--before", type=float, default=3.0, help="seconds before the quote (default 3)")
    ap.add_argument("--after", type=float, default=2.0, help="seconds after the quote (default 2)")
    ap.add_argument("--min-len", type=float, default=6.0)
    ap.add_argument("--max-len", type=float, default=60.0)
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--no-subtitles", action="store_true", help="cut without burned captions")
    ap.add_argument("--font", help="TrueType font for the captions (default: a system font)")
    ap.add_argument("--include-weak", action="store_true", help="also cut quotes located 'weak'")
    ap.add_argument("--model", default="small")
    ap.add_argument("--lang")
    ap.add_argument("--dry-run", action="store_true", help="print the ffmpeg commands, cut nothing")
    a = ap.parse_args(argv)

    try:
        clips, skipped = read_clips(Path(a.clips), a.include_weak)
        media = lq.parse_pairs(a.media, "--media")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as err:
        print(f"cut_clips: {err}", file=sys.stderr)
        return 2
    if not clips:
        print("cut_clips: no clips to cut (nothing located).", file=sys.stderr)
        return 2
    for s in skipped:
        print(f"skipped {s}: not located", file=sys.stderr)

    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not a.dry_run and not (ffmpeg and ffprobe):
        print(NO_FFMPEG, file=sys.stderr)
        return 2
    ffmpeg, ffprobe = ffmpeg or "ffmpeg", ffprobe or "ffprobe"
    backend = None
    if not a.dry_run:
        backend = lq.detect_backend()
        if backend is None:
            print(lq.NO_BACKEND, file=sys.stderr)
            return 2
        if not a.no_subtitles and importlib.util.find_spec("PIL") is None:
            print(NO_PILLOW, file=sys.stderr)
            return 2

    sources = {}
    for c in clips:
        src = Path(c["media"]) if c.get("media") else lq.resolve_media(c["session"] or "", media, a.media_dir)
        if src is None or not src.is_file():
            print(f"cut_clips: no recording for {c['id']} (session {c['session']}); use --media or --media-dir.",
                  file=sys.stderr)
            return 2
        sources[c["id"]] = src

    out_dir = Path(a.out_dir)
    cfg = {"ffmpeg": ffmpeg, "before": a.before, "after": a.after, "min_len": a.min_len,
           "max_len": a.max_len, "width": a.width, "subtitles": not a.no_subtitles}

    if a.dry_run:
        for c in clips:
            start, end = plan_window(c["start_s"], c["end_s"], c["quote"], a.before, a.after,
                                     a.min_len, a.max_len)
            print(f"# {c['id']}: {lq.mmss(start)} to {lq.mmss(end)} of {sources[c['id']].name}")
            print(" ".join(build_cut_command(ffmpeg, sources[c["id"]], start, end - start,
                                             out_dir / f"{safe_name(c['id'])}.mp4", (), a.width)))
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    font = find_font(a.font)
    transcriber = lq.Transcriber(backend, a.model, a.lang)

    def run(cmd):
        subprocess.run(cmd, check=True)

    rows = []
    with tempfile.TemporaryDirectory() as work:
        for c in clips:
            row = make_clip(c, sources[c["id"]], out_dir, cfg, run, transcriber.words,
                            lambda p: probe_duration(ffprobe, p),
                            lambda text, path: render_caption_png(text, path, a.width, font), work)
            rows.append(row)
            print(("ok     " if row["ok"] else "REVIEW "), row["file"], "coverage", row["coverage"],
                  "|", "; ".join(row["reasons"]), flush=True)
    (out_dir / "clips-cut.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n",
                                            encoding="utf-8")
    good = sum(r["ok"] for r in rows)
    print(f"{good} of {len(rows)} ok. Open each at three frames and blur before it goes anywhere.",
          file=sys.stderr)
    return 0 if good == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
