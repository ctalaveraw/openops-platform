"""Reject changes to the fixture's source contracts without starting services."""

import configparser
import json
import os
import shutil
import subprocess
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


class GitMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        self.app = self.repo / "apps/hello-world"
        self.app.mkdir(parents=True)
        shutil.copyfile(ROOT.parents[1] / ".gitignore", self.repo / ".gitignore")
        shutil.copyfile(ROOT / ".gitattributes", self.app / ".gitattributes")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_ATTR_NOSYSTEM="1",
        )
        self.git("init", "-q", "--template=", check=True)

    def git(self, *args: str, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                "git",
                "-c",
                f"core.excludesFile={os.devnull}",
                "-c",
                f"core.attributesFile={os.devnull}",
                *args,
            ],
            cwd=self.repo,
            env=self.env,
            text=True,
            capture_output=True,
            check=check,
        )

    def assert_ignored(self, path: str, expected: bool) -> None:
        result = self.git("check-ignore", "--no-index", "-q", "--", path)
        self.assertEqual(result.returncode, 0 if expected else 1, result.stderr)

    def test_generated_files_are_ignored_but_source_is_not(self) -> None:
        for path in (
            ".venv/bin/python",
            "build/report.json",
            "site/index.html",
            "apps/hello-world/tests/__pycache__/sample.pyc",
            "apps/hello-world/node_modules/example/index.js",
        ):
            with self.subTest(path=path):
                self.assert_ignored(path, True)
        for path in ("public/index.html", "fixtures/hello.json", "tests/test_hello.py"):
            with self.subTest(path=path):
                self.assert_ignored(f"apps/hello-world/{path}", False)

    def test_source_ignore_regression_is_detected(self) -> None:
        with (self.repo / ".gitignore").open("a", encoding="utf-8") as stream:
            stream.write("\n/apps/hello-world/public/\n")
        with self.assertRaises(AssertionError):
            self.assert_ignored("apps/hello-world/public/index.html", False)

    def test_effective_git_attributes(self) -> None:
        for name in ("public/index.html", "fixtures/hello.csv", "fixtures/hello.sql"):
            path = f"apps/hello-world/{name}"
            result = self.git("check-attr", "text", "eol", "--", path, check=True)
            self.assertEqual(
                result.stdout.splitlines(), [f"{path}: text: set", f"{path}: eol: lf"]
            )


class PackagingSourceTests(unittest.TestCase):
    def test_dockerfile_keeps_the_small_source_contract(self) -> None:
        def check_source(source: str) -> None:
            lines = [
                line.strip()
                for line in source.splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            self.assertEqual(len(lines), 4)
            self.assertRegex(
                lines[0],
                r"^FROM nginx/nginx-unprivileged:stable-alpine@sha256:[a-f0-9]{64}$",
            )
            self.assertEqual(
                lines[1], 'LABEL org.opencontainers.image.title="OpenOps Hello World"'
            )
            self.assertEqual(
                lines[2:], ["COPY public/ /usr/share/nginx/html/", "EXPOSE 8080"]
            )

        source = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        check_source(source)
        with self.assertRaises(AssertionError):
            check_source(source.replace("COPY public/", "COPY ./"))

    def test_dockerignore_declares_the_expected_exclusions(self) -> None:
        # Literal specimen contract, not a Docker pattern-matching engine.
        rules = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            set(rules),
            {
                ".git/",
                "docs/",
                "fixtures/",
                "schemas/",
                "contracts/",
                "l10n/",
                "scripts/",
                "tests/",
                "__pycache__/",
                "*.md",
                "Makefile",
                "compose.yaml",
                "VERSION",
            },
        )
