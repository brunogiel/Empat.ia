# 3b, Field process

## Objective

Prepare a protocol for before, during, and after interviewing.

## Method notes

- Ask for consent.
- Protect privacy.
- Use recording or an AI notetaker if you can.
- Never cut off what the interviewee is saying.
- Everything the user says is evidence of their perspective; don't argue with it during the interview.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add field_process`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/3-guide/process.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/decisions.md`

## Quality checklist

- Before.
- During.
- After.
- Mistakes to avoid.
- File naming convention.
- Consent and privacy policy.
- Context plan, if applicable.
- Permissions for photos, recordings, and materials.

## Gate

Suggested action:

- `Advance` if the team can interview without improvising.
- `Deepen` if tools or consent are missing.
- `Question` if there is ethical risk.
