# Discovery

This folder holds your user discovery project. It is numbered by phase, so the
order you see is the order you work in.

**It grows as you go.** Right now most of it does not exist yet. That is the
design, not a broken install: each file is written when you reach its phase, in
your language, already filled with what the project knows by then. A blank form
handed to you on day one helps nobody.

## The eight pieces

| Phase | What happens | What it leaves behind |
|---|---|---|
| **1 · Desk research** | Frame the challenge, look at the market, write down what you already know and what you are assuming | `1-desk-research/` |
| **2 · Profiling** | Decide who you need to talk to, and how you will reach them | `2-profiling/` |
| **3 · The guide** | Build the instrument: the questions, and how you will work in the room | `3-guide/` |
| **4 · The field** | Interviews and observation. One note per person, one per outing | `4-field/` |
| **5 · Debrief** | Cross everything into design principles | `5-debrief/` |
| **6 · Ideation** *(on demand)* | From the How Might We questions to three to five concepts | `6-ideation/` |
| **7 · Validation** *(on demand)* | Put a prototype in front of people and watch what they do, not what they say | `7-validation/` |
| **8 · Report** | The final write-up of the whole project, on one page you can share | `8-report/` |

You do not walk them in number order by default. The brief closes with a **plan**
(`## Plan`) that says which pieces this project uses, in what order, and who does
each one. The order is the plan's, not the folder numbers'.

The deliverable is **design principles**: short decision rules, traceable to
something a real person said, that you use later for product, communication and
strategy.

## What to open now

`1-desk-research/brief.md`. Every other phase folder has a short `0-README.md` that says what it
is for and what will appear in it.

Ask your assistant *"how's it going"* at any point and it will tell you where
you are and what comes next.

## What is not for you

- **`_engine/`** — the assistant's workspace: state, assumptions, decisions,
  evidence, and the long raw material. You never need to open it.
- **`_prep/` and `_raw/`** inside `4-field/` — the disposable sheet you carry
  into each interview, and the transcripts, audio, photos and consents.
- **`AGENTS.md` and `CLAUDE.md`** — two short pointers so any AI assistant that
  opens this project knows what this folder is. They are not documentation for
  you; this file is.

## Two rules worth knowing

**The state lives in `_engine/state.yaml` and nowhere else.** If a summary
anywhere disagrees with it, that file wins.

**The folder listing tells you how far you got, not what you finished.** A file
appears when you *enter* its phase. To know whether a phase is closed, ask the
assistant or look at `_engine/state.yaml`.
