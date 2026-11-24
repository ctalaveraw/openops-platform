"""Verify successful and rejected web manifest inputs."""

import json
import tempfile
import unittest
from pathlib import Path

from checks.validate_manifest import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_valid_manifest(self) -> None:
        validate_manifest(ROOT / "public/site.webmanifest")

    def test_external_icon_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "site.webmanifest"
            data = json.loads(
                (ROOT / "public/site.webmanifest").read_text(encoding="utf-8")
            )
            data["icons"][0]["src"] = "https://example.invalid/icon.svg"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "wrong icon"):
                validate_manifest(path)

    def test_external_start_url_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "site.webmanifest"
            data = json.loads(
                (ROOT / "public/site.webmanifest").read_text(encoding="utf-8")
            )
            data["start_url"] = "https://example.invalid/"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "wrong start URL"):
                validate_manifest(path)

    def test_invalid_json_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "site.webmanifest"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                validate_manifest(path)
