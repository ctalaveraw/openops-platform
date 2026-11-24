"""Check the Hello World CSV specimen."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_csv import load_csv

ROOT = Path(__file__).resolve().parents[1]


class CsvTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_csv(ROOT / "fixtures/hello.csv")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.csv"
            path.write_text("id,title,status\\n001,Hello\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_csv(path)
