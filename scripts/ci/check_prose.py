#!/usr/bin/env python3
"""Check repository prose with the pinned SlopMonster scorer."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "vendor" / "slopmonster"


# Verify imported vendor files from upstream
def verify_vendor() -> None:
    manifest = json.loads((VENDOR / "UPSTREAM.json").read_text(encoding="utf-8"))
    for name in ("deslop.py", "LICENSE"):
        actual = hashlib.sha256((VENDOR / name).read_bytes()).hexdigest()
        if actual != manifest["sha256"][name]:
            raise ValueError(f"vendored {name} does not match UPSTREAM.json")


# Selects documentation for prose check and fails if missing
def markdown_inputs() -> list[Path]:
    if not (ROOT / "README.md").is_file():
        raise ValueError("required README.md is missing")
    if not (ROOT / "docs").is_dir():
        raise ValueError("required docs/ directory is missing")

    listed = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            "README.md",
            "docs/",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    # Preserves filenames and builds set with parsed filenames
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}
    # Returns existing markdown files, excluding deleted tracked files
    return sorted(path for path in paths if path.suffix == ".md" and path.is_file())


# Executing function
def main() -> int:
    if len(sys.argv) != 1:
        print(
            "ERROR lint-prose: this command accepts no path arguments.", file=sys.stderr
        )
        return 2

    try:
        verify_vendor()
        paths = markdown_inputs()
        if not paths:
            raise ValueError("no Markdown inputs were selected")

        failures = 0
        for path in paths:
            print(f"RUN lint-prose: {path.relative_to(ROOT)}", flush=True)
            result = subprocess.run(
                [sys.executable, str(VENDOR / "deslop.py"), str(path)],
                cwd=ROOT,
                check=False,
            )
            if result.returncode != 0:
                failures += 1
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"ERROR lint-prose: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"FAIL lint-prose: {failures} file(s) returned nonzero.", file=sys.stderr)
        return 1

    print(f"PASS lint-prose: {len(paths)} file(s) checked.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
