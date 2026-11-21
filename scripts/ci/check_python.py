#!/usr/bin/env python3
"""Check repository Python with the pinned Ruff linter and formatter."""

import os  # Decode Git filenames using the filesystem encoding.
import subprocess  # Run Git and Ruff as child processes.
import sys  # Reuse this interpreter and return a process exit status.
from importlib.util import find_spec  # Check whether Ruff is installed.
from pathlib import Path  # Build paths independently of the caller's directory.

# Layout: <checkout>/scripts/ci/check_python.py
# parents[0] = ci/, parents[1] = scripts/, parents[2] = <checkout>.
ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "pyproject.toml"


def python_inputs() -> list[Path]:
    # Include tracked files and new files that Git does not ignore.
    # NUL separators preserve spaces and newlines inside filenames.
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,  # A failed discovery command must fail this check.
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}

    # Keep existing Python source/stubs; skip pinned upstream source.
    # Sorting gives a stable order, and is_file() skips tracked deletions.
    return sorted(
        path
        for path in paths
        if path.suffix in {".py", ".pyi"}
        and path.relative_to(ROOT).parts[0] != "vendor"
        and path.is_file()
    )


def main() -> int:
    # Keep the required scope fixed. Use Ruff directly for focused local work.
    if len(sys.argv) != 1:
        print(
            "ERROR lint-python: this command accepts no path arguments.",
            file=sys.stderr,
        )
        return 2

    try:
        if find_spec("ruff") is None:
            raise ValueError("Ruff is missing. Run make setup.")
        if not CONFIG.is_file():
            raise ValueError("required pyproject.toml is missing")

        paths = python_inputs()
        if not paths:
            raise ValueError("no Python inputs were selected")

        # Both commands inspect source. Neither applies fixes or writes a cache.
        checks = (
            ("lint", ["check", "--no-fix", "--no-cache"]),
            ("format", ["format", "--check", "--no-cache"]),
        )
        has_findings = False

        for label, arguments in checks:
            print(
                f"RUN lint-python: Ruff {label}, {len(paths)} file(s)",
                flush=True,
            )
            result = subprocess.run(
                [
                    sys.executable,  # Keep the interpreter selected by Make.
                    "-m",
                    "ruff",
                    *arguments,
                    "--config",
                    str(CONFIG),  # Always use this checkout's configuration.
                    "--",  # Everything after this is a filename.
                    *(str(path) for path in paths),
                ],
                cwd=ROOT,
                check=False,  # Inspect Ruff's status rather than raising on findings.
            )

            # Still run formatting after ordinary lint findings.
            if result.returncode == 1:
                has_findings = True
            elif result.returncode != 0:
                raise RuntimeError(f"Ruff {label} exited {result.returncode}")

    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR lint-python: {error}", file=sys.stderr)
        return 2

    if has_findings:
        print("FAIL lint-python: fix lint or formatting findings.", file=sys.stderr)
        return 1

    print("PASS lint-python", flush=True)
    return 0


if __name__ == "__main__":
    # Make and CI receive the integer returned by main().
    raise SystemExit(main())
