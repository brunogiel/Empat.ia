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

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "templates" / "state.yaml"
BUDGETS = REPO / "templates" / "budgets.yaml"
STEPS_DIR = REPO / "workflows" / "user-discovery" / "steps"

PHASES = ["1-desk-research", "2-profiling", "3-guide", "4-field", "5-debrief",
          "6-ideation", "7-validation", "8-report"]
ENGINE_EXEMPT = ("_engine/", "4-field/_prep/", "4-field/_raw/", "4-field/INT-",
                 "4-field/OBS-", "7-validation/_prep/", "7-validation/_raw/",
                 "7-validation/VAL-", "7-validation/feedback/", "notes.md")

# Every template the user opens. Each one starts with an 'Owns:' line.
OWNED_TEMPLATES = ["brief", "knowledge", "market", "profiles", "recruiting", "guide",
                   "process", "findings", "principles", "summary", "concepts", "tasks",
                   "validation-findings", "expert-consult", "meeting-coverage",
                   "exercise-menu", "usability-matrix", "presentation", "meeting-claims"]


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


class TestValidationRound(unittest.TestCase):
    """Phases 6 and 7: bets that can conclude, a menu, logistics, moderator feedback, a matrix."""

    def read(self, *parts):
        return REPO.joinpath(*parts).read_text(encoding="utf-8")

    def test_the_bets_say_what_confirms_and_what_drops_them(self):
        concepts = self.read("templates", "concepts.md")
        self.assertRegex(concepts, r"\| Bet \| Comes from \| Confirmed if \| Dropped if \|")
        self.assertIn("whoever did the ideation", concepts)
        ideation = self.read("workflows", "user-discovery", "steps", "6a-ideation.md")
        self.assertIn("## The bets", ideation)
        self.assertIn("external", ideation)
        guide = self.read("workflows", "user-discovery", "steps", "7a-validation-guide.md")
        self.assertIn("in the same change", guide)
        self.assertIn("not tested", guide)

    def test_7a_brings_the_goal_down_and_orders_the_tasks(self):
        guide = self.read("workflows", "user-discovery", "steps", "7a-validation-guide.md")
        for phrase in ["behaviour you can watch", "The real case comes first",
                       "## Optional, 7a.0: the menu of exercises", "## Order and contamination",
                       "build_menu.py", "exercise_menu", "go", "maybe"]:
            self.assertIn(phrase, guide)
        table = guide[guide.index("## Order and contamination"):guide.index("## Process")]
        self.assertGreaterEqual(len(re.findall(r"^\| (?!If this|---)", table, re.M)), 5)
        tasks = self.read("templates", "tasks.md")
        self.assertIn("Order of the tasks, and why", tasks)

    def test_7b_has_the_logistics_checklist_and_the_moderator_page(self):
        step = self.read("workflows", "user-discovery", "steps", "7b-validation-sessions.md")
        block = step[step.index("## Before each session"):step.index("## The moderator's feedback")]
        for phrase in ["computer", "same message as the link", "Test data", "floating window",
                       "Time per task"]:
            self.assertIn(phrase, block)
        self.assertIn("moderator-feedback.html", step)
        self.assertNotIn("interview-feedback.html", step)

    def test_the_moderator_page_has_no_discovery_scales_and_loads_nothing(self):
        page = self.read("templates", "moderator-feedback.html")
        self.assertNotIn("{{SCALES}}", page)
        self.assertNotIn("<script", page)
        self.assertIn("prefers-color-scheme: dark", page)
        for word in ["alone", "guided", "induced", "person", "trade", "Task by task"]:
            self.assertIn(word, page)
        urls = set(re.findall(r'(?:src|href)="(https?://[^"]+)"', page))
        self.assertTrue(all("fonts.g" in u for u in urls), urls)

    def test_7c_separates_a_prototype_failure_from_a_finding(self):
        step = self.read("workflows", "user-discovery", "steps", "7c-validation-debrief.md")
        for phrase in ["`prototype`", "does not count toward", "validation_matrix",
                       "validation_analysis_guide", "refuter", "provisional",
                       "The devil's advocate is seeded too"]:
            self.assertIn(phrase, step)
        matrix = self.read("templates", "usability-matrix.md")
        for word in ["alone", "guided", "induced", "failed", "prototype", "design",
                     "undetermined", "Provisional"]:
            self.assertIn(word, matrix)
        self.assertIn("Cause", self.read("templates", "validation-findings.md"))

    def test_the_new_files_are_declared_and_budgeted(self):
        state = self.read("templates", "state.yaml")
        budgets = self.read("templates", "budgets.yaml")
        lazy, _ = lazy_map()
        for step in ["exercise_menu", "validation_matrix", "validation_analysis_guide"]:
            dest = lazy[step][1]
            self.assertIn(dest, state, step)
            self.assertIn(dest, budgets, step)
        for name in ["exercise-menu.md", "usability-matrix.md", "moderator-feedback.html"]:
            self.assertTrue((REPO / "templates" / name).exists(), name)


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
        """The files that must never grow are the two scripts you hold in the room:
        the master guide (the file that grows across interviews) and the
        validation task script."""
        text = BUDGETS.read_text(encoding="utf-8")
        hard = re.findall(r"^  ([^\s#][^:]*):\n    lines: \d+\n    hard: true",
                          text, re.M)
        self.assertEqual(sorted(hard), ["3-guide/guide.md", "7-validation/tasks.md"],
                         f"hard budgets are {hard}; expected exactly the two guides")

    def test_new_pieces_have_the_budgets_the_spec_gives(self):
        text = BUDGETS.read_text(encoding="utf-8")
        for path, lines, hard in [("6-ideation/concepts.md", 80, "false"),
                                  ("7-validation/tasks.md", 100, "true"),
                                  ("7-validation/findings.md", 120, "false"),
                                  ("8-report/summary.md", 60, "false")]:
            with self.subTest(path=path):
                self.assertRegex(text, rf"  {re.escape(path)}:\n    lines: {lines}\n    hard: {hard}")

    def test_shipped_templates_fit_their_budgets(self):
        text = BUDGETS.read_text(encoding="utf-8")
        for path, template in [("6-ideation/concepts.md", "concepts.md"),
                               ("7-validation/tasks.md", "tasks.md"),
                               ("7-validation/findings.md", "validation-findings.md"),
                               ("8-report/summary.md", "summary.md")]:
            with self.subTest(path=path):
                lines = int(re.search(rf"  {re.escape(path)}:\n    lines: (\d+)", text).group(1))
                body = (REPO / "templates" / template).read_text(encoding="utf-8")
                self.assertLessEqual(len(body.splitlines()), lines)


class TestPlan(unittest.TestCase):
    """The map has eight pieces and the plan, not the folder number, orders them."""

    def test_the_map_has_eight_phases(self):
        phases = state_phase_steps()
        self.assertEqual(sorted(phases), list(range(1, 9)))
        self.assertEqual(phases[6], ["ideation"])
        self.assertEqual(phases[7], ["validation_guide", "validation_capture",
                                     "validation_debrief"])
        self.assertEqual(phases[8], ["report"])

    def test_plan_is_the_last_gated_step_of_phase_1_and_has_a_gate(self):
        """After the plan only on-demand steps may follow (1f: after a client meeting)."""
        steps = state_steps()
        gated = [s for s in state_phase_steps()[1] if not steps[s].get("on_demand")]
        self.assertEqual(gated[-1], "plan")
        self.assertEqual(state_steps()["plan"]["gate"], "true")
        self.assertEqual(state_steps()["plan"]["file"], "1-desk-research/brief.md")

    def test_phases_6_and_7_are_on_demand_and_8_is_not(self):
        steps = state_steps()
        for name in ["ideation", "validation_guide", "validation_capture",
                     "validation_debrief"]:
            self.assertEqual(steps[name].get("on_demand"), "true", name)
        self.assertNotIn("on_demand", steps["report"])

    def test_default_plan_has_eight_entries(self):
        text = STATE.read_text(encoding="utf-8")
        entries = re.findall(r"^  - \{piece: ([\w-]+),\s+status: (\w+)", text, re.M)
        self.assertEqual(len(entries), 8)
        status = dict(entries)
        for piece in ["desk-research", "profiling", "guide", "field", "debrief", "report"]:
            self.assertEqual(status[piece], "planned")
        self.assertEqual(status["ideation"], "skipped")
        self.assertEqual(status["validation"], "skipped")
        self.assertIn("THE ORDER IS THE PLAN'S, NOT THE FOLDER NUMBER'S", text)

    def test_the_brief_closes_with_a_plan_section(self):
        brief = (REPO / "templates" / "brief.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^## Plan$", brief, re.M)), 1)
        self.assertTrue(brief.rstrip().splitlines()[-1].startswith("|"),
                        "the plan is the last thing in the brief")

    def test_the_plan_step_tells_the_guide_what_to_say(self):
        step = (STEPS_DIR / "1e-plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("skipped", step)
        self.assertIn("external", step)
        self.assertIn("widget", step)
        self.assertIn("decisions.md", step)

    def test_new_pieces_have_steps_and_templates(self):
        for name in ["1e-plan.md", "6a-ideation.md", "7a-validation-guide.md",
                     "7b-validation-sessions.md", "7c-validation-debrief.md",
                     "8a-report.md"]:
            self.assertIn(name, step_files())
        for name in ["concepts.md", "tasks.md", "validation-findings.md"]:
            self.assertTrue((REPO / "templates" / name).exists(), name)


class TestPlanIsAContract(unittest.TestCase):
    """R22-R23: every plan row says who, how and when it is done."""

    def test_every_default_plan_row_has_the_contract_fields(self):
        text = STATE.read_text(encoding="utf-8")
        rows = re.findall(r"^  - \{piece:.*\}$", text, re.M)
        self.assertEqual(len(rows), 8)
        for row in rows:
            for field in ["owner:", "reviewers:", "how:", "done_when:"]:
                with self.subTest(row=row[:30], field=field):
                    self.assertIn(field, row)

    def test_the_brief_plan_table_has_the_four_new_columns(self):
        brief = (REPO / "templates" / "brief.md").read_text(encoding="utf-8")
        header = next(l for l in brief.splitlines() if l.startswith("| Step |"))
        for col in ["Owner", "Reviews or helps", "How", "Done when"]:
            self.assertIn(col, header)

    def test_the_gate_checks_the_piece_against_how_and_done_when(self):
        skill = (REPO / "skills" / "discovery-guide" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`how` and `done_when`", skill)
        self.assertIn("course change", skill)
        step = (STEPS_DIR / "1e-plan.md").read_text(encoding="utf-8")
        self.assertIn("owner", step)
        self.assertIn("reviewers", step)


class TestShareable(unittest.TestCase):
    """R24: the snapshot is one file that loads nothing from outside."""

    FILES = ["share.html", "share-onepager.html"]

    def test_the_templates_exist_and_load_nothing_external(self):
        for name in self.FILES:
            body = (REPO / "templates" / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertNotIn("http", body)
                self.assertNotRegex(body, r"(?i)<link\b|<script\b|@import|url\(|<img\b|<iframe\b")
                self.assertIn("prefers-color-scheme: dark", body)
                self.assertIn("@media print", body)

    def test_the_guide_offers_the_snapshot_at_gates_and_session_end(self):
        skill = (REPO / "skills" / "discovery-guide" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("shareable snapshot", skill)
        self.assertIn("every gate close", skill)
        self.assertIn("end of a work session", skill)
        self.assertIn("share/YYYY-MM-DD-<slug>.html", skill)

    def test_the_snapshot_never_carries_internal_material(self):
        skill = (REPO / "skills" / "discovery-guide" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("no assumptions", skill)
        self.assertIn("consent", skill)

    def test_share_is_not_routed_or_budgeted(self):
        self.assertNotIn("share/", BUDGETS.read_text(encoding="utf-8").split("budgets:")[1]
                         .split("# Files with no line budget")[0])
        editor = (REPO / "agents" / "editor.md").read_text(encoding="utf-8")
        self.assertIn("`share/`", editor)


class TestGatesAndReviewers(unittest.TestCase):
    """One owner per piece, seeded model checkers, two council modes, one checkpoint page."""

    def read(self, *parts):
        return (REPO.joinpath(*parts)).read_text(encoding="utf-8")

    def test_the_checkpoint_page_is_one_file_with_the_four_buttons(self):
        body = self.read("templates", "checkpoint.html")
        self.assertNotIn("http", body)
        self.assertNotRegex(body, r"(?i)<link\b|@import|url\(|<img\b|<iframe\b|<script[^>]*\bsrc=")
        self.assertIn("prefers-color-scheme: dark", body)
        self.assertIn("@media print", body)
        for choice in ["Advance", "Deepen", "Question", "Council"]:
            self.assertIn(f'data-choice="{choice}"', body)
        for word in ["data-ref", "Already corrected", "Copy decisions", "Owns:"]:
            self.assertIn(word, body)

    def test_the_checkpoint_page_is_named_where_the_gate_is_run(self):
        step = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        skill = self.read("skills", "discovery-guide", "SKILL.md")
        for text in (step, skill):
            self.assertIn("templates/checkpoint.html", text)
        self.assertIn("second round brings only what is new", step.lower())

    def test_the_seeded_rule_lives_in_one_place_and_the_others_point_at_it(self):
        step = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        self.assertEqual(step.count("### Every model checker: seeded, and the right tier"), 1)
        self.assertIn("No seed caught, no gate", step)
        for name in ["7c-validation-debrief.md", "8a-report.md", "3a-guide.md", "7a-validation-guide.md"]:
            with self.subTest(step=name):
                self.assertIn("Every model checker", self.read("workflows", "user-discovery", "steps", name))

    def test_a_clip_is_checked_like_a_quote(self):
        step = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        self.assertIn("A video or audio clip is a quote", step)

    def test_sense_checks_never_go_to_the_small_model(self):
        step = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        self.assertIn("A small model never runs a check of sense", step)

    def test_sub_stages_are_one_at_a_time(self):
        step = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        for phrase in ["One owner per piece", "One sub-stage at a time", "preliminary",
                       "if you don't decide, I'll continue", "Compressed mode"]:
            self.assertIn(phrase, step)
        self.assertIn("One sub-stage at a time", self.read("skills", "discovery-guide", "SKILL.md"))

    def test_the_council_has_two_modes_and_no_new_agent_files(self):
        council = self.read("agents", "council.md")
        for phrase in ["## Two modes", "## Review mode", "Variant: lateral guests",
                       "N reviewers said this", "Never reopens it", "hypotheses, not evidence",
                       "Simulated client validator", "The blind panel"]:
            self.assertIn(phrase, council)
        for lens in ["Client reader", "Editor", "Designer", "Person from the studied audience",
                     "Verifier", "Finder of the forgotten", "Clip reviewer"]:
            self.assertIn(f"| {lens} |", council)
        roster = {p.stem for p in (REPO / "agents").glob("*.md")}
        for name in ["reviewer", "validator", "simulated-client", "panel"]:
            self.assertNotIn(name, roster)


class TestOneFileOneJob(unittest.TestCase):
    """R19: every file the user opens writes only what is its own."""

    def test_every_template_opens_with_an_owns_line(self):
        missing = []
        for name in OWNED_TEMPLATES:
            text = (REPO / "templates" / f"{name}.md").read_text(encoding="utf-8")
            if not re.search(r"^Owns: .+ Does not own: .+→", text, re.M):
                missing.append(name)
        self.assertEqual(missing, [], "templates with no Owns / Does not own line")

    def test_profiles_keeps_only_the_interview_subject(self):
        text = (REPO / "templates" / "profiles.md").read_text(encoding="utf-8")
        self.assertNotIn("User vs", text)
        self.assertNotIn("Coverage plan", text)
        self.assertNotIn("Sample risks", text)

    def test_moved_sections_have_a_new_home(self):
        brief = (REPO / "templates" / "brief.md").read_text(encoding="utf-8")
        self.assertIn("## Who is who", brief)
        knowledge = (REPO / "templates" / "knowledge.md").read_text(encoding="utf-8")
        self.assertIn("Who answers it", knowledge)
        recruiting = (REPO / "templates" / "recruiting.md").read_text(encoding="utf-8")
        self.assertIn("## Sample risks", recruiting)

    def test_the_guide_template_carries_no_research_criteria(self):
        text = (REPO / "templates" / "guide.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("coverage plan", text)
        self.assertNotIn("learning question", text)

    def test_the_skill_states_the_principle(self):
        skill = (REPO / "skills" / "discovery-guide" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("One file, one job", skill)

    def test_the_editor_routes_by_the_owns_line(self):
        editor = (REPO / "agents" / "editor.md").read_text(encoding="utf-8")
        self.assertIn("Owns:", editor)


class TestGuideStructureAndCopies(unittest.TestCase):
    """The guide is built structure first, written by rules, and copied by script."""

    def read(self, *parts):
        return (REPO.joinpath(*parts)).read_text(encoding="utf-8")

    def test_the_structure_comes_before_the_questions(self):
        step = self.read("workflows", "user-discovery", "steps", "3a-guide.md")
        self.assertIn("## First, the structure", step)
        self.assertLess(step.index("## First, the structure"), step.index("## Recommended structure"))
        for phrase in ["guide-braindump.md", "generative mode", "it never blocks"]:
            self.assertIn(phrase, step)

    def test_the_twelve_writing_rules_are_numbered_one_to_twelve(self):
        step = self.read("workflows", "user-discovery", "steps", "3a-guide.md")
        block = step[step.index("## Rules for writing the questions"):step.index("## Exercises")]
        self.assertEqual(re.findall(r"^(\d+)\. \*\*", block, re.M), [str(n) for n in range(1, 13)])

    def test_the_guide_template_opens_with_owns_then_the_sections_table(self):
        lines = self.read("templates", "guide.md").splitlines()
        owns = next(i for i, l in enumerate(lines) if l.startswith("Owns:"))
        table = next(i for i, l in enumerate(lines) if l.startswith("| # |"))
        first_block = next(i for i, l in enumerate(lines) if l.startswith("### "))
        self.assertLess(owns, table)
        self.assertLess(table, first_block)
        self.assertLessEqual(table - owns, 5, "the table goes right under the Owns line")

    def test_the_guide_template_has_a_protected_exercise_with_a_fixed_prompt(self):
        text = self.read("templates", "guide.md")
        for phrase in ["<!-- annex", "<!-- end annex -->", "Prompt:", "Feeds:",
                       "never reworded", "Piloted", "Minimum sessions"]:
            self.assertIn(phrase, text)

    def test_exercises_are_piloted_fixed_protected_and_counted(self):
        step = self.read("workflows", "user-discovery", "steps", "3a-guide.md")
        for phrase in ["Pilot it before the field", "fixed in writing", "never cut for time",
                       "Declare the minimum"]:
            self.assertIn(phrase, step)
        debrief = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        self.assertIn("not enough", debrief)
        card_sort = self.read("templates", "card-sort.md")
        for phrase in ["Piloted", "Minimum", "not enough"]:
            self.assertIn(phrase, card_sort)

    def test_the_expert_consult_names_its_bias_and_keeps_hypotheses(self):
        text = self.read("templates", "expert-consult.md")
        for phrase in ["witness", "sample bias", "hypothesis for the field"]:
            self.assertIn(phrase, text)
        step = self.read("workflows", "user-discovery", "steps", "3a-guide.md")
        self.assertIn("--add expert_consult", step)
        sys.path.insert(0, str(REPO / "scripts"))
        import init_project
        self.assertIn("expert_consult", init_project.LAZY)

    def test_the_export_script_is_named_where_the_guide_is_used(self):
        for parts in [("workflows", "user-discovery", "steps", "3a-guide.md"),
                      ("workflows", "user-discovery", "steps", "3b-process.md"),
                      ("templates", "process.md"), ("templates", "interview-prep.md")]:
            with self.subTest(file=parts[-1]):
                self.assertIn("export_guide.py", self.read(*parts))
        self.assertTrue((REPO / "scripts" / "export_guide.py").exists())

    def test_the_workflow_runs_the_export_suite(self):
        workflow = self.read(".github", "workflows", "tests.yml")
        self.assertIn("tests/test_export_guide.py", workflow)


class TestMeetingCoverageStep(unittest.TestCase):
    """Step 1f: map a client meeting to the files before editing any of them."""

    def read(self, *parts):
        return (REPO.joinpath(*parts)).read_text(encoding="utf-8")

    def test_the_step_is_declared_on_demand_without_a_gate(self):
        step = state_steps()["meeting_coverage"]
        self.assertEqual(step["phase"], "1")
        self.assertEqual(step["gate"], "false")
        self.assertEqual(step["on_demand"], "true")
        self.assertIn("1f-meeting-coverage.md", step_files())

    def test_the_step_waits_for_the_researchers_ok_before_editing(self):
        text = self.read("workflows", "user-discovery", "steps", "1f-meeting-coverage.md")
        for phrase in ["decide where every point lands", "OK", "tensions", "stays here", "`pending: why`"]:
            self.assertIn(phrase, text)
        self.assertLess(text.index("Show the matrix"), text.index("Only then edit"))

    def test_the_skill_lists_the_step_in_order_and_counts_the_files(self):
        skill = self.read("skills", "discovery-guide", "SKILL.md")
        self.assertIn("`1f-meeting-coverage.md`", skill)
        self.assertIn("Nineteen step files", skill)
        self.assertEqual(len(step_files()), 19)

    def test_the_brief_tells_where_the_clients_data_goes(self):
        brief = self.read("templates", "brief.md")
        self.assertIn("The brief holds the decision, not the client's data", brief)
        self.assertIn("knowledge.md", brief)
        self.assertIn("meeting-coverage.md", brief)


class TestPresentationStage(unittest.TestCase):
    """Step 5b: a sample before the deck, a report that layers, pieces built by script."""

    def read(self, *parts):
        return (REPO.joinpath(*parts)).read_text(encoding="utf-8")

    def test_the_step_is_declared_on_demand_with_a_gate_and_a_file(self):
        step = state_steps()["presentation"]
        self.assertEqual(step["phase"], "5")
        self.assertEqual(step["gate"], "true")
        self.assertEqual(step["on_demand"], "true")
        self.assertEqual(step["file"], "5-debrief/presentation.md")
        self.assertIn("5b-presentation.md", step_files())
        self.assertEqual(state_phase_steps()[5], ["debrief", "presentation"])
        lazy, _ = lazy_map()
        self.assertEqual(lazy["presentation"][1], "5-debrief/presentation.md")
        self.assertEqual(lazy["meeting_claims"][1], "5-debrief/meeting-claims.md")

    def test_the_sample_comes_before_the_deck_and_a_draft_is_a_draft(self):
        text = self.read("workflows", "user-discovery", "steps", "5b-presentation.md")
        for phrase in ["A sample before the deck, always", "real content", "Draft, not mock-up",
                       "finishing work", "does not start until the sample is accepted",
                       "found in slide, left out", "A count is not a slide", "what is left to measure",
                       "focus of the analysis"]:
            self.assertIn(phrase, text)
        self.assertLess(text.index("Build the sample"), text.index("Build the deck by script"))

    def test_the_script_rules_and_the_rewrite_rule_live_in_5b_and_8a_names_them(self):
        step = self.read("workflows", "user-discovery", "steps", "5b-presentation.md")
        report = self.read("workflows", "user-discovery", "steps", "8a-report.md")
        for phrase in ["The canonical is a Markdown file", "by number or by pattern",
                       "map from IDs to titles", "never runs on a literal quote",
                       "table of changes", "reopens a closed decision"]:
            self.assertIn(phrase, step)
        for phrase in ["table of changes", "never the file", "the correction goes to the Markdown",
                       "--source", "UNLINKED", "--titles-from"]:
            self.assertIn(phrase, report)
        self.assertIn("--source", step)

    def test_the_report_layers_on_what_was_accepted(self):
        report = self.read("workflows", "user-discovery", "steps", "8a-report.md")
        for phrase in ["as it was presented", "new layer", "go **last**", "tasks of the script",
                       "The cover names the design challenge", "table of verdicts",
                       "what is left to measure"]:
            self.assertIn(phrase, report)
        summary = self.read("templates", "summary.md")
        for heading in ["## The design challenge", "## What was presented and accepted",
                        "## What is left to measure", "## Adjustments for this version"]:
            self.assertIn(heading, summary)
        self.assertGreater(summary.index("## Adjustments for this version"),
                           summary.index("## What is left to measure"))

    def test_the_meeting_claims_step_is_named_in_5a_and_the_template_has_its_tables(self):
        step = self.read("workflows", "user-discovery", "steps", "5a-debrief.md")
        for phrase in ["what I said vs. the evidence", "meeting-claims.md", "cross against the whole list",
                       "corrected with the client"]:
            self.assertIn(phrase, step)
        template = self.read("templates", "meeting-claims.md")
        for phrase in ["does not hold", "to confirm", "A list the client voted or ranked", "no evidence"]:
            self.assertIn(phrase, template)

    def test_the_skill_and_the_architecture_name_the_stage(self):
        self.assertIn("`5b-presentation.md`", self.read("skills", "discovery-guide", "SKILL.md"))
        self.assertIn("5b", self.read("docs", "method-architecture.md"))


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
        self.assertEqual(len(install), 11,
                         "the README and the skill both say eleven files install")
        mine = [d for d in install.values()
                if not d.startswith("_engine/") and d not in {"AGENTS.md", "CLAUDE.md"}]
        self.assertEqual(sorted(mine), ["0-README.md", "1-desk-research/brief.md",
                                        "2-profiling/0-README.md", "3-guide/0-README.md",
                                        "4-field/0-README.md", "4-field/notes.md",
                                        "5-debrief/0-README.md"])


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


class TestPathsAndNames(unittest.TestCase):
    """What a step says about a gate, a path or the method root is true."""

    def gate_section(self, name):
        text = (STEPS_DIR / name).read_text(encoding="utf-8")
        match = re.search(r"^## Gate\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        return match.group(1) if match else ""

    def test_a_step_without_a_gate_says_so(self):
        """state.yaml's gate: false and the step's Gate section agree."""
        by_phase = state_phase_steps()
        order = [s for n in sorted(by_phase) for s in by_phase[n]]
        steps = state_steps()
        for step, name in zip(order, step_files()):
            with self.subTest(step=step, file=name):
                says_no_gate = "no gate" in self.gate_section(name).lower()
                self.assertEqual(says_no_gate, steps[step]["gate"] == "false",
                                 f"{name}: gate is {steps[step]['gate']} in state.yaml")

    def test_one_placeholder_for_the_method_root(self):
        tracked = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                                 text=True).stdout.split()
        offenders = []
        for rel in tracked:
            if rel == "CHANGELOG.md" or rel.endswith("test_consistency.py"):
                continue
            path = REPO / rel
            if path.suffix not in {".md", ".py", ".yaml", ".html", ".sh"}:
                continue
            body = path.read_text(encoding="utf-8", errors="ignore")
            for token in ("{skill-root}", "{method-root}", "<skill-root>"):
                if token in body:
                    offenders.append(f"{rel} -> {token}")
        self.assertEqual(offenders, [], "write <method-root>:\n" + "\n".join(offenders))

    @unittest.skipUnless(shutil.which("bash"), "install.sh needs bash")
    def test_the_install_holds_every_path_the_steps_name(self):
        """install.sh puts the method agents in agents/ and process-interview next to
        the guide, so agents/council.md and the skill the steps run both exist."""
        home = Path(tempfile.mkdtemp())
        try:
            env = dict(os.environ, HOME=str(home))
            result = subprocess.run(["bash", str(REPO / "install.sh"), "claude"], env=env,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            dest = home / ".claude" / "skills" / "discovery-guide"
            self.assertTrue((home / ".claude" / "skills" / "process-interview" / "SKILL.md").exists())
            self.assertTrue((dest / "agents" / "openai.yaml").exists())
            sources = [*STEPS_DIR.glob("*.md"), REPO / "skills" / "discovery-guide" / "SKILL.md"]
            named = set()
            for source in sources:
                body = source.read_text(encoding="utf-8")
                named |= set(re.findall(r"`((?:agents|templates|scripts|references)/[\w.-]+\.\w+)`", body))
            self.assertGreater(len(named), 10)
            missing = sorted(n for n in named if not (dest / n).exists())
            self.assertEqual(missing, [], "named in a step, missing from the install")
        finally:
            shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
