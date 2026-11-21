#!/usr/bin/env python3
"""Validate repository GitHub workflows with the pinned actionlint tool."""

import os  # Decode Git filenames and control the child process environment.
import subprocess  # Run tools directly, without evaluating shell command text.
import sys  # Use the current Python environment and return a process status.
from pathlib import Path  # Derive checkout paths from this script's location.

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
CONFIG = ROOT / ".github" / "actionlint.yaml"

# Native tools live beside the interpreter chosen by Make.
# Do not resolve Python's symlink out of its virtual environment.
ACTIONLINT = Path(sys.executable).with_name(
    "actionlint.exe" if os.name == "nt" else "actionlint"
)
SHELLCHECK = Path(sys.executable).with_name(
    "shellcheck.exe" if os.name == "nt" else "shellcheck"
)


def workflow_inputs() -> list[Path]:
    # Include tracked workflows and new workflows that Git does not ignore.
    # NUL separators keep unusual filenames intact.
    listed = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            ".github/workflows/",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}

    # GitHub loads workflow files directly inside this directory.
    # Skip tracked deletions; keep a stable order for diagnostics.
    return sorted(
        path
        for path in paths
        if path.parent == WORKFLOWS
        and path.suffix in {".yml", ".yaml"}
        and path.is_file()
    )


def main() -> int:
    # Required workflow validation always covers the whole selected scope.
    if len(sys.argv) != 1:
        print(
            "ERROR validate-actions: this command accepts no path arguments.",
            file=sys.stderr,
        )
        return 2

    try:
        for tool in (ACTIONLINT, SHELLCHECK):
            if not tool.is_file():
                raise ValueError(f"{tool.name} is missing. Run make setup.")
        if not CONFIG.is_file():
            raise ValueError("required .github/actionlint.yaml is missing")

        paths = workflow_inputs()
        if not paths:
            # This repository is expected to contain GitHub workflows.
            raise ValueError("no GitHub workflow inputs were selected")

        environment = os.environ.copy()
        # Give the embedded-shell checks one policy, regardless of user settings.
        environment["SHELLCHECK_OPTS"] = "--norc"

        # actionlint can silently omit an unavailable optional ShellCheck backend.
        # Check that our required backend can actually execute before using it.
        subprocess.run(
            [str(SHELLCHECK), "--version"],
            stdout=subprocess.DEVNULL,
            env=environment,
            check=True,
        )

        print(
            f"RUN validate-actions: actionlint, {len(paths)} workflow(s)",
            flush=True,
        )
        result = subprocess.run(
            [
                str(ACTIONLINT),
                "-no-color",
                "-config-file",
                str(CONFIG),
                "-shellcheck",
                str(SHELLCHECK),
                # Python program logic belongs in files checked by Ruff.
                # Disable optional Pyflakes instead of discovering a host tool.
                "-pyflakes=",
                "--",
                *(str(path) for path in paths),
            ],
            cwd=ROOT,
            env=environment,
            check=False,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR validate-actions: {error}", file=sys.stderr)
        return 2

    if result.returncode == 1:
        print("FAIL validate-actions: fix the workflow findings.", file=sys.stderr)
        return 1
    if result.returncode != 0:
        print(
            f"ERROR validate-actions: actionlint exited {result.returncode}.",
            file=sys.stderr,
        )
        return 2

    print("PASS validate-actions", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
