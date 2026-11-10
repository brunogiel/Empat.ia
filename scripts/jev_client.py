#!/usr/bin/env python3
"""Client for jev (typesafe.ai), the optional judge of the interviewer feedback.

A library, not a CLI: the one you run is classify_exchanges.py.

EXPERIMENTAL. jev answers closed questions about one item per call, with no
batch and no neighbours, so the judgement of one exchange never bleeds into the
next. It does not write and does not reason. On the first real round (five
interviews, about 500 exchanges, about one US cent per interview) the questions
about the person's answer held up; the ones about the interviewer's own question
did not, and are counted by hand. Check the first run of a new project by hand.

The API key never lives in the repository or in the project folder:
    export TYPESAFE_API_KEY="tsk_..."
    # or
    mkdir -p ~/.config/typesafe && echo "tsk_..." > ~/.config/typesafe/api_key
    chmod 600 ~/.config/typesafe/api_key

Optional everywhere. Without a key, classify_exchanges.py exits with code 2 and
the feedback goes on without the judged parts: the two scales that are plain
counts still come out.
"""

import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
CONCURRENCY = 6
RETRIES = 5
USD_PER_INPUT_TOKEN = 42 / 1e9  # list price, USD 42 per billion input tokens

TYPES = ("noul", "choice", "score")

NO_KEY_MESSAGE = (
    "no typesafe key: the feedback goes on without the judged parts.\n"
    "  jev is optional. To turn it on:\n"
    "    mkdir -p ~/.config/typesafe && echo 'tsk_...' > ~/.config/typesafe/api_key\n"
    "    chmod 600 ~/.config/typesafe/api_key"
)


def read_key():
    """The key, or None when there is none. Never stops the program."""
    k = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if k:
        return k
    f = Path.home() / ".config" / "typesafe" / "api_key"
    if f.is_file():
        k = f.read_text().strip()
        if k:
            return k
    return None


def load_pack(path, variables=None):
    """Read a pack and fill in its variables.

    A pack is {"descripcion": ..., "variables": [...], "preguntas": {id: question}}.
    Only "preguntas" is sent. The question ids are for the code and never reach
    the model, so each question has to say on its own what it wants to know.
    Anything else at the top level (the topic titles, for example) stays local.
    """
    pack = json.loads(Path(path).read_text(encoding="utf-8"))
    questions = pack.get("preguntas")
    if not questions:
        raise ValueError(f"{path}: the pack has no 'preguntas'")

    variables = dict(variables or {})
    missing = [v for v in pack.get("variables") or [] if v not in variables]
    if missing:
        raise ValueError(f"{path}: missing variables: {', '.join(missing)} "
                         "(pass them with --var NAME=value)")

    questions = _substitute(questions, variables)
    for qid, q in questions.items():
        if q.get("type") not in TYPES:
            raise ValueError(f"{path}: question '{qid}' has an invalid type: {q.get('type')}")
        left = _placeholders(q)
        if left:
            raise ValueError(f"{path}: question '{qid}' still has {{{left[0]}}} unresolved. "
                             "Build the pack with feedback_packs.py, or pass it with --var.")
    return pack, questions


def _substitute(obj, variables):
    if isinstance(obj, str):
        for k, v in variables.items():
            obj = obj.replace("{" + k + "}", str(v))
        return obj
    if isinstance(obj, dict):
        return {k: _substitute(v, variables) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute(v, variables) for v in obj]
    return obj


def _placeholders(obj):
    return re.findall(r"\{([A-Z_][A-Z0-9_]*)\}", json.dumps(obj, ensure_ascii=False))


def ask(state, questions, key):
    """One call with ALL the questions: the state is paid for once.

    The questions run in parallel and do not see each other.
    """
    body = json.dumps({"model": MODEL, "state": state, "questions": questions},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    last = None
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}"
            if e.code in (429, 500, 502, 503, 529):
                time.sleep((2 ** attempt) + random.random())
                continue
            raise RuntimeError(last) from e
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep((2 ** attempt) + random.random())
    raise RuntimeError(f"no answer after {RETRIES} attempts: {last}")


def flatten(resp):
    """From the API answer to flat columns: per question, its value.

    A noul gives a probability (`<id>_p`); a choice or a score gives its value and
    a confidence (`<id>_conf`). The confidence does not rank a list: it says
    which single item to doubt. A low confidence on a choice usually means the
    pack is missing an option.
    """
    out = {}
    for qid, a in (resp.get("answers") or {}).items():
        kind = a.get("type")
        if kind == "noul":
            out[f"{qid}_p"] = a.get("noul")
        elif kind == "choice":
            out[qid] = a.get("choice")
        elif kind == "score":
            out[qid] = a.get("score")
        out[f"{qid}_conf"] = a.get("confidence")
    usage = resp.get("usage") or {}
    out["_in"] = usage.get("input_tokens", 0)
    out["_out"] = usage.get("output_tokens", 0)
    return out


def columns_of(questions):
    """The column names flatten() returns, in the pack's order. A noul has no
    separate confidence: the probability is the answer."""
    cols = []
    for qid, q in questions.items():
        cols += [f"{qid}_p"] if q["type"] == "noul" else [qid, f"{qid}_conf"]
    return cols


def run(items, questions, key, cache_path, redo=False, say=print):
    """Ask about every item, one call each, caching to JSONL.

    The cache is keyed by item id, not by question: after changing a pack, run
    with redo=True or the old answers come back silently.
    Returns (answers_by_id, failures). Failures are reported, never swallowed.
    """
    cache = {}
    cache_path = Path(cache_path)
    if cache_path.is_file() and not redo:
        for line in cache_path.open(encoding="utf-8"):
            try:
                row = json.loads(line)
                cache[row["id"]] = row
            except (json.JSONDecodeError, KeyError):
                pass
        if cache:
            say(f"Cache: {len(cache)} already answered ({cache_path.name})")
    elif cache_path.is_file():
        cache_path.unlink()

    pending = [i for i in items if i["id"] not in cache]
    if not pending:
        return cache, []

    lock, failures, done = Lock(), [], [0]
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    def work(item):
        try:
            resp = ask(item["state"], questions, key)
        except Exception as e:  # noqa: BLE001 -- reported, not swallowed
            with lock:
                failures.append((item["id"], str(e)[:140]))
            return
        row = {"id": item["id"], **flatten(resp)}
        with lock:
            cache[item["id"]] = row
            with cache_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            done[0] += 1
            if done[0] % 25 == 0 or done[0] == len(pending):
                say(f"  {done[0]}/{len(pending)}")

    say(f"Asking about {len(pending)} of {len(items)}...")
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        list(ex.map(work, pending))
    return cache, failures


def estimated_cost(items, questions):
    """Input tokens and USD at list price. The questions travel in every call."""
    pack_chars = len(json.dumps(questions, ensure_ascii=False))
    chars = sum(len(i["state"] if isinstance(i["state"], str)
                    else json.dumps(i["state"], ensure_ascii=False)) + pack_chars
                for i in items)
    tokens = chars / 4
    return tokens, tokens * USD_PER_INPUT_TOKEN
