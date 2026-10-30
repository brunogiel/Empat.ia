#!/usr/bin/env python3
"""Does resolve_deictics.py pick the right phrases and keep personal data out of the sheet?

Only the steps that need no video run here: candidates, batches and report.
The steps that call ffmpeg, Whisper or Pillow are exercised by hand on a real session.

Run:  python3 tests/test_resolve_deictics.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import resolve_deictics as rd  # noqa: E402

TRANSCRIPT = """\
[1:00] System audio (Ana): this is the start, nothing here yet
[8:10] System audio (Ana): I would click here to apply
[8:13] System audio (Ana): and this one too
[8:30] Microphone: what do you expect?
[9:00] System audio (Ana): that's why I left the old site
[9:30] System audio (Ana): this form asks for too much
[40:00] System audio (Ana): this is after the video ends
"""


class Candidates(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.transcript = self.tmp / "t.txt"
        self.transcript.write_text(TRANSCRIPT, encoding="utf-8")
        self.rows = rd.read_lines(self.transcript)

    def test_reads_person_and_interviewer(self):
        roles = [r for _, r, _ in self.rows]
        self.assertEqual(roles.count("interviewer"), 1)
        self.assertEqual(roles.count("person"), 6)

    def test_warm_up_connectors_bursts_and_the_video_end_are_left_out(self):
        found = rd.find_candidates(self.rows, offset=10, duration=2000, from_s=480, lang="en")
        lines = [c["line"] for c in found]
        self.assertEqual(lines, ["I would click here to apply", "this form asks for too much"])
        # video clock = recorder clock - offset
        self.assertEqual(found[0]["video_t"], 8 * 60 + 10 - 10)
        self.assertEqual(found[0]["id"], "C001")

    def test_context_has_neighbour_lines(self):
        found = rd.find_candidates(self.rows, offset=0, duration=3000, from_s=480, lang="en")
        self.assertTrue(any("I:" in line for line in found[0]["context"]))


class Report(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp())
        cands = [
            dict(id="C001", recorder_t=500, video_t=490, line="I would click here", context=[]),
            dict(id="C002", recorder_t=600, video_t=590, line="this form asks for a lot", context=[]),
            dict(id="C003", recorder_t=700, video_t=690, line="that is my old job", context=[]),
            dict(id="C004", recorder_t=800, video_t=790, line="this is Sam talking", context=[]),
            dict(id="C005", recorder_t=900, video_t=890, line="here maybe", context=[]),
        ]
        answers = [
            dict(id="C001", points_at="yes", component="PAGE1-action", element="Apply button", confidence="high"),
            dict(id="C002", points_at="yes", component="PAGE1-form", element="the form", confidence="high"),
            dict(id="C003", points_at="no", component="NOT-APPLICABLE", confidence="high"),
            dict(id="C004", points_at="yes", component="PAGE1-body", element="text", confidence="high"),
        ]
        (self.work / "candidates.json").write_text(json.dumps(cands))
        (self.work / "out_1.json").write_text(json.dumps(answers))
        (self.work / "other_speaker.txt").write_text("C004\n")
        self.glossary = REPO / "templates" / "deictic-glossary.md"

    def build(self, lang="en"):
        return rd.build_report(self.work, "VAL-001", "Ana", 12.5, "test", self.glossary,
                               "strips", lang)

    def test_counts_and_drops(self):
        text, stats = self.build()
        self.assertEqual(stats, dict(rows=2, dropped=1, other=1, missing=1, review=0))
        self.assertNotIn("old job", text)
        self.assertNotIn("Sam talking", text)

    def test_sensitive_component_gets_no_capture(self):
        text, _ = self.build()
        form = next(l for l in text.splitlines() if "asks for a lot" in l)
        self.assertIn("no capture (personal data)", form)
        button = next(l for l in text.splitlines() if "I would click" in l)
        self.assertIn("strips/C001.jpg", button)

    def test_unknown_goes_to_review(self):
        answers = json.loads((self.work / "out_1.json").read_text())
        answers[0].update(component="UNKNOWN", confidence="low")
        (self.work / "out_1.json").write_text(json.dumps(answers))
        text, stats = self.build()
        self.assertEqual(stats["review"], 1)
        self.assertIn("**review**", text)

    def test_spanish_strings(self):
        text, _ = self.build("es")
        self.assertIn("qué señalaba", text)

    def test_glossary_tags(self):
        tags = rd.read_glossary(self.glossary)
        self.assertEqual(tags["PAGE1-form"], {"sensitive"})
        self.assertEqual(tags["BROWSER"], {"outside"})
        self.assertEqual(tags["PAGE1-header"], set())


class Masks(unittest.TestCase):
    def test_masks_apply_only_inside_their_time_range(self):
        masks = [dict(from_video_s=10, to_video_s=20, rect=[0, 0, 1, 0.1])]
        self.assertEqual(len(rd.active_masks(masks, 15)), 1)
        self.assertEqual(rd.active_masks(masks, 25), [])

    def test_paint_masks_blacks_out_the_rectangle(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        rd.paint_masks(image, [[0, 0, 1, 0.5]])
        self.assertEqual(image.getpixel((50, 10)), (0, 0, 0))
        self.assertEqual(image.getpixel((50, 90)), (255, 255, 255))


class Batches(unittest.TestCase):
    def test_splits_in_batches(self):
        work = Path(tempfile.mkdtemp())
        cands = [dict(id=f"C{i:03d}", line="x", context=[]) for i in range(1, 6)]
        (work / "candidates.json").write_text(json.dumps(cands))
        self.assertEqual(rd.write_batches(work, 2), 3)
        self.assertEqual(len(json.loads((work / "cases_3.json").read_text())), 1)


if __name__ == "__main__":
    unittest.main()
