#!/usr/bin/env python3
"""Tests for scripts/check_counts.py: seeded errors the script has to catch.

Run:  python3 tests/test_check_counts.py

Each test plants one error (a count that drifted, a universal a transcript breaks, a
tick on two people, a strong pattern nobody read) and checks the script finds it. The
control is the clean input, which has to pass. Fixtures are invented and generic.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_counts.py"
sys.path.insert(0, str(REPO / "scripts"))
import check_counts  # noqa: E402

FINDINGS = """\
# Findings

| ID | Pattern | Evidence | Who does not show it |
|---|---|---|---|
| PAT-01 | Compares prices on several sites first | INT-001-03, INT-001-04, INT-002-01, INT-004-02 | INT-003 |
| PAT-02 | Waits a day before booking | INT-001-05, INT-005-06 | |
| PAT-03 | Asks a relative before paying | INT-002-02, INT-003-01, INT-004-07 | |
| PAT-04 | Reads the cancellation rules | INT-002-09, INT-003-04, INT-005-01, INT-001-09 | |
"""

TALK = {
    "INT-001": "I compare prices on three sites. I wait a day before I book anything.",
    "INT-002": "I compare prices on my phone. I ask my brother before I pay.",
    "INT-003": "I never compare. I read the cancellation rules twice, then I ask my aunt.",
    "INT-004": "I compare prices, then I ask my mother.",
    "INT-005": "I book the same day when the fare is low. I read the cancellation rules.",
}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "5-debrief").mkdir()
        raw = self.root / "4-field" / "_raw"
        raw.mkdir(parents=True)
        (self.root / "5-debrief" / "findings.md").write_text(FINDINGS, encoding="utf-8")
        for int_id, said in TALK.items():
            lines = [f"Microphone: Tell me more, part {n}.\nSystem audio: {said} Part {n}."
                     for n in range(3)]
            (raw / f"{int_id}-x-transcript.txt").write_text("\n".join(lines), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True)


class TestCounts(Fixture):
    def test_a_count_that_matches_the_table_passes(self):
        f = self.write("insights.md", "I1 reads PAT-01: 3 of 5 people compare prices first.\n")
        result = self.run_cli(str(f))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("MISMATCH", result.stdout)

    def test_a_count_that_drifted_is_a_mismatch(self):
        f = self.write("insights.md", "I1 reads PAT-02: 4 of 5 people wait a day.\n")
        result = self.run_cli(str(f))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("MISMATCH", result.stdout)
        self.assertIn("PAT-02 has 2", result.stdout)

    def test_words_and_spanish_forms_are_read(self):
        for sentence in ("PAT-02: four out of five wait a day.", "PAT-02: cuatro de cinco esperan un dia.",
                         "PAT-02: 4 de 5 esperan un dia."):
            with self.subTest(sentence=sentence):
                result = self.run_cli(str(self.write("i.md", sentence + "\n")))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("MISMATCH", result.stdout)

    def test_the_nearest_pattern_id_is_the_one_counted(self):
        f = self.write("i.md", "PAT-01 and PAT-03 matter. " + "x " * 120 + "PAT-02 is held by 2 of 5.\n")
        self.assertEqual(self.run_cli(str(f)).returncode, 0)

    def test_a_count_with_no_pattern_nearby_is_listed_but_does_not_fail(self):
        f = self.write("i.md", "Overall 3 of 5 liked it.\n")
        result = self.run_cli(str(f))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("UNLINKED", result.stdout)
        self.assertEqual(self.run_cli(str(f), "--strict").returncode, 1)

    def test_an_id_missing_from_the_table_fails(self):
        f = self.write("i.md", "PAT-09: 2 of 5 do it.\n")
        result = self.run_cli(str(f))
        self.assertEqual(result.returncode, 1)
        self.assertIn("UNKNOWN_ID", result.stdout)

    def test_first_number_bigger_than_second_fails(self):
        f = self.write("i.md", "PAT-01: 6 of 5 people.\n")
        self.assertIn("BAD_FRACTION", self.run_cli(str(f)).stdout)

    def test_the_table_counts_people_not_evidence_rows(self):
        patterns = check_counts.read_patterns(self.root / "5-debrief" / "findings.md", "PAT")
        self.assertEqual(len(patterns["PAT-01"]), 3)  # INT-001 twice is one person
        self.assertEqual(patterns["PAT-01"], {"INT-001", "INT-002", "INT-004"})

    def test_a_column_of_who_does_not_show_it_is_not_support(self):
        patterns = check_counts.read_patterns(self.root / "5-debrief" / "findings.md", "PAT")
        self.assertNotIn("INT-003", patterns["PAT-01"])

    def test_a_quoted_count_is_the_persons_voice_and_is_skipped(self):
        f = self.write("i.md", 'PAT-02: she said «two of my three friends wait» and then left.\n')
        self.assertEqual(self.run_cli(str(f)).returncode, 0)

    def test_html_is_read_too(self):
        f = self.write("share.html", "<p>PAT-02: <b>5 of 5</b> wait a day.</p>")
        result = self.run_cli(str(f))
        self.assertEqual(result.returncode, 1)
        self.assertIn("MISMATCH", result.stdout)


class TestSmallN(Fixture):
    def test_a_tick_on_two_people_is_flagged(self):
        for line in ("| Quick checkout | 2 of 2 | ✓ worked |", "Funcionó: 1 de 2 lo entendió."):
            with self.subTest(line=line):
                result = self.run_cli(str(self.write("slides.md", line + "\n")))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("SMALL_N", result.stdout)

    def test_a_small_count_without_a_tick_is_fine(self):
        result = self.run_cli(str(self.write("s.md", "Only 1 of 2 finished the task.\n")))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_tick_on_three_people_is_not_small(self):
        result = self.run_cli(str(self.write("s.md", "✓ 3 of 3 understood it.\n")))
        self.assertNotIn("SMALL_N", result.stdout)


class TestUniversals(Fixture):
    def test_a_negative_universal_lists_the_transcript_turns_that_break_it(self):
        f = self.write("i.md", "Nobody books the same day.\n")
        result = self.run_cli(str(f))
        self.assertIn("UNIVERSAL", result.stdout)
        self.assertIn("counterexample candidates: INT-005", result.stdout)
        self.assertNotIn("INT-001 «", result.stdout)

    def test_a_positive_universal_lists_the_interviews_with_no_support(self):
        f = self.write("i.md", "Everyone compares prices.\n")
        result = self.run_cli(str(f))
        self.assertIn("UNIVERSAL", result.stdout)
        self.assertIn("no support found in: INT-005", result.stdout)

    def test_a_universal_nothing_contradicts_says_so(self):
        f = self.write("i.md", "Nobody mentioned a loyalty programme in these interviews.\n")
        self.assertIn("survives this search", self.run_cli(str(f)).stdout)

    def test_spanish_universals(self):
        for sentence in ("Nadie reserva el mismo dia.", "Todos comparan precios.",
                         "La mayoría compara precios.", "Siempre esperan un dia."):
            with self.subTest(sentence=sentence):
                self.assertIn("UNIVERSAL", self.run_cli(str(self.write("i.md", sentence + "\n"))).stdout)

    def test_most_as_a_superlative_is_not_a_universal(self):
        f = self.write("i.md", "This is the most important finding.\n")
        self.assertNotIn("UNIVERSAL", self.run_cli(str(f)).stdout)

    def test_a_universal_inside_a_quote_is_the_persons_voice(self):
        f = self.write("i.md", 'She said: «nobody I know books the same day».\n')
        self.assertNotIn("UNIVERSAL", self.run_cli(str(f)).stdout)

    def test_five_of_five_is_a_universal_said_as_a_count(self):
        f = self.write("i.md", "PAT-01: 5 of 5 people compare prices.\n")
        out = self.run_cli(str(f)).stdout
        self.assertIn("MISMATCH", out)
        self.assertIn("everyone, said as a count", out)

    def test_universals_do_not_fail_the_run_unless_strict(self):
        f = self.write("i.md", "Nobody books the same day.\n")
        self.assertEqual(self.run_cli(str(f)).returncode, 0)
        self.assertEqual(self.run_cli(str(f), "--strict").returncode, 1)

    def test_validation_transcripts_are_searched_too(self):
        val = self.root / "7-validation" / "_raw"
        val.mkdir(parents=True)
        (val / "VAL-001-x-transcript.txt").write_text(
            "\n".join("Microphone: and?\nSystem audio: I booked the same day, no problem." for _ in range(3)),
            encoding="utf-8")
        out = self.run_cli(str(self.write("i.md", "Nobody books the same day.\n"))).stdout
        self.assertIn("VAL-001", out)


class TestOrphans(Fixture):
    def insights(self, text, heading="## Prioritized insights"):
        """The insights live in findings.md, under their own heading."""
        path = self.root / "5-debrief" / "findings.md"
        path.write_text(FINDINGS + f"\n{heading}\n\n{text}\n\n## Evidence gaps\n\nnone\n",
                        encoding="utf-8")

    def test_a_strong_pattern_with_no_insight_is_listed(self):
        self.insights("I1 (PAT-01): people compare first.")
        result = self.run_cli("--orphans")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("ORPHAN", result.stdout)
        self.assertIn("PAT-03", result.stdout)
        self.assertIn("PAT-04", result.stdout)
        self.assertNotIn("PAT-01  ", result.stdout)
        self.assertNotIn("PAT-02", result.stdout)  # held by 2: not strong

    def test_the_support_table_itself_does_not_count_as_an_insight(self):
        # Every pattern is named in its own table row. Only the insights section counts.
        self.insights("Pending.")
        result = self.run_cli("--orphans")
        self.assertEqual(result.returncode, 1, result.stdout)
        for pid in ("PAT-01", "PAT-03", "PAT-04"):
            self.assertIn(pid, result.stdout)

    def test_a_line_that_says_why_there_is_no_insight_answers_it(self):
        self.insights("I1 (PAT-01, PAT-03): a relative decides.\n"
                      "PAT-04: no insight, because it only describes the form.")
        result = self.run_cli("--orphans")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_the_threshold_can_move(self):
        self.insights("I1 (PAT-01, PAT-03, PAT-04).")
        self.assertEqual(self.run_cli("--orphans").returncode, 0)
        self.assertEqual(self.run_cli("--orphans", "--min-people", "2").returncode, 1)  # PAT-02

    def test_a_separate_insights_file_is_read_whole(self):
        self.write("my-insights.md", "I1 (PAT-01, PAT-03, PAT-04).\n")
        result = self.run_cli("--orphans", "--insights", str(self.root / "my-insights.md"))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_support_table_with_no_insights_section_lists_every_strong_pattern(self):
        result = self.run_cli("--orphans")  # fixture findings.md has the table and nothing else
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("PAT-01", result.stdout)

    def test_missing_support_table_is_a_usage_error(self):
        (self.root / "5-debrief" / "findings.md").unlink()
        self.assertEqual(self.run_cli("--orphans").returncode, 2)


class TestUsage(Fixture):
    def test_missing_file_exits_2(self):
        self.assertEqual(self.run_cli(str(self.root / "nope.md")).returncode, 2)

    def test_the_pattern_prefix_can_change(self):
        (self.root / "5-debrief" / "findings.md").write_text(
            FINDINGS.replace("PAT-", "PT-"), encoding="utf-8")
        f = self.write("i.md", "PT-02: 4 of 5 wait.\n")
        self.assertEqual(self.run_cli(str(f), "--pattern-prefix", "PT").returncode, 1)


if __name__ == "__main__":
    unittest.main()
