#!/usr/bin/env python3
"""Check that _engine/state.yaml does not contradict itself.

The state of the project lives in one file, and inside that file the same fact is
written in more than one place: `current_status` and the status of the current step,
the phase and the step, a step and its sub-stages, the plan and the steps. When a
gate closes and only one of them is edited, the file says "validated" and "drafted"
at once and nobody notices until the Guide reads the wrong one. This script reads
them side by side. Same file in, same verdicts out.

Errors (exit code 1):
  - a status that is not in valid_statuses (or, for a sub-stage, not one of
    not_started | in_progress | done | skipped)
  - current_status differs from the status of the step named in current_step
  - current_phase differs from the phase of current_step
  - current_step is not a step declared in steps
  - a sub-stage is done (or in progress) while the one before it is not done or skipped
  - a step is closed (validated, advanced_with_assumptions) while a sub-stage is not done or skipped
  - a step is not_started while one of its sub-stages is in progress or done
  - a plan row is done while a step of its phase that has a gate is not closed
    (steps that are on demand and not started do not count)

Warnings (exit code 0, or 1 with --strict):
  - `next` or `recommended_reason` names, in backticks, a step or a sub-stage that is
    already closed: the pointer says to do something that is done
  - the current step is closed but `next` is empty: nobody rewrote the pointer at the gate

`substeps` and `next` are optional: a state file written before they existed passes
without them. Exit code 2 when the file is missing or cannot be read.

Usage:
  python3 scripts/check_state.py                      # <cwd>/_engine/state.yaml
  python3 scripts/check_state.py --root discovery
  python3 scripts/check_state.py --state path/to/state.yaml --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CLOSED = {"validated", "advanced_with_assumptions"}
SUBSTEP_STATUSES = ("not_started", "in_progress", "done", "skipped")
DEFAULT_STATUSES = ("not_started", "capturing", "drafted", "validated", "advanced_with_assumptions")
# A plan piece is a phase name or a step key. Phase names, in the template's order.
PHASE_PIECES = {"desk-research": 1, "profiling": 2, "guide": 3, "field": 4, "debrief": 5,
                "ideation": 6, "validation": 7, "report": 8}


# ---- a reader for the small YAML subset state.yaml uses -------------------------------

def _strip_comment(line: str) -> str:
    quote = None
    for i, c in enumerate(line):
        if quote:
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def _split_top(text: str) -> list:
    """Split on commas that are not inside quotes, brackets or braces."""
    parts, depth, quote, cur = [], 0, None, ""
    for c in text:
        if quote:
            cur += c
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            cur += c
        elif c in "[{":
            depth += 1
            cur += c
        elif c in "]}":
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    if cur.strip():
        parts.append(cur)
    return parts


def _scalar(text: str):
    text = text.strip()
    if text == "":
        return None
    if text[0] in "\"'" and text[-1] == text[0] and len(text) >= 2:
        return text[1:-1]
    if text[0] == "[" and text[-1] == "]":
        return [_scalar(p) for p in _split_top(text[1:-1])]
    if text[0] == "{" and text[-1] == "}":
        out = {}
        for part in _split_top(text[1:-1]):
            key, _, value = part.partition(":")
            out[key.strip()] = _scalar(value)
        return out
    lowered = text.lower()
    if lowered in ("null", "~"):
        return None
    if lowered in ("true", "false"):
        return lowered == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def parse_yaml(text: str):
    """Mappings, lists, flow lists and maps, and scalars: enough for state.yaml."""
    lines = []
    for raw in text.splitlines():
        stripped = _strip_comment(raw).rstrip()
        if stripped.strip():
            lines.append((len(stripped) - len(stripped.lstrip(" ")), stripped.strip()))

    def block(i: int, indent: int):
        if i >= len(lines):
            return None, i
        if lines[i][1].startswith("- ") or lines[i][1] == "-":
            out = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("-"):
                out.append(_scalar(lines[i][1][1:].strip()))
                i += 1
            return out, i
        out = {}
        while i < len(lines) and lines[i][0] == indent:
            content = lines[i][1]
            m = re.match(r"^([^:]+?):(?:\s+(.*))?$", content)
            if not m:
                i += 1
                continue
            key, rest = m.group(1).strip().strip("\"'"), m.group(2)
            i += 1
            if rest is None or rest == "":
                if i < len(lines) and lines[i][0] > indent:
                    out[key], i = block(i, lines[i][0])
                elif i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                    out[key], i = block(i, indent)  # a list at the same indent as its key
                else:
                    out[key] = None
            else:
                out[key] = _scalar(rest)
        return out, i

    parsed, _ = block(0, lines[0][0]) if lines else ({}, 0)
    return parsed if isinstance(parsed, dict) else {}


# ---- the checks ---------------------------------------------------------------------

def check(state: dict):
    errors: list = []
    warnings: list = []
    steps = state.get("steps") or {}
    statuses = tuple(state.get("valid_statuses") or DEFAULT_STATUSES)
    current_step = state.get("current_step")
    current_status = state.get("current_status")
    substeps = state.get("substeps") or {}

    for key, step in steps.items():
        status = (step or {}).get("status")
        if status not in statuses:
            errors.append(f"steps.{key}.status is '{status}', not one of {', '.join(statuses)}")
    if current_status not in statuses:
        errors.append(f"current_status is '{current_status}', not one of {', '.join(statuses)}")

    if steps:
        if current_step not in steps:
            errors.append(f"current_step '{current_step}' is not a step declared in steps")
        else:
            step_status = (steps[current_step] or {}).get("status")
            if step_status != current_status:
                errors.append(f"current_status is '{current_status}' but steps.{current_step}.status "
                              f"is '{step_status}': a gate moves both marks")
            phase = (steps[current_step] or {}).get("phase")
            if phase is not None and state.get("current_phase") is not None \
                    and phase != state.get("current_phase"):
                errors.append(f"current_phase is {state.get('current_phase')} but current_step "
                              f"'{current_step}' belongs to phase {phase}")

    for step_key, subs in substeps.items():
        subs = subs or {}
        step_status = ((steps.get(step_key) or {}).get("status")) if steps else None
        previous_open = None
        for sub, status in subs.items():
            if status not in SUBSTEP_STATUSES:
                errors.append(f"substeps.{step_key}.{sub} is '{status}', not one of "
                              f"{', '.join(SUBSTEP_STATUSES)}")
                continue
            if status in ("done", "in_progress") and previous_open is not None:
                errors.append(f"substeps.{step_key}.{sub} is {status} but {previous_open[0]} "
                              f"before it is {previous_open[1]}")
            if status not in ("done", "skipped") and previous_open is None:
                previous_open = (sub, status)
        if step_status in CLOSED and any(s not in ("done", "skipped") for s in subs.values()):
            open_ones = ", ".join(f"{k} ({v})" for k, v in subs.items() if v not in ("done", "skipped"))
            errors.append(f"steps.{step_key}.status is '{step_status}' but sub-stages are open: {open_ones}")
        if step_status == "not_started" and any(s in ("in_progress", "done") for s in subs.values()):
            errors.append(f"steps.{step_key}.status is 'not_started' but a sub-stage has started")

    by_phase: dict = {}
    for key, step in steps.items():
        by_phase.setdefault((step or {}).get("phase"), []).append(key)
    for row in state.get("plan") or []:
        if not isinstance(row, dict) or row.get("status") != "done":
            continue
        piece = row.get("piece")
        keys = by_phase.get(PHASE_PIECES.get(piece), []) if piece in PHASE_PIECES else (
            [piece] if piece in steps else [])
        blocking = [k for k in keys
                    if steps[k].get("gate") is True
                    and not (steps[k].get("on_demand") and steps[k].get("status") == "not_started")
                    and steps[k].get("status") not in CLOSED]
        if blocking:
            errors.append(f"plan says '{piece}' is done but "
                          + ", ".join(f"{k} is {steps[k].get('status')}" for k in blocking))

    closed_steps = {k for k, v in steps.items() if (v or {}).get("status") in CLOSED}
    closed_subs = {s for subs in substeps.values() for s, v in (subs or {}).items()
                   if v in ("done", "skipped")}
    for field in ("next", "recommended_reason"):
        text = state.get(field)
        if not isinstance(text, str):
            continue
        for name in re.findall(r"`([^`]+)`", text):
            if name in closed_steps or name in closed_subs:
                warnings.append(f"{field} points at `{name}`, which is already closed")
    if steps.get(current_step) and (steps[current_step] or {}).get("status") in CLOSED \
            and not (state.get("next") or "").strip() and "next" in state:
        warnings.append(f"the current step '{current_step}' is closed and `next` is empty: "
                        "rewrite it at the gate")
    return errors, warnings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check that state.yaml does not contradict itself.")
    ap.add_argument("--root", default=".", help="discovery folder (default: current directory)")
    ap.add_argument("--state", help="state file (default: <root>/_engine/state.yaml)")
    ap.add_argument("--strict", action="store_true", help="warnings fail the run too")
    a = ap.parse_args(argv)

    path = Path(a.state) if a.state else Path(a.root) / "_engine" / "state.yaml"
    try:
        state = parse_yaml(path.read_text(encoding="utf-8"))
    except OSError as err:
        print(f"Cannot read {path}: {err}", file=sys.stderr)
        return 2
    if not state:
        print(f"{path} has nothing this script can read", file=sys.stderr)
        return 2

    errors, warnings = check(state)
    for e in errors:
        print(f"ERROR  {e}")
    for w in warnings:
        print(f"WARN   {w}")
    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings | {path}")
    return 1 if errors or (a.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
