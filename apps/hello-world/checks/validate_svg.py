"""Validate the static application's SVG icon contract."""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_ROOT = "{http://www.w3.org/2000/svg}"


def validate_svg(path: Path) -> None:
    root = ET.parse(path).getroot()
    if root.tag != SVG_ROOT + "svg" or root.get("viewBox") != "0 0 64 64":
        raise ValueError(f"{path.name}: wrong SVG root or viewBox")
    if root.findtext(SVG_ROOT + "title") != "OpenOps star":
        raise ValueError(f"{path.name}: missing icon title")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Hello World SVG icon")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        validate_svg(args.path)
    except OSError as error:
        print(f"ERROR svg: {error}", file=sys.stderr)
        return 2
    except (ET.ParseError, ValueError) as error:
        print(f"FAIL svg: {error}", file=sys.stderr)
        return 1
    print(f"PASS svg: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
