"""Check the Hello World TSV specimen."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_csv import load_tsv

ROOT = Path(__file__).resolve().parents[1]


class TsvTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_tsv(ROOT / "fixtures/hello.tsv")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.tsv"
            path.write_text("id,title,status\\n001,Hello,ready\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_tsv(path)
