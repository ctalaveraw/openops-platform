"""Exercise real verifier failures using temporary source fixtures."""

import configparser
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import verify

ROOT = verify.ROOT


class ChangedFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for name in ("public", "fixtures", "schemas"):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copyfile(ROOT / "VERSION", self.root / "VERSION")
        context = patch.object(verify, "ROOT", self.root)
        context.start()
        self.addCleanup(context.stop)

    def test_missing_linked_asset_fails(self) -> None:
        (self.root / "public/style.css").unlink()
        with self.assertRaisesRegex(ValueError, "missing asset"):
            verify.verify_static()

    def test_manifest_rejects_external_icon_and_start_url(self) -> None:
        path = self.root / "public/site.webmanifest"
        original = path.read_text(encoding="utf-8")
        for field in ("icons", "start_url"):
            with self.subTest(field=field):
                manifest = json.loads(original)
                if field == "icons":
                    manifest[field][0]["src"] = "https://example.invalid/icon.svg"
                else:
                    manifest[field] = "https://example.invalid/"
                path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "site.webmanifest"):
                    verify.verify_static()

    def test_svg_rejects_non_svg_xml(self) -> None:
        (self.root / "public/favicon.svg").write_text("<icon/>", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "wrong SVG root"):
            verify.verify_static()

    def test_equal_but_invalid_versions_fail(self) -> None:
        for name in ("VERSION", "public/version.txt"):
            (self.root / name).write_text("not-a-version\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "VERSION:"):
            verify.verify_static()

    def test_changed_record_fails_actual_parity_check(self) -> None:
        path = self.root / "fixtures/hello.csv"
        path.write_text("id,title,status\n001,Wrong,ready\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "csv: expected"):
            verify.verify_formats()

    def test_incomplete_csv_record_fails_loader(self) -> None:
        path = self.root / "fixtures/hello.csv"
        path.write_text("id,title,status\n001,Hello\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "expected one complete"):
            verify.load_delimited(path, ",")

    def test_duplicate_properties_fail_loader(self) -> None:
        path = self.root / "fixtures/hello.properties"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("id=002\n")
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            verify.verify_formats()

    def test_duplicate_ini_keys_fail_loader(self) -> None:
        path = self.root / "fixtures/hello.ini"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("id = 002\n")
        with self.assertRaises(configparser.DuplicateOptionError):
            verify.verify_formats()

    def test_wrong_xml_shape_fails_loader(self) -> None:
        path = self.root / "fixtures/hello.xml"
        path.write_text("<episode><id>001</id></episode>\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unexpected XML fields"):
            verify.verify_formats()
