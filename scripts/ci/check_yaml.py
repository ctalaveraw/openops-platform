#!/usr/bin/env python3
"""Lint repository YAML with the pinned yamllint configuration."""

import os
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] # later refactor
CONFIG = ROOT / ".yamllint.yaml"


def yaml_inputs() -> list[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}
    return sorted(
        path
        for path in paths
        if path.suffix in {".yaml", ".yml"}
        and path.relative_to(ROOT).parts[0] != "vendor"
        and path.is_file()
    )


def main() -> int:
    if len(sys.argv) != 1:
        print("ERROR lint-yaml: this command accepts no path arguments.", file=sys.stderr)
        return 2

    if find_spec("yamllint") is None:
        print("ERROR lint-yaml: yamllint is missing. Run make setup.", file=sys.stderr)
        return 2

    try:
        if not CONFIG.is_file():
            raise ValueError("required .yamllint.yaml is missing")
        paths = yaml_inputs()
        if not paths:
            raise ValueError("no YAML inputs were selected")

        print(f"RUN lint-yaml: {len(paths)} file(s)", flush=True)
        result = subprocess.run(
            [
                sys.executable, "-m", "yamllint",
                "--strict", "--format", "standard",
                "--config-file", str(CONFIG),
                "--",
                *(str(path) for path in paths),
            ],
            cwd=ROOT,
            check=False,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR lint-yaml: {error}", file=sys.stderr)
        return 2

    if result.returncode == 0:
        print("PASS lint-yaml", flush=True)
        return 0
    if result.returncode in (1, 2):
        print("FAIL lint-yaml: fix the reported problems.", file=sys.stderr)
        return 1

    print(f"ERROR lint-yaml: checker exited {result.returncode}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
