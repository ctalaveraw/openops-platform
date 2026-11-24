"""Check the Hello World JSON specimen."""

import json
import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_json import load_json

ROOT = Path(__file__).resolve().parents[1]


class JsonTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_json(ROOT / "fixtures/hello.json")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_json(path)
