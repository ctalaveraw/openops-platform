"""Load the JSON episode specimen."""

import json
from pathlib import Path


def load_json(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))["episode"]
