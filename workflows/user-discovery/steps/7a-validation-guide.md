# 7a, Validation guide

## Objective

Build the task script for putting a prototype in front of people: what you ask
them to do, what you watch for, and what counts as stuck. Validation looks at what
people do, not at what they say.

Empat.ia guides the validation. It does not build the prototype.

## Method notes

- **Bring the client's goal down to a behaviour you can watch.** "Make the page convert better" is not a task. Name one call to action or one concrete action in the prototype per goal (press this, send that, choose between these), and say what it looks like when a person does it. A goal with two behaviours (reach someone who is not looking yet, and help someone who is looking finish fast) gets one action each. A goal nobody can observe is not tested; it is written down as not tested.
- Give a situation, never the steps. Say nothing about how.
- Watch what they do first; ask why after.
- **The real case comes first, the prototype second.** Before the prototype is shown, ask for the last time the person did the thing today, and write it down. It is what you compare their behaviour on the prototype with. Never measure declared intent ("would you sign up?", "which channel do you prefer?"): ask what they did, and watch what they do.
- **Enter where people really enter.** Start the task from the place the person comes from in real life (a link, a search, a message), not from the page the team wishes they started on.
- One task tests one bet from the ideation.
- Use the same kind of people as the field, so the two rounds can be compared.
- Don't lead: do not name the feature before they find it.

## First, the file of this step

The file this step writes does not exist yet, and neither does its folder. That is
the design: `7-validation/` is born with this step.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add validation_guide`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/7-validation/tasks.md`
- `discovery/6-ideation/concepts.md`
- `discovery/_engine/assumptions.md`
- `discovery/_engine/decisions.md`
- `discovery/_engine/state.yaml`

## Optional, 7a.0: the menu of exercises

Use it when there are more good exercises than minutes. The point is to separate two
jobs that usually get mixed: thinking of exercises, and choosing among them.

1. **[LATENT]** Create the menu: `python3 <method-root>/scripts/init_project.py --project-root . --add exercise_menu`. Set the session length and the reserve (consent, welcome, closing).
2. **[LATENT] Diverge with unlimited time and people.** Write every exercise worth considering, as a situation, each with the bet it tests and its minutes. Ask several people with different eyes (an expert of the trade, someone from the audience's side) for the exercises they would run, each alone and before seeing yours. This is a session of proposals only, separate from the blind review in step 8 (`agents/council.md`: never mix the two modes in one session). What two or more propose independently goes in the last column. Merge duplicates; do not judge yet.
3. **[DET] The researcher chooses on a page.** `python3 <method-root>/scripts/build_menu.py 7-validation/exercise-menu.md` writes a page with `go`, `maybe` and `no` on every row and the running sum of minutes against the session. The assistant never picks for the researcher. `--apply` writes the choices back into the table.
4. **[LATENT]** Write the script from the `go` rows. Say in `_engine/decisions.md` which bet lost its exercise because of the cut.

Skipping 7a.0 is fine when the script has a handful of obvious tasks.

## Order and contamination

In a session where the same person does several tasks, an earlier task changes the later
ones. Decide the order with this table, and write the order and the reason in `tasks.md`.

| If this comes first | It changes the next task like this | So |
|---|---|---|
| A task that shows a version of a page | The second version is judged against the first, not on its own | Only the first pass is cold. Run the second as a comparison and mark it so |
| A task that names a feature or a word | Anyone who learned it will find it faster later | Tasks that need discovery come before any task that names it |
| The same content in two layouts | The person learns the content and not the layout | Use twin content for the second layout |
| A task where the moderator helped | The hint carries into every later task | Mark it `guided`; plan the next task so the hint does not apply |
| A question about what they would prefer | They answer the next task to be consistent | Preference questions go after all the tasks |
| Seeing two options side by side | The cold reading is gone | Side by side is the last thing the person sees |

When the cost of a comparison inside the same person is too high, split it across
people instead and say so in `decisions.md`.

## Process

1. **[LATENT]** Take the bets from `6-ideation/concepts.md`, whoever did the ideation.
   If the file has no bets table, write it first, with the client's goal for the round
   brought down to behaviours (see the method notes).
2. **[LATENT]** Write one task per bet, as a situation. For each: what to watch for,
   when it is done, and what a stuck person looks like.
3. **[DET]** Keep it inside 100 lines. This is a hard budget, like the master guide.
4. **[LATENT]** More than one profile? One whole script per profile, never deltas.
5. **[LATENT]** Set `validations.target` in `_engine/state.yaml`.
6. **[LATENT] Order the tasks** with the contamination table, and write the order and why in `tasks.md`.
7. **[LATENT] Keep the bets able to conclude.** If the design of the validation changes at any point (a comparison is dropped, a task is cut, a profile is left out, the number of sessions shrinks), rewrite the affected bets in `6-ideation/concepts.md` **in the same change**. Each rewritten bet says what result confirms it and what drops it with the design that remains. A bet that the new design cannot confirm or drop is marked `not tested` in the table, not left as it was. Log the change in `_engine/decisions.md`.
8. **[LATENT] Blind review.** Before the script goes to the field, run a **blind panel** (`agents/council.md`, review mode): each reviewer reads the script alone, never sees another reviewer's opinion, and receives the closed decisions of `_engine/decisions.md`. Look for tasks that give the steps, tasks that name the feature, and bets with no task. If a model does any of this, it is a model checker: plant a few leading tasks in a copy first (see "Every model checker" in `5a-debrief.md`).

## Quality criteria

- A person who is not you can run a session from the script and its prep sheet.
- Every task tests a named bet, and every bet says what confirms it and what drops it.
- Every goal of the client is a behaviour someone can watch, or is written down as not tested.
- The order of the tasks has a reason, taken from the contamination table.
- No task contains the steps.

## What does NOT go here

| If you wrote it in the tasks | It belongs in |
|---|---|
| The concept and why it was chosen | `6-ideation/concepts.md` |
| The long list of exercises and the cut | `7-validation/exercise-menu.md` |
| The assumptions being tested | `_engine/assumptions.md`, and the tasks link to them |
| Recruiting, scheduling, incentives | `2-profiling/recruiting.md` |
| Version history of the script | `_engine/sources/guide-versions/` |

## Gate

Suggested action:

- `Advance` if every task tests a bet and nobody needs the steps.
- `Deepen` if bets are missing a task.
- `Question` if a task leads the person.
- `Council` if the prototype could be read as the answer to a different question.
