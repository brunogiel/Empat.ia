#!/usr/bin/env python3
"""Find the minute of each quote in the video, not in the recorder's transcript.

The tool that records a call also writes a transcript, and its clock can drift from the
video's by seconds or by minutes. A clip cut at the transcript's minute shows the wrong
moment. This tool listens to the audio again, locally, and aligns the words it hears
against the text of each quote. The minute it returns is the video's.

Optional and on request. It helps most when a quote will be played to someone (a clip in a
slide or a report) and when the sessions were recorded by a tool whose clock you do not trust.
Nothing here is needed to process a debrief.

How it decides (all by words, never by one long string):
  - The quote and the heard words are lowercased, without accents or punctuation.
  - Coverage = share of the quote's content words found inside one window of the heard
    words. Content words are the ones that are not a common function word ("the", "de") and
    have 3 letters or more; a quote with fewer than 3 of them is read whole.
  - A heard word matches a quote word if it is equal, or if both have 5 letters or more
    and are close (a speech model misspells names and rare words).
  - The best window has the most covered words; ties go to the window nearest the hint
    (the transcript's own minute, minus the offset when you give one), then to the
    narrowest one.
  - located   coverage >= 0.8      weak   0.5 to 0.8, check by hand      not_found   below 0.5

Each result keeps both clocks: `t_transcript` (what the recorder said, if known) and
`t_video` (what the audio says). Their difference, `offset_s`, is the same offset that
`resolve_deictics.py offset` estimates: video clock = recorder clock - offset. The median per
session is printed, so you can reuse it.

Input (one of):
  --evidence [FILE]   quote rows of _engine/evidence.md (default: ./_engine/evidence.md).
                      The minute is read from the `t_transcript` column or, failing that,
                      from the first mm:ss in `Location`.
  --quotes FILE       JSON list of {"id", "session", "quote", "t_transcript" (optional)}.
Media: --media SESSION=PATH (repeat) or --media-dir DIR (a file whose name starts with the
session ID). Audio or video; the speech model reads the file itself.

Usage:
  python3 scripts/locate_quotes.py --evidence --media-dir ../recordings --cache-dir ../words
  python3 scripts/locate_quotes.py --quotes quotes.json --media INT-001=a.mp4 \\
      --offset INT-001=52.8 --window 300 --format md

Exit codes: 0 every quote located; 1 some are weak or not found; 2 no local speech-to-text
installed, a bad input or a missing file. Needs `faster-whisper` or `openai-whisper`
(pip install faster-whisper). Nothing leaves the machine. Recordings and the word files in
--cache-dir are personal data: keep them outside the project and delete them when done.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import math
import re
import statistics
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_deictics import clock_seconds, mmss  # noqa: E402  (one clock convention)

LOCATED = 0.8
WEAK = 0.5
MIN_CONTENT_WORDS = 3
FUZZY_MIN_LETTERS = 5
FUZZY_RATIO = 0.8
MEDIA_SUFFIXES = (".mp4", ".mov", ".mkv", ".webm", ".m4a", ".mp3", ".wav", ".aac", ".ogg", ".flac")
ITEM_ID = re.compile(r"(?:INT|VAL|OBS)-\d")
CLOCK = re.compile(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b")

STOPWORDS = {
    # English
    "the", "and", "for", "but", "not", "you", "are", "was", "were", "with", "that", "this",
    "have", "has", "had", "its", "from", "they", "them", "their", "then", "than", "there",
    "what", "when", "which", "who", "will", "would", "can", "could", "just", "like", "got",
    "all", "any", "out", "one", "our", "your", "his", "her", "she", "him", "how", "why",
    "yeah", "okay", "also", "very", "too", "about", "into", "some", "been", "being",
    # Spanish
    "que", "los", "las", "una", "uno", "unos", "unas", "del", "por", "con", "para", "pero",
    "como", "mas", "muy", "ese", "esa", "esto", "eso", "este", "esta", "sus", "les", "nos",
    "fue", "era", "son", "hay", "ser", "ver", "yo", "tus", "mis", "cuando", "donde", "porque",
    "tambien", "entonces", "bueno", "claro", "sino", "sin", "sobre", "hasta", "desde",
}


# ------------------------------------------------------------------ words

def norm_tokens(text: str) -> list:
    """Lowercase, no accents, no [bracketed corrections], words and digits only."""
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", text)


def content_tokens(tokens: list) -> list:
    """The words that carry the quote. A very short quote is read whole."""
    kept = [t for t in tokens if len(t) >= 3 and t not in STOPWORDS]
    return kept if len(kept) >= MIN_CONTENT_WORDS else list(tokens)


def words_match(a: str, b: str) -> bool:
    if a == b:
        return True
    if len(a) < FUZZY_MIN_LETTERS or len(b) < FUZZY_MIN_LETTERS:
        return False
    return SequenceMatcher(None, a, b).ratio() >= FUZZY_RATIO


def flatten_words(raw_words: list) -> list:
    """[(token, start_s, end_s)] from [{"word", "start", "end"}]. One heard word may
    hold several tokens ("don't"); they share its times."""
    flat = []
    for w in raw_words:
        for tok in norm_tokens(str(w.get("word", ""))):
            flat.append((tok, float(w["start"]), float(w["end"])))
    return flat


def coverage_in_tokens(quote: str, heard_tokens: list) -> float:
    """Share of the quote's content words that appear anywhere in `heard_tokens`.
    For a short text already known to hold the quote (a cut clip)."""
    q = content_tokens(norm_tokens(quote))
    if not q:
        return 0.0
    heard = set(heard_tokens)
    cache = {}

    def found(word):
        if word not in cache:
            cache[word] = word in heard or any(words_match(word, h) for h in heard)
        return cache[word]

    return sum(1 for w in q if found(w)) / len(q)


def locate(flat: list, quote: str, hint_s=None, radius_s=None):
    """Best window of heard words for `quote`.

    Returns {"coverage", "start_s", "end_s", "matched", "of"} or None if the quote has no
    words or nothing was heard. `hint_s` breaks ties; with `radius_s` the search is
    limited to heard words that start within that distance of the hint."""
    all_tokens = norm_tokens(quote)
    q = content_tokens(all_tokens)
    if not q or not flat:
        return None
    first = 0
    last = len(flat)
    if hint_s is not None and radius_s is not None:
        inside = [i for i, (_, s, _) in enumerate(flat) if abs(s - hint_s) <= radius_s]
        if not inside:
            return None
        first, last = inside[0], inside[-1] + 1
    span = max(len(all_tokens), len(q))
    size = math.ceil(span * 1.5) + 3

    verdict = {}  # heard token -> list of quote indexes it matches, built lazily

    def matches(tok):
        if tok not in verdict:
            verdict[tok] = [k for k, w in enumerate(q) if words_match(w, tok)]
        return verdict[tok]

    positions = [[] for _ in q]
    for i in range(first, last):
        for k in matches(flat[i][0]):
            positions[k].append(i)

    # covered[start] = how many quote words have a heard match in flat[start:start+size]
    diff = [0] * (len(flat) + 2)
    for plist in positions:
        merged = []
        for p in plist:
            lo, hi = max(first, p - size + 1), p
            if merged and lo <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        for lo, hi in merged:
            diff[lo] += 1
            diff[hi + 1] -= 1
    best, running = 0, 0
    counts = []
    for i in range(len(flat)):
        running += diff[i]
        counts.append(running)
        best = max(best, running)
    if best == 0:
        return None

    pick = None
    for i in range(first, last):
        if counts[i] != best:
            continue
        window_end = min(i + size, len(flat))
        found = []  # (index, quote word) of matches inside the window
        for k, plist in enumerate(positions):
            for p in plist:
                if i <= p < window_end:
                    found.append((p, k))
        mid = statistics.median(p for p, _ in found)
        chosen = {}
        for p, k in found:  # one heard match per quote word, the one nearest the cluster
            if k not in chosen or abs(p - mid) < abs(chosen[k] - mid):
                chosen[k] = p
        lo, hi = min(chosen.values()), max(chosen.values())
        start_s, end_s = flat[lo][1], flat[hi][2]
        near = abs(start_s - hint_s) if hint_s is not None else 0.0
        key = (near, hi - lo)
        if pick is None or key < pick[0]:
            pick = (key, start_s, end_s)
    _, start_s, end_s = pick
    return {"coverage": round(best / len(q), 2), "start_s": round(start_s, 2),
            "end_s": round(end_s, 2), "matched": best, "of": len(q)}


def status_of(coverage: float) -> str:
    if coverage >= LOCATED:
        return "located"
    return "weak" if coverage >= WEAK else "not_found"


# ------------------------------------------------------------------ times

def parse_time(value):
    """Seconds from 52.8, "52.8", "1:05" or "1:02:03"; None if empty."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().strip("[]()")
    m = CLOCK.fullmatch(text)
    if m:
        return float(clock_seconds(m.group(1), m.group(2), m.group(3)))
    return float(text)


def location_clock(cell: str):
    m = CLOCK.search(cell or "")
    return float(clock_seconds(m.group(1), m.group(2), m.group(3))) if m else None


# ------------------------------------------------------------------ input

def read_evidence(path: Path) -> list:
    """Quote rows of the evidence ledger, with their transcript minute when it is there.
    Columns are found by header name, so a ledger with more or fewer columns works.
    Vetoed rows are skipped: nothing is played from them."""
    import verify_quotes
    items, at = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        lowered = [c.lower() for c in cells]
        if "evidence id" in lowered and "type" in lowered:
            at = {name: lowered.index(name) for name in
                  ("evidence id", "interview", "type", "evidence", "location", "use in synthesis",
                   "t_transcript") if name in lowered}
            continue
        if not at or len(cells) <= at.get("evidence", 99):
            continue
        if "interview" not in at or not ITEM_ID.match(cells[at["interview"]]):
            continue
        if cells[at["type"]].lower() not in ("quote", "cita"):
            continue
        use = cells[at["use in synthesis"]] if "use in synthesis" in at and at["use in synthesis"] < len(cells) else ""
        if re.match(r"(vetoed|vetada)\b", use, re.I):
            continue
        t = None
        if "t_transcript" in at and at["t_transcript"] < len(cells):
            t = parse_time(cells[at["t_transcript"]])
        if t is None and "location" in at and at["location"] < len(cells):
            t = location_clock(cells[at["location"]])
        for n, piece in enumerate(verify_quotes.quotes_of(cells[at["evidence"]]), 1):
            eid = cells[at["evidence id"]]
            items.append({"id": eid if n == 1 else f"{eid}#{n}",
                          "session": cells[at["interview"]], "quote": piece, "t_transcript": t})
    return items


def read_quotes(path: Path) -> list:
    rows = json.loads(path.read_text(encoding="utf-8"))
    items = []
    for n, r in enumerate(rows, 1):
        session = r.get("session") or r.get("int")
        if not session or not r.get("quote"):
            raise ValueError(f"item {n} needs a 'session' and a 'quote'")
        items.append({"id": r.get("id") or f"Q{n:03d}", "session": session, "quote": r["quote"],
                      "t_transcript": parse_time(r.get("t_transcript"))})
    return items


def resolve_media(session: str, media: dict, media_dir):
    """Path of the recording for a session, or None."""
    if session in media:
        return Path(media[session])
    if media_dir:
        hits = sorted(p for p in Path(media_dir).iterdir()
                      if p.is_file() and p.suffix.lower() in MEDIA_SUFFIXES
                      and p.name.lower().startswith(session.lower()))
        if hits:
            return hits[0]
    return None


def parse_pairs(values, what):
    """['A=1', 'B=2'] -> {'A': '1', 'B': '2'}"""
    out = {}
    for v in values or []:
        if "=" not in v:
            raise ValueError(f"{what} wants SESSION=VALUE, got {v!r}")
        key, val = v.split("=", 1)
        out[key.strip()] = val.strip()
    return out


# ------------------------------------------------------------------ speech to text

def detect_backend():
    """'faster_whisper', 'whisper' (openai-whisper) or None. A PyPI package also called
    `whisper` is not a speech model, so it is checked for `load_model`."""
    for name in ("faster_whisper", "whisper"):
        if importlib.util.find_spec(name) is None:
            continue
        if name == "whisper":
            try:
                if not hasattr(importlib.import_module("whisper"), "load_model"):
                    continue
            except Exception:  # a broken install is the same as none
                continue
        return name
    return None


NO_BACKEND = ("No local speech-to-text found. Install one, for example:\n"
              "  pip install faster-whisper      (or: pip install openai-whisper)\n"
              "It runs on this machine; no audio is sent anywhere.")


class Transcriber:
    """Words with times from an audio or video file. The model loads on first use."""

    def __init__(self, backend, model="small", language=None):
        self.backend, self.model_name, self.language = backend, model, language
        self._model = None

    def words(self, media) -> list:
        if self._model is None:
            if self.backend == "faster_whisper":
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self.model_name, compute_type="int8")
            else:
                import whisper
                self._model = whisper.load_model(self.model_name)
        if self.backend == "faster_whisper":
            segments, _ = self._model.transcribe(str(media), language=self.language,
                                                 word_timestamps=True)
            return [{"word": w.word, "start": w.start, "end": w.end}
                    for s in segments for w in (s.words or [])]
        result = self._model.transcribe(str(media), language=self.language,
                                        word_timestamps=True, fp16=False)
        return [{"word": w["word"], "start": w["start"], "end": w["end"]}
                for s in result["segments"] for w in s.get("words", [])]


def cached_words(media: Path, cache_dir, transcriber) -> list:
    """Transcribe once per file: the result is kept in cache_dir under a name that
    changes when the file does."""
    if not cache_dir:
        return transcriber.words(media)
    stat = media.stat()
    key = hashlib.sha1(f"{media.name}|{stat.st_size}|{int(stat.st_mtime)}".encode()).hexdigest()[:10]
    path = Path(cache_dir) / f"{media.stem}-{key}.words.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    words = transcriber.words(media)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    return words


# ------------------------------------------------------------------ run

def locate_all(items, words_of, offsets, window_s, default_offset=0.0):
    """Results per item. `words_of(session)` gives the flat words, or None without media."""
    results = []
    for item in items:
        flat = words_of(item["session"])
        row = {"id": item["id"], "session": item["session"], "quote": item["quote"],
               "t_transcript_s": item["t_transcript"]}
        if flat is None:
            row.update(status="no_media", coverage=0.0)
            results.append(row)
            continue
        offset = offsets.get(item["session"], default_offset)
        hint = item["t_transcript"] - offset if item["t_transcript"] is not None else None
        found = locate(flat, item["quote"], hint, window_s if hint is not None else None)
        if found is None:
            row.update(status="not_found", coverage=0.0)
        else:
            status = status_of(found["coverage"])
            row.update(status=status, coverage=found["coverage"], matched=found["matched"],
                       of=found["of"])
            if status != "not_found":
                row.update(t_video_s=found["start_s"], t_video=mmss(found["start_s"]),
                           end_s=found["end_s"])
                if item["t_transcript"] is not None:
                    row["t_transcript"] = mmss(item["t_transcript"])
                    row["offset_s"] = round(item["t_transcript"] - found["start_s"], 1)
        results.append(row)
    return results


def session_offsets(results) -> dict:
    """Median offset per session from the quotes that were located well."""
    by = {}
    for r in results:
        if r["status"] == "located" and "offset_s" in r:
            by.setdefault(r["session"], []).append(r["offset_s"])
    return {s: {"offset_s": round(statistics.median(v), 1), "n": len(v),
                "spread_s": round(max(v) - min(v), 1)} for s, v in by.items()}


def render_md(results, offsets) -> str:
    lines = ["| ID | Session | t_transcript | t_video | Coverage | Status |", "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['id']} | {r['session']} | {r.get('t_transcript', '')} | "
                     f"{r.get('t_video', '')} | {r['coverage']:.2f} | {r['status']} |")
    for s, o in offsets.items():
        lines.append(f"\n{s}: offset {o['offset_s']} s (recorder - video) from {o['n']} quotes, "
                     f"spread {o['spread_s']} s")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Find each quote's minute in the video (local speech-to-text).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--evidence", nargs="?", const="_engine/evidence.md", metavar="FILE",
                     help="quote rows of the evidence ledger")
    src.add_argument("--quotes", metavar="FILE", help="JSON list of {id, session, quote, t_transcript}")
    ap.add_argument("--media", action="append", metavar="SESSION=PATH", help="recording of a session")
    ap.add_argument("--media-dir", help="folder with recordings named after the session ID")
    ap.add_argument("--offset", action="append", metavar="[SESSION=]SECONDS",
                    help="recorder clock - video clock; one number for all sessions or per session")
    ap.add_argument("--window", type=float, metavar="SECONDS",
                    help="search only this far around transcript minute - offset (default: the whole recording)")
    ap.add_argument("--cache-dir", help="keep the heard words here, one file per recording")
    ap.add_argument("--model", default="small", help="speech model size (default: small)")
    ap.add_argument("--lang", help="language code of the audio (default: detected)")
    ap.add_argument("--out", help="write the result here (default: print)")
    ap.add_argument("--format", choices=("json", "md"), default="json")
    a = ap.parse_args(argv)

    try:
        items = read_evidence(Path(a.evidence)) if a.evidence else read_quotes(Path(a.quotes))
        media = parse_pairs(a.media, "--media")
        offsets, default_offset = {}, 0.0
        for v in a.offset or []:
            if "=" in v:
                k, val = v.split("=", 1)
                offsets[k.strip()] = float(val)
            else:
                default_offset = float(v)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"locate_quotes: {err}", file=sys.stderr)
        return 2
    if not items:
        print("locate_quotes: no quotes to locate.", file=sys.stderr)
        return 2

    sessions = sorted({i["session"] for i in items})
    paths = {s: resolve_media(s, media, a.media_dir) for s in sessions}
    for s, p in paths.items():
        if p is not None and not p.is_file():
            print(f"locate_quotes: {s}: {p} is not a file.", file=sys.stderr)
            return 2

    backend = detect_backend()
    if backend is None and any(p is not None for p in paths.values()):
        print(NO_BACKEND, file=sys.stderr)
        return 2

    transcriber = Transcriber(backend, a.model, a.lang)
    memo = {}

    def words_of(session):
        if paths[session] is None:
            return None
        if session not in memo:
            print(f"listening to {paths[session].name} ...", file=sys.stderr)
            memo[session] = flatten_words(cached_words(paths[session], a.cache_dir, transcriber))
        return memo[session]

    results = locate_all(items, words_of, offsets, a.window, default_offset)
    per_session = session_offsets(results)
    if a.format == "md":
        text = render_md(results, per_session)
    else:
        text = json.dumps({"results": results, "sessions": per_session}, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    good = sum(r["status"] == "located" for r in results)
    print(f"{good} of {len(results)} located (coverage >= {LOCATED}); the rest need a person.",
          file=sys.stderr)
    return 0 if good == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
