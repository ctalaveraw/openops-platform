"""A few tests for the static page and data fixtures."""

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts import verify


class FixtureTests(unittest.TestCase):
    def test_formats_agree(self) -> None:
        verify.verify_formats()
        self.assertEqual(
            set(verify.load_episode_formats()),
            {"json", "csv", "tsv", "xml", "yaml", "toml", "ini", "jsonl", "properties"},
        )

    def test_reject_malformed_json(self) -> None:
        with self.assertRaises(json.JSONDecodeError):
            json.loads((verify.ROOT / "fixtures/invalid/bad.json.txt").read_text())

    def test_reject_malformed_xml(self) -> None:
        with self.assertRaises(ET.ParseError):
            verify.load_xml(verify.ROOT / "fixtures/invalid/bad.xml")

    def test_reject_duplicate_csv(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected one complete"):
            verify.load_delimited(verify.ROOT / "fixtures/invalid/duplicate.csv", ",")

    def test_reject_wrong_tsv_delimiter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.tsv"
            path.write_text("id,title,status\n001,Hello,ready\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected columns"):
                verify.load_delimited(path, "\t")

    def test_reject_unsupported_yaml_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "other.yaml"
            path.write_text("episode:\n  unexpected: 1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected fixture layout"):
                verify.load_fixture_yaml(path)

    def test_reject_changed_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed.csv"
            path.write_text(
                "id,title,status\n001,Wrong title,ready\n", encoding="utf-8"
            )
            self.assertNotEqual(verify.load_delimited(path, ","), verify.EXPECTED)


class WebTests(unittest.TestCase):
    def test_static_files_and_metadata(self) -> None:
        verify.verify_static()

    def test_only_expected_runtime_assets_are_present(self) -> None:
        public = verify.ROOT / "public"
        self.assertEqual(
            {p.name for p in public.iterdir()},
            {
                "index.html",
                "style.css",
                "favicon.svg",
                "site.webmanifest",
                "robots.txt",
                "healthz",
                "version.txt",
            },
        )

    def test_banner_does_not_contain_javascript(self) -> None:
        html = (verify.ROOT / "public/index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script", html.lower())
        self.assertIn("<main", html)

    def test_container_copies_only_public(self) -> None:
        dockerfile = (verify.ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY public/ /usr/share/nginx/html/", dockerfile)
        self.assertNotIn("COPY . ", dockerfile)


if __name__ == "__main__":
    unittest.main()
