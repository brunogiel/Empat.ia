#!/usr/bin/env python3
"""Tests for the Empat.ia project initializer.

Run:  python3 tests/test_init.py

These exist because the method shipped two breaking changes in two days and
neither release ever ran a clean install against itself. Every check below is a
claim the README makes about the folder; if one fails, the claim is false.

No dependencies: standard library only, so CI is one line.
"""

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


class TestAddStep(TempProject):

    def test_add_materialises_one_file(self):
        self.init()
        result = self.init("--add", "market_research")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.discovery / "1-desk-research" / "market.md").exists())

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
        stale = ["field-kit/", "_system/", "_sources/", "interviews/"]
        offenders = []
        skip = {"CHANGELOG.md", "init_project.py", "test_init.py"}
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
