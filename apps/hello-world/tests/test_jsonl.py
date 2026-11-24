"""Check the Hello World JSONL specimen."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_jsonl import load_jsonl

ROOT = Path(__file__).resolve().parents[1]


class JsonlTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_jsonl(ROOT / "fixtures/hello.jsonl")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.jsonl"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_jsonl(path)
