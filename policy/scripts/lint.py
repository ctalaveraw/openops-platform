#!/usr/bin/env python3
"""Parse component-owned source and input fixtures without writing files."""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    for path in sorted(ROOT.rglob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in sorted(ROOT.rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
    print("PASS: Python and JSON source parses")


if __name__ == "__main__":
    main()
