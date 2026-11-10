#!/usr/bin/env python3
"""Tests for scripts/verify_quotes.py, including the seeded-error control.

Run:  python3 tests/test_verify_quotes.py

A verifier is only worth trusting if it has been shown to catch planted errors.
test_seeded_errors_are_all_caught is that control: a tampered quote, an invented
one, one from another person and one the interviewer said must all be flagged,
and a real one must pass. Fixtures are invented and generic.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "verify_quotes.py"
sys.path.insert(0, str(REPO / "scripts"))
import verify_quotes  # noqa: E402

INT_A = """\
Microphone: Tell me about the last time you booked a trip.
System audio: I usually start on my phone, on the train, and I compare three or four sites.
Microphone: And then what happens?
System audio: Then I wait. I never book the same day because prices might drop tomorrow.
Microphone: What would make you trust a new site?
System audio: Honestly, seeing the cancellation rules before I enter my card number.
Microphone: Do you ever ask friends for advice?
System audio: My sister always knows a cheaper way, so I text her first.
"""

INT_B = """\
Microphone: How do you pay for groceries?
System audio: I pay with the card of my partner because mine has a low limit.
Microphone: Is that a problem?
System audio: Only when we split the bill at the end of the month.
Microphone: How often is that?
System audio: Every month, and it always takes an evening to sort out.
"""

REAL = "I never book the same day because prices might drop tomorrow."
TAMPERED = "I never book the same day because prices will surely collapse tomorrow."
INVENTED = "I would pay double for a site that answers my questions at midnight."
OTHER_PERSON = "I pay with the card of my partner because mine has a low limit."
INTERVIEWER = "What would make you trust a new site?"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        raw = self.root / "4-field" / "_raw"
        raw.mkdir(parents=True)
        (raw / "INT-001-trip-transcript.txt").write_text(INT_A, encoding="utf-8")
        (raw / "INT-002-bills-transcript.txt").write_text(INT_B, encoding="utf-8")
        self.verifier = verify_quotes.Verifier(raw, "System audio", "Microphone")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True)


class TestVerdicts(Fixture):
    def test_real_quote_is_ok(self):
        self.assertEqual(self.verifier.check("INT-001", REAL)[0], "OK")

    def test_accents_case_and_punctuation_are_ignored(self):
        self.assertEqual(self.verifier.check("INT-001", REAL.upper().replace(".", "!"))[0], "OK")

    def test_bracketed_correction_is_ignored(self):
        quote = "My sister [Ana] always knows a cheaper way, so I text her first."
        self.assertEqual(self.verifier.check("INT-001", quote)[0], "OK")

    def test_small_difference_is_literal_approx_with_the_real_text(self):
        verdict, detail = self.verifier.check(
            "INT-001", "I never book on the same day because prices might drop tomorrow.")
        self.assertEqual(verdict, "LITERAL~")
        self.assertIn("real text", detail)

    def test_interviewer_words_are_flagged(self):
        self.assertEqual(self.verifier.check("INT-001", INTERVIEWER)[0], "INTERVIEWER")

    def test_short_quote_is_short(self):
        self.assertEqual(self.verifier.check("INT-001", "I wait.")[0], "SHORT")

    def test_missing_transcript_is_reported_not_guessed(self):
        self.assertEqual(self.verifier.check("INT-099", REAL)[0], "NO_TRANSCRIPT")

    def test_person_label_is_configurable(self):
        raw = self.root / "other"
        raw.mkdir()
        (raw / "INT-003-x-transcript.txt").write_text(
            "\n".join(f"Speaker 2: I always check the weather twice, round {n}.\nInterviewer: And?"
                      for n in range(4)), encoding="utf-8")
        v = verify_quotes.Verifier(raw, "Speaker 2", "Interviewer")
        self.assertEqual(v.check("INT-003", "I always check the weather twice, round 2.")[0], "OK")
        self.assertEqual(v.check("INT-003", "And and and")[0], "INTERVIEWER")


class TestSeededErrors(Fixture):
    def test_seeded_errors_are_all_caught(self):
        seeded = {
            "tampered": (TAMPERED, "INT-001"),
            "invented": (INVENTED, "INT-001"),
            "other person": (OTHER_PERSON, "INT-001"),
            "interviewer": (INTERVIEWER, "INT-001"),
        }
        for name, (quote, int_id) in seeded.items():
            with self.subTest(seeded=name):
                self.assertNotEqual(self.verifier.check(int_id, quote)[0], "OK",
                                    f"the verifier let a {name} quote through")
        self.assertEqual(self.verifier.check("INT-001", REAL)[0], "OK")

    def test_the_other_persons_quote_is_ok_in_their_own_interview(self):
        self.assertEqual(self.verifier.check("INT-002", OTHER_PERSON)[0], "OK")

    def test_cli_exits_1_on_a_seeded_error_and_0_on_clean_input(self):
        bad = self.root / "bad.json"
        bad.write_text(json.dumps([{"id": "a", "int": "INT-001", "quote": REAL},
                                   {"id": "b", "int": "INT-001", "quote": INVENTED}]))
        good = self.root / "good.json"
        good.write_text(json.dumps([{"id": "a", "int": "INT-001", "quote": REAL}]))
        result = self.run_cli("--json", str(bad))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL", result.stdout)
        self.assertEqual(self.run_cli("--json", str(good)).returncode, 0)


class TestModes(Fixture):
    def test_evidence_mode_reads_quote_rows_only(self):
        engine = self.root / "_engine"
        engine.mkdir()
        (engine / "evidence.md").write_text(
            "| Evidence ID | Interview | Profile | Type | Evidence | Location |\n"
            "|---|---|---|---|---|---|\n"
            f"| INT-001-01 | INT-001 | A | quote | «{REAL}» | 02:10 |\n"
            f"| INT-001-02 | INT-001 | A | fact | «{INVENTED}» | 02:10 |\n"
            f"| INT-001-03 | INT-001 | A | quote | «{INVENTED}» | 03:00 |\n",
            encoding="utf-8")
        result = self.run_cli("--evidence")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("OK 1", result.stdout)
        self.assertIn("FAIL 1", result.stdout)
        self.assertIn("total 2", result.stdout)

    def test_evidence_ellipsis_splits_a_quote_in_pieces(self):
        engine = self.root / "_engine"
        engine.mkdir()
        ledger = engine / "evidence.md"
        ledger.write_text(
            "| ID | Interview | Profile | Type | Evidence | Location |\n"
            "| INT-001-01 | INT-001 | A | quote | «I usually start on my phone... "
            "seeing the cancellation rules before I enter my card number» | 1 |\n",
            encoding="utf-8")
        self.assertEqual(len(verify_quotes.from_evidence(ledger)), 2)

    def test_cases_mode_walks_nested_quotes_and_exits_1_on_fail(self):
        cases = self.root / "5-debrief" / "cases"
        cases.mkdir(parents=True)
        (cases / "INT-001.json").write_text(json.dumps({
            "id": "INT-001",
            "journey": [{"stage": "search", "evidence": {"quote": REAL, "line": 4}},
                        {"stage": "trust", "evidence": {"quote": INVENTED, "line": 9}}],
        }), encoding="utf-8")
        result = self.run_cli("--cases", "--only-problems")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("INT-001.journey[1].evidence", result.stdout)
        self.assertNotIn("journey[0]", result.stdout)

    def test_cases_mode_accepts_legacy_cita_key(self):
        cases = self.root / "5-debrief" / "cases"
        cases.mkdir(parents=True)
        (cases / "INT-001.json").write_text(json.dumps({
            "id": "INT-001", "journey": [{"cita": REAL, "line": 4}]}), encoding="utf-8")
        result = self.run_cli("--cases")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("OK 1", result.stdout)

    def test_file_mode_reads_data_int_in_html(self):
        page = self.root / "report.html"
        page.write_text(
            f'<p>Intro</p><blockquote data-int="INT-001">«{REAL}»</blockquote>'
            f'<blockquote data-int="INT-001">«{TAMPERED}»</blockquote>',
            encoding="utf-8")
        result = self.run_cli("--file", str(page))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("OK 1", result.stdout)
        self.assertIn("FAIL 1", result.stdout)

    def test_custom_raw_folder(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "INT-001-trip-transcript.txt").write_text(INT_A, encoding="utf-8")
        data = self.root / "q.json"
        data.write_text(json.dumps([{"id": "a", "int": "INT-001", "quote": REAL}]))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", "/nonexistent", "--raw", str(elsewhere),
             "--json", str(data)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
