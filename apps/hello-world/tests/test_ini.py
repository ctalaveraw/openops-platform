"""Check the INI specimen and duplicate-key rejection."""

import configparser
import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_ini import load_ini

ROOT = Path(__file__).resolve().parents[1]


class IniTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_ini(ROOT / "fixtures/hello.ini")["id"], "001")

    def test_duplicate_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.ini"
            path.write_text(
                (ROOT / "fixtures/hello.ini").read_text(encoding="utf-8")
                + "\nid=002\n",
                encoding="utf-8",
            )
            with self.assertRaises(configparser.DuplicateOptionError):
                load_ini(path)
