#!/usr/bin/env python3
"""Install locked web tooling explicitly, or check application HTML and CSS."""

import os  # Decode Git filenames and pass the operator's environment to tools.
import subprocess  # Discover source files through Git.
import sys  # Return one status to Make and CI.
from pathlib import Path  # Locate the checkout without machine-specific paths.

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = {
    "html-validate": ROOT / ".htmlvalidate.json",
    "stylelint": ROOT / ".stylelintrc.json",
}
NPM_FLAGS = [
    "--ignore-scripts",  # Installation never runs package lifecycle scripts.
    "--no-audit",
    "--no-fund",
    "--no-update-notifier",
    "--cache",
    str(ROOT / ".venv" / "npm-cache"),  # Keep npm's cache inside ignored tooling.
]


def web_inputs() -> list[Path]:
    # App scope is independent of any specific component or pending app PR.
    listed = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            "apps/",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    selected = set()
    for name in listed.stdout.split(b"\0"):
        if not name:
            continue
        relative = Path(os.fsdecode(name))
        # Intentional negative fixtures have an explicit directory convention.
        invalid = any(
            relative.parts[index : index + 2] == ("fixtures", "invalid")
            for index in range(len(relative.parts) - 1)
        )
        if invalid or {"vendor", "node_modules"}.intersection(relative.parts):
            continue
        path = ROOT / relative
        if path.suffix in {".html", ".htm", ".css"} and path.is_file():
            selected.add(path)
    return sorted(selected)


def main() -> int:
    # Installation is an explicit operator mode. File selection stays fixed.
    if sys.argv[1:] not in ([], ["--setup"]):
        print("ERROR lint-web: use no arguments, or --setup.", file=sys.stderr)
        return 2

    try:
        # These functions use Node/npm from this Python environment's wheel.
        from nodejs_wheel import node, npm

        if sys.argv[1:] == ["--setup"]:
            print("RUN setup-web: install locked JavaScript tooling", flush=True)
            if npm(["ci", "--engine-strict", *NPM_FLAGS], cwd=ROOT):
                raise ValueError("npm ci failed")
            print("PASS setup-web", flush=True)
            return 0

        # Normal checks examine installed dependencies offline.
        # Capture the dependency tree so successful checks stay readable.
        installed = npm(
            ["ls", "--all", "--json", "--offline", *NPM_FLAGS],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            return_completed_process=True,
        )
        if installed.returncode:
            raise ValueError(
                "JavaScript tooling is missing or outdated; run make setup"
            )

        paths = web_inputs()
        if not paths:
            print("SKIP lint-web: no application HTML or CSS selected.", flush=True)
            return 0

        print(f"RUN lint-web: {len(paths)} file(s)", flush=True)
        failures = 0
        for path in paths:
            try:
                source = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as error:
                print(
                    f"FAIL lint-web: {path.relative_to(ROOT)}: {error}", file=sys.stderr
                )
                failures += 1
                continue

            # HTML receives both markup validation and embedded CSS checks.
            tools = ["stylelint"] if path.suffix == ".css" else list(CONFIGS)
            failed = False
            for tool in tools:
                print(f"RUN lint-web: {tool}: {path.relative_to(ROOT)}", flush=True)
                cli = ROOT / "node_modules" / tool / "bin" / f"{tool}.mjs"
                status = node(
                    [
                        str(cli),
                        "--config",
                        str(CONFIGS[tool]),
                        "--max-warnings",
                        "0",
                        "--stdin",
                        "--stdin-filename",
                        str(path),
                    ],
                    cwd=ROOT,
                    input=source,
                    text=True,
                )
                # Each linter assigns its own status to ordinary findings.
                finding_status = 1 if tool == "html-validate" else 2
                if status not in (0, finding_status):
                    raise ValueError(f"{tool} could not complete; exit status {status}")
                failed = failed or status != 0
            failures += failed

    except (ImportError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR lint-web: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"FAIL lint-web: {failures} file(s) failed.", file=sys.stderr)
        return 1

    print("PASS lint-web", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
