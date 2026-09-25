#!/usr/bin/env python3
"""Initialize, extend or migrate the discovery folder for Empat.ia.

The folder is numbered by phase, and it grows as you go:

  0-README.md        the map
  1-desk-research/   what you research before talking to anyone
  2-profiling/       who you talk to and how you reach them
  3-guide/           the instrument you take to the field
  4-field/           interviews and observation
  5-debrief/         findings, principles, and what you hand to someone else
  _engine/           state, assumptions, decisions, evidence, raw sources

Only six files exist at install. Every other file is born when you ENTER its
phase, written in the project's language. A file that does not exist yet is the
design, not a missing piece.

Three commands:

  (default)   create a new discovery/ folder
  --add STEP  materialise one phase's file from its template
  --migrate   move a v1 or v2 folder into the v3 layout, without losing anything
"""

from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import shutil
from pathlib import Path


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
    "interview_feedback": ("interview-feedback.md", "4-field/0-interview-feedback.md"),
    "observation": ("observation-plan.md", "4-field/0-observation-plan.md"),
    "evidence": ("evidence.md", "_engine/evidence.md"),
    "assumptions": ("assumptions.md", "_engine/assumptions.md"),
    "decisions": ("decisions.md", "_engine/decisions.md"),
    "findings": ("findings.md", "5-debrief/findings.md"),
    "principles": ("principles.md", "5-debrief/principles.md"),
    "summary": ("summary.md", "5-debrief/output/summary.md"),
    "synthesis_log": ("synthesis-log.md", "_engine/synthesis-log.md"),
}

# Per-item templates the assistant copies once per interview or observation.
# They take a name, so they are not in LAZY.
PER_ITEM = {
    "interview-note": "interview-note.md",
    "interview-prep": "interview-prep.md",
    "observation-note": "observation-note.md",
    "notes": "notes.md",
}

DIRECTORIES = [
    "1-desk-research",
    "2-profiling",
    "3-guide",
    "4-field",
    "4-field/_prep",
    "4-field/_raw",
    "5-debrief",
    "5-debrief/output",
    "_engine",
    "_engine/sources",
    "_engine/sources/councils",
    "_engine/sources/data-reviews",
    "_engine/sources/guide-versions",
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
        "file: 4-field/0-index.md + 4-field/0-interview-feedback.md + _engine/evidence.md",
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


def add_step(templates: Path, discovery: Path, step: str,
             force: bool, overwrite_modified: bool) -> tuple[str, str]:
    if step not in LAZY:
        known = ", ".join(sorted(LAZY))
        raise SystemExit(f"Unknown step '{step}'. Known steps: {known}")
    template_name, relative = LAZY[step]
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

    # Everything else under _sources/ keeps its shape one level down.
    sources_dir = discovery / "_sources"
    if sources_dir.is_dir():
        for item in sorted(sources_dir.iterdir()):
            if item.name == ".DS_Store":
                continue
            move(item, discovery / "_engine" / "sources" / item.name, moved, unrouted,
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
    if (project_root / "discovery").exists():
        return "discovery"
    named = sorted(p.name for p in project_root.glob("discovery-*") if p.is_dir())
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
                        help="Materialise one phase's file. Run it when the step starts.")
    parser.add_argument("--migrate", action="store_true",
                        help="Move an existing v1 or v2 folder into the v3 layout.")
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

    # --- add one step's file ------------------------------------------------
    if args.add:
        if version != 3:
            raise SystemExit(
                f"{discovery} is not a v3 folder (detected: {version or 'nothing'}). "
                "Run --migrate first.")
        outcome, detail = add_step(templates, discovery, args.add,
                                   args.force, args.overwrite_modified)
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
            print(f"{discovery} is already v3. Nothing to migrate.")
            return 0
        make_directories(discovery)
        moved, unrouted = migrate(discovery, version)
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
    results = install(templates, discovery, project_root.name, args.lang, today,
                      args.force, args.overwrite_modified)

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
