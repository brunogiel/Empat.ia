#!/usr/bin/env python3
"""Does cut_clips.py plan a clip, build its ffmpeg call and judge it correctly?

No ffmpeg, Pillow or speech model is needed: the commands are built as lists and checked,
and the whole clip pipeline runs with fake functions for the parts that touch a file. Fixtures
are invented.

Run:  python3 tests/test_cut_clips.py
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
import cut_clips as cc  # noqa: E402
import locate_quotes as lq  # noqa: E402

QUOTE = "I never book the same day because prices might drop tomorrow"


def words(text, start=0.0, step=0.4):
    out, t = [], start
    for w in text.split():
        out.append({"word": " " + w, "start": round(t, 2), "end": round(t + step - 0.05, 2)})
        t += step
    return out


class Window(unittest.TestCase):
    def test_the_margins_surround_the_quote(self):
        self.assertEqual(cc.plan_window(100.0, 108.0, QUOTE, 3, 2), (97.0, 110.0))

    def test_an_unknown_end_is_guessed_from_the_words(self):
        start, end = cc.plan_window(100.0, None, QUOTE, 3, 2)
        self.assertGreater(end - start, 8)

    def test_never_before_zero_never_too_short_never_too_long(self):
        self.assertEqual(cc.plan_window(1.0, 2.0, QUOTE, 3, 2, min_len=6)[0], 0.0)
        s, e = cc.plan_window(50.0, 51.0, QUOTE, 1, 1, min_len=6)
        self.assertEqual(e - s, 6)
        s, e = cc.plan_window(50.0, 500.0, QUOTE, 3, 2, max_len=60)
        self.assertEqual(e - s, 60)

    def test_the_clip_stays_inside_the_recording(self):
        s, e = cc.plan_window(95.0, 99.0, QUOTE, 3, 5, min_len=6, media_duration=100.0)
        self.assertLessEqual(e, 100.0)
        self.assertLess(s, e)


class Captions(unittest.TestCase):
    def test_cards_close_on_word_count_a_pause_or_a_long_run(self):
        ws = words("one two three four five six seven eight nine ten")
        cards = cc.group_captions(ws, max_words=4)
        self.assertEqual([c["text"] for c in cards],
                         ["one two three four", "five six seven eight", "nine ten"])
        paused = words("hello there") + words("after the pause", start=9.0)
        self.assertEqual([c["text"] for c in cc.group_captions(paused)], ["hello there", "after the pause"])
        slow = words("a b c d e f", step=1.5)
        self.assertGreater(len(cc.group_captions(slow, max_words=99, max_seconds=3.2)), 1)

    def test_no_words_no_cards(self):
        self.assertEqual(cc.group_captions([]), [])


class Commands(unittest.TestCase):
    def cut(self, overlays=()):
        return cc.build_cut_command("ffmpeg", "in.mp4", 97.0, 13.0, "out.mp4", overlays)

    def test_the_seek_comes_before_the_input_so_it_is_fast_and_the_length_is_set(self):
        cmd = self.cut()
        self.assertLess(cmd.index("-ss"), cmd.index("-i"))
        self.assertEqual(cmd[cmd.index("-ss") + 1], "97.000")
        self.assertEqual(cmd[cmd.index("-t") + 1], "13.000")
        self.assertEqual(cmd[-1], "out.mp4")
        self.assertIn("+faststart", cmd)
        self.assertIn("libx264", cmd)

    def test_captions_are_images_laid_over_the_picture_not_a_text_track(self):
        cmd = self.cut([{"png": "c0.png", "t0": 0.5, "t1": 2.5}, {"png": "c1.png", "t0": 2.5, "t1": 4.0}])
        graph = cmd[cmd.index("-filter_complex") + 1]
        self.assertEqual(graph.count("overlay="), 2)
        self.assertIn("enable='between(t,0.50,2.50)'", graph)
        self.assertIn("[2:v]", graph)
        self.assertEqual(cmd.count("-i"), 3)
        self.assertNotIn("subtitles=", graph)
        self.assertIn("-sn", cmd)             # no subtitle stream in the output
        self.assertNotIn("-c:s", cmd)
        self.assertEqual(cmd[cmd.index("-map") + 1], "[v2]")

    def test_without_captions_the_video_map_is_the_scaled_stream(self):
        cmd = self.cut()
        self.assertEqual(cmd[cmd.index("-map") + 1], "[v0]")
        self.assertIn("scale=960:-2", cmd[cmd.index("-filter_complex") + 1])

    def test_the_thumbnail_is_one_frame(self):
        cmd = cc.build_thumb_command("ffmpeg", "in.mp4", 101.5, "t.jpg")
        self.assertIn("-frames:v", cmd)
        self.assertEqual(cmd[cmd.index("-frames:v") + 1], "1")
        self.assertEqual(cmd[-1], "t.jpg")


class Verdict(unittest.TestCase):
    def test_ok_needs_the_words_and_a_file_that_opens(self):
        self.assertTrue(cc.judge(0.95, 12.0)["ok"])
        self.assertTrue(cc.judge(0.8, 12.0)["ok"])
        self.assertFalse(cc.judge(0.79, 12.0)["ok"])
        self.assertFalse(cc.judge(1.0, 0.0)["ok"])
        self.assertFalse(cc.judge(1.0, 75.0, max_len=60)["ok"])
        self.assertTrue(cc.judge(0.2, 12.0)["reasons"])

    def test_safe_names(self):
        self.assertEqual(cc.safe_name("INT-001-03"), "INT-001-03")
        self.assertEqual(cc.safe_name("a/b c#2"), "a-b-c-2")


class Pipeline(unittest.TestCase):
    """Runs make_clip with fakes: what it asks ffmpeg for, and what it concludes."""

    def run_clip(self, heard_text, duration=12.0):
        calls = []
        said = {"raw": words("so " + QUOTE), "final": words(heard_text)}

        def transcribe(path):
            return said["raw"] if str(path).endswith("-raw.mp4") else said["final"]

        cfg = {"ffmpeg": "ffmpeg", "before": 3.0, "after": 2.0, "min_len": 6.0, "max_len": 60.0,
               "width": 960, "subtitles": True}
        clip = {"id": "A-1", "quote": QUOTE, "session": "S", "start_s": 100.0, "end_s": 108.0,
                "illustrates": "Prices are compared before booking"}
        with tempfile.TemporaryDirectory() as out, tempfile.TemporaryDirectory() as work:
            row = cc.make_clip(clip, Path("in.mp4"), out, cfg, run=calls.append, transcribe=transcribe,
                               probe=lambda p: 600.0 if str(p) == "in.mp4" else duration,
                               render_png=lambda text, path: None, workdir=work)
        return row, calls

    def test_a_clip_that_says_the_quote_is_ok_and_keeps_what_it_illustrates(self):
        row, calls = self.run_clip("so " + QUOTE + " you see")
        self.assertTrue(row["ok"])
        self.assertEqual(row["coverage"], 1.0)
        self.assertEqual(row["illustrates"], "Prices are compared before booking")
        self.assertEqual((row["file"], row["thumbnail"]), ("A-1.mp4", "A-1.jpg"))
        # raw cut for the captions, final cut with captions, thumbnail
        self.assertEqual(len(calls), 3)
        self.assertTrue(calls[0][-1].endswith("A-1-raw.mp4"))
        self.assertIn("overlay=", calls[1][calls[1].index("-filter_complex") + 1])
        self.assertIn("-frames:v", calls[2])

    def test_a_clip_that_cut_the_quote_short_is_not_ok(self):
        row, _ = self.run_clip("so I never book the same")
        self.assertFalse(row["ok"])
        self.assertLess(row["coverage"], 0.8)
        self.assertTrue(row["reasons"])

    def test_a_clip_with_another_voice_entirely_is_not_ok(self):
        row, _ = self.run_clip("we looked at the invoices for the whole afternoon")
        self.assertFalse(row["ok"])


class Input(unittest.TestCase):
    def test_a_locate_output_is_read_and_unlocated_quotes_are_skipped(self):
        data = {"results": [
            {"id": "A", "session": "S", "quote": QUOTE, "status": "located", "t_video_s": 100.0, "end_s": 107.0},
            {"id": "B", "session": "S", "quote": QUOTE, "status": "weak", "t_video_s": 200.0},
            {"id": "C", "session": "S", "quote": QUOTE, "status": "not_found", "coverage": 0.1}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "located.json"
            path.write_text(json.dumps(data))
            clips, skipped = cc.read_clips(path)
            weak, _ = cc.read_clips(path, include_weak=True)
        self.assertEqual([c["id"] for c in clips], ["A"])
        self.assertEqual(skipped, ["B", "C"])
        self.assertEqual([c["id"] for c in weak], ["A", "B"])

    def test_a_hand_made_list_may_give_minutes_as_clock_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            path.write_text(json.dumps([{"id": "A", "session": "S", "quote": QUOTE, "t_video": "1:40"}]))
            clips, _ = cc.read_clips(path)
        self.assertEqual(clips[0]["start_s"], 100.0)

    def test_a_clip_without_a_start_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            path.write_text(json.dumps([{"id": "A", "session": "S", "quote": QUOTE}]))
            with self.assertRaises(ValueError):
                cc.read_clips(path)


class Exit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.media = self.dir / "S.mp4"
        self.media.write_bytes(b"x")
        self.clips = self.dir / "c.json"
        self.clips.write_text(json.dumps([{"id": "A", "session": "S", "quote": QUOTE, "t_video_s": 10.0}]))
        self.argv = [str(self.clips), "--out-dir", str(self.dir / "out"), "--media", f"S={self.media}"]

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cc.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_no_ffmpeg_exits_with_2_and_says_how_to_install(self):
        with mock.patch.object(cc.shutil, "which", return_value=None):
            code, _, err = self.run_main(self.argv)
        self.assertEqual(code, 2)
        self.assertIn("ffmpeg", err)
        self.assertIn("install", err)

    def test_no_speech_to_text_exits_with_2(self):
        with mock.patch.object(cc.shutil, "which", return_value="/usr/bin/x"), \
                mock.patch.object(lq, "detect_backend", return_value=None):
            code, _, err = self.run_main(self.argv)
        self.assertEqual(code, 2)
        self.assertIn("pip install faster-whisper", err)

    def test_no_pillow_exits_with_2_unless_captions_are_off(self):
        with mock.patch.object(cc.shutil, "which", return_value="/usr/bin/x"), \
                mock.patch.object(lq, "detect_backend", return_value="whisper"), \
                mock.patch.object(cc.importlib.util, "find_spec", return_value=None):
            code, _, err = self.run_main(self.argv)
        self.assertEqual(code, 2)
        self.assertIn("--no-subtitles", err)

    def test_a_missing_recording_exits_with_2(self):
        with mock.patch.object(cc.shutil, "which", return_value="/usr/bin/x"), \
                mock.patch.object(lq, "detect_backend", return_value="whisper"):
            code, _, err = self.run_main([str(self.clips), "--out-dir", str(self.dir / "o"),
                                          "--no-subtitles"])
        self.assertEqual(code, 2)
        self.assertIn("no recording", err)

    def test_a_dry_run_prints_the_commands_and_needs_nothing_installed(self):
        with mock.patch.object(cc.shutil, "which", return_value=None):
            code, out, _ = self.run_main(self.argv + ["--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("ffmpeg -nostdin", out)
        self.assertFalse((self.dir / "out").exists())


if __name__ == "__main__":
    unittest.main(verbosity=1)
