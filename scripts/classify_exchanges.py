#!/usr/bin/env python3
"""Judge every exchange of an interview with jev: one call per exchange.

EXPERIMENTAL and optional. Without a typesafe key it exits with code 2 and the
feedback goes on without the judged parts. See jev_client.py.

Usage
  # --dry-run first: prints one request and the cost, calls nothing
  python3 classify_exchanges.py --items discovery/_engine/feedback/INT-004-ana.jsonl \\
      --pack discovery/_engine/feedback/depth-pack.json \\
      --out discovery/_engine/feedback/INT-004-ana-depth.csv --dry-run
  # then the same without --dry-run, and again with branches-pack.json
  #   --out discovery/_engine/feedback/INT-004-ana-branches.csv

The answers are cached next to the CSV (<out>.answers.jsonl): running again is
free. After changing a pack, pass --redo, or the old answers come back.

Exit codes: 0 ok · 2 no key (go on without jev) · 1 a real error.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev_client as jev  # noqa: E402


def read_items(path, limit=None):
    items, seen = [], set()
    for n, line in enumerate(Path(path).open(encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            sys.exit(f"{path}:{n}: not valid JSON ({e})")
        if "id" not in item or "state" not in item:
            sys.exit(f"{path}:{n}: missing 'id' or 'state'")
        item["id"] = str(item["id"])
        if item["id"] in seen:
            sys.exit(f"{path}:{n}: repeated id '{item['id']}'")
        seen.add(item["id"])
        items.append(item)
        if limit and len(items) >= limit:
            break
    if not items:
        sys.exit(f"{path}: no items")
    return items


def parse_vars(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"malformed --var: '{p}'. Use NAME=value")
        k, v = p.split("=", 1)
        out[k.strip()] = v
    return out


def main():
    ap = argparse.ArgumentParser(description="Judge exchanges with jev (optional).")
    ap.add_argument("--items", required=True, help="JSONL from segment_interview.py")
    ap.add_argument("--pack", required=True, help="depth-pack.json or branches-pack.json")
    ap.add_argument("--out", required=True, help="CSV to write")
    ap.add_argument("--var", action="append", metavar="NAME=value",
                    help="a variable the pack asks for (repeatable)")
    ap.add_argument("--limit", type=int, help="only the first N exchanges")
    ap.add_argument("--dry-run", action="store_true", help="call nothing")
    ap.add_argument("--redo", action="store_true", help="ignore the cache")
    args = ap.parse_args()

    items = read_items(args.items, args.limit)
    try:
        _, questions = jev.load_pack(args.pack, parse_vars(args.var))
    except (ValueError, json.JSONDecodeError) as e:
        sys.exit(str(e))

    out = Path(args.out)
    cache_path = out.with_suffix(".answers.jsonl")
    print(f"Exchanges: {len(items)} · pack: {Path(args.pack).name} "
          f"({len(questions)} questions) · model: {jev.MODEL}")

    tokens, usd = jev.estimated_cost(items, questions)
    if args.dry_run:
        print("\n--- sample request (truncated) ---")
        print(json.dumps({"model": jev.MODEL, "state": items[0]["state"], "questions": questions},
                         ensure_ascii=False, indent=2)[:2600])
        print(f"\n~{tokens:,.0f} input tokens · USD {usd:.4f} at list price")
        return 0

    key = jev.read_key()
    if not key:
        print(f"⚠ {jev.NO_KEY_MESSAGE}", file=sys.stderr)
        return 2

    answers, failures = jev.run(items, questions, key, cache_path, args.redo)
    cols = ["id"] + jev.columns_of(questions)
    rows, tin = [], 0
    for item in items:
        a = answers.get(item["id"])
        if not a:
            continue
        tin += a.get("_in", 0)
        rows.append({c: (a.get(c, "") if c != "id" else item["id"]) for c in cols})

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"\n{out}  ({len(rows)} of {len(items)} exchanges)")
    print(f"Spent: {tin:,} input tokens · USD {tin * jev.USD_PER_INPUT_TOKEN:.4f}")
    if failures:
        print(f"\n⚠ {len(failures)} without an answer (left out of the CSV):", file=sys.stderr)
        for i, e in failures[:10]:
            print(f"  {i}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
