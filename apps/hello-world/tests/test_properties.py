"""Check the properties specimen and duplicate-key rejection."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_properties import load_properties

ROOT = Path(__file__).resolve().parents[1]


class PropertiesTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(
            load_properties(ROOT / "fixtures/hello.properties")["id"], "001"
        )

    def test_duplicate_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.properties"
            path.write_text(
                (ROOT / "fixtures/hello.properties").read_text(encoding="utf-8")
                + "id=002\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                load_properties(path)
