"""Check the Hello World YAML specimen."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_yaml import load_fixture_yaml

ROOT = Path(__file__).resolve().parents[1]


class YamlTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_fixture_yaml(ROOT / "fixtures/hello.yaml")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.yaml"
            path.write_text("episode:\\n  unexpected: 1\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_fixture_yaml(path)
