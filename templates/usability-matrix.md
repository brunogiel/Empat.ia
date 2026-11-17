# Usability matrix

Owns: the grid of what each person did on each task or component, how far they got and why a cell failed. Does not own: the findings and what to change → `7-validation/findings.md`; the atomic evidence → `_engine/evidence.md`.

Optional (step 7c), and often the piece the client opens first: one glance shows where people
got through and where they did not. It is a map to the findings, not a replacement for them.

Rows are the tasks of `7-validation/tasks.md`, or the components of the prototype (a header,
a form, a filter) when one task crosses several. Columns are the people. Every cell is one of:

- `alone`: nobody pointed the way.
- `guided`: the moderator gave a hint or an answer first.
- `induced`: the idea or the word came from the moderator. A lead, never a "worked".
- `failed`: the person did not get through. A `failed` cell always carries a **cause**.
- `not reached`: the session ended first, or the task was skipped. Not a failure.

## The grid

| Task or component | VAL-001 | VAL-002 | VAL-003 | Seen in video |
|---|---|---|---|---|
| Pending | Pending | Pending | Pending | N of N rows seen |

## Cause of each failure

A failure is not a finding until its cause is known. `prototype`: the prototype broke (a bug,
a broken link, a screen that was not ready, a missing test account). `design`: the prototype
worked and the person could not understand or find it. `undetermined`: the video and the
transcript do not say. **A `prototype` failure does not count toward "X of N" and is not a
finding about the person.** It goes to the team as a fix. `undetermined` counts only as a lead.

| Cell | Cause | Evidence | What shows it | Next step |
|---|---|---|---|---|
| Pending | prototype / design / undetermined | VAL-001-02 | Pending *(the click, the error, the quote)* | Pending |

## Provisional reading by component (optional)

When the designer needs something before the analysis is done. One line per component, marked
**provisional**: written from the cells above, before the quotes were checked and before the
seeded checker and the devil's advocate ran. It does not leave the team as a finding.

| Component | Provisional reading | Sessions behind it | Alone / guided / induced |
|---|---|---|---|
| Pending | Pending | Pending | Pending |

## How it feeds the findings

- Count a cell once per person. "Alone" in the title of a finding needs its cell to say `alone`.
- Two people or fewer: say what each did. The grid does not turn that into a result.
- When a cell changes after the checks, change it here first and then in `findings.md`.
