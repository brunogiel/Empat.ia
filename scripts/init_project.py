#!/usr/bin/env python3
"""Initialize, extend or migrate the discovery folder for Empat.ia.

The folder is numbered by phase, and it grows as you go:

  0-README.md        the map
  1-desk-research/   what you research before talking to anyone
  2-profiling/       who you talk to and how you reach them
  3-guide/           the instrument you take to the field
  4-field/           interviews and observation
  5-debrief/         findings and principles
  6-ideation/        (on demand) from the HMW questions to a few concepts
  7-validation/      (on demand) a prototype in front of people
  8-report/          the final write-up of the whole project
  _engine/           state, assumptions, decisions, evidence, raw sources

Only six files exist at install. Every other file is born when you ENTER its
phase, written in the project's language. A file that does not exist yet is the
design, not a missing piece. That includes the folders of phases 6, 7 and 8:
they are born with their first --add.

The ORDER of the work is the plan in the brief (and `plan:` in state.yaml), not
the folder numbers.

Three commands:

  (default)   create a new discovery/ folder
  --add STEP  materialise one phase's file from its template
  --migrate   move a v1 or v2 folder into the v3 layout, or bring a v3 folder
              up to date (summary to 8-report/, default plan), losing nothing
"""

from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import re
import shutil
from pathlib import Path

# --- Per-interview / per-observation / per-session files, on demand --------
# The base name is the same ID the rest of the method already uses:
# INT-004-ana-lopez-acme, OBS-002-store-floor, VAL-001-ben-ito. Validated so a
# typo does not silently create a file under the wrong ID.
BASE_NAME = re.compile(r"^(INT|OBS|VAL)-\d{3}-[a-z0-9-]+$")

# Which ID prefix each kind of per-item file takes, by the start of its type:
# interview-* needs INT-, observation-* needs OBS-, validation-* needs VAL-.
ITEM_PREFIX = {"interview": "INT", "observation": "OBS", "validation": "VAL"}


# --- What exists the moment you install ------------------------------------
# Six files. Two of them are yours; four are for the machine.
INSTALL = {
    "0-readme.md": "0-README.md",
    "agents-pointer.md": "AGENTS.md",
    "claude-pointer.md": "CLAUDE.md",
    "brief.md": "1-desk-research/brief.md",
    "state.yaml": "_engine/state.yaml",
    "budgets.yaml": "_engine/budgets.yaml",
}

# --- What is born later, when its step starts ------------------------------
# The assistant calls `--add <step>`; this is the single source of truth for
# which template lands where. It mirrors the `file:` field in state.yaml.
LAZY = {
    "market_research": ("market.md", "1-desk-research/market.md"),
    "knowledge_base": ("knowledge.md", "1-desk-research/knowledge.md"),
    "profiles": ("profiles.md", "2-profiling/profiles.md"),
    "recruiting": ("recruiting.md", "2-profiling/recruiting.md"),
    "interview_guide": ("guide.md", "3-guide/guide.md"),
    "field_process": ("process.md", "3-guide/process.md"),
    "field_index": ("field-index.md", "4-field/0-index.md"),
    "interview_feedback": ("feedback-readme.md", "4-field/feedback/0-README.md"),
    "observation": ("observation-plan.md", "4-field/0-observation-plan.md"),
    "evidence": ("evidence.md", "_engine/evidence.md"),
    "assumptions": ("assumptions.md", "_engine/assumptions.md"),
    "decisions": ("decisions.md", "_engine/decisions.md"),
    "findings": ("findings.md", "5-debrief/findings.md"),
    "principles": ("principles.md", "5-debrief/principles.md"),
    "synthesis_log": ("synthesis-log.md", "_engine/synthesis-log.md"),
    "ideation": ("concepts.md", "6-ideation/concepts.md"),
    "validation_guide": ("tasks.md", "7-validation/tasks.md"),
    "validation_index": ("validation-index.md", "7-validation/0-index.md"),
    "validation_debrief": ("validation-findings.md", "7-validation/findings.md"),
    "report": ("summary.md", "8-report/summary.md"),
}

# Per-item templates the assistant copies once per interview or observation.
# They take a name, so they are not in LAZY.
PER_ITEM = {
    "interview-note": "interview-note.md",
    "interview-prep": "interview-prep.md",
    "interview-feedback": "interview-feedback.md",
    "observation-note": "observation-note.md",
    # Validation sessions reuse the interview templates: same shape of work.
    "validation-note": "interview-note.md",
    "validation-prep": "interview-prep.md",
    "validation-feedback": "interview-feedback.md",
    "notes": "notes.md",
}

# Where each per-item file lands, built from --name. Only the items that
# take a base name are here: 'notes' is the phase drawer, not per-interview,
# and is not addressed through --add.
PER_ITEM_PATHS = {
    "interview-note": "4-field/{name}.md",
    "interview-prep": "4-field/_prep/{name}-prep.md",
    "interview-feedback": "4-field/feedback/{name}-feedback.md",
    "observation-note": "4-field/{name}.md",
    "validation-note": "7-validation/{name}.md",
    "validation-prep": "7-validation/_prep/{name}-prep.md",
    "validation-feedback": "7-validation/feedback/{name}-feedback.md",
}

DIRECTORIES = [
    "1-desk-research",
    # Client material -- briefs, decks, canvases, spreadsheets, whiteboards --
    # so a human can see what the method was fed. Not the assistant's own
    # working material: that goes to _engine/sources/ below.
    "1-desk-research/sources",
    "2-profiling",
    "3-guide",
    "4-field",
    "4-field/_prep",
    "4-field/_raw",
    "4-field/feedback",
    "5-debrief",
    # 6-ideation/, 7-validation/ and 8-report/ are not here on purpose: they are
    # born with their first --add, so a project that skips them never sees them.
    "_engine",
    "_engine/sources",
    "_engine/sources/councils",
    "_engine/sources/data-reviews",
    "_engine/sources/guide-versions",
    # Project-level wrapper skills (e.g. one that fetches transcripts from the
    # team's recorder). These belong to the assistant, not the human.
    "_engine/skills",
]

# --- Migration -------------------------------------------------------------
# v2 path -> v3 path. Moves files, never deletes them.
MIGRATION_V2 = {
    "README.md": "0-README.md",
    "challenge.md": "1-desk-research/brief.md",
    "_sources/market-research.md": "1-desk-research/market.md",
    "_sources/knowledge-base.md": "1-desk-research/knowledge.md",
    "who-to-talk-to.md": "2-profiling/profiles.md",
    "recruiting.md": "2-profiling/recruiting.md",
    "field-kit/guide.md": "3-guide/guide.md",
    "field-kit/checklist.md": "3-guide/process.md",
    "field-kit/observation.md": "4-field/0-observation-plan.md",
    "interviews/index.md": "4-field/0-index.md",
    "findings.md": "5-debrief/findings.md",
    "principles.md": "5-debrief/principles.md",
    "_system/state.yaml": "_engine/state.yaml",
    "_system/assumptions.md": "_engine/assumptions.md",
    "_system/decisions.md": "_engine/decisions.md",
    "_system/evidence-ledger.md": "_engine/evidence.md",
    "_system/budgets.yaml": "_engine/budgets.yaml",
    # Dissolved in v3, archived so nothing is lost. The cheatsheet's job is done
    # by the per-interview prep sheet; the modules' job by one guide per profile.
    "field-kit/cheatsheet.md": "_engine/sources/v2-cheatsheet.md",
    "field-kit/modules.md": "_engine/sources/v2-modules.md",
    "interviews/README.md": "_engine/sources/v2-interviews-readme.md",
    "interviews/notes/_notes-template.md": "_engine/sources/v2-notes-template.md",
}

# v1 path -> v2 path, so a v1 folder can be chained v1 -> v2 -> v3.
MIGRATION_V1 = {
    "interview-guides.md": "field-kit/guide.md",
    "field-checklist.md": "field-kit/checklist.md",
    "guide-context.md": "field-kit/observation.md",
    "users-and-sample.md": "who-to-talk-to.md",
    "recruitment.md": "recruiting.md",
    "synthesis.md": "principles.md",
    "state.yaml": "_system/state.yaml",
    "assumptions.md": "_system/assumptions.md",
    "decision-log.md": "_system/decisions.md",
    "knowledge-base.md": "_sources/knowledge-base.md",
    "market-research.md": "_sources/market-research.md",
    "interviews/evidence-ledger.md": "_system/evidence-ledger.md",
    "discovery-document.md": "_sources/discovery-document-v1.md",
}

# Raw field material: every v2 tray collapses into one.
RAW_TRAYS = ["interviews/incoming", "interviews/transcripts",
             "interviews/artifacts", "interviews/consent", "interviews/processed"]

# Rewrites inside a migrated state.yaml. Matched literally.
STATE_REWRITES = {
    "output: challenge.md": "file: 1-desk-research/brief.md",
    "output: _sources/market-research.md": "file: 1-desk-research/market.md",
    "output: _sources/knowledge-base.md": "file: 1-desk-research/knowledge.md",
    "output: who-to-talk-to.md": "file: 2-profiling/profiles.md",
    "output: recruiting.md": "file: 2-profiling/recruiting.md",
    "output: field-kit/guide.md + field-kit/cheatsheet.md + field-kit/modules.md":
        "file: 3-guide/guide.md",
    "output: field-kit/checklist.md": "file: 3-guide/process.md",
    "output: field-kit/observation.md": "file: 4-field/0-observation-plan.md",
    "output: interviews/index.md + _system/evidence-ledger.md + findings.md":
        "file: 4-field/0-index.md + 4-field/feedback/0-README.md + _engine/evidence.md",
    "output: principles.md": "file: 5-debrief/findings.md + 5-debrief/principles.md",
    "version: 2": "version: 3",
}


def detect_version(discovery: Path) -> int | None:
    """Which layout is this folder in? None if it is not a discovery folder.

    v1 keeps state.yaml at the root.
    v2 keeps it in _system/.
    v3 keeps it in _engine/.

    This replaces v2's looks_like_v1(), which answered a yes/no question and so
    could not tell a v2 folder from a fresh one: a v2 folder returned False, the
    init fell through to the create branch, and it planted the new layout beside
    the old one without a word.
    """
    if not discovery.exists():
        return None
    if (discovery / "_engine" / "state.yaml").exists():
        return 3
    if (discovery / "_system" / "state.yaml").exists():
        return 2
    if (discovery / "state.yaml").exists():
        return 1
    return None


def make_directories(discovery: Path) -> None:
    discovery.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (discovery / relative).mkdir(parents=True, exist_ok=True)


def stamp_state(path: Path, project_name: str, language: str, today: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace('created_at: ""', f'created_at: "{today}"')
    text = text.replace('updated_at: ""', f'updated_at: "{today}"')
    text = text.replace('project_name: ""', f'project_name: "{project_name}"')
    text = text.replace('language: ""', f'language: "{language}"')
    path.write_text(text, encoding="utf-8")


def copy_one(templates: Path, discovery: Path, template_name: str, relative: str,
             force: bool, overwrite_modified: bool) -> tuple[str, str]:
    """Copy one template. Returns (outcome, detail).

    --force only overwrites a file that is still byte-identical to its template,
    which means nobody has touched it. A file you edited, or that the assistant
    wrote in your language, is never clobbered without --overwrite-modified.
    This is the fix for the v2 foot-gun: running --force used to silently replace
    hand-translated Spanish files with the English templates.
    """
    source = templates / template_name
    if not source.exists():
        return "missing", template_name

    dest = discovery / relative
    if dest.exists():
        if not force and not overwrite_modified:
            return "kept", relative
        untouched = filecmp.cmp(source, dest, shallow=False)
        if not untouched and not overwrite_modified:
            return "protected", relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    return "created", relative


def install(templates: Path, discovery: Path, project_name: str, language: str,
            today: str, force: bool, overwrite_modified: bool) -> dict:
    results: dict[str, list[str]] = {}
    for template_name, relative in INSTALL.items():
        outcome, detail = copy_one(templates, discovery, template_name, relative,
                                   force, overwrite_modified)
        results.setdefault(outcome, []).append(detail)
        if outcome == "created" and relative == "_engine/state.yaml":
            stamp_state(discovery / relative, project_name, language, today)
    return results


# Two of state.yaml's steps are aggregates: their 'file' field lists more than
# one path, each one already a LAZY step of its own. --add on the aggregate
# name runs every concrete step it stands for, instead of failing with
# "Unknown step" and making the user go read state.yaml to find the real ones.
AGGREGATE_STEPS = {
    "interview_capture": ["field_index", "interview_feedback", "evidence"],
    "debrief": ["findings", "principles"],
    "validation_capture": ["validation_index", "evidence"],
}

# 'start', 'design_challenge' and 'plan' all write into
# 1-desk-research/brief.md, which is created at install, not via --add. There
# is nothing to materialise. 'plan' is not an error: its section is already in
# the installed brief, so asking for it exits 0 and says so.
INSTALLED_AT_INIT_STEPS = {"start", "design_challenge", "plan"}
PLAN_STEP = "plan"


def add_step(templates: Path, discovery: Path, step: str,
             force: bool, overwrite_modified: bool):
    """Materialise one step's file. Returns (outcome, detail).

    'aggregate' is a third outcome, on top of copy_one's four: detail is then
    a list of (sub_step, outcome, detail) tuples, one per concrete step run.
    'installed' is a fourth, for the step with nothing to create ('plan').
    """
    if step == PLAN_STEP:
        return "installed", ("the '## Plan' section already lives in the installed "
                             "1-desk-research/brief.md; nothing was created. Write it there "
                             "and in the 'plan:' block of _engine/state.yaml")
    if step in INSTALLED_AT_INIT_STEPS:
        raise SystemExit(
            f"'{step}' has no separate file to add: its output, "
            "1-desk-research/brief.md, is created at install, not via --add. "
            "Edit that file directly.")
    if step in AGGREGATE_STEPS:
        concrete = AGGREGATE_STEPS[step]
        results = [(sub, *add_step(templates, discovery, sub, force, overwrite_modified))
                   for sub in concrete]
        return "aggregate", results
    if step not in LAZY:
        known = ", ".join(sorted(LAZY))
        aggregates = ", ".join(f"{k} (runs {', '.join(v)})" for k, v in sorted(AGGREGATE_STEPS.items()))
        raise SystemExit(
            f"Unknown step '{step}'. Known steps: {known}. "
            f"Aggregate steps: {aggregates}.")
    template_name, relative = LAZY[step]
    return copy_one(templates, discovery, template_name, relative,
                    force, overwrite_modified)


def add_item(templates: Path, discovery: Path, item: str, name: str,
             force: bool, overwrite_modified: bool) -> tuple[str, str]:
    """Materialise one per-interview or per-observation file.

    Unlike a LAZY step, this one takes a name: INT-004-ana-lopez-acme,
    OBS-002-store-floor, VAL-001-ben-ito. The prefix has to match the kind of
    file: interview-* takes INT-, observation-* OBS-, validation-* VAL-. Never overwrites an existing file, same as --add
    on a LAZY step (copy_one's own force / overwrite_modified rules apply).
    """
    if item not in PER_ITEM_PATHS:
        known = ", ".join(sorted(PER_ITEM_PATHS))
        raise SystemExit(f"Unknown item '{item}'. Known items: {known}")
    if not BASE_NAME.match(name):
        raise SystemExit(
            f"'--name {name}' does not look like a base name. Expected "
            f"'{BASE_NAME.pattern}', for example INT-004-ana-lopez-acme, "
            "OBS-002-store-floor or VAL-001-ben-ito.")
    expected = ITEM_PREFIX[item.split("-")[0]]
    if not name.startswith(expected + "-"):
        raise SystemExit(
            f"'--add {item}' takes a name that starts with {expected}-, for example "
            f"{expected}-001-ana-lopez, and '--name {name}' does not. "
            "Interviews are INT-, observations OBS-, validation sessions VAL-.")
    template_name = PER_ITEM[item]
    relative = PER_ITEM_PATHS[item].format(name=name)
    return copy_one(templates, discovery, template_name, relative,
                    force, overwrite_modified)


def move(source: Path, dest: Path, moved: list, unrouted: list, label: str) -> None:
    if not source.exists():
        return
    if dest.exists():
        unrouted.append(f"{label} (destination {dest.name} already exists, left in place)")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))
    moved.append(f"{label} -> {dest}")


def migrate(discovery: Path, version: int) -> tuple[list, list]:
    """Move a v1 or v2 folder into the v3 layout. Nothing is deleted."""
    moved: list[str] = []
    unrouted: list[str] = []

    if version == 1:
        for old, new in MIGRATION_V1.items():
            move(discovery / old, discovery / new, moved, unrouted, f"v1 {old}")

    for old, new in MIGRATION_V2.items():
        move(discovery / old, discovery / new, moved, unrouted, old)

    # Interview notes become top-level field notes.
    notes_dir = discovery / "interviews" / "notes"
    if notes_dir.is_dir():
        for item in sorted(notes_dir.glob("*.md")):
            move(item, discovery / "4-field" / item.name, moved, unrouted,
                 f"interviews/notes/{item.name}")

    # Five raw trays collapse into one.
    for tray in RAW_TRAYS:
        tray_dir = discovery / tray
        if not tray_dir.is_dir():
            continue
        for item in sorted(tray_dir.iterdir()):
            if item.name == ".DS_Store":
                continue
            move(item, discovery / "4-field" / "_raw" / item.name, moved, unrouted,
                 f"{tray}/{item.name}")

    # Everything else under _sources/ is raw input material a human should be
    # able to see -- the market research and knowledge base above are already
    # gone from here by this point, moved by MIGRATION_V2. What is left is
    # client material (briefs, decks, canvases, spreadsheets, whiteboards),
    # so it goes to 1-desk-research/sources/, not to _engine/sources/, which
    # is reserved for the assistant's own working material.
    sources_dir = discovery / "_sources"
    if sources_dir.is_dir():
        for item in sorted(sources_dir.iterdir()):
            if item.name == ".DS_Store":
                continue
            move(item, discovery / "1-desk-research" / "sources" / item.name, moved, unrouted,
                 f"_sources/{item.name}")

    # Loose files at the root that nothing claimed.
    for item in sorted(discovery.glob("*.md")):
        if item.name in {"0-README.md"}:
            continue
        move(item, discovery / "_engine" / "sources" / "unrouted" / item.name,
             moved, unrouted, f"{item.name} (unclaimed)")

    state_path = discovery / "_engine" / "state.yaml"
    if state_path.exists():
        text = state_path.read_text(encoding="utf-8")
        for old, new in STATE_REWRITES.items():
            text = text.replace(old, new)
        state_path.write_text(text, encoding="utf-8")
        moved.append("_engine/state.yaml: step files repointed, version bumped to 3")
        unrouted.append(
            "_engine/state.yaml keeps its v2 step keys. The Guide maps them to the "
            "five phases on the next session; nothing is lost, but the phase numbers "
            "will look empty until then.")

    # Empty shells left behind.
    for shell in ["field-kit", "interviews", "_system", "_sources"]:
        shell_dir = discovery / shell
        if shell_dir.is_dir():
            leftovers = [p for p in shell_dir.rglob("*") if p.is_file() and p.name != ".DS_Store"]
            if leftovers:
                unrouted.append(f"{shell}/ still holds {len(leftovers)} file(s), route them by hand")
            else:
                unrouted.append(f"{shell}/ is empty now and unused in v3; remove it when you want")

    return moved, unrouted


# What a v3 folder made before the plan existed is missing: the summary lived in
# 5-debrief/output/, and state.yaml had no plan.
OLD_SUMMARY = "5-debrief/output/summary.md"
NEW_SUMMARY = "8-report/summary.md"
PLAN_MARKER = "# --- The plan"


def default_plan_block(templates: Path) -> str:
    """The plan block (with its comment) as shipped in templates/state.yaml."""
    text = (templates / "state.yaml").read_text(encoding="utf-8")
    start = text.find(PLAN_MARKER)
    if start == -1:
        raise SystemExit("templates/state.yaml has no plan block: the bundle is incomplete.")
    return text[start:]


def upgrade_v3(templates: Path, discovery: Path) -> tuple[list, list]:
    """Bring a v3 folder up to the layout with the plan and the report.

    Moves 5-debrief/output/summary.md to 8-report/summary.md, repoints it in
    state.yaml, and adds the default plan if state.yaml has none. Never deletes,
    never overwrites: if the destination exists, the source stays where it is
    and the report says so. Running it again changes nothing.
    """
    moved: list[str] = []
    unrouted: list[str] = []

    source = discovery / OLD_SUMMARY
    dest = discovery / NEW_SUMMARY
    conflict = source.exists() and dest.exists()
    if conflict:
        unrouted.append(f"{OLD_SUMMARY} was not moved: {NEW_SUMMARY} already exists. "
                        "Both are left as they are; merge them by hand.")
    elif source.exists():
        move(source, dest, moved, unrouted, OLD_SUMMARY)

    state_path = discovery / "_engine" / "state.yaml"
    if state_path.exists():
        text = state_path.read_text(encoding="utf-8")
        original = text
        # The path in state.yaml follows the new layout, whether or not the file
        # exists yet. The one exception is a conflict: both files exist, nothing
        # moved, so state.yaml is left alone for the user to decide.
        if not conflict and OLD_SUMMARY in text:
            text = text.replace(OLD_SUMMARY, NEW_SUMMARY)
            moved.append(f"_engine/state.yaml: {OLD_SUMMARY} repointed to {NEW_SUMMARY}")
        if not re.search(r"^plan:", text, re.M):
            text = text.rstrip("\n") + "\n\n" + default_plan_block(templates)
            moved.append("_engine/state.yaml: default plan added (a starting point: "
                         "the Guide proposes it and you approve it)")
        if text != original:
            state_path.write_text(text, encoding="utf-8")
    return moved, unrouted


def report(header: str, lines) -> None:
    if lines:
        print(f"\n{header}:")
        for line in lines:
            print(f"  {line}")


def resolve_folder(project_root: Path, folder: str | None) -> str:
    """Which folder holds the discovery.

    'discovery' unless the user names another. A project that already renamed
    its folder to 'discovery-<project>' keeps working without the flag: if
    exactly one such folder exists, that is the one. Two of them is ambiguous,
    and guessing would write into the wrong project.
    """
    if folder:
        return folder
    named = sorted(p.name for p in project_root.glob("discovery-*") if p.is_dir())
    if (project_root / "discovery").exists():
        named = ["discovery"] + named
    if len(named) == 1:
        return named[0]
    if len(named) > 1:
        raise SystemExit(f"More than one discovery folder here ({', '.join(named)}). "
                         "Say which one with --folder.")
    return "discovery"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize, extend or migrate an Empat.ia discovery folder.")
    parser.add_argument("--project-root", default=".", help="Project directory.")
    parser.add_argument("--method-root", default=None, help="Method bundle root.")
    parser.add_argument("--lang", default="en",
                        help="Working language for the project, e.g. en, es, pt. "
                             "The assistant writes every file in this language.")
    parser.add_argument("--folder", default=None,
                        help="Name of the discovery folder. Default 'discovery', or the one "
                             "'discovery-*' folder already in the project. Use 'discovery-<project>' "
                             "when one place holds more than one discovery.")
    parser.add_argument("--add", metavar="STEP",
                        help="Materialise one phase's file (run it when the step starts), or "
                             "one per-item file with --name: interview-note, interview-prep, "
                             "interview-feedback, observation-note, validation-note, "
                             "validation-prep, validation-feedback.")
    parser.add_argument("--name", default=None,
                        help="Base name for a per-item --add, e.g. INT-004-ana-lopez-acme, "
                             "OBS-002-store-floor or VAL-001-ben-ito (the prefix has to match "
                             "the type). Required when --add is a per-item type.")
    parser.add_argument("--project-name", default=None,
                        help="Project name stamped into state.yaml. Defaults to the project "
                             "root's folder name.")
    parser.add_argument("--migrate", action="store_true",
                        help="Move an existing v1 or v2 folder into the v3 layout, or bring a v3 "
                             "folder up to date (summary to 8-report/, default plan).")
    parser.add_argument("--force", action="store_true",
                        help="Re-copy templates over files nobody has touched. "
                             "Files you or the assistant edited are left alone.")
    parser.add_argument("--overwrite-modified", action="store_true",
                        help="DANGEROUS: also overwrite files that were edited, "
                             "including anything already written in your language.")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    method_root = (Path(args.method_root).expanduser().resolve() if args.method_root
                   else Path(__file__).resolve().parents[1])
    templates = method_root / "templates"
    discovery = project_root / resolve_folder(project_root, args.folder)

    if not templates.exists():
        raise SystemExit(f"Templates not found: {templates}")

    today = dt.date.today().isoformat()
    version = detect_version(discovery)

    # --- add one per-item file (interview note, prep sheet, feedback, ...) --
    if args.add and args.add in PER_ITEM_PATHS:
        if version != 3:
            raise SystemExit(
                f"{discovery} is not a v3 folder (detected: {version or 'nothing'}). "
                "Run --migrate first.")
        if not args.name:
            raise SystemExit(f"--add {args.add} takes a base name: pass --name "
                              "INT-004-ana-lopez-acme (or OBS-002-... for an observation).")
        outcome, detail = add_item(templates, discovery, args.add, args.name,
                                   args.force, args.overwrite_modified)
        print({"created": f"Created {detail}",
               "kept": f"Already there, kept as is: {detail}",
               "protected": f"Edited already, not overwritten: {detail}",
               "missing": f"Template missing from the bundle: {detail}"}[outcome])
        print("Now write it in the project's language, filled with what the project "
              "already knows. An empty template is not a finished step.")
        return 1 if outcome == "missing" else 0

    # --- add one step's file -------------------------------------------------
    if args.add:
        if version != 3:
            raise SystemExit(
                f"{discovery} is not a v3 folder (detected: {version or 'nothing'}). "
                "Run --migrate first.")
        outcome, detail = add_step(templates, discovery, args.add,
                                   args.force, args.overwrite_modified)
        if outcome == "aggregate":
            print(f"'{args.add}' is an aggregate step; ran each of its concrete steps:")
            missing_any = False
            for sub, sub_outcome, sub_detail in detail:
                label = {"created": "created", "kept": "kept as is",
                          "protected": "edited already, not overwritten",
                          "missing": "template missing"}[sub_outcome]
                print(f"  {sub}: {label} ({sub_detail})")
                missing_any = missing_any or sub_outcome == "missing"
            print("Now write each one in the project's language, filled with what the "
                  "project already knows. An empty template is not a finished step.")
            return 1 if missing_any else 0
        if outcome == "installed":
            print(f"Nothing to create: {detail}.")
            return 0
        print({"created": f"Created {detail}",
               "kept": f"Already there, kept as is: {detail}",
               "protected": f"Edited already, not overwritten: {detail}",
               "missing": f"Template missing from the bundle: {detail}"}[outcome])
        print("Now write it in the project's language, filled with what the project "
              "already knows. An empty template is not a finished step.")
        return 1 if outcome == "missing" else 0

    # --- migrate ------------------------------------------------------------
    if args.migrate:
        if version is None:
            raise SystemExit(f"Nothing to migrate: {discovery} is not a discovery folder.")
        if version == 3:
            moved, unrouted = upgrade_v3(templates, discovery)
            if not moved and not unrouted:
                print(f"{discovery} is already v3. Nothing to migrate.")
                return 0
            print(f"Brought the v3 folder at {discovery} up to date")
            report("Done", moved)
            report("Needs your eye", unrouted)
            print("\nNothing was deleted.")
            return 0
        make_directories(discovery)
        moved, unrouted = migrate(discovery, version)
        more_moved, more_unrouted = upgrade_v3(templates, discovery)
        moved += more_moved
        unrouted += more_unrouted
        print(f"Migrated v{version} -> v3 at {discovery}")
        report("Moved", moved)
        report("Needs your eye", unrouted)
        print("\nNothing was deleted. Check the list above before you remove anything.")
        return 0

    # --- create -------------------------------------------------------------
    if version is not None and version != 3:
        raise SystemExit(
            f"{discovery} is a v{version} folder. Run again with --migrate to move it "
            f"to v3. Creating on top of it would leave two layouts side by side.")

    make_directories(discovery)
    results = install(templates, discovery, args.project_name or project_root.name, args.lang,
                      today, args.force, args.overwrite_modified)

    print(f"Discovery ready at {discovery}")
    report("Created", results.get("created"))
    report("Kept as is", results.get("kept"))
    report("Edited already, not overwritten", results.get("protected"))
    report("Missing templates (the bundle is incomplete)", results.get("missing"))

    print(f"\nSix files, and only two are yours: 0-README.md and "
          f"1-desk-research/brief.md.")
    print(f"Everything else is born when you enter its phase. Write all of it in "
          f"'{args.lang}'.")
    return 1 if results.get("missing") else 0


if __name__ == "__main__":
    raise SystemExit(main())
