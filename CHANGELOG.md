# Changelog

## 2.0.0 - 2026-09-23

Breaking. The `discovery/` folder is reorganized into three zones. Existing projects migrate with
`python3 scripts/init_project.py --project-root <path> --migrate --lang <lang>`, which moves files
and never deletes them.

### Why

The first external run of the method produced a 257-line interview guide: it had absorbed the field
checklists, the recruiting logistics, the coding definitions and the assumption IDs, while the files
that own that content stayed empty. The guide was unusable in the room it was written for. Nothing
in the method routed the overflow or capped the growth.

### Added

- `field-kit/cheatsheet.md`. One page, hard budget, what the interviewer holds during the interview.
- `field-kit/modules.md`. Per-profile variants as deltas against the base guide.
- `findings.md`. The distilled layer between atomic evidence and design principles.
- `_system/budgets.yaml`. A line budget per zone 1 file.
- `agents/editor.md`. Runs at every gate: distills, routes misplaced content, trims by budget.
  It shows its plan, waits for an OK, and never deletes.
- A canonical path and an application ledger for council output. A council can return thirteen
  recommendations and have twelve applied; the ledger keeps the missing one visible.
- `language` in `state.yaml` and `--lang` on init. The scaffolding is written in the project's
  language, not only the conversation.
- A field signal in `state.yaml`: from stage 07 on, zero interviews past `stale_after_days` is
  reported before anything else.
- `VERSION` and this changelog.

### Changed

- `discovery-document.md` is dissolved. Its summary moved to `challenge.md`, its index to
  `README.md`, its state to `_system/state.yaml`. State now lives in exactly one place.
- Renamed for clarity: `users-and-sample.md` to `who-to-talk-to.md`, `recruitment.md` to
  `recruiting.md`, `synthesis.md` to `principles.md`, `decision-log.md` to `decisions.md`,
  `interview-guides.md` to `field-kit/guide.md`, `field-checklist.md` to `field-kit/checklist.md`,
  `guide-context.md` to `field-kit/observation.md`.
- `evidence-ledger.md` moved from `interviews/` to `_system/`.
- Stage 06 gained a "What does NOT go here" routing table, a rule about renumbering reordered
  blocks, and gate questions about misplaced content.

### Fixed

- `SKILL.md` referenced `_template-notes.md`; the file has always been `_notes-template.md`.
- `inputs/` was created and documented nowhere. Removed; `interviews/incoming/` and `_sources/` cover it.
