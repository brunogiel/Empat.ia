#!/usr/bin/env python3
"""Tests for scripts/check_share.py: a folder of shareable pieces seeded with errors.

Run:  python3 tests/test_check_share.py

The folder holds one clean piece and one piece per planted error: a vetoed quote, a
false count, a loose code, a block marked as internal and speaker notes. The script
has to catch each one, in one command, and has to pass the clean piece. Fixtures are
invented and generic.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_share.py"
sys.path.insert(0, str(REPO / "scripts"))
import check_share  # noqa: E402

TRANSCRIPT = """\
Microphone: Tell me about the last time you booked a trip.
System audio: I usually start on my phone, on the train, and I compare three or four sites.
Microphone: And then what happens?
System audio: Then I wait. I never book the same day because prices might drop tomorrow.
Microphone: Do you ever ask friends for advice?
System audio: My sister always knows a cheaper way, so I text her first.
"""

VETOED_QUOTE = "My sister always knows a cheaper way, so I text her first."
GOOD_QUOTE = "I never book the same day because prices might drop tomorrow."

EVIDENCE = f"""\
| Evidence ID | Interview | Profile | Type | Evidence | Location | Tags | Reading | Confidence | Use in synthesis |
|---|---|---|---|---|---|---|---|---|---|
| INT-001-01 | INT-001 | A | quote | «{GOOD_QUOTE}» | 02:10 | t | r | high | yes |
| INT-001-02 | INT-001 | A | quote | «{VETOED_QUOTE}» | 04:00 | t | r | low | vetoed: induced |
| INT-001-03 | INT-001 | A | fact | The sister charges a monthly fee for her advice [not for the report] | 05:00 | t | r | low | no |
"""

FINDINGS = """\
# Findings

| ID | Pattern | Evidence | Who does not show it |
|---|---|---|---|
| PAT-01 | Compares prices on several sites first | INT-001-03, INT-002-01, INT-004-02 | |
| PAT-02 | Waits a day before booking | INT-001-05, INT-005-06 | |

The reviewer thinks the whole timeline is wrong and has not said why.
<!-- not for the report -->
The pilot group was recruited from the sister company of the sponsor.
Nobody outside the sponsor saw the early prototype in this room.
<!-- end not for the report -->
"""

LOG = """\
# Verification log

## What already went out

| File | To whom | When | What it claims | State |
|---|---|---|---|---|
| clean.html | the team | 2026-01-10 | prices are compared | current |
| old.md | the sponsor | 2026-01-03 | an early reading | outdated |
"""

CLEAN = "<html><body><h1>What we saw</h1><p>People compare several sites and wait a day.</p></body></html>"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ("4-field/_raw", "5-debrief", "_engine", "share"):
            (self.root / folder).mkdir(parents=True)
        (self.root / "4-field/_raw/INT-001-trip-transcript.txt").write_text(TRANSCRIPT, encoding="utf-8")
        (self.root / "_engine/evidence.md").write_text(EVIDENCE, encoding="utf-8")
        (self.root / "5-debrief/findings.md").write_text(FINDINGS, encoding="utf-8")
        (self.root / "5-debrief/verification-log.md").write_text(LOG, encoding="utf-8")
        self.put("clean.html", CLEAN)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, text):
        path = self.root / "share" / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True)


class TestCleanFolder(Fixture):
    def test_a_clean_piece_passes(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("nothing flagged", result.stdout)

    def test_no_share_folder_is_not_an_error(self):
        (self.root / "share" / "clean.html").unlink()
        (self.root / "share").rmdir()
        result = self.run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertIn("Nothing has gone out", result.stdout)

    def test_a_folder_that_was_asked_for_and_is_missing_is_exit_2(self):
        self.assertEqual(self.run_cli("--share", str(self.root / "nope")).returncode, 2)


class TestSeededErrors(Fixture):
    def test_a_vetoed_quote_in_a_shared_page_fails(self):
        self.put("vetoed.html", f"<p>One person said: «{VETOED_QUOTE}»</p>")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("VETOED", result.stdout)
        self.assertIn("induced", result.stdout)

    def test_a_vetoed_quote_in_markdown_fails(self):
        self.put("note.md", f"A person told us \"{VETOED_QUOTE}\" last week.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("VETOED", result.stdout)

    def test_a_quote_that_is_not_in_the_transcript_fails(self):
        self.put("made-up.html",
                 '<blockquote data-int="INT-001">I would pay double for a site that answers at midnight.'
                 "</blockquote>")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL", result.stdout)

    def test_a_false_count_fails(self):
        self.put("counts.md", "PAT-02 is held by 4 of 5 people.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("MISMATCH", result.stdout)

    def test_a_loose_code_fails_with_its_line(self):
        self.put("codes.md", "First line.\nThe pattern PAT-01 and the note INT-003-12 explain it.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("codes.md:2", result.stdout)
        self.assertIn("«PAT-01»", result.stdout)
        self.assertIn("«INT-003-12»", result.stdout)

    def test_short_codes_and_working_labels_fail(self):
        for text, token in (("See H04 for the rest.", "H04"), ("The A-023 bet held.", "A-023"),
                            ("TODO fill this in", "TODO"), ("Closed at GATE 2.", "GATE 2")):
            with self.subTest(token=token):
                self.put("c.md", text + "\n")
                result = self.run_cli()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(f"«{token}»", result.stdout)

    def test_a_sentence_in_normal_case_is_not_a_code(self):
        self.put("fine.md", "Gate two closed. We saw it in step 5. Page A4 is the cover.\n")
        self.assertEqual(self.run_cli().returncode, 0)

    def test_a_code_inside_a_tag_or_a_script_is_not_read_by_a_person(self):
        self.put("quiet.html", '<p id="INT-001" class="H04">Plain text here.</p>'
                               "<style>.A-023 { color: #F00 }</style><script>var PAT-01 = 1</script>")
        self.assertEqual(self.run_cli().returncode, 0)

    def test_text_marked_internal_in_a_canonical_file_cannot_leave(self):
        self.put("leak.html",
                 "<p>The pilot group was recruited from the sister company of the sponsor.</p>")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("INTERNAL", result.stdout)
        self.assertIn("findings.md", result.stdout)

    def test_a_marked_table_row_cannot_leave_either(self):
        self.put("leak.md", "Our advice came from someone: the sister charges a monthly fee for her advice.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("INTERNAL", result.stdout)
        self.assertIn("evidence.md", result.stdout)

    def test_the_mark_itself_cannot_be_in_a_shared_piece(self):
        self.put("tag.md", "A line of text. [not for the report]\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn("carries the 'not for the report' mark", result.stdout)

    def test_unmarked_text_of_a_canonical_file_may_be_shared(self):
        self.put("fine.md", "The reviewer thinks the whole timeline is wrong and has not said why.\n")
        self.assertEqual(self.run_cli().returncode, 0)

    def test_speaker_notes_fail_unless_kept(self):
        self.put("deck.html", '<section><h2>Findings</h2><aside class="notes">Say the thing.</aside></section>')
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("NOTES", result.stdout)
        self.assertEqual(self.run_cli("--keep-notes").returncode, 0)

    def test_every_planted_error_is_caught_in_one_run(self):
        self.put("a.html", f"<p>«{VETOED_QUOTE}»</p>")
        self.put("b.md", "PAT-02 is held by 4 of 5 people.\n")
        self.put("c.html", "<p>The pilot group was recruited from the sister company of the sponsor.</p>")
        self.put("d.html", '<aside class="notes">x</aside>')
        out = self.run_cli().stdout
        for verdict in ("VETOED", "MISMATCH", "CODE", "INTERNAL", "NOTES"):
            self.assertIn(verdict, out)


class TestExceptions(Fixture):
    def test_an_allowed_token_passes(self):
        self.put("name.md", "The H20 product line was part of the study.\n")
        self.assertEqual(self.run_cli().returncode, 1)
        self.assertEqual(self.run_cli("--allow", "H20").returncode, 0)

    def test_a_pattern_exception_passes(self):
        self.put("iso.md", "The XY-123 model was part of the study.\n")
        self.assertEqual(self.run_cli().returncode, 1)
        self.assertEqual(self.run_cli("--allow", r"re:^XY-\d+$").returncode, 0)

    def test_the_exceptions_file_is_read(self):
        self.put("name.md", "The H20 product line was part of the study.\n")
        (self.root / "_engine" / "share-allow.txt").write_text("# names that look like codes\nH20\n", encoding="utf-8")
        self.assertEqual(self.run_cli().returncode, 0)

    def test_a_source_file_may_hold_codes_but_its_counts_are_checked(self):
        source = self.root / "8-source.md"
        source.write_text("PAT-02 is held by 2 of 5 people (INT-001-05).\n", encoding="utf-8")
        self.assertEqual(self.run_cli("--source", str(source)).returncode, 0)
        source.write_text("PAT-02 is held by 4 of 5 people (INT-001-05).\n", encoding="utf-8")
        result = self.run_cli("--source", str(source))
        self.assertEqual(result.returncode, 1)
        self.assertIn("MISMATCH", result.stdout)
        self.assertNotIn("CODE", result.stdout)


class TestLog(Fixture):
    def test_a_piece_missing_from_the_log_is_listed_and_fails_only_when_strict(self):
        self.put("new.md", "A fresh page with plain words.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("NOT_LOGGED", result.stdout)
        self.assertEqual(self.run_cli("--strict").returncode, 1)

    def test_an_outdated_piece_still_in_the_folder_is_listed(self):
        self.put("old.md", "An early reading in plain words.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertIn("OUTDATED", result.stdout)
        self.assertEqual(self.run_cli("--strict").returncode, 1)

    def test_the_log_table_is_read_by_state(self):
        rows = check_share.read_log(self.root / "5-debrief" / "verification-log.md")
        self.assertEqual(rows, {"clean.html": "current", "old.md": "outdated"})


class TestTitles(Fixture):
    """A title edited by hand in the piece and not in the canonical file is caught by script."""

    def canon(self):
        path = self.root / "canon.md"
        path.write_text("# Findings\n\n## 01 People compare several sites first\n\n"
                        "## 02 They wait a day before booking\n\n### Open questions\n", encoding="utf-8")
        return path

    def test_a_title_that_matches_passes(self):
        self.put("deck.html", "<h2>People compare several sites first</h2><h2>2. They wait a day before booking</h2>")
        result = self.run_cli("--titles-from", str(self.canon()))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_title_edited_by_hand_fails_with_the_canonical_one(self):
        self.put("deck.html", "<h2>People compare many sites first</h2>")
        result = self.run_cli("--titles-from", str(self.canon()))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("TITLE_DRIFT", result.stdout)
        self.assertIn("People compare several sites first", result.stdout)

    def test_the_same_finding_with_two_titles_in_one_piece_is_caught(self):
        self.put("deck.md", "## Summary\n\n### They wait a day before booking\n\n### They wait one day before they book\n")
        result = self.run_cli("--titles-from", str(self.canon()))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("deck.md:5", result.stdout)
        self.assertNotIn("deck.md:3", result.stdout)

    def test_a_heading_of_the_pieces_own_is_left_alone(self):
        self.put("deck.html", "<h1>What we saw in the round</h1><h2>Where to go next</h2>")
        self.assertEqual(self.run_cli("--titles-from", str(self.canon())).returncode, 0)

    def test_without_the_flag_titles_are_not_read(self):
        self.put("deck.html", "<h2>People compare many sites first</h2>")
        self.assertEqual(self.run_cli().returncode, 0)

    def test_a_missing_canonical_file_is_exit_2(self):
        self.assertEqual(self.run_cli("--titles-from", str(self.root / "nope.md")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
