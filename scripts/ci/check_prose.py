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


def required_markdown_inputs(root: Path) -> list[Path]:
    """Select required documents from the repository manifest."""
    manifest = root / "scripts/ci/required-prose.txt"

    names = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not names:
        raise ValueError("required prose manifest is empty")

    if len(names) != len(set(names)):
        raise ValueError("duplicate required prose path")

    paths = []

    for name in names:
        relative = Path(name)

        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".md":
            raise ValueError(f"invalid required prose path: {name}")

        path = root / relative

        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"path escapes repository: {name}")

        if not path.is_file():
            raise ValueError(f"missing required prose document: {name}")

        paths.append(path)

    return paths


# Executing function
def main() -> int:
    if sys.argv[1:] not in ([], ["--required"]):
        print("ERROR lint-prose: expected no arguments or --required.", file=sys.stderr)
        return 2

    required = sys.argv[1:] == ["--required"]
    label = "check-required-prose" if required else "lint-prose"

    try:
        verify_vendor()
        paths = required_markdown_inputs(ROOT) if required else markdown_inputs()
        if not paths:
            raise ValueError("no Markdown inputs were selected")

        failures = 0
        for path in paths:
            print(f"RUN {label}: {path.relative_to(ROOT)}", flush=True)
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
        print(f"ERROR {label}: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"FAIL {label}: {failures} file(s) returned nonzero.", file=sys.stderr)
        return 1

    print(f"PASS {label}: {len(paths)} file(s) checked.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
