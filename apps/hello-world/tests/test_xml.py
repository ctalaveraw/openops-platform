"""Check the Hello World XML specimen."""

import tempfile
import unittest
from pathlib import Path

from checks.formats.validate_xml import load_xml

ROOT = Path(__file__).resolve().parents[1]


class XmlTests(unittest.TestCase):
    def test_current_fixture_passes(self) -> None:
        self.assertEqual(load_xml(ROOT / "fixtures/hello.xml")["id"], "001")

    def test_invalid_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hello.xml"
            path.write_text("<episode><id>001</id></episode>", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_xml(path)
