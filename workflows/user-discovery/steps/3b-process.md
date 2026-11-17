# 3b, Field process

## Objective

Prepare a protocol for before, during, and after interviewing.

## Method notes

- Ask for consent.
- Protect privacy.
- Use recording or an AI notetaker if you can. Arm the recording from the account of whoever keeps the material (`2b`), and always record a session on a screen.
- Never cut off what the interviewee is saying.
- Everything the user says is evidence of their perspective; don't argue with it during the interview.
- The prep sheet of each session is made from the master guide, never retyped: `python3 <method-root>/scripts/export_guide.py --project-root . --prep <INT-00X-name>` (see `3a-guide.md`). Make it the day before, after the last edit of the master.

## First, the file of this step

The file this step writes does not exist yet. That is the design: a step's file is
born when the step starts, never at install.

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

This step has no gate (`gate: false` in `state.yaml`): the guide's gate in 3a closes phase 3.
Suggested action when you close it:

- `Advance` if the team can interview without improvising.
- `Deepen` if tools or consent are missing.
- `Question` if there is ethical risk.
