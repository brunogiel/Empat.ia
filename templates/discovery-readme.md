# Discovery

This folder holds a user discovery project run with Empat.ia. Three zones: what you read and edit, what the assistant uses to work, and the raw field material.

## Map

```text
discovery/
├── README.md                 where am I, what do I open now
├── challenge.md               what I'm researching, for whom, what it decides
├── who-to-talk-to.md          profiles, sample, bias
├── recruiting.md              channels, ready-to-paste copy, tracker
├── field-kit/                 what you take to the interview
│   ├── cheatsheet.md          one page: blocks, timing, words not to say
│   ├── guide.md                the script, questions only
│   ├── modules.md             per-profile variants
│   ├── checklist.md           before / during / after
│   └── observation.md         observation and immersion plan
├── findings.md                what is emerging, distilled
├── principles.md              THE DELIVERABLE
├── _system/                   the assistant lives here, you don't open it
├── _sources/                  raw and long, you consult it, you don't read it
└── interviews/                field material
```

## Where am I, what do I open now

| Stage | What's happening | Open |
|---|---|---|
| 1. Start | Framing the project and its maturity | `challenge.md` |
| 2. Design Challenge | Turning the problem into an open question | `challenge.md` |
| 3. Market research | Category, substitutes, references | `_sources/market-research.md` |
| 4. Knowledge base | What we know, assume, need to learn | `_sources/knowledge-base.md` |
| 5. Users and sample | Profiles, sample, bias | `who-to-talk-to.md` |
| 6. Interview guides | Script and printable cheat sheet | `field-kit/guide.md`, `field-kit/cheatsheet.md` |
| 7. Recruitment | Channels, copy, tracker | `recruiting.md` |
| 8. Field checklist | Before, during, after | `field-kit/checklist.md` |
| 9. Interview capture | Transcripts, notes, atomic evidence | `interviews/`, `_system/evidence-ledger.md` |
| 10. Synthesis | Distilling toward the deliverable | `findings.md`, then `principles.md` |

## About `_system/` and `_sources/`

`_system/` is where the assistant keeps state, assumptions, decisions and the evidence ledger. `_sources/` holds raw and long material: market research, the knowledge base, councils, data reviews, guide versions. You don't need to open either one; the assistant reads and writes them for you.

## Canonical state

The project's state lives in `_system/state.yaml`, and nowhere else. If a summary elsewhere disagrees with it, `_system/state.yaml` wins.
