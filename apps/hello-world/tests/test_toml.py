"""Check the Hello World TOML specimen."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_toml import load_toml

ROOT = Path(__file__).resolve().parents[1]


class TomlTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_toml(ROOT / "fixtures/hello.toml")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.toml"
            path.write_text("[episode\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_toml(path)
