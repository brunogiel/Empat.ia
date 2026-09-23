#!/usr/bin/env python3
"""Initialize (or migrate) the discovery folder for Empat.ia.

The discovery folder has three zones:

  zone 1  the files you open            discovery/*.md, discovery/field-kit/
  zone 2  the assistant's workspace     discovery/_system/
  zone 3  raw and long material         discovery/_sources/

Field material keeps its own folder: discovery/interviews/.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path


# template filename -> destination path inside discovery/
LAYOUT = {
    "discovery-readme.md": "README.md",
    "challenge.md": "challenge.md",
    "who-to-talk-to.md": "who-to-talk-to.md",
    "recruiting.md": "recruiting.md",
    "findings.md": "findings.md",
    "principles.md": "principles.md",
    "field-kit-cheatsheet.md": "field-kit/cheatsheet.md",
    "field-kit-guide.md": "field-kit/guide.md",
    "field-kit-modules.md": "field-kit/modules.md",
    "field-kit-checklist.md": "field-kit/checklist.md",
    "field-kit-observation.md": "field-kit/observation.md",
    "state.yaml": "_system/state.yaml",
    "assumptions.md": "_system/assumptions.md",
    "decisions.md": "_system/decisions.md",
    "evidence-ledger.md": "_system/evidence-ledger.md",
    "budgets.yaml": "_system/budgets.yaml",
    "market-research.md": "_sources/market-research.md",
    "knowledge-base.md": "_sources/knowledge-base.md",
    "interviews-readme.md": "interviews/README.md",
    "interview-index.md": "interviews/index.md",
    "interview-note-template.md": "interviews/notes/_notes-template.md",
}

DIRECTORIES = [
    "field-kit",
    "_system",
    "_sources",
    "_sources/councils",
    "_sources/data-reviews",
    "_sources/guide-versions",
    "interviews",
    "interviews/incoming",
    "interviews/transcripts",
    "interviews/notes",
    "interviews/artifacts",
    "interviews/consent",
    "interviews/processed",
]

# v1 path -> v2 path. Migration moves files, it never deletes them.
MIGRATION = {
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
    # discovery-document.md is dissolved: its summary belongs in challenge.md and
    # its state in _system/state.yaml. We archive it so nothing is lost.
    "discovery-document.md": "_sources/discovery-document-v1.md",
}

# Paths a v1 state.yaml points at, rewritten to their v2 home.
STATE_PATH_REWRITES = {
    "output: discovery-document.md": "output: challenge.md",
    "output: market-research.md": "output: _sources/market-research.md",
    "output: knowledge-base.md": "output: _sources/knowledge-base.md",
    "output: users-and-sample.md": "output: who-to-talk-to.md",
    "output: interview-guides.md": "output: field-kit/guide.md",
    "output: recruitment.md": "output: recruiting.md",
    "output: field-checklist.md": "output: field-kit/checklist.md",
    "output: guide-context.md": "output: field-kit/observation.md",
    "output: synthesis.md": "output: principles.md",
    "output: interviews/index.md + interviews/evidence-ledger.md":
        "output: interviews/index.md + _system/evidence-ledger.md",
}


def looks_like_v1(discovery_dir: Path) -> bool:
    """A v1 folder keeps state.yaml at the root; v2 keeps it in _system/."""
    return (discovery_dir / "state.yaml").exists() and not (discovery_dir / "_system").exists()


def make_directories(discovery_dir: Path) -> None:
    discovery_dir.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (discovery_dir / relative).mkdir(parents=True, exist_ok=True)


def stamp_state(path: Path, project_name: str, language: str, today: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace('created_at: ""', f'created_at: "{today}"')
    text = text.replace('updated_at: ""', f'updated_at: "{today}"')
    text = text.replace('project_name: ""', f'project_name: "{project_name}"')
    text = text.replace('language: ""', f'language: "{language}"')
    path.write_text(text, encoding="utf-8")


def copy_templates(templates_dir: Path, discovery_dir: Path, force: bool,
                   project_name: str, language: str, today: str) -> tuple[list, list, list]:
    created, skipped, missing = [], [], []
    for template_name, relative in LAYOUT.items():
        src = templates_dir / template_name
        if not src.exists():
            missing.append(template_name)
            continue
        dest = discovery_dir / relative
        if dest.exists() and not force:
            skipped.append(relative)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        if relative == "_system/state.yaml":
            stamp_state(dest, project_name, language, today)
        created.append(relative)
    return created, skipped, missing


def add_missing_state_keys(text: str, language: str) -> str:
    """A v1 state file has no version, language, editor or field signal. Add what is missing."""
    if "\nversion:" not in text:
        text = text.replace("method: design-empathy-ai",
                            "method: design-empathy-ai\nversion: 2", 1)
    if "\nlanguage:" not in text:
        text = text.replace("guide: guide",
                            f'# Working language for every document in discovery/.\n'
                            f'language: "{language}"\nguide: guide', 1)
    if "\neditor:" not in text:
        text = text.replace("steps:",
                            "# The editor runs at every gate: it distills, routes misplaced content\n"
                            "# and trims by the budgets in budgets.yaml. It never deletes.\n"
                            "editor: on\nsteps:", 1)
    if "stale_after_days" not in text and "interviews:" in text:
        text = text.rstrip("\n") + (
            "\n  # Field signal. From step 07 on, if 'done' is still 0 and more than\n"
            "  # 'stale_after_days' have passed since created_at, the Guide says so first.\n"
            "  stale_after_days: 7\n")
    return text


def migrate(discovery_dir: Path, language: str) -> tuple[list, list]:
    """Move a v1 folder into the three-zone layout. Nothing is deleted."""
    moved, unrouted = [], []

    for old_relative, new_relative in MIGRATION.items():
        source = discovery_dir / old_relative
        if not source.exists():
            continue
        destination = discovery_dir / new_relative
        if destination.exists():
            unrouted.append(f"{old_relative} (destination {new_relative} already exists)")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved.append(f"{old_relative} -> {new_relative}")

    # Files the user added on their own, routed by name.
    for item in sorted(discovery_dir.glob("*.md")):
        if item.name in {"README.md", "challenge.md", "who-to-talk-to.md",
                         "recruiting.md", "findings.md", "principles.md"}:
            continue
        lowered = item.name.lower()
        if "council" in lowered:
            target = discovery_dir / "_sources" / "councils" / item.name
        elif "review" in lowered or "analytics" in lowered or "posthog" in lowered:
            target = discovery_dir / "_sources" / "data-reviews" / item.name
        else:
            unrouted.append(f"{item.name} (left in place, route it by hand)")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            unrouted.append(f"{item.name} (destination already exists)")
            continue
        shutil.move(str(item), str(target))
        moved.append(f"{item.name} -> {target.relative_to(discovery_dir)}")

    # inputs/ is gone in v2: interviews/incoming/ and _sources/ cover it.
    inputs_dir = discovery_dir / "inputs"
    if inputs_dir.is_dir():
        leftovers = [p for p in inputs_dir.iterdir() if p.name != ".DS_Store"]
        if leftovers:
            for item in leftovers:
                shutil.move(str(item), str(discovery_dir / "_sources" / item.name))
                moved.append(f"inputs/{item.name} -> _sources/{item.name}")
        unrouted.append("inputs/ is empty now and unused in v2; remove it when you want")

    state_path = discovery_dir / "_system" / "state.yaml"
    if state_path.exists():
        text = state_path.read_text(encoding="utf-8")
        for old, new in STATE_PATH_REWRITES.items():
            text = text.replace(old, new)
        text = add_missing_state_keys(text, language)
        state_path.write_text(text, encoding="utf-8")
        moved.append("_system/state.yaml: step outputs repointed, v2 keys added")

    return moved, unrouted


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or migrate an Empat.ia discovery folder.")
    parser.add_argument("--project-root", default=".", help="Project directory to initialize.")
    parser.add_argument("--method-root", default=None, help="Method bundle root. Defaults to script parent/..")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--lang", default="en", help="Working language for the project, e.g. en, es, pt.")
    parser.add_argument("--migrate", action="store_true",
                        help="Move an existing v1 discovery folder into the three-zone layout.")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    method_root = Path(args.method_root).expanduser().resolve() if args.method_root else Path(__file__).resolve().parents[1]
    templates_dir = method_root / "templates"
    discovery_dir = project_root / "discovery"

    if not templates_dir.exists():
        raise SystemExit(f"Templates not found: {templates_dir}")

    today = dt.date.today().isoformat()
    moved, unrouted = [], []

    if args.migrate:
        if not discovery_dir.exists():
            raise SystemExit(f"Nothing to migrate: {discovery_dir} does not exist.")
        if not looks_like_v1(discovery_dir):
            print(f"{discovery_dir} is not a v1 folder. Nothing to migrate.")
        else:
            make_directories(discovery_dir)
            moved, unrouted = migrate(discovery_dir, args.lang)
    else:
        if looks_like_v1(discovery_dir):
            raise SystemExit(
                f"{discovery_dir} looks like a v1 folder. Run again with --migrate to move it to v2."
            )
        make_directories(discovery_dir)

    created, skipped, missing = copy_templates(
        templates_dir, discovery_dir, args.force, project_root.name, args.lang, today
    )

    print(f"Discovery ready at {discovery_dir}")
    if moved:
        print("\nMoved:")
        for line in moved:
            print(f"  {line}")
    if created:
        print("\nCreated:")
        for line in created:
            print(f"  {line}")
    if skipped:
        print("\nKept as is: " + ", ".join(skipped))
    if unrouted:
        print("\nNeeds your eye:")
        for line in unrouted:
            print(f"  {line}")
    if missing:
        print("\nMissing templates (the method bundle is incomplete): " + ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
