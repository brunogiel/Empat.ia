#!/usr/bin/env python3
"""Tests for scripts/verify_quotes.py, including the seeded-error control.

Run:  python3 tests/test_verify_quotes.py

A verifier is only worth trusting if it has been shown to catch planted errors.
test_seeded_errors_are_all_caught is that control: a tampered quote, an invented
one, one from another person and one the interviewer said must all be flagged,
and a real one must pass. Fixtures are invented and generic.

Also here: the cut check (a literal fragment whose negation sits outside it), vetoed
quotes, validation transcripts, and transcripts with a clock prefix or continuation lines.
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


INT_CUT = """\
Microphone: How do you feel about price alerts?
System audio: I think I never stopped comparing prices on my phone.
Microphone: And the app?
System audio: I like the app, but I never finish a purchase there.
Microphone: Why not?
System audio: My sister always knows a cheaper way, so I text her first.
Microphone: Do you trust the reviews?
System audio: I don't think we ever tried the reviews page.
Microphone: And in your language?
System audio: Creo que nunca dejé de comparar precios en el celular.
Microphone: Y la tienda?
System audio: Me gusta la tienda pero casi nunca termino de pagar.
Microphone: Anything else?
System audio: Nothing else. I compare prices every single week without fail.
"""


class Cuts(Fixture):
    def setUp(self):
        super().setUp()
        (self.root / "4-field" / "_raw" / "INT-005-cuts-transcript.txt").write_text(
            INT_CUT, encoding="utf-8")

    def verdict(self, quote):
        return self.verifier.check("INT-005", quote)

    def test_negation_right_before_the_fragment_is_cut(self):
        verdict, detail = self.verdict("stopped comparing prices on my phone")
        self.assertEqual(verdict, "CUT?")
        self.assertIn("never", detail)
        self.assertIn("[QUOTE]", detail)

    def test_the_full_sentence_is_still_ok(self):
        self.assertEqual(self.verdict("I think I never stopped comparing prices on my phone.")[0], "OK")

    def test_but_right_after_the_fragment_is_cut(self):
        verdict, detail = self.verdict("I like the app")
        self.assertEqual(verdict, "CUT?")
        self.assertIn("but", detail)

    def test_a_fragment_that_starts_mid_sentence_is_cut(self):
        verdict, detail = self.verdict("so I text her first.")
        self.assertEqual(verdict, "CUT?")
        self.assertIn("starts in the middle", detail)

    def test_a_fragment_that_ends_mid_sentence_is_cut(self):
        verdict, detail = self.verdict("My sister always knows a cheaper way")
        self.assertEqual(verdict, "CUT?")
        self.assertIn("ends in the middle", detail)

    def test_english_contraction_counts_as_a_negation(self):
        verdict, detail = self.verdict("think we ever tried the reviews page.")
        self.assertEqual(verdict, "CUT?")
        self.assertIn("negation", detail)

    def test_spanish_negation_and_contrast_are_read_too(self):
        self.assertEqual(self.verdict("dejé de comparar precios en el celular.")[0], "CUT?")
        verdict, detail = self.verdict("Me gusta la tienda")
        self.assertEqual(verdict, "CUT?")
        self.assertIn("pero", detail)

    def test_midsentence_rule_can_be_switched_off(self):
        v = verify_quotes.Verifier(self.root / "4-field" / "_raw", "System audio", "Microphone",
                                   midsentence=False)
        self.assertEqual(v.check("INT-005", "so I text her first.")[0], "OK")
        # The negation rule stays on.
        self.assertEqual(v.check("INT-005", "stopped comparing prices on my phone")[0], "CUT?")

    def test_a_negation_in_the_previous_sentence_does_not_count(self):
        self.assertEqual(self.verdict("I compare prices every single week without fail.")[0], "OK")

    def test_cut_does_not_fail_the_run_but_shows_with_only_problems(self):
        data = self.root / "q.json"
        data.write_text(json.dumps([{"id": "a", "int": "INT-005",
                                     "quote": "stopped comparing prices on my phone"}]))
        result = self.run_cli("--json", str(data), "--only-problems")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CUT?", result.stdout)

    def test_a_transcript_with_no_punctuation_never_flags_midsentence(self):
        (self.root / "4-field" / "_raw" / "INT-006-flat-transcript.txt").write_text(
            "\n".join(f"Microphone: tell me more {n}\nSystem audio: i compare prices on my phone "
                      f"every week round {n} and then i wait"
                      for n in range(5)), encoding="utf-8")
        self.assertEqual(self.verifier.check("INT-006", "compare prices on my phone every week round 2")[0],
                         "OK")


class Vetoed(Fixture):
    def ledger(self):
        engine = self.root / "_engine"
        engine.mkdir(exist_ok=True)
        path = engine / "evidence.md"
        path.write_text(
            "| Evidence ID | Interview | Profile | Type | Evidence | Location | Tags | Reading | Confidence | Use in synthesis |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            f"| INT-001-01 | INT-001 | A | quote | «{REAL}» | 02:10 | t | r | high | yes |\n"
            "| INT-001-02 | INT-001 | A | quote | «My sister always knows a cheaper way, so I text her first.» "
            "| 04:00 | t | r | low | vetoed: induced by the question |\n",
            encoding="utf-8")
        return path

    def test_a_vetoed_quote_in_another_file_is_flagged_and_fails_the_run(self):
        self.ledger()
        data = self.root / "q.json"
        data.write_text(json.dumps([
            {"id": "a", "int": "INT-001", "quote": REAL},
            {"id": "b", "int": "INT-001",
             "quote": "My sister always knows a cheaper way, so I text her first."}]))
        result = self.run_cli("--json", str(data))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("VETOED", result.stdout)
        self.assertIn("induced by the question", result.stdout)
        self.assertIn("OK 1", result.stdout)

    def test_a_vetoed_quote_is_caught_even_when_cut_or_extended(self):
        self.ledger()
        v = verify_quotes.Verifier(self.root / "4-field" / "_raw", "System audio", "Microphone",
                                   vetoed=verify_quotes.vetoed_quotes(self.root / "_engine" / "evidence.md"))
        self.assertEqual(v.check("INT-001", "always knows a cheaper way, so I text her")[0], "VETOED")
        self.assertEqual(v.check("INT-001", "Honestly, my sister always knows a cheaper way, "
                                            "so I text her first. And more")[0], "VETOED")

    def test_the_ledger_itself_does_not_fail_on_its_own_vetoed_row(self):
        self.ledger()
        result = self.run_cli("--evidence")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("total 1", result.stdout)

    def test_scan_finds_a_vetoed_quote_in_markdown(self):
        self.ledger()
        page = self.root / "principles.md"
        page.write_text("# Principles\n\nP-01 rests on «My sister always knows a cheaper way, "
                        f"so I text her first.» and on «{REAL}».\n", encoding="utf-8")
        result = self.run_cli("--scan", str(page))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("VETOED 1", result.stdout)
        self.assertNotIn("OK", result.stdout)

    def test_file_mode_catches_a_vetoed_quote_outside_a_data_int_element(self):
        self.ledger()
        page = self.root / "share.html"
        page.write_text(f'<blockquote data-int="INT-001">«{REAL}»</blockquote>'
                        "<p>As she put it: “My sister always knows a cheaper way, so I text her first.”</p>",
                        encoding="utf-8")
        result = self.run_cli("--file", str(page))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("VETOED 1", result.stdout)
        self.assertIn("OK 1", result.stdout)

    def test_no_ledger_means_no_vetoes(self):
        data = self.root / "q.json"
        data.write_text(json.dumps([{"id": "a", "int": "INT-001", "quote": REAL}]))
        self.assertEqual(self.run_cli("--json", str(data)).returncode, 0)


INT_CLOCK = """\
[0:03] Microphone: Tell me about the last time you booked a trip.
[0:09] System audio: I usually start on my phone, on the train,
and I compare three or four sites
before I decide anything at all.
[1:02:30] Microphone: And then what happens?
[1:02:41] System audio: Then I wait. I never book the same day.
[1:03:00] Microphone: Why not?
[1:03:05] System audio: Prices might drop tomorrow.
"""


class RealWorldTranscripts(Fixture):
    def setUp(self):
        super().setUp()
        raw = self.root / "4-field" / "_raw"
        (raw / "INT-007-clock-transcript.txt").write_text(INT_CLOCK, encoding="utf-8")
        val = self.root / "7-validation" / "_raw"
        val.mkdir(parents=True)
        (val / "VAL-001-prototype-transcript.txt").write_text(INT_B, encoding="utf-8")
        self.verifier = verify_quotes.Verifier(raw, "System audio", "Microphone", val)

    def test_clock_prefix_does_not_hide_the_speakers(self):
        verdict = self.verifier.check("INT-007", "I usually start on my phone, on the train")[0]
        self.assertEqual(verdict, "CUT?")  # a real fragment: the clock was read, the sentence goes on
        self.assertEqual(self.verifier.check("INT-007", "Then I wait.")[0], "OK")
        self.assertEqual(self.verifier.check("INT-007", "I never book the same day.")[0], "OK")

    def test_a_line_with_no_speaker_belongs_to_whoever_spoke_last(self):
        quote = ("I usually start on my phone, on the train, and I compare three or four sites "
                 "before I decide anything at all.")
        self.assertEqual(self.verifier.check("INT-007", quote)[0], "OK")

    def test_the_interviewer_is_still_the_interviewer_behind_a_clock(self):
        self.assertEqual(self.verifier.check("INT-007", "Tell me about the last time you booked a trip.")[0],
                         "INTERVIEWER")

    def test_clock_forms(self):
        text = "[3:05] Name: hello there\n(1:02:03) Name: again\n4:15 Name: and again\nName [5:00]: last\n[9:99]\n"
        cleaned = verify_quotes.strip_clocks(text)
        self.assertEqual(cleaned.splitlines()[:4],
                         ["Name: hello there", "Name: again", "Name: and again", "Name: last"])

    def test_a_time_of_day_inside_a_line_is_left_alone(self):
        self.assertIn("10:30 is when", verify_quotes.strip_clocks("System audio: ok\n10:30 is when I wake up\n"))

    def test_fallback_parser_carries_the_speaker_over_continuation_lines(self):
        short = ("Microphone: Anything to add?\nSystem audio: I check the weather twice\n"
                 "before I leave the house.\n")
        turns = verify_quotes.read_turns(short, "System audio", "Microphone")
        self.assertEqual(turns[1][0], "person")
        self.assertIn("before I leave the house", turns[1][1])

    def test_validation_transcripts_are_read_from_their_own_folder(self):
        self.assertEqual(self.verifier.check("VAL-001", OTHER_PERSON)[0], "OK")
        self.assertEqual(self.verifier.check("INT-001", OTHER_PERSON)[0], "FAIL")

    def test_cli_reads_val_rows_of_the_ledger_and_the_validation_folder(self):
        engine = self.root / "_engine"
        engine.mkdir()
        (engine / "evidence.md").write_text(
            "| ID | Interview | Profile | Type | Evidence | Location |\n"
            f"| VAL-001-01 | VAL-001 | A | quote | «{OTHER_PERSON}» | 1 |\n", encoding="utf-8")
        result = self.run_cli("--evidence")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("OK 1", result.stdout)

    def test_val_case_sheets_and_html_markers_are_read(self):
        cases = self.root / "5-debrief" / "cases"
        cases.mkdir(parents=True)
        (cases / "VAL-001.json").write_text(json.dumps({"id": "VAL-001", "x": {"quote": OTHER_PERSON}}))
        self.assertIn("OK 1", self.run_cli("--cases").stdout)
        page = self.root / "r.html"
        page.write_text(f'<blockquote data-int="VAL-001">«{OTHER_PERSON}»</blockquote>')
        self.assertIn("OK 1", self.run_cli("--file", str(page)).stdout)


if __name__ == "__main__":
    unittest.main()
