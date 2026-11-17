#!/usr/bin/env python3
"""Tests for scripts/check_state.py: a state file that contradicts itself must fail.

Run:  python3 tests/test_check_state.py

The control is the shipped template, which has to pass as it is. Every other test starts
from it and plants one contradiction.
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_state.py"
TEMPLATE = (REPO / "templates" / "state.yaml").read_text(encoding="utf-8")
sys.path.insert(0, str(REPO / "scripts"))
import check_state  # noqa: E402


def set_top(text, key, value):
    return re.sub(rf"^{key}: .*$", f"{key}: {value}", text, count=1, flags=re.M)


def set_step(text, step, status):
    return re.sub(rf"(^  {step}:\n    phase: \d\n    status: )\w+", rf"\g<1>{status}", text,
                  count=1, flags=re.M)


def set_sub(text, sub, status):
    return re.sub(rf"(^    {re.escape(sub)}: )\w+", rf"\g<1>{status}", text, count=1, flags=re.M)


def at_debrief(text, status):
    """The project is in the debrief and both marks say the same."""
    text = set_top(text, "current_phase", "5")
    text = set_top(text, "current_step", "debrief")
    text = set_top(text, "current_status", status)
    return set_step(text, "debrief", status)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_state(self, text, *args):
        folder = self.root / "_engine"
        folder.mkdir(exist_ok=True)
        (folder / "state.yaml").write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True)

    def errors(self, text):
        return check_state.check(check_state.parse_yaml(text))


class TestControl(Base):
    def test_the_shipped_template_passes(self):
        result = self.run_state(TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("0 errors, 0 warnings", result.stdout)

    def test_a_consistent_debrief_in_progress_passes(self):
        text = at_debrief(TEMPLATE, "drafted")
        for sub in ("5a.0", "5a.1"):
            text = set_sub(text, sub, "done")
        text = set_sub(text, "5a.2", "in_progress")
        self.assertEqual(self.errors(text), ([], []))

    def test_the_reader_handles_the_template(self):
        state = check_state.parse_yaml(TEMPLATE)
        self.assertEqual(state["steps"]["debrief"]["phase"], 5)
        self.assertEqual(state["steps"]["observation"]["on_demand"], True)
        self.assertEqual(state["phases"]["1"]["steps"][0], "start")
        self.assertEqual(state["plan"][0]["piece"], "desk-research")
        self.assertEqual(list(state["substeps"]["debrief"]), ["5a.0", "5a.1", "5a.2", "5a.3", "5a.4"])


class TestTwoMarksOfTheSameFact(Base):
    def test_validated_and_drafted_at_once_fails(self):
        text = at_debrief(TEMPLATE, "validated")
        text = set_step(text, "debrief", "drafted")
        for sub in ("5a.0", "5a.1", "5a.2", "5a.3", "5a.4"):
            text = set_sub(text, sub, "done")
        result = self.run_state(text)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("current_status is 'validated' but steps.debrief.status is 'drafted'", result.stdout)

    def test_the_phase_and_the_step_have_to_agree(self):
        text = at_debrief(TEMPLATE, "drafted")
        text = set_top(text, "current_phase", "4")
        errors, _ = self.errors(text)
        self.assertTrue(any("current_phase is 4" in e for e in errors), errors)

    def test_a_current_step_that_does_not_exist_fails(self):
        errors, _ = self.errors(set_top(TEMPLATE, "current_step", "dancing"))
        self.assertTrue(any("not a step declared" in e for e in errors), errors)

    def test_a_status_outside_the_list_fails(self):
        errors, _ = self.errors(set_step(TEMPLATE, "start", "finished"))
        self.assertTrue(any("steps.start.status is 'finished'" in e for e in errors), errors)


class TestSubstages(Base):
    def test_a_substage_done_after_one_that_is_not_fails(self):
        text = at_debrief(TEMPLATE, "drafted")
        text = set_sub(text, "5a.0", "done")
        text = set_sub(text, "5a.2", "done")  # 5a.1 never closed
        errors, _ = self.errors(text)
        self.assertTrue(any("5a.2 is done but 5a.1" in e for e in errors), errors)

    def test_a_skipped_substage_does_not_block_the_next(self):
        text = at_debrief(TEMPLATE, "drafted")
        text = set_sub(set_sub(text, "5a.0", "skipped"), "5a.1", "done")
        self.assertEqual(self.errors(text), ([], []))

    def test_a_closed_step_with_an_open_substage_fails(self):
        text = at_debrief(TEMPLATE, "validated")
        for sub in ("5a.0", "5a.1", "5a.2"):
            text = set_sub(text, sub, "done")
        errors, _ = self.errors(text)
        self.assertTrue(any("sub-stages are open: 5a.3" in e for e in errors), errors)

    def test_a_step_not_started_with_a_substage_done_fails(self):
        text = set_sub(TEMPLATE, "5a.0", "done")
        errors, _ = self.errors(text)
        self.assertTrue(any("not_started' but a sub-stage has started" in e for e in errors), errors)

    def test_an_unknown_substage_status_fails(self):
        errors, _ = self.errors(set_sub(TEMPLATE, "5a.1", "validated"))
        self.assertTrue(any("substeps.debrief.5a.1" in e for e in errors), errors)

    def test_a_project_from_before_substeps_existed_still_passes(self):
        old = TEMPLATE[:TEMPLATE.index("# Optional. A step that runs in sub-stages")]
        old += TEMPLATE[TEMPLATE.index("# --- The plan"):]
        old = old.replace('next: ""\n', "")
        self.assertNotIn("substeps:", old)
        self.assertEqual(self.errors(at_debrief(old, "drafted")), ([], []))


class TestPlanAndNext(Base):
    def test_a_plan_piece_done_while_its_steps_are_not_started_fails(self):
        text = TEMPLATE.replace("{piece: field, status: planned", "{piece: field, status: done")
        errors, _ = self.errors(text)
        self.assertTrue(any("plan says 'field' is done" in e for e in errors), errors)

    def test_a_plan_piece_done_when_its_steps_are_closed_passes(self):
        text = TEMPLATE.replace("{piece: guide, status: planned", "{piece: guide, status: done")
        text = set_step(set_step(text, "interview_guide", "validated"), "field_process", "validated")
        self.assertEqual(self.errors(text)[0], [])

    def test_next_that_points_at_something_already_done_warns(self):
        text = at_debrief(TEMPLATE, "drafted")
        for sub in ("5a.0", "5a.1", "5a.2"):
            text = set_sub(text, sub, "done")
        text = set_top(text, "next", '"Synthesise the patterns (`5a.2`), then the insights (`5a.3`)."')
        errors, warnings = self.errors(text)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("`5a.2`", warnings[0])
        result = self.run_state(text)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN", result.stdout)
        self.assertEqual(self.run_state(text, "--strict").returncode, 1)

    def test_next_that_points_at_a_closed_step_warns(self):
        text = set_step(TEMPLATE, "start", "validated")
        text = set_top(text, "next", '"Write the brief (`start`)."')
        _, warnings = self.errors(text)
        self.assertTrue(any("`start`" in w for w in warnings), warnings)

    def test_a_closed_current_step_with_an_empty_next_warns(self):
        text = set_top(set_top(TEMPLATE, "current_status", "validated"), "current_step", "start")
        text = set_step(text, "start", "validated")
        _, warnings = self.errors(text)
        self.assertTrue(any("`next` is empty" in w for w in warnings), warnings)

    def test_next_that_names_something_still_open_is_fine(self):
        text = at_debrief(TEMPLATE, "drafted")
        text = set_top(text, "next", '"Write the insights (`5a.3`)."')
        self.assertEqual(self.errors(text), ([], []))


class TestUsage(Base):
    def test_a_missing_file_exits_2(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root / "nowhere")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_state_flag_reads_a_file_anywhere(self):
        path = self.root / "s.yaml"
        path.write_text(TEMPLATE, encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--state", str(path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
