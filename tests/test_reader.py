"""Synthetic staged-reading checks, not claims of independent comprehension."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labo_tools import reader  # noqa: E402
from labo_tools.reader import (  # noqa: E402
    ReadingError, next_reading, observe_reading, reading_status, start_reading,
)


SOURCE = "writing/example/section.tex"
SESSION = "research/reviews/first-reader.json"
SPOILER = "FUTURE_HEADING_AND_RESCUE_SENTINEL"
TEXT = "Question: what is the object?\r\nVisible relation α → β.\n" + SPOILER + "\nFinal answer."


class ReadingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / SOURCE
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(TEXT.encode("utf-8"))
        self.session = self.root / SESSION
        self.session.parent.mkdir(parents=True)

    def start(self, **kwargs):
        return start_reading(self.root, SOURCE, SESSION, "Synthetic reader", **kwargs)

    def observe(self, **kwargs):
        return observe_reading(self.root, SESSION, "I can recover the question.",
                               "The object's domain is not yet given.", **kwargs)

    def state(self):
        return json.loads(self.session.read_text(encoding="utf-8"))

    def put_state(self, data):
        self.session.write_text(json.dumps(data), encoding="utf-8")

    def unchanged_error(self, function, *args, **kwargs):
        before = self.session.read_bytes()
        with self.assertRaises(ReadingError):
            function(*args, **kwargs)
        self.assertEqual(self.session.read_bytes(), before)
        self.assertFalse(Path(str(self.session) + ".lock").exists())

    def test_prefix_only_explicit_lifecycle_and_exact_bytes(self):
        before = self.source.read_bytes()
        summary = self.start(mode="independent")
        self.assertEqual(summary["through_line"], 0)
        self.assertFalse(summary["awaiting_observation"])
        for result in (summary, reading_status(self.root, SESSION)):
            rendered = json.dumps(result)
            for hidden in (SPOILER, SOURCE, str(self.root), "Final answer", "source", "lines"):
                self.assertNotIn(hidden, rendered)
        result = next_reading(self.root, SESSION, 1)
        self.assertEqual(result["text"].encode(), before.splitlines(keepends=True)[0])
        self.assertNotIn(SPOILER, json.dumps(result))
        self.assertEqual(result["prefix_sha256"], hashlib.sha256(result["text"].encode()).hexdigest())
        self.assertTrue(result["awaiting_observation"])
        self.observe()
        result = next_reading(self.root, SESSION, 2)
        self.assertEqual(result["text"], "".join(TEXT.splitlines(keepends=True)[:2]))
        self.assertNotIn(SPOILER, json.dumps(result))
        self.observe()
        result = next_reading(self.root, SESSION, 4)
        self.assertEqual(result["text"].encode(), before)
        self.assertIn(SPOILER, result["text"])
        self.assertEqual(self.source.read_bytes(), before)

    def test_observation_gating_strict_growth_and_bounds(self):
        self.start()
        self.unchanged_error(observe_reading, self.root, SESSION, "understood", "none")
        for boundary in (0, -1, 5, True, 1.0, "1"):
            self.unchanged_error(next_reading, self.root, SESSION, boundary)
        next_reading(self.root, SESSION, 2)
        self.unchanged_error(next_reading, self.root, SESSION, 3)
        self.unchanged_error(self.observe, rescue=True)
        self.unchanged_error(observe_reading, self.root, SESSION, " ", "none")
        self.unchanged_error(observe_reading, self.root, SESSION, "understood", "")
        self.observe()
        for boundary in (1, 2, 5):
            self.unchanged_error(next_reading, self.root, SESSION, boundary)
        next_reading(self.root, SESSION, 3)

    def test_initial_observation_is_never_replaced_and_rescues_are_separate(self):
        self.start()
        next_reading(self.root, SESSION, 1)
        self.observe()
        first = copy.deepcopy(self.state()["events"][1])
        self.unchanged_error(self.observe)
        for text in ("Reference resolved it.", "Author explanation resolved it later."):
            observe_reading(self.root, SESSION, text, "No remaining confusion.", rescue=True)
        events = self.state()["events"]
        self.assertEqual(events[1], first)
        self.assertEqual([e["kind"] for e in events], ["exposure", "initial", "rescue", "rescue"])
        status = reading_status(self.root, SESSION)
        self.assertEqual(status["exposures"], [
            {"through_line": 1, "initial_recorded": True, "rescue_count": 2},
        ])
        self.assertNotIn("Reference resolved", json.dumps(status))

    def test_status_is_read_only_even_when_lock_exists(self):
        self.start()
        before = self.session.read_bytes()
        lock = Path(str(self.session) + ".lock")
        lock.write_text("Do not clear a possibly live coordinator lock.")
        status = reading_status(self.root, SESSION)
        self.assertEqual(status["through_line"], 0)
        self.assertEqual(self.session.read_bytes(), before)
        with self.assertRaises(ReadingError):
            next_reading(self.root, SESSION, 1)
        self.assertTrue(lock.exists())
        self.assertEqual(self.session.read_bytes(), before)

    def test_changed_source_rejects_every_operation_without_refresh(self):
        self.start()
        next_reading(self.root, SESSION, 1)
        self.source.write_text(TEXT + "Changed source.\n", encoding="utf-8")
        for function, args in (
            (reading_status, (self.root, SESSION)),
            (next_reading, (self.root, SESSION, 2)),
            (observe_reading, (self.root, SESSION, "understood", "none")),
        ):
            self.unchanged_error(function, *args)

    def test_same_bytes_replaced_source_is_a_different_identity(self):
        self.start()
        replacement = self.source.with_suffix(".new")
        replacement.write_bytes(self.source.read_bytes())
        replacement.replace(self.source)
        self.unchanged_error(reading_status, self.root, SESSION)

    def test_existing_session_parent_policy_and_paths_are_never_overwritten(self):
        self.start()
        original = self.session.read_bytes()
        self.unchanged_error(self.start)
        self.assertEqual(self.session.read_bytes(), original)
        self.assertFalse((self.root / "missing").exists())
        with self.assertRaises(ReadingError):
            start_reading(self.root, SOURCE, "missing/session.json", "Reader")
        self.assertFalse((self.root / "missing").exists())
        for unsafe in ("../outside", "/tmp/outside", "C:/outside", "C:outside",
                       "writing/../outside", "./writing/example/section.tex", "x\\y", ""):
            for target in ("source", "session"):
                with self.subTest(unsafe=unsafe, target=target):
                    with self.assertRaises(ReadingError):
                        start_reading(self.root, unsafe if target == "source" else SOURCE,
                                      unsafe if target == "session" else "research/reviews/new.json", "Reader")
        with self.assertRaises(ReadingError):
            start_reading(reader._workspace.__globals__["CHECKOUT"], SOURCE, SESSION, "Reader")

    def test_symlinked_source_session_ancestors_and_locks_rejected(self):
        linked_source = self.root / "source.tex"
        linked_source.symlink_to(self.source)
        with self.assertRaises(ReadingError):
            start_reading(self.root, "source.tex", SESSION, "Reader")
        (self.root / "linked").symlink_to(self.session.parent, target_is_directory=True)
        with self.assertRaises(ReadingError):
            start_reading(self.root, SOURCE, "linked/session.json", "Reader")
        self.session.symlink_to(self.source)
        before = self.source.read_bytes()
        with self.assertRaises(ReadingError):
            self.start()
        self.assertEqual(self.source.read_bytes(), before)
        self.session.unlink()
        self.start()
        Path(str(self.session) + ".lock").symlink_to(self.source)
        original = self.session.read_bytes()
        with self.assertRaises(ReadingError):
            next_reading(self.root, SESSION, 1)
        self.assertEqual(self.session.read_bytes(), original)
        self.assertEqual(self.source.read_bytes(), before)

    def test_unknown_fields_tamper_bad_hashes_and_bad_yaml_are_rejected(self):
        self.start()
        next_reading(self.root, SESSION, 1)
        self.observe()
        pristine = self.state()
        mutations = [
            lambda d: d.update(extra="bad"),
            lambda d: d["header"].update(schema_version=True),
            lambda d: d["header"].update(reader="Changed reader"),
            lambda d: d["header"].update(mode=[]),
            lambda d: d["header"]["source"].update(sha256="not a hash"),
            lambda d: d["events"][0].update(through_line=2),
            lambda d: d["events"][1].update(understanding="Rewritten first observation"),
            lambda d: d["events"][0].update(prefix_sha256="f" * 64),
            lambda d: d["events"].pop(),
            lambda d: d.update(events=[]),
            lambda d: d.update(events="not a list"),
        ]
        for mutate in mutations:
            data = copy.deepcopy(pristine)
            mutate(data)
            self.put_state(data)
            self.unchanged_error(reading_status, self.root, SESSION)
        for malformed in ("{bad: [", "header: 1\nheader: 2\n", "!!python/object:builtins.object {}", "[]"):
            self.session.write_text(malformed, encoding="utf-8")
            self.unchanged_error(reading_status, self.root, SESSION)

    def test_schema_checks_history_even_if_chain_is_recomputed(self):
        self.start()
        next_reading(self.root, SESSION, 1)
        self.observe()
        pristine = self.state()
        for change in ("repeat-exposure", "duplicate-initial", "rescue-before-initial", "bad-prefix"):
            data = copy.deepcopy(pristine)
            if change == "repeat-exposure":
                data["events"].append(copy.deepcopy(data["events"][0]))
            elif change == "duplicate-initial":
                data["events"].append(copy.deepcopy(data["events"][1]))
            elif change == "rescue-before-initial":
                data["events"][1]["kind"] = "rescue"
            else:
                data["events"][0]["prefix_sha256"] = "f" * 64
            previous = data["header_sha256"]
            for event in data["events"]:
                event["previous"] = previous
                event.pop("sha256", None)
                event["sha256"] = reader._digest(event)
                previous = event["sha256"]
            data["history_sha256"] = previous
            self.put_state(data)
            self.unchanged_error(reading_status, self.root, SESSION)

    def test_json_and_yaml_and_session_identity(self):
        self.start()
        self.session.write_text(yaml.safe_dump(self.state()), encoding="utf-8")
        reading_status(self.root, SESSION)
        other = self.session.with_name("copied.json")
        other.write_bytes(self.session.read_bytes())
        with self.assertRaises(ReadingError):
            reading_status(self.root, other.relative_to(self.root).as_posix())

    def test_bad_source_and_bounded_metadata(self):
        for raw in (b"", b"\xff"):
            self.source.write_bytes(raw)
            with self.assertRaises(ReadingError):
                self.start()
            self.assertFalse(self.session.exists())
        self.source.write_bytes(TEXT.encode())
        self.start()
        with patch.object(reader, "MAX_SESSION_BYTES", 10):
            self.unchanged_error(reading_status, self.root, SESSION)

    def test_private_parser_and_path_errors_do_not_echo_spoilers(self):
        self.start()
        self.session.write_text("{bad: [" + SPOILER, encoding="utf-8")
        with self.assertRaises(ReadingError) as caught:
            reading_status(self.root, SESSION)
        self.assertNotIn(SPOILER, str(caught.exception))
        with self.assertRaises(ReadingError) as caught:
            start_reading(self.root, "../" + SPOILER, "research/reviews/other.json", "Reader")
        self.assertNotIn(SPOILER, str(caught.exception))

    def test_failed_atomic_publication_preserves_original_and_cleans_temporaries(self):
        self.start()
        with patch.object(reader.os, "replace", side_effect=OSError("synthetic failure")):
            self.unchanged_error(next_reading, self.root, SESSION, 1)
        self.assertEqual(list(self.session.parent.glob(".reading-*")), [])


if __name__ == "__main__":
    unittest.main()
