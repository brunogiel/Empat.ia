# Exercise menu

Owns: the long list of possible exercises for a validation session and which ones were chosen. Does not own: the script that comes out of it → `7-validation/tasks.md`; the bets the exercises test → `6-ideation/concepts.md`.

Optional (step 7a.0). Write it before the script, when the session has more candidate
exercises than minutes. Assume unlimited time and unlimited people: list every exercise
worth considering, then cut. The cut is the researcher's, made on a page of buttons
(`scripts/build_menu.py`), never the assistant's.

Session length: Pending minutes
Reserve: Pending minutes *(consent, welcome and closing; the page subtracts it)*

Keep the table header as it is: the script reads it. One row per exercise. `Minutes` is a
number (a range counts at its upper end). Leave `Choice` empty; the page fills it with
`go`, `maybe` or `no`.

| ID | Exercise | Bet | Minutes | Where it comes from | Choice |
|---|---|---|---|---|---|
| E-01 | Pending *(a situation, never the steps)* | B-1 | 5 | the researcher / a panel reviewer / the client | |
| E-02 | Pending | B-1 | 8 | Pending | |
| E-03 | Pending | B-2 | 10 | Pending | |

## How to use it

1. Fill the table. Mix your own ideas with those of a **blind panel** (`agents/council.md`):
   reviewers who have not seen your idea propose exercises on their own. What several of
   them propose independently is the signal; write that in the last column.
2. Build the page: `python3 <method-root>/scripts/build_menu.py 7-validation/exercise-menu.md`.
   Open it, press `go` / `maybe` / `no` on each row. It adds up the minutes of the `go` rows
   (and of `go` plus `maybe`) against the session length.
3. Copy the choices from the page and write them back:
   `python3 <method-root>/scripts/build_menu.py 7-validation/exercise-menu.md --apply choices.txt`.
4. Only then write `7-validation/tasks.md`, from the `go` rows. Each task still tests one bet.
   Put the order of the tasks through the contamination table of `7a`.

## What was left out, and why

- Pending. *(the `no` rows that a bet still needs: say which bet loses its test)*
