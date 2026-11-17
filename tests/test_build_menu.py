#!/usr/bin/env python3
"""Does build_menu.py read the menu, add up the minutes and write the choices back?

Fixtures are invented: a booking app for a small clinic.

Run:  python3 tests/test_build_menu.py
"""

import contextlib
import io
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import build_menu as bm  # noqa: E402

MENU = """\
# Exercise menu

Owns: the long list. Does not own: the script → `tasks.md`.

Session length: 60 minutes
Reserve: 10 minutes

| ID | Exercise | Bet | Minutes | Where it comes from | Choice |
|---|---|---|---|---|---|
| E-01 | Book the earliest slot for a child | B-1 | 8 | the researcher | go |
| E-02 | Move an appointment you already have | B-1 | 5-7 | a panel reviewer | |
| E-03 | Find the clinic's opening hours | B-2 | 4 | the client | maybe |
| E-04 | Cancel and rebook in one go | B-2 | 12 | 3 of 4 reviewers | |
"""


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = bm.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class Parse(unittest.TestCase):
    def test_reads_length_reserve_and_rows(self):
        menu = bm.parse_menu(MENU)
        self.assertEqual((menu["length"], menu["reserve"]), (60, 10))
        self.assertEqual([r["id"] for r in menu["rows"]], ["E-01", "E-02", "E-03", "E-04"])

    def test_a_range_counts_at_its_upper_end(self):
        self.assertEqual(bm.parse_menu(MENU)["rows"][1]["minutes"], 7)

    def test_totals_split_go_from_go_plus_maybe(self):
        t = bm.totals(bm.parse_menu(MENU)["rows"])
        self.assertEqual(t, {"go": 8, "go_maybe": 12})

    def test_a_table_without_the_columns_is_refused(self):
        with self.assertRaises(bm.MenuError):
            bm.parse_menu("| ID | Exercise |\n|---|---|\n| E-01 | x |\n")

    def test_an_unknown_choice_is_refused(self):
        with self.assertRaises(bm.MenuError):
            bm.parse_menu(MENU.replace("| go |", "| yes |"))

    def test_a_row_without_minutes_is_refused(self):
        with self.assertRaises(bm.MenuError):
            bm.parse_menu(MENU.replace("| 4 |", "| soon |"))

    def test_the_template_parses(self):
        text = (REPO / "templates" / "exercise-menu.md").read_text(encoding="utf-8")
        menu = bm.parse_menu(text)
        self.assertGreaterEqual(len(menu["rows"]), 1)


class Apply(unittest.TestCase):
    def test_choices_land_in_the_choice_column_only(self):
        menu = bm.parse_menu(MENU)
        text, unknown = bm.apply_choices(menu, {"E-02": "go", "E-04": "no"})
        self.assertEqual(unknown, [])
        again = bm.parse_menu(text)
        self.assertEqual([r["choice"] for r in again["rows"]], ["go", "go", "maybe", "no"])
        self.assertEqual([r["exercise"] for r in again["rows"]],
                         [r["exercise"] for r in menu["rows"]])

    def test_an_id_the_menu_does_not_have_is_reported(self):
        _, unknown = bm.apply_choices(bm.parse_menu(MENU), {"E-09": "go"})
        self.assertEqual(unknown, ["E-09"])

    def test_choices_file_formats(self):
        got = bm.parse_choices("E-01: go\nE-02 maybe\n# comment\n\nE-03 = no\n")
        self.assertEqual(got, {"E-01": "go", "E-02": "maybe", "E-03": "no"})

    def test_a_bad_choice_line_is_refused(self):
        for bad in ("E-01: sure", "first one go"):
            with self.subTest(bad=bad), self.assertRaises(bm.MenuError):
                bm.parse_choices(bad)


class Page(unittest.TestCase):
    def test_the_page_is_self_contained_and_has_the_buttons(self):
        page = bm.build_page(bm.parse_menu(MENU))
        self.assertNotRegex(page, r'(?:src|href)="https?://')
        self.assertIn("prefers-color-scheme: dark", page)
        self.assertIn('name="viewport"', page)
        for choice in bm.CHOICES:
            self.assertEqual(page.count(f'data-v="{choice}"'), 4)
        self.assertIn('"length": 60', page)
        self.assertIn('"reserve": 10', page)

    def test_the_text_of_an_exercise_is_escaped(self):
        page = bm.build_page(bm.parse_menu(MENU.replace("Book the earliest", "<b>Book</b> the earliest")))
        self.assertNotIn("<b>Book</b>", page)
        self.assertIn("&lt;b&gt;Book&lt;/b&gt;", page)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.menu = self.tmp / "exercise-menu.md"
        self.menu.write_text(MENU, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_the_page_next_to_the_menu(self):
        code, out, _ = run(str(self.menu))
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "exercise-menu.html").exists())

    def test_apply_writes_back_and_reports_the_minutes(self):
        choices = self.tmp / "choices.txt"
        choices.write_text("E-02: go\nE-04: maybe\n", encoding="utf-8")
        code, out, _ = run(str(self.menu), "--apply", str(choices))
        self.assertEqual(code, 0)
        self.assertIn("go: 15 min", out)
        self.assertIn("go + maybe: 31 min", out)
        self.assertRegex(self.menu.read_text(encoding="utf-8"), r"\| E-02 \|.*\| go \|")

    def test_apply_with_an_unknown_id_writes_nothing(self):
        choices = self.tmp / "choices.txt"
        choices.write_text("E-09: go\n", encoding="utf-8")
        before = self.menu.read_text(encoding="utf-8")
        code, _, err = run(str(self.menu), "--apply", str(choices))
        self.assertEqual(code, 1)
        self.assertIn("E-09", err)
        self.assertEqual(self.menu.read_text(encoding="utf-8"), before)

    def test_a_missing_file_exits_two(self):
        code, _, err = run(str(self.tmp / "nope.md"))
        self.assertEqual(code, 2)
        self.assertIn("Cannot read", err)


if __name__ == "__main__":
    unittest.main()
