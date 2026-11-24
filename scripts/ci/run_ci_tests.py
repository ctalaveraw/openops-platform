#!/usr/bin/env python3
"""Run root CI tests and reject an empty test suite."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "tests/ci"


def run_tests(directory: Path) -> int:
    if not directory.is_dir():
        print(f"ERROR test-ci: missing {directory}", file=sys.stderr)
        return 2

    try:
        suite = unittest.TestLoader().discover(str(directory), pattern="test_*.py")
    except (ImportError, OSError, ValueError) as error:
        print(f"ERROR test-ci: {error}", file=sys.stderr)
        return 2

    if suite.countTestCases() == 0:
        print("ERROR test-ci: no tests discovered", file=sys.stderr)
        return 2

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main() -> int:
    if len(sys.argv) != 1:
        print("ERROR test-ci: no arguments accepted", file=sys.stderr)
        return 2
    return run_tests(TEST_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
