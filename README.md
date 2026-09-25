# Empat.ia

> Installable method to **guide you through a user discovery project**, using [Claude](https://claude.com/claude-code) or Codex. A tandem between YOU + Artificial Intelligence to carry out a Design Thinking project.

Empat.ia is a co-pilot that guides you through an empathic design process following the Design Thinking methodology. The final deliverable is **design principles** traceable to evidence, which you'll use to decide on product, user communication, and strategy.

## ⚠️ Before you use it

- **It's a co-pilot.** It doesn't replace fieldwork. If you don't talk to real users, the method doesn't work.
- **It takes time: at least a week of serious dedication + 10-12 interviews done by you.** The Guide puts together the interview guides, helps you recruit, and organizes the evidence, but it doesn't interview for you.
- **It doesn't replace professional judgment in high-stakes research** (medical, legal, financial, user vulnerability). Consult with a senior researcher.


## What it does

- It walks you through building **design principles** traceable to evidence. That is the central deliverable.
- It creates a `discovery/` folder inside your project, split in three zones: what you open, what the assistant keeps, and the raw material underneath.
- It guides you step by step through 10 stages, from initial alignment to evidence-based synthesis.
- It separates facts, assumptions, and inferences. It doesn't let you confuse them.
- It turns raw interview material into traceable atomic evidence before writing insights and principles.
- It offers you a council of agents (economist, sociologist, philosopher, artist, SME owner, cab driver, and others) when a decision needs more pressure.
- It keeps the project state visible at all times: where you are, what you've done, what's next.

## Who it's for

For anyone willing to learn from their users and ready to do the work. In particular: early-stage founders, Product Managers, UX Researchers, SME owners rethinking a service, students, and innovation teams.

Minimum requirements:

| What you need                          | What for                                       |
| -------------------------------------- | ---------------------------------------------- |
| Paid Claude or Codex account           | So an assistant can run the method with you    |
| 10-12 interviews with real users       | You do the fieldwork; it can't be delegated    |
| At least 1 week of dedication          | Without time, the method doesn't pay off       |

## How to use it

Tell your assistant (Claude or Codex), by copying this message:

```text
Install this repo for me: https://github.com/brunogiel/Empat.ia
```

Your assistant downloads the method, explains what it's about, and gets started with you.

At any point you can ask _"how's it going"_ or _"status"_ and it shows you where you are.

### Working in your own language

Tell your assistant which language you work in, and the whole folder is written
in it, not just the conversation. The repository stays in English; your
`discovery/` folder does not. File and folder names keep their English spelling
on purpose — they are the method's plumbing, and the numbers do the work of
telling you the order.

### Installing as a global skill

Optional, if you want it available across all your projects without pasting the link every time:

```bash
./install.sh claude   # copies the skill to ~/.claude/skills/discovery-guide
./install.sh codex    # copies the skill to ~/.codex/skills/discovery-guide
```

Then you invoke it with _"use Empat.ia"_ from any project.

## The discovery folder

It is numbered by phase, so the order you see is the order you work in. And it
**grows as you go**: six files exist at install, and only two of those are
yours. Every other file is written when you reach its phase, in your language,
already filled with what the project knows by then.

```text
discovery/
  0-README.md            the map: where am I, what do I open now
  1-desk-research/       brief.md  market.md  knowledge.md  sources/
  2-profiling/           profiles.md  recruiting.md
  3-guide/               guide.md  process.md
  4-field/               0-index.md  0-observation-plan.md  feedback/
                         INT-001-name-surname.md  OBS-001-place.md  _prep/  _raw/
  5-debrief/             findings.md  principles.md  output/summary.md
  _engine/               state, assumptions, decisions, evidence, budgets, sources, skills
  AGENTS.md  CLAUDE.md   two pointers so any assistant knows what this folder is
```

A file that does not exist yet is the design, not a broken install. Files you
open have a line budget: when one grows past it, the excess moves down to
`_engine/` instead of turning the document you need in the room into something
you cannot read. `3-guide/guide.md` has a hard cap of two printed pages, because
that is the file that broke first.

## The five phases

| Phase | What happens | Estimated time | What it leaves behind |
|---|---|---|---|
| **1 · Desk research** | Alignment, the design challenge, the market, and what you already know versus what you are assuming | 2-5 hrs | `1-desk-research/` |
| **2 · Profiling** | Who you need to talk to, and how you reach them. Recruiting starts here because it is the only step that takes days, not hours | 2-5 days | `2-profiling/` |
| **3 · The guide** | The instrument: the questions, and how your team works in the room | 1-2 hrs | `3-guide/` |
| **4 · The field** | Interviews and, when it applies, observation. One note per person, one per outing, plus feedback on how you are interviewing | 1-3 weeks | `4-field/` |
| **5 · Debrief** | Cross everything into design principles, and one page you can hand to someone who read none of it | 3-5 hrs | `5-debrief/` |

**Final deliverable**: a set of **design principles** traceable to interview quotes and evidence. Decision rules that you'll then use to guide:

- **Product**: what to build and what to leave out, how to prioritize features, how to resolve design dilemmas when they come up.
- **User communication**: what words to use, what to promise, what not to promise, how to speak to different profiles.
- **Strategy**: where to bet, which segment to prioritize, which opportunities are worth pursuing and which aren't.

The principles come with patterns, insights, top quotes, and "How might we..." (HMW) questions that open the next ideation phase. The principles are what you keep when the method ends.

Each phase closes with a gate: the Guide tells you what you have, what you are
still assuming, and what it would cost to move on. **It recommends; it does not
block.** If you decide to advance on assumptions, it records the assumption and
moves.

You do not have to run the whole thing. Say _"I just want the guide"_ and it
takes you through phases 1 to 3 at the minimum, or _"I already did the
interviews"_ and it starts at phase 4. Skipped phases are recorded as what you
are assuming by skipping them, so the gap stays visible instead of disappearing.

## What comes next

The method ends at design principles, and that is on purpose: the How Might We
questions it produces are the handoff, not the finish line. Two phases are
planned and not built yet.

| Coming | What it would cover |
|---|---|
| **Ideation** | Take the How Might We questions into concepts: diverge, cluster, choose with criteria that trace back to the principles instead of to taste |
| **Testing** | Put a concept in front of the same people, and learn from what they do with it rather than from what they say about it |

Until they exist, phase 5 hands you the questions and says so plainly. It does
not pretend the work is over.

## The Guide's four actions

At every gate, the Guide recommends an action:

- **Advance**: the material is enough, we move to the next stage.
- **Deepen**: there's a base but more depth is needed before moving on.
- **Question**: there are dangerous assumptions or loose definitions, let's pressure-test them before advancing.
- **Council**: the decision deserves bringing in outside voices with different lenses.

The Guide proposes. You choose. You can always override the recommendation, and the Guide will show you the risks of doing so.

## The council

When a decision is hard, you can call the council: a multidisciplinary team that pressures you from different lenses. As in an IDEO team, we mix profiles that don't think alike:

- An **economist** who looks at incentives and costs.
- A **sociologist** who challenges cultural context.
- A **philosopher** who fights for definitions and assumptions.
- An **artist** who opens up analogies and non-obvious possibilities.
- An **SME owner** who brings operational reality.
- A **growth specialist** who looks at channels and language.
- And others: technologist, industry expert, uxer, qualitative researcher, and even a **cab driver** for when the team gets too expert-heavy and a lateral perspective is needed.

The Guide proposes 3-5 based on the project and the gate, and helps you choose. You can also add or remove agents by hand. The rule: combine at least three different lenses to force useful disagreement. The council shows you the angles you can't see on your own.

## Privacy and sources

The public repository contains only generic method files. Private projects, client work, and specific examples are kept out.

The method was built on proprietary facilitation material, external human-centered design references (IDEO, Acumen, and others), and **years of experience running this method manually, pre-AI**. References are listed in [`docs/reference-map.md`](docs/reference-map.md). Source documents remain with their original owners.

## License

MIT, see [`LICENSE`](LICENSE).
