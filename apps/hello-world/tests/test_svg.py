"""Test valid and invalid SVG inputs."""

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from checks.validate_svg import validate_svg


ROOT = Path(__file__).resolve().parents[1]


class SvgValidationTests(unittest.TestCase):
    def test_valid_svg_passes(self) -> None:
        validate_svg(ROOT / "public/favicon.svg")

    def test_non_svg_xml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.svg"
            path.write_text("<not-svg/>", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "wrong SVG root"):
                validate_svg(path)

    def test_malformed_xml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.svg"
            path.write_text("<svg", encoding="utf-8")

            with self.assertRaises(ET.ParseError):
                validate_svg(path)

    def test_missing_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.svg"

            with self.assertRaises(FileNotFoundError):
                validate_svg(path)

    def test_wrong_viewbox_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "favicon.svg"
            source = (ROOT / "public/favicon.svg").read_text(encoding="utf-8")
            path.write_text(
                source.replace('viewBox="0 0 64 64"', 'viewBox="0 0 32 32"'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "viewBox"):
                validate_svg(path)

    def test_missing_title_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "favicon.svg"
            source = (ROOT / "public/favicon.svg").read_text(encoding="utf-8")
            path.write_text(
                source.replace("OpenOps star", "Different title"), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "missing icon title"):
                validate_svg(path)
