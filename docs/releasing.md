# Releasing

Short on purpose. Every line here is something that went wrong once.

## Before you tag

1. **Run both suites.** `python3 tests/test_init.py && python3 tests/test_consistency.py`
   CI does this on every push, but run it before you touch the version so a red
   suite never reaches a tag.

2. **Read the method as a whole, not as a diff.** The tests compare two files
   against each other; they cannot tell you that a document now contradicts
   another in prose, or that the skill narrates a flow the code no longer has.
   That needs a person or a review pass. Two releases shipped with a file saying
   "duplicate this section per profile" while another said that is never done.

3. **Grep the whole tree, not only the diff**, and every format, not only `.md`.
   Names, clients, amounts, IDs, local paths, email addresses. A file outside
   the change you were making is exactly where the last leak was found.

4. **Bump `VERSION` and write the `CHANGELOG` entry.** Major when the folder
   layout or a template breaks. Minor when a phase, a template or a skill is
   added. Patch for everything else.

## After you push

5. **Verify by cloning from the remote**, never by looking at your disk. What
   matters is what went public, not what sits locally.

```bash
git clone https://github.com/brunogiel/Empat.ia.git /tmp/verify && cd /tmp/verify
python3 tests/test_init.py && python3 tests/test_consistency.py
python3 scripts/init_project.py --project-root /tmp/fresh --lang es
```

The last line is the one that matters: a clean install has to produce six files
and nothing else. Two releases shipped without anyone running it.

## One rule about the changelog

Write what the kit gained, never what was taken out. An entry saying a reference
was removed points a reader at what it used to say.
