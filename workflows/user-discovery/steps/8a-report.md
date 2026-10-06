# 8a, Report

## Objective

Write the final report of the whole project, on one page, for someone who read
none of it. Every plan closes with it, whatever pieces it used.

## Method notes

- It covers every round that ran: the field and, when there was one, the
  ideation and the validation.
- It is a shorter view of material that already exists. It adds no new claim.
- It is the only shareable artefact of the method: no raw quotes without consent,
  no internal notes, no project logistics.
- A skipped piece gets one line: what we assume by not doing it.
- A piece done by someone else gets a link to their result.

## First, the file of this step

The file this step writes does not exist yet, and neither does its folder. That is
the design: `8-report/` is born with this step.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add report`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Older projects

A project made before this piece existed may hold its summary in
`5-debrief/output/summary.md`. Run
`python3 <method-root>/scripts/init_project.py --project-root . --migrate`:
it moves the file to `8-report/summary.md` and never overwrites a file that is
already there.

## Documents to touch

- `discovery/8-report/summary.md`
- `discovery/5-debrief/principles.md`
- `discovery/5-debrief/findings.md`
- `discovery/7-validation/findings.md` (if validation ran)
- `discovery/6-ideation/concepts.md` (if ideation ran)
- `discovery/1-desk-research/brief.md` (the plan)
- `discovery/_engine/state.yaml`

## Process

1. Read the plan in the brief: which pieces ran, which were skipped, which were external.
2. Fill the page from the pieces that ran. Link the external ones.
3. Check every quote against its consent.
4. Check the page fits its budget in `_engine/budgets.yaml`.
5. Mark the `report` piece `done` in the plan.

## Quality criteria

- Someone who read nothing else can say what was found and what happens next.
- Nothing in it is missing from the sources it summarises.
- No quote lacks consent.

## Gate

Suggested action:

- `Advance` if the page is complete and every claim traces to a source file.
- `Deepen` if a piece that ran is missing from the page.
- `Question` if the page says more than the evidence does.
- `Council` if the report will inform a decision that is hard to reverse.
