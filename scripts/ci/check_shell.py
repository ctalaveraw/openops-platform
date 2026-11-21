#!/usr/bin/env python3
"""Check repository shell scripts with the pinned ShellCheck binary."""

import os  # Decode Git filenames and copy the child process environment.
import subprocess  # Run Git and ShellCheck without invoking a shell.
import sys  # Reuse this interpreter's environment and return an exit status.
from pathlib import Path  # Build paths from the script's location.

# Layout: <checkout>/scripts/ci/check_shell.py.
ROOT = Path(__file__).resolve().parents[2]

# Find the native tool beside the Python interpreter selected by Make.
# Keep the Python path unresolved so a venv symlink stays inside its venv.
SHELLCHECK = Path(sys.executable).with_name(
    "shellcheck.exe" if os.name == "nt" else "shellcheck"
)
SHELL_SUFFIXES = {".sh", ".bash", ".bats", ".dash", ".ksh"}
SHELL_NAMES = {"sh", "bash", "dash", "ksh"}


def is_shell_input(path: Path) -> bool:
    # Named shell files are checked even when they are not executable.
    if path.suffix in SHELL_SUFFIXES:
        return True
    if path.suffix:
        return False

    # Recognize common extensionless scripts by reading their first line.
    # Bound the read so a large binary without newlines stays cheap to inspect.
    with path.open("rb") as source:
        first_line = source.readline(4096)
    words = first_line[2:].split() if first_line.startswith(b"#!") else []

    # Handle both "#!/usr/bin/env bash" and "env -S bash ..." forms.
    if words and Path(os.fsdecode(words[0])).name == "env":
        words = words[1:]
        if words[:1] == [b"-S"]:
            words = words[1:]

    if not words:
        return False
    command = Path(os.fsdecode(words[0])).name
    return command in SHELL_NAMES or (command == "busybox" and words[1:2] == [b"sh"])


def shell_inputs() -> list[Path]:
    # Git supplies tracked files and new files that it does not ignore.
    # NUL separators preserve spaces and newlines inside filenames.
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}

    # Skip pinned upstream source and tracked deletions before inspecting files.
    return sorted(
        path
        for path in paths
        if path.relative_to(ROOT).parts[0] != "vendor"
        and path.is_file()
        and is_shell_input(path)
    )


def main() -> int:
    # Keep the repository gate's scope fixed, as with our other wrappers.
    if len(sys.argv) != 1:
        print(
            "ERROR lint-shell: this command accepts no path arguments.",
            file=sys.stderr,
        )
        return 2

    try:
        if not SHELLCHECK.is_file():
            raise ValueError("ShellCheck is missing. Run make setup.")

        paths = shell_inputs()
        if not paths:
            # An empty shell scope is valid before the repo has shell scripts.
            print("SKIP lint-shell: no shell scripts selected.", flush=True)
            return 0

        # Ignore machine-specific options and automatic configuration discovery.
        # The gate's settings live here so local and hosted runs use one policy.
        environment = os.environ.copy()
        environment.pop("SHELLCHECK_OPTS", None)

        print(f"RUN lint-shell: ShellCheck, {len(paths)} file(s)", flush=True)
        result = subprocess.run(
            [
                str(SHELLCHECK),
                "--norc",
                "--format=gcc",
                "--severity=style",
                "--",  # Remaining arguments are filenames, never tool options.
                *(str(path) for path in paths),
            ],
            cwd=ROOT,
            env=environment,
            check=False,  # Findings are expected statuses, not Python exceptions.
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR lint-shell: {error}", file=sys.stderr)
        return 2

    if result.returncode == 1:
        print("FAIL lint-shell: fix the ShellCheck findings.", file=sys.stderr)
        return 1
    if result.returncode != 0:
        print(
            f"ERROR lint-shell: ShellCheck exited {result.returncode}.",
            file=sys.stderr,
        )
        return 2

    print("PASS lint-shell", flush=True)
    return 0


if __name__ == "__main__":
    # Make and CI receive the status returned by main().
    raise SystemExit(main())
