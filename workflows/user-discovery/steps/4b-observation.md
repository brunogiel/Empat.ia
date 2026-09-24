# 4b, Observation

Optional. `gate: false`. A project that only interviews never opens this step.

In v2 this content had no step file of its own: `state.yaml` declared eleven
steps against ten files, and `guide_context` lived buried inside the field
checklist. It also sat in the field kit, as if it were preparation for the
guide. It is not. Observation is fieldwork: you go somewhere and watch.

## Objective

Learn what interviews cannot tell you, because people do not narrate what they
have stopped noticing.

## When it applies

- The problem happens in a specific place, process or tool.
- What people say and what they do are likely to diverge.
- There is material to collect: forms, screens, spreadsheets, workarounds taped
  to a wall.

Skip it when the behaviour is not observable, or when access would cost more
than it returns.

## Method notes

Pick what the case needs: contextual observation, shadowing, immersion, an
expert conversation, or analogous inspiration from a different industry that
solved a similar friction.

Experts add context. They do not replace users, and their opinion is not
evidence about a user.

## Documents to touch

- `4-field/0-observation-plan.md`: where to go, who to see, when, what to look for.
- `4-field/OBS-00X-<place>.md`: one note per outing.
- `4-field/0-index.md`: register the outing like an interview.
- `_engine/evidence.md`: its evidence, with `OBS-` IDs.

## Flow

1. **[DET]** Create the plan with
   `init_project.py --project-root . --add observation`, then write it in the
   project's language.
2. **[LATENT]** Decide where, who, when, and what you are going to look for.
   A plan without a question is tourism.
3. **[DET]** Ask for permissions before, not after: photos, recordings,
   materials.
4. **[LATENT]** Go. Describe what happened before interpreting it.
5. **[DET]** Write `OBS-00X-<place>.md` within 24 hours, same rule as an
   interview.
6. **[DET]** Extract evidence into `_engine/evidence.md` with `OBS-` IDs, so it
   crosses with interview evidence in phase 5.

## Quality checklist

- [ ] Description is separated from interpretation.
- [ ] Contradictions with what people said in interviews are written down, not smoothed over.
- [ ] Permissions are on file for every material collected.
- [ ] The evidence traces to an `OBS-` ID and a moment.

## Gate

No gate. It informs phases 4 and 5 and never blocks them.
