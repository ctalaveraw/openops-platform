"""Verify effective Git ignore and text-attribute rules."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import verify

ROOT = verify.ROOT


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
