#!/usr/bin/env python3
"""Does the method hang together?

Every check here exists because a real inconsistency survived two releases:
state.yaml declared eleven steps against ten files, the editor's routing table
pointed at folders the layout no longer had, the guide told you to duplicate a
section per profile while another file said that is never done, and the shipped
guide template broke the line budget shipped beside it.

None of those needed judgement to catch. They needed someone to compare two
files, which is what a test does in a second, for free, forever.

Run:  python3 tests/test_consistency.py
"""

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "templates" / "state.yaml"
BUDGETS = REPO / "templates" / "budgets.yaml"
STEPS_DIR = REPO / "workflows" / "user-discovery" / "steps"

PHASES = ["1-desk-research", "2-profiling", "3-guide", "4-field", "5-debrief"]
ENGINE_EXEMPT = ("_engine/", "4-field/_prep/", "4-field/_raw/", "4-field/INT-",
                 "4-field/OBS-", "notes.md")


def state_steps():
    """{step_key: {"phase": n, "file": "...", "gate": bool}} from state.yaml."""
    text = STATE.read_text(encoding="utf-8")
    block = text[text.index("\nsteps:"):text.index("\ninterviews:")]
    steps, current = {}, None
    for line in block.splitlines():
        key = re.match(r"^  ([a-z_]+):\s*$", line)
        if key:
            current = key.group(1)
            steps[current] = {}
            continue
        field = re.match(r"^    ([a-z_]+):\s*(.+)$", line)
        if field and current:
            steps[current][field.group(1)] = field.group(2).strip()
    return steps


def state_phase_steps():
    """{phase_number: [step, ...]} from the phases block."""
    text = STATE.read_text(encoding="utf-8")
    block = text[text.index("\nphases:"):text.index("\nsteps:")]
    out, current = {}, None
    for line in block.splitlines():
        num = re.match(r"^  (\d+):\s*$", line)
        if num:
            current = int(num.group(1))
            continue
        listed = re.match(r"^    steps:\s*\[(.+)\]\s*$", line)
        if listed and current:
            out[current] = [s.strip() for s in listed.group(1).split(",")]
    return out


def budget_paths():
    text = BUDGETS.read_text(encoding="utf-8")
    block = text[text.index("\nbudgets:"):text.index("\n# Files with no line budget")]
    return set(re.findall(r"^  ([^\s#][^:]*):\s*$", block, re.M))


def step_files():
    return sorted(p.name for p in STEPS_DIR.glob("*.md"))


def lazy_map():
    sys.path.insert(0, str(REPO / "scripts"))
    import init_project
    return init_project.LAZY, init_project.INSTALL


class TestStepsAndFiles(unittest.TestCase):
    """state.yaml, the step files, and the phase list have to agree."""

    def test_every_declared_step_has_a_file(self):
        declared = set(state_steps())
        prefixes = {name.split("-")[0] for name in step_files()}
        self.assertEqual(len(declared), len(step_files()),
                         f"{len(declared)} steps declared, {len(step_files())} step files. "
                         f"This is the guide_context bug: a step nobody could read.")
        self.assertEqual(len(prefixes), len(step_files()),
                         "two step files share a prefix")

    def test_phase_lists_cover_every_step_exactly_once(self):
        listed = [s for steps in state_phase_steps().values() for s in steps]
        self.assertEqual(sorted(listed), sorted(state_steps()),
                         "a step is missing from its phase, or listed twice")

    def test_step_file_prefix_matches_its_phase(self):
        """4a-interview-capture.md must belong to phase 4, not to phase 3."""
        by_phase = state_phase_steps()
        order = [s for n in sorted(by_phase) for s in by_phase[n]]
        phase_of = {s: n for n, steps in by_phase.items() for s in steps}
        for step, name in zip(order, step_files()):
            with self.subTest(step=step):
                self.assertTrue(name.startswith(str(phase_of[step])),
                                f"step '{step}' is in phase {phase_of[step]} "
                                f"but its file is named '{name}'")


class TestFilesAndBudgets(unittest.TestCase):

    def test_every_step_output_has_a_budget_or_is_exempt(self):
        """A file the user opens with no budget is a file nobody trims."""
        budgets = budget_paths()
        missing = []
        for step, fields in state_steps().items():
            for path in [p.strip() for p in fields.get("file", "").split("+")]:
                if not path or path.startswith(ENGINE_EXEMPT):
                    continue
                if path not in budgets:
                    missing.append(f"{step} -> {path}")
        self.assertEqual(missing, [],
                         "step outputs with no line budget:\n" + "\n".join(missing))

    def test_every_budget_points_at_a_real_phase(self):
        for path in budget_paths():
            with self.subTest(path=path):
                self.assertTrue(path == "0-README.md" or path.split("/")[0] in PHASES,
                                f"budget for '{path}', which is not in any phase")

    def test_the_hard_budget_is_the_guide(self):
        """The one file that must never grow is the master guide. It is the file
        that reached 257 lines on the first external run."""
        text = BUDGETS.read_text(encoding="utf-8")
        hard = re.findall(r"^  ([^\s#][^:]*):\n    lines: \d+\n    hard: true",
                          text, re.M)
        self.assertEqual(hard, ["3-guide/guide.md"],
                         f"hard budgets are {hard}; expected exactly the master guide")


class TestScriptMatchesState(unittest.TestCase):
    """init_project.py and state.yaml describe the same folder or they lie."""

    def test_every_lazy_destination_is_declared_in_state(self):
        lazy, _ = lazy_map()
        declared = set()
        for fields in state_steps().values():
            declared.update(p.strip() for p in fields.get("file", "").split("+"))
        orphans = [f"{step} -> {dest}" for step, (_, dest) in lazy.items()
                   if dest not in declared and not dest.startswith("_engine/")]
        self.assertEqual(orphans, [],
                         "the script can create files state.yaml never mentions:\n"
                         + "\n".join(orphans))

    def test_install_matches_what_the_docs_promise(self):
        _, install = lazy_map()
        self.assertEqual(len(install), 6,
                         "the README and the skill both say six files install")
        mine = [d for d in install.values()
                if not d.startswith("_engine/") and d not in {"AGENTS.md", "CLAUDE.md"}]
        self.assertEqual(sorted(mine), ["0-README.md", "1-desk-research/brief.md"])


class TestEditorCanDoItsJob(unittest.TestCase):
    """The editor is the only thing that enforces budgets. A routing table
    pointing at folders that no longer exist makes every other guardrail
    decorative, and that is exactly what almost shipped."""

    def test_every_routing_destination_is_a_real_path(self):
        text = (REPO / "agents" / "editor.md").read_text(encoding="utf-8")
        table = text[text.index("## Routing table"):text.index("## Hard rules")]
        destinations = re.findall(r"\|\s*`([^`]+)`", table)
        bad = [d for d in destinations
               if not (d.split("/")[0] in PHASES or d.startswith("_engine/")
                       or d == "0-README.md")]
        self.assertEqual(bad, [], f"editor routes to paths outside the layout: {bad}")

    def test_the_editor_knows_about_notes(self):
        text = (REPO / "agents" / "editor.md").read_text(encoding="utf-8")
        self.assertIn("notes.md", text,
                      "notes.md is the editor's inbox; if it is not in the contract, "
                      "the drawer fills up and nobody empties it")


class TestNoContradictions(unittest.TestCase):
    """Two files telling the user opposite things is the failure a grep can
    catch and a reader usually will not."""

    def test_the_guide_does_not_ask_to_duplicate_per_profile_twice(self):
        """v2 had guide.md saying 'duplicate this section per profile' while
        modules.md said a module is 'never a full guide duplicated'."""
        guide = (REPO / "templates" / "guide.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("duplicate this section", guide)
        self.assertFalse((REPO / "templates" / "field-kit-modules.md").exists(),
                         "modules.md is back, and with it the two-mechanism contradiction")

    def test_findings_and_principles_do_not_overlap(self):
        """v2 added findings.md repeating four of principles.md's sections."""
        principles = (REPO / "templates" / "principles.md").read_text(encoding="utf-8")
        for heading in ["Patterns that repeat", "Strong patterns", "Weak signals",
                        "Open contradictions", "Prioritized insights"]:
            with self.subTest(heading=heading):
                self.assertNotIn(f"## {heading}", principles,
                                 f"'{heading}' belongs to findings.md, not to the deliverable")

    def test_the_readme_does_not_claim_the_method_blocks_skipping(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("won't let you skip", readme)
        self.assertIn("I just want the guide", readme,
                      "the named entry points replace the claim; keep them documented")


if __name__ == "__main__":
    unittest.main(verbosity=2)
