# 2b, Recruiting

## Objective

Prepare messages and a scheduling plan.

## Method notes

- Incentives can help.
- Better if they aren't just friends.
- They shouldn't know the solution if that biases them.
- Possible channels: WhatsApp, email, LinkedIn, indirect acquaintances.

## First, the file of this step

The file this step writes does not exist yet. That is the design: nothing is
created at install except phase 1's brief.

1. **[DET]** Create it:
   `python3 <method-root>/scripts/init_project.py --project-root . --add recruiting`
2. **[DET]** Write it **in the language set in `_engine/state.yaml`**, not in
   the language of the repository.
3. **[LATENT]** Pre-fill it with what the project already knows. An empty
   template handed to the user is not a finished step.

## Documents to touch

- `discovery/2-profiling/recruiting.md`
- `discovery/2-profiling/profiles.md`
- `discovery/_engine/state.yaml`

## Checklist

- Clear message.
- Explicit duration.
- Purpose without biasing.
- Incentive, if applicable.
- Link or scheduling mechanism.
- Tracking of invitees.
- Criteria per profile.
- Bias risks by channel.
- Status of each contact.

## Using the template

Fill out:

- Criteria per profile.
- Channels with bias risks.
- Messages per channel.
- Recruitment tracker.

## Gate

Suggested action:

- `Advance` if there are messages and channels per profile.
- `Deepen` if access to users is missing.
- `Question` if recruitment biases too much.
