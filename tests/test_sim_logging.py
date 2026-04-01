"""Tests for psyflow.sim.logging — JSONL serialization and roundtrip."""

import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from psyflow.sim.logging import _to_jsonable, iter_sim_events, make_sim_jsonl_logger


class TestToJsonable(unittest.TestCase):
    """_to_jsonable() should flatten dataclasses, dicts, and lists."""

    def test_plain_values_pass_through(self):
        self.assertEqual(_to_jsonable(42), 42)
        self.assertEqual(_to_jsonable("hi"), "hi")
        self.assertIsNone(_to_jsonable(None))

    def test_nested_dict(self):
        result = _to_jsonable({"a": {"b": [1, 2]}})
        self.assertEqual(result, {"a": {"b": [1, 2]}})

    def test_dataclass_flattened(self):
        @dataclass
        class Pt:
            x: int
            y: int

        result = _to_jsonable(Pt(1, 2))
        self.assertEqual(result, {"x": 1, "y": 2})

    def test_nested_dataclass_in_dict(self):
        @dataclass
        class Inner:
            val: str

        result = _to_jsonable({"key": Inner("hello")})
        self.assertEqual(result, {"key": {"val": "hello"}})

    def test_list_of_mixed(self):
        @dataclass
        class Tag:
            name: str

        result = _to_jsonable([Tag("a"), 1, "b"])
        self.assertEqual(result, [{"name": "a"}, 1, "b"])


class TestLoggerRoundtrip(unittest.TestCase):
    """make_sim_jsonl_logger → iter_sim_events roundtrip."""

    def test_write_and_read_back(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.jsonl"
            logger = make_sim_jsonl_logger(path)

            logger({"type": "test", "value": 1})
            logger({"type": "test", "value": 2})

            events = list(iter_sim_events(path))
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["type"], "test")
            self.assertEqual(events[1]["value"], 2)
            # Auto-injected timestamps
            self.assertIn("t", events[0])
            self.assertIn("t_utc", events[0])

    def test_iter_nonexistent_file_yields_nothing(self):
        events = list(iter_sim_events("/tmp/does_not_exist_xyz.jsonl"))
        self.assertEqual(events, [])

    def test_iter_skips_blank_and_invalid_lines(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "messy.jsonl"
            path.write_text(
                '{"ok": true}\n'
                '\n'
                'not json\n'
                '{"also": "ok"}\n',
                encoding="utf-8",
            )
            events = list(iter_sim_events(path))
            self.assertEqual(len(events), 2)

    def test_logger_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sub" / "dir" / "events.jsonl"
            logger = make_sim_jsonl_logger(path)
            logger({"type": "init"})
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
