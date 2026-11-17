#!/usr/bin/env python3
"""Turn the exercise menu (7-validation/exercise-menu.md) into a page of buttons.

The researcher picks, the page adds up. Each exercise gets three buttons, go, maybe and
no. The page sums the minutes of the `go` rows, and of `go` plus `maybe`, against the
session length, and turns red when `go` does not fit. It loads nothing from outside and
needs no server: open the file.

  python3 build_menu.py MENU.md [--out FILE]      write the page (default: next to the menu)
  python3 build_menu.py MENU.md --apply FILE      write the choices of FILE into the Choice column

What it reads from the menu, and nothing else:

  * a line `Session length: 60 minutes`, and an optional `Reserve: 10 minutes` (consent,
    welcome and closing), which is subtracted;
  * the table whose header has the columns ID, Exercise, Minutes and Choice, in any order
    (the header words are not translated: keep them as the template has them);
  * a row is an exercise when its first cell looks like E-01 / E-12.
    `Minutes` is a number; a range such as 5-8 counts at its upper end.

FILE for --apply has one choice per line, `E-01: go`, `E-02 maybe`, `E-03 = no`. That is
the text the page copies. A line for an ID that is not in the menu is reported and the
menu is left untouched. A value that is not go, maybe or no is refused.

Exit codes: 0 done, 1 something to fix in the menu or the choices, 2 a file that cannot be read.
Standard library only.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

CHOICES = ("go", "maybe", "no")
ID_RE = re.compile(r"^E-\d+$")
REQUIRED = ("id", "exercise", "minutes", "choice")


class MenuError(Exception):
    pass


def _cells(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _minutes(text: str):
    nums = [int(n) for n in re.findall(r"\d+", text)]
    return max(nums) if nums else None


def parse_menu(text: str) -> dict:
    """Return {"length", "reserve", "rows", "header", "lines"} or raise MenuError."""
    length = re.search(r"^Session length:\s*(\d+)", text, re.M | re.I)
    reserve = re.search(r"^Reserve:\s*(\d+)", text, re.M | re.I)
    lines = text.splitlines()
    header_at = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("|"):
            names = [c.lower() for c in _cells(line)]
            if all(r in names for r in REQUIRED):
                header_at = i
                break
    if header_at is None:
        raise MenuError("no table with the columns ID, Exercise, Minutes and Choice")
    header = [c.lower() for c in _cells(lines[header_at])]
    col = {name: header.index(name) for name in REQUIRED}
    rows = []
    for i in range(header_at + 2, len(lines)):
        if not lines[i].lstrip().startswith("|"):
            break
        cells = _cells(lines[i])
        if len(cells) < len(header) or not ID_RE.match(cells[col["id"]]):
            continue
        mins = _minutes(cells[col["minutes"]])
        if mins is None:
            raise MenuError(f"{cells[col['id']]} has no number of minutes")
        choice = cells[col["choice"]].lower()
        if choice and choice not in CHOICES:
            raise MenuError(f"{cells[col['id']]} has the choice '{choice}': use go, maybe or no")
        rows.append({"id": cells[col["id"]], "exercise": cells[col["exercise"]],
                     "minutes": mins, "choice": choice, "line": i,
                     "cells": cells,
                     "extra": [(header[j], cells[j]) for j in range(len(header))
                               if j not in col.values() and cells[j]]})
    if not rows:
        raise MenuError("the table has no exercise rows (an ID like E-01 in the first column)")
    return {"length": int(length.group(1)) if length else None,
            "reserve": int(reserve.group(1)) if reserve else 0,
            "rows": rows, "header": header, "col": col, "lines": lines}


def totals(rows: list) -> dict:
    go = sum(r["minutes"] for r in rows if r["choice"] == "go")
    maybe = sum(r["minutes"] for r in rows if r["choice"] == "maybe")
    return {"go": go, "go_maybe": go + maybe}


def parse_choices(text: str) -> dict:
    out = {}
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(E-\d+)\s*[:=]?\s*([A-Za-z]+)\s*$", line)
        if not m:
            raise MenuError(f"line {n} of the choices is not 'E-01: go': {raw!r}")
        value = m.group(2).lower()
        if value not in CHOICES:
            raise MenuError(f"line {n}: '{value}' is not go, maybe or no")
        out[m.group(1)] = value
    return out


def apply_choices(menu: dict, choices: dict) -> tuple:
    """Return (new text, ids in the choices that the menu does not have)."""
    known = {r["id"] for r in menu["rows"]}
    unknown = sorted(set(choices) - known)
    lines = list(menu["lines"])
    for r in menu["rows"]:
        if r["id"] in choices:
            cells = list(r["cells"])
            cells[menu["col"]["choice"]] = choices[r["id"]]
            lines[r["line"]] = "| " + " | ".join(cells) + " |"
    return "\n".join(lines) + "\n", unknown


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Exercise menu</title>
<style>
:root{--bg:#f6f7f9;--surface:#fff;--fg:#17202b;--muted:#5b6675;--line:#dde2ea;--accent:#1f5fd1;
--go:#1d7a4f;--maybe:#b4561b;--no:#5b6675;--bad:#b3261e;--soft:#eaf0fb;--sans:system-ui,-apple-system,"Segoe UI",sans-serif;--mono:ui-monospace,Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#11161d;--surface:#18202a;--fg:#e7ecf2;--muted:#9aa6b5;--line:#2a3542;--accent:#7aa7ff;--go:#5fc795;--maybe:#f0a066;--no:#9aa6b5;--bad:#ff8a80;--soft:#1c2a40;color-scheme:dark}}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:16px;line-height:1.5}
.wrap{max-width:900px;margin:0 auto;padding-inline:16px;padding-block:24px 64px}
h1{font-size:clamp(24px,5vw,32px);margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 16px}
.bar{position:sticky;top:0;background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:12px 16px;display:flex;flex-wrap:wrap;gap:8px 24px;align-items:baseline;z-index:2}
.bar b{font-family:var(--mono);font-size:20px}
.bar .over{color:var(--bad)}
.row{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin-top:12px;display:grid;gap:8px}
.row h2{font-size:16px;margin:0}
.meta{font-family:var(--mono);font-size:12px;color:var(--muted)}
.btns{display:flex;gap:8px;flex-wrap:wrap}
button{font:inherit;padding:8px 16px;min-height:44px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--fg);cursor:pointer}
button[aria-pressed="true"].go{background:var(--go);color:#fff;border-color:var(--go)}
button[aria-pressed="true"].maybe{background:var(--maybe);color:#fff;border-color:var(--maybe)}
button[aria-pressed="true"].no{background:var(--no);color:#fff;border-color:var(--no)}
.out{margin-top:24px;display:grid;gap:8px}
textarea{width:100%;min-height:140px;font-family:var(--mono);font-size:13px;background:var(--surface);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px;box-sizing:border-box}
</style>
</head>
<body>
<div class="wrap">
<h1>Exercise menu</h1>
<p class="sub">Press go, maybe or no on each exercise. The minutes add up against the session. Nothing leaves this page until you copy the choices.</p>
<div class="bar" id="bar" role="status" aria-live="polite"></div>
__ROWS__
<div class="out">
<button type="button" id="copy">Copy the choices</button>
<textarea id="choices" readonly aria-label="Choices, one per line"></textarea>
<p class="sub">Paste them into a file and run <code>build_menu.py &lt;menu&gt; --apply &lt;file&gt;</code>.</p>
</div>
</div>
<script>
var DATA = __DATA__;
var state = {};
DATA.rows.forEach(function (r) { state[r.id] = r.choice || ""; });
function sum(values) {
  return DATA.rows.reduce(function (t, r) { return values.indexOf(state[r.id]) >= 0 ? t + r.minutes : t; }, 0);
}
function render() {
  var go = sum(["go"]), both = sum(["go", "maybe"]);
  var room = DATA.length === null ? null : DATA.length - DATA.reserve;
  var bar = document.getElementById("bar");
  var html = "<span>go <b class=\\"" + (room !== null && go > room ? "over" : "") + "\\">" + go + "</b> min</span>" +
             "<span>go + maybe <b class=\\"" + (room !== null && both > room ? "over" : "") + "\\">" + both + "</b> min</span>";
  if (room !== null) {
    html += "<span>room " + room + " min" + (DATA.reserve ? " (session " + DATA.length + ", reserve " + DATA.reserve + ")" : "") + "</span>";
    html += "<span class=\\"" + (go > room ? "over" : "") + "\\">" + (go > room ? (go - room) + " min over: drop something" : (room - go) + " min left") + "</span>";
  } else {
    html += "<span>the menu has no session length</span>";
  }
  bar.innerHTML = html;
  document.querySelectorAll("button[data-id]").forEach(function (b) {
    b.setAttribute("aria-pressed", state[b.dataset.id] === b.dataset.v ? "true" : "false");
  });
  document.getElementById("choices").value = DATA.rows.filter(function (r) { return state[r.id]; })
    .map(function (r) { return r.id + ": " + state[r.id]; }).join("\\n");
}
document.addEventListener("click", function (e) {
  var b = e.target.closest("button[data-id]");
  if (b) { state[b.dataset.id] = state[b.dataset.id] === b.dataset.v ? "" : b.dataset.v; render(); }
});
document.getElementById("copy").addEventListener("click", function () {
  var box = document.getElementById("choices");
  box.select();
  try { navigator.clipboard.writeText(box.value); } catch (err) { document.execCommand("copy"); }
});
render();
</script>
</body>
</html>
"""


def build_page(menu: dict) -> str:
    rows = []
    for r in menu["rows"]:
        extra = " · ".join(f"{html.escape(k)}: {html.escape(v)}" for k, v in r["extra"])
        buttons = "".join(
            f'<button type="button" class="{c}" data-id="{r["id"]}" data-v="{c}" aria-pressed="false">{c}</button>'
            for c in CHOICES)
        rows.append(f'<section class="row"><h2>{html.escape(r["id"])} · {html.escape(r["exercise"])}</h2>'
                    f'<div class="meta">{r["minutes"]} min{" · " + extra if extra else ""}</div>'
                    f'<div class="btns">{buttons}</div></section>')
    data = {"length": menu["length"], "reserve": menu["reserve"],
            "rows": [{"id": r["id"], "minutes": r["minutes"], "choice": r["choice"]}
                     for r in menu["rows"]]}
    payload = json.dumps(data).replace("</", "<\\/")
    return PAGE.replace("__ROWS__", "\n".join(rows)).replace("__DATA__", payload)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Page of buttons for the exercise menu.")
    ap.add_argument("menu", help="7-validation/exercise-menu.md")
    ap.add_argument("--out", help="where to write the page (default: <menu>.html next to it)")
    ap.add_argument("--apply", metavar="FILE", help="write the choices of FILE into the menu")
    args = ap.parse_args(argv)
    path = Path(args.menu)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        print(f"Cannot read {path}: {err}", file=sys.stderr)
        return 2
    try:
        menu = parse_menu(text)
        if args.apply:
            try:
                choices = parse_choices(Path(args.apply).read_text(encoding="utf-8"))
            except OSError as err:
                print(f"Cannot read {args.apply}: {err}", file=sys.stderr)
                return 2
            new_text, unknown = apply_choices(menu, choices)
            if unknown:
                print("Not in the menu, nothing was written: " + ", ".join(unknown), file=sys.stderr)
                return 1
            path.write_text(new_text, encoding="utf-8")
            t = totals(parse_menu(new_text)["rows"])
            print(f"{len(choices)} choices written. go: {t['go']} min, go + maybe: {t['go_maybe']} min.")
            return 0
        out = Path(args.out) if args.out else path.with_suffix(".html")
        out.write_text(build_page(menu), encoding="utf-8")
        print(f"Page written to {out}")
        if menu["length"] is None:
            print("The menu has no 'Session length: N minutes' line: the page cannot compare.")
        return 0
    except MenuError as err:
        print(f"Menu: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
