#!/usr/bin/env python3
"""Does locate_quotes.py find a quote by its words, and say so when it cannot?

Only the logic that needs no speech model runs here: word alignment, coverage, the hint that
tells two identical phrases apart, reading the evidence ledger, the offset per session, and
the exit with code 2 when no speech-to-text is installed. The listening step is exercised by
hand on a real recording. Fixtures are invented.

Run:  python3 tests/test_locate_quotes.py
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import locate_quotes as lq  # noqa: E402

CHATTER = ("so yeah and then I think that we were just talking about the other thing and "
           "you know it was the same as before and that is what the team said").split()
QUOTE = "I never book the same day because prices might drop tomorrow"


def heard(text, start=0.0, step=0.4):
    """Timed words, one every `step` seconds, like a speech model returns them."""
    out, t = [], start
    for w in text.split():
        out.append({"word": " " + w + ",", "start": round(t, 2), "end": round(t + step - 0.05, 2)})
        t += step
    return out


def session_words(*parts):
    """Chatter, then each (text) in turn, with chatter between: [(token, start, end)]."""
    words, t = [], 0.0
    for part in parts:
        chunk = heard(part, start=t)
        words += chunk
        t = chunk[-1]["end"] + 0.05
    return lq.flatten_words(words)


class Words(unittest.TestCase):
    def test_normalising_drops_accents_punctuation_and_corrections(self):
        self.assertEqual(lq.norm_tokens("¡Qué difícil, [Acme] es!"), ["que", "dificil", "es"])
        self.assertEqual(lq.norm_tokens("Don't stop"), ["don", "t", "stop"])

    def test_function_words_do_not_count_but_a_tiny_quote_is_read_whole(self):
        self.assertEqual(lq.content_tokens(lq.norm_tokens("the price and the cancellation rules")),
                         ["price", "cancellation", "rules"])
        self.assertEqual(lq.content_tokens(lq.norm_tokens("it is the price")), ["it", "is", "the", "price"])

    def test_a_misheard_long_word_still_matches_a_short_one_must_be_exact(self):
        self.assertTrue(lq.words_match("cancellation", "cancelation"))
        self.assertFalse(lq.words_match("this", "his"))
        self.assertFalse(lq.words_match("book", "look"))


class Alignment(unittest.TestCase):
    def test_an_exact_quote_is_found_where_it_was_said(self):
        flat = session_words(" ".join(CHATTER), QUOTE, " ".join(CHATTER))
        found = lq.locate(flat, QUOTE)
        self.assertEqual(found["coverage"], 1.0)
        expected = len(CHATTER) * 0.4
        self.assertAlmostEqual(found["start_s"], expected, delta=1.0)
        self.assertGreater(found["end_s"], found["start_s"])

    def test_a_quote_the_model_heard_a_little_wrong_is_still_located(self):
        said = "I never book the same day because prizes might drop tomorrow"
        flat = session_words(" ".join(CHATTER), said)
        found = lq.locate(flat, QUOTE)
        self.assertGreaterEqual(found["coverage"], lq.LOCATED)
        self.assertEqual(lq.status_of(found["coverage"]), "located")

    def test_chatter_made_of_the_quotes_function_words_is_not_a_match(self):
        # The old way (one long string compared as a whole) flagged this kind of text.
        flat = session_words(" ".join(CHATTER * 5))
        found = lq.locate(flat, QUOTE)
        self.assertTrue(found is None or lq.status_of(found["coverage"]) == "not_found")

    def test_a_quote_that_was_never_said_is_not_found(self):
        flat = session_words(" ".join(CHATTER), "we compared the invoices for three hours yesterday")
        found = lq.locate(flat, "I would pay double for a site that answers my questions at midnight")
        self.assertTrue(found is None or lq.status_of(found["coverage"]) == "not_found")

    def test_half_a_quote_is_weak_not_located(self):
        flat = session_words(" ".join(CHATTER), "I never book the same day because prices")
        found = lq.locate(flat, "I never book the same day because prices might drop tomorrow evening")
        self.assertEqual(lq.status_of(found["coverage"]), "weak")

    def test_the_same_phrase_said_twice_goes_to_the_one_near_the_hint(self):
        flat = session_words(QUOTE, " ".join(CHATTER) * 3, QUOTE)
        first = lq.locate(flat, QUOTE, hint_s=1.0)
        last_at = flat[-1][1] - 4.0
        second = lq.locate(flat, QUOTE, hint_s=last_at)
        self.assertLess(first["start_s"], 2.0)
        self.assertGreater(second["start_s"], first["start_s"] + 30)

    def test_a_radius_limits_the_search_to_the_neighbourhood(self):
        flat = session_words(QUOTE, " ".join(CHATTER) * 3, QUOTE)
        near_start = lq.locate(flat, QUOTE, hint_s=0.5, radius_s=10)
        self.assertLess(near_start["start_s"], 2.0)
        nothing_there = lq.locate(flat, QUOTE, hint_s=flat[len(flat) // 2][1], radius_s=3)
        self.assertTrue(nothing_there is None or lq.status_of(nothing_there["coverage"]) != "located")

    def test_clip_coverage_counts_the_quotes_words_in_what_the_clip_says(self):
        clip = lq.norm_tokens("so I never book the same day because prices might drop tomorrow ok")
        self.assertEqual(lq.coverage_in_tokens(QUOTE, clip), 1.0)
        cut = lq.norm_tokens("so I never book the same day because")
        self.assertLess(lq.coverage_in_tokens(QUOTE, cut), lq.LOCATED)

    def test_an_empty_quote_or_nothing_heard_returns_nothing(self):
        self.assertIsNone(lq.locate([], QUOTE))
        self.assertIsNone(lq.locate(session_words("hello there"), "   "))


class Clocks(unittest.TestCase):
    def test_times_in_every_form(self):
        self.assertEqual(lq.parse_time("1:05"), 65.0)
        self.assertEqual(lq.parse_time("[1:02:03]"), 3723.0)
        self.assertEqual(lq.parse_time("52.8"), 52.8)
        self.assertEqual(lq.parse_time(7), 7.0)
        self.assertIsNone(lq.parse_time(""))

    def test_both_clocks_and_their_difference_are_kept(self):
        flat = session_words(" ".join(CHATTER), QUOTE)
        items = [{"id": "INT-001-01", "session": "INT-001", "quote": QUOTE, "t_transcript": 75.0}]
        out = lq.locate_all(items, lambda s: flat, {}, None)[0]
        self.assertEqual(out["status"], "located")
        self.assertEqual(out["t_transcript"], "1:15")
        self.assertAlmostEqual(out["offset_s"], 75.0 - out["t_video_s"], places=1)

    def test_a_known_offset_steers_the_search_toward_the_right_repeat(self):
        flat = session_words(QUOTE, " ".join(CHATTER) * 3, QUOTE)
        late = flat[-1][1] - 4.0
        items = [{"id": "Q", "session": "S", "quote": QUOTE, "t_transcript": late + 50.0}]
        out = lq.locate_all(items, lambda s: flat, {"S": 50.0}, 20.0)[0]
        self.assertAlmostEqual(out["t_video_s"], late, delta=4.0)

    def test_the_session_offset_is_the_median_of_the_good_ones(self):
        results = [{"session": "S", "status": "located", "offset_s": o} for o in (50.0, 52.0, 51.0)]
        results.append({"session": "S", "status": "weak", "offset_s": 400.0})
        self.assertEqual(lq.session_offsets(results)["S"], {"offset_s": 51.0, "n": 3, "spread_s": 2.0})

    def test_a_session_without_a_recording_says_so(self):
        out = lq.locate_all([{"id": "Q", "session": "S", "quote": QUOTE, "t_transcript": None}],
                            lambda s: None, {}, None)[0]
        self.assertEqual(out["status"], "no_media")


LEDGER = """\
| Evidence ID | Interview | Profile | Type | Evidence | Location | Tags | Preliminary reading | Confidence | Use in synthesis | Voice | Induced | t_transcript | t_video |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INT-001-01 | INT-001 | A | quote | "I never book the same day." | minute 12:30 | price | x | high | yes | person | none | | |
| INT-001-02 | INT-001 | A | quote | "Prices might drop tomorrow." | line 40 | price | x | high | vetoed: induced | person | none | | |
| INT-001-03 | INT-001 | A | fact | She books on the train. | 3:10 | price | x | high | yes | person | none | | |
| INT-002-01 | INT-002 | B | quote | "My sister knows a cheaper way." | 4:00 | family | x | high | yes | person | none | 9:05 | |
"""


class Input(unittest.TestCase):
    def test_the_ledger_gives_quotes_and_minutes_and_skips_vetoed_and_non_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.md"
            path.write_text(LEDGER, encoding="utf-8")
            items = lq.read_evidence(path)
        self.assertEqual([i["id"] for i in items], ["INT-001-01", "INT-002-01"])
        self.assertEqual(items[0]["t_transcript"], 12 * 60 + 30)   # from Location
        self.assertEqual(items[1]["t_transcript"], 9 * 60 + 5)     # the column wins over Location

    def test_a_quotes_file_needs_a_session_and_a_quote(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.json"
            path.write_text(json.dumps([{"id": "A", "quote": "no session here"}]))
            with self.assertRaises(ValueError):
                lq.read_quotes(path)

    def test_media_is_found_by_the_session_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("INT-001-call.mp4", "int-002.m4a", "INT-003.txt"):
                (Path(tmp) / name).write_bytes(b"")
            self.assertEqual(lq.resolve_media("INT-001", {}, tmp).name, "INT-001-call.mp4")
            self.assertEqual(lq.resolve_media("INT-002", {}, tmp).name, "int-002.m4a")
            self.assertIsNone(lq.resolve_media("INT-003", {}, tmp))
            self.assertEqual(lq.resolve_media("X", {"X": "/a/b.mp4"}, tmp), Path("/a/b.mp4"))


class Exit(unittest.TestCase):
    def run_main(self, argv):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = lq.main(argv)
        return code, err.getvalue()

    def test_no_speech_to_text_exits_with_2_and_says_how_to_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            quotes = Path(tmp) / "q.json"
            media = Path(tmp) / "INT-001.mp4"
            media.write_bytes(b"")
            quotes.write_text(json.dumps([{"id": "A", "session": "INT-001", "quote": QUOTE}]))
            with mock.patch.object(lq, "detect_backend", return_value=None):
                code, err = self.run_main(["--quotes", str(quotes), "--media", f"INT-001={media}"])
        self.assertEqual(code, 2)
        self.assertIn("pip install faster-whisper", err)

    def test_a_bad_input_exits_with_2(self):
        code, err = self.run_main(["--quotes", "/no/such/file.json"])
        self.assertEqual(code, 2)

    def test_the_whole_run_with_a_fake_speech_model(self):
        words = heard(" ".join(CHATTER) + " " + QUOTE)

        class Fake:
            def __init__(self, *a, **k):
                pass

            def words(self, media):
                return words

        with tempfile.TemporaryDirectory() as tmp:
            quotes = Path(tmp) / "q.json"
            media = Path(tmp) / "INT-001.mp4"
            media.write_bytes(b"x")
            quotes.write_text(json.dumps([
                {"id": "A", "session": "INT-001", "quote": QUOTE, "t_transcript": "1:00"},
                {"id": "B", "session": "INT-001", "quote": "something nobody ever said aloud here"}]))
            out = Path(tmp) / "out.json"
            with mock.patch.object(lq, "detect_backend", return_value="whisper"), \
                    mock.patch.object(lq, "Transcriber", Fake):
                code, _ = self.run_main(["--quotes", str(quotes), "--media-dir", tmp,
                                         "--out", str(out), "--cache-dir", str(Path(tmp) / "cache")])
            data = json.loads(out.read_text())
            self.assertTrue(any(Path(tmp, "cache").glob("*.words.json")))
        self.assertEqual(code, 1)  # one quote was not found
        self.assertEqual([r["status"] for r in data["results"]], ["located", "not_found"])
        self.assertIn("INT-001", data["sessions"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
