"""Load the fixed YAML specimen layout, not general YAML."""

import re
from pathlib import Path


def load_fixture_yaml(path: Path) -> dict[str, str]:
    """Read only the three quoted fields in our specimen, not general YAML."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    if len(lines) != 4 or lines[0] != "episode:":
        raise ValueError(f"{path.name}: unexpected fixture layout")
    fields = {}
    for line in lines[1:]:
        match = re.fullmatch(r'  (id|title|status): "([^"\n]*)"', line)
        if match is None or match.group(1) in fields:
            raise ValueError(f"{path.name}: unexpected field")
        fields[match.group(1)] = match.group(2)
    return fields
