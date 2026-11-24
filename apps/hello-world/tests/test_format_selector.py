"""Check focused fixture selection without reducing the full gate."""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from checks.__main__ import ROOT, run_checks


class FormatSelectorTests(unittest.TestCase):
    def test_all_formats_pass(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_checks("formats", "all", ROOT), 0)

    def test_one_format_passes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_checks("formats", "json", ROOT), 0)

    def test_unknown_format_fails(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_checks("formats", "not-a-format", ROOT), 2)

    def test_changed_csv_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "fixtures", root / "fixtures")
            (root / "fixtures/hello.csv").write_text(
                "id,title,status\n001,Wrong,ready\n", encoding="utf-8"
            )
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(run_checks("formats", "csv", root), 1)
