"""Check CI test execution and empty-suite handling."""

import tempfile
import unittest
from pathlib import Path

from scripts.ci import run_ci_tests


class CiRunnerTests(unittest.TestCase):
    def test_empty_suite_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(run_ci_tests.run_tests(Path(directory)), 2)

    def test_missing_directory_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            self.assertEqual(run_ci_tests.run_tests(missing), 2)

    def test_discovered_passing_test_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test_example.py"

            path.write_text(
                "import unittest\n"
                "class Example(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )

            self.assertEqual(run_ci_tests.run_tests(Path(directory)), 0)

    def test_discovered_failing_test_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test_failure.py"
            path.write_text(
                "import unittest\n"
                "class Broken(unittest.TestCase):\n"
                "    def test_fails(self):\n"
                "        self.fail('intentional failure')\n",
                encoding="utf-8",
            )
            self.assertEqual(run_ci_tests.run_tests(Path(directory)), 1)
