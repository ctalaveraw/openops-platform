"""Check selection and failure handling in the local static-check runner."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from checks.__main__ import ROOT, run_checks


class StaticSelectorTests(unittest.TestCase):
    def test_all_registered_static_checks_pass(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_checks("static", "all", ROOT), 0)

    def test_unknown_selection_fails(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_checks("static", "not-a-check", ROOT), 2)

    def test_missing_input_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(run_checks("static", "svg", Path(directory)), 2)
