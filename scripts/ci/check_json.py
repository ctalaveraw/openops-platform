#!/usr/bin/env python3
"""Check repository JSON and the notification examples' existing contract."""

import json  # Parse JSON data without executing it.
import os  # Decode Git filenames using the filesystem encoding.
import subprocess  # Ask Git which files belong to the check.
import sys  # Return an exit status and import this checkout's validator.
from pathlib import Path  # Derive paths independently of the caller's directory.

ROOT = Path(__file__).resolve().parents[2]
EVENT_EXAMPLES = ROOT / "examples" / "notifications"


def unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    # Python normally keeps the last value when an object repeats a key.
    # Reject duplicates at every nesting level so values are not silently lost.
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    # Python accepts these numeric extensions unless we reject them explicitly.
    raise ValueError(f"nonstandard JSON numeric token: {value}")


def json_inputs() -> list[Path]:
    # Include tracked files and new files that Git does not ignore.
    # NUL separators preserve spaces and newlines inside filenames.
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        check=True,
    )
    paths = {ROOT / os.fsdecode(name) for name in listed.stdout.split(b"\0") if name}

    # This data check includes vendor metadata. It never rewrites any input.
    # Skip tracked deletions and sort paths for stable diagnostic ordering.
    return sorted(path for path in paths if path.suffix == ".json" and path.is_file())


def main() -> int:
    # Keep required file selection fixed, as with our other check wrappers.
    if len(sys.argv) != 1:
        print(
            "ERROR lint-json: this command accepts no path arguments.", file=sys.stderr
        )
        return 2

    try:
        # This repo is not installed as a Python package. Running by filename
        # starts sys.path in scripts/ci/, so add this checkout's root for imports.
        sys.path.insert(0, str(ROOT))
        from scripts.notifications.notify_zulip import InputError, read_event

        paths = json_inputs()
        if not paths:
            raise ValueError("no JSON inputs were selected")

        print(f"RUN lint-json: {len(paths)} file(s)", flush=True)
        failures = 0
        for path in paths:
            try:
                # Parse a UTF-8 document. The hooks make our policy explicit.
                json.loads(
                    path.read_text(encoding="utf-8"),
                    object_pairs_hook=unique_keys,
                    parse_constant=reject_constant,
                )
                if path.is_relative_to(EVENT_EXAMPLES):
                    # Reuse the notifier's size and field validation.
                    # This function only reads an event; it does not send it.
                    read_event(path)
            except (ValueError, RecursionError, InputError) as error:
                # Content problems are findings. Continue to check other files.
                print(
                    f"FAIL lint-json: {path.relative_to(ROOT)}: {error}",
                    file=sys.stderr,
                )
                failures += 1

    except (ImportError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR lint-json: {error}", file=sys.stderr)
        return 2

    if failures:
        print(f"FAIL lint-json: {failures} file(s) failed.", file=sys.stderr)
        return 1

    print("PASS lint-json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
