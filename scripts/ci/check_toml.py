#!/usr/bin/env python3
"""Check repository TOML and the root uv lockfile without rewriting them."""

import os  # Decode Git filenames using the filesystem encoding.
import subprocess  # Ask Git which files belong to the check.
import sys  # Return the wrapper's status to Make or the calling shell.
import tomllib  # Python 3.12 already includes a TOML 1.0 parser.
from pathlib import Path  # Find this checkout without hardcoded machine paths.

ROOT = Path(__file__).resolve().parents[2]
LOCKFILE = ROOT / "uv.lock"


def toml_inputs() -> list[Path]:
    # Include tracked files and new files that Git does not ignore.
    # NUL separators preserve spaces and newlines inside filenames.
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}

    # uv.lock contains TOML despite its filename. Include it explicitly.
    # Skip tracked deletions and sort paths for stable diagnostic ordering.
    return sorted(
        path
        for path in paths
        if (path.suffix == ".toml" or path == LOCKFILE) and path.is_file()
    )


def main() -> int:
    # Fixed selection prevents callers from narrowing the required check.
    if len(sys.argv) != 1:
        print(
            "ERROR lint-toml: this command accepts no path arguments.", file=sys.stderr
        )
        return 2

    try:
        paths = toml_inputs()
        if not paths:
            raise ValueError("no TOML inputs were selected")

        print(f"RUN lint-toml: {len(paths)} file(s)", flush=True)
        failures = 0
        for path in paths:
            try:
                # tomllib.load expects a binary file and decodes it as UTF-8.
                # The with block closes the file even when parsing fails.
                with path.open("rb") as source:
                    tomllib.load(source)
            except (
                tomllib.TOMLDecodeError,
                UnicodeDecodeError,
                RecursionError,
            ) as error:
                # Invalid content is a finding. Continue checking other files.
                print(
                    f"FAIL lint-toml: {path.relative_to(ROOT)}: {error}",
                    file=sys.stderr,
                )
                failures += 1

    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        # Discovery and file-access failures mean the check could not complete.
        print(f"ERROR lint-toml: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"FAIL lint-toml: {failures} file(s) failed.", file=sys.stderr)
        return 1

    print("PASS lint-toml", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
