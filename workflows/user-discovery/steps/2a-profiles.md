# 2a, Profiles and qualitative sample

## Objective

Define who to interview and with what minimum diversity.

## Method notes

- Ask who the real user is, not just who buys.
- In logistics, for example, the user may be whoever handles logistics inside the company.
- Qualitative default: 10-12 interviews when the scope justifies it.
- You don't need statistical representativeness; you need diversity to find patterns.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add profiles`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/2-profiling/profiles.md`
- `discovery/_engine/state.yaml`
- `discovery/_engine/assumptions.md`
- `discovery/_engine/decisions.md`

## Quality checklist

- Focus user defined.
- Other relevant profiles identified.
- Clear diversity criteria.
- Quantity per profile.
- Reason for each profile.
- Distinguishes user, customer, payer, decision-maker, and operator.
- Includes mainstream and extremes when useful.
- Considers real accessibility for recruiting.

## Using the template

Fill out:

- User vs customer table.
- Possible segments.
- Extremes and mainstream.
- Recommended sample.
- Coverage plan per learning question.

## Council

Suggest `Council` if:

- There are multiple stakeholders.
- It is unclear who is user, buyer, or influencer.
- There is a marketplace or two-sided ecosystem.
- The target includes SMEs and it is unclear who decides, who operates, and who pays.

## Gate

Suggested action:

- `Advance` if the sample is recruitable and responds to the challenge.
- `Deepen` if profiles or criteria are missing.
- `Question` if only convenient users/friends were chosen.
