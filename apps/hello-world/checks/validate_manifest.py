"""Validate the web manifest used by the static page."""

import argparse
import json
import sys
from pathlib import Path


def validate_manifest(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: expected JSON object")
    if data.get("start_url") != "/" or data.get("display") != "standalone":
        raise ValueError(f"{path.name}: wrong start URL or display mode")
    if data.get("icons") != [
        {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}
    ]:
        raise ValueError(f"{path.name}: wrong icon")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Hello World web manifest"
    )
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        validate_manifest(args.path)
    except OSError as error:
        print(f"ERROR manifest: {error}", file=sys.stderr)
        return 2
    except (ValueError, TypeError, AttributeError) as error:
        print(f"FAIL manifest: {error}", file=sys.stderr)
        return 1
    print(f"PASS manifest: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
