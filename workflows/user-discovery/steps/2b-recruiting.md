# 2b, Recruiting

## Objective

Prepare messages and a scheduling plan.

## Method notes

- Incentives can help.
- Better if they aren't just friends.
- They shouldn't know the solution if that biases them.
- Possible channels: WhatsApp, email, LinkedIn, indirect acquaintances.
- **A focus per profile is filtered here.** If the client asked for a focus (for example, "people who do not know the brand"), it goes in the profile's "Must meet" column, in the screening question, and again in the first minutes of the session. If the sample that came did not meet it, the report says so; it is not hidden by a good count.
- **The session is recorded, and the recording is armed from the account of whoever keeps the material.** A recording lands in the storage of whoever starts or hosts the call. If that is someone who is not the keeper, the file may never reach the project, or reach it late. So the keeper (the person who will store and process the material) creates the call and the scheduling link, or is the one who starts the recording, and checks after the first session that the file arrived where the project can read it. A session on a screen (a prototype, a wireframe, a form) is always recorded: without the video, "this", "here" and the clicks are lost.
- **Consent lives in the project, per person.** Get it signed before the first session and record it in the "Consent record" of `recruiting.md`: where the file is, and what it allows (record, quote, name, clip) as four separate permissions. A missing permission means no. Before any name or clip leaves, `4a` and `8a` cross the record with the audience and with the client's contract.

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
- The calls and the scheduling link are created from the keeper's account, with the recording on.
- A consent row per person, with the four permissions.
- The focus of each profile, in the criteria and in the screening question.

## Using the template

Fill out:

- Criteria per profile.
- Channels with bias risks.
- Messages per channel.
- Consent record.
- Recruitment tracker.

## Gate

Suggested action:

- `Advance` if there are messages and channels per profile.
- `Deepen` if access to users is missing.
- `Question` if recruitment biases too much.
