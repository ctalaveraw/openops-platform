"""Test invalid prose configuration and checker failures."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ci import check_prose


class ProseFailureTests(unittest.TestCase):
    def test_invalid_manifest_entries_fail(self) -> None:
        cases = (
            "",
            "README.md\\nREADME.md\\n",
            "../outside.md\\n",
            "/tmp/outside.md\\n",
            "README.txt\\n",
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "scripts/ci/required-prose.txt"
            manifest.parent.mkdir(parents=True)

            for content in cases:
                with self.subTest(content=content):
                    manifest.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        check_prose.required_markdown_inputs(root)

    def test_missing_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                check_prose.required_markdown_inputs(Path(directory))

    def test_unknown_cli_argument_fails(self) -> None:
        with patch.object(sys, "argv", ["check_prose.py", "--invalid"]):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(check_prose.main(), 2)

    def test_missing_vendor_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(check_prose, "VENDOR", Path(directory) / "missing"),
                patch.object(sys, "argv", ["check_prose.py", "--required"]),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(check_prose.main(), 2)

    def test_checker_failure_propagates(self) -> None:
        with (
            patch.object(check_prose, "verify_vendor"),
            patch.object(
                check_prose,
                "required_markdown_inputs",
                return_value=[check_prose.ROOT / "README.md"],
            ),
            patch.object(
                check_prose.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(args=["deslop"], returncode=1),
            ),
            patch.object(sys, "argv", ["check_prose.py", "--required"]),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(check_prose.main(), 1)
