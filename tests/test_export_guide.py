#!/usr/bin/env python3
"""Tests for scripts/export_guide.py: the client export and the prep sheet.

Run:  python3 tests/test_export_guide.py

Both copies come from the master guide, so the tests plant what must NOT travel (the
Owns line, internal codes, the interviewer's notes, what follows the exercise annex)
and what must (the questions, word for word, in order). Fixtures are invented and
generic: a booking app for a small clinic.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "export_guide.py"
INIT = REPO / "scripts" / "init_project.py"
sys.path.insert(0, str(REPO / "scripts"))
import export_guide  # noqa: E402

GUIDE = """\
# Interview guide

Owns: interview questions and blocks, nothing else. Does not own: the protocol → `process.md`.

| # | Section | Min | Priority | Covers |
|---|---|---:|---|---|
| 1 | Start and consent | 5 | Must | S-004 |
| 2 | The last booking | 15 | Must | Request 2 |
| 3 | Ordering exercise | 12 | Must | NS-010 |
| 4 | Closing | 3 | If there is time | |

Master note that never leaves: see A-012 and the pilot.

### 1. Start and consent

Goal: they understand the purpose and feel at ease.

Thanks for coming. We are looking at how people book a visit; we are not selling anything. May we record?
*Say it in your own voice, not mine.*

### 2. The last booking

Goal: rebuild the real story.

- Think of the last time you booked a visit. Tell me that story from the start. → And then? (T9)
  *Stages are your map. Never say them out loud.*
- Who else was involved? → What did they do?
- Did you cancel anything? → Which one? What happened?
  - What did you do next?

### 3. Ordering exercise

Goal: what they put first, aloud.
<!-- annex: what the client sees -->
Prompt: If a clinic page had this information, what would you want on it, and in what order?
Cards or items: Opening hours · Price list · How to cancel · Parking
Minutes: 12
<!-- end annex -->
*Never reword the prompt live.*
Feeds: the page order (PAT-01). Minimum sessions: 3.
- Why that card first? → And the last one?

### 4. Closing

- Is there anything I did not ask? → What?
"""

PREP_QUESTIONS = [
    "Think of the last time you booked a visit. Tell me that story from the start. → And then? (T9)",
    "Who else was involved? → What did they do?",
    "Did you cancel anything? → Which one? What happened?",
    "What did you do next?",
    "Why that card first? → And the last one?",
    "Is there anything I did not ask? → What?",
]


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          text=True, cwd=cwd)


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, str(INIT), "--project-root", str(self.tmp),
                        "--method-root", str(REPO)], capture_output=True, check=True)
        self.disc = self.tmp / "discovery"
        self.guide = self.disc / "3-guide" / "guide.md"
        self.guide.parent.mkdir(exist_ok=True)
        self.guide.write_text(GUIDE, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def export(self, *extra):
        return run("--project-root", str(self.tmp), "--method-root", str(REPO), *extra)

    def client_text(self, fmt="md"):
        return (self.disc / "share" / f"guide-for-client.{fmt}").read_text(encoding="utf-8")


class TestParse(unittest.TestCase):
    def test_sections_questions_and_notes_are_told_apart(self):
        guide = export_guide.parse(GUIDE)
        self.assertEqual([s.num for s in guide.sections], ["1", "2", "3", "4"])
        self.assertEqual(export_guide.count_questions(guide), len(PREP_QUESTIONS))
        self.assertEqual(len(guide.rows), 4)
        notes = [i.text for s in guide.sections for i in s.items if i.kind == "note"]
        self.assertTrue(any("Stages are your map" in n for n in notes))

    def test_only_a_line_wholly_in_italics_is_a_note(self):
        self.assertTrue(export_guide.is_note("*a note*"))
        self.assertFalse(export_guide.is_note("**bold** text"))
        self.assertFalse(export_guide.is_note("Ask *why* every time"))

    def test_the_table_is_read_by_column_not_by_header_language(self):
        spanish = GUIDE.replace("| # | Section | Min | Priority | Covers |",
                                "| N | Sección | Minutos | Prioridad | Cubre |")
        rows = export_guide.parse(spanish).rows
        self.assertEqual(rows[0][:4], ("1", "Start and consent", "5", "Must"))

    def test_no_sections_is_refused(self):
        with self.assertRaises(SystemExit):
            export_guide.parse("# Guide\n\nJust talk.\n")


class TestClientExport(Project):
    def test_what_must_not_travel_does_not(self):
        result = self.export("--client")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.client_text()
        self.assertNotIn("Owns:", text)
        self.assertNotIn("Does not own", text)
        self.assertNotIn("T9", text)
        self.assertNotIn("A-012", text)
        self.assertNotIn("PAT-01", text)
        self.assertNotIn("Stages are your map", text)
        self.assertNotIn("Never reword the prompt", text)
        self.assertNotIn("Say it in your own voice", text)
        self.assertNotIn("Covers", text)
        self.assertNotIn("Priority", text)
        self.assertNotIn("Feeds", text)

    def test_what_must_travel_does(self):
        self.export("--client")
        text = self.client_text()
        for q in ["Who else was involved? → What did they do?",
                  "Did you cancel anything? → Which one? What happened?",
                  "- What did you do next?"]:
            self.assertIn(q, text)
        self.assertIn("Thanks for coming", text)
        self.assertIn("| 2 | The last booking | 15 |", text)
        self.assertIn("Total: about 35 minutes.", text)

    def test_the_annex_shows_the_exercise(self):
        self.export("--client")
        text = self.client_text()
        self.assertIn("see Annex A", text)
        annex = text[text.index("## Annex A"):]
        self.assertIn("If a clinic page had this information", annex)
        for card in ["Opening hours", "Price list", "How to cancel", "Parking"]:
            self.assertIn(f"- {card}", annex)
        self.assertIn("12", annex)

    def test_a_code_left_in_the_text_stops_the_export(self):
        self.guide.write_text(GUIDE.replace("Who else was involved?",
                                            "Who else was involved in INT-003?"), encoding="utf-8")
        result = self.export("--client")
        self.assertEqual(result.returncode, 1)
        self.assertIn("INT-003", result.stdout)
        self.assertFalse((self.disc / "share" / "guide-for-client.md").exists())

    def test_allow_lets_a_word_through(self):
        self.guide.write_text(GUIDE.replace("Parking", "H20 water"), encoding="utf-8")
        self.assertEqual(self.export("--client").returncode, 1)
        self.assertEqual(self.export("--client", "--allow", "H20").returncode, 0)

    def test_html_is_one_printable_page_that_loads_nothing(self):
        result = self.export("--client", "--format", "html")
        self.assertEqual(result.returncode, 0, result.stdout)
        body = self.client_text("html")
        self.assertNotIn("http", body)
        self.assertNotRegex(body, r"(?i)<link\b|<script\b|@import|url\(|<img\b")
        self.assertIn("@media print", body)
        self.assertIn("<h2>Annex A", body)
        self.assertIn("<li>Price list</li>", body)

    def test_an_html_special_character_is_escaped(self):
        self.guide.write_text(GUIDE.replace("Parking", "Fees <b> & more"), encoding="utf-8")
        self.export("--client", "--format", "html")
        self.assertIn("Fees &lt;b&gt; &amp; more", self.client_text("html"))

    def test_the_shipped_template_exports_clean(self):
        shutil.copyfile(REPO / "templates" / "guide.md", self.guide)
        result = self.export("--client")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Owns:", self.client_text())


class TestPrepSheet(Project):
    def prep(self, name="INT-004-ana-lopez"):
        return self.disc / "4-field" / "_prep" / f"{name}-prep.md"

    def checkboxes(self, text):
        return [l.strip()[6:] for l in text.splitlines() if l.strip().startswith("- [ ] ")]

    def test_the_questions_are_copied_word_for_word_in_order(self):
        result = self.export("--prep", "INT-004-ana-lopez")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.checkboxes(self.prep().read_text(encoding="utf-8")), PREP_QUESTIONS)

    def test_the_route_table_carries_priority_and_minutes_from_the_master(self):
        self.export("--prep", "INT-004-ana-lopez")
        text = self.prep().read_text(encoding="utf-8")
        self.assertIn("| 2 | The last booking | Must | 15 |", text)
        self.assertIn("| 4 | Closing | If there is time | 3 |", text)

    def test_the_interviewers_notes_and_the_exercise_travel_to_the_prep(self):
        self.export("--prep", "INT-004-ana-lopez")
        text = self.prep().read_text(encoding="utf-8")
        self.assertIn("Stages are your map", text)
        self.assertIn("Prompt: If a clinic page", text)
        self.assertIn("Never reword the prompt live", text)

    def test_a_second_run_changes_nothing(self):
        self.export("--prep", "INT-004-ana-lopez")
        first = self.prep().read_text(encoding="utf-8")
        self.export("--prep", "INT-004-ana-lopez")
        self.assertEqual(self.prep().read_text(encoding="utf-8"), first)
        self.assertEqual(first.count("<!-- guide:start -->"), 1)

    def test_the_rest_of_the_sheet_is_kept_when_the_master_changes(self):
        self.export("--prep", "INT-004-ana-lopez")
        text = self.prep().read_text(encoding="utf-8")
        self.prep().write_text(text.replace("- Pending. *(three to five bullets)*",
                                            "- A nurse who books for three doctors."),
                               encoding="utf-8")
        self.guide.write_text(GUIDE.replace("Who else was involved?", "Who else took part?"),
                              encoding="utf-8")
        self.export("--prep", "INT-004-ana-lopez")
        text = self.prep().read_text(encoding="utf-8")
        self.assertIn("A nurse who books for three doctors.", text)
        self.assertIn("Who else took part? → What did they do?", text)
        self.assertNotIn("Who else was involved?", text)

    def test_a_sheet_with_marks_is_not_overwritten_without_force(self):
        self.export("--prep", "INT-004-ana-lopez")
        text = self.prep().read_text(encoding="utf-8").replace("- [ ] Who else", "- [x] Who else", 1)
        self.prep().write_text(text, encoding="utf-8")
        self.guide.write_text(GUIDE.replace("Closing", "Wrap-up"), encoding="utf-8")
        result = self.export("--prep", "INT-004-ana-lopez")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--force", result.stdout)
        self.assertIn("- [x] Who else", self.prep().read_text(encoding="utf-8"))
        self.assertEqual(self.export("--prep", "INT-004-ana-lopez", "--force").returncode, 0)
        self.assertNotIn("- [x]", self.prep().read_text(encoding="utf-8"))

    def test_a_prep_sheet_can_be_named_by_path(self):
        target = self.tmp / "mine-prep.md"
        self.assertEqual(self.export("--prep", str(target)).returncode, 0)
        self.assertEqual(self.checkboxes(target.read_text(encoding="utf-8")), PREP_QUESTIONS)

    def test_a_bad_name_is_refused_with_a_reason(self):
        result = self.export("--prep", "ana lopez")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("base name", result.stderr + result.stdout)


class TestUsage(Project):
    def test_asking_for_nothing_is_a_usage_error(self):
        self.assertEqual(self.export().returncode, 2)

    def test_a_missing_guide_says_how_to_create_it(self):
        self.guide.unlink()
        result = self.export("--client")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--add interview_guide", result.stderr)

    def test_a_guide_with_no_question_is_refused(self):
        self.guide.write_text("# G\n\n### 1. Start\n\nJust a paragraph.\n", encoding="utf-8")
        result = self.export("--client")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no question", result.stderr)

    def test_the_shipped_prep_template_takes_the_markers(self):
        template = (REPO / "templates" / "interview-prep.md").read_text(encoding="utf-8")
        self.assertIn("## The route", template)
        self.assertIn("## The questions", template)
        self.assertIsNotNone(re.search(r"^- \[ \] ", template, re.M))


if __name__ == "__main__":
    unittest.main()
