# discovery/ — for the assistant

This folder is a user discovery project running the **Empat.ia** method. Read
this before touching anything in it.

**State.** `_engine/state.yaml` is the only place the project state lives.
Never repeat it in another document. Read it first; it tells you the current
phase, the current step and its status.

**Language.** Write every file in the language set in `state.yaml` under
`language:`. The method's repository is in English; this folder is not.

**The folder grows.** Files are born when the user enters their phase, from the
method's templates, and you write them filled with what the project already
knows. A file that does not exist yet is not missing — it belongs to a phase the
user has not reached. Create one with
`python3 <method-root>/scripts/init_project.py --project-root . --add <step>`,
then write it. The step names are the keys under `steps:` in `state.yaml`.

**The five phases.** `1-desk-research/` · `2-profiling/` · `3-guide/` ·
`4-field/` · `5-debrief/`. The deliverable is `5-debrief/principles.md`.

**Do not edit `_engine/` by hand** beyond `state.yaml`, and do not rewrite
`3-guide/guide.md` during fieldwork: it is the master guide, reused across every
interview. Propose edits, apply them only when the user says so.

**Project-level skills belong in `_engine/skills/`.** If this project needs its
own wrapper skill (for example, one that fetches transcripts from the team's
recorder), it lives there, not in a numbered phase folder: it is yours, not
the human's.

**Budgets.** `_engine/budgets.yaml` caps the files the user opens.
`3-guide/guide.md` is a hard cap.

**The full method** lives in the Empat.ia bundle: its `SKILL.md`, its
`workflows/user-discovery/steps/`, and its `references/`. If you cannot find
it, ask the user where they installed it, or fetch
`https://github.com/brunogiel/Empat.ia`.
