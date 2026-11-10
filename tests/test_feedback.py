#!/usr/bin/env python3
"""Tests for the interviewer feedback engine: exchanges, packs, scales, hand count.

Run:  python3 tests/test_feedback.py

No network. jev is never called: the judged CSVs are written by hand here, in
the shape classify_exchanges.py writes them. Fixtures are invented and generic.
"""

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
import count_interview as ci  # noqa: E402
import feedback_packs  # noqa: E402
import feedback_scales  # noqa: E402
import jev_client  # noqa: E402
import segment_interview as seg  # noqa: E402

TRANSCRIPT = """\
Microphone: Hi, can you hear me?
System audio (Ana Lopez): Yes, all good.
Microphone: Tell me about the last time you booked a trip.
System audio (Ana Lopez): I started on my phone on the train.
Microphone: Great.
System audio (Ana Lopez): Then I compared three sites.
System audio: And I waited a day.
Microphone: Why did you wait?
System audio (Ana Lopez): Because prices drop.
Microphone: ok
Microphone: Thanks a lot for your time today.
System audio (Ana Lopez): Bye.
"""

GUIDE = """\
# Interview guide

### 0. Opening (2)
Goal: consent and rapport.

### 1. Your last trip (10)
Goal: the story of one trip, end to end.

### 2. What makes a site trustworthy
**Intención:** sus criterios, con sus palabras.

### 3. Card sorting (10)

### 4. Closing
"""


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


class Exchanges(unittest.TestCase):
    """An exchange is a real question plus everything until the next one."""

    def turns(self, text):
        return ci.parse(seg.RECORDER_LABEL.sub(r"\1System audio:", text))

    def test_short_acknowledgements_do_not_cut(self):
        ex = seg.segment(self.turns(TRANSCRIPT), "Microphone")
        questions = [q for q, _ in ex]
        self.assertIn("Tell me about the last time you booked a trip.", questions)
        self.assertNotIn("Great.", questions)
        trip = dict(ex)["Tell me about the last time you booked a trip."]
        self.assertIn("[interviewer: Great.]", trip)
        self.assertIn("compared three sites", trip)

    def test_a_label_without_the_name_is_still_the_interviewee(self):
        """'System audio:' without '(Name)' was learned as a separate, rare speaker,
        and its words were glued to the interviewer's turn."""
        trip = dict(seg.segment(self.turns(TRANSCRIPT), "Microphone"))[
            "Tell me about the last time you booked a trip."]
        self.assertIn("I waited a day", trip)

    def test_question_mark_cuts_even_when_short(self):
        ex = seg.segment(self.turns(TRANSCRIPT), "Microphone")
        self.assertIn("Why did you wait?", [q for q, _ in ex])

    def test_items_carry_language_keys(self):
        items = seg.to_items([("Q?", "A")], "es")
        self.assertEqual(items[0]["id"], "x001")
        self.assertEqual(seg.question_of(items[0]["state"]), "Q?")
        self.assertEqual(seg.answer_of(items[0]["state"]), "A")
        self.assertIn("pregunta_entrevistador", items[0]["state"])

    def test_cli_writes_jsonl_and_skips_chatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / "t.md"
            t.write_text("Microphone: talking to a colleague before\n" + TRANSCRIPT, encoding="utf-8")
            out = Path(tmp) / "INT-001-ana.jsonl"
            r = subprocess.run([sys.executable, str(SCRIPTS / "segment_interview.py"), str(t),
                                "--interviewer", "Microphone", "--out", str(out),
                                "--skip-until-first-interviewee"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            first = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
            self.assertNotIn("colleague", json.dumps(first))


class Packs(unittest.TestCase):
    """The topics come from the project's guide, not from the method."""

    def build(self, lang="en", logistics=None):
        with tempfile.TemporaryDirectory() as tmp:
            g = Path(tmp) / "guide.md"
            g.write_text(GUIDE, encoding="utf-8")
            return feedback_packs.build(feedback_packs.read_blocks(g), "booking trips", lang, logistics)

    def test_topics_come_from_the_guide(self):
        pack = self.build()
        titles = [t["title"] for t in pack["topics"]]
        self.assertEqual(titles, ["Your last trip", "What makes a site trustworthy", "Card sorting"])
        criteria = pack["preguntas"]["bloque"]["criteria"]
        self.assertIn("The story of one trip, end to end.", criteria["t1_your_last_trip"])
        self.assertIn("Sus criterios", criteria["t2_what_makes_a_site_trustworthy"])
        self.assertIn("booking trips", pack["preguntas"]["bloque"]["instructions"])

    def test_opening_and_closing_fold_into_logistics_with_a_way_out(self):
        pack = self.build()
        criteria = pack["preguntas"]["bloque"]["criteria"]
        self.assertIn(pack["logistics_key"], criteria)
        self.assertIn(pack["none_key"], criteria)
        self.assertFalse(any(k.startswith(("t0_", "t4_")) for k in criteria))

    def test_logistics_can_be_given_by_number(self):
        pack = self.build(logistics={"1"})
        keys = [t["key"] for t in pack["topics"]]
        self.assertNotIn("t1_your_last_trip", keys)
        self.assertIn("t0_opening", keys)

    def test_the_card_sort_is_marked_as_an_exercise(self):
        self.assertEqual([t["title"] for t in self.build()["topics"] if t["exercise"]], ["Card sorting"])

    def test_built_pack_loads_with_nothing_unresolved(self):
        for lang in ("en", "es"):
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / "depth.json"
                p.write_text(json.dumps(self.build(lang)), encoding="utf-8")
                _, questions = jev_client.load_pack(p)
                self.assertEqual(questions["bloque"]["type"], "choice")

    def test_languages_ask_the_same_questions(self):
        for name in ("depth", "branches"):
            en = json.loads((SCRIPTS / "packs" / f"{name}.en.json").read_text(encoding="utf-8"))
            es = json.loads((SCRIPTS / "packs" / f"{name}.es.json").read_text(encoding="utf-8"))
            self.assertEqual(list(en["preguntas"]), list(es["preguntas"]), name)
            for qid, q in en["preguntas"].items():
                self.assertEqual(q["type"], es["preguntas"][qid]["type"], qid)

    def test_shipped_packs_name_no_domain(self):
        """The packs were measured on a job-search round; the shipped ones are generic."""
        for path in (SCRIPTS / "packs").glob("*.json"):
            text = path.read_text(encoding="utf-8").lower()
            for word in ("linkedin", "empresa", "postul", "career", "trabajo", "company"):
                self.assertNotIn(word, text, f"{path.name}: {word}")


class Scales(unittest.TestCase):
    """The numbers come from counts and from fixed thresholds on jev's answers."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        pack = {"topics": [{"key": "t1_trip", "title": "Your last trip", "exercise": False},
                           {"key": "t3_cards", "title": "Card sorting", "exercise": True}],
                "logistics_key": "logistics_opening_or_closing", "none_key": "none_of_the_topics"}
        (self.folder / "depth-pack.json").write_text(json.dumps(pack), encoding="utf-8")
        long = " ".join(["word"] * 250)
        self.make("INT-001-ana", [("Hi?", "hello there"), ("Last time?", long),
                                  ("Why?", " ".join(["w"] * 20)), ("Thanks?", "bye")])
        self.make("INT-002-ben", [("Hi?", "hi"), ("Last time?", " ".join(["w"] * 40)),
                                  ("Why?", " ".join(["w"] * 60)), ("Thanks?", "bye")],
                  judged=False)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, base, exchanges, judged=True):
        items = seg.to_items(exchanges)
        (self.folder / f"{base}.jsonl").write_text(
            "".join(json.dumps(i) + "\n" for i in items), encoding="utf-8")
        if not judged:
            return
        blocks = ["logistics_opening_or_closing", "t1_trip", "t1_trip", "logistics_opening_or_closing"]
        depth = [{"id": i["id"], "bloque": b, "bloque_conf": "0.9", "episodio_p": "0.9" if k == 1 else "0.1",
                  "motivo_p": "0.8" if k == 2 else "0.1", "tension_p": "0.7" if k == 1 else "0.1",
                  "generalizacion_p": "0.1", "pide_motivo_p": "0.9" if k == 2 else "0.1",
                  "pide_episodio_p": "0.9" if k == 1 else "0.1", "premisa_p": "0.7" if k == 2 else "0.1",
                  "responde": "directa", "responde_conf": "0.8"}
                 for k, (i, b) in enumerate(zip(items, blocks))]
        write_csv(self.folder / f"{base}-depth.csv", depth)
        write_csv(self.folder / f"{base}-branches.csv",
                  [{"id": i["id"], "arranca_contestando_p": "0.9" if k == 1 else "0.2",
                    "se_va_a_otro_tema_p": "0.1"} for k, i in enumerate(items)])

    def run_scales(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "feedback_scales.py"), str(self.folder),
                            "--label", "INT-001-ana=Ána"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return (json.loads((self.folder / "INT-001-ana-data.json").read_text(encoding="utf-8")),
                json.loads((self.folder / "INT-002-ben-data.json").read_text(encoding="utf-8")))

    def test_logistics_leave_the_median_and_monologues_are_counted(self):
        ana, _ = self.run_scales()
        self.assertEqual(ana["substantive_exchanges"], 2)
        self.assertEqual(ana["median_words"], (250 + 20) / 2)
        self.assertEqual(ana["monologues"], 1)
        self.assertEqual(ana["monologue_pct"], round(100 * 250 / 270))

    def test_goes_to_the_point_and_topics(self):
        ana, _ = self.run_scales()
        self.assertEqual(ana["goes_to_point"], 5.0)
        trip = ana["topics"]["t1_trip"]
        self.assertEqual((trip["exchanges"], trip["concrete_cases"], trip["reasons"]), (2, 1, 1))
        self.assertEqual([c["id"] for c in ana["premise_candidates"]], ["x003"])

    def test_without_jev_the_counts_still_come_out(self):
        _, ben = self.run_scales()
        self.assertFalse(ben["judged_with_jev"])
        self.assertIsNone(ben["goes_to_point"])
        self.assertEqual(ben["substantive_exchanges"], 4)
        self.assertEqual(ben["topics"], {})
        html = (self.folder / "INT-002-ben-scales.html").read_text(encoding="utf-8")
        self.assertIn("read this scale by hand", html)

    def test_scales_put_the_whole_round_on_the_bar(self):
        self.run_scales()
        html = (self.folder / "INT-001-ana-scales.html").read_text(encoding="utf-8")
        self.assertIn("Ána · 135", html)
        self.assertIn("Ben", html)
        self.assertEqual(html.count("<svg"), 3)

    def test_hand_count_sheet_is_never_overwritten(self):
        self.run_scales()
        sheet = self.folder / "INT-001-ana-hand-count.md"
        text = sheet.read_text(encoding="utf-8")
        self.assertIn("| x002 |", text)
        self.assertNotIn("| x001 |", text, "logistics rows are left out")
        sheet.write_text(text + "\nmy own counts\n", encoding="utf-8")
        self.run_scales()
        self.assertIn("my own counts", sheet.read_text(encoding="utf-8"))

    def test_values_off_the_axis_stay_on_the_bar(self):
        self.assertEqual(feedback_scales.position(-5, feedback_scales.POINT_AXIS), feedback_scales.X0)
        self.assertEqual(feedback_scales.position(99, feedback_scales.TELL_AXIS), feedback_scales.X1)


class JevIsOptional(unittest.TestCase):
    """No key never breaks anything: exit code 2, and the feedback goes on."""

    def test_no_key_exits_with_code_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = Path(tmp) / "INT-001-a.jsonl"
            items.write_text(json.dumps({"id": "x001", "state": {"q": "a"}}) + "\n", encoding="utf-8")
            env = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
            env["HOME"] = tmp
            r = subprocess.run([sys.executable, str(SCRIPTS / "classify_exchanges.py"),
                                "--items", str(items), "--pack", str(SCRIPTS / "packs" / "branches.en.json"),
                                "--out", str(Path(tmp) / "out.csv")],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertFalse((Path(tmp) / "out.csv").exists())

    def test_unbuilt_depth_pack_is_refused(self):
        with self.assertRaises(ValueError):
            jev_client.load_pack(SCRIPTS / "packs" / "depth.en.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
