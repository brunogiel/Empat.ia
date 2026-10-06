#!/usr/bin/env python3
"""Tests for the Empat.ia project initializer.

Run:  python3 tests/test_init.py

These exist because the method shipped two breaking changes in two days and
neither release ever ran a clean install against itself. Every check below is a
claim the README makes about the folder; if one fails, the claim is false.

No dependencies: standard library only, so CI is one line.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INIT = REPO / "scripts" / "init_project.py"

INSTALLED = {
    "0-README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "1-desk-research/brief.md",
    "_engine/state.yaml",
    "_engine/budgets.yaml",
}


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(INIT), *args],
                          capture_output=True, text=True, cwd=cwd)


def files_in(discovery):
    return {str(p.relative_to(discovery)) for p in discovery.rglob("*") if p.is_file()}


class TempProject(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.discovery = self.tmp / "discovery"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def init(self, *extra):
        return run("--project-root", str(self.tmp), "--method-root", str(REPO), *extra)


class TestCleanInstall(TempProject):

    def test_installs_exactly_six_files(self):
        """The whole bet of v3. v2 installed 21, all of them empty."""
        self.init("--lang", "es")
        self.assertEqual(files_in(self.discovery), INSTALLED)

    def test_only_two_files_belong_to_the_user(self):
        self.init()
        mine = {f for f in files_in(self.discovery)
                if not f.startswith("_engine/") and f not in {"AGENTS.md", "CLAUDE.md"}}
        self.assertEqual(mine, {"0-README.md", "1-desk-research/brief.md"})

    def test_language_is_stamped_into_state(self):
        self.init("--lang", "es")
        state = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertIn('language: "es"', state)
        self.assertIn("version: 3", state)

    def test_no_phase_folder_is_prefilled(self):
        """Phases 2 to 5 have no files until you reach them."""
        self.init()
        for phase in ["2-profiling", "3-guide", "4-field", "5-debrief"]:
            found = list((self.discovery / phase).rglob("*.md"))
            self.assertEqual(found, [], f"{phase} should be empty at install")

    def test_phases_6_7_8_are_not_created_at_install(self):
        """They are born with their first --add, so a project that skips them
        never sees an empty folder."""
        self.init()
        for folder in ["6-ideation", "7-validation", "8-report"]:
            self.assertFalse((self.discovery / folder).exists(), folder)

    def test_1_desk_research_sources_is_created(self):
        """Client material (briefs, decks, canvases, spreadsheets, whiteboards)
        needs a folder a human can see, distinct from _engine/sources/, which
        is the assistant's own working material."""
        self.init()
        self.assertTrue((self.discovery / "1-desk-research" / "sources").is_dir())


class TestAddStep(TempProject):

    def test_add_materialises_one_file(self):
        self.init()
        result = self.init("--add", "market_research")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "1-desk-research" / "market.md").exists())

    def test_interview_feedback_step_creates_the_feedback_readme(self):
        """Interview feedback moved from one accumulating log to one file per
        interview. --add interview_feedback only materialises the folder's
        0-README.md; per-interview files are written by the assistant."""
        self.init()
        result = self.init("--add", "interview_feedback")
        self.assertEqual(result.returncode, 0, result.stderr)
        readme = self.discovery / "4-field" / "feedback" / "0-README.md"
        self.assertTrue(readme.exists())
        self.assertFalse((self.discovery / "4-field" / "0-interview-feedback.md").exists())

    def test_unknown_step_fails_loudly(self):
        self.init()
        result = self.init("--add", "not_a_step")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown step", result.stderr + result.stdout)

    def test_every_lazy_step_has_a_template(self):
        """A step whose template is missing would fail silently at the worst moment."""
        self.init()
        sys.path.insert(0, str(REPO / "scripts"))
        import init_project  # noqa: E402
        for step, (template, _) in init_project.LAZY.items():
            with self.subTest(step=step):
                self.assertTrue((REPO / "templates" / template).exists(),
                                f"step '{step}' points at missing template {template}")


class TestNewPieces(TempProject):
    """R2 and R5: --add for the plan and the pieces 6, 7 and 8."""

    def test_add_plan_creates_nothing_and_exits_zero(self):
        self.init()
        before = files_in(self.discovery)
        result = self.init("--add", "plan")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("brief", result.stdout)
        self.assertEqual(files_in(self.discovery), before)

    def test_each_new_step_creates_only_its_file(self):
        expected = {
            "ideation": {"6-ideation/concepts.md"},
            "validation_guide": {"7-validation/tasks.md"},
            "validation_debrief": {"7-validation/findings.md"},
            "report": {"8-report/summary.md"},
            "validation_capture": {"7-validation/0-index.md", "_engine/evidence.md"},
        }
        for step, created in expected.items():
            with self.subTest(step=step):
                shutil.rmtree(self.discovery, ignore_errors=True)
                self.init()
                before = files_in(self.discovery)
                result = self.init("--add", step)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(files_in(self.discovery) - before, created)

    def test_validation_capture_keeps_an_existing_evidence_ledger(self):
        self.init()
        self.init("--add", "evidence")
        ledger = self.discovery / "_engine" / "evidence.md"
        ledger.write_text("mine\n", encoding="utf-8")
        self.init("--add", "validation_capture")
        self.assertEqual(ledger.read_text(encoding="utf-8"), "mine\n")

    def test_lazy_state_and_budgets_declare_the_same_destinations(self):
        sys.path.insert(0, str(REPO / "scripts"))
        import init_project  # noqa: E402
        state = (REPO / "templates" / "state.yaml").read_text(encoding="utf-8")
        budgets = (REPO / "templates" / "budgets.yaml").read_text(encoding="utf-8")
        for step in ["ideation", "validation_guide", "validation_debrief", "report"]:
            dest = init_project.LAZY[step][1]
            with self.subTest(step=step):
                self.assertIn(dest, state)
                self.assertIn(dest, budgets)


class TestAddPerItem(TempProject):
    """--add interview-note|interview-prep|interview-feedback|observation-note --name <base>,
    the mechanism PER_ITEM declared but never wired up."""

    def test_interview_note_lands_at_4_field_base(self):
        self.init()
        result = self.init("--add", "interview-note", "--name", "INT-004-ana-lopez-acme")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "4-field" / "INT-004-ana-lopez-acme.md").exists())

    def test_interview_prep_lands_under_prep(self):
        self.init()
        result = self.init("--add", "interview-prep", "--name", "INT-004-ana-lopez-acme")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "4-field" / "_prep"
                         / "INT-004-ana-lopez-acme-prep.md").exists())

    def test_interview_feedback_lands_under_feedback(self):
        self.init()
        result = self.init("--add", "interview-feedback", "--name", "INT-004-ana-lopez-acme")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "4-field" / "feedback"
                         / "INT-004-ana-lopez-acme-feedback.md").exists())

    def test_observation_note_lands_at_4_field_base(self):
        self.init()
        result = self.init("--add", "observation-note", "--name", "OBS-002-store-floor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "4-field" / "OBS-002-store-floor.md").exists())

    def test_validation_note_lands_in_7_validation(self):
        self.init()
        result = self.init("--add", "validation-note", "--name", "VAL-001-ana-lopez")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "7-validation" / "VAL-001-ana-lopez.md").exists())

    def test_validation_prep_and_feedback_land_in_their_folders(self):
        self.init()
        self.init("--add", "validation-prep", "--name", "VAL-001-ana-lopez")
        self.init("--add", "validation-feedback", "--name", "VAL-001-ana-lopez")
        self.assertTrue((self.discovery / "7-validation" / "_prep"
                         / "VAL-001-ana-lopez-prep.md").exists())
        self.assertTrue((self.discovery / "7-validation" / "feedback"
                         / "VAL-001-ana-lopez-feedback.md").exists())

    def test_validation_note_refuses_an_interview_id(self):
        self.init()
        result = self.init("--add", "validation-note", "--name", "INT-001-x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VAL-", result.stderr + result.stdout)
        self.assertFalse((self.discovery / "7-validation").exists())

    def test_interview_note_refuses_a_validation_id(self):
        self.init()
        result = self.init("--add", "interview-note", "--name", "VAL-001-x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INT-", result.stderr + result.stdout)

    def test_observation_note_refuses_an_interview_id(self):
        self.init()
        result = self.init("--add", "observation-note", "--name", "INT-001-x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OBS-", result.stderr + result.stdout)

    def test_missing_name_fails_loudly(self):
        self.init()
        result = self.init("--add", "interview-note")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--name", result.stderr + result.stdout)

    def test_bad_name_is_refused(self):
        self.init()
        result = self.init("--add", "interview-note", "--name", "ana-lopez")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("base name", (result.stderr + result.stdout).lower())

    def test_never_overwrites_an_existing_item(self):
        self.init()
        self.init("--add", "interview-note", "--name", "INT-004-ana-lopez-acme")
        note = self.discovery / "4-field" / "INT-004-ana-lopez-acme.md"
        note.write_text("mine\n", encoding="utf-8")
        self.init("--add", "interview-note", "--name", "INT-004-ana-lopez-acme")
        self.assertEqual(note.read_text(encoding="utf-8"), "mine\n")


class TestAggregateSteps(TempProject):
    """interview_capture and debrief are aggregates in state.yaml: their 'file'
    field lists more than one path, each already a concrete LAZY step."""

    def test_interview_capture_runs_its_three_concrete_steps(self):
        self.init()
        result = self.init("--add", "interview_capture")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "4-field" / "0-index.md").exists())
        self.assertTrue((self.discovery / "4-field" / "feedback" / "0-README.md").exists())
        self.assertTrue((self.discovery / "_engine" / "evidence.md").exists())

    def test_debrief_runs_its_three_concrete_steps(self):
        self.init()
        result = self.init("--add", "debrief")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "5-debrief" / "findings.md").exists())
        self.assertTrue((self.discovery / "5-debrief" / "principles.md").exists())
        self.assertFalse((self.discovery / "5-debrief" / "output" / "summary.md").exists(),
                         "the summary moved to 8-report/ and is its own step")

    def test_start_and_design_challenge_point_at_the_installed_brief(self):
        self.init()
        for step in ["start", "design_challenge"]:
            with self.subTest(step=step):
                result = self.init("--add", step)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("brief.md", result.stderr + result.stdout)


class TestProjectName(TempProject):

    def test_project_name_flag_is_stamped(self):
        self.init("--project-name", "Acme Discovery")
        state = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertIn('project_name: "Acme Discovery"', state)

    def test_default_is_still_the_folder_name(self):
        self.init()
        state = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertIn(f'project_name: "{self.tmp.name}"', state)


class TestForceIsSafe(TempProject):
    """The v2 foot-gun: --force used to replace hand-translated files with the
    English templates. A real project logged 'do not run --force: it overwrites
    the Spanish'."""

    def test_force_does_not_touch_an_edited_file(self):
        self.init("--lang", "es")
        brief = self.discovery / "1-desk-research" / "brief.md"
        brief.write_text("# El desafio\nEsto lo traduje a mano.\n", encoding="utf-8")
        self.init("--force")
        self.assertIn("traduje a mano", brief.read_text(encoding="utf-8"))

    def test_force_does_recopy_an_untouched_file(self):
        self.init()
        readme = self.discovery / "0-README.md"
        original = readme.read_text(encoding="utf-8")
        readme.unlink()
        self.init("--force")
        self.assertEqual(readme.read_text(encoding="utf-8"), original)

    def test_overwrite_modified_is_the_only_way_to_clobber(self):
        self.init()
        brief = self.discovery / "1-desk-research" / "brief.md"
        brief.write_text("mine\n", encoding="utf-8")
        self.init("--overwrite-modified")
        self.assertNotEqual(brief.read_text(encoding="utf-8"), "mine\n")


class TestVersionDetection(TempProject):
    """v2's looks_like_v1() answered a yes/no question, so a v2 folder read as
    'not v1', fell through to the create branch, and got the new layout planted
    beside the old one without a word."""

    def make_v2(self):
        (self.discovery / "_system").mkdir(parents=True)
        (self.discovery / "_system" / "state.yaml").write_text("version: 2\n", encoding="utf-8")

    def make_v1(self):
        self.discovery.mkdir(parents=True)
        (self.discovery / "state.yaml").write_text("method: design-empathy-ai\n", encoding="utf-8")

    def test_refuses_to_create_over_v2(self):
        self.make_v2()
        result = self.init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("v2 folder", result.stderr + result.stdout)

    def test_refuses_to_create_over_v1(self):
        self.make_v1()
        result = self.init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("v1 folder", result.stderr + result.stdout)

    def test_migrate_is_idempotent_on_v3(self):
        self.init()
        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0)
        self.assertIn("already v3", result.stdout)


class TestMigrateV3ToReport(TempProject):
    """R8: a v3 folder made before the report existed keeps its summary, and
    the summary moves to 8-report/ without ever overwriting or deleting."""

    OLD = "5-debrief/output/summary.md"
    NEW = "8-report/summary.md"

    def old_project(self):
        """A v3 folder as it was: summary in 5-debrief/output/, no plan."""
        self.init()
        state = self.discovery / "_engine" / "state.yaml"
        text = state.read_text(encoding="utf-8")
        text = text[:text.index("# --- The plan")].rstrip("\n") + "\n"
        text = text.replace("file: 5-debrief/findings.md + 5-debrief/principles.md",
                            f"file: 5-debrief/findings.md + 5-debrief/principles.md + {self.OLD}")
        state.write_text(text, encoding="utf-8")
        brief = self.discovery / "1-desk-research" / "brief.md"
        text = brief.read_text(encoding="utf-8")
        brief.write_text(text[:text.index("## Plan")].rstrip("\n") + "\n", encoding="utf-8")
        (self.discovery / "5-debrief" / "output").mkdir(parents=True)
        (self.discovery / self.OLD).write_text("# Mi resumen\n", encoding="utf-8")

    def test_summary_moves_and_the_plan_is_added(self):
        self.old_project()
        before = len(files_in(self.discovery))
        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.discovery / self.OLD).exists())
        self.assertEqual((self.discovery / self.NEW).read_text(encoding="utf-8"), "# Mi resumen\n")
        self.assertEqual(len(files_in(self.discovery)), before)
        state = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertIn(self.NEW, state)
        self.assertNotIn(self.OLD, state)
        self.assertEqual(len(re.findall(r"^  - \{piece:", state, re.M)), 8)

    def test_running_it_twice_changes_nothing(self):
        self.old_project()
        self.init("--migrate")
        snapshot = {f: (self.discovery / f).read_bytes() for f in files_in(self.discovery)}
        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0)
        self.assertIn("already v3", result.stdout)
        after = {f: (self.discovery / f).read_bytes() for f in files_in(self.discovery)}
        self.assertEqual(after, snapshot)

    def test_it_never_overwrites_an_existing_report(self):
        self.old_project()
        (self.discovery / "8-report").mkdir()
        (self.discovery / self.NEW).write_text("hand made\n", encoding="utf-8")
        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0)
        self.assertEqual((self.discovery / self.NEW).read_text(encoding="utf-8"), "hand made\n")
        self.assertEqual((self.discovery / self.OLD).read_text(encoding="utf-8"), "# Mi resumen\n")
        self.assertIn("already exists", result.stdout)

    def test_a_folder_without_a_summary_only_gets_the_plan(self):
        self.old_project()
        (self.discovery / self.OLD).unlink()
        self.init("--migrate")
        state = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertIn("plan:", state)
        self.assertFalse((self.discovery / "8-report").exists())

    def make_really_old(self, with_brief_plan):
        """A v3 folder from before this change: 5 phases, no plan step, an
        old summary budget, statuses already in progress."""
        self.init()
        d = self.discovery
        state = d / "_engine" / "state.yaml"
        s = state.read_text(encoding="utf-8")
        s = s[:s.index("# --- The plan")]
        s = s[:s.index("\nvalidations:")].rstrip("\n") + "\n" if "\nvalidations:" in s else s
        s = re.sub(r"  6:\n(?:    .*\n)+  7:\n(?:    .*\n)+  8:\n(?:    .*\n)+", "", s)
        s = s.replace(", plan]", "]")
        s = re.sub(r"  plan:\n(?:    .*\n|  #.*\n)+", "", s)
        s = re.sub(r"  (ideation|validation_guide|validation_capture|validation_debrief|report):\n(?:    .*\n)+", "", s)
        s = s.replace("\n  # The plan can run", "\n  # The plan can run")
        s = s.replace("file: 5-debrief/findings.md + 5-debrief/principles.md",
                      "file: 5-debrief/findings.md + 5-debrief/principles.md + 5-debrief/output/summary.md")
        s = s.replace("current_step: start\ncurrent_status: not_started",
                      "current_step: start\ncurrent_status: validated")
        state.write_text(s, encoding="utf-8")
        b = d / "_engine" / "budgets.yaml"
        bt = b.read_text(encoding="utf-8")
        for path in ["6-ideation/concepts.md", "7-validation/tasks.md", "7-validation/0-index.md",
                     "7-validation/findings.md"]:
            bt = re.sub(rf"  {re.escape(path)}:\n    lines: \d+\n    hard: \w+\n", "", bt)
        bt = bt.replace("  8-report/summary.md:", "  5-debrief/output/summary.md:")
        b.write_text(bt, encoding="utf-8")
        brief = d / "1-desk-research" / "brief.md"
        text = brief.read_text(encoding="utf-8")
        text = text[:text.index("## Plan")].rstrip("\n") + "\n"
        if with_brief_plan:
            text += "\n## Plan\n\n1. interviews 5\n2. validation 5\n"
        brief.write_text(text, encoding="utf-8")
        (d / "5-debrief" / "output").mkdir(parents=True)
        (d / "5-debrief" / "output" / "summary.md").write_text("# s\n", encoding="utf-8")

    def test_full_migration_with_a_plan_in_the_brief_leaves_plan_empty(self):
        self.make_really_old(True)
        before = len(files_in(self.discovery))
        brief_before = (self.discovery / "1-desk-research" / "brief.md").read_bytes()
        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0, result.stderr)
        s = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        for n in "678":
            self.assertRegex(s, rf"(?m)^  {n}:$")
        self.assertRegex(s, r"(?m)^    steps: \[start, design_challenge, market_research, knowledge_base, plan\]")
        for step in ["plan", "ideation", "validation_guide", "validation_capture",
                     "validation_debrief", "report"]:
            self.assertRegex(s, rf"(?m)^  {step}:$")
        self.assertRegex(s, r"(?m)^validations:")
        self.assertRegex(s, r"(?m)^plan: \[\]")
        self.assertEqual(len(re.findall(r"^  - \{piece:", s, re.M)), 0)
        self.assertIn("current_status: validated", s, "an existing status was changed")
        self.assertNotIn("5-debrief/output/summary.md", s)
        self.assertEqual(len(files_in(self.discovery)), before)
        self.assertEqual((self.discovery / "1-desk-research" / "brief.md").read_bytes(), brief_before)
        self.assertIn("Guide", result.stdout)
        bud = (self.discovery / "_engine" / "budgets.yaml").read_text(encoding="utf-8")
        for path in ["6-ideation/concepts.md", "7-validation/tasks.md", "8-report/summary.md"]:
            self.assertIn(f"  {path}:", bud)
        self.assertNotIn("5-debrief/output/summary.md", bud)

    def test_full_migration_without_a_plan_in_the_brief_writes_the_default(self):
        self.make_really_old(False)
        self.init("--migrate")
        s = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^  - \{piece:", s, re.M)), 8)
        self.assertRegex(s, r"(?m)^validations:")

    def test_full_migration_is_idempotent_and_the_result_is_consistent(self):
        for with_plan in (True, False):
            with self.subTest(with_plan=with_plan):
                shutil.rmtree(self.discovery, ignore_errors=True)
                self.make_really_old(with_plan)
                self.init("--migrate")
                snap = {f: (self.discovery / f).read_bytes() for f in files_in(self.discovery)}
                result = self.init("--migrate")
                self.assertIn("already v3", result.stdout)
                self.assertEqual({f: (self.discovery / f).read_bytes()
                                  for f in files_in(self.discovery)}, snap)
                s = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
                self.assertEqual(s.count("\nvalidations:"), 1)
                self.assertEqual(len(re.findall(r"(?m)^  report:$", s)), 1)

    def test_a_v2_folder_ends_in_the_new_layout_with_a_plan(self):
        v2 = TestMigrationLosesNothing.build_v2_folder
        v2(self)
        self.init("--migrate")
        state = (self.discovery / "_engine" / "state.yaml").read_text(encoding="utf-8")
        self.assertIn("version: 3", state)
        self.assertIn("plan:", state)


class TestMigrationLosesNothing(TempProject):

    def build_v2_folder(self):
        layout = {
            "README.md": "# Descubrimiento\n",
            "challenge.md": "# Desafio\nEn espanol, a mano.\n",
            "who-to-talk-to.md": "# Perfiles\n",
            "recruiting.md": "# Reclutamiento\n",
            "findings.md": "# Hallazgos\n",
            "principles.md": "# Principios\n",
            "field-kit/guide.md": "# Guia\n",
            "field-kit/cheatsheet.md": "# Machete\n",
            "field-kit/checklist.md": "# Checklist\n",
            "field-kit/modules.md": "# Modulos\n",
            "field-kit/observation.md": "# Observacion\n",
            "_system/state.yaml": "version: 2\noutput: challenge.md\n",
            "_system/assumptions.md": "# Supuestos\n",
            "_system/evidence-ledger.md": "# Evidencia\n",
            "_system/budgets.yaml": "budgets: {}\n",
            "_sources/market-research.md": "# Mercado\n",
            "_sources/knowledge-base.md": "# Conocimiento\n",
            "interviews/index.md": "# Indice\n",
            "interviews/README.md": "# Entrevistas\n",
            "interviews/transcripts/INT-001.txt": "hola\n",
            "interviews/consent/INT-001.pdf": "consent\n",
            "interviews/notes/INT-001-ana.md": "# Ana\n",
        }
        for rel, body in layout.items():
            path = self.discovery / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return layout

    def test_migration_keeps_every_file_and_every_line(self):
        layout = self.build_v2_folder()
        before_files = len(files_in(self.discovery))
        before_lines = sum(len(b.splitlines()) for b in layout.values())

        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0, result.stderr)

        after = files_in(self.discovery)
        after_lines = sum(len((self.discovery / f).read_text(encoding="utf-8").splitlines())
                          for f in after)
        self.assertEqual(len(after), before_files, "a file went missing in migration")
        self.assertGreaterEqual(after_lines, before_lines, "lines were lost in migration")

    def test_migration_preserves_hand_translated_text(self):
        self.build_v2_folder()
        self.init("--migrate")
        brief = self.discovery / "1-desk-research" / "brief.md"
        self.assertTrue(brief.exists())
        self.assertIn("a mano", brief.read_text(encoding="utf-8"))

    def test_raw_trays_collapse_into_one(self):
        self.build_v2_folder()
        self.init("--migrate")
        raw = files_in(self.discovery / "4-field" / "_raw")
        self.assertIn("INT-001.txt", raw)
        self.assertIn("INT-001.pdf", raw)

    def test_dissolved_v2_files_are_archived_not_deleted(self):
        self.build_v2_folder()
        self.init("--migrate")
        sources = files_in(self.discovery / "_engine" / "sources")
        self.assertIn("v2-cheatsheet.md", sources)
        self.assertIn("v2-modules.md", sources)

    def test_leftover_sources_route_to_desk_research_not_engine(self):
        """market-research.md and knowledge-base.md are mapped explicitly and
        go to 1-desk-research/{market,knowledge}.md. Anything else left in
        _sources/ is raw client material a human should see, so it goes to
        1-desk-research/sources/, not to _engine/sources/, which is the
        assistant's own working material."""
        layout = self.build_v2_folder()
        (self.discovery / "_sources" / "client-deck.pdf").write_text("deck\n", encoding="utf-8")
        result = self.init("--migrate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "1-desk-research" / "sources" / "client-deck.pdf").exists())
        self.assertFalse((self.discovery / "_engine" / "sources" / "client-deck.pdf").exists())
        # The explicitly mapped files still go where they always did.
        self.assertTrue((self.discovery / "1-desk-research" / "market.md").exists())
        self.assertTrue((self.discovery / "1-desk-research" / "knowledge.md").exists())


class TestRepoIsConsistent(unittest.TestCase):
    """Checks about the bundle itself, not about any one project."""

    def test_every_installed_template_exists(self):
        sys.path.insert(0, str(REPO / "scripts"))
        import init_project  # noqa: E402
        for template in init_project.INSTALL:
            with self.subTest(template=template):
                self.assertTrue((REPO / "templates" / template).exists())

    def test_the_guide_respects_its_hard_budget(self):
        """budgets.yaml declares 3-guide/guide.md at 100 lines, hard. The shipped
        template has to fit inside the rule it ships."""
        guide = (REPO / "templates" / "guide.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(guide.splitlines()), 100,
                             "the guide template breaks its own hard budget")

    def test_no_file_still_points_at_the_v2_layout(self):
        stale = ["field-kit/", "_system/", "_sources/", "interviews/",
                 "_notes-template", "cheatsheet.md", "modules.md"]
        offenders = []
        skip = {"CHANGELOG.md", "init_project.py", "test_init.py", "test_consistency.py"}
        for path in REPO.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".yaml"}:
                continue
            if ".git" in path.parts or path.name in skip:
                continue
            body = path.read_text(encoding="utf-8", errors="ignore")
            for token in stale:
                if token in body:
                    offenders.append(f"{path.relative_to(REPO)} -> {token}")
        self.assertEqual(offenders, [], "v2 paths survive:\n" + "\n".join(offenders))


class NamedFolder(unittest.TestCase):
    """A project can call its folder discovery-<project>, and nothing breaks."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_folder_flag_creates_the_named_folder(self):
        result = run("--project-root", str(self.tmp), "--folder", "discovery-acme")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "discovery-acme" / "_engine" / "state.yaml").exists())
        self.assertFalse((self.tmp / "discovery").exists())

    def test_a_renamed_folder_is_found_without_the_flag(self):
        run("--project-root", str(self.tmp), "--folder", "discovery-acme")
        result = run("--project-root", str(self.tmp), "--add", "profiles")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "discovery-acme" / "2-profiling" / "profiles.md").exists())

    def test_plain_and_named_folder_together_are_refused(self):
        run("--project-root", str(self.tmp))
        run("--project-root", str(self.tmp), "--folder", "discovery-acme")
        result = run("--project-root", str(self.tmp), "--add", "profiles")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--folder", result.stdout + result.stderr)

    def test_two_named_folders_are_refused_not_guessed(self):
        run("--project-root", str(self.tmp), "--folder", "discovery-a")
        run("--project-root", str(self.tmp), "--folder", "discovery-b")
        result = run("--project-root", str(self.tmp), "--add", "profiles")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--folder", result.stdout + result.stderr)


class CountFromTheStartMarker(unittest.TestCase):
    """One transcript file holds notes, small talk and the interview."""

    def test_comments_and_small_talk_are_not_counted(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        text = ("# header\n# live note: Ana: ask why\n"
                "Ana: hi, waiting for him\n"
                "# === INTERVIEW START ===\n"
                "Ana: tell me about the last time\nLuis: it was monday\n")
        kept = interview_text(text)
        self.assertNotIn("waiting", kept)
        self.assertNotIn("live note", kept)
        self.assertIn("Luis: it was monday", kept)

    def test_a_hash_that_is_speech_is_kept(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        kept = interview_text("Ana: what matters?\nLuis: two things\n#1 is speed\n")
        self.assertIn("#1 is speed", kept)

    def test_without_a_marker_only_comments_go(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        kept = interview_text("# note\nAna: hi\nLuis: hello\n")
        self.assertEqual(kept, "Ana: hi\nLuis: hello")

    def test_the_new_marker_is_interview_heading(self):
        """The current convention: '## Interview' (or '## Entrevista'), not the
        old '# === INTERVIEW START ===' line."""
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        text = ("# Transcript · INT-006 · Ana Lopez (Acme) · 2026-09-25\n"
                "> Recorder: otter, id 123.\n"
                "> Speakers: Ana (interviewer) · Luis (interviewee)\n\n"
                "## Live notes\n- ask why twice\n\n"
                "## Before the interview\n"
                "Ana: how's the weather\n\n"
                "## Interview\n"
                "Ana: tell me about the last time\n\n"
                "Luis: it was monday\n")
        kept = interview_text(text)
        self.assertNotIn("ask why twice", kept)
        self.assertNotIn("weather", kept)
        self.assertIn("Luis: it was monday", kept)

    def test_entrevista_marker_also_works(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        text = "Ana: charla previa\n## Entrevista\nAna: pregunta\nLuis: respuesta\n"
        kept = interview_text(text)
        self.assertNotIn("charla previa", kept)
        self.assertIn("Luis: respuesta", kept)

    def test_headings_below_the_marker_are_not_counted(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        text = ("## Interview\n"
                "### A section someone pasted mid-transcript\n"
                "Ana: question\n\nLuis: answer\n")
        kept = interview_text(text)
        self.assertNotIn("section someone pasted", kept)
        self.assertIn("Luis: answer", kept)

    def test_blockquotes_below_the_marker_are_not_counted(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import interview_text
        text = ("## Interview\n"
                "> Recorder note: audio glitch at 12:03\n"
                "Ana: question\n\nLuis: answer\n")
        kept = interview_text(text)
        self.assertNotIn("audio glitch", kept)
        self.assertIn("Luis: answer", kept)


class ParseOneLineExports(unittest.TestCase):
    """The one-line export shapes recorders actually produce. Before the fix, a
    bare '\\s' boundary let a colon inside prose get learned as a label, so
    these either produced garbage speakers or reported one speaker at 0%/100%
    interviewer share."""

    def setUp(self):
        sys.path.insert(0, str(REPO / "scripts"))
        global parse
        from count_interview import parse

    def test_sentence_punctuation_separated_one_liner(self):
        text = ("Me: hola, como andas? Them: bien, todo bien. "
                "Me: contame, por que paso eso? Them: porque si, fue asi. "
                "Me: y despues que hiciste? Them: segui como siempre.")
        turns = parse(text)
        self.assertEqual({t["speaker"] for t in turns}, {"Me", "Them"})
        self.assertEqual(len(turns), 6)

    def test_double_space_separated_one_liner(self):
        text = "Me: hola  Them: bien  Me: contame mas  Them: listo  Me: ok gracias  Them: de nada"
        turns = parse(text)
        self.assertEqual({t["speaker"] for t in turns}, {"Me", "Them"})
        self.assertEqual(len(turns), 6)

    def test_normal_multiline_transcript_is_unchanged(self):
        text = ("Ana: hi\nLuis: hello\nAna: how are you\nLuis: fine\n"
                "Ana: tell me more\nLuis: sure thing\n")
        turns = parse(text)
        self.assertEqual({t["speaker"] for t in turns}, {"Ana", "Luis"})
        self.assertEqual(len(turns), 6)

    def test_single_speaker_result_errors(self):
        transcript = REPO / "tests" / "_tmp_single_speaker.md"
        transcript.write_text("Ana: hi\nAna: how are you\nAna: tell me more\n",
                              encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "count_interview.py"),
                 str(transcript), "--interviewer", "Ana"],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("one speaker", (result.stderr + result.stdout).lower())
        finally:
            transcript.unlink()


class PatternsEsConcreteAnchors(unittest.TestCase):
    """CONCRETE anchors must catch masculine/other forms too, not only the
    feminine ones already listed."""

    def test_masculine_and_other_last_time_forms(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from patterns_es import CONCRETE
        for phrase in ["el ultimo", "el otro dia", "ayer", "la semana pasada"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, CONCRETE)

    def test_contame_el_ultimo_reclamo_is_detected(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from count_interview import fold
        from patterns_es import CONCRETE
        text = fold("contame el último reclamo")
        self.assertTrue(any(n in text for n in CONCRETE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
