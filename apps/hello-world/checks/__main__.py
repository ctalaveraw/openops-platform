"""Select and run component-owned source validators."""

import argparse
import configparser
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from checks.formats import FORMAT_LOADERS, check_format
from checks.validate_manifest import validate_manifest
from checks.validate_svg import validate_svg

ROOT = Path(__file__).resolve().parents[1]


def check_svg(root: Path) -> None:
    validate_svg(root / "public/favicon.svg")


def check_manifest(root: Path) -> None:
    validate_manifest(root / "public/site.webmanifest")


# Explicit registration of supported checks.
STATIC_CHECKS = {
    "svg": check_svg,
    "manifest": check_manifest,
}


def run_checks(group: str, selected: str, root: Path) -> int:
    if group == "static":
        available = tuple(STATIC_CHECKS)
    elif group == "formats":
        available = tuple(FORMAT_LOADERS)
    else:
        print(f"ERROR checks: unknown group {group}", file=sys.stderr)
        return 2

    if selected == "all":
        names = available
    elif selected in available:
        names = (selected,)
    else:
        print(f"ERROR {group}: unknown check {selected}", file=sys.stderr)
        print(f"Available: {', '.join(available)}", file=sys.stderr)
        return 2

    for name in names:
        try:
            if group == "static":
                STATIC_CHECKS[name](root)
            else:
                check_format(root, name)
        except OSError as error:
            print(f"ERROR {name}: {error}", file=sys.stderr)
            return 2
        except (
            ValueError,
            TypeError,
            KeyError,
            ET.ParseError,
            configparser.Error,
        ) as error:
            print(f"FAIL {name}: {error}", file=sys.stderr)
            return 1
        print(f"PASS {name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=["static", "formats"])
    parser.add_argument("--only", default="all")
    args = parser.parse_args()
    return run_checks(args.group, args.only, ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
