#!/usr/bin/env python3
"""Lint this checkout's Markdown with repository-owned settings."""

import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

# resolve this script as a system path, relative to current repo layout ## REFACTOR FOR BETTER PATHING
ROOT = Path(__file__).resolve().parents[2]

def main() -> int:

    # check if interpreter can find PyMarkdown, exit code 2 if not found
    if find_spec("pymarkdown") is None:
        print(
            "PyMarkdown is missing. Run make setup.",
            file=sys.stderr,
        )
        return 2

 print("RUN lint-markdown: repository Markdown (Git ignores applied)", flush=True)
    
    # construct the PyMarkdown command  
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pymarkdown",
            "--return-code-scheme",
            "explicit",
            "--strict-config",
            "--config",
            str(ROOT / ".pymarkdown.json"),
            "scan",
            "--recurse",
            "--respect-gitignore",
            ".",
        ],
        cwd=ROOT,
        check=False,
    )

    # PyMarkdown's explicit scheme distinguishes empty scope from findings.
    if result.returncode == 0:
        print("PASS lint-markdown", flush=True)
    # Exit code 1 means no inputs
    elif result.returncode == 1:
        print(
            "ERROR lint-markdown: no Markdown inputs; inspect scope and Git ignores.",
            file=sys.stderr,
        )
    # Exit code 4 means rule was enforced
    elif result.returncode == 4:
        print("FAIL lint-markdown: fix the reported rules.", file=sys.stderr)
    # Catch other exit codes as error
    else:
        print(
            f"ERROR lint-markdown: checker exited {result.returncode}.",
            file=sys.stderr,
        )
    return result.returncode

# returns integer from PyMarkdown becomes exit code of script
if __name__ == "__main__":
    raise SystemExit(main())

